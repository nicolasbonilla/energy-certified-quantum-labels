"""Post-hoc tolerance scan of the map (R5 S6). NOT part of any declaration. Reads stored JSON only (seconds).

  python -I tau_scan.py <phase3/full_runs/map/laptop_analysis>   -> <dir>/tau_scan.json

For tau = f |O_GS| with f in (0.03, 0.06, 0.10) it recomputes, for m_s and Czz_bar at n = 57 and 115 (reading 1), the
outer eps_tau of every computed training row from the stored chains (same formula as analyze_map.py: sigma <O> <=
(E - F + dG)/(lam S), minimised over the chain, capped at 1; bisection in log eps), and then J* (central and strict) and
the counts of certified training points with the same log-linear interpolation in Jz. The f = 0.06 run must reproduce
the stored summary_map.json (checked and recorded below)."""
import json
import math
import os
import sys

D = sys.argv[1]
OUT = os.path.join(D, "out")
S = json.load(open(os.path.join(D, "summary_map.json"), encoding="utf8"))
RD = json.load(open(os.path.join(D, "code", "readings_declared.json"), encoding="utf8"))


def rj(*p):
    q = os.path.join(OUT, *p)
    return json.load(open(q, encoding="utf8")) if os.path.exists(q) else None


def eps_tau(f, tau, lo, hi):
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


def outer_w(r):
    n, J, lab = r["n"], r["Jz"], r["label"]
    ch = {s: rj("chains", "chain_n%d_J%.1f_%s_%s.json" % (n, J, lab, s)) for s in "+-"}
    E0 = rj("thr", "thr_n%d_J%.1f.json" % (n, J))["E0"]
    Sc = ch["+"]["S"]

    def w(e):
        E = E0 + e
        res = {}
        for s, sign in (("+", 1), ("-", -1)):
            best = min((E - p["F"] + r["dG"][s]) / (p["lam"] * Sc) for p in ch[s]["points"])
            res[s] = sign * min(best, 1.0)
        return res["+"] - res["-"]
    return w


def jstar(rows, n, frac):
    pts = sorted((r["Jz"], r) for r in rows if r["n"] == n)
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
        e = RD["eps1"].get("%d_%.1f" % (n, J))
        et = interp(J, "et_lb")
        if e is None or et is None:
            table.append(dict(Jz=J, central=None, strict=None))
            continue
        table.append(dict(Jz=J, central=e <= et, strict=1.2 * e * ginterp(J) <= et))

    def jfrom(key):
        js = None
        for t in reversed([t for t in table if t.get(key) is not None]):
            if t[key]:
                js = t["Jz"]
            else:
                break
        return js
    return dict(J_star_central=jfrom("central"), J_star_strict=jfrom("strict"),
                n_certified_central=sum(1 for t in table if t.get("central")),
                n_certified_strict=sum(1 for t in table if t.get("strict")))


res = {"note": "post-hoc (R5 S6), not declared; tau = frac |O_GS|; reading 1; outer side (certified)", "frac": {}}
check = {}
for frac in (0.03, 0.06, 0.10):
    blk = {}
    for lab in ("m_s", "Czz_bar"):
        for n in (57, 115):
            rows = []
            for r in S["rows"]:
                if r["n"] != n or r["label"] != lab or r.get("ood"):
                    continue
                tau = frac * abs(r["O_GS"])
                w = outer_w(r)
                emax = r["eps_max_computed"]
                et = eps_tau(w, tau, 1e-7, emax)
                et_lb = et if et is not None else (emax if w(emax) < tau else None)
                rows.append(dict(n=n, Jz=r["Jz"], et=et, et_lb=et_lb, gap_factor=r["gap_factor"],
                                 status=("CERTIFIED" if w(r["eps"]["up"]) <= tau else "not certified")))
                if frac == 0.06:
                    check["%d_%.1f_%s" % (n, r["Jz"], lab)] = (et, r["eps_tau_out"])
            blk["%d_%s" % (n, lab)] = jstar(rows, n, frac)
    res["frac"]["%.2f" % frac] = blk
# reproduction of the stored values at 6 %
dev = max(abs(a / b - 1) for a, b in check.values() if a and b)
same_none = all((a is None) == (b is None) for a, b in check.values())
stored = {k: {q: S["jstar"][k + "_r1"][q] for q in ("J_star_central", "J_star_strict", "n_certified_central", "n_certified_strict")}
          for k in ("57_m_s", "115_m_s", "57_Czz_bar", "115_Czz_bar")}
res["check_6pct"] = dict(max_rel_dev_eps_tau_out=dev, same_none=same_none, n_rows=len(check),
                         jstar_equal_stored=all(res["frac"]["0.06"][k] == stored[k] for k in stored), stored=stored)
json.dump(res, open(os.path.join(D, "tau_scan.json"), "w", encoding="utf8"), indent=1)
print(json.dumps(res, indent=1))
