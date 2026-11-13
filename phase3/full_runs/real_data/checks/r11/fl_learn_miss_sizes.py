# R11 fix pass (fixer FL, 2026-11-13): copy of the script `miss_sizes.py` of the reader hostile-B
# (paper/reviews/R11_2026-11-13/scratch/hostile-B/scripts/), stored here so that the numbers it supports can be
# cited from the run folder. Changed: only this header, the default paths (the real_data folder is found from
# this file's location when no argument is given) and the name of the imported module. Output: fl_learn_miss_sizes_out.txt
# hostile-B (R11): how large is the miss behind "the truth at none of the 45 couplings"?  Held-out cubic predictions in
# the training range against the authors' DMRG value, in units of tau; counts above tau/2 and tau; which held-out labels
# fall outside the jackknife interval.
# usage: python -B -I -X utf8 miss_sizes.py <real_data_dir> <scripts_dir>
import sys
sys.path.insert(0, sys.argv[2] if len(sys.argv) > 2 else __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
RD = sys.argv[1] if len(sys.argv) > 1 else __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", ".."))
import fl_learn_recompute as rl
import numpy as np

for n in (57, 115):
    D = rl.load(n); Js = D["Js"]; y = D["y"]; ys = D["ys"]; tau = {J: 0.06 * abs(ys[J]) for J in Js}
    train = [J for J in Js if J >= 1.6 - 1e-9]
    rows = []
    for J in train:
        rest = [i for i in train if i != J]
        q = rl.jack_q(rest, y); p = rl.cubic_pred(rest, y, J)
        rows.append((J, abs(p - ys[J]) / tau[J], q / tau[J], abs(p - y[J]) <= q, abs(p - ys[J]) <= q, abs(y[J] - ys[J]) / tau[J]))
    m = np.array([r[1] for r in rows])
    print("n=%d: held-out cubic miss of the truth: min %.4f, median %.4f, max %.4f tau" % (n, m.min(), np.median(m), m.max()))
    print("   > tau at %d couplings (%s); > tau/2 at %d (%s); < 0.2 tau at %d; < 0.1 tau at %d" % (
        (m > 1).sum(), [r[0] for r in rows if r[1] > 1], (m > 0.5).sum(), [r[0] for r in rows if r[1] > 0.5], (m < 0.2).sum(), (m < 0.1).sum()))
    print("   held-out labels outside the interval at:", [r[0] for r in rows if not r[3]], "; truth inside at:", [r[0] for r in rows if r[4]])
    print("   half-width q/tau: %.4f-%.4f ; smallest (miss - q)/tau over couplings with truth outside: %.4f" % (
        min(r[2] for r in rows), max(r[2] for r in rows), min(r[1] - r[2] for r in rows if not r[4])))
    print("   couplings from Jz=3.5: miss %.4f-%.4f tau" % (min(r[1] for r in rows if r[0] >= 3.5), max(r[1] for r in rows if r[0] >= 3.5)))
