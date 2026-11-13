"""Figure 2: the rule of what energy certifies, from exact toy checks to the 57/115-qubit dataset.

  python fig2_rule.py

(a) Theorem 2 (averages): exact two-sided width of the staggered magnetization of the comb ferrimagnet (extensively
    pinned sector) vs the energy error per site, n = 6, 9, 12, with the sqrt law 2 sqrt(2 chi0 de); points with the
    window above the gap (eps/Delta > 1) are ringed.  Source: paper/data/r3gen/out/t3_comb.txt (exact diagonalization,
    copied from the session's r3gen scratchpad; script paper/data/r3gen/scripts/t3_avg.py).
(b) Theorem 1 (local labels): exact width of Z_0 in the transverse-field Ising chain (h = 1.5) at fixed energy error
    per site vs n; the full range is 2.  Source: paper/data/r3gen/out/t2_local.txt, block (iv).
(c) The design rule at scale: delta e*_law / delta e* (computed, certificate side) for every averaged and local row of
    the map with Jz >= 1.6; the declared band [0.8, 1.25] is shaded.  Source: summary_map.json rows[*].law_ratio_out.
(d) Size dependence of delta e*: delta e*(115) / delta e*(57) for the three averages at every Jz >= 2.0, and Z_bulk at
    Jz = 4.0; lines at 1 (intensive) and 57/115 (1/n).  Source: summary_map.json claims["C-E"].rows.
"""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402


def parse_t3(path):
    rows = []
    pat = re.compile(r"n=\s*(\d+)\s+\S+\s+de=([0-9.e+-]+)\s+eps/gap=\s*([0-9.]+)\s*\|\s*exact w=([0-9.]+).*?"
                     r"2sqrt\(2chi0 de\)=([0-9.]+)")
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = pat.search(line)
            if m:
                rows.append(dict(n=int(m.group(1)), de=float(m.group(2)), eg=float(m.group(3)),
                                 w=float(m.group(4)), law=float(m.group(5))))
    return rows


def parse_t2_iv(path):
    out = {}
    txt = open(path, encoding="utf-8").read()
    blk = txt.split("== (iv)")[1].split("==")[1] if "== (iv)" in txt else ""
    blk = txt.split("== (iv)")[1]
    for line in blk.splitlines()[1:]:
        m = re.match(r"de=([0-9.]+):(.*)", line.strip())
        if not m:
            if line.startswith("=="):
                break
            continue
        de = float(m.group(1))
        pts = re.findall(r"n=(\d+): w=([0-9.]+)", m.group(2))
        out[de] = [(int(a), float(b)) for a, b in pts]
    return out


def main():
    C.style(plt)
    S = C.map_summary()
    fig, axs = plt.subplots(1, 4, figsize=(C.FULL_W, 2.05), gridspec_kw={"wspace": 0.62})

    ax = axs[0]
    rows = parse_t3(os.path.join(C.R3, "t3_comb.txt"))
    cols = {6: "#9ecae1", 9: "#4292c6", 12: "#08306b"}
    for n in (6, 9, 12):
        R = sorted((r for r in rows if r["n"] == n), key=lambda r: r["de"])
        ax.plot([r["de"] for r in R], [r["w"] for r in R], "o-", color=cols[n], ms=2.8, lw=0.9, label="$n=%d$" % n)
        hi = [r for r in R if r["eg"] > 1.0]
        ax.plot([r["de"] for r in hi], [r["w"] for r in hi], "o", mfc="none", mec="#c0392b", ms=6, mew=0.8)
    R = sorted((r for r in rows if r["n"] == 12), key=lambda r: r["de"])
    ax.plot([r["de"] for r in R], [r["law"] for r in R], ":", color=C.INK, lw=0.9, label=r"$2\sqrt{2\chi\,\delta e}$")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$\delta e$ (per site)"); ax.set_ylabel(r"width of $\bar O$")
    ax.legend(frameon=False, loc="upper left", handlelength=1.2)
    ax.text(0.97, 0.05, r"ringed: $\epsilon>\Delta$", transform=ax.transAxes, ha="right", fontsize=6, color="#c0392b")
    ax.set_title("(a) average, exact", fontsize=8)

    ax = axs[1]
    D = parse_t2_iv(os.path.join(C.R3, "t2_local.txt"))
    for de, c in zip(sorted(D), ("#fdae6b", "#e6550d", "#7f2704")):
        ax.plot([p[0] for p in D[de]], [p[1] for p in D[de]], "s-", color=c, ms=2.8, lw=0.9, label=r"$\delta e=%g$" % de)
    ax.axhline(2.0, color=C.INK, lw=0.6, ls=":")
    ax.text(6.1, 2.03, "full range", fontsize=6, color=C.MUTED, va="bottom")
    ax.set_xlabel("$n$"); ax.set_ylabel(r"width of $Z_0$")
    ax.set_ylim(1.35, 2.15)
    ax.set_xticks([6, 8, 10, 12])
    ax.legend(frameon=False, loc="lower right", handlelength=1.2)
    ax.set_title("(b) local, exact", fontsize=8)

    ax = axs[2]
    ax.axhspan(0.8, 1.25, color=C.CERT_SHADE, lw=0, zorder=0)
    for key, name, c, m, ls in C.LAB:
        for n, fill in ((57, True), (115, False)):
            P = sorted((r["Jz"], r["law_ratio_out"]) for r in S["rows"]
                       if r["n"] == n and r["label"] == key and r["Jz"] >= 1.6 and r.get("law_ratio_out"))
            if P:
                ax.plot([p[0] for p in P], [p[1] for p in P], m, color=c, mfc=c if fill else "white", ms=2.8, mew=0.7,
                        lw=0, label=name if n == 57 else None)
    ax.axhline(1.0, color=C.INK, lw=0.5)
    ax.set_ylim(0.7, 1.9)
    ax.set_xlim(1.3, 6.4)
    ax.set_xlabel(r"$J_z$"); ax.set_ylabel(r"$\delta e^*_{\rm law}/\delta e^*$")
    ax.legend(frameon=False, loc="upper left", ncol=2, handlelength=0.8, columnspacing=0.6, fontsize=5.8)
    ax.set_title("(c) rule at 57/115 qubits", fontsize=8)

    ax = axs[3]
    CE = S["claims"]["C-E"]["rows"]
    for key, name, c, m, ls in C.LAB:
        P = sorted((r["Jz"], r["ratio"]) for r in CE if r["label"] == key)
        if P:
            ax.plot([p[0] for p in P], [p[1] for p in P], m + ("-" if len(P) > 1 else ""), color=c, ms=3, lw=0.8,
                    label=name)
    ax.axhline(1.0, color=C.INK, lw=0.5)
    ax.axhline(57 / 115, color=C.INK, lw=0.5, ls=":")
    ax.text(2.0, 57 / 115 + 0.03, "57/115", fontsize=6, color=C.MUTED)
    ax.set_ylim(0.35, 1.35)
    ax.set_xlabel(r"$J_z$"); ax.set_ylabel(r"$\delta e^*(115)/\delta e^*(57)$")
    ax.legend(frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.43), handlelength=1.0, fontsize=5.8)
    ax.set_title("(d) size dependence", fontsize=8)
    for a in axs:
        a.grid(True, which="major", color=C.GRID, lw=0.4)
    C.save(fig, "fig2_rule")


if __name__ == "__main__":
    main()
