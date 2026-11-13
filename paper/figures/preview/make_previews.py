"""make_previews.py -- PNG previews of the figures of the article, for reading on the web.

README.md and docs/FIGURES.md of the replication package show these files. Each preview is the compiled figure file
of paper/figures/ (the file that the LaTeX documents include) rendered at 216 dots per inch on a white background;
nothing is redrawn and no number is read here. The vector files stay the reference.

    python -B make_previews.py          (needs PyMuPDF; writes the PNG files next to this script)
"""
import os
import sys

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
FIGURES = os.path.dirname(HERE)
ZOOM = 3.0                               # 72 dpi x 3 = 216 dpi
NAMES = [
    # main text, Figs. 1-4
    "fig1_overview_rd_pgf", "fig1_composite_rd_pgf", "fig1_map_rd_pgf", "fig_bias_law_rd",
    # Supplemental Material
    "figS_landscape_n57_pgf", "figS_lattice_pgf", "figS1_bias_vs_ratio_pgf", "figS_learning_pgf", "figS_huang_pgf",
    "fig2_rule_pgf", "fig3_mechanism_pgf",
    # ancillary tables
    "figS_landscape_n115_pgf", "figS_lattice_n115_pgf",
]


def main():
    bad = 0
    for name in NAMES:
        src = os.path.join(FIGURES, name + ".pdf")
        if not os.path.isfile(src):
            print("MISSING  %s.pdf" % name)
            bad += 1
            continue
        doc = fitz.open(src)
        if len(doc) != 1:
            print("NOT ONE PAGE  %s.pdf (%d pages)" % (name, len(doc)))
            bad += 1
            continue
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), alpha=False)
        out = os.path.join(HERE, name + ".png")
        pix.save(out)
        print("%-28s %4d x %4d pixels  %7d bytes" % (name + ".png", pix.width, pix.height, os.path.getsize(out)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
