"""Check 4 -- (a) how much of the 'certified' side is due to the sector assumption, and
               (b) a miniature, independent replication of the truncation (sampled-support + Rayleigh-Ritz) bias.

(a) Ferrimagnetic XXZ comb, n = 12 (8 majority, 4 minority sites), Jz = 1.6 and 4.0, H = 1/4 sum (XX+YY+Jz ZZ).
    Information limit of m_s (eta = +1 on the majority colour) and of the edge average C_zz, with the window
    restricted to the Neel sector (n_up = 8, as the paper assumes) and without any sector restriction.
(b) Same comb in its sector at Jz = 1.2, 1.6, 4.0: exact ground state psi; for subspace sizes D we keep
    (i) the D most probable configurations, (ii) the unique configurations of M perfect samples of |psi|^2;
    we report the signed m_s bias of the projected ground state (support only), of the lowest Rayleigh-Ritz vector
    in that subspace (what sample-based diagonalization returns), and of the multiplicity-weighted sample mean.
Seconds.
"""
import numpy as np
import scipy.sparse as sp

import edlib as ed

rng = np.random.default_rng(11)
n, edges, col = ed.comb(8)
nmaj = int((col == 0).sum())
eta = np.where(col == 0, 1.0, -1.0)
print("comb: n=%d, majority %d, minority %d, edges %d" % (n, nmaj, n - nmaj, len(edges)))

print("\n(a) window of m_s and C_zz with and without the sector restriction")
full = ed.basis(n)
sec = ed.basis(n, nmaj)
for Jz in (1.6, 4.0):
    out = {}
    for name, st in (("sector n_up=%d" % nmaj, sec), ("no sector", full)):
        H = ed.xxz(n, edges, Jz, st)
        Z = ed.zvals(n, st)
        ms = Z @ eta / n
        czz = np.mean([Z[:, i] * Z[:, j] for (i, j) in edges], axis=0)
        w, v = ed.ground(H, k=3)
        E0 = w[0]
        for de in (1e-3, 1e-2):
            for lab, Od in (("m_s", ms), ("C_zz", czz)):
                lo, hi = ed.two_sided(H, Od, n * de, E0)
                out[(name, de, lab)] = (lo, hi)
        out[(name, "spec")] = w[:3] - E0
    for name in ("sector n_up=%d" % nmaj, "no sector"):
        print("  Jz=%.1f %-15s lowest levels above E0: %s" % (Jz, name, np.round(out[(name, "spec")], 5)))
        for de in (1e-3, 1e-2):
            print("     de=%.0e  m_s window [%+.4f, %+.4f] (width %.4f)   C_zz window [%+.4f, %+.4f] (width %.4f)" % (
                de, *out[(name, de, "m_s")], out[(name, de, "m_s")][1] - out[(name, de, "m_s")][0],
                *out[(name, de, "C_zz")], out[(name, de, "C_zz")][1] - out[(name, de, "C_zz")][0]))

print("\n(b) truncation bias in the sector (signed m_s error; + = over-ordered)")
st = sec
Z = ed.zvals(n, st)
ms_op = Z @ eta / n
for Jz in (1.2, 1.6, 4.0):
    H = ed.xxz(n, edges, Jz, st).toarray()
    w, v = np.linalg.eigh(H)
    psi = v[:, 0] * np.sign(v[np.argmax(np.abs(v[:, 0])), 0])
    p = psi ** 2
    mref = p @ ms_op
    order = np.argsort(-p)
    print("  Jz=%.1f  dim=%d  m_s(GS)=%.4f" % (Jz, len(st), mref))

    Hs = sp.csr_matrix(H)

    def rr(idx):
        h = Hs[idx][:, idx]
        ww, vv = ed.ground(h, k=1)
        c = vv[:, 0]
        return (c ** 2) @ ms_op[idx], ww[0] - w[0]

    def proj(idx):
        c = psi[idx]
        return (c ** 2) @ ms_op[idx] / (c @ c), 1 - c @ c

    for D in (10, 30, 60, 120, 240):
        idx = order[:D]
        mp, miss = proj(idx)
        mr, de_ = rr(idx)
        print("     top-%3d  captured weight %.3f  support-only %+.4f  Rayleigh-Ritz %+.4f  (RR eps/gap %.2f)" % (
            D, 1 - miss, mp - mref, mr - mref, de_ / (w[1] - w[0])))
    for M in (30, 100, 300, 1000):
        reps = []
        for r in range(30):
            smp = rng.choice(len(st), size=M, p=p)
            idx, cnt = np.unique(smp, return_counts=True)
            mp, _ = proj(idx)
            mr, _ = rr(idx)
            mean = (cnt @ ms_op[idx]) / M
            reps.append((len(idx), mp - mref, mr - mref, mean - mref))
        reps = np.array(reps)
        print("     M=%4d shots (30 repetitions): D=%5.1f  support-only %+.4f  RR %+.4f (min %+.4f, frac>0 %.2f)  sample mean %+.4f +- %.4f" % (
            M, reps[:, 0].mean(), reps[:, 1].mean(), reps[:, 2].mean(), reps[:, 2].min(), (reps[:, 2] > 0).mean(),
            reps[:, 3].mean(), reps[:, 3].std() / np.sqrt(len(reps))))
