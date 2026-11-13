"""Main-text Fig. 2: the certification map and the emulated bias of the method's first stage.

  python fig1_map.py           (writes fig1_map.pdf / .png next to this file)

Top row (n = 57, 115): two-sided information-limit width of each label at the dataset's digitized energy (reading 1),
in units of tau = 0.06 |O_GS|; the vertical bar at each computed point runs from the inner (rigorous) width at E_lo to
the outer (DMRG-referenced) width at E_up. Below the line w/tau = 1 the window is at most tau wide ("certified"):
the dataset's label is then within tau (6 % of |O_GS|) of the ground-state value; only the window midpoint is
within tau/2.
Source: phase3/full_runs/map/laptop_analysis/summary_map.json (rows[*].at_dig.w_out, at_lo.w_in, at_up.w_out, tau).
Adapted from phase3/full_runs/map/code/plot_map2.py.

Bottom row: m_s window at the dataset's digitized energy, relative to the ground-state value (band = inner side,
thin lines = outer side; summary_map.json rows[label=m_s].at_dig.inner/outer, O_GS), with the signed m_s bias of the
emulated method class overlaid:
  open circles  = emulation at the published shot budget, at its own energy (emu_n*_J*.json var.primary.err.dm_s);
  filled diamonds = the emulated bias read at the dataset's reported energy ratio, an estimate (summary.json
                    bias_at_ibm_energy; n = 115 points are extrapolations beyond the sampled range, drawn hollow).
Track-2 revision (2026-10-31): the squares that converted the dataset paper's unsigned Delta Z with the sign of the
emulation (summary.json dZ_matched) were removed, so that no sign is attributed to the dataset's own labels; the
hand-set abstention line of the old learning test was removed too; end labels are spaced further apart.
Source: phase3/full_runs/method/laptop_post/out/.
"""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C

SHOW_ESTIMATES = False   # final-fix pass: no diamonds in the main-text map  # noqa: E402


def main():
    C.style(plt)
    S = C.map_summary()
    M = C.meth_summary()
    E = C.meth_emu()
    fig, axs = plt.subplots(2, 2, figsize=(C.FULL_W, 5.1), sharex=True,
                            gridspec_kw={"height_ratios": [1.15, 1.0], "hspace": 0.08, "wspace": 0.16})
    for col, n in enumerate((57, 115)):
        ax = axs[0, col]
        ax.axvspan(1.05, 1.5, color=C.OOD_SHADE, zorder=0, lw=0)
        ax.axhspan(0.08, 1.0, color=C.CERT_SHADE, zorder=0, lw=0)
        ax.axhline(1.0, color=C.INK, lw=0.8, zorder=1)
        ends = []
        for key, name, c, m, ls in C.LAB:
            pts = sorted((r["Jz"], r) for r in S["rows"] if r["n"] == n and r["label"] == key)
            if not pts:
                continue
            J = [p[0] for p in pts]
            y = [p[1]["at_dig"]["w_out"] / p[1]["tau"] for p in pts]
            lo = [max((p[1]["at_lo"]["w_in"] or 0) / p[1]["tau"], 1e-3) for p in pts]
            hi = [p[1]["at_up"]["w_out"] / p[1]["tau"] for p in pts]
            ax.plot(J, y, ls=ls if len(J) > 1 else "none", color=c, lw=1.2, marker=m, ms=3.2, zorder=3, label=name)
            ax.vlines(J, lo, hi, color=c, lw=0.7, alpha=0.6, zorder=2)
            if len(J) > 1:
                ends.append([math.log10(y[-1]), J[-1], name, c])
        ends.sort()
        for k in range(1, len(ends)):
            if ends[k][0] - ends[k - 1][0] < 0.15:
                ends[k][0] = ends[k - 1][0] + 0.15
        for ly, Je, name, c in ends:
            ax.text(Je + 0.07, 10 ** ly, name, color=c, fontsize=6.5, va="center")
        ax.set_yscale("log")
        ax.set_ylim(0.08, 80)
        ax.set_xlim(1.05, 6.75)
        ax.grid(True, which="major", color=C.GRID, lw=0.5)
        ax.set_title(r"(%s)  $n=%d$" % ("ab"[col], n), color=C.INK)
        ax.text(1.09, 0.105, "OOD\n(conditional)", fontsize=6, color=C.MUTED, va="bottom")
        ax.text(3.9, 0.15, "certified " + r"(width $\leq\tau$)", fontsize=6.3, color="#2f6b3c", ha="center",
                va="center")
        if col == 0:
            ax.set_ylabel(r"width / $\tau$ at the dataset energy")
        if n == 115:
            ax.text(4.05, 3.0, r"$Z_{\rm bulk}$", fontsize=6.5, color="#b07d00", va="center")

        ax = axs[1, col]
        ax.axvspan(1.05, 1.5, color=C.OOD_SHADE, zorder=0, lw=0)
        ax.axhline(0, color=C.INK, lw=0.6, zorder=1)
        rows = sorted((r["Jz"], r) for r in S["rows"] if r["n"] == n and r["label"] == "m_s")
        J = [p[0] for p in rows]
        g = [p[1]["O_GS"] for p in rows]
        il = [p[1]["at_dig"]["inner"][0] - gg for p, gg in zip(rows, g)]
        iu = [p[1]["at_dig"]["inner"][1] - gg for p, gg in zip(rows, g)]
        ol = [p[1]["at_dig"]["outer"][0] - gg for p, gg in zip(rows, g)]
        ou = [p[1]["at_dig"]["outer"][1] - gg for p, gg in zip(rows, g)]
        ax.fill_between(J, il, iu, color="#cfe0f4", lw=0, zorder=1, label="window of $m_s$")
        ax.plot(J, ol, color="#7aa6d8", lw=0.6, zorder=2)
        ax.plot(J, ou, color="#7aa6d8", lw=0.6, zorder=2)
        tau = [p[1]["tau"] / 2 for p in rows]
        ax.plot(J, tau, color=C.INK, lw=0.6, ls=":", zorder=2, label=r"$\pm\tau/2$")
        ax.plot(J, [-t for t in tau], color=C.INK, lw=0.6, ls=":", zorder=2)
        je = sorted(j for (m_, j) in E if m_ == n)
        ax.plot(je, [E[(n, j)]["var"]["primary"]["err"]["dm_s"] for j in je], "o", mfc="white", mec="#c0392b",
                ms=3.6, mew=0.9, zorder=4, label="emulation, own energy")
        first = True
        # final-fix pass (2026-11-04): the estimates at the dataset's energy moved to the Supplemental Material
        # (referee R2, M5.2); the main-text map no longer draws them.
        for k, d in (M["bias_at_ibm_energy"].items() if SHOW_ESTIMATES else []):
            if d["n"] == n and d["dm_s"] is not None:
                hollow = d["status"] == "extrapolated" and n == 115
                ax.plot(d["Jz"], d["dm_s"], "D", color="k", mfc="white" if hollow else "k", ms=3.8, zorder=6,
                        label="emulation read at reported energy" if first else None)
                first = False
        ax.set_ylim(-0.36, 0.40)
        ax.set_xlabel(r"$J_z$")
        ax.grid(True, which="major", color=C.GRID, lw=0.5)
        if col == 0:
            ax.set_ylabel(r"$m_s - m_s^{\rm GS}$")
            ax.legend(loc="upper right", frameon=True, framealpha=0.92, edgecolor="none", ncol=1, handlelength=1.2, borderaxespad=0.2, fontsize=6.3)
        ax.text(0.985, 0.03, "(%s)" % "cd"[col], transform=ax.transAxes, fontsize=8, ha="right", va="bottom")
    for ax in axs[1]:
        ax.set_xticks([1.2, 1.6, 2, 3, 4, 5, 6])
        ax.set_xticklabels(["1.2", "1.6", "2", "3", "4", "5", "6"])
    C.save(fig, "fig1_map")


if __name__ == "__main__":
    main()
