# real_data / rd_predict.py  (own code; 2026-11-12; task rd-code-learn)
#
# DECLARATION.md Sec. 5 (predictions P1-P5 of the emulation, confronted with the real labels) and the "small classical
# calculation" of Sec. 6 (exact n = 19 against the truth at n = 57 / 115). Pure functions on arrays; the only reader of
# real data is rd_common.load_real, which needs the gate. Rules are implemented as written:
#   P1-P3  t_x = (o_real - o_GS) / (o_Neel - o_GS);  F = fraction of (item, coupling) pairs with t_x > 0;  holds iff
#          F >= 0.95, per family and size, over the couplings given (the 50 of the dataset);
#   P4     D(n, Jz) = mean over items of |o_real - o_GS| / (0.06 |o_GS|);  holds iff Spearman(D, Jz) <= -0.9;
#   P5     curve of bias_law/code/n19b.py (function f, unchanged): Delta = m_real - m_GS, ratio = Delta / curve(de),
#          miss = |m_real - curve(de) - m_GS| / tau; PASS iff mean miss <= 0.2 (n = 57) and <= 0.6 (n = 115) and every
#          ratio lies in [0.75, 1.3] at the couplings where the raw miss is at least 0.2 tau.
import math

import numpy as np

import rd_common as rdc

F_MIN = 0.95
RHO_MAX = -0.9
P5_MEAN_MAX = {57: 0.2, 115: 0.6}
P5_RATIO = (0.75, 1.3)
P5_RAW_MIN = 0.2


# ------------------------------------------------------------------------------------------------ statistics
def ranks(a):
    """Ranks 1..N with ties given their average rank."""
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a))
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    """Spearman rank correlation (Pearson correlation of the average ranks); nan if one side is constant."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) != len(y) or len(x) < 2 or not (np.all(np.isfinite(x)) and np.all(np.isfinite(y))):
        return float("nan")
    rx, ry = ranks(x) - (len(x) + 1) / 2, ranks(y) - (len(y) + 1) / 2
    den = math.sqrt(float(rx @ rx) * float(ry @ ry))
    return float(rx @ ry) / den if den > 0 else float("nan")


# ------------------------------------------------------------------------------------------------ P1-P3
def t_values(o_real, o_gs, o_neel):
    """t_x of Sec. 5; nan where the Neel value equals the ground-state value (t_x undefined)."""
    o_real, o_gs, o_neel = (np.asarray(v, float) for v in (o_real, o_gs, o_neel))
    den = o_neel - o_gs
    t = np.full(den.shape, np.nan)
    ok = den != 0
    t[ok] = (o_real[ok] - o_gs[ok]) / den[ok]
    return t


def sign_test(T_by_J):
    """T_by_J: {Jz: array of t_x over the items of one family}. An undefined t_x counts as 'not > 0'."""
    Js = sorted(T_by_J)
    allt = np.concatenate([np.ravel(T_by_J[J]) for J in Js])
    N = len(allt)
    pos = np.nan_to_num(allt, nan=-1.0) > 0
    le1 = np.nan_to_num(allt, nan=2.0) <= 1
    F = float(pos.sum()) / N
    return dict(n_pairs=int(N), n_items=int(len(np.ravel(T_by_J[Js[0]]))), n_couplings=len(Js), F=F,
                holds=bool(F >= F_MIN), rule="holds iff F >= %.2f" % F_MIN,
                frac_t_le_1=float(le1.sum()) / N, frac_0_lt_t_le_1=float((pos & le1).sum()) / N,
                n_undefined=int(np.isnan(allt).sum()),
                F_per_coupling={rdc.jkey(J): float((np.nan_to_num(np.ravel(T_by_J[J]), nan=-1.0) > 0).mean()) for J in Js},
                frac_t_le_1_per_coupling={rdc.jkey(J): float((np.nan_to_num(np.ravel(T_by_J[J]), nan=2.0) <= 1).mean()) for J in Js},
                t_min=float(np.nanmin(allt)) if N > np.isnan(allt).sum() else None,
                t_max=float(np.nanmax(allt)) if N > np.isnan(allt).sum() else None)


# ------------------------------------------------------------------------------------------------ P4
def D_value(o_real, o_gs):
    """Mean over the items of |o_real - o_GS| / (0.06 |o_GS|); inf if a ground-state value is exactly 0."""
    o_real, o_gs = np.asarray(o_real, float), np.asarray(o_gs, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        d = np.abs(o_real - o_gs) / (rdc.TAU_REL * np.abs(o_gs))
    d = np.where(np.isnan(d), 0.0, d)                              # 0/0: the label equals a vanishing truth
    return float(np.mean(d))


def p4_test(D_by_J):
    Js = sorted(D_by_J)
    Dv = [D_by_J[J] for J in Js]
    rho = spearman(Js, Dv)
    return dict(n_couplings=len(Js), spearman=rho, holds=bool(rho <= RHO_MAX), rule="holds iff Spearman <= %.1f" % RHO_MAX,
                D={rdc.jkey(J): float(D_by_J[J]) for J in Js}, D_min=float(min(Dv)), D_max=float(max(Dv)))


# ------------------------------------------------------------------------------------------------ P5
def curve_value(C, J, de):
    """Function f of bias_law/code/n19b.py, unchanged: the n = 19 curve read by linear interpolation in sqrt(de).
    (numpy's interp holds the end values outside the range of the curve.)"""
    c = np.array(C[str(float(J))]['curve']); return float(np.interp(np.sqrt(max(de, 0)), np.sqrt(np.maximum(c[:, 0], 0)), c[:, 1]))


def chord_value(C, J, de, n19=19, n_edges19=20):
    """Chord between the ground and Neel states (final_tests/DECLARATION.md Sec. 3, predictor (c)):
    (1 - m_s^GS(19)) sqrt(de / de_Neel(19)), de_Neel(19) = (-20 Jz/4 - E0(19)) / 19."""
    c = C[str(float(J))]
    de_neel = (-n_edges19 * float(J) / 4 - c["E0"]) / n19
    return float((1 - c["ms0"]) * math.sqrt(max(de, 0) / de_neel))


def p5_row(J, m_real, m_gs, de, C):
    tau = rdc.TAU_REL * abs(m_gs)
    delta = m_real - m_gs
    cur = curve_value(C, J, de)
    ch = chord_value(C, J, de)
    c = np.array(C[str(float(J))]["curve"])
    return dict(Jz=J, m_real=m_real, m_gs=m_gs, tau=tau, de=de, Delta=delta, curve=cur,
                ratio=(delta / cur) if cur != 0 else None,
                raw_miss_tau=abs(delta) / tau, miss_tau=abs(m_real - cur - m_gs) / tau,
                chord=ch, miss_chord_tau=abs(m_real - ch - m_gs) / tau,
                m_s_n19=C[str(float(J))]["ms0"], miss_n19_truth_tau=abs(C[str(float(J))]["ms0"] - m_gs) / tau,
                de_inside_curve=bool(max(c[:, 0].min(), 0.0) <= de <= c[:, 0].max()),
                decides_ratio=bool(abs(delta) / tau >= P5_RAW_MIN))


def p5_summary(rows, n):
    """Numbers of one size over the rows given (the 50 couplings decide; the 45 training couplings are reported)."""
    mean = lambda k: float(np.mean([r[k] for r in rows]))
    mx = lambda k: float(np.max([r[k] for r in rows]))
    dec = [r for r in rows if r["decides_ratio"]]
    bad = [r["Jz"] for r in dec if r["ratio"] is None or not (P5_RATIO[0] <= r["ratio"] <= P5_RATIO[1])]
    rat = [r["ratio"] for r in dec if r["ratio"] is not None]
    return dict(n=n, n_couplings=len(rows), mean_miss_tau=mean("miss_tau"), max_miss_tau=mx("miss_tau"),
                mean_raw_miss_tau=mean("raw_miss_tau"), max_raw_miss_tau=mx("raw_miss_tau"),
                mean_miss_chord_tau=mean("miss_chord_tau"), max_miss_chord_tau=mx("miss_chord_tau"),
                mean_miss_n19_truth_tau=mean("miss_n19_truth_tau"), max_miss_n19_truth_tau=mx("miss_n19_truth_tau"),
                mean_miss_ok=bool(mean("miss_tau") <= P5_MEAN_MAX[n]), mean_miss_limit=P5_MEAN_MAX[n],
                deciding_couplings=[r["Jz"] for r in dec], n_deciding=len(dec),
                ratio_range_deciding=[float(min(rat)), float(max(rat))] if rat else None,
                ratios_outside=bad, ratios_ok=bool(not bad),
                curve_beats_chord=bool(mean("miss_tau") < mean("miss_chord_tau")),
                curve_beats_raw=bool(mean("miss_tau") < mean("raw_miss_tau")),
                n_de_outside_curve=int(sum(not r["de_inside_curve"] for r in rows)))


def p5_rule(s57, s115):
    """The pass rule of the earlier blind test, on the summaries of the two sizes (each over its 50 couplings)."""
    ok = bool(s57["mean_miss_ok"] and s115["mean_miss_ok"] and s57["ratios_ok"] and s115["ratios_ok"])
    return dict(outcome="PASS" if ok else "FAIL",
                rule="mean miss <= 0.2 tau (n = 57) and <= 0.6 tau (n = 115), and every ratio in [0.75, 1.3] where the raw "
                     "miss is at least 0.2 tau",
                mean_miss_57=s57["mean_miss_tau"], mean_miss_115=s115["mean_miss_tau"],
                ratios_outside_57=s57["ratios_outside"], ratios_outside_115=s115["ratios_outside"])


# ------------------------------------------------------------------------------------------------ one size
def analyse_size(rd, C19, sets=None):
    """P1-P5 and the n = 19 comparison for one size. rd: rdc.RealData. C19: the n = 19 curves. sets: parse_sets
    output or None (then the 'kept' part of the n = 19 comparison is reported as not available)."""
    G, n = rd.G, rd.n
    Js = rd.labelled()
    neel = rdc.neel_values(G)
    out = dict(n=n, group=rd.group, couplings=Js, n_couplings=len(Js),
               orientation_all_plus=bool(all(rd.lab[J]["orientation"] > 0 and rd.truth[J]["orientation"] > 0 for J in Js)),
               truth_sources=dict(E0_project=[J for J in Js if rd.truth[J]["E0_source"] == "project"],
                                  m_s_project=[J for J in Js if rd.truth[J]["label_source"]["m_s"] == "project"]))
    # P1-P3
    P13 = {}
    for fam in rdc.FAMILIES:
        T = {J: t_values(rd.lab[J]["families"][fam], rd.truth[J]["families"][fam], neel[fam]) for J in Js}
        P13[fam] = sign_test(T)
    out["P1_P3"] = P13
    # P4 (the four families decide; m_s is reported next to them and was seen before, F7)
    P4 = {}
    for fam in rdc.FAMILIES:
        P4[fam] = p4_test({J: D_value(rd.lab[J]["families"][fam], rd.truth[J]["families"][fam]) for J in Js})
    P4["m_s"] = dict(p4_test({J: D_value([rd.lab[J]["labels"]["m_s"]], [rd.truth[J]["labels"]["m_s"]]) for J in Js}),
                     note="single label, reported next to the four families; seen before (F7)")
    out["P4"] = P4
    # P5
    rows = [p5_row(J, rd.lab[J]["labels"]["m_s"], rd.truth[J]["labels"]["m_s"], rd.lab[J]["de"], C19) for J in Js]
    out["P5"] = dict(rows=rows, all=p5_summary(rows, n),
                     training_45=p5_summary([r for r in rows if r["Jz"] >= rdc.TRAIN_MIN], n),
                     test_1p1_1p4=p5_summary([r for r in rows if r["Jz"] in rdc.TEST], n))
    # Sec. 6: the small classical calculation next to every label
    cmp_rows = [dict(Jz=r["Jz"], n19_minus_truth_tau=r["miss_n19_truth_tau"], label_miss_tau=r["raw_miss_tau"],
                     m_s_n19=r["m_s_n19"], m_gs=r["m_gs"]) for r in rows]
    c = dict(rows=cmp_rows, at_test={rdc.jkey(r["Jz"]): r["n19_minus_truth_tau"] for r in cmp_rows if r["Jz"] in rdc.TEST},
             max_all=float(max(r["n19_minus_truth_tau"] for r in cmp_rows)))
    if sets is not None:
        kept = [r for r in cmp_rows if r["Jz"] in set(sets["S"])]
        c.update(kept=sets["S"], n_kept=len(kept),
                 max_over_kept=float(max(r["n19_minus_truth_tau"] for r in kept)) if kept else None,
                 sentence_within_a_fifth_on_kept=bool(kept and max(r["n19_minus_truth_tau"] for r in kept) <= 0.2) if kept else None)
    else:
        c.update(kept=None, note="kept set not available (no sets file given)")
    out["n19_comparison"] = c
    return out
