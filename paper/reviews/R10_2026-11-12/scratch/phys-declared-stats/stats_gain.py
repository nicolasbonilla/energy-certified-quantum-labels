"""R10 reviewer phys-declared-stats: paired statistics over the six test instances for the comparisons quoted in
main.tex 727-729 and 743-744 (from recompute_table2_out.json, written by recompute_table2.py)."""
import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "recompute_table2_out.json")))
T975 = 2.5705818366147395     # Student t, 5 degrees of freedom, 97.5 %
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def signrank_p(d):
    """exact two-sided Wilcoxon signed-rank p value for n = 6 (no ties assumed)"""
    d = np.asarray(d, float)
    r = np.argsort(np.argsort(np.abs(d))) + 1
    w = float(r[d > 0].sum())
    n = len(d)
    tot = n * (n + 1) / 2
    cnt = 0
    alls = 0
    for signs in itertools.product([0, 1], repeat=n):
        s = sum(k + 1 for k, b in enumerate(signs) if b)
        alls += 1
        if abs(s - tot / 2) >= abs(w - tot / 2) - 1e-12:
            cnt += 1
    return cnt / alls


def tci(x):
    x = np.asarray(x, float)
    h = T975 * x.std(ddof=1) / math.sqrt(len(x))
    return x.mean() - h, x.mean() + h


P("paired comparisons over the six test instances (per-instance mean miss over 121 labels)")
for J in ("1.6", "2.5"):
    p = R[J]["per"]
    for a_name, b_name in (("q_top", "reg"), ("q_kry", "reg"), ("q_top_noref", "reg"), ("q_top", "open19"), ("q_top", "emb19"), ("q_kry", "emb19"), ("label", "q_top")):
        a, b = np.array(p[a_name]), np.array(p[b_name])
        gain = 100 * (1 - a / b)
        lo, hi = tci(gain)
        wins = int((a < b).sum())
        psign = 2 * sum(math.comb(6, k) for k in range(max(wins, 6 - wins), 7)) / 64
        P("Jz %s  %-11s vs %-6s: change of the mean %+7.1f %% ; per-instance %s ; t interval of the per-instance change [%+.1f, %+.1f] %% ; better in %d/6 (sign test p = %.3f; signed-rank p = %.3f)" % (
            J, a_name, b_name, -100 * (1 - a.mean() / b.mean()), np.round(-gain, 1).tolist(), -hi, -lo, wins, min(1.0, psign), signrank_p(b - a)))
    ps, pb = R[J]["per_site"], R[J]["per_bond"]
    for a_name, b_name in (("q_top", "reg"), ("q_kry", "reg")):
        for nm, pp in (("sites", ps), ("bonds", pb)):
            a, b = np.array(pp[a_name]), np.array(pp[b_name])
            P("Jz %s  %-6s vs %-4s, %s only: means %.3f vs %.3f (%+.1f %%), better in %d/6" % (J, a_name, b_name, nm, a.mean(), b.mean(), 100 * (a.mean() / b.mean() - 1), int((a < b).sum())))
    for a_name in ("q_top", "q_kry"):
        r = np.array(p[a_name]) / np.array(p["emb19"])
        lo, hi = tci(r)
        P("Jz %s  per-instance ratio %s / emb19: %s ; mean %.2f, t interval [%.2f, %.2f]" % (J, a_name, np.round(r, 2).tolist(), r.mean(), lo, hi))
P("")
P("Table II with a spread: mean [min, max] over the six instances, and standard error of the mean")
names = [("label", "Label as generated"), ("q_top", "Label with correction (primary)"), ("q_kry", "Same, trained on first stage at n=19"),
         ("reg", "Regression on local couplings"), ("open19", "Open cluster, 19 sites"), ("emb13", "Embedded cluster, 13 sites"),
         ("emb19", "Embedded cluster, 19 sites (best)"), ("dmrg32", "DMRG on target, bond dimension 32")]
for k, nm in names:
    out = []
    for J in ("1.6", "2.5"):
        a = np.array(R[J]["per"][k])
        out.append("%.4g [%.3g, %.3g] se %.2g" % (a.mean(), a.min(), a.max(), a.std(ddof=1) / math.sqrt(6)))
    P("  %-38s Jz=1.6: %-34s Jz=2.5: %s" % (nm, out[0], out[1]))
open(os.path.join(HERE, "stats_gain_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
