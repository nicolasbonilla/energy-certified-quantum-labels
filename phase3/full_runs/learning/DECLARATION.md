# Learning run (Track 1 of `paper/reviews/REVISION_PLAN.md`): DECLARATION

**Label: declared and hashed before any computation at n ≥ 19.** Written 2026-10-31 (UTC) by the learning-run agent
under the coordinator's brief. The SHA-256 of this file goes into `DECLARATION.sha256` before the VM is started.
Nothing here changes after the hash; anything learned later goes, dated, into `DEVIATIONS.md`.

## 0. Question

Split conformal prediction and its standard variants, calibrated on labels from a quantum generator, guarantee
coverage of the **generator's** labels, not of the physics. (a) How far below the nominal 90 % does the coverage of
the **true** (exact ground-state) labels fall, for averages and for single pairs, under a realistic truncated-subspace
generator and under an energy-valid adversary at the same energy error per site δe? (b) Do physics-certified label
intervals (the information limit of the energy window, computed exactly at n = 20) restore a truth-relative guarantee,
and at what width cost? (c) What abstention rule follows from the certified width, and what does it guarantee?

## 1. What was done before this hash (and nothing else)

Laptop only. No diagonalization at n ≥ 19, no model trained on any n = 20 label, no cloud action.
1. **Data (untrusted, read as data only).** The 100 n = 20 instances (`heisenberg_4x5_id{1..100}`) of the official
   repository of arXiv:2106.12627 (github.com/hsinyuan-huang/provable-ml-quantum, commit
   646a1cb2481e546d1e900ec1add98013fc14d81b, the clone already used by `full_runs/huang/`, in the session scratchpad):
   files `_couplings`, `_XX`, `_YY`, `_ZZ`, `_E` copied to `data_huang20/` (SHA-256 in `provenance/DATA20_SHA256.txt`,
   identical to the clone: `provenance/CLONE_SAME_FILES_SHA256.txt`). **This is every n = 20 instance the benchmark
   has (100).** n = 30 / 45 are not used (no exact diagonalization there; not cheap). The notebook `Code.ipynb` was read
   as text only (to transcribe the model class, §4), never run. The data-convention check of `full_runs/huang/`
   (arithmetic on the stored numbers of all 578 instances) is reused, not repeated.
2. **Instance draws** (`code/make_instances.py`, numbers only): the OOD set and two toy sets (§2).
3. **Code and toys.** Unit tests `code/tests/test_learning.py` (T1-T5, all pass on the laptop; logs in
   `logs_laptop/`) and a full toy dry run on the 3 × 5 lattice (n = 15; 100 + 40 random toy instances, not from the
   dataset): VM tasks, label tables, both learners, all conformal methods, abstention. The toy results are used here
   only to set priors (§8); they are not results of this run.

## 2. Instances

- **D (in distribution): the benchmark's 100 instances at n = 20** (4 × 5, open boundaries, J_b ∈ [0, 2]).
- **O (out of distribution, a held-out region of coupling space, defined here): 40 instances with every coupling
  J_b ~ U[1, 2] i.i.d.** (`code/instances_ood.json`, seed 20261102, drawn by `make_instances.py`). The benchmark draws
  J_b ~ U[0, 2], so the region [1, 2]^31 has probability 2^−31 under it: no D instance lies there. Physically: weak
  relative disorder.
- Toys (dry run only, never a result): `instances_T3.json` (100, U[0, 2], seed 777), `instances_U3.json` (40, U[1, 2],
  seed 778), on the 3 × 5 lattice.

## 3. Labels (all computed on the VM by `code/task_l.py`, exact diagonalization at n = 20)

Conventions of `full_runs/huang/` (verified there): H = Σ_b J_b (X_iX_j + Y_iY_j + Z_iZ_j) (the paper's units; the
repository's `*_E.txt` stores ⟨H⟩/2), site s = 5x + y, bond order of ITensors' `square_lattice(L, 5)`; labels
C_ij = (X_iX_j + Y_iY_j + Z_iZ_j)/3 ∈ [−1, 1/3]. Sector S^z = 0 (dimension 184 756); by the SU(2) argument of
`full_runs/huang/DECLARATION.md` §0 every limit computed in the sector holds over **all** states (no sector assumption).

**Label classes.**
- *Averages* (`avg`): Cnn (mean over the 31 nn bonds), Cd2 (mean over the 24 diagonal pairs), Cstag (mean of η_iη_j C_ij
  over all 190 pairs, η = (−1)^{x+y}).
- *Single pairs, nearest neighbours* (`nn`): the 31 bond correlators. Tier A.
- *Single pairs, diagonal* (`diag`): the 24 second-neighbour correlators. Tier B (droppable, §9).
The other 135 pairs are not used (no witnesses; cost).

**(i) Exact labels.** Ground state of H by Lanczos (scipy `eigsh`, fixed random start, tol 1e-12, two lowest).

**(ii) Realistic generator: truncated-subspace (SQD/SKQD-type) diagonalization at matched δe.** For each instance:
an ideal sampler of the exact ground state in the computational basis (shots i.i.d. from |ψ₀(b)|²; the order of first
appearance is drawn exactly by Poissonization, T_b = E_b/p_b with E_b ~ Exp(1), seed 20261101 + 100000·set + k); the
generator's state is the Rayleigh-Ritz ground state of H in the span of the first D sampled configurations, with D the
**smallest** prefix whose energy error per site (E_RR − E₀)/n is ≤ δe (bisection; RR energy is non-increasing in D by
interlacing). This is the method class of `full_runs/method/` without device noise, Krylov sampling or configuration
recovery (there, perfect ground-state samples reproduced the full pipeline's bias at the same subspace size: D2 =
0.997). It is the generous, noise-free version of the class. **δe ∈ {1e-3, 5e-3}** (paper units; ε = nδe = 0.02, 0.1;
0.04 %, 0.2 % of |e₀|). The two subspaces of an instance are prefixes of one shot stream. Labels: all 190 C_ij of the
RR state and the three averages; energy E_gen recorded.

**(iii) Adversarial energy-valid labels at the same δe (Corollary L).** For each label O (field operator G = S·O,
`lattice.label_pairs`) and each sign σ: ground states of H − σλG at λ aimed by a log-log secant so that ⟨H⟩ = E₀ + ε
for each ε ∈ {0.02, 0.1} (start λ = √(2ε₁/χ_guess); ≤ 3 evaluations per target; stop within 25 % of ε). The
adversarial label is the extreme of the explicit pool {ψ₀} ∪ {witness states of that sign} at energy E₀ + ε (pure points
and two-state mixtures, `hull.py`; by Toeplitz-Hausdorff a pure state attains every mixture value). Two directions:
**advL = toward less antiferromagnetic order** (σ = −σ_order, σ_order = η_iη_j for pairs, −1 for Cnn, +1 for Cd2 and
Cstag), **primary**, because on the toy the generator moved 100 % of the averages and diagonal pairs and ≈ 64 % of the
nn pairs in that direction; **advM = toward more order**, secondary. These are witness labels per label (each label
from its own state), exactly the Corollary L construction.

**Certified interval of a label at energy E** (`labels_l.cert_interval`): hi(E) = min over the + points of
(E − F_lo)/(λS), lo(E) = −min over the − points of (E − F_lo)/(λS), capped at the label's range, F_lo = Ritz value −
residual (Lagrange duality, Lemma A: rigorous for every state with ⟨H⟩ ≤ E; exact up to the λ grid at n = 20). It
contains the true label and the label of every state of the window. Computed at E_gen for (ii) and at E₀ + ε for (iii).
It uses only the generator's energy, not E₀.

## 4. Learners (laptop; both linear in the training labels)

- **M1 (primary) = the benchmark's model class**, faithful numpy reimplementation of the KernelRidge branch of the
  official notebook (cells 3-4): Dirichlet features cos(πk₁x_k), k₁ = −2..2, instance-normalized, linear kernel; and
  the Gaussian kernel on the instance-normalized coupling vector, γ = 1/31; α = 1/(2C), C ∈ {0.0125, 0.025, 0.05,
  0.125, 0.25, 0.5, 1, 2}; no intercept; selection by 5-fold cross-validation (contiguous folds) on the mean fold
  RMSE of the training labels, over both kernels, first minimum kept. Equal to sklearn's KernelRidge and
  cross_val_score to 1e-12 (test T2). **Omitted from the notebook:** the SVR branch (not linear in the labels) and the
  neural tangent kernels (need jax/neural_tangents). One model per label, as in the notebook.
- **M2 (secondary) = a local learner of the Lewis et al. type** (Nat. Commun. 15, 895 (2024)): additive Gaussian
  kernel over the label's terms, each on the raw couplings of the bonds within lattice distance δ of the term
  (`models_l.bank_m2`); δ ∈ {0, 1}, γ = c/|N|, c ∈ {0.25, 1, 4}, α ∈ {1e-3, 1e-2, 1e-1, 1}; same selection. It is the
  kernel limit of their random Fourier features with ridge instead of their ℓ1 penalty. Reason (from the toy): M1's
  test error on nn bonds (0.18 at n = 15) is so large that it could hide any label bias; M2 halves it. M2 answers
  "does a better learner change the conclusion?".
Hyperparameters are selected on the labels the learner is trained on (generator or adversarial), then held fixed.

## 5. Splits, uncertainty methods, coverage

- **R = 200 random splits** of D into 60 training (the notebook's training size) / 20 calibration / 20 test
  instances (seed 20261103 + r). Every split also tests on all of O (training and calibration always from D).
- Nominal level 1 − α = 0.90; conformal quantile = the ⌈21 · 0.9⌉ = 19-th of 20 calibration scores.
- **Standard methods, calibrated on held-out generator (or adversarial) labels:** SC (split conformal, absolute
  residual); NC (normalized split conformal, score |y − f|/s(x), s = bootstrap-ensemble standard deviation (20
  resamples, same hyperparameters) + 0.1 × its calibration median); ENS (the ensemble interval mean ± 1.645 sd,
  uncalibrated: the usual deep-ensemble practice).
- **Certified methods** (the calibration labels enter only through their certified intervals [lo, hi]):
  CSC (score max(|f − lo|, |f − hi|)); CNC (the same divided by s(x)); CB (the exact image [f_lo, f_hi] of the
  training intervals under the linear predictor, plus the conformal margin of the score max(0, hi − f_hi, f_lo − lo));
  BAND ([f_lo, f_hi] alone; no truth guarantee; its width W(x) = Σ_i |a_i(x)|(hi_i − lo_i) bounds deterministically,
  in and out of distribution, the deviation of the prediction from that of the same model trained on the exact labels).
  CSC, CNC, CB cover the truth with probability ≥ 0.9 under exchangeability of (couplings, true label), because the
  certified scores dominate the true-label scores. Exact-label baseline: SC on label set (i) (the oracle width).
- **Reported per label class (avg, nn, diag), per label set (exact, gen1, gen5, advL1, advL5, advM1, advM5), per
  domain (ID test, OOD), per learner:** coverage of the true labels, coverage of the labels of the same generator,
  mean width; model RMSE against the truth. Pooled over the labels of a class, test instances and splits.

## 6. Abstention

- Tolerance **τ = 0.08** (full width; ±3 % of the correlator range, the convention of `full_runs/huang/`), and τ₂ = 0.04
  recorded.
- **Rule BAND (the derived rule): answer iff W(x) ≤ τ.** Guarantee (deterministic, any x): an answered prediction lies
  within τ of what the same learner would answer with exact labels.
- **Rule CB (truth-certified): answer iff the CB interval width ≤ τ; predict its midpoint.** Guarantee (ID,
  exchangeable): P(answered and |prediction − truth| > τ/2) ≤ α, hence a selective error rate ≤ α/answer-rate.
- Compared with the conformal-based rules (answer iff the NC, resp. SC, width ≤ τ) and the ensemble rule.
- **Risk-coverage curves** for rankings by CB, BAND, CNC, CSC, NC, ENS, SC widths, random and oracle: selective RMSE
  against the truth and selective exceedance P(|f − y_true| > τ/2) at coverages 0.05, 0.10, …, 1; AURC. Per class and
  for the pooled query set; ID test instances (held out) and OOD instances (off the training region).

## 7. Decisive quantities and thresholds (ID, label sets at δe = 5e-3, learner M1 unless stated)

Cov_T(·) = pooled coverage of the true labels. Thresholds 0.70 / 0.85 (the brief's example; excess miscoverage 20 vs
5 points, 4× apart).

| id | quantity | strong | null | in between |
|---|---|---|---|---|
| **D1** realistic generator, single pairs | Cov_T(SC, nn, gen5) | < 0.70 | ≥ 0.85 | intermediate |
| **D2** realistic generator, averages | Cov_T(SC, avg, gen5) | < 0.70 | ≥ 0.85 | intermediate |
| **D3** energy-valid adversary, single pairs | Cov_T(SC, nn, advL5) | < 0.70 | ≥ 0.85 | intermediate |
| D3′ (recorded) same with M2 | Cov_T(SC, nn, advL5; M2) | < 0.70 | ≥ 0.85 | intermediate |
| **D4** validity of the certified construction | (a) deterministic: every exact, generator and adversarial training label inside its certified interval (all instances, both δe); 0 band violations; 0 BAND-rule violations; (b) Cov_T(CSC) and Cov_T(CB) ≥ 0.88 for every class, every non-exact label set, both learners, ID | PASS iff all | FAIL otherwise (a FAIL of (a) is a bug) | — |
| **D5** width cost | ρ = mean width(CSC)/mean width(SC), gen5, per class avg and nn | expensive ≥ 4.5 | cheap ≤ 1.5 | moderate |
| **D6** the derived rule | answer rates of BAND at τ = 0.08 on gen5: a_avg, a_nn | confirmed: a_avg ≥ 0.9 and a_nn ≤ 0.1 | refuted: a_avg ≤ 0.5 or a_nn ≥ 0.5 | partial |
| **D7** conformal-based abstention vs truth | e_NC = P(\|f − y_true\| > τ/2 \| NC rule answers), pooled avg + nn, advL5 | unsafe: e_NC ≥ 0.30 | safe: e_NC ≤ 0.10 | intermediate; no decision if NC answers < 1 % |

Also reported without a decision: everything at δe = 1e-3, advM, M2 (except D3′), the diag class, OOD coverages,
risk-coverage curves and AURC, model errors, the oracle width ratio width(CSC, gen5)/width(SC, exact), generator
statistics (D, captured weight, shots) and the label bias of the generator against the certified half-width.

## 8. Priors (set from the n = 15 toy; recorded before the hash)

D1 null 0.85 (toy: 0.92); D2 null 0.6, strong 0.1 (toy 0.91; averages self-average at n = 20, the bias does not);
D3 null 0.5, strong 0.1 (toy 0.85); D3′ strong 0.45 (toy 0.69); D4 PASS 0.95; D5 avg cheap 0.6, nn cheap 0.6
(toy 1.43, 1.27); D6 confirmed 0.7 (toy: 1.00 / 0.00); D7 intermediate 0.5, safe 0.3 (toy 0.13 at a 2.5 % answer rate).

## 9. Gates, compute plan, drop rules

- **G-ED** (each D instance): ED residuals ≤ 1e-8; |Σ_b 3J_b C_b − E₀| ≤ 1e-8; E₀ ≤ 2E_file + 1e-9|E₀| (our ED at or
  below the dataset's DMRG energy); |E₀/(2E_file) − 1| ≤ 1e-5; max_ij |C_ED − XX_file| ≤ 1e-4. **On the brief's
  "within 1e-6":** our ED is exact to 1e-8 (residual, energy identity), but the dataset's labels are DMRG values whose
  own XX vs ZZ inconsistency reaches 1.4e-5 at L = 4 (`full_runs/huang/logs_laptop/check_data.txt`) and which
  `full_runs/huang/` found within 1.1-1.6e-5 of ED; agreement with the files cannot be tested below ≈ 1e-5, so it is
  gated at 1e-4 and the measured maximum is reported. O instances: residual and energy identity. An instance failing
  is excluded and reported; more than 5 failures stop the run (no decision).
- **G-GEN** (each instance, each δe): 0.9 ≤ δe_gen/δe ≤ 1; |⟨H⟩_ψgen − E_gen| ≤ 1e-8; RR residual ≤ 1e-6. A failing
  instance is excluded from that label set.
- **G-CONF**: T1 (split conformal on a synthetic problem: mean coverage 19/21 within Monte Carlo error; certified
  variants ≥ 0.9), T2 (learner equals sklearn), T3 (band exactness). Pass on the laptop before the hash; T1, T3 also
  on the VM.
- **G-WIT**: T4 (generator), T5 (certified interval contains the exact information limit of a 2 × 5 toy, tight to
  5 %; adversarial and random window states inside) on the VM; and D4(a).
- **VM: cj-runner-1b only (n2-highmem-8, zone europe-west3-b, `--configuration=sqd-research`), lock
  `full_runs/LOCK_cj-runner-1b.txt` (noclobber), the up/down procedure of `phase3/pilot_witness/code/vm/`**
  (`code/vm/vm_l.sh`, `code/vm/l_vm.sh`): cj-poweroff=off before start, max-run-duration 7 h with STOP, the sealed
  runner stopped after boot, work only under `/mnt/cj/sandbox/learning_<stamp>/` (tools in
  `/mnt/cj/sandbox/learning_tools/`), the venv read-only, never the mirror, prereg/runs, the queue or the ledgers; at
  the end cj-poweroff=on, stop, clear max-run-duration, show TERMINATED, remove the lock. **Cap 8 VM-h.** If
  cj-runner-1b is not TERMINATED or its lock exists, cj-runner-2 (n2-highmem-4, lane vm2) under the same rules.
- **Tasks:** 280 = {A, B} × (100 D + 40 O); A (ED, generator, witnesses of the 3 averages and 31 nn bonds) at
  priority 1, B (ED, witnesses of the 24 diagonal pairs) at priority 2; 8 slots, one BLAS thread each.
- **Checkpoint and drop rule:** when 16 A tasks have finished, and again at 3 VM-h, project the end from the mean task
  times. If the projected total exceeds 6.5 VM-h: drop B tasks of O; if still > 6.5: drop all B tasks (the diag class
  is then not reported); if still > 7.0: drop A tasks of O 21-40 (OOD set of 20). D and O tier A for k ≤ 20 are never
  dropped.

## 10. Outputs

- VM: `out/inst/{A,B}_{D,O}_<k>.json` (energies, all 190 exact and generator pair correlators, generator statistics,
  every witness point (λ, F, residual, ⟨H⟩, ⟨O⟩)), logs, unit tests; `OUT_SHA256SUMS.txt`.
- Laptop: `analysis/` (gates, label tables, `learn_M1_D_O.json`, `learn_M2_D_O.json`, tables, figure),
  `RESULTS.md` (eight-line summary in simple Spanish, then English), `DEVIATIONS.md`, `FINAL_SHA256.txt`.
- Re-executed vs only compared vs not checked is reported item by item.

## 11. Code at the hash

The SHA-256 of every file of `code/` at the hash is in `CODE_SHA256_at_hash.txt`, written in the same step as
`DECLARATION.sha256`.
