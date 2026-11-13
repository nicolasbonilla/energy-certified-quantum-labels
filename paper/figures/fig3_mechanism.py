"""Figure 3: where the over-ordering of the emulated method class comes from.

  python fig3_mechanism.py

(a, b) Signed m_s bias vs subspace dimension D for perfect samples of the DMRG ground state (n = 57: Jz = 1.2, 1.6,
       2.5, 4.0; n = 115: Jz = 1.2, 1.6, 2.5):
         filled circles  = Rayleigh-Ritz in the sampled configurations (what the method does)      [families gs_random]
         crosses         = the ground state projected on the same configurations (support only)   [families gs_projected]
         open triangles  = multiplicity-weighted mean of the same samples (no diagonalization)    [gsscan nested sample_mean]
         stars           = full emulated pipeline at the published shot budget (primary variant)  [families pipeline_floor]
(c)    Signed m_s bias vs energy ratio r = (E - E0)/(E1 - E0) at n = 57 for every emulated family (perfect samples,
       most-probable-first subsets, Krylov shot scans, pipeline variants); vertical ticks = the dataset's reported r
       (its Fig. 2, digitized), diamonds = the bias read there (summary.json bias_at_ibm_energy).
Sources: phase3/full_runs/method/laptop_post/out/summary.json (families, bias_at_ibm_energy) and out/gsscan/*.json.
Adapted from phase3/full_runs/method/code/figs.py.
"""
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402

JCOL = {1.2: "#c0392b", 1.6: "#d68910", 2.5: "#2471a3", 4.0: "#1e8449"}


def main():
    C.style(plt)
    M = C.meth_summary()
    F = M["families"]
    gs = {}
    for p in glob.glob(os.path.join(C.METH, "laptop_post", "out", "gsscan", "gsscan_n*_J*.json")):
        g = C.rj(p)
        gs[(g["n"], round(g["Jz"], 1))] = g
    fig, axs = plt.subplots(1, 3, figsize=(C.FULL_W, 2.35), gridspec_kw={"wspace": 0.33})
    for ax, n in zip(axs[:2], (57, 115)):
        for key, fam in F.items():
            nn, j = key.split("_")
            nn, j = int(nn), float(j)
            if nn != n or j not in JCOL or "gs_random" not in fam:
                continue
            c = JCOL[j]
            P = sorted(fam["gs_random"], key=lambda p: p["D"])
            ax.plot([p["D"] for p in P], [p["dm_s"] for p in P], "o-", color=c, ms=3, lw=0.9, label=r"$J_z=%.1f$" % j)
            if "gs_projected" in fam:
                Q = sorted(fam["gs_projected"], key=lambda p: p["D"])
                ax.plot([p["D"] for p in Q], [p["dm_s"] for p in Q], "x:", color=c, ms=3.5, lw=0.7)
            g = gs.get((n, j))
            if g:
                ax.plot([r["D"] for r in g["nested"]], [r["sample_mean"]["dm_s"] for r in g["nested"]], "^",
                        mfc="white", mec=c, ms=3.2, mew=0.7)
            if "pipeline_floor" in fam:
                p = fam["pipeline_floor"][0]
                ax.plot(p["D"], p["dm_s"], "*", color=c, ms=8, mec="k", mew=0.4, zorder=5)
        ax.axhline(0, color=C.INK, lw=0.5)
        ax.set_xscale("log")
        ax.set_xlabel("subspace dimension $D$")
        ax.set_ylim(-0.02, 0.34)
        ax.set_title("(%s) $n=%d$, perfect samples" % ("ab"[n == 115], n), fontsize=8)
        ax.grid(True, color=C.GRID, lw=0.4)
    axs[0].set_ylabel(r"$m_s - m_s^{\rm GS}$")
    h, l = axs[0].get_legend_handles_labels()
    hx = [plt.Line2D([], [], color=C.MUTED, marker="o", lw=0.9, ms=3),
          plt.Line2D([], [], color=C.MUTED, marker="x", ls=":", lw=0.7, ms=3.5),
          plt.Line2D([], [], color=C.MUTED, marker="^", mfc="white", lw=0, ms=3.2),
          plt.Line2D([], [], color=C.MUTED, marker="*", mec="k", lw=0, ms=7)]
    lx = ["diagonalized (RR)", "support only", "sample mean", "full pipeline"]
    axs[0].legend(h, l, frameon=False, loc="upper left", fontsize=6, handlelength=1.0)
    axs[1].legend(hx, lx, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.36), fontsize=6, handlelength=1.4)

    ax = axs[2]
    n = 57
    for key, fam in F.items():
        nn, j = key.split("_")
        nn, j = int(nn), float(j)
        if nn != n or j not in (1.6, 2.5, 4.0):
            continue
        c = JCOL[j]
        for fn, st in (("gs_random", "o-"), ("gs_top", "^-"), ("kscan_ideal", "s-"), ("kscan_floor", "d-")):
            if fn in fam:
                P = sorted(fam[fn], key=lambda p: p["ratio"])
                ax.plot([p["ratio"] for p in P], [p["dm_s"] for p in P], st, color=c, ms=2.5, lw=0.7,
                        mfc=c if fn == "gs_random" else "white", label=(r"$J_z=%.1f$" % j) if fn == "gs_random" else None)
        for fn, v in fam.items():
            if fn.startswith("pipeline_"):
                for p in v:
                    ax.plot(p["ratio"], p["dm_s"], "*", color=c, ms=6, mec="k", mew=0.3)
        b = M["bias_at_ibm_energy"].get(key)
        if b and b["dm_s"] is not None:
            ax.axvline(b["ibm_ratio"], color=c, lw=0.6, ls=":")
            ax.plot(b["ibm_ratio"], b["dm_s"], "D", color="k", ms=4, zorder=6)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"energy ratio $(E-E_0)/(E_1-E_0)$")
    ax.set_title("(c) $n=57$: bias vs energy", fontsize=8)
    ax.legend(frameon=False, loc="lower right", fontsize=6, handlelength=1.2)
    ax.grid(True, which="major", color=C.GRID, lw=0.4)
    C.save(fig, "fig3_mechanism")


if __name__ == "__main__":
    main()
