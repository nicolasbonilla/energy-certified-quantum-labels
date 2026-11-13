"""Second, independent reading of the energy figures of arXiv 2606.15983 (IBM): Fig. 2 (left), Supp. Fig. 9 and
Fig. 4 (left). Laptop only; numpy + PIL; the PNG files are read as data (run with python -I, paths as arguments).

Method (different from the first reading, pilot/PRIOR_ART_CHECK.md §3, which used two major ticks per axis, RGB colour
boxes and the median row of the densest 25-row window in a +-4 px column band):
  1. Axis calibration by least squares on ALL detected tick marks (major and minor, on both opposite frame sides):
     log10(value) = a + b*row for the log axes, Jz = c + d*col for the linear axes. Tick values are assigned by
     nearest prediction from a provisional fit on the majors, then the fit is redone with every tick (residuals
     reported).
  2. Markers located by 2D shape matching: a hue/saturation mask of the series colour is scored with a synthetic
     filled template of the marker shape (size measured on the figure's own legend marker):
        score(x, y) = mean(mask inside the template) - mean(mask in a 3 px ring around it),
     maximised over x in [x(Jz) - 3, x(Jz) + 3] and every row outside the legend, for Supp. Fig. 9 (where circles and
     diamonds of the same colours are present) only among positions whose corner patches are filled; the row is refined by a parabola through the three best rows.
     Hollow markers (white interior), other shapes and the connecting lines score low; score < 0.30 (0.20 for the
     dense Fig. 4) = hidden or unreadable.
  python -I digitize2.py <dl_dir> <out.json>
"""
import json
import sys
import numpy as np
from PIL import Image


def load(path):
    im = Image.open(path).convert("RGB")
    rgb = np.asarray(im).astype(float) / 255.0
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255.0
    return rgb, hsv


def runs(idx):
    """Group sorted integer indices into runs; return their centres."""
    out = []
    if not len(idx):
        return out
    start = prev = idx[0]
    for i in list(idx[1:]) + [None]:
        if i is not None and i == prev + 1:
            prev = i
            continue
        out.append(((start + prev) / 2.0, prev - start + 1))
        if i is not None:
            start = prev = i
    return out


def ticks(rgb, frame, side, minlen=4):
    """Inward tick marks on one frame side. Returns [(centre, length)] (centre in rows or cols)."""
    fx0, fx1, fy0, fy1 = frame
    blk = rgb.sum(axis=2) < 250 / 255.0 * 3 * 0.33
    res = []
    if side in ("left", "right"):
        x = fx0 + 3 if side == "left" else fx1 - 3
        step = 1 if side == "left" else -1
        for y in range(fy0 + 4, fy1 - 3):
            L = 0
            while blk[y, x + step * L] and L < 60:
                L += 1
            if minlen <= L < 60:
                res.append((y, L))
    else:
        y = fy1 - 3 if side == "bottom" else fy0 + 3
        step = -1 if side == "bottom" else 1
        for x in range(fx0 + 4, fx1 - 3):
            L = 0
            while blk[y + step * L, x] and L < 60:
                L += 1
            if minlen <= L < 60:
                res.append((x, L))
    # group consecutive positions
    pos = [p for p, _ in res]
    lens = dict(res)
    out = []
    for c, w in runs(pos):
        if w > 8:                      # not a tick (a marker or a line touching the frame)
            continue
        lo, hi = int(round(c - (w - 1) / 2)), int(round(c + (w - 1) / 2))
        out.append((c, max(lens.get(k, 0) for k in range(lo, hi + 1))))
    return out


def calib_log(rgb, frame, top_major_decade):
    """Least-squares log axis from all left+right ticks. Returns (a, b, residual_rms_px, n_ticks, table)."""
    T = ticks(rgb, frame, "left") + ticks(rgb, frame, "right")
    Ls = np.array([L for _, L in T])
    major_len = Ls.max()
    majors = sorted(set(round(c, 1) for c, L in T if L >= 0.75 * major_len))
    # merge left/right duplicates
    mj = []
    for c in majors:
        if not mj or abs(c - mj[-1][0]) > 3:
            mj.append([c])
        else:
            mj[-1].append(c)
    mj = [np.mean(g) for g in mj]
    dec = [top_major_decade - k for k in range(len(mj))]
    b = np.polyfit(mj, dec, 1) if len(mj) >= 2 else None
    # provisional: log10 v = p0*row + p1; assign every tick to the nearest candidate value k*10^m
    cands = [np.log10(k * 10.0 ** m) for m in range(-4, 4) for k in range(1, 10)]
    rows, vals = [], []
    for c, L in T:
        pv = b[0] * c + b[1]
        nearest = min(cands, key=lambda v: abs(v - pv))
        if abs(nearest - pv) < 0.02:
            rows.append(c); vals.append(nearest)
    p = np.polyfit(rows, vals, 1)
    res = np.array(vals) - np.polyval(p, rows)
    rms_px = float(np.sqrt(np.mean((res / p[0]) ** 2)))
    return p, rms_px, len(rows), list(zip(rows, [10 ** v for v in vals]))


def calib_lin(rgb, frame, labels):
    """Linear Jz axis from bottom+top major ticks with the given labels (left to right)."""
    T = ticks(rgb, frame, "bottom") + ticks(rgb, frame, "top")
    cols = sorted(c for c, _ in T)
    grp = []
    for c in cols:
        if not grp or abs(c - grp[-1][0]) > 3:
            grp.append([c])
        else:
            grp[-1].append(c)
    centres = [np.mean(g) for g in grp]
    assert len(centres) == len(labels), (centres, labels)
    xs, js = [], []
    for g, J in zip(grp, labels):
        for c in g:
            xs.append(c); js.append(J)
    p = np.polyfit(xs, js, 1)
    res = np.array(js) - np.polyval(p, xs)
    return p, float(np.sqrt(np.mean((res / p[0]) ** 2))), len(xs), list(zip(centres, labels))


def series_mask(hsv, rgb, colour):
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    if colour == "green":
        return (h > 0.22) & (h < 0.42) & (s > 0.25) & (v > 0.25)
    if colour == "purple":
        return (h > 0.68) & (h < 0.84) & (s > 0.18) & (v > 0.35)
    raise ValueError(colour)


def template(shape, size):
    """Filled synthetic marker on a (2R+1)^2 grid, R = ceil(size/2) + 4; returns (inside, ring) boolean arrays."""
    R = int(np.ceil(size / 2.0)) + 4
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(float)
    h = size / 2.0
    if shape == "square":
        inside = (np.abs(xx) <= h) & (np.abs(yy) <= h)
    elif shape == "tri_down":                     # matplotlib 'v': apex down, bbox centre at the data point
        # vertices (0, +h) bottom apex (rows grow downward), (-h, -h), (+h, -h)
        frac = (yy + h) / (2 * h)                 # 0 at the top edge, 1 at the apex
        inside = (yy >= -h) & (yy <= h) & (np.abs(xx) <= h * (1 - frac))
    else:
        raise ValueError(shape)
    dil = np.zeros_like(inside)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                dil |= np.roll(np.roll(inside, dy, 0), dx, 1)
    ring = dil & ~inside
    return inside, ring


def measure_legend_marker(mask, box):
    """Marker size from the legend: extent of the mask in the box, excluding the horizontal legend line rows."""
    x0, y0, x1, y1 = box
    sub = mask[y0:y1, x0:x1]
    rows = sub.sum(axis=1)
    full = rows >= 0.8 * (x1 - x0)                 # rows of the legend line through the marker
    cols = sub[~full].sum(axis=0)
    xs = np.nonzero(cols > 0)[0]
    ys = np.nonzero((rows > 0) & ~full)[0]
    # marker rows: those with partial width; size = max(col extent, row extent of the marker)
    return float(xs.max() - xs.min() + 1), float(ys.max() - ys.min() + 1)


def corners(shape, size):
    """Small patches just inside the corners of the marker's bounding box that a filled marker of this shape covers
    and a circle or a diamond of similar size does not (shape discrimination)."""
    h = int(round(size / 2.0)) - 2
    pts = []
    for cy in (-h, h) if shape == "square" else (-h,):
        for cx in (-h, h):
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    pts.append((cy + dy, cx + dx))
    return np.array(pts)


def locate(mask, inside, ring, corner_pts, xc, yrange, excl, dx=3, min_corner=0.6):
    """Best (x, y) by score = mean(mask in template) - mean(mask in ring), among positions whose corner patches are
    filled (>= min_corner). excl: list of (x0, y0, x1, y1) boxes excluded (legend)."""
    from scipy.ndimage import correlate
    R = inside.shape[0] // 2
    x0, x1 = int(round(xc)) - dx - R - 2, int(round(xc)) + dx + R + 3
    y0, y1 = yrange
    sub = mask[y0:y1, x0:x1].astype(float)
    sin = correlate(sub, inside.astype(float) / inside.sum(), mode="constant", cval=0.0)
    srg = correlate(sub, ring.astype(float) / ring.sum(), mode="constant", cval=0.0)
    cm = np.zeros((2 * R + 1, 2 * R + 1))
    for (cy, cx) in corner_pts:
        cm[cy + R, cx + R] = 1.0
    scn = correlate(sub, cm / cm.sum(), mode="constant", cval=0.0)
    score = sin - srg
    valid = np.zeros_like(score, dtype=bool)
    xs = np.arange(x0, x1)
    ys = np.arange(y0, y1)
    colok = (xs >= int(round(xc)) - dx) & (xs <= int(round(xc)) + dx)
    rowok = (ys >= y0 + R) & (ys < y1 - R)
    valid[np.ix_(rowok, colok)] = True
    for (ex0, ey0, ex1, ey1) in excl:
        valid[np.ix_((ys >= ey0 - R) & (ys <= ey1 + R), (xs >= ex0 - R) & (xs <= ex1 + R))] = False
    valid &= scn >= min_corner
    if not valid.any():
        return None, None, None
    sc = np.where(valid, score, -9.0)
    iy, ix = np.unravel_index(np.argmax(sc), sc.shape)
    s0 = sc[iy, ix]
    sm = sc[iy - 1, ix] if iy > 0 and sc[iy - 1, ix] > -9 else s0
    sp = sc[iy + 1, ix] if iy + 1 < sc.shape[0] and sc[iy + 1, ix] > -9 else s0
    den = sm - 2 * s0 + sp
    d = 0.5 * (sm - sp) / den if den < 0 else 0.0
    return float(xs[ix]), float(ys[iy] + max(-1.0, min(1.0, d))), float(s0)


MIN_SCORE = 0.30          # below this the marker is taken as hidden (e.g. n = 57 gap markers under n = 115 ones)
FIGS = {
    # name: file, frame (x0, x1, y0, y1), top major decade, x labels, series: (key, colour, shape, legend box, Jz list)
    "fig2_left": dict(file="fig2v6.png", frame=(104, 698, 15, 1014), top_decade=0, xlabels=[2, 4, 6],
                      exclude=[(385, 30, 680, 165)],
                      series=[("ratio_n57", "green", "tri_down", (420, 40, 470, 95)),
                              ("ratio_n115", "purple", "square", (420, 100, 470, 150))],
                      J=[round(1.6 + 0.1 * k, 1) for k in range(45)]),
    "supp_fig9": dict(file="suppfig_energy_super_comparisonv5.png", frame=(372, 1671, 68, 947), top_decade=1,
                      min_corner=0.35,
                      xlabels=[2, 3, 4, 5, 6],
                      series=[("ratio_n57", "green", "tri_down", (1745, 425, 1835, 500)),
                              ("ratio_n115", "purple", "square", (1745, 725, 1835, 800))],
                      J=[round(1.6 + 0.1 * k, 1) for k in range(45)]),
    "fig4_left": dict(file="fig4v9.png", frame=(100, 591, 114, 1125), top_decade=0, xlabels=[1, 2, 4, 6],
                      exclude=[(310, 985, 575, 1110)], min_score=0.20,
                      min_score_series={"gap_n57": 0.10},     # n = 57 markers partly hidden under n = 115 ones
                      series=[("gap_n115", "purple", "square", None), ("gap_n57", "green", "tri_down", None)],
                      J=[round(1.1 + 0.1 * k, 1) for k in range(50)]),
}


def main(dl, outp):
    out = {}
    for name, F in FIGS.items():
        rgb, hsv = load(dl + "/" + F["file"])
        py, rms_y, nty, tab_y = calib_log(rgb, F["frame"], F["top_decade"])
        px, rms_x, ntx, tab_x = calib_lin(rgb, F["frame"], F["xlabels"])
        res = dict(calib=dict(log10v_per_row=float(py[0]), log10v_at_row0=float(py[1]), rms_px_y=rms_y, n_ticks_y=nty,
                              Jz_per_col=float(px[0]), Jz_at_col0=float(px[1]), rms_px_x=rms_x, n_ticks_x=ntx,
                              x_majors=tab_x))
        fx0, fx1, fy0, fy1 = F["frame"]
        for key, colour, shape, lbox in F["series"]:
            mask = series_mask(hsv, rgb, colour)
            if lbox is not None:
                w, h = measure_legend_marker(mask, lbox)
                size = max(w, h)
            else:
                size = None
            if size is None:                       # Fig. 4: size from the Fig. 2 legend scaled by the axis scale
                size = 20.0 if shape == "square" else 21.0
            inside, ring = template(shape, size)
            cpts = corners(shape, size)
            vals = {}
            for J in F["J"]:
                xc = (J - px[1]) / px[0]
                x, y, sc = locate(mask, inside, ring, cpts, xc, (fy0 + 4, fy1 - 4), F.get("exclude", []),
                                  min_corner=F.get("min_corner", 0.0))
                if x is None or sc < F.get("min_score_series", {}).get(key, F.get("min_score", MIN_SCORE)):
                    vals["%.1f" % J] = dict(value=None, score=sc)
                    continue
                v = 10 ** (py[0] * y + py[1])
                vals["%.1f" % J] = dict(value=float(v), row=y, col=x, score=sc, Jz_at_col=float(np.polyval(px, x)))
            res[key] = dict(marker_size_px=size, shape=shape, colour=colour, points=vals)
        out[name] = res
        print(name, "y-ticks %d rms %.2f px; x-ticks %d rms %.2f px" % (nty, rms_y, ntx, rms_x))
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
