"""Overlap check of a standalone figure PDF (the four figures of the public-data rewrite, 2026-11-12).

  python -B -I overlap_check_rd.py <folder>/<name>.pdf [...]     writes <folder>/overlap_check_<name>.txt
  python -B -I overlap_check_rd.py --print-only <pdf> [...]      prints only (for a PDF in a folder not to be written)

Same idea as pgf_map/overlap_check.py, without a list of colours per figure:
1. Text against text: the tight glyph boxes of two text spans of different lines must not intersect (pieces of one
   formula, e.g. an accent, a subscript or a superscript next to its symbol, are exempt).
2. Text against ink: all text is removed from an in-memory copy of the page (redaction; the vector graphics stay),
   the copy is rendered at 600 dpi, and inside every text box, grown by a clearance of 0.8 bp, the pixels are compared
   with the most frequent colour of that box. A box whose pixels are not (nearly) all of one colour has a line, a
   marker, a tick or the edge of a shaded area behind or next to the text; it is listed with the share of such pixels.
   Text set on a colour gradient (the map of Fig. 2a) is listed too and has to be looked at.
The PDF is opened read-only; nothing but the report is written.
"""
import os
import sys

import fitz
import numpy as np

DPI = 600
CLEAR = 0.8          # bp
TOL = 14             # per channel
SHARE = 0.02         # a box is listed if more than this share of its pixels differs from its dominant colour


def check(pdf, write=True):
    fitz.TOOLS.set_small_glyph_heights(True)
    src = fitz.open(pdf)
    page = src[0]
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for li, ln in enumerate(b.get("lines", [])):
            for s in ln["spans"]:
                if s["text"].strip():
                    spans.append({"t": s["text"], "r": fitz.Rect(s["bbox"]), "line": (id(b), li), "size": s["size"]})
    out = ["%s: %d text spans; clearance %.1f bp; render %d dpi" % (os.path.basename(pdf), len(spans), CLEAR, DPI)]
    n1 = 0
    for i in range(len(spans)):
        for j in range(i + 1, len(spans)):
            a, b = spans[i], spans[j]
            if a["line"] == b["line"]:
                continue
            inter = a["r"] & b["r"]
            if inter.is_empty or inter.width < 0.05 or inter.height < 0.05:
                continue
            near = abs(a["r"].x1 - b["r"].x0) < 1.0 or abs(b["r"].x1 - a["r"].x0) < 1.0 or (
                a["r"].x0 >= b["r"].x0 - 0.5 and a["r"].x1 <= b["r"].x1 + 0.5 and min(a["r"].height, b["r"].height) < 6.5)
            stacked = max(a["r"].height, b["r"].height) < 6.5
            if near or stacked:
                continue
            out.append("TEXT/TEXT  %r %s  vs  %r %s" % (a["t"], tuple(round(v, 1) for v in a["r"]), b["t"],
                                                        tuple(round(v, 1) for v in b["r"])))
            n1 += 1
    # text removed, graphics kept
    doc = fitz.open()
    doc.insert_pdf(src)
    pg = doc[0]
    for s in spans:
        pg.add_redact_annot(s["r"], fill=False)
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)      # as pgf_map/overlap_check.py: text only
    left = len(pg.get_text("words"))
    out.append("text left after removal: %d words" % left)
    pix = pg.get_pixmap(dpi=DPI, alpha=False)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    k = DPI / 72.0
    n2 = 0
    for s in spans:
        r = s["r"]
        x0, y0 = max(0, int((r.x0 - CLEAR) * k)), max(0, int((r.y0 - CLEAR) * k))
        x1, y1 = min(pix.width, int((r.x1 + CLEAR) * k) + 1), min(pix.height, int((r.y1 + CLEAR) * k) + 1)
        box = img[y0:y1, x0:x1].reshape(-1, 3)
        if len(box) == 0:
            continue
        q = (box // 8) * 8                                   # coarse colours for the mode
        vals, counts = np.unique(q, axis=0, return_counts=True)
        mode = vals[counts.argmax()] + 4
        off = (np.abs(box - mode) > TOL).any(axis=1)
        share = off.mean()
        if share > SHARE:
            n2 += 1
            out.append("TEXT/INK   %-28r box %s: %4.1f %% of the pixels differ from the dominant colour %s"
                       % (s["t"][:26], tuple(round(v, 1) for v in r), 100 * share, tuple(int(v) for v in mode)))
    out.append("text/text conflicts: %d; text boxes with ink or a colour edge behind them: %d" % (n1, n2))
    if write:
        rep = os.path.join(os.path.dirname(pdf), "overlap_check_%s.txt" % os.path.splitext(os.path.basename(pdf))[0])
        with open(rep, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return n1, n2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    WRITE = "--print-only" not in args          # --print-only: no report file (used on the earlier figures)
    for p in (a for a in args if a != "--print-only"):
        check(os.path.abspath(p), WRITE)
        print()
