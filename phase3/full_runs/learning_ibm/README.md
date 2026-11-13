# learning_ibm — realistic learning test on the heavy-hex XXZ model (final-fix pass, 2026-11-04)

New folder; no other result folder was modified. Laptop only. Light post-processing of stored outputs:
**no new DMRG, no diagonalization, no new emulation.**

## Question

Does standard conformal calibration on labels of a realistic quantum-data generator cover the truth, and what does
the physics-derived abstention ("answer only where the energy certifies the label") do, on the 57/115-qubit
heavy-hex XXZ model of the dataset paper (arXiv:2606.15983)?

## Inputs (read-only)

| What | Where |
|---|---|
| emulated first-stage states (labels Z_i, m_s, energy) | `../method/out_20261030T003230Z/out/emu/emu_n{57,115}_J*.json` (variant `primary`; variant `ideal` as a second state) |
| DMRG truth | `../method/out_20261030T003230Z/out/ref/ref_n{57,115}_J*.json` |
| certification map | `../map/laptop_analysis/summary_map.json` |
| our device points (illustration only) | `../qpu/analysis/analysis.json` |
| regressors (imported, unchanged, no bytecode written) | `../method/code/ml2.py`, `../method/code/graphs/hh_d{5,7}.json` |

Available couplings (all used; none invented): n = 57: 14 couplings (10 training, Jz = 1.6, 1.8, 2.0, 2.2, 2.5,
3.0, 3.5, 4.0, 5.0, 6.0; 4 test, Jz = 1.1-1.4). n = 115: 11 couplings (7 training, Jz = 1.6, 2.0, 2.5, 3.0, 4.0, 5.0,
6.0; 4 test). pilot3 (`../../design/pilot3/`) holds n = 57 emulations on the same 14 couplings and adds no new
coupling. The dataset paper's 45 training points and its labels are not available.

## Design (in the header of `code/learn_ibm.py`, fixed before its outputs were read)

Not time-stamped in advance, unlike the other runs of this project: the design lives in the script header and was
fixed after the held-out errors of the method test (`../method/`) were known. The script was edited once (18:02:18)
after a first quick output (`out/results_fast.json`, 17:47:18); `results_fast.json` and `results_cheap.json` are
identical except for timings (checked 2026-11-04), so the edit changed no number.

- Models: cubic in 1/Jz (linear in its labels), the pilot's small perceptron, the dataset paper's architecture 1
  ("ibm_arch1"; test range only, for cost), nearest-neighbour null.
- Standard conformal, alpha = 0.1, calibrated on held-out emulated labels: each training coupling held out in turn
  (the plain jackknife of Barber et al., not jackknife+: no finite-sample guarantee); interval = prediction of the
  model trained on all training couplings +- q. Per-site residuals pooled over sites; they are dependent within a
  coupling, so the effective calibration size is the number of couplings. For m_s with N = 9 or 10 couplings
  (n = 57) q is the maximum residual and 0.9 is just attainable; at n = 115 (7 couplings) the attainable level is
  N/(N+1) < 0.9 and the maximum residual is used.
- Tests: test range 1.1-1.4; in distribution (one more coupling held out, repeated).
- Coverage of new emulated labels (primary, and the `ideal` state) and of the DMRG truth; widths and misses in
  units of tau = 0.06 |o_GS| (per site for Z_i).
- Control: the same trained and calibrated on DMRG labels (model error only).
- Certified status at each label's own energy from the map (eps_tau_out); width bounds from the stored windows.
- Label filter ("abstention" in the code): answer only where the map certifies the generated label at its own
  energy. It needs a generated label and its energy at the query; it is not the learner-side rule of Proposition 2.
  Couplings without a map row (n = 57: Jz = 2.2, 3.5) abstain by default.
- Robustness: a single split with 3 (n = 57) / 2 (n = 115) calibration couplings, all choices (cubic, null).

## Jobs run (2026-11-04, laptop, single-threaded BLAS)

```
python -I code/learn_ibm.py ../../.. out --models=poly3_invJ,null_nn --tag=cheap
python -I code/learn_ibm.py ../../.. out --models=mlp_pilot3 --sizes=57 --tag=mlp57
python -I code/learn_ibm.py ../../.. out --models=mlp_pilot3 --sizes=115 --tag=mlp115 --no-indist=ibm_arch1,mlp_pilot3
python -I code/learn_ibm.py ../../.. out --models=ibm_arch1 --sizes=57 --tag=ibm57
python -I code/learn_ibm.py ../../.. out --models=ibm_arch1 --sizes=115 --tag=ibm115   (STOPPED after ~45 min: several hours on the laptop; no output kept)
python -I code/learn_ibm.py ../../.. out --merge          -> out/results.json
python -I code/widths_huang.py ../../.. > out/widths_huang.txt     (benchmark widths in units of tau)
python -I -B code/consistency_huang.py ../../.. > out/consistency_huang_output.txt
```
`out/results_fast.json` is a first quick run of the cubic and null models only (identical numbers to `cheap`); a
first all-in-one run was stopped after about an hour (multi-threaded BLAS on tiny matrices) and left no output.

## Proposition 2(a)/(b) for the cubic model (added 2026-11-04, after the third reading)

Design note `PROP2_DESIGN.md`, written before the script existed; SHA-256
`bf410afde2292f2cd0929eb50b79f2ebbecf2fe86f5bbc08f26d2aa1c269384c`, hashed 2026-11-04T19:30:04Z
(`PROP2_DESIGN.sha256`, `PROP2_DESIGN_hash_time.txt`).

```
python -I code/prop2_cubic.py ../../.. out > out/prop2_cubic_stdout.txt     (about 1 min; -> out/prop2_cubic.json)
python -I code/descriptive.py ../../.. out > out/descriptive_stdout.txt     (arithmetic only; -> out/descriptive.json)
```
`code/prop2_cubic.py` follows the design note; `code/descriptive.py` tabulates ratios already implied by stored
outputs (emulated vs digitized energy error, label errors in tau, the OOD floor against the error needed to certify)
and has no decision rule. Each was run once.

Outcome (n = 57, cubic in 1/Jz, m_s): the learner-side intervals of Proposition 2 are wider than tau at every
coupling. Energy-calibrated intervals (b): 2q >= 16.5-22.4 tau in the training range (held out), 25.1-30.1 tau in the
test range. Band (a): W(x) >= 1.15-24.1 tau in the training range (held out; minimum at Jz = 5.0), 41.9-249 tau in
the test range; cubic on all ten training labels, in sample: W = 0.88-1.16 tau at 5.0, 2.1-2.9 tau at 4.0 and 6.0.
Rule (c) answers 0 of 14 couplings (n = 115: 0 of 11), all definite abstentions (even the lower values exceed tau).
The "3 of 14" answers at Jz = 4, 5, 6 belong to the label filter only. The widths come from the labels near the
isotropic point (energy interval at Jz = 1.6, at the emulated energy: 11.7-12.7 tau). Every label and every true value
lies in its outer interval; the coefficient form reproduces ml2.fit_poly to 2e-13.
Label filter with the J* interpolation at the two couplings without a map row: 2.2 stays uncertified (excess 0.638
against 0.041), 3.5 would be certified (0.126 against 0.192).

## Main results (n = 57, cubic model; full table in `out/results.json` and Supplemental Table "learn_ibm")

- Training range: the standard 90 % intervals cover 0.904 of new emulated site labels and 0.100 of the true ones
  (m_s: 0.9 and 0.1 of 10 couplings); width 0.09 tau; miss of m_s up to 3.05 tau.
- Test range 1.1-1.4: coverage of the truth 0 (sites and m_s); miss 4.5-8.8 tau (27-53 %); predictions within 1.4 %
  of the new emulated labels; coverage of the new emulated labels only 0.31 (input shift).
- Exact-label control: miss at most 0.20 tau (0.1-1.2 %) in the test range: the miss is label error.
- Label filter: m_s certified at its own energy at Jz = 4.0, 5.0, 6.0 only (3 of 14); site labels at 6.0 only; in
  the test range the energy interval of m_s is >= 11.3-17.3 tau wide, of the bulk site >= 35 tau. The filter answers
  no test query; its answers miss the truth by <= 0.44 % (0.07 tau). It also drops 3.0 and 3.5 (labels within 0.32
  and 0.16 tau), 3.5 and 2.2 only for lack of a map row.
- Every model evaluated in the training range (cubic, perceptron, null) misses the true m_s by more than tau/2 at
  Jz = 1.6-2.5 and by less than tau/2 at 3.0-6.0 (`out/descriptive.json`). The null's intervals (0.47 tau) cover
  0.50 of the true m_s in range: in-range coverage of the truth measures width against bias.
- Device points (Jz = 1.2, 1.6, 4.0): outside the emulation-calibrated intervals; none certified at its energy.
- Small perceptron (n = 57): training range 0.926 new emulated / 0.200 truth; test range 0.338 / 0.000, miss
  4.4-8.5 tau; its exact-label control misses by up to 2.3 tau (model error larger than the cubic's). n = 115
  (test range only): 0.933 / 0.000.
- Dataset paper's architecture (n = 57, test range only; run time 7005 s): 0.425 new emulated / 0.000 truth, miss
  4.3-8.2 tau (26-49 %); exact-label control misses 1.0-3.1 tau (6.2-18.9 %) on our 10 training couplings.
- Nearest-neighbour null: test range 0.785 (n = 57) / 0.998 (n = 115) of new emulated labels, 0 truth.

## Also here

- `code/widths_huang.py`, `out/widths_huang.{txt,json}`: absolute widths of the benchmark intervals (from
  `../learning/analysis/learn_M*_D_O.json`), CSC averages 1.22-1.53 tau, single bonds 6.74-12.11 tau.
- `code/consistency_huang.py` (written as a separate cross-check, re-executed here):
  the energy implied by the 31 bond labels of the benchmark; per-label shifted sets imply 95-287 times the declared
  excess or energies below E0; realistic labels 0.999-1.000.
- `crosschecks/` (renamed 2026-11-04): separate-code exact-diagonalization checks `prop2_attack.py` (n = 8
  miniature of the benchmark with a one-state adversary) and `thm_attack.py` (Theorems 1-3, Lemmas A-B on small
  systems), with their outputs; `adv_consistency_output.txt` is the output of `code/consistency_huang.py`. Both
  scripts were re-executed on 2026-11-04 (`python -I -B prop2_attack.py`, 171 s; `python -I -B thm_attack.py`, 275 s);
  the outputs are identical to the stored ones (kept in `crosschecks/stored_before_rerun/`) except the runtime line.
  The paper quotes from them the one-state bond coverage 0.91-0.92 and the factor 1.8-4.1.

## Not done

- No realizable (one-state) adversary on the n = 20 benchmark itself: it would need new diagonalization runs.
- No test on the dataset's own labels or its 45 training points (not available).
- The dataset paper's architecture at n = 115 (stopped for cost) and in the training range (design: test range only).

SHA-256 of every file: `SHA256SUMS.txt`.
