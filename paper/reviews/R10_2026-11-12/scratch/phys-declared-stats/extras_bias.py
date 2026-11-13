"""R10 reviewer phys-declared-stats: spreads behind the means quoted in the exploratory part of Sec. V (main.tex 650-705),
recomputed from the stored outputs with the formulas of bias_law.py, plus two checks the paper does not make:
the fourth device label (Jz = 6.0, job of 2026-11-10) against the n = 19 curve, and the monotonicity of the n = 19
truth in the certified range.  Reads only."""
import glob
import json
import os
import re

import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
FT = ROOT + "/phase3/full_runs/final_tests"
M = ROOT + "/phase3/full_runs/method/out_20261030T003230Z/out"
BL = ROOT + "/phase3/full_runs/bias_law"
QPU = ROOT + "/phase3/full_runs/qpu/analysis/analysis.json"
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


def family(n, J):
    e = emu(n, J)
    Pp = [("pipe_" + k, v["dE_site"], v["err"]["dm_s"]) for k, v in e["var"].items() if not v.get("alias_of")]
    Pp += [("kscan", (s["E"] - e["E0"]) / n, s["err"]["dm_s"]) for s in e.get("kscan", [])]
    f = "%s/gsscan/gsscan_n%d_J%s.json" % (M, n, J)
    if os.path.exists(f):
        g = rj(f)
        Pp += [("gs_random", s["dE_site"], s["err"]["dm_s"]) for s in g["nested"]]
        Pp += [("gs_top", s["dE_site"], s["err"]["dm_s"]) for s in g["topD"]]
    return e, Pp


def curve19(J, de):
    c = np.array(C[J]["curve"])
    return float(np.interp(np.sqrt(max(de, 0.0)), np.sqrt(np.maximum(c[:, 0], 0.0)), c[:, 1]))


def chord(J, de):
    dn = (-NE[19] * J / 4 - C[J]["E0"]) / 19
    return (1 - C[J]["ms0"]) * np.sqrt(max(de, 0.0) / dn)


def fit(Pp):
    s = np.sqrt([p[1] for p in Pp])
    y = np.array([p[2] for p in Pp])
    A = np.c_[s, s ** 2, s ** 3]
    c = np.linalg.lstsq(A, y, rcond=None)[0]
    return lambda de: float(np.array([de ** .5, de, de ** 1.5]) @ c)


def desc(a):
    a = np.asarray(a, float)
    return "mean %.3f, median %.3f, min %.3f, max %.3f, n %d" % (a.mean(), np.median(a), a.min(), a.max(), a.size)


P("=== spreads behind the exploratory means of Sec. V (units of tau = 0.06 m_s(GS) at the target) ===")
# families 57 -> 115
A = []
names = set()
for J in (1.2, 1.6, 2.5):
    e57, P57 = family(57, J)
    f = fit(P57)
    e, Pp = family(115, J)
    t = .06 * e["ref_m_s"]
    for name, de, dm in Pp:
        A.append((abs(dm) / t, abs(dm - f(de)) / t, J, name))
        names.add(name)
P("52 states of 7 families at n=115 with the n=57 cubic: raw %s" % desc([a[0] for a in A]))
P("                                                  corrected %s ; families %d ; worst %s" % (
    desc([a[1] for a in A]), len(names), max(A, key=lambda a: a[1])[1:]))
for J in (1.2, 1.6, 2.5):
    P("   J=%.1f corrected %s" % (J, desc([a[1] for a in A if a[2] == J])))
# device with the emu57 cubic and with the n19 curve
Q = rj(QPU)
d19, d57, dch, draw = [], [], [], []
for J in ("1.2", "1.6", "4.0"):
    e, Pp = family(57, float(J))
    f = fit(Pp)
    t = .06 * e["ref_m_s"]
    for m in ("rec", "ps"):
        v = Q["points"][J]["device"][m]
        de = v["eps"] / 57
        d = v["dm_s"]
        draw.append(abs(d) / t)
        d19.append(abs(d - curve19(float(J), de)) / t)
        d57.append(abs(d - f(de)) / t)
        dch.append(abs(d - chord(float(J), de)) / t)
P("device, six readings (3 couplings x with/without recovery): raw %s" % desc(draw))
P("   n=19 curve %s" % desc(d19))
P("   n=57 cubic %s" % desc(d57))
P("   chord      %s" % desc(dch))
P("   per coupling (rec): n=19 curve %s" % [round(x, 3) for x in d19[0::2]])
# chord and classical forms per coupling
for n in (57, 115):
    a = []
    for J in grid(n):
        e = emu(n, J)
        v = e["var"]["primary"]
        a.append(abs(v["err"]["dm_s"] - chord(J, v["dE_site"])) / (.06 * e["ref_m_s"]))
    P("chord, primary labels n=%d: %s" % (n, desc(a)))
forms = {"a+b/n": lambda n: 1 / n, "a+b*Ne/n": lambda n: NE[n] / n, "a+b/sqrt(n)": lambda n: n ** -.5}
for name, g in forms.items():
    a = []
    for J in grid(115):
        m19, m57, m115 = C[J]["ms0"], emu(57, J)["ref_m_s"], emu(115, J)["ref_m_s"]
        b = (m19 - m57) / (g(19) - g(57))
        a.append(abs(m57 + b * (g(115) - g(57)) - m115) / (.06 * m115))
    P("classical two-point form %-12s at n=115 (11 couplings): %s" % (name, desc(a)))
a = [r["corr57"] for r in R["classical_tie_115"]["rows"]]
P("label corrected with the n=57 curve at n=115 (stored rows): %s" % desc(a))
a = [abs(emu(57, J)["ref_m_s"] - emu(115, J)["ref_m_s"]) / (.06 * emu(115, J)["ref_m_s"]) for J in grid(115)]
P("truth at n=57 used as the answer at n=115: %s" % desc(a))

P("")
P("=== truth at n = 19 against the truth at n = 57 (abstract: 'within a fifth of the tolerance' from Jz = 3.2 up) ===")
rows = []
for J in grid(57):
    e = emu(57, J)
    rows.append((J, abs(C[J]["ms0"] - e["ref_m_s"]) / (.06 * e["ref_m_s"])))
ta = rj(FT + "/analysis/test_a.json")
for r in ta["rows"]:
    if r["n"] == 57:
        rows.append((r["J"], r["small_truth"]))
rows.sort()
P("  J: miss of the n=19 truth (tau):", ", ".join("%.1f: %.3f" % x for x in rows))
v = [x[1] for x in rows]
P("  monotonically decreasing in Jz over the %d stored couplings: %s ; couplings with Jz >= 3.2: %s ; largest there %.4f" % (
    len(rows), all(v[i] > v[i + 1] for i in range(len(v) - 1)), [x[0] for x in rows if x[0] >= 3.2], max(x[1] for x in rows if x[0] >= 3.2)))

P("")
P("=== a check the paper does not make: the device label of the declared job at Jz = 6.0 against the n = 19 curve ===")
e = emu(57, 6.0)
m0 = e["ref_m_s"]
t = .06 * m0
for var in ("rec", "ps"):
    r = rj(FT + "/out_c3b_20261110T164846Z/out/c/rq_C_J6.0_%s.json" % var)
    de = (r["E_float"] - e["E0"]) / 57
    dm = r["m_s_label"] - m0
    c = curve19(6.0, de)
    ch = chord(6.0, de)
    P("  %s: E-E0 = %.4f J (de %.5f), dm_s = %+.5f (raw miss %.3f tau); n=19 curve %.5f -> ratio %.3f, corrected miss %.3f tau; chord %.5f -> miss %.3f tau" % (
        var, r["E_float"] - e["E0"], de, dm, abs(dm) / t, c, dm / c, abs(dm - c) / t, ch, abs(dm - ch) / t))
ctl = rj(FT + "/out_20261106T120830Z/out/c/control_J6.0.json")
P("  noiseless control keys:", list(ctl.keys())[:15])
open(os.path.join(HERE, "extras_bias_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
