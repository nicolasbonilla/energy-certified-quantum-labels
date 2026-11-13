"""R2 pilot2 additions, unit tests on toy graphs (n <= 12): the C2_bar field (TeNPy DMRG vs dense ED), the outer
(Lagrange-dual) bound vs the exact information limit, and the Legendre bracket of Czz_bar from a ground-energy curve.
"""
import itertools
import math
import os
import sys
import unittest
import warnings
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, CODE)
sys.path.insert(0, HERE)
warnings.filterwarnings("ignore")
import toygraphs as TG     # noqa: E402
import hhmodel as HM       # noqa: E402


def dense_sector(G):
    """Dense sector H pieces in GRAPH labels: A (XY), diag zz (edges), diag zz2 (nn2), diag M; basis bit i = up."""
    n = G["n"]
    st = np.array(sorted(sum(1 << i for i in c) for c in itertools.combinations(range(n), G["n_up"])), dtype=np.int64)
    D = len(st)
    bits = ((st[:, None] >> np.arange(n)) & 1).astype(np.int64)
    z = 2.0 * bits - 1.0
    A = np.zeros((D, D))
    for (i, j) in G["edges"]:
        diff = bits[:, i] != bits[:, j]
        f = st[diff] ^ ((1 << i) | (1 << j))
        A[np.nonzero(diff)[0], np.searchsorted(st, f)] += 0.5
    zz = sum(z[:, i] * z[:, j] for (i, j) in G["edges"])
    zz2 = sum(z[:, i] * z[:, j] for (i, j) in G["nn2"])
    M = (z * np.array(G["eta"], float)).sum(1)
    return A, zz, zz2, M


class T(unittest.TestCase):
    def test_c2_field_dmrg_vs_ed(self):
        G = TG.ring_two_pendants(10)
        Jz, lam = 4.0, 0.05
        A, zz, zz2, M = dense_sector(G)
        for sign in (+1, -1):
            Hd = A + np.diag(0.25 * Jz * zz - sign * lam * zz2)
            w, v = np.linalg.eigh(Hd)
            e_ed = float(w[0]); c2_ed = float(v[:, 0] ** 2 @ zz2) / len(G["nn2"])
            H0 = A + np.diag(0.25 * Jz * zz)
            E_ed = float(v[:, 0] @ H0 @ v[:, 0])
            Mf = HM.HHModel(G, Jz, HM.field_for(G, "C2_bar", sign, lam))
            psi = HM.new_mps(Mf, HM.product_state(G, "neel"))
            psi, st = HM.run_dmrg(psi, Mf, HM.dmrg_opts(chi_max=64, max_sweeps=30, min_sweeps=6, max_E_err=1e-13,
                                                        svd_min=1e-14))
            M0 = HM.HHModel(G, Jz)
            E = float(np.real(M0.H_MPO.expectation_value(psi)))
            Ef = float(np.real(Mf.H_MPO.expectation_value(psi)))
            pos = {v_: k for k, v_ in enumerate(G["order"])}
            c2 = np.mean([float(np.real(psi.expectation_value_term([("Sigmaz", min(pos[a], pos[b])),
                                                                   ("Sigmaz", max(pos[a], pos[b]))])))
                          for (a, b) in G["nn2"]])
            self.assertAlmostEqual(Ef, e_ed, delta=1e-9)
            self.assertAlmostEqual(E, E_ed, delta=1e-7)
            self.assertAlmostEqual(c2, c2_ed, delta=1e-7)

    def test_outer_equals_exact_limit(self):
        """Dual bound sign<O> <= (E - G_sign(lam))/lam at the bisected lam equals the exact (ED) witness value."""
        G = TG.ring_two_pendants(10)
        Jz = 1.6
        A, zz, zz2, M = dense_sector(G)
        H0 = A + np.diag(0.25 * Jz * zz)
        w0, v0 = np.linalg.eigh(H0)
        E = w0[0] + 0.1
        for sign in (+1, -1):
            def ev(lam):
                w, v = np.linalg.eigh(H0 - sign * lam * np.diag(M))
                psi = v[:, 0]
                return float(psi @ H0 @ psi), float(psi ** 2 @ M), float(w[0])
            lo, hi = 0.0, 1.0
            while ev(hi)[0] <= E:
                hi *= 2
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if ev(mid)[0] <= E:
                    lo = mid
                else:
                    hi = mid
            e_lo, o_lo, g_lo = ev(lo)
            outer = (E - g_lo) / lo                 # bound on sign*<M>
            self.assertGreaterEqual(outer + 1e-9, sign * o_lo)
            self.assertAlmostEqual(outer, sign * o_lo, delta=1e-6)
            # any other lam gives a valid (looser) bound
            for lam in (0.5 * lo, 2 * lo):
                self.assertGreaterEqual((E - ev(lam)[2]) / lam + 1e-12, outer - 1e-9)

    def test_legendre_czz(self):
        """Exact max/min of Czz_bar at <H(Jz)> <= E equals the bracket from E0(Jz') (fine grid)."""
        G = TG.ring_two_pendants(10)
        A, zz, zz2, M = dense_sector(G)
        ne = len(G["edges"])
        Jz = 2.5
        H = lambda J: A + np.diag(0.25 * J * zz)
        e0 = np.linalg.eigvalsh(H(Jz))[0]
        E = e0 + 0.06
        grid = np.arange(0.5, 6.0001, 0.01)
        E0s = {J: np.linalg.eigvalsh(H(J))[0] for J in grid}
        ub = min((E - E0s[J]) / ((Jz - J) * ne / 4) for J in grid if J < Jz - 1e-9)
        lb = max((E0s[J] - E) / ((J - Jz) * ne / 4) for J in grid if J > Jz + 1e-9)
        Czz = np.diag(zz / ne)
        for sign, ref in ((+1, ub), (-1, lb)):
            lo, hi = 0.0, 1.0
            f = lambda lam: np.linalg.eigh(H(Jz) - sign * lam * Czz)[1][:, 0]
            while (lambda p: p @ H(Jz) @ p)(f(hi)) <= E:
                hi *= 2
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                p = f(mid)
                if p @ H(Jz) @ p <= E:
                    lo = mid
                else:
                    hi = mid
            p = f(lo)
            val = float(p @ Czz @ p)
            self.assertAlmostEqual(val, ref, delta=2e-4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
