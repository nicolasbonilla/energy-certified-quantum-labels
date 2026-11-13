# Huang benchmark (second public dataset): DECLARATION

**Label: declared and hashed before any computation at n ≥ 19.** Written 2026-10-31 (UTC) by the Huang-run agent under
the coordinator's brief (plan `phase3/PLAN_UNICO_2026-10-30.md` §6, row "Segundo conjunto de datos público"; design
`phase3/design/R3_generality.md` Part B #3). The SHA-256 of this file goes into `DECLARATION.sha256` before the VM is
started. Nothing here changes after the hash; anything learned later goes, dated, into `DEVIATIONS.md`.

**Question.** If the public benchmark of Huang, Kueng, Torlai, Albert, Preskill (arXiv:2106.12627, Science 377,
eabk3333 (2022)) had been produced on a quantum device with intensive energy error δe ∈ [1e-3, 1e-2], which of its
labels would the energy certify, at what δe\*, and does the rule δe\* = τ²/(8χ) (averages) / τ²/(8nχ_i) (local labels)
hold there?

**Run before this hash (and nothing else):** laptop only.
1. Downloads (untrusted data, own folders in the session scratchpad, read as data only; nothing from them executed):
   the arXiv abstract page and PDF of 2106.12627 (PDF SHA-256 29485e88…; abstract page copied to
   `provenance/arxiv_2106.12627_abs.html`); the official repository named in the arXiv comments field ("open-source code
   available at" github.com/hsinyuan-huang/provable-ml-quantum), cloned at commit
   646a1cb2481e546d1e900ec1add98013fc14d81b (2022-11-22, MIT licence). The notebook `Code.ipynb` was read as text only
   (to learn the file conventions), never run. The data files of the six instances below were copied to `data_huang/`
   (SHA-256 in `provenance/DATA_SHA256.txt`, identical to the clone: `provenance/SOURCE_CLONE_SHA256.txt`).
2. Convention check (`code/check_data.py`, arithmetic on stored numbers only; output `logs_laptop/check_data.txt`):
   for all 578 instances of the repository the stored energy equals Σ_b J_b (XX + YY + ZZ)_b / 2 with the ITensors
   `square_lattice(L, 5)` bond order to ≤ 1.5e-14 (relative), while the other orders tried miss by O(1-10); couplings
   lie in [0, 2]; XX = YY to 1e-11 and XX = ZZ to ≤ 7.6e-4 (≤ 8.1e-5 for the six chosen instances).
3. Code writing; unit tests on toy strips (n ≤ 15, random couplings not from the dataset; `code/tests/test_huang.py`)
   (T1 sector = global, T2 ladder = exact limit over all states to ≤ 1 % in ε_τ, T3 evaluators, T4 end to end; logs in
   `logs_laptop/test_*.txt`; T2 ran on the current `chain.py`, `ed_h.py`, `hull.py`) and a toy dry run of the whole
   pipeline including `g4.py` and `analyze_h.py` (`code/tests/dryrun_h.py`); two tests at n = 18 (3 × 6, random couplings, not
   from the dataset): the sector solver takes 0.3 s per ground state; DMRG on that width-6 strip has energy errors
   9.8e-4 (χ = 128) and 2.5e-6 (χ = 256) against exact diagonalization. The second number fixed the chain bond dimension
   below (χ_c = 256; a first draft had 128).
No diagonalization or DMRG at n ≥ 19, no cloud action.

## 0. Conventions (verified against the paper's text and the data files)

- **Model (paper p. 8 and App. D.3, Fig. 3a):** square lattice L × 5, open boundaries, H = Σ_⟨ij⟩ J_ij (X_iX_j +
  Y_iY_j + Z_iZ_j), J_ij uniform in [0, 2]. Sites s = 5x + y (x = 0..L−1 along the length, y = 0..4), bond k of
  `*_couplings.txt` = k-th bond of ITensors' `square_lattice(L, 5)` (per site: (s, s+5) if x < L−1, then (s, s+1) if
  y < 4). The repository's `*_E.txt` stores ⟨H⟩/2. **Energies here are in the paper's units** (H as written). In the
  file's units δe would be halved; in S·S units (H = Σ 4J S·S) divided by 4. The relative error δe/|e₀|
  (e₀ = E₀/n ≈ −2.6) is reported next to every δe\*.
- **Labels (the paper's two-point correlator):** C_ij = (X_iX_j + Y_iY_j + Z_iZ_j)/3 ∈ [−1, 1/3] (range 4/3). The
  paper's ML model predicts C_ij for every pair; `*_XX.txt` holds them for the DMRG ground state (SU(2): XX = YY = ZZ).
  - **Benchmark labels:** all 190 pairs i < j at n = 20 (exact diagonalization).
  - **Averages:** Cnn = mean of C over the nn bonds (31 / 49 / 76 at n = 20 / 30 / 45); Cd2 = mean over the diagonal
    second-neighbour pairs (24 / 40 / 64); Cstag = mean of η_iη_j C_ij over all pairs, η = (−1)^{x+y} (n = 20 only,
    record).
  - **Featured local labels:** Ccent = the horizontal bond ((L−1)//2, 2)-((L−1)//2 + 1, 2) of the middle row; Cfar =
    the end-to-end pair (0, 2)-(L−1, 2) of that row; Cfix = the bond (1, 2)-(2, 2) = sites (7, 12) at every size
    (= Ccent at L = 4).
- **Instances (dataset indices, the lowest available, fixed before any computation):** (L, k) = (4, 1), (4, 2), (4, 3)
  [n = 20, ED]; (6, 1) [n = 30, DMRG]; (9, 1), (9, 2) [n = 45, DMRG]. Known before the hash: instances with the same
  index k share their first couplings (the k = 1 lists of L = 4, 6, 9 are prefixes of one another), so bond (7, 12) and
  its couplings up to column 2 are identical in (4, 1), (6, 1), (9, 1): Cfix is the same physical bond in a growing
  lattice. The other instances are independent draws.
- **No sector assumption.** H and every label are SU(2) invariant. The lowest multiplet of H − λS·O always contains a
  member with S^z = 0 (n even) or S^z = +1/2 (n odd), so the ground energy in that S^z sector equals the global one for
  every λ. By Lemma 0 (R3 §A.1) the information limit over all states equals the one computed in the sector (checked
  on toys: test T1). The limits below therefore hold for **any** device state, pure or mixed (Lemma P), with no
  assumption on its symmetry sector.
- **Field:** H − σλ S·O with S·O = Σ_p w_p C_p (S = number of pairs of an average, 1 for a pair label). For a bond
  label this is the coupling shift J_ij → J_ij − σλ/3.
- **Tolerance.** **Primary τ = 0.08 = 0.06 × (4/3):** a label is certified when the energy confines it to an interval
  of full width ≤ 0.08, i.e. ±0.04 = ±3 % of the range [−1, 1/3] of a correlator (the map's "±3 %" convention, taken
  relative to the range because many C_ij are close to 0). Recorded as well: τ₂ = 0.04 (full width 3 % of the range)
  and **τ_paper = 2 × RMSE** of the benchmark's own training labels (the notebook's shadow estimator from
  `*_samples.txt` against `*_XX.txt`, mean over the six instances; also with the first 500 snapshots, the paper's
  T = 500), i.e. the ±1σ band of the labels the ML model is trained on.
- **δe grid:** {1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3, 1e-2} (paper units); ε = n·δe.

## 1. What is computed

For every (instance, label), from one witness chain of each sign (ground states of H − σλS·O):

- **Inner side (rigorous, explicit states):** hull of the chain states and the ground state (pure points and
  two-state mixtures; `hull.py` of the map, unchanged). By Toeplitz-Hausdorff every mixture point is attained by a pure
  state.
- **Outer side:** σ⟨O⟩ ≤ (E − F_lo)/(λS) for every chain point, capped at the label bounds. **n = 20 (ED):** F_lo =
  Ritz value − residual (exact up to the Lanczos residual). **n = 30, 45 (DMRG-referenced):** F_lo = F − δG with
  δG = max(2·δχ_c, |G(χ_c) − G(384)| measured by gate P2 at that instance), δχ_c = |E₀(χ_c = 256) − E₀(384)|.
- **E₀:** ED ground energy (n = 20); χ = 384 DMRG energy (n = 30, 45; staged 32 → 64 → 128 → 256 from the Néel state,
  then 384). The DMRG inner side is evaluated at E₀ + ε − 2·δχ_ref (δχ_ref = |E₀(256) − E₀(384)| = δχ_c), to allow for
  the reference error.
- **Widths** w_in, w_out at every grid δe; **ε_τ^in** = smallest ε with w_in ≥ τ (rigorous for "not certified"),
  **ε_τ^out** = smallest ε with w_out ≥ τ (certificate side); **δe\* = ε_τ/n.** If w_out stays below τ up to the largest
  chain energy, that energy is reported as a lower bound of ε_τ^out.
- **The rule (R2 Prop. L, R3 Cor. A):** χ_two = (o₊(λ₀) − o₋(λ₀))/(2λ₀) from the two small-field points (λ₀ = 0.005 for
  averages, 0.1 for pair labels); **δe\*_law = S·τ²/(8·χ_two·n)**, which is τ²/(8χ) with the per-site susceptibility
  χ = χ_two·n/S for averages and τ²/(8nχ_i) with χ_i = χ_two for pair labels. law/computed = δe\*_law/δe\*^out.
- **Regime (n = 20):** ε/Δ with Δ the first excitation gap in the sector (the spin gap).

## 2. Runs

- **ED, n = 20** (`ed_h.py`, S^z = 0 sector, dim 184,756; every Lanczos call from one fixed random vector, seed
  20261031; tol 1e-12; residual stored): `edref` (ground state, first excitation, all C_ij, gate G2) for the three
  instances; `edlab` for Cnn, Cd2, Ccent, Cfar (and Cstag, record) with the full ladder (λ₀; the seven grid energies;
  the law's ε_τ; ε_τ straddled on each side in up to two rounds; ≤ 16 points per side); `edpairs`: the 190 pair labels
  in 12 batches with the short ladder (λ₀; δe ∈ {1e-3, 3e-3, 1e-2}; the law's ε_τ; ε_τ straddled; ≤ 9 points per side).
- **DMRG** (TeNPy 1.1.0, the pilots' wheel 890b6d42…; `hmodel.py`; S^z conserved): references (4, 1) [gate G1],
  (6, 1), (9, 1), (9, 2): χ = 32 → 64 → 128 → 256 → 384, cold from the Néel state (TeNPy convergence |ΔE| < 1e-9,
  |ΔS| < 1e-4). Chains at **χ_c = 256** (warm start from the nearest λ of the same chain, mixer 1e-6, 3-8 sweeps,
  |ΔE| < 1e-7, |ΔS| < 1e-3, svd_min 1e-12), ladder: λ₀; δe ∈ {1e-3, 1e-2}; the law's ε_τ; ε_τ straddled on each side
  (≤ 8 points per side); labels Cnn, Cd2, Ccent, Cfar, Cfix at n = 30, 45 and Cnn, Ccent, Cfar at (4, 1) (gate G1).
  Every state is stored (`.npz`,
  SHA-256) and evaluated in-process by TeNPy (MPO energy, correlators) and by the independent numpy evaluator
  `indep_eval_h.py` (energy from the bond correlators, labels, norm, S^z moments); labels are taken from the
  independent evaluator.
- **Gates tasks:** P2 (χ = 384 re-run of G at the decisive λ = the chain point whose dual line gives the outer bound at
  ε_τ^out) and P3 (cold start from Néel at χ_c at the same λ) for Cnn and Ccent, both signs, at (9, 1); G4 after the run
  (`g4.py`, separate process, TeNPy not importable).
- **Priorities** (a higher number is dropped first, §4): 1 ED references and featured labels; DMRG references; Cnn,
  Ccent rows at n = 30, 45; G1 rows. 2 DMRG Cfar and Cfix rows, Cd2 rows of (6, 1) and (9, 1); ED nn-bond pair labels
  (three instances); P2/P3. 3 ED Cstag; ED other pairs of (4, 1); DMRG Cd2 of (9, 2). 4 ED other pairs of (4, 2),
  (4, 3). 84 tasks (`witness.py plan`).

## 3. Decisive quantities and decision rules

**Row status** at each grid δe (τ = 0.08; the same recorded at τ₂ and τ_paper): **CERTIFIED** if w_out(nδe) ≤ τ
(exact at n = 20; DMRG-referenced at n = 30, 45); **NOT CERTIFIED** if w_in(nδe) ≥ τ (rigorous: explicit states);
**GRAY** otherwise.

**Claims (decided here; priors are judgment):**
- **C-H1 (benchmark labels).** No n = 20 pair correlator is CERTIFIED at δe = 1e-3 (any of the computed pairs, three
  instances). Prior 0.75. Recorded: counts C/N/G at every δe and τ, and the δe\* distribution by pair class (nn,
  diagonal, r ≤ 3, r > 3).
- **C-H2 (local labels at the larger sizes).** Ccent, Cfar and Cfix are NOT CERTIFIED (rigorous side) at δe = 1e-3 at
  every n = 30, 45 instance. Prior 0.85.
- **C-H3 (averages).** Cnn is CERTIFIED at δe = 1e-3 at all six instances. Prior 0.8. Recorded: Cnn at 1e-2 (prior
  0.4); Cd2 at 1e-3 (prior 0.6).
- **C-H4 (the rule).** law/computed ∈ [0.8, 1.25] for every Cnn and Cd2 row (prior 0.75) and for every Ccent, Cfar,
  Cfix row (prior 0.65); for the n = 20 pair labels, the fraction in the band is ≥ 0.9 (prior 0.6).
- **C-H5 (size dependence).** (a) Cfix in the k = 1 family ((4, 1), (6, 1), (9, 1)) and the k = 2 family ((4, 2),
  (9, 2); same prefix property): ε_τ(n)/ε_τ(20, same k) ∈ [0.67, 1.5] at every n = 30, 45 instance (an O(1) extensive
  cost, δe\* ∝ 1/n; Theorem 1). Prior 0.6. (b) Cnn: δe\*(n)/mean δe\*(n = 20) ∈ [0.67, 1.5] at every n = 30,
  45 instance (intensive; Theorem 2). Prior 0.7.
- **Instance spread:** min / mean / max of δe\* per featured label over the three n = 20 instances and the two n = 45
  instances; for pair labels, the per-instance distributions.

**Gates** (a failure means "no decision" for the claims that depend on it; the reason is reported):
- **G2 (convention, all instances):** max_ij |C_ij(ours) − C_ij(file)| ≤ 0.01 and |E₀/(2E_file) − 1| ≤ 1e-3 (ED, and
  DMRG at χ = 384). A failure stops the analysis of that instance (convention error).
- **G1 (DMRG pipeline vs ED, (4, 1), Cnn, Ccent, Cfar; χ_c = 256 as in production):** |w_out − w_ED| ≤ 0.01·w_ED at the
  aimed grid points (1e-3, 1e-2) and ε_τ^in, ε_τ^out within 5 % of the ED ε_τ. Failure: DMRG rows "no decision".
- **P1 (reference):** δχ_ref ≤ 0.02 × the smallest featured local ε_τ^out of the instance (else those rows are flagged).
- **P2:** |G(χ_c) − G(384)| ≤ 0.01·ε_τ^out at the checked decisive λ. **P3:** F_cold ≥ F_warm − 1e-5·|F|.
- **P4:** every stored DMRG state in the sector (TeNPy charge, S^z variance < 1e-10); TeNPy vs independent evaluator
  |ΔE|, |ΔC|, |Δnorm|/norm < 1e-8. **ED:** every residual ≤ 1e-8 (recorded).
- **G4 (separate process):** every headline component (hull components of the inner extremes at δe = 1e-3, 1e-2 and at
  ε_τ^in of every DMRG chain; the χ = 384 references) re-evaluated from its `.npz`: |ΔE|, |ΔO| ≤ 1e-8, S^z variance
  < 1e-10, every headline mixture at or below its energy.

## 4. Cost cap and cloud rules

- **Hard cap: 6 VM-hours on cj-runner-2** (n2-highmem-4, ≈ 0.30 EUR/h list: ≤ 1.8 EUR). Expected ≈ 3.5-4 VM-h
  (≈ 9 job-hours on 4 vCPU). **Checkpoint** ≈ 1 VM-h after the scheduler starts (`project_h.py`, measured task times):
  if the projection exceeds 5.3 VM-h, drop (via `skip.txt`) in this order until it fits: (1) priority 4; (2) priority 3;
  (3) the P3 cold tasks; (4) the Cd2 and Cfix rows of (6, 1). The projection is repeated at ≈ 2.5 VM-h with the same
  rule. **Never dropped: priority 1.** The
  scheduler is stopped (STOP) at 5.4 VM-h since boot and what exists is analysed; the VM is down before 6 VM-h.
- `gcloud` only with `--configuration=sqd-research`; only **cj-runner-2** (lane vm2), zone europe-west3-b; never
  cj-runner-1 or cj-runner-1b (another agent's), never another configuration, never ADC. If cj-runner-2 is RUNNING at
  the start (not started by this run), stop and report. Sequence (the pilots' `code/vm/` procedure, copied as
  `code/vm/vm_h.sh` and `h_vm.sh`): `cj-poweroff=off` before start; max-run-duration 6 h with STOP as safety net; after
  boot `systemctl stop cj-runner@vm2`, confirm no `heavy_run.py`; record line counts and SHA-256 of the sealed ledgers
  at boot and at the end; work only under `/mnt/cj/sandbox/huang_<stamp>/` (tools in `/mnt/cj/sandbox/huang_tools/`);
  never touch `/mnt/cj/mirror`, `prereg/runs`, the queue, the ledgers or `/mnt/cj/venv` (used read-only). At the end:
  `cj-poweroff=on`, stop the VM, clear max-run-duration, `instances list` showing TERMINATED. No credential, token or
  personal data printed or stored. Concurrency 4 tasks, BLAS 1 thread. Unit tests T1, T3, T4 must pass on the VM
  before production (T2, slow, on the laptop). Outputs copied to `gs://cj-sqd-research-0f818af9/exploratory/huang_<stamp>/`.

## 5. Reporting

- Verbs "computed", "evaluated". Next to every number: exact (ED, n = 20), rigorous (inner side, explicit states),
  DMRG-referenced (outer side, n = 30, 45).
- Every reported number comes from a file with SHA-256 in the fetched outputs or from a laptop re-execution listed in
  RESULTS.md; re-executed / only compared / not checked listed separately.
- RESULTS.md: 8-line summary in simple Spanish, then English: the per-label certification table vs δe, the rule check,
  the instance spread, a draft figure with its script, cost, deviations, the VM final state.

## 6. Only compared (no new decision)

The map's numbers (IBM heavy-hex: law within 0-5 % for averages without level crossings) and R3's T2-T3 toy checks.

## 7. Code and data manifest at hash time (SHA-256)

```
646e36a19952b0a2d5e632b1fd87bcf1bdc4cd2664ba91b0b3250f441299ccfe  code/analyze_h.py
11f866d61a8fef8180d83f50415e2b322e0d45e69ea99bd59b3d414dc2224215  code/chain.py
7de7ccf4e923a8f33c61d0352ae8cc0af1c3e95b515074f338591a89ac6acaf7  code/check_data.py
3ce1a2af2caae1006689ab46527717b6e70533b17f2893003dd8f291a93dde0c  code/ed_h.py
e0c7223f1c0d032c9e37ee3a76bede09925d81e209048be02f9390b434f92595  code/g4.py
24d159e30e80b0e9351a27027c8d6119e98048406125aabad4287b124a85a105  code/hmodel.py
8598cdc365b58422c35fc7d5dbdc6fb68f1ea9b994c233a0fa7d7c934fcbc88a  code/hull.py
996bd86e82b53e4ef9e8f8882006f2843b0285756fd643a2d688e29f7043b42a  code/indep_eval_h.py
b1c786bbd5d52fc885af2886cd9a1fc8797d3977f7247474b558e67f38553290  code/lattice.py
304ade2a4c82d3315aa2e44e61cd0274a8fe2b117c5df4c33d6a2c3b4a5ec4f1  code/plot_h.py
c1014d9318d76953a43e3c84f67d0987bb5287076ef2756db41b8bc0352fb88b  code/project_h.py
eee644326144ed3a4e22225a0dc6e1e31a4d620fe6353ca8c7502020286f3437  code/sched.py
cca9e075639387aedaf14f2f86120f40d5043c370c40275a7f9a1305329e8938  code/witness.py
ec76e1770110e5d84c93ec825066fafe90c24e0cfeefbc5d397684ef7c01dc0d  code/tests/dryrun_h.py
5bb0acc0fed2b2bbaaecfd687a92de516989246f20b8de1a80abf55887d4852f  code/tests/test_huang.py
4c7699123b2ff11b3a790e7e5c6f7e4ec6147e3c5370bdc850826598bb1c5201  code/vm/h_vm.sh
f6d516747469861c668d63376ee16daa70920aedd185994ad796f4353335b015  code/vm/vm_h.sh
c2376d6bf5bf93efbb82fb932fe6f97dd32114f6f088715ec6e7ce33dbc25df8  data_huang/LICENSE_upstream.md
184af40d7e49c836768db828c72b5e227c624409d5e309898ea9ec27395dd673  data_huang/heisenberg_4x5_id1_E.txt
cb0514ab901dab5b10ef130956bfc9972d87e551ca3979a01051f4c32dbe46c9  data_huang/heisenberg_4x5_id1_SvN.txt
29192ab10ff347eb0488ae1be2a87ff0ca5c36cf52b8317349a437ff78a9abaa  data_huang/heisenberg_4x5_id1_XX.txt
52dcfa73cf03bc137de4c5672d22fa93d32f78a24b9dea383438679b4d529436  data_huang/heisenberg_4x5_id1_YY.txt
e139e11071d330d7fc3983bef4aae0d5c617b7e3e09fd951aed6da4422e26f72  data_huang/heisenberg_4x5_id1_ZZ.txt
298cc46b1c179354c9a402d064f2d53784cf447ae8d7ae5b7fb3a93be230de45  data_huang/heisenberg_4x5_id1_couplings.txt
7939674b98c33ea3e7669d02d71b06fb8daf1b94ba2787a201278f1006966fd8  data_huang/heisenberg_4x5_id1_samples.txt
472d106bf6a07d648a859a1c94a12000f347e3c9fb21deaa3b567c3c97c04a43  data_huang/heisenberg_4x5_id2_E.txt
1d3ac79ff095322534ce54f235c22b0fa7abf97fedc9fa0b418d267cdbb06060  data_huang/heisenberg_4x5_id2_SvN.txt
60053e7722d44404bbfe4e9d45b17796160dd6e3dfa13e29ec0c73a7e507f995  data_huang/heisenberg_4x5_id2_XX.txt
ee162aa200115556490276b4868bd1efd43d6fa4a5f21369f2b38cb0815c8e8a  data_huang/heisenberg_4x5_id2_YY.txt
d966abb02a06d09384384eda8c8b160560116f5fd56b42869221dfabc6b49c4c  data_huang/heisenberg_4x5_id2_ZZ.txt
a1f13ee5a3534b8b746a4789aa78f56f26016befce997f7e82d22b38a4af8136  data_huang/heisenberg_4x5_id2_couplings.txt
676b2b817242cb2d236e603e1a2fa35ad52c155d6fbd33cb3ac2a1ebf1585d98  data_huang/heisenberg_4x5_id2_samples.txt
2299a1541a59784f93e24fe036afa50e1335648b67612d9545e5185da6d38cd8  data_huang/heisenberg_4x5_id3_E.txt
f31c9d32696af934b71fbc8361b14d042effccafc81822da329937188630c8b2  data_huang/heisenberg_4x5_id3_SvN.txt
46bbd858d5000a1663987e29ab6a3cef7f5e01dddae4419c1f7e506f79f40ad4  data_huang/heisenberg_4x5_id3_XX.txt
743f0db30338709d784ea754f2eb981f817ab0105783f2e87c4df3dc51588294  data_huang/heisenberg_4x5_id3_YY.txt
134cce65628dfc28c89faadc50fa1bd3686082b3c68f6aa5bb668a176ed264ac  data_huang/heisenberg_4x5_id3_ZZ.txt
bffdf4fc7adbd08ab97a2f758f3d77c482cb78e61f6363c6472bdd939b1b5f63  data_huang/heisenberg_4x5_id3_couplings.txt
5bdd8f65689148d605d3cda4ac1a33756e871a1a851ec63730ea821e890109a1  data_huang/heisenberg_4x5_id3_samples.txt
277af5676530df35882716418eb2dde71d5de88428f8f5d637534602291c52b7  data_huang/heisenberg_6x5_id1_E.txt
3b64660d8b104a9b5f428a122a7297c62fb585342a9be3eebddcd213663b7522  data_huang/heisenberg_6x5_id1_SvN.txt
019bc41cbf734365df41a237c6d78c812a71609b7e42c8fcc691e0b0d10dd7fa  data_huang/heisenberg_6x5_id1_XX.txt
512c3cc098db43eebde6e605c101eba5c6475eabcd0ed1b0a560895b5e424740  data_huang/heisenberg_6x5_id1_YY.txt
4ea7969e5fa3b19b6e2b62a570cb39533a7ca0bd5728d8e6bc19bdb10a947072  data_huang/heisenberg_6x5_id1_ZZ.txt
2031be5d9eccd27258a50022b1f9a2c1752f6c80e0fb66e074baeaeb47819d66  data_huang/heisenberg_6x5_id1_couplings.txt
a194d9190b08dcae7e91a81e1e55db56d1ae099dd2380f49f76fad799eb28ad8  data_huang/heisenberg_6x5_id1_samples.txt
b07132bdffc8c294c67b061eb2bea123f857ee7843e5d01b36d3108a43dac13b  data_huang/heisenberg_9x5_id1_E.txt
d2373999ffac2620bdae626c257498004867e5fe474a30d0b0c9b7c52999db97  data_huang/heisenberg_9x5_id1_SvN.txt
32fcb9910175bbac0eb8be5b89ce1b47a967826923a154105cabc7611f6cb065  data_huang/heisenberg_9x5_id1_XX.txt
c270e12420dac3f64d72d8a9447f686317a2e58fb149bf3b9632f69cb50ab626  data_huang/heisenberg_9x5_id1_YY.txt
3b662f2e629718ec7cb5af515cbb139187b2a953aae205f581008348a6291c5c  data_huang/heisenberg_9x5_id1_ZZ.txt
413246655bcdd30d84824a11ae8b07e941f4b38a38a94405bdfe779d779217f2  data_huang/heisenberg_9x5_id1_couplings.txt
d9aa2be53185d08c5e782b46ae8ac0efb5f9353eff9f305643d31aeb1d075552  data_huang/heisenberg_9x5_id1_samples.txt
c6276cd5ef6e02d58799b9408ea2a98f93f5368686800807491b4ad3b3b5dd30  data_huang/heisenberg_9x5_id2_E.txt
060da23c2a4f1fb792dc51e7634e6625d33b7970676d4b5f9c0f5dd37c9895ed  data_huang/heisenberg_9x5_id2_SvN.txt
85de07d17b48024bf9fd96189f2c51ebdd3300ca07a86f7a979f58be47de2b16  data_huang/heisenberg_9x5_id2_XX.txt
f7034033c412b8330a172bcea5d6a49f4203299379d90be32bc3e7b071b18b3e  data_huang/heisenberg_9x5_id2_YY.txt
a606cdf81c9489f6be61657645adf637815b78a19749c5db1efa7c69ec3b1a80  data_huang/heisenberg_9x5_id2_ZZ.txt
79e97dbdb5df252e998da9867063fb63651cb49c86e423d4aa510001b8a3f001  data_huang/heisenberg_9x5_id2_couplings.txt
f65bada7aeaf6e60620b78ef8ab652197db7b7ba11507b65dbcf05d36ee37a1c  data_huang/heisenberg_9x5_id2_samples.txt
636a689865dc42f9c37fea8d4d48a530f31bc23b778d17ab9561c2e253fc3f7f  provenance/DATA_SHA256.txt
c376160223f76a4500c8e8b53227d258ecbaec447a6204b1945b03a3eb5a03fc  provenance/SOURCE_CLONE_SHA256.txt
9961d043e2718c375437b0f0c4cae7e7d1aad249d44837e7916d85f7d6f99a06  provenance/arxiv_2106.12627_abs.html
890b6d42e1daf067a87a6d0dac283c757f22e12b6a02718335f379c0cac227fe  wheels/physics_tenpy-1.1.0-cp311-cp311-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl
28e6507d9427226b06979a155494f1b5babdbedb15d2100d95a99116144954c3  logs_laptop/check_data.txt
f67f4f54bb7f701b6f6b68b343e6da7bd62ea46153b19298b395e7ff8a1893dc  logs_laptop/test_T2_run1.txt
c6e5787a089866d19aff6f4a8db726dc5b3f97268a1885b6ea786a02cbbd73ca  logs_laptop/test_T134_final.txt
```

`hull.py` and `sched.py` are unchanged copies of full_runs/map/code (SHA-256 8598cdc3…, eee64432…); the wheel is the
pilots' TeNPy 1.1.0 wheel. Downloads: arXiv PDF 29485e88e4b744e13ce160f7e1bb54650d92d6bab22590176d04ebd9c913183f;
repository commit 646a1cb2481e546d1e900ec1add98013fc14d81b.
