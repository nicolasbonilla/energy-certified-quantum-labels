"""break_F.py -- referee attack on F1 (learner-independent floor) and F2 (energy-only procedures). Own code.

F1-1  floors recomputed from learning_ibm/out/prop2_cubic.json (n = 57, 115), with the order statistic k stated by
      the proposition itself (k = ceil((m+1)(1-alpha)), q = +inf if k > m), and with k = m (the maximum score)
F1-2  the 45-point statement from map/laptop_analysis/summary_map.json
F1-3  adversarial learners for the constant-width score (exact minimum of 2q) and a random search
F1-4  OTHER SCORES inside the construction of the supplement ("any score"): a width-normalized score with
      sigma(x) tracking the width of the energy interval; finite-population exact coverage; does rule (c) answer
      although fewer than k calibration intervals are narrower than tau?
F1-5  part (iii) by Monte Carlo with adversarial predictors
F2-1  a procedure INSIDE the class (energy-only, Definition E) whose output is not an interval: part (c) with
      |C| = Lebesgue measure
F2-2  the two attaining procedures; exchangeability is not used
F2-3  the two-Hamiltonian illustration on a model WITHOUT a symmetry O -> -O
"""
import json, math, time
import numpy as np
from bl_common import two_colour, sector, zvals, build, lowest, expect

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
t00 = time.time()
rng = np.random.default_rng(5)
P = json.load(open(f"{ROOT}/phase3/full_runs/learning_ibm/out/prop2_cubic.json"))
alpha = P["alpha"]


def kth(m, a):
    return math.ceil((m + 1) * (1 - a) - 1e-12)


print(f"F1-1. floors from the stored intervals (alpha = {alpha})")
STORE = {}
for size in ("57", "115"):
    S = P["sizes"][size]
    train = [float(x) for x in S["train"]]
    recs = {float(r["Jz"]): r for r in S["indist"] + S["ood"]}
    test = [float(r["Jz"]) for r in S["ood"]]
    w_in, w_out, inner = {}, {}, {}
    for J in train + test:
        I = S["intervals"].get(str(J))
        w_in[J] = I["w_in"] if I else 0.0
        w_out[J] = I["w_out"] if I else None
        inner[J] = tuple(I["inner"]) if I else None
    STORE[size] = (train, test, recs, w_in, inner)
    print(f" n = {size}: training couplings {train}; no map row at {S['missing_rows']}")
    print("   inner widths in own tolerances: " + ", ".join(f"{J}: {w_in[J] / recs[J]['tau']:.2f}" for J in train))
    print("   query   m   k=ceil((m+1)(1-a))   floor_k/tau     floor_max/tau   stored 2q_lo/tau   ratio to floor_max   q recomputed from stored scores")
    for J in train + test:
        cal = [c for c in train if c != J]
        m = len(cal)
        k = kth(m, alpha)
        ws = sorted(w_in[c] for c in cal)
        tau = recs[J]["tau"]
        fk = ws[k - 1] / tau if k <= m else float("inf")
        fmax = ws[-1] / tau
        sc = sorted(c["s_lo"] for c in recs[J]["calib_scores"])
        qk = sc[k - 1] if k <= len(sc) else float("inf")
        print(f"   {J:4.1f}  {m:3d}   {k:3d} {'(> m: q = +inf)' if k > m else '               '}  {fk:10.3f}     {fmax:10.3f}      "
              f"{recs[J]['width_b_lo_tau']:10.3f}        {recs[J]['width_b_lo_tau'] / fmax:6.3f}          "
              f"2 s_(k)/tau = {2 * qk / tau:8.3f}, 2 max s/tau = {2 * sc[-1] / tau:8.3f}, #scores = {len(sc)}")
    rin = [sorted(w_in[c] for c in train if c != J)[-1] / recs[J]["tau"] for J in train]
    rte = [sorted(w_in[c] for c in train)[-1] / recs[J]["tau"] for J in test]
    print(f"   floor of the maximum score: training range {min(rin):.3f} .. {max(rin):.3f}; test range {min(rte):.3f} .. {max(rte):.3f}")
    # does the stored score equal max over the inner interval of |pred - y| ?
    dev = 0.0
    for J in train:
        for c in recs[J]["calib_scores"]:
            I = inner[float(c["Jz"])]
            if I is not None:
                lo, hi = min(I[0], c["label"]), max(I[1], c["label"])
                s_in = max(abs(c["pred_loo"] - I[0]), abs(c["pred_loo"] - I[1]))
                s_hull = max(abs(c["pred_loo"] - lo), abs(c["pred_loo"] - hi))
                dev = max(dev, min(abs(s_in - c["s_lo"]), abs(s_hull - c["s_lo"])))
    print(f"   stored s_lo reproduced from pred_loo and the inner interval (or its hull with the label): max deviation {dev:.1e}")

print("\nF1-2. the dataset's 45 training points (k = 42 of m = 45 at alpha = 0.1)")
print(f"   k = {kth(45, 0.1)}; intervals allowed to be wider than 2q: {45 - kth(45, 0.1)}")
M = json.load(open(f"{ROOT}/phase3/full_runs/map/laptop_analysis/summary_map.json"))
labs = sorted({r["label"] for r in M["rows"]})
grid = {round(1.6 + 0.1 * i, 1) for i in range(45)}
for nn in (57, 115):
    rows = sorted([r for r in M["rows"] if r["n"] == nn and r["label"] == "m_s" and not r.get("ood", False)], key=lambda r: r["Jz"])
    on = [r for r in rows if round(r["Jz"], 1) in grid]
    ws = sorted(((r["at_lo"]["w_in"], r["Jz"]) for r in on), reverse=True)
    taumax = max(r["tau"] for r in rows)
    jt = [r["Jz"] for r in rows if r["tau"] == taumax][0]
    mono = all(rows[i]["tau"] <= rows[i + 1]["tau"] + 1e-12 for i in range(len(rows) - 1))
    print(f"   n = {nn}: {len(rows)} computed training-range rows of m_s ({len(on)} on the 0.1 grid); four widest inner widths at the lowest "
          f"energy of the band: " + ", ".join(f"{w:.5f} (Jz={J})" for w, J in ws[:4]))
    print(f"        w_(42) >= {ws[3][0]:.5f}; largest tolerance among the computed rows {taumax:.5f} (Jz = {jt}; tau increasing in Jz: {mono}); "
          f"ratio {ws[3][0] / taumax:.4f}; eps_lo/eps_dig at that row = {[r['eps']['lo'] / r['eps']['dig'] for r in on if r['Jz'] == ws[3][1]][0]:.3f}")

print("\nF1-3. adversarial learners, constant-width score (n = 57 intervals)")
train, test, recs, w_in, inner = STORE["57"]
have = [J for J in train if inner[J] is not None]
lo = np.array([inner[J][0] for J in have]); hi = np.array([inner[J][1] for J in have])
m = len(have); k = kth(m, 1 / 8.0)
floor = np.sort(hi - lo)[k - 1]
best = np.inf
for trial in range(400000 // 2000):
    f = lo + (hi - lo) * rng.random((2000, m)) if trial % 2 else 0.5 * (lo + hi) + 0.02 * rng.standard_normal((2000, m))
    s = np.maximum(np.abs(f - lo), np.abs(f - hi))
    best = min(best, 2 * np.sort(s, axis=1)[:, k - 1].min())
mid = 0.5 * (lo + hi)
att = 2 * np.sort(np.maximum(np.abs(mid - lo), np.abs(mid - hi)))[k - 1]
print(f"   m = {m}, k = {k}: floor w_(k) = {floor:.6f}; smallest 2q over 400 000 prediction vectors = {best:.6f}; midpoints give {att:.6f}; "
      f"below the floor: {best < floor - 1e-12}")

print("\nF1-4. a width-normalized score inside the construction of Supplement (b) ('any score'), n = 57, 8 couplings with a row")
Js = np.array(have); w = hi - lo
taus = np.array([recs[J]["tau"] for J in have])
a8 = 1 / 8.0
for label, sig in (("sigma(x) = width of the energy interval at x (needs the energy at the query, as the filter does)", w.copy()),
                   ("sigma(x) = A Jz^-p fitted to all 8 widths (symmetric in the 8 points; a function of x only)",
                    np.exp(np.polyval(np.polyfit(np.log(Js), np.log(w), 1), np.log(Js))))):
    s = (w / 2) / sig                                        # midpoint learner: s_j = w_j / (2 sigma_j)
    ans, cov, lines = [], 0, []
    for i, J in enumerate(have):
        others = np.delete(s, i)
        kk = kth(len(others), a8)
        q = np.sort(others)[kk - 1]
        width = 2 * q * sig[i]
        contains = s[i] <= q + 1e-15
        cov += contains
        if width <= taus[i]:
            ans.append(J)
        lines.append(f"{J}: {width / taus[i]:.2f}{'' if contains else '*'}")
    narrow = int((w <= taus).sum())
    print(f"   {label}")
    print(f"      width/tau at each held-out coupling (* = does not contain the query's energy interval): " + ", ".join(lines))
    print(f"      contains the query's whole energy interval at {cov} of 8 held-out couplings (level 7/8 requires >= 7); rule (c) answers at {ans}; "
          f"calibration-wide count of intervals narrower than their tau: {narrow} of 8 (k = {kth(7, a8)} of m = 7 needed by (iv) for the constant-width score)")

print("\nF1-5. part (iii) by Monte Carlo: P(I(x) inside [f(x)-q, f(x)+q]) >= 1 - alpha, adversarial predictors")
for a, mm in ((0.1, 9), (0.1, 19), (0.2, 14)):
    kk = kth(mm, a)
    hits = 0; R = 60000
    xs = rng.random((R, mm + 1))
    wid = 0.02 + rng.pareto(1.5, (R, mm + 1)) * 0.05                # heavy-tailed widths, a function of nothing but chance
    centre = np.sin(7 * xs)
    f = centre + np.where(xs > 0.5, 1.0, -0.3) * wid * (xs - 0.3)     # predictor correlated with the width
    s = np.maximum(np.abs(f - (centre - wid / 2)), np.abs(f - (centre + wid / 2)))
    q = np.sort(s[:, :mm], axis=1)[:, kk - 1]
    hits = (s[:, mm] <= q).mean()
    print(f"   alpha = {a}, m = {mm}, k = {kk}: frequency {hits:.4f} (bound {1 - a:.2f}; exact value for continuous scores k/(m+1) = {kk / (mm + 1):.4f})")

print("\nF2-1. a non-interval procedure inside the class: part (c) with |C| = Lebesgue measure")
a = 0.1; eps = 0.1; wq = 1.0; tau = 0.9
R = 200000
U = rng.random(R)
refs = np.linspace(0, 1, 101)                                # reference positions (fractions of the interval), both ends included
cov = [float((((r - U) % 1.0) >= eps).mean()) for r in refs]
both = float(((((0.0 - U) % 1.0) >= eps) & (((1.0 - U) % 1.0) >= eps)).mean())
print(f"   C(x) = I(x) minus a cyclic arc of length eps*w at a uniform position, eps = alpha = {a}: Lebesgue measure (1-eps) w = {1 - eps:.2f} w always;")
print(f"   coverage of 101 references: min {min(cov):.4f} (exact 1 - eps = {1 - eps}); contains both ends with frequency {both:.4f};")
print(f"   with tau = {tau} w < w the rule 'answer iff Leb(C) <= tau' answers with probability 1 at an input whose energy interval is wider than tau "
      f"(bound claimed: 2 alpha = {2 * a}). With |C| = sup C - inf C it answers with probability <= {1 - both:.4f}.")

print("\nF2-2. attainment (exact): 'I w.p. 1-alpha, else empty' covers every reference w.p. 1-alpha and a fraction 1-alpha;")
print("      'I w.p. 1-2alpha, else I minus a piece at the upper / lower end (alpha each)' covers every reference w.p. >= 1-alpha and both ends w.p. 1-2alpha;")
print("      with pieces of length w - tau (tau < w <= 2 tau) the rule of (c) answers w.p. exactly 2 alpha: the constant of (c) is attained too.")
print("      The proof uses Definition E at the query only: the exchangeability hypothesis of the statement is not used.")

print("\nF2-3. two Hamiltonians with the same data: is the second truth the other end of the window without a symmetry O -> -O ?")
n = 10
E = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 9)]            # heavy-hex Y piece, sublattices 6 / 4
eta = np.array(two_colour(n, E), float)
st = sector(n, int((eta > 0).sum()))
Hoff, diag = build(st, n, E, hop=0.5, jz=2.5)
Od = eta @ zvals(st, n)


def gs(lam):                                                 # ground state of H - lam O
    w, v = lowest(Hoff, diag - lam * Od, k=2)
    return v, float(v * v @ Od) / n, expect(Hoff, diag, v)


nu0 = 0.05
v, y, Eg = gs(nu0)
v2, y2, E2 = gs(-nu0)
lo_, hi_ = 0.0, 5.0
for _ in range(80):                                          # lower end of the window of H at energy Eg: ground state of H + lam' O with <H> = Eg
    mid_ = 0.5 * (lo_ + hi_)
    if gs(-mid_)[2] < Eg:
        lo_ = mid_
    else:
        hi_ = mid_
v3, y3, E3 = gs(-hi_)
print(f"   Y piece (n = 10, Neel sector, Jz = 2.5), generator state = ground state of H - nu0 O, nu0 = {nu0}: (y, E) = ({y:.6f}, {Eg:.6f})")
print(f"   ground state of H + nu0 O: label {y2:.6f}, <H> = {E2:.6f}  (energy differs from E by {E2 - Eg:+.6f})")
print(f"   lower end of the window of H at E: label {y3:.6f}, reached at the field -{hi_:.6f} (not -nu0); <H> = {E3:.6f}")
print(f"   -> 'the truths for nu = +-nu0 are the two ends of the window' needs the symmetry; in general the second field is nu' = {hi_:.4f} != nu0")
print(f"\ntotal time {time.time() - t00:.0f} s")
