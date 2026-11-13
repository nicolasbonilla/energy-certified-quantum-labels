"""Classical emulation of the SKQD + bit-flip recovery + basis-optimization pipeline of arXiv:2606.15983 (R4 pilot).

Pure numpy/scipy (no TeNPy). Conventions:
  H = 1/4 sum_edges (X X + Y Y + Jz Z Z) on the graph JSON (node indices = rustworkx heavy_hex_graph indices).
  A configuration is a uint64; bit i = 1  <=>  node i is spin DOWN (Z_i = -1). The Neel state has the minority
  colour (eta = -1) down. Sector: popcount = n_down.
  Pauli strings are c * X^x Z^z (Z acts first): X^x Z^z |b> = (-1)^popcount(z & b) |b ^ x>.
"""
import json
import math
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.optimize import minimize

U64 = np.uint64


def pc(a):
    return np.bitwise_count(a).astype(np.int64)


# ----------------------------------------------------------------------------------------------------------- graph
def load_graph(path_or_dict):
    G = json.load(open(path_or_dict)) if isinstance(path_or_dict, str) else path_or_dict
    n = G["n"]
    eta = np.array(G["eta"], dtype=int)               # node-indexed, +1 majority (up)
    edges = [tuple(int(v) for v in e) for e in G["edges"]]
    nn2 = [tuple(int(v) for v in e) for e in G["nn2"]]
    loops = G.get("loops12") or ([G["local"]["loop"]] if G.get("local", {}).get("loop") else [])
    neel = 0
    for i in range(n):
        if eta[i] == -1:
            neel |= 1 << i
    return dict(n=n, eta=eta, edges=edges, nn2=nn2, pairs=edges + nn2, loops=[list(l) for l in loops],
                order=list(G["order"]), neel=neel, n_down=int((eta == -1).sum()), G=G)


def bits_matrix(C, n):
    return ((C[:, None] >> np.arange(n, dtype=U64)[None, :]) & U64(1)).astype(np.int8)


# ------------------------------------------------------------------------------------------------------- sampling
def sample_mps(Ts, order, down_index, N, rng, batch=20000):
    """Perfect sampling of N bitstrings from an MPS given as dense right-canonical tensors (vL, p, vR) in MPS order
    (norm folded into Ts[0]). order[k] = graph node of MPS site k. Returns uint64 configurations."""
    out = np.zeros(N, dtype=U64)
    up_index = 1 - down_index
    for s in range(0, N, batch):
        m = min(batch, N - s)
        L = np.ones((m, 1), dtype=np.result_type(*Ts))
        bits = np.zeros(m, dtype=U64)
        for k, T in enumerate(Ts):
            a_d = L @ T[:, down_index, :]
            a_u = L @ T[:, up_index, :]
            p_d = np.einsum("ij,ij->i", a_d.conj(), a_d).real
            p_u = np.einsum("ij,ij->i", a_u.conj(), a_u).real
            tot = p_d + p_u
            down = rng.random(m) * tot < p_d
            L = np.where(down[:, None], a_d, a_u)
            L /= np.sqrt(np.where(down, p_d, p_u))[:, None]
            bits |= down.astype(U64) << U64(order[k])
        out[s:s + m] = bits
    return out


def add_noise(bits, n, p, rng):
    """Independent bit flips with probability p on every qubit."""
    if p <= 0:
        return bits.copy()
    out = bits.copy()
    for i in range(n):
        f = rng.random(len(bits)) < p
        out ^= f.astype(U64) << U64(i)
    return out


def recover(bits, n, n_down, rng, chunk=100000):
    """Random bit-flip configuration recovery (2606.15983 Supp. II.2): on every out-of-sector string flip uniformly
    random bits of the excess species until the sector is reached."""
    out = bits.copy()
    w = pc(out)
    bad = np.nonzero(w != n_down)[0]
    sh = np.arange(n, dtype=U64)
    for s in range(0, len(bad), chunk):
        idx = bad[s:s + chunk]
        B = out[idx]
        wb = w[idx]
        M = ((B[:, None] >> sh[None, :]) & U64(1)).astype(bool)
        exc_down = wb > n_down
        elig = np.where(exc_down[:, None], M, ~M)
        k = np.abs(wb - n_down)
        keys = rng.random(M.shape)
        keys[~elig] = 2.0
        order = np.argsort(keys, axis=1)
        sel = np.arange(n)[None, :] < k[:, None]
        rows = np.nonzero(sel)[0]
        cols = order[sel]
        fl = np.zeros(len(idx), dtype=U64)
        np.bitwise_or.at(fl, rows, U64(1) << cols.astype(U64))
        out[idx] = B ^ fl
    assert (pc(out) == n_down).all()
    return out


# ------------------------------------------------------------------------------------------- subspace Hamiltonian
def lookup(C, f):
    pos = np.searchsorted(C, f)
    pos[pos >= len(C)] = 0
    ok = C[pos] == f
    return pos, ok


def diag_energy(C, g, Jz):
    d = np.zeros(len(C))
    for (i, j) in g["edges"]:
        anti = ((C >> U64(i)) ^ (C >> U64(j))) & U64(1)
        d += 0.25 * Jz * (1.0 - 2.0 * anti.astype(float))
    return d


def build_H(C, g, Jz):
    """Projected H on the sorted unique configuration array C (in one Sz sector)."""
    D = len(C)
    rows, cols = [], []
    for (i, j) in g["edges"]:
        anti = (((C >> U64(i)) ^ (C >> U64(j))) & U64(1)).astype(bool)
        idx = np.nonzero(anti)[0]
        f = C[idx] ^ U64((1 << i) | (1 << j))
        pos, ok = lookup(C, f)
        rows.append(pos[ok]); cols.append(idx[ok])
    r = np.concatenate(rows); c = np.concatenate(cols)
    H = sparse.coo_matrix((np.full(len(r), 0.5), (r, c)), shape=(D, D)).tocsr()
    H = H + sparse.diags(diag_energy(C, g, Jz))
    return H.tocsr()


def ground(H, v0=None, tol=1e-10):
    D = H.shape[0]
    if D <= 2000:
        w, V = np.linalg.eigh(H.toarray())
        return float(w[0]), V[:, 0]
    w, V = eigsh(H, k=1, which="SA", v0=v0, tol=tol, ncv=min(D - 1, 60), maxiter=20000)
    return float(w[0]), V[:, 0]


# ---------------------------------------------------------------------------------------------------- observables
def diag_labels(C, amp, g):
    """Labels of a state sum_b amp_b |b> on configurations C (diagonal observables only)."""
    w = np.abs(amp) ** 2
    w = w / w.sum()
    n = g["n"]
    Z = np.array([float(w @ (1.0 - 2.0 * ((C >> U64(i)) & U64(1)).astype(float))) for i in range(n)])
    Czz = []
    for (i, j) in g["pairs"]:
        anti = (((C >> U64(i)) ^ (C >> U64(j))) & U64(1)).astype(float)
        Czz.append(float(w @ (1.0 - 2.0 * anti)))
    loops = []
    for lp in g["loops"]:
        m = 0
        for v in lp:
            m |= 1 << v
        par = (pc(C & U64(m)) & 1).astype(float)
        loops.append(float(w @ (1.0 - 2.0 * par)))
    return dict(Z=Z.tolist(), Czz=Czz, Zloop=loops, m_s=float(g["eta"] @ Z / n))


def label_errors(lab, ref):
    """Mean relative errors as in 2606.15983 Eqs. (3), (15) (absolute value in the denominator), plus signed m_s."""
    def mre(a, b):
        a = np.asarray(a); b = np.asarray(b)
        return float(np.mean(np.abs(a - b) / np.abs(b))) * 100.0
    Z = np.asarray(lab["Z"]); Zr = np.asarray(ref["Z"])
    out = dict(dZ=mre(Z, Zr), dCzz=mre(lab["Czz"], ref["Czz"]),
               dZloop=mre(lab["Zloop"], ref["Zloop"]) if lab.get("Zloop") else None,
               dm_s=float(lab["m_s"] - ref["m_s"]), rel_m_s=float((lab["m_s"] - ref["m_s"]) / ref["m_s"]) * 100,
               frac_sites_overordered=float(np.mean(np.abs(Z) > np.abs(Zr))))
    return out


# ------------------------------------------------------------------------------------------------ Pauli algebra
def anticommute(x1, z1, x2, z2):
    return (bin(x1 & z2).count("1") + bin(z1 & x2).count("1")) & 1


def mult(c1, x1, z1, c2, x2, z2):
    s = -1 if bin(z1 & x2).count("1") & 1 else 1
    return c1 * c2 * s, x1 ^ x2, z1 ^ z2


def H_terms(g, Jz):
    T = []
    for (i, j) in g["edges"]:
        m = (1 << i) | (1 << j)
        T.append((0.25, m, 0))           # X_i X_j
        T.append((-0.25, m, m))          # Y_i Y_j = - X_i X_j Z_i Z_j
        T.append((0.25 * Jz, 0, m))      # Z_i Z_j
    return T


def edge_colouring(g):
    """Proper 3-edge-colouring of a bipartite graph of max degree 3 (Kempe-chain swaps; deterministic)."""
    n = g["n"]
    at = [dict() for _ in range(n)]          # at[v][colour] = neighbour
    for (u, v) in g["edges"]:
        fu = [c for c in range(3) if c not in at[u]]
        fv = [c for c in range(3) if c not in at[v]]
        common = [c for c in fu if c in fv]
        if common:
            a = common[0]
        else:
            a, b = fu[0], fv[0]              # a free at u (used at v), b free at v
            path = []
            w, c = v, a
            while c in at[w]:
                x = at[w][c]
                path.append((w, x, c))
                w, c = x, (b if c == a else a)
            assert all(u not in (p, q) for (p, q, _) in path)
            for (p, q, c) in path:
                del at[p][c]; del at[q][c]
            for (p, q, c) in path:
                c2 = b if c == a else a
                at[p][c2] = q; at[q][c2] = p
        at[u][a] = v; at[v][a] = u
    col = {}
    for v in range(n):
        for c, w in at[v].items():
            col[tuple(sorted((v, w)))] = c
    assert len(col) == len(g["edges"])
    for v in range(n):
        assert len(at[v]) == len(set(at[v].keys()))
    return col


def bo_gates(g, orientation="minority_control"):
    """One layer of CNOT-RY(theta)-CNOT blocks = exp(-i theta/2 Z_c Y_t) on every edge, in 3 sub-layers by edge
    colour (sub-layer 0 acts first). Returns list of (c, t, sublayer)."""
    col = edge_colouring(g)
    eta = g["eta"]
    gates = []
    for (a, b) in g["edges"]:
        e = tuple(sorted((a, b)))
        c, t = (a, b) if eta[a] == -1 else (b, a)
        if orientation == "majority_control" or (orientation == "alt_sublayer" and col[e] % 2 == 1):
            c, t = t, c
        gates.append((c, t, col[e]))
    gates.sort(key=lambda q: (q[2], q[0], q[1]))
    return gates


def propagate(terms, gates):
    """U O U^dagger for U = prod over sub-layers (layer 0 first) of exp(-i th_g/2 G_g), G_g = Z_c Y_t.
    terms: list of (coef, x, z). Returns dict (x, z) -> list of (coef, cosmask, sinmask) with real coefficients."""
    cur = {}
    for (c, x, z) in terms:
        cur.setdefault((x, z), []).append((complex(c), 0, 0))
    for gi, (gc, gt, _) in enumerate(gates):
        xg = 1 << gt
        zg = (1 << gc) | (1 << gt)
        cg = 1j                                  # Z_c Y_t = i X_t Z_c Z_t
        bit = 1 << gi
        new = {}
        for (x, z), monos in cur.items():
            if anticommute(x, z, xg, zg):
                new.setdefault((x, z), []).extend((m[0], m[1] | bit, m[2]) for m in monos)
                c2, x2, z2 = mult(1.0, x, z, cg, xg, zg)
                fac = 1j * c2
                new.setdefault((x2, z2), []).extend((m[0] * fac, m[1], m[2] | bit) for m in monos)
            else:
                new.setdefault((x, z), []).extend(monos)
        cur = new
    out = {}
    for k, monos in cur.items():
        for (c, cm, sm) in monos:
            assert abs(c.imag) < 1e-12, c
        out[k] = [(c.real, cm, sm) for (c, cm, sm) in monos]
    return out


def sector_relevant(strings):
    """Keep strings whose X part has even weight (others have zero matrix elements inside one Sz sector)."""
    return {k: v for k, v in strings.items() if bin(k[0]).count("1") % 2 == 0}


MAX_TABLE_BITS = 14


class GroupedOp:
    """A propagated operator restricted to a sector subspace, grouped by X-mask for fast evaluation."""

    def __init__(self, strings, n_gates):
        self.n_gates = n_gates
        groups = {}
        for (x, z), monos in strings.items():
            groups.setdefault(x, []).append((z, monos))
        self.groups = []
        mono_coef, mono_g, mono_kind, mono_str = [], [], [], []
        s_index = 0
        for x, lst in groups.items():
            S = 0
            for z, _ in lst:
                S |= z
            pos = [i for i in range(64) if (S >> i) & 1]
            zp = []
            for z, monos in lst:
                p = 0
                for k, i in enumerate(pos):
                    if (z >> i) & 1:
                        p |= 1 << k
                zp.append(p)
                for (c, cm, sm) in monos:
                    gl = [i for i in range(n_gates) if (cm >> i) & 1]
                    sl = [i for i in range(n_gates) if (sm >> i) & 1]
                    mono_coef.append(c)
                    mono_g.append(gl + sl)
                    mono_kind.append([0] * len(gl) + [1] * len(sl))
                    mono_str.append(s_index)
                s_index += 1
            if len(pos) <= MAX_TABLE_BITS:
                npat = 1 << len(pos)
                pats = np.arange(npat)
                zp_arr = np.array(zp, dtype=np.int64)
                sign = 1.0 - 2.0 * (np.bitwise_count((zp_arr[:, None] & pats[None, :]).astype(np.uint64)) & 1)
                self.groups.append(dict(x=x, pos=pos, sign=sign, s0=s_index - len(lst), ns=len(lst), direct=False))
            else:   # wide support (e.g. the diagonal group): evaluate every string directly
                zm = np.array([z for z, _ in lst], dtype=U64)
                self.groups.append(dict(x=x, pos=pos, zm=zm, s0=s_index - len(lst), ns=len(lst), direct=True))
        self.n_strings = s_index
        Lmax = max(len(g) for g in mono_g) if mono_g else 1
        self.Lmax = Lmax
        Nm = len(mono_coef)
        self.mcoef = np.array(mono_coef)
        self.mstr = np.array(mono_str, dtype=np.int64)
        self.mg = np.full((Nm, max(Lmax, 1)), n_gates, dtype=np.int64)   # index n_gates = dummy factor 1
        self.mk = np.zeros((Nm, max(Lmax, 1)), dtype=np.int64)
        for a, (gl, kl) in enumerate(zip(mono_g, mono_kind)):
            self.mg[a, :len(gl)] = gl
            self.mk[a, :len(kl)] = kl
        self.max_support = max((len(G["pos"]) for G in self.groups), default=0)

    def _pairs(self, C, x):
        """Indices (row = index of b^x, col = index of b) of subspace pairs connected by X-mask x, and the bits b."""
        D = len(C)
        if x == 0:
            idx = np.arange(D)
            return idx, idx, C
        xm = U64(x)
        wx = bin(x).count("1")
        bal = pc(C & xm) * 2 == wx
        idx = np.nonzero(bal)[0]
        f = C[idx] ^ xm
        pos, ok = lookup(C, f)
        return pos[ok], idx[ok], C[idx[ok]]

    @staticmethod
    def _pattern(b, pos):
        p = np.zeros(len(b), dtype=np.int64)
        for k, i in enumerate(pos):
            p |= (((b >> U64(i)) & U64(1)).astype(np.int64)) << k
        return p

    def string_expectations(self, C, amp):
        """e_s = sum_b amp[b^x] amp[b] (-1)^popcount(z_s & b) for every string (real amplitudes)."""
        e = np.zeros(self.n_strings)
        for G in self.groups:
            r, c, b = self._pairs(C, G["x"])
            if len(r) == 0:
                continue
            if G["direct"]:
                w = amp[r] * amp[c]
                for k, z in enumerate(G["zm"]):
                    e[G["s0"] + k] = w @ (1.0 - 2.0 * (pc(b & z) & 1))
                continue
            pat = self._pattern(b, G["pos"])
            h = np.bincount(pat, weights=amp[r] * amp[c], minlength=G["sign"].shape[1])
            e[G["s0"]:G["s0"] + G["ns"]] = G["sign"] @ h
        return e

    def _factors(self, theta):
        cs = np.concatenate([np.cos(theta), [1.0]])
        sn = np.concatenate([np.sin(theta), [1.0]])
        dcs = np.concatenate([-np.sin(theta), [0.0]])
        dsn = np.concatenate([np.cos(theta), [0.0]])
        F = np.where(self.mk == 0, cs[self.mg], sn[self.mg])
        dF = np.where(self.mk == 0, dcs[self.mg], dsn[self.mg])
        return F, dF

    def string_coefs(self, theta):
        F, _ = self._factors(theta)
        return np.bincount(self.mstr, weights=self.mcoef * F.prod(axis=1), minlength=self.n_strings)

    def value_and_grad(self, theta, e):
        F, dF = self._factors(theta)
        w = self.mcoef * e[self.mstr]
        Nm, L = F.shape
        pre = np.ones((Nm, L + 1)); suf = np.ones((Nm, L + 1))
        for k in range(L):
            pre[:, k + 1] = pre[:, k] * F[:, k]
            suf[:, L - k - 1] = suf[:, L - k] * F[:, L - k - 1]
        val = float(w @ pre[:, L])
        grad = np.zeros(self.n_gates + 1)
        for k in range(L):
            gk = w * pre[:, k] * suf[:, k + 1] * dF[:, k]
            grad += np.bincount(self.mg[:, k], weights=gk, minlength=self.n_gates + 1)
        return val, grad[:self.n_gates]

    def matrix(self, C, theta):
        coefs = self.string_coefs(theta)
        D = len(C)
        R, Cc, V = [], [], []
        for G in self.groups:
            r, c, b = self._pairs(C, G["x"])
            if len(r) == 0:
                continue
            if G["direct"]:
                v = np.zeros(len(b))
                for k, z in enumerate(G["zm"]):
                    cf = coefs[G["s0"] + k]
                    if cf != 0:
                        v += cf * (1.0 - 2.0 * (pc(b & z) & 1))
            else:
                table = coefs[G["s0"]:G["s0"] + G["ns"]] @ G["sign"]
                pat = self._pattern(b, G["pos"])
                v = table[pat]
            keep = v != 0
            R.append(r[keep]); Cc.append(c[keep]); V.append(v[keep])
        M = sparse.coo_matrix((np.concatenate(V), (np.concatenate(R), np.concatenate(Cc))), shape=(D, D)).tocsr()
        return M

    def expectation(self, C, amp, theta):
        return float(self.string_coefs(theta) @ self.string_expectations(C, amp))


def basis_optimize(C, alpha, g, Jz, gates, rng, n_starts=4, scale=0.3, maxiter=500):
    """Minimize C(theta) = <alpha|U H U^dag|alpha> over per-gate angles (alpha fixed), as in 2606.15983 Eqs. (8)-(10);
    then re-diagonalize U H U^dag in the same subspace (Eq. (11))."""
    strings = sector_relevant(propagate(H_terms(g, Jz), gates))
    op = GroupedOp(strings, len(gates))
    e = op.string_expectations(C, alpha)
    E0 = op.value_and_grad(np.zeros(len(gates)), e)[0]
    best = None
    starts = [np.zeros(len(gates)) + 1e-3] + [rng.normal(0, scale, len(gates)) for _ in range(n_starts - 1)]
    for th0 in starts:
        r = minimize(lambda t: op.value_and_grad(t, e), th0, jac=True, method="L-BFGS-B",
                     options=dict(maxiter=maxiter, gtol=1e-9, ftol=1e-13))
        if best is None or r.fun < best.fun:
            best = r
    theta = best.x
    Hp = op.matrix(C, theta)
    asym = abs(Hp - Hp.T).max() if Hp.nnz else 0.0
    Ep, psi = ground(Hp, v0=alpha)
    return dict(theta=theta, C_alpha_at_0=E0, C_alpha_opt=float(best.fun), E_bo=Ep, psi=psi, n_strings=op.n_strings,
                n_groups=len(op.groups), max_support=op.max_support, asym=float(asym), op=op)


def rotated_labels(C, psi, g, gates, theta):
    """Labels of the physical state U^dag psi: <psi| U O U^dag |psi> for Z_i, C_zz pairs (loops not rotated)."""
    n = g["n"]
    Z = []
    for i in range(n):
        op = GroupedOp(sector_relevant(propagate([(1.0, 0, 1 << i)], gates)), len(gates))
        Z.append(op.expectation(C, psi, theta))
    Czz = []
    for (i, j) in g["pairs"]:
        op = GroupedOp(sector_relevant(propagate([(1.0, 0, (1 << i) | (1 << j))], gates)), len(gates))
        Czz.append(op.expectation(C, psi, theta))
    Z = np.array(Z)
    return dict(Z=Z.tolist(), Czz=Czz, Zloop=[], m_s=float(g["eta"] @ Z / n))


# ---------------------------------------------------------------------------------------------------- dense (tests)
PAULI = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]], complex), "Y": np.array([[0, -1j], [1j, 0]]),
         "Z": np.diag([1.0 + 0j, -1.0])}


def dense_op(n, ops):
    """ops: dict site -> 'X'|'Y'|'Z'. Basis index = sum_i bit_i 2^i, bit 1 = down = Z eigenvalue -1."""
    M = np.array([[1.0 + 0j]])
    for i in reversed(range(n)):
        M = np.kron(M, PAULI[ops.get(i, "I")])
    return M


def dense_pauli(n, c, x, z):
    D = 1 << n
    b = np.arange(D)
    sgn = 1.0 - 2.0 * (np.bitwise_count((b & z).astype(np.uint64)) & 1)
    M = np.zeros((D, D), complex)
    M[b ^ x, b] = c * sgn
    return M


def dense_H(g, Jz):
    n = g["n"]
    H = 0
    for (c, x, z) in H_terms(g, Jz):
        H = H + dense_pauli(n, c, x, z)
    return H
