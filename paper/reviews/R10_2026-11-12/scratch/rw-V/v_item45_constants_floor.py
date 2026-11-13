"""v_item45_constants_floor.py -- verifier V.
PART 1 (item 4): the constants of theorem4_v2.tex by direct summation (mpmath, 40 digits):
        Phi_*, Phi_*', mu_0, mu_0', the m_s constant, C1bar of Eq. (C1bar); and the counting behind Phi_*'
        checked on the real patches d = 3, 5, 7 (edges and P2 pairs leaving a merged set X).
PART 2 (item 4): the remark "Theorem 2(c) as stated, for the pair labels": on the real patches, the assignment
        of edges to minority ends and of P2 pairs to common neighbours; ||o_i|| <= n/S <= 1; sum_i o_i = n O/3.
PART 3 (item 4): the ten-site cell on the tori: the lattice of translations and the quotient.
PART 4 (item 5): F1_floor_v2.tex: floors recomputed from the stored intervals (read-only), the level at n = 115,
        the width-normalized counterexample, and a Monte Carlo of parts (i), (iii), (v).
Output: v_item45_out.txt
"""
import os, sys, json, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
import numpy as np
import mpmath as mp
from v_common import patch, adjacency, bfs_dist, pairs_dist2

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
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


mp.mp.dps = 40
# ---------------------------------------------------------------------------------------------------------------- 1
say("PART 1. constants of Theorem 4 (tau = 1/16, delta_0 = 0.05, lambda = 1)")
tau = mp.mpf(1) / 16
d0 = mp.mpf("0.05")
e = mp.e
Phi = 4 * (mp.mpf(3) / 8 + tau) + 24 * e * (3 + 4 * tau) + 128 * e ** 2 * tau
# rebuilt term by term: sites 1*norm*N^2, edges 3 * 2 * norm * N^4 * e, pairs 4 * 2 * norm * N^4 * e^2 with N = 2
Phi_b = 1 * (mp.mpf(3) / 8 + tau) * 4 + 3 * 2 * (mp.mpf(3) / 4 + tau) * 16 * e + 4 * 2 * tau * 16 * e ** 2
check(abs(Phi - Phi_b) < mp.mpf(10) ** -30, "Phi_* formula")
# merged site, N = 8: weight of a term on k (merged) sites of diameter D: k * 64^k * e^D
Phip = 64 * (mp.mpf(21) / 8 + 6 * tau) + 40960 * e * (mp.mpf(3) / 4 + tau) + 98304 * e ** 2 * tau
inside = 3 * (mp.mpf(3) / 8 + tau) + 2 * (mp.mpf(3) / 4 + tau) + 1 * tau          # 3 sites, 2 edges, 1 pair
Phip_b = 1 * 64 * inside + 5 * (2 * 64 ** 2 * e) * (mp.mpf(3) / 4 + tau) + 12 * (2 * 64 ** 2 * e ** 2) * tau
check(abs(inside - (mp.mpf(21) / 8 + 6 * tau)) < mp.mpf(10) ** -30, "norm of the merged single-site term")
check(abs(Phip - Phip_b) < mp.mpf(10) ** -25, "Phi_*' formula")
other = 64 * (mp.mpf(3) / 8 + tau) + 24576 * e * (mp.mpf(3) / 4 + tau) + 32768 * e ** 2 * tau
other_b = 64 * (mp.mpf(3) / 8 + tau) + 3 * (2 * 64 ** 2 * e) * (mp.mpf(3) / 4 + tau) + 4 * (2 * 64 ** 2 * e ** 2) * tau
check(abs(other - other_b) < mp.mpf(10) ** -25 and other < Phip, "sum at another site")
mu0 = d0 / (4 * Phi + d0)
mu0p = d0 / (4 * Phip + d0)
say(f"   Phi_*  = {mp.nstr(Phi, 8)}   [text: about 273]      mu_0  = {mp.nstr(mu0, 6)}   [text: about 4.6e-5]")
say(f"   Phi_*' = {mp.nstr(Phip, 8)}   [text: about 1.4e5]    mu_0' = {mp.nstr(mu0p, 6)}   [text: about 9e-8];  "
    f"sum at any other site = {mp.nstr(other, 8)} < Phi_*': {other < Phip};  mu_0' <= mu_0: {mu0p <= mu0}")


def series(mu, coef):                     # sum_{m>=1} coef (2m+1)^2 e^{-mu m}, closed form
    q = mp.e ** (-mu)
    s0 = q / (1 - q)
    s1 = q / (1 - q) ** 2
    s2 = q * (1 + q) / (1 - q) ** 3
    return coef * (4 * s2 + 4 * s1 + s0)


C0 = 2 * (1 + 2 / mp.pi + 1 / mp.sqrt(mp.pi * mu0))
Cms = 1 + C0 * series(mu0, 3)
C0p = 2 * (1 + 4 / mp.pi + 1 / mp.sqrt(mp.pi * mu0p))
C1bar = 12 + C0p * series(mu0p, 36)
# brute-force partial sum as a cross-check of the closed form (coarse mu to keep it short)
mu_t = mp.mpf("0.01")
bf = mp.nsum(lambda m: 3 * (2 * m + 1) ** 2 * mp.e ** (-mu_t * m), [1, mp.inf])
check(abs(bf - series(mu_t, 3)) / bf < mp.mpf(10) ** -20, "closed form of the series")
say(f"   constant found for m_s alone: 1 + C_0 sum 3(2m+1)^2 e^(-mu_0 m) = {mp.nstr(Cms, 5)}   [text: exceeds 4e16]: {Cms > 4e16}")
say(f"   C1bar of Eq. (C1bar): 12 + C_0' sum 36(2m+1)^2 e^(-mu_0' m) = {mp.nstr(C1bar, 5)}   [text: exceeds 1e27]: {C1bar > 1e27}")
say(f"   the first draft's '> 1e16' is the m_s constant, not C1bar: {Cms > 1e16 and C1bar > 1e27}")
check(Cms > 4e16 and C1bar > mp.mpf(10) ** 27, "constants")
# counting on the real patches: for every connected X with |X| <= 3 (single sites, edges, P2 pairs with their common neighbour)
say("   counting behind Phi_*' on the real patches (X = an edge, or a P2 pair with its common neighbour):")
for d in (3, 5, 7, 9):
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    P2 = pairs_dist2(n, E)
    Eset = [frozenset(x) for x in E]
    P2set = [frozenset(x) for x in P2]
    D = bfs_dist(n, E)
    per_site_pairs = max(sum(1 for p in P2set if i in p) for i in range(n))
    cn_ok = all(sum(1 for k in range(n) if D[i, k] == 1 and D[j, k] == 1) == 1 for i, j in P2)
    worst = dict(ext_edges=0, ext_pairs=0, in_edges=0, in_pairs=0, meet=0, nb12=0)
    Xs = [set(e_) for e_ in Eset] + [set(p) | {k for k in range(n) if all(D[q, k] == 1 for q in p)} for p in P2set]
    for X in Xs:
        ee = sum(1 for e_ in Eset if len(e_ & X) == 1)
        ie = sum(1 for e_ in Eset if e_ <= X)
        ep = sum(1 for p in P2set if len(p & X) == 1)
        ip = sum(1 for p in P2set if p <= X)
        worst["ext_edges"] = max(worst["ext_edges"], ee)
        worst["in_edges"] = max(worst["in_edges"], ie)
        worst["ext_pairs"] = max(worst["ext_pairs"], ep)
        worst["in_pairs"] = max(worst["in_pairs"], ip)
        worst["meet"] = max(worst["meet"], sum(1 for p in P2set if p & X), sum(1 for e_ in Eset if e_ & X))
    # pairs at distance m >= 1 from X_p against 36 (2m+1)^2 ; balls against 3 (2m+1)^2
    okball = True
    okpairs = True
    for i in range(n):
        for m in range(0, 8):
            if (D[i] <= m).sum() > 3 * (2 * m + 1) ** 2:
                okball = False
    for X in Xs[::7]:
        dX = D[list(X)].min(axis=0)
        for m in range(1, 8):
            cnt = sum(1 for p in P2set if min(dX[q] for q in p) == m) if len(X) == 3 else \
                  sum(1 for e_ in Eset if min(dX[q] for q in e_) == m)
            if cnt > 36 * (2 * m + 1) ** 2:
                okpairs = False
    say(f"      d = {d}: |P2| = {len(P2)} (formula {(9*d*d-10*d-1)//2}); S >= n: |E| {len(E)} >= {n}, |P2| {len(P2)} >= {n}; "
        f"pairs per site <= {per_site_pairs}; one common neighbour per pair: {cn_ok}; over all X: edges leaving X <= "
        f"{worst['ext_edges']} (text 5), pairs with one site in X <= {worst['ext_pairs']} (text 12), edges inside <= "
        f"{worst['in_edges']} (2), pairs inside <= {worst['in_pairs']} (1), pairs or edges meeting X <= {worst['meet']} (12); "
        f"balls <= 3(2m+1)^2: {okball}; pairs at distance m <= 36(2m+1)^2: {okpairs}")
    check(len(P2) == (9 * d * d - 10 * d - 1) // 2 and len(E) >= n and len(P2) >= n and per_site_pairs <= 4 and cn_ok
          and worst["ext_edges"] <= 5 and worst["ext_pairs"] <= 12 and worst["in_edges"] <= 2 and worst["in_pairs"] <= 1
          and worst["meet"] <= 12 and okball and okpairs, f"counting at d = {d}")

# ---------------------------------------------------------------------------------------------------------------- 2
say("\nPART 2. 'Theorem 2(c) as stated' for the two pair labels: o_i = (n/3S) sum_{p -> i} Z_p")
for d in (3, 5, 7, 9, 11):
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    P2 = pairs_dist2(n, E)
    D = bfs_dist(n, E)
    # edges -> minority end
    recv_e = [0] * n
    for a, b in E:
        m_ = a if eta[a] < 0 else b
        check(eta[a] != eta[b], "edge not bipartite")
        recv_e[m_] += 1
    recv_p = [0] * n
    for i, j in P2:
        cn = [k for k in range(n) if D[i, k] == 1 and D[j, k] == 1]
        check(len(cn) == 1, "pair without a unique common neighbour")
        recv_p[cn[0]] += 1
    SE, SP = len(E), len(P2)
    ok = (max(recv_e) <= 3 and max(recv_p) <= 3 and sum(recv_e) == SE and sum(recv_p) == SP
          and Fr(n, 3 * SE) * max(recv_e) <= 1 and Fr(n, 3 * SP) * max(recv_p) <= 1 and SE >= n and SP >= n)
    check(ok, f"assignment at d = {d}")
    say(f"   d = {d}: a site receives at most {max(recv_e)} edges and {max(recv_p)} pairs; ||o_i|| <= n/S = "
        f"{Fr(n, SE)} (edges), {Fr(n, SP)} (pairs), both <= 1: {SE >= n and SP >= n}; (1/n) sum_i o_i = O/3 (every edge and "
        f"pair assigned exactly once): {sum(recv_e) == SE and sum(recv_p) == SP}")
say("   cost bound: Theorem 3(c) for O/3 with chibar' = 2(C1bar/3)/(delta_0 Jz): moving O by c moves O/3 by c/3, cost >= "
    "n (c/3)^2/(2 chibar') = n c^2 delta_0 Jz/(12 C1bar); Eq. (linear) gives n c^2 delta_0 Jz/(4 C1bar): ratio "
    f"{Fr(1,12)/Fr(1,4)} (three times weaker): {Fr(1, 9) * Fr(3, 4) == Fr(1, 12)}")
check(Fr(1, 9) * Fr(3, 4) == Fr(1, 12), "factor 12")

# ---------------------------------------------------------------------------------------------------------------- 3
say("\nPART 3. the ten-site cell on the tori")
# lattice Gamma: D(i,j), F(i,j) for all (i,j); S(i,j) for i+j odd.  Translations preserving it: (a,b) with a+b even.
# primitive: u = (1,1), v = (1,-1) (5 sites per cell); cell of (2,0),(0,2): 10 sites.  Torus T_L = Gamma/<(2L,0),(0,2L)>.
for L in (3, 4, 5):
    sites = [(k, i, j) for i in range(2 * L) for j in range(2 * L) for k in "DF"] + \
            [("S", i, j) for i in range(2 * L) for j in range(2 * L) if (i + j) % 2 == 1]
    nT = len(sites)
    edges = []
    for i in range(2 * L):
        for j in range(2 * L):
            edges.append((("F", i, j), ("D", i, j)))
            edges.append((("F", i, j), ("D", i, (j + 1) % (2 * L))))
            if (i + j) % 2 == 1:
                edges.append((("S", i, j), ("F", i, j)))
                edges.append((("S", i, j), ("F", (i + 1) % (2 * L), j)))
    # (2L,0) = L u + L v ; (0,2L) = L u - L v : index of <(L,L),(L,-L)> in Z^2 (u,v coordinates) = |det| = 2 L^2
    det_prim = abs(L * (-L) - L * L)
    # in the coordinates of the (2,0),(0,2) lattice the torus is (Z/L)^2 with L^2 cells
    ok = (nT == 10 * L * L and len(edges) == 12 * L * L and det_prim == 2 * L * L and 5 * det_prim == nT and 10 * L * L == nT)
    # is Z^2/<(L,L),(L,-L)> isomorphic to (Z/L)^2 ?  its invariant factors are those of [[L,L],[L,-L]]: gcd = L, det/gcd = 2L
    inv = (math.gcd(L, L), det_prim // math.gcd(L, L))
    check(ok and inv != (L, L), f"torus L = {L}")
    say(f"   L = {L}: n = {nT} = 10 L^2, |E| = {len(edges)} = 12 L^2 (twelve edges per ten-site cell); with the five-site primitive "
        f"cell the torus has {det_prim} = 2 L^2 cells and is Z^2/<(L,L),(L,-L)> = Z/{inv[0]} x Z/{inv[1]}, not (Z/{L})^2; "
        f"with the ten-site cell it is (Z/{L})^2 with {L*L} cells")
say(f"   beta = (c/Jz) x 12 edges x ||(XX+YY)/4|| = (c/Jz) x 12 x 1/2 = 6 c/Jz")

# ---------------------------------------------------------------------------------------------------------------- 4
say("\nPART 4. F1 (floor): stored intervals of learning_ibm/out/prop2_cubic.json (read-only)")
P = json.load(open(f"{ROOT}/phase3/full_runs/learning_ibm/out/prop2_cubic.json"))
alpha = P["alpha"]
for size in ("57", "115"):
    S = P["sizes"][size]
    train = S["train"]
    tauq = {r["Jz"]: r["tau"] for r in S["indist"] + S["ood"]}
    w = {}
    cen = {}
    for jz in train:
        key = str(jz)
        if key in S["intervals"] and jz not in S.get("missing_rows", []):
            lo, hi = S["intervals"][key]["inner"]
            w[jz] = hi - lo
            cen[jz] = (hi + lo) / 2
        else:
            w[jz] = 0.0
    say(f" n = {size}: training couplings {train}; widths of the lower version in own tolerances: "
        + ", ".join(f"{jz}: {w[jz]/tauq[jz]:.4f}" for jz in train))
    rng = []
    for q in train:
        others = sorted(w[j] for j in train if j != q)
        m = len(others)
        k = math.ceil((m + 1) * (1 - alpha) - 1e-12)
        fl = others[k - 1] if k <= m else math.inf
        rng.append((q, m, k, fl / tauq[q], max(others) / tauq[q]))
    test = [r["Jz"] for r in S["ood"]]
    rng_t = []
    allw = sorted(w[j] for j in train)
    m = len(allw)
    k = math.ceil((m + 1) * (1 - alpha) - 1e-12)
    for q in test:
        fl = allw[k - 1] if k <= m else math.inf
        rng_t.append((q, m, k, fl / tauq[q], max(allw) / tauq[q]))
    say(f"   training range: m = {rng[0][1]}, k = ceil((m+1)(1-alpha)) = {rng[0][2]}"
        f"{' > m: q = +infinity' if rng[0][2] > rng[0][1] else ''}; floor w_(k)/tau: "
        + ", ".join(f"{q}: {f:.4f}" for q, m_, k_, f, mx in rng))
    say(f"      floor of the largest score (nominal level m/(m+1) = {rng[0][1]}/{rng[0][1]+1}): "
        + ", ".join(f"{q}: {mx:.4f}" for q, m_, k_, f, mx in rng)
        + f"   -> range {min(r[4] for r in rng):.4f} .. {max(r[4] for r in rng):.4f}")
    say(f"   test range: m = {rng_t[0][1]}, k = {rng_t[0][2]}{' > m: q = +infinity' if rng_t[0][2] > rng_t[0][1] else ''}; "
        f"floor w_(k)/tau: " + ", ".join(f"{q}: {f:.4f}" for q, m_, k_, f, mx in rng_t)
        + f"; largest score: {min(r[4] for r in rng_t):.4f} .. {max(r[4] for r in rng_t):.4f}")
    # the cubic model's stored 2 q against the floor of the largest score
    rat = []
    for r in S["indist"]:
        mx = max(w[j] for j in train if j != r["Jz"])
        rat.append(2 * r["q_lo"] / mx)
        # every stored score dominates half the width of its interval
        for cs in r["calib_scores"]:
            check(cs["s_lo"] >= w[cs["Jz"]] / 2 - 1e-12, f"score below w/2 at {cs['Jz']}")
    for r in S["ood"]:
        rat.append(2 * r["q_lo"] / max(allw))
        for cs in r["calib_scores"]:
            check(cs["s_lo"] >= w[cs["Jz"]] / 2 - 1e-12, f"score below w/2 at {cs['Jz']}")
    say(f"   stored 2q of the cubic model / floor of the largest score: {min(rat):.4f} .. {max(rat):.4f}; every stored score "
        f">= half the width of its interval: checked")
    if size == "57":
        rows8 = [j for j in train if w[j] > 0]
        say(f"   width-normalized score on the {len(rows8)} couplings with a map row, hold one out, alpha = 1/{len(rows8)}:")
        m = len(rows8) - 1
        a8 = 1 / len(rows8)
        k = math.ceil((m + 1) * (1 - a8) - 1e-12)
        check(k == m, "k for the leave-one-out example")
        # sigma = A Jz^-p, least squares in log-log on the eight widths
        X = np.log(np.array(rows8))
        Y = np.log(np.array([w[j] for j in rows8]))
        p_, logA = np.polyfit(X, Y, 1)
        sig = {j: math.exp(logA) * j ** p_ for j in rows8}
        for nm, sg in (("sigma(x) = A Jz^p fitted to the eight widths, p = %.3f" % p_, sig), ("sigma(x) = w(x)", {j: w[j] for j in rows8})):
            res = []
            for q in rows8:
                sc = sorted((w[j] / 2) / sg[j] for j in rows8 if j != q)
                qq = sc[k - 1]
                width = 2 * qq * sg[q]
                res.append((q, width / tauq[q], width >= w[q] - 1e-15))
            ncont = sum(1 for r in res if r[2])
            ans = [r[0] for r in res if r[1] <= 1]
            wider = sum(1 for j in rows8 if w[j] > tauq[j])
            say(f"      {nm}: width/tau " + ", ".join(f"{q}: {x:.4f}{'' if c else '*'}" for q, x, c in res)
                + f"; contains the query's energy interval at {ncont} of {len(rows8)} (* = not); rule (c) answers at {ans}; "
                f"intervals wider than their own tolerance: {wider} of {len(rows8)}")
        for q in (4.0, 5.0, 6.0):
            say(f"      query {q}: calibration intervals wider than the tolerance at the query: "
                f"{sum(1 for j in rows8 if j != q and w[j] > tauq[q])} of {m}; constant-width floor there: "
                f"{max(w[j] for j in rows8 if j != q)/tauq[q]:.3f} tau")

say("\n   Monte Carlo of parts (i), (iii), (v) (own draws; exchangeable pairs (x, I(x)))")
rng_ = np.random.default_rng(11)
for (alpha_, m) in ((0.1, 9), (0.1, 19), (0.2, 14), (0.1, 45)):
    k = math.ceil((m + 1) * (1 - alpha_) - 1e-12)
    T = 100000
    wj = rng_.lognormal(0.0, 1.0, size=(T, m + 1))                       # widths, last column = the query
    cj = rng_.normal(0, 1, size=(T, m + 1))                              # centres
    fj = cj + rng_.normal(0, 0.3, size=(T, m + 1)) * rng_.integers(0, 2, size=(T, m + 1))   # some midpoints, some off
    s = np.abs(fj - cj) + wj / 2                                         # max_{y in I} |f - y|
    q = np.sort(s[:, :m], axis=1)[:, k - 1]
    cover = (s[:, m] <= q).mean()
    wk = np.sort(wj[:, :m], axis=1)[:, k - 1]
    below = (2 * q < wk - 1e-12).sum()
    # normalized by the width, midpoint predictions: interval = I(x) exactly
    s2 = (wj / 2) / wj
    q2 = np.sort(s2[:, :m], axis=1)[:, k - 1]
    exact = np.allclose(2 * q2 * wj[:, m], wj[:, m])
    say(f"      alpha = {alpha_}, m = {m}, k = {k}: 2q < w_(k) in {below} of {T} draws; frequency of I(x) inside C(x) = {cover:.4f} "
        f"(bound {1-alpha_:.2f}, exact k/(m+1) = {k/(m+1):.4f}); width-normalized with midpoints gives exactly I(x): {exact}")
    check(below == 0 and cover >= 1 - alpha_ - 0.004 and exact, "Monte Carlo of F1")

say(f"\nTOTAL FAILURES: {fails}")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item45_out.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
