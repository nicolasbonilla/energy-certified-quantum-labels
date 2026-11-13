"""Compile fig_composite.tex with pdflatex, scan the log, render PNG previews (300 dpi and print size, 150 dpi).

  cd paper/figures/pgf_composite && python -B build.py      -> fig_composite.pdf, fig_composite_{300,150}dpi.png,
                                                             build_check.txt
"""
import os
import re
import subprocess

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "fig_composite.tex"], cwd=HERE,
                       capture_output=True, text=True, errors="replace")
    log = open(os.path.join(HERE, "fig_composite.log"), encoding="latin-1").read()
    pats = {"errors": r"^! ", "overfull": r"Overfull \\[hv]box", "underfull": r"Underfull \\[hv]box",
            "missing characters": r"Missing character", "warnings": r"[Ww]arning"}
    out = ["pdflatex exit code %d" % r.returncode]
    for k, p in pats.items():
        hits = [ln for ln in log.splitlines() if re.search(p, ln)]
        out.append("%-19s %d" % (k + ":", len(hits)) + ("" if not hits else "  e.g. " + hits[0][:100]))
    pdf = os.path.join(HERE, "fig_composite.pdf")
    d = fitz.open(pdf)
    w, h = d[0].rect.width / 72 * 2.54, d[0].rect.height / 72 * 2.54
    d.close()
    out.append("natural size %.2f cm x %.2f cm; PDF %.0f kB" % (w, h, os.path.getsize(pdf) / 1024))
    for dpi in (300, 150):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", "fig_composite.pdf",
                        "fig_composite_%ddpi" % dpi], cwd=HERE, check=True)
        out.append("rendered fig_composite_%ddpi.png" % dpi)
    print("\n".join(out))
    with open(os.path.join(HERE, "build_check.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
