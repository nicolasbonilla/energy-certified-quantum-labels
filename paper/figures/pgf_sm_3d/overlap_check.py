"""Geometric check of a figure PDF: does any text touch a stroked line, a marker or another text?

  python -B overlap_check.py <file.pdf> [...]      (also used by build.py)

Text boxes: the glyph boxes of PyMuPDF (font ascent/descent, shrunk vertically to 70 % around their centre).
Obstacles: every stroked segment or curve (inflated by half its line width) and every small filled shape with curves
(markers, lattice nodes).  Backgrounds are not obstacles: map cells (filled and stroked in their own colour), bands,
label boxes, colour bars.  Clipping is not modelled, so a halo that is clipped at an axis frame can be reported; such
hits are checked by eye on the 300-dpi PNG.
"""
import sys

import fitz

SMALL = 30.0
VSHRINK = 0.70


def _dist(p, q, r):
    best = 1e9
    for k in range(41):
        t = k / 40
        x, y = p.x + t * (q.x - p.x), p.y + t * (q.y - p.y)
        dx = max(r.x0 - x, 0, x - r.x1)
        dy = max(r.y0 - y, 0, y - r.y1)
        best = min(best, (dx * dx + dy * dy) ** 0.5)
    return best


def _bez(p0, p1, p2, p3, n=16):
    out = []
    for k in range(n + 1):
        t = k / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append(fitz.Point(a * p0.x + b * p1.x + c * p2.x + d * p3.x, a * p0.y + b * p1.y + c * p2.y + d * p3.y))
    return out


def check_pdf(path):
    pg = fitz.open(path)[0]
    words = []
    for bi, b in enumerate(pg.get_text("rawdict")["blocks"]):
        for ln in b.get("lines", []):
            horiz = abs(ln["dir"][0] - 1) < 1e-6
            for sp in ln["spans"]:
                txt = "".join(c["c"] for c in sp["chars"])
                for c in sp["chars"]:
                    if not c["c"].strip():
                        continue
                    r = fitz.Rect(c["bbox"])
                    if horiz:                                # glyph box from the baseline and the font size (the
                        oy, sz = c["origin"][1], sp["size"]  # font bbox is loose); rotated text: its bbox
                        r = fitz.Rect(r.x0, oy - 0.72 * sz, r.x1, oy + 0.20 * sz)
                    words.append((txt, r, bi if horiz else "rot"))   # rotated glyphs: one axis label
    segs, blobs, nbg = [], [], 0
    clips = {}                                   # level -> clip rectangle (scissor) of the enclosing clip paths
    for d in pg.get_drawings(extended=True):
        lev = d.get("level", 0)
        for k in [k for k in clips if k >= lev]:
            del clips[k]
        if d.get("type") == "clip":
            clips[lev] = fitz.Rect(d["scissor"])
            continue
        if d.get("type") == "group":
            continue
        sc = None
        for k in sorted(clips):
            sc = clips[k] if sc is None else sc & clips[k]
        stroked = d.get("type") in ("s", "fs")
        filled = d.get("type") in ("f", "fs")
        hw = (d.get("width") or 0.4) / 2
        rr = d["rect"]
        kinds = set(it[0] for it in d["items"])
        if filled and "c" not in kinds and (not stroked or d.get("fill") == d.get("color")):
            nbg += 1
            continue
        if filled and "c" in kinds and rr.width < SMALL and rr.height < SMALL:
            blobs.append(rr)
            continue
        if not stroked:
            continue
        new = []
        for it in d["items"]:
            if it[0] == "l":
                new.append((it[1], it[2], hw))
            elif it[0] == "c":
                pts = _bez(*it[1:5])
                new += [(a, b, hw) for a, b in zip(pts[:-1], pts[1:])]
            elif it[0] == "re":
                q = it[1]
                new += [(a, b, hw) for a, b in ((q.tl, q.tr), (q.tr, q.br), (q.br, q.bl), (q.bl, q.tl))]
            elif it[0] == "qu":
                q = it[1]
                new += [(a, b, hw) for a, b in ((q.ul, q.ur), (q.ur, q.lr), (q.lr, q.ll), (q.ll, q.ul))]
        if sc is not None:                       # keep only the visible part: clip each segment to the scissor
            vis = []
            for p, q, w in new:
                pts = [fitz.Point(p.x + t / 20 * (q.x - p.x), p.y + t / 20 * (q.y - p.y)) for t in range(21)]
                ins = [pt for pt in pts if sc.x0 <= pt.x <= sc.x1 and sc.y0 <= pt.y <= sc.y1]
                if len(ins) >= 2:
                    vis.append((ins[0], ins[-1], w))
                elif len(ins) == 1:
                    vis.append((ins[0], ins[0], w))
            new = vis
        segs += new
    hits = []
    for txt, r, _ in words:
        for p, q, hw in segs:
            if min(p.x, q.x) > r.x1 + 3 or max(p.x, q.x) < r.x0 - 3 or min(p.y, q.y) > r.y1 + 3 or \
                    max(p.y, q.y) < r.y0 - 3:
                continue
            if _dist(p, q, r) - hw < 0.3:
                hits.append((txt, "line", (round(r.x0, 1), round(r.y0, 1))))
        for b in blobs:
            if r.intersects(b):
                hits.append((txt, "marker", (round(r.x0, 1), round(r.y0, 1))))
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            a, b = words[i][1], words[j][1]
            if words[i][2] == words[j][2]:          # same text block: one label or formula (sub/superscripts)
                continue
            if a.intersects(b) and min(a.x1, b.x1) - max(a.x0, b.x0) > 1.0 and min(a.y1, b.y1) - max(a.y0, b.y0) > 0.5:
                hits.append((words[i][0] + " | " + words[j][0], "text", (round(a.x0, 1), round(a.y0, 1))))
    uniq = {}
    for t, k, at in hits:
        uniq.setdefault((t, k), at)
    out = ["overlap check: %d glyphs, %d stroked segments, %d markers/nodes, %d background fills ignored; "
           "text items touching something: %d" % (len(words), len(segs), len(blobs), nbg, len(uniq))]
    out += ["    %-45s %-6s at %s pt" % (t, k, at) for (t, k), at in sorted(uniq.items())]
    return out


if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(f)
        print("\n".join(check_pdf(f)))
