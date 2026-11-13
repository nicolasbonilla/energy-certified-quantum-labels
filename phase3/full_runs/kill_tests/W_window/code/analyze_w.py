"""Kill test W: analysis (DECLARATION.md sec. 6-7). Reads out/ed/*.json and out/methods/*.json, writes out/analysis.json
and out/analysis.txt. Runs on the VM.

  python analyze_w.py <SB>
"""
import glob
import json
import math
import os
import sys

import numpy as np

TARGETS = [10 ** (-3 + 0.25 * i) for i in range(5)]


def load(p):
    return json.load(open(p))


def hull(points, side):
    """upper concave hull (side=+1) or lower convex hull (side=-1) of (de, o) points, as sorted vertex arrays"""
    pts = sorted((float(d), side * float(o)) for d, o in points)
    h = []
    for p in pts:
        while len(h) >= 2:
            (x1, y1), (x2, y2) = h[-2], h[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) >= 0:  # h[-1] not above segment -> drop
                h.pop()
            else:
                break
        h.append(p)
    # keep the nondecreasing part (the window grows with de)
    out = [h[0]]
    for p in h[1:]:
        if p[1] >= out[-1][1]:
            out.append(p)
    xs = np.array([p[0] for p in out]); ys = np.array([p[1] for p in out])
    return xs, ys


class Chain:
    def __init__(self, d):
        self.obs, self.side, self.e0, self.o0 = d["obs"], d["side"], d["e0"], d["o0"]
        self.recs = d["records"]
        self.done = d.get("done", False)
        pts = [(r["e"] - self.e0, r[self.obs]) for r in self.recs]
        pts = [(max(de, 0.0), o) for de, o in pts]
        self.hx, self.hy = hull(pts, self.side)
        self.dual = [(r["lam"], r["g"]) for r in self.recs if r["lam"] > 0]

    def w_in(self, de):
        s = self.side
        if de <= 0:
            return 0.0
        y = np.interp(de, self.hx, self.hy, right=self.hy[-1])
        return float(y - s * self.o0)

    def w_out(self, de):
        s = self.side
        return float(min((self.e0 + de - g) / lam for lam, g in self.dual) - s * self.o0)

    def checks(self):
        s = self.side
        worst_wd = 0.0
        for r in self.recs:
            for lam, g in self.dual:
                lhs = s * r[self.obs]
                rhs = (r["e"] - g) / lam
                worst_wd = max(worst_wd, lhs - rhs)
        restarts = [r["restart"]["dg"] for r in self.recs if "restart" in r]
        res = max(r["res"] for r in self.recs)
        return {"weak_duality_worst_violation": worst_wd, "restart_dg": restarts, "max_residual": res,
                "n_records": len(self.recs), "done": self.done,
                "max_de": max(r["e"] - self.e0 for r in self.recs)}


def r_of(row, obs, chains):
    de = row["de"]
    err = row[obs] - chains[1].o0
    if de < -1e-12:
        return None, err, 0, None
    if err == 0:
        return 0.0, err, 0, 0.0
    s = 1 if err > 0 else -1
    w = chains[s].w_in(de)
    wo = chains[s].w_out(de)
    return (abs(err) / w if w > 0 else float("inf")), err, s, (abs(err) / wo if wo > 0 else float("inf"))


def interp_r(pts, t):
    """piecewise-linear interpolation of r in log10(de); None outside the covered range"""
    if not pts:
        return None
    xs = np.log10([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    o = np.argsort(xs, kind="stable"); xs, ys = xs[o], ys[o]
    ux, uy = [], []
    for x, y in zip(xs, ys):
        if ux and abs(x - ux[-1][-1]) < 1e-9:
            ux[-1].append(x); uy[-1].append(y)
        else:
            ux.append([x]); uy.append([y])
    mx = np.array([np.mean(a) for a in ux]); my = np.array([np.mean(a) for a in uy])
    lt = math.log10(t)
    if lt < mx[0] - 1e-12 or lt > mx[-1] + 1e-12:
        return None
    return float(np.interp(lt, mx, my))


def window_median(pts, t, half=0.2):
    lt = math.log10(t)
    sel = [p[1] for p in pts if abs(math.log10(p[0]) - lt) <= half]
    return (float(np.median(sel)), len(sel)) if sel else (None, 0)


def exponents(ch):
    xs, ys = ch.hx, ch.hy - ch.side * ch.o0
    m = (xs > 0) & (ys > 0)
    lx, ly = np.log(xs[m]), np.log(ys[m])
    loc = [{"de_mid": float(math.exp(0.5 * (lx[i] + lx[i + 1]))), "slope": float((ly[i + 1] - ly[i]) / (lx[i + 1] - lx[i]))}
           for i in range(len(lx) - 1)]
    fits = {}
    for lo, hi in [(1e-6, 1e-5), (1e-5, 1e-4), (1e-4, 1e-3), (1e-3, 1e-2), (1e-2, 1e-1)]:
        sel = (xs[m] >= lo) & (xs[m] <= hi)
        if sel.sum() >= 2:
            fits["%g-%g" % (lo, hi)] = {"slope": float(np.polyfit(lx[sel], ly[sel], 1)[0]), "n": int(sel.sum())}
        else:
            fits["%g-%g" % (lo, hi)] = None
    return {"local": loc, "fits": fits}


def main(SB):
    O = os.path.join(SB, "out")
    res = {"targets": TARGETS}
    lines = []
    for J2 in (0.0, 0.5):
        gs = load(os.path.join(O, "ed", "gs_%g.json" % J2))
        e0 = gs["e0"]
        rows = []
        for f in sorted(glob.glob(os.path.join(O, "methods", "*_%g*.json" % J2))):
            if "gate" in os.path.basename(f):
                continue
            d = load(f)
            if abs(d.get("J2", -1) - J2) > 1e-12:
                continue
            for r in d["rows"]:
                if r["method"] == "MPS" and not r.get("gate_ok", False):
                    r["excluded"] = "dmrg gate failed"
                r["de"] = r["e"] - e0
                r["source"] = os.path.basename(f)
                rows.append(r)
        res["J2=%g" % J2] = {"e0": e0, "gs": gs["gs"], "obs": {}}
        for obs in (("ms",) if J2 == 0.0 else ("ms", "dim")):
            chains = {}
            for side in (1, -1):
                p = os.path.join(O, "ed", "env_%g_%s_%+d.json" % (J2, obs, side))
                chains[side] = Chain(load(p)) if os.path.exists(p) else None
            if chains[1] is None or chains[-1] is None:
                res["J2=%g" % J2]["obs"][obs] = {"error": "missing chain"}
                continue
            assert abs(chains[1].e0 - e0) < 1e-10 and abs(chains[-1].e0 - e0) < 1e-10
            table = []
            per = {}
            for r in rows:
                if r.get("excluded"):
                    continue
                rv, err, s, rvo = r_of(r, obs, chains)
                t = {"method": r["method"], "label": r["label"], "de": r["de"], "o": r[obs], "err": err, "side": s,
                     "w_in": chains[s].w_in(r["de"]) if s else 0.0, "r": rv, "r_outer": rvo, "S2": r.get("S2")}
                table.append(t)
                if rv is not None and r["de"] > 0:
                    per.setdefault(r["method"], []).append((r["de"], rv))
            stats = {}
            for t_ in TARGETS:
                row = {"de": t_}
                for mth, pts in per.items():
                    row[mth] = interp_r(pts, t_)
                    row[mth + "_median"] = window_median(pts, t_)
                for side in (1, -1):
                    row["w_in_%+d" % side] = chains[side].w_in(t_)
                    row["w_out_%+d" % side] = chains[side].w_out(t_)
                a, b = row.get("ViT"), row.get("MPS")
                row["ratio"] = (a / b if (a is not None and b not in (None, 0.0)) else (float("inf") if (a is not None and b == 0.0) else None))
                am, bm = row.get("ViT_median", (None, 0))[0], row.get("MPS_median", (None, 0))[0]
                row["ratio_median"] = am / bm if (am is not None and bm) else None
                stats["%.4g" % t_] = row
            verdict = None
            if J2 == 0.0 and obs == "ms":
                vit_de = [p[0] for p in per.get("ViT", [])]
                ev = [s_["ratio"] for s_ in stats.values() if s_["ratio"] is not None]
                above = sum(1 for x in ev if x > 0.5)
                below = sum(1 for x in ev if x <= 0.5)
                evm = [s_["ratio_median"] for s_ in stats.values() if s_["ratio_median"] is not None]
                if not vit_de or min(vit_de) > 1e-2:
                    verdict = "NO DECISION (ViT did not reach de <= 1e-2)"
                elif above >= 3:
                    verdict = "DEAD"
                elif below >= 3:
                    verdict = "SURVIVES"
                else:
                    verdict = "NO DECISION (fewer than 3 evaluable points on either side)"
                verdict = {"verdict": verdict, "evaluable": len(ev), "above_0.5": above, "at_or_below_0.5": below,
                           "secondary_median": {"evaluable": len(evm), "above_0.5": sum(1 for x in evm if x > 0.5),
                                                "at_or_below_0.5": sum(1 for x in evm if x <= 0.5)},
                           "vit_min_de": min(vit_de) if vit_de else None}
            res["J2=%g" % J2]["obs"][obs] = {
                "o0": chains[1].o0, "chains": {"+1": chains[1].checks(), "-1": chains[-1].checks()},
                "hull_plus": [list(map(float, chains[1].hx)), list(map(float, chains[1].hy))],
                "hull_minus": [list(map(float, chains[-1].hx)), list(map(float, -chains[-1].hy))],
                "exponent_plus": exponents(chains[1]), "exponent_minus": exponents(chains[-1]),
                "table": table, "stats": stats, "verdict": verdict,
                "max_r_outer": max([t["r_outer"] for t in table if t["r_outer"] is not None] or [0.0])}
            lines.append("== J2=%g obs=%s o0=%.10f e0=%.12f" % (J2, obs, chains[1].o0, e0))
            for k, s_ in stats.items():
                lines.append("de=%s  r_ViT=%s r_MPS=%s r_Kry=%s ratio=%s  w+=%.5f w-=%.5f" % (
                    k, s_.get("ViT"), s_.get("MPS"), s_.get("Krylov"), s_.get("ratio"), s_["w_in_+1"], s_["w_in_-1"]))
            if verdict:
                lines.append("VERDICT %s" % json.dumps(verdict))
    with open(os.path.join(O, "analysis.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    with open(os.path.join(O, "analysis.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(*sys.argv[1:])
