# Main figures on the public data (rewrite of 2026-11-12): script, inputs, output

Addendum to `FIGURES_README.md` (which is unchanged, as are all earlier figure files, scripts and `pgf_*` folders).
The four figures of the main text were rebuilt on the public data of the dataset paper (repository at the pinned
commit, converted under `phase3/full_runs/real_data/`). Every plotted number is read from a stored file by the export
script of its folder; no physics is recomputed (one exception, stated below: a four-parameter least-squares curve
that is redrawn between the couplings and asserted equal to the stored predictions). Each export script writes
`export_check.txt`: the assertions it ran and the numbers quoted in the caption, with the rounding used.

All scripts run on a laptop in a few seconds: `python -B -I <export script>`, then `python -B -I build_rd.py <name>`
in the same folder (pdflatex, PNG previews at 300 and 150 dpi, scan of the LaTeX log into `log_check_<name>.txt`).
The compiled PDF is then copied to `paper/figures/` under the name used by the main text.

| Output used by the main text | Folder | Export script, TeX source | Inputs (under `phase3/full_runs/` unless stated) |
|---|---|---|---|
| `fig1_map_rd_pgf.pdf` (Fig. 3) | `pgf_map_rd/` | `export_map_rd.py`, `fig_map_rd.tex` | `real_data/out/map_rows.json` and `real_data/e1/map_e1/map_rows.json` (the second repeats the first and adds the column of the extension E1; equality of every field drawn is asserted); `method/laptop_post/out/emu/emu_n*_J*.json` (emulated first stage, `var.primary.err.dm_s`, `var.primary.dE_site`) |
| `fig1_composite_rd_pgf.pdf` (Fig. 2) | `pgf_composite_rd/` | `export_composite_rd.py`, `fig_composite_rd.tex` | (a) `a_map.dat`, `a_contour_tau.dat` copied byte for byte from `pgf_composite/` (the map is a property of the model); line: `real_data/out/map_rows.json` (`de_real`, n = 57). (b) the same map rows (status, `exact.width_over_tau`, `lower.w_lower_over_tau`) and `real_data/out/predict_real.json` (`sizes.57.n19_comparison`). (c, d) `cd_*.dat` and the printed device numbers copied byte for byte from `pgf_composite/` |
| `fig1_overview_rd_pgf.pdf` (Fig. 1) | `pgf_overview_rd/` | `export_overview_rd.py`, `fig_overview_rd.tex` | (a) schematic. (b) `b_*.dat` copied byte for byte from `pgf_overview/`. (c) `real_data/out/learn/results_cheap.json` (`sizes.57.models.poly3_invJ`: labels, reference, predictions, standard interval, coverage, control trained on DMRG labels) and `real_data/out/map_rows.json` (status, exact interval, labels of the two explicit states) |
| `fig_bias_law_rd.pdf` (Fig. 4) | `pgf_biaslaw_rd/` | `export_biaslaw_rd.py`, `fig_bias_law_rd.tex` | `data_biaslaw/*.dat` copied byte for byte from `figures/data_biaslaw/`; new: `pub_n<n>_J<Jz>.dat` from `real_data/out/predict_real.json` (`sizes.<n>.P5.rows`: `de`, `Delta`), cross-checked with `real_data/out/map_rows.json` |

## What each figure draws

**Fig. 3, `fig_map_rd`.** Top row: for each of the seven labels and each of the 50 couplings, the quantity that
decides the row. Certified (filled symbol): `exact.width_over_tau`, the width of the exact interval. Not certified
(open symbol): `lower.w_lower_over_tau`, the distance between the labels of the two explicit states. Undecided (grey,
drawn for m_s and Czz_bar): the explicit-state distance, with a bar up to the width of an exact interval where one
exists. Extension E1 (light symbols on a dashed line): `exact_e1.width_over_tau` where the extension gives an interval
that the stored certificates did not, or changes the status. Lines join neighbouring not-certified couplings; C2_bar
and the local labels carry a marker at every third coupling (staggered) and at every not-certified point without a
not-certified neighbour. Strip: status code of every row (0 not certified, 1 undecided, 2 certified, 3 certified only
with E1). Bottom row: m_s minus the reference in units of tau; band = `lower.witness`, lines = `exact.lo`, `exact.hi`
(dashed: `exact_e1`), dots = `label_real`, circles = emulated first stage. Vertical coordinate: y for |y| <= 1,
sign(y)(1 + log10|y|) beyond (function `sym` of the export script; the tick positions are printed in
`export_check.txt`). Two pgfplots warnings "the current plot has no coordinates" are expected: no undecided m_s row
at n = 115 has a stored exact interval, and the extension certifies no additional row at n = 57.

**Fig. 2, `fig_composite_rd`.** (a) the colour map and the teal contour are the earlier ones (sector window, inner
side); the black line with one dot per coupling is `de_real`; the dashed line is the smallest certified coupling of
m_s (3.5). (b) m_s at n = 57 with the status coding of Fig. 3 (the intervals of the extension E1 are not drawn here)
and the distance of the exact 19-site value from the reference. (c, d) unchanged.

**Fig. 1, `fig_overview_rd`.** (c): the cubic in 1/Jz of `ml2.fit_poly` (ridge 1e-8) fitted to the 45 public
labels. The stored file holds its predictions at the couplings; to draw the curve between them the script refits the
same four coefficients on the 45 stored labels and asserts equality with the stored predictions at the four test
couplings (max difference 1.6e-13). Band: plus or minus the stored half-width `qM`. Teal bars: `exact.lo`,
`exact.hi` of the 26 certified labels. Grey bars: `lower.witness` at the other 24 couplings. Right: stored coverage
counts of the m_s interval (`covM_emu`, `covM_truth`, and `covM_truth` of the control). In that file the keys
`*_emulated` hold the PUBLIC labels (the declared script is the stored one with the labels replaced).

**Fig. 4, `fig_bias_law_rd`.** The earlier figure plus eight filled symbols in panel (a): the public label of m_s at
its published energy error, at the four couplings of the panel and both sizes.

## Checks run on 2026-11-12/13 (see each `export_check.txt`, `log_check_*.txt`, `overlap_check_*.txt`)

- Export scripts: every assertion passes (55, 22, 29 and 8 lines marked PASS for the map, the landscape, the overview
  and the bias figure; none marked FAIL).
- pdflatex: return code 0, no overfull or underfull box, no missing character in the four figures (the two expected
  "no coordinates" warnings of the map figure are explained above).
- `overlap_check_rd.py` (new, in `paper/figures/`; `python -B -I overlap_check_rd.py <pdf> ...`): glyph boxes of
  different text lines against each other, and every text box against the page rendered at 600 dpi without its text.
  Map figure: no text on ink; 4 box contacts, all between pieces of one symbol (the bar of a `\bar C`, the superscript
  and the parenthesis of the rotated axis label). Landscape: 4 text boxes listed, three of them unchanged from the
  earlier figure (labels set on a white box over the colour map) and the pointer "(c, d)" above its own tick.
  Overview: 2 box contacts in the schematic of panel (a), unchanged from the earlier figure. Bias figure: 1 box contact
  and 3 text boxes listed, all unchanged from the earlier figure (`--print-only` on the earlier PDFs gives the same
  lines). The 150 and 300 dpi previews were also looked at.
- The earlier files `fig1_map_pgf.pdf`, `fig1_composite_pgf.pdf`, `fig1_overview_pgf.pdf`, `fig_bias_law.pdf`, their
  folders, `data_biaslaw/` and `FIGURES_README.md` were not touched (the new folders hold copies of the data files
  they reuse, with equal SHA-256 recorded in each `export_check.txt`).
