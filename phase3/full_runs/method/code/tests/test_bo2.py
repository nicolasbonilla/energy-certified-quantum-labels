"""Unit tests of bo2.py (generators ZY / YX / Givens, parameter maps, procedure) against dense algebra (n = 9, 12).
Run: python tests/test_bo2.py"""
import os
import sys
import unittest
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import emu  # noqa: E402
import bo2  # noqa: E402
import toygraphs  # noqa: E402


def ring9():
    G = toygraphs.ring_pendant(8); G.setdefault("loops12", [])
    return emu.load_graph(G)


def sector(g):
    b = np.arange(1 << g["n"], dtype=np.uint64)
    return b[np.bitwise_count(b) == g["n_down"]]


def dense_U(g, gates, th):
    n = g["n"]
    U = np.eye(1 << n, dtype=complex)
    for gi, (xg, zg, cg, _, _) in enumerate(gates):
        P = emu.dense_pauli(n, cg, xg, zg)
        U = (np.cos(th[gi] / 2) * np.eye(1 << n) - 1j * np.sin(th[gi] / 2) * P) @ U
    return U


class TestBO2(unittest.TestCase):
    def test_generators_vs_dense(self):
        g = ring9(); n = g["n"]
        rng = np.random.default_rng(1)
        Hd = emu.dense_H(g, 1.4)
        Sz = sum(emu.dense_op(n, {i: "Z"}) for i in range(n))
        C = sector(g)
        Csub = np.sort(rng.choice(C, size=len(C) // 2, replace=False))
        ii = Csub.astype(int)
        for kind in ("ZY", "YX", "GV"):
            for shared in (False, True):
                gates, npar = bo2.gates_for(g, kind, "minority_control", shared)
                P = bo2.Param(gates, npar)
                phi = rng.normal(0, 0.8, npar)
                th = P.theta(phi)
                U = dense_U(g, gates, th)
                self.assertLess(np.abs(U.imag).max(), 1e-12)
                if kind == "GV":
                    self.assertLess(np.abs(U @ Sz - Sz @ U).max(), 1e-12)
                else:
                    self.assertGreater(np.abs(U @ Sz - Sz @ U).max(), 1e-3)
                Hp = U @ Hd @ U.conj().T
                strings = bo2.propagate(emu.H_terms(g, 1.4), gates)
                M = 0
                for (x, z), monos in strings.items():
                    for (cf, cm, sm) in monos:
                        f = cf
                        for i in range(len(gates)):
                            if (cm >> i) & 1: f *= np.cos(th[i])
                            if (sm >> i) & 1: f *= np.sin(th[i])
                        M = M + emu.dense_pauli(n, f, x, z)
                self.assertLess(np.abs(M - Hp).max(), 1e-11, (kind, shared))
                a = rng.normal(size=len(Csub)); a /= np.linalg.norm(a)
                pb = bo2.Problem(Csub, a, g, 1.4, kind, "minority_control", shared)
                v, gr = pb.f(phi)
                self.assertLess(abs(v - a @ Hp[np.ix_(ii, ii)].real @ a), 1e-11)
                for k in range(min(npar, 3)):
                    d = np.zeros(npar); d[k] = 1e-6
                    fd = (pb.f(phi + d)[0] - pb.f(phi - d)[0]) / 2e-6
                    self.assertLess(abs(fd - gr[k]), 1e-6)
                Ms = pb.op.matrix(Csub, th).toarray()
                self.assertLess(np.abs(Ms - Hp[np.ix_(ii, ii)].real).max(), 1e-11)
                lab = bo2.rotated_labels(Csub, a, g, gates, th)
                psi = np.zeros(1 << n); psi[ii] = a
                phys = U.conj().T @ psi
                for i in (0, n - 1):
                    self.assertLess(abs(lab["Z"][i] - np.vdot(phys, emu.dense_op(n, {i: "Z"}) @ phys).real), 1e-11)

    def test_run_all_toy(self):
        G = toygraphs.hh3_prefix(12); G.setdefault("loops12", [])
        g = emu.load_graph(G)
        C = sector(g)
        rng = np.random.default_rng(3)
        Csub = np.sort(rng.choice(C, size=80, replace=False))
        if np.uint64(g["neel"]) not in set(Csub.tolist()):
            Csub = np.sort(np.append(Csub, np.uint64(g["neel"])))
        H = emu.build_H(Csub, g, 2.0)
        E, a = emu.ground(H)
        Hd = emu.dense_H(g, 2.0).real
        E0 = np.linalg.eigvalsh(Hd[np.ix_(C.astype(int), C.astype(int))])[0]
        ref = dict(E0=E0, labels=emu.diag_labels(C, np.linalg.eigh(Hd[np.ix_(C.astype(int), C.astype(int))])[1][:, 0], g))
        out = bo2.run_all(Csub, a, E, g, 2.0, ref, 1.0, rng)
        self.assertLess(abs(out["E_pre_check"] - E), 1e-10)
        for name, r in out["variants"].items():
            self.assertLessEqual(r["C_opt"], r["C_at_0"] + 1e-10, name)
            self.assertLessEqual(r["E_bo"], r["C_opt"] + 1e-9, name)
            self.assertLess(r["asym"], 1e-12)
            self.assertLess(abs(r["C_at_0"] - E), 1e-10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
