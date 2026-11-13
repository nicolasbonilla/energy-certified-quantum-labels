# Figures and tables: script, inputs, output

All scripts run on a laptop from `paper/figures/` (`python <script>`), read the deposited result folders read-only
(paths in `common.py`, relative to `J_next_paper/`) and write only into `paper/figures/`. No physics is recomputed.
Python 3.11 with numpy, matplotlib, Pillow; the 3-D renders also need PyVista 0.49 (VTK 9.7, off-screen; Phong
shading, screen-space ambient occlusion, 2x supersampling). New figures use Computer Modern (matplotlib `cmr10`).
Design log of the 3-D figures: `ART_LOG.md`.

| Output | Script | Inputs (under `phase3/full_runs/` unless stated) |
|---|---|---|
| `fig1_composite.pdf/.png` (main Fig. 2 since the Track-1 integration, 2026-11-04; 600-dpi 3-D rasters + vector text; (b) rings the points proved with exact lower bounds, from `rigor/outputs/results_v2.json`) | `fig1_composite.py` (via `landscape_data.py`) | (a) `map/laptop_analysis/out/states/*.json`, `out/thr/*.json`, `summary_map.json`; (b) `summary_map.json` (rows at_dig.ratio_out, jstar); (c, d) `qpu/out_20261031T093107Z/out/device_A_J1.2.json`, `control_J1.2.json`, `qpu/refs/ref_n57_J1.2.json`, `qpu/jobs/A/prep.json` (routed sites); graph `map/laptop_analysis/code/graphs/hh_d5.json` |
| `fig_bias_law.pdf` (main Fig. 4; native PGFPlots, 2026-11-06) | `fig_bias_law.tex` (pdflatex in `paper/figures/`) | `data_biaslaw/*.dat`, written by `phase3/full_runs/bias_law/code/bias_law.py` |
| `fig1_overview.pdf/.png` (main Fig. 1; Track-1 integration, 2026-11-04) | `fig1_overview.py` | (a) schematic, no data; (b) `map/laptop_analysis/summary_map.json` rows (n = 19, 57, 115; Jz = 4.0; Czz_bar, Z_bulk; de_star_out, de_star_in), `huang/laptop_analysis/summary_huang.json` rows (Cnn of every instance; Ccent (4,1), Cfix (6,1), (9,1); tau.de_out, tau.de_in); (c) `learning/analysis/learn_M1_D_O.json`, `learn_M2_D_O.json` (coverage[advL5, gen5][SC, CSC][avg, nn].covT_id, covO_id, wid_id) |
| `figS_learning.pdf/.png` (SM Fig. S4; Track-1 integration) | `figS_learning.py` (imports the panels of `learning/code/plot_learn.py` with bytecode writing off; the result folder is only read) | `learning/analysis/learn_M1_D_O.json`, `learn_M2_D_O.json` |
| `sm_tables/learn_cov_M1.tex`, `learn_cov_M2.tex`, `learn_abst.tex` (SM Tables S18-S20; Track-1 integration) | `make_sm_learning.py` | `learning/analysis/learn_M1_D_O.json`, `learn_M2_D_O.json` (coverage; abstention[*].rule; the CB column is the declared midpoint rule, JSON key CB_mid) |
| `fig1_map.pdf/.png` (main Fig. 3) | `fig1_map.py` | `map/laptop_analysis/summary_map.json`; `method/laptop_post/out/summary.json`, `out/emu/*.json` |
| `fig2_rule.pdf/.png` (main Fig. 4) | `fig2_rule.py` | `paper/data/r3gen/out/t2_local.txt`, `t3_comb.txt`; `summary_map.json` (law_ratio_out, claims C-E) |
| `fig3_mechanism.pdf/.png` (main Fig. 5) | `fig3_mechanism.py` | `method/laptop_post/out/summary.json` (families, bias_at_ibm_energy), `out/gsscan/*.json` |
| `fig4_learning.pdf/.png` (no longer in the paper: the old in-grid learning test was removed in the Track-1 integration) | `fig4_learning.py` | `method/laptop_post/out/ml/ml_n57.json`, `ml_n115.json`, `out/ref/*.json`, `out/emu/*.json` |
| `figS_landscape_n57.pdf/.png`, `figS_landscape_n115.pdf/.png` (SM) | `fig_landscape.py` (via `landscape_data.py`) | `map/laptop_analysis/out/states/*.json`, `out/thr/*.json`, `summary_map.json`; `method/laptop_post/out/emu/*.json`, `out/summary.json` (dZ_matched) |
| `figS_lattice.pdf/.png`, `figS_lattice_n115.pdf/.png` (SM) | `fig_lattice.py` (renderer of `fig1_composite.py`) | `method/laptop_post/out/emu/emu_n*_J1.2.json`, `out/ref/ref_n*_J1.2.json`; `map/laptop_analysis/out/states/*.json` and `summary_map.json` (witness components at E_lo); graphs `hh_d5.json`, `hh_d7.json` (= `phase3/pilot_witness/code/graphs/`, checked) |
| `figS1_bias_vs_ratio.pdf/.png` (SM) | `figS1_bias_vs_ratio.py` | `method/laptop_post/out/summary.json` (families, bias_at_ibm_energy) |
| `graphical_abstract.png/.pdf` (not in the PDFs) | `fig_graphical_abstract.py` (renderers of `fig1_composite.py`) | as Fig. 1 (a) and (c) |
| `_render_*.png` (intermediate 3-D renders, no text) | the 3-D scripts above | as above |
| `table1_rows.tex` (main Table I) | `make_table1.py` | `summary_map.json` |
| `figS_huang.pdf/.png` (SM Fig. S5 since the Track-1 integration; integration pass) | `figS_huang.py` (restyled from `huang/code/plot_h.py`) | `huang/laptop_analysis/summary_huang.json` |
| `sm_tables/{map_glance,rig_v2,rig_v1,qpu,huang_featured,huang_pairs}.tex` (SM Tables S3, S8, S9, S17, S22, S23 since the Track-1 integration; integration pass) | `make_sm_new.py` (helpers of `make_sm_tables.py`) | `summary_map.json`; `rigor/outputs/results_v2.json`, `results.json`; `qpu/analysis/analysis.json`; `huang/laptop_analysis/summary_huang.json` |
| `sm_tables/*.tex` (all 21 SM tables) | `make_sm_tables.py` | `summary_map.json` (map tables; every cell cross-checked against `map/laptop_analysis/tables_map.md`), `map/RESULTS.md` Secs. 8 and 11, `method/laptop_post/results_tables.md`, `paper/data/r3gen/out/t3_*.txt`, `t5_defects.txt` |

Checks built into the scripts: `landscape_data.py` reproduces the stored inner window edges of every m_s row of
`summary_map.json` exactly (max difference 0) and asserts that the per-site witness differences average to the m_s
width and that every heavy-hex edge has unit length; `fig1_composite.py` asserts that the device and control
per-site values equal eta_i(<Z_i> - <Z_i>_DMRG) recomputed from their stored labels and the stored reference (max
difference 0) and average to the stored Delta m_s; `make_sm_tables.py` compares 2145 map cells with the deposited
Markdown tables (0 differences) and asserts the constant columns it drops.

Integration pass (2026-10-31, evening): `tables.tex` (ancillary `tables.pdf`) inputs the moved SM tables
(`map_widths_n57`, `map_status_n57`, `map_widths_n115`, `map_status_n115`, `map_law`, `meth_perfect`, `meth_window`) and the
figures `figS_landscape_n115`, `figS_lattice_n115`, unchanged. `figS1_bias_vs_ratio.py` now labels minor log ticks only
at 2 and 5 per decade (the default labels overlapped).

Track-2 revision (2026-10-31, after the hostile readings): `fig1_map.py` (main Fig. 2) no longer draws the squares that
converted the dataset paper's unsigned Delta Z with the emulation's sign, nor the hand-set abstention line; its
"certified" label reads "width <= tau" and the end labels are spaced further apart. `fig1_composite.py` (Fig. 1) and
`fig_landscape.py` (Figs. S1, A1) replace "+-3 %" by "width <= tau"; Fig. 1(b) says "lower bounds proved in exact
arithmetic"; the SM landscape legend labels the Delta Z points "sign assumed from emulation". All three re-run on the
laptop (PyVista renders about 2.5 and 1.8 min). Fig. 1 itself is still to be rebuilt (revision plan item 9).

Final-fix pass (2026-11-04):
- `fig1_overview.py`: panel (c) is now the realistic learning test on the 57-qubit heavy-hex model (reads
  `phase3/full_runs/learning_ibm/out/results.json`, the method emulation and DMRG outputs, and the map windows).
- `fig1_map.py`: `SHOW_ESTIMATES = False` (the estimates at the dataset's energy are no longer drawn in the main text).
- `make_sm_learning_ibm.py`: Supplemental table of the realistic learning test (`sm_tables/learn_ibm.tex`).
- `fig2_rule.pdf` and `fig3_mechanism.pdf` are now used by the Supplemental Material (Sec. S12), not the main text.

Third-reading pass (2026-11-04):
- `fig1_overview.py`: wording only. Panel (a) box "energy interval" (was "certified interval"); panel (c) grey bars
  labelled as an inner bound on the energy interval, "label dropped"; teal "certified, kept". "Certified" now means
  width <= tau only. Data unchanged.
- `make_sm_learning_prop2.py` (new): Supplemental table of Proposition 2(a)/(b) for the cubic model
  (`sm_tables/learn_prop2.tex`, from `phase3/full_runs/learning_ibm/out/prop2_cubic.json`).

Native-figure pass (2026-11-09; R6 S10 and LECCIONES item 12): main Figs. 1-3 rebuilt as standalone PGFPlots/TikZ
documents, same data, no physics recomputed. Each folder holds its export script (imports the loaders of the
matplotlib script above, writes `.dat` files), `export_check.txt` (assertions against the stored JSON, including the
caption numbers), the `.tex`, its log and PNG previews. The compiled PDFs are copied to `figures/` under new names;
the matplotlib/PyVista outputs above are kept unchanged.

| Output used by main.tex | Source folder | Rebuild |
|---|---|---|
| `fig1_overview_pgf.pdf` (Fig. 1) | `pgf_overview/` (`export_overview.py`, `fig_overview.tex`) | `python -B export_overview.py`; `pdflatex fig_overview.tex`; copy `fig_overview.pdf` |
| `fig1_composite_pgf.pdf` (Fig. 2; (a) is now a 2-D map, matrix plot 99 x 75 cells from the 16 x 150 relief grid, every second delta-e row; (c, d) TikZ lattice) | `pgf_composite/` (`export_composite.py`, `fig_composite.tex`, `build.py`, `overlap_check.py`) | `python -B export_composite.py`; `python -B build.py`; copy `fig_composite.pdf` |
| `fig1_map_pgf.pdf` (Fig. 3) | `pgf_map/` (`export_map.py`, `fig_map.tex`, `build.py`, `overlap_check.py`, `cvd_check.py`) | `python -B export_map.py`; `python -B build.py`; copy `fig_map.pdf` |

Supplemental and ancillary figures, same pass (each folder: export script with assertions in `export_check.txt`, `.tex`, `build.py`
where present, PNG previews):

| Output used by supplement.tex / tables.tex | Source folder |
|---|---|
| `figS_learning_pgf.pdf`, `figS_huang_pgf.pdf` | `pgf_sm_learning/` (`export_sm.py` runs the old scripts' `main()` with saving disabled and records the plotted arrays) |
| `fig2_rule_pgf.pdf`, `fig3_mechanism_pgf.pdf`, `figS1_bias_vs_ratio_pgf.pdf` | `pgf_sm_method/` (`export_sm_method.py`, `fig_rule.tex`, `fig_mechanism.tex`, `fig_bias_ratio.tex`, `build.py`, `overlap_check.py`) |
| `figS_landscape_n57_pgf.pdf`, `figS_landscape_n115_pgf.pdf`, `figS_lattice_pgf.pdf`, `figS_lattice_n115_pgf.pdf` | `pgf_sm_3d/` (`export_sm3d.py`, `*_pgf.tex`, `build.py`, `overlap_check.py`; landscape maps use the full 16 x 150 grid with shader interp) |

Correction to the table above: panel (c) of `fig1_overview` reads `learning_ibm/out/results.json`, the n = 57 emu and
ref files of `method/out_20261030T003230Z/out`, `hh_d5.json` and `summary_map.json` (not `learn_M{1,2}_D_O.json`,
which feed `figS_learning` and the SM tables).
