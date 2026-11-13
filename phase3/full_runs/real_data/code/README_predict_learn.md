# real_data/code: predictions and learning tests (DECLARATION.md Secs. 5, 6 (n = 19 comparison), 7)

Written 2026-11-12 by the task `rd-code-learn`, before the declaration was hashed and **without opening
`converted/*.json`** (schema only: `convert_real_data.py`, `checks/convert_stdout.txt`, the set-up report). Tested on
synthetic numbers and on the stored emulated labels (gate G8). SHA-256 of every file: `SHA256SUMS_predict_learn.txt`.

## The gate

`run_predict.py`, `run_learn.py`, `rd_learn_ibm.py`, `rd_prop2_cubic.py` and `rd_learn_parts.py` stop with exit code 3
and the word `REFUSED` unless `real_data/DECLARATION.sha256` exists, its 64-hex token equals the SHA-256 of
`DECLARATION.md`, and the argument `--hash=<64 hex>` equals both. The only function that opens a converted file is
`rd_common.read_converted`; it needs the gate object and also checks the SHA-256 of the file against the value pinned
in Sec. 11 of the declaration. Seeds: `int(hash[:8], 16)` (Sec. 7), from the hash passed as an argument.

## Files

| file | what |
|---|---|
| `rd_common.py` | gate, seeds, loader of the converted data (pairs matched by site pair, loops by site set), the four families and seven labels, truth rule of Sec. 0, reader and checks of `out/S_sets.json`, label intervals for Proposition 2 |
| `n19_curves.py` | exact n = 19 (sector dimension 75,582) at the 50 couplings, recipe of `bias_law/code/n19b.py` lines 15-31 unchanged; no real datum; outputs in `out/n19/` |
| `rd_predict.py` | P1-P3 (`t_values`, `sign_test`), P4 (`D_value`, `spearman`, `p4_test`), P5 (`curve_value` = `n19b.f`, `p5_row`, `p5_summary`, `p5_rule`), comparators (chord, truth at n = 19), the n = 19 comparison of Sec. 6 |
| `run_predict.py` | **entry point** for Secs. 5 and 6 |
| `make_derived.py` | writes the two derived scripts from the stored ones by exact text operations |
| `rd_learn_ibm.py` | derived from `learning_ibm/code/learn_ibm.py`; changed only in the data loader (`--data=real` or `--data=emulated`) |
| `rd_prop2_cubic.py` | derived from `learning_ibm/code/prop2_cubic.py`; changed only in the data loader: labels, and label intervals read from `out/S_sets.json` |
| `rd_learn_parts.py` | operational: the realistic test of one model and size in pieces (same functions, same numbers) |
| `rd_f23.py` | (f2) floor, (f3) constructive test (splits, M1, M2, M0, both scores, pass rule), L1-L3 |
| `run_learn.py` | **entry point** for Sec. 7 |

`method/code/ml2.py` (regressors) and `map/laptop_analysis/code/analyze_map.py` are imported, not changed.

## Commands (after the hash; H = the SHA-256 of DECLARATION.md)

```
python -B -I code/run_predict.py --hash=H                 -> out/predict/predict_results.json   (seconds)
python -B -I code/run_learn.py --hash=H --stage=cheap     -> out/learn/: results_cheap.json, prop2_cubic.json, f2_floor.json,
                                                             f3_constructive.json, f1_rules.json   (about two minutes)
python -B -I code/run_learn.py --hash=H --stage=f1_mlp57 | f1_mlp115 | f1_ibm57 | merge | prop2 | f2 | f3 | rules
```
`run_predict.py` needs `out/n19/n19_curves.json` (present) and uses `out/S_sets.json` if it exists (kept set of the
filter). The stages `prop2`, `f2`, `f3` need `out/S_sets.json` **and** `out/S_sets.sha256` (Sec. 7: "written to a file
with its SHA-256 before any learning number is computed"); they refuse otherwise.

n = 19 (already run, 2 x 29 s): `python -B -I code/n19_curves.py <work> out/n19 run 11 59 2`, the same with `12 60 2`,
then `... merge`. Tests: `python -B -I tests/run_all.py` (about 45 s; output in `tests/out/predict_learn_tests.txt`).

### Cost of the neural models (measured on random labels of the right shape, one thread)

| job | fits | per fit | one process | suggested |
|---|---|---|---|---|
| perceptron, n = 57, test range and in distribution, real and DMRG labels | 2 x (46 + 45 x 45) = 4142 | about 7 s (16 s in the stored run) | 8 to 18 hours | `rd_learn_parts.py`, 6 to 8 pieces |
| perceptron, n = 115 (secondary) | 4142 | about 10 s | about 12 hours | pieces |
| architecture 1, n = 57, test range only, real and DMRG labels | 2 x 46 = 92 | about 520 s | about 13 hours | one process overnight |

```
python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=H --model=mlp_pilot3 --size=57 --part=ood
python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=H --model=mlp_pilot3 --size=57 --part=0/6   (... 5/6)
python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=H --model=mlp_pilot3 --size=57 --assemble=6
python -B -I code/run_learn.py --hash=H --stage=merge ;  python -B -I code/run_learn.py --hash=H --stage=rules
```

## Format of `out/S_sets.json` (written by `map_tables.write_s_sets`, read by `rd_common.parse_sets`)

```
{"schema": "p5-real-data-S-sets-v1", "declaration_sha256": "<64 hex>", "label": "m_s",
 "sizes": {"57": {
    "S":     [3.4, ...],      training couplings whose m_s row is CERTIFIED (exact), reference tolerance, stored certificates only
    "S_3_4": [...], "S_1_2": [...],        interval at most 3/4 and 1/2 of tau wide
    "S_p":   [...], "S_p_name": "S_1_2" | "S_3_4" | "S" | null,     the most stringent set with at least 15 couplings ([] if none)
    "intervals": {"1.1": {"tau": 0.06 |m_s^GS|, "q": (M_0 - M_real)/2,
                          "exact":      {"lo": .., "hi": .., ...} | null,   interval I = [-U_-, U_+] of Sec. 2
                          "lower":      {"lo": .., "hi": .., ...} | null,   labels of the two explicit witness mixtures ((1 - q) x hull)
                          "outer_like": {"lo": .., "hi": ..} | null},       like-for-like outer at E_real (indicative)
                  ... one record per coupling "1.1" .. "6.0"}},
  "115": {...}}}
```
`out/S_sets.sha256` holds the SHA-256 of the file. The reader refuses the file if it was written under another
declaration, if the sets are not nested, if a member has no exact interval or one wider than its bound, or if `S_p` is
not the declared choice; a certified coupling missing from a set gives a warning. Extra keys are ignored.

## What each analysis computes (rules as written in the declaration)

- **P1-P3.** Families: 57 / 115 sites, 64 / 132 edges, 87 / 185 second neighbours, 4 / 12 loops; Neel values eta_i,
  -1, +1, +1; t_x = (o_real - o_GS)/(o_Neel - o_GS); F = fraction of (item, coupling) pairs with t_x > 0 over the 50
  couplings; **holds iff F >= 0.95**, per family and size. Also: F per coupling, fraction with t_x <= 1, fraction with
  0 < t_x <= 1, number of undefined t_x (counted as not positive).
- **P4.** D(n, Jz) = mean over items of |o_real - o_GS|/(0.06 |o_GS|); **holds iff Spearman(D, Jz) <= -0.9** (average
  ranks for ties). The four families decide; m_s is printed next to them (seen before, F7).
- **P5.** `curve_value` is the function `f` of `n19b.py`; Delta, ratio, miss, raw miss, chord, truth at n = 19 at every
  coupling; **PASS iff mean miss <= 0.2 tau (n = 57) and <= 0.6 tau (n = 115) and every ratio in [0.75, 1.3] where the
  raw miss is at least 0.2 tau**, over the 50 couplings of each size; the 45 training couplings are reported.
- **Truth.** Sec. 0: this project's references where stored (`summary_map.json`: E0 and the seven label types),
  otherwise the authors' DMRG; single items (sites, pairs, loops) exist only in the authors' files. Sec. 7: the
  authors' DMRG at all couplings.
- **(f1).** `rd_learn_ibm.py`: cubic in 1/Jz (`ml2.fit_poly`), nearest neighbour, perceptron, architecture 1 (test
  range only); standard conformal, alpha = 0.1, plain jackknife; in distribution and out of distribution; control on
  DMRG labels. In its output the key `emulated` denotes the labels of the data source (the real labels). Its
  `certification` and `abstention` blocks compare the real energy with the stored in-sector thresholds: they are
  **like-for-like numbers, not properties of the real labels**. `rd_prop2_cubic.py`: Proposition 2(a), (b); upper
  version = exact interval where it exists, otherwise an indicative one, flagged (`upper_kind`: `exact`,
  `like_for_like`, `interpolated`), which can neither answer nor pin; lower version = the witness interval.
  `rd_f23.f1_rules`: L1, L2, L3 (each holds iff true at n = 57).
- **(f2).** floor = the k-th narrowest of the 45 lower widths, k = ceil(46 x 0.9) = 42; reported in tau(x) at every
  coupling, and held out (44 labels, k = 41) at every training coupling.
- **(f3).** Splits: `numpy.random.default_rng([seed, n, c])`, c = 0, 1, 2 for S, S_3/4, S_1/2; each split is one
  permutation of the sorted set: training couplings first, then calibration, the rest queries; 200 splits. M1: least
  squares on (1, 1/Jz); M2: least squares of 1 - y on (1/Jz^2, 1/Jz^4); M0: cubic in 1/Jz with ridge 1e-8 on every
  training label outside the calibration and query couplings. Score max(|f - lo|, |f - hi|); q = the
  ceil((m+1)(1-alpha))-th smallest; (W) and (C) as declared; **PASS iff (W) and (C) for both M1 and M2 on S_p at
  n = 57**. Secondary: `norm_literal` (|f - y|/sigma, sigma = the calibration label's own width) and `norm_interval`
  (worst case over the label's interval, sigma interpolated without that label).
