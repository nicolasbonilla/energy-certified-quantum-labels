"""Graphical abstract / table-of-contents image (not used in the PDFs).

  python fig_graphical_abstract.py   -> graphical_abstract.png (600 dpi) and .pdf

The two pictures are rendered here by the renderers of fig1_composite.py from the same deposited data as Fig. 1:
the relief of the m_s window width over (J_z, delta e) at n = 57 (map run, stored states) and the per-site excess of
order of our own device data at J_z = 1.2 (phase3/full_runs/qpu/out_*/device_A_J1.2.json).  Only the short labels
are added here.
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402
import fig1_composite as F  # noqa: E402


def main():
    F.rc()
    D = F.relief_data()
    imgA, mk, _ = F.render_relief(D, int(3.9 * F.DPI), int(2.6 * F.DPI), os.path.join(C.HERE, "_render_ga_a.png"))
    vals, moved = F.device_values()
    imgB = F.render_lattice(F.N, vals["device"][0], 0.5, moved, int(2.7 * F.DPI), int(0.8 * 2.7 * F.DPI),
                            os.path.join(C.HERE, "_render_ga_b.png"))
    W, H = 7.0, 3.4
    fig = plt.figure(figsize=(W, H))
    fig.text(0.012, 0.965, "What a sample's energy certifies in quantum-generated training data", fontsize=12,
             color=F.INK, va="top")
    ax1 = fig.add_axes([0.0, 0.0, 3.9 / W, 2.6 / H])
    ax1.imshow(imgA)
    ax1.set_xlim(0, imgA.shape[1])
    ax1.set_ylim(imgA.shape[0], 0)
    ax1.axis("off")
    ax1.text(*mk["cert"][0], "certified", color="white", fontsize=9, ha="center", va="center")
    ax1.text(mk["path"][0][0] + 40, mk["path"][0][1], "the data", color=F.INK, fontsize=8, ha="left", va="center")
    fig.text(0.02, (0.62 + 1.80 + 0.06) / H, "where the energy pins a label (teal), and where it does not", fontsize=8, color="#444444",
             va="bottom")
    hb = 1.80
    wb = hb * imgB.shape[1] / imgB.shape[0]
    ax2 = fig.add_axes([(W - wb - 0.15) / W, 0.62 / H, wb / W, hb / H])
    ax2.imshow(imgB)
    ax2.axis("off")
    fig.text((W - wb - 0.15) / W, (0.62 + hb + 0.06) / H, "the method inside the open window:\nevery site more ordered (our device data)",
             fontsize=8, color="#444444", va="bottom")
    F.colorbar(fig, [(W - wb + 0.2) / W, 0.36 / H, (wb - 0.7) / W, 0.06 / H], 0.5,
               r"excess of order per site, $\eta_i\,\Delta\langle Z_i\rangle$")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(C.HERE, "graphical_abstract." + ext), dpi=F.DPI)
    plt.close(fig)
    print("wrote graphical_abstract.{png,pdf}")


if __name__ == "__main__":
    main()
