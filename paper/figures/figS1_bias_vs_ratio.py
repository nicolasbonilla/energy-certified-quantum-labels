"""Supplemental Fig. S1: signed m_s bias vs energy ratio for every emulated family at every (n, Jz) with a
perfect-sampler scan; the dataset's reported ratio (its Fig. 2, digitized) and the bias read there.

  python figS1_bias_vs_ratio.py
Source: phase3/full_runs/method/laptop_post/out/summary.json (families, bias_at_ibm_energy).
Adapted from phase3/full_runs/method/code/figs.py (its Fig. 3).
"""
import matplotlib
import matplotlib.ticker  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402


def main():
    C.style(plt)
    M = C.meth_summary()
    F = M["families"]
    keys = sorted([k for k, fam in F.items() if "gs_random" in fam],
                  key=lambda k: (int(k.split("_")[0]), float(k.split("_")[1])))
    fig, axs = plt.subplots(2, 4, figsize=(C.FULL_W, 3.6), gridspec_kw={"hspace": 0.5, "wspace": 0.35})
    slots = {57: 0, 115: 0}
    for key in keys:
        n = int(key.split("_")[0])
        ax = axs[0 if n == 57 else 1, slots[n]]
        slots[n] += 1
        fam = F[key]
        for fn, st, lab in (("gs_random", "o-", "perfect samples, RR"), ("gs_top", "^-", "top-D, RR"),
                            ("gs_projected", "x:", "support only"), ("kscan_ideal", "s-", "Krylov, no noise"),
                            ("kscan_floor", "d-", "Krylov, 1% flips")):
            if fn in fam:
                P = sorted(fam[fn], key=lambda p: p["ratio"])
                ax.plot([p["ratio"] for p in P], [p["dm_s"] for p in P], st, ms=2.5, lw=0.7, label=lab)
        first = True
        for fn, v in fam.items():
            if fn.startswith("pipeline_"):
                for p in v:
                    ax.plot(p["ratio"], p["dm_s"], "k*", ms=5, label="pipeline variants" if first else None)
                    first = False
        fb = True
        for fn, v in fam.items():
            if fn.startswith("bo_"):
                for p in v:
                    ax.plot(p["ratio"], p["dm_s_rot"], "mo", mfc="none", ms=4,
                            label="unstated rotation: physical state" if fb else None)
                    fb = False
        b = M["bias_at_ibm_energy"].get(key)
        if b:
            ax.axvline(b["ibm_ratio"], color="k", ls=":", lw=0.7)
            if b["dm_s"] is not None:
                ax.plot(b["ibm_ratio"], b["dm_s"], "kD", ms=4)
        ax.set_xscale("log")
        ax.axhline(0, color="k", lw=0.4)
        ax.set_title(r"$n=%s$, $J_z=%s$" % tuple(key.split("_")), fontsize=7.5)
        ax.tick_params(labelsize=6)
        # minor labels at 2 and 5 per decade only (the default labels overlapped on short ranges)
        ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(subs=(2.0, 5.0)))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: "%g" % v))
        ax.grid(True, color=C.GRID, lw=0.4)
    for r in range(2):
        for c in range(4):
            if (r == 0 and c >= slots[57]) or (r == 1 and c >= slots[115]):
                axs[r, c].axis("off")
    for ax in axs[:, 0]:
        ax.set_ylabel(r"$m_s-m_s^{\rm GS}$", fontsize=7)
    for ax in axs[1]:
        ax.set_xlabel(r"$(E-E_0)/(E_1-E_0)$", fontsize=7)
    h, l = axs[0, 0].get_legend_handles_labels()
    axs[1, 3].legend(h, l, frameon=False, fontsize=6, loc="center")
    C.save(fig, "figS1_bias_vs_ratio")


if __name__ == "__main__":
    main()
