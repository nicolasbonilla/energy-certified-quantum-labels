"""Unit tests of emu2.py (multi-word configurations) against dense algebra (n <= 12 active spins) and against pilot3's
emu.py (uint64) on random n = 57 subspaces. Run: python tests/test_emu2.py"""
import os
import sys
import unittest
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import emu  # noqa: E402
import emu2  # noqa: E402
import toygraphs  # noqa: E402

SHIFT = 60
NBIG = 76


def toy12():
    G = toygraphs.hh3_prefix(12)
    G.setdefault("loops12", [])
    return G


def shifted(G):
    """The toy graph embedded at bit positions SHIFT.. SHIFT+11 of an NBIG-bit word pair (other spins inactive)."""
    n = G["n"]
    eta = [1] * NBIG
    for i in range(n):
        eta[i + SHIFT] = G["eta"][i]
    edges = [(a + SHIFT, b + SHIFT) for a, b in G["edges"]]
    nn2 = [(a + SHIFT, b + SHIFT) for a, b in G["nn2"]]
    loop = [v + SHIFT for v in range(min(n, 12))][:6]
    g = dict(n=NBIG, W=2, eta=np.array(eta), edges=edges, nn2=nn2, pairs=edges + nn2, loops=[loop],
             n_down=int(sum(1 for e in G["eta"] if e == -1)))
    g["neel"] = emu2.mask(NBIG, [i for i in range(NBIG) if eta[i] == -1])
    return g


def sector_ints(G):
    n = G["n"]; nd = sum(1 for e in G["eta"] if e == -1)
    b = np.arange(1 << n, dtype=np.uint64)
    return b[np.bitwise_count(b) == nd].astype(np.int64)


class TestEmu2(unittest.TestCase):
    def test_cset_lookup_unique(self):
        rng = np.random.default_rng(1)
        for n in (57, 115):
            W = emu2.nwords(n)
            B = rng.integers(0, 2 ** 63, size=(5000, W), dtype=np.uint64)
            if n == 115:
                B[:, 1] &= np.uint64((1 << (115 - 64)) - 1)
            B = np.concatenate([B, B[:1000]])
            cs = emu2.CSet(B, n)
            self.assertEqual(len(cs), len(set(map(tuple, B.tolist()))))
            pos, ok = cs.lookup(B)
            self.assertTrue(ok.all())
            self.assertTrue((cs.B[pos] == B).all())
            Q = B[:500].copy(); Q[:, 0] ^= np.uint64(1 << 40)
            pos, ok = cs.lookup(Q)
            truth = np.array([tuple(q) in set(map(tuple, B.tolist())) for q in Q.tolist()])
            self.assertTrue((ok == truth).all())
            Bu, ku, c, f = emu2.unique_rows(B, np.ones(len(B), np.int64), np.arange(len(B)), reduce=["sum", "min"])
            self.assertEqual(int(c.sum()), len(B))
            self.assertEqual(int((c == 2).sum()), 1000)

    def test_H_labels_two_words_vs_dense(self):
        G = toy12(); n = G["n"]
        g1 = emu.load_graph(G)
        g = shifted(G)
        Jz = 1.7
        Hd = emu.dense_H(g1, Jz).real
        ints = sector_ints(G)
        rng = np.random.default_rng(2)
        sub = np.sort(rng.choice(ints, size=len(ints) // 3, replace=False))
        B = emu2.from_int([int(v) << SHIFT for v in sub], NBIG)
        cs = emu2.CSet(B, NBIG)
        back = np.array([v >> SHIFT for v in emu2.to_int(cs.B)])
        Hs = emu2.SubH(cs, g, Jz)
        self.assertLess(np.abs(Hs.toarray() - Hd[np.ix_(back, back)]).max(), 1e-12)
        a = rng.normal(size=len(cs)); a /= np.linalg.norm(a)
        lab = emu2.diag_labels(cs, a, g)
        psi = np.zeros(1 << n); psi[back] = a
        for i in range(n):
            Zi = psi @ (emu.dense_op(n, {i: "Z"}).real @ psi)
            self.assertLess(abs(lab["Z"][i + SHIFT] - Zi), 1e-12)
        self.assertLess(abs(lab["Z"][0] - 1.0), 1e-12)
        for k, (i, j) in enumerate(g["pairs"][:20]):
            zz = psi @ (emu.dense_op(n, {i - SHIFT: "Z", j - SHIFT: "Z"}).real @ psi)
            self.assertLess(abs(lab["Czz"][k] - zz), 1e-12)
        lp = [v - SHIFT for v in g["loops"][0]]
        ops = {v: "Z" for v in lp}
        self.assertLess(abs(lab["Zloop"][0] - psi @ (emu.dense_op(n, ops).real @ psi)), 1e-12)
        # ground state of the full sector, sparse path forced
        csf = emu2.CSet(emu2.from_int([int(v) << SHIFT for v in ints], NBIG), NBIG)
        Hf = emu2.SubH(csf, g, Jz)
        from scipy.sparse.linalg import eigsh, LinearOperator
        op = LinearOperator((Hf.D, Hf.D), matvec=Hf.matvec, dtype=float)
        w = eigsh(op, k=1, which="SA", tol=1e-12)[0][0]
        ws = np.linalg.eigvalsh(Hd[np.ix_(ints, ints)])[0]
        self.assertLess(abs(w - ws), 1e-9)
        self.assertLess(abs(emu2.ground(Hf)[0] - ws), 1e-9)
        self.assertLess(abs(Hf.energy(np.ones(Hf.D)) - np.ones(Hf.D) @ Hd[np.ix_(ints, ints)] @ np.ones(Hf.D) / Hf.D),
                        1e-10)

    def test_equal_to_pilot3_at_n57(self):
        g1 = emu.load_graph(os.path.join(os.path.dirname(HERE), "graphs", "hh_d5.json"))
        g2 = emu2.load_graph(os.path.join(os.path.dirname(HERE), "graphs", "hh_d5.json"))
        rng = np.random.default_rng(3)
        cur = np.full(3000, np.uint64(g1["neel"]))
        allc = [cur.copy()]
        for step in range(12):
            e = rng.integers(0, len(g1["edges"]), size=len(cur))
            for r in range(len(cur)):
                i, j = g1["edges"][e[r]]
                if ((int(cur[r]) >> i) ^ (int(cur[r]) >> j)) & 1:
                    cur[r] ^= np.uint64((1 << i) | (1 << j))
            allc.append(cur.copy())
        C = np.unique(np.concatenate(allc))
        H1 = emu.build_H(C, g1, 1.3)
        cs = emu2.CSet(C.reshape(-1, 1), 57)
        self.assertTrue((cs.B[:, 0] == C).all())
        H2 = emu2.SubH(cs, g2, 1.3)
        self.assertLess(abs(H1 - (H2.A + __import__("scipy").sparse.diags(H2.diag))).max(), 1e-14)
        self.assertEqual(H1.nnz, H2.nnz)
        E1, a1 = emu.ground(H1)
        E2, a2 = emu2.ground(H2, v0=emu2.neel_start(cs, g2))
        self.assertLess(abs(E1 - E2), 1e-9)
        l1 = emu.diag_labels(C, a1, g1); l2 = emu2.diag_labels(cs, a2, g2)
        self.assertLess(abs(l1["m_s"] - l2["m_s"]), 1e-8)
        self.assertLess(np.max(np.abs(np.array(l1["Czz"]) - l2["Czz"])), 1e-8)
        self.assertLess(np.max(np.abs(np.array(l1["Zloop"]) - l2["Zloop"])), 1e-8)
        e1 = emu.label_errors(l1, l2); self.assertLess(e1["dZ"], 1e-5)

    def test_recover_noise_two_words(self):
        rng = np.random.default_rng(4)
        n, nd = 115, 48
        B = rng.integers(0, 2 ** 63, size=(4000, 2), dtype=np.uint64)
        B[:, 1] &= np.uint64((1 << 51) - 1)
        r = emu2.recover(B, n, nd, rng)
        self.assertTrue((emu2.popcount(r) == nd).all())
        w = emu2.popcount(B)
        up = w > nd
        self.assertTrue(((r[up] & ~B[up]) == 0).all())        # only 1 -> 0 where too many downs
        self.assertTrue(((B[~up] & ~r[~up]) == 0).all())      # only 0 -> 1 otherwise
        flips = emu2.popcount(r ^ B)
        self.assertTrue((flips == np.abs(w - nd)).all())
        x = emu2.add_noise(np.zeros((20000, 2), np.uint64), n, 0.1, rng)
        self.assertLess(abs(emu2.popcount(x).mean() / n - 0.1), 0.005)
        self.assertEqual(int((x[:, 1] >> np.uint64(51)).max()), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
