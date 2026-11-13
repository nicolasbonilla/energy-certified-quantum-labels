# real_data / run_predict.py  (own code; 2026-11-12; task rd-code-learn)   ENTRY POINT, DECLARATION.md Secs. 5 and 6
#
#   python -B -I run_predict.py --hash=<SHA-256 of DECLARATION.md> [--root=<work/>] [--out=<dir>] [--sets=<S_sets.json>]
#                               [--converted=<dir>] [--no-variant]
#
# REFUSES to read converted/ unless real_data/DECLARATION.sha256 exists, equals the SHA-256 of DECLARATION.md and
# equals --hash (exit code 3, nothing read). Reads: converted/real_n{57,115}.json (through rd_common.load_real),
# out/n19/n19_curves.json (exact n = 19, no real datum), this project's graph files and summary_map.json, and, if
# present, out/S_sets.json with out/S_sets.sha256 (kept set of the filter, for the n = 19 comparison of Sec. 6).
# Writes <out>/predict_results.json (default out = real_data/out/predict). Prints a summary.
import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rd_common as rdc  # noqa: E402
import rd_predict as rp  # noqa: E402

SEEN = dict(
    P1_P3="seen before the hash: sites at 14 couplings per size (F8) and the sign of m_s (F7); not seen: edges, second "
          "neighbours, loops",
    P4="seen before the hash: m_s (F7); not seen: the four families",
    P5="seen before the hash: Delta and de_real separately at all 100 points, and which couplings have a raw miss above "
       "0.2 tau; not computed before: any ratio or corrected miss",
    n19_comparison="descriptive, no rule; the n = 19 values involve no real datum")


def main(argv):
    arg = {a.split("=")[0][2:]: a.split("=", 1)[1] for a in argv if a.startswith("--") and "=" in a}
    root = os.path.abspath(arg.get("root", rdc.ROOT_DEFAULT))
    out_dir = os.path.abspath(arg.get("out", os.path.join(rdc.RD, "out", "predict")))
    if "hash" not in arg:
        raise rdc.Refused("--hash=<SHA-256 of the hashed declaration> is required.")
    gate = rdc.require_declaration_hash(rdc.RD, arg["hash"])           # nothing of converted/ is opened before this line
    n19_dir = os.path.join(rdc.RD, "out", "n19")
    C19 = rdc.rj(os.path.join(n19_dir, "n19_curves.json"))
    sets_path = arg.get("sets", os.path.join(rdc.RD, "out", "S_sets.json"))
    res = dict(declaration_sha256=gate.sha, n19_curves_sha256=rdc.sha256_file(os.path.join(n19_dir, "n19_curves.json")),
               seen=SEEN, sizes={}, variant_post_select={})
    for n in (57, 115):
        sets = rdc.load_sets(sets_path, n, gate) if os.path.exists(sets_path) else None
        rd = rdc.load_real(n, gate, root, arg.get("converted"))
        res["sizes"][str(n)] = rp.analyse_size(rd, C19, sets)
    res["P5_rule"] = rp.p5_rule(res["sizes"]["57"]["P5"]["all"], res["sizes"]["115"]["P5"]["all"])
    res["P5_rule_training_45_reported_only"] = rp.p5_rule(res["sizes"]["57"]["P5"]["training_45"],
                                                         res["sizes"]["115"]["P5"]["training_45"])
    if "--no-variant" not in argv:                                     # secondary: comparison variant, n = 115 only
        rdv = rdc.load_real(115, gate, root, arg.get("converted"), group="skqd_post_select")
        res["variant_post_select"]["115"] = (rp.analyse_size(rdv, C19, None) if rdv.labelled()
                                             else dict(note="no labels in this group"))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "predict_results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    report(res)
    return res


def report(res):
    for n, S in res["sizes"].items():
        print("n = %s (%d couplings; orientation +1 everywhere: %s)" % (n, S["n_couplings"], S["orientation_all_plus"]))
        for fam, r in S["P1_P3"].items():
            print("  P1-P3 %-18s F = %.4f over %d pairs -> %s | t <= 1: %.4f | undefined: %d" % (
                fam, r["F"], r["n_pairs"], "HOLDS" if r["holds"] else "DOES NOT HOLD", r["frac_t_le_1"], r["n_undefined"]))
        for fam, r in S["P4"].items():
            print("  P4    %-18s Spearman(D, Jz) = %+.4f -> %s | D from %.3f to %.3f" % (
                fam, r["spearman"], "HOLDS" if r["holds"] else "DOES NOT HOLD", r["D_min"], r["D_max"]))
        for k in ("all", "training_45"):
            s = S["P5"][k]
            print("  P5 %-11s mean miss %.3f tau (limit %.1f; raw %.3f, chord %.3f, n = 19 truth %.3f) | ratios at %d deciding "
                  "couplings: %s, outside [0.75, 1.3] at %s" % (k, s["mean_miss_tau"], s["mean_miss_limit"], s["mean_raw_miss_tau"],
                                                              s["mean_miss_chord_tau"], s["mean_miss_n19_truth_tau"],
                                                              s["n_deciding"], s["ratio_range_deciding"], s["ratios_outside"]))
        c = S["n19_comparison"]
        print("  n = 19 against the truth, in tau: test couplings %s | largest over all %.3f | over the kept labels: %s" % (
            {k: round(v, 3) for k, v in c["at_test"].items()}, c["max_all"], c.get("max_over_kept")))
    print("P5 rule (50 couplings of each size): %s" % res["P5_rule"]["outcome"])
    print("P5 rule on the 45 training couplings (reported, does not decide): %s" % res["P5_rule_training_45_reported_only"]["outcome"])


if __name__ == "__main__":
    main(sys.argv[1:])
