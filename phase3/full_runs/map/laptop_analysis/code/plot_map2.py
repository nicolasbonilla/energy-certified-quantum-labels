"""Draft main-text figure of the certification map (laptop only; matplotlib).

  python plot_map2.py <summary_map.json> <readings_declared.json> <out.png>
Top row (n = 57, n = 115): width of the two-sided information limit at the dataset's digitized energy (reading 1),
in units of tau = 0.06 |O_GS| (log scale; below 1 = certified to +-3 %), for the seven label families; the bar at
each computed point runs from the inner width at E_lo (rigorous witnesses) to the outer width at E_up (certificate
side). OOD window (Jz < 1.6) shaded: conditional on the 0.012-per-site floor. Bottom row: the energy error per site
at which each label stops being certifiable, delta e* = eps_tau(outer)/n, against IBM's digitized error per site
(reading 1 black, reading 2 grey) at the 45 training points; a label is certified where IBM's error lies below its
curve. Palette: the dataviz reference categorical slots 1-7 in fixed order (validated: all checks pass; the
contrast warning is relieved by direct labels, marker shapes, line styles and the table in RESULTS.md).
"""
import json
import math
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

LAB = [("m_s", "m$_s$", "#2a78d6", "o", "-"), ("Czz_bar", r"$\bar C_{zz}$", "#eb6834", "s", "-"),
       ("C2_bar", r"$\bar C_2$", "#1baf7a", "D", "-"), ("Z_bulk", "Z bulk", "#eda100", "v", "--"),
       ("Z_boundary", "Z boundary", "#e87ba4", "^", "--"), ("Czz_edge", "C$_{zz}$ edge", "#008300", "<", "--"),
       ("Z_loop", "Z loop", "#6250d6", ">", "--")]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def main(sp, rp, outp):
    S = json.load(open(sp))
    RD = json.load(open(rp))
    rows = [r for r in S["rows"] if r["n"] in (57, 115)]
    fig, axs = plt.subplots(2, 2, figsize=(11, 8.2), sharex=True)
    for col, n in enumerate((57, 115)):
        ax = axs[0, col]
        ax.axvspan(1.05, 1.55, color="#f0efec", zorder=0)
        ax.text(1.08, 0.13, "OOD\n(conditional)", fontsize=8, color=MUTED, va="bottom")
        ax.axhline(1.0, color=INK, lw=1.0, zorder=1)
        ax.text(6.05, 1.0, "±3 %", fontsize=8, color=INK, va="center")
        ends = []
        for key, name, c, m, ls in LAB:
            pts = sorted((r["Jz"], r) for r in rows if r["n"] == n and r["label"] == key)
            if not pts:
                continue
            J = [p[0] for p in pts]
            y = [p[1]["at_dig"]["w_out"] / p[1]["tau"] for p in pts]
            lo = [(p[1]["at_lo"]["w_in"] or 0) / p[1]["tau"] for p in pts]
            hi = [p[1]["at_up"]["w_out"] / p[1]["tau"] for p in pts]
            ax.plot(J, y, ls=ls, color=c, lw=2, marker=m, ms=5, label=name, zorder=3)
            ax.vlines(J, [max(a, 1e-3) for a in lo], hi, color=c, lw=1, alpha=0.6, zorder=2)
            ends.append([math.log10(y[-1]), J[-1], name])
        ends.sort()                                  # direct labels at the line ends, nudged apart in log space
        for k in range(1, len(ends)):
            if ends[k][0] - ends[k - 1][0] < 0.075:
                ends[k][0] = ends[k - 1][0] + 0.075
        for ly, Je, name in ends:
            ax.text(Je + 0.06, 10 ** ly, name, color=INK, fontsize=7.5, va="center")
        ax.set_yscale("log")
        ax.set_title("n = %d: width / (0.06 |O$_{GS}$|) at IBM's energy" % n, fontsize=10, color=INK)
        ax.grid(True, which="major", color=GRID, lw=0.6)
        ax.set_xlim(1.05, 6.6)
        ax.set_ylim(0.1, 60)
        if col == 0:
            ax.set_ylabel("w / τ  (below 1: certified)", color=INK)
        ax.tick_params(colors=MUTED)
        ax = axs[1, col]
        ax.axvspan(1.05, 1.55, color="#f0efec", zorder=0)
        for key, name, c, m, ls in LAB:
            pts = sorted((r["Jz"], r) for r in rows if r["n"] == n and r["label"] == key and r.get("de_star_out"))
            if pts:
                ax.plot([p[0] for p in pts], [p[1]["de_star_out"] for p in pts], ls=ls, color=c, lw=2, marker=m, ms=5,
                        label=name, zorder=3)
        Jt = [round(1.6 + 0.1 * k, 1) for k in range(45)]
        for rd, colr, lab in (("1", INK, "IBM (reading 1)"), ("2", "#9b9a95", "IBM (reading 2)")):
            xs, ys = [], []
            for J in Jt:
                e = RD["eps" + rd].get("%d_%.1f" % (n, J))
                if e:
                    xs.append(J); ys.append(e / n)
            ax.plot(xs, ys, color=colr, lw=1.2, marker=".", ms=4, label=lab, zorder=4)
        ax.set_yscale("log")
        ax.grid(True, which="major", color=GRID, lw=0.6)
        ax.set_xlabel("J$_z$", color=INK)
        if col == 0:
            ax.set_ylabel("energy error per site  δe", color=INK)
        ax.set_title("n = %d: δe*(O) (labels) vs IBM's δe" % n, fontsize=10, color=INK)
        ax.tick_params(colors=MUTED)
    h, l = axs[1, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(outp, dpi=160)
    print("wrote", outp)


if __name__ == "__main__":
    main(*sys.argv[1:])
