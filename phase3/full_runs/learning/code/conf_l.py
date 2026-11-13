"""Split-conformal intervals, standard and certified (laptop). Columns = labels; rows = instances.

Standard (calibrated on the labels of the generator that produced the training labels):
  SC   absolute residual |y - f|                                  -> f +- q
  NC   normalized residual |y - f| / s(x), s = ensemble std + 0.1 median_cal(std)   -> f +- q s(x)
  ENS  bootstrap-ensemble interval mean +- 1.645 std (no calibration; the usual ensemble interval)
Certified (the calibration labels enter only through their certified intervals [lo, hi], which contain the true
label by the window theory; the scores dominate the true-label scores, so the true-label coverage is >= 1 - alpha
under exchangeability of (couplings, true label)):
  CSC  max(|f - lo|, |f - hi|)                                    -> f +- q
  CNC  max(|f - lo|, |f - hi|) / s(x)                              -> f +- q s(x)
  CB   band [f_lo, f_hi] = exact image of the training intervals under the linear predictor;
       score max(0, hi - f_hi, f_lo - lo)                          -> [f_lo - q, f_hi + q]
  BAND the band [f_lo, f_hi] alone (no conformal margin; no truth guarantee): its width W(x) bounds, for every query in
       or out of distribution, the deviation |f(x) - f_exact(x)| between the prediction and that of the same model
       (same kernel and alpha) trained on the exact labels, or on ANY labels inside the training intervals
       (deterministic, no probability).
"""
import math

import numpy as np

Z90 = 1.6448536269514722


def qhat(scores, alpha):
    """Conformal quantile per column: the ceil((m+1)(1-alpha))-th smallest score (inf if that exceeds m)."""
    m = scores.shape[0]
    k = int(math.ceil((m + 1) * (1.0 - alpha) - 1e-12))
    if k > m:
        return np.full(scores.shape[1:], np.inf)
    return np.sort(scores, axis=0)[k - 1]


def band(A, lo, hi):
    """Exact image of the box prod_i [lo_i, hi_i] under y -> A y (A: (q, t); lo, hi: (t, m))."""
    Ap, Am = np.maximum(A, 0.0), np.minimum(A, 0.0)
    return Ap @ lo + Am @ hi, Ap @ hi + Am @ lo


def intervals(f_ca, f_q, y_ca, lo_ca, hi_ca, s_ca, s_q, mu_q, sd_q, flo_ca, fhi_ca, flo_q, fhi_q, alpha):
    """All methods' intervals at the query rows. Every array is (rows, m). Returns {method: (low, high)}."""
    out = {}
    q = qhat(np.abs(y_ca - f_ca), alpha)
    out["SC"] = (f_q - q, f_q + q)
    q = qhat(np.abs(y_ca - f_ca) / s_ca, alpha)
    out["NC"] = (f_q - q * s_q, f_q + q * s_q)
    out["ENS"] = (mu_q - Z90 * sd_q, mu_q + Z90 * sd_q)
    sc = np.maximum(np.abs(f_ca - lo_ca), np.abs(f_ca - hi_ca))
    q = qhat(sc, alpha)
    out["CSC"] = (f_q - q, f_q + q)
    q = qhat(sc / s_ca, alpha)
    out["CNC"] = (f_q - q * s_q, f_q + q * s_q)
    sb = np.maximum(0.0, np.maximum(hi_ca - fhi_ca, flo_ca - lo_ca))
    q = qhat(sb, alpha)
    out["CB"] = (flo_q - q, fhi_q + q)
    out["BAND"] = (flo_q, fhi_q)
    return out
