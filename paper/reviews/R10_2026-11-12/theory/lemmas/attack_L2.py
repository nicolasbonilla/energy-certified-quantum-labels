"""attack_L2.py -- exact attack of Lemma L2 (Peierls bound for the heavy-hex patch family).

Units Jz = 1. Every comparison is exact (fractions.Fraction or Python integers); no floating point decides anything.

Parts
  A  coordinate definition HH_d of the patches; equality with rustworkx.generators.heavy_hex_graph(d) as LABELLED
     graphs (explicit index map) for odd d = 3..41, and with the paper's stored graphs hh_d{3,5,7}.json
  B  structural facts (S1), (S2) used by the proof, checked site by site, and the list of neighbourhood types
  C  the three-number certificate g = x + y (deg b' - deg b), t on dangling edges: every site inequality and every
     range condition, for a grid of B covering the window 0 < B < 1/2, for odd d = 3..41
  D  brute force over all 2^19 - 1 non-empty sets D at d = 3 (n = 19): exact minimum of cost(D)/|D|
  E  exact minimum of cost(D)/|D| by Dinkelbach iteration on integer minimum cuts, d = 3..13, compared with the
     certified constant; the decomposition H_cl - E_Neel = sum_i s_i n_i + sum_e t_e on random configurations
Run:  python -B attack_L2.py > attack_L2_out.txt
"""
import json, random, sys, time
from fractions import Fraction as Fr
from math import lcm
import numpy as np
import networkx as nx
import rustworkx as rx

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
t00 = time.time()


# ----------------------------------------------------------------------------------------------------------------
# A. coordinate definition
# ----------------------------------------------------------------------------------------------------------------
def hh_coord(d):
    """HH_d, d odd >= 3.  Sites (names) and the generator's index for each:
       D(c,k)  c,k = 0..d-1                       index c*d + k                         (majority)
       F(c,r)  c = 0..d-1, r = 0..d-2             index d^2 + (d^2-1)/2 + c*(d-1) + r   (minority)
       S(i,r)  i = 0..d-2, r = 0..d-2, i+r odd    (majority)   } syndrome block, chunk i of size (d+1)/2:
       T(i)    i = 0..d-2                         (minority)   } i even: T(i),S(i,1),S(i,3),..,S(i,d-2)
                                                                 i odd : S(i,0),S(i,2),..,S(i,d-3),T(i)
       Edges:  F(c,r) - D(c,r), F(c,r) - D(c,r+1);  S(i,r) - F(i,r), S(i,r) - F(i+1,r);
               T(i) - D(i,0), T(i) - D(i+1,0) for i even;  T(i) - D(i,d-1), T(i) - D(i+1,d-1) for i odd."""
    assert d % 2 == 1 and d >= 3
    h = (d + 1) // 2
    base_s = d * d
    base_f = d * d + (d * d - 1) // 2
    idx = {}
    for c in range(d):
        for k in range(d):
            idx[("D", c, k)] = c * d + k
        for r in range(d - 1):
            idx[("F", c, r)] = base_f + c * (d - 1) + r
    for i in range(d - 1):
        if i % 2 == 0:
            idx[("T", i)] = base_s + i * h
            for p in range(1, h):
                idx[("S", i, 2 * p - 1)] = base_s + i * h + p
        else:
            for p in range(h - 1):
                idx[("S", i, 2 * p)] = base_s + i * h + p
            idx[("T", i)] = base_s + i * h + h - 1
    n = len(idx)
    assert sorted(idx.values()) == list(range(n))
    E = set()
    def add(u, v):
        a, b = idx[u], idx[v]
        E.add((min(a, b), max(a, b)))
    for c in range(d):
        for r in range(d - 1):
            add(("F", c, r), ("D", c, r)); add(("F", c, r), ("D", c, r + 1))
    for i in range(d - 1):
        for r in range(d - 1):
            if (i + r) % 2 == 1:
                add(("S", i, r), ("F", i, r)); add(("S", i, r), ("F", i + 1, r))
        if i % 2 == 0:
            add(("T", i), ("D", i, 0)); add(("T", i), ("D", i + 1, 0))
        else:
            add(("T", i), ("D", i, d - 1)); add(("T", i), ("D", i + 1, d - 1))
    name = {v: k for k, v in idx.items()}
    maj = {v for k, v in idx.items() if k[0] in ("D", "S")}
    return n, sorted(E), maj, name


def generator_edges(d):
    g = rx.generators.heavy_hex_graph(d)
    return g.num_nodes(), sorted({(min(a, b), max(a, b)) for a, b in g.edge_list()})


print("=" * 110)
print("A. coordinate definition HH_d against the generator (rustworkx %s), as labelled graphs" % rx.__version__)
DS = list(range(3, 43, 2))
okA = True
for d in DS:
    n, E, maj, name = hh_coord(d)
    ng, Eg = generator_edges(d)
    same = (n == ng and E == Eg)
    okA &= same
    assert n == (5 * d * d - 2 * d - 1) // 2
print("  labelled edge sets equal for every odd d in %d..%d: %s" % (DS[0], DS[-1], okA))
for d in (3, 5, 7):
    for sub in ("map", "method"):
        J = json.load(open(f"{ROOT}/phase3/full_runs/{sub}/code/graphs/hh_d{d}.json"))
        Ej = sorted({(min(a, b), max(a, b)) for a, b in J["edges"]})
        n, E, maj, name = hh_coord(d)
        eta_ok = all((J["eta"][i] == 1) == (i in maj) for i in range(n))
        print(f"  stored {sub}/code/graphs/hh_d{d}.json: n = {J['n']}, edges equal: {Ej == E}, eta = +1 exactly on D and S: {eta_ok}")
        okA &= (Ej == E) and eta_ok


# ----------------------------------------------------------------------------------------------------------------
# B. structural facts
# ----------------------------------------------------------------------------------------------------------------
def structure(d):
    n, E, maj, name = hh_coord(d)
    adj = {i: [] for i in range(n)}
    for a, b in E:
        adj[a].append(b); adj[b].append(a)
    deg = {i: len(adj[i]) for i in range(n)}
    return n, E, maj, name, adj, deg


def other(adj, a, b):
    """the neighbour of the degree-2 site a that is not b"""
    o = [v for v in adj[a] if v != b]
    assert len(o) == 1
    return o[0]


print("=" * 110)
print("B. structural facts used in the proof, checked on every site")
print("   (S1) bipartite between maj = D u S and min = F u T; majority degrees in {1,2}; minority degrees in {2,3}")
print("   (S2) every minority site has a degree-2 majority neighbour whose other neighbour has degree 3")
types_by_d = {}
okB = True
for d in DS:
    n, E, maj, name, adj, deg = structure(d)
    bip = all((a in maj) != (b in maj) for a, b in E)
    nmaj = len(maj); nmin = n - nmaj
    counts = (nmaj == (3 * d * d - 2 * d + 1) // 2 and nmin == d * d - 1)
    s1 = all(deg[i] in (1, 2) for i in maj) and all(deg[i] in (2, 3) for i in range(n) if i not in maj)
    dang = sorted(name[i] for i in maj if deg[i] == 1)
    dang_ok = dang == sorted([("D", 0, d - 1), ("D", d - 1, 0)])
    min2 = sorted(name[i] for i in range(n) if i not in maj and deg[i] == 2)
    exp2 = sorted([("F", d - 1, r) for r in range(1, d - 1, 2)] + [("F", 0, r) for r in range(0, d - 1, 2)]
                  + [("T", i) for i in range(d - 1)])
    min2_ok = (min2 == exp2 and len(min2) == 2 * (d - 1))
    s2 = True
    rows = set()
    for b in range(n):
        if b in maj:
            continue
        good = False
        key = []
        for a in adj[b]:
            if deg[a] == 2:
                k2 = deg[other(adj, a, b)]
                key.append(k2)
                good |= (k2 == 3)
            else:
                key.append("dangling")
        s2 &= good
        rows.add(("minority", deg[b], tuple(sorted(map(str, key)))))
    for a in maj:
        rows.add(("majority", deg[a], tuple(sorted(str(deg[b]) for b in adj[a]))))
    types_by_d[d] = rows
    ok = bip and counts and s1 and dang_ok and min2_ok and s2
    okB &= ok
    if d <= 9 or d == DS[-1]:
        print(f"  d={d:2d} n={n:5d} maj/min={nmaj}/{nmin} bipartite={bip} counts={counts} S1={s1} dangling={dang_ok} "
              f"deg-2 minority sites as predicted={min2_ok} S2={s2} | neighbourhood types: {len(rows)}")
print("  all of the above for every odd d in %d..%d: %s" % (DS[0], DS[-1], okB))
ref = types_by_d[5]
print("  list of neighbourhood types (colour, degree, degrees seen through each neighbour) identical for all d >= 5: %s; "
      "d = 3 has a subset: %s (missing: %s)" % (all(types_by_d[d] == ref for d in DS if d >= 5), types_by_d[3] <= ref,
                                                 sorted(ref - types_by_d[3])))
print("  the %d types (d >= 5):" % len(ref))
for r in sorted(ref):
    print("     ", r)


# ----------------------------------------------------------------------------------------------------------------
# C. the certificate
# ----------------------------------------------------------------------------------------------------------------
def gamma_loc(B):
    return min(Fr(2) * B / 13, (1 - 2 * B) / 3)


def rule(B, gam=None):
    gam = gamma_loc(B) if gam is None else gam
    x = B - gam / 2
    y = 2 * gam
    t = min(Fr(1, 2), 2 * B - gam)
    return gam, x, y, t


def certificate(d, B, gam=None):
    """returns (ok, min slack majority, min slack minority, max |g|, g dict keyed by (a, b))"""
    n, E, maj, name, adj, deg = structure(d)
    gam, x, y, t = rule(B, gam)
    g = {}
    for a in maj:
        for b in adj[a]:
            g[(a, b)] = t if deg[a] == 1 else x + y * (deg[other(adj, a, b)] - deg[b])
    ok = all(abs(v) <= Fr(1, 2) for v in g.values())
    smaj = min(2 * B - gam - sum(g[(a, b)] for b in adj[a]) for a in maj)
    smin = min(sum(g[(a, b)] for a in adj[b]) - 2 * B - gam for b in range(n) if b not in maj)
    return (ok and smaj >= 0 and smin >= 0), smaj, smin, max(abs(v) for v in g.values()), g


print("=" * 110)
print("C. certificate g(a->b) = x + y (deg b' - deg b) for a of degree 2 (b' = other neighbour of a), g = t for a dangling;")
print("   gamma(B) = min(2B/13, (1-2B)/3), x = B - gamma/2, y = 2 gamma, t = min(1/2, 2B - gamma)   [units Jz = 1]")
Bgrid = sorted(set([Fr(k, 100) for k in range(1, 50)] + [Fr(3, 8), Fr(13, 32), Fr(13, 48), Fr(1, 1000), Fr(499, 1000),
                                                         Fr(7, 20), Fr(13, 38), Fr(55, 164), Fr(5, 16), Fr(1, 3)]))
okC = True
for d in DS:
    for B in (Bgrid if d <= 21 else [Fr(1, 100), Fr(13, 48), Fr(3, 8), Fr(13, 32), Fr(49, 100)]):
        ok, smaj, smin, gmax, g = certificate(d, B)
        okC &= ok
print("  all site inequalities and |g| <= 1/2 hold, d = %d..%d, %d values of B in (0, 1/2) for d <= 21 and 5 values above: %s"
      % (DS[0], DS[-1], len(Bgrid), okC))
print("  table at B = 3/8 (gamma = %s):" % gamma_loc(Fr(3, 8)))
gam, x, y, t = rule(Fr(3, 8))
print("     x = %s, y = %s, t = %s; values: equal degrees %s, towards degree 2 from degree 3 %s, towards degree 3 from degree 2 %s, dangling %s"
      % (x, y, t, x, x + y, x - y, t))
print("     majority budget 2B - gamma = %s, minority demand 2B + gamma = %s" % (2 * Fr(3, 8) - gam, 2 * Fr(3, 8) + gam))
for B in (Fr(1, 100), Fr(1, 8), Fr(1, 4), Fr(13, 48), Fr(5, 16), Fr(3, 8), Fr(13, 32), Fr(9, 20), Fr(49, 100)):
    ok, smaj, smin, gmax, g = certificate(7, B)
    print(f"     d=7 B={str(B):>6}: gamma={str(gamma_loc(B)):>7} ok={ok} min slack maj={smaj} min={smin} max|g|={gmax}")
# an attempt to beat the constant with the same three-number form must fail somewhere: gamma slightly larger
bad = 0
for B in (Fr(1, 8), Fr(3, 8), Fr(13, 32), Fr(9, 20)):
    ok, *_ = certificate(7, B, gamma_loc(B) + Fr(1, 10 ** 6))
    bad += (not ok)
print("  the same form with gamma(B) + 1e-6 violates an inequality or the range at 4 of 4 tested B (d = 7): %s" % (bad == 4))


# ----------------------------------------------------------------------------------------------------------------
# D. brute force, d = 3
# ----------------------------------------------------------------------------------------------------------------
print("=" * 110)
print("D. brute force over all non-empty D, d = 3 (n = 19, 524287 sets); exact integers")
n, E, maj, name, adj, deg = structure(3)
N = 1 << n
masks = np.arange(N, dtype=np.int64)
bits = [(masks >> i) & 1 for i in range(n)]
cut = np.zeros(N, dtype=np.int64)
for a, b in E:
    cut += bits[a] ^ bits[b]
na = sum(bits[i] for i in range(n) if i in maj)
nb = sum(bits[i] for i in range(n) if i not in maj)
size = na + nb
okD = True
for B in (Fr(1, 100), Fr(1, 8), Fr(1, 4), Fr(7, 20), Fr(3, 8), Fr(13, 32), Fr(9, 20), Fr(49, 100)):
    gam = gamma_loc(B)
    L = lcm(2, B.denominator, gam.denominator)
    cost = (L // 2) * cut + int(2 * B * L) * (na - nb)          # L * cost(D)
    margin = cost - int(gam * L) * size                          # L * (cost - gamma |D|)
    mn = int(margin[1:].min())
    best = min(Fr(int(cost[1:][size[1:] == s].min()), L * s) for s in range(1, n + 1))
    nzero = int((cost[1:] <= 0).sum())
    okD &= (mn >= 0 and nzero == 0)
    print(f"   B={str(B):>6}: min over D of cost - gamma_loc|D| = {Fr(mn, L)} (>= 0: {mn >= 0}); exact min cost/|D| = {best}; "
          f"gamma_loc = {gam}; sets with cost <= 0: {nzero}")
for B in (Fr(0), Fr(1, 2)):
    L = 2
    cost = cut + int(2 * B * L) * (na - nb)
    print(f"   B={B}: sets with cost <= 0: {int((cost[1:] <= 0).sum())} (the window 0 < B < 1/2 is exact: at its ends a set costs nothing)")
print("  brute force agrees with the lemma at d = 3: %s" % okD)


# ----------------------------------------------------------------------------------------------------------------
# E. exact minimum ratio by integer minimum cuts
# ----------------------------------------------------------------------------------------------------------------
def min_F(n, E, maj, B, gam):
    """exact min over D (possibly empty) of cut(D)/2 + sum_{i in D} w_i, w = 2B - gam (maj), -2B - gam (min);
       returns (value, D) with value a Fraction"""
    L = lcm(2, B.denominator, gam.denominator)
    G = nx.DiGraph()
    neg = 0
    for i in range(n):
        w = (2 * B - gam) if i in maj else (-2 * B - gam)
        wi = int(w * L)
        if wi < 0:
            G.add_edge("s", i, capacity=-wi); neg += wi
        elif wi > 0:
            G.add_edge(i, "t", capacity=wi)
    for a, b in E:
        G.add_edge(a, b, capacity=L // 2); G.add_edge(b, a, capacity=L // 2)
    if "s" not in G or "t" not in G:
        return Fr(neg, L), set(range(n)) if "t" not in G else set()
    val, (S, T) = nx.minimum_cut(G, "s", "t", flow_func=nx.algorithms.flow.dinitz)
    D = set(S) - {"s"}
    return Fr(neg + val, L), D


def cost_of(D, E, maj, B):
    c = sum(1 for a, b in E if (a in D) != (b in D))
    na = sum(1 for i in D if i in maj)
    return Fr(c, 2) + 2 * B * (2 * na - len(D))


def gamma_exact(d, B):
    n, E, maj, name, adj, deg = structure(d)
    b0 = min((i for i in range(n) if i not in maj), key=lambda i: deg[i])
    D = {b0}
    gam = cost_of(D, E, maj, B) / len(D)
    for it in range(60):
        val, D2 = min_F(n, E, maj, B, gam)
        if val >= 0 or not D2:
            return gam, D, it
        D = D2
        gam = cost_of(D, E, maj, B) / len(D)
    raise RuntimeError("Dinkelbach did not stop")


print("=" * 110)
print("E. exact min over D of cost(D)/|D| (Dinkelbach on integer minimum cuts) against the certified gamma_loc(B)")
print("   d    n     B   gamma_exact  gamma_loc  ratio loc/exact  |D*|")
okE = True
tab = {}
for d in (3, 5, 7, 9, 11, 13):
    Bs = [Fr(1, 100), Fr(1, 8), Fr(1, 4), Fr(5, 16), Fr(3, 8), Fr(13, 32), Fr(9, 20), Fr(49, 100)] if d <= 9 else \
         [Fr(1, 8), Fr(3, 8), Fr(13, 32), Fr(9, 20)]
    for B in Bs:
        ge, D, it = gamma_exact(d, B)
        gl = gamma_loc(B)
        okE &= (ge >= gl > 0)
        tab[(d, str(B))] = str(ge)
        print(f"  {d:2d} {(5*d*d-2*d-1)//2:4d} {str(B):>6} {str(ge):>11} {str(gl):>9}   {float(gl/ge):.4f}        {len(D)}")
print("  gamma_exact >= gamma_loc > 0 in every row: %s" % okE)
# cross-checks of three exact values quoted in reports/level-theory.md
chk = [(3, Fr(7, 20), Fr(1, 10)), (5, Fr(13, 38), Fr(2, 19)), (7, Fr(55, 164), Fr(9, 82)), (3, Fr(3, 8), Fr(1, 12)),
       (5, Fr(3, 8), Fr(1, 12)), (7, Fr(3, 8), Fr(1, 12))]
for d, B, want in chk:
    ge, D, it = gamma_exact(d, B)
    print(f"  cross-check d={d} B={B}: exact {ge}, quoted {want}, equal: {ge == want}")
# brute force (part D) against min cut at d = 3
ge3, _, _ = gamma_exact(3, Fr(3, 8))
print("  d = 3, B = 3/8: minimum cut gives %s; brute force gave the value printed in part D" % ge3)

# decomposition H_cl - E_Neel = sum_i s_i n_i + sum_e t_e on random configurations (exact)
random.seed(5)
okdec = True
for d in (3, 5, 7):
    n, E, maj, name, adj, deg = structure(d)
    for B in (Fr(1, 8), Fr(3, 8), Fr(9, 20)):
        for mu in (Fr(0), Fr(-1, 50), Fr(1, 10)):
            ok, smaj, smin, gmax, g = certificate(d, B)
            gam = gamma_loc(B)
            for trial in range(40):
                p = random.random()
                D = {i for i in range(n) if random.random() < p}
                direct = cost_of(D, E, maj, B) + 2 * mu * len(D)
                # direct recomputation from the spin configuration, as a check of cost_of itself
                s = {i: (1 if i in maj else -1) * (-1 if i in D else 1) for i in range(n)}
                s0 = {i: (1 if i in maj else -1) for i in range(n)}
                Hcl = lambda z: Fr(1, 4) * sum(z[a] * z[b] for a, b in E) - B * sum(z.values()) \
                    - mu * sum((1 if i in maj else -1) * z[i] for i in range(n))
                okdec &= (Hcl(s) - Hcl(s0) == direct)
                tot = Fr(0)
                smin_site = None
                for i in range(n):
                    if i in maj:
                        si = 2 * B + 2 * mu - sum(g[(i, b)] for b in adj[i])
                    else:
                        si = -2 * B + 2 * mu + sum(g[(a, i)] for a in adj[i])
                    okdec &= (si >= gam + 2 * mu)
                    tot += si * (1 if i in D else 0)
                for (a, b), ge_ in g.items():
                    na_, nb_ = int(a in D), int(b in D)
                    te = (Fr(1, 2) + ge_) * na_ * (1 - nb_) + (Fr(1, 2) - ge_) * nb_ * (1 - na_)
                    okdec &= (te >= 0)
                    tot += te
                okdec &= (tot == direct) and (direct >= (gam + 2 * mu) * len(D))
print("  decomposition H_cl - E_Neel = sum_i s_i n_i + sum_e t_e with s_i >= gamma + 2 mu, t_e >= 0, and the bound "
      "cost >= (gamma + 2 mu)|D|: exact on 1080 random configurations (d = 3, 5, 7): %s" % okdec)

print("=" * 110)
print("ALL PARTS PASS: %s    (%.1f s)" % (okA and okB and okC and okD and okE and okdec, time.time() - t00))
