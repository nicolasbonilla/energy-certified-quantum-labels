"""Toy tests (n <= 12) of tn.py (TeNPy) + emu sampler against dense linear algebra. Run: python tests/test_tn.py"""
import os
import sys
import unittest
import numpy as np
from scipy.sparse.linalg import expm_multiply
from scipy import sparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import emu  # noqa: E402
import tn  # noqa: E402
import toygraphs  # noqa: E402


def toy9():
    G = toygraphs.ring_pendant(8)
    G.setdefault("loops12", [])
    return emu.load_graph(G)


class TestTN(unittest.TestCase):
    def test_tdvp_vs_exact_and_sampler(self):
        g = toy9(); n = g["n"]
        Jz, dt = 1.3, 0.06
        Hd = sparse.csr_matrix(emu.dense_H(g, Jz))
        v0 = np.zeros(1 << n, complex); v0[g["neel"]] = 1.0
        rng = np.random.default_rng(7)
        for k, psi, info in tn.krylov_states(g, Jz, dt, 4, chi_max=64):
            ex = expm_multiply(-1j * k * dt * Hd, v0)
            v = tn.dense_vector(psi, g)
            ov = abs(np.vdot(ex, v))
            self.assertGreater(ov, 1 - 1e-7, (k, ov))
            if k == 4:
                Ts = tn.export(psi)
                N = 200000
                s = emu.sample_mps(Ts, g["order"], tn.down_index(psi), N, rng)
                cnt = np.bincount(s.astype(np.int64), minlength=1 << n) / N
                p = np.abs(ex) ** 2
                sig = np.sqrt(p * (1 - p) / N) + 1e-6
                self.assertLess(np.max(np.abs(cnt - p) / sig), 6.0)
                self.assertTrue((np.bitwise_count(s) == g["n_down"]).all())

    def test_dmrg_vs_ed_and_labels(self):
        g = toy9(); n = g["n"]
        Jz = 1.6
        psi, E, st = tn.dmrg_ground(g, Jz, {0: 16, 2: 32}, max_sweeps=10)
        C = np.arange(1 << n, dtype=np.uint64)
        C = C[np.bitwise_count(C) == g["n_down"]]
        E0, a = emu.ground(emu.build_H(C, g, Jz))
        self.assertLess(abs(E - E0), 1e-9)
        lab = tn.mps_labels(psi, g)
        ref = emu.diag_labels(C, a, g)
        self.assertLess(np.max(np.abs(np.array(lab["Z"]) - ref["Z"])), 1e-7)
        self.assertLess(np.max(np.abs(np.array(lab["Czz"]) - ref["Czz"])), 1e-7)
        self.assertLess(abs(lab["m_s"] - ref["m_s"]), 1e-7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
