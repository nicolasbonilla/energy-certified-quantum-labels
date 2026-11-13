# Kill test W, step 0: does the envelope formula survive published iPEPS data?

Date 2026-11-07 (UTC). Formula: `FORMULA.md` (SHA-256 in `FORMULA.sha256`, hashed 15:54:55Z, before the paper below was opened). No cloud used for this step. On the laptop: web reading, extraction of plotted coordinates from two vector figures (text parsing of the PDF content streams), and arithmetic on the resulting dozen numbers.

## Verdict

**The formula SURVIVES step 0.** r ranges from 0.52 to 0.56 for D = 3 to 6 (0.57 at D = 7). The kill threshold was r > 1.2 for any D in 3..6. With the older QMC constants (Sandvik 1997: e0 = -0.669437, m0^2 = 0.0942), r rises to at most 0.61 for D = 3..6 (0.76 at D = 7). No D comes close to leaving the window.

## 1. The paper

arXiv 2009.02313 (v2): J. Hasik, D. Poilblanc, F. Becca, "Investigation of the Néel phase of the frustrated Heisenberg antiferromagnet by differentiable symmetric tensor networks", SciPost Phys. 10, 012 (2021). Checked through the arXiv API (title, authors, journal reference). C4v-symmetric U(1) iPEPS, D = 2..7, J1-J2 square lattice.

Definitions in the paper: m = |Tr[ρ^(1) S]| (single-site reduced density matrix), so m^2 is the squared length of the local moment, as assumed in `FORMULA.md` (no conversion needed). ξ is the transfer-matrix (transverse) correlation length, χ → ∞ extrapolated.

## 2. Where the numbers come from

- **Table II** (`tab:enemag`, TeX source lines 503-525, copied to `step0_inputs/2009.02313_table2_tex.txt`) gives only **D = 7**: e(7, χ→∞) = -0.669432, m^2(7, χ→∞) = 0.0994 (χ = 147: -0.669428 and 0.0994).
- **D = 3..6 exist only in figures**: Fig. 4 (energy against 1/ξ, J2 = 0 panel) and Fig. 5 (m^2 against 1/ξ, left panel). Reading them by eye is not precise enough: at D = 5, 6 the energy differs from e0 by less than the marker size. The figures in the arXiv source (sha256 of the e-print 6ef87db3…) are vector PDFs made by matplotlib 3.1.1. I decompressed their content streams (`code/step0/pdfstreams.py`) and listed every painted path with its colour and clip box (`code/step0/paths.py`). Each data point has an error-bar pair and a one-point marker path whose coordinates are the data point. The red (J2 = 0) entries of the first panel are in `step0_inputs/fig4_J2eq0_errorbars.txt` and `fig5_left_J2eq0_errorbars.txt`. Axis calibration from the tick and grid positions in the same streams: Fig. 4, e = -0.670 at y = 315.968828 pt, 39.353973 pt per 0.001; 1/ξ = 0 at x = 94.563264, 162.888889 pt per unit. Fig. 5, m^2 = 0 at y = 51.684375, 3127.5 pt per unit; 1/ξ = 0 at x = 101.675852, 370.805732 pt per unit.
- **Checks of the extraction.** (i) D = 7 from the figures: e = -0.66943196, m^2 = 0.099380, equal to Table II's χ→∞ values (-0.669432, 0.0994) to the printed digits; the plotted energies are therefore the χ-extrapolated ones (χ = 147 would give -0.669428). (ii) The 1/ξ abscissa of every D agrees between Fig. 4 and Fig. 5 to 1e-5, which confirms the identification of each point with its D (markers drawn in the caption's order D = 3..7). (iii) Coordinates are printed to 1e-6 pt, i.e. 3e-11 in e and 3e-10 in m^2: the reading error is negligible against everything else. What is not checked: whether the plotted values are exactly the paper's final numbers for D = 3..6 (no table exists to compare).

## 3. Values and r

δe = e(D) - e0 with e0 = -0.669441857 (Sandvik 2026). Envelope Δm2_env = 2 m0 u + u^2, u = 0.635984 δe^(1/3), m0 = 0.307444, m0^2 = 0.094522. r = (m^2 - m0^2) / Δm2_env.

| D | 1/ξ | e (χ→∞) | m^2 | δe | m^2 - m0^2 | Δm2_env | **r** | r with e0 = -0.669437 | r with 1997 e0 and m0^2 = 0.0942 |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 1.4905 | (not plotted in Fig. 4) | 0.152978 | — | 0.0585 | — | — | — | — |
| 3 | 1.1479 | -0.66460143 | 0.137910 | 4.840e-3 | 0.04339 | 0.07772 | **0.558** | 0.558 | 0.563 |
| 4 | 0.4853 | -0.66896732 | 0.112848 | 4.745e-4 | 0.01833 | 0.03296 | **0.556** | 0.558 | 0.568 |
| 5 | 0.2256 | -0.66938019 | 0.103088 | 6.167e-5 | 0.00857 | 0.01608 | **0.533** | 0.548 | 0.568 |
| 6 | 0.1431 | -0.66942312 | 0.100097 | 1.874e-5 | 0.00558 | 0.01067 | **0.522** | 0.579 | 0.610 |
| 7 | 0.1128 | -0.66943196 (table: -0.669432) | 0.099380 (table: 0.0994) | 9.89e-6 | 0.00486 | 0.00858 | 0.566 | 0.712 | 0.755 |

The brief's single point (D = 7, envelope 0.0067-0.0084, r ≈ 0.6-0.8) is reproduced: 0.00682-0.00858 for the two values of e0.

## 4. Reading

- Every iPEPS state of this paper lies inside the parameter-free envelope, using about 52-57 % of its upper width at every D from 3 to 7, across three decades of δe (5e-3 to 1e-5). The near-constant r is what finite-correlation-length scaling predicts (e - e0 ∝ ξ^-3, m^2 - m0^2 ∝ ξ^-1, refs. 1803.08445 and 1803.08566): the iPEPS sequence follows a δe^(1/3) curve parallel to the envelope.
- Limits of this check. (1) The envelope is leading order in the staggered field; the next term (k2 + k3) h^2 has unknown sign and size, and at D = 3 the optimal field corresponds to a magnon length of about 2 lattice spacings, so the D = 3 row tests the formula outside its clear validity. (2) Passing means the formula is not contradicted by one family of very good variational states; it does not show that the envelope is tight (that the true sup is near the formula). A tight check needs the exact envelope, which only exists on finite lattices (step 1). (3) For D = 6, 7 δe depends on e0 at the 25-50 % level (the 1997 and 2026 QMC values differ by 4.9e-6); r changes by at most a factor 1.26.
- The ratio r ≈ 0.55 is one method (iPEPS, one ansatz family) on one model. It says nothing yet about neural states.

## 5. Consequence

Step 0 does not kill the formula, so step 1 (declared numerics on cj-runner-1b) goes ahead.
