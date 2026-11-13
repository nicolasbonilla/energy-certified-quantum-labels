# Certification map: DEVIATIONS from DECLARATION.md (a0817801…, hashed 2026-10-30T02:23:12Z)

Dated entries (UTC). None may change a rule, threshold or decision of the declaration silently; each says what changed
and whether any number is affected.

1. **2026-10-30T02:48Z, operational.** The laptop side of the `run` SSH call was closed by the remote side ("Remote side
   unexpectedly closed network connection") right after the scheduler had started detached (`setsid nohup`); the
   scheduler kept running (status at 02:51Z: 8 tasks running). Same event as pilot2's deviation 3. No effect.
2. **2026-10-30T03:05Z, laptop only.** `code/tables_map.py` (markdown tables from `summary_map.json`, arithmetic only)
   was written after the hash; it is not used on the VM and changes no rule or number.
3. **2026-10-30T04:24Z, checkpoint timing.** At the declared checkpoint (≈ 1.5 VM-h after the scheduler start; 2.0 VM-h
   since boot) 63 tasks had finished, all of them references (the scheduler runs every priority-1 reference before
   any lab task), so no lab time had been measured. `project.py` with its placeholder lab time (900 s at n = 57,
   ×2.4 at n = 115) gave 18.0 VM-h; an estimate from the measured χ = 160 sweep times of the references (6.3 s per
   sweep at n = 57, 16.5 s at n = 115, ≈ 14 points per lab task) gives ≈ 11 VM-h. Measured reference times: n = 115
   R1a 1514 s, R2 655 s, R3 585 s; n = 57 R1a 470 s, R3 215 s, R4 220 s. The projection-and-drop decision is taken
   again at ≈ 05:45Z with measured lab times, with the same rule (drop in the declared order only if the projection
   exceeds 13.5 VM-h). No task was skipped at 04:24Z.
4. **2026-10-30T05:52Z, drop order applied (declared rule, at the deferred checkpoint).** Measured lab times: the four
   finished n = 115 lab tasks (m_s and C̄_zz at Jz = 1.1, 1.2) took 3103-3473 s; every chain point there ran the full
   10-sweep cap at χ = 160 (≈ 170 s per point; 16-18 points per task). Projection with these times (small-Jz n = 115
   tasks ≈ 55 min, n = 57 ≈ 20 min; Jz ≥ 3 assumed ≈ 20 / 8 min): ≈ 95 job-hours remaining, 15.4-16 VM-h in total,
   above 13.5. Dropped, in the declared order: (1) priority 7 (n = 115 local rows at Jz = 5.0-6.0, 12 tasks),
   (2) priority 6 (n = 115 Z_loop rows, 13 tasks), (3) priority 5 (n = 115 C_zz(edge) and Z_boundary rows, 26
   tasks): 51 task ids appended to `skip.txt` (`logs_laptop/checkpoint/skip_0555.txt`). New projection ≈ 12.5 VM-h.
   Kept: every m_s, C̄_zz, C̄₂ row (both n), the n = 115 Z_bulk rows, all n = 57 local rows, gates, minimal χ, J*
   points. The projection is re-checked when Jz ≥ 3 lab times exist; the next item in the declared order is priority 4.
5. **2026-10-30T07:36Z, drop order continued (declared rule) with one exception.** At 5.2 VM-h, 24 n = 115 lab tasks
   had finished: Jz ≤ 2.5 2572-3604 s, Jz ≥ 3.0 1511-2582 s (m_s "−" chains at Jz = 4 cross a first-order level
   crossing near λ ≈ 0.22, where DMRG runs to the sweep cap). Projection: ≈ 73 job-hours remaining (n = 57 lab times
   extrapolated as 0.38 × n = 115, the measured χ = 160 sweep-time ratio), ≈ 15.2 VM-h in total. Dropped next, in the
   declared order: (4) priority 4 (n = 115 Z_bulk rows), (5) the minimal-χ point at n = 115, (6) the n = 115 J* extra
   points (3.2, 3.4: references, thresholds, m_s and C̄_zz): 23 task ids appended to `skip.txt`
   (`logs_laptop/checkpoint/skip_0740.txt`). **Exception:** `lab115_Z_bulk_4.0` is kept (0.7 job-hours) so that one
   n = 115 local row exists at the decisive Jz for the 1/n drift of local labels (C-E) and for the comparison with
   pilot2's n = 115, Jz = 4.0 Z_bulk row. New projection ≈ 13.5 VM-h; the hard stop at 14 VM-h (§5) protects the cap.
   Consequences: no n = 115 local rows except Z_bulk at 4.0; J* at n = 115 from the computed 3.0 / 3.3 / 3.6 points
   (the interpolation check is done at n = 57 only); minimal-χ witnesses at two points (n = 57, Jz = 1.6 and 4.0).
6. **2026-10-30T10:05Z, analysis (laptop and the final VM summary).** `analyze_map.py`: when the two-sided width
   stays below τ up to the largest computed energy (ε_τ beyond the chain, e.g. C̄_zz at n = 115, Jz = 6.0), the
   largest computed ε is used as a lower bound of ε_τ^out (`eps_tau_out_lb`, `f_out_lb`) in J* and in the C-A
   robustness fraction; before, such rows broke the Jz interpolation and the top training points counted as not
   certified. Conservative for certificates (a lower bound of ε_τ); no row status changes. `tables_map.py` prints
   "> f" for these rows. The VM copy is patched (hash-logged) before the final summary.
7. **2026-10-30T12:15-13:47Z, laptop network outage (operational).** The laptop lost network access (DNS failure); the
   12:15Z status poll returned nothing and no check was made until 13:47Z. The VM and its scheduler were not affected:
   at 13:48Z the full scheduler log shows 432 planned tasks, 74 skipped (deviations 4-5), 356 finished with rc = 0,
   2 running (`minchi57_1.6`, `minchi57_4.0`, started 13:20Z), none failed, none lost. The VM-side copy of
   `analyze_map.py` was then patched (deviation 6; hash-logged in `out/patches.txt`: old 8eb866e7…, new 128ea506…).
   Free disk on `/mnt/cj` reached 3.7 GB at 13:49Z (no pruning: the declared disk rule is evaluated at boot only).
8. **2026-10-30T14:20Z, operational script fix.** `code/vm/vm_map.sh getnpz` copied two remote files in one
   `gcloud compute scp` call, which PuTTY refuses; split into two calls (laptop script only; nothing on the VM
   changed). The `.npz` list must have LF line endings.
