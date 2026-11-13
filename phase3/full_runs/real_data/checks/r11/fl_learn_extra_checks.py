# R11 fix pass (fixer FL, 2026-11-13): copy of the script `extra_checks.py` of the reader hostile-B
# (paper/reviews/R11_2026-11-13/scratch/hostile-B/scripts/), stored here so that the numbers it supports can be
# cited from the run folder. Changed: only this header, the default paths (the real_data folder is found from
# this file's location when no argument is given) and the name of the imported module. Output: fl_learn_extra_checks_out.txt
# hostile-B (R11): extra checks. (1) emulated first stage against the dataset's OWN first stage (public record holds
# the energy before the last step); (2) jackknife+ variant of the headline coverage counts; (3) lower bound on the miss
# of any model that reproduces the public labels to 3 % (the accuracy the dataset paper reports for its own model).
# usage: python -B -I -X utf8 extra_checks.py <real_data_dir>
import json, math, sys
from fractions import Fraction

import numpy as np

RD = sys.argv[1] if len(sys.argv) > 1 else __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", ".."))
ALPHA = 0.1; RIDGE = 1e-8


def jk(J):
    return "%.1f" % J


def load(n):
    d = json.load(open("%s/converted/real_n%d.json" % (RD, n), encoding="utf-8"))
    lm = json.load(open("%s/converted/lattice_maps.json" % RD, encoding="utf-8"))["maps"][str(n)]
    eta = np.where(np.array(lm["colour_with_node0_as_1"], float) > 0.5, 1.0, -1.0)
    Js = [round(1.1 + 0.1 * i, 1) for i in range(50)]
    y = {}; ys = {}; de = {}; def_ = {}
    for J in Js:
        a = d["skqd_random_flip"][jk(J)]; b = d["dmrg"][jk(J)]
        y[J] = float(eta @ np.array(a["z_basis_opt"]) / n); ys[J] = float(eta @ np.array(b["z"]) / n)
        de[J] = (a["final_global_energy"] - b["ground_state_energy"]) / n
        def_[J] = (a["ground_state_energy"] - b["ground_state_energy"]) / n
    return Js, y, ys, de, def_


def coef(xtr, xq):
    X = np.vander(1.0 / np.asarray(xtr, float), 4); v = np.vander(np.array([1.0 / xq]), 4)
    return (v @ np.linalg.solve(X.T @ X + RIDGE * np.eye(4), X.T))[0]


def pred(xtr, lab, xq):
    return float(coef(xtr, xq) @ np.array([lab[j] for j in xtr]))


def main():
    emu = json.load(open("%s/checks/emulation_vs_published_energy.json" % RD, encoding="utf-8"))["sizes"]
    for n in (57, 115):
        Js, y, ys, de, def_ = load(n)
        tau = {J: 0.06 * abs(ys[J]) for J in Js}
        print("=" * 20, "n =", n)
        # (1)
        r1 = []; r2 = []
        for row in emu[str(n)]["rows"]:
            J = row["Jz"]; r1.append(row["de_emulated"] / def_[J]); r2.append(row["de_emulated"] / de[J])
            print("  Jz=%.1f  de emulated %.5f | dataset first stage %.5f | dataset final %.5f | emu/first %.3f | emu/final %.3f" % (
                J, row["de_emulated"], def_[J], de[J], r1[-1], r2[-1]))
        print("emulated first stage over the dataset's own first stage: %.3f to %.3f (median %.3f); over final: %.3f to %.3f" % (
            min(r1), max(r1), float(np.median(r1)), min(r2), max(r2)))
        # (2) jackknife+ and split-style variants for the cubic, training range
        train = [J for J in Js if J >= 1.6 - 1e-9]
        for name, lab in (("public", y), ("DMRG control", ys)):
            nl = nt = 0; wid = []
            for J in train:
                rest = [i for i in train if i != J]; m = len(rest)
                lo = []; hi = []
                for i in rest:
                    r2_ = [k for k in rest if k != i]
                    R = abs(lab[i] - pred(r2_, lab, i)); mu = pred(r2_, lab, J)
                    lo.append(mu - R); hi.append(mu + R)
                kk = int(math.ceil(Fraction(m + 1) * (1 - Fraction(str(ALPHA)))))
                L = np.sort(lo)[m - kk]            # floor(alpha (m+1))-th smallest of mu - R
                U = np.sort(hi)[kk - 1]            # ceil((1-alpha)(m+1))-th smallest of mu + R
                nl += L <= lab[J] <= U; nt += L <= ys[J] <= U; wid.append((U - L) / tau[J])
            print("jackknife+ (Barber et al.), cubic, labels=%s: held-out label inside %d of 45; truth inside %d of 45; width %.4f-%.4f tau" % (
                name, nl, nt, min(wid), max(wid)))
        # (3)
        for J in (1.1, 1.2, 1.3, 1.4):
            rel = (y[J] - ys[J]) / ys[J]
            lb = (0.97 * y[J] - ys[J])
            print("  Jz=%.1f public m_s %.5f, authors' DMRG %.5f: label %.1f %% above (%.2f tau); a model within 3 %% of the label is at least %.1f %% = %.2f tau above the DMRG value" % (
                J, y[J], ys[J], 100 * rel, (y[J] - ys[J]) / tau[J], 100 * lb / ys[J], lb / tau[J]))


if __name__ == "__main__":
    main()
