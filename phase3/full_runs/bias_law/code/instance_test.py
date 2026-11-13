# Exploratory analysis, no prior declaration. Do corrected sample-based labels carry instance-specific information that a classical
# model trained on small-system truth lacks?  Random Heisenberg (Huang-type couplings J in [0,2]) on a 4x5 target; calibration on
# different 4x4 instances. Per-bond label <ZZ>_b. Miss in tau = 0.06 mean|C0|.
#   raw        : truncated-state label
#   corrected  : C_s -> a(de) C_s + b(de), a, b fitted on the calibration instances at matched energy error per site
#   classical  : ridge on local couplings (J_b, neighbours), fitted on the truth of the calibration instances; uses no quantum data
#   both       : corrected label plus the local features
import sys, json
import numpy as np
sys.path.insert(0, 'code')
from scipy.sparse.linalg import eigsh
import importlib.util, types
src = open('code/generality.py', encoding='utf8').read().split("sizes = [(3, 4)")[0]
exec(src)
def inst(Lx, Ly, seed):
    r = np.random.default_rng(seed); E = grid(Lx, Ly); J = r.uniform(0, 2, len(E)); return E, J
def feats(E, J, n):
    s = np.zeros(n); c = np.zeros(n)
    for (i, j), x in zip(E, J): s[i] += x; s[j] += x; c[i] += 1; c[j] += 1
    F = []
    for (i, j), x in zip(E, J):
        o = s[i] + s[j] - 2 * x
        F.append([1, x, x * x, x**3, o, o * o, x * o, c[i] + c[j]])
    return np.array(F)
def states(Lx, Ly, seed, nD):
    n = Lx * Ly; E, J = inst(Lx, Ly, seed); H, Zc = build(n, [(i, j, c, c) for (i, j), c in zip(E, J)])
    w, v = eigsh(H, k=1, which='SA', tol=1e-9); E0 = w[0]; psi = v[:, 0]; p0 = psi**2
    P = np.stack([Zc[:, i] * Zc[:, j] for i, j in E], 1)
    C0 = p0 @ P; order = np.argsort(-p0); dim = len(psi); out = []
    for D in sorted(set(int(x) for x in np.round(np.logspace(1.2, np.log10(dim * .5), nD)))):
        B = np.sort(order[:D]); Hb = H[B][:, B]
        if D < 300: ww, vv = np.linalg.eigh(Hb.toarray())
        else: ww, vv = eigsh(Hb, k=1, which='SA', tol=1e-7)
        out.append(((ww[0] - E0) / n, (vv[:, 0]**2) @ P[B]))
    return dict(E=E, J=J, n=n, C0=C0, F=feats(E, J, n), S=out)
cal = [states(4, 4, 1000 + s, 12) for s in range(8)]
Fc = np.vstack([c['F'] for c in cal]); Yc = np.concatenate([c['C0'] for c in cal])
lam = 1e-3; wcl = np.linalg.solve(Fc.T @ Fc + lam * np.eye(Fc.shape[1]), Fc.T @ Yc)
print('classical model, in-sample rms on calibration truth %.4f, %d bonds' % (np.sqrt(np.mean((Fc @ wcl - Yc)**2)), len(Yc))); sys.stdout.flush()
def fitpair(de, both):
    X, Y = [], []
    for c in cal:
        k = int(np.argmin([abs(np.log(max(s[0], 1e-9) / de)) for s in c['S']])); Cs = c['S'][k][1]
        A = np.c_[np.ones(len(Cs)), Cs] if not both else np.c_[Cs, c['F']]
        X.append(A); Y.append(c['C0'])
    X = np.vstack(X); Y = np.concatenate(Y)
    return np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ Y)
print(' seed   de      raw   corrected  classical  corr+local   (mean per-bond miss in tau; corr. between bond errors of raw label and truth)')
tot = []
for s in (1, 2, 3, 4):
    T = states(4, 5, 2000 + s, 6); C0 = T['C0']; tau = .06 * np.mean(np.abs(C0)); pc = T['F'] @ wcl
    for de, Cs in T['S']:
        if de < 1e-3: continue
        a = fitpair(de, False); pa = a[0] + a[1] * Cs; b = fitpair(de, True); pb = np.c_[Cs, T['F']] @ b
        m = [np.mean(np.abs(x - C0)) / tau for x in (Cs, pa, pc, pb)]; tot.append(m)
        print(f' {s:3d} {de:8.4f} {m[0]:7.2f} {m[1]:7.2f} {m[2]:9.2f} {m[3]:9.2f}'); sys.stdout.flush()
print('mean over rows: raw %.2f corrected %.2f classical %.2f corrected+local %.2f' % tuple(np.mean(tot, axis=0)))
