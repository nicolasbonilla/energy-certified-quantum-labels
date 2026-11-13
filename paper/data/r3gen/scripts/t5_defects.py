"""T5: (a) cheap-defect mechanism for a pinned order parameter (XXZ open odd chain, Jz=4, Sz=+1/2):
the '-' side u_-(eps) ramps ~linearly in eps (domain-wall mixture) and is ~n-independent as a function of TOTAL eps,
i.e. local-like; contrast with the comb ferrimagnet (extensive pinning) where u(eps) at fixed eps shrinks ~ 1/sqrt(n).
(b) universal linear lower bound for averages from k well-separated single-site resets (TFIM1D h=1.5, Zbar):
energy of the k-site reset = k * eps_1 exactly (disjoint supports), so u(n de) >= (k/n)(1 - o0), k = floor(n de/eps_1)."""
import time, numpy as np
from edcore import *

t0 = time.time()
print("(a) u(eps) as a function of TOTAL eps")
for fam in ('open-odd XXZ Jz=4 (pinned, cheap wall)', 'comb ferrimagnet Jz=1.6 (extensive pinning)'):
    print("  " + fam)
    ns = (5, 7, 9, 11) if fam.startswith('open') else (6, 9, 12)
    for eps in (0.5, 1.0, 2.0, 4.0):
        vals = []
        for n in ns:
            if fam.startswith('open'):
                b, H = xxz(n, chain_edges(n, periodic=False), 4.0, (n + 1) // 2)
                sub = [(-1) ** i for i in range(n)]
            else:
                edges, sub = comb_edges(n // 3)
                b, H = xxz(n, edges, 1.6, sum(1 for x in sub if x > 0))
            Ot = diag_op(b, [(sub[i], (i,)) for i in range(n)])
            W = Window(H, Ot, -1)
            vals.append(W.u(eps)[0] / n)
        print(f"    eps={eps:4.1f}: u_-(n) = " + ", ".join(f"{v:.4f}" for v in vals) + f"   (n={ns})")
print("(b) k well-separated resets, TFIM1D h=1.5 n=12, Zbar")
n = 12
b, H = tfim(n, chain_edges(n), 1.0, 1.5)
Ot = diag_op(b, [(1.0, (i,)) for i in range(n)])
W = Window(H, Ot, +1)
psi = W.psi0.astype(complex)
idx = np.arange(2 ** n)
e1 = None
for k in range(1, 7):
    S = list(range(0, 2 * k, 2))
    v = psi.copy()
    # reset each site in S to up: rho -> sum over measured configs; implement by successive single-site resets on vectors
    vecs = [v]
    for i in S:
        new = []
        for w in vecs:
            up = np.zeros_like(w); dn = np.zeros_like(w)
            m1 = ((idx >> i) & 1) == 1
            up[idx[m1]] = w[m1]                     # component with site i up stays
            dn[idx[~m1] | (1 << i)] = w[~m1]        # component with site i down moved to up
            new += [up, dn]
        vecs = new
    E = sum(np.real(np.vdot(w, H @ w)) for w in vecs) - W.E0
    o = sum(np.real(np.vdot(w, Ot @ w)) for w in vecs) / n - W.o0 / n
    if k == 1:
        e1 = E
    u = W.u(E)[0] / n
    print(f"  k={k}: reset energy={E:.6f}  k*eps_1={k * e1:.6f}  [additive: {abs(E - k * e1) < 1e-9}]  shift={o:.4f} = k/n*(1-o0)={k / n * (1 - W.o0 / n):.4f}; exact u={u:.4f} [>= shift: {u >= o - 1e-12}]")
print(f"time {time.time() - t0:.1f} s")
