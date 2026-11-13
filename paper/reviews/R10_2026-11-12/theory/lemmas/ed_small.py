"""ed_small.py -- minimal exact diagonalization of XXZ models in a fixed-S^z sector (used by the attack scripts).

H = (1/4) sum_edges (XX + YY + Jz ZZ) + sum_i f_i Z_i.  Basis: bit i of a state = 1 means spin up at site i.
Written for this review; nothing is imported from the project code.
"""
from itertools import combinations
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla


def basis(n, nup):
    return np.array(sorted(sum(1 << i for i in c) for c in combinations(range(n), nup)), dtype=np.int64)


def zvals(states, n):
    return np.array([(((states >> i) & 1) * 2 - 1) for i in range(n)], dtype=np.float64)   # (n, dim)


def build(states, n, edges, Jz, fields=None):
    """returns (K, diag): K = (1/4) sum (XX + YY) as a sparse matrix, diag = diagonal of the rest"""
    dim = len(states)
    z = zvals(states, n)
    diag = np.zeros(dim)
    rows, cols = [], []
    for (i, j) in edges:
        diag += 0.25 * Jz * z[i] * z[j]
        src = np.nonzero(((states >> i) & 1) != ((states >> j) & 1))[0]
        tgt = np.searchsorted(states, states[src] ^ ((1 << i) | (1 << j)))
        rows.append(tgt); cols.append(src)
    if fields is not None:
        diag += np.asarray(fields, dtype=float) @ z
    rows = np.concatenate(rows); cols = np.concatenate(cols)
    K = sp.csr_matrix((0.5 * np.ones(len(rows)), (rows, cols)), shape=(dim, dim))
    return K, diag


def lowest(K, diag, k=1, v0=None):
    """k lowest eigenvalues and the ground vector of K + diag (dense below 2500 states, Lanczos above)"""
    dim = len(diag)
    if dim <= 2500:
        w, v = np.linalg.eigh(K.toarray() + np.diag(diag))
        return w[:k], v[:, 0]
    H = (K + sp.diags(diag)).tocsr()
    w, v = sla.eigsh(H, k=max(k, 2), which="SA", tol=1e-12, v0=v0, ncv=min(dim - 1, 48), maxiter=20000)
    o = np.argsort(w)
    return w[o][:k], v[:, o[0]]


def conj_cost(K, diag, odiag, n, target, sign, psi0, E0, mu_hi0=0.05, xtol=1e-13):
    """Exact cost of moving the average O/n to `target` (sign=+1: <O>/n >= target above the ground value;
    sign=-1: <O>/n <= target below it), by the conjugate function:
        E* = sup_{mu >= 0} [ E0(H - sign mu O) - E0 + sign mu n target ].
    Returns (dual lower bound, primal upper bound, mu*). Every evaluated mu gives a valid dual value; every evaluated
    mu whose ground state reaches the target gives a valid primal value (an explicit state)."""
    from scipy.optimize import brentq
    duals, primals = [0.0], []
    cache = {"v": psi0}

    def f(mu):
        w, v = lowest(K, diag - sign * mu * odiag, 1, v0=cache["v"])
        cache["v"] = v
        o = float(np.sum(v * v * odiag)) / n
        e = float(v @ (K @ v) + np.sum(v * v * diag)) - E0
        duals.append(w[0] - E0 + sign * mu * n * target)
        if sign * (o - target) >= 0:
            primals.append(e)
        return sign * (o - target)

    hi = mu_hi0
    for _ in range(60):
        if f(hi) >= 0:
            break
        hi *= 2.0
    else:
        return max(duals), float("inf"), float("nan")
    lo = 0.0
    if f(lo) >= 0:
        return max(duals), min(primals), 0.0
    mu = brentq(f, lo, hi, xtol=xtol, rtol=1e-14, maxiter=200)
    f(mu * (1 + 1e-9) + 1e-12)          # one more point on the feasible side
    return max(duals), min(primals), mu


def ring(n):
    return [(i, (i + 1) % n) for i in range(n)], [(-1) ** i for i in range(n)]


def chain(n):
    return [(i, i + 1) for i in range(n - 1)], [(-1) ** i for i in range(n)]


def ladder(L, periodic):
    """2 x L ladder; site (x, y) -> 2x + y"""
    E = [(2 * x, 2 * x + 1) for x in range(L)]
    for x in range(L if periodic else L - 1):
        for y in (0, 1):
            E.append((2 * x + y, 2 * ((x + 1) % L) + y))
    return E, [(-1) ** (x + y) for x in range(L) for y in (0, 1)]


def torus(Lx, Ly, periodic=True):
    """Lx x Ly square lattice; site (x, y) -> x * Ly + y"""
    E = set()
    for x in range(Lx):
        for y in range(Ly):
            for (dx, dy) in ((1, 0), (0, 1)):
                X, Y = x + dx, y + dy
                if periodic:
                    X %= Lx; Y %= Ly
                elif X >= Lx or Y >= Ly:
                    continue
                a, b = x * Ly + y, X * Ly + Y
                if a != b:
                    E.add((min(a, b), max(a, b)))
    return sorted(E), [(-1) ** (x + y) for x in range(Lx) for y in range(Ly)]
