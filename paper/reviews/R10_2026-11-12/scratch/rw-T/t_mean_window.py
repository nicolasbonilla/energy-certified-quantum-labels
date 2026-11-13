"""t_mean_window.py  --  R10 rewrite, writer T (theory), 2026-11-13.  Own code; nothing imported from the paper.

What a fixed MEAN magnetization constrains.  12-site comb ferrimagnet of paper/data/crosschecks/check4 (backbone
chain of 8 sites, one pendant on every odd backbone site; 8 majority, 4 minority sites, 11 edges),
H = 1/4 sum_<ij> (X X + Y Y + Jz Z Z), M_z = sum_i Z_i, Neel sector M_z = M_0 = 4.

For the labels m_s = (1/n) sum_i eta_i Z_i and C_zz = mean over the edges of Z_i Z_j, at energy E = E_0 + n*de:
  (S) sector window     { Tr H s <= E, s in the sector M_z = M_0 }
  (M) mean window       { Tr H s <= E, Tr M_z s = M }          (no sector projector), M = M_0 and M = M_0 - 2 q
  (F) free window       { Tr H s <= E }
Every operator here commutes with M_z, so the lowest eigenvalue of H - lam*O + mu*M_z on the whole space is
min_q [ e_q(lam) + mu*q ], e_q the lowest eigenvalue of H - lam*O in the sector M_z = q, and
  outer (dual) value   sup O = inf_{lam>0} [ E - env_lam(M) ] / lam ,
      env_lam(M) = lower convex envelope of the points (q, e_q(lam)) at M   (= the minimum over mu, done exactly);
  inner (primal) value  an explicit mixture of sector ground states of H -+ lam*O (linear programme over the
      stored points (q, energy, label)); inner <= exact <= outer.
Also: the interval (B_-, B_+) of uniform fields for which the sector ground state is the ground state of
H - B*M_z on the whole space, and the bound  sum_q p_q |q - M_0| <= 2 eps / (B_+ - B_-)  on any state of the mean
window at M = M_0 (p_q = weight of the sector q), in particular  p_{-M_0} <= eps / (2 M_0 (B_+ - B_-)).

Run:  python -B t_mean_window.py > t_mean_window_out.txt      (about a minute, 2 threads)
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
import itertools
import sys
import time

import numpy as np
from scipy.linalg import eigh
from scipy.optimize import linprog, minimize_scalar

T0 = time.time()


def comb(nb=8):
    edges = [(i, i + 1) for i in range(nb - 1)]
    n = nb
    for i in range(1, nb, 2):
        edges.append((i, n))
        n += 1
    col = np.zeros(n, int)
    for i in range(nb):
        col[i] = i % 2
    for (a, b) in edges[nb - 1:]:
        col[b] = 1 - col[a]
    if (col == 0).sum() < (col == 1).sum():
        col = 1 - col
    return n, edges, col


n, edges, col = comb(8)
eta = np.where(col == 0, 1.0, -1.0)
NMAJ = int((col == 0).sum())
M0 = 2 * NMAJ - n
print("comb: n = %d, majority %d, minority %d, edges %d, Neel sector n_up = %d, M_0 = %d" % (
    n, NMAJ, n - NMAJ, len(edges), NMAJ, M0))

# ---- sector blocks -------------------------------------------------------------------------------------------------
SECT = {}
for nup in range(n + 1):
    states = [sum(1 << i for i in c) for c in itertools.combinations(range(n), nup)]
    idx = {s: k for k, s in enumerate(states)}
    st = np.array(states, dtype=np.int64)
    Z = np.where((st[:, None] >> np.arange(n)[None, :]) & 1, 1.0, -1.0)
    hop = np.zeros((len(states), len(states)))
    for (i, j) in edges:
        for k, s in enumerate(states):
            if ((s >> i) & 1) != ((s >> j) & 1):
                hop[idx[s ^ (1 << i) ^ (1 << j)], k] += 0.5          # 1/4 (XX + YY)
    zz = sum(Z[:, i] * Z[:, j] for (i, j) in edges)                   # sum over edges of Z_i Z_j
    SECT[2 * nup - n] = dict(hop=hop, zz=zz, ms=Z @ eta / n, czz=zz / len(edges), dim=len(states))
QS = sorted(SECT)
print("sectors M_z =", QS, " dimensions", [SECT[q]["dim"] for q in QS])


def lowest(q, Jz, lam, lab, vec=False):
    """lowest eigenpair of H - lam*O in the sector q (O = SECT[q][lab], diagonal)."""
    s = SECT[q]
    A = s["hop"] + np.diag(0.25 * Jz * s["zz"] - lam * s[lab])
    if s["dim"] == 1:
        return (A[0, 0], np.ones(1)) if vec else A[0, 0]
    if vec:
        w, v = eigh(A, subset_by_index=[0, 0])
        return w[0], v[:, 0]
    return eigh(A, eigvals_only=True, subset_by_index=[0, 0])[0]


def envelope(pts, M):
    """lower convex envelope of the points (q, e) at M (exact: best single point or pair)."""
    best = np.inf
    for q, e in pts:
        if q == M:
            best = min(best, e)
    for (q1, e1), (q2, e2) in itertools.combinations(pts, 2):
        if q1 < M < q2:
            best = min(best, e1 + (e2 - e1) * (M - q1) / (q2 - q1))
    return best


def dual_end(Jz, lab, sign, E, mode, M=None):
    """outer value of sup (sign*O) over the window; mode 'S' sector, 'M' mean, 'F' free."""
    cache = {}

    def f(t):
        lam = float(np.exp(t))
        if mode == "S":
            low = lowest(M0, Jz, sign * lam, lab)
        else:
            pts = [(q, lowest(q, Jz, sign * lam, lab)) for q in QS]
            low = min(e for _, e in pts) if mode == "F" else envelope(pts, M)
        cache[t] = (E - low) / lam
        return cache[t]
    grid = np.linspace(np.log(1e-4), np.log(3e2), 41)
    vals = [f(t) for t in grid]
    k = int(np.argmin(vals))
    lo, hi = grid[max(k - 1, 0)], grid[min(k + 1, len(grid) - 1)]
    r = minimize_scalar(f, bounds=(lo, hi), method="bounded", options=dict(xatol=1e-9, maxiter=200))
    val = min(r.fun, min(vals))
    top = max(float(np.max(sign * SECT[q][lab])) for q in (QS if mode != "S" else [M0]))
    return min(val, top), float(np.exp(r.x))


def primal_points(Jz, lab):
    """explicit states: sector ground states of H -+ lam*O on a grid; rows (q, energy under H, label)."""
    rows = []
    lams = np.concatenate([[0.0], np.exp(np.linspace(np.log(1e-4), np.log(3e2), 90))])
    for q in QS:
        s = SECT[q]
        for sg in (+1, -1):
            for lam in lams:
                w, v = lowest(q, Jz, sg * lam, lab, vec=True)
                o = float(v ** 2 @ s[lab])
                rows.append((q, w + sg * lam * o, o))
    return np.array(rows)


def primal_end(rows, sign, E, mode, M=None):
    """inner value: best explicit mixture (linear programme)."""
    if mode == "S":
        rows = rows[rows[:, 0] == M0]
    c = -sign * rows[:, 2]
    A_ub, b_ub = [rows[:, 1]], [E]
    A_eq, b_eq = [np.ones(len(rows))], [1.0]
    if mode == "M":
        A_eq.append(rows[:, 0])
        b_eq.append(M)
    r = linprog(c, A_ub=np.array(A_ub), b_ub=b_ub, A_eq=np.array(A_eq), b_eq=b_eq, bounds=(0, None), method="highs")
    if r.status != 0:
        return np.nan, None, rows
    return -r.fun, r.x, rows


for Jz in (1.6, 4.0):
    e0q = {q: lowest(q, Jz, 0.0, "ms") for q in QS}
    E0 = e0q[M0]
    Bp = min((e0q[q] - E0) / (q - M0) for q in QS if q > M0)
    Bm = max((E0 - e0q[q]) / (M0 - q) for q in QS if q < M0)
    w0, v0 = lowest(M0, Jz, 0.0, "ms", vec=True)
    ms_gs = float(v0 ** 2 @ SECT[M0]["ms"])
    czz_gs = float(v0 ** 2 @ SECT[M0]["czz"])
    print("\n=== Jz = %.1f ===" % Jz)
    print("sector ground energies E_0^(q) - E_0^(M_0):", "  ".join("%+d: %.5f" % (q, e0q[q] - E0) for q in QS))
    print("global ground energy minus E_0^(M_0): %.3e (the Neel sector and its mirror image are the lowest)" % (
        min(e0q.values()) - E0))
    print("interval of uniform fields (per unit of M_z): B_- = %.6f, B_+ = %.6f  [B_+/Jz = %.6f]" % (Bm, Bp, Bp / Jz))
    print("ground state of the Neel sector: m_s = %.6f, C_zz = %.6f" % (ms_gs, czz_gs))
    rows_ms, rows_czz = primal_points(Jz, "ms"), primal_points(Jz, "czz")
    for de in (1e-3, 1e-2):
        eps = n * de
        E = E0 + eps
        print("  de = %.0e  (eps = %.4f)" % (de, eps))
        print("     bounds for the mean window at M = M_0:  sum_q p_q |q - M_0| <= 2 eps/(B_+ - B_-) = %.5f ;"
              "  weight of the mirror sector p_(-M_0) <= eps/(2 M_0 (B_+ - B_-)) = %.5f" % (
                  2 * eps / (Bp - Bm), eps / (2 * M0 * (Bp - Bm))))
        for lab, rows, name in (("ms", rows_ms, "m_s "), ("czz", rows_czz, "C_zz")):
            res = {}
            for mode, M in (("S", None), ("M", float(M0)), ("M", float(M0) - 0.2), ("F", None)):
                up_out, _ = dual_end(Jz, lab, +1, E, mode, M)
                dn_out, _ = dual_end(Jz, lab, -1, E, mode, M)
                up_in, xu, rr = primal_end(rows, +1, E, mode, M)
                dn_in, xd, rr = primal_end(rows, -1, E, mode, M)
                key = mode if M is None or M == M0 else "M'"
                res[key] = (-dn_out, up_out, -dn_in, up_in, xu, xd, rr)
            names = {"S": "sector M_z = M_0            ", "M": "mean  Tr M_z s = M_0       ",
                     "M'": "mean  Tr M_z s = M_0 - 0.2 ", "F": "no constraint on M_z       "}
            for key in ("S", "M", "M'", "F"):
                lo_o, hi_o, lo_i, hi_i, xu, xd, rr = res[key]
                print("     %s %s outer [%+.4f, %+.4f] width %.4f | inner [%+.4f, %+.4f] width %.4f" % (
                    name, names[key], lo_o, hi_o, hi_o - lo_o, lo_i, hi_i, hi_i - lo_i))
                if key in ("M", "M'") and xd is not None:
                    wq = {}
                    for x, (q, e, o) in zip(xd, rr):
                        if x > 1e-9:
                            wq[int(q)] = wq.get(int(q), 0.0) + x
                    print("          lower-end mixture, weights by sector: %s ; weight outside the Neel sector %.5f"
                          % ("  ".join("%+d: %.5f" % (q, wq[q]) for q in sorted(wq)), 1 - wq.get(M0, 0.0)))
            if lab == "ms":
                s_lo, s_hi = res["S"][0], res["S"][1]
                m_lo, m_hi = res["M"][0], res["M"][1]
                print("     m_s: the mean window at M_0 exceeds the sector window by %.4f below and %.4f above (outer "
                      "values); the free window is [%+.4f, %+.4f]" % (s_lo - m_lo, m_hi - s_hi, res["F"][0], res["F"][1]))
        sys.stdout.flush()
print("\nelapsed %.0f s" % (time.time() - T0))
