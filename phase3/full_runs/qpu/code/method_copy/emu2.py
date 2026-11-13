"""Multi-word classical emulation of the SKQD-type method class (n <= 128), full method runs.

Generalizes pilot3's emu.py (uint64, n <= 64) to configurations stored as W = ceil(n/64) uint64 words.
Conventions (unchanged from pilot3):
  H = 1/4 sum_edges (X X + Y Y + Jz Z Z) on the graph JSON (node indices = rustworkx heavy_hex_graph indices).
  Node i lives in word i >> 6, bit i & 63; bit = 1 <=> spin DOWN (Z_i = -1). Neel: minority colour (eta = -1) down.
  Sector: popcount = n_down.
New here:
  * CSet: sorted unique configuration set with exact lookup (W = 1: numeric order, identical to pilot3; W = 2:
    order by a 64-bit mixing key, every lookup verified on all words; key collisions inside a set raise).
  * sample_mps: exact sampling by binomial splitting of identical prefixes inside each batch (same distribution as
    independent shots), returns unique strings, counts, first batch index, and exact log-probabilities and signs.
  * build_H: CSR with int32 indices (off-diagonal) + diagonal vector; ground() through a LinearOperator.
"""
import json
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh, LinearOperator

U64 = np.uint64
_C1 = U64(0xBF58476D1CE4E5B9)
_C2 = U64(0x94D049BB133111EB)
_K = U64(0x9E3779B97F4A7C15)


def nwords(n):
    return (n + 63) // 64


def pc(a):
    return np.bitwise_count(a).astype(np.int64)


def popcount(B):
    return pc(B).sum(axis=1)


def _mix(x):
    x = x ^ (x >> U64(30))
    x = x * _C1
    x = x ^ (x >> U64(27))
    x = x * _C2
    return x ^ (x >> U64(31))


def key(B):
    if B.shape[1] == 1:
        return B[:, 0].copy()
    if B.shape[1] == 2:
        return _mix(B[:, 0] ^ _mix(B[:, 1] + _K))
    raise ValueError("n > 128 not supported")


def mask(n, sites):
    m = np.zeros(nwords(n), dtype=U64)
    for i in sites:
        m[i >> 6] |= U64(1) << U64(i & 63)
    return m


def bit(B, i):
    return ((B[:, i >> 6] >> U64(i & 63)) & U64(1)).astype(np.int8)


def from_int(vals, n):
    """Python ints -> (N, W) words (tests and Neel)."""
    W = nwords(n)
    B = np.zeros((len(vals), W), dtype=U64)
    for r, v in enumerate(vals):
        for w in range(W):
            B[r, w] = U64((int(v) >> (64 * w)) & 0xFFFFFFFFFFFFFFFF)
    return B


def to_int(B):
    out = []
    for row in B:
        v = 0
        for w in range(len(row)):
            v |= int(row[w]) << (64 * w)
        out.append(v)
    return out


def unique_rows(B, *extra, reduce=None):
    """Sort rows by key (then words) and drop duplicates. extra arrays are carried along; reduce[i] in
    {'sum', 'min', 'first'} says how duplicates of extra[i] combine. Returns (B_unique, key_unique, extras...)."""
    k = key(B)
    W = B.shape[1]
    if W == 1:
        order = np.argsort(k, kind="stable")
    else:
        order = np.lexsort(tuple(B[:, w] for w in range(W - 1, -1, -1)) + (k,))
    k = k[order]
    Bs = B[order]
    if len(k) == 0:
        return (Bs, k) + tuple(e[order] for e in extra)
    new = np.ones(len(k), dtype=bool)
    same = k[1:] == k[:-1]
    for w in range(W):
        same &= Bs[1:, w] == Bs[:-1, w]
    new[1:] = ~same
    starts = np.nonzero(new)[0]
    Bu = Bs[starts]
    ku = k[starts]
    if len(ku) > 1 and np.any(ku[1:] == ku[:-1]):
        raise RuntimeError("64-bit key collision between distinct configurations")
    outs = []
    for i, e in enumerate(extra):
        es = e[order]
        r = (reduce or ["first"] * len(extra))[i]
        if r == "sum":
            outs.append(np.add.reduceat(es, starts))
        elif r == "min":
            outs.append(np.minimum.reduceat(es, starts))
        else:
            outs.append(es[starts])
    return (Bu, ku) + tuple(outs)


class CSet:
    """Sorted unique configuration set (rows of uint64 words)."""

    def __init__(self, B, n, presorted=False):
        self.n = n
        self.W = nwords(n)
        B = np.ascontiguousarray(B, dtype=U64).reshape(-1, self.W)
        if presorted:
            self.B, self.k = B, key(B)
        else:
            self.B, self.k = unique_rows(B)

    def __len__(self):
        return len(self.k)

    def lookup(self, Q):
        kq = key(Q)
        pos = np.searchsorted(self.k, kq)
        pos[pos >= len(self.k)] = 0
        ok = self.k[pos] == kq
        if self.W > 1:
            for w in range(self.W):
                ok &= self.B[pos, w] == Q[:, w]
        return pos, ok

    def contains(self, Q):
        return self.lookup(Q)[1]


# ----------------------------------------------------------------------------------------------------------- graph
def load_graph(path_or_dict):
    G = json.load(open(path_or_dict)) if isinstance(path_or_dict, str) else path_or_dict
    n = G["n"]
    eta = np.array(G["eta"], dtype=int)
    edges = [tuple(int(v) for v in e) for e in G["edges"]]
    nn2 = [tuple(int(v) for v in e) for e in G["nn2"]]
    loops = G.get("loops12") or ([G["local"]["loop"]] if G.get("local", {}).get("loop") else [])
    neel = mask(n, [i for i in range(n) if eta[i] == -1])
    return dict(n=n, W=nwords(n), eta=eta, edges=edges, nn2=nn2, pairs=edges + nn2, loops=[list(l) for l in loops],
                order=list(G["order"]), neel=neel, n_down=int((eta == -1).sum()), G=G)


# ------------------------------------------------------------------------------------------------------- sampling
def sample_mps(Ts, order, down_index, N, rng, n, batch=100000, want_amp=True, merge=True):
    """Exact sampling of N shots from an MPS given as dense right-canonical tensors (vL, p, vR) in MPS order (norm
    folded into Ts[0]); order[k] = graph node of MPS site k. Within each batch identical prefixes are split by
    binomial draws (same law as independent shots). Returns dict with B (unique strings, CSet order), count,
    first (index of the first batch containing the string), logp (log |psi_b|^2 of the normalized state) and sign
    (phase of psi_b relative to the MPS gauge; real states: +-1). merge=False: rows unique within each batch, with
    their batch index ('batch') and per-batch counts, not merged across batches."""
    W = nwords(n)
    up_index = 1 - down_index
    dt = np.result_type(*Ts)
    allB, allc, allf, alll, alls = [], [], [], [], []
    nb = 0
    for s in range(0, N, batch):
        m = min(batch, N - s)
        L = np.ones((1, 1), dtype=dt)
        cnt = np.array([m], dtype=np.int64)
        bits = np.zeros((1, W), dtype=U64)
        logp = np.zeros(1)
        for k, T in enumerate(Ts):
            vL, p, vR = T.shape
            A = (L @ T.reshape(vL, p * vR)).reshape(len(cnt), p, vR)
            if np.iscomplexobj(A):
                pr = (A.real ** 2 + A.imag ** 2).sum(axis=2)
            else:
                pr = (A * A).sum(axis=2)
            tot = pr.sum(axis=1)
            pdn = np.clip(pr[:, down_index] / tot, 0.0, 1.0)
            cd = rng.binomial(cnt, pdn)
            cu = cnt - cd
            id_d = np.nonzero(cd > 0)[0]
            id_u = np.nonzero(cu > 0)[0]
            node = order[k]
            bm = U64(1) << U64(node & 63)
            Ld = A[id_d, down_index, :] / np.sqrt(pr[id_d, down_index])[:, None]
            Lu = A[id_u, up_index, :] / np.sqrt(pr[id_u, up_index])[:, None]
            L = np.concatenate([Ld, Lu], axis=0)
            bd = bits[id_d].copy()
            bd[:, node >> 6] |= bm
            bits = np.concatenate([bd, bits[id_u]], axis=0)
            logp = np.concatenate([logp[id_d] + np.log(pdn[id_d]), logp[id_u] + np.log1p(-pdn[id_u])])
            cnt = np.concatenate([cd[id_d], cu[id_u]])
        sign = L[:, 0] / np.abs(L[:, 0])
        allB.append(bits); allc.append(cnt); allf.append(np.full(len(cnt), nb, dtype=np.int32))
        alll.append(logp); alls.append(sign)
        nb += 1
    B = np.concatenate(allB)
    if not merge:
        out = dict(B=B, count=np.concatenate(allc), batch=np.concatenate(allf), n_batches=nb, batch_size=batch, N=N)
        if want_amp:
            out.update(logp=np.concatenate(alll), sign=np.concatenate(alls))
        return out
    Bu, ku, c, f, lp, sg = unique_rows(B, np.concatenate(allc), np.concatenate(allf), np.concatenate(alll),
                                       np.concatenate(alls), reduce=["sum", "min", "first", "first"])
    out = dict(B=Bu, count=c, first=f, n_batches=nb, batch=batch, N=N)
    if want_amp:
        out.update(logp=lp, sign=sg)
    return out


def expand(B, count):
    """Unique strings with counts -> one row per shot (random order irrelevant: noise is i.i.d. per shot)."""
    return np.repeat(B, count, axis=0)


def add_noise(B, n, p, rng):
    """Independent bit flips with probability p on every qubit of every row."""
    out = B.copy()
    if p <= 0:
        return out
    for i in range(n):
        f = rng.random(len(B)) < p
        out[:, i >> 6] ^= f.astype(U64) << U64(i & 63)
    return out


def bits_matrix(B, n):
    M = np.zeros((len(B), n), dtype=bool)
    for i in range(n):
        M[:, i] = bit(B, i).astype(bool)
    return M


def from_bits_matrix(M):
    N, n = M.shape
    W = nwords(n)
    B = np.zeros((N, W), dtype=U64)
    for i in range(n):
        B[:, i >> 6] |= M[:, i].astype(U64) << U64(i & 63)
    return B


def recover(B, n, n_down, rng, chunk=100000):
    """Random bit-flip configuration recovery (2606.15983 Supp. II.2): on every out-of-sector string flip uniformly
    random bits of the excess species until the sector is reached."""
    out = B.copy()
    w = popcount(out)
    bad = np.nonzero(w != n_down)[0]
    for s in range(0, len(bad), chunk):
        idx = bad[s:s + chunk]
        M = bits_matrix(out[idx], n)
        wb = w[idx]
        exc_down = wb > n_down
        elig = np.where(exc_down[:, None], M, ~M)
        k = np.abs(wb - n_down)
        keys = rng.random(M.shape)
        keys[~elig] = 2.0
        order = np.argsort(keys, axis=1)
        sel = np.arange(n)[None, :] < k[:, None]
        rows = np.nonzero(sel)[0]
        cols = order[sel]
        F = np.zeros(M.shape, dtype=bool)
        F[rows, cols] = True
        out[idx] = from_bits_matrix(M ^ F)
    assert (popcount(out) == n_down).all()
    return out


# ------------------------------------------------------------------------------------------- subspace Hamiltonian
def diag_energy(cs, g, Jz):
    d = np.zeros(len(cs))
    for (i, j) in g["edges"]:
        anti = bit(cs.B, i) ^ bit(cs.B, j)
        d += 0.25 * Jz * (1.0 - 2.0 * anti)
    return d


class SubH:
    """Projected H = 0.5 * A (flip-flop part, CSR, int32) + diag on a CSet."""

    def __init__(self, cs, g, Jz):
        D = len(cs)
        rows, cols = [], []
        diag = np.zeros(D)
        for (i, j) in g["edges"]:
            anti = (bit(cs.B, i) ^ bit(cs.B, j)).astype(bool)
            diag += 0.25 * Jz * np.where(anti, -1.0, 1.0)
            idx = np.nonzero(anti)[0]
            Q = cs.B[idx] ^ mask(g["n"], (i, j))[None, :]
            pos, ok = cs.lookup(Q)
            rows.append(pos[ok].astype(np.int32)); cols.append(idx[ok].astype(np.int32))
        r = np.concatenate(rows) if rows else np.zeros(0, np.int32)
        c = np.concatenate(cols) if cols else np.zeros(0, np.int32)
        order = np.argsort(r, kind="stable")
        indices = c[order].astype(np.int32)
        indptr = np.zeros(D + 1, dtype=np.int64)
        np.cumsum(np.bincount(r, minlength=D), out=indptr[1:])
        if indptr[-1] < 2 ** 31:
            indptr = indptr.astype(np.int32)
        self.A = sparse.csr_matrix((np.full(len(indices), 0.5), indices, indptr), shape=(D, D))
        self.diag = diag
        self.D = D
        self.nnz = int(self.A.nnz + D)

    def matvec(self, v):
        return self.A @ v + self.diag * v

    def energy(self, a):
        a = np.asarray(a, float)
        return float(a @ self.matvec(a) / (a @ a))

    def toarray(self):
        return self.A.toarray() + np.diag(self.diag)


def ground(Hs, v0=None, tol=1e-10):
    D = Hs.D
    if D <= 2000:
        w, V = np.linalg.eigh(Hs.toarray())
        return float(w[0]), V[:, 0]
    op = LinearOperator((D, D), matvec=Hs.matvec, dtype=float)
    ncv = 40 if D < 3_000_000 else 24
    w, V = eigsh(op, k=1, which="SA", v0=v0, tol=tol, ncv=min(D - 1, ncv), maxiter=50000)
    return float(w[0]), V[:, 0]


def neel_start(cs, g):
    v0 = np.ones(len(cs)) / np.sqrt(len(cs))
    pos, ok = cs.lookup(g["neel"][None, :])
    if ok[0]:
        v0 = v0 * 0.01
        v0[pos[0]] = 1.0
    return v0


# ---------------------------------------------------------------------------------------------------- observables
def diag_labels(cs, w, g, weights=False):
    """Labels of a state on configurations cs: amplitudes w (weights=False) or probabilities w (weights=True)."""
    w = np.asarray(w, float)
    if not weights:
        w = w * w
    w = w / w.sum()
    n = g["n"]
    B = cs.B
    Z = np.array([float(w @ (1.0 - 2.0 * bit(B, i))) for i in range(n)])
    Czz = [float(w @ (1.0 - 2.0 * (bit(B, i) ^ bit(B, j)))) for (i, j) in g["pairs"]]
    loops = []
    for lp in g["loops"]:
        m = mask(n, lp)
        par = (pc(B & m[None, :]).sum(axis=1) & 1).astype(float)
        loops.append(float(w @ (1.0 - 2.0 * par)))
    return dict(Z=Z.tolist(), Czz=Czz, Zloop=loops, m_s=float(g["eta"] @ Z / n))


def label_errors(lab, ref):
    """Mean relative errors as in 2606.15983 Eqs. (3), (15) (|.| in the denominator), plus signed quantities."""
    def mre(a, b):
        a = np.asarray(a); b = np.asarray(b)
        return float(np.mean(np.abs(a - b) / np.abs(b))) * 100.0
    Z = np.asarray(lab["Z"]); Zr = np.asarray(ref["Z"])
    C = np.asarray(lab["Czz"]); Cr = np.asarray(ref["Czz"])
    out = dict(dZ=mre(Z, Zr), dCzz=mre(C, Cr),
               dZloop=mre(lab["Zloop"], ref["Zloop"]) if lab.get("Zloop") else None,
               dm_s=float(lab["m_s"] - ref["m_s"]), rel_m_s=float((lab["m_s"] - ref["m_s"]) / ref["m_s"]) * 100,
               frac_sites_overordered=float(np.mean(np.abs(Z) > np.abs(Zr))),
               signed_dZ_mean=float(np.mean(np.sign(Zr) * (Z - Zr))),
               signed_dZ_min=float(np.min(np.sign(Zr) * (Z - Zr))),
               frac_Czz_stronger=float(np.mean(np.abs(C) > np.abs(Cr))),
               signed_dCzz_mean=float(np.mean(np.sign(Cr) * (C - Cr))),
               signed_dZloop_mean=(float(np.mean(np.sign(ref["Zloop"]) * (np.asarray(lab["Zloop"]) -
                                                                          np.asarray(ref["Zloop"]))))
                                   if lab.get("Zloop") else None))
    return out


# ---------------------------------------------------------------------------------------------------- dense (tests)
def dense_index(B):
    """(N, W) words -> python-int basis indices (toy sizes only)."""
    return np.array(to_int(B), dtype=np.int64)
