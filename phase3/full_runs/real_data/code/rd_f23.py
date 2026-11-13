# real_data / rd_f23.py  (own code; 2026-11-12; task rd-code-learn)
#
# DECLARATION.md Sec. 7: (f2) the learner-independent floor, (f3) the constructive test on labels certified at their
# own energy, and the three statements L1-L3 of (f1) read from the outputs of the derived scripts. Pure functions on
# dictionaries {Jz: number}; nothing here opens a data file.
#
# (f2)  for any learner and the constant-width score, 2q >= w_(k), the k-th narrowest calibration interval,
#       k = ceil((m+1)(1-alpha)); computed with the LOWER widths ((1 - q) x hull of explicit states).
# (f3)  200 seeded splits of a nested set T (6 training / 12 calibration couplings if |T| >= 20; 4 / 9 if
#       15 <= |T| < 20; not run below 15); models M1 (line in 1/Jz), M2 (1 - a/Jz^2 - b/Jz^4), control M0 (cubic in
#       1/Jz, ridge 1e-8, trained on every training label outside the calibration and query couplings of the split);
#       score s_j = max(|f(x_j) - lo_j|, |f(x_j) - hi_j|), q = the ceil((m+1)(1-alpha))-th smallest, interval
#       f(x) +- q; Proposition 2(a) W(x) = sum_j |a_j(x)| width(I_j);
#       (W) in at least 90 % of the splits 2q <= tau(x) at every query; (C) the truth within q of the prediction in at
#       least 90 % of all (split, query) pairs.  PASS iff (W) and (C) for both M1 and M2 (n = 57, set S_p).
#       Secondary, same splits: width-normalized scores.
import math

import numpy as np

import rd_common as rdc

RIDGE = 1e-8
N_SPLITS = 200
PASS_FRAC = 0.9
SET_CODE = {"S": 0, "S_3_4": 1, "S_1_2": 2}
MODELS = ("M1", "M2", "M0")


def kth_smallest(values, alpha=rdc.ALPHA):
    """(value, k, level): the ceil((m+1)(1-alpha))-th smallest; if that index exceeds m, the largest value and the
    attainable level m/(m+1), as learning_ibm/code/learn_ibm.py:qconf."""
    s = np.sort(np.asarray(values, float)); m = len(s); k = rdc.k_index(m, alpha)
    if k > m:
        return float(s[-1]), k, m / (m + 1)
    return float(s[k - 1]), k, 1 - alpha


# ------------------------------------------------------------------------------------------------ (f2)
def floor_f2(lower_width, tau, train=None, alpha=rdc.ALPHA):
    """lower_width: {Jz: lower width of the label's energy interval} for the calibration (training) couplings;
    tau: {Jz: 0.06 |m_s^truth|} at every coupling to be reported. Returns the floor and its value in tau(x)."""
    train = sorted(train if train is not None else [J for J in rdc.TRAIN_J if J in lower_width])
    w = [lower_width[J] for J in train]
    floor, k, level = kth_smallest(w, alpha)
    out = dict(m=len(train), k=k, level=level, floor=floor, widths_sorted=[float(x) for x in np.sort(w)],
               statement="for any learner and the constant-width score, 2q >= w_(k)",
               floor_over_tau={rdc.jkey(J): floor / tau[J] for J in sorted(tau)})
    loo = {}
    for J in train:                                     # in distribution: the query's own label is held out
        f1, k1, _ = kth_smallest([lower_width[j] for j in train if j != J], alpha)
        loo[rdc.jkey(J)] = dict(floor=f1, k=k1, m=len(train) - 1, floor_over_tau=f1 / tau[J])
    out["in_distribution_held_out"] = loo
    tq = [J for J in rdc.TEST if J in tau]
    out["holds_at_test_queries"] = bool(tq and all(floor > tau[J] for J in tq))
    out["holds_at_every_coupling"] = bool(all(floor > tau[J] for J in tau))
    out["holds_in_distribution_held_out"] = bool(all(v["floor"] > tau[float(k_)] for k_, v in loo.items()))
    out["holds"] = out["holds_at_test_queries"]
    out["readings_agree"] = bool(out["holds_at_test_queries"] == out["holds_at_every_coupling"] == out["holds_in_distribution_held_out"])
    out["rule"] = ("holds iff the floor w_(k) of the m = %d calibration labels (k = %d) exceeds tau(x) at each of the four test "
                   "queries; reported next to it: the same floor against tau(x) at every coupling, and the held-out floors "
                   "(m = %d) at every training coupling" % (len(train), k, len(train) - 1))
    return out


# ------------------------------------------------------------------------------------------------ (f3) models
def coef(model, xtr, xq):
    """(a, c): the prediction at xq is c + a @ labels(xtr). M1: least-squares line in 1/Jz. M2: least squares of
    1 - y on (1/Jz^2, 1/Jz^4). M0: ml2.fit_poly (cubic in 1/Jz, ridge 1e-8), in the coefficient form of prop2_cubic."""
    xtr = np.asarray(xtr, float); xq = float(xq)
    if model == "M1":
        a = np.array([1.0, 1 / xq]) @ np.linalg.pinv(np.column_stack([np.ones(len(xtr)), 1 / xtr]))
        return a, 0.0
    if model == "M2":
        a = np.array([1 / xq ** 2, 1 / xq ** 4]) @ np.linalg.pinv(np.column_stack([1 / xtr ** 2, 1 / xtr ** 4]))
        return a, 1.0 - float(a.sum())
    if model == "M0":
        X = np.vander(1.0 / xtr, 4); v = np.vander(1.0 / np.atleast_1d(xq), 4)
        return (v @ np.linalg.solve(X.T @ X + RIDGE * np.eye(4), X.T))[0], 0.0
    raise ValueError(model)


def make_splits(T, seed0, n, set_name, n_splits=N_SPLITS):
    """The seeded splits of the set T: numpy default_rng([seed0, n, code of the set]); each split is one permutation
    of the sorted set: first the training couplings, then the calibration couplings, the rest are queries."""
    T = sorted(T); sz = rdc.split_sizes(len(T))
    if sz is None:
        return None
    ntr, ncal = sz
    rng = np.random.default_rng([int(seed0), int(n), SET_CODE[set_name]])
    out = []
    for _ in range(n_splits):
        p = rng.permutation(len(T))
        out.append((sorted(T[i] for i in p[:ntr]), sorted(T[i] for i in p[ntr:ntr + ncal]), sorted(T[i] for i in p[ntr + ncal:])))
    return out


def sigma_loglinear(x, pts):
    """Log-linear interpolation in Jz through the points pts = [(Jz, width > 0)]; beyond the ends, the line through
    the two nearest points (as scratch/math-learning/normalized_b.py)."""
    pts = sorted(pts)
    for j, w in pts:
        if j == x:
            return w
    lo = [p for p in pts if p[0] < x]; hi = [p for p in pts if p[0] > x]
    if lo and hi:
        a, b = lo[-1], hi[0]
    elif hi:
        a, b = hi[0], hi[1]
    else:
        a, b = lo[-2], lo[-1]
    t = (x - a[0]) / (b[0] - a[0])
    return math.exp((1 - t) * math.log(a[1]) + t * math.log(b[1]))


def eval_split(model, tr, cal, qs, d, alpha=rdc.ALPHA):
    """One split, one model. d: dict(y, ystar, tau, exact={Jz: (lo, hi)}, lower_w={Jz: width}, train_all=[...])."""
    y, ystar, tau, exact = d["y"], d["ystar"], d["tau"], d["exact"]
    xtr = sorted(set(d["train_all"]) - set(cal) - set(qs)) if model == "M0" else list(tr)
    ytr = np.array([y[j] for j in xtr])
    f = {}
    for x in list(cal) + list(qs):
        a, c = coef(model, xtr, x)
        f[x] = (c + float(a @ ytr), a)
    s = [max(abs(f[j][0] - exact[j][0]), abs(f[j][0] - exact[j][1])) for j in cal]
    q, k, level = kth_smallest(s, alpha)
    wcal = [exact[j][1] - exact[j][0] for j in cal]
    wk = kth_smallest(wcal, alpha)[0]
    rows = []
    for x in qs:
        a = f[x][1]
        W_hi = float(np.abs(a) @ np.array([exact[j][1] - exact[j][0] for j in xtr])) if all(j in exact for j in xtr) else None
        W_lo = float(np.abs(a) @ np.array([d["lower_w"].get(j, 0.0) for j in xtr]))
        rows.append(dict(Jz=x, pred=f[x][0], truth=ystar[x], tau=tau[x], width_tau=2 * q / tau[x], ok_W=bool(2 * q <= tau[x]),
                         covered=bool(abs(ystar[x] - f[x][0]) <= q), miss_tau=abs(f[x][0] - ystar[x]) / tau[x],
                         W_a_exact_tau=(W_hi / tau[x]) if W_hi is not None else None, W_a_lower_tau=W_lo / tau[x],
                         a_l1=float(np.abs(a).sum())))
    out = dict(q=q, k=k, level=level, floor_w_k=wk, floor_ok=bool(2 * q >= wk - 1e-12), n_train=len(xtr), rows=rows,
               all_ok_W=bool(all(r["ok_W"] for r in rows)))
    # secondary, same split: width-normalized scores (no rule)
    if min(wcal) > 0:
        pts = [(j, w) for j, w in zip(cal, wcal)]
        s_lit = [abs(f[j][0] - y[j]) / w for j, w in pts]                       # literal: |f - y| / sigma, sigma(x_j) = w_j
        q_lit = kth_smallest(s_lit, alpha)[0]
        s_iv = [max(abs(f[j][0] - exact[j][0]), abs(f[j][0] - exact[j][1])) / sigma_loglinear(j, [p for p in pts if p[0] != j])
                for j in cal]                                                   # worst case over I_j, sigma without label j
        q_iv = kth_smallest(s_iv, alpha)[0]
        for r in rows:
            sg = sigma_loglinear(r["Jz"], pts)
            r.update(sigma_tau=sg / r["tau"], norm_literal_width_tau=2 * q_lit * sg / r["tau"],
                     norm_literal_covered=bool(abs(r["truth"] - r["pred"]) <= q_lit * sg),
                     norm_interval_width_tau=2 * q_iv * sg / r["tau"],
                     norm_interval_covered=bool(abs(r["truth"] - r["pred"]) <= q_iv * sg))
        out.update(q_norm_literal=q_lit, q_norm_interval=q_iv)
    return out


def aggregate(per_split):
    """(W), (C) and summary numbers of one model over the splits."""
    rows = [r for s in per_split for r in s["rows"]]
    wt = np.array([r["width_tau"] for r in rows])
    frac_W = float(np.mean([s["all_ok_W"] for s in per_split]))
    frac_C = float(np.mean([r["covered"] for r in rows]))
    out = dict(n_splits=len(per_split), n_pairs=len(rows), frac_splits_W=frac_W, frac_pairs_C=frac_C,
               W_holds=bool(frac_W >= PASS_FRAC), C_holds=bool(frac_C >= PASS_FRAC),
               width_tau_min=float(wt.min()), width_tau_median=float(np.median(wt)), width_tau_max=float(wt.max()),
               frac_pairs_width_le_tau=float(np.mean([r["ok_W"] for r in rows])),
               largest_miss_tau=float(max(r["miss_tau"] for r in rows)),
               floor_violations=int(sum(not s["floor_ok"] for s in per_split)),
               two_q_over_floor_min=float(min(2 * s["q"] / s["floor_w_k"] for s in per_split if s["floor_w_k"] > 0)) if any(s["floor_w_k"] > 0 for s in per_split) else None,
               W_a_lower_tau_max=float(max(r["W_a_lower_tau"] for r in rows)))
    ex = [r["W_a_exact_tau"] for r in rows if r["W_a_exact_tau"] is not None]
    out["W_a_exact_tau_range"] = [float(min(ex)), float(max(ex))] if ex else None
    out["W_a_exact_available_pairs"] = len(ex)
    for key in ("norm_literal", "norm_interval"):
        if rows and (key + "_width_tau") in rows[0]:
            w = np.array([r[key + "_width_tau"] for r in rows])
            by = {}
            for s in per_split:
                by.setdefault(0, []).append(all(r[key + "_width_tau"] <= 1 for r in s["rows"]))
            out[key] = dict(width_tau_min=float(w.min()), width_tau_median=float(np.median(w)), width_tau_max=float(w.max()),
                            frac_splits_all_widths_le_tau=float(np.mean(by[0])),
                            frac_pairs_covered=float(np.mean([r[key + "_covered"] for r in rows])))
    return out


def run_set(n, set_name, T, d, seed0, n_splits=N_SPLITS, keep_splits=True):
    """The constructive test on one nested set. Returns dict(status, models={M1, M2, M0}, outcome for M1 and M2)."""
    T = sorted(T)
    sp = make_splits(T, seed0, n, set_name, n_splits)
    if sp is None:
        return dict(set=set_name, n=n, size=len(T), status="NOT RUN (fewer than 15 couplings)")
    missing = [J for J in T if J not in d["exact"]]
    if missing:
        raise ValueError("no exact interval at %s" % missing)
    inside = dict(label=[J for J in T if not (d["exact"][J][0] - 1e-12 <= d["y"][J] <= d["exact"][J][1] + 1e-12)],
                  truth=[J for J in T if not (d["exact"][J][0] - 1e-12 <= d["ystar"][J] <= d["exact"][J][1] + 1e-12)])
    res = dict(set=set_name, n=n, size=len(T), couplings=T, n_train=len(sp[0][0]), n_cal=len(sp[0][1]), n_query=len(sp[0][2]),
               k=rdc.k_index(len(sp[0][1])), status="RUN", models={},
               gate_G7_outside_interval=inside, seed_entropy=[int(seed0), int(n), SET_CODE[set_name]])
    for model in MODELS:
        per = [eval_split(model, tr, cal, qs, d) for tr, cal, qs in sp]
        res["models"][model] = aggregate(per)
        if keep_splits:
            res["models"][model]["splits"] = [dict(q=s["q"], all_ok_W=s["all_ok_W"], floor_w_k=s["floor_w_k"],
                                                   widths_tau=[r["width_tau"] for r in s["rows"]],
                                                   covered=[r["covered"] for r in s["rows"]]) for s in per]
    if keep_splits:
        res["splits"] = [dict(train=tr, cal=cal, query=qs) for tr, cal, qs in sp]
    ok = all(res["models"][m]["W_holds"] and res["models"][m]["C_holds"] for m in ("M1", "M2"))
    res["outcome_M1_M2"] = "PASS" if ok else "FAIL"
    res["outcome_M0_control"] = "PASS" if (res["models"]["M0"]["W_holds"] and res["models"]["M0"]["C_holds"]) else "FAIL"
    return res


def run_f3(n, sets, d, seed0, n_splits=N_SPLITS, keep_splits=True):
    """All nested sets of one size, and the decision on the primary set S_p."""
    out = dict(n=n, S_p_name=sets["S_p_name"], sizes={k: len(sets[k]) for k in ("S", "S_3_4", "S_1_2")}, sets={})
    for name in ("S", "S_3_4", "S_1_2"):
        out["sets"][name] = run_set(n, name, sets[name], d, seed0, n_splits, keep_splits)
    if sets["S_p_name"] is None:
        out["primary"] = dict(outcome="NOT RUN", reason="S has fewer than 15 couplings")
    else:
        r = out["sets"][sets["S_p_name"]]
        out["primary"] = dict(set=sets["S_p_name"], outcome=r["outcome_M1_M2"],
                              rule="(W) 2q <= tau(x) at every query in at least 90 % of the splits and (C) the truth within "
                                   "q of the prediction in at least 90 % of all (split, query) pairs, for both M1 and M2",
                              M1=dict(W=r["models"]["M1"]["frac_splits_W"], C=r["models"]["M1"]["frac_pairs_C"]),
                              M2=dict(W=r["models"]["M2"]["frac_splits_W"], C=r["models"]["M2"]["frac_pairs_C"]))
    return out


# ------------------------------------------------------------------------------------------------ (f1) L1-L3
def f1_rules(results, prop2, n, src="emulated"):
    """L1-L3 of Sec. 7 (f1) from the outputs of rd_learn_ibm.py (results) and rd_prop2_cubic.py (prop2) for size n.
    In those files the key 'emulated' denotes the labels of the chosen data source (the real labels in a real run)."""
    rows = results["sizes"][str(n)]["models"]["poly3_invJ"]["ood_" + src]["rows"]
    rows = [r for r in rows if round(r["Jz"], 1) in rdc.TEST]
    L1 = dict(miss_tau={rdc.jkey(r["Jz"]): r["miss_ms_over_tau"] for r in rows},
              holds=bool(len(rows) == 4 and all(r["miss_ms_over_tau"] > 1 for r in rows)),
              statement="the cubic misses the true m_s by more than tau at each of 1.1-1.4")
    L2 = dict(covered={rdc.jkey(r["Jz"]): bool(r["covM_truth"]) for r in rows},
              site_coverage={rdc.jkey(r["Jz"]): r["covZ_truth"] for r in rows},
              holds=bool(len(rows) == 4 and not any(r["covM_truth"] for r in rows)),
              statement="standard intervals calibrated on the labels cover the true m_s at none of the four test couplings")
    P = prop2["sizes"][str(n)]
    qs = sorted(set(r["q_lo"] for r in P["ood"]))
    taus = {round(r["Jz"], 1): r["tau"] for r in P["indist"] + P["ood"]}
    q_lo = qs[-1] if qs else None
    L3 = dict(q_lo_all_training_labels=q_lo, one_value=bool(len(qs) == 1), n_couplings=len(taus),
              width_tau={rdc.jkey(J): 2 * q_lo / t for J, t in sorted(taus.items())} if qs else None,
              holds=bool(len(qs) == 1 and all(2 * q_lo > t for t in taus.values())),
              held_out_width_tau_range=[min(r["width_b_lo_tau"] for r in P["indist"]), max(r["width_b_lo_tau"] for r in P["indist"])],
              statement="the intervals of 2(b) calibrated on all training labels are wider than tau at every coupling (lower version)")
    return dict(n=n, L1=L1, L2=L2, L3=L3)
