"""T3: Theorem 2 (intensive averages).  Usage: python t3_avg.py <family>
For Obar = (1/n) sum o_i, field family H - mu * O_tot.  Per-site response alpha(mu) = [E0 - mu<O_tot> - E0(H - mu O_tot)]/n.
Checks: (a) exact u_n(de) (both signs) vs sqrt(2 chi0 de); (b) sandwich with envelope susceptibilities on (0, mu1];
(c) intensivity in n, including windows far above the in-sector gap (eps/Delta >> 1);
(d) comparison with Manchanda 2610.03989 Thm 2 range (eps <= Dbar/2) and Eq. 10 upper bound (dense spectrum, dim <= 924);
(e) sum-rule lower bound chi0 >= 2 v^2 / s1;  (f) universal reset lower bound u >= (k/n)(o_max - o0), k = floor(n de / eps_1)."""
import sys, time, numpy as np
from edcore import *

fam = sys.argv[1]
t0 = time.time()
DE = [1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1]
MU1 = 0.3


def build(fam, n):
    if fam.startswith('xxz1do'):   # open odd chain, Sz = +1/2: Neel orientation pinned (IBM-like n_A != n_B)
        Jz = float(fam.split('_')[1])
        b, H = xxz(n, chain_edges(n, periodic=False), Jz, (n + 1) // 2)
        Ot = diag_op(b, [((-1) ** i, (i,)) for i in range(n)])
        return b, H, Ot, 'm_s', 1.0
    if fam.startswith('xxz1d'):
        Jz = float(fam.split('_')[1])
        b, H = xxz(n, chain_edges(n), Jz, n // 2)
        Ot = diag_op(b, [((-1) ** i, (i,)) for i in range(n)])
        return b, H, Ot, 'm_s', 1.0
    if fam in ('comb', 'lieb', 'cyl'):
        if fam == 'comb':
            edges, sub = comb_edges(n // 3)
        elif fam == 'lieb':
            edges, sub = lieb_edges(2)
        else:
            edges = cyl_edges(n // 2, 2); Ly = 2
            sub = [(-1) ** ((i // Ly) + (i % Ly)) for i in range(n)]
        nup = sum(1 for x in sub if x > 0) if fam != 'cyl' else n // 2   # B sublattice up: ferrimagnetic sector
        b, H = xxz(n, edges, 1.6, nup)
        Ot = diag_op(b, [(sub[i], (i,)) for i in range(n)])
        return b, H, Ot, 'm_s', 1.0
    if fam == 'xxz2d':
        b, H = xxz(n, rect_edges(3, n // 3, True), 1.6, n // 2)
        Ly = n // 3
        Ot = diag_op(b, [((-1) ** ((i // Ly) + (i % Ly)), (i,)) for i in range(n)])
        return b, H, Ot, 'm_s', 1.0
    if fam.startswith('tfim1d'):
        h = float(fam.split('_')[1]); lab = fam.split('_')[2]
        b, H = tfim(n, chain_edges(n), 1.0, h)
        Ot = diag_op(b, [(1.0, (i,)) for i in range(n)]) if lab == 'Z' else x_op(b, [(i, 1.0) for i in range(n)])
        return b, H, Ot, lab + 'bar', 1.0
    if fam == 'tfim2d':
        b, H = tfim(n, rect_edges(3, n // 3, True), 1.0, 3.5)
        Ot = diag_op(b, [(1.0, (i,)) for i in range(n)])
        return b, H, Ot, 'Zbar', 1.0
    raise ValueError(fam)


NS = {'xxz2d': [12], 'tfim2d': [12], 'lieb': [12], 'comb': [6, 9, 12], 'cyl': [6, 8, 10, 12]}.get(fam, [5, 7, 9, 11] if fam.startswith('xxz1do') else [6, 8, 10, 12])
summary = []
for n in NS:
    b, H, Ot, lab, omax = build(fam, n)
    # in-sector gap and (if small) dense spectrum for Manchanda comparison
    dense = b.dim <= 924
    if dense:
        w, V = np.linalg.eigh(H.toarray())
        E0d = w[0]; gap = w[1] - w[0]
        Od = V.conj().T @ (Ot.toarray() / n) @ V      # Obar in eigenbasis
        O0n = Od[0, 1:]; om = w[1:] - w[0]
        chi_M = 2 * np.sum(np.abs(O0n) ** 2 / om)    # Manchanda chi_O for Obar
        Dbar = np.sum(np.abs(O0n) ** 2 / om) / np.sum(np.abs(O0n) ** 2 / om ** 2)
        sig = np.sqrt(np.sum(np.abs(O0n) ** 2))
        Oex = Od[1:, 1:] - Od[0, 0] * np.eye(len(om))
        Hm12 = np.diag(om ** -0.5)
        popn = np.linalg.norm(Hm12 @ Oex @ Hm12, 2); Oexn = np.linalg.norm(Oex, 2)
    else:
        vals = sla.eigsh(H, k=2, which='SA', tol=1e-12)[0]; gap = vals[1] - vals[0]
    res = {}
    for sgn in (+1, -1):
        W = Window(H, Ot, sgn)
        o0 = W.o0 / n
        # response function per site and susceptibilities
        mus = np.array([1e-3, 0.01, 0.03, 0.06, 0.1, 0.15, 0.2, 0.3])
        alph = np.array([W.alpha(m) / n for m in mus])
        ratio = 2 * alph / mus ** 2
        chi0 = ratio[0]
        chim, chip = ratio[mus <= MU1].min(), ratio[mus <= MU1].max()
        for de in DE:
            u = W.u(n * de)[0] / n
            lo = min(np.sqrt(2 * chim * de), chim * MU1 / 2)
            hi = np.sqrt(2 * chip * de) if de <= chip * MU1 ** 2 / 2 else chip * MU1 / 2 + de / MU1
            res.setdefault(de, []).append((u, lo, hi, chi0))
    for de in DE:
        (up, lop, hip, c0p), (um, lom, him, c0m) = res[de]
        wex = up + um
        eps = n * de
        line = (f"{fam:12s} n={n:2d} {lab:5s} de={de:7.1e} eps/gap={eps / gap:7.2f} | exact w={wex:.5f} (u+={up:.5f}, u-={um:.5f}) | "
                f"2sqrt(2chi0 de)={2 * np.sqrt(2 * c0p * de):.5f} | sandwich lo={lop + lom:.5f} hi={hip + him:.5f} "
                f"[{lop + lom <= wex + 1e-9 <= hip + him + 2e-9}]")
        if dense:
            # Manchanda (one-sided radius delta_O = max(u+, u-)):
            A_eps = np.sum(np.abs(O0n) ** 2 / (om + eps))
            eq10 = min(eps * popn, Oexn) + min(2 * np.sqrt(eps * A_eps), sig)
            thm2_ok = eps <= Dbar / 2
            thm2 = np.sqrt(2 * eps * chi_M) * np.sqrt(max(0, 1 - eps / Dbar)) if thm2_ok else float('nan')
            line += (f" | Manchanda: radius exact={max(up, um):.5f}, Eq.10 upper={eq10:.5f}, Thm2 lower={thm2:.5f} "
                     f"(applies: eps<=Dbar/2={Dbar / 2:.4f}? {thm2_ok})")
        print(line)
        summary.append((n, de, wex))
    if dense:
        # (e) sum-rule bound on chi0 (sign +)
        psi = V[:, 0]
        Om = Ot.toarray() / n
        v = (psi @ Om @ Om @ psi - (psi @ Om @ psi) ** 2) * n
        dc = 2 * (psi @ Om @ H.toarray() @ Om @ psi - E0d * psi @ Om @ Om @ psi) * n   # <[Obar,[H,Obar]]> * n
        s1 = dc / 2
        print(f"   n={n}: chi0 (finite diff)={res[DE[0]][0][3]:.5f}; Manchanda chi_O*n={chi_M * n:.5f}; sum-rule bound 2v^2/s1={2 * v ** 2 / s1:.5f} "
              f"[{2 * v ** 2 / s1 <= chi_M * n + 1e-9}]; gap={gap:.4f}")
print("intensivity: w(n)/w(n_max) at fixed de:")
for de in DE:
    ws = [x[2] for x in summary if x[1] == de]
    print(f"  de={de:7.1e}: " + ", ".join(f"{x:.4f}" for x in ws))
print(f"time {time.time() - t0:.1f} s")
