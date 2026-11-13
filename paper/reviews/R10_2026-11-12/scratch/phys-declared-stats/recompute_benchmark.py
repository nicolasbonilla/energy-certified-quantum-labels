"""R10 reviewer phys-declared-stats: own check of the benchmark numbers of main.tex 912-916 and supplement S9
(206 of 570, 3 of 570, none of nine rows, 558 of 570 within 1 %) from the raw ladder files of the benchmark run
(huang/out_20261031T080637Z/out/ed/chains/*.json and out/chains/*.json), not from the run's summary file.

Outer bound at energy E (Lagrange duality): for a point of sign s at field lam with lower bound F_lo on the ground
energy of H - s*lam*S*O,   s*<O> <= (E - F_lo)/(lam*S).  Width = hi - lo, capped at the label range.
Inner side: convex hull of the stored states (E_k, o_k) and the ground state (two-state mixtures).
"""
import glob
import json
import os
import re

import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
HO = ROOT + "/phase3/full_runs/huang/out_20261031T080637Z/out"
HERE = os.path.dirname(os.path.abspath(__file__))
TAU = 0.08
GRID = [1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3, 1e-2]
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def rj(p):
    with open(p) as f:
        return json.load(f)


def outer(c, E, key="F_lo", dG=0.0):
    lo, hi = c["obounds"]
    S = c["S"]
    up = min(((E - (p[key] - dG)) / (p["lam"] * S) for p in c["points"] if p["sign"] == +1), default=hi)
    dn = min(((E - (p[key] - dG)) / (p["lam"] * S) for p in c["points"] if p["sign"] == -1), default=-lo)
    return max(lo, -dn), min(hi, up)


def w_out(c, eps, dG=0.0):
    a, b = outer(c, c["E0"] + eps, dG=dG)
    return b - a


def eps_tau_out(c, dG=0.0):
    """smallest eps with outer width >= tau (bisection; the outer width is nondecreasing in eps)"""
    hi = c["eps_hi"]
    if w_out(c, hi, dG) < TAU:
        return None
    a, b = 0.0, hi
    for _ in range(200):
        m = 0.5 * (a + b)
        if w_out(c, m, dG) >= TAU:
            b = m
        else:
            a = m
    return b


def hull_extremes(pts, E):
    """max and min of o over mixtures of two stored points with mixture energy <= E. pts: list of (E_k, o_k)."""
    best_hi, best_lo = -np.inf, np.inf
    for i, (e1, o1) in enumerate(pts):
        if e1 <= E:
            best_hi, best_lo = max(best_hi, o1), min(best_lo, o1)
        for (e2, o2) in pts[i + 1:]:
            a, b = ((e1, o1), (e2, o2)) if e1 <= e2 else ((e2, o2), (e1, o1))
            if a[0] <= E < b[0]:
                t = (E - a[0]) / (b[0] - a[0])
                o = a[1] + t * (b[1] - a[1])
                best_hi, best_lo = max(best_hi, o), min(best_lo, o)
    return best_lo, best_hi


def w_in(c, eps, shift=0.0):
    pts = [(c["E0"], c["o_GS"])] + [(p["E"], p["o"]) for p in c["points"]]
    lo, hi = hull_extremes(pts, c["E0"] + eps - shift)
    return hi - lo


def chi_two(c):
    lam0 = c["lam0"]
    op = [p["o"] for p in c["points"] if p["sign"] == +1 and abs(p["lam"] - lam0) < 1e-12]
    om = [p["o"] for p in c["points"] if p["sign"] == -1 and abs(p["lam"] - lam0) < 1e-12]
    assert len(op) == 1 and len(om) == 1, (c["label"], len(op), len(om))
    return (op[0] - om[0]) / (2 * lam0)


def cls_of(i, j, L=4, W=5):
    xi, yi, xj, yj = i // W, i % W, j // W, j % W
    dx, dy = abs(xi - xj), abs(yi - yj)
    if dx + dy == 1:
        return "nn"
    if dx == 1 and dy == 1:
        return "diag"
    return "r<=3" if (dx * dx + dy * dy) ** 0.5 <= 3 else "r>3"


# ------------------------------------------------------------------------------------------------- n = 20 pairs
P("=== n = 20: all 190 pair correlators of each of three instances (exact diagonalization ladders) ===")
tot = {de: 0 for de in GRID}
tot_cls = {}
law_ratio = []
n_pairs = 0
per_inst = {}
max_res = 0.0
gray = 0
for k in (1, 2, 3):
    files = sorted(glob.glob(HO + "/ed/chains/L4_k%d_P_*.json" % k))
    assert len(files) == 190, len(files)
    cnt = {de: 0 for de in GRID}
    for f in files:
        c = rj(f)
        i, j = map(int, re.search(r"P_(\d+)_(\d+)", f).groups())
        n = c["n"]
        assert n == 20 and c["S"] == 1.0 and abs(c["tau"] - TAU) < 1e-15
        max_res = max(max_res, max(p["residual"] for p in c["points"]))
        cl = cls_of(i, j)
        for de in GRID:
            cert = w_out(c, n * de) <= TAU
            notc = w_in(c, n * de) >= TAU
            if not cert and not notc:
                gray += 1
            if cert:
                cnt[de] += 1
                tot[de] += 1
                tot_cls.setdefault((cl, de), 0)
                tot_cls[(cl, de)] += 1
        tot_cls.setdefault((cl, "n"), 0)
        tot_cls[(cl, "n")] += 1
        et = eps_tau_out(c)
        x = chi_two(c)
        de_law = c["S"] * TAU ** 2 / (8 * x * n)
        law_ratio.append((de_law / (et / n), k, i, j, cl, et / n))
        n_pairs += 1
    per_inst[k] = cnt
    P("instance (4,%d): certified at grid de" % k, {("%g" % de): v for de, v in cnt.items()})
P("pairs: %d ; certified at de=1e-3: %d ; at de=1e-2: %d ; gray rows at any grid value: %d ; largest Lanczos residual %.2e" % (
    n_pairs, tot[1e-3], tot[1e-2], gray, max_res))
for cl in ("nn", "diag", "r<=3", "r>3"):
    P("  class %-5s n=%3d certified at 1e-3: %3d ; at 1e-2: %d" % (cl, tot_cls[(cl, "n")], tot_cls.get((cl, 1e-3), 0), tot_cls.get((cl, 1e-2), 0)))
r = np.array([x[0] for x in law_ratio])
P("accuracy law de*_law / de*_out over %d pairs: within 0.3 %%: %d ; within 1 %%: %d ; within 2 %%: %d ; in [0.8, 1.25]: %d ; min %.4f max %.4f median %.4f" % (
    len(r), int((np.abs(r - 1) <= 0.003).sum()), int((np.abs(r - 1) <= 0.01).sum()), int((np.abs(r - 1) <= 0.02).sum()),
    int(((r >= 0.8) & (r <= 1.25)).sum()), r.min(), r.max(), np.median(r)))
out = sorted(law_ratio, key=lambda x: -abs(x[0] - 1))[:14]
P("  the pairs farthest from 1: " + "; ".join("(4,%d) P_%d_%d %s %.4f de*=%.2e" % (x[1], x[2], x[3], x[4], x[0], x[5]) for x in out))
dstar = np.array([x[5] for x in law_ratio])
P("  de* of the 570 pairs: min %.2e median %.2e max %.2e ; number with de* > 1e-3: %d ; > 1e-2: %d" % (
    dstar.min(), np.median(dstar), dstar.max(), int((dstar > 1e-3).sum()), int((dstar > 1e-2).sum())))

# ---------------------------------------------------------------------------------- featured rows at all sizes
P("")
P("=== featured labels: status at the seven grid values (C certified = outer width <= tau; N = inner width >= tau) ===")
refs = {}
for f in glob.glob(HO + "/refs/ref_L*_k*.json"):
    x = rj(f)
    refs[(x["L"], x["k"])] = x
S9 = {}
rows = []
for f in sorted(glob.glob(HO + "/ed/chains/L4_k*_C*.json")) + sorted(glob.glob(HO + "/chains/L[69]_k*_C*.json")):
    c = rj(f)
    L, k, n, lab = c["L"], c["k"], c["n"], c["label"]
    if c["method"] == "DMRG":
        dchi = c["dchi"]
        # declared outer margin: dG = max(2*dchi_c, |G(chi_c) - G(384)| of gate P2 at that instance); P2 exists for (9,1) only
        dG = 2 * dchi
        shift = 2 * dchi
    else:
        dG, shift = 0.0, 0.0
    st = ""
    wi = {}
    for de in GRID:
        wo_ = w_out(c, n * de, dG)
        wi_ = w_in(c, n * de, shift)
        wi[de] = (wi_ / TAU, wo_ / TAU)
        st += "C" if wo_ <= TAU else ("N" if wi_ >= TAU else "G")
    et = eps_tau_out(c, dG)
    x = chi_two(c)
    de_law = c["S"] * TAU ** 2 / (8 * x * n)
    rows.append(dict(L=L, k=k, n=n, label=lab, method=c["method"], status=st, de_out=(et / n if et else None), de_law=de_law,
                     law_over_out=(de_law / (et / n) if et else None), w1=wi[1e-3], w2=wi[1e-2], eps_tau_out=et))
    P("%-6s (%d,%d) n=%2d %-4s status %s  de*_out %s  de*_law %.3e  law/out %s  w/tau at 1e-3 in/out %.2f/%.2f  at 1e-2 %.2f/%.2f" % (
        lab, L, k, n, c["method"], st, ("%.3e" % (et / n)) if et else "None", de_law, ("%.3f" % (de_law / (et / n))) if et else "-",
        wi[1e-3][0], wi[1e-3][1], wi[1e-2][0], wi[1e-2][1]))
loc = [r_ for r_ in rows if r_["label"] in ("Ccent", "Cfar", "Cfix")]
big = [r_ for r_ in loc if r_["n"] > 20]
small = [r_ for r_ in loc if r_["n"] == 20]
P("single-pair rows at n = 30, 45: %d ; certified at any grid value: %d ; NOT certified (rigorous inner side) at every grid value: %d" % (
    len(big), sum("C" in r_["status"] for r_ in big), sum(r_["status"] == "NNNNNNN" for r_ in big)))
P("the same featured single pairs at n = 20: %d rows ; certified at any grid value: %d ; status %s" % (
    len(small), sum("C" in r_["status"] for r_ in small), sorted(set(r_["status"] for r_ in small))))
P("  inner width / tau at de=1e-3: n=20 %s ; n=30,45 %s" % (
    "%.2f-%.2f" % (min(r_["w1"][0] for r_ in small), max(r_["w1"][0] for r_ in small)),
    "%.2f-%.2f" % (min(r_["w1"][0] for r_ in big), max(r_["w1"][0] for r_ in big))))
av = [r_ for r_ in rows if r_["label"] in ("Cnn", "Cd2")]
P("average rows (Cnn, Cd2): %d ; certified at every grid value: %d ; law/out range %.3f-%.3f ; Cnn de*_out %s" % (
    len(av), sum(r_["status"] == "CCCCCCC" for r_ in av), min(r_["law_over_out"] for r_ in av), max(r_["law_over_out"] for r_ in av),
    ", ".join("(%d,%d) %.4f" % (r_["L"], r_["k"], r_["de_out"]) for r_ in av if r_["label"] == "Cnn")))
cnn = {(r_["L"], r_["k"]): r_["de_out"] for r_ in av if r_["label"] == "Cnn"}
m20 = np.mean([cnn[(4, k)] for k in (1, 2, 3)])
P("C-H5(b): Cnn de*(n)/mean de*(20) = %s (declared band [0.67, 1.5])" % ", ".join("(%d,%d) %.3f" % (L, k, cnn[(L, k)] / m20) for (L, k) in ((6, 1), (9, 1), (9, 2))))
fx = {(r_["L"], r_["k"]): r_ for r_ in loc if r_["label"] in ("Cfix",)}
cc = {(r_["L"], r_["k"]): r_ for r_ in loc if r_["label"] == "Ccent"}
for (L, k) in ((6, 1), (9, 1), (9, 2)):
    P("C-H5(a): Cfix eps_tau(n)/eps_tau(20, same k) (%d,%d): %.3f ; de* %.3e vs n=20 %.3e ; 1/n scaling would give %.3e" % (
        L, k, fx[(L, k)]["eps_tau_out"] / cc[(4, k)]["eps_tau_out"], fx[(L, k)]["de_out"], cc[(4, k)]["de_out"], cc[(4, k)]["de_out"] * 20 / fx[(L, k)]["n"]))

json.dump(dict(per_inst={str(k): {("%g" % a): b for a, b in v.items()} for k, v in per_inst.items()}, total={("%g" % a): b for a, b in tot.items()},
               law=[list(map(float, x[:1])) + list(x[1:5]) + [float(x[5])] for x in law_ratio], rows=rows),
          open(os.path.join(HERE, "recompute_benchmark_out.json"), "w"), indent=1)
open(os.path.join(HERE, "recompute_benchmark_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
