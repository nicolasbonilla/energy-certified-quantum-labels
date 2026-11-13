# Deviations from DECLARATION.md (dated)

## 1. 2026-11-06 12:2xZ. Tolerance of one unit test (G1), before any task of the plan ran

The sealed test `test_krylov_vs_exact` failed on the VM: |<Z>_MPS - <Z>_exact| = 4.1e-5 against a limit of 2e-5 that I had written
without considering the time-step error of the evolution. Diagnostic (`code/tests/diag_krylov.py`, n = 19 only, `logs_laptop/diag_krylov.txt`):
the unchanged `tn.krylov_states` and the new `ft.dis_krylov_states` give the same error at J_e = 1 (1.043e-3 at k = 10, nsub = 2), and the
error falls by 3.9x per doubling of nsub (disordered: 1.70e-3, 4.53e-4). So the new code has no coupling error; the difference is the second-order
time-step error of the method run's own evolution, which the declaration keeps (nsub = 2). The test was replaced by a stricter check of the
right kind: convergence (factor > 3 per halving, error < 1e-3 up to k = 4) and equality with the unchanged code at J_e = 1 (< 1e-10).
No pipeline code changed. Consequence to state in the results: the Krylov states differ from exact evolution by up to about 2e-3 in <Z> at k = 10;
they only decide which configurations are sampled. The labels come from Rayleigh-Ritz with the exact H in those configurations.

## 2. 2026-11-06 13:2xZ. Additions after the hash that change no rule

`code/tests/diag_krylov.py` (diagnostic of item 1) and `code_c3/` with `ADDENDUM_C3.md` (declared in section 5: written after the gate). `submit_c3.py` is `qpu/code/submit_job.py`
cut to one job; `c3_post.py` is the control of `qpu_post.py`. The usable Python on the laptop for IBM is the previous run's `C:\tmp\qgss4env`, not the system one.

## 3. 2026-11-06 14:3xZ. C3 not submitted, although the sealed gate passed (the decision that matters)

Sealed gate: ε_sim = 0.2892 J ≤ 0.8 ε_thr = 0.4782 J: **PASS**, with noise calibrated on ibm_kingston (job B). At preparation (14:32Z), after Test B as ordered, the sealed backend rule did not
give ibm_kingston: today its calibration has seven pairs above 0.2, six of them listed with error 1.0: (29,38), (112,113), (121,122), (130,131), (145,146), (146,147), the layout rule finds no embedding at
×1, ×2, ×4, and even ×8 fails (at ×20 the score is 3.9 expected two-qubit errors per step; `logs_laptop/diag_kingston.txt`). ibm_marrakesh: no embedding. The rule therefore selects ibm_fez, relaxation ×4,
score 1.252 against 0.790 for job B: a device the gate's noise does not describe.

Added check, not in the seal, which can only stop the job (`code/c_gate_fez.py`, `out/c/sim_fez.json`): same simulation with p_k scaled by a factor f. Mean ε (J): f = 1.0: 0.289; 1.1: 0.334; 1.2: 0.363; 1.3: 0.534;
1.4: 0.710; 1.585 (= 1.252/0.790): **1.224**; 1.98: 1.730. So at fez's ratio the simulated error is 2.6 times the gate limit and twice the threshold. Scaling all p_k by the score ratio is a crude estimate, and I have no device data
from fez. But the margin is wide, and the brief's gate says processor time is spent only if the simulated error passes.

**Decision: no job was submitted. 0 s of processor time used; balance stays 179 s; no job id exists.** The literal sealed procedure would have run on fez. I did not follow it, because the number that passes describes a different device, and spending the
free seconds cannot be undone while not spending can. This is my decision, not the author's: the prepared package (`jobs/C/prep.json`, `isa.qpy`, `ADDENDUM_C3.md`) stays ready, and if the author prefers to run on fez the outcome expected from the simulation is an interval about 1.8 τ wide. Practical criterion from the
scan (exploratory): the gate holds up to f ≈ 1.2, about 0.95 expected errors per step, which fez today does not reach; ibm_kingston on 2026-10-31 did (0.79).

Also added after the hash, changing no rule: `code/analyze_c_extra.py`; the noiseless control at Jz = 6 was run during Test B (13:30Z) so as not to keep the VM on afterwards; it is reported though no device data exist to compare it with.

## 4. 2026-11-06 15:1xZ. Wording error in the sealed addendum

`ADDENDUM_C3.md` says "Certificates: all 42 at Jz = 6 (stored + the 6 new)". 42 is the total at Jz = 4 and 6 (36 stored + 6 new); Jz = 6 has 18 (12 stored + 6 new). `analyze_c.py` filters by coupling, so every number is right. The sealed file is left unchanged.

## 5. 2026-11-08 to 2026-11-10. Author ratification: item 3 overruled; C3 run on ibm_kingston; exact analysis not yet run

**Author, 2026-11-08: "si, hagamos el intento"**, after being told that the likely outcome was a declared failure (about 1.8 τ; that figure was the ibm_fez estimate of item 3).
This overrules the non-submission of item 3, for ibm_kingston only. Before any processor use, `ADDENDUM_C3b.md` (SHA-256 afe88fa51b3fccca5909329a3ebeaa8c5184c456dbe50b2cedcfdc44c1290224,
hashed 2026-11-08T15:47:52Z) fixed four conditions, all met: (a) ibm_kingston operational and the sealed layout rule succeeds (at ×1, no relaxation); (b) score 0.8493 ≤ 0.95
(stop-only addition, stricter than the seal); (c) 179 s remaining, plan open, pricing free; (d) bit-order tests 7/7. No fall-back to another backend. Protocol, decision rule,
shots, certificates and analysis are those of `ADDENDUM_C3.md`; the errata of item 4 stands. The sealed code ran unchanged through `code_c3b/run_c3b.py` (job folder
`jobs/C_20261108/`, backend restricted to ibm_kingston); `jobs/C/` was not touched.

**Run.** Prepared 2026-11-08T15:48:00-15:48:16Z on the calibration of 15:24:37Z (equivalence 9.6e-12, lower-bound estimate 109.2 s). **One job, `dbo9jnk4148s73925q8g`, submitted
15:48:46Z** (balance read just before: 179 s). Queued 33 h; executed 2026-11-10 01:02:00-01:04:06Z; DONE; fetched 01:16:57Z. **119.0 s used** (declared expectation about 119 s);
**balance 60 s**. **Bit-order checks pass**: neel minimum site agreement 0.9536, asym 0.9583, majority equal in both, so the data count. Recorded, not a rule: at execution the
calibration had changed (last update 2026-11-10 00:55:51Z) and the prepared layout scores 0.7931 on it (0.8493 at preparation).

**Not run: the exact quotient and the interval.** During the queue the author set a new rule: no cloud VM without his explicit OK (cloud spending is now a concern). So
`ft.py crq C 6.0 rec|ps` was not run, no VM was started, no lock created, no disk touched, and `code_c3b/vm_c3b.sh` (fixed in the addendum) was not used. **C3 has no verdict
yet.** The noiseless control needs no new run: it is device-independent (logical circuits, fixed seeds, 40,000 shots per circuit, the sealed `code_c3/c3_post.py`) and was run
on 2026-11-06 (`out_20261106T120830Z/out/c/control_J6.0.json`, item 3 last paragraph); a rerun would only reproduce it. Running the quotient on the laptop instead of the VM would
be a further deviation (DECLARATION section 5 "rebuilt on the VM"; ADDENDUM_C3b "on cj-runner-1b"; laptop numpy 2.4.6 and scipy 1.17.1 against the VM's 2.2.6 and 1.13.1)
and is left to the author.

**Added after the hash, exploratory, read-only, seconds on the laptop:** `code_c3b/noise_c3b.py`: the in-sector fraction of any in-sector state under i.i.d. flips depends only
on the flip probability, so it is inverted exactly (the gate inverted the same function by Monte Carlo; the exact inverse reproduces the gate's p_k within 0.003). Today
p_k / p_k(gate) = 0.47 at k = 1 rising to 0.88-0.99 at k = 7..10, mean 0.81: the device was not noisier than the gate's model. `code_c3b/score_at_run_c3b.py` (the score above).
Status was polled 99 times (every 10, then 20 minutes): 92 answers, 6 failures from a loss of the laptop's network (2026-11-09 03:45-05:25Z) and one crash of the local Python
process (exit 139), none affecting the job. Another agent also polled the job (`logs_laptop/c3b_watch_20261109.txt`, not mine); its last poll rewrote
`jobs/C_20261108/status.json` (time only) at 01:20:03Z, after which `jobs/C_20261108/SHA256SUMS.txt` was regenerated.

## 6. 2026-11-10. Exact quotient and interval run as sealed (closes the open point of item 5; no new departure)

**Author, 2026-11-10: "opcion A vamos al maximo nivel"**, after being offered (A) the sealed VM, about 15 minutes and 0.15 EUR, cap 30 minutes and 0.30 EUR, or (B) the
laptop at no cost as a declared deviation. So the open point of item 5 is closed without a deviation: `code_c3b/vm_c3b.sh` (SHA-256 47ca0db4…, unchanged) ran `up`,
`push` (stamp `c3b_20261110T164846Z`), `crq`, `fetch`, `down` on cj-runner-1b only, with the declared versions (python 3.11.2, numpy 2.2.6, scipy 1.13.1, TeNPy 1.1.0).
VM 16:47:36-16:51:56Z; lock released 16:52:36Z; all VMs TERMINATED. `code/analyze_c.py` (unchanged) then ran on the laptop in seconds, as DECLARATION section 6 allows,
on a folder of byte copies of the 2026-11-06 certificate and job-B outputs plus the two new quotients (`analysis/c3b_20261110/merged_out/`; sources verified against
their SHA-256). The noiseless control was not rerun (device-independent; run on 2026-11-06 with the sealed code).

Added, stop-only, not in the seal: a laptop watchdog (`logs_laptop/c3b_vm_watchdog_20261110.txt`) that would run `vm_c3b.sh down` 30 minutes after arming, to enforce the
author's cap below the sealed 2 h limit. It could only stop the VM.

**Outcome: PROVED BELOW TOLERANCE** (variant `rec`, m_s, width 0.4992 τ). Details in `RESULTS.md`, section "C3: veredicto (2026-11-10)".

Note to item 6 (2026-11-10, after an independent reading of the paper's changed text): not rerunning the noiseless control
departs from the letter of `ADDENDUM_C3b.md` ("noiseless control ... both on cj-runner-1b"). It is counted under this item,
with the stop-only timer, so the paper lists six deviations. The control of 2026-11-06 used the same sealed code
(`code_c3/c3_post.py`), the same logical circuits and fixed seeds; it does not depend on the device. Also: only the exact
quotient ran on the VM; the interval (`analyze_c.py`) ran on the laptop, as DECLARATION section 6 allows.
