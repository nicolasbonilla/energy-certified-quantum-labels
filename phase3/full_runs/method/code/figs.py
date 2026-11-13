"""Draft figures of the full method runs (laptop). Reads <root>/out/summary.json, emu/, ref/, ml/.

  python figs.py <root> <outdir>
"""
import glob
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

JSTAR = 3.3
COL = {"primary": "#c0392b", "ideal": "#2471a3", "dev_ps": "#7d3c98", "dev_rec": "#d68910", "pre": "#7f8c8d"}
JCOL = {1.2: "#c0392b", 1.6: "#d68910", 2.5: "#2471a3", 4.0: "#1e8449"}


def rj(p):
    with open(p) as f:
        return json.load(f)


def main(root, outdir):
    os.makedirs(outdir, exist_ok=True)
    O = os.path.join(root, "out")
    S = rj(os.path.join(O, "summary.json"))
    emu = {}
    for p in glob.glob(os.path.join(O, "emu", "emu_n*_J*.json")):
        r = rj(p); emu[(r["n"], round(r["Jz"], 1))] = r
    ref = {}
    for p in glob.glob(os.path.join(O, "ref", "ref_n*_J*.json")):
        r = rj(p); ref[(r["n"], round(r["Jz"], 1))] = r

    # ---------------- Fig. 1: bias vs Jz
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, n in zip(axs, (57, 115)):
        js = sorted(j for (m, j) in emu if m == n)
        for v in ("primary", "ideal", "dev_ps", "dev_rec", "pre"):
            pts = [(j, emu[(n, j)]["var"][v]["err"]["dm_s"]) for j in js if v in emu[(n, j)]["var"]]
            if pts:
                ax.plot(*zip(*pts), "o-" if v == "primary" else ".--", color=COL[v], label=v, ms=5 if v == "primary" else 4)
        for k, d in S.get("dZ_matched", {}).items():
            if d["n"] == n and d["Jz"] <= 1.6:
                ax.errorbar(d["Jz"], d["dm_s"], yerr=[[d["dm_s"] - d["dm_s_range"][0]], [d["dm_s_range"][1] - d["dm_s"]]],
                            fmt="s", color="k", mfc="white", ms=6, capsize=3,
                            label="estimate at IBM's ΔZ (Supp. Fig. 11)" if d["Jz"] == 1.2 else None)
        for k, d in S.get("bias_at_ibm_energy", {}).items():
            if d["n"] == n and d["dm_s"] is not None:
                ax.errorbar(d["Jz"], d["dm_s"], yerr=[[d["dm_s"] - d["band"][0]], [d["band"][1] - d["dm_s"]]], fmt="D",
                            color="k", ms=6, capsize=3, label="at IBM's reported energy" if d["Jz"] == 1.6 else None)
        ax.axvspan(1.0, 1.55, color="0.92", zorder=0)
        ax.axvline(JSTAR, color="0.4", ls=":", lw=1)
        ax.text(JSTAR + 0.05, 0.20, "J* (certified →)", fontsize=8, color="0.3")
        ax.axhline(0, color="k", lw=0.6)
        ax.set_xlabel("Jz"); ax.set_title("n = %d" % n)
        ax.set_xscale("log"); ax.set_xticks([1.2, 1.4, 1.6, 2, 2.5, 3, 4, 6]); ax.set_xticklabels(["1.2", "1.4", "1.6", "2", "2.5", "3", "4", "6"])
    axs[0].set_ylabel("Δm_s = m_s(label) − m_s(DMRG)")
    axs[0].legend(fontsize=7, loc="upper center")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "fig_bias_vs_Jz.png"), dpi=150); plt.close(fig)

    # ---------------- Fig. 2: mechanism (bias vs D and vs captured weight)
    F = S.get("families", {})
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    for col, n in enumerate((57, 115)):
        ax, ax2 = axs[0, col], axs[1, col]
        for key, fam in F.items():
            nn, j = key.split("_"); nn = int(nn); j = float(j)
            if nn != n or j not in JCOL:
                continue
            c = JCOL[j]
            if "gs_random" in fam:
                P = sorted(fam["gs_random"], key=lambda p: p["D"])
                ax.plot([p["D"] for p in P], [p["dm_s"] for p in P], "o-", color=c, label="Jz=%.1f RR (perfect samples)" % j)
                ax2.plot([1 - p["W"] for p in P], [p["dm_s"] for p in P], "o-", color=c, label="Jz=%.1f RR" % j)
            if "gs_projected" in fam:
                P = sorted(fam["gs_projected"], key=lambda p: p["D"])
                ax.plot([p["D"] for p in P], [p["dm_s"] for p in P], "x:", color=c)
                ax2.plot([1 - p["W"] for p in P], [p["dm_s"] for p in P], "x:", color=c)
            if "gs_top" in fam:
                P = sorted(fam["gs_top"], key=lambda p: p["D"])
                ax.plot([p["D"] for p in P], [p["dm_s"] for p in P], "^-", color=c, mfc="white", ms=5)
            for v, mk in (("pipeline_floor", "*"), ("pipeline_ideal", "P"), ("pipeline_dev_rec", "v"), ("pipeline_dev_ps", "<")):
                if v in fam:
                    p = fam[v][0]
                    ax.plot(p["D"], p["dm_s"], mk, color=c, ms=9, mec="k", mew=0.5)
        ax.set_xscale("log"); ax.set_xlabel("subspace size D"); ax.set_ylabel("Δm_s"); ax.set_title("n = %d" % n)
        ax.axhline(0, color="k", lw=0.6)
        ax2.set_xscale("log"); ax2.set_xlabel("missing ground-state weight 1 − W"); ax2.set_ylabel("Δm_s")
        ax2.axhline(0, color="k", lw=0.6)
        ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "fig_mechanism.png"), dpi=150); plt.close(fig)

    # ---------------- Fig. 3: bias vs energy ratio
    keys = sorted([k for k, fam in F.items() if "gs_random" in fam],
                  key=lambda k: (int(k.split("_")[0]), float(k.split("_")[1])))
    if keys:
        fig, axs = plt.subplots(2, 4, figsize=(15, 7))
        slots = {57: 0, 115: 0}
        for key in keys:
            n = int(key.split("_")[0])
            ax = axs[0 if n == 57 else 1, slots[n]]; slots[n] += 1
            fam = F[key]
            for fn, st, lab in (("gs_random", "o-", "perfect samples, RR"), ("gs_top", "^-", "top-D, RR"),
                                ("gs_projected", "x:", "perfect samples, support only"),
                                ("kscan_ideal", "s-", "Krylov ideal, shot scan"), ("kscan_floor", "d-", "Krylov 1 % flips, shot scan")):
                if fn in fam:
                    P = sorted(fam[fn], key=lambda p: p["ratio"])
                    ax.plot([p["ratio"] for p in P], [p["dm_s"] for p in P], st, ms=4, label=lab)
            first = True
            for fn, v in fam.items():
                if fn.startswith("pipeline_"):
                    for p in v:
                        ax.plot(p["ratio"], p["dm_s"], "k*", ms=8, label="method variants" if first else None); first = False
            fb = True
            for fn, v in fam.items():
                if fn.startswith("bo_"):
                    for p in v:
                        ax.plot(p["ratio"], p["dm_s"], "m*", ms=8, label="non-stated BO: labels of psi'" if fb else None)
                        ax.plot(p["ratio"], p["dm_s_rot"], "mo", mfc="none", ms=7, label="non-stated BO: physical state" if fb else None)
                        fb = False
            b = S.get("bias_at_ibm_energy", {}).get(key)
            if b:
                ax.axvline(b["ibm_ratio"], color="k", ls=":", lw=1)
                if b["dm_s"] is not None:
                    ax.plot(b["ibm_ratio"], b["dm_s"], "kD", ms=7, label="read at IBM's ratio")
            ax.set_xscale("log"); ax.set_xlabel("(E − E0)/(E1 − E0)")
            ax.set_title("n = %s, Jz = %s" % tuple(key.split("_")), fontsize=10)
            ax.axhline(0, color="k", lw=0.6)
            ax.set_ylabel("Δm_s")
        for r in range(2):
            for c in range(4):
                if (r == 0 and c >= slots[57]) or (r == 1 and c >= slots[115]):
                    axs[r, c].axis("off")
        axs[0, 0].legend(fontsize=6.5, loc="upper left")
        fig.tight_layout(); fig.savefig(os.path.join(outdir, "fig_bias_vs_ratio.png"), dpi=150); plt.close(fig)

    # ---------------- Fig. 4: learning
    mls = sorted(glob.glob(os.path.join(O, "ml", "ml_n*.json")), key=lambda p: int(os.path.basename(p)[4:-5]))
    if mls:
        fig, axs = plt.subplots(1, len(mls), figsize=(5.5 * len(mls), 4.2))
        axs = np.atleast_1d(axs)
        for ax, p in zip(axs, mls):
            m = rj(p); n = m["n"]
            js = sorted(j for (nn, j) in ref if nn == n)
            ax.plot(js, [ref[(n, j)]["labels"]["m_s"] for j in js], "k-", lw=2, label="DMRG")
            je = sorted(j for (nn, j) in emu if nn == n)
            ax.plot(je, [emu[(n, j)]["var"]["primary"]["labels"]["m_s"] for j in je], "o", color=COL["primary"],
                    label="method labels (primary)")
            for mname, st in (("ibm_arch1", "^"), ("poly3_invJ", "s"), ("null_nn", "x"), ("null_const", "+")):
                rows = m["models"][mname]["rows"]
                ax.plot([r["Jz"] for r in rows], [r["m_s_pred_labels"] for r in rows], st, ms=7, mfc="none",
                        label="%s, trained on labels" % mname)
            ax.axvspan(1.05, 1.45, color="0.9", zorder=0); ax.text(0.02, 0.03, "OOD test", fontsize=8, transform=ax.transAxes)
            ax.axvspan(1.05, JSTAR, color="#f5b7b1", alpha=0.25, zorder=0)
            ax.axvline(JSTAR, color="0.3", ls=":"); ax.text(0.30, 0.03, "abstain below J* = 3.3", fontsize=8, transform=ax.transAxes)
            ax.set_xlabel("Jz"); ax.set_ylabel("m_s"); ax.set_title("n = %d" % n); ax.legend(fontsize=6.5, loc="lower right")
        fig.tight_layout(); fig.savefig(os.path.join(outdir, "fig_learning.png"), dpi=150); plt.close(fig)
    print("figures in", outdir)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
