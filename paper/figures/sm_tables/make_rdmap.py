"""Supplemental tables of the certification map on the public data (rewrite of 2026-11-12, writer D).

  python -B -I make_rdmap.py      -> rdmap_{sector,status,exact_ms,exact_czz,e1,counts,factor,compare,checks,figchecks,rig18}.tex and rdmap_summary_rows.tex (this folder)

No number is typed by hand: every value is read from the stored outputs below (read-only) and only rounded and laid
out here. Nothing is recomputed: no certificate, no state, no status.

Sources (paths relative to the project root, the parent of paper/):
  phase3/full_runs/real_data/out/map_rows.json       rows of the sealed map code (exact rationals of every interval)
  phase3/full_runs/real_data/out/map_real.json       the same rows in compact form (flag "rests on a re-evaluated energy")
  phase3/full_runs/real_data/out/map_summary.json    thresholds, counts, accuracy factors, figures-based map against the data
  phase3/full_runs/real_data/out/map_gates.json      the checks of the declaration
  phase3/full_runs/real_data/e1/map_e1/map_rows.json, map_summary.json    the column of the extension E1
  phase3/full_runs/map/laptop_analysis/summary_map.json (gates.G3_gap_record) and the existing table map_checks.tex:
      rdmap_figchecks.tex is map_checks.tex with its last row, a recorded comparison of gaps, recomputed from the
      stored record (the sentence in map/RESULTS.md that map_checks.tex copies is not right at n = 57, Jz = 1.6)
  phase3/full_runs/rigor/outputs/results_v2.json    the 18 proved rows of the figures-based windows: rdmap_rig18.tex is the
      table rig_v2.tex with outward rounding and a column for the reference-free tolerance (0.06 times the smaller
      end of the proved interval in absolute value)

Rounding (rule 7b): the ends of a proved interval are rounded outward from the exact rationals; widths and misses are
rounded up; margins and accuracy factors are rounded down; plain values (labels, reference values, energies) to nearest.
"""
import json
import math
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RD = os.path.join(ROOT, "phase3", "full_runs", "real_data")


def rj(*p):
    with open(os.path.join(RD, *p), encoding="utf-8") as f:
        return json.load(f)


MW = rj("out", "map_rows.json")
MR = rj("out", "map_real.json")
MS = rj("out", "map_summary.json")
MG = rj("out", "map_gates.json")
EW = rj("e1", "map_e1", "map_rows.json")
EQ = rj("e1", "map_e1", "map_summary.json")

LABS = ["m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop"]
TEX = {"m_s": r"$m_s$", "Czz_bar": r"$\bar C_{zz}$", "C2_bar": r"$\bar C_{2}$", "Z_bulk": r"$Z_{\rm bulk}$",
       "Z_boundary": r"$Z_{\rm bdry}$", "Czz_edge": r"$C_{zz}^{\rm edge}$", "Z_loop": r"$Z_{\rm loop}$"}
M0 = {57: 9, 115: 19}
STRUT = r"\rule[-3pt]{0pt}{11.5pt}"     # as in make_sm_final_tests.py: digit-only rows of a REVTeX longtable need it


def fr(x):
    return Fraction(x)


def down(x, d):
    return "%.*f" % (d, math.floor(fr(x) * 10 ** d) / 10 ** d)


def up(x, d):
    return "%.*f" % (d, math.ceil(fr(x) * 10 ** d) / 10 ** d)


def near(x, d):
    return "%.*f" % (d, x)


def m(s):
    return "$%s$" % s


def sci(x, sig=4):
    """nearest, `sig` significant digits, as a x 10^b"""
    e = math.floor(math.log10(abs(x)))
    return r"$%.*f\times10^{%d}$" % (sig - 1, x / 10 ** e, e)


def sci_up(x, sig=2):
    e = math.floor(math.log10(abs(x)))
    q = math.ceil(fr(x) / fr(10) ** e * 10 ** (sig - 1)) / 10 ** (sig - 1)
    return r"$%.*f\times10^{%d}$" % (sig - 1, q, e)


def sel(src, n, lab):
    return sorted([r for r in src["rows"] if r["n"] == n and r["label"] == lab], key=lambda r: r["Jz"])


def one(src, n, lab, Jz):
    return [r for r in sel(src, n, lab) if abs(r["Jz"] - Jz) < 1e-9][0]


def ranges(js):
    js = sorted(js)
    if not js:
        return "none"
    out, a, b = [], js[0], js[0]
    for x in js[1:]:
        if abs(x - b - 0.1) < 1e-6:
            b = x
        else:
            out.append((a, b))
            a = b = x
    out.append((a, b))
    return ", ".join("%.1f" % a if a == b else "%.1f--%.1f" % (a, b) for a, b in out)


MAXL = 36                       # most lines of one piece of a table (rows and group headings)
ROW_PT, HEAD_PT, CAPTION_PT = 12.5, 16, 80     # generous height estimates (pt) for \needspace


def write(name, src, cols, header, body, sep=5):
    """A table that never breaks inside a piece, as the other generated tables of the Supplement (make_sm_tables.py):
    the first piece is a longtable with the caption; a table of more than MAXL lines continues in further pieces, each
    a tabular headed "Table N (continued)"; \\needspace moves a piece to a new page when the rest of the page is too
    short. Pieces are cut between groups (rows that start with \\multicolumn) where possible. Every row starts with a
    strut (digit-only rows of a REVTeX longtable were found set too close, see make_sm_final_tests.py)."""
    ncol = sum(cols.count(ch) for ch in "lcr")
    groups, cur = [], None
    for l in body:
        if l.startswith(r"\multicolumn"):
            cur = [l, []]
            groups.append(cur)
        else:
            if cur is None:
                cur = [None, []]
                groups.append(cur)
            cur[1].append(l)
    pieces, now = [], []
    for g, rows in groups:
        k = len(rows) + (g is not None)
        if now and len(now) + k > MAXL:
            pieces.append(now)
            now = []
        if k <= MAXL:
            now += ([g] if g is not None else []) + rows
        else:                                              # one group longer than a piece: balanced parts
            nparts = -(-len(rows) // (MAXL - 1))
            size = -(-len(rows) // nparts)
            for i in range(nparts):
                part = rows[i * size:(i + 1) * size]
                head = [] if g is None else [g if i == 0 else g.replace(r"}}\\", r" \textmd{\textit{(continued)}}}}\\")]
                if now:
                    pieces.append(now)
                now = head + part
    if now:
        pieces.append(now)

    def strut(l):
        if l.startswith(r"\multicolumn"):
            return l.replace(r"}{\textbf{", "}{" + STRUT + r"\textbf{", 1)
        return STRUT + " " + l

    L = ["% generated by figures/sm_tables/make_rdmap.py from " + src + " -- do not edit",
         r"{\footnotesize\setlength{\tabcolsep}{%spt}\renewcommand{\arraystretch}{1.2}" % sep]
    for k, piece in enumerate(pieces):
        need = ROW_PT * len(piece) + HEAD_PT * len(header) + (CAPTION_PT if k == 0 else 30)
        L.append(r"\needspace{%dpt}" % need)
        if k == 0:
            L += [r"\begin{longtable}{%s}" % cols, r"\caption{\SMcap}\label{\SMlab}\\", r"\toprule"]
        else:
            L += [r"\begin{center}\begin{tabular}{%s}" % cols,
                  r"\multicolumn{%d}{@{}l}{\textit{Table \thetable\ (continued)}}\\" % ncol, r"\toprule"]
        L += header + [r"\midrule"] + [strut(l) for l in piece] + [r"\bottomrule"]
        if k < len(pieces) - 1:
            L.append(r"\multicolumn{%d}{r@{}}{\textit{continued on next page}}\\" % ncol)
        L.append(r"\end{longtable}" if k == 0 else r"\end{tabular}\end{center}")
    L.append("}")
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print("written", name, "(%d rows, %d piece%s)" % (sum(1 for l in body if "&" in l), len(pieces), "" if len(pieces) == 1 else "s"))


SRC = "phase3/full_runs/real_data/out/"
E1SRC = "phase3/full_runs/real_data/e1/map_e1/"
RE = {(r["n"], r["Jz"], r["label"]): bool(r["explicit"].get("rests_on_re_evaluated_energy")) and r["status"]["not_certified_explicit"]
      for r in MR["rows"]}


# ------------------------------------------------------------------------------- the published states and the sector
def t_sector():
    a, b = sel(MW, 57, "m_s"), sel(MW, 115, "m_s")
    body = []
    for x, y in zip(a, b):
        assert abs(x["Jz"] - y["Jz"]) < 1e-9
        tag = r"\rlap{$^{\dagger}$}" if x["Jz"] < 1.45 else (r"\rlap{$^{\ddagger}$}" if x["Jz"] < 1.55 else "")
        body.append("%.1f%s & %s & %s & %s & %s & %s & %s \\\\" % (
            x["Jz"], tag, near(M0[57] - x["M_real"], 6), near(x["q"], 6), near(x["de_real"], 6),
            near(M0[115] - y["M_real"], 6), near(y["q"], 6), near(y["de_real"], 6)))
    header = [r" & \multicolumn{3}{c}{$n=57$ ($M_0=9$)} & \multicolumn{3}{c}{$n=115$ ($M_0=19$)} \\ \cmidrule(lr){2-4}\cmidrule(l){5-7}",
              r"$J_z$ & $M_0-M_{\rm pub}$ & $q$ & $\delta e_{\rm pub}$ & $M_0-M_{\rm pub}$ & $q$ & $\delta e_{\rm pub}$ \\"]
    write("rdmap_sector.tex", SRC + "map_rows.json (M_real, q, de_real)", "lcccccc", header, body)


# ---------------------------------------------------------------------------------------- status of every row
def t_status():
    body = []
    cells = {}
    for n in (57, 115):
        for lab in LABS:
            for r, e in zip(sel(MW, n, lab), sel(EW, n, lab)):
                assert abs(r["Jz"] - e["Jz"]) < 1e-9
                s = {"CERTIFIED_EXACT": "C", "NOT_CERTIFIED": "N", "GRAY": "U"}[r["status"]]
                if s == "N" and RE[(n, r["Jz"], lab)]:
                    s = "N$^{*}$"
                if r["status"] != "CERTIFIED_EXACT" and e.get("status_e1") == "CERTIFIED_EXACT":
                    s = "C$^{+}$"
                cells[(n, r["Jz"], lab)] = r"\textbf{C}" if s == "C" else s
    for r in sel(MW, 57, "m_s"):
        Jz = r["Jz"]
        tag = r"\rlap{$^{\dagger}$}" if Jz < 1.45 else (r"\rlap{$^{\ddagger}$}" if Jz < 1.55 else "")
        body.append("%.1f%s & " % (Jz, tag) + " & ".join(cells[(n, Jz, lab)] for n in (57, 115) for lab in LABS) + r" \\")
    header = [r" & \multicolumn{7}{c}{$n=57$} & \multicolumn{7}{c}{$n=115$} \\ \cmidrule(lr){2-8}\cmidrule(l){9-15}",
              "$J_z$ & " + " & ".join(TEX[lab] for _ in (57, 115) for lab in LABS) + r" \\"]
    write("rdmap_status.tex", SRC + "map_rows.json (status), map_real.json (re-evaluated energies); " + E1SRC + "map_rows.json (status_e1)",
          "l" + "c" * 14, header, body, sep=4)


# ------------------------------------------------------------------------------- exact intervals, primary column
def exact_row(r, lab):
    e = r["exact"]
    lo, hi = down(e["lo_exact"], 5), up(e["hi_exact"], 5)
    w = fr(e["width_exact"])
    wt, wrf = up(w / fr(e["tau"]), 4), up(w / fr(e["tau_rf_exact"]), 4)
    s = e["sides"]
    wm0 = up((fr(s["+"]["cases"]["M_0"]["u"]) + fr(s["-"]["cases"]["M_0"]["u"])) / fr(e["tau"]), 4)
    if not e["in_range"]:
        st = "within $\\tau$, not counted$^{\\S}$" if e.get("within_tau_outside_range") else "outside the range$^{\\S}$"
        mar = "--"
    else:
        st = "certified" if e["certified"] else "undecided"
        mar = down(e["f_exact"], 3)
    assert e["label_inside"] and e["truth_inside"]
    return "%.1f & $[%s,\\,%s]$ & %s & %s & %s & %s & $%s$ & $%s$ & %s & %s \\\\" % (
        r["Jz"], lo, hi, wt, wrf, wm0, mar, near(r["label_real"], 6), near(r["O_GS"], 6), up(r["miss_tau"], 4), st)


def t_exact(lab, name):
    body = []
    for n in (57, 115):
        body.append(r"\multicolumn{10}{@{}l}{\textbf{$n=%d$}}\\" % n)
        for r in sel(MW, n, lab):
            if r["exact"].get("exists"):
                body.append(exact_row(r, lab))
    header = [r"$J_z$ & exact interval $I$ & $w/\tau$ & $w/\tau_{\rm rf}$ & $w/\tau$ at $M_0$ & margin & public label & reference & miss$/\tau$ & status \\"]
    write(name, SRC + "map_rows.json (exact: lo_exact, hi_exact, width_exact, tau, tau_rf_exact, sides, f_exact; label_real, O_GS, miss_tau)",
          "@{}lccccccccl@{}", header, body, sep=4)


# ------------------------------------------------------------------------------------------ the column of E1
def t_e1():
    body = []
    for n in (57, 115):
        body.append(r"\multicolumn{8}{@{}l}{\textbf{$n=%d$}}\\" % n)
        for lab in ("m_s", "Czz_bar"):
            for r in sel(EW, n, lab):
                e = r.get("exact_e1")
                if not e or not e.get("exists"):
                    continue
                p = r["exact"]
                same_iv = p.get("exists") and p["lo_exact"] == e["lo_exact"] and p["hi_exact"] == e["hi_exact"]
                if same_iv and r["status"] == r["status_e1"]:
                    continue
                if p.get("exists"):
                    prim = "%s, %s" % (up(fr(p["width_exact"]) / fr(p["tau"]), 4),
                                       {"CERTIFIED_EXACT": "certified", "GRAY": "undecided", "NOT_CERTIFIED": "not certified"}[r["status"]])
                else:
                    prim = "no interval, " + {"GRAY": "undecided", "NOT_CERTIFIED": "not certified"}[r["status"]]
                st = {"CERTIFIED_EXACT": "certified", "GRAY": "undecided", "NOT_CERTIFIED": "not certified"}[r["status_e1"]]
                assert r["status_e1"] == r["status_e1_rf"]
                w = fr(e["width_exact"])
                body.append("%.1f & %s & %s & $[%s,\\,%s]$ & %s & %s & %s & %s \\\\" % (
                    r["Jz"], TEX[lab], prim, down(e["lo_exact"], 5), up(e["hi_exact"], 5), up(w / fr(e["tau"]), 4),
                    up(w / fr(e["tau_rf_exact"]), 4), down(e["f_exact"], 3), st))
    header = [r"$J_z$ & label & primary column: $w/\tau$, status & interval with the added certificates & $w/\tau$ & $w/\tau_{\rm rf}$ & margin & status \\"]
    write("rdmap_e1.tex", E1SRC + "map_rows.json (exact, exact_e1, status, status_e1, status_e1_rf)", "@{}llllcccl@{}", header, body, sep=4)


# -------------------------------------------------------------------------------------- counts per label and size
def t_counts():
    body = []
    for n in (57, 115):
        body.append(r"\multicolumn{9}{@{}l}{\textbf{$n=%d$}}\\" % n)
        for lab in LABS:
            R, E = sel(MW, n, lab), sel(EW, n, lab)
            tr = [r for r in R if r["training"]]
            js = MS["jstar"]["%d_%s" % (n, lab)]
            je = EQ["jstar"]["%d_%s" % (n, lab)]
            c = [r["Jz"] for r in tr if r["status"] == "CERTIFIED_EXACT"]
            crf = [r["Jz"] for r in tr if r["status_rf"] == "CERTIFIED_EXACT"]
            ce = [r["Jz"] for r in E if r["training"] and (r.get("status_e1") or r["status"]) == "CERTIFIED_EXACT"]
            nc = [r["Jz"] for r in R if r["status"] == "NOT_CERTIFIED"]
            g = [r["Jz"] for r in tr if r["status"] == "GRAY"]
            ge = [r["Jz"] for r in E if r["training"] and (r.get("status_e1") or r["status"]) == "GRAY"]
            assert len(c) == js["sec2"]["certified_exact"] and len(crf) == js["sec2_rf"]["certified_exact"]
            assert sum(1 for r in tr if r["status"] == "NOT_CERTIFIED") == js["sec2"]["not_certified"] and len(g) == js["sec2"]["gray"]
            if "sec2_e1" in je:
                assert len(ce) == je["sec2_e1"]["certified_exact"] == je["sec2_e1_rf"]["certified_exact"]
            else:
                assert len(ce) == 0
            body.append("%s & %d & %s & %d & %d & %s & %d & %s & %d (%d) \\\\" % (
                TEX[lab], len(c), ranges(c) if c else "--", len(crf), len(ce), ranges(ce) if ce else "--",
                js["sec2"]["not_certified"], ranges(nc), len(g), len(ge)))
    header = [r" & \multicolumn{3}{c}{certified (of 45)} & \multicolumn{2}{c}{with the added certificates} & \multicolumn{2}{c}{not certified (of 45)} & undecided \\ \cmidrule(lr){2-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}",
              r"Label & $\tau$ & couplings & $\tau_{\rm rf}$ & of 45 & couplings & of 45 & couplings$^{a}$ & of 45 (added) \\"]
    write("rdmap_counts.tex", SRC + "map_rows.json, map_summary.json (jstar); " + E1SRC + "map_rows.json, map_summary.json (jstar.*.sec2_e1)",
          "@{}lclcclclc@{}", header, body, sep=4)


# ------------------------------------------------------------------------------ accuracy needed at the test couplings
def t_factor():
    body = []
    for n in (57, 115):
        body.append(r"\multicolumn{7}{@{}l}{\textbf{$n=%d$}}\\" % n)
        for lab in ("m_s", "Czz_bar"):
            a = MS["accuracy_factors"][str(n)][lab]
            for v in a["values"]:
                tag = "" if v["test_coupling"] else r"\rlap{$^{\ddagger}$}"
                body.append("%s & %.1f%s & %s & %s & %s & %s & %s \\\\" % (
                    TEX[lab], v["Jz"], tag, near(v["de_real"], 6), sci(v["de_star_in"], 5), down(v["F_A"], 2), down(v["F_B"], 2),
                    "stored states of this coupling" if v["test_coupling"] else "states of 1.4 and 1.6, re-evaluated"))
            assert math.floor(a["min_F_A"] / 10 ** math.floor(math.log10(a["min_F_A"]) - 1)) * 10 ** math.floor(math.log10(a["min_F_A"]) - 1) == a["headline_F_A"]
    header = [r"Label & $J_z$ & $\delta e_{\rm pub}$ & $\delta e^{*}_{\rm in}$ & $F_A$ & $F_B$ & states behind $\delta e^{*}_{\rm in}$ \\"]
    write("rdmap_factor.tex", SRC + "map_summary.json (accuracy_factors)", "@{}llccccl@{}", header, body)


# ----------------------------------------------------------------- the figures-based map against the public energies
def t_compare():
    body = []
    pv = MS["predicted_vs_obtained"]
    last = None
    for j in pv["jstar"]:
        n, lab = j["n"], j["label"]
        if n != last:
            body.append(r"\multicolumn{8}{@{}l}{\textbf{$n=%d$}}\\" % n)
            last = n
        js = MS["jstar"]["%d_%s" % (n, lab)]
        assert j["within_0p1"] and abs(js["J_star_s"] - j["J_star_s"]) < 1e-9
        ex = js["sec2"]
        body.append("%s & %.1f & %s & %d & %.1f & %d & %s & %d \\\\" % (
            TEX[lab], j["J_star_stored"], ("%.1f" % j["J_star_stored_strict"]) if j["J_star_stored_strict"] is not None else r"\textit{none}",
            j["n_certified_stored"], j["J_star_s"], js["like"]["certified"],
            ("%.1f" % ex["J_star_exact"]) if ex.get("J_star_exact") is not None else r"\textit{none}", ex["certified_exact"]))
    header = [r" & \multicolumn{3}{c}{figures-based map (sector, DMRG-referenced)} & \multicolumn{2}{c}{same rule at $E_{\rm pub}$} & \multicolumn{2}{c}{public-data map (exact)} \\ \cmidrule(lr){2-4}\cmidrule(lr){5-6}\cmidrule(l){7-8}",
              r"Label & $J^*$ central & $J^*$, 20\,\% margin & certified (of 45) & $J^*_s$ & certified$_s$ (of 45) & lowest certified $J_z$ & certified (of 45) \\"]
    write("rdmap_compare.tex", SRC + "map_summary.json (predicted_vs_obtained.jstar, jstar)", "@{}lccccccc@{}", header, body)
    c = pv["counts"]
    assert c["confirmed"] == 152 and c["resolved"] == 13 and not pv["contradicted"] and pv["confirmed_by_the_data"]


# ----------------------------------------------------------------------------------------------- the checks
def box(w, s):
    return r"\parbox[t]{%dpt}{\raggedright\strut %s\strut}" % (w, s)


def t_checks():
    g = MG
    r57, r115 = [x["ratio"] for x in g["G2_57"]["rows"]], [x["ratio"] for x in g["G2_115"]["rows"]]
    d57, d115 = [x["E_real_minus_E0_authors"] for x in g["G3_57"]["rows"]], [x["E_real_minus_E0_authors"] for x in g["G3_115"]["rows"]]
    assert g["G2_57"]["pass"] and g["G2_115"]["pass"] and not g["G2_57"]["failed"] and not g["G2_115"]["failed"]
    assert g["G3_57"]["pass"] and g["G3_115"]["pass"] and g["G4_57"]["pass"] and g["G4_115"]["pass"]
    assert g["G5a"]["pass"] and g["G5b"]["pass"] and all(x["ok"] for x in g["G5b"]["rows"]) and g["G6b"]["pass"] and g["G7"]["pass"]
    assert g["G6a"]["n_checked"] == 0 and not g["G6a"]["complete"]
    o57 = max(v for v in g["G4_57"]["max_abs_dO_over_tau"].values() if v is not None)
    o115 = max(v for v in g["G4_115"]["max_abs_dO_over_tau"].values() if v is not None)
    rows = [
        ("Conversion of the public files", "the converter, run again on the pinned archive, reproduces the three converted files",
         "completed$^{a}$", "byte-identical outputs; 302 data files read, none refused"),
        ("One state behind energy and labels (necessary condition of hypothesis H)",
         "the exchange part of $E_{\\rm pub}$ lies within the range $[-B,B]$ that the published $\\langle Z_i\\rangle$ and $\\langle Z_iZ_j\\rangle$ allow, edge by edge",
         "holds at 100 of 100 points",
         "exchange part over $B$: $%s$ to $%s$ ($n=57$), $%s$ to $%s$ ($n=115$)" % (down(min(r57), 4), up(max(r57), 4), down(min(r115), 4), up(max(r115), 4))),
        ("Published energy above the ground energy", "$E_{\\rm pub}\\ge E_0$ of the authors' DMRG at every coupling", "holds at 100 of 100 points",
         "$E_{\\rm pub}-E_0$ between %s and %s ($n=57$) and between %s and %s ($n=115$)" % (down(min(d57), 4), up(max(d57), 4), down(min(d115), 4), up(max(d115), 4))),
        ("Reference values", "the authors' DMRG against our references at the stored couplings: labels within $10^{-3}\\,\\tau$, energies within $10^{-4}$",
         "holds", "%d and %d label rows, largest difference %s and %s $\\tau$; %d and %d energies, largest difference %s and %s" % (
             g["G4_57"]["n_label_rows"], g["G4_115"]["n_label_rows"], sci_up(o57), sci_up(o115), g["G4_57"]["n_energy_rows"], g["G4_115"]["n_energy_rows"],
             sci_up(g["G4_57"]["max_abs_dE0"]), sci_up(g["G4_115"]["max_abs_dE0"], 3))),
        ("Certificates", "every certificate used has a recorded exact verification; those that decide the lowest certified coupling are proved again by a second exact program",
         "holds", "%d files, %d distinct, %d used (%d at $n=57$, %d at $n=115$); %d proved again, all equal to the claimed bound" % (
             g["G5a"]["n_files"], g["G5a"]["n_distinct"], g["G5a"]["n_used"], g["G5a"]["by_size"]["57"], g["G5a"]["by_size"]["115"], len(g["G5b"]["rows"]))),
        ("Off-grid rule against the stored tensors", "for the decisive states of %d selected ``not certified'' rows, the energy at the row's coupling recomputed from the tensors equals the linear rule to $10^{-8}$" % g["G6a"]["n_rows"],
         "\\textbf{not completed}", "%d of %d components checked: their tensors are not on the laptop$^{b}$" % (g["G6a"]["n_checked"], g["G6a"]["n_missing_tensors"])),
        ("Re-evaluated energies", "every re-evaluated energy of a sector state is at least $E_0(J_z)-10^{-6}$", "holds",
         "%d rows with re-evaluated states; smallest distance above $E_0$: %s" % (g["G6b"]["n_rows"], sci(g["G6b"]["min_over_rows"], 3))),
        ("Certified labels inside their intervals", "every certified public label and its reference value lie inside the exact interval", "holds",
         "%d certified rows (either tolerance), no violation; of the %d rows with an interval of any width, %d fail to contain label and reference" % (
             g["G7"]["n_certified_rows"], g["G7"]["n_rows_with_an_interval"], g["G7"]["n_intervals_not_containing_label_and_truth"])),
    ]
    body = ["%s & %s & %s & %s \\\\" % (box(112, r"\textbf{%s}" % a), box(150, b), box(62, c), box(150, d)) for a, b, c, d in rows]
    header = [r"Check & Rule fixed before the analysis & Outcome & Numbers \\"]
    L = ["% generated by figures/sm_tables/make_rdmap.py from " + SRC + "map_gates.json; phase3/full_runs/real_data/checks/G1_rerun_2026-11-12.md (row 1) -- do not edit",
         r"{\footnotesize\setlength{\tabcolsep}{5pt}\renewcommand{\arraystretch}{1.3}", r"\needspace{420pt}",
         r"\begin{longtable}{@{}llll@{}}",
         r"\caption{\SMcap}\label{\SMlab}\\", r"\toprule"] + header + [r"\midrule"]
    L += body + [r"\bottomrule", r"\end{longtable}}"]
    with open(os.path.join(HERE, "rdmap_checks.tex"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print("written rdmap_checks.tex (%d rows)" % len(body))


# ------------------------------------------- checks of the figures-based map, with the gap row recomputed
def t_figchecks():
    with open(os.path.join(ROOT, "phase3", "full_runs", "map", "laptop_analysis", "summary_map.json"), encoding="utf-8") as f:
        g = json.load(f)["gates"]["G3_gap_record"]
    rows = g["rows"]
    tr = [r for r in rows if r["Jz"] > 1.55]                                   # training couplings, both readings
    exc = {r["reading"]: r["rel"] for r in tr if r["n"] == 57 and abs(r["Jz"] - 1.6) < 1e-9}
    rest = [r for r in tr if not (r["n"] == 57 and abs(r["Jz"] - 1.6) < 1e-9)]
    t11 = {r["reading"]: r["rel"] for r in rows if r["n"] == 115 and abs(r["Jz"] - 1.1) < 1e-9}
    t12 = {r["reading"]: r["rel"] for r in rows if r["n"] == 115 and abs(r["Jz"] - 1.2) < 1e-9}
    assert all(abs(r["rel"]) < 0.01 for r in rest) and len(exc) == 2 and g["n"] == len(rows)

    def pc(x, d=1):
        return up(abs(x) * 100, d)

    PCT = "\\%"
    detail = ("within " + pc(max(abs(r["rel"]) for r in rest), 2) + " " + PCT + " at every computed training coupling (both readings) except "
              "$n={}$57, $J_z$ = 1.6, where the dataset's marker is partly covered: +" + pc(exc["1"]) + " " + PCT + " (reading 1) and +"
              + pc(exc["2"]) + " " + PCT + " (reading 2); $n={}$115, $J_z$ = 1.1: +" + pc(t11["1"]) + " " + PCT + " and +" + pc(t11["2"]) + " " + PCT
              + ", 1.2: +" + pc(t12["1"]) + " " + PCT + " and +" + pc(t12["2"]) + " " + PCT
              + " (our bond dimension $\\le$ 200 reference is under-converged there; the thresholds at the test couplings do not use the gap)")
    BOX = "\\parbox[t]{%dpt}{\\raggedright\\strut %s\\strut}"
    new = (BOX % (150, "\\textbf{Gap against the dataset's (recorded, not a pass condition)}\\\\ our $S^z=s-1$ gap vs the dataset's") + " & "
           + BOX % (52, "%d/%d within 10 %s" % (g["n_within_10pct"], g["n"], PCT)) + " & " + BOX % (270, detail) + " \\\\")
    with open(os.path.join(HERE, "map_checks.tex"), encoding="utf-8") as f:
        L = f.read().split(chr(10))
    k = [i for i, l in enumerate(L) if "textbf{Gap against the dataset's" in l]
    assert len(k) == 1 and "1 " + PCT + " at every" in L[k[0]]
    L[k[0]] = new
    L[0] = ("% generated by figures/sm_tables/make_rdmap.py: figures/sm_tables/map_checks.tex with its last row recomputed from "
            "phase3/full_runs/map/laptop_analysis/summary_map.json (gates.G3_gap_record) -- do not edit")
    with open(os.path.join(HERE, "rdmap_figchecks.tex"), "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(chr(10).join(L))
    print("written rdmap_figchecks.tex")


# --------------------- the 18 proved rows of the figures-based windows (rigor run v2), rounded outward (finding 06)
def sig(x, n=3):
    e = math.floor(math.log10(abs(x)))
    return "%.*f" % (max(0, n - 1 - e), x)


def t_rig18():
    with open(os.path.join(ROOT, "phase3", "full_runs", "rigor", "outputs", "results_v2.json"), encoding="utf-8") as f:
        d = json.load(f)
    body, n_tau, n_rf = [], 0, 0
    for n in (57, 115):
        body.append(r"\multicolumn{8}{@{}l}{\textbf{$n=%d$}}\\" % n)
        for r in sorted((x for x in d["rows"] if x["n"] == n), key=lambda x: (x["Jz"], x["label"] != "m_s")):
            lo, hi = r["interval"]
            w = fr(hi) - fr(lo)
            assert abs(float(w) - r["w_cert"]) < 1e-12
            wt = w / fr(r["tau"])
            wrf = w / (fr(6) / fr(100) * min(abs(fr(lo)), abs(fr(hi))))
            assert (wt <= 1) == bool(r["certified"])
            n_tau += wt <= 1
            n_rf += wrf <= 1
            sp, sm = r["sides"]["+"]["best"], r["sides"]["-"]["best"]
            body.append("%s & %s & $[%s,\\,%s]$ & %s & %s & %s & %s / %s & %s \\\\" % (
                (r"\textbf{%.1f}" if r["certified"] else "%.1f") % r["Jz"], TEX[r["label"]], down(lo, 5), up(hi, 5), up(wt, 3), up(wrf, 3),
                sig(r["w_F"] / r["tau"], 3), sig(sp["slack"], 2), sig(sm["slack"], 2),
                r"within $\tau$ \ding{51}" if r["certified"] else r"wider than $\tau$ \ding{55}"))
    header = [r"$J_z$ & Label & proved interval at $E_{\rm up}$ & $w_{\rm rig}/\tau$ & $w_{\rm rig}/\tau_{\rm rf}$ & $w_{\rm DMRG}/\tau$ & slack $+$ / $-$ & status \\"]
    write("rdmap_rig18.tex", "phase3/full_runs/rigor/outputs/results_v2.json (rows: interval, w_cert, tau, w_F, sides)", "@{}llccccll@{}", header, body)
    print("   rows within tau: %d of %d; within the reference-free tolerance: %d" % (n_tau, len(d["rows"]), n_rf))
    assert n_tau == 17 and n_rf == 16 and len(d["rows"]) == 18


# ------------------------------------------ summary rows for the table of Sec. S12 (one row per label and size)
def t_summary():
    L = ["% generated by figures/sm_tables/make_rdmap.py from " + SRC + "map_rows.json, map_summary.json; " + E1SRC + "map_rows.json -- do not edit"]
    for n in (57, 115):
        for lab in LABS:
            R, E = sel(MW, n, lab), sel(EW, n, lab)
            c = sorted(r["Jz"] for r in R if r["training"] and r["status"] == "CERTIFIED_EXACT")
            ce = sorted(r["Jz"] for r in E if r["training"] and (r.get("status_e1") or r["status"]) == "CERTIFIED_EXACT")
            for js in (c, ce):                           # certified couplings form one block that ends at 6.0
                assert not js or (abs(js[-1] - 6.0) < 1e-9 and abs(js[-1] - js[0] - 0.1 * (len(js) - 1)) < 1e-6)
            frm = ("%.1f" % c[0]) if c else "none"
            cnt = "%d" % len(c)
            if ce != c:
                frm += " (%.1f)" % ce[0]
                cnt += " (%d)" % len(ce)
            sep12 = down(one(MW, n, lab, 1.2)["lower"]["w_lower_over_tau"], 2)
            sep16 = down(one(MW, n, lab, 1.6)["lower"]["w_lower_over_tau"], 2)
            e6 = one(MW, n, lab, 6.0)["exact"] or {}
            w6 = up(fr(e6["width_exact"]) / fr(e6["tau"]), 3) if e6.get("exists") else "--"
            fa = ("$>%d$" % MS["accuracy_factors"][str(n)][lab]["headline_F_A"]) if lab in ("m_s", "Czz_bar") else "--"
            L.append("%s & %d & %s & %s & %s & %s & %s & %s \\\\" % (TEX[lab], n, sep12, sep16, frm, cnt, w6, fa))
        if n == 57:
            L.append(r"\hline")
    with open(os.path.join(HERE, "rdmap_summary_rows.tex"), "w", encoding="utf-8", newline=chr(10)) as f:
        f.write(chr(10).join(L) + chr(10))
    print("written rdmap_summary_rows.tex (%d rows)" % sum(1 for l in L if "&" in l))


if __name__ == "__main__":
    assert MW["declaration_sha256"] == MR["declaration_sha256"] == MS["declaration_sha256"]
    assert len(MW["rows"]) == len(EW["rows"]) == 700 and EQ["certificates_E1"] == 48
    t_sector()
    t_status()
    t_exact("m_s", "rdmap_exact_ms.tex")
    t_exact("Czz_bar", "rdmap_exact_czz.tex")
    t_e1()
    t_counts()
    t_factor()
    t_compare()
    t_checks()
    t_figchecks()
    t_rig18()
    t_summary()
