# R11 fix pass (fixer FL, 2026-11-13): copy of the script `recompute_learning.py` of the reader hostile-B
# (paper/reviews/R11_2026-11-13/scratch/hostile-B/scripts/), stored here so that the numbers it supports can be
# cited from the run folder. Changed: only this header, the default paths (the real_data folder is found from
# this file's location when no argument is given) and the name of the imported module. Output: fl_learn_recompute_out.txt
# hostile-B (R11, 2026-11-13): independent recomputation of the learning numbers of main.tex Sec. VI A / supplement S19
# from the converted public data and the stored intervals. Own code; imports nothing from the project.
# usage: python -B -I -X utf8 recompute_learning.py <real_data_dir>
import json, math, sys
from fractions import Fraction

import numpy as np

RD = sys.argv[1] if len(sys.argv) > 1 else __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", ".."))
ALPHA = 0.1
RIDGE = 1e-8
SEED0 = 1845216616          # learn_real.json: "seed" (from the checksum of the declaration)
SET_CODE = {"S": 0, "S_3_4": 1, "S_1_2": 2}


def jk(J):
    return "%.1f" % J


def load(n):
    d = json.load(open("%s/converted/real_n%d.json" % (RD, n), encoding="utf-8"))
    lm = json.load(open("%s/converted/lattice_maps.json" % RD, encoding="utf-8"))["maps"][str(n)]
    col = np.array(lm["colour_with_node0_as_1"], float)
    eta = np.where(col > 0.5, 1.0, -1.0)
    assert int((eta > 0).sum()) in (33, 67)
    Js = [round(1.1 + 0.1 * i, 1) for i in range(50)]
    y = {}; ys = {}; Zl = {}; Zr = {}; E = {}; E0 = {}; E1 = {}; Efirst = {}
    for J in Js:
        a = d["skqd_random_flip"][jk(J)]; b = d["dmrg"][jk(J)]
        Zl[J] = np.array(a["z_basis_opt"], float); Zr[J] = np.array(b["z"], float)
        y[J] = float(eta @ Zl[J] / n); ys[J] = float(eta @ Zr[J] / n)
        E[J] = a["final_global_energy"]; Efirst[J] = a["ground_state_energy"]
        E0[J] = b["ground_state_energy"]; E1[J] = b["e1"]
    return dict(n=n, Js=Js, eta=eta, y=y, ys=ys, Zl=Zl, Zr=Zr, E=E, E0=E0, E1=E1, Efirst=Efirst, raw=d)


def kidx(m, alpha=ALPHA):
    return int(math.ceil(Fraction(m + 1) * (1 - Fraction(str(alpha)))))


def kth(vals, alpha=ALPHA):
    s = np.sort(np.asarray(vals, float)); m = len(s); k = kidx(m, alpha)
    return float(s[-1] if k > m else s[k - 1])


def cubic_coef(xtr, xq):
    X = np.vander(1.0 / np.asarray(xtr, float), 4); v = np.vander(np.array([1.0 / xq]), 4)
    return (v @ np.linalg.solve(X.T @ X + RIDGE * np.eye(4), X.T))[0]


def cubic_pred(xtr, lab, xq):
    return float(cubic_coef(xtr, xq) @ np.array([lab[j] for j in xtr]))


def jack_q(xtr, lab):
    """plain jackknife over the couplings xtr: k-th smallest leave-one-out residual of m_s."""
    res = []
    for j in xtr:
        rest = [i for i in xtr if i != j]
        res.append(abs(lab[j] - cubic_pred(rest, lab, j)))
    return kth(res)


def f1(D, lab, name):
    Js = D["Js"]; ys = D["ys"]; tau = {J: 0.06 * abs(ys[J]) for J in Js}
    train = [J for J in Js if J >= 1.6 - 1e-9]; test = [J for J in Js if J <= 1.4 + 1e-9]
    out = {}
    # test range
    q = jack_q(train, lab)
    miss = [abs(cubic_pred(train, lab, J) - ys[J]) / tau[J] for J in test]
    cov_t = sum(abs(cubic_pred(train, lab, J) - ys[J]) <= q for J in test)
    cov_l = sum(abs(cubic_pred(train, lab, J) - D["y"][J]) <= q for J in test)
    out["test"] = dict(miss_tau=[round(m, 4) for m in miss], truth_in=int(cov_t), public_label_in=int(cov_l),
                       width_tau=[round(2 * q / tau[J], 4) for J in test])
    # training range, each coupling held out in turn
    nl = nt = 0; wid = []; mis = []
    for J in train:
        rest = [i for i in train if i != J]
        qj = jack_q(rest, lab); p = cubic_pred(rest, lab, J)
        nl += abs(p - lab[J]) <= qj; nt += abs(p - ys[J]) <= qj
        wid.append(2 * qj / tau[J]); mis.append(abs(p - ys[J]) / tau[J])
    out["ind"] = dict(n=len(train), held_out_label_in=int(nl), truth_in=int(nt), width_tau=[round(min(wid), 4), round(max(wid), 4)],
                      miss_tau=[round(min(mis), 4), round(max(mis), 4)])
    print("f1 cubic, n=%d, labels=%s:" % (D["n"], name), json.dumps(out))
    return out


def m1_coef(xtr, xq):
    xtr = np.asarray(xtr, float)
    return np.array([1.0, 1 / xq]) @ np.linalg.pinv(np.column_stack([np.ones(len(xtr)), 1 / xtr])), 0.0


def m2_coef(xtr, xq):
    xtr = np.asarray(xtr, float)
    a = np.array([1 / xq ** 2, 1 / xq ** 4]) @ np.linalg.pinv(np.column_stack([1 / xtr ** 2, 1 / xtr ** 4]))
    return a, 1.0 - float(a.sum())


def f3(D, sets, set_name, verbose_split=None, score="interval"):
    n = D["n"]; Js = D["Js"]; y = D["y"]; ys = D["ys"]; tau = {J: 0.06 * abs(ys[J]) for J in Js}
    T = sorted(sets[set_name]); m = len(T)
    ntr, ncal = (6, 12) if m >= 20 else (4, 9)
    iv = sets["intervals"]
    ex = {J: (iv[jk(J)]["exact"]["lo"], iv[jk(J)]["exact"]["hi"]) for J in T}
    train_all = [J for J in Js if J >= 1.6 - 1e-9]
    rng = np.random.default_rng([SEED0, n, SET_CODE[set_name]])
    res = {M: dict(W=0, C=0, pairs=0, wmin=9e9, wmax=0.0, miss=0.0, splits=0) for M in ("M1", "M2", "M0")}
    for s in range(200):
        p = rng.permutation(m)
        tr = sorted(T[i] for i in p[:ntr]); cal = sorted(T[i] for i in p[ntr:ntr + ncal]); qs = sorted(T[i] for i in p[ntr + ncal:])
        for M in ("M1", "M2", "M0"):
            xtr = sorted(set(train_all) - set(cal) - set(qs)) if M == "M0" else tr
            ytr = np.array([y[j] for j in xtr])

            def pred(x):
                if M == "M1":
                    a, c = m1_coef(xtr, x)
                elif M == "M2":
                    a, c = m2_coef(xtr, x)
                else:
                    a, c = cubic_coef(xtr, x), 0.0
                return c + float(a @ ytr)
            if score == "interval":
                sc = [max(abs(pred(j) - ex[j][0]), abs(pred(j) - ex[j][1])) for j in cal]
            else:                                    # standard score: distance to the public label
                sc = [abs(pred(j) - y[j]) for j in cal]
            q = kth(sc)
            wt = [2 * q / tau[x] for x in qs]; cv = [abs(ys[x] - pred(x)) <= q for x in qs]
            r = res[M]
            r["W"] += all(w <= 1 for w in wt); r["C"] += sum(cv); r["pairs"] += len(qs); r["splits"] += 1
            r["wmin"] = min(r["wmin"], min(wt)); r["wmax"] = max(r["wmax"], max(wt))
            r["miss"] = max(r["miss"], max(abs(ys[x] - pred(x)) / tau[x] for x in qs))
            if verbose_split is not None and s == verbose_split and M == "M1" and score == "interval":
                print("  --- split %d of %s (n=%d), model M1, end to end ---" % (s, set_name, n))
                print("  training couplings:", tr); print("  calibration couplings:", cal); print("  query couplings:", qs)
                a, c = m1_coef(tr, 1.0)
                A = np.column_stack([np.ones(len(tr)), 1 / np.array(tr)]); beta = np.linalg.lstsq(A, ytr, rcond=None)[0]
                print("  public m_s labels at training couplings:", [round(y[j], 6) for j in tr])
                print("  fitted line m_s = %.6f + %.6f / Jz" % (beta[0], beta[1]))
                for j, sj in zip(cal, sc):
                    print("   cal Jz=%.1f  f=%.6f  I=[%.6f, %.6f]  width/tau=%.4f  score=%.6f  (w/2=%.6f)" % (
                        j, pred(j), ex[j][0], ex[j][1], (ex[j][1] - ex[j][0]) / tau[j], sj, (ex[j][1] - ex[j][0]) / 2))
                print("  k = %d of m = %d  ->  q = %.15f ; floor w_(k)/2 = %.6f" % (kidx(len(cal)), len(cal), q, kth([ex[j][1] - ex[j][0] for j in cal]) / 2))
                for x, w, cc in zip(qs, wt, cv):
                    print("   query Jz=%.1f  f=%.6f  truth=%.6f  tau=%.6f  2q/tau=%.10f  |f-truth|/tau=%.4f  truth inside: %s" % (
                        x, pred(x), ys[x], tau[x], w, abs(pred(x) - ys[x]) / tau[x], cc))
    for M in ("M1", "M2", "M0"):
        r = res[M]
        print("f3 n=%d set=%s (%d couplings; %d/%d/%d) score=%s %s: (W) %d of %d splits; (C) %d of %d pairs; 2q/tau %.4f-%.4f; max miss %.4f" % (
            n, set_name, m, ntr, ncal, m - ntr - ncal, score, M, r["W"], r["splits"], r["C"], r["pairs"], r["wmin"], r["wmax"], r["miss"]))
    return res


def main():
    sets_all = json.load(open("%s/out/S_sets.json" % RD, encoding="utf-8"))["sizes"]
    for n in (57, 115):
        D = load(n); Js = D["Js"]; y = D["y"]; ys = D["ys"]; tau = {J: 0.06 * abs(ys[J]) for J in Js}
        sets = sets_all[str(n)]
        print("=" * 30, "n =", n)
        miss = {J: (y[J] - ys[J]) / tau[J] for J in Js}
        print("public m_s label minus authors' DMRG, in tau: Jz=1.1: %.4f ; Jz=1.6: %.4f (Delta=%.4f) ; Jz=6.0: %.4f ; all positive: %s ; n>tau up to Jz=%s" % (
            miss[1.1], miss[1.6], y[1.6] - ys[1.6], miss[6.0], all(v > 0 for v in miss.values()), max(J for J in Js if miss[J] > 1)))
        print("m_s at Jz=1.1: public %.5f, authors' DMRG %.5f" % (y[1.1], ys[1.1]))
        # f1
        f1(D, y, "public"); f1(D, ys, "DMRG (control)")
        # Jz = 1.5 apart
        train = [J for J in Js if J >= 1.6 - 1e-9]
        print("Jz=1.5 apart: cubic miss %.4f tau" % (abs(cubic_pred(train, y, 1.5) - ys[1.5]) / tau[1.5]))
        # filter
        S = sets["S"]; kept = [abs(miss[J]) for J in S]; dropped = [J for J in train if J not in S]
        print("filter: kept %d (Jz %.1f-%.1f), max miss kept %.4f tau; dropped %d, of which within tau: %d" % (
            len(S), min(S), max(S), max(kept), len(dropped), sum(abs(miss[J]) <= 1 for J in dropped)))
        # f2 floor
        iv = sets["intervals"]
        lw = {J: iv[jk(J)]["lower"]["hi"] - iv[jk(J)]["lower"]["lo"] for J in train}
        k = kidx(len(train)); fl = kth(list(lw.values()))
        widest = sorted(train, key=lambda J: -lw[J])[:4]
        print("f2: m=%d k=%d floor=%.6f ; widest four at %s ; floor/tau at 1.1-1.4: %s ; min over all couplings %.4f" % (
            len(train), k, fl, sorted(widest), [round(fl / tau[J], 4) for J in (1.1, 1.2, 1.3, 1.4)], min(fl / tau[J] for J in Js)))
        ho = [kth([lw[i] for i in train if i != J]) / tau[J] for J in train]
        print("f2 held out (m=44,k=%d): %.4f-%.4f" % (kidx(44), min(ho), max(ho)))
        # Prop 2(b) lower version for the cubic: scores with the lower intervals, leave-one-out predictions
        lo = {J: (iv[jk(J)]["lower"]["lo"], iv[jk(J)]["lower"]["hi"]) for J in train}
        sc = []
        for J in train:
            rest = [i for i in train if i != J]; p = cubic_pred(rest, y, J)
            sc.append(max(abs(p - lo[J][0]), abs(p - lo[J][1])))
        qb = kth(sc)
        print("Prop 2(b) cubic, lower widths, all 45 labels: q=%.5f ; 2q/tau at test %.4f-%.4f ; over all 49: %.4f-%.4f" % (
            qb, min(2 * qb / tau[J] for J in (1.1, 1.2, 1.3, 1.4)), max(2 * qb / tau[J] for J in (1.1, 1.2, 1.3, 1.4)),
            min(2 * qb / tau[J] for J in Js if J != 1.5), max(2 * qb / tau[J] for J in Js if J != 1.5)))
        # f3
        for name in ("S_1_2", "S_3_4", "S"):
            if len(sets[name]) < 15:
                print("f3 n=%d set=%s: %d couplings, not run" % (n, name, len(sets[name]))); continue
            f3(D, sets, name, verbose_split=0 if (n == 57 and name == "S_1_2") else None)
            T = sorted(sets[name])
            ch = ys[max(T)] - ys[min(T)]
            print("   truth change over the set: %.4f-%.4f tau ; exact widths %.4f-%.4f tau ; max label miss %.4f tau" % (
                ch / max(tau[J] for J in T), ch / min(tau[J] for J in T),
                min((iv[jk(J)]["exact"]["hi"] - iv[jk(J)]["exact"]["lo"]) / tau[J] for J in T),
                max((iv[jk(J)]["exact"]["hi"] - iv[jk(J)]["exact"]["lo"]) / tau[J] for J in T), max(abs(miss[J]) for J in T)))
        pname = sets["S_p_name"]
        f3(D, sets, pname, score="standard")
        print("truth change Jz 4 to 6: %.4f-%.4f tau" % ((ys[6.0] - ys[4.0]) / tau[6.0], (ys[6.0] - ys[4.0]) / tau[4.0]))


if __name__ == "__main__":
    main()
