"""Bit-order and equivalence unit tests on a LOCAL simulator (qiskit-aer; no IBM job, no network).

Conventions under test: qpu_lib C1-C7 and qpu_route (routed layout). Fake backend: FakeKingston (Heron r2 coupling
map shipped with qiskit-ibm-runtime; its calibration is a stored snapshot, used only to choose a layout here).
  T1  the asymmetric check state is not invariant under any automorphism of heavy_hex_graph(5) nor under i -> 56 - i
  T2  product states (asymmetric, Neel, single sites incl. boundary nodes) through transpile + routed layout + Aer
      + decode_bitarray return exactly the prepared configuration; get_int_counts and get_counts agree; the reversed
      (big-endian) reading does NOT
  T3  check_isa_routed passes on transpiled routed Krylov circuits; check_verdict logic on synthetic data
  T4  numpy TrotterMPS == dense Trotter state (d = 3, n = 19, k = 3)
  T5  routed circuit == logical Trotter circuit (d = 3, statevector incl. ancillas; ancillas return to |0>)
  T6  ISA circuit of the routed d = 3 Krylov k = 1 on the fake device, sampled by Aer MPS and decoded, reproduces the
      dense <Z_i> (5 sigma) -> the whole chain layout -> device qubits -> clbits -> configuration on an entangled state
  T7  emu2.sample_mps on the TrotterMPS export reproduces the dense <Z_i> (5 sigma)
"""
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import qpu_lib as ql  # noqa: E402
import qpu_route as qr  # noqa: E402

DT = 0.0569
JZ = 1.2


def fake():
    from qiskit_ibm_runtime.fake_provider import FakeKingston
    return FakeKingston()


def run_aer(circs, shots, method):
    from qiskit_aer.primitives import SamplerV2
    s = SamplerV2(seed=1234, options=dict(backend_options=dict(method=method)))
    res = s.run([(c,) for c in circs], shots=shots).result()
    return [r.data.c for r in res]


def mps_dense(T, g):
    psi = T.export()
    v = psi[0]
    for t in psi[1:]:
        v = np.tensordot(v, t, axes=(v.ndim - 1, 0))
    v = v.reshape([2] * g["n"])
    out = np.zeros(1 << g["n"], complex)
    for idx in np.ndindex(*([2] * g["n"])):
        b = 0
        for k, p in enumerate(idx):
            if p == 1:
                b |= 1 << g["order"][k]
        out[b] = v[idx]
    return out


def z_dense(v, n):
    pr = np.abs(v) ** 2
    idx = np.arange(len(v))
    return np.array([float(pr @ (1 - 2 * ((idx >> i) & 1))) for i in range(n)])


class T1Asym(unittest.TestCase):
    def test_asymmetric(self):
        import rustworkx as rx
        g = ql.graph57()
        S = set(ql.ASYM_SITES)
        P = rx.PyGraph()
        P.add_nodes_from(list(range(g["n"])))
        for (i, j) in g["edges"]:
            P.add_edge(i, j, None)
        n_aut = 0
        for m in rx.vf2_mapping(P, P, subgraph=False):
            n_aut += 1
            if all(m[i] == i for i in m):
                continue
            self.assertNotEqual(set(m[i] for i in S), S)
        self.assertGreater(n_aut, 1)
        self.assertNotEqual(set(g["n"] - 1 - i for i in S), S)
        self.assertNotEqual(S, set(ql.neel_sites(g)))
        self.assertNotEqual(len(S), len(ql.neel_sites(g)))
        eta = set(int(x) for x in np.asarray(g["eta"])[sorted(S)])
        self.assertEqual(eta, {-1, 1})


class T2Product(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = fake()
        cls.g = ql.graph57()
        cls.sel = qr.choose_routed_layout(cls.b.target, cls.g, 5)

    def test_products(self):
        g, sel = self.g, self.sel
        cases = [("asym", ql.ASYM_SITES), ("neel", ql.neel_sites(g)), ("s0", (0,)), ("s25", (25,)),
                 ("s36", (36,)), ("s56", (56,))]
        circs = [ql.product_circuit(g, s, nm) for nm, s in cases]
        isas = ql.transpile_isa(circs, self.b, sel["layout"])
        for c in isas:
            ql.check_isa(c, g, sel["layout"])
        bas = run_aer(isas, 64, "stabilizer")
        for (nm, s), ba in zip(cases, bas):
            exp = ql.config_int(s)
            conf = ql.decode_bitarray(ba)
            self.assertTrue(np.all(conf == np.uint64(exp)), nm)
            self.assertEqual(set(ba.get_int_counts().keys()), {exp}, nm)
            key = list(ba.get_counts().keys())[0]
            self.assertEqual(len(key), g["n"])
            for i in range(g["n"]):
                self.assertEqual(int(key[g["n"] - 1 - i]), (exp >> i) & 1, (nm, i))
            rev = int(key[::-1], 2)
            if nm in ("asym", "neel", "s0", "s25"):
                self.assertNotEqual(rev, exp, nm)
            v = ql.check_verdict(conf, exp, g["n"])
            self.assertTrue(v["pass_"], nm)


class T3ISA(unittest.TestCase):
    def test_routed_isa_and_verdict(self):
        b = fake()
        g = ql.graph57()
        sel = qr.choose_routed_layout(b.target, g, 5)
        circs = [qr.routed_krylov_circuit(g, JZ, DT, k, sel) for k in (1, 2)]
        isas = ql.transpile_isa(circs, b, qr.routed_layout_list(sel))
        for k, c in zip((1, 2), isas):
            st = qr.check_isa_routed(c, g, sel)
            self.assertEqual(st["n_meas"], 57)
            self.assertGreaterEqual(c.count_ops().get("cz", 0), 192 * k)
        rng = np.random.default_rng(7)
        exp = ql.config_int(ql.ASYM_SITES)
        conf = np.full(20000, exp, dtype=np.uint64)
        flips = (rng.random((20000, 57)) < 0.04)
        for i in range(57):
            conf ^= flips[:, i].astype(np.uint64) << np.uint64(i)
        self.assertTrue(ql.check_verdict(conf, exp, 57)["pass_"])
        rev = int(format(exp, "057b")[::-1], 2)
        self.assertFalse(ql.check_verdict(conf, rev, 57)["pass_"])
        bad = conf.copy()
        f = rng.random(20000) < 0.15
        bad ^= f.astype(np.uint64) << np.uint64(25)
        self.assertFalse(ql.check_verdict(bad, exp, 57)["pass_"])


class T4MPS(unittest.TestCase):
    def test_mps_vs_dense(self):
        g = ql.graph(3)
        T = ql.TrotterMPS(g, chi_max=64)
        for _ in range(3):
            T.step(JZ, DT)
        v = ql.dense_trotter(g, JZ, DT, 3)
        w = mps_dense(T, g)
        F = abs(np.vdot(v, w)) ** 2 / (np.vdot(v, v).real * np.vdot(w, w).real)
        self.assertGreater(F, 1 - 1e-10)
        self.assertLess(np.max(np.abs(T.z_expect() - z_dense(v, g["n"]))), 1e-9)
        self.assertLess(T.discarded, 1e-12)


class T5Routed(unittest.TestCase):
    def test_routed_equals_logical(self):
        from qiskit.quantum_info import Statevector
        b = fake()
        g = ql.graph(3)
        sel = qr.choose_routed_layout(b.target, g, 3)
        self.assertEqual(sorted(int(s) for s in sel["paths"]), qr.boundary_nodes(g, 3))
        k = 2
        v = ql.dense_trotter(g, JZ, DT, k)
        lg = ql.krylov_circuit(g, JZ, DT, k, measure=False)
        sv = Statevector(lg.remove_final_measurements(inplace=False)).data
        self.assertGreater(abs(np.vdot(v, sv)) ** 2, 1 - 1e-10)
        rc = qr.routed_krylov_circuit(g, JZ, DT, k, sel, measure=False)
        sr = Statevector(rc).data
        n = g["n"]
        idx = np.arange(len(sr))
        anc_pop = float(np.sum(np.abs(sr[idx >= (1 << n)]) ** 2))
        self.assertLess(anc_pop, 1e-12)
        self.assertGreater(abs(np.vdot(v, sr[:1 << n])) ** 2, 1 - 1e-10)


class T6ISASampling(unittest.TestCase):
    def test_isa_chain(self):
        b = fake()
        g = ql.graph(3)
        sel = qr.choose_routed_layout(b.target, g, 3)
        qc = qr.routed_krylov_circuit(g, JZ, DT * 4, 1, sel)        # larger angle: a clearly entangled state
        isa = ql.transpile_isa([qc], b, qr.routed_layout_list(sel))[0]
        qr.check_isa_routed(isa, g, sel)
        N = 20000
        ba = run_aer([isa], N, "matrix_product_state")[0]
        conf = ql.decode_bitarray(ba)
        Zs = np.array([1 - 2 * float(np.mean((conf >> np.uint64(i)) & np.uint64(1))) for i in range(g["n"])])
        Ze = z_dense(ql.dense_trotter(g, JZ, DT * 4, 1), g["n"])
        sig = np.sqrt(np.maximum(1 - Ze ** 2, 1e-4) / N)
        self.assertLess(np.max(np.abs(Zs - Ze) / sig), 5.0)
        self.assertGreater(np.max(np.abs(Ze - z_dense(ql.dense_trotter(g, JZ, DT * 4, 0), g["n"]))), 0.05)


class T7Sampler(unittest.TestCase):
    def test_sample_mps(self):
        import emu2
        g = ql.graph(3)
        T = ql.TrotterMPS(g, chi_max=64)
        for _ in range(4):
            T.step(JZ, DT * 3)
        Ts = T.export()
        N = 40000
        r = emu2.sample_mps(Ts, g["order"], 1, N, np.random.default_rng(3), g["n"], batch=20000, want_amp=False)
        B = r["B"][:, 0]
        c = r["count"]
        Zs = np.array([1 - 2 * float(np.sum(c * ((B >> np.uint64(i)) & np.uint64(1))) / N) for i in range(g["n"])])
        Ze = T.z_expect()
        sig = np.sqrt(np.maximum(1 - Ze ** 2, 1e-4) / N)
        self.assertLess(np.max(np.abs(Zs - Ze) / sig), 5.0)
        self.assertTrue(np.all(emu2.popcount(r["B"]) == g["n_down"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
