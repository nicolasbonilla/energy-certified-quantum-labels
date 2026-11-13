# Real data of arXiv:2606.15983: RESULTS of the learning tests on the real labels (declaration Sec. 7: f1, f2, f3)

Task `rd-learn`, 2026-11-12. Declaration: `real_data/DECLARATION.md`, SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa` (checked before anything was read).
Every outcome below is the output of the sealed code `code/run_learn.py` (and its sealed helpers), run unchanged. No rule was changed.
Nested sets and label intervals: `out/S_sets.json`, SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4` (written by the map task before any learning number; equal to `out/S_sets.sha256`).

## Resumen en español (ocho líneas)

1. Se comprobó que la declaración sellada no había cambiado (su huella coincide) y que el archivo de conjuntos ya estaba escrito, con su huella, antes de calcular nada. El programa sellado se ejecutó tal cual, sin tocarlo.
2. Modelo entrenado con las etiquetas reales: fuera del rango de entrenamiento falla el valor verdadero por entre 2,28 y 3,73 veces la tolerancia a 57 cúbits (entre 2,37 y 5,07 a 115), y los intervalos de confianza habituales no contienen el valor verdadero en ninguna de las cuatro constantes de prueba. Las tres predicciones L1, L2 y L3 SE CUMPLEN.
3. Dentro del rango de entrenamiento esos intervalos habituales contienen 41 de 45 etiquetas nuevas, pero el valor verdadero en 0 de 45 (57 cúbits) y en 11 de 45 (115): aciertan la etiqueta y fallan la verdad.
4. Control con etiquetas de referencia (el cálculo clásico de los autores): dentro del rango contiene la verdad en 41 de 45; fuera del rango tampoco la contiene (0 de 4), aunque falla por poco (entre 0,02 y 0,25 de la tolerancia). Por eso L2 sola no separa «etiquetas sesgadas» de «extrapolación»; lo que las separa es el tamaño del fallo (L1).
5. Suelo que no depende del modelo (f2): calibrando con las 45 etiquetas, ningún método puede dar un intervalo garantizado más estrecho que 5,35 tolerancias en las constantes de prueba a 57 cúbits (4,65 a 115). SE CUMPLE. Con los intervalos de energía de las 45 etiquetas, el intervalo del modelo cúbico mide como mínimo entre 6,71 y 11,08 tolerancias, según la constante (L3).
6. Prueba constructiva (f3), conjunto principal (las 18 etiquetas certificadas a media tolerancia, Jz de 4,3 a 6,0, 57 cúbits): PASA. Intervalos de entre 0,56 y 0,86 tolerancias en 200 de 200 particiones y el valor verdadero dentro en 1000 de 1000 casos, con los dos modelos declarados. A 115 cúbits (21 etiquetas, de 4,0 a 6,0): PASA.
7. Con el mismo relieve: a 57 cúbits, en el conjunto completo de etiquetas certificadas (26) y en el intermedio (23) NO PASA, por anchura (solo 6 y entre 50 y 66 de 200 particiones); el modelo de control, entrenado también con etiquetas sin certificar, pasa igual que los otros; y en el rango del conjunto principal el valor verdadero cambia solo 0,30 tolerancias. La prueba muestra que la garantía sobrevive al aprendizaje, no que se haya aprendido una función difícil.
8. Un segundo programa, escrito aparte, reproduce estos números (diferencia máxima 7e-11). No se halló ningún defecto en el programa sellado ni se cambió regla alguna. Quedan sin calcular, por coste, la red pequeña dentro del rango y a 115 cúbits y la red grande del artículo original (de la red pequeña solo hay las cuatro constantes de prueba a 57 cúbits). Dos comprobaciones de la tarea del mapa siguen incompletas (G1 y la primera parte de G6).

## Summary (English)

| analysis | declared rule | outcome |
|---|---|---|
| L1, n = 57 (decides) | the cubic misses the true m_s by more than tau at each of 1.1-1.4 | **HOLDS** (3.72, 3.17, 2.69, 2.29 tau) |
| L2, n = 57 (decides) | standard intervals calibrated on the real labels cover the truth at none of the four test couplings | **HOLDS** (covered at 0 of 4) |
| L3, n = 57 (decides) | the 2(b) intervals calibrated on all 45 labels are wider than tau at every coupling (lower version) | **HOLDS** (2q = 6.71-11.08 tau over the 49 couplings) |
| L1, n = 115 (reported) | the cubic misses the true m_s by more than tau at each of 1.1-1.4 | **HOLDS** (5.06, 3.85, 2.99, 2.38 tau) |
| L2, n = 115 (reported) | standard intervals calibrated on the real labels cover the truth at none of the four test couplings | **HOLDS** (covered at 0 of 4) |
| L3, n = 115 (reported) | the 2(b) intervals calibrated on all 45 labels are wider than tau at every coupling (lower version) | **HOLDS** (2q = 5.92-9.40 tau over the 49 couplings) |
| (f2) floor, n = 57 | the floor w_(42) of the 45 lower widths exceeds tau(x) at each test query | **HOLDS** (floor = 6.42 / 5.97 / 5.62 / 5.35 tau at 1.1-1.4; at least 3.89 tau at every coupling) |
| (f2) floor, n = 115 | the floor w_(42) of the 45 lower widths exceeds tau(x) at each test query | **HOLDS** (floor = 5.49 / 5.14 / 4.86 / 4.65 tau at 1.1-1.4; at least 3.46 tau at every coupling) |
| (f3) **PRIMARY**, n = 57, set S_1/2 = S_p (18 couplings, Jz 4.3-6.0; 4 train / 9 calibration / 5 query) | (W) 2q <= tau(x) at every query in >= 90 % of the splits and (C) truth within q in >= 90 % of the pairs, both M1 and M2 | **PASS** (M1: (W) 200 of 200 splits, (C) 1000 of 1000 pairs, 2q = 0.586-0.857 tau, largest miss 0.137 tau; M2: (W) 200 of 200 splits, (C) 1000 of 1000 pairs, 2q = 0.562-0.856 tau, largest miss 0.149 tau) |
| control M0 on the same splits | same rule | **PASS** ((W) 200 of 200, (C) 1000 of 1000, 2q = 0.599-0.761 tau, largest miss 0.090 tau) |
| (f3) secondary, n = 57, set S_3/4 (23 couplings, Jz 3.8-6.0; 6 train / 12 calibration / 5 query) | (W) 2q <= tau(x) at every query in >= 90 % of the splits and (C) truth within q in >= 90 % of the pairs, both M1 and M2 | **FAIL** (M1: (W) 50 of 200 splits, (C) 1000 of 1000 pairs, 2q = 0.815-1.163 tau, largest miss 0.157 tau; M2: (W) 66 of 200 splits, (C) 1000 of 1000 pairs, 2q = 0.822-1.137 tau, largest miss 0.137 tau) |
| control M0 on the same splits | same rule | **FAIL** ((W) 50 of 200, (C) 1000 of 1000, 2q = 0.817-1.083 tau, largest miss 0.121 tau) |
| (f3) secondary, n = 57, set S (26 couplings, Jz 3.5-6.0; 6 train / 12 calibration / 8 query) | (W) 2q <= tau(x) at every query in >= 90 % of the splits and (C) truth within q in >= 90 % of the pairs, both M1 and M2 | **FAIL** (M1: (W) 6 of 200 splits, (C) 1600 of 1600 pairs, 2q = 0.906-1.564 tau, largest miss 0.212 tau; M2: (W) 6 of 200 splits, (C) 1600 of 1600 pairs, 2q = 0.916-1.546 tau, largest miss 0.211 tau) |
| control M0 on the same splits | same rule | **FAIL** ((W) 6 of 200, (C) 1600 of 1600, 2q = 0.889-1.432 tau, largest miss 0.156 tau) |
| (f3) secondary, n = 115, set S_1/2 | (W) and (C) for M1 and M2 | NOT RUN: 10 couplings, fewer than 15 |
| (f3) secondary, n = 115, set S_3/4 = S_p (21 couplings, Jz 4.0-6.0; 6 train / 12 calibration / 3 query) | (W) 2q <= tau(x) at every query in >= 90 % of the splits and (C) truth within q in >= 90 % of the pairs, both M1 and M2 | **PASS** (M1: (W) 200 of 200 splits, (C) 600 of 600 pairs, 2q = 0.862-0.985 tau, largest miss 0.122 tau; M2: (W) 200 of 200 splits, (C) 600 of 600 pairs, 2q = 0.865-0.991 tau, largest miss 0.131 tau) |
| control M0 on the same splits | same rule | **PASS** ((W) 200 of 200, (C) 600 of 600, 2q = 0.858-0.965 tau, largest miss 0.068 tau) |
| (f3) secondary, n = 115, set S (21 couplings, Jz 4.0-6.0; 6 train / 12 calibration / 3 query) | (W) 2q <= tau(x) at every query in >= 90 % of the splits and (C) truth within q in >= 90 % of the pairs, both M1 and M2 | **PASS** (M1: (W) 200 of 200 splits, (C) 600 of 600 pairs, 2q = 0.859-0.999 tau, largest miss 0.109 tau; M2: (W) 199 of 200 splits, (C) 600 of 600 pairs, 2q = 0.869-1.028 tau, largest miss 0.117 tau) |
| control M0 on the same splits | same rule | **PASS** ((W) 200 of 200, (C) 600 of 600, 2q = 0.864-0.963 tau, largest miss 0.067 tau) |
| (f1) models | cubic, nearest-neighbour null, pilot perceptron, architecture 1 (n = 57, test range) | cubic and null: complete at both sizes. Perceptron: test range at n = 57 only. **Not computed (cost):** perceptron in distribution and at n = 115; architecture 1 (Sec. 3.6). L1-L3 are decided on the cubic (declaration Sec. 12, line 10). |

**Gate notes, printed with every result (declaration Sec. 12, line 14).** G1 is NOT COMPLETE: the converter was not re-run on the pinned archive; the converted files have the pinned SHA-256 (checked by the sealed loader at every read). The first part of G6 is NOT COMPLETE with nothing checked (no tensors on the laptop): it concerns every number of the *lower version* (the floor of f2, L3, W_lo and 2q_lo of Proposition 2), because the explicit-state interval of 33 (n = 57) and 33 (n = 115) of the 45 training labels rests on energies re-evaluated by the linear rule H = A + Jz B (flag `rests_on_re_evaluated_energy` of the map rows). G2, G3, G4, G5, the second part of G6 and G7 passed in the map task. The exact intervals used by (f3) rest on certificates (G5) and do not depend on G6.

**Hypothesis behind every exact interval (declaration Sec. 10, item 6):** the published energy and the published site magnetizations are expectation values of one and the same state.

**The limit that the declaration requires with the result of (f3):** between Jz = 4 and 6 the true m_s changes by 0.4 tau (measured here: 0.388-0.398 tau at n = 57, 0.364-0.373 at n = 115; over the primary set, Jz = 4.3-6.0, 0.294-0.301 tau). The test shows that the intervals survive the learner and its calibration where labels are certified. It does not show that a hard function was learned.

Marks on numbers: **[S]** already seen before the hash (item of declaration Sec. 1 in brackets); **[M]** fixed by the map task after the hash and before any learning number (the sets and the label intervals); **[N]** not seen and not computed before the hash. Unless marked otherwise, every learning number below is **[N]** (declaration Sec. 1: no learning result on real labels and no interval width at a real energy had been seen).

## 1. What was run

- `DECLARATION.sha256` equals the SHA-256 of `DECLARATION.md` (`sha256sum`, the gate of the sealed code, and this script). `python -B -I checks/make_manifest.py --check` before the runs: 69 lines of Sec. 11 equal to the files on disk, 0 different, 4 not re-hashed there. Hashed again by this script after the runs: 64 plain-file lines of Sec. 11 equal, 0 different (the archive under `source/` was not re-hashed; tree digests not recomputed here).
- `out/S_sets.json` existed with SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4`, equal to `out/S_sets.sha256` and to the value announced by the map task, before any learning number was computed; the sealed stages `prop2`, `f2`, `f3` refuse to run otherwise.
- Command 1: `python -B -I code/run_learn.py --hash=6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa --stage=cheap` (stages f1_cheap, prop2, f2, f3, rules), 2026-11-12T19:55:38Z to 2026-11-12T19:56:28Z UTC. Seed 1845216616 (first eight hex digits of the hash).
- Command 2: `python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=... --model=mlp_pilot3 --size=57 --part=ood` (the perceptron, test range, real and DMRG labels; 92 fits), 2026-11-12T19:55:35Z to 2026-11-12T20:25:33Z UTC (19.5 s per fit on the shared laptop).
- Python 3.11.4, numpy 1.26.4, scipy 1.13.1 (as at gate G8), one thread per process, laptop only.
- Sealed code, hashed again after the runs and equal to Sec. 11: `code/run_learn.py` `8332d1f06289...`, `code/rd_f23.py` `3512c2206936...`, `code/rd_learn_ibm.py` `9c65738a9d8f...`, `code/rd_prop2_cubic.py` `694adaf0451e...`, `code/rd_learn_parts.py` `83e2d7fb54f5...`, `code/rd_common.py` `6efde0302f75...`.
- Outputs of the sealed code (`out/learn/`): `results_cheap.json`, `prop2_cubic.json`, `f2_floor.json`, `f3_constructive.json`, `f1_rules.json`, `parts/f1_mlp_pilot3_n57_ood.json`; copied verbatim into `out/learn_real.json` with provenance, the independent check and the post hoc lines under separate keys. SHA-256 of every file: `results/SHA256SUMS_learn.txt`.
- Truth in this section of the declaration: the authors' DMRG at all couplings (truth and tau(x) in L1-L3, (f2), (W), (C)); membership of S, S_3/4, S_1/2 uses the tau of Sec. 0 (Sec. 12, line 1).
- No code defect was found. Nothing listed in Sec. 11 was changed. Dated notes of this task: `DEVIATIONS.md`.

## 2. Inputs fixed before any learning number [M]

| size | set | couplings | Jz range | exact interval width (tau) | largest miss of a real label in the set (tau) [S, F7] | true m_s changes over the set by (tau) |
|---|---|---|---|---|---|---|
| 57 | S | 26 | 3.5-6.0 | 0.217-0.911 | 0.175 | 0.598-0.621 |
| 57 | S_3/4 | 23 | 3.8-6.0 | 0.217-0.701 | 0.121 | 0.462-0.476 |
| 57 | S_1/2 = **S_p** | 18 | 4.3-6.0 | 0.217-0.491 | 0.082 | 0.294-0.301 |
| 115 | S | 21 | 4.0-6.0 | 0.144-0.665 | 0.064 | 0.364-0.373 |
| 115 | S_3/4 = **S_p** | 21 | 4.0-6.0 | 0.144-0.665 | 0.064 | 0.364-0.373 |
| 115 | S_1/2 | 10 | 5.1-6.0 | 0.144-0.483 | 0.032 | 0.112-0.114 |

- S: training couplings whose m_s row is CERTIFIED (exact) with the reference tolerance, stored certificates only; S_3/4 and S_1/2: exact interval at most 3/4 and 1/2 of tau wide; S_p: the most stringent nested set with at least 15 couplings (decided before the hash).
- n = 57, Jz = 3.4 has an exact interval 1.0042 tau wide and is therefore not in S (S starts at 3.5). At n = 115, S = S_3/4 (the same 21 couplings; their splits differ, being drawn with different seeds).
- Exact intervals exist at 27 couplings (n = 57) and 21 (n = 115); explicit-state (lower) intervals at all 50 couplings of both sizes. The intervals of `out/S_sets.json` equal those of the m_s rows of `out/map_real.json` (largest difference 3.3e-16 at n = 57, 2.2e-16 at n = 115), and S equals the CERTIFIED (exact) training rows of that file (own check, Sec. 6).

## 3. (f1) The realistic test: standard conformal prediction on the real labels

Standard conformal, alpha = 0.1, plain jackknife over couplings. Test range: trained and calibrated on the 45 training labels, queried at Jz = 1.1-1.4. In distribution: each training coupling held out in turn (44 labels). m_s is derived from the per-site model. "New real labels" are the held-out real labels (test range: the real labels at 1.1-1.4). Width = 2q / tau(x). Control: the same pipeline trained and calibrated on the authors' DMRG labels.

### 3.1 Every model

| size | model | labels | range | new real labels covered (m_s) | truth covered (m_s) | sites: labels / truth covered | width 2q (tau), m_s | miss of the prediction (tau), m_s | queries missed by more than tau |
|---|---|---|---|---|---|---|---|---|---|
| 57 | cubic in 1/Jz (primary) | real | test 1.1-1.4 | 0 of 4 | **0 of 4** | 0.083 / 0.004 | 0.139-0.167 | 2.28-3.73 | 4 of 4 |
| 57 | cubic in 1/Jz (primary) | real | in distribution | 41 of 45 | **0 of 45** | 0.895 / 0.345 | 0.096-0.150 | 0.05-1.64 | 4 of 45 |
| 57 | cubic in 1/Jz (primary) | DMRG (control) | test 1.1-1.4 | n/a | **0 of 4** | n/a / 0.018 | 0.004-0.006 | 0.02-0.25 | 0 of 4 |
| 57 | cubic in 1/Jz (primary) | DMRG (control) | in distribution | n/a | **41 of 45** | n/a / 0.899 | 0.003-0.005 | 0.00-0.01 | 0 of 45 |
| 57 | nearest-neighbour null | real | test 1.1-1.4 | 0 of 4 | **0 of 4** | 0.079 / 0.000 | 0.619-0.744 | 3.10-7.06 | 4 of 4 |
| 57 | nearest-neighbour null | real | in distribution | 41 of 45 | **32 of 45** | 0.892 / 0.650 | 0.308-0.524 | 0.03-1.96 | 3 of 45 |
| 57 | nearest-neighbour null | DMRG (control) | test 1.1-1.4 | n/a | **0 of 4** | n/a / 0.000 | 0.799-0.960 | 1.30-4.90 | 4 of 4 |
| 57 | nearest-neighbour null | DMRG (control) | in distribution | n/a | **41 of 45** | n/a / 0.896 | 0.530-0.677 | 0.01-0.49 | 0 of 45 |
| 57 | pilot perceptron | real | test 1.1-1.4 | 2 of 4 | **0 of 4** | 0.127 / 0.000 | 0.290-0.350 | 2.65-6.42 | 4 of 4 |
| 57 | pilot perceptron | real | in distribution | not computed (cost) | not computed | not computed | not computed | not computed | not computed |
| 57 | pilot perceptron | DMRG (control) | test 1.1-1.4 | n/a | **0 of 4** | n/a / 0.000 | 0.027-0.034 | 0.27-2.41 | 2 of 4 |
| 57 | pilot perceptron | DMRG (control) | in distribution | not computed (cost) | not computed | not computed | not computed | not computed | not computed |
| 115 | cubic in 1/Jz (primary) | real | test 1.1-1.4 | 1 of 4 | **0 of 4** | 0.167 / 0.000 | 0.084-0.101 | 2.37-5.07 | 4 of 4 |
| 115 | cubic in 1/Jz (primary) | real | in distribution | 40 of 45 | **11 of 45** | 0.899 / 0.411 | 0.059-0.085 | 0.02-1.61 | 3 of 45 |
| 115 | cubic in 1/Jz (primary) | DMRG (control) | test 1.1-1.4 | n/a | **0 of 4** | n/a / 0.020 | 0.004-0.005 | 0.02-0.20 | 0 of 4 |
| 115 | cubic in 1/Jz (primary) | DMRG (control) | in distribution | n/a | **41 of 45** | n/a / 0.899 | 0.002-0.004 | 0.00-0.01 | 0 of 45 |
| 115 | nearest-neighbour null | real | test 1.1-1.4 | 0 of 4 | **0 of 4** | 0.026 / 0.000 | 0.306-0.363 | 2.84-6.40 | 4 of 4 |
| 115 | nearest-neighbour null | real | in distribution | 41 of 45 | **27 of 45** | 0.891 / 0.677 | 0.228-0.425 | 0.00-1.77 | 3 of 45 |
| 115 | nearest-neighbour null | DMRG (control) | test 1.1-1.4 | n/a | **0 of 4** | n/a / 0.000 | 0.730-0.864 | 1.19-4.45 | 4 of 4 |
| 115 | nearest-neighbour null | DMRG (control) | in distribution | n/a | **41 of 45** | n/a / 0.889 | 0.490-0.627 | 0.01-0.45 | 0 of 45 |
| 57 | architecture 1 of the dataset paper | real and DMRG | test 1.1-1.4 | not computed (cost) | not computed | not computed | not computed | not computed | not computed |
| 115 | pilot perceptron | real and DMRG | both | not computed (cost) | not computed | not computed | not computed | not computed | not computed |

Reading, with failures and passes side by side:

- **In distribution the standard intervals track the labels, not the truth.** Cubic, n = 57: 41 of 45 held-out real labels are covered (nominal level 0.9), the truth at 0 of 45; n = 115: 40 of 45 labels, the truth at 11 of 45. The intervals are 0.096-0.150 tau wide (n = 57), narrower than the bias of the labels.
- **In the test range nothing is covered.** Cubic on real labels: truth at 0 of 4 at both sizes; the real labels at 1.1-1.4 themselves at 0 of 4 (n = 57) and 1 of 4 (n = 115).
- **The control does not cover the truth in the test range either** (0 of 4 at both sizes): trained on DMRG labels the cubic misses the truth by 0.02-0.25 tau (n = 57) and 0.02-0.20 tau (n = 115) with intervals 0.004-0.006 tau wide. L2 therefore holds for the real labels *and* would hold for exact labels: by itself it does not separate biased labels from extrapolation error. What separates them is the size of the miss: 2.28-3.73 tau with the real labels (L1) against at most 0.25 tau with exact labels.
- In distribution the control behaves as designed: truth covered at 41 of 45 (n = 57) and 41 of 45 (n = 115), largest miss 0.0086 tau.
- Nearest-neighbour null, n = 57, in distribution: truth covered at 32 of 45 with intervals 0.308-0.524 tau wide (wide enough to contain the bias at large Jz); test range: 0 of 4, miss 3.10-7.06 tau.
- Pilot perceptron, n = 57, test range only: truth covered at 0 of 4, miss 2.65-6.42 tau with real labels; with DMRG labels it still misses by 0.27-2.41 tau (truth covered at 0 of 4): at these couplings the perceptron extrapolates poorly whatever the labels.

### 3.2 The cubic, coupling by coupling, with Proposition 2(a) and (b) at the real intervals

Columns: miss of the real label [S, F7]; miss of the cubic's prediction; standard interval 2q; whether it contains the truth / the held-out real label; Proposition 2(a) band W = sum_j |a_j(x)| width(I_j), lower version (explicit states) and upper version; Proposition 2(b) width 2q with the interval score, lower and upper version; rule (c) and band (a) of the stored design. All in units of tau(x). Training couplings: the query's own label is held out (44 labels). **Upper version: NOT AVAILABLE at any query** (the cubic is trained and calibrated on all training labels, and those below Jz = 3.4 (n = 57) or 4.0 (n = 115) have no exact interval); the upper numbers printed are indicative only (like-for-like outer or interpolated width) and can neither answer nor pin.

**n = 57**

| Jz | range | label miss [S] | cubic miss | standard 2q | truth / label in standard interval | W_lo (2a) | W_hi (2a, indicative) | 2q_lo (2b) | 2q_hi (2b, indicative) | upper interval of this label | rule (c) | band (a) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | test | 4.95 | 3.72 | 0.167 | no / no | 185.24 | 193.03 | 11.07 | 12.66 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.2 | test | 4.10 | 3.17 | 0.155 | no / no | 104.42 | 108.79 | 10.29 | 11.77 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.3 | test | 3.46 | 2.69 | 0.146 | no / no | 60.00 | 62.52 | 9.69 | 11.09 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.4 | test | 2.69 | 2.29 | 0.139 | no / no | 34.19 | 35.63 | 9.23 | 10.55 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.6 | train | 1.67 | 1.64 | 0.126 | no / yes | 15.48 | 16.07 | 7.35 | 7.92 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.7 | train | 1.43 | 1.42 | 0.150 | no / yes | 6.64 | 6.90 | 7.14 | 7.70 | interpolated | ABSTAIN | NOT_PINNED |
| 1.8 | train | 1.15 | 1.24 | 0.106 | no / no | 5.83 | 6.03 | 6.99 | 7.49 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.9 | train | 1.09 | 1.05 | 0.131 | no / yes | 5.10 | 5.26 | 6.81 | 7.37 | interpolated | ABSTAIN | NOT_PINNED |
| 2.0 | train | 0.89 | 0.92 | 0.113 | no / yes | 4.48 | 4.58 | 7.81 | 8.93 | like-for-like | ABSTAIN | NOT_PINNED |
| 2.1 | train | 0.86 | 0.79 | 0.101 | no / no | 4.45 | 4.57 | 7.66 | 8.77 | interpolated | ABSTAIN | NOT_PINNED |
| 2.2 | train | 0.75 | 0.69 | 0.101 | no / no | 4.19 | 4.30 | 7.56 | 8.66 | interpolated | ABSTAIN | NOT_PINNED |
| 2.3 | train | 0.64 | 0.61 | 0.124 | no / yes | 3.82 | 3.90 | 7.48 | 8.56 | interpolated | ABSTAIN | NOT_PINNED |
| 2.4 | train | 0.53 | 0.54 | 0.111 | no / yes | 3.42 | 3.49 | 7.42 | 8.48 | interpolated | ABSTAIN | NOT_PINNED |
| 2.5 | train | 0.41 | 0.48 | 0.097 | no / no | 3.09 | 3.16 | 7.36 | 8.41 | like-for-like | ABSTAIN | NOT_PINNED |
| 2.6 | train | 0.41 | 0.42 | 0.109 | no / yes | 2.78 | 2.86 | 7.29 | 8.33 | interpolated | ABSTAIN | NOT_PINNED |
| 2.7 | train | 0.34 | 0.37 | 0.104 | no / yes | 2.48 | 2.55 | 7.24 | 8.27 | interpolated | ABSTAIN | NOT_PINNED |
| 2.8 | train | 0.33 | 0.33 | 0.109 | no / yes | 2.17 | 2.26 | 7.19 | 8.22 | interpolated | ABSTAIN | NOT_PINNED |
| 2.9 | train | 0.30 | 0.29 | 0.108 | no / yes | 1.88 | 1.97 | 7.14 | 8.17 | interpolated | ABSTAIN | NOT_PINNED |
| 3.0 | train | 0.23 | 0.27 | 0.105 | no / yes | 1.66 | 1.74 | 7.11 | 8.13 | like-for-like | ABSTAIN | NOT_PINNED |
| 3.1 | train | 0.21 | 0.24 | 0.105 | no / yes | 1.48 | 1.56 | 7.07 | 8.09 | interpolated | ABSTAIN | NOT_PINNED |
| 3.2 | train | 0.19 | 0.21 | 0.106 | no / yes | 1.40 | 1.49 | 7.04 | 8.05 | like-for-like | ABSTAIN | NOT_PINNED |
| 3.3 | train | 0.21 | 0.19 | 0.106 | no / yes | 1.43 | 1.53 | 7.02 | 8.02 | like-for-like | ABSTAIN | NOT_PINNED |
| 3.4 | train | 0.18 | 0.17 | 0.105 | no / yes | 1.47 | 1.57 | 6.99 | 7.99 | exact | ABSTAIN | NOT_PINNED |
| 3.5 | train | 0.16 | 0.16 | 0.105 | no / yes | 1.51 | 1.61 | 6.97 | 7.97 | exact | ABSTAIN | NOT_PINNED |
| 3.6 | train | 0.15 | 0.14 | 0.105 | no / yes | 1.54 | 1.64 | 6.95 | 7.94 | exact | ABSTAIN | NOT_PINNED |
| 3.7 | train | 0.17 | 0.13 | 0.103 | no / yes | 1.54 | 1.64 | 6.93 | 7.92 | exact | ABSTAIN | NOT_PINNED |
| 3.8 | train | 0.12 | 0.12 | 0.104 | no / yes | 1.54 | 1.64 | 6.91 | 7.90 | exact | ABSTAIN | NOT_PINNED |
| 3.9 | train | 0.12 | 0.11 | 0.104 | no / yes | 1.51 | 1.61 | 6.89 | 7.88 | exact | ABSTAIN | NOT_PINNED |
| 4.0 | train | 0.11 | 0.10 | 0.103 | no / yes | 1.47 | 1.57 | 6.88 | 7.86 | exact | ABSTAIN | NOT_PINNED |
| 4.1 | train | 0.11 | 0.09 | 0.103 | no / yes | 1.43 | 1.52 | 6.86 | 7.85 | exact | ABSTAIN | NOT_PINNED |
| 4.2 | train | 0.09 | 0.09 | 0.103 | no / yes | 1.37 | 1.46 | 6.85 | 7.83 | exact | ABSTAIN | NOT_PINNED |
| 4.3 | train | 0.07 | 0.08 | 0.104 | no / yes | 1.31 | 1.40 | 6.84 | 7.82 | exact | ABSTAIN | NOT_PINNED |
| 4.4 | train | 0.08 | 0.08 | 0.103 | no / yes | 1.23 | 1.32 | 6.83 | 7.81 | exact | ABSTAIN | NOT_PINNED |
| 4.5 | train | 0.08 | 0.07 | 0.103 | no / yes | 1.15 | 1.23 | 6.82 | 7.79 | exact | ABSTAIN | NOT_PINNED |
| 4.6 | train | 0.08 | 0.07 | 0.102 | no / yes | 1.05 | 1.13 | 6.81 | 7.78 | exact | ABSTAIN | NOT_PINNED |
| 4.7 | train | 0.07 | 0.07 | 0.102 | no / yes | 0.95 | 1.03 | 6.80 | 7.77 | exact | ABSTAIN | UNDECIDED |
| 4.8 | train | 0.06 | 0.06 | 0.102 | no / yes | 0.85 | 0.92 | 6.79 | 7.76 | exact | ABSTAIN | UNDECIDED |
| 4.9 | train | 0.06 | 0.06 | 0.102 | no / yes | 0.73 | 0.80 | 6.78 | 7.75 | exact | ABSTAIN | UNDECIDED |
| 5.0 | train | 0.05 | 0.06 | 0.102 | no / yes | 0.62 | 0.68 | 6.77 | 7.74 | exact | ABSTAIN | UNDECIDED |
| 5.1 | train | 0.07 | 0.06 | 0.102 | no / yes | 0.51 | 0.57 | 6.76 | 7.74 | exact | ABSTAIN | UNDECIDED |
| 5.2 | train | 0.05 | 0.06 | 0.102 | no / yes | 0.48 | 0.53 | 6.76 | 7.73 | exact | ABSTAIN | UNDECIDED |
| 5.3 | train | 0.05 | 0.06 | 0.102 | no / yes | 0.57 | 0.62 | 6.75 | 7.72 | exact | ABSTAIN | UNDECIDED |
| 5.4 | train | 0.08 | 0.05 | 0.102 | no / yes | 0.69 | 0.75 | 6.75 | 7.71 | exact | ABSTAIN | UNDECIDED |
| 5.5 | train | 0.04 | 0.06 | 0.101 | no / yes | 0.85 | 0.91 | 6.74 | 7.71 | exact | ABSTAIN | UNDECIDED |
| 5.6 | train | 0.04 | 0.06 | 0.101 | no / yes | 1.02 | 1.09 | 6.74 | 7.70 | exact | ABSTAIN | NOT_PINNED |
| 5.7 | train | 0.07 | 0.05 | 0.102 | no / yes | 1.19 | 1.26 | 6.73 | 7.69 | exact | ABSTAIN | NOT_PINNED |
| 5.8 | train | 0.04 | 0.06 | 0.101 | no / yes | 1.39 | 1.48 | 6.73 | 7.69 | exact | ABSTAIN | NOT_PINNED |
| 5.9 | train | 0.07 | 0.05 | 0.102 | no / yes | 1.59 | 1.68 | 6.72 | 7.68 | exact | ABSTAIN | NOT_PINNED |
| 6.0 | train | 0.04 | 0.06 | 0.100 | no / yes | 1.82 | 1.92 | 6.72 | 7.68 | exact | ABSTAIN | NOT_PINNED |

Jz = 1.5 (in neither set, on its own line): cubic miss 1.94 tau; standard interval contains the truth: no; 2(b) lower width 8.86 tau.

**n = 115**

| Jz | range | label miss [S] | cubic miss | standard 2q | truth / label in standard interval | W_lo (2a) | W_hi (2a, indicative) | 2q_lo (2b) | 2q_hi (2b, indicative) | upper interval of this label | rule (c) | band (a) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | test | 4.67 | 5.06 | 0.100 | no / no | 158.00 | 174.04 | 9.40 | 11.65 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.2 | test | 3.63 | 3.85 | 0.094 | no / no | 89.72 | 98.76 | 8.79 | 10.90 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.3 | test | 2.95 | 2.99 | 0.089 | no / no | 51.98 | 57.13 | 8.32 | 10.32 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.4 | test | 2.37 | 2.38 | 0.085 | no / yes | 29.88 | 32.77 | 7.95 | 9.86 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.6 | train | 1.54 | 1.61 | 0.084 | no / no | 13.71 | 15.10 | 6.42 | 7.17 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.7 | train | 1.29 | 1.30 | 0.078 | no / yes | 6.01 | 6.45 | 6.26 | 6.98 | interpolated | ABSTAIN | NOT_PINNED |
| 1.8 | train | 1.14 | 1.07 | 0.063 | no / no | 5.15 | 5.59 | 6.10 | 6.84 | like-for-like | ABSTAIN | NOT_PINNED |
| 1.9 | train | 0.91 | 0.91 | 0.074 | no / yes | 4.50 | 4.90 | 6.00 | 6.70 | interpolated | ABSTAIN | NOT_PINNED |
| 2.0 | train | 0.75 | 0.77 | 0.080 | no / yes | 3.92 | 4.28 | 6.82 | 8.45 | like-for-like | ABSTAIN | NOT_PINNED |
| 2.1 | train | 0.72 | 0.65 | 0.059 | no / no | 3.91 | 4.28 | 6.70 | 8.31 | interpolated | ABSTAIN | NOT_PINNED |
| 2.2 | train | 0.53 | 0.57 | 0.066 | no / no | 3.72 | 4.02 | 6.64 | 8.23 | interpolated | ABSTAIN | NOT_PINNED |
| 2.3 | train | 0.47 | 0.49 | 0.075 | no / yes | 3.38 | 3.65 | 6.56 | 8.14 | interpolated | ABSTAIN | NOT_PINNED |
| 2.4 | train | 0.41 | 0.42 | 0.074 | no / yes | 3.02 | 3.26 | 6.50 | 8.06 | interpolated | ABSTAIN | NOT_PINNED |
| 2.5 | train | 0.34 | 0.37 | 0.075 | no / yes | 2.71 | 2.93 | 6.45 | 7.99 | like-for-like | ABSTAIN | NOT_PINNED |
| 2.6 | train | 0.30 | 0.32 | 0.072 | no / yes | 2.44 | 2.64 | 6.40 | 7.93 | interpolated | ABSTAIN | NOT_PINNED |
| 2.7 | train | 0.27 | 0.28 | 0.070 | no / yes | 2.16 | 2.36 | 6.35 | 7.88 | interpolated | ABSTAIN | NOT_PINNED |
| 2.8 | train | 0.28 | 0.25 | 0.064 | no / no | 1.89 | 2.08 | 6.31 | 7.83 | interpolated | ABSTAIN | NOT_PINNED |
| 2.9 | train | 0.22 | 0.22 | 0.067 | no / yes | 1.63 | 1.81 | 6.28 | 7.78 | interpolated | ABSTAIN | NOT_PINNED |
| 3.0 | train | 0.20 | 0.19 | 0.067 | no / yes | 1.43 | 1.60 | 6.25 | 7.75 | like-for-like | ABSTAIN | NOT_PINNED |
| 3.1 | train | 0.16 | 0.17 | 0.067 | no / yes | 1.27 | 1.44 | 6.22 | 7.71 | interpolated | ABSTAIN | NOT_PINNED |
| 3.2 | train | 0.16 | 0.15 | 0.067 | no / yes | 1.20 | 1.38 | 6.19 | 7.68 | interpolated | ABSTAIN | NOT_PINNED |
| 3.3 | train | 0.15 | 0.14 | 0.067 | no / yes | 1.23 | 1.42 | 6.17 | 7.65 | like-for-like | ABSTAIN | NOT_PINNED |
| 3.4 | train | 0.12 | 0.12 | 0.066 | no / yes | 1.28 | 1.47 | 6.15 | 7.63 | interpolated | ABSTAIN | NOT_PINNED |
| 3.5 | train | 0.11 | 0.11 | 0.065 | no / yes | 1.32 | 1.51 | 6.13 | 7.60 | interpolated | ABSTAIN | NOT_PINNED |
| 3.6 | train | 0.10 | 0.10 | 0.065 | no / yes | 1.34 | 1.54 | 6.11 | 7.58 | like-for-like | ABSTAIN | NOT_PINNED |
| 3.7 | train | 0.09 | 0.09 | 0.065 | no / yes | 1.35 | 1.55 | 6.10 | 7.56 | interpolated | ABSTAIN | NOT_PINNED |
| 3.8 | train | 0.08 | 0.08 | 0.065 | no / yes | 1.35 | 1.55 | 6.08 | 7.54 | interpolated | ABSTAIN | NOT_PINNED |
| 3.9 | train | 0.07 | 0.07 | 0.065 | no / yes | 1.33 | 1.53 | 6.07 | 7.53 | interpolated | ABSTAIN | NOT_PINNED |
| 4.0 | train | 0.06 | 0.07 | 0.064 | no / yes | 1.29 | 1.50 | 6.06 | 7.51 | exact | ABSTAIN | NOT_PINNED |
| 4.1 | train | 0.06 | 0.06 | 0.065 | no / yes | 1.25 | 1.45 | 6.05 | 7.50 | exact | ABSTAIN | NOT_PINNED |
| 4.2 | train | 0.06 | 0.06 | 0.065 | no / yes | 1.19 | 1.40 | 6.03 | 7.48 | exact | ABSTAIN | NOT_PINNED |
| 4.3 | train | 0.06 | 0.05 | 0.065 | no / yes | 1.13 | 1.34 | 6.02 | 7.47 | exact | ABSTAIN | NOT_PINNED |
| 4.4 | train | 0.05 | 0.05 | 0.064 | no / yes | 1.06 | 1.27 | 6.01 | 7.46 | exact | ABSTAIN | NOT_PINNED |
| 4.5 | train | 0.04 | 0.04 | 0.064 | no / yes | 0.99 | 1.19 | 6.01 | 7.45 | exact | ABSTAIN | UNDECIDED |
| 4.6 | train | 0.04 | 0.04 | 0.064 | no / yes | 0.90 | 1.11 | 6.00 | 7.44 | exact | ABSTAIN | UNDECIDED |
| 4.7 | train | 0.04 | 0.04 | 0.064 | no / yes | 0.81 | 1.01 | 5.99 | 7.43 | exact | ABSTAIN | UNDECIDED |
| 4.8 | train | 0.06 | 0.03 | 0.065 | no / yes | 0.70 | 0.90 | 5.98 | 7.42 | exact | ABSTAIN | UNDECIDED |
| 4.9 | train | 0.03 | 0.03 | 0.064 | no / yes | 0.60 | 0.80 | 5.98 | 7.41 | exact | ABSTAIN | UNDECIDED |
| 5.0 | train | 0.03 | 0.03 | 0.064 | yes / yes | 0.50 | 0.69 | 5.97 | 7.40 | exact | ABSTAIN | UNDECIDED |
| 5.1 | train | 0.02 | 0.03 | 0.064 | yes / yes | 0.40 | 0.60 | 5.96 | 7.40 | exact | ABSTAIN | UNDECIDED |
| 5.2 | train | 0.03 | 0.03 | 0.064 | yes / yes | 0.37 | 0.57 | 5.96 | 7.39 | exact | ABSTAIN | UNDECIDED |
| 5.3 | train | 0.02 | 0.03 | 0.063 | yes / yes | 0.45 | 0.66 | 5.95 | 7.38 | exact | ABSTAIN | UNDECIDED |
| 5.4 | train | 0.02 | 0.03 | 0.063 | yes / yes | 0.57 | 0.79 | 5.95 | 7.38 | exact | ABSTAIN | UNDECIDED |
| 5.5 | train | 0.02 | 0.02 | 0.063 | yes / yes | 0.70 | 0.94 | 5.94 | 7.37 | exact | ABSTAIN | UNDECIDED |
| 5.6 | train | 0.02 | 0.02 | 0.063 | yes / yes | 0.85 | 1.10 | 5.94 | 7.37 | exact | ABSTAIN | UNDECIDED |
| 5.7 | train | 0.02 | 0.02 | 0.063 | yes / yes | 1.00 | 1.27 | 5.94 | 7.36 | exact | ABSTAIN | NOT_PINNED |
| 5.8 | train | 0.03 | 0.02 | 0.063 | yes / yes | 1.17 | 1.46 | 5.93 | 7.36 | exact | ABSTAIN | NOT_PINNED |
| 5.9 | train | 0.01 | 0.02 | 0.064 | yes / yes | 1.35 | 1.67 | 5.93 | 7.35 | exact | ABSTAIN | NOT_PINNED |
| 6.0 | train | 0.01 | 0.02 | 0.064 | yes / yes | 1.54 | 1.88 | 5.92 | 7.35 | exact | ABSTAIN | NOT_PINNED |

Jz = 1.5 (in neither set, on its own line): cubic miss 1.92 tau; standard interval contains the truth: no; 2(b) lower width 7.66 tau.

### 3.3 Proposition 2 for the cubic: summary

- n = 57. 2(a), lower version: W_lo = 34.18-185.25 tau at the test couplings and 0.48-15.49 tau at the held-out training couplings; band (a) is NOT_PINNED at 40 of 49 queries, UNDECIDED at 9 (Jz = 4.7-5.5: W_lo below tau, upper version not available), PINNED at 0. 2(b), lower version: 2q_lo = 9.22-11.08 tau at the test couplings, 6.71-7.82 tau held out; these intervals contain the truth at 4 of 4 test and 45 of 45 training queries. Rule (c) answers 0 of 49 queries (definite abstention at 49: 2q_lo > tau). Upper kinds over the 45 training labels: exact 27, like-for-like 7, interpolated 11. Check of the stored script: every label and every truth lies in its upper interval (True, True); linearity check 1.3e-13.
- n = 115. 2(a), lower version: W_lo = 29.87-158.00 tau at the test couplings and 0.37-13.71 tau at the held-out training couplings; band (a) is NOT_PINNED at 37 of 49 queries, UNDECIDED at 12 (Jz = 4.5-5.6: W_lo below tau, upper version not available), PINNED at 0. 2(b), lower version: 2q_lo = 7.95-9.40 tau at the test couplings, 5.92-6.83 tau held out; these intervals contain the truth at 3 of 4 test and 45 of 45 training queries. Rule (c) answers 0 of 49 queries (definite abstention at 49: 2q_lo > tau). Upper kinds over the 45 training labels: exact 21, like-for-like 7, interpolated 17. Check of the stored script: every label and every truth lies in its upper interval (True, True); linearity check 7.2e-14.
- n = 57: queries at which the 2(b) lower-version interval does not contain the truth: none.
- n = 115: queries at which the 2(b) lower-version interval does not contain the truth: Jz = 1.1 (miss 5.06 tau against a half-width of 4.70 tau).
- The lower version is a lower bound on the width that a valid interval of this construction must have. It is not itself a guaranteed interval, and no conformal guarantee applies outside the training range.

### 3.4 Outcomes of L1, L2, L3 (each holds iff true at n = 57; n = 115 reported)

| | n = 57 (decides) | n = 115 (reported) |
|---|---|---|
| **L1** the cubic misses the true m_s by more than tau at each of 1.1-1.4 | **HOLDS**: 3.72, 3.17, 2.69, 2.29 tau | HOLDS: 5.06, 3.85, 2.99, 2.38 tau |
| **L2** standard intervals calibrated on the real labels cover the truth at none of the four test couplings | **HOLDS**: covered at 0 of 4 (sites: 0.018, 0.000, 0.000, 0.000) | HOLDS: covered at 0 of 4 (sites: 0.000, 0.000, 0.000, 0.000) |
| **L3** 2(b) intervals calibrated on all 45 labels wider than tau at every coupling (lower version) | **HOLDS**: one value of q_lo = 0.19773; 2q_lo = 6.71-11.08 tau over the 45 training and 4 test couplings (held out, 44 labels: 6.71-7.82 tau) | HOLDS: q_lo = 0.17461; 5.92-9.40 tau (held out: 5.92-6.83 tau) |

L1 and L2 were predictions of the emulation-based test; the miss of the real m_s label itself at 1.1-1.4 had been seen [S, F7], the cubic's miss had not. L3 carries the mark of gate G6 (first part NOT COMPLETE).

### 3.5 Blocks that the derived script inherits from the stored one

- n = 57. Per-site split conformal over all choices of 3 calibration couplings (14190 choices), test range: sites covered, labels / truth: cubic 0.073 / 0.004, null 0.070 / 0.000. **Like-for-like block, not a property of the real labels** (the stored in-sector thresholds at E_real, at the couplings of the stored map only; seen before the hash, F6 and F9): m_s "answered" at Jz = 3.2, 3.3, 3.4, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0; local labels at none; largest miss of the cubic at those couplings 0.214 tau.
- n = 115. Per-site split conformal over all choices of 2 calibration couplings (990 choices), test range: sites covered, labels / truth: cubic 0.180 / 0.000, null 0.022 / 0.000. **Like-for-like block, not a property of the real labels** (the stored in-sector thresholds at E_real, at the couplings of the stored map only; seen before the hash, F6 and F9): m_s "answered" at Jz = 3.3, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0; local labels at none; largest miss of the cubic at those couplings 0.137 tau.
- The block `device_illustration` of the stored script (this project's three device points against the cubic trained on the real labels) is in `out/learn/results_cheap.json`; it is not part of the declaration and is not used.

### 3.6 Not computed

- **pilot perceptron, n = 57, in distribution (45 held-out couplings, real and DMRG labels)** (4050 fits). Reason: cost: about 22 CPU-hours at the 19.5 s per fit measured in this run; outside the time allowed to this task. To complete: python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=H --model=mlp_pilot3 --size=57 --part=i/k (i = 0..k-1), then --assemble=k, then run_learn.py --stage=merge and --stage=rules; the test-range piece is already in out/learn/parts/.
- **pilot perceptron, n = 115 (secondary), test range and in distribution** (4142 fits). Reason: cost: more than 22 CPU-hours. To complete: the same commands with --size=115 (first --part=ood).
- **the dataset paper's architecture 1, n = 57, test range (real and DMRG labels)** (92 fits). Reason: cost: about 13 CPU-hours (520 s per fit measured before the hash on an idle core). To complete: python -B -I code/run_learn.py --hash=H --stage=f1_ibm57, then --stage=merge.
- None of L1-L3, (f2), (f3) uses these models. Their rows in the table of Sec. 3.1 stay empty; they are not passes.

## 4. (f2) The learner-independent floor

Rule: for any learner and the constant-width score, 2q >= w_(k), the k-th narrowest calibration interval, k = ceil((m+1)(1-alpha)) = 42 for m = 45; computed with the lower widths ((1 - q) x hull of explicit states); **holds iff the floor exceeds tau(x) at each of the four test queries** (Sec. 12, line 12).

| size | floor w_(42) | at Jz = 1.1 / 1.2 / 1.3 / 1.4 (tau) | smallest over the 50 couplings (tau) | held out, m = 44, k = 41 (tau) | outcome |
|---|---|---|---|---|---|
| 57 | 0.22959 | 6.42 / 5.97 / 5.62 / 5.35 | 3.89 | 3.89-4.54 | **HOLDS** (every coupling: True; held out: True) |
| 115 | 0.20427 | 5.49 / 5.14 / 4.86 / 4.65 | 3.46 | 3.46-3.99 | **HOLDS** (every coupling: True; held out: True) |

Floor at every query, in units of tau(x):

| Jz | n = 57 | n = 115 | held out, n = 57 | held out, n = 115 |
|---|---|---|---|---|
| 1.1 | 6.42 | 5.49 | - | - |
| 1.2 | 5.97 | 5.14 | - | - |
| 1.3 | 5.62 | 4.86 | - | - |
| 1.4 | 5.35 | 4.65 | - | - |
| 1.5 | 5.14 | 4.47 | - | - |
| 1.6 | 4.96 | 4.33 | 4.23 | 3.76 |
| 1.7 | 4.82 | 4.22 | 4.11 | 3.66 |
| 1.8 | 4.71 | 4.13 | 4.01 | 3.58 |
| 1.9 | 4.61 | 4.05 | 3.93 | 3.51 |
| 2.0 | 4.53 | 3.98 | 4.53 | 3.98 |
| 2.1 | 4.46 | 3.92 | 4.46 | 3.92 |
| 2.2 | 4.40 | 3.87 | 4.40 | 3.87 |
| 2.3 | 4.34 | 3.83 | 4.34 | 3.83 |
| 2.4 | 4.30 | 3.80 | 4.30 | 3.80 |
| 2.5 | 4.26 | 3.76 | 4.26 | 3.76 |
| 2.6 | 4.23 | 3.73 | 4.23 | 3.73 |
| 2.7 | 4.19 | 3.71 | 4.19 | 3.71 |
| 2.8 | 4.17 | 3.69 | 4.17 | 3.69 |
| 2.9 | 4.14 | 3.67 | 4.14 | 3.67 |
| 3.0 | 4.12 | 3.65 | 4.12 | 3.65 |
| 3.1 | 4.10 | 3.63 | 4.10 | 3.63 |
| 3.2 | 4.08 | 3.62 | 4.08 | 3.62 |
| 3.3 | 4.07 | 3.60 | 4.07 | 3.60 |
| 3.4 | 4.05 | 3.59 | 4.05 | 3.59 |
| 3.5 | 4.04 | 3.58 | 4.04 | 3.58 |
| 3.6 | 4.03 | 3.57 | 4.03 | 3.57 |
| 3.7 | 4.02 | 3.56 | 4.02 | 3.56 |
| 3.8 | 4.01 | 3.55 | 4.01 | 3.55 |
| 3.9 | 4.00 | 3.54 | 4.00 | 3.54 |
| 4.0 | 3.99 | 3.54 | 3.99 | 3.54 |
| 4.1 | 3.98 | 3.53 | 3.98 | 3.53 |
| 4.2 | 3.97 | 3.52 | 3.97 | 3.52 |
| 4.3 | 3.96 | 3.52 | 3.96 | 3.52 |
| 4.4 | 3.96 | 3.51 | 3.96 | 3.51 |
| 4.5 | 3.95 | 3.51 | 3.95 | 3.51 |
| 4.6 | 3.95 | 3.50 | 3.95 | 3.50 |
| 4.7 | 3.94 | 3.50 | 3.94 | 3.50 |
| 4.8 | 3.94 | 3.49 | 3.94 | 3.49 |
| 4.9 | 3.93 | 3.49 | 3.93 | 3.49 |
| 5.0 | 3.93 | 3.49 | 3.93 | 3.49 |
| 5.1 | 3.92 | 3.48 | 3.92 | 3.48 |
| 5.2 | 3.92 | 3.48 | 3.92 | 3.48 |
| 5.3 | 3.91 | 3.48 | 3.91 | 3.48 |
| 5.4 | 3.91 | 3.47 | 3.91 | 3.47 |
| 5.5 | 3.91 | 3.47 | 3.91 | 3.47 |
| 5.6 | 3.90 | 3.47 | 3.90 | 3.47 |
| 5.7 | 3.90 | 3.47 | 3.90 | 3.47 |
| 5.8 | 3.90 | 3.46 | 3.90 | 3.46 |
| 5.9 | 3.90 | 3.46 | 3.90 | 3.46 |
| 6.0 | 3.89 | 3.46 | 3.89 | 3.46 |

- n = 57: the four widest lower widths are those of the labels at Jz = 1.6, 1.7, 1.8, 1.9; the floor is the fourth of them. No training label lacks an explicit-state interval (list of widths taken as 0: []). Gate mark: 33 of the 45 lower widths rest on re-evaluated energies (G6, first part, NOT COMPLETE). **Post hoc robustness (not declared):** with those widths set to 0, the floor is 0.10219, that is 2.86 / 2.65 / 2.50 / 2.38 tau at the four test queries: still above tau.
- n = 115: the four widest lower widths are those of the labels at Jz = 1.6, 1.7, 1.8, 1.9; the floor is the fourth of them. No training label lacks an explicit-state interval (list of widths taken as 0: []). Gate mark: 33 of the 45 lower widths rest on re-evaluated energies (G6, first part, NOT COMPLETE). **Post hoc robustness (not declared):** with those widths set to 0, the floor is 0.09382, that is 2.52 / 2.36 / 2.23 / 2.13 tau at the four test queries: still above tau.
- What decides the floor: the labels at Jz = 1.6-1.9, whose windows are several tau wide. The floor says nothing about a calibration set restricted to certified labels; that is (f3).

## 5. (f3) The constructive test: train and calibrate only on labels certified at their own energy

200 seeded splits of the set (`numpy.random.default_rng([1845216616, n, c])`). M1: line in 1/Jz; M2: 1 - a/Jz^2 - b/Jz^4, both fitted to the real m_s labels of the training couplings. Control M0: the cubic in 1/Jz trained on every real training label outside the calibration and query couplings (uncertified labels included). Score s_j = max(|f(x_j) - lo_j|, |f(x_j) - hi_j|) over the exact interval of the calibration label; q = the ceil((m+1)(1-alpha))-th smallest; interval f(x) +- q. **Pass rule, n = 57, set S_p, both M1 and M2: (W) in at least 90 % of the splits 2q <= tau(x) at every query, and (C) the truth within q of the prediction in at least 90 % of all (split, query) pairs.**

### 5.1 Primary: n = 57, S_p = S_1/2 (18 couplings, Jz = 4.3-6.0; 4 training, 9 calibration, 5 query couplings per split): **PASS**

- M1: (W) 200 of 200 splits (rule: at least 180): met. (C) 1000 of 1000 pairs (rule: at least 900): met. Width 2q = 0.586-0.857 tau (median 0.733). Largest miss of the prediction 0.137 tau. Smallest ratio of 2q to the widest calibration interval: 1.271 (the floor of (f2) is respected in every split: 0 violations).
- M2: (W) 200 of 200 splits (rule: at least 180): met. (C) 1000 of 1000 pairs (rule: at least 900): met. Width 2q = 0.562-0.856 tau (median 0.719). Largest miss of the prediction 0.149 tau. Smallest ratio of 2q to the widest calibration interval: 1.164 (the floor of (f2) is respected in every split: 0 violations).
- Control M0 (secondary): **PASS**. (W) 200 of 200, (C) 1000 of 1000, 2q = 0.599-0.761 tau, largest miss 0.090 tau. **The control passes as well, with a smaller largest miss than M1 and M2:** on these data, what makes the test pass is calibrating on certified labels with the interval score; training only on certified labels brought no measurable gain.
- With m = 9 calibration labels, k = 9: q is the largest calibration score; the level 9/10 = 0.9 is attained exactly.
- The 1000 (split, query) pairs are drawn from 18 couplings and are not independent trials; the counts are those of the declared rule.
- Gate G7 inside the test: labels outside their exact interval: none; truths outside: none.

### 5.2 Every set, model and size

| size | set | couplings | train / cal / query | model | (W): splits with 2q <= tau at every query | (C): pairs with the truth inside | 2q (tau): min / median / max | largest miss (tau) | min of 2q over the widest calibration interval | outcome |
|---|---|---|---|---|---|---|---|---|---|---|
| 57 | S | 26 (3.5-6.0) | 6 / 12 / 8 | M1 | 6 of 200 **(rule not met)** | 1600 of 1600 | 0.906 / 1.356 / 1.564 | 0.212 | 1.500 | **FAIL** (M1 and M2 together) |
| 57 | S | 26 (3.5-6.0) | 6 / 12 / 8 | M2 | 6 of 200 **(rule not met)** | 1600 of 1600 | 0.916 / 1.333 / 1.546 | 0.211 | 1.186 | **FAIL** (M1 and M2 together) |
| 57 | S | 26 (3.5-6.0) | 6 / 12 / 8 | M0 (control) | 6 of 200 **(rule not met)** | 1600 of 1600 | 0.889 / 1.317 / 1.432 | 0.156 | 1.495 | **FAIL** |
| 57 | S_3/4 | 23 (3.8-6.0) | 6 / 12 / 5 | M1 | 50 of 200 **(rule not met)** | 1000 of 1000 | 0.815 / 1.056 / 1.163 | 0.157 | 1.495 | **FAIL** (M1 and M2 together) |
| 57 | S_3/4 | 23 (3.8-6.0) | 6 / 12 / 5 | M2 | 66 of 200 **(rule not met)** | 1000 of 1000 | 0.822 / 1.020 / 1.137 | 0.137 | 1.289 | **FAIL** (M1 and M2 together) |
| 57 | S_3/4 | 23 (3.8-6.0) | 6 / 12 / 5 | M0 (control) | 50 of 200 **(rule not met)** | 1000 of 1000 | 0.817 / 1.040 / 1.083 | 0.121 | 1.505 | **FAIL** |
| 57 | S_1/2 (**primary**) | 18 (4.3-6.0) | 4 / 9 / 5 | M1 | 200 of 200 | 1000 of 1000 | 0.586 / 0.733 / 0.857 | 0.137 | 1.271 | **PASS** (M1 and M2 together) |
| 57 | S_1/2 (**primary**) | 18 (4.3-6.0) | 4 / 9 / 5 | M2 | 200 of 200 | 1000 of 1000 | 0.562 / 0.719 / 0.856 | 0.149 | 1.164 | **PASS** (M1 and M2 together) |
| 57 | S_1/2 (**primary**) | 18 (4.3-6.0) | 4 / 9 / 5 | M0 (control) | 200 of 200 | 1000 of 1000 | 0.599 / 0.735 / 0.761 | 0.090 | 1.501 | **PASS** |
| 115 | S | 21 (4.0-6.0) | 6 / 12 / 3 | M1 | 200 of 200 | 600 of 600 | 0.859 / 0.932 / 0.999 | 0.109 | 1.397 | **PASS** (M1 and M2 together) |
| 115 | S | 21 (4.0-6.0) | 6 / 12 / 3 | M2 | 199 of 200 | 600 of 600 | 0.869 / 0.938 / 1.028 | 0.117 | 1.411 | **PASS** (M1 and M2 together) |
| 115 | S | 21 (4.0-6.0) | 6 / 12 / 3 | M0 (control) | 200 of 200 | 600 of 600 | 0.864 / 0.937 / 0.963 | 0.067 | 1.414 | **PASS** |
| 115 | S_3/4 (S_p, secondary) | 21 (4.0-6.0) | 6 / 12 / 3 | M1 | 200 of 200 | 600 of 600 | 0.862 / 0.932 / 0.985 | 0.122 | 1.397 | **PASS** (M1 and M2 together) |
| 115 | S_3/4 (S_p, secondary) | 21 (4.0-6.0) | 6 / 12 / 3 | M2 | 200 of 200 | 600 of 600 | 0.865 / 0.938 / 0.991 | 0.131 | 1.414 | **PASS** (M1 and M2 together) |
| 115 | S_3/4 (S_p, secondary) | 21 (4.0-6.0) | 6 / 12 / 3 | M0 (control) | 200 of 200 | 600 of 600 | 0.858 / 0.935 / 0.965 | 0.068 | 1.413 | **PASS** |
| 115 | S_1/2 | 10 | - | - | - | - | - | - | - | NOT RUN (fewer than 15 couplings) |

- **n = 57, set S (all 26 certified labels, Jz 3.5-6.0): FAIL.** (C) is met in every pair, (W) in only 6 of 200 splits: with labels certified at up to 0.911 tau the returned interval is 0.906-1.564 tau wide. This is the case announced in the declaration ("labels certified at nearly tau make (W) fail even with a perfect model"); the declared prior for a pass on S was 0.4.
- **n = 57, set S_3/4 (23 labels): FAIL** on (W) (50 and 66 of 200 splits for M1 and M2); (C) met in every pair.
- **n = 57, set S_1/2 (18 labels): PASS** (declared prior 0.8).
- **n = 115 (secondary): PASS on S_p = S_3/4 and on S** (the same 21 couplings, Jz 4.0-6.0, different splits); on S, M2 meets (W) in 199 of 200 splits. Widths 0.859-1.028 tau: close to the tolerance. S_1/2 has 10 couplings: NOT RUN.
- Forecast against outcome: the declaration quoted 0.71-0.76 tau from emulated labels in [4, 6]. Obtained on [4.0, 6.0] at n = 115: 0.859-0.999 tau (median 0.932 for M1), wider than the forecast; on [4.3, 6.0] at n = 57: 0.586-0.857 tau (median 0.733 for M1).

### 5.3 Proposition 2(a) on the same splits and the secondary width-normalized scores (no rule)

| size | set | model | W(x) with exact intervals (tau): min-max | W(x), lower version: max (tau) | normalized score, literal: 2q sigma (tau) min-max; truth covered | normalized score, worst case over the interval: 2q sigma (tau) min-max; splits all <= tau; truth covered |
|---|---|---|---|---|---|---|
| 57 | S | M1 | 0.27-2.04 | 1.75 | 0.004-0.419; 2.1 % of pairs | 0.06-9.94; 1.5 % of splits; 99.8 % of pairs |
| 57 | S | M2 | 0.29-4.49 | 3.94 | 0.004-0.327; 4.4 % of pairs | 0.06-8.99; 2.0 % of splits; 99.9 % of pairs |
| 57 | S | M0 | not available (M0 uses labels without exact interval) | 10.03 | 0.004-0.622; 7.9 % of pairs | 0.06-10.56; 1.5 % of splits; 99.8 % of pairs |
| 57 | S_3/4 | M1 | 0.27-1.52 | 1.31 | 0.004-0.276; 2.3 % of pairs | 0.06-7.13; 10.5 % of splits; 99.9 % of pairs |
| 57 | S_3/4 | M2 | 0.29-2.84 | 2.53 | 0.004-0.230; 1.3 % of pairs | 0.06-7.05; 10.0 % of splits; 99.9 % of pairs |
| 57 | S_3/4 | M0 | not available (M0 uses labels without exact interval) | 5.33 | 0.003-0.294; 2.5 % of pairs | 0.06-7.38; 9.5 % of splits; 99.8 % of pairs |
| 57 | S_1/2 | M1 | 0.24-2.45 | 2.23 | 0.012-0.579; 7.9 % of pairs | 0.17-7.10; 43.5 % of splits; 100.0 % of pairs |
| 57 | S_1/2 | M2 | 0.24-4.66 | 4.24 | 0.014-0.545; 7.2 % of pairs | 0.18-7.16; 48.0 % of splits; 100.0 % of pairs |
| 57 | S_1/2 | M0 | not available (M0 uses labels without exact interval) | 7.06 | 0.011-0.436; 3.3 % of pairs | 0.18-7.33; 36.0 % of splits; 100.0 % of pairs |
| 115 | S | M1 | 0.26-1.90 | 0.93 | 0.007-0.259; 31.5 % of pairs | 0.20-1.34; 51.5 % of splits; 100.0 % of pairs |
| 115 | S | M2 | 0.29-3.38 | 1.70 | 0.005-0.236; 4.5 % of pairs | 0.20-1.23; 51.5 % of splits; 100.0 % of pairs |
| 115 | S | M0 | not available (M0 uses labels without exact interval) | 4.48 | 0.008-0.255; 31.5 % of pairs | 0.20-1.32; 46.0 % of splits; 100.0 % of pairs |
| 115 | S_3/4 | M1 | 0.26-2.26 | 1.13 | 0.006-0.363; 27.7 % of pairs | 0.20-1.32; 54.5 % of splits; 100.0 % of pairs |
| 115 | S_3/4 | M2 | 0.28-4.86 | 2.46 | 0.006-0.158; 4.2 % of pairs | 0.19-1.20; 59.5 % of splits; 100.0 % of pairs |
| 115 | S_3/4 | M0 | not available (M0 uses labels without exact interval) | 4.48 | 0.010-0.310; 33.3 % of pairs | 0.20-1.26; 49.0 % of splits; 100.0 % of pairs |

- The literal width-normalized score (|f - y| / sigma, which ignores the label's interval) returns narrow intervals that contain the truth in only 7.9 % of the pairs on the primary set (M1): it must not be presented as a certified interval. The worst-case variant keeps the truth inside (100.0 %) but is below tau at every query in only 43.5 % of the splits. Neither decides anything.
- The band of Proposition 2(a) exceeds tau in part of the pairs (largest 2.45 tau for M1 on the primary set): 2(a) alone would not give the guarantee that 2(b) gives here.

### 5.4 The limit, printed with the result (declaration Sec. 7)

Between Jz = 4 and 6 the true m_s changes by 0.4 tau (measured: 0.388-0.398 tau at n = 57 and 0.364-0.373 tau at n = 115; over the primary set, Jz = 4.3-6.0: 0.294-0.301 tau). The test shows that the intervals survive the learner and its calibration where labels are certified. It does not show that a hard function was learned. Two facts of this run say the same: the control M0 passes, and the largest miss of the real labels of the primary set is already 0.082 tau [S, F7].

## 6. Independent recomputation (own code, `checks/rd_learn_independent.py`; decides nothing)

Written after the hash; imports no sealed file. It recomputes with other formulas (least squares on an augmented system instead of the normal equations; m_s fitted directly instead of site by site): the cubic and the null of (f1) at both sizes, real and control labels, test range and in distribution; q_lo and W_lo of Proposition 2; the floor of (f2); (W), (C), widths and largest miss of (f3) for every set that was run and M1, M2, M0. The splits were regenerated with the declared generator call and equal the stored ones.

| quantity | largest absolute difference from the sealed output |
|---|---|
| f1 cubic cov_label flags | 0.0e+00 |
| f1 cubic cov_truth flags | 0.0e+00 |
| f1 cubic miss/tau | 6.6e-11 |
| f1 cubic pred | 2.4e-12 |
| f1 cubic q | 6.9e-13 |
| f1 nearest cov_label flags | 0.0e+00 |
| f1 nearest cov_truth flags | 0.0e+00 |
| f1 nearest miss/tau | 0.0e+00 |
| f1 nearest pred | 0.0e+00 |
| f1 nearest q | 0.0e+00 |
| f2 floor | 0.0e+00 |
| f3 frac_pairs_C | 0.0e+00 |
| f3 frac_splits_W | 0.0e+00 |
| f3 largest miss/tau | 8.7e-13 |
| f3 width/tau max | 1.6e-12 |
| f3 width/tau median | 1.4e-12 |
| f3 width/tau min | 3.1e-12 |
| prop2 W_lo/tau (relative) | 3.8e-12 |
| prop2 q_lo (all 45 labels) | 3.1e-15 |

Not recomputed independently: the per-site coverages, the upper (indicative) versions of Proposition 2, the secondary normalized scores, the perceptron.

## 7. Post hoc (not declared; these lines decide nothing)

**7.1 The standard score on the splits of (f3).** Same splits, same models, score |f(x_j) - y_j| on the calibration labels instead of the interval score:

| size | set | model | interval score (declared): (W) / (C) | standard score: splits with 2q <= tau | standard score: pairs with the truth inside | standard 2q (tau) |
|---|---|---|---|---|---|---|
| 57 | S | M1 | 3.0 % / 100.0 % | 100.0 % | **1.6 %** | 0.031-0.119 |
| 57 | S | M2 | 3.0 % / 100.0 % | 100.0 % | **12.7 %** | 0.022-0.405 |
| 57 | S | M0 | 3.0 % / 100.0 % | 100.0 % | **3.1 %** | 0.028-0.139 |
| 57 | S | constant (post hoc) | 0.0 % / 100.0 % | 100.0 % | **82.8 %** | 0.358-0.890 |
| 57 | S_3/4 | M1 | 25.0 % / 100.0 % | 100.0 % | **0.4 %** | 0.024-0.096 |
| 57 | S_3/4 | M2 | 33.0 % / 100.0 % | 100.0 % | **2.3 %** | 0.024-0.176 |
| 57 | S_3/4 | M0 | 25.0 % / 100.0 % | 100.0 % | **0.0 %** | 0.027-0.099 |
| 57 | S_3/4 | constant (post hoc) | 1.5 % / 100.0 % | 100.0 % | **81.5 %** | 0.283-0.679 |
| 57 | S_1/2 | M1 | 100.0 % / 100.0 % | 100.0 % | **2.9 %** | 0.028-0.159 |
| 57 | S_1/2 | M2 | 100.0 % / 100.0 % | 100.0 % | **5.6 %** | 0.026-0.251 |
| 57 | S_1/2 | M0 | 100.0 % / 100.0 % | 100.0 % | **0.0 %** | 0.022-0.103 |
| 57 | S_1/2 | constant (post hoc) | 48.5 % / 100.0 % | 100.0 % | **80.1 %** | 0.163-0.509 |
| 115 | S | M1 | 100.0 % / 100.0 % | 100.0 % | **36.0 %** | 0.016-0.150 |
| 115 | S | M2 | 99.5 % / 100.0 % | 100.0 % | **26.0 %** | 0.010-0.209 |
| 115 | S | M0 | 100.0 % / 100.0 % | 100.0 % | **15.0 %** | 0.010-0.065 |
| 115 | S | constant (post hoc) | 1.5 % / 100.0 % | 100.0 % | **85.2 %** | 0.253-0.562 |
| 115 | S_3/4 | M1 | 100.0 % / 100.0 % | 100.0 % | **35.5 %** | 0.012-0.116 |
| 115 | S_3/4 | M2 | 100.0 % / 100.0 % | 100.0 % | **24.8 %** | 0.009-0.135 |
| 115 | S_3/4 | M0 | 100.0 % / 100.0 % | 100.0 % | **15.0 %** | 0.012-0.080 |
| 115 | S_3/4 | constant (post hoc) | 2.5 % / 100.0 % | 100.0 % | **86.0 %** | 0.241-0.533 |

- On the primary set the standard recipe returns intervals of at most 0.251 tau that contain the truth in 2.9 % (M1), 5.6 % (M2) and 0.0 % (M0) of the pairs; the interval score contains it in 100 %. At n = 115 (S_p): 35.5 %, 24.8 %, 15.0 %. Even on labels certified to half the tolerance, the standard intervals follow the labels and miss the truth; the energy intervals are what restores coverage, at the price of the width.
- **7.2 A constant model** (the mean of the training labels) with the interval score on the primary set: (C) 100.0 % of pairs, (W) 48.5 % of splits (2q = 0.528-1.207 tau, largest miss 0.321 tau). A constant would fail the pass rule on width only, and a line in 1/Jz (M1) is enough to pass it. This quantifies the limit of Sec. 5.4.
- **7.3 The floor without the labels that rest on re-evaluated energies:** Sec. 4.

## 8. Re-executed, only compared, not checked

- **Re-executed:** the sealed code (cheap stage: cubic, null, Proposition 2, floor, constructive test, rules; the perceptron's test-range piece at n = 57); the manifest check; own independent recomputation (Sec. 6); the post hoc lines.
- **Only compared:** the intervals of `out/S_sets.json` with the m_s rows of `out/map_real.json` (equal); S with the CERTIFIED (exact) rows; the stored splits with the regenerated ones.
- **Not checked here:** the exact certificates and the explicit states behind the intervals (map task, gates G5-G7; G6 first part NOT COMPLETE); the conversion of the public files (G1 NOT COMPLETE); the unit tests of gate G8 were not re-run; the perceptron in distribution and at n = 115 and architecture 1 were not computed (Sec. 3.6); the perceptron's test-range numbers have no independent recomputation.

## 9. Two sentences for an abstract, each traceable

1. At 57 qubits, standard conformal intervals calibrated on the public labels contain 41 of 45 held-out labels but the reference (DMRG) value of the staggered magnetization at 0 of the 45 training couplings and at 0 of the 4 test couplings, where the cubic model misses it by 2.28 to 3.73 times the tolerance.
   Source: `out/learn_real.json` -> `summary.57.models.poly3_invJ.real.ind` (label_covered, truth_covered), `.real.test` (truth_covered, miss_tau); sealed file `out/learn/results_cheap.json`.
2. Calibrated instead on the 18 labels that the published energy and site magnetizations certify to within half the tolerance (Jz = 4.3 to 6.0), intervals built from the exact energy bounds were narrower than the tolerance in 200 of 200 random splits (0.56 to 0.86 of it) and contained the reference value in 1000 of 1000 cases, for both declared models; the true value varies by only 0.30 of the tolerance over that range, so this shows that the guarantee survives the learner and its calibration, not that a hard function was learned.
   Source: `summary.57.f3.sets.S_1_2.models.M1|M2` (n_splits_W, n_pairs_C, width_tau_min, width_tau_max); `independent_check.sizes.57.f3.S_1_2.truth_change_over_tau` (post hoc line); sealed file `out/learn/f3_constructive.json`.

Alternative for the negative half: With all 45 public training labels in the calibration set, no learner using a constant-width score can return a guaranteed interval narrower than 5.35 times the tolerance at the test couplings (57 qubits; 4.65 at 115). Source: `summary.57.f2.test`, `summary.115.f2.test` (sealed file `out/learn/f2_floor.json`; carries the mark of gate G6).

Limits to keep next to them: sentence 2 is a statement about 18 couplings at large Jz, where the labels are already within 0.082 tau of the truth and the control model passes too; on all 26 certified labels the same test fails on width; the cases are (split, query) pairs drawn from these couplings, not independent trials; the exact intervals assume that the published energy and site magnetizations belong to one state.

