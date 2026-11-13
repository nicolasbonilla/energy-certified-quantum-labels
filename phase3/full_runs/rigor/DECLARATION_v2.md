# Rigor test, stage v2: declared λ grid — DECLARATION

**Label: DECLARED STAGE v2, hashed before any v2 computation.** Written 2026-10-31 (UTC) after stage v1 (`DECLARATION.md`
fddd7542…, `RESULTS.md`: declared verdict REJECT; post hoc the m_s rows were certified at a smaller field). Brief of
the coordinator: make the post-hoc finding a declared result by fixing the λ grid and the rule in advance. Cap 5 VM-hours
on cj-runner-1b. The SHA-256 of this file goes into `DECLARATION_v2.sha256` before the VM is started; later changes go,
dated, into `DEVIATIONS_v2.md`.

**Run before this hash:** laptop only — building the grid from the map's stored chains (`code/make_plan_v2.py` →
`outputs/grid_v2.json`, `outputs/plan_v2_A.json`) and a scheduler test in mock mode (no physics). No v2 bound computed.
Code of the bounds and of the exact verifier is unchanged from v1 (`lb_opt.py`, `lbcore.py`, `verify_exact.py`,
`ed_sector.py`: same SHA-256 as in `DECLARATION.md` §8).

## 1. Why any λ is allowed

For every λ > 0 and every in-sector state ρ with energy ≤ E_up: σ⟨O⟩ ≤ (E_up − G_σ(λ))/(λS) ≤ (E_up − E_LB(λ))/(λS),
where E_LB(λ) is an exactly verified lower bound on the sector ground energy of H − σλSO. Hence, for any set of λ
values, the minimum over the set is a theorem. Choosing the set in advance (this file) makes it a declared result.

## 2. The grid (fixed here; `outputs/grid_v2.json`)

For every row (n, Jz, label) in scope and each sign σ:
- **all λ points of the stored map chain** `chain_n{n}_J{Jz}_{label}_{σ}.json` (the λ₀ = 0.005 point included), at the
  exact float λ of the chain;
- **geometric refinement:** λ_dec·0.85^k, k = 1, 2, 3, rounded to the dyadic grid 2⁻²⁰, where λ_dec is the chain point
  that minimises the DMRG-referenced bound (E_up − F)/(λS) at E_up (no δG). (It moves the field away from the
  first-order crossings that sit above λ_dec on the "−" m_s chains.)
- Upper reference for every grid point, used only for pruning and for reporting slacks, never inside a certified
  width: F_up(λ) = min over the stored states k of that chain of (E_k − σλS·o_k), the energy of an in-sector state, hence
  ≥ the true G_σ(λ) (at chain points F_up ≤ the chain's F).
- **Provable pruning:** u_lb(p) = (E_up − F_up(p))/(λ_p S) ≤ the rigorous u of any certified bound at p. A point is not
  computed if u_lb(p) + min_q u_lb(q) > τ (q over the other side): with p no certified width ≤ τ is possible.

Scope and grid sizes (points kept / grid points per side; λ_dec per side):

| scope | n | Jz | row | τ | DMRG width / τ | v1 s_req (J) | + kept/grid | − kept/grid | λ_dec (+ / −) |
|---|---|---|---|---|---|---|---|---|---|
| S1 | 57 | 4.0 | m_s | 0.0575 | 0.610 | 0.1832 | 9/10 | 10/12 | 0.3149 / 0.1875 |
| S1 | 57 | 4.0 | C̄_zz | 0.0573 | 0.625 | 0.1851 | 8/9 | 9/10 | 0.1678 / 0.2600 |
| S1 | 57 | 6.0 | m_s | 0.0589 | 0.232 | 0.6577 | 8/9 | 9/12 | 0.4065 / 0.2618 |
| S1 | 57 | 6.0 | C̄_zz | 0.0588 | 0.247 | 0.9392 | 11/12 | 9/10 | 0.2321 / 0.3300 |
| S2 | 57 | 3.4 | m_s | 0.0566 | 0.958 | 0.0145 | 8/9 | 7/10 | 0.3052 / 0.1619 |
| S2 | 57 | 3.4 | C̄_zz | 0.0563 | 0.953 | 0.0173 | 7/9 | 8/9 | 0.1663 / 0.2541 |
| S2 | 57 | 3.6 | m_s | 0.0569 | 0.809 | 0.0742 | 9/10 | 10/11 | 0.3047 / 0.1713 |
| S2 | 57 | 3.6 | C̄_zz | 0.0567 | 0.814 | 0.0749 | 8/9 | 9/10 | 0.1611 / 0.2531 |
| S2 | 57 | 4.5 | m_s | 0.0580 | 0.446 | 0.3190 | 10/11 | 9/12 | 0.3273 / 0.2058 |
| S2 | 57 | 4.5 | C̄_zz | 0.0578 | 0.465 | 0.3391 | 9/10 | 10/11 | 0.1755 / 0.2689 |
| S2 | 57 | 5.0 | m_s | 0.0584 | 0.325 | 0.4354 | 9/10 | 10/12 | 0.3234 / 0.2089 |
| S2 | 57 | 5.0 | C̄_zz | 0.0582 | 0.343 | 0.5233 | 10/11 | 10/11 | 0.1890 / 0.2648 |
| S2 | 57 | 5.5 | m_s | 0.0587 | 0.267 | 0.5547 | 8/9 | 9/12 | 0.3558 / 0.2312 |
| S2 | 57 | 5.5 | C̄_zz | 0.0585 | 0.283 | 0.7263 | 11/12 | 10/11 | 0.2069 / 0.2901 |
| S3 | 115 | 4.0 | m_s | 0.0577 | 0.486 | 0.4853 | 9/10 | 10/12 | 0.2728 / 0.1737 |
| S3 | 115 | 4.0 | C̄_zz | 0.0574 | 0.516 | 0.4778 | 9/10 | 10/11 | 0.1542 / 0.2156 |
| S3 | 115 | 6.0 | m_s | 0.0589 | 0.144 | 1.4429 | 8/9 | 8/12 | 0.2634 / 0.2013 |
| S3 | 115 | 6.0 | C̄_zz | 0.0588 | 0.159 | 2.0227 | 9/10 | 9/10 | 0.1628 / 0.2055 |

S1 = n = 57 at Jz = 4.0, 6.0 (confirmation); S2 = every other Jz the map certifies at n = 57; S3 = n = 115 at 4.0, 6.0.
The Jz = 3.4 rows are already within 5 % of τ with the DMRG reference (their v1 requirement is 0.015-0.017 J), so a
certified width ≤ τ there is unlikely; they are kept as declared.

## 3. What is computed (`code/run_v2.py`, VM)

- **Stage A, level vball2** (radius-2 vertex balls, v1 settings), on the grid, by an exact **branch-and-bound** per side:
  points in increasing u_lb; one job per side at a time; a side stops when the next point has
  u_lb ≥ (best certified u of that side) − 0.01 τ. So each side's certified bound is within 0.01 τ of the best over the
  whole grid, and the row width within 0.02 τ (the CERTIFIED/not decision can change only if a row ends within 0.02 τ
  of τ; this is reported).
- Verified v1 certificates at grid points (v1 decisive and exploratory points, both levels; read-only from the v1
  sandbox) enter the bound and the branch-and-bound from the start.
- **Stage B, level eball2** (v1 settings), rule fixed here: when both sides of a row are finished and its certified
  width is > 0.85 τ, eball2 at the best vball2 point of each side (unless an eball2 certificate exists there). Caps: S1 8,
  S2 8, S3 4 jobs; S3 only if < 2.5 h have elapsed since the scheduler started.
- **Gate (n = 19):** vball2 at the 24 S1 refinement points (same Jz, σ, λ) with exact sector diagonalization.
- Priority: S1 stage A, S1 stage B, n = 19 gate, S2 A, S2 B, S3 A, S3 B. 8 jobs in parallel (one thread each).
- Every bound is optimized by `lb_opt.py` and verified in a separate process by `verify_exact.py` (exact integers); only
  verified bounds count.

## 4. Decision (`code/analyze_v2.py`, laptop)

- **Certified width** of a row: w_cert = Σ_σ min over every verified certificate (v1 or v2, any level) at a grid point of
  u = (E_up − E_LB)/(λS). Rigorous interval: [−u_−, u_+]. CERTIFIED iff w_cert ≤ τ.
- **ρ_row = (w_cert − w_F)/(τ − w_F)**, w_F = the DMRG-referenced width over the grid's chain points (no δG). ρ ≤ 1 ⟺
  certified; ρ is the v1 ratio "slack over requirement" generalized to a grid (it equals v1's ρ when both sides use
  the same points).
- **Same thresholds as v1, per scope:** ACCEPT if ρ_max ≤ 1, REJECT if ρ_max ≥ 3, GRAY otherwise. S1 also includes v1's
  verified ρ_H for H(4.0) and H(6.0) (0.025, 0.002). S2 and S3 get their own verdicts (and the number of certified rows).
- **Gate:** at least 12 of the 24 n = 19 gate jobs verified, and every verified n = 19 v2 bound ≤ exact E₀ + 1e-9 J;
  else NO DECISION. A row with a side that has no verified
  certificate is INCOMPLETE; a scope with an incomplete row is INCOMPLETE unless decided by the present rows (REJECT if
  some present ρ ≥ 3).
- Prior (judgment): S1 ACCEPT ≈ 0.9; S2 ACCEPT ≈ 0.2 (the 3.4 rows), S2 rows certified except 3.4 ≈ 0.7; S3 ACCEPT ≈ 0.6.

## 5. Cloud and cost

- **VM lock (binding):** before starting, create `full_runs/LOCK_cj-runner-1b.txt` atomically (`set -o noclobber`);
  proceed only if that succeeds AND cj-runner-1b is TERMINATED; if the lock exists, wait with background polling. Delete
  the lock only after `down` has shown TERMINATED (`code/vm/vm_rigor.sh up/down`).
- Same cloud procedure as v1: `--configuration=sqd-research` only; only **cj-runner-1b**; never cj-runner-2 (the huang
  agent's) or cj-runner-1; `cj-poweroff=off` before start, max-run-duration 5 h STOP; runner stopped after boot, no
  `heavy_run.py`; work only under `/mnt/cj/sandbox/rigor_<stamp>/` and `rigor_tools/` (the v1 sandbox read only);
  never touch `/mnt/cj/mirror`, `prereg/runs`, the queue, the ledgers, `/mnt/cj/venv`; at the end `cj-poweroff=on`,
  stop, clear max-run-duration, `instances list` TERMINATED.
- **Cap 5 VM-hours.** Expected 1.5-2.5 VM-h (mock schedule: ≈ 65 stage-A jobs, 24 gate jobs, a few stage-B jobs; n = 57
  vball2 ≈ 3-4 min per job, eball2 ≈ 35 min, n = 115 measured and reported). Stop rule: the scheduler stops launching
  4.0 h after the VM start; at 4.3 h the STOP flag is set and my remaining jobs are stopped; shutdown by 4.6 h.

## 6. Reporting

`RESULTS_v2.md`: 8-line summary in simple Spanish, then English: per row the certified interval, w_cert/τ, ρ, the
winning λ and its slack; the three verdicts; the n = 19 gate; the n = 115 cost and scaling; VM time and final state;
re-executed / only compared / not checked; the updated paper text (§6 of `RESULTS.md`, rewritten in `RESULTS_v2.md`).

## 7. Manifest at hash time (SHA-256)

```
e7a897a7b2ee452d0d60af7cb774c8416ac5a059e2a59ab343f07cf96a3be9e2  code/analyze.py
702bb5b20a7afacd3ce41f944d868db3c93a699c4f73d0f11280f7234b9e483a  code/analyze_explore.py
6401f6891e1c7999c52f86cb44cfc6a38ac5c85af3639f47392c08e9af3d4eeb  code/analyze_v2.py
f841cbd5eb1b289f660b59f4a92858f2fcea9d2fc745b968e5ea42d13f0003cf  code/ed_sector.py
25cdf279c213aa1274a1a3f3efc5056984290cbb71122ea980ab7746c8165353  code/lb_opt.py
160e434ab1f57bc364794649519098bf6094700388f7e9cf498ccbe243e3c65c  code/lbcore.py
e208d9859b58b7e4e47ead545cb456e132829ef215c97a6c94d97dc0dcbd6ed0  code/make_plan.py
8f76ff927a6bfd992f0770e807ea77ea858ba5c8622ca9549f325ab7d51a9ced  code/make_plan_v2.py
d15978c760961c68774e3c642efe8d82755929286784a1c49815aba3500c746f  code/requirement.py
004d4fa42d1709aeb5f6f0b77114afcd2ee5f1f6f24ebb7e54ff5923380c9694  code/run_all.py
d511e6314c0924a8e79bd9f0ae27068335197cf6a895c1804570ed2c939943e7  code/run_v2.py
dfee00b9c7abb6dde007a36d3402e932165f86f83c7eb7c36acea1141043ca9c  code/verify_exact.py
28a30a4053b916a740802bf95d42745652f773617e5b88e6cd9e4ecf992d7bfc  code/tests/test_toy.py
e47259d23fbbb3b70995c58910fee2fa79f80893ca981e915080f67ec3a312ec  code/vm/rigor_vm.sh
e3f7fdd17c7a6e571475dc4df0b9772ead7252933d099f5ac8bde316f58f5a65  code/vm/vm_rigor.sh
d8d42f5f54e33699562ba4584ca06925074d206ee8c6baddf73b9ab8c76aace1  code/graphs/hh_d3.json
80790817cc70ed56396799df3ca7205cfe62519477fda50e6e13311b1d528712  code/graphs/hh_d5.json
b5b630097e895a46a6d4072171fec3e5552ec0ea8f6e7b41e9106c9be6e7c8d7  code/graphs/hh_d7.json
beb9a35fcf81510666f11ce158e3da0bc44968e570b1bcd8090effb860a13a0d  outputs/grid_v2.json
d05fcf6ea66c33428d294bcaa8c360290b99ab91bb77b9f88dd42ef276cdfc01  outputs/plan_v2_A.json
dbd3c45639ace935e3dd70503f914cb50eb4450083624d90e42487a3da557fb2  outputs/requirement.json
8890220651e7dedd57329252b48723fe3db31170484ddd412a5c847bab502947  outputs/results.json
```
