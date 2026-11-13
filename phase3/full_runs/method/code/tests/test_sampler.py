"""Unit tests of emu2.sample_mps (binomial splitting, amplitudes, two-word nodes) against exact contraction of random
right-canonical MPS (10 sites), and against TeNPy states on a toy graph. Run: python tests/test_sampler.py"""
import os
import sys
import unittest
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import emu2  # noqa: E402


def random_rc_mps(L, chi, rng, cplx):
    dims = [1] + [min(chi, 2 ** min(k, L - k)) for k in range(1, L)] + [1]
    Ts = []
    for k in range(L):
        T = rng.normal(size=(dims[k], 2, dims[k + 1]))
        if cplx:
            T = T + 1j * rng.normal(size=T.shape)
        Ts.append(T)
    # right-canonicalize by LQ sweeps from the right
    for k in range(L - 1, 0, -1):
        vl, p, vr = Ts[k].shape
        M = Ts[k].reshape(vl, p * vr)
        Q, R = np.linalg.qr(M.conj().T)          # M = R^dag Q^dag
        Ts[k] = Q.conj().T.reshape(-1, p, vr)
        Ts[k - 1] = np.tensordot(Ts[k - 1], R.conj().T, axes=(2, 0))
    Ts[0] = Ts[0] / np.linalg.norm(Ts[0])
    return Ts


def exact_amplitudes(Ts, order, down_index, n):
    L = len(Ts)
    amps = {}
    for idx in np.ndindex(*([2] * L)):
        v = np.ones((1, 1), dtype=Ts[0].dtype)
        for k, s in enumerate(idx):
            v = v @ Ts[k][:, s, :]
        b = 0
        for k, s in enumerate(idx):
            if s == down_index:
                b |= 1 << order[k]
        amps[b] = v[0, 0]
    return amps


class TestSampler(unittest.TestCase):
    def run_case(self, cplx, down_index):
        rng = np.random.default_rng(10 + cplx + 2 * down_index)
        L, n = 10, 76
        order = [61, 3, 70, 12, 64, 0, 75, 33, 63, 40]
        Ts = random_rc_mps(L, 6, rng, cplx)
        amps = exact_amplitudes(Ts, order, down_index, n)
        p = {b: abs(a) ** 2 for b, a in amps.items()}
        self.assertLess(abs(sum(p.values()) - 1), 1e-12)
        N = 300000
        r = emu2.sample_mps(Ts, order, down_index, N, rng, n, batch=70000)
        ints = emu2.to_int(r["B"])
        self.assertEqual(int(r["count"].sum()), N)
        for b, c, lp, sg in zip(ints, r["count"], r["logp"], r["sign"]):
            self.assertLess(abs(lp - np.log(p[b])), 1e-9)
            self.assertLess(abs(sg - amps[b] / abs(amps[b])), 1e-9)
        freq = {b: c / N for b, c in zip(ints, r["count"])}
        z = [abs(freq.get(b, 0.0) - pb) / (np.sqrt(pb * (1 - pb) / N) + 1e-6) for b, pb in p.items()]
        self.assertLess(max(z), 6.0)
        self.assertLess(np.mean(np.array(z) ** 2), 1.6)
        r2 = emu2.sample_mps(Ts, order, down_index, 50000, rng, n, batch=20000, merge=False)
        self.assertEqual(int(r2["count"].sum()), 50000)
        self.assertEqual(set(r2["batch"].tolist()), {0, 1, 2})
        for bb in range(3):
            sel = r2["batch"] == bb
            self.assertEqual(len(emu2.unique_rows(r2["B"][sel])[1]), int(sel.sum()))

    def test_real_down0(self):
        self.run_case(False, 0)

    def test_complex_down1(self):
        self.run_case(True, 1)

    def test_tenpy_toy(self):
        import tn
        import emu
        import toygraphs
        from scipy.sparse.linalg import expm_multiply
        from scipy import sparse
        G = toygraphs.ring_pendant(8); G.setdefault("loops12", [])
        g = emu2.load_graph(G); g1 = emu.load_graph(G)
        Jz, dt = 1.3, 0.06
        Hd = sparse.csr_matrix(emu.dense_H(g1, Jz))
        v0 = np.zeros(1 << g["n"], complex); v0[g1["neel"]] = 1.0
        rng = np.random.default_rng(7)
        for k, psi, info in tn.krylov_states(g, Jz, dt, 3, chi_max=64):
            pass
        ex = expm_multiply(-1j * 3 * dt * Hd, v0)
        Ts = tn.export(psi)
        r = emu2.sample_mps(Ts, g["order"], tn.down_index(psi), 100000, rng, g["n"], batch=30000)
        ints = np.array(emu2.to_int(r["B"]))
        self.assertTrue((np.bitwise_count(ints.astype(np.uint64)) == g["n_down"]).all())
        v = tn.dense_vector(psi, g)
        v = v / np.linalg.norm(v)
        p = np.abs(v[ints]) ** 2
        self.assertLess(np.max(np.abs(np.exp(r["logp"]) - p)), 1e-10)
        # relative phases agree with the MPS amplitudes up to one global phase
        ph = r["sign"] * np.abs(v[ints]) / v[ints]
        self.assertLess(np.max(np.abs(ph - ph[0])), 1e-8)
        # and the MPS is the exact evolution (pilot3 accuracy)
        self.assertGreater(abs(np.vdot(ex, v)), 1 - 1e-6)
        self.assertLess(np.max(np.abs(p - np.abs(ex[ints]) ** 2)), 1e-3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
