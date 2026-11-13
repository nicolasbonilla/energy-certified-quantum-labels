"""SM figure of the second benchmark (arXiv:2106.12627): the rule on a public dataset of 2-D random Heisenberg models.

  python figS_huang.py     -> figS_huang.pdf / .png
Restyled from phase3/full_runs/huang/code/plot_h.py (same data, same panels) in the paper's style.  Reads only
phase3/full_runs/huang/laptop_analysis/summary_huang.json (read-only).
(a) two-sided width / tau vs delta e, n = 20, instance (4,1), exact; (b) the same at n = 45, instance (9,1)
(solid: outer, DMRG-referenced; dashed: inner, rigorous); (c) delta e* per label vs n (filled: computed; bar: band
between the rigorous inner and the DMRG-referenced outer value; open: the rule tau^2/(8 chi)); (d) delta e* of all
570 pair correlators at n = 20 by pair class.  Shaded: delta e in [1e-3, 1e-2].
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402

F_HU = os.path.join(C.ROOT, "phase3", "full_runs", "huang", "laptop_analysis", "summary_huang.json")
TAU = 0.08
COL = {"Cnn": "#2a78d6", "Cd2": "#eb6834", "Ccent": "#1baf7a", "Cfar": "#b07d00", "Cfix": "#d0628f"}
MARK = {"Cnn": "o", "Cd2": "s", "Ccent": "^", "Cfar": "D", "Cfix": "v"}
NAME = {"Cnn": r"$\bar C_{\rm nn}$ (average)", "Cd2": r"$\bar C_{\rm diag}$ (average)",
        "Ccent": r"$C_{\rm cent}$ (central bond)", "Cfar": r"$C_{\rm far}$ (end to end)",
        "Cfix": r"$C_{(7,12)}$ (fixed bond)"}
CLS = [("nn", "nearest neighbours", "#2a78d6"), ("diag", "diagonal pairs", "#eb6834"),
       ("r<=3", r"other, $r\leq3$", "#1baf7a"), ("r>3", r"other, $r>3$", "#b07d00")]
BAND = "#efeeea"


def rc():
    plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                         "axes.formatter.use_mathtext": True, "axes.unicode_minus": False, "font.size": 8,
                         "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.6,
                         "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                         "axes.edgecolor": "#555555", "xtick.color": "#444444", "ytick.color": "#444444",
                         "pdf.fonttype": 42})


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def main():
    rc()
    s = json.load(open(F_HU, encoding="utf-8"))
    rows = s["rows"]
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 5.4))
    for ax, (L, k, meth, title) in zip(axs[0], ((4, 1, "ED", r"$n=20$, instance (4,1), exact"),
                                                (9, 1, "DMRG", r"$n=45$, instance (9,1)"))):
        clean(ax)
        ax.axvspan(1e-3, 1e-2, color=BAND, lw=0, zorder=0)
        for lab in ("Cnn", "Cd2", "Ccent", "Cfar", "Cfix"):
            r = [x for x in rows if x["L"] == L and x["k"] == k and x["label"] == lab and x["method"] == meth
                 and not x.get("alias_of")]
            if not r or (lab == "Cfix" and L == 4):            # at n = 20 the fixed bond is the central bond
                continue
            w = r[0]["tau"]["widths"]
            de = [x["de"] for x in w]
            ax.plot(de, [x["w_out"] / TAU for x in w], color=COL[lab], lw=1.2, marker=MARK[lab], ms=3.2,
                    label=NAME[lab])
            if meth == "DMRG":
                ax.plot(de, [x["w_in"] / TAU for x in w], color=COL[lab], lw=0.8, ls=(0, (3, 2)))
        ax.axhline(1.0, color="#0b0b0b", lw=0.8)
        ax.text(2.2e-3, 1.08, r"certified below this line ($\tau=0.08$)", fontsize=6.6, color="#0b0b0b",
                va="bottom")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(r"energy error per site $\delta e$")
        ax.set_ylabel(r"width $/\,\tau$")
        ax.set_title(title, fontsize=8, loc="left")
    axs[0][1].text(0.98, 0.04, "solid: outer (DMRG-referenced)\ndashed: inner (rigorous)", transform=axs[0][1].transAxes,
                   fontsize=6.4, ha="right", va="bottom", color="#444444")
    ax = axs[1][0]
    clean(ax)
    ax.axhspan(1e-3, 1e-2, color=BAND, lw=0, zorder=0)
    off = {"Cnn": -1.6, "Cd2": -0.8, "Ccent": 0.0, "Cfar": 0.8, "Cfix": 1.6}
    for lab in ("Cnn", "Cd2", "Ccent", "Cfar", "Cfix"):
        xs, ys, yl = [], [], []
        for r in rows:
            if r["label"] != lab or (r["method"] == "DMRG" and r["n"] == 20) or (lab == "Cfix" and r["n"] == 20):
                continue
            t = r["tau"]
            v = t["de_out"]
            if v:
                x = r["n"] + off[lab]
                xs.append(x)
                ys.append(v)
                yl.append(t["de_law"])
                if r["method"] == "DMRG" and t["de_in"]:
                    ax.plot([x, x], [t["de_out"], t["de_in"]], color=COL[lab], lw=1.0, zorder=2)
        ax.scatter(xs, ys, color=COL[lab], marker=MARK[lab], s=14, label=NAME[lab], zorder=3, lw=0)
        ax.scatter(xs, yl, facecolor="none", edgecolor=COL[lab], marker=MARK[lab], s=34, lw=0.7, zorder=2)
    ax.set_yscale("log")
    ax.set_xticks([20, 30, 45])
    ax.set_xlim(14, 51)
    ax.set_xlabel(r"number of spins $n$")
    ax.set_ylabel(r"$\delta e^*$ (largest certified $\delta e$)")
    ax.set_title("filled: computed; open: the rule; bars: inner--outer band", fontsize=7, loc="left", color="#444444")
    ax = axs[1][1]
    clean(ax)
    ax.axvspan(1e-3, 1e-2, color=BAND, lw=0, zorder=0)
    allv = [r["tau"]["de_out"] for rs in s["pairs"].values() for r in rs if r["tau"]["de_out"]]
    bins = np.geomspace(min(allv) / 1.2, max(max(allv) * 1.2, 1.2e-2), 30)
    for cls, name, col in CLS:
        v = [r["tau"]["de_out"] for rs in s["pairs"].values() for r in rs if r["cls"] == cls and r["tau"]["de_out"]]
        ax.hist(v, bins=bins, histtype="step", lw=1.1, color=col, label="%s (%d)" % (name, len(v)))
    ax.set_xscale("log")
    ax.set_xlabel(r"$\delta e^*$ of each pair correlator $C_{ij}$, $n=20$")
    ax.set_ylabel("number of pairs")
    ax.set_title(r"the benchmark's own labels (570 pairs)", fontsize=8, loc="left")
    ax.legend(frameon=False, loc="upper right")
    for a, t in zip(axs.flat, "abcd"):
        a.text(-0.13, 1.06, "(%s)" % t, transform=a.transAxes, fontsize=9, fontweight="bold", va="bottom")
    hs = {}
    for a in (axs[0][0], axs[0][1]):
        for h, l in zip(*a.get_legend_handles_labels()):
            hs.setdefault(l, h)
    fig.legend(list(hs.values()), list(hs.keys()), loc="upper center", ncol=5, frameon=False,
               bbox_to_anchor=(0.5, 1.0), handlelength=1.8, columnspacing=1.2)
    fig.tight_layout(h_pad=1.4, w_pad=1.6, rect=(0, 0, 1, 0.95))
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(C.HERE, "figS_huang." + ext), dpi=300)
    print("wrote figS_huang.pdf/.png;", len(allv), "pair labels")
    assert len(allv) == 570


if __name__ == "__main__":
    main()
