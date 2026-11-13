# Exploratory analysis, no prior declaration: does the bias-vs-energy-per-site curve transfer across sizes in other models?
# Truncation = top-D configurations of the exact ground state, then Rayleigh-Ritz (the family that matched at n = 19 -> 57, 115).
# Metrics at matched energy error per site, in tau = 0.06 |o_GS(big)|: raw label error, transfer miss, and the "use the small truth" baseline.
import sys, json, itertools
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
def grid(Lx, Ly):
    idx = lambda x, y: x * Ly + y; E = []
    for x in range(Lx):
        for y in range(Ly):
            if x + 1 < Lx: E.append((idx(x, y), idx(x + 1, y)))
            if y + 1 < Ly: E.append((idx(x, y), idx(x, y + 1)))
    return E
def diag(Lx, Ly):
    idx = lambda x, y: x * Ly + y; E = []
    for x in range(Lx - 1):
        for y in range(Ly):
            if y + 1 < Ly: E.append((idx(x, y), idx(x + 1, y + 1)))
            if y - 1 >= 0: E.append((idx(x, y), idx(x + 1, y - 1)))
    return E
def build(n, terms):           # terms: (i, j, Jxy, Jzz) for 1/4 (Jxy (XX+YY) + Jzz ZZ)
    nd = n // 2
    cfg = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(n), nd)], dtype=np.int64); cfg.sort(); dim = len(cfg)
    bits = ((cfg[:, None] >> np.arange(n)) & 1).astype(np.int8); Zc = (1 - 2 * bits).astype(np.float32)
    d = np.zeros(dim); R, C, V = [], [], []
    for i, j, a, b in terms:
        d += b / 4 * Zc[:, i] * Zc[:, j]
        s = np.nonzero(bits[:, i] != bits[:, j])[0]
        R.append(s); C.append(np.searchsorted(cfg, cfg[s] ^ ((1 << i) | (1 << j)))); V.append(np.full(len(s), a / 2))
    H = sparse.csr_matrix((np.concatenate(V), (np.concatenate(R), np.concatenate(C))), shape=(dim, dim)) + sparse.diags(d)
    return H.tocsr(), Zc
def curve(H, n, label, nD=16):
    w, v = eigsh(H, k=1, which='SA', tol=1e-9); E0 = w[0]; psi = v[:, 0]; o0 = label(psi**2, None)
    order = np.argsort(-psi**2); dim = len(psi); out = []
    for D in sorted(set(int(x) for x in np.round(np.logspace(0.8, np.log10(dim * .7), nD)))):
        B = np.sort(order[:D]); Hb = H[B][:, B]
        if D < 300: ww, vv = np.linalg.eigh(Hb.toarray())
        else: ww, vv = eigsh(Hb, k=1, which='SA', tol=1e-7)
        out.append(((ww[0] - E0) / n, label(vv[:, 0]**2, B) - o0))
    return o0, np.array(sorted(out))
def compare(tag, res, tau_frac=.06):
    names = list(res); big = names[-1]; o0b, cb = res[big]; tau = tau_frac * abs(o0b)
    print(f'{tag}: sizes {names}  truth ' + ' '.join(f'{res[k][0]:.4f}' for k in names))
    x = np.sqrt(np.maximum(cb[:, 0], 0))
    for sm in names[:-1]:
        o0s, cs = res[sm]; xs = np.sqrt(np.maximum(cs[:, 0], 0))
        m = (x >= xs.min()) & (x <= xs.max()) & (np.abs(cb[:, 1]) > .25 * tau)
        if m.sum() == 0: print(f'   {sm}: no overlap'); continue
        pred = np.interp(x[m], xs, cs[:, 1]); raw = np.abs(cb[m, 1]) / tau; miss = np.abs(cb[m, 1] - pred) / tau; base = abs(o0s - o0b) / tau
        print(f'   from {sm:>4s} to {big}: rows {m.sum():2d}  raw mean {raw.mean():6.2f} max {raw.max():6.2f} | corrected mean {miss.mean():5.2f} max {miss.max():5.2f} | small-truth baseline {base:5.2f}')
    sys.stdout.flush()
sizes = [(3, 4), (4, 4), (4, 5)]
def run(tag, mk, lab):
    res = {}
    for Lx, Ly in sizes:
        n = Lx * Ly; H, Zc = build(n, mk(Lx, Ly)); res[str(n)] = curve(H, n, lab(Lx, Ly, Zc)); 
    compare(tag, res)
def czz(Lx, Ly, Zc):
    E = grid(Lx, Ly); P = sum(Zc[:, i] * Zc[:, j] for i, j in E) / len(E)
    return lambda p, B: float(p @ (P if B is None else P[B]))
def m2(Lx, Ly, Zc):
    eta = np.array([(-1) ** (x + y) for x in range(Lx) for y in range(Ly)], np.float32); n = Lx * Ly; P = ((Zc @ eta) / n) ** 2
    return lambda p, B: float(p @ (P if B is None else P[B]))
for Jz in (1.2, 2.0, 4.0):
    mk = lambda Lx, Ly, Jz=Jz: [(i, j, 1., Jz) for i, j in grid(Lx, Ly)]
    run(f'square XXZ Jz={Jz} C_zz', mk, czz); run(f'square XXZ Jz={Jz} m_s^2', mk, m2)
for J2 in (0.3, 0.5):
    mk = lambda Lx, Ly, J2=J2: [(i, j, 1., 1.) for i, j in grid(Lx, Ly)] + [(i, j, J2, J2) for i, j in diag(Lx, Ly)]
    run(f'frustrated J1-J2 Heisenberg J2={J2} C_zz', mk, czz)
for seed in (1, 2, 3):
    def mk(Lx, Ly, seed=seed):
        r = np.random.default_rng(seed * 100 + Lx * Ly); return [(i, j, c, c) for (i, j), c in zip(grid(Lx, Ly), r.uniform(0, 2, 4 * Lx * Ly))]
    run(f'random Heisenberg (Huang-type) seed={seed} C_zz', mk, czz)
