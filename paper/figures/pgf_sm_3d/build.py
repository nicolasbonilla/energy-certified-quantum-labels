"""Compile the four native Supplemental figures with pdflatex, scan the logs, render PNG previews (300 dpi and the
print size, 150 dpi) and run the overlap check.

  cd paper/figures/pgf_sm_3d && python -B build.py [name ...]     -> <name>.pdf, <name>_{300,150}dpi.png,
                                                                     build_check.txt (all names)
"""
import os
import re
import subprocess
import sys

import fitz

from overlap_check import check_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
ALL = ["figS_landscape_n57_pgf", "figS_landscape_n115_pgf", "figS_lattice_pgf", "figS_lattice_n115_pgf"]


def build(name):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"], cwd=HERE,
                       capture_output=True, text=True, errors="replace")
    log = open(os.path.join(HERE, name + ".log"), encoding="latin-1").read()
    pats = {"errors": r"^! ", "overfull": r"Overfull \\[hv]box", "underfull": r"Underfull \\[hv]box",
            "missing characters": r"Missing character", "warnings": r"[Ww]arning"}
    out = ["[%s] pdflatex exit code %d" % (name, r.returncode)]
    for k, p in pats.items():
        hits = [ln for ln in log.splitlines() if re.search(p, ln)]
        out.append("  %-19s %d" % (k + ":", len(hits)) + ("" if not hits else "  e.g. " + hits[0][:110]))
    pdf = os.path.join(HERE, name + ".pdf")
    if r.returncode != 0 or not os.path.exists(pdf):
        return out
    d = fitz.open(pdf)
    w, h = d[0].rect.width / 72 * 2.54, d[0].rect.height / 72 * 2.54
    d.close()
    out.append("  natural size %.2f cm x %.2f cm; PDF %.0f kB" % (w, h, os.path.getsize(pdf) / 1024))
    for dpi in (300, 150):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", name + ".pdf", "%s_%ddpi" % (name, dpi)],
                       cwd=HERE, check=True)
    out += ["  " + s for s in check_pdf(pdf)]
    return out


def main():
    names = sys.argv[1:] or ALL
    res = []
    for nm in names:
        res += build(nm)
    print("\n".join(res))
    p = os.path.join(HERE, "build_check.txt")
    old = {}
    if os.path.exists(p):                     # keep the entries of figures not rebuilt this time
        cur = None
        for ln in open(p, encoding="utf-8").read().splitlines():
            m = re.match(r"\[(\S+)\]", ln)
            if m:
                cur = m.group(1)
            if cur:
                old.setdefault(cur, []).append(ln)
    new = {}
    cur = None
    for ln in res:
        m = re.match(r"\[(\S+)\]", ln)
        if m:
            cur = m.group(1)
        new.setdefault(cur, []).append(ln)
    old.update(new)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for nm in ALL:
            if nm in old:
                f.write("\n".join(old[nm]) + "\n")


if __name__ == "__main__":
    main()
