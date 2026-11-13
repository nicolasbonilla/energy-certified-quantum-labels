"""Figure 4: a learner trained and validated on same-method labels, two null models, and the abstaining rule.

  python fig4_learning.py

(a, b) m_s vs Jz at n = 57 and 115: DMRG reference (line), the emulated method's labels (open circles), and the
       predictions of models trained on those labels on the grid Jz in [1.6, 6.0] (the paper-like per-site MLP stack
       and the nearest-neighbour null); OOD test points 1.1-1.4 shaded; the learner abstains left of J = 3.3.
(c)    Relative m_s error at the OOD point Jz = 1.2 against new same-method labels (the validation available to a
       data generator) and against the DMRG reference, for every model and both n.
Sources: phase3/full_runs/method/laptop_post/out/ml/ml_n{57,115}.json (models.*.rows), ref/ (DMRG m_s),
         emu/ (var.primary.labels.m_s). Adapted from phase3/full_runs/method/code/figs.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import common as C  # noqa: E402

MODELS = [("poly3_invJ", "cubic in $1/J_z$"), ("mlp_pilot3", "small MLP"), ("ibm_arch1", "per-site MLP stack"),
          ("null_nn", "nearest-neighbour null"), ("null_const", "constant null")]


def main():
    C.style(plt)
    ref, emu = C.meth_ref(), C.meth_emu()
    fig = plt.figure(figsize=(C.FULL_W, 2.35))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.15], wspace=0.40)
    axs = [fig.add_subplot(gs[0, k]) for k in range(3)]
    for ax, n in zip(axs[:2], (57, 115)):
        m = C.meth_ml(n)
        js = sorted(j for (nn, j) in ref if nn == n)
        ax.axvspan(1.05, 1.45, color=C.OOD_SHADE, lw=0, zorder=0)
        ax.axvspan(1.05, m["Jstar"], color="#f6e1de", alpha=0.45, lw=0, zorder=0)
        ax.axvline(m["Jstar"], color=C.MUTED, lw=0.8, ls=(0, (4, 2)))
        ax.plot(js, [ref[(n, j)]["labels"]["m_s"] for j in js], "-", color=C.INK, lw=1.3, label="DMRG reference")
        je = sorted(j for (nn, j) in emu if nn == n)
        ax.plot(je, [emu[(n, j)]["var"]["primary"]["labels"]["m_s"] for j in je], "o", mfc="white", mec="#c0392b",
                ms=3.4, mew=0.8, label="method labels")
        for key, st, c in (("ibm_arch1", "^", "#2a78d6"), ("null_nn", "x", "#6250d6")):
            rows = m["models"][key]["rows"]
            ax.plot([r["Jz"] for r in rows], [r["m_s_pred_labels"] for r in rows], st, color=c, ms=3.4, mew=0.8,
                    mfc="none", label=dict(MODELS)[key])
        ax.set_xlabel(r"$J_z$")
        ax.set_xlim(1.05, 6.2)
        ax.set_ylim(0.55, 1.01)
        ax.text(1.1, 0.565, "OOD", fontsize=6, color=C.MUTED)
        ax.text(m["Jstar"] + 0.08, 0.6, "answers →", fontsize=6, color=C.MUTED)
        ax.set_title("(%s) $n=%d$" % ("ab"[n == 115], n), fontsize=8)
        ax.grid(True, color=C.GRID, lw=0.4)
    axs[0].set_ylabel("$m_s$")
    axs[0].legend(frameon=False, loc="center right", fontsize=5.9, handlelength=1.1)

    ax = axs[2]
    x = np.arange(len(MODELS))
    w = 0.19
    for k, (n, hatch) in enumerate(((57, None), (115, "////"))):
        m = C.meth_ml(n)
        same, dm = [], []
        for key, _ in MODELS:
            r = [r for r in m["models"][key]["rows"] if abs(r["Jz"] - 1.2) < 1e-9][0]
            same.append(r["err_vs_samemethod_pct"]); dm.append(r["err_vs_dmrg_pct"])
        off = (-1.5 + 2 * k) * w
        ax.bar(x + off, same, w, color="#9ecae1", edgecolor="#2471a3", hatch=hatch, lw=0.5,
               label="vs same-method labels" if k == 0 else None)
        ax.bar(x + off + w, dm, w, color="#f4a582", edgecolor="#b2182b", hatch=hatch, lw=0.5,
               label="vs DMRG" if k == 0 else None)
    ax.set_yscale("log")
    ax.set_ylim(0.01, 4000)
    ax.set_xticks(x)
    ax.set_xticklabels(["cubic", "MLP", "per-site\nMLP", "NN\nnull", "const.\nnull"], fontsize=6.2)
    ax.set_ylabel(r"error at $J_z=1.2$ (%)")
    h, l = ax.get_legend_handles_labels()
    h.append(plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=C.MUTED, hatch="////", lw=0.5))
    l.append("$n=115$ (hatched)")
    ax.legend(h, l, frameon=False, loc="upper left", fontsize=5.9, ncol=2, handlelength=1.0, columnspacing=0.8)
    ax.set_title("(c) the same-method test", fontsize=8)
    ax.grid(True, axis="y", color=C.GRID, lw=0.4)
    C.save(fig, "fig4_learning")


if __name__ == "__main__":
    main()
