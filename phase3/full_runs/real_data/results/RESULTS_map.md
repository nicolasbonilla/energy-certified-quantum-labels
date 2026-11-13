# Map on the real data of arXiv:2606.15983: RESULTS (Secs. 2, 3, 4, 6 and gates G1-G7 of the declaration)

Written by the task `rd-map` on 2026-11-12 from the outputs of the sealed code (`code/run_map.py`, run from 2026-11-12T19:28:57Z to 2026-11-12T19:31:01Z UTC, after the hash of 2026-11-12T19:22:32Z). Declaration SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa`, checked against `DECLARATION.sha256` before anything was read. **Label of the whole analysis: DECLARED AFTER PARTIAL SIGHT. NOT BLIND.** Every block below says which of its numbers had been seen before the hash (items F1-F10 and T1-T7 of Sec. 1 of the declaration) and which are new.

Printed numbers are rounded outward (interval ends away from the interval, widths and misses up, margins down). The exact rationals are in `out/map_rows.json`; the same rows in compact form are in `out/map_real.json`. This file is produced by `results/make_results_map.py`, which copies and does not recompute.

**Two marks that go with every result of this file.** Gate G1 is NOT COMPLETE: the three converted files have the SHA-256 pinned in the declaration and the archive has its pinned SHA-256, but the converter was not run again (it uses a restricted unpickler, and this task was told to unpickle nothing). Gate G6 (first part) is NOT COMPLETE: none of the 150 witness components selected by the declared rule has its tensors on the laptop, so none was checked; 280 of the 439 NOT CERTIFIED rows rest on an energy re-evaluated by the linear rule and carry this mark. Extension E1 was not available when the map was run: there is no E1 column.

## Resumen en ocho líneas (español llano)

1. Los datos públicos se analizaron con las reglas fijadas de antemano; la huella de la declaración se comprobó antes de abrir nada y ninguna regla se cambió después.
2. Punto de partida: los estados cuyas etiquetas se publican no están en el sector que supone el artículo; la desviación es pequeña pero aparece en los 100 puntos, así que se usó la regla más débil (energía y magnetización media).
3. Con esa regla y aritmética exacta, la magnetización alternada publicada queda garantizada dentro de la tolerancia en 26 de 45 puntos de entrenamiento con 57 cúbits (acoplamiento 3.5 a 6.0) y en 21 de 45 con 115 cúbits (4.0 a 6.0); la correlación media entre vecinos, en 27 y 21.
4. En el otro extremo, con estados explícitos se muestra que la energía y la magnetización media NO bastan para garantizar esas dos etiquetas desde 1.1 hasta 3.1 (57 cúbits) y hasta 3.0 (115), incluidos todos los puntos de prueba; las etiquetas locales no quedan garantizadas en casi ningún punto de 57 cúbits.
5. Entre ambos extremos queda una franja sin decidir: 3.2 a 3.4 con 57 cúbits y 3.1 a 3.9 con 115 (magnetización alternada).
6. La predicción hecha a partir de las figuras se confirma según la regla declarada: de 165 filas, 152 coinciden, 13 pasan de sin decidir a decididas, ninguna se contradice, y los ocho umbrales salen idénticos.
7. Lo que NO se puede decir: que la cifra del artículo (garantizado desde 3.2, 29 de 45) sea una propiedad de las etiquetas reales, porque descansa en la hipótesis del sector, que los datos no cumplen; ni que ninguna etiqueta local quede garantizada bajo esa hipótesis (dos lo están con 57 cúbits y acoplamiento 6.0).
8. Dos comprobaciones quedaron incompletas y así se dice: no se repitió la conversión de los datos, y la comprobación de las energías recalculadas no pudo hacerse sobre los estados decisivos porque no están en este equipo.

## 0. First, plainly: what the real data allow the paper to say about the dataset's own labels, and what they do not

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

## 1. The departure from the sector at every coupling (finding of Sec. 2 of the declaration)

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

## 2. Exact intervals of m_s and Czz_bar at the real energies (certified side of Sec. 2)

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

## 3. NOT CERTIFIED from explicit states (all seven labels)

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

## 4. Like-for-like statuses under the paper's sector hypothesis, and J*_s

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

## 5. J* under each rule and the counts out of 45 (table of Sec. 3 of the declaration)

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

## 6. Predicted from the figures versus obtained from the data (the 171 stored rows)

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

## 7. The accuracy factor at the test couplings (Sec. 4 of the declaration)

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

## 8. The label filter on the 45 real training labels per size (Sec. 6 of the declaration)

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

## 9. The nested sets of Sec. 7 (f3), fixed here for the learning task

`out/S_sets.json`, SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4` (also in `out/S_sets.sha256`), written by the sealed code before any other output and before any learning number. Stored certificates only (no E1).

| n | S (interval <= tau) | S_3/4 | S_1/2 | S_p |
|---|---|---|---|---|
| 57 | 26: 3.5-6.0 | 23: 3.8-6.0 | 18: 4.3-6.0 | S_1/2 (18 couplings) |
| 115 | 21: 4.0-6.0 | 21: 4.0-6.0 | 10: 5.1-6.0 | S_3/4 (21 couplings) |

## 10. Gates G1-G7

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

## 11. Secondary rows (Sec. 3 of the declaration)

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

## 12. Post hoc: independent check of the exact intervals (`checks/spotcheck_exact_intervals.py`; not declared, decides nothing)

A separate script of this task, written from the text of the declaration, importing nothing of the sealed code (standard library, `fractions.Fraction`), rebuilt the interval of m_s and Czz_bar at all 50 couplings of both sizes from the certificate files and the converted data. Rows compared with the sealed output: 200; identical in both ends as exact rationals and in both flags: 200. Certified rows whose label or truth lies outside the interval: 0. Its counts: n = 115 Czz_bar (tau): 21 of 45, J*_exact 4.0; n = 115 Czz_bar (tau_rf): 21 of 45, J*_exact 4.0; n = 115 m_s (tau): 21 of 45, J*_exact 4.0; n = 115 m_s (tau_rf): 21 of 45, J*_exact 4.0; n = 57 Czz_bar (tau): 27 of 45, J*_exact 3.4; n = 57 Czz_bar (tau_rf): 27 of 45, J*_exact 3.4; n = 57 m_s (tau): 26 of 45, J*_exact 3.5; n = 57 m_s (tau_rf): 26 of 45, J*_exact 3.5. Six rows are printed in full in `checks/spotcheck_exact_intervals_stdout.txt` (m_s at n = 57, Jz = 3.4 and 3.5; m_s at n = 115, Jz = 4.0 and 5.0; Czz_bar at n = 57, Jz = 5.0 and at n = 115, Jz = 4.0).

**Post hoc: explicit states against exact bounds (`checks/finalize_rd_map.py`; not declared, decides nothing).** The two explicit witness mixtures of a row lie in W(E_real, M_real), so their labels must lie inside the exact interval of the same row. rows with both an exact interval and a witness interval: 108; violations: 0 []; smallest distance of a witness end to the corresponding end of I: 0.000202. The two sides of Sec. 2 (stored DMRG states, exact-arithmetic certificates) do not depend on each other, so this checks both.

## 13. Re-executed, only compared, not checked

- **Re-executed by this task:** the sealed map code on `converted/` (one run, default options: hash check of G1, G2-G7, re-proof of the deciding certificates); the independent recomputation of the 200 exact rows (Sec. 12); the post hoc supplement to G6; `sha256sum` of the declaration, of every code file listed in Sec. 11 of the declaration (all equal) and of the pinned archive.
- **Only compared (not recomputed here):** the stored map (chains, thresholds, states), read through its own code; the stored exact certificates other than the 12 re-proved for G5 (each has its recorded verification; 196 distinct ones were re-proved by the review report `math-rigorous-bounds`); this project's references against the authors' DMRG (G4).
- **Not checked:** the conversion of the archive (G1 re-run); the energies of the decisive witness components from their tensors (G6, first part); that the published energy and site magnetizations belong to one state beyond the necessary condition of G2; the unit tests were not run again (gate G8 was passed and recorded by the sealing task).
- **Code:** no sealed file was changed. SHA-256 of the six map code files at run time (from `out/map_summary.json`): `map_certs.py` 3922350fea086147; `map_common.py` ec8f92a779305718; `map_gates.py` 5f1f47a4b0b8e719; `map_stored.py` e1214cf36f5a3c08; `map_tables.py` a1c04230ef8b5db3; `run_map.py` 199e5b0a0a6c0851.
- **Files:** `out/S_sets.json`, `out/S_sets.sha256`, `out/map_rows.json`, `out/map_summary.json`, `out/map_secondary.json`, `out/map_gates.json`, `out/map_tables.md`, `out/SHA256SUMS_map.txt`, `out/g5/` (sealed code); `out/map_real.json`, `results/RESULTS_map.md` (this script); `checks/spotcheck_exact_intervals.*`, `checks/g6_supplement.*`, `checks/finalize_rd_map.py`, `checks/consistency_witness_inside_exact.txt`; `DEVIATIONS.md`; hashes in `results/SHA256SUMS_rd-map.txt`.

