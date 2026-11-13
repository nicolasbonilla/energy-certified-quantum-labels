"""Guard against printed text hidden by mistake inside a LaTeX comment (added 2026-11-10).

The slip it catches (four times on 2026-11-10, once each in the R6 and R7 passes): an edit inserts a new `% src:` comment
in the middle of an existing line, so the rest of that line -- prose and its own `% src:` -- becomes part of the comment
and disappears from the PDF without any LaTeX error.

A comment is flagged when, after the first `src:` of the line, it contains
  - a second `% src` (an old source comment swallowed by a new one), or
  - LaTeX that only printed text uses: \\ref{, \\cite{, \\emph{, \\label{, ~\\, \\Jz, \\ms, \\Czz, \\tau inside $...$, or
  - three or more consecutive lower-case words after a closing parenthesis that ends a source item (prose after a source).
usage: python check_hidden_text.py [file.tex ...]   (default: main.tex supplement.tex tables.tex cover_letter.tex)
Exit code 1 if anything is flagged."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = sys.argv[1:] or ["main.tex", "supplement.tex", "tables.tex", "cover_letter.tex"]
LATEX = re.compile(r"\\(ref|cite|emph|label|eqref)\{|~\\|\$[^$]*\\(Jz|ms|Czz|tau|de|des)\b[^$]*\$")
PROSE = re.compile(r"\)\s+(?:[a-z]+[,.]?\s+){2}[a-z]+")


def comment(line):
    k = 0
    while True:
        j = line.find("%", k)
        if j < 0:
            return ""
        if j > 0 and line[j - 1] == "\\":
            k = j + 1
            continue
        return line[j:]


bad = 0
for f in FILES:
    path = f if os.path.isabs(f) else os.path.join(HERE, f)
    for i, line in enumerate(open(path, encoding="utf-8").read().splitlines(), 1):
        c = comment(line)
        if "src:" not in c:
            continue
        body = c.split("src:", 1)[1]
        why = []
        if c.count("% src") > 1:
            why.append("two src comments")
        if LATEX.search(body):
            why.append("LaTeX of printed text")
        m = PROSE.search(body)
        if m and not re.search(r"derived|structural|note|rounded|floored|ceiled|read|from|see|as in", body[max(0, m.start() - 60):m.end()]):
            why.append("prose after a source item")
        if why:
            bad += 1
            print(f"{f}:{i}: {', '.join(why)}: {c[:180]}")
print(f"check_hidden_text: {bad} suspect line(s) in {', '.join(FILES)}")
sys.exit(1 if bad else 0)
