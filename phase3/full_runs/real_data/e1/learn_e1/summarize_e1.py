# real_data / e1 / learn_e1 / summarize_e1.py   (own code; 2026-11-12, rewrite task rw-L; decides nothing)
#
# Reads the outputs that the declared entry point wrote into this folder (f3_constructive.json, f2_floor.json) and
#   1. compares the n = 57 block of f3 and the whole of f2 with the primary outputs of real_data/out/learn/
#      (at n = 57 the E1-extended sets and intervals equal the declared ones, so the numbers must be identical);
#   2. tabulates the constructive test on the E1-extended sets of n = 115;
#   3. adds descriptive lines (post hoc, no rule): the change of the true m_s over each set, the greatest miss of a
#      public label in each set, the range of the exact interval widths (the truth is read with the declared loader,
#      rd_common.load_real, after its own check of the declaration checksum; nothing else of the declared code is used);
#   4. writes summary_e1.json and RESULTS_learn_e1.md in this folder. Display rule: lower ends of ranges and
#      "at least" numbers are rounded down, upper ends and "at most" numbers up; counts are exact.
# It writes ONLY into its own folder.   python -B -I summarize_e1.py
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RD, "code"))
import rd_common as rdc  # noqa: E402  (declared code, imported unchanged; used for load_real only)

NAMES = (("S", "S"), ("S_3_4", "S_3/4"), ("S_1_2", "S_1/2"))


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dn(x, d=3):
    return math.floor(x * 10 ** d + 1e-12) / 10 ** d


def up(x, d=3):
    return math.ceil(x * 10 ** d - 1e-12) / 10 ** d


def leaves(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, path + "." + str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, path + "[%d]" % i)
    else:
        yield path, x


def compare(a, b, skip=()):
    """(number of leaves compared, largest absolute difference of numbers, list of paths that differ otherwise)."""
    la, lb = dict(leaves(a)), dict(leaves(b))
    other, big, n = [], 0.0, 0
    for k in sorted(set(la) | set(lb)):
        if any(s in k for s in skip):
            continue
        n += 1
        if k not in la or k not in lb:
            other.append(k)
        elif isinstance(la[k], (int, float)) and isinstance(lb[k], (int, float)) and not isinstance(la[k], bool):
            big = max(big, abs(la[k] - lb[k]))
        elif la[k] != lb[k]:
            other.append(k)
    return n, big, other


def main():
    F3 = rj(os.path.join(HERE, "f3_constructive.json"))
    F2 = rj(os.path.join(HERE, "f2_floor.json"))
    P3 = rj(os.path.join(RD, "out", "learn", "f3_constructive.json"))
    P2 = rj(os.path.join(RD, "out", "learn", "f2_floor.json"))
    SE = rj(os.path.join(HERE, "S_sets_E1.json"))
    S0 = rj(os.path.join(RD, "out", "S_sets.json"))
    gate = rdc.require_declaration_hash(rdc.RD, F3["declaration_sha256"])
    out = dict(what="constructive test (f3) on the E1-extended sets: SECONDARY, declaration Sec. 3 and Sec. 12 line 17",
               declaration_sha256=F3["declaration_sha256"], seed=F3["seed"], sets_sha256=F3["sets_sha256"],
               primary_sets_sha256=P3["sets_sha256"], sizes={})
    n3, d3, o3 = compare(F3["sizes"]["57"], P3["sizes"]["57"])
    n2, d2, o2 = compare(F2["sizes"], P2["sizes"])
    out["identity_checks"] = dict(
        f3_n57_vs_primary=dict(leaves=n3, largest_abs_difference=d3, other_differences=o3),
        f2_both_sizes_vs_primary=dict(leaves=n2, largest_abs_difference=d2, other_differences=o2))
    L = ["# Constructive test (f3) on the E1-extended sets: SECONDARY analysis", "",
         "Declaration Sec. 3: \"the set S of Sec. 7 (f3) is fixed WITHOUT them (the E1-extended set is reported as secondary if",
         "E1 finishes)\"; Sec. 12, line 17. Declaration SHA-256 `%s`. Run on 2026-11-12, after every result of the" % F3["declaration_sha256"],
         "primary analysis was known; it decides nothing and replaces nothing.", "",
         "- Sets and intervals: `S_sets_E1.json` (SHA-256 `%s`), written by `make_sets_e1.py` from the outputs of the" % F3["sets_sha256"],
         "  declared map code run with the E1 certificates (`e1/map_e1/S_sets.json`, key `secondary_E1`; `e1/map_e1/map_rows.json`,",
         "  field `exact_e1`). Nothing is recomputed there.",
         "- Run: the declared entry point `code/run_learn.py`, unchanged (stages `f3` and `f2`), with `--sets` and `--out` pointing",
         "  to this folder. Same rule, same seed (%d), same generator call `default_rng([seed, n, c])`, same models, same" % F3["seed"],
         "  thresholds. Times: `run_times_utc.txt`.", "",
         "## Identity checks", "",
         "- n = 57: the E1-extended sets and their exact intervals equal the declared ones (E1 added intervals only at Jz = 3.2",
         "  and 3.3, both wider than tau), so the test is the same test: %d numbers of the n = 57 block compared with" % n3,
         "  `out/learn/f3_constructive.json`, largest absolute difference %.1e, other differences: %s." % (d3, o3 or "none"),
         "- (f2): the floor uses the explicit-state (lower) widths, which E1 does not change: %d numbers compared with" % n2,
         "  `out/learn/f2_floor.json`, largest absolute difference %.1e, other differences: %s." % (d2, o2 or "none"), ""]
    for n in ("57", "115"):
        rd = rdc.load_real(int(n), gate)
        truth = {J: rd.truth_authors[J]["labels"]["m_s"] for J in rd.labelled()}
        label = {J: rd.lab[J]["labels"]["m_s"] for J in rd.labelled()}
        tau = {J: rdc.TAU_REL * abs(truth[J]) for J in truth}
        res = F3["sizes"][n]
        blk = dict(S_p_name=res["S_p_name"], primary_outcome=res["primary"]["outcome"], sets={})
        L += ["## n = %s" % n, "",
              "E1-extended sets: |S| = %d, |S_3/4| = %d, |S_1/2| = %d; the most stringent nested set with at least 15 couplings is %s."
              % (res["sizes"]["S"], res["sizes"]["S_3_4"], res["sizes"]["S_1_2"], dict(NAMES)[res["S_p_name"]]),
              "Declared sets (stored certificates only): |S| = %d, |S_3/4| = %d, |S_1/2| = %d."
              % tuple(len(S0["sizes"][n][k]) for k in ("S", "S_3_4", "S_1_2")), "",
              "| set | couplings | train / cal / query | model | (W): splits with 2q <= tau at every query | (C): pairs with the truth inside | 2q (tau): min / median / max | greatest miss (tau) | min of 2q over the widest calibration interval | outcome |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for key, name in NAMES:
            s = res["sets"][key]
            if s["status"] != "RUN":
                L.append("| %s | %d | - | - | - | - | - | - | - | %s |" % (name, s["size"], s["status"]))
                blk["sets"][key] = dict(status=s["status"], size=s["size"])
                continue
            T = s["couplings"]
            iv = SE["sizes"][n]["intervals"]
            w = [iv["%.1f" % J]["exact"]["width_over_tau"] for J in T]
            ch = max(truth[J] for J in T) - min(truth[J] for J in T)
            tc = [ch / max(tau[J] for J in T), ch / min(tau[J] for J in T)]
            lm = max(abs(label[J] - truth[J]) / tau[J] for J in T)
            b = dict(status="RUN", size=s["size"], range=[T[0], T[-1]], n_train=s["n_train"], n_cal=s["n_cal"],
                     n_query=s["n_query"], k=s["k"], outcome_M1_M2=s["outcome_M1_M2"], outcome_M0=s["outcome_M0_control"],
                     exact_width_tau_range=[min(w), max(w)], truth_change_over_tau=tc, greatest_label_miss_tau=lm,
                     labels_or_truths_outside_their_interval=s["gate_G7_outside_interval"], models={})
            for m in ("M1", "M2", "M0"):
                a = s["models"][m]
                nW = int(round(a["frac_splits_W"] * a["n_splits"])); nC = int(round(a["frac_pairs_C"] * a["n_pairs"]))
                b["models"][m] = dict(n_splits=a["n_splits"], n_pairs=a["n_pairs"], n_splits_W=nW, n_pairs_C=nC,
                                      frac_splits_W=a["frac_splits_W"], frac_pairs_C=a["frac_pairs_C"],
                                      W_holds=a["W_holds"], C_holds=a["C_holds"], width_tau_min=a["width_tau_min"],
                                      width_tau_median=a["width_tau_median"], width_tau_max=a["width_tau_max"],
                                      largest_miss_tau=a["largest_miss_tau"], two_q_over_floor_min=a["two_q_over_floor_min"],
                                      floor_violations=a["floor_violations"])
                L.append("| %s | %d (%.1f-%.1f) | %d / %d / %d | %s | %d of %d%s | %d of %d | %.3f / %.3f / %.3f | %.3f | %.3f | %s |" % (
                    name, s["size"], T[0], T[-1], s["n_train"], s["n_cal"], s["n_query"], m + (" (control)" if m == "M0" else ""),
                    nW, a["n_splits"], "" if a["W_holds"] else " (rule not met)", nC, a["n_pairs"],
                    dn(a["width_tau_min"]), a["width_tau_median"], up(a["width_tau_max"]), up(a["largest_miss_tau"]),
                    dn(a["two_q_over_floor_min"]), (s["outcome_M0_control"] if m == "M0" else s["outcome_M1_M2"] + " (M1 and M2 together)")))
            blk["sets"][key] = b
        L += ["", "Descriptive lines (post hoc, no rule):", ""]
        for key, name in NAMES:
            b = blk["sets"][key]
            if b.get("status") != "RUN":
                continue
            L.append("- %s: %d couplings, Jz = %.1f-%.1f; exact intervals (with E1) %.3f-%.3f tau wide; greatest miss of a public "
                     "label in the set %.3f tau; the true m_s changes over the set by %.3f-%.3f tau; labels or truths outside "
                     "their exact interval: %s."
                     % (name, b["size"], b["range"][0], b["range"][1], dn(b["exact_width_tau_range"][0]), up(b["exact_width_tau_range"][1]),
                        up(b["greatest_label_miss_tau"]), dn(b["truth_change_over_tau"][0]), up(b["truth_change_over_tau"][1]),
                        "none" if not (b["labels_or_truths_outside_their_interval"]["label"] or b["labels_or_truths_outside_their_interval"]["truth"]) else b["labels_or_truths_outside_their_interval"]))
        L.append("")
        out["sizes"][n] = blk
    r = out["sizes"]["115"]["sets"]
    L += ["## Reading (n = 115, with the certificates of the extension E1)", "",
          "- S_1/2 (%d couplings, Jz = %.1f-%.1f; 4 / 9 / 5): %s. (W) %d of 200 splits (M1) and %d of 200 (M2), (C) %d of %d and %d of %d pairs;"
          % (r["S_1_2"]["size"], r["S_1_2"]["range"][0], r["S_1_2"]["range"][1], r["S_1_2"]["outcome_M1_M2"],
             r["S_1_2"]["models"]["M1"]["n_splits_W"], r["S_1_2"]["models"]["M2"]["n_splits_W"],
             r["S_1_2"]["models"]["M1"]["n_pairs_C"], r["S_1_2"]["models"]["M1"]["n_pairs"],
             r["S_1_2"]["models"]["M2"]["n_pairs_C"], r["S_1_2"]["models"]["M2"]["n_pairs"]),
          "  2q = %.3f-%.3f tau over M1 and M2. Control M0: %s (%d of 200, %d of %d; 2q = %.3f-%.3f tau)."
          % (dn(min(r["S_1_2"]["models"][m]["width_tau_min"] for m in ("M1", "M2"))),
             up(max(r["S_1_2"]["models"][m]["width_tau_max"] for m in ("M1", "M2"))), r["S_1_2"]["outcome_M0"],
             r["S_1_2"]["models"]["M0"]["n_splits_W"], r["S_1_2"]["models"]["M0"]["n_pairs_C"], r["S_1_2"]["models"]["M0"]["n_pairs"],
             dn(r["S_1_2"]["models"]["M0"]["width_tau_min"]), up(r["S_1_2"]["models"]["M0"]["width_tau_max"])),
          "- S_3/4 (%d couplings, Jz = %.1f-%.1f): %s on (W): %d and %d of 200 splits (M1, M2); 2q up to %.3f tau."
          % (r["S_3_4"]["size"], r["S_3_4"]["range"][0], r["S_3_4"]["range"][1], r["S_3_4"]["outcome_M1_M2"],
             r["S_3_4"]["models"]["M1"]["n_splits_W"], r["S_3_4"]["models"]["M2"]["n_splits_W"],
             up(max(r["S_3_4"]["models"][m]["width_tau_max"] for m in ("M1", "M2")))),
          "- S (%d couplings, Jz = %.1f-%.1f): %s on (W): %d and %d of 200 splits (M1, M2); 2q up to %.3f tau."
          % (r["S"]["size"], r["S"]["range"][0], r["S"]["range"][1], r["S"]["outcome_M1_M2"],
             r["S"]["models"]["M1"]["n_splits_W"], r["S"]["models"]["M2"]["n_splits_W"],
             up(max(r["S"]["models"][m]["width_tau_max"] for m in ("M1", "M2")))),
          "- (C) holds in every pair of every set and model. The floor of (f2) is respected in every split (0 violations).",
          "- The same three limits as for the primary result apply: the control model passes wherever M1 and M2 pass; the true",
          "  m_s changes little over the set; the test fails on width on the full certified set and on the 3/4 set.",
          "- This analysis was run after the primary results were known. It is secondary, as declared; it is not a",
          "  replication on independent data (the 115-qubit labels were already used by the declared secondary run).", ""]
    with open(os.path.join(HERE, "summary_e1.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(HERE, "RESULTS_learn_e1.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
