"""v_item1_sector.py -- verifier V, item 1: part (d) of L1_field_lemma_v2.tex (the sector gap suffices for observables
that commute with the charge).  Own code.

PART A (statics, sectors up to n = 19): sector gap against the best charge gap over all uniform fields B,
        C_1 = max_i sum_j |<Z_i;Z_j>|, decay with distance.
   A1  the referee's example: ferromagnetic Ising-like open chain, Jz = -4, end fields -1, +1, sector M = 0
   A2  mine: chain of ferromagnetic dimers (pair binding) with a step field; the sector M = 0 holds one unpaired
       spin; the charge gap is NEGATIVE by about 1.5 for every field B
   A3  mine: the paper's own model, heavy-hex n = 19, Jz = 4, opposing tilt mu: window of mu where no field B makes
       the Neel-sector ground state the global ground state although the sector gap is open
   A4  mine: open antiferromagnetic chain of odd length (sector M = 1), opposing tilt
PART B (dynamics; a test with teeth): the proof of Nachtergaele-Sims Theorem 2, read with the spectral supports
        of B'Omega and B'*Omega only, gives for every alpha > 0 (my derivation, see report)
            |<A B'>| <= (1/2)(|A psi||B'* psi| + |A* psi||B' psi|) exp(-gamma^2/(4 alpha))
                         + (1/2 pi) int |[A, tau_t(B')]| exp(-alpha t^2)/|t| dt                              (T)
        with gamma = SECTOR gap if (d) is right.  Both sides are computed exactly (commutator norm over the whole
        Hilbert space, all sectors).  gamma_max = the largest gamma for which (T) still holds for every alpha:
        (d) requires gamma_max >= sector gap.  A violation would refute (d).
Output: v_item1_sector_out.txt
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v_common import patch, adjacency, bfs_dist, sector_states, zmat, hop_matrix, lowest
import numpy as np

t00 = time.time()
lines = []
fails = 0


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def sector_problem(n, E, hop, jz, fields, nup, k=2):
    st = sector_states(n, nup)
    z = zmat(st, n)
    amps = hop if np.ndim(hop) else [hop] * len(E)
    jzs = jz if np.ndim(jz) else [jz] * len(E)
    K = hop_matrix(st, E, amps=amps)
    diag = sum(0.25 * g * z[:, i] * z[:, j] for g, (i, j) in zip(jzs, E))
    if fields is not None:
        diag = diag + z @ np.asarray(fields, float)
    w, v = lowest(K, diag, k=k)
    return w, v, z


def statics(name, n, E, hop, jz, fields, nup, dist, verbose=True):
    """sector gap, charge interval (B-, B+), best charge gap over B, C_1, decay profile"""
    e0 = {}
    keep = None
    for q in range(n + 1):
        w, v, z = sector_problem(n, E, hop, jz, fields, q, k=2 if q == nup else 1)
        e0[2 * q - n] = w[0]
        if q == nup:
            keep = (w, v, z)
    w, v, z = keep
    M0 = 2 * nup - n
    lo = max([(e0[M0] - e0[p]) / (M0 - p) for p in e0 if p < M0], default=-np.inf)
    hi = min([(e0[p] - e0[M0]) / (p - M0) for p in e0 if p > M0], default=np.inf)
    # Delta_c(B) = min_p [e0(p) - e0(M0) - B (p - M0)] is concave piecewise linear; its maximum is at a breakpoint
    cand = set()
    ps = [p for p in e0 if p != M0]
    for a in ps:
        for b in ps:
            if a < b and (a - M0) != (b - M0):
                cand.add(((e0[b] - e0[M0]) - (e0[a] - e0[M0])) / ((b - M0) - (a - M0)))
    cand |= {lo, hi, 0.0}
    cand = [c for c in cand if np.isfinite(c)]
    dc = max(min(e0[p] - e0[M0] - B * (p - M0) for p in ps) for B in cand)
    psi = v[:, 0]
    p = psi * psi
    mz = z.T @ p
    corr = (z * p[:, None]).T @ z - np.outer(mz, mz)
    C1 = np.abs(corr).sum(axis=1).max()
    rmax = int(dist.max())
    prof = [max(abs(corr[i, j]) for i in range(n) for j in range(n) if dist[i, j] == r) for r in range(1, min(rmax, 8) + 1)]
    out = dict(gap=w[1] - w[0], lo=lo, hi=hi, dc=dc, C1=C1, prof=prof, mz=mz, e0=e0, corr=corr)
    if verbose:
        say(f"   {name}: sector gap {out['gap']:.5f}; B- = {lo:+.4e}, B+ = {hi:+.4e} -> interval "
            f"{'non-empty' if lo < hi else 'EMPTY'}; best charge gap over all B = {dc:+.3e}; C_1 = {C1:.4f}")
        say("        max |<Z_i;Z_j>| at distance 1.." + str(len(prof)) + ": " + " ".join(f"{x:.1e}" for x in prof))
    return out


# ================================================================================================================ A
say("PART A. statics")
say("A1. referee's example: ferromagnetic Ising-like open chain, Jz = -4, hop 1/2, fields -1 (first site), +1 (last), M = 0")
for n in (8, 12, 16):
    E = [(i, i + 1) for i in range(n - 1)]
    f = np.zeros(n)
    f[0], f[-1] = -1.0, 1.0
    D = np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
    r = statics(f"n = {n}", n, E, 0.5, -4.0, f, n // 2, D)
    nPhi = 8 * 2 * (4 + 2) * np.e + 4 * 1.0
    say(f"        rate of the published bound with lambda = 1: with the sector gap m = {r['gap']/(4*nPhi + r['gap']):.2e}; "
        f"with the best global gap m <= {max(r['dc'], 0)/(4*nPhi):.1e}")

say("\nA2. mine: ferromagnetic dimers (intra: hop 1/2, Jz = -4; inter: hop 0.2, Jz = 0), fields -1 on the left dimers,")
say("    0 on the middle dimer, +1 on the right dimers; sector M = 0 (one unpaired spin on the middle dimer)")


def dimer_model(L, tp=0.2):
    n = 2 * L
    E, hop, jz = [], [], []
    for k in range(L):
        E.append((2 * k, 2 * k + 1)); hop.append(0.5); jz.append(-4.0)
        if k < L - 1:
            E.append((2 * k + 1, 2 * k + 2)); hop.append(tp); jz.append(0.0)
    f = np.zeros(n)
    mid = (L - 1) // 2
    for k in range(L):
        if k < mid:
            f[2 * k] = f[2 * k + 1] = -1.0
        elif k > mid:
            f[2 * k] = f[2 * k + 1] = +1.0
    return n, E, hop, jz, f


for L in (3, 5, 7, 9):
    n, E, hop, jz, f = dimer_model(L)
    D = np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
    r = statics(f"n = {n}", n, E, hop, jz, f, L, D)
    say(f"        E0(M=+2) - E0(0) = {r['e0'][2]-r['e0'][0]:+.4f}, E0(M=-2) - E0(0) = {r['e0'][-2]-r['e0'][0]:+.4f}")

say("\nA3. mine: the paper's model, heavy-hex n = 19, Jz = 4, family H - mu O - B M with O = sum eta Z, opposing tilt mu < 0")
n, E, names, eta = patch(3)
Dhh = bfs_dist(n, E)
Jz = 4.0
nupN = int((eta > 0).sum())
say("    mu/Jz    sector gap    m_s      C_1     B-/Jz      B+/Jz     interval   best charge gap")
rowsA3 = []
for x in (0.0, -0.04, -0.048, -0.050, -0.0505, -0.051, -0.0514, -0.0518, -0.052, -0.0522, -0.0524, -0.053, -0.08):
    r = statics("", n, E, 0.5, Jz, -(x * Jz) * eta, nupN, Dhh, verbose=False)
    ms = float(r["mz"] @ eta / n)
    rowsA3.append((x, r["gap"], ms, r["C1"], r["lo"] / Jz, r["hi"] / Jz, r["dc"]))
    say(f"    {x:+.4f}   {r['gap']:9.5f}   {ms:+.4f}  {r['C1']:6.3f}   {r['lo']/Jz:.6f}   {r['hi']/Jz:.6f}   "
        f"{'non-empty' if r['lo'] < r['hi'] else 'EMPTY    '}  {r['dc']:+.4f}    [{time.time()-t00:.0f} s]")
win = [row for row in rowsA3 if row[4] >= row[5] and row[2] > 0.5]
say(f"    tilts with EMPTY interval and Neel-like sector ground state (m_s > 0.5): "
    + ", ".join(f"mu = {row[0]:+.4f} Jz (sector gap {row[1]:.4f}, C_1 = {row[3]:.3f})" for row in win))

say("\nA4. mine: open antiferromagnetic XXZ chain of odd length, sector M = +1 (Neel), opposing tilt; Jz = 4")
for n4 in (11, 15):
    E4 = [(i, i + 1) for i in range(n4 - 1)]
    eta4 = np.array([1 if i % 2 == 0 else -1 for i in range(n4)])
    D4 = np.abs(np.subtract.outer(np.arange(n4), np.arange(n4)))
    say(f"    n = {n4}:  mu/Jz    sector gap    m_s      C_1     B-/Jz      B+/Jz     interval   best charge gap")
    for x in (0.0, -0.02, -0.04, -0.05, -0.06, -0.07, -0.08, -0.10):
        r = statics("", n4, E4, 0.5, 4.0, -(x * 4.0) * eta4, (n4 + 1) // 2, D4, verbose=False)
        ms = float(r["mz"] @ eta4 / n4)
        say(f"              {x:+.4f}   {r['gap']:9.5f}   {ms:+.4f}  {r['C1']:6.3f}   {r['lo']/4:.6f}   {r['hi']/4:.6f}   "
            f"{'non-empty' if r['lo'] < r['hi'] else 'EMPTY    '}  {r['dc']:+.4f}")


# ================================================================================================================ B
say("\nPART B. the inequality (T) with gamma = sector gap, exact on both sides")


def test_T(name, n, E, hop, jz, fields, nup, pairs, dt=0.05, tmax=20.0):
    global fails
    amps = hop if np.ndim(hop) else [hop] * len(E)
    jzs = jz if np.ndim(jz) else [jz] * len(E)
    secs = []
    for q in range(n + 1):
        st = sector_states(n, q)
        z = zmat(st, n)
        H = hop_matrix(st, E, amps=amps).toarray()
        diag = sum(0.25 * g * z[:, i] * z[:, j] for g, (i, j) in zip(jzs, E))
        if fields is not None:
            diag = diag + z @ np.asarray(fields, float)
        H[np.arange(len(st)), np.arange(len(st))] += diag
        w, V = np.linalg.eigh(H)
        secs.append((w, V, z))
    w, V, z = secs[nup]
    psi = V[:, 0]
    gap = w[1] - w[0]
    e0min = min(s[0][0] for s in secs)
    p = psi * psi
    mz = z.T @ p
    ts = np.arange(0.0, tmax + dt / 2, dt)
    ts[0] = 1e-5
    js = sorted(set(j for _, j in pairs))
    iset = {j: sorted(set(i for i, jj in pairs if jj == j)) for j in js}
    N = {pr: np.zeros(len(ts)) for pr in pairs}          # full-space commutator norm
    Nq = {pr: np.zeros(len(ts)) for pr in pairs}         # restricted to the sector of psi
    for qi, (wq, Vq, zq) in enumerate(secs):
        if len(wq) < 2:
            continue
        dw = wq[:, None] - wq[None, :]
        for j in js:
            Mj = Vq.T @ (zq[:, j][:, None] * Vq)
            for k, t in enumerate(ts):
                W = Vq @ ((Mj * np.exp(1j * dw * t)) @ Vq.T)
                for i in iset[j]:
                    up = zq[:, i] > 0
                    if up.all() or (~up).all():
                        continue
                    val = 2 * np.linalg.norm(W[np.ix_(up, ~up)], 2)
                    if val > N[(i, j)][k]:
                        N[(i, j)][k] = val
                    if qi == nup:
                        Nq[(i, j)][k] = val
    alphas = np.exp(np.linspace(np.log(0.08), np.log(60.0), 80))
    say(f"   {name}: n = {n}, sector M = {2*nup-n}, sector gap {gap:.4f}; lowest level of the whole space lies "
        f"{w[0]-e0min:.4f} below the sector ground state" if w[0] - e0min > 1e-9 else
        f"   {name}: n = {n}, sector M = {2*nup-n}, sector gap {gap:.4f}; the sector ground state is the lowest level at B = 0")
    say("      pair (i,j)   |<Z_i;Z_j>|     min_alpha RHS(T)   RHS/|corr|   gamma_max/gap (full-space norm)   (sector norm)")
    wts = np.ones(len(ts))
    wts[1:-1:2] = 4
    wts[2:-1:2] = 2
    wts *= dt / 3
    for (i, j) in pairs:
        c = abs(float((z[:, i] * z[:, j]) @ p - mz[i] * mz[j]))
        pref = np.sqrt(max(1 - mz[j] ** 2, 0.0))          # |Z_i psi| |(Z_j - <Z_j>) psi|
        outs = []
        for NN in (N[(i, j)], Nq[(i, j)]):
            II = np.array([(NN / ts * np.exp(-a * ts ** 2)) @ wts / np.pi for a in alphas])
            rhs = pref * np.exp(-gap ** 2 / (4 * alphas)) + II
            ok = c <= rhs.min() * (1 + 1e-9)
            need = c - II
            gm = np.inf
            for a, nd in zip(alphas, need):
                if nd > 0:
                    if nd >= pref:
                        gm = 0.0
                    else:
                        gm = min(gm, np.sqrt(4 * a * np.log(pref / nd)))
            outs.append((rhs.min(), ok, gm))
        if not outs[0][1]:
            fails += 1
        say(f"      ({i:2d},{j:2d})      {c:.4e}      {outs[0][0]:.4e}      {outs[0][0]/c if c > 0 else np.inf:9.2f}"
            f"      {outs[0][2]/gap:8.3f} {'ok' if outs[0][1] else 'VIOLATED'}"
            f"                 {outs[1][2]/gap:8.3f} {'ok' if outs[1][1] else 'VIOLATED'}")


# B1: pinned wall, n = 10
n = 10
E = [(i, i + 1) for i in range(n - 1)]
f = np.zeros(n)
f[0], f[-1] = -1.0, 1.0
test_T("B1 pinned wall (referee's example)", n, E, 0.5, -4.0, f, n // 2, [(4, 5), (4, 6), (3, 6), (4, 7), (2, 7)])
say(f"   [{time.time()-t00:.0f} s]")
# B2: dimers, n = 10, stronger inter-dimer hopping so that correlations are sizeable
n, E, hop, jz, f = dimer_model(5, tp=0.35)
test_T("B2 ferromagnetic dimers, inter-dimer hop 0.35", n, E, hop, jz, f, 5, [(4, 5), (3, 4), (3, 6), (2, 5), (2, 7), (1, 8)])
say(f"   [{time.time()-t00:.0f} s]")
# B3: odd antiferromagnetic chain n = 9, Jz = 2, opposing tilt chosen where no field B works (scan first)
n = 9
E = [(i, i + 1) for i in range(n - 1)]
eta9 = np.array([1 if i % 2 == 0 else -1 for i in range(n)])
D9 = np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
pick = None
say("   B3 scan (open antiferromagnetic chain n = 9, Jz = 2, sector M = +1, family H - mu O):")
for x in (0.0, -0.02, -0.04, -0.06, -0.08, -0.10, -0.12, -0.14):
    r = statics("", n, E, 0.5, 2.0, -(x * 2.0) * eta9, 5, D9, verbose=False)
    ms = float(r["mz"] @ eta9 / n)
    emp = r["lo"] >= r["hi"]
    say(f"      mu = {x:+.2f} Jz: sector gap {r['gap']:.4f}, m_s = {ms:+.4f}, C_1 = {r['C1']:.3f}, interval "
        f"{'EMPTY' if emp else 'non-empty'} (B- = {r['lo']:.4f}, B+ = {r['hi']:.4f}), best charge gap {r['dc']:+.4f}")
    if emp and ms > 0.3 and pick is None:
        pick = x
if pick is None:
    pick = -0.06
test_T(f"B3 antiferromagnetic chain, Jz = 2, tilt mu = {pick:+.2f} Jz", n, E, 0.5, 2.0, -(pick * 2.0) * eta9, 5,
       [(4, 5), (4, 6), (3, 6), (2, 6), (1, 7), (0, 8)])
say(f"   [{time.time()-t00:.0f} s]")
# B4: same chain without tilt (sector ground state degenerate with M = -1 at B = 0): a case with large correlations
test_T("B4 antiferromagnetic chain, Jz = 1.2, no tilt", n, E, 0.5, 1.2, None, 5, [(4, 5), (4, 6), (3, 6), (2, 6), (1, 7), (0, 8)])

say(f"\nviolations of (T) with the full-space norm: {fails}   [{time.time()-t00:.0f} s]")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item1_sector_out.txt"), "w") as fo:
    fo.write("\n".join(lines) + "\n")
