"""Slack requirement for making the CERTIFIED rows of the certification map rigorous (laptop, reads fetched JSON).

Outer side of the map (analyze_map.make_limit.outer):  sigma<O> <= (E_up - F_k + dG)/(lam_k S), min over chain points k,
with F_k = chi-160 DMRG energy of H - sigma lam_k S O (an UPPER bound on the true G_sigma(lam_k)).
Rigorous version: replace F_k by a certified lower bound G_LB,k = F_k - s_k and drop dG.  With a uniform slack s
the rigorous width is w(s) = sum_sigma min_k (E_up - F_k + s)/(lam_k S) (capped at 1).  The row stays CERTIFIED
iff w(s) <= tau.  s_req = the largest such s (bisection).  Reported with the decisive chain point of each side at
E_up + s_req (where a rigorous bound must be computed), its F, and (C_zz_bar) the equivalent Jz' = Jz - 4 sigma lam.
"""
import json, sys, os
OUT = sys.argv[1]          # .../map/out_20261030T022613Z/out
SUMMARY = sys.argv[2]      # .../map/laptop_analysis/summary_map.json
RES = sys.argv[3]          # output json

S = json.load(open(SUMMARY))
rows = [r for r in S["rows"] if r["label"] in ("m_s", "Czz_bar") and r["status"] == "CERTIFIED"]
refs = S["refs"]
res = []
for r in sorted(rows, key=lambda r: (r["n"], r["label"], r["Jz"])):
    n, J, lab = r["n"], r["Jz"], r["label"]
    js = ("%.1f" % J)
    ref = refs["%d_%s" % (n, js)]
    E0, Eup = ref["E0"], ref["E_up"]
    ch = {s: json.load(open(os.path.join(OUT, "chains", "chain_n%d_J%s_%s_%s.json" % (n, js, lab, s)))) for s in "+-"}
    Sop = ch["+"]["S"]
    tau = r["tau"]

    def side(s, sh, dG=0.0):
        best = min(((Eup - p["F"] + sh + dG) / (p["lam"] * Sop), p) for p in ch[s]["points"])
        return min(best[0], 1.0), best[1]

    def w(sh):
        return side("+", sh)[0] + side("-", sh)[0]
    # check: reproduces the map's w_out(E_up) with dG
    w_map = side("+", 0.0, r["dG"]["+"])[0] + side("-", 0.0, r["dG"]["-"])[0]
    lo, hi = 0.0, 50.0
    if w(lo) > tau:
        sreq = None
    else:
        for _ in range(200):
            m = 0.5 * (lo + hi)
            if w(m) <= tau:
                lo = m
            else:
                hi = m
        sreq = lo
    dec = {}
    for s, sg in (("+", 1), ("-", -1)):
        u, p = side(s, sreq or 0.0)
        d = dict(lam=p["lam"], F=p["F"], E=p["E"], o=p["o"], sid=p["sid"], u=sg * u)
        if lab == "Czz_bar":
            d["Jz_equiv"] = J - 4 * sg * p["lam"]
            d["F_equals_E0_of_H(Jz_equiv)"] = True
        dec[s] = d
    eps_up = Eup - E0
    out = dict(n=n, Jz=J, label=lab, E0=E0, E_up=Eup, eps_up=eps_up, eps_tau_out=r["eps_tau_out"], tau=tau,
               w_out_map=r["at_up"]["w_out"], w_out_recomputed=w_map, dG=r["dG"], s_req=sreq,
               s_req_uniform_formula=(r["eps_tau_out"] - eps_up) if r["eps_tau_out"] is not None else None, s_req_rel_E0=(sreq / abs(E0)) if sreq else None,
               s_req_rel_F={s: (sreq / abs(dec[s]["F"])) if sreq else None for s in "+-"},
               s_req_per_site=(sreq / n) if sreq else None, decisive=dec)
    res.append(out)
    if sreq is None or r["eps_tau_out"] is None:
        res.append(out); print("n=%d Jz=%.1f %s: eps_tau_out not resolved (beyond computed range); s_req = %s" % (n, J, lab, sreq)); continue
    print("n=%3d Jz=%.1f %-8s E0=%10.4f eps_up=%.4f eps_tau=%.4f  s_req=%.4f J  (%.3f %% |E0|, %.2e J/site)  "
          "dec+: lam=%.4f F=%.3f  dec-: lam=%.4f F=%.3f %s" % (
              n, J, lab, E0, eps_up, r["eps_tau_out"], sreq, 100 * sreq / abs(E0), sreq / n,
              dec["+"]["lam"], dec["+"]["F"], dec["-"]["lam"], dec["-"]["F"],
              ("Jz'=%.3f/%.3f" % (dec["+"]["Jz_equiv"], dec["-"]["Jz_equiv"])) if lab == "Czz_bar" else ""))
    assert abs(w_map - r["at_up"]["w_out"]) < 1e-9, (w_map, r["at_up"]["w_out"])
json.dump(res, open(RES, "w"), indent=1)
