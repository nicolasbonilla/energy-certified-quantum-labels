# Final tests: what a single-author paper can claim (DECLARATION)

**Written 2026-11-06 (UTC), before any computation on the models below.** Hashed with SHA-256 into `DECLARATION.sha256`
(time in `DECLARATION_hash_time.txt`) before the VM is started. After the hash this file does not change. Later decisions are
deviations, dated, in `DEVIATIONS.md`. Every outcome is reported against the rule stated here, failures included. Honest
failure is an acceptable outcome; a result bent to pass is not. Nothing here is a statement that the labels of
arXiv:2606.15983 are wrong: results concern the emulated method class and our own device data.

**Run before this hash (and nothing else).** Reading of the paper, `bias_law/`, `method/`, `rigor/`, `qpu/`, `R4_fresh.md`,
`R7_continuation.md`. Code writing. `code/make_inputs.py` (copies stored inputs, no physics). Eight numpy-only unit tests on
the laptop at toy sizes (n ≤ 12; plus re-deriving two stored `rigor/` v2 intervals from the stored certificates, which passed).
Generation of the 12 test coupling vectors of Test B (`inputs/B_test_couplings.json`; random numbers only). Listing of stored
values needed for planning: certificates at n = 57, Jz = 4, 6 and their λ; stored run times; per-circuit device counts of job B;
the stored energy of the device label at Jz = 4 (E = −66.17025). **Disclosed:** while planning I evaluated by hand the stored
certificates at that energy (about [0.87, 1.00] for m_s) and at Jz = 6 (m_s threshold near 0.56 J). C1 is a fixed evaluation of
stored numbers, so nothing can be tuned to it, but it is not blind. No state, label, DMRG run or truncated curve at any coupling
of Test A or any instance of Test B was computed or read.

**Blindness of Test A, stated exactly.** No emulated label, truncated curve or n = 19 quantity exists at these couplings.
But DMRG ground states at n = 57 **do** exist from earlier runs: Jz = 2.8 and 3.2 in `design/pilot2/`, Jz = 3.2 in `map/`
(file names checked; contents not read). So "never computed" holds for labels and predictors, not for the truth at two of the
seven points. The truth is recomputed fresh here. Jz = 1.5, 1.7 at n = 57 and all n = 115 points have no stored state.

## 1. Common

- Code: `code/` (manifest in §8). `fr.py`, `emu2.py`, `tn.py`, `hhmodel.py`, graphs: byte-identical copies of `method/code/`.
  `rigor/lb_opt.py`, `lbcore.py`, `verify_exact.py`: byte-identical copies of `rigor/code/`. New: `ft.py`, `ftlib.py`, `ftml.py`,
  `sched_ft.py`, `analyze_a.py`, `analyze_b.py`, `analyze_c.py`, `make_inputs.py`, `tests/test_ft.py`, `vm/`.
- Versions expected on the VM (recorded in `out/versions.txt`): python 3.11.2, numpy 2.2.6, scipy 1.13.1, TeNPy 1.1.0.
- Seeds: `fr.seed` (SHA-256 of "fr|...") for Test A, unchanged; `ftlib.seed` (SHA-256 of "ft|...") for the rest; device
  post-processing keeps the `qpu_post.seed` scheme, so that the stored subspace at Jz = 4 is reproduced.
- Gate G1: `tests/test_ft.py full` passes on the VM (the 8 light tests, DMRG against exact diagonalization on a disordered n = 19
  instance, Krylov evolution against exact evolution). If G1 fails no result counts until fixed; a fix is a dated deviation.

## 2. Order and priorities

Declaration; C1 and C2; Test A; Test B; C3 if the gate passed. On the VM these share one queue with that priority, so that
long tasks overlap. If the budget runs short, Test B is protected: drop in this order n = 115 Jz = 1.7, n = 115 Jz = 2.8, the
secondary n = 19 Krylov family, then Test A's remaining points.

## 3. Test A: blind test of the bias curve

- **Points.** n = 57: Jz = 1.5, 1.7, 2.8, 3.2. n = 115: Jz = 1.5, 1.7, 2.8. No reduction is declared.
- **Labels.** `fr.t_ref`, `fr.t_krylov`, `fr.t_emu` unchanged: DMRG truth (n = 57 χ ramp to 200, n = 115 to 320), Krylov states
  from Néel, k = 1..10, exact evolution, χ ≤ 128, 10⁵ shots per circuit, stored calibration (`inputs/calib_n*.json`:
  p* = 0, p_dev = 0.6717 and 0.2928). Primary label = `primary` = `floor`: 1 % flips, random-flip recovery, Rayleigh-Ritz.
- **Time steps.** Published table where it has the coupling (Jz = 1.5: 0.0579, 0.0335). Otherwise linear interpolation between
  the neighbouring table entries, a choice of this run: n = 57: 1.7: 0.06075; 2.8: 0.05856; 3.2: 0.05892. n = 115: 1.7:
  0.035275; 2.8: 0.03346.
- **Predictors, frozen.** With δe = (E − E₀)/n at the target and Δ = m_s(label) − m_s(GS):
  (a) **the curve**: exact n = 19 top-D truncation at the same Jz (`ft.t_n19` = `bias_law/code/n19b.py`, 26 levels), read by linear
  interpolation in √δe; (b) **curve from n = 57 variants** (n = 115 targets): the four n = 57 variants `ideal`, `primary`,
  `dev_ps`, `dev_rec` at the same Jz, interpolation through the origin in √δe, linear extrapolation beyond the last point, as
  `bias_law.py` section D; (c) **chord**: (1 − m_s^GS(19)) √(δe/δe_Néel(19)), δe_Néel(19) = (−20 Jz/4 − E₀(19))/19; (d) **classical
  two-point forms** for n = 115 from truth at n = 19 and 57: a + b/n, a + b N_e/n, a + b/√n (N_e = 20, 64, 132). Recorded also: the
  label as generated, truth at n = 19, truth at n = 57.
- **Metric.** Corrected label m − prediction; miss = |corrected − m_s(GS)|/τ, τ = 0.06 |m_s(GS)| at the target; mean and maximum per
  size. Ratio = Δ / curve(δe) at the seven primary labels.
- **Rule.** The curve **holds out of sample** iff its mean miss ≤ 0.2 τ at n = 57 **and** ≤ 0.6 τ at n = 115 **and** all seven ratios
  lie in [0.75, 1.3]. Stated separately: whether it beats the chord (n = 57, n = 115), and whether it beats each classical form
  (n = 115), by comparison of mean misses. Where classical forms do not apply (n = 57) this is said.
- **Gates.** G-A2: `n19` at Jz = 1.6 reproduces the stored curve (|ΔE₀| ≤ 1e-8, |Δm_s| ≤ 1e-6, curve ≤ 1e-5). G-A3: replication of the
  stored n = 57, Jz = 2.5 task with the same seeds (|ΔE₀| ≤ 1e-3, |ΔΔm_s(primary)| ≤ 2e-3). A failed gate means no decision for Test A.

## 4. Test B: do quantum labels add information?

- **Model.** Heavy-hex n = 57 (`hh_d5.json`), H = ¼ Σ_e J_e (XX + YY + Jz ZZ), J_e uniform in [0.5, 1.5], sector of the Néel state of
  the two-colouring, Jz = 1.6 and 2.5, **six test instances per Jz**, no reduction. Couplings: `ftlib.test_instance`, seed
  ("B", "test", Jz, i), i = 0..5, listed in `inputs/B_test_couplings.json`.
- **Labels.** Per-site Z_i (57) and per-bond Z_iZ_j on the 64 edges: 121 per instance. Site labels are compared in the form η_i Z_i.
- **Truth.** DMRG per instance: χ ramp 32, 64, 128, 200 with the method run's settings (4-14 sweeps, max_E_err 1e-9, mixer), then
  continued at χ = 320 (4-8 sweeps). Truth = χ = 320 state; E₀ = its energy. Per-sweep energies, χ and truncation errors kept.
- **Generator.** Same first stage: Krylov states from Néel, k = 1..10, TeNPy exact evolution with the disordered H, χ ≤ 128,
  Δt = 0.0622 (1.6) and 0.0570 (2.5), 10⁵ shots per circuit (10⁶ per instance), exact sampling. **Noise variant fixed: `floor`**, as
  Test A's primary: 1 % flips, random-flip recovery. Rayleigh-Ritz in the configurations, labels of the lowest vector.
- **Training data for every learned model.** 600 disordered n = 19 instances per Jz, exact diagonalization, seeds ("B", "train", Jz,
  idx). Even idx: the distance-3 graph. Odd idx: a 19-site breadth-first ball of the distance-5 graph around a random centre
  (this covers bulk environments that the distance-3 graph lacks, for both sides alike). Sector: Néel restriction. **No n = 57
  truth enters any training.** Truncated states at matched energy error: levels with δe in [δ₀/5, 5 δ₀], δ₀ = 0.0248 (1.6), 0.0073
  (2.5), the uniform model's stored values; at most 8 levels per instance, evenly spaced in the list.
  **Primary family: top-D truncation of the exact ground state** (as the curve of Test A). **Secondary family: the same first stage at
  n = 19** (exact Krylov states, S shots per circuit nested, 1 % flips, recovery, Rayleigh-Ritz). The rule uses the primary family only.
- **Local features.** `ftlib.site_features`, `bond_features`: couplings within radius 2 (edges with both ends within graph distance 2 of
  the site; for a bond, the bond, the edges touching it and the edges touching those), with degrees, sublattice sign, sorted
  couplings and shell sums (23 columns each).
- **Classical side (uses no quantum data).** C1 `reg`: regression on the local features, trained on n = 19 truth. C2 `open19`: exact
  ground state of a 19-site cluster around each site or bond, open boundary, Néel sector of the cluster, label read at the centre.
  C3 `emb19`: the same with cut bonds replaced by the mean field (Jz J_e/4) Z_i ⟨Z_j⟩, two self-consistent passes from C2's Z. C4, C5
  `open13`, `emb13`: the same with 13 sites. C6 `stack`: regression of truth on (features, open13, emb13) trained on the n = 19
  instances, where 13-site clusters are proper patches. **Best classical estimate = the one of C1-C6 with the smallest mean miss
  on the test instances of that Jz**: an oracle choice that favours the classical side.
- **Quantum side.** `q_top`: truth − label regressed on (features, label, √δe, δe, label √δe, label δe), trained on the same n = 19
  instances and levels; applied as label + prediction. δe = (E_label − E₀)/57 with the DMRG E₀. Separately `q_top_noref`: same model,
  δe from E₀ estimated without a target-size reference, E₀ ≈ Σ_b e_b with e_b the bond energies of the embedded 19-site clusters
  (the bond-energy regression `E0_reg` is recorded). `q_kry`, `q_kry_noref`: secondary family.
- **Regressors, same for all.** `ftml.Model`: ridge on quadratic monomials, or on linear terms plus 1500 random Fourier features with
  length 2, 4, 8; penalty 1e-7..1e-2 relative; chosen by 4-fold cross-validation over training instances on at most 240 instances
  (mean absolute error); final fit on all rows. Separate models per Jz and per label type. Seeds ("B", "model", Jz, type, name).
- **Primary outcome.** Per instance, mean over its 121 labels of |estimate − truth|/τ_type, τ_Z = 0.06 mean_i|Z_i|, τ_C = 0.06
  mean_b|C_b| (truth of that instance; a fixed scale per type, so a few small labels cannot dominate). M = mean over the six instances.
  Recorded: sites and bonds apart; the per-label tolerance 0.06|o_i|; a bootstrap over instances.
- **Rule.** At each Jz, quantum labels add information iff 1 − M(q_top)/M(best classical) ≥ 0.25 **and** q_top beats that same classical
  estimate in at least five of six instances. **The claim is general only if this holds at both Jz.** Otherwise we report that they do
  not. `q_top_noref` is reported against the same rule. `q_kry` is reported against the same rule as secondary: if it passes where the
  primary fails, the verdict stays "no" and it is called an exploratory lead.
- **Scope, said in advance.** The truth is itself classical (DMRG), so "adds information" means: relative to these local classical
  estimates, at their cost. DMRG on the target at χ = 32 and 64 is computed and reported (cost and miss), but is not in the decisive
  classical set, because at some χ it must equal the truth. If those rows beat q_top, the report says so plainly.
- **Gates.** G-B1 truth: mean over labels of |χ200 − χ320|/τ ≤ 0.1 per instance. An instance that fails is flagged, and the rule is
  evaluated with and without flagged instances; if the two disagree, NO DECISION at that Jz. G-B2 energy: test δe inside the training
  window; else flagged.

## 5. Test C: a processor label with a fully proved interval

- **Interval.** For an in-sector state at energy ≤ E: σ⟨O⟩ ≤ (E − E_LB(σ, λ))/(λ S), S = 57 for m_s, 64 for C̄_zz, E_LB exactly verified
  lower bounds of `rigor/`. Interval = [max(−1, −min_λ u₋), min(1, min_λ u₊)] over the verified certificates, in exact rationals
  (`ftlib.interval`). **τ = 0.06 × the smallest |O| on the interval** (no DMRG). No digitized figure enters.
- **State and energy.** The device subspace (stored raw configurations, the stored seed and pipeline) is rebuilt on the VM; the lowest
  Ritz vector is rounded to integers (2⁴⁴ of its largest entry); its Rayleigh quotient, m_s and C̄_zz are computed in exact rational
  arithmetic (`ftlib.exact_rq`), with an exact check that every configuration is in the sector. Those exact numbers are the state's.
- **C1 (free).** Jz = 4.0, job B, variants `rec` (primary) and `ps`; the 36 stored certificates at n = 57, Jz = 4, 6
  (`inputs/certs_n57_stored.json`), Jz = 4 subset only. Reported even if wider than τ. Check: exact E within 1e-8 J of the stored float.
- **C2 (gate).** New Krylov samples at Jz = 4.0 and 6.0 (`fr.t_krylov`). **Device-calibrated noise:** per circuit k an i.i.d. flip
  probability p_k fixed by matching job B's fraction of in-sector shots of circuit k at Jz = 4.0. Same p_k at Jz = 6.0. Simulation
  of the planned job: S = 40,000 shots per circuit, random-flip recovery, Rayleigh-Ritz, 3 seeds, mean ε_sim = E − E₀ (stored DMRG
  E₀, planning only). Validation recorded: same procedure at Jz = 4.0, S = 23,000, against the device's 0.8256 J. **Rigorous
  threshold ε_thr:** largest energy with width ≤ τ for m_s, over all verified certificates at Jz = 6: the stored ones plus six new
  ones fixed here (m_s, σ = −1, λ = 297/1024, 317/1024, 338/1024 at level eball2; σ = +1, λ = 614/1024, 819/1024, 1 at vball2; same
  optimizer settings; verified by `verify_exact.py`). **Gate: processor time is spent only if ε_sim ≤ 0.8 ε_thr.** A rescaled
  value ε_sim × max(1, device/simulated at Jz = 4) is recorded and is not the gate.
- **C3 (only if the gate passes).** A sealed addendum `ADDENDUM_C3.md` (SHA-256, UTC time, code hashes) is written first. Protocol of job
  B: Néel and asymmetric checks, 10⁴ shots each; Jz = 6.0, Δt = 0.0681 (table), k = 1..10, S = 40,000 shots each; routed layout rule;
  SamplerV2, dynamical decoupling on, gate twirling on, measurement twirling off; the 7 bit-order unit tests rerun first; pre-submission
  equivalence of the k = 1 ISA circuit within 1e-6; `max_execution_time` 150 s, the balance read immediately before submission and at
  least 150 s, plan open, pricing free; no resubmission except after an error before running. Backend: ibm_kingston if operational and the
  layout rule succeeds, otherwise the free backend with the fewest pending jobs among those where it succeeds. **Expected usage ≈ 119 s;
  hard limit 150 s in total.** Every job id is logged. Data count only if both bit-order checks pass (every site ≥ 0.9, majority equal).
  Noiseless control of the identical circuits on the VM (χ ≤ 256), same post-processing. Exact Rayleigh quotient and interval as above.
- **Statement to make.** Say plainly whether one real processor label ends with a proved interval below τ (m_s, variant `rec`, width ≤ τ;
  C̄_zz reported beside it), and that at Jz = 6 a classical method is at least as good.

## 6. Cloud, budget, stop rules

- Only cj-runner-1b (8 vCPU, 0.594 EUR/h list); `--configuration=sqd-research`; never cj-runner-1; never ADC. Lock
  `full_runs/LOCK_cj-runner-1b.txt` by `set -o noclobber`; `cj-poweroff=off` before start; stop `cj-runner@vm` after boot; work under
  `/mnt/cj/sandbox/ft_<stamp>/`; max-run-duration 10 h with STOP; at the end `cj-poweroff=on`, stop, clear the limit, remove the lock,
  confirm all VMs TERMINATED. No deletion of cloud resources; no bucket copies. Outputs fetched often.
- **Budget: at most 12 EUR, about 20 h.** Expected 5-7 VM-h. At 16 VM-h I stop launching and report. Real cost reported as VM-hours from
  gcloud timestamps; the bill itself has a delay.
- IBM: free plan, saved account through `QiskitRuntimeService()`, credentials never read or printed, at most 150 s, only after the gate.
- The laptop runs only editing, gcloud, seconds of analysis of fetched JSON, one process at a time, and the IBM client steps of C3.

## 7. Outputs

`RESULTS.md` (plain Spanish summary first, tables, deviations, real cost, job ids, what was re-executed, only compared, not checked),
`SHA256SUMS.txt`, `DEVIATIONS.md`, `analysis/`.

## 8. Manifest at hash time (SHA-256)

```
480e533757fb11c6ed52d0a670f9d4d3174a3fd15fa775b869f84cc01fa869b2  code/analyze_a.py
ebeb4b64ffc1f49027a67022224137d2315c8f0d97fe3851bbdd5dc95c10ac10  code/analyze_b.py
e050da8541497bbb497acc061893ddeea447a084d0c5e5abb65b6838af5653a8  code/analyze_c.py
79e295a61025d686b30ecec69b7dbf53f9fae5be75e706884b453865893ad586  code/emu2.py
287fc1fbabfcc81afe9d24f498a069dc464edd011dcf39c40e41a8194a1bc857  code/fr.py
59b975590c75f48ba3e1130904881a0d9043bdc6413a92e59cd71c3af155245c  code/ft.py
2ab68d056fd1bd33e36af86f26721ad943a43156b8d3c5c9846c536e74852d18  code/ftlib.py
bbcaaba9939fd86fc5827aa1fbe09613bd7d6772910d9fbaf22ca3eff05d50fc  code/ftml.py
1eb7b6cead37b1e06e95592f8cf7a08b252f188c4ac9e0730a977ee92db4921a  code/hhmodel.py
70e4e883f84bcd533362f4e9f7d57f0be50eaa97b7a6aec307c6f71ab02c72fc  code/make_inputs.py
6859a5facb9d49e3a6d00955eadf6c997fb98b67f98b3890a3f88051d1f16556  code/sched_ft.py
edd848d7ffd2952ec332cd0cd5bd149c8bf0cd00840329979c0eece957a39d9a  code/tn.py
a1ee15158e33baa7f5c17016fb78784d17a4b0bcc84f3fdf61438060e48f8f16  code/tests/test_ft.py
25cdf279c213aa1274a1a3f3efc5056984290cbb71122ea980ab7746c8165353  code/rigor/lb_opt.py
160e434ab1f57bc364794649519098bf6094700388f7e9cf498ccbe243e3c65c  code/rigor/lbcore.py
dfee00b9c7abb6dde007a36d3402e932165f86f83c7eb7c36acea1141043ca9c  code/rigor/verify_exact.py
d8d42f5f54e33699562ba4584ca06925074d206ee8c6baddf73b9ab8c76aace1  code/graphs/hh_d3.json
80790817cc70ed56396799df3ca7205cfe62519477fda50e6e13311b1d528712  code/graphs/hh_d5.json
b5b630097e895a46a6d4072171fec3e5552ec0ea8f6e7b41e9106c9be6e7c8d7  code/graphs/hh_d7.json
f2bcc00266f3a7b3325ce8004806c4562b5a0bc25adefc3fab2770273c33b363  code/vm/ft_vm.sh
8c1f8f102e1e37e126729fcf14c7dc117b2ef3009a4c092ca076532733f89d9a  code/vm/vm_ft.sh
9adc1b67acb113f96fbd3655467cfe955b96e8b59b507e1ae34b99acff587b13  inputs/B_test_couplings.json
51244e5e47ac9b6576419e640f00d1461c2028f59fb11cab97e15fc15e4c258b  inputs/calib_n115.json
5820cc03469966f4324251d16cfbcd61ceca44b061ea9b6ec64a8d5f18d1f1e7  inputs/calib_n57.json
ca37c9f340de0323250e8ab8bb58dc95f076421f5b6b04db2bbbd8fa62c43b70  inputs/certs_n57_stored.json
1e487f94dfeae3b95f1801c4e2f1ed8a873cd43b6c2297201a589dacca26e6b4  inputs/qpu_B_pubs.json
dc4d9e9377fbbcc862f253e82386735cf38b86e5f8fc79f7ee304232999a3625  inputs/qpu_B_raw_configs.npz
0563dd371ad01c0f1ca61a64a0c1085c3d9154920c3cb7a56ee94dfe879527cf  inputs/ref_n57_J4.0.json
a404a20be05105b48e87a7406a01a11f7e770ddb30e805875710e19a7d01a4f0  inputs/ref_n57_J6.0.json
8943c0a899107919a8af92dd2c0c2bb8d0043b532d052ec54fc2b36a06d3d933  inputs/stored_device_B_J4.0.json
798006ce7b1b1ef6cd46273b672fa8b88297f9764adbe0a8b29f571823a4a008  inputs/stored_emu_n57_J2.5.json
a4f4c44f50752e3372a88a04e8e6f6b027006804c285cfa70feaeccefa479c7e  inputs/stored_n19_curves.json
4be0ccb7eb0aa91ab8d0bd32370059211d30a6068956994d5ffbad73cff40fbc  inputs/stored_ref_n57_J2.5.json
890b6d42e1daf067a87a6d0dac283c757f22e12b6a02718335f379c0cac227fe  wheels/physics_tenpy-1.1.0-cp311-cp311-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl
```
