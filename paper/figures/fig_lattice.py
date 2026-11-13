"""Lattice portrait (SM): per-site staggered magnetization of the emulated method class at J_z = 1.2 (OOD point).

  python fig_lattice.py      -> figS_lattice.pdf / .png        (n = 57)
                                figS_lattice_n115.pdf / .png   (n = 115)

Panels, same colour scale (a change of <Z_i> towards the Neel pattern, eta_i = +1 on the majority colour):
  (a) what the emulated method class does:  eta_i (<Z_i>_emulated - <Z_i>_DMRG), primary variant at its own energy
      (method laptop_post/out/emu/emu_n*_J1.2.json labels.Z, ref/ref_n*_J1.2.json labels.Z);
  (b) what the energy allows:  eta_i (<Z_i>(phi+) - <Z_i>(phi-)) for the two m_s witnesses of the window at the lower
      energy E_lo of the map (OOD floor): the stored states and mixture weights of summary_map.json
      rows[n, 1.2, m_s].at_lo.comps, with per-site <Z_i> from the stored states (indep.Z_graph).
  The site average of (a) is the m_s bias and that of (b) the m_s width (both asserted in landscape_data.py).
Geometry: landscape_data.layout(n), the heavy-hex coupling map of rustworkx.heavy_hex_graph(d) (unit edges).
Rendering: the renderer of fig1_composite.py (PyVista off screen at 2x, ambient occlusion, three-point light);
colour bar and text by matplotlib (Computer Modern).
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import common as C  # noqa: E402
import fig1_composite as F  # noqa: E402
import landscape_data as L  # noqa: E402

J = 1.2
CMAP = F.CMAP


def figure(n, out):
    F.rc()
    a = L.site_overorder(n, J)
    b, ms, inner = L.site_freedom(n, J)
    vmax = np.ceil(max(a.max(), b.max()) * 10) / 10
    W = int(3.3 * F.DPI)
    imgs = [F.render_lattice(n, v, vmax, [], W, int(0.8 * W), os.path.join(C.HERE, "_render_%s_%s.png" % (out, t)))
            for v, t in ((a, "a"), (b, "b"))]
    h = max(i.shape[0] / i.shape[1] for i in imgs) * 3.25
    H = h + 1.25
    fig = plt.figure(figsize=(C.FULL_W, H))
    subs = (r"$\eta_i(\langle Z_i\rangle_{\rm emulated}-\langle Z_i\rangle_{\rm DMRG})$; site average %.3f (the $m_s$ "
            r"bias), smallest %.3f" % (a.mean(), a.min()),
            r"$\eta_i(\langle Z_i\rangle_{\phi_+}-\langle Z_i\rangle_{\phi_-})$ at $E_{\rm lo}$; site average %.3f "
            r"(the $m_s$ width), smallest %.3f" % (b.mean(), b.min()))
    for k, (img, letter, ttl, sub) in enumerate(zip(imgs, ("(a)", "(b)"),
                                                    ("what the emulated method does", "what the energy allows"),
                                                    subs)):
        x0 = 0.02 + k * 3.5
        ax = fig.add_axes([(x0 + 0.1) / C.FULL_W, 0.72 / H, 3.25 / C.FULL_W, h / H])
        ax.imshow(img)
        ax.axis("off")
        fig.text(x0 / C.FULL_W, 1 - 0.06 / H, letter, fontsize=9, va="top")
        fig.text((x0 + 0.27) / C.FULL_W, 1 - 0.06 / H, ttl, fontsize=8, va="top", color=F.INK)
        fig.text((x0 + 0.27) / C.FULL_W, 1 - 0.27 / H, sub, fontsize=6.6, va="top", color="#3d3d3d")
    F.colorbar(fig, [0.30, 0.30 / H, 0.40, 0.075 / H], vmax,
               r"change of $\langle Z_i\rangle$ towards the N$\acute{\rm e}$el pattern, $\eta_i\,\Delta\langle Z_i\rangle$")
    fig.text(0.99, 0.30 / H, r"$n=%d$, $J_z=%.1f$" % (n, J), ha="right", va="bottom", fontsize=7.5, color=F.INK)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(C.HERE, out + "." + ext), dpi=F.DPI)
    plt.close(fig)
    print("wrote %s: (a) mean %.4f min %.4f max %.4f; (b) mean %.4f min %.4f max %.4f; m_s witnesses %s, summary %s"
          % (out, a.mean(), a.min(), a.max(), b.mean(), b.min(), b.max(), ms, inner))


if __name__ == "__main__":
    figure(57, "figS_lattice")
    figure(115, "figS_lattice_n115")
