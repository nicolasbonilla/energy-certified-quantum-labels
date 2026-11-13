"""Export the arrays that ../fig1_overview.py plots in panels (b) and (c) as .dat files for fig_overview.tex.

How: the plotting functions law() and learner() of fig1_overview.py are run unchanged on matplotlib axes wrapped in a
recorder that logs every plot/scatter/fill_between/axvline call (the arrays exactly as passed to matplotlib). The
recorded arrays are written here; nothing is refitted or recomputed. Afterwards every key value is compared with the
stored JSON, read independently, and the caption's numbers are checked. Results go to export_check.txt.

Run from anywhere with  python -B export_overview.py  (no bytecode). Reads only; writes only into this folder.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.abspath(os.path.join(HERE, ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, FIG)

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402
import fig1_overview as F  # noqa: E402

LOG = []
OUT = []


def say(s=""):
    print(s)
    OUT.append(s)


class Rec:
    """Forward everything to a real Axes; log the data-carrying calls with their arrays."""
    KEEP = ("plot", "scatter", "fill_between", "axvline")

    def __init__(self, ax, tag):
        self._ax, self._tag = ax, tag

    def __getattr__(self, name):
        a = getattr(self._ax, name)
        if name not in self.KEEP:
            return a

        def wrap(*args, **kw):
            LOG.append((self._tag, name, [np.array(x, dtype=float) if not isinstance(x, str) else x for x in args],
                        dict(kw)))
            return a(*args, **kw)
        return wrap


def fmt(v):
    return "nan" if (v is None or (isinstance(v, float) and math.isnan(v))) else repr(float(v))


def write(name, header, rows):
    p = os.path.join(HERE, name)
    with open(p, "w", encoding="ascii", newline="\n") as f:
        f.write(" ".join(header) + "\n")
        for r in rows:
            f.write(" ".join(fmt(v) for v in r) + "\n")
    # round trip: the file holds the recorded floats exactly
    back = [ln.split() for ln in open(p, encoding="ascii").read().splitlines()[1:]]
    for r, b in zip(rows, back):
        for v, s in zip(r, b):
            if s == "nan":
                assert v is None or math.isnan(v)
            else:
                assert float(s) == float(v), (name, v, s)
    say("wrote %-22s %3d rows  (%s)" % (name, len(rows), " ".join(header)))


def close(a, b, tol=0.0):
    return abs(a - b) <= tol


# ------------------------------------------------------------------------------------------------ run the originals
F.rc()
fig = plt.figure()
axb, axc, axw = fig.add_subplot(131), fig.add_subplot(132), fig.add_subplot(133)
F.law(Rec(axb, "b"))
F.learner(Rec(axc, "c"), Rec(axw, "w"))
plt.close(fig)
assert os.path.exists(F.F_LI), "results.json missing: fig1_overview would fall back to the fast layout file"

say("export_overview.py: arrays recorded from fig1_overview.law() and .learner() (%d data calls)" % len(LOG))
say("inputs: %s" % os.path.relpath(C.F_MAP_SUMMARY, C.ROOT))
say("        %s" % os.path.relpath(F.F_HU, C.ROOT))
say("        %s" % os.path.relpath(F.F_LI, C.ROOT))
say("        %s (emu, ref, n = 57)" % os.path.relpath(os.path.dirname(os.path.dirname(F.F_EMU)), C.ROOT))
say()

# ------------------------------------------------------------------------------------------------ panel (b)
CERT, WARM = F.CERT, F.WARM
b = [x for x in LOG if x[0] == "b"]
series = {}          # name -> list of [n, y_marker, y_bar_end]
guides = []
lines = {}
cur = None
for tag, kind, args, kw in b:
    if kind == "scatter":
        x, y = args[0], args[1]
        if kw.get("marker") == "s":
            cur = ("hh_avg" if kw["color"] == CERT else "hh_loc")
            for xx, yy in zip(x, y):
                series.setdefault(cur, []).append([xx, yy, None])
        else:
            assert kw.get("facecolor") == "white"
            cur = ("bm_avg" if kw["edgecolor"] == CERT else "bm_loc")
            series.setdefault(cur, []).append([x[0], y[0], None])
    elif kind == "plot":
        x, y = args[0], args[1]
        if kw.get("ls") == ":":
            guides.append((x, y))
        elif len(x) == 2 and x[0] == x[1]:
            # bar of the current series: from the marker value to the inner-bound value
            row = [r for r in series[cur] if r[0] == x[0] and r[1] == y[0]]
            assert len(row) == 1 and row[0][2] is None, (cur, x, y)
            row[0][2] = y[1]
        else:
            lines["hh_avg" if (kw["color"] == CERT) else ("hh_loc" if "ls" not in kw else "bm_loc")] = (x, y)
assert sorted(series) == ["bm_avg", "bm_loc", "hh_avg", "hh_loc"] and len(guides) == 2

# every connecting line passes through exactly the markers of its series
for k in ("hh_avg", "hh_loc", "bm_loc"):
    x, y = lines[k]
    assert [r[0] for r in series[k]] == list(x) and [r[1] for r in series[k]] == list(y), k

for k in ("hh_avg", "hh_loc", "bm_avg", "bm_loc"):
    write("b_%s.dat" % k, ["n", "de_out", "de_in"], series[k])
# bars as segments separated by nan rows (unbounded coords=jump)
bars = []
for k in ("hh_avg", "hh_loc", "bm_avg", "bm_loc"):
    seg = []
    for n, a, c in series[k]:
        if c is not None:
            seg += [[n, a], [n, c], [float("nan"), float("nan")]]
    write("b_%s_bars.dat" % k, ["n", "de"], seg)
write("b_guide_loc_hh.dat", ["n", "de"], list(zip(*guides[0])))
write("b_guide_loc_bm.dat", ["n", "de"], list(zip(*guides[1])))

# --- independent JSON checks for (b)
S = C.rj(C.F_MAP_SUMMARY)
HU = C.rj(F.F_HU)["rows"]
nchk = 0
for k, lab in (("hh_avg", "Czz_bar"), ("hh_loc", "Z_bulk")):
    for n, a, c in series[k]:
        r = [x for x in S["rows"] if x["n"] == int(n) and abs(x["Jz"] - 4.0) < 1e-12 and x["label"] == lab]
        assert len(r) == 1
        assert a == r[0]["de_star_out"] and c == r[0]["de_star_in"], (k, n)
        nchk += 2
assert [r[0] for r in series["hh_avg"]] == [19, 57, 115]


def hu(L, k, lab, meth):
    r = [x for x in HU if x["L"] == L and x["k"] == k and x["label"] == lab and x["method"] == meth
         and not x.get("alias_of")]
    assert len(r) == 1
    return r[0]


exp_avg = [(20, hu(4, 1, "Cnn", "ED")), (20, hu(4, 2, "Cnn", "ED")), (20, hu(4, 3, "Cnn", "ED")),
           (30, hu(6, 1, "Cnn", "DMRG")), (45, hu(9, 1, "Cnn", "DMRG")), (45, hu(9, 2, "Cnn", "DMRG"))]
exp_loc = [(20, hu(4, 1, "Ccent", "ED")), (30, hu(6, 1, "Cfix", "DMRG")), (45, hu(9, 1, "Cfix", "DMRG"))]
for k, exp in (("bm_avg", exp_avg), ("bm_loc", exp_loc)):
    assert len(series[k]) == len(exp)
    for (n, a, c), (ne, r) in zip(series[k], exp):
        assert n == ne and a == r["tau"]["de_out"], (k, n)
        nchk += 1
        if r["method"] == "DMRG":
            assert c == r["tau"]["de_in"], (k, n)
            nchk += 1
        else:
            assert c is None
z0, b0 = series["hh_loc"][0][1], series["bm_loc"][0][1]
assert list(guides[0][0]) == [19, 140] and close(guides[0][1][0], z0 * 1.35) and close(guides[0][1][1], z0 * 1.35 * 19 / 140)
assert list(guides[1][0]) == [20, 140] and close(guides[1][1][0], b0 / 1.35) and close(guides[1][1][1], b0 / 1.35 * 20 / 140)
say()
say("(b) %d marker/bar values equal summary_map.json (rows n=19,57,115, Jz=4: de_star_out, de_star_in) and "
    "summary_huang.json (tau.de_out, tau.de_in) exactly" % nchk)
say("    guides: 1.35 x and 1/1.35 x the smallest-size local value, slope -1 (styling, as in fig1_overview.py)")
for k in ("hh_avg", "hh_loc", "bm_loc"):
    s = series[k]
    say("    %s: de_out(n_max)/de_out(n_min) = %.3f; n_min/n_max = %.3f"
        % (k, s[-1][1] / s[0][1], s[0][0] / s[-1][0]))

# ------------------------------------------------------------------------------------------------ panel (c)
c = [x for x in LOG if x[0] == "c"]
w = [x for x in LOG if x[0] == "w"]
INK, GREYBAR = F.INK, "#c9ccd0"
bars_c = [x for x in c if x[1] == "plot" and x[3].get("solid_capstyle") == "butt"]
grey = [[a[0][0], a[1][0], a[1][1]] for _, _, a, kw in bars_c if kw["color"] == GREYBAR]
teal = [[a[0][0], a[1][0], a[1][1]] for _, _, a, kw in bars_c if kw["color"] == CERT]
assert len(grey) + len(teal) == len(bars_c)
truth_l = [x for x in c if x[1] == "plot" and len(x[2]) > 2 and x[2][2] == "-"]
truth_m = [x for x in c if x[1] == "plot" and len(x[2]) > 2 and x[2][2] == "o" and x[3].get("color") == INK]
band = [x for x in c if x[1] == "fill_between"]
model = [x for x in c if x[1] == "plot" and len(x[2]) > 2 and x[2][2] == "--"]
lab_tr = [x for x in c if x[1] == "plot" and len(x[2]) > 2 and x[2][2] == "o" and x[3].get("color") == WARM]
lab_od = [x for x in c if x[1] == "plot" and len(x[2]) > 2 and x[2][2] == "o" and x[3].get("mfc") == "white"]
assert len(truth_l) == len(truth_m) == len(band) == len(model) == len(lab_tr) == len(lab_od) == 1
assert len(bars_c) + 6 == len(c), "unrecognised data call in panel (c)"
Jt, mt = truth_l[0][2][0], truth_l[0][2][1]
assert np.array_equal(Jt, truth_m[0][2][0]) and np.array_equal(mt, truth_m[0][2][1])
jj, lo, hi = band[0][2]
jj2, pred = model[0][2][0], model[0][2][1]
assert np.array_equal(jj, jj2)
qs = np.unique(np.round((hi - lo) / 2.0, 15))
assert len(qs) == 1
q = (hi - lo)[0] / 2.0

write("c_truth.dat", ["J", "ms"], list(zip(Jt, mt)))
write("c_labels_train.dat", ["J", "ms"], list(zip(lab_tr[0][2][0], lab_tr[0][2][1])))
write("c_labels_test.dat", ["J", "ms"], list(zip(lab_od[0][2][0], lab_od[0][2][1])))
write("c_model.dat", ["J", "lo", "pred", "hi"], list(zip(jj, lo, pred, hi)))
seg = []
for J, a, bb in grey:
    seg += [[J, a], [J, bb], [float("nan"), float("nan")]]
write("c_bars_grey.dat", ["J", "ms"], seg)
seg = []
for J, a, bb in teal:
    seg += [[J, a], [J, bb], [float("nan"), float("nan")]]
write("c_bars_teal.dat", ["J", "ms"], seg)
write("c_bars_table.dat", ["J", "lo", "hi", "certified"], [[J, a, bb, 0] for J, a, bb in grey] +
      [[J, a, bb, 1] for J, a, bb in teal])

# side panel: coverage rows (connector line, open = new emulated labels, filled = truth), and the reference line
cov = []
conn = [x for x in w if x[1] == "plot"]
sc = [x for x in w if x[1] == "scatter"]
vl = [x for x in w if x[1] == "axvline"]
for p in conn:
    y = p[2][1][0]
    t, e = p[2][0]
    so = [s for s in sc if s[3].get("facecolor") == "white" and s[2][1][0] == y and s[2][0][0] == e]
    sf = [s for s in sc if s[3].get("facecolor") is None and s[2][1][0] == y and s[2][0][0] == t]
    assert len(so) == 1 and len(sf) == 1
    cov.append([y, t, e])
assert len(cov) == 2 and len(vl) == 1
cov.sort(key=lambda r: -r[0])          # training range first
write("c_coverage.dat", ["row", "cov_truth", "cov_new"], cov)
seg = []
for y, t, e in cov:
    seg += [[t, y], [e, y], [float("nan"), float("nan")]]
write("c_coverage_seg.dat", ["cov", "row"], seg)
ref_level = float(vl[0][2][0])

# --- independent JSON checks for (c)
LI = C.rj(F.F_LI)
L = LI["sizes"]["57"]
M = L["models"]["poly3_invJ"]
rowsJ = {}
for part in ("indist_emulated", "ood_emulated"):
    for r in M[part]["rows"]:
        rowsJ[round(r["Jz"], 1)] = r
say()
assert list(Jt) == L["couplings"] and len(Jt) == 14
d_truth = max(abs(m - rowsJ[round(J, 1)]["m_s_truth"]) for J, m in zip(Jt, mt))
d_lab = max(abs(m - rowsJ[round(J, 1)]["m_s_emu"]) for J, m in zip(*lab_tr[0][2][:2]))
d_lab = max(d_lab, max(abs(m - rowsJ[round(J, 1)]["m_s_emu"]) for J, m in zip(*lab_od[0][2][:2])))
assert d_truth < 1e-12 and d_lab < 1e-12
assert list(lab_tr[0][2][0]) == L["train"] and list(lab_od[0][2][0]) == L["ood"]
say("(c) truth (14 couplings) equals results.json rows m_s_truth: max |diff| = %.1e" % d_truth)
say("    emulated labels (10 training + 4 test) equal rows m_s_emu: max |diff| = %.1e" % d_lab)
qood = [r["qM"] for r in M["ood_emulated"]["rows"]]
assert len(set(qood)) == 1 and q == qood[0] or close(q, qood[0], 1e-15)
say("    band half-width q = %.6g = ood_emulated rows[*].qM (all four equal) = device_illustration qM %.6g"
    % (q, L["device_illustration"]["1.2"]["qM"]))
# drawn model at the test couplings against the stored predictions of the model trained on the whole training range
d_pred = max(abs(np.interp(J, jj, pred) - rowsJ[J]["m_s_pred"]) for J in L["ood"])
say("    drawn model (200-point grid, linear interpolation) vs stored ood m_s_pred: max |diff| = %.1e" % d_pred)
assert d_pred < 5e-4
# bars against the map windows, read directly
SM = {(r["n"], round(r["Jz"], 1), r["label"]): r for r in S["rows"]}
cert = L["certification"]
nb = 0
for J, a, bb in grey + teal:
    r = SM[(57, round(J, 1), "m_s")]
    e = cert["%.1f" % J]["eps_emu"]
    st = sorted((r[k]["eps"], r[k]) for k in ("at_lo", "at_dig", "at_up"))
    if cert["%.1f" % J]["m_s"]["certified"]:
        exp = next(d for (ee, d) in st if ee >= e)["outer"]
        assert [a, bb] == exp and bb - a <= r["tau"], J
    else:
        inner = [d for (ee, d) in st if ee <= e][-1]["inner"]
        lab = rowsJ[round(J, 1)]["m_s_emu"]
        assert close(a, min(inner[0], lab), 1e-12) and close(bb, max(inner[1], lab), 1e-12), J
        assert bb - a > r["tau"], J
    nb += 1
Jbars = sorted(round(x[0], 1) for x in grey + teal)
missing = [J for J in L["couplings"] if round(J, 1) not in Jbars]
assert missing == [2.2, 3.5] and all(not cert["%.1f" % J]["m_s"]["row"] for J in missing)
assert [round(x[0], 1) for x in teal] == [4.0, 5.0, 6.0]
say("    %d window bars equal the map rows (grey: inner bound at the last eps <= the label's eps, widened to the "
    "label; teal: outer at the first eps >= it)" % nb)
say("    grey widths / tau: %s  (all > 1: wider than tau, label dropped)"
    % ", ".join("%.1f:%.2f" % (J, (bb - a) / SM[(57, round(J, 1), "m_s")]["tau"]) for J, a, bb in grey))
say("    teal widths / tau: %s  (all <= 1: certified, kept)"
    % ", ".join("%.1f:%.3f" % (J, (bb - a) / SM[(57, round(J, 1), "m_s")]["tau"]) for J, a, bb in teal))
say("    no bar at Jz = %s: the map has no m_s row there (certification[J].m_s.row = false)" % missing)
lo_vis = min(a for _, a, _ in grey)
say("    lowest grey-bar end %.4f (drawn axis in fig1_overview.py starts at 0.38: bars at the test couplings are clipped)"
    % lo_vis)

# coverage values
for (y, t, e), part in zip(cov, ("indist_emulated", "ood_emulated")):
    s = M[part]["summary"]
    assert t == s["covZ_truth"] and e == s["covZ_emu"]
    say("    coverage %-16s truth %.4f, new labels %.4f  (= summary covZ_truth, covZ_emu)" % (part, t, e))

# caption numbers
alpha = LI["alpha"]
lev = [M["ood_emulated"]["levelZ"], M["ood_emulated"]["levelM"]] + \
      [r["levelZ"] for r in M["indist_emulated"]["rows"]] + [r["levelM"] for r in M["indist_emulated"]["rows"]]
assert close(alpha, 0.1, 1e-15) and all(close(v, 1 - alpha, 1e-12) for v in lev) and close(ref_level, 1 - alpha, 1e-12)
wM = M["indist_emulated"]["summary"]["widthM_tau_median"]
wZi = M["indist_emulated"]["summary"]["widthZ_tau_median"]
wZo = M["ood_emulated"]["summary"]["widthZ_tau_median"]
assert "%.3f" % wM == "0.093" and "%.3f" % wZi == "0.092" and "%.3f" % wZo == "0.117"
assert "%.2f" % wZi == "0.09" and "%.2f" % wZo == "0.12" and "%.1f" % wM == "0.1"
taus = {J: SM[(57, J, "m_s")]["tau"] for J in (1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0)}
rel = [2 * q / t for t in taus.values()]
assert 0.05 < min(rel) and max(rel) < 0.2
say()
say("caption checks (main.tex Fig. 1):")
say("  standard 90%% interval: alpha = %g, levels %s, reference line at %g" % (alpha, sorted(set(lev)), ref_level))
say("  m_s interval median width (training range) widthM_tau_median = %.4f -> '0.093', 'about 0.1 tau'" % wM)
say("  per-site Z median width, training range widthZ_tau_median = %.4f -> 0.092 (printed 0.09 tau)" % wZi)
say("  per-site Z median width, test range     widthZ_tau_median = %.4f -> 0.117 (printed 0.12 tau)" % wZo)
say("  drawn band 2q / tau(Jz) over the couplings with a map row: %.3f .. %.3f (about 0.1 tau, too narrow to see)"
    % (min(rel), max(rel)))
say("  n = 57 qubits: results.json sizes['57']; tau_rel = %g" % LI["tau_rel"])
say()
say("ALL ASSERTIONS PASSED")
with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(OUT) + "\n")
