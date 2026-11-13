# Extension E1: what is computed and how (fixed before any E1 bound was computed)

Written on 2026-11-12 by the task `rd-e1`, after the dry run and **before the E1 scheduler was started**. Its SHA-256
is in `E1_SPEC.sha256`, the UTC time in `E1_SPEC_hash_time.txt`. Anything learned later goes, dated, to the end of
`HOW_TO_COLLECT.md` (section "Log"), not into this file. `real_data/DECLARATION.md` (SHA-256 `6dfbc568...a209ffaa`,
checked against `DECLARATION.sha256` before anything else) is not changed by E1.

## 1. Scope (real_data/DECLARATION.md Sec. 3, "Extension E1")

New exact certificates for the label m_s, in this order of priority: n = 57 at Jz = 3.3 and 3.2; n = 115 at
Jz = 5.0, 3.6 and 3.3. Laptop only, at most 8 hours of wall time in total, counted from the first start of the
scheduler (`out/T0.txt`). A coupling not finished within the cap is reported as not computed.

## 2. What is unchanged from rigor/DECLARATION_v2.md (SHA-256 `aac90b97...5b2d83db`)

- **Bound and verifier code:** `code/lb_opt.py`, `code/lbcore.py`, `code/verify_exact.py`, `code/graphs/hh_d5.json`,
  `code/graphs/hh_d7.json` are byte-identical copies (same SHA-256 as in the manifest of `DECLARATION_v2.md`); they
  take their paths as arguments, so no line was adapted.
- **Optimizer settings:** K = 32, maxiter = 600, betas = [30, 300, 3000, 30000, 100000], use_mu = true; vertex balls
  of radius 2 in stage A, edge balls of radius 2 in stage B. Libraries as on the cloud machine of the stored runs:
  numpy 2.2.6, scipy 1.13.1 (`python -B`, without `-I`; Python 3.11.4 against 3.11.2).
- **Lambda grid (Sec. 2 of v2):** every point of the stored map chain of the row and sign, plus lambda_dec x 0.85^k,
  k = 1, 2, 3, rounded to 2^-20, lambda_dec the chain point that minimizes (E_up - F)/(lambda S); the provable
  pruning u_lb(p) + min_q u_lb(q) > tau. `code/make_plan_e1.py` contains the loop body of `make_plan_v2.py` and
  first checks itself: fed with the stored v2 inputs it reproduces `rigor/outputs/grid_v2.json` (18 rows) and the
  stage-A entries of `plan_v2_A.json` (326) exactly.
- **Stage rule (Sec. 3 of v2):** stage A by branch-and-bound per side (points in increasing u_lb, one job per side
  at a time, a side stops when u_lb(next) >= best - 0.01 tau); only exactly verified bounds count; stage B when both
  sides of a row are done and the row is wider than 0.85 tau, at the best vertex-ball point of each side; caps of
  stage B as for the scopes of the same size (n = 57: 8 jobs, as S2; n = 115: 4 jobs and only if less than 2.5 h
  have passed since the first start, as S3); stage B of a row comes before stage A of the rows after it.

## 3. Readings fixed here (each is an input of the search; none can make a certificate wrong)

1. **The energy of a row is the public energy:** E_up := E_real + 1e-6, with E_real = `final_global_energy` of the
   group `skqd_random_flip` and 1e-6 the allowance of real_data/DECLARATION.md Sec. 2. In v2, E_up was the upper
   reading of the digitized energy of the stored map. The E1 certificates serve the rows of the real-data map, whose
   energy is E_real. With the digitized upper reading the unchanged pruning rule leaves **no point to compute** at
   n = 57, Jz = 3.3 and 3.2 (DMRG-referenced width 1.056 tau and 1.080 tau there; `plan_e1_stdout.txt`), the two
   rows that the declaration puts first; with E_real the DMRG-referenced widths are 0.958 tau and 0.977 tau. E_up
   enters the choice of points only (lambda_dec, pruning, order, stopping, the 0.85 tau trigger of stage B), in the
   in-sector form (mean magnetization M_0) used by v2. The five energies had been seen before (DECLARATION Sec. 1,
   F2). **This is a reading of the declaration, to be confirmed by the coordinator and entered in
   `real_data/DEVIATIONS.md`.**
2. **tau** of a row: the stored value of `summary_map.json` (0.06 |O_GS|, this project's reference), as in v2.
3. **Chains:** `map/laptop_analysis/out/chains` (the folder of the manifest of real_data/DECLARATION.md; the files
   are identical to those of `map/out_20261030T022613Z/out/chains`).
4. **No earlier certificate** exists at the five couplings, so every side starts without a bound.
5. **Verification:** every certificate is proved by the stored verifier `verify_exact.py` (the verifier of record;
   its record has the stored `*_ver.json` format) and, in addition, by the independent exact verifier `myverify.py`
   (SHA-256 `6015ebb5...`, the one of gate G5), after that verifier reproduced the stored verdict and the stored
   exact bound on two stored certificates in this task's own run (Sec. 4). A bound counts in the search only with
   an ok record of the stored verifier; a certificate that the second verifier does not confirm is marked DISPUTED,
   does not count and is not collected.
6. **Order:** rows are served in the order of priority of the declaration (v2 ordered by scope).
7. **Cap:** the scheduler starts no job in the last 10 minutes and stops the jobs still running at T0 + 8 h; an
   independent watchdog stops everything at T0 + 8 h + 2 min. A stopped job gives no certificate.
8. **Where the certificates are:** jobs write into `out/jobs/`; the record of the stored verifier is named
   `<id>_verify_exact.json` there, so that the declared map code does not see a half-finished E1. `collect_e1.py`
   copies every doubly verified certificate to `certs/` as `<id>_cert.json` + `<id>_ver.json` (the stored names),
   which is where `real_data/code/run_map.py` reads E1 from (clarification 17 of the declaration).

## 4. Dry run (scratch `paper/reviews/R10_2026-11-12/scratch/rd-e1/dryrun/`, nothing of it is under `real_data/e1/`)

| task (stored id) | bound here | stored bound | difference | time here / stored | stored verifier | independent verifier |
|---|---|---|---|---|---|---|
| `v2_n19_vball2_m_s_p4.0_l0.227502` | -25.181289039 | -25.181286787 | -2.3e-6 J | 65 s / 65 s | ok | ok |
| `v2_n57_vball2_m_s_p3.4_l0.305157` | -74.541455304 | -74.541454978 | -3.3e-7 J | 199 s / 271 s | ok | ok |

The n = 19 bound lies 5.3e-4 J below the exact sector ground energy of the stored exact diagonalization
(-25.180761443). The independent verifier reproduced the stored verdict, the stored exact bound (equal as rationals)
and the file hash on `v2_n57_eball2_m_s_p3.4_l0.305157` (nine-site clusters; 33 s against 691 s of the stored
verifier on the cloud machine) and on `v2_n115_vball2_m_s_p4.0_l0.272766` (17 s). The copy of the stored verifier
re-proved the second one in 9 s.

## 5. Plan and time estimate

`plan_e1.json` / `grid_e1.json` (hashes in `E1_MANIFEST.sha256`): at most 83 vertex-ball jobs (n = 57: 14 + 15;
n = 115: 17 + 19 + 18), of which the branch-and-bound is expected to run about 50, and up to 4 (n = 57) + 4
(n = 115) edge-ball jobs. Measured or stored times per job: n = 57 vertex balls 3.5-4.5 min; n = 115 vertex balls
6-10 min; n = 57 edge balls about 41 min plus about 12 min for the stored verifier; n = 115 edge balls about 75 min
(estimate of the stored run) plus about 25 min. Six jobs at a time, two threads each. The longest chain is a "-"
side at n = 115 (up to 10 points one after the other, about 1.5-2 h). **Expected total: 3 to 5 hours; all five
couplings are expected to be reached within the 8-hour cap.** Stage B at n = 115 runs only for a row that finishes
stage A within 2.5 h of the start (declared rule).

**Expectation stated now:** at n = 57, Jz = 3.3 and 3.2, the DMRG-referenced width at the real energy is already
0.958 tau and 0.977 tau; the stored row with the same margin (n = 57, Jz = 3.4 at the digitized energy, 0.958 tau)
ended at 1.086 tau. The exact intervals there are therefore expected to come out slightly wider than tau: the
certificates then extend the range in which an exact interval exists, without certifying those two rows.
