# real_data / checks / rd_learn_independent.py   (own code; task rd-learn; 2026-11-12; written AFTER the hash)
#
# Independent recomputation of the cheap learning numbers of DECLARATION.md Sec. 7 and a few POST HOC lines.
# It decides nothing: the declared outcomes are those of the sealed code (code/run_learn.py). It imports no sealed
# file and no stored script; it reads converted/*.json (plain JSON) only after checking the declaration hash and the
# pinned hashes of the files, and out/S_sets.json only after checking its recorded SHA-256.
#
#   python -B -I checks/rd_learn_independent.py        -> out/learn/independent_check.json, summary on stdout
#
# What is recomputed with other formulas than the sealed code (least squares by numpy.linalg.lstsq on an augmented
# system instead of the normal equations; m_s fitted directly instead of site by site):
#   f1   cubic in 1/Jz and nearest-neighbour null on m_s: test range and in distribution, real labels and DMRG control
#   f1   Proposition 2 for the cubic: W_lo (2(a), lower version) and q_lo (2(b), lower version, all 45 labels)
#   f2   the floor w_(42)
#   f3   every nested set that was run, M1, M2, M0: (W), (C), widths, largest miss   (the splits are regenerated with
#        the declared generator call and compared with the stored ones)
#   in   the intervals of out/S_sets.json against the m_s rows of out/map_real.json
# POST HOC (not declared; they decide nothing):
#   ph1  on the splits of (f3): the standard score |f - y| instead of the interval score (width, coverage of the truth)
#   ph2  on the splits of (f3): a constant model (mean of the training labels) with the interval score
#   ph3  the change of the true m_s over each nested set, in units of tau
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)
WORK = os.path.dirname(os.path.dirname(os.path.dirname(RD)))
OUT = os.path.join(RD, "out", "learn")
PIN = {"real_n57.json": "ec96cd6d49a160ba91b38a08f987d221aa01c465c470e0eb17c13f9bacedc4dd",
       "real_n115.json": "5890160c5ff0992b0859ce44fba3a74d1aff6fa6e005f8ef0d0db4f4233d0002"}
TEST = [1.1, 1.2, 1.3, 1.4]
ALPHA = Fraction(1, 10)
RIDGE = 1e-8
SET_CODE = {"S": 0, "S_3_4": 1, "S_1_2": 2}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def token(p):
    with open(p, encoding="utf-8") as f:
        return f.read().split()[0].lower()


def kidx(m):
    return int(math.ceil(Fraction(m + 1) * (1 - ALPHA)))


def kth(vals):
    s = sorted(float(v) for v in vals); m = len(s); k = kidx(m)
    return s[-1] if k > m else s[k - 1]


def load(n):
    o = rj(os.path.join(RD, "converted", "real_n%d.json" % n))
    G = rj(os.path.join(WORK, "phase3", "full_runs", "method", "code", "graphs", "hh_d%d.json" % {57: 5, 115: 7}[n]))
    eta = np.array(G["eta"], float)
    assert len(eta) == n
    y = {round(float(k), 1): float(np.dot(np.array(e["z_basis_opt"], float), eta) / n)
         for k, e in o["skqd_random_flip"].items() if "z_basis_opt" in e}
    t = {round(float(k), 1): float(np.dot(np.array(e["z"], float), eta) / n) for k, e in o["dmrg"].items()}
    return y, t


# ---------------------------------------------------------------------------------------------- models (own formulas)
def cubic(xtr, ytr):
    """Cubic in 1/Jz with ridge 1e-8 on the four coefficients, by least squares on the augmented system."""
    u = 1.0 / np.asarray(xtr, float)
    X = np.column_stack([np.ones_like(u), u, u ** 2, u ** 3])
    A = np.vstack([X, math.sqrt(RIDGE) * np.eye(4)])
    b = np.concatenate([np.asarray(ytr, float), np.zeros(4)])
    c = np.linalg.lstsq(A, b, rcond=None)[0]
    return lambda q: float(c[0] + c[1] / q + c[2] / q ** 2 + c[3] / q ** 3)


def nearest(xtr, ytr):
    J = np.asarray(xtr, float); Y = list(ytr)
    return lambda q: float(Y[int(np.argmin(np.abs(J - q)))])


def line(xtr, ytr):
    u = 1.0 / np.asarray(xtr, float)
    c = np.linalg.lstsq(np.column_stack([np.ones_like(u), u]), np.asarray(ytr, float), rcond=None)[0]
    return lambda q: float(c[0] + c[1] / q)


def even(xtr, ytr):
    u = 1.0 / np.asarray(xtr, float)
    c = np.linalg.lstsq(np.column_stack([u ** 2, u ** 4]), 1.0 - np.asarray(ytr, float), rcond=None)[0]
    return lambda q: float(1.0 - c[0] / q ** 2 - c[1] / q ** 4)


def const(xtr, ytr):
    m = float(np.mean(ytr))
    return lambda q: m


# ---------------------------------------------------------------------------------------------- f1
def f1(model, R, lab, truth, y_real):
    """Standard conformal (plain jackknife over couplings) for one model on the labels 'lab'."""
    def run(train, tests):
        f = model(train, [lab[j] for j in train])
        res = [abs(model([j for j in train if j != k], [lab[j] for j in train if j != k])(k) - lab[k]) for k in train]
        q = kth(res)
        rows = []
        for t in tests:
            tau = 0.06 * abs(truth[t]); p = f(t)
            rows.append(dict(Jz=t, pred=p, q=q, miss_tau=abs(p - truth[t]) / tau, width_tau=2 * q / tau,
                             cov_truth=bool(abs(p - truth[t]) <= q), cov_label=bool(abs(p - y_real[t]) <= q)))
        return rows
    ood = run(R, TEST)
    ind = [run([j for j in R if j != t], [t])[0] for t in R]
    return ood, ind


def summ(rows):
    return dict(n=len(rows), cov_truth=sum(r["cov_truth"] for r in rows), cov_label=sum(r["cov_label"] for r in rows),
                miss_tau=[min(r["miss_tau"] for r in rows), max(r["miss_tau"] for r in rows)],
                width_tau=[min(r["width_tau"] for r in rows), max(r["width_tau"] for r in rows)])


def main():
    decl = sha(os.path.join(RD, "DECLARATION.md"))
    if decl != token(os.path.join(RD, "DECLARATION.sha256")):
        raise SystemExit("REFUSED: the declaration hash does not match")
    for name, h in PIN.items():
        if sha(os.path.join(RD, "converted", name)) != h:
            raise SystemExit("REFUSED: %s does not have the pinned SHA-256" % name)
    sp = os.path.join(RD, "out", "S_sets.json")
    if sha(sp) != token(os.path.join(RD, "out", "S_sets.sha256")):
        raise SystemExit("REFUSED: S_sets.json does not match its recorded SHA-256")
    seed = int(decl[:8], 16)
    SETS = rj(sp)
    sealed = dict(res=rj(os.path.join(OUT, "results_cheap.json")), f2=rj(os.path.join(OUT, "f2_floor.json")),
                  f3=rj(os.path.join(OUT, "f3_constructive.json")), rules=rj(os.path.join(OUT, "f1_rules.json")),
                  prop2=rj(os.path.join(OUT, "prop2_cubic.json")))
    MAP = rj(os.path.join(RD, "out", "map_real.json"))
    out = dict(what="independent recomputation and post hoc lines of the task rd-learn; decides nothing",
               declaration_sha256=decl, sets_sha256=sha(sp), seed=seed, numpy=np.__version__, sizes={})
    worst = {}

    def cmp(tag, a, b):
        d = abs(float(a) - float(b)); worst[tag] = max(worst.get(tag, 0.0), d)

    for n in (57, 115):
        y, t = load(n)
        Js = sorted(y); R = [j for j in Js if j >= 1.6]
        assert len(Js) == 50 and len(R) == 45
        tau = {j: 0.06 * abs(t[j]) for j in Js}
        S = SETS["sizes"][str(n)]; iv = {round(float(k), 1): v for k, v in S["intervals"].items()}
        o = dict(n=n)
        # ---- inputs: intervals of S_sets.json against the m_s rows of map_real.json
        rows = {round(r["Jz"], 1): r for r in MAP["rows"] if r["n"] == n and r["label"] == "m_s"}
        dmax, n_ex, n_lo, memb = 0.0, 0, 0, True
        for j in Js:
            r, v = rows[j], iv[j]
            if (r["exact"] is None or r["exact"].get("interval") is None) != (v["exact"] is None):
                dmax = float("inf")
            elif v["exact"] is not None:
                n_ex += 1
                dmax = max(dmax, abs(r["exact"]["interval"][0] - v["exact"]["lo"]), abs(r["exact"]["interval"][1] - v["exact"]["hi"]))
            wi = (r.get("explicit") or {}).get("witness_interval")
            if (wi is None) != (v["lower"] is None):
                dmax = float("inf")
            elif wi is not None:
                n_lo += 1
                dmax = max(dmax, abs(wi[0] - v["lower"]["lo"]), abs(wi[1] - v["lower"]["hi"]))
            dmax = max(dmax, abs(y[j] - r["label_real"]))
            if j in R:
                memb = memb and (bool(r["status"]["certified_exact"]) == (j in [round(x, 1) for x in S["S"]]))
        o["inputs"] = dict(max_abs_diff_intervals_and_labels_vs_map_real=dmax, exact_intervals=n_ex, lower_intervals=n_lo,
                           S_equals_certified_exact_rows_of_map_real=memb)
        # ---- f1: cubic and nearest neighbour, real labels and DMRG control
        o["f1"] = {}
        for mname, model, key in (("cubic", cubic, "poly3_invJ"), ("nearest", nearest, "null_nn")):
            for src, lab, skey in (("real", y, "emulated"), ("dmrg_control", t, "exact_control")):
                ood, ind = f1(model, R, lab, t, y)
                o["f1"]["%s_%s" % (mname, src)] = dict(test=summ(ood), in_distribution=summ(ind), test_rows=ood)
                M = sealed["res"]["sizes"][str(n)]["models"][key]
                for mine, theirs in ((ood, M["ood_" + skey]["rows"]), (ind, M["indist_" + skey]["rows"])):
                    assert len(mine) == len(theirs)
                    for a, b in zip(mine, theirs):
                        assert abs(a["Jz"] - b["Jz"]) < 1e-9
                        cmp("f1 %s pred" % mname, a["pred"], b["m_s_pred"]); cmp("f1 %s q" % mname, a["q"], b["qM"])
                        cmp("f1 %s miss/tau" % mname, a["miss_tau"], b["miss_ms_over_tau"])
                        cmp("f1 %s cov_truth flags" % mname, a["cov_truth"], b["covM_truth"])
                        cmp("f1 %s cov_label flags" % mname, a["cov_label"], b["covM_emu"])
        # ---- Proposition 2 for the cubic, lower version
        wlo = {j: (iv[j]["lower"]["hi"] - iv[j]["lower"]["lo"]) if iv[j]["lower"] is not None else 0.0 for j in Js}
        s_lo = []
        for k in R:
            tr = [j for j in R if j != k]; f = cubic(tr, [y[j] for j in tr])(k)
            c = [abs(f - y[k])] + ([abs(f - iv[k]["lower"]["lo"]), abs(f - iv[k]["lower"]["hi"])] if iv[k]["lower"] is not None else [])
            s_lo.append(max(c))
        q_lo = kth(s_lo)
        cmp("prop2 q_lo (all 45 labels)", q_lo, sealed["rules"]["sizes"][str(n)]["L3"]["q_lo_all_training_labels"])
        W = {}
        for x in TEST:
            a = np.array([cubic(R, list(np.eye(len(R))[i]))(x) for i in range(len(R))])      # linear in the labels
            W[x] = float(np.abs(a) @ np.array([wlo[j] for j in R])) / tau[x]
            sr = [r for r in sealed["prop2"]["sizes"][str(n)]["ood"] if abs(r["Jz"] - x) < 1e-9][0]
            cmp("prop2 W_lo/tau (relative)", W[x] / sr["W_lo_tau"], 1.0)
        o["prop2_lower"] = dict(q_lo=q_lo, width_2b_lo_tau={("%.1f" % j): 2 * q_lo / tau[j] for j in Js if j != 1.5},
                                W_lo_tau_test={("%.1f" % x): W[x] for x in TEST})
        # ---- f2
        floor = kth([wlo[j] for j in R])
        cmp("f2 floor", floor, sealed["f2"]["sizes"][str(n)]["floor"])
        o["f2"] = dict(k=kidx(len(R)), m=len(R), floor=floor, floor_over_tau={("%.1f" % j): floor / tau[j] for j in Js},
                       couplings_of_the_four_widest=[("%.1f" % j) for j in sorted(R, key=lambda j: -wlo[j])[:4]])
        # ---- f3 and post hoc lines on the same splits
        o["f3"] = {}
        ex = {j: (iv[j]["exact"]["lo"], iv[j]["exact"]["hi"]) for j in Js if iv[j]["exact"] is not None}
        for name in ("S", "S_3_4", "S_1_2"):
            T = sorted(round(float(x), 1) for x in S[name])
            sset = sealed["f3"]["sizes"][str(n)]["sets"][name]
            chg = (max(t[j] for j in T) - min(t[j] for j in T)) if T else None
            rec = dict(size=len(T), range=[T[0], T[-1]] if T else None,
                       truth_change_over_set=chg,
                       truth_change_over_tau=[chg / max(tau[j] for j in T), chg / min(tau[j] for j in T)] if T else None,
                       exact_width_tau=[min((ex[j][1] - ex[j][0]) / tau[j] for j in T), max((ex[j][1] - ex[j][0]) / tau[j] for j in T)] if T else None,
                       label_miss_tau_max=max(abs(y[j] - t[j]) / tau[j] for j in T) if T else None)
            if len(T) < 15:
                rec["status"] = "NOT RUN"; assert sset["status"] != "RUN"; o["f3"][name] = rec; continue
            ntr, ncal = (6, 12) if len(T) >= 20 else (4, 9)
            rng = np.random.default_rng([seed, n, SET_CODE[name]])
            splits = []
            for _ in range(200):
                p = rng.permutation(len(T))
                splits.append((sorted(T[i] for i in p[:ntr]), sorted(T[i] for i in p[ntr:ntr + ncal]), sorted(T[i] for i in p[ntr + ncal:])))
            same = all(a[0] == b["train"] and a[1] == b["cal"] and a[2] == b["query"] for a, b in zip(splits, sset["splits"]))
            rec.update(status="RUN", n_train=ntr, n_cal=ncal, n_query=len(T) - ntr - ncal, splits_equal_stored=bool(same), models={})
            for mname, model in (("M1", line), ("M2", even), ("M0", cubic), ("const_posthoc", const)):
                okW, cov, wid, miss, okW_s, cov_s, wid_s = [], [], [], [], [], [], []
                for tr, cal, qs in splits:
                    xtr = sorted(set(R) - set(cal) - set(qs)) if mname == "M0" else tr
                    f = model(xtr, [y[j] for j in xtr])
                    q = kth([max(abs(f(j) - ex[j][0]), abs(f(j) - ex[j][1])) for j in cal])
                    qs_std = kth([abs(f(j) - y[j]) for j in cal])                                   # ph1: standard score
                    okW.append(all(2 * q <= tau[x] for x in qs)); okW_s.append(all(2 * qs_std <= tau[x] for x in qs))
                    for x in qs:
                        cov.append(abs(t[x] - f(x)) <= q); wid.append(2 * q / tau[x]); miss.append(abs(f(x) - t[x]) / tau[x])
                        cov_s.append(abs(t[x] - f(x)) <= qs_std); wid_s.append(2 * qs_std / tau[x])
                a = dict(frac_splits_W=float(np.mean(okW)), frac_pairs_C=float(np.mean(cov)), width_tau=[min(wid), float(np.median(wid)), max(wid)],
                         largest_miss_tau=max(miss), n_pairs=len(cov),
                         standard_score_posthoc=dict(frac_splits_W=float(np.mean(okW_s)), frac_pairs_C=float(np.mean(cov_s)),
                                                     width_tau=[min(wid_s), float(np.median(wid_s)), max(wid_s)]))
                rec["models"][mname] = a
                if mname in sset["models"]:
                    b = sset["models"][mname]
                    cmp("f3 frac_splits_W", a["frac_splits_W"], b["frac_splits_W"]); cmp("f3 frac_pairs_C", a["frac_pairs_C"], b["frac_pairs_C"])
                    cmp("f3 width/tau min", a["width_tau"][0], b["width_tau_min"]); cmp("f3 width/tau max", a["width_tau"][2], b["width_tau_max"])
                    cmp("f3 width/tau median", a["width_tau"][1], b["width_tau_median"]); cmp("f3 largest miss/tau", a["largest_miss_tau"], b["largest_miss_tau"])
            o["f3"][name] = rec
        # ph3 for the interval named in the declaration
        o["truth_change_4_to_6_over_tau"] = [(t[6.0] - t[4.0]) / tau[6.0], (t[6.0] - t[4.0]) / tau[4.0]]
        out["sizes"][str(n)] = o
    out["largest_difference_from_sealed_output"] = worst
    with open(os.path.join(OUT, "independent_check.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("declaration %s | seed %d | numpy %s" % (decl, seed, np.__version__))
    print("largest absolute differences from the sealed output:")
    for k in sorted(worst):
        print("  %-34s %.3e" % (k, worst[k]))
    for n in ("57", "115"):
        o = out["sizes"][n]
        print("n = %s inputs: %s" % (n, o["inputs"]))
        print("  f2 floor %.6f (k = %d of %d); the four widest lower widths are at %s" % (o["f2"]["floor"], o["f2"]["k"], o["f2"]["m"], o["f2"]["couplings_of_the_four_widest"]))
        print("  truth change 4.0 -> 6.0: %.3f-%.3f tau" % tuple(o["truth_change_4_to_6_over_tau"]))
        for name, r in o["f3"].items():
            print("  %-6s size %d range %s truth change %s tau, exact widths %s tau, label miss <= %s tau: %s" % (
                name, r["size"], r["range"], ["%.3f" % v for v in r["truth_change_over_tau"]], ["%.3f" % v for v in r["exact_width_tau"]],
                "%.3f" % r["label_miss_tau_max"], r["status"]))
            if r["status"] != "RUN":
                continue
            print("         splits equal to the stored ones: %s" % r["splits_equal_stored"])
            for m, a in r["models"].items():
                s = a["standard_score_posthoc"]
                print("         %-13s interval score: W %.3f C %.3f 2q/tau %.3f-%.3f miss <= %.3f | standard score (post hoc): W %.3f C %.3f 2q/tau %.4f-%.4f" % (
                    m, a["frac_splits_W"], a["frac_pairs_C"], a["width_tau"][0], a["width_tau"][2], a["largest_miss_tau"],
                    s["frac_splits_W"], s["frac_pairs_C"], s["width_tau"][0], s["width_tau"][2]))


if __name__ == "__main__":
    main()
