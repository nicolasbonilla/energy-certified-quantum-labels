# t5_dilute_and_avg.py
#   part A: what Theorem 1(b) proves in a DILUTE U(1) sector (one up spin on an XXZ ring of n sites).  The exact window
#           of Z_i loses certification at n ~ 1/de, but the bound of Theorem 1(b), maximised over ALL blocks, stays below
#           tau at every n when de is small: "proved, also in a charge sector" needs a condition on the sector.
#   part B: Theorem 1(d): average of Z over b sites, no sector (TFIM ring): exact full-range energy against b*kappa_1,
#           additivity of separated resets, and the same label in a U(1) sector (XXZ chain).
import sys, time, json
import numpy as np
import scipy.sparse as sp
from r10lib import *

t0 = time.time()
out = {}

print("== part A: one-magnon sector of the XXZ ring, H = (1/4) sum (XX + YY + Jz ZZ), Jz = 1.6, label Z_0 ==")
Jz = 1.6
spread = (1 + Jz) / 2
A = []
for de in (0.011, 0.002):
    print(f"  error per site de = {de}")
    for n in (20, 50, 100, 200, 400):
        # basis |j> = the up spin sits on site j ; (XX+YY)/4 hops with amplitude 1/2 ; ZZ part is a constant on a ring
        hopm = sp.lil_matrix((n, n))
        for j in range(n):
            hopm[j, (j + 1) % n] = 0.5
            hopm[(j + 1) % n, j] = 0.5
        Hs = (hopm + sp.identity(n) * (Jz / 4) * (n - 4)).tocsr()
        Od = -np.ones(n)
        Od[0] = 1.0
        W = WindowSolver(Hs, sp.diags(Od).tocsr(), dense_below=64, grid=(-5.0, 3.0, 49))
        psi = W.G[:, 0]
        ogs = W.oGS_plus
        tau = 0.06 * abs(ogs)
        eps = n * de
        r = W.window(eps, tol=1e-9)
        # Theorem 1(b), every block: by symmetry of the uniform ground state only the block size m matters for c_B, and
        # among blocks of size m an arc has the fewest touching bonds (m + 1), hence the smallest kappa_B
        best_up = best_dn = 0.0
        best_m = None
        for m in range(1, n + 1):
            cBp = -1 + 2 * m / n                    # 1 - 2 P(block fully down), P = 1 - m/n
            cBm = -1.0 if m >= 2 else ogs           # -1 + 2 P(block fully up)
            kB = min(m + 1, n) * spread
            bu = min(1.0, eps / kB) * (cBp - ogs)
            bd = min(1.0, eps / kB) * (ogs - cBm)
            if bu > best_up:
                best_up, best_m = bu, m
            best_dn = max(best_dn, bd)
        best = best_up + best_dn                    # upper and lower sides may use different blocks
        A.append(dict(de=de, n=n, eps=eps, oGS=ogs, tau=tau, deg=W.deg, w_exact_inner=r["w_inner"],
                      w_exact_outer=r["w_outer"], thm1b_best=best, best_block_size=best_m))
        print(f"    n={n:3d} eps={eps:6.3f} o_GS={ogs:+.4f} tau={tau:.4f} | exact width {r['w_inner']:.4f} "
              f"({r['w_inner']/tau:6.1f} tau; {'NOT certified' if r['w_inner'] > tau else 'certified'}) | best Theorem 1(b) "
              f"bound over all blocks {best:.4f} ({best/tau:5.2f} tau, block of {best_m} sites): "
              f"{'proves the loss' if best > tau else 'proves nothing'}   [deg {W.deg}]", flush=True)
out["partA"] = A

print("\n== part B: Theorem 1(d) -- label = average of Z over b sites ==")
n = 10
S = Spins(n)
terms = S.tfim_terms(chain(n, True), h=1.5)
H = total(terms)
k1 = max(kappa(terms, [i]) for i in range(n))
w0, V0 = lowest(H, k=2)
psi0 = V0[:, 0]
E0 = float(w0[0])
print(f"  TFIM ring n={n} h=1.5 (no sector): kappa_1 = {k1}")
Bout = []
for sites in ([0], [0, 1], [0, 5], [0, 1, 2], [0, 3, 6], [0, 1, 2, 3, 4], [0, 2, 4, 6, 8], list(range(10))):
    b = len(sites)
    O = sum(S.Z[i] for i in sites) / b
    W = WindowSolver(H, O, dense_below=64, grid=(-3.0, 3.0, 31))
    kB = kappa(terms, sites)
    phi = np.zeros(2 ** b, dtype=complex)
    phi[-1] = 1.0                                   # all b sites up
    ens = reset_ensemble(psi0.astype(complex), n, sites, phi)
    cost = ens_expval(H, ens) - E0
    single = 0.0
    for i in sites:
        e1 = reset_ensemble(psi0.astype(complex), n, [i], np.array([0, 1], dtype=complex))
        single += ens_expval(H, e1) - E0
    share = any(len(set(sup) & set(sites)) >= 2 for sup, _ in terms)
    eps_full = W.Esat_plus - W.E0
    # bound of (d) with b*kappa_1 at a few energies
    worst = np.inf
    for eps in (0.25 * b * k1, 0.5 * b * k1, b * k1):
        u = W.extreme(eps, +1, tol=1e-8)["inner"] - W.oGS_plus
        bound = min(1.0, eps / (b * k1)) * (W.omax - W.oGS_plus)
        worst = min(worst, u - bound)
    Bout.append(dict(sites=sites, b=b, kappa_B=kB, b_kappa1=b * k1, reset_cost=cost, sum_single_costs=single,
                     share_a_term=share, eps_full=eps_full, worst_margin=worst))
    print(f"    sites {str(sites):32s} b={b:2d}: exact full-range energy {eps_full:7.4f} <= joint reset cost {cost:7.4f} "
          f"<= kappa_B {kB:5.1f} <= b*kappa_1 {b*k1:5.1f} ; sum of single-site reset costs {single:7.4f} "
          f"({'sites share a term' if share else 'no shared term: costs add, diff %.1e' % abs(single - cost)}) ; "
          f"min(exact - bound) = {worst:+.3f}", flush=True)
out["partB_tfim"] = Bout

print("  XXZ open chain n=10, Jz=1.6, sector nup=5: the same label inside a sector")
terms = S.xxz_terms(chain(n), 1.6)
H = total(terms)
idx = S.sector(5)
Hs = H[idx][:, idx]
k1 = max(kappa(terms, [i]) for i in range(n))
Cout = []
for sites in ([4], [4, 5], [4, 6], [3, 4, 5, 6], [0, 2, 4, 6, 8], list(range(10))):
    b = len(sites)
    O = sum(S.Z[i] for i in sites) / b
    Os = O[idx][:, idx]
    W = WindowSolver(Hs, Os, dense_below=64, grid=(-3.0, 3.0, 31))
    eps = b * k1
    r = W.window(eps, tol=1e-8)
    Cout.append(dict(sites=sites, b=b, eps=eps, lo=r["o_minus_inner"], hi=r["o_plus_inner"], omin=W.omin, omax=W.omax,
                     oGS=W.oGS_plus))
    print(f"    sites {str(sites):28s} b={b:2d}: at eps = b*kappa_1 = {eps:5.1f} the sector window is "
          f"[{r['o_minus_inner']:+.4f},{r['o_plus_inner']:+.4f}]; spectral range of the label in the sector "
          f"[{W.omin:+.4f},{W.omax:+.4f}]; without a sector it would be [-1,+1]", flush=True)
out["partB_xxz_sector"] = Cout
json.dump(out, open("t5_dilute_and_avg.json", "w"), indent=1, default=float)
print("total time %.0f s" % (time.time() - t0))
