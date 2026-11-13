"""Cross-check by exact diagonalization of Proposition 2 (learning from certified labels) on a miniature of the paper's
benchmark: random antiferromagnetic Heisenberg models on a 2 x 4 open lattice (n = 8, 10 bonds, couplings U[0, 2]),
exact diagonalization in S^z = 0 (dim 70; SU(2) => no sector assumption). Separate code (numpy/scipy only).

Label sets (for every instance, at energy E0 + n*de):
  exact      ground-state labels;
  perlabel   the paper's construction: EACH label from its OWN extremal window state, toward less order
             (DECLARATION Sec. 3(iii));
  onestate   a jointly realizable adversary: ONE window state per instance (ground state of H - lam * sum_b C_b at
             <H> = E0 + n*de, the state that pushes the bond sum toward less order), all labels taken from it.
Learner: kernel ridge (Gaussian kernel on the couplings), fixed label-independent hyperparameters (linear in labels).
Checks: Prop. 2(a) deterministic band; 2(b) certified split-conformal coverage of the truth vs standard split
conformal; 2(c) selective error; and the energy identity E = 3 sum_b J_b C_b as a trivial detector of the
per-label set. 200 random splits 80/30/50 of 160 instances; alpha = 0.1."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"   # tiny matrices: one BLAS thread is much faster

import itertools, time
import numpy as np
from scipy.linalg import eigh

t0 = time.time()
rng = np.random.default_rng(7)
Lx, Ly = 2, 4
n = Lx * Ly
site = lambda x, y: Ly * x + y
bonds = [(site(x, y), site(x + 1, y)) for x in range(Lx - 1) for y in range(Ly)] + \
        [(site(x, y), site(x, y + 1)) for x in range(Lx) for y in range(Ly - 1)]
nb = len(bonds)
basis = [s for s in range(2 ** n) if bin(s).count('1') == n // 2]
index = {s: k for k, s in enumerate(basis)}
d = len(basis)


def bond_op(a, b):  # (XX + YY + ZZ) on the S^z = 0 basis
    M = np.zeros((d, d))
    for k, s in enumerate(basis):
        za, zb = (s >> a) & 1, (s >> b) & 1
        M[k, k] += 1.0 if za == zb else -1.0
        if za != zb:
            M[index[s ^ ((1 << a) | (1 << b))], k] += 2.0
    return M


P = [bond_op(a, b) for a, b in bonds]           # H = sum_b J_b P_b ; label C_b = <P_b>/3


def gs(A):
    w, v = eigh(A, subset_by_index=[0, 1])
    return w[0], v[:, 0], w[1] - w[0]


def golden(f, a, b, it=60):
    g = (np.sqrt(5) - 1) / 2
    c, e = b - g * (b - a), a + g * (b - a)
    fc, fe = f(c), f(e)
    for _ in range(it):
        if fc < fe:
            b, e, fe = e, c, fc; c = b - g * (b - a); fc = f(c)
        else:
            a, c, fc = c, e, fe; e = a + g * (b - a); fe = f(e)
    return 0.5 * (a + b)


def window_extreme(H, O, E, E0, sign):
    """Dual bound (Lemma A) on sign*<O> over {<H> <= E}: min_lam (E - E0(H - sign lam O))/lam (valid at any lam),
    and the primal: ground state of H - sign lam O with the largest lam s.t. <H> <= E (a state in the window)."""
    # By strong duality the optimal multiplier is the one at which the tilted ground state has <H> = E, so one
    # bisection gives both: the primal witness at lam_lo (<H> <= E) and the dual bound evaluated at lam_hi and
    # lam_lo (each lam gives a valid bound; we keep the smaller).
    lo, hi = 0.0, 1.0
    while True:
        _, v, _ = gs(H - sign * hi * O)
        if v @ H @ v > E or hi > 1e4:
            break
        lo, hi = hi, 2 * hi
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        _, v, _ = gs(H - sign * mid * O)
        if v @ H @ v <= E:
            lo = mid
        else:
            hi = mid
    _, v, _ = gs(H - sign * lo * O)
    dual = min((E - gs(H - sign * lam * O)[0]) / lam for lam in (lo, hi) if lam > 0)
    return sign * dual, v                       # bound on <O> (upper if sign=+1, lower if -1), witness state


def instance(J, de):
    H = sum(j * p for j, p in zip(J, P))
    E0, v0, gap = gs(H)
    E = E0 + n * de
    ops = [p / 3 for p in P] + [sum(P) / (3 * nb)]        # 10 bonds + the average Cnn (index nb)
    exact = np.array([v0 @ o @ v0 for o in ops])
    cert = np.zeros((nb + 1, 2)); perlabel = np.zeros(nb + 1)
    for k, o in enumerate(ops):
        hi, vhi = window_extreme(H, o, E, E0, +1)
        lo, _ = window_extreme(H, o, E, E0, -1)
        cert[k] = (lo, hi)
        perlabel[k] = vhi @ o @ vhi             # toward less AF order = larger C
    _, vone = window_extreme(H, ops[nb], E, E0, +1)
    onestate = np.array([vone @ o @ vone for o in ops])
    Eimp = lambda C: 3 * np.dot(J, C[:nb])
    return dict(exact=exact, cert=cert, perlabel=perlabel, onestate=onestate, E0=E0, E=E, gap=gap,
                Eimp_perlabel=Eimp(perlabel), Eimp_onestate=Eimp(onestate), Eimp_exact=Eimp(exact))


def kernel(A, B, g=1.0 / nb):
    d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
    return np.exp(-g * d2)


def run(de, N=160, R=200, ntr=80, ncal=30, alpha=0.1, ridge=1e-2, tau=0.08):
    Js = rng.uniform(0, 2, (N, nb))
    recs = [instance(J, de) for J in Js]
    Y = {k: np.array([r[k] for r in recs]) for k in ('exact', 'perlabel', 'onestate')}
    CI = np.array([r['cert'] for r in recs])               # N x labels x 2
    eps = n * de
    ex = lambda key: np.array([(r[key] - r['E0']) / eps for r in recs])
    print(f"\n=== de = {de:g}  (eps = {eps:g}); instances {N}, splits {R}")
    print(f"energy identity, implied (E - E0)/eps of the 10 bond labels: exact {np.median(ex('Eimp_exact')):+.3f}, "
          f"onestate median {np.median(ex('Eimp_onestate')):+.3f}, perlabel median {np.median(ex('Eimp_perlabel')):+.1f} "
          f"[min {ex('Eimp_perlabel').min():+.1f}]")
    inside = all((CI[i, k, 0] - 1e-9 <= Y[s][i, k] <= CI[i, k, 1] + 1e-9)
                 for i in range(N) for k in range(nb + 1) for s in Y)
    print("all labels of every set inside their certified intervals:", inside)
    shift = {s: np.mean(np.abs(Y[s] - Y['exact']), 0) for s in ('perlabel', 'onestate')}
    print(f"mean |shift| bonds: perlabel {shift['perlabel'][:nb].mean():.4f}, onestate {shift['onestate'][:nb].mean():.4f};"
          f" Cnn: perlabel {shift['perlabel'][nb]:.4f}, onestate {shift['onestate'][nb]:.4f};"
          f" mean certified half-width bonds {0.5 * (CI[:, :nb, 1] - CI[:, :nb, 0]).mean():.4f}")
    qidx = int(np.ceil((ncal + 1) * (1 - alpha))) - 1
    stats = {}
    band_viol = 0; band_checks = 0; joint_ex = []; ans = []
    for r in range(R):
        perm = rng.permutation(N)
        tr, ca, te = perm[:ntr], perm[ntr:ntr + ncal], perm[ntr + ncal:]
        K = kernel(Js[tr], Js[tr]); Ainv = np.linalg.inv(K + ridge * np.eye(ntr))
        Aca = kernel(Js[ca], Js[tr]) @ Ainv; Ate = kernel(Js[te], Js[tr]) @ Ainv   # a(x) rows
        for s in ('exact', 'perlabel', 'onestate'):
            for cls, ks in (('bond', range(nb)), ('avg', [nb])):
                for k in ks:
                    ytr = Y[s][tr, k]
                    fca, fte = Aca @ ytr, Ate @ ytr
                    # standard split conformal on the generated labels
                    qs = np.sort(np.abs(fca - Y[s][ca, k]))[qidx]
                    # certified split conformal (CSC): score max over the certified interval
                    sc = np.maximum(np.abs(fca - CI[ca, k, 0]), np.abs(fca - CI[ca, k, 1]))
                    qc = np.sort(sc)[qidx]
                    yt = Y['exact'][te, k]
                    st = stats.setdefault((s, cls), dict(sc=[], csc=[], own=[], wsc=[], wcsc=[]))
                    st['sc'].append(np.mean(np.abs(fte - yt) <= qs)); st['own'].append(np.mean(np.abs(fte - Y[s][te, k]) <= qs))
                    st['csc'].append(np.mean(np.abs(fte - yt) <= qc)); st['wsc'].append(2 * qs); st['wcsc'].append(2 * qc)
                    # Prop 2(a): |f - f*| <= W(x) = sum_i |a_i(x)| (hi_i - lo_i)
                    if s != 'exact':
                        fstar = Ate @ Y['exact'][tr, k]
                        W = np.abs(Ate) @ (CI[tr, k, 1] - CI[tr, k, 0])
                        band_viol += int(np.sum(np.abs(fte - fstar) > W + 1e-12)); band_checks += len(te)
                    # Prop 2(c) with the CB construction: band [f_lo, f_hi] + conformal margin, answer iff width <= tau
                    if s == 'perlabel' and cls == 'avg':
                        wtr = CI[tr, k]
                        flo = lambda A: A.clip(min=0) @ wtr[:, 0] + A.clip(max=0) @ wtr[:, 1]
                        fhi = lambda A: A.clip(min=0) @ wtr[:, 1] + A.clip(max=0) @ wtr[:, 0]
                        scb = np.maximum(0, np.maximum(CI[ca, k, 1] - fhi(Aca), flo(Aca) - CI[ca, k, 0]))
                        qb = np.sort(scb)[qidx]
                        lo_t, hi_t = flo(Ate) - qb, fhi(Ate) + qb
                        a_ = (hi_t - lo_t) <= tau
                        mid = 0.5 * (lo_t + hi_t)
                        joint_ex.append(np.mean(a_ & (np.abs(mid - yt) > tau / 2))); ans.append(np.mean(a_))
    print(f"{'labels':9s} {'class':5s} {'SC truth':>9s} {'SC own':>7s} {'CSC truth':>9s} {'min CSC/split':>13s} {'width CSC/SC':>12s}")
    for (s, cls), st in stats.items():
        print(f"{s:9s} {cls:5s} {np.mean(st['sc']):9.3f} {np.mean(st['own']):7.3f} {np.mean(st['csc']):9.3f} "
              f"{np.min(st['csc']):13.3f} {np.mean(st['wcsc']) / np.mean(st['wsc']):12.2f}")
    print(f"Prop 2(a): {band_viol} violations in {band_checks} checks")
    print(f"Prop 2(c) (CB, perlabel, avg, tau={tau}): answer rate {np.mean(ans):.3f}, "
          f"P(answer and miss > tau/2) = {np.mean(joint_ex):.4f} <= alpha = {alpha}")


for de in (2e-3, 1e-2):
    run(de)
print(f"\nruntime {time.time() - t0:.1f} s")
