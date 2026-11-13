# real_data/code: what each file does and how to run it

Code for the analysis of the public data of arXiv:2606.15983 under `../DECLARATION.md`. Python standard library and
numpy only. Nothing here unpickles anything and no code of the downloaded repository is imported or executed: the data
are the plain JSON files of `../converted/`.

**Rule kept by every script that reads `../converted/`:** it refuses unless `../DECLARATION.sha256` exists and holds
the SHA-256 of `../DECLARATION.md` (exit code 3, message `REFUSED: ...`). The unit tests use stored objects of this
project and synthetic numbers only.

## Files of the map (task `rd-code-map`: Secs. 2, 3, 4, 6, the sets of Sec. 7, gates G1-G7)

| file | what it does |
|---|---|
| `map_common.py` | paths and constants of Sec. 0 (sizes, the 50 couplings, training 1.6-6.0, test 1.1-1.4, 1.5 apart, tolerance, allowance 1e-6); the guard `declaration_guard()`; the loader of the converted files **by schema** (`parse_real` on a parsed object, `read_converted` / `load_real` on the files, guard inside): pairs matched by site pair, loops by site set, never by position; E_real, E_first, M_real (exact sum of the stored dyadic numbers), the seven labels, m_s and Czz_bar also as exact rationals. |
| `map_certs.py` | loader of the exact certificates (`*_cert.json` of the two rigor runs and of `final_tests/`; de-duplicated by SHA-256; kinds `m_s`, `Czz_bar`, `H`; a certificate is used only with its verification record and if `sum_k t_k - mu M_0 == E_claim` exactly). The exact interval of Sec. 2: pool of direct certificates and of pairs combined by concavity (m_s), every `Czz_bar` / `H` certificate as a bound at any target coupling (Czz_bar), evaluated at M in {M_real, M_0} with the stated allowances, capped at [-1, 1]; both tolerances; the largest energy at which a row stays CERTIFIED (exact), solved exactly. Everything in `fractions.Fraction`. |
| `map_stored.py` | the stored map through its own code (`map/laptop_analysis/code/analyze_map.py` and `hull.py`, imported, not changed): `outer(E)`, `inner(E)`, thresholds, states. Linear re-evaluation of a stored state's energy at another coupling; pools of in-sector states (own states where a chain of the label is stored, otherwise the two bracketing grid couplings re-evaluated); reference state R3 / R4; the NOT CERTIFIED side with q; like-for-like statuses and log-linearly interpolated thresholds; the truth rule of Sec. 0. |
| `map_tables.py` | one row per (size, coupling, label) with the three statuses; J* under each rule and the counts out of 45; the table "predicted from the figures versus obtained from the data" with its relations, the rule "confirmed by the data", claims C-A, C-B, C-C; accuracy factors in forms A and B; the filter table; the nested sets S, S_3/4, S_1/2 and S_p, written to `out/S_sets.json` with `out/S_sets.sha256` (format read by `rd_common.parse_sets`). |
| `map_gates.py` | gates G1-G7 as functions, and `apply_no_decision` (a failed gate turns the rows that depend on it into NO_DECISION). |
| `run_map.py` | **the entry point.** Guard first, then gates, rows, sets, tables, secondary rows (window at E_first; comparison variant), outputs. `run()` takes parsed data and is what the tests call on synthetic objects. |
| `../tests/test_map_stored.py` | tests against stored objects: (a) the stored map row by row, its J* and counts; (b) the 18 exact rows of the rigor table; (c) the stored device interval at Jz = 6.0; (d) concavity. |
| `../tests/test_map_synthetic.py` | tests on synthetic cases with known answers: guard, loader, a two-site model with closed-form certificates (also out of the sector, q > 0), q > 0 and q < 0 on the explicit side, the linear rule (against stored reference energies and stored tensors), every gate, tables, one end-to-end run of `run()`. |
| `../tests/run_map_tests.py` | runs both and writes `../tests/out/map_tests.txt`. |

## Other files in this folder

`convert_real_data.py`, `provenance_check.py`, `descriptive_checks.py` (task `real-data-setup`: archive to plain JSON,
provenance, descriptive checks). `rd_common.py`, `rd_predict.py`, `run_predict.py`, `rd_learn_ibm.py`,
`rd_prop2_cubic.py`, `rd_f23.py`, `run_learn.py`, `make_derived.py`, `n19_curves.py` and whatever that task adds
(task `rd-code-learn`: Secs. 5-7): see `README_predict_learn.md`. The map code does not import them; one test
cross-checks the two loaders and the format of `S_sets.json`.

## How to run

```
# unit tests (gate G8; no real datum; about 30 s; --slow also re-proves one stored certificate)
python -B -I ../tests/run_map_tests.py --slow

# the map on the real data (only after the declaration is hashed)
python -B -I run_map.py                       # default output folder ../out
python -B -I run_map.py --g1-rerun            # also re-runs the converter on the pinned archive (gate G1 in full)
python -B -I run_map.py --no-g5-reprove       # skips the exact re-proof of the deciding certificates (G5 "skipped")
```

Use `python -B` (no byte code is written into the stored run folders; the code also sets this itself) and `-I`
(isolated mode; with it this machine loads numpy 1.26.4, without it 2.2.6: both work, numpy is used only by the
stored map code and by one bisection). Two threads are enough: `OMP_NUM_THREADS=2`.

Run time measured on a full-size synthetic data set (2 sizes x 50 couplings x 7 labels): loading the certificates
9 s, the stored map 1.5 s, all rows, tables and gates without the re-proofs under 10 s. The re-proof of a deciding
certificate takes about 8 s (seven-site clusters) to about a minute (nine-site clusters).

## Outputs of `run_map.py` (deterministic JSON, sorted keys, no time stamp)

| file | content |
|---|---|
| `S_sets.json`, `S_sets.sha256` | nested sets and m_s intervals at every coupling; written first; an existing file with another content is not overwritten (`--replace-sets` to force) |
| `map_rows.json` | 700 rows: eps_real, de_real, q, like-for-like status with f_in, f_out, explicit-state side with its witness components, exact interval as rationals with the certificates behind it, widths over both tolerances, largest eps that keeps the row certified |
| `map_summary.json` | J* and counts, predicted versus obtained (171 rows, relations, stored J* against J*_s, the rule, claims), accuracy factors, filter tables, certificate counts, flags, SHA-256 of the code |
| `map_secondary.json` | window at E_first (m_s, like-for-like); comparison variant |
| `map_gates.json` | G1-G7 with every number |
| `map_tables.md`, `SHA256SUMS_map.txt` | the main tables as text; hashes of the outputs |

## Readings fixed in the code (dictionary `RULES` of `run_map.py`; listed as ambiguities in the task report)

- Grid couplings = the 16 couplings of `map/DECLARATION.md` Sec. 3; a grid coupling is bracketed by itself.
- "A coupling with a stored chain" = a chain of the row's own label and size (a row of `summary_map.json`).
- Truth: E0 = this project's reference at the 18 + 16 couplings of `summary_map.json`; O_GS = this project's reference
  where `summary_map.json` has a row for that label, size and coupling (the reading of `rd_common.project_refs` too);
  otherwise the authors' DMRG.
- Allowance on M_real taken certificate by certificate (the result then holds for every M within 1e-6).
- CERTIFIED (exact) only inside [3.4, 6.0] (n = 57) and [4.0, 6.0] (n = 115), for both labels; a Czz_bar interval
  within tau outside that range is reported and flagged, not counted.
- Stored J* = `J_star_central` of reading 1. A training coupling without a status is not a certified point.
- Extension E1: certificates found in `../e1/` (same file format, each with its `*_ver.json`) feed a separate column
  and separate secondary sets; S, S_3/4, S_1/2, S_p never use them.

SHA-256 of every code file: `SHA256SUMS.txt` (this folder).
