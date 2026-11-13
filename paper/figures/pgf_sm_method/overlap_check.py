"""Overlap check of the native figures (python -B overlap_check.py [name ...]; writes overlap_check.txt here).

Same method as figures/pgf_map/overlap_check.py, for several PDFs:
1. Text against text: tight glyph boxes (PyMuPDF, small glyph heights) of spans on different lines or nodes must not
   intersect (pieces of one formula, a sub- and a superscript, are exempt).
2. Text against ink: all text is removed from an in-memory copy (redaction; vector graphics untouched), the copy is
   rendered at 600 dpi and every text box, grown by 1.0 bp (0.35 mm), must contain only background colours (white,
   the shading of the figure, or their blend with the white legend background). Any other pixel is a curve, marker,
   tick, frame or line touching the text.
3. Legend against data: no path drawn before a legend background may have a point inside it (grown by 1.0 bp).
The PDFs are opened read-only; the text-free renders are written as <name>_textless.png.
"""
import os
import sys

import fitz
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DPI = 600
CLEAR = 1.0
TOL = 10
SHADES = {"fig_rule": [(0xE3, 0xF1, 0xE6)], "fig_mechanism": [], "fig_bias_ratio": []}
NAMES = ["fig_rule", "fig_mechanism", "fig_bias_ratio"]


def bg_mask(a, bgs):
    m = np.zeros(a.shape[:2], bool)
    for bgc in bgs:
        m |= (np.abs(a.astype(int) - np.array(bgc)) <= TOL).all(axis=2)
    return m


def check(name):
    out = ["== %s ==" % name]
    bgs = [(255, 255, 255)] + SHADES.get(name, [])
    bgs += [tuple(round(0.88 * 255 + 0.12 * c) for c in b) for b in bgs[1:]]
    fitz.TOOLS.set_small_glyph_heights(True)
    src = fitz.open(os.path.join(HERE, name + ".pdf"))
    spans = []
    for b in src[0].get_text("dict")["blocks"]:
        for li, ln in enumerate(b.get("lines", [])):
            for s in ln["spans"]:
                if s["text"].strip():
                    spans.append({"t": s["text"], "r": fitz.Rect(s["bbox"]), "line": (id(b), li),
                                  "radical": "Extension" in s["font"] and s["text"].strip() in "pqrs"})
    out.append("%d text spans; clearance %.1f bp; render %d dpi" % (len(spans), CLEAR, DPI))
    bad = 0
    for i in range(len(spans)):
        for j in range(i + 1, len(spans)):
            a, b = spans[i], spans[j]
            if a["line"] == b["line"]:
                continue
            inter = a["r"] & b["r"]
            if inter.is_empty or inter.width < 0.05 or inter.height < 0.05:
                continue
            near = abs(a["r"].x1 - b["r"].x0) < 1.0 or abs(b["r"].x1 - a["r"].x0) < 1.0
            stacked = max(min(a["r"].width, a["r"].height), min(b["r"].width, b["r"].height)) < 6.5  # scripts, also rotated
            if near or stacked:
                continue
            out.append("TEXT/TEXT  %r %s  vs  %r %s" % (a["t"], a["r"], b["t"], b["r"]))
            bad += 1
    doc = fitz.open()
    doc.insert_pdf(src)
    page = doc[0]
    for s in spans:
        page.add_redact_annot(s["r"], fill=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    out.append("text left after removal: %d words" % len(page.get_text("words")))
    pix = page.get_pixmap(dpi=DPI, alpha=False)
    pix.save(os.path.join(HERE, name + "_textless.png"))
    z = DPI / 72.0
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    ink = ~bg_mask(img, bgs)
    # TeX rules (fraction bars, radical overlines) are filled rectangles without a stroke: part of the text
    nrule = 0
    for d in src[0].get_drawings():
        if d.get("color") is None and d.get("fill") is not None and len(d["items"]) == 1 \
                and d["items"][0][0] == "re" and d["rect"].height < 1.2 and d["rect"].width < 40:
            r = d["rect"]
            ink[int(r.y0 * z) - 1:int(r.y1 * z) + 2, int(r.x0 * z) - 1:int(r.x1 * z) + 2] = False
            nrule += 1
    out.append("TeX rules treated as text: %d" % nrule)
    for s in spans:
        g = s["r"] + (-CLEAR, -CLEAR, CLEAR, CLEAR)
        if s["radical"]:          # a root sign continues into its overline (a TeX rule), which is text, not data
            g = s["r"] + (-CLEAR, -CLEAR, -1.5, CLEAR)
        x0, y0, x1, y1 = int(g.x0 * z), int(g.y0 * z), int(g.x1 * z) + 1, int(g.y1 * z) + 1
        n = int(ink[max(y0, 0):min(y1, pix.height), max(x0, 0):min(x1, pix.width)].sum())
        if n:
            out.append("TEXT/INK   %r %s: %d non-background pixels in its box" % (s["t"], s["r"], n))
            bad += 1
    drw = src[0].get_drawings()
    boxes = [d for d in drw if d.get("fill") is not None and all(abs(v - 1.0) < 1e-6 for v in d["fill"])
             and (d.get("fill_opacity") or 1.0) < 0.99]
    out.append("legend backgrounds: %d" % len(boxes))
    for bx in boxes:
        g = bx["rect"] + (-CLEAR, -CLEAR, CLEAR, CLEAR)
        for d in drw:
            if d["seqno"] >= bx["seqno"] or not d["rect"].intersects(g):
                continue
            pts = []
            for it in d["items"]:
                if it[0] == "l":
                    pts += [it[1] + (it[2] - it[1]) * (k / 48.0) for k in range(49)]
                elif it[0] == "c":
                    pts += [it[1], it[2], it[3], it[4]]
                elif it[0] == "re":
                    rr = it[1]
                    for p, q in ((rr.tl, rr.tr), (rr.tr, rr.br), (rr.br, rr.bl), (rr.bl, rr.tl)):
                        pts += [p + (q - p) * (k / 48.0) for k in range(49)]
                elif it[0] == "qu":
                    pts += [it[1].ul, it[1].ur, it[1].ll, it[1].lr]
            inside = [p for p in pts if g.x0 < p.x < g.x1 and g.y0 < p.y < g.y1]
            if inside:
                out.append("LEGEND/DATA  legend box %s covers %d points of path %s (stroke %s, fill %s)"
                           % (bx["rect"], len(inside), d["rect"], d.get("color"), d.get("fill")))
                bad += 1
    out.append("conflicts: %d" % bad)
    return out


def main():
    names = sys.argv[1:] or NAMES
    allout = []
    for n in names:
        if os.path.exists(os.path.join(HERE, n + ".pdf")):
            allout += check(n)
    print("\n".join(allout))
    keep, cur = {}, None
    p = os.path.join(HERE, "overlap_check.txt")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if line.startswith("== "):
                cur = line.strip()[3:-3]
                keep[cur] = []
            if cur:
                keep[cur].append(line.rstrip("\n"))
    for line in allout:
        if line.startswith("== "):
            cur = line[3:-3]
            keep[cur] = []
        keep[cur].append(line)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for n in NAMES:
            if n in keep:
                f.write("\n".join(keep[n]) + "\n")


if __name__ == "__main__":
    main()
