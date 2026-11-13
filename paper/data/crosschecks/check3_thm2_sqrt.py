"""Check 3 -- Theorem 2 (intensive averages), Corollary 1 (accuracy law), and the hypotheses of Theorem 2(c).

For an average O = (1/n) sum_i o_i, f_n(mu) = E0(H - mu n O)/n, alpha_n(mu) = f_n(0) - mu o_GS - f_n(mu),
u_n(de) = inf_mu [alpha_n(mu) + de]/mu (exact, Lemma A), chi_+-(mu1) = sup/inf_{0<mu<=mu1} 2 alpha/mu^2.
Tests, at fixed error per site de and growing n:
  (b) sandwich  min{sqrt(2 chi_- de), chi_- mu1/2} <= u_n(de) <= sqrt(2 chi_+ de)   for de <= chi_+ mu1^2/2;
  (c) chi_+ <= 2 C1/Delta_*  with Delta_* the smallest gap and C1 = max_i sum_j |<o_i o_j>_c| along 0 <= mu <= mu1;
  size independence of u_n(de), also when eps = n de exceeds the gap (eps/Delta > 1);
  (d) u_n ~ sqrt(2 chi(0) de) at small de;
  Corollary 1: the exact de* at which the two-sided width equals tau, against tau^2/(8 chi(0)).
Families:
  A  transverse-field Ising ring, h = 1.5 (gapped paramagnet), O = mean Z   (sides symmetric)
  B  XXZ comb ferrimagnet (Jz = 2), extensively pinned max-S^z sector, O = m_s, both sides (as in the dataset)
  C  contrast: XXZ ring (Jz = 2) in the balanced S^z = 0 sector, O = m_s (unpinned: hypothesis of (c) fails)
alpha is tabulated once per (instance, side) on a log grid of mu (1e-5 .. 20) that resolves chi(0); u is the grid
minimum refined by Brent inside the bracketing grid cell. About half a minute.
"""
import numpy as np
import scipy.sparse as sp
from scipy.optimize import brentq, minimize_scalar

import edlib as ed

MU = np.geomspace(1e-5, 20.0, 110)


def family_A(n):
    H, _ = ed.tfim(n, 1.5, periodic=True)
    return H, ed.zvals(n, ed.basis(n)), np.ones(n)


def family_B(nb):
    n, edges, col = ed.comb(nb)
    st = ed.basis(n, int((col == 0).sum()))
    return ed.xxz(n, edges, 2.0, st), ed.zvals(n, st), np.where(col == 0, 1.0, -1.0)


def family_C(n):
    edges = [(i, (i + 1) % n) for i in range(n)]
    st = ed.basis(n, n // 2)
    return ed.xxz(n, edges, 2.0, st), ed.zvals(n, st), np.array([(-1) ** i for i in range(n)], float)


class Avg:
    def __init__(self, H, Z, w):
        self.H, self.Z, self.w = H, Z, w
        self.n = Z.shape[1]
        self.Od = Z @ w / self.n
        self.F = sp.diags(Z @ w)                     # n * O
        w0, v0 = ed.ground(H, k=2)
        self.E0, self.gap0 = w0[0], w0[1] - w0[0]
        self.oGS = float(v0[:, 0] ** 2 @ self.Od)
        self.cache = {}

    def gs(self, mu, k=1):
        key = (mu, k)
        if key not in self.cache:
            w, v = ed.ground(self.H - mu * self.F, k=k)
            self.cache[key] = (w[0], (w[1] - w[0]) if k > 1 else None, v[:, 0])
        return self.cache[key]

    def alpha(self, mu):
        return (self.E0 - mu * self.n * self.oGS - self.gs(mu)[0]) / self.n

    def table(self, sign):
        return np.array([self.alpha(sign * m) for m in MU])

    def u(self, de, sign, tab):
        g = (tab + de) / MU
        k = int(np.argmin(g))
        a, b = MU[max(k - 1, 0)], MU[min(k + 1, len(MU) - 1)]
        r = minimize_scalar(lambda m: (self.alpha(sign * m) + de) / m, bounds=(a, b), method="bounded",
                            options=dict(xatol=1e-12 * b))
        return min(r.fun, g[k])

    def C1(self, mu):
        p = self.gs(mu)[2] ** 2
        Zw = self.Z * self.w[None, :]
        m = p @ Zw
        C = (Zw * p[:, None]).T @ Zw - np.outer(m, m)
        return float(np.max(np.abs(C).sum(axis=1)))


def analyse(A, mu1, des, sign):
    tab = A.table(sign)
    sel = MU <= mu1
    r = 2 * tab[sel] / MU[sel] ** 2
    chip, chim, chi0 = r.max(), r.min(), r[0]
    probe = np.unique(np.concatenate([MU[sel][::4], np.linspace(0.05, mu1, 8)]))
    gaps = [A.gs(sign * m, k=2)[1] for m in probe] + [A.gap0]
    C1 = max([A.C1(sign * m) for m in probe])
    Dst = min(gaps)
    imin = int(np.argmin(gaps[:-1]))
    rows = []
    for de in des:
        u = A.u(de, sign, tab)
        lo = min(np.sqrt(2 * chim * de), chim * mu1 / 2)
        hi = np.sqrt(2 * chip * de)
        valid = de <= chip * mu1 ** 2 / 2
        ok = (lo * (1 - 1e-7) <= u <= hi * (1 + 1e-7)) if valid else None
        rows.append((de, u, lo, hi, valid, ok, np.sqrt(2 * chi0 * de), A.n * de / A.gap0))
    return dict(tab=tab, chip=chip, chim=chim, chi0=chi0, C1=C1, Dst=Dst, mu_at_Dmin=probe[imin],
                bound=2 * C1 / Dst, rows=rows)


viol = ntest = 0
summary = {}
des = (1e-4, 1e-3, 1e-2, 3e-2, 0.1, 0.3)
for fam, builder, sizes, mu1, sides in (("A TFIM h=1.5, mean Z", family_A, (6, 8, 10, 12), 0.4, (+1,)),
                                         ("B comb Jz=2 pinned sector, m_s", family_B, (4, 6, 8), 0.4, (+1, -1)),
                                         ("C XXZ ring Jz=2 S^z=0, m_s", family_C, (6, 8, 10, 12), 0.4, (+1,))):
    print("=" * 112)
    print("Family", fam, "  (mu1 = %.2f)" % mu1)
    for sz in sizes:
        A = Avg(*builder(sz))
        for sg in sides:
            o = analyse(A, mu1, des, sg)
            summary[(fam[0], A.n, sg)] = (A, o)
            okc = o["chip"] <= o["bound"] * (1 + 1e-9)
            ntest += 1
            viol += not okc
            print(" n=%2d side %+d o_GS=%+.4f gap0=%.4g chi(0)=%.4f chi+=%.4f chi-=%.4f | C1=%.4f Delta*=%.4g (at mu=%.3g) 2C1/Delta*=%.4f [chi+ <= it: %s]" % (
                A.n, sg, A.oGS, A.gap0, o["chi0"], o["chip"], o["chim"], o["C1"], o["Dst"], sg * o["mu_at_Dmin"],
                o["bound"], okc))
            for (de, u, lo, hi, valid, ok, law, eg) in o["rows"]:
                if valid:
                    ntest += 1
                    viol += not ok
                print("     de=%.0e u_n=%.6f sandwich [%.6f, %.6f] %-9s sqrt(2 chi0 de)=%.6f u/law=%.4f eps/gap0=%.2f" % (
                    de, u, lo, hi, ("ok" if ok else "VIOLATION") if valid else "(n/a)", law, u / law, eg))

print("=" * 112)
print("Size dependence of u_n(de), side + (and side - for B):")
for fam, sg in (("A", 1), ("B", 1), ("B", -1), ("C", 1)):
    for de in (1e-3, 1e-2, 0.1):
        vals = [(k[1], [r[1] for r in v[1]["rows"] if abs(r[0] - de) < 1e-15][0]) for k, v in summary.items()
                if k[0] == fam and k[2] == sg]
        print("  %s side %+d de=%.0e: " % (fam, sg, de) + "  ".join("n=%d: %.5f" % t for t in vals))

print("=" * 112)
print("Corollary 1 (accuracy law): exact de* where the two-sided width u+ + u- equals tau, vs tau^2/(8 chi(0))")
for key, taus in ((("A", 8, 1), (0.05, 0.1, 0.2, 0.4)), (("A", 10, 1), (0.05, 0.2)),
                  (("B", 9, 1), ("6%",)), (("B", 12, 1), ("6%",))):
    A, o = summary[key]
    tm = summary.get((key[0], key[1], -1), (A, o))[1]["tab"] if key[0] == "B" else o["tab"]
    sm = -1 if key[0] == "B" else 1
    chi0 = 0.5 * (o["chi0"] + (summary[(key[0], key[1], -1)][1]["chi0"] if key[0] == "B" else o["chi0"]))
    for tau in taus:
        t = 0.06 * abs(A.oGS) if tau == "6%" else tau
        width = lambda d: A.u(d, 1, o["tab"]) + A.u(d, sm, tm)
        dstar = brentq(lambda d: width(d) - t, 1e-9, 0.5, xtol=1e-14, rtol=1e-10)
        print("  %s n=%2d tau=%.4f exact de*=%.6g  law=%.6g  law/exact=%.4f  eps*/gap0=%.3f" % (
            key[0], key[1], t, dstar, t ** 2 / (8 * chi0), t ** 2 / (8 * chi0) / dstar, key[1] * dstar / A.gap0))
print("\nTheorem 2 tests (sandwich where valid + chi bound): %d, violations: %d" % (ntest, viol))
