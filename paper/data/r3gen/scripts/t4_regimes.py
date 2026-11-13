"""T4: regimes of Theorem 2.
(a) SSB without pinning: TFIM1D h=0.5, Zbar, full space: u_n(de) -> m_spont = (1-h^2)^(1/8) as n grows, at every de.
(b) Criticality, Hellmann-Feynman conjugate, exact thermodynamic limit (free fermions): Xbar of TFIM at h=1 vs h=1.5.
    u_inf(de) = inf_mu [alpha(mu)+de]/mu with alpha from e0(h) = -(1/pi) int_0^pi sqrt(1+h^2+2h cos k) dk.
    Prediction: regular h: u^2/de -> 2 chi (const); critical h=1: u^2/de grows like log(1/de).
(c) Criticality, order parameter: TFIM1D h=1 Zbar, finite-size scaling u_n n^{1/8} vs x = de n^2 (beta/nu=1/8, d+z=2);
    TL prediction u ~ de^{1/(1+delta)} = de^{1/16}.
(d) Scaling lemma: alpha = A mu^p  =>  u = p/(p-1) (A(p-1))^{1/p} de^{1-1/p}  (numerical check)."""
import time, numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar
from edcore import *

t0 = time.time()
print("(a) SSB, TFIM1D h=0.5, Zbar, no symmetry constraint; m_spont = %.4f" % ((1 - 0.25) ** 0.125))
for de in (1e-4, 1e-3, 1e-2):
    out = []
    for n in (6, 8, 10, 12):
        b, H = tfim(n, chain_edges(n), 1.0, 0.5)
        Ot = diag_op(b, [(1.0, (i,)) for i in range(n)])
        W = Window(H, Ot, +1)
        out.append(W.u(n * de)[0] / n)
    print(f"  de={de:7.1e}: u_n = " + ", ".join(f"{x:.4f}" for x in out) + "  (n=6,8,10,12; o0=0)")

print("\n(b) exact TL, TFIM Xbar (HF conjugate of h)")


def e0(h):
    return -quad(lambda k: np.sqrt(1 + h * h + 2 * h * np.cos(k)), 0, np.pi, limit=400, epsabs=1e-14, epsrel=1e-13)[0] / np.pi


def u_inf(h, de, side=+1):
    d = 1e-6
    x0 = -(e0(h + d) - e0(h - d)) / (2 * d)       # <Xbar> = -de0/dh
    def ob(lm):
        mu = np.exp(lm)
        a = e0(h) - side * mu * x0 - e0(h + side * mu)
        return (a + de) / mu
    r = minimize_scalar(ob, bounds=(np.log(1e-7), np.log(5.0)), method='bounded', options={'xatol': 1e-10})
    return r.fun, np.exp(r.x)


for h in (1.5, 1.0):
    print(f"  h={h}:")
    for de in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
        up, mp = u_inf(h, de, +1); um, mm = u_inf(h, de, -1)
        print(f"    de={de:7.1e}: u+={up:.6f} u-={um:.6f}  (u-)^2/de={um ** 2 / de:.4f}  (u+)^2/de={up ** 2 / de:.4f}  "
              f"log(1/de)={np.log(1 / de):.2f}")
# finite-n comparison at h=1
for n in (8, 12):
    b, H = tfim(n, chain_edges(n), 1.0, 1.0)
    Ot = x_op(b, [(i, 1.0) for i in range(n)])
    W = Window(H, Ot, -1)
    print(f"  ED n={n}, h=1, u-(de=1e-3) = {W.u(n * 1e-3)[0] / n:.5f}   (TL {u_inf(1.0, 1e-3, -1)[0]:.5f})")

print("\n(c) critical order parameter, TFIM1D h=1, Zbar, finite-size scaling")
rows = []
for n in (6, 8, 10, 12):
    b, H = tfim(n, chain_edges(n), 1.0, 1.0)
    Ot = diag_op(b, [(1.0, (i,)) for i in range(n)])
    W = Window(H, Ot, +1)
    for x in (0.03, 0.1, 0.3, 1.0, 3.0):
        de = x / n ** 2
        u = W.u(n * de)[0] / n
        rows.append((n, x, de, u, u * n ** 0.125))
for x in (0.03, 0.1, 0.3, 1.0, 3.0):
    sel = [r for r in rows if r[1] == x]
    print(f"  x=de n^2={x:5.2f}: u_n n^(1/8) = " + ", ".join(f"{r[4]:.4f}" for r in sel) + "   (n=6,8,10,12)")
for n in (6, 12):
    sel = [r for r in rows if r[0] == n]
    sl = np.polyfit(np.log([r[2] for r in sel[-3:]]), np.log([r[3] for r in sel[-3:]]), 1)[0]
    print(f"  n={n}: local slope dlog u/dlog de over x in [0.3,3] = {sl:.3f}  (TL prediction 1/16 = 0.0625; mean-field 1/4; regular 1/2)")

print("\n(d) scaling lemma check")
for p, A in ((2.0, 0.7), (1 + 1 / 15, 0.3), (1 + 1 / 3, 1.0), (1.5, 2.0)):
    for de in (1e-6, 1e-3):
        r = minimize_scalar(lambda lm: (A * np.exp(lm) ** p + de) / np.exp(lm), bounds=(-60, 10), method='bounded',
                            options={'xatol': 1e-12})
        pred = p / (p - 1) * (A * (p - 1)) ** (1 / p) * de ** (1 - 1 / p)
        print(f"  p={p:.4f} A={A}: de={de:.0e} numeric u={r.fun:.6e}  formula={pred:.6e}  rel.err={abs(r.fun / pred - 1):.1e}")
print(f"time {time.time() - t0:.1f} s")
