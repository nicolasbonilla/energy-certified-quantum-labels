"""Export the data of main Fig. 4 with the PUBLIC labels added to panel (a) (fig_bias_law_rd.tex).

  python -B -I export_biaslaw_rd.py     (run from anywhere; writes only into this folder)

Nothing physical is recomputed.
  data_biaslaw/*.dat   copied byte for byte from ../data_biaslaw/ (written by phase3/full_runs/bias_law/code/
                       bias_law.py from stored outputs): the curves of the exact 19-site ground state, the chords,
                       the stored emulated states, our device labels, panel (b)
  pub_n<n>_J<Jz>.dat   NEW: the public label of the dataset at the four couplings of panel (a), n = 57 and 115:
                       de = published energy error per site, dm = public label of m_s minus the reference; from
                       phase3/full_runs/real_data/out/predict_real.json, sizes.<n>.P5.rows[Jz=...] (fields de,
                       Delta, curve, ratio), cross-checked with out/map_rows.json (de_real, label_real - O_GS)
Writes export_check.txt.
"""
import hashlib
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.abspath(os.path.join(HERE, "..", "data_biaslaw"))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RD = os.path.join(ROOT, "phase3", "full_runs", "real_data")
COUPLINGS = (1.2, 1.6, 2.5, 4.0)       # the four couplings of panel (a)
LOG = []


def log(s=""):
    print(s)
    LOG.append(s)


def check(cond, what):
    log(("PASS  " if cond else "FAIL  ") + what)
    assert cond, what


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    log("export_biaslaw_rd.py -- data of main Fig. 4 with the public labels (nothing recomputed)")
    log("")
    log("[0] data of the earlier figure, copied unchanged from ../data_biaslaw/")
    dst = os.path.join(HERE, "data_biaslaw")
    os.makedirs(dst, exist_ok=True)
    names = sorted(f for f in os.listdir(OLD) if f.endswith(".dat"))
    for fn in names:
        shutil.copyfile(os.path.join(OLD, fn), os.path.join(dst, fn))
        assert sha(os.path.join(OLD, fn)) == sha(os.path.join(dst, fn)), fn
    check(len(names) == 18, "%d files copied with equal SHA-256 (curve19, chord, states_n57, states_n115 at Jz = 1.2, "
          "1.6, 2.5, 4.0; device; tie115)" % len(names))
    log("")
    log("[1] the public labels at their published energies (panel (a), filled symbols)")
    P = rj(os.path.join(RD, "out", "predict_real.json"))["sizes"]
    MAP = {(r["n"], round(r["Jz"], 1)): r for r in rj(os.path.join(RD, "out", "map_rows.json"))["rows"]
           if r["label"] == "m_s"}
    allv = []
    for n in (57, 115):
        rows = {round(r["Jz"], 1): r for r in P[str(n)]["P5"]["rows"]}
        check(len(rows) == 50, "n = %d: 50 rows of the curve test P5" % n)
        for J in COUPLINGS:
            r, m = rows[J], MAP[(n, J)]
            assert abs(r["de"] - m["de_real"]) < 1e-12, (n, J)
            assert abs(r["Delta"] - (m["label_real"] - m["O_GS"])) < 5e-5, (n, J, r["Delta"], m["label_real"] - m["O_GS"])
            assert r["Delta"] > 0 and r["de_inside_curve"], (n, J)
            with open(os.path.join(HERE, "pub_n%d_J%.1f.dat" % (n, J)), "w", encoding="ascii", newline="\n") as f:
                f.write("# public label of m_s, n = %d, Jz = %.1f: de = published energy error per site, dm = label - reference\n" % (n, J))
                f.write("# source real_data/out/predict_real.json sizes.%d.P5.rows[Jz=%.1f] (de, Delta)\n" % (n, J))
                f.write("de dm\n%r %r\n" % (r["de"], r["Delta"]))
            log("  n = %-3d Jz = %.1f  de = %.6f  label - reference = %.6f (%.3f tau)  19-site curve at that de = %.6f  "
                "ratio = %.4f%s" % (n, J, r["de"], r["Delta"], r["raw_miss_tau"], r["curve"], r["ratio"],
                                    "" if r["decides_ratio"] else "  (not a deciding coupling of the declared test)"))
            allv.append((n, J, r["de"], r["Delta"], r["ratio"], r["decides_ratio"]))
    check(all(4e-4 < v[2] < 0.2 and 1.5e-4 < v[3] < 0.6 for v in allv), "all eight points inside the axes of panel (a)")
    below = [v for v in allv if v[4] < 1]
    above = [v for v in allv if v[4] >= 1]
    check(len(below) == 7 and len(above) == 1 and above[0][:2] == (57, 4.0),
          "seven of the eight public labels lie below the 19-site curve of their coupling (ratio label bias / curve "
          "%.2f-%.2f); the eighth, n = 57 at Jz = 4.0, lies above it (ratio %.2f)"
          % (min(v[4] for v in below), max(v[4] for v in below), above[0][4]))
    check("%.2f" % min(v[4] for v in below) == "0.70" and "%.2f" % max(v[4] for v in below) == "0.86"
          and "%.2f" % above[0][4] == "1.15", "caption: ratios 0.70-0.86 at seven points, 1.15 at n = 57, Jz = 4.0")
    log("")
    log("[2] the declared test of the curve on the public labels (P5), for the caption")
    R = rj(os.path.join(RD, "out", "predict_real.json"))["P5_rule"]
    a57, a115 = P["57"]["P5"]["all"], P["115"]["P5"]["all"]
    log("  outcome %s; mean miss of m_s over the 50 couplings: %.4f -> %.4f tau (n = 57), %.4f -> %.4f tau (n = 115) after "
        "subtracting the curve" % (R["outcome"], a57["mean_raw_miss_tau"], a57["mean_miss_tau"], a115["mean_raw_miss_tau"],
                                   a115["mean_miss_tau"]))
    log("  deciding ratios: n = 57: %d couplings, %.4f-%.4f, %d outside the declared band; n = 115: %d couplings, "
        "%.4f-%.4f, %d outside" % (a57["n_deciding"], a57["ratio_range_deciding"][0], a57["ratio_range_deciding"][1],
                                   len(a57["ratios_outside"]), a115["n_deciding"], a115["ratio_range_deciding"][0],
                                   a115["ratio_range_deciding"][1], len(a115["ratios_outside"])))
    check(R["outcome"] == "FAIL" and len(a57["ratios_outside"]) == 0 and len(a115["ratios_outside"]) == 12
          and a57["n_deciding"] == 22 and a115["n_deciding"] == 19,
          "the declared test FAILS: 0 of 22 deciding ratios outside the band at n = 57, 12 of 19 at n = 115")
    check("%.2f" % a57["mean_raw_miss_tau"] == "0.62" and "%.2f" % a57["mean_miss_tau"] == "0.11" and
          "%.2f" % a115["mean_raw_miss_tau"] == "0.53" and "%.2f" % a115["mean_miss_tau"] == "0.17",
          "mean miss 0.62 -> 0.11 tau (n = 57) and 0.53 -> 0.17 tau (n = 115)")
    log("")
    log("ALL ASSERTIONS PASSED")
    with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
