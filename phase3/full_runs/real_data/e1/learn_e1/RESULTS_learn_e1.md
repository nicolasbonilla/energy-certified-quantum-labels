# Constructive test (f3) on the E1-extended sets: SECONDARY analysis

Declaration Sec. 3: "the set S of Sec. 7 (f3) is fixed WITHOUT them (the E1-extended set is reported as secondary if
E1 finishes)"; Sec. 12, line 17. Declaration SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa`. Run on 2026-11-12, after every result of the
primary analysis was known; it decides nothing and replaces nothing.

- Sets and intervals: `S_sets_E1.json` (SHA-256 `e62a4df738166d76998e5893473c24b50e6489946d36fb1cb3c4a8e9a46137e3`), written by `make_sets_e1.py` from the outputs of the
  declared map code run with the E1 certificates (`e1/map_e1/S_sets.json`, key `secondary_E1`; `e1/map_e1/map_rows.json`,
  field `exact_e1`). Nothing is recomputed there.
- Run: the declared entry point `code/run_learn.py`, unchanged (stages `f3` and `f2`), with `--sets` and `--out` pointing
  to this folder. Same rule, same seed (1845216616), same generator call `default_rng([seed, n, c])`, same models, same
  thresholds. Times: `run_times_utc.txt`.

## Identity checks

- n = 57: the E1-extended sets and their exact intervals equal the declared ones (E1 added intervals only at Jz = 3.2
  and 3.3, both wider than tau), so the test is the same test: 40758 numbers of the n = 57 block compared with
  `out/learn/f3_constructive.json`, largest absolute difference 0.0e+00, other differences: none.
- (f2): the floor uses the explicit-state (lower) widths, which E1 does not change: 572 numbers compared with
  `out/learn/f2_floor.json`, largest absolute difference 0.0e+00, other differences: none.

## n = 57

E1-extended sets: |S| = 26, |S_3/4| = 23, |S_1/2| = 18; the most stringent nested set with at least 15 couplings is S_1/2.
Declared sets (stored certificates only): |S| = 26, |S_3/4| = 23, |S_1/2| = 18.

| set | couplings | train / cal / query | model | (W): splits with 2q <= tau at every query | (C): pairs with the truth inside | 2q (tau): min / median / max | greatest miss (tau) | min of 2q over the widest calibration interval | outcome |
|---|---|---|---|---|---|---|---|---|---|
| S | 26 (3.5-6.0) | 6 / 12 / 8 | M1 | 6 of 200 (rule not met) | 1600 of 1600 | 0.906 / 1.356 / 1.564 | 0.212 | 1.499 | FAIL (M1 and M2 together) |
| S | 26 (3.5-6.0) | 6 / 12 / 8 | M2 | 6 of 200 (rule not met) | 1600 of 1600 | 0.916 / 1.333 / 1.546 | 0.211 | 1.185 | FAIL (M1 and M2 together) |
| S | 26 (3.5-6.0) | 6 / 12 / 8 | M0 (control) | 6 of 200 (rule not met) | 1600 of 1600 | 0.889 / 1.317 / 1.432 | 0.156 | 1.494 | FAIL |
| S_3/4 | 23 (3.8-6.0) | 6 / 12 / 5 | M1 | 50 of 200 (rule not met) | 1000 of 1000 | 0.815 / 1.056 / 1.163 | 0.157 | 1.495 | FAIL (M1 and M2 together) |
| S_3/4 | 23 (3.8-6.0) | 6 / 12 / 5 | M2 | 66 of 200 (rule not met) | 1000 of 1000 | 0.822 / 1.020 / 1.137 | 0.137 | 1.288 | FAIL (M1 and M2 together) |
| S_3/4 | 23 (3.8-6.0) | 6 / 12 / 5 | M0 (control) | 50 of 200 (rule not met) | 1000 of 1000 | 0.817 / 1.040 / 1.083 | 0.121 | 1.505 | FAIL |
| S_1/2 | 18 (4.3-6.0) | 4 / 9 / 5 | M1 | 200 of 200 | 1000 of 1000 | 0.586 / 0.733 / 0.857 | 0.137 | 1.271 | PASS (M1 and M2 together) |
| S_1/2 | 18 (4.3-6.0) | 4 / 9 / 5 | M2 | 200 of 200 | 1000 of 1000 | 0.562 / 0.719 / 0.856 | 0.149 | 1.163 | PASS (M1 and M2 together) |
| S_1/2 | 18 (4.3-6.0) | 4 / 9 / 5 | M0 (control) | 200 of 200 | 1000 of 1000 | 0.599 / 0.735 / 0.761 | 0.090 | 1.500 | PASS |

Descriptive lines (post hoc, no rule):

- S: 26 couplings, Jz = 3.5-6.0; exact intervals (with E1) 0.217-0.911 tau wide; greatest miss of a public label in the set 0.175 tau; the true m_s changes over the set by 0.598-0.621 tau; labels or truths outside their exact interval: none.
- S_3/4: 23 couplings, Jz = 3.8-6.0; exact intervals (with E1) 0.217-0.701 tau wide; greatest miss of a public label in the set 0.121 tau; the true m_s changes over the set by 0.462-0.476 tau; labels or truths outside their exact interval: none.
- S_1/2: 18 couplings, Jz = 4.3-6.0; exact intervals (with E1) 0.217-0.491 tau wide; greatest miss of a public label in the set 0.082 tau; the true m_s changes over the set by 0.294-0.301 tau; labels or truths outside their exact interval: none.

## n = 115

E1-extended sets: |S| = 27, |S_3/4| = 25, |S_1/2| = 18; the most stringent nested set with at least 15 couplings is S_1/2.
Declared sets (stored certificates only): |S| = 21, |S_3/4| = 21, |S_1/2| = 10.

| set | couplings | train / cal / query | model | (W): splits with 2q <= tau at every query | (C): pairs with the truth inside | 2q (tau): min / median / max | greatest miss (tau) | min of 2q over the widest calibration interval | outcome |
|---|---|---|---|---|---|---|---|---|---|
| S | 27 (3.4-6.0) | 6 / 12 / 9 | M1 | 15 of 200 (rule not met) | 1800 of 1800 | 0.720 / 1.364 / 1.530 | 0.192 | 1.398 | FAIL (M1 and M2 together) |
| S | 27 (3.4-6.0) | 6 / 12 / 9 | M2 | 15 of 200 (rule not met) | 1800 of 1800 | 0.742 / 1.312 / 1.459 | 0.161 | 1.442 | FAIL (M1 and M2 together) |
| S | 27 (3.4-6.0) | 6 / 12 / 9 | M0 (control) | 15 of 200 (rule not met) | 1800 of 1800 | 0.738 / 1.290 / 1.391 | 0.124 | 1.434 | FAIL |
| S_3/4 | 25 (3.6-6.0) | 6 / 12 / 7 | M1 | 42 of 200 (rule not met) | 1400 of 1400 | 0.734 / 1.113 / 1.226 | 0.151 | 1.437 | FAIL (M1 and M2 together) |
| S_3/4 | 25 (3.6-6.0) | 6 / 12 / 7 | M2 | 43 of 200 (rule not met) | 1400 of 1400 | 0.743 / 1.083 / 1.178 | 0.128 | 1.435 | FAIL (M1 and M2 together) |
| S_3/4 | 25 (3.6-6.0) | 6 / 12 / 7 | M0 (control) | 43 of 200 (rule not met) | 1400 of 1400 | 0.738 / 1.083 / 1.117 | 0.099 | 1.443 | FAIL |
| S_1/2 | 18 (4.3-6.0) | 4 / 9 / 5 | M1 | 200 of 200 | 1000 of 1000 | 0.405 / 0.677 / 0.821 | 0.108 | 1.314 | PASS (M1 and M2 together) |
| S_1/2 | 18 (4.3-6.0) | 4 / 9 / 5 | M2 | 200 of 200 | 1000 of 1000 | 0.408 / 0.666 / 0.836 | 0.120 | 1.296 | PASS (M1 and M2 together) |
| S_1/2 | 18 (4.3-6.0) | 4 / 9 / 5 | M0 (control) | 200 of 200 | 1000 of 1000 | 0.416 / 0.625 / 0.709 | 0.056 | 1.329 | PASS |

Descriptive lines (post hoc, no rule):

- S: 27 couplings, Jz = 3.4-6.0; exact intervals (with E1) 0.144-0.902 tau wide; greatest miss of a public label in the set 0.118 tau; the true m_s changes over the set by 0.611-0.635 tau; labels or truths outside their exact interval: none.
- S_3/4: 25 couplings, Jz = 3.6-6.0; exact intervals (with E1) 0.144-0.741 tau wide; greatest miss of a public label in the set 0.096 tau; the true m_s changes over the set by 0.515-0.532 tau; labels or truths outside their exact interval: none.
- S_1/2: 18 couplings, Jz = 4.3-6.0; exact intervals (with E1) 0.144-0.496 tau wide; greatest miss of a public label in the set 0.062 tau; the true m_s changes over the set by 0.276-0.282 tau; labels or truths outside their exact interval: none.

## Reading (n = 115, with the certificates of the extension E1)

- S_1/2 (18 couplings, Jz = 4.3-6.0; 4 / 9 / 5): PASS. (W) 200 of 200 splits (M1) and 200 of 200 (M2), (C) 1000 of 1000 and 1000 of 1000 pairs;
  2q = 0.405-0.836 tau over M1 and M2. Control M0: PASS (200 of 200, 1000 of 1000; 2q = 0.416-0.709 tau).
- S_3/4 (25 couplings, Jz = 3.6-6.0): FAIL on (W): 42 and 43 of 200 splits (M1, M2); 2q up to 1.226 tau.
- S (27 couplings, Jz = 3.4-6.0): FAIL on (W): 15 and 15 of 200 splits (M1, M2); 2q up to 1.530 tau.
- (C) holds in every pair of every set and model. The floor of (f2) is respected in every split (0 violations).
- The same three limits as for the primary result apply: the control model passes wherever M1 and M2 pass; the true
  m_s changes little over the set; the test fails on width on the full certified set and on the 3/4 set.
- This analysis was run after the primary results were known. It is secondary, as declared; it is not a
  replication on independent data (the 115-qubit labels were already used by the declared secondary run).

