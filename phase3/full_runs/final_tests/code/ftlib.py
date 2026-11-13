"""Final tests (DECLARATION.md): shared numerics without TeNPy.

Instances, exact diagonalization in a sector, truncated states, local patches, local features, exact Rayleigh quotient.
Conventions as method/code/emu2.py: bit i = 1 <=> site i DOWN (Z_i = -1); sector = number of down spins = Neel's.
H = sum_e J_e [ 1/4 (X X + Y Y) + Jz/4 Z Z ]  (+ sum_i h_i Z_i for embedded patches).
"""
import hashlib
import json
import os
from fractions import Fraction

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh, expm_multiply

import emu2

HERE = os.path.dirname(os.path.abspath(__file__))
JLO, JHI = 0.5, 1.5           # coupling distribution of Test B
K = 10


def js(Jz):
    return "%.1f" % float(Jz)


def seed(*parts):
    return int.from_bytes(hashlib.sha256(("ft|" + "|".join(str(p) for p in parts)).encode()).digest()[:8], "little")


def rng_of(*parts):
    return np.random.default_rng(seed(*parts))


def graph_json(d):
    with open(os.path.join(HERE, "graphs", "hh_d%d.json" % d)) as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------------- instances
def make_instance(G, nodes, J, name):
    """Induced subgraph of the graph JSON G on `nodes`, relabelled 0..m-1 in the given (sorted) order; J per edge."""
    nodes = sorted(int(v) for v in nodes)
    loc = {v: k for k, v in enumerate(nodes)}
    edges = [(loc[int(a)], loc[int(b)]) for a, b in G["edges"] if int(a) in loc and int(b) in loc]
    eta = np.array([G["eta"][v] for v in nodes], dtype=int)
    J = np.asarray(J, float)
    assert len(J) == len(edges)
    return dict(n=len(nodes), edges=edges, J=J, eta=eta, n_down=int((eta == -1).sum()), name=name, nodes=nodes)


def ball_nodes(G, center, size=19):
    """First `size` nodes of a breadth-first search of G from `center` (ties: node index)."""
    n = G["n"]
    adj = [[] for _ in range(n)]
    for a, b in G["edges"]:
        adj[int(a)].append(int(b))
        adj[int(b)].append(int(a))
    dist = {center: 0}
    order = [center]
    i = 0
    while i < len(order):
        u = order[i]
        i += 1
        for w in sorted(adj[u]):
            if w not in dist:
                dist[w] = dist[u] + 1
                order.append(w)
    order.sort(key=lambda v: (dist[v], v))
    return order[:size]


def test_instance(Jz, idx):
    G = graph_json(5)
    r = rng_of("B", "test", js(Jz), idx)
    J = r.uniform(JLO, JHI, len(G["edges"]))
    return make_instance(G, range(G["n"]), J, "test_J%s_%d" % (js(Jz), idx))


def train_instance(Jz, idx):
    """Even idx: the distance-3 graph (n = 19). Odd idx: a 19-site breadth-first ball of the distance-5 graph."""
    r = rng_of("B", "train", js(Jz), idx)
    if idx % 2 == 0:
        G = graph_json(3)
        nodes = list(range(G["n"]))
    else:
        G = graph_json(5)
        nodes = ball_nodes(G, int(r.integers(G["n"])), 19)
    base = make_instance(G, nodes, np.ones(sum(1 for a, b in G["edges"] if int(a) in set(nodes) and int(b) in set(nodes))),
                         "train_J%s_%d" % (js(Jz), idx))
    base["J"] = r.uniform(JLO, JHI, len(base["edges"]))
    return base


# --------------------------------------------------------------------------------------------------------- sectors
_SEC = {}


class Sector:
    def __init__(self, n, nd):
        a = np.arange(1 << n, dtype=np.uint64)
        self.cfg = a[np.bitwise_count(a) == nd].astype(np.int64)
        self.n, self.nd, self.dim = n, nd, len(self.cfg)
        self.bits = ((self.cfg[:, None] >> np.arange(n)) & 1).astype(np.int8)
        self.Zc = 1.0 - 2.0 * self.bits


def sector(n, nd):
    k = (n, nd)
    if k not in _SEC:
        if len(_SEC) > 12:
            _SEC.clear()
        _SEC[k] = Sector(n, nd)
    return _SEC[k]


def build_H(sec, edges, J, Jz, h=None):
    diag = np.zeros(sec.dim)
    R, C, V = [], [], []
    b = sec.bits
    for (i, j), x in zip(edges, J):
        anti = b[:, i] != b[:, j]
        diag += 0.25 * Jz * x * np.where(anti, -1.0, 1.0)
        src = np.nonzero(anti)[0]
        tgt = np.searchsorted(sec.cfg, sec.cfg[src] ^ ((1 << i) | (1 << j)))
        R.append(src)
        C.append(tgt)
        V.append(np.full(len(src), 0.5 * x))
    if h is not None:
        diag = diag + sec.Zc @ np.asarray(h, float)
    if R:
        A = sparse.csr_matrix((np.concatenate(V), (np.concatenate(R), np.concatenate(C))), shape=(sec.dim, sec.dim))
    else:
        A = sparse.csr_matrix((sec.dim, sec.dim))
    return (A + sparse.diags(diag)).tocsr()


def ground(H, tol=1e-9):
    D = H.shape[0]
    if D <= 700:
        w, V = np.linalg.eigh(H.toarray())
        return float(w[0]), V[:, 0]
    v0 = np.random.default_rng(12345).standard_normal(D)
    w, V = eigsh(H, k=1, which="SA", tol=tol, v0=v0, ncv=min(D - 1, 32))
    return float(w[0]), V[:, 0]


def labels_of(sec, edges, p):
    """<Z_i>, <Z_i Z_j> on edges for probabilities p over the (full-sector) configurations."""
    Z = p @ sec.Zc
    C = np.array([p @ (sec.Zc[:, i] * sec.Zc[:, j]) for i, j in edges]) if len(edges) else np.zeros(0)
    return Z, C


def bond_energies(sec, edges, J, Jz, psi, C):
    e = np.zeros(len(edges))
    for k, ((i, j), x) in enumerate(zip(edges, J)):
        src = np.nonzero(sec.bits[:, i] != sec.bits[:, j])[0]
        tgt = np.searchsorted(sec.cfg, sec.cfg[src] ^ ((1 << i) | (1 << j)))
        e[k] = 0.25 * Jz * x * C[k] + 0.5 * x * float(psi[src] @ psi[tgt])
    return e


def solve_exact(inst, Jz):
    sec = sector(inst["n"], inst["n_down"])
    H = build_H(sec, inst["edges"], inst["J"], Jz)
    E0, psi = ground(H)
    Z, C = labels_of(sec, inst["edges"], psi * psi)
    return dict(sec=sec, H=H, E0=E0, psi=psi, Z=Z, C=C, e=bond_energies(sec, inst["edges"], inst["J"], Jz, psi, C))


def sub_labels(sec, edges, B, x):
    """Labels of a vector x on the sector indices B."""
    p = x * x
    p = p / p.sum()
    Zc = sec.Zc[B]
    return p @ Zc, np.array([p @ (Zc[:, i] * Zc[:, j]) for i, j in edges])


def sub_ground(H, B):
    Hb = H[B][:, B]
    if len(B) <= 700:
        w, V = np.linalg.eigh(Hb.toarray())
        return float(w[0]), V[:, 0]
    v0 = np.random.default_rng(777).standard_normal(len(B))
    w, V = eigsh(Hb, k=1, which="SA", tol=1e-8, v0=v0, ncv=min(len(B) - 1, 32))
    return float(w[0]), V[:, 0]


def topD_levels(ex, inst, win, nlev=40):
    """Truncation to the D most probable configurations of the exact ground state, as bias_law/code/n19b.py, on a grid of
    nlev values of D. Levels with energy error per site in win = (lo, hi) are returned."""
    sec, H, psi, E0, n = ex["sec"], ex["H"], ex["psi"], ex["E0"], inst["n"]
    order = np.argsort(-psi * psi, kind="stable")
    Ds = sorted(set(int(x) for x in np.round(np.logspace(0.7, np.log10(sec.dim * 0.9), nlev))))
    out = []
    for D in Ds:
        B = np.sort(order[:D])
        E, x = sub_ground(H, B)
        de = (E - E0) / n
        if de < win[0]:
            break
        if de <= win[1]:
            Z, C = sub_labels(sec, inst["edges"], B, x)
            out.append(dict(D=D, de=de, Z=Z.tolist(), C=C.tolist()))
    return out


SGRID = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096]


def krylov_levels(ex, inst, Jz, dt, win, rng, p_flip=0.01):
    """Same first stage at n = 19: exact e^{-iHk dt}|Neel>, k = 1..K, S shots per circuit (nested), flips p_flip,
    random-flip recovery, Rayleigh-Ritz. Levels with energy error per site in win are returned."""
    sec, H, E0, n, nd = ex["sec"], ex["H"], ex["E0"], inst["n"], inst["n_down"]
    neel = 0
    for i in range(n):
        if inst["eta"][i] == -1:
            neel |= 1 << i
    v = np.zeros(sec.dim, complex)
    v[int(np.searchsorted(sec.cfg, neel))] = 1.0
    A = (-1j * dt) * H
    Smax = SGRID[-1]
    shots = []
    for _ in range(K):
        v = expm_multiply(A, v)
        p = np.abs(v) ** 2
        p = p / p.sum()
        idx = rng.choice(sec.dim, size=Smax, p=p)
        conf = sec.cfg[idx].astype(np.uint64).reshape(-1, 1)
        shots.append(emu2.add_noise(conf, n, p_flip, rng))
    out = []
    for S in SGRID:
        raw = np.concatenate([s[:S] for s in shots])
        Bu, _ = emu2.unique_rows(raw)
        rec = emu2.recover(Bu, n, nd, rng)
        cs, _ = emu2.unique_rows(rec)
        B = np.searchsorted(sec.cfg, cs[:, 0].astype(np.int64))
        B.sort()
        E, x = sub_ground(H, B)
        de = (E - E0) / n
        if de < win[0]:
            break
        if de <= win[1]:
            Z, C = sub_labels(sec, inst["edges"], B, x)
            out.append(dict(S=S, D=int(len(B)), de=de, Z=Z.tolist(), C=C.tolist()))
    return out


# --------------------------------------------------------------------------------------------------------- patches
def adjacency(inst):
    adj = [[] for _ in range(inst["n"])]
    for (i, j), x in zip(inst["edges"], inst["J"]):
        adj[i].append((j, float(x)))
        adj[j].append((i, float(x)))
    return adj


def patch_nodes(inst, adj, seeds, size):
    """Cluster around `seeds`: nodes by graph distance; inside the last, partial shell the node most strongly coupled
    to the cluster goes first (ties: index)."""
    n = inst["n"]
    if n <= size:
        return list(range(n))
    dist = {s: 0 for s in seeds}
    frontier = list(seeds)
    while frontier:
        nxt = []
        for u in frontier:
            for w, _ in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        frontier = nxt
    S = set(seeds)
    d = 1
    while len(S) < size:
        shell = [v for v in range(n) if dist.get(v) == d]
        if len(S) + len(shell) <= size:
            S.update(shell)
            d += 1
            continue
        shell = set(shell)
        while len(S) < size:
            def strength(v):
                return sum(x for w, x in adj[v] if w in S)
            best = sorted(shell, key=lambda v: (-strength(v), v))[0]
            S.add(best)
            shell.remove(best)
    return sorted(S)


def solve_cluster(inst, adj, nodes, Jz, m=None):
    """Ground state of the cluster, in the Neel sector of the cluster. m: <Z_j> of the outside sites (mean-field
    embedding of the cut bonds, (Jz J_e / 4) Z_i m_j), or None (open boundary)."""
    loc = {v: k for k, v in enumerate(nodes)}
    ed, Jc = [], []
    for (i, j), x in zip(inst["edges"], inst["J"]):
        if i in loc and j in loc:
            ed.append((loc[i], loc[j]))
            Jc.append(x)
    h = None
    if m is not None:
        h = np.zeros(len(nodes))
        for v in nodes:
            for w, x in adj[v]:
                if w not in loc:
                    h[loc[v]] += 0.25 * Jz * x * m[w]
    nd = int(sum(inst["eta"][v] == -1 for v in nodes))
    sec = sector(len(nodes), nd)
    H = build_H(sec, ed, Jc, Jz, h)
    E, psi = ground(H)
    return sec, psi, loc, ed, Jc


def patch_estimates(inst, Jz, size, passes=2):
    """Open-boundary and mean-field-embedded estimates of every Z_i and every bond's ZZ and energy."""
    adj = adjacency(inst)
    n = inst["n"]
    site_nodes = [patch_nodes(inst, adj, [i], size) for i in range(n)]
    bond_nodes = [patch_nodes(inst, adj, [i, j], size) for i, j in inst["edges"]]

    def sites(m):
        Z = np.zeros(n)
        for i in range(n):
            sec, psi, loc, ed, Jc = solve_cluster(inst, adj, site_nodes[i], Jz, m)
            Z[i] = (psi * psi) @ sec.Zc[:, loc[i]]
        return Z

    def bonds(m):
        C = np.zeros(len(inst["edges"]))
        e = np.zeros(len(inst["edges"]))
        for b, (i, j) in enumerate(inst["edges"]):
            sec, psi, loc, ed, Jc = solve_cluster(inst, adj, bond_nodes[b], Jz, m)
            p = psi * psi
            C[b] = p @ (sec.Zc[:, loc[i]] * sec.Zc[:, loc[j]])
            e[b] = bond_energies(sec, [(loc[i], loc[j])], [inst["J"][b]], Jz, psi, [C[b]])[0]
        return C, e
    Zo = sites(None)
    Co, eo = bonds(None)
    m = Zo
    hist = []
    for _ in range(passes):
        Zn = sites(m)
        hist.append(float(np.max(np.abs(Zn - m))))
        m = Zn
    Ce, ee = bonds(m)
    return dict(size=size, Z_open=Zo.tolist(), C_open=Co.tolist(), e_open=eo.tolist(), Z_emb=m.tolist(), C_emb=Ce.tolist(),
                e_emb=ee.tolist(), emb_change=hist)


# -------------------------------------------------------------------------------------------------- local features
def _others(adj, j, excl):
    return sorted((x for v, x in adj[j] if v != excl), reverse=True)


def site_features(inst):
    """Local couplings within radius 2 of each site (edges with both ends at graph distance <= 2). 23 columns."""
    adj = adjacency(inst)
    F = []
    for i in range(inst["n"]):
        nb = sorted(adj[i], key=lambda t: (-t[1], t[0]))
        d = len(nb)
        row = [float(d == 1), float(d == 2), float(d == 3), float(inst["eta"][i])]
        s2 = []
        for k in range(3):
            if k < d:
                j, x = nb[k]
                o = _others(adj, j, i)
                s2 += o
                row += [x, o[0] if len(o) > 0 else 0.0, o[1] if len(o) > 1 else 0.0, float(len(o))]
            else:
                row += [0.0, 0.0, 0.0, 0.0]
        s1 = [x for _, x in nb]
        row += [sum(s1), sum(x * x for x in s1), sum(s2), sum(x * x for x in s2), float(len(s2)), max(s2 or [0.0]),
                min(s2 or [0.0])]
        F.append(row)
    return np.array(F)


def bond_features(inst):
    """Local couplings within radius 2 of each bond (the bond, the edges touching it, the edges touching those). 23 columns."""
    adj = adjacency(inst)
    F = []
    for (a, b), x in zip(inst["edges"], inst["J"]):
        i, j = a, b
        ka = (len(adj[a]), sum(y for _, y in adj[a]))
        kb = (len(adj[b]), sum(y for _, y in adj[b]))
        if kb > ka:
            i, j = b, a
        row = [float(x), float(len(adj[i])), float(len(adj[j])), float(inst["eta"][i])]
        s1, s2 = [], []
        for u, excl in ((i, j), (j, i)):
            nb = sorted(((v, y) for v, y in adj[u] if v != excl), key=lambda t: (-t[1], t[0]))
            for k in range(2):
                if k < len(nb):
                    v, y = nb[k]
                    o = _others(adj, v, u)
                    s1.append(y)
                    s2 += o
                    row += [y, sum(o), float(len(o))]
                else:
                    row += [0.0, 0.0, 0.0]
        row += [sum(s1), sum(y * y for y in s1), sum(s2), sum(y * y for y in s2), float(len(s2)), max(s2 or [0.0]),
                min(s2 or [0.0])]
        F.append(row)
    return np.array(F)


# ------------------------------------------------------------------------------- subspace with disordered couplings
class SubHd(emu2.SubH):
    """emu2.SubH with a coupling J_e per edge of g['edges'] (order of the graph JSON)."""

    def __init__(self, cs, g, Jz, J):
        D = len(cs)
        rows, cols, vals = [], [], []
        diag = np.zeros(D)
        for (i, j), x in zip(g["edges"], J):
            anti = (emu2.bit(cs.B, i) ^ emu2.bit(cs.B, j)).astype(bool)
            diag += 0.25 * Jz * x * np.where(anti, -1.0, 1.0)
            idx = np.nonzero(anti)[0]
            Q = cs.B[idx] ^ emu2.mask(g["n"], (i, j))[None, :]
            pos, ok = cs.lookup(Q)
            rows.append(pos[ok].astype(np.int32))
            cols.append(idx[ok].astype(np.int32))
            vals.append(np.full(int(ok.sum()), 0.5 * float(x)))
        r = np.concatenate(rows)
        c = np.concatenate(cols)
        v = np.concatenate(vals)
        order = np.argsort(r, kind="stable")
        indptr = np.zeros(D + 1, dtype=np.int64)
        np.cumsum(np.bincount(r, minlength=D), out=indptr[1:])
        if indptr[-1] < 2 ** 31:
            indptr = indptr.astype(np.int32)
        self.A = sparse.csr_matrix((v[order], c[order].astype(np.int32), indptr), shape=(D, D))
        self.diag = diag
        self.D = D
        self.nnz = int(self.A.nnz + D)


# ---------------------------------------------------------------------------------- exact arithmetic on a subspace
def round_vector(a, bits=44):
    """Float vector -> Python integers, a_int = round(a * 2^bits / max|a|)."""
    s = float(2 ** bits) / float(np.max(np.abs(a)))
    return np.array([int(x) for x in np.rint(np.asarray(a, float) * s)], dtype=object)


def exact_rq(cs, g, Jz, a):
    """Exact Rayleigh quotient and labels of the integer vector a on the configuration set cs (uniform model, one word
    per configuration). Every configuration must lie in the Neel sector. Returns Fractions."""
    B = cs.B
    assert (emu2.popcount(B) == g["n_down"]).all(), "state not in the sector"
    a = np.asarray(a, dtype=object)
    w = a * a
    den = int(w.sum())
    zz = 0
    off = 0
    for (i, j) in g["edges"]:
        anti = (emu2.bit(B, i) ^ emu2.bit(B, j)).astype(bool)
        zz += int(w[~anti].sum()) - int(w[anti].sum())
        idx = np.nonzero(anti)[0]
        Q = B[idx] ^ emu2.mask(g["n"], (i, j))[None, :]
        pos, ok = cs.lookup(Q)
        off += int((a[idx[ok]] * a[pos[ok]]).sum())
    E = Fraction(Jz) / 4 * Fraction(zz, den) + Fraction(off, 2 * den)
    st = np.zeros(len(B), dtype=np.int64)
    for i in range(g["n"]):
        st += int(g["eta"][i]) * (1 - 2 * emu2.bit(B, i).astype(np.int64))
    sm = int((w * st.astype(object)).sum())
    return dict(E=E, m_s=Fraction(sm, g["n"] * den), Czz_bar=Fraction(zz, len(g["edges"]) * den), den_bits=den.bit_length())


# --------------------------------------------------------------------------------- intervals from exact lower bounds
def load_certs(path):
    with open(path) as f:
        return json.load(f)


def side_bound(E, certs, kind, Jz, sigma, S):
    """min over the verified certificates of (E - E_LB)/(lam S): a theorem for every in-sector state at energy <= E."""
    best = None
    for c in certs:
        if c["kind"] != kind or Fraction(c["Jz"]) != Fraction(Jz) or int(c["sigma"]) != sigma:
            continue
        u = (Fraction(E) - Fraction(c["E_LB_exact"])) / (Fraction(c["lam"]) * S)
        if best is None or u < best[0]:
            best = (u, c)
    return best


def interval(E, certs, kind, Jz, S):
    """Two-sided interval of the label O (kind m_s or Czz_bar), clipped to the trivial range [-1, 1]."""
    up = side_bound(E, certs, kind, Jz, +1, S)
    dn = side_bound(E, certs, kind, Jz, -1, S)
    hi = min(up[0], Fraction(1))
    lo = max(-dn[0], Fraction(-1))
    return lo, hi, up[1], dn[1]


def tol_of(lo, hi, frac=Fraction(6, 100)):
    """tau = 0.06 x the smallest |O| on the interval (the lower end of |O|): no reference to the ground state."""
    m = Fraction(0) if lo <= 0 <= hi else min(abs(lo), abs(hi))
    return frac * m


def threshold(certs, kind, Jz, S, E_lo, E_hi, it=60):
    """Largest energy with interval width <= tau, by bisection (E_lo must satisfy it)."""
    def ok(E):
        lo, hi, _, _ = interval(E, certs, kind, Jz, S)
        return (hi - lo) <= tol_of(lo, hi)
    a, b = Fraction(E_lo), Fraction(E_hi)
    if not ok(a):
        return None
    for _ in range(it):
        c = (a + b) / 2
        if ok(c):
            a = c
        else:
            b = c
    return a
