# Real data of arXiv:2606.15983: RESULTS (consolidated and audited)

Assembled on 2026-11-12 by the task `rd-audit` from the three partial result files of the tasks `rd-map`, `rd-predict` and
`rd-learn` (`results/RESULTS_map.md`, `results/RESULTS_predict.md`, `results/RESULTS_learn.md`), which are reproduced in
Parts I-III without any change to a number, and from an independent recomputation (Part 0, Sec. 0.3). Declaration:
`DECLARATION.md`, SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa`, hashed 2026-11-12T19:22:32Z.

**Label of the whole analysis, as in the declaration: DECLARED AFTER PARTIAL SIGHT. NOT BLIND.**

**Hypothesis behind every exact statement about a published label (declaration Sec. 10, item 6):** the published energy
and the published site magnetizations are expectation values of one and the same state. Gate G2 supports it at all 100
points; it cannot be proved from the files.

**Marks carried by every result:** gate G1 NOT COMPLETE (the converter was not re-run; Sec. 0.4 gives what was checked
instead); gate G6, first part, NOT COMPLETE with nothing checked (it concerns the 280 NOT CERTIFIED rows that rest on a
re-evaluated energy, and every "lower version" number of the learning tests); three pieces of (f1) NOT COMPUTED.
Extension E1 finished while this file was being assembled; its column is separate (Sec. 0.3) and replaces no
number of Parts I-III.

## Resumen en ocho líneas (español llano)

1. **Lo que los datos reales confirman.** Las energías publicadas coinciden con las que el artículo había leído de las
   figuras (entre 0,94 y 1,20 veces a 57 cúbits, 43 de 45 dentro del 5 %; entre 0,98 y 1,02 a 115). Con ellas, ninguna
   de las 152 casillas ya decididas del mapa cambia y las 13 que estaban sin decidir quedan decididas. Esta coincidencia
   se había visto antes de fijar las reglas: es una comprobación, no una predicción a ciegas.
2. **Lo que cambian.** Los estados publicados no cumplen la condición que el artículo daba por supuesta: su
   magnetización total queda por debajo del valor fijo en los 100 puntos (poco, pero siempre). Por eso «garantizado
   desde 3,2, 29 de 45 puntos» deja de ser una afirmación sobre las etiquetas reales.
3. **Lo que ahora queda demostrado sobre las etiquetas del propio conjunto**, con aritmética exacta y usando solo la
   energía y la magnetización publicadas: la magnetización alternada está a menos de la tolerancia del valor verdadero
   en 26 de los 45 puntos de entrenamiento a 57 cúbits (acoplamientos de 3,5 a 6,0) y en 21 de 45 a 115 (de 4,0 a 6,0);
   la correlación media entre vecinos, en 27 y en 21.
4. **También queda demostrado, con estados concretos,** que la energía no puede garantizar esas dos etiquetas hasta 3,1
   (57 cúbits) y hasta 3,0 (115), ni ninguna de las siete etiquetas en los cuatro puntos de prueba. Allí la energía
   tendría que ser más de 110 veces más precisa a 57 cúbits (más de 79 veces a 115).
5. **Lo que la simulación había anunciado y se cumple.** Las etiquetas reales se desvían hacia el lado más ordenado en
   32 785 de 32 800 casos y el error baja al crecer el acoplamiento. Un modelo entrenado con ellas falla el valor
   verdadero, fuera del rango de entrenamiento, por entre 2,28 y 3,73 veces la tolerancia a 57 cúbits, y sus intervalos
   habituales contienen las etiquetas nuevas pero no el valor verdadero.
6. **Lo que falló.** La curva que relaciona el sesgo con el error de energía no supera su prueba con las etiquetas
   reales: a 115 cúbits el sesgo real es alrededor de una cuarta parte menor de lo que dice la curva (12 de 19 cocientes
   fuera de la banda). Esa parte del artículo vale solo para la primera etapa del método. Y la prueba de aprendizaje con
   todas las etiquetas garantizadas no pasa (6 de 200 repartos a 57 cúbits); pasa con las 18 garantizadas a media
   tolerancia, donde el valor verdadero apenas cambia (unas 0,30 tolerancias).
7. **Lo que quedó sin terminar, y así se dice.** No se repitió la conversión de los archivos originales (una comparación
   directa, sin ejecutar nada, da iguales todos los números de los 302 archivos); las energías recalculadas de los
   estados usados en 280 casillas no se pudieron comprobar con los estados completos, que no están en este portátil;
   y faltan tres piezas de la prueba con redes neuronales. Las garantías nuevas, calculadas después de ver los datos,
   terminaron al final: a 115 cúbits amplían el rango garantizado hasta el acoplamiento 3,4 (27 de 45 puntos en vez de
   21); a 57 cúbits no cambian nada.
8. **Revisión independiente.** Un segundo juego de programas, escrito aparte y sin usar los programas sellados, rehízo
   los números principales desde los archivos publicados, los certificados y los estados guardados: ninguna diferencia
   más allá del redondeo. No se cambió ninguna regla y ningún fallo quedó escondido; la única advertencia de fondo es la
   de la línea 1.

# Part 0. Consolidated outcomes and the audit

## 0.1 Every declared analysis against its rule

Marks: **[S]** already seen before the hash (item of declaration Sec. 1 in brackets); **[N]** not seen before the hash;
**[S*]** not compared before the hash, but its outcome followed from seen numbers (audit finding rd-audit-01).

| # | analysis (declaration) | declared rule | outcome | numbers | mark |
|---|---|---|---|---|---|
| 1 | The published states and the sector (Sec. 2; reported in any case) | none | reported | sum_i <Z_i> - M_0 negative at 50 of 50 couplings at both sizes; -0.2342 to -0.0003 (n = 57), -0.4353 to -0.0026 (n = 115); q = (M_0 - M_real)/2 at most 0.1171 and 0.2177 | [S] T2 |
| 2 | Map predicted from the figures against the public energies, like-for-like under the sector hypothesis (Sec. 3) | confirmed iff no row is contradicted and every stored J* is met within 0.1 | **CONFIRMED** | 165 rows: 152 confirmed, 13 resolved from GRAY, 0 opened, 0 contradicted; J*_s = stored J* for all eight (3.2, 3.2, 4.0, 6.0, 6.0 at n = 57; 3.1, 3.1, 3.8 at n = 115) | m_s rows [S] F6; other labels [S*] |
| 3 | Exact certification of the published labels, window of energy and mean magnetization (Secs. 2, 3) | CERTIFIED (exact) iff the exact interval is at most tau wide, inside the certificate range | reported | m_s: J*_exact = 3.5 (26 of 45) at n = 57, 4.0 (21 of 45) at n = 115; Czz_bar: 3.4 (27) and 4.0 (21); same counts with the reference-free tolerance; one row inside the range fails: m_s, n = 57, Jz = 3.4, 1.0043 tau | [N] |
| 4 | NOT CERTIFIED from explicit states (Sec. 2) | (1 - q) w_in(E*) >= tau | reported | m_s and Czz_bar: Jz = 1.1-3.1 (n = 57), 1.1-3.0 (n = 115); all seven labels at 1.1-1.5; GRAY for m_s at 3.2-3.4 (n = 57) and 3.1-3.9 (n = 115) | [N] |
| 5 | Stored claims re-evaluated (Sec. 3) | as stored | C-A holds (both versions); C-B holds (both; no floor needed any more); C-C holds with the statuses of Sec. 2 and **does not hold** like-for-like | C-C: Z_bulk and Czz_edge at n = 57, Jz = 6.0 are CERTIFIED_s at the real energy (0.9770 and 0.9737 tau) | [N] |
| 6 | Accuracy factor at the test couplings (Sec. 4) | headline = smallest value over Jz = 1.1-1.4, rounded down to two digits | reported | m_s, same-coupling form: more than 110 (n = 57), more than 79 (n = 115); the paper's form: more than 85 and 60. Czz_bar: more than 57 and 49; 42 and 37 | m_s [S] F5; Czz_bar [N] |
| 7 | P1-P3, the sign (Sec. 5) | F >= 0.95 per family and size | **HOLDS** in 8 of 8 | F = 1, 0.999375, 1, 1 (n = 57: sites, edges, second neighbours, loops); 0.999652, 0.999545, 0.999243, 0.998333 (n = 115); 32,785 of 32,800 pairs | sites [S] F2, F8; others [N] |
| 8 | P4, the error falls with Jz (Sec. 5) | Spearman <= -0.9 | **HOLDS** in 8 of 8 | -0.9803 to -0.9719 (n = 57), -0.9955 to -0.9924 (n = 115) | sites [S] (order equal to F7); others [N] |
| 9 | P5, the bias-against-energy curve (Sec. 5) | mean miss <= 0.2 / 0.6 tau and every deciding ratio in [0.75, 1.3] | **FAIL** | mean miss 0.1110 and 0.1676 tau (both met); n = 57: 22 deciding ratios 0.8029-1.0455, none outside; n = 115: 19 deciding ratios 0.6087-0.8122, 12 below 0.75 | ratios [N] |
| 10 | Label filter (Sec. 6) | keep iff CERTIFIED (exact) | reported | m_s: keeps 26 (n = 57) and 21 (n = 115); largest miss kept 0.1746 and 0.0639 tau; drops 19 and 24, of which 15 and 21 are within tau | exact [N]; like-for-like [S] F9 |
| 11 | Exact 19-site value next to every label (Sec. 6) | none | reported | within 0.1344 tau (n = 57) and 0.1424 tau (n = 115) of the truth on the kept labels; 1.05-1.47 and 1.43-2.07 tau at the test couplings | no real datum |
| 12 | L1 (Sec. 7, f1) | the cubic misses the true m_s by more than tau at each of 1.1-1.4 (n = 57 decides) | **HOLDS** | 2.28-3.73 tau (n = 57); 2.37-5.07 tau (n = 115) | [N] |
| 13 | L2 (f1) | standard intervals cover the truth at none of the four test couplings | **HOLDS** | 0 of 4 at both sizes. The control trained on DMRG labels also covers 0 of 4 (it misses by 0.02-0.25 tau), so L2 does not isolate the label bias by itself | [N] |
| 14 | L3 (f1) | the 2(b) intervals calibrated on all 45 labels are wider than tau at every coupling (lower version) | **HOLDS** | 6.71-11.08 tau (n = 57); 5.92-9.40 tau (n = 115); mark of gate G6 | [N] |
| 15 | (f2) learner-independent floor | floor w_(42) > tau(x) at each test query | **HOLDS** | 6.42, 5.97, 5.62, 5.35 tau (n = 57); 5.49, 5.14, 4.86, 4.65 tau (n = 115), rounded down; mark of gate G6 | [N] |
| 16 | (f3) constructive test, PRIMARY: n = 57, S_p = S_1/2 (18 couplings, 4.3-6.0) | (W) in >= 90 % of splits and (C) in >= 90 % of pairs, both M1 and M2 | **PASS** | (W) 200 of 200, (C) 1000 of 1000 for both; 2q = 0.562-0.857 tau | [N] |
| 17 | (f3) secondary: n = 57, S (26 couplings) and S_3/4 (23) | same | **FAIL** and **FAIL** | S: (W) 6 of 200 for M1 and M2; S_3/4: 50 and 66 of 200; (C) holds everywhere | [N] |
| 18 | (f3) secondary: n = 115 | same | S and S_3/4 (the same 21 couplings): **PASS**; S_1/2: not run (10 couplings) | 2q = 0.859-1.028 tau | [N] |
| 19 | (f3) control M0 (cubic trained on uncertified labels as well) | same | passes wherever M1 and M2 pass | so the result is due to the calibration on certified labels, not to the training set | [N] |
| 20 | (f1) other models | reported | **NOT COMPLETE** | cubic and nearest-neighbour null: done. Perceptron: four test couplings at n = 57 only. Not computed: perceptron in distribution and at n = 115; the dataset paper's architecture 1 | - |
| 21 | Extension E1 (Sec. 3) | separate column; replaces nothing; the sets of (f3) are fixed without it | reported (finished 2026-11-12T21:56Z; 48 certificates, each proved by both verifiers) | m_s, n = 57: the new intervals at Jz = 3.2 and 3.3 are 1.1533 and 1.1145 tau wide, so nothing changes (26 of 45). m_s, n = 115: certified from Jz = 3.4 (27 of 45, against 21 with the stored certificates); Jz = 3.3: 1.0695 tau. Czz_bar, n = 115: 25 of 45 (Jz >= 3.6) | [N]; computed after every primary result was known |

Gates: G1 NOT COMPLETE; G2 PASS; G3 PASS; G4 PASS; G5 PASS; G6 first part NOT COMPLETE (0 of 150 components checked), second
part PASS; G7 PASS; G8 passed before the hash (records `checks/G8_*`). Details: Part I, Sec. 10.

## 0.2 What was already seen before the hash (declaration Sec. 1), in one place

- F2-F4: every energy at all 100 points; eps_real / eps_digitized; the energy error per site at Jz = 1.1-1.5.
- F5: the accuracy factor of m_s in both forms. F6, F9: the like-for-like status and the like-for-like filter counts of m_s.
- F7: the miss of the real m_s at all 100 points. F8 (and F2): the fraction of sites more ordered than DMRG.
- T2: sum_i <Z_i> - M_0 at every coupling. T3-T7: the consistency identity, energy differences, the authors' DMRG against
  this project's references, the multipliers of the stored certificates.
- Not seen: any label other than m_s against its reference (except the two site statistics); any status of a label
  other than m_s; any exact interval or interval width at a real energy; any quantity at the window of energy and mean
  magnetization; any ratio to the n = 19 curve; any learning result.
- Audit addition (rd-audit-01): the like-for-like outcome of row 2 for the six labels marked "not seen" was fixed by F3
  and F4 through the monotonicity of the window in the energy (Sec. 0.3, check A).

## 0.3 Independent audit (task `rd-audit`)

**Integrity.**
- `sha256sum DECLARATION.md` = `DECLARATION.sha256` = `checks/DECLARATION.sha256`. The three converted files and
  `out/S_sets.json` have their pinned SHA-256. `python -B -I checks/make_manifest.py --check`: 69 lines equal, 0 different.
- File times (when this file was assembled): of the 771 files under `out/`, `results/` and `e1/`, 716 are later than the
  hash file; the other 55 are the files of `out/n19/` (exact n = 19, no real datum, listed in Sec. 11 of the declaration
  as computed before the hash). No file of `code/`, `tests/`, `converted/` or `source/` is later than the hash. Three
  distinctive real values (two energies, one label) were searched in `tests/` and in the scratch folders of the review:
  before the hash they occur only in the declared first look. These are file times and a text search, not an external
  time stamp.
- `DEVIATIONS.md`: no sealed file was changed by any task (the three tasks re-hashed them). Its items are incomplete
  gates, output names, files added after the hash, parts not computed for cost, and descriptive sentences of the
  declaration checked against the data. None changes a rule, a threshold or a primary choice.

**Recomputation with own scripts** (`checks/rd_audit_map.py`, `checks/rd_audit_predict_learn.py`,
`checks/rd_audit_integrity.py`; they import nothing from `code/`; outputs next to them). "Stored" is the output of the
sealed run.

| item | mine | stored | difference |
|---|---|---|---|
| Departure from the sector, 100 points | negative at 100; five couplings below | same | 9e-16 |
| Exact intervals of m_s and Czz_bar, every row where one exists | 108 rows | 108 rows | identical as exact rationals, both ends and both flags |
| J*_exact and counts, both tolerances | 3.5 (26), 3.4 (27), 4.0 (21), 4.0 (21) | same | none |
| NOT CERTIFIED side of m_s, 100 rows (own hull; four rows also by a linear program) | 21 and 20 couplings | same | 2e-12 in the width |
| Like-for-like statuses at the real energy, 165 rows (own outer and inner bounds) | 152 / 13 / 0 / 0 | same | none |
| Accuracy factors, both forms, m_s and Czz_bar (own thresholds from the stored states) | 396.22, 268.83, 180.69, 116.47 (m_s, n = 57, form A) and the rest | same | below 1e-6 relative |
| P1-P3 and P4, four families, two sizes | 32,785 of 32,800 | same | below 1e-9 |
| n = 19 curve (own exact diagonalization, 50 couplings, 26 levels) and P5 | FAIL; ratios below | FAIL | curve points 8e-9 |
| Filter and n = 19 comparison | 26 / 21 kept; 0.1344 / 0.1424 tau | same | none |
| Floor of (f2) | 6.4284, 5.9754, 5.6277, 5.3563; 5.4953, 5.1401, 4.8656, 4.6500 | same | below 1e-8 |
| (f3): sets, 200 splits of five (size, set) cases, three models | PASS / FAIL as in rows 16-19 | same | 2e-12 in q and widths |
| L1 and L2 for the cubic (L3 was not recomputed) | 3.720, 3.175, 2.695, 2.286 tau (n = 57); 0 of 4 | same to the digits printed | - |

Five couplings per size, sum_i <Z_i> - M_0 and q: n = 57: 1.1: -0.234198, 0.117099; 1.6: -0.095047, 0.047524; 3.4: -0.008297, 0.004148; 4.0: -0.004367, 0.002183; 6.0: -0.000729, 0.000365. n = 115: 1.1: -0.435201, 0.217600; 1.6: -0.202599, 0.101300; 3.4: -0.020793, 0.010396; 4.0: -0.011457, 0.005728; 6.0: -0.002675, 0.001338.

Exact interval of m_s at six couplings per size (ends rounded outward; width in units of tau and of the reference-free
tolerance; width with M = M_0 alone; the two couplings that decide J*_exact are the first two of n = 57 and, at
n = 115, Jz = 3.9, where no m_s certificate exists, and 4.0):

| n | Jz | interval | width / tau | width / tau_rf | at M_0 alone | CERTIFIED (exact) | label, truth |
|---|---|---|---|---|---|---|---|
| 57 | 3.4 | [0.90776, 0.96459] | 1.0043 | 1.0433 | 0.9860 | no | 0.953217, 0.943039 |
| 57 | 3.5 | [0.91420, 0.96590] | 0.9105 | 0.9423 | 0.8942 | yes | 0.955448, 0.946167 |
| 57 | 3.6 | [0.91997, 0.96750] | 0.8346 | 0.8609 | 0.8191 | yes | 0.957445, 0.949046 |
| 57 | 4.0 | [0.93776, 0.97280] | 0.6092 | 0.6227 | 0.5995 | yes | 0.964851, 0.958546 |
| 57 | 5.0 | [0.96234, 0.98122] | 0.3231 | 0.3268 | 0.3187 | yes | 0.976306, 0.973299 |
| 57 | 6.0 | [0.97421, 0.98705] | 0.2179 | 0.2195 | 0.2164 | yes | 0.983597, 0.981396 |
| 115 | 4.0 | [0.94303, 0.97271] | 0.5148 | 0.5246 | 0.5018 | yes | 0.964699, 0.961015 |
| 115 | 4.1 | [0.94220, 0.97511] | 0.5696 | 0.5820 | 0.5577 | yes | 0.966516, 0.962858 |
| 115 | 4.5 | [0.94646, 0.98060] | 0.5871 | 0.6011 | 0.5772 | yes | 0.971458, 0.969068 |
| 115 | 5.0 | [0.95455, 0.98563] | 0.5314 | 0.5427 | 0.5252 | yes | 0.976834, 0.974872 |
| 115 | 5.5 | [0.96662, 0.98665] | 0.3408 | 0.3452 | 0.3361 | yes | 0.980307, 0.979188 |
| 115 | 6.0 | [0.97774, 0.98627] | 0.1446 | 0.1453 | 0.1413 | yes | 0.983287, 0.982484 |

The six certificates behind the rows that decide J*_exact (n = 57: the two at Jz = 3.4 and the two at 3.6 whose pairs
give the row at 3.5; n = 115: the two at 4.0) were re-proved in this audit with the independent exact verifier
`scratch/math-rigorous-bounds/myverify.py` (verified Cholesky): operator identity exact, every cluster inequality
proved, bound equal to the certificate's claim, in 6 of 6 (`checks/rd_audit_g5_reproved.json`). All six are also among
the 196 certificates re-proved earlier by `math-rigorous-bounds`.

Two NOT CERTIFIED rows from explicit states, and two more (m_s; hull by pairs and by a linear program, equal to 1e-8):

| n | Jz | q | reference state | E* | pool | hull of m_s at E* | (1 - q) width | status |
|---|---|---|---|---|---|---|---|---|
| 57 | 1.1 | 0.117099 | R3 of 1.1 | -25.436998 | 109 states stored at 1.1 | [0.057872, 0.819401] | 18.82 tau | NOT CERTIFIED |
| 57 | 3.1 | 0.006084 | R3 of 3.0 | -53.280078 | 198 states of 3.0 and 3.3, re-evaluated | [0.899037, 0.956893] | 1.028 tau | NOT CERTIFIED (rests on re-evaluated energies) |
| 115 | 1.4 | 0.134436 | R3 of 1.4 | -59.586801 | 56 states stored at 1.4 | [0.397020, 0.895752] | 9.82 tau | NOT CERTIFIED |
| 115 | 3.0 | 0.015845 | R3 of 3.0 | -106.524151 | 42 states stored at 3.0 | [0.898502, 0.957502] | 1.038 tau | NOT CERTIFIED |

P5 ratios at five couplings (own n = 19 diagonalization), at Jz = 1.1, 1.5, 2.0, 2.5, 2.9: n = 57: 0.8512, 0.8062, 0.8392, 0.8212, 0.9454; n = 115: 0.8122, 0.6087, 0.7313, 0.6962, 0.7331 (below 0.75 at 1.5, 2.0, 2.5, 2.9).
Equal to the stored ones to the digits shown. From my numbers over the 50 couplings: mean miss 0.1110 tau (n = 57) and 0.1676 tau
(n = 115); deciding ratios outside the band: 0 of 22 and 12 of 19; one decision: FAIL.

One split of (f3) end to end (n = 57, S_1/2, split 0; training 4.7, 4.9, 5.2, 5.4; calibration 4.5, 4.6, 5.1, 5.3, 5.5, 5.6, 5.8, 5.9, 6.0; queries 4.3, 4.4, 4.8, 5.0, 5.7). M1: q = 0.019479137, 2q / tau(x) = 0.6735, 0.6724, 0.6687, 0.6671, 0.6630, miss / tau(x) = 0.0688, 0.0666, 0.0635, 0.0646, 0.0766, truth inside at 5 of 5. M2: q = 0.019075297, 2q / tau(x) = 0.6596, 0.6585, 0.6548, 0.6533, 0.6492, miss / tau(x) = 0.0500, 0.0545, 0.0648, 0.0669, 0.0663, truth inside at 5 of 5. M0: q = 0.020374537, 2q / tau(x) = 0.7045, 0.7033, 0.6994, 0.6978, 0.6934, miss / tau(x) = 0.0877, 0.0837, 0.0739, 0.0718, 0.0732, truth inside at 5 of 5
(control; trained on the 31 real training labels outside the calibration and query couplings). The 200 splits of every set
equal the stored ones; q and the widths agree to 2e-12.

**Three extra checks of the audit (post hoc; they decide nothing).**
- *Check A, why the map could not be contradicted.* At every stored training coupling the public energy error lies
  inside the window that the figures-based map had assumed (0.967-1.038 times the digitized value at n = 57, 0.986-1.011 at
  n = 115, against a window of at least 0.8-1.2); at the four test couplings it is 1.28-1.79 times (n = 57) and
  1.28-1.90 times (n = 115) the floor of 0.012 per site that the map had assumed, so above its window. A window grows
  with the energy: a row predicted CERTIFIED stays so while the energy is below the upper end of its window, and a row
  predicted NOT CERTIFIED stays so while the energy is above the lower end. All 152 decisive predicted statuses (112 at
  training couplings, 40 at test couplings) carry over for that reason alone; the 13 GRAY rows are the only ones whose
  outcome was open.
- *Check B, second route for gate G1 (not the declared gate).* The 302 archive members named in the converted files have
  the recorded SHA-256 and size. Their byte streams were tokenized with `pickletools.genops` (a parser: nothing is
  unpickled, imported or executed) and the numbers that follow each field name were compared with the converted JSON:
  every float field and every integer field (pair lists, loop sites) of every member is equal bit for bit (dataset,
  comparison variant and DMRG). Not covered: the DMRG parameter record and one boolean flag.
- *Check C.* Every explicit witness of an m_s row lies inside the exact interval of the same row (no violation), as it must.

**Extension E1 (finished during the audit; separate column).** E1 ended on 2026-11-12T21:56:33Z with 48 certificates
(m_s; n = 57 at Jz = 3.2 and 3.3; n = 115 at 3.3, 3.6 and 5.0), and its task built the declared E1 column with the sealed
map code in `e1/map_e1/`. With my own code (`checks/rd_audit_e1_preview.py`): each of the 48 certificates has two agreeing
verification records (stored verifier and independent verifier) and satisfies the claim identity; my E1 intervals equal
the declared ones as exact rationals on all 117 rows that have one. Widths are rounded up.

| n | label | stored certificates (the declared result) | with E1 (separate column) | rows that are new in the range |
|---|---|---|---|---|
| 57 | m_s | J*_exact 3.5, 26 of 45 | 3.5, 26 of 45 | Jz = 3.2: 1.1533 tau; 3.3: 1.1145 tau; neither certified |
| 57 | Czz_bar | 3.4, 27 of 45 | 3.4, 27 of 45 | Jz = 3.2: 1.0623 tau; 3.3: 1.0214 tau; neither certified |
| 115 | m_s | 4.0, 21 of 45 | 3.4, 27 of 45 | Jz = 3.3: 1.0695 tau, not certified; 3.4-3.9: 0.9013, 0.8466, 0.7401, 0.7221, 0.6456, 0.5940 tau, certified; 19 rows of the old range become narrower (largest gain at Jz = 5.0: 0.5314 to 0.2826 tau) |
| 115 | Czz_bar | 4.0, 21 of 45 | 3.6, 25 of 45 | Jz = 3.6-3.9: 0.9576, 0.7781, 0.6379, 0.5766 tau (these intervals existed and now lie inside the range); 3.4 and 3.5 are wider than tau |

The counts are the same with the reference-free tolerance, and every label and reference value lies inside its interval.
The E1 certificates were computed after every primary result was known. They are theorems: they extend the range and
replace no number of Parts I-III, and the sets of (f3) stay those fixed without them. E1-extended sets (secondary):
n = 115: |S| = 27, |S_3/4| = 25, |S_1/2| = 18; n = 57: unchanged. The secondary learning runs on these sets
(`e1/learn_e1/`) were not audited.

**Findings of the audit** (details and proposed handling: `paper/reviews/R10_2026-11-12/reports/rd-audit.md`).

- **rd-audit-01 (major, wording).** "Confirmed by the data" (row 2) was not an open test. Given F3 and F4, which were
  seen before the hash, no decisive row could change (check A). What the public data add to the like-for-like map is
  (i) the agreement of the digitization with the public energies, (ii) the removal of the assumed floor at the test
  couplings, (iii) the 13 resolved rows. The paper must say this and must not present row 2 as a prediction borne out
  on six unseen label types.
- **rd-audit-02 (major, process).** (f1) is incomplete: three declared pieces were not computed. The paper can state the
  realistic test on the public labels for the cubic and the nearest-neighbour null (and the perceptron at the four test
  couplings of n = 57) only, or the pieces must be run first.
- **rd-audit-03 (major, process).** Gate G1 stays NOT COMPLETE as declared. Check B makes a conversion error in a float
  or integer field very unlikely; one run of the converter by a task that is allowed to run it closes the gate.
- **rd-audit-04 (major, process).** Gate G6, first part, stays NOT COMPLETE with nothing checked. For m_s it concerns 12
  (n = 57) and 11 (n = 115) of the NOT CERTIFIED couplings, all off the grid; the statements at the test couplings, at
  the other grid couplings and the whole certified side do not depend on it.
- **rd-audit-05 (minor, process).** Extension E1 finished during the audit; its map column agrees with my own
  computation on all 117 rows. Its reading of "stored optimizer settings" (the search grid is steered by the public
  energy) awaits the coordinator's confirmation and has no dated entry in `DEVIATIONS.md` yet; neither has this audit
  (text ready in the report). The secondary learning runs on the E1 sets were not audited.
- **rd-audit-06 (minor, wording).** Two "HOLDS" need their control next to them wherever they are printed: L2 (the
  control on DMRG labels has zero coverage in the test range too) and the PASS of (f3) (the control M0 passes as well, and
  the truth changes by 0.294-0.301 tau over the primary set). Both are stated in Part III; neither was played down.
- **rd-audit-07 (note).** No disagreement beyond rounding between the recomputation and the stored outputs; no rule was
  bent; every failure (P5; (f3) on S and S_3/4; claim C-C like-for-like; the row at Jz = 3.4) is reported with the same
  prominence as the passes.

## 0.4 What is not complete or not computed, and what would complete it

| item | state | to complete |
|---|---|---|
| Gate G1 | hashes equal; converter not re-run; check B of Sec. 0.3 | `python -B -I code/run_map.py --g1-rerun --out <new folder>` in a task that is allowed to run the converter |
| Gate G6, first part | 0 of 150 components checked (no tensors on the laptop) | bring the tensors of the 150 components to the laptop (needs the author's yes for cloud access), or keep the mark on the 280 rows |
| (f1) perceptron in distribution (n = 57), perceptron at n = 115, architecture 1 | not computed (about 22, more than 22 and 13 CPU-hours) | commands in Part III, Sec. 3.6 |
| Extension E1 | finished and collected by its task (`e1/map_e1/`, `e1/learn_e1/`); map column audited (Sec. 0.3) | a dated entry in `DEVIATIONS.md` for the E1 task; an audit of the secondary learning runs if they are to be printed |

## 0.5 Post hoc material (not declared; decides nothing)

Part I Sec. 12, Part II Sec. 8, Part III Sec. 7, and the three checks of Sec. 0.3. Nothing in them changes an outcome.

## 0.6 Re-executed, only read, not checked (this audit)

- **Re-executed:** the hash and manifest checks; own recomputation of every item of the table of Sec. 0.3 from
  `converted/`, the certificate files, the stored state records, chains and thresholds; own exact diagonalization at
  n = 19 (50 couplings); the independent exact verifier on six certificates; the parser-only comparison of the archive.
- **Only read:** the sealed code where a convention had to be understood (never imported); `DEVIATIONS.md`; the three
  partial result files and the reports of the three tasks; the supplementary check of gate G6 on six tensor files; the
  status file of E1.
- **Not checked:** the conversion as declared (G1); any energy from tensors (G6, first part); the perceptron numbers;
  the secondary rows (first-stage energy, comparison variant); the upper and lower versions of Proposition 2 for the cubic
  beyond the floor; the unit tests of G8 (not re-run); the secondary learning runs on the E1 sets; that the hash was made when the file says.

# Part I. The map on the real energies, the accuracy factor, the filter, the gates

Verbatim from `results/RESULTS_map.md` (SHA-256 `73f494cb8721ff93f7793918a64d571bebf29882593b0d5cc36f95bc96d40c92`), without its Spanish summary. Original title: "Map on the real data of arXiv:2606.15983: RESULTS (Secs. 2, 3, 4, 6 and gates G1-G7 of the declaration)".

Written by the task `rd-map` on 2026-11-12 from the outputs of the sealed code (`code/run_map.py`, run from 2026-11-12T19:28:57Z to 2026-11-12T19:31:01Z UTC, after the hash of 2026-11-12T19:22:32Z). Declaration SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa`, checked against `DECLARATION.sha256` before anything was read. **Label of the whole analysis: DECLARED AFTER PARTIAL SIGHT. NOT BLIND.** Every block below says which of its numbers had been seen before the hash (items F1-F10 and T1-T7 of Sec. 1 of the declaration) and which are new.

Printed numbers are rounded outward (interval ends away from the interval, widths and misses up, margins down). The exact rationals are in `out/map_rows.json`; the same rows in compact form are in `out/map_real.json`. This file is produced by `results/make_results_map.py`, which copies and does not recompute.

**Two marks that go with every result of this file.** Gate G1 is NOT COMPLETE: the three converted files have the SHA-256 pinned in the declaration and the archive has its pinned SHA-256, but the converter was not run again (it uses a restricted unpickler, and this task was told to unpickle nothing). Gate G6 (first part) is NOT COMPLETE: none of the 150 witness components selected by the declared rule has its tensors on the laptop, so none was checked; 280 of the 439 NOT CERTIFIED rows rest on an energy re-evaluated by the linear rule and carry this mark. Extension E1 was not available when the map was run: there is no E1 column.

## I-0. First, plainly: what the real data allow the paper to say about the dataset's own labels, and what they do not

Hypothesis H behind every statement about a real label (decision 6 of the declaration): the published energy and the published site magnetizations are expectation values of one and the same state. Gate G2 supports it at all 100 points; it cannot be proved from the files.

**What they allow.**

1. *The published states are not in the sector.* sum_i <Z_i> is below M_0 at all 50 couplings of both sizes; q = (M_0 - M_real)/2 runs from 0.00018 to 0.1171 at n = 57 and from 0.00133 to 0.2177 at n = 115 (Sec. 1 below; seen before the hash, item T2). The paper's sector statuses are therefore not statements about these labels.
2. *Certified in exact arithmetic from the energy and the mean magnetization (new).* Under H, the published m_s is within tau of the sector ground-state value at every training coupling Jz = 3.5-6.0 (n = 57: 26 of 45) and Jz = 4.0-6.0 (n = 115: 21 of 45); the published Czz_bar at Jz = 3.4-6.0 (n = 57: 27 of 45) and Jz = 4.0-6.0 (n = 115: 21 of 45). The counts are the same with the reference-free tolerance. The intervals are between 0.217 and 0.911 tau wide (m_s, n = 57), 0.144 and 0.665 (m_s, n = 115), 0.228 and 0.931 (Czz_bar, n = 57), 0.154 and 0.513 (Czz_bar, n = 115). Every certified label and its truth lie inside its interval (gate G7: 95 rows, no violation).
3. *Not certifiable from the energy and the mean magnetization, by explicit states (new for the real window).* Two explicit states with energy at most E_real and mean magnetization M_real have labels at least tau apart for m_s at Jz = 1.1-3.1 (n = 57) and 1.1-3.0 (n = 115), for Czz_bar at 1.1-3.1 and 1.1-3.0, and for all seven labels at the four test couplings 1.1-1.4 and at 1.5, at both sizes. At n = 57 the four local labels are NOT CERTIFIED at 42, 44, 42 and 45 of the 45 training couplings (Z_bulk, Z_boundary, Czz_edge, Z_loop).
4. *The map predicted from the figures is confirmed by the data under the declared rule* (like-for-like, sector hypothesis): 152 rows confirmed, 13 resolved from GRAY, 0 opened, 0 contradicted, out of 165 with data; the eight stored J* are reproduced exactly (Sec. 6).
5. *Accuracy factor at the test couplings (in-sector thresholds).* For m_s the energy per site would have to be more than 110 times (n = 57) and more than 79 times (n = 115) more accurate at Jz = 1.1-1.4 (form A; form B: more than 85 and 60). For Czz_bar: more than 57 and 49 (form A), 42 and 37 (form B). The in-sector window is a subset of what the energy and the mean magnetization allow, so each factor is a lower bound on what the weaker hypothesis would require (Sec. 7).
6. *Filter.* Keeping a training label iff its row is CERTIFIED (exact) keeps 26 (n = 57) and 21 (n = 115) m_s labels; every kept label is within 0.175 tau and 0.064 tau of the truth, and each carries the guarantee of item 2 (Sec. 8).

**What they do not allow.**

1. *To print the like-for-like numbers as properties of the real labels.* "Certified from J* = 3.2, 29 of 45" (n = 57) and "from 3.1, 30 of 45" (n = 115) are statements about in-sector states at the real energy. For the real labels the numbers are J*_exact = 3.5 (26 of 45) and 4.0 (21 of 45) for m_s.
2. *Any certificate of a real label other than m_s and Czz_bar.* There are no exact certificates for C2_bar or for the four local labels; in the window of Sec. 2 these rows are NOT CERTIFIED or GRAY, never CERTIFIED.
3. *Any statement in the undecided band.* m_s: Jz = 3.2-3.4 (n = 57) and 3.1-3.9 (n = 115); Czz_bar: 3.2-3.3 and 3.1-3.9. There no row is CERTIFIED (exact) under the declared rule and the explicit states do not separate by tau (for Czz_bar at n = 115, Jz = 3.6-3.9, a proved interval within tau exists but lies outside the declared range and is not counted). At n = 57, Jz = 3.4, m_s is inside the certificate range and is NOT certified: the exact interval is 1.0043 tau wide; it would be certified only if the energy error were at most 0.9913 of the published one.
4. *"No local label is certified at any computed point" as a like-for-like statement at the real energies.* Under the sector hypothesis two local rows are CERTIFIED_s at the real energy: Z_bulk and Czz_edge at n = 57, Jz = 6.0 (outer widths 0.9770 and 0.9737 tau; the energy could rise by factors 1.054 and 1.062 before the status changes). The stored map had both GRAY and its central reading already passed them; the relation is "resolved", not "contradicted". In the window of Sec. 2 no local label is certified.
5. *That the filter selects the accurate labels.* It selects the labels that carry a guarantee. Of the 19 dropped m_s labels at n = 57, 15 are within tau of the truth (10 within tau/2); of the 24 dropped at n = 115, 21 (17).
6. *Completeness of gates G1 and G6 (first part), and anything about extension E1* (see the two marks above and Sec. 10).

## I-1. The departure from the sector at every coupling (finding of Sec. 2 of the declaration)

Rule: none (a finding, reported in any case). **Seen before the hash (T2):** all of it. M_real = sum_i `z_basis_opt`[i]; M_0 = 9 (n = 57), 19 (n = 115); q = (M_0 - M_real)/2. M_real - M_0 is negative at 50 of 50 couplings (n = 57) and 50 of 50 (n = 115); |M_real - M_0| <= 0.05 at 40 and 34 couplings.

| Jz | n = 57: M_real - M_0 | q | de_real | n = 115: M_real - M_0 | q | de_real |
|---|---|---|---|---|---|---|
| 1.1 | -0.234198 | 0.117099 | 0.021400 | -0.435201 | 0.217600 | 0.022729 |
| 1.2 | -0.182177 | 0.091088 | 0.019759 | -0.382272 | 0.191136 | 0.019683 |
| 1.3 | -0.142952 | 0.071476 | 0.018017 | -0.319376 | 0.159688 | 0.017174 |
| 1.4 | -0.125230 | 0.062615 | 0.015424 | -0.268872 | 0.134436 | 0.015418 |
| 1.5 | -0.109602 | 0.054801 | 0.012613 | -0.262089 | 0.131045 | 0.015706 |
| 1.6 | -0.095047 | 0.047524 | 0.011355 | -0.202599 | 0.101300 | 0.011680 |
| 1.7 | -0.084983 | 0.042492 | 0.010245 | -0.172730 | 0.086365 | 0.010396 |
| 1.8 | -0.066393 | 0.033197 | 0.008873 | -0.143132 | 0.071566 | 0.009622 |
| 1.9 | -0.055223 | 0.027611 | 0.008690 | -0.126607 | 0.063304 | 0.008303 |
| 2.0 | -0.054181 | 0.027091 | 0.007507 | -0.109764 | 0.054882 | 0.007292 |
| 2.1 | -0.036848 | 0.018424 | 0.007435 | -0.090083 | 0.045042 | 0.007072 |
| 2.2 | -0.033880 | 0.016940 | 0.006835 | -0.086739 | 0.043370 | 0.005725 |
| 2.3 | -0.027140 | 0.013570 | 0.006285 | -0.074168 | 0.037084 | 0.005266 |
| 2.4 | -0.027168 | 0.013584 | 0.005365 | -0.062634 | 0.031317 | 0.004750 |
| 2.5 | -0.024316 | 0.012158 | 0.004281 | -0.058501 | 0.029251 | 0.004254 |
| 2.6 | -0.022117 | 0.011059 | 0.004347 | -0.051185 | 0.025592 | 0.003876 |
| 2.7 | -0.020207 | 0.010104 | 0.003739 | -0.045976 | 0.022988 | 0.003539 |
| 2.8 | -0.015719 | 0.007860 | 0.003737 | -0.035094 | 0.017547 | 0.003722 |
| 2.9 | -0.015138 | 0.007569 | 0.003474 | -0.034843 | 0.017422 | 0.003099 |
| 3.0 | -0.013531 | 0.006766 | 0.002810 | -0.031690 | 0.015845 | 0.002940 |
| 3.1 | -0.012168 | 0.006084 | 0.002709 | -0.028894 | 0.014447 | 0.002404 |
| 3.2 | -0.011065 | 0.005533 | 0.002533 | -0.024941 | 0.012471 | 0.002581 |
| 3.3 | -0.009163 | 0.004581 | 0.002700 | -0.019924 | 0.009962 | 0.002480 |
| 3.4 | -0.008297 | 0.004148 | 0.002470 | -0.020793 | 0.010396 | 0.001946 |
| 3.5 | -0.007170 | 0.003585 | 0.002208 | -0.017389 | 0.008695 | 0.001944 |
| 3.6 | -0.006697 | 0.003348 | 0.002123 | -0.017016 | 0.008508 | 0.001694 |
| 3.7 | -0.005392 | 0.002696 | 0.002576 | -0.014386 | 0.007193 | 0.001725 |
| 3.8 | -0.005514 | 0.002757 | 0.001749 | -0.013827 | 0.006913 | 0.001502 |
| 3.9 | -0.005057 | 0.002528 | 0.001854 | -0.012495 | 0.006247 | 0.001446 |
| 4.0 | -0.004367 | 0.002183 | 0.001717 | -0.011457 | 0.005728 | 0.001248 |
| 4.1 | -0.004005 | 0.002003 | 0.001705 | -0.010358 | 0.005179 | 0.001303 |
| 4.2 | -0.003729 | 0.001864 | 0.001467 | -0.009505 | 0.004752 | 0.001317 |
| 4.3 | -0.003641 | 0.001820 | 0.001122 | -0.008420 | 0.004210 | 0.001247 |
| 4.4 | -0.002917 | 0.001458 | 0.001382 | -0.007700 | 0.003850 | 0.001005 |
| 4.5 | -0.002737 | 0.001369 | 0.001352 | -0.007861 | 0.003931 | 0.000911 |
| 4.6 | -0.002499 | 0.001250 | 0.001345 | -0.006888 | 0.003444 | 0.000972 |
| 4.7 | -0.002267 | 0.001133 | 0.001264 | -0.006449 | 0.003225 | 0.000921 |
| 4.8 | -0.002211 | 0.001105 | 0.001145 | -0.004898 | 0.002449 | 0.001418 |
| 4.9 | -0.001773 | 0.000886 | 0.001102 | -0.005478 | 0.002739 | 0.000741 |
| 5.0 | -0.001848 | 0.000924 | 0.001006 | -0.004743 | 0.002372 | 0.000857 |
| 5.1 | -0.001487 | 0.000743 | 0.001293 | -0.004765 | 0.002383 | 0.000609 |
| 5.2 | -0.001465 | 0.000733 | 0.001101 | -0.004098 | 0.002049 | 0.000842 |
| 5.3 | -0.001330 | 0.000665 | 0.000913 | -0.004169 | 0.002085 | 0.000561 |
| 5.4 | -0.000611 | 0.000306 | 0.001942 | -0.003785 | 0.001892 | 0.000656 |
| 5.5 | -0.001198 | 0.000599 | 0.000939 | -0.003677 | 0.001838 | 0.000511 |
| 5.6 | -0.001099 | 0.000550 | 0.000821 | -0.003395 | 0.001697 | 0.000470 |
| 5.7 | -0.000586 | 0.000293 | 0.001987 | -0.003092 | 0.001546 | 0.000522 |
| 5.8 | -0.000982 | 0.000491 | 0.000870 | -0.002691 | 0.001346 | 0.000787 |
| 5.9 | -0.000370 | 0.000185 | 0.001857 | -0.002782 | 0.001391 | 0.000409 |
| 6.0 | -0.000729 | 0.000365 | 0.000878 | -0.002675 | 0.001338 | 0.000398 |

de_real = (E_real - E0)/n was seen before the hash (F2, F4). E0 is this project's reference at the 18 + 16 couplings of the stored map and the authors' DMRG value elsewhere (gate G4 compares the two where both exist).

## I-2. Exact intervals of m_s and Czz_bar at the real energies (certified side of Sec. 2)

Rule: I = [-U_-, U_+], U_sigma = max over M in {M_real, M_0} of the smallest proved bound of the pool, at E_real + 1e-6 and with the worse of M_real +- 1e-6; CERTIFIED (exact) iff width(I) <= tau = 0.06 |O_GS| and the coupling lies in the declared range ([3.4, 6.0] at n = 57, [4.0, 6.0] at n = 115). Reference-free tolerance: tau_rf = 0.06 min |O| over I. Arithmetic: `fractions.Fraction`. **New: every number of this section** (no exact interval at a real energy had been computed before the hash). Certificates: 220 files, 214 distinct, 140 used (n = 57: 120; n = 115: 20).

| n | label | J*_exact (tau) | CERTIFIED (exact) of 45 (tau) | J*_exact (tau_rf) | of 45 (tau_rf) | certified couplings |
|---|---|---|---|---|---|---|
| 57 | m_s | 3.5 | 26 | 3.5 | 26 | 3.5-6.0 |
| 57 | Czz_bar | 3.4 | 27 | 3.4 | 27 | 3.4-6.0 |
| 115 | m_s | 4.0 | 21 | 4.0 | 21 | 4.0-6.0 |
| 115 | Czz_bar | 4.0 | 21 | 4.0 | 21 | 4.0-6.0 |

Outcome against what the declaration expected (Sec. 3, "Expected and stated now"): J*_exact does not lie below 3.4 (n = 57) or 4.0 (n = 115), as stated. At n = 115 it sits at the lower end of the certificate range for both labels. At n = 57 it is 3.5 for m_s: the row at 3.4 is not certified (width 1.0043 tau).

Inside the declared range, CERTIFIED (exact) at 26 of 27 couplings (m_s, n = 57), 21 of 21 (m_s, n = 115), 27 of 27 (Czz_bar, n = 57) and 21 of 21 (Czz_bar, n = 115): the distance between J*_exact and the like-for-like J*_s is set by where certificates exist, except for the one row at n = 57, Jz = 3.4.

What leaving the sector hypothesis costs on the certified side (descriptive; the declaration expected a slight widening from the term mu (M_real - M_0)): width(I) minus the width that the same certificates give at M = M_0 alone, over tau, on the rows of the declared range: at most 0.0184 (m_s, n = 57), 0.0131 (m_s, n = 115), 0.0160 (Czz_bar, n = 57), 0.0156 (Czz_bar, n = 115).

The one row of the declared range that is not certified, m_s at n = 57, Jz = 3.4, in detail (descriptive, post hoc): the same certificates give 0.9860 tau at M = M_0 alone and 1.0042 tau at M = M_real alone; the declared interval, the hull over both, is 1.0043 tau wide. An in-sector state at this energy would be within tau; the published mean magnetization (q = 0.00415) takes the row above tau. Its real label misses the truth by 0.1799 tau.

**n = 57, m_s.** Columns: interval I (ends rounded outward); width over tau and over tau_rf (rounded up); C = CERTIFIED (exact) with tau / with tau_rf; real label; its miss over tau (seen for m_s, F7; new for Czz_bar); truth O_GS; margin = largest energy error at which the row stays certified, over eps_real (rounded down; above 1 for a certified row); what decides each end.

| Jz | eps_real | I | width/tau | width/tau_rf | C tau / tau_rf | real label | miss/tau | truth | margin | lower end | upper end |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.4 | 0.14079 | [0.907761, 0.964584] | 1.0043 | 1.0433 | no / no | 0.953217 | 0.1799 | 0.943039 | 0.9913 | M_real, direct m_s@3.4 | M_0, direct m_s@3.4 |
| 3.5 | 0.12586 | [0.914207, 0.965892] | 0.9105 | 0.9423 | C / C | 0.955448 | 0.1635 | 0.946167 | 1.2040 | M_real, pair m_s@3.4+m_s@3.6 | M_0, pair m_s@3.4+m_s@3.6 |
| 3.6 | 0.12099 | [0.919971, 0.967492] | 0.8346 | 0.8609 | C / C | 0.957445 | 0.1475 | 0.949046 | 1.3907 | M_real, direct m_s@3.6 | M_0, direct m_s@3.6 |
| 3.7 | 0.14681 | [0.920697, 0.971006] | 0.8811 | 0.9107 | C / C | 0.961670 | 0.1746 | 0.951703 | 1.2533 | M_real, pair m_s@3.6+m_s@4.0 | M_0, pair m_s@3.6+m_s@4.0 |
| 3.8 | 0.09970 | [0.929976, 0.970088] | 0.7007 | 0.7189 | C / C | 0.960878 | 0.1174 | 0.954160 | 2.0062 | M_real, pair m_s@3.6+m_s@4.0 | M_0, pair m_s@3.6+m_s@4.0 |
| 3.9 | 0.10567 | [0.932978, 0.971944] | 0.6791 | 0.6961 | C / C | 0.963333 | 0.1203 | 0.956435 | 2.0733 | M_real, pair m_s@3.6+m_s@4.0 | M_real, pair m_s@3.6+m_s@4.0 |
| 4.0 | 0.09789 | [0.937760, 0.972797] | 0.6092 | 0.6227 | C / C | 0.964851 | 0.1097 | 0.958546 | 2.5263 | M_real, direct m_s@4.0 | M_real, direct m_s@4.0 |
| 4.1 | 0.09719 | [0.939722, 0.974349] | 0.6009 | 0.6142 | C / C | 0.966584 | 0.1055 | 0.960509 | 2.6504 | M_real, pair m_s@4.0+m_s@4.5 | M_real, pair m_s@4.0+m_s@4.5 |
| 4.2 | 0.08361 | [0.943315, 0.974993] | 0.5487 | 0.5597 | C / C | 0.967576 | 0.0908 | 0.962336 | 3.2230 | M_real, pair m_s@4.0+m_s@4.5 | M_real, pair m_s@4.0+m_s@4.5 |
| 4.3 | 0.06394 | [0.947645, 0.975133] | 0.4753 | 0.4835 | C / C | 0.967898 | 0.0667 | 0.964041 | 4.4176 | M_real, pair m_s@4.0+m_s@4.5 | M_real, pair m_s@4.0+m_s@4.5 |
| 4.4 | 0.07877 | [0.948561, 0.976980] | 0.4905 | 0.4994 | C / C | 0.970362 | 0.0817 | 0.965633 | 3.7853 | M_real, pair m_s@4.0+m_s@4.5 | M_real, pair m_s@4.0+m_s@4.5 |
| 4.5 | 0.07704 | [0.951415, 0.977771] | 0.4542 | 0.4617 | C / C | 0.971647 | 0.0780 | 0.967122 | 4.0855 | M_real, direct m_s@4.5 | M_0, direct m_s@4.5 |
| 4.6 | 0.07664 | [0.953258, 0.978879] | 0.4409 | 0.4480 | C / C | 0.972908 | 0.0756 | 0.968517 | 4.2585 | M_real, pair m_s@4.5+m_s@5.0 | M_0, pair m_s@4.5+m_s@5.0 |
| 4.7 | 0.07207 | [0.955553, 0.979642] | 0.4140 | 0.4202 | C / C | 0.973890 | 0.0699 | 0.969826 | 4.7261 | M_real, pair m_s@4.5+m_s@5.0 | M_0, pair m_s@4.5+m_s@5.0 |
| 4.8 | 0.06528 | [0.958037, 0.980171] | 0.3799 | 0.3851 | C / C | 0.974727 | 0.0631 | 0.971055 | 5.4850 | M_real, pair m_s@4.5+m_s@5.0 | M_0, pair m_s@4.5+m_s@5.0 |
| 4.9 | 0.06280 | [0.960055, 0.980782] | 0.3554 | 0.3599 | C / C | 0.975668 | 0.0593 | 0.972211 | 6.0326 | M_real, pair m_s@4.5+m_s@5.0 | M_0, pair m_s@4.0+m_s@5.0 |
| 5.0 | 0.05733 | [0.962344, 0.981213] | 0.3231 | 0.3268 | C / C | 0.976306 | 0.0515 | 0.973299 | 7.0112 | M_real, direct m_s@5.0 | M_0, direct m_s@5.0 |
| 5.1 | 0.07370 | [0.962036, 0.983018] | 0.3589 | 0.3635 | C / C | 0.978143 | 0.0654 | 0.974325 | 5.6652 | M_real, pair m_s@5.0+m_s@5.5 | M_0, pair m_s@5.0+m_s@5.5 |
| 5.2 | 0.06278 | [0.964369, 0.983240] | 0.3225 | 0.3262 | C / C | 0.978511 | 0.0550 | 0.975293 | 6.9234 | M_real, pair m_s@5.0+m_s@5.5 | M_0, pair m_s@5.0+m_s@5.5 |
| 5.3 | 0.05204 | [0.966606, 0.983379] | 0.2864 | 0.2892 | C / C | 0.978849 | 0.0451 | 0.976207 | 8.7180 | M_real, pair m_s@5.0+m_s@5.5 | M_0, pair m_s@5.0+m_s@5.5 |
| 5.4 | 0.11069 | [0.963067, 0.986753] | 0.4041 | 0.4099 | C / C | 0.981797 | 0.0806 | 0.977072 | 4.2936 | M_real, pair m_s@5.0+m_s@5.5 | M_0, pair m_s@4.0+m_s@5.5 |
| 5.5 | 0.05354 | [0.969009, 0.984549] | 0.2649 | 0.2673 | C / C | 0.980507 | 0.0446 | 0.977891 | 9.2760 | M_real, direct m_s@5.5 | M_0, direct m_s@5.5 |
| 5.6 | 0.04681 | [0.970636, 0.984934] | 0.2435 | 0.2455 | C / C | 0.980871 | 0.0376 | 0.978667 | 11.1202 | M_real, pair m_s@5.5+m_s@6.0 | M_0, pair m_s@5.5+m_s@6.0 |
| 5.7 | 0.11324 | [0.966683, 0.988625] | 0.3734 | 0.3783 | C / C | 0.983706 | 0.0733 | 0.979403 | 4.8248 | M_real, pair m_s@5.5+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.8 | 0.04957 | [0.972353, 0.986205] | 0.2356 | 0.2375 | C / C | 0.982412 | 0.0394 | 0.980101 | 11.5456 | M_real, pair m_s@5.5+m_s@6.0 | M_0, pair m_s@5.5+m_s@6.0 |
| 5.9 | 0.10585 | [0.969542, 0.989110] | 0.3326 | 0.3364 | C / C | 0.984686 | 0.0667 | 0.980765 | 5.6778 | M_real, pair m_s@5.5+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 6.0 | 0.05002 | [0.974215, 0.987043] | 0.2179 | 0.2195 | C / C | 0.983597 | 0.0374 | 0.981396 | 12.5835 | M_real, direct m_s@6.0 | M_0, direct m_s@6.0 |

**n = 57, Czz_bar.** Columns: interval I (ends rounded outward); width over tau and over tau_rf (rounded up); C = CERTIFIED (exact) with tau / with tau_rf; real label; its miss over tau (seen for m_s, F7; new for Czz_bar); truth O_GS; margin = largest energy error at which the row stays certified, over eps_real (rounded down; above 1 for a certified row); what decides each end.

| Jz | eps_real | I | width/tau | width/tau_rf | C tau / tau_rf | real label | miss/tau | truth | margin | lower end | upper end |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.8 (outside the declared range) | 0.21303 | [-0.948131, -0.710506] | 4.3438 | 5.5741 | no / no | -0.927217 | 0.2830 | -0.911739 | - | M_real, other coupling Czz_bar@4.5 | M_real, other coupling Czz_bar@3.4 |
| 2.9 (outside the declared range) | 0.19801 | [-0.950795, -0.829034] | 2.2126 | 2.4479 | no / no | -0.931402 | 0.2583 | -0.917190 | - | M_real, other coupling Czz_bar@4.5 | M_real, other coupling Czz_bar@3.4 |
| 3.0 (outside the declared range) | 0.16016 | [-0.951491, -0.870619] | 1.4617 | 1.5482 | no / no | -0.933236 | 0.2001 | -0.922169 | - | M_real, other coupling H@4.0 | M_real, other coupling Czz_bar@3.4 |
| 3.1 (outside the declared range) | 0.15442 | [-0.954016, -0.886456] | 1.2151 | 1.2703 | no / no | -0.937122 | 0.1870 | -0.926726 | - | M_real, other coupling H@4.0 | M_real, other coupling Czz_bar@3.4 |
| 3.2 (outside the declared range) | 0.14441 | [-0.956311, -0.896981] | 1.0623 | 1.1024 | no / no | -0.940716 | 0.1757 | -0.930906 | - | M_real, other coupling H@4.0 | M_real, other coupling Czz_bar@3.4 |
| 3.3 (outside the declared range) | 0.15391 | [-0.959659, -0.902378] | 1.0214 | 1.0580 | no / no | -0.945226 | 0.1869 | -0.934748 | - | M_real, other coupling Czz_bar@5.0 | M_real, other coupling Czz_bar@3.4 |
| 3.4 | 0.14079 | [-0.961155, -0.908784] | 0.9303 | 0.9605 | C / C | -0.947332 | 0.1607 | -0.938286 | 1.1794 | M_real, direct Czz_bar@3.4 | M_real, direct Czz_bar@3.4 |
| 3.5 | 0.12586 | [-0.962380, -0.914814] | 0.8420 | 0.8666 | C / C | -0.949915 | 0.1481 | -0.941551 | 1.4586 | M_real, other coupling Czz_bar@3.4 | M_real, other coupling Czz_bar@3.6 |
| 3.6 | 0.12099 | [-0.964259, -0.919697] | 0.7863 | 0.8076 | C / C | -0.952239 | 0.1354 | -0.944569 | 1.6438 | M_real, direct Czz_bar@3.6 | M_real, direct Czz_bar@3.6 |
| 3.7 | 0.14681 | [-0.967897, -0.921210] | 0.8214 | 0.8447 | C / C | -0.956504 | 0.1608 | -0.947365 | 1.5155 | M_real, other coupling Czz_bar@5.5 | M_real, other coupling Czz_bar@4.0 |
| 3.8 | 0.09970 | [-0.966701, -0.928556] | 0.6693 | 0.6847 | C / C | -0.956125 | 0.1082 | -0.949958 | 2.4387 | M_real, other coupling Czz_bar@3.6 | M_real, other coupling Czz_bar@3.6 |
| 3.9 | 0.10567 | [-0.969005, -0.931129] | 0.6629 | 0.6780 | C / C | -0.958709 | 0.1110 | -0.952368 | 2.5201 | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 4.0 | 0.09789 | [-0.969980, -0.935574] | 0.6007 | 0.6130 | C / C | -0.960486 | 0.1026 | -0.954610 | 2.9588 | M_real, direct Czz_bar@4.0 | M_real, other coupling Czz_bar@6.0 |
| 4.1 | 0.09719 | [-0.971415, -0.938598] | 0.5717 | 0.5828 | C / C | -0.962405 | 0.0994 | -0.956701 | 3.2191 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@6.0 |
| 4.2 | 0.08361 | [-0.971993, -0.942131] | 0.5192 | 0.5283 | C / C | -0.963608 | 0.0862 | -0.958653 | 4.0231 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@6.0 |
| 4.3 | 0.06394 | [-0.972002, -0.946117] | 0.4492 | 0.4560 | C / C | -0.963937 | 0.0601 | -0.960477 | 5.6440 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.5 |
| 4.4 | 0.07877 | [-0.974401, -0.947170] | 0.4717 | 0.4792 | C / C | -0.966669 | 0.0777 | -0.962186 | 4.9246 | M_real, other coupling Czz_bar@4.5 | M_real, other coupling Czz_bar@4.5 |
| 4.5 | 0.07704 | [-0.975349, -0.949591] | 0.4455 | 0.4521 | C / C | -0.968053 | 0.0738 | -0.963787 | 5.3985 | M_real, direct Czz_bar@4.5 | M_real, direct Czz_bar@4.5 |
| 4.6 | 0.07664 | [-0.976412, -0.951633] | 0.4279 | 0.4340 | C / C | -0.969482 | 0.0724 | -0.965290 | 5.7680 | M_real, other coupling Czz_bar@4.5 | M_real, other coupling H@4.0 |
| 4.7 | 0.07207 | [-0.977254, -0.954111] | 0.3990 | 0.4043 | C / C | -0.970532 | 0.0661 | -0.966702 | 6.4914 | M_real, other coupling Czz_bar@4.5 | M_real, other coupling H@4.0 |
| 4.8 | 0.06528 | [-0.977865, -0.956302] | 0.3713 | 0.3758 | C / C | -0.971487 | 0.0595 | -0.968031 | 7.5380 | M_real, other coupling H@6.0 | M_real, other coupling H@4.0 |
| 4.9 | 0.06280 | [-0.978531, -0.958080] | 0.3517 | 0.3558 | C / C | -0.972579 | 0.0567 | -0.969283 | 8.2078 | M_real, other coupling H@6.0 | M_real, other coupling Czz_bar@5.0 |
| 5.0 | 0.05733 | [-0.979060, -0.960086] | 0.3259 | 0.3294 | C / C | -0.973364 | 0.0499 | -0.970463 | 9.7620 | M_real, other coupling H@6.0 | M_real, direct Czz_bar@5.0 |
| 5.1 | 0.07370 | [-0.980988, -0.960194] | 0.3567 | 0.3610 | C / C | -0.975297 | 0.0639 | -0.971578 | 8.1988 | M_real, other coupling Czz_bar@5.0 | M_real, other coupling Czz_bar@5.0 |
| 5.2 | 0.06278 | [-0.981225, -0.962580] | 0.3195 | 0.3229 | C / C | -0.975747 | 0.0534 | -0.972631 | 10.3331 | M_real, other coupling Czz_bar@5.0 | M_real, other coupling Czz_bar@3.4 |
| 5.3 | 0.05204 | [-0.981393, -0.964737] | 0.2851 | 0.2878 | C / C | -0.976217 | 0.0444 | -0.973627 | 13.3188 | M_real, other coupling Czz_bar@5.0 | M_real, other coupling Czz_bar@3.6 |
| 5.4 | 0.11069 | [-0.984789, -0.961830] | 0.3927 | 0.3979 | C / C | -0.979449 | 0.0835 | -0.974570 | 6.6662 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@3.4 |
| 5.5 | 0.05354 | [-0.982743, -0.966857] | 0.2715 | 0.2739 | C / C | -0.978032 | 0.0439 | -0.975464 | 14.5928 | M_real, direct Czz_bar@5.5 | M_real, direct Czz_bar@5.5 |
| 5.6 | 0.04681 | [-0.982984, -0.968292] | 0.2508 | 0.2529 | C / C | -0.978499 | 0.0374 | -0.976312 | 17.6250 | M_real, other coupling Czz_bar@5.5 | M_real, other coupling Czz_bar@5.5 |
| 5.7 | 0.11324 | [-0.986536, -0.965195] | 0.3640 | 0.3685 | C / C | -0.981609 | 0.0767 | -0.977118 | 7.6694 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@3.6 |
| 5.8 | 0.04957 | [-0.984534, -0.970267] | 0.2432 | 0.2451 | C / C | -0.980178 | 0.0392 | -0.977883 | 18.3750 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.9 | 0.10585 | [-0.987417, -0.967573] | 0.3380 | 0.3419 | C / C | -0.982697 | 0.0696 | -0.978610 | 9.0069 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@5.5 |
| 6.0 | 0.05002 | [-0.985438, -0.972027] | 0.2283 | 0.2300 | C / C | -0.981515 | 0.0377 | -0.979303 | 19.8811 | M_real, direct Czz_bar@6.0 | M_real, direct Czz_bar@6.0 |

**n = 115, m_s.** Columns: interval I (ends rounded outward); width over tau and over tau_rf (rounded up); C = CERTIFIED (exact) with tau / with tau_rf; real label; its miss over tau (seen for m_s, F7; new for Czz_bar); truth O_GS; margin = largest energy error at which the row stays certified, over eps_real (rounded down; above 1 for a certified row); what decides each end.

| Jz | eps_real | I | width/tau | width/tau_rf | C tau / tau_rf | real label | miss/tau | truth | margin | lower end | upper end |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.0 | 0.14355 | [0.943030, 0.972710] | 0.5148 | 0.5246 | C / C | 0.964699 | 0.0639 | 0.961015 | 3.2781 | M_real, direct m_s@4.0 | M_real, direct m_s@4.0 |
| 4.1 | 0.14983 | [0.942206, 0.975109] | 0.5696 | 0.5820 | C / C | 0.966516 | 0.0634 | 0.962858 | 2.9537 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.2 | 0.15145 | [0.942042, 0.977161] | 0.6069 | 0.6214 | C / C | 0.968222 | 0.0631 | 0.964574 | 2.7760 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.3 | 0.14343 | [0.942789, 0.978719] | 0.6198 | 0.6352 | C / C | 0.969488 | 0.0572 | 0.966174 | 2.8176 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.4 | 0.11555 | [0.944994, 0.979465] | 0.5938 | 0.6080 | C / C | 0.970357 | 0.0463 | 0.967669 | 3.3998 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.5 | 0.10477 | [0.946461, 0.980595] | 0.5871 | 0.6011 | C / C | 0.971458 | 0.0412 | 0.969068 | 3.6825 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.6 | 0.11179 | [0.947180, 0.982142] | 0.6005 | 0.6152 | C / C | 0.972787 | 0.0414 | 0.970379 | 3.4372 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.7 | 0.10593 | [0.948929, 0.983130] | 0.5867 | 0.6007 | C / C | 0.973896 | 0.0393 | 0.971608 | 3.6494 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.8 | 0.16312 | [0.947208, 0.986018] | 0.6650 | 0.6829 | C / C | 0.976325 | 0.0611 | 0.972763 | 2.4174 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 4.9 | 0.08523 | [0.953469, 0.984410] | 0.5296 | 0.5409 | C / C | 0.975655 | 0.0310 | 0.973849 | 4.7476 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 5.0 | 0.09854 | [0.954550, 0.985629] | 0.5314 | 0.5427 | C / C | 0.976834 | 0.0336 | 0.974872 | 4.2556 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 5.1 | 0.07001 | [0.958004, 0.985374] | 0.4675 | 0.4762 | C / C | 0.977278 | 0.0247 | 0.975836 | 6.2362 | M_real, pair m_s@4.0+m_s@6.0 | M_real, pair m_s@4.0+m_s@6.0 |
| 5.2 | 0.09681 | [0.958550, 0.986807] | 0.4822 | 0.4914 | C / C | 0.978580 | 0.0313 | 0.976746 | 4.7249 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.3 | 0.06448 | [0.962238, 0.986212] | 0.4087 | 0.4153 | C / C | 0.978880 | 0.0218 | 0.977605 | 7.4514 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.4 | 0.07543 | [0.963737, 0.986927] | 0.3951 | 0.4011 | C / C | 0.979837 | 0.0242 | 0.978419 | 6.9976 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.5 | 0.05881 | [0.966629, 0.986647] | 0.3408 | 0.3452 | C / C | 0.980307 | 0.0191 | 0.979188 | 9.9046 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.6 | 0.05406 | [0.968951, 0.986664] | 0.3013 | 0.3047 | C / C | 0.980934 | 0.0173 | 0.979918 | 11.8414 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.7 | 0.05998 | [0.970784, 0.986946] | 0.2747 | 0.2775 | C / C | 0.981675 | 0.0181 | 0.980610 | 11.6782 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.8 | 0.09050 | [0.971533, 0.987955] | 0.2790 | 0.2818 | C / C | 0.982822 | 0.0265 | 0.981267 | 8.4361 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 5.9 | 0.04708 | [0.975587, 0.986453] | 0.1845 | 0.1857 | C / C | 0.982732 | 0.0143 | 0.981891 | 17.5884 | M_real, pair m_s@4.0+m_s@6.0 | M_0, pair m_s@4.0+m_s@6.0 |
| 6.0 | 0.04582 | [0.977741, 0.986264] | 0.1446 | 0.1453 | C / C | 0.983287 | 0.0137 | 0.982484 | 19.5340 | M_real, direct m_s@6.0 | M_0, direct m_s@6.0 |

**n = 115, Czz_bar.** Columns: interval I (ends rounded outward); width over tau and over tau_rf (rounded up); C = CERTIFIED (exact) with tau / with tau_rf; real label; its miss over tau (seen for m_s, F7; new for Czz_bar); truth O_GS; margin = largest energy error at which the row stays certified, over eps_real (rounded down; above 1 for a certified row); what decides each end.

| Jz | eps_real | I | width/tau | width/tau_rf | C tau / tau_rf | real label | miss/tau | truth | margin | lower end | upper end |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.4 (outside the declared range) | 0.22374 | [-0.962883, -0.458158] | 8.9446 | 18.3607 | no / no | -0.945910 | 0.0964 | -0.940474 | - | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 3.5 (outside the declared range) | 0.22357 | [-0.964325, -0.873760] | 1.5996 | 1.7275 | no / no | -0.948992 | 0.0948 | -0.943630 | - | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 3.6 (outside the declared range; within tau, not counted) | 0.19476 | [-0.965146, -0.910762] | 0.9576 | 0.9952 | no / no | -0.951076 | 0.0798 | -0.946546 | - | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 3.7 (outside the declared range; within tau, not counted) | 0.19838 | [-0.966648, -0.922334] | 0.7781 | 0.8008 | no / no | -0.953821 | 0.0804 | -0.949246 | - | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 3.8 (outside the declared range; within tau, not counted) | 0.17275 | [-0.967418, -0.930992] | 0.6379 | 0.6521 | no / no | -0.955573 | 0.0670 | -0.951750 | - | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 3.9 (outside the declared range; within tau, not counted) | 0.16633 | [-0.968676, -0.935672] | 0.5766 | 0.5879 | no / no | -0.957733 | 0.0639 | -0.954077 | - | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 4.0 | 0.14355 | [-0.969402, -0.940003] | 0.5124 | 0.5213 | C / C | -0.959275 | 0.0529 | -0.956242 | 3.6089 | M_real, direct Czz_bar@4.0 | M_real, direct Czz_bar@4.0 |
| 4.1 | 0.14983 | [-0.971196, -0.942400] | 0.5009 | 0.5093 | C / C | -0.961399 | 0.0546 | -0.958260 | 3.9096 | M_real, other coupling Czz_bar@4.0 | M_real, other coupling Czz_bar@4.0 |
| 4.2 | 0.15145 | [-0.972838, -0.944744] | 0.4877 | 0.4956 | C / C | -0.963290 | 0.0547 | -0.960143 | 4.3635 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 4.3 | 0.14343 | [-0.973695, -0.947106] | 0.4607 | 0.4679 | C / C | -0.964819 | 0.0506 | -0.961904 | 5.0988 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 4.4 | 0.11555 | [-0.973933, -0.949790] | 0.4176 | 0.4237 | C / C | -0.965805 | 0.0390 | -0.963552 | 6.8907 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 4.5 | 0.10477 | [-0.974686, -0.951561] | 0.3994 | 0.4051 | C / C | -0.967096 | 0.0346 | -0.965097 | 8.1574 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 4.6 | 0.11179 | [-0.976107, -0.952682] | 0.4040 | 0.4098 | C / C | -0.968658 | 0.0364 | -0.966547 | 8.1220 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 4.7 | 0.10593 | [-0.977176, -0.954047] | 0.3983 | 0.4041 | C / C | -0.969880 | 0.0340 | -0.967909 | 9.0092 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 4.8 | 0.16312 | [-0.980713, -0.953859] | 0.4618 | 0.4693 | C / C | -0.972618 | 0.0590 | -0.969191 | 6.1001 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 4.9 | 0.08523 | [-0.979265, -0.956667] | 0.3882 | 0.3937 | C / C | -0.971921 | 0.0262 | -0.970399 | 12.0456 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.0 | 0.09854 | [-0.980769, -0.957361] | 0.4016 | 0.4075 | C / C | -0.973290 | 0.0301 | -0.971537 | 10.6766 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.1 | 0.07001 | [-0.980772, -0.961033] | 0.3383 | 0.3424 | C / C | -0.973800 | 0.0204 | -0.972612 | 15.2748 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.2 | 0.09681 | [-0.981729, -0.962274] | 0.3331 | 0.3370 | C / C | -0.975309 | 0.0288 | -0.973627 | 11.2309 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.3 | 0.06448 | [-0.981587, -0.967214] | 0.2458 | 0.2477 | C / C | -0.975646 | 0.0182 | -0.974588 | 18.5803 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.4 | 0.07543 | [-0.982270, -0.968077] | 0.2425 | 0.2444 | C / C | -0.976743 | 0.0213 | -0.975497 | 17.3981 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.5 | 0.05881 | [-0.982365, -0.970104] | 0.2093 | 0.2107 | C / C | -0.977295 | 0.0160 | -0.976359 | 24.3094 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.6 | 0.05406 | [-0.982696, -0.971216] | 0.1958 | 0.1970 | C / C | -0.978019 | 0.0144 | -0.977177 | 28.6702 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.7 | 0.05998 | [-0.983303, -0.971772] | 0.1965 | 0.1978 | C / C | -0.978879 | 0.0158 | -0.977953 | 27.8923 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.8 | 0.09050 | [-0.984679, -0.971499] | 0.2245 | 0.2262 | C / C | -0.980160 | 0.0251 | -0.978690 | 19.8773 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@4.0 |
| 5.9 | 0.04708 | [-0.983867, -0.974337] | 0.1622 | 0.1631 | C / C | -0.980093 | 0.0120 | -0.979392 | 40.9306 | M_real, other coupling Czz_bar@6.0 | M_real, other coupling Czz_bar@6.0 |
| 6.0 | 0.04582 | [-0.984319, -0.975229] | 0.1546 | 0.1554 | C / C | -0.980730 | 0.0115 | -0.980059 | 44.8981 | M_real, direct Czz_bar@6.0 | M_real, direct Czz_bar@6.0 |

Flag "within tau outside the declared range" (Sec. 12 line 3: reported, never counted): n = 115, Jz = 3.6, Czz_bar, width 0.9576 tau; n = 115, Jz = 3.7, Czz_bar, width 0.7781 tau; n = 115, Jz = 3.8, Czz_bar, width 0.6379 tau; n = 115, Jz = 3.9, Czz_bar, width 0.5766 tau. No interval is empty; no row is in conflict (CERTIFIED and NOT CERTIFIED at once): none.

## I-3. NOT CERTIFIED from explicit states (all seven labels)

Rule: with q = (M_0 - M_real)/2, r the stored S^z = s - 1 state of a bracketing grid coupling (lower re-evaluated energy), E* = (E_real - q E_r)/(1 - q): NOT CERTIFIED iff (1 - q) w_in(E*) >= tau, w_in the hull width over the stored in-sector states (own chain where one is stored, otherwise the states of the two bracketing grid couplings re-evaluated by the linear rule). **New: every number of this section** (nothing at the window W(E, M) had been computed). Each cell: status of Sec. 2 (N = NOT CERTIFIED (explicit states), C = CERTIFIED (exact), g = GRAY) and (1 - q) w_in(E*)/tau rounded down; `*` = the status uses an energy re-evaluated at another coupling (pool or reference state), which gate G6 (first part) could not check on the laptop.

**n = 57.** NOT CERTIFIED at 264 of the 350 rows (229 of the 315 training rows).

| Jz | q | m_s | Czz_bar | C2_bar | Z_bulk | Z_boundary | Czz_edge | Z_loop |
|---|---|---|---|---|---|---|---|---|
| 1.1 | 0.11710 | N 18.825 | N 8.366 | N 19.094 | N 46.813 | N 40.710 | N 40.346 | N 71.975 |
| 1.2 | 0.09109 | N 16.011 | N 7.904 | N 17.252 | N 42.404 | N 39.449 | N 37.446 | N 60.555 |
| 1.3 | 0.07148 | N 13.555 | N 7.471 | N 15.747 | N 39.096 | N 37.743 | N 35.335 | N 52.117 |
| 1.4 | 0.06262 | N 11.184 | N 6.875 | N 14.101 | N 34.542 | N 36.675 | N 31.130 | N 45.960 |
| 1.5 | 0.05480 | N 8.825* | N 5.932* | N 11.919* | N 28.112* | N 32.195* | N 25.742* | N 39.466* |
| 1.6 | 0.04752 | N 7.399 | N 5.197 | N 10.224 | N 24.507 | N 28.651 | N 22.768 | N 34.180 |
| 1.7 | 0.04249 | N 6.200* | N 4.560* | N 8.819* | N 21.070* | N 24.839* | N 19.774* | N 29.498* |
| 1.8 | 0.03320 | N 5.174 | N 3.957 | N 7.543 | N 18.225 | N 21.514 | N 17.241 | N 25.510 |
| 1.9 | 0.02761 | N 4.612* | N 3.648* | N 6.862* | N 16.511* | N 19.677* | N 15.772* | N 23.110* |
| 2.0 | 0.02709 | N 3.860 | N 3.142 | N 5.854 | N 14.206 | N 16.840 | N 13.648 | N 19.989 |
| 2.1 | 0.01842 | N 3.530* | N 2.922* | N 5.388* | N 13.163* | N 15.640* | N 12.707* | N 18.451* |
| 2.2 | 0.01694 | N 3.048* | N 2.583* | N 4.720* | N 11.154* | N 13.184* | N 10.840* | N 15.668* |
| 2.3 | 0.01357 | N 2.649* | N 2.360* | N 4.264* | N 10.182* | N 11.955* | N 9.903* | N 14.466* |
| 2.4 | 0.01358 | N 2.283* | N 2.067* | N 3.707* | N 9.041* | N 10.662* | N 8.818* | N 12.851* |
| 2.5 | 0.01216 | N 1.898 | N 1.732 | N 3.107 | N 7.609 | N 8.823 | N 7.434 | N 10.964 |
| 2.6 | 0.01106 | N 1.783* | N 1.652* | N 2.938* | N 7.163* | N 8.320* | N 7.014* | N 10.283* |
| 2.7 | 0.01010 | N 1.526* | N 1.449* | N 2.555* | N 5.944* | N 6.800* | N 5.837* | N 8.516* |
| 2.8 | 0.00786 | N 1.429* | N 1.377* | N 2.424* | N 5.784* | N 6.612* | N 5.682* | N 8.375* |
| 2.9 | 0.00757 | N 1.305* | N 1.261* | N 2.218* | N 5.430* | N 6.238* | N 5.343* | N 7.853* |
| 3.0 | 0.00677 | N 1.107 | N 1.075 | N 1.884 | N 4.654 | N 5.272 | N 4.583 | N 6.743 |
| 3.1 | 0.00608 | N 1.028* | N 1.004* | N 1.758* | N 4.312* | N 4.862* | N 4.250* | N 6.247* |
| 3.2 | 0.00553 | g 0.944 | g 0.930 | N 1.622* | N 3.967* | N 4.461* | N 3.915* | N 5.749* |
| 3.3 | 0.00458 | g 0.932 | g 0.923 | N 1.601 | N 3.963 | N 4.507 | N 3.916 | N 5.750 |
| 3.4 | 0.00415 | g 0.844 | C 0.843 | N 1.463* | N 3.593* | N 4.054* | N 3.553* | N 5.217* |
| 3.5 | 0.00359 | C 0.761 | C 0.764 | N 1.326* | N 3.253* | N 3.635* | N 3.219* | N 4.715* |
| 3.6 | 0.00335 | C 0.710 | C 0.718 | N 1.239 | N 3.079 | N 3.448 | N 3.048 | N 4.468 |
| 3.7 | 0.00270 | C 0.756 | C 0.767 | N 1.321* | N 3.253* | N 3.703* | N 3.224* | N 4.684* |
| 3.8 | 0.00276 | C 0.587 | C 0.594 | N 1.024* | N 2.488* | N 2.734* | N 2.465* | N 3.612* |
| 3.9 | 0.00253 | C 0.584 | C 0.593 | N 1.020* | N 2.527* | N 2.814* | N 2.505* | N 3.677* |
| 4.0 | 0.00218 | C 0.539 | C 0.553 | g 0.952 | N 2.364 | N 2.626 | N 2.345 | N 3.436 |
| 4.1 | 0.00200 | C 0.517 | C 0.531 | g 0.911 | N 2.254* | N 2.499* | N 2.237* | N 3.275* |
| 4.2 | 0.00186 | C 0.458 | C 0.471 | g 0.811 | N 1.943* | N 2.124* | N 1.929* | N 2.784* |
| 4.3 | 0.00182 | C 0.382 | C 0.396 | g 0.680 | N 1.662* | N 1.775* | N 1.651* | N 2.377* |
| 4.4 | 0.00146 | C 0.415 | C 0.431 | g 0.738 | N 1.821* | N 2.000* | N 1.809* | N 2.651* |
| 4.5 | 0.00137 | C 0.395 | C 0.412 | g 0.704 | N 1.752 | N 1.927 | N 1.742 | N 2.555 |
| 4.6 | 0.00125 | C 0.381 | C 0.397 | g 0.677 | N 1.683* | N 1.847* | N 1.674* | N 2.450* |
| 4.7 | 0.00113 | C 0.356 | C 0.367 | g 0.626 | N 1.542* | N 1.683* | N 1.533* | N 2.227* |
| 4.8 | 0.00111 | C 0.328 | C 0.339 | g 0.577 | N 1.429* | N 1.549* | N 1.421* | N 2.073* |
| 4.9 | 0.00089 | C 0.312 | C 0.328 | g 0.558 | N 1.388* | N 1.510* | N 1.380* | N 2.016* |
| 5.0 | 0.00092 | C 0.288 | C 0.304 | g 0.517 | N 1.293 | N 1.401 | N 1.286 | N 1.875 |
| 5.1 | 0.00074 | C 0.319 | C 0.337 | g 0.573 | N 1.412* | N 1.561* | N 1.406* | N 2.060* |
| 5.2 | 0.00073 | C 0.284 | C 0.298 | g 0.507 | N 1.241* | N 1.350* | N 1.235* | N 1.813* |
| 5.3 | 0.00067 | C 0.250 | C 0.264 | g 0.448 | N 1.104* | N 1.187* | N 1.099* | N 1.599* |
| 5.4 | 0.00031 | C 0.360 | C 0.382 | g 0.649 | N 1.544* | N 1.755* | N 1.537* | N 2.154* |
| 5.5 | 0.00060 | C 0.240 | C 0.256 | g 0.433 | N 1.079 | N 1.174 | N 1.074 | N 1.574 |
| 5.6 | 0.00055 | C 0.217 | C 0.231 | g 0.391 | g 0.984 | N 1.056* | g 0.980 | N 1.427* |
| 5.7 | 0.00029 | C 0.334 | C 0.353 | g 0.599 | N 1.440* | N 1.612* | N 1.434* | N 1.841* |
| 5.8 | 0.00049 | C 0.212 | C 0.227 | g 0.384 | g 0.941 | N 1.016* | g 0.937 | N 1.371* |
| 5.9 | 0.00018 | C 0.305 | C 0.325 | g 0.551 | N 1.315* | N 1.463* | N 1.310* | N 1.796* |
| 6.0 | 0.00036 | C 0.203 | C 0.218 | g 0.368 | g 0.914 | g 0.996 | g 0.910 | N 1.342 |

**n = 115.** NOT CERTIFIED at 175 of the 350 rows (140 of the 315 training rows).

| Jz | q | m_s | Czz_bar | C2_bar | Z_bulk | Z_boundary | Czz_edge | Z_loop |
|---|---|---|---|---|---|---|---|---|
| 1.1 | 0.21760 | N 16.305 | N 9.715 | N 20.008 | N 16.711 | N 7.750 | N 9.841 | N 24.604 |
| 1.2 | 0.19114 | N 12.316 | N 8.243 | N 16.775 | N 13.426 | N 6.869 | N 8.371 | N 20.015 |
| 1.3 | 0.15969 | N 11.573 | N 7.397 | N 14.762 | N 11.146 | N 6.230 | N 7.363 | N 17.498 |
| 1.4 | 0.13444 | N 9.827 | N 6.600 | N 12.872 | N 9.259 | N 5.573 | N 6.464 | N 15.017 |
| 1.5 | 0.13104 | N 8.806* | N 6.136* | N 11.816* | N 8.225* | N 5.631* | N 5.979* | N 13.639* |
| 1.6 | 0.10130 | N 6.713 | N 4.971 | N 9.405 | N 6.292 | N 4.642 | N 4.781 | N 10.741 |
| 1.7 | 0.08637 | N 5.606* | N 4.354* | N 8.134* | N 5.318* | N 4.465* | N 4.171* | N 9.228* |
| 1.8 | 0.07157 | N 4.899 | N 3.914 | N 7.196 | N 4.625 | N 3.838 | N 3.721 | N 8.121 |
| 1.9 | 0.06330 | N 4.052* | N 3.377* | N 6.143* | N 3.884* | N 3.625* | N 3.199* | N 6.905* |
| 2.0 | 0.05488 | N 3.455 | N 2.959 | N 5.338 | N 3.331 | N 3.100 | N 2.797 | N 5.987 |
| 2.1 | 0.04504 | N 3.112* | N 2.714* | N 4.862* | N 3.001* | N 2.978* | N 2.560* | N 5.433* |
| 2.2 | 0.04337 | N 2.487* | N 2.239* | N 3.983* | N 2.418* | N 2.476* | N 2.096* | N 4.416* |
| 2.3 | 0.03708 | N 2.176* | N 2.056* | N 3.617* | N 2.179* | N 2.208* | N 1.916* | N 4.012* |
| 2.4 | 0.03132 | N 1.962* | N 1.861* | N 3.255* | N 1.952* | N 2.013* | N 1.733* | N 3.618* |
| 2.5 | 0.02925 | N 1.730 | N 1.653 | N 2.887 | N 1.729 | N 1.849 | N 1.547 | N 3.225 |
| 2.6 | 0.02559 | N 1.531* | N 1.486* | N 2.578* | N 1.530* | N 1.636* | N 1.382* | N 2.868* |
| 2.7 | 0.02299 | N 1.361* | N 1.350* | N 2.325* | N 1.369* | N 1.415* | N 1.248* | N 2.578* |
| 2.8 | 0.01755 | N 1.308* | N 1.323* | N 2.273* | N 1.334* | N 1.361* | N 1.223* | N 2.520* |
| 2.9 | 0.01742 | N 1.102* | N 1.143* | N 1.962* | N 1.153* | N 1.191* | N 1.062* | N 2.189* |
| 3.0 | 0.01585 | N 1.038 | N 1.059 | N 1.810 | N 1.063 | N 1.065 | g 0.983 | N 2.023 |
| 3.1 | 0.01445 | g 0.890 | g 0.903 | N 1.543* | g 0.902 | g 0.994 | g 0.839 | N 1.723* |
| 3.2 | 0.01247 | g 0.880 | g 0.905 | N 1.540* | g 0.899 | g 0.988 | g 0.840 | N 1.722* |
| 3.3 | 0.00996 | g 0.827 | g 0.851 | N 1.444 | g 0.841 | g 0.923 | g 0.789 | N 1.615 |
| 3.4 | 0.01040 | g 0.686 | g 0.713 | N 1.212* | g 0.703 | g 0.801 | g 0.662 | N 1.353* |
| 3.5 | 0.00869 | g 0.660 | g 0.687 | N 1.164* | g 0.675 | g 0.769 | g 0.638 | N 1.303* |
| 3.6 | 0.00851 | g 0.583 | g 0.612 | N 1.036 | g 0.600 | g 0.641 | g 0.568 | N 1.159 |
| 3.7 | 0.00719 | g 0.566 | g 0.594 | N 1.002* | N 3.297* | g 0.657 | N 2.127* | N 1.220* |
| 3.8 | 0.00691 | g 0.503 | g 0.527 | g 0.890 | N 3.184* | g 0.597 | N 2.055* | N 1.188* |
| 3.9 | 0.00625 | g 0.474 | g 0.503 | g 0.849 | N 3.115* | g 0.541 | N 2.011* | N 1.213* |
| 4.0 | 0.00573 | C 0.422 | C 0.449 | g 0.755 | N 2.798 | g 0.457 | N 1.807 | N 1.126 |
| 4.1 | 0.00518 | C 0.414 | C 0.443 | g 0.746 | N 2.734* | g 0.439 | N 1.773* | N 1.163* |
| 4.2 | 0.00475 | C 0.393 | C 0.427 | g 0.721 | N 2.561* | g 0.415 | N 1.662* | N 1.153* |
| 4.3 | 0.00421 | C 0.366 | C 0.398 | g 0.669 | N 2.208* | g 0.390 | N 1.433* | N 1.065* |
| 4.4 | 0.00385 | C 0.321 | C 0.349 | g 0.584 | N 1.621* | g 0.348 | N 1.046* | g 0.869 |
| 4.5 | 0.00393 | C 0.298 | C 0.321 | g 0.537 | g 0.307 | g 0.318 | g 0.297 | g 0.602 |
| 4.6 | 0.00344 | C 0.298 | C 0.321 | g 0.536 | g 0.307 | g 0.347 | g 0.297 | g 0.601 |
| 4.7 | 0.00322 | C 0.278 | C 0.296 | g 0.495 | g 0.283 | g 0.327 | g 0.274 | g 0.555 |
| 4.8 | 0.00245 | C 0.344 | C 0.369 | g 0.616 | g 0.351 | g 0.384 | g 0.341 | g 0.689 |
| 4.9 | 0.00274 | C 0.235 | C 0.255 | g 0.425 | g 0.243 | g 0.257 | g 0.236 | g 0.478 |
| 5.0 | 0.00237 | C 0.247 | C 0.269 | g 0.449 | g 0.256 | g 0.262 | g 0.249 | g 0.503 |
| 5.1 | 0.00238 | C 0.196 | C 0.207 | g 0.347 | g 0.197 | g 0.236 | g 0.192 | g 0.388 |
| 5.2 | 0.00205 | C 0.230 | C 0.245 | g 0.409 | g 0.232 | g 0.265 | g 0.226 | g 0.457 |
| 5.3 | 0.00208 | C 0.178 | C 0.191 | g 0.319 | g 0.182 | g 0.203 | g 0.177 | g 0.358 |
| 5.4 | 0.00189 | C 0.190 | C 0.206 | g 0.342 | g 0.195 | g 0.206 | g 0.190 | g 0.384 |
| 5.5 | 0.00184 | C 0.162 | C 0.178 | g 0.296 | g 0.168 | g 0.170 | g 0.164 | g 0.332 |
| 5.6 | 0.00170 | C 0.147 | C 0.161 | g 0.268 | g 0.152 | g 0.167 | g 0.149 | g 0.301 |
| 5.7 | 0.00155 | C 0.151 | C 0.166 | g 0.275 | g 0.156 | g 0.168 | g 0.153 | g 0.309 |
| 5.8 | 0.00135 | C 0.187 | C 0.205 | g 0.341 | g 0.193 | g 0.200 | g 0.189 | g 0.382 |
| 5.9 | 0.00139 | C 0.130 | C 0.143 | g 0.237 | g 0.135 | g 0.139 | g 0.132 | g 0.267 |
| 6.0 | 0.00134 | C 0.125 | C 0.137 | g 0.228 | g 0.130 | g 0.130 | g 0.127 | g 0.256 |

| n | label | NOT CERTIFIED (explicit) of 45 | at the couplings | GRAY of 45 | CERTIFIED (exact) of 45 |
|---|---|---|---|---|---|
| 57 | m_s | 16 | 1.1-3.1 | 3 | 26 |
| 57 | Czz_bar | 16 | 1.1-3.1 | 2 | 27 |
| 57 | C2_bar | 24 | 1.1-3.9 | 21 | 0 |
| 57 | Z_bulk | 42 | 1.1-5.5, 5.7, 5.9 | 3 | 0 |
| 57 | Z_boundary | 44 | 1.1-5.9 | 1 | 0 |
| 57 | Czz_edge | 42 | 1.1-5.5, 5.7, 5.9 | 3 | 0 |
| 57 | Z_loop | 45 | 1.1-6.0 | 0 | 0 |
| 115 | m_s | 15 | 1.1-3.0 | 9 | 21 |
| 115 | Czz_bar | 15 | 1.1-3.0 | 9 | 21 |
| 115 | C2_bar | 22 | 1.1-3.7 | 23 | 0 |
| 115 | Z_bulk | 23 | 1.1-3.0, 3.7-4.4 | 22 | 0 |
| 115 | Z_boundary | 15 | 1.1-3.0 | 30 | 0 |
| 115 | Czz_edge | 22 | 1.1-2.9, 3.7-4.4 | 23 | 0 |
| 115 | Z_loop | 28 | 1.1-4.3 | 17 | 0 |

The couplings listed include the five outside the training set (1.1-1.5). At n = 115 the stored map has no chain of Z_boundary, Czz_edge or Z_loop, and of Z_bulk only at Jz = 4.0; their pools are the states of the other labels' chains, which is why those columns turn GRAY early (and why Z_bulk and Czz_edge are NOT CERTIFIED again between 3.7 and 4.4, where the richer pool of Jz = 4.0 is in the bracket). A GRAY cell there says that the stored states do not decide, not that the label is close to certified.

## I-4. Like-for-like statuses under the paper's sector hypothesis, and J*_s

Rule: at a coupling with a stored chain of the label, CERTIFIED_s iff w_out(E_real) <= tau, NOT CERTIFIED_s iff w_in(E_real) >= tau, GRAY_s otherwise; elsewhere the stored thresholds interpolated log-linearly in Jz ("interpolated, not a bound", suffix `i`). A CERTIFIED_s status is a statement about in-sector states and is never a certificate of a real label. **Seen before the hash (F6):** the m_s statuses at the couplings of the stored map, with their energy-over-threshold ratios. **New:** the other six labels, and m_s at the interpolated couplings. Each cell: status (C, N, g; `-` = not available, no chain of that label at that size) and the margin: for C, f_out = eps_tau_out/eps_real (rounded down, above 1); for N, f_in = eps_tau_in/eps_real (rounded up, below 1).

**n = 57.**

| Jz | eps_real | m_s | Czz_bar | C2_bar | Z_bulk | Z_boundary | Czz_edge | Z_loop |
|---|---|---|---|---|---|---|---|---|
| 1.1 | 1.21983 | N 0.003 | N 0.008 | N 0.002 | N 0.001 | N 0.001 | N 0.001 | N 0.001 |
| 1.2 | 1.12626 | N 0.004 | N 0.010 | N 0.002 | N 0.001 | N 0.001 | N 0.001 | N 0.001 |
| 1.3 | 1.02695 | N 0.006 | N 0.013 | N 0.003 | N 0.001 | N 0.001 | N 0.001 | N 0.001 |
| 1.4 | 0.87918 | N 0.009 | N 0.018 | N 0.005 | N 0.001 | N 0.001 | N 0.001 | N 0.001 |
| 1.5 | 0.71891 | N 0.014i | N 0.026i | N 0.007i | N 0.001i | N 0.001i | N 0.002i | N 0.001i |
| 1.6 | 0.64722 | N 0.020 | N 0.034 | N 0.009 | N 0.002 | N 0.002 | N 0.002 | N 0.001 |
| 1.7 | 0.58399 | N 0.028i | N 0.044i | N 0.012i | N 0.002i | N 0.002i | N 0.003i | N 0.001i |
| 1.8 | 0.50578 | N 0.040 | N 0.059 | N 0.016 | N 0.003 | N 0.003 | N 0.003 | N 0.002 |
| 1.9 | 0.49533 | N 0.049i | N 0.069i | N 0.020i | N 0.004i | N 0.003i | N 0.004i | N 0.002i |
| 2.0 | 0.42789 | N 0.069 | N 0.093 | N 0.027 | N 0.005 | N 0.004 | N 0.005 | N 0.002 |
| 2.1 | 0.42382 | N 0.082i | N 0.107i | N 0.032i | N 0.005i | N 0.005i | N 0.006i | N 0.003i |
| 2.2 | 0.38958 | N 0.105i | N 0.132i | N 0.040i | N 0.007i | N 0.006i | N 0.007i | N 0.003i |
| 2.3 | 0.35827 | N 0.134i | N 0.163i | N 0.050i | N 0.008i | N 0.007i | N 0.009i | N 0.004i |
| 2.4 | 0.30580 | N 0.184i | N 0.217i | N 0.067i | N 0.011i | N 0.009i | N 0.011i | N 0.006i |
| 2.5 | 0.24403 | N 0.270 | N 0.309 | N 0.096 | N 0.015 | N 0.013 | N 0.016 | N 0.008 |
| 2.6 | 0.24777 | N 0.301i | N 0.339i | N 0.107i | N 0.017i | N 0.015i | N 0.018i | N 0.009i |
| 2.7 | 0.21315 | N 0.396i | N 0.438i | N 0.139i | N 0.022i | N 0.019i | N 0.023i | N 0.011i |
| 2.8 | 0.21303 | N 0.448i | N 0.488i | N 0.156i | N 0.025i | N 0.021i | N 0.026i | N 0.012i |
| 2.9 | 0.19801 | N 0.546i | N 0.585i | N 0.189i | N 0.030i | N 0.025i | N 0.031i | N 0.015i |
| 3.0 | 0.16016 | N 0.764 | N 0.805 | N 0.262 | N 0.041 | N 0.035 | N 0.043 | N 0.020 |
| 3.1 | 0.15442 | N 0.881i | N 0.919i | N 0.300i | N 0.047i | N 0.040i | N 0.049i | N 0.023i |
| 3.2 | 0.14441 | C 1.047 | C 1.080 | N 0.354i | N 0.056i | N 0.048i | N 0.057i | N 0.027i |
| 3.3 | 0.15391 | C 1.086 | C 1.110 | N 0.368 | N 0.058 | N 0.050 | N 0.059 | N 0.028 |
| 3.4 | 0.14079 | C 1.307 | C 1.327 | N 0.440i | N 0.069i | N 0.059i | N 0.071i | N 0.034i |
| 3.5 | 0.12586 | C 1.602i | C 1.616i | N 0.539i | N 0.084i | N 0.073i | N 0.086i | N 0.041i |
| 3.6 | 0.12099 | C 1.826 | C 1.831 | N 0.614 | N 0.096 | N 0.083 | N 0.098 | N 0.047 |
| 3.7 | 0.14681 | C 1.626i | C 1.633i | N 0.549i | N 0.086i | N 0.074i | N 0.088i | N 0.042i |
| 3.8 | 0.09970 | C 2.589i | C 2.601i | N 0.877i | N 0.137i | N 0.118i | N 0.140i | N 0.067i |
| 3.9 | 0.10567 | C 2.640i | C 2.655i | N 0.898i | N 0.140i | N 0.121i | N 0.143i | N 0.068i |
| 4.0 | 0.09789 | C 3.081 | C 3.101 | C 1.050 | N 0.164 | N 0.142 | N 0.167 | N 0.080 |
| 4.1 | 0.09719 | C 3.304i | C 3.352i | C 1.138i | N 0.178i | N 0.153i | N 0.180i | N 0.087i |
| 4.2 | 0.08361 | C 4.088i | C 4.182i | C 1.423i | N 0.222i | N 0.191i | N 0.225i | N 0.108i |
| 4.3 | 0.06394 | C 5.689i | C 5.868i | C 2.002i | N 0.311i | N 0.269i | N 0.316i | N 0.152i |
| 4.4 | 0.07877 | C 4.915i | C 5.112i | C 1.747i | N 0.272i | N 0.234i | N 0.275i | N 0.133i |
| 4.5 | 0.07704 | C 5.349 | C 5.610 | C 1.922 | N 0.298 | N 0.257 | N 0.302 | N 0.146 |
| 4.6 | 0.07664 | C 5.600i | C 6.007i | C 2.061i | N 0.319i | N 0.275i | N 0.323i | N 0.156i |
| 4.7 | 0.07207 | C 6.202i | C 6.804i | C 2.339i | N 0.361i | N 0.312i | N 0.365i | N 0.177i |
| 4.8 | 0.06528 | C 7.130i | C 8.002i | C 2.755i | N 0.424i | N 0.367i | N 0.429i | N 0.209i |
| 4.9 | 0.06280 | C 7.720i | C 8.861i | C 3.055i | N 0.470i | N 0.406i | N 0.474i | N 0.231i |
| 5.0 | 0.05733 | C 8.807 | C 10.340 | C 3.571 | N 0.547 | N 0.473 | N 0.552 | N 0.270 |
| 5.1 | 0.07370 | C 7.132i | C 8.517i | C 2.945i | N 0.455i | N 0.394i | N 0.459i | N 0.223i |
| 5.2 | 0.06278 | C 8.719i | C 10.589i | C 3.665i | N 0.570i | N 0.494i | N 0.575i | N 0.277i |
| 5.3 | 0.05204 | C 10.951i | C 13.527i | C 4.687i | N 0.733i | N 0.636i | N 0.740i | N 0.354i |
| 5.4 | 0.11069 | C 5.361i | C 6.735i | C 2.336i | N 0.368i | N 0.320i | N 0.372i | N 0.177i |
| 5.5 | 0.05354 | C 11.541 | C 14.746 | C 5.120 | N 0.812 | N 0.706 | N 0.820 | N 0.386 |
| 5.6 | 0.04681 | C 13.612i | C 17.691i | C 6.176i | N 0.988i | N 0.852i | N 0.998i | N 0.466i |
| 5.7 | 0.11324 | C 5.801i | C 7.668i | C 2.692i | N 0.435i | N 0.371i | N 0.439i | N 0.203i |
| 5.8 | 0.04957 | C 13.667i | C 18.374i | C 6.485i | g 0.965/1.057i | N 0.894i | g 0.972/1.066i | N 0.489i |
| 5.9 | 0.10585 | C 6.599i | C 9.024i | C 3.202i | N 0.527i | N 0.442i | N 0.531i | N 0.242i |
| 6.0 | 0.05002 | C 14.398 | C 20.026 | C 7.146 | C 1.054 | N 0.984 | C 1.062 | N 0.539 |

**n = 115.**

| Jz | eps_real | m_s | Czz_bar | C2_bar | Z_bulk | Z_boundary | Czz_edge | Z_loop |
|---|---|---|---|---|---|---|---|---|
| 1.1 | 2.61379 | N 0.007 | N 0.012 | N 0.006 | - | - | - | - |
| 1.2 | 2.26356 | N 0.009 | N 0.014 | N 0.006 | - | - | - | - |
| 1.3 | 1.97504 | N 0.010 | N 0.017 | N 0.006 | - | - | - | - |
| 1.4 | 1.77302 | N 0.013 | N 0.021 | N 0.007 | - | - | - | - |
| 1.5 | 1.80620 | N 0.015i | N 0.023i | N 0.008i | - | - | - | - |
| 1.6 | 1.34321 | N 0.025 | N 0.036 | N 0.011 | - | - | - | - |
| 1.7 | 1.19558 | N 0.034i | N 0.047i | N 0.014i | - | - | - | - |
| 1.8 | 1.10654 | N 0.045 | N 0.058 | N 0.018 | - | - | - | - |
| 1.9 | 0.95480 | N 0.062i | N 0.078i | N 0.024i | - | - | - | - |
| 2.0 | 0.83858 | N 0.085 | N 0.102 | N 0.032 | - | - | - | - |
| 2.1 | 0.81329 | N 0.102i | N 0.119i | N 0.038i | - | - | - | - |
| 2.2 | 0.65834 | N 0.147i | N 0.167i | N 0.053i | - | - | - | - |
| 2.3 | 0.60555 | N 0.187i | N 0.207i | N 0.067i | - | - | - | - |
| 2.4 | 0.54619 | N 0.242i | N 0.261i | N 0.085i | - | - | - | - |
| 2.5 | 0.48919 | N 0.315 | N 0.331 | N 0.109 | - | - | - | - |
| 2.6 | 0.44571 | N 0.392i | N 0.404i | N 0.134i | - | - | - | - |
| 2.7 | 0.40694 | N 0.486i | N 0.492i | N 0.164i | - | - | - | - |
| 2.8 | 0.42808 | N 0.523i | N 0.521i | N 0.175i | - | - | - | - |
| 2.9 | 0.35641 | N 0.711i | N 0.697i | N 0.236i | - | - | - | - |
| 3.0 | 0.33808 | N 0.849 | N 0.818 | N 0.279 | - | - | - | - |
| 3.1 | 0.27650 | C 1.128i | C 1.097i | N 0.376i | - | - | - | - |
| 3.2 | 0.29683 | C 1.163i | C 1.123i | N 0.387i | - | - | - | - |
| 3.3 | 0.28519 | C 1.339 | C 1.285 | N 0.445 | - | - | - | - |
| 3.4 | 0.22374 | C 1.867i | C 1.785i | N 0.621i | - | - | - | - |
| 3.5 | 0.22357 | C 2.044i | C 1.948i | N 0.680i | - | - | - | - |
| 3.6 | 0.19476 | C 2.567 | C 2.439 | N 0.854 | - | - | - | - |
| 3.7 | 0.19838 | C 2.700i | C 2.591i | N 0.910i | - | - | - | - |
| 3.8 | 0.17275 | C 3.322i | C 3.219i | C 1.132i | - | - | - | - |
| 3.9 | 0.16633 | C 3.696i | C 3.617i | C 1.276i | - | - | - | - |
| 4.0 | 0.14355 | C 4.587 | C 4.535 | C 1.604 | N 0.112 | - | - | - |
| 4.1 | 0.14983 | C 4.666i | C 4.662i | C 1.652i | - | - | - | - |
| 4.2 | 0.15145 | C 4.901i | C 4.950i | C 1.757i | - | - | - | - |
| 4.3 | 0.14343 | C 5.493i | C 5.609i | C 1.995i | - | - | - | - |
| 4.4 | 0.11555 | C 7.239i | C 7.471i | C 2.662i | - | - | - | - |
| 4.5 | 0.10477 | C 8.477 | C 8.843 | C 3.157 | - | - | - | - |
| 4.6 | 0.11179 | C 8.314i | C 8.828i | C 3.156i | - | - | - | - |
| 4.7 | 0.10593 | C 9.182i | C 9.924i | C 3.553i | - | - | - | - |
| 4.8 | 0.16312 | C 6.240i | C 6.865i | C 2.461i | - | - | - | - |
| 4.9 | 0.08523 | C 12.500i | C 13.997i | C 5.026i | - | - | - | - |
| 5.0 | 0.09854 | C 11.314 | C 12.896 | C 4.637 | - | - | - | - |
| 5.1 | 0.07001 | C 16.287i | C 19.216i | C 6.918i | - | - | - | - |
| 5.2 | 0.09681 | C 12.046i | C 14.712i | C 5.303i | - | - | - | - |
| 5.3 | 0.06448 | C 18.498i | C 23.386i | C 8.440i | - | - | - | - |
| 5.4 | 0.07543 | C 16.170i | C 21.162i | C 7.647i | - | - | - | - |
| 5.5 | 0.05881 | C 21.212 | C 28.736 | C 10.396 | - | - | - | - |
| 5.6 | 0.05406 | C 23.936i | C 31.703i | C 11.923i | - | - | - | - |
| 5.7 | 0.05998 | C 22.377i | C 28.978i | C 11.330i | - | - | - | - |
| 5.8 | 0.09050 | C 15.384i | C 19.478i | C 7.917i | - | - | - | - |
| 5.9 | 0.04708 | C 30.677i | C 37.976i | C 16.046i | - | - | - | - |
| 6.0 | 0.04582 | C 32.691 | C 39.567 | C 17.381 | - | - | - | - |

| n | label | J*_s | CERTIFIED_s of 45 | NOT CERTIFIED_s | GRAY_s | not available | of which interpolated |
|---|---|---|---|---|---|---|---|
| 57 | m_s | 3.2 | 29 | 16 | 0 | 0 | 31 |
| 57 | Czz_bar | 3.2 | 29 | 16 | 0 | 0 | 31 |
| 57 | C2_bar | 4.0 | 21 | 24 | 0 | 0 | 33 |
| 57 | Z_bulk | 6.0 | 1 | 43 | 1 | 0 | 33 |
| 57 | Z_boundary | - | 0 | 45 | 0 | 0 | 33 |
| 57 | Czz_edge | 6.0 | 1 | 43 | 1 | 0 | 33 |
| 57 | Z_loop | - | 0 | 45 | 0 | 0 | 33 |
| 115 | m_s | 3.1 | 30 | 15 | 0 | 0 | 33 |
| 115 | Czz_bar | 3.1 | 30 | 15 | 0 | 0 | 33 |
| 115 | C2_bar | 3.8 | 23 | 22 | 0 | 0 | 33 |
| 115 | Z_bulk | - | 0 | 1 | 0 | 44 | 44 |
| 115 | Z_boundary | - | 0 | 0 | 0 | 45 | 45 |
| 115 | Czz_edge | - | 0 | 0 | 0 | 45 | 45 |
| 115 | Z_loop | - | 0 | 0 | 0 | 45 | 45 |

J* is the stored definition: the smallest training Jz from which every larger training point is certified (resolution 0.1); a training coupling without a status is not a certified point.

## I-5. J* under each rule and the counts out of 45 (table of Sec. 3 of the declaration)

| n | label | J*_s | cert_s | J*_exact (tau) | cert exact (tau) | J*_exact (tau_rf) | cert exact (tau_rf) | NOT CERTIFIED (explicit) | GRAY (Sec. 2) |
|---|---|---|---|---|---|---|---|---|---|
| 57 | m_s | 3.2 | 29 | 3.5 | 26 | 3.5 | 26 | 16 | 3 |
| 57 | Czz_bar | 3.2 | 29 | 3.4 | 27 | 3.4 | 27 | 16 | 2 |
| 57 | C2_bar | 4.0 | 21 | - | 0 | - | 0 | 24 | 21 |
| 57 | Z_bulk | 6.0 | 1 | - | 0 | - | 0 | 42 | 3 |
| 57 | Z_boundary | - | 0 | - | 0 | - | 0 | 44 | 1 |
| 57 | Czz_edge | 6.0 | 1 | - | 0 | - | 0 | 42 | 3 |
| 57 | Z_loop | - | 0 | - | 0 | - | 0 | 45 | 0 |
| 115 | m_s | 3.1 | 30 | 4.0 | 21 | 4.0 | 21 | 15 | 9 |
| 115 | Czz_bar | 3.1 | 30 | 4.0 | 21 | 4.0 | 21 | 15 | 9 |
| 115 | C2_bar | 3.8 | 23 | - | 0 | - | 0 | 22 | 23 |
| 115 | Z_bulk | - | 0 | - | 0 | - | 0 | 23 | 22 |
| 115 | Z_boundary | - | 0 | - | 0 | - | 0 | 15 | 30 |
| 115 | Czz_edge | - | 0 | - | 0 | - | 0 | 22 | 23 |
| 115 | Z_loop | - | 0 | - | 0 | - | 0 | 28 | 17 |

The number "certified from 3.2, 29 of 45" (n = 57) and "from 3.1, 30 of 45" (n = 115) is the like-for-like number (seen, F6 and F9, at the stored couplings) and, as the declaration says, must not be printed as a property of the real labels.

## I-6. Predicted from the figures versus obtained from the data (the 171 stored rows)

Rule: the figures-based map is **confirmed by the data** iff no row is contradicted (CERTIFIED against NOT CERTIFIED) and, for every label and size with a stored J*, |J*_s - J*_stored| <= 0.1. The 6 rows of n = 19 have no public data; the rule is applied to the 165 rows of n = 57 and n = 115. **Seen before the hash (F6):** the m_s rows (no contradiction; n = 57: 3.2 and 3.3 resolve from GRAY to CERTIFIED_s). **New:** the rows of the other six labels.

**Outcome: CONFIRMED BY THE DATA.** Relations over the 165 rows: confirmed 152, resolved 13, opened 0, contradicted 0, GRAY on both sides 0 (plus 6 rows of n = 19 without real data).

| n | label | stored J* (central) | stored J* (strict) | certified in the stored map | J*_s at E_real | certified_s at E_real | within 0.1 |
|---|---|---|---|---|---|---|---|
| 57 | m_s | 3.2 | 3.4 | 29 | 3.2 | 29 | yes |
| 57 | Czz_bar | 3.2 | 3.4 | 29 | 3.2 | 29 | yes |
| 57 | C2_bar | 4.0 | 4.2 | 21 | 4.0 | 21 | yes |
| 57 | Z_bulk | 6.0 | - | 1 | 6.0 | 1 | yes |
| 57 | Czz_edge | 6.0 | - | 1 | 6.0 | 1 | yes |
| 115 | m_s | 3.1 | 3.3 | 30 | 3.1 | 30 | yes |
| 115 | Czz_bar | 3.1 | 3.3 | 30 | 3.1 | 30 | yes |
| 115 | C2_bar | 3.8 | 3.9 | 23 | 3.8 | 23 | yes |

The 13 resolved rows: n = 57, Jz = 3.2, m_s: GRAY -> CERTIFIED_s; n = 57, Jz = 3.3, m_s: GRAY -> CERTIFIED_s; n = 57, Jz = 3.2, Czz_bar: GRAY -> CERTIFIED_s; n = 57, Jz = 3.3, Czz_bar: GRAY -> CERTIFIED_s; n = 57, Jz = 4.0, C2_bar: GRAY -> CERTIFIED_s; n = 57, Jz = 5.5, Z_bulk: GRAY -> NOT_CERTIFIED_s; n = 57, Jz = 6.0, Z_bulk: GRAY -> CERTIFIED_s; n = 57, Jz = 6.0, Z_boundary: GRAY -> NOT_CERTIFIED_s; n = 57, Jz = 5.5, Czz_edge: GRAY -> NOT_CERTIFIED_s; n = 57, Jz = 6.0, Czz_edge: GRAY -> CERTIFIED_s; n = 115, Jz = 3.0, m_s: GRAY -> NOT_CERTIFIED_s; n = 115, Jz = 3.0, Czz_bar: GRAY -> NOT_CERTIFIED_s; n = 115, Jz = 3.6, C2_bar: GRAY -> NOT_CERTIFIED_s.

**Stored claims re-evaluated on the stored rows** (map/DECLARATION.md Sec. 4), with the like-for-like statuses and with those of Sec. 2:

| claim | like-for-like at E_real | with the statuses of Sec. 2 |
|---|---|---|
| C-A (m_s and Czz_bar certified at Jz >= 4.0, both sizes; 20 rows) | MAP-POSITIVE; rows not certified: none | MAP-POSITIVE; rows not certified: none |
| C-B (every row at Jz <= 1.6 NOT CERTIFIED; 50 rows; no longer conditional on a floor) | HOLDS; exceptions: none | HOLDS; exceptions: none |
| C-C (no local label certified; 65 rows) | DOES NOT HOLD; certified local rows: n = 57, Jz = 6.0, Czz_edge; n = 57, Jz = 6.0, Z_bulk | HOLDS; certified local rows: none; GRAY: n = 57, Jz = 6.0, Czz_edge; n = 57, Jz = 6.0, Z_boundary; n = 57, Jz = 6.0, Z_bulk |

C-C does not hold like-for-like: at the real energy the bulk-site and single-edge labels at n = 57, Jz = 6.0 are CERTIFIED_s (margins f_out 1.054 and 1.062). In the stored map the claim held with these two rows GRAY, and its central reading already passed them (stored J* = 6.0 for both, one certified point each). This is the failure of a stored claim under the real energies and is reported as such; it is not a contradicted row (GRAY became decisive), so it does not enter the rule above.

| n | Jz | label | predicted (figures) | like-for-like at E_real | relation | f_out | f_in | status of Sec. 2 (tau) | (tau_rf) |
|---|---|---|---|---|---|---|---|---|---|
| 19 | 1.6 | m_s | NOT_CERTIFIED | no real data | no real data | - | - | - | - |
| 19 | 4.0 | m_s | CERTIFIED | no real data | no real data | - | - | - | - |
| 19 | 1.6 | Czz_bar | NOT_CERTIFIED | no real data | no real data | - | - | - | - |
| 19 | 4.0 | Czz_bar | CERTIFIED | no real data | no real data | - | - | - | - |
| 19 | 1.6 | Z_bulk | NOT_CERTIFIED | no real data | no real data | - | - | - | - |
| 19 | 4.0 | Z_bulk | NOT_CERTIFIED | no real data | no real data | - | - | - | - |
| 57 | 1.1 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.002 | 0.003 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.2 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.003 | 0.004 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.3 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.005 | 0.006 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.4 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.008 | 0.009 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.6 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.019 | 0.020 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.8 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.039 | 0.040 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.0 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.068 | 0.069 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.5 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.269 | 0.270 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.0 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.762 | 0.764 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.2 | m_s | GRAY | CERTIFIED_s | resolved | 1.047 | 1.048 | GRAY | GRAY |
| 57 | 3.3 | m_s | GRAY | CERTIFIED_s | resolved | 1.086 | 1.087 | GRAY | GRAY |
| 57 | 3.4 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 1.307 | 1.309 | GRAY | GRAY |
| 57 | 3.6 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 1.826 | 1.827 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 4.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 3.081 | 3.119 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 4.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 5.349 | 5.391 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 5.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 8.807 | 9.316 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 5.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 11.541 | 12.197 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 6.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 14.398 | 15.789 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 1.1 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.007 | 0.008 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.2 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.009 | 0.010 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.3 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.012 | 0.013 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.4 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.017 | 0.018 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.6 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.033 | 0.034 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.8 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.058 | 0.059 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.0 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.092 | 0.093 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.5 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.308 | 0.309 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.0 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.803 | 0.805 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.2 | Czz_bar | GRAY | CERTIFIED_s | resolved | 1.080 | 1.081 | GRAY | GRAY |
| 57 | 3.3 | Czz_bar | GRAY | CERTIFIED_s | resolved | 1.110 | 1.112 | GRAY | GRAY |
| 57 | 3.4 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 1.327 | 1.329 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 3.6 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 1.831 | 1.833 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 4.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 3.101 | 3.106 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 4.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 5.610 | 5.613 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 5.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 10.340 | 10.355 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 5.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 14.746 | 14.884 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 6.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 20.026 | 22.299 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 57 | 1.1 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.001 | 0.002 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.2 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.001 | 0.002 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.002 | 0.003 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.4 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.004 | 0.005 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.6 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.008 | 0.009 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.8 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.015 | 0.016 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.026 | 0.027 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.5 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.095 | 0.096 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.261 | 0.262 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.366 | 0.368 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.6 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.612 | 0.614 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.0 | C2_bar | GRAY | CERTIFIED_s | resolved | 1.050 | 1.052 | GRAY | GRAY |
| 57 | 4.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 1.922 | 1.923 | GRAY | GRAY |
| 57 | 5.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 3.571 | 3.574 | GRAY | GRAY |
| 57 | 5.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 5.120 | 5.122 | GRAY | GRAY |
| 57 | 6.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 7.146 | 7.151 | GRAY | GRAY |
| 57 | 1.1 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.2 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.3 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.4 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.6 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.001 | 0.002 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.8 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.002 | 0.003 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.004 | 0.005 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.5 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.014 | 0.015 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.040 | 0.041 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.3 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.056 | 0.058 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.6 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.093 | 0.096 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.160 | 0.164 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.5 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.291 | 0.298 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.538 | 0.547 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.5 | Z_bulk | GRAY | NOT_CERTIFIED_s | resolved | 0.771 | 0.812 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 6.0 | Z_bulk | GRAY | CERTIFIED_s | resolved | 1.054 | 1.186 | GRAY | GRAY |
| 57 | 1.1 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.2 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.3 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.4 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.6 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.001 | 0.002 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.8 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.002 | 0.003 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.003 | 0.004 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.5 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.012 | 0.013 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.034 | 0.035 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.3 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.047 | 0.050 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.6 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.080 | 0.083 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.137 | 0.142 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.5 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.249 | 0.257 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.0 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.469 | 0.473 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.5 | Z_boundary | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.669 | 0.706 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 6.0 | Z_boundary | GRAY | NOT_CERTIFIED_s | resolved | 0.939 | 0.984 | GRAY | GRAY |
| 57 | 1.1 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.2 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.3 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.4 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.6 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.001 | 0.002 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.8 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.002 | 0.003 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.004 | 0.005 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.5 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.015 | 0.016 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.041 | 0.043 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.3 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.057 | 0.059 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.6 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.095 | 0.098 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.162 | 0.167 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.5 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.294 | 0.302 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.0 | Czz_edge | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.543 | 0.552 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.5 | Czz_edge | GRAY | NOT_CERTIFIED_s | resolved | 0.777 | 0.820 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 6.0 | Czz_edge | GRAY | CERTIFIED_s | resolved | 1.062 | 1.194 | GRAY | GRAY |
| 57 | 1.1 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.2 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.3 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.4 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.6 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.001 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 1.8 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.001 | 0.002 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.001 | 0.002 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 2.5 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.007 | 0.008 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.019 | 0.020 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.3 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.027 | 0.028 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 3.6 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.046 | 0.047 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.079 | 0.080 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 4.5 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.145 | 0.146 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.269 | 0.270 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 5.5 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.385 | 0.386 | NOT_CERTIFIED | NOT_CERTIFIED |
| 57 | 6.0 | Z_loop | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.538 | 0.539 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.1 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.007 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.2 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.009 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.3 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.004 | 0.010 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.4 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.008 | 0.013 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.6 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.021 | 0.025 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.8 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.042 | 0.045 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 2.0 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.083 | 0.085 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 2.5 | m_s | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.313 | 0.315 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 3.0 | m_s | GRAY | NOT_CERTIFIED_s | resolved | 0.834 | 0.849 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 3.3 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 1.339 | 1.361 | GRAY | GRAY |
| 115 | 3.6 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 2.567 | 2.578 | GRAY | GRAY |
| 115 | 4.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 4.587 | 4.671 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 4.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 8.477 | 8.480 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 5.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 11.314 | 11.439 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 5.5 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 21.212 | 23.296 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 6.0 | m_s | CERTIFIED | CERTIFIED_s | confirmed | 32.691 | 37.208 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 1.1 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.002 | 0.012 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.2 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.006 | 0.014 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.3 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.010 | 0.017 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.4 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.015 | 0.021 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.6 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.032 | 0.036 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.8 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.055 | 0.058 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 2.0 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.100 | 0.102 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 2.5 | Czz_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.329 | 0.331 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 3.0 | Czz_bar | GRAY | NOT_CERTIFIED_s | resolved | 0.816 | 0.818 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 3.3 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 1.285 | 1.286 | GRAY | GRAY |
| 115 | 3.6 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 2.439 | 2.442 | GRAY | GRAY |
| 115 | 4.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 4.535 | 4.540 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 4.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 8.843 | 8.852 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 5.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 12.896 | 12.909 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 5.5 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 28.736 | 29.551 | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 6.0 | Czz_bar | CERTIFIED | CERTIFIED_s | confirmed | 39.567 | - | CERTIFIED_EXACT | CERTIFIED_EXACT |
| 115 | 1.1 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.006 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.2 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.006 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.000 | 0.006 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.4 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.002 | 0.007 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.6 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.007 | 0.011 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 1.8 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.015 | 0.018 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 2.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.030 | 0.032 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 2.5 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.107 | 0.109 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 3.0 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.278 | 0.279 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 3.3 | C2_bar | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.444 | 0.445 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 3.6 | C2_bar | GRAY | NOT_CERTIFIED_s | resolved | 0.853 | 0.854 | NOT_CERTIFIED | NOT_CERTIFIED |
| 115 | 4.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 1.604 | 1.605 | GRAY | GRAY |
| 115 | 4.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 3.157 | 3.162 | GRAY | GRAY |
| 115 | 5.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 4.637 | 4.642 | GRAY | GRAY |
| 115 | 5.5 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 10.396 | 10.405 | GRAY | GRAY |
| 115 | 6.0 | C2_bar | CERTIFIED | CERTIFIED_s | confirmed | 17.381 | 17.415 | GRAY | GRAY |
| 115 | 4.0 | Z_bulk | NOT_CERTIFIED | NOT_CERTIFIED_s | confirmed | 0.109 | 0.112 | NOT_CERTIFIED | NOT_CERTIFIED |

## I-7. The accuracy factor at the test couplings (Sec. 4 of the declaration)

Rule: F_A = de_real(n, Jz)/de*_in(n, Jz) and F_B = de_real(n, 1.6)/de*_in(n, Jz), de*_in the stored rigorous inner threshold (explicit in-sector states) at Jz = 1.1-1.4; at 1.5 the threshold of the re-evaluated pool with q = 0. Headline: the smallest value over Jz = 1.1-1.4, rounded down to two significant digits. **Seen before the hash (F5):** every m_s value at 1.1-1.4 in both forms. **New:** Czz_bar, and the line at Jz = 1.5. de*_out is printed alongside and decides nothing (at 1.5 it is interpolated, not a bound; at n = 115, Jz = 1.1 the stored outer threshold of m_s is the floor value of the stored map).

| n | label | headline form A | smallest F_A | headline form B | smallest F_B |
|---|---|---|---|---|---|
| 57 | m_s | more than 110 | 116.47 | more than 85 | 85.74 |
| 57 | Czz_bar | more than 57 | 57.33 | more than 42 | 42.21 |
| 115 | m_s | more than 79 | 79.43 | more than 60 | 60.18 |
| 115 | Czz_bar | more than 49 | 49.20 | more than 37 | 37.27 |

| n | label | Jz | de_real | de*_in | de*_out | F_A | F_B | source of de*_in |
|---|---|---|---|---|---|---|---|---|
| 57 | m_s | 1.1 | 0.021400 | 5.4012e-05 | 4.9178e-05 | 396.22 | 210.22 | stored row (de_star_in) |
| 57 | m_s | 1.2 | 0.019759 | 7.3500e-05 | 7.0740e-05 | 268.83 | 154.48 | stored row (de_star_in) |
| 57 | m_s | 1.3 | 0.018017 | 9.9709e-05 | 9.7778e-05 | 180.69 | 113.88 | stored row (de_star_in) |
| 57 | m_s | 1.4 | 0.015424 | 1.3244e-04 | 1.3142e-04 | 116.47 | 85.74 | stored row (de_star_in) |
| 57 | m_s | 1.5 (apart) | 0.012613 | 2.0646e-04 | 1.7088e-04 | 61.09 | 55.00 | re-evaluated pool of Sec. 2 with q = 0 ([1.4, 1.6]) |
| 57 | Czz_bar | 1.1 | 0.021400 | 1.5927e-04 | 1.5426e-04 | 134.37 | 71.29 | stored row (de_star_in) |
| 57 | Czz_bar | 1.2 | 0.019759 | 1.8933e-04 | 1.8626e-04 | 104.36 | 59.97 | stored row (de_star_in) |
| 57 | Czz_bar | 1.3 | 0.018017 | 2.2549e-04 | 2.2382e-04 | 79.90 | 50.35 | stored row (de_star_in) |
| 57 | Czz_bar | 1.4 | 0.015424 | 2.6903e-04 | 2.6754e-04 | 57.33 | 42.21 | stored row (de_star_in) |
| 57 | Czz_bar | 1.5 (apart) | 0.012613 | 3.2040e-04 | 3.1726e-04 | 39.36 | 35.44 | re-evaluated pool of Sec. 2 with q = 0 ([1.4, 1.6]) |
| 115 | m_s | 1.1 | 0.022729 | 1.5886e-04 | 8.6957e-10 | 143.07 | 73.52 | stored row (de_star_in) |
| 115 | m_s | 1.2 | 0.019683 | 1.5799e-04 | 1.7097e-05 | 124.58 | 73.93 | stored row (de_star_in) |
| 115 | m_s | 1.3 | 0.017174 | 1.7079e-04 | 7.0512e-05 | 100.56 | 68.39 | stored row (de_star_in) |
| 115 | m_s | 1.4 | 0.015418 | 1.9410e-04 | 1.2679e-04 | 79.43 | 60.18 | stored row (de_star_in) |
| 115 | m_s | 1.5 (apart) | 0.015706 | 2.6236e-04 | 1.7881e-04 | 59.86 | 44.52 | re-evaluated pool of Sec. 2 with q = 0 ([1.4, 1.6]) |
| 115 | Czz_bar | 1.1 | 0.022729 | 2.6351e-04 | 5.6937e-05 | 86.25 | 44.32 | stored row (de_star_in) |
| 115 | Czz_bar | 1.2 | 0.019683 | 2.6419e-04 | 1.2203e-04 | 74.50 | 44.21 | stored row (de_star_in) |
| 115 | Czz_bar | 1.3 | 0.017174 | 2.8127e-04 | 1.8530e-04 | 61.06 | 41.53 | stored row (de_star_in) |
| 115 | Czz_bar | 1.4 | 0.015418 | 3.1337e-04 | 2.4626e-04 | 49.20 | 37.27 | stored row (de_star_in) |
| 115 | Czz_bar | 1.5 (apart) | 0.015706 | 3.3999e-04 | 3.0608e-04 | 46.20 | 34.35 | re-evaluated pool of Sec. 2 with q = 0 ([1.4, 1.6]) |

de_real(n, 1.6) = 0.011355 (n = 57) and 0.011680 (n = 115). Stated with the number, as declared: the in-sector window is a subset of what the energy and the mean magnetization allow, so each factor is a lower bound on what the weaker hypothesis would require.

## I-8. The label filter on the 45 real training labels per size (Sec. 6 of the declaration)

Rule (m_s primary, Czz_bar secondary): keep a label iff its row is CERTIFIED (exact). Guarantee: a kept label is within tau of the truth, given the published energy and site magnetizations (hypothesis H). The like-for-like version (stored thresholds, interpolated where there is no row; the paper's present filter) is next to it. Miss = |label - truth|/tau. **Seen before the hash:** every miss of m_s (F7) and the like-for-like counts at the stored couplings (F9: n = 57 identical to the line below; n = 115 was counted from Jz = 3.3, 28 labels, and becomes 30 here because the interpolated thresholds also pass 3.1 and 3.2). **New:** the exact filter, and everything about Czz_bar.

| n | label | version | kept | kept couplings | largest miss kept | mean miss kept | dropped | largest miss dropped | mean miss dropped | dropped within tau/2 | dropped within tau | dropped above tau | kept above tau/2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 57 | m_s | exact | 26 | 3.5-6.0 | 0.1746 | 0.0815 | 19 | 1.6685 | 0.6215 | 10 | 15 | 4 | 0 |
| 57 | m_s | exact reference free | 26 | 3.5-6.0 | 0.1746 | 0.0815 | 19 | 1.6685 | 0.6215 | 10 | 15 | 4 | 0 |
| 57 | m_s | like for like | 29 | 3.2-6.0 | 0.2071 | 0.0931 | 16 | 1.6685 | 0.7018 | 7 | 12 | 4 | 0 |
| 115 | m_s | exact | 21 | 4.0-6.0 | 0.0639 | 0.0358 | 24 | 1.5427 | 0.4343 | 17 | 21 | 3 | 0 |
| 115 | m_s | exact reference free | 21 | 4.0-6.0 | 0.0639 | 0.0358 | 24 | 1.5427 | 0.4343 | 17 | 21 | 3 | 0 |
| 115 | m_s | like for like | 30 | 3.1-6.0 | 0.1627 | 0.0600 | 15 | 1.5427 | 0.6249 | 8 | 12 | 3 | 0 |
| 57 | Czz_bar | exact | 27 | 3.4-6.0 | 0.1608 | 0.0806 | 18 | 1.1700 | 0.5104 | 10 | 16 | 2 | 0 |
| 57 | Czz_bar | exact reference free | 27 | 3.4-6.0 | 0.1608 | 0.0806 | 18 | 1.1700 | 0.5104 | 10 | 16 | 2 | 0 |
| 57 | Czz_bar | like for like | 29 | 3.2-6.0 | 0.1869 | 0.0876 | 16 | 1.1700 | 0.5516 | 8 | 14 | 2 | 0 |
| 115 | Czz_bar | exact | 21 | 4.0-6.0 | 0.0590 | 0.0312 | 24 | 1.1113 | 0.3373 | 18 | 23 | 1 | 0 |
| 115 | Czz_bar | exact reference free | 21 | 4.0-6.0 | 0.0590 | 0.0312 | 24 | 1.1113 | 0.3373 | 18 | 23 | 1 | 0 |
| 115 | Czz_bar | like for like | 30 | 3.1-6.0 | 0.1398 | 0.0512 | 15 | 1.1113 | 0.4809 | 9 | 14 | 1 | 0 |

Cost of the exact filter, in words: at n = 57 it drops 19 m_s labels, of which 10 are within tau/2 and 15 within tau of the truth; at n = 115 it drops 24, of which 17 and 21. No kept label is above tau/2 in any version. Said in advance by the declaration: where the labels are already accurate the filter buys a guarantee, not accuracy.

**The small classical calculation next to every label (descriptive, no rule).** |m_s(exact, n = 19) - m_s^GS(n)|/tau: largest value over the kept labels 0.1344 (n = 57) and 0.1424 (n = 115); at the test couplings 1.1-1.4: 1.472, 1.339, 1.194, 1.052 (n = 57) and 2.067, 1.847, 1.630, 1.431 (n = 115). The paper's sentence ("a range in which an exact 19-site calculation already lies within a fifth of the tolerance") re-evaluated on the kept set: true at n = 57, true at n = 115. New (no real datum enters these numbers except through the kept set).

**n = 57, every training label** (k = kept, d = dropped; widths rounded up, misses rounded up).

| Jz | m_s miss/tau | exact | exact width/tau | like-for-like | n = 19 exact calculation, miss/tau | Czz_bar miss/tau | exact | exact width/tau | like-for-like |
|---|---|---|---|---|---|---|---|---|---|
| 1.6 | 1.6685 | d | - | d | 0.8090 | 1.1700 | d | - | d |
| 1.7 | 1.4264 | d | - | d | 0.7101 | 1.0396 | d | - | d |
| 1.8 | 1.1455 | d | - | d | 0.6253 | 0.8475 | d | - | d |
| 1.9 | 1.0872 | d | - | d | 0.5529 | 0.8526 | d | - | d |
| 2.0 | 0.8946 | d | - | d | 0.4911 | 0.7023 | d | - | d |
| 2.1 | 0.8609 | d | - | d | 0.4383 | 0.7092 | d | - | d |
| 2.2 | 0.7460 | d | - | d | 0.3931 | 0.6246 | d | - | d |
| 2.3 | 0.6437 | d | - | d | 0.3541 | 0.5350 | d | - | d |
| 2.4 | 0.5282 | d | - | d | 0.3204 | 0.4337 | d | - | d |
| 2.5 | 0.4105 | d | - | d | 0.2912 | 0.3458 | d | - | d |
| 2.6 | 0.4102 | d | - | d | 0.2657 | 0.3480 | d | - | d |
| 2.7 | 0.3356 | d | - | d | 0.2433 | 0.2891 | d | - | d |
| 2.8 | 0.3302 | d | - | d | 0.2236 | 0.2830 | d | 4.3438 | d |
| 2.9 | 0.2979 | d | - | d | 0.2062 | 0.2583 | d | 2.2126 | d |
| 3.0 | 0.2301 | d | - | d | 0.1907 | 0.2001 | d | 1.4617 | d |
| 3.1 | 0.2135 | d | - | d | 0.1769 | 0.1870 | d | 1.2151 | d |
| 3.2 | 0.1938 | d | - | k | 0.1646 | 0.1757 | d | 1.0623 | k |
| 3.3 | 0.2071 | d | - | k | 0.1535 | 0.1869 | d | 1.0214 | k |
| 3.4 | 0.1799 | d | 1.0043 | k | 0.1435 | 0.1607 | k | 0.9303 | k |
| 3.5 | 0.1635 | k | 0.9105 | k | 0.1344 | 0.1481 | k | 0.8420 | k |
| 3.6 | 0.1475 | k | 0.8346 | k | 0.1262 | 0.1354 | k | 0.7863 | k |
| 3.7 | 0.1746 | k | 0.8811 | k | 0.1187 | 0.1608 | k | 0.8214 | k |
| 3.8 | 0.1174 | k | 0.7007 | k | 0.1119 | 0.1082 | k | 0.6693 | k |
| 3.9 | 0.1203 | k | 0.6791 | k | 0.1056 | 0.1110 | k | 0.6629 | k |
| 4.0 | 0.1097 | k | 0.6092 | k | 0.0999 | 0.1026 | k | 0.6007 | k |
| 4.1 | 0.1055 | k | 0.6009 | k | 0.0946 | 0.0994 | k | 0.5717 | k |
| 4.2 | 0.0908 | k | 0.5487 | k | 0.0898 | 0.0862 | k | 0.5192 | k |
| 4.3 | 0.0667 | k | 0.4753 | k | 0.0853 | 0.0601 | k | 0.4492 | k |
| 4.4 | 0.0817 | k | 0.4905 | k | 0.0811 | 0.0777 | k | 0.4717 | k |
| 4.5 | 0.0780 | k | 0.4542 | k | 0.0772 | 0.0738 | k | 0.4455 | k |
| 4.6 | 0.0756 | k | 0.4409 | k | 0.0737 | 0.0724 | k | 0.4279 | k |
| 4.7 | 0.0699 | k | 0.4140 | k | 0.0703 | 0.0661 | k | 0.3990 | k |
| 4.8 | 0.0631 | k | 0.3799 | k | 0.0672 | 0.0595 | k | 0.3713 | k |
| 4.9 | 0.0593 | k | 0.3554 | k | 0.0643 | 0.0567 | k | 0.3517 | k |
| 5.0 | 0.0515 | k | 0.3231 | k | 0.0616 | 0.0499 | k | 0.3259 | k |
| 5.1 | 0.0654 | k | 0.3589 | k | 0.0590 | 0.0639 | k | 0.3567 | k |
| 5.2 | 0.0550 | k | 0.3225 | k | 0.0566 | 0.0534 | k | 0.3195 | k |
| 5.3 | 0.0451 | k | 0.2864 | k | 0.0544 | 0.0444 | k | 0.2851 | k |
| 5.4 | 0.0806 | k | 0.4041 | k | 0.0523 | 0.0835 | k | 0.3927 | k |
| 5.5 | 0.0446 | k | 0.2649 | k | 0.0503 | 0.0439 | k | 0.2715 | k |
| 5.6 | 0.0376 | k | 0.2435 | k | 0.0484 | 0.0374 | k | 0.2508 | k |
| 5.7 | 0.0733 | k | 0.3734 | k | 0.0466 | 0.0767 | k | 0.3640 | k |
| 5.8 | 0.0394 | k | 0.2356 | k | 0.0450 | 0.0392 | k | 0.2432 | k |
| 5.9 | 0.0667 | k | 0.3326 | k | 0.0434 | 0.0696 | k | 0.3380 | k |
| 6.0 | 0.0374 | k | 0.2179 | k | 0.0419 | 0.0377 | k | 0.2283 | k |

The five labels apart (m_s; none is kept by any version): Jz = 1.1, miss 4.955 tau; Jz = 1.2, miss 4.097 tau; Jz = 1.3, miss 3.456 tau; Jz = 1.4, miss 2.690 tau; Jz = 1.5, miss 2.005 tau.

**n = 115, every training label** (k = kept, d = dropped; widths rounded up, misses rounded up).

| Jz | m_s miss/tau | exact | exact width/tau | like-for-like | n = 19 exact calculation, miss/tau | Czz_bar miss/tau | exact | exact width/tau | like-for-like |
|---|---|---|---|---|---|---|---|---|---|
| 1.6 | 1.5427 | d | - | d | 1.0985 | 1.1113 | d | - | d |
| 1.7 | 1.2865 | d | - | d | 0.9659 | 0.9473 | d | - | d |
| 1.8 | 1.1361 | d | - | d | 0.8526 | 0.8792 | d | - | d |
| 1.9 | 0.9122 | d | - | d | 0.7561 | 0.6950 | d | - | d |
| 2.0 | 0.7540 | d | - | d | 0.6737 | 0.5792 | d | - | d |
| 2.1 | 0.7159 | d | - | d | 0.6032 | 0.5849 | d | - | d |
| 2.2 | 0.5341 | d | - | d | 0.5426 | 0.4125 | d | - | d |
| 2.3 | 0.4725 | d | - | d | 0.4903 | 0.3701 | d | - | d |
| 2.4 | 0.4096 | d | - | d | 0.4450 | 0.3249 | d | - | d |
| 2.5 | 0.3436 | d | - | d | 0.4055 | 0.2679 | d | - | d |
| 2.6 | 0.3046 | d | - | d | 0.3709 | 0.2432 | d | - | d |
| 2.7 | 0.2675 | d | - | d | 0.3405 | 0.2154 | d | - | d |
| 2.8 | 0.2800 | d | - | d | 0.3136 | 0.2368 | d | - | d |
| 2.9 | 0.2170 | d | - | d | 0.2898 | 0.1806 | d | - | d |
| 3.0 | 0.1979 | d | - | d | 0.2685 | 0.1657 | d | - | d |
| 3.1 | 0.1592 | d | - | k | 0.2495 | 0.1281 | d | - | k |
| 3.2 | 0.1627 | d | - | k | 0.2325 | 0.1398 | d | - | k |
| 3.3 | 0.1524 | d | - | k | 0.2171 | 0.1325 | d | - | k |
| 3.4 | 0.1174 | d | - | k | 0.2033 | 0.0964 | d | 8.9446 | k |
| 3.5 | 0.1131 | d | - | k | 0.1907 | 0.0948 | d | 1.5996 | k |
| 3.6 | 0.0960 | d | - | k | 0.1792 | 0.0798 | d | 0.9576 | k |
| 3.7 | 0.0941 | d | - | k | 0.1688 | 0.0804 | d | 0.7781 | k |
| 3.8 | 0.0799 | d | - | k | 0.1592 | 0.0670 | d | 0.6379 | k |
| 3.9 | 0.0748 | d | - | k | 0.1505 | 0.0639 | d | 0.5766 | k |
| 4.0 | 0.0639 | k | 0.5148 | k | 0.1424 | 0.0529 | k | 0.5124 | k |
| 4.1 | 0.0634 | k | 0.5696 | k | 0.1350 | 0.0546 | k | 0.5009 | k |
| 4.2 | 0.0631 | k | 0.6069 | k | 0.1282 | 0.0547 | k | 0.4877 | k |
| 4.3 | 0.0572 | k | 0.6198 | k | 0.1219 | 0.0506 | k | 0.4607 | k |
| 4.4 | 0.0463 | k | 0.5938 | k | 0.1160 | 0.0390 | k | 0.4176 | k |
| 4.5 | 0.0412 | k | 0.5871 | k | 0.1106 | 0.0346 | k | 0.3994 | k |
| 4.6 | 0.0414 | k | 0.6005 | k | 0.1055 | 0.0364 | k | 0.4040 | k |
| 4.7 | 0.0393 | k | 0.5867 | k | 0.1008 | 0.0340 | k | 0.3983 | k |
| 4.8 | 0.0611 | k | 0.6650 | k | 0.0964 | 0.0590 | k | 0.4618 | k |
| 4.9 | 0.0310 | k | 0.5296 | k | 0.0922 | 0.0262 | k | 0.3882 | k |
| 5.0 | 0.0336 | k | 0.5314 | k | 0.0884 | 0.0301 | k | 0.4016 | k |
| 5.1 | 0.0247 | k | 0.4675 | k | 0.0847 | 0.0204 | k | 0.3383 | k |
| 5.2 | 0.0313 | k | 0.4822 | k | 0.0813 | 0.0288 | k | 0.3331 | k |
| 5.3 | 0.0218 | k | 0.4087 | k | 0.0781 | 0.0182 | k | 0.2458 | k |
| 5.4 | 0.0242 | k | 0.3951 | k | 0.0751 | 0.0213 | k | 0.2425 | k |
| 5.5 | 0.0191 | k | 0.3408 | k | 0.0723 | 0.0160 | k | 0.2093 | k |
| 5.6 | 0.0173 | k | 0.3013 | k | 0.0696 | 0.0144 | k | 0.1958 | k |
| 5.7 | 0.0181 | k | 0.2747 | k | 0.0671 | 0.0158 | k | 0.1965 | k |
| 5.8 | 0.0265 | k | 0.2790 | k | 0.0647 | 0.0251 | k | 0.2245 | k |
| 5.9 | 0.0143 | k | 0.1845 | k | 0.0624 | 0.0120 | k | 0.1622 | k |
| 6.0 | 0.0137 | k | 0.1446 | k | 0.0603 | 0.0115 | k | 0.1546 | k |

The five labels apart (m_s; none is kept by any version): Jz = 1.1, miss 4.667 tau; Jz = 1.2, miss 3.627 tau; Jz = 1.3, miss 2.948 tau; Jz = 1.4, miss 2.372 tau; Jz = 1.5, miss 1.709 tau.

## I-9. The nested sets of Sec. 7 (f3), fixed here for the learning task

`out/S_sets.json`, SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4` (also in `out/S_sets.sha256`), written by the sealed code before any other output and before any learning number. Stored certificates only (no E1).

| n | S (interval <= tau) | S_3/4 | S_1/2 | S_p |
|---|---|---|---|---|
| 57 | 26: 3.5-6.0 | 23: 3.8-6.0 | 18: 4.3-6.0 | S_1/2 (18 couplings) |
| 115 | 21: 4.0-6.0 | 21: 4.0-6.0 | 10: 5.1-6.0 | S_3/4 (21 couplings) |

## I-10. Gates G1-G7

| gate | rule | outcome | numbers |
|---|---|---|---|
| G1 data | converter re-run on the pinned archive reproduces `converted/SHA256SUMS.txt` | **NOT COMPLETE** | the three converted files have the SHA-256 of `converted/SHA256SUMS.txt` and of Sec. 11 of the declaration; the archive has its pinned SHA-256 (checked by this task with `sha256sum`); the converter was NOT run again: it reads the archive through a restricted unpickler and this task was told to unpickle nothing |
| G2 same state, n = 57 | exchange part of E_real inside [-B, B] at every coupling | **PASS** | 50 couplings; exchange/B between -0.9890 and -0.9318; negative radicands: 0; failed: none (seen, T3) |
| G3 energies, n = 57 | E_real >= E0(authors) at every coupling | **PASS** | E_real - E0 between 0.0468 and 1.2198; failed: none (seen, T4) |
| G4 truth, n = 57 | authors' DMRG against this project's references: at most 1e-3 tau per label, 1e-4 in E0 | **PASS** | 116 label rows, largest difference 1.46e-04 tau; 18 energies, largest difference 1.87e-06 (seen, T5) |
| G2 same state, n = 115 | exchange part of E_real inside [-B, B] at every coupling | **PASS** | 50 couplings; exchange/B between -0.9965 and -0.9520; negative radicands: 0; failed: none (seen, T3) |
| G3 energies, n = 115 | E_real >= E0(authors) at every coupling | **PASS** | E_real - E0 between 0.0458 and 2.6138; failed: none (seen, T4) |
| G4 truth, n = 115 | authors' DMRG against this project's references: at most 1e-3 tau per label, 1e-4 in E0 | **PASS** | 49 label rows, largest difference 2.79e-04 tau; 16 energies, largest difference 3.01e-05 (seen, T5) |
| G5 certificates, records | every certificate used has a recorded exact verification | **PASS** | 220 files, 214 distinct, 140 used; excluded for a missing or bad record: 0 |
| G5 certificates, re-proof | the certificates that decide J*_exact and the boundary of the filter re-proved with `myverify.py` | **PASS** | 12 certificates re-proved in this run (operator identity and every cluster inequality, exact arithmetic, method `chol`); all equal the claimed bound: True |
| G6 linear rule against tensors | decisive witness components of the NOT CERTIFIED rows within 0.3 of a J* and of ten rows drawn with the seed: agreement to 1e-8 | **NOT COMPLETE** | 32 rows selected (22 near a J*, 10 drawn, seed 1845216616); 150 components; checked: 0; without tensors on the laptop: 150 |
| G6 re-evaluated energies | every re-evaluated in-sector energy at least E0(Jz) - 1e-6 | **PASS** | 472 rows with a re-evaluated pool; smallest (lowest pool energy - E0) = 9.78e-06; failed: 0 |
| G7 filter | every CERTIFIED (exact) label and its truth inside its interval | **PASS** | 95 certified rows (either tolerance), violations: 0; of the 108 rows with an interval of any width, 0 do not contain label and truth |

No gate failed, so no row is "no decision" (0 rows without decision). G1 and the first part of G6 are NOT COMPLETE and are not reported as passes (Sec. 12 line 14 of the declaration).

Certificates re-proved for G5: `v2_n115_vball2_Czz_bar_m4.0_l0.215619`, `v2_n115_vball2_Czz_bar_p4.0_l0.142866`, `v2_n115_vball2_Czz_bar_p4.0_l0.154158`, `v2_n115_vball2_m_s_m4.0_l0.144973`, `v2_n115_vball2_m_s_p4.0_l0.272766`, `v2_n57_eball2_Czz_bar_m3.4_l0.254136`, `v2_n57_eball2_Czz_bar_p3.4_l0.166339`, `v2_n57_eball2_m_s_m3.4_l0.125924`, `v2_n57_eball2_m_s_m3.6_l0.123765`, `v2_n57_eball2_m_s_p3.4_l0.305157`, `v2_n57_eball2_m_s_p3.6_l0.304711`, `v2_n57_vball2_Czz_bar_p5.0_l0.189045`.

**Post hoc supplement to G6 (not the gate; `checks/g6_supplement.py`).** The tensors on the laptop belong to 6 stored states (n = 57, Jz = 1.6). (A) Among the (row, component) pairs of all 439 NOT CERTIFIED rows, 4 have tensors here (m_s at n = 57, Jz = 1.5, 1.6, 1.6, 1.7; largest difference 1.5e-13). (B) Each of the 6 states evaluated from its tensors at Jz = 1.5 and 1.7 with the independent evaluator against the linear rule: 12 pairs, largest difference 1.6e-13, all within 1e-8: yes. This supports the linear rule as an identity; it does not check the decisive components.

## I-11. Secondary rows (Sec. 3 of the declaration)

**Window at E_first (first-stage states, in the sector by construction), m_s, like-for-like. New.**

| n | de_first range | CERTIFIED_s at | NOT CERTIFIED_s at | GRAY_s at | J*_s |
|---|---|---|---|---|---|
| 57 | 0.0049 to 0.0852 | 4.9-6.0 | 1.1-4.8 | none | 4.9 |
| 115 | 0.0286 to 0.1497 | none | 1.1-6.0 | none | - |

**Comparison variant (`skqd_post_select`), secondary everywhere. New.**

| n | what is public | gate G2 | gate G3 | label | J*_s | CERTIFIED_s | NOT CERTIFIED_s | CERTIFIED (exact) | NOT CERTIFIED (explicit) | GRAY (Sec. 2) | training couplings |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 57 | energies only | - | PASS | m_s | 3.6 | 25 | 20 | - | - | - | 45 |
| 57 | energies only | - | PASS | Czz_bar | 3.6 | 25 | 20 | - | - | - | 45 |
| 57 | energies only | - | PASS | C2_bar | 4.7 | 14 | 31 | - | - | - | 45 |
| 115 | energies and labels (minus Jz = 5.6, 5.7, 5.9, 6.0) | PASS | PASS | m_s | - | 26 | 15 | 17 | 15 | 9 | 41 |
| 115 | energies and labels (minus Jz = 5.6, 5.7, 5.9, 6.0) | PASS | PASS | Czz_bar | - | 26 | 15 | 17 | 15 | 9 | 41 |
| 115 | energies and labels (minus Jz = 5.6, 5.7, 5.9, 6.0) | PASS | PASS | C2_bar | - | 19 | 22 | 0 | 21 | 20 | 41 |

At n = 115 the comparison variant has no J* because its largest training coupling (6.0) is one of the four excluded by gate G2 and a coupling without a status is not a certified point. Its rows are in `out/map_secondary.json`.

**Extension E1.** Not available when the map was run (`real_data/e1/` held no certificate). There is no E1 column in these results. S, S_3/4, S_1/2 and S_p never use E1. Note for whoever adds the column: with certificates in `e1/` the sealed code adds a key `secondary_E1` to `S_sets.json`, whose SHA-256 would then differ; it refuses to overwrite the existing file. Run it with another `--out` folder so that the hashed `out/S_sets.json` stays as it is.

## I-12. Post hoc: independent check of the exact intervals (`checks/spotcheck_exact_intervals.py`; not declared, decides nothing)

A separate script of this task, written from the text of the declaration, importing nothing of the sealed code (standard library, `fractions.Fraction`), rebuilt the interval of m_s and Czz_bar at all 50 couplings of both sizes from the certificate files and the converted data. Rows compared with the sealed output: 200; identical in both ends as exact rationals and in both flags: 200. Certified rows whose label or truth lies outside the interval: 0. Its counts: n = 115 Czz_bar (tau): 21 of 45, J*_exact 4.0; n = 115 Czz_bar (tau_rf): 21 of 45, J*_exact 4.0; n = 115 m_s (tau): 21 of 45, J*_exact 4.0; n = 115 m_s (tau_rf): 21 of 45, J*_exact 4.0; n = 57 Czz_bar (tau): 27 of 45, J*_exact 3.4; n = 57 Czz_bar (tau_rf): 27 of 45, J*_exact 3.4; n = 57 m_s (tau): 26 of 45, J*_exact 3.5; n = 57 m_s (tau_rf): 26 of 45, J*_exact 3.5. Six rows are printed in full in `checks/spotcheck_exact_intervals_stdout.txt` (m_s at n = 57, Jz = 3.4 and 3.5; m_s at n = 115, Jz = 4.0 and 5.0; Czz_bar at n = 57, Jz = 5.0 and at n = 115, Jz = 4.0).

**Post hoc: explicit states against exact bounds (`checks/finalize_rd_map.py`; not declared, decides nothing).** The two explicit witness mixtures of a row lie in W(E_real, M_real), so their labels must lie inside the exact interval of the same row. rows with both an exact interval and a witness interval: 108; violations: 0 []; smallest distance of a witness end to the corresponding end of I: 0.000202. The two sides of Sec. 2 (stored DMRG states, exact-arithmetic certificates) do not depend on each other, so this checks both.

## I-13. Re-executed, only compared, not checked

- **Re-executed by this task:** the sealed map code on `converted/` (one run, default options: hash check of G1, G2-G7, re-proof of the deciding certificates); the independent recomputation of the 200 exact rows (Sec. 12); the post hoc supplement to G6; `sha256sum` of the declaration, of every code file listed in Sec. 11 of the declaration (all equal) and of the pinned archive.
- **Only compared (not recomputed here):** the stored map (chains, thresholds, states), read through its own code; the stored exact certificates other than the 12 re-proved for G5 (each has its recorded verification; 196 distinct ones were re-proved by the review report `math-rigorous-bounds`); this project's references against the authors' DMRG (G4).
- **Not checked:** the conversion of the archive (G1 re-run); the energies of the decisive witness components from their tensors (G6, first part); that the published energy and site magnetizations belong to one state beyond the necessary condition of G2; the unit tests were not run again (gate G8 was passed and recorded by the sealing task).
- **Code:** no sealed file was changed. SHA-256 of the six map code files at run time (from `out/map_summary.json`): `map_certs.py` 3922350fea086147; `map_common.py` ec8f92a779305718; `map_gates.py` 5f1f47a4b0b8e719; `map_stored.py` e1214cf36f5a3c08; `map_tables.py` a1c04230ef8b5db3; `run_map.py` 199e5b0a0a6c0851.
- **Files:** `out/S_sets.json`, `out/S_sets.sha256`, `out/map_rows.json`, `out/map_summary.json`, `out/map_secondary.json`, `out/map_gates.json`, `out/map_tables.md`, `out/SHA256SUMS_map.txt`, `out/g5/` (sealed code); `out/map_real.json`, `results/RESULTS_map.md` (this script); `checks/spotcheck_exact_intervals.*`, `checks/g6_supplement.*`, `checks/finalize_rd_map.py`, `checks/consistency_witness_inside_exact.txt`; `DEVIATIONS.md`; hashes in `results/SHA256SUMS_rd-map.txt`.

# Part II. The predictions of the emulation on the real labels

Verbatim from `results/RESULTS_predict.md` (SHA-256 `0692f9e77d74d27d247bbe1e26c481e718866a64e2dfe7d27b71b2c6d3867131`), without its Spanish summary. Original title: "Real data of arXiv:2606.15983: RESULTS of the predictions (declaration Sec. 5) and of the n = 19 comparison (Sec. 6)".

Task `rd-predict`, 2026-11-12. Declaration: `real_data/DECLARATION.md`, SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa` (checked before anything was read).
Every outcome below is the output of the sealed code `code/run_predict.py`, run unchanged. No rule was changed.

## II-Summary (English)

| analysis | declared rule | outcome |
|---|---|---|
| P1-P3 sign, sites, n = 57 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 1.000000; 0 of 2850 pairs not positive) |
| P1-P3 sign, edges, n = 57 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 0.999375; 2 of 3200 pairs not positive) |
| P1-P3 sign, second neighbours, n = 57 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 1.000000; 0 of 4350 pairs not positive) |
| P1-P3 sign, loops, n = 57 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 1.000000; 0 of 200 pairs not positive) |
| P1-P3 sign, sites, n = 115 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 0.999652; 2 of 5750 pairs not positive) |
| P1-P3 sign, edges, n = 115 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 0.999545; 3 of 6600 pairs not positive) |
| P1-P3 sign, second neighbours, n = 115 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 0.999243; 7 of 9250 pairs not positive) |
| P1-P3 sign, loops, n = 115 | F >= 0.95 over the 50 couplings | **HOLDS** (F = 0.998333; 1 of 600 pairs not positive) |
| P4 error decreases with Jz, sites, n = 57 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.980216) |
| P4 error decreases with Jz, edges, n = 57 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.972629) |
| P4 error decreases with Jz, second neighbours, n = 57 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.975894) |
| P4 error decreases with Jz, loops, n = 57 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.971957) |
| P4 error decreases with Jz, sites, n = 115 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.995486) |
| P4 error decreases with Jz, edges, n = 115 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.992413) |
| P4 error decreases with Jz, second neighbours, n = 115 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.992893) |
| P4 error decreases with Jz, loops, n = 115 | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (-0.994334) |
| P5 bias-against-energy curve (one decision) | mean miss <= 0.2 tau (n = 57) and <= 0.6 tau (n = 115), and every ratio in [0.75, 1.3] where the raw miss is at least 0.2 tau; 50 couplings of each size | **FAIL** |
| P5, part n = 57 | | mean miss 0.111 tau: met. Ratios at the 22 deciding couplings 0.802-1.046: all inside. |
| P5, part n = 115 | | mean miss 0.168 tau: met. Ratios at the 19 deciding couplings 0.608-0.813: **12 outside, all below 0.75** (Jz = 1.5, 1.6, 1.7, 1.9, 2.0, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.9). |
| P5 on the 45 training couplings (reported, does not decide) | same rule | FAIL (n = 115: 11 of 14 deciding ratios outside) |
| n = 19 comparison of Sec. 6 | descriptive, no rule | see Sec. 5 below |

**Gate note, printed with every result (declaration Sec. 12, line 14).** G1 is NOT COMPLETE: the converter was not re-run on the pinned archive; the three converted files have the pinned SHA-256 (checked by the sealed loader at every read, by the map task and by this task). G2, G3 and G4 pass for the dataset at both sizes (map task; re-checked here with own code, Sec. 7). G8 was passed before the hash.

**What P5 means for Sec. V of the paper, as the declaration states it (Sec. 5, P5):** "the curve was built for the first stage (truncation in the computational basis). The real labels come after a rotation that lowers the energy error per site five- to tenfold. A pass extends Sec. V to the full method; a fail restricts Sec. V to the first stage, and the paper says so." The outcome is FAIL. **Sec. V is therefore restricted to the first stage, and the paper has to say so.** The declared prior for a pass was 0.4.

Marks on numbers: **[S]** already seen before the hash (item of declaration Sec. 1 in brackets); **[N]** not seen and not computed before the hash; **[0]** involves no real datum (exact n = 19 and the truth, both in hand before the hash).

## II-1. What was run

- `DECLARATION.sha256` equals the SHA-256 of `DECLARATION.md` (`sha256sum`; the gate of the sealed code; the independent script). `python -B -I checks/make_manifest.py --check`: 69 lines of Sec. 11 equal to the files on disk, 0 different, 4 not re-hashed there (`converted/`, `source/`). The four code and two n = 19 files used here were hashed again by this script and equal Sec. 11: `code/run_predict.py`, `code/rd_predict.py`, `code/rd_common.py`, `code/n19_curves.py`, `out/n19/n19_curves.json`, `out/n19/n19_labels.json`.
- Command: `python -B -I code/run_predict.py --hash=6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa` (Python 3.11.4, numpy 1.26.4, scipy 1.13.1, two threads, laptop; about 3 s).
- Run 1: 2026-11-12T19:28:35Z to 2026-11-12T19:28:39Z UTC, before `out/S_sets.json` existed (kept set of the filter not available). Run 2: 2026-11-12T19:36:08Z to 2026-11-12T19:36:10Z UTC, after the map task had written `out/S_sets.json` (SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4`, equal to `out/S_sets.sha256`). The two outputs are identical except for the kept-set part of the n = 19 comparison (compared key by key). Run 1 is kept in `out/predict/first_run_before_S_sets/`.
- Output of the sealed code: `out/predict/predict_results.json` (SHA-256 `04be4924ea62f10c201afa8a713fb365d4308af67de74920d09ef450f92c2ac8`), copied verbatim into `out/predict_real.json` together with provenance, the independent check and the post hoc lines.
- Truth (declaration Sec. 0 and Sec. 12, line 1): this project's bond-dimension-320 references for E0 and m_s at 18 (n = 57) and 16 (n = 115) couplings, the authors' DMRG elsewhere and for every single site, pair and loop. Orientation +1 at every coupling for labels and truth: True (57), True (115).
- No code defect was found. Nothing listed in Sec. 11 was changed. See `DEVIATIONS.md` for the dated notes of this task.

## II-2. P1-P3: every label lies on the Neel side of the truth

Rule: t_x = (o_real - o_GS) / (o_Neel - o_GS); F = fraction of (item, coupling) pairs with t_x > 0 over the 50 couplings; **holds iff F >= 0.95**, decided separately for each family and size (eight outcomes). Neel values eta_i, -1, +1, +1.

| n | family | items | pairs | pairs with t <= 0 | F | outcome | fraction with t <= 1 | smallest t | largest t | seen before? |
|---|---|---|---|---|---|---|---|---|---|---|
| 57 | sites | 57 | 2850 | 0 | 1.000000 | **HOLDS** | 1.0000 | 0.0550 | 0.6157 | [S] at 14 couplings (F8: Jz = 1.1-2.0, 3.0, 4.0, 5.0, 6.0), [N] at the other 36 |
| 57 | edges | 64 | 3200 | 2 | 0.999375 | **HOLDS** | 1.0000 | -0.0164 | 0.6503 | [N] |
| 57 | second neighbours | 87 | 4350 | 0 | 1.000000 | **HOLDS** | 1.0000 | 0.0652 | 0.4467 | [N] |
| 57 | loops | 4 | 200 | 0 | 1.000000 | **HOLDS** | 1.0000 | 0.0694 | 0.3432 | [N] |
| 115 | sites | 115 | 5750 | 2 | 0.999652 | **HOLDS** | 1.0000 | -1.6901 | 0.6085 | [S] at 14 couplings (F8: Jz = 1.1-2.0, 3.0, 4.0, 5.0, 6.0), [N] at the other 36 |
| 115 | edges | 132 | 6600 | 3 | 0.999545 | **HOLDS** | 1.0000 | -1.5057 | 0.7837 | [N] |
| 115 | second neighbours | 185 | 9250 | 7 | 0.999243 | **HOLDS** | 1.0000 | -0.7789 | 0.4410 | [N] |
| 115 | loops | 12 | 600 | 1 | 0.998333 | **HOLDS** | 1.0000 | -0.4731 | 0.3800 | [N] |

- Undefined t_x (Neel value equal to the truth): none. The fraction with t_x <= 1 ("between the ground state and the Neel state" when t_x > 0) is 1.0000 at every coupling, for every family and size: no label lies beyond the Neel value.
- Sites: the first-look file also holds a number of this kind for all 50 couplings (F2), printed for 14 (F8: 1.00 everywhere except 0.98 at n = 115, Jz = 1.5). The present values agree with F8: F = 0.9826 at (115, 1.5), 1.0000 at the other 13 printed couplings of each size.
- **The pairs that are not on the Neel side** (list from the independent recomputation; the counts are those of the sealed output):
  - n = 57: 2 pairs, both edges at Jz = 1.9: edge (19, 36), t = -0.0164 (label -0.84424, truth -0.84675); edge (24, 56), t = -0.0074 (label -0.79632, truth -0.79781). Both differences are below 0.05 of the item's own 6 % tolerance.
  - n = 115: 13 pairs, **all at Jz = 1.5** and all around sites 19 and 89 (2 sites, 3 edges, 7 second-neighbour pairs, 1 loop). There the published label is *less* ordered than the truth by 4.4 to 7.4 times the item's own 6 % tolerance: site 19 has <Z> = 0.523 against 0.823. This is a local feature of that one published state, at a coupling that is in neither the training nor the test set.

F per coupling (fraction of the items of the family with t_x > 0). Sites: [S] at Jz = 1.1-2.0, 3.0, 4.0, 5.0, 6.0; everything else [N].

| Jz | sites 57 | edges 57 | 2nd nb. 57 | loops 57 | sites 115 | edges 115 | 2nd nb. 115 | loops 115 |
|---|---|---|---|---|---|---|---|---|
| 1.1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 1.2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 1.3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 1.4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 1.5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.9826 | 0.9773 | 0.9622 | 0.9167 |
| 1.6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 1.7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 1.8 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 1.9 | 1.0000 | 0.9688 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.8 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 2.9 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.8 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 3.9 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.8 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 4.9 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.8 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 5.9 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| 6.0 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## II-3. P4: the error decreases with Jz

Rule: D(n, Jz) = mean over the items of |o_real - o_GS| / (0.06 |o_GS|); **holds iff the Spearman rank correlation of D with Jz is <= -0.9** over the 50 couplings, decided separately for each family and size (eight outcomes). m_s is not one of the four families; it is printed next to them and adds no decision.

| n | family | Spearman(D, Jz) | outcome | largest D (Jz = 1.1) | smallest D | seen before? |
|---|---|---|---|---|---|---|
| 57 | sites | -0.980216 | **HOLDS** | 5.244 | 0.037 | [N] |
| 57 | edges | -0.972629 | **HOLDS** | 2.859 | 0.037 | [N] |
| 57 | second neighbours | -0.975894 | **HOLDS** | 7.954 | 0.065 | [N] |
| 57 | loops | -0.971957 | **HOLDS** | 8.929 | 0.065 | [N] |
| 57 | m_s (no decision) | -0.980216 | (<= -0.9) | 4.954 | 0.037 | [S] (F7) |
| 115 | sites | -0.995486 | **HOLDS** | 4.967 | 0.014 | [N] |
| 115 | edges | -0.992413 | **HOLDS** | 2.866 | 0.011 | [N] |
| 115 | second neighbours | -0.992893 | **HOLDS** | 7.609 | 0.022 | [N] |
| 115 | loops | -0.994334 | **HOLDS** | 8.531 | 0.020 | [N] |
| 115 | m_s (no decision) | -0.995486 | (<= -0.9) | 4.667 | 0.014 | [S] (F7) |

D is not monotonic. Couplings at which D is larger than at the coupling 0.1 below (from the D values of the sealed output; the rule is a rank correlation and tolerates them):

| n | family | number of increases | at Jz = |
|---|---|---|---|
| 57 | sites | 8 | 3.3, 3.7, 3.9, 4.4, 5.1, 5.4, 5.7, 5.9 |
| 57 | edges | 11 | 1.9, 2.1, 2.6, 3.3, 3.7, 3.9, 4.4, 5.1, 5.4, 5.7, 5.9 |
| 57 | second neighbours | 8 | 3.3, 3.7, 3.9, 4.4, 5.1, 5.4, 5.7, 5.9 |
| 57 | loops | 11 | 2.1, 2.8, 3.3, 3.7, 3.9, 4.4, 4.9, 5.1, 5.4, 5.7, 5.9 |
| 57 | m_s | 8 | 3.3, 3.7, 3.9, 4.4, 5.1, 5.4, 5.7, 5.9 |
| 115 | sites | 9 | 2.8, 3.2, 4.6, 4.8, 5.0, 5.2, 5.4, 5.7-5.8 |
| 115 | edges | 13 | 2.1, 2.8, 3.2, 3.7, 4.1-4.2, 4.6, 4.8, 5.0, 5.2, 5.4, 5.7-5.8 |
| 115 | second neighbours | 10 | 2.8, 3.2, 4.1, 4.6, 4.8, 5.0, 5.2, 5.4, 5.7-5.8 |
| 115 | loops | 11 | 2.8, 3.2, 4.1, 4.3, 4.6, 4.8, 5.0, 5.2, 5.4, 5.7-5.8 |
| 115 | m_s | 9 | 2.8, 3.2, 4.6, 4.8, 5.0, 5.2, 5.4, 5.7-5.8 |

How blind each line is: m_s was seen (F7). For the sites, the 50 couplings are ordered by D exactly as by the m_s miss at n = 57 (same order) and at n = 115 (same order), so the rank correlation of the sites repeats a number that was seen: it is a confirmation by a fixed pipeline, not a prediction. Edges, second neighbours and loops had not been compared with their references before the hash.

D per coupling, in units of the item's 6 % tolerance (m_s columns [S], F7; the others [N]).

| Jz | sites 57 | edges 57 | 2nd nb. 57 | loops 57 | m_s 57 [S] | sites 115 | edges 115 | 2nd nb. 115 | loops 115 | m_s 115 [S] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | 5.244 | 2.859 | 7.954 | 8.929 | 4.954 | 4.967 | 2.866 | 7.609 | 8.531 | 4.667 |
| 1.2 | 4.320 | 2.493 | 6.542 | 7.311 | 4.096 | 3.818 | 2.330 | 5.889 | 6.396 | 3.627 |
| 1.3 | 3.620 | 2.265 | 5.579 | 5.798 | 3.455 | 3.080 | 1.996 | 4.809 | 5.047 | 2.947 |
| 1.4 | 2.790 | 1.835 | 4.360 | 4.523 | 2.689 | 2.462 | 1.663 | 3.862 | 4.068 | 2.371 |
| 1.5 | 2.069 | 1.391 | 3.257 | 3.195 | 2.004 | 1.971 | 1.442 | 3.055 | 3.130 | 1.709 |
| 1.6 | 1.718 | 1.181 | 2.703 | 2.679 | 1.668 | 1.588 | 1.118 | 2.491 | 2.541 | 1.543 |
| 1.7 | 1.463 | 1.048 | 2.320 | 2.337 | 1.426 | 1.320 | 0.953 | 2.081 | 2.061 | 1.286 |
| 1.8 | 1.171 | 0.854 | 1.871 | 1.840 | 1.145 | 1.162 | 0.884 | 1.864 | 1.884 | 1.136 |
| 1.9 | 1.110 | 0.860 | 1.804 | 1.747 | 1.087 | 0.932 | 0.699 | 1.475 | 1.480 | 0.912 |
| 2.0 | 0.910 | 0.707 | 1.479 | 1.441 | 0.895 | 0.768 | 0.582 | 1.220 | 1.203 | 0.754 |
| 2.1 | 0.876 | 0.713 | 1.442 | 1.444 | 0.861 | 0.728 | 0.587 | 1.184 | 1.188 | 0.716 |
| 2.2 | 0.758 | 0.628 | 1.257 | 1.238 | 0.746 | 0.543 | 0.414 | 0.858 | 0.844 | 0.534 |
| 2.3 | 0.653 | 0.538 | 1.069 | 0.980 | 0.644 | 0.480 | 0.372 | 0.760 | 0.722 | 0.472 |
| 2.4 | 0.535 | 0.436 | 0.870 | 0.848 | 0.528 | 0.415 | 0.326 | 0.659 | 0.636 | 0.410 |
| 2.5 | 0.415 | 0.348 | 0.695 | 0.658 | 0.410 | 0.348 | 0.269 | 0.548 | 0.537 | 0.344 |
| 2.6 | 0.415 | 0.350 | 0.684 | 0.640 | 0.410 | 0.308 | 0.244 | 0.491 | 0.479 | 0.305 |
| 2.7 | 0.339 | 0.290 | 0.569 | 0.501 | 0.336 | 0.270 | 0.216 | 0.432 | 0.414 | 0.267 |
| 2.8 | 0.334 | 0.284 | 0.550 | 0.511 | 0.330 | 0.283 | 0.238 | 0.459 | 0.418 | 0.280 |
| 2.9 | 0.301 | 0.259 | 0.499 | 0.442 | 0.298 | 0.219 | 0.181 | 0.355 | 0.355 | 0.217 |
| 3.0 | 0.232 | 0.201 | 0.387 | 0.359 | 0.230 | 0.200 | 0.166 | 0.324 | 0.320 | 0.198 |
| 3.1 | 0.215 | 0.188 | 0.360 | 0.336 | 0.213 | 0.160 | 0.128 | 0.255 | 0.244 | 0.159 |
| 3.2 | 0.195 | 0.176 | 0.335 | 0.324 | 0.194 | 0.164 | 0.140 | 0.270 | 0.253 | 0.163 |
| 3.3 | 0.208 | 0.188 | 0.350 | 0.350 | 0.207 | 0.153 | 0.133 | 0.253 | 0.248 | 0.152 |
| 3.4 | 0.181 | 0.161 | 0.302 | 0.291 | 0.180 | 0.118 | 0.097 | 0.189 | 0.183 | 0.117 |
| 3.5 | 0.165 | 0.148 | 0.277 | 0.263 | 0.163 | 0.114 | 0.095 | 0.183 | 0.169 | 0.113 |
| 3.6 | 0.148 | 0.136 | 0.251 | 0.241 | 0.147 | 0.097 | 0.080 | 0.156 | 0.149 | 0.096 |
| 3.7 | 0.176 | 0.161 | 0.294 | 0.260 | 0.175 | 0.095 | 0.081 | 0.154 | 0.140 | 0.094 |
| 3.8 | 0.118 | 0.108 | 0.201 | 0.190 | 0.117 | 0.080 | 0.067 | 0.130 | 0.125 | 0.080 |
| 3.9 | 0.121 | 0.111 | 0.204 | 0.197 | 0.120 | 0.075 | 0.064 | 0.123 | 0.118 | 0.075 |
| 4.0 | 0.110 | 0.103 | 0.187 | 0.178 | 0.110 | 0.064 | 0.053 | 0.103 | 0.098 | 0.064 |
| 4.1 | 0.106 | 0.100 | 0.181 | 0.176 | 0.105 | 0.064 | 0.055 | 0.104 | 0.100 | 0.063 |
| 4.2 | 0.091 | 0.086 | 0.157 | 0.146 | 0.091 | 0.063 | 0.055 | 0.103 | 0.083 | 0.063 |
| 4.3 | 0.067 | 0.060 | 0.112 | 0.100 | 0.067 | 0.057 | 0.051 | 0.095 | 0.087 | 0.057 |
| 4.4 | 0.082 | 0.078 | 0.140 | 0.134 | 0.082 | 0.046 | 0.039 | 0.075 | 0.069 | 0.046 |
| 4.5 | 0.078 | 0.074 | 0.133 | 0.125 | 0.078 | 0.041 | 0.035 | 0.067 | 0.064 | 0.041 |
| 4.6 | 0.076 | 0.073 | 0.130 | 0.123 | 0.076 | 0.041 | 0.036 | 0.069 | 0.067 | 0.041 |
| 4.7 | 0.070 | 0.066 | 0.118 | 0.114 | 0.070 | 0.039 | 0.034 | 0.064 | 0.060 | 0.039 |
| 4.8 | 0.063 | 0.060 | 0.107 | 0.099 | 0.063 | 0.061 | 0.059 | 0.105 | 0.092 | 0.061 |
| 4.9 | 0.059 | 0.057 | 0.101 | 0.100 | 0.059 | 0.031 | 0.026 | 0.050 | 0.048 | 0.031 |
| 5.0 | 0.052 | 0.050 | 0.089 | 0.085 | 0.051 | 0.034 | 0.030 | 0.056 | 0.059 | 0.034 |
| 5.1 | 0.066 | 0.064 | 0.112 | 0.110 | 0.065 | 0.025 | 0.020 | 0.040 | 0.037 | 0.025 |
| 5.2 | 0.055 | 0.053 | 0.094 | 0.090 | 0.055 | 0.031 | 0.029 | 0.053 | 0.054 | 0.031 |
| 5.3 | 0.045 | 0.044 | 0.078 | 0.074 | 0.045 | 0.022 | 0.018 | 0.035 | 0.033 | 0.022 |
| 5.4 | 0.081 | 0.084 | 0.142 | 0.143 | 0.081 | 0.024 | 0.021 | 0.040 | 0.035 | 0.024 |
| 5.5 | 0.045 | 0.044 | 0.077 | 0.076 | 0.045 | 0.019 | 0.016 | 0.031 | 0.028 | 0.019 |
| 5.6 | 0.038 | 0.037 | 0.066 | 0.065 | 0.038 | 0.017 | 0.014 | 0.028 | 0.026 | 0.017 |
| 5.7 | 0.073 | 0.077 | 0.130 | 0.132 | 0.073 | 0.018 | 0.016 | 0.030 | 0.029 | 0.018 |
| 5.8 | 0.039 | 0.039 | 0.068 | 0.066 | 0.039 | 0.026 | 0.025 | 0.045 | 0.044 | 0.026 |
| 5.9 | 0.067 | 0.070 | 0.118 | 0.117 | 0.067 | 0.014 | 0.012 | 0.023 | 0.021 | 0.014 |
| 6.0 | 0.037 | 0.038 | 0.065 | 0.069 | 0.037 | 0.014 | 0.011 | 0.022 | 0.020 | 0.014 |

## II-4. P5: the bias-against-energy curve of Sec. V

Recipe of the n = 19 curve unchanged (`bias_law/code/n19b.py`: exact ground state at n = 19 at the same Jz, top-D truncation, 26 levels, read by linear interpolation in sqrt(de), end values held), computed before the hash at the 50 couplings (`out/n19/n19_curves.json`, no real datum). Delta = m_s(real) - m_s(GS); ratio = Delta / curve(de_real); corrected miss = |m_s(real) - curve(de_real) - m_s(GS)| / tau.

**Rule (one decision): PASS iff the mean corrected miss is at most 0.2 tau at n = 57 and at most 0.6 tau at n = 115, and every ratio lies in [0.75, 1.3] at the couplings where the raw miss is at least 0.2 tau, over the 50 couplings of each size.**

**Outcome: FAIL.**

| part | n = 57 | n = 115 |
|---|---|---|
| mean corrected miss over the 50 couplings [N] | 0.1110 tau (limit 0.2): met | 0.1676 tau (limit 0.6): met |
| deciding couplings (raw miss >= 0.2 tau) [S] | 22: Jz = 1.1-3.1 and 3.3 | 19: Jz = 1.1-2.9 |
| ratios at the deciding couplings [N] | 0.8029 to 1.0455 (median 0.851): **all inside [0.75, 1.3]** | 0.6087 to 0.8122 (median 0.741): **12 of 19 outside, all below 0.75**: Jz = 1.5, 1.6, 1.7, 1.9, 2.0, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.9 |
| couplings read outside the range of the curve | 0 | 0 |
| the part of this size | both conditions met | mean miss met, ratio condition **not met** |

In words: at n = 115 the published labels are biased towards the Neel state by 60 to 82 % of what the first-stage curve gives at their own energy error (median 74 %) wherever the bias matters (raw miss at least 0.2 tau). The curve over-corrects them. At n = 57 the same ratio is 80 to 105 % (median 85 %), inside the declared band.

### II-4.1 Mean and largest misses, with the comparators (units of tau)

| set of couplings | n | label as published (raw) [S] | corrected with the curve [N] | corrected with the chord [N] | truth at n = 19 instead of the label [0] | curve beats chord? |
|---|---|---|---|---|---|---|
| all 50 (decides) | 57 | mean 0.623, max 4.954 | mean 0.111, max 0.866 | mean 0.058, max 0.329 | mean 0.294, max 1.472 | **no** |
| all 50 (decides) | 115 | mean 0.530, max 4.667 | mean 0.168, max 1.098 | mean 0.094, max 0.545 | mean 0.407, max 2.067 | **no** |
| 45 training, Jz >= 1.6 (reported) | 57 | mean 0.310, max 1.668 | mean 0.056, max 0.396 | mean 0.041, max 0.109 | mean 0.194, max 0.809 | **no** |
| 45 training, Jz >= 1.6 (reported) | 115 | mean 0.248, max 1.543 | mean 0.082, max 0.519 | mean 0.084, max 0.196 | mean 0.269, max 1.098 | yes |
| 4 test, Jz = 1.1-1.4 (reported) | 57 | mean 3.799, max 4.954 | mean 0.637, max 0.866 | mean 0.249, max 0.329 | mean 1.264, max 1.472 | **no** |
| 4 test, Jz = 1.1-1.4 (reported) | 115 | mean 3.403, max 4.667 | mean 0.897, max 1.079 | mean 0.089, max 0.143 | mean 1.744, max 2.067 | **no** |

- The correction with the curve lowers the mean miss at both sizes (0.623 to 0.111 tau at n = 57, 0.530 to 0.168 tau at n = 115, 50 couplings). This is what the mean-miss part of the rule measures, and it is met.
- **The parameter-free chord does better than the curve** over the 50 couplings at both sizes (0.058 against 0.111 tau at n = 57; 0.094 against 0.168 tau at n = 115) and over the 45 training couplings at n = 57 (0.041 against 0.056); over the 45 training couplings at n = 115 the two are level (0.084 chord, 0.082 curve).
- At the four test couplings the curve leaves 0.48-0.87 tau (n = 57) and 0.72-1.08 tau (n = 115); the chord leaves 0.11-0.33 and 0.06-0.15 tau.
- The same rule on the 45 training couplings (reported, does not decide): FAIL; mean misses 0.0559 (n = 57) and 0.0820 tau (n = 115), both within the limits; ratios at the deciding couplings 0.8029-1.0455 (n = 57, 17 couplings, none outside) and 0.6962-0.7884 (n = 115, 14 couplings, 11 outside: Jz = 1.6, 1.7, 1.9, 2.0, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.9).

### II-4.2 Every coupling, n = 57

de = (E_real - E0)/n. Columns marked [S] were seen before the hash (de: F2, F4; Delta: m_s of the label and of the truth, F2; raw miss: F7; which couplings decide). Ratio, corrected miss and chord miss are [N]. "D" marks a deciding coupling; **OUT** a deciding ratio outside [0.75, 1.3]; (out) a ratio outside the band at a coupling that does not decide.

| Jz | set | de [S] | Delta [S] | curve(de) | ratio [N] | decides [S] | raw miss/tau [S] | corrected miss/tau [N] | chord miss/tau [N] | n = 19 truth miss/tau [0] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | test | 0.021400 | 0.176947 | 0.207886 | 0.8512 | D | 4.954 | 0.866 | 0.329 | 1.472 |
| 1.2 | test | 0.019759 | 0.157386 | 0.183910 | 0.8558 | D | 4.096 | 0.690 | 0.272 | 1.339 |
| 1.3 | test | 0.018017 | 0.140971 | 0.161745 | 0.8716 | D | 3.455 | 0.509 | 0.281 | 1.194 |
| 1.4 | test | 0.015424 | 0.115277 | 0.136028 | 0.8474 | D | 2.689 | 0.484 | 0.112 | 1.052 |
| 1.5 | apart | 0.012613 | 0.089509 | 0.111030 | 0.8062 | D | 2.004 | 0.482 | 0.058 | 0.923 |
| 1.6 | train | 0.011355 | 0.077108 | 0.095416 | 0.8081 | D | 1.668 | 0.396 | 0.078 | 0.809 |
| 1.7 | train | 0.010245 | 0.067847 | 0.082586 | 0.8215 | D | 1.426 | 0.310 | 0.064 | 0.710 |
| 1.8 | train | 0.008873 | 0.055835 | 0.069539 | 0.8029 | D | 1.145 | 0.281 | 0.109 | 0.625 |
| 1.9 | train | 0.008690 | 0.054112 | 0.064183 | 0.8431 | D | 1.087 | 0.202 | 0.042 | 0.553 |
| 2.0 | train | 0.007507 | 0.045329 | 0.054013 | 0.8392 | D | 0.895 | 0.171 | 0.066 | 0.491 |
| 2.1 | train | 0.007435 | 0.044305 | 0.051102 | 0.8670 | D | 0.861 | 0.132 | 0.018 | 0.438 |
| 2.2 | train | 0.006835 | 0.038914 | 0.045732 | 0.8509 | D | 0.746 | 0.131 | 0.032 | 0.393 |
| 2.3 | train | 0.006285 | 0.033974 | 0.039958 | 0.8502 | D | 0.644 | 0.113 | 0.048 | 0.354 |
| 2.4 | train | 0.005365 | 0.028170 | 0.033715 | 0.8355 | D | 0.528 | 0.104 | 0.067 | 0.320 |
| 2.5 | train | 0.004281 | 0.022095 | 0.026904 | 0.8212 | D | 0.410 | 0.089 | 0.086 | 0.291 |
| 2.6 | train | 0.004347 | 0.022260 | 0.025303 | 0.8797 | D | 0.410 | 0.056 | 0.058 | 0.266 |
| 2.7 | train | 0.003739 | 0.018345 | 0.021495 | 0.8535 | D | 0.336 | 0.058 | 0.072 | 0.243 |
| 2.8 | train | 0.003737 | 0.018169 | 0.019687 | 0.9229 | D | 0.330 | 0.028 | 0.054 | 0.224 |
| 2.9 | train | 0.003474 | 0.016486 | 0.017438 | 0.9454 | D | 0.298 | 0.017 | 0.052 | 0.206 |
| 3.0 | train | 0.002810 | 0.012801 | 0.014413 | 0.8882 | D | 0.230 | 0.029 | 0.067 | 0.191 |
| 3.1 | train | 0.002709 | 0.011934 | 0.013047 | 0.9147 | D | 0.213 | 0.020 | 0.063 | 0.177 |
| 3.2 | train | 0.002533 | 0.010882 | 0.011649 | 0.9341 | - | 0.194 | 0.014 | 0.060 | 0.165 |
| 3.3 | train | 0.002700 | 0.011672 | 0.011164 | 1.0455 | D | 0.207 | 0.009 | 0.043 | 0.153 |
| 3.4 | train | 0.002470 | 0.010178 | 0.009890 | 1.0291 | - | 0.180 | 0.005 | 0.048 | 0.143 |
| 3.5 | train | 0.002208 | 0.009281 | 0.008665 | 1.0710 | - | 0.163 | 0.011 | 0.042 | 0.134 |
| 3.6 | train | 0.002123 | 0.008399 | 0.007999 | 1.0499 | - | 0.147 | 0.007 | 0.045 | 0.126 |
| 3.7 | train | 0.002576 | 0.009966 | 0.008455 | 1.1787 | - | 0.175 | 0.026 | 0.028 | 0.119 |
| 3.8 | train | 0.001749 | 0.006719 | 0.006280 | 1.0698 | - | 0.117 | 0.008 | 0.043 | 0.112 |
| 3.9 | train | 0.001854 | 0.006898 | 0.006092 | 1.1322 | - | 0.120 | 0.014 | 0.038 | 0.106 |
| 4.0 | train | 0.001717 | 0.006305 | 0.005482 | 1.1502 | - | 0.110 | 0.014 | 0.037 | 0.100 |
| 4.1 | train | 0.001705 | 0.006075 | 0.005184 | 1.1718 | - | 0.105 | 0.015 | 0.035 | 0.095 |
| 4.2 | train | 0.001467 | 0.005240 | 0.004436 | 1.1813 | - | 0.091 | 0.014 | 0.034 | 0.090 |
| 4.3 | train | 0.001122 | 0.003857 | 0.003573 | 1.0797 | - | 0.067 | 0.005 | 0.039 | 0.085 |
| 4.4 | train | 0.001382 | 0.004729 | 0.003872 | 1.2212 | - | 0.082 | 0.015 | 0.031 | 0.081 |
| 4.5 | train | 0.001352 | 0.004525 | 0.003646 | 1.2411 | - | 0.078 | 0.015 | 0.030 | 0.077 |
| 4.6 | train | 0.001345 | 0.004391 | 0.003481 | 1.2613 | - | 0.076 | 0.016 | 0.028 | 0.074 |
| 4.7 | train | 0.001264 | 0.004064 | 0.003193 | 1.2729 | - | 0.070 | 0.015 | 0.028 | 0.070 |
| 4.8 | train | 0.001145 | 0.003672 | 0.002849 | 1.2889 | - | 0.063 | 0.014 | 0.027 | 0.067 |
| 4.9 | train | 0.001102 | 0.003458 | 0.002662 | 1.2991 | - | 0.059 | 0.014 | 0.026 | 0.064 |
| 5.0 | train | 0.001006 | 0.003007 | 0.002391 | 1.2580 | - | 0.051 | 0.011 | 0.027 | 0.062 |
| 5.1 | train | 0.001293 | 0.003818 | 0.002784 | 1.3717 (out) | - | 0.065 | 0.018 | 0.021 | 0.059 |
| 5.2 | train | 0.001101 | 0.003218 | 0.002385 | 1.3492 (out) | - | 0.055 | 0.014 | 0.023 | 0.057 |
| 5.3 | train | 0.000913 | 0.002641 | 0.001996 | 1.3233 (out) | - | 0.045 | 0.011 | 0.024 | 0.054 |
| 5.4 | train | 0.001942 | 0.004724 | 0.003498 | 1.3506 (out) | - | 0.081 | 0.021 | 0.017 | 0.052 |
| 5.5 | train | 0.000939 | 0.002616 | 0.001910 | 1.3697 (out) | - | 0.045 | 0.012 | 0.021 | 0.050 |
| 5.6 | train | 0.000821 | 0.002204 | 0.001666 | 1.3227 (out) | - | 0.038 | 0.009 | 0.022 | 0.048 |
| 5.7 | train | 0.001987 | 0.004304 | 0.003404 | 1.2641 | - | 0.073 | 0.015 | 0.017 | 0.047 |
| 5.8 | train | 0.000870 | 0.002311 | 0.001638 | 1.4111 (out) | - | 0.039 | 0.011 | 0.019 | 0.045 |
| 5.9 | train | 0.001857 | 0.003921 | 0.003088 | 1.2697 | - | 0.067 | 0.014 | 0.016 | 0.043 |
| 6.0 | train | 0.000878 | 0.002201 | 0.001552 | 1.4178 (out) | - | 0.037 | 0.011 | 0.018 | 0.042 |

### II-4.3 Every coupling, n = 115

de = (E_real - E0)/n. Columns marked [S] were seen before the hash (de: F2, F4; Delta: m_s of the label and of the truth, F2; raw miss: F7; which couplings decide). Ratio, corrected miss and chord miss are [N]. "D" marks a deciding coupling; **OUT** a deciding ratio outside [0.75, 1.3]; (out) a ratio outside the band at a coupling that does not decide.

| Jz | set | de [S] | Delta [S] | curve(de) | ratio [N] | decides [S] | raw miss/tau [S] | corrected miss/tau [N] | chord miss/tau [N] | n = 19 truth miss/tau [0] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | test | 0.022729 | 0.173475 | 0.213582 | 0.8122 | D | 4.667 | 1.079 | 0.087 | 2.067 |
| 1.2 | test | 0.019683 | 0.144128 | 0.183465 | 0.7856 | D | 3.627 | 0.990 | 0.063 | 1.847 |
| 1.3 | test | 0.017174 | 0.123723 | 0.157119 | 0.7874 | D | 2.947 | 0.796 | 0.064 | 1.630 |
| 1.4 | test | 0.015418 | 0.104165 | 0.135994 | 0.7660 | D | 2.371 | 0.725 | 0.143 | 1.431 |
| 1.5 | apart | 0.015706 | 0.077944 | 0.128045 | **0.6087 OUT** | D | 1.709 | 1.098 | 0.545 | 1.253 |
| 1.6 | train | 0.011680 | 0.072618 | 0.097039 | **0.7483 OUT** | D | 1.543 | 0.519 | 0.196 | 1.098 |
| 1.7 | train | 0.010396 | 0.062191 | 0.083468 | **0.7451 OUT** | D | 1.286 | 0.440 | 0.191 | 0.966 |
| 1.8 | train | 0.009622 | 0.056173 | 0.073863 | 0.7605 | D | 1.136 | 0.358 | 0.152 | 0.853 |
| 1.9 | train | 0.008303 | 0.045977 | 0.062040 | **0.7411 OUT** | D | 0.912 | 0.319 | 0.178 | 0.756 |
| 2.0 | train | 0.007292 | 0.038642 | 0.052844 | **0.7313 OUT** | D | 0.754 | 0.277 | 0.182 | 0.674 |
| 2.1 | train | 0.007072 | 0.037220 | 0.048999 | 0.7596 | D | 0.716 | 0.227 | 0.133 | 0.603 |
| 2.2 | train | 0.005725 | 0.028116 | 0.039067 | **0.7197 OUT** | D | 0.534 | 0.208 | 0.172 | 0.543 |
| 2.3 | train | 0.005266 | 0.025147 | 0.034888 | **0.7208 OUT** | D | 0.472 | 0.183 | 0.156 | 0.490 |
| 2.4 | train | 0.004750 | 0.022012 | 0.030633 | **0.7186 OUT** | D | 0.410 | 0.160 | 0.146 | 0.445 |
| 2.5 | train | 0.004254 | 0.018621 | 0.026746 | **0.6962 OUT** | D | 0.344 | 0.150 | 0.148 | 0.405 |
| 2.6 | train | 0.003876 | 0.016634 | 0.023749 | **0.7004 OUT** | D | 0.305 | 0.130 | 0.135 | 0.371 |
| 2.7 | train | 0.003539 | 0.014710 | 0.020925 | **0.7030 OUT** | D | 0.267 | 0.113 | 0.127 | 0.340 |
| 2.8 | train | 0.003722 | 0.015491 | 0.019648 | 0.7884 | D | 0.280 | 0.075 | 0.101 | 0.314 |
| 2.9 | train | 0.003099 | 0.012070 | 0.016463 | **0.7331 OUT** | D | 0.217 | 0.079 | 0.111 | 0.290 |
| 3.0 | train | 0.002940 | 0.011060 | 0.014751 | 0.7498 (out) | - | 0.198 | 0.066 | 0.105 | 0.268 |
| 3.1 | train | 0.002404 | 0.008935 | 0.012264 | 0.7286 (out) | - | 0.159 | 0.059 | 0.100 | 0.249 |
| 3.2 | train | 0.002581 | 0.009170 | 0.011763 | 0.7795 | - | 0.163 | 0.046 | 0.093 | 0.232 |
| 3.3 | train | 0.002480 | 0.008620 | 0.010673 | 0.8077 | - | 0.152 | 0.036 | 0.086 | 0.217 |
| 3.4 | train | 0.001946 | 0.006662 | 0.008706 | 0.7653 | - | 0.117 | 0.036 | 0.084 | 0.203 |
| 3.5 | train | 0.001944 | 0.006442 | 0.008091 | 0.7962 | - | 0.113 | 0.029 | 0.079 | 0.191 |
| 3.6 | train | 0.001694 | 0.005483 | 0.007050 | 0.7777 | - | 0.096 | 0.027 | 0.075 | 0.179 |
| 3.7 | train | 0.001725 | 0.005385 | 0.006658 | 0.8088 | - | 0.094 | 0.022 | 0.072 | 0.169 |
| 3.8 | train | 0.001502 | 0.004585 | 0.005763 | 0.7956 | - | 0.080 | 0.021 | 0.068 | 0.159 |
| 3.9 | train | 0.001446 | 0.004302 | 0.005286 | 0.8139 | - | 0.075 | 0.017 | 0.065 | 0.150 |
| 4.0 | train | 0.001248 | 0.003684 | 0.004561 | 0.8079 | - | 0.064 | 0.015 | 0.061 | 0.142 |
| 4.1 | train | 0.001303 | 0.003658 | 0.004392 | 0.8328 | - | 0.063 | 0.013 | 0.059 | 0.135 |
| 4.2 | train | 0.001317 | 0.003648 | 0.004158 | 0.8774 | - | 0.063 | 0.009 | 0.055 | 0.128 |
| 4.3 | train | 0.001247 | 0.003314 | 0.003797 | 0.8729 | - | 0.057 | 0.008 | 0.054 | 0.122 |
| 4.4 | train | 0.001005 | 0.002687 | 0.003162 | 0.8499 | - | 0.046 | 0.008 | 0.050 | 0.116 |
| 4.5 | train | 0.000911 | 0.002390 | 0.002821 | 0.8473 | - | 0.041 | 0.007 | 0.047 | 0.111 |
| 4.6 | train | 0.000972 | 0.002408 | 0.002768 | 0.8699 | - | 0.041 | 0.006 | 0.047 | 0.105 |
| 4.7 | train | 0.000921 | 0.002288 | 0.002539 | 0.9012 | - | 0.039 | 0.004 | 0.044 | 0.101 |
| 4.8 | train | 0.001418 | 0.003562 | 0.003337 | 1.0674 | - | 0.061 | 0.004 | 0.039 | 0.096 |
| 4.9 | train | 0.000741 | 0.001806 | 0.002009 | 0.8988 | - | 0.031 | 0.003 | 0.039 | 0.092 |
| 5.0 | train | 0.000857 | 0.001962 | 0.002104 | 0.9325 | - | 0.034 | 0.002 | 0.039 | 0.088 |
| 5.1 | train | 0.000609 | 0.001443 | 0.001614 | 0.8938 | - | 0.025 | 0.003 | 0.035 | 0.085 |
| 5.2 | train | 0.000842 | 0.001834 | 0.001935 | 0.9477 | - | 0.031 | 0.002 | 0.037 | 0.081 |
| 5.3 | train | 0.000561 | 0.001274 | 0.001392 | 0.9156 | - | 0.022 | 0.002 | 0.032 | 0.078 |
| 5.4 | train | 0.000656 | 0.001418 | 0.001473 | 0.9630 | - | 0.024 | 0.001 | 0.032 | 0.075 |
| 5.5 | train | 0.000511 | 0.001119 | 0.001197 | 0.9346 | - | 0.019 | 0.001 | 0.029 | 0.072 |
| 5.6 | train | 0.000470 | 0.001016 | 0.001087 | 0.9349 | - | 0.017 | 0.001 | 0.028 | 0.070 |
| 5.7 | train | 0.000522 | 0.001065 | 0.001103 | 0.9656 | - | 0.018 | 0.001 | 0.028 | 0.067 |
| 5.8 | train | 0.000787 | 0.001556 | 0.001516 | 1.0264 | - | 0.026 | 0.001 | 0.029 | 0.065 |
| 5.9 | train | 0.000409 | 0.000841 | 0.000874 | 0.9629 | - | 0.014 | 0.001 | 0.025 | 0.062 |
| 6.0 | train | 0.000398 | 0.000802 | 0.000823 | 0.9748 | - | 0.014 | 0.000 | 0.024 | 0.060 |

Ratios at couplings that do not decide (reported): at n = 57 the ratio rises with Jz and is above 1.3 at 8 couplings (Jz = 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.8, 6.0), where the raw miss is at most 0.081 tau; over all 50 couplings it runs from 0.802 to 1.418. At n = 115 it is below 0.75 at 2 further couplings that do not decide (Jz = 3.0, 3.1); over all 50 it runs from 0.608 to 1.068.

## II-5. The small classical calculation next to every label (Sec. 6; descriptive, no rule)

|m_s(exact, n = 19) - m_s^GS(n)| in units of tau = 0.06 |m_s^GS(n)|, at all 50 couplings and both sizes [0], next to the miss of the published label [S] (F7). "kept" = the training coupling is in the set S fixed by the map task (m_s row CERTIFIED (exact), reference tolerance, stored certificates; `out/S_sets.json`).

| Jz | n = 57: n = 19 exact [0] | n = 57: published label [S] | n = 57 kept | n = 115: n = 19 exact [0] | n = 115: published label [S] | n = 115 kept |
|---|---|---|---|---|---|---|
| 1.1 | 1.472 | 4.954 |  | 2.067 | 4.667 |  |
| 1.2 | 1.339 | 4.096 |  | 1.847 | 3.627 |  |
| 1.3 | 1.194 | 3.455 |  | 1.630 | 2.947 |  |
| 1.4 | 1.052 | 2.689 |  | 1.431 | 2.371 |  |
| 1.5 | 0.923 | 2.004 |  | 1.253 | 1.709 |  |
| 1.6 | 0.809 | 1.668 |  | 1.098 | 1.543 |  |
| 1.7 | 0.710 | 1.426 |  | 0.966 | 1.286 |  |
| 1.8 | 0.625 | 1.145 |  | 0.853 | 1.136 |  |
| 1.9 | 0.553 | 1.087 |  | 0.756 | 0.912 |  |
| 2.0 | 0.491 | 0.895 |  | 0.674 | 0.754 |  |
| 2.1 | 0.438 | 0.861 |  | 0.603 | 0.716 |  |
| 2.2 | 0.393 | 0.746 |  | 0.543 | 0.534 |  |
| 2.3 | 0.354 | 0.644 |  | 0.490 | 0.472 |  |
| 2.4 | 0.320 | 0.528 |  | 0.445 | 0.410 |  |
| 2.5 | 0.291 | 0.410 |  | 0.405 | 0.344 |  |
| 2.6 | 0.266 | 0.410 |  | 0.371 | 0.305 |  |
| 2.7 | 0.243 | 0.336 |  | 0.340 | 0.267 |  |
| 2.8 | 0.224 | 0.330 |  | 0.314 | 0.280 |  |
| 2.9 | 0.206 | 0.298 |  | 0.290 | 0.217 |  |
| 3.0 | 0.191 | 0.230 |  | 0.268 | 0.198 |  |
| 3.1 | 0.177 | 0.213 |  | 0.249 | 0.159 |  |
| 3.2 | 0.165 | 0.194 |  | 0.232 | 0.163 |  |
| 3.3 | 0.153 | 0.207 |  | 0.217 | 0.152 |  |
| 3.4 | 0.143 | 0.180 |  | 0.203 | 0.117 |  |
| 3.5 | 0.134 | 0.163 | kept | 0.191 | 0.113 |  |
| 3.6 | 0.126 | 0.147 | kept | 0.179 | 0.096 |  |
| 3.7 | 0.119 | 0.175 | kept | 0.169 | 0.094 |  |
| 3.8 | 0.112 | 0.117 | kept | 0.159 | 0.080 |  |
| 3.9 | 0.106 | 0.120 | kept | 0.150 | 0.075 |  |
| 4.0 | 0.100 | 0.110 | kept | 0.142 | 0.064 | kept |
| 4.1 | 0.095 | 0.105 | kept | 0.135 | 0.063 | kept |
| 4.2 | 0.090 | 0.091 | kept | 0.128 | 0.063 | kept |
| 4.3 | 0.085 | 0.067 | kept | 0.122 | 0.057 | kept |
| 4.4 | 0.081 | 0.082 | kept | 0.116 | 0.046 | kept |
| 4.5 | 0.077 | 0.078 | kept | 0.111 | 0.041 | kept |
| 4.6 | 0.074 | 0.076 | kept | 0.105 | 0.041 | kept |
| 4.7 | 0.070 | 0.070 | kept | 0.101 | 0.039 | kept |
| 4.8 | 0.067 | 0.063 | kept | 0.096 | 0.061 | kept |
| 4.9 | 0.064 | 0.059 | kept | 0.092 | 0.031 | kept |
| 5.0 | 0.062 | 0.051 | kept | 0.088 | 0.034 | kept |
| 5.1 | 0.059 | 0.065 | kept | 0.085 | 0.025 | kept |
| 5.2 | 0.057 | 0.055 | kept | 0.081 | 0.031 | kept |
| 5.3 | 0.054 | 0.045 | kept | 0.078 | 0.022 | kept |
| 5.4 | 0.052 | 0.081 | kept | 0.075 | 0.024 | kept |
| 5.5 | 0.050 | 0.045 | kept | 0.072 | 0.019 | kept |
| 5.6 | 0.048 | 0.038 | kept | 0.070 | 0.017 | kept |
| 5.7 | 0.047 | 0.073 | kept | 0.067 | 0.018 | kept |
| 5.8 | 0.045 | 0.039 | kept | 0.065 | 0.026 | kept |
| 5.9 | 0.043 | 0.067 | kept | 0.062 | 0.014 | kept |
| 6.0 | 0.042 | 0.037 | kept | 0.060 | 0.014 | kept |

- **Test couplings (Jz = 1.1, 1.2, 1.3, 1.4):** 1.472, 1.339, 1.194, 1.052 tau (n = 57) and 2.067, 1.847, 1.630, 1.431 tau (n = 115). These are the values already printed in the paper (1.05-1.47 and 1.43-2.07 tau).
- **Largest value over all 50 couplings:** 1.472 tau (n = 57) and 2.067 tau (n = 115), both at Jz = 1.1. The exact n = 19 value is within a fifth of tau of the truth from Jz = 3.0 on (n = 57) and from Jz = 3.5 on (n = 115).
- **Largest value over the kept labels:** 0.1344 tau at n = 57 (26 labels, Jz = 3.5-6.0) and 0.1424 tau at n = 115 (21 labels, Jz = 4.0-6.0). **The paper's sentence ("a range in which an exact 19-site calculation already lies within a fifth of the tolerance") is true on the kept set at both sizes** (sealed output: True, True).
- **Against the label itself.** At n = 57 the exact n = 19 value is closer to the truth than the published label at 39 of the 50 couplings (34 of the 45 training couplings), including 15 of the 26 kept labels (Jz = 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2, 4.4, 4.5, 4.6, 5.1, 5.4, 5.7, 5.9); over the kept labels the mean distances are 0.075 tau (n = 19) and 0.082 tau (label). At n = 115 it is closer at 11 of 50 (Jz = 1.1-2.1 only) and at none of the 21 kept labels (mean 0.093 against 0.036 tau).
- Said in advance in the declaration (Sec. 6): where the labels are already accurate the filter buys a guarantee, not accuracy.
- If extension E1 adds certificates below the stored range (reported by its own task): the n = 19 distance is 0.203 tau at Jz = 3.4 and 0.217 tau at 3.3 for n = 115 (above a fifth), and at most 0.165 tau for n = 57 down to Jz = 3.2.

## II-6. Secondary: the comparison variant (`skqd_post_select`, n = 115, 46 couplings; Jz = 5.6, 5.7, 5.9, 6.0 excluded by gate G2)

Same code, same rules, no decision attached (secondary everywhere). All [N].

- Sign: F = 1.0000, 1.0000, 1.0000, 1.0000 (sites, edges, second neighbours, loops), all pairs positive; fraction with t <= 1: 1.0000.
- Rank correlation of D with Jz: -0.9964, -0.9928, -0.9964, -0.9947.
- Curve: mean corrected miss 0.179 tau (raw 0.567, chord 0.098, truth at n = 19 0.437); ratios at the 19 deciding couplings 0.697-0.802, **outside [0.75, 1.3] at 14 of them** (Jz = 1.5-2.7, 2.9). The variant shows the same shortfall as the dataset at n = 115.

## II-7. Gates and checks behind these numbers

- **G1 (data): NOT COMPLETE.** Hashes of `converted/real_n57.json`, `real_n115.json`, `lattice_maps.json` equal the pinned ones; the declared re-run of the converter on the pinned archive was not done (not by this task; the map task records `rerun: null`).
- **G2 (same state), re-checked here with own code:** the exchange part of the energy lies inside the bound at all 100 points: 0.932-0.989 of the bound (n = 57) and 0.952-0.997 (n = 115) [S] (T3).
- **G3 (energies):** E_real - E0(authors) >= 0.0468 (n = 57) and 0.0458 (n = 115) [S] (T4). **G4 (truth):** authors' DMRG against this project's references at the stored couplings: m_s within 5.3e-05 tau and 5.2e-05 tau, the seven label types within 1.5e-04 and 2.8e-04 tau (limit 1e-3), E0 within 1.9e-06 and 3.0e-05 (limit 1e-4) [S] (T5).
- **Independent recomputation** (`checks/rd_predict_independent.py`, written after the hash, no function shared with the sealed code; lattice from the repository's edge list, second neighbours derived, Neel values computed as products of eta, `scipy.stats.spearmanr`, own interpolation): the largest absolute difference from the sealed output over 84 compared quantities (F, F per coupling, t range, D, rank correlations, every column of the P5 rows, the means) is **2.2e-16**; the same couplings decide, the same ratios are outside, the same outcomes.
- **n = 19 from scratch** (own exact diagonalization, sector dimension 75582, the same 26 levels): against `out/n19/n19_curves.json` at the 50 couplings |dE0| <= 5e-14, |dm_s| <= 2e-11, curve points within 4e-15 (energy) and 8e-09 (bias); residual of the ground state at most 3e-11. Reading the curve from this recomputation changes no ratio by more than 3e-09.
- **Same recipe as the paper's curves:** `out/n19/n19_curves.json` against `bias_law/inputs/n19_curves.json` at the 14 couplings they share: |dE0| <= 3e-14, |dm_s| <= 3e-11, curve within 1e-08 (the tolerances of the earlier gate were 1e-8, 1e-6, 1e-5).

## II-8. Post hoc (not declared; no rule; nothing here changes an outcome)

- **The outcome of P5 does not depend on the choice of truth or on the curve file.** With the authors' DMRG as truth at every coupling (instead of this project's references where stored): FAIL, the same 12 couplings outside at n = 115, ratios 0.6087-0.8122; n = 57 ratios 0.8029-1.0455. With the curve recomputed from scratch: FAIL, identical.
- **Not a borderline failure.** Three of the twelve outside ratios at n = 115 are within 0.01 of the band (Jz = 1.6: 0.7483; 1.7: 0.7451; 1.9: 0.7411); the other nine are 0.734 or lower, down to 0.6087 at Jz = 1.5.
- **The point n = 115, Jz = 1.5** has the lowest ratio, a larger energy error per site than its neighbour at 1.4 (0.0157 against 0.0154) and all 13 pairs of Sec. 2 that are not on the Neel side: the published state has a local region (around sites 19 and 89) that is less ordered than the ground state. Without this coupling the ratio condition still fails at n = 115 (11 other couplings outside).
- **Ratio of the bias to the chord** (the rule does not apply to the chord): at the deciding couplings 0.771-1.089 at n = 57 (0 outside [0.75, 1.3]) and 0.660-1.020 at n = 115 (6 outside: Jz = 2.4, 2.5, 2.6, 2.7, 2.8, 2.9). The chord has smaller mean misses than the curve, but it would not meet the ratio condition at n = 115 either.
- **Coupling by coupling,** the curve leaves a smaller miss than the chord at 34 of 50 couplings at n = 57 (Jz = 2.6-5.3, 5.5-6.0) and at 35 of 50 at n = 115 (Jz = 2.6-6.0); the chord leaves the smaller miss at the other 16 and 15 (Jz = 1.1-2.5, 5.4; Jz = 1.1-2.5). The chord wins in the mean because it is the better of the two at small Jz, where the misses are large. The correction with the curve makes no label worse than it was (couplings with corrected miss above raw miss: 0 at n = 57, 0 at n = 115).
- **How much the basis optimization lowers the energy error** (E_first against E_real, both in the public files; [S] in part: F10, T4): the error per site before the optimization is 2.8 to 8.9 times the final one at n = 57 (median 6.7) and 6.6 to 175.4 times at n = 115 (median 29.6); at the deciding couplings 4.0-7.7 and 6.6-24.1. The declaration's phrase "five- to tenfold" describes n = 57; at n = 115 the factor is above ten at 45 of the 50 couplings. The final optimization does far more of the work at n = 115, which is where the first-stage curve fails. This is an observation; no test of it was declared or made.

## II-9. Re-executed, only compared, not checked

**Re-executed by this task:** the hash check of the declaration; `checks/make_manifest.py --check`; the sealed `code/run_predict.py` (twice); an independent recomputation of P1-P5 and of the n = 19 comparison from the plain JSON; the exact diagonalization at n = 19 at the 50 couplings, from scratch; gates G2, G3, G4 for the dataset.

**Only read or compared:** the kept sets of `out/S_sets.json` (fixed by the map task; read through the sealed loader, which checks the file against `out/S_sets.sha256` and the declaration hash; not re-derived here); the gate records of the map task (`out/map_gates.json`, `out/run_map_stdout.txt`); the numbers of declaration Sec. 1 (F4, F7, F8, T3-T5) against the present output, which agree at every value compared (de at Jz = 1.1-1.5; raw misses 4.95 and 4.67 tau at Jz = 1.1; above tau up to Jz = 1.9 and 1.8, above tau/2 up to 2.4 and 2.2; site fraction 0.98 at (115, 1.5)).

**Not checked:** gate G1 in full (no re-run of the converter); the unit tests of G8 were not re-run (their records are `checks/G8_*`; the tested files are byte-identical to those run, by the manifest); that the published energy and the published labels belong to one and the same state (declaration Sec. 10, point 6: supported by G2 and by the reading of the authors' code, not provable from the files); the authors' DMRG itself, which is the truth for every single site, pair and loop (no new DMRG was run).

## II-10. Files

| file | what |
|---|---|
| `out/predict/predict_results.json` | output of the sealed code, run 2 (with the kept set) |
| `out/predict/run_predict_stdout.txt` | its printed summary |
| `out/predict/first_run_before_S_sets/` | run 1 (before the kept set existed) |
| `out/predict_real.json` | sealed output verbatim + provenance + independent check + post hoc lines |
| `checks/rd_predict_independent.py`, `.json`, `_stdout.txt` | independent recomputation (written after the hash; decides nothing) |
| `checks/rd_predict_make_results.py` | writes this file and `out/predict_real.json` from the two JSON files above |
| `results/SHA256SUMS_predict.txt` | SHA-256 of the files of this task |
| `DEVIATIONS.md` | dated notes of this task (no code defect; two runs; file names) |

# Part III. The learning tests on the real labels

Verbatim from `results/RESULTS_learn.md` (SHA-256 `6ac425aa2f4ac2f6586e85f52339a050ed377126bebd8cee05da64f8a1e3ce9b`), without its Spanish summary. Original title: "Real data of arXiv:2606.15983: RESULTS of the learning tests on the real labels (declaration Sec. 7: f1, f2, f3)".

Task `rd-learn`, 2026-11-12. Declaration: `real_data/DECLARATION.md`, SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa` (checked before anything was read).
Every outcome below is the output of the sealed code `code/run_learn.py` (and its sealed helpers), run unchanged. No rule was changed.
Nested sets and label intervals: `out/S_sets.json`, SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4` (written by the map task before any learning number; equal to `out/S_sets.sha256`).

## III-Summary (English)

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

## III-1. What was run

- `DECLARATION.sha256` equals the SHA-256 of `DECLARATION.md` (`sha256sum`, the gate of the sealed code, and this script). `python -B -I checks/make_manifest.py --check` before the runs: 69 lines of Sec. 11 equal to the files on disk, 0 different, 4 not re-hashed there. Hashed again by this script after the runs: 64 plain-file lines of Sec. 11 equal, 0 different (the archive under `source/` was not re-hashed; tree digests not recomputed here).
- `out/S_sets.json` existed with SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4`, equal to `out/S_sets.sha256` and to the value announced by the map task, before any learning number was computed; the sealed stages `prop2`, `f2`, `f3` refuse to run otherwise.
- Command 1: `python -B -I code/run_learn.py --hash=6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa --stage=cheap` (stages f1_cheap, prop2, f2, f3, rules), 2026-11-12T19:55:38Z to 2026-11-12T19:56:28Z UTC. Seed 1845216616 (first eight hex digits of the hash).
- Command 2: `python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=... --model=mlp_pilot3 --size=57 --part=ood` (the perceptron, test range, real and DMRG labels; 92 fits), 2026-11-12T19:55:35Z to 2026-11-12T20:25:33Z UTC (19.5 s per fit on the shared laptop).
- Python 3.11.4, numpy 1.26.4, scipy 1.13.1 (as at gate G8), one thread per process, laptop only.
- Sealed code, hashed again after the runs and equal to Sec. 11: `code/run_learn.py` `8332d1f06289...`, `code/rd_f23.py` `3512c2206936...`, `code/rd_learn_ibm.py` `9c65738a9d8f...`, `code/rd_prop2_cubic.py` `694adaf0451e...`, `code/rd_learn_parts.py` `83e2d7fb54f5...`, `code/rd_common.py` `6efde0302f75...`.
- Outputs of the sealed code (`out/learn/`): `results_cheap.json`, `prop2_cubic.json`, `f2_floor.json`, `f3_constructive.json`, `f1_rules.json`, `parts/f1_mlp_pilot3_n57_ood.json`; copied verbatim into `out/learn_real.json` with provenance, the independent check and the post hoc lines under separate keys. SHA-256 of every file: `results/SHA256SUMS_learn.txt`.
- Truth in this section of the declaration: the authors' DMRG at all couplings (truth and tau(x) in L1-L3, (f2), (W), (C)); membership of S, S_3/4, S_1/2 uses the tau of Sec. 0 (Sec. 12, line 1).
- No code defect was found. Nothing listed in Sec. 11 was changed. Dated notes of this task: `DEVIATIONS.md`.

## III-2. Inputs fixed before any learning number [M]

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

## III-3. (f1) The realistic test: standard conformal prediction on the real labels

Standard conformal, alpha = 0.1, plain jackknife over couplings. Test range: trained and calibrated on the 45 training labels, queried at Jz = 1.1-1.4. In distribution: each training coupling held out in turn (44 labels). m_s is derived from the per-site model. "New real labels" are the held-out real labels (test range: the real labels at 1.1-1.4). Width = 2q / tau(x). Control: the same pipeline trained and calibrated on the authors' DMRG labels.

### III-3.1 Every model

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

### III-3.2 The cubic, coupling by coupling, with Proposition 2(a) and (b) at the real intervals

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

### III-3.3 Proposition 2 for the cubic: summary

- n = 57. 2(a), lower version: W_lo = 34.18-185.25 tau at the test couplings and 0.48-15.49 tau at the held-out training couplings; band (a) is NOT_PINNED at 40 of 49 queries, UNDECIDED at 9 (Jz = 4.7-5.5: W_lo below tau, upper version not available), PINNED at 0. 2(b), lower version: 2q_lo = 9.22-11.08 tau at the test couplings, 6.71-7.82 tau held out; these intervals contain the truth at 4 of 4 test and 45 of 45 training queries. Rule (c) answers 0 of 49 queries (definite abstention at 49: 2q_lo > tau). Upper kinds over the 45 training labels: exact 27, like-for-like 7, interpolated 11. Check of the stored script: every label and every truth lies in its upper interval (True, True); linearity check 1.3e-13.
- n = 115. 2(a), lower version: W_lo = 29.87-158.00 tau at the test couplings and 0.37-13.71 tau at the held-out training couplings; band (a) is NOT_PINNED at 37 of 49 queries, UNDECIDED at 12 (Jz = 4.5-5.6: W_lo below tau, upper version not available), PINNED at 0. 2(b), lower version: 2q_lo = 7.95-9.40 tau at the test couplings, 5.92-6.83 tau held out; these intervals contain the truth at 3 of 4 test and 45 of 45 training queries. Rule (c) answers 0 of 49 queries (definite abstention at 49: 2q_lo > tau). Upper kinds over the 45 training labels: exact 21, like-for-like 7, interpolated 17. Check of the stored script: every label and every truth lies in its upper interval (True, True); linearity check 7.2e-14.
- n = 57: queries at which the 2(b) lower-version interval does not contain the truth: none.
- n = 115: queries at which the 2(b) lower-version interval does not contain the truth: Jz = 1.1 (miss 5.06 tau against a half-width of 4.70 tau).
- The lower version is a lower bound on the width that a valid interval of this construction must have. It is not itself a guaranteed interval, and no conformal guarantee applies outside the training range.

### III-3.4 Outcomes of L1, L2, L3 (each holds iff true at n = 57; n = 115 reported)

| | n = 57 (decides) | n = 115 (reported) |
|---|---|---|
| **L1** the cubic misses the true m_s by more than tau at each of 1.1-1.4 | **HOLDS**: 3.72, 3.17, 2.69, 2.29 tau | HOLDS: 5.06, 3.85, 2.99, 2.38 tau |
| **L2** standard intervals calibrated on the real labels cover the truth at none of the four test couplings | **HOLDS**: covered at 0 of 4 (sites: 0.018, 0.000, 0.000, 0.000) | HOLDS: covered at 0 of 4 (sites: 0.000, 0.000, 0.000, 0.000) |
| **L3** 2(b) intervals calibrated on all 45 labels wider than tau at every coupling (lower version) | **HOLDS**: one value of q_lo = 0.19773; 2q_lo = 6.71-11.08 tau over the 45 training and 4 test couplings (held out, 44 labels: 6.71-7.82 tau) | HOLDS: q_lo = 0.17461; 5.92-9.40 tau (held out: 5.92-6.83 tau) |

L1 and L2 were predictions of the emulation-based test; the miss of the real m_s label itself at 1.1-1.4 had been seen [S, F7], the cubic's miss had not. L3 carries the mark of gate G6 (first part NOT COMPLETE).

### III-3.5 Blocks that the derived script inherits from the stored one

- n = 57. Per-site split conformal over all choices of 3 calibration couplings (14190 choices), test range: sites covered, labels / truth: cubic 0.073 / 0.004, null 0.070 / 0.000. **Like-for-like block, not a property of the real labels** (the stored in-sector thresholds at E_real, at the couplings of the stored map only; seen before the hash, F6 and F9): m_s "answered" at Jz = 3.2, 3.3, 3.4, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0; local labels at none; largest miss of the cubic at those couplings 0.214 tau.
- n = 115. Per-site split conformal over all choices of 2 calibration couplings (990 choices), test range: sites covered, labels / truth: cubic 0.180 / 0.000, null 0.022 / 0.000. **Like-for-like block, not a property of the real labels** (the stored in-sector thresholds at E_real, at the couplings of the stored map only; seen before the hash, F6 and F9): m_s "answered" at Jz = 3.3, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0; local labels at none; largest miss of the cubic at those couplings 0.137 tau.
- The block `device_illustration` of the stored script (this project's three device points against the cubic trained on the real labels) is in `out/learn/results_cheap.json`; it is not part of the declaration and is not used.

### III-3.6 Not computed

- **pilot perceptron, n = 57, in distribution (45 held-out couplings, real and DMRG labels)** (4050 fits). Reason: cost: about 22 CPU-hours at the 19.5 s per fit measured in this run; outside the time allowed to this task. To complete: python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=H --model=mlp_pilot3 --size=57 --part=i/k (i = 0..k-1), then --assemble=k, then run_learn.py --stage=merge and --stage=rules; the test-range piece is already in out/learn/parts/.
- **pilot perceptron, n = 115 (secondary), test range and in distribution** (4142 fits). Reason: cost: more than 22 CPU-hours. To complete: the same commands with --size=115 (first --part=ood).
- **the dataset paper's architecture 1, n = 57, test range (real and DMRG labels)** (92 fits). Reason: cost: about 13 CPU-hours (520 s per fit measured before the hash on an idle core). To complete: python -B -I code/run_learn.py --hash=H --stage=f1_ibm57, then --stage=merge.
- None of L1-L3, (f2), (f3) uses these models. Their rows in the table of Sec. 3.1 stay empty; they are not passes.

## III-4. (f2) The learner-independent floor

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

## III-5. (f3) The constructive test: train and calibrate only on labels certified at their own energy

200 seeded splits of the set (`numpy.random.default_rng([1845216616, n, c])`). M1: line in 1/Jz; M2: 1 - a/Jz^2 - b/Jz^4, both fitted to the real m_s labels of the training couplings. Control M0: the cubic in 1/Jz trained on every real training label outside the calibration and query couplings (uncertified labels included). Score s_j = max(|f(x_j) - lo_j|, |f(x_j) - hi_j|) over the exact interval of the calibration label; q = the ceil((m+1)(1-alpha))-th smallest; interval f(x) +- q. **Pass rule, n = 57, set S_p, both M1 and M2: (W) in at least 90 % of the splits 2q <= tau(x) at every query, and (C) the truth within q of the prediction in at least 90 % of all (split, query) pairs.**

### III-5.1 Primary: n = 57, S_p = S_1/2 (18 couplings, Jz = 4.3-6.0; 4 training, 9 calibration, 5 query couplings per split): **PASS**

- M1: (W) 200 of 200 splits (rule: at least 180): met. (C) 1000 of 1000 pairs (rule: at least 900): met. Width 2q = 0.586-0.857 tau (median 0.733). Largest miss of the prediction 0.137 tau. Smallest ratio of 2q to the widest calibration interval: 1.271 (the floor of (f2) is respected in every split: 0 violations).
- M2: (W) 200 of 200 splits (rule: at least 180): met. (C) 1000 of 1000 pairs (rule: at least 900): met. Width 2q = 0.562-0.856 tau (median 0.719). Largest miss of the prediction 0.149 tau. Smallest ratio of 2q to the widest calibration interval: 1.164 (the floor of (f2) is respected in every split: 0 violations).
- Control M0 (secondary): **PASS**. (W) 200 of 200, (C) 1000 of 1000, 2q = 0.599-0.761 tau, largest miss 0.090 tau. **The control passes as well, with a smaller largest miss than M1 and M2:** on these data, what makes the test pass is calibrating on certified labels with the interval score; training only on certified labels brought no measurable gain.
- With m = 9 calibration labels, k = 9: q is the largest calibration score; the level 9/10 = 0.9 is attained exactly.
- The 1000 (split, query) pairs are drawn from 18 couplings and are not independent trials; the counts are those of the declared rule.
- Gate G7 inside the test: labels outside their exact interval: none; truths outside: none.

### III-5.2 Every set, model and size

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

### III-5.3 Proposition 2(a) on the same splits and the secondary width-normalized scores (no rule)

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

### III-5.4 The limit, printed with the result (declaration Sec. 7)

Between Jz = 4 and 6 the true m_s changes by 0.4 tau (measured: 0.388-0.398 tau at n = 57 and 0.364-0.373 tau at n = 115; over the primary set, Jz = 4.3-6.0: 0.294-0.301 tau). The test shows that the intervals survive the learner and its calibration where labels are certified. It does not show that a hard function was learned. Two facts of this run say the same: the control M0 passes, and the largest miss of the real labels of the primary set is already 0.082 tau [S, F7].

## III-6. Independent recomputation (own code, `checks/rd_learn_independent.py`; decides nothing)

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

## III-7. Post hoc (not declared; these lines decide nothing)

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

## III-8. Re-executed, only compared, not checked

- **Re-executed:** the sealed code (cheap stage: cubic, null, Proposition 2, floor, constructive test, rules; the perceptron's test-range piece at n = 57); the manifest check; own independent recomputation (Sec. 6); the post hoc lines.
- **Only compared:** the intervals of `out/S_sets.json` with the m_s rows of `out/map_real.json` (equal); S with the CERTIFIED (exact) rows; the stored splits with the regenerated ones.
- **Not checked here:** the exact certificates and the explicit states behind the intervals (map task, gates G5-G7; G6 first part NOT COMPLETE); the conversion of the public files (G1 NOT COMPLETE); the unit tests of gate G8 were not re-run; the perceptron in distribution and at n = 115 and architecture 1 were not computed (Sec. 3.6); the perceptron's test-range numbers have no independent recomputation.

## III-9. Two sentences for an abstract, each traceable

1. At 57 qubits, standard conformal intervals calibrated on the public labels contain 41 of 45 held-out labels but the reference (DMRG) value of the staggered magnetization at 0 of the 45 training couplings and at 0 of the 4 test couplings, where the cubic model misses it by 2.28 to 3.73 times the tolerance.
   Source: `out/learn_real.json` -> `summary.57.models.poly3_invJ.real.ind` (label_covered, truth_covered), `.real.test` (truth_covered, miss_tau); sealed file `out/learn/results_cheap.json`.
2. Calibrated instead on the 18 labels that the published energy and site magnetizations certify to within half the tolerance (Jz = 4.3 to 6.0), intervals built from the exact energy bounds were narrower than the tolerance in 200 of 200 random splits (0.56 to 0.86 of it) and contained the reference value in 1000 of 1000 cases, for both declared models; the true value varies by only 0.30 of the tolerance over that range, so this shows that the guarantee survives the learner and its calibration, not that a hard function was learned.
   Source: `summary.57.f3.sets.S_1_2.models.M1|M2` (n_splits_W, n_pairs_C, width_tau_min, width_tau_max); `independent_check.sizes.57.f3.S_1_2.truth_change_over_tau` (post hoc line); sealed file `out/learn/f3_constructive.json`.

Alternative for the negative half: With all 45 public training labels in the calibration set, no learner using a constant-width score can return a guaranteed interval narrower than 5.35 times the tolerance at the test couplings (57 qubits; 4.65 at 115). Source: `summary.57.f2.test`, `summary.115.f2.test` (sealed file `out/learn/f2_floor.json`; carries the mark of gate G6).

Limits to keep next to them: sentence 2 is a statement about 18 couplings at large Jz, where the labels are already within 0.082 tau of the truth and the control model passes too; on all 26 certified labels the same test fails on width; the cases are (split, query) pairs drawn from these couplings, not independent trials; the exact intervals assume that the published energy and site magnetizations belong to one state.

