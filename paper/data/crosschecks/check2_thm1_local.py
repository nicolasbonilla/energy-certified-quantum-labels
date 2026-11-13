"""Check 2 -- Theorem 1 (local labels): reset bound, the size N* = kappa/de, and the U(1)-sector version.

(a) Open transverse-field Ising chain H = -sum Z_i Z_{i+1} - h sum X_i (h = 1.5), O = Z_c at the central site
    (kappa_A = 2 + 2 + 2h = 7, i.e. two bonds of spread 2 and one field of spread 2h). For n = 4..12 and fixed error
    per site de we compute the exact upper and lower extents (Lemma A) and test
        o+(E0+eps) - o_GS >= min(1, eps/kappa) (1 - o_GS)        (and the mirror for o-),
    and whether the window is the full range [-1, 1] once n >= N* = kappa/de.
(b) XXZ chain (Jz = 2, quarter-normalised as in the paper) in the S^z = 0 and S^z = 1 sectors, O = Z_c, block
    B = {c, c+1}: kappa_B = (deg c + deg c+1 - 1)(1+Jz)/2, c_B+ = 1 - 2 P(block fully down) evaluated on the ground
    state. Test o+ - o_GS >= min(1, eps/kappa_B)(c_B+ - o_GS).
Also reports how loose N* is: the smallest n at which the computed window first reaches 99% of the full range.
"""
import numpy as np

import edlib as ed

viol = 0
ntest = 0
print("(a) TFIM open chain, h=1.5, O = Z_center, kappa_A = 7")
h = 1.5
kappa = 2 + 2 + 2 * h
for de in (0.05, 0.1, 0.2, 0.75):
    Nstar = kappa / de
    print("  de = %.2f   N* = kappa/de = %.2f" % (de, Nstar))
    first99 = None
    for n in (4, 6, 8, 10, 12):
        H, _ = ed.tfim(n, h, periodic=False)
        Z = ed.zvals(n, ed.basis(n))[:, n // 2]
        E0, v = ed.ground(H, k=1)
        E0 = E0[0]
        oGS = float(v[:, 0] ** 2 @ Z)
        eps = n * de
        lo, hi = ed.two_sided(H, Z, eps, E0)
        b_up = min(1, eps / kappa) * (1 - oGS)
        b_dn = min(1, eps / kappa) * (1 + oGS)
        ok = (hi - oGS >= b_up - 1e-6) and (oGS - lo >= b_dn - 1e-6)
        ntest += 1
        viol += not ok
        w = hi - lo
        if first99 is None and w >= 0.99 * 2:
            first99 = n
        print("    n=%2d eps=%5.2f  window [%+.4f, %+.4f] width %.4f  bound-up %.4f actual-up %.4f  %s%s" % (
            n, eps, lo, hi, w, b_up, hi - oGS, "ok" if ok else "VIOLATION",
            "   (n >= N*: full range required)" if n >= Nstar else ""))
        if n >= Nstar and w < 2 - 1e-4:
            viol += 1
            print("      ^^ VIOLATION: n >= N* but window not full")
    print("  -> window reaches 99%% of full range first at n = %s (N* = %.1f)" % (first99, Nstar))

print("\n(b) XXZ chain Jz=2 in a U(1) sector, O = Z_center, block B = {c, c+1}")
Jz = 2.0
for n in (8, 12):
    edges = [(i, i + 1) for i in range(n - 1)]
    c = n // 2
    deg = lambda i: sum(1 for e in edges if i in e)
    kB = (deg(c) + deg(c + 1) - 1) * (1 + Jz) / 2
    for nup in (n // 2, n // 2 + 1):
        st = ed.basis(n, nup)
        H = ed.xxz(n, edges, Jz, st)
        Zs = ed.zvals(n, st)
        E0, v = ed.ground(H, k=1)
        E0 = E0[0]
        p = v[:, 0] ** 2
        oGS = float(p @ Zs[:, c])
        P0 = float(p @ ((Zs[:, c] < 0) & (Zs[:, c + 1] < 0)))
        cBp = 1 - 2 * P0
        for de in (0.01, 0.03, 0.1):
            eps = n * de
            lo, hi = ed.two_sided(H, Zs[:, c], eps, E0)
            bnd = min(1, eps / kB) * (cBp - oGS)
            ok = hi - oGS >= bnd - 1e-6
            ntest += 1
            viol += not ok
            print("  n=%2d nup=%2d de=%.2f kappa_B=%.2f c_B+=%.4f o_GS=%+.4f  bound %.4f  actual %.4f  %s" % (
                n, nup, de, kB, cBp, oGS, bnd, hi - oGS, "ok" if ok else "VIOLATION"))
print("\nTheorem 1 tests: %d, violations: %d" % (ntest, viol))
