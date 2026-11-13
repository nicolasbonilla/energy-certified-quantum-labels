# R11 fix pass (fixer FT, 2026-11-13): copy of paper/reviews/R10_2026-11-12/scratch/math-rigorous-bounds/mu_table.py;
# only the path of the rigor folder was adapted (now found from this file's location). Output: ft_rigor_mu_table_out.txt.
"""Reviewer math-rigorous-bounds (R10): for the 36 winning certificates, mu, the bare sum of the cluster bounds, the
certified E_LB = sum_k t_k - mu (n_up - n_down), the DMRG upper reference F at the same field and the relative slack.
Shows (i) that 'the sum of the cluster ground energies' alone is not a lower bound when mu > 0, (ii) the tightness."""
import json
from fractions import Fraction
import os
RIG = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rigor")).replace("\\", "/")
res = json.load(open(RIG + "/outputs/results_v2.json"))
bad = 0; rel = []; dmax = {57: 0.0, 115: 0.0}
print("row | side | mu | sum_k t_k | E_LB | DMRG upper reference F | sum_k t_k <= F ? | slack/|F| in %")
for r in res["rows"]:
    for s in "+-":
        b = r["sides"][s]["best"]
        tag, jid = b["src"].split(":", 1)
        d = RIG + ("/out_20261031T073328Z" if tag == "v1" else "/out_20261031T100015Z") + "/out/jobs/" + jid
        C = json.load(open(d + "_cert.json")); v = json.load(open(d + "_ver.json"))
        mu = Fraction(int(C["mu"]), 2 ** int(C["K"]))
        st = sum(Fraction(int(t), 2 ** int(C["K"])) for t in C["t"])
        E = Fraction(v["E_LB_exact"])
        assert st - mu * v["twoS"] == E
        ok = float(st) <= b["F_ref"]
        bad += (not ok)
        dmax[r["n"]] = max(dmax[r["n"]], abs(float(st - E)))
        rs = b["slack"] / abs(b["F_ref"]) * 100
        rel.append((rs, r["n"], r["Jz"], r["label"], s, b["slack"]))
        print("n=%3d Jz=%.1f %-8s %s  mu %+.5f  sum t %.4f  E_LB %.4f  F %.4f  %s  %.4f" % (r["n"], r["Jz"], r["label"], s, float(mu),
              float(st), float(E), b["F_ref"], "yes" if ok else "NO ", rs))
print("certificates where the bare sum of the cluster bounds lies ABOVE the DMRG sector energy: %d of 36" % bad)
print("largest |sum_k t_k - E_LB|: %.2f (n = 57), %.2f (n = 115)" % (dmax[57], dmax[115]))
rel.sort(reverse=True)
print("largest relative slacks:", [("%.4f%%" % a, n, J, lab, s, round(sl, 4)) for a, n, J, lab, s, sl in rel[:4]])
print("max over '+' sides and Czz sides: %.4f %% ; max over m_s '-' sides: %.4f %%" % (
    max(x[0] for x in rel if not (x[3] == "m_s" and x[4] == "-")), max(x[0] for x in rel if x[3] == "m_s" and x[4] == "-")))
