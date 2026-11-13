"""attack_F2.py -- attack of the floor F2 for procedures whose guarantee rests on the energies alone.

Statement attacked. Each input x carries an interval I(x) = [l(x), h(x)] (the energy interval of the label at x,
width w(x)). A procedure maps the calibration data and the query to a set C(x). It is "energy-only at level
1 - alpha" if P(t(X) in C(X)) >= 1 - alpha for EVERY reference selection t with t(x) in I(x). Then
   (a) P(l(X) in C(X) and h(X) in C(X)) >= 1 - 2 alpha   (for interval-valued C: C contains I(X), so |C| >= w(X));
   (b) E[ Leb(C(X) n I(X)) / w(X) ] >= 1 - alpha;
   (c) a rule that answers only when |C(X)| <= tau answers at an input with w(X) > tau with probability <= 2 alpha.
Part A  exact enumeration on the stored heavy-hex intervals (n = 57, the 8 training couplings with a map row),
        finite-population exchangeability (the held-out coupling is uniform), alpha = 1/8.
Part B  Monte Carlo in a synthetic i.i.d. world, alpha = 0.1, m = 19.
Part C  exact diagonalization (ring of 8 sites): the two-Hamiltonian construction behind the two-point argument,
        and why it does not give a floor for a procedure that knows the Hamiltonian.
Run:  python -B attack_F2.py > attack_F2_out.txt
"""
import json, math
import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
rng = np.random.default_rng(7)


def frac_covered(clo, chi, lo, hi):
    return max(0.0, min(chi, hi) - max(clo, lo)) / (hi - lo)


# ---------------------------------------------------------------------------------------------------------------
print("=" * 110)
print("Part A: stored intervals (hull of the inner interval and the label), exact enumeration over the held-out coupling")
P = json.load(open(f"{ROOT}/phase3/full_runs/learning_ibm/out/prop2_cubic.json"))["sizes"]["57"]
lab = {float(r["Jz"]): r["label"] for r in P["indist"]}
tau = {float(r["Jz"]): r["tau"] for r in P["indist"]}
Js = [float(j) for j in P["train"] if P["intervals"][str(float(j))] is not None]
lo = np.array([min(P["intervals"][str(j)]["inner"][0], lab[j]) for j in Js])
hi = np.array([max(P["intervals"][str(j)]["inner"][1], lab[j]) for j in Js])
y = np.array([lab[j] for j in Js]); w = hi - lo
N = len(Js); m = N - 1
alpha = 1.0 / N
k = math.ceil((m + 1) * (1 - alpha))
print(f"  couplings {Js}; N = {N}, m = {m}, alpha = 1/{N}, k = {k}; widths/tau = {[round(float(w[i]/tau[Js[i]]),2) for i in range(N)]}")
X = np.vander(1.0 / np.array(Js), 4)
f_cubic = X @ np.linalg.lstsq(X, y, rcond=None)[0]
mid = 0.5 * (lo + hi)
learners = {"cubic through the labels": f_cubic, "midpoints": mid, "top ends": hi.copy()}
for r in range(3):
    learners[f"random function {r}"] = rng.uniform(lo.min() - 0.2, hi.max() + 0.2, N)
refs = {"top": hi, "bottom": lo, "mid": mid}
for r in range(200):
    refs[f"rand{r}"] = lo + rng.uniform(0, 1, N) * w


def evaluate(name, sets, sound_expected=True):
    """sets[i] = list of (probability, clo, chi) for held-out index i"""
    cov = {rn: np.mean([sum(p for (p, a, b) in sets[i] if a - 1e-15 <= t[i] <= b + 1e-15) for i in range(N)]) for rn, t in refs.items()}
    both = np.mean([sum(p for (p, a, b) in sets[i] if a - 1e-15 <= lo[i] and hi[i] <= b + 1e-15) for i in range(N)])
    fr = np.mean([sum(p * frac_covered(a, b, lo[i], hi[i]) for (p, a, b) in sets[i]) for i in range(N)])
    mincov = min(cov.values())
    sound = mincov >= 1 - alpha - 1e-12
    okA = (both >= 1 - 2 * alpha - 1e-12 and fr >= 1 - alpha - 1e-12) if sound else None
    print(f"  {name:44s} min coverage over 203 references {mincov:.4f} ({'energy-only' if sound else 'NOT energy-only'});"
          f" P(C contains I) = {both:.4f}; mean covered fraction = {fr:.4f}"
          + ("" if okA is None else f";  bounds {1-2*alpha:.3f}, {1-alpha:.3f}: {'ok' if okA else 'VIOLATION'}"))
    return sound, okA


viol = 0
for ln, f in learners.items():
    s = np.maximum(np.abs(f - lo), np.abs(f - hi))
    sets = []
    for i in range(N):
        q = np.sort(np.delete(s, i))[k - 1]
        sets.append([(1.0, f[i] - q, f[i] + q)])
    sd, ok = evaluate(f"Prop. 2(b), constant width, {ln}", sets); viol += (ok is False) + (not sd)
    sn = s / w
    sets = []
    for i in range(N):
        q = np.sort(np.delete(sn, i))[k - 1]
        sets.append([(1.0, f[i] - q * w[i], f[i] + q * w[i])])
    sd, ok = evaluate(f"Prop. 2(b), width-normalized, {ln}", sets); viol += (ok is False) + (not sd)
sd, ok = evaluate("the window itself, C = I", [[(1.0, lo[i], hi[i])] for i in range(N)]); viol += (ok is False) + (not sd)
sd, ok = evaluate("all-or-nothing: I w.p. 1-alpha, else empty", [[(1 - alpha, lo[i], hi[i]), (alpha, 1.0, 0.0)] for i in range(N)]); viol += (ok is False) + (not sd)
d = 1e-6
sd, ok = evaluate("two ends: a sliver dropped at one end w.p. alpha each",
                  [[(1 - 2 * alpha, lo[i], hi[i]), (alpha, lo[i] + d * w[i], hi[i]), (alpha, lo[i], hi[i] - d * w[i])] for i in range(N)])
viol += (ok is False) + (not sd)
# a procedure that is not energy-only: standard split conformal on the generated labels
s_std = np.abs(f_cubic - y)
sets = []
for i in range(N):
    q = np.sort(np.delete(s_std, i))[k - 1]
    sets.append([(1.0, f_cubic[i] - q, f_cubic[i] + q)])
evaluate("standard conformal on the labels (cubic)", sets)
print(f"  Part A: violations among energy-only procedures: {viol}")

# ---------------------------------------------------------------------------------------------------------------
print("=" * 110)
print("Part B: synthetic i.i.d. world, x ~ U[0,1], I(x) = [g(x) - 0.3 w(x), g(x) + 0.7 w(x)], w(x) = 0.02 + 0.5 (1-x)^2,")
print("        generated label at the top third of the interval; alpha = 0.1, m = 19, k = 18; learner fitted on 40 separate labels")
alpha = 0.1; m = 19; k = math.ceil((m + 1) * (1 - alpha))
g = lambda x: 0.6 + 0.3 * x
wf = lambda x: 0.02 + 0.5 * (1 - x) ** 2
REP = 40000
cov = {r: 0 for r in ("top", "bottom", "mid", "label", "random")}
cov_std = dict(cov)
both = both_std = 0; fr = fr_std = 0.0; ans_wide = 0
tau_syn = 0.1
for rep in range(REP):
    xt = rng.uniform(0, 1, 40); yt = g(xt) + (0.7 - rng.uniform(0, 1 / 3, 40)) * wf(xt)
    coef = np.polyfit(xt, yt, 2)
    xc = rng.uniform(0, 1, m + 1)
    l_ = g(xc) - 0.3 * wf(xc); h_ = g(xc) + 0.7 * wf(xc); y_ = h_ - rng.uniform(0, 1 / 3, m + 1) * wf(xc)
    f = np.polyval(coef, xc)
    s = np.maximum(np.abs(f - l_), np.abs(f - h_))
    q = np.sort(s[:m])[k - 1]
    q_std = np.sort(np.abs(f - y_)[:m])[k - 1]
    t = dict(top=h_[m], bottom=l_[m], mid=0.5 * (l_[m] + h_[m]), label=y_[m], random=l_[m] + rng.uniform() * (h_[m] - l_[m]))
    for r in cov:
        cov[r] += abs(f[m] - t[r]) <= q
        cov_std[r] += abs(f[m] - t[r]) <= q_std
    both += (f[m] - q <= l_[m] and h_[m] <= f[m] + q); both_std += (f[m] - q_std <= l_[m] and h_[m] <= f[m] + q_std)
    fr += frac_covered(f[m] - q, f[m] + q, l_[m], h_[m]); fr_std += frac_covered(f[m] - q_std, f[m] + q_std, l_[m], h_[m])
    ans_wide += (2 * q <= tau_syn and (h_[m] - l_[m]) > tau_syn)
se = math.sqrt(0.1 * 0.9 / REP)
print("  Prop. 2(b): coverage of references " + ", ".join(f"{r} {cov[r]/REP:.4f}" for r in cov)
      + f"; P(C contains I) = {both/REP:.4f} (bound {1-2*alpha:.2f}); mean covered fraction = {fr/REP:.4f} (bound {1-alpha:.2f});"
      + f" P(answered and w > tau) = {ans_wide/REP:.4f} (bound {2*alpha:.2f})   [Monte Carlo s.e. about {se:.4f}]")
print("  standard conformal on the labels: coverage of references " + ", ".join(f"{r} {cov_std[r]/REP:.4f}" for r in cov_std)
      + f"; P(C contains I) = {both_std/REP:.4f}; mean covered fraction = {fr_std/REP:.4f}  (not energy-only: the bounds do not apply and do not hold)")

# ---------------------------------------------------------------------------------------------------------------
print("=" * 110)
print("Part C: two Hamiltonians with identical data (ring of 8 sites, Jz = 2.5, sector S^z = 0, O = sum eta_i Z_i)")
from ed_small import basis, zvals, build, ring
n = 8
E, eta = ring(n)
st = basis(n, n // 2)
z = zvals(st, n); od = np.asarray(eta, float) @ z
K, diag = build(st, n, E, 2.5)
Hd = K.toarray() + np.diag(diag)
lam = np.linspace(-0.6, 0.6, 2401)
e = np.empty_like(lam); o = np.empty_like(lam)
for i, l in enumerate(lam):
    wv, v = np.linalg.eigh(Hd - l * np.diag(od))
    p = v[:, 0] ** 2
    o[i] = p @ od / n
    e[i] = v[:, 0] @ (Hd @ v[:, 0])
i0 = int(np.argmin(np.abs(lam)))
ig = int(np.argmin(np.abs(lam - 0.05)))
yg, Eg = o[ig], e[ig]
print(f"  generator state: ground state of H - 0.05 O; label y = {yg:+.5f}, energy under H: E = {Eg:.6f} (E0 = {e[i0]:.6f}, error {Eg-e[i0]:.6f})")


def world(nu, name):
    """true Hamiltonian H_nu = H - nu (O - n y): same generator state, same label, same energy number"""
    en = e - nu * n * (o - yg)                       # energy of psi(lam) under H_nu
    it = int(np.argmin(np.abs(lam - nu)))            # ground state of H_nu is psi(nu)
    feas = en <= Eg + 1e-12
    print(f"  {name}: nu = {nu:+.3f}; energy of the generator state under H_nu = {en[ig]:.6f}; ground energy {en[it]:.6f} "
          f"(error {Eg-en[it]:.6f}); true label {o[it]:+.5f}; labels of the family states with energy <= E: "
          f"[{o[feas].min():+.5f}, {o[feas].max():+.5f}]"
          + (" (lower end: end of the field grid, the interval extends further)" if feas[0] else ""))
    return o[it], o[feas].min(), o[feas].max()


world(0.0, "nominal H          ")
tp, ap, bp = world(+0.03, "world +, nu small  ")
tm, am, bm = world(-0.03, "world -, nu small  ")
tP, aP, bP = world(+0.05, "world +, nu = 0.05 ")
tM, aM, bM = world(-0.05, "world -, nu = -0.05")
print(f"  identical data (y, E) in every world; true labels {tP:+.5f} and {tM:+.5f} in the last two worlds: the two ends of")
print(f"  the nominal window [{-yg:+.5f}, {yg:+.5f}]. A procedure that sees only (x, y, E) and covers the truth in both must contain")
print("  both with probability >= 1 - 2 alpha. The energy intervals computed with the true Hamiltonian differ between the")
print("  worlds (a point in world +, a wide interval in world -), so a procedure that knows the Hamiltonian tells them apart:")
print("  the two-point argument needs an unknown conjugate field, not only an unknown ground state.")
