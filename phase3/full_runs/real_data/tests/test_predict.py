# real_data / tests / test_predict.py  (own code; 2026-11-12; task rd-code-learn)
# Unit tests of the prediction code (DECLARATION.md Secs. 5, 6) on SYNTHETIC numbers with known answers, and of the
# n = 19 curves against the stored ones. No real datum is read.     python -B -I test_predict.py
import copy
import json
import os
import sys
import tempfile

import numpy as np
from scipy import stats

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # python -I does not add the script folder
import synth  # noqa: E402
from synth import rdc, rp  # noqa: E402

C = synth.Checks("test_predict")
N19 = os.path.join(synth.REAL_RD, "out", "n19")
C19 = rdc.rj(os.path.join(N19, "n19_curves.json"))

# ---------------------------------------------------------------- Spearman
C.close(rp.spearman([1, 2, 3, 4, 5], [2, 1, 4, 3, 5]), 0.8, "Spearman, closed form without ties (1 - 6*4/120)")
C.close(rp.spearman([1, 2, 3, 4], [9, 7, 4, 1]), -1.0, "Spearman of a strictly decreasing sequence is -1")
rng = np.random.default_rng(1)
worst = 0.0
for _ in range(200):
    x = rng.integers(0, 6, 30).astype(float); y = rng.integers(0, 6, 30).astype(float)
    if len(set(x)) > 1 and len(set(y)) > 1:
        worst = max(worst, abs(rp.spearman(x, y) - stats.spearmanr(x, y)[0]))
C.ok(worst < 1e-12, "Spearman with ties equals scipy.stats.spearmanr on 200 random cases (largest difference %.1e)" % worst)
C.ok(np.isnan(rp.spearman([1, 2, 3], [5, 5, 5])), "Spearman of a constant sequence is undefined (nan)")

# ---------------------------------------------------------------- t_x and F
t = rp.t_values([0.9, -0.9, -0.5, 0.2], [0.8, -0.8, -0.6, 0.5], [1, -1, -1, 1])
C.ok(np.allclose(t, [0.5, 0.5, -0.25, -0.6]), "t_x = (o_real - o_GS)/(o_Neel - o_GS) on four hand cases")
C.ok(np.isnan(rp.t_values([0.3], [1.0], [1.0])[0]), "t_x undefined when the Neel value equals the truth")
r = rp.sign_test({1.0: np.array([0.1] * 19 + [-0.1])})
C.ok(r["F"] == 0.95 and r["holds"], "F = 19/20 = 0.95 holds (the rule is F >= 0.95)")
r = rp.sign_test({1.0: np.array([0.1] * 18 + [-0.1, 0.0])})
C.ok(abs(r["F"] - 0.9) < 1e-15 and not r["holds"], "F = 18/20 does not hold; t = 0 is not > 0")
r = rp.sign_test({1.0: np.array([0.5, 1.0, 1.5, np.nan]), 2.0: np.array([0.5, 0.5, -1.0, 2.0])})
C.ok(r["F"] == 6 / 8 and r["frac_t_le_1"] == 5 / 8 and r["frac_0_lt_t_le_1"] == 4 / 8 and r["n_undefined"] == 1,
     "F, fraction t <= 1, fraction 0 < t <= 1 and undefined count over two couplings")
C.ok(r["F_per_coupling"] == {"1.0": 0.75, "2.0": 0.75}, "F per coupling")

# ---------------------------------------------------------------- D and P4
C.close(rp.D_value([0.53, -0.47], [0.5, -0.5]), 1.0, "D = mean |o_real - o_GS| / (0.06 |o_GS|) = 1 on a hand case")
r = rp.p4_test({J: 1 / J for J in rdc.ALL_J})
C.ok(r["spearman"] == -1.0 and r["holds"], "P4 holds for a strictly decreasing error (Spearman -1)")
D = {J: 1 / J for J in rdc.ALL_J}
for J in rdc.ALL_J[:12]:
    D[J] = 0.01 * J                                        # the error rises over the first twelve couplings
r = rp.p4_test(D)
C.close(r["spearman"], stats.spearmanr(sorted(D), [D[J] for J in sorted(D)])[0], "P4 Spearman equals scipy on a non-monotone case")
C.ok(r["spearman"] > -0.9 and not r["holds"], "P4 does not hold when Spearman is %.3f (> -0.9)" % r["spearman"])

# ---------------------------------------------------------------- the curve, the chord, the n = 19 files
stored = rdc.rj(os.path.join(rdc.FR, "bias_law", "inputs", "n19_curves.json"))


def f_n19b(Cc, J, de):                                    # function f of bias_law/code/n19b.py, copied verbatim
    c = np.array(Cc[J]['curve']); return float(np.interp(np.sqrt(max(de, 0)), np.sqrt(np.maximum(c[:, 0], 0)), c[:, 1]))


Cf = {float(k): v for k, v in stored.items()}
worst = max(abs(rp.curve_value(stored, J, de) - f_n19b(Cf, J, de)) for J in Cf for de in (0.0, 1e-5, 0.003, 0.02, 0.2, 5.0))
C.ok(worst == 0.0, "curve_value equals n19b.f on the stored curves, also outside their range (held end values)")
dE, dm, dc, nlev = 0.0, 0.0, 0.0, set()
for k in stored:
    a, b = stored[k], C19[k]
    ca, cb = np.array(a["curve"]), np.array(b["curve"])
    dE = max(dE, abs(a["E0"] - b["E0"])); dm = max(dm, abs(a["ms0"] - b["ms0"])); dc = max(dc, float(np.abs(ca - cb).max()))
    nlev.add(len(cb))
C.ok(len(stored) == 14 and dE <= 1e-8 and dm <= 1e-6 and dc <= 1e-5,
     "the new n = 19 curves reproduce the 14 stored ones (gate G-A2 tolerances): |dE0| %.1e, |dm_s| %.1e, curve %.1e" % (dE, dm, dc))
C.ok(sorted(float(k) for k in C19) == rdc.ALL_J and nlev == {26}, "n = 19 curves exist at the 50 couplings, 26 levels each")
L19 = rdc.rj(os.path.join(N19, "n19_labels.json"))
G19 = rdc.graph(19, synth.ROOT)
bad = 0
for k, l in L19.items():
    ok = (abs(np.array(l["Z"]) @ G19["eta"] / 19 - l["m_s"]) < 1e-12 and abs(l["sum_Z"] - 3.0) < 1e-9 and l["residual_norm"] < 1e-8
          and l["dim"] == 75582 and abs(l["E0"] - C19[k]["E0"]) == 0 and l["E0"] < l["E_neel"]
          and abs(np.mean(l["Czz_edges"]) - l["Czz_bar"]) < 1e-12 and min(c[0] for c in C19[k]["curve"]) > -1e-10)
    bad += not ok
C.ok(bad == 0, "n = 19 labels: m_s = eta.Z/19, sum Z = 3 (sector 11 up / 8 down), residual < 1e-8, E0 below the Neel energy, at all 50")
J0 = 3.0
l = L19["3.0"]
C.close(rp.chord_value(C19, J0, l["de_neel"]), 1 - l["m_s"], "the chord at the Neel energy error equals 1 - m_s(19)")
C.close(rp.chord_value(C19, J0, l["de_neel"] / 4), (1 - l["m_s"]) / 2, "the chord scales as sqrt(de)")

# ---------------------------------------------------------------- P5 rule on synthetic rows
Cs = {str(float(J)): dict(E0=-20 * J / 4 * 1.1, ms0=0.9, curve=[[x * x, 2 * x] for x in np.linspace(0, 0.5, 26)]) for J in rdc.ALL_J}
C.close(rp.curve_value(Cs, 2.0, 0.01), 0.2, "synthetic curve: curve(de) = 2 sqrt(de)")


def rows(n, ratio, de=0.0004, m_gs=0.9):
    return [rp.p5_row(J, m_gs + ratio.get(J, 1.0) * rp.curve_value(Cs, J, de), m_gs, de, Cs) for J in rdc.ALL_J]


tau = 0.06 * 0.9; cur = 0.04                               # raw miss = 0.74 tau: every coupling decides
s57, s115 = rp.p5_summary(rows(57, {}), 57), rp.p5_summary(rows(115, {}), 115)
C.ok(rp.p5_rule(s57, s115)["outcome"] == "PASS" and s57["n_deciding"] == 50 and s57["mean_miss_tau"] < 1e-12, "P5 passes when every label sits on the curve")
r1 = rows(57, {2.0: 1.31})
C.ok(rp.p5_rule(rp.p5_summary(r1, 57), s115)["outcome"] == "FAIL" and rp.p5_summary(r1, 57)["ratios_outside"] == [2.0]
     and rp.p5_summary(r1, 57)["mean_miss_ok"], "P5 fails on one ratio of 1.31 although the mean miss is small")
rb = rows(57, {}); rb[3]["ratio"], rb[7]["ratio"] = 1.3, 0.75
C.ok(rp.p5_summary(rb, 57)["ratios_ok"], "ratios of exactly 1.3 and 0.75 are inside (closed interval)")
rb[3]["ratio"] = 1.3000001
C.ok(rp.p5_summary(rb, 57)["ratios_outside"] == [rb[3]["Jz"]], "a ratio of 1.3000001 is outside")
rb[3]["ratio"] = None
C.ok(not rp.p5_summary(rb, 57)["ratios_ok"], "an undefined ratio at a deciding coupling counts as outside")
x = 1 + 0.2 * tau / cur                                    # every miss = 0.2 tau exactly
m = rp.p5_summary(rows(57, {J: x for J in rdc.ALL_J}), 57)
C.ok(abs(m["mean_miss_tau"] - 0.2) < 1e-12, "construction: mean miss of 0.2 tau")
y = 1 + 0.21 * tau / cur
m57 = rp.p5_summary(rows(57, {J: y for J in rdc.ALL_J}), 57); m115 = rp.p5_summary(rows(115, {J: y for J in rdc.ALL_J}), 115)
C.ok(not m57["mean_miss_ok"] and m115["mean_miss_ok"] and m57["ratios_ok"], "mean miss 0.21 tau: above the limit at n = 57 (0.2), below it at n = 115 (0.6)")
C.ok(rp.p5_rule(m57, s115)["outcome"] == "FAIL" and rp.p5_rule(s57, m115)["outcome"] == "PASS", "the rule uses 0.2 at n = 57 and 0.6 at n = 115")
small = [rp.p5_row(J, 0.9 + 3.0 * rp.curve_value(Cs, J, 1e-6), 0.9, 1e-6, Cs) for J in rdc.ALL_J]   # raw miss 0.11 tau
ms_ = rp.p5_summary(small, 57)
C.ok(ms_["n_deciding"] == 0 and ms_["ratios_ok"] and ms_["mean_miss_ok"], "a ratio of 3 where the raw miss is below 0.2 tau does not decide")
C.ok(rows(57, {})[0]["de_inside_curve"] and not rp.p5_row(2.0, 0.95, 0.9, 0.3, Cs)["de_inside_curve"], "flag for an energy error outside the curve")

# ---------------------------------------------------------------- loader: pairs by site pair, truth rule
obj, exp, G = synth.build(57, C19)
rd = rdc.from_objects(57, obj, G, None)
Z, e_gs, n2_gs, l_gs = synth.truth_fields(G, 2.0)
C.ok(np.allclose(rd.truth[2.0]["families"]["edges"], e_gs, atol=0, rtol=0) and np.allclose(rd.truth[2.0]["families"]["second_neighbours"], n2_gs, atol=0, rtol=0)
     and np.allclose(rd.truth[2.0]["families"]["loops"], l_gs, atol=0, rtol=0),
     "pairs and loops are matched by their sites although the files list them in other orders")
C.ok(len(rd.Js) == 50 and len(rd.truth) == 51, "50 label couplings, 51 DMRG couplings")
C.close(rd.lab[2.0]["de"], exp["de"][2.0], "de_real = (E_real - E0)/n", 1e-9)
C.close(rd.lab[2.0]["labels"]["m_s"], exp["m_real"][2.0], "m_s of the label from the site labels")
bad = copy.deepcopy(obj); bad["skqd_random_flip"]["2.0"]["2_nn_corr_pairs_zz_basis_opt"][0] = bad["skqd_random_flip"]["2.0"]["2_nn_corr_pairs_zz_basis_opt"][1][::-1]
C.raises(ValueError, lambda: rdc.from_objects(57, bad, G, None), "a repeated pair in a file is refused")
bad = copy.deepcopy(obj); bad["skqd_random_flip"]["2.0"]["jz"] = 2.1
C.raises(ValueError, lambda: rdc.from_objects(57, bad, G, None), "a coupling field that contradicts the file name is refused")
bad = copy.deepcopy(obj); bad["dmrg"]["2.0"]["2_nn_corr_pairs"][0] = [0, 0]
C.raises(ValueError, lambda: rdc.from_objects(57, bad, G, None), "a missing pair is refused")
rd2 = rdc.from_objects(57, obj, G, ({2.0: -1000.0}, {(2.0, "m_s"): 0.5}))
C.ok(rd2.truth[2.0]["E0"] == -1000.0 and rd2.truth[2.0]["labels"]["m_s"] == 0.5 and rd2.truth[2.1]["E0_source"] == "authors"
     and rd2.truth_authors[2.0]["labels"]["m_s"] == rd.truth[2.0]["labels"]["m_s"] and rd2.truth[2.0]["labels"]["Czz_bar"] == rd.truth[2.0]["labels"]["Czz_bar"],
     "truth rule of Sec. 0: this project's reference where stored, the authors' DMRG otherwise; Sec. 7 truth is the authors'")
sv = rdc.seven_labels(rdc.parse_dmrg(obj, 57)[2.0], G)
C.ok(sv["Z_bulk"] == Z[46] and sv["Z_boundary"] == Z[4] and sorted(G["local"]["edge"]) == [11, 46] and G["local"]["bulk_site"] == 46
     and abs(sv["Czz_bar"] - e_gs.mean()) < 1e-15 and abs(sv["C2_bar"] - n2_gs.mean()) < 1e-15 and abs(sv["m_s"] - Z @ G["eta"] / 57) < 1e-15,
     "local labels use site 46 (bulk), site 4 (boundary), edge (11, 46) at n = 57")

# ---------------------------------------------------------------- analyse_size on the synthetic data
for n in (57, 115):
    obj, exp, G = synth.build(n, C19)
    rd = rdc.from_objects(n, obj, G, None)
    A = rp.analyse_size(rd, C19, None)
    for fam in rdc.FAMILIES:
        C.close(A["P1_P3"][fam]["F"], exp["F"][fam], "n = %d, F of %s" % (n, fam))
    C.ok([A["P1_P3"][f]["holds"] for f in rdc.FAMILIES] == [True, n == 115, True, True], "n = %d: F rule per family (edges fail at 57 by construction)" % n)
    C.close(A["P1_P3"]["loops"]["frac_t_le_1"], exp["loops_frac_t_le_1"], "n = %d, loops between the ground and Neel states at 41 of 50 couplings" % n)
    Js = sorted(exp["D_sites"])
    C.close(A["P4"]["sites"]["spearman"], stats.spearmanr(Js, [exp["D_sites"][J] for J in Js])[0], "n = %d, P4 Spearman of the sites" % n)
    C.close(A["P4"]["sites"]["D"]["2.0"], exp["D_sites"][2.0], "n = %d, D of the sites at Jz = 2.0" % n, 1e-9)
    C.ok(A["P5"]["all"]["mean_miss_tau"] < 1e-9 and all(abs(r["ratio"] - 1) < 1e-9 for r in A["P5"]["rows"]), "n = %d: labels built on the curve give ratio 1 and miss 0" % n)
    C.ok(A["P5"]["training_45"]["n_couplings"] == 45 and A["P5"]["all"]["n_couplings"] == 50, "n = %d: 50 couplings decide, 45 reported" % n)
    r0 = A["n19_comparison"]["rows"][9]
    C.close(r0["n19_minus_truth_tau"], abs(C19["2.0"]["ms0"] - exp["m_gs"][2.0]) / (0.06 * exp["m_gs"][2.0]), "n = %d: n = 19 against the truth at Jz = 2.0" % n)

# ---------------------------------------------------------------- end to end through the gate (synthetic folder)
import run_predict  # noqa: E402
tmp = tempfile.mkdtemp(prefix="rd_predict_")
sha, exp, pinned = synth.make_rd(tmp, os.path.join(N19, "n19_curves.json"), ratio_dev={(57, 1.2): 1.5})
real_RD, real_PIN, real_refs = rdc.RD, rdc.PINNED, rdc.project_refs
rdc.RD, rdc.PINNED, rdc.project_refs = tmp, pinned, (lambda n, root=None: ({}, {}))
try:
    out = os.path.join(tmp, "out", "predict")
    C.raises(rdc.Refused, lambda: run_predict.main(["--hash=" + "0" * 64, "--out=" + out]), "run_predict refuses a hash that is not the declaration's")
    C.ok(not os.path.exists(os.path.join(out, "predict_results.json")), "nothing is written after a refusal")
    res = run_predict.main(["--hash=" + sha, "--out=" + out])
    C.ok(res["P5_rule"]["outcome"] == "FAIL" and res["P5_rule"]["ratios_outside_57"] == [1.2] and res["P5_rule"]["ratios_outside_115"] == [],
         "end to end: one ratio of 1.5 at (57, Jz = 1.2) makes P5 fail and is named")
    C.ok(res["sizes"]["57"]["n19_comparison"]["n_kept"] == 27, "end to end: kept set read from the sets file")
    v = res["variant_post_select"]["115"]
    C.ok(v["n_couplings"] == 46 and not (set(v["couplings"]) & {5.6, 5.7, 5.9, 6.0}), "end to end: the comparison variant at n = 115 leaves out the four couplings of gate G2")
    C.ok(res["sizes"]["57"]["n19_comparison"]["kept"][0] == 3.4, "end to end: the kept set starts at 3.4 in the synthetic sets file")
    with open(os.path.join(tmp, "converted", "real_n57.json"), "a") as f:
        f.write(" ")
    C.raises(rdc.Refused, lambda: run_predict.main(["--hash=" + sha, "--out=" + out]), "a converted file whose SHA-256 is not the pinned one is refused")
    os.remove(os.path.join(tmp, "DECLARATION.sha256"))
    C.raises(rdc.Refused, lambda: run_predict.main(["--hash=" + sha, "--out=" + out]), "run_predict refuses when DECLARATION.sha256 does not exist")
finally:
    rdc.RD, rdc.PINNED, rdc.project_refs = real_RD, real_PIN, real_refs
C.done()
