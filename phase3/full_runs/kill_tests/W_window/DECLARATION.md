# Kill test W: fraction of the energy window used by each method (DECLARATION)

Written 2026-11-07 (UTC), before cj-runner-1b is started and before any state of the 4x6 lattice has been computed anywhere. Candidate W of `phase3/design/R8_alternatives.md`. Hashed with SHA-256 into `DECLARATION.sha256` (UTC time on its second line). Later changes go in `DEVIATIONS.md`, dated; code fixes that change no rule are logged in `out/patches.txt` with hashes.

## 1. Status before computing

- Step 0 (`FORMULA.md`, `STEP0.md`): the parameter-free envelope u(δe) = 3 (c/12π)^(2/3) (m0/ρs) δe^(1/3) survives the published iPEPS data of arXiv 2009.02313 (r = 0.52-0.56 for D = 3..6, threshold 1.2). Step 1 therefore runs.
- Known before starting, disclosed: the published 4x4 ground energy (-11.2284832084); the closed forms in section 8; nothing about any 4x6 state, ViT, DMRG or Krylov result of this test. On the laptop only text work, web reading, hashing and gcloud. No physics is computed on the laptop and none will be.

## 2. Question

On a lattice where the exact window is computable, does a small ViT neural quantum state use a much smaller fraction of the energy window of the order parameter than an MPS at the same energy error? Hypothesis to kill: r_ViT / r_MPS ≤ 0.5 over δe ∈ [1e-3, 1e-2].

## 3. System and observables

- **Lattice:** 4x6 square torus, LX = 6, LY = 4, periodic in both directions, n = 24; site index i = x*4 + y; ε_i = (-1)^(x+y).
- **Why 4x6:** it is the largest torus on which (i) the full S^z = 0 sector (2 704 156 states) allows exact Lanczos at every point of the window chain within budget and (ii) every ViT and MPS state can be written as a full vector and evaluated exactly. Both lengths are even, so the Néel pattern and columnar dimers along x and y fit, and (π,π), (π,0), (0,π) are allowed momenta. 4x4 is too small (16 sites, used only for gates); 6x6 (S^z = 0 dimension 9.1e9) is out of reach. The aspect ratio 1.5 removes the 90-degree rotation; this is stated, not corrected.
- **Hamiltonian:** H = Σ_<ij> S_i·S_j + J2 Σ_<<ij>> S_i·S_j, J2 = 0 (primary) and J2 = 0.5 (secondary), spin-1/2 operators.
- **O_ms** = (1/n²) ⟨M_s·M_s⟩, M_s = Σ ε_i S_i (all three components; computed as (M_s^z)² plus ½(‖M_s^- ψ‖² + ‖M_s^+ ψ‖²) through the S^z = ∓1 sectors).
- **O_dim** (J2 = 0.5 only) = (1/n²) (⟨B_x²⟩ + ⟨B_y²⟩), B_a = Σ_r (-1)^(r_a) S_r·S_(r+a) (columnar dimer structure factor).
- Energy per site e = ⟨H⟩/n, δe = e - e0(24), e0(24) the exact ground energy per site of this lattice at this J2.
- All operators are sparse matrices in the S^z = 0 sector built by `code/wlib.py`; every method's state is evaluated by the same `Ops.evaluate` on its full normalised vector (energy, O_ms, O_dim, ⟨S²⟩, translation and spin-flip overlaps, energy variance).

## 4. Exact envelope (`code/ed_env.py`)

- **Ground state:** Lanczos (ARPACK, tol 1e-14) in the full S^z = 0 sector, from a seeded random vector.
- **Chain:** for side σ = ±1 and λ = 10^(k/8), k = -24..16 (1e-3 to 100), the ground state of H - σ λ n O, warm-started from the previous λ plus 1e-3 of a seeded random vector, tol 1e-12; stop after a point with δe > 1.0 or when O has changed by < 1e-7 three times in a row. Chains: (J2 = 0, ms, ±), (0.5, ms, ±), (0.5, dim, ±).
- **Symmetry sectors.** H and both O are SU(2) scalars and commute with all lattice translations and the spin flip, so every eigenvector of H - σλnO has a member in S^z = 0; working in the full S^z = 0 sector (no spatial reduction) lets the chain follow level crossings between momentum sectors. Each extremal state's translation and spin-flip overlaps and ⟨S²⟩ are recorded, so the sector it lies in is reported.
- **Envelope (duality, exact for density matrices).** Inner width w_in^σ(δe): the upper concave (σ = +) or lower convex (σ = -) hull of the chain points (δe_k, O_k) including (0, O_GS), linear between points (attained by mixtures), constant beyond the last point. Outer width w_out^σ(δe) = min_k [e0 + δe - g_k]/λ_k - σ O_GS (Lemma A). Primary: w_in. Checks: weak duality at every chain point (violation ≤ 1e-9), random-restart ground energies at λ = 0.1, 1, 10 (|Δg| ≤ 1e-9 per site), residuals; w_out/w_in at the five test points reported.
- **Exponent (report, no rule):** least-squares slope of ln w_in^+ against ln δe on the hull points in [1e-6,1e-5], ..., [1e-2,1e-1], and local slopes, at J2 = 0 for O_ms, against 1/3. Said now: the finite-size tower of states and singlet gap make the window quadratic (exponent 1/2) at small enough δe; any approach to 1/3 can only be seen at intermediate δe.

## 5. Methods (all start in the S^z = 0 sector)

**(a) MPS, two-site DMRG** (`code/dmrg_w.py`, TeNPy 1.1.0): torus as a finite MPS (default order, x major), U(1) conserved, start from the Néel product state, fixed χ_max ∈ {2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 256}, mixer on (amplitude 1e-5, decay 1.2, off after 15 sweeps), 6-40 sweeps, max_E_err 1e-11. Each final MPS is contracted to the full vector. Gate per state: |E_DMRG/n - e_exact(vector)| ≤ 1e-9 and |1 - norm²| ≤ 1e-9, else the state is excluded and listed.

**(b) ViT** (`code/vit_w.py`, NetKet 3.21.0, JAX 0.8.1, CPU): 2x2 patches (6 tokens), linear embedding, `layers` pre-LayerNorm blocks of factored attention (attention weights depend only on the relative patch position, `heads` heads) plus a GELU MLP of width 2d, final LayerNorm, sum over tokens, a dense layer to (log|ψ|, phase), plus the Marshall phase π·#(up on sublattice A). Real parameters, float64. Sizes S (d = 8, 1 layer, 2 heads), M (16, 2, 2), L (32, 2, 4). VMC with SR: SGD lr 0.02, diag_shift 1e-2·0.995^t floored at 1e-4; 1024 samples, 16 chains, MetropolisExchange on the coupling graph, 16 discarded per chain; 2000 steps or 80 minutes of wall time per run, whichever comes first. Runs: J2 = 0: S, M, L; J2 = 0.5: M, L; seed 1 each. Checkpoints after 10, 25, 50, 100, 200, 400, 700, 1000, 1500, 2000 steps (and at the wall cap): full vector of all 2 704 156 amplitudes, exact evaluation. Every checkpoint is a ViT state ("several sizes and training lengths"). If the NetKet version does not accept `VMC(preconditioner=SR)`, `VMC_SR` with the same lr and diag_shift is used (recorded).

**(c) Krylov generator, reported without verdict** (`code/krylov_w.py`): ψ_k = exp(-iHkΔt)|Néel⟩, k = 1..10, Δt = π/(E_max - E_0) with E_max = Σ_bonds J_b/4 (ferromagnetic state, exact maximum), exact Taylor propagation; subspaces (i) top-K configurations of p(x) = (1/10)Σ_k |⟨x|ψ_k⟩|², K ∈ {1e2, 3e2, 1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6}, ties by basis order; (ii) union of exact multinomial samples, 1e3, 1e4, 1e5 shots per circuit; Rayleigh-Ritz, lowest Ritz vector evaluated exactly. No noise, no configuration recovery: an idealised version of the paper's generator.

## 6. The measure

For a state with (δe, O): err = O - O_GS; side σ = sign(err); r = |err| / w_in^σ(δe) (r_outer with w_out also reported). By construction 0 ≤ r ≤ 1 up to the hull resolution; any r_outer > 1 + 1e-9 is a bug and blocks the verdict until explained.
Per method (MPS: all gated χ; ViT: all checkpoints of all runs at that J2; Krylov: all subspaces), r(δe) is interpolated piecewise-linearly in log10 δe through the method's points sorted by δe (points with equal δe to 1e-9 in log10 averaged); no extrapolation outside the method's δe range. Secondary (no rule): median of r over the method's states within ±0.2 decades.

## 7. Kill rule (fixed now, from the brief) and its reading

- **Primary:** J2 = 0, O = O_ms. Five points δe_i = 10^(-3 + 0.25 i), i = 0..4 (1e-3, 1.78e-3, 3.16e-3, 5.62e-3, 1e-2). Ratio ρ_i = r_ViT(δe_i) / r_MPS(δe_i) (ρ = ∞ if r_MPS = 0 and r_ViT > 0).
- **DEAD if ρ_i > 0.5 at three or more of the five points.** SURVIVES if ρ_i ≤ 0.5 at three or more. Otherwise (points not evaluable because a method does not cover them): NO DECISION.
- **If no ViT state reaches δe ≤ 1e-2 within budget: NO DECISION**, reported as such, never as SURVIVES.
- J2 = 0.5 (O_ms and O_dim): same statistics, no verdict. Krylov: r reported, no verdict.
- Also reported: r tables per method and δe, the envelope itself, signs of the errors (which side each method errs on), w_out/w_in, the exponent of section 4.
- The analysis (`code/analyze_w.py`) runs on the VM; the laptop only reads `analysis.json`.

## 8. Gates (must pass before the numbers they guard count)

- G1 (`gates_w.py ed`): 4x4 Heisenberg ground energy -11.2284832084 within 1e-6.
- G2: Néel product state on 4x6 at both J2: e = -0.5 + 0.5 J2, O_ms = 1/4 + 1/(2n), O_dim = 1/(2n), ⟨S²⟩ = n/2 (to 1e-12).
- G3: O_ms by ladder operators equals the direct pair sum (1/n²) Σ_ij ε_i ε_j ⟨S_i·S_j⟩ on the 4x4 ground state (1e-12).
- G4: columnar singlet product on 4x4 (ground state of the even x-bonds): E = -6, O_dim = 45/256, O_ms = 24/256 (1e-10).
- G5: DMRG at χ = 16 on 4x6 at both J2 passes the per-state gate of 5(a).
- G6 (`gates_w.py netket`): for a random ViT on 4x4 at both J2, NetKet's full-sum energy equals wlib's exact evaluation (1e-10); samples stay in S^z = 0; 30 VMC steps lower the energy.
- G7 (`gates_w.py krylov`): Taylor propagator equals scipy `expm_multiply` on 4x4 (1e-10).
A failed gate is fixed and logged; unresolved, it means NO DECISION for what it guards.

## 9. Cost and budget

Estimate (one core per task; this machine gives about 5.5 core-hours per VM-hour): ED chains 6 × 25-40 min, two ground states, DMRG 4 tasks 10-40 min, ViT 5 runs ≤ 80 min each plus evaluations, Krylov 2 × 10 min, gates 10 min. About 3 VM-h of computing plus 0.5-1 h setup, install and transfers: **about 4 VM-h ≈ 2.4 EUR** (0.594 EUR/h list). Hard limits: **5 EUR; at 8 VM-h I stop and report what I have**; max-run-duration 8.5 h with STOP as a safety net. ViT runs are started first among the production tasks because they are the risk; if they are cut by the wall cap, their checkpoints so far are the ViT states.

## 10. Cloud procedure (binding)

`gcloud --configuration=sqd-research` on every command; only cj-runner-1b (europe-west3-b); never cj-runner-1; cj-runner-2 not touched; never ADC. Lock `phase3/full_runs/LOCK_cj-runner-1b.txt` by noclobber, stop if it exists. Start: cj-poweroff off, max-run-duration 8.5 h (30 600 s) with STOP, start, stop `cj-runner@vm`. Free space on /mnt/cj checked first (about 3.4 GB expected; venv about 1.2 GB, outputs a few MB, work vectors deleted at the end). Work only under `/mnt/cj/sandbox/W_<stamp>/` (scripts in `/mnt/cj/sandbox/W_tools/`).
**Packages, temporary outbound address (as in test M):** after the code upload, an ephemeral access config `w-temp-pip` is attached to nic0 only to install pinned wheels into `<sandbox>/venv` with `pip --only-binary :all:` (pip 24.3.1 from its wheel, SHA-256 checked): numpy 2.2.6, scipy 1.15.3, jax 0.8.1, jaxlib 0.8.1, flax 0.12.2, optax 0.2.6, netket 3.21.0, numba 0.62.1, physics-tenpy 1.1.0; transitive versions recorded in `out/pip_freeze.txt`. No scientific code and no import test runs while it is attached. It is removed with `delete-access-config` and its absence confirmed with `describe` before any computing, and again at the end; timestamps in `logs_laptop/ip.txt`. If attaching fails, I stop and report. If a pin cannot be installed, I may change only that pin while the address is attached, logged as a deviation. No firewall change, no new or deleted resource, no IBM, no contact with anyone, no `git add -A` or push, nothing under `paper/` edited, no anonymous paper of the author named.
End: cj-poweroff on, stop, clear the limit, remove the lock, confirm all VMs TERMINATED and no external address. Results fetched often.

## 11. Outputs

`FORMULA.md`, `STEP0.md`, this file and its hash, `DEVIATIONS.md` if needed, `code/`, `out_<stamp>/` (JSON from the VM, `analysis.json`), `SHA256SUMS.txt`, `RESULTS.md` (at most 8 plain lines in simple Spanish first, then the technical report). No novelty claims; a negative is not softened; what a hostile referee would say about a 24-site test is written down.

## 12. Code manifest at hash time

See `DECLARATION_manifest.sha256` (SHA-256 of every file under `code/`, written in the same minute as the hash of this file).
