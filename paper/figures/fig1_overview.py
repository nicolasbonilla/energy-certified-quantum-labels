"""Main Fig. 1 (Track-1 integration pass, 2026-11-04): the pipeline, the law against system size, the learner.

(a) Schematic: quantum processor -> label y and energy E -> energy window W(E) (contains the generated state and the
    ground state) -> energy interval [lo, hi] (contains y and the true label y*) -> train/answer if its width is
    at most tau, otherwise abstain.  No data.
(b) delta e* (largest energy error per site at which a label is certified at tolerance tau) against n, for one
    average and one local label of two models:
      heavy-hex XXZ at Jz = 4.0 (n = 19, 57, 115): Czz_bar and Z_bulk; summary_map.json rows[*].de_star_out
      (marker) and de_star_in (bar end);
      random Heisenberg benchmark (n = 20, 30, 45): C_nn average (every computed instance) and the bond (7,12) in the
      instances with identical surroundings, (4,1) -> (6,1) -> (9,1); summary_huang.json rows[*].tau.de_out / de_in
      (at n = 20 that bond is the row "Ccent" of instance (4,1), exact diagonalization).
    Dotted guides: proportional to 1/n through the smallest size of each local series.
(c) Learning on the public benchmark (all 100 n = 20 instances, delta e = 5e-3, 200 splits, nominal 0.90), labels
    shifted within the energy window toward less order (label set advL5): coverage of the TRUE labels by standard
    split conformal (open) and by certified split conformal (filled); the arrow starts at the coverage the standard
    method reports on its own (shifted) labels.  Right: width of the certified over the standard interval, with
    realistic-generator labels (gen5) and with the shifted labels (advL5).
    Source: phase3/full_runs/learning/analysis/learn_M{1,2}_D_O.json coverage[set][SC|CSC][avg|nn].{covT_id,covO_id,
    wid_id}.  Restyled from phase3/full_runs/learning/code/plot_learn.py (that file is not modified).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

import common as C  # noqa: E402

F_HU = os.path.join(C.ROOT, "phase3", "full_runs", "huang", "laptop_analysis", "summary_huang.json")
F_L = os.path.join(C.ROOT, "phase3", "full_runs", "learning", "analysis", "learn_%s_D_O.json")

CERT, SHORE, WARM, INK, MUTE, LIGHT = "#169b88", "#0b5f53", "#cf5521", "#1d1d1d", "#6f6f6b", "#e9ebed"
BLUE = "#2a78d6"


def rc():
    plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                         "axes.formatter.use_mathtext": True, "axes.unicode_minus": False, "font.size": 8,
                         "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.8,
                         "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                         "axes.edgecolor": "#555555", "xtick.color": "#444444", "ytick.color": "#444444",
                         "pdf.fonttype": 42})


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ----------------------------------------------------------------------------------------------- (a) schematic
def box(ax, x, y, w, h, title, sub, fc, ec, tc=INK, fs=8.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.05", fc=fc, ec=ec, lw=0.8,
                                zorder=2))
    ax.text(x + w / 2, y + h - 0.13, title, ha="center", va="top", fontsize=fs, color=tc, zorder=3)
    if sub:
        ax.text(x + w / 2, y + 0.10, sub, ha="center", va="bottom", fontsize=6.6, color=MUTE, zorder=3,
                linespacing=1.15)


def arrow(ax, p, q, col=MUTE):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=0.9, color=col, zorder=1,
                                 shrinkA=1, shrinkB=1))


def schematic(ax):
    ax.set_xlim(-0.05, 10.05)
    ax.set_ylim(0.08, 1.12)
    ax.axis("off")
    H, Y = 0.92, 0.15
    # 1. processor: a small heavy-hex-like motif of dots and bonds
    box(ax, 0.0, Y, 1.45, H, "quantum processor", "", "#f4f4f2", "#9a9a96", fs=7.4)
    import numpy as np
    xs = 0.28 + 0.225 * np.arange(5)
    for row, yy in enumerate((0.38, 0.66)):
        ax.plot(xs, [yy] * 5, color="#aaa79f", lw=1.0, zorder=3)
        ax.scatter(xs, [yy] * 5, s=11, color=WARM if row == 0 else "#ef8d55", zorder=4, lw=0)
    for k in (0, 2, 4):
        ax.plot([xs[k], xs[k]], [0.38, 0.66], color="#aaa79f", lw=1.0, zorder=3)
    # 2. label and energy
    box(ax, 1.85, Y, 1.50, H, r"label $y$, energy $E$", "one sample per\nHamiltonian $H(x)$", "#f4f4f2", "#9a9a96")
    # 3. window
    box(ax, 3.75, Y, 2.00, H, r"energy window $\mathcal{W}(E)$", "all states with energy $\leq E$;\n"
        "it holds the generated state\nand the ground state", "#f4f4f2", "#9a9a96")
    # 4. energy interval with a small bar
    box(ax, 6.15, Y, 1.85, H, "energy interval", "", "#e3f1ee", CERT)
    bx0, bx1, by = 6.45, 7.70, 0.50
    ax.plot([bx0, bx1], [by, by], color=CERT, lw=3.0, solid_capstyle="butt", zorder=3)
    for xx in (bx0, bx1):
        ax.plot([xx, xx], [by - 0.07, by + 0.07], color=SHORE, lw=1.0, zorder=3)
    ax.scatter([6.80], [by + 0.06], marker="v", s=16, color=INK, zorder=4, lw=0)
    ax.text(6.80, by + 0.11, r"label $y$", ha="center", va="bottom", fontsize=6.6, color=INK)
    ax.scatter([7.38], [by + 0.06], marker="v", s=16, color=SHORE, zorder=4, lw=0)
    ax.text(7.38, by + 0.11, r"true $y^*$", ha="center", va="bottom", fontsize=6.6, color=SHORE)
    ax.text((bx0 + bx1) / 2, by - 0.10, r"width $w$; tolerance $\tau$", ha="center", va="top", fontsize=6.6, color=SHORE)
    # 5. decision
    box(ax, 8.40, 0.64, 1.60, 0.43, r"$w\leq\tau$: use", "", CERT, CERT, tc="white", fs=7.6)
    box(ax, 8.40, 0.15, 1.60, 0.43, r"$w>\tau$: abstain", "", "#dcdcd8", "#9a9a96", tc=INK, fs=7.6)
    for a, b in (((1.45, 0.61), (1.85, 0.61)), ((3.35, 0.61), (3.75, 0.61)), ((5.75, 0.61), (6.15, 0.61))):
        arrow(ax, a, b)
    arrow(ax, (8.0, 0.70), (8.40, 0.86), CERT)
    arrow(ax, (8.0, 0.52), (8.40, 0.37))


# ----------------------------------------------------------------------------------------------- (b) law vs n
def law(ax):
    S = C.map_summary()
    hu = json.load(open(F_HU, encoding="utf-8"))["rows"]

    def hrow(L, k, lab, meth):
        r = [x for x in hu if x["L"] == L and x["k"] == k and x["label"] == lab and x["method"] == meth
             and not x.get("alias_of")]
        return r[0] if r else None

    # heavy-hex XXZ, Jz = 4.0
    for lab, col, mk, nm in (("Czz_bar", CERT, "s", r"$\bar C_{zz}$"), ("Z_bulk", WARM, "s", r"$Z_{\rm bulk}$")):
        P = [(n, C.map_row(S, n, 4.0, lab)) for n in (19, 57, 115)]
        ns = [n for n, _ in P]
        vo = [r["de_star_out"] for _, r in P]
        vi = [r["de_star_in"] for _, r in P]
        ax.plot(ns, vo, color=col, lw=1.0, zorder=3)
        ax.scatter(ns, vo, marker=mk, s=22, color=col, zorder=4, lw=0)
        for n, a, b in zip(ns, vo, vi):
            ax.plot([n, n], [a, b], color=col, lw=0.9, zorder=3)
        if lab == "Z_bulk":
            ax.plot([19, 140], [vo[0] * 1.35, vo[0] * 1.35 * 19 / 140], color=MUTE, lw=0.7, ls=":", zorder=2)
    # random Heisenberg benchmark
    cnn = [(20, hrow(4, k, "Cnn", "ED")) for k in (1, 2, 3)] + [(30, hrow(6, 1, "Cnn", "DMRG"))] + \
          [(45, hrow(9, k, "Cnn", "DMRG")) for k in (1, 2)]
    for n, r in cnn:
        t = r["tau"]
        ax.scatter([n], [t["de_out"]], marker="o", s=20, facecolor="white", edgecolor=CERT, lw=0.9, zorder=4)
        if t.get("de_in") and r["method"] == "DMRG":
            ax.plot([n, n], [t["de_out"], t["de_in"]], color=CERT, lw=0.9, zorder=3)
    fam = [(20, hrow(4, 1, "Ccent", "ED")), (30, hrow(6, 1, "Cfix", "DMRG")), (45, hrow(9, 1, "Cfix", "DMRG"))]
    ns = [n for n, _ in fam]
    vo = [r["tau"]["de_out"] for _, r in fam]
    ax.plot(ns, vo, color=WARM, lw=1.0, ls=(0, (3, 1.5)), zorder=3)
    for n, r in fam:
        t = r["tau"]
        ax.scatter([n], [t["de_out"]], marker="o", s=20, facecolor="white", edgecolor=WARM, lw=0.9, zorder=4)
        if r["method"] == "DMRG":
            ax.plot([n, n], [t["de_out"], t["de_in"]], color=WARM, lw=0.9, zorder=3)
    ax.plot([20, 140], [vo[0] / 1.35, vo[0] / 1.35 * 20 / 140], color=MUTE, lw=0.7, ls=":", zorder=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(15, 150)
    ax.set_ylim(6e-5, 0.2)
    ax.set_xticks([20, 30, 45, 57, 115])
    ax.set_xticklabels(["20", "30", "45", "57", "115"])
    ax.minorticks_off()
    ax.set_xlabel(r"system size $n$")
    ax.set_ylabel(r"certified up to an energy error per site $\delta e^*$")
    clean(ax)
    ax.text(16, 0.115, "averages: size-independent", color=SHORE, fontsize=7.2, ha="left", va="bottom")
    ax.text(16, 7.2e-5, r"single site or bond: $\propto 1/n$ (dotted guides)", color=WARM, fontsize=7.2, ha="left", va="bottom")
    ax.text(22, 7.4e-3, r"heavy-hex XXZ, $J_z=4$ (filled squares)", color=MUTE, fontsize=6.4, ha="left",
            va="bottom")
    ax.text(52, 0.045, "random Heisenberg\nbenchmark (open circles)", color=MUTE, fontsize=6.4, ha="left",
            va="center", linespacing=1.1)


# ----------------------------------------------------------------------------------------------- (c) learner
F_LI = os.path.join(C.ROOT, "phase3", "full_runs", "learning_ibm", "out", "results.json")
F_EMU = os.path.join(C.METH, "out_20261030T003230Z", "out", "%s", "%s_n57_J%.1f.json")


def learner(ax, axw):
    """Final-fix pass (2026-11-04): the realistic learning case on the 57-qubit heavy-hex model.
    m_s against Jz: DMRG truth, emulated first-stage labels (training range and the new labels at 1.1-1.4), the cubic
    model trained on the emulated labels with its standard conformal 90 % interval (q from learning_ibm results), and the
    energy interval of m_s at each label's own energy (map windows; grey = inner bound, not certified; teal =
    certified, width <= tau). Third-reading pass: wording only ('certified' reserved for width <= tau).  Right: coverage of new emulated labels (open) and of the truth (filled) by the standard intervals,
    per-site labels, cubic model (learning_ibm/out/results.json)."""
    f = F_LI if os.path.exists(F_LI) else F_LI.replace("results.json", "results_fast.json")   # fast file: layout tests only
    L = json.load(open(f, encoding="utf-8"))["sizes"]["57"]
    S = C.map_summary()
    rows = {(r["n"], round(r["Jz"], 1), r["label"]): r for r in S["rows"]}
    Js = L["couplings"]
    G = json.load(open(os.path.join(C.METH, "code", "graphs", "hh_d5.json"), encoding="utf-8"))
    eta = G["eta"]
    ms = lambda Z: sum(e * z for e, z in zip(eta, Z)) / len(eta)
    mt, ml = {}, {}
    for J in Js:
        e = json.load(open(F_EMU % ("emu", "emu", J), encoding="utf-8"))
        r = json.load(open(F_EMU % ("ref", "ref", J), encoding="utf-8"))
        mt[J], ml[J] = ms(r["labels"]["Z"]), ms(e["var"]["primary"]["labels"]["Z"])
    tr = L["train"]
    # cubic in 1/Jz, as ml2.fit_poly (linear in the labels, so fitting m_s equals deriving it from the site model)
    import numpy as np
    X = np.vander(1.0 / np.array(tr), 4)
    w = np.linalg.solve(X.T @ X + 1e-8 * np.eye(4), X.T @ np.array([ml[j] for j in tr]))
    jj = np.linspace(1.05, 6.05, 200)
    pred = np.vander(1.0 / jj, 4) @ w
    q = L["models"]["poly3_invJ"]["ood_emulated"]["rows"][0]["qM"]
    cert = L["certification"]
    for J in Js:
        r = rows.get((57, J, "m_s"))
        if r is None:
            continue
        e = cert[str(J)]["eps_emu"]
        st = sorted((r[k]["eps"], r[k]) for k in ("at_lo", "at_dig", "at_up"))
        if cert[str(J)]["m_s"]["certified"]:
            lo, hi = next(d for (ee, d) in st if ee >= e)["outer"]
            col, lw = CERT, 3.2
        else:
            lo, hi = [d for (ee, d) in st if ee <= e][-1]["inner"]
            # the window at the label's own energy contains this smaller window and the emulated label itself
            lo, hi = min(lo, ml[J]), max(hi, ml[J])
            col, lw = "#c9ccd0", 3.2
        ax.plot([J, J], [lo, hi], color=col, lw=lw, solid_capstyle="butt", zorder=1)
    # (no shading of the test range: the window bars there already fill it)
    ax.plot(Js, [mt[j] for j in Js], "-", color=INK, lw=0.9, zorder=3)
    ax.plot(Js, [mt[j] for j in Js], "o", color=INK, ms=2.2, zorder=3)
    ax.fill_between(jj, pred - q, pred + q, color=WARM, alpha=0.35, lw=0, zorder=2)
    ax.plot(jj, pred, "--", color=WARM, lw=0.8, zorder=2)
    ax.plot(tr, [ml[j] for j in tr], "o", color=WARM, ms=3.0, zorder=4)
    od = L["ood"]
    ax.plot(od, [ml[j] for j in od], "o", mfc="white", mec=WARM, mew=0.9, ms=3.4, zorder=4)
    ax.set_xlim(1.0, 6.2)
    ax.set_ylim(0.38, 1.02)
    ax.set_xlabel(r"coupling $J_z$")
    ax.set_ylabel(r"staggered magnetization $m_s$", labelpad=1)
    clean(ax)
    ax.text(1.25, 0.395, "test\nrange", ha="center", va="bottom", fontsize=6.2, color=MUTE, linespacing=1.0)
    ax.text(2.55, 0.425, "truth (DMRG)", color=INK, fontsize=6.4, ha="left", va="center")
    ax.text(3.3, 0.655, "emulated labels and\nmodel trained on them,\nwith its standard 90% interval",
            color=WARM, fontsize=6.2, ha="left", va="center", linespacing=1.05)
    ax.text(1.55, 0.47, "energy interval at the\nlabel's energy (inner\nbound): grey = wider\nthan $\\tau$, label dropped",
            color=MUTE, fontsize=6.0, ha="left", va="bottom", linespacing=1.05)
    ax.text(4.95, 0.885, "teal: certified,\nkept", color=SHORE, fontsize=6.0, ha="center", va="top",
            linespacing=1.05)
    # right: coverage of the standard intervals (per-site labels, cubic model)
    M = L["models"]["poly3_invJ"]
    ys = {"indist_emulated": 1.0, "ood_emulated": 0.0}
    for k, y in ys.items():
        s = M[k]["summary"]
        axw.plot([s["covZ_truth"], s["covZ_emu"]], [y, y], color="#c9c9c5", lw=0.8, zorder=1)
        axw.scatter([s["covZ_emu"]], [y], marker="o", s=24, facecolor="white", edgecolor=WARM, lw=1.1, zorder=3)
        axw.scatter([s["covZ_truth"]], [y], marker="o", s=24, color=WARM, lw=0, zorder=3)
    axw.axvline(0.9, color=MUTE, lw=0.7, ls="--", zorder=0)
    axw.set_xlim(-0.05, 1.05)
    axw.set_ylim(-0.6, 2.35)
    axw.set_yticks([1.0, 0.0])
    axw.set_yticklabels(["training\nrange", "test\nrange"], fontsize=6.4, linespacing=1.0)
    axw.tick_params(axis="y", length=0, pad=1)
    clean(axw)
    axw.set_xticks([0, 0.5, 0.9])
    axw.set_xticklabels(["0", "0.5", "0.9"])
    axw.set_xlabel("coverage of the\nstandard interval", linespacing=1.0, fontsize=7)
    axw.scatter([0.02], [2.15], marker="o", s=20, facecolor="white", edgecolor=WARM, lw=1.0)
    axw.text(0.10, 2.15, "new labels", color=WARM, fontsize=6.0, ha="left", va="center")
    axw.scatter([0.02], [1.75], marker="o", s=20, color=WARM, lw=0)
    axw.text(0.10, 1.75, "truth", color=WARM, fontsize=6.0, ha="left", va="center")


def main():
    rc()
    fig = plt.figure(figsize=(C.FULL_W, 3.95))
    gs = fig.add_gridspec(2, 3, height_ratios=[0.88, 2.55], width_ratios=[1.0, 0.86, 0.34], hspace=0.26,
                          wspace=0.10, left=0.07, right=0.985, top=0.95, bottom=0.11)
    axa = fig.add_subplot(gs[0, :])
    schematic(axa)
    axb = fig.add_subplot(gs[1, 0])
    law(axb)
    axc = fig.add_subplot(gs[1, 1])
    axw = fig.add_subplot(gs[1, 2])
    learner(axc, axw)
    pos = axc.get_position()
    axc.set_position([pos.x0 + 0.050, pos.y0, pos.width - 0.050, pos.height])
    pw = axw.get_position()
    axw.set_position([pw.x0 + 0.040, pw.y0, pw.width - 0.052, pw.height])
    fig.text(0.006, 0.985, "(a)", fontsize=9, va="top", ha="left", fontweight="bold")
    fig.text(0.045, 0.985, "the pipeline: energy turns each label into an interval", fontsize=7.8, va="top")
    yb = axb.get_position().y1 + 0.035
    fig.text(0.006, yb, "(b)", fontsize=9, va="top", ha="left", fontweight="bold")
    fig.text(0.045, yb, "the law against system size", fontsize=7.8, va="top")
    xc = axc.get_position().x0 - 0.062
    fig.text(xc, yb, "(c)", fontsize=9, va="top", ha="left", fontweight="bold")
    fig.text(xc + 0.035, yb, "learning from a realistic generator, 57 qubits", fontsize=7.8, va="top")
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(C.HERE, "fig1_overview." + ext), dpi=300)
    print("wrote fig1_overview.{pdf,png}")


if __name__ == "__main__":
    main()
