"""Export the data of main Fig. 2 (fig1_composite) for the native PGFPlots version (fig_composite.tex).

  cd paper/figures/pgf_composite && python -B export_composite.py

Nothing physical is recomputed.  Every array comes from the loaders of the existing figure scripts, imported as they
are (../landscape_data.py, ../fig1_composite.py, ../common.py; they read the deposited outputs read-only):

  (a) fig1_composite.relief_data(): the (J_z, de) grid of log10(w / tau), w = inner width of the m_s window (16
      computed couplings x 150 log-spaced de), the dataset's digitized error de_dig = eps.dig / n and the ood flags.
      For display the grid is resampled every 0.05 in J_z by straight interpolation between computed couplings (the
      rule of fig1_composite.refine, checked below); the width = tau contour is traced on that interpolation.
  (b) summary_map.json rows (at_dig.ratio_out, ood), jstar.57_m_s_r1.J_star_central and the rings of
      rigor/outputs/results_v2.json, read exactly as in fig1_composite.main().
  (c, d) fig1_composite.device_values() (its assertions: per-site values = eta_i(<Z_i> - <Z_i>_DMRG), mean = stored
      Delta m_s) and landscape_data.layout(57) (unit-length heavy-hex drawing, asserted there).

Writes only into this folder: *.dat, composite_values.tex (numbers printed in the figure) and export_check.txt.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.abspath(os.path.join(HERE, ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, FIG)

import common as C                 # noqa: E402
import landscape_data as L         # noqa: E402
import fig1_composite as F         # noqa: E402  (imports pyvista/vtk at module level; nothing is rendered here)

N = F.N
DE_STEP = 2          # drawn map: every 2nd of the 150 de rows (pdflatex main memory); 1 = all rows (lualatex)
LOG = []


def log(s=""):
    print(s)
    LOG.append(s)


def check(cond, what):
    log(("PASS  " if cond else "FAIL  ") + what)
    assert cond, what


def wtable(name, header, rows, blocks=None):
    """rows: list of tuples; blocks: list of lists of tuples (written with a blank line between blocks)"""
    p = os.path.join(HERE, name)
    with open(p, "w", encoding="ascii", newline="\n") as f:
        f.write(" ".join(header) + "\n")
        for blk in (blocks if blocks is not None else [rows]):
            for r in blk:
                f.write(" ".join(fmt(v) for v in r) + "\n")
            if blocks is not None:
                f.write("\n")
    return p


def fmt(v):
    if isinstance(v, (bool, np.bool_)):
        return "1" if v else "0"
    if isinstance(v, (int, np.integer)):
        return "%d" % v
    return "%.12g" % v


def interp_J(Js, V, Jq):
    """straight interpolation between computed couplings, column by column (the rule of fig1_composite.refine)"""
    i = np.clip(np.searchsorted(Js, Jq, side="right") - 1, 0, len(Js) - 2)
    t = (Jq - Js[i]) / (Js[i + 1] - Js[i])
    return (1 - t)[:, None] * V[i] + t[:, None] * V[i + 1]


def main():
    log("export_composite.py -- data of main Fig. 2 (n = %d) for fig_composite.tex" % N)
    log("inputs via ../fig1_composite.py, ../landscape_data.py, ../common.py (ROOT = %s)" % C.ROOT)
    log("")

    # ------------------------------------------------------------------------------------------- built-in checks
    log("[built-in checks of the figure scripts]")
    w_inner = L.check_inner(N)
    check(w_inner == 0.0, "landscape_data.check_inner(57): inner hull = summary_map.json at E_lo, E_dig, E_up of "
                          "every m_s row (max |diff| = %.2e)" % w_inner)
    D = F.relief_data()          # asserts the validity mask of the whole grid
    log("PASS  fig1_composite.relief_data(): grid valid everywhere (assert ok.all() inside)")
    vals, moved = F.device_values()   # asserts per-site = eta_i(<Z_i> - <Z_i>_DMRG) and mean = stored dm_s
    log("PASS  fig1_composite.device_values(): its two assertions (per-site formula, mean = stored Delta m_s)")
    pos, edges = L.layout(N)     # asserts unit edge lengths
    log("PASS  landscape_data.layout(57): every heavy-hex edge has unit length (assert inside)")
    log("")

    # ------------------------------------------------------------------------------------------- (a) the map
    log("[panel (a): map of log10(width / tau) over (J_z, de)]")
    Js, de, lw = D["Js"], D["de"], D["lw"]
    log("relief grid: %d computed couplings x %d de values (%.4g .. %.4g, log-spaced); log10(w/tau) in [%.4f, %.4f]"
        % (len(Js), len(de), de[0], de[-1], lw.min(), lw.max()))
    log("couplings: %s" % ", ".join("%g" % j for j in Js))
    wtable("a_grid_raw.dat", ["J", "de", "lw", "w_over_tau"],
           [(Js[i], de[k], lw[i, k], 10 ** lw[i, k]) for k in range(len(de)) for i in range(len(Js))])
    # display grid: every 0.05 in J (contains every computed coupling), straight between computed couplings
    Jd = np.round(Js[0] + 0.05 * np.arange(int(round((Js[-1] - Js[0]) / 0.05)) + 1), 10)
    lwd = interp_J(Js, lw, Jd)
    hit = [int(np.argmin(np.abs(Jd - j))) for j in Js]
    check(all(abs(Jd[h] - j) < 1e-9 for h, j in zip(hit, Js)), "display grid contains every computed coupling")
    check(np.abs(lwd[hit] - lw).max() == 0.0, "display grid equals the relief grid at the computed couplings")
    Jf, lwf = F.refine(Js, lw)                       # the relief mesh of the current figure (k = 14)
    dref = np.abs(interp_J(Js, lw, Jf) - lwf).max()
    check(dref < 1e-12, "same interpolation as fig1_composite.refine (relief mesh), max |diff| = %.1e" % dref)
    # drawn grid: every DE_STEP-th de row (regular downsampling, for pdflatex's main memory; the full 150 rows of
    # the 99-column grid exceed it).  With matrix plot* every cell is centred on its sample, so the top cell
    # (row 148) ends exactly at de[149] = the top of the map.
    kk = np.arange(0, len(de), DE_STEP)
    check(np.allclose(np.log10(de[kk[-1]]) + 0.5 * DE_STEP * np.diff(np.log10(de)).mean(), np.log10(de[-1]))
          or kk[-1] == len(de) - 1, "downsampled rows still cover the whole de range")
    wtable("a_map.dat", ["J", "de", "lw"],
           [(Jd[i], de[k], lwd[i, k]) for k in kk for i in range(len(Jd))])
    log("a_map.dat (drawn): %d J columns (every 0.05) x %d de rows (every %d-th of the 150 rows) = %d cells; "
        "full-resolution relief grid in a_grid_raw.dat" % (len(Jd), len(kk), DE_STEP, len(Jd) * len(kk)))
    # width = tau contour (log10 w/tau = 0) on the same interpolation, traced in (J, log10 de)
    import contourpy
    Jc = np.round(Js[0] + 0.01 * np.arange(int(round((Js[-1] - Js[0]) / 0.01)) + 1), 10)
    lwc = interp_J(Js, lw, Jc)
    lines = contourpy.contour_generator(np.log10(de), Jc, lwc, name="serial").lines(0.0)
    segs = [[(p[1], 10 ** p[0]) for p in seg] for seg in lines]
    wtable("a_contour_tau.dat", ["J", "de"], None, blocks=segs)
    log("width = tau contour: %d segment(s), %s points" % (len(segs), [len(s) for s in segs]))
    for s in segs:
        log("  from (J=%.3f, de=%.3g) to (J=%.3f, de=%.3g)" % (s[0][0], s[0][1], s[-1][0], s[-1][1]))
    # dataset line: de_dig at the computed couplings of the relief; grey = conditional floor (ood rows) up to the
    # first in-distribution coupling, black from there on (as P[:k0+1] / P[k0:] in fig1_composite.render_relief)
    dig, lwdig, ood = D["dig"], D["lwd"], D["ood"]
    k0 = int(np.argmax(~ood))
    check(ood[:k0].all() and not ood[k0:].any(), "ood rows are the first %d couplings (J_z <= %g)" % (k0, Js[k0 - 1]))
    wtable("a_line_floor.dat", ["J", "de", "lw_inner"], [(Js[i], dig[i], lwdig[i]) for i in range(k0 + 1)])
    wtable("a_line_data.dat", ["J", "de", "lw_inner"], [(Js[i], dig[i], lwdig[i]) for i in range(k0, len(Js))])
    for i in range(len(Js)):
        log("  line J=%-4g de_dig=%.6f inner w/tau=%.4f %s" % (Js[i], dig[i], 10 ** lwdig[i],
                                                              "(floor)" if ood[i] else ""))
    check(dig.max() <= de[-1] and dig.min() >= de[0], "dataset line inside the map (de range)")
    # where the line enters the teal region: inner width at de_dig, straight between computed couplings
    j = int(np.argmax(lwdig <= 0))
    Jx = Js[j - 1] + (Js[j] - Js[j - 1]) * lwdig[j - 1] / (lwdig[j - 1] - lwdig[j])
    check((lwdig[:j] > 0).all() and (lwdig[j:] <= 0).all(), "the line crosses width = tau once")
    jstar = C.map_summary()["jstar"]["%d_m_s_r1" % N]["J_star_central"]
    check(abs(jstar - F.JSTAR) < 1e-12 and abs(jstar - 3.2) < 1e-12, "J* = %g (caption: J* = 3.2)" % jstar)
    check(round(Jx, 1) == round(jstar, 1), "the drawn line meets the contour at J_z = %.3f, i.e. at J* = 3.2 to "
                                           "the printed digit (between computed %g and %g)" % (Jx, Js[j - 1], Js[j]))
    log("")

    # ------------------------------------------------------------------------------------------- (b) the slice
    log("[panel (b): width at the dataset's energy]")
    S = C.map_summary()
    rows = sorted((r for r in S["rows"] if r["n"] == N and r["label"] == "m_s"), key=lambda r: r["Jz"])
    J = np.array([r["Jz"] for r in rows])
    w = np.array([r["at_dig"]["ratio_out"] for r in rows])
    oodb = np.array([bool(r.get("ood")) for r in rows])
    rig = C.rj(os.path.join(C.ROOT, "phase3", "full_runs", "rigor", "outputs", "results_v2.json"))
    Jr = sorted(r["Jz"] for r in rig["rows"] if r["n"] == N and r["label"] == "m_s" and r["certified"])
    check(all(min(abs(J - x)) < 1e-9 for x in Jr) and len(Jr) == 6, "6 ringed points, all computed: %s" % Jr)
    ring = np.array([any(abs(x - y) < 1e-9 for y in Jr) for x in J])
    wtable("b_line.dat", ["J", "w", "ood", "ringed"], list(zip(J, w, oodb, ring)))
    wtable("b_filled.dat", ["J", "w"], [(a, b) for a, b, o in zip(J, w, oodb) if not o])
    wtable("b_open.dat", ["J", "w"], [(a, b) for a, b, o in zip(J, w, oodb) if o])
    wtable("b_ringed.dat", ["J", "w"], [(a, b) for a, b, r in zip(J, w, ring) if r])
    for a, b, o, r in zip(J, w, oodb, ring):
        log("  J=%-4g w_out/tau=%.4f %s%s" % (a, b, "open (floor)" if o else "filled", "  ringed" if r else ""))
    check(w.min() > 0.15 and w.max() < 30, "all points inside the y range 0.15..30 of the current panel")
    i32 = int(np.argmin(abs(J - jstar)))
    check(w[i32] <= 1 and (w[J < jstar] > 1).all() and (w[J >= jstar] <= 1).all(),
          "w_out <= tau exactly from J* on (w(3.2) = %.4f, w(3.0) = %.4f)" % (w[i32], w[J < jstar][-1]))
    taus = np.array([r["tau"] / abs(r["O_GS"]) for r in rows])
    check(np.allclose(taus, 0.06, rtol=0, atol=1e-12), "tau = 0.06 |m_s,GS| in every row (caption)")
    log("")

    # ------------------------------------------------------------------------------------------- (c, d) lattices
    log("[panels (c), (d): per-site excess of order at J_z = 1.2]")
    eta = np.array(L.graph(N)["eta"], float)
    dev = C.rj(os.path.join(F.QOUT, "device_A_J1.2.json"))["var"]["rec"]
    ctl = C.rj(os.path.join(F.QOUT, "control_J1.2.json"))["var"]["rec"]
    ref = C.rj(os.path.join(F.QPU, "refs", "ref_n57_J1.2.json"))
    out = {}
    for name, v in (("device", dev), ("control", ctl)):
        s, dm = vals[name][0], vals[name][1]
        rec = eta * (np.array(v["labels"]["Z"]) - np.array(ref["labels"]["Z"]))
        dd = np.abs(s - rec).max()
        check(dd < 1e-12, "%s: per-site value = eta_i(<Z_i> - <Z_i>_DMRG), max |diff| = %.1e" % (name, dd))
        dmean = abs(s.mean() - v["err"]["dm_s"])
        check(dmean < 1e-12, "%s: mean of the 57 values = stored Delta m_s = %.6f (|diff| = %.1e)"
              % (name, v["err"]["dm_s"], dmean))
        check(len(s) == N and (s > 0).all(), "%s: all %d sites positive" % (name, len(s)))
        check(s.max() <= 0.5, "%s: largest site %.4f inside the colour scale 0..0.5" % (name, s.max()))
        out[name] = dict(s=s, dm=dm, smin=s.min())
        log("      %s: Delta m_s = %+.4f, smallest %+.4f, largest %+.4f" % (name, dm, s.min(), s.max()))
    check("%+.3f" % out["device"]["dm"] == "+0.310", "caption (c): Delta m_s = +0.310")
    check("%+.3f" % out["control"]["dm"] == "+0.253", "caption (d): Delta m_s = +0.253")
    check("%+.3f" % out["device"]["smin"] == "+0.202", "figure (c): smallest site +0.202")
    check("%+.3f" % out["control"]["smin"] == "+0.160", "figure (d): smallest site +0.160")
    dn = out["device"]["dm"] - out["control"]["dm"]
    check("%+.3f" % dn == "+0.057", "caption (d): the device noise adds %+.4f (+0.057)" % dn)
    check(len(moved) == 4, "4 routed sites: %s" % moved)
    check(all(0 <= k < N for k in moved), "routed sites are graph indices")
    check(len(pos) == N and np.isfinite(pos).all(), "heavy-hex d = 5: %d nodes placed, %d edges"
          % (len(pos), len(edges)))
    wtable("cd_nodes.dat", ["i", "x", "y", "device", "control", "routed"],
           [(i, pos[i, 0], pos[i, 1], out["device"]["s"][i], out["control"]["s"][i], int(i in moved))
            for i in range(N)])
    wtable("cd_edges.dat", ["a", "b", "x", "y", "dx", "dy"],   # one row per edge (drawn as a quiver without tips)
           [(a, b, pos[a, 0], pos[a, 1], pos[b, 0] - pos[a, 0], pos[b, 1] - pos[a, 1]) for a, b in edges])
    wtable("cd_routed.dat", ["i", "x", "y"], [(k, pos[k, 0], pos[k, 1]) for k in moved])
    dmin = min(np.linalg.norm(pos[a] - pos[b]) for a in range(N) for b in range(a + 1, N))
    log("      smallest distance between two sites in the drawing: %.3f (bond length 1)" % dmin)
    log("")

    # ------------------------------------------------------------------------------------------- numbers for TeX
    p = os.path.join(HERE, "composite_values.tex")
    with open(p, "w", encoding="ascii", newline="\n") as f:
        f.write("%% written by export_composite.py -- numbers printed in fig_composite.tex\n")
        f.write("\\newcommand{\\Jstar}{%g}\n" % jstar)
        f.write("\\newcommand{\\DmsDev}{%+.3f}\n" % out["device"]["dm"])
        f.write("\\newcommand{\\MinDev}{%+.3f}\n" % out["device"]["smin"])
        f.write("\\newcommand{\\DmsCtl}{%+.3f}\n" % out["control"]["dm"])
        f.write("\\newcommand{\\MinCtl}{%+.3f}\n" % out["control"]["smin"])
        f.write("\\newcommand{\\NRouted}{%d}\n" % len(moved))
        f.write("\\newcommand{\\MapCols}{%d}\n" % len(Jd))
    log("wrote composite_values.tex, a_grid_raw.dat, a_map.dat, a_contour_tau.dat, a_line_floor.dat, "
        "a_line_data.dat, b_line.dat, b_filled.dat, b_open.dat, b_ringed.dat, cd_nodes.dat, cd_edges.dat, "
        "cd_routed.dat")
    log("ALL CHECKS PASSED")
    with open(os.path.join(HERE, "export_check.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
