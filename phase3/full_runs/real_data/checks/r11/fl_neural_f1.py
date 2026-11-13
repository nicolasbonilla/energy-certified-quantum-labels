# R11 fix pass (fixer FL, 2026-11-13). The pilot perceptron ("small neural network") of the declared test (f1) on
# the public labels, completed after the declaration by real_data/f1_neural/ (driver run_f1_neural.py, which only
# starts the sealed scripts of real_data/code/ unchanged): pieces A (n = 57, training range) and B (n = 115, test
# range and training range). Piece C (the dataset paper's architecture 1 at n = 57, test range) finished on
# 2026-11-13 and is read too: its two rows go into the same table file and block 7 prints its numbers (added by
# the coordinator; blocks 1-6 are unchanged).
#
# What this script does (read only, no learning is re-run):
#   1. checks the SHA-256 of the sealed scripts that the driver started against real_data/code/SHA256SUMS*.txt;
#   2. reads f1_neural/out/results_mlp_pilot3_n{57,115}.json (in these files "emulated" means the PUBLIC labels and
#      "exact_control" the DMRG labels, as in the sealed code run with --data=real);
#   3. turns each block into the summary format of out/learn_real.json (summary.<n>.models.<model>.<real|control>.
#      <test|ind>) and checks that the n = 57 test-range block equals the one stored there (it was copied, not re-run);
#   4. writes paper/figures/sm_tables/rdlearn_f1_extra.json (format: docstring of make_rdlearn.py, t_f1) and a copy
#      next to itself (fl_rdlearn_f1_extra.json);
#   5. prints every number that the paper prints from these files, in the paper's rounding (counts exact; medians to
#      the nearest unit of the last digit; ranges rounded outward).
#
# usage:  python -B -I -X utf8 fl_neural_f1.py > fl_neural_f1_out.txt
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(RD, "..", "..", ".."))
OUT = os.path.join(RD, "f1_neural", "out")
TABLES = os.path.join(ROOT, "paper", "figures", "sm_tables")


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dn(x, d=2):
    return math.floor(x * 10 ** d + 1e-9) / 10 ** d


def up(x, d=2):
    return math.ceil(x * 10 ** d - 1e-9) / 10 ** d


def rng(a, d=2):
    return "%.*f-%.*f" % (d, dn(a[0], d), d, up(a[1], d))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# 1. sealed code
print("1. sealed scripts started by f1_neural/run_f1_neural.py, SHA-256 against real_data/code/SHA256SUMS*.txt")
listed = {}
for name in ("SHA256SUMS.txt", "SHA256SUMS_predict_learn.txt"):
    p = os.path.join(RD, "code", name)
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            parts = line.split()
            if len(parts) >= 2:
                listed.setdefault(os.path.basename(parts[-1].lstrip("*")), set()).add(parts[0].lower())
for s in ("rd_learn_parts.py", "rd_learn_ibm.py", "rd_common.py"):
    h = sha(os.path.join(RD, "code", s))
    print("   %-18s %s  listed: %s" % (s, h[:16], "yes, equal" if h in listed.get(s, set()) else
                                        ("NOT EQUAL" if s in listed else "not listed")))

# 2-3. results -> summary format
L = rj(os.path.join(RD, "out", "learn_real.json"))
KEY = {("real", "test"): "ood_emulated", ("real", "ind"): "indist_emulated",
       ("control", "test"): "ood_exact_control", ("control", "ind"): "indist_exact_control"}
extra = {}
blocks = {}
for n in ("57", "115"):
    R = rj(os.path.join(OUT, "results_mlp_pilot3_n%s.json" % n))["sizes"][n]["models"]["mlp_pilot3"]
    for (lab, rg), k in KEY.items():
        rows, s = R[k]["rows"], R[k]["summary"]
        d = {"n": len(rows),
             "truth_covered": sum(1 for r in rows if r["covM_truth"]),
             "label_covered": sum(1 for r in rows if r["covM_emu"]),
             "site_truth": s["covZ_truth"], "site_label": s["covZ_emu"],
             "width_tau": s["widthM_tau_range"], "site_width_tau_median": s["widthZ_tau_median"],
             "miss_tau": s["miss_ms_over_tau_range"],
             "n_miss_above_tau": sum(1 for r in rows if r["miss_ms_over_tau"] > 1.0)}
        assert d["n"] == s["n_cases"]
        assert abs(d["truth_covered"] / d["n"] - s["covM_truth"]) < 1e-12
        assert abs(d["label_covered"] / d["n"] - s["covM_emu"]) < 1e-12
        blocks[(n, lab, rg)] = (d, s, rows)
        stored = (L["summary"].get(n, {}).get("models", {}).get("mlp_pilot3") or {}).get(lab, {}).get(rg)
        if stored is not None:
            same = all((abs(stored[f] - d[f]) < 1e-12) if not isinstance(d[f], list) else
                       all(abs(a - b) < 1e-12 for a, b in zip(stored[f], d[f])) for f in d)
            print("3. n = %s, %s, %s: already in learn_real.json; recomputed block equal: %s" % (n, lab, rg, same))
            continue
        extra["%s|mlp_pilot3|%s|%s" % (n, lab, rg)] = d

# piece C: the dataset paper's architecture 1 (our implementation), n = 57, test couplings only
C = rj(os.path.join(OUT, "results_ibm57.json"))["sizes"]["57"]["models"]["ibm_arch1"]
blocksC = {}
for lab, k in (("real", "ood_emulated"), ("control", "ood_exact_control")):
    rows, s = C[k]["rows"], C[k]["summary"]
    d = {"n": len(rows),
         "truth_covered": sum(1 for r in rows if r["covM_truth"]),
         "label_covered": sum(1 for r in rows if r["covM_emu"]),
         "site_truth": s["covZ_truth"], "site_label": s["covZ_emu"],
         "width_tau": s["widthM_tau_range"], "site_width_tau_median": s["widthZ_tau_median"],
         "miss_tau": s["miss_ms_over_tau_range"],
         "n_miss_above_tau": sum(1 for r in rows if r["miss_ms_over_tau"] > 1.0)}
    assert d["n"] == s["n_cases"] == 4 and [r["Jz"] for r in rows] == [1.1, 1.2, 1.3, 1.4]
    assert abs(d["truth_covered"] / d["n"] - s["covM_truth"]) < 1e-12
    assert abs(d["label_covered"] / d["n"] - s["covM_emu"]) < 1e-12
    blocksC[lab] = (d, s, rows)
    extra["57|ibm_arch1|%s|test" % lab] = d

meta = {"_source": "phase3/full_runs/real_data/f1_neural/out/results_mlp_pilot3_n57.json, _n115.json and results_ibm57.json, written "
                   "by the sealed scripts started by f1_neural/run_f1_neural.py after the declaration; converted by "
                   "phase3/full_runs/real_data/checks/r11/fl_neural_f1.py"}
for path in (os.path.join(TABLES, "rdlearn_f1_extra.json"), os.path.join(HERE, "fl_rdlearn_f1_extra.json")):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dict(meta, **extra), f, indent=1, sort_keys=True)
print("4. wrote rdlearn_f1_extra.json with the blocks:", ", ".join(sorted(extra)))

# 5. printed numbers
print()
print("5. small neural network (pilot perceptron), standard intervals at nominal level 0.9 (plain jackknife)")
for n in ("57", "115"):
    print("==================== n = %s" % n)
    for lab, name in (("real", "public labels"), ("control", "DMRG labels (control)")):
        d, s, rows = blocks[(n, lab, "ind")]
        print("  training range, %s: held-out public labels inside %d of %d ; truth inside %d of %d"
              % (name, d["label_covered"], d["n"], d["truth_covered"], d["n"]))
        print("      width of the m_s interval: median %.4f tau (PRINTED %.2f tau), range %.4f-%.4f tau (PRINTED %s)"
              % (s["widthM_tau_median"], s["widthM_tau_median"], d["width_tau"][0], d["width_tau"][1],
                 rng(d["width_tau"], 3)))
        print("      miss of the truth: %.4f-%.4f tau (PRINTED %s) ; above tau at %d of %d ; site labels / true site "
              "values inside %.3f / %.3f" % (d["miss_tau"][0], d["miss_tau"][1], rng(d["miss_tau"]),
                                             d["n_miss_above_tau"], d["n"], d["site_label"], d["site_truth"]))
        inside = [r["Jz"] for r in rows if r["covM_truth"]]
        print("      truth inside at Jz =", inside)
    for lab, name in (("real", "public labels"), ("control", "DMRG labels (control)")):
        d, s, rows = blocks[(n, lab, "test")]
        print("  test couplings 1.1-1.4, %s: truth inside %d of %d ; held-out public labels inside %d of %d ; miss "
              "%.4f-%.4f tau (PRINTED %s) ; width median %.4f tau" % (
                  name, d["truth_covered"], d["n"], d["label_covered"], d["n"], d["miss_tau"][0], d["miss_tau"][1],
                  rng(d["miss_tau"]), s["widthM_tau_median"]))

print()
print("6. comparison with the cubic model (out/learn_real.json summary.<n>.models.poly3_invJ.real.ind)")
for n in ("57", "115"):
    c = L["summary"][n]["models"]["poly3_invJ"]["real"]["ind"]
    w = L["sealed"]["results_cheap"]["sizes"][n]["models"]["poly3_invJ"]["indist_emulated"]["summary"]
    dnet, snet, _ = blocks[(n, "real", "ind")]
    print("  n = %s: cubic labels %d, truth %d of 45, width median %.4f tau (range %.4f-%.4f) ; network labels %d, "
          "truth %d of 45, width median %.4f tau ; network median / cubic median = %.2f"
          % (n, c["label_covered"], c["truth_covered"], w["widthM_tau_median"], c["width_tau"][0], c["width_tau"][1],
             dnet["label_covered"], dnet["truth_covered"], snet["widthM_tau_median"],
             snet["widthM_tau_median"] / w["widthM_tau_median"]))

print()
print("7. the dataset paper's architecture 1 (our implementation), n = 57, test couplings 1.1-1.4, standard intervals "
      "at nominal level 0.9 (plain jackknife); file f1_neural/out/results_ibm57.json")
for lab, name in (("real", "public labels"), ("control", "DMRG labels (control)")):
    d, s, rows = blocksC[lab]
    print("  %s: truth inside %d of %d ; held-out public labels inside %d of %d ; miss of the truth %.4f-%.4f tau "
          "(PRINTED %s) ; above tau at %d of %d" % (name, d["truth_covered"], d["n"], d["label_covered"], d["n"],
                                                    d["miss_tau"][0], d["miss_tau"][1], rng(d["miss_tau"]),
                                                    d["n_miss_above_tau"], d["n"]))
    print("      width of the m_s interval: %.4f-%.4f tau (PRINTED %s), median %.4f tau ; site labels / true site "
          "values inside %.3f / %.3f ; error against the truth %.1f-%.1f %%"
          % (d["width_tau"][0], d["width_tau"][1], rng(d["width_tau"], 3), s["widthM_tau_median"], d["site_label"],
             d["site_truth"], s["err_ms_vs_truth_pct_range"][0], s["err_ms_vs_truth_pct_range"][1]))
print("  computing time of the sealed script for this piece: %.0f s" % C["secs"])
