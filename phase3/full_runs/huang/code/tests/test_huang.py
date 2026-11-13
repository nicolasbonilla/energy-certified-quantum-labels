"""Unit tests of the Huang-benchmark run on toy lattices (n <= 15; L = 2, 3 strips of width 5).

  python tests/test_huang.py            (from code/)
1. sector = global: the S^z-sector ground energy of H - lam*S*O equals the full-space one (SU(2) argument).
2. the ED ladder reproduces the exact information limit over ALL states (dense full space, Lagrange dual on a fine
   lambda grid): eps_tau within 1 %, widths at the targets within 1e-6.
3. indep_eval_h vs TeNPy vs ED: energy, correlators, norm, S^z moments (even and odd n).
4. end to end (toy dataset written in a temporary root): edref/edlab vs ref/lab (DMRG) for Cnn, Ccent, Cfar: eps_tau
   within 2 %, dataset gate G2 ~ 1e-10.
"""
import json
import math
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, CODE)
import numpy as np  # noqa: E402
import lattice as LT  # noqa: E402
import ed_h  # noqa: E402
import chain as CH  # noqa: E402


def rand_J(L, seed):
    return list(np.random.default_rng(seed).uniform(0, 2, len(LT.bonds(L))))


def full_ops(n):
    """Dense full-space sigma_i . sigma_j (all 2^n states; real): diag Z_i Z_j, 2 on antiparallel flips."""
    st = np.arange(2 ** n)
    bits = (st[:, None] >> np.arange(n)) & 1

    def sdot(i, j):
        M = np.diag(((2 * bits[:, i] - 1) * (2 * bits[:, j] - 1)).astype(float))
        idx = np.nonzero(bits[:, i] != bits[:, j])[0]
        M[st[idx] ^ ((1 << i) | (1 << j)), idx] = 2.0
        return M
    return sdot


def write_toy_dataset(root, L, k, seed):
    n = 5 * L
    J = rand_J(L, seed)
    sec = ed_h.Sector(n)
    Hm = sec.hamiltonian(LT.bonds(L), J)
    w, v, r = sec.lowest(Hm)
    psi = v[:, 0] / np.linalg.norm(v[:, 0])
    C = sec.all_corr(psi)
    d = os.path.join(root, "data_huang")
    os.makedirs(d, exist_ok=True)
    pre = os.path.join(d, "heisenberg_%dx5_id%d_" % (L, k))
    with open(pre + "couplings.txt", "w") as f:
        f.write("\n".join(repr(float(x)) for x in J) + "\n")
    with open(pre + "E.txt", "w") as f:
        f.write(repr(float(w[0]) / 2.0) + "\n")
    with open(pre + "SvN.txt", "w") as f:
        f.write("0.0\n")
    for kind in ("XX", "YY", "ZZ"):
        np.savetxt(pre + kind + ".txt", C, delimiter="\t")
    return J, float(w[0]), C


class T1Sector(unittest.TestCase):
    def test_sector_equals_global(self):
        L = 2
        n = 10
        J = rand_J(L, 1)
        B = LT.bonds(L)
        sdot = full_ops(n)
        Hf = sum(c * sdot(i, j) for (i, j), c in zip(B, J))
        sec = ed_h.Sector(n)
        Hs = sec.hamiltonian(B, J)
        self.assertAlmostEqual(np.linalg.eigvalsh(Hf)[0], sec.lowest(Hs)[0][0], places=9)
        for label in ("Cnn", "Ccent", "Cfar", "P_0_9", "Cd2", "Cstag"):
            P, Wt, S, ob = LT.label_pairs(L, label)
            Gf = sum(w_ * sdot(i, j) / 3.0 for (i, j), w_ in zip(P, Wt))
            Gs = sec.sdots(P, [w_ / 3.0 for w_ in Wt])
            for lam in (0.05, 0.7, 3.0, 12.0):
                for sg in (1, -1):
                    ef = np.linalg.eigvalsh(Hf - sg * lam * Gf)[0]
                    es = sec.lowest((Hs - sg * lam * Gs).tocsr())[0][0]
                    self.assertAlmostEqual(ef, es, places=8, msg=(label, lam, sg))


def exact_width(Hf, Gf, S, E, ob):
    """Exact o+-(E) by the Lagrange dual on a fine lambda grid plus golden refinement (dense sector matrices; by T1 the
    sector dual equals the full-space dual, so this is the limit over ALL states)."""
    E0 = np.linalg.eigvalsh(Hf)[0]

    def dual(sign, lam):
        return (E - np.linalg.eigvalsh(Hf - sign * lam * Gf)[0]) / (lam * S)
    out = {}
    for sign in (1, -1):
        grid = np.geomspace(1e-4, 200, 240)
        vals = [dual(sign, l) for l in grid]
        i = int(np.argmin(vals))
        a, b = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
        for _ in range(80):
            m1, m2 = a + 0.382 * (b - a), a + 0.618 * (b - a)
            if dual(sign, m1) < dual(sign, m2):
                b = m2
            else:
                a = m1
        v = min(dual(sign, 0.5 * (a + b)), min(vals))
        out[sign] = min(v, ob[1]) if sign > 0 else min(v, -ob[0])
    return out[1] + out[-1], E0


class T2Ladder(unittest.TestCase):
    def test_ladder_exact(self):
        L, n = 2, 10
        J = rand_J(L, 2)
        B = LT.bonds(L)
        sec = ed_h.Sector(n)
        Hs = sec.hamiltonian(B, J)
        Hf = Hs.toarray()
        w, v, r = sec.lowest(Hs)
        E0 = float(w[0])
        psi = v[:, 0]
        for label in ("Cnn", "Ccent", "Cfar"):
            P, Wt, S, ob = LT.label_pairs(L, label)
            Gs = sec.sdots(P, [w_ / 3.0 for w_ in Wt])
            Gf = Gs.toarray()
            o0 = float(psi @ (Gs @ psi)) / S
            solver = ed_h.LabelSolver(sec, Hs, Gs, S)

            def solve(sign, lam, why):
                d = solver.solve(sign, lam); d.pop("psi"); d["F_lo"] = d["F"] - d["residual"]; return d
            lam0, lam_max = (0.005, 6.4) if label == "Cnn" else (0.1, 25.6)
            tau = 0.08
            lad = CH.Ladder(solve, E0, o0, S, ob, tau, lam0, lam_max, 16)
            targets = [(n * d, False) for d in (1e-3, 3e-3, 1e-2, 3e-2)]
            summ = lad.run(targets, 20 * n * 1e-2)
            pool = CH.pool_of(E0, o0, lad.points())
            for e, _ in targets:
                wex, _ = exact_width(Hf, Gf, S, E0 + e, ob)
                wi = CH.w_in(pool, E0 + e)
                wo = CH.w_out(lad.points(), E0 + e, S, ob)
                self.assertLessEqual(wi, wex + 1e-9, (label, e))
                self.assertGreaterEqual(wo, wex - 1e-9, (label, e))
                self.assertLess(wo - wi, 0.02 * wex + 1e-9, (label, e, wi, wo, wex))
            # exact eps_tau by bisection on the exact width
            lo, hi = 1e-7, 20 * n * 1e-2
            if exact_width(Hf, Gf, S, E0 + hi, ob)[0] >= tau:
                for _ in range(50):
                    m = math.sqrt(lo * hi)
                    if exact_width(Hf, Gf, S, E0 + m, ob)[0] >= tau:
                        hi = m
                    else:
                        lo = m
                self.assertLess(abs(summ["eps_tau_in"] / hi - 1), 0.01, (label, summ, hi))
                self.assertLess(abs(summ["eps_tau_out"] / hi - 1), 0.01, (label, summ, hi))
                self.assertGreaterEqual(summ["eps_tau_in"], hi * (1 - 1e-6))
                self.assertLessEqual(summ["eps_tau_out"], hi * (1 + 1e-6))


class T3Evaluator(unittest.TestCase):
    def test_eval(self):
        import hmodel as HM
        import indep_eval_h as IE
        for L, seed in ((2, 3), (3, 4)):
            n = 5 * L
            J = rand_J(L, seed)
            B = LT.bonds(L)
            sec = ed_h.Sector(n)
            Hs = sec.hamiltonian(B, J)
            w, v, r = sec.lowest(Hs)
            Ce = sec.all_corr(v[:, 0] / np.linalg.norm(v[:, 0]))
            M = HM.HeisModel(n, B, J)
            psi = HM.new_mps(M, HM.neel_labels(n))
            psi, st = HM.run_dmrg(psi, M, HM.dmrg_opts(chi_list={0: 16, 2: 64, 4: 128}, min_sweeps=10, max_sweeps=30,
                                                       max_E_err=1e-13, svd_min=1e-14))
            pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
            tev = HM.tenpy_eval(psi, M, pairs)
            Ts = HM.export_tensors(psi)
            iev = IE.evaluate(Ts, HM.sz_basis(psi), B, J, pairs)
            self.assertAlmostEqual(tev["E"], iev["E"], places=9)
            self.assertAlmostEqual(iev["E"], float(w[0]), places=7)
            self.assertAlmostEqual(iev["norm"], tev["overlap"], places=9)
            self.assertLess(abs(iev["sz_var"]), 1e-10)
            self.assertAlmostEqual(iev["sz_mean"], 0.5 * (n % 2), places=10)
            for (i, j) in pairs:
                self.assertAlmostEqual(iev["C"]["%d_%d" % (i, j)], Ce[i, j], places=6)
                self.assertAlmostEqual(iev["C"]["%d_%d" % (i, j)], tev["C"]["%d_%d" % (i, j)], places=9)
            # a field model: <H - lam G> of the DMRG state vs ED
            P, Wt, S, ob = LT.label_pairs(L, "Ccent")
            M2 = HM.HeisModel(n, B, J, HM.field_terms(P, Wt, +1, 1.5))
            psi2, st2 = HM.run_dmrg(psi.copy(), M2, HM.dmrg_opts(chi_max=128, min_sweeps=6, max_sweeps=30,
                                                                 max_E_err=1e-13, svd_min=1e-14))
            Gs = sec.sdots(P, [w_ / 3.0 for w_ in Wt])
            ee = sec.lowest((Hs - 1.5 * Gs).tocsr())[0][0]
            self.assertAlmostEqual(st2["E_dmrg"], ee, places=7)


class T4EndToEnd(unittest.TestCase):
    def test_end_to_end(self):
        import witness as WT
        root = tempfile.mkdtemp(prefix="huang_toy_")
        try:
            L, k = 2, 1
            J, E0, C = write_toy_dataset(root, L, k, 7)
            WT.task_edref(root, L, k)
            ref = json.load(open(os.path.join(root, "out", "ed", "ref_L2_k1.json")))
            self.assertLess(ref["max_dC_vs_XX"], 1e-9)
            self.assertLess(abs(ref["dE_vs_file"]), 1e-9)
            WT.task_ref(root, L, k)
            r2 = json.load(open(os.path.join(root, "out", "refs", "ref_L2_k1.json")))
            self.assertLess(abs(r2["E0"] - E0), 1e-8)
            self.assertLess(r2["max_dC_vs_XX"], 1e-6)
            for lab in ("Cnn", "Ccent", "Cfar"):
                WT.task_edlab(root, L, k, lab)
                WT.task_lab(root, L, k, lab)
                a = json.load(open(os.path.join(root, "out", "ed", "chains", "L2_k1_%s.json" % lab)))
                b = json.load(open(os.path.join(root, "out", "chains", "L2_k1_%s.json" % lab)))
                for key in ("eps_tau_in", "eps_tau_out"):
                    if a[key] and b[key]:
                        self.assertLess(abs(b[key] / a[key] - 1), 0.02, (lab, key, a[key], b[key]))
                self.assertLess(abs(b["chi_two"] / a["chi_two"] - 1), 1e-3, lab)
            WT.task_edpairs(root, L, k, 0)
            WT.task_chk(root, L, k, "Ccent", "+")
            WT.task_cold(root, L, k, "Ccent", "-")
            c = json.load(open(os.path.join(root, "out", "cold", "cold_L2_k1_Ccent_-.json")))
            self.assertFalse(c["flag_warm_stuck"])
            WT.task_lawscan(root, L, k, 0)
            WT.make_plan(os.path.join(root, "plan.json"))
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
