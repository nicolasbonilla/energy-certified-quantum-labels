"""Reviewer math-learning (R10): extra checks on what Proposition 2 does and does not imply, from the stored labels,
references and windows (n = 57).  Own implementation (own_lib.py); no project code imported.

  A. Decomposition of the band W(x) of Prop. 2(a) by training label (cubic model).
  B. Label sensitivity |a(x)|_1 of the cubic: W(x) if EVERY training label were certified exactly at its tolerance.
  C. Local learners trained on ALL ten labels (uncertified ones included): piecewise-linear interpolation in 1/Jz and
     nearest neighbour.  Band (a) at Jz = 4, 5, 6.
  D. Learners trained on the three certified labels only (line / parabola in 1/Jz): band (a) and miss, with the map's
     own DMRG reference at Jz = 4.5 and 5.5 as an out-of-sample truth.
  E. Learner-independent floor of the (b) width: 2q >= k-th smallest calibration-label width.
  F. Label filter: energy-interval widths of the kept labels; label errors of kept and dropped labels.

  python -B extra_checks.py > extra_checks_out.txt
"""
import json
import math

import numpy as np

import own_lib as L

n = 57
eta, D = L.load_labels(n)
Wn = L.Windows(n)
Js = sorted(D)
R = [j for j in Js if j >= L.TRAIN_MIN]
od = [j for j in Js if j in L.OOD]
y = {j: L.ms(D[j]["Zl"], eta) for j in Js}
ys = {j: L.ms(D[j]["Zr"], eta) for j in Js}
tau = {j: L.TAU_REL * abs(ys[j]) for j in Js}
I = {}
for j in Js:
    if not Wn.has_row(j):
        I[j] = None
        continue
    E = Wn.thr(j)["E0"] + D[j]["eps"]
    olo, ohi = Wn.outer(j, E)
    ilo, ihi = Wn.inner(j, E)
    I[j] = dict(outer=(olo, ohi), inner=(ilo, ihi), w_out=ohi - olo, w_in=ihi - ilo)
have = [j for j in Js if I[j] is not None]


def interp_log(J, key):
    lo = max(x for x in have if x < J)
    hi = min(x for x in have if x > J)
    t = (J - lo) / (hi - lo)
    return math.exp((1 - t) * math.log(I[lo][key]) + t * math.log(I[hi][key]))


w_lo = {j: (I[j]["w_in"] if I[j] else 0.0) for j in Js}
w_hi = {j: (I[j]["w_out"] if I[j] else interp_log(j, "w_out")) for j in Js}
OUT = {}

print("=" * 100)
print("A. Band (a) of the cubic, by training label.  Lower version (inner widths; 0 at 2.2 and 3.5), units of tau(x).")
print("   Columns: share of W_lo(x) carried by the labels at 1.6-2.5 (uncertified, miss > tau/2), by 3.0-3.5, by 4.0-6.0.")
A = []
for t in R + od:
    Jtr = [j for j in R if j != t] if t in R else R
    a = L.coef_vec(Jtr, t)
    c = {j: abs(a[i]) * w_lo[j] / tau[t] for i, j in enumerate(Jtr)}
    g1 = sum(v for j, v in c.items() if j <= 2.5)
    g2 = sum(v for j, v in c.items() if 2.5 < j < 4.0)
    g3 = sum(v for j, v in c.items() if j >= 4.0)
    ch = {j: abs(a[i]) * w_hi[j] / tau[t] for i, j in enumerate(Jtr)}
    g3h = sum(v for j, v in ch.items() if j >= 4.0)
    A.append(dict(Jz=t, W_lo=g1 + g2 + g3, from_1p6_2p5=g1, from_3p0_3p5=g2, from_4_6=g3, from_4_6_upper=g3h))
    print("   Jz=%.1f  W_lo=%8.3f | 1.6-2.5: %8.3f (%5.1f %%) | 3.0-3.5: %6.3f | 4.0-6.0: %6.3f (upper %6.3f)"
          % (t, g1 + g2 + g3, g1, 100 * g1 / (g1 + g2 + g3), g2, g3, g3h))
OUT["A"] = A

print("=" * 100)
print("B. Label sensitivity of the cubic.  W_all_at_tau(x) = sum_j |a_j(x)| tau_j / tau(x): the band if every training")
print("   label were certified exactly at its own tolerance (w_j = tau_j).  > 1 means: certified labels are not enough.")
B = []
for t in R + od:
    Jtr = [j for j in R if j != t] if t in R else R
    a = L.coef_vec(Jtr, t)
    l1 = float(np.abs(a).sum())
    wat = float(sum(abs(a[i]) * tau[j] for i, j in enumerate(Jtr)) / tau[t])
    B.append(dict(Jz=t, a_l1=l1, sum_a=float(a.sum()), W_all_at_tau=wat, w_needed_over_tau=1.0 / wat))
    print("   Jz=%.1f (%s)  |a|_1 = %7.3f  sum a = %.6f  W_all_at_tau = %7.3f tau  -> labels would have to be certified at"
          " tau/%.2f" % (t, "held out" if t in R else "test", l1, a.sum(), wat, wat))
print("   in sample (cubic on all ten labels):")
for t in R:
    a = L.coef_vec(R, t)
    wat = float(sum(abs(a[i]) * tau[j] for i, j in enumerate(R)) / tau[t])
    print("   Jz=%.1f  |a|_1 = %.3f  W_all_at_tau = %.3f tau" % (t, np.abs(a).sum(), wat))
OUT["B"] = B

print("=" * 100)
print("C. Local learners trained on ALL ten emulated labels (the uncertified ones included).")


def lin_interp_coef(Jtr, x):
    """Piecewise-linear interpolation in u = 1/Jz between the two neighbouring training couplings (linear in the
    labels, non-negative weights, sum 1).  Outside the range: the nearest label."""
    u = 1.0 / np.asarray(Jtr, float)
    ux = 1.0 / x
    a = np.zeros(len(Jtr))
    order = np.argsort(u)
    us = u[order]
    if ux <= us[0]:
        a[order[0]] = 1.0
    elif ux >= us[-1]:
        a[order[-1]] = 1.0
    else:
        k = int(np.searchsorted(us, ux))
        if abs(us[k] - ux) < 1e-15:
            a[order[k]] = 1.0
        else:
            t = (ux - us[k - 1]) / (us[k] - us[k - 1])
            a[order[k - 1]], a[order[k]] = 1 - t, t
    return a


def nn_coef(Jtr, x):
    a = np.zeros(len(Jtr))
    a[int(np.argmin(np.abs(np.asarray(Jtr, float) - x)))] = 1.0
    return a


C = []
for name, cf in (("piecewise-linear in 1/Jz", lin_interp_coef), ("nearest neighbour", nn_coef)):
    print("   learner: %s" % name)
    for mode in ("held out", "in sample"):
        for t in R:
            Jtr = [j for j in R if j != t] if mode == "held out" else R
            a = cf(Jtr, t)
            used = [j for i, j in enumerate(Jtr) if abs(a[i]) > 0]
            Wl = float(sum(abs(a[i]) * w_lo[j] for i, j in enumerate(Jtr)) / tau[t])
            Wh = float(sum(abs(a[i]) * w_hi[j] for i, j in enumerate(Jtr)) / tau[t])
            f = float(a @ np.array([y[j] for j in Jtr]))
            fs = float(a @ np.array([ys[j] for j in Jtr]))
            indic = any(I[j] is None for j in used)
            C.append(dict(learner=name, mode=mode, Jz=t, used=used, W_lo=Wl, W_hi=Wh, indicative=indic,
                          f_minus_fstar=abs(f - fs) / tau[t], miss=abs(f - ys[t]) / tau[t],
                          model_err_exact_labels=abs(fs - ys[t]) / tau[t], n_train=len(Jtr)))
            if t >= 3.0:
                print("     %-9s Jz=%.1f  trained on %2d labels, uses %-12s W(x) = %.3f-%.3f tau%s -> %s | |f-f*| = %.3f tau"
                      " | miss of truth %.3f tau (same learner on exact labels: %.3f tau)"
                      % (mode, t, len(Jtr), str(used), Wl, Wh, " (interp. width)" if indic else "",
                         "PINNED within tau" if (Wh <= 1 and not indic) else "not pinned", abs(f - fs) / tau[t],
                         abs(f - ys[t]) / tau[t], abs(fs - ys[t]) / tau[t]))
OUT["C"] = C

print("=" * 100)
print("D. Learners trained on the three certified labels only (Jz = 4, 5, 6).  Truth at 4.5 and 5.5: the map's DMRG")
print("   reference m_s_GS (thr files; no emulated label exists there).")
cert = [4.0, 5.0, 6.0]
truth_extra = {j: Wn.thr(j)["m_s_GS"] for j in (4.5, 5.5)}
truth_all = dict(ys)
truth_all.update(truth_extra)
Dres = []
for name, deg in (("line in 1/Jz (least squares)", 1), ("parabola in 1/Jz (interpolation)", 2)):
    print("   learner: %s, trained on %s" % (name, cert))
    for x in [4.0, 4.5, 5.0, 5.5, 6.0] + od:
        a = L.coef_vec(cert, x, deg=deg, ridge=0.0)
        tx = L.TAU_REL * abs(truth_all[x])
        Wl = float(sum(abs(a[i]) * w_lo[j] for i, j in enumerate(cert)) / tx)
        Wh = float(sum(abs(a[i]) * w_hi[j] for i, j in enumerate(cert)) / tx)
        f = float(a @ np.array([y[j] for j in cert]))
        fs = float(a @ np.array([ys[j] for j in cert]))
        Dres.append(dict(learner=name, Jz=x, a_l1=float(np.abs(a).sum()), W_lo=Wl, W_hi=Wh, miss=abs(f - truth_all[x]) / tx,
                         f_minus_fstar=abs(f - fs) / tx, model_err_exact_labels=abs(fs - truth_all[x]) / tx))
        print("     Jz=%.1f %-22s |a|_1 = %8.3f  W(x) = %8.3f-%8.3f tau  |f-f*| = %7.3f tau  miss of truth = %7.3f tau"
              "  (exact-label learner: %.3f tau)  bound W + model error = %.3f tau"
              % (x, "(new coupling)" if x in truth_extra else ("(test range)" if x in od else "(in sample)"),
                 np.abs(a).sum(), Wl, Wh, abs(f - fs) / tx, abs(f - truth_all[x]) / tx, abs(fs - truth_all[x]) / tx,
                 Wh + abs(fs - truth_all[x]) / tx))
    # leave-one-out among the three certified labels
    for t in cert:
        tr = [j for j in cert if j != t]
        a = L.coef_vec(tr, t, deg=1, ridge=0.0)
        Wh = float(sum(abs(a[i]) * w_hi[j] for i, j in enumerate(tr)) / tau[t])
        f = float(a @ np.array([y[j] for j in tr]))
        print("     leave-one-out (line through the other two) Jz=%.1f: |a|_1 = %.3f  W = %.3f tau  miss = %.3f tau"
              % (t, np.abs(a).sum(), Wh, abs(f - ys[t]) / tau[t]))
    if deg == 2:
        break
OUT["D"] = Dres

print("=" * 100)
print("E. Learner-independent floor of the width of (b): s_j = max_{y in I_j} |f(x_j) - y| >= w_j / 2 for ANY f, so")
print("   2q >= the k-th smallest label-interval width of the calibration set (k = ceil((N+1)(1-alpha)), or N).")
Eres = []
for t in R + od:
    cal = [j for j in R if j != t] if t in R else R
    N = len(cal)
    k = min(N, int(math.ceil((1 - L.ALPHA) * (N + 1) - 1e-12)))
    ws = np.sort([w_lo[j] for j in cal])
    Eres.append(dict(Jz=t, N=N, k=k, floor_tau=float(ws[k - 1] / tau[t]),
                     n_cal_wider_than_tau=int(sum(w_lo[j] > tau[j] for j in cal))))
    print("   Jz=%.1f  N=%2d k=%2d  floor of 2q = %6.2f tau(x)   (calibration labels with inner width > own tau: %d of %d)"
          % (t, N, k, ws[k - 1] / tau[t], sum(w_lo[j] > tau[j] for j in cal), N))
print("   -> range over the training couplings %.2f-%.2f tau, over the test couplings %.2f-%.2f tau"
      % (min(e["floor_tau"] for e in Eres if e["Jz"] in R), max(e["floor_tau"] for e in Eres if e["Jz"] in R),
         min(e["floor_tau"] for e in Eres if e["Jz"] in od), max(e["floor_tau"] for e in Eres if e["Jz"] in od)))
print("   how many calibration labels may be wider than tau before rule (c) is excluded: N - k = 0 for N = 9, 10 at"
      " alpha = 0.1; for the dataset's 45 training points k = %d, so at most %d." % (
          int(math.ceil(0.9 * 46 - 1e-12)), 45 - int(math.ceil(0.9 * 46 - 1e-12))))
OUT["E"] = Eres

print("=" * 100)
print("F. Label filter at the labels' own energies (own windows).  w_out <= tau: certified.")
Fres = []
for j in Js:
    le = abs(y[j] - ys[j]) / tau[j]
    if I[j] is None:
        print("   Jz=%.1f  no map row                      label error %.3f tau" % (j, le))
        Fres.append(dict(Jz=j, row=False, label_err=le))
        continue
    wo, wi = I[j]["w_out"] / tau[j], I[j]["w_in"] / tau[j]
    st = "CERTIFIED (kept)" if wo <= 1 else ("not certified (inner > tau)" if wi > 1 else "undecided")
    # guaranteed distance of the label from the truth: the farther end of the outer interval
    g = max(abs(y[j] - I[j]["outer"][0]), abs(y[j] - I[j]["outer"][1])) / tau[j]
    print("   Jz=%.1f  w_in %.3f  w_out %.3f tau  %-28s label error %.3f tau  (guaranteed <= %.3f tau)"
          % (j, wi, wo, st, le, g))
    Fres.append(dict(Jz=j, row=True, w_in=wi, w_out=wo, status=st, label_err=le, guaranteed=g))
kept = [f for f in Fres if f.get("status", "").startswith("CERT")]
drop = [f for f in Fres if not f.get("status", "").startswith("CERT")]
print("   kept %d of %d: %s ; max label error kept %.3f tau ; max guaranteed distance kept %.3f tau"
      % (len(kept), len(Fres), [f["Jz"] for f in kept], max(f["label_err"] for f in kept),
         max(f["guaranteed"] for f in kept)))
print("   dropped with label error > tau/2: %s ; dropped with label error <= tau/2: %s ; dropped with error <= tau: %s"
      % ([f["Jz"] for f in drop if f["label_err"] > 0.5], [f["Jz"] for f in drop if f["label_err"] <= 0.5],
         [f["Jz"] for f in drop if f["label_err"] <= 1.0]))
OUT["F"] = Fres

with open("extra_checks.json", "w") as fo:
    json.dump(OUT, fo, indent=1, default=float)
