1. Hicimos las tres pruebas con las reglas selladas antes de calcular. Dos dan una respuesta clara y la tercera quedó sin hacer en el procesador real.
2. **Prueba A (la curva del error, con valores nuevos): PASA.** La curva calculada con 19 sitios predice el error de las etiquetas con 57 y 115 sitios: falla de media 0,06 y 0,34 unidades de tolerancia (los límites eran 0,2 y 0,6), y todas las proporciones quedan entre 0,88 y 1,06. Pero no es lo mejor que hay: con 115 sitios una fórmula sencilla sin ajustes falla 0,11, y tres cuentas clásicas que no usan datos cuánticos fallan 0,08, 0,02 y 0,01.
3. **Prueba B (¿las etiquetas cuánticas añaden información?): NO.** Es la decisiva y el resultado no deja dudas. El mejor método clásico, resolver exactamente un trozo de 19 sitios alrededor de cada etiqueta, falla 0,08 y 0,01 unidades. El modelo con etiquetas cuánticas falla 0,74 y 0,21: de 9 a 20 veces peor, en los 12 casos de los 12. La regla pedía ser un 25 % mejor.
4. Corregir la etiqueta sí sirve: el error baja unas 4 veces (de 3,30 a 0,74 y de 0,87 a 0,21). Pero no llega a lo clásico. Además, un cálculo clásico barato sobre el sistema completo (menos de un minuto) falla 0,05 y 0,004.
5. **Prueba C, primera parte: hecha.** La etiqueta real del procesador en Jz = 4 ya tiene un intervalo totalmente demostrado, sin cálculo clásico de referencia ni lectura de gráficas: orden magnético entre 0,868 y 0,997. Es 2,47 veces más ancho que la tolerancia: demostrado, pero no suficiente. La correlación entre vecinos queda 2,01 veces por encima.
6. **Prueba C, segunda parte: la compuerta pasó, pero no envié el trabajo.** La simulación daba 0,29 J frente a un límite de 0,48 J, con el ruido de `ibm_kingston`. Hoy kingston tiene enlaces averiados y no admite la colocación, y el único equipo posible es `ibm_fez`, con 1,6 veces más ruido esperado. Con ese ruido la simulación da 1,22 J: no pasaría. Decidí no gastar los segundos gratuitos. Esta decisión es mía y se aparta del procedimiento sellado; está anotada.
7. **Por tanto, hoy ninguna etiqueta real del procesador tiene un intervalo demostrado por debajo de la tolerancia.** Y aunque lo tuviera, en Jz = 6 un método clásico es al menos igual de bueno: con el cálculo clásico el intervalo sería unas 5 veces más estrecho que el esperado del procesador.
8. Coste: 2,89 horas de máquina, unos 1,71 € (2,14 € con el recargo que se usó en cuentas anteriores), de 12 € permitidos. Procesador de IBM: 0 segundos usados, quedan 179. Las tres máquinas están apagadas, sin candados. La factura real aún no se puede leer.

---

# Final tests: results (2026-11-06)

Rules: `DECLARATION.md` (SHA-256 8bf821e5af73f180fcab45e0f7c26aec94e1b78107321e7a8a031a5708e9091b, hashed 2026-11-06T12:01:21Z, before the VM started) and
`ADDENDUM_C3.md` (SHA-256 ebb393d3f83089a46259d10251d3c20d89a2beea84189c4d870aa04ed035bd24, hashed 2026-11-06T13:23:01Z). Deviations: `DEVIATIONS.md` (4 items). Run stamp 20261106T120830Z on cj-runner-1b.
Queue: 128 tasks, 0 failed. All numbers come from `out_20261106T120830Z/out/` (0 files failing their SHA-256) through `code/analyze_a.py`, `analyze_b.py`, `analyze_c.py`, `analyze_c_extra.py`
(`analysis/`). Statements concern the emulated method class and our own device data, not the labels of arXiv:2606.15983.

## 1. Verdicts against the declared rules

| Test | Declared rule | Outcome | Verdict |
|---|---|---|---|
| **A** | mean miss ≤ 0.2 τ (n = 57), ≤ 0.6 τ (n = 115), all ratios in [0.75, 1.3] | 0.062 τ, 0.340 τ, ratios 0.885-1.057 | **HOLDS OUT OF SAMPLE** |
| A, against the chord | stated separately | beats it at n = 57 (0.062 vs 0.234); loses at n = 115 (0.340 vs 0.105) | mixed |
| A, against classical forms (n = 115) | stated separately | loses to all: a + b/n 0.082, a + b N_e/n 0.019, a + b/√n 0.011 | **does not beat them** |
| **B**, Jz = 1.6 | q_top ≥ 25 % better than best classical, ≥ 5 of 6 | −806 %, 0 of 6 | **NO** |
| **B**, Jz = 2.5 | same | −2006 %, 0 of 6 | **NO** |
| **B**, general | both Jz | | **QUANTUM LABELS DO NOT ADD INFORMATION** |
| B, no target-size reference | same rule | −843 %, −1985 %, 0 of 6 at both | NO |
| B, secondary family | same rule | −429 %, −1890 %, 0 of 6 at both | NO |
| **C1** | report the interval | m_s 2.47 τ, C̄_zz 2.01 τ | done; not below τ |
| **C2** | ε_sim ≤ 0.8 ε_thr | 0.2892 ≤ 0.4782 J | **PASS** on the noise of ibm_kingston |
| **C3** | run if the gate passes | **not run** (deviation 3) | **no processor label below τ** |

Gates: G1 10/10 after deviation 1; G-A2 pass (|ΔE₀| 2e-14, |Δm_s| 1e-13, curve 4e-9); G-A3 pass, exact replication (ΔE₀ = 0, ΔΔm_s = 0, same D); G-B1 pass (largest mean |χ200 − χ320| 6.7e-5 τ); G-B2 pass
(δe 0.0263-0.0289 and 0.0085-0.0094, inside the windows). Krylov truncation below the method run's 1e-6 flag in Tests A and B (largest 8.2e-7); above it in the samples of the C2 simulation (1.1e-6 at Jz = 4, 1.5e-6 at Jz = 6), which feed a planning quantity only. Sealed ledgers identical at boot and end.

## 2. Test A: blind test of the bias curve

Miss in τ = 0.06 |m_s(GS)|. "Raw" = label as generated.

| n | Jz | m_s(GS) | δe | Δm_s | raw | **n = 19 curve** | ratio | chord | n = 19 truth | n = 57 curve | a + b/n | a + b N_e/n | a + b/√n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 57 | 1.5 | 0.7443 | 0.02859 | +0.1627 | 3.64 | **0.132** | 0.965 | 0.538 | 0.92 | – | – | – | – |
| 57 | 1.7 | 0.7928 | 0.02145 | +0.1191 | 2.50 | **0.085** | 0.967 | 0.348 | 0.71 | – | – | – | – |
| 57 | 2.8 | 0.9171 | 0.00493 | +0.0235 | 0.43 | **0.017** | 1.041 | 0.013 | 0.22 | – | – | – | – |
| 57 | 3.2 | 0.9359 | 0.00305 | +0.0136 | 0.24 | **0.013** | 1.057 | 0.037 | 0.16 | – | – | – | – |
| 115 | 1.5 | 0.7602 | 0.05865 | +0.2048 | 4.49 | **0.584** | 0.885 | 0.134 | 1.25 | 0.098 | 0.121 | 0.027 | 0.016 |
| 115 | 1.7 | 0.8057 | 0.04844 | +0.1603 | 3.32 | **0.397** | 0.893 | 0.128 | 0.97 | 0.044 | 0.091 | 0.018 | 0.015 |
| 115 | 2.8 | 0.9222 | 0.01867 | +0.0502 | 0.91 | **0.039** | 0.959 | 0.054 | 0.31 | 0.026 | 0.035 | 0.012 | 0.001 |

| Mean (max) | raw | n = 19 curve | chord | n = 19 truth | n = 57 curve | n = 57 truth | a + b/n | a + b N_e/n | a + b/√n |
|---|---|---|---|---|---|---|---|---|---|
| n = 57 | 1.70 (3.64) | **0.062** (0.132) | 0.234 (0.538) | 0.505 (0.92) | – | – | – | – | – |
| n = 115 | 2.90 (4.49) | **0.340** (0.584) | 0.105 (0.134) | 0.844 (1.25) | 0.056 (0.098) | 0.236 (0.35) | 0.082 (0.121) | 0.019 (0.027) | 0.011 (0.016) |

Readings.
- This is the first declared test of the curve, and it passes with room at both sizes. It reproduces the exploratory pattern: the curve is best at n = 57, while at n = 115 it is below the chord.
- At n = 57 only three of four rows beat the chord: at Jz = 2.8 the chord is slightly better (0.013 vs 0.017). The mean favours the curve because of the two rows near the isotropic point.
- At n = 57 all four variants also lie near the curve (ratios 0.946-1.124; `analysis/test_a.json`). The seven rule ratios use the primary label only.
- At n = 115 the ratio stays below 1 at all three couplings (0.885-0.959), the same systematic deficit seen in the exploration.
- The test says the bias is predictable. It does not say the corrected label beats a classical estimate: every classical form at n = 115 beats it, and only the n = 57 curve beats a + b/n.
- **Blindness, as declared:** labels and predictors at these couplings did not exist. DMRG truth at n = 57, Jz = 2.8 and 3.2 did exist (`design/pilot2/`, `map/`). It was not read; it was recomputed. The brief's phrase "never computed before" is therefore true of the labels only.
- Time steps at Jz = 1.7, 2.8, 3.2 are interpolated, a choice of this run. The n = 115 emulation is the one the paper already calls uncalibrated, and the same applies here.

## 3. Test B: do quantum labels add information?

Mean over 121 labels and six instances, in units of τ_type (0.06 × mean |label| of that type and instance). n = 57, J_e uniform in [0.5, 1.5]; 600 training instances per Jz at n = 19.

| Estimator | uses | Jz = 1.6 | Jz = 2.5 |
|---|---|---|---|
| label as generated | quantum | 3.303 | 0.867 |
| **q_top: label + correction (primary)** | quantum | **0.742** | **0.207** |
| q_top, E₀ without target-size reference | quantum | 0.772 | 0.205 |
| q_kry: secondary family | quantum | 0.433 | 0.196 |
| q_kry, no reference | quantum | 0.417 | 0.182 |
| C1 regression on local couplings | classical | 0.921 | 0.240 |
| C2 open cluster, 19 sites | classical | 0.918 | 0.158 |
| C4 open cluster, 13 sites | classical | 2.205 | 0.711 |
| C6 stack on 13-site clusters | classical | 0.240 | 0.030 |
| C5 embedded cluster, 13 sites | classical | 0.163 | 0.025 |
| **C3 embedded cluster, 19 sites (best classical)** | classical | **0.082** | **0.010** |
| recorded: DMRG on the target, χ = 32 (about 1 minute) | classical | 0.051 | 0.0043 |
| recorded: DMRG on the target, χ = 64 (about 1 minute) | classical | 0.0040 | 0.00015 |

| Per instance (0..5) | Jz = 1.6 | Jz = 2.5 |
|---|---|---|
| best classical | 0.066, 0.085, 0.093, 0.095, 0.086, 0.066 | 0.008, 0.012, 0.009, 0.010, 0.010, 0.010 |
| q_top | 0.663, 0.743, 0.882, 0.914, 0.613, 0.637 | 0.189, 0.238, 0.184, 0.218, 0.204, 0.210 |
| change, 95 % bootstrap | −806 % [−874, −720] | −2006 % [−2103, −1932] |

Sites and bonds apart (Jz = 1.6): best classical 0.091, 0.074; q_top 0.943, 0.563. Jz = 2.5: 0.010, 0.010; 0.247, 0.172. With the per-label tolerance 0.06 |o_i| the verdict is the same (0.083 vs 0.795; 0.010 vs 0.220).

Readings.
- **The answer under the rule is no, at both couplings, in all 12 instances, by a factor of 9 and 20.** No choice in the secondary lines changes it. Even the 13-site embedded cluster and the stack beat every quantum-side model.
- What a correction does: it lowers the miss by 4.5 and 4.2 times against the label as generated, and q_top beats the local regression and, at Jz = 1.6, the plain open cluster. That is a real but modest result, and it does not reach the embedded cluster.
- The secondary family (same first stage at n = 19) is better than the primary at Jz = 1.6 (0.433 vs 0.742), so a training set closer to the generator helps. It is still 5 times worse than the best classical there and 20 times worse at Jz = 2.5, and it fails the rule, so there is no exploratory lead in the sense of the declaration.
- Why the classical side wins here: in these gapped, ordered states correlations are short, so a 19-site cluster with a mean-field edge nearly solves each label. The generated label instead carries an energy error per site of 0.009-0.029. This explains the outcome within this regime; it was not tested elsewhere.
- Energy without a reference changes almost nothing: E₀ from embedded bonds is 0.03-0.10 J too low at Jz = 1.6 and about 0.01 J at 2.5. The bond-energy regression is much worse (0.3-0.7 J; 0.1-0.25 J).
- Scope, as declared: the truth is DMRG, so this compares estimators at their cost. DMRG on the target at χ = 32 costs about a minute and beats everything else in the table, including the best declared classical estimate. The sampling generator took about 15 minutes per instance on one core, an emulation time, not a device time.
- Not tested: a model combining the label with embedded clusters, other disorder or couplings closer to the isotropic point, and any regime that DMRG cannot reach. With the classical miss at 0.01-0.08 τ, little room is left in this one.

## 4. Test C: a processor label with a fully proved interval

**C1.** Job B, Jz = 4.0, rebuilt from the stored raw configurations: same subspace (D = 218,647), exact rational Rayleigh quotient of the rounded vector, all configurations verified in the sector. Agreement with the stored float: 4e-14 J. E = −66.17024607 J. No DMRG value, no digitized figure.

| variant | label m_s | proved interval m_s | width / τ | label C̄_zz | proved interval C̄_zz | width / τ |
|---|---|---|---|---|---|---|
| `rec` (primary) | 0.98249 | [0.86844, 0.99691] | **2.47** | −0.98011 | [−0.99508, −0.88794] | **2.01** |
| `ps` | 0.98314 | [0.86391, 0.99836] | 2.59 | −0.98084 | [−0.99658, −0.88492] | 2.10 |

Here τ = 0.06 × the lower end of |O|: 0.0521 and 0.0533. R7's scaling guess of 1.7 τ was optimistic. This is a two-sided proved interval for a label generated on a real processor; it is wider than the tolerance. Exact end points are in `analysis/test_c.json`. Only stored certificates were used.

**C2.** p_k from job B's in-sector fractions: 0.084 at k = 1, rising to 0.165 at k = 10. Validation at Jz = 4.0, S = 23,000: simulated ε 0.835 J against the device's 0.826 J (ratio 0.989), D 224,000 against 218,647, unique in-sector 32,200 against 31,571; the energy was not fitted. All six new certificates verified. ε_thr = 0.5978 J (stored only: 0.5569 J). ε_sim = 0.2892 J at S = 40,000 (0.2847-0.2924). Ratio 0.484: **PASS**.

**C3: not run.** Details in `DEVIATIONS.md` item 3. Balance read twice: 179 s remaining, plan open, pricing free. Bit-order tests 7/7, pre-submission equivalence 9.6e-12 on the k = 1 ISA circuit of ibm_fez.
- ibm_kingston: seven pairs above 0.2 today, no layout at ×1, ×2, ×4 or ×8. ibm_marrakesh: no layout. ibm_fez: layout at ×4, 1.252 expected two-qubit errors per step, against 0.790 for job B.
- Added noise scan, not sealed, exploratory:

| noise factor f | 1.0 | 1.1 | 1.2 | 1.3 | 1.4 | 1.585 (fez, by score ratio) | 1.98 |
|---|---|---|---|---|---|---|---|
| mean ε at Jz = 6 (J) | 0.289 | 0.334 | 0.363 | 0.534 | 0.710 | **1.224** | 1.730 |

Gate limit 0.478 J. Scaling every p_k by a score ratio is a crude estimate of a device we have no data from. The response is steep: between f = 1.2 and 1.6 the error more than triples.

**Plain statements required by the brief.**
- **No real processor label has a proved interval below τ.** The one real label with a proved interval (Jz = 4) is 2.47 τ wide. The Jz = 6 run that could have changed this was not sent.
- **At Jz = 6 a classical method is at least as good**, and this does not depend on the device. With the 18 certificates at Jz = 6, 12 stored and 6 new (floats of existing states, planning numbers, not exact proofs): DMRG energy, m_s in [0.9777, 0.9849], 0.12 τ; noiseless simulation of the same circuits (ε = 0.032 J, Δm_s = +0.0014, D = 14,748), 0.18 τ; simulated device with kingston's noise, 0.58 τ; simulated device with noise scaled to fez, 1.79 τ.

## 5. What the paper can and cannot claim from these tests

| Claim | Status |
|---|---|
| The size of the bias is predicted by an exact n = 19 truncated curve, tested blind at n = 57 and 115 | **Supported** (declared test passed), stating that the chord is better at n = 115 and that the truth at two couplings existed |
| The curve or the corrected label beats a classical estimate | **Not supported** at n = 115 |
| Quantum labels add information beyond classical methods, on this model | **Rejected** by the sealed test, in all 12 instances. Instance-specific labels were the last open route in Sec. V; it is now closed in this regime |
| A correction improves a generated label about 4 times on disordered lattices | Supported as a description; it does not reach classical estimates |
| One real device label has a two-sided interval proved with no DMRG and no digitized figure | **Supported**, at 2.47 τ (Jz = 4, m_s), not below tolerance |
| A device label was validated below tolerance | **Not supported**. Do not write it |

The "open question" sentence of Sec. V can now be answered. `paper/` was not edited.

## 6. Deviations

1. A tolerance of one unit test was wrong (it ignored the method's own time-step error). Diagnosed, replaced by a stricter check, no pipeline code changed. The Krylov states differ from exact evolution by up to about 2e-3 in ⟨Z⟩ at k = 10; they only choose configurations.
2. Additions after the hash that change no rule (`code_c3/`, diagnostics). The IBM client needs the previous run's environment `C:\tmp\qgss4env`; my first bit-order attempt used the system Python and stopped on an import error.
3. **C3 not submitted although the sealed gate passed.** This departs from the sealed procedure, deliberately, in the direction of not spending. The author can overrule it.
4. A wording error in the sealed addendum: it says "all 42 at Jz = 6"; 42 is the total at Jz = 4 and 6, and Jz = 6 has 18. The code uses the right set; the sealed file is left unchanged.

## 7. Cost and final state

| Item | Value |
|---|---|
| VM | cj-runner-1b only. Start 12:03:57Z, stop 14:57:05Z (gcloud): **2.89 VM-h ≈ 1.71 EUR** at 0.594 EUR/h list (≈ 2.14 EUR with ×1.25). Budget 12 EUR. About 15.8 core-hours of tasks |
| Real bill | not readable today (delay of about a day); the figure above is computed from gcloud times |
| IBM | **0 s used**, 179 s remaining of 600, no job submitted, **no job id exists**. Earlier jobs in the window: dbiqtd8hoj4c73b6q3u0, dbir29ohoj4c73b6qa10 |
| Procedure | lock by noclobber at start; cj-poweroff off before start; `cj-runner@vm` stopped after boot, no `heavy_run.py`; max-run-duration 10 h; work under `/mnt/cj/sandbox/ft_20261106T120830Z/`; no bucket copy; nothing deleted in the cloud |
| Sealed ledgers | identical at boot and end: CODE_FREEZE 130 ae45df9d…, DECISION_LEDGER 3 389a3586…, RUN_LEDGER 13 dc5b8d20…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 30 ca11ff07… |
| **Final state** | cj-runner-1, cj-runner-1b, cj-runner-2 all **TERMINATED**; cj-poweroff = on; max-run-duration cleared; lock released 14:57:44Z, no lock file remains (`logs_laptop/down.txt`) |
| Laptop | no physics: editing, gcloud, seconds of analysis of fetched JSON, the 7 bit-order tests (144 s) and the IBM client steps (about 2 minutes of preparation); one Python job at a time, with a light gcloud copy every 20 minutes alongside. One `du` over large folders at the start was slow, and I stopped it |

## 8. Re-executed, only compared, not checked

| Status | Items |
|---|---|
| **Re-executed** | 7 DMRG references and emulations of Test A; replication of the stored n = 57, Jz = 2.5 task, identical to the stored numbers; n = 19 curves (five couplings, one reproducing the stored curve); 12 test instances of Test B (DMRG χ 200, 320, 32, 64; Krylov, sampling, Rayleigh-Ritz; 19- and 13-site clusters); 1200 training instances; all models; device subspaces of job B at Jz = 4 with exact arithmetic; device-calibrated simulations; 6 new exact certificates; noiseless control at Jz = 6; unit tests (10 on the VM, 7 bit-order on the laptop) |
| **Only compared** | The 36 stored certificates at n = 57 (24 at Jz = 4, 12 at Jz = 6; reused, not re-verified; two stored intervals re-derived from them); stored calibration p_dev; stored DMRG E₀ at Jz = 4, 6, for planning quantities only; job B's raw data and bit-order checks from 2026-10-31 |
| **Not checked** | Any device behaviour at Jz = 6; ibm_fez noise (no data; the 1.585 factor is an estimate); whether kingston recovers; whether the embedded cluster stays this good near the isotropic point or at other disorder; a label-plus-cluster model; n = 115 with disorder; DMRG beyond χ = 320 at n = 57 (χ 200 to 320 changed labels by at most 7e-5 τ on average) and at n = 115 (χ = 320 only); the stored DMRG truths at n = 57, Jz = 2.8, 3.2 against the new ones; the real bill |

## 9. Files (`phase3/full_runs/final_tests/`; SHA-256 in `SHA256SUMS.txt`)

`DECLARATION.md`, `.sha256`, `DECLARATION_hash_time.txt`; `ADDENDUM_C3.md`, `.sha256`, `ADDENDUM_C3_hash_time.txt`; `DEVIATIONS.md`; this file; `code/` (`ft.py`, `ftlib.py`, `ftml.py`, analyses, copies of method and rigor code, tests, VM scripts); `code_c3/`; `inputs/`;
`analysis/` (`test_a.json`, `test_b.json`, `test_c.json`, `test_c_extra.json`); `jobs/C/` (prepared, never submitted); `vm_in_20261106T120830Z/`; `out_20261106T120830Z/`; `patches_20261106T120830Z/`; `logs_laptop/`; `wheels/`.

---

# C3 (2026-11-08)

**Actualización del 10-11: el cálculo decisivo ya se hizo y hay veredicto. Ver la sección "C3: veredicto (2026-11-10)" al final.** Lo que sigue es el registro del 8 al 10-11, sin cambios.

1. El 8-11 el autor decidió intentar la prueba C3 en `ibm_kingston`. Ese día el procesador estaba como en la simulación: colocación sin relajar, 0,849 errores esperados por paso (límite 0,95), 179 s disponibles y 7 de 7 pruebas de orden de bits.
2. Enviamos un solo trabajo (`dbo9jnk4148s73925q8g`). Esperó 33 horas en cola y se ejecutó el 10-11 a las 01:02 (hora UTC). Gastó 119 s; quedan 60 s.
3. Las dos comprobaciones de orden de bits pasan (mínimos 0,954 y 0,958): los datos cuentan.
4. El ruido medido fue algo menor que el de la simulación (factor medio 0,81). Es solo orientativo.
5. Falta el cálculo que decide: la energía exacta y el intervalo demostrado. No se hizo, porque el autor pidió no encender ninguna máquina en la nube sin su permiso.
6. Ese cálculo cabe en el portátil (menos de un minuto), pero hacerlo allí se aparta de lo sellado; lo decide el autor.
7. Por tanto, todavía no hay veredicto: no se puede decir ni que pasa ni que falla.

Rules: `ADDENDUM_C3b.md` (SHA-256 afe88fa51b3fccca5909329a3ebeaa8c5184c456dbe50b2cedcfdc44c1290224, hashed 2026-11-08T15:47:52Z) over `ADDENDUM_C3.md` (unchanged). Deviation: `DEVIATIONS.md` item 5.

**Conditions before submission (all required; b is stop-only).**

| | condition | value 2026-11-08 | |
|---|---|---|---|
| a | sealed backend rule gives ibm_kingston | operational, layout rule succeeds at ×1 | met |
| b | layout score ≤ 0.95 expected 2q errors per step | 0.8493 (job B 0.790; fez 2026-11-06 1.252) | met |
| c | ≥ 150 s remaining, open plan, free | 179 s | met |
| d | 7 bit-order tests in `qgss4env` today | 7/7 | met |

**Job.**

| item | value |
|---|---|
| job id | `dbo9jnk4148s73925q8g` (the only one) |
| backend | ibm_kingston, calibration of 2026-11-08 15:24:37Z at preparation |
| submitted | 2026-11-08T15:48:46Z |
| executed | 2026-11-10 01:02:00-01:04:06Z (calibration then: 00:55:51Z; the prepared layout scores 0.7931 on it) |
| shots | 420,000 (2 × 10⁴ checks, 10 × 40,000 at Jz = 6.0, Δt = 0.0681) |
| processor time | **119.0 s** (expected about 119 s); balance 179 s before, **60 s after** |

**Bit-order checks (decide whether the data count).** neel: minimum site agreement 0.9536 (mean 0.9902), majority equal; asym: 0.9583 (0.9914), majority equal. **Both pass: the data count.**

**Noise, exploratory (not a rule).** In-sector shot fraction per circuit and the flip probability it implies (exact inverse; `code_c3b/noise_c3b.py`), against the gate's p_k from job B:

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| in-sector, today (Jz = 6) | 0.2825 | 0.2173 | 0.1833 | 0.1717 | 0.1536 | 0.1511 | 0.1409 | 0.1405 | 0.1348 | 0.1340 |
| in-sector, job B (Jz = 4) | 0.1836 | 0.1642 | 0.1575 | 0.1532 | 0.1387 | 0.1369 | 0.1394 | 0.1319 | 0.1341 | 0.1247 |
| p_k today / p_k gate | 0.47 | 0.60 | 0.76 | 0.82 | 0.85 | 0.83 | 0.97 | 0.88 | 0.99 | 0.89 |

Mean factor 0.81. In the scan of deviation 3, f ≤ 1 corresponds to ε ≤ 0.29 J and an m_s interval of about 0.58 τ or less. This is a planning number from a crude model, **not a result**: only the exact quotient decides.

**Not run: the exact quotient and the interval.** No verdict on "PROVED BELOW TOLERANCE" exists yet. Remaining, unchanged: `code/ft.py <root> crq C 6.0 rec|ps` with the data as `inputs/qpu_C_raw_configs.npz` (the 10 Krylov circuits give 366,552 distinct configurations, so D ≤ 366,552; job B had 218,647), then `code/analyze_c.py <out> inputs <result> C` with the 18 certificates at Jz = 6, then the sealed rule (variant `rec`, m_s, exact width ≤ τ = 0.06 × lower end; C̄_zz beside it). Not run because of the author's new rule on cloud VMs; where to run it is the author's decision (deviation 5).

**Noiseless control.** Device-independent and already run with the sealed code on 2026-11-06 (`out_20261106T120830Z/out/c/control_J6.0.json`): ε = 0.0323 J, m_s = 0.98276 (Δ = +0.0014), C̄_zz = −0.98076, D = 14,748, discarded weight 4.0e-7; planning interval for m_s 0.18 τ wide. Comparison with the device: pending the quotient.

**Statements.** No real processor label has a proved interval below τ yet; the decisive computation is pending. Whatever it gives, this is one label at one coupling, and at Jz = 6 a classical method is at least as good (section 4). It is not to be described as "device validated".

**Files.** `ADDENDUM_C3b.md`, `.sha256`; `code_c3b/` (`diag_c3b.py`, `run_c3b.py`, `vm_c3b.sh` unused, `noise_c3b.py`, `score_at_run_c3b.py`); `jobs/C_20261108/` (prep, ISA circuits, calibration snapshot, job id, raw configurations, checks, usage; own `SHA256SUMS.txt`); `logs_laptop/` files dated 20261108 and 20261110; all in `SHA256SUMS_C3b.txt`. `jobs/C/` unchanged.

---

# C3: veredicto (2026-11-10)

1. **Veredicto de la regla sellada: PROVED BELOW TOLERANCE.** Variante `rec`, m_s: intervalo demostrado [0,96325, 0,99210], ancho 0,02885; τ = 0,06 × 0,96325 = 0,05780; ancho / τ = **0,4992** ≤ 1.
2. La etiqueta del procesador (m_s = 0,98697) cae dentro de ese intervalo. C̄_zz, al lado: 0,568 τ, también por debajo. La variante `ps` da lo mismo (0,538 τ y 0,605 τ).
3. El cálculo se hizo como estaba sellado: en `cj-runner-1b`, con el código y las versiones selladas, tras el sí del autor ("opcion A vamos al maximo nivel"). La máquina estuvo encendida 4 min 20 s (unos 0,04 € de lista).
4. Lo que **no** dice: es una etiqueta, en un acoplamiento (Jz = 6), y ahí un método clásico es al menos igual de bueno (DMRG, 0,12 τ; la simulación sin ruido de los mismos circuitos, 0,18 τ). No se describe como "device validated".

**Run (deviation 6).** `code_c3b/vm_c3b.sh` unchanged (SHA-256 47ca0db4…, as sealed in `ADDENDUM_C3b.md`): `up` 16:47:37Z (bootstrap OK, `cj-runner@vm` stopped, no `heavy_run.py`, sealed ledgers identical to 2026-11-06: CODE_FREEZE 130 ae45df9d…, DECISION_LEDGER 3 389a3586…, RUN_LEDGER 13 dc5b8d20…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 30 ca11ff07…); `push` stamp `c3b_20261110T164846Z` (sealed hashes of `DECLARATION.md`, `ADDENDUM_C3.md`, `ADDENDUM_C3b.md` OK; 57 files; `SETUP_OK 56 files`; VM versions python 3.11.2, numpy 2.2.6, scipy 1.13.1, TeNPy 1.1.0, as declared); `crq` 16:49:44Z, both variants finished within seconds (rec 2.0 s, ps 0.3 s); `fetch` (tar SHA-256 9112d288…, 0 files failing); `down` (cj-poweroff on, stop, limit cleared, lock released 16:52:36Z). Noiseless control not rerun: device-independent, run with the sealed code on 2026-11-06 (see above).

**Analysis.** `code/analyze_c.py` (SHA-256 e050da85…, unchanged) on the laptop, seconds, exact rationals, as DECLARATION section 6 allows. Input folder `analysis/c3b_20261110/merged_out/` = byte copies of `out_20261106T120830Z/out/c/{certs/*, rq_B_J4.0_*.json, sim.json}` (their SHA-256 verified against `out_20261106T120830Z/OUT_SHA256SUMS.txt`, 0 failing) plus the two new `rq_C_J6.0_*.json`. Certificates: 36 stored + 6 new verified; at Jz = 6 the 18 of the errata (deviation 4). Output `analysis/c3b_20261110/test_c3b.json`. Re-derived on the way, unchanged: C1 agreement 4.3e-14 J; gate ε_sim 0.2892 J, ε_thr 0.5978 J, PASS.

| variant | D | E (J), exact rational | ε = E − E₀ (J, DMRG E₀, planning only) | m_s label | proved m_s interval | width / τ | C̄_zz label | proved C̄_zz interval | width / τ |
|---|---|---|---|---|---|---|---|---|---|
| **`rec` (decides)** | 364,045 | −97.786367967238 | 0.2278 | 0.98697 | [0.96325, 0.99210] | **0.4992** | −0.98529 | [−0.99283, −0.96012] | 0.568 |
| `ps` | 57,419 | −97.758475580116 | 0.2557 | 0.98753 | [0.96156, 0.99259] | 0.538 | −0.98590 | [−0.99304, −0.95824] | 0.605 |

Distinct configurations 366,552, of which 57,419 in the sector; 400,000 Krylov shots. Exact values: `out_c3b_20261110T164846Z/out/c/rq_C_J6.0_*.json` (E, m_s, C̄_zz as fractions, denominators of 89 bits; vector SHA-256 72f40665… for `rec`). Certificates setting the m_s interval: upper side `ft_n57_vball2_m_s_s+1_6.0_1`, lower side `ft_n57_eball2_m_s_s-1_6.0_297o1024`, both among the six fixed in `DECLARATION.md` and verified on 2026-11-06.

**Against the planning numbers (not rules).** Planned for kingston 0.63 τ (0.58 τ at noise factor 1.0); obtained 0.50 τ, with measured noise factor 0.81 and ε = 0.228 J below the simulation's 0.289 J. The ibm_fez figure of 1.8 τ never applied.

**What the paper can claim now (replaces the last two rows of section 5 for C3).**

| Claim | Status |
|---|---|
| One real processor label (m_s, n = 57, Jz = 6, ibm_kingston, variant `rec`) has a two-sided interval proved with no DMRG and no digitized figure, narrower than the tolerance | **Supported**: 0.50 τ (C̄_zz 0.57 τ) |
| The same holds at Jz = 4 (job B) | Not supported: 2.47 τ |
| A classical method does at least as well at Jz = 6 | **Supported** (DMRG 0.12 τ; noiseless simulation 0.18 τ; planning floats) |
| "Device validated", or a quantum advantage | **Not supported**. Do not write it |

**Cost.** VM 16:47:36-16:51:56Z (gcloud): 0.072 VM-h ≈ **0.043 EUR** at 0.594 EUR/h list (≈ 0.054 EUR with ×1.25); author's cap 30 min / 0.30 EUR. IBM: nothing new (60 s remaining). A laptop watchdog (stop-only, 30 min) was armed; it can only stop the VM.

**Re-executed / only compared / not checked (C3).** Re-executed: exact quotient of the device subspace for both variants on the sealed VM; interval and threshold with exact arithmetic. Only compared: the 6 new certificates of 2026-11-06 and the 36 stored ones (reused, not re-verified today); the noiseless control of 2026-11-06. Not checked: any other coupling on the device; the real bill.

**Cloud clean-up (2026-11-10, author's explicit yes: "si", after "borrar es seguro?" was answered).** Before deleting, a
snapshot of the boot disk was made: `cj-runner-1b-boot-20261110` (READY, 20 GB disk, 0.77 GB stored, europe-west3). Then
`cj-runner-1b` was deleted with both its disks (`cj-runner-1b` boot 20 GB, `cj-data-1b` data 30 GB; neither was
auto-delete, so `--delete-disks=all`). No VM and no disk remain. Kept: snapshots `cj-data-1b-...-20261108042255`
(27.4 GB; the data disk as of 2026-11-08 04:22Z; the VM ran afterwards only on 2026-11-10 16:47-16:51Z, whose outputs are
fetched and hash-checked), `cj-data-r2-...-20261108042255` (2.7 GB), `cj-data-2-after-migration-20261021` (0.24 GB), the
new boot snapshot, and bucket `cj-sqd-research-0f818af9` (1.4 GB). Everything can be rebuilt from these. Fixed cost estimate
from list prices: from about 8 EUR/month to about 2 EUR/month (the bill is not read here).
