# bias_law: exploratory bias-versus-energy analysis (2026-11-06)

**Exploratory.** Found after the data were known, no prior declaration. The paper says so (Sec. V, Methods, Limitations).
Nothing here was a blind test.

- `code/bias_law.py`: reads stored outputs only (`../method/out_20261030T003230Z/out`, `../qpu/analysis/analysis.json`,
  `inputs/`) and writes `out/results.json` and `paper/figures/data_biaslaw/*.dat`. Seconds on a laptop.
- `code/n19b.py`: produced `inputs/n19_curves.json` (exact n = 19, sector dimension 75,582, top-D truncation, 26 levels).
- `code/generality.py`, `code/instance_test.py`: produced `inputs/generality.txt`, `inputs/instance_test.txt` (n <= 20).
- Run: `python -I phase3/full_runs/bias_law/code/bias_law.py <J_next_paper root>`.

Reading guide: `n19_curve`, `device`, `families_57_to_115`, `no_reference_115`, `learner` are the positive side;
`classical_tie_115`, `published`, `other_models`, `internal_checks` are the limits. `nulls` decides the framing: the corrected
label (0.090 tau at n = 115) does not beat a classical a + b/sqrt(n) extrapolation (0.014 tau), and a parameter-free chord
between the ground and Neel states does as well or better at n = 115 and on the device.

Done later, under declared rules: new couplings and disordered lattices at n = 57, in `../final_tests/` (RESULTS.md).
Not done: truth-free estimate of E0 beyond the a n + b edges fit at the uniform model.
