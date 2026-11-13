"""T6: Theorem 2(c) ingredient: chi_n(mu) = -f_n''(mu) <= 2 Var_mu(n Obar) / (n Delta_mu), and the sum-rule lower bound
chi_n(mu) >= 2 v^2/s1 (v = Var/n, s1 = <[O,[H,O]]>/(2n)), along the field family mu in [0, 0.3]. Dense ED (dim <= 495)."""
import numpy as np
from edcore import *
for name in ('TFIM1D h=1.5 n=8 Zbar', 'comb ferrimagnet n=12 m_s', 'XXZ open odd Jz=4 n=11 m_s'):
    if name.startswith('TFIM'):
        n = 8; b, H = tfim(n, chain_edges(n), 1.0, 1.5); Ot = diag_op(b, [(1.0, (i,)) for i in range(n)])
    elif name.startswith('comb'):
        n = 12; edges, sub = comb_edges(4); b, H = xxz(n, edges, 1.6, 8); Ot = diag_op(b, [(sub[i], (i,)) for i in range(n)])
    else:
        n = 11; b, H = xxz(n, chain_edges(n, periodic=False), 4.0, 6); Ot = diag_op(b, [((-1) ** i, (i,)) for i in range(n)])
    Hd, Od = H.toarray(), Ot.toarray()
    worst_up, worst_lo = -1e9, -1e9
    for mu in np.linspace(0, 0.3, 7):
        def f(m):
            return np.linalg.eigvalsh(Hd - m * Od)[0] / n
        d = 1e-3
        chi = -(f(mu + d) - 2 * f(mu) + f(mu - d)) / d ** 2
        w, V = np.linalg.eigh(Hd - mu * Od)
        g = V[:, 0]; gap = w[1] - w[0]
        var = g @ Od @ Od @ g - (g @ Od @ g) ** 2
        Hm = Hd - mu * Od
        dc = 2 * (g @ Od @ Hm @ Od @ g - w[0] * (g @ Od @ Od @ g))
        up = 2 * var / (n * gap); lo = 2 * (var / n) ** 2 / (dc / (2 * n))
        worst_up = max(worst_up, chi - up); worst_lo = max(worst_lo, lo - chi)
        print(f"{name:28s} mu={mu:.2f}: chi={chi:.4f}  upper 2Var/(n gap)={up:.4f}  lower 2v^2/s1={lo:.4f}  gap={gap:.3f}")
    print(f"  max(chi - upper) = {worst_up:+.2e} (<= ~1e-5 expected); max(lower - chi) = {worst_lo:+.2e} (<= ~1e-5 expected)")
