"""v_item3_PD.py -- verifier V, item 3: the new bound of PD_domain_walls_v2.tex (at least |R|/6 crossing bonds).

Own code. A region R is ADMISSIBLE if the graph induced on R has an automorphism that exchanges the two sublattices.
The proof of bound (ii) uses only two consequences: (P1) R has as many minority as majority sites; (P2) every
minority site of R has at most two neighbours in R.  The proof in fact gives  #minority(R) <= 3 |bd R|  from (P2)
alone.  So I test three nested families:
   F0 = all sets satisfying (P2)                      claim tested:  3 |bd R| >= #minority(R)
   F1 = F0 with (P1)                                  claim tested:  6 |bd R| >= |R|
   F2 = admissible regions (own backtracking search)  claims tested: the numbers printed in the v2 text
 A. d = 3: all 2^19 - 1 sets, exhaustive (F0, F1, F2)
 B. d = 5, 7, 9: integer programmes (scipy.optimize.milp / HiGHS) over F1 for every size |R| = 2k, and over F0;
    plus F1 with the extra necessary condition "equal induced-degree counts on the two sublattices"
 C. the charging argument itself, replayed on random F0 sets at d = 5, 7 (each crossing bond charged <= 3 times)
 D. n = 19, Jz = 4: exact cost E*_n(-c) of lowering m_s (dual), and the smallest bound of part (c)
Output: v_item3_PD_out.txt
"""
import os, sys, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
from v_common import patch, adjacency, sector_states, zmat, hop_matrix, lowest
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import scipy.sparse as sp

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


# ----------------------------------------------------------------------------------------------------------------
def exch_automorphism(R, adj, eta):
    """Is there a bijection pi of R that preserves adjacency inside R and maps each site to the other sublattice?
    Own backtracking search (vertices in BFS order; images must have the same induced degree, opposite colour,
    and be adjacent to the images of already-mapped neighbours / non-adjacent to images of mapped non-neighbours)."""
    R = list(R)
    Rs = set(R)
    nb = {v: [u for u in adj[v] if u in Rs] for v in R}
    dg = {v: len(nb[v]) for v in R}
    maj = [v for v in R if eta[v] > 0]
    mino = [v for v in R if eta[v] < 0]
    if len(maj) != len(mino):
        return False
    if sorted(dg[v] for v in maj) != sorted(dg[v] for v in mino):
        return False
    # BFS order over components
    order, seen = [], set()
    for s in R:
        if s in seen:
            continue
        seen.add(s)
        q = [s]
        while q:
            u = q.pop(0)
            order.append(u)
            for w in nb[u]:
                if w not in seen:
                    seen.add(w)
                    q.append(w)
    img = {}
    used = set()

    def rec(k):
        if k == len(order):
            return True
        v = order[k]
        mapped_nb = [img[u] for u in nb[v] if u in img]
        if mapped_nb:
            cands = [w for w in nb[mapped_nb[0]]]
        else:
            cands = mino if eta[v] > 0 else maj
        for w in cands:
            if w in used or eta[w] == eta[v] or dg[w] != dg[v]:
                continue
            ok = True
            for u in nb[v]:
                if u in img and img[u] not in nb[w]:
                    ok = False
                    break
            if not ok:
                continue
            # non-neighbours already mapped must not map to neighbours of w (count check)
            cnt = sum(1 for x in nb[w] if x in used)
            if cnt != len(mapped_nb):
                continue
            img[v] = w
            used.add(w)
            if rec(k + 1):
                return True
            del img[v]
            used.discard(w)
        return False
    return rec(0)


# ---------------------------------------------------------------------------------------------------------------- A
say("A. d = 3 (n = 19): exhaustive")
n, E, names, eta = patch(3)
adj = adjacency(n, E)
deg = [len(a) for a in adj]
st = np.arange(1, 1 << n, dtype=np.int64)
bits = ((st[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8)
a_cnt = bits[:, eta > 0].sum(axis=1).astype(np.int64)
b_cnt = bits[:, eta < 0].sum(axis=1).astype(np.int64)
bd = np.zeros(len(st), dtype=np.int64)
for i, j in E:
    bd += bits[:, i] ^ bits[:, j]
p2 = np.ones(len(st), dtype=bool)
for b in range(n):
    if eta[b] < 0:
        inn = bits[:, adj[b]].sum(axis=1)
        p2 &= ~((bits[:, b] == 1) & (inn > 2))
F0 = p2
F1 = p2 & (a_cnt == b_cnt)
v0 = int((3 * bd[F0] < b_cnt[F0]).sum())
v1 = int((6 * bd[F1] < 2 * a_cnt[F1]).sum())
check(v0 == 0, "F0 violation at d = 3")
check(v1 == 0, "F1 violation at d = 3")
say(f"   F0 (every minority site of R has at most two neighbours in R): {int(F0.sum())} sets; violations of "
    f"3|bd R| >= #minority(R): {v0}; smallest |bd R|/#minority(R) over sets with a minority site: "
    f"{min(Fr(int(c), int(b)) for c, b in set(zip(bd[F0 & (b_cnt > 0)].tolist(), b_cnt[F0 & (b_cnt > 0)].tolist())))}")
say(f"   F1 (F0 and balanced): {int(F1.sum())} sets of the {int((a_cnt == b_cnt).sum())} balanced ones; violations of "
    f"6|bd R| >= |R|: {v1}; smallest |bd R|/|R| = "
    f"{min(Fr(int(c), 2 * int(a)) for c, a in set(zip(bd[F1].tolist(), a_cnt[F1].tolist())))}")
# without (P2) the bound is false? (shows which hypothesis carries it)
balanced = a_cnt == b_cnt
say(f"   all balanced sets, (P2) dropped: smallest |bd R|/|R| = "
    f"{min(Fr(int(c), 2 * int(a)) for c, a in set(zip(bd[balanced].tolist(), a_cnt[balanced].tolist())))} "
    f"(for comparison; 1/6 = {1/6:.4f})")
# F2: admissible regions
t1 = time.time()
idxF1 = np.nonzero(F1)[0]
adm = np.zeros(len(st), dtype=bool)
for k in idxF1:
    R = [i for i in range(n) if bits[k, i]]
    if exch_automorphism(R, adj, eta):
        adm[k] = True
# balanced sets outside F1 cannot be admissible (P2 is necessary); verify on a sample with the search itself
rng = np.random.default_rng(1)
idx_out = np.nonzero(balanced & ~p2)[0]
samp = rng.choice(idx_out, size=min(3000, len(idx_out)), replace=False)
bad = sum(exch_automorphism([i for i in range(n) if bits[k, i]], adj, eta) for k in samp)
check(bad == 0, "a balanced set violating (P2) has an exchanging automorphism")
nadm = int(adm.sum())
say(f"   F2 (admissible: an automorphism of the induced graph exchanges the sublattices; own search, {time.time()-t1:.0f} s): "
    f"{nadm} of the {int(balanced.sum())} balanced sets [v2 text: 34 317 of 75 581]; "
    f"{len(samp)} sampled balanced sets violating (P2): {bad} admissible")
check(nadm == 34317 and int(balanced.sum()) == 75581, "counts 34317 / 75581")
prof = []
for size in range(2, 18, 2):
    m = adm & (a_cnt + b_cnt == size)
    prof.append(int(bd[m].min()) if m.any() else None)
say(f"   fewest crossing bonds for |R| = 2, 4, ..., 16: {prof} [v2 text: 2, 2, 2, 3, 3, 4, 4, 4]")
check(prof == [2, 2, 2, 3, 3, 4, 4, 4], "profile of fewest crossing bonds")
rat = min(Fr(int(c), int(s)) for c, s in set(zip(bd[adm].tolist(), (a_cnt + b_cnt)[adm].tolist())))
say(f"   smallest |bd R|/|R| over admissible regions: {rat} [v2 text: 1/4]; bound (i) |R|/2 - 2(d-1) = |R|/2 - 4 attained: "
    f"{bool(((bd == (a_cnt + b_cnt) // 2 - 4) & adm).any())} (at |R| = "
    f"{sorted(set((a_cnt + b_cnt)[(bd == (a_cnt + b_cnt) // 2 - 4) & adm].tolist()))}); violated: "
    f"{bool(((bd < (a_cnt + b_cnt) // 2 - 4) & adm).any())}")
check(rat == Fr(1, 4), "min ratio 1/4")
say(f"   6|bd R| >= |R| on admissible regions: violations {int((6 * bd[adm] < (a_cnt + b_cnt)[adm]).sum())}")
adm_bits = bits[adm].copy()
adm_bd = bd[adm].copy()

# ---------------------------------------------------------------------------------------------------------------- B
say("\nB. d = 5, 7, 9: integer programmes")


def ilp(d, k=None, family="F1", degree_match=False, objective="cross", tlim=120):
    """minimise |bd R| (objective 'cross') or 6|bd R| - |R| ('slack6') or 3|bd R| - #minority ('slack3')."""
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    m = len(E)
    nv = n + m
    extra = 0
    rows, lo, hi = [], [], []

    def addrow(coefs, l, h):
        rows.append(coefs)
        lo.append(l)
        hi.append(h)
    for e, (u, v) in enumerate(E):                     # c_e >= r_u - r_v ; c_e >= r_v - r_u
        addrow({n + e: 1, u: -1, v: 1}, 0, np.inf)
        addrow({n + e: 1, u: 1, v: -1}, 0, np.inf)
    for b in range(n):                                 # (P2): r_b + sum_{a ~ b} r_a <= 3 for minority sites of degree 3
        if eta[b] < 0 and len(adj[b]) == 3:
            c = {b: 1}
            for a in adj[b]:
                c[a] = 1
            addrow(c, -np.inf, 3)
    if family == "F1":
        c = {i: (1 if eta[i] > 0 else -1) for i in range(n)}
        addrow(c, 0, 0)
    if k is not None:
        addrow({i: 1 for i in range(n)}, 2 * k, 2 * k)
    else:
        addrow({i: 1 for i in range(n)}, 1, np.inf)
    ncol = nv
    if degree_match:
        # induced degree of v in R: sum_{u~v} r_u - (crossing bonds at v) if v in R.  Number of crossing bonds whose
        # end in R is on a given sublattice must match in total: sum_{v in R, maj} deg_R(v) = sum_{v in R, min} deg_R(v)
        # holds automatically (bipartite).  Necessary condition used: number of sites of R with induced degree 0
        # (isolated in R) is equal on both sublattices is not linear; use instead the linear necessary condition
        #   sum over majority v in R of deg(v) - sum over minority v in R of deg(v) = (cross at maj ends) - (cross at min ends)
        # which is an identity, so no extra constraint: this option is kept only as a label.
        pass
    A = sp.lil_matrix((len(rows), ncol))
    for r, c in enumerate(rows):
        for j, val in c.items():
            A[r, j] = val
    cost = np.zeros(ncol)
    if objective == "cross":
        cost[n:n + m] = 1
    elif objective == "slack6":
        cost[n:n + m] = 6
        cost[:n] = -1
    elif objective == "slack3":
        cost[n:n + m] = 3
        cost[:n] = [-1 if eta[i] < 0 else 0 for i in range(n)]
    res = milp(c=cost, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=np.ones(ncol),
               bounds=Bounds(0, 1), options={"time_limit": tlim, "mip_rel_gap": 0.0})
    return res, n, E, eta


for d in (5, 7, 9):
    t1 = time.time()
    res, n, E, eta = ilp(d, family="F0", objective="slack3")
    ok0 = res.status == 0
    val0 = round(res.fun) if res.x is not None else None
    res, n, E, eta = ilp(d, family="F1", objective="slack6")
    ok1 = res.status == 0
    val1 = round(res.fun) if res.x is not None else None
    check(ok0 and val0 >= 0, f"d = {d}: F0 ILP gives min(3|bd| - #minority) = {val0} (status {res.status})")
    check(ok1 and val1 >= 0, f"d = {d}: F1 ILP gives min(6|bd| - |R|) = {val1}")
    say(f"   d = {d} (n = {n}): min over F0 of 3|bd R| - #minority(R) = {val0} (optimal: {ok0}); "
        f"min over F1 of 6|bd R| - |R| = {val1} (optimal: {ok1})   [{time.time()-t1:.0f} s]")
for d in (5, 7):
    t1 = time.time()
    nmin = d * d - 1
    prof = []
    allopt = True
    for k in range(1, nmin + 1):
        res, n, E, eta = ilp(d, k=k, family="F1", objective="cross", tlim=60)
        if res.x is None:
            prof.append(None)
            continue
        allopt = allopt and res.status == 0
        prof.append(round(res.fun))
    ratios = [Fr(c, 2 * (k + 1)) for k, c in enumerate(prof) if c is not None]
    bi = [c - ((k + 1) - 2 * (d - 1)) for k, c in enumerate(prof) if c is not None]
    viol6 = [(2 * (k + 1), c) for k, c in enumerate(prof) if c is not None and 6 * c < 2 * (k + 1)]
    check(not viol6, f"d = {d}: sizes violating |bd R| >= |R|/6: {viol6}")
    say(f"   d = {d}: fewest crossing bonds over F1 for |R| = 2, 4, ..., {2*nmin}: {prof}")
    say(f"      all optimal: {allopt}; smallest ratio |bd R|/|R| = {min(ratios)} = {float(min(ratios)):.4f} "
        f"[v2 text, the referee's relaxation: at least 0.27]; min of |bd R| - (|R|/2 - 2(d-1)) = {min(bi)} "
        f"(0 means bound (i) is attained in the relaxation, negative would contradict it only for non-admissible sets)"
        f"   [{time.time()-t1:.0f} s]")

# ---------------------------------------------------------------------------------------------------------------- C
say("\nC. the charging argument of the proof, replayed (d = 3 all F0 sets with a minority site: sample; d = 5, 7: random F0 sets)")
random.seed(5)


def charge(R, adj, eta, deg):
    """Assign to each minority site of R a crossing bond exactly as in the v2 proof; return max multiplicity,
    or None if some step of the proof is impossible."""
    Rs = set(R)
    assign = {}
    first = {}
    for b in R:
        if eta[b] < 0 and deg[b] == 3:
            out = [a for a in adj[b] if a not in Rs]
            if not out:
                return None, "degree-3 minority site without a crossing bond"
            first[b] = (b, out[0])
            assign[b] = first[b]
    for b in R:
        if eta[b] < 0 and deg[b] == 2:
            cand = None
            for a in adj[b]:
                if deg[a] == 2:
                    bp = [c for c in adj[a] if c != b][0]
                    if deg[bp] == 3:
                        cand = (a, bp)
                        break
            if cand is None:
                return None, "(S2) fails"
            a, bp = cand
            if a not in Rs:
                assign[b] = (b, a)
            elif bp not in Rs:
                assign[b] = (a, bp)
            else:
                assign[b] = first[bp]
    mult = {}
    for b, e in assign.items():
        if (e[0] in Rs) == (e[1] in Rs):
            return None, "assigned bond is not a crossing bond"
        key = tuple(sorted(e))
        mult[key] = mult.get(key, 0) + 1
    return (max(mult.values()) if mult else 0), len(assign)


for d in (3, 5, 7):
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    deg = [len(a) for a in adj]
    worst = 0
    tested = 0
    for trial in range(20000):
        p = random.random()
        R = [i for i in range(n) if random.random() < p]
        Rs = set(R)
        # enforce (P2) by removing a random neighbour of each offending minority site
        for b in list(R):
            if eta[b] < 0 and b in Rs:
                inn = [a for a in adj[b] if a in Rs]
                if len(inn) > 2:
                    Rs.discard(random.choice(inn))
        R = sorted(Rs)
        if not any(eta[b] < 0 for b in R):
            continue
        mx, info = charge(R, adj, eta, deg)
        tested += 1
        if mx is None:
            check(False, f"d = {d}: charging step impossible: {info}")
            break
        worst = max(worst, mx)
        nb_ = sum(1 for b in R if eta[b] < 0)
        c = sum((u in Rs) != (v in Rs) for u, v in E)
        check(mx <= 3 and 3 * c >= nb_, f"d = {d}: multiplicity {mx} or 3|bd| < #minority")
    say(f"   d = {d}: {tested} random F0 sets; largest number of sites charged to one crossing bond: {worst} (proof: at most 3)")

# ---------------------------------------------------------------------------------------------------------------- D
say("\nD. n = 19, Jz = 4: exact cost of lowering m_s and the smallest bound of part (c)")
n, E, names, eta = patch(3)
Jz = 4.0
nup = int((eta > 0).sum())
stt = sector_states(n, nup)
z = zmat(stt, n)
K = hop_matrix(stt, E, 0.5)
zz = sum(z[:, i] * z[:, j] for i, j in E)
stag = z @ eta
w, v = lowest(K, 0.25 * Jz * zz, k=2)
E0 = w[0]
psi = v[:, 0]
mz = z.T @ (psi * psi)
ms0 = float(mz @ eta / n)
say(f"   E0 = {E0:.6f}, sector gap {w[1]-w[0]:.5f}, m_s = {ms0:.5f}")


def e0nu(nu):                      # lowest level of H + nu * O in the sector, O = sum eta Z
    return lowest(K, 0.25 * Jz * zz + nu * stag, k=1)[0][0]


def estar_minus(c):
    """E*_n(-c) = sup_{nu >= 0} [ E0(H + nu O) - nu n (m_s - c) ] - E0  (concave in nu): golden section."""
    f = lambda nu: e0nu(nu) - nu * n * (ms0 - c) - E0
    lo_, hi_ = 0.0, 0.6
    gr = (5 ** 0.5 - 1) / 2
    x1, x2 = hi_ - gr * (hi_ - lo_), lo_ + gr * (hi_ - lo_)
    f1, f2 = f(x1), f(x2)
    for _ in range(34):
        if f1 < f2:
            lo_, x1, f1 = x1, x2, f2
            x2 = lo_ + gr * (hi_ - lo_)
            f2 = f(x2)
        else:
            hi_, x2, f2 = x2, x1, f1
            x1 = hi_ - gr * (hi_ - lo_)
            f1 = f(x1)
    return max(f1, f2), (lo_ + hi_) / 2


s_spread = max((Jz + 1) / 2, 1.0)
O_R = adm_bits.astype(float) @ (eta * mz)                      # <O_R> for each admissible region
sizeR = adm_bits.sum(axis=1)
true_bound_per_c = n * s_spread * adm_bd / (2 * O_R)           # (c / c_R) kappa / c with the actual c_R
loose_per_c = n * s_spread * adm_bd / (2 * sizeR)              # with c_R <= 2|R|/n
cR = 2 * O_R / n
for c in (0.1, 0.5, 1.0):
    val, nu = estar_minus(c)
    okR = cR >= c
    tb = float((c * true_bound_per_c[okR]).min())
    lb = float((c * loose_per_c[okR]).min())
    say(f"   c = {c}: exact E*_n(-c) = {val:.4f} (attained at field nu = {nu:.4f} = {nu/Jz:.4f} Jz); cost/(c n) = {val/(c*n):.3f}; "
        f"smallest bound of (c) over admissible regions with c_R >= c: {tb:.4f} with the computed <O_R>, "
        f"{lb:.4f} with c_R replaced by 2|R|/n   [v2 text: {dict([(0.1,(0.33,0.59)),(0.5,(1.93,2.96)),(1.0,(3.92,5.93))])[c]}]")
    check(val <= tb + 1e-9, "exact cost exceeds the proposition's bound")
say(f"   (s/12) c n at c = 1: {s_spread/12*n:.4f}; bound (ii) holds for every admissible region: "
    f"{bool((true_bound_per_c >= s_spread * n / 12 - 1e-12).all())}")

say(f"\nTOTAL FAILURES: {fails}   [{time.time()-t00:.0f} s]")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item3_PD_out.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
