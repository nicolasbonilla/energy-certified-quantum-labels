"""Kill test W: common library (lattice, S^z = 0 basis, sparse operators, exact evaluation of any state vector).

Conventions (DECLARATION.md section 3):
  site index i = x*LY + y, x in [0, LX), y in [0, LY), periodic in both directions;
  basis = integers with NUP bits set, bit i = 1 means spin up at site i, sorted increasingly;
  H = sum_<ij> S_i.S_j + J2 sum_<<ij>> S_i.S_j  (spin-1/2 operators);
  O_ms  = (1/n^2) <M_s . M_s>,  M_s = sum_i eps_i S_i,  eps_i = (-1)^(x+y);
  O_dim = (1/n^2) (<B_x^2> + <B_y^2>),  B_a = sum_r (-1)^(r_a) S_r.S_(r+a)   (columnar dimer structure factor).
Nothing here runs at import time.
"""
import hashlib
import json
import os
import time

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import LinearOperator, eigsh


def seed_of(*parts):
    h = hashlib.sha256(("W|" + "|".join(str(p) for p in parts)).encode()).hexdigest()
    return int(h[:8], 16)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    os.replace(tmp, path)


class Lattice:
    def __init__(self, LX=6, LY=4):
        self.LX, self.LY = LX, LY
        self.n = LX * LY
        self.xy = [(i // LY, i % LY) for i in range(self.n)]
        self.eps = np.array([1 if (x + y) % 2 == 0 else -1 for (x, y) in self.xy], dtype=np.int64)

    def site(self, x, y):
        return (x % self.LX) * self.LY + (y % self.LY)

    def j1(self):
        b = []
        for x in range(self.LX):
            for y in range(self.LY):
                b.append((self.site(x, y), self.site(x + 1, y), "x"))
                b.append((self.site(x, y), self.site(x, y + 1), "y"))
        return b

    def j2(self):
        b = []
        for x in range(self.LX):
            for y in range(self.LY):
                b.append((self.site(x, y), self.site(x + 1, y + 1)))
                b.append((self.site(x, y), self.site(x + 1, y - 1)))
        return b

    def check_bonds(self):
        s1 = {frozenset(b[:2]) for b in self.j1()}
        s2 = {frozenset(b) for b in self.j2()}
        assert len(s1) == 2 * self.n and len(s2) == 2 * self.n and not (s1 & s2), "bond sets not distinct"
        return True

    def neel_int(self):
        return int(sum(1 << i for i in range(self.n) if self.eps[i] == 1))

    def translate_x(self, i):
        x, y = self.xy[i]
        return self.site(x + 1, y)

    def translate_y(self, i):
        x, y = self.xy[i]
        return self.site(x, y + 1)


def basis_nup(n, nup):
    a = np.arange(1 << n, dtype=np.int64)
    return a[np.bitwise_count(a) == nup]


def _bond_coo(basis, bonds_w):
    """COO pieces of sum_b w_b S_i.S_j inside one S^z sector (off-diagonal) and its diagonal."""
    dim = basis.size
    idx = np.arange(dim, dtype=np.int64)
    diag = np.zeros(dim)
    rows, cols, vals = [], [], []
    for (i, j, w) in bonds_w:
        bi = (basis >> i) & 1
        bj = (basis >> j) & 1
        same = bi == bj
        diag += np.where(same, 0.25 * w, -0.25 * w)
        m = ~same
        fl = basis[m] ^ ((1 << i) | (1 << j))
        c = np.searchsorted(basis, fl)
        assert np.array_equal(basis[c], fl)
        rows.append(idx[m].astype(np.int32))
        cols.append(c.astype(np.int32))
        vals.append(np.full(c.size, 0.5 * w))
    return diag, rows, cols, vals


def bond_operator(basis, bonds_w):
    dim = basis.size
    diag, rows, cols, vals = _bond_coo(basis, bonds_w)
    idx = np.arange(dim, dtype=np.int32)
    r = np.concatenate(rows + [idx]); c = np.concatenate(cols + [idx]); v = np.concatenate(vals + [diag])
    del rows, cols, vals
    M = sp.csr_matrix((v, (r, c)), shape=(dim, dim))
    M.sum_duplicates()
    return M


def ladder(basis_from, basis_to, n, weights, raise_=False):
    """sum_i w_i S_i^- (raise_=False) or S_i^+ (raise_=True) from basis_from to basis_to, CSR (dim_to x dim_from)."""
    rows, cols, vals = [], [], []
    idx = np.arange(basis_from.size, dtype=np.int32)
    for i in range(n):
        bit = (basis_from >> i) & 1
        m = bit == (0 if raise_ else 1)
        t = basis_from[m] ^ (1 << i)
        r = np.searchsorted(basis_to, t)
        assert np.array_equal(basis_to[r], t)
        rows.append(r.astype(np.int32)); cols.append(idx[m]); vals.append(np.full(r.size, float(weights[i])))
    return sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                         shape=(basis_to.size, basis_from.size))


class Ops:
    """All operators of one (lattice, J2) in the S^z = 0 sector and the two neighbouring sectors."""

    def __init__(self, lat, J2, verbose=True):
        t0 = time.time()
        self.lat, self.J2, self.n = lat, float(J2), lat.n
        n = self.n
        self.basis = basis_nup(n, n // 2)
        self.dim = self.basis.size
        b_m = basis_nup(n, n // 2 - 1)
        b_p = basis_nup(n, n // 2 + 1)
        bw = [(i, j, 1.0) for (i, j, _) in lat.j1()]
        if self.J2 != 0.0:
            bw += [(i, j, self.J2) for (i, j) in lat.j2()]
        self.H = bond_operator(self.basis, bw)
        eps = lat.eps
        self.Mm = ladder(self.basis, b_m, n, eps, raise_=False)   # M_s^- : 0 -> -1
        self.Mp = ladder(self.basis, b_p, n, eps, raise_=True)    # M_s^+ : 0 -> +1
        self.Sm = ladder(self.basis, b_m, n, np.ones(n), raise_=False)
        self.Sp = ladder(self.basis, b_p, n, np.ones(n), raise_=True)
        del b_m, b_p
        mz = np.zeros(self.dim)
        for i in range(n):
            mz += eps[i] * (((self.basis >> i) & 1) - 0.5)
        self.mz2 = mz ** 2
        bx = [(i, j, float((-1) ** lat.xy[i][0])) for (i, j, d) in lat.j1() if d == "x"]
        by = [(i, j, float((-1) ** lat.xy[i][1])) for (i, j, d) in lat.j1() if d == "y"]
        self.Bx = bond_operator(self.basis, bx)
        self.By = bond_operator(self.basis, by)
        # symmetry maps (diagnostics): index of the image of each basis state
        self.tx = self._perm_index([lat.translate_x(i) for i in range(n)])
        self.ty = self._perm_index([lat.translate_y(i) for i in range(n)])
        self.flip = np.searchsorted(self.basis, self.basis ^ ((1 << n) - 1))
        self.build_seconds = time.time() - t0
        if verbose:
            print("%s Ops n=%d J2=%g dim=%d nnz H=%d Mm=%d Bx=%d built in %.1fs" % (
                now(), n, self.J2, self.dim, self.H.nnz, self.Mm.nnz, self.Bx.nnz, self.build_seconds), flush=True)

    def _perm_index(self, perm):
        new = np.zeros_like(self.basis)
        for i, j in enumerate(perm):
            new |= ((self.basis >> i) & 1) << j
        return np.searchsorted(self.basis, new)

    # ---- operator actions ----
    def O_ms(self, v):
        n2 = float(self.n) ** 2
        return (self.mz2 * v + 0.5 * (self.Mm.T @ (self.Mm @ v) + self.Mp.T @ (self.Mp @ v))) / n2

    def O_dim(self, v):
        n2 = float(self.n) ** 2
        return (self.Bx @ (self.Bx @ v) + self.By @ (self.By @ v)) / n2

    def O(self, name, v):
        return self.O_ms(v) if name == "ms" else self.O_dim(v)

    # ---- exact evaluation of a state (any normalisation, real or complex) ----
    def evaluate(self, v):
        v = np.asarray(v)
        nrm2 = float(np.vdot(v, v).real)
        n = self.n
        a2 = np.abs(v) ** 2
        Hv = mul(self.H, v)
        e = float(np.vdot(v, Hv).real) / nrm2 / n
        h2 = float(np.vdot(Hv, Hv).real) / nrm2
        nm = lambda A: np.linalg.norm(mul(A, v)) ** 2
        ms = (float(np.dot(self.mz2, a2)) + 0.5 * (nm(self.Mm) + nm(self.Mp))) / nrm2 / n ** 2
        dim = (nm(self.Bx) + nm(self.By)) / nrm2 / n ** 2
        s2 = 0.5 * (nm(self.Sm) + nm(self.Sp)) / nrm2
        tx = complex(np.vdot(v[self.tx], v)) / nrm2
        ty = complex(np.vdot(v[self.ty], v)) / nrm2
        fl = complex(np.vdot(v[self.flip], v)) / nrm2
        return {"e": e, "var_e_per_site": (h2 - (e * n) ** 2) / n, "ms": float(ms), "dim": float(dim), "S2": float(s2),
                "Tx": [tx.real, tx.imag], "Ty": [ty.real, ty.imag], "flip": [fl.real, fl.imag], "norm2": nrm2}


def mul(A, v):
    """sparse real matrix times real or complex vector without converting the matrix to complex"""
    if np.iscomplexobj(v):
        return (A @ v.real) + 1j * (A @ v.imag)
    return A @ v


def ground(matvec, dim, v0, tol=1e-12, ncv=24, maxiter=20000):
    cnt = [0]

    def mv(x):
        cnt[0] += 1
        return matvec(x)
    A = LinearOperator((dim, dim), matvec=mv, dtype=np.float64)
    w, v = eigsh(A, k=1, which="SA", v0=v0, tol=tol, ncv=ncv, maxiter=maxiter)
    x = v[:, 0]
    res = float(np.linalg.norm(matvec(x) - w[0] * x))
    return float(w[0]), x, cnt[0], res


def int_to_pm(basis_chunk, n):
    """+1 for up (bit set), -1 for down; shape (len, n), float64."""
    return (((basis_chunk[:, None] >> np.arange(n)) & 1) * 2 - 1).astype(np.float64)
