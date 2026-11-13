"""Export the data of the four 3-D Supplemental figures for their native PGFPlots/TikZ versions.

  cd paper/figures/pgf_sm_3d && python -B export_sm3d.py

  figS_landscape_n57 / _n115 (fig_landscape.py)  ->  land57_*.dat, land115_*.dat
  figS_lattice / _n115       (fig_lattice.py)    ->  lat57_*.dat,  lat115_*.dat
  numbers printed in the figures                 ->  values57.tex, values115.tex
  checks                                         ->  export_check.txt

Nothing physical is recomputed.  Every array comes from the loaders of the existing scripts, imported as they are:
fig_landscape.data(n) (inner window edges m_s^+-m_s,GS and m_s^- - m_s,GS on 16 computed couplings x 150 de, the window
at the dataset's digitized error, the threshold de*(J_z) = eps_tau_out / n), fig_landscape.thresh_at (log-linear in
J_z, the rule used for J*), landscape_data.emu_states / dz_matched (orange / violet markers), landscape_data.
site_overorder / site_freedom / layout (lattices).  The edge grids are drawn as they are (16 couplings x 150 de),
Gouraud-shaded, i.e. straight between computed couplings (the rule of fig_landscape.refine, checked below).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import common as C                 # noqa: E402
import landscape_data as L         # noqa: E402
import fig_landscape as FL         # noqa: E402  (imports pyvista/vtk at module level; nothing is rendered here)

J_LAT = 1.2
LOG = []


def log(s=""):
    print(s)
    LOG.append(s)


def check(cond, what):
    log(("PASS  " if cond else "FAIL  ") + what)
    assert cond, what


def fmt(v):
    if isinstance(v, (bool, np.bool_)):
        return "1" if v else "0"
    if isinstance(v, (int, np.integer)):
        return "%d" % v
    return "%.12g" % v


def wtable(name, header, rows):
    with open(os.path.join(HERE, name), "w", encoding="ascii", newline="\n") as f:
        f.write(" ".join(header) + "\n")
        for r in rows:
            f.write(" ".join(fmt(v) for v in r) + "\n")


def interp_J(Js, V, Jq):
    """straight interpolation between computed couplings, row by row (fig_landscape.refine)"""
    Jq = np.atleast_1d(Jq)
    i = np.clip(np.searchsorted(Js, Jq, side="right") - 1, 0, len(Js) - 2)
    t = (Jq - Js[i]) / (Js[i + 1] - Js[i])
    return (1 - t)[:, None] * V[i] + t[:, None] * V[i + 1]


def surface_at(D, key, J, de):
    """value of the drawn surface at (J, de): straight in J_z, linear in log10 de (as the 3-D mesh)"""
    row = interp_J(D["Js"], D[key], [J])[0]
    return float(np.interp(np.log10(de), np.log10(D["de"]), row))


# ----------------------------------------------------------------------------------------------- landscapes
def landscape(n, cap):
    log("=" * 100)
    log("[figS_landscape_n%d]" % n)
    D = FL.data(n)                                   # asserts the validity mask of the whole grid
    log("PASS  fig_landscape.data(%d): edges valid on the whole grid (assert ok.all() inside)" % n)
    B = D["box"]
    Js, de, up, lo = D["Js"], D["de"], D["up"], D["lo"]
    log("grid: %d computed couplings x %d de (%.4g .. %.4g, log-spaced); up in [%.4f, %.4f], lo in [%.4f, %.4f]"
        % (len(Js), len(de), de[0], de[-1], up.min(), up.max(), lo.min(), lo.max()))
    # caption: de range and the coupling that sets it
    emax = {J: (L.pool(n, J)[0].max() - L.thr(n, J)["E0"]) / n for J in Js}
    Jset = min(emax, key=emax.get)
    check(abs(B.de_max - cap["de_max"]) < 1e-12, "caption: the de range stops at %.3f (largest stored energy common "
                                                 "to all couplings %.5f, at J_z = %g)" % (B.de_max, emax[Jset], Jset))
    if "J_set" in cap:
        check(abs(Jset - cap["J_set"]) < 1e-9, "caption: that limit is set by J_z = %g" % cap["J_set"])
    check((up >= 0).all() and (lo <= 0).all(), "upper edge >= m_s,GS >= lower edge everywhere (the ground state is "
                                               "in every window)")
    up_w = up - lo
    w_main = None
    if n == 57:                                       # the width of main Fig. 2(a) (fig1_composite.relief_data)
        import fig1_composite as F
        R = F.relief_data()
        tau = np.array([r["tau"] for r in D["rows"]])
        dd = np.abs(np.log10(up_w / tau[:, None]) - R["lw"]).max()
        w_main = dd
        check(dd < 1e-12 and np.allclose(R["Js"], Js) and np.allclose(R["de"], de),
              "upper minus lower edge = the width of main Fig. 2(a) on the same grid (max |diff| of log10 w/tau "
              "= %.1e)" % dd)
    # the grid is drawn as it is (no resampling): Gouraud shading (shader=interp) between the grid points is
    # straight in J_z between computed couplings, the rule of fig_landscape.refine (checked here on its own mesh)
    wtable("land%d_grid_raw.dat" % n, ["J", "de", "up", "lo"],
           [(Js[i], de[k], up[i, k], lo[i, k]) for k in range(len(de)) for i in range(len(Js))])
    Jf, upf = FL.refine(D, up)
    check(np.abs(interp_J(Js, up, Jf) - upf).max() < 1e-12, "straight interpolation between computed couplings "
                                                            "= fig_landscape.refine")
    log("drawn maps: the full grid, %d couplings x %d de = %d points per map, Gouraud-shaded (no downsampling)"
        % (len(Js), len(de), up.size))
    # threshold de*(J_z), log-linear between computed couplings (fig_landscape.thresh_at); 0 where eps_tau_out = 0
    Jt = np.round(Js[0] + 0.01 * np.arange(int(round((Js[-1] - Js[0]) / 0.01)) + 1), 10)
    with np.errstate(divide="ignore"):
        th = FL.thresh_at(D, Jt)
    zero = [(r["Jz"]) for r in D["rows"] if r["eps_tau_out"] <= 0]
    if zero:
        log("NOTE  eps_tau_out = 0 at J_z = %s (no error certifies there); the threshold is drawn from where it is "
            "positive" % zero)
    ok = th > 0
    wtable("land%d_thresh.dat" % n, ["J", "de"], [(a, b) for a, b in zip(Jt[ok], th[ok])])
    inside = (th >= B.de_min) & (th <= B.de_max)
    log("threshold de*: inside the plotted de range for J_z in [%.2f, %.2f]" % (Jt[inside].min(), Jt[inside].max()))
    for r in D["rows"]:
        log("  J=%-4g de*=%.6f de_dig=%.6f  %s" % (r["Jz"], r["eps_tau_out"] / n, r["eps"]["dig"] / n,
                                                  "certified (de_dig <= de*)" if r["eps"]["dig"] <= r["eps_tau_out"]
                                                  else ""))
    # dataset line and the window at the dataset's energy (grey = conditional floor)
    ood = np.array([bool(r.get("ood")) for r in D["rows"]])
    k0 = int(np.argmax(~ood))
    check(ood[:k0].all() and not ood[k0:].any(), "ood rows are the first %d couplings" % k0)
    dig, wlo, wup = D["dig"], D["wlo"], D["wup"]
    wtable("land%d_line_floor.dat" % n, ["J", "de", "wlo", "wup"],
           [(Js[i], dig[i], wlo[i], wup[i]) for i in range(k0 + 1)])
    wtable("land%d_line_data.dat" % n, ["J", "de", "wlo", "wup"],
           [(Js[i], dig[i], wlo[i], wup[i]) for i in range(k0, len(Js))])
    wtable("land%d_bars_floor.dat" % n, ["J", "wlo", "dw"],                 # bars at computed couplings
           [(Js[i], wlo[i], wup[i] - wlo[i]) for i in range(len(Js)) if ood[i]])
    wtable("land%d_bars_data.dat" % n, ["J", "wlo", "dw"],
           [(Js[i], wlo[i], wup[i] - wlo[i]) for i in range(len(Js)) if not ood[i]])
    check((wlo < 0).all() and (wup > 0).all(), "window at the dataset's energy straddles m_s,GS at every coupling")
    dmax = max(max(abs(surface_at(D, "up", Js[i], dig[i]) - wup[i]), abs(surface_at(D, "lo", Js[i], dig[i]) - wlo[i]))
               for i in range(len(Js)) if de[0] <= dig[i] <= de[-1])
    check(dmax < 5e-3, "the window at the dataset's energy lies on the drawn edges (max |diff| between the hull at "
                       "de_dig and the grid read at de_dig = %.1e)" % dmax)
    # markers: orange = emulated states at their own energy (inside the plotted range, as fig_landscape.render);
    # violet = estimates at the dataset's energy (|Delta Z| with the sign assumed from the emulation)
    emu_all = L.emu_states(n)
    emu = [(J, e, dm) for J, e, dm in emu_all if B.de_min <= e <= B.de_max and FL.J_MIN <= J <= FL.J_MAX]
    out_rng = [(J, e) for J, e, _ in emu_all if not (B.de_min <= e <= B.de_max)]
    check(min(J for J, _, _ in emu) == cap["emu_from"] and all(J >= cap["emu_from"] for J, _, _ in emu) and
          all(J < cap["emu_from"] for J, _ in out_rng),
          "caption: orange only for J_z >= %g (inside the plotted range: %s)" % (cap["emu_from"],
                                                                                 [J for J, _, _ in emu]))
    rows_e = []
    for J, e, dm in emu:
        u = surface_at(D, "up", J, e)
        rows_e.append((J, e, dm, u))
        exact = ""
        if any(abs(J - j) < 1e-9 for j in Js):       # at computed couplings: the hull at the state's own energy
            E, o = L.pool(n, J)
            t = L.thr(n, J)
            lo_, hi_ = L.inner(E, o, [t["E0"] + n * e])
            exact = " (hull at that energy: %.4f)" % (hi_[0] - t["m_s_GS"])
        log("  orange J=%-4g de=%.5f dm_s=%+.4f; upper edge at its own energy %.4f, ratio %.2f%s"
            % (J, e, dm, u, dm / u, exact))
    wtable("land%d_emu.dat" % n, ["J", "de", "dm", "up_own"], rows_e)
    digJ = dict(zip(Js, dig))
    wupJ = dict(zip(Js, wup))
    dz = [(J, digJ[J], dm, wupJ[J]) for J, dm in L.dz_matched(n) if J in digJ]
    for J, e, dm, u in dz:
        log("  violet J=%-4g de_dig=%.5f dm_s=%+.4f; upper edge at the dataset's energy %.4f, ratio %.2f"
            % (J, e, dm, u, dm / u))
    wtable("land%d_dz.dat" % n, ["J", "de", "dm", "wup"], dz)
    check(all(dm > 0 for _, _, dm, _ in rows_e) and all(dm > 0 for _, _, dm, _ in dz),
          "caption: orange and violet all on the '+' side (dm_s > 0)")
    above = [(J, dm, u) for J, _, dm, u in rows_e if dm > u + 1e-12] + \
        [(J, dm, u) for J, _, dm, u in dz if dm > u + 1e-12]
    if n == 57:
        check(not above, "every marker lies below the drawn upper edge at its own energy")
    else:
        log("NOTE  markers above the drawn (inner) upper edge at their own energy: %s -- not an error: the inner "
            "edge is the hull of the stored states, a lower bound on the true upper edge; the data are drawn as "
            "they are" % [(J, round(dm, 4), round(u, 4)) for J, dm, u in above])
    log("  'close to the top surface': orange dm/upper edge in [%.2f, %.2f], violet in [%.2f, %.2f]"
        % (min(d / u for _, _, d, u in rows_e), max(d / u for _, _, d, u in rows_e),
           min(d / u for _, _, d, u in dz), max(d / u for _, _, d, u in dz)))
    # colour range: as the z range of fig_landscape (box)
    zt = [round(z, 6) + 0.0 for z in np.arange(-0.8, 0.81, 0.2) if B.z_min - 1e-9 <= z <= B.z_max + 1e-9]
    # two-slope diverging colour map (ColorBrewer RdBu, darkest steps dropped): red over [z_min, 0], white at the
    # ground-state value 0, blue over [0, z_max]; positions are (z - z_min) in units of 0.1
    reds = [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (247, 247, 247)]
    blues = [(247, 247, 247), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172)]
    stops = [(B.z_min + k * (0 - B.z_min) / 4, c) for k, c in enumerate(reds)] + \
        [(k * B.z_max / 4, c) for k, c in enumerate(blues)][1:]
    cmap = " ".join("rgb255(%.4fcm)=(%d,%d,%d)" % ((z - B.z_min) * 10, *c) for z, c in stops)
    with open(os.path.join(HERE, "values%d.tex" % n), "a", encoding="ascii", newline="\n") as f:
        f.write("\\newcommand{\\LdeMax}{%g}\n" % B.de_max)
        f.write("\\newcommand{\\LzMin}{%g}\n\\newcommand{\\LzMax}{%g}\n" % (B.z_min, B.z_max))
        f.write("\\newcommand{\\LzTicks}{%s}\n" % ",".join("%g" % z for z in zt))
        f.write("\\newcommand{\\LzTickLabels}{%s}\n" % ",".join("$0$" if z == 0 else "$%+.1f$" % z for z in zt))
        f.write("\\newcommand{\\LrawCols}{%d}\n" % len(Js))
        f.write("\\newcommand{\\Lemufrom}{%g}\n" % cap["emu_from"])
        f.write("\\newcommand{\\LJs}{%s}\n" % ",".join("%g" % j for j in Js))
        f.write("\\newcommand{\\LzZero}{%.6f}\n" % ((0 - B.z_min) / (B.z_max - B.z_min)))
        f.write("\\pgfplotsset{colormap={edgemap}{%s}}\n" % cmap)
    log("colour range of the edge maps: [%g, %g] (the z range of fig_landscape)" % (B.z_min, B.z_max))
    return w_main


# ----------------------------------------------------------------------------------------------- lattices
def lattice(n, cap):
    log("=" * 100)
    log("[figS_lattice%s]" % ("" if n == 57 else "_n115"))
    a = L.site_overorder(n, J_LAT)
    b, ms, inner = L.site_freedom(n, J_LAT)      # asserts mean(b) = m_s width of the two witnesses
    log("PASS  landscape_data.site_freedom(%d, 1.2): site average = m_s width of the witnesses (assert inside)" % n)
    pos, edges = L.layout(n)                     # asserts unit edge lengths
    log("PASS  landscape_data.layout(%d): unit edge lengths (assert inside)" % n)
    eta = np.array(L.graph(n)["eta"], float)
    e = C.meth_emu()[(n, J_LAT)]["var"]["primary"]
    ref = C.meth_ref()[(n, J_LAT)]
    da = np.abs(a - eta * (np.array(e["labels"]["Z"]) - np.array(ref["labels"]["Z"]))).max()
    check(da < 1e-12, "(a) per-site value = eta_i(<Z_i>_emulated - <Z_i>_DMRG), max |diff| = %.1e" % da)
    check(abs(a.mean() - e["err"]["dm_s"]) < 1e-12, "(a) site average = stored m_s bias %.6f" % e["err"]["dm_s"])
    check((a > 0).all() and len(a) == n, "caption: (a) positive at every site (%d of %d)" % ((a > 0).sum(), n))
    check(abs(b.mean() - (inner[1] - inner[0])) < 1e-9, "(b) site average = m_s width of summary_map.json at E_lo "
                                                        "(%.6f)" % (inner[1] - inner[0]))
    if n == 57:
        check("%+.4f" % a.mean() == "+0.2586", "SM text: +0.2586 at J_z = 1.2 (n = 57)")
    check("%.3f" % e["dE_site"] == cap["de_emu"], "caption: emulated state at de = %s (%.5f)" % (cap["de_emu"],
                                                                                                 e["dE_site"]))
    r = [x for x in L.rows(n) if abs(x["Jz"] - J_LAT) < 1e-9][0]
    check("%.4f" % (r["eps"]["lo"] / n) == "0.0096", "caption: witnesses at de = 0.0096 (E_lo = %.4f n)"
          % (r["eps"]["lo"] / n))
    vmax = np.ceil(max(a.max(), b.max()) * 10) / 10            # the colour range of fig_lattice.figure
    check(a.min() >= 0 and b.min() >= 0 and max(a.max(), b.max()) <= vmax, "all values inside the colour scale "
                                                                           "0..%.1f" % vmax)
    if n == 115:                                                # "greatest near two corners of the lattice"
        Lx = pos[:, 0].max()
        top = np.argsort(-b)[:8]
        dtl = np.hypot(pos[top, 0] - 0, pos[top, 1] - 0)
        dbr = np.hypot(pos[top, 0] - Lx, pos[top, 1] + Lx)
        near = np.minimum(dtl, dbr)
        check((near <= 3.5).all() and (dtl <= 3.5).any() and (dbr <= 3.5).any(),
              "caption: the 8 largest values of (b) lie within 3.5 bonds of the top-left or bottom-right corner "
              "(distances %s)" % np.round(near, 2).tolist())
    log("      (a) mean %.4f min %.4f max %.4f; (b) mean %.4f min %.4f max %.4f; colour scale 0..%.1f"
        % (a.mean(), a.min(), a.max(), b.mean(), b.min(), b.max(), vmax))
    for k, v in cap["printed"].items():
        val = {"amean": a.mean(), "amin": a.min(), "bmean": b.mean(), "bmin": b.min()}[k]
        check("%.3f" % val == v, "printed in the current figure: %s = %s" % (k, v))
    wtable("lat%d_nodes.dat" % n, ["i", "x", "y", "a", "b"], [(i, pos[i, 0], pos[i, 1], a[i], b[i]) for i in range(n)])
    wtable("lat%d_edges.dat" % n, ["p", "q", "x", "y", "dx", "dy"],
           [(p, q, pos[p, 0], pos[p, 1], pos[q, 0] - pos[p, 0], pos[q, 1] - pos[p, 1]) for p, q in edges])
    log("      %d sites, %d edges, drawing %g x %g bonds" % (n, len(edges), np.ptp(pos[:, 0]), np.ptp(pos[:, 1])))
    with open(os.path.join(HERE, "values%d.tex" % n), "a", encoding="ascii", newline="\n") as f:
        f.write("\\newcommand{\\Aavg}{%.3f}\n\\newcommand{\\Amin}{%.3f}\n" % (a.mean(), a.min()))
        f.write("\\newcommand{\\Bavg}{%.3f}\n\\newcommand{\\Bmin}{%.3f}\n" % (b.mean(), b.min()))
        f.write("\\newcommand{\\Vmax}{%.1f}\n\\newcommand{\\Nsites}{%d}\n\\newcommand{\\Jlat}{%.1f}\n"
                % (vmax, n, J_LAT))
        f.write("\\newcommand{\\Lside}{%g}\n" % np.ptp(pos[:, 0]))


def main():
    for n in (57, 115):
        with open(os.path.join(HERE, "values%d.tex" % n), "w", encoding="ascii", newline="\n") as f:
            f.write("%% written by export_sm3d.py -- numbers printed in the n = %d figures\n" % n)
    log("export_sm3d.py -- data of the 3-D Supplemental figures (inputs via ../fig_landscape.py, "
        "../landscape_data.py, ../common.py; ROOT = %s)" % C.ROOT)
    for n in (57, 115):
        w = L.check_inner(n)
        check(w == 0.0, "landscape_data.check_inner(%d): inner hull = summary_map.json at E_lo, E_dig, E_up of every "
                        "m_s row (max |diff| = %.1e)" % (n, w))
    landscape(57, dict(de_max=0.024, emu_from=1.8))
    landscape(115, dict(de_max=0.016, J_set=2.5, emu_from=3.0))
    lattice(57, dict(de_emu="0.043", printed=dict(amean="0.259", amin="0.165", bmean="0.462", bmin="0.264")))
    lattice(115, dict(de_emu="0.079", printed=dict(amean="0.301", amin="0.206", bmean="0.422", bmin="0.195")))
    log("=" * 100)
    log("ALL CHECKS PASSED")
    with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
