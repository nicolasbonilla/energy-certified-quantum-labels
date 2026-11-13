"""v_item1c_rows.py -- verifier V, item 1 (complement): the remaining n = 19 rows quoted in "Exact checks" of
L1_field_lemma (Jz = 1.6, mu = 0; Jz = 4, mu = -0.12 Jz, -0.16 Jz), with my own code: interval of part (b),
largest global gap max_B min(Delta_s, Delta_c(B)) and the field where it is reached.  Output: v_item1c_out.txt"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v_common import patch, sector_states, zmat, hop_matrix, lowest
import numpy as np
t0 = time.time()
lines = []
def say(s=""):
    print(s, flush=True); lines.append(s)
n, E, names, eta = patch(3)
nupN = int((eta > 0).sum())
secs = {}
for q in range(n + 1):
    st = sector_states(n, q); z = zmat(st, n)
    secs[q] = (hop_matrix(st, E, 0.5), sum(z[:, i] * z[:, j] for i, j in E), z @ eta, z)
say("   Jz    mu/Jz   sector gap    m_s      C_1     B-/Jz       B+/Jz      max_B min(Ds,Dc)   at B/Jz     Dc at 3Jz/8")
for Jz, x in ((1.6, 0.0), (4.0, 0.0), (4.0, -0.04), (4.0, -0.12), (4.0, -0.16)):
    e0 = {}
    for q, (K, zz, stag, z) in secs.items():
        w, v = lowest(K, 0.25 * Jz * zz - (x * Jz) * stag, k=2 if q == nupN else 1)
        e0[2 * q - n] = w[0]
        if q == nupN:
            gap = w[1] - w[0]; psi = v[:, 0]; zN = z
    M0 = 3
    lo = max((e0[M0] - e0[p]) / (M0 - p) for p in e0 if p < M0)
    hi = min((e0[p] - e0[M0]) / (p - M0) for p in e0 if p > M0)
    ps = [p for p in e0 if p != M0]
    cand = {lo, hi, 0.375 * Jz}
    for a in ps:
        for b in ps:
            if a < b:
                cand.add((e0[b] - e0[a]) / (b - a))
    def Dc(B):
        return min(e0[p] - e0[M0] - B * (p - M0) for p in ps)
    # max_B min(Ds, Dc(B)): Dc concave; if max Dc >= Ds the minimum is Ds on an interval; report the B maximizing Dc
    best = max(cand, key=Dc)
    p_ = psi * psi
    mz = zN.T @ p_
    corr = (zN * p_[:, None]).T @ zN - np.outer(mz, mz)
    say(f"   {Jz:.1f}   {x:+.2f}   {gap:9.5f}   {mz @ eta / n:+.4f}  {np.abs(corr).sum(axis=1).max():6.3f}   {lo/Jz:.6f}   {hi/Jz:.6f}   "
        f"{'EMPTY' if lo >= hi else 'non-empty'}   {min(gap, Dc(best)):+.5f}      {best/Jz:.4f}     {Dc(0.375*Jz):+.5f}   [{time.time()-t0:.0f} s]")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item1c_out.txt"), "w").write("\n".join(lines) + "\n")
