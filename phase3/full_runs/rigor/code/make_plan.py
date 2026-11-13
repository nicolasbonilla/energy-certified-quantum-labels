"""Build the declared job list from outputs/requirement.json.  usage: python make_plan.py <requirement.json> <plan.json>
Items: n = 57 rows m_s and Czz_bar at Jz = 4.0 and 6.0 (decisive chain points of both signs at E_up + s_req) and H(4.0),
H(6.0); n = 19 calibration: the same 10 specs (exact diagonalization reference) plus the n = 19 decisive points of the
Jz = 4.0 rows of the map (gate G1 rows).  Levels: eball2 (main), vball2 (hierarchy check)."""
import json
import sys
from fractions import Fraction

R = json.load(open(sys.argv[1]))
OPT = dict(K=32, maxiter=600, betas=[30, 300, 3000, 30000, 100000], use_mu=True)


def items_for(n, Jz):
    out = []
    for lab in ("m_s", "Czz_bar"):
        r = next(x for x in R if x["n"] == n and x["Jz"] == Jz and x["label"] == lab)
        for s, sg in (("+", 1), ("-", -1)):
            d = r["decisive"][s]
            out.append(dict(name="%s_%s%s" % (lab, "p" if sg > 0 else "m", ("%.1f" % Jz)), kind=lab, Jz=repr(Jz),
                            sigma=sg, lam=str(Fraction(d["lam"])), F_ref=d["F"], row=(n, Jz, lab)))
    return out


plan = []
specs57 = items_for(57, 4.0) + items_for(57, 6.0)
E0 = {J: next(x for x in R if x["n"] == 57 and x["Jz"] == J)["E0"] for J in (4.0, 6.0)}
specs57 += [dict(name="H_4.0", kind="H", Jz="4.0", sigma=0, lam="0", F_ref=E0[4.0], row=None),
            dict(name="H_6.0", kind="H", Jz="6.0", sigma=0, lam="0", F_ref=E0[6.0], row=None)]
specs19 = [dict(s, F_ref=None, row=None) for s in specs57]
r19 = items_for(19, 4.0)
E019 = next(x for x in R if x["n"] == 19 and x["Jz"] == 4.0)["E0"]
specs19 += [dict(s, name="G1_" + s["name"]) for s in r19]
for level in ("eball2", "vball2"):
    for s in specs57:
        task = dict(OPT, kind=s["kind"], Jz=s["Jz"], sigma=s["sigma"], lam=s["lam"], clusters=level)
        plan.append(dict(id="n57_%s_%s" % (level, s["name"]), graph="hh_d5.json", task=task, ed=False,
                         F_ref=s["F_ref"], row=s["row"], n=57))
for level in ("eball2", "vball2"):
    for s in specs19:
        task = dict(OPT, kind=s["kind"], Jz=s["Jz"], sigma=s["sigma"], lam=s["lam"], clusters=level)
        plan.append(dict(id="n19_%s_%s" % (level, s["name"]), graph="hh_d3.json", task=task, ed=(level == "eball2"),
                         F_ref=s["F_ref"], row=s["row"], n=19))
# order: n = 57 eball2 first (longest), then n = 19, then n = 57 vball2
order = [p for p in plan if p["n"] == 57 and "eball2" in p["id"]] + [p for p in plan if p["n"] == 19] + \
        [p for p in plan if p["n"] == 57 and "vball2" in p["id"]]
json.dump(order, open(sys.argv[2], "w"), indent=1)
print(len(order), "jobs")
for p in order:
    print(p["id"], p["task"]["kind"], p["task"]["Jz"], p["task"]["sigma"], p["task"]["lam"], p["F_ref"])
