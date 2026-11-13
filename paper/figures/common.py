"""Shared paths, loaders and style for the paper figures (laptop only; reads deposited outputs, writes nothing there).

Every number drawn comes from one of the files below; nothing is typed by hand except plot styling.
Paths are relative to J_next_paper/ (the folder that holds phase3/ and paper/).
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))          # J_next_paper/
MAP = os.path.join(ROOT, "phase3", "full_runs", "map")
METH = os.path.join(ROOT, "phase3", "full_runs", "method")
R3 = os.path.join(ROOT, "paper", "data", "r3gen", "out")         # copy of the session's r3gen toy outputs

F_MAP_SUMMARY = os.path.join(MAP, "laptop_analysis", "summary_map.json")
F_READINGS = os.path.join(MAP, "code", "readings_declared.json")
F_METH_SUMMARY = os.path.join(METH, "laptop_post", "out", "summary.json")
D_METH_EMU = os.path.join(METH, "laptop_post", "out", "emu")
D_METH_REF = os.path.join(METH, "laptop_post", "out", "ref")
D_METH_ML = os.path.join(METH, "laptop_post", "out", "ml")

J_ABSTAIN = 3.3        # abstention threshold used by the learning test (method DECLARATION / ml_n*.json "Jstar")

# style: two-column APS figure widths (inches)
COL_W, FULL_W = 3.375, 7.0
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
OOD_SHADE, CERT_SHADE = "#efeeea", "#e3f1e6"
LAB = [("m_s", r"$m_s$", "#2a78d6", "o", "-"),
       ("Czz_bar", r"$\bar C_{zz}$", "#eb6834", "s", "-"),
       ("C2_bar", r"$\bar C_{2}$", "#1baf7a", "D", "-"),
       ("Z_bulk", r"$Z_{\rm bulk}$", "#b07d00", "v", "--"),
       ("Z_boundary", r"$Z_{\rm bdry}$", "#d0628f", "^", "--"),
       ("Czz_edge", r"$C_{zz}^{\rm edge}$", "#007a3d", "<", "--"),
       ("Z_loop", r"$Z_{\rm loop}$", "#6250d6", ">", "--")]


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def map_summary():
    return rj(F_MAP_SUMMARY)


def map_row(S, n, Jz, label):
    for r in S["rows"]:
        if r["n"] == n and abs(r["Jz"] - Jz) < 1e-9 and r["label"] == label:
            return r
    return None


def meth_summary():
    return rj(F_METH_SUMMARY)


def meth_emu():
    out = {}
    for p in glob.glob(os.path.join(D_METH_EMU, "emu_n*_J*.json")):
        r = rj(p)
        out[(r["n"], round(r["Jz"], 1))] = r
    return out


def meth_ref():
    out = {}
    for p in glob.glob(os.path.join(D_METH_REF, "ref_n*_J*.json")):
        r = rj(p)
        out[(r["n"], round(r["Jz"], 1))] = r
    return out


def meth_ml(n):
    return rj(os.path.join(D_METH_ML, "ml_n%d.json" % n))


def style(plt):
    plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5, "legend.fontsize": 6.8,
                         "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.edgecolor": MUTED,
                         "axes.linewidth": 0.6, "xtick.color": MUTED, "ytick.color": MUTED,
                         "axes.labelcolor": INK, "font.family": "serif", "mathtext.fontset": "cm",
                         "savefig.dpi": 300, "pdf.fonttype": 42})


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(HERE, name + "." + ext), bbox_inches="tight")
    print("wrote", os.path.join(HERE, name + ".{pdf,png}"))
