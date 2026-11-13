"""Render a PDF of this folder to PNG previews (300 dpi and print size 150 dpi) and print its natural size.
Usage: python -B render.py <stem>                         -> <stem>_300dpi.png, <stem>_print150dpi.png
       python -B render.py <stem> x0 y0 x1 y1 dpi out.png  -> crop (cm from the top-left corner)"""
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
stem = sys.argv[1]
page = fitz.open(os.path.join(HERE, stem + ".pdf"))[0]
w, h = page.rect.width, page.rect.height
print("%s natural size: %.2f x %.2f pt = %.2f x %.2f cm" % (stem, w, h, w / 72 * 2.54, h / 72 * 2.54))
if len(sys.argv) == 2:
    for dpi, suf in ((300, "_300dpi.png"), (150, "_print150dpi.png")):
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        pix.save(os.path.join(HERE, stem + suf))
        print("wrote", stem + suf, pix.width, "x", pix.height)
else:
    x0, y0, x1, y1, dpi = (float(v) for v in sys.argv[2:7])
    k = 72 / 2.54
    pix = page.get_pixmap(dpi=int(dpi), clip=fitz.Rect(x0 * k, y0 * k, x1 * k, y1 * k), alpha=False)
    pix.save(os.path.join(HERE, sys.argv[7]))
    print("wrote", sys.argv[7], pix.width, "x", pix.height)
