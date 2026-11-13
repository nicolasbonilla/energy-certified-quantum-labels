# r10lib.py -- reviewer "math-thm1" (R10, 2026-11-12): own exact-diagonalization library.
# Written from scratch for this review; it does not import or copy the paper's edlib.py.
# Conventions: spin-1/2, Pauli operators (eigenvalues +-1); basis index bit i = 1 means site i is UP (Z_i = +1).
import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

I2 = sp.identity(2, format="csr", dtype=complex)
SX = sp.csr_matrix(np.array([[0, 1], [1, 0]], dtype=complex))
SY = sp.csr_matrix(np.array([[0, -1j], [1j, 0]], dtype=complex))
# bit = 1 <-> up <-> Z = +1 ; local basis order (bit 0, bit 1) = (down, up)
SZ = sp.csr_matrix(np.array([[-1, 0], [0, 1]], dtype=complex))


def site_op(op, i, n):
    """op acting on site i (bit i of the basis index) of n sites."""
    out = sp.identity(1, format="csr", dtype=complex)
    for s in range(n - 1, -1, -1):          # most significant factor first
        out = sp.kron(out, op if s == i else I2, format="csr")
    return out


def realify(M):
    """drop a vanishing imaginary part (speeds up the eigensolvers)."""
    if sp.issparse(M):
        M = M.tocsr()
        if M.nnz == 0 or np.abs(M.data.imag).max() < 1e-14:
            return M.real.tocsr()
        return M
    return M.real if np.abs(M.imag).max() < 1e-14 else M


class Spins:
    def __init__(self, n):
        self.n = n
        self.X = [site_op(SX, i, n) for i in range(n)]
        self.Y = [site_op(SY, i, n) for i in range(n)]
        self.Z = [site_op(SZ, i, n) for i in range(n)]
        self.dim = 2 ** n
        idx = np.arange(self.dim)
        self.nup = np.zeros(self.dim, dtype=int)
        for i in range(n):
            self.nup += (idx >> i) & 1

    def sector(self, nup):
        return np.where(self.nup == nup)[0]

    def xxz_terms(self, edges, Jz, coeff=0.25, bond_scale=None):
        """list of (support, operator) with h_ij = coeff (XX + YY + Jz ZZ)."""
        terms = []
        for k, (i, j) in enumerate(edges):
            s = 1.0 if bond_scale is None else bond_scale[k]
            h = s * coeff * (self.X[i] @ self.X[j] + self.Y[i] @ self.Y[j] + Jz * self.Z[i] @ self.Z[j])
            terms.append(((i, j), realify(h)))
        return terms

    def tfim_terms(self, edges, J=1.0, h=1.0, hz=0.0):
        """H = -J sum ZZ - h sum X - hz sum Z ; one term per bond and one per site."""
        terms = []
        for (i, j) in edges:
            terms.append(((i, j), realify(-J * self.Z[i] @ self.Z[j])))
        for i in range(self.n):
            terms.append(((i,), realify(-h * self.X[i] - hz * self.Z[i])))
        return terms


def total(terms):
    H = None
    for _, h in terms:
        H = h if H is None else H + h
    return H.tocsr()


def support_indices(support):
    k = len(support)
    idx = []
    for a in range(2 ** k):
        full = 0
        for b, s in enumerate(support):
            if (a >> b) & 1:
                full |= (1 << s)
        idx.append(full)
    return np.array(idx)


def block_op(op_full, block):
    """dense matrix of an operator supported on `block`, in the block-configuration basis (bit a = site block[a])."""
    idx = support_indices(list(block))
    return op_full.tocsr()[idx][:, idx].toarray()


def local_spread(term_op, support):
    """(lambda_max - lambda_min, lambda_min, lambda_max) of a term, from its matrix on the support only."""
    M = block_op(term_op, support)
    w = np.linalg.eigvalsh((M + M.conj().T) / 2)
    return float(w[-1] - w[0]), float(w[0]), float(w[-1])


def kappa(terms, region):
    """kappa_A = sum over the terms that touch the region of (lambda_max - lambda_min)."""
    reg = set(region)
    k = 0.0
    for sup, h in terms:
        if reg & set(sup):
            k += local_spread(h, sup)[0]
    return k


def herm(M):
    return (M + M.conj().T) / 2


def lowest(M, k=1, dense_below=300, v0seed=12345):
    """lowest k eigenpairs of a Hermitian matrix (sparse or dense). Returns (w, V)."""
    d = M.shape[0]
    if d <= dense_below:
        A = M.toarray() if sp.issparse(M) else np.asarray(M)
        w, V = np.linalg.eigh(herm(A))
        return w[:k], V[:, :k]
    rng = np.random.default_rng(v0seed)
    v0 = rng.standard_normal(d)
    kk = min(max(k, 3), d - 2)
    w, V = spla.eigsh(M, k=kk, which="SA", v0=v0, tol=1e-12, ncv=min(d - 1, max(40, 4 * kk)), maxiter=50000)
    o = np.argsort(w)
    return w[o][:k], V[:, o][:, :k]


def expval(op, v):
    return float(np.real(np.vdot(v, op @ v)))


def ens_expval(op, ens):
    """expectation value in the (unnormalised-vector) ensemble: sum_k <v_k|op|v_k>."""
    return float(sum(np.real(np.vdot(v, op @ v)) for v in ens))


class WindowSolver:
    """Exact information limit o^+(E) = max { Tr O s : s in W(E) } for Hermitian H, O already restricted to the
    sector (so sector ground energies are plain ground energies).
    A "chain" of ground states of H - sign*lam*O on a geometric grid of lam is computed once per sign; then
      outer(E) = min over all computed lam of [E - G(lam)]/lam       (weak duality: rigorous upper bound)
      inner(E) = value of an explicit window state: the mixture, with mean energy exactly E, of the two computed
                 ground states whose energies bracket E               (rigorous lower bound)
    and the bracket is tightened by root finding in lam until the two agree.
    Saturation: if E >= E_sat = lowest energy inside the top eigenspace of O, then o^+ = o_max exactly.
    """

    def __init__(self, H, O, dense_below=300, grid=(-4.0, 3.0, 57)):
        self.H = realify(H.tocsr() if sp.issparse(H) else sp.csr_matrix(H))
        self.O = realify(O.tocsr() if sp.issparse(O) else sp.csr_matrix(O))
        self.d = self.H.shape[0]
        self.dense_below = dense_below
        self.grid = grid
        w, V = lowest(self.H, k=min(6, self.d), dense_below=dense_below)
        self.E0 = float(w[0])
        self.spectrum_low = np.array(w, dtype=float)
        self.gap = float(w[1] - w[0]) if len(w) > 1 else np.inf
        deg = int(np.sum(w - w[0] < 1e-9))        # ground-state manifold (degeneracy tolerance 1e-9)
        self.G = V[:, :deg]
        Og = self.G.conj().T @ (self.O @ self.G)
        wg = np.linalg.eigvalsh(herm(np.atleast_2d(Og)))
        self.oGS_minus, self.oGS_plus = float(wg[0]), float(wg[-1])
        self.deg = deg
        self.omax, self.Esat_plus = self._sat(+1)
        m, self.Esat_minus = self._sat(-1)
        self.omin = -m
        self.pts = {+1: {}, -1: {}}      # lam -> (G, <H>, <O>)
        self._last = {+1: None, -1: None}
        self._chain_done = {+1: False, -1: False}
        self.nsolve = 0
        self.rng = np.random.default_rng(2026)

    def _sat(self, sign):
        """(top eigenvalue of sign*O, lowest energy of H inside that eigenspace)."""
        O = self.O
        if (O - sp.diags(O.diagonal())).count_nonzero() == 0:           # diagonal label
            dv = sign * np.real(O.diagonal())
            top = dv.max()
            idx = np.where(dv > top - 1e-12)[0]
            w, _ = lowest(self.H[idx][:, idx], k=1, dense_below=self.dense_below)
            return float(top), float(w[0])
        O2 = (O @ O - sp.identity(self.d)).tocsr()
        if O2.nnz == 0 or np.abs(O2.data).max() < 1e-12:                # involution: projector (1 + sign O)/2
            P = (sp.identity(self.d) + sign * O) / 2
            hmax = float(abs(self.H).sum(axis=1).max()) + 1.0           # > lambda_max(H)
            M = P @ (self.H - hmax * sp.identity(self.d)) @ P
            w, _ = lowest(M.tocsr(), k=1, dense_below=self.dense_below)
            return 1.0, float(w[0] + hmax)
        if self.d <= 1024:
            w, V = np.linalg.eigh(herm(sign * O.toarray()))
            top = w[-1]
            P = V[:, w > top - 1e-10]
            ws = np.linalg.eigvalsh(herm(P.conj().T @ (self.H @ P)))
            return float(top), float(ws[0])
        w, _ = lowest(-sign * O, k=1, dense_below=self.dense_below)
        return float(-w[0]), np.inf

    def solve(self, lam, sign):
        lam = float(lam)
        if lam in self.pts[sign]:
            return self.pts[sign][lam]
        M = self.H - sign * lam * self.O
        if self.d <= self.dense_below:
            w, V = np.linalg.eigh(herm(M.toarray()))
            v = V[:, 0]
            G = float(w[0])
        else:
            v0 = self._last[sign]
            noise = self.rng.standard_normal(self.d)
            if v0 is None:
                v0 = noise
            else:
                v0 = np.real(v0) + 1e-2 * noise / np.linalg.norm(noise)
            w, V = spla.eigsh(M, k=2, which="SA", v0=v0, tol=1e-12, ncv=min(self.d - 1, 32), maxiter=50000)
            k = int(np.argmin(w))
            v = V[:, k]
            G = float(w[k])
            self._last[sign] = v
        self.nsolve += 1
        out = (G, expval(self.H, v), expval(self.O, v))
        self.pts[sign][lam] = out
        return out

    def chain(self, sign):
        if not self._chain_done[sign]:
            for lam in np.logspace(*self.grid):
                self.solve(lam, sign)
            self._chain_done[sign] = True
        lams = np.array(sorted(self.pts[sign].keys()))
        arr = np.array([self.pts[sign][l] for l in lams])
        return lams, arr[:, 0], arr[:, 1], arr[:, 2]

    def _bounds(self, E, sign):
        lams, G, Eh, o = self.chain(sign)
        top = self.omax if sign > 0 else -self.omin
        ogs = self.oGS_plus if sign > 0 else -self.oGS_minus
        outer = min(float(np.min((E - G) / lams)), top)
        so = sign * o
        below = Eh <= E + 1e-13
        inner = ogs
        ka = kb = None
        if below.any():
            ka = int(np.where(below)[0][-1])      # energies are nondecreasing in lam
            inner = max(inner, float(so[below].max()))
            if ka + 1 < len(lams) and Eh[ka + 1] > E:
                kb = ka + 1
                t = (E - Eh[ka]) / (Eh[kb] - Eh[ka])
                inner = max(inner, float((1 - t) * so[ka] + t * so[kb]))
        else:
            kb = 0
            t = (E - self.E0) / (Eh[0] - self.E0)     # mixture with the ground state
            inner = max(inner, float((1 - t) * ogs + t * so[0]))
        la = lams[ka] if ka is not None else None
        lb = lams[kb] if kb is not None else None
        return outer, inner, la, lb

    def extreme(self, eps, sign=+1, refine=True, tol=1e-9, maxit=60):
        """sign*<O> maximised over W(E0+eps): dict(outer=dual value, inner=value of an explicit window state)."""
        E = self.E0 + eps
        top = self.omax if sign > 0 else -self.omin
        Esat = self.Esat_plus if sign > 0 else self.Esat_minus
        ogs = self.oGS_plus if sign > 0 else -self.oGS_minus
        if eps <= 0:
            return dict(outer=ogs, inner=ogs, saturated=False)
        if E >= Esat - 1e-12:
            return dict(outer=top, inner=top, saturated=True)
        outer, inner, la, lb = self._bounds(E, sign)
        it = 0
        while refine and outer - inner > tol and it < maxit:
            it += 1
            if la is None:
                lam = lb / 4.0
            elif lb is None:
                lam = la * 4.0
            else:
                # regula falsi in log lam on <H>(lam) - E, safeguarded by bisection every third step
                Ea = self.pts[sign][la][1]
                Eb = self.pts[sign][lb][1]
                if it % 3 and Eb > Ea:
                    t = min(max((E - Ea) / (Eb - Ea), 0.05), 0.95)
                else:
                    t = 0.5
                lam = float(np.exp((1 - t) * np.log(la) + t * np.log(lb)))
                if lam in self.pts[sign] or lb / la - 1 < 1e-13:
                    break
            self.solve(lam, sign)
            outer, inner, la, lb = self._bounds(E, sign)
        return dict(outer=outer, inner=float(inner), saturated=False)

    def window(self, eps, refine=True, tol=1e-9):
        up = self.extreme(eps, +1, refine=refine, tol=tol)
        dn = self.extreme(eps, -1, refine=refine, tol=tol)
        return dict(o_plus_outer=up["outer"], o_plus_inner=up["inner"],
                    o_minus_outer=-dn["outer"], o_minus_inner=-dn["inner"],
                    w_outer=up["outer"] + dn["outer"], w_inner=up["inner"] + dn["inner"],
                    sat_plus=up["saturated"], sat_minus=dn["saturated"])

    def eps_for_width(self, target_w, lo=1e-8, hi=None, rtol=1e-5, tol=1e-9):
        """smallest eps at which the two-sided width reaches target_w (the width is nondecreasing in eps):
        bisection in log eps on the mean of inner and outer.  Returns np.inf if the width never reaches it."""
        if hi is None:
            hi = max(self.Esat_plus, self.Esat_minus) - self.E0
            if not np.isfinite(hi):
                hi = 50.0

        def f(e):
            r = self.window(e, tol=tol)
            return 0.5 * (r["w_outer"] + r["w_inner"])

        if f(hi) < target_w:
            return np.inf
        if f(lo) >= target_w:
            return lo
        for _ in range(200):
            mid = float(np.sqrt(lo * hi))
            if f(mid) >= target_w:
                hi = mid
            else:
                lo = mid
            if hi / lo - 1 < rtol:
                break
        return hi


# ---------------------------------------------------------------------------------------------
# channels of Theorem 1, as ensembles of (unnormalised) pure states
# ---------------------------------------------------------------------------------------------
def _maps(n, block):
    block = list(block)
    rest = [s for s in range(n) if s not in block]
    idx = np.arange(2 ** n)
    b = np.zeros(2 ** n, dtype=np.int64)
    r = np.zeros(2 ** n, dtype=np.int64)
    for a, s in enumerate(block):
        b |= ((idx >> s) & 1) << a
    for a, s in enumerate(rest):
        r |= ((idx >> s) & 1) << a
    return b, r, len(block), len(rest)


def to_tensor(vec, n, block):
    """psi[b, r] with b = block configuration, r = configuration of the rest."""
    b, r, nb, nr = _maps(n, block)
    psi = np.zeros((2 ** nb, 2 ** nr), dtype=complex)
    psi[b, r] = vec
    return psi, (b, r)


def product_vec(phi_block, chi_rest, maps):
    b, r = maps
    return phi_block[b] * chi_rest[r]


def reset_ensemble(vec, n, block, phi_block):
    """R(rho) = |phi><phi|_B (x) Tr_B rho for rho = |vec><vec|: ensemble { phi (x) <b|vec> : b }."""
    psi, maps = to_tensor(vec, n, block)
    return [product_vec(phi_block, psi[a, :], maps) for a in range(psi.shape[0])
            if np.vdot(psi[a, :], psi[a, :]).real > 1e-30]


def covariant_ensemble(vec, n, block, O_blk, sign=+1):
    """sum_q |phi_q><phi_q| (x) Tr_B(P_q rho P_q), phi_q a top (sign=+1) / bottom (sign=-1) eigenvector of the
    restriction of O to block charge q.  Returns (ensemble of unnormalised full vectors, p_q, c_B, lambda_q).
    O_blk may be a dense matrix on the block or a 1-d array (diagonal label)."""
    psi, maps = to_tensor(vec, n, block)
    kb, kr = psi.shape
    nb = len(list(block))
    pop = np.array([bin(a).count("1") for a in range(kb)])
    O_blk = np.asarray(O_blk)
    if O_blk.ndim == 2 and np.abs(O_blk - np.diag(np.diag(O_blk))).max() < 1e-13:
        O_blk = np.real(np.diag(O_blk))
    ens, pq, lamq, c = [], {}, {}, 0.0
    for q in range(nb + 1):
        idx = np.where(pop == q)[0]
        sub = psi[idx, :]
        p = float(np.real(np.vdot(sub, sub)))
        pq[q] = p
        phi = np.zeros(kb, dtype=complex)
        if O_blk.ndim == 1:
            dv = sign * O_blk[idx]
            k = int(np.argmax(dv))
            lam = float(O_blk[idx][k])
            phi[idx[k]] = 1.0
        else:
            w, V = np.linalg.eigh(herm(O_blk[np.ix_(idx, idx)]))
            k = -1 if sign > 0 else 0
            lam = float(w[k])
            phi[idx] = V[:, k]
        lamq[q] = lam
        c += p * lam
        if p < 1e-30:
            continue
        if len(idx) <= kr:
            for a in range(len(idx)):
                if np.vdot(sub[a, :], sub[a, :]).real > 1e-30:
                    ens.append(product_vec(phi, sub[a, :], maps))
        else:
            rho_q = sub.T @ sub.conj()
            w, U = np.linalg.eigh(herm(rho_q))
            for m in range(len(w)):
                if w[m] > 1e-30:
                    ens.append(product_vec(phi, np.sqrt(w[m]) * U[:, m], maps))
    return ens, pq, float(c), lamq


def reduced_rest_from_ens(ens, n, block):
    """reduced density matrix on the complement of the block, from an ensemble of full vectors."""
    out = None
    for v in ens:
        psi, _ = to_tensor(v, n, block)
        m = psi.T @ psi.conj()
        out = m if out is None else out + m
    return out


def padded_lambda_max(O_blk, block_size):
    """lambda_max of the PADDED operator Pi_q O Pi_q on the whole block space (what the printed formula literally
    says), for every block charge q -- to be compared with the restricted maximum used in the proof."""
    kb = O_blk.shape[0]
    pop = np.array([bin(a).count("1") for a in range(kb)])
    out = {}
    for q in range(block_size + 1):
        P = np.diag((pop == q).astype(float))
        out[q] = float(np.linalg.eigvalsh(herm(P @ O_blk @ P))[-1])
    return out


# ---------------------------------------------------------------------------------------------
# graphs
# ---------------------------------------------------------------------------------------------
def chain(n, periodic=False):
    e = [(i, i + 1) for i in range(n - 1)]
    if periodic and n > 2:
        e.append((n - 1, 0))
    return e


def ladder(L, periodic=False):
    e = []
    for x in range(L):
        e.append((2 * x, 2 * x + 1))
        if x + 1 < L:
            e.append((2 * x, 2 * x + 2))
            e.append((2 * x + 1, 2 * x + 3))
    if periodic and L > 2:
        e.append((2 * (L - 1), 0))
        e.append((2 * (L - 1) + 1, 1))
    return e


def grid(Lx, Ly):
    e = []
    for x in range(Lx):
        for y in range(Ly):
            s = x * Ly + y
            if y + 1 < Ly:
                e.append((s, s + 1))
            if x + 1 < Lx:
                e.append((s, s + Ly))
    return e


def comb(L):
    """backbone 0..L-1 with one tooth on every backbone site: n = 2L (bipartite tree)."""
    e = [(i, i + 1) for i in range(L - 1)]
    e += [(i, L + i) for i in range(L)]
    return e


def heavy_hex_ring(extra=0):
    """one heavy-hex plaquette: 12-site ring (vertex sites 0,2,4,... alternate with bridge sites 1,3,5,...),
    plus `extra` dangling sites attached to the vertex sites 0, 2, 4, ... (those vertices then have degree 3)."""
    e = [(i, (i + 1) % 12) for i in range(12)]
    for k in range(extra):
        e.append((2 * k, 12 + k))
    return e


def degrees(edges, n):
    d = [0] * n
    for i, j in edges:
        d[i] += 1
        d[j] += 1
    return d


def two_colouring(edges, n):
    col = [-1] * n
    adj = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    for s in range(n):
        if col[s] >= 0:
            continue
        col[s] = 0
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if col[v] < 0:
                    col[v] = 1 - col[u]
                    stack.append(v)
                elif col[v] == col[u]:
                    raise ValueError("not bipartite")
    return col
