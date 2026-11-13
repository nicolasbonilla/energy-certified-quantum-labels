"""Absolute widths of the benchmark's prediction intervals in units of tau = 0.08 (final-fix pass, 2026-11-04).
Reads phase3/full_runs/learning/analysis/learn_M{1,2}_D_O.json (read-only); delta e = 5e-3, realistic (gen5) and
shifted (advL5) label sets; SC = standard split conformal, CSC = certified split conformal; mean width over splits.
  python -I widths_huang.py <J_next_paper root>"""
import json, os, sys
root = sys.argv[1]
tau = 0.08
out = {}
for m in ("M1", "M2"):
    c = json.load(open(os.path.join(root, "phase3/full_runs/learning/analysis/learn_%s_D_O.json" % m)))["coverage"]
    for s in ("gen5", "advL5"):
        for meth in ("SC", "CSC"):
            for cl in ("avg", "nn", "diag"):
                out["%s|%s|%s|%s" % (m, s, meth, cl)] = c[s][meth][cl]["wid_id"] / tau
for k, v in out.items():
    print("%-22s width/tau %.2f" % (k, v))
for meth in ("SC", "CSC"):
    for cl in ("avg", "nn"):
        v = [out[k] for k in out if k.split("|")[2] == meth and k.split("|")[3] == cl]
        print("range %s %s: %.2f-%.2f" % (meth, cl, min(v), max(v)))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "widths_huang.json"), "w"), indent=1)
