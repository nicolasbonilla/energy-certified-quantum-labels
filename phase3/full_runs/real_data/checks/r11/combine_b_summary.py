"""combine_b_summary.py -- one page that collects the eight outputs of combine_b.py.

    python -B -I combine_b_summary.py        (writes combine_b_summary_out.txt next to this script)

POST HOC (see combine_b.py): the declared classical stack on 13-site clusters with the generated label and its energy
error added as inputs, against that stack without the label and against the best classical estimate (the embedded
19-site cluster). Misses are mean absolute misses over the labels of an instance, in units of 6 % of the mean absolute
label of each type, as in the table of the declared test. Every range is rounded OUTWARD to one decimal.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FAM = {"top": "primary estimate", "kry": "secondary estimate"}
lines = []


def P(s=""):
    print(s)
    lines.append(s)


def down(x):
    return math.floor(x * 10.0 + 1e-9) / 10.0


def up(x):
    return math.ceil(x * 10.0 - 1e-9) / 10.0


P("combine_b_summary.py: label + 13-site clusters against the stack without the label and against the embedded")
P("19-site cluster; 2 couplings x 2 label types x 2 label families = 8 cases, 6 test instances each")
P("")
res = {}
for fam in ("top", "kry"):
    for Jz in ("1.6", "2.5"):
        for typ in ("site", "bond"):
            d = json.load(open(os.path.join(HERE, "combine_b_J%s_%s_%s_out.json" % (Jz, typ, fam))))
            a = [r["combined"] for r in d["rows"]]
            b = [r["stack"] for r in d["rows"]]
            e = [r["emb19"] for r in d["rows"]]
            ma, mb, me = sum(a) / 6.0, sum(b) / 6.0, sum(e) / 6.0
            chg = 100.0 * (ma / mb - 1.0)
            nb = sum(1 for x, y in zip(a, b) if x < y)
            ne = sum(1 for x, y in zip(a, e) if x < y)
            res[(fam, Jz, typ)] = dict(chg=chg, nb=nb, ne=ne, ratio=ma / me)
            P("%-18s Jz = %s %-4s: combined %.4f, stack %.4f, change %+.1f %% (combined better in %d of 6); "
              "embedded 19-site cluster %.4f (combined better in %d of 6; combined / cluster = %.2f)" % (
                  FAM[fam], Jz, typ, ma, mb, chg, nb, me, ne, ma / me))
P("")
P("SUMMARY (changes in per cent of the miss of the stack without the label; ranges rounded outward)")
n_best = sum(v["ne"] for v in res.values())
P("  combined better than the embedded 19-site cluster: %d of 48 instances (0 of 6 in each of the 8 cases: %s)" % (
    n_best, all(v["ne"] == 0 for v in res.values())))
rt = [v["ratio"] for v in res.values()]
P("  miss of the combined model over the miss of the embedded 19-site cluster: %.1f to %.1f times" % (down(min(rt)), up(max(rt))))
top = [res[("top", J, t)]["chg"] for J in ("1.6", "2.5") for t in ("site", "bond")]
P("  primary estimate: worse than the stack without the label in all 4 cases, by %.1f to %.1f %%" % (down(min(top)), up(max(top))))
ks = [res[("kry", J, "site")] for J in ("1.6", "2.5")]
P("  secondary estimate, site labels: %.1f %% (Jz = 1.6) and %.1f %% (Jz = 2.5), better in %d of 6 and %d of 6 instances" % (
    ks[0]["chg"], ks[1]["chg"], ks[0]["nb"], ks[1]["nb"]))
kb = [res[("kry", J, "bond")] for J in ("1.6", "2.5")]
P("  secondary estimate, bond labels: %+.1f %% (Jz = 1.6) and %+.1f %% (Jz = 2.5), better in %d of 6 and %d of 6 instances" % (
    kb[0]["chg"], kb[1]["chg"], kb[0]["nb"], kb[1]["nb"]))
open(os.path.join(HERE, "combine_b_summary_out.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
