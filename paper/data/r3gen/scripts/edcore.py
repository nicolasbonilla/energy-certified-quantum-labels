"""Tiny exact-diagonalization core for the R3 generality checks (n <= 12).

Conventions: bit i of the basis integer = 1 means spin up, Z_i = +1.
Sector: fixed number of up spins (U(1)), or full space (sector=None).
All energies in model units.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from itertools import combinations


def chain_edges(n, periodic=True):
    e = [(i, i + 1) for i in range(n - 1)]
    if periodic and n > 2:
        e.append((n - 1, 0))
    return e


def rect_edges(Lx, Ly, periodic=True):
    idx = lambda x, y: x * Ly + y
    e = set()
    for x in range(Lx):
        for y in range(Ly):
            for dx, dy in ((1, 0), (0, 1)):
                X, Y = x + dx, y + dy
                if X >= Lx:
                    if not periodic or Lx <= 2:
                        continue
                    X %= Lx
                if Y >= Ly:
                    if not periodic or Ly <= 2:
                        continue
                    Y %= Ly
                a, b = idx(x, y), idx(X, Y)
                if a != b:
                    e.add(tuple(sorted((a, b))))
    return sorted(e)


class Basis:
    def __init__(self, n, nup=None):
        self.n = n
        if nup is None:
            self.states = np.arange(2 ** n, dtype=np.int64)
        else:
            st = []
            for c in combinations(range(n), nup):
                s = 0
                for i in c:
                    s |= 1 << i
                st.append(s)
            self.states = np.array(sorted(st), dtype=np.int64)
        self.dim = len(self.states)
        self.index = {int(s): k for k, s in enumerate(self.states)}
        self.full = nup is None
        # z values: (dim, n) array of +-1
        self.z = ((self.states[:, None] >> np.arange(n)[None, :]) & 1) * 2 - 1

    def lookup(self, s):
        if self.full:
            return s
        return np.array([self.index.get(int(x), -1) for x in s])

    def embed(self, v):
        """Return the full-space (2^n) vector of a sector vector."""
        w = np.zeros(2 ** self.n, dtype=complex)
        w[self.states] = v
        return w


def diag_op(basis, coeffs_sites):
    """sum_k c_k prod_{i in sites_k} Z_i as a diagonal sparse matrix."""
    d = np.zeros(basis.dim)
    for c, sites in coeffs_sites:
        t = np.ones(basis.dim)
        for i in sites:
            t = t * basis.z[:, i]
        d += c * t
    return sp.diags(d)


def x_op(basis, coeffs):
    """sum_i c_i X_i (full basis only)."""
    assert basis.full
    rows, cols, vals = [], [], []
    for i, c in coeffs:
        if c == 0:
            continue
        rows.append(basis.states)
        cols.append(basis.states ^ (1 << i))
        vals.append(np.full(basis.dim, c, dtype=float))
    if not rows:
        return sp.csr_matrix((basis.dim, basis.dim))
    return sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                         shape=(basis.dim, basis.dim))


def flipflop_op(basis, edges, amp):
    """amp * sum_edges (s+_i s-_j + h.c.), i.e. amp/2 (XX+YY)."""
    rows, cols, vals = [], [], []
    for (i, j) in edges:
        bi = (basis.states >> i) & 1
        bj = (basis.states >> j) & 1
        m = bi != bj
        src = basis.states[m]
        dst = src ^ ((1 << i) | (1 << j))
        di = basis.lookup(dst)
        rows.append(np.arange(basis.dim)[m])
        cols.append(di)
        vals.append(np.full(m.sum(), amp))
    r = np.concatenate(rows); c = np.concatenate(cols); v = np.concatenate(vals)
    return sp.csr_matrix((v, (r, c)), shape=(basis.dim, basis.dim))


def tfim(n, edges, J=1.0, h=1.0, g=0.0):
    b = Basis(n)
    H = diag_op(b, [(-J, e) for e in edges] + [(-g, (i,)) for i in range(n)] if g else [(-J, e) for e in edges])
    H = H + x_op(b, [(i, -h) for i in range(n)])
    return b, sp.csr_matrix(H)


def xxz(n, edges, Jz, nup):
    """IBM convention H = 1/4 sum_edges (XX + YY + Jz ZZ) in the sector with nup up spins."""
    b = Basis(n, nup)
    H = flipflop_op(b, edges, 0.5) + diag_op(b, [(Jz / 4.0, e) for e in edges])
    return b, sp.csr_matrix(H)


_RNG = np.random.default_rng(12345)
_RV = {}


def ground(Hm, v0=None, dense_max=300):
    d = Hm.shape[0]
    if v0 is not None:
        # break any symmetry of the warm start so Lanczos can reach every symmetry sector
        if d not in _RV:
            _RV[d] = _RNG.standard_normal(d)
        v0 = np.real(v0) + 1e-2 * _RV[d] / np.sqrt(d)
    if d <= dense_max:
        w, V = np.linalg.eigh(Hm.toarray())
        return w[0], V[:, 0], w
    w, V = sla.eigsh(Hm, k=1, which='SA', v0=v0, tol=1e-12, maxiter=20000)
    return w[0], V[:, 0], None


def expval(M, v):
    return float(np.real(np.vdot(v, M @ v)))


class Window:
    """Exact energy-window limits for one observable O via Lemma 0 (Lagrange duality).

    For lam > 0: psi_lam = GS of H - lam O.  E(lam) = <H>, o(lam) = <O>, F(lam) = E - lam o.
    u(eps) = max_{W(E0+eps)} <O> - o0 is attained at the lam* with E(lam*) = E0 + eps (pure GS),
    or by a two-state mixture across a level crossing.  dual(eps, lam) = (E0 + eps - F(lam))/lam.
    """

    def __init__(self, H, O, sign=+1):
        self.H = H
        self.O = O * sign
        self.sign = sign
        self.E0, self.psi0, self.spec = ground(H)
        self.o0 = expval(self.O, self.psi0)
        self.cache = {}

    def at(self, lam):
        if lam == 0:
            return self.E0, self.o0, self.psi0
        key = round(lam, 15)
        if key in self.cache:
            return self.cache[key]
        if self.cache:
            kn = min(self.cache.keys(), key=lambda k: abs(np.log(k) - np.log(lam)))
            v0 = self.cache[kn][2]
        else:
            v0 = self.psi0
        e, v, _ = ground(self.H - lam * self.O, v0=v0)
        E = expval(self.H, v); o = expval(self.O, v)
        self.cache[key] = (E, o, v)
        return E, o, v

    def F(self, lam):
        E, o, _ = self.at(lam)
        return E - lam * o

    def u(self, eps, lam_hi=64.0, xtol=1e-9):
        """Exact one-sided window extent u(eps) = max<O> - o0 (signed frame).

        Root of E(lam) = E0 + eps by Brent in log(lam); across a level crossing the
        two-state mixture of the bracketing ground states is used.  Returns (u, lam*, flag)."""
        from scipy.optimize import brentq
        target = self.E0 + eps
        Ehi, ohi, _ = self.at(lam_hi)
        while Ehi <= target and lam_hi < 1e7:
            lam_hi *= 32.0
            Ehi, ohi, _ = self.at(lam_hi)
        if Ehi <= target:
            return ohi - self.o0, lam_hi, 'saturated'
        # bracket from below in log space
        s_hi = np.log(lam_hi)
        s_lo = s_hi
        while True:
            s_lo -= np.log(8.0)
            E, o, _ = self.at(np.exp(s_lo))
            if E <= target or s_lo < np.log(1e-9):
                break
        g = lambda s: self.at(np.exp(s))[0] - target
        s_star = brentq(g, s_lo, s_hi, xtol=xtol, rtol=4 * np.finfo(float).eps, maxiter=200)
        lam_a, lam_b = np.exp(s_star - 2 * xtol), np.exp(s_star + 2 * xtol)
        Ea, oa, _ = self.at(lam_a); Eb, ob, _ = self.at(lam_b)
        if Ea > target:   # numerical safety: step down until feasible
            lam_a = np.exp(s_star - 1e-6); Ea, oa, _ = self.at(lam_a)
        if Eb - Ea < 1e-15:
            val = oa
        else:
            t = min(1.0, max(0.0, (target - Ea) / (Eb - Ea)))
            val = (1 - t) * oa + t * ob
        self.last = dict(lam_a=lam_a, lam_b=lam_b, Ea=Ea, Eb=Eb, oa=oa, ob=ob)
        return val - self.o0, np.exp(s_star), 'interior'

    def dual_at(self, eps, lam):
        return (self.E0 + eps - self.F(lam)) / lam - self.o0

    def dual(self, eps, lams):
        return min((self.E0 + eps - self.F(l)) / l for l in lams) - self.o0

    def alpha(self, lam):
        """alpha(lam) = E0 - lam o0 - E0(H - lam O) >= 0 (response function)."""
        return self.E0 - lam * self.o0 - self.F(lam)


def rdm(psi_full, n, sites):
    """Reduced density matrix of a full-space state on `sites` (ordered list)."""
    t = psi_full.reshape([2] * n)  # axis k <-> bit (n-1-k)
    axes = [n - 1 - s for s in sites]
    rest = [a for a in range(n) if a not in axes]
    t = np.transpose(t, axes + rest).reshape(2 ** len(sites), -1)
    return t @ t.conj().T  # basis index: first site most significant


def cyl_edges(Lx, Ly):
    """Lx x Ly cylinder: open in x, periodic in y (Ly even => bipartite)."""
    idx = lambda x, y: x * Ly + y
    e = set()
    for x in range(Lx):
        for y in range(Ly):
            if x + 1 < Lx:
                e.add(tuple(sorted((idx(x, y), idx(x + 1, y)))))
            e.add(tuple(sorted((idx(x, y), idx(x, (y + 1) % Ly)))))
    return sorted(e)


def comb_edges(ncell):
    """Decorated (comb) chain, 3 sites per cell: A_c (deg 3), B_c (chain), P_c (pendant on A_c). Periodic.
    Sublattice A = {A_c}; B = {B_c, P_c}: n_B - n_A = ncell (extensive imbalance, like heavy-hex)."""
    A = lambda c: 3 * (c % ncell); B = lambda c: 3 * (c % ncell) + 1; P = lambda c: 3 * (c % ncell) + 2
    e = []
    for c in range(ncell):
        e += [(A(c), B(c)), (B(c), A(c + 1)), (A(c), P(c))]
    sub = [(-1 if k % 3 == 0 else +1) for k in range(3 * ncell)]   # +1 on B/P sublattice
    return sorted(tuple(sorted(x)) for x in e), sub


def lieb_edges(L):
    """Lieb lattice L x L cells, periodic: corner C (deg 4), right edge R, up edge U (deg 2). 3 sites per cell."""
    C = lambda x, y: 3 * ((x % L) * L + (y % L)); R = lambda x, y: C(x, y) + 1; U = lambda x, y: C(x, y) + 2
    e = set()
    for x in range(L):
        for y in range(L):
            for a, b in [(C(x, y), R(x, y)), (R(x, y), C(x + 1, y)), (C(x, y), U(x, y)), (U(x, y), C(x, y + 1))]:
                e.add(tuple(sorted((a, b))))
    sub = [(-1 if k % 3 == 0 else +1) for k in range(3 * L * L)]
    return sorted(e), sub
