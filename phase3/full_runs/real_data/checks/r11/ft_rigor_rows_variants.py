# R11 fix pass (fixer FT, 2026-11-13): copy of paper/reviews/R10_2026-11-12/scratch/math-rigorous-bounds/rows_variants.py;
# only the paths were adapted (root found from this file's location; the JSON it writes is named ft_rigor_rows_variants.json). Output: ft_rigor_rows_variants_out.txt.
"""Reviewer math-rigorous-bounds (R10): the 18 rows with restricted certificate sets (exact arithmetic).
  all      : every verified certificate at a declared grid point (the paper's rule)
  v2only   : only certificates computed in the declared v2 run
  no_x     : without the v1 exploratory (post hoc, 'x_') certificates
  anylam   : every verified certificate of that (n, label, Jz, side), on the grid or not
Also: S values against the graph files, and outward-rounding check of the printed table (5 decimals / 3 digits).
"""
import glob, json, os
from fractions import Fraction
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, getcontext
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..")).replace("\\", "/")
RIG = ROOT + "/phase3/full_runs/rigor"
V1 = RIG + "/out_20261031T073328Z/out/jobs"
V2 = RIG + "/out_20261031T100015Z/out/jobs"
grid = json.load(open(RIG + "/outputs/grid_v2.json"))
GR = {57: json.load(open(RIG + "/code/graphs/hh_d5.json")), 115: json.load(open(RIG + "/code/graphs/hh_d7.json"))}
certs = []
for d, tag in ((V1, "v1"), (V2, "v2")):
    for vf in sorted(glob.glob(d + "/*_ver.json")):
        jid = os.path.basename(vf)[:-9]
        v = json.load(open(vf))
        if not v.get("ok"):
            continue
        t = v["task"]
        n = 115 if "n115_" in jid else (57 if "n57_" in jid else 19)
        certs.append(dict(n=n, kind=t["kind"], Jz=Fraction(t["Jz"]), sigma=int(t.get("sigma", 0)), lam=Fraction(t.get("lam", 0)),
                          E=Fraction(v["E_LB_exact"]), src=tag + ":" + jid, twoS=v["twoS"]))
print("twoS by n:", {n: sorted(set(c["twoS"] for c in certs if c["n"] == n)) for n in (19, 57, 115)})
for n, G in GR.items():
    print("n=%d: sites %d edges %d  n_up %d n_down %d" % (n, G["n"], len(G["mps"]["edges"]), G["n_up"], G["n_down"]))


def best(g, s, pred, grid_only=True):
    n, Jz, kind = g["n"], Fraction(str(g["Jz"])), g["label"]
    sg = g["sides"][s]["sigma"]
    gl = set(Fraction(q["lam"]) for q in g["sides"][s]["pts"])
    b = None
    for c in certs:
        if (c["n"], c["kind"], c["Jz"], c["sigma"]) != (n, kind, Jz, sg) or not pred(c):
            continue
        if grid_only and c["lam"] not in gl:
            continue
        u = (Fraction(g["E_up"]) - c["E"]) / (c["lam"] * Fraction(g["S"]))
        if b is None or u < b[0]:
            b = (u, c)
    return b


def q(x, nd, mode):
    return str(Decimal(x.numerator) / Decimal(x.denominator) if False else (Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal(1).scaleb(-nd), rounding=mode))


getcontext().prec = 60
variants = dict(all=lambda c: True, v2only=lambda c: c["src"].startswith("v2:"), no_x=lambda c: not c["src"].startswith("v1:x_"))
tab = []
for g in grid:
    G = GR[g["n"]]
    assert g["S"] == (G["n"] if g["label"] == "m_s" else len(G["mps"]["edges"])), "S is not n / number of edges"
    tau = Fraction(g["tau"])
    line = "n=%3d Jz=%.1f %-8s" % (g["n"], g["Jz"], g["label"])
    rec = dict(n=g["n"], Jz=g["Jz"], label=g["label"])
    for name, pred in variants.items():
        bp, bm = best(g, "+", pred), best(g, "-", pred)
        if bp is None or bm is None:
            line += "  %s: incomplete" % name
            rec[name] = None
            continue
        w = bp[0] + bm[0]
        line += "  %s: %.4f %s" % (name, float(w / tau), "C" if w <= tau else "n")
        rec[name] = float(w / tau)
        if name == "all":
            lo, hi = -bm[0], bp[0]
            rec.update(lo_out=q(lo, 5, ROUND_FLOOR), hi_out=q(hi, 5, ROUND_CEILING), lo_near="%.5f" % float(lo), hi_near="%.5f" % float(hi),
                       w_out=q(w / tau, 3, ROUND_CEILING), w_near="%.3f" % float(w / tau), w6="%.6f" % float(w / tau),
                       lo9="%.9f" % float(lo), hi9="%.9f" % float(hi))
    bp, bm = best(g, "+", lambda c: True, grid_only=False), best(g, "-", lambda c: True, grid_only=False)
    w = bp[0] + bm[0]
    line += "  anylam: %.4f %s" % (float(w / tau), "C" if w <= tau else "n")
    print(line)
    tab.append(rec)
print()
print("outward rounding of the printed table (rig_v2.tex prints nearest):")
for r in tab:
    flag = []
    if r["lo_out"] != r["lo_near"]:
        flag.append("lower end printed %s, proved >= %s (outward: %s)" % (r["lo_near"], r["lo9"], r["lo_out"]))
    if r["hi_out"] != r["hi_near"]:
        flag.append("upper end printed %s, proved <= %s (outward: %s)" % (r["hi_near"], r["hi9"], r["hi_out"]))
    if r["w_out"] != r["w_near"]:
        flag.append("w/tau printed %s, value %s (outward: %s)" % (r["w_near"], r["w6"], r["w_out"]))
    print("n=%3d Jz=%.1f %-8s %s" % (r["n"], r["Jz"], r["label"], "; ".join(flag) if flag else "outward as printed"))
json.dump(tab, open(os.path.dirname(os.path.abspath(__file__)) + "/ft_rigor_rows_variants.json", "w"), indent=1)
