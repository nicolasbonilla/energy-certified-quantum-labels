"""Tiny exact-diagonalization helpers for the cross-checks (n <= 12, sparse, seconds).

Conventions: bit 1 of a basis index = spin up = Z eigenvalue +1. Hamiltonians are scipy.sparse CSR matrices,
optionally restricted to a fixed-popcount (S^z) sector. Written separately from the rest of the deposited
code.
"""
import itertools

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.optimize import minimize_scalar


def basis(n, nup=None):
    """List of basis indices (all, or those with popcount nup)."""
    if nup is None:
        return np.arange(2 ** n)
    return np.array([x for x in range(2 ** n) if bin(x).count("1") == nup], dtype=np.int64)


def zvals(n, states):
    """Array (len(states), n) of Z eigenvalues."""
    s = np.asarray(states)[:, None]
    return np.where((s >> np.arange(n)[None, :]) & 1, 1.0, -1.0)


def xxz(n, edges, Jz, states, Jxy=0.25, Jzz=None, hx=0.0):
    """H = sum_edges Jxy (XX+YY) + Jzz ZZ  (Jzz defaults to Jz/4), restricted to `states`.
    If hx != 0 the full basis must be passed (transverse field breaks S^z)."""
    Jzz = Jz / 4.0 if Jzz is None else Jzz
    idx = {int(s): k for k, s in enumerate(states)}
    Z = zvals(n, states)
    diag = np.zeros(len(states))
    rows, cols, vals = [], [], []
    for (i, j) in edges:
        diag += Jzz * Z[:, i] * Z[:, j]
        for k, s in enumerate(states):
            s = int(s)
            if ((s >> i) & 1) != ((s >> j) & 1):
                t = s ^ (1 << i) ^ (1 << j)
                rows.append(idx[t]); cols.append(k); vals.append(2.0 * Jxy)
    if hx:
        for i in range(n):
            for k, s in enumerate(states):
                t = int(s) ^ (1 << i)
                rows.append(idx[t]); cols.append(k); vals.append(hx)
    H = sp.coo_matrix((vals, (rows, cols)), shape=(len(states), len(states))).tocsr()
    return H + sp.diags(diag)


def tfim(n, h, periodic=True, J=1.0):
    """H = -J sum Z_i Z_{i+1} - h sum X_i on the full 2^n basis."""
    st = basis(n)
    Z = zvals(n, st)
    edges = [(i, i + 1) for i in range(n - 1)] + ([(n - 1, 0)] if periodic and n > 2 else [])
    diag = np.zeros(len(st))
    for (i, j) in edges:
        diag += -J * Z[:, i] * Z[:, j]
    rows, cols, vals = [], [], []
    for i in range(n):
        rows.append(st ^ (1 << i)); cols.append(st); vals.append(np.full(len(st), -h))
    X = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(len(st), len(st))).tocsr()
    return (X + sp.diags(diag)).tocsr(), edges


def ground(H, k=2, dense_below=64):
    """Lowest k eigenpairs (sorted)."""
    if H.shape[0] <= dense_below:
        w, v = np.linalg.eigh(H.toarray())
        return w[:k], v[:, :k]
    rng = np.random.default_rng(1)
    v0 = rng.standard_normal(H.shape[0])
    w, v = sla.eigsh(H, k=k, which="SA", v0=v0, tol=1e-12, maxiter=20000)
    o = np.argsort(w)
    return w[o], v[:, o]


def e0(H):
    return ground(H, k=1)[0][0]


def upper_extent(H, Odiag_or_op, eps, E0=None, lam_max=1e3):
    """Lemma A (dual): o^+(E0+eps) = min_{lam>0} [E0 + eps - E0(H - lam O)]/lam.
    O may be a 1-D array (diagonal) or a sparse matrix. Returns (value, lam*)."""
    O = sp.diags(Odiag_or_op) if np.ndim(Odiag_or_op) == 1 else Odiag_or_op
    E0 = e0(H) if E0 is None else E0
    f = lambda t: (E0 + eps - e0(H - np.exp(t) * O)) / np.exp(t)
    r = minimize_scalar(f, bounds=(np.log(1e-7), np.log(lam_max)), method="bounded",
                        options=dict(xatol=1e-10, maxiter=500))
    # also compare with the saturation value lam -> infinity (largest eigenvalue of O restricted)
    return r.fun, float(np.exp(r.x))


def two_sided(H, Od, eps, E0=None):
    """Return (o_minus, o_plus) of the information limit at E0+eps, clipped to the spectral range of O
    (the dual with a bounded multiplier overshoots by O(1/lam_max) once the label saturates)."""
    up, _ = upper_extent(H, Od, eps, E0)
    dn, _ = upper_extent(H, -np.asarray(Od) if np.ndim(Od) == 1 else -Od, eps, E0)
    if np.ndim(Od) == 1:
        up, dn = min(up, float(np.max(Od))), min(dn, float(-np.min(Od)))
    return -dn, up


def comb(nb):
    """Comb graph: backbone chain of nb sites (0..nb-1), one pendant on every odd backbone site.
    Bipartite with unequal sublattices. Returns (n, edges, colour) with colour 0 = majority."""
    edges = [(i, i + 1) for i in range(nb - 1)]
    n = nb
    for i in range(1, nb, 2):
        edges.append((i, n)); n += 1
    col = np.zeros(n, int)
    for i in range(nb):
        col[i] = i % 2
    for k, (a, b) in enumerate(edges[nb - 1:]):
        col[b] = 1 - col[a]
    # make colour 0 the majority
    if (col == 0).sum() < (col == 1).sum():
        col = 1 - col
    return n, edges, col
