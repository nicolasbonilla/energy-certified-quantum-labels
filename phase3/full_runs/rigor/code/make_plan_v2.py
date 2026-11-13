"""v2 plan (declared): λ grid per (n, Jz, label, sign) = every stored map chain point + a fixed geometric refinement
λ_dec·0.85^k (k = 1, 2, 3), λ_dec = the chain point that is decisive at E_up for the DMRG-referenced outer bound (no δG).
usage: python make_plan_v2.py <map chains dir> <requirement.json> <out plan_v2_A.json> <out grid_v2.json>

Upper reference for every grid point (used only for pruning and slack reporting, never for a certified width):
F_up(λ) = min over the stored chain states of the same chain of (E_k − σ λ S o_k) — the variational energy of an
in-sector state, hence ≥ the true G_σ(λ). At chain points F_up ≤ F (the chain's own DMRG value).
Provable pruning: u_lb(p) = (E_up − F_up(p))/(λ_p S) ≤ the rigorous u(p) for any certified bound.  A point p is not
computed if u_lb(p) + min_q u_lb(q) > τ (q over the other side's grid): with p no certified width ≤ τ is possible.
"""
import json
import os
import sys
from fractions import Fraction

CH, REQ, OUTA, OUTG = sys.argv[1:5]
req = json.load(open(REQ))
SCOPES = [("S1", 57, [4.0, 6.0]), ("S2", 57, [3.4, 3.6, 4.5, 5.0, 5.5]), ("S3", 115, [4.0, 6.0])]
GRAPH = {19: "hh_d3.json", 57: "hh_d5.json", 115: "hh_d7.json"}
NE = {19: 20, 57: 64, 115: 132}
REF = (0.85, 0.85 ** 2, 0.85 ** 3)
OPT_V = dict(K=32, maxiter=600, betas=[30, 300, 3000, 30000, 100000], use_mu=True, clusters="vball2")


def dyadic(x, bits=20):
    return Fraction(round(x * 2 ** bits), 2 ** bits)


grid, plan = [], []
for scope, n, Jzs in SCOPES:
    for Jz in Jzs:
        for lab in ("m_s", "Czz_bar"):
            r = next(x for x in req if x["n"] == n and x["Jz"] == Jz and x["label"] == lab)
            S = float(n if lab == "m_s" else NE[n])
            Eup, tau = r["E_up"], r["tau"]
            sides = {}
            for s, sg in (("+", 1), ("-", -1)):
                ch = json.load(open(os.path.join(CH, "chain_n%d_J%.1f_%s_%s.json" % (n, Jz, lab, s))))
                st = [(p["E"], p["o"]) for p in ch["points"]]
                def Fup(lam):
                    return min(E - sg * lam * S * o for (E, o) in st)
                pts = []
                for p in ch["points"]:
                    lam = Fraction(p["lam"])
                    pts.append(dict(lam=str(lam), lam_f=p["lam"], kind="chain", F=p["F"], F_up=min(p["F"], Fup(p["lam"])),
                                    eps=p["eps"]))
                dec = min(pts, key=lambda q: (Eup - q["F"]) / (q["lam_f"] * S))
                for f in REF:
                    lam = dyadic(dec["lam_f"] * f)
                    pts.append(dict(lam=str(lam), lam_f=float(lam), kind="ref%.4f" % f, F=None, F_up=Fup(float(lam)),
                                    eps=None))
                for q in pts:
                    q["u_lb"] = (Eup - q["F_up"]) / (q["lam_f"] * S)
                sides[s] = dict(sigma=sg, pts=pts, lam_dec=dec["lam_f"])
            for s, o in (("+", "-"), ("-", "+")):
                best_other = min(q["u_lb"] for q in sides[o]["pts"])
                for q in sides[s]["pts"]:
                    q["pruned"] = q["u_lb"] + best_other > tau
            w_F = sum(min((Eup - q["F"]) / (q["lam_f"] * S) for q in sides[s]["pts"] if q["F"] is not None)
                      for s in "+-")
            row = dict(scope=scope, n=n, Jz=Jz, label=lab, S=S, E_up=Eup, tau=tau, s_req=r["s_req"], w_F=w_F,
                       sides=sides)
            grid.append(row)
            for s in "+-":
                for q in sorted(sides[s]["pts"], key=lambda q: q["u_lb"]):
                    if q["pruned"]:
                        continue
                    task = dict(OPT_V, kind=lab, Jz=repr(Jz), sigma=sides[s]["sigma"], lam=q["lam"])
                    plan.append(dict(id="v2_n%d_vball2_%s_%s%.1f_l%.6f" % (n, lab, "p" if s == "+" else "m", Jz, q["lam_f"]),
                                     graph=GRAPH[n], task=task, ed=False, n=n, scope=scope, row="%d_%.1f_%s" % (n, Jz, lab),
                                     side=s, lam_f=q["lam_f"], F=q["F"], F_up=q["F_up"], u_lb=q["u_lb"], kind=q["kind"]))
# n = 19 sanity gate: the S1 refinement λ values with exact diagonalization (vball2)
for row in [g for g in grid if g["scope"] == "S1"]:
    for s in "+-":
        for q in row["sides"][s]["pts"]:
            if q["kind"].startswith("ref"):
                task = dict(OPT_V, kind=row["label"], Jz=repr(row["Jz"]), sigma=row["sides"][s]["sigma"], lam=q["lam"])
                plan.append(dict(id="v2_n19_vball2_%s_%s%.1f_l%.6f" % (row["label"], "p" if s == "+" else "m", row["Jz"],
                                                                      q["lam_f"]),
                                 graph=GRAPH[19], task=task, ed=True, n=19, scope="G19", row=None, side=s,
                                 lam_f=q["lam_f"], F=None, F_up=None, u_lb=None, kind=q["kind"]))
order = {"S1": 0, "G19": 1, "S2": 2, "S3": 3}
plan.sort(key=lambda p: order[p["scope"]])
json.dump(plan, open(OUTA, "w"), indent=1)
json.dump(grid, open(OUTG, "w"), indent=1)
for row in grid:
    ns = {s: (len(row["sides"][s]["pts"]), sum(not q["pruned"] for q in row["sides"][s]["pts"])) for s in "+-"}
    print("%s n=%d Jz=%.1f %-8s tau %.4f w_F/tau %.3f grid(+) %d kept %d  grid(-) %d kept %d  lam_dec %.4f / %.4f" % (
        row["scope"], row["n"], row["Jz"], row["label"], row["tau"], row["w_F"] / row["tau"], ns["+"][0], ns["+"][1],
        ns["-"][0], ns["-"][1], row["sides"]["+"]["lam_dec"], row["sides"]["-"]["lam_dec"]))
from collections import Counter
print("jobs:", dict(Counter(p["scope"] for p in plan)))
