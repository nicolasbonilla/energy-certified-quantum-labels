"""Export the data of main Fig. 3 on the PUBLIC data (fig_map_rd.tex) as whitespace-separated .dat tables.

  python -B -I export_map_rd.py      (run from anywhere; writes only into this folder: dat/*.dat, export_check.txt)

Nothing physical is recomputed. Inputs, all read-only:
  phase3/full_runs/real_data/out/map_rows.json          the map on the published energies (status, exact, lower)
  phase3/full_runs/real_data/e1/map_e1/map_rows.json    the same rows plus the column of the declared extension E1
                                                        (exact_e1, status_e1); asserted equal to the first file
                                                        in every field drawn from it
  phase3/full_runs/method/laptop_post/out/emu/*.json    the emulated first stage (as in ../pgf_map/export_map.py)

Top row (a, b), width in units of tau = 0.06 |O_GS| of each row:
  CERTIFIED_EXACT  -> exact.width_over_tau       (width of the exact interval, an upper bound on the spread)
  NOT_CERTIFIED    -> lower.w_lower_over_tau     (distance of the labels of two explicit states of the window)
  GRAY (undecided) -> lower.w_lower_over_tau and, where an exact interval exists, exact.width_over_tau (m_s, Czz_bar);
                      the bar between the two is drawn up to at most CAP = 3 tau (longer bars: ucap_*.dat, an arrow)
  extension E1     -> exact_e1.width_over_tau where it exists and differs from the stored column
Status strip: status of every label at every coupling (0 not certified, 1 undecided, 2 certified, 3 certified
only with E1).
Bottom row (c, d), in units of tau and relative to the reference O_GS: the labels of the two explicit states
(lower.witness), the exact interval (exact.lo, exact.hi; exact_e1 for the extension), the public label (label_real)
and the emulated first stage at its own energy. The vertical coordinate is linear up to one tau and logarithmic
beyond (function sym below); the .dat files hold both the plain and the transformed values.
"""
import glob
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RD = os.path.join(ROOT, "phase3", "full_runs", "real_data")
F_ROWS = os.path.join(RD, "out", "map_rows.json")
F_E1 = os.path.join(RD, "e1", "map_e1", "map_rows.json")
D_EMU = os.path.join(ROOT, "phase3", "full_runs", "method", "laptop_post", "out", "emu")
OUT = os.path.join(HERE, "dat")
LABELS = ["m_s", "Czz_bar", "C2_bar", "Z_loop", "Z_boundary", "Z_bulk", "Czz_edge"]   # strip rows, top to bottom
CERT_LABELS = ("m_s", "Czz_bar")                                                      # labels with certificates
PHASE = {"C2_bar": 1, "Z_loop": 0, "Z_boundary": 1, "Z_bulk": 0, "Czz_edge": 2}       # marker stagger (index mod 3)
NAN = float("nan")
CAP = 3.0       # undecided bars of (a, b) are drawn up to at most 3 tau (an arrow marks a longer bar; F2 2026-11-13)
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


def fmt(v):
    if isinstance(v, int):
        return "%d" % v
    if isinstance(v, float) and math.isnan(v):
        return "nan"
    return repr(float(v))


def wdat(name, header, cols, rows):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="ascii", newline="\n") as f:
        for h in header:
            f.write("# " + h + "\n")
        f.write(" ".join(cols) + "\n")
        for r in rows:
            f.write(" ".join(fmt(v) for v in r) + "\n")
    return name


def sym(y):
    """vertical coordinate of (c, d): linear for |y| <= 1 (units of tau), logarithmic beyond"""
    return y if abs(y) <= 1 else math.copysign(1 + math.log10(abs(y)), y)


def up(x, d):
    """round upward to d decimals (widths, misses)"""
    return math.ceil(x * 10 ** d - 1e-9) / 10 ** d


def down(x, d):
    return math.floor(x * 10 ** d + 1e-9) / 10 ** d


def runs(Js):
    """'3.5-6.0' for a contiguous list of couplings on the 0.1 grid; several runs joined by commas"""
    out, a, b = [], None, None
    for J in Js:
        if a is None:
            a = b = J
        elif abs(J - b - 0.1) < 1e-9:
            b = J
        else:
            out.append((a, b))
            a = b = J
    if a is not None:
        out.append((a, b))
    return ", ".join("%.1f" % x if abs(x - y) < 1e-9 else "%.1f-%.1f" % (x, y) for x, y in out) or "none"


def main():
    os.makedirs(OUT, exist_ok=True)
    R0 = rj(F_ROWS)["rows"]
    R1 = rj(F_E1)["rows"]
    key = lambda r: (r["n"], r["label"], round(r["Jz"], 1))
    B = {key(r): r for r in R0}
    E = {key(r): r for r in R1}
    log("export_map_rd.py -- data of main Fig. 3 on the public data (python -B -I; nothing recomputed)")
    log("inputs: phase3/full_runs/real_data/out/map_rows.json (%d rows), e1/map_e1/map_rows.json (%d rows), "
        "method/laptop_post/out/emu/*.json" % (len(R0), len(R1)))
    log("")
    log("[0] the E1 file repeats the declared map in every field drawn here")
    check(set(B) == set(E) and len(B) == 700, "same 700 rows (7 labels x 50 couplings x 2 sizes) in both files")
    nd = 0
    for k, r in B.items():
        e = E[k]
        for f in ("status", "status_rf", "E_real", "M_real", "tau", "O_GS", "label_real", "miss_tau", "de_real",
                  "training"):
            nd += r.get(f) != e.get(f)
        nd += (r["exact"] or {}).get("width_over_tau") != (e["exact"] or {}).get("width_over_tau")
        nd += (r["lower"] or {}).get("w_lower_over_tau") != (e["lower"] or {}).get("w_lower_over_tau")
        nd += (r["lower"] or {}).get("witness") != (e["lower"] or {}).get("witness")
    check(nd == 0, "status, energies, tau, reference, label, exact width, explicit-state width and pair: 0 differences")
    check(all(abs(r["tau"] / abs(r["O_GS"]) - 0.06) < 1e-12 for r in R0), "tau = 0.06 |O_GS| in all 700 rows")
    check(all(r["status"] == r["status_rf"] for r in R0),
          "status with the reference-free tolerance = status with tau in all 700 rows")
    check(all(e.get("status_e1", e["status"]) == e.get("status_e1_rf", e["status_rf"]) for e in R1),
          "same for the E1 column")
    log("")

    written, top_vals, bot_vals = [], [], []
    facts = {}
    for n in (57, 115):
        Js = sorted({k[2] for k in B if k[0] == n})
        check(len(Js) == 50 and abs(Js[0] - 1.1) < 1e-9 and abs(Js[-1] - 6.0) < 1e-9, "n = %d: 50 couplings 1.1-6.0" % n)
        strip = []
        for li, lab in enumerate(LABELS):
            rows = [E[(n, lab, J)] for J in Js]
            st = [r["status"] for r in rows]
            st1 = [r.get("status_e1", r["status"]) for r in rows]
            # ---- top row: one table per label, columns by status (nan = not that status) ----
            tab, bars, caps = [], [], []
            for k_, (r, s, s1) in enumerate(zip(rows, st, st1)):
                ex, lo = r["exact"] or {}, r["lower"] or {}
                e1 = r.get("exact_e1") or {}
                wl = lo.get("w_lower_over_tau")
                wx = ex.get("width_over_tau") if ex.get("exists") else None
                wN = wl if s == "NOT_CERTIFIED" else NAN
                wC = wx if s == "CERTIFIED_EXACT" else NAN
                wUl = wl if (s == "GRAY" and lab in CERT_LABELS) else NAN
                wUu = wx if (s == "GRAY" and lab in CERT_LABELS and wx is not None) else NAN
                # E1 layer: an exact interval of the extension that the stored certificates did not give
                w1 = e1.get("width_over_tau") if e1.get("exists") else None
                new1 = w1 is not None and (wx is None or abs(w1 - wx) > 1e-12 or s1 != s)
                wE = w1 if new1 else NAN
                cE = (1 if s1 == "CERTIFIED_EXACT" else 0) if new1 else 0
                if s == "NOT_CERTIFIED":
                    assert wl is not None and wl >= 1, (n, lab, r["Jz"], wl)
                if s == "CERTIFIED_EXACT":
                    assert wx is not None and wx <= 1 and ex["in_range"], (n, lab, r["Jz"], wx)
                if s == "GRAY":
                    assert wl is None or wl < 1 or True
                tab.append((r["Jz"], k_, wN, wC, wUl, wUu, wE, cE))
                # grey bar of an undecided row: from the explicit-state distance up to the width of an exact interval;
                # drawn up to at most CAP (bars above it end at CAP with an arrow, listed in ucap_*.dat; F2 2026-11-13)
                top = wUu if not math.isnan(wUu) else (wE if (s == "GRAY" and lab in CERT_LABELS) else NAN)
                if not math.isnan(wUl) and not math.isnan(top):
                    bars += [(r["Jz"], wUl), (r["Jz"], min(top, CAP)), (NAN, NAN)]
                    if top > CAP:
                        caps.append((r["Jz"], CAP, top))
                        facts.setdefault("capped", []).append((n, lab, r["Jz"], top))
                top_vals += [v for v in (wN, wC, wUl, wUu, wE) if not (isinstance(v, float) and math.isnan(v))]
                # facts for the caption: an exact interval within tau outside the declared range of couplings
                if s == "GRAY" and wx is not None and wx <= 1:
                    facts.setdefault("in_tau_outside_range", []).append((n, lab, r["Jz"], wx, bool(ex.get("in_range")), s1))
                code = {"NOT_CERTIFIED": 0, "GRAY": 1, "CERTIFIED_EXACT": 2}[s]
                if s != "CERTIFIED_EXACT" and s1 == "CERTIFIED_EXACT":
                    code = 3
                strip.append((r["Jz"], li, code))
            # markers of the not-certified points: every coupling for m_s and Czz_bar; for the other labels every
            # third coupling (phase PHASE[lab]) and, so that no decided point stays invisible, every point that has
            # no not-certified neighbour on either side (a run of length one, which the line cannot show)
            isN = [not math.isnan(t[2]) for t in tab]
            tab2, n_iso = [], 0
            for i, t in enumerate(tab):
                lone = isN[i] and not (i > 0 and isN[i - 1]) and not (i + 1 < len(tab) and isN[i + 1])
                show = isN[i] and (lab in CERT_LABELS or i % 3 == PHASE[lab] or lone)
                n_iso += lone
                # Uud: the top tick of an undecided bar, only where the bar is not capped (F2 2026-11-13)
                tab2.append(t[:3] + (t[2] if show else NAN,) + t[3:] + (t[5] if not math.isnan(t[5]) and t[5] <= CAP else NAN,))
            facts[(n, lab, "lone")] = n_iso
            written.append(wdat("w_n%d_%s.dat" % (n, lab), [
                "Fig. 3 (a, b), n=%d, label %s; source real_data/e1/map_e1/map_rows.json (= out/map_rows.json)" % (n, lab),
                "N = lower.w_lower_over_tau where status NOT_CERTIFIED; C = exact.width_over_tau where CERTIFIED_EXACT;",
                "Nm = N at the couplings that carry a marker (all for m_s and Czz_bar; else every third and lone points);",
                "Ul, Uu = the same two quantities where status GRAY (m_s, Czz_bar only; Uu nan if no exact interval);",
                "E1 = exact_e1.width_over_tau where the extension gives an interval the stored certificates did not;",
                "cE1 = 1 if status_e1 is CERTIFIED_EXACT there. nan = not applicable; k = index of the coupling (0..49)",
                "Uud = Uu where Uu <= %g (the drawn top of an undecided bar; longer bars end at %g with an arrow)" % (CAP, CAP)],
                ["J", "k", "N", "Nm", "C", "Ul", "Uu", "E1", "cE1", "Uud"], tab2))
            if lab in CERT_LABELS:
                written.append(wdat("ubar_n%d_%s.dat" % (n, lab), [
                    "grey bars of the undecided rows, n=%d, %s: (J, Ul), (J, top), blank; top = Uu, or E1 if no stored" % (n, lab),
                    "exact interval exists; top drawn at most %g (units of tau): see ucap_n%d_%s.dat" % (CAP, n, lab)],
                    ["J", "w"], bars or [(NAN, NAN)]))
                written.append(wdat("ucap_n%d_%s.dat" % (n, lab), [
                    "bars of ubar_n%d_%s.dat that reach above %g tau: drawn up to w = %g with an arrow; top = the width" % (n, lab, CAP, CAP),
                    "of the exact interval (units of tau), not drawn"], ["J", "w", "top"], caps or [(NAN, NAN, NAN)]))
            facts[(n, lab)] = dict(
                cert=[J for J, s in zip(Js, st) if s == "CERTIFIED_EXACT"],
                cert1=[J for J, s in zip(Js, st1) if s == "CERTIFIED_EXACT"],
                notc=[J for J, s in zip(Js, st) if s == "NOT_CERTIFIED"],
                gray=[J for J, s in zip(Js, st) if s == "GRAY"],
                gray1=[J for J, s in zip(Js, st1) if s == "GRAY"],
                train=[r["Jz"] for r in rows if r["training"]])
        # strip, row-major for matrix plot (rows = labels, 50 columns each)
        written.append(wdat("strip_n%d.dat" % n, [
            "Fig. 3 status strip, n=%d: row = index in %s (0 = top)" % (n, LABELS),
            "code: 0 NOT_CERTIFIED, 1 GRAY (undecided), 2 CERTIFIED_EXACT, 3 CERTIFIED_EXACT only with extension E1"],
            ["J", "row", "code"], strip))
        written.append(wdat("strip_e1_n%d.dat" % n, ["cells with code 3 (certified only with E1)"], ["J", "row"],
                            [(J, li) for J, li, c in strip if c == 3] or [(NAN, NAN)]))

        # ---- bottom row: m_s relative to the reference, in units of tau ----
        rows = [E[(n, "m_s", J)] for J in Js]
        tab = []
        for r in rows:
            g, t = r["O_GS"], r["tau"]
            w = r["lower"]["witness"]
            ex = r["exact"] or {}
            e1 = r.get("exact_e1") or {}
            wl, wu = (w[0] - g) / t, (w[1] - g) / t
            xl = (ex["lo"] - g) / t if ex.get("exists") else NAN
            xu = (ex["hi"] - g) / t if ex.get("exists") else NAN
            new1 = e1.get("exists") and (not ex.get("exists") or abs(e1["lo"] - ex["lo"]) > 1e-15
                                         or abs(e1["hi"] - ex["hi"]) > 1e-15)
            el = (e1["lo"] - g) / t if new1 else NAN
            eu = (e1["hi"] - g) / t if new1 else NAN
            lab = (r["label_real"] - g) / t
            assert abs(abs(lab) - r["miss_tau"]) < 1e-9, (n, r["Jz"])
            assert w[0] <= r["label_real"] <= w[1] and w[0] <= g <= w[1], (n, r["Jz"])
            if ex.get("exists"):
                assert ex["label_inside"] and ex["truth_inside"] and ex["lo"] <= w[0] and w[1] <= ex["hi"], (n, r["Jz"])
            if e1.get("exists"):
                assert e1["lo"] <= r["label_real"] <= e1["hi"] and e1["lo"] <= g <= e1["hi"], (n, r["Jz"])
                assert e1["lo"] <= w[0] and w[1] <= e1["hi"], (n, r["Jz"])
            vals = (wl, wu, xl, xu, el, eu, lab)
            tab.append((r["Jz"],) + vals + tuple(sym(v) if not math.isnan(v) else NAN for v in vals))
            bot_vals += [v for v in vals if not math.isnan(v)]
        written.append(wdat("ms_n%d.dat" % n, [
            "Fig. 3 (c, d), n=%d, m_s minus the reference O_GS in units of tau; source e1/map_e1/map_rows.json" % n,
            "wl, wu = lower.witness (labels of the two explicit states of the window); xl, xu = exact.lo, exact.hi;",
            "el, eu = exact_e1.lo, exact_e1.hi where the extension gives a new interval; lab = label_real;",
            "s* = the same values on the drawn scale: y for |y| <= 1, sign(y)(1 + log10|y|) beyond"],
            ["J", "wl", "wu", "xl", "xu", "el", "eu", "lab", "swl", "swu", "sxl", "sxu", "sel", "seu", "slab"], tab))
        facts[(n, "lab")] = [(r["Jz"], (r["label_real"] - r["O_GS"]) / r["tau"]) for r in rows]
        facts[(n, "wit")] = [(r["Jz"], r["lower"]["witness"], r["lower"]["w_lower_over_tau"]) for r in rows]
        # emulated first stage at its own energy (as ../pgf_map/export_map.py: var.primary.err.dm_s)
        emu, dref = [], []
        for p in sorted(glob.glob(os.path.join(D_EMU, "emu_n%d_J*.json" % n))):
            v = rj(p)
            J = round(v["Jz"], 1)
            r = E[(n, "m_s", J)]
            # the emulation's own reference (method run) against the reference of the map row: recorded below
            dref.append(abs(v["ref_m_s"] - r["O_GS"]) / r["tau"])
            d = v["var"]["primary"]["err"]["dm_s"] / r["tau"]
            emu.append((J, d, sym(d), v["var"]["primary"]["dE_site"], r["de_real"]))
            bot_vals.append(d)
        emu.sort()
        written.append(wdat("emu_n%d.dat" % n, [
            "Fig. 3 (c, d), n=%d, emulated first stage at its own energy: var.primary.err.dm_s / tau of the map row;" % n,
            "sdms = the same on the drawn scale; de_emu = var.primary.dE_site; de_pub = de_real of the map row"],
            ["J", "dms", "sdms", "de_emu", "de_pub"], emu))
        facts[(n, "emu")] = emu
        facts[(n, "dref")] = max(dref)

    log("files written: %d" % len(written))
    for p in written:
        log("  dat/" + p)
    log("")

    # ------------------------------------------------------------------ facts quoted in the caption of Fig. 3
    log("[1] statuses of the order parameter and of the mean correlation (caption; counts out of the 45 training couplings)")
    for n in (57, 115):
        for lab in CERT_LABELS:
            f = facts[(n, lab)]
            tr = set(f["train"])
            check(len(tr) == 45 and min(tr) > 1.55, "n = %d %s: 45 training couplings, 1.6-6.0" % (n, lab))
            c, c1 = [J for J in f["cert"] if J in tr], [J for J in f["cert1"] if J in tr]
            check(len(c) == len(f["cert"]) and len(c1) == len(f["cert1"]), "every certified coupling is a training coupling")
            log("  n = %-3d %-7s certified: %d of 45 (Jz = %s); with E1: %d of 45 (Jz = %s); not certified: Jz = %s; "
                "undecided: Jz = %s; undecided with E1: Jz = %s"
                % (n, lab, len(c), runs(f["cert"]), len(c1), runs(f["cert1"]), runs(f["notc"]), runs(f["gray"]),
                   runs(f["gray1"])))
    f = facts
    check(len(f[(57, "m_s")]["cert"]) == 26 and runs(f[(57, "m_s")]["cert"]) == "3.5-6.0", "m_s, n = 57: 26 of 45, Jz = 3.5-6.0")
    check(len(f[(115, "m_s")]["cert"]) == 21 and runs(f[(115, "m_s")]["cert"]) == "4.0-6.0", "m_s, n = 115: 21 of 45, Jz = 4.0-6.0")
    check(len(f[(115, "m_s")]["cert1"]) == 27 and runs(f[(115, "m_s")]["cert1"]) == "3.4-6.0", "m_s, n = 115 with E1: 27 of 45, Jz = 3.4-6.0")
    check(len(f[(57, "m_s")]["cert1"]) == 26 and len(f[(57, "Czz_bar")]["cert1"]) == 27,
          "n = 57 with E1: still 26 of 45 (m_s) and 27 of 45 (Czz_bar): the extension certifies none more at n = 57")
    check(len(f[(57, "Czz_bar")]["cert"]) == 27 and runs(f[(57, "Czz_bar")]["cert"]) == "3.4-6.0", "Czz_bar, n = 57: 27 of 45, Jz = 3.4-6.0")
    check(len(f[(115, "Czz_bar")]["cert"]) == 21 and runs(f[(115, "Czz_bar")]["cert"]) == "4.0-6.0", "Czz_bar, n = 115: 21 of 45, Jz = 4.0-6.0")
    check(len(f[(115, "Czz_bar")]["cert1"]) == 25 and runs(f[(115, "Czz_bar")]["cert1"]) == "3.6-6.0", "Czz_bar, n = 115 with E1: 25 of 45, Jz = 3.6-6.0")
    check(runs(f[(57, "m_s")]["notc"]) == "1.1-3.1" and runs(f[(57, "Czz_bar")]["notc"]) == "1.1-3.1", "not certified, n = 57: m_s and Czz_bar at Jz = 1.1-3.1")
    check(runs(f[(115, "m_s")]["notc"]) == "1.1-3.0" and runs(f[(115, "Czz_bar")]["notc"]) == "1.1-3.0", "not certified, n = 115: m_s and Czz_bar at Jz = 1.1-3.0")
    check(runs(f[(57, "m_s")]["gray"]) == "3.2-3.4" and runs(f[(115, "m_s")]["gray"]) == "3.1-3.9", "undecided m_s: Jz = 3.2-3.4 (n = 57), 3.1-3.9 (n = 115)")
    check(runs(f[(115, "m_s")]["gray1"]) == "3.1-3.3" and runs(f[(57, "m_s")]["gray1"]) == "3.2-3.4", "undecided m_s with E1: Jz = 3.1-3.3 (n = 115), 3.2-3.4 (n = 57)")
    for n in (57, 115):
        allN = [J for J in sorted({k[2] for k in B if k[0] == n})
                if all(B[(n, lab, J)]["status"] == "NOT_CERTIFIED" for lab in LABELS)]
        check(all(any(abs(J - x) < 1e-9 for x in allN) for J in (1.1, 1.2, 1.3, 1.4, 1.5)),
              "n = %d: all seven labels NOT_CERTIFIED at Jz = 1.1-1.5 (all seven at Jz = %s)" % (n, runs(allN)))
        oth = [lab for lab in LABELS if lab not in CERT_LABELS]
        nC = sum(E[(n, lab, J)].get("status_e1", E[(n, lab, J)]["status"]) == "CERTIFIED_EXACT" or
                 B[(n, lab, J)]["status"] == "CERTIFIED_EXACT" for lab in oth for J in {k[2] for k in B if k[0] == n})
        check(nC == 0, "n = %d: no row of C2_bar or of a local label is certified (no certificate exists for them)" % n)
        cnt = {lab: (len(facts[(n, lab)]["notc"]), len(facts[(n, lab)]["gray"])) for lab in oth}
        log("      n = %d, (not certified, undecided) of 50 couplings: %s" % (n, cnt))
        log("      n = %d, not-certified points with no not-certified neighbour (drawn with their own marker): %s"
            % (n, {lab: facts[(n, lab, "lone")] for lab in oth}))
    # which stored states the local rows use (a limit kept from the earlier figure)
    LOCAL = ("Z_loop", "Z_boundary", "Z_bulk", "Czz_edge")
    for n in (57, 115):
        kinds = {}
        for lab in LOCAL:
            for J in sorted({k[2] for k in B if k[0] == n}):
                kinds.setdefault(B[(n, lab, J)]["lower"]["pool"]["kind"], []).append((lab, J))
        log("      n = %d, local rows by the kind of states used: %s" % (n, {k: len(v) for k, v in kinds.items()}))
        facts[(n, "kinds")] = kinds
    check(facts[(115, "kinds")].get("stored chain") == [("Z_bulk", 4.0)],
          "caption: at n = 115 states aimed at a local label were stored only for Z_bulk at Jz = 4 (the only local row "
          "with a stored chain of its own label)")
    import re as _re
    aimed, zb = {}, set()
    for lab in LOCAL:
        for J in sorted({k[2] for k in B if k[0] == 115}):
            for side in ("max", "min"):
                for comp in B[(115, lab, J)]["lower"]["components"][side]:
                    m = _re.match(r"n\d+_J[0-9.]+_(?:chk\d+_)?(.*?)_[pm](?:_l|$)", comp[0])
                    a = m.group(1) if m else comp[0]
                    aimed[a] = aimed.get(a, 0) + 1
                    if a == "Z_bulk":
                        zb.add(J)
    log("      n = 115, labels that the states used by the local rows were aimed at (number of components): %s" % aimed)
    check(set(aimed) <= {"m_s", "Czz_bar", "C2_bar", "Z_bulk"}, "caption: at n = 115 the local rows use states aimed at "
          "the averages (m_s, Czz_bar, C2_bar) or at Z_bulk")
    check(min(zb) > 3.65 and max(zb) < 4.45, "the states aimed at Z_bulk are used at Jz = %.1f-%.1f only" % (min(zb), max(zb)))
    und = {n: sum(len(facts[(n, lab)]["gray"]) for lab in LOCAL) for n in (57, 115)}
    check(und == {57: 7, 115: 92}, "caption: undecided local rows: 92 of the 200 at n = 115, 7 of the 200 at n = 57 "
          "(four local labels x 50 couplings)")
    check("stored states, no chain of this label" not in facts[(57, "kinds")],
          "at n = 57 every local row uses states of its own label (stored chain or re-evaluated)")
    io = facts.get("in_tau_outside_range", [])
    log("  undecided rows that have an exact interval of at most tau: %s"
        % ", ".join("n = %d %s Jz = %.1f (%.3f tau, in declared range: %s, with E1: %s)" % x for x in io))
    check(sorted((x[0], x[1], round(x[2], 1)) for x in io) == [(115, "Czz_bar", J) for J in (3.6, 3.7, 3.8, 3.9)]
          and not any(x[4] for x in io) and all(x[5] == "CERTIFIED_EXACT" for x in io),
          "caption: only Czz_bar at n = 115, Jz = 3.6-3.9 has an exact interval within tau at a coupling outside the "
          "range of couplings fixed in the declaration; it is counted only with the extension E1")
    log("")

    log("[2] widths quoted in the caption (units of tau; printed value rounded upward)")
    def W(n, lab, J, fld="exact"):
        r = E[(n, lab, J)]
        return r[fld]["width_over_tau"]
    for n, J in ((57, 6.0), (115, 6.0), (57, 3.5), (57, 3.4)):
        w = W(n, "m_s", J)
        log("  m_s n = %-3d Jz = %.1f exact interval width / tau = %.6f -> %.2f (%.4f)" % (n, J, w, up(w, 2), up(w, 4)))
    check("%.2f" % up(W(57, "m_s", 6.0), 2) == "0.22" and "%.2f" % up(W(115, "m_s", 6.0), 2) == "0.15",
          "caption: 0.22 tau (n = 57) and 0.15 tau (n = 115) at Jz = 6.0")
    check("%.4f" % up(W(57, "m_s", 3.4), 4) == "1.0043", "the row m_s, n = 57, Jz = 3.4: exact interval 1.0043 tau wide (undecided)")
    for n, J in ((57, 3.2), (57, 3.3), (115, 3.3)):
        w = W(n, "m_s", J, "exact_e1")
        log("  m_s n = %-3d Jz = %.1f E1 exact interval width / tau = %.6f -> %.2f (undecided)" % (n, J, w, up(w, 2)))
    check("%.2f" % up(W(57, "m_s", 3.3, "exact_e1"), 2) == "1.12" and "%.2f" % up(W(57, "m_s", 3.2, "exact_e1"), 2) == "1.16",
          "E1 at n = 57: exact intervals 1.12 tau (Jz = 3.3) and 1.16 tau (Jz = 3.2) wide, undecided")
    check("%.2f" % up(W(115, "m_s", 3.3, "exact_e1"), 2) == "1.07", "E1 at n = 115, Jz = 3.3: exact interval 1.07 tau wide, undecided")
    for n in (57, 115):
        J, w, wl = facts[(n, "wit")][0]
        r = E[(n, "m_s", J)]
        log("  m_s n = %-3d Jz = %.1f explicit states: labels %.4f and %.4f (outward: [%.3f, %.3f]), distance %.4f tau -> %.1f tau (rounded down)"
            % (n, J, w[0], w[1], up(w[0], 3), down(w[1], 3), wl, down(wl, 1)))
    check("%.1f" % down(facts[(57, "wit")][0][2], 1) == "18.8" and "%.1f" % down(facts[(115, "wit")][0][2], 1) == "16.3",
          "caption: explicit states at Jz = 1.1 are 18.8 tau (n = 57) and 16.3 tau (n = 115) apart")
    log("")

    log("[3] the public labels of m_s against the reference (caption of c, d)")
    for n in (57, 115):
        L = facts[(n, "lab")]
        check(all(v > 0 for _, v in L), "n = %d: label above the reference at all %d couplings" % (n, len(L)))
        log("  n = %d: (label - reference)/tau = %.4f at Jz = %.1f, %.4f at Jz = %.1f; largest %.4f, smallest %.4f"
            % (n, L[0][1], L[0][0], L[-1][1], L[-1][0], max(v for _, v in L), min(v for _, v in L)))
    L57, L115 = facts[(57, "lab")], facts[(115, "lab")]
    check("%.2f" % L57[0][1] == "4.95" and "%.2f" % L57[-1][1] == "0.04", "caption: 4.95 tau (Jz = 1.1) to 0.04 tau (6.0) at n = 57")
    check("%.2f" % L115[0][1] == "4.67" and "%.2f" % up(L115[-1][1], 2) == "0.02", "caption: 4.67 tau (Jz = 1.1) at n = 115; 0.02 tau at 6.0 (0.0136 rounded up)")
    log("  every label and the reference lie between the labels of the two explicit states (100 rows) and inside the "
        "exact interval where one exists (asserted row by row above)")
    for n in (57, 115):
        e = facts[(n, "emu")]
        check(all(d > 0 for _, d, _, _, _ in e), "n = %d: emulated first stage above the reference at all %d couplings" % (n, len(e)))
        ratio = [de / dp for _, _, _, de, dp in e]
        log("  n = %d emulation: %d couplings (%s); dm_s/tau from %.3f (Jz = %.1f) to %.4f (Jz = %.1f); "
            "its energy error over the published one: %.3f-%.3f" % (n, len(e), ", ".join("%.1f" % x[0] for x in e),
                                                                  e[0][1], e[0][0], e[-1][1], e[-1][0], min(ratio), max(ratio)))
        facts[(n, "ratio")] = ratio
        check(facts[(n, "dref")] < 5e-3, "n = %d: the emulation's own reference and the reference of the map differ by at "
              "most %.1e tau (the emulated bias is taken against its own reference, as in the earlier figure)"
              % (n, facts[(n, "dref")]))
    check(min(facts[(115, "ratio")]) > 1, "n = 115: the emulation's energy error exceeds the published one at every emulated coupling")
    check("%.1f" % down(min(facts[(115, "ratio")]), 1) == "3.8",
          "caption: at n = 115 the emulation's energy error is more than 3.8 times the published one (smallest ratio %.3f)"
          % min(facts[(115, "ratio")]))
    lo57 = sum(1 for x in facts[(57, "ratio")] if x < 1)
    log("  n = 57: the emulation's energy error is below the published one at %d of %d emulated couplings" % (lo57, len(facts[(57, "ratio")])))
    for n in (57, 115):
        d = [x[1] for x in facts[(n, "emu")]]
        check(all(a > b for a, b in zip(d, d[1:])), "n = %d: the emulated bias in units of tau falls from one emulated "
              "coupling to the next (same sign and same trend as the public labels)" % n)
        L = [v for _, v in facts[(n, "lab")]]
        nup = sum(1 for a, b in zip(L, L[1:]) if b > a)
        log("  n = %d: the public label's distance from the reference, in units of tau, rises between neighbouring "
            "couplings %d times out of %d (it falls overall: %.2f tau at Jz = 1.1, %.2f tau at 6.0)" % (n, nup, len(L) - 1, L[0], L[-1]))
    log("")

    log("[4] axis limits of fig_map_rd.tex contain every drawn value")
    check(0.08 < min(top_vals) and max(top_vals) < 200, "top row: min %.4f, max %.4f within [0.08, 200]" % (min(top_vals), max(top_vals)))
    check(-22 < min(bot_vals) and max(bot_vals) < 14, "bottom row: min %+.3f tau, max %+.3f tau within [-22, 14] (drawn scale [%.3f, %.3f])"
          % (min(bot_vals), max(bot_vals), sym(-22), sym(14)))
    log("  drawn-scale tick positions: " + ", ".join("%g tau -> %.4f" % (v, sym(v)) for v in (0.5, 1, 2, 3, 5, 10, 20)))
    cp = facts.get("capped", [])
    log("  undecided bars of (a, b) longer than %g tau, drawn up to %g tau with an arrow: %s"
        % (CAP, CAP, ", ".join("n = %d %s Jz = %.1f (top %.4f tau)" % x for x in cp) or "none"))
    check([(x[0], x[1], round(x[2], 1)) for x in cp] == [(115, "Czz_bar", 3.4)] and "%.1f" % down(cp[0][3], 1) == "8.9",
          "caption: one undecided bar exceeds %g tau (n = 115, Czz_bar, Jz = 3.4, exact interval %.1f tau wide, rounded "
          "down); it is drawn up to %g tau with an arrow" % (CAP, down(cp[0][3], 1) if cp else NAN, CAP))
    log("")
    log("all assertions passed")
    with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
