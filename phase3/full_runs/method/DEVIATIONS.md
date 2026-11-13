# Full method runs: deviations from DECLARATION.md (SHA-256 c1fd71e1…, hashed 2026-10-30T00:20:14Z)

Dated entries, UTC. None of the entries below changes a rule, a threshold, a gate, a variant definition or a run in
the declaration unless it says so explicitly.

1. **Header time (2026-10-30).** The header says "written 00:20-00:40 UTC"; the text was written before 00:20 and hashed
   at 00:20:14Z (`DECLARATION_hash_time.txt`). Nothing was computed between writing and hashing.
2. **Code changes after the hash, before the VM run (00:20-00:32Z).** All in files the declaration lists; none changes
   a computation of the target model:
   - `fr.py`: TeNPy's end-of-run consistency check (`max_trunc_err`, default 1e-4 on the final sweep) raised to 1e-2,
     so that a DMRG run whose final truncation error exceeds 1e-4 is recorded (the per-sweep truncation errors are in
     every output) instead of aborting the task. Found by the 70-site toy dry run (χ = 32 there).
   - `fr.py`: the Krylov bond dimension became a named constant `KCHI` (128, as declared; 24 only in toy dry runs).
   - `code/vm/vm_fr.sh`, `code/vm/fr_vm.sh` written (procedure as declared); `ml2.py`, `figs.py` written (allowed by
     §8 of the declaration; no learning output had been read).
3. **Laptop dry run on the 70-site fragment (00:21-00:27Z).** The first attempt used the production Krylov bond
   dimension (128) on the laptop, which is not light work; I stopped it (only the processes it had started) after
   ≈ 6 minutes and re-ran it with χ = 24 (toy). Its only finding is item 2's truncation check.
4. **The `run` SSH call (00:35Z)** was cut by a local 120 s timeout because it stays attached (as in the pilots). The
   scheduler is detached (`setsid nohup`) and kept running (checked at 00:37Z).
5. **Declared checkpoint (02:07Z).** First n = 115 Krylov tasks ended at 02:05:56Z / 02:06:36Z; projected total
   ≈ 7.5-8 VM-h (< 11): no drops (`logs_laptop/checkpoint_20261030T0207Z.txt`). Actual: 7.51 VM-h.
6. **Sampling caps reached (declared behaviour, recorded here for visibility).** The ground-state scans ran slower
   than planned (≈ 1 ms per shot at n = 57, χ_s = 128; ≈ 7 ms at n = 115, χ_s = 160), so the declared wall caps stopped
   sampling at 5.1×10⁶ shots (n = 57, Jz 1.2; D = 3.16×10⁶), 1.01×10⁷ (n = 57, 1.6), 8×10⁵ (n = 115, 1.2), 10⁶
   (n = 115, 1.6) and 2.6×10⁶ (n = 115, 2.5). D3 is therefore flagged "D_max short", as the declaration prescribes.
7. **Krylov truncation flag (recorded, as declared).** n = 115 at Jz 4.0, 5.0, 6.0: max truncation error per step 2.0e-6,
   1.9e-6, 2.8e-6 (> 1e-6); all other Krylov runs ≤ 9.2e-7.
8. **Post-processing on the laptop only.** `summarize.py`, `ml2.py`, `figs.py` and `results_tables.py` ran on the
   laptop from the fetched, hash-verified outputs; the VM `post` step was not used (it would have run the slow first
   version of `ml2.py` on the VM). `ml2.py` was changed after the hash and before any learning output on this run's
   data was read (02:30-02:50Z): float32 arithmetic and per-site matrix products for the IBM-like networks, Adam
   written in place (same arithmetic), the IBM-like model evaluated in-sample at training points for the abstention
   table (leave-one-out kept for the cubic and the small MLP), and the ensemble-spread rule computed from the main
   IBM-like ensemble instead of a second fit. It was validated against pilot3's outputs: cubic 0.67 % / 41.33 % and
   small MLP 0.14 % / 40.58 % at Jz = 1.2, identical to pilot3's TABLES.md. `figs.py` and `results_tables.py` were
   edited after the outputs were read (layout and labels only).
9. **Partial fetches.** Two intermediate fetches (06:20Z and 07:42Z) were made to start the analysis; they were also
   copied by the fetch script to the bucket (`method_20261030T003230Z/fetch_*`). The final fetch (07:58Z, after the scheduler exit at 07:54Z) is the one
   reported; the local partial copies were deleted.
10. **cj-runner-1b** was RUNNING when we shut cj-runner-2 down (08:00Z): the certification-map agent's machine; it was
    never touched.
