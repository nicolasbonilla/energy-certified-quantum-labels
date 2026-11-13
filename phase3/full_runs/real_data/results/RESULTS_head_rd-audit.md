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
- File times: of the 507 files under `out/`, `results/` and `e1/`, 452 are later than the hash file; the other 55 are the
  files of `out/n19/` (exact n = 19, no real datum, listed in Sec. 11 of the declaration as computed before the hash).
  No file of `code/`, `tests/`, `converted/` or `source/` is later than the hash. Three distinctive real values (two
  energies, one label) were searched in `tests/` and in the scratch folders of the review: before the hash they occur
  only in the declared first look. These are file times and a text search, not an external time stamp.
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

Five couplings per size, sum_i <Z_i> - M_0 and q: n = 57: 1.1: -0.234198, 0.117099; 1.6: -0.095047, 0.047524; 3.4:
-0.008297, 0.004148; 4.0: -0.004367, 0.002183; 6.0: -0.000729, 0.000365. n = 115: 1.1: -0.435201, 0.217600; 1.6:
-0.202599, 0.101300; 3.4: -0.020793, 0.010396; 4.0: -0.011457, 0.005728; 6.0: -0.002675, 0.001338.

Exact interval of m_s at six couplings per size (ends rounded outward; width in units of tau and of the reference-free
tolerance; width with M = M_0 alone; the two couplings that decide J*_exact are the first two of n = 57 and, at
n = 115, Jz = 3.9, where no m_s certificate exists, and 4.0):

| n | Jz | interval | width / tau | width / tau_rf | at M_0 alone | CERTIFIED (exact) | label, truth |
|---|---|---|---|---|---|---|---|
| 57 | 3.4 | [0.90776, 0.96459] | 1.0043 | 1.0433 | 0.9860 | no | 0.953217, 0.943039 |
| 57 | 3.5 | [0.91420, 0.96590] | 0.9105 | 0.9423 | 0.8943 | yes | 0.955448, 0.946167 |
| 57 | 3.6 | [0.91997, 0.96750] | 0.8346 | 0.8610 | 0.8191 | yes | 0.957445, 0.949046 |
| 57 | 4.0 | [0.93776, 0.97280] | 0.6093 | 0.6228 | 0.5995 | yes | 0.964851, 0.958546 |
| 57 | 5.0 | [0.96234, 0.98122] | 0.3232 | 0.3269 | 0.3187 | yes | 0.976306, 0.973299 |
| 57 | 6.0 | [0.97421, 0.98705] | 0.2179 | 0.2195 | 0.2164 | yes | 0.983597, 0.981396 |
| 115 | 4.0 | [0.94303, 0.97271] | 0.5148 | 0.5246 | 0.5018 | yes | 0.964699, 0.961015 |
| 115 | 4.1 | [0.94220, 0.97511] | 0.5696 | 0.5821 | 0.5578 | yes | 0.966516, 0.962858 |
| 115 | 4.5 | [0.94646, 0.98060] | 0.5871 | 0.6012 | 0.5773 | yes | 0.971458, 0.969068 |
| 115 | 5.0 | [0.95455, 0.98563] | 0.5314 | 0.5427 | 0.5252 | yes | 0.976834, 0.974872 |
| 115 | 5.5 | [0.96662, 0.98665] | 0.3408 | 0.3452 | 0.3361 | yes | 0.980307, 0.979188 |
| 115 | 6.0 | [0.97774, 0.98627] | 0.1447 | 0.1454 | 0.1413 | yes | 0.983287, 0.982484 |

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
| 115 | 1.4 | 0.134436 | R3 of 1.4 | -59.586801 | 56 states stored at 1.4 | [0.397020, 0.895752] | 9.827 tau | NOT CERTIFIED |
| 115 | 3.0 | 0.015845 | R3 of 3.0 | -106.524151 | 42 states stored at 3.0 | [0.898502, 0.957502] | 1.038 tau | NOT CERTIFIED |

P5 ratios at five couplings (own n = 19 diagonalization): n = 57: 0.8512, 0.8062, 0.8392, 0.8212, 0.9454 at Jz = 1.1,
1.5, 2.0, 2.5, 2.9; n = 115: 0.8122, 0.6087, 0.7313, 0.6962, 0.7331 (the last four below 0.75). Equal to the stored
ones to the digits shown.

One split of (f3) end to end (n = 57, S_1/2, split 0; training 4.7, 4.9, 5.2, 5.4; calibration 4.5, 4.6, 5.1, 5.3, 5.5,
5.6, 5.8, 5.9, 6.0; queries 4.3, 4.4, 4.8, 5.0, 5.7): M1: q = 0.019479137, 2q / tau(x) = 0.6735, 0.6724, 0.6687, 0.6671,
0.6630, truth inside at 5 of 5; M2: q = 0.019075297, 0.6596-0.6492, 5 of 5; M0: q = 0.020374537, 0.7045-0.6934, 5 of 5.
The 200 splits of every set equal the stored ones.

**Three extra checks of the audit (post hoc; they decide nothing).**
- *Check A, why the map could not be contradicted.* At every stored training coupling the public energy error lies
  inside the window that the figures-based map had assumed (0.967-1.038 times the digitized value at n = 57,
  0.986-1.011 at n = 115, against a window of 0.8-1.2); at the four test couplings it is 1.28-1.79 times (n = 57) and
  1.28-1.90 times (n = 115) the floor that the map had assumed. A window grows with the energy, so every one of the 152
  decisive predicted statuses carries over for that reason alone; the 13 GRAY rows are the only ones whose outcome was open.
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
