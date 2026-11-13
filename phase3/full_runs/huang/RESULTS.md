# Huang benchmark (second public dataset): RESULTS

**Declared and hashed before any computation at n ≥ 19** (`DECLARATION.md`, SHA-256
053ceac828d21999c4d2dd3ef5999c9de1e639153d411a6c63ec272aa6479f6e, hashed 2026-10-31T08:03:58Z). Batch
20261031T080637Z on cj-runner-2. Dataset: Huang, Kueng, Torlai, Albert, Preskill, arXiv:2106.12627, official repository
github.com/hsinyuan-huang/provable-ml-quantum at commit 646a1cb2… (read as data only). Energies in the paper's units
H = Σ_b J_b (XX + YY + ZZ) (the repository's `*_E.txt` stores ⟨H⟩/2); labels C_ij = (XX + YY + ZZ)/3 ∈ [−1, 1/3].
Every number comes from `out_20261031T080637Z/` (fetched; 1069 files verified against `OUT_SHA256SUMS.txt`) or from the
laptop re-executions listed in §11. Written 2026-10-31, 11:35-12:30 UTC.

## Resumen en español sencillo

1. Probamos la regla del artículo con el conjunto de datos público más usado en este campo (Huang y colaboradores: imanes de 20 a 45 espines con enlaces al azar), con las reglas selladas antes de calcular. Usamos 3,5 horas de máquina (unos 1,0 €; 1,3 € con el recargo del programa), dentro del tope de 6. La máquina quedó apagada.
2. Los promedios (la correlación media entre vecinos y la media en diagonal) quedan garantizados por la energía en todo el rango pedido, de 0,001 a 0,01 de error por espín, en los seis casos. El error tolerable de la media entre vecinos va de 0,03 a 0,08 por espín, de 3 a 8 veces más que el máximo del rango.
3. Los datos de un solo par, que son lo que predice el modelo de IA del artículo, casi nunca. Con 20 espines, de 570 pares se garantizan 206 con error 0,001 (casi todos los pares en diagonal, que se mueven poco) y solo 3 con 0,01. Con 30 y 45 espines, ninguno de los nueve pares estudiados se garantiza en ningún punto del rango.
4. Para el mismo enlace, el error tolerable baja al crecer el sistema: 7,3, 4,2 y 2,3 diezmilésimas con 20, 30 y 45 espines. Es lo que dice la regla de los datos locales: el coste en energía de mover un par no crece con el tamaño.
5. La fórmula τ²/(8χ) acierta. Con 20 espines (cálculo exacto) acierta al 1 % en 558 de los 570 pares, dentro del 25 % en todos, y con un error de hasta el 5 % en los promedios. Con 30 y 45 espines, en los promedios la diferencia es como mucho del 12 %.
6. Una excepción con 45 espines: para el par de un extremo al otro, la fórmula se equivoca por un factor 2. La causa es numérica: el cálculo clásico de referencia no es lo bastante preciso a esa escala, y dos controles sellados lo avisaron. Midiendo la respuesta con un empujón algo mayor, menos sensible a ese ruido, la fórmula cae dentro del margen calculado en los 9 casos de 30 y 45 espines.
7. Dos apuestas previas fallaron. Esperábamos que ningún par se garantizara con 20 espines, y un 36 % sí. Esperábamos que el error tolerable de los promedios casi no cambiara entre casos, y va de 0,03 a 0,08: cambia más por el azar de los enlaces que por el tamaño.
8. Las comprobaciones pasan: el cálculo aproximado coincide con el exacto al 0,3 % con 20 espines; nuestras correlaciones coinciden con las publicadas hasta la cuarta cifra decimal; y un programa aparte revisó 185 estados sin diferencias. Los datos se bajaron del repositorio oficial y se trataron solo como datos.

---

## 1. Decisions under the declared rules (DECLARATION §3)

| claim | declared rule | outcome |
|---|---|---|
| **C-H1** benchmark labels | no n = 20 pair correlator CERTIFIED at δe = 1e-3 (prior 0.75) | **fails.** 206 of 570 pairs are CERTIFIED at δe = 1e-3 (56 / 68 / 82 per instance). By class: 70 of 72 diagonal pairs, 2 of 93 nn bonds, 89 of 243 pairs with r ≤ 3, 45 of 162 with r > 3. At δe = 1e-2, 3 of 570 |
| **C-H2** local labels, n = 30, 45 | Ccent, Cfar, Cfix NOT CERTIFIED (rigorous side) at δe = 1e-3 at every n = 30, 45 instance (prior 0.85) | **holds**: 9 of 9 rows NOT CERTIFIED at δe = 1e-3, and at every grid δe. The widths are 1.3-1.8 τ (inner side) at 1e-3 |
| **C-H3** averages | Cnn CERTIFIED at δe = 1e-3 at all six instances (prior 0.8; recorded: at 1e-2, prior 0.4) | **holds**: CERTIFIED at every grid δe (1e-3 … 1e-2) at all six instances. Cd2 also at every δe on all six; Cstag (n = 20, record) on all three |
| **C-H4** the rule | law/computed ∈ [0.8, 1.25] for every Cnn, Cd2 row; every Ccent, Cfar, Cfix row; pair labels ≥ 90 % in band | **averages hold** (12 rows, 0.981-1.121). **Pair labels hold** (570 of 570 in band; median 0.999). **Local rows:** n = 20 (exact) 9 of 9 rows at 0.999. At n = 30, 45 the declared gates P1 and P2 failed, so by the declared rule these rows are **no decision**. As computed, 2 rows lie out of band: Cfar at (9, 1) 2.07 and at (9, 2) 2.26. The other 7 lie in 1.02-1.20. §5 gives the cause |
| **C-H5 (a)** size, same bond | Cfix: ε_τ(n)/ε_τ(20, same k) ∈ [0.67, 1.5] at n = 30, 45 (prior 0.6) | **holds on the declared (outer) values**: 0.85 (6, 1), 0.71 (9, 1), 0.91 (9, 2). It depends on the DMRG-referenced side, and P1/P2 failed, so formally this is no decision. The DMRG band gives [0.71, 1.05] and [0.91, 1.58] at n = 45 |
| **C-H5 (b)** size, average | Cnn: δe\*(n)/mean δe\*(20) ∈ [0.67, 1.5] at every n = 30, 45 instance (prior 0.7) | **fails**: 0.64 (6, 1), 0.74 (9, 1), 1.70 (9, 2). The spread between instances (n = 20: 0.040-0.060; n = 45: 0.036-0.083) is larger than any size trend. There is no 1/n decay: the n = 45 mean is 0.060, against the 0.049 n = 20 mean |

**Gates.**

| gate | result | detail |
|---|---|---|
| G2 (convention) | **pass** | max \|C − C_file\| = 1.1-1.6e-5 (ED), 2.2e-4 / 3.9e-4 / 5.6e-4 (DMRG n = 30 / 45 / 45); \|E₀/(2E_file) − 1\| ≤ 3.3e-6 |
| G1 (DMRG pipeline vs ED at (4, 1), χ_c = 256) | **pass** | ε_τ within 0.06-0.25 %, aimed outer widths within 0.07-0.11 % (limits 5 % and 1 %); E₀(256) − E₀^ED = 7.8e-6, E₀(384) − E₀^ED = 3.9e-7 |
| P1 (reference) | **fail at n = 30, 45** | δχ_ref / min local ε_τ = 0.037 (6, 1), 0.091 (9, 1), 0.179 (9, 2) (limit 0.02); 0.0006 at (4, 1) |
| P2 (G(256) vs G(384) at the decisive λ, (9, 1)) | **fail for Ccent, pass for Cnn** | Ccent ±: \|ΔG\| = 9.3e-4 / 9.8e-4 J, ratio 0.079 / 0.084 (limit 0.01); Cnn ±: 3.1e-4 / 3.1e-3, ratio 0.0002 / 0.0019 |
| P3 (cold starts) | **pass** | F_cold − F_warm ∈ [−1.6e-6, +5.6e-6], none stuck |
| P4 (268 stored DMRG states) | **pass** | 0 out of sector; TeNPy vs independent evaluator \|ΔE\| ≤ 1.3e-12, \|ΔC\| ≤ 1e-14, \|Δnorm\|/norm ≤ 4e-15 |
| G4 (separate process, TeNPy not importable) | **pass** | 185 headline components, \|ΔE\| ≤ 1.2e-12, \|ΔO\| = 0, every headline mixture at or below its energy, none missing |
| ED residuals | ≤ 8.7e-11 | every Lanczos call (≈ 13,000) |

**Reading.** At n = 20 everything is exact. It holds over all states, with no symmetry-sector assumption, by the SU(2)
argument of DECLARATION §0 (checked on toys, test T1). At n = 30, 45 the NOT-CERTIFIED statements are rigorous
(explicit states). The CERTIFIED statements and the δe\* values are DMRG-referenced. For the averages the reference
error is irrelevant (ε_τ ≈ 0.6-3.7 against δχ ≤ 2e-3). For the local labels at n = 45 it matters (ε_τ ≈ 0.01-0.02
against δχ ≈ 1-2e-3), hence the P1/P2 failures and the bands below.

## 2. Per-label certification table vs δe (τ = 0.08, ±3 % of the correlator range)

Status letters at δe = 1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3, 1e-2. C = CERTIFIED (w_out ≤ τ); N = NOT CERTIFIED
(w_in ≥ τ, rigorous); G = gray. δe\*_in / δe\*_out: the δe at which the rigorous inner width, resp. the outer width,
reaches τ (equal at n = 20; a DMRG band at n = 30, 45). δe\*_law = S τ²/(8 χ_two n) with χ_two from the λ₀ points.

| label | inst (L,k) | n | method | O_GS | δe\*_in (rigorous) | δe\*_out | δe\*_law | law/out | status | w/τ at 1e-3 (in/out) | w/τ at 1e-2 (in/out) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Cnn | (4,1) | 20 | exact | −0.4581 | 4.01e-02 | 4.00e-02 | 3.95e-02 | 0.988 | C C C C C C C | 0.16 / 0.16 | 0.50 / 0.50 |
| Cnn | (4,2) | 20 | exact | −0.4589 | 4.68e-02 | 4.67e-02 | 4.65e-02 | 0.994 | C C C C C C C | 0.15 / 0.15 | 0.46 / 0.46 |
| Cnn | (4,3) | 20 | exact | −0.4652 | 6.01e-02 | 6.00e-02 | 6.28e-02 | 1.047 | C C C C C C C | 0.13 / 0.13 | 0.40 / 0.40 |
| Cnn | (6,1) | 30 | DMRG | −0.4331 | 3.16e-02 | 3.13e-02 | 3.34e-02 | 1.067 | C C C C C C C | 0.09 / 0.28 | 0.55 / 0.55 |
| Cnn | (9,1) | 45 | DMRG | −0.4245 | 3.63e-02 | 3.62e-02 | 4.06e-02 | 1.121 | C C C C C C C | 0.08 / 0.24 | 0.49 / 0.50 |
| Cnn | (9,2) | 45 | DMRG | −0.4477 | 8.49e-02 | 8.33e-02 | 8.17e-02 | 0.981 | C C C C C C C | 0.06 / 0.13 | 0.35 / 0.35 |
| Cd2 | (4,1) | 20 | exact | +0.2266 | 1.99e-02 | 1.99e-02 | 1.98e-02 | 0.995 | C C C C C C C | 0.22 / 0.22 | 0.71 / 0.71 |
| Cd2 | (4,2) | 20 | exact | +0.2168 | 1.56e-02 | 1.56e-02 | 1.54e-02 | 0.991 | C C C C C C C | 0.25 / 0.25 | 0.80 / 0.80 |
| Cd2 | (4,3) | 20 | exact | +0.2383 | 2.90e-02 | 2.89e-02 | 2.88e-02 | 0.995 | C C C C C C C | 0.18 / 0.19 | 0.59 / 0.59 |
| Cd2 | (6,1) | 30 | DMRG | +0.2062 | 1.42e-02 | 1.42e-02 | 1.42e-02 | 0.999 | C C C C C C C | 0.16 / 0.42 | 0.84 / 0.84 |
| Cd2 | (9,1) | 45 | DMRG | +0.1966 | 1.36e-02 | 1.35e-02 | 1.35e-02 | 0.996 | C C C C C C C | 0.14 / 0.45 | 0.85 / 0.86 |
| Cd2 | (9,2) | 45 | DMRG | +0.2251 | 2.16e-02 | 2.14e-02 | 2.12e-02 | 0.987 | C C C C C C C | 0.11 / 0.29 | 0.68 / 0.69 |
| Cstag | (4,1) | 20 | exact | +0.2093 | 1.01e-02 | 1.01e-02 | 1.02e-02 | 1.004 | C C C C C C C | 0.31 / 0.31 | 0.99 / 0.99 |
| Cstag | (4,2) | 20 | exact | +0.2091 | 1.21e-02 | 1.21e-02 | 1.21e-02 | 1.003 | C C C C C C C | 0.29 / 0.29 | 0.91 / 0.91 |
| Cstag | (4,3) | 20 | exact | +0.2168 | 1.49e-02 | 1.49e-02 | 1.47e-02 | 0.988 | C C C C C C C | 0.26 / 0.26 | 0.82 / 0.82 |
| Ccent (= Cfix) | (4,1) | 20 | exact | −0.3771 | 7.32e-04 | 7.32e-04 | 7.31e-04 | 0.999 | N N N N N N N | 1.17 / 1.17 | 3.67 / 3.68 |
| Ccent (= Cfix) | (4,2) | 20 | exact | −0.6997 | 6.03e-04 | 6.02e-04 | 6.02e-04 | 0.999 | N N N N N N N | 1.29 / 1.29 | 4.02 / 4.03 |
| Ccent (= Cfix) | (4,3) | 20 | exact | −0.4003 | 7.36e-04 | 7.36e-04 | 7.36e-04 | 0.999 | N N N N N N N | 1.17 / 1.17 | 3.66 / 3.67 |
| Ccent | (6,1) | 30 | DMRG | −0.5339 | 5.93e-04 | 5.48e-04 | 5.58e-04 | 1.019 | N N N N N N N | 1.31 / 1.34 | 4.10 / 4.20 |
| Ccent | (9,1) | 45 | DMRG | −0.2022 | 3.71e-04 | 2.60e-04 | 3.07e-04 | 1.180 | N N N N N N N | 1.74 / 1.84 | 5.51 / 5.64 |
| Ccent | (9,2) | 45 | DMRG | −0.7095 | 4.30e-04 | 2.51e-04 | 2.95e-04 | 1.175 | N N N N N N N | 1.70 / 1.88 | 5.64 / 5.72 |
| Cfix | (6,1) | 30 | DMRG | −0.3940 | 4.60e-04 | 4.16e-04 | 4.26e-04 | 1.026 | N N N N N N N | 1.50 / 1.54 | 4.73 / 4.80 |
| Cfix | (9,1) | 45 | DMRG | −0.3888 | 3.41e-04 | 2.31e-04 | 2.78e-04 | 1.204 | N N N N N N N | 1.83 / 1.94 | 5.82 / 5.92 |
| Cfix | (9,2) | 45 | DMRG | −0.5734 | 4.22e-04 | 2.45e-04 | 2.89e-04 | 1.179 | N N N N N N N | 1.72 / 1.90 | 5.68 / 5.79 |
| Cfar | (4,1) | 20 | exact | −0.2180 | 6.38e-04 | 6.38e-04 | 6.38e-04 | 0.999 | N N N N N N N | 1.25 / 1.25 | 3.92 / 3.93 |
| Cfar | (4,2) | 20 | exact | −0.1436 | 6.75e-04 | 6.75e-04 | 6.75e-04 | 0.999 | N N N N N N N | 1.22 / 1.22 | 3.82 / 3.82 |
| Cfar | (4,3) | 20 | exact | −0.1536 | 8.08e-04 | 8.08e-04 | 8.07e-04 | 0.999 | N N N N N N N | 1.11 / 1.11 | 3.49 / 3.50 |
| Cfar | (6,1) | 30 | DMRG | −0.1571 | 3.41e-04 | 2.97e-04 | 3.45e-04 | 1.162 | N N N N N N N | 1.79 / 1.84 | 5.78 / 5.79 |
| Cfar | (9,1) | 45 | DMRG | +0.0320 | 4.58e-04 | 3.47e-04 | 7.17e-04 | 2.066 | N N N N N N N | 1.57 / 1.67 | 5.17 / 5.22 |
| Cfar | (9,2) | 45 | DMRG | +0.0470 | 5.82e-04 | 4.06e-04 | 9.16e-04 | 2.255 | N N N N N N N | 1.41 / 1.57 | 4.93 / 4.98 |

**Which labels does the energy certify, and at what δe\*?**
- **Averages: always, over the whole requested range.** Cnn δe\* = 0.031-0.083, Cd2 0.014-0.029, Cstag 0.010-0.015
  (n = 20), i.e. 1.0-8.3 × above δe = 1e-2. At the top of the range Cnn is still at 0.35-0.55 τ (Cstag at (4, 1) is just
  at the edge: 0.99 τ).
- **Single correlators: almost never, and less so as n grows.** δe\* = 6.0-8.1e-4 at n = 20, 3.0-5.9e-4 at n = 30, and
  2.3-5.8e-4 at n = 45, all below the range. Their widths at δe = 1e-2 are 3.5-5.9 τ. At n = 45 and δe = 1e-2 the
  outer widths are 30-36 % of the full range 4/3.
- **Regime (n = 20, exact):** first gap Δ = 0.52 / 0.78 / 0.63. The local ε_τ (0.012-0.016) is ≪ Δ. The averages'
  ε_τ lies above the gap: Cnn ε_τ/Δ = 1.53 / 1.19 / 1.90. The √ law still holds there (law/computed 0.99-1.05), as
  Theorem 2 states.
- **Relative error:** e₀ = E₀/n = −2.57, −2.60, −2.95 (n = 20), −2.37 (n = 30), −2.44, −2.90 (n = 45). So δe = 1e-3 …
  1e-2 is 0.03-0.4 % of |e₀|. In the repository's units (⟨H⟩/2) these δe would be halved; in S·S units, divided by 4.

## 3. The benchmark's own labels: all 190 pair correlators at n = 20 (exact)

Counts CERTIFIED per δe (τ = 0.08). The rest are NOT CERTIFIED; there are no gray rows at τ.

| inst | pairs | 1e-3 | 1.5e-3 | 2e-3 | 3e-3 | 5e-3 | 7e-3 | 1e-2 | at 1e-3 with τ₂ = 0.04 | at 1e-3 / 1e-2 with τ_paper = 0.111 |
|---|---|---|---|---|---|---|---|---|---|---|
| (4,1) | 190 | 56 | 23 | 15 | 9 | 6 | 4 | 1 | 7 | 154 / 6 |
| (4,2) | 190 | 68 | 25 | 15 | 5 | 1 | 0 | 0 | 2 | 158 / 1 |
| (4,3) | 190 | 82 | 45 | 24 | 10 | 5 | 3 | 2 | 8 | 172 / 5 |

δe\* by pair class (r = Euclidean distance; "diag" = second neighbours (x ± 1, y ± 1)):

| inst | class | n | δe\* min | p10 | median | p90 | max | certified at 1e-3 | law/out median [min, max] | in band |
|---|---|---|---|---|---|---|---|---|---|---|
| (4,1) | nn | 31 | 2.64e-04 | 3.61e-04 | 5.69e-04 | 7.50e-04 | 7.91e-04 | 0 | 0.9992 [0.9969, 1.0001] | 31/31 |
| (4,1) | diag | 24 | 9.54e-04 | 1.06e-03 | 2.15e-03 | 7.64e-03 | 1.29e-02 | 23 | 0.9985 [0.9955, 1.2439] | 24/24 |
| (4,1) | r ≤ 3 | 81 | 2.90e-04 | 4.48e-04 | 8.69e-04 | 1.39e-03 | 2.76e-03 | 27 | 0.9992 [0.9976, 1.0123] | 81/81 |
| (4,1) | r > 3 | 54 | 1.29e-04 | 4.34e-04 | 7.22e-04 | 1.01e-03 | 1.64e-03 | 6 | 0.9992 [0.9979, 1.0062] | 54/54 |
| (4,2) | nn | 31 | 3.14e-04 | 3.31e-04 | 5.23e-04 | 6.77e-04 | 1.43e-03 | 1 | 0.9992 [0.9980, 0.9997] | 31/31 |
| (4,2) | diag | 24 | 9.49e-04 | 1.08e-03 | 1.96e-03 | 2.89e-03 | 3.80e-03 | 23 | 0.9984 [0.9928, 1.0009] | 24/24 |
| (4,2) | r ≤ 3 | 81 | 1.86e-04 | 5.01e-04 | 8.09e-04 | 1.47e-03 | 5.54e-03 | 26 | 0.9992 [0.9970, 1.0102] | 81/81 |
| (4,2) | r > 3 | 54 | 2.51e-04 | 4.80e-04 | 8.26e-04 | 1.17e-03 | 1.41e-03 | 18 | 0.9991 [0.9967, 1.0021] | 54/54 |
| (4,3) | nn | 31 | 3.38e-04 | 4.84e-04 | 6.41e-04 | 7.85e-04 | 2.25e-03 | 1 | 0.9992 [0.9986, 0.9998] | 31/31 |
| (4,3) | diag | 24 | 1.07e-03 | 1.45e-03 | 2.46e-03 | 8.42e-03 | 1.12e-02 | 24 | 0.9984 [0.9964, 1.1381] | 24/24 |
| (4,3) | r ≤ 3 | 81 | 2.36e-04 | 5.91e-04 | 9.30e-04 | 1.91e-03 | 2.52e-03 | 36 | 0.9992 [0.9972, 1.0046] | 81/81 |
| (4,3) | r > 3 | 54 | 1.77e-04 | 5.27e-04 | 8.77e-04 | 1.41e-03 | 1.78e-03 | 21 | 0.9989 [0.9969, 1.0051] | 54/54 |

- **The nn bonds** (the labels closest to the Hamiltonian's own terms) are the least certifiable: median δe\* =
  5.2-6.4e-4; 2 of 93 reach δe\* > 1e-3. **The diagonal pairs** (same sublattice) respond least to their conjugate
  field (small χ_i) and have δe\* ≈ 1-13e-3. They are what makes C-H1 fail. Longer pairs sit in between (median
  7-9e-4).
- **Tolerance matters as τ².** At τ₂ = 0.04 (full width 3 % of the range) only 2-8 pairs per instance are certified at
  1e-3. At τ_paper = 0.111 (± the RMSE of the benchmark's own shadow training labels, 0.052-0.058 with the 1000
  snapshots of each file; 0.072-0.081 with T = 500), 154-172 of 190 are certified at 1e-3, and 1-6 at 1e-2.
- **Size.** δe\* of a local label falls ∝ 1/n (Theorem 1; §6). So the n = 20 fractions above are upper bounds for
  the larger lattices of the same benchmark. Scaling the n = 20 distribution by 20/45, 11-15 of 190 pairs per instance
  (6-8 %, all diagonal or short-range) would still be certified at 1e-3 at n = 45 (an extrapolation, not computed). The only pairs computed at n = 30, 45 (the
  featured ones) are certified nowhere.

## 4. The rule δe\* = τ²/(8χ) (averages) and τ²/(8nχ_i) (local)

| rows | law/computed (declared: χ from λ₀; computed = δe\*_out) |
|---|---|
| averages, n = 20 exact (Cnn, Cd2, Cstag; 9 rows) | 0.988-1.047 |
| averages, n = 30, 45 DMRG (Cnn, Cd2; 6 rows) | 0.981-1.121 |
| pair labels, n = 20 exact (570 rows) | median 0.999; 570 of 570 in [0.8, 1.25]; extremes 0.993 and 1.244 (one diagonal pair) |
| featured local, n = 20 exact (9 rows) | 0.999-1.000 |
| featured local, n = 30, 45 DMRG (9 rows) | 1.02-1.20 for Ccent, Cfix and Cfar (6, 1); **2.07 and 2.26 for Cfar at (9, 1), (9, 2)** |

- **At n = 20, where everything is exact, the rule is nearly an identity.**
  - Pair labels: 541 of 570 within 0.3 %, 558 within 1 %, and all within [0.8, 1.25]. The 8 rows off by 2-24 % are
    diagonal pairs with large ε_τ (δe\* ≥ 2e-3), where the response is no longer quadratic.
  - The six featured local ladders: 0.999.
  - Averages: within 5 %, even with ε_τ above the gap.
  This replicates the map's finding (IBM heavy-hex: 0-5 % for averages without level crossings) on a different model,
  geometry and label type.
- **The n = 45 outliers are a precision problem, not a failure of the rule** (post-hoc diagnosis, DEVIATIONS 8).
  - The χ = 256 chain states carry an energy offset ≈ δχ (9.5e-4, 2.0e-3). So the λ₀ = 0.1 points sit at ε = 1.1-2.3e-3
    instead of χλ₀²/2 ≈ 1-3e-4, and their label shifts (±0.0025 for Cfar) are comparable to the truncation error of a
    distance-8 correlator.
  - Taking χ from the second chain point of each side (λ ≈ 0.24-0.54, label shift ≈ 10×) leaves Ccent and Cfix
    unchanged (χ₂ = χ_two to 0.2 %). It doubles χ for Cfar at n = 45, and puts the rule **inside the computed DMRG band
    in 9 of 9 rows at n = 30, 45**:

| inst | label | χ_two (λ₀) | χ₂ (2nd points) | ε at λ₀ (+/−) | δe\*_law (λ₀) | δe\*_law (χ₂) | DMRG band [δe\*_out, δe\*_in] | χ₂ rule inside |
|---|---|---|---|---|---|---|---|---|
| (6,1) | Ccent | 0.0478 | 0.0478 | 5.7e-04 / 5.7e-04 | 5.58e-04 | 5.58e-04 | [5.48e-04, 5.93e-04] | yes |
| (6,1) | Cfar | 0.0773 | 0.0889 | 7.6e-04 / 7.5e-04 | 3.45e-04 | 3.00e-04 | [2.97e-04, 3.41e-04] | yes |
| (6,1) | Cfix | 0.0626 | 0.0625 | 6.5e-04 / 6.4e-04 | 4.26e-04 | 4.27e-04 | [4.16e-04, 4.60e-04] | yes |
| (9,1) | Ccent | 0.0579 | 0.0578 | 1.2e-03 / 1.2e-03 | 3.07e-04 | 3.07e-04 | [2.60e-04, 3.71e-04] | yes |
| (9,1) | Cfar | 0.0248 | 0.0462 | 1.1e-03 / 1.1e-03 | 7.17e-04 | 3.85e-04 | [3.47e-04, 4.58e-04] | yes |
| (9,1) | Cfix | 0.0640 | 0.0640 | 1.3e-03 / 1.3e-03 | 2.78e-04 | 2.78e-04 | [2.31e-04, 3.41e-04] | yes |
| (9,2) | Ccent | 0.0602 | 0.0603 | 2.3e-03 / 2.3e-03 | 2.95e-04 | 2.95e-04 | [2.51e-04, 4.30e-04] | yes |
| (9,2) | Cfar | 0.0194 | 0.0384 | 2.1e-03 / 2.1e-03 | 9.16e-04 | 4.63e-04 | [4.06e-04, 5.82e-04] | yes |
| (9,2) | Cfix | 0.0616 | 0.0616 | 2.3e-03 / 2.3e-03 | 2.89e-04 | 2.89e-04 | [2.45e-04, 4.22e-04] | yes |

  The law/out values of 1.18-1.20 for Ccent and Cfix at n = 45 come from the declared outer margin (δG = 3.1e-3 at (9, 1),
  from P2) lowering δe\*_out. The rule sits inside the band in every row. A 20 % test of the rule for local labels at
  n = 45 would need chains with energy offsets ≲ 2e-4 (χ ≳ 512).
- Lesson for the paper's method: for local labels, the two-point χ must be taken where the label shift exceeds the
  numerical noise of the states (here λ ≈ ε_τ-scale fields), not at the smallest field.

## 5. Instance spread (disorder)

| label | n = 20 (three instances, exact) | n = 30 (one) | n = 45 (two) |
|---|---|---|---|
| Cnn δe\* | 0.040 / 0.047 / 0.060 (mean 0.049) | 0.031 | 0.036 / 0.083 |
| Cd2 δe\* | 0.020 / 0.016 / 0.029 | 0.014 | 0.014 / 0.021 |
| Cstag δe\* (record) | 0.010 / 0.012 / 0.015 | — | — |
| Ccent δe\* | 7.3e-4 / 6.0e-4 / 7.4e-4 | 5.5-5.9e-4 | 2.6-3.7e-4 / 2.5-4.3e-4 |
| Cfix δe\* | (= Ccent) | 4.2-4.6e-4 | 2.3-3.4e-4 / 2.4-4.2e-4 |
| Cfar δe\* | 6.4e-4 / 6.8e-4 / 8.1e-4 | 3.0-3.4e-4 | 3.5-4.6e-4 / 4.1-5.8e-4 |
| pair labels, median δe\* | 7.8e-4 / 8.2e-4 / 8.9e-4 | — | — |
| pairs certified at 1e-3 | 56 / 68 / 82 of 190 | — | — |

(DMRG entries give the band [δe\*_out, δe\*_in].)
- For the averages the spread across instances at fixed n is a factor 1.5 (n = 20) to 2.3 (n = 45). It tracks χ, the
  response of the average to a uniform shift of the couplings. (9, 2) also has the largest coupling sum (ΣJ = 84.9
  against 68.8 for (9, 1)); that link is not tested. It does not change the conclusion: every instance certifies Cnn
  with a margin ≥ 3×.
- For the local labels, the spread across instances at fixed n is ≤ 35 %; the size trend dominates.

## 6. Size dependence: the same bond in a growing lattice (Theorem 1)

Instances with the same index k share their first couplings (verified before the hash). So the bond (7, 12) (Cfix) has
identical couplings around it in (4, 1), (6, 1), (9, 1), and likewise in (4, 2), (9, 2).

| family | n = 20 | n = 30 | n = 45 |
|---|---|---|---|
| k = 1: ε_τ (extensive cost, J) | 0.0146 (exact) | 0.0125-0.0138 | 0.0104-0.0154 |
| k = 1: δe\* | 7.3e-4 | 4.2-4.6e-4 | 2.3-3.4e-4 |
| k = 2: ε_τ | 0.0120 (exact) | — | 0.0110-0.0190 |
| k = 2: δe\* | 6.0e-4 | — | 2.4-4.2e-4 |

The energy needed to move this one bond's correlator by ±τ/2 stays ≈ 0.010-0.019 J while n doubles, so δe\* falls ≈ 1/n
(7.3 → 4.2-4.6 → 2.3-3.4 × 10⁻⁴). For the averages, δe\* does not fall: Cnn 0.049 (mean, n = 20) → 0.031 (n = 30) →
0.060 (mean, n = 45).

## 7. Draft figure

`huang_figure.png` (script `code/plot_h.py`, data `laptop_analysis/summary_huang.json`):
- (a) two-sided width / τ vs δe at n = 20 (instance (4, 1), exact);
- (b) the same at n = 45 (instance (9, 1); solid: outer, DMRG-referenced; dashed: inner, rigorous);
- (c) δe\* per label vs n: filled = computed, bar = DMRG band, open = the rule with χ from λ₀;
- (d) δe\* of all 570 pair correlators at n = 20 by class.

The shaded area is the requested range δe ∈ [1e-3, 1e-2].

## 8. Cost and the VM's final state

- **cj-runner-2 (n2-highmem-4):** lastStart 2026-10-31T08:05:18Z → lastStop 11:34:05Z = **3.48 VM-hours ≈ 1.04 EUR**
  at ≈ 0.30 EUR/h list (≈ 1.30 EUR with the program's × 1.25). Cap 6 VM-h respected. Bucket and network < 0.01 EUR.
  The real bill was not read (it arrives with a one-day delay).
- Scheduler 08:10:10Z → 11:18:42Z: 84 tasks, **84 finished, 0 failed, 0 dropped** (two checkpoints, projections 3.04
  and 3.13 VM-h, below the 5.3 drop threshold). Then G4, summary and fetch.
- **Procedure:**
  - `--configuration=sqd-research` only; only cj-runner-2 (cj-runner-1b was RUNNING, another agent's, and was never
    touched);
  - before start: cj-runner-2 TERMINATED, then `cj-poweroff=off`, max-run-duration 6 h with STOP;
  - after boot: `cj-runner@vm2` stopped, no `heavy_run.py`;
  - work only under `/mnt/cj/sandbox/huang_20261031T080637Z/` (tools in `/mnt/cj/sandbox/huang_tools/`); `/mnt/cj/mirror`,
    `prereg/runs`, the queue, the ledgers and `/mnt/cj/venv` untouched (venv used read-only).
- **Sealed ledgers identical at boot (08:06Z) and end (11:31Z):** CODE_FREEZE 133 a54dc944…, DECISION_LEDGER 5
  402ea1a8…, RUN_LEDGER 33 8afbec65…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 58 72fbe2db…; runner inactive.
- **Final state** (`logs_laptop/vm/down.txt`, 11:34Z): **cj-runner-2 TERMINATED**, `cj-poweroff=on`, scheduling
  without max-run-duration or termination action. cj-runner-1 TERMINATED, cj-runner-1b RUNNING (not ours). Lock
  `full_runs/LOCK_cj-runner-2.txt` created at 09:28Z (coordinator's rule) and removed at 11:34:55Z, after TERMINATED.
- Outputs copied to `gs://cj-sqd-research-0f818af9/exploratory/huang_20261031T080637Z/`.

## 9. Deviations (`DEVIATIONS.md`, 9 entries)

1. The `run` SSH call did not return; the laptop process was stopped (no effect).
2. Checkpoint 1: no drop.
3. `code/post_laptop.sh` was written after the hash.
4. Post-hoc same-χ reference sensitivity added to the analysis (`same_chi_ref`; it does not change any declared number).
5. Lock file (coordinator's new rule).
6. Checkpoint 2: no drop.
7. `plot_h.py` edits; two partial read-only snapshots used for development and then deleted.
8. Post-hoc χ₂ diagnostic (§4).
9. VM down and lock removed; G4 ran after the VM-side summary.

None changes a declared rule, threshold or claim outcome.

## 10. What changes for the paper

- **The general rule transfers to the field's canonical benchmark.** Averages of the benchmark's correlators are
  certified by energy alone far beyond δe = 1e-2. Single correlators, which are exactly what the benchmark's ML model
  predicts, are not certified at n = 30-45 anywhere in δe ∈ [1e-3, 1e-2], and their tolerable error falls as 1/n. The
  δe\* law τ²/(8χ) holds within 1 % on 98 % of the exact local rows (all within [0.8, 1.25]) and within 12 % on all
  averages.
- **Correction to our own prior:** at n = 20 the energy does certify about a third of the pair labels at δe = 1e-3
  (mostly second-neighbour pairs with small susceptibility). The honest statement is "per-label, decided by τ²/(8nχ_i)",
  not "no local label is ever certified".

## 11. Re-executed, only compared, not checked

**Re-executed (new computation)**
- On cj-runner-2:
  - ED at n = 20 for three instances (references, 15 featured ladders, 570 pair ladders; ≈ 13,000 Lanczos calls);
  - DMRG references and 21 chains at n = 20 / 30 / 45;
  - gates P2 and P3 (8 tasks);
  - unit tests T1, T3, T4;
  - G4 in a separate process;
  - the VM-side summary.
- Laptop:
  - unit tests T1-T4 (toys);
  - the toy dry run;
  - the data-convention check over all 578 repository instances;
  - the final analysis (`analyze_h.py`, from the fetched outputs);
  - the post-hoc χ₂ diagnostic;
  - the figure.

**Only compared**
- The dataset's own correlators and energies, as a convention gate (G2). At n = 30 and 45 our χ = 384 energy lies
  6.1e-5 / 1.6e-4 / 4.3e-4 above theirs, so their DMRG reached lower energies there.
- The map's law accuracy (§4).

**Not checked**
- A rigorous lower bound on E₀ at n = 30, 45: every CERTIFIED status there is DMRG-referenced (for the averages with
  margins ≥ 3×).
- The size of E₀(384) − E₀^true at n = 45 (no χ = 512 run).
- The law at n = 45 for local labels at the declared λ₀, to 20 %: limited by the χ = 256 chains (§4).
- Pair labels other than the five featured ones at n = 30, 45.
- The repository's license terms beyond the MIT file.
- The real cloud bill.

## 12. Files (all under `J_next_paper/phase3/full_runs/huang/`)

- `DECLARATION.md` (053ceac8…), `DECLARATION.sha256`, `DECLARATION_hash_time.txt`, `DEVIATIONS.md`, `RESULTS.md`,
  `FINAL_SHA256.txt` (code, outputs, figure).
- `code/`:
  - tasks and models: `witness.py`, `lattice.py`, `ed_h.py`, `chain.py`, `hmodel.py`, `indep_eval_h.py`, `g4.py`;
  - analysis and laptop scripts: `analyze_h.py`, `plot_h.py`, `posthoc_chi2.py`, `project_h.py`, `check_data.py`,
    `post_laptop.sh`;
  - unchanged copies: `hull.py`, `sched.py`;
  - `tests/` (`test_huang.py`, `dryrun_h.py`), `vm/` (`vm_h.sh`, `h_vm.sh`).
- `data_huang/`: the six instances' files from the official repository (data only), `provenance/` (SHA-256 of the
  copies and of the clone, the arXiv abstract page).
- `out_20261031T080637Z/`: fetched outputs (`out/`, `OUT_SHA256SUMS.txt` with 1069 files, tar cb3d5b7d…).
- `laptop_analysis/`: `summary_huang.json` (b464fee0…), `tables_huang.md`, `results_tables.md`, `posthoc_chi2.json`,
  `featured_rows_dump.txt`, `LAPTOP_SHA256.txt`.
- `huang_figure.png` (eedf2b5e…).
- `logs_laptop/`: data check, unit tests, dry run, VM logs (up, push, tests, run, g4, summary, fetch, ledgers, down),
  checkpoints.
