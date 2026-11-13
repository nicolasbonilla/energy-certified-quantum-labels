# R11 fix pass (fixer FL, 2026-11-13): copy of the script `recompute_e1.py` of the reader hostile-B
# (paper/reviews/R11_2026-11-13/scratch/hostile-B/scripts/), stored here so that the numbers it supports can be
# cited from the run folder. Changed: only this header, the default paths (the real_data folder is found from
# this file's location when no argument is given) and the name of the imported module. Output: fl_learn_recompute_e1_out.txt
# hostile-B (R11): the secondary constructive test on the sets extended by the later certificates (n = 115), with my
# own f3 code (recompute_learning.py) and the stored extended sets file.
# usage: python -B -I -X utf8 recompute_e1.py <real_data_dir> <scripts_dir>
import json, sys
sys.argv_keep = list(sys.argv)
RD = sys.argv[1] if len(sys.argv) > 1 else __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", ".."))
sys.path.insert(0, sys.argv[2] if len(sys.argv) > 2 else __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import fl_learn_recompute as rl

sets_all = json.load(open("%s/e1/learn_e1/S_sets_E1.json" % RD, encoding="utf-8"))["sizes"]
for n in (57, 115):
    D = rl.load(n); sets = sets_all[str(n)]
    ys = D["ys"]; tau = {J: 0.06 * abs(ys[J]) for J in D["Js"]}
    print("n=%d extended sets: S %d (%.1f-%.1f), S_3_4 %d, S_1_2 %d, S_p %s" % (
        n, len(sets["S"]), min(sets["S"]), max(sets["S"]), len(sets["S_3_4"]), len(sets["S_1_2"]), sets["S_p_name"]))
    if n == 57:
        continue
    for name in ("S_1_2", "S_3_4", "S"):
        rl.f3(D, sets, name)
        T = sorted(sets[name]); ch = ys[max(T)] - ys[min(T)]
        print("   set %s: Jz %.1f-%.1f ; truth change %.4f-%.4f tau" % (name, min(T), max(T), ch / max(tau[J] for J in T), ch / min(tau[J] for J in T)))
