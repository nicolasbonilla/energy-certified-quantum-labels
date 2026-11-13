"""MAP unit tests on toy graphs (n <= 12, exact dense diagonalization; laptop and VM).

1 Czz_bar field == Jz shift (TeNPy ground state of H(Jz - 4 sign lam) vs ED of H - sign lam sum ZZ).
2 predict_lam on synthetic eps(lam) curves (quadratic, steep, saturating).
3 End to end on a toy (task_ref, task_thr, task_lab for all seven labels at a training and an OOD point, then
  analyze_map.row): inner <= exact <= outer at E_lo, E_dig, E_up; both within 2e-3 of the exact information limit
  at E_lo (straddled) and within 2e-3 + 3 % (inner) / + 1 % (outer) at E_dig, E_up;
  eps_tau (inner and outer) within 5 % of the exact one; every state in the sector.
"""
import itertools
import json
import math
import os
import shutil
import sys
import tempfile
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
import witness as W        # noqa: E402


def dense_sector(G):
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
    return A, z, zz


def diag_label(G, z, label):
    loc = G["local"]
    if label == "m_s":
        return (z * np.array(G["eta"], float)).sum(1) / G["n"]
    if label == "Czz_bar":
        return sum(z[:, i] * z[:, j] for (i, j) in G["edges"]) / len(G["edges"])
    if label == "C2_bar":
        return sum(z[:, i] * z[:, j] for (i, j) in G["nn2"]) / len(G["nn2"])
    if label == "Z_bulk":
        return z[:, loc["bulk_site"]].copy()
    if label == "Z_boundary":
        return z[:, loc["boundary_site"]].copy()
    if label == "Czz_edge":
        a, b = loc["edge"]
        return z[:, a] * z[:, b]
    if label == "Z_loop":
        return np.prod(z[:, loc["loop"]], axis=1)
    raise ValueError(label)


_CURVES = {}


def exact_extreme(H, O, sign, E, refine=True):
    """Exact sign-extreme of <O> at <H> <= E: ground-state curve of H - sign*lam*O on a log grid of lam (cached), then
    bisection in lam inside the bracketing grid interval (refine=True: exact; refine=False: grid chord, < 1e-4)."""
    key = (id(H), id(O), sign)
    if key not in _CURVES:
        import scipy.linalg as sl
        lams = np.concatenate([[0.0], np.geomspace(1e-4, 2e3, 400)])
        Es, os_ = [], []
        for lam in lams:
            w, v = sl.eigh(H - sign * lam * np.diag(O), subset_by_index=[0, 0], driver="evr")
            p = v[:, 0]
            Es.append(float(p @ H @ p)); os_.append(float(p ** 2 @ O))
        _CURVES[key] = (np.array(Es), np.array(os_))
        _CURVES[key + ("lam",)] = lams
    Es, os_ = _CURVES[key]
    if E >= Es[-1]:
        return os_[-1]
    k = int(np.searchsorted(Es, E, side="right"))      # Es nondecreasing in lam
    if k == 0:
        return os_[0]
    lams = _CURVES[key + ("lam",)]
    lo, hi = (lams[k - 1], Es[k - 1], os_[k - 1]), (lams[k], Es[k], os_[k])
    if refine:                                          # exact: bisection inside the bracketing grid interval
        import scipy.linalg as sl
        for _ in range(45):
            if hi[1] - lo[1] < 1e-13:
                break
            m = 0.5 * (lo[0] + hi[0])
            w, v = sl.eigh(H - sign * m * np.diag(O), subset_by_index=[0, 0], driver="evr")
            p = v[:, 0]
            pt = (m, float(p @ H @ p), float(p ** 2 @ O))
            if pt[1] <= E:
                lo = pt
            else:
                hi = pt
    t = (E - lo[1]) / (hi[1] - lo[1]) if hi[1] > lo[1] else 0.0
    return (1 - t) * lo[2] + t * hi[2]


class T1Czz(unittest.TestCase):
    def test_czz_shift(self):
        G = TG.ring_two_pendants(10)
        A, z, zz = dense_sector(G)
        Jz, lam = 2.5, 0.07
        for sign in (+1, -1):
            Hd = A + np.diag(0.25 * Jz * zz - sign * lam * zz)
            e_ed = np.linalg.eigvalsh(Hd)[0]
            M = W.model_for(G, Jz, "Czz_bar", sign, lam)
            psi = HM.new_mps(M, HM.product_state(G, "neel"))
            psi, st = HM.run_dmrg(psi, M, HM.dmrg_opts(chi_max=64, max_sweeps=30, min_sweeps=6, max_E_err=1e-13,
                                                       svd_min=1e-14))
            self.assertAlmostEqual(st["E_dmrg"], e_ed, delta=1e-9)


class T2Predict(unittest.TestCase):
    def test_predict(self):
        E0 = -5.0
        for f, lam_true in ((lambda l: 3.0 * l * l, None), (lambda l: 0.5 * l ** 3.5, None),
                            (lambda l: 1 - math.exp(-l), None)):
            pts = [(0.005, E0 + f(0.005))]
            target = f(0.3)
            for _ in range(4):
                lam = W.predict_lam(pts, E0, target, None, 1.0, 0.005, 10.0)
                pts.append((lam, E0 + f(lam)))
            self.assertLess(abs(f(pts[-1][0]) / target - 1), 0.06)


class T3EndToEnd(unittest.TestCase):
    def test_lab_vs_exact(self):
        import analyze_map as AM
        root = tempfile.mkdtemp(prefix="maptest_")
        try:
            os.makedirs(os.path.join(root, "code", "graphs"))
            G = TG.ring_two_pendants(10)
            json.dump(G, open(os.path.join(root, "code", "graphs", "hh_d5.json"), "w"))
            for d in (3, 7):
                shutil.copy(os.path.join(CODE, "graphs", "hh_d%d.json" % d), os.path.join(root, "code", "graphs"))
            # readings: eps_dig = r1 * gap1 chosen so that the per-site window is moderate on the toy
            RD = dict(r1={"57_2.0": 0.05}, gap1={"57_2.0": 1.0, "57_1.2": 0.2}, eps1={}, r2={}, gap2={}, eps2={})
            json.dump(RD, open(os.path.join(root, "code", "readings_declared.json"), "w"))
            A, z, zz = dense_sector(G)
            for J in (2.0, 1.2):
                for kind in ("R1a", "R2", "R3", "R4"):
                    W.task_ref(root, 57, J, kind)
                W.task_thr(root, 57, J)
                for label in W.LABELS:
                    W.task_lab(root, 57, J, label)
            D = AM.Data(root)
            OS = {label: diag_label(G, z, label) for label in W.LABELS}
            HS = {J: A + np.diag(0.25 * J * zz) for J in (2.0, 1.2)}
            for J in (2.0, 1.2):
                H = HS[J]
                E0x = np.linalg.eigvalsh(H)[0]
                thr = D.thr(57, J)
                self.assertAlmostEqual(thr["E0"], E0x, delta=1e-8)
                for label in W.LABELS:
                    O = OS[label]
                    r = AM.row(D, 57, J, label)
                    for k in ("lo", "dig", "up"):
                        E = E0x + thr["eps_" + k]
                        wx = exact_extreme(H, O, +1, E) - exact_extreme(H, O, -1, E)
                        a = r["at_" + k]
                        self.assertLessEqual(a["w_in"], wx + 1e-7, (J, label, k))
                        self.assertGreaterEqual(a["w_out"], wx - 1e-7, (J, label, k))
                        tin = 2e-3 if k == "lo" else 2e-3 + 0.03 * wx     # declared accuracy (G1: 1 % / 3 %)
                        tout = 2e-3 if k == "lo" else 2e-3 + 0.01 * wx
                        self.assertLess(wx - a["w_in"], tin, (J, label, k, wx, a["w_in"]))
                        self.assertLess(a["w_out"] - wx, tout, (J, label, k, wx, a["w_out"]))
                    w0 = np.linalg.eigh(H)[1][:, 0]
                    tau = 0.06 * abs(float(w0 ** 2 @ O))

                    def wd(e):
                        return exact_extreme(H, O, +1, E0x + e, False) - exact_extreme(H, O, -1, E0x + e, False)
                    a_, b_ = 1e-7, max(r["eps_max_computed"], 1e-6)
                    if wd(b_) >= tau and r["eps_tau_in"] and r["eps_tau_out"] and r["eps_tau_out"] > 2e-7:
                        for _ in range(50):
                            m = math.sqrt(a_ * b_)
                            if wd(m) >= tau:
                                b_ = m
                            else:
                                a_ = m
                        self.assertLess(abs(r["eps_tau_in"] / b_ - 1), 0.05, (J, label, r["eps_tau_in"], b_))
                        self.assertLess(abs(r["eps_tau_out"] / b_ - 1), 0.05, (J, label, r["eps_tau_out"], b_))
            for s in D.states.values():
                if abs(s["sector_s"] - G["sz"]) < 1e-9:
                    self.assertTrue(s["in_sector"])
                    self.assertLess(s["agree"]["dE"], 1e-8)
        finally:
            shutil.rmtree(root, ignore_errors=True)


class T4ToeplitzHausdorff(unittest.TestCase):
    def test_th_pure_witness(self):
        import json as _j
        import th_witness as TH
        import indep_eval as IE
        G = TG.ring_two_pendants(10)
        Jz = 1.6
        root = tempfile.mkdtemp(prefix="thtest_")
        try:
            paths = []
            for sign, lam in ((+1, 0.0), (+1, 0.2)):
                M = W.model_for(G, Jz, "m_s", sign, lam)
                psi = HM.new_mps(M, HM.product_state(G, "neel"))
                psi, st = HM.run_dmrg(psi, M, HM.dmrg_opts(chi_max=32, max_sweeps=30, min_sweeps=6,
                                                           max_E_err=1e-13, svd_min=1e-14))
                p = os.path.join(root, "s%d" % len(paths))
                HM.save_state(psi, p, dict(n=G["n"], order=G["order"], Jz=Jz, sid="t"), pkl=False)
                paths.append(p + ".npz")
            gp = os.path.join(root, "g.json")
            _j.dump(G, open(gp, "w"))
            outp = os.path.join(root, "th.json")
            TH.main(gp, Jz, "m_s", paths[0], 0.4, paths[1], 0.6, 0.0, outp)
            r = _j.load(open(outp))
            self.assertLess(abs(r["dE_pure_mix"]), 1e-9)
            self.assertLess(abs(r["dO_pure_mix"]), 1e-9)
            self.assertLess(r["pure"]["sector_var"], 1e-12)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
