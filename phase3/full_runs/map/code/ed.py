"""Sector exact diagonalization for the witness pilot (DECLARATION.md SHA-256 529e8dcd..., §5.4).

Graph labels (not the MPS order). Basis: integers whose bit i = 1 means site i is UP (Z = +1).
Every eigsh call starts from ONE fixed random vector (seed 20261029), never from a previous eigenvector
(lesson of pilot/RESULTS.md §11.4); residuals are returned with every eigenvector.
"""
import itertools
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

SEED = 20261029


class Sector:
    def __init__(self, G, nup):
        n = G["n"]
        self.n, self.nup = n, nup
        st = np.array(sorted(sum(1 << i for i in c) for c in itertools.combinations(range(n), nup)), dtype=np.int64)
        self.states = st
        self.D = len(st)
        bits = ((st[:, None] >> np.arange(n)) & 1).astype(np.int8)
        self.z = (2 * bits - 1).astype(np.int8)            # Z_i eigenvalue per basis state
        rows, cols = [], []
        for (i, j) in G["edges"]:
            diff = bits[:, i] != bits[:, j]
            f = st[diff] ^ ((1 << i) | (1 << j))
            rows.append(np.nonzero(diff)[0]); cols.append(np.searchsorted(st, f))
        r = np.concatenate(rows); c = np.concatenate(cols)
        self.Hoff = sp.csr_matrix((np.full(len(r), 0.5), (r, c)), shape=(self.D, self.D))   # 1/4 (XX + YY)
        self.zz = np.zeros(self.D)
        for (i, j) in G["edges"]:
            self.zz += self.z[:, i].astype(float) * self.z[:, j]
        self.eta = np.array(G["eta"], dtype=float)
        self.M = (self.z * self.eta).sum(1).astype(float)    # sum_i eta_i Z_i
        rng = np.random.default_rng(SEED)
        self.v0 = rng.standard_normal(self.D)

    def H(self, Jz):
        return (self.Hoff + sp.diags(0.25 * Jz * self.zz)).tocsr()

    def lowest(self, A, k=1, tol=1e-13):
        w, v = sla.eigsh(A, k=k, which="SA", tol=tol, v0=self.v0)
        o = np.argsort(w)
        w, v = w[o], v[:, o]
        res = [float(np.linalg.norm(A @ v[:, i] - w[i] * v[:, i])) for i in range(k)]
        return w, v, res

    def expect_diag(self, psi, diag):
        return float(np.dot(psi * psi, diag) / np.dot(psi, psi))


def witness_point(sec, H, lam, sign, tol=1e-13):
    """Exact ground state of H - sign*lam*M in the sector: returns (<H>, m_s, residual)."""
    A = (H - sp.diags(sign * lam * sec.M)).tocsr() if lam > 0 else H
    w, v, res = sec.lowest(A, 1, tol)
    psi = v[:, 0]
    E = float(psi @ (H @ psi) / (psi @ psi))
    m = sec.expect_diag(psi, sec.M) / sec.n
    return E, m, res[0]


def witness_at(sec, H, sign, Ethr, E0, m0, lam0=0.005, etol=1e-9, maxit=60, lam_max=64.0):
    """Doubling from lam0, then bisection in lambda until |<H> - Ethr| <= etol; m_s at Ethr by linear interpolation
    between the final bracket points (a two-state mixture, exact energy Ethr)."""
    pts = [(0.0, E0, m0, 0.0)]
    lam = lam0
    while True:
        E, m, r = witness_point(sec, H, lam, sign)
        pts.append((lam, E, m, r))
        if E > Ethr or lam >= lam_max:
            break
        lam *= 2
    below = [p for p in pts if p[1] <= Ethr]
    above = [p for p in pts if p[1] > Ethr]
    lo = max(below, key=lambda p: p[0]); hi = min(above, key=lambda p: p[0])
    it = 0
    while abs(lo[1] - Ethr) > etol and abs(hi[1] - Ethr) > etol and it < maxit:
        lam = 0.5 * (lo[0] + hi[0])
        E, m, r = witness_point(sec, H, lam, sign)
        pts.append((lam, E, m, r))
        if E <= Ethr:
            lo = (lam, E, m, r)
        else:
            hi = (lam, E, m, r)
        it += 1
    if abs(lo[1] - Ethr) <= etol:
        m_at = lo[2]
    elif abs(hi[1] - Ethr) <= etol:
        m_at = hi[2]
    else:
        t = (Ethr - lo[1]) / (hi[1] - lo[1])
        m_at = (1 - t) * lo[2] + t * hi[2]
    return dict(m_at=float(m_at), lam_lo=lo[0], E_lo=lo[1], m_lo=lo[2], lam_hi=hi[0], E_hi=hi[1], m_hi=hi[2],
                n_eval=len(pts) - 1, points=[list(map(float, p)) for p in pts],
                max_residual=float(max(p[3] for p in pts)))
