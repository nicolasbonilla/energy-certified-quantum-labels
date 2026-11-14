# Manuscript sources in this package

`paper/main.tex`, `paper/supplement.tex` and `paper/tables.tex` are public copies of the working manuscript:
comment-only lines (notes for the author) are left out and trailing comments that are not provenance
comments (`% src:`, `% fig:`, `% (...)`) are cut down to their percent sign. Nothing printed differs; the
PDFs in `paper/` were compiled from the working manuscript, and `python run_checks.py pdf` compiles the
copies. The number check (`paper/check_numbers.py`) was run on these copies.

| file | comment-only lines left out | trailing notes cut |
|---|---|---|
| `paper/main.tex` | 170 | 5 |
| `paper/supplement.tex` | 109 | 8 |
| `paper/tables.tex` | 10 | 2 |
