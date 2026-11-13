# Deviations from DECLARATION.md (dated, UTC)

Declaration hashed 2026-11-07T18:13:55Z (`DECLARATION.sha256`), VM started 18:15:49Z. Code fixes that change no rule are also logged with hashes in `out/patches.txt` (VM) and copies in `patches_<stamp>/`.

## 1. Long gaps between laptop steps (procedure, cost)

Between consecutive laptop commands there were gaps of about 50 minutes that I did not control (VM up at 18:17Z, code upload at 19:06Z, address attached at 20:06Z). The VM was idle in those gaps, with no address and nothing running: about 1.8 VM-h (≈ 1.1 EUR) were spent before any computing started at 20:11Z. To protect the budget against further gaps, a laptop watchdog was added (item 3).

## 2. Temporary address and packages

Address `w-temp-pip` attached 20:06:25Z, deleted 20:08:36Z; absence confirmed by `describe` three times before any code ran (`logs_laptop/ip.txt`, `logs_laptop/ipoff.txt`). In that window only a network check, the pip wheel download (SHA-256 checked) and `pip install --only-binary :all:` ran. All nine pins installed as declared. Transitive packages (82 in `out/pip_freeze.txt`) include Google Cloud storage clients pulled in by `orbax-checkpoint` (a Flax dependency); nothing imports them and the VM has no outbound route.

## 3. 20:10Z. Laptop watchdog added after the hash (procedure only)

`code/vm/watch_W.sh` (not in the hashed manifest) polls the scheduler every 10 minutes, fetches results every 30 minutes, shuts the VM down when the analysis has run, leaves it up and returns control on a task failure, and at 01:45Z stops the scheduler, runs the analysis on what exists, fetches and shuts down. It decides no rule.

## 4. 20:11Z. `run` left the laptop ssh client attached (procedure only)

As in tests E and T, the ssh client stayed attached after the scheduler was started with `setsid nohup`; the local client was stopped at about 20:14Z. The scheduler was unaffected.

## 5. 20:15Z. DMRG gates G5 failed on a TeNPy default (code fix, rule unchanged)

TeNPy 1.1.0 raises `TenpyInconsistencyError` when the truncation error of a sweep exceeds its option `max_trunc_err` (default 0.01). At χ = 16 on this torus that happens by design (the declared ramp starts at χ = 2). `dmrg_w.py` now sets `max_trunc_err = 1.0` (never raise); no other option changed. Patch hash adce2963… (old a2aa3b9b…). Both gate tasks were reset and rerun; no DMRG state had been produced before the fix.

## 6. 20:22Z. Reference of the per-state DMRG gate changed (gate definition, before any MPS number was used)

The declared gate compared E_DMRG (the value returned by the engine) with the exact energy of the contracted vector. At χ = 2 they differed by 3.8e-3 per site, at χ = 16 by 3e-15. The engine's E is the energy of the last two-site update before truncation, not that of the final truncated MPS, so the declared comparison would have excluded valid small-χ states for a reason unrelated to what the gate is meant to catch (contraction or lattice mismatch). The gate now compares the MPO expectation value of the final MPS, ⟨ψ|H_MPO|ψ⟩, with the exact evaluation of the same state (tolerance unchanged, 1e-9 per site); E_DMRG is still recorded. Patch d98feb8b… (old adce2963…). The running task `dmrg_0_a` (χ = 2 and 3 done) was killed at 20:22:52Z and restarted from scratch; its pre-fix output and log were renamed `*_prepatch*` and are not used. No MPS result had been looked at beyond the gate line of χ = 2 and the gate task at χ = 16.

## 7. 21:11Z. Large bond dimensions run as parallel manual tasks (scheduling only, χ list unchanged)

The progress lines showed that DMRG on this torus converges slowly (the χ = 64 line printed δe ≈ 5e-3) and that its time grows roughly as χ³ (χ = 64: 162 s under full load), so the declared sequential tasks `dmrg_0_b` and `dmrg_5_b` (χ = 80..256 each) would not have ended before the deadline. They were skipped in the scheduler; the same χ values run as four manual tasks started by `code/vm/watch2_W.sh` once the five ViT runs have ended (to stay within memory): J2 = 0 χ = 256; J2 = 0 χ = 80..192; J2 = 0.5 χ = 256; J2 = 0.5 χ = 80..192. Same script, same options; outputs `dmrg_<J2>_m256.json`, `dmrg_<J2>_m80.json`. Scheduler slots lowered from 8 to 5 for the same reason. Because `analyze` depends on the skipped tasks, the scheduler will not run it; watch2 runs `analyze_w.py` by hand when the scheduler has exited and no DMRG process is left, then fetches and shuts the VM down (deadline 01:45Z as before). The decision was taken after seeing MPS energies up to χ = 64 and some ViT checkpoint energies in the progress lines, before any r value had been computed. No χ was added or removed. Said now: if χ = 256 does not reach δe ≤ 1e-3, the first test point is not evaluable for MPS, and the brief's target range down to 1e-4 for MPS is not reached on this lattice within budget.
Outcome: the ViT runs ended at 21:33-21:34Z (all five at the 80-minute wall cap); the manual tasks started at 21:37-21:43Z. Without the ViT load, χ = 256 at J2 = 0 took 217 s, so the fear above did not materialise. Slots were raised from 5 to 7 at 21:44Z.

## 8. 21:52Z. Watchdog fault fixed before it acted

watch2 counted DMRG processes with the pattern `code/dmrg_w.py`, but the manual tasks run `dmrg_w.py` by relative path, so it would have run the analysis and shut the VM down while manual DMRG tasks were still running. Found at its poll of 21:51Z (count 1 instead of 4) before any shutdown condition was met; the pattern is now `python.*dmrg_w[.]py` and the watchdog was restarted directly in phase 2 (no task relaunched).

## 9. End of run

- The analysis ran at 22:53:34Z as a manual task (item 7), was fetched (0 files failing their hash) and the VM was stopped at 22:55:50Z by the watchdog; lock released 22:56:24Z.
- The declared `clean` step (removing the two ground-state vectors in `work/` and the pip wheel) was not run before the stop. Left on /mnt/cj: the sandbox `W_20261107T190617Z` with its 1.0 GB venv, 43 MB of vectors and the pip wheel (free space 2.3 GB, 3.3 GB before). Removing them needs a restart of the VM; not done.
- All five ViT runs ended at the declared 80-minute wall cap (203-618 of 2000 steps), as the declaration allows; recorded here because the shortfall is large.
