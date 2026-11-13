"""break_PD.py -- referee attack on Proposition D (domain walls). Own code; regions and models the writer did not use.

Part A  (a)-(c) on: an open 3 x 4 square lattice pinned on one column (column blocks, an interior block, 2 x 2 corner
        blocks with two different reflections, a single bond); an open frustrated J1-J2 XXZ chain (reflection of an
        end segment; three terms cross); an odd chain pinned by its sector with an INTERIOR segment.
        Control: a permutation that does not preserve H_R.
Part B  the added claim for the heavy-hex patches.
        B1  d = 3: ALL 75 581 balanced regions; which have a sublattice-exchanging automorphism of the induced graph
            (VF2); number of crossing bonds against |R|/2 - 2(d-1) and against |R|.
        B2  d = 5, 7, 9: integer programme (HiGHS) over a RELAXATION of the admissible regions (balanced; a
            degree-3 minority site of R has at most two neighbours in R): minimum of crossing/|R| and of
            crossing - |R|/2.
        B3  n = 19, Jz = 4: the exact cost E*_n(-c) of lowering m_s, against the best bound the proposition can give.
"""
import itertools, time
import numpy as np
import scipy.sparse as sp
from bl_common import heavy_hex, adjacency, two_colour, sector, zvals, build, lowest, expect, perm_op, conj_cost

t00 = time.time()
rng = np.random.default_rng(11)
VIOL = []


def spread(J, Jz):
    return J * max((Jz + 1) / 2.0, 1.0)


def analyse(name, n, nup, edges, hop, jz, fields, eta, regions, Jz_label):
    st = sector(n, nup)
    Hoff, diag = build(st, n, edges, hop=hop, jz=jz, fields=fields)
    w, psi = lowest(Hoff, diag, k=2)
    E0 = w[0]
    z = zvals(st, n)
    Od = np.asarray(eta, float) @ z
    oGS = float(psi * psi @ Od) / n
    hopa = np.broadcast_to(np.asarray(hop, float), (len(edges),))
    jza = np.broadcast_to(np.asarray(jz, float), (len(edges),))
    print(f"{name}: dim {len(st)}, sector gap {w[1] - w[0]:.4f}, m_s(GS) = {oGS:+.4f}")
    cache = {"v": psi}

    def Hfun(mu):                                   # sign = -1:  H + mu O
        ww, v = lowest(Hoff, diag + mu * Od, k=2, v0=cache["v"], dense_below=400)
        cache["v"] = v
        return ww[0], float(np.abs(v) ** 2 @ Od) / n, expect(Hoff, diag, v)
    for rname, R, perm_R, expect_ok in regions:
        Rs = set(R)
        perm = list(range(n))
        for a, b in perm_R.items():
            perm[a] = b
        t = perm_op(st, n, perm)
        inside = [k for k, (a, b) in enumerate(edges) if a in Rs and b in Rs]
        crossing = [k for k, (a, b) in enumerate(edges) if (a in Rs) != (b in Rs)]
        kappa = sum(2 * hopa[k] * max((jza[k] / (2 * hopa[k]) + 1) / 2.0, 1.0) for k in crossing)
        # invariance of H_R (bonds inside R; on-site fields inside R must be invariant too)
        HRo, HRd = build(st, n, [edges[k] for k in inside], hop=hopa[inside], jz=jza[inside],
                         fields=None if fields is None else [fields[i] if i in Rs else 0.0 for i in range(n)])
        v = rng.standard_normal(len(st))
        w1 = HRo @ v[t] + HRd * v[t]
        out = np.zeros(len(st)); out[t] = w1
        inv = np.abs(out - (HRo @ v + HRd * v)).max()
        swap_ok = all(eta[perm[i]] == -eta[i] for i in R)
        u = np.zeros(len(st)); u[t] = psi
        dE = expect(Hoff, diag, u) - E0
        o_new = float(u * u @ Od) / n
        cR = 2.0 / n * float(psi * psi @ (np.asarray([eta[i] if i in Rs else 0 for i in range(n)], float) @ z))
        worst = 0.0
        for rep in range(8):
            x = rng.standard_normal(len(st)) if rep < 4 else psi + 0.4 * rng.standard_normal(len(st)) / np.sqrt(len(st)) * 5
            x /= np.linalg.norm(x)
            y = np.zeros(len(st)); y[t] = x
            worst = max(worst, abs(expect(Hoff, diag, y) - expect(Hoff, diag, x)))
        line = (f"   {rname:38s} |R|={len(R):2d} crossing={len(crossing)} kappa={kappa:6.3f} H_R-invariance err {inv:.0e} swaps sublattices {swap_ok} | "
                f"cost(U psi0) {dE:7.4f}  m_s {oGS:+.3f}->{o_new:+.3f} (c_R {cR:.4f}, check {abs(oGS - o_new - cR):.0e})  "
                f"max|dE| on 8 states {worst:6.3f}")
        if expect_ok:
            ok = (inv < 1e-9) and swap_ok and dE <= kappa + 1e-9 and worst <= kappa + 1e-9 and abs(oGS - o_new - cR) < 1e-9
            ex = ""
            if cR > 1e-6:
                cache["v"] = psi
                dual, primal, mus = conj_cost(Hfun, E0, n, oGS - cR, -1, mu_hi=0.02, iters=42)
                ok = ok and dual <= dE + 1e-8
                ex = f"  exact E*(-c_R) in [{dual:.5f}, {primal:.5f}] = {dual / kappa:.3f} of the bound"
            if not ok:
                VIOL.append((name, rname))
            print(line + ex + ("  ok" if ok else "  VIOLATION"))
        else:
            print(line + f"   [CONTROL: hypothesis violated; |dE| {'exceeds' if max(worst, abs(dE)) > kappa else 'within'} kappa]")


# ---------------------------------------------------------------------------------------------------- Part A
print("PART A. the inequality on new regions and models")
Lx, Ly = 4, 3
n = Lx * Ly
sid = lambda x, y: Ly * x + y
E = [(sid(x, y), sid(x, y + 1)) for x in range(Lx) for y in range(Ly - 1)] + [(sid(x, y), sid(x + 1, y)) for x in range(Lx - 1) for y in range(Ly)]
eta = [(-1) ** (x + y) for x in range(Lx) for y in range(Ly)]
fields = [(-1.0 * eta[sid(0, y)] if x == 0 else 0.0) for x in range(Lx) for y in range(Ly)]
colswap = lambda c1, c2: {**{sid(c1, y): sid(c2, y) for y in range(Ly)}, **{sid(c2, y): sid(c1, y) for y in range(Ly)}}
R_cols23 = [sid(x, y) for x in (2, 3) for y in range(Ly)]
R_cols12 = [sid(x, y) for x in (1, 2) for y in range(Ly)]
R_blk = [sid(2, 0), sid(2, 1), sid(3, 0), sid(3, 1)]
bad = dict(zip(R_cols23, [R_cols23[k] for k in (1, 0, 3, 2, 5, 4)]))        # swaps (y=0,y=1) only: does not preserve H_R
regions = [
    ("columns 2,3; reflection x", R_cols23, colswap(2, 3), True),
    ("columns 1,2 (interior); reflection x", R_cols12, colswap(1, 2), True),
    ("2x2 corner block; reflection x", R_blk, {sid(2, 0): sid(3, 0), sid(3, 0): sid(2, 0), sid(2, 1): sid(3, 1), sid(3, 1): sid(2, 1)}, True),
    ("2x2 corner block; reflection y", R_blk, {sid(2, 0): sid(2, 1), sid(2, 1): sid(2, 0), sid(3, 0): sid(3, 1), sid(3, 1): sid(3, 0)}, True),
    ("single bond (3,0)-(3,1); swap", [sid(3, 0), sid(3, 1)], {sid(3, 0): sid(3, 1), sid(3, 1): sid(3, 0)}, True),
    ("CONTROL columns 2,3; partial swap", R_cols23, bad, False),
]
for Jz in (1.0, 2.5, 4.0):
    analyse(f"open 3x4 square lattice, Jz = {Jz}, staggered field on column 0", n, n // 2, E, 0.5, Jz, fields, eta, regions, Jz)

N = 14
Ea = [(i, i + 1) for i in range(N - 1)]; Eb = [(i, i + 2) for i in range(N - 2)]
eta = [(-1) ** i for i in range(N)]
f = [0.0] * N; f[0] = -1.0
for Jz in (1.0, 4.0):
    regs = []
    for k in (1, 2, 3, 4, 5):
        R = list(range(N - 2 * k, N))
        regs.append((f"last {2 * k} sites; reflection", R, {R[i]: R[-1 - i] for i in range(len(R))}, True))
    analyse(f"open J1-J2 XXZ chain N=14 (J2 = 0.3, Jz = {Jz}), field on site 0", N, N // 2, Ea + Eb,
            [0.5] * len(Ea) + [0.15] * len(Eb), [Jz] * len(Ea) + [0.3 * Jz] * len(Eb), f, eta, regs, Jz)

N = 13
Ec = [(i, i + 1) for i in range(N - 1)]
eta = [(-1) ** i for i in range(N)]
for Jz in (2.5,):
    regs = [("interior sites 4..9; reflection", list(range(4, 10)), {i: 13 - i for i in range(4, 10)}, True),
            ("interior sites 5..6; swap", [5, 6], {5: 6, 6: 5}, True),
            ("last 8 sites; reflection", list(range(5, 13)), {i: 17 - i for i in range(5, 13)}, True)]
    analyse(f"open chain N=13 in the sector S^z = 1/2 (no field), Jz = {Jz}", N, 7, Ec, 0.5, Jz, None, eta, regs, Jz)
print(f"   violations in Part A: {len(VIOL)}")

# ---------------------------------------------------------------------------------------------------- Part B1
print("\nPART B1. d = 3: all balanced regions of the 19-site patch")
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
n, E, _ = heavy_hex(3)
eta = two_colour(n, E)
adj = adjacency(n, E)
deg = [len(a) for a in adj]
adjm = [sum(1 << v for v in adj[u]) for u in range(n)]
maj = [v for v in range(n) if eta[v] == 1]; mino = [v for v in range(n) if eta[v] == -1]
nbal = nadm = 0
best = {}
minratio = (9.9, None)
minslack = (99, None)
t0 = time.time()
for k in range(1, len(mino) + 1):
    for A in itertools.combinations(maj, k):
        ma = sum(1 << v for v in A)
        for Bm in itertools.combinations(mino, k):
            mask = ma | sum(1 << v for v in Bm)
            nbal += 1
            da = sorted(bin(adjm[v] & mask).count("1") for v in A)
            db = sorted(bin(adjm[v] & mask).count("1") for v in Bm)
            if da != db:
                continue
            R = list(A) + list(Bm)
            g1 = nx.Graph(); g2 = nx.Graph()
            for v in R:
                g1.add_node(v, c=eta[v]); g2.add_node(v, c=-eta[v])
            for a, b in E:
                if (mask >> a) & 1 and (mask >> b) & 1:
                    g1.add_edge(a, b); g2.add_edge(a, b)
            if not GraphMatcher(g1, g2, node_match=lambda p, q: p["c"] == q["c"]).is_isomorphic():
                continue
            nadm += 1
            cross = sum(deg[v] for v in R) - 2 * g1.number_of_edges()
            sz = 2 * k
            if sz not in best or cross < best[sz][0]:
                best[sz] = (cross, R)
            if cross / sz < minratio[0]:
                minratio = (cross / sz, R)
            sl = cross - (sz / 2 - 2 * (3 - 1))
            if sl < minslack[0]:
                minslack = (sl, R)
print(f"   balanced regions: {nbal}; with a sublattice-exchanging automorphism of the induced graph: {nadm}  [{time.time() - t0:.0f} s]")
print("   |R| : fewest crossing bonds among admissible regions")
print("   " + "  ".join(f"{s}:{best[s][0]}" for s in sorted(best)))
print(f"   minimum of crossing/|R| = {minratio[0]:.4f} at R = {sorted(minratio[1])}")
print(f"   minimum of crossing - (|R|/2 - 2(d-1)) = {minslack[0]} (the written bound holds iff >= 0)")
for s in sorted(best):
    if best[s][0] < s / 2 - 4:
        VIOL.append(("heavy-hex bound", s))

# ---------------------------------------------------------------------------------------------------- Part B2
print("\nPART B2. d = 5, 7, 9: integer programme over a relaxation of the admissible regions")
from scipy.optimize import milp, LinearConstraint, Bounds


def ilp(d, lam, half):
    """min  crossing(R) - lam |R|  over R with: balanced, |R| >= 2, each degree-3 minority site of R has <= 2
       neighbours in R.  half=True: objective crossing - |R|/2 (lam ignored)."""
    n, E, _ = heavy_hex(d)
    eta = two_colour(n, E)
    adj = adjacency(n, E)
    m = len(E)
    cvec = np.concatenate([np.full(n, -(0.5 if half else lam)), np.ones(m)])
    rows, lo, hi = [], [], []
    for k, (a, b) in enumerate(E):
        for s in (1, -1):
            r = np.zeros(n + m); r[a] = s; r[b] = -s; r[n + k] = -1
            rows.append(r); lo.append(-np.inf); hi.append(0.0)
    r = np.zeros(n + m); r[:n] = eta; rows.append(r); lo.append(0.0); hi.append(0.0)
    r = np.zeros(n + m); r[:n] = 1; rows.append(r); lo.append(2.0); hi.append(np.inf)
    for b in range(n):
        if eta[b] == -1 and len(adj[b]) == 3:
            r = np.zeros(n + m); r[b] = 1
            for a in adj[b]:
                r[a] = 1
            rows.append(r); lo.append(-np.inf); hi.append(3.0)
    res = milp(c=cvec, constraints=LinearConstraint(np.array(rows), lo, hi),
               integrality=np.concatenate([np.ones(n), np.zeros(m)]), bounds=Bounds(0, 1),
               options={"time_limit": 120})
    x = np.round(res.x[:n]).astype(int)
    cross = sum(1 for a, b in E if x[a] != x[b])
    return res.fun, int(x.sum()), cross, res.status


for d in (3, 5, 7, 9):
    t0 = time.time()
    lam = 0.5
    for it in range(30):
        val, sz, cross, status = ilp(d, lam, False)
        if val > -1e-7:
            break
        lam = cross / sz
    v2, sz2, cross2, st2 = ilp(d, 0.0, True)
    print(f"   d={d}: min crossing/|R| over the relaxation = {lam:.4f} (attained at |R| = {sz}, crossing = {cross}; status {status});  "
          f"min [crossing - |R|/2] = {v2:.1f} at |R| = {sz2} (written bound: >= {-2 * (d - 1)}; status {st2})  [{time.time() - t0:.0f} s]")
    if v2 < -2 * (d - 1) - 1e-6:
        VIOL.append(("heavy-hex bound, relaxation", d))

# ---------------------------------------------------------------------------------------------------- Part B3
print("\nPART B3. n = 19, Jz = 4: exact cost of lowering m_s in the Neel sector")
n, E, _ = heavy_hex(3)
eta = np.array(two_colour(n, E), float)
nup = int((eta > 0).sum())
st = sector(n, nup)
Jz = 4.0
Hoff, diag = build(st, n, E, hop=0.5, jz=Jz)
z = zvals(st, n)
Od = eta @ z
w, psi = lowest(Hoff, diag, k=2)
E0 = w[0]
oGS = float(psi * psi @ Od) / n
cache = {"v": psi}


def Hfun19(mu):
    ww, v = lowest(Hoff, diag + mu * Od, k=2, v0=cache["v"], tol=1e-10)
    cache["v"] = v
    return ww[0], float(v * v @ Od) / n, expect(Hoff, diag, v)


print(f"   m_s(GS) = {oGS:.4f}, sector gap {w[1] - w[0]:.4f}; spread of a bond term s = {(Jz + 1) / 2}")
for c in (0.1, 0.5, 1.0):
    cache["v"] = psi
    dual, primal, mus = conj_cost(Hfun19, E0, n, oGS - c, -1, mu_hi=0.05, iters=34)
    pd_best = (Jz + 1) / 2 * minratio[0] * n * c / 2          # s * (crossing/|R|)_min * n c / 2, using c_R <= 2|R|/n
    print(f"   c = {c:3.1f}: exact E*_n(-c) in [{dual:.4f}, {primal:.4f}] = {dual / (n * c):.4f} per site per unit c "
          f"(classical in-sector Peierls value 3Jz/56 * 2 ... see report); smallest bound Proposition D can give: {pd_best:.3f}  "
          f"(field mu* = {mus:.4f} = {mus / Jz:.4f} Jz)")
print(f"\ntotal violations: {len(VIOL)}; total time {time.time() - t00:.0f} s")
for v in VIOL:
    print("  VIOLATION", v)
