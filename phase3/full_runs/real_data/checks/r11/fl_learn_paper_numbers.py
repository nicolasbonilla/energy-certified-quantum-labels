# R11 fix pass (fixer FL, 2026-11-13). The numbers that the fix pass adds to Sec. VI A of the main text and to
# Sec. S19 of the Supplement, recomputed from the converted public data and the stored sets, and printed in the
# rounding used in the paper (ranges and bounds outward, the rule named on each line), so that every printed string
# can be found in this script's output.
#
# Three post hoc checks, none of them part of the declared analysis:
#   A. the size of the miss behind "the truth at none of the 45 couplings" (held-out cubic, plain jackknife);
#   B. the same counts with the jackknife+ of Barber et al. (level 1 - 2 alpha under exchangeability);
#   C. a bound for any model that reproduces the public labels of m_s to 3 % (the accuracy the dataset paper reports
#      for its own networks at the test couplings);
#   D. the widths of the exact intervals of the nested sets of the constructive test (stored sets, read only).
# The computations are those of the reader's scripts copied next to this file (fl_learn_recompute.py,
# fl_learn_miss_sizes.py, fl_learn_extra_checks.py); this file imports the first and repeats the few lines of the
# other two that it needs, so that it also prints which couplings are inside.
#
# usage (no argument; reads ../../converted and ../../out, writes nothing but its standard output):
#   python -B -I -X utf8 fl_learn_paper_numbers.py > fl_learn_paper_numbers_out.txt
import json
import math
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = sys.argv[:1]                     # the imported module takes its folder from its own location
import fl_learn_recompute as rl             # noqa: E402

RD = rl.RD
ALPHA = 0.1


def dn(x, d):
    return math.floor(x * 10 ** d + 1e-9) / 10 ** d


def up(x, d):
    return math.ceil(x * 10 ** d - 1e-9) / 10 ** d


def span(js):
    js = sorted(js)
    if not js:
        return "none"
    ok = all(abs(js[i + 1] - js[i] - 0.1) < 1e-9 for i in range(len(js) - 1))
    return ("Jz = %.1f-%.1f (%d couplings, consecutive)" % (js[0], js[-1], len(js))) if ok else str(js)


def jackknife_plus(train, lab, ys, tau):
    """jackknife+ interval of Barber et al. at each held-out coupling J of the training range, nested as in the
    plain-jackknife test: the 44 other couplings are the data, each left out in turn."""
    nl = nt = 0
    wid = []
    inside_truth = []
    outside_label = []
    for J in train:
        rest = [i for i in train if i != J]
        m = len(rest)
        lo = []
        hi = []
        for i in rest:
            r2 = [k for k in rest if k != i]
            R = abs(lab[i] - rl.cubic_pred(r2, lab, i))
            mu = rl.cubic_pred(r2, lab, J)
            lo.append(mu - R)
            hi.append(mu + R)
        kk = int(math.ceil(Fraction(m + 1) * (1 - Fraction(str(ALPHA)))))
        L = np.sort(lo)[m - kk]
        U = np.sort(hi)[kk - 1]
        a = L <= lab[J] <= U
        b = L <= ys[J] <= U
        nl += a
        nt += b
        wid.append((U - L) / tau[J])
        if b:
            inside_truth.append(J)
        if not a:
            outside_label.append(J)
    return int(nl), int(nt), min(wid), max(wid), inside_truth, outside_label


def main():
    sets_all = json.load(open(os.path.join(RD, "out", "S_sets.json"), encoding="utf-8"))["sizes"]
    print("fl_learn_paper_numbers.py (R11 fix pass, post hoc). Units: tau(x) = 0.06 |m_s^DMRG(x)|, the authors' DMRG.")
    print("Rounding: lower ends and 'at least' numbers down, upper ends and 'at most' numbers up; medians to nearest.")
    for n in (57, 115):
        D = rl.load(n)
        Js = D["Js"]
        y = D["y"]
        ys = D["ys"]
        tau = {J: 0.06 * abs(ys[J]) for J in Js}
        train = [J for J in Js if J >= 1.6 - 1e-9]
        print()
        print("=" * 24, "n = %d" % n, "=" * 24)
        # ---------------------------------------------------------------- A. size of the miss, plain jackknife
        rows = []
        for J in train:
            rest = [i for i in train if i != J]
            q = rl.jack_q(rest, y)
            p = rl.cubic_pred(rest, y, J)
            rows.append(dict(J=J, miss=abs(p - ys[J]) / tau[J], q=q / tau[J], lab_in=abs(p - y[J]) <= q,
                             tru_in=abs(p - ys[J]) <= q))
        miss = np.array([r["miss"] for r in rows])
        print("A. plain jackknife, cubic in 1/Jz trained on the public labels, each of the %d training couplings held out in turn" % len(train))
        print("   held-out labels inside: %d of %d ; truth inside: %d of %d" % (
            sum(r["lab_in"] for r in rows), len(rows), sum(r["tru_in"] for r in rows), len(rows)))
        print("   truth inside at: %s" % span([r["J"] for r in rows if r["tru_in"]]))
        print("   held-out labels outside at: %s" % [r["J"] for r in rows if not r["lab_in"]])
        print("   miss of the truth by the held-out prediction: min %.4f, median %.4f, max %.4f tau" % (
            miss.min(), float(np.median(miss)), miss.max()))
        print("   PRINTED: miss %.2f-%.2f tau (range rounded outward), median %.2f tau (to nearest)" % (
            dn(miss.min(), 2), up(miss.max(), 2), float(np.median(miss))))
        gt1 = [r["J"] for r in rows if r["miss"] > 1]
        gth = [r["J"] for r in rows if r["miss"] > 0.5]
        print("   miss above tau at %d couplings: %s" % (len(gt1), span(gt1)))
        print("   miss above tau/2 at %d couplings: %s" % (len(gth), span(gth)))
        print("   miss below 0.2 tau at %d couplings; below 0.1 tau at %d" % (int((miss < 0.2).sum()), int((miss < 0.1).sum())))
        late = [r["miss"] for r in rows if r["J"] >= 3.5 - 1e-9]
        print("   from Jz = 3.5 (%d couplings): miss %.4f-%.4f tau ; PRINTED: at most %.2f tau (rounded up)" % (
            len(late), min(late), max(late), up(max(late), 2)))
        qq = [r["q"] for r in rows]
        print("   half-width q: %.4f-%.4f tau ; width 2q: %.4f-%.4f tau ; PRINTED: half-widths %.3f-%.3f tau, widths %.2f-%.2f tau (outward)" % (
            min(qq), max(qq), 2 * min(qq), 2 * max(qq), dn(min(qq), 3), up(max(qq), 3), dn(2 * min(qq), 2), up(2 * max(qq), 2)))
        out = [r["miss"] - r["q"] for r in rows if not r["tru_in"]]
        print("   where the truth is outside, it is outside by %.4f to %.4f tau (miss minus half-width)" % (min(out), max(out)))
        out_late = [r["miss"] - r["q"] for r in rows if not r["tru_in"] and r["J"] >= 3.5 - 1e-9]
        if out_late:
            print("   from Jz = 3.5, where the truth is outside: outside by %.4f to %.4f tau ; PRINTED: at most %.2f tau (rounded up)" % (
                min(out_late), max(out_late), up(max(out_late), 2)))
        # ---------------------------------------------------------------- B. jackknife+
        print("B. jackknife+ (Barber, Candes, Ramdas, Tibshirani), same model and nesting, alpha = %.1f" % ALPHA)
        for name, lab in (("public labels", y), ("DMRG labels (control)", ys)):
            nl, nt, w0, w1, ins, outl = jackknife_plus(train, lab, ys, tau)
            print("   %s: held-out labels inside %d of %d ; truth inside %d of %d ; width %.4f-%.4f tau" % (
                name, nl, len(train), nt, len(train), w0, w1))
            print("      truth inside at: %s ; held-out labels outside at: %s" % (span(ins), outl))
            print("      PRINTED: %d labels and %d truths of %d ; widths %.3f-%.3f tau (range rounded outward)" % (
                nl, nt, len(train), dn(w0, 3), up(w1, 3)))
        # ---------------------------------------------------------------- C. any model within 3 % of the labels
        print("C. test couplings: the public label of m_s against the authors' DMRG, and a model within 3 % of the label")
        rel = []
        lb = []
        for J in (1.1, 1.2, 1.3, 1.4):
            r = 100 * (y[J] - ys[J]) / ys[J]
            b = (0.97 * y[J] - ys[J]) / tau[J]
            rel.append(r)
            lb.append(b)
            print("   Jz = %.1f: public m_s %.5f, DMRG %.5f, label above by %.4f %% (%.4f tau); 0.97 x label is above by %.4f tau" % (
                J, y[J], ys[J], r, (y[J] - ys[J]) / tau[J], b))
        print("   PRINTED: labels %.1f-%.1f %% above the DMRG values (range rounded outward); such a model is at least %.2f tau above (smallest of the four, rounded down)" % (
            dn(min(rel), 1), up(max(rel), 1), dn(min(lb), 2)))
        # ---------------------------------------------------------------- D. exact widths of the nested sets
        sets = sets_all[str(n)]
        iv = sets["intervals"]
        print("D. widths of the exact intervals of the nested sets (declared certificates; file out/S_sets.json)")
        for name in ("S_1_2", "S_3_4", "S"):
            T = sorted(sets[name])
            w = [(iv[rl.jk(J)]["exact"]["hi"] - iv[rl.jk(J)]["exact"]["lo"]) / tau[J] for J in T]
            print("   %-5s: %2d couplings, Jz = %.1f-%.1f, exact widths %.4f-%.4f tau ; PRINTED: at most %.2f tau (rounded up)" % (
                name, len(T), min(T), max(T), min(w), max(w), up(max(w), 2)))


if __name__ == "__main__":
    main()
