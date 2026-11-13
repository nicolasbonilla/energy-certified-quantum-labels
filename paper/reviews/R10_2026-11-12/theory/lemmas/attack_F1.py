"""attack_F1.py -- the learner-independent floor of Proposition 2(b): recomputation and attack with random learners.

Statement attacked. Calibration labels j = 1..m with intervals I_j = [l_j, h_j] of widths w_j; ANY real numbers f_j
(the learner's predictions at the calibration inputs; for the jackknife, the leave-one-out predictions); scores
s_j = max_{y in I_j} |f_j - y|; q = k-th smallest score, k = ceil((m+1)(1-alpha)) (q = +infinity if k > m; the stored
heavy-hex protocol uses k = m in that case). Then 2q >= w_(k), the k-th smallest width, with equality when every f_j is
the midpoint of I_j.

Part 1  stored intervals of phase3/full_runs/learning_ibm/out/prop2_cubic.json (read-only; own code):
        floor for every query coupling, n = 57 and 115; comparison with the cubic model's stored 2q;
        attack: random predictions, learners trained on random admissible labels, a direct minimizer.
Part 2  the dataset's own 45 training points (alpha = 0.1, k = 42), from the stored certification map
        phase3/full_runs/map/laptop_analysis/summary_map.json (rows of m_s, inner widths at the lowest energy of
        the digitization band).
Run:  python -B attack_F1.py > attack_F1_out.txt
"""
import json, math
import numpy as np
from scipy.optimize import minimize

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
rng = np.random.default_rng(2026)
ALPHA = 0.1


def kth(m, alpha=ALPHA):
    return math.ceil((m + 1) * (1 - alpha))


def conformal_q(scores, k):
    s = np.sort(np.asarray(scores, float))
    return s[min(k, len(s)) - 1]            # stored protocol: the largest score when k > m


def scores(f, lo, hi, lab=None):
    s = np.maximum(np.abs(f - lo), np.abs(f - hi))
    if lab is not None:
        s = np.maximum(s, np.abs(f - lab))
    return s


P = json.load(open(f"{ROOT}/phase3/full_runs/learning_ibm/out/prop2_cubic.json"))
print("=" * 112)
print("Part 1: stored energy intervals of m_s (inner = hull of stored explicit states, a sub-interval of the window;")
print("        outer = DMRG-referenced interval). Widths in units of tau(x) = 0.06 |m_s^truth(x)| at the QUERY x.")
tot_draws = 0
worst_ratio = np.inf
nviol = 0
for size in ("57", "115"):
    S = P["sizes"][size]
    R = [float(x) for x in S["train"]]
    info = {}
    for rec in S["indist"] + S["ood"]:
        info[float(rec["Jz"])] = dict(tau=rec["tau"], truth=rec["truth"], label=rec["label"],
                                      b_lo=rec["width_b_lo_tau"], b_hi=rec["width_b_hi_tau"])
    iv = {}
    for J in R:
        I = S["intervals"].get(str(J))
        y = info[J]["label"]
        if I is None:                       # no map row at this coupling: lower version = the label alone, width 0
            iv[J] = dict(lo=y, hi=y, w_in=0.0, w_out=None, y=y)
        else:
            iv[J] = dict(lo=I["inner"][0], hi=I["inner"][1], w_in=I["w_in"], w_out=I["w_out"], y=y)
        # the label is a window value too: hull of inner interval and label
        iv[J]["lo2"] = min(iv[J]["lo"], y); iv[J]["hi2"] = max(iv[J]["hi"], y)
        iv[J]["w2"] = iv[J]["hi2"] - iv[J]["lo2"]
    print(f"\nn = {size}: training couplings {R}; missing map rows: {S['missing_rows']}")
    print("   Jz    tau      w_in/tau(Jz)  w_out/tau(Jz)  hull(inner,label)/tau(Jz)")
    for J in R:
        t = info[J]["tau"]
        wo = "   n/a" if iv[J]["w_out"] is None else f"{iv[J]['w_out']/t:8.3f}"
        print(f"   {J:3.1f}  {t:.5f}   {iv[J]['w_in']/t:8.3f}      {wo}        {iv[J]['w2']/t:8.3f}")
    print("   query  range  m   k   floor (inner)  floor (inner+label)  floor (outer; n/a if a row is missing)  cubic 2q_lo  cubic 2q_hi  2q_lo/floor")
    floors = {"train": [], "test": []}
    for J in sorted(info):
        rngname = "train" if J in R else "test"
        cal = [c for c in R if c != J]
        m = len(cal); k = min(kth(m), m)
        t = info[J]["tau"]
        w_in = np.sort([iv[c]["w_in"] for c in cal]); w2 = np.sort([iv[c]["w2"] for c in cal])
        fl = w_in[k - 1] / t; fl2 = w2[k - 1] / t
        if any(iv[c]["w_out"] is None for c in cal):
            flo = float("nan")
        else:
            flo = np.sort([iv[c]["w_out"] for c in cal])[k - 1] / t
        floors[rngname].append((fl, fl2, flo))
        print(f"   {J:4.1f}   {rngname:5s} {m:2d}  {k:2d}   {fl:9.3f}      {fl2:9.3f}            {flo:9.3f}                         "
              f"{info[J]['b_lo']:8.3f}     {info[J]['b_hi']:8.3f}    {info[J]['b_lo']/fl2:6.3f}")
        assert info[J]["b_lo"] >= fl2 - 1e-9
        # ---- attack with random learners (the lower version of the scores includes the label, as in the design note)
        lo = np.array([iv[c]["lo"] for c in cal]); hi = np.array([iv[c]["hi"] for c in cal]); lab = np.array([iv[c]["y"] for c in cal])
        mid = 0.5 * (np.minimum(lo, lab) + np.maximum(hi, lab))
        best = np.inf
        # (i) arbitrary predictions
        F = rng.uniform(-0.5, 1.5, size=(20000, m))
        # (ii) predictions near the midpoints
        F = np.vstack([F, mid + rng.normal(0, 0.02, size=(20000, m)), mid + rng.normal(0, 0.002, size=(20000, m))])
        # (iii) a cubic in 1/Jz fitted to labels drawn uniformly inside the intervals, evaluated at the calibration
        #       inputs (in sample) and leave-one-out
        X = np.vander(1.0 / np.array(cal), 4)
        Y = rng.uniform(np.minimum(lo, lab), np.maximum(hi, lab), size=(5000, m))
        Hat = X @ np.linalg.pinv(X)
        F = np.vstack([F, Y @ Hat.T])
        loo = np.empty((2000, m))
        for j in range(m):
            keep = [i for i in range(m) if i != j]
            A = np.linalg.pinv(X[keep]) @ Y[:2000, keep].T            # (4, 2000)
            loo[:, j] = X[j] @ A
        F = np.vstack([F, loo])
        s = np.maximum(np.maximum(np.abs(F - lo), np.abs(F - hi)), np.abs(F - lab))
        q = np.sort(s, axis=1)[:, k - 1]
        best = float((2 * q / t).min())
        tot_draws += len(F)
        # (iv) direct minimization of 2q over the prediction vector
        obj = lambda f: 2 * conformal_q(scores(f, lo, hi, lab), k) / t
        for start in (mid + rng.normal(0, 0.05, m), rng.uniform(0, 1, m), mid):
            r = minimize(obj, start, method="Nelder-Mead", options=dict(xatol=1e-10, fatol=1e-12, maxiter=20000))
            best = min(best, float(r.fun))
        att = obj(mid)
        worst_ratio = min(worst_ratio, best / fl2)
        nviol += (best < fl2 - 1e-9)
        if abs(att - fl2) > 1e-9:
            print("      midpoint learner does not attain the floor:", att, fl2)
    for name in ("train", "test"):
        a = np.array(floors[name])
        print(f"   n = {size}, {name} range: floor (inner) {a[:,0].min():.2f}-{a[:,0].max():.2f} tau; "
              f"with the label in the hull {a[:,1].min():.2f}-{a[:,1].max():.2f} tau; outer {np.nanmin(a[:,2]) if not np.all(np.isnan(a[:,2])) else float('nan'):.2f}-{np.nanmax(a[:,2]) if not np.all(np.isnan(a[:,2])) else float('nan'):.2f} tau")
print(f"\nattack: {tot_draws} random prediction vectors plus 3 direct minimizations per query; "
      f"violations of 2q >= floor: {nviol}; smallest 2q/floor found: {worst_ratio:.6f} (1 = attained by the midpoints)")

# ---------------------------------------------------------------------------------------------------------------
print("=" * 112)
print("Part 2: the dataset's own 45 training couplings (Jz = 1.6, 1.7, ..., 6.0), alpha = 0.1")
M = json.load(open(f"{ROOT}/phase3/full_runs/map/laptop_analysis/summary_map.json"))
labels = sorted({r["label"] for r in M["rows"]})
print("   labels in the map:", labels)
lab_ms = [l for l in labels if l.lower().replace("_", "") in ("ms", "mstag", "msbar")]
lab_ms = lab_ms[0] if lab_ms else [l for l in labels if "m" in l.lower() and "s" in l.lower()][0]
m45 = 45
k45 = kth(m45)
print(f"   m = {m45}, k = ceil(46 x 0.9) = {k45}: at most {m45 - k45} calibration labels may have intervals wider than 2q")
grid = [round(1.6 + 0.1 * i, 1) for i in range(45)]
for nn in (57, 115):
    rows = sorted([r for r in M["rows"] if r["n"] == nn and r["label"] == lab_ms and not r.get("ood", False)], key=lambda r: r["Jz"])
    print(f"\n   n = {nn}, label {lab_ms}: computed map rows in the training range (width of the hull of explicit states at the three energies of the digitization band)")
    print("     Jz    eps_lo    eps_dig   eps_up    tau       w_in(lo)  /tau    w_in(dig) /tau    w_out(up) /tau   on the 0.1 grid")
    tab = []
    for r in rows:
        on = round(r["Jz"], 1) in grid
        tab.append((r["Jz"], r["at_lo"]["w_in"], r["tau"], r["at_dig"]["w_in"], r["at_up"]["w_out"] if "at_up" in r else float("nan"), on))
        print(f"     {r['Jz']:3.1f}  {r['eps']['lo']:8.4f}  {r['eps']['dig']:8.4f} {r['eps']['up']:8.4f}  {r['tau']:.5f}   "
              f"{r['at_lo']['w_in']:.5f} {r['at_lo']['w_in']/r['tau']:6.2f}    {r['at_dig']['w_in']:.5f} {r['at_dig']['w_in']/r['tau']:6.2f}    "
              f"{(r['at_up']['w_out'] if 'at_up' in r else float('nan')):.5f} {(r['at_up']['w_out']/r['tau'] if 'at_up' in r else float('nan')):6.2f}   {on}")
    taumax = max(t[2] for t in tab)
    for (nm, col) in (("lowest energy of the band (at_lo, inner)", 1), ("digitized energy (at_dig, inner)", 3)):
        w = sorted([t[col] for t in tab if t[5]], reverse=True)
        nwide = sum(1 for t in tab if t[5] and t[col] > t[2])
        need = m45 - k45 + 1                 # the (m-k+1)-th widest label bounds w_(k) from below
        if len(w) >= need:
            wk = w[need - 1]
            print(f"     {nm}: {nwide} computed couplings wider than their tau; the {need}th widest computed interval is {wk:.5f}"
                  f" -> w_(42) >= {wk:.5f} whatever the other {m45 - len(w)} labels are;")
            print(f"        in units of the largest tolerance of the training range (tau = {taumax:.5f} at Jz = {max(tab, key=lambda t: t[2])[0]}): "
                  f"{wk/taumax:.3f} tau;   in units of tau at the coupling of that label: {wk/[t[2] for t in tab if t[col] == wk][0]:.3f} tau")
print("\n   The floor of Part 2 is conditional on the digitized energies of the map (the dataset's own energies were")
print("   read from figures) and on all 45 training points being used as calibration points with the constant-width score.")
