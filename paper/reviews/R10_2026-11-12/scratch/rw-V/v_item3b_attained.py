"""v_item3b_attained.py -- verifier V, item 3 (complement): is bound (i), |bd R| >= |R|/2 - 2(d-1), attained by an
ADMISSIBLE region at d = 5, 7, 9 (the v2 text says "bound (i) is attained for d = 3, 5, 7, 9"; the referee's
programme ran over a relaxation)?  Own argument: at |R| = 2(d^2-1) (all minority sites) an optimum of the relaxation
has every minority site with exactly two neighbours in R, hence (degree count) every majority site of R with two
neighbours in R: the induced graph is a union of even cycles, which has a sublattice-exchanging automorphism
(rotate every cycle by one step).  Here: solve the programme, then verify the solution directly.
Output: v_item3b_out.txt
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v_common import patch, adjacency
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import scipy.sparse as sp

lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


for d in (5, 7, 9):
    t0 = time.time()
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    m = len(E)
    k = d * d - 1
    rows, lo, hi = [], [], []
    for e, (u, v) in enumerate(E):
        rows.append({n + e: 1, u: -1, v: 1}); lo.append(0); hi.append(np.inf)
        rows.append({n + e: 1, u: 1, v: -1}); lo.append(0); hi.append(np.inf)
    for b in range(n):
        if eta[b] < 0 and len(adj[b]) == 3:
            c = {b: 1}
            for a in adj[b]:
                c[a] = 1
            rows.append(c); lo.append(-np.inf); hi.append(3)
    rows.append({i: (1 if eta[i] > 0 else -1) for i in range(n)}); lo.append(0); hi.append(0)
    rows.append({i: 1 for i in range(n)}); lo.append(2 * k); hi.append(2 * k)
    A = sp.lil_matrix((len(rows), n + m))
    for r, c in enumerate(rows):
        for j, val in c.items():
            A[r, j] = val
    cost = np.zeros(n + m)
    cost[n:] = 1
    res = milp(c=cost, constraints=LinearConstraint(A.tocsr(), lo, hi), integrality=np.ones(n + m), bounds=Bounds(0, 1),
               options={"time_limit": 120, "mip_rel_gap": 0.0})
    R = [i for i in range(n) if res.x[i] > 0.5]
    Rs = set(R)
    cross = sum((u in Rs) != (v in Rs) for u, v in E)
    degR = {v: sum(1 for u in adj[v] if u in Rs) for v in R}
    two_reg = all(x == 2 for x in degR.values())
    # explicit automorphism: walk each cycle and shift by one step
    pi = {}
    seen = set()
    ncyc = 0
    for s in R:
        if s in seen:
            continue
        cyc = [s]
        seen.add(s)
        prev, cur = None, s
        while True:
            nxt = [u for u in adj[cur] if u in Rs and u != prev]
            nxt = nxt[0]
            if nxt == s:
                break
            cyc.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        ncyc += 1
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            pi[a] = b
    ok_bij = sorted(pi.values()) == sorted(R)
    ok_col = all(eta[pi[v]] == -eta[v] for v in R)
    ok_adj = all((pi[u] in adj[pi[v]]) for v in R for u in adj[v] if u in Rs)
    say(f"d = {d}: optimum of the relaxation at |R| = {2*k}: {round(res.fun)} crossing bonds (status {res.status}); "
        f"|R|/2 - 2(d-1) = {k - 2*(d-1)}; recount {cross}; induced graph 2-regular: {two_reg} ({ncyc} cycles, lengths even); "
        f"explicit map: bijection {ok_bij}, exchanges the sublattices {ok_col}, preserves adjacency {ok_adj} "
        f"-> bound (i) attained by an admissible region: {cross == k - 2*(d-1) and two_reg and ok_bij and ok_col and ok_adj}"
        f"   [{time.time()-t0:.0f} s]")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item3b_out.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
