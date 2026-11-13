"""Export the arrays drawn by ../fig2_rule.py, ../fig3_mechanism.py and ../figS1_bias_vs_ratio.py as .dat tables.

  python -B export_sm_method.py      (writes only into this folder: dat/*.dat, export_check.txt)

No physics is recomputed. Loaders: ../common.py (imported); the text parsers parse_t3 and parse_t2_iv are imported
from ../fig2_rule.py; the per-point expressions of the three main() functions are copied verbatim (line numbers below
refer to the scripts as of 2026-10-31). The check log compares exported values with the stored files read
independently and asserts every number the three captions state.
"""
import glob
import json
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, FIGS)

import common as C           # noqa: E402
import fig2_rule as R        # noqa: E402  (parse_t3, parse_t2_iv; importing draws nothing)

OUT = os.path.join(HERE, "dat")
LOG = []
WRITTEN = []
JS = {1.2: "1.2", 1.6: "1.6", 2.5: "2.5", 4.0: "4.0"}


def log(s=""):
    print(s)
    LOG.append(s)


def fmt(v):
    return repr(float(v))


def write_dat(name, header, cols, rows):
    rows = list(rows)
    assert rows, "empty table " + name
    with open(os.path.join(OUT, name), "w", encoding="ascii", newline="\n") as f:
        for h in header:
            f.write("# " + h + "\n")
        f.write(" ".join(cols) + "\n")
        for r in rows:
            f.write(" ".join(fmt(v) for v in r) + "\n")
    WRITTEN.append(name)
    return rows


def read_dat(name):
    with open(os.path.join(OUT, name), encoding="ascii") as f:
        lines = [ln.split() for ln in f if ln.strip() and not ln.startswith("#")]
    return [dict(zip(lines[0], map(float, ln))) for ln in lines[1:]]


def rel(p):
    return os.path.relpath(p, C.ROOT).replace("\\", "/")


# ---------------------------------------------------------------- fig2_rule (figS:rule)
def export_rule(S):
    t3 = os.path.join(C.R3, "t3_comb.txt")
    t2 = os.path.join(C.R3, "t2_local.txt")
    rows = R.parse_t3(t3)                                   # fig2_rule.py L62
    for n in (6, 9, 12):                                    # L64-68
        Rn = sorted((r for r in rows if r["n"] == n), key=lambda r: r["de"])
        write_dat("rule_a_n%d.dat" % n, ["fig2_rule (a), n=%d; source %s (parse_t3)" % (n, rel(t3)),
                                          "de, w = exact width, eg = eps/gap, ring = 1 if eg > 1 (ringed)"],
                  ["de", "w", "eg", "ring"], [(r["de"], r["w"], r["eg"], 1 if r["eg"] > 1.0 else 0) for r in Rn])
        hi = [r for r in Rn if r["eg"] > 1.0]
        write_dat("rule_a_ring_n%d.dat" % n, ["fig2_rule (a), n=%d, points with eps/gap > 1 (ringed)" % n],
                  ["de", "w"], [(r["de"], r["w"]) for r in hi])
    R12 = sorted((r for r in rows if r["n"] == 12), key=lambda r: r["de"])   # L69-70
    write_dat("rule_a_law.dat", ["fig2_rule (a), dotted law 2 sqrt(2 chi0 de) of the n=12 rows; source %s" % rel(t3)],
              ["de", "law"], [(r["de"], r["law"]) for r in R12])
    D = R.parse_t2_iv(t2)                                   # L78-80
    for de in sorted(D):
        write_dat("rule_b_de%g.dat" % de, ["fig2_rule (b), de=%g; source %s block (iv) (parse_t2_iv)" % (de, rel(t2))],
                  ["n", "w"], D[de])
    for key, name, c, m, ls in C.LAB:                       # L91-97
        for n in (57, 115):
            P = sorted((r["Jz"], r["law_ratio_out"]) for r in S["rows"]
                       if r["n"] == n and r["label"] == key and r["Jz"] >= 1.6 and r.get("law_ratio_out"))
            if P:
                write_dat("rule_c_n%d_%s.dat" % (n, key), ["fig2_rule (c), n=%d, %s: rows[*].law_ratio_out, Jz >= 1.6"
                                                           % (n, key)], ["J", "ratio"], P)
    CE = S["claims"]["C-E"]["rows"]                          # L106-111
    for key, name, c, m, ls in C.LAB:
        P = sorted((r["Jz"], r["ratio"]) for r in CE if r["label"] == key)
        if P:
            write_dat("rule_d_%s.dat" % key, ["fig2_rule (d), %s: claims['C-E'].rows ratio = de*(115)/de*(57)" % key],
                      ["J", "ratio"], P)
    return rows, D


# ---------------------------------------------------------------- fig3_mechanism and figS1
def export_method(M):
    F = M["families"]
    gs = {}
    for p in glob.glob(os.path.join(C.METH, "laptop_post", "out", "gsscan", "gsscan_n*_J*.json")):   # L34-36
        g = C.rj(p)
        gs[(g["n"], round(g["Jz"], 1))] = g
    src = rel(C.F_METH_SUMMARY)
    # (a, b) of fig3_mechanism.py, L38-56: vs subspace dimension D
    ab = []
    for n in (57, 115):
        for key, fam in F.items():
            nn, j = key.split("_")
            nn, j = int(nn), float(j)
            if nn != n or j not in JS or "gs_random" not in fam:
                continue
            tag = "n%d_J%s" % (n, JS[j])
            P = sorted(fam["gs_random"], key=lambda p: p["D"])
            write_dat("mech_ab_%s_rr.dat" % tag, ["fig3_mechanism (a,b): families[%s].gs_random; %s" % (key, src)],
                      ["D", "dms"], [(p["D"], p["dm_s"]) for p in P])
            if "gs_projected" in fam:
                Q = sorted(fam["gs_projected"], key=lambda p: p["D"])
                write_dat("mech_ab_%s_proj.dat" % tag, ["fig3_mechanism (a,b): families[%s].gs_projected" % key],
                          ["D", "dms"], [(p["D"], p["dm_s"]) for p in Q])
            g = gs.get((n, j))
            if g:
                write_dat("mech_ab_%s_mean.dat" % tag, ["fig3_mechanism (a,b): gsscan_n%d_J%s.json nested[*].sample_mean"
                                                        % (n, JS[j])],
                          ["D", "dms"], [(r["D"], r["sample_mean"]["dm_s"]) for r in g["nested"]])
            if "pipeline_floor" in fam:
                p = fam["pipeline_floor"][0]
                write_dat("mech_ab_%s_pipe.dat" % tag, ["fig3_mechanism (a,b): families[%s].pipeline_floor[0]" % key],
                          ["D", "dms"], [(p["D"], p["dm_s"])])
            ab.append((n, j))
    # every family against the energy ratio: fig3_mechanism.py L75-93 (n=57, Jz 1.6/2.5/4.0) and
    # figS1_bias_vs_ratio.py L20-52 (every key with gs_random); identical expressions, one table per series
    keys = sorted([k for k, fam in F.items() if "gs_random" in fam],
                  key=lambda k: (int(k.split("_")[0]), float(k.split("_")[1])))
    for key in keys:
        fam = F[key]
        n, j = int(key.split("_")[0]), float(key.split("_")[1])
        tag = "n%d_J%s" % (n, JS[j])
        for fn in ("gs_random", "gs_top", "gs_projected", "kscan_ideal", "kscan_floor"):
            if fn in fam:
                P = sorted(fam[fn], key=lambda p: p["ratio"])
                write_dat("fam_%s_%s.dat" % (tag, fn), ["families[%s].%s sorted by ratio; %s" % (key, fn, src)],
                          ["ratio", "dms"], [(p["ratio"], p["dm_s"]) for p in P])
        pipe = [(p["ratio"], p["dm_s"]) for fn, v in fam.items() if fn.startswith("pipeline_") for p in v]
        write_dat("fam_%s_pipe.dat" % tag, ["families[%s].pipeline_* (all variants): stars" % key], ["ratio", "dms"],
                  pipe)
        bo = [(p["ratio"], p["dm_s_rot"]) for fn, v in fam.items() if fn.startswith("bo_") for p in v]
        if bo:
            write_dat("fam_%s_bo.dat" % tag, ["families[%s].bo_*: ratio, dm_s_rot (labels of the physical state)" % key],
                      ["ratio", "dmsrot"], bo)
        b = M["bias_at_ibm_energy"].get(key)
        if b:
            write_dat("fam_%s_ibm.dat" % tag, ["bias_at_ibm_energy[%s]: ibm_ratio (dotted line), dm_s (diamond);" % key,
                                                "extrap = 1 if status == 'extrapolated' (not drawn differently)"],
                      ["ratio", "dms", "extrap"],
                      [(b["ibm_ratio"], b["dm_s"] if b["dm_s"] is not None else float("nan"),
                        1 if b["status"] == "extrapolated" else 0)])
    return F, gs, keys, ab


def panels(tex):
    """Split a groupplot .tex into (options, body) per \\nextgroupplot, with bracket matching."""
    out, i = [], 0
    while True:
        i = tex.find("\\nextgroupplot[", i)
        if i < 0:
            return out
        j, depth = i + len("\\nextgroupplot["), 1
        while depth:
            depth += {"[": 1, "]": -1}.get(tex[j], 0)
            j += 1
        nxt = tex.find("\\nextgroupplot[", j)
        end = tex.find("\\end{groupplot}", j)
        out.append((tex[i + 15:j - 1], tex[j:nxt if 0 <= nxt < end else end]))
        i = j


def tex_check(RM):
    """The .tex files draw every exported table, nothing outside the axis limits, and the stored diamond status."""
    log("=== consistency of the .tex files with the tables ===")
    used = set()
    for name in ("fig_rule", "fig_mechanism", "fig_bias_ratio"):
        p = os.path.join(HERE, name + ".tex")
        if not os.path.exists(p):
            log("  %s.tex not found: skipped" % name)
            continue
        tex = open(p, encoding="utf-8").read()
        npts = 0
        for opts, body in panels(tex):
            files = set(re.findall(r"\{dat/([\w.]+\.dat)\}", body))
            files |= {"fam_%s_%s.dat" % (a, b) for a, b in re.findall(r"\\F\{[^}]*\}\{([\w.]+)\}\{(\w+)\}", body)}
            files |= {"fam_%s_bo.dat" % a for a in re.findall(r"\\Bo\{([\w.]+)\}", body)}
            files |= {"mech_ab_%s_%s.dat" % (a, s) for a in re.findall(r"\\ab\{([\w.]+)\}", body)
                      for s in ("rr", "proj", "mean", "pipe")}
            files |= {"rule_c_n%s_%s.dat" % (a, b) for a, b in re.findall(r"\\pts\{[^}]*\}\{(\d+)\}\{(\w+)\}", body)}
            if not files:
                continue
            lim = {k: float(v) for k, v in re.findall(r"\b(xmin|xmax|ymin|ymax)=([-0-9.e]+)", opts)}
            for f in files:
                d = read_dat(f)
                cols = list(d[0].keys())
                for r in d:
                    x, y = r[cols[0]], r[cols[1]]
                    assert lim["xmin"] < x < lim["xmax"] and lim["ymin"] < y < lim["ymax"], (name, f, x, y, lim)
                    npts += 1
            used |= files
            for style, tag in re.findall(r"\\F\{(fIbmX?)\}\{([\w.]+)\}\{ibm\}", body) + \
                    re.findall(r"\\addplot\[(fIbmX?)\] table\[[^\]]*\] \{dat/fam_([\w.]+)_ibm\.dat\}", body):
                n, j = tag[1:].split("_J")
                st = RM["bias_at_ibm_energy"]["%s_%s" % (n, j)]["status"]
                assert (style == "fIbmX") == (st == "extrapolated"), (name, tag, style, st)
                log("  %-15s %-10s diamond %-5s <-> status %s  OK" % (name, tag, "open" if style == "fIbmX"
                                                                       else "filled", st))
        log("  %-15s every drawn point lies inside its panel's axis limits (%d points)  OK" % (name, npts))
    unused = sorted(set(WRITTEN) - used)
    assert not unused, unused
    log("  every exported table is drawn (%d tables)  OK" % len(used))
    log("")


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".dat"):
            os.remove(os.path.join(OUT, f))
    S = C.map_summary()
    M = C.meth_summary()
    rows, D = export_rule(S)
    F, gs, keys, ab = export_method(M)
    log("export_sm_method.py check log (python -B; nothing recomputed; exact float equality unless stated)")
    log("tables written: %d (dat/)" % len(WRITTEN))
    log("")

    # ===== independent reads =====
    with open(C.F_MAP_SUMMARY, encoding="utf-8") as f:
        RAW = json.load(f)
    with open(C.F_METH_SUMMARY, encoding="utf-8") as f:
        RM = json.load(f)
    t3txt = open(os.path.join(C.R3, "t3_comb.txt"), encoding="utf-8").read()
    t2txt = open(os.path.join(C.R3, "t2_local.txt"), encoding="utf-8").read()

    log("=== fig2_rule (figS:rule) ===")
    log("[a] values against the raw lines of t3_comb.txt")
    for n, de in ((6, 1e-4), (9, 0.03), (12, 0.3)):
        line = [ln for ln in t3txt.splitlines() if re.search(r"n=\s*%d\s" % n, ln) and "de=%.1e" % de in ln][0]
        w = float(re.search(r"exact w=([0-9.]+)", line).group(1))
        d = [r for r in read_dat("rule_a_n%d.dat" % n) if abs(r["de"] - de) < 1e-12][0]
        assert d["w"] == w
        log("  n=%-2d de=%g  w=%.5f  OK" % (n, de, w))
    ns = sorted({r["n"] for r in rows})
    assert ns == [6, 9, 12]
    ring = [(r["n"], r["de"], r["eg"], r["w"]) for r in rows if r["eg"] > 1.0]
    log("  caption 'n = 6, 9, 12': n in file = %s  OK" % ns)
    log("  ringed (eps/gap > 1): %s" % [(a, b, c, d) for a, b, c, d in ring])
    w6, w12 = [r["w"] for r in rows if r["n"] == 6 and r["de"] == 0.3][0], [r["w"] for r in rows
                                                                           if r["n"] == 12 and r["de"] == 0.3][0]
    eg12 = [r["eg"] for r in rows if r["n"] == 12 and r["de"] == 0.3][0]
    assert all(r[1] == 0.3 for r in ring) and abs(w12 / w6 - 1) < 0.005 and eg12 == 2.14
    log("  caption 'intensive above the gap': w(n=12)/w(n=6) at de=0.3 = %.5f/%.5f = %.4f, eps/gap(n=12) = %.2f  OK"
        % (w12, w6, w12 / w6, eg12))
    law = read_dat("rule_a_law.dat")
    assert [r["law"] for r in law] == [r["law"] for r in sorted((r for r in rows if r["n"] == 12),
                                                                 key=lambda r: r["de"])]
    log("  dotted law = 2sqrt(2chi0 de) column of the n=12 rows (%d points)  OK" % len(law))
    log("[b] t2_local.txt block (iv)")
    hdr = re.search(r"== \(iv\).*TFIM1D h=([0-9.]+), O=Z_0, range ([0-9.]+)", t2txt)
    assert hdr and float(hdr.group(1)) == 1.5 and float(hdr.group(2)) == 2.0
    log("  caption 'h = 1.5', 'full range is 2': block header h=%s, range %s  OK" % (hdr.group(1), hdr.group(2)))
    for de in sorted(D):
        d = read_dat("rule_b_de%g.dat" % de)
        assert [(int(r["n"]), r["w"]) for r in d] == D[de]
        log("  de=%g: %s  OK" % (de, ", ".join("n=%d w=%.3f" % (a, b) for a, b in D[de])))
    assert max(w for de in D for _, w in D[de]) == 2.0
    log("[c] law_ratio_out against the JSON")
    allrows = [r for r in RAW["rows"] if r["n"] in (57, 115) and r["Jz"] >= 1.6]
    have = [r for r in allrows if r.get("law_ratio_out")]
    miss = sorted((r["n"], r["label"], r["Jz"]) for r in allrows if not r.get("law_ratio_out"))
    npts = sum(len(read_dat(f)) for f in WRITTEN if f.startswith("rule_c_"))
    assert npts == len(have)
    log("  rows with Jz >= 1.6 (n=57, 115): %d; with a stored law_ratio_out (drawn): %d; without: %d %s"
        % (len(allrows), len(have), len(miss), miss))
    for n, key, J in ((57, "m_s", 6.0), (115, "m_s", 6.0), (115, "C2_bar", 1.6), (57, "Z_boundary", 2.0)):
        d = [r for r in read_dat("rule_c_n%d_%s.dat" % (n, key)) if abs(r["J"] - J) < 1e-9][0]
        v = C.map_row(RAW, n, J, key)["law_ratio_out"]
        assert d["ratio"] == v
        log("  n=%-3d %-10s Jz=%.1f ratio=%.4f  OK" % (n, key, J, v))
    out = sorted((r["n"], r["label"], r["Jz"], round(r["law_ratio_out"], 4)) for r in have
                 if not 0.8 <= r["law_ratio_out"] <= 1.25)
    assert [(a, b) for a, b, c, d in out] == [(57, "m_s")] * 3 + [(115, "m_s")] * 3 and all(c >= 5.0 for _, _, c, _ in out)
    log("  caption 'band [0.8, 1.25]; the outliers are m_s at Jz >= 5': points outside the band = %s  OK" % out)
    inb = [r["law_ratio_out"] for r in have if 0.8 <= r["law_ratio_out"] <= 1.25]
    log("  drawn points inside the band: %d, range %.4f-%.4f" % (len(inb), min(inb), max(inb)))
    log("[d] claims C-E")
    CE = RAW["claims"]["C-E"]["rows"]
    zb = [r["ratio"] for r in CE if r["label"] == "Z_bulk"]
    av = [r["ratio"] for r in CE if r["label"] in ("m_s", "Czz_bar", "C2_bar")]
    assert len(zb) == 1 and abs(zb[0] - 57 / 115) < 1e-3 and min(av) > 0.95 and max(av) < 1.2
    assert read_dat("rule_d_Z_bulk.dat")[0]["ratio"] == zb[0]
    log("  caption 'Z_bulk follows 57/115': ratio %.4f vs 57/115 = %.4f  OK" % (zb[0], 57 / 115))
    log("  caption 'averages are intensive': %d ratios in %.4f-%.4f  OK" % (len(av), min(av), max(av)))
    log("")

    log("=== fig3_mechanism (figS:mechanism) ===")
    log("[a,b] panels drawn (n, Jz): %s" % ab)
    assert sorted(ab) == [(57, 1.2), (57, 1.6), (57, 2.5), (57, 4.0), (115, 1.2), (115, 1.6), (115, 2.5)]
    E = C.meth_emu()
    for n, j in ab:
        tag = "n%d_J%s" % (n, JS[j])
        st = read_dat("mech_ab_%s_pipe.dat" % tag)[0]
        key = "%d_%s" % (n, JS[j])
        assert st["dms"] == RM["families"][key]["pipeline_floor"][0]["dm_s"]
        e = E[(n, j)]
        assert e["primary_alias"] == "floor" and st["dms"] == e["var"]["primary"]["err"]["dm_s"]
        mean = read_dat("mech_ab_%s_mean.dat" % tag)
        rr = read_dat("mech_ab_%s_rr.dat" % tag)
        assert [r["dms"] for r in rr] == [p["dm_s"] for p in sorted(RM["families"][key]["gs_random"], key=lambda p: p["D"])]
        log("  n=%-3d Jz=%.1f star (pipeline_floor = primary variant at the published budget) dm_s=%+.4f D=%d; "
            "RR %d pts; max |sample mean| = %.1e" % (n, j, st["dms"], st["D"], len(rr), max(abs(r["dms"]) for r in mean)))
    smax = max(abs(r["dms"]) for n, j in ab for r in read_dat("mech_ab_n%d_J%s_mean.dat" % (n, JS[j])))
    assert smax < 6e-4
    log("  text 'sample mean reproduces the reference m_s to 6e-4 in every case': max |dm_s| = %.2e  OK" % smax)
    rr12 = RM["families"]["57_1.2"]
    log("[c] n=57, Jz = 1.6, 2.5, 4.0 (Jz = 1.2 has no reported ratio); families drawn: gs_random, gs_top,"
        " kscan_ideal, kscan_floor, pipeline_*; gs_projected is not drawn in (c)")
    for j in (1.6, 2.5, 4.0):
        key = "57_%s" % JS[j]
        b = RM["bias_at_ibm_energy"][key]
        d = read_dat("fam_n57_J%s_ibm.dat" % JS[j])[0]
        assert d["ratio"] == b["ibm_ratio"] and d["dms"] == b["dm_s"]
        log("  Jz=%.1f reported r=%.4f, diamond dm_s=%.5f (%s)  OK" % (j, b["ibm_ratio"], b["dm_s"], b["status"]))
    assert "57_1.2" not in RM["bias_at_ibm_energy"] and "115_1.2" not in RM["bias_at_ibm_energy"]
    log("")

    log("=== figS1_bias_vs_ratio ===")
    log("  panels (every key with gs_random): %s" % keys)
    assert keys == ["57_1.2", "57_1.6", "57_2.5", "57_4.0", "115_1.2", "115_1.6", "115_2.5"]
    for key in keys:
        n, j = key.split("_")
        tag = "n%s_J%s" % (n, j)
        fams = [fn for fn in ("gs_random", "gs_top", "gs_projected", "kscan_ideal", "kscan_floor")
                if os.path.exists(os.path.join(OUT, "fam_%s_%s.dat" % (tag, fn)))]
        npipe = len(read_dat("fam_%s_pipe.dat" % tag))
        nbo = len(read_dat("fam_%s_bo.dat" % tag)) if os.path.exists(os.path.join(OUT, "fam_%s_bo.dat" % tag)) else 0
        ibm = read_dat("fam_%s_ibm.dat" % tag)[0] if os.path.exists(os.path.join(OUT, "fam_%s_ibm.dat" % tag)) else None
        assert npipe == sum(len(v) for fn, v in RM["families"][key].items() if fn.startswith("pipeline_"))
        log("  %-7s families %s; %d pipeline stars; %d rotation circles; reported r %s" % (
            key, fams, npipe, nbo, "none" if ibm is None else "%.4f, diamond %.5f, %s" % (
                ibm["ratio"], ibm["dms"], "extrapolated" if ibm["extrap"] else "interpolated")))
    bo = [(k, fn, p["variant"]) for k in keys for fn, v in RM["families"][k].items() if fn.startswith("bo_") for p in v]
    variants = sorted({v.split("_")[0] for _, _, v in bo})
    assert variants == ["GV", "YX"]
    log("  caption 'the two rotation variants': bo_* variants %s (YX = R_Y on the control wire, minority and majority"
        " orientation give the same point; GV = Givens)  OK" % variants)
    for key, fn, i in (("57_1.2", "bo_primary", 2), ("57_2.5", "bo_dev_rec", 0)):
        p = RM["families"][key][fn][i]
        n, j = key.split("_")
        d = read_dat("fam_n%s_J%s_bo.dat" % (n, j))
        assert any(r["ratio"] == p["ratio"] and r["dmsrot"] == p["dm_s_rot"] for r in d)
        log("  %s %s %s: ratio=%.4f dm_s_rot=%.4f  OK" % (key, fn, p["variant"], p["ratio"], p["dm_s_rot"]))
    log("")
    with open(os.path.join(HERE, "ranges.txt"), "w", encoding="utf-8", newline="\n") as f:
        for name in sorted(WRITTEN):
            d = read_dat(name)
            cols = list(d[0].keys())
            f.write("%-34s " % name + "  ".join("%s %.4g..%.4g" % (c, min(r[c] for r in d), max(r[c] for r in d))
                                                 for c in cols[:2]) + "\n")
    tex_check(RM)
    log("all assertions passed")
    with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
