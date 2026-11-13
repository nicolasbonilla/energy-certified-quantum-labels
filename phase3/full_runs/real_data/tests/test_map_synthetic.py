# real_data / tests / test_map_synthetic.py  (own code; 2026-11-12; task rd-code-map)
#
# Unit tests of the map code on SYNTHETIC cases with known answers (test (e) of the task; no real datum; every file
# opened is recorded and the module fails if one of them lies in converted/):
#   - the guard (no DECLARATION.sha256, wrong hash, tampered file) and the schema loader;
#   - the exact interval on a two-site model whose certificates are known in closed form, including out-of-sector
#     mixtures with q > 0 where the bound is exactly tight, pairs combined by concavity, the Czz_bar rule, caps,
#     allowances, both tolerances, the exact root of the largest energy;
#   - the NOT CERTIFIED side with q > 0 and q < 0, the re-evaluated pools and the linear rule on stored states
#     (against the stored reference energies and against stored tensors with the independent evaluator);
#   - every gate G1-G7 (pass and fail), "no decision", J*, relations, factors, filter, nested sets;
#   - one end-to-end run of run_map.run() on a synthetic data set made of genuine mixtures of stored states.
# Run:  python -B -I test_map_synthetic.py      (about one minute)
import builtins
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Fr
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(os.path.dirname(HERE), "code")
sys.path.insert(0, CODE)
sys.dont_write_bytecode = True

import map_common as C      # noqa: E402
import map_certs as MC      # noqa: E402
import map_gates as MG      # noqa: E402
import map_stored as MS     # noqa: E402
import map_tables as T      # noqa: E402
import run_map as RM        # noqa: E402

S = None
LOADED = None
OPENED_CONVERTED = []
_real_open = builtins.open
CONV = os.path.normcase(os.path.join(C.RD, "converted")) + os.sep


def _spy_open(file, *a, **k):
    if isinstance(file, (str, bytes, os.PathLike)):
        p = os.path.normcase(os.path.abspath(os.fsdecode(file)))
        if p.startswith(CONV):
            OPENED_CONVERTED.append(p)
    return _real_open(file, *a, **k)


def setUpModule():
    global S, LOADED
    builtins.open = _spy_open
    S = MS.Stored()
    LOADED = MC.load_certificates()


def tearDownModule():
    builtins.open = _real_open
    assert OPENED_CONVERTED == [], "a test opened a file of converted/: %s" % OPENED_CONVERTED


def mk(n, kind, sigma, lam, J, c, mu, name="syn"):
    x = MC.Cert()
    x.sha, x.paths, x.name, x.n, x.kind, x.sigma, x.level = name, ["<synthetic>"], name, n, kind, sigma, "synthetic"
    x.lam, x.J, x.c, x.mu, x.E_claim = Fr(lam), Fr(J), Fr(c), Fr(mu), None
    x.Jp = x.J - 4 * sigma * x.lam if kind == "Czz_bar" else x.J
    return x


def fake_rd(tmp, files=None, hashed=True, wrong=False):
    """A scratch 'real_data' folder with a declaration that lists the hashes of three small converted files."""
    files = files or {"real_n57.json": b'{"schema": "p5-real-data-v1", "n": 57}\n', "real_n115.json": b'{"schema": "p5-real-data-v1", "n": 115}\n',
                      "lattice_maps.json": b"{}\n"}
    os.makedirs(os.path.join(tmp, "converted"))
    pinned = {}
    for k, b in files.items():
        with open(os.path.join(tmp, "converted", k), "wb") as f:
            f.write(b)
        pinned[k] = hashlib.sha256(b).hexdigest()
    with open(os.path.join(tmp, "converted", "SHA256SUMS.txt"), "w") as f:
        for k in sorted(pinned):
            f.write("%s  %s\n" % (pinned[k], k))
    decl = "# synthetic declaration\n" + "".join("%s  converted/%s\n" % (v, k) for k, v in pinned.items())
    with open(os.path.join(tmp, "DECLARATION.md"), "w", newline="\n") as f:
        f.write(decl)
    if hashed:
        h = hashlib.sha256(decl.encode()).hexdigest()
        with open(os.path.join(tmp, "DECLARATION.sha256"), "w") as f:
            f.write("%s *DECLARATION.md\n" % (("0" * 64) if wrong else h))
    return pinned, files


class TestGuard(unittest.TestCase):
    def test_refuses_without_or_with_a_wrong_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b, c = (os.path.join(tmp, x) for x in "abc")
            for d in (a, b, c):
                os.makedirs(d)
            pa, _ = fake_rd(a, hashed=False)
            pb, _ = fake_rd(b, wrong=True)
            pc, files = fake_rd(c)
            with mock.patch.dict(C.PINNED, pa, clear=True):
                for rd in (a, b):
                    with self.assertRaises(C.Refused) as cm:
                        C.read_converted(57, rd)
                    self.assertEqual(cm.exception.code, 3)
                    with self.assertRaises(C.Refused):
                        MG.g1_data(rd=rd, pinned=pa)
                sha = C.declaration_guard(c)
                self.assertEqual(sha, C.sha256_file(os.path.join(c, "DECLARATION.md")))
                obj, sha2 = C.read_converted(57, c)
                self.assertEqual((obj["n"], sha2), (57, sha))
                with open(os.path.join(c, "converted", "real_n57.json"), "ab") as f:      # tampered data file
                    f.write(b" ")
                with self.assertRaises(C.Refused):
                    C.read_converted(57, c)
            with mock.patch.dict(C.PINNED, {"real_n115.json": "f" * 64}):                # hash not listed in the declaration
                with self.assertRaises(C.Refused):
                    C.read_converted(115, c)

    def test_the_real_folder_is_refused_while_the_declaration_is_not_hashed(self):
        if os.path.exists(os.path.join(C.RD, "DECLARATION.sha256")):
            self.skipTest("the declaration is hashed: the refusal can no longer be shown on the real folder")
        with self.assertRaises(C.Refused):
            C.load_real(57)
        with self.assertRaises(C.Refused):
            RM.main([])
        p = subprocess.run([sys.executable, "-B", "-I", os.path.join(CODE, "run_map.py")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 3)
        self.assertIn("REFUSED", p.stderr)

    def test_seed(self):
        self.assertEqual(C.seed_from_hash("0000000a" + "f" * 56), 10)


G4S = C.synthetic_graph(4, edges=[(0, 1), (1, 2), (2, 3)], nn2=[(0, 2), (1, 3)], eta=[1, -1, 1, -1], loops=[(0, 1, 2, 3)],
                        local=dict(bulk_site=1, boundary_site=0, edge=[1, 2], loop=[0, 1, 2, 3]))


def small_obj(E=-1.25, z=(0.5, -0.25, 0.75, -0.5), ce=(-0.5, -0.25, -0.75), c2=(0.25, 0.5), loop=0.125, order=None, flip=False):
    pairs = list(zip([(0, 1), (1, 2), (2, 3), (0, 2), (1, 3)], list(ce) + list(c2)))
    if order:
        pairs = [pairs[i] for i in order]
    pl = [[b, a] if flip else [a, b] for (a, b), _ in pairs]
    lab = {"jz": 2.0, "ground_state_energy": -1.0, "final_global_energy": E, "energy_vopt": E, "z_basis_opt": list(z),
           "2_nn_corr_funcs_zz_basis_opt": [v for _, v in pairs], "2_nn_corr_pairs_zz_basis_opt": pl, "z_loop": [loop],
           "z_loop_sites": [[3, 1, 0, 2]]}
    dm = {"jz": 2.0, "ground_state_energy": -1.5, "e1": -1.0, "dmrg_params": {"chi_max": 320, "trunc_cut": 1e-6}, "z": list(z),
          "2_nn_corr_funcs_zz": [v for _, v in pairs], "2_nn_corr_pairs": pl, "z_loop": [loop], "z_loop_sites": [[0, 1, 2, 3]],
          "_heavy_hex_ordered": True}
    return {"schema": C.SCHEMA, "n": 4, C.DATASET: {"2.0": lab}, C.COMPARISON: {"2.0": {"jz": 2.0, "ground_state_energy": -1.0,
            "final_global_energy": -1.2, "energy_vopt": -1.2}}, C.DMRG: {"2.0": dm}}


class TestSchemaLoader(unittest.TestCase):
    def test_labels_and_exact_quantities(self):
        r = C.parse_real(small_obj(), 4, G4S)
        d = r["dataset"]["2.0"]
        self.assertEqual(d["M"], Fr(1, 2))                                   # 0.5 - 0.25 + 0.75 - 0.5, exactly
        self.assertEqual(d["labels_exact"]["m_s"], Fr(2, 4))                 # (0.5 + 0.25 + 0.75 + 0.5)/4
        self.assertEqual(d["labels_exact"]["Czz_bar"], Fr(-1, 2))
        self.assertEqual(d["sum_zz_edges"], Fr(-3, 2))
        self.assertEqual(d["labels"], dict(m_s=0.5, Czz_bar=-0.5, C2_bar=0.375, Z_bulk=-0.25, Z_boundary=0.5, Czz_edge=-0.25, Z_loop=0.125))
        self.assertEqual((d["E_real"], d["E_first"], d["orientation"]), (-1.25, -1.0, 1))
        self.assertFalse(r["comparison"]["2.0"]["has_labels"])
        self.assertEqual(r["dmrg"]["2.0"]["E0"], -1.5)
        # matched by site pair, never by position: any order of the pair list, either order of the two sites
        r2 = C.parse_real(small_obj(order=[4, 2, 0, 3, 1], flip=True), 4, G4S)
        self.assertEqual(r2["dataset"]["2.0"]["labels"], d["labels"])
        self.assertEqual(r2["dataset"]["2.0"]["families"], d["families"])

    def test_bad_objects_are_refused(self):
        def broken(f):
            o = small_obj()
            f(o)
            return o
        cases = [lambda o: o.update(schema="other"), lambda o: o[C.DATASET]["2.0"].update(jz=2.1),
                 lambda o: o[C.DATASET]["2.0"]["z_basis_opt"].pop(), lambda o: o[C.DATASET]["2.0"]["z_basis_opt"].__setitem__(0, float("nan")),
                 lambda o: o[C.DATASET]["2.0"]["2_nn_corr_pairs_zz_basis_opt"].__setitem__(1, [1, 0]),      # the pair (0, 1) twice
                 lambda o: o[C.DATASET]["2.0"]["2_nn_corr_pairs_zz_basis_opt"].__setitem__(1, [0, 3]),      # the edge (1, 2) missing
                 lambda o: o[C.DATASET]["2.0"].pop("final_global_energy"), lambda o: o[C.DMRG]["2.0"]["z_loop_sites"].__setitem__(0, [0, 1, 2]),
                 lambda o: o[C.DATASET].update({"2": o[C.DATASET]["2.0"]})]
        for f in cases:
            with self.assertRaises(ValueError):
                C.parse_real(broken(f), 4, G4S)
        with self.assertRaises(ValueError):
            C.check_complete(C.parse_real(small_obj(), 4, G4S))

    def test_agrees_with_the_loader_of_the_learning_code(self):
        try:
            import numpy as np
            import rd_common as RC
            Gs = dict(n=4, eta=np.array(G4S["eta"], float), M0=0.0, edges=G4S["edges"], nn2=G4S["nn2"], loops=G4S["loops"], local=G4S["local"])
            rec = RC.parse_label_group(small_obj(order=[3, 1, 4, 0, 2], flip=True), C.DATASET, 4)[2.0]
            theirs = RC.seven_labels(rec, Gs)
        except Exception as ex:                                             # another task's file; its interface may change
            self.skipTest("rd_common not usable here: %r" % (ex,))
        mine = C.parse_real(small_obj(), 4, G4S)["dataset"]["2.0"]
        for k in C.LABELS:
            self.assertAlmostEqual(theirs[k], mine["labels"][k], delta=1e-15)
        self.assertAlmostEqual(rec["M_real"], mine["M_float"], delta=1e-15)


class TestExactSideOnTheDimer(unittest.TestCase):
    """Two sites, H(J) = (XX + YY + J ZZ)/4, eta = (+1, -1), m_s = (Z_1 - Z_2)/2, M_0 = 0. In the M = 0 block the
    lowest eigenvalue of H - sigma lam (Z_1 - Z_2) is -J/4 - sqrt(1/4 + 4 lam^2); |up up> and |down down> have
    J/4 +- 2 mu. For lam = 1/3 the root is 5/6 and the ground state v = (3, -1)/sqrt(10) has m_s = 4/5,
    <H> = -J/4 - 3/10; for lam = 15/32 the root is 17/16."""

    def cmin(self, J, root, mu):
        return min(Fr(J) / 4 + 2 * Fr(mu), Fr(J) / 4 - 2 * Fr(mu), -Fr(J) / 4 - Fr(root))

    def test_tight_bound_in_and_out_of_the_sector(self):
        J = 4
        mu = Fr(-17, 12)                                                   # |up up> degenerate with v: tight for mixtures
        c = self.cmin(J, Fr(5, 6), mu)
        self.assertEqual(c, Fr(-11, 6))
        certs = [mk(2, "m_s", 1, Fr(1, 3), J, c, mu, "p"), mk(2, "m_s", -1, Fr(1, 3), J, self.cmin(J, Fr(5, 6), 0), 0, "m")]
        pool = MC.pool_ms(certs, 2, Fr(J))
        Ev = -Fr(J) / 4 - Fr(3, 10)
        iv = MC.exact_interval(pool, Ev, None, 0, allow=0)                 # the in-sector state v
        self.assertEqual(iv["hi"], Fr(4, 5))                               # exactly its label
        self.assertEqual(iv["sides"][-1]["U"], (Ev + Fr(11, 6)) / Fr(2, 3))
        for q in (Fr(1, 20), Fr(2, 5)):                                    # rho = (1-q)|v><v| + q|up up><up up|, M = 2q
            E, M, label = (1 - q) * Ev + q * Fr(J) / 4, 2 * q, (1 - q) * Fr(4, 5)
            only_real = MC.exact_interval(pool, E, M, None, allow=0)
            self.assertEqual(only_real["sides"][1]["U"], label)            # tight: the published-value branch
            both = MC.exact_interval(pool, E, M, 0, allow=0)
            self.assertEqual(both["sides"][1]["decisive_M"], "M_0")        # mu < 0, M_real > M_0: the sector branch is larger
            self.assertEqual(both["sides"][1]["U"], (E - c) / Fr(2, 3))
            self.assertTrue(both["lo"] <= label <= both["hi"])
            # allowance: 1e-6 on E and the worse of M +- 1e-6, bound by bound
            al = MC.exact_interval(pool, E, M, None)
            self.assertEqual(al["sides"][1]["U"] - label, (C.ALLOW + abs(mu) * C.ALLOW) / Fr(2, 3))
            # the other out-of-sector direction, rho' = (1-q)|v><v| + q|down down><down down|: M = -2q, mu M > 0, so the
            # published-value branch is now the larger one and decides (value known in closed form)
            Md = -2 * q
            down = MC.exact_interval(pool, E, Md, 0, allow=0)
            self.assertEqual(down["sides"][1]["decisive_M"], "M_real")
            self.assertEqual(down["sides"][1]["U"], (1 - q) * Fr(4, 5) + q * Fr(17, 2))
            self.assertEqual(down["sides"][1]["cases"]["M_0"][0], (1 - q) * Fr(4, 5) + q * Fr(17, 4))
            self.assertTrue(down["lo"] <= label <= down["hi"])

    def test_pairs_by_concavity_and_range(self):
        a = mk(2, "m_s", 1, Fr(1, 3), 4, self.cmin(4, Fr(5, 6), 0), 0, "a")
        b = mk(2, "m_s", 1, Fr(15, 32), 8, self.cmin(8, Fr(17, 16), 0), 0, "b")
        a2 = mk(2, "m_s", -1, Fr(1, 3), 4, self.cmin(4, Fr(5, 6), 0), 0, "a2")
        b2 = mk(2, "m_s", -1, Fr(1, 3), 8, self.cmin(8, Fr(5, 6), 0), 0, "b2")
        certs = [a, b, a2, b2]
        pool = MC.pool_ms(certs, 2, Fr(6))
        self.assertEqual((len(pool[1]), len(pool[-1])), (1, 1))
        bd = pool[1][0]
        self.assertEqual((bd.how, bd.t), ("pair", Fr(1, 2)))
        self.assertEqual(bd.lamS, (Fr(1, 3) + Fr(15, 32)) / 2 * 2)
        self.assertEqual(bd.c, (a.c + b.c) / 2)
        lam_t = float(bd.lamS) / 2
        true_c = -6 / 4 - (0.25 + 4 * lam_t ** 2) ** 0.5                   # exact ground energy at (6, lam_t)
        self.assertLess(float(bd.c), true_c)                               # valid and weaker than the direct bound there
        self.assertEqual(pool[-1][0].c, -Fr(6, 4) - Fr(5, 6))              # equal fields: the combination is exact
        t45 = MC.pool_ms(certs, 2, Fr(5))[1][0].t
        self.assertEqual(t45, Fr(3, 4))
        self.assertEqual(MC.pool_ms(certs, 2, Fr(9)), {1: [], -1: []})     # outside: no certificate, no interval
        self.assertIsNone(MC.exact_interval(MC.pool_ms(certs, 2, Fr(9)), Fr(0), None, 0))
        self.assertTrue(MC.in_range(certs, 2, Fr(4)) and MC.in_range(certs, 2, Fr(8)) and not MC.in_range(certs, 2, Fr(9)))
        self.assertFalse(MC.in_range(certs, 2, Fr(39, 10)))
        direct = MC.pool_ms(certs, 2, Fr(4))
        self.assertEqual([x.how for x in direct[1]], ["direct"])

    def test_czz_rule(self):
        # plain-Hamiltonian certificates at J'' = 2 < J = 4 < J' = 6; the singlet has E = -J/4 - 1/2, Czz = -1
        J, E = Fr(4), -Fr(4) / 4 - Fr(1, 2)
        mu = -Fr(2) / 4 - Fr(1, 4)                                         # |up up> degenerate with the singlet at J'' = 2
        up = mk(2, "H", 0, 0, 2, self.cmin(2, Fr(1, 2), mu), mu, "h2")
        dn = mk(2, "Czz_bar", -1, Fr(1, 2), 4, self.cmin(6, Fr(1, 2), 0), 0, "c6")   # base 4, field 1/2: J' = 4 + 2 = 6
        self.assertEqual(dn.Jp, Fr(6))
        pool = MC.pool_czz([up, dn], 2, J, 1)
        self.assertEqual((pool[1][0].how, pool[-1][0].how), ("other_coupling", "direct"))
        iv = MC.exact_interval(pool, E, None, 0, allow=0)
        self.assertEqual((iv["lo"], iv["hi"], iv["width"]), (Fr(-1), Fr(-1), Fr(0)))
        self.assertEqual(pool[1][0].u(E, 0), 4 * (E - up.c) / ((J - 2) * 1))          # the formula of the declaration
        self.assertEqual(pool[-1][0].u(E, 0), 4 * (E - dn.c) / ((6 - J) * 1))
        q = Fr(1, 4)                                                       # out of the sector: label 2q - 1, M = 2q
        Eq, M = (1 - q) * E + q * J / 4, 2 * q
        self.assertEqual(MC.exact_interval(pool, Eq, M, None, allow=0)["sides"][1]["U"], 2 * q - 1)
        self.assertIsNone(MC.exact_interval(MC.pool_czz([up, dn], 2, Fr(7), 1), E, None, 0))  # both J' below the target
        self.assertEqual(MC.pool_czz([up], 2, Fr(2), 1), {1: [], -1: []})                    # J' = J: no bound

    def test_caps_tolerances_and_largest_energy(self):
        p = mk(10, "m_s", 1, Fr(1, 2), 4, -3, Fr(1, 4), "p")
        m = mk(10, "m_s", -1, Fr(1, 4), 4, Fr(-11, 4), Fr(-1, 2), "m")
        pool = MC.pool_ms([p, m], 10, Fr(4))
        iv = MC.exact_interval(pool, Fr(-2), Fr(4), 2, allow=0)
        self.assertEqual(iv["sides"][1]["cases"]["M_real"][0], Fr(2, 5))    # (-2 + 3 + 1)/5
        self.assertEqual(iv["sides"][1]["cases"]["M_0"][0], Fr(3, 10))      # (-2 + 3 + 1/2)/5
        self.assertEqual(iv["sides"][-1]["cases"]["M_real"][0], Fr(-1, 2))  # (-2 + 11/4 - 2)/(5/2)
        self.assertEqual(iv["sides"][-1]["cases"]["M_0"][0], Fr(-1, 10))
        self.assertEqual((iv["sides"][1]["decisive_M"], iv["sides"][-1]["decisive_M"]), ("M_real", "M_0"))
        self.assertEqual((iv["lo"], iv["hi"]), (Fr(1, 10), Fr(2, 5)))
        al = MC.exact_interval(pool, Fr(-2), Fr(4), 2)
        self.assertEqual(al["hi"] - iv["hi"], (C.ALLOW + Fr(1, 4) * C.ALLOW) / 5)
        self.assertEqual(iv["lo"] - al["lo"], C.ALLOW / Fr(5, 2))           # the sector branch has no allowance on M
        j = MC.judge(iv, Fr(3, 10))
        self.assertTrue(j["within_tau"])
        self.assertEqual(j["tau_rf"], Fr(6, 100) * Fr(1, 10))
        self.assertFalse(j["within_tau_rf"])
        self.assertFalse(MC.judge(iv, Fr(29, 100))["within_tau"])
        self.assertEqual(MC.tau_reference_free(Fr(-1, 10), Fr(1, 2)), 0)
        self.assertEqual(MC.tau_reference_free(Fr(-1, 2), Fr(-1, 4)), Fr(6, 100) * Fr(1, 4))
        hi = MC.exact_interval(pool, Fr(3), Fr(4), 2, allow=0)              # capped at the spectral range
        self.assertEqual((hi["hi"], hi["hi_raw"] > 1), (Fr(1), True))
        em = MC.exact_interval(pool, Fr(-4), Fr(4), 2, allow=0)             # energy below what the certificates allow
        self.assertTrue(em["empty"])
        self.assertFalse(MC.judge(em, Fr(1))["within_tau"])
        # largest energy: width(E) = (E + 4)/5 + (E + 7/4)/(5/2) on the active pieces (M_real on '+', M_0 on '-')
        tau = Fr(3, 10)
        le = MC.largest_E(pool, Fr(4), 2, tau, -2.0, allow=0)
        self.assertTrue(le["exact"])
        self.assertEqual(MC.exact_interval(pool, le["E"], Fr(4), 2, allow=0)["width"], tau)
        self.assertEqual(le["E"], Fr(-2))                                   # 2/5 - 1/10 = 3/10 exactly at E = -2
        le2 = MC.largest_E(pool, Fr(4), 2, Fr(1, 2), 5.0, allow=0)          # found from above as well
        self.assertEqual(MC.exact_interval(pool, le2["E"], Fr(4), 2, allow=0)["width"], Fr(1, 2))
        # a pool whose upper end reaches the cap first: u_+ = E + 4 (capped at 1 from E = -3), u_- = (E + 7/4)/(5/2);
        # width = 1 + (E + 7/4)/(5/2) = 13/10 at E = -1, where the upper cap is active
        pool2 = MC.pool_ms([mk(10, "m_s", 1, Fr(1, 10), 4, -3, Fr(1, 4), "p2"), m], 10, Fr(4))
        cap = MC.largest_E(pool2, Fr(4), 2, Fr(13, 10), -2.0, allow=0)
        ivc = MC.exact_interval(pool2, cap["E"], Fr(4), 2, allow=0)
        self.assertEqual((cap["E"], ivc["width"], ivc["hi"], ivc["lo"], cap["exact"]), (Fr(-1), Fr(13, 10), Fr(1), Fr(-3, 10), True))
        self.assertGreater(ivc["hi_raw"], 1)


def arrays(sid):
    s = S.D.states[sid]
    return dict(sid=sid, Jg=s["Jz"], E=s["tenpy"]["E"], slope=S.slope(sid), z=list(s["indep"]["Z_graph"]),
                ce=list(s["indep"]["Czz_edges"]), c2=list(s["indep"]["Czz_nn2"]), loop=s["indep"]["Z_loop"])


def mixture(parts, J):
    """Genuine density matrix sum_k w_k |k><k| of stored states: energy at coupling J by the linear rule, arrays."""
    E = sum(w * (a["E"] + (J - a["Jg"]) * a["slope"]) for w, a in parts)
    comb = lambda k: [sum(w * a[k][i] for w, a in parts) for i in range(len(parts[0][1][k]))]
    return dict(E=E, z=comb("z"), ce=comb("ce"), c2=comb("c2"), loop=sum(w * a["loop"] for w, a in parts))


def entry(J, m, G, rng, dmrg=False, E_first=None):
    pairs = list(zip(G["edges"], m["ce"])) + list(zip(G["nn2"], m["c2"]))
    rng.shuffle(pairs)
    pl = [[b, a] if rng.random() < 0.5 else [a, b] for (a, b), _ in pairs]
    loops = [list(l) for l in G["loops"]]
    rng.shuffle(loops)
    lv = [m["loop"] if C.st(l) == C.st(G["local"]["loop"]) else 0.5 for l in loops]
    if dmrg:
        return {"jz": J, "ground_state_energy": m["E"], "e1": m["E"] + 1.0, "dmrg_params": {"chi_max": 320, "trunc_cut": 1e-6},
                "z": m["z"], "2_nn_corr_funcs_zz": [v for _, v in pairs], "2_nn_corr_pairs": pl, "z_loop": lv, "z_loop_sites": loops,
                "_heavy_hex_ordered": True}
    return {"jz": J, "ground_state_energy": m["E"] + 1.0 if E_first is None else E_first, "final_global_energy": m["E"], "energy_vopt": m["E"],
            "z_basis_opt": m["z"], "2_nn_corr_funcs_zz_basis_opt": [v for _, v in pairs], "2_nn_corr_pairs_zz_basis_opt": pl,
            "z_loop": lv, "z_loop_sites": loops}


def witness_state(n, J, label="m_s", frac=0.4):
    """A stored in-sector state of (n, J): the one at the given quantile of the pool energies."""
    pts = sorted(S.own_pool(n, C.jfr(J), label), key=lambda p: p["E"])
    return pts[int(frac * (len(pts) - 1))]["sid"]


class TestNotCertifiedSide(unittest.TestCase):
    def test_q_positive_known_answer(self):
        import hull
        n, J, q = 57, C.jfr("4.0"), 0.05
        G = C.graph(n)
        phi, r = arrays(witness_state(n, 4.0)), arrays("n57_J4.0_R3_sz_minus")
        tau = S.rows[(57, "4.0", "m_s")]["tau"]
        E_real = (1 - q) * (phi["E"] + 2 * MS.DELTA) + q * r["E"]
        M_real = G["M0"] - 2 * q
        nc = S.not_certified(n, J, "m_s", E_real, M_real, tau)
        self.assertAlmostEqual(nc["q"], q, delta=1e-12)
        self.assertEqual((nc["ref"]["sid"], nc["ref"]["which"]), ("n57_J4.0_R3_sz_minus", "R3"))
        self.assertAlmostEqual(nc["Estar"], phi["E"] + 2 * MS.DELTA, delta=1e-9)
        pts = S.limit(n, J, "m_s")["pts"]
        W, up, lo, _, _ = hull.width(pts, nc["Estar"] - MS.DELTA)            # the stored hull, called directly
        self.assertAlmostEqual(nc["w_in"], W, delta=1e-14)
        self.assertAlmostEqual(nc["w_lower"], (1 - nc["q"]) * W, delta=1e-14)
        self.assertEqual(nc["not_certified"], bool((1 - nc["q"]) * W >= tau))
        o_phi = S.D.states[phi["sid"]]["indep"]["m_s"]
        o_r = S.D.states[r["sid"]]["indep"]["m_s"]
        label = (1 - q) * o_phi + q * o_r                                    # label of the synthetic published state
        self.assertTrue(nc["witness"][0] - 1e-12 <= label <= nc["witness"][1] + 1e-12)
        self.assertAlmostEqual(nc["witness"][1] - nc["witness"][0], nc["w_lower"], delta=1e-14)
        # the same state through the exact side: a genuine state of W(E, M) must lie in the proved interval
        m = mixture([(1 - q, phi), (q, r)], 4.0)
        rec = C.parse_label_entry("4.0", entry(4.0, m, G, random.Random(1)), G, C.DATASET)
        self.assertEqual(rec["M"], sum(Fr(x) for x in m["z"]))
        ex = T.exact_side(LOADED["certs"], n, "m_s", J, rec["E_real"], rec["M"], tau, S.E0(n, J), G, rec["E_real"] - S.E0(n, J))
        self.assertTrue(Fr(ex["lo_exact"]) <= rec["labels_exact"]["m_s"] <= Fr(ex["hi_exact"]))
        # and the two sides cannot contradict each other
        self.assertGreaterEqual(ex["width"] + 1e-9, (1 - q) * hull.width(pts, (rec["E_real"] - q * r["E"]) / (1 - q) - MS.DELTA)[0])

    def test_q_negative_and_zero(self):
        tau = S.rows[(57, "4.0", "m_s")]["tau"]
        E0 = S.E0(57, C.jfr("4.0"))
        nc = S.not_certified(57, C.jfr("4.0"), "m_s", E0 + 0.3, 9 + 0.08, tau)         # M_real > M_0: R4 (n = 57 only)
        self.assertEqual(nc["ref"]["which"], "R4")
        self.assertAlmostEqual(nc["q"], -0.04, delta=1e-12)
        r4 = S.D.states["n57_J4.0_R4_sz_plus"]
        self.assertAlmostEqual(r4["indep"]["sum_Z"], 11.0, delta=1e-8)
        self.assertAlmostEqual(nc["Estar"], (E0 + 0.3 - 0.04 * r4["tenpy"]["E"]) / 0.96, delta=1e-9)
        nc115 = S.not_certified(115, C.jfr("4.0"), "m_s", S.E0(115, C.jfr("4.0")) + 0.3, 19.08, 0.05)
        self.assertFalse(nc115["not_certified"])
        self.assertIn("no stored R4 state", nc115["reason"])
        z = S.not_certified(57, C.jfr("4.0"), "m_s", E0 + 0.3, 9.0, tau)
        self.assertEqual((z["q"], z["ref"], z["Estar"]), (0.0, None, E0 + 0.3))
        low = S.not_certified(57, C.jfr("4.0"), "m_s", E0 - 1.0, 9.0, tau)             # nothing below: no witness
        self.assertFalse(low["not_certified"])
        self.assertIn("no pool state", low["reason"])

    def test_pools_brackets_and_the_linear_rule_on_stored_states(self):
        self.assertEqual(S.bracket("3.1"), (C.jfr("3.0"), C.jfr("3.3")))
        self.assertEqual(S.bracket("3.2"), (C.jfr("3.0"), C.jfr("3.3")))                # 3.2 is not one of the 16 grid couplings
        self.assertEqual(S.bracket("4.0"), (C.jfr("4.0"), C.jfr("4.0")))
        self.assertEqual(S.bracket("1.5"), (C.jfr("1.4"), C.jfr("1.6")))
        pts, info = S.pool(57, "3.1", "m_s")
        a, b = S.own_pool(57, C.jfr("3.0"), "m_s"), S.own_pool(57, C.jfr("3.3"), "m_s")
        self.assertEqual((info["kind"], info["couplings"], len(pts)), ("re-evaluated", [3.0, 3.3], len(a) + len(b)))
        p = pts[7]
        st = S.D.states[p["sid"]]
        self.assertAlmostEqual(p["E"], st["tenpy"]["E"] + (3.1 - st["Jz"]) * 0.25 * sum(st["indep"]["Czz_edges"]), delta=1e-12)
        self.assertEqual(p["o"], st["indep"]["m_s"])
        own, info2 = S.pool(57, "3.2", "m_s")                                           # a chain of m_s is stored at 3.2
        self.assertEqual((info2["kind"], len(own)), ("stored chain", S.rows[(57, "3.2", "m_s")]["pool"]))
        # C2_bar has no chain at 3.2: states of 3.0 and 3.3 re-evaluated at 3.2, where this project's E0 is stored.
        # Variational check of the linear rule (sign and size): no re-evaluated energy below E0, the best one close.
        for key in ("3.2", "3.4"):
            pts, info = S.pool(57, key, "C2_bar")
            self.assertEqual(info["kind"], "re-evaluated")
            d = min(q["E"] for q in pts) - S.E0(57, C.jfr(key))
            self.assertGreaterEqual(d, -1e-6)
            self.assertLess(d, 0.05)
            r = S.ref_state(57, key, "R3")                                              # from 3.0 / 3.3 or 3.3 / 3.6
            own_r3 = S.D.states["n57_J%s_R3_sz_minus" % key]["tenpy"]["E"]              # stored at the coupling itself
            self.assertNotEqual(r["Jg"], float(key))
            self.assertGreaterEqual(r["E"] - own_r3, -1e-6)
            self.assertLess(r["E"] - own_r3, 0.05)
        g, info3 = S.pool(115, "4.0", "Z_loop")                                         # grid coupling, no chain of this label
        self.assertEqual(info3["kind"], "stored states, no chain of this label")
        self.assertTrue(all(q["E"] == q["E_own"] for q in g) and len(g) > 10)
        self.assertEqual(S.ref_state(57, "4.0", "R3")["sid"], "n57_J4.0_R3_sz_minus")
        self.assertIsNone(S.ref_state(115, "4.0", "R4"))

    def test_threshold_of_the_reevaluated_pool(self):
        # Sec. 4 at 1.5: with the stored chain pool the same routine must return the stored eps_tau_in
        r = S.rows[(57, "1.4", "m_s")]
        et, info = S.eps_tau_in_pool(57, "1.4", "m_s", S.E0(57, C.jfr("1.4")), r["tau"])
        self.assertEqual(info["kind"], "stored chain")
        self.assertAlmostEqual(et / r["eps_tau_in"], 1.0, delta=1e-9)
        tau = 0.5 * (S.rows[(57, "1.4", "m_s")]["tau"] + S.rows[(57, "1.6", "m_s")]["tau"])
        E0 = min(p["E"] for p in S.pool(57, "1.5", "m_s")[0]) - 1e-3                    # synthetic reference energy
        et15, info15 = S.eps_tau_in_pool(57, "1.5", "m_s", E0, tau)
        self.assertEqual(info15["couplings"], [1.4, 1.6])
        self.assertTrue(et15 is not None and 0 < et15 < 0.1)


class TestGates(unittest.TestCase):
    def test_g1(self):
        with tempfile.TemporaryDirectory() as tmp:
            pinned, files = fake_rd(tmp)
            g = MG.g1_data(rd=tmp, pinned=pinned)
            self.assertTrue(g["pass"] and g["hashes_ok"] and not g["complete"])
            # re-run with a stand-in converter (a script of this test; nothing is unpickled anywhere)
            os.makedirs(os.path.join(tmp, "code"))
            os.makedirs(os.path.join(tmp, "source"))
            with open(os.path.join(tmp, "source", "a.tar.gz"), "wb") as f:
                f.write(b"archive")
            conv = ("import sys, os, hashlib\nout = sys.argv[2]\nos.makedirs(out, exist_ok=True)\nfiles = %r\n"
                    "open(os.path.join(out, 'SHA256SUMS.txt'), 'w').write(''.join('%%s  %%s\\n' %% (hashlib.sha256(b).hexdigest(), k) "
                    "for k, b in sorted(files.items())))\n")
            arch = ("source/a.tar.gz", hashlib.sha256(b"archive").hexdigest())
            with open(os.path.join(tmp, "code", "convert_real_data.py"), "w") as f:
                f.write(conv % (files,))
            g = MG.g1_data(rd=tmp, pinned=pinned, rerun=True, scratch=os.path.join(tmp, "s1"), archive=arch)
            self.assertTrue(g["pass"] and g["complete"] and g["rerun"]["ok"])
            with open(os.path.join(tmp, "code", "convert_real_data.py"), "w") as f:
                f.write(conv % (dict(files, **{"real_n57.json": b"other"}),))
            g = MG.g1_data(rd=tmp, pinned=pinned, rerun=True, scratch=os.path.join(tmp, "s2"), archive=arch)
            self.assertFalse(g["pass"])
            g = MG.g1_data(rd=tmp, pinned=pinned, rerun=True, scratch=os.path.join(tmp, "s3"), archive=("source/a.tar.gz", "0" * 64))
            self.assertFalse(g["pass"])
            with self.assertRaises(ValueError):
                MG.g1_data(rd=tmp, pinned=pinned, rerun=True, scratch=os.path.join(tmp, "s1"), archive=arch)   # not empty
            with open(os.path.join(tmp, "converted", "lattice_maps.json"), "ab") as f:
                f.write(b" ")
            self.assertFalse(MG.g1_data(rd=tmp, pinned=pinned)["pass"])

    def test_g2_g3(self):
        # Neel product state on the 4-site chain at Jz = 2: every edge has <ZZ> = -1 and B = 0, so the exchange part is 0
        neel = small_obj(E=2.0 / 4 * (-3), z=(1, -1, 1, -1), ce=(-1, -1, -1), c2=(1, 1), loop=1)
        r = C.parse_real(neel, 4, G4S)
        g = MG.g2_same_state(r)
        self.assertTrue(g["pass"])
        self.assertEqual((g["rows"][0]["exchange"], g["rows"][0]["B"]), (0.0, 0.0))
        self.assertFalse(MG.g2_same_state(C.parse_real(small_obj(E=-1.6, z=(1, -1, 1, -1), ce=(-1, -1, -1), c2=(1, 1)), 4, G4S))["pass"])
        # z = 0, <ZZ> = -1/2 on every edge: B = 3 * (1/2) * (3/4) = 9/8; the ZZ part is -3/4
        ok = small_obj(E=-0.75 - 1.0, z=(0, 0, 0, 0), ce=(-0.5, -0.5, -0.5))
        g = MG.g2_same_state(C.parse_real(ok, 4, G4S))
        self.assertTrue(g["pass"])
        self.assertAlmostEqual(g["rows"][0]["B"], 1.125, delta=1e-15)
        self.assertAlmostEqual(g["rows"][0]["ratio"], -1.0 / 1.125, delta=1e-15)
        bad = MG.g2_same_state(C.parse_real(small_obj(E=-0.75 - 1.2, z=(0, 0, 0, 0), ce=(-0.5, -0.5, -0.5)), 4, G4S))
        self.assertEqual((bad["pass"], bad["failed"]), (False, ["2.0"]))
        imp = MG.g2_same_state(C.parse_real(small_obj(E=-0.3, z=(1, -1, 0, 0), ce=(0.5, 0, 0)), 4, G4S))   # impossible pair
        self.assertEqual(imp["rows"][0]["n_negative_radicand"], 1)
        g3 = MG.g3_energies(C.parse_real(small_obj(E=-1.25), 4, G4S))
        self.assertTrue(g3["pass"])
        g3 = MG.g3_energies(C.parse_real(small_obj(E=-1.6), 4, G4S))                   # below the authors' E0 = -1.5
        self.assertEqual((g3["pass"], g3["failed"]), (False, ["2.0"]))

    def synth_dmrg(self, n, shift=None):
        G, rng, obj = C.graph(n), random.Random(5), {"schema": C.SCHEMA, "n": n, C.DATASET: {}, C.DMRG: {}}
        for (nn, key), t in S.refs.items():
            if nn == n:
                a = arrays(t["gs_sid"])
                if shift and key == shift[0]:
                    a["z"][shift[1]] += shift[2]
                obj[C.DMRG][key] = entry(float(key), a, G, rng, dmrg=True)
        return C.parse_real(obj, n)

    def test_g4_and_the_seven_labels_from_raw_arrays(self):
        for n, ncoup, nrow in ((57, 18, 116), (115, 16, 49)):
            real = self.synth_dmrg(n)
            g = MG.g4_truth(S, real)
            self.assertTrue(g["pass"])
            self.assertEqual((g["n_energy_rows"], g["n_label_rows"]), (ncoup, nrow))    # the rows of the stored map
            self.assertLess(max(v for v in g["max_abs_dO_over_tau"].values() if v is not None), 1e-9)
            self.assertEqual(g["max_abs_dE0"], 0.0)
            # the seven labels computed by the loader from raw arrays equal the stored ones at every stored coupling
            for (nn, key), t in S.refs.items():
                if nn == n:
                    for lab in C.LABELS:
                        self.assertAlmostEqual(real["dmrg"][key]["labels"][lab], S.O_GS_record(n, C.jfr(key), lab), delta=1e-12)
                        if S.O_GS(n, C.jfr(key), lab) is not None:
                            self.assertEqual(S.O_GS(n, C.jfr(key), lab), S.O_GS_record(n, C.jfr(key), lab))
            tr = MS.truth(S, real, n, C.jfr("4.0"), "Z_loop")
            self.assertEqual((tr["E0_source"], tr["O_source"]), ("project", "project" if n == 57 else "authors"))
        bad = MG.g4_truth(S, self.synth_dmrg(57, shift=("4.0", C.graph(57)["local"]["bulk_site"], 1e-3)))
        self.assertFalse(bad["pass"])
        self.assertEqual(sorted(set(r["label"] for r in bad["failed"])), ["Z_bulk"])   # 1e-3 on one site: 1.7e-2 tau there
        self.assertLess(bad["max_abs_dO_over_tau"]["m_s"], 1e-3)                       # and 3e-4 tau on m_s

    def test_g5(self):
        g = MG.g5_records(LOADED)
        self.assertTrue(g["pass"])
        self.assertEqual((g["n_used"], g["excluded_for_a_missing_or_bad_record"]), (140, []))
        with tempfile.TemporaryDirectory() as tmp:                                     # a certificate without its record
            src = [x for x in LOADED["certs"] if x.n == 57 and x.level == "vball2"][0].paths[0]
            shutil.copy(src, os.path.join(tmp, "a_cert.json"))
            x, why = MC.read_cert(os.path.join(tmp, "a_cert.json"))
            self.assertEqual((x, why), (None, "no verification record"))
            v = C.rj(src[:-10] + "_ver.json")
            for k, val, msg in (("ok", False, "not ok"), ("cert_sha256", "0" * 64, "another file"), ("E_LB_exact", "1/3", "disagrees")):
                with open(os.path.join(tmp, "a_ver.json"), "w") as f:
                    json.dump(dict(v, **{k: val}), f)
                self.assertIn(msg, MC.read_cert(os.path.join(tmp, "a_cert.json"))[1])
            with open(os.path.join(tmp, "a_ver.json"), "w") as f:
                json.dump(v, f)
            self.assertIsNotNone(MC.read_cert(os.path.join(tmp, "a_cert.json"))[0])
            d = C.rj(src)                                                              # tampered bound: E_claim no longer sum t - mu M_0
            d["t"][0] += 1
            with open(os.path.join(tmp, "b_cert.json"), "w") as f:
                json.dump(d, f)
            self.assertIn("differs from E_claim", MC.read_cert(os.path.join(tmp, "b_cert.json"))[1])
            got = MC.load_certificates(roots=(tmp,))
            self.assertEqual((got["n_files"], got["n_used"], len(got["excluded"])), (2, 1, 1))
            self.assertEqual(len(MG.g5_records(got)["excluded_for_a_missing_or_bad_record"]), 1)
        # deciding rows: the two rows on each side of a change of the CERTIFIED (exact) flag
        ix = {}
        for J in C.TRAIN_J:
            cert = J >= C.jfr("3.6")
            ix[(57, C.jkey(J), "m_s")] = dict(n=57, Jz=float(J), key=C.jkey(J), label="m_s",
                                              exact=dict(exists=True, certified=cert, certified_rf=cert,
                                                         certificates=[dict(sha256="s" + C.jkey(J), name="c" + C.jkey(J), path="p")]))
        self.assertEqual([r["key"] for r in MG.deciding_rows(ix, 57, "m_s")], ["3.5", "3.6"])
        self.assertEqual(sorted(MG.deciding_certificates(ix)), ["s3.5", "s3.6"])

    @unittest.skipUnless(os.environ.get("RD_MAP_SLOW") == "1", "set RD_MAP_SLOW=1 to re-prove one stored certificate (about a minute)")
    def test_g5_reprove_one_stored_certificate(self):
        x = sorted((c for c in LOADED["certs"] if c.n == 57 and c.level == "vball2" and c.kind == "m_s"), key=lambda c: c.name)[0]
        with tempfile.TemporaryDirectory() as tmp:
            g = MG.g5_reprove([x.ident()], tmp)
            self.assertTrue(g["pass"], g)
            self.assertEqual(Fr(g["rows"][0]["E_LB_exact"]), x.E_claim)
            bad = dict(x.ident(), sha256="0" * 64)
            self.assertFalse(MG.g5_reprove([bad], os.path.join(tmp, "b"))["pass"])

    def test_g6(self):
        rows = [dict(n=57, Jz=round(1.6 + 0.1 * k, 1), key="%.1f" % (1.6 + 0.1 * k), label="m_s", status="NOT_CERTIFIED" if k < 20 else "GRAY",
                     E0=-10.0, lower=dict(min_pool_E=-10.0 + 1e-3, pool=dict(kind="re-evaluated"))) for k in range(45)]
        near, other = MG.g6_select(rows, {(57, "m_s"): [3.6, None]}, 1234)
        self.assertEqual([r["Jz"] for r in near], [3.3, 3.4, 3.5])
        self.assertEqual(len(other), 10)
        self.assertEqual([r["Jz"] for r in other], [r["Jz"] for r in MG.g6_select(rows, {(57, "m_s"): [3.6]}, 1234)[1]])
        self.assertNotEqual([r["Jz"] for r in other], [r["Jz"] for r in MG.g6_select(rows, {(57, "m_s"): [3.6]}, 1235)[1]])
        self.assertFalse(set(r["Jz"] for r in other) & {3.3, 3.4, 3.5})
        self.assertTrue(MG.g6_energies(rows)["pass"])
        rows[3]["lower"]["min_pool_E"] = -10.0 - 2e-6
        g = MG.g6_energies(rows)
        self.assertEqual((g["pass"], len(g["failed"])), (False, 1))
        # linear rule against stored tensors (the tensors of six states of n = 57, Jz = 1.6 are on this machine)
        sid, other_sid = "n57_J1.6_minchi32_m_s_p_l0.194440", "n57_J4.0_R1_chi320"
        st = S.D.states[sid]
        row = lambda J: dict(n=57, Jz=J, label="m_s", lower=dict(components=dict(min=[[sid, 1.0, st["tenpy"]["E"], 0.0]], max=[[other_sid, 1.0, 0.0, 0.0]]),
                                                                 ref=None))
        g = MG.g6_linear(S, [row(1.5), row(1.8), row(1.6)])
        self.assertEqual((g["n_checked"], g["n_missing_tensors"], g["complete"], g["pass"]), (3, 3, False, True))
        self.assertLess(g["max_dE"], 1e-8)
        self.assertGreater(abs(g["checked"][0]["E_linear"] - st["tenpy"]["E"]), 0.1)   # the re-evaluation is not a small shift
        wrong = MG.g6_linear(S, [row(1.5)], evaluator=lambda path, n, J: st["tenpy"]["E"])
        self.assertFalse(wrong["pass"])
        self.assertEqual(MG.g6_components(dict(lower=dict(components=dict(min=[["a", 1, 0, 0]], max=[["b", .5, 0, 0], ["a", .5, 0, 0]]), ref=dict(sid="r")))),
                         ["a", "b", "r"])

    def test_g7_and_no_decision(self):
        mkrow = lambda key, cert, li, ti, **kw: dict(n=57, Jz=float(key), key=key, label="m_s", status="CERTIFIED_EXACT" if cert else "GRAY",
                                                     status_rf="GRAY", like=dict(status="CERTIFIED_s"),
                                                     exact=dict(exists=True, certified=cert, certified_rf=False, label_inside=li, truth_inside=ti, empty=False, **kw))
        rows = [mkrow("4.0", True, True, True), mkrow("4.1", False, False, True), dict(n=57, Jz=4.2, key="4.2", label="Z_bulk", exact=None,
                                                                                    status="GRAY", status_rf="GRAY", like=dict(status="GRAY_s"))]
        g = MG.g7_filter(rows)
        self.assertEqual((g["pass"], g["n_certified_rows"], g["n_rows_with_an_interval"], g["n_intervals_not_containing_label_and_truth"]), (True, 1, 2, 1))
        rows.append(mkrow("4.3", True, True, False))
        g = MG.g7_filter(rows)
        self.assertEqual((g["pass"], [v["Jz"] for v in g["violations"]]), (False, [4.3]))
        nb = MG.apply_no_decision(rows, g2=dict(n=57, failed=["4.0"]), g3=dict(n=57, failed=[]), g4=dict(n=57, **{"pass": True}))
        self.assertEqual(nb, 1)
        self.assertEqual((rows[0]["status"], rows[0]["status_raw"], rows[0]["no_decision"], rows[0]["exact"]["certified"], rows[0]["like"]["status"]),
                         ("NO_DECISION", "CERTIFIED_EXACT", ["G2"], False, "NA_s"))
        self.assertEqual((rows[1]["status"], rows[1]["no_decision"]), ("GRAY", []))
        self.assertEqual(MG.apply_no_decision(rows, g4=dict(n=57, **{"pass": False})), 4)


class TestTables(unittest.TestCase):
    def test_jstar_relations_rounding(self):
        f = lambda j0, holes=(): {C.jkey(J): (None if C.jkey(J) in holes else J >= C.jfr(j0)) for J in C.TRAIN_J}
        self.assertEqual(T.jstar(f("3.2")), 3.2)
        self.assertEqual(T.jstar(f("1.6")), 1.6)
        self.assertEqual(T.jstar(f("6.0")), 6.0)
        self.assertIsNone(T.jstar(f("6.1")))
        d = f("3.2")
        d["4.0"] = False                                                   # a hole above: J* restarts above it
        self.assertEqual(T.jstar(d), 4.1)
        self.assertEqual(T.jstar(f("3.2", holes=("5.0",))), 5.1)           # a point without a status is not certified
        self.assertIsNone(T.jstar(f("3.2", holes=("6.0",))))
        self.assertIsNone(T.jstar({}))
        R = T.relation
        self.assertEqual([R("CERTIFIED", "CERTIFIED_s"), R("NOT_CERTIFIED", "NOT_CERTIFIED_s")], ["confirmed"] * 2)
        self.assertEqual([R("GRAY", "CERTIFIED_s"), R("GRAY", "NOT_CERTIFIED_s")], ["resolved"] * 2)
        self.assertEqual([R("CERTIFIED", "GRAY_s"), R("NOT_CERTIFIED", "GRAY_s")], ["opened"] * 2)
        self.assertEqual([R("CERTIFIED", "NOT_CERTIFIED_s"), R("NOT_CERTIFIED", "CERTIFIED_s")], ["contradicted"] * 2)
        self.assertEqual([R("GRAY", "GRAY_s"), R("CERTIFIED", "NA_s")], ["gray_both", "not_available"])
        rd = C.round_down_2sig
        self.assertEqual([rd(116.5), rd(85.7), rd(60.2), rd(396.2), rd(0.0123), rd(9.99), rd(100.0), rd(79.4)],
                         [110.0, 85.0, 60.0, 390.0, 0.012, 9.9, 100.0, 79.0])
        self.assertIsNone(rd(None))
        self.assertEqual(T.sec2_status(dict(certified=True), dict(not_certified=True)), "CONFLICT")
        self.assertEqual(T.sec2_status(dict(certified=False, certified_rf=True), None, "certified_rf"), "CERTIFIED_EXACT")
        self.assertEqual(T.sec2_status(None, dict(not_certified=True)), "NOT_CERTIFIED")
        self.assertEqual(T.sec2_status(None, None), "GRAY")

    def rows(self, widths, tau=0.0625):
        """Hand-made m_s rows over the training couplings; widths: {coupling key: width in units of tau or None}."""
        ix = {}
        for J in C.TRAIN_J:
            k = C.jkey(J)
            w = widths.get(k)
            ex = None if w is None else dict(exists=True, certified=bool(w <= 1), certified_rf=bool(w <= 0.9), width_exact=C.fstr(Fr(w) * Fr(tau)),
                                             lo=0.9, hi=0.9 + float(w) * tau, lo_exact="9/10", hi_exact=C.fstr(Fr(9, 10) + Fr(w) * Fr(tau)),
                                             width_over_tau=float(w))
            ix[(57, k, "m_s")] = dict(n=57, Jz=float(J), key=k, label="m_s", tau=tau, training=True, q=0.01, exact=ex, lower=None,
                                      like=dict(status="CERTIFIED_s" if J >= C.jfr("3.2") else "NOT_CERTIFIED_s", outer=None, interpolated=True),
                                      status="CERTIFIED_EXACT" if (ex and ex["certified"]) else "GRAY", status_rf="GRAY",
                                      miss_tau=0.1 if J >= C.jfr("4.0") else (0.4 if J >= C.jfr("3.8") else 2.0 - 0.3 * float(J)), O_GS=0.95)
        return ix

    def test_nested_sets_and_primary_set(self):
        w = {}
        for J in C.TRAIN_J:                                                # 3.4-6.0: 27 couplings with an interval
            if J >= C.jfr("3.4"):
                w[C.jkey(J)] = Fr(11, 10) if J < C.jfr("3.6") else (Fr(1) if J < C.jfr("4.0") else (Fr(3, 4) if J < C.jfr("4.8") else Fr(1, 2)))
        ix = self.rows(w)
        s = T.s_sets(ix, 57)
        self.assertEqual((len(s["S"]), len(s["S_3_4"]), len(s["S_1_2"])), (25, 21, 13))   # edges of the sets are exact (<=)
        self.assertEqual((s["S"][0], s["S_3_4"][0], s["S_1_2"][0]), (3.6, 4.0, 4.8))
        self.assertEqual((s["S_p_name"], s["S_p"]), ("S_3_4", s["S_3_4"]))               # S_1/2 has 13 < 15
        self.assertEqual(T.choose_S_p(list(range(20)), list(range(16)), list(range(15)))[0], "S_1_2")
        self.assertEqual(T.choose_S_p(list(range(14)), [], []), (None, []))
        self.assertEqual(T.choose_S_p(list(range(15)), list(range(14)), [])[0], "S")
        j = T.jstar_table(ix, 57, "m_s")
        self.assertEqual((j["J_star_s"], j["like"]["certified"], j["like"]["not_certified"], j["sec2"]["J_star_exact"], j["sec2"]["certified_exact"]),
                         (3.2, 29, 16, 3.6, 25))
        with tempfile.TemporaryDirectory() as tmp:
            obj, sha = T.write_s_sets({57: ix}, "ab" * 32, tmp)
            self.assertEqual(sha, C.sha256_file(os.path.join(tmp, "S_sets.json")))
            with open(os.path.join(tmp, "S_sets.sha256")) as f:
                self.assertEqual(f.read().split()[0], sha)
            obj2, sha2 = T.write_s_sets({57: ix}, "ab" * 32, os.path.join(tmp, "again"))
            self.assertEqual(sha2, sha)                                    # deterministic
            self.assertEqual(T.write_s_sets({57: ix}, "ab" * 32, tmp)[1], sha)     # the same content again: accepted
            other = self.rows({k: Fr(1, 2) for k in w})                    # other sets: the fixed file is not overwritten
            with self.assertRaises(RuntimeError):
                T.write_s_sets({57: other}, "ab" * 32, tmp)
            self.assertEqual(C.sha256_file(os.path.join(tmp, "S_sets.json")), sha)
            self.assertNotEqual(T.write_s_sets({57: other}, "ab" * 32, os.path.join(tmp, "third"), replace=True)[1], sha)
            self.assertEqual(obj["sizes"]["57"]["S_p"], s["S_p"])
            try:
                import rd_common as RC
                p = RC.parse_sets(C.rj(os.path.join(tmp, "S_sets.json")), 57, "ab" * 32)
            except ImportError as ex:
                self.skipTest("rd_common not importable: %r" % (ex,))
            self.assertEqual((p["S"], p["S_3_4"], p["S_1_2"], p["S_p"], p["S_p_name"]), (s["S"], s["S_3_4"], s["S_1_2"], s["S_p"], "S_3_4"))
            self.assertEqual(p["warnings"], [])

    def test_filter(self):
        w = {C.jkey(J): (Fr(1, 2) if J >= C.jfr("4.0") else Fr(3, 2)) for J in C.TRAIN_J if J >= C.jfr("3.4")}
        ix = self.rows(w)
        f = T.filter_table(ix, 57, n19={C.jkey(J): 0.95 + 0.0625 * (0.1 if J >= C.jfr("4.0") else 0.5) for J in C.TRAIN_J})
        self.assertEqual((f["n_kept"], f["kept"][0], f["n_training"]), (21, 4.0, 45))
        self.assertAlmostEqual(f["miss_kept"]["max"], 0.1)
        # dropped: 1.6-3.9 (24 labels); miss 2 - 0.3 Jz is within tau from 3.4 (3.4-3.7: four) and 0.4 at 3.8, 3.9
        self.assertEqual((f["kept_above_half_tau"], f["dropped_within_tau"], f["dropped_within_half_tau"]), (0, 6, 2))
        self.assertEqual((len(f["dropped"]), f["kept_above_tau"], len(f["per_label"])), (24, 0, 45))
        self.assertAlmostEqual(f["miss_dropped"]["max"], 2.0 - 0.3 * 1.6)
        self.assertAlmostEqual(f["classical_n19"]["max_over_kept"], 0.1, delta=1e-9)
        self.assertTrue(f["classical_n19"]["all_kept_within_a_fifth_of_tau"])
        like = T.filter_table(ix, 57, keep=lambda r: r["like"]["status"] == "CERTIFIED_s")
        self.assertEqual((like["n_kept"], like["kept"][0]), (29, 3.2))


class TestEndToEnd(unittest.TestCase):
    def test_run_on_genuine_mixtures_of_stored_states(self):
        n, G, rng, q, p = 57, C.graph(57), random.Random(11), 0.03, 0.2
        obj = {"schema": C.SCHEMA, "n": n, C.DATASET: {}, C.DMRG: {}, C.COMPARISON: {}}
        keys = sorted((k for (nn, k) in S.refs if nn == n), key=float)
        for key in keys:                                                   # published = (1-q)[(1-p) gs + p witness] + q R3
            gs, r3 = arrays(S.refs[(n, key)]["gs_sid"]), arrays("n57_J%s_R3_sz_minus" % key)
            w = arrays(witness_state(n, key, "m_s", 0.3))
            m = mixture([((1 - q) * (1 - p), gs), ((1 - q) * p, w), (q, r3)], float(key))
            obj[C.DATASET][key] = entry(float(key), m, G, rng)
            obj[C.DMRG][key] = entry(float(key), gs, G, rng, dmrg=True)
            obj[C.COMPARISON][key] = {"jz": float(key), "ground_state_energy": m["E"] + 1, "final_global_energy": m["E"] + 0.01, "energy_vopt": m["E"]}
        for key, base in (("1.5", "1.4"), ("3.1", "3.0")):                 # couplings without stored objects
            J = float(key)
            gs, r3 = arrays(S.refs[(n, base)]["gs_sid"]), arrays("n57_J%s_R3_sz_minus" % base)
            m = mixture([(1 - q, gs), (q, r3)], J)
            obj[C.DATASET][key] = entry(J, m, G, rng)
            truth = mixture([(1.0, gs)], J)
            truth["E"] -= 0.02                                             # a synthetic 'authors' DMRG' below every trial state
            obj[C.DMRG][key] = entry(J, truth, G, rng, dmrg=True)
        real = C.parse_real(obj, n)
        cps = tuple(C.jfr(k) for k in sorted(obj[C.DATASET], key=float))
        sha = hashlib.sha256(b"synthetic declaration").hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            summ = RM.run({n: real}, S, LOADED, sha, tmp, sizes=(n,), couplings=cps, n19=None, log=lambda s: None)
            rows = C.rj(os.path.join(tmp, "map_rows.json"))["rows"]
            gates = C.rj(os.path.join(tmp, "map_gates.json"))
            sets = C.rj(os.path.join(tmp, "S_sets.json"))
            sums = MG._read_sums(os.path.join(tmp, "SHA256SUMS_map.txt"))
            for k, v in sums.items():
                self.assertEqual(C.sha256_file(os.path.join(tmp, k)), v)
            self.assertTrue(os.path.exists(os.path.join(tmp, "map_tables.md")))
            sec = C.rj(os.path.join(tmp, "map_secondary.json"))
        self.assertEqual(len(rows), 7 * len(cps))
        ix = T.index(rows)
        # genuine states: the consistency gates hold, no row is contradictory, every proved interval holds its label
        for k in ("G2_57", "G3_57", "G4_57", "G6b", "G7"):
            self.assertTrue(gates[k]["pass"], k)
        self.assertEqual(summ["flags"]["conflicts"], [])
        self.assertEqual(summ["flags"]["empty_intervals"], [])
        n_iv = 0
        for r in rows:
            self.assertAlmostEqual(r["q"], q, delta=1e-9)
            self.assertEqual(r["no_decision"], [])
            if r["exact"] and r["exact"]["exists"]:
                n_iv += 1
                self.assertTrue(r["exact"]["label_inside"], (r["key"], r["label"]))
                self.assertTrue(r["exact"]["truth_inside"], (r["key"], r["label"]))
                if r["lower"].get("w_lower") is not None:
                    self.assertGreaterEqual(r["exact"]["width"] + 1e-9, r["lower"]["w_lower"])
            if r["lower"] and r["lower"].get("witness"):
                lo, hi = r["lower"]["witness"]
                self.assertTrue(lo - 1e-9 <= r["label_real"] <= hi + 1e-9 or r["key"] in ("1.5", "3.1"), (r["key"], r["label"]))
        # m_s has an interval on [3.4, 6.0] (7 of the 20 couplings); Czz_bar wherever a certificate with J' below the
        # target exists, i.e. above the smallest J' of the stored certificates (2.7198 at n = 57: 11 couplings)
        jp_min = min(x.Jp for x in LOADED["certs"] if x.n == 57 and x.kind != "m_s")
        self.assertEqual(n_iv, 7 + sum(1 for J in cps if J > jp_min))
        self.assertEqual(n_iv, 18)
        self.assertTrue(all(ix[(57, k, "Czz_bar")]["exact"]["exists"] == (C.jfr(k) > jp_min) for k in obj[C.DATASET]))
        self.assertTrue(all(not ix[(57, k, "Czz_bar")]["exact"]["certified"] for k in obj[C.DATASET] if float(k) < 3.4))
        self.assertTrue(all(ix[(57, k, "m_s")]["exact"]["exists"] == (float(k) >= 3.4) for k in obj[C.DATASET]))
        self.assertTrue(all(not ix[(57, k, "m_s")]["exact"]["certified"] for k in obj[C.DATASET] if float(k) < 3.4))
        self.assertEqual((ix[(57, "3.1", "m_s")]["like"]["interpolated"], ix[(57, "3.1", "m_s")]["lower"]["pool"]["kind"]), (True, "re-evaluated"))
        self.assertEqual((ix[(57, "3.1", "m_s")]["E0_source"], ix[(57, "3.0", "m_s")]["E0_source"]), ("authors", "project"))
        self.assertEqual(ix[(57, "4.0", "Z_bulk")]["exact"], None)
        # a largest energy was solved for the exact rows inside the range, and it is consistent with the status
        for k in ("4.0", "6.0"):
            ex = ix[(57, k, "m_s")]["exact"]
            self.assertTrue(ex["eps_max_is_exact_root"])
            self.assertEqual(ex["certified"], ix[(57, k, "m_s")]["eps_real"] <= ex["eps_max"])
        # tables
        pvo = summ["predicted_vs_obtained"]
        self.assertEqual(len(pvo["table"]), 171)
        self.assertEqual(pvo["counts"]["no_real_data"], 171 - 116)
        self.assertEqual(sum(v for k, v in pvo["counts"].items() if k != "no_real_data"), 116)
        fa = summ["accuracy_factors"]["57"]["m_s"]["values"][0]
        self.assertEqual(fa["Jz"], 1.1)
        self.assertAlmostEqual(fa["F_A"], ix[(57, "1.1", "m_s")]["de_real"] / S.rows[(57, "1.1", "m_s")]["de_star_in"], delta=1e-9)
        self.assertAlmostEqual(fa["F_B"], ix[(57, "1.6", "m_s")]["de_real"] / S.rows[(57, "1.1", "m_s")]["de_star_in"], delta=1e-9)
        self.assertIn("re-evaluated pool", summ["accuracy_factors"]["57"]["m_s"]["values"][4]["source"])
        self.assertEqual(sets["declaration_sha256"], sha)
        self.assertEqual(sets["sizes"]["57"]["S"], [r["Jz"] for r in rows if r["label"] == "m_s" and r["training"] and r["exact"]["certified"]])
        self.assertEqual(len(sec["first_stage"]["57"]), len(cps))
        self.assertEqual(sec["comparison"]["57"]["rows"][0]["status"], "NOT_AVAILABLE")
        self.assertEqual(summ["gates"]["G5b"], "skipped")
        # Extension E1 as a SEPARATE column: take the stored m_s certificates of Jz = 3.4 out of the main set and hand
        # them in as 'E1'. The main column loses 3.4 (range [3.6, 6.0]); the E1 column has it; S never uses E1.
        e1 = [c for c in LOADED["certs"] if c.n == 57 and c.kind == "m_s" and c.J == C.jfr("3.4")]
        main = dict(LOADED, certs=[c for c in LOADED["certs"] if c not in e1])
        self.assertTrue(len(e1) >= 2)
        with tempfile.TemporaryDirectory() as tmp:
            s2 = RM.run({n: real}, S, main, sha, tmp, sizes=(n,), couplings=tuple(C.jfr(k) for k in ("3.3", "3.4", "3.6")),
                        certs_e1=e1, log=lambda s: None)
            r2 = T.index(C.rj(os.path.join(tmp, "map_rows.json"))["rows"])
            sets2 = C.rj(os.path.join(tmp, "S_sets.json"))["sizes"]["57"]
        a, b = r2[(57, "3.4", "m_s")], ix[(57, "3.4", "m_s")]
        self.assertEqual((a["exact"]["exists"], a["exact"]["in_range"], a["exact"]["certified"], a["status"]), (False, False, False, "GRAY"))
        self.assertEqual((a["exact_e1"]["lo_exact"], a["exact_e1"]["hi_exact"], a["exact_e1"]["certified"], a["status_e1"]),
                         (b["exact"]["lo_exact"], b["exact"]["hi_exact"], b["exact"]["certified"], b["status"]))
        self.assertEqual((sets2["S"], sets2["secondary_E1"]["S"]), ([3.6], [3.4, 3.6]))
        self.assertEqual((s2["jstar"]["57_m_s"]["sec2"]["certified_exact"], s2["jstar"]["57_m_s"]["sec2_e1"]["certified_exact"]), (1, 2))
        self.assertEqual(s2["certificates_E1"], len(e1))
        self.assertIn("exact_with_E1", s2["filter"]["57_m_s"])
        print("\n(e) end-to-end synthetic run: %d rows, %d exact intervals, all labels inside; statuses of m_s: %s" % (
            len(rows), n_iv, {k: ix[(57, k, "m_s")]["status"] for k in ("1.1", "3.0", "3.4", "4.0", "6.0")}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
