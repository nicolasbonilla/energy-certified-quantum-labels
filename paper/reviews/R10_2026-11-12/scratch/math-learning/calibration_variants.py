"""Reviewer math-learning (R10): does the "passes validation, misses the truth" result depend on the plain jackknife?
Own implementation (own_lib.py), n = 57, cubic model, m_s, emulated labels.

  1. plain jackknife (the paper's), jackknife+ and jackknife-minmax (Barber et al.) for m_s, in distribution
     (one coupling held out as the query, the other nine for training and calibration).
  2. the paper's robustness check: a single split with 3 calibration couplings, all 120 choices, test range.
  3. per-coupling coverage of the new emulated site labels by the plain jackknife (what "90 %" is made of).

  python -B calibration_variants.py > calibration_variants_out.txt
"""
import itertools
import math

import numpy as np

import own_lib as L

n = 57
eta, D = L.load_labels(n)
Js = sorted(D)
R = [j for j in Js if j >= L.TRAIN_MIN]
od = [j for j in Js if j in L.OOD]
y = {j: L.ms(D[j]["Zl"], eta) for j in Js}
ys = {j: L.ms(D[j]["Zr"], eta) for j in Js}
tau = {j: L.TAU_REL * abs(ys[j]) for j in Js}
ALPHA = L.ALPHA


def fit_pred(tr, x):
    return float(L.coef_vec(tr, x) @ np.array([y[j] for j in tr]))


print("1. m_s, cubic, emulated labels: intervals at the held-out coupling t from the other nine (N = 9, alpha = 0.1)")
print("   %-4s | %-28s | %-28s | %-28s" % ("Jz", "jackknife  w/tau  emu truth", "jackknife+ w/tau  emu truth", "minmax     w/tau  emu truth"))
tot = {k: [0, 0, []] for k in ("jk", "jk+", "mm")}
for t in R:
    tr = [j for j in R if j != t]
    N = len(tr)
    f_all = fit_pred(tr, t)
    f_loo_at_t, res = [], []
    for k in tr:
        tk = [j for j in tr if j != k]
        res.append(abs(fit_pred(tk, k) - y[k]))
        f_loo_at_t.append(fit_pred(tk, t))
    res, f_loo_at_t = np.array(res), np.array(f_loo_at_t)
    kq = min(N, int(math.ceil((1 - ALPHA) * (N + 1) - 1e-12)))          # 9 of 9
    kl = max(1, int(math.floor(ALPHA * (N + 1) + 1e-12)))               # 1 of 9
    q = np.sort(res)[kq - 1]
    iv = {"jk": (f_all - q, f_all + q),
          "jk+": (np.sort(f_loo_at_t - res)[kl - 1], np.sort(f_loo_at_t + res)[kq - 1]),
          "mm": (f_loo_at_t.min() - q, f_loo_at_t.max() + q)}
    line = "   %-4.1f" % t
    for k in ("jk", "jk+", "mm"):
        lo, hi = iv[k]
        ce, ct = lo <= y[t] <= hi, lo <= ys[t] <= hi
        tot[k][0] += ce
        tot[k][1] += ct
        tot[k][2].append((hi - lo) / tau[t])
        line += " | %10.3f   %5s %5s    " % ((hi - lo) / tau[t], ce, ct)
    print(line)
for k, nm in (("jk", "plain jackknife (no guarantee)"), ("jk+", "jackknife+ (1 - 2 alpha = 0.8 under exchangeability)"),
              ("mm", "jackknife-minmax (1 - alpha = 0.9 under exchangeability)")):
    print("   %-55s covers new emulated m_s at %d of 10, the true m_s at %d of 10; median width %.3f tau (range %.3f-%.3f)"
          % (nm, tot[k][0], tot[k][1], np.median(tot[k][2]), min(tot[k][2]), max(tot[k][2])))

print()
print("2. single split, 3 calibration couplings, all C(10,3) = 120 choices, per-site labels, test range (paper: 0.22 / 0)")
ce, ct, kk = [], [], set()
for C in itertools.combinations(R, 3):
    T = [j for j in R if j not in C]
    Y = np.array([D[j]["Zl"] for j in T])
    sc = np.concatenate([np.abs(L.predict(T, Y, c) - D[c]["Zl"]) for c in C])
    q, lev, k, N = L.conf_q(sc)
    kk.add((k, N))
    for t in od:
        p = L.predict(T, Y, t)
        ce.append(np.mean(np.abs(p - D[t]["Zl"]) <= q))
        ct.append(np.mean(np.abs(p - D[t]["Zr"]) <= q))
print("   coverage of new emulated site labels %.4f, of the true ones %.4f; quantile index (k, N) = %s" % (
    np.mean(ce), np.mean(ct), sorted(kk)))

print()
print("3. plain jackknife, per-site labels pooled: coverage of the new emulated site labels by held-out coupling")
cov = []
for t in R:
    tr = [j for j in R if j != t]
    rz = []
    for k in tr:
        tk = [j for j in tr if j != k]
        rz.append(np.abs(L.predict(tk, np.array([D[j]["Zl"] for j in tk]), k) - D[k]["Zl"]))
    q, lev, kq, N = L.conf_q(np.concatenate(rz))
    p = L.predict(tr, np.array([D[j]["Zl"] for j in tr]), t)
    c = float(np.mean(np.abs(p - D[t]["Zl"]) <= q))
    cov.append(c)
    print("   Jz=%.1f  %.3f   (true site labels: %.3f)" % (t, c, float(np.mean(np.abs(p - D[t]["Zr"]) <= q))))
print("   mean %.4f; interior couplings (1.8-5.0) mean %.4f; the two end couplings %.3f and %.3f" % (
    np.mean(cov), np.mean(cov[1:-1]), cov[0], cov[-1]))
