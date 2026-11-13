# real_data/e1/learn_e1: the constructive test (f3) on the E1-extended sets (SECONDARY)

Written 2026-11-12 by the rewrite task `rw-L` (learning writer), after every result of the primary analysis was known.
Declaration: `real_data/DECLARATION.md`, SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa`,
Sec. 3 ("the E1-extended set is reported as secondary if E1 finishes") and Sec. 12, line 17. This folder decides
nothing and replaces nothing; nothing was written under `real_data/out/`, `code/`, `converted/` or `source/`.

## What was run

1. `python -B -I make_sets_e1.py` (own code, in this folder). The declared entry point `code/run_learn.py` reads the
   keys `S`, `S_3_4`, `S_1_2`, `S_p` and `intervals` of a sets file and ignores the key `secondary_E1` that the declared
   map code writes when E1 certificates exist; and the `intervals` of `e1/map_e1/S_sets.json` hold the exact intervals
   of the stored certificates only. `make_sets_e1.py` therefore writes `S_sets_E1.json` (+ `.sha256`) in the format of
   the declared code: the four sets are the `secondary_E1` sets copied from `e1/map_e1/S_sets.json`, and the `exact`
   interval of each coupling is the field `exact_e1` of the m_s row of `e1/map_e1/map_rows.json`; `tau`, `q`, `lower`
   and `outer_like` are copied unchanged. Nothing is recomputed (no interval, no set, no threshold). The two input
   files are checked against `e1/map_e1/SHA256SUMS_map.txt` first.
2. The declared entry point, UNCHANGED, with one thread:
   `python -B -I code/run_learn.py --hash=<H> --stage=f3 --sets=<this folder>/S_sets_E1.json --out=<this folder>`
   (2026-11-12T22:33:03Z to 22:33:24Z UTC) and the same with `--stage=f2` (22:33:24Z to 22:33:26Z UTC).
   Same rule, same seed (1845216616), same generator call `default_rng([seed, n, c])`, same models, same thresholds.
   The declared loader re-checked the sets file (nested sets; S_p = the most stringent set with at least 15 couplings;
   every member has an exact interval within its fraction of tau). SHA-256 of `code/run_learn.py`, `code/rd_f23.py`
   and `code/rd_common.py` before and after the run: `8332d1f0...c004f`, `3512c220...c9704`, `6efde030...edb3e`, the
   values of Sec. 11 of the declaration.
3. `python -B -I summarize_e1.py` (own code): comparison with the primary outputs, tables, descriptive lines
   (`RESULTS_learn_e1.md`, `summary_e1.json`).

## Outcome in three lines

- n = 57: E1 added exact intervals only at Jz = 3.2 and 3.3, both wider than tau; sets and intervals are those of
  the declaration, and the n = 57 block of `f3_constructive.json` equals `out/learn/f3_constructive.json` number by
  number (40758 numbers, largest difference 0). The floor (f2) is unchanged as well.
- n = 115: |S| = 27 (Jz 3.4-6.0), |S_3/4| = 25 (3.6-6.0), |S_1/2| = 18 (4.3-6.0) = most stringent set with at least
  15 couplings. S_1/2: PASS (200 of 200 splits and 1000 of 1000 pairs for M1 and M2; 2q = 0.405-0.836 tau; control
  M0 passes). S_3/4: FAIL on width (42 and 43 of 200). S: FAIL on width (15 and 15 of 200). (C) holds everywhere.
- Same three limits as the primary result; run after the primary result was known; not a replication on
  independent data.

Files: `make_sets_e1.py`, `make_sets_e1_stdout.txt`, `S_sets_E1.json`, `S_sets_E1.sha256`, `f3_constructive.json`,
`f2_floor.json`, `run_f3_e1_stdout.txt`, `run_f2_e1_stdout.txt` (stderr files empty), `run_times_utc.txt`,
`summarize_e1.py`, `summary_e1.json`, `RESULTS_learn_e1.md`, `SHA256SUMS.txt`, this file.
