"""Export the data of main Fig. 2 on the PUBLIC data (fig_composite_rd.tex).

  python -B -I export_composite_rd.py     (run from anywhere; writes only into this folder)

Nothing physical is recomputed.
  (a) the colour map and its width = tau contour are a property of the model: a_map.dat and a_contour_tau.dat are
      copied byte for byte from ../pgf_composite/ (written there by export_composite.py from the stored states);
      the black line is the PUBLISHED energy error per site at the 50 couplings, de_real of the m_s rows of
      phase3/full_runs/real_data/out/map_rows.json (n = 57).
  (b) the width of m_s at the published energy with the status of each row (same tables as ../pgf_map_rd/), from
      real_data/e1/map_e1/map_rows.json (asserted equal to out/map_rows.json in the fields used), and the distance
      of the exact 19-site value from the reference, real_data/out/predict_real.json
      (sizes.57.n19_comparison.rows[*].n19_minus_truth_tau).
  (c, d) our device data: cd_nodes.dat, cd_edges.dat, cd_routed.dat and the printed numbers are copied byte for
      byte from ../pgf_composite/ (unchanged).
Writes *.dat, composite_rd_values.tex and export_check.txt.
"""
import hashlib
import json
import math
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.abspath(os.path.join(HERE, "..", "pgf_composite"))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RD = os.path.join(ROOT, "phase3", "full_runs", "real_data")
N = 57
NAN = float("nan")
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
    if isinstance(v, int):
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
    log("export_composite_rd.py -- data of main Fig. 2 on the public data (n = %d; nothing recomputed)" % N)
    log("")
    log("[0] files of the model map and of the device panels, copied unchanged from ../pgf_composite/")
    for fn in ("a_map.dat", "a_contour_tau.dat", "cd_nodes.dat", "cd_edges.dat", "cd_routed.dat"):
        src, dst = os.path.join(OLD, fn), os.path.join(HERE, fn)
        shutil.copyfile(src, dst)
        check(sha(src) == sha(dst), "%s copied, SHA-256 %s" % (fn, sha(dst)[:16]))
    with open(os.path.join(OLD, "composite_values.tex"), encoding="ascii") as f:
        old_vals = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", f.read()))
    check(set(old_vals) >= {"DmsDev", "MinDev", "DmsCtl", "MinCtl", "NRouted", "MapCols"},
          "printed device numbers read from ../pgf_composite/composite_values.tex: %s"
          % {k: old_vals[k] for k in ("DmsDev", "MinDev", "DmsCtl", "MinCtl", "NRouted", "MapCols")})
    with open(os.path.join(HERE, "a_map.dat"), encoding="ascii") as f:
        de_map = [float(ln.split()[1]) for ln in f.read().split("\n")[1:] if ln.strip()]
    log("")

    R0 = rj(os.path.join(RD, "out", "map_rows.json"))["rows"]
    R1 = rj(os.path.join(RD, "e1", "map_e1", "map_rows.json"))["rows"]
    rows0 = sorted((r for r in R0 if r["n"] == N and r["label"] == "m_s"), key=lambda r: r["Jz"])
    rows = sorted((r for r in R1 if r["n"] == N and r["label"] == "m_s"), key=lambda r: r["Jz"])
    check(len(rows) == 50 and len(rows0) == 50, "50 rows of m_s at n = 57 in both map files")
    same = all(a[f] == b[f] for a, b in zip(rows0, rows) for f in ("Jz", "status", "de_real", "tau", "O_GS")) and all(
        (a["exact"] or {}).get("width_over_tau") == (b["exact"] or {}).get("width_over_tau") and
        a["lower"]["w_lower_over_tau"] == b["lower"]["w_lower_over_tau"] for a, b in zip(rows0, rows))
    check(same, "the E1 file repeats out/map_rows.json in status, de_real, exact width and explicit-state distance")

    log("")
    log("[1] panel (a): the published energy error per site, de_real = (E_pub - E_0)/n")
    line = [(r["Jz"], r["de_real"], {"NOT_CERTIFIED": 0, "GRAY": 1, "CERTIFIED_EXACT": 2}[r["status"]]) for r in rows]
    wdat("a_line_pub.dat", ["Fig. 2(a): published energy error per site of the n = 57 dataset at the 50 couplings",
                            "source real_data/out/map_rows.json rows[n=57,label=m_s].de_real; st = status code of m_s "
                            "(0 not certified, 1 undecided, 2 certified)"], ["J", "de", "st"], line)
    de = [x[1] for x in line]
    check(min(de_map) <= min(de) and max(de) <= 0.024, "the line lies inside the map: de from %.6f (Jz = %.1f) to %.6f "
          "(Jz = %.1f); map range %.4g-%.4g" % (min(de), line[de.index(min(de))][0], max(de), line[de.index(max(de))][0],
                                                min(de_map), max(de_map)))
    log("  de_real at Jz = 1.1, 1.2, 1.3, 1.4: " + ", ".join("%.5f" % x for x in de[:4]) + "; at 6.0: %.5f" % de[-1])

    log("")
    log("[2] panel (b): width of m_s at the published energy, status coding of Fig. 3")
    tab, bars = [], []
    for k, r in enumerate(rows):
        s = r["status"]
        ex, e1 = r["exact"] or {}, r.get("exact_e1") or {}
        wl = r["lower"]["w_lower_over_tau"]
        wx = ex.get("width_over_tau") if ex.get("exists") else None
        w1 = e1.get("width_over_tau") if e1.get("exists") else None
        wN = wl if s == "NOT_CERTIFIED" else NAN
        wC = wx if s == "CERTIFIED_EXACT" else NAN
        wUl = wl if s == "GRAY" else NAN
        wUu = wx if (s == "GRAY" and wx is not None) else NAN
        new1 = w1 is not None and (wx is None or abs(w1 - wx) > 1e-12)
        wE = w1 if new1 else NAN
        if s == "GRAY" and not math.isnan(wUu):
            # bar of an undecided row up to the exact interval of the declared column (the intervals of the
            # extension E1 are shown in Fig. 3 only; the column E1 is written for reference and is not drawn)
            bars += [(r["Jz"], wUl), (r["Jz"], wUu), (NAN, NAN)]
        tab.append((r["Jz"], k, wN, wC, wUl, wUu, wE))
    wdat("b_ms.dat", ["Fig. 2(b), m_s at n = 57 (as ../pgf_map_rd/dat/w_n57_m_s.dat): N = lower.w_lower_over_tau "
                      "(NOT_CERTIFIED),", "C = exact.width_over_tau (CERTIFIED_EXACT), Ul/Uu = the two for GRAY rows, "
                      "E1 = exact_e1.width_over_tau where new (not drawn in Fig. 2)"],
         ["J", "k", "N", "C", "Ul", "Uu", "E1"], tab)
    wdat("b_ubar.dat", ["grey bars of the undecided rows that have an exact interval in the declared column: "
                        "(J, Ul), (J, Uu), blank"], ["J", "w"], bars or [(NAN, NAN)])
    check(len(bars) == 3 and abs(bars[0][0] - 3.4) < 1e-9, "one grey bar, at Jz = 3.4 (from %.4f to %.4f tau)"
          % (bars[0][1], bars[1][1]))
    cert = [r["Jz"] for r in rows if r["status"] == "CERTIFIED_EXACT"]
    notc = [r["Jz"] for r in rows if r["status"] == "NOT_CERTIFIED"]
    gray = [r["Jz"] for r in rows if r["status"] == "GRAY"]
    check(len(cert) == 26 and abs(cert[0] - 3.5) < 1e-9 and abs(cert[-1] - 6.0) < 1e-9 and
          all(abs(b - a - 0.1) < 1e-9 for a, b in zip(cert, cert[1:])), "certified: 26 couplings, Jz = 3.5-6.0 (all training)")
    check(abs(notc[0] - 1.1) < 1e-9 and abs(notc[-1] - 3.1) < 1e-9 and len(notc) == 21, "not certified: Jz = 1.1-3.1 (21 couplings)")
    check([round(x, 1) for x in gray] == [3.2, 3.3, 3.4], "undecided: Jz = 3.2, 3.3, 3.4 (shaded, hatched, in (a) and (b))")
    check(abs(gray[-1] + 0.1 - cert[0]) < 1e-9 and abs(notc[-1] + 0.1 - gray[0]) < 1e-9,
          "the undecided run lies between the last not-certified coupling (%.1f) and the first certified one (%.1f)"
          % (notc[-1], cert[0]))
    wN = {round(r["Jz"], 1): r["lower"]["w_lower_over_tau"] for r in rows}
    log("  explicit states at the test couplings Jz = 1.1-1.4: %s tau apart (rounded down: %.1f-%.1f)"
        % (", ".join("%.3f" % wN[J] for J in (1.1, 1.2, 1.3, 1.4)), down(wN[1.4], 1), down(wN[1.1], 1)))
    check("%.1f" % down(wN[1.4], 1) == "11.1" and "%.1f" % down(wN[1.1], 1) == "18.8",
          "caption: the explicit states are 11.1-18.8 tau apart at the test couplings")
    wC = {round(r["Jz"], 1): r["exact"]["width_over_tau"] for r in rows if r["status"] == "CERTIFIED_EXACT"}
    log("  exact interval width / tau: %.4f at Jz = 3.5 (rounded up %.2f), %.4f at 6.0 (rounded up %.2f); largest "
        "over the certified rows %.4f, smallest %.4f" % (wC[3.5], up(wC[3.5], 2), wC[6.0], up(wC[6.0], 2),
                                                         max(wC.values()), min(wC.values())))
    check("%.2f" % up(wC[3.5], 2) == "0.92" and "%.2f" % up(wC[6.0], 2) == "0.22",
          "caption: exact intervals 0.92 tau (Jz = 3.5) to 0.22 tau (6.0) wide")
    r34 = [r for r in rows if abs(r["Jz"] - 3.4) < 1e-9][0]
    check("%.4f" % up(r34["exact"]["width_over_tau"], 4) == "1.0043", "Jz = 3.4: exact interval 1.0043 tau wide, undecided")

    log("")
    log("[3] panel (b): the exact 19-site value against the reference of n = 57")
    P = rj(os.path.join(RD, "out", "predict_real.json"))["sizes"]["57"]["n19_comparison"]
    n19 = [(x["Jz"], x["n19_minus_truth_tau"]) for x in P["rows"]]
    check(len(n19) == 50 and all(abs(a[0] - r["Jz"]) < 1e-9 for a, r in zip(n19, rows)), "50 couplings, same grid")
    for (J, m), x, r in zip(n19, P["rows"], rows):
        assert abs(abs(x["m_s_n19"] - x["m_gs"]) / r["tau"] - m) < 1e-9 and abs(x["m_gs"] - r["O_GS"]) < 1e-12, J
    log("PASS  n19_minus_truth_tau = |m_s(19 sites) - reference| / tau with the reference and tau of the map row (50 rows)")
    wdat("b_n19.dat", ["Fig. 2(b): |m_s of the exact 19-site ground state - reference of n = 57| / tau",
                       "source real_data/out/predict_real.json sizes.57.n19_comparison.rows[*].n19_minus_truth_tau"],
         ["J", "miss"], n19)
    kept = [m for J, m in n19 if any(abs(J - c) < 1e-9 for c in cert)]
    test = [m for J, m in n19 if J < 1.45]
    check(abs(max(kept) - P["max_over_kept"]) < 1e-12 and P["n_kept"] == 26,
          "largest distance over the 26 certified couplings: %.4f tau (stored max_over_kept), rounded up 0.135" % max(kept))
    check("%.3f" % up(max(kept), 3) == "0.135", "caption: at most 0.135 tau at the certified couplings")
    check("%.2f" % down(min(test), 2) == "1.05" and "%.2f" % down(max(test), 2) == "1.47",
          "caption: 1.05-1.47 tau at the four test couplings (%s)" % ", ".join("%.4f" % m for m in test))
    # colour range of (a) (F2 2026-11-13): it ends at its end ticks 0.03 and 30 (units of tau); every cell inside
    lw = [v for v in (float(ln.split()[2]) for ln in open(os.path.join(HERE, "a_map.dat"), encoding="ascii").read()
                      .split("\n")[1:] if ln.strip()) if not math.isnan(v)]
    check(math.log10(0.03) < min(lw) and max(lw) < math.log10(30),
          "colour range of (a) = 0.03-30 tau, its end ticks; the map spans %.4f-%.3f tau (no cell outside the range)"
          % (10 ** min(lw), 10 ** max(lw)))
    allv = [v for row in tab for v in row[2:] if not math.isnan(v)] + [m for _, m in n19]
    check(0.03 < min(allv) and max(allv) < 30, "panel (b): every drawn value inside the axis range 0.03-30 "
          "(min %.4f, max %.4f)" % (min(allv), max(allv)))

    with open(os.path.join(HERE, "composite_rd_values.tex"), "w", encoding="ascii", newline="\n") as f:
        f.write("%% written by export_composite_rd.py -- numbers printed in fig_composite_rd.tex\n")
        f.write("\\newcommand{\\JcertFirst}{%.1f}\n" % cert[0])
        # the undecided couplings, shaded in (a) and (b) (F2 2026-11-13): first and last, and the band edges
        # half a grid step outside them
        f.write("\\newcommand{\\JundLo}{%.1f}\n\\newcommand{\\JundHi}{%.1f}\n" % (gray[0], gray[-1]))
        f.write("\\newcommand{\\JundBandLo}{%.2f}\n\\newcommand{\\JundBandHi}{%.2f}\n" % (gray[0] - 0.05, gray[-1] + 0.05))
        for k in ("DmsDev", "MinDev", "DmsCtl", "MinCtl", "NRouted", "MapCols"):
            f.write("\\newcommand{\\%s}{%s}\n" % (k, old_vals[k]))
    log("")
    log("wrote a_line_pub.dat, b_ms.dat, b_ubar.dat, b_n19.dat, composite_rd_values.tex; copied a_map.dat, "
        "a_contour_tau.dat, cd_nodes.dat, cd_edges.dat, cd_routed.dat")
    log("ALL CHECKS PASSED")
    with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
