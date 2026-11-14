"""level-theory (R10): exact checks of three proposed statements.

A. Unpinned order (balanced bipartite lattice, sector S^z = 0, spin-flip symmetry F):  with O = sum_i eta_i Z_i,
   sigma^2 = <m_s^2>, phi = O psi0/|O psi0|:   <phi|H - E0|phi> = 8|<K_xy>|/(n^2 sigma^2) <= 4|E|/(n^2 sigma^2),
   and (psi0 + phi)/sqrt2 has m_s = sigma at excess energy half of that  =>  E*_n(c) <= 2|E|/(n^2 sigma^2), c <= sigma.
B. Domain-wall class: a reflection of a region R onto itself that swaps the sublattices is a charge-conserving unitary;
   it reverses the staggered magnetization of R and costs at most the spread of the terms crossing the boundary of R.
C. Local window on a ring: translation invariance pins the ground state's energy per bond, so the weighted block energy
   bounds a local label with a width that does not depend on n (exact diagonalization of the block only).
"""
import itertools, sys, time
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
from scipy.optimize import minimize_scalar

def sector(n, edges, k):
    st = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(n), k)], dtype=np.int64); st.sort()
    bits = ((st[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8); Z = 2 * bits - 1
    zz = np.zeros(len(st)); r = []; c = []
    for a, b in edges:
        zz += Z[:, a] * Z[:, b]
        m = bits[:, a] != bits[:, b]
        r.append(np.nonzero(m)[0]); c.append(np.searchsorted(st, st[m] ^ ((1 << a) | (1 << b))))
    r = np.concatenate(r); c = np.concatenate(c)
    K = sp.csr_matrix((np.full(len(r), 0.5), (r, c)), shape=(len(st), len(st)))
    return st, Z, K, zz / 4.0

def gs(H, k=2):
    if H.shape[0] <= 600:
        w, v = np.linalg.eigh(H.toarray()); return w[:k], v[:, 0]
    w, v = eigsh(H, k=k, which="SA", ncv=max(30, 2 * k + 1), tol=1e-11); o = np.argsort(w); return w[o], v[:, o[0]]

def ring(n): return [(i, (i + 1) % n) for i in range(n)]
def torus(L):
    idx = lambda x, y: (x % L) * L + (y % L)
    return sorted(set(tuple(sorted(e)) for x in range(L) for y in range(L) for e in [(idx(x, y), idx(x + 1, y)), (idx(x, y), idx(x, y + 1))]))
def two_colour(n, edges):
    col = {0: 1}; adj = {i: [] for i in range(n)}
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in col: col[v] = -col[u]; stack.append(v)
    return np.array([col[i] for i in range(n)])

print("=== A. unpinned order: balanced lattices, sector S^z = 0 ===")
print("lattice n Jz | sigma=sqrt<m_s^2> | exact gap E1-E0 | dE(phi) direct | 8|<Kxy>|/(n^2 s^2) | bound 4|E|/(n^2 s^2) | n*dE | "
      "E*(c=sigma) in [dual lower bound, dE/2]")
for name, n, edges in [("ring", 8, ring(8)), ("ring", 12, ring(12)), ("ring", 16, ring(16)), ("ring", 20, ring(20)), ("torus4x4", 16, torus(4))]:
    eta = two_colour(n, edges); st, Z, K, zz = sector(n, edges, n // 2); O = (Z * eta).sum(1).astype(float)
    for Jz in (1.6, 2.5, 4.0):
        H = K + sp.diags(Jz * zz); w, v = gs(H); E0 = w[0]
        s2 = (v ** 2) @ (O / n) ** 2; kxy = v @ (K @ v)
        phi = O * v; phi /= np.linalg.norm(phi); dE = phi @ (H @ phi) - E0
        f1 = 8 * abs(kxy) / (n ** 2 * s2); f2 = 4 * len(edges) / (n ** 2 * s2)
        c = np.sqrt(s2); low = 0.0
        if n <= 16:                              # exact lower bound on E*(c): sup_lambda [lambda n c - alpha(lambda)], any lambda is valid
            for lam in np.geomspace(1e-7, 0.3, 22):
                wl, _ = gs(H - lam * sp.diags(O), k=1); low = max(low, lam * n * c - (E0 - wl[0]))
        print(f"{name:8s} {n:2d} {Jz:3.1f} | {c:.4f} | {w[1]-E0:.3e} | {dE:.5f} | {f1:.5f} | {f2:.5f} | {n*dE:.4f} | "
              f"[{low:.2e}, {dE/2:.5f}]" + ("" if n <= 16 else "  (lower bound not computed)"), flush=True)

print("\n=== B. domain-wall class: open chain with one extra majority site (sector pinned non-extensively) ===")
for n, Jz in [(15, 2.5), (19, 2.5), (19, 4.0)]:
    edges = [(i, i + 1) for i in range(n - 1)]; eta = np.array([1 if i % 2 == 0 else -1 for i in range(n)])
    st, Z, K, zz = sector(n, edges, (n + 1) // 2); H = K + sp.diags(Jz * zz); w, v = gs(H); E0 = w[0]
    ms0 = (v ** 2) @ ((Z * eta).sum(1) / n); bound = Jz / 2 + 0.5
    print(f"n={n} Jz={Jz}: E0={E0:.5f}  m_s(GS)={ms0:.4f}  bound on the cost = spread of one bond = Jz/2 + 1/2 = {bound:.3f}")
    for k in sorted(set([1, 2, (n - 1) // 4, (n - 1) // 2 - 1, (n - 1) // 2])):
        m = 2 * k                                 # region R = sites 0..m-1, reflection i -> m-1-i (swaps sublattices, conserves S^z)
        bits = ((st[:, None] >> np.arange(n)[None, :]) & 1)
        perm = np.arange(n); perm[:m] = np.arange(m)[::-1]
        newst = (bits[:, perm] << np.arange(n)[None, :]).sum(1)
        u = np.zeros_like(v); u[np.searchsorted(st, newst)] = v
        cost = u @ (H @ u) - E0; ms1 = (u ** 2) @ ((Z * eta).sum(1) / n)
        print(f"   |R|={m:2d}: cost={cost:.4f} (<= {bound:.3f}: {cost <= bound + 1e-9})   m_s: {ms0:.4f} -> {ms1:+.4f}  (shift {ms1-ms0:+.4f})")

print("\n=== C. local window on a ring: label C = Z_0 Z_1, block = open segment with weights, exact block diagonalization ===")
def block_ops(L, w, Jz):
    """H_B^w = sum_e w_e h_e on 2^L (no sector), C = Z_a Z_{a+1} at the centre bond"""
    dim = 1 << L; s = np.arange(dim); bits = (s[:, None] >> np.arange(L)[None, :]) & 1; Zb = 2 * bits - 1
    d = np.zeros(dim); r = []; c = []; val = []
    for e in range(L - 1):
        d += w[e] * Jz / 4 * Zb[:, e] * Zb[:, e + 1]
        m = bits[:, e] != bits[:, e + 1]
        r.append(s[m]); c.append(s[m] ^ (3 << e)); val.append(np.full(m.sum(), 0.5 * w[e]))
    Hb = sp.csr_matrix((np.concatenate(val), (np.concatenate(r), np.concatenate(c))), shape=(dim, dim)) + sp.diags(d)
    a = L // 2 - 1
    return Hb, (Zb[:, a] * Zb[:, a + 1]).astype(float)
def e0(Hm):
    if Hm.shape[0] <= 1024: return np.linalg.eigvalsh(Hm.toarray())[0]
    return eigsh(Hm, k=1, which="SA", ncv=24, tol=1e-10)[0][0]
n = 16; edges = ring(n)
for Jz in (2.5, 4.0, 6.0):
    st, Z, K, zz = sector(n, edges, n // 2); H = K + sp.diags(Jz * zz); w, v = gs(H); eb = w[0] / n
    cgs = (v ** 2) @ (Z[:, 0] * Z[:, 1]); tau = 0.06 * abs(cgs)
    print(f"ring n={n} Jz={Jz}: energy per bond e0={eb:.5f}, C_GS=<Z0Z1>={cgs:.4f}, tolerance tau=0.06|C_GS|={tau:.4f}")
    for L in (6, 8, 10, 12):
        for prof in ("flat", "tent", "sin2"):
            x = (np.arange(L - 1) + 1) / L
            wts = {"flat": np.ones(L - 1), "tent": 1 - np.abs(2 * x - 1) * (1 - 1.0 / L), "sin2": np.sin(np.pi * x) ** 2}[prof]
            Hb, C = block_ops(L, wts, Jz); W = wts.sum(); Cd = sp.diags(C); out = []
            for de in (0.0, 0.005, 0.011):
                e = W * (eb + de)                 # de = excess energy per bond of the certified energy
                up = minimize_scalar(lambda t: (e - e0(Hb - np.exp(t) * Cd)) / np.exp(t), bounds=(-6, 4), method="bounded", options={"xatol": 1e-3}).fun
                lo = -minimize_scalar(lambda t: (e - e0(Hb + np.exp(t) * Cd)) / np.exp(t), bounds=(-6, 4), method="bounded", options={"xatol": 1e-3}).fun
                out.append((de, max(lo, -1.0), min(up, 1.0)))
            print(f"   L={L:2d} {prof:4s}: " + "  ".join(f"de={de}: [{lo:+.4f},{up:+.4f}] width={up-lo:.4f} ({(up-lo)/tau:.1f} tau)" for de, lo, up in out), flush=True)
