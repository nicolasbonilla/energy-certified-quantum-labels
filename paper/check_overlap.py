"""Find printed rows of text set too close together in a PDF (added 2026-11-10, LECCIONES 12: nothing overlapping).

For every pair of PyMuPDF text lines on a page that overlap horizontally and have the same font size (within 20 %),
the distance between their baselines is compared with that size: normal rows sit at >= ~1.1 x the size; a distance
between LOW and HIGH x the size means two different rows that touch or overlap (the 2026-11-10 case: Table S31, digits
only, rows 0.63 x apart). Pieces of one row (same baseline) and scripts (smaller font) are not compared. Glyphs of
formulas and figure tick labels give false hits (e.g. the two "0.0" at a plot's corner); the reliable signal is a pair
of rows that both hold only digits. Fix found on 2026-11-10: an absolute strut at the start of every table row.
usage: python check_overlap.py file.pdf [...]      (default: main.pdf supplement.pdf tables.pdf)"""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
LOW, HIGH = 0.25, 0.95


def lines(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            spans = [s for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            s0 = max(spans, key=lambda s: s["size"])
            x0, _, x1, _ = ln["bbox"]
            out.append((x0, x1, s0["origin"][1], s0["size"], "".join(s["text"] for s in spans).strip()))
    return out


def main():
    files = sys.argv[1:] or ["main.pdf", "supplement.pdf", "tables.pdf"]
    total = 0
    for f in files:
        doc = fitz.open(os.path.join(HERE, f) if not os.path.isabs(f) else f)
        hits = []
        for pno, page in enumerate(doc, 1):
            L = lines(page)
            for i in range(len(L)):
                for j in range(i + 1, len(L)):
                    a, b = L[i], L[j]
                    if min(a[1], b[1]) - max(a[0], b[0]) <= 1:
                        continue
                    if abs(a[3] - b[3]) > 0.2 * max(a[3], b[3]):
                        continue
                    d = abs(a[2] - b[2])
                    if LOW * a[3] < d < HIGH * a[3]:
                        hits.append((pno, d / a[3], a[4][:45], b[4][:45]))
        total += len(hits)
        print(f"{f}: {len(hits)} pairs of rows too close, on pages {sorted({h[0] for h in hits})}")
        for h in hits[:30]:
            print(("   p%d  baseline gap %.2f x size  | %s || %s" % h).encode("ascii", "replace").decode())
    print(f"check_overlap: {total} pair(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
