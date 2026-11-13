"""Compile the native figures of this folder, render PNG previews and scan the LaTeX logs.

  python -B build.py [name ...]      (default: fig_rule fig_mechanism fig_bias_ratio; works only in this folder)

For each name: pdflatex name.tex -> name.pdf; pdftoppm -> name_300dpi.png and name_150dpi.png (print size);
the log is scanned for errors, overfull/underfull boxes, missing characters and warnings; results in log_check.txt.
"""
import os
import re
import subprocess
import sys

import fitz  # PyMuPDF, page size and fonts only

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["fig_rule", "fig_mechanism", "fig_bias_ratio"]


def run(cmd):
    return subprocess.run(cmd, cwd=HERE, capture_output=True, text=True).returncode


def check(name):
    out = ["== %s ==" % name]
    rc = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"])
    with open(os.path.join(HERE, name + ".log"), encoding="latin-1") as f:
        log = f.read()
    if rc == 0 and "Rerun" in log:          # legends placed by name need a second run
        rc = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"])
        with open(os.path.join(HERE, name + ".log"), encoding="latin-1") as f:
            log = f.read()
        out.append("second pdflatex run (cross-references)")
    out.append("pdflatex return code: %d" % rc)
    pats = {"errors (lines starting with !)": r"^!.*$", "overfull boxes": r"Overfull \\[hv]box.*$",
            "underfull boxes": r"Underfull \\[hv]box.*$", "missing characters": r"Missing character.*$",
            "warnings": r"^.*Warning.*$"}
    for k, p in pats.items():
        hits = re.findall(p, log, flags=re.M)
        out.append("%s: %d" % (k, len(hits)))
        out.extend("    " + h.strip() for h in hits[:10])
    if rc == 0:
        d = fitz.open(os.path.join(HERE, name + ".pdf"))
        r = d[0].rect
        out.append("page size: %.1f x %.1f bp = %.2f x %.2f cm" % (r.width, r.height, r.width / 72 * 2.54,
                                                                  r.height / 72 * 2.54))
        out.append("fonts: " + ", ".join(sorted({f[3].split("+")[-1] for f in d[0].get_fonts()})))
        d.close()
        run(["pdftoppm", "-r", "300", "-png", "-singlefile", name + ".pdf", name + "_300dpi"])
        run(["pdftoppm", "-r", "150", "-png", "-singlefile", name + ".pdf", name + "_150dpi"])
    return out


def main():
    names = sys.argv[1:] or NAMES
    allout = []
    for n in names:
        allout += check(n)
    print("\n".join(allout))
    keep = {}
    p = os.path.join(HERE, "log_check.txt")
    if os.path.exists(p):
        cur = None
        for line in open(p, encoding="utf-8"):
            if line.startswith("== "):
                cur = line.strip()[3:-3]
                keep[cur] = []
            if cur:
                keep[cur].append(line.rstrip("\n"))
    cur = None
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
