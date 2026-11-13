# Deviations from DECLARATION.md (SHA-256 b9ac4df6…, hashed 2026-10-31T08:59:18Z)

1. **2026-10-31T09:10Z — code fix in the pre-submission equivalence test (before any submission; criterion
   unchanged).** The first `prepare A` (logs_laptop/prepare_A_try1_equivalence_bug.txt) stopped, as declared, because
   the equivalence test returned max |Δ⟨Z⟩| = 0.998. Diagnosis: Aer's matrix-product-state `save_expectation_value`
   with a one-qubit operator on a subset of the 156 qubits returned ≈ 0 at every home for this circuit (it returned
   the correct ±1 for the product-state check circuit). The ISA circuit itself is correct: Aer MPS sampling of it
   (4000 shots) agrees with the noiseless control within 1.8 σ at every site, all shots in the sector; with the
   operator written on all 156 qubits, Aer's exact ⟨Z⟩ equals the control to 3.0e-11. `equivalence()` in
   `code/submit_job.py` now uses the full-width operator. Nothing was submitted before this fix.

2. **2026-10-31T09:20Z — shots of job B (before job B was prepared or submitted; the 480 s cap and job B's cap of
   floor(480 − U_A − 10) = 185 s are unchanged).** Job A used U_A = 285 s (runtime estimate 484 s). Its execution
   spans: checks 7 s (2.0 × 10⁴ shots), Krylov 279 s (10⁶ shots, 10 pubs × 32 randomizations). The declared formula
   S_B = 1000·floor((480 − U_A − 10 − 2·10⁴u)/(20u)/1000) with u = U_A/1.02·10⁶ gives S_B = 32,000 and an expected
   usage of ≈ 185 s by the same per-shot rate, i.e. at the job's own cap. It also ignores the per-randomization
   overhead, which doubles in job B (20 Krylov pubs instead of 10). With that overhead the expected usage is
   ≈ 210 s, above the cap, and the whole job would be cancelled by the system at 185 s with no data. Used instead:
   T = shots·r0 + n_rand·o fitted on job A's Krylov span (r0 = rep_delay + mean ISA duration, o = overhead per
   randomization), and S_B = the largest multiple of 1000 with expected usage ≤ 0.9 × 185 s (never above the
   declared formula's value; still ≥ 10⁴, so Jz = 4.0 is kept). The values are in `jobs/B/prep.json` (`sb`).

3. **2026-10-31T09:27Z — VM rule replaced by the coordinator** (before any VM was started). DECLARATION §5's condition
   "huang/ or rigor/RESULTS.md exists AND the VM is TERMINATED" is replaced by: create
   `full_runs/LOCK_<vm>.txt` atomically (bash noclobber, content "qpu <time>"), proceed only if that succeeds AND the
   VM is TERMINATED, delete the lock only after `down` has shown TERMINATED (`code/vm/wait_lock_vm.sh`,
   `vm_qpu.sh up/unlock`). Everything else in §5 (procedure, sandbox, 6 VM-h cap) is unchanged.
