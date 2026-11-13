"""v2 analysis (declared in DECLARATION_v2.md §4).
usage: python analyze_v2.py <v2 out dir> <v1 out dir> <grid_v2.json> <plan_v2_A.json> <v1 results.json> <out.json>

For every row: w_cert = Σ_sides min over every exactly verified certificate (v1 or v2, any level) at a grid point of
u = (E_up − E_LB)/(λ S);  w_F = the DMRG-referenced width over the chain points of the grid (no δG);
ρ = (w_cert − w_F)/(τ − w_F)  (ρ ≤ 1 ⟺ w_cert ≤ τ ⟺ CERTIFIED with no DMRG reference on the outer side).
Scope verdicts: ACCEPT if max ρ ≤ 1 (S1 also includes v1's ρ_H for H(4.0), H(6.0)), REJECT if max ρ ≥ 3, GRAY otherwise.
Gate: every verified n = 19 bound (v2 gate jobs) ≤ exact E₀ + 1e-9, else NO DECISION.
"""
import glob
import json
import os
import sys
from fractions import Fraction

V2, V1, GRID, PLAN, V1RES, RES = sys.argv[1:7]
grid = json.load(open(GRID))
plan = json.load(open(PLAN))
v1res = json.load(open(V1RES))


def key(n, kind, Jz, sigma, lam):
    return (int(n), kind, Fraction(str(Jz)), int(sigma), Fraction(str(lam)))


certs = {}
for d, tag in ((os.path.join(V1, "jobs"), "v1"), (os.path.join(V2, "jobs"), "v2")):
    for vf in glob.glob(os.path.join(d, "*_ver.json")):
        jid = os.path.basename(vf)[:-9]
        v = json.load(open(vf))
        if not v.get("ok"):
            continue
        t = json.load(open(os.path.join(d, jid + "_task.json")))
        n = 115 if "n115_" in jid else (57 if "n57_" in jid else 19)
        certs.setdefault(key(n, t["kind"], t["Jz"], t["sigma"], t["lam"]), []).append(
            dict(E_LB=v["E_LB_float_floor"], E_exact=v["E_LB_exact"], level=t["clusters"], src="%s:%s" % (tag, jid)))
state = {}
sp = os.path.join(V2, "state_v2.json")
if os.path.exists(sp):
    state = json.load(open(sp))["sides"]

rows = []
for g in grid:
    rk = "%d_%.1f_%s" % (g["n"], g["Jz"], g["label"])
    out = dict(scope=g["scope"], n=g["n"], Jz=g["Jz"], label=g["label"], tau=g["tau"], E_up=g["E_up"], w_F=g["w_F"],
               s_req=g["s_req"], sides={})
    ok = True
    for s in "+-":
        sg = g["sides"][s]["sigma"]
        best = None
        ncomp = 0
        for q in g["sides"][s]["pts"]:
            for c in certs.get(key(g["n"], g["label"], g["Jz"], sg, q["lam"]), []):
                ncomp += 1
                u = (g["E_up"] - c["E_LB"]) / (q["lam_f"] * g["S"])
                ref = q["F"] if q["F"] is not None else q["F_up"]
                if best is None or u < best["u"]:
                    best = dict(u=u, lam=q["lam_f"], kind=q["kind"], E_LB=c["E_LB"], level=c["level"], src=c["src"],
                                F_ref=ref, slack=ref - c["E_LB"], u_lb=q["u_lb"])
        st = state.get("%s|%s" % (rk, s), {})
        out["sides"][s] = dict(best=best, n_certificates=ncomp, bb_done=st.get("done"))
        ok &= best is not None
    if ok:
        w = out["sides"]["+"]["best"]["u"] + out["sides"]["-"]["best"]["u"]
        lo = -out["sides"]["-"]["best"]["u"]
        hi = out["sides"]["+"]["best"]["u"]
        if g["label"] == "Czz_bar" or True:
            pass
        out.update(w_cert=w, w_over_tau=w / g["tau"], rho=(w - g["w_F"]) / (g["tau"] - g["w_F"]),
                   certified=w <= g["tau"], interval=[lo, hi])
    rows.append(out)

gate = []
for p in plan:
    if p["scope"] != "G19":
        continue
    vf = os.path.join(V2, "jobs", p["id"] + "_ver.json")
    ef = os.path.join(V2, "jobs", p["id"] + "_ed.json")
    if os.path.exists(vf) and os.path.exists(ef):
        v = json.load(open(vf))
        e = json.load(open(ef))["E0"]
        if v.get("ok"):
            gate.append(dict(id=p["id"], E_LB=v["E_LB_float_floor"], E0=e, slack_true=e - v["E_LB_float_floor"]))
gate_ok = len(gate) >= 12 and all(x["slack_true"] >= -1e-9 for x in gate)

verd = {}
H1 = [v1res["H"][i]["levels"]["best"]["rho"] for i in range(2)]
for sc in ("S1", "S2", "S3"):
    R = [r for r in rows if r["scope"] == sc]
    rh = [r["rho"] for r in R if "rho" in r]
    if sc == "S1":
        rh = rh + H1
    complete = all("rho" in r for r in R)
    m = max(rh) if rh else None
    v = ("NO DECISION (gate)" if not gate_ok else ("INCOMPLETE" if not complete else
         ("ACCEPT" if m <= 1 else ("REJECT" if m >= 3 else "GRAY"))))
    verd[sc] = dict(rho_max=m, verdict=v, n_rows=len(R), n_certified=sum(1 for r in R if r.get("certified")),
                    complete=complete)
json.dump(dict(gate_v2=dict(passed=gate_ok, n=len(gate), max_slack_true=max([x["slack_true"] for x in gate] or [None]) if gate else None,
                            items=gate), verdicts=verd, rows=rows, H_v1_rho=H1), open(RES, "w"), indent=1)
print("gate v2 n=19 (%d jobs): %s" % (len(gate), gate_ok))
for r in rows:
    if "rho" not in r:
        print("%s n=%d Jz=%.1f %-8s INCOMPLETE" % (r["scope"], r["n"], r["Jz"], r["label"]))
        continue
    b = {s: r["sides"][s]["best"] for s in "+-"}
    print("%s n=%3d Jz=%.1f %-8s w_cert/tau %.3f (DMRG %.3f) rho %6.3f %s  interval [%.5f, %.5f] | + lam %.5f %s %s slack %.4f | - lam %.5f %s %s slack %.4f | bb %s/%s" % (
        r["scope"], r["n"], r["Jz"], r["label"], r["w_over_tau"], r["w_F"] / r["tau"], r["rho"],
        "CERT" if r["certified"] else "not ", r["interval"][0], r["interval"][1],
        b["+"]["lam"], b["+"]["kind"], b["+"]["level"], b["+"]["slack"], b["-"]["lam"], b["-"]["kind"], b["-"]["level"],
        b["-"]["slack"], r["sides"]["+"]["bb_done"], r["sides"]["-"]["bb_done"]))
for sc, v in verd.items():
    print("VERDICT %s: rho_max %s -> %s (%d/%d rows certified)" % (sc, "%.3f" % v["rho_max"] if v["rho_max"] is not None else "-",
                                                                 v["verdict"], v["n_certified"], v["n_rows"]))
