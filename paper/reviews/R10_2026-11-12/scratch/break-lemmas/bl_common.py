"""bl_common.py -- own helper code of the referee "break-lemmas" (R10, 2026-11-12).

Nothing is imported from the project or from the writer's scripts (theory/lemmas/ed_small.py is NOT used).
Contents: heavy-hex generator (my own port of the Rust source of rustworkx-core 0.14.2), two-colouring,
exact diagonalization of spin-1/2 models with S^z conservation in a fixed sector (general complex hopping per
oriented bond, per-bond ZZ, on-site Z fields), swap operators, conjugate-function cost E*_n(c).

Convention: bit i of a basis state = 1 means spin up at site i (Z_i = +1).
H = sum_e [ a_e s+_i s-_j + conj(a_e) s-_i s+_j ] + sum_e (Jz_e/4) Z_i Z_j + sum_i f_i Z_i ,  e = (i, j).
The paper's bond  (1/4)(XX + YY + Jz ZZ)  is a_e = 1/2, Jz_e = Jz.
"""
from itertools import combinations
from collections import deque
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla


# ---------------------------------------------------------------------------------------------------------------
# graphs
# ---------------------------------------------------------------------------------------------------------------
def heavy_hex(d):
    """Port of rustworkx_core::generators::heavy_hex_graph (0.14.2), read from the Rust source.
    Returns n, edges (generator order), and a dict of the node classes."""
    assert d % 2 == 1 and d >= 3
    nd, ns, nf = d * d, (d - 1) * (d + 1) // 2, d * (d - 1)
    data = list(range(nd))
    syn = list(range(nd, nd + ns))
    flag = list(range(nd + ns, nd + ns + nf))
    E = []
    for i in range(d):                                   # connect data and flags
        for j in range(d - 1):
            f = flag[i * (d - 1) + j]
            E.append((data[i * d + j], f))
            E.append((data[i * d + j + 1], f))
    h = (d + 1) // 2
    chunks = [syn[k * h:(k + 1) * h] for k in range(d - 1)]
    for i, ch in enumerate(chunks):                      # connect data and syndromes
        if i % 2 == 0:
            E.append((data[i * d], ch[0]))
            E.append((data[(i + 1) * d], ch[0]))
        else:
            E.append((data[i * d + (d - 1)], ch[-1]))
            E.append((data[i * d + (2 * d - 1)], ch[-1]))
    for i, ch in enumerate(chunks):                      # connect flags and syndromes
        if i % 2 == 0:
            for j, s in enumerate(ch):
                if j != 0:
                    E.append((s, flag[i * (d - 1) + 2 * (j - 1) + 1]))
                    E.append((s, flag[(i + 1) * (d - 1) + 2 * (j - 1) + 1]))
        else:
            for j, s in enumerate(ch):
                if j != len(ch) - 1:
                    E.append((s, flag[i * (d - 1) + 2 * j]))
                    E.append((s, flag[(i + 1) * (d - 1) + 2 * j]))
    return nd + ns + nf, E, dict(data=data, syn=syn, flag=flag, chunks=chunks)


def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def two_colour(n, edges):
    """Returns eta (+1 on the larger colour class, -1 on the other); raises if not bipartite/connected."""
    adj = adjacency(n, edges)
    col = [-1] * n
    col[0] = 0
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if col[v] < 0:
                col[v] = 1 - col[u]
                q.append(v)
            elif col[v] == col[u]:
                raise ValueError("not bipartite")
    if min(col) < 0:
        raise ValueError("not connected")
    n1 = sum(col)
    maj = 1 if n1 > n - n1 else 0
    return [1 if c == maj else -1 for c in col]


# ---------------------------------------------------------------------------------------------------------------
# exact diagonalization in a fixed-S^z sector
# ---------------------------------------------------------------------------------------------------------------
def sector(n, nup):
    s = np.fromiter((sum(1 << i for i in c) for c in combinations(range(n), nup)), dtype=np.int64)
    s.sort()
    return s


def zvals(states, n):
    return np.array([(((states >> i) & 1) * 2 - 1) for i in range(n)], dtype=np.float64)      # (n, dim)


def build(states, n, edges, hop=0.5, jz=1.0, fields=None):
    """Sparse H in the sector.  hop, jz: scalars or per-edge sequences (hop may be complex).
    Returns (Hoff, diag): Hoff = hopping part (csr), diag = diagonal part (ZZ and fields)."""
    dim = len(states)
    z = zvals(states, n)
    hop = np.broadcast_to(np.asarray(hop, dtype=complex), (len(edges),))
    jz = np.broadcast_to(np.asarray(jz, dtype=float), (len(edges),))
    diag = np.zeros(dim)
    rows, cols, vals = [], [], []
    for k, (i, j) in enumerate(edges):
        diag += 0.25 * jz[k] * z[i] * z[j]
        if hop[k] != 0:
            bi = (states >> i) & 1
            bj = (states >> j) & 1
            src = np.nonzero((bi == 0) & (bj == 1))[0]            # s+_i s-_j acts on (i down, j up)
            tgt = np.searchsorted(states, states[src] ^ ((1 << i) | (1 << j)))
            rows.append(tgt); cols.append(src); vals.append(np.full(len(src), hop[k]))
            rows.append(src); cols.append(tgt); vals.append(np.full(len(src), np.conj(hop[k])))
    if fields is not None:
        diag += np.asarray(fields, dtype=float) @ z
    if rows:
        rows = np.concatenate(rows); cols = np.concatenate(cols); vals = np.concatenate(vals)
        if np.all(vals.imag == 0):
            vals = vals.real
        Hoff = sp.csr_matrix((vals, (rows, cols)), shape=(dim, dim))
    else:
        Hoff = sp.csr_matrix((dim, dim))
    return Hoff, diag


def swap_op(states, i, j):
    """Permutation operator P_ij (exchange of the spins at i and j) in the sector, as csr."""
    bi = (states >> i) & 1
    bj = (states >> j) & 1
    new = np.where(bi != bj, states ^ ((1 << i) | (1 << j)), states)
    tgt = np.searchsorted(states, new)
    dim = len(states)
    return sp.csr_matrix((np.ones(dim), (tgt, np.arange(dim))), shape=(dim, dim))


def perm_op(states, n, perm):
    """Unitary of a site permutation: the spin at site i moves to site perm[i]. Returns target indices t with
    (U psi)[t[k]] = psi[k]."""
    new = np.zeros_like(states)
    for i in range(n):
        new |= ((states >> i) & 1) << perm[i]
    return np.searchsorted(states, new)


def lowest(Hoff, diag, k=2, v0=None, dense_below=3000, tol=1e-11):
    """k lowest eigenvalues (ascending) and the ground vector."""
    dim = len(diag)
    if dim <= dense_below:
        w, v = np.linalg.eigh(Hoff.toarray() + np.diag(diag))
        return w[:k], v[:, 0]
    H = (Hoff + sp.diags(diag)).tocsr()
    kk = min(max(k, 2), dim - 2)
    w, v = sla.eigsh(H, k=kk, which="SA", tol=tol, v0=v0, ncv=min(dim - 1, max(40, 4 * kk)), maxiter=40000)
    o = np.argsort(w)
    return w[o][:k], v[:, o[0]]


def expect(Hoff, diag, v):
    return float(np.real(np.vdot(v, Hoff @ v) + np.sum(np.abs(v) ** 2 * diag)))


def conj_cost(Hfun, E0, n, target, sign, mu_hi=0.05, iters=70):
    """E*(c) through the conjugate function, for a label O/n with ground value o_GS and target = o_GS + sign*c.
       Hfun(mu) must return (E0(H - sign*mu*O), <O>/n in that ground state, <H> in that ground state).
       dual(mu) = E0(H - sign mu O) - E0 + sign mu n target  is a LOWER bound on E* for every mu >= 0;
       every evaluated ground state that reaches the target gives an UPPER bound <H> - E0.
       Returns (best dual, best primal, mu*)."""
    duals, primals = [0.0], []

    def f(mu):
        e, o, h = Hfun(mu)
        duals.append(e - E0 + sign * mu * n * target)
        if sign * (o - target) >= -1e-13:
            primals.append(h - E0)
        return sign * (o - target)

    lo, hi = 0.0, mu_hi
    if f(0.0) >= 0:
        return max(duals), 0.0, 0.0
    for _ in range(80):
        if f(hi) >= 0:
            break
        hi *= 2.0
    else:
        return max(duals), float("inf"), float("nan")
    for _ in range(iters):                       # bisection on the sign of (o - target)
        mid = 0.5 * (lo + hi)
        if f(mid) >= 0:
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-13 * max(1.0, hi):
            break
    return max(duals), min(primals), hi
