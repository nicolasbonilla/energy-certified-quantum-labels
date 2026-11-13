# real_data: DEVIATIONS

Dated notes on anything learned or done after the hash of `DECLARATION.md` (SHA-256
`6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa`, hashed 2026-11-12T19:22:32Z).
No rule of the declaration is changed by anything below.

## 2026-11-12, task `rd-map` (the map on the real data: Secs. 2, 3, 4, 6 and gates G1-G7)

The declaration hash was checked against `DECLARATION.sha256` before anything was read. The sealed code ran once, from
2026-11-12T19:28:57Z to 19:31:01Z UTC (`out/run_map_stdout.txt`), with its default options.

1. **No sealed file was changed; no defect that needed a fix was found.** Old SHA-256 = new SHA-256 for every file of `code/` and
   `tests/` listed in Sec. 11 of the declaration (32 files, hashed again after the run). The six files of the map:
   - `code/map_common.py`  `ec8f92a77930571855c53e539fc8b75907214118c2c949664f1ba039316f639d` (unchanged)
   - `code/map_certs.py`  `3922350fea0861470d6338bfaa6fb6fe25853cac56cf8b3c83f4ffa4a19b6765` (unchanged)
   - `code/map_stored.py`  `e1214cf36f5a3c088b44a2d5155b33be8c3b8c1ab34aab7fba4874eec5ba0728` (unchanged)
   - `code/map_tables.py`  `a1c04230ef8b5db38610c1cd5ef2d82e082a1f4620e2049d258cf8b2461f0fe3` (unchanged)
   - `code/map_gates.py`  `5f1f47a4b0b8e7193e41f936c4084c5be60fe8697d4632041fdb05005b8dc292` (unchanged)
   - `code/run_map.py`  `199e5b0a0a6c0851a7862680fe7ef040b3b5eccc62391a01917069cb9cd1866d` (unchanged)
2. **Gate G1 is NOT COMPLETE (no rule changed).** The gate as declared is the re-run of `code/convert_real_data.py` on the pinned
   archive. That converter passes every data file through a static inspection and then a restricted unpickler (whitelisted
   constructors only). The task `rd-map` was instructed to unpickle nothing, so `--g1-rerun` was not used. Checked instead: the
   SHA-256 of the three converted files against `converted/SHA256SUMS.txt` and Sec. 11, and of the archive against its pinned value
   (`13aa8e69...dedbb91`); all equal. To complete G1, a task that is allowed to run the converter runs
   `python -B -I code/run_map.py --g1-rerun --out <new folder>` (or the converter alone into a scratch folder) and compares the
   three hashes.
3. **Gate G6, first part, is NOT COMPLETE, with nothing checked.** The declared selection (22 NOT CERTIFIED rows within 0.3 of a J*,
   10 rows drawn with the seed 1845216616) has 150 witness components; none has its tensors on the laptop (the six tensor files are
   states of n = 57, Jz = 1.6), and Sec. 9 of the declaration excludes cloud access. The sealed summary line reads "pass on what could
   be checked; not complete"; since nothing was checked, the results report it as NOT COMPLETE only. 280 of the 439 NOT CERTIFIED rows
   use an energy re-evaluated at another coupling and carry the mark; the other 159 do not. The second part of G6 passed (472 rows,
   smallest margin above E0: 9.8e-6). Post hoc supplement, not the gate (`checks/g6_supplement.py`): the 4 (row, component) pairs with
   tensors among all NOT CERTIFIED rows (m_s, n = 57, Jz = 1.5, 1.6, 1.6, 1.7) and the six tensor states at Jz = 1.5 and 1.7 agree
   with the linear rule to 1.6e-13.
4. **Extension E1 was not available when the map ran** (`real_data/e1/` held no certificate at 19:31Z). The results have no E1
   column. Caution for the task that adds it: with certificates in `e1/` the sealed code adds the key `secondary_E1` to
   `S_sets.json`, so the SHA-256 of that file would differ from the one already fixed
   (`45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4`), and the code refuses to overwrite it. Run the E1 column with
   another `--out` folder; S, S_3/4, S_1/2 and S_p do not depend on E1 by construction.
5. **Output name.** The sealed code writes the 700 rows to `out/map_rows.json`. The file asked of this task, `out/map_real.json`, is
   built from it by `results/make_results_map.py` (copy, and outward rounding for display in `results/RESULTS_map.md`; no status,
   interval or threshold is recomputed).
6. **Files added after the hash by this task** (own code; none is imported by the sealed code; none changes a rule):
   - `checks/spotcheck_exact_intervals.py`  `0f80f04d0233707d7fee676c00dd907c4fa38c5fefda622d9df19a79a2f33bb9`
   - `checks/g6_supplement.py`  `810ca27b74e28b1ee572e96e6712ecd25bef58f9a0dcb9deb9b035c9af29f998`
   - `checks/finalize_rd_map.py`  `6d6fe378e8c472da9a13d1fbb749bdbf74e57fe438e2af4b20f5ed4fc09c5522`
   - `results/make_results_map.py`  `f0cbc7829046601c7bd4b05807597d3b1d440e03426286d852aa11d113a5de24`
7. **Things noticed in the sealed code and left as they are** (they change no number of this run): (a) `map_gates.g6_linear` returns
   `pass = True` when no component could be checked (item 3); (b) `map_tables.write_s_sets` changes the content of `S_sets.json`
   when E1 certificates exist (item 4).
8. **A like-for-like count that differs from item F9 of the declaration, for a stated reason.** At n = 115 the like-for-like filter
   keeps 30 m_s labels (J*_s = 3.1), because the interpolated thresholds also pass Jz = 3.1 and 3.2; item F9 had counted 28 from
   Jz = 3.3, at the couplings of the stored map only. Both are like-for-like numbers under the sector hypothesis; neither is a
   property of the real labels.
9. **Post hoc checks added by this task (not declared; they decide nothing):** the independent recomputation of the 200 exact rows
   (`checks/spotcheck_exact_intervals.py`: 200 of 200 identical as exact rationals); the containment of every explicit witness
   interval in the exact interval of its row (`checks/consistency_witness_inside_exact.txt`: 108 rows, 0 violations).

## 2026-11-12, task `rd-predict` (the predictions on the real labels: Sec. 5, and the n = 19 comparison of Sec. 6)

The declaration hash was checked against `DECLARATION.sha256` before anything was read, and
`python -B -I checks/make_manifest.py --check` gave 69 lines of Sec. 11 equal to the files on disk and 0 different, before
and after the runs.

1. **No sealed file was changed; no code defect was found.** `code/run_predict.py` (`41c83978...9159470b`),
   `code/rd_predict.py` (`75dd603f...7d21b406`), `code/rd_common.py` (`6efde030...edb3e`), `code/n19_curves.py`
   (`76b74ee9...9259e4`) and `out/n19/n19_curves.json` (`1c8378ec...835470`) have the SHA-256 of Sec. 11.
2. **The sealed code was run twice (no rule involved).** Run 1, 2026-11-12T19:28:35Z to 19:28:39Z UTC, started before the
   map task had written `out/S_sets.json`; the sealed code then reports the kept-set part of the n = 19 comparison of
   Sec. 6 as not available. Run 2, 19:36:08Z to 19:36:10Z UTC, with `out/S_sets.json`
   (`45308c52...9610ab4`, equal to `out/S_sets.sha256`) in place, is the one reported. The two outputs are identical
   except for that part (compared key by key): run 1 `a2a31c241a169bea86066b3559318b6917c4be66405a437d4765226f0f3837f6`
   (`out/predict/first_run_before_S_sets/`), run 2 `04be4924ea62f10c201afa8a713fb365d4308af67de74920d09ef450f92c2ac8`
   (`out/predict/predict_results.json`). For the record: the P1-P5 numbers of run 1 were on screen before S existed; S
   is computed by the map code from certificates and energies and does not depend on them, and this task did not touch it.
3. **Output name.** The sealed code writes `out/predict/predict_results.json`. The file asked of this task,
   `out/predict_real.json`, is written by `checks/rd_predict_make_results.py`: the sealed output verbatim (asserted key by
   key), plus provenance, the independent check and the post hoc lines under separate keys.
4. **Files added after the hash by this task** (own code; none is imported by the sealed code; none decides anything):
   - `checks/rd_predict_independent.py`  `17f044e50fcf9325831435417322c1e3ea20b65b2f0f8fcc0d0a8572eca85083`
     (independent recomputation of P1-P5 and of the n = 19 comparison, with the n = 19 exact diagonalization redone from
     scratch; reads `converted/` only after checking the declaration hash and the pinned hashes of the files; largest
     difference from the sealed output 2.2e-16);
   - `checks/rd_predict_make_results.py`  `df8e468ead75cffb882989f9be95b606a4ef6ac24d2f54051085aa981276866b`
     (writes `results/RESULTS_predict.md`, `out/predict_real.json`, `results/SHA256SUMS_predict.txt`; reads `converted/`
     only for E_first and E_real of one post hoc line).
5. **Post hoc lines added by this task (not declared; they decide nothing; Sec. 8 of `results/RESULTS_predict.md`):** P5
   with the authors' DMRG as truth at every coupling and with the curve recomputed from scratch (same outcome); the ratio
   of the bias to the chord; curve against chord coupling by coupling; the list of the (item, coupling) pairs that are not
   on the Neel side; the couplings where D increases; the factor by which the basis optimization lowers the energy error.
6. **A descriptive sentence of the declaration against the data (no rule involved).** Sec. 5 (P5) says that the rotation
   "lowers the energy error per site five- to tenfold". From the public files (E_first against E_real): 2.8 to 8.9 times
   at n = 57 (median 6.7); 6.6 to 175 times at n = 115 (median 29.6; above ten at 45 of the 50 couplings). The sentence
   enters no rule and the outcome of P5 does not depend on it; a paper sentence built on it should use the measured factors.
7. **Blindness of two lines, stated more precisely than Sec. 5 does (no rule involved).** For the sites, the 50 couplings
   are ordered by D exactly as by the miss of m_s (seen, F7) at both sizes, so the rank correlation of P4 for the sites
   equals the seen one to six decimals; and the first-look file held the site fraction of P1-P3 at all 50 couplings
   (F2), printed for 14 (F8). For the sites, P1-P4 are confirmations by a fixed pipeline. Edges, second neighbours and
   loops had not been compared with their references before the hash.
8. **Gate G1 stays NOT COMPLETE for these results** (item 2 of the task `rd-map` above); it is printed with them.

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
   - `results/make_results_learn.py`  `d2f9bdbc8c6e1f91f8c7b0fd731ab5f6dbd51f84a09a08138974121005cb973a`
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
