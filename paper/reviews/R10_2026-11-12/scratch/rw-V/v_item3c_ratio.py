"""v_item3c_ratio.py -- verifier V, item 3 (complement): exact minimum of |bd R|/|R| over the relaxation F1
(balanced; every minority site of R has at most two neighbours in R) for d = 5, 7, 9, by Dinkelbach iteration on
integer programmes (integer data: minimise q|bd R| - p|R| for a rational p/q).  Output: v_item3c_out.txt"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
from v_common import patch, adjacency
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import scipy.sparse as sp
lines = []
def say(s=""):
    print(s, flush=True); lines.append(s)
for d in (5, 7, 9):
    t0 = time.time()
    n, E, names, eta = patch(d)
    adj = adjacency(n, E)
    m = len(E)
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
    rows.append({i: 1 for i in range(n)}); lo.append(2); hi.append(np.inf)
    A = sp.lil_matrix((len(rows), n + m))
    for r, c in enumerate(rows):
        for j, val in c.items():
            A[r, j] = val
    A = A.tocsr()
    rho = Fr(1, 2)
    it = 0
    while True:
        it += 1
        cost = np.zeros(n + m)
        cost[n:] = rho.denominator
        cost[:n] = -rho.numerator
        res = milp(c=cost, constraints=LinearConstraint(A, lo, hi), integrality=np.ones(n + m), bounds=Bounds(0, 1),
                   options={"time_limit": 300, "mip_rel_gap": 0.0})
        assert res.status == 0, res.message
        R = [i for i in range(n) if res.x[i] > 0.5]
        Rs = set(R)
        cross = sum((u in Rs) != (v in Rs) for u, v in E)
        val = rho.denominator * cross - rho.numerator * len(R)
        if val >= 0:
            break
        rho = Fr(cross, len(R))
    say(f"d = {d} (n = {n}): minimum of |bd R|/|R| over the relaxation = {rho} = {float(rho):.4f} "
        f"({it} programmes, all solved to optimality; last optimum value {val}); >= 0.27: {rho >= Fr(27, 100)}; "
        f">= 1/6: {rho >= Fr(1, 6)}   [{time.time()-t0:.0f} s]")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item3c_out.txt"), "w").write("\n".join(lines) + "\n")
