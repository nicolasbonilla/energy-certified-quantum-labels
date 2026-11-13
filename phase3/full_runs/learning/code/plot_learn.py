"""Figures of the learning run (laptop).

  python plot_learn.py <analysis_dir> [<id_set> <ood_set>]
Writes <analysis_dir>/fig_learner_panel.png (draft of the new Fig. 1 learner panel; learner M1, delta e = 5e-3) and
<analysis_dir>/fig_learning_supp.png (both learners; risk-coverage curves).

Panel: coverage of the TRUE labels against the mean interval width, for averages (circles) and single nn pairs
(triangles), labels from the realistic truncated-subspace generator (blue) or the energy-valid adversary (orange);
open = standard split conformal calibrated on the generator's labels, filled = certified split conformal (the
calibration labels enter through their certified energy-window intervals); x = the exact-label baseline (aqua).
Dashed: nominal 0.90 and the tolerance tau = 0.08. Colors: the first three slots of the dataviz reference palette
(validated all-pairs); identity is also carried by marker shape and fill, and by direct labels.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
SURF = "#fcfcfb"
TAU = 0.08


def panel(ax, r, title=None, legend=True, de="5"):
    c = r["coverage"]
    sets = [("gen" + de, BLUE, "realistic generator"), ("advL" + de, ORANGE, "energy-valid adversary")]
    shapes = {"avg": ("o", "averages"), "nn": ("^", "single pairs")}
    for cl, (mk, nm) in shapes.items():
        ex = c["exact"]["SC"][cl]
        ax.plot(ex["wid_id"], ex["covT_id"], marker="x", ms=8, mew=2, color=AQUA, ls="none", zorder=4)
        for ls, col, _ in sets:
            a, b = c[ls]["SC"][cl], c[ls]["CSC"][cl]
            ax.annotate("", xy=(b["wid_id"], b["covT_id"]), xytext=(a["wid_id"], a["covT_id"]),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2, alpha=0.55, shrinkA=6, shrinkB=6))
            ax.plot(a["wid_id"], a["covT_id"], marker=mk, ms=9, mfc=SURF, mec=col, mew=2, ls="none", zorder=5)
            ax.plot(b["wid_id"], b["covT_id"], marker=mk, ms=9, mfc=col, mec=SURF, mew=1.5, ls="none", zorder=6)
        ax.annotate(nm, xy=(c["gen" + de]["CSC"][cl]["wid_id"], c["gen" + de]["CSC"][cl]["covT_id"]),
                    xytext=(0, 10), textcoords="offset points", ha="center", va="bottom", fontsize=8, color=INK2)
    ax.axhline(0.9, color=INK2, lw=1, ls="--", zorder=1)
    ax.axvline(TAU, color=INK2, lw=1, ls=":", zorder=1)
    ax.text(TAU * 1.04, 0.02, "tolerance $\\tau$", transform=ax.get_xaxis_transform(), fontsize=7.5, color=INK2,
            ha="left", va="bottom")
    ax.text(0.5, 0.897, "nominal 90 %", transform=ax.get_yaxis_transform(), fontsize=7.5, color=INK2, ha="center",
            va="top")
    ax.set_xscale("log")
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    tk = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
    ax.xaxis.set_major_locator(FixedLocator(tk))
    ax.xaxis.set_major_formatter(FixedFormatter(["0.02", "0.05", "0.1", "0.2", "0.5", "1"]))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlim(0.04, 1.3)
    ax.set_xlabel("mean interval width (correlator units)", color=INK)
    ax.set_ylabel("coverage of the true labels", color=INK)
    lo = min(0.5, min(c[ls]["SC"][cl]["covT_id"] for ls, _, _ in sets for cl in shapes) - 0.05)
    ax.set_ylim(lo, 1.02)
    ax.grid(True, which="major", color=GRID, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    if title:
        ax.set_title(title, fontsize=9, color=INK, loc="left", pad=14)
    if legend:
        from matplotlib.lines import Line2D
        h = [Line2D([], [], marker="s", ls="none", mfc=BLUE, mec=BLUE, label=sets[0][2]),
             Line2D([], [], marker="s", ls="none", mfc=ORANGE, mec=ORANGE, label=sets[1][2]),
             Line2D([], [], marker="o", ls="none", mfc=SURF, mec=INK2, mew=1.5, label="standard conformal"),
             Line2D([], [], marker="o", ls="none", mfc=INK2, mec=INK2, label="certified conformal"),
             Line2D([], [], marker="x", ls="none", color=AQUA, mew=2, label="exact labels (reference)")]
        ax.legend(handles=h, fontsize=7, frameon=False, loc="lower right")


def risk_panel(ax, r, key, title):
    a = r["abstention"][key]
    cg = np.array(r["cgrid"])
    for rk, col, ls_, nm in (("oracle", INK2, ":", "oracle"), ("CB", BLUE, "-", "certified width (CB)"),
                             ("BAND", AQUA, "-", "label band W(x)"), ("NC", ORANGE, "--", "conformal width (NC)"),
                             ("random", GRID, "-", "random")):
        ax.plot(cg, a["ex"][rk], color=col, ls=ls_, lw=2, label=nm)
    ax.set_xlabel("fraction of queries answered", color=INK)
    ax.set_ylabel("P(|error vs truth| > $\\tau$/2 | answered)", color=INK)
    ax.set_ylim(0, None)
    ax.grid(True, color=GRID, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.set_title(title, fontsize=9, color=INK, loc="left")
    ax.legend(fontsize=7, frameon=False)


def main(an, sid="D", sood="O"):
    R = {M: json.load(open(os.path.join(an, "learn_%s_%s_%s.json" % (M, sid, sood)))) for M in ("M1", "M2")
         if os.path.exists(os.path.join(an, "learn_%s_%s_%s.json" % (M, sid, sood)))}
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.facecolor": SURF, "figure.facecolor": SURF})
    fig, ax = plt.subplots(figsize=(3.6, 3.1), dpi=300)
    panel(ax, R["M1"])
    fig.tight_layout()
    fig.savefig(os.path.join(an, "fig_learner_panel.png"))
    plt.close(fig)
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 6.4), dpi=200)
    panel(axs[0, 0], R["M1"], "(a) benchmark learner (M1), $\\delta e$ = 5e-3")
    if "M2" in R:
        panel(axs[0, 1], R["M2"], "(b) local learner (M2), $\\delta e$ = 5e-3", legend=False)
    risk_panel(axs[1, 0], R["M1"], "gen5|all|id|0.08", "(c) M1, realistic generator, all queries")
    risk_panel(axs[1, 1], R["M1"], "advL5|all|id|0.08", "(d) M1, energy-valid adversary, all queries")
    fig.tight_layout()
    fig.savefig(os.path.join(an, "fig_learning_supp.png"))
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main(*sys.argv[1:])
