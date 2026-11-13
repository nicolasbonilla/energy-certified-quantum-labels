"""break_L1.py -- referee attack on Lemma L1 (field lemma). Own code (bl_common), instances the writer did not use.

Part 1  (a), (b) against the FULL 2^n matrix of K = H - mu O - B M built without sectors, on three unbalanced graphs
        (a comb with 8/3 sublattices, a 10-site tree piece of the heavy-hex lattice, a 12-site piece of the d = 3
        patch) and on a frustrated triangle (degenerate sector ground state): every sector q, fields inside,
        outside and exactly at the ends of the interval of (b).
Part 2  heavy-hex n = 19, all 20 sectors, own Lanczos: the writer's four rows, plus two rows beyond the crossing
        (mu = -0.12 Jz, -0.16 Jz): is the sector ground state gapped IN THE SECTOR while no field B makes it the
        global ground state?  (-> the charge gap is sufficient for clustering, not necessary.)
Part 3  a second example of the same kind (ferromagnetic Ising-like chain with a pinned wall).
H = (1/4) sum (XX + YY + Jz ZZ),  O = sum eta_i Z_i,  M = sum Z_i,  sector label q = M = 2 nup - n.
"""
import sys, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from bl_common import heavy_hex, adjacency, two_colour, sector, zvals, build, lowest

t00 = time.time()
TOL = 1e-8
MIS = []


def lower_hull_strict_vertices(pts):
    """strict vertices of the lower convex hull of points (x, y), x increasing (monotone chain, own code)."""
    hull = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) <= 1e-10:      # hull[-1] on or above the chord
                hull.pop()
            else:
                break
        hull.append(p)
    return set(x for x, _ in hull)


def all_sectors(n, edges, eta, Jz, mu, hop=0.5, extra_fields=None):
    out = {}
    for nup in range(n + 1):
        st = sector(n, nup)
        f = -mu * np.asarray(eta, float)
        if extra_fields is not None:
            f = f + np.asarray(extra_fields, float)
        Hoff, diag = build(st, n, edges, hop=hop, jz=Jz, fields=f)
        w, v = lowest(Hoff, diag, k=2)
        E1 = w[1] if len(w) > 1 else np.inf
        out[2 * nup - n] = (w[0], E1, v, st)
    return out


def interval(sec, q):
    E = {k: v[0] for k, v in sec.items()}
    lo = max([(E[q] - E[p]) / (q - p) for p in E if p < q], default=-np.inf)
    hi = min([(E[p] - E[q]) / (p - q) for p in E if p > q], default=np.inf)
    return lo, hi


def charge_gap(sec, q, B):
    E = {k: v[0] for k, v in sec.items()}
    return min(E[p] - E[q] - B * (p - q) for p in E if p != q)


# ------------------------------------------------------------------------------------------------------ Part 1
print("PART 1. (a), (b) against the full-space matrix (no sectors)")


def full_space(n, edges, eta, Jz, mu, hop=0.5):
    st = np.arange(1 << n, dtype=np.int64)
    Hoff, diag = build(st, n, edges, hop=hop, jz=Jz, fields=-mu * np.asarray(eta, float))
    Mdiag = zvals(st, n).sum(axis=0)
    return Hoff, diag, Mdiag


def full_ground(Hoff, diag, Mdiag, B, dense):
    d = diag - B * Mdiag
    if dense:
        w, v = np.linalg.eigh(Hoff.toarray() + np.diag(d))
        w = w[:3]; v0 = v[:, 0]
    else:
        H = (Hoff + sp.diags(d)).tocsr()
        w, v = sla.eigsh(H, k=4, which="SA", tol=1e-12, ncv=48, maxiter=50000)
        o = np.argsort(w); w = w[o][:3]; v0 = v[:, o[0]]
    p = np.abs(v0) ** 2
    m = float(p @ Mdiag)
    var = float(p @ Mdiag ** 2) - m * m
    return w, m, var, v0


graphs = {}
# comb: spine 0-1-2-3-4, two teeth on each of the spine sites 0, 2, 4  (n = 11, sublattices 8 / 3)
E = [(i, i + 1) for i in range(4)]
k = 5
for sp_site in (0, 2, 4):
    for _ in range(2):
        E.append((sp_site, k)); k += 1
graphs["comb 8/3 (n=11)"] = (11, E)
# heavy-hex tree piece: minority centre 0, majority 1,2,3, minority 4,5,6, pendant majority 7,8,9  (n = 10, 6 / 4)
graphs["heavy-hex Y piece 6/4 (n=10)"] = (10, [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 9)])
# 12-site connected piece of the d = 3 patch with unbalanced sublattices (first BFS ball that qualifies)
n19, E19, _ = heavy_hex(3)
adj19 = adjacency(n19, E19)
eta19 = two_colour(n19, E19)
piece = None
for root in range(n19):
    order = [root]; seen = {root}
    for u in order:
        for v in sorted(adj19[u]):
            if v not in seen:
                seen.add(v); order.append(v)
    S = order[:12]
    imb = abs(sum(eta19[v] for v in S))
    if imb >= 2:
        piece = S; break
idx = {v: i for i, v in enumerate(piece)}
Ep = [(idx[a], idx[b]) for a, b in E19 if a in idx and b in idx]
graphs[f"piece of the d=3 patch (n=12, sites {piece})"] = (12, Ep)

ncase = 0
RUN1 = "--skip1" not in sys.argv
for name, (n, E) in (graphs.items() if RUN1 else []):
    eta = two_colour(n, E)
    dense = n <= 10
    t0 = time.time()
    nloc = 0
    for Jz in (1.6, 4.0):
        for mur in (0.0, 0.05, -0.05, -0.15):
            mu = mur * Jz
            sec = all_sectors(n, E, eta, Jz, mu)
            Hoff, diag, Mdiag = full_space(n, E, eta, Jz, mu)
            verts = lower_hull_strict_vertices(sorted((q, sec[q][0]) for q in sec))
            qs = sorted(sec) if n <= 10 else [q for q in sorted(sec) if abs(q) <= 5]
            for q in qs:
                E0, E1, vq, st = sec[q]
                ds = E1 - E0
                lo, hi = interval(sec, q)
                nonempty = lo < hi - 1e-10
                # (b): non-empty interval <=> strict vertex of the lower convex hull
                if nonempty != (q in verts):
                    MIS.append((name, Jz, mur, q, "hull"))
                tests = []
                if nonempty:
                    L = lo if np.isfinite(lo) else hi - 4.0
                    Hh = hi if np.isfinite(hi) else lo + 4.0
                    wdt = Hh - L
                    tests += [(0.5 * (L + Hh), "in"), (L + 1e-3 * wdt, "in"), (Hh - 1e-3 * wdt, "in")]
                    if np.isfinite(lo):
                        tests += [(lo - 1e-3 * wdt - 1e-6, "out")]
                        if dense:
                            tests += [(lo, "edge")]
                    if np.isfinite(hi):
                        tests += [(hi + 1e-3 * wdt + 1e-6, "out")]
                        if dense:
                            tests += [(hi, "edge")]
                else:
                    tests += [(0.5 * (lo + hi), "out"), (0.0, "out")]
                for B, kind in tests:
                    dc = charge_gap(sec, q, B)
                    w, m, var, v0 = full_ground(Hoff, diag, Mdiag, B, dense)
                    gap = w[1] - w[0]
                    unique_in_q = gap > TOL and abs(m - q) < 1e-6 and var < 1e-6
                    cond_i = ds > TOL and dc > TOL
                    ok = True
                    if kind == "edge":
                        ok = (abs(dc) < 1e-9) and (gap < 1e-8)                     # degenerate with another sector
                    elif cond_i != unique_in_q:
                        ok = False
                    elif cond_i:
                        ok = abs(gap - min(ds, dc)) < 1e-7
                        # the full ground vector is the sector ground vector
                        emb = np.zeros(1 << n); emb[st] = vq
                        ok = ok and abs(abs(emb @ v0) - 1) < 1e-6
                    if not ok:
                        MIS.append((name, Jz, mur, q, B, kind, ds, dc, gap, m))
                    ncase += 1; nloc += 1
    print(f"   {name}: {nloc} comparisons [{time.time() - t0:.1f} s]")
# frustrated triangle: sector nup = 1 has a twofold degenerate ground state -> (i) fails; (ii) must fail for every B
n, E = 3, [(0, 1), (1, 2), (0, 2)]
for Jz in ((1.0, 4.0) if RUN1 else ()):
    Hoff, diag, Mdiag = full_space(n, E, [0, 0, 0], Jz, 0.0)
    st = sector(3, 1)
    Ho, dg = build(st, 3, E, jz=Jz)
    ws = np.linalg.eigvalsh(Ho.toarray() + np.diag(dg))
    for B in np.linspace(-3, 3, 25):
        w, m, var, v0 = full_ground(Hoff, diag, Mdiag, B, True)
        unique_in_q = (w[1] - w[0] > TOL) and abs(m - (-1)) < 1e-6 and var < 1e-6
        if unique_in_q or ws[1] - ws[0] > 1e-9:
            MIS.append(("triangle", Jz, B))
        ncase += 1
if RUN1:
    print(f"   frustrated triangle, sector M = -1 (degenerate sector ground state, splitting {ws[1] - ws[0]:.1e}): "
          f"never the unique ground state of K for 25 fields x 2 couplings")
print(f"   TOTAL comparisons {ncase}, mismatches {len(MIS)}")
for m in MIS[:10]:
    print("   MISMATCH", m)

# ------------------------------------------------------------------------------------------------------ Part 2
print("\nPART 2. heavy-hex n = 19, all 20 sectors (own Lanczos)")
n, E, _ = heavy_hex(3)
eta = np.array(two_colour(n, E), float)
nup0 = int((eta > 0).sum())
cache = {}
for nup in range(n + 1):
    st = sector(n, nup)
    z = zvals(st, n)
    Hoff, _ = build(st, n, E, hop=0.5, jz=0.0)
    dZZ = np.zeros(len(st))
    for a, b in E:
        dZZ += 0.25 * z[a] * z[b]
    dO = eta @ z
    cache[nup] = (st, Hoff, dZZ, dO)
print(f"   matrices built [{time.time() - t00:.0f} s]; Neel sector nup = {nup0} (M = {2 * nup0 - n}), dim {len(cache[nup0][0])}")


def hh_sectors(Jz, mu):
    out = {}
    sym = (mu == 0.0)
    for nup in range(n + 1):
        if sym and nup > n // 2 and nup != nup0:          # fixed after the first run: the Neel sector is always computed
            out[2 * nup - n] = out[n - 2 * nup][:2] + (None,)
            continue
        st, Hoff, dZZ, dO = cache[nup]
        w, v = lowest(Hoff, Jz * dZZ - mu * dO, k=2, tol=1e-12)
        out[2 * nup - n] = (w[0], w[1] if len(w) > 1 else np.inf, v)
    return out


print("   Jz   mu/Jz  sector gap   m_s       C_1     interval of (b) in units of Jz       max_B min(Ds,Dc)  at B/Jz   Dc at 3Jz/8")
q0 = 2 * nup0 - n
for Jz, mur in ((1.6, 0.0), (4.0, 0.0), (4.0, -0.04), (4.0, -0.08), (4.0, -0.12), (4.0, -0.16)):
    t0 = time.time()
    mu = mur * Jz
    sec = hh_sectors(Jz, mu)
    E0, E1, v = sec[q0]
    ds = E1 - E0
    lo, hi = interval({k: (x[0],) for k, x in sec.items()}, q0)
    st = cache[nup0][0]
    z = zvals(st, n)
    p = v * v
    mz = z @ p
    corr = (z * p) @ z.T - np.outer(mz, mz)
    C1 = np.abs(corr).sum(axis=1).max()
    ms = float(eta @ mz) / n
    if lo < hi:
        Bs = np.linspace(lo, hi, 4001)
        g = np.array([min(ds, charge_gap({k: (x[0],) for k, x in sec.items()}, q0, B)) for B in Bs])
        kbest = int(np.argmax(g))
        gtxt = f"{g[kbest]:.5f}          {Bs[kbest] / Jz:.4f}"
        d38 = charge_gap({k: (x[0],) for k, x in sec.items()}, q0, 0.375 * Jz)
        itxt = f"({lo / Jz:.6f}, {hi / Jz:.6f})"
    else:
        gtxt = "none                   "
        d38 = charge_gap({k: (x[0],) for k, x in sec.items()}, q0, 0.375 * Jz)
        itxt = f"EMPTY (B- = {lo / Jz:.4f} > B+ = {hi / Jz:.4f})"
        # best possible charge gap over all B (it is <= 0)
        Bs = np.linspace(min(lo, hi) - 1, max(lo, hi) + 1, 4001)
        dcb = max(charge_gap({k: (x[0],) for k, x in sec.items()}, q0, B) for B in Bs)
        itxt += f"; max_B Dc = {dcb:.4f}"
    print(f"   {Jz:3.1f}  {mur:+.2f}  {ds:10.5f}  {ms:+.4f}  {C1:7.3f}   {itxt:40s} {gtxt}   {d38:+.5f}   [{time.time() - t0:.0f} s]")
    # distance dependence of the connected correlations in the sector ground state
    adj = adjacency(n, E)
    dist = np.full((n, n), -1)
    for s0 in range(n):
        dist[s0, s0] = 0; qq = [s0]
        for u in qq:
            for w_ in adj[u]:
                if dist[s0, w_] < 0:
                    dist[s0, w_] = dist[s0, u] + 1; qq.append(w_)
    prof = [float(np.abs(corr[dist == r]).max()) for r in range(1, 9)]
    print("        max |<Z_i Z_j>_c| at graph distance 1..8: " + " ".join(f"{x:.1e}" for x in prof))

# ------------------------------------------------------------------------------------------------------ Part 3
print("\nPART 3. ferromagnetic Ising-like open chain with boundary fields: a pinned wall in the sector M = 0")
for n3 in (12, 16):
    E3 = [(i, i + 1) for i in range(n3 - 1)]
    f = np.zeros(n3); f[0] = -1.0; f[-1] = +1.0            # field term  -Z_0 + Z_{n-1}: up on the left, down on the right
    sec = {}
    for nup in range(n3 + 1):
        st = sector(n3, nup)
        Hoff, diag = build(st, n3, E3, hop=0.5, jz=-4.0, fields=f)
        w, v = lowest(Hoff, diag, k=2)
        sec[2 * nup - n3] = (w[0], w[1] if len(w) > 1 else np.inf, v, st)
    E0, E1, v, st = sec[0]
    lo, hi = interval(sec, 0)
    Bs = np.linspace(-3, 3, 6001)
    dcb = max(charge_gap(sec, 0, B) for B in Bs)
    z = zvals(st, n3); p = v * v; mz = z @ p
    corr = (z * p) @ z.T - np.outer(mz, mz)
    C1 = np.abs(corr).sum(axis=1).max()
    far = max(abs(corr[i, j]) for i in range(n3) for j in range(n3) if abs(i - j) >= 4)
    print(f"   n = {n3}: sector gap {E1 - E0:.4f}; B- = {lo:.5f}, B+ = {hi:.5f} -> interval {'EMPTY' if lo >= hi else 'non-empty'}; "
          f"max_B charge gap = {dcb:.5f}; C_1 = {C1:.4f}; max |<Z_i Z_j>_c| for |i-j| >= 4: {far:.2e}")
print(f"\ntotal time {time.time() - t00:.0f} s; mismatches in Part 1: {len(MIS)}")
