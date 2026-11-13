# R11 fix pass (fixer FT, 2026-11-13): copy of paper/reviews/R11_2026-11-13/scratch/hostile-A/d1_constants.py, unchanged
# (it reads no file). Output: ft_theorem4_constant_out.txt (next to this file).
# hostile-A / d1_constants.py -- the constant C1bar of Supplemental Eq. (C1bar) for given delta_0 and tbar (own evaluation)
from mpmath import mp, mpf, e, pi, sqrt, exp, nsum, inf
mp.dps = 40
def consts(d0, tb):
    d0, tb = mpf(d0), mpf(tb)
    Phi = 4*(mpf(3)/8 + tb) + 24*e*(3 + 4*tb) + 128*e**2*tb
    mu0 = d0/(4*Phi + d0)
    Phip = 64*(mpf(21)/8 + 6*tb) + 40960*e*(mpf(3)/4 + tb) + 98304*e**2*tb
    mu0p = d0/(4*Phip + d0)
    def S(mu):   # sum_{m>=1} (2m+1)^2 exp(-mu m), closed form
        x = exp(-mu)
        s0 = x/(1-x); s1 = x/(1-x)**2; s2 = x*(1+x)/(1-x)**3
        return 4*s2 + 4*s1 + s0
    C0 = 2*(1 + 2/pi + 1/sqrt(pi*mu0)); Cms = 1 + C0*3*S(mu0)
    C0p = 2*(1 + 4/pi + 1/sqrt(pi*mu0p)); C1bar = 12 + C0p*36*S(mu0p)
    return Phi, mu0, Cms, Phip, mu0p, C1bar
for (d0, tb, tag) in (("0.05", mpf(1)/16, "printed example (delta_0 = 0.05, tbar = 1/16)"),
                      (mpf(3)/104, 0, "infimum over two-sided windows: delta_0 -> 3/104, c_0 -> 0"),
                      ((mpf(3)/52 - mpf(2)/40)/2, mpf(1)/40, "m_s, c_0 = 1/40: delta_0 <= gamma(-1/40)/2"),
                      ((mpf(3)/52 - mpf(2)/100)/2, mpf(1)/100, "m_s, c_0 = 1/100: delta_0 <= gamma(-1/100)/2"),
                      ((mpf(3)/52 - mpf(42)/13/100)/2, mpf(1)/100, "C_zz, c_0 = 1/100"),
                      ((mpf(3)/52 - mpf(8)/200)/2, mpf(1)/200, "C_2, c_0 = 1/200")):
    Phi, mu0, Cms, Phip, mu0p, C1 = consts(d0, tb)
    print("%-62s delta_0=%.5f Phi*=%.2f mu0=%.3e const(m_s)=%.3e | Phi*'=%.1f mu0'=%.3e C1bar=%.4e" % (
        tag, float(mpf(d0)), float(Phi), float(mu0), float(Cms), float(Phip), float(mu0p), float(C1)))
print()
for (d0, tb, tag) in (("0.05", 0, "delta_0 = 0.05, c_0 -> 0"), ("0.05", mpf(3)/104, "delta_0 = 0.05, c_0 -> 3/104 (largest two-sided window of m_s)"),
                      ("0.05", mpf(1)/56, "delta_0 = 0.05, c_0 -> 1/56 (C_zz)"), ("0.05", mpf(3)/416, "delta_0 = 0.05, c_0 -> 3/416 (C_2)"),
                      (mpf(3)/52, 0, "formal supremum delta_0 -> 3/52, c_0 -> 0")):
    Phi, mu0, Cms, Phip, mu0p, C1 = consts(d0, tb)
    print("%-62s Phi*'=%.1f mu0'=%.3e C1bar=%.4e" % (tag, float(Phip), float(mu0p), float(C1)))
