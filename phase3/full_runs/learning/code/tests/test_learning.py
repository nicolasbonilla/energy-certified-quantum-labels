"""Unit tests of the learning run (toys only; nothing from the benchmark's n = 20 data).

  python -I -B tests/test_learning.py [TestName ...]
T1Conformal   split conformal on a synthetic problem with known coverage: mean coverage = ceil(0.9 (m+1))/(m+1)
              (= 19/21 for m = 20) within Monte Carlo error; the certified variants cover the truth at >= 0.9
T2Model       the numpy kernel ridge reimplementation equals sklearn's KernelRidge and cross_val_score (if sklearn is
              importable; laptop only); Dirichlet features equal a literal transcription of the notebook loop
T3Band        exactness of the interval propagation through a linear predictor
T4Generator   truncated-subspace generator on a 2 x 5 toy: RR energy non-increasing in the prefix, full prefix = E0,
              matched delta e, captured weight
T5Witness     on a 2 x 5 toy, the certified interval contains the exact information limit (dense scan over lambda),
              the adversarial label lies inside it and every random window state's label lies inside it
"""
import math
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import conf_l as CF  # noqa: E402
import models_l as ML  # noqa: E402
import lattice as LT  # noqa: E402


class T1Conformal(unittest.TestCase):
    def test_split_conformal_exact_coverage(self):
        rng = np.random.default_rng(1)
        reps, m, nte, alpha = 4000, 20, 50, 0.1
        covs, covc, covb = [], [], []
        for _ in range(reps):
            x = rng.uniform(-2, 2, size=m + nte)
            y = np.sin(x) + 0.3 * rng.standard_normal(m + nte)
            f = np.sin(x) + 0.1 * x            # a fixed (biased) predictor
            sc = np.abs(y[:m] - f[:m])[:, None]
            q = CF.qhat(sc, alpha)[0]
            covs.append(np.mean(np.abs(y[m:] - f[m:]) <= q))
            # certified: interval labels that contain the truth, of random width and position
            w = rng.uniform(0, 0.5, size=m + nte)
            u = rng.uniform(0, 1, size=m + nte)
            lo, hi = y - u * w, y + (1 - u) * w
            scc = np.maximum(np.abs(f[:m] - lo[:m]), np.abs(f[:m] - hi[:m]))[:, None]
            qc = CF.qhat(scc, alpha)[0]
            covc.append(np.mean(np.abs(y[m:] - f[m:]) <= qc))
            # band version with a constant band [f - 0.05, f + 0.05]
            flo, fhi = f - 0.05, f + 0.05
            sb = np.maximum(0, np.maximum(hi[:m] - fhi[:m], flo[:m] - lo[:m]))[:, None]
            qb = CF.qhat(sb, alpha)[0]
            covb.append(np.mean((y[m:] >= flo[m:] - qb) & (y[m:] <= fhi[m:] + qb)))
        expect = math.ceil(0.9 * (m + 1)) / (m + 1)
        se = 0.30 / math.sqrt(reps)   # generous: sd of a per-rep coverage is <= ~0.1-0.3
        print("T1: SC mean coverage %.4f (expected %.4f), certified %.4f, band %.4f" % (
            np.mean(covs), expect, np.mean(covc), np.mean(covb)))
        self.assertLess(abs(np.mean(covs) - expect), 4 * se)
        self.assertGreater(np.mean(covc), 0.9 - 4 * se)
        self.assertGreater(np.mean(covb), 0.9 - 4 * se)

    def test_qhat_index(self):
        s = np.arange(1, 21, dtype=float)[:, None]
        self.assertEqual(CF.qhat(s, 0.1)[0], 19.0)
        self.assertTrue(np.isinf(CF.qhat(np.arange(5.0)[:, None], 0.1)[0]))


class T2Model(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(3)
        self.X = rng.uniform(0, 2, size=(70, 31))
        self.y = np.cos(self.X[:, 0]) - 0.5 * self.X[:, 3] * self.X[:, 4] + 0.1 * rng.standard_normal(70)

    def test_dirichlet_literal(self):
        X = self.X
        lit = np.zeros((len(X), X.shape[1] * 5))
        for i, x1 in enumerate(X):
            cnt = 0
            for k in range(len(x1)):
                for k1 in range(-2, 3):
                    lit[i, cnt] += np.cos(np.pi * k1 * x1[k])
                    cnt += 1
        for i in range(len(lit)):
            lit[i] /= np.linalg.norm(lit[i])
        self.assertLess(np.abs(lit - ML.dirichlet_features(X)).max(), 1e-14)

    def test_against_sklearn(self):
        try:
            from sklearn.kernel_ridge import KernelRidge
            from sklearn.model_selection import cross_val_score
        except Exception:
            self.skipTest("sklearn not importable")
        X, y = self.X, self.y
        bank, combos = ML.bank_m1(X)
        tr, q = np.arange(50), np.arange(50, 70)
        Wt = ML.weights(bank, combos, tr, q)
        F = ML.dirichlet_features(X)
        Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
        worst, worst_cv = 0.0, 0.0
        best, scores = ML.cv_select(bank, combos, tr, y[tr][:, None])
        for c, (kk, al) in enumerate(combos):
            if kk == "dir":
                mdl = KernelRidge(kernel="linear", alpha=al).fit(F[tr], y[tr])
                p = mdl.predict(F[q])
                cv = -np.mean(cross_val_score(KernelRidge(kernel="linear", alpha=al), F[tr], y[tr], cv=5,
                                              scoring="neg_root_mean_squared_error"))
            else:
                mdl = KernelRidge(kernel="rbf", alpha=al).fit(Xn[tr], y[tr])
                p = mdl.predict(Xn[q])
                cv = -np.mean(cross_val_score(KernelRidge(kernel="rbf", alpha=al), Xn[tr], y[tr], cv=5,
                                              scoring="neg_root_mean_squared_error"))
            worst = max(worst, np.abs(Wt[c] @ y[tr] - p).max())
            worst_cv = max(worst_cv, abs(cv - scores[c, 0]))
        # M2 (local additive kernel): weights equal sklearn KernelRidge with the precomputed Gram matrix
        bank2, combos2 = ML.bank_m2(X[:, :31], "P_7_12", 4)
        W2 = ML.weights(bank2, combos2, tr, q)
        for c, (kk, al) in enumerate(combos2):
            Kp = bank2[kk]
            mdl = KernelRidge(kernel="precomputed", alpha=al).fit(Kp[np.ix_(tr, tr)], y[tr])
            worst = max(worst, np.abs(W2[c] @ y[tr] - mdl.predict(Kp[np.ix_(q, tr)])).max())
        best = combos[best[0]]
        print("T2: max |pred - sklearn| = %.2e (M1 and M2), max |cv - sklearn| = %.2e, selected %s" % (
            worst, worst_cv, best))
        self.assertLess(worst, 1e-9)
        self.assertLess(worst_cv, 1e-9)


class T3Band(unittest.TestCase):
    def test_band_exact(self):
        rng = np.random.default_rng(5)
        A = rng.standard_normal((7, 30))
        lo = rng.uniform(-1, 0, size=(30, 2))
        hi = lo + rng.uniform(0, 0.5, size=(30, 2))
        flo, fhi = CF.band(A, lo, hi)
        for _ in range(2000):
            u = rng.uniform(size=(30, 2))
            v = A @ (lo + u * (hi - lo))
            self.assertTrue(np.all(v >= flo - 1e-12) and np.all(v <= fhi + 1e-12))
        vert = np.where(A[:, :, None] > 0, hi[None], lo[None])   # maximizing vertex per row
        top = np.einsum("qt,qtm->qm", A, vert)
        self.assertLess(np.abs(top - fhi).max(), 1e-12)


def toy_setup(L=2, seed=11):
    import ed_h
    rng = np.random.default_rng(seed)
    B = LT.bonds(L)
    J = rng.uniform(0, 2, size=len(B))
    sec = ed_h.Sector(L * LT.W)
    H = sec.hamiltonian(B, J)
    return sec, H, B, J


class T4Generator(unittest.TestCase):
    def test_generator(self):
        import task_l as TK
        sec, H, B, J = toy_setup()
        n = sec.n
        w, v = np.linalg.eigh(H.toarray())
        E0, psi0 = w[0], v[:, 0]
        order, T, p = TK.gen_order(psi0, 99)
        Es = []
        for k in range(1, sec.D + 1, 7):
            Es.append(TK.rr_ground(H, np.sort(order[:k]))[0])
        self.assertTrue(all(Es[i + 1] <= Es[i] + 1e-10 for i in range(len(Es) - 1)))
        self.assertLess(abs(TK.rr_ground(H, np.arange(sec.D))[0] - E0), 1e-10)
        for de in (1e-3, 5e-3, 2e-2):
            g, psig = TK.generator(sec, H, E0, psi0, n, de, order, T, p)
            self.assertLessEqual(g["de_gen"], de + 1e-12)
            if g["de_prev"] is not None:
                self.assertGreater(g["de_prev"], de)
            self.assertLess(abs(float(psig @ (H @ psig)) - g["E_gen"]), 1e-9)
            print("T4: de=%.0e D=%d/%d de_gen=%.3e W=%.4f" % (de, g["D_sub"], sec.D, g["de_gen"],
                                                              g["captured_weight"]))


class T5Witness(unittest.TestCase):
    def test_witness_bounds(self):
        import task_l as TK
        import labels_l as LB
        sec, H, B, J = toy_setup(seed=13)
        n = sec.n
        Hd = H.toarray()
        w, v = np.linalg.eigh(Hd)
        E0, psi0 = w[0], v[:, 0]
        C0 = sec.all_corr(psi0)
        rng = np.random.default_rng(17)
        for lab in ["Cnn", "Cstag", LT.nn_pair_labels(2)[3], LT.pair_label(*LT.diag_pairs(2)[1])]:
            P, Wt, S, ob = LT.label_pairs(2, lab)
            G = sec.sdots(P, [x / 3.0 for x in Wt])
            Gd = G.toarray()
            o0 = TK.label_value(C0, 2, lab)
            pts = []
            for sign in (+1, -1):
                pts += TK.witness_points(sec, H, E0, o0, G, S, sign, [n * 1e-3, n * 5e-3], TK.chi_guess(lab))
            wrec = dict(S=S, obounds=list(ob), o_GS=o0, points=pts)
            lams = np.geomspace(1e-3, 50, 300)
            Fp, Fm, pool = [], [], {+1: [dict(sid="gs", E=E0, o=o0)], -1: [dict(sid="gs", E=E0, o=o0)]}
            for i, l in enumerate(lams):
                for sg, lst in ((+1, Fp), (-1, Fm)):
                    ww, vv = np.linalg.eigh(Hd - sg * l * Gd)
                    lst.append(ww[0])
                    x = vv[:, 0]
                    pool[sg].append(dict(sid="%d" % i, E=float(x @ Hd @ x), o=float(x @ Gd @ x) / S))
            Fp, Fm = np.array(Fp), np.array(Fm)
            import hull
            for de in (1e-3, 5e-3):
                E = E0 + n * de
                lo, hi = LB.cert_interval(wrec, E)
                out_hi = min(ob[1], np.min((E - Fp) / (lams * S)))        # grid bound: >= exact limit
                out_lo = max(ob[0], -np.min((E - Fm) / (lams * S)))
                in_hi = hull.extreme(pool[+1], E, +1)[0]                   # attained: <= exact limit
                in_lo = hull.extreme(pool[-1], E, -1)[0]
                self.assertLessEqual(in_hi, out_hi + 1e-9)
                self.assertGreaterEqual(hi, in_hi - 1e-9)                  # validity of our bound
                self.assertLessEqual(lo, in_lo + 1e-9)
                wex = out_hi - out_lo
                self.assertLessEqual(hi, out_hi + 0.05 * wex)              # tightness (5 % of the width)
                self.assertGreaterEqual(lo, out_lo - 0.05 * wex)
                ex_lo, ex_hi = in_lo, in_hi
                for s_ in (+1, -1):
                    av, _ = LB.adversarial(wrec, E0, E, s_)
                    self.assertTrue(out_lo - 1e-9 <= av <= out_hi + 1e-9)
                # random window states: mixtures of the lowest eigenstates with <H> <= E
                kk = 12
                for _ in range(300):
                    c = rng.dirichlet(np.ones(kk) * 0.3)
                    c[0] += 0.0
                    Eav = float(c @ w[:kk])
                    if Eav > E:
                        t = (E - E0) / (Eav - E0)
                        c = t * c
                        c[0] += 1 - t
                    oav = float(sum(c[i] * (v[:, i] @ Gd @ v[:, i]) for i in range(kk)) / S)
                    self.assertTrue(lo - 1e-9 <= oav <= hi + 1e-9)
                print("T5: %s de=%.0e cert [%.6f, %.6f]; exact limit within [%.6f, %.6f] (attained) and "
                      "[%.6f, %.6f] (grid bound); loss vs attained %.3f%%" % (
                          lab, de, lo, hi, in_lo, in_hi, out_lo, out_hi, 100 * ((hi - lo) / (in_hi - in_lo) - 1)))


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]] + sys.argv[1:], verbosity=1)
