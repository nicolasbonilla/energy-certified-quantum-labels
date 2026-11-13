"""Cross-check by exact diagonalization of Theorem 2 (intensive averages), with Theorem 3(a), Lemma A, Lemma B and
Theorem 1(a,b), by exact diagonalization at n <= 10. Separate code (numpy/scipy only). Runs in ~2.5 min.

Systems (random parameters, fixed seed):
  S1  XXZ on random bipartite trees with unequal sublattices, Neel ("pinned") S^z sector, O = staggered m_s;
  S2  XXZ chain (n = 8, 9), lowest |S^z| sector, O = average nearest-neighbour ZZ;
  S3  transverse-field Ising chain (no sector), O = average Z (h > 1) and average X;
  S4  eigenvector case (Thm 2(d)): XXZ chain without a sector, O = average Z (the GS is an eigenvector).
For each: alpha_n(mu) exactly, u_n(de) by the dual (Lemma A, golden section; unimodal), the primal value of the
dual-optimal ground state, the sandwich (2b) at several mu_1, the 'iff' of (2b), the gap bound (2c) with C_1 and
Delta_* measured along the deformed family, (2d), and Theorem 3(a) E*(c) (primal bisection on <O>) vs alpha*(c)
(Legendre, golden section). Prints the worst margins; a negative margin is a violation."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"   # tiny matrices: one BLAS thread is much faster

import itertools
import numpy as np
from scipy.linalg import eigh

rng = np.random.default_rng(20261104)
X = np.array([[0, 1], [1, 0]], float); Y = np.array([[0, -1j], [1j, 0]]); Z = np.diag([1., -1.]); I2 = np.eye(2)


def op(n, ops):  # ops: {site: 2x2}
    m = np.array([[1.0]])
    for s in range(n):
        m = np.kron(m, ops.get(s, I2))
    return m


def sector_basis(n, nup):
    idx = [i for i in range(2 ** n) if bin(i).count('1') == nup]
    return np.array(idx)


def zdiag(n, s):  # Z_s diagonal in computational basis (kron order, site 0 = most significant)
    return np.array([1 - 2 * ((i >> (n - 1 - s)) & 1) for i in range(2 ** n)], float)


def xxz(n, edges, Jz, Jxy=None):
    H = np.zeros((2 ** n, 2 ** n), complex)
    for k, (a, b) in enumerate(edges):
        jx = 1.0 if Jxy is None else Jxy[k]
        H += 0.25 * (jx * (op(n, {a: X, b: X}) + op(n, {a: Y, b: Y})) + Jz[k] * op(n, {a: Z, b: Z}))
    return H.real


def low2(A):
    w, v = eigh(A, subset_by_index=[0, 1])
    return w, v


class Fam:
    """H - mu * n * Obar restricted to a sector (P = list of basis indices)."""
    def __init__(self, H, Ob, n, P=None):
        if P is not None:
            H = H[np.ix_(P, P)]; Ob = Ob[np.ix_(P, P)]
        self.H, self.O, self.n = H, Ob, n
        w, v = low2(H)
        self.E0, self.gap0 = w[0], w[1] - w[0]
        self.psi0 = v[:, 0]
        self.o0 = float(self.psi0 @ Ob @ self.psi0)

    def gs(self, mu):
        w, v = low2(self.H - mu * self.n * self.O)
        p = v[:, 0]
        return w, p, float(p @ self.H @ p), float(p @ self.O @ p)

    def alpha(self, mu):  # per site
        w, _, _, _ = self.gs(mu)
        return (self.E0 - mu * self.n * self.o0 - w[0]) / self.n


def golden(f, a, b, it=50):
    g = (np.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(it):
        if fc < fd:
            b, d, fd = d, c, fc; c = b - g * (b - a); fc = f(c)
        else:
            a, c, fc = c, d, fd; d = a + g * (b - a); fd = f(d)
    x = 0.5 * (a + b)
    return x, f(x)


def u_dual(F, de, sign=+1):
    """u(de) = inf_{mu>0} [alpha(sign*mu) + de]/mu for the extent in direction sign (Lemma A / Thm 2a)."""
    grid = np.geomspace(1e-6, 200, 40)
    vals = [(F.alpha(sign * m) + de) / m for m in grid]
    k = int(np.argmin(vals))
    lo, hi = grid[max(k - 1, 0)], grid[min(k + 1, len(grid) - 1)]
    lmu, val = golden(lambda t: (F.alpha(sign * np.exp(t)) + de) / np.exp(t), np.log(lo), np.log(hi))
    return val, np.exp(lmu)


def chi_pm(F, mu1, sign=+1):
    grid = np.geomspace(mu1 * 1e-5, mu1, 160)   # log grid: the sup is often at small mu
    r = np.array([2 * F.alpha(sign * m) / m ** 2 for m in grid])
    # refine sup and inf
    def ref(k, s):
        lo, hi = grid[max(k - 1, 0)], grid[min(k + 1, len(grid) - 1)]
        _, v = golden(lambda m: -s * 2 * F.alpha(sign * m) / m ** 2, lo, hi, 60)
        return -s * v
    cp = max(r.max(), ref(int(np.argmax(r)), +1))
    cm = min(r.min(), ref(int(np.argmin(r)), -1))
    return cp, cm


def C1_gap(F, mu, ops_local, P):
    """Delta_* (in-sector gap) and C_1 = max_i sum_j |<o_i o_j>_c| at the deformed ground state."""
    w, p, _, _ = F.gs(mu)
    loc = [o[np.ix_(P, P)] if P is not None else o for o in ops_local]
    ev = np.array([p @ o @ p for o in loc])
    C = np.array([[p @ (a @ b) @ p - ea * eb for b, eb in zip(loc, ev)] for a, ea in zip(loc, ev)])
    return w[1] - w[0], np.abs(C).sum(1).max()


def random_tree(n):
    edges = [(i, int(rng.integers(0, i))) for i in range(1, n)]
    col = [0] * n
    for i, j in edges:
        col[i] = 1 - col[j]
    return edges, col


report = {}
diag = []

def worst(key, margin):
    report[key] = min(report.get(key, np.inf), margin)


def test_family(name, F, ops_local, P, mu1_list, des):
    for sign in (+1, -1):
        for mu1 in mu1_list:
            cp, cm = chi_pm(F, mu1, sign)
            # Theorem 2(b) sandwich, for de <= chi+ mu1^2/2
            for de in des:
                if de > cp * mu1 ** 2 / 2:
                    continue
                u, mustar = u_dual(F, de, sign)
                up = np.sqrt(2 * cp * de)
                lo = min(np.sqrt(2 * max(cm, 0) * de), max(cm, 0) * mu1 / 2)
                worst('T2b upper  (sqrt(2chi+de) - u)/u', (up - u) / max(u, 1e-12))
                worst('T2b lower  (u - lower)/u', (u - lo) / max(u, 1e-12))
                # Lemma A strong duality: primal value of the dual-optimal ground state
                _, p, e, o = F.gs(sign * mustar)
                prim = sign * (o - F.o0)
                epsr = (e - F.E0) / F.n
                if abs(epsr - de) < 0.05 * de:   # the optimizer sits on a ground state with the right energy
                    worst('LemA |primal - dual|/u (neg = gap)', -abs(prim - u) / max(u, 1e-12) + 2e-3)
            # Theorem 2(c): chi+ <= 2 C1/Delta_*  with sup C1 and inf Delta along [0, mu1]
            mus = np.linspace(0, mu1, 25)
            vals = [C1_gap(F, sign * m, ops_local, P) for m in mus]
            Dmin = min(v[0] for v in vals); C1 = max(v[1] for v in vals)
            if Dmin > 1e-6:
                worst('T2c (2C1/Delta* - chi+)/chi+', (2 * C1 / Dmin - cp) / cp)
        # 'iff' of (2b): by conjugacy sup_de u(de)^2/(2 de) must equal chi_glob = sup_mu 2 alpha(mu)/mu^2.
        # '<=' is the 'if' direction (u <= sqrt(2 chi_glob de) for all de); '>=' (tightness) is the 'only if':
        # any chi < chi_glob is violated at some de.
        mus = np.geomspace(1e-5, 100, 400)
        r2 = np.array([2 * F.alpha(sign * m) / m ** 2 for m in mus])
        k = int(np.argmax(r2)); cg = r2[k]; mu_arg = mus[k]
        # the de at which the dual optimum sits at mu_arg: de = mu alpha'(mu) - alpha(mu)
        h = 1e-4 * mu_arg
        dal = (F.alpha(sign * (mu_arg + h)) - F.alpha(sign * (mu_arg - h))) / (2 * h) if k > 0 else 0.0
        de_arg = mu_arg * dal - F.alpha(sign * mu_arg)
        des_g = np.geomspace(1e-9, 20, 40)
        Rs = [u_dual(F, de, sign)[0] ** 2 / (2 * de) for de in des_g]
        j = int(np.argmax(Rs))
        # refine the sup over de by golden section in log(de) between the neighbouring grid points
        a_, b_ = np.log(des_g[max(j - 1, 0)]), np.log(des_g[min(j + 1, len(des_g) - 1)])
        tR = golden(lambda t: -u_dual(F, np.exp(t), sign)[0] ** 2 / (2 * np.exp(t)), a_, b_, 40)[0]
        Rr = u_dual(F, np.exp(tR), sign)[0] ** 2 / (2 * np.exp(tR))
        R, de_R = (Rr, np.exp(tR)) if Rr > Rs[j] else (Rs[j], des_g[j])
        diag.append((name, sign, cg, mu_arg, de_arg, R, de_R))
        worst('T2b iff (if):      (chi_glob - sup u^2/2de)/chi_glob', (cg - R) / cg)
        worst('T2b iff (only if): -(chi_glob - sup u^2/2de)/chi_glob + 1e-2', -(cg - R) / cg + 1e-2)
        # Theorem 3(a): E*(c) (primal: bisection on <O> along the family, then the hull of the curve) vs alpha*(c)
        omax = sign * np.linalg.eigvalsh(F.O)[-1 if sign > 0 else 0]
        for frac in (0.05, 0.2, 0.5):
            c = frac * (omax - sign * F.o0)
            # dual: alpha*(c) = sup_mu [mu c - alpha(mu)]  (concave in mu)
            _, negv = golden(lambda t: -(np.exp(t) * c - F.alpha(sign * np.exp(t))), np.log(1e-4), np.log(200))
            astar = -negv * F.n  # total energy
            # primal: smallest mu with sign*(<O>-o0) >= c, energy of that ground state; with a level crossing the
            # mixture of the two bracketing ground states on the line is the minimiser
            lo_, hi_ = 0.0, 1.0
            while sign * (F.gs(sign * hi_)[3] - F.o0) < c and hi_ < 1e4:
                hi_ *= 2
            for _ in range(60):
                mid = 0.5 * (lo_ + hi_)
                if sign * (F.gs(sign * mid)[3] - F.o0) >= c:
                    hi_ = mid
                else:
                    lo_ = mid
            _, _, ea, oa = F.gs(sign * lo_); _, _, eb, ob = F.gs(sign * hi_)
            t = (c - sign * (oa - F.o0)) / max(sign * (ob - oa), 1e-15)
            t = min(max(t, 0), 1)
            Estar = (1 - t) * ea + t * eb - F.E0
            worst('T3a |E*(c) - alpha*(c)|/E* (neg = gap)', -abs(Estar - astar) / max(Estar, 1e-12) + 2e-3)


# ---------- S1: pinned bipartite trees, m_s ----------
for trial in range(4):
    n = 9 if trial % 2 else 8
    for _ in range(50):
        edges, col = random_tree(n)
        na = sum(1 for c in col if c == 0)
        if abs(2 * na - n) >= 2:
            break
    maj = 0 if na > n - na else 1
    eta = [1 if c == maj else -1 for c in col]
    Jz = rng.uniform(1.2, 3.0, len(edges))
    H = xxz(n, edges, Jz)
    nup = sum(1 for e in eta if e > 0)   # Neel sector: majority colour up
    zs = [zdiag(n, s) for s in range(n)]
    # sector: number of up spins = nup (Z = +1 <-> bit 0)
    P = np.array([i for i in range(2 ** n) if sum(1 for s in range(n) if zs[s][i] > 0) == nup])
    ms = np.diag(sum(e * z for e, z in zip(eta, zs)) / n)
    F = Fam(H, ms, n, P)
    test_family('S1', F, [np.diag(e * z) for e, z in zip(eta, zs)], P, [0.05, 0.2], [1e-4, 1e-3, 5e-3, 2e-2])

# ---------- S2: XXZ chain, Sz = 0, average nn ZZ ----------
for n in (8, 9):
    edges = [(i, i + 1) for i in range(n - 1)]
    Jz = rng.uniform(0.5, 2.0, len(edges))
    H = xxz(n, edges, Jz)
    zs = [zdiag(n, s) for s in range(n)]
    P = np.array([i for i in range(2 ** n) if sum(1 for s in range(n) if zs[s][i] > 0) == n // 2])
    zz = [np.diag(zs[a] * zs[b]) for a, b in edges]
    Ob = sum(zz) / n
    F = Fam(H, Ob, n, P)
    test_family('S2', F, zz, P, [0.05, 0.2], [1e-4, 1e-3, 5e-3])

# ---------- S3: TFIM chain, h > 1, average Z and average X ----------
for n, h in ((6, 1.6), (7, 2.3)):
    H = -sum(op(n, {i: Z, i + 1: Z}) for i in range(n - 1)) - h * sum(op(n, {i: X}) for i in range(n))
    H = H.real
    for which in ('Z', 'X'):
        loc = [op(n, {i: (Z if which == 'Z' else X)}).real for i in range(n)]
        F = Fam(H, sum(loc) / n, n)
        test_family('S3' + which, F, loc, None, [0.1, 0.4], [1e-4, 1e-3, 1e-2])

# ---------- S4: eigenvector case (Thm 2(d)): u <= de/mu_c ----------
n = 8
edges = [(i, i + 1) for i in range(n - 1)]
H = xxz(n, edges, rng.uniform(1.0, 2.0, len(edges)))
M = sum(op(n, {i: Z}).real for i in range(n)) / n
F = Fam(H, M, n)
# mu_c: the field at which the ground state changes (alpha stays 0 until then)
mus = np.linspace(1e-4, 3, 300)
al = np.array([F.alpha(m) for m in mus])
k = int(np.argmax(al > 1e-10)); lo_, hi_ = mus[k - 1], mus[k]
for _ in range(50):   # bisection for the field at which the ground state changes
    mid = 0.5 * (lo_ + hi_)
    lo_, hi_ = (mid, hi_) if F.alpha(mid) <= 1e-12 else (lo_, mid)
muc = hi_
for de in (1e-4, 1e-3, 1e-2, 5e-2):
    u, _ = u_dual(F, de, +1)
    worst('T2d (de/mu_c - u)/u', (de / muc - u) / max(u, 1e-12))
print(f"T2d check: GS eigenvector of M (o_GS = {F.o0:+.3e}), mu_c = {muc:.6f}")

# ---------- Theorem 1(a) (no sector) and 1(b) (U(1) sector, covariant block reset) ----------
# 1(a): TFIM chain, O = Z_i: exact extent >= min(1, eps/kappa_A)(o_max - o_GS)
n, h = 8, 1.5
H = (-sum(op(n, {i: Z, i + 1: Z}) for i in range(n - 1)) - h * sum(op(n, {i: X}) for i in range(n))).real
i0 = 3
Zi = op(n, {i0: Z}).real
kappa = 2 * 2 + 2 * h          # two ZZ bonds (spread 2 each) + the X_i term (spread 2h)
F = Fam(H, Zi / n, n)          # Fam multiplies by n: H - mu n (Z/n) = H - mu Z
for eps in (0.05, 0.2, 1.0, 3.0, 10.0):
    u, _ = u_dual(F, eps / n, +1)
    u *= n                     # extent of Z_i itself
    bound = min(1, eps / kappa) * (1 - F.o0 * n)
    worst('T1a (extent - bound)', u - bound)
# 1(b): XXZ chain in S^z = 0, O = Z_i, block B = {i, i+1}: extent >= min(1, eps/kappa_B)(c_B^+ - o_GS)
n = 8
edges = [(i, i + 1) for i in range(n - 1)]
Jzv = 1.7
H = xxz(n, edges, [Jzv] * len(edges))
zs = [zdiag(n, s) for s in range(n)]
P = np.array([i for i in range(2 ** n) if sum(1 for s in range(n) if zs[s][i] > 0) == n // 2])
i0 = 3
F = Fam(H, np.diag(zs[i0]) / n, n, P)
psi = np.zeros(2 ** n); psi[P] = F.psi0
p_down = sum(abs(psi[k]) ** 2 for k in range(2 ** n) if zs[i0][k] < 0 and zs[i0 + 1][k] < 0)
cB = 1 - 2 * p_down
kappaB = 3 * (1 + Jzv) / 2     # three bonds touch {i, i+1}; spread of (XX+YY+Jz ZZ)/4 = (1+Jz)/2
for eps in (0.05, 0.2, 1.0, 3.0, 10.0):
    u, _ = u_dual(F, eps / n, +1)
    u *= n
    bound = min(1, eps / kappaB) * (cB - F.o0 * n)
    worst('T1b (extent - bound)', u - bound)

# ---------- Lemma B: a two-state mixture is attained by a pure state in the span ----------
n = 8
edges = [(i, i + 1) for i in range(n - 1)]
H = xxz(n, edges, rng.uniform(1.0, 2.0, len(edges)))
zs = [zdiag(n, s) for s in range(n)]
P = np.array([i for i in range(2 ** n) if sum(1 for s in range(n) if zs[s][i] > 0) == n // 2])
Ob = np.diag(sum(zs[a] * zs[b] for a, b in edges) / n)
F = Fam(H, Ob, n, P)
worstB = 0.0
for _ in range(10):
    m1, m2 = rng.uniform(0, 0.5), rng.uniform(-0.5, 0)
    _, a, ea, oa = F.gs(m1); _, b, eb, ob = F.gs(m2)
    t = rng.uniform(0.1, 0.9)
    target = np.array([(1 - t) * ea + t * eb, (1 - t) * oa + t * ob])
    best = np.inf
    for th, ph in itertools.product(np.linspace(0, np.pi / 2, 121), np.linspace(0, 2 * np.pi, 121)):
        v = np.cos(th) * a + np.exp(1j * ph) * np.sin(th) * b
        v = v / np.linalg.norm(v)
        pt = np.array([np.real(v.conj() @ F.H @ v), np.real(v.conj() @ F.O @ v)])
        best = min(best, np.abs(pt - target).max())
    worstB = max(worstB, best)
print(f"LemB: worst distance of a two-state mixture point to the pure numerical range of the span "
      f"(121x121 grid): {worstB:.2e}")

print("\nT2b iff diagnostics (family, side, chi_glob, mu at sup, de there, sup_de u^2/2de, de at sup, rel gap):")
for d_ in diag:
    print("  %-4s %+d  chi_glob %.5f  mu* %.3g  de(mu*) %.3g  R %.5f  de_R %.3g  rel %.2e"
          % (d_[0], d_[1], d_[2], d_[3], d_[4], d_[5], d_[6], (d_[2] - d_[5]) / d_[2]))
print("\nWorst margins (negative = violation):")
for k, v in report.items():
    print(f"  {k:48s} {v:+.3e}")
