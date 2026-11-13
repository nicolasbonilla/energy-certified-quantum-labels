"""POST-HOC (DEVIATIONS 1): rigorous outer widths of the n = 57 m_s rows using every verified bound available on each
side (declared decisive points and the exploratory smaller-field points), min over points per side.
usage: python analyze_explore.py <out_dir/out> <plan.json> <plan_explore.json> <requirement.json> <out.json>"""
import json
import os
import sys

OUT, PLAN, PLANX, REQ, RES = sys.argv[1:6]
J = os.path.join(OUT, "jobs")
req = json.load(open(REQ))


def ver(jid):
    p = os.path.join(J, jid + "_ver.json")
    if not os.path.exists(p):
        return None
    v = json.load(open(p))
    return v if v.get("ok") else None


def ed(jid):
    p = os.path.join(J, jid + "_ed.json")
    return json.load(open(p))["E0"] if os.path.exists(p) else None


from fractions import Fraction
pts = []
for p in json.load(open(PLAN)) + json.load(open(PLANX)):
    t = p["task"]
    if t["kind"] != "m_s":
        continue
    v = ver(p["id"])
    pts.append(dict(id=p["id"], n=p["n"], Jz=float(Fraction(t["Jz"])), sigma=t["sigma"], lam=float(Fraction(t["lam"])),
                    level=t["clusters"], E_LB=(v["E_LB_float_floor"] if v else None), F=p.get("F_ref"),
                    E0_ED=ed(p["id"])))
# n = 19 exact values for the same specs (ED stored in the eball2 job of each spec)
edmap = {(q["Jz"], q["sigma"], round(q["lam"], 12)): q["E0_ED"] for q in pts if q["n"] == 19 and q["E0_ED"] is not None}
out = dict(points=[], rows=[])
for q in pts:
    if q["n"] == 19:
        q["E0_ED"] = edmap.get((q["Jz"], q["sigma"], round(q["lam"], 12)))
        q["slack_true"] = (q["E0_ED"] - q["E_LB"]) if (q["E0_ED"] is not None and q["E_LB"] is not None) else None
    else:
        q["slack_ref"] = (q["F"] - q["E_LB"]) if (q["F"] is not None and q["E_LB"] is not None) else None
    out["points"].append(q)
for Jz in (4.0, 6.0):
    r = next(x for x in req if x["n"] == 57 and x["Jz"] == Jz and x["label"] == "m_s")
    S, Eup, tau = 57.0, r["E_up"], r["tau"]
    side = {}
    for sg in (1, -1):
        cand = [q for q in pts if q["n"] == 57 and q["Jz"] == Jz and q["sigma"] == sg and q["E_LB"] is not None]
        if not cand:
            continue
        best = min(cand, key=lambda q: (Eup - q["E_LB"]) / (q["lam"] * S))
        side[sg] = dict(u=sg * (Eup - best["E_LB"]) / (best["lam"] * S), point=best["id"], lam=best["lam"],
                        E_LB=best["E_LB"], all=[(q["id"], q["lam"], q["E_LB"], (Eup - q["E_LB"]) / (q["lam"] * S))
                                                 for q in cand])
    if 1 in side and -1 in side:
        w = side[1]["u"] - side[-1]["u"]
        out["rows"].append(dict(Jz=Jz, tau=tau, E_up=Eup, w_rig=w, w_over_tau=w / tau, certified_rigorously=w <= tau,
                                interval=[side[-1]["u"], side[1]["u"]], sides=side, label="POST HOC (DEVIATIONS 1)"))
json.dump(out, open(RES, "w"), indent=1)
for q in out["points"]:
    print("%-40s n=%d Jz=%.1f s=%+d lam=%.5f E_LB=%s F=%s ED=%s" % (q["id"], q["n"], q["Jz"], q["sigma"], q["lam"],
          q["E_LB"], q.get("F"), q.get("E0_ED")))
for r in out["rows"]:
    print("m_s Jz=%.1f POST-HOC rigorous interval [%.4f, %.4f] width %.4f tau %.4f -> w/tau %.3f certified: %s" % (
        r["Jz"], r["interval"][0], r["interval"][1], r["w_rig"], r["tau"], r["w_over_tau"], r["certified_rigorously"]))
    for sg in (1, -1):
        for a in r["sides"][sg]["all"]:
            print("    side %+d %-40s lam %.5f E_LB %.5f u %.5f" % (sg, a[0], a[1], a[2], a[3]))
