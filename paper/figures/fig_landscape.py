"""Certification landscape (3-D): what the energy allows for the staggered magnetization, over (J_z, delta e).

  python fig_landscape.py            -> figS_landscape_n57.pdf / .png     (n = 57; SM, the full version of Fig. 1a)
                                        figS_landscape_n115.pdf / .png    (n = 115)

Every value drawn is read from the deposited outputs through landscape_data.py:
  surfaces  m_s^+(J_z, de) - m_s,GS (top) and m_s^-(J_z, de) - m_s,GS (bottom): the inner (rigorous) edges of the energy
            window, i.e. the hull of the stored sector states of the map run at each computed J_z (identical to
            summary_map.json at the three stored window energies of every row); straight between computed J_z (thin
            lines mark the computed J_z);
  green     de <= de*(J_z): below the certification threshold, where the (DMRG-referenced) outer width equals
            tau = 0.06 |m_s,GS| (summary_map.json rows[*].eps_tau_out / n), log-linear between computed J_z, as for J*;
  black     the window at the dataset's digitized energy error de_dig(J_z) (rows[*].eps.dig / n): one bar per
            computed J_z between the two surfaces;
  floor     the threshold and the dataset's curve projected on the (J_z, de) plane (the 2-D map);
  markers   emulated method-class states at their own energy (method emu_n*_J*.json, primary variant), and the bias
            estimated at the dataset's energy from its published unsigned Delta Z, with the sign assumed from the
            emulation (method summary.json dZ_matched).  Track-2 revision: these estimates appear only here, in
            the Supplemental Material, labelled as such; they were removed from main-text Fig. 2.
The de range stops at the largest stored energy common to all computed J_z, so the surfaces are data everywhere.
Rendering: PyVista (VTK) off screen; axes and text are vector graphics drawn by matplotlib at projected positions.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

import common as C  # noqa: E402
import landscape_data as L  # noqa: E402

os.environ.setdefault("PYVISTA_OFF_SCREEN", "true")
import pyvista as pv  # noqa: E402
import vtk  # noqa: E402

NDE = 150
J_MIN, J_MAX = 1.1, 6.0
SX, SY, SZ = 1.8, 0.95, 1.35            # scene box for J_z, log10 de, m_s - m_s,GS
NEUTRAL, NEUTRAL_LO, CERT = "#9db6d8", "#d5d9e0", "#25a274"
INKC, EMU_C, EST_C = "#0b0b0b", "#e0622e", "#5b4bd0"
W_PX, H_PX = 4200, 2750
PADL, PADB, PADT = 380, 130, 250                  # white margin (px) left and below the render, for the axis labels
CAM = [(-1.25, -3.00, 3.05), (0.95, 0.45, 0.45), (0, 0, 1)]


class Box:
    def __init__(self, de_min, de_max, z_min, z_max):
        self.lmin, self.lmax = np.log10(de_min), np.log10(de_max)
        self.de_min, self.de_max, self.z_min, self.z_max = de_min, de_max, z_min, z_max

    def X(self, J):
        return (np.asarray(J, float) - J_MIN) / (J_MAX - J_MIN) * SX

    def Y(self, de):                    # large de in front (y = 0), small de at the back (y = SY)
        return (self.lmax - np.log10(de)) / (self.lmax - self.lmin) * SY

    def Z(self, z):
        return (np.asarray(z, float) - self.z_min) / (self.z_max - self.z_min) * SZ


def data(n):
    rows = [r for r in L.rows(n) if not (n == 57 and r["Jz"] in (3.2, 3.4))]   # 3.2/3.4: short extra chains (J*)
    Js = np.array([r["Jz"] for r in rows])
    emax = min((L.pool(n, J)[0].max() - L.thr(n, J)["E0"]) / n for J in Js)
    de_max = np.floor(emax * 1000) / 1000              # rounded down: every surface point is data
    de = np.logspace(-4, np.log10(de_max), NDE)
    up, lo, ok = L.landscape(n, Js, de)
    assert ok.all()
    wlo, wup = [], []
    for r in rows:
        E, o = L.pool(n, r["Jz"])
        t = L.thr(n, r["Jz"])
        a, b = L.inner(E, o, [t["E0"] + r["eps"]["dig"]])
        wlo.append(a[0] - t["m_s_GS"])
        wup.append(b[0] - t["m_s_GS"])
    zl = np.floor(min(lo.min(), 0) * 10) / 10
    zh = np.ceil(max(up.max(), 0) * 10) / 10
    return dict(n=n, Js=Js, de=de, up=up, lo=lo, rows=rows, box=Box(1e-4, de_max, zl, zh),
                des=np.array([r["eps_tau_out"] / n for r in rows]), dig=np.array([r["eps"]["dig"] / n for r in rows]),
                wlo=np.array(wlo), wup=np.array(wup))


def thresh_at(D, J):
    """de*(J): log-linear interpolation between computed J_z (the rule used for J* in the map analysis)"""
    return 10 ** np.interp(J, D["Js"], np.log10(D["des"]))


def refine(D, V, k=10):
    Js = D["Js"]
    Jf = np.concatenate([np.linspace(Js[i], Js[i + 1], k, endpoint=False) for i in range(len(Js) - 1)] + [[Js[-1]]])
    idx = np.clip(np.searchsorted(Js, Jf, side="right") - 1, 0, len(Js) - 2)
    t = (Jf - Js[idx]) / (Js[idx + 1] - Js[idx])
    return Jf, (1 - t)[:, None] * V[idx] + t[:, None] * V[idx + 1]


def surface(D, key):
    B = D["box"]
    Jf, Vf = refine(D, D[key])
    g = pv.StructuredGrid(*np.meshgrid(B.X(Jf), B.Y(D["de"]), np.zeros(1), indexing="ij"))
    P = np.zeros((len(Jf), len(D["de"]), 3))
    P[..., 0] = B.X(Jf)[:, None]
    P[..., 1] = B.Y(D["de"])[None, :]
    P[..., 2] = B.Z(Vf)
    g.points = P.reshape(-1, 3, order="F") if False else np.stack([P[..., 0].ravel(order="F"),
                                                                   P[..., 1].ravel(order="F"),
                                                                   P[..., 2].ravel(order="F")], axis=1)
    cert = (D["de"][None, :] <= thresh_at(D, Jf)[:, None]).astype(float)
    g.point_data["cert"] = cert.ravel(order="F")
    return g.extract_surface().compute_normals(auto_orient_normals=False, consistent_normals=True)


def line(P):
    return pv.lines_from_points(np.asarray(P, float))


def render(D, png):
    B = D["box"]
    p = pv.Plotter(off_screen=True, window_size=(W_PX, H_PX), lighting="none")
    p.set_background("white")
    p.add_light(pv.Light(position=(-1.2, -2.2, 4.5), focal_point=(0.9, 0.5, 0.4), intensity=0.70))
    p.add_light(pv.Light(position=(3.5, -0.5, 2.0), focal_point=(0.9, 0.5, 0.4), intensity=0.30))
    p.add_light(pv.Light(light_type="headlight", intensity=0.30))
    z0 = 0.0
    # floor and the 2-D map on it
    p.add_mesh(pv.Plane(center=(SX / 2, SY / 2, z0 - 0.003), direction=(0, 0, 1), i_size=SX, j_size=SY),
               color="#f3f2ee", ambient=1.0, diffuse=0.0, specular=0.0)
    Jf = np.linspace(D["Js"][0], D["Js"][-1], 500)
    tf = np.clip(thresh_at(D, Jf), B.de_min, B.de_max)
    poly = [(B.X(J), B.Y(B.de_min), z0) for J in Jf[::-1]] + [(B.X(J), B.Y(t), z0) for J, t in zip(Jf, tf)]
    region = pv.PolyData(np.array(poly), faces=np.r_[len(poly), np.arange(len(poly))]).triangulate()
    p.add_mesh(region, color="#d3ecdf", ambient=1.0, diffuse=0.0, specular=0.0)
    for J in D["Js"]:
        p.add_mesh(line([(B.X(J), 0, z0 + 0.001), (B.X(J), SY, z0 + 0.001)]), color="#e2e1db", line_width=3)
    for k in (-3, -2):
        p.add_mesh(line([(0, B.Y(10.0 ** k), z0 + 0.001), (SX, B.Y(10.0 ** k), z0 + 0.001)]), color="#e2e1db",
                   line_width=3)
    p.add_mesh(line([(B.X(J), B.Y(t), z0 + 0.002) for J, t in zip(Jf, tf)]).tube(radius=0.0042), color=CERT,
               ambient=0.7, diffuse=0.3)
    p.add_mesh(line([(B.X(J), B.Y(e), z0 + 0.003) for J, e in zip(D["Js"], D["dig"])]).tube(radius=0.0042),
               color="#3a3a3a", ambient=0.7, diffuse=0.3)
    # surfaces: lower almost opaque, upper translucent
    cm_lo = matplotlib.colors.ListedColormap([NEUTRAL_LO, CERT])
    cm_up = matplotlib.colors.ListedColormap([NEUTRAL, CERT])
    p.add_mesh(surface(D, "lo"), scalars="cert", cmap=cm_lo, clim=(0, 1), show_scalar_bar=False,
               smooth_shading=True, opacity=0.96, ambient=0.40, diffuse=0.65, specular=0.15, specular_power=25)
    p.add_mesh(surface(D, "up"), scalars="cert", cmap=cm_up, clim=(0, 1), show_scalar_bar=False,
               smooth_shading=True, opacity=0.50, ambient=0.38, diffuse=0.65, specular=0.35, specular_power=40)
    # certification boundary on both surfaces (de = de*(J_z)): a dark green line, readable in greyscale
    Jb = np.linspace(D["Js"][0], D["Js"][-1], 400)
    for key in ("lo", "up"):
        Jf, Vf = refine(D, D[key], k=40)
        tb = thresh_at(D, Jf)
        okb = (tb >= B.de_min) & (tb <= B.de_max)
        zb = np.array([np.interp(np.log10(t), np.log10(D["de"]), v) for t, v in zip(tb, Vf)])
        P = [(B.X(J), B.Y(t), B.Z(z)) for J, t, z, o in zip(Jf, tb, zb, okb) if o]
        p.add_mesh(line(P).tube(radius=0.0045), color="#145e43", smooth_shading=True)
    # computed J_z on both surfaces
    for i, J in enumerate(D["Js"]):
        for key in ("lo", "up"):
            p.add_mesh(line([(B.X(J), B.Y(e), B.Z(z)) for e, z in zip(D["de"], D[key][i])]), color="#51627a",
                       line_width=2.5, opacity=0.6)
    # ground state: the back edge, where the window closes
    p.add_mesh(line([(0, SY, B.Z(0)), (SX, SY, B.Z(0))]).tube(radius=0.0045), color=INKC)
    # window at the dataset's energy: a filled vertical ribbon between the two surfaces, bars at computed J_z
    top = np.array([(B.X(J), B.Y(e), B.Z(z)) for J, e, z in zip(D["Js"], D["dig"], D["wup"])])
    bot = np.array([(B.X(J), B.Y(e), B.Z(z)) for J, e, z in zip(D["Js"], D["dig"], D["wlo"])])
    k = len(top)
    faces = np.hstack([[4, i, i + 1, k + i + 1, k + i] for i in range(k - 1)])
    p.add_mesh(pv.PolyData(np.vstack([top, bot]), faces), color="#2b3442", opacity=0.55, ambient=0.6, diffuse=0.4,
               specular=0.0)
    for J, e, a, b in zip(D["Js"], D["dig"], D["wlo"], D["wup"]):
        if B.de_min <= e <= B.de_max:
            p.add_mesh(line([(B.X(J), B.Y(e), B.Z(a)), (B.X(J), B.Y(e), B.Z(b))]).tube(radius=0.0035),
                       color=INKC, smooth_shading=True)
    for v in (D["wlo"], D["wup"]):
        p.add_mesh(line([(B.X(J), B.Y(e), B.Z(z)) for J, e, z in zip(D["Js"], D["dig"], v)]).tube(radius=0.0040),
                   color=INKC)
    # markers
    nemu = 0
    for J, de, dm in L.emu_states(D["n"]):
        if B.de_min <= de <= B.de_max and J_MIN <= J <= J_MAX:
            p.add_mesh(pv.Sphere(radius=0.019, center=(B.X(J), B.Y(de), B.Z(dm)), theta_resolution=48,
                                 phi_resolution=48), color=EMU_C, smooth_shading=True, ambient=0.35, diffuse=0.7,
                       specular=0.5, specular_power=40)
            nemu += 1
    digJ = dict(zip(D["Js"], D["dig"]))
    for J, dm in L.dz_matched(D["n"]):
        if J in digJ:
            c = pv.Octahedron(center=(B.X(J), B.Y(digJ[J]), B.Z(dm)), radius=0.024)
            p.add_mesh(c, color=EST_C, ambient=0.35, diffuse=0.7, specular=0.4)
    p.enable_depth_peeling(number_of_peels=16)
    p.enable_anti_aliasing("ssaa")
    p.camera_position = CAM
    p.camera.view_angle = 22.5
    img = p.screenshot(png, return_img=True)
    ren = p.renderer
    co = vtk.vtkCoordinate()
    co.SetCoordinateSystemToWorld()

    def proj(P):
        out = []
        for q in np.atleast_2d(P):
            co.SetValue(*map(float, q))
            x, y = co.GetComputedDoubleDisplayValue(ren)
            out.append((x, H_PX - y))
        return np.array(out)
    proj([(0, 0, 0)])
    pts = {k: proj(v) for k, v in dict(
        jx=[(B.X(J), 0, 0) for J in (1.2, 2, 3, 4, 5, 6)], jx2=[(B.X(J), -0.03, 0) for J in (1.2, 2, 3, 4, 5, 6)],
        dy=[(0, B.Y(10.0 ** k), 0) for k in (-4, -3, -2)], dy2=[(-0.035, B.Y(10.0 ** k), 0) for k in (-4, -3, -2)],
        zz=[(SX + 0.05, -0.05, B.Z(z)) for z in ZT(B)], zz2=[(SX + 0.085, -0.05, B.Z(z)) for z in ZT(B)],
        jend=[(0, 0, 0), (SX, 0, 0)], dend=[(0, 0, 0), (0, SY, 0)],
        zend=[(SX + 0.05, -0.05, B.Z(ZT(B)[0])), (SX + 0.05, -0.05, B.Z(ZT(B)[-1]))],
        jlab=[(SX * 0.55, -0.2, 0)], dlab=[(-0.22, SY * 0.55, 0)], zlab=[(SX + 0.05, -0.05, B.Z(ZT(B)[-1]) + 0.09)],
        gs=[(B.X(2.6), SY, B.Z(0))], cur=[(B.X(D["Js"][4]), B.Y(D["dig"][4]), B.Z(0.5 * (D["wup"][4] + D["wlo"][4])))],
        thr=[(B.X(4.6), B.Y(thresh_at(D, 4.6)), 0)], dset=[(B.X(5.5), B.Y(D["dig"][-2]), 0)],
        cert=[(B.X(5.0), B.Y(1.5e-4), B.Z(D["up"][-3, 3]))]).items()}
    p.close()
    return img, pts, nemu


def ZT(B):
    return [z for z in np.arange(-0.8, 0.81, 0.2) if B.z_min - 1e-9 <= z <= B.z_max + 1e-9]


def compose(D, img, P, out, tag):
    B = D["box"]
    import fig1_composite as F1
    F1.rc()
    fig = plt.figure(figsize=(C.FULL_W, C.FULL_W * (H_PX + PADB + PADT) / (W_PX + PADL)))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, interpolation="lanczos")
    ax.set_xlim(-PADL, W_PX)
    ax.set_ylim(H_PX + PADB, -PADT)
    ax.axis("off")
    tick = dict(color="#3d3d3a", fontsize=7)
    lab = dict(color=C.INK, fontsize=8)
    for (a, b) in (P["jend"], P["dend"], P["zend"]):
        pass
    ax.plot(*P["jend"].T, color=C.MUTED, lw=0.6)
    ax.plot(*P["dend"].T, color=C.MUTED, lw=0.6)
    ax.plot(*P["zend"].T, color=C.MUTED, lw=0.6)
    for q, q2, J in zip(P["jx"], P["jx2"], (1.2, 2, 3, 4, 5, 6)):
        ax.plot([q[0], q2[0]], [q[1], q2[1]], color=C.MUTED, lw=0.6)
        ax.text(q2[0], q2[1] + 22, "%g" % J, ha="center", va="top", **tick)
    for q, q2, k in zip(P["dy"], P["dy2"], (-4, -3, -2)):
        ax.plot([q[0], q2[0]], [q[1], q2[1]], color=C.MUTED, lw=0.6)
        ax.text(q2[0] - 20, q2[1], r"$10^{%d}$" % k, ha="right", va="center", **tick)
    for q, q2, z in zip(P["zz"], P["zz2"], ZT(B)):
        ax.plot([q[0], q2[0]], [q[1], q2[1]], color=C.MUTED, lw=0.6)
        ax.text(q2[0] + 18, q2[1], (r"$%+.1f$" % z) if abs(z) > 1e-9 else "$0$", ha="left", va="center", **tick)
    ax.text(*P["jlab"][0], r"coupling $J_z$", ha="center", va="top", **lab)
    ax.text(*P["dlab"][0], "energy error\nper site " + r"$\delta e$", ha="right", va="center", **lab)
    ax.text(*P["zlab"][0], r"$m_s - m_s^{\rm GS}$", ha="center", va="bottom", **lab)
    ann = dict(fontsize=6.8, va="center")

    def note(q, s, dx, dy, color=C.INK, ha="left"):
        ax.annotate(s, xy=q, xytext=(q[0] + dx, q[1] + dy), color=color, ha=ha, **ann,
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.5, shrinkA=1, shrinkB=1))
    note(P["gs"][0], "ground state:\nthe window closes", -260, -120, ha="right")
    note(P["cur"][0], "window at the\ndataset's energy", -520, 120, ha="right")
    note(P["thr"][0], r"threshold $\delta e^*(J_z)$:" + "\n" + r"width $=\tau$", 380, 300, color="#17704f")
    note(P["dset"][0], r"dataset's $\delta e$", 300, 160, color="#3a3a3a")
    ax.text(0.012, 0.975, tag, transform=ax.transAxes, fontsize=9, color=C.INK, va="top", ha="left")
    handles = [Patch(facecolor=CERT, edgecolor="none", label=r"certified (width $\leq\tau$)"),
               Patch(facecolor=NEUTRAL, edgecolor="none", label="not certified"),
               Line2D([], [], color=INKC, lw=1.8, label="window at the dataset's energy"),
               Line2D([], [], marker="o", color="none", markerfacecolor=EMU_C, markeredgecolor="none", ms=5.5,
                      label="emulated method, at its own energy"),
               Line2D([], [], marker="D", color="none", markerfacecolor=EST_C, markeredgecolor="none", ms=4.5,
                      label=r"estimate at the dataset's energy ($|\Delta Z|$, sign assumed from emulation)")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.075, 0.995), frameon=False, fontsize=6.8,
              handlelength=1.5, borderaxespad=0.2, ncol=2, columnspacing=1.6)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(C.HERE, out + "." + ext), dpi=600)
    plt.close(fig)
    print("wrote", out)


def main():
    todo = ((57, "figS_landscape_n57", r"$n=57$"), (115, "figS_landscape_n115", r"$n=115$"))
    for n, out, tag in todo:
        D = data(n)
        B = D["box"]
        print("n=%d: %d couplings, de in [%.0e, %.3g], z in [%.1f, %.1f]" % (n, len(D["Js"]), B.de_min, B.de_max,
                                                                              B.z_min, B.z_max))
        img, P, nemu = render(D, os.path.join(C.HERE, "_render_%s.png" % out))
        print("   emulated states inside the plotted range:", nemu)
        compose(D, img, P, out, tag)
        if "--one" in sys.argv:
            break


if __name__ == "__main__":
    main()
