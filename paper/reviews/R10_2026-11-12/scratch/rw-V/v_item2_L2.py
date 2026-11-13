"""v_item2_L2.py -- verifier V, item 2: the repaired proof step of L2_peierls_v2.tex ("The rule") on the real graphs.

Own code. Checks, for the patches built from the printed formula (v_common.patch):
  A. the patch is isomorphic to rustworkx.generators.heavy_hex_graph(d) (d = 3..13) and to the stored graphs
     phase3/full_runs/map/code/graphs/hh_d{3,5,7}.json (read-only)
  B. (S1) and (S2) for d = 3..41
  C. neighbourhood types that occur; rows that (S1) allows; rows that (S1)+(S2) allow but that do not occur
  D. the rule g = x + y (deg b' - deg b), t on dangling sites: every site inequality in exact rationals for many B,
     on the real graphs AND on every hypothetical row that (S1)+(S2) allow (the v2 proof claims these need no list)
  E. d = 3: all 2^19 - 1 sets: cost(D) >= gamma(B) |D| (exact, on the distinct triples (boundary, a, b));
     exact minimum over all sets and over the sets that keep the magnetization (3/28 claim)
  F. d = 5, 7, 9: random and grown sets, exact
Output: v_item2_L2_out.txt
"""
import os, sys, json, time, itertools, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
from v_common import patch, adjacency
import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
t00 = time.time()
lines = []
fails = 0


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def check(cond, msg):
    global fails
    if not cond:
        fails += 1
        say("   FAIL: " + msg)


# ---------------------------------------------------------------------------------------------------------------- A
say("A. my construction against the generator and the stored graphs")
import rustworkx as rx
for d in (3, 5, 7, 9, 11, 13):
    n, E, names, eta = patch(d)
    g1 = rx.PyGraph(multigraph=False)
    g1.add_nodes_from(range(n))
    g1.add_edges_from_no_data(E)
    g2 = rx.generators.heavy_hex_graph(d)
    iso = rx.is_isomorphic(g1, g2)
    check(iso, f"d = {d}: not isomorphic to rustworkx")
    check(n == (5 * d * d - 2 * d - 1) // 2 and len(E) == 3 * d * d - 2 * d - 1, f"d = {d}: counts")
    say(f"   d = {d}: n = {n}, |E| = {len(E)}, isomorphic to rustworkx.generators.heavy_hex_graph({d}) "
        f"(rustworkx {rx.__version__}): {iso}")
for d in (3, 5, 7):
    n, E, names, eta = patch(d)
    S = json.load(open(f"{ROOT}/phase3/full_runs/map/code/graphs/hh_d{d}.json"))
    g1 = rx.PyGraph(multigraph=False)
    g1.add_nodes_from(range(n))
    g1.add_edges_from_no_data(E)
    g2 = rx.PyGraph(multigraph=False)
    g2.add_nodes_from(range(S["n"]))
    g2.add_edges_from_no_data([tuple(e) for e in S["edges"]])
    iso = rx.is_isomorphic(g1, g2)
    check(iso and S["n"] == n and int(sum(S["eta"])) == int(eta.sum()), f"stored graph d = {d}")
    say(f"   d = {d}: isomorphic to the stored map graph hh_d{d}.json: {iso}; stored sum(eta) = {int(sum(S['eta']))}, "
        f"mine {int(eta.sum())}")

# ---------------------------------------------------------------------------------------------------------------- B, C
say("\nB. (S1), (S2);  C. neighbourhood types")
ALLTYPES = {}
for d in list(range(3, 43, 2)):
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    deg = [len(a) for a in adj]
    maj = [i for i in range(n) if eta[i] > 0]
    mino = [i for i in range(n) if eta[i] < 0]
    bip = all(eta[a] != eta[b] for a, b in E)
    s1 = (bip and sorted(set(deg[i] for i in maj)) == [1, 2] and sum(deg[i] == 1 for i in maj) == 2
          and sorted(set(deg[i] for i in mino)) == [2, 3] and sum(deg[i] == 2 for i in mino) == 2 * (d - 1)
          and len(maj) == (3 * d * d - 2 * d + 1) // 2 and len(mino) == d * d - 1)
    # the degree-2 minority sites are exactly C(i), F(0, r even), F(d-1, r odd)
    named = set(i for i in mino if names[i][0] == "C" or (names[i][0] == "F" and names[i][1] == 0 and names[i][2] % 2 == 0)
                or (names[i][0] == "F" and names[i][1] == d - 1 and names[i][2] % 2 == 1))
    s1 = s1 and named == set(i for i in mino if deg[i] == 2)
    dang = set(names[i] for i in maj if deg[i] == 1)
    s1 = s1 and dang == {("D", 0, d - 1), ("D", d - 1, 0)}

    def other(a, b):
        o = [c for c in adj[a] if c != b]
        return o[0] if o else None
    s2 = True
    types = {}
    for b in mino:
        ok = False
        desc = []
        for a in adj[b]:
            if deg[a] == 1:
                desc.append("d")
            else:
                bp = other(a, b)
                desc.append(str(deg[bp]))
                if deg[bp] == 3:
                    ok = True
        s2 = s2 and ok
        key = ("minority", deg[b], tuple(sorted(desc)))
        types[key] = types.get(key, 0) + 1
    for a in maj:
        key = ("majority", deg[a], tuple(sorted(str(deg[b]) for b in adj[a])))
        types[key] = types.get(key, 0) + 1
    check(s1, f"(S1) fails at d = {d}")
    check(s2, f"(S2) fails at d = {d}")
    ALLTYPES[d] = types
    if d in (3, 5, 7, 9, 11, 25, 41):
        say(f"   d = {d}: bipartite {bip}; (S1) {s1}; (S2) {s2}; {len(types)} types")
say(f"   (S1), (S2) hold for every odd d = 3..41: {fails == 0}")
TABLE = [("majority", 1, ("3",)), ("majority", 2, ("2", "2")), ("majority", 2, ("2", "3")), ("majority", 2, ("3", "3")),
         ("minority", 2, ("2", "3")), ("minority", 2, ("3", "3")), ("minority", 3, ("2", "2", "3")),
         ("minority", 3, ("2", "3", "3")), ("minority", 3, ("3", "3", "3")), ("minority", 3, ("2", "3", "d"))]
for d in (3, 5, 7):
    say(f"   d = {d}: types and multiplicities:")
    for k in sorted(ALLTYPES[d]):
        say(f"      {k[0]:8s} degree {k[1]}  sees ({','.join(k[2])}) : {ALLTYPES[d][k]:4d}   {'in table' if k in TABLE else 'NOT IN TABLE'}")
same = all(set(ALLTYPES[d]) == set(TABLE) for d in ALLTYPES if d >= 5)
check(same, "types for d >= 5 differ from the ten rows of the table")
check(set(ALLTYPES[3]) <= set(TABLE) and len(ALLTYPES[3]) == 7, "d = 3 types")
say(f"   types for every odd d = 5..41 are exactly the ten rows of the table: {same}; d = 3 has {len(ALLTYPES[3])} of them")
# rows that (S1) alone allows for a minority site; which of them (S2) excludes; which remain but do not occur
occ = set(k for d in ALLTYPES for k in ALLTYPES[d] if k[0] == "minority")
say("   minority rows allowed by (S1) alone [degree; for each neighbour: degree of its other neighbour or d]:")
hyp_rows = []
for dg in (2, 3):
    for desc in itertools.combinations_with_replacement(["2", "3", "d"], dg):
        key = ("minority", dg, tuple(sorted(desc)))
        s2ok = "3" in desc
        status = "occurs" if key in occ else ("excluded by (S2)" if not s2ok else "allowed by (S1)+(S2), does NOT occur (d <= 41)")
        hyp_rows.append((dg, desc, s2ok, key in occ))
        say(f"      degree {dg} ({','.join(desc)}): {status}")

# ---------------------------------------------------------------------------------------------------------------- D
say("\nD. the rule in exact rationals (Jz = 1)")


def gam(B):
    return min(2 * B / 13, (1 - 2 * B) / 3)


def xyt(B):
    g = gam(B)
    return B - g / 2, 2 * g, min(Fr(1, 2), 2 * B - g), g


BS = [Fr(1, 1000), Fr(1, 100), Fr(1, 20), Fr(1, 10), Fr(1, 8), Fr(1, 5), Fr(1, 4), Fr(3, 10), Fr(1, 3), Fr(7, 20),
      Fr(13, 38), Fr(55, 164), Fr(3, 8), Fr(2, 5), Fr(13, 32), Fr(21, 50), Fr(9, 20), Fr(12, 25), Fr(49, 100),
      Fr(499, 1000), Fr(4999, 10000)]
nineq = 0
for d in (3, 5, 7, 9, 11, 13, 21):
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    deg = [len(a) for a in adj]
    for B in BS:
        x, y, t, g = xyt(B)
        gval = {}
        for a in range(n):
            if eta[a] < 0:
                continue
            if deg[a] == 1:
                gval[(a, adj[a][0])] = t
            else:
                b, bp = adj[a]
                gval[(a, b)] = x + y * (deg[bp] - deg[b])
                gval[(a, bp)] = x + y * (deg[b] - deg[bp])
        for (a, b), v in gval.items():
            check(-Fr(1, 2) <= v <= Fr(1, 2) and v > 0, f"range of g at d = {d}, B = {B}")
        for a in range(n):
            if eta[a] > 0:
                s = sum(gval[(a, b)] for b in adj[a])
                check(s <= 2 * B - g, f"majority site d = {d}, B = {B}")
            else:
                s = sum(gval[(a2, a)] for a2 in adj[a])
                check(s >= 2 * B + g, f"minority site d = {d}, B = {B}: {names[a]} sum {s} < {2*B+g}")
            nineq += 1
say(f"   {nineq} site inequalities on d = 3, 5, 7, 9, 11, 13, 21 at {len(BS)} fields B in (0, 1/2): failures so far {fails}")
# hypothetical rows: every minority row allowed by (S1)+(S2), whether it occurs or not; fine grid of B
grid = [Fr(k, 2000) for k in range(1, 1000)]
bad_rows = 0
for dg, desc, s2ok, occurs in hyp_rows:
    worst = None
    for B in grid:
        x, y, t, g = xyt(B)
        s = 0
        for c in desc:
            s += t if c == "d" else x + y * (int(c) - dg)
        slack = s - (2 * B + g)
        worst = slack if worst is None else min(worst, slack)
    if s2ok:
        check(worst >= 0, f"hypothetical row degree {dg} {desc} violates the minority inequality")
        if worst < 0:
            bad_rows += 1
    say(f"      degree {dg} ({','.join(desc)}): min over B of [sum g - (2B + gamma)] = {worst} ({float(worst):+.5f})"
        f"{'' if s2ok else '   <- not required: excluded by (S2)'}")
say(f"   every row allowed by (S1)+(S2) satisfies the minority inequality for all 999 fields B = k/2000: {bad_rows == 0}")
# the two lower bounds of the v2 proof, as identities in B
for B in grid:
    x, y, t, g = xyt(B)
    check(x - y > 0 and x + y <= Fr(1, 2) and x < t <= Fr(1, 2) and t <= 2 * B - g, f"ranges at B = {B}")
    check(2 * x + y == 2 * B + g and 3 * x - 2 * y == 2 * B + g + (B - Fr(13, 2) * g) and B - Fr(13, 2) * g >= 0,
          f"identities at B = {B}")
    check(min(x, t) == x and min(x - y, t) == x - y, f"minima at B = {B}")
say(f"   ranges 0 < x-y, x+y <= 1/2, x < t <= min(1/2, 2B-gamma); identities 2x+y = 2B+gamma, 3x-2y = 2B+gamma+(B-13gamma/2) >= 0: "
    f"checked at 999 fields; failures so far {fails}")
x, y, t, g = xyt(Fr(3, 8))
say(f"   at B = 3/8: gamma = {g}, x = {x}, y = {y}, t = {t}, budget {2*Fr(3,8)-g}, demand {2*Fr(3,8)+g}; gamma(13/32) = {gam(Fr(13,32))}")

# ---------------------------------------------------------------------------------------------------------------- E
say("\nE. d = 3: all 2^19 - 1 sets")
n, E, names, eta = patch(3)
st = np.arange(1, 1 << n, dtype=np.int64)
bits = ((st[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8)
a_cnt = bits[:, eta > 0].sum(axis=1).astype(np.int64)
b_cnt = bits[:, eta < 0].sum(axis=1).astype(np.int64)
bd = np.zeros(len(st), dtype=np.int64)
for i, j in E:
    bd += bits[:, i] ^ bits[:, j]
trip, cnts = np.unique(np.stack([bd, a_cnt, b_cnt], axis=1), axis=0, return_counts=True)
say(f"   {len(st)} sets, {len(trip)} distinct triples (boundary bonds, majority, minority)")
viol = 0
for B in BS:
    g = gam(B)
    mn = None
    for (c, a, b) in trip:
        cost = Fr(int(c), 2) + 2 * B * (int(a) - int(b))
        if cost < g * (int(a) + int(b)):
            viol += 1
        r = cost / (int(a) + int(b))
        mn = r if mn is None else min(mn, r)
    if B in (Fr(1, 4), Fr(7, 20), Fr(3, 8), Fr(13, 32), Fr(9, 20)):
        say(f"      B = {B}: gamma = {g} ({float(g):.5f}); exact minimum of cost/|D| over all sets = {mn} ({float(mn):.5f}); "
            f"ratio certified/exact = {float(g/mn):.3f}")
check(viol == 0, "a set violates the bound at d = 3")
say(f"   violations of cost(D) >= gamma(B)|D| over all sets and {len(BS)} fields: {viol}")
bal = a_cnt == b_cnt
nb = int(bal.sum())
ratio = None
arg = None
for (c, a, b) in trip:
    if a == b and a > 0:
        r = Fr(int(c), 2) / (2 * int(a))
        if ratio is None or r < ratio:
            ratio, arg = r, (int(c), int(a))
say(f"   sets that keep the magnetization: {nb}; minimum of (1/2)|bd D|/|D| = {ratio} at |D| = {2*arg[1]}, {arg[0]} boundary bonds; "
    f"classical crossing field = {ratio/2} = {float(ratio/2):.4f} Jz; sector statement gamma/16-form: "
    f"min |bd D|/|D| = {2*ratio} >= 1/8: {2*ratio >= Fr(1,8)}")
check(nb == 75581 and ratio == Fr(3, 28) and arg == (3, 7), "sector numbers at n = 19")

# ---------------------------------------------------------------------------------------------------------------- F
say("\nF. d = 5, 7, 9: random, grown and adversarial sets (exact rationals)")
random.seed(20261112)
tot = 0
viol = 0
for d in (5, 7, 9):
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    cnt = 0
    worst = None
    seen = set()
    for trial in range(40000):
        mode = trial % 4
        if mode == 0:
            p = random.random()
            D = set(i for i in range(n) if random.random() < p)
        elif mode == 1:                                           # grown connected cluster
            size = random.randint(1, n)
            D = {random.randrange(n)}
            fr = list(D)
            while len(D) < size and fr:
                u = random.choice(fr)
                nb_ = [v for v in adj[u] if v not in D]
                if not nb_:
                    fr.remove(u)
                    continue
                v = random.choice(nb_)
                D.add(v)
                fr.append(v)
        elif mode == 2:                                           # minority-rich: minority sites plus some neighbours
            p = random.random()
            D = set(i for i in range(n) if eta[i] < 0 and random.random() < p)
            q = random.random()
            D |= set(a for b in list(D) for a in adj[b] if random.random() < q)
        else:                                                     # a cluster plus its closure on majority degree-2 sites
            size = random.randint(1, n // 2)
            D = {random.choice([i for i in range(n) if eta[i] < 0])}
            fr = list(D)
            while len(D) < size and fr:
                u = random.choice(fr)
                nb_ = [v for v in adj[u] if v not in D]
                if not nb_:
                    fr.remove(u)
                    continue
                v = random.choice(nb_)
                D.add(v)
                fr.append(v)
            D |= set(a for a in range(n) if eta[a] > 0 and all(b in D for b in adj[a]))
        if not D:
            continue
        c = sum((u in D) != (v in D) for u, v in E)
        a = sum(1 for i in D if eta[i] > 0)
        b = len(D) - a
        if (c, a, b) in seen:
            continue
        seen.add((c, a, b))
        for B in BS:
            g = gam(B)
            cost = Fr(c, 2) + 2 * B * (a - b)
            cnt += 1
            if cost < g * (a + b):
                viol += 1
            if B == Fr(3, 8):
                r = cost / (a + b)
                worst = r if worst is None else min(worst, r)
    tot += cnt
    say(f"   d = {d}: {len(seen)} distinct triples from 40000 sets, {cnt} exact comparisons; smallest cost/|D| seen at B = 3/8: "
        f"{worst} ({float(worst):.4f}; certified 3/52 = {3/52:.4f}, claimed exact 1/12 = {1/12:.4f})")
check(viol == 0, "a sampled set violates the bound")
say(f"   violations: {viol} in {tot} comparisons")

say(f"\nTOTAL FAILURES: {fails}   [{time.time()-t00:.0f} s]")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item2_L2_out.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
