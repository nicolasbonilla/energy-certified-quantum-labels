"""T1: Lemma 0 (Lagrange duality) is exact: primal witness value == dual value at lam*,
and no lam on a grid gives a dual value below the primal (weak duality)."""
import time, numpy as np
from edcore import *

t0 = time.time()
cases = []
n = 8
b, H = tfim(n, chain_edges(n), J=1.0, h=1.5)
cases.append(('TFIM1D n=8 h=1.5', H, x_op(b, [(0, 1.0)]), 'X_0'))
cases.append(('TFIM1D n=8 h=1.5', H, diag_op(b, [(1.0 / n, (i,)) for i in range(n)]), 'Zbar'))
n = 10
b, H = xxz(n, chain_edges(n), 1.6, n // 2)
cases.append(('XXZ1D n=10 Jz=1.6 Sz=0', H, diag_op(b, [(1.0, (0,))]), 'Z_0'))
cases.append(('XXZ1D n=10 Jz=1.6 Sz=0', H, diag_op(b, [((-1) ** i / n, (i,)) for i in range(n)]), 'm_s'))
b, H = tfim(12, rect_edges(3, 4, True), J=1.0, h=3.5)
cases.append(('TFIM2D 3x4 h=3.5', H, diag_op(b, [(1.0 / 12, (i,)) for i in range(12)]), 'Zbar'))
b, H = xxz(12, rect_edges(3, 4, True), 1.6, 6)
cases.append(('XXZ2D 3x4 Jz=1.6 Sz=0', H, diag_op(b, [((-1) ** ((i // 4) + (i % 4)) / 12, (i,)) for i in range(12)]), 'm_s'))

lams = np.logspace(-3, np.log10(64), 30)
worst_gap, worst_weak = 0.0, 0.0
for name, H, O, lab in cases:
    for sgn in (+1, -1):
        W = Window(H, O, sgn)
        for eps in (0.01, 0.1, 0.5, 2.0):
            u, ls, flag = W.u(eps)
            # primal feasibility of the witness at lam*: energy <= E0+eps
            # primal: mixture of GS(lam_a), GS(lam_b) is feasible (energy <= E0+eps); dual at lam_a, lam_b bound from above
            dual_star = min(W.dual_at(eps, W.last['lam_a']), W.dual_at(eps, W.last['lam_b'])) if flag == 'interior' else np.nan
            dual_grid = W.dual(eps, lams)
            gap = abs(dual_star - u) if flag == 'interior' else 0.0
            weak = u - dual_grid  # must be <= 0 (up to rounding)
            worst_gap = max(worst_gap, gap); worst_weak = max(worst_weak, weak)
            print(f"{name:26s} {lab:5s} sgn={sgn:+d} eps={eps:5.2f} u={u:.6f} dual(lam*)-u={dual_star - u if flag=='interior' else float('nan'):+.1e} "
                  f"gridDual-u={dual_grid - u:+.2e} lam*={ls:.4g} {flag}")
print(f"max |dual(lam*) - primal| = {worst_gap:.2e};  max (primal - grid dual) = {worst_weak:.2e} (must be <= ~1e-10)")
print(f"time {time.time() - t0:.1f} s")
