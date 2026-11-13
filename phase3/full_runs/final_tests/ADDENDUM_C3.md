# Sealed addendum for Test C3 (written 2026-11-06, after the gate, before any processor use)

Parent: `DECLARATION.md` (SHA-256 8bf821e5af73f180fcab45e0f7c26aec94e1b78107321e7a8a031a5708e9091b, hashed 2026-11-06T12:01:21Z). This file is hashed
into `ADDENDUM_C3.sha256` before job submission and does not change afterwards.

## Gate result (DECLARATION section 5, C2; `analysis/test_c_stage2.json`)

- Rigorous threshold for m_s at Jz = 6, over 36 stored + 6 new verified certificates: ε_thr = 0.5978 J (stored only: 0.5569 J).
- Device-calibrated simulation of the planned job (S = 40,000 per circuit, 3 seeds): ε_sim = 0.2892 J.
- Gate: ε_sim ≤ 0.8 ε_thr = 0.4782 J. **PASS** (ratio 0.484).
- Validation at Jz = 4.0, S = 23,000: simulated 0.8350 J, device 0.8256 J (device/simulated 0.989), so the rescaled value is the same 0.2892 J.
  The noise model is fitted to in-sector shot fractions only; the energy agreement is a check, not a fit.

## Protocol, fixed here

- Exactly as DECLARATION section 5, C3: checks `neel` and `asym`, 10⁴ shots each; Jz = 6.0, Δt = 0.0681, k = 1..10, 40,000 shots each (420,000 shots in all);
  routed layout rule of `qpu_route.choose_routed_layout` on the calibration current at preparation; SamplerV2, dynamical decoupling on, gate twirling on
  (auto), measurement twirling off; `max_execution_time` = 150 s; one job.
- Balance read 2026-11-06T12:50Z: 421 s consumed of 600, 179 s remaining, plan open, pricing free. Read again immediately before submission; at least 150 s required.
- Order: the job is submitted after Test B has finished, as the brief orders.
- Backend rule: ibm_kingston if operational and the layout rule succeeds; otherwise the free backend with the fewest pending jobs where it succeeds.
- Software: the virtual environment of the previous device run, `C:\tmp\qgss4env` (the laptop's system Python has an old qiskit that cannot run this code).
  Bit-order tests: 7/7 pass with it today (`logs_laptop/test_bitorder_c3.txt`). Note: the first attempt used the system Python by mistake and failed on an import
  error, before any test ran on the right environment.
- **Decision rule.** Data count only if both bit-order checks pass (every site ≥ 0.9, majority equal). PROVED BELOW TOLERANCE iff variant `rec`, m_s, exact width ≤ τ with
  τ = 0.06 × the interval's lower end. C̄_zz reported beside it. Certificates: all 42 at Jz = 6 (stored + the 6 new). If the job fails or the checks fail, that is reported and no
  second job is sent.
- Noiseless control: `code_c3/c3_post.py` on the VM with the same shots. Exact quotient: `ft.py crq C 6.0 rec|ps`.

## Code at this hash

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
```
