"""real_data/checks/r11/fp_bias_curve_recompute.py  (R11 fix pass, fixer FP, 2026-11-13)
Copy of paper/reviews/R10_2026-11-12/scratch/phys-declared-stats/recompute_testA_bias.py with its paths adapted
(the work tree is found from this file; outputs fp_bias_curve_recompute_out.txt / .json next to this file) and one
block appended at the end (marked): the states outside the ratio range of the four plotted couplings, which in
the R10 review had been printed by a typed command (ratio_outliers_out.txt), and the range of the primary labels
over both sizes.   python -B -I fp_bias_curve_recompute.py

Text of the original header:
R10 reviewer phys-declared-stats: own recomputation of
 (1) the blind test of the bias curve (final_tests Test A; main.tex 707-718, supplement S14),
 (2) the exploratory numbers of Sec. V that the mission names (the '-12 to +24 %' spread, the corrected misses),
from the stored per-point outputs.  Reads in place; writes only next to itself.

m_s is rebuilt from the stored site labels and the graph's sublattice signs (not read from the stored 'm_s'/'err'
fields), and the energy error from the stored energies.
"""
import glob
import json
import os
import re

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..")).replace(chr(92), "/")   # the work tree, found from this file (R11: path adapted)
FT = ROOT + "/phase3/full_runs/final_tests"
OUT = FT + "/out_20261106T120830Z/out"
M = ROOT + "/phase3/full_runs/method/out_20261030T003230Z/out"
BL = ROOT + "/phase3/full_runs/bias_law"
QPU = ROOT + "/phase3/full_runs/qpu/analysis/analysis.json"
HERE = os.path.dirname(os.path.abspath(__file__))
NE = {19: 20, 57: 64, 115: 132}
DIST = {19: 3, 57: 5, 115: 7}
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def rj(p):
    with open(p) as f:
        return json.load(f)


G = {n: rj(FT + "/code/graphs/hh_d%d.json" % d) for n, d in DIST.items()}
ETA = {n: np.array(G[n]["eta"], float) for n in G}
for n in G:
    assert G[n]["n"] == n and len(G[n]["edges"]) == NE[n]


def ms_of(Z, n):
    return float(np.dot(ETA[n], np.array(Z)) / n)


def interp_curve(curve, de):
    c = np.array(curve)
    return float(np.interp(np.sqrt(max(de, 0.0)), np.sqrt(np.maximum(c[:, 0], 0.0)), c[:, 1]))


def chord(c19, J, de):
    dn = (-NE[19] * J / 4 - c19["E0"]) / 19
    return float((1 - c19["ms0"]) * np.sqrt(max(de, 0.0) / dn))


# ------------------------------------------------------------------------------------------------ (1) blind test
P("=== (1) Blind test of the curve (declared rule: mean miss <= 0.2 tau at n=57, <= 0.6 tau at n=115, all 7 ratios in [0.75, 1.3]) ===")
A_JZ = {57: [1.5, 1.7, 2.8, 3.2], 115: [1.5, 1.7, 2.8]}
C19 = {J: rj(OUT + "/n19/curve_J%.1f.json" % J) for J in A_JZ[57]}
rows = []
for n in (57, 115):
    for J in A_JZ[n]:
        e = rj(OUT + "/emu/emu_n%d_J%.1f.json" % (n, J))
        r = rj(OUT + "/ref/ref_n%d_J%.1f.json" % (n, J))
        v = e["var"]["primary"]
        m0 = ms_of(r["labels"]["Z"], n)
        m = ms_of(v["labels"]["Z"], n)
        assert abs(m0 - e["ref_m_s"]) < 1e-12 and abs(m - v["labels"]["m_s"]) < 1e-12, (m0, e["ref_m_s"], m, v["labels"]["m_s"])
        assert abs(r["E0"] - e["E0"]) < 1e-12
        de = (v["E"] - r["E0"]) / n
        dm = m - m0
        tau = 0.06 * abs(m0)
        c = interp_curve(C19[J]["curve"], de)
        ch = chord(C19[J], J, de)
        row = dict(n=n, J=J, m0=m0, de=de, dm=dm, tau=tau, raw=abs(dm) / tau, pred=c, miss=abs(dm - c) / tau, ratio=dm / c,
                   chord=abs(dm - ch) / tau, small=abs(C19[J]["ms0"] - m0) / tau, signed_resid=(dm - c) / tau,
                   de_max_curve=float(np.array(C19[J]["curve"])[:, 0].max()))
        rows.append(row)
by = {(r["n"], r["J"]): r for r in rows}
for J in A_JZ[115]:
    r = by[(115, J)]
    e57 = rj(OUT + "/emu/emu_n57_J%.1f.json" % J)
    ref57 = rj(OUT + "/ref/ref_n57_J%.1f.json" % J)
    m57 = ms_of(ref57["labels"]["Z"], 57)
    pts = []
    for k in ("ideal", "primary", "dev_rec", "dev_ps"):
        v = e57["var"][k]
        pts.append(((v["E"] - ref57["E0"]) / 57, ms_of(v["labels"]["Z"], 57) - m57))
    pts.sort()
    s = np.sqrt(np.r_[0, [p[0] for p in pts]])
    y = np.r_[0, [p[1] for p in pts]]
    x = np.sqrt(r["de"])
    c57 = float(np.interp(x, s, y)) if x <= s[-1] else float(y[-1] + (y[-1] - y[-2]) / (s[-1] - s[-2]) * (x - s[-1]))
    r["curve57"] = abs(r["dm"] - c57) / r["tau"]
    r["curve57_extrapolated"] = bool(x > s[-1])
    r["truth57"] = abs(m57 - r["m0"]) / r["tau"]
    m19 = C19[J]["ms0"]
    for name, g in (("a_b_over_n", lambda q: 1 / q), ("a_b_edges_over_n", lambda q: NE[q] / q), ("a_b_over_sqrt_n", lambda q: q ** -0.5)):
        b = (m19 - m57) / (g(19) - g(57))
        r[name] = abs(m57 + b * (g(115) - g(57)) - r["m0"]) / r["tau"]
P("%4s %4s %8s %9s %8s %7s %8s %7s %7s %7s | n=115 only: %7s %7s %7s %7s %7s" % ("n", "Jz", "m0", "de", "dm", "raw", "curve19", "ratio", "chord", "n19tr", "curve57", "tr57", "a+b/n", "a+bNe/n", "a+b/rt"))
for r in rows:
    extra = ""
    if r["n"] == 115:
        extra = " | %7.3f %7.3f %7.3f %7.3f %7.3f %s" % (r["curve57"], r["truth57"], r["a_b_over_n"], r["a_b_edges_over_n"], r["a_b_over_sqrt_n"],
                                                       "(n=57 curve extrapolated beyond its last point)" if r["curve57_extrapolated"] else "")
    P("%4d %4.1f %8.4f %9.5f %+8.4f %7.3f %8.4f %7.4f %7.3f %7.3f%s   signed residual %+0.3f tau; de/de_max(n19 curve) %.3f" % (
        r["n"], r["J"], r["m0"], r["de"], r["dm"], r["raw"], r["miss"], r["ratio"], r["chord"], r["small"], extra, r["signed_resid"], r["de"] / r["de_max_curve"]))
S = {}
for n in (57, 115):
    rs = [r for r in rows if r["n"] == n]
    S[n] = {k: (float(np.mean([r[k] for r in rs])), float(np.min([r[k] for r in rs])), float(np.max([r[k] for r in rs])))
            for k in rs[0] if k in ("raw", "miss", "chord", "small", "curve57", "truth57", "a_b_over_n", "a_b_edges_over_n", "a_b_over_sqrt_n")}
    P("n=%d  mean (min, max):" % n, {k: "%.4f (%.4f, %.4f)" % v for k, v in S[n].items()})
ratios = [r["ratio"] for r in rows]
P("ratios: min %.4f max %.4f ; all in [0.75, 1.3]: %s" % (min(ratios), max(ratios), all(0.75 <= x <= 1.3 for x in ratios)))
P("rule: mean57 %.4f <= 0.2: %s ; mean115 %.4f <= 0.6: %s" % (S[57]["miss"][0], S[57]["miss"][0] <= 0.2, S[115]["miss"][0], S[115]["miss"][0] <= 0.6))
P("paper: '1.7 to 0.06 tau' -> %.3f to %.4f ; '2.9 to 0.34 tau' -> %.3f to %.4f ; 'ratios 0.88-1.06' -> %.4f-%.4f" % (
    S[57]["raw"][0], S[57]["miss"][0], S[115]["raw"][0], S[115]["miss"][0], min(ratios), max(ratios)))
P("how far inside the rule: mean57/limit %.2f, mean115/limit %.2f; largest single miss n=57 %.3f, n=115 %.3f tau" % (
    S[57]["miss"][0] / 0.2, S[115]["miss"][0] / 0.6, S[57]["miss"][2], S[115]["miss"][2]))
P("sign of the residual (dm - curve): n=57 %s ; n=115 %s" % ([("%+.3f" % r["signed_resid"]) for r in rows if r["n"] == 57],
                                                            [("%+.3f" % r["signed_resid"]) for r in rows if r["n"] == 115]))
# what a trivially scaled curve would have needed: the rule's ratio band [0.75, 1.3] against the exploratory spread
# all variants at the blind couplings
P("ratios of all stored variants at the blind couplings (not the rule):")
for n in (57, 115):
    for J in A_JZ[n]:
        e = rj(OUT + "/emu/emu_n%d_J%.1f.json" % (n, J))
        r = rj(OUT + "/ref/ref_n%d_J%.1f.json" % (n, J))
        m0 = ms_of(r["labels"]["Z"], n)
        d = {}
        for k, v in e["var"].items():
            if v.get("alias_of"):
                continue
            de = (v["E"] - r["E0"]) / n
            d[k] = round((ms_of(v["labels"]["Z"], n) - m0) / interp_curve(C19[J]["curve"], de), 3)
        P("  n=%d J=%.1f" % (n, J), d)

# ------------------------------------------------------------------------------------------- (2) exploratory part
P("")
P("=== (2) Exploratory analysis (bias_law): stored emulated states against the n=19 curve ===")
C = {float(k): v for k, v in rj(BL + "/inputs/n19_curves.json").items()}


def grid(n):
    return sorted(float(re.search(r"_J([0-9.]+)\.json", f).group(1)) for f in glob.glob("%s/emu/emu_n%d_J*.json" % (M, n)))


def emu(n, J):
    return rj("%s/emu/emu_n%d_J%s.json" % (M, n, J))


def family(n, J):
    e = emu(n, J)
    Pp = [("pipe_" + k, v["dE_site"], v["err"]["dm_s"]) for k, v in e["var"].items() if not v.get("alias_of")]
    Pp += [("kscan", (s["E"] - e["E0"]) / n, s["err"]["dm_s"]) for s in e.get("kscan", [])]
    f = "%s/gsscan/gsscan_n%d_J%s.json" % (M, n, J)
    if os.path.exists(f):
        g = rj(f)
        Pp += [("gs_random", s["dE_site"], s["err"]["dm_s"]) for s in g["nested"]]
        Pp += [("gs_top", s["dE_site"], s["err"]["dm_s"]) for s in g["topD"]]
    return e, Pp


expl = {}
for n in (57, 115):
    rws = []
    for J in grid(n):
        e = emu(n, J)
        v = e["var"]["primary"]
        m0 = e["ref_m_s"]
        # independent m_s from the site labels
        ref = rj("%s/ref/ref_n%d_J%s.json" % (M, n, J))
        m0b = ms_of(ref["labels"]["Z"], n)
        mb = ms_of(v["labels"]["Z"], n)
        assert abs(m0b - m0) < 1e-10 and abs((mb - m0b) - v["err"]["dm_s"]) < 1e-10
        de = (v["E"] - ref["E0"]) / n
        assert abs(de - v["dE_site"]) < 1e-12
        t = 0.06 * m0
        d = mb - m0b
        c = interp_curve(C[J]["curve"], de)
        rws.append(dict(J=J, de=de, dm=d, raw=abs(d) / t, corrected=abs(d - c) / t, ratio=d / c, small=abs(C[J]["ms0"] - m0) / t,
                        chord=abs(d - chord(C[J], J, de)) / t, signed=(d - c) / t))
    expl[n] = rws
    P("n=%d primary labels at %d couplings: raw mean %.3f, corrected mean %.4f (max %.3f), n19 truth mean %.3f, chord mean %.3f" % (
        n, len(rws), np.mean([r["raw"] for r in rws]), np.mean([r["corrected"] for r in rws]), max(r["corrected"] for r in rws),
        np.mean([r["small"] for r in rws]), np.mean([r["chord"] for r in rws])))
    P("   per coupling  J: ratio dm/curve, corrected miss (tau), signed residual (tau)")
    for r in rws:
        P("     J=%.1f ratio %.4f  corrected %.4f  signed %+.4f  raw %.3f  de %.5f" % (r["J"], r["ratio"], r["corrected"], r["signed"], r["raw"], r["de"]))
    rr = [r["ratio"] for r in rws]
    P("   primary-label ratio over ALL %d couplings: min %.4f max %.4f  -> %.1f %% below, %.1f %% above the curve" % (
        len(rws), min(rr), max(rr), 100 * (1 - min(rr)), 100 * (max(rr) - 1)))
    tr = [r["corrected"] for r in rws if r["J"] >= 1.6]
    te = [r["corrected"] for r in rws if r["J"] < 1.5]
    P("   corrected miss: training couplings (Jz >= 1.6) mean %.4f max %.4f ; test couplings (Jz < 1.5) %.3f-%.3f, mean %.3f" % (
        np.mean(tr), max(tr), min(te), max(te), np.mean(te)))
    # bootstrap over couplings of the mean corrected miss (couplings are a fixed grid, so this is only a description of spread)
    rng = np.random.default_rng(57 * n)
    a = np.array([r["corrected"] for r in rws])
    bm = a[rng.integers(0, len(a), (20000, len(a)))].mean(1)
    P("   mean corrected miss %.3f, sd over couplings %.3f, bootstrap-over-couplings 95 %% range of the mean [%.3f, %.3f], median %.3f" % (
        a.mean(), a.std(ddof=1), np.percentile(bm, 2.5), np.percentile(bm, 97.5), np.median(a)))

P("")
P("--- the sentence 'lie within -12 to +24 % of that curve' (blw:nulls.spread_pct_low/high) ---")
allrat = {}
for sel_name, Js in (("four plotted couplings 1.2, 1.6, 2.5, 4.0 (as in bias_law.py)", (1.2, 1.6, 2.5, 4.0)), ("all stored couplings", None)):
    rat = []
    detail = []
    for n in (57, 115):
        for J in (Js if Js else grid(n)):
            _, Pp = family(n, J)
            for name, de, dm in Pp:
                c = interp_curve(C[J]["curve"], de)
                if c > 0:
                    rat.append(dm / c)
                    detail.append((dm / c, n, J, name, de))
    detail.sort()
    P("%s: %d states, ratio min %.4f (n=%d J=%.1f %s) max %.4f (n=%d J=%.1f %s) -> -%.2f %% .. +%.2f %%" % (
        sel_name, len(rat), detail[0][0], detail[0][1], detail[0][2], detail[0][3], detail[-1][0], detail[-1][1], detail[-1][2], detail[-1][3],
        100 * (1 - min(rat)), 100 * (max(rat) - 1)))
    allrat[sel_name] = detail
    q = np.percentile(rat, [5, 25, 50, 75, 95])
    P("    quantiles 5/25/50/75/95 %%: %s ; fraction within +-10 %%: %.2f" % (np.round(q, 3).tolist(), float(np.mean(np.abs(np.array(rat) - 1) <= 0.10))))
    for n in (57, 115):
        rn = [d[0] for d in detail if d[1] == n]
        P("    n=%d: %d states, min %.4f max %.4f median %.4f" % (n, len(rn), min(rn), max(rn), np.median(rn)))

P("")
P("--- device labels against the n=19 curve (the sentence also names 'our device labels at three couplings') ---")
Q = rj(QPU)
dev = []
for J in ("1.2", "1.6", "4.0"):
    e = emu(57, float(J))
    t = 0.06 * e["ref_m_s"]
    for mth in ("rec", "ps"):
        v = Q["points"][J]["device"][mth]
        de = v["eps"] / 57
        d = v["dm_s"]
        c = interp_curve(C[float(J)]["curve"], de)
        dev.append(dict(J=float(J), reading=mth, de=de, dm=d, curve=c, ratio=d / c, raw=abs(d) / t, corrected=abs(d - c) / t,
                        chord=abs(d - chord(C[float(J)], float(J), de)) / t))
        P("  device J=%s %s: de %.5f dm %+.4f curve %.4f ratio %.4f (%+.1f %%)  raw %.3f tau corrected %.3f tau chord %.3f tau" % (
            J, mth, de, d, c, d / c, 100 * (d / c - 1), abs(d) / t, abs(d - c) / t, dev[-1]["chord"]))
dr = [x["ratio"] for x in dev]
P("  device ratio range: %.4f .. %.4f  -> %+.1f %% .. %+.1f %% ; raw mean %.3f, corrected mean %.3f (max %.3f), chord mean %.3f" % (
    min(dr), max(dr), 100 * (min(dr) - 1), 100 * (max(dr) - 1), np.mean([x["raw"] for x in dev]), np.mean([x["corrected"] for x in dev]),
    max(x["corrected"] for x in dev), np.mean([x["chord"] for x in dev])))
P("  device 'rec' readings only (3 points): ratio %s ; corrected %s" % ([round(x["ratio"], 3) for x in dev if x["reading"] == "rec"],
                                                                        [round(x["corrected"], 3) for x in dev if x["reading"] == "rec"]))

P("")
P("--- limited power of the blind test: linear interpolation in Jz of the exploratory corrected misses ---")
for n in (57, 115):
    Jg = np.array([r["J"] for r in expl[n]])
    cg = np.array([r["corrected"] for r in expl[n]])
    sg = np.array([r["signed"] for r in expl[n]])
    rg = np.array([r["ratio"] for r in expl[n]])
    pred, preds, predr, obs = [], [], [], []
    for J in A_JZ[n]:
        pred.append(float(np.interp(J, Jg, cg)))
        preds.append(float(np.interp(J, Jg, sg)))
        predr.append(float(np.interp(J, Jg, rg)))
        obs.append(by[(n, J)])
    P("n=%d  interpolated |miss| %s mean %.4f ; observed %s mean %.4f ; max |difference| %.4f" % (
        n, np.round(pred, 4).tolist(), np.mean(pred), np.round([o["miss"] for o in obs], 4).tolist(), np.mean([o["miss"] for o in obs]),
        max(abs(a - o["miss"]) for a, o in zip(pred, obs))))
    P("       interpolated ratio %s ; observed ratio %s ; max |difference| %.4f" % (
        np.round(predr, 4).tolist(), np.round([o["ratio"] for o in obs], 4).tolist(), max(abs(a - o["ratio"]) for a, o in zip(predr, obs))))
    P("       neighbours' exploratory ratios bracket every blind ratio: %s" % all(
        min(rg[np.searchsorted(Jg, J) - 1], rg[np.searchsorted(Jg, J)]) - 1e-9 <= by[(n, J)]["ratio"] <= max(rg[np.searchsorted(Jg, J) - 1], rg[np.searchsorted(Jg, J)]) + 1e-9
        for J in A_JZ[n]))

# ---------------------------------------------------------------------------------------------------------------------
# Appended in the R11 fix pass (fixer FP, 2026-11-13). Nothing above this line was changed except the paths.
# (a) range of the ratio of the primary labels over both sizes; (b) the stored states whose ratio lies outside the
# range of the four plotted couplings (replaces ratio_outliers_out.txt of the R10 review, which had no script).
P("")
P("--- appended (R11): primary labels over both sizes, and states outside the range of the four plotted couplings ---")
rr_all = [r["ratio"] for n in (57, 115) for r in expl[n]]
P("primary-label ratio over all %d coupling-size pairs (%d + %d): %.4f-%.4f" % (
    len(rr_all), len(expl[57]), len(expl[115]), min(rr_all), max(rr_all)))
four = allrat["four plotted couplings 1.2, 1.6, 2.5, 4.0 (as in bias_law.py)"]
lo4, hi4 = four[0][0], four[-1][0]
P("ratio range of the %d states at the four plotted couplings: [%.4f, %.4f]" % (len(four), lo4, hi4))
outside = []
for (ratio, n, J, name, de) in allrat["all stored couplings"]:
    if ratio < lo4 - 1e-12 or ratio > hi4 + 1e-12:
        t = 0.06 * emu(n, J)["ref_m_s"]
        c = interp_curve(C[J]["curve"], de)
        dm = ratio * c
        outside.append(dict(ratio=ratio, n=n, J=J, family=name, de=de, raw_tau=abs(dm) / t, dev_tau=abs(dm - c) / t))
        P("  ratio %.4f n=%d J=%.1f %-12s de=%.5f  |dm-curve|=%.4f tau  raw=%.3f tau" % (ratio, n, J, name, de, abs(dm - c) / t, abs(dm) / t))
below = [o for o in outside if o["ratio"] < lo4]
above = [o for o in outside if o["ratio"] > hi4]
P("states outside the range of the four couplings: %d of %d (%d below, %d above)" % (
    len(outside), len(allrat["all stored couplings"]), len(below), len(above)))
P("  below: %s" % ["n=%d J=%.1f %s" % (o["n"], o["J"], o["family"]) for o in below])
P("  above: couplings %s ; families %s ; greatest raw bias among them raw=%.3f tau ; greatest ratio %.4f" % (
    sorted(set(o["J"] for o in above)), sorted(set(o["family"] for o in above)), max(o["raw_tau"] for o in above), max(o["ratio"] for o in above)))

json.dump(dict(blind=rows, exploratory={str(k): v for k, v in expl.items()}, device=dev, outside_four_couplings=outside),
          open(os.path.join(HERE, "fp_bias_curve_recompute_out.json"), "w"), indent=1)
open(os.path.join(HERE, "fp_bias_curve_recompute_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
