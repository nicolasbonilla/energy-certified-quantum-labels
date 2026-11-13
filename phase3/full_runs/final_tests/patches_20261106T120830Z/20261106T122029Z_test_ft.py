"""Unit tests of the final tests. `light`: numpy only, toy sizes, seconds (laptop). `full`: adds the TeNPy tests (VM).
usage: python tests/test_ft.py <inputs dir> light|full"""
import json
import os
import sys
import unittest
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import emu2  # noqa: E402
import ftlib as fl  # noqa: E402
import ftml  # noqa: E402

INP = sys.argv[1]
MODE = sys.argv[2]
del sys.argv[1:]


def toy(m=10, sd=1):
    G = fl.graph_json(5)
    nodes = fl.ball_nodes(G, 12, m)
    e = sum(1 for a, b in G["edges"] if int(a) in set(nodes) and int(b) in set(nodes))
    return fl.make_instance(G, nodes, np.random.default_rng(sd).uniform(.5, 1.5, e), "toy")


def dense_H(inst, Jz, h=None):
    """Brute-force 2^n matrix from Pauli Kronecker products (bit i = 1: down; Z = diag(1, -1) on bit 0 / 1)."""
    n = inst["n"]
    X = np.array([[0, 1], [1, 0]], complex)
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]], complex)

    def op(P, i, Q=None, j=None):
        M = np.eye(1)
        for s in range(n - 1, -1, -1):          # site 0 = least significant bit
            A = P if s == i else (Q if s == j else np.eye(2))
            M = np.kron(M, A)
        return M
    H = np.zeros((2 ** n, 2 ** n), complex)
    for (i, j), x in zip(inst["edges"], inst["J"]):
        H += x * 0.25 * (op(X, i, X, j) + op(Y, i, Y, j) + Jz * op(Z, i, Z, j))
    if h is not None:
        for i in range(n):
            H += h[i] * op(Z, i)
    return H


def gdict(inst):
    return dict(n=inst["n"], edges=inst["edges"], n_down=inst["n_down"], eta=inst["eta"], pairs=inst["edges"], loops=[],
                neel=emu2.mask(inst["n"], [i for i in range(inst["n"]) if inst["eta"][i] == -1]))


class Light(unittest.TestCase):
    def test_sector_vs_bruteforce(self):
        inst = toy(8)
        h = np.random.default_rng(3).normal(size=8) * 0.3
        sec = fl.sector(8, inst["n_down"])
        H = fl.build_H(sec, inst["edges"], inst["J"], 1.7, h).toarray()
        D = dense_H(inst, 1.7, h)
        idx = sec.cfg
        self.assertLess(np.abs(H - D[np.ix_(idx, idx)]).max(), 1e-12)

    def test_subh(self):
        inst = toy(10)
        g = gdict(inst)
        sec = fl.sector(10, inst["n_down"])
        B = sec.cfg.astype(np.uint64).reshape(-1, 1)
        cs = emu2.CSet(B, 10)
        Hd = fl.SubHd(cs, g, 2.5, inst["J"]).toarray()
        H = fl.build_H(sec, inst["edges"], inst["J"], 2.5).toarray()
        self.assertLess(np.abs(H - Hd).max(), 1e-12)
        Hu = fl.SubHd(cs, g, 2.5, np.ones(len(inst["J"]))).toarray()
        self.assertLess(np.abs(Hu - emu2.SubH(cs, g, 2.5).toarray()).max(), 1e-12)

    def test_patch_whole_is_exact(self):
        inst = toy(11)
        ex = fl.solve_exact(inst, 1.6)
        pe = fl.patch_estimates(inst, 1.6, 19, passes=1)
        self.assertLess(np.abs(np.array(pe["Z_open"]) - ex["Z"]).max(), 1e-7)
        self.assertLess(np.abs(np.array(pe["C_emb"]) - ex["C"]).max(), 1e-7)
        self.assertLess(abs(sum(pe["e_open"]) - ex["E0"]), 1e-7)

    def test_truncation_family(self):
        inst = toy(12)
        ex = fl.solve_exact(inst, 1.6)
        lv = fl.topD_levels(ex, inst, (1e-5, 1.0), nlev=12)
        self.assertTrue(len(lv) >= 3 and all(a["de"] >= b["de"] for a, b in zip(lv, lv[1:])))
        kl = fl.krylov_levels(ex, inst, 1.6, 0.0622, (1e-5, 5.0), np.random.default_rng(1))
        self.assertTrue(len(kl) >= 1)

    def test_exact_rq(self):
        inst = toy(10)
        G = fl.graph_json(5)
        inst["J"] = np.ones(len(inst["J"]))
        g = gdict(inst)
        sec = fl.sector(10, inst["n_down"])
        cs = emu2.CSet(sec.cfg.astype(np.uint64).reshape(-1, 1), 10)
        a = np.random.default_rng(5).standard_normal(len(cs))
        ai = fl.round_vector(a)
        x = fl.exact_rq(cs, g, Fraction(4), ai)
        Hs = emu2.SubH(cs, g, 4.0)
        af = np.array([float(v) for v in ai])
        self.assertLess(abs(float(x["E"]) - Hs.energy(af)), 1e-10)
        lab = emu2.diag_labels(cs, af, dict(g, nn2=[], pairs=inst["edges"]))
        self.assertLess(abs(float(x["m_s"]) - lab["m_s"]), 1e-10)
        self.assertLess(abs(float(x["Czz_bar"]) - np.mean(lab["Czz"])), 1e-10)

    def test_interval_reproduces_rigor_v2(self):
        c = fl.load_certs(os.path.join(INP, "certs_n57_stored.json"))
        lo, hi, _, _ = fl.interval(Fraction(-97.95158903089465), c, "m_s", "6.0", 57)
        self.assertLess(abs(float(lo) - 0.97347), 6e-6)
        self.assertLess(abs(float(hi) - 0.98758), 6e-6)
        lo, hi, _, _ = fl.interval(Fraction(-66.87736042153998), c, "Czz_bar", "4.0", 64)
        self.assertLess(abs(float(lo) + 0.97092), 6e-6)
        self.assertLess(abs(float(hi) + 0.93360), 6e-6)

    def test_features(self):
        i5 = fl.test_instance(1.6, 0)
        self.assertEqual(fl.site_features(i5).shape, (57, 23))
        self.assertEqual(fl.bond_features(i5).shape, (64, 23))
        t = fl.train_instance(1.6, 1)
        self.assertEqual(t["n"], 19)
        self.assertEqual(fl.site_features(t).shape, (19, 23))
        adj = fl.adjacency(i5)
        self.assertEqual(len(fl.patch_nodes(i5, adj, [0], 19)), 19)
        self.assertEqual(len(fl.patch_nodes(i5, adj, list(i5["edges"][3]), 13)), 13)

    def test_model(self):
        r = np.random.default_rng(0)
        X = r.normal(size=(1500, 6))
        y = X[:, 0] * X[:, 1] + 0.5 * np.sin(X[:, 2])
        g = np.arange(1500) // 5
        ftml.M_RFF = 200
        m = ftml.Model(1).fit(X, y, g)
        self.assertLess(m.best["cv_mae"], 0.3)
        Xn = r.normal(size=(300, 6))
        self.assertLess(np.abs(m.predict(Xn) - (Xn[:, 0] * Xn[:, 1] + 0.5 * np.sin(Xn[:, 2]))).mean(), 0.35)


class Full(unittest.TestCase):
    def setUp(self):
        import ft
        self.ft = ft
        self.g = emu2.load_graph(os.path.join(fl.HERE, "graphs", "hh_d3.json"))
        self.G = fl.graph_json(3)
        self.inst = fl.make_instance(self.G, range(19), np.random.default_rng(9).uniform(.5, 1.5, 20), "t")

    def test_dmrg_vs_ed(self):
        import tn
        ex = fl.solve_exact(self.inst, 1.6)
        psi, E, st = self.ft.dmrg_d(self.g, 1.6, self.inst["J"], {0: 32, 2: 64}, 4, 12)
        self.assertLess(abs(E - ex["E0"]), 1e-7)
        lab = tn.mps_labels(psi, self.g)
        self.assertLess(np.abs(np.array(lab["Z"]) - ex["Z"]).max(), 1e-5)
        self.assertLess(np.abs(np.array(lab["Czz"][:20]) - ex["C"]).max(), 1e-5)

    def test_krylov_vs_exact(self):
        from scipy.sparse.linalg import expm_multiply
        inst = self.inst
        sec = fl.sector(19, inst["n_down"])
        H = fl.build_H(sec, inst["edges"], inst["J"], 2.5)
        neel = sum(1 << i for i in range(19) if inst["eta"][i] == -1)
        v = np.zeros(sec.dim, complex)
        v[int(np.searchsorted(sec.cfg, neel))] = 1
        pos = {v_: k for k, v_ in enumerate(self.g["order"])}
        dt = 0.057
        Zx = []
        for _ in range(4):
            v = expm_multiply((-1j * dt) * H, v)
            Zx.append((np.abs(v) ** 2) @ sec.Zc)

        def zs(gen):
            out = []
            for k, psi, inf in gen:
                Zm = np.real(np.asarray(psi.expectation_value("Sigmaz")))
                out.append(np.array([Zm[pos[i]] for i in range(19)]))
            return out
        # DEVIATIONS.md item 1: the evolution has a second-order time-step error, so it is tested by convergence to the exact
        # evolution (about 4x per halving of the step) and by equality with the unchanged tn.krylov_states at J_e = 1.
        e2 = max(np.abs(a - b).max() for a, b in zip(zs(self.ft.dis_krylov_states(self.g, 2.5, inst["J"], dt, 4, chi_max=128, nsub=2)), Zx))
        e4 = max(np.abs(a - b).max() for a, b in zip(zs(self.ft.dis_krylov_states(self.g, 2.5, inst["J"], dt, 4, chi_max=128, nsub=4)), Zx))
        self.assertLess(e2, 1e-3)
        self.assertGreater(e2 / e4, 3.0)
        import tn
        one = np.ones(20)
        a = zs(tn.krylov_states(self.g, 2.5, dt, 4, chi_max=128, nsub=2))
        b = zs(self.ft.dis_krylov_states(self.g, 2.5, one, dt, 4, chi_max=128, nsub=2))
        self.assertLess(max(np.abs(x - y).max() for x, y in zip(a, b)), 1e-10)


if __name__ == "__main__":
    s = unittest.TestLoader().loadTestsFromTestCase(Light)
    if MODE == "full":
        s.addTests(unittest.TestLoader().loadTestsFromTestCase(Full))
    r = unittest.TextTestRunner(verbosity=2).run(s)
    sys.exit(0 if r.wasSuccessful() else 1)
