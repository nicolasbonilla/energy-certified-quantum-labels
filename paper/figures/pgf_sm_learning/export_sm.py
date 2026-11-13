"""Export the arrays that ../figS_learning.py and ../figS_huang.py plot, as .dat files for the PGFPlots versions.

How: the main() of each script is run UNCHANGED, with matplotlib's plt.subplots patched to return axes wrapped in a
recorder and a figure whose savefig does nothing (so nothing is written outside this folder). Every array passed to
plot / scatter / hist / annotate / axhline / axvline / axhspan / axvspan is logged exactly as passed (hist also logs
its returned counts and bin edges) and written here. Nothing is refitted or recomputed. Afterwards the plotted values
are compared with the stored JSON, read independently, and the caption numbers are checked -> export_check.txt.

  python -B export_sm.py        (reads only; writes only into this folder)
"""
import inspect
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

OUT = []


def say(s=""):
    print(s)
    OUT.append(s)


def snapshot(d):
    if not os.path.isdir(d):
        return {}
    return {f: os.path.getmtime(os.path.join(d, f)) for f in os.listdir(d)}


LRN = os.path.join(C.ROOT, "phase3", "full_runs", "learning")
WATCH_DIRS = [os.path.join(FIG, "__pycache__"), os.path.join(LRN, "code", "__pycache__"), os.path.join(LRN, "analysis"),
              os.path.join(LRN, "code")]
WATCH_FILES = [os.path.join(FIG, n) for n in ("figS_learning.pdf", "figS_learning.png", "figS_huang.pdf",
                                               "figS_huang.png")]
before = {d: snapshot(d) for d in WATCH_DIRS}
before_f = {f: os.path.getmtime(f) for f in WATCH_FILES}

LOG = []
SAVED = []


class Rec:
    KEEP = ("plot", "scatter", "hist", "annotate", "axhline", "axvline", "axhspan", "axvspan")

    def __init__(self, ax, tag):
        self._ax, self._tag = ax, tag

    def __getattr__(self, name):
        a = getattr(self._ax, name)
        if name not in self.KEEP:
            return a

        def wrap(*args, **kw):
            res = a(*args, **kw)
            entry = {"tag": self._tag, "kind": name, "kw": dict(kw),
                     "args": [x if isinstance(x, str) else np.array(x, dtype=float) for x in args]}
            if name == "hist":
                entry["counts"], entry["edges"] = np.array(res[0], dtype=float), np.array(res[1], dtype=float)
            LOG.append(entry)
            return res
        return wrap


class FigP:
    def __init__(self, fig):
        self._fig = fig

    def savefig(self, path, *a, **k):     # never write the original outputs
        SAVED.append(path)

    def __getattr__(self, name):
        return getattr(self._fig, name)


REAL_SUBPLOTS = plt.subplots


def fake_subplots(*a, **k):
    fig, axs = REAL_SUBPLOTS(*a, **k)
    arr = np.empty(axs.shape, dtype=object)
    for idx in np.ndindex(axs.shape):
        arr[idx] = Rec(axs[idx], idx)
    return FigP(fig), arr


def fmt(v):
    return "nan" if (v is None or (isinstance(v, float) and math.isnan(v))) else repr(float(v))


def write(name, header, rows):
    p = os.path.join(HERE, name)
    with open(p, "w", encoding="ascii", newline="\n") as f:
        f.write(" ".join(header) + "\n")
        for r in rows:
            f.write(" ".join(fmt(v) for v in r) + "\n")
    back = [ln.split() for ln in open(p, encoding="ascii").read().splitlines()[1:]]
    assert len(back) == len(rows)
    for r, b in zip(rows, back):
        for v, s in zip(r, b):
            assert (s == "nan" and (v is None or math.isnan(v))) or float(s) == float(v), (name, v, s)
    return name


def run(module_name):
    del LOG[:]
    plt.subplots = fake_subplots
    try:
        mod = __import__(module_name)
        mod.main()
    finally:
        plt.subplots = REAL_SUBPLOTS
        plt.close("all")
    return mod, list(LOG)


def nan_seg(pairs):
    seg = []
    for x, a, b in pairs:
        seg += [[x, a], [x, b], [float("nan"), float("nan")]]
    return seg


# ================================================================================================ figS_learning
FL, LOGL = run("figS_learning")
PL = FL.PL
src = inspect.getsource(FL.main)
for s in ('R["M1"], "(a)', 'R["M2"], "(b)', '"gen5|all|id|0.08"', '"advL5|all|id|0.08"'):
    assert s in src, s
say("== figS_learning: figS_learning.main() run unchanged (savefig neutralised: %d calls caught); %d data calls"
    % (len(SAVED), len(LOGL)))
SET_OF = {PL.BLUE: "gen5", PL.ORANGE: "advL5"}
RJ = {M: C.rj(os.path.join(LRN, "analysis", "learn_%s_D_O.json" % M)) for M in ("M1", "M2")}
written = []
pts = {}
nchk = 0
for tag, M in (((0, 0), "M1"), ((0, 1), "M2")):
    L = [e for e in LOGL if e["tag"] == tag]
    cl_order = iter(("avg", "nn"))
    cl = None
    for e in L:
        if e["kind"] == "plot" and e["kw"].get("marker") == "x":
            cl = next(cl_order)
            pts[(M, cl, "exact")] = (float(e["args"][0]), float(e["args"][1]))
        elif e["kind"] == "plot" and e["kw"].get("mfc") == PL.SURF:
            pts[(M, cl, SET_OF[e["kw"]["mec"]], "SC")] = (float(e["args"][0]), float(e["args"][1]))
        elif e["kind"] == "plot":
            pts[(M, cl, SET_OF[e["kw"]["mfc"]], "CSC")] = (float(e["args"][0]), float(e["args"][1]))
        elif e["kind"] == "annotate" and e["args"][0] == "":
            st = SET_OF[e["kw"]["arrowprops"]["color"]]
            # arrow from the standard (SC) point to the energy-calibrated (CSC) point
            pts[(M, cl, st, "arrow")] = (tuple(e["kw"]["xytext"]), tuple(e["kw"]["xy"]))
        elif e["kind"] == "axhline":
            assert float(e["args"][0]) == 0.9
        elif e["kind"] == "axvline":
            assert float(e["args"][0]) == PL.TAU
    c = RJ[M]["coverage"]
    for cl in ("avg", "nn"):
        assert pts[(M, cl, "exact")] == (c["exact"]["SC"][cl]["wid_id"], c["exact"]["SC"][cl]["covT_id"])
        nchk += 2
        written.append(write("lr_%s_exact_%s.dat" % (M, cl), ["wid", "cov"], [pts[(M, cl, "exact")]]))
        for st in ("gen5", "advL5"):
            a, b = pts[(M, cl, st, "SC")], pts[(M, cl, st, "CSC")]
            assert a == (c[st]["SC"][cl]["wid_id"], c[st]["SC"][cl]["covT_id"])
            assert b == (c[st]["CSC"][cl]["wid_id"], c[st]["CSC"][cl]["covT_id"])
            assert pts[(M, cl, st, "arrow")] == (a, b)
            nchk += 4
            written.append(write("lr_%s_%s_%s.dat" % (M, cl, st), ["wid", "cov"], [a, b]))
say("(a, b) %d plotted coverage/width values equal learn_M{1,2}_D_O.json coverage[set][SC|CSC][avg|nn]"
    ".{wid_id, covT_id} exactly; arrows run SC -> CSC; reference lines at 0.9 and tau = %g" % (nchk, PL.TAU))
risk = {}
NAME = {"oracle": "oracle", "certified width (CB)": "CB", "label band W(x)": "BAND", "conformal width (NC)": "NC",
        "random": "random"}
for tag, key in (((1, 0), "gen5|all|id|0.08"), ((1, 1), "advL5|all|id|0.08")):
    L = [e for e in LOGL if e["tag"] == tag and e["kind"] == "plot"]
    assert len(L) == 5
    cg = L[0]["args"][0]
    cols = {NAME[e["kw"]["label"]]: e["args"][1] for e in L}
    assert all(np.array_equal(e["args"][0], cg) for e in L)
    st = key.split("|")[0]
    a = RJ["M1"]["abstention"][key]
    assert list(cg) == RJ["M1"]["cgrid"]
    for rk, v in cols.items():
        assert list(v) == a["ex"][rk], (key, rk)
    risk[st] = (cg, cols)
    rows = [[cg[i]] + [cols[k][i] for k in ("oracle", "CB", "BAND", "NC", "random")] for i in range(len(cg))]
    written.append(write("lr_risk_%s.dat" % st, ["c", "oracle", "CB", "BAND", "NC", "random"], rows))
    dmax = max(np.max(np.abs(cols[x] - cols[y])) for x, y in (("CB", "BAND"), ("CB", "NC"), ("BAND", "NC")))
    say("(c, d) %s: 5 risk-coverage curves (20 points each) equal abstention['%s'].ex exactly; max spread among "
        "CB, BAND, NC = %.3f (fraction of answers); at full coverage %.3f" % (st, key, dmax, cols["CB"][-1]))
say("wrote %d files: %s" % (len(written), " ".join(written)))

meta = RJ["M1"]["meta"]
assert RJ["M2"]["meta"]["R"] == meta["R"] == 200 and meta["n_id"] == 100 and meta["alpha"] == 0.1
assert meta["taus"][0] == PL.TAU == 0.08
assert meta["classes"].count("avg") == 3 and meta["classes"].count("nn") == 31 and meta["classes"].count("diag") == 24
lab_stats = C.rj(os.path.join(LRN, "analysis", "label_stats.json"))
assert any(k.endswith("|0.005") for k in lab_stats["D"])
res_md = open(os.path.join(LRN, "RESULTS.md"), encoding="utf-8").read()
assert "δe = 5e-3" in res_md and "gen5" in res_md and "advL5" in res_md
say("caption checks (supplement.tex Fig. S learnS):")
say("  delta e = 5e-3: label sets gen5/advL5 (RESULTS.md: 'delta e = 5e-3', label_stats keys '|0.005')")
say("  100 instances at n = 20 (meta.n_id = %d), 200 splits (meta.R = %d, both learners), tau = %g (meta.taus[0]),"
    " nominal level 1 - alpha = %.2f" % (meta["n_id"], meta["R"], meta["taus"][0], 1 - meta["alpha"]))
c1, c2 = RJ["M1"]["coverage"], RJ["M2"]["coverage"]
chk = [("D1 M1 SC nn gen5 0.920", c1["gen5"]["SC"]["nn"]["covT_id"], "%.3f", "0.920"),
       ("D2 M1 SC avg gen5 0.909", c1["gen5"]["SC"]["avg"]["covT_id"], "%.3f", "0.909"),
       ("D3 M1 SC nn advL5 0.821", c1["advL5"]["SC"]["nn"]["covT_id"], "%.3f", "0.821"),
       ("D3' M2 SC nn advL5 0.599", c2["advL5"]["SC"]["nn"]["covT_id"], "%.3f", "0.599"),
       ("D5 avg CSC/SC width 1.60", c1["gen5"]["CSC"]["avg"]["wid_id"] / c1["gen5"]["SC"]["avg"]["wid_id"], "%.2f", "1.60"),
       ("D5 nn CSC/SC width 1.30", c1["gen5"]["CSC"]["nn"]["wid_id"] / c1["gen5"]["SC"]["nn"]["wid_id"], "%.2f", "1.30")]
for nm, v, f, exp in chk:
    assert f % v == exp, (nm, v)
    say("  body text read off the figure: %-28s = %.4f -> %s" % (nm, v, exp))
au = RJ["M1"]["abstention"]["gen5|all|id|0.08"]["aurc"]
say("  note: body-text AUCs 0.0827/0.0817/0.0817/0.0815, random 0.139, oracle 0.049 are aurc[CB, BAND, NC, ENS, "
    "random, oracle] = %.4f/%.4f/%.4f/%.4f, %.4f, %.4f (areas of the 'rm' risk, not of the plotted 'ex' curves)"
    % (au["CB"], au["BAND"], au["NC"], au["ENS"], au["random"], au["oracle"]))
assert ["%.4f" % au[k] for k in ("CB", "BAND", "NC", "ENS")] == ["0.0827", "0.0817", "0.0817", "0.0815"]
assert "%.3f" % au["random"] == "0.139" and "%.3f" % au["oracle"] == "0.049"
say()

# ================================================================================================ figS_huang
SAVED_L = len(SAVED)
FH, LOGH = run("figS_huang")
say("== figS_huang: figS_huang.main() run unchanged (savefig neutralised: %d calls caught); %d data calls"
    % (len(SAVED) - SAVED_L, len(LOGH)))
LAB_OF = {v: k for k, v in FH.COL.items()}
S = C.rj(FH.F_HU)
rows = S["rows"]
TAU = FH.TAU


def hrow(L, k, lab, meth):
    r = [x for x in rows if x["L"] == L and x["k"] == k and x["label"] == lab and x["method"] == meth
         and not x.get("alias_of")]
    assert len(r) == 1
    return r[0]


GRID = [0.001, 0.0015, 0.002, 0.003, 0.005, 0.007, 0.01]
nchk = 0
for tag, (L, k, meth, nm) in (((0, 0), (4, 1, "ED", "a")), ((0, 1), (9, 1, "DMRG", "b"))):
    E = [e for e in LOGH if e["tag"] == tag]
    outs = [e for e in E if e["kind"] == "plot" and "label" in e["kw"]]
    ins = [e for e in E if e["kind"] == "plot" and "label" not in e["kw"]]
    span = [e for e in E if e["kind"] == "axvspan"]
    assert len(span) == 1 and [float(x) for x in span[0]["args"]] == [1e-3, 1e-2]
    assert [float(e["args"][0]) for e in E if e["kind"] == "axhline"] == [1.0]
    for e in outs:
        lab = LAB_OF[e["kw"]["color"]]
        r = hrow(L, k, lab, meth)
        assert r["taus"]["tau"] == TAU == 0.08 if "taus" in r else TAU == 0.08
        w = r["tau"]["widths"]
        assert list(e["args"][0]) == [x["de"] for x in w] == GRID
        assert list(e["args"][1]) == [x["w_out"] / TAU for x in w]
        nchk += 2 * len(w)
        data = [[d, o] for d, o in zip(e["args"][0], e["args"][1])]
        hdr = ["de", "w_out"]
        if meth == "DMRG":
            ii = [x for x in ins if LAB_OF[x["kw"]["color"]] == lab]
            assert len(ii) == 1 and list(ii[0]["args"][1]) == [x["w_in"] / TAU for x in w]
            nchk += len(w)
            data = [[d, o, i] for (d, o), i in zip(data, ii[0]["args"][1])]
            hdr.append("w_in")
        written.append(write("hu_%s_%s.dat" % (nm, lab), hdr, data))
    labs = [LAB_OF[e["kw"]["color"]] for e in outs]
    say("(%s) n = %d instance (%d,%d) %s: labels %s; width/tau on the grid %s equals summary_huang.json "
        "tau.widths exactly" % (nm, 5 * L, L, k, meth, labs, GRID))
    if nm == "a":
        assert labs == ["Cnn", "Cd2", "Ccent", "Cfar"]
    else:
        assert labs == ["Cnn", "Cd2", "Ccent", "Cfar", "Cfix"]
# (c)
E = [e for e in LOGH if e["tag"] == (1, 0)]
span = [e for e in E if e["kind"] == "axhspan"]
assert len(span) == 1 and [float(x) for x in span[0]["args"]] == [1e-3, 1e-2]
filled = [e for e in E if e["kind"] == "scatter" and "label" in e["kw"]]
opened = [e for e in E if e["kind"] == "scatter" and e["kw"].get("facecolor") == "none"]
bars = [e for e in E if e["kind"] == "plot"]
fall = {}
NBARS = 0
for f, o in zip(filled, opened):
    lab = LAB_OF[f["kw"]["color"]]
    assert LAB_OF[o["kw"]["edgecolor"]] == lab and np.array_equal(f["args"][0], o["args"][0])
    xs, yo, yl = f["args"][0], f["args"][1], o["args"][1]
    exp = [r for r in rows if r["label"] == lab and not (r["method"] == "DMRG" and r["n"] == 20)
           and not (lab == "Cfix" and r["n"] == 20) and r["tau"]["de_out"]]
    assert len(exp) == len(xs)
    data = []
    for x, a, l_, r in zip(xs, yo, yl, exp):
        assert x == r["n"] + {"Cnn": -1.6, "Cd2": -0.8, "Ccent": 0.0, "Cfar": 0.8, "Cfix": 1.6}[lab]
        assert a == r["tau"]["de_out"] and l_ == r["tau"]["de_law"]
        bi = None
        if r["method"] == "DMRG" and r["tau"]["de_in"]:
            bb = [b for b in bars if LAB_OF[b["kw"]["color"]] == lab and b["args"][0][0] == x and b["args"][1][0] == a]
            assert len(bb) == 1
            bi = float(bb[0]["args"][1][1])
            assert bi == r["tau"]["de_in"]
            nchk += 1
            NBARS += 1
        nchk += 2
        data.append([x, r["n"], a, l_, bi])
    written.append(write("hu_c_%s.dat" % lab, ["x", "n", "de_out", "de_law", "de_in"], data))
    written.append(write("hu_c_%s_bars.dat" % lab, ["x", "de"], nan_seg([(d[0], d[2], d[4]) for d in data if d[4]])))
    by_n = {}
    for d in data:
        by_n.setdefault(int(d[1]), []).append(d[2])
    fall[lab] = (np.median(by_n[45]) / np.median(by_n[20 if 20 in by_n else 30]), sorted(by_n))
assert len(bars) == NBARS, (len(bars), NBARS)   # every bar drawn belongs to a selected DMRG row
say("(c) markers (x = n + offset), rule values and bars equal tau.{de_out, de_law, de_in} of every selected row")
for lab, (ratio, ns) in fall.items():
    say("    %-6s n = %s: median de_out(n=45) / median de_out(smallest n) = %.2f" % (lab, ns, ratio))
assert all(fall[l][0] < 0.7 for l in ("Ccent", "Cfar", "Cfix")) and all(fall[l][0] > 0.7 for l in ("Cnn", "Cd2"))
say("    -> caption 'the single pairs fall with n; the averages do not' holds (single pairs < 0.7, averages > 0.7)")
# (d)
E = [e for e in LOGH if e["tag"] == (1, 1)]
span = [e for e in E if e["kind"] == "axvspan"]
assert len(span) == 1 and [float(x) for x in span[0]["args"]] == [1e-3, 1e-2]
hists = [e for e in E if e["kind"] == "hist"]
assert len(hists) == 4
edges = hists[0]["edges"]
counts_tab = []
total = 0
SAFE = {"nn": "nn", "diag": "diag", "r<=3": "rle3", "r>3": "rgt3"}
for (cls, name, col), h in zip(FH.CLS, hists):
    assert np.array_equal(h["edges"], edges) and h["kw"]["color"] == col
    v = [r["tau"]["de_out"] for rs in S["pairs"].values() for r in rs if r["cls"] == cls and r["tau"]["de_out"]]
    assert list(h["args"][0]) == v
    cnt = np.histogram(v, bins=edges)[0]
    assert np.array_equal(cnt, h["counts"]) and int(cnt.sum()) == len(v)
    assert h["kw"]["label"] == "%s (%d)" % (name, len(v))
    total += len(v)
    nz = np.nonzero(cnt)[0]
    i0, i1 = nz[0], nz[-1]
    # step outline exactly as histtype='step' draws it, without the empty bins before the first and after the last
    # non-empty bin (they lie on the baseline)
    out = [[edges[i0], 0.0]]
    for i in range(i0, i1 + 1):
        out += [[edges[i], cnt[i]], [edges[i + 1], cnt[i]]]
    out.append([edges[i1 + 1], 0.0])
    written.append(write("hu_d_%s.dat" % SAFE[cls], ["x", "count"], out))
    counts_tab.append((cls, len(v)))
write("hu_d_bins.dat", ["left", "right"] + [SAFE[c] for c, _, _ in FH.CLS],
      [[edges[i], edges[i + 1]] + [float(h["counts"][i]) for h in hists] for i in range(len(edges) - 1)])
assert total == 570 and dict(counts_tab) == {"nn": 93, "diag": 72, "r<=3": 243, "r>3": 162}
assert all(len(v) == 190 for v in S["pairs"].values()) and sorted(S["pairs"]) == ["4_1", "4_2", "4_3"]
say("(d) histogram: %d bins (edges as plotted), counts equal np.histogram of pairs[*].tau.de_out by class: %s; "
    "total %d = 3 instances x 190 pairs" % (len(edges) - 1, counts_tab, total))
say("caption checks (supplement.tex Fig. S huang): n = 20 instance (4,1) exact (ED); n = 45 instance (9,1) (DMRG); "
    "570 pair correlators at n = 20; shaded delta e in [1e-3, 1e-2] (all four spans); tau = 0.08")
say()
assert len(SAVED) == 4, SAVED
after = {d: snapshot(d) for d in WATCH_DIRS}
assert after == before, "a watched folder changed"
assert {f: os.path.getmtime(f) for f in WATCH_FILES} == before_f
say("nothing written outside this folder: savefig calls caught %d (%s); __pycache__ of figures/ and of "
    "learning/code/, learning/analysis/ and learning/code/ unchanged; figS_*.pdf/png untouched"
    % (len(SAVED), ", ".join(os.path.basename(p) for p in SAVED)))
say("wrote %d data files" % (len(set(written)) + 1))
say()
say("ALL ASSERTIONS PASSED")
with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(OUT) + "\n")
