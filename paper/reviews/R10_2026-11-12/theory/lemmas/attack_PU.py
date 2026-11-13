"""attack_PU.py -- numerical attack of Proposition PU (unpinned order on balanced lattices).

Claim attacked (label O-bar = O/n, O = sum_i eta_i Z_i, sector ground state psi_0 non-degenerate, a symmetry F with
F H F^-1 = H, F O F^-1 = -O that maps the sector to itself):
    <O> = <O^3> = 0,   <phi|H - E0|phi> = D/(2 n^2 sigma^2)  for phi = O psi_0/|O psi_0|,
    E*_n(c) <= D/(4 n^2 sigma^2) [1 - sqrt(1 - c^2/sigma^2)] <= D/(4 n^2 sigma^2) <= 2|E|/(n^2 sigma^2),  0 <= c <= sigma,
with sigma^2 = <O-bar^2>, D = <[O,[H,O]]> = 16 |<K_xy>|.
E*_n(c) is computed exactly through the conjugate function (ed_small.conj_cost): a dual value (lower bound) and the
energy of an explicit state that reaches c (upper bound); the two agree to the digits printed.
A violation would be: bound < dual value.
Run:  python -B attack_PU.py > attack_PU_out.txt
"""
import time
import numpy as np
from ed_small import basis, zvals, build, lowest, conj_cost, ring, ladder, torus

t0 = time.time()
cases = []
for n in (8, 12, 16):
    cases.append((f"ring {n}", n, *ring(n), n // 2, "spin flip"))
for L in (4, 6, 8):
    cases.append((f"ladder 2x{L} periodic", 2 * L, *ladder(L, True), L, "spin flip"))
cases.append(("ladder 2x8 open", 16, *ladder(8, False), 8, "spin flip"))
cases.append(("square 4x4 torus", 16, *torus(4, 4, True), 8, "spin flip"))
cases.append(("square 4x4 open", 16, *torus(4, 4, False), 8, "spin flip"))
for n in (12, 16):
    cases.append((f"ring {n}, sector S^z=1", n, *ring(n), n // 2 + 1, "translation"))
    cases.append((f"ring {n}, sector S^z=2", n, *ring(n), n // 2 + 2, "translation"))

print("PU attack: exact E*_n(c) against the bound.  Columns: c/sigma, E* (dual value), E* (explicit state), bound, bound/E*")
worst = np.inf
nviol = 0
rows_summary = []
for (name, n, E, eta, nup, sym) in cases:
    st = basis(n, nup)
    z = zvals(st, n)
    odiag = np.asarray(eta, float) @ z
    for Jz in (1.0, 2.5, 4.0):
        K, diag = build(st, n, E, Jz)
        w, psi = lowest(K, diag, 2)
        E0, gap = w[0], w[1] - w[0]
        p = psi * psi
        O1 = float(p @ odiag); O2 = float(p @ odiag ** 2); O3 = float(p @ odiag ** 3)
        sig = np.sqrt(O2) / n
        Kxy = float(psi @ (K @ psi))
        D = -16.0 * Kxy
        phi = odiag * psi; phi /= np.linalg.norm(phi)
        etrial = float(phi @ (K @ phi) + np.sum(phi * phi * diag)) - E0
        ident = D / (2 * n * n * sig * sig)
        crude = 2 * len(E) / (n * n * sig * sig)
        print(f"\n{name:26s} Jz={Jz:3.1f} n={n} |E|={len(E)} dim={len(st)} symmetry: {sym}")
        print(f"   E0={E0:.10f} sector gap={gap:.6f} <O>={O1:+.1e} <O^3>={O3:+.1e} sigma={sig:.6f} D={D:.6f} (<= 8|E| = {8*len(E)})")
        print(f"   trial state: <phi|H-E0|phi> = {etrial:.10f}; identity D/(2 n^2 sigma^2) = {ident:.10f}; difference {etrial-ident:+.1e}")
        assert abs(O1) < 1e-7 and abs(O3) < 1e-6 and abs(etrial - ident) < 1e-8 and D <= 8 * len(E) + 1e-9
        for frac in (0.25, 0.5, 0.75, 1.0):
            c = frac * sig
            lo, hi, mu = conj_cost(K, diag, odiag, n, c, +1, psi, E0)
            bound = D / (4 * n * n * sig * sig) * (1 - np.sqrt(max(0.0, 1 - frac * frac)))
            ratio = bound / hi if hi > 0 else np.inf
            ok = bound >= lo - 1e-9
            nviol += (not ok)
            worst = min(worst, ratio)
            print(f"   c/sigma={frac:4.2f}  E*: [{lo:.9f}, {hi:.9f}]  bound={bound:.9f}  bound/E*={ratio:7.3f}  mu*={mu:.6f}  {'ok' if ok else 'VIOLATION'}")
            if frac == 1.0:
                rows_summary.append((name, Jz, n, sig, hi, bound, crude, n * hi, n * bound))

print("\n" + "=" * 100)
print("summary at c = sigma_n:  lattice, Jz, n, sigma_n, E*_n(sigma_n), bound D/(4 n^2 sigma^2), crude 2|E|/(n^2 sigma^2), n E*, n bound")
for r in rows_summary:
    print("  %-26s %3.1f %3d  %.4f  %.6f  %.6f  %.6f  %.4f  %.4f" % r)
print("violations: %d;  smallest bound/E* over all rows: %.4f   (%.1f s)" % (nviol, worst, time.time() - t0))
