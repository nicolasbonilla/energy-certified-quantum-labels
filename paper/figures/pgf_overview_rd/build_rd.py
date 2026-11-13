"""Compile a standalone figure of this folder, render PNG previews and scan the LaTeX log.

  python -B -I build_rd.py [name]      (default name: fig_map_rd; works only in this folder)

Writes <name>.pdf/.log/.aux, <name>_300dpi.png, <name>_150dpi.png (about print size at 17.8 cm) and
log_check_<name>.txt. Same steps as ../pgf_map/build.py.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    return subprocess.run(cmd, cwd=HERE, capture_output=True, text=True).returncode


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "fig_map_rd"
    rc = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"])
    out = ["pdflatex return code: %d" % rc]
    with open(os.path.join(HERE, name + ".log"), encoding="latin-1") as f:
        log = f.read()
    pats = {"errors (lines starting with !)": r"^!.*$", "overfull boxes": r"Overfull \\[hv]box.*$",
            "underfull boxes": r"Underfull \\[hv]box.*$", "missing characters": r"Missing character.*$",
            "warnings": r"^.*Warning.*$"}
    for k, p in pats.items():
        hits = re.findall(p, log, flags=re.M)
        out.append("%s: %d" % (k, len(hits)))
        out.extend("    " + h.strip() for h in hits[:10])
    if rc == 0:
        import fitz  # PyMuPDF, for the page size and the fonts only
        d = fitz.open(os.path.join(HERE, name + ".pdf"))
        r = d[0].rect
        out.append("page size: %.1f x %.1f bp = %.2f x %.2f cm" % (r.width, r.height, r.width / 72 * 2.54,
                                                                  r.height / 72 * 2.54))
        out.append("fonts: " + ", ".join(sorted({f[3] for f in d[0].get_fonts()})))
        d.close()
        run(["pdftoppm", "-r", "300", "-png", "-singlefile", name + ".pdf", name + "_300dpi"])
        run(["pdftoppm", "-r", "150", "-png", "-singlefile", name + ".pdf", name + "_150dpi"])
        out.append("previews: %s_300dpi.png, %s_150dpi.png (pdftoppm)" % (name, name))
    else:
        i = log.find("\n!")
        out.append(log[i:i + 1500])
    print("\n".join(out))
    with open(os.path.join(HERE, "log_check_%s.txt" % name), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
