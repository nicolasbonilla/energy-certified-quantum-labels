# Certification map (phase 3, full run): DECLARATION

**Label: PAPER-GRADE RUN, declared and hashed before any computation at n ≥ 19.** Written 2026-10-30 (UTC) by the map
agent under the coordinator's brief (plan `phase3/PLAN_UNICO_2026-10-30.md` §6, weeks 1-2; cap 15 VM-hours on
cj-runner-1b, free trial credit). The SHA-256 of this file goes into `DECLARATION.sha256` before the VM is started.
Nothing here changes after the hash; anything learned later goes, dated, into `DEVIATIONS.md`.

**Run before this hash (and nothing else):** laptop only. (i) The two readings of IBM 2606.15983's energy figures
(`digitization/`, `code/digitize1_pilot_copy.py`, `code/digitize2.py`, `code/compare_readings.py`,
`code/make_readings.py`; the PNG files are read as data); (ii) code writing; (iii) unit tests on toy graphs (n ≤ 12,
exact dense diagonalization) and end-to-end dry runs of the plan on toy graphs (n ≤ 12; one full-plan run stopped
after 229 tasks, then three reduced-plan runs while fixing the defects they found: the TeNPy truncation check at small
χ, a too-small λ step, and the placement of the ε_τ points; the last run, with the code hashed here, passes G1 against
exact diagonalization and every gate that applies to toys). No DMRG at n ≥ 19, no cloud action.

**Basis.** `design/pilot2/DECLARATION.md` (7f0d651e…) and `design/R2_constructive_half.md` §2-4 (the method extended
here); `pilot_witness/DECLARATION.md` (529e8dcd…), `RESULTS.md`, `TABLES.md` (witness machinery, gates G1-G4);
`design/R1_hostile_review.md` §5-6 and §9 (rigor requirements); `design/R3_generality.md` Part A (Lemma P, Lemma 0,
Theorems 1-3, Corollary A). Code: copied from `design/pilot2/code/` (unchanged files listed in §8 with their
SHA-256); new or changed files are marked "MAP".

## 0. Conventions (unchanged from the pilots)

- H(Jz) = ¼ Σ_edges (XX + YY + Jz ZZ) = A + Jz·B on `heavy_hex_graph(d)` (d = 5: n = 57; d = 7: n = 115; d = 3:
  n = 19 for gate G1 only), MPS order and sector S^z = s of the pilots (33 up / 24 down, 67 / 48; n = 19: 11 / 8).
  Energy of a state = exact MPO Rayleigh quotient at zero field (TeNPy) and, independently, the numpy evaluator
  `indep_eval.py`. E₀ := our χ = 320 ground energy (cold start from the Néel state, χ 160 → 320; n = 19: χ ≤ 512).
- **Labels (7 families, IBM's outputs and their averages):** m_s = (1/n)Σ η_i⟨Z_i⟩; C̄_zz = edge average of ⟨Z_iZ_j⟩
  (n_e = 64 / 132); C̄₂ = second-neighbour average (87 / 185 pairs); Z_bulk (site 46 / 93); Z_boundary (site 4 / 6);
  C_zz on one edge ((11, 46) / (23, 93)); Z_loop (12-site string through the bulk site). The field operator is S·O
  with S = n (m_s), n_e (C̄_zz), n_nn2 (C̄₂), 1 (local labels). For C̄_zz the field is exact as a Jz shift:
  H − σλ Σ_e Z_iZ_j = H(Jz − 4σλ).
- **τ = 0.06·|O_GS|** (an interval of half-width 3 % of the ground-state label: the pilots' convention). "Certified"
  means w_O ≤ τ; ratio = w/τ.
- **Chain states (MAP):** ground states of H − σλS·O by two-site DMRG at **χ = 160** (warm start from the χ = 320
  ground state or from the nearest computed λ of the same chain; mixer 1e-6; 3-10 sweeps; ΔE ≤ 1e-9; svd_min 1e-10).
  Every state is stored (raw tensors `.npz` with SHA-256) and evaluated in-process by both TeNPy and the independent
  numpy evaluator (energy, all seven labels, norm, sector variance from charge-resolved weights).

## 1. What is computed

For every (n, Jz, label) of the run list (§3), from one chain of each sign:

- **Inner side (rigorous, explicit states):** hull of the pool of all stored in-sector states of the same (n, Jz)
  (pure states and two-state mixtures; `hull.py`). By Toeplitz-Hausdorff (R3 Lemma P) every mixture point is attained by
  a pure state in the span of its two components (bond dimension ≤ χ_a + χ_b); the **pure-state headline** is
  w_pure = the width from the best single stored states (no mixture), reported next to w_in.
- **Outer side (DMRG-referenced):** σ⟨O⟩ ≤ (E − G_σ(λ) + δG)/(λS) for every chain point (G = ⟨H − σλSO⟩ of the chain
  state), minimised over the chain and capped at the spectral range ±1. **δG = max(2·δχ, |G(χ 160) − G(χ 320)|
  where gate P2 measured it)**, δχ = |E₀(χ 160) − E₀(χ 320)| of the same (n, Jz).
- **Widths** w_in, w_pure, w_out at E_lo, E_dig, E_up (§2) under reading 1, and at the reading-2 analogues.
- **ε_τ** = the energy above E₀ at which the two-sided width reaches τ: ε_τ^in = smallest ε with w_in ≥ τ (rigorous
  for "not certified"), ε_τ^out = smallest ε with w_out ≥ τ (certificate side). δe* = ε_τ/n.
- **The δe* rule (R2 Prop. L, R3 Corollary A):** χ = (o₊(λ₀) − o₋(λ₀))/(2λ₀) from the two smallest-field points
  (λ₀ = 0.005 for averages, 0.1 for local labels); **δe*_law = (S/n)·τ²/(8χ)**; law/measured = δe*_law/δe*.
- **Robustness (fractions of the digitized error ε_dig):** f_in = ε_τ^in/ε_dig (a "not certified" conclusion holds
  whenever IBM's true error is ≥ f_in·ε_dig) and f_out = ε_τ^out/ε_dig (a "certified" conclusion holds whenever the
  true error is ≤ f_out·ε_dig).
- **Regime:** ε_dig/Δ_in (in-sector gap, R2 runs) and ε_dig/Δ(S^z = s − 1) at every point.

## 2. Thresholds (windows)

- **Readings** (fixed before this hash in `code/readings_declared.json`, SHA-256 in §8). Reading 1 = the pilots'
  method (`pilot/PRIOR_ART_CHECK.md` §3, script copied verbatim as `code/digitize1_pilot_copy.py`, same calibration),
  re-run at every Jz = k/10; it reproduces the nine published values (r and gap) to ≤ 0.6 % (they were rounded to
  three digits). Reading 2 =
  `code/digitize2.py` (independent: least-squares axis calibration on all 30-55 tick marks per figure, rms 0.14-0.27
  px; marker centres by 2D template matching with legend-measured marker sizes). Agreement before this hash:
  ε₂/ε₁ = 0.93-1.02 over 89 training points (median 0.995); r within 5 % at 88/89 points; gap within 2.4 % at 50/50
  (n = 115 markers). Supp. Fig. 9 (same data) read by method 2: n = 57 median −3.1 % vs Fig. 2 (43 points, 1
  confusion with another series), n = 115 25 readable points (median −2.0 %), the rest hidden or confused.
- **Primary windows: reading 1.** Training points (Jz ≥ 1.6): ε_dig = r₁·Δ₁ (IBM ratio × IBM gap; the n = 57 gap above
  Jz = 1.6 is the n = 115 marker, as in the pilots); **E_lo = E₀ + 0.8·r₁·min(Δ_ours, Δ₁)** (witness side);
  **E_up = E₀ + 1.2·r₁·max(Δ_ours, Δ₁) + δχ** (certificate side); E_dig = E₀ + ε_dig. Δ_ours = min of our computed
  in-sector E₁ (R2), S^z = s − 1 (R3) and S^z = s + 1 (R4, n = 57 only) gaps (R3 only at the J* extra points).
- **OOD (Jz = 1.1-1.4; conditional):** IBM reports no energy; the pilots' declared floor δe = 0.012 per site:
  ε_dig = 0.012·n, E_lo = E₀ + 0.8·0.012·n, E_up = E₀ + 1.2·0.012·n + δχ. Every OOD statement is conditional on it.
- **Reading 2** (analysis only): the same formulas with (r₂, Δ₂).
- **n = 19 (gate G1 only):** the per-site window of n = 57 at the same Jz (ε = ε₁(57)·19/57, ×0.8 / ×1.2).
- Validity (as pilot2): the certificate side contains IBM's energy if the reading is within ±5 % per factor, IBM's
  gap within 10 % of max(Δ_ours, Δ₁) and E₀^IBM − E₀^ours ≤ 0.04·r·Δ; the witness side needs E_lo ≤ E_dev. Both also
  need IBM's energies to be Rayleigh quotients of in-sector states (not verified).

## 3. Runs (TeNPy 1.1.0; references as in pilot2 unless stated)

Grid **Jz ∈ {1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.3, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0}** at n = 57 and
n = 115; J* extra points **{3.2, 3.4}** (m_s and C̄_zz only); n = 19 at {1.6, 4.0} (gate G1).

- **References per (n, Jz):** R1a (ground state, χ 160 → 320, cold from Néel), R3 (S^z = s − 1), R2 (in-sector E₁,
  orthogonal to the ground state), R4 (S^z = s + 1, n = 57 only); MAP: R2-R4 at χ ≤ 200 (an under-converged energy only
  enlarges Δ_ours, i.e. E_up; E_lo uses min(Δ_ours, Δ₁)); R1b (χ = 480) at n = 57, Jz ∈ {1.2, 1.6, 3.3, 4.0, 6.0}.
- **Lab task (MAP), one per (n, Jz, label), both signs:** (1) λ₀ on both sides → χ and the law's first guess
  ε_τ^law = S·τ²/(8χ); (2) per side, the target energies ε_lo, ε_up (aimed 3 % above) and min(ε_τ^law, 20·ε_up) are aimed at by
  log-log interpolation of ε(λ) until each has a point within ±10 % (≤ 2 tries); ε_lo is **straddled** (one point
  in [0.9, 1]·ε_lo and one in (1, 1.1]·ε_lo, ≤ 3 tries), so that the witness-side inner width is tight; (3) the
  ε_τ measured from the points (inner and outer) is straddled in the same way on each side, in up to two rounds
  (stop when inner and outer agree to 2 %); ≤ 9 evaluations per side; λ_max = 1.28 (m_s, C̄₂), Jz' = Jz − 4σλ ∈
  [0.2, Jz + 8] (C̄_zz), 6.4 (local labels). The law check (§1) compares ε_τ^law with the measured ε_τ.
- **Gate tasks:** P2 (χ = 320 re-run of G at the decisive λ = the chain point that gives the outer bound at E_up) and
  P3 (cold start from Néel at χ = 160 at the same λ; m_s only) at (n, Jz) ∈ {57, 115} × {3.3, 4.0}, labels m_s and
  C̄_zz, both signs; G1 (n = 19, exact sector diagonalization of the limits of m_s, C̄_zz, Z_bulk at E_lo, E_dig, E_up
  and ε_τ, Jz = 1.6 and 4.0).
- **Minimal-χ witnesses (R1 C5):** at (57, 1.6), (57, 4.0), (115, 1.6), label m_s: χ ∈ {16, 32, 64}, both signs,
  cold from Néel, λ bisected so that the best state stays below E_lo (≤ 10 evaluations); reported: D_pure(χ) and its
  fraction of the full pure width.
- **Separate-process re-evaluation (G4)** after the run, TeNPy not importable, of every headline witness component:
  the hull components (mixtures) and best pure states at E_lo and E_up of m_s and C̄_zz at every grid Jz (both n) and
  of Z_bulk at Jz = 1.6, 4.0, 6.0.
- **Laptop (light):** analysis; the explicit Toeplitz-Hausdorff pure witnesses (R1 C6) for the two m_s mixture
  witnesses at n = 57, Jz = 1.6, E_lo (fetched `.npz`; `code/th_witness.py`); figure; comparisons with the pilots.

**Priorities** (scheduler order; a higher number is dropped first, §5): 1 references, m_s and C̄_zz rows (both n),
G1; 2 C̄₂ rows (both n), R1b, gates P2/P3; 3 local rows at n = 57, J* extra points, minimal χ; 4 n = 115 Z_bulk
rows (Jz ≤ 4.5); 5 n = 115 C_zz(edge) and Z_boundary rows (Jz ≤ 4.5); 6 n = 115 Z_loop rows (Jz ≤ 4.5); 7 n = 115
local rows at Jz = 5.0-6.0. 432 tasks in total (`witness.py plan`).

## 4. Decisive quantities and decision rules

**Row status** (every (n, Jz, label), reading 1): **CERTIFIED** if w_out(E_up) ≤ τ (DMRG-referenced, conditional on
§2); **NOT CERTIFIED** if w_in(E_lo) ≥ τ (rigorous given E_lo ≤ E_dev; OOD conditional on the floor); **GRAY**
otherwise. The same under reading 2 (recorded). "NOT CERTIFIED (pure)" if also w_pure(E_lo) ≥ τ.

**J\*** (per label and n, readings 1 and 2): on IBM's 0.1 training grid (1.6-6.0), ε_τ^out interpolated log-linearly in
Jz between computed grid points; a training point is certified (central) if ε_dig ≤ ε_τ^out and (strict) if
1.2·ε_dig·max(1, Δ_ours/Δ₁) ≤ ε_τ^out; **J\*** = the smallest training Jz from which every larger training point is
certified (central; strict recorded); also the number of certified training points out of 45. Resolution ±0.1 =
IBM's grid. **Interpolation check:** ε_τ^out at 3.3 interpolated from 3.2 and 3.4 vs computed: if they differ by more
than 5 %, J* is reported only at computed grid points.

**Paper claims, decided here:**
- **C-A (positive map).** MAP-POSITIVE if m_s and C̄_zz are CERTIFIED at every computed Jz ≥ 4.0 at both n = 57 and
  n = 115, and gates G1, P1-P4, G4 pass; MAP-PARTIAL if this holds at one size only or at a subset of Jz ≥ 4.0;
  MAP-ABSENT if neither label is CERTIFIED at any Jz ≥ 4.0 at n = 115. Prior (judgment): P(POSITIVE) ≈ 0.85.
- **C-B (negative region).** Every label NOT CERTIFIED at every Jz ≤ 1.6 at both n (rigorous; OOD conditional).
  Prior ≈ 0.97.
- **C-C (local labels).** "No local label is certified at any computed point" holds if no row of Z_bulk, Z_boundary,
  C_zz(edge), Z_loop is CERTIFIED (both n); otherwise J* of each local label is reported. Prior: none certified at
  n = 115 ≈ 0.7; some local row certified at n = 57, Jz = 5.5-6.0 ≈ 0.35.
- **C-D (δe* rule).** Holds if δe*_law/δe*^out ∈ [0.8, 1.25] at every averaged-label point with Jz ≥ 2.0 (both n);
  local labels recorded (the rule applies until the full-range ceiling). Prior ≈ 0.8.
- **C-E (intensivity).** δe*(115)/δe*(57) ∈ [0.67, 1.5] for m_s, C̄_zz, C̄₂ and ≤ 0.75 for local labels (1/n drift) at
  every Jz ≥ 2.0 computed at both sizes. Prior ≈ 0.75.
- **Robustness:** f_in and f_out for every row; for each claim, the smallest (C-B, C-C) or largest (C-A) fraction of
  the digitized error at which it still holds.

**Gates (a failure means "no decision" for the claims that depend on it; the reason is reported).**
- **G1** (n = 19 vs exact diagonalization): |w_out − w_ED| ≤ 0.01·w_ED at E_lo, E_dig, E_up; |w_in − w_ED| ≤ 0.01·w_ED
  at E_lo (straddled) and ≤ 0.03·w_ED at E_dig, E_up (not straddled); ε_τ^in, ε_τ^out within 5 % of the exact ε_τ
  (m_s, C̄_zz, Z_bulk; Jz = 1.6, 4.0).
- **P1** (χ): |E₀(χ 320) − E₀(χ 480)| ≤ 0.02·ε_up at the five R1b points.
- **P2** (outer-bound accuracy): |G(χ 160) − G(χ 320)| ≤ 0.01·ε_up at every checked decisive λ.
- **P3** (warm starts): F_cold ≥ F_warm − 1e-5·|F| at every checked λ.
- **P4** (sector and evaluators): every stored state of the declared sector has variance < 1e-12 and TeNPy charge =
  2s; TeNPy vs in-process evaluator |ΔE|, |Δm_s| < 1e-8.
- **G4** (separate process): |ΔE|, |ΔO| (all labels), |Δnorm|/norm < 1e-8 and sector variance < 1e-12 for every
  headline component whose `.npz` is kept; every headline mixture (all components evaluated) and pure witness energy
  (from the separate evaluation) ≤ its threshold; components removed by the disk rule are listed.
- **G3** (record only): our S^z = s − 1 gap vs IBM's gap (both readings) within 10 %.

## 5. Cost cap and cloud rules

- **Hard cap: 15 VM-hours** (n2-highmem-8, 0.594 EUR/h list: ≤ 8.9 EUR); expected 10-13 VM-h (≈ 75 job-hours on 8 processes). **Checkpoint** ≈ 1.5
  VM-h after the scheduler starts: projection from the measured task times; if it exceeds 13.5 VM-h, drop (via
  `skip.txt`) in this order until it fits: (1) priority 7 (n = 115 local rows at Jz = 5.0-6.0); (2) priority 6
  (n = 115 Z_loop rows); (3) priority 5; (4) priority 4; (5) minimal χ at n = 115; (6) the n = 115 J* extra points.
  **Never dropped: priority 1 (references, m_s and C̄_zz rows, G1).** If the cap is still at risk, the scheduler is
  stopped at 14 VM-h and what exists is analysed.
- `gcloud` only with `--configuration=sqd-research`; only **cj-runner-1b**, zone europe-west3-b; never cj-runner-1,
  never cj-runner-2 (another agent's), never another configuration, never ADC. Sequence (pilot2's `code/vm/`, copied
  as `code/vm/vm_map.sh` and `map_vm.sh`): `cj-poweroff=off` before start; **max-run-duration 13 h with STOP** as
  safety net on every boot; after boot `systemctl stop cj-runner@vm`, confirm no `heavy_run.py`; record line counts
  and SHA-256 of the sealed ledgers at boot and at the end; work only under `/mnt/cj/sandbox/map_<stamp>/` (tools in
  `/mnt/cj/sandbox/map_tools/`); never touch `/mnt/cj/mirror`, `prereg/runs`, the queue, the ledgers or
  `/mnt/cj/venv` (used read-only). At the end: `cj-poweroff=on`, stop the VM, clear max-run-duration, `instances
  list` showing TERMINATED. No credential, token or personal data is printed or stored.
- **Disk rule:** if `/mnt/cj` has < 18 GB free at boot, `prune.txt = 1` (each lab task keeps the `.npz` of the λ₀
  points and of the two points per side nearest each of ε_lo, ε_dig, ε_up and the measured ε_τ; the JSON of every
  state keeps both evaluations and the SHA-256).
- Concurrency 8 tasks (operationally up to 10). TeNPy wheel: the pilots' `physics_tenpy-1.1.0-cp311-…whl`
  (890b6d42…). Unit tests (`tests/test_witness.py`, `tests/test_r2.py`, `tests/test_map.py`) must pass on the VM
  before production.
- Outputs copied to `gs://cj-sqd-research-0f818af9/exploratory/map_<stamp>/`.

## 6. Reporting

- Verbs "computed", "evaluated", "digitized". Next to every number: rigorous (inner, explicit states, given
  E_lo ≤ E_dev), DMRG-referenced (outer), conditional (OOD floor; readings).
- Every reported number comes from a file with SHA-256 in the fetched outputs or from a laptop re-execution listed in
  RESULTS.md. Re-executed / only compared / not checked are listed separately.
- RESULTS.md: 8-line summary in simple Spanish, then English; the full map table; J* per label and size; the δe*
  rule check; robustness fractions; the two readings and their agreement; minimal-χ witnesses; the Toeplitz-Hausdorff
  construction; VM-hours and cost; deviations. A draft main-text figure (map) as PNG with its script.

## 7. Only compared (no new decision)

Pilot2 (n = 57, Jz = 3.0-6.0 m_s; 4.0 C̄₂, Z_bulk, C_zz(edge); the χ = 320 C̄_zz curve; n = 115, 4.0 m_s, Z_bulk) and
the witness pilot (n = 57, 1.2/1.6/2.5 m_s and 1.2/1.6 local labels; n = 115, 1.6 m_s), at their own thresholds where
they coincide with ours (E_lo = the witness pilot's E_thr at 1.2 and 1.6).

## 8. Code and data manifest at hash time (SHA-256)

```
8eb866e7e6026af9a098f9d82163aefa468db2adc79623ec00b65eaab62f5349  code/analyze_map.py
f483f412c688bdbe9041aac403b70ab401677f7d4a9409a7d4c7a4e1c940ebce  code/compare_pilots.py
9b0d9e83706558a2f31b290842006b5a833c95a06fb57ca3975ad1e7a9f4318c  code/compare_readings.py
60fe5ce013787c0eeec0c9cf3df0a9bd32aaaf6b15c9ffdb973cab8730511cd0  code/digitize1_pilot_copy.py
7c1aea44b79bcbbf023f729d4fd05ca1676aaadd28a139a79d730cdf9f6a6741  code/digitize2.py
eafbfae5a643589d8fc949e084d061e636d462e6fd85aec039983b1823ba72cf  code/ed.py
26cd8b9d2f74c6ce049e55d74c696575607d606195bedfa1be361b0876216ef0  code/gen_graphs.py
d8d42f5f54e33699562ba4584ca06925074d206ee8c6baddf73b9ab8c76aace1  code/graphs/hh_d3.json
80790817cc70ed56396799df3ca7205cfe62519477fda50e6e13311b1d528712  code/graphs/hh_d5.json
b5b630097e895a46a6d4072171fec3e5552ec0ea8f6e7b41e9106c9be6e7c8d7  code/graphs/hh_d7.json
d42ce32ad4492c48817aa0e7e326638f4eb7bf41e321fe205fecf783c2c680da  code/hhmodel.py
8598cdc365b58422c35fc7d5dbdc6fb68f1ea9b994c233a0fa7d7c934fcbc88a  code/hull.py
a2993adce626856a94f90c63e80e4737ab76cc691b4e6902c7a863acefb43a54  code/indep_eval.py
7784085be04d1073a35ab5e46637607d982f53b87679bddde2ccd1693caff377  code/make_readings.py
1e1e12f4db07d3f820cf430c52059623bd444c036d0e3f57e8801110bde5056c  code/plot_map2.py
1e2992f7ce1644a8f311956da4dfbd89ab3f10ef030e63bf749d86cd6412c600  code/project.py
cb4c697f65246c33c51fecf66a5e9ce880e2fdc405252b0a9aeee78d5e57cb74  code/readings_declared.json
eee644326144ed3a4e22225a0dc6e1e31a4d620fe6353ca8c7502020286f3437  code/sched.py
a1e1f7111c6d8ef579d703fc31a3ed77207a4bb185f5203110b23a23b5f0b883  code/tests/dryrun_map.py
2b398eb1f49e20e93ef964dc9a6ebc7efa643f3a04f9fd154145adee957aa888  code/tests/test_map.py
eda4706709588125cb8135d42ad6db3fc93f4ec0187decb9d8da5743ee9ca56d  code/tests/test_r2.py
4a589ec65898750e4d134446819f9a9f1e1457f3e0a6dd384a2b049a6cee2125  code/tests/test_witness.py
c39532dba667093dd4a157f85176e841a9eb85b6c85ad020162caaa5f3a0a67b  code/tests/toygraphs.py
c6cfb104ca09ce9d117709032f85ae290b8397d4f9ce4b717d28c173e0da8590  code/th_witness.py
187be0bafa30f67ccabe7ec66e3d52b3f397323455c4803d01c357a2cc04a880  code/vm/map_vm.sh
39678335794632edca5dd0edc64d77a588fdea83bdf333efd6231702ce06a143  code/vm/vm_map.sh
d9aec0bebeca5e25b9a681571ee56f0ae89139e617b928b5a81e0ad16b9f78b1  code/witness.py
748857e26f14632d09519c101a73266822637ff582566c27d9f1719e71baa18d  digitization/compare_stdout.txt
dec11e4bf9f30253617229c76940945268cb5bf3ddd5da970e11540cd5126c62  digitization/reading1_fig2_raw.txt
0e276d1e070535797ad4a817efd3e017f18973bf32eac1ef7c315789f660b3c0  digitization/reading1_fig4_raw.txt
b45b10c371b126ec5297288777787cd4dd6dee758300fcdeb755274ef29af208  digitization/reading2_raw.json
9eccb7c37e1547c3ae5ef681865790cb65923711a769902235c17ad23b5219ff  digitization/readings.json
890b6d42e1daf067a87a6d0dac283c757f22e12b6a02718335f379c0cac227fe  wheels/physics_tenpy-1.1.0-cp311-cp311-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl
```

Unchanged copies of pilot2 files (identical SHA-256): `hhmodel.py`, `indep_eval.py`, `hull.py`, `sched.py`, `ed.py`,
`gen_graphs.py`, `graphs/hh_d{3,5,7}.json`, `tests/toygraphs.py`, `tests/test_witness.py`, `tests/test_r2.py`; the wheel is the
pilots' TeNPy 1.1.0 wheel. `digitize1_pilot_copy.py` is a verbatim copy of the pilot's `digit.py`. Downloads read as data
(scratchpad `pilot_step0/dl/`, SHA-256 as in `pilot/step0_evidence/DOWNLOADS_SHA256.txt`): `fig2v6.png` 61a9eaf6…,
`fig4v9.png` 0d52df22…, `suppfig_energy_super_comparisonv5.png` 9778ded8….
