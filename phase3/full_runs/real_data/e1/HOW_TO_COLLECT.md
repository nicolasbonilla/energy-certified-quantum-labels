# Extension E1: how to see progress, how to stop, how to collect

E1 = new exact m_s certificates at n = 57 (Jz = 3.3, 3.2) and n = 115 (Jz = 5.0, 3.6, 3.3), in that order of
priority (`real_data/DECLARATION.md` Sec. 3). What is computed and every reading: `E1_SPEC.md` (fixed and hashed
before the start). The run started on **2026-11-12 at 19:43:03 UTC** and is stopped at the latest on
**2026-11-13 at 03:43:03 UTC** (8 hours of wall time; `out/T0.txt`). Commands below are typed in PowerShell from
this folder (`...\phase3\full_runs\real_data\e1`).

## 1. See progress

- `STATUS.json` (rewritten every 5 seconds while the scheduler lives):
  - `finished` (true when everything has ended), `stop_reason`, `updated_utc`, `elapsed_hours`, `hard_stop_utc`;
  - `running`: the jobs in progress; `job_counts`: verified / failed / stopped;
  - `rows`: for each of the five rows the best bound per side, the number of points done, whether stage A is done,
    what stage B did, and `w_cert_over_tau`. **That width is the in-sector form at E_real + 1e-6; it steers the
    search. The declared E1 column (energy and mean magnetization, Sec. 2) is produced by `collect_e1.py`.**
  - `jobs`: one line per certificate job (`state`: running / verified / failed / stopped / DISPUTED; exact bound;
    verdict of the stored verifier and of the independent verifier; times of the three steps).
- `out/run_log.txt`: one line per start and end of a job. `out/watchdog_log.txt`: the watchdog.
- `out/jobs/<id>_opt.log`: the optimizer of one job, line by line.
- Processes alive: `python -B code\watchdog_e1.py --list`
- If `updated_utc` is more than a minute old while `finished` is false, the scheduler has died: read
  `out/logs/scheduler_*.err.txt`, then resume (Sec. 3).

## 2. Stop

- **Gently** (no new job; the jobs in progress finish, each takes 4 to 60 minutes): create the empty file `out/STOP`
  (`New-Item out\STOP`).
- **At once** (jobs in progress are stopped and give no certificate): `python -B code\watchdog_e1.py --now`
  (it creates `out/KILL`, waits 20 s for the scheduler to stop its jobs, then stops whatever is left).
- **Nothing to do at the cap:** the scheduler starts no job in the last 10 minutes and stops its jobs at 8 h; the
  watchdog (a second, independent process) stops everything of E1 two minutes later.
- The cap counts wall time: a laptop that sleeps loses that time. Nothing else on the machine is touched: only the
  processes whose command line contains `real_data\e1\code` are stopped.

## 3. Resume after a stop or a crash (within the same 8 hours)

`powershell -NoProfile -ExecutionPolicy Bypass -File launch_e1.ps1`

It refuses while a scheduler is alive. Otherwise it moves `out/STOP`, `out/KILL`, `out/RUN_EXIT` aside, stops job
processes left over from the previous start, reads every finished job from `out/jobs/` and continues the same
branch-and-bound. **The cap still counts from the first start** (`out/T0.txt`); after 03:43 UTC a resumed scheduler
ends at once. Do not delete `out/T0.txt`: that would start a new 8-hour budget, which the declaration does not allow.

## 4. Collect

When `STATUS.json` says `"finished": true` (or earlier, with `--partial`):

```
python -B -I collect_e1.py            # checks, copies to certs\, runs the declared map code into map_e1\
python -B -I collect_e1.py --dry      # only lists what would be collected; writes nothing
python -B -I collect_e1.py --partial  # the same before the end (the column is then not the final one)
python -B -I collect_e1.py --no-map   # checks and copies only
```

What it does: (1) refuses unless `DECLARATION.md` matches its hash; (2) accepts a certificate only if it is an E1
task with the stored settings and a field of the declared grid, its claimed bound equals `sum t_k - mu M_0`, the
stored verifier's record is ok for that very file and bound, and the independent exact verifier confirms the same;
(3) copies the accepted ones to `certs/` as `<id>_cert.json` + `<id>_ver.json` (the stored names and format) with a
manifest `certs/E1_CERTS.json`; (4) runs `real_data/code/run_map.py --out e1/map_e1` (the declared code, unchanged),
which builds the **separate E1 column** with the rule of Sec. 2: fields `exact_e1`, `status_e1`, `status_e1_rf` of
`map_e1/map_rows.json`; `sec2_e1` in the J* table of `map_e1/map_summary.json`; `secondary_E1` in
`map_e1/S_sets.json`. It prints the rows where the E1 column differs from the stored one. `real_data/out/` is never
written.

**Two things to know after collecting:**

1. As long as `e1/certs/` holds certificates, `real_data/code/run_map.py` **without `--out`** stops with
   "S_sets.json exists with another content": the code protects the hashed nested sets of `real_data/out/`, and
   with E1 present the file would gain the key `secondary_E1`. This is intended. Either pass `--out` (as
   `collect_e1.py` does), or move `e1/certs/` away to get the pre-E1 state back. Before collection nothing of this
   happens: in `out/jobs/` the stored verifier's record is named `<id>_verify_exact.json`, which the map code does
   not read.
2. The sets S, S_3/4, S_1/2 and S_p never use E1 (declaration Sec. 3 and 7); only `secondary_E1` does.

## 5. What is where

| path | content |
|---|---|
| `E1_SPEC.md`, `E1_SPEC.sha256`, `E1_SPEC_hash_time.txt`, `E1_MANIFEST.sha256` | what is computed, fixed before the start; hashes of code, plan and grid |
| `code/lb_opt.py`, `lbcore.py`, `verify_exact.py`, `graphs/` | byte-identical copies of `rigor/code/` (optimizer and stored exact verifier) |
| `code/myverify.py` | byte-identical copy of the independent exact verifier of gate G5 |
| `code/make_plan_e1.py`, `plan_e1.json`, `grid_e1.json`, `plan_e1_stdout.txt` | the declared grid for the five rows (self-check against the stored v2 grid) |
| `code/run_e1.py`, `job_e1.py`, `watchdog_e1.py`, `launch_e1.ps1` | scheduler (branch-and-bound and stage rule of v2), one job, watchdog, launcher |
| `out/jobs/` | per job: `_task.json`, `_cert.json`, `_verify_exact.json`, `_myver.json`, logs, `.done` |
| `out/run_log.txt`, `out/watchdog_log.txt`, `out/launch_log.txt`, `out/logs/`, `out/T0.txt`, `out/pids.json` | logs |
| `STATUS.json` | progress |
| `certs/`, `map_e1/` | created by `collect_e1.py` |

## 6. Reading the result honestly

- A certificate is a theorem about the operator H(Jz) - sigma lam S m_s + mu M_tot. It does not depend on any energy.
- A row is CERTIFIED (exact) in the E1 column only if its interval at (E_real, M) for both M_real and M_0 is at most
  tau wide. At n = 57, Jz = 3.3 and 3.2 the DMRG-referenced width at the real energy is already 0.958 tau and
  0.977 tau, so those two intervals are expected to come out slightly wider than tau (`E1_SPEC.md` Sec. 5): the
  certificates then extend the range where an exact interval exists without certifying those rows.
- A coupling whose jobs were stopped by the cap is "not computed". `STATUS.json` and `certs/E1_CERTS.json` say
  which couplings have certificates on both sides.

## Log (dated additions after the start)

- 2026-11-12 19:43:03 UTC: first start (scheduler and watchdog started with Start-Process; the session's job object
  does not end its processes on close: limit flags 0x1800). Six jobs running.
- 2026-11-12 19:47:50 UTC: first certificates verified by both verifiers (n = 57, Jz = 3.3 and 3.2, both signs; 286 to 296 s each). `collect_e1.py --dry --partial` accepted 4 of 4; the declared map code, pointed to a scratch copy, accepted 4 of 4 and built the E1 column (scratch `paper/reviews/R10_2026-11-12/scratch/rd-e1/hook_test_stdout.txt`). The task `rd-e1` ended here; the run continues on its own. Report: `paper/reviews/R10_2026-11-12/reports/rd-e1.md`.
