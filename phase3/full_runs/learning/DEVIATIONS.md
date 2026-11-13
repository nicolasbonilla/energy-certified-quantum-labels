# Learning run: DEVIATIONS (dated, after the declaration hash e905263a…, 2026-10-31T15:25:10Z)

1. **2026-10-31T15:31-15:34Z. Missing data files.** All 100 tier-A tasks of the D set failed within 10 s
   (`FileNotFoundError: …/data_huang20/heisenberg_4x5_id1_SvN.txt`): the file reader `lattice.load_instance` (an unchanged
   copy from `full_runs/huang/`) also reads the `_SvN` file (the dataset's entanglement entropy, not used here), which
   had not been copied. Fix, with **no code change**: the 100 `_SvN.txt` files of the same clone (commit 646a1cb2…) were
   added to `data_huang20/` (SHA-256 in `provenance/DATA20_SvN_SHA256_added_after_hash.txt`, identical to the clone),
   uploaded as one tar (SHA-256 6b5e783d…, `patches_20261031T152732Z/svn_files.tar`) and unpacked in the sandbox's
   `data_huang20/` (logged in the VM's `out/patches.txt`); the 100 `A_D_*.fail` markers were removed so that the running
   scheduler retried those tasks. No tier-B task had started. The O-set tasks were not affected. No declared rule,
   threshold or label changes.

2. **2026-10-31T15:29Z. The laptop SSH call of `run` did not return** (the detached scheduler kept the session open, as
   in `full_runs/huang/` deviation 1). The laptop process was stopped; the VM scheduler was unaffected.
3. **2026-10-31T15:48Z and 15:50Z. Checkpoint (declared rule §9):** projected total ≈ 4.3 VM-h < 6.5: no task dropped
   (`logs_laptop/checkpoint/checkpoint1.txt`).
4. **2026-10-31, after tier A finished (17:58Z): the agent was stopped by the usage limit before `fetch` and `down`.**
   The scheduler finished **all 280 declared tasks** (`scheduler exit: done=280 failed=0`, 20:15:27Z; the only failures in
   the log are the 100 early tier-A D attempts of deviation 1, all re-run successfully). The VM then ran idle until its
   7-h max-run-duration stopped it at 22:27:00Z: **7.01 VM-h instead of the ≈ 4.3 projected** (≈ 2.2 h idle). cj-poweroff
   stayed `off` and the max-run-duration stayed set until the second boot; the lock `full_runs/LOCK_cj-runner-1b.txt`
   was kept. **No task or output was lost.**
5. **2026-11-04T14:55:52Z-15:01:13Z. Second boot (0.09 VM-h), on the coordinator's instruction**, only to read the
   scheduler state, fetch (tar SHA-256 28092d7c…, 849 files, 0 failing their hash, copied to the bucket), read the sealed
   ledgers (identical to the first boot) and run `down` (cj-poweroff=on, max-run-duration cleared, TERMINATED; lock
   removed 15:01:59Z). For it `code/vm/vm_l.sh` was changed to take the max-run-duration from `MAXRUN` (50 min used)
   instead of the fixed 7 h: an operational change, no effect on any result. **Total: 7.10 VM-h (cap 8).**
6. **Scripts written after the hash** (they implement only the declared quantities; none existed at the hash):
   `code/report_l.py` (gates, label statistics, tables, verdicts; D7 computed, as declared, from the avg and nn
   groups pooled), `code/plot_learn.py` (figures), `code/post_laptop.sh`.
