"""attack_PD.py -- numerical attack of Proposition PD (domain walls).

Claim attacked: R a region, pi a permutation of the sites of R whose unitary U leaves the sum of the terms supported
inside R invariant. Then for every state rho:  |Tr H U rho U* - Tr H rho| <= kappa_dR  (sum of the spreads of the
terms that cross the boundary of R), U keeps the S^z sector, and if pi exchanges the sublattices inside R the
staggered magnetization of R is reversed, so that
        E*_n(-c_R) <= <U psi_0|H|U psi_0> - E_0 <= kappa_dR,   c_R = (2/n) sum_{i in R} eta_i <Z_i>_0.
Models (order pinned only at a boundary or by the sector; XXZ, H = (1/4) sum (XX + YY + Jz ZZ) + fields):
  (i)   open ladder 2 x L, sector S^z = 0, staggered pinning field h = 1 on the first rung only;
        R = the last l rungs, pi = exchange of the two legs inside R; two leg bonds cross, kappa_dR = 2 kappa_e
  (ii)  open chain, n even, sector S^z = 0, field -h Z_0 on the first site only; R = the last 2k sites,
        pi = reflection of R; one bond crosses, kappa_dR = kappa_e
  (iii) open chain, n odd, sector S^z = 1/2 (orientation fixed by the sector, no field); R = the last 2k sites
kappa_e = spread of one bond term = max((Jz+1)/2, 1).
E*_n(-c_R) is computed exactly through the conjugate function (dual value and explicit state).
Run:  python -B attack_PD.py > attack_PD_out.txt
"""
import time
import numpy as np
from ed_small import basis, zvals, build, lowest, conj_cost, chain, ladder

t0 = time.time()
rng = np.random.default_rng(11)


def apply_perm(states, psi, perm):
    """U|s> = |s'> with the spin of site i moved to site perm[i]"""
    new = np.zeros_like(states)
    for i, pi in enumerate(perm):
        new |= ((states >> i) & 1) << pi
    out = np.zeros_like(psi)
    out[np.searchsorted(states, new)] = psi
    return out


def energy(K, diag, v):
    return float(v @ (K @ v) + np.sum(v * v * diag))


def run(name, n, E, eta, nup, fields, regions, Jz, ncross):
    global nviol, nrand
    st = basis(n, nup)
    z = zvals(st, n)
    eta = np.asarray(eta, float)
    odiag = eta @ z
    K, diag = build(st, n, E, Jz, fields)
    w, psi = lowest(K, diag, 2)
    E0 = w[0]
    p = psi * psi
    zexp = z @ p
    ms0 = float(p @ odiag) / n
    ke = max((Jz + 1) / 2, 1.0)
    kap = ncross * ke
    print(f"\n{name}  Jz={Jz:3.1f}  n={n} dim={len(st)}  E0={E0:.8f} sector gap={w[1]-w[0]:.5f}  m_s(ground)={ms0:+.5f}  kappa_dR={kap:.3f}")
    print("    region                |R|   c_R      m_s after   cost <U psi0|H|U psi0>-E0   E*_n(-c_R) [dual, explicit]     cost/kappa  E*/cost")
    for (rname, R, perm) in regions:
        assert sorted(perm) == list(range(n)) and all(perm[i] == i for i in range(n) if i not in R)
        assert all(eta[perm[i]] == -eta[i] for i in R)                       # exchanges the sublattices inside R
        inside = [(a, b) for a, b in E if a in R and b in R]
        assert sorted((min(perm[a], perm[b]), max(perm[a], perm[b])) for a, b in inside) == sorted(inside)
        assert fields is None or all(fields[i] == 0 for i in R)              # interior terms invariant
        assert sum(1 for a, b in E if (a in R) != (b in R)) == ncross
        u = apply_perm(st, psi, perm)
        cost = energy(K, diag, u) - E0
        ms1 = float((u * u) @ odiag) / n
        cR = 2.0 / n * float(sum(eta[i] * zexp[i] for i in R))
        assert abs((ms0 - ms1) - cR) < 1e-10
        lo, hi, mu = conj_cost(K, diag, odiag, n, ms1, -1, psi, E0)
        ok = (cost <= kap + 1e-9) and (lo <= cost + 1e-8)
        nviol += (not ok)
        print(f"    {rname:20s} {len(R):3d}  {cR:+.5f}  {ms1:+.5f}    {cost:.8f}              [{lo:.8f}, {hi:.8f}]      {cost/kap:.3f}     {hi/cost if cost > 0 else float('nan'):.3f}  {'ok' if ok else 'VIOLATION'}")
        for _ in range(4):                                                   # the inequality for arbitrary states
            v = rng.standard_normal(len(st)); v /= np.linalg.norm(v)
            dv = energy(K, diag, apply_perm(st, v, perm)) - energy(K, diag, v)
            nrand += 1
            if abs(dv) > kap + 1e-9:
                nviol += 1
                print("      VIOLATION for a random state:", dv)
            # a low-energy state different from the ground state: one Lanczos-like step
        v = psi + 0.3 * (rng.standard_normal(len(st)) / np.sqrt(len(st))); v /= np.linalg.norm(v)
        dv = energy(K, diag, apply_perm(st, v, perm)) - energy(K, diag, v)
        nrand += 1
        if abs(dv) > kap + 1e-9:
            nviol += 1
            print("      VIOLATION for a perturbed ground state:", dv)


nviol = 0
nrand = 0
for Jz in (1.0, 2.5, 4.0):
    for L in (4, 6, 8):
        E, eta = ladder(L, False)
        n = 2 * L
        f = np.zeros(n); f[0] = -1.0 * eta[0]; f[1] = -1.0 * eta[1]            # pins Z_i = eta_i on the first rung
        regs = []
        for l in range(1, L):
            R = set(range(2 * (L - l), n))
            perm = list(range(n))
            for x in range(L - l, L):
                perm[2 * x], perm[2 * x + 1] = 2 * x + 1, 2 * x
            regs.append((f"last {l} rung(s)", R, perm))
        run(f"(i) open ladder 2x{L}, field on rung 0", n, E, eta, L, f, regs, Jz, 2)
    for n in (12, 16):
        E, eta = chain(n)
        f = np.zeros(n); f[0] = -1.0
        regs = []
        for k in range(1, n // 2):
            R = set(range(n - 2 * k, n))
            perm = list(range(n))
            for j in range(2 * k):
                perm[n - 2 * k + j] = n - 1 - j
            regs.append((f"last {2*k} sites", R, perm))
        run(f"(ii) open chain n={n}, field on site 0", n, E, eta, n // 2, f, regs, Jz, 1)
    n = 15
    E, eta = chain(n)
    regs = []
    for k in range(1, n // 2 + 1):
        R = set(range(n - 2 * k, n))
        perm = list(range(n))
        for j in range(2 * k):
            perm[n - 2 * k + j] = n - 1 - j
        regs.append((f"last {2*k} sites", R, perm))
    run(f"(iii) open chain n={n}, sector S^z=1/2", n, E, eta, 8, None, regs, Jz, 1)

print("\n" + "=" * 100)
print("violations: %d   (random and perturbed states tested: %d)   (%.1f s)" % (nviol, nrand, time.time() - t0))
