# real_data / tests / test_learn.py  (own code; 2026-11-12; task rd-code-learn)
# Unit tests of the learning code (DECLARATION.md Sec. 7: floor f2, constructive test f3, sets file, intervals for
# Proposition 2, the real-data branch of the derived scripts) on SYNTHETIC numbers with known answers.
# No real datum is read.     python -B -I test_learn.py
import copy
import json
import os
import runpy
import sys
import tempfile

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # python -I does not add the script folder
import synth  # noqa: E402
from synth import rdc  # noqa: E402
import rd_f23 as f23  # noqa: E402
sys.path.insert(0, os.path.join(rdc.FR, "method", "code"))
import ml2  # noqa: E402

C = synth.Checks("test_learn")

# ---------------------------------------------------------------- index, seeds, split sizes, S_p
C.ok([rdc.k_index(m) for m in (45, 44, 12, 9, 19, 8)] == [42, 41, 12, 9, 18, 9], "k = ceil((m+1)(1-alpha)): 42 for m = 45, 41 for 44, 12 for 12, 9 for 9, 18 for 19, 9 for 8")
C.ok(all(rdc.k_index(m) == int(np.ceil((1 - 0.1) * (m + 1))) for m in range(1, 500)), "the exact index equals the floating-point formula of the stored scripts for m < 500")
C.ok(rdc.seed_from_hash("0000002a" + "f" * 56) == 42 and rdc.seed_from_hash("FFFFFFFF" + "0" * 56) == 4294967295, "seed = integer of the first eight hex digits")
C.raises(ValueError, lambda: rdc.seed_from_hash("abc"), "a string that is not a SHA-256 gives no seed")
C.ok([rdc.split_sizes(m) for m in (27, 20, 19, 15, 14)] == [(6, 12), (6, 12), (4, 9), (4, 9), None], "split sizes: 6/12 from 20 couplings, 4/9 from 15 to 19, not run below 15")
C.ok(rdc.choose_S_p(list(range(27)), list(range(21)), list(range(11)))[0] == "S_3_4" and rdc.choose_S_p(list(range(27)), list(range(21)), list(range(15)))[0] == "S_1_2"
     and rdc.choose_S_p(list(range(16)), [1, 2], [])[0] == "S" and rdc.choose_S_p(list(range(14)), [], []) == (None, None),
     "S_p is the most stringent nested set with at least 15 couplings; none if S has fewer")
T = [k / 10 for k in range(34, 61)]
sp = f23.make_splits(T, 123, 57, "S")
C.ok(len(sp) == 200 and all(len(a) == 6 and len(b) == 12 and len(c) == 9 and sorted(a + b + c) == T for a, b, c in sp), "200 splits, each a partition into 6 / 12 / 9 couplings")
C.ok(sp == f23.make_splits(T, 123, 57, "S") and sp != f23.make_splits(T, 124, 57, "S") and sp != f23.make_splits(T, 123, 115, "S")
     and len(set(json.dumps(s) for s in sp)) > 190, "the splits are fixed by (seed, size, set) and change with each of them")
C.ok(f23.make_splits(T[:14], 1, 57, "S") is None and len(f23.make_splits(T[:17], 1, 57, "S_3_4")[0][2]) == 4, "14 couplings: no split; 17 couplings: 4 / 9 / 4")

# ---------------------------------------------------------------- the floor (f2)
rng = np.random.default_rng(7)
viol, eq = 0, 0
for _ in range(2000):
    m = int(rng.integers(5, 46)); lo = rng.normal(size=m); w = rng.uniform(0.01, 1, m); hi = lo + w
    f = lo + w / 2 + rng.normal(size=m) * rng.choice([0.0, 0.01, 1.0])
    q = f23.kth_smallest(np.maximum(abs(f - lo), abs(f - hi)))[0]; wk = f23.kth_smallest(w)[0]
    viol += bool(2 * q < wk - 1e-12)
    eq += bool(abs(2 * f23.kth_smallest(np.maximum(abs(lo + w / 2 - lo), abs(lo + w / 2 - hi)))[0] - wk) < 1e-12)
C.ok(viol == 0 and eq == 2000, "floor: 2q >= w_(k) in 2000 random cases (any predictions), with equality for predictions at the midpoints")
lw = {J: float(i + 1) for i, J in enumerate(rdc.TRAIN_J)}              # 45 lower widths: 1, 2, ..., 45
r = f23.floor_f2(lw, {J: 41.5 for J in rdc.ALL_J})
C.ok(r["m"] == 45 and r["k"] == 42 and r["floor"] == 42.0 and r["holds"] and r["floor_over_tau"]["1.1"] == 42 / 41.5, "floor of the widths 1..45 is the 42nd narrowest, 42; it exceeds tau = 41.5")
h = r["in_distribution_held_out"]
C.ok(h["1.6"]["floor"] == 42.0 and h["6.0"]["floor"] == 41.0 and h["6.0"]["k"] == 41 and not r["holds_in_distribution_held_out"] and not r["readings_agree"],
     "held out: 41st narrowest of the other 44 (42 if a narrow label is removed, 41 if a wide one); the readings are reported separately")
C.ok(not f23.floor_f2(lw, {J: 42.0 for J in rdc.ALL_J})["holds"], "a floor equal to tau does not exceed it")

# ---------------------------------------------------------------- models of (f3)
x = np.array([3.4, 4.0, 4.4, 5.0, 5.5, 6.0])
a, c = f23.coef("M1", x, 4.7)
C.close(c + a @ (0.3 + 0.7 / x), 0.3 + 0.7 / 4.7, "M1 reproduces a line in 1/Jz")
a, c = f23.coef("M2", x, 3.7)
C.close(c + a @ (1 - 0.675 / x ** 2 + 0.188 / x ** 4), 1 - 0.675 / 3.7 ** 2 + 0.188 / 3.7 ** 4, "M2 reproduces 1 - a/Jz^2 - b/Jz^4")
C.close(c + float(a.sum()), 1.0, "M2 predicts 1 for labels equal to 1 (its constant term)")
Y = rng.normal(size=(45, 5)); eta5 = np.array([1, -1, 1, -1, 1.0])
a, c = f23.coef("M0", rdc.TRAIN_J, 1.2)
C.close(float(a @ (Y @ eta5 / 5)), float(ml2.ms(ml2.fit_poly(rdc.TRAIN_J, Y)(1.2)[0], eta5)), "M0 equals ml2.fit_poly (cubic in 1/Jz, ridge 1e-8) on m_s", 1e-9)
C.ok(abs(f23.sigma_loglinear(5, [(4, 1.0), (6, 4.0)]) - 2) < 1e-12 and abs(f23.sigma_loglinear(7, [(4, 1.0), (6, 4.0)]) - 8) < 1e-12
     and abs(f23.sigma_loglinear(3, [(4, 1.0), (6, 4.0)]) - 0.5) < 1e-12 and f23.sigma_loglinear(4, [(4, 1.0), (6, 4.0)]) == 1.0, "log-linear width model: 2 between 1 and 4, continued beyond the ends")

# ---------------------------------------------------------------- (f3): a perfect model, and what the floor does to (W)
mfun = lambda v: 1 - 0.675 / v ** 2 + 0.188 / v ** 4                    # exactly of the form of M2
ystar = {J: mfun(J) for J in rdc.ALL_J}; tau = {J: 0.06 * ystar[J] for J in rdc.ALL_J}


def data(cfrac, y=None, truth=None):
    y = y or ystar
    return dict(y=y, ystar=truth or ystar, tau=tau, exact={J: (y[J] - cfrac * tau[J] / 2, y[J] + cfrac * tau[J] / 2) for J in T},
                lower_w={J: 0.0 for J in rdc.ALL_J}, train_all=rdc.TRAIN_J)


r = f23.run_set(57, "S", T, data(0.97), 2024)
M2 = r["models"]["M2"]
sp = f23.make_splits(T, 2024, 57, "S")
theory = float(np.mean([max(0.97 * tau[j] for j in cal) <= min(tau[v] for v in qs) for tr, cal, qs in sp]))
C.ok(all(abs(2 * s["q"] - s["floor_w_k"]) < 1e-12 for s in M2["splits"]), "perfect model, labels certified at 0.97 tau: 2q equals the widest calibration interval in every split")
C.close(M2["frac_splits_W"], theory, "perfect model: (W) holds exactly in the splits where the widest calibration interval is below every query's tau")
C.ok(theory < 0.9 and M2["frac_pairs_C"] == 1.0 and not M2["W_holds"] and M2["C_holds"] and r["outcome_M1_M2"] == "FAIL",
     "so the test FAILS on (W) with a perfect model and full coverage (fraction of splits %.3f), as the floor says" % theory)
C.ok(all(r["models"][m]["floor_violations"] == 0 and r["models"][m]["two_q_over_floor_min"] >= 1 - 1e-12 for m in f23.MODELS), "2q >= w_(k) in every split, for M1, M2 and M0")
r2 = f23.run_set(57, "S_1_2", T, data(0.45), 2024)
C.ok(r2["models"]["M2"]["frac_splits_W"] == 1.0 and r2["models"]["M2"]["frac_pairs_C"] == 1.0 and r2["outcome_M1_M2"] == "PASS"
     and r2["models"]["M2"]["width_tau_max"] < 0.47, "the same model with labels certified at 0.45 tau PASSES: 2q/tau at most %.3f" % r2["models"]["M2"]["width_tau_max"])
C.ok(r2["models"]["M1"]["W_a_exact_available_pairs"] == 200 * 9 and r2["models"]["M0"]["W_a_exact_tau_range"] is None,
     "Proposition 2(a): exact band for M1 and M2 (training labels certified); not available for M0 (uncertified training labels)")
a, c = f23.coef("M2", sp[0][0], sp[0][2][0])
r3 = f23.eval_split("M2", *sp[0], data(0.45))
C.close(r3["rows"][0]["W_a_exact_tau"], float(np.abs(a) @ np.array([0.45 * tau[j] for j in sp[0][0]])) / tau[sp[0][2][0]], "W(x) = sum_j |a_j(x)| width(I_j) on one split")
shift = {J: ystar[J] + 2 * tau[J] for J in rdc.ALL_J}
r4 = f23.run_set(57, "S_1_2", T, data(0.45, truth=shift), 2024)
C.ok(r4["models"]["M2"]["frac_pairs_C"] == 0.0 and r4["outcome_M1_M2"] == "FAIL" and r4["gate_G7_outside_interval"]["truth"] == T and r4["gate_G7_outside_interval"]["label"] == [],
     "a truth outside the label intervals: (C) fails and every coupling is listed as an inconsistency (gate G7)")
C.ok(f23.run_set(57, "S_1_2", T[:14], data(0.45), 2024)["status"].startswith("NOT RUN"), "a set with 14 couplings is not run")
lit = r2["models"]["M2"]["norm_literal"]; ivn = r2["models"]["M2"]["norm_interval"]
C.ok(lit["width_tau_max"] < 1e-9 and 0.44 < ivn["width_tau_min"] and ivn["width_tau_max"] < 0.47,
     "secondary scores on the perfect model: label-only score gives width 0; worst-case score over I_j gives about 0.45 tau")
sets = dict(S=T, S_3_4=T[6:], S_1_2=T[16:], S_p_name="S_3_4", S_p=T[6:])
out = f23.run_f3(57, sets, data(0.45), 2024, keep_splits=False)
C.ok(out["primary"]["set"] == "S_3_4" and out["primary"]["outcome"] == "PASS" and out["sets"]["S_1_2"]["status"].startswith("NOT RUN") and out["sets"]["S"]["status"] == "RUN",
     "run_f3: decision on the primary set; the other nested sets are run or reported as not run")

# ---------------------------------------------------------------- sets file and intervals for Proposition 2
y = {J: ystar[J] + 0.001 for J in rdc.ALL_J}
so = {"schema": rdc.SETS_SCHEMA, "declaration_sha256": "a" * 64, "sizes": {"57": synth.sets_object(57, y, ystar, "a" * 64, outer_like_at=(1.1, 3.0))}}
ps = rdc.parse_sets(so, 57, "a" * 64)
C.ok(len(ps["S"]) == 27 and len(ps["S_3_4"]) == 21 and len(ps["S_1_2"]) == 11 and ps["S_p_name"] == "S_3_4" and ps["S_p"] == ps["S_3_4"] and not ps["warnings"], "sets file: 27 / 21 / 11 couplings, primary set S_3/4")
C.raises(ValueError, lambda: rdc.parse_sets(so, 57, "b" * 64), "a sets file written under another declaration is refused")
bad = copy.deepcopy(so); bad["sizes"]["57"]["S_p"] = bad["sizes"]["57"]["S"]
C.raises(ValueError, lambda: rdc.parse_sets(bad, 57), "a primary set that is not the declared one is refused")
bad = copy.deepcopy(so); bad["sizes"]["57"]["S_1_2"] = [3.4]
C.raises(ValueError, lambda: rdc.parse_sets(bad, 57), "sets that are not nested are refused")
bad = copy.deepcopy(so); bad["sizes"]["57"]["intervals"]["4.0"]["exact"] = None
C.raises(ValueError, lambda: rdc.parse_sets(bad, 57), "a member of S without an exact interval is refused")
bad = copy.deepcopy(so); bad["sizes"]["57"]["intervals"]["5.5"]["exact"]["hi"] += 0.02
C.raises(ValueError, lambda: rdc.parse_sets(bad, 57), "a member of S_1/2 with an interval wider than tau/2 is refused")
bad = copy.deepcopy(so); bad["sizes"]["57"]["S"] = bad["sizes"]["57"]["S"][1:]
C.ok(len(rdc.parse_sets(bad, 57)["warnings"]) == 1, "a certified coupling left out of S is reported as a warning")
I = rdc.prop2_intervals(rdc.ALL_J, y, ystar, ps)
w11, w30 = 4 * tau[1.1], 4 * tau[3.0]
C.ok(I[4.0]["upper_kind"] == "exact" and not I[4.0]["indicative"] and I[1.1]["upper_kind"] == "like_for_like" and I[1.1]["indicative"]
     and I[2.0]["upper_kind"] == "interpolated" and I[2.0]["indicative"] and I[2.0]["neighbours"] == [1.1, 3.0], "upper intervals: exact where they exist, otherwise flagged as indicative")
tq = (2.0 - 1.1) / (3.0 - 1.1)
C.close(I[2.0]["w_out"], float(np.exp((1 - tq) * np.log(w11) + tq * np.log(w30))), "indicative width: log-linear in Jz between the neighbours")
C.close(max(abs(0.7 - I[2.0]["outer"][0]), abs(0.7 - I[2.0]["outer"][1])), abs(0.7 - y[2.0]) + I[2.0]["w_out"], "indicative score equals |f - y| + w, as in the stored script")
C.close(I[2.0]["w_in"], 3.0 * tau[2.0], "lower version: the width given by the sets file")
C.ok(I[4.0]["truth_in_outer"] and I[4.0]["label_in_outer"], "label and truth inside the exact interval (gate G7) in the synthetic case")

# ---------------------------------------------------------------- the real-data branch, end to end on a synthetic folder
N19 = os.path.join(synth.REAL_RD, "out", "n19", "n19_curves.json")
tmp = tempfile.mkdtemp(prefix="rd_learn_")
sha, exp, pinned = synth.make_rd(tmp, N19)
real = (rdc.RD, rdc.PINNED, rdc.project_refs, sys.argv)
rdc.RD, rdc.PINNED, rdc.project_refs = tmp, pinned, (lambda n, root=None: ({}, {}))
try:
    out = os.path.join(tmp, "out", "learn"); setsp = os.path.join(tmp, "out", "S_sets.json")
    sys.argv = ["rd_learn_ibm.py", synth.ROOT, out, "--data=real", "--hash=" + sha, "--models=poly3_invJ,null_nn", "--tag=cheap"]
    runpy.run_path(os.path.join(synth.CODE, "rd_learn_ibm.py"), run_name="__main__")
    res = rdc.rj(os.path.join(out, "results_cheap.json"))
    S = res["sizes"]["57"]
    C.ok(len(S["train"]) == 45 and S["ood"] == [1.1, 1.2, 1.3, 1.4] and S["n_couplings"] == 50, "derived realistic test on the real-data branch: 45 training couplings, 4 test couplings, 50 in all")
    G = rdc.graph(57, synth.ROOT)
    rd = rdc.from_objects(57, rdc.rj(os.path.join(tmp, "converted", "real_n57.json")), G, None)
    fit = ml2.fit_poly(rdc.TRAIN_J, np.array([rd.lab[J]["Z"] for J in rdc.TRAIN_J]))
    mt = ml2.ms(rd.truth_authors[1.1]["Z"], G["eta"])
    row = S["models"]["poly3_invJ"]["ood_emulated"]["rows"][0]
    C.close(row["miss_ms_over_tau"], abs(ml2.ms(fit(1.1)[0], G["eta"]) - mt) / (0.06 * abs(mt)), "its miss at Jz = 1.1 equals a direct computation (labels = z_basis_opt, truth = the DMRG group)", 1e-9)
    C.close(row["m_s_emu"], exp[57]["m_real"][1.1], "the label of the row is the label of the data file", 1e-12)
    C.ok(len(S["models"]["poly3_invJ"]["indist_emulated"]["rows"]) == 45 and "ood_exact_control" in S["models"]["poly3_invJ"], "in distribution over 45 held-out couplings; control on DMRG labels present")
    sys.argv = ["rd_prop2_cubic.py", synth.ROOT, out, "--data=real", "--hash=" + sha, "--sets=" + setsp]
    runpy.run_path(os.path.join(synth.CODE, "rd_prop2_cubic.py"), run_name="__main__")
    P = rdc.rj(os.path.join(out, "prop2_cubic.json"))["sizes"]["57"]
    kinds = {k: v["upper_kind"] for k, v in P["intervals"].items()}
    C.ok(kinds["4.0"] == "exact" and kinds["1.6"] == "like_for_like" and kinds["1.8"] == "interpolated" and len(P["indist"]) == 45 and len(P["ood"]) == 4,
         "derived Proposition 2 on the real-data branch: 45 + 4 queries; upper intervals exact, like-for-like or interpolated")
    C.ok(all(r["rule_c"] != "ANSWER" and r["band_a"] != "PINNED" and r["q_indicative"] and r["W_indicative"] for r in P["indist"] + P["ood"]),
         "an indicative upper interval can neither answer (rule c) nor pin (band a)")
    C.ok(P["linearity_check_max_abs"] < 1e-10 and len(P["label_filter_interp"]) == 50 - 18, "coefficient form equals ml2.fit_poly; like-for-like filter interpolated at the 32 couplings without a stored row")
    import run_learn  # noqa: E402
    for stage in ("f2", "f3", "rules"):
        run_learn.main(["--hash=" + sha, "--stage=" + stage, "--out=" + out, "--sets=" + setsp])
    F2 = rdc.rj(os.path.join(out, "f2_floor.json"))["sizes"]["57"]
    lowers = sorted((3.0 if J < 3.0 else 0.3) * 0.06 * abs(exp[57]["m_gs"][J]) for J in rdc.TRAIN_J)
    C.close(F2["floor"], lowers[41], "run_learn f2: the floor is the 42nd narrowest of the 45 lower widths of the sets file", 1e-9)
    F3 = rdc.rj(os.path.join(out, "f3_constructive.json"))
    C.ok(F3["seed"] == int(sha[:8], 16) and F3["sizes"]["57"]["S_p_name"] == "S_3_4" and F3["decision"]["outcome"] in ("PASS", "FAIL")
         and F3["sizes"]["57"]["sets"]["S_1_2"]["status"].startswith("NOT RUN") and F3["sizes"]["57"]["sets"]["S"]["models"]["M0"]["n_splits"] == 200,
         "run_learn f3: seed from the hash, primary set S_3/4, 200 splits, decision %s" % F3["decision"]["outcome"])
    first = json.dumps(F3["sizes"], sort_keys=True)
    run_learn.main(["--hash=" + sha, "--stage=f3", "--out=" + out, "--sets=" + setsp])
    C.ok(json.dumps(rdc.rj(os.path.join(out, "f3_constructive.json"))["sizes"], sort_keys=True) == first, "run_learn f3 is reproducible (same seed, same numbers)")
    R = rdc.rj(os.path.join(out, "f1_rules.json"))["sizes"]["57"]
    C.ok(set(R) >= {"L1", "L2", "L3", "apart"} and "1.5" in R["apart"] and R["L3"]["n_couplings"] == 49, "run_learn rules: L1, L2, L3 and the coupling 1.5 on its own line")
    with open(setsp, "a") as f:
        f.write(" ")
    C.raises(rdc.Refused, lambda: run_learn.main(["--hash=" + sha, "--stage=f3", "--out=" + out, "--sets=" + setsp]), "a sets file that no longer matches its SHA-256 is refused")
    C.raises(rdc.Refused, lambda: run_learn.main(["--hash=" + "1" * 64, "--stage=f2", "--out=" + out]), "run_learn refuses a hash that is not the declaration's")
finally:
    rdc.RD, rdc.PINNED, rdc.project_refs, sys.argv = real
C.done()
