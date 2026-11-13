
## 2026-11-12, task `rd-learn` (the learning tests on the real labels: Sec. 7, f1-f3)

The declaration hash was checked against `DECLARATION.sha256` before anything was read; `python -B -I checks/make_manifest.py --check` gave 69 lines of Sec. 11
equal to the files on disk and 0 different before the runs; `out/S_sets.json` existed with SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4`, equal to `out/S_sets.sha256`,
before any learning number was computed.

1. **No sealed file was changed; no code defect that needed a fix was found.** Hashed again after the runs and equal to Sec. 11:
   - `code/run_learn.py`  `8332d1f0628911be99b80ecc4c10877a6165b7fd4dd41d83a1ba0f5d866c004f` (unchanged)
   - `code/rd_f23.py`  `3512c22069365d3d2df7f2905bf4d14e2dcaf1ee518dda752db54019d6bc9704` (unchanged)
   - `code/rd_learn_ibm.py`  `9c65738a9d8f19ee0f11296e6dbc739a4a6bcada2439d6ade035d5e571ceab86` (unchanged)
   - `code/rd_prop2_cubic.py`  `694adaf0451ed9dedf3b3562c5b3c2b608b9688a89afb7c222aa5500515eb3fe` (unchanged)
   - `code/rd_learn_parts.py`  `83e2d7fb54f54dae2de30318cff0e5658beed64e70653996eb0f30b385fc692f` (unchanged)
   - `code/rd_common.py`  `6efde0302f750d3c9e0c9a86909fd86a221b63283250f7a59665275edeeedb3e` (unchanged)
   64 plain-file lines of Sec. 11 were hashed again after the runs: all equal.
2. **The sealed code was run once per stage.** `code/run_learn.py --stage=cheap` (f1_cheap, prop2, f2, f3, rules): 2026-11-12T19:55:38Z to 2026-11-12T19:56:28Z UTC. `code/rd_learn_parts.py
   --model=mlp_pilot3 --size=57 --part=ood` (the perceptron in the test range): 2026-11-12T19:55:35Z to 2026-11-12T20:25:33Z UTC (92 fits, 19.5 s per fit). Seed 1845216616.
3. **Three parts of (f1) were NOT COMPUTED, for cost (no rule changed; they are reported as not computed, never as passes):** the pilot perceptron in
   distribution at n = 57 (4050 fits, about 22 CPU-hours at the measured rate), the pilot perceptron at n = 115 (secondary), and the dataset paper's
   architecture 1 at n = 57 (92 fits, about 13 CPU-hours). L1, L2, L3, (f2) and (f3) do not use them (Sec. 12, line 10: decided on the cubic). To complete:
   `code/rd_learn_parts.py ... --part=i/k` and `--assemble=k` (the test-range piece is already in `out/learn/parts/`), `code/run_learn.py --stage=f1_ibm57`,
   then `--stage=merge` and `--stage=rules`.
4. **Output names.** The sealed code writes `out/learn/{results_cheap,prop2_cubic,f2_floor,f3_constructive,f1_rules}.json`. The files asked of this task,
   `out/learn_real.json` and `results/RESULTS_learn.md`, are written by `results/make_results_learn.py`: the sealed outputs verbatim under the key `sealed`,
   plus provenance, the independent check and the post hoc lines under separate keys; display with outward rounding; no declared outcome is recomputed.
5. **Files added after the hash by this task** (own code; none is imported by the sealed code; none decides anything):
   - `checks/rd_learn_independent.py`  `bae91241a61a705a8bb249d28d19d9636aea510aa0bf3ccfe81e9f6eea1b7cd5`
   - `results/make_results_learn.py`  `(its SHA-256 is in `results/SHA256SUMS_learn.txt`)`
6. **Things noticed in the sealed code and left as they are** (they change no declared outcome): (a) the derived script `rd_learn_ibm.py` keeps the stored
   script's blocks `certification`, `abstention` and `device_illustration`; on the real data the first two are like-for-like numbers (stored in-sector
   thresholds at E_real, couplings of the stored map only) and are reported as such, never as properties of the real labels; the third is not part of the
   declaration and is not used. (b) In the nearest-neighbour null, a held-out coupling has its two neighbours at the same distance up to rounding of k/10;
   which one is used is decided by that rounding. No rule depends on the null. (c) In the outputs of the derived scripts the key `emulated` denotes the
   real labels (as the README of the code states).
7. **Gate marks carried by these results (Sec. 12, line 14).** G1 NOT COMPLETE (item 2 of the task `rd-map`). G6, first part, NOT COMPLETE with nothing checked:
   it concerns every lower-version number of this task (the floor of (f2), L3, W_lo and 2q_lo of Proposition 2), because 33 (n = 57) and 33 (n = 115) of the 45
   training labels have an explicit-state interval that rests on re-evaluated energies. Post hoc robustness line (not the rule): with those widths set to 0
   the floor is still 2.86 / 2.65 / 2.50 / 2.38 tau (n = 57) and 2.52 / 2.36 / 2.23 / 2.13 tau (n = 115) at the four test queries. (f3) uses the exact intervals only and does not depend on G6.
8. **Post hoc lines added by this task (not declared; they decide nothing; Sec. 7 of `results/RESULTS_learn.md`):** the standard score |f - y| on the splits
   of (f3); a constant model on the same splits; the change of the true m_s over each nested set; the floor without the re-evaluated labels.
9. **Two descriptive sentences of the declaration against the data (no rule involved).** Sec. 7 says that between Jz = 4 and 6 the true m_s changes by
   0.4 tau: measured 0.388-0.398 tau (n = 57) and 0.364-0.373 tau (n = 115). Sec. 7 quotes a forecast of 0.71-0.76 tau for the width in [4, 6] from emulated labels:
   obtained on [4.0, 6.0] at n = 115, 0.859-0.999 tau (M1), wider than the forecast.
10. **Time.** The suggested 45 minutes were exceeded: the perceptron piece alone took 30 minutes of wall time on the shared laptop.
