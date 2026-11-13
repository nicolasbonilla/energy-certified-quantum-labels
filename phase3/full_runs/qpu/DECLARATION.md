# Own device data of the SKQD-type method class at n = 57 on an IBM heavy-hex processor (DECLARATION)

Written 2026-10-31, before any QPU submission and before any device data exist. Hashed with SHA-256 into
`DECLARATION.sha256` (time in `DECLARATION_hash_time.txt`) before the first submission. After the hash this file does
not change; deviations go, dated, into `DEVIATIONS.md`. Basis: the brief of 2026-10-31, the coordinator's decision of
the same day (option (a): routed embedding, ibm_kingston with ibm_fez as fallback, inclusion rule of §6), the
feasibility record `FEASIBILITY_20261031.md`, `full_runs/method/` (emulation, references) and `full_runs/map/`.
Everything below is a property of the method class and of **our** device data; nothing here is, or will be written
as, a statement about the data or the circuits of arXiv:2606.15983.

**Run before this hash (and nothing else):** read-only account and backend queries (plan, usage window,
configurations, calibrations, coupling maps); embedding searches and local transpilation with those calibrations;
the 7 local-simulator unit tests of `code/tests/test_bitorder.py` (three times; 7/7 in runs 2 and 3); a 2-step timing
run of the noiseless MPS control at n = 57 (no label computed from it); a laptop dry run of `code/qpu_post.py` on
synthetic configurations (30,000 random flips of the Néel string; a 1-step χ = 32 control), only to exercise the code
path; the copy of the references into `refs/` (SHA-256 equal to the method run's `OUT_SHA256SUMS.txt`). No QPU job,
no VM.

## 0. Questions

1. On our own device data of the raw SKQD stage (Krylov sampling on hardware, random-flip recovery, subspace
   diagonalization; no basis optimization), does the method class over-order the labels at Jz = 1.2 (out of the
   training range) as the emulation predicts (Δm_s = +0.253 noiseless, +0.323 with device-like noise, at 10⁶ shots)?
2. How large is the effect of the real device noise, measured against a noiseless control of the identical circuits
   with identical post-processing?
3. Where do our device points sit on the certification map, and inside the "+" witness window?

## 1. Model, references, conventions

- H = ¼Σ_edges(XX + YY + Jz ZZ) on rustworkx `heavy_hex_graph(5)` (n = 57, 64 edges; `code/graphs/hh_d5.json`,
  byte-identical to method/ and map/, asserted equal to rustworkx's graph on the laptop), sector 33↑/24↓.
- References (hash-verified copies from `method/out_20261030T003230Z/out/`): DMRG χ = 200 ground states
  `ref_n57_J{1.2,1.6,4.0}.json` (E₀ = −27.86347, −32.53317, −66.99581 J; m_s = 0.64040, 0.77026, 0.95855) and our
  S^z − 1 gaps (0.16195, 0.48147, 1.88738 J). Emulation predictions (only compared): `emu_n57_J*.json`.
- **Bit order and layout:** conventions C1-C7 in the header of `code/qpu_lib.py` and the routed layout of
  `code/qpu_route.py`. Site i = node i = virtual qubit i = clbit i; |0⟩ = up, measured 1 = down; Qiskit little-endian
  (integer bit i = clbit i) = the configuration convention of method/code/emu2.py; Néel = minority colour (η = −1)
  down; L[i] = physical home of site i; ancilla virtual qubits 57.. are routing-only and never measured; decoding of
  SamplerV2 BitArrays by `decode_bitarray` (big-endian bytes, last byte = clbits 0-7).

## 2. The deviation from a native embedding (a property of OUR run)

`heavy_hex_graph(5)` contains four 10-cycles; the heavy-hex coupling graphs of ibm_kingston, ibm_fez and
ibm_marrakesh have girth 12, so the graph cannot be embedded natively on them. Our run embeds the 53-node core
natively and routes the 4 boundary sites (25, 30, 31, 36): their non-adjacent edges are applied after moving the
site's state into free |0⟩ qubits (move = CX·CX) and back. **Consequence, stated plainly: our device circuits have
about 17 % more two-qubit gates and about 55 % more two-qubit depth than a native embedding of the same Trotter
circuit** (today on ibm_kingston: 2240 CZ and CZ depth 141 at k = 10, against 3 CZ × 64 edges × 10 steps = 1920 and
9 layers × 10 + 1 = 91). This is why the noiseless control of the identical circuits (§5) is mandatory and is a
condition of the inclusion rule. The routed circuit is the same logical circuit: verified exactly at d = 3 (test
T5) and at n = 57, k = 1 on the chosen layout before submission (§4).

## 3. Circuits, backend, layout, primitive

- Krylov circuit k (k = 1..10) = Néel preparation + k first-order Trotter steps of size Δt (2606.15983 Supp.
  Table 1 as in method/code/fr.py: Jz 1.2: 0.0569; 1.6: 0.0622; 4.0: 0.0602); per step the colour classes 0, 1, 2 of
  `emu.edge_colouring`; edge gate RXX(Δt/2)·RYY(Δt/2)·RZZ(Jz Δt/2) = exp(−iΔt/4 (XX + YY + Jz ZZ)) + measurement of
  the 57 homes. Built by `qpu_route.routed_krylov_circuit`.
- **Check circuits** (in every job): `neel` = the k = 0 Krylov circuit (Néel product state); `asym` = X on sites
  {0, 1, 2, 3, 9, 14, 25, 30, 37, 44, 50, 56} (both colours, two routed boundary sites, not invariant under any
  automorphism of the graph nor under i → 56 − i). Neither enters the subspace.
- **Backend:** ibm_kingston; ibm_fez only if kingston is not operational or the layout rule finds no layout on it at
  preparation time. Job B uses the backend of job A.
- **Layout rule** (`qpu_route.choose_routed_layout`, with the calibration current at preparation, saved in full):
  over all native embeddings of the core and all homes / move paths (≤ 3 moves) of the boundary sites, minimise the
  expected two-qubit error per Trotter step (3ε per edge gate, 2ε per move, out and back); every used qubit with
  readout error ≤ 0.05 and every used pair with CZ error ≤ 0.05, relaxed ×2 then ×4 if nothing qualifies (recorded);
  ties by fewer moves, then mean readout error. Re-applied with the current calibration when job B is prepared.
- **Transpilation:** local, optimization level 3, seed_transpiler 20261031, initial_layout = homes + ancillas. Every
  ISA circuit must pass `check_isa` (checks) / `check_isa_routed` (Krylov): initial = final layout, no SWAP, two-qubit
  gates only on the declared native and routing pairs, clbit c read from home L[c]; otherwise no submission.
- **Primitive:** SamplerV2 in job mode on the ISA circuits; dynamical decoupling on (default sequence); gate twirling
  on (num_randomizations and shots_per_randomization "auto"); measurement twirling off; default rep_delay
  (250 µs) and init_qubits; no job tags; max_execution_time per job as in §4. No other mitigation.

## 4. Jobs, shots, QPU cap

- **Job A (decisive, one job, shared calibration):** `neel` and `asym`, 10⁴ shots each; Jz = 1.2, k = 1..10,
  **10⁵ shots each** (the published budget). max_execution_time = 380 s.
- **Job B (after A, only if the time allows):** `neel` and `asym`, 10⁴ shots each; Jz = 1.6 then Jz = 4.0, k = 1..10,
  S_B shots each, S_B = 1000 · floor((480 − U_A − 10 − 2·10⁴·u) / (20 · u) / 1000), u = U_A / 1.02·10⁶ (U_A = job A's
  quantum seconds). If S_B < 10⁴: Jz = 4.0 is dropped and S_B is recomputed with 10 circuits; if still < 10⁴, job B
  is not submitted. max_execution_time = 480 − U_A − 10 s (integer, floor).
- **QPU cap of this run: 480 s** (80 % of the 600 s window; 0 s used at 08:46Z). **Immediately before each
  submission** the account is re-read: the instance must be plan "open" with pricing "free", and the remaining seconds
  must be ≥ the job's max_execution_time + 120 s (the 20 % margin is never touched); otherwise no submission and
  stop. After submission, if the runtime's usage estimate exceeds the job's max_execution_time, the queued job is
  cancelled (the only cancellation allowed; no job is deleted).
- **Pre-submission equivalence (job A and B):** the transpiled k = 1 ISA circuit of the first Jz, simulated with the
  local Aer MPS simulator (156 qubits), gives ⟨Z⟩ at the 57 homes equal to the noiseless MPS control within 1e-6;
  otherwise no submission.
- **Stored:** job ids at submission; the calibration snapshot (properties, target errors, configuration timing); the
  layout and routing; the ISA circuits (QPY) with SHA-256; per circuit the decoded uint64 configurations in shot order
  and their unique strings / counts (npz); result metadata; the job's usage and metrics. Nothing is re-submitted
  (one version), except that a job that ends in ERROR before running may be submitted once more with the same
  circuits (recorded).

## 5. Device checks, post-processing, noiseless control

- **Device bit-order checks:** a check passes if at each of the 57 sites the fraction of its 10⁴ shots equal to the
  expected bit is ≥ 0.9 and the majority vote equals the expected bit. **Both checks of a job must pass, or no
  Krylov data of that job are used** (they are stored and reported only as a failed run).
- **Post-processing (identical to the method emulation; code path of method/code/fr.py `subspace(p < 0,
  recovery=True)` → `rr` → `evaluate`, with `emu2` byte-identical):** per Jz, the shots of k = 1..10 → unique →
  random-flip recovery (`emu2.recover`, seed = fr-style SHA-256 seed of ("qpu", "recover", n, Jz, variant)) →
  `emu2.CSet` → `emu2.SubH` → `emu2.ground` (Lanczos, tol 1e-10, Néel start) → `emu2.diag_labels`,
  `emu2.label_errors` against the references; E, ratio r = (E − E₀)/gap. Variants: `rec` (primary) and `ps`
  (post-selection of in-sector strings). Recorded: shots, unique strings, unique in-sector strings, D, nnz.
- **Noiseless control of the identical circuits:** `qpu_lib.TrotterMPS` (the same logical gate list, χ ≤ 256,
  svd_min 1e-12 relative, discarded weight recorded and flagged if > 1e-6), sampled after each step with
  `emu2.sample_mps` at the same shots per circuit as the device (seed ("qpu", "control", Jz, k)), then the same
  post-processing (`rec`, `ps`). Computed on the VM for every Jz that has device data from a job whose checks pass.
- **Cloud:** only a VM that no other agent uses: cj-runner-2 (lane vm2) only after `full_runs/huang/RESULTS.md`
  exists and it is TERMINATED; cj-runner-1b (lane vm) only after `full_runs/rigor/RESULTS.md` exists and it is
  TERMINATED; wait with background polling. gcloud only with --configuration=sqd-research, zone europe-west3-b;
  procedure of `pilot_witness/code/vm/` (cj-poweroff=off before start, max-run-duration with STOP, stop the sealed
  runner after boot, work only under `/mnt/cj/sandbox/qpu_<stamp>/`, venv read-only; at the end cj-poweroff=on,
  stop, clear max-run-duration and termination action, show TERMINATED). **Cap 6 VM-hours.**

## 6. Decisive quantities and the inclusion rule

- **D1 (Jz = 1.2):** Q = Δm_s(device, `rec`) − 0 = m_s(device labels) − 0.64040; per-site signed excess
  sign(Z_ref,i)(Z_i − Z_ref,i) for the 57 sites; fraction of sites over-ordered. Reading: **PRESENT** if Q ≥ +0.10 and
  ≥ 90 % of sites over-ordered; **NULL** if |Q| < 0.03; **REVERSED** if Q ≤ −0.10; **WEAK** otherwise. (The 0.10 line
  is 2.5× / 3.2× below the noiseless / device-like predictions.)
- **D2:** energy ratio r(device) at each Jz; ε = E − E₀ in J.
- **D3:** Δm_s(device) − Δm_s(control) at each Jz, with r(device) / r(control).
- **D4 (recorded):** map placement: ε(device) against the map's ε_τ (outer, DMRG-referenced; inner, rigorous) for m_s
  and C̄_zz at that Jz (`map/laptop_analysis/summary_map.json`): certified at our energy if ε ≤ ε_τ,in, not certified
  if ε > ε_τ,out, gray otherwise. Window position f₊ = Δm_s / (m_s⁺(ε) − m_s,GS), m_s⁺ = upper concave envelope of
  the map's m_s "+" chain with the ground state; if ε is beyond the chain, f₊ is reported as an upper bound.
- **Recorded, not gating:** unique in-sector strings per 10⁶ shots vs IBM's 81,862; r at 1.6 / 4.0 vs IBM's raw
  (pre-basis-optimization) 6.89 / 0.367 and the emulation's device-like 7.44 / 0.400; comparison with the method's
  `ideal` and `dev_rec` emulations at equal Jz.
- **Inclusion rule. Main text only if all of:** (i) both bit-order checks of job A pass; (ii) the noiseless control
  of the identical circuits is computed at Jz = 1.2; (iii) the device energy ratio at Jz = 1.2 is within 3× of the
  value the method emulation predicts with IBM-like noise (`dev_rec`, r = 31.307), i.e. r ∈ [10.44, 93.92].
  **Otherwise supplementary material only.** If (i) fails, nothing of job A is used. Job B's points follow the same
  rule with their own checks and are reported with job A's verdict. Verbs: "on hardware" only for numbers from these
  jobs; the routed embedding and its gate overhead (§2) are named wherever the device data appear.
- **Learning test:** not performed (at most two in-distribution device points, 1.6 and 4.0: too few for a
  same-method learning test); stated as such.

## 7. Files

`code/qpu_lib.py`, `code/qpu_route.py`, `code/submit_job.py` (preparation, submission, fetch), `code/qpu_post.py`
(VM: control and post-processing), `code/tests/test_bitorder.py`, `code/method_copy/` (emu.py, emu2.py identical to
method/), `code/graphs/`, `code/vm/` (laptop and VM scripts). SHA-256 of all code at the hash:
`CODE_SHA256_at_hash.txt`. The laptop analysis (`code/analyze.py`, map placement and window position) may be written
after the hash; it implements §6 as written.
