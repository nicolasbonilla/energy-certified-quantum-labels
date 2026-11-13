# t9_filling_corollary.py -- direct exact test of the reviewer's sector-uniform corollary of Theorem 1(b):
# in a U(1) sector with N up spins on n sites (m = (2N - n)/n), for every site j and every eps >= 0,
#       w_{Z_j}(E0 + eps)  >=  n/(n-1) * (1 - m <Z_j>_GS) * min(1, eps/kappa_2),     kappa_2 = kappa_{j} + kappa_1
# (kappa_1 = largest single-site kappa).  Proof: sum_{k != j} P(j down, k up) = N P(j down), so some k has
# 2 P(j down, k up) >= N (1 - o)/(n-1); likewise 2 P(j up, k' down) >= (n-N)(1 + o)/(n-1); apply Theorem 1(b) to the
# two-site blocks {j,k} and {j,k'} (not necessarily neighbours), whose kappa is at most kappa_{j} + kappa_1.
import time, json
import numpy as np
from r10lib import *

t0 = time.time()
ntest = nviol = nund = 0
minratio = np.inf
rows = []


def run(name, n, edges, Jz, sites, fillings):
    global ntest, nviol, nund, minratio
    S = Spins(n)
    terms = S.xxz_terms(edges, Jz)
    H = total(terms)
    k1 = max(kappa(terms, [i]) for i in range(n))
    for N in fillings:
        idx = S.sector(N)
        Hs = H[idx][:, idx]
        m = (2 * N - n) / n
        for j in sites:
            W = WindowSolver(Hs, S.Z[j][idx][:, idx], dense_below=64, grid=(-4.0, 3.0, 43))
            if W.deg != 1:
                print(f"  {name} N={N} site {j}: degenerate sector ground state (deg {W.deg}), skipped")
                continue
            o = W.oGS_plus
            k2 = kappa(terms, [j]) + k1
            pref = n / (n - 1) * (1 - m * o)
            worst = np.inf
            for eps in (0.02, 0.1, 0.3, 1.0, 0.5 * k2, k2):
                r = W.window(eps, tol=1e-8)
                bound = pref * min(1.0, eps / k2)
                ntest += 1
                if r["w_inner"] >= bound - 1e-8:
                    pass
                elif r["w_outer"] < bound - 1e-8:
                    nviol += 1
                    print("   VIOLATION", name, N, j, eps, r["w_inner"], r["w_outer"], bound)
                else:
                    nund += 1
                if bound > 1e-9:
                    worst = min(worst, r["w_inner"] / bound)
            minratio = min(minratio, worst)
            rows.append(dict(model=name, n=n, N=N, m=m, site=j, oGS=o, kappa_2=k2, prefactor=pref, min_ratio=worst))
            print(f"  {name:22s} N={N:2d} (m={m:+.2f}) site {j}: o_GS={o:+.4f} prefactor n/(n-1)(1-m o)={pref:.4f} kappa_2={k2:.2f} "
                  f"min exact/bound = {worst:.2f}   [{time.time()-t0:.0f} s]", flush=True)


for Jz in (0.6, 1.6, 4.0):
    run(f"chain10 Jz={Jz}", 10, chain(10), Jz, (0, 4, 5), (1, 2, 3, 5, 6, 8, 9))
run("ring10 Jz=1.6", 10, chain(10, True), 1.6, (0,), (1, 3, 5, 7))
run("ladder2x5 Jz=1.6", 10, ladder(5), 1.6, (4, 5), (2, 5, 6))
hh13 = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (4, 8), (5, 9), (5, 10), (6, 11), (6, 12)]
run("heavy-hex tree13 Jz=1.6", 13, hh13, 1.6, (0, 1, 7), (9, 8, 4))
print(f"\nfilling corollary: {ntest} exact tests, violations {nviol}, undecided {nund}, smallest exact/bound ratio {minratio:.3f}")
json.dump(rows, open("t9_filling_corollary.json", "w"), indent=1)
print("time %.0f s" % (time.time() - t0))
