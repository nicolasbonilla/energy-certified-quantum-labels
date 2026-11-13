# t3_looseness.py -- the "six to seven times" looseness of N* = kappa_A/de (main.tex 365-366, supplement 129-136,
# 278-281, 1190-1197).  Transverse-field Ising chain H = -sum Z Z - h sum X, label Z at one site.
#   part A: exact energy at which the window is EXACTLY the full range, eps_full = E_sat - E0, for n up to 27
#           (E0 by free fermions, E_sat = two half chains with a boundary field, by sparse ED)
#   part B: exact widths at fixed error per site for n = 4..13 (open chain, centre; periodic chain), all integers n
#   part C: energy at which the width reaches 99 % of the range; looseness factors for several fields h
import sys, time, json
import numpy as np
from r10lib import *

t0 = time.time()
out = {}


def e0_tfim_open_ff(n, J=1.0, h=1.5):
    """ground energy of the open chain by free fermions: -sum of the singular values of h*1 - J*superdiagonal."""
    M = h * np.eye(n) - J * np.diag(np.ones(n - 1), 1)
    return -float(np.linalg.svd(M, compute_uv=False).sum())


def e_half(m, J=1.0, h=1.5):
    """ground energy of an open chain of m sites with a boundary field -J Z on its last site (frozen neighbour up)."""
    if m == 0:
        return 0.0
    S = Spins(m)
    H = total(S.tfim_terms(chain(m), J=J, h=h)) - J * S.Z[m - 1]
    w, _ = lowest(realify(H), k=1)
    return float(w[0])


print("== part A: exact full-range energy eps_full(n) = E_sat - E0, open chain, Z at site c ==")
print("   (kappa_A = 2 + 2 + 2h for an interior site; the reset bound says full range once eps >= kappa_A)")
partA = {}
for h in (1.5,):
    kap = 4 + 2 * h
    half_cache = {}
    rows = []
    for n in list(range(3, 28)):
        c = n // 2
        mL, mR = c, n - 1 - c
        for m in (mL, mR):
            if m not in half_cache:
                half_cache[m] = e_half(m, h=h)
        E0 = e0_tfim_open_ff(n, h=h)
        eps_full = half_cache[mL] + half_cache[mR] - E0
        rows.append((n, E0, eps_full))
        print(f"  h={h} n={n:2d}  E0={E0:.8f}  eps_full={eps_full:.6f}  kappa_A/eps_full={kap/eps_full:.3f}", flush=True)
    partA[str(h)] = rows
    # cross-check E0 by ED at n = 8, 10
    for n in (8, 10):
        S = Spins(n)
        w, _ = lowest(total(S.tfim_terms(chain(n), h=h)), k=1)
        print(f"  check: n={n} E0(ED)={w[0]:.8f}  E0(free fermions)={e0_tfim_open_ff(n, h=h):.8f}")
    eps_inf = rows[-1][2]
    for de in (0.05, 0.1, 0.2):
        nfull = next((n for (n, _, e) in rows if n * de >= e), None)
        print(f"  h={h} de={de}: N*={kap/de:.1f}; smallest n with n*de >= eps_full(n): {nfull}; "
              f"eps_full(n=27)/de = {eps_inf/de:.2f}; N*/that = {kap/eps_inf:.2f}")
out["partA"] = partA
print("  time %.0f s" % (time.time() - t0), flush=True)

print("\n== part B: exact width of Z at fixed error per site (inner = explicit states, outer = dual) ==")
partB = {}
for geom in ("open-centre", "periodic"):
    for n in range(4, 13):
        S = Spins(n)
        edges = chain(n, periodic=(geom == "periodic"))
        H = total(S.tfim_terms(edges, h=1.5))
        site = n // 2 if geom == "open-centre" else 0
        W = WindowSolver(H, S.Z[site], grid=(-3.0, 2.0, 31))
        line = []
        for de in (0.05, 0.1, 0.2):
            r = W.extreme(n * de, +1, tol=1e-8)          # Z2 symmetry: the window is symmetric, width = 2 u_+
            wi, wo = 2 * r["inner"], 2 * r["outer"]
            partB[f"{geom}|{n}|{de}"] = (wi, wo, bool(r["saturated"]))
            line.append(f"de={de}: w={wi:.4f}/{wo:.4f}{'*' if r['saturated'] else ' '}")
        eps_full = W.Esat_plus - W.E0
        partB[f"{geom}|{n}|eps_full"] = eps_full
        print(f"  {geom:11s} n={n:2d} site={site} E0={W.E0:.6f} eps_full={eps_full:.4f} | " + " | ".join(line)
              + f"   [{time.time()-t0:.0f} s, {W.nsolve} solves]", flush=True)
out["partB"] = partB
for geom in ("open-centre", "periodic"):
    for de in (0.05, 0.1, 0.2):
        ns = [n for n in range(4, 13)]
        n99 = next((n for n in ns if partB[f"{geom}|{n}|{de}"][0] >= 1.98), None)
        n99e = next((n for n in ns if n % 2 == 0 and partB[f"{geom}|{n}|{de}"][0] >= 1.98), None)
        nfull = next((n for n in ns if partB[f"{geom}|{n}|{de}"][2]), None)
        print(f"  {geom:11s} de={de}: N*={7/de:.0f}; first n with width >= 99% of range: {n99} (even n only: {n99e}); "
              f"first n with EXACTLY the full range: {nfull};  N*/n99 = {7/de/n99 if n99 else float('nan'):.2f}, "
              f"N*/n_full = {7/de/nfull if nfull else float('nan'):.2f}")

print("\n== part C: energy at which the width reaches 99 % of the range, and looseness for other fields h (n = 10) ==")
partC = {}
n = 10
S = Spins(n)
for h in (0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0):
    H = total(S.tfim_terms(chain(n), h=h))
    W = WindowSolver(H, S.Z[n // 2], grid=(-3.0, 2.0, 31))
    kap = 4 + 2 * h
    eps_full = W.Esat_plus - W.E0
    # bisection for u_+ = 0.99
    lo, hi = 1e-4, eps_full
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if W.extreme(mid, +1, tol=1e-8)["inner"] >= 0.99:
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-5:
            break
    partC[str(h)] = dict(kappa=kap, eps_full=eps_full, eps_99=hi, gap=W.gap)
    print(f"  h={h:3.1f}: kappa_A={kap:5.1f}  gap={W.gap:.4f}  eps_99={hi:.4f}  eps_full={eps_full:.4f}   "
          f"kappa/eps_99={kap/hi:6.2f}   kappa/eps_full={kap/eps_full:6.2f}   [{time.time()-t0:.0f} s]", flush=True)
out["partC"] = partC
json.dump(out, open("t3_looseness.json", "w"), indent=1)
print("total time %.0f s" % (time.time() - t0))
