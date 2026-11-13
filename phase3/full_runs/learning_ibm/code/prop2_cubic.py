"""Proposition 2(a)/(b) for the cubic model on the heavy-hex labels (design: ../PROP2_DESIGN.md, hashed before this
script was written). Stored outputs only: no DMRG, no diagonalization, no emulation.

  python -I prop2_cubic.py <J_next_paper root> <out dir>      -> <out dir>/prop2_cubic.json (and a summary on stdout)

Label intervals: the certification map's window of m_s at each label's own energy, from the stored chains
(outer, DMRG-referenced, valid) and the stored explicit states (inner, a sub-interval of the window), via
make_limit of map/laptop_analysis/code/analyze_map.py (imported, unchanged).
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np  # noqa: E402

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
FR = os.path.join(ROOT, "phase3", "full_runs")
MAPROOT = os.path.join(FR, "map", "laptop_analysis")
sys.path.insert(0, os.path.join(FR, "method", "code"))
sys.path.insert(0, os.path.join(MAPROOT, "code"))
import ml2  # noqa: E402
import analyze_map as AM  # noqa: E402

EMU = os.path.join(FR, "method", "out_20261030T003230Z", "out")
ALPHA = 0.1
OOD = [1.1, 1.2, 1.3, 1.4]
TRAIN_MIN = 1.6
TAU_REL = 0.06
RIDGE = 1e-8


def rj(p):
    with open(p) as f:
        return json.load(f)


def load(n):
    """As learn_ibm.load: emulated primary labels, their energy excess, DMRG truth."""
    G = rj(os.path.join(FR, "method", "code", "graphs", "hh_d%d.json" % {57: 5, 115: 7}[n]))
    eta = np.array(G["eta"], float)
    D = {}
    import glob
    for p in glob.glob(os.path.join(EMU, "emu", "emu_n%d_J*.json" % n)):
        e = rj(p); J = round(e["Jz"], 1)
        r = rj(os.path.join(EMU, "ref", "ref_n%d_J%s.json" % (n, ("%g" % J if J != int(J) else "%.1f" % J))))
        v = e["var"]
        Zl, Zr = np.array(v["primary"]["labels"]["Z"]), np.array(r["labels"]["Z"])
        D[J] = dict(eps=v["primary"]["E"] - e["E0"], E0_emu=e["E0"], y=ml2.ms(Zl, eta), ystar=ml2.ms(Zr, eta),
                    Zl=Zl)
    return eta, D


def coef(Jtr, Jq, deg=3):
    """a(Jq): the cubic's prediction at Jq is a @ labels (ml2.fit_poly, same ridge)."""
    X = np.vander(1.0 / np.asarray(Jtr, float), deg + 1)
    v = np.vander(1.0 / np.atleast_1d(float(Jq)), deg + 1)
    return (v @ np.linalg.solve(X.T @ X + RIDGE * np.eye(deg + 1), X.T))[0]


def intervals(n, D, Dmap, MR):
    """Energy interval of each m_s label at its own energy (outer and inner); None where the map has no row."""
    I = {}
    for J, d in D.items():
        thr = Dmap.thr(n, J) if (n, J, "m_s") in MR else None
        if thr is None:
            I[J] = None
            continue
        L = AM.make_limit(Dmap, n, J, "m_s", thr)
        E = thr["E0"] + d["eps"]
        olo, ohi = L["outer"](E)
        ilo, ihi = L["inner_fast"](E)
        I[J] = dict(E=E, E0_map=thr["E0"], outer=[olo, ohi], w_out=ohi - olo,
                    inner=[ilo, ihi] if ihi is not None else None, w_in=(ihi - ilo) if ihi is not None else 0.0,
                    label_in_outer=bool(olo - 1e-12 <= d["y"] <= ohi + 1e-12),
                    truth_in_outer=bool(olo - 1e-12 <= d["ystar"] <= ohi + 1e-12))
    return I


def interp_width(J, I, D):
    """Indicative width at a coupling without a map row: log-linear in Jz between the neighbouring computed rows."""
    lo = max(j for j in I if I[j] is not None and j < J)
    hi = min(j for j in I if I[j] is not None and j > J)
    t = (J - lo) / (hi - lo)
    return math.exp((1 - t) * math.log(I[lo]["w_out"]) + t * math.log(I[hi]["w_out"])), [lo, hi]


def widths(I, D, J):
    """(w_lo, w_hi, indicative?) for the label at J."""
    if I[J] is not None:
        return I[J]["w_in"], I[J]["w_out"], False
    w, _ = interp_width(J, I, D)
    return 0.0, w, True


def band(Jtr, Jq, I, D):
    a = coef(Jtr, Jq)
    wl, wh, ind = zip(*[widths(I, D, j) for j in Jtr])
    return dict(W_lo=float(np.abs(a) @ np.array(wl)), W_hi=float(np.abs(a) @ np.array(wh)), indicative=any(ind),
                a_l1=float(np.abs(a).sum()), a=[float(x) for x in a])


def q_of(scores):
    s = np.sort(np.asarray(scores)); N = len(s)
    k = int(math.ceil((1 - ALPHA) * (N + 1)))
    return (float(s[-1]), N / (N + 1)) if k > N else (float(s[k - 1]), 1 - ALPHA)


def calib(Jcal, I, D):
    """Leave-one-coupling-out certified scores on Jcal (plain jackknife, as learn_ibm.loo_calib). Returns q_lo, q_hi,
    level, indicative?, per-coupling scores."""
    slo, shi, rows, ind = [], [], [], False
    for k in Jcal:
        tr = [j for j in Jcal if j != k]
        f = float(coef(tr, k) @ np.array([D[j]["y"] for j in tr]))
        y = D[k]["y"]
        if I[k] is not None:
            lo_o, hi_o = I[k]["outer"]
            sl = max([abs(f - y)] + ([abs(f - I[k]["inner"][0]), abs(f - I[k]["inner"][1])] if I[k]["inner"] else []))
            sh = max(abs(f - lo_o), abs(f - hi_o))
        else:
            w, _ = interp_width(k, I, D)
            sl, sh, ind = abs(f - y), abs(f - y) + w, True
        slo.append(sl); shi.append(sh)
        rows.append(dict(Jz=k, pred_loo=f, label=y, s_std=abs(f - y), s_lo=sl, s_hi=sh))
    qlo, lev = q_of(slo); qhi, _ = q_of(shi)
    return qlo, qhi, lev, ind, rows


def evaluate(Jtr, Jq, I, D):
    f = float(coef(Jtr, Jq) @ np.array([D[j]["y"] for j in Jtr]))
    tau = TAU_REL * abs(D[Jq]["ystar"])
    qlo, qhi, lev, ind, crow = calib(Jtr, I, D)
    b = band(Jtr, Jq, I, D)
    out = dict(Jz=Jq, tau=tau, pred=f, truth=D[Jq]["ystar"], label=D[Jq]["y"],
               W_lo_tau=b["W_lo"] / tau, W_hi_tau=b["W_hi"] / tau, W_indicative=b["indicative"], a_l1=b["a_l1"],
               q_lo=qlo, q_hi=qhi, level=lev, q_indicative=ind,
               width_b_lo_tau=2 * qlo / tau, width_b_hi_tau=2 * qhi / tau,
               covers_truth_b_lo=bool(abs(f - D[Jq]["ystar"]) <= qlo),
               miss_over_tau=abs(f - D[Jq]["ystar"]) / tau, calib_scores=crow)
    # rule (c)
    if (not ind) and 2 * qhi <= tau:
        out["rule_c"] = "ANSWER"
    elif 2 * qlo > tau:
        out["rule_c"] = "ABSTAIN"
    else:
        out["rule_c"] = "ABSTAIN_DEFAULT"
    if (not b["indicative"]) and b["W_hi"] <= tau:
        out["band_a"] = "PINNED"
    elif b["W_lo"] > tau:
        out["band_a"] = "NOT_PINNED"
    else:
        out["band_a"] = "UNDECIDED"
    return out


def label_filter_interp(n, D, MR):
    """Label filter with eps_tau_out interpolated log-linearly in Jz where the map has no row (as for J*)."""
    rows = {J: MR[(n, J, "m_s")] for J in D if (n, J, "m_s") in MR}
    res = {}
    for J in sorted(D):
        if J in rows:
            continue
        lo = max(j for j in rows if j < J); hi = min(j for j in rows if j > J)
        t = (J - lo) / (hi - lo)
        et = math.exp((1 - t) * math.log(rows[lo]["eps_tau_out"]) + t * math.log(rows[hi]["eps_tau_out"]))
        res[str(J)] = dict(eps_emu=D[J]["eps"], eps_tau_out_interp=et, neighbours=[lo, hi],
                           certified_interp=bool(D[J]["eps"] <= et))
    return res


def main():
    Dmap = AM.Data(MAPROOT)
    M = rj(os.path.join(MAPROOT, "summary_map.json"))
    MR = {(r["n"], round(r["Jz"], 1), r["label"]): r for r in M["rows"]}
    res = dict(design="PROP2_DESIGN.md", alpha=ALPHA, ridge=RIDGE, tau_rel=TAU_REL, sizes={})
    for n in (57, 115):
        eta, D = load(n)
        Js = sorted(D)
        R = [j for j in Js if j >= TRAIN_MIN]
        od = [j for j in Js if j in OOD]
        I = intervals(n, D, Dmap, MR)
        # check: a(x) @ m_s labels reproduces m_s of ml2.fit_poly's per-site predictions
        fpoly = ml2.fit_poly(R, np.array([D[j]["Zl"] for j in R]))
        lin_check = max(abs(float(coef(R, t) @ np.array([D[j]["y"] for j in R])) - ml2.ms(fpoly(t)[0], eta)) for t in Js)
        S = dict(couplings=Js, train=R, ood=od, linearity_check_max_abs=lin_check,
                 intervals={str(J): (dict(I[J], w_out_tau=I[J]["w_out"] / (TAU_REL * abs(D[J]["ystar"])),
                                          w_in_tau=I[J]["w_in"] / (TAU_REL * abs(D[J]["ystar"]))) if I[J] else None)
                            for J in Js},
                 missing_rows=[J for J in Js if I[J] is None])
        S["interp_widths"] = {str(J): dict(zip(("w", "neighbours"), interp_width(J, I, D))) for J in Js if I[J] is None}
        S["indist"] = [evaluate([j for j in R if j != t], t, I, D) for t in R]
        S["ood"] = [evaluate(R, t, I, D) for t in od]
        S["in_sample_all_R"] = [dict(Jz=t, **{k: v for k, v in band(R, t, I, D).items() if k != "a"},
                                     tau=TAU_REL * abs(D[t]["ystar"])) for t in R]
        for r in S["in_sample_all_R"]:
            r["W_lo_tau"], r["W_hi_tau"] = r["W_lo"] / r["tau"], r["W_hi"] / r["tau"]
        rows = S["indist"] + S["ood"]
        S["summary"] = dict(
            answered_rule_c=[r["Jz"] for r in rows if r["rule_c"] == "ANSWER"],
            n_answered_rule_c=sum(r["rule_c"] == "ANSWER" for r in rows), n_queries=len(rows),
            abstain_definite=[r["Jz"] for r in rows if r["rule_c"] == "ABSTAIN"],
            abstain_default=[r["Jz"] for r in rows if r["rule_c"] == "ABSTAIN_DEFAULT"],
            pinned_a=[r["Jz"] for r in rows if r["band_a"] == "PINNED"],
            not_pinned_a=[r["Jz"] for r in rows if r["band_a"] == "NOT_PINNED"],
            width_b_lo_tau_indist=[min(r["width_b_lo_tau"] for r in S["indist"]), max(r["width_b_lo_tau"] for r in S["indist"])],
            width_b_lo_tau_ood=[min(r["width_b_lo_tau"] for r in S["ood"]), max(r["width_b_lo_tau"] for r in S["ood"])],
            width_b_hi_tau_ood=[min(r["width_b_hi_tau"] for r in S["ood"]), max(r["width_b_hi_tau"] for r in S["ood"])],
            W_lo_tau_indist=[min(r["W_lo_tau"] for r in S["indist"]), max(r["W_lo_tau"] for r in S["indist"])],
            W_lo_tau_ood=[min(r["W_lo_tau"] for r in S["ood"]), max(r["W_lo_tau"] for r in S["ood"])],
            W_hi_tau_ood=[min(r["W_hi_tau"] for r in S["ood"]), max(r["W_hi_tau"] for r in S["ood"])],
            truth_covered_b_lo_indist=sum(r["covers_truth_b_lo"] for r in S["indist"]),
            truth_covered_b_lo_ood=sum(r["covers_truth_b_lo"] for r in S["ood"]),
            sanity_label_in_outer=all(v["label_in_outer"] for v in I.values() if v),
            sanity_truth_in_outer=all(v["truth_in_outer"] for v in I.values() if v))
        S["label_filter_interp"] = label_filter_interp(n, D, MR)
        res["sizes"][str(n)] = S
        print("n=%d  rule (c) with Prop. 2(b) intervals answers %d of %d queries %s" % (
            n, S["summary"]["n_answered_rule_c"], len(rows), S["summary"]["answered_rule_c"]))
        print("  %-5s %-7s %8s %8s %8s %8s %8s  %s / %s" % ("Jz", "range", "W_lo", "W_hi", "2q_lo", "2q_hi", "miss",
                                                             "rule(c)", "band(a)"))
        for r in rows:
            print("  %-5.1f %-7s %8.2f %8.2f %8.2f %8.2f %8.2f  %s / %s%s" % (
                r["Jz"], "test" if r["Jz"] in OOD else "train", r["W_lo_tau"], r["W_hi_tau"], r["width_b_lo_tau"],
                r["width_b_hi_tau"], r["miss_over_tau"], r["rule_c"], r["band_a"],
                "  (indicative upper)" if (r["W_indicative"] or r["q_indicative"]) else ""))
        print("  in sample (cubic on all of R): " + ", ".join("%.1f: %.2f-%.2f" % (r["Jz"], r["W_lo_tau"], r["W_hi_tau"])
                                                         for r in S["in_sample_all_R"]))
        print("  label filter, interpolated threshold where no map row:", S["label_filter_interp"])
        print("  sanity: label in outer %s, truth in outer %s" % (S["summary"]["sanity_label_in_outer"],
                                                                 S["summary"]["sanity_truth_in_outer"]))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "prop2_cubic.json"), "w") as fo:
        json.dump(res, fo, indent=1, default=float)


if __name__ == "__main__":
    main()
