# Rigor test (optional upgrade): certified lower bounds on heavy-hex XXZ ground energies — DECLARATION

**Label: OPTIONAL TEST, declared and hashed before any computation at n ≥ 19.** Written 2026-10-31 (UTC) under the
coordinator's brief (plan `phase3/PLAN_UNICO_2026-10-30.md` §6, row "Prueba opcional de rigor completo"; cap 5 VM-hours
on cj-runner-1b). The SHA-256 of this file goes into `DECLARATION.sha256` before the VM is started. Nothing here changes
after the hash; anything learned later goes, dated, into `DEVIATIONS.md`.

**Run before this hash (and nothing else):** laptop only. (i) `code/requirement.py` on the fetched outputs of the map
run (`../map/out_20261030T022613Z/out/chains/*.json`, `../map/laptop_analysis/summary_map.json`): reading existing
numbers, no new physics; (ii) code writing; (iii) toy tests at n ≤ 12 (exact dense diagonalization; §6). Structure-only
counts of clusters/overlaps at n = 19 and 57 (no Hamiltonian evaluated). No computation at n ≥ 19, no cloud action.

## 0. Model and conventions (identical to the map)

H(Jz) = ¼ Σ_edges (XX + YY + Jz ZZ) on `heavy_hex_graph(d)` (MPS site labels of `code/graphs/hh_d{3,5}.json`,
identical SHA-256 to the map's copies), sector S^z = (n_up − n_down)/2 (33/24 at n = 57; 11/8 at n = 19). The chain
Hamiltonians of the map: m_s side σ: H − σλ Σ_i η_i Z_i; C̄_zz side σ: H − σλ Σ_e Z_iZ_j = H(Jz − 4σλ).

## 1. What a rigorous certified row needs (derived; replaces the plan's guess of 0.3 %)

The map's outer (certificate) side is σ⟨O⟩ ≤ (E_up − F_k + δG)/(λ_k S), minimised over the chain points k, where F_k is
the χ = 160 DMRG energy of the tilted Hamiltonian (an **upper** bound on its ground energy G). E_up is the declared
upper bound on IBM's energy (DMRG E₀ is an upper bound on the true E₀, so E_up needs no lower bound). The side becomes
rigorous if F_k is replaced by a certified lower bound G_LB,k and δG is dropped. With a uniform slack s = F − G_LB the
rigorous width at E_up is w(s) = Σ_σ min_k (E_up − F_k + s)/(λ_k S). **s_req** = the largest s with w(s) ≤ τ
(bisection on the stored chain points; `outputs/requirement.json`, SHA-256 in §8). The **decisive points** are the
minimising chain points of each side at E_up + s_req; at those points the exact condition for a pair of slacks is
Σ_σ s_σ/(λ_σ S) ≤ τ − Σ_σ (E_up − F_σ)/(λ_σ S) (equality at s_+ = s_− = s_req).

| n | Jz | row | ε_up (J) | ε_τ^out (J) | **s_req (J)** | s_req/\|E₀\| | decisive λ (+ / −) | F at decisive λ (+ / −) | Jz' (C̄_zz) |
|---|---|---|---|---|---|---|---|---|---|
| 57 | 4.0 | m_s | 0.11845 | 0.30168 | **0.1832** | **0.273 %** | 0.5850 / 0.2196 | −99.4101 / −55.1313 | — |
| 57 | 4.0 | C̄_zz | 0.11845 | 0.30357 | **0.1851** | **0.276 %** | 0.2500 / 0.5025 | −51.9497 / −98.1687 | 3.0001 / 6.0099 |
| 57 | 6.0 | m_s | 0.06254 | 0.72026 | **0.6577** | **0.671 %** | 1.2800 / 0.3448 | −170.1744 / −78.8190 | — |
| 57 | 6.0 | C̄_zz | 0.06254 | 1.00176 | **0.9392** | **0.958 %** | 0.6460 / 2.0000 | −58.1466 / −224.8680 | 3.4162 / 14.0000 |
| 19 | 4.0 | m_s (gate G1 row) | 0.03939 | 0.07781 | 0.0384 | 0.183 % | 0.4363 / 0.1972 | −29.0385 / −17.5045 | — |
| 19 | 4.0 | C̄_zz (gate G1 row) | 0.03939 | 0.08602 | 0.0466 | 0.222 % | 0.2323 / 0.4056 | −16.6756 / −28.8468 | 3.0708 / 5.6223 |

For the record (not decisive here): the other certified n = 57 rows need 0.0145-0.0173 J (0.025-0.030 %) at
Jz = 3.4, 0.074 J (0.12 %) at 3.6, 0.32-0.34 J (0.43-0.45 %) at 4.5, 0.44-0.52 J at 5.0, 0.55-0.73 J at 5.5; n = 115
rows are in `outputs/requirement.json` (not tested). In units of the quantum correction F − F_classical (≈ 3.9 J at
Jz' = 3, ≈ 3.7 J for the m_s "−" point at Jz = 4) the Jz = 4.0 rows tolerate a loss of ≈ 5 % (uniform) to ≈ 6-7 %
(best split of the two sides).

**H(Jz) itself** (E₀ of H at Jz = 4.0, 6.0; λ = 0) is not needed by the certificate side (see above); it is declared
because the brief asks for it and as the λ → 0 anchor. Its requirement is s_req,H = min over the two rows at that Jz:
**0.1832 J (Jz = 4.0)** and **0.6577 J (6.0)**. (A rigorous witness side would need E₀ − E₀,LB ≤ 0.2·ε_dig ≈ 0.02 J at
Jz = 4: out of scope, recorded only.)

## 2. Method (choice by cost)

**(b)/(c) hybrid: local-consistency (cluster-marginal) relaxation solved in its dual form, i.e. an Anderson cluster
bound with fully optimized splitting.** For clusters C_k and every pairwise overlap O = C_k ∩ C_l, any real symmetric,
S^z-block-diagonal operators Y_O on O and any μ give

  E₀(sector) ≥ Σ_k λ_min(h_k) − μ·(n_up − n_down),  h_k = (terms assigned to k) + Σ_O (±Y_O ⊗ 1) + μ Σ_{i∈A_k} Z_i,

because Σ_k h_k = H + μ Σ_i Z_i exactly (each Y_O enters +Y in k and −Y in l; every term and every Z_i once) and
Σ_i Z_i = n_up − n_down on the sector. The Y_O span all S^z-preserving operators on O, so they also redistribute terms
(the plain Anderson bound, every term spread uniformly, is the starting point and is reported). The μ term imposes
the sector's mean magnetization (it excludes the reversed-sublattice state for the m_s "−" side).

- **Levels:** **eball2** (main): clusters = sites within graph distance 2 of an edge's endpoints (≤ 9 sites; n = 57:
  62 clusters, 719 overlaps, ≈ 1.3·10⁵ multiplier entries); **vball2** (hierarchy check): radius-2 vertex balls (≤ 7
  sites; 55 clusters). Strict subsets are removed. Larger clusters (radius-3 balls, ≤ 13 sites) are not run: the exact
  verification below scales as (block size)³ in big-integer arithmetic.
- **Numerics** (`code/lb_opt.py`, numpy/scipy only): maximise the soft-min smoothing of the bound with L-BFGS-B,
  β = 30, 300, 3000, 30000, 100000 (J⁻¹), ≤ 600 iterations per β, warm-started; keep the best hard bound. Round Y and μ to
  dyadic rationals (2⁻³²); per cluster claim t_k = λ_min(h_k) − 1e-9·(1 + ‖h_k‖_∞) rounded down to 2⁻³². λ values are
  the map's exact float λ (dyadic), so the bounded Hamiltonian is exactly the one whose DMRG energy F is the reference.
- **Exact certification** (`code/verify_exact.py`, separate process, pure Python integers, does not import the
  optimizer): re-derives the Hamiltonian from the graph JSON and the task, rebuilds every h_k from the certificate with
  its own code (checks S^z conservation, symmetry, the ±Y pairing, term and site assignment), and proves
  D·(h_k − t_k·1) ≻ 0 for every S^z block by fraction-free Bareiss elimination (all leading principal minors > 0).
  E_LB = Σ_k t_k − μ(n_up − n_down) is then an exact rational lower bound on the sector ground energy. **Only verified
  bounds are reported as rigorous.**
- **Slack** s = F_ref − E_LB with F_ref = the map's DMRG value (χ = 160 chain F at the decisive λ; χ = 320 E₀ for H).
  F_ref ≥ the true ground energy, so the reported slack is ≥ the true slack (conservative). At n = 19 the true slack
  against exact diagonalization (`code/ed_sector.py`) is also reported.

## 3. Runs (`outputs/plan.json`, 48 jobs; `code/make_plan.py`)

- **n = 57 (decisive), both levels:** the 8 decisive tilted Hamiltonians of §1 (m_s and C̄_zz, Jz = 4.0 and 6.0, both
  signs) and H(4.0), H(6.0).
- **n = 19 (calibration), both levels:** the same 10 specifications (same Jz, σ, λ) with exact diagonalization, plus the
  4 decisive points of the map's n = 19 rows at Jz = 4.0 (with their n = 19 chain F).
- Order: n = 57 eball2, then n = 19, then n = 57 vball2; 8 jobs in parallel (one thread each).

## 4. Decision rule

- Per n = 57 row: **ρ_row = [Σ_σ s_σ/(λ_σ S)] / [τ − Σ_σ (E_up − F_σ)/(λ_σ S)]** at the declared decisive points (equals
  s/s_req for equal slacks). ρ_row ≤ 1 ⟺ the rigorous outer width at E_up, w_rig = Σ_σ (E_up − E_LB,σ)/(λ_σ S), is ≤ τ,
  i.e. the row is CERTIFIED with no DMRG reference on its outer side (still conditional on the readings and on IBM's
  energies being in-sector Rayleigh quotients, as in the map).
- Per H(Jz): ρ_H = s_H / s_req,H.
- For each item the best verified bound over the two levels is used (each is independently valid).
  **ρ_max = max(ρ of the 4 rows, ρ_H at 4.0 and 6.0).**
- **ACCEPT** if ρ_max ≤ 1: the positive rows m_s and C̄_zz at Jz = 4.0 and 6.0 (n = 57) become fully rigorous; the paper
  may say so for those rows (and states that 3.4-3.6 and 4.5-5.5 were not tested unless later run).
  **REJECT** if ρ_max ≥ 3: the paper keeps one sentence (no certified lower bounds reached the needed slack).
  **GRAY** otherwise (reported with the per-row ρ and w_rig/τ).
- **Gate (n = 19):** every verified E_LB ≤ exact E₀ + 1e-9 J; otherwise NO DECISION (a bug) and the n = 57 numbers are
  not used. A certificate that fails exact verification is reported as "not verified" and its item counts as missing;
  missing items make the verdict INCOMPLETE unless the rule is already decided by the present items (REJECT if some
  present ρ ≥ 3).
- Prior (judgment, from the toys of §6): P(ACCEPT) ≈ 0.35, P(GRAY) ≈ 0.4, P(REJECT) ≈ 0.25.

## 5. Cloud and cost

- `gcloud` only with `--configuration=sqd-research`; only **cj-runner-1b** (n2-highmem-8, europe-west3-b); never
  cj-runner-1 or cj-runner-2 (another agent's), never another configuration, never ADC. Procedure (`code/vm/vm_rigor.sh`,
  copied from `pilot_witness/code/vm/`): refuse to start unless cj-runner-1b is TERMINATED; `cj-poweroff=off` before
  start; max-run-duration 5 h with STOP as safety net; after boot `systemctl stop cj-runner@vm` and confirm no
  `heavy_run.py`; ledger line counts and SHA-256 at boot and at the end; work only under `/mnt/cj/sandbox/rigor_<stamp>/`
  (tools in `/mnt/cj/sandbox/rigor_tools/`); never touch `/mnt/cj/mirror`, `prereg/runs`, the queue, the ledgers or
  `/mnt/cj/venv` (used read-only). At the end: `cj-poweroff=on`, stop, clear max-run-duration, `instances list`
  showing TERMINATED.
- **Cap 5 VM-hours (≈ 3 EUR).** Expected ≈ 1.5-2.5 VM-h. Stop rule: at 4 VM-h after start, set the STOP flag, analyse
  what exists, shut down by 4.5 VM-h. VM toy tests (`tests/test_toy.py`, vball2, n ≤ 12) must pass before the run.
- Outputs copied to `gs://cj-sqd-research-0f818af9/exploratory/rigor_<stamp>/`.

## 6. Toy tests before the hash (laptop, n ≤ 12; exact diagonalization)

12-site heavy-hex piece (tree), 12-site ring, 10-site tree; every verified bound ≤ exact E₀; a tampered certificate
(one t_k raised by 2⁻⁶ J) is rejected. Slack (E₀ − E_LB)/|E₀| at Jz = 4 (H): vball2 0.31 % (piece; 0.30 % with a longer
optimization), 1.12 % (ring), 0.12 % (tree); C̄_zz "+" point (Jz' = 3.0): 0.54 %, 2.0 %, 0.17 %. eball2 on the piece
(H, Jz = 4; claimed bound, not run through the verifier): 0.031 %. The toys' sectors have equal sublattices, so their
m_s "−" points are not representative (the reversed state is in-sector there). On the toys the eball2 clusters cover
most of the graph; n = 19 is the real calibration.

## 7. Reporting

RESULTS.md: 8-line summary in simple Spanish, then English: s_req per row; the bounds at n = 19 (with exact
diagonalization) and n = 57, each with its exact-verification record; ρ per row and per H; the verdict; cost; VM final
state; re-executed / only compared / not checked. Every number from a file with SHA-256 in the fetched outputs or from a
laptop re-execution. `code/analyze.py` (declared here) produces `results.json`.

## 8. Manifest at hash time (SHA-256)

```
dbd3c45639ace935e3dd70503f914cb50eb4450083624d90e42487a3da557fb2  outputs/requirement.json
3895fd9489a4da4ab870e1c852db8406b8f79bf3931e994e0b49a84f00bbe0b7  outputs/plan.json
e7a897a7b2ee452d0d60af7cb774c8416ac5a059e2a59ab343f07cf96a3be9e2  code/analyze.py
f841cbd5eb1b289f660b59f4a92858f2fcea9d2fc745b968e5ea42d13f0003cf  code/ed_sector.py
25cdf279c213aa1274a1a3f3efc5056984290cbb71122ea980ab7746c8165353  code/lb_opt.py
160e434ab1f57bc364794649519098bf6094700388f7e9cf498ccbe243e3c65c  code/lbcore.py
e208d9859b58b7e4e47ead545cb456e132829ef215c97a6c94d97dc0dcbd6ed0  code/make_plan.py
d15978c760961c68774e3c642efe8d82755929286784a1c49815aba3500c746f  code/requirement.py
004d4fa42d1709aeb5f6f0b77114afcd2ee5f1f6f24ebb7e54ff5923380c9694  code/run_all.py
dfee00b9c7abb6dde007a36d3402e932165f86f83c7eb7c36acea1141043ca9c  code/verify_exact.py
28a30a4053b916a740802bf95d42745652f773617e5b88e6cd9e4ecf992d7bfc  code/tests/test_toy.py
9943d22e3a6d03b20820ddf2d6be6984c572a6a2f5537d34215882b3e9af7c77  code/vm/rigor_vm.sh
57586e78b2aadc0044535bb2dcc6168eef466ab69901fdfb4edcda6ecf4ccec5  code/vm/vm_rigor.sh
d8d42f5f54e33699562ba4584ca06925074d206ee8c6baddf73b9ab8c76aace1  code/graphs/hh_d3.json
80790817cc70ed56396799df3ca7205cfe62519477fda50e6e13311b1d528712  code/graphs/hh_d5.json
b5b630097e895a46a6d4072171fec3e5552ec0ea8f6e7b41e9106c9be6e7c8d7  code/graphs/hh_d7.json
```
