# Learning run (Track 1): RESULTS

**Declared and hashed before any computation at n ≥ 19** (`DECLARATION.md`, SHA-256
e905263ad68733a9bcbbbcfa541b6875650a7041cb2c74d6febabe828b6e330e, hashed 2026-10-31T15:25:10Z). Batch 20261031T152732Z on
cj-runner-1b. Data: the 100 n = 20 instances of arXiv:2106.12627 (official repository, commit 646a1cb2…, read as data
only) and 40 declared out-of-distribution instances. Every number below comes from `out_20261031T152732Z/` (fetched;
849 files verified against `OUT_SHA256SUMS.txt`) and `analysis/` (laptop). Deviations: `DEVIATIONS.md` (6 entries).
Written 2026-11-04.

## Resumen en español sencillo

1. Con los 100 casos de 20 espines del conjunto público, calculamos tres juegos de etiquetas: las exactas, las de un método realista de computador cuántico con error de energía del 0,04 % y del 0,2 %, y las peores que esa misma energía permite. Las reglas se sellaron antes de calcular.
2. El método realista se equivoca casi siempre hacia "menos orden", pero poco: en los promedios, un tercio de lo que la energía permite; en los pares sueltos, menos de una décima.
3. Con esas etiquetas realistas, la garantía estadística usual del 90 % (calibrada con datos del mismo método) sigue cubriendo el valor verdadero entre el 87 % y el 92 %. Las dos apuestas de fallo fuerte salen nulas, y lo decimos así.
4. Pero la energía no descarta el peor caso. Con etiquetas igual de buenas en energía, esa garantía cubre la verdad solo el 82 % (pares) y el 72 % (promedios) con el modelo del artículo, y el 60 % y el 63 % con un modelo mejor, mientras sigue marcando 90 % sobre sus propios datos.
5. La versión certificada, que usa el margen que da la física, cubre la verdad entre el 95 % y el 100 % en todos los casos, sin excepción. Cuesta intervalos entre 1,2 y 2 veces más anchos (hasta 2,5 en el peor caso).
6. La regla para abstenerse que sale de la física (responder solo si el margen heredado de las etiquetas cabe en la tolerancia) responde con el modelo del artículo el 99,8 % de las preguntas sobre promedios y ninguna sobre pares sueltos, como predice la teoría. Su garantía no falló nunca.
7. Fuera de la zona de entrenamiento, con el modelo del artículo todas las garantías fallan en los promedios, incluso con etiquetas exactas: ahí falla el modelo, no las etiquetas. Ordenar las preguntas por el margen certificado no las ordena mejor que la garantía usual; lo que cambia es respecto a qué se garantiza: la verdad o el método.
8. Coste: 7,1 horas de máquina (unos 4-5 €), dentro del tope de 8. Una pausa por el límite de uso dejó la máquina encendida y sin trabajo 2,2 horas; no se perdió ningún cálculo. La máquina quedó apagada y el candado, retirado.

---

## 1. Verdicts under the declared rules (DECLARATION §7; ID test instances, δe = 5e-3, learner M1 unless stated)

| id | quantity | value | declared thresholds | verdict | prior |
|---|---|---|---|---|---|
| **D1** realistic generator, single pairs | Cov_T(SC, nn, gen5) | **0.920** | strong < 0.70, null ≥ 0.85 | **NULL** | null 0.85 |
| **D2** realistic generator, averages | Cov_T(SC, avg, gen5) | **0.909** | same | **NULL** | null 0.6 |
| **D3** energy-valid adversary, single pairs | Cov_T(SC, nn, advL5) | **0.821** | same | **INTERMEDIATE** | null 0.5 |
| D3′ (recorded) same, local learner M2 | Cov_T(SC, nn, advL5; M2) | **0.599** | same | **STRONG** | strong 0.45 |
| **D4** validity of the certified construction | deterministic containments; band checks; Cov_T(CSC), Cov_T(CB) ≥ 0.88 everywhere | all containments hold (0 failures); 0 band violations in 11.1 M checks (both learners); 0 BAND-rule violations; worst certified coverage **0.949** (M1, advL1, CSC, nn) | PASS iff all | **PASS** | 0.95 |
| **D5** width cost | ρ = width(CSC)/width(SC), gen5 | avg **1.60**, nn **1.30** | cheap ≤ 1.5, expensive ≥ 4.5 | avg **MODERATE**, nn **CHEAP** | cheap 0.6 / 0.6 |
| **D6** the derived rule | BAND rule at τ = 0.08, gen5: answer rate on averages / single pairs | **0.998 / 0.000** | confirmed: ≥ 0.9 and ≤ 0.1 | **CONFIRMED** | 0.7 |
| **D7** conformal-based abstention vs truth | e_NC = P(\|f − y_true\| > τ/2 \| NC answers), avg + nn, advL5 | **0.122** (answer rate 6.3 %; its own-label exceedance 0.038) | unsafe ≥ 0.30, safe ≤ 0.10 | **INTERMEDIATE** | intermediate 0.5 |

Reading in one paragraph. A realistic truncated-subspace generator at a matched energy error does **not** break
generator-calibrated conformal coverage of the truth on this benchmark (D1, D2 null): its label bias is one-signed but
small against the learners' own errors. The energy, however, cannot exclude a generator that is as good in energy and
much worse in labels: with such labels (Corollary L witnesses) the standard intervals still report ≈ 90 % coverage of
the labels they were calibrated on, while their coverage of the truth falls to 0.82 / 0.72 (M1, pairs / averages) and
0.60 / 0.63 (M2). The better learner is the more exposed one. The certified intervals keep ≥ 0.95 truth coverage in
every class, label set and learner, at 1.3-1.8× the width (up to 2.5× under the adversary). The abstention rule derived
from the certified width reproduces the certification law (answer averages, abstain on single pairs) with a guarantee
that held in every query.

## 2. Gates

| gate | result | detail |
|---|---|---|
| **G-ED** (100 D instances) | **pass 100/100** | ED residuals ≤ 3.6e-11; \|Σ3J_bC_b − E₀\| ≤ 2.4e-13; E₀ − 2E_file ∈ [−5.4e-6, −8.7e-7] (our ED at or below the dataset's DMRG energy in every instance; max relative 1.1e-7); max \|C_ED − XX_file\| = **6.5e-5** (median 1.2e-5); the file's own max \|XX − ZZ\| = 1.4e-5 |
| G-ED on the brief's "1e-6" | as declared | our ED is exact to < 1e-10 (residual, energy identity); agreement with the dataset's DMRG labels is 1.2e-5 typical, 6.5e-5 worst, i.e. at the dataset's own precision, not 1e-6 |
| G-ED (40 O instances) | pass 40/40 | residuals ≤ 6.3e-11, energy identity ≤ 2.8e-13 |
| **G-GEN** (subspace-energy matching, 140 × 2) | **pass 280/280** | δe_gen/δe ∈ [0.9994, 1.0000]; \|⟨H⟩_ψgen − E_gen\| ≤ 2.1e-13; RR residual ≤ 7.2e-9 |
| **G-CONF** (conformal on a toy with known coverage) | **pass** | split conformal mean coverage 0.9059 vs exact 19/21 = 0.9048 (4000 repetitions); certified variants 0.967 ≥ 0.9 (laptop and VM, identical) |
| G-CONF (learner = sklearn) | pass | M1 and M2 predictions equal sklearn's KernelRidge to 2e-12, cross-validation scores to 7e-16 |
| **G-WIT** | **pass** | T4 (generator), T5 (certified interval ⊇ exact information limit of a 2 × 5 toy, loss ≤ 5.2 %; adversarial and 300 random window states inside) on the VM; D4(a) on all 140 instances |
| Sealed ledgers | identical | CODE_FREEZE 130 ae45df9d…, DECISION_LEDGER 3 389a3586…, RUN_LEDGER 13 dc5b8d20…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 30 ca11ff07… at the first boot, the second boot and the end; runner inactive, no heavy_run.py |

The first D instance reproduces `full_runs/huang/` exactly (Cnn −0.4581, Cd2 0.2266, Cstag 0.2093, bond (7,12) −0.3771).

## 3. The realistic generator and the label bias

Truncated-subspace (SQD-type) Rayleigh-Ritz with ideal samples of the exact ground state, D = the smallest shot-stream
prefix with energy error per site ≤ δe (sector dimension 184 756):

| set | δe | subspace D (min / median / max) | fraction of the sector | captured weight (median) | shots (median) |
|---|---|---|---|---|---|
| D | 1e-3 | 63 382 / 107 589 / 139 791 | 0.34-0.76 | 0.99939 | 2.8e7 |
| D | 5e-3 | 41 027 / 76 292 / 111 170 | 0.22-0.60 | 0.99625 | 4.8e6 |
| O | 1e-3 | 130 061 / 139 317 / 143 563 | 0.70-0.78 | 0.99962 | 3.9e7 |
| O | 5e-3 | 101 411 / 113 186 / 118 736 | 0.55-0.64 | 0.99775 | 9.0e6 |

Label bias, signed toward more antiferromagnetic order, mean over labels and instances (set D):

| class | δe | generator bias | share toward less order | mean \|bias\| | certified half-width | \|bias\| / half-width | adversary shift (less / more) | labels certified at τ = 0.08 |
|---|---|---|---|---|---|---|---|---|
| avg | 1e-3 | −0.0023 | 100 % | 0.0023 | 0.0091 | 0.23 | −0.0091 / +0.0087 | 100 % |
| nn | 1e-3 | −0.0010 | 63 % | 0.0020 | 0.0551 | 0.04 | −0.0546 / +0.0531 | 4 % |
| diag | 1e-3 | −0.0021 | 100 % | 0.0021 | 0.0291 | 0.06 | −0.0306 / +0.0266 | 88 % |
| avg | 5e-3 | **−0.0074** | 100 % | 0.0074 | 0.0204 | **0.35** | −0.0210 / +0.0186 | 100 % |
| nn | 5e-3 | −0.0036 | 63 % | 0.0074 | 0.1228 | **0.06** | −0.1244 / +0.1156 | 0 % |
| diag | 5e-3 | −0.0075 | 100 % | 0.0075 | 0.0653 | 0.10 | −0.0737 / +0.0510 | 12 % |

- **Sign.** On this isotropic model the truncation **weakens** order (all averages and diagonal pairs, 63 % of the
  nn bonds, in every instance). This is the opposite sign to the heavy-hex XXZ over-ordering of `full_runs/method/`;
  the mechanism (the discarded weight sits on specific configurations) is the same, the sign depends on the model.
  The declared primary adversary (advL, toward less order) has the generator's sign.
- **Size.** The realistic bias uses about a third of what the energy allows for averages, and 6 % for single pairs. The
  generator is far from the worst case the energy permits, which is why D1-D2 are null.
- O set (weak relative disorder): the same pattern at about half the size (avg −0.0040, nn −0.0009 at 5e-3).

## 4. Coverage of the true labels (nominal 0.90; 200 random splits 60/20/20; pooled over labels and test instances)

### M1 = the benchmark's learner (model RMSE vs truth, ID: avg 0.017, nn 0.181, diag 0.059)

Truth coverage / coverage of the generator's own labels / mean width. ID = held-out benchmark instances; OOD = region
[1, 2]^31 (truth coverage).

| labels | class | SC (standard) | NC (normalized) | ENS (ensemble) | **CSC (certified)** | CB (certified band) | SC OOD | CSC OOD |
|---|---|---|---|---|---|---|---|---|
| exact | avg | 0.910 / 0.910 / 0.058 | 0.908 | 0.176 | 0.910 | 0.910 | 0.202 | 0.202 |
| exact | nn | 0.905 / 0.905 / 0.613 | 0.904 | 0.158 | 0.905 | 0.905 | 1.000 | 1.000 |
| gen5 | avg | **0.909** / 0.911 / 0.062 | 0.898 | 0.143 | **0.992** / 0.099 | 0.995 / 0.100 | 0.069 | 0.540 |
| gen5 | nn | **0.920** / 0.905 / 0.637 | 0.919 | 0.165 | **0.985** / 0.829 | 0.986 / 0.828 | 1.000 | 1.000 |
| gen5 | diag | 0.924 / 0.905 / 0.220 | 0.923 | 0.156 | 0.996 / 0.371 | 0.996 / 0.364 | 0.987 | 1.000 |
| advL5 | avg | **0.718** / 0.911 / 0.065 | 0.726 | 0.077 | **0.993** / 0.120 | 0.995 / 0.100 | 0.004 | 0.417 |
| advL5 | nn | **0.821** / 0.904 / 0.626 | 0.821 | 0.143 | **0.974** / 0.969 | 0.986 / 0.828 | 0.956 | 1.000 |
| advL5 | diag | 0.795 / 0.905 / 0.263 | 0.788 | 0.093 | 0.994 / 0.358 | 0.996 / 0.365 | 0.627 | 0.999 |
| advM5 | avg | 0.707 / 0.909 / 0.051 | 0.720 | 0.093 | 0.995 / 0.132 | 0.995 | 0.550 | 0.999 |
| advM5 | nn | 0.785 / 0.905 / 0.570 | 0.788 | 0.119 | 0.989 / 0.978 | 0.986 | 0.993 | 1.000 |
| advM5 | diag | 0.669 / 0.904 / 0.149 | 0.671 | 0.129 | 0.996 / 0.488 | 0.996 | 0.992 | 1.000 |
| gen1 | avg / nn / diag | 0.919 / 0.909 / 0.911 | | | 0.976 / 0.956 / 0.968 | | | |
| advL1 | avg / nn / diag | 0.887 / 0.889 / 0.905 | | | 0.966 / 0.949 / 0.972 | | | |

Per label (M1, advL5): Cnn 0.707, Cd2 0.756, Cstag 0.691; nn pairs 0.775-0.877 (87 % of the 31 below 0.85).

### M2 = the local (Lewis-type) learner (model RMSE vs truth, ID: avg 0.016, nn 0.077, diag 0.039)

| labels | class | SC | NC | ENS | **CSC** | CB | SC OOD | CSC OOD |
|---|---|---|---|---|---|---|---|---|
| exact | avg | 0.902 / 0.902 / 0.052 | 0.906 | 0.413 | 0.902 | 0.902 | 0.712 | 0.712 |
| exact | nn | 0.903 / 0.903 / 0.278 | 0.903 | 0.594 | 0.903 | 0.903 | 0.993 | 0.993 |
| gen5 | avg | **0.868** / 0.903 / 0.054 | 0.869 | 0.370 | **0.992** / 0.097 | 1.000 / 0.141 | 0.605 | 0.979 |
| gen5 | nn | **0.915** / 0.904 / 0.297 | 0.914 | 0.613 | **0.993** / 0.539 | 1.000 / 1.054 | 0.993 | 1.000 |
| gen5 | diag | 0.916 / 0.905 / 0.152 | 0.915 | 0.530 | 0.998 / 0.300 | 1.000 / 0.448 | 0.983 | 1.000 |
| advL5 | avg | **0.634** / 0.904 / 0.056 | 0.656 | 0.188 | **0.991** / 0.123 | 1.000 / 0.143 | 0.322 | 0.985 |
| advL5 | nn | **0.599** / 0.903 / 0.292 | 0.572 | 0.198 | **0.989** / 0.716 | 1.000 / 1.052 | 0.746 | 1.000 |
| advL5 | diag | 0.637 / 0.905 / 0.180 | 0.626 | 0.171 | 0.992 / 0.384 | 1.000 / 0.442 | 0.800 | 1.000 |
| advM5 | avg / nn / diag | 0.645 / 0.552 / 0.550 | 0.667 / 0.530 / 0.526 | | 0.997 / 0.995 / 0.999 | | | |
| gen1 | avg / nn / diag | 0.903 / 0.907 / 0.910 | | | 0.972 / 0.972 / 0.981 | | | |
| advL1 | avg / nn / diag | 0.842 / 0.847 / 0.860 | | | 0.967 / 0.967 / 0.973 | | | |

Readings.
1. **Generator-calibrated conformal measures the generator.** In every row its coverage of the generator's own labels
   is 0.90-0.91, as guaranteed. Its coverage of the truth is set by bias / model error: harmless for the realistic
   generator (0.87-0.92), 0.55-0.82 for the energy-valid adversary at δe = 5e-3, 0.84-0.91 at δe = 1e-3.
2. **A better learner is more exposed.** M2 halves the single-pair error (0.077 vs 0.181), so the same label shift
   is a larger fraction of its intervals: D3 0.82 → 0.60. Even the realistic generator moves M2's averages to 0.868.
3. **The uncalibrated ensemble interval is not an uncertainty statement** here: 0.08-0.61 coverage of the truth even
   with exact labels (its intervals are 3-9× narrower than the calibrated ones).
4. **Certified conformal is valid in every row** (0.949-1.000 ID), including the adversarial ones, as (S2) of §6 states.
5. **OOD ([1, 2]^31): covariate shift dominates.** With exact labels M1's standard coverage of the averages is 0.20
   (M2: 0.71); no conformal method is guaranteed there. The certified intervals are wider and cover more (M1 0.42-0.67,
   M2 0.98-0.99 for the averages) but carry no OOD guarantee. Single pairs OOD are covered (≥ 0.95) because their
   intervals are wide and the OOD labels vary less (except M2 under the adversary, 0.75).

## 5. The width cost

| learner | labels | class | width SC | width CSC | **CSC/SC** | width SC with exact labels | **CSC / exact-label SC** |
|---|---|---|---|---|---|---|---|
| M1 | gen1 | avg / nn / diag | 0.060 / 0.620 / 0.209 | 0.076 / 0.711 / 0.272 | 1.27 / 1.15 / 1.30 | 0.058 / 0.613 / 0.204 | 1.30 / 1.16 / 1.33 |
| M1 | gen5 | avg / nn / diag | 0.062 / 0.637 / 0.220 | 0.099 / 0.829 / 0.371 | **1.60 / 1.30** / 1.69 | | 1.69 / 1.35 / 1.81 |
| M1 | advL5 | avg / nn / diag | 0.065 / 0.626 / 0.263 | 0.120 / 0.969 / 0.358 | 1.83 / 1.55 / 1.36 | | 2.06 / 1.58 / 1.75 |
| M2 | gen1 | avg / nn / diag | 0.053 / 0.283 / 0.144 | 0.071 / 0.394 / 0.208 | 1.35 / 1.39 / 1.44 | 0.052 / 0.278 / 0.141 | 1.36 / 1.42 / 1.48 |
| M2 | gen5 | avg / nn / diag | 0.054 / 0.297 / 0.152 | 0.098 / 0.539 / 0.300 | 1.80 / 1.81 / 1.97 | | 1.87 / 1.94 / 2.13 |
| M2 | advL5 | avg / nn / diag | 0.056 / 0.292 / 0.180 | 0.123 / 0.716 / 0.384 | 2.19 / 2.45 / 2.14 | | 2.36 / 2.57 / 2.73 |

- The cost of a truth guarantee is 1.15-1.4× at δe = 1e-3 and 1.3-2.0× at 5e-3 (up to 2.5× when the calibration
  labels are adversarial). It grows as √δe through the certified half-width (§3).
- **In absolute terms the law reappears.** Certified averages are 0.07-0.12 wide (about τ); certified single pairs
  are 0.39-0.97 wide (5-12 τ): for a single pair the truth-guaranteed interval spans most of the correlator range.
- The certified band CB is as narrow as CSC for M1 but much wider for M2 (nn 1.05 vs 0.54): M2's small ridge penalty
  gives it a large label sensitivity ‖a(x)‖₁, which multiplies the training labels' certified widths (§6, S1).

## 6. Abstention

**The learning statements** (two-line proofs; they are what the certified constructions implement).
Instances x exchangeable; true label y*(x); the generator returns y(x) and its energy E(x); the window theory returns
I(x) = [lo, hi] ∋ y*(x), y(x). A learner linear in its labels, f(x) = Σ_i a_i(x) y_i (kernel ridge, ridge on fixed
features; the Huang et al. and Lewis et al. estimators are of this form).
- **(S1) Label-induced error, deterministic.** For every x, in or out of distribution,
  |f(x) − f*(x)| ≤ W(x) = Σ_i |a_i(x)| (hi_i − lo_i) ≤ ‖a(x)‖₁ max_i w_i, with f* the same learner trained on the
  true labels. With the window widths (w ≈ 2√(2χ̄δe) for averages, size-independent; ≈ 2√(2χ_i nδe) for a local label
  until N* = κ/δe), the label-induced error of a linear learner inherits the certification law, scaled by its label
  sensitivity ‖a(x)‖₁. Verified: 0 violations in 11.1 M checks (both learners, all label sets, ID and OOD).
- **(S2) Truth coverage from generator-calibrated data.** Calibrating with s_j = max_{y∈I_j} |f(x_j) − y| ≥ |f(x_j) − y_j*|
  gives P(y*(x) ∈ C(x)) ≥ 1 − α whatever the generator's bias; the standard scores give it for y(x) only.
- **(S3) Selective guarantee.** Answer iff |C(x)| ≤ τ, predict the midpoint: P(answered and |m − y*| > τ/2) ≤ α, so the
  error rate among answers is ≤ α / answer rate.

**The derived rule and its comparison at τ = 0.08** (answer rate / P(|error vs truth| > τ/2 | answered) / same vs the
generator's own labels; ID unless stated).

| learner, labels, class | BAND rule (W(x) ≤ τ) | CB rule (truth-certified) | CSC rule | NC rule (conformal) | SC rule | ensemble rule |
|---|---|---|---|---|---|---|
| M1, gen5, avg | **0.998** / 0.031 / 0.036 | 0.337 / **0.000** / 0.010 | 0.333 / 0.000 | 0.765 / 0.026 / 0.032 | 0.815 / 0.026 | 1.000 / 0.031 |
| M1, gen5, nn | **0.000** | 0.000 | 0.000 | 0.000 | 0.000 | 0.449 / 0.816 |
| M1, gen5, diag | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.995 / 0.557 |
| M1, advL5, avg | 0.995 / 0.142 / 0.044 | 0.337 / **0.000** / 0.011 | 0.225 / 0.009 | 0.709 / **0.122** / 0.038 | 0.773 / 0.125 / 0.040 | 1.000 / 0.143 |
| M1, gen5, avg, OOD | 0.998 / 0.607 | 0.340 / 0.017 | 0.333 / 0.014 | 0.880 / 0.577 | 0.815 / 0.553 | 1.000 / 0.607 |
| M2, gen5, avg | 0.156 / 0.009 | 0.119 / 0.000 | 0.333 / 0.000 | 0.847 / 0.028 / 0.016 | 0.925 / 0.030 | 1.000 / 0.031 |
| M2, advL5, avg | 0.139 / 0.056 | 0.109 / 0.000 | 0.240 / 0.004 | 0.828 / **0.137** / 0.021 | 0.908 / 0.143 | 1.000 / 0.148 |
| M2, gen5, avg, OOD | 0.241 / 0.141 | 0.206 / 0.001 | 0.333 / 0.000 | 0.814 / 0.067 | 0.925 / 0.077 | 1.000 / 0.085 |

- **The derived rule (BAND).** With the benchmark's learner it answers every average and no single pair (D6
  confirmed), and every answer is within τ of what the learner would say with exact labels (S1; never violated, also
  OOD). It does not bound the learner's own error: 3 % of its answers on averages miss the truth by more than τ/2 with
  realistic labels, 14 % with adversarial labels, 61 % OOD. With M2 it answers only 14-16 % of the averages, because
  M2 amplifies label error (‖a‖₁ large): the rule penalizes label-sensitive learners, which a model-error criterion
  cannot see.
- **The truth-certified rule (CB) never erred**: 0.000 exceedance among its answers in distribution in every row
  (bound α / answer rate = 0.30), and ≤ 0.017 OOD. It answers a third of the average queries (M1) at τ = 0.08.
- **Conformal-based abstention is calibrated on the wrong target**: under the adversary its answers miss the truth by
  > τ/2 in 12-14 % of cases while its own-label exceedance is 2-4 % (D7 intermediate: e_NC = 0.122).
- **Risk-coverage curves** (`fig_learning_supp.png` (c, d); `analysis/TABLES.md`, AURC): ranking queries by the
  certified width, the band W(x), the conformal width or the ensemble spread gives **the same curve** within 1-5 %
  (M1, gen5, all queries: AURC 0.0827 CB, 0.0817 BAND, 0.0817 NC, 0.0815 ENS; random 0.139; oracle 0.049). All
  rankings put averages first, then diagonal, then nn pairs. **The certified width does not rank better; it changes
  what the answered set is guaranteed against** (the truth instead of the generator).

## 7. Figure (draft of the new Fig. 1 learner panel)

`analysis/fig_learner_panel.png` (script `code/plot_learn.py`, data `analysis/learn_M1_D_O.json`). Coverage of the true
labels against the mean interval width, learner M1, δe = 5e-3, held-out benchmark instances: averages (circles) and
single pairs (triangles); realistic generator (blue) and energy-valid adversary (orange); open = standard split
conformal calibrated on the generator's labels, filled = certified; × = exact labels; dashed = nominal 90 %, dotted =
tolerance τ. Draft caption (≈ 60 words): *"A learner calibrated on generator labels certifies the generator. Standard
conformal intervals (open) keep 90 % coverage of the truth with realistic labels (blue) but not with labels of equal
energy chosen by the energy-valid adversary (orange). Intervals calibrated through the energy window (filled) cover the
truth in every case; they cost 1.3-1.8× in width, and for single pairs they exceed the tolerance."*
`analysis/fig_learning_supp.png`: (a) the same, (b) for M2, (c, d) risk-coverage curves (M1, all queries).

## 8. What changes for the paper

- **The learning section can now state a result, not a moral:** (S1)-(S3) plus the measured split "realistic
  generator harmless here, energy-valid adversary undetectable by same-generator calibration, certified calibration
  valid at 1.15-2× width". It answers the referee's M6.4 items: windows as interval-valued labels (S1, S2), selective
  prediction with risk-coverage curves against conformal, ensemble and random baselines, OOD queries actually answered
  (by the CB rule, 1-2 % error), and the benchmark's own model class on all 100 n = 20 instances.
- **Report the nulls.** D1 and D2 are null: on this benchmark a realistic SQD-type generator at 0.04-0.2 % energy error
  does not break conformal coverage of the truth. Its bias is one-signed but a third (averages) or 6 % (pairs) of what
  the energy allows. The claim is about what the energy *cannot exclude*, not about what the method does.
- **The sign of the method's bias is model-dependent:** here the truncation weakens order (heavy-hex XXZ: over-orders).
  The paper should not present over-ordering as universal.
- **The derived rule is the certification law in learning form** (answer averages, abstain on single pairs) and it
  rewards learners with small label sensitivity; the referee's "circular" objection does not apply: the rule is not a
  threshold on J_z but a computed quantity per query, and its guarantee holds out of distribution.
- **Do not claim** a better ranking from the certified width (it is not better), or any OOD truth guarantee.

## 9. Cost and the VM's final state

- **cj-runner-1b (n2-highmem-8)**, two boots: 2026-10-31T15:26:10Z → 22:27:00Z (7.01 h; stopped by its own 7-h
  max-run-duration, see DEVIATIONS 4) and 2026-11-04T14:55:52Z → 15:01:13Z (0.09 h). **Total 7.10 VM-h (cap 8)**, of
  which ≈ 2.2 h idle after the scheduler finished (20:15:27Z) because the agent was paused by the usage limit before
  `fetch` and `down`. Estimated ≈ 4.3 EUR at ≈ 0.60 EUR/h list (≈ 5.3 EUR with the program's × 1.25); the real bill was
  not read.
- Scheduler: 280 tasks, **280 finished, 0 failed, 0 dropped** (checkpoint projection 4.3 VM-h; DEVIATIONS 3); the 100
  early D failures of DEVIATIONS 1 were re-run.
- **Final state** (`logs_laptop/vm/down.txt`, 15:01Z): **cj-runner-1b TERMINATED**, `cj-poweroff=on`, no
  max-run-duration and no termination action; cj-runner-1 and cj-runner-2 TERMINATED (not touched). Lock
  `full_runs/LOCK_cj-runner-1b.txt` taken 2026-10-31T15:25:17Z, removed 2026-11-04T15:01:59Z after TERMINATED.
- Work only under `/mnt/cj/sandbox/learning_20261031T152732Z/` and `/mnt/cj/sandbox/learning_tools/`; the venv
  read-only; mirror, prereg/runs, queue and ledgers untouched (ledger hashes identical at both boots and at the end).
- Outputs copied to `gs://cj-sqd-research-0f818af9/exploratory/learning_20261031T152732Z/`.

## 10. Re-executed, only compared, not checked

**Re-executed (new computation).** On the VM: ED of 140 instances (100 benchmark, 40 OOD), the generator at two δe
(280 matched subspaces, 9 451 Rayleigh-Ritz solves in the bisections), 36 367 + 14 100 witness ground states (58 labels × 140 instances × 2 signs),
unit tests T1, T3, T4, T5. On the laptop: unit tests T1-T5, the n = 15 toy dry run, the label tables, both learners
on 200 splits each, the report, the figures.
**Only compared.** The dataset's own correlators and energies (gate G-ED; at the dataset's precision); the first
instance's values against `full_runs/huang/`.
**Not checked.** n = 30 / 45 (no ED; not attempted); the 135 longer-range pairs (no witnesses); noisy or Krylov
sampling in the generator (perfect samples only, the generous case); the notebook's SVR and neural-tangent kernels;
Lewis et al.'s ℓ1 penalty (M2 uses ridge); a re-run of the IBM-dataset learning test (REVISION_PLAN Track 1 "Also";
not in this brief); the real bill.

## 11. Files (all under `J_next_paper/phase3/full_runs/learning/`)

- `DECLARATION.md` (e905263a…), `DECLARATION.sha256`, `DECLARATION_hash_time.txt`, `CODE_SHA256_at_hash.txt`,
  `DEVIATIONS.md`, `RESULTS.md`, `FINAL_SHA256.txt`.
- `code/`: VM side `task_l.py`, `sched.py`, unchanged copies `lattice.py`, `ed_h.py`, `hull.py`; instance draws
  `make_instances.py`, `instances_ood.json` (+ toys); laptop side `labels_l.py`, `models_l.py`, `conf_l.py`,
  `learn_l.py`, `report_l.py`, `plot_learn.py`, `post_laptop.sh`; `tests/test_learning.py`; `vm/vm_l.sh`, `vm/l_vm.sh`.
- `data_huang20/` (500 + 100 data files, provenance in `provenance/`), `patches_20261031T152732Z/` (the SvN tar).
- `out_20261031T152732Z/` (fetched VM outputs, `OUT_SHA256SUMS.txt`, tar 28092d7c…).
- `analysis/`: `learn_M1_D_O.json`, `learn_M2_D_O.json`, `gates.json`, `label_stats.json`, `verdicts.json`,
  `TABLES.md`, `fig_learner_panel.png`, `fig_learning_supp.png`, stdout logs, `ANALYSIS_SHA256.txt`.
- `logs_laptop/`: unit tests, toy dry run, VM logs (up, up2, push, tests, run, fetch, ledgers, down, scheduler log),
  checkpoint.
