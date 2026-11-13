"""Fig. 2(b) addition (R7, 2026-11-09): the miss of the exact n = 19 order parameter against our n = 57 reference, in
units of tau, at every coupling where it is stored. No physics recomputed: reads
  phase3/full_runs/bias_law/out/results.json      n19_curve["57"]["rows"][*]  (J, small_truth)
  phase3/full_runs/final_tests/analysis/test_a.json  rows with n = 57          (J, small_truth)
and writes b_n19.dat (J miss_tau), sorted by J. Run from paper/figures/pgf_composite/ with python -B."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))  # J_next_paper/
BLW = os.path.join(ROOT, "phase3", "full_runs", "bias_law", "out", "results.json")
FTA = os.path.join(ROOT, "phase3", "full_runs", "final_tests", "analysis", "test_a.json")

blw = json.load(open(BLW, encoding="utf-8"))
fta = json.load(open(FTA, encoding="utf-8"))

pts = {}
for r in blw["n19_curve"]["57"]["rows"]:
    pts[round(r["J"], 3)] = ("blw", r["small_truth"])
for r in fta["rows"]:
    if r.get("n") == 57:
        J = round(r["J"], 3)
        assert J not in pts, "coupling stored twice: %s" % J
        pts[J] = ("fta", r["small_truth"])

rows = sorted(pts.items())
log = []
log.append("points: %d (%d from bias_law n19_curve, %d from final_tests test_a)" % (
    len(rows), sum(1 for _, v in rows if v[0] == "blw"), sum(1 for _, v in rows if v[0] == "fta")))
for J, (src, v) in rows:
    log.append("  J=%.1f  miss/tau=%.4f  (%s)" % (J, v, src))

# checks against the numbers printed in main.tex
d = dict((J, v) for J, (_, v) in rows)
assert abs(d[3.2] - 0.1645) < 5e-5, d[3.2]                      # fta:rows[n=57,J=3.2].small_truth
assert abs(d[1.4] - 1.0526) < 5e-5 and abs(d[1.1] - 1.4727) < 5e-5  # blw:nulls.small_truth_test_57_min/max
assert abs(d[1.6] - 0.809) < 5e-4                               # blw:n19_curve.57.rows[J=1.6].small_truth
cert = [d[J] for J in d if J >= 3.2]
assert max(cert) < 0.2, max(cert)                               # "within a fifth of the tolerance" where certified (J >= J* = 3.2)
assert all(d[J] > 1.0 for J in (1.1, 1.2, 1.3, 1.4))             # "misses by more than a tolerance" at the test couplings
log.append("PASS  J=3.2: 0.1645; J=1.1-1.4: 1.0526-1.4727 (> 1); J=1.6: 0.809")
log.append("PASS  max over J >= 3.2 (certified range at n = 57): %.4f < 0.2" % max(cert))

with open(os.path.join(HERE, "b_n19.dat"), "w", encoding="utf-8") as f:
    f.write("J miss\n")
    for J, (_, v) in rows:
        f.write("%.1f %.6f\n" % (J, v))
with open(os.path.join(HERE, "export_n19_check.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log) + "\n")
print("\n".join(log))
