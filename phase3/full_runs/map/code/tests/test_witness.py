"""Unit tests of the witness pilot (DECLARATION.md SHA-256 529e8dcd..., §9). Toy graphs only (n <= 12).

1 graph JSON checks (d = 3, 5, 7); 2 TeNPy MPO energy of product states and DMRG ground energy == ED;
3 witness ground states of H - s*lam*O (O = M, Z_site, Z_aZ_b, loop string) == ED; 4 independent evaluator ==
dense state-vector contraction on TeNPy states and on random non-canonical MPS (with / without U(1) structure),
sector variance exact; 5 ED == dense eigh; 6 lambda search and hull logic.
"""
import json
import math
import os
import sys
import unittest
import warnings
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, CODE)
sys.path.insert(0, HERE)
warnings.filterwarnings("ignore")
import toygraphs as TG     # noqa: E402
import ed                  # noqa: E402
import hull                # noqa: E402
import indep_eval as IE    # noqa: E402
import hhmodel as HM       # noqa: E402

GRAPHS = os.path.join(CODE, "graphs")
TOYS = None


def toys():
    global TOYS
    if TOYS is None:
        TOYS = [TG.ring_pendant(), TG.hh3_prefix()]
    return TOYS


# ------------------------------------------------------------------ dense helpers (TeNPy physical basis order)
def dense_from_mps(Ts):
    v = Ts[0]
    for A in Ts[1:]:
        v = np.tensordot(v, A, axes=(v.ndim - 1, 0))
    return v.reshape([2] * len(Ts))          # legs (s0, ..., s_{n-1}); boundary dims are 1


def apply(psi, k, op):
    x = np.tensordot(op, psi, axes=(1, k))
    return np.moveaxis(x, 0, k)


def expect_string(psi, ops):
    phi = psi
    for k, op in ops:
        phi = apply(phi, k, op)
    return np.vdot(psi, phi) / np.vdot(psi, psi)


def dense_E(psi, G, Jz, b):
    E = 0.0
    for (i, j) in G["mps"]["edges"]:
        E += 0.5 * (expect_string(psi, [(i, b.SP), (j, b.SM)]) + expect_string(psi, [(i, b.SM), (j, b.SP)]))
        E += 0.25 * Jz * expect_string(psi, [(i, b.Z), (j, b.Z)])
    return E


def ed_field_diag(sec, G, label):
    if label == "m_s":
        return sec.M
    loc = G["local"]
    if label == "Z_bulk":
        return sec.z[:, loc["bulk_site"]].astype(float)
    if label == "Z_boundary":
        return sec.z[:, loc["boundary_site"]].astype(float)
    if label == "Czz_edge":
        a, b = loc["edge"]
        return (sec.z[:, a] * sec.z[:, b]).astype(float)
    if label == "Z_loop":
        return np.prod(sec.z[:, loc["loop"]].astype(float), axis=1)
    raise ValueError(label)


def dmrg_exact(G, Jz, field=None, start=None):
    M = HM.HHModel(G, Jz, field)
    psi = start.copy() if start is not None else HM.new_mps(M, HM.product_state(G, "neel"))
    opts = HM.dmrg_opts(chi_list={0: 16, 2: 64}, mixer=(1e-5, 2.0, 6), min_sweeps=8, max_sweeps=40,
                        max_E_err=1e-13, svd_min=1e-14, max_hours=0.1)
    return HM.run_dmrg(psi, M, opts)


class T1Graphs(unittest.TestCase):
    def test_graph_json(self):
        exp = {3: (19, 11, 8, 20, 25), 5: (57, 33, 24, 64, 87), 7: (115, 67, 48, 132, 185)}
        for d, (n, nu, nd, ne, n2) in exp.items():
            G = json.load(open(os.path.join(GRAPHS, "hh_d%d.json" % d)))
            self.assertEqual((G["n"], G["n_up"], G["n_down"], G["n_edges"], G["n_nn2"]), (n, nu, nd, ne, n2))
            for a, b in G["edges"]:
                self.assertNotEqual(G["colour"][a], G["colour"][b])
            self.assertEqual(sorted(G["order"]), list(range(n)))
            pos = {v: k for k, v in enumerate(G["order"])}
            prof = [sum(1 for a, b in G["edges"] if min(pos[a], pos[b]) < c <= max(pos[a], pos[b])) for c in range(1, n)]
            self.assertEqual(max(prof), G["max_crossing"])
            self.assertEqual(sum(G["mps"]["up_init"]), nu)
            self.assertEqual(G["sz"], (nu - nd) / 2)
        self.assertEqual(json.load(open(os.path.join(GRAPHS, "hh_d5.json")))["n_czz_outputs"], 151)
        self.assertEqual(json.load(open(os.path.join(GRAPHS, "hh_d7.json")))["n_czz_outputs"], 317)
        self.assertEqual(json.load(open(os.path.join(GRAPHS, "hh_d5.json")))["max_crossing_bfs_root0"], 7)
        self.assertEqual(json.load(open(os.path.join(GRAPHS, "hh_d7.json")))["max_crossing_bfs_root0"], 11)


class T2Energies(unittest.TestCase):
    def test_product_and_gs(self):
        rng = np.random.default_rng(1)
        for G in toys():
            n = G["n"]
            sec = ed.Sector(G, G["n_up"])
            for Jz in (1.2, 1.6, 2.5):
                M = HM.HHModel(G, Jz)
                for _ in range(3):
                    idx = rng.integers(sec.D)
                    st = sec.states[idx]
                    labels = ["up" if (st >> G["order"][k]) & 1 else "down" for k in range(n)]
                    psi = HM.new_mps(M, labels)
                    E = float(np.real(M.H_MPO.expectation_value(psi)))
                    self.assertAlmostEqual(E, 0.25 * Jz * sec.zz[idx], places=12)
                w, v, res = sec.lowest(sec.H(Jz), 1)
                psi, st = dmrg_exact(G, Jz)
                ev = HM.tenpy_eval(psi, G, Jz, M)
                self.assertLess(abs(ev["E"] - w[0]), 1e-9, (G["n"], Jz))
                m_ed = sec.expect_diag(v[:, 0], sec.M) / n
                self.assertLess(abs(ev["m_s"] - m_ed), 1e-7)


class T3Witness(unittest.TestCase):
    def test_fields(self):
        Jz = 1.6
        for G in toys():
            n = G["n"]
            sec = ed.Sector(G, G["n_up"])
            H = sec.H(Jz)
            M0 = HM.HHModel(G, Jz)
            labs = ["m_s", "Z_bulk", "Z_boundary", "Czz_edge"] + (["Z_loop"] if G["local"]["loop"] else [])
            for lab in labs:
                O = ed_field_diag(sec, G, lab)
                for sign in (+1, -1):
                    lam = 0.1 if lab == "m_s" else 0.4
                    import scipy.sparse as sp
                    w, v, res = sec.lowest((H - sp.diags(sign * lam * O)).tocsr(), 1)
                    p = v[:, 0]
                    E_ed = float(p @ (H @ p)); o_ed = float(p @ (O * p))
                    psi, st = dmrg_exact(G, Jz, HM.field_for(G, lab, sign, lam))
                    ev = HM.tenpy_eval(psi, G, Jz, M0)
                    o_t = ev["m_s"] * n if lab == "m_s" else ev[lab if lab != "Czz_edge" else "Czz_edge_loc"]
                    self.assertLess(abs(ev["E"] - E_ed), 1e-7, (n, lab, sign))
                    self.assertLess(abs(o_t - o_ed), 1e-7, (n, lab, sign))
                    self.assertLess(abs(st["E_dmrg"] - w[0]), 1e-8)


def random_mps(n, chi, rng, u1_target=None, sz_basis=(-0.5, 0.5)):
    up = sz_basis.index(0.5)
    if u1_target is None:
        dims = [1] + [min(chi, 2 ** min(k, n - k)) for k in range(1, n)] + [1]
        return [rng.standard_normal((dims[k], 2, dims[k + 1])) for k in range(n)]
    lab = []
    for k in range(n + 1):
        if k == 0:
            lab.append([0])
        elif k == n:
            lab.append([u1_target])
        else:
            us = [u for u in range(max(0, u1_target - (n - k)), min(k, u1_target) + 1)]
            lab.append([u for u in us for _ in range(2)][:chi])
    Ts = []
    for k in range(n):
        A = np.zeros((len(lab[k]), 2, len(lab[k + 1])))
        for a, ua in enumerate(lab[k]):
            for s in range(2):
                for b, ub in enumerate(lab[k + 1]):
                    if ub == ua + (1 if s == up else 0):
                        A[a, s, b] = rng.standard_normal()
        Ts.append(A)
    return Ts


class T4Indep(unittest.TestCase):
    def check(self, Ts, G, Jz, sz_basis, s):
        b = IE.Basis(sz_basis)
        psi = dense_from_mps(Ts)
        r = IE.evaluate(Ts, G, Jz, sz_basis, s=s)
        n = G["n"]
        self.assertLess(abs(r["norm"] - np.vdot(psi, psi).real), 1e-10 * max(1, abs(r["norm"])))
        self.assertLess(abs(r["norm_R"] - r["norm"]), 1e-10 * max(1, abs(r["norm"])))
        self.assertLess(abs(r["E"] - dense_E(psi, G, Jz, b).real), 1e-10)
        Z = [expect_string(psi, [(k, b.Z)]).real for k in range(n)]
        self.assertLess(abs(r["m_s"] - np.dot(G["mps"]["eta"], Z) / n), 1e-10)
        pos = {v: k for k, v in enumerate(G["order"])}
        for (i, j), val in zip(G["mps"]["nn2"], r["Czz_nn2"]):
            self.assertLess(abs(val - expect_string(psi, [(i, b.Z), (j, b.Z)]).real), 1e-10)
        if G["local"]["loop"]:
            sl = sorted(pos[v] for v in G["local"]["loop"])
            self.assertLess(abs(r["Z_loop"] - expect_string(psi, [(k, b.Z) for k in sl]).real), 1e-10)
        # sector variance, dense
        Sz = sum(0.5 * apply(psi, k, b.Z) for k in range(n))
        X = Sz - s * psi
        var = (np.vdot(X, X) / np.vdot(psi, psi)).real
        self.assertLess(abs(r["sector_var"] - var), 1e-9 * max(1, var))
        return r

    def test_tenpy_states(self):
        for G in toys():
            psi, st = dmrg_exact(G, 1.6, HM.field_for(G, "m_s", +1, 0.05))
            Ts = HM.export_tensors(psi)
            r = self.check(Ts, G, 1.6, HM.site_basis_meta(psi)["sz_basis"], G["sz"])
            self.assertEqual(r["sector_var"], 0.0)

    def test_random_noncanonical(self):
        rng = np.random.default_rng(7)
        G = toys()[0]
        n = G["n"]
        for basis in ((-0.5, 0.5), (0.5, -0.5)):
            Ts = random_mps(n, 6, rng)                          # no structure: several sectors
            r = self.check(Ts, G, 1.6, list(basis), G["sz"])
            self.assertGreater(r["sector_var"], 1e-3)
            tgt = G["n_up"]
            Ts = random_mps(n, 8, rng, u1_target=tgt, sz_basis=basis)
            Ts = [T * 1.7 for T in Ts]                          # unnormalised
            r = self.check(Ts, G, 1.6, list(basis), G["sz"])
            self.assertEqual(r["sector_var"], 0.0)


class T5ED(unittest.TestCase):
    def test_dense(self):
        for G in toys():
            sec = ed.Sector(G, G["n_up"])
            for Jz in (1.2, 2.5):
                H = sec.H(Jz)
                wd = np.linalg.eigh(H.toarray())[0]
                w, v, res = sec.lowest(H, 3)
                self.assertLess(np.max(np.abs(w - wd[:3])), 1e-10)
                self.assertLess(max(res), 1e-8)
                Ethr = w[0] + 0.012 * G["n"]
                m0 = sec.expect_diag(v[:, 0], sec.M) / G["n"]
                wp = ed.witness_at(sec, H, +1, Ethr, w[0], m0)
                self.assertLessEqual(min(abs(wp["E_lo"] - Ethr), abs(wp["E_hi"] - Ethr)), 1e-9)


class T6Hull(unittest.TestCase):
    def test_search_and_hull(self):
        a, b = 3.0, 2.0                       # E(lam) - E0 = a lam^2, o(lam) = o0 + b lam
        E0, o0 = -10.0, 0.5
        eps = 0.3; Ethr = E0 + eps
        ev = []
        while True:
            lam, why = hull.next_lambda(ev, E0, Ethr, 1e-6, eps, 0.005, 1.28, 0.1, 12)
            if lam is None:
                break
            ev.append((lam, E0 + a * lam ** 2))
        self.assertIn(why, ("bracketed", "N_max"))
        lo, hi = hull.bracket(ev, Ethr, 1e-6)
        self.assertLessEqual(E0 + a * lo ** 2, Ethr - 1e-6)
        self.assertGreater(E0 + a * hi ** 2, Ethr - 1e-6)
        pts = [dict(sid="gs", E=E0, o=o0)] + [dict(sid=str(l), E=E, o=o0 + b * l) for l, E in ev]
        v, comps = hull.extreme(pts, Ethr - 1e-6, +1)
        self.assertLessEqual(hull.mix_energy(comps), Ethr - 1e-6 + 1e-12)
        exact = o0 + b * math.sqrt((eps - 1e-6) / a)
        self.assertLessEqual(v, exact + 1e-12)
        self.assertGreater(v, exact - 0.01)
        # saturation
        ev2 = []
        while True:
            lam, why = hull.next_lambda(ev2, E0, Ethr, 1e-6, eps, 0.1, 6.4, 0.1, 7)
            if lam is None:
                break
            ev2.append((lam, E0 + 0.001 * min(lam, 1.0)))
        self.assertEqual(why, "saturated")
        # eps_star on a sqrt curve
        pts3 = [dict(sid="gs", E=0.0, o=0.0)] + [dict(sid=str(e), E=e, o=math.sqrt(e)) for e in hull.log_grid(1e-4, 1, 40)]
        pts3 += [dict(sid="m" + p["sid"], E=p["E"], o=-p["o"]) for p in pts3[1:]]
        es, D = hull.eps_star(pts3, 0.0, 0.2)
        self.assertLess(abs(D - 0.2), 1e-6)
        self.assertLess(abs(es - 0.01), 0.002)


if __name__ == "__main__":
    unittest.main(verbosity=2)
