# Huang benchmark: DEVIATIONS from DECLARATION.md (053ceac8…, hashed 2026-10-31T08:03:58Z)

Dated entries (UTC). None may change a rule, threshold or decision of the declaration silently; each says what changed
and whether any number is affected.

1. **2026-10-31T08:09Z, operational.** The laptop side of the `run` SSH call did not return after the scheduler had
   started detached (`setsid nohup`); the laptop process was stopped at 08:13Z. The scheduler kept running (status at
   08:13Z: 3 tasks running, the first 7 finished with rc = 0). Same event as the map's deviation 1. No effect.
2. **2026-10-31T08:55Z, checkpoint (declared rule, no drop).** 0.83 VM-h since boot, 27 tasks finished. `project_h.py`
   with the measured mean task times (which already include the 4-process contention, so efficiency 1.0): 3.04 VM-h in
   total; with the script's default efficiency 0.65 it would be 4.2 VM-h. Both are below 5.3 VM-h: nothing dropped.
   Placeholders still used for edpairs (420 s per batch) and chk/cold (900/600 s). Files: `logs_laptop/checkpoint/`.
3. **2026-10-31T08:20Z, laptop only.** `code/post_laptop.sh` (runs analyze_h.py and plot_h.py on the fetched outputs,
   hashes the laptop outputs) was written after the hash; not used on the VM; changes no rule or number.
4. **2026-10-31T09:05Z, analysis (laptop), post-hoc sensitivity.** The DMRG references show δχ = |E₀(256) − E₀(384)|
   = 3.3e-4 (n = 30) and 9.5e-4 / 2.0e-3 (n = 45), and E₀(384) lies 6.1e-5 (n = 30) and 1.6e-4 ((9, 1)) **above** the
   dataset's own energy 2·E_file: at n = 45 the χ = 256 chains carry an energy offset of order 1e-3 against local
   ε_τ ≈ 0.015 (the declared gate P1 will flag these rows). `analyze_h.py` now also reports, for every DMRG chain, ε_τ
   and law/computed with the chain referenced to the χ_c = 256 ground state (same truncation as the chain states;
   field `same_chi_ref`). This is a sensitivity bracket, not a declared quantity: every declared number (E₀ := χ = 384)
   is reported unchanged and decides the claims.
5. **2026-10-31T09:28Z, operational (coordinator's new VM rule).** Lock file `full_runs/LOCK_cj-runner-2.txt` created
   atomically (noclobber) while cj-runner-2 was in use by this run; it is deleted only after `down` shows TERMINATED.
   No other change; cj-runner-1b (locked by another agent) never touched.
6. **2026-10-31T10:33Z, second checkpoint (declared rule, no drop).** 2.47 VM-h since boot; 64 tasks finished, all
   rc = 0; only priority-4 pair batches left. Projection 3.13 VM-h (measured times: edpairs 528 s, n = 45 lab 1609 s,
   chk 282 s, cold 270 s). Below 5.3 VM-h: nothing dropped.
7. **2026-10-31T10:45Z, laptop only.** `code/plot_h.py` edited after the hash (empty-panel guards; panel (c) now draws
   the DMRG band [δe\*_out, δe\*_in] as a bar). Figure only; no number changes. Two partial read-only snapshots of
   `out/` (09:12Z, 10:35Z) were copied to the laptop to develop the analysis and figure (`partial_*`; superseded by the
   final fetch and deleted after it).
8. **2026-10-31T11:45Z, analysis (laptop), post-hoc diagnostic.** Gates P1 (all n = 30, 45 instances) and P2 (Ccent at
   (9, 1)) failed: the χ = 256 chains carry an energy offset ≈ δχ (9.5e-4 / 2.0e-3 at n = 45), so the λ₀ = 0.1 points
   of the local ladders sit at ε ≈ 1.1-2.3e-3 instead of χλ₀²/2 ≈ 1-3e-4. `code/posthoc_chi2.py` recomputes the rule's
   δe\* with χ from the second chain point of each side (λ ≈ 0.24-0.81) for every local chain; output
   `laptop_analysis/posthoc_chi2.json`. Not a declared quantity; the declared numbers and claim outcomes are reported
   first and unchanged.
9. **2026-10-31T11:34Z, operational.** VM down at 11:34:05Z (3.48 VM-h); lock removed at 11:34:55Z after TERMINATED
   was shown. G4 ran after the VM-side `summary`, so the VM summary has G4 = null; the laptop analysis (the reported
   one) includes G4.
