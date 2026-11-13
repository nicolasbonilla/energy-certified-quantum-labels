"""R10 reviewer phys-declared-stats: remaining exploratory numbers of Sec. V (main.tex 659-702), recomputed from the
stored outputs: the cubic learner on corrected labels, the ceiling fraction, the energy-reference nulls, the log-log
slopes, the internal checks, and the comparison with stored results.json.  Reads only."""
import glob
import json
import os
import re

import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
M = ROOT + "/phase3/full_runs/method/out_20261030T003230Z/out"
BL = ROOT + "/phase3/full_runs/bias_law"
HERE = os.path.dirname(os.path.abspath(__file__))
NE = {19: 20, 57: 64, 115: 132}
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def rj(p):
    with open(p) as f:
        return json.load(f)


C = {float(k): v for k, v in rj(BL + "/inputs/n19_curves.json").items()}
R = rj(BL + "/out/results.json")


def grid(n):
    return sorted(float(re.search(r"_J([0-9.]+)\.json", f).group(1)) for f in glob.glob("%s/emu/emu_n%d_J*.json" % (M, n)))


def emu(n, J):
    return rj("%s/emu/emu_n%d_J%s.json" % (M, n, J))


def curve19(J, de):
    c = np.array(C[J]["curve"])
    return float(np.interp(np.sqrt(max(de, 0.0)), np.sqrt(np.maximum(c[:, 0], 0.0)), c[:, 1]))


def cmp(name, mine, stored, tol=5e-4):
    ok = abs(mine - stored) <= tol * max(1.0, abs(stored))
    P("  %-46s mine %.4f stored %.4f %s" % (name, mine, stored, "OK" if ok else "DIFFERS"))


P("=== cubic learner in 1/Jz trained on the training couplings (Jz >= 1.6), tested at Jz = 1.1-1.4 ===")
for n in (57, 115):
    rs = []
    for J in grid(n):
        e = emu(n, J)
        v = e["var"]["primary"]
        rs.append(dict(J=J, m=v["labels"]["m_s"], m0=e["ref_m_s"], de=v["dE_site"]))
    tr = [r for r in rs if r["J"] >= 1.6]
    te = [r for r in rs if r["J"] < 1.5]
    X = lambda q: np.array([[1, 1 / r["J"], 1 / r["J"] ** 2, 1 / r["J"] ** 3] for r in q])
    targets = dict(raw=[r["m"] for r in tr], corrected=[r["m"] - curve19(r["J"], r["de"]) for r in tr], exact=[r["m0"] for r in tr])
    for k, y in targets.items():
        c = np.linalg.lstsq(X(tr), np.array(y), rcond=None)[0]
        miss = [abs(float(X([r])[0] @ c) - r["m0"]) / (.06 * r["m0"]) for r in te]
        P("  n=%d trained on %-9s labels (%d couplings): test misses %s" % (n, k, len(tr), np.round(miss, 3).tolist()))
        cmp("    min", min(miss), R["learner"][str(n)][k]["min"])
        cmp("    max", max(miss), R["learner"][str(n)][k]["max"])
P("  note: a cubic has 4 parameters; n=57 uses 10 training couplings, n=115 uses 7")

P("")
P("=== ceiling, energy-reference nulls ===")
ceil = [emu(115, J)["var"]["primary"]["err"]["dm_s"] / (1 - emu(115, J)["ref_m_s"]) for J in grid(115) if J <= 1.6]
P("  bias / (1 - m_s^GS) at n=115, Jz <= 1.6 (%d couplings): %s" % (len(ceil), np.round(ceil, 3).tolist()))
ceil57 = [emu(57, J)["var"]["primary"]["err"]["dm_s"] / (1 - emu(57, J)["ref_m_s"]) for J in grid(57) if J <= 1.6]
P("  the same at n=57: %s" % np.round(ceil57, 3).tolist())
rows = []
for J in grid(115):
    e57, e = emu(57, J), emu(115, J)
    v = e["var"]["primary"]
    ab = np.linalg.solve(np.array([[19, NE[19]], [57, NE[57]]], float), [C[J]["E0"], e57["E0"]])
    de = (v["E"] - ab @ [115, NE[115]]) / 115
    rows.append(abs(v["err"]["dm_s"] - curve19(J, de)) / (.06 * e["ref_m_s"]))
cmp("n=115, E0 from a n + b edges fit (mean)", float(np.mean(rows)), R["no_reference_115"]["mean"])
P("     max %.3f" % max(rows))
for key, ratio in (("e0_57_per_bond", NE[57] / NE[19]), ("e0_57_per_site", 57 / 19)):
    a = []
    for J in grid(57):
        e = emu(57, J)
        v = e["var"]["primary"]
        de = (v["E"] - C[J]["E0"] * ratio) / 57
        a.append(abs(v["err"]["dm_s"] - curve19(J, de)) / (.06 * e["ref_m_s"]))
    cmp("n=57, " + key + " (mean)", float(np.mean(a)), R["nulls"][key]["mean"])
    P("     max %.3f" % max(a))

P("")
P("=== log-log slope of the n=19 curves (stored: %s) ===" % {k: round(v, 3) for k, v in R["nulls"]["log_slope"].items()})
for J in sorted(C):
    c = np.array([p for p in C[J]["curve"] if p[0] > 1e-5 and p[1] > 0])
    x, y = np.log(c[:, 0]), np.log(c[:, 1])
    out = []
    for lo, hi, key in ((1e-4, 1e-3, "low"), (1e-2, 1e-1, "high")):
        m_ = (c[:, 0] >= lo) & (c[:, 0] <= hi)
        out.append("%s: %s (%d pts)" % (key, ("%.3f" % np.polyfit(x[m_], y[m_], 1)[0]) if m_.sum() >= 3 else "n/a", int(m_.sum())))
    P("  J=%.1f  %s" % (J, " ; ".join(out)))

P("")
P("=== internal checks on the biased family (n=57): slope of E(Jz) against the label ===")
for n in (57, 115):
    Js = grid(n)
    E, b, b0, e0 = [], [], [], []
    for J in Js:
        e = emu(n, J)
        ref = rj("%s/ref/ref_n%d_J%s.json" % (M, n, J))
        v = e["var"]["primary"]
        E.append(v["E"])
        b.append(sum(v["labels"]["Czz"][:NE[n]]) / 4)
        b0.append(sum(ref["labels"]["Czz"][:NE[n]]) / 4)
        e0.append(ref["E0"])
    J = np.array(Js)
    E, b, b0, e0 = map(np.array, (E, b, b0, e0))
    a = E - J * b
    frac = [(E[i] - (a + x * b).min()) / (E[i] - e0[i]) for i, x in enumerate(Js)]
    slope = np.gradient(E, J)
    ratio = np.abs(slope - b0) / np.abs(b - b0)
    P("  n=%d ratio |slope - truth| / |label - truth| per coupling: %s" % (n, ", ".join("%.1f: %.3f" % (j, r) for j, r in zip(Js, ratio))))
    P("       range for Jz <= 2.5: %.3f-%.3f ; over all couplings: %.3f-%.3f ; hull fraction max %.4f" % (
        ratio[J <= 2.5].min(), ratio[J <= 2.5].max(), ratio.min(), ratio.max(), max(frac)))

P("")
P("=== stored spread numbers ===")
for k in ("ratio_to_curve_min", "ratio_to_curve_max", "spread_pct_low", "spread_pct_high", "ceiling_pct_min", "ceiling_pct_max"):
    P("  %s = %.4f" % (k, R["nulls"][k]))
P("  published comparison:", [(r["n"], r["J"], round(r["over_pct"], 1)) for r in R["published"]["rows"]])
open(os.path.join(HERE, "extras_bias2_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
