"""Render fig_overview.pdf to PNG previews (300 dpi and print-size 150 dpi) and print the natural page size.
Usage: python -B render.py [crop x0 y0 x1 y1 in cm, zoom dpi]  -> also writes a cropped zoom preview."""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
pdf = os.path.join(HERE, "fig_overview.pdf")
doc = fitz.open(pdf)
page = doc[0]
w, h = page.rect.width, page.rect.height
print("natural size: %.2f x %.2f pt = %.2f x %.2f cm" % (w, h, w / 72 * 2.54, h / 72 * 2.54))
if len(sys.argv) == 1:
    for dpi, name in ((300, "fig_overview_300dpi.png"), (150, "fig_overview_print150dpi.png")):
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        pix.save(os.path.join(HERE, name))
        print("wrote", name, pix.width, "x", pix.height)
else:
    x0, y0, x1, y1, dpi = (float(v) for v in sys.argv[1:6])
    k = 72 / 2.54
    clip = fitz.Rect(x0 * k, y0 * k, x1 * k, y1 * k)
    pix = page.get_pixmap(dpi=int(dpi), clip=clip, alpha=False)
    name = sys.argv[6] if len(sys.argv) > 6 else "zoom.png"
    pix.save(os.path.join(HERE, name))
    print("wrote", name, pix.width, "x", pix.height)
