"""SM figure of the learning run (Track-1 integration pass, 2026-11-04): the panels of
phase3/full_runs/learning/code/plot_learn.py (coverage of the true labels against width for both learners;
risk-coverage curves), drawn with the paper's fonts into paper/figures/.  The result folder is only read: the module
is imported with bytecode writing disabled, and its own outputs (analysis/fig_*.png) are not touched.
Source: phase3/full_runs/learning/analysis/learn_M1_D_O.json, learn_M2_D_O.json.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402

LRN = os.path.join(C.ROOT, "phase3", "full_runs", "learning")
sys.path.insert(0, os.path.join(LRN, "code"))
import plot_learn as PL  # noqa: E402


def main():
    R = {M: json.load(open(os.path.join(LRN, "analysis", "learn_%s_D_O.json" % M), encoding="utf-8"))
         for M in ("M1", "M2")}
    plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                         "axes.formatter.use_mathtext": True, "axes.unicode_minus": False, "font.size": 8,
                         "axes.facecolor": "white", "figure.facecolor": "white", "pdf.fonttype": 42})
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 6.0))
    PL.panel(axs[0, 0], R["M1"], "(a) benchmark model (M1), $\\delta e=5\\times10^{-3}$")
    PL.panel(axs[0, 1], R["M2"], "(b) local model (M2), $\\delta e=5\\times10^{-3}$", legend=False)
    PL.risk_panel(axs[1, 0], R["M1"], "gen5|all|id|0.08", "(c) M1, realistic labels, all queries")
    PL.risk_panel(axs[1, 1], R["M1"], "advL5|all|id|0.08", "(d) M1, shifted labels, all queries")
    for ax in axs[1]:            # cmr10 has no text glyphs for "|" and ">": set the label in mathtext
        ax.set_ylabel(r"$P(\,|f-y^*|>\tau/2\ \mathrm{given\ answered})$")
    for ax in axs.flat:          # wording of the main text
        for t in ax.texts:
            t.set_text(t.get_text().replace("single pairs", "single bonds"))
        lg = ax.get_legend()
        if lg:
            for t in lg.get_texts():
                t.set_text(t.get_text().replace("energy-valid adversary", "shifted labels")
                           .replace("realistic generator", "realistic labels"))
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(C.HERE, "figS_learning." + ext), dpi=300)
    print("wrote figS_learning.{pdf,png}")


if __name__ == "__main__":
    main()
