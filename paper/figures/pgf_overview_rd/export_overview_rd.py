"""Export the data of main Fig. 1 on the PUBLIC data (fig_overview_rd.tex).

  python -B -I export_overview_rd.py     (run from anywhere; writes only into this folder)

Panel (a) is a schematic (no data). Panel (b) is unchanged: its b_*.dat files are copied byte for byte from
../pgf_overview/ (written there by export_overview.py from summary_map.json and summary_huang.json).
Panel (c) is new, on the public labels of the 57-qubit dataset; nothing physical is recomputed:
  phase3/full_runs/real_data/out/learn/results_cheap.json   sizes.57.models.poly3_invJ: the cubic model in 1/Jz
        trained on the 45 public labels, its standard 90 % interval, the reference and the labels (the keys
        *_emulated of that file hold the PUBLIC labels: the declared script is the stored one with the labels
        replaced), the control trained on DMRG labels; coverage counts
  phase3/full_runs/real_data/out/map_rows.json              m_s rows, n = 57: status, exact interval (certified),
        labels of the two explicit states (lower.witness)
The model curve is the least-squares cubic in 1/Jz of ml2.fit_poly (ridge 1e-8), refitted here on the 45 stored
public labels only to draw it between the couplings; it is asserted equal to the stored predictions at the four
test couplings.
Writes b_*.dat (copies), c_*.dat and export_check.txt; since 2026-11-13 (F2) also c_bars_notcert.dat, c_bars_undec.tex,
c_bars_kept.tex, c_cut.dat (bars by status, break marks) and overview_rd_values.tex (the counts printed in panel (c)).
"""
import hashlib
import json
import math
import os
import shutil
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.abspath(os.path.join(HERE, "..", "pgf_overview"))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RD = os.path.join(ROOT, "phase3", "full_runs", "real_data")
NAN = float("nan")
YMIN, YMAX = 0.33, 1.12      # vertical axis of panel (c) (F2 2026-11-13; before: 0.38, 1.05)
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


def fmt(v):
    if isinstance(v, (int, np.integer)):
        return "%d" % v
    if isinstance(v, float) and math.isnan(v):
        return "nan"
    return repr(float(v))


def wdat(name, header, cols, rows):
    with open(os.path.join(HERE, name), "w", encoding="ascii", newline="\n") as f:
        for h in header:
            f.write("# " + h + "\n")
        f.write(" ".join(cols) + "\n")
        for r in rows:
            f.write(" ".join(fmt(v) for v in r) + "\n")
    return name


def up(x, d):
    return math.ceil(x * 10 ** d - 1e-9) / 10 ** d


def down(x, d):
    return math.floor(x * 10 ** d + 1e-9) / 10 ** d


def main():
    log("export_overview_rd.py -- data of main Fig. 1 on the public data (nothing recomputed)")
    log("")
    log("[0] panel (b): files copied unchanged from ../pgf_overview/")
    for fn in sorted(f for f in os.listdir(OLD) if f.startswith("b_") and f.endswith(".dat")):
        shutil.copyfile(os.path.join(OLD, fn), os.path.join(HERE, fn))
        check(sha(os.path.join(OLD, fn)) == sha(os.path.join(HERE, fn)), "%s copied, SHA-256 %s" % (fn, sha(os.path.join(HERE, fn))[:16]))
    with open(os.path.join(OLD, "export_check.txt"), encoding="utf-8") as f:
        old_check = f.read()
    check("rows n=19,57,115, Jz=4" in old_check, "the check log of the earlier figure names the rows of panel (b): 'rows n=19,57,115, Jz=4'")
    log("  (b) quoted from ../pgf_overview/export_check.txt: heavy-hex XXZ rows n=19,57,115, Jz=4 (de_star_out, de_star_in); "
        "benchmark instances of summary_huang.json")
    log("")

    C = rj(os.path.join(RD, "out", "learn", "results_cheap.json"))
    S = C["sizes"]["57"]
    M = S["models"]["poly3_invJ"]
    R = sorted((r for r in rj(os.path.join(RD, "out", "map_rows.json"))["rows"] if r["n"] == 57 and r["label"] == "m_s"),
               key=lambda r: r["Jz"])
    MAP = {round(r["Jz"], 1): r for r in R}
    log("[1] panel (c): the cubic model on the 45 public labels (n = 57)")
    check(abs(C["alpha"] - 0.1) < 1e-15 and abs(C["tau_rel"] - 0.06) < 1e-15, "alpha = 0.1 (standard 90 %% interval), tau = 0.06 |m_s|")
    tr, od = M["indist_emulated"]["rows"], M["ood_emulated"]["rows"]
    Jtr, Jod = [r["Jz"] for r in tr], [r["Jz"] for r in od]
    check(len(tr) == 45 and Jtr == S["train"] and abs(Jtr[0] - 1.6) < 1e-9 and abs(Jtr[-1] - 6.0) < 1e-9,
          "45 training couplings, Jz = 1.6-6.0")
    check(Jod == [1.1, 1.2, 1.3, 1.4] == S["ood"], "four test couplings, Jz = 1.1-1.4")
    dl = max(abs(r["m_s_emu"] - MAP[round(r["Jz"], 1)]["label_real"]) for r in tr + od)
    dt = max(abs(r["m_s_truth"] - MAP[round(r["Jz"], 1)]["O_GS"]) for r in tr + od)
    check(dl < 1e-12, "the labels of the learning file are the published labels of the map rows (max |diff| = %.1e)" % dl)
    check(dt < 5e-5, "the reference of the learning file (the authors' DMRG) and the reference of the map rows differ by at most %.1e" % dt)
    # the drawn curve: fit_poly of ml2.py (cubic in 1/Jz, ridge 1e-8) on the 45 stored public labels
    u = 1.0 / np.array(Jtr)
    X = np.vander(u, 4)
    W = np.linalg.solve(X.T @ X + 1e-8 * np.eye(4), X.T @ np.array([r["m_s_emu"] for r in tr]))
    f = lambda J: np.vander(1.0 / np.atleast_1d(J), 4) @ W
    dp = max(abs(float(f(r["Jz"])[0]) - r["m_s_pred"]) for r in od)
    check(dp < 1e-9, "refitted cubic = stored predictions at the four test couplings (max |diff| = %.1e)" % dp)
    q = od[0]["qM"]
    check(all(r["qM"] == q for r in od), "half-width of the standard interval at the test couplings: q = %.6f (one value)" % q)
    grid = np.round(np.linspace(1.05, 6.05, 201), 6)
    pred = f(grid)
    wdat("c_model.dat", ["Fig. 1(c): cubic in 1/Jz fitted to the 45 public labels (fit_poly, ridge 1e-8) on a 201-point grid;",
                         "lo, hi = pred -+ q, q = ood_emulated.rows[*].qM of results_cheap.json"],
         ["J", "lo", "pred", "hi"], [(J, p - q, p, p + q) for J, p in zip(grid, pred)])
    wdat("c_truth.dat", ["Fig. 1(c): reference m_s (the authors' DMRG) at the 49 couplings of the learning file "
                         "(rows m_s_truth)"], ["J", "ms"], [(r["Jz"], r["m_s_truth"]) for r in od + tr])
    wdat("c_labels_train.dat", ["Fig. 1(c): the 45 public training labels (rows m_s_emu of indist_emulated)"],
         ["J", "ms"], [(r["Jz"], r["m_s_emu"]) for r in tr])
    wdat("c_labels_test.dat", ["Fig. 1(c): the public labels at the four test couplings (rows m_s_emu of ood_emulated)"],
         ["J", "ms"], [(r["Jz"], r["m_s_emu"]) for r in od])
    so, si = M["ood_emulated"]["summary"], M["indist_emulated"]["summary"]
    miss = [r["miss_ms_over_tau"] for r in od]
    check("%.2f" % down(min(miss), 2) == "2.28" and "%.2f" % up(max(miss), 2) == "3.73",
          "caption: the model misses the reference by 2.28-3.73 tau at the test couplings (%s)" % ", ".join("%.4f" % m for m in miss))
    wtr, wod = si["widthM_tau_median"], so["widthM_tau_range"]
    log("  width of the standard interval of m_s: median %.4f tau in the training range (range %.4f-%.4f); %.4f-%.4f tau "
        "at the test couplings" % (wtr, si["widthM_tau_range"][0], si["widthM_tau_range"][1], wod[0], wod[1]))
    check("%.1f" % wtr == "0.1" and "%.2f" % up(wod[1], 2) == "0.17" and "%.2f" % up(si["widthM_tau_range"][1], 2) == "0.15",
          "caption: standard interval about 0.1 tau wide (at most 0.15 tau in the training range, 0.17 tau at the test couplings)")
    log("")

    log("[2] panel (c): the label filter and the intervals")
    kept = [r for r in R if r["status"] == "CERTIFIED_EXACT"]
    drop = [r for r in R if r["training"] and r["status"] != "CERTIFIED_EXACT"]
    und = [r for r in drop if r["status"] == "GRAY"]
    check(len(kept) == 26 and all(r["training"] for r in kept) and len(drop) == 19 and len(und) == 3,
          "filter: keeps 26 of the 45 training labels (Jz = %.1f-%.1f), drops 19 (Jz = %.1f-%.1f; 16 not certified, 3 undecided)"
          % (kept[0]["Jz"], kept[-1]["Jz"], drop[0]["Jz"], drop[-1]["Jz"]))
    teal, grey = [], []
    for r in kept:
        ex = r["exact"]
        assert ex["hi"] - ex["lo"] <= r["tau"] and ex["lo"] <= r["label_real"] <= ex["hi"] and ex["lo"] <= r["O_GS"] <= ex["hi"]
        teal += [(r["Jz"], ex["lo"]), (r["Jz"], ex["hi"]), (NAN, NAN)]
    for r in R:
        if r["status"] == "CERTIFIED_EXACT":
            continue
        w = r["lower"]["witness"]
        assert w[0] <= r["label_real"] <= w[1] and w[0] <= r["O_GS"] <= w[1], r["Jz"]
        grey += [(r["Jz"], w[0]), (r["Jz"], w[1]), (NAN, NAN)]
    wdat("c_bars_teal.dat", ["Fig. 1(c): exact interval [exact.lo, exact.hi] of the 26 certified labels (kept)"], ["J", "ms"], teal)
    wdat("c_bars_grey.dat", ["Fig. 1(c): labels of the two explicit states of the window (lower.witness) at the 24 couplings",
                             "Jz = 1.1-3.4 whose label is not certified (5 below the training range, 19 dropped training labels)"],
         ["J", "ms"], grey)
    check(len(grey) == 3 * 24, "grey bars at 24 couplings, Jz = 1.1-3.4")
    # status code of Figs. 1(c), 2(b), 3 (F2 2026-11-13): the bars by status. Not certified: dark lines
    # (c_bars_notcert.dat); undecided and certified: rectangles with a rim, written as TeX macro calls
    # (c_bars_undec.tex: \undecbar{J}{lo}{hi}; c_bars_kept.tex: \keptbar{J}{lo}{hi}); couplings whose bar is cut by the
    # lower axis limit YMIN: c_cut.dat (a break mark is drawn there)
    notc = [r for r in R if r["status"] == "NOT_CERTIFIED"]
    undc = [r for r in R if r["status"] == "GRAY"]
    check(len(notc) + len(undc) == 24 and len(undc) == 3 and all(r["training"] for r in undc)
          and sum(r["training"] for r in notc) == 16,
          "grey bars by status: %d not certified (Jz = %.1f-%.1f; %d of them training labels), %d undecided (Jz = %.1f-%.1f)"
          % (len(notc), notc[0]["Jz"], notc[-1]["Jz"], sum(r["training"] for r in notc), len(undc), undc[0]["Jz"], undc[-1]["Jz"]))
    rows_n = []
    for r in notc:
        rows_n += [(r["Jz"], r["lower"]["witness"][0]), (r["Jz"], r["lower"]["witness"][1]), (NAN, NAN)]
    wdat("c_bars_notcert.dat", ["Fig. 1(c): lower.witness at the %d NOT_CERTIFIED couplings (dark bars)" % len(notc)],
         ["J", "ms"], rows_n)

    def wtex(name, head, macro, rows):
        with open(os.path.join(HERE, name), "w", encoding="ascii", newline="\n") as fh:
            fh.write("%% %s (written by export_overview_rd.py)\n" % head)
            for J, lo_, hi_ in rows:
                fh.write("\\%s{%r}{%r}{%r}\n" % (macro, J, lo_, hi_))
    wtex("c_bars_undec.tex", "Fig. 1(c): lower.witness at the 3 GRAY (undecided) couplings", "undecbar",
         [(r["Jz"], r["lower"]["witness"][0], r["lower"]["witness"][1]) for r in undc])
    wtex("c_bars_kept.tex", "Fig. 1(c): exact.lo, exact.hi of the 26 CERTIFIED_EXACT (kept) labels", "keptbar",
         [(r["Jz"], r["exact"]["lo"], r["exact"]["hi"]) for r in kept])
    cutJ = [r["Jz"] for r in R if r["status"] != "CERTIFIED_EXACT" and r["lower"]["witness"][0] < YMIN]
    wdat("c_cut.dat", ["Fig. 1(c): couplings whose bar reaches below the lower axis limit %g (break mark)" % YMIN],
         ["J"], [(J,) for J in cutJ])
    log("  every kept label and the reference lie inside the exact interval; every other label and the reference lie "
        "between the labels of the two explicit states (asserted)")
    wk = [r["exact"]["width_over_tau"] for r in kept]
    log("  exact interval width of the kept labels: %.4f-%.4f tau" % (min(wk), max(wk)))
    wn = {round(r["Jz"], 1): r["lower"]["w_lower_over_tau"] for r in R if r["status"] == "NOT_CERTIFIED"}
    cut = [J for J in sorted(wn) if MAP[J]["lower"]["witness"][0] < YMIN]
    check(cut == [1.1, 1.2, 1.3] and cut == [round(J, 1) for J in cutJ],
          "bars cut by the axis (lower end below %g): Jz = 1.1, 1.2, 1.3 (break marks)" % YMIN)
    check("%.1f" % down(wn[1.3], 1) == "13.5" and "%.1f" % down(wn[1.1], 1) == "18.8",
          "caption: those three bars are 13.5-18.8 tau wide (%s)" % ", ".join("%.3f" % wn[J] for J in cut))
    mk = max(r["miss_tau"] for r in kept)
    check("%.3f" % up(mk, 3) == "0.175", "every kept label is within 0.175 tau of the reference (largest %.4f)" % mk)
    hi = max(max(r["label_real"] for r in R), max(float(p) for p in pred) + q, max(r["exact"]["hi"] for r in kept))
    check(hi < 0.99, "every drawn value lies below 0.99 (largest %.4f): the strip up to the axis limit %g holds the "
          "counts printed in the panel" % (hi, YMAX))
    log("")

    log("[3] panel (c), right: coverage by the standard interval (m_s)")
    ce, ci = M["ood_exact_control"]["summary"], M["indist_exact_control"]["summary"]
    cnt = dict(tr_lab=sum(bool(r["covM_emu"]) for r in tr), tr_ref=sum(bool(r["covM_truth"]) for r in tr),
               tr_ctl=sum(bool(r["covM_truth"]) for r in M["indist_exact_control"]["rows"]),
               te_lab=sum(bool(r["covM_emu"]) for r in od), te_ref=sum(bool(r["covM_truth"]) for r in od),
               te_ctl=sum(bool(r["covM_truth"]) for r in M["ood_exact_control"]["rows"]))
    check(cnt == dict(tr_lab=41, tr_ref=0, tr_ctl=41, te_lab=0, te_ref=0, te_ctl=0),
          "training range: 41 of 45 held-out public labels, 0 of 45 reference values, control (trained on DMRG labels) "
          "41 of 45 reference values; test range: 0 of 4, 0 of 4, control 0 of 4")
    check(abs(si["covM_emu"] - 41 / 45) < 1e-12 and si["covM_truth"] == 0 and abs(ci["covM_truth"] - 41 / 45) < 1e-12
          and so["covM_emu"] == 0 and so["covM_truth"] == 0 and ce["covM_truth"] == 0, "the same from the stored summaries")
    cm = [r["miss_ms_over_tau"] for r in M["ood_exact_control"]["rows"]]
    log("  control at the test couplings: misses the reference by %.4f-%.4f tau (at most 0.25 tau), interval %.4f-%.4f tau wide"
        % (min(cm), max(cm), ce["widthM_tau_range"][0], ce["widthM_tau_range"][1]))
    check("%.2f" % up(max(cm), 2) == "0.25", "caption: the control misses the reference by at most 0.25 tau at the test couplings")
    rows = [(5, 41 / 45, 41, 45), (4, 0.0, 0, 45), (3, 41 / 45, 41, 45), (1.6, 0.0, 0, 4), (0.6, 0.0, 0, 4), (-0.4, 0.0, 0, 4)]
    wdat("c_coverage.dat", ["Fig. 1(c) right: rows (top to bottom) training range: held-out public labels, reference, "
                            "reference by the control;", "test range: the same three. cov = k/m"],
         ["row", "cov", "k", "m"], rows)
    seg = []
    for y, c, _, _ in rows:
        seg += [(0.0, y), (c, y), (NAN, NAN)]
    wdat("c_coverage_seg.dat", ["connector of each row from 0 to its coverage"], ["cov", "row"], seg)
    # numbers printed inside panel (c) and in its right strip (F2 2026-11-13: no number typed by hand in the .tex)
    vals = dict(CovTrLab=cnt["tr_lab"], CovTrRef=cnt["tr_ref"], CovTrCtl=cnt["tr_ctl"], NTr=len(tr),
                CovTeLab=cnt["te_lab"], CovTeRef=cnt["te_ref"], CovTeCtl=cnt["te_ctl"], NTe=len(od))
    with open(os.path.join(HERE, "overview_rd_values.tex"), "w", encoding="ascii", newline="\n") as fh:
        fh.write("%% written by export_overview_rd.py -- numbers printed in fig_overview_rd.tex, panel (c)\n")
        for k, v in vals.items():
            fh.write("\\newcommand{\\%s}{%d}\n" % (k, v))
        fh.write("\\newcommand{\\JtestLo}{%.2f}\n\\newcommand{\\JtestHi}{%.2f}\n" % (min(Jod) - 0.05, max(Jod) + 0.05))
        fh.write("\\newcommand{\\Ymin}{%g}\n\\newcommand{\\Ymax}{%g}\n" % (YMIN, YMAX))
    log("  printed in panel (c) (overview_rd_values.tex): training range %d/%d held-out public labels, %d/%d reference "
        "values, control %d/%d; test range %d/%d, %d/%d, control %d/%d; test range shaded Jz = %.2f-%.2f"
        % (vals["CovTrLab"], vals["NTr"], vals["CovTrRef"], vals["NTr"], vals["CovTrCtl"], vals["NTr"], vals["CovTeLab"],
           vals["NTe"], vals["CovTeRef"], vals["NTe"], vals["CovTeCtl"], vals["NTe"], min(Jod) - 0.05, max(Jod) + 0.05))
    log("")
    log("ALL ASSERTIONS PASSED")
    with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
