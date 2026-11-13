"""Sector exact diagonalization for H = sum_b J_b sigma_i . sigma_j (Pauli units) and pair labels
C_ij = sigma_i . sigma_j / 3, in the S^z sector with n_up up spins (n_up = ceil(n/2): S^z = 0 or +1/2).

For SU(2)-invariant H and labels, the lowest multiplet of H - lam*S*O always has a member in this sector, so the sector
ground energy is the global one at every lam: the information limit computed here is the one over ALL states (no
sector assumption; DECLARATION section 0).

Basis: integers whose bit i = 1 means site i is UP (Z_i = +1). Every eigsh call starts from ONE fixed random vector
(seed 20261031), never from a previous eigenvector (lesson of the pilots); the residual is returned with every
eigenvector.
"""
import itertools
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

SEED = 20261031


class Sector:
    def __init__(self, n, nup=None):
        self.n = n
        self.nup = (n + 1) // 2 if nup is None else nup
        st = np.fromiter((sum(1 << i for i in c) for c in itertools.combinations(range(n), self.nup)),
                         dtype=np.int64)
        st.sort()
        self.states = st
        self.D = len(st)
        self.bits = ((st[:, None] >> np.arange(n)) & 1).astype(np.int8)
        self.z = (2 * self.bits - 1).astype(np.int8)
        rng = np.random.default_rng(SEED)
        self.v0 = rng.standard_normal(self.D)

    def sdots(self, pairs, weights):
        """sum_p w_p sigma_i . sigma_j = sum_p w_p (2 F_ij + Z_i Z_j) as a CSR matrix (F_ij = flip of an antiparallel
        pair; <s'|(XX + YY)|s> = 2)."""
        rows, cols, vals = [], [], []
        diag = np.zeros(self.D)
        for (i, j), w in zip(pairs, weights):
            if w == 0:
                continue
            diff = self.bits[:, i] != self.bits[:, j]
            idx = np.nonzero(diff)[0]
            f = self.states[idx] ^ ((1 << i) | (1 << j))
            rows.append(idx)
            cols.append(np.searchsorted(self.states, f))
            vals.append(np.full(len(idx), 2.0 * w))
            diag += w * self.z[:, i].astype(float) * self.z[:, j]
        if rows:
            r = np.concatenate(rows); c = np.concatenate(cols); v = np.concatenate(vals)
            M = sp.csr_matrix((v, (r, c)), shape=(self.D, self.D))
        else:
            M = sp.csr_matrix((self.D, self.D))
        return (M + sp.diags(diag)).tocsr()

    def hamiltonian(self, bonds, J):
        return self.sdots(bonds, J)

    def lowest(self, A, tol=1e-12, k=1):
        w, v = sla.eigsh(A, k=k, which="SA", tol=tol, v0=self.v0)
        o = np.argsort(w)
        w, v = w[o], v[:, o]
        res = [float(np.linalg.norm(A @ v[:, i] - w[i] * v[:, i])) for i in range(k)]
        return w, v, res

    def pair_corr(self, psi, i, j):
        """<C_ij> = <sigma_i . sigma_j>/3 for a normalized real vector."""
        diff = self.bits[:, i] != self.bits[:, j]
        idx = np.nonzero(diff)[0]
        f = np.searchsorted(self.states, self.states[idx] ^ ((1 << i) | (1 << j)))
        zz = float(np.dot(psi * psi, self.z[:, i].astype(float) * self.z[:, j]))
        flip = 2.0 * float(np.dot(psi[idx], psi[f]))
        return (flip + zz) / 3.0

    def all_corr(self, psi):
        n = self.n
        C = np.eye(n)
        for i in range(n):
            for j in range(i + 1, n):
                C[i, j] = C[j, i] = self.pair_corr(psi, i, j)
        return C

    def sz_moments(self, psi):
        m = self.z.sum(1).astype(float) / 2.0
        p = psi * psi
        return float(np.dot(p, m)), float(np.dot(p, m * m) - np.dot(p, m) ** 2)


class LabelSolver:
    """Ground states of H - sign*lam*G (G = S*O, the field operator of a label) in the sector; returns
    <H>, <O> = <G>/S, F = lowest eigenvalue, residual."""

    def __init__(self, sec, H, G, S, tol=1e-12):
        self.sec, self.H, self.G, self.S, self.tol = sec, H, G, float(S), tol

    def solve(self, sign, lam):
        A = (self.H - (sign * lam) * self.G).tocsr() if lam > 0 else self.H
        w, v, res = self.sec.lowest(A, self.tol)
        psi = v[:, 0] / np.linalg.norm(v[:, 0])
        Hpsi = self.H @ psi
        E = float(psi @ Hpsi)
        g = float(psi @ (self.G @ psi))
        return dict(lam=float(lam), E=E, o=g / self.S, F=float(w[0]), residual=float(res[0]), psi=psi)
