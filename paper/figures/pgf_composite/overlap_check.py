"""Geometric check of fig_composite.pdf: does any text touch a stroked line, a marker or another text?

  cd paper/figures/pgf_composite && python -B overlap_check.py      -> overlap_check.txt

Text boxes are the glyph boxes of PyMuPDF (font ascent/descent, shrunk vertically to 70 % around their centre so that
ascender space does not count); obstacles are every stroked segment or curve (inflated by half its line width) and
every small filled shape (markers, lattice nodes).  Large fills (map cells, the certified band, white label boxes,
colour bars) are backgrounds and are not obstacles.  A hit is reported with the text and the distance in pt.
"""
import os

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
SMALL = 30.0          # pt: filled shapes smaller than this in both directions are markers / nodes
VSHRINK = 0.70


def seg_rect_dist(p, q, r):
    """distance between segment pq and rectangle r (0 if they intersect), sampled finely"""
    best = 1e9
    n = 40
    for k in range(n + 1):
        t = k / n
        x, y = p.x + t * (q.x - p.x), p.y + t * (q.y - p.y)
        dx = max(r.x0 - x, 0, x - r.x1)
        dy = max(r.y0 - y, 0, y - r.y1)
        best = min(best, (dx * dx + dy * dy) ** 0.5)
    return best


def bezier_pts(p0, p1, p2, p3, n=16):
    out = []
    for k in range(n + 1):
        t = k / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t * t
        d = t ** 3
        out.append(fitz.Point(a * p0.x + b * p1.x + c * p2.x + d * p3.x, a * p0.y + b * p1.y + c * p2.y + d * p3.y))
    return out


def main():
    doc = fitz.open(os.path.join(HERE, "fig_composite.pdf"))
    pg = doc[0]
    words = []
    for b in pg.get_text("rawdict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                chars = [c for c in sp["chars"] if c["c"].strip()]
                if not chars:
                    continue
                txt = "".join(c["c"] for c in sp["chars"])
                for c in chars:
                    r = fitz.Rect(c["bbox"])
                    h = r.height * VSHRINK
                    cy = (r.y0 + r.y1) / 2
                    words.append((txt, fitz.Rect(r.x0, cy - h / 2, r.x1, cy + h / 2)))
    segs, blobs = [], []
    n_cells = 0
    for d in pg.get_drawings():
        stroked = d.get("type") in ("s", "fs")
        filled = d.get("type") in ("f", "fs")
        hw = (d.get("width") or 0.4) / 2
        rr = d["rect"]
        kinds = set(it[0] for it in d["items"])
        if filled and "c" not in kinds and (not stroked or d.get("fill") == d.get("color")):
            n_cells += 1           # map cell (filled and stroked in its own colour), band, label box: background
            continue
        if filled and "c" in kinds and rr.width < SMALL and rr.height < SMALL:
            blobs.append(rr)       # filled marker or lattice node
            continue
        if not stroked:
            continue
        for it in d["items"]:
            if it[0] == "qu":
                q = it[1]
                for a, b in ((q.ul, q.ur), (q.ur, q.lr), (q.lr, q.ll), (q.ll, q.ul)):
                    segs.append((a, b, hw))
            if it[0] == "l":
                segs.append((it[1], it[2], hw))
            elif it[0] == "c":
                pts = bezier_pts(*it[1:5])
                segs += [(a, b, hw) for a, b in zip(pts[:-1], pts[1:])]
            elif it[0] == "re":
                q = it[1]
                for a, b in ((q.tl, q.tr), (q.tr, q.br), (q.br, q.bl), (q.bl, q.tl)):
                    segs.append((a, b, hw))
    hits = []
    for txt, r in words:
        for p, q, hw in segs:
            if min(p.x, q.x) > r.x1 + 3 or max(p.x, q.x) < r.x0 - 3 or min(p.y, q.y) > r.y1 + 3 or \
                    max(p.y, q.y) < r.y0 - 3:
                continue
            dd = seg_rect_dist(p, q, r) - hw
            if dd < 0.3:
                hits.append((txt, "line", round(dd, 2), tuple(round(v, 1) for v in r)))
        for b in blobs:
            if r.intersects(b):
                hits.append((txt, "marker", 0, tuple(round(v, 1) for v in r)))
    # text against text (different spans)
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            a, b = words[i][1], words[j][1]
            if words[i][0] != words[j][0] and a.intersects(b) and min(a.x1, b.x1) - max(a.x0, b.x0) > 1.5:
                # (an overlap of <= 1.5 pt in x is a subscript tucked under its letter, e.g. J_z, m_s)
                hits.append((words[i][0] + " | " + words[j][0], "text", 0, tuple(round(v, 1) for v in words[i][1])))
    uniq = sorted(set((h[0], h[1]) for h in hits))
    out = ["overlap_check.py on fig_composite.pdf: %d glyphs, %d stroked segments, %d markers/nodes, %d background "
           "fills ignored" % (len(words), len(segs), len(blobs), n_cells),
           "text items touching something: %d" % len(uniq)]
    out += ["  %-40s %s" % u for u in uniq]
    print("\n".join(out))
    with open(os.path.join(HERE, "overlap_check.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
