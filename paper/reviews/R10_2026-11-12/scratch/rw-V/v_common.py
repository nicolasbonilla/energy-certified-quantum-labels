"""v_common.py -- helper code of the verifier "V" (R10 rewrite, 2026-11-12).

Written from the statements in theory/*_v2.tex. Nothing is imported from the project, from the writers or from
the two referees (break-lemmas, break-theorem4).

Conventions: bit i of a basis state = 1 means spin up at site i (Z_i = +1).
Paper's bond: (1/4)(XX + YY + Jz ZZ) = (1/2)(S+S- + S-S+) + (Jz/4) ZZ.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
from itertools import combinations
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla


# ----------------------------------------------------------------------------------------------------------------
# graphs
# ----------------------------------------------------------------------------------------------------------------
def patch(d):
    """Heavy-hex patch of odd distance d, built from the formula printed in theorem4_v2.tex (Setting) and
    L2_peierls.tex: sites D(i,j), F(i,j), S(i,j) with i+j odd, caps C(i).
    Returns n, edges, names (list), eta (+1 majority = D,S ; -1 minority = F,C)."""
    assert d % 2 == 1 and d >= 3
    idx = {}
    names = []

    def add(nm):
        idx[nm] = len(names)
        names.append(nm)
    for i in range(d):
        for j in range(d):
            add(("D", i, j))
    for i in range(d):
        for j in range(d - 1):
            add(("F", i, j))
    for i in range(d - 1):
        for j in range(d - 1):
            if (i + j) % 2 == 1:
                add(("S", i, j))
    for i in range(d - 1):
        add(("C", i))
    E = []
    for i in range(d):
        for j in range(d - 1):
            E.append((idx[("F", i, j)], idx[("D", i, j)]))
            E.append((idx[("F", i, j)], idx[("D", i, j + 1)]))
    for i in range(d - 1):
        for j in range(d - 1):
            if (i + j) % 2 == 1:
                E.append((idx[("S", i, j)], idx[("F", i, j)]))
                E.append((idx[("S", i, j)], idx[("F", i + 1, j)]))
    for i in range(d - 1):
        if i % 2 == 0:
            E.append((idx[("C", i)], idx[("D", i, 0)]))
            E.append((idx[("C", i)], idx[("D", i + 1, 0)]))
        else:
            E.append((idx[("C", i)], idx[("D", i, d - 1)]))
            E.append((idx[("C", i)], idx[("D", i + 1, d - 1)]))
    eta = np.array([+1 if nm[0] in "DS" else -1 for nm in names])
    return len(names), E, names, eta


def adjacency(n, E):
    adj = [[] for _ in range(n)]
    for a, b in E:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def bfs_dist(n, E):
    adj = adjacency(n, E)
    D = np.full((n, n), -1, dtype=int)
    for s in range(n):
        D[s, s] = 0
        q = [s]
        while q:
            nq = []
            for u in q:
                for v in adj[u]:
                    if D[s, v] < 0:
                        D[s, v] = D[s, u] + 1
                        nq.append(v)
            q = nq
    return D


def pairs_dist2(n, E):
    D = bfs_dist(n, E)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if D[i, j] == 2]


# ----------------------------------------------------------------------------------------------------------------
# exact diagonalization in a fixed-magnetization sector
# ----------------------------------------------------------------------------------------------------------------
def sector_states(n, nup):
    """sorted array of the integers with nup bits set among n"""
    if nup == 0:
        return np.array([0], dtype=np.int64)
    out = np.fromiter((sum(1 << b for b in c) for c in combinations(range(n), nup)), dtype=np.int64)
    out.sort()
    return out


def zmat(states, n):
    """(dim, n) array of Z_i = +-1"""
    return (((states[:, None] >> np.arange(n)[None, :]) & 1) * 2 - 1).astype(np.float64)


def hop_matrix(states, E, amp=0.5, amps=None):
    """sum_e amp_e (S+_i S-_j + h.c.) restricted to the sector (real symmetric CSR)."""
    dim = len(states)
    rows, cols, vals = [], [], []
    for k, (i, j) in enumerate(E):
        a = amp if amps is None else amps[k]
        if a == 0:
            continue
        differ = ((states >> i) ^ (states >> j)) & 1
        src = np.nonzero(differ)[0]
        tgt = states[src] ^ ((1 << i) | (1 << j))
        pos = np.searchsorted(states, tgt)
        rows.append(pos)
        cols.append(src)
        vals.append(np.full(len(src), a))
    if not rows:
        return sp.csr_matrix((dim, dim))
    return sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(dim, dim))


def lowest(Hoff, diag, k=1, tol=1e-11, seed=7, want_vec=True):
    """lowest k eigenpairs of Hoff + diag(diag); dense for small matrices, Lanczos otherwise."""
    dim = len(diag)
    if dim <= 600:
        w, v = np.linalg.eigh(Hoff.toarray() + np.diag(diag))
        return w[:k], v[:, :k]
    H = (Hoff + sp.diags(diag)).tocsr()
    rng = np.random.default_rng(seed)
    v0 = rng.standard_normal(dim)
    kk = min(k, dim - 2)
    w, v = sla.eigsh(H, k=kk, which="SA", tol=tol, v0=v0, ncv=max(2 * kk + 2, 40), maxiter=20000)
    o = np.argsort(w)
    return w[o], v[:, o]


# ----------------------------------------------------------------------------------------------------------------
# full Hilbert space (small n) -- for dynamics and spectral-support tests
# ----------------------------------------------------------------------------------------------------------------
def full_ops(n):
    """dense single-site Z, S+, S- on the full 2^n space (bit i set = up)."""
    dim = 1 << n
    st = np.arange(dim, dtype=np.int64)
    Z = [np.diag((((st >> i) & 1) * 2 - 1).astype(float)) for i in range(n)]
    Sp = []
    for i in range(n):
        m = np.zeros((dim, dim))
        src = st[((st >> i) & 1) == 0]
        m[src | (1 << i), src] = 1.0
        Sp.append(m)
    return st, Z, Sp


def full_xxz(n, E, hop, jz, fields=None):
    """dense H = sum_e hop_e (S+S- + h.c.) + sum_e (jz_e/4) ZZ + sum_i f_i Z_i on the full space.
    hop, jz: scalars or per-edge lists."""
    dim = 1 << n
    st = np.arange(dim, dtype=np.int64)
    H = np.zeros((dim, dim))
    z = (((st[:, None] >> np.arange(n)[None, :]) & 1) * 2 - 1).astype(float)
    diag = np.zeros(dim)
    for k, (i, j) in enumerate(E):
        a = hop[k] if np.ndim(hop) else hop
        g = jz[k] if np.ndim(jz) else jz
        diag += 0.25 * g * z[:, i] * z[:, j]
        differ = (((st >> i) ^ (st >> j)) & 1) == 1
        src = st[differ]
        H[src ^ ((1 << i) | (1 << j)), src] += a
    if fields is not None:
        diag += z @ np.asarray(fields, float)
    H[np.arange(dim), np.arange(dim)] += diag
    return H, z
