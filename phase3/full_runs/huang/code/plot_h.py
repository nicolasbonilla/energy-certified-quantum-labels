"""Draft figure of the Huang-benchmark certification run (laptop; reads summary_huang.json from analyze_h.py).

  python plot_h.py <summary_huang.json> <out.png>
(a), (b) two-sided width / tau vs delta e for the featured labels at n = 20 (instance (4, 1), exact) and n = 45
(instance (9, 1); solid = outer, DMRG-referenced; dashed = inner, rigorous); (c) delta e* per label vs n (filled =
computed, open = the rule tau^2/(8 chi)); (d) delta e* of all n = 20 pair correlators by class. Shaded: the device
range delta e in [1e-3, 1e-2].
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SLOT = {"Cnn": "#2a78d6", "Cd2": "#eb6834", "Ccent": "#1baf7a", "Cfar": "#eda100", "Cfix": "#e87ba4"}
MARK = {"Cnn": "o", "Cd2": "s", "Ccent": "^", "Cfar": "D", "Cfix": "v"}
NAME = {"Cnn": "C̄ nn (average)", "Cd2": "C̄ diag (average)", "Ccent": "C central bond", "Cfar": "C end-to-end",
        "Cfix": "C bond (7,12)"}
CLS = [("nn", "#2a78d6"), ("diag", "#eb6834"), ("r<=3", "#1baf7a"), ("r>3", "#eda100")]
INK, INK2, GRID, BAND = "#0b0b0b", "#52514e", "#e4e3df", "#f1efe8"


def style(ax):
    ax.set_facecolor("#fcfcfb")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def main(sp, outp):
    s = json.load(open(sp))
    rows = s["rows"]
    fig, axs = plt.subplots(2, 2, figsize=(10, 7.6))
    fig.patch.set_facecolor("#fcfcfb")
    for ax, (L, k, meth, title) in zip(axs[0], ((4, 1, "ED", "(a) n = 20, instance (4,1), exact"),
                                                (9, 1, "DMRG", "(b) n = 45, instance (9,1)"))):
        style(ax)
        ax.axvspan(1e-3, 1e-2, color=BAND, zorder=0)
        drawn = 0
        for lab in ("Cnn", "Cd2", "Ccent", "Cfar", "Cfix"):
            r = [x for x in rows if x["L"] == L and x["k"] == k and x["label"] == lab and x["method"] == meth
                 and not x.get("alias_of")]
            if not r:
                continue
            w = r[0]["tau"]["widths"]
            de = [x["de"] for x in w]
            ax.plot(de, [x["w_out"] / 0.08 for x in w], color=SLOT[lab], lw=2, marker=MARK[lab], ms=6,
                    label=NAME[lab])
            ax.plot(de, [x["w_in"] / 0.08 for x in w], color=SLOT[lab], lw=1.2, ls="--")
            drawn += 1
        ax.axhline(1.0, color=INK, lw=1)
        if drawn:
            ax.text(1.05e-3, 1.05, "certified below this line (τ = 0.08, ±3 % of range)", fontsize=7, color=INK)
        if drawn:
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.legend(fontsize=7, frameon=False, loc="lower right")
        else:
            ax.text(0.5, 0.5, "no data", transform=ax.transAxes, ha="center", color=INK2)
        ax.set_xlabel("intensive energy error δe (paper units)", fontsize=9, color=INK)
        ax.set_ylabel("two-sided width / τ", fontsize=9, color=INK)
        ax.set_title(title, fontsize=10, color=INK, loc="left")
    ax = axs[1][0]
    style(ax)
    ax.axhspan(1e-3, 1e-2, color=BAND, zorder=0)
    off = {"Cnn": -1.2, "Cd2": -0.6, "Ccent": 0.0, "Cfar": 0.6, "Cfix": 1.2}
    for lab in ("Cnn", "Cd2", "Ccent", "Cfar", "Cfix"):
        xs, ys, yl = [], [], []
        for r in rows:
            if r["label"] != lab or (r["method"] == "DMRG" and r["n"] == 20):
                continue
            t = r["tau"]
            v = t["de_out"] or (t["eps_out_lb"] / r["n"] if t["eps_out_lb"] else None)
            if v:
                xs.append(r["n"] + off[lab]); ys.append(v); yl.append(t["de_law"])
                if r["method"] == "DMRG" and t["de_in"] and t["de_out"]:     # reference band (outer .. inner)
                    ax.plot([r["n"] + off[lab]] * 2, [t["de_out"], t["de_in"]], color=SLOT[lab], lw=1.5, zorder=2)
        if xs:
            ax.scatter(xs, ys, color=SLOT[lab], marker=MARK[lab], s=36, label=NAME[lab], zorder=3,
                       edgecolor="#fcfcfb", lw=1)
            ax.scatter(xs, yl, facecolor="none", edgecolor=SLOT[lab], marker=MARK[lab], s=70, lw=1.2, zorder=2)
    ax.set_yscale("log")
    ax.set_xticks([20, 30, 45])
    ax.set_xlabel("number of spins n", fontsize=9, color=INK)
    ax.set_ylabel("δe* (filled: computed; bar: DMRG band; open: rule)", fontsize=9, color=INK)
    ax.set_title("(c) energy error at which each label stops being certified", fontsize=10, color=INK, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="best")
    ax = axs[1][1]
    style(ax)
    ax.axvspan(1e-3, 1e-2, color=BAND, zorder=0)
    allv = [r["tau"]["de_out"] for rs in s["pairs"].values() for r in rs if r["tau"]["de_out"]]
    if allv:
        bins = np.geomspace(min(allv) / 1.2, max(max(allv) * 1.2, 1.2e-2), 30)
        for cls, col in CLS:
            v = [r["tau"]["de_out"] for rs in s["pairs"].values() for r in rs if r["cls"] == cls and r["tau"]["de_out"]]
            if v:
                ax.hist(v, bins=bins, histtype="step", lw=2, color=col, label="%s (%d)" % (cls, len(v)))
    ax.set_xscale("log")
    ax.set_xlabel("δe* of each pair correlator C_ij, n = 20 (three instances)", fontsize=9, color=INK)
    ax.set_ylabel("number of pair labels", fontsize=9, color=INK)
    ax.set_title("(d) the benchmark's own labels", fontsize=10, color=INK, loc="left")
    ax.legend(fontsize=7, frameon=False, title="pair class", title_fontsize=7)
    fig.tight_layout()
    fig.savefig(outp, dpi=160, facecolor=fig.get_facecolor())
    print("wrote", outp)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
