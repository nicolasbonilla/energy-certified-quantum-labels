"""Toy tests (n <= 12) of emu.py and tn.py against dense linear algebra. Run: python tests/test_emu.py"""
import os
import sys
import unittest
import numpy as np
from scipy.linalg import expm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import emu  # noqa: E402
import toygraphs  # noqa: E402


def toy(kind):
    if kind == "hh12":
        G = toygraphs.hh3_prefix(12)
    elif kind == "ring9":
        G = toygraphs.ring_pendant(8)
    else:
        G = toygraphs.ring_two_pendants(10)
    G.setdefault("loops12", [])
    return emu.load_graph(G)


def sector_configs(g):
    n = g["n"]
    b = np.arange(1 << n, dtype=np.uint64)
    return b[np.bitwise_count(b) == g["n_down"]]


class TestEmu(unittest.TestCase):
    def test_colouring_proper(self):
        for k in ("hh12", "ring"):
            g = toy(k)
            col = emu.edge_colouring(g)
            for v in range(g["n"]):
                cs = [c for e, c in col.items() if v in e]
                self.assertEqual(len(cs), len(set(cs)))

    def test_H_subspace_vs_dense(self):
        g = toy("hh12"); n = g["n"]
        Hd = emu.dense_H(g, 1.7)
        C = sector_configs(g)
        rng = np.random.default_rng(1)
        Csub = np.sort(rng.choice(C, size=len(C) // 3, replace=False))
        H = emu.build_H(Csub, g, 1.7).toarray()
        Hs = Hd[np.ix_(Csub.astype(int), Csub.astype(int))]
        self.assertLess(np.abs(H - Hs).max(), 1e-12)
        # full sector ground state = dense sector ground state
        E, v = emu.ground(emu.build_H(C, g, 1.7))
        w = np.linalg.eigvalsh(Hd[np.ix_(C.astype(int), C.astype(int))].real)
        self.assertLess(abs(E - w[0]), 1e-10)

    def test_propagation_vs_dense(self):
        for orient in ("minority_control", "majority_control"):
            g = toy("ring9"); n = g["n"]
            gates = emu.bo_gates(g, orient)
            rng = np.random.default_rng(2)
            th = rng.normal(0, 0.7, len(gates))
            U = np.eye(1 << n, dtype=complex)
            for gi, (c, t, _) in enumerate(gates):     # layer order: first gate acts first
                G = emu.dense_op(n, {c: "Z", t: "Y"})
                U = (np.cos(th[gi] / 2) * np.eye(1 << n) - 1j * np.sin(th[gi] / 2) * G) @ U
            self.assertLess(np.abs(U.imag).max(), 1e-12)   # real orthogonal
            Hd = emu.dense_H(g, 1.3)
            Hp = U @ Hd @ U.conj().T
            strings = emu.propagate(emu.H_terms(g, 1.3), gates)
            M = 0
            for (x, z), monos in strings.items():
                for (cf, cm, sm) in monos:
                    f = cf
                    for i in range(len(gates)):
                        if (cm >> i) & 1: f *= np.cos(th[i])
                        if (sm >> i) & 1: f *= np.sin(th[i])
                    M = M + emu.dense_pauli(n, f, x, z)
            self.assertLess(np.abs(M - Hp).max(), 1e-11)
            # grouped operator restricted to a random sector subspace
            C = sector_configs(g)
            Csub = np.sort(rng.choice(C, size=len(C) // 2, replace=False))
            op = emu.GroupedOp(emu.sector_relevant(strings), len(gates))
            Ms = op.matrix(Csub, th).toarray()
            ii = Csub.astype(int)
            self.assertLess(np.abs(Ms - Hp[np.ix_(ii, ii)].real).max(), 1e-11)
            a = rng.normal(size=len(Csub)); a /= np.linalg.norm(a)
            e = op.string_expectations(Csub, a)
            val, grad = op.value_and_grad(th, e)
            self.assertLess(abs(val - a @ Hp[np.ix_(ii, ii)].real @ a), 1e-11)
            for k in (0, 3, len(gates) - 1):
                d = np.zeros(len(gates)); d[k] = 1e-6
                fd = (op.value_and_grad(th + d, e)[0] - op.value_and_grad(th - d, e)[0]) / 2e-6
                self.assertLess(abs(fd - grad[k]), 1e-6)
            # rotated labels = labels of the physical state U^dag psi
            psi = np.zeros(1 << n); psi[ii] = a
            phys = U.conj().T @ psi
            lab = emu.rotated_labels(Csub, a, g, gates, th)
            for i in range(n):
                Zi = np.vdot(phys, emu.dense_op(n, {i: "Z"}) @ phys).real
                self.assertLess(abs(Zi - lab["Z"][i]), 1e-11)
            i, j = g["pairs"][0]
            zz = np.vdot(phys, emu.dense_op(n, {i: "Z", j: "Z"}) @ phys).real
            self.assertLess(abs(zz - lab["Czz"][0]), 1e-11)

    def test_bo_lowers_energy(self):
        g = toy("hh12")
        C = sector_configs(g)
        rng = np.random.default_rng(3)
        Csub = np.sort(rng.choice(C, size=60, replace=False))
        if g["neel"] not in set(Csub.tolist()):
            Csub = np.sort(np.append(Csub, np.uint64(g["neel"])))
        H = emu.build_H(Csub, g, 2.0)
        E, a = emu.ground(H)
        r = emu.basis_optimize(Csub, a, g, 2.0, emu.bo_gates(g), rng, n_starts=3)
        self.assertLessEqual(r["C_alpha_opt"], E + 1e-12)
        self.assertLessEqual(r["E_bo"], r["C_alpha_opt"] + 1e-10)
        self.assertLess(abs(r["C_alpha_at_0"] - E), 1e-10)
        self.assertLess(r["asym"], 1e-12)

    def test_recover_and_noise(self):
        g = toy("hh12"); n = g["n"]
        rng = np.random.default_rng(4)
        b = rng.integers(0, 1 << n, size=5000).astype(np.uint64)
        r = emu.recover(b, n, g["n_down"], rng)
        self.assertTrue((np.bitwise_count(r) == g["n_down"]).all())
        ok = np.bitwise_count(b) == g["n_down"]
        self.assertTrue((r[ok] == b[ok]).all())
        # only excess-species bits flipped
        bad = ~ok
        up = np.bitwise_count(b[bad]) > g["n_down"]
        self.assertTrue(((r[bad][up] & ~b[bad][up]) == 0).all())       # only 1 -> 0
        self.assertTrue(((b[bad][~up] & ~r[bad][~up]) == 0).all())     # only 0 -> 1
        x = emu.add_noise(np.zeros(20000, dtype=np.uint64), n, 0.1, rng)
        self.assertLess(abs(np.bitwise_count(x).mean() / n - 0.1), 0.01)

    def test_diag_labels(self):
        g = toy("hh12"); n = g["n"]
        C = sector_configs(g)
        rng = np.random.default_rng(5)
        a = rng.normal(size=len(C)); a /= np.linalg.norm(a)
        lab = emu.diag_labels(C, a, g)
        psi = np.zeros(1 << n); psi[C.astype(int)] = a
        for i in (0, 5, n - 1):
            self.assertLess(abs(lab["Z"][i] - np.vdot(psi, emu.dense_op(n, {i: "Z"}) @ psi).real), 1e-12)
        i, j = g["pairs"][-1]
        self.assertLess(abs(lab["Czz"][-1] - np.vdot(psi, emu.dense_op(n, {i: "Z", j: "Z"}) @ psi).real), 1e-12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
