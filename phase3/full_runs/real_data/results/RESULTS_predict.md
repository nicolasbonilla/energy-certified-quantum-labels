# Real data of arXiv:2606.15983: RESULTS of the predictions (declaration Sec. 5) and of the n = 19 comparison (Sec. 6)

Task `rd-predict`, 2026-11-12. Declaration: `real_data/DECLARATION.md`, SHA-256 `6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa` (checked before anything was read).
Every outcome below is the output of the sealed code `code/run_predict.py`, run unchanged. No rule was changed.

## Resumen en español (ocho líneas)

1. Se comprobó que la declaración sellada no había cambiado (su huella coincide) y se ejecutó el programa sellado, tal cual, sobre los datos públicos.
2. Predicción de signo (P1-P3): SE CUMPLE en los ocho casos (cuatro familias de etiquetas, dos tamaños). Entre el 99,83 % y el 100 % de las etiquetas reales quedan desplazadas hacia el estado de Néel respecto del valor verdadero; la regla pedía el 95 %.
3. Predicción de que el error baja al crecer Jz (P4): SE CUMPLE en los ocho casos. La correlación de rangos va de -0,996 a -0,971; la regla pedía -0,9 o menos.
4. Predicción de la curva de sesgo contra energía (P5): NO PASA. El error medio tras corregir sí cumple (0,111 tau con límite 0,2 a 57 cúbits; 0,168 tau con límite 0,6 a 115) y los cocientes a 57 cúbits también (de 0,802 a 1,046); pero a 115 cúbits 12 de los 19 cocientes que deciden quedan por debajo de 0,75 (van de 0,608 a 0,813).
5. Consecuencia fijada de antemano en la declaración: la Sec. V del artículo queda limitada a la primera etapa del método, y el artículo tiene que decirlo.
6. La fórmula sencilla sin parámetros (la «cuerda») corrige mejor que la curva sobre las 50 constantes: 0,058 tau frente a 0,111 tau a 57 cúbits y 0,094 tau frente a 0,168 tau a 115.
7. El cálculo exacto pequeño (19 sitios) queda a 1,05-1,47 tau (57) y 1,43-2,07 tau (115) de la verdad en las cuatro constantes de prueba y, como mucho, a 0,135 tau y 0,143 tau en las etiquetas que el filtro conserva; a 57 cúbits está más cerca de la verdad que la etiqueta real en 39 de las 50 constantes (a 115, en 11).
8. Un segundo programa, escrito aparte, reproduce todos los números (diferencia máxima 2e-16). No se halló ningún defecto en el programa sellado y no se cambió ninguna regla. Una comprobación queda incompleta (G1: no se repitió la conversión de los datos; sus huellas sí coinciden).

## Summary (English)

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

## 1. What was run

- `DECLARATION.sha256` equals the SHA-256 of `DECLARATION.md` (`sha256sum`; the gate of the sealed code; the independent script). `python -B -I checks/make_manifest.py --check`: 69 lines of Sec. 11 equal to the files on disk, 0 different, 4 not re-hashed there (`converted/`, `source/`). The four code and two n = 19 files used here were hashed again by this script and equal Sec. 11: `code/run_predict.py`, `code/rd_predict.py`, `code/rd_common.py`, `code/n19_curves.py`, `out/n19/n19_curves.json`, `out/n19/n19_labels.json`.
- Command: `python -B -I code/run_predict.py --hash=6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa` (Python 3.11.4, numpy 1.26.4, scipy 1.13.1, two threads, laptop; about 3 s).
- Run 1: 2026-11-12T19:28:35Z to 2026-11-12T19:28:39Z UTC, before `out/S_sets.json` existed (kept set of the filter not available). Run 2: 2026-11-12T19:36:08Z to 2026-11-12T19:36:10Z UTC, after the map task had written `out/S_sets.json` (SHA-256 `45308c5273c43303968eb0e014153ff2ed10c7e656a1dc4cf5a6161ab9610ab4`, equal to `out/S_sets.sha256`). The two outputs are identical except for the kept-set part of the n = 19 comparison (compared key by key). Run 1 is kept in `out/predict/first_run_before_S_sets/`.
- Output of the sealed code: `out/predict/predict_results.json` (SHA-256 `04be4924ea62f10c201afa8a713fb365d4308af67de74920d09ef450f92c2ac8`), copied verbatim into `out/predict_real.json` together with provenance, the independent check and the post hoc lines.
- Truth (declaration Sec. 0 and Sec. 12, line 1): this project's bond-dimension-320 references for E0 and m_s at 18 (n = 57) and 16 (n = 115) couplings, the authors' DMRG elsewhere and for every single site, pair and loop. Orientation +1 at every coupling for labels and truth: True (57), True (115).
- No code defect was found. Nothing listed in Sec. 11 was changed. See `DEVIATIONS.md` for the dated notes of this task.

## 2. P1-P3: every label lies on the Neel side of the truth

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

## 3. P4: the error decreases with Jz

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

## 4. P5: the bias-against-energy curve of Sec. V

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

### 4.1 Mean and largest misses, with the comparators (units of tau)

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

### 4.2 Every coupling, n = 57

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

### 4.3 Every coupling, n = 115

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

## 5. The small classical calculation next to every label (Sec. 6; descriptive, no rule)

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

## 6. Secondary: the comparison variant (`skqd_post_select`, n = 115, 46 couplings; Jz = 5.6, 5.7, 5.9, 6.0 excluded by gate G2)

Same code, same rules, no decision attached (secondary everywhere). All [N].

- Sign: F = 1.0000, 1.0000, 1.0000, 1.0000 (sites, edges, second neighbours, loops), all pairs positive; fraction with t <= 1: 1.0000.
- Rank correlation of D with Jz: -0.9964, -0.9928, -0.9964, -0.9947.
- Curve: mean corrected miss 0.179 tau (raw 0.567, chord 0.098, truth at n = 19 0.437); ratios at the 19 deciding couplings 0.697-0.802, **outside [0.75, 1.3] at 14 of them** (Jz = 1.5-2.7, 2.9). The variant shows the same shortfall as the dataset at n = 115.

## 7. Gates and checks behind these numbers

- **G1 (data): NOT COMPLETE.** Hashes of `converted/real_n57.json`, `real_n115.json`, `lattice_maps.json` equal the pinned ones; the declared re-run of the converter on the pinned archive was not done (not by this task; the map task records `rerun: null`).
- **G2 (same state), re-checked here with own code:** the exchange part of the energy lies inside the bound at all 100 points: 0.932-0.989 of the bound (n = 57) and 0.952-0.997 (n = 115) [S] (T3).
- **G3 (energies):** E_real - E0(authors) >= 0.0468 (n = 57) and 0.0458 (n = 115) [S] (T4). **G4 (truth):** authors' DMRG against this project's references at the stored couplings: m_s within 5.3e-05 tau and 5.2e-05 tau, the seven label types within 1.5e-04 and 2.8e-04 tau (limit 1e-3), E0 within 1.9e-06 and 3.0e-05 (limit 1e-4) [S] (T5).
- **Independent recomputation** (`checks/rd_predict_independent.py`, written after the hash, no function shared with the sealed code; lattice from the repository's edge list, second neighbours derived, Neel values computed as products of eta, `scipy.stats.spearmanr`, own interpolation): the largest absolute difference from the sealed output over 84 compared quantities (F, F per coupling, t range, D, rank correlations, every column of the P5 rows, the means) is **2.2e-16**; the same couplings decide, the same ratios are outside, the same outcomes.
- **n = 19 from scratch** (own exact diagonalization, sector dimension 75582, the same 26 levels): against `out/n19/n19_curves.json` at the 50 couplings |dE0| <= 5e-14, |dm_s| <= 2e-11, curve points within 4e-15 (energy) and 8e-09 (bias); residual of the ground state at most 3e-11. Reading the curve from this recomputation changes no ratio by more than 3e-09.
- **Same recipe as the paper's curves:** `out/n19/n19_curves.json` against `bias_law/inputs/n19_curves.json` at the 14 couplings they share: |dE0| <= 3e-14, |dm_s| <= 3e-11, curve within 1e-08 (the tolerances of the earlier gate were 1e-8, 1e-6, 1e-5).

## 8. Post hoc (not declared; no rule; nothing here changes an outcome)

- **The outcome of P5 does not depend on the choice of truth or on the curve file.** With the authors' DMRG as truth at every coupling (instead of this project's references where stored): FAIL, the same 12 couplings outside at n = 115, ratios 0.6087-0.8122; n = 57 ratios 0.8029-1.0455. With the curve recomputed from scratch: FAIL, identical.
- **Not a borderline failure.** Three of the twelve outside ratios at n = 115 are within 0.01 of the band (Jz = 1.6: 0.7483; 1.7: 0.7451; 1.9: 0.7411); the other nine are 0.734 or lower, down to 0.6087 at Jz = 1.5.
- **The point n = 115, Jz = 1.5** has the lowest ratio, a larger energy error per site than its neighbour at 1.4 (0.0157 against 0.0154) and all 13 pairs of Sec. 2 that are not on the Neel side: the published state has a local region (around sites 19 and 89) that is less ordered than the ground state. Without this coupling the ratio condition still fails at n = 115 (11 other couplings outside).
- **Ratio of the bias to the chord** (the rule does not apply to the chord): at the deciding couplings 0.771-1.089 at n = 57 (0 outside [0.75, 1.3]) and 0.660-1.020 at n = 115 (6 outside: Jz = 2.4, 2.5, 2.6, 2.7, 2.8, 2.9). The chord has smaller mean misses than the curve, but it would not meet the ratio condition at n = 115 either.
- **Coupling by coupling,** the curve leaves a smaller miss than the chord at 34 of 50 couplings at n = 57 (Jz = 2.6-5.3, 5.5-6.0) and at 35 of 50 at n = 115 (Jz = 2.6-6.0); the chord leaves the smaller miss at the other 16 and 15 (Jz = 1.1-2.5, 5.4; Jz = 1.1-2.5). The chord wins in the mean because it is the better of the two at small Jz, where the misses are large. The correction with the curve makes no label worse than it was (couplings with corrected miss above raw miss: 0 at n = 57, 0 at n = 115).
- **How much the basis optimization lowers the energy error** (E_first against E_real, both in the public files; [S] in part: F10, T4): the error per site before the optimization is 2.8 to 8.9 times the final one at n = 57 (median 6.7) and 6.6 to 175.4 times at n = 115 (median 29.6); at the deciding couplings 4.0-7.7 and 6.6-24.1. The declaration's phrase "five- to tenfold" describes n = 57; at n = 115 the factor is above ten at 45 of the 50 couplings. The final optimization does far more of the work at n = 115, which is where the first-stage curve fails. This is an observation; no test of it was declared or made.

## 9. Re-executed, only compared, not checked

**Re-executed by this task:** the hash check of the declaration; `checks/make_manifest.py --check`; the sealed `code/run_predict.py` (twice); an independent recomputation of P1-P5 and of the n = 19 comparison from the plain JSON; the exact diagonalization at n = 19 at the 50 couplings, from scratch; gates G2, G3, G4 for the dataset.

**Only read or compared:** the kept sets of `out/S_sets.json` (fixed by the map task; read through the sealed loader, which checks the file against `out/S_sets.sha256` and the declaration hash; not re-derived here); the gate records of the map task (`out/map_gates.json`, `out/run_map_stdout.txt`); the numbers of declaration Sec. 1 (F4, F7, F8, T3-T5) against the present output, which agree at every value compared (de at Jz = 1.1-1.5; raw misses 4.95 and 4.67 tau at Jz = 1.1; above tau up to Jz = 1.9 and 1.8, above tau/2 up to 2.4 and 2.2; site fraction 0.98 at (115, 1.5)).

**Not checked:** gate G1 in full (no re-run of the converter); the unit tests of G8 were not re-run (their records are `checks/G8_*`; the tested files are byte-identical to those run, by the manifest); that the published energy and the published labels belong to one and the same state (declaration Sec. 10, point 6: supported by G2 and by the reading of the authors' code, not provable from the files); the authors' DMRG itself, which is the truth for every single site, pair and loop (no new DMRG was run).

## 10. Files

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

