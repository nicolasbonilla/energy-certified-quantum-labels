# Addendum C3b for Test C3 (written 2026-11-08, before the job is prepared and before any processor use)

Parents: `DECLARATION.md` (SHA-256 8bf821e5af73f180fcab45e0f7c26aec94e1b78107321e7a8a031a5708e9091b, hashed 2026-11-06T12:01:21Z) and `ADDENDUM_C3.md`
(SHA-256 ebb393d3f83089a46259d10251d3c20d89a2beea84189c4d870aa04ed035bd24, hashed 2026-11-06T13:23:01Z). This file is hashed into `ADDENDUM_C3b.sha256`
(UTC time on its second line) before the job is prepared, and does not change afterwards. It changes no rule of either parent.

## Decision

- 2026-11-06: C3 was not submitted although the sealed gate passed (`DEVIATIONS.md` item 3). The sealed backend rule did not give ibm_kingston that day, and the
  gate's noise model, fitted on ibm_kingston on 2026-10-31 (layout score 0.790), does not describe ibm_fez (score 1.252). The author then answered
  "SI AUTORIZO TODO", read as ratifying that and retrying only if ibm_kingston recovers (`NOTES_AFTER_RESULTS.md`).
- **2026-11-08: the author decided "si, hagamos el intento"**, after being told that the likely outcome is a declared failure (interval about 1.8 τ wide).
  This overrules the non-submission of 2026-11-06. **The author approved ibm_kingston only.**

## State today (read-only look, 2026-11-08T15:40:41Z; `logs_laptop/diag_kingston_20261108.txt`, `.json`)

- Plan: open, pricing free; 421 s consumed of 600 in the rolling 28-day window; **179 s remaining**.
- ibm_kingston: operational, status "active", 35 pending jobs. **Calibration last update 2026-11-08 16:24:37+01:00 (15:24:37Z).** No faulty qubit or gate
  listed. Five pairs still listed with error 1.0: (112,113), (121,122), (130,131), (145,146), (146,147); the pair (29,38) of 2026-11-06 has recovered.
  Readout error median 0.0095.
- Sealed layout rule `qpu_route.choose_routed_layout` (ladder ×1, ×2, ×4): **succeeds at ×1** (no relaxation), **score 0.8493** expected two-qubit errors
  per Trotter step (job B on 2026-10-31: 0.790; ibm_fez on 2026-11-06: 1.252), 16 moves per step, mean readout error 0.0114 of the 57 homes, 8 ancillas,
  57 native and 7 routed edges.
- Bit-order tests `code_c3/tests/test_bitorder.py` with `C:\tmp\qgss4env`: **7/7 pass** (15:41:08Z-15:43:36Z; `logs_laptop/test_bitorder_c3b_20261108.txt`).

## Conditions, all required; if any fails, nothing is submitted

- **(a)** The sealed backend rule gives ibm_kingston: operational and the sealed layout rule succeeds. Today: yes, at ×1.
- **(b)** Its score ≤ 0.95 expected two-qubit errors per step, the validity limit of the gate's noise model (`DEVIATIONS.md` item 3: the scan holds up to a
  noise factor f ≈ 1.2 relative to job B). **This is a stop-only addition, stricter than the seal**: it can prevent the job; it cannot cause it, and it changes
  no rule. Today: 0.8493 (f = 0.8493/0.790 = 1.075).
- **(c)** At least 150 s remain, plan open, pricing free. Today: 179 s.
- **(d)** The 7 bit-order tests pass today in `qgss4env`. Today: 7/7.

(a) and (b) are evaluated again by the code at preparation, on the calibration current then; (c) again immediately before submission. If any fails there,
nothing is submitted. **No fall-back**: the second branch of the sealed backend rule (another free backend) is not used, because the author approved only
ibm_kingston.

## Protocol, decision rule, shots, certificates and analysis: exactly those of `ADDENDUM_C3.md`

Nothing of `ADDENDUM_C3.md` (and of `DECLARATION.md` section 5, C3, to which it refers) is changed: checks `neel` and `asym` with 10⁴ shots each; Jz = 6.0,
Δt = 0.0681, k = 1..10, 40,000 shots each (420,000 in all); routed layout rule on the calibration current at preparation; SamplerV2, dynamical decoupling on,
gate twirling on (auto), measurement twirling off; `max_execution_time` = 150 s; pre-submission equivalence of the k = 1 ISA circuit within 1e-6; one job,
no resubmission except after an error before running; every job id logged. Decision rule: data count only if both bit-order checks pass (every site ≥ 0.9,
majority equal); **PROVED BELOW TOLERANCE iff variant `rec`, m_s, exact width ≤ τ with τ = 0.06 × the interval's lower end**; C̄_zz reported beside it.
If the job fails or the checks fail, that is reported and no second job is sent. Exact quotient `code/ft.py <root> crq C 6.0 rec|ps` and noiseless control
`code_c3/c3_post.py <root> 40000`, both on cj-runner-1b; interval with the unchanged `code/analyze_c.py <out> inputs <result> C` (exact arithmetic, seconds),
reading the verified certificates of 2026-11-06. Whatever the outcome, it is not described as "device validated".

**Known errata (`DEVIATIONS.md` item 4).** `ADDENDUM_C3.md` says "Certificates: all 42 at Jz = 6 (stored + the 6 new)". 42 is the total at Jz = 4 and 6
(36 stored + 6 new); Jz = 6 has 18 (12 stored + 6 new). `analyze_c.py` filters by coupling, so the set used is the 18 at Jz = 6.

## Implementation (changes no rule)

- Job folder `jobs/C_20261108/`. `jobs/C/` (prepared for ibm_fez on 2026-11-06) stays untouched and is not reused.
- `code_c3b/run_c3b.py`: imports the sealed `code_c3/submit_c3.py` unchanged after checking the 10 sealed hashes below; sets the job folder; replaces
  `choose_backend` by its first branch (the same calls on ibm_kingston) without the fall-back, plus the stop-only limit (b); refuses to prepare or submit
  unless this file matches `ADDENDUM_C3b.sha256`. `prepare`, `submit`, `poll`, `fetch` are the sealed functions.
- `code_c3b/diag_c3b.py`: the read-only look above. `code_c3b/vm_c3b.sh`: the VM procedure of `code/vm/vm_ft.sh` (lock by noclobber, cj-poweroff off before
  start, `cj-runner@vm` stopped, max-run-duration with STOP, here 2 h, the budget of this part; at the end cj-poweroff on, stop, limit cleared, lock removed),
  new sandbox `/mnt/cj/sandbox/ft_c3b_<stamp>/` set up by the sealed `code/vm/ft_vm.sh`. Device configurations enter as `inputs/qpu_C_raw_configs.npz`.

## Planning expectation (exploratory, not a rule)

The noise scan of `DEVIATIONS.md` item 3, at today's factor 1.075: mean ε ≈ 0.32 J (0.289 J at f = 1.0, 0.334 J at f = 1.1), below the gate limit 0.478 J and
the threshold 0.598 J. With the 18 certificates at Jz = 6 that energy gives an m_s interval about 0.63 τ wide (0.58 τ at f = 1.0, 0.68 τ at f = 1.2;
`logs_laptop/c3b_planning_widths_20261108.txt`). The 1.8 τ figure given to the author was for ibm_fez's ratio 1.585. Scaling every p_k by a score ratio is
crude and no device data at Jz = 6 exist, so the outcome can differ in either direction; the response is steep beyond f = 1.2.

## Code and records at this hash

```
3b62b60c48613f1da8e1da3d15d116cffefc10e1a3437418ed29d8730fed1315  code_c3/c3_post.py
b5d9483fac22887c75ed73d546fe4a2cadaeb7c10146342aed42635ba2c970be  code_c3/qpu_lib.py
7ff6fd17a0cba8c3452b4a4d37ecbc0d1483044ca1d3ccb82aab2c4c2d85e18b  code_c3/qpu_route.py
4e4a642c2988ac0bd619453d9495689a6bf15b739d68b35f4dcf888c53c92ef2  code_c3/submit_c3.py
0ffacd2ed6cbf0c979a835c6939a4734711589625edc4d091cf8542ca847db96  code_c3/tests/test_bitorder.py
2ca90a6ec4349d027adbde10699ba6f8b1d7fbba559bd95a41be4dec762af0e0  code_c3/tests/toygraphs.py
a0f0ac663742f306c0daaca4fe80f8859bc1b547189015b41893355ca0c98fae  code_c3/method_copy/emu.py
79e295a61025d686b30ecec69b7dbf53f9fae5be75e706884b453865893ad586  code_c3/method_copy/emu2.py
1eb7b6cead37b1e06e95592f8cf7a08b252f188c4ac9e0730a977ee92db4921a  code_c3/method_copy/hhmodel.py
edd848d7ffd2952ec332cd0cd5bd149c8bf0cd00840329979c0eece957a39d9a  code_c3/method_copy/tn.py
54c7054d3a2a148ef6c7615e779d05fa143d4f0cffa12151fd435919e30b0cda  code_c3b/diag_c3b.py
08f9d69a544b2ac1c396d9a02a20102bd80cd83b38aaebfe7721f82b126c97ec  code_c3b/run_c3b.py
47ca0db473f7ebea0a1ca33f0d5d193e2ef29410aeff513af4d0f5a6d51adb6b  code_c3b/vm_c3b.sh
59b975590c75f48ba3e1130904881a0d9043bdc6413a92e59cd71c3af155245c  code/ft.py
e050da8541497bbb497acc061893ddeea447a084d0c5e5abb65b6838af5653a8  code/analyze_c.py
2ab68d056fd1bd33e36af86f26721ad943a43156b8d3c5c9846c536e74852d18  code/ftlib.py
79e295a61025d686b30ecec69b7dbf53f9fae5be75e706884b453865893ad586  code/emu2.py
287fc1fbabfcc81afe9d24f498a069dc464edd011dcf39c40e41a8194a1bc857  code/fr.py
f2bcc00266f3a7b3325ce8004806c4562b5a0bc25adefc3fab2770273c33b363  code/vm/ft_vm.sh
86e780fef50cb67befd544b722384979f9a8f76ab2067b818d0769dd4af8beef  logs_laptop/diag_kingston_20261108.json
3b440d7810c04b52c67ede07241697395b49af49da1d38d10f32aeb64bc89683  logs_laptop/diag_kingston_20261108.txt
9b6cf84883234bcb07e0432b45caab67b429d36f2d29e7cbc51a19e515fc8ed4  logs_laptop/test_bitorder_c3b_20261108.txt
5c218ba0d219cbf7561f458de72dac4a271f817d8de65bc64062df1472bb1a6b  logs_laptop/c3b_planning_widths_20261108.txt
```
