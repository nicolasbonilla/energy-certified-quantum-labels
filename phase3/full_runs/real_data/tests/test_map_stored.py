# real_data / tests / test_map_stored.py  (own code; 2026-11-12; task rd-code-map)
#
# Unit tests of the map code against STORED objects only (no real datum; converted/ is never opened):
#   (a) with the stored digitized energies, M = M_0 and q = 0 the code reproduces the stored map row by row
#       (statuses, widths at the stored windows, J* and counts of summary_map.json);
#   (b) at the stored upper windows it reproduces the exact rows of the rigor table (17 of 18 within tau; the
#       exception at 1.0859 tau), as exact rationals against the independent recomputation of the review;
#   (c) it reproduces the stored exact device interval at Jz = 6.0 (0.4992 tau), which is of the same form;
#   (d) concavity: a bound predicted at a stored certificate coupling from its two neighbours is valid (no stored
#       in-sector state violates it) and weaker than the direct one.
# Run:  python -B -I test_map_stored.py      (about fifteen seconds; or run_map_tests.py for both test files)
import os
import sys
import unittest
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "code"))
sys.dont_write_bytecode = True

import map_common as C      # noqa: E402
import map_certs as MC      # noqa: E402
import map_stored as MS     # noqa: E402
import map_tables as T      # noqa: E402

S = None
CERTS = None
LOADED = None


def setUpModule():
    global S, CERTS, LOADED
    S = MS.Stored()
    LOADED = MC.load_certificates()
    CERTS = LOADED["certs"]


class TestA_StoredMap(unittest.TestCase):
    def test_rows_reproduce_the_stored_map(self):
        self.assertEqual(len(S.rows), 171)
        mism, n_nc, n_c = [], 0, 0
        for (n, key, label), r in sorted(S.rows.items()):
            thr, J = S.refs[(n, key)], C.jfr(key)
            if n in C.SIZES:                                   # truth rule of Sec. 0 at the stored couplings
                self.assertEqual(S.O_GS(n, J, label), r["O_GS"])
                self.assertEqual(C.TAU_FRAC * abs(S.O_GS(n, J, label)), r["tau"])
                self.assertEqual(S.E0(n, J), thr["E0"])
            like = S.like_for_like(n, J, label, thr["E_up"], thr["E0"], r["tau"], E_inner=thr["E_lo"])
            if like["status"][:-2] != r["status"]:
                mism.append((n, key, label, r["status"], like["status"]))
            self.assertFalse(like["interpolated"])
            self.assertAlmostEqual(like["w_out"], r["at_up"]["w_out"], delta=1e-12)
            if r["at_lo"]["w_in"] is None:
                self.assertIsNone(like["w_in"])
            else:
                self.assertAlmostEqual(like["w_in"], r["at_lo"]["w_in"], delta=1e-12)
            # the NOT CERTIFIED side of Sec. 2 with M = M_0 (q = 0) at the stored lower window is the stored inner side
            nc = S.not_certified(n, J, label, thr["E_lo"], C.graph(n)["M0"], r["tau"])
            self.assertEqual(nc["q"], 0.0)
            self.assertIsNone(nc["ref"])
            expect = r["at_lo"]["w_in"] is not None and r["at_lo"]["w_in"] >= r["tau"]
            self.assertEqual(nc["not_certified"], expect)
            if r["status"] == "NOT_CERTIFIED":
                self.assertTrue(nc["not_certified"])
                self.assertAlmostEqual(nc["w_lower"], r["at_lo"]["w_in"], delta=1e-12)
                n_nc += 1
            n_c += r["status"] == "CERTIFIED"
            # central window: both widths
            dig = S.like_for_like(n, J, label, thr["E_dig"], thr["E0"], r["tau"])
            self.assertAlmostEqual(dig["w_out"], r["at_dig"]["w_out"], delta=1e-12)
            if r["at_dig"]["w_in"] is not None:
                self.assertAlmostEqual(dig["w_in"], r["at_dig"]["w_in"], delta=1e-12)
        self.assertEqual(mism, [])
        print("\n(a) 171 stored rows reproduced: %d CERTIFIED, %d NOT_CERTIFIED, %d GRAY; 0 mismatches"
              % (n_c, n_nc, 171 - n_c - n_nc))

    def test_jstar_and_counts_of_the_stored_map(self):
        RD, seen = S.D.RD, 0
        for name, js in sorted(S.SM["jstar"].items()):
            if not name.endswith("_r1"):
                continue
            n = int(name.split("_")[0])
            label = name[len(str(n)) + 1:-3]
            flags = {}
            for J in C.TRAIN_J:
                e = RD["eps1"].get("%d_%s" % (n, C.jkey(J)))
                eo, ei = S.interp(n, label, J, "eps_tau_out_lb"), S.interp(n, label, J, "eps_tau_in")
                flags[C.jkey(J)] = None if (e is None or (eo is None and ei is None)) else bool(eo is not None and e <= eo)
            self.assertEqual(T.jstar(flags), js["J_star_central"], name)
            self.assertEqual(sum(1 for v in flags.values() if v), js["n_certified_central"], name)
            seen += 1
        self.assertEqual(seen, 10)
        print("\n(a) J* (central) and counts of the stored map reproduced for %d label-size pairs" % seen)

    def test_interpolation_returns_the_computed_value_at_a_computed_point(self):
        r = S.rows[(57, "3.3", "m_s")]
        self.assertAlmostEqual(S.interp(57, "m_s", C.jfr("3.3"), "eps_tau_out_lb"), r["eps_tau_out_lb"], delta=1e-15)
        self.assertIsNone(S.interp(115, "Z_bulk", C.jfr("3.0"), "eps_tau_in"))        # one computed point only
        self.assertEqual(S.like_for_like(115, C.jfr("3.0"), "Z_loop", -100.0, -101.0, 0.05)["status"], "NA_s")


class TestB_RigorRows(unittest.TestCase):
    def test_loader_counts(self):
        self.assertEqual((LOADED["n_files"], LOADED["n_distinct"], LOADED["n_used"]), (220, 214, 140))
        self.assertEqual(LOADED["by_size"], {57: 120, 115: 20})
        self.assertEqual(LOADED["n_verified_other_sizes"], 56)                         # n = 19
        self.assertTrue(all("not one of the heavy-hex graphs" in why for _, why in LOADED["excluded"]))
        self.assertEqual([float(j) for j in MC.ms_couplings(CERTS, 57)], [3.4, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0])
        self.assertEqual([float(j) for j in MC.ms_couplings(CERTS, 115)], [4.0, 6.0])
        for n in C.SIZES:                                                              # the declared range
            js = MC.ms_couplings(CERTS, n)
            self.assertEqual((js[0], js[-1]), MC.DECLARED_RANGE[n])
        print("\n(b) certificates: %d files, %d distinct by SHA-256, %d used (n = 57: %d, n = 115: %d)"
              % (LOADED["n_files"], LOADED["n_distinct"], LOADED["n_used"], LOADED["by_size"][57], LOADED["by_size"][115]))

    def test_rows_of_the_rigor_table(self):
        grid = C.rj(os.path.join(C.RIGOR, "outputs", "grid_v2.json"))
        res = C.rj(os.path.join(C.RIGOR, "outputs", "results_v2.json"))["rows"]
        ref = C.rj(os.path.join(C.REVIEW, "scratch", "math-rigorous-bounds", "rows_exact.json"))["rows"]
        self.assertEqual(len(grid), 18)
        within, worst, full_within = 0, None, 0
        for g, r, x in zip(grid, res, ref):
            n, J, label = g["n"], C.jfr(g["Jz"]), g["label"]
            self.assertEqual((x["n"], x["Jz"], x["label"]), (g["n"], g["Jz"], g["label"]))
            G = C.graph(n)
            Eup, tau = Fraction(g["E_up"]), Fraction(g["tau"])
            full = MC.make_pool(CERTS, n, label, J, n_e=len(G["edges"]))
            gl = {sg: set(Fraction(q["lam"]) for q in g["sides"][s]["pts"]) for s, sg in (("+", 1), ("-", -1))}
            # the pool of the rigor table: direct certificates of the two rigor runs at the declared fields
            pool = {sg: [b for b in full[sg] if b.how == "direct" and not b.members[0].name.startswith("ft_")
                         and b.members[0].lam in gl[sg]] for sg in (1, -1)}
            iv = MC.exact_interval(pool, Eup, None, G["M0"], allow=0)
            jd = MC.judge(iv, tau)
            for s, sg in (("+", 1), ("-", -1)):
                self.assertEqual(iv["sides"][sg]["U"], Fraction(x["sides"][s]["u_exact"]))
                win = iv["sides"][sg]["cases"]["M_0"][1].members[0]
                self.assertEqual(win.name, x["sides"][s]["src"].split(":")[1])
                self.assertEqual(win.E_claim, Fraction(x["sides"][s]["E_LB_exact"]))
                self.assertGreaterEqual(Fraction(r["sides"][s]["best"]["u"]), iv["sides"][sg]["U"])   # stored float is outward
            self.assertEqual(jd["within_tau"], r["certified"])
            self.assertEqual(jd["within_tau"], x["certified_exact"])
            self.assertEqual(jd["within_tau_rf"], x["certified_reference_free"])
            self.assertAlmostEqual(jd["width_over_tau"], x["w_over_tau"], delta=1e-12)
            self.assertAlmostEqual(jd["width_over_tau"], r["w_over_tau"], delta=1e-9)
            within += jd["within_tau"]
            if not jd["within_tau"]:
                worst = (n, float(J), label, jd["width_over_tau"])
            # the full pool of Sec. 2 (off-grid fields, final-test certificates, pairs, other couplings) is a superset
            ivf = MC.exact_interval(full, Eup, None, G["M0"], allow=0)
            self.assertLessEqual(ivf["width"], iv["width"])
            full_within += MC.judge(ivf, tau)["within_tau"]
        self.assertEqual(within, 17)
        self.assertEqual(worst[:3], (57, 3.4, "m_s"))
        self.assertEqual(round(worst[3], 4), 1.0859)
        print("\n(b) rigor table reproduced as exact rationals: %d of 18 within tau; exception %s at %.4f tau; "
              "with the full pool of Sec. 2: %d of 18" % (within, worst[:3], worst[3], full_within))

    def test_largest_energy_is_an_exact_root(self):
        n, J, label = 57, C.jfr("4.0"), "m_s"
        G, thr, row = C.graph(n), S.refs[(57, "4.0")], S.rows[(57, "4.0", "m_s")]
        pool, tau = MC.make_pool(CERTS, n, label, J), Fraction(row["tau"])
        le = MC.largest_E(pool, None, G["M0"], tau, thr["E_up"], allow=0)
        self.assertTrue(le["exact"])
        self.assertEqual(MC.exact_interval(pool, le["E"], None, G["M0"], allow=0)["width"], tau)
        self.assertGreater(MC.exact_interval(pool, le["E"] + Fraction(1, 10 ** 9), None, G["M0"], allow=0)["width"], tau)
        self.assertGreater(le["E"], Fraction(thr["E_up"]))               # the stored row is certified with a margin
        # with the sector value and the published-value branch equal (M_real = M_0) the allowance only widens
        iv0 = MC.exact_interval(pool, Fraction(thr["E_up"]), None, G["M0"], allow=0)
        iv1 = MC.exact_interval(pool, Fraction(thr["E_up"]), Fraction(G["M0"]), G["M0"])
        self.assertGreater(iv1["width"], iv0["width"])
        self.assertLess(float(iv1["width"] - iv0["width"]), 1e-4)


class TestC_DeviceInterval(unittest.TestCase):
    def test_device_interval_at_6(self):
        ana = C.rj(os.path.join(C.FT, "analysis", "c3b_20261110", "test_c3b.json"))["C3"]["rec"]
        rq = C.rj(os.path.join(C.FT, "out_c3b_20261110T164846Z", "out", "c", "rq_C_J6.0_rec.json"))
        allowed = set(c["cert_sha256"] for c in C.rj(os.path.join(C.FT, "inputs", "certs_n57_stored.json")))
        allowed |= set(x.sha for x in CERTS if x.name.startswith("ft_"))
        self.assertEqual(len(allowed), 42)
        E, J, G = Fraction(rq["E_exact"]), C.jfr("6.0"), C.graph(57)
        for label, expect in (("m_s", 0.499177), ("Czz_bar", 0.567753)):
            a = ana[label]
            full = MC.make_pool(CERTS, 57, label, J, n_e=len(G["edges"]))
            pool = {sg: [b for b in full[sg] if b.how == "direct" and b.members[0].sha in allowed] for sg in (1, -1)}
            iv = MC.exact_interval(pool, E, None, G["M0"], allow=0)
            self.assertEqual(iv["lo"], Fraction(a["lo_exact"]))
            self.assertEqual(iv["hi"], Fraction(a["hi_exact"]))
            trf = MC.tau_reference_free(iv["lo"], iv["hi"])
            self.assertEqual(bool(iv["width"] <= trf), a["below_tau"])
            self.assertAlmostEqual(float(iv["width"] / trf), a["w_over_tau"], delta=1e-12)
            self.assertEqual(round(float(iv["width"] / trf), 6), expect)
            lab = Fraction(rq["%s_exact" % label])
            self.assertTrue(iv["lo"] <= lab <= iv["hi"])
            ivf = MC.exact_interval(full, E, None, G["M0"], allow=0)
            self.assertLessEqual(ivf["width"], iv["width"])
            print("\n(c) device interval at Jz = 6.0, %s: [%.9f, %.9f], %.6f tau (stored %.6f); full pool of Sec. 2: %.6f tau"
                  % (label, float(iv["lo"]), float(iv["hi"]), float(iv["width"] / trf), a["w_over_tau"],
                     float(ivf["width"] / MC.tau_reference_free(ivf["lo"], ivf["hi"]))))


class TestD_Concavity(unittest.TestCase):
    def test_neighbours_predict_a_valid_weaker_bound(self):
        n, G = 57, C.graph(57)
        M0, Js = G["M0"], MC.ms_couplings(CERTS, 57)
        cs = [x for x in CERTS if x.n == n and x.kind == "m_s"]
        done = 0
        for i in range(1, len(Js) - 1):
            J, Ja, Jb = Js[i], Js[i - 1], Js[i + 1]
            key = C.jkey(J)
            direct = MC.pool_ms(CERTS, n, J, pairs=False)
            pred = {s: [MC.combine(a, b, J, n) for a in cs if a.sigma == s and a.J == Ja
                        for b in cs if b.sigma == s and b.J == Jb] for s in (1, -1)}
            self.assertTrue(pred[1] and pred[-1] and direct[1] and direct[-1])
            # valid: every stored in-sector state of (57, J) obeys every predicted bound (and every direct one)
            pts = S.own_pool(n, J, "m_s")
            self.assertGreater(len(pts), 50)
            worst = None
            for pool in (pred, direct):
                for s in (1, -1):
                    for b in pool[s]:
                        a0, b0 = (float(v) for v in b.line(Fraction(M0)))
                        m = min(a0 + b0 * p["E"] - s * p["o"] for p in pts)
                        worst = m if worst is None else min(worst, m)
            self.assertGreaterEqual(worst, -1e-9)
            # weaker than the direct one at the stored upper window (sector value of M, no allowance)
            E, tau = Fraction(S.refs[(n, key)]["E_up"]), Fraction(S.rows[(n, key, "m_s")]["tau"])
            ivd = MC.exact_interval(direct, E, None, M0, allow=0)
            ivp = MC.exact_interval(pred, E, None, M0, allow=0)
            for s in (1, -1):
                self.assertGreaterEqual(ivp["sides"][s]["U"], ivd["sides"][s]["U"])
            self.assertGreaterEqual(ivp["width"], ivd["width"])
            o = S.rows[(n, key, "m_s")]["O_GS"]
            self.assertTrue(ivp["lo"] <= Fraction(o) <= ivp["hi"] and ivd["lo"] <= Fraction(o) <= ivd["hi"])
            # the pool of Sec. 2 contains both, so it is at least as tight as either
            ivs = MC.exact_interval(MC.pool_ms(CERTS, n, J), E, None, M0, allow=0)
            self.assertLessEqual(ivs["width"], ivd["width"])
            print("\n(d) m_s, n = 57, Jz = %s from (%s, %s): direct %.4f tau, predicted by concavity %.4f tau, pool of "
                  "Sec. 2 %.4f tau; smallest margin of a stored state %.2e" % (key, C.jkey(Ja), C.jkey(Jb), float(ivd["width"] / tau),
                                                                               float(ivp["width"] / tau), float(ivs["width"] / tau), worst))
            done += 1
        self.assertEqual(done, 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
