"""Analysis of the certification MAP (phase3/full_runs/map/DECLARATION.md). numpy/json only (no TeNPy).
Built on design/pilot2/code/analyze2.py; every rule follows DECLARATION §2-§4.

  python analyze_map.py <root> g4prep                     -> out/g4/g4_list.json (headline witness components)
  python analyze_map.py <root> g4check <indep.json> [...] -> out/g4/g4_check.json (separate-process agreement)
  python analyze_map.py <root> summary [<outdir>]         -> <outdir>/summary_map.json

Information limit of a label O at energy E (sector states with Tr H rho <= E), as in pilot2:
  inner (rigorous, explicit states): hull of the pool of stored in-sector states of the same (n, Jz) (pure states
         and two-state mixtures; by Toeplitz-Hausdorff every mixture point is also attained by a pure state in the
         span of its two components), hull.py; "pure" = best single stored state, no mixture;
  outer (DMRG-referenced): sigma <O> <= (E - G_sigma(lam) + dG)/(lam S), G = <H - sigma lam S O> of the label's chain
         states, dG = max(2 dchi, |G(chi 160) - G(chi 320)| where checked), minimised over the chain, capped at 1.
eps_tau = energy above E0 at which the two-sided width reaches tau = 0.06 |O_GS| (inner: smallest eps with
w_in >= tau, rigorous for "not certified"; outer: smallest eps with w_out >= tau, the certificate side).
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hull  # noqa: E402
import witness as W  # noqa: E402   (constants and pure helpers only; TeNPy is imported lazily there)

DELTA = 1e-6
KEY = W.IKEY


def rj(p):
    with open(p) as f:
        return json.load(f)


def jstr(J):
    return "%.1f" % float(J)


class Data:
    def __init__(self, root):
        self.root = root
        self.out = os.path.join(root, "out")
        self.states = {}
        for p in glob.glob(os.path.join(self.out, "states", "*.json")):
            r = rj(p)
            self.states[r["sid"]] = r
        self.G = {n: rj(os.path.join(root, "code", "graphs", "hh_d%d.json" % d)) for n, d in W.D_OF_N.items()}
        self.RD = rj(os.path.join(root, "code", "readings_declared.json"))

    def get(self, sub, name):
        p = os.path.join(self.out, sub, name)
        return rj(p) if os.path.exists(p) else None

    def thr(self, n, J):
        return self.get("thr", "thr_n%d_J%s.json" % (n, jstr(J)))

    def chain(self, n, J, lab, s):
        return self.get("chains", "chain_n%d_J%s_%s_%s.json" % (n, jstr(J), lab, s))

    def st(self, n, J, tag):
        return self.states.get("n%d_J%s_%s" % (n, jstr(J), tag))

    def pool(self, n, J, label):
        sz = self.G[n]["sz"]
        pts = []
        for r in self.states.values():
            if r["n"] != n or abs(r["Jz"] - float(J)) > 1e-9 or not r.get("in_sector"):
                continue
            if abs(r["sector_s"] - sz) > 1e-9 or r["indep"]["sector_var"] >= 1e-12:
                continue
            v = r["indep"].get(KEY[label])
            if v is None:
                continue
            pts.append(dict(sid=r["sid"], E=r["tenpy"]["E"], o=v))
        return pts


def make_limit(D, n, J, label, thr):
    """Return (pool, w_in(E), w_out(E), intervals) closures for one (n, Jz, label)."""
    pts = D.pool(n, J, label)
    ch = {s: D.chain(n, J, label, s) for s in "+-"}
    if not ch["+"] or not ch["-"]:
        return None
    S = ch["+"]["S"]
    dG = {}
    for s in "+-":
        c = D.get("chk", "chk_n%d_J%s_%s_%s.json" % (n, jstr(J), label, s))
        dG[s] = max(2.0 * thr.get("dchi", 0.0), abs(c["dG"]) if c else 0.0)

    import numpy as np
    Ea = np.array([p["E"] for p in pts])
    oa = np.array([p["o"] for p in pts])

    def inner(E):
        Wd, up, lo, cu, cl = hull.width(pts, E - DELTA)
        return lo, up, cl, cu

    def inner_fast(E):
        """Same value as inner() (hull.py logic, vectorised); used inside the eps_tau bisections."""
        e = E - DELTA
        a = Ea <= e
        b = ~a
        if not a.any():
            return None, None
        hi, lo = oa[a].max(), oa[a].min()
        if b.any():
            ea, eb = Ea[a][:, None], Ea[b][None, :]
            t = (e - ea) / (eb - ea)
            val = (1 - t) * oa[a][:, None] + t * oa[b][None, :]
            hi, lo = max(hi, val.max()), min(lo, val.min())
        return float(lo), float(hi)

    def pure(E):
        up, su = hull.pure_extreme(pts, E - DELTA, +1)
        lo, sl = hull.pure_extreme(pts, E - DELTA, -1)
        return lo, up, sl, su

    def outer(E):
        res = {}
        for s, sign in (("+", 1), ("-", -1)):
            best = min((E - p["F"] + dG[s]) / (p["lam"] * S) for p in ch[s]["points"])
            res[s] = sign * min(best, 1.0)
        return res["-"], res["+"]
    return dict(pts=pts, ch=ch, S=S, dG=dG, inner=inner, inner_fast=inner_fast, outer=outer, pure=pure)


def eps_tau(f, tau, lo, hi):
    """Smallest eps in [lo, hi] with f(eps) >= tau (f nondecreasing); None if f(hi) < tau; lo if f(lo) >= tau."""
    if f(hi) < tau:
        return None
    if f(lo) >= tau:
        return lo
    for _ in range(80):
        m = math.sqrt(lo * hi)
        if f(m) >= tau:
            hi = m
        else:
            lo = m
    return hi


def lin_resp(ch):
    p = min(ch["+"]["points"], key=lambda x: x["lam"])
    m = min(ch["-"]["points"], key=lambda x: x["lam"])
    if abs(p["lam"] - m["lam"]) > 1e-12:
        return None
    return (p["o"] - m["o"]) / (2 * p["lam"])


def row(D, n, J, label):
    thr = D.thr(n, J)
    if thr is None:
        return None
    L = make_limit(D, n, J, label, thr)
    if L is None:
        return None
    E0 = thr["E0"]
    gs = D.st(n, J, "R1_chi512" if n == 19 else "R1_chi320")
    oG = gs["indep"][KEY[label]]
    tau = W.TAU_FRAC * abs(oG)
    R = dict(n=n, Jz=J, label=label, O_GS=oG, tau=tau, S=L["S"], dG=L["dG"], pool=len(L["pts"]),
             n_points={s: len(L["ch"][s]["points"]) for s in "+-"},
             saturated={s: L["ch"][s].get("saturated") for s in "+-"}, ood=thr.get("ood"),
             eps=dict(lo=thr["eps_lo"], dig=thr["eps_dig"], up=thr["eps_up"]), dchi=thr.get("dchi"))
    # reading 2 windows (training points only)
    key = "%d_%s" % (n, jstr(J))
    if n in (57, 115) and not thr.get("ood"):
        r2, g2 = D.RD["r2"].get(key), D.RD["gap2"].get(key)
        if r2 and g2:
            ours = thr["gap_ours"]
            R["eps2"] = dict(lo=0.8 * r2 * min(ours, g2), dig=r2 * g2, up=1.2 * r2 * max(ours, g2) + thr["dchi"])

    def w_in(e):
        lo, up = L["inner_fast"](E0 + e)
        return (up - lo) if up is not None else 0.0

    def w_out(e):
        lo, up = L["outer"](E0 + e)
        return up - lo

    for nm, e in list(R["eps"].items()) + [("r2_" + k, v) for k, v in R.get("eps2", {}).items()]:
        E = E0 + e
        lo, up, cl, cu = L["inner"](E)
        olo, oup = L["outer"](E)
        plo, pup, psl, psu = L["pure"](E)
        flo, fup = L["inner_fast"](E)
        if up is not None and (abs(flo - lo) > 1e-12 or abs(fup - up) > 1e-12):
            R.setdefault("flags", []).append("inner_fast differs at " + nm)
        R["at_" + nm] = dict(eps=e, inner=[lo, up], w_in=(up - lo) if up is not None else None, outer=[olo, oup],
                             w_out=oup - olo, pure=[plo, pup], w_pure=(pup - plo) if pup is not None else None,
                             pure_sids=[psl, psu], comps=[cl, cu],
                             ratio_out=(oup - olo) / tau, ratio_in=((up - lo) / tau) if up is not None else None,
                             ratio_pure=((pup - plo) / tau) if pup is not None else None)
    emax = max([p["eps"] for s in "+-" for p in L["ch"][s]["points"]] + [thr["eps_up"]])
    lo_e = 1e-7
    R["eps_tau_in"] = eps_tau(w_in, tau, lo_e, emax)
    R["eps_tau_out"] = eps_tau(w_out, tau, lo_e, emax)
    R["eps_max_computed"] = emax
    R["w_out_floor"] = w_out(lo_e)
    # MAP (DEVIATIONS 6): eps_tau beyond the computed range -> the largest computed eps is a lower bound
    R["eps_tau_out_lb"] = R["eps_tau_out"] if R["eps_tau_out"] is not None else (emax if w_out(emax) < tau else None)
    # declared status (DECLARATION §4)
    a_lo, a_up = R["at_lo"], R["at_up"]
    if a_up["w_out"] <= tau:
        R["status"] = "CERTIFIED"
    elif a_lo["w_in"] is not None and a_lo["w_in"] >= tau:
        R["status"] = "NOT_CERTIFIED"
    else:
        R["status"] = "GRAY"
    if "at_r2_up" in R:
        if R["at_r2_up"]["w_out"] <= tau:
            R["status_r2"] = "CERTIFIED"
        elif R["at_r2_lo"]["w_in"] is not None and R["at_r2_lo"]["w_in"] >= tau:
            R["status_r2"] = "NOT_CERTIFIED"
        else:
            R["status_r2"] = "GRAY"
    # robustness: fraction of the digitized error (central) at which the conclusion flips
    ed = thr["eps_dig"]
    R["f_in"] = (R["eps_tau_in"] / ed) if R["eps_tau_in"] is not None else None       # NOT_CERTIFIED holds for f >= f_in
    R["f_out"] = (R["eps_tau_out"] / ed) if R["eps_tau_out"] is not None else None    # CERTIFIED holds for f <= f_out
    R["f_out_lb"] = (R["eps_tau_out_lb"] / ed) if R["eps_tau_out_lb"] is not None else None
    # law (Prop. L): chi from lambda_0, delta e* = (S/n) tau^2 / (8 chi)
    chi = lin_resp(L["ch"])
    R["chi"] = chi
    if chi and chi > 0:
        R["de_star_law"] = (L["S"] / n) * tau ** 2 / (8 * chi)
        R["w_law_dig"] = 2 * math.sqrt(2 * ed * chi / L["S"])
        R["w_law_up"] = 2 * math.sqrt(2 * thr["eps_up"] * chi / L["S"])
        for k in ("in", "out"):
            e = R["eps_tau_" + k]
            R["law_ratio_" + k] = (R["de_star_law"] / (e / n)) if e else None
    R["de_star_in"] = (R["eps_tau_in"] / n) if R["eps_tau_in"] else None
    R["de_star_out"] = (R["eps_tau_out"] / n) if R["eps_tau_out"] else None
    R["de_dig"] = ed / n
    # regime
    gaps = thr.get("gaps", {})
    if gaps.get("in_sector"):
        R["eps_over_gap_in"] = ed / gaps["in_sector"]
    if gaps.get("sz_minus"):
        R["eps_over_gap_szm"] = ed / gaps["sz_minus"]
    return R


def jstar(D, rows, n, label, reading="1"):
    """J* on IBM's 0.1 training grid: log delta e* interpolated linearly in Jz between computed grid points (outer
    eps_tau for 'certified'), compared with eps_dig (central) and with 1.2 * eps_dig * max(1, gap_ours/gap_IBM)
    (strict) at every training point."""
    pts = sorted((r["Jz"], r) for r in rows if r["n"] == n and r["label"] == label and not r.get("ood"))
    if len(pts) < 2:
        return None
    Js = [p[0] for p in pts]

    def interp(J, key):
        for (J0, r0), (J1, r1) in zip(pts[:-1], pts[1:]):
            if J0 - 1e-9 <= J <= J1 + 1e-9:
                a, b = r0.get(key), r1.get(key)
                if not a or not b:
                    return None
                t = (J - J0) / (J1 - J0)
                return math.exp((1 - t) * math.log(a) + t * math.log(b))
        return None

    def ginterp(J):
        for (J0, r0), (J1, r1) in zip(pts[:-1], pts[1:]):
            if J0 - 1e-9 <= J <= J1 + 1e-9:
                t = (J - J0) / (J1 - J0)
                return (1 - t) * r0["gap_factor"] + t * r1["gap_factor"]
        return 1.0
    table = []
    for k in range(45):
        J = round(1.6 + 0.1 * k, 1)
        key = "%d_%s" % (n, jstr(J))
        e = D.RD["eps1" if reading == "1" else "eps2"].get(key)
        et_out = interp(J, "eps_tau_out_lb")
        et_in = interp(J, "eps_tau_in")
        if e is None or (et_out is None and et_in is None):
            table.append(dict(Jz=J, eps=e, eps_tau_out=et_out, eps_tau_in=et_in, central=None, strict=None))
            continue
        cen = (et_out is not None) and (e <= et_out)
        stri = (et_out is not None) and (1.2 * e * ginterp(J) <= et_out)
        notc = (et_in is not None) and (0.8 * e >= et_in)
        table.append(dict(Jz=J, eps=e, eps_tau_out=et_out, eps_tau_in=et_in, central=cen, strict=stri, not_cert=notc,
                          computed=any(abs(J - x) < 1e-9 for x in Js)))

    def jfrom(key):
        ok = [t for t in table if t.get(key) is not None]
        js = None
        for t in reversed(ok):
            if t[key]:
                js = t["Jz"]
            else:
                break
        return js
    return dict(table=table, J_star_central=jfrom("central"), J_star_strict=jfrom("strict"),
                n_certified_central=sum(1 for t in table if t.get("central")),
                n_certified_strict=sum(1 for t in table if t.get("strict")),
                n_not_certified=sum(1 for t in table if t.get("not_cert")))


def summary(root, outdir=None):
    D = Data(root)
    outdir = outdir or D.out
    S = dict(rows=[], jstar={}, gates={}, law={}, intens={}, minchi={}, g1={}, refs={})
    for p in sorted(glob.glob(os.path.join(D.out, "labs", "lab_n*_J*_*.json"))):
        lb = rj(p)
        r = row(D, lb["n"], lb["Jz"], lb["label"])
        if r is None:
            continue
        thr = D.thr(lb["n"], lb["Jz"])
        g1 = thr.get("gap_ibm1")
        r["gap_factor"] = max(1.0, thr["gap_ours"] / g1) if (g1 and thr.get("gap_ours")) else 1.0
        r["lab_time_s"] = lb.get("time_s")
        S["rows"].append(r)
    rows = [r for r in S["rows"] if r["n"] in (57, 115)]
    for n in (57, 115):
        for label in W.LABELS:
            for rd in ("1", "2"):
                js = jstar(D, rows, n, label, rd)
                if js:
                    S["jstar"]["%d_%s_r%s" % (n, label, rd)] = js
    # references, thresholds and G3 (gap check, record only)
    g3 = []
    for p in sorted(glob.glob(os.path.join(D.out, "thr", "thr_n*_J*.json"))):
        t = rj(p)
        S["refs"]["%d_%s" % (t["n"], jstr(t["Jz"]))] = t
        if t["n"] in (57, 115) and t.get("gaps", {}).get("sz_minus"):
            key = "%d_%s" % (t["n"], jstr(t["Jz"]))
            for rd in ("1", "2"):
                g = D.RD["gap%s" % rd].get(key)
                if g:
                    g3.append(dict(n=t["n"], Jz=t["Jz"], reading=rd, ours=t["gaps"]["sz_minus"], ibm=g,
                                   rel=t["gaps"]["sz_minus"] / g - 1))
    S["gates"]["G3_gap_record"] = dict(rows=g3, max_abs_rel=max(abs(x["rel"]) for x in g3) if g3 else None,
                                       n_within_10pct=sum(1 for x in g3 if abs(x["rel"]) <= 0.10), n=len(g3))
    S["gates"]["G3_gap_record"]["pass_"] = (S["gates"]["G3_gap_record"]["n_within_10pct"] == len(g3)) if g3 else None
    # P1 / G2: chi 480 vs chi 320 at the R1b points
    p1 = []
    for J in (1.2, 1.6, 3.3, 4.0, 6.0):
        a, b, t = D.st(57, J, "R1_chi320"), D.st(57, J, "R1_chi480"), D.thr(57, J)
        if a and b and t:
            p1.append(dict(Jz=J, dE=abs(a["E"] - b["E"]), limit=0.02 * t["eps_up"],
                           pass_=abs(a["E"] - b["E"]) <= 0.02 * t["eps_up"]))
    S["gates"]["P1_chi480"] = dict(rows=p1, pass_=all(x["pass_"] for x in p1) if p1 else None)
    # P2 (chi 320 check of G), P3 (cold start)
    p2 = [rj(p) for p in sorted(glob.glob(os.path.join(D.out, "chk", "*.json")))]
    S["gates"]["P2_chk320"] = dict(rows=[dict(n=c["n"], Jz=c["Jz"], label=c["label"], sign=c["sign"], dG=c["dG"],
                                              limit=0.01 * c["eps_up"], pass_=abs(c["dG"]) <= 0.01 * c["eps_up"])
                                         for c in p2])
    S["gates"]["P2_chk320"]["pass_"] = all(x["pass_"] for x in S["gates"]["P2_chk320"]["rows"]) if p2 else None
    p3 = [rj(p) for p in sorted(glob.glob(os.path.join(D.out, "cold", "*.json")))]
    S["gates"]["P3_cold"] = dict(rows=[dict(n=c["n"], Jz=c["Jz"], label=c["label"], sign=c["sign"], dF=c["dF"],
                                            flag=c["flag_warm_stuck"]) for c in p3],
                                 pass_=all(not c["flag_warm_stuck"] for c in p3) if p3 else None)
    # P4: every in-plan state in sector and TeNPy == independent evaluator
    allst = [r for r in D.states.values() if r["kind"] in ("witness", "gs", "cold", "chk320", "minchi")
             and abs(r["sector_s"] - D.G[r["n"]]["sz"]) < 1e-9]
    S["gates"]["P4_sector_eval"] = dict(n=len(allst),
                                        n_out_of_sector=sum(1 for r in allst if not r["in_sector"]),
                                        max_var=max(r["indep"]["sector_var"] for r in allst) if allst else None,
                                        max_dE=max(r["agree"]["dE"] for r in allst) if allst else None,
                                        max_dm=max(r["agree"]["dm"] for r in allst) if allst else None)
    g = S["gates"]["P4_sector_eval"]
    g["pass_"] = bool(allst) and g["n_out_of_sector"] == 0 and g["max_dE"] < 1e-8 and g["max_dm"] < 1e-8
    p = os.path.join(D.out, "g4", "g4_check.json")
    S["gates"]["G4_separate_process"] = rj(p) if os.path.exists(p) else None
    # G1: n = 19 against exact diagonalization
    g1rows = []
    for J in W.G1_POINTS:
        ed = D.get("g1", "g1_J%s.json" % jstr(J))
        if not ed:
            continue
        for label in W.G1_LABELS:
            r = next((x for x in S["rows"] if x["n"] == 19 and abs(x["Jz"] - J) < 1e-9 and x["label"] == label), None)
            if r is None:
                continue
            E = ed["labels"][label]
            for k in ("lo", "dig", "up"):
                we = E["rows"]["eps_" + k]["w"]
                g1rows.append(dict(Jz=J, label=label, at=k, w_ed=we, w_in=r["at_" + k]["w_in"],
                                   w_out=r["at_" + k]["w_out"],
                                   rel_in=(r["at_" + k]["w_in"] / we - 1) if we else None,
                                   rel_out=(r["at_" + k]["w_out"] / we - 1) if we else None))
            et = E.get("eps_tau")
            g1rows.append(dict(Jz=J, label=label, at="eps_tau", ed=et, inn=r["eps_tau_in"], out=r["eps_tau_out"],
                               rel_in=(r["eps_tau_in"] / et - 1) if (et and r["eps_tau_in"]) else None,
                               rel_out=(r["eps_tau_out"] / et - 1) if (et and r["eps_tau_out"]) else None))
    if g1rows:
        wr = [x for x in g1rows if x["at"] != "eps_tau"]
        tr = [x for x in g1rows if x["at"] == "eps_tau"]
        ok_w = all(abs(x["rel_out"]) <= 0.01 and abs(x["rel_in"]) <= (0.01 if x["at"] == "lo" else 0.03)
                   for x in wr if x["rel_in"] is not None)
        ok_t = all(abs(x["rel_in"]) <= 0.05 and abs(x["rel_out"]) <= 0.05 for x in tr if x["rel_in"] is not None)
        S["gates"]["G1_ed19"] = dict(rows=g1rows, pass_=ok_w and ok_t)
    # minimal chi
    for p in sorted(glob.glob(os.path.join(D.out, "minchi", "*.json"))):
        m = rj(p)
        thr = D.thr(m["n"], m["Jz"])
        base = next((x for x in rows if x["n"] == m["n"] and abs(x["Jz"] - m["Jz"]) < 1e-9 and x["label"] == m["label"]),
                    None)
        per = {}
        for run in m["runs"]:
            per.setdefault(run["chi"], {})[run["sign"]] = run["points"]
        res = {}
        for chi, d in per.items():
            gs = d.get("0", [None])[0]
            best = {}
            for s, sign in (("+", 1), ("-", -1)):
                c = [p for p in d.get(s, []) + ([gs] if gs else []) if p["E"] <= thr["E_lo"] - 0 and p["in_sector"]]
                best[s] = max(c, key=lambda p: sign * p["o"]) if c else None
            Dp = (best["+"]["o"] - best["-"]["o"]) if (best["+"] and best["-"]) else None
            res[str(chi)] = dict(gs_eps=gs["eps"] if gs else None, D_pure=Dp,
                                 best={s: (dict(sid=b["sid"], E=b["E"], o=b["o"], lam=b["lam"]) if b else None)
                                       for s, b in best.items()},
                                 frac_of_full=(Dp / base["at_lo"]["w_pure"]) if (Dp is not None and base and
                                                                                  base["at_lo"]["w_pure"]) else None)
        S["minchi"]["%d_%s_%s" % (m["n"], jstr(m["Jz"]), m["label"])] = dict(
            E_lo_eps=thr["eps_lo"], full_D_pure=base["at_lo"]["w_pure"] if base else None, chis=res)
    # law summary and intensivity
    for r in S["rows"]:
        if r.get("law_ratio_in"):
            S["law"]["%d_%s_%s" % (r["n"], jstr(r["Jz"]), r["label"])] = dict(
                chi=r["chi"], de_star_law=r["de_star_law"], de_star_in=r["de_star_in"], de_star_out=r["de_star_out"],
                ratio_in=r["law_ratio_in"], ratio_out=r.get("law_ratio_out"),
                w_law_dig=r["w_law_dig"], w_out_dig=r["at_dig"]["w_out"],
                eps_over_gap_in=r.get("eps_over_gap_in"))
    for J in W.GRID:
        for label in W.LABELS:
            a = next((x for x in rows if x["n"] == 57 and abs(x["Jz"] - J) < 1e-9 and x["label"] == label), None)
            b = next((x for x in rows if x["n"] == 115 and abs(x["Jz"] - J) < 1e-9 and x["label"] == label), None)
            if a and b and a.get("de_star_out") and b.get("de_star_out"):
                S["intens"]["%s_%s" % (jstr(J), label)] = dict(de57=a["de_star_out"], de115=b["de_star_out"],
                                                               ratio=b["de_star_out"] / a["de_star_out"])
    S["jstar_interp_check"] = interp_check(rows)
    S["claims"] = claims(S, rows)
    with open(os.path.join(outdir, "summary_map.json"), "w") as f:
        json.dump(S, f, indent=1)
    print_summary(S)
    return S


def interp_check(rows):
    """DECLARATION §4: eps_tau_out at Jz = 3.3 interpolated (log-linear) from 3.2 and 3.4 vs computed."""
    out = {}
    for n in (57, 115):
        for label in ("m_s", "Czz_bar"):
            g = {round(r["Jz"], 1): r for r in rows if r["n"] == n and r["label"] == label}
            if all(J in g and g[J].get("eps_tau_out") for J in (3.2, 3.3, 3.4)):
                ip = math.exp(0.5 * (math.log(g[3.2]["eps_tau_out"]) + math.log(g[3.4]["eps_tau_out"])))
                out["%d_%s" % (n, label)] = dict(interp=ip, computed=g[3.3]["eps_tau_out"],
                                                 rel=ip / g[3.3]["eps_tau_out"] - 1,
                                                 ok=abs(ip / g[3.3]["eps_tau_out"] - 1) <= 0.05)
    return out


def claims(S, rows):
    """DECLARATION §4 claims C-A ... C-E with their robustness fractions."""
    G = S["gates"]
    gate_ok = all((G.get(k) or {}).get("pass_") for k in ("G1_ed19", "P1_chi480", "P2_chk320", "P3_cold",
                                                          "P4_sector_eval", "G4_separate_process"))
    C = {}
    hi = {n: [r for r in rows if r["n"] == n and r["label"] in ("m_s", "Czz_bar") and r["Jz"] >= 3.95] for n in (57, 115)}
    allc = {n: bool(hi[n]) and all(r["status"] == "CERTIFIED" for r in hi[n]) for n in hi}
    anyc115 = any(r["status"] == "CERTIFIED" for r in hi[115])
    if allc[57] and allc[115] and gate_ok:
        v = "MAP-POSITIVE"
    elif not anyc115:
        v = "MAP-ABSENT"
    elif allc[57] or allc[115] or any(r["status"] == "CERTIFIED" for n in hi for r in hi[n]):
        v = "MAP-PARTIAL"
    else:
        v = "MAP-ABSENT"
    fo = [r["f_out_lb"] for n in hi for r in hi[n] if r.get("f_out_lb")]
    C["C-A"] = dict(verdict=v, gates_ok=gate_ok, all_certified={str(k): v_ for k, v_ in allc.items()},
                    rows=[(r["n"], r["Jz"], r["label"], r["status"]) for n in hi for r in hi[n]],
                    holds_up_to_fraction=min(fo) if fo else None)
    low = [r for r in rows if r["Jz"] <= 1.65]
    fi = [r["f_in"] for r in low if r.get("f_in")]
    C["C-B"] = dict(holds=bool(low) and all(r["status"] == "NOT_CERTIFIED" for r in low), n_rows=len(low),
                    exceptions=[(r["n"], r["Jz"], r["label"], r["status"]) for r in low if r["status"] != "NOT_CERTIFIED"],
                    holds_down_to_fraction=max(fi) if fi else None)
    loc = [r for r in rows if r["label"] in W.LOCALS]
    cert = [(r["n"], r["Jz"], r["label"]) for r in loc if r["status"] == "CERTIFIED"]
    fl = [r["f_in"] for r in loc if r["status"] == "NOT_CERTIFIED" and r.get("f_in")]
    C["C-C"] = dict(no_local_certified=not cert, certified_local_rows=cert, n_rows=len(loc),
                    gray=[(r["n"], r["Jz"], r["label"]) for r in loc if r["status"] == "GRAY"],
                    holds_down_to_fraction=max(fl) if fl else None)
    av = [r for r in rows if r["label"] in W.AVERAGES and r["Jz"] >= 1.95 and r.get("law_ratio_out")]
    bad = [(r["n"], r["Jz"], r["label"], r["law_ratio_out"]) for r in av if not 0.8 <= r["law_ratio_out"] <= 1.25]
    C["C-D"] = dict(holds=bool(av) and not bad, n_rows=len(av), outside=bad,
                    range=[min(r["law_ratio_out"] for r in av), max(r["law_ratio_out"] for r in av)] if av else None)
    ie = []
    for k, v_ in S["intens"].items():
        J, label = k.split("_", 1)
        if float(J) >= 1.95:
            ok = (0.67 <= v_["ratio"] <= 1.5) if label in W.AVERAGES else (v_["ratio"] <= 0.75)
            ie.append(dict(Jz=float(J), label=label, ratio=v_["ratio"], ok=ok))
    C["C-E"] = dict(holds=bool(ie) and all(x["ok"] for x in ie), rows=ie)
    return C


def print_summary(S):
    print("%-4s %-4s %-10s %8s %8s %8s %8s %8s %-13s %8s %8s %6s" % ("n", "Jz", "label", "O_GS", "w_in_lo", "w_out_up",
                                                                   "r_dig", "r_pure", "status", "f_in", "f_out", "law"))
    for r in sorted(S["rows"], key=lambda r: (r["n"], r["label"], r["Jz"])):
        f = lambda x: ("%8.4f" % x) if isinstance(x, (int, float)) and x is not None else "%8s" % "-"
        print("%-4d %-4.1f %-10s %s %s %s %s %s %-13s %s %s %s" % (
            r["n"], r["Jz"], r["label"], f(r["O_GS"]), f(r["at_lo"]["w_in"]), f(r["at_up"]["w_out"]),
            f(r["at_dig"]["ratio_out"]), f(r["at_dig"]["ratio_pure"]), r["status"], f(r["f_in"]), f(r["f_out"]),
            ("%6.3f" % r["law_ratio_in"]) if r.get("law_ratio_in") else "     -"))
    for k, v in S["jstar"].items():
        print("J*", k, "central", v["J_star_central"], "strict", v["J_star_strict"], "n_cert", v["n_certified_central"],
              v["n_certified_strict"], "n_notcert", v["n_not_certified"])
    print(json.dumps({k: (v.get("pass_") if isinstance(v, dict) else v) for k, v in S["gates"].items()}))
    if "claims" in S:
        print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("rows",)} for k, v in S["claims"].items()},
                         default=str)[:3000])


# ----------------------------------------------------------------------------------------------- G4 (separate process)
HEADLINE = dict(labels=["m_s", "Czz_bar"], local_label="Z_bulk", local_J=[1.6, 4.0, 6.0])


def g4prep(root):
    D = Data(root)
    lst = []
    for p in sorted(glob.glob(os.path.join(D.out, "labs", "lab_n*_J*_*.json"))):
        lb = rj(p)
        n, J, label = lb["n"], lb["Jz"], lb["label"]
        if n not in (57, 115):
            continue
        if not (label in HEADLINE["labels"] or (label == HEADLINE["local_label"] and
                                                any(abs(J - x) < 1e-9 for x in HEADLINE["local_J"]))):
            continue
        thr = D.thr(n, J)
        L = make_limit(D, n, J, label, thr)
        for side in ("lo", "up"):
            E = thr["E_" + side]
            lo, up, cl, cu = L["inner"](E)
            plo, pup, psl, psu = L["pure"](E)
            for which, comps in (("min", cl), ("max", cu)):
                for (sid, w, Ea, oa) in comps:
                    lst.append(dict(n=n, Jz=J, label=label, at=side, E_thr=E, which=which, kind="mix", sid=sid,
                                    weight=w, E=Ea, o=oa, npz=D.states[sid]["npz"],
                                    npz_present=os.path.exists(os.path.join(root, D.states[sid]["npz"]))))
            for which, sid in (("min", psl), ("max", psu)):
                if sid:
                    r = D.states[sid]
                    lst.append(dict(n=n, Jz=J, label=label, at=side, E_thr=E, which=which, kind="pure", sid=sid,
                                    weight=1.0, E=r["tenpy"]["E"], o=r["indep"][KEY[label]], npz=r["npz"],
                                    npz_present=os.path.exists(os.path.join(root, r["npz"]))))
    os.makedirs(os.path.join(D.out, "g4"), exist_ok=True)
    with open(os.path.join(D.out, "g4", "g4_list.json"), "w") as f:
        json.dump(lst, f, indent=1)
    for x in sorted(set((x["n"], x["npz"]) for x in lst if x["npz_present"])):
        print(x[0], x[1])


def g4check(root, paths):
    D = Data(root)
    ev = {}
    for pth in paths:
        for r in rj(pth):
            ev[r["meta"]["sid"]] = r
    lst = rj(os.path.join(D.out, "g4", "g4_list.json"))
    rows = []
    for sid, r in ev.items():
        s = D.states[sid]
        rows.append(dict(sid=sid, dE=abs(r["E"] - s["tenpy"]["E"]),
                         dO=max(abs(r[KEY[k]] - s["indep"][KEY[k]]) for k in W.LABELS),
                         dm_tenpy=abs(r["m_s"] - s["tenpy"]["m_s"]),
                         dnorm=abs(r["norm"] / s["tenpy"]["overlap"] - 1), var=r["sector_var"]))
    # mixture energies from the separately evaluated components, against the thresholds
    mix = {}
    for x in lst:
        if x["kind"] != "mix" or x["sid"] not in ev:
            continue
        k = (x["n"], x["Jz"], x["label"], x["at"], x["which"])
        m = mix.setdefault(k, dict(E=0.0, o=0.0, w=0.0, E_thr=x["E_thr"]))
        m["E"] += x["weight"] * ev[x["sid"]]["E"]
        m["o"] += x["weight"] * ev[x["sid"]][KEY[x["label"]]]
        m["w"] += x["weight"]
    mrows = [dict(key=list(k), E=v["E"], E_thr=v["E_thr"], complete=abs(v["w"] - 1) < 1e-9,
                  below=(v["E"] <= v["E_thr"]) if abs(v["w"] - 1) < 1e-9 else None, w=v["w"]) for k, v in mix.items()]
    pure_ok = all(ev[x["sid"]]["E"] <= x["E_thr"] for x in lst if x["kind"] == "pure" and x["sid"] in ev)
    out = dict(n_components=len(rows), rows=rows, mixtures=mrows,
               max_dE=max(x["dE"] for x in rows), max_dO=max(x["dO"] for x in rows),
               max_dm_tenpy=max(x["dm_tenpy"] for x in rows), max_dnorm=max(x["dnorm"] for x in rows),
               max_var=max(x["var"] for x in rows),
               all_mixtures_below=all(m["below"] for m in mrows if m["complete"]),
               n_mixtures_incomplete=sum(1 for m in mrows if not m["complete"]),
               all_pure_below=pure_ok, n_missing=sum(1 for x in lst if x["sid"] not in ev and x["npz_present"]),
               n_pruned=sum(1 for x in lst if not x["npz_present"]))
    out["pass_"] = (out["max_dE"] < 1e-8 and out["max_dO"] < 1e-8 and out["max_dnorm"] < 1e-8 and
                    out["max_var"] < 1e-12 and out["all_mixtures_below"] and pure_ok and out["n_missing"] == 0)
    with open(os.path.join(D.out, "g4", "g4_check.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "mixtures")}))


if __name__ == "__main__":
    root, mode = sys.argv[1], sys.argv[2]
    if mode == "summary":
        summary(root, sys.argv[3] if len(sys.argv) > 3 else None)
    elif mode == "g4prep":
        g4prep(root)
    elif mode == "g4check":
        g4check(root, sys.argv[3:])
    else:
        raise SystemExit("unknown mode")
