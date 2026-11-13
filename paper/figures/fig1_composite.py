"""Main-text Fig. 1: what a sample's energy certifies, and what the method does inside the window (n = 57).

  python fig1_composite.py     -> fig1_composite.pdf / .png  (7.0 in wide; the 3-D panels are 600-dpi rasters made
                                  by PyVista off screen at 2x and downsampled; all text is vector, Computer Modern)

(a) Relief of the window width w(J_z, de) / tau of m_s over the (J_z, de) plane (log height).  w = m_s^+ - m_s^- is
    the inner (rigorous) width: the hull of the stored sector states of the map run (landscape_data.py; it reproduces
    summary_map.json at every stored window energy), straight between computed J_z; tau = 0.06 |m_s,GS| of each row.
    Teal: w <= tau ("certified": the dataset's label is then within tau = 6 % of |m_s,GS| of the ground-state
    value; the window midpoint within tau/2) -- the dark teal shoreline is the contour w = tau of the surface.
    Line: the dataset's digitized error de_dig(J_z) (rows[*].eps.dig / n) traced on the relief, grey where it is the
    conditional floor of the out-of-distribution points.
(b) The quantitative slice at the dataset's energy: rows[*].at_dig.ratio_out (outer width / tau, the map value).
(c) Our device data (phase3/full_runs/qpu/out_20261031T093107Z/out/device_A_J1.2.json, var.rec.signed_dZ_site =
    eta_i (<Z_i> - <Z_i>_DMRG), J_z = 1.2), on the heavy-hex graph (landscape_data.layout).  Ringed: the 4 boundary
    sites moved by the routing (qpu/jobs/A/prep.json sel.paths).
(d) The noiseless simulation of the same circuits (control_J1.2.json, same field), same colour scale.
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize  # noqa: E402
from PIL import Image  # noqa: E402

import common as C  # noqa: E402
import landscape_data as L  # noqa: E402

os.environ.setdefault("PYVISTA_OFF_SCREEN", "true")
import pyvista as pv  # noqa: E402
import vtk  # noqa: E402

N = 57
QPU = os.path.join(C.ROOT, "phase3", "full_runs", "qpu")
QOUT = os.path.join(QPU, "out_20261031T093107Z", "out")

# palette: greys for context, one teal for "certified", one warm sequential ramp for the excess of order
LAND, WALL, CERT, SHORE, INK, MUTE = "#d6d8db", "#e3e5e8", "#169b88", "#0b5f53", "#1d1d1d", "#8a8a86"
CMAP = LinearSegmentedColormap.from_list("excess", ["#fbf3ea", "#f7c9a2", "#ef8d55", "#cf5521", "#7c2a0f"])
SS, DPI = 2, 600


def rc():
    plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                         "axes.formatter.use_mathtext": True, "axes.unicode_minus": False, "font.size": 8,
                         "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.6,
                         "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.edgecolor": "#555555",
                         "xtick.color": "#444444", "ytick.color": "#444444", "pdf.fonttype": 42})


# ------------------------------------------------------------------------------------------------ (a) the relief
class Box:
    SX, SY, SZ = 1.70, 1.0, 0.62

    def __init__(self, lmin, lmax, zmin, zmax):
        self.lmin, self.lmax, self.zmin, self.zmax = lmin, lmax, zmin, zmax

    def X(self, J):
        return (np.asarray(J, float) - 1.1) / (6.0 - 1.1) * self.SX

    def Y(self, de):                    # small de in front (y = 0), large de at the back
        return (np.log10(de) - self.lmin) / (self.lmax - self.lmin) * self.SY

    def Z(self, lw):                    # lw = log10(w / tau)
        return (np.asarray(lw, float) - self.zmin) / (self.zmax - self.zmin) * self.SZ


JSTAR = C.map_summary()["jstar"]["%d_m_s_r1" % N]["J_star_central"]


def relief_data():
    rows = [r for r in L.rows(N) if r["Jz"] not in (3.2, 3.4)]          # 3.2/3.4: short extra chains (J*)
    Js = np.array([r["Jz"] for r in rows])
    tau = np.array([r["tau"] for r in rows])
    emax = min((L.pool(N, J)[0].max() - L.thr(N, J)["E0"]) / N for J in Js)
    de_max = np.floor(emax * 1000) / 1000
    de = np.logspace(-4, np.log10(de_max), 150)
    up, lo, ok = L.landscape(N, Js, de)
    assert ok.all()
    lw = np.log10((up - lo) / tau[:, None])
    wd = []
    for r in rows:                      # inner width at the dataset's digitized energy (same hull)
        E, o = L.pool(N, r["Jz"])
        t = L.thr(N, r["Jz"])
        a, b = L.inner(E, o, [t["E0"] + r["eps"]["dig"]])
        wd.append(np.log10((b[0] - a[0]) / r["tau"]))
    return dict(Js=Js, de=de, lw=lw, dig=np.array([r["eps"]["dig"] / N for r in rows]), lwd=np.array(wd),
                ood=np.array([bool(r.get("ood")) for r in rows]),
                box=Box(-4, np.log10(de_max), np.floor(lw.min() * 4) / 4 - 0.15, np.ceil(lw.max() * 4) / 4))


def refine(Js, V, k=14):
    Jf = np.concatenate([np.linspace(Js[i], Js[i + 1], k, endpoint=False) for i in range(len(Js) - 1)] + [[Js[-1]]])
    i = np.clip(np.searchsorted(Js, Jf, side="right") - 1, 0, len(Js) - 2)
    t = (Jf - Js[i]) / (Js[i + 1] - Js[i])
    return Jf, (1 - t)[:, None] * V[i] + t[:, None] * V[i + 1]


def relief_meshes(D):
    B = D["box"]
    Jf, lw = refine(D["Js"], D["lw"])
    X, Y = np.meshgrid(B.X(Jf), B.Y(D["de"]), indexing="ij")
    top = pv.StructuredGrid(X, Y, B.Z(lw))
    top.point_data["lw"] = lw.ravel(order="F")
    surf = top.extract_surface(algorithm="dataset_surface").compute_normals(auto_orient_normals=True)
    shore = top.contour([0.0], scalars="lw")
    z0 = B.Z(B.zmin)
    walls = []
    for xs, ys, zs in ((X[:, 0], Y[:, 0], lw[:, 0]), (X[0], Y[0], lw[0]), (X[-1], Y[-1], lw[-1]),
                       (X[:, -1], Y[:, -1], lw[:, -1])):
        Pt = np.c_[xs, ys, B.Z(zs)]
        Pb = np.c_[xs, ys, np.full(len(xs), z0)]
        n = len(xs)
        pts = np.vstack([Pt, Pb])
        faces = np.hstack([[4, i, i + 1, n + i + 1, n + i] for i in range(n - 1)])
        walls.append(pv.PolyData(pts, faces).compute_normals(auto_orient_normals=False, consistent_normals=True))
    return surf, shore, walls


def lw_at(D, J, de):
    """log10(w / tau) of the relief at (J, de): the same straight-in-J, grid-in-de interpolation as the mesh"""
    Jf, lw = refine(D["Js"], D["lw"], k=200)
    i = int(np.argmin(np.abs(Jf - J)))
    return float(np.interp(np.log10(de), np.log10(D["de"]), lw[i]))


def render_relief(D, W, H, png):
    B = D["box"]
    p = pv.Plotter(off_screen=True, window_size=(W * SS, H * SS), lighting="none")
    p.set_background("white")
    c = (B.SX / 2, B.SY / 2, B.SZ / 3)
    p.add_light(pv.Light(position=(-1.6, -2.4, 3.2), focal_point=c, intensity=0.72))      # key, front-left high
    p.add_light(pv.Light(position=(3.8, -0.8, 1.2), focal_point=c, intensity=0.30))       # fill, right
    p.add_light(pv.Light(position=(0.8, 3.6, 2.4), focal_point=c, intensity=0.30))        # rim, back
    p.add_light(pv.Light(light_type="headlight", intensity=0.16))
    p.add_mesh(pv.Plane(center=(c[0], c[1], -0.002), direction=(0, 0, 1), i_size=400, j_size=400), color="white",
               ambient=1.0, diffuse=0.0, specular=0.0)        # pure white floor: only the ambient-occlusion shadow
    surf, shore, walls = relief_meshes(D)
    p.add_mesh(surf, scalars="lw", cmap=ListedColormap([CERT, LAND]), clim=(-1, 1), show_scalar_bar=False,
               smooth_shading=True, interpolate_before_map=True, ambient=0.48, diffuse=0.58, specular=0.12,
               specular_power=20)
    for w in walls:
        p.add_mesh(w, color=WALL, ambient=0.42, diffuse=0.62, specular=0.05)
    p.add_mesh(shore.tube(radius=0.0042, n_sides=16), color=SHORE, ambient=0.5)
    P = np.array([(B.X(J), B.Y(e), B.Z(z) + 0.012) for J, e, z in zip(D["Js"], D["dig"], D["lwd"])])
    k0 = int(np.argmax(~D["ood"]))
    p.add_mesh(pv.Spline(P[:k0 + 1], 60).tube(radius=0.0078, n_sides=20), color="#7d7d7d", ambient=0.5)
    p.add_mesh(pv.lines_from_points(P[k0:]).tube(radius=0.0090, n_sides=20), color=INK, ambient=0.45,
               specular=0.3)
    p.add_mesh(pv.Sphere(radius=0.017, center=P[-1], theta_resolution=32, phi_resolution=32), color=INK)
    p.enable_ssao(radius=0.10, bias=0.002, kernel_size=64, blur=True)
    p.camera_position = [(-0.90, -2.45, 2.05), (0.88, 0.50, 0.12), (0, 0, 1)]
    p.camera.view_angle = 23
    img = p.screenshot(png, return_img=True)
    img = img.copy()
    img[: int(0.06 * img.shape[0])] = 255                 # the far horizon of the floor, a hairline at the top
    ren = p.renderer
    co = vtk.vtkCoordinate()
    co.SetCoordinateSystemToWorld()

    def proj(Q):
        out = []
        for q in np.atleast_2d(Q):
            co.SetValue(*map(float, q))
            x, y = co.GetComputedDoubleDisplayValue(ren)
            out.append((x / SS, H - y / SS))
        return np.array(out)
    z0 = B.Z(B.zmin)
    zt = [k for k in (-1, 0, 1) if B.zmin <= k <= B.zmax]
    mk = dict(
        jl=proj([(0, -0.03, z0), (B.SX, -0.03, z0)]),
        jx=proj([(B.X(J), -0.03, z0) for J in (2, 4, 6)]), jx2=proj([(B.X(J), -0.065, z0) for J in (2, 4, 6)]),
        dl=proj([(-0.03, 0, z0), (-0.03, B.SY, z0)]),
        dy=proj([(-0.03, B.Y(10.0 ** k), z0) for k in (-4, -3, -2)]),
        dy2=proj([(-0.065, B.Y(10.0 ** k), z0) for k in (-4, -3, -2)]),
        zl=proj([(-0.01, B.SY + 0.01, z0), (-0.01, B.SY + 0.01, B.Z(zt[-1]))]),
        zx=proj([(-0.01, B.SY + 0.01, B.Z(k)) for k in zt]),
        zx2=proj([(-0.045, B.SY + 0.01, B.Z(k)) for k in zt]),
        js=proj([(B.X(JSTAR), -0.03, z0), (B.X(JSTAR), -0.065, z0)]),
        jt=proj([(B.SX * 0.5, -0.20, z0)]), dt=proj([(-0.05, B.SY + 0.10, z0)]),
        zt=proj([(-0.01, B.SY + 0.01, B.Z(zt[-1]) + 0.05)]),
        cert=proj([(B.X(5.0), B.Y(3.0e-4), B.Z(lw_at(D, 5.0, 3.0e-4)))]), path=proj([P[-1]]))
    p.close()
    return whiten(np.asarray(Image.fromarray(img).resize((W, H), Image.LANCZOS))), mk, zt


# ------------------------------------------------------------------------------------------------ (c,d) lattice
def whiten(a, thr=244, tint=8):
    """near-white, nearly grey pixels (the faint occlusion tint far from the objects) -> pure white"""
    a = a.copy()
    rgb = a[..., :3].astype(int)
    m = (rgb.min(axis=2) >= thr) & (rgb.max(axis=2) - rgb.min(axis=2) <= tint)
    a[m, :3] = 255
    return a


def device_values():
    dev = C.rj(os.path.join(QOUT, "device_A_J1.2.json"))
    ctl = C.rj(os.path.join(QOUT, "control_J1.2.json"))
    ref = C.rj(os.path.join(QPU, "refs", "ref_n57_J1.2.json"))
    eta = np.array(L.graph(N)["eta"], float)
    out = {}
    for name, d in (("device", dev), ("control", ctl)):
        v = d["var"]["rec"]
        s = np.array(v["signed_dZ_site"])
        assert np.abs(s - eta * (np.array(v["labels"]["Z"]) - np.array(ref["labels"]["Z"]))).max() < 1e-12
        assert abs(s.mean() - v["err"]["dm_s"]) < 1e-12
        out[name] = (s, v["err"]["dm_s"], v["ratio"])
    moved = sorted(int(k) for k in C.rj(os.path.join(QPU, "jobs", "A", "prep.json"))["sel"]["paths"])
    return out, moved


def render_lattice(n, vals, vmax, moved, W, H, png, cmap=None):
    cmap = cmap or CMAP
    pos, edges = L.layout(n)
    pos = pos - pos.mean(axis=0)
    P3 = np.c_[pos, np.zeros(len(pos))]
    size = np.ptp(pos, axis=0).max()
    p = pv.Plotter(off_screen=True, window_size=(W * SS, H * SS), lighting="none")
    p.set_background("white")
    p.add_light(pv.Light(position=(-0.6 * size, -1.0 * size, 2.4 * size), focal_point=(0, 0, 0), intensity=0.62))
    p.add_light(pv.Light(position=(1.2 * size, -0.4 * size, 0.9 * size), focal_point=(0, 0, 0), intensity=0.25))
    p.add_light(pv.Light(position=(0.0, 1.5 * size, 1.2 * size), focal_point=(0, 0, 0), intensity=0.20))
    p.add_light(pv.Light(light_type="headlight", intensity=0.22))
    ymax, ymin = pos[:, 1].max() + 0.9, pos[:, 1].min() - 0.6 * size     # floor ends just behind the lattice
    p.add_mesh(pv.Plane(center=(0, (ymax + ymin) / 2, -0.38), direction=(0, 0, 1), i_size=size * 2.2,
                        j_size=ymax - ymin),
               color="white", ambient=1.0, diffuse=0.0, specular=0.0)   # white floor: only the occlusion shadow
    bonds = pv.PolyData(P3, lines=np.hstack([[2, a, b] for a, b in edges]))
    p.add_mesh(bonds.tube(radius=0.07, n_sides=24), color="#aaa79f", smooth_shading=True, ambient=0.45,
               diffuse=0.6, specular=0.2)
    rgba = cmap(Normalize(0, vmax)(vals))
    for k in range(n):
        p.add_mesh(pv.Sphere(radius=0.30, center=P3[k], theta_resolution=44, phi_resolution=44), color=rgba[k, :3],
                   smooth_shading=True, ambient=0.50, diffuse=0.55, specular=0.32, specular_power=36)
    for k in moved:                                       # a thin dark ring around each routed site
        ring = pv.ParametricTorus(ringradius=0.43, crosssectionradius=0.028, u_res=90, v_res=16, w_res=4)
        p.add_mesh(ring.translate(P3[k]), color="#3a3a3a", smooth_shading=True, ambient=0.5, diffuse=0.5)
    p.enable_ssao(radius=0.45, bias=0.004, kernel_size=64, blur=True)
    p.camera_position = [(0.0, -1.20 * size, 2.10 * size), (0, -0.05 * size, 0), (0, 0, 1)]
    p.camera.view_angle = 30
    img = p.screenshot(png, return_img=True).copy()
    p.close()
    img[: int(0.06 * img.shape[0])] = 255                 # the far horizon of the floor, a hairline at the top
    a = whiten(np.asarray(Image.fromarray(img).resize((W, H), Image.LANCZOS)))
    rgb = a[..., :3].astype(int)
    sat_rows = np.where(((rgb.max(axis=2) - rgb.min(axis=2)) > 40).any(axis=1))[0]
    if len(sat_rows):                                     # blank the far floor above the lattice (occlusion banding)
        a[: max(0, sat_rows[0] - int(0.035 * H)), :, :3] = 255
        top = slice(0, min(H, sat_rows[0] + int(0.06 * H)))  # light, unsaturated banding beside the top row
        sub = a[top].astype(int)
        m = (sub[..., :3].min(axis=2) > 200) & ((sub[..., :3].max(axis=2) - sub[..., :3].min(axis=2)) < 12)
        a[top][m] = 255
        blk = a[top].copy()
        blk[m, :3] = 255
        a[top] = blk
    nz = np.where((a[..., :3] < 246).any(axis=2))
    y0, y1, x0, x1 = nz[0].min(), nz[0].max(), nz[1].min(), nz[1].max()
    return a[max(0, y0 - 8):y1 + 8, max(0, x0 - 8):x1 + 8]


def colorbar(fig, rect, vmax, label, cmap=None):
    cax = fig.add_axes(rect)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, vmax), cmap=cmap or CMAP), cax=cax,
                      orientation="horizontal")
    cb.outline.set_linewidth(0.4)
    cb.set_ticks(np.round(np.arange(0, vmax + 1e-9, 0.1 if vmax <= 0.6 else 0.2), 2))
    cb.ax.tick_params(labelsize=6.8, length=2, width=0.4, pad=1.5)
    cb.set_label(label, fontsize=7, labelpad=2)
    return cb


# ------------------------------------------------------------------------------------------------ composition
def main():
    rc()
    D = relief_data()
    S = C.map_summary()
    W_IN, H_IN = 7.0, 4.40
    AW, AH, AX0 = 4.20, 2.80, 0.42                   # panel (a), inches (AX0: margin for the axis titles)
    imgA, mk, zt = render_relief(D, int((AW - AX0) * DPI), int(AH * DPI), os.path.join(C.HERE, "_render_fig1_a.png"))
    vals, moved = device_values()
    vmax = 0.5
    LW_IN = 2.20                                     # lattice panels, inches wide
    imgs = [render_lattice(N, vals[k][0], vmax, moved, int(LW_IN * DPI), int(0.80 * LW_IN * DPI),
                           os.path.join(C.HERE, "_render_fig1_%s.png" % t)) for k, t in (("device", "c"),
                                                                                       ("control", "d"))]
    fig = plt.figure(figsize=(W_IN, H_IN))
    fx = lambda x: x / W_IN                         # noqa: E731
    fy = lambda y: y / H_IN                         # noqa: E731
    # (a) relief
    axA = fig.add_axes([fx(AX0), fy(H_IN - AH), fx(AW - AX0), fy(AH)])
    WA, HA = imgA.shape[1], imgA.shape[0]
    axA.imshow(imgA)
    axA.set_xlim(0, WA)
    axA.set_ylim(HA, 0)
    axA.axis("off")
    g = dict(color="#777777", lw=0.6)
    tk = dict(fontsize=7, color="#444444")
    for key in ("jl", "dl", "zl"):
        axA.plot(*mk[key].T, **g)
    for q, q2, s in zip(mk["jx"], mk["jx2"], ("2", "4", "6")):
        axA.plot(*np.c_[q, q2], **g)
        axA.text(q2[0], q2[1] + 30, s, ha="center", va="top", **tk)
    for q, q2, k in zip(mk["dy"], mk["dy2"], (-4, -3, -2)):
        axA.plot(*np.c_[q, q2], **g)
        axA.text(q2[0] - 28, q2[1], r"$10^{%d}$" % k, ha="right", va="center", **tk)
    lab = dict(fontsize=7.6, color=INK)
    for q, q2, k in zip(mk["zx"], mk["zx2"], zt):
        axA.plot(*np.c_[q, q2], **g)
        axA.text(q2[0] - 25, q2[1], {-1: "0.1", 0: "1", 1: "10"}[k], ha="right", va="center", **tk)
    axA.text(mk["zt"][0][0], mk["zt"][0][1], "width / " + r"$\tau$", ha="center", va="bottom", **lab)
    axA.plot(*mk["js"].T, color=SHORE, lw=0.9)
    axA.text(mk["js"][1][0], mk["js"][1][1] + 30, r"$J^*$", ha="center", va="top", color=SHORE, fontsize=7.2)

    def along(seg, dist, side, text):    # axis title parallel to its axis, "dist" pixels outwards
        (x1, y1), (x2, y2) = seg
        ang = np.degrees(np.arctan2(-(y2 - y1), x2 - x1))
        ang = ang - 180 if ang > 90 else ang + 180 if ang < -90 else ang
        nx, ny = (y2 - y1), -(x2 - x1)
        nn = np.hypot(nx, ny)
        nx, ny = nx / nn, ny / nn
        if (side == "left" and nx > 0) or (side == "below" and ny < 0):
            nx, ny = -nx, -ny
        xm, ym = (x1 + x2) / 2 + dist * nx, (y1 + y2) / 2 + dist * ny
        axA.text(xm, ym, text, rotation=ang, rotation_mode="anchor", ha="center", va="center", **lab)
    along(mk["jl"], 175, "below", r"coupling $J_z$")
    along(mk["dl"], 235, "left", r"energy error per site, $\delta e$")
    axA.text(*mk["cert"][0], "certified\n" + r"(width $\leq\tau$)", color="white", fontsize=8.2, ha="center",
             va="center", fontweight="bold")
    axA.text(mk["path"][0][0] + 38, mk["path"][0][1], "dataset's\nenergy error", color=INK, fontsize=7,
             ha="left", va="center")
    fig.text(0.004, 0.995, "(a)", fontsize=9, va="top", ha="left", fontweight="bold")
    fig.text(fx(0.30), 0.995, r"the range of $m_s$ allowed by the energy (height: width of the range, log scale)", fontsize=7.6,
             va="top", ha="left", color=INK)
    # (b) slice
    rows = sorted((r for r in S["rows"] if r["n"] == N and r["label"] == "m_s"), key=lambda r: r["Jz"])
    J = np.array([r["Jz"] for r in rows])
    w = np.array([r["at_dig"]["ratio_out"] for r in rows])
    ood = np.array([bool(r.get("ood")) for r in rows])
    jstar = S["jstar"]["%d_m_s_r1" % N]["J_star_central"]
    axB = fig.add_axes([fx(0.55), fy(0.40), fx(AW - 0.75), fy(1.02)])
    axB.axhspan(0.05, 1.0, color="#d9efeb", lw=0, zorder=0)
    axB.axhline(1.0, color=CERT, lw=0.9, zorder=1)
    axB.axvline(jstar, color=MUTE, lw=0.6, ls=(0, (3, 2)), zorder=1)
    axB.plot(J, w, color=INK, lw=1.0, zorder=2)
    axB.plot(J[~ood], w[~ood], "o", ms=2.6, color=INK, zorder=3)
    axB.plot(J[ood], w[ood], "o", ms=2.6, mfc="white", mec=INK, mew=0.7, zorder=3)
    # computed points whose certification is proved with exact lower bounds (rigor run v2, declared grid)
    rig = C.rj(os.path.join(C.ROOT, "phase3", "full_runs", "rigor", "outputs", "results_v2.json"))
    Jr = sorted(r["Jz"] for r in rig["rows"] if r["n"] == N and r["label"] == "m_s" and r["certified"])
    wr = [w[int(np.argmin(abs(J - x)))] for x in Jr]
    assert all(min(abs(J - x)) < 1e-9 for x in Jr) and len(Jr) == 6, Jr
    axB.plot(Jr, wr, "o", ms=6.0, mfc="none", mec=CERT, mew=0.9, zorder=4)
    axB.text(3.35, 5.0, "ringed: lower bounds proved\nin exact arithmetic", color=SHORE, fontsize=6.6,
             ha="left", va="center")
    axB.set_yscale("log")
    axB.set_ylim(0.15, 30)
    axB.set_xlim(1.0, 6.2)
    axB.set_yticks([0.3, 1, 3, 10])
    axB.set_yticklabels(["0.3", "1", "3", "10"])
    axB.set_xticks([1.2, 2, 3, 4, 5, 6])
    axB.set_xticklabels(["1.2", "2", "3", "4", "5", "6"])
    axB.minorticks_off()
    for s in ("top", "right"):
        axB.spines[s].set_visible(False)
    axB.set_xlabel(r"coupling $J_z$", labelpad=1)
    axB.set_ylabel("width / " + r"$\tau$", labelpad=2)
    axB.text(6.15, 0.42, r"certified (width $\leq\tau$)", color=SHORE, fontsize=7, ha="right", va="center")
    axB.text(4.6, 1.22, r"width $=\tau$", color=SHORE, fontsize=7, ha="left", va="bottom")
    axB.plot([1.2, 1.2], [0.15, 0.21], color="#cf5521", lw=1.2, zorder=4)
    axB.text(1.27, 0.19, "(c, d)", color="#cf5521", fontsize=6.8, ha="left", va="center")
    axB.text(jstar + 0.07, 13, r"$J^*=%g$" % jstar, color="#555555", fontsize=7, ha="left", va="center")
    fig.text(0.004, fy(1.52), "(b)", fontsize=9, va="top", ha="left", fontweight="bold")
    fig.text(fx(0.30), fy(1.52), "the window width at the dataset's energy", fontsize=7.6, va="top", ha="left",
             color=INK)
    # (c), (d) lattices
    x0 = AW + 0.08
    y_top = H_IN - 0.05
    titles = (("(c)", "our device data (ringed: 4 routed sites)", "device"),
              ("(d)", "noiseless simulation of the same circuits", "control"))
    h = (H_IN - 0.05 - 2 * 0.30 - 0.02 - 0.64) / 2          # lattice height that fits the column
    colw = W_IN - x0 - 0.02
    for img, (letter, ttl, key) in zip(imgs, titles):
        wd = h * img.shape[1] / img.shape[0]
        y_top -= 0.30
        ax = fig.add_axes([fx(x0 + 0.04 + (colw - 0.04 - wd) / 2), fy(y_top - h), fx(wd), fy(h)])
        ax.imshow(img)
        ax.axis("off")
        s, dm, r = vals[key]
        fig.text(fx(x0 - 0.02), fy(y_top + 0.27), letter, fontsize=9, fontweight="bold", va="top")
        fig.text(fx(x0 + 0.24), fy(y_top + 0.265), ttl, fontsize=7.6, va="top", color=INK)
        fig.text(fx(x0 + 0.24), fy(y_top + 0.115), r"$\Delta m_s=+%.3f$; every site $>0$ (smallest $+%.3f$)"
                 % (dm, s.min()), fontsize=6.8, va="top", color="#3d3d3d")
        y_top -= h + 0.02
    colorbar(fig, [fx(x0 + 0.24), fy(0.36), fx(LW_IN - 0.40), fy(0.072)], vmax,
             r"excess of order per site, $\eta_i\,\Delta\langle Z_i\rangle$, at $J_z=1.2$")
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(C.HERE, "fig1_composite." + ext), dpi=DPI)
    plt.close(fig)
    dv, cv = vals["device"][0], vals["control"][0]
    print("wrote fig1_composite (%.2f x %.2f in); device mean %.4f min %.4f max %.4f; control mean %.4f min %.4f "
          "max %.4f; routed sites %s; lattice heights %s"
          % (W_IN, H_IN, dv.mean(), dv.min(), dv.max(), cv.mean(), cv.min(), cv.max(), moved,
             [round(LW_IN * i.shape[0] / i.shape[1], 2) for i in imgs]))


if __name__ == "__main__":
    main()
