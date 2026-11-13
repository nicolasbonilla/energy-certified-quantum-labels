# R2: the constructive half of the witness paper (design, 2026-10-29)

## Resumen en español sencillo (8 líneas)

1. Recomiendo como mitad positiva un «mapa de garantías»: para cada dato del conjunto de IBM y cada valor de Jz, cuánto garantiza de verdad su propia energía. El mismo cálculo da los dos lados (lo que no se puede garantizar y lo que sí) y los dos lados coinciden: la diferencia en el orden magnético es de dos diezmilésimas como mucho.
2. Prueba nueva en la nube con 57 cúbits, con reglas escritas antes de calcular: en Jz = 4 la energía de IBM sí garantiza el orden magnético (±1,8 %) y la correlación media entre vecinos (±1,9 %). En Jz = 3 todavía no (±3,8 %). El cambio ocurre hacia Jz ≈ 3,3: unos 27 de los 45 puntos de entrenamiento quedan garantizados; ninguno de los puntos de prueba fuera de rango.
3. Los datos de un solo sitio o de un solo enlace no quedan garantizados en ningún punto calculado: en Jz = 4 su margen es 2,7 veces demasiado ancho, y con 115 cúbits empeora (3,3 veces), aunque el error por sitio de IBM es menor. Según la regla, solo rozarían el límite al final del rango (Jz = 5-6); falta comprobarlo. El orden magnético, en cambio, mejora con 115 cúbits (±1,5 %).
4. Una regla sencilla predice todos estos márgenes con un error de entre el 1 y el 6 %: el error de energía por sitio que hace falta es τ²/(8χ), y χ sale de dos cálculos con un campo pequeño. Para promedios no depende del tamaño; para datos locales hay que dividirlo por el número de cúbits.
5. Usar las energías de varios Jz a la vez (la idea de Hellmann-Feynman) no aporta nada nuevo: demostré que da exactamente el mismo límite. Además, la energía de IBM en Jz = 1,6 no distingue su estado fundamental del de Jz = 1,2.
6. Medir la varianza de la energía, usar la simetría de la red (solo tiene 2 simetrías) o medir por separado las partes de la energía tampoco ayuda a este tamaño; lo comprobé de forma exacta en sistemas pequeños.
7. Para la parte de inteligencia artificial, el mapa da una regla de qué etiquetas cuánticas son seguras para entrenar y una cota del ruido de cada etiqueta. Es sencillo, pero es el encuadre que el artículo necesita.
8. Coste: 2,25 horas de máquina en la nube (unos 1,3 euros del crédito gratuito, 1,7 con el margen del programa), dentro del tope de 5 horas. La máquina quedó apagada y los registros sellados no cambiaron. El artículo completo con este mapa necesitaría unas 9-11 horas más (unos 6-8 euros). Lo positivo depende de cálculos clásicos de referencia y de la lectura de las gráficas de IBM: conviene que el fundador pida a los autores sus energías exactas.

---

## 0. Bottom line (for the coordinator)

- **Recommended positive result (new candidate A):** the same DMRG chains that give the rigorous witnesses also give a
  DMRG-referenced *outer* bound (Lagrange dual), so every energy-window information limit is computed **two-sided**.
  Run where IBM's own errors are small, this **certifies** the averaged labels: at n = 57, Jz = 4.0 the dataset's
  energy pins m_s to [0.9388, 0.9739] (±1.8 %) and C̄_zz to [−0.9708, −0.9347] (±1.9 %); inner and outer agree to
  10⁻⁴. Declared rule: **POSITIVE** (pilot2, all five gates pass). The boundary is J* ≈ 3.3 for m_s and C̄_zz (≈ 27 of the 45
  training points certified, none of the OOD points); C̄₂ needs Jz slightly above 4; site/edge labels are
  certified at no computed point (2.7× too wide at Jz = 4, 3.3× at n = 115; the law puts them near the line only at
  Jz = 5-6, to be computed).
- It turns the negative half into an equality (the pilot's D values *are* the information limits, to 2 × 10⁻⁴) and
  gives the paper one figure that carries both halves: the certified-label map.
- **Candidate 1 (multi-Jz Hellmann-Feynman):** proved equal to the single-point information limit (Prop. C); C̄_zz is
  ±14-18 % at Jz = 1.6 and certified only for Jz ≳ 3.3; useful as the cheap conjugate row of the map, not as a result.
- **Candidate 2 (law):** δe* = τ²/(8χ) for averages (size-independent), τ²/(8nχ_i) for local labels; predicts every
  measured width to 1-6 % including at ε/Δ_in = 0.72-0.97 where Manchanda's theorems do not apply. The spine of A.
- **Candidates 3-4 (variance, symmetry, side information):** no positive result at scale (exact toy tests + Prop. S +
  |Aut| = 2 for IBM's graphs). One paragraph each.
- **Candidate 5 (AI):** certified label-noise bound and a safe-to-train rule; framing, not a separate result.
- **Cloud:** pilot2 used 2.25 VM-hours on cj-runner-1b (20:54:30Z → 23:09:20Z), ≈ 1.33 EUR list (≈ 1.67 EUR with ×1.25), under the 5 VM-h cap; 84/84 tasks, 0 failed; VM TERMINATED, cj-poweroff=on, max-run-duration cleared; sealed ledgers identical at boot and end. cj-runner-2 was found RUNNING at the end (started 21:18:00Z, not by me; not touched).

## 1. What was done, and the status of every number

- **Read:** the witness pilot (RESULTS, TABLES, DECLARATION, code, every chain JSON), STEP0 §2 and §3.6, phase2 G1
  (G1-1) and G3, the previous pilot's RESULTS (optimality constraints inactive at level 2: not re-proposed).
- **Laptop, toy sizes only** (n ≤ 12, sector dimension ≤ 792, exact dense diagonalization; `toy_tests/toy_r2.py`,
  dc8eb65e…; output `toy_r2_out.json`, ec119941…): T1 conjugate labels, T2 label map + δe*(n), T3 variance, T4
  symmetry. Wall time 45 min on 14 processes, after a first attempt that I stopped (my own processes) because of a
  sampling loop that never ended in T3; fixed (finite sampling, results saved per stage) and rerun in full.
  Note: `hh3_prefix(12)` and `ring_two_pendants(10)` turned out to be isomorphic, so the toy numbers are for one graph.
- **Laptop arithmetic on stored outputs** (no physics computation): the witness pilot's chains re-analysed for outer
  bounds, linear response and the cross-Jz pool (`toy_tests/pilot_reanalysis.py`, ca94b6b1…).
- **Cloud (declared, hashed):** pilot2 on cj-runner-1b, `phase3/design/pilot2/` (DECLARATION.md SHA-256
  7f0d651e0440b70b0a1ac01892eafd4b488046f3b56052545cb607c5a759867a, hashed 2026-10-29T20:33:04Z before any cloud
  action). 84 DMRG tasks at n = 57 and 115. Details in §9.
- **Status labels used below:** *rigorous* (explicit states, exact evaluation; conditional on E_lo ≤ E_dev for
  statements about the dataset), *DMRG-referenced* (needs DMRG ground energies as lower bounds), *exact (toy)*
  (dense diagonalization, n ≤ 12), *only compared*.

## 2. Candidate A (new; recommended): two-sided information limits and the certified-label map

### 2.1 Statement

**Prop. P (one DMRG chain gives both sides).** Let O be a label with field scale S (S = n for m_s, the number of pairs
for a pair average, 1 for a local label), and let φ_σ(λ) be any in-sector state (here: the DMRG ground state of
H − σλS·O) with G_σ(λ) := ⟨H − σλS·O⟩_{φ_σ(λ)}. For every threshold E:
- (inner, rigorous) every φ_σ(λ) and every two-state mixture with ⟨H⟩ ≤ E is a window element (Prop. W of STEP0), so
  the hull of the chain gives w_O(E) ≥ D_in;
- (outer) if G_σ(λ) − δG ≤ E₀(H − σλS·O) (the sector ground energy), then for every λ > 0
  σ·⟨O⟩_ρ ≤ (E − G_σ(λ) + δG)/(λS) for all ρ in the window, hence w_O(E) ≤ D_out;
- (tightness) by strong Lagrange duality (Slater: E > E₀), D_out → w_O(E) ← D_in when the chain's λ brackets the
  point where ⟨H⟩_{φ_σ(λ)} = E and the φ_σ are true ground states.

*Proof.* ⟨H − σλSO⟩_ρ ≥ E₀(H − σλSO) for every sector state ρ; rearrange with ⟨H⟩_ρ ≤ E. Strong duality: the window is
a convex set of density matrices with a strictly feasible point; the Lagrangian maximiser is a ground state of the
shifted Hamiltonian. ∎

The inner side is rigorous at scale (explicit states, exact evaluation, sector checked). The outer side is
**DMRG-referenced**: it needs δG ≥ G_σ − E₀(H − σλSO), estimated by χ = 320 → 480 re-runs and cold-start checks; it
becomes rigorous only with a certified lower bound on the shifted ground energy (ED at n ≤ 19, a relaxation at scale,
whose slack today is comparable to the windows, STEP0 §2.5).

**What it adds to the paper.** (i) The pilot's witness widths are not just lower bounds: they *are* the information
limits (to 10⁻⁴), so the negative half becomes an equality. (ii) The same computation, run where IBM's errors are
small, certifies labels: a positive, constructive statement at the same scale, with the same machinery, which no
referee can call a different paper. (iii) It yields a per-label, per-Jz map of what the dataset's own energy
guarantees, which is the object the AI reader needs (§7).

### 2.2 The witness pilot's chains, re-analysed (laptop arithmetic on the stored outputs; no new computation)

Script `toy_tests/pilot_reanalysis.py` (ca94b6b1…) on `phase3/pilot_witness/out_20261029T173236Z/out` (read-only);
output `toy_tests/pilot_reanalysis_out.json`. Inner = mixture of the chain's bracketing points at E_thr − 10⁻⁶;
outer = Prop. P minimised over the chain's λ (δG = 0 here; the pilot's χ 320 → 480 changes are ≤ 3.5 × 10⁻⁶ J). The
windows are the pilot's E_thr (0.8 × IBM's digitized error; at Jz = 1.2 the declared conditional floor 0.8 × 0.012 per
site).

| n | Jz | label | ε (J) | inner [lo, hi] | outer [lo, hi] | w_in | w_out | w_out − w_in |
|---|---|---|---|---|---|---|---|---|
| 19 | 1.6 | m_s | 0.2280 | [0.4563, 0.8847] | [0.4563, 0.8847] | 0.4284 | 0.4284 | 1.8e-05 |
| 19 | 2.5 | m_s | 0.0836 | [0.8056, 0.9327] | [0.8056, 0.9327] | 0.1271 | 0.1271 | 1.7e-05 |
| 57 | 1.2 | m_s | 0.5472 | [0.3511, 0.8136] | [0.3511, 0.8137] | 0.4625 | 0.4626 | 9.5e-05 |
| 57 | 1.6 | m_s | 0.4993 | [0.5756, 0.8846] | [0.5755, 0.8846] | 0.3090 | 0.3091 | 6.3e-05 |
| 57 | 2.5 | m_s | 0.1987 | [0.8421, 0.9372] | [0.8421, 0.9372] | 0.0951 | 0.0951 | 8.8e-06 |
| 115 | 1.6 | m_s | 1.0692 | [0.5958, 0.8940] | [0.5955, 0.8940] | 0.2982 | 0.2984 | 2.1e-04 |
| 57 | 1.6 | Z_bulk | 0.4993 | [−0.9936, 0.0489] | [−1.0000, 0.0519] | 1.0425 | 1.0519 | 9.4e-03 |
| 57 | 1.6 | Z_boundary | 0.4993 | [−0.2849, 0.9978] | [−0.2871, 1.0000] | 1.2827 | 1.2871 | 4.4e-03 |
| 57 | 1.6 | C_zz(edge) | 0.4993 | [−0.9941, −0.0056] | [−1.0000, 0.0016] | 0.9885 | 1.0016 | 1.3e-02 |
| 57 | 1.6 | Z_loop | 0.4993 | [−0.2103, 0.9881] | [−0.2156, 1.0000] | 1.1984 | 1.2156 | 1.7e-02 |
| 57 | 1.2 | Z_bulk | 0.5472 | [−0.9932, 0.4306] | [−1.0000, 0.4329] | 1.4238 | 1.4329 | 9.1e-03 |
| 57 | 1.2 | Z_boundary | 0.5472 | [−0.6718, 0.9978] | [−0.6725, 1.0000] | 1.6696 | 1.6725 | 2.9e-03 |
| 57 | 1.2 | C_zz(edge) | 0.5472 | [−0.9940, 0.3068] | [−1.0000, 0.3091] | 1.3008 | 1.3091 | 8.3e-03 |
| 57 | 1.2 | Z_loop | 0.5472 | [−0.5313, 0.9879] | [−0.5319, 0.9940] | 1.5191 | 1.5259 | 6.8e-03 |

- **Every information limit of the pilot is now two-sided.** For m_s the inner and outer widths agree to ≤ 2 × 10⁻⁴
  (n = 115, 7-point chains) and ≤ 10⁻⁴ at n = 57; for the local labels to ≤ 0.017 (coarse 7-point chains; saturated
  sides use the spectral cap ±1). At n = 19 the outer side is rigorous (ED gate G1 of the pilot agrees to 1.7 × 10⁻⁵).
- So the headline can be stated as an equality: *the dataset's energy at Jz = 1.6 (n = 57) determines m_s only to the
  interval [0.576, 0.885] and nothing narrower* (inner rigorous given E_thr ≤ E_dev; outer DMRG-referenced).
- Extra (cross-Jz pool): every stored n = 57 state was re-evaluated at H(Jz) from its ⟨A⟩, ⟨B⟩. The window at
  Jz = 1.6 contains the **ground state of the OOD point Jz = 1.2** (E − E₀ = 0.347 J < 0.499 J), and the window at
  Jz = 1.2 contains the Jz = 1.6 ground state (0.302 J < 0.547 J). The dataset's energy at 1.6 cannot tell which of the
  two Hamiltonians the state is the ground state of. (Adding the foreign states changes the m_s widths by 0; it
  widens C̄_zz at 1.6 from 0.197 to 0.222, see §3.)

### 2.3 Pilot2 at n = 57 and 115 (cloud, declared)

Declared rules: `pilot2/DECLARATION.md` (7f0d651e…). Windows: E_lo = E₀ + 0.8·r·min(Δ) (witness side, as in the
pilot) and **E_up = E₀ + 1.2·r·max(Δ) + δχ** (certificate side: contains IBM's energy if the figure reading is within
±5 % per factor and IBM's gap within 10 % of ours). r and Δ_IBM are the digitized values of PRIOR_ART_CHECK §3.
"ratio" = w_out(E_up)/(0.06·|O_GS|): below 1 = the dataset's energy pins the label to an interval of half-width
< 3 % (the pilot's convention); "strict" = w_out/(0.03·|O_GS|) < 1 means the *dataset label itself* is within 3 % of
the ground-state value.

**References (n = 57).** Our S^z = s − 1 gap reproduces IBM's plotted gap at every new point: 1.3436 vs 1.336
(Jz = 3.0), 1.8874 vs 1.883 (4.0), 2.4121 vs 2.395 (5.0), 2.9278 vs 2.905 (6.0), i.e. +0.2 to +0.8 %. This confirms (i)
IBM's "E₁" is the S^z = s − 1 state (now from Jz = 1.2 to 6.0) and (ii) the hidden n = 57 gap markers equal the n = 115
ones, the assumption the pilot flagged. χ 320 → 480 changes of E₀: ≤ 2.7 × 10⁻¹⁰ J at Jz = 3-6.

**Decisive result (declared rule, n = 57, Jz = 4.0, E_up): POSITIVE** (all gates P1-P5 pass).

| n | Jz | label | O_GS | ε_up (J) / δe_up | inner [lo, hi] | outer [lo, hi] | w_out | ratio | strict | w at E_lo | law 2√(2δe χ) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 57 | 3.0 | m_s | 0.9274 | 0.1951 / 3.42e-3 | [0.8864, 0.9573] | [0.8864, 0.9573] | 0.0709 | **1.27** | 2.55 | 0.0575 | 0.0695 |
| 57 | 4.0 | m_s | 0.9585 | 0.1185 / 2.08e-3 | [0.9388, 0.9739] | [0.9388, 0.9739] | 0.0351 | **0.61** | 1.22 | 0.0285 | 0.0348 |
| 57 | 5.0 | m_s | 0.9733 | 0.0695 / 1.22e-3 | [0.9628, 0.9818] | [0.9628, 0.9818] | 0.0190 | **0.33** | 0.65 | 0.0155 | 0.0189 |
| 57 | 6.0 | m_s | 0.9814 | 0.0629 / 1.10e-3 | [0.9739, 0.9875] | [0.9739, 0.9875] | 0.0137 | **0.23** | 0.47 | 0.0111 | 0.0136 |
| 57 | 4.0 | C̄_zz (curve) | −0.9546 | 0.1185 | [−0.9708, −0.9352] | [−0.9708, −0.9347] | 0.0361 | **0.63** | 1.26 | 0.0292 | — |
| 57 | 4.0 | C̄₂ | 0.9247 | 0.1185 | [0.8920, 0.9516] | [0.8920, 0.9516] | 0.0595 | **1.07** | 2.15 | 0.0487 | 0.0595 |
| 57 | 4.0 | Z_bulk (local) | −0.9592 | 0.1185 | [−0.9958, −0.8437] | [−1.0000, −0.8430] | 0.1570 | **2.73** | 5.46 | 0.1292 | 0.1584 |
| 57 | 4.0 | C_zz(edge) (local) | −0.9597 | 0.1185 | [−0.9958, −0.8447] | [−1.0000, −0.8441] | 0.1559 | **2.71** | 5.41 | 0.1284 | 0.1572 |
| 115 | 4.0 | m_s | 0.9610 | 0.1733 / 1.51e-3 | [0.9455, 0.9736] | [0.9455, 0.9736] | 0.0280 | **0.49** | 0.97 | 0.0227 | — |
| 115 | 4.0 | Z_bulk (local) | −0.9592 | 0.1733 | [−0.9958, −0.8139] | [−1.0000, −0.8088] | 0.1912 | **3.32** | 6.65 | 0.1481 | 0.1915 |

(n = 115: our S^z = s − 1 gap 1.8874 vs IBM 1.883; δχ = |E₀(χ 160) − E₀(χ 320)| = 4.1 × 10⁻⁶ J used as the DMRG margin.)

- **Inner = outer.** For m_s the two sides agree to ≤ 4 × 10⁻⁶ in width (pinning (w_out − w_in)/w_out = 1.2 × 10⁻⁴ at
  Jz = 4.0, limit 0.1); for C̄₂ to < 10⁻⁵; for the local labels to 0.005 (their "−" side runs into the spectral cap −1).
- **Where the energy certifies.** m_s and C̄_zz cross the ±3 % line at **J* ≈ 3.3** (log-linear interpolation between
  3.0 and 4.0: 3.33 and 3.31); C̄₂ just after 4.0 (ratio 1.07). The stricter "dataset label within 3 % of the truth"
  holds for m_s from Jz ≈ 4.4 on (ratio 1.22 at 4.0, 0.65 at 5.0). IBM's training grid is 1.6-6.0 in steps of 0.1, so
  **m_s and C̄_zz are energy-certified at ±3 % on about 27 of the 45 training points (Jz ≥ 3.4) and on none of
  the OOD points; site- or edge-resolved labels at no computed point** (2.7× too wide at Jz = 4.0, 3.3× at n = 115).
  Extrapolating the law with χ_Z ∝ Jz⁻³ from the measured χ_Z(4.0) = 0.0265 gives ratios ≈ 1.5 (Jz = 5) and ≈ 1.1
  (Jz = 6) for Z_bulk at n = 57: local labels approach the line only at the very end of the training range, and at
  fixed per-site error they drift up as √n. This must be computed, not assumed, in the full paper.
- **Compared with what IBM offers.** At Jz = 4.0 their Eckart-type bound (Supp. III.1, r = 0.0523) gives trace
  distance ≤ √r = 0.23, i.e. |Δm_s| ≤ 0.46; the label-specific window gives ±0.018: **25× tighter**, from the same
  energy.
- **Law check.** 2√(2δe·χ) with χ from the first two chain points (λ = 0.005) predicts every width in the table to
  ≤ 2 % (local labels: the law slightly exceeds the capped outer width).
- **Regime, honestly.** The certified points are sub-gap and perturbative: ε_up/Δ_in = 0.035 at Jz = 4.0 (0.082 at
  3.0). This is the regime where Manchanda's sandwich applies; what is new is the two-sided computation at 57 qubits on
  a real dataset, the crossing J*, and the averaged/local split at the same energy.

**Gates (all from files in `out_20261029T205557Z/`).** P1: |E₀(χ 320) − E₀(χ 480)| = 8.7 × 10⁻¹² J ≤ 2.4 × 10⁻³.
P2: |G(χ 480) − G(χ 320)| at the decisive λ_lo = 1.4 × 10⁻¹⁴ (+) and 5.1 × 10⁻¹⁰ J (−) ≤ 1.2 × 10⁻³. P3: cold-start
F_cold − F_warm = +8.5 × 10⁻¹⁴ and −9.0 × 10⁻¹³ J, no flag. P4: 71 chain states at Jz = 4.0, sector variance 0,
TeNPy vs in-process evaluator |ΔE| ≤ 5.5 × 10⁻¹³ J, |Δm_s| ≤ 6.9 × 10⁻¹³. P5: separate-process evaluator with TeNPy not importable, on the 4 components of the decisive m_s witnesses: |ΔE| ≤ 3.0 × 10⁻¹³ J, |Δm_s| ≤ 1.2 × 10⁻¹³, |Δnorm|/norm ≤ 4.2 × 10⁻¹⁵, sector variance 0 (limit 10⁻⁸ / 10⁻¹²): pass.

### 2.4 The figure

`pilot2/map_figure.png` (draft, laptop, `code/plot_map.py`): ratio w/(0.06|O_GS|) against Jz on a log axis, for m_s
(n = 57 and 115), C̄_zz (9 digitized Jz), C̄₂ and the local labels; the horizontal line at 1 separates "certified to
±3 %" (below) from "not certified" (above); the OOD window is shaded. It shows in one picture both halves of the paper:
everything above the line at Jz ≤ 3 (the negative half, now as equalities) and the averages dropping below the line
at J* ≈ 3.3 while the local labels stay well above at every computed point (the positive half and its limit).

## 3. Candidate 1: multi-parameter Hellmann-Feynman bracket

**Prop. C (conjugate labels: the information limit is the Legendre bracket of the ground-energy curve).** Write
H(x) = A + xB (A = ¼Σ(XX + YY), B = ¼ΣZZ, x = Jz) in the dataset's sector, E₀(y) its (concave) ground energy. For
E > E₀(x),

  max{⟨B⟩_ρ : ⟨H(x)⟩_ρ ≤ E} = inf_{y<x} (E − E₀(y))/(x − y),  min = sup_{y>x} (E₀(y) − E)/(y − x),

and the extremes are attained by mixtures of **ground states of H(y)**, y = x ∓ μ*. The same holds for every label in
span{A, B} (C̄_xy through H − λ·4A/n_e = c·H(x/c)). *Proof:* H(x) − λB = H(x − λ); Lagrange duality with Slater's
point; the dual optimiser is a ground state of the shifted Hamiltonian. ∎

Consequences, each checked:
1. **The multi-parameter bracket with exact references *is* the single-point information limit; nothing more.** The
   dataset's energies at other Jz′ are upper bounds on E₀(Jz′), and the bracket needs lower bounds there; an upper
   bound at Jz′ never narrows the interval for the truth at Jz. The pilot's 0.20-0.25 movement of C̄_zz "at fixed Jz"
   is therefore not an artefact of ignoring the other Jz: it is (almost all of) the information limit.
2. **The inner witnesses for C̄_zz are the ground states of neighbouring Jz′** (the dataset's own neighbours). Toy
   (n = 12, exact, T1): generic field-on-C̄_zz limit = Legendre outer = curve inner to 10⁻⁵ at Jz = 1.2, 1.6, 2.5, 4.0
   (same for C̄_xy); ground states of Jz′ ∈ [1.04, 2.42] lie inside the Jz = 1.6 window at the dataset's per-site error.
3. **Small-window form:** w(C̄_zz) ≈ (4/n_e)·2√(2εκ) = 2√(8δe|dC̄_zz/dJz|·n/n_e) (κ = |E₀″|); toy: 0.270 vs exact
   0.265 at Jz = 1.6.
4. **At scale it is DMRG-referenced** (needs E₀(Jz′) as lower bounds; we use χ = 320 DMRG with a margin d₀ = 2 × the
   largest χ 320 → 480 change on the curve). Rigorous only at n ≤ 19 (ED) or with a relaxation whose slack g ≪ ε;
   with slack g the width grows to ≈ 2√(2(ε + g)κ)(4/n_e), and today's level-2 slack is of the order of ε itself
   (previous pilot, `pilot/RESULTS.md` §3 finding 4), i.e. ×√2.

**n = 57 numbers.**
- From the pilot's three ground energies only (Jz′ = 1.2, 1.6, 2.5; laptop arithmetic): at Jz = 1.6, C̄_zz ∈
  [−0.878, −0.652] (outer) against [−0.876, −0.654] (inner, cross-Jz pool): **width 0.222-0.227, i.e. ±14 % of
  |C̄_zz^GS| = 0.777, 11 % of the range**. C̄_xy ∈ [−0.960, −0.597] outer, [−0.955, −0.600] inner (width 0.355-0.363).
- From the pilot2 ground-state curve (36 independent cold-start χ = 320 ground states, Jz′ = 0.6-7.2; DMRG margin
  d₀ = 2.0 × 10⁻⁴ J on every E₀(Jz′); inner from the cross-Jz pool of all n = 57 states), at IBM's digitized errors
  (E_up / E_lo as in §2.3; at Jz without our own gap, E₀ + 1.2·r·Δ_IBM + d₀ and E₀ + 0.8·r·Δ_IBM):

| Jz | δe_up | C̄_zz^GS | outer at E_up | inner at E_up | w_out (E_up) | ratio | w_out (E_lo) | C̄_xy^GS | w_out C̄_xy (E_up) | C̄_xy ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.6 | 1.31e-02 | −0.7768 | [−0.8957, −0.6227] | [−0.8956, −0.6244] | 0.2730 | 5.86 | 0.2255 | −0.7905 | 0.4368 | 9.21 |
| 1.8 | 1.08e-02 | −0.8130 | [−0.9094, −0.6875] | [−0.9091, −0.6880] | 0.2219 | 4.55 | 0.1829 | −0.7290 | 0.3994 | 9.13 |
| 2.0 | 9.15e-03 | −0.8420 | [−0.9213, −0.7385] | [−0.9213, −0.7393] | 0.1828 | 3.62 | 0.1512 | −0.6741 | 0.3656 | 9.04 |
| 2.1 | 9.00e-03 | −0.8542 | [−0.9284, −0.7550] | [−0.9283, −0.7572] | 0.1735 | 3.38 | 0.1405 | −0.6490 | 0.3643 | 9.35 |
| 2.5 | 5.25e-03 | −0.8919 | [−0.9390, −0.8317] | [−0.9390, −0.8335] | 0.1073 | 2.01 | 0.0871 | −0.5628 | 0.2683 | 7.95 |
| 3.0 | 3.42e-03 | −0.9222 | [−0.9527, −0.8845] | [−0.9526, −0.8846] | 0.0682 | 1.23 | 0.0556 | −0.4802 | 0.2046 | 7.10 |
| 4.0 | 2.08e-03 | −0.9546 | [−0.9708, −0.9347] | [−0.9708, −0.9351] | 0.0361 | **0.63** | 0.0292 | −0.3688 | 0.1444 | 6.52 |
| 5.0 | 1.22e-03 | −0.9705 | [−0.9796, −0.9596] | [−0.9796, −0.9597] | 0.0200 | **0.34** | 0.0162 | −0.2983 | 0.1001 | 5.59 |
| 6.0 | 1.10e-03 | −0.9793 | [−0.9860, −0.9713] | [−0.9859, −0.9714] | 0.0147 | **0.25** | 0.0119 | −0.2501 | 0.0879 | 5.86 |

  Inner and outer agree to ≤ 0.002 everywhere (to ≤ 0.0005 for Jz ≥ 2.5). The C̄_zz information limit is ±14-18 % of
  the value at Jz = 1.6 and certified at ±3 % only from Jz ≈ 3.3. The XY average (not one of IBM's labels) is never
  certified relative to its value (|C̄_xy| shrinks as 1/Jz while its width shrinks more slowly): ratio 5.6-9.4.

**Verdict.** The Hellmann-Feynman bracket does **not** certify C̄_zz or the XY average to the few-% level at IBM's
errors where it matters (Jz ≤ 2.5); it certifies C̄_zz only where IBM's errors are small (Jz ≳ 3.3, about 27 of
45 training points) and the XY average nowhere (relative to its value). As a statement it is exact and cheap (one ground-state DMRG per Jz′, no witness chains) and it belongs inside candidate A as
the conjugate row of the map. It is not a separate positive result.

## 4. Candidate 2: the device-accuracy law δe*(O)

**Prop. L (exact dual form; intensive law).** For an average O = (1/n)Σ o_i of bounded local terms, define the
per-site curvature functions f_σ(λ) := [E₀(H) − E₀(H − σλ n O)]/n − σλ O_GS ≥ 0 (convex, intensive, f_σ(λ) =
χλ²/2 + O(λ³) with χ = dO/dλ the per-site susceptibility). Then, exactly (Lagrange duality, Prop. P),

  O⁺(δe) − O_GS = inf_{λ>0} [δe + f₊(λ)]/λ,  O_GS − O⁻(δe) = inf_{λ>0} [δe + f₋(λ)]/λ,

so w_O(E₀ + nδe) = 2√(2δe·χ)·(1 + O(√δe)), with the correction set by the per-site third derivative of f, **not by
the gap**. For a local label o_i the same algebra gives w = 2√(2nδe·χ_i) until the reset-channel ceiling (full range
once nδe exceeds the local excitation cost). Design rule:

  **δe*(average) = τ²/(8χ)** (size-independent) and **δe*(local) = τ²/(8nχ_i)** (vanishes as 1/n),

for an interval of width τ (τ = 0.06|O_GS| is the pilot's ±3 %).

**Is it more than Manchanda's Eq. 22?** The leading formula is the same (his χ_O for an average is χ/n and ε = nδe).
What is new and checkable: (i) the *exact* dual form above, two-sided and computable at scale from the same chains;
(ii) his lower bound (Thm 2) needs ε ≤ Δ̄_O/2 and his upper bound a gap, while the intensive expansion needs neither:
the law holds where his theorems do not apply (table below, ε/Δ_in = 0.72 and 0.97); (iii) the 1/n law for local labels
and its ceiling, which he states only qualitatively (asymptotic footnote); (iv) numbers for a real dataset.

**Test 1 (laptop arithmetic on the pilot's chains; χ from the first chain points λ = 0.005, the two signs averaged;
χ from m_s and from the energy agree to ≤ 0.3 %).**

| n | Jz | χ (per site) | ε/Δ_in | δe at window | D_law = 2√(2δeχ) | D (measured, two-sided) | law/measured | δe*_law | δe* (measured) |
|---|---|---|---|---|---|---|---|---|---|
| 19 | 1.6 | 1.722 | 0.24 | 0.0120 | 0.407 | 0.428 | 0.95 | 1.40e-4 | 1.57e-4 |
| 19 | 2.5 | 0.431 | 0.05 | 0.0044 | 0.123 | 0.127 | 0.97 | 8.1e-4 | 8.8e-4 |
| 57 | 1.2 | 2.568 | 0.72 | 0.0096 | 0.444 | 0.463 | 0.96 | 7.2e-5 | 8.0e-5 |
| 57 | 1.6 | 1.198 | 0.46 | 0.0088 | 0.290 | 0.309 | 0.94 | 2.23e-4 | 2.34e-4 |
| 57 | 2.5 | 0.310 | 0.10 | 0.0035 | 0.093 | 0.095 | 0.98 | 1.17e-3 | 1.24e-3 |
| 115 | 1.6 | (1.198, n = 57 value) | 0.97 | 0.0093 | 0.299 | 0.298 | 1.00 | — | — |
| 57 | 3.0 | 0.1766 | 0.082 | 0.00342 (E_up) | 0.0695 | 0.0709 | 0.98 | — | — |
| 57 | 4.0 | 0.0727 | 0.035 | 0.00208 (E_up) | 0.0348 | 0.0351 | 0.99 | — | — |
| 57 | 5.0 | 0.0367 | 0.016 | 0.00122 (E_up) | 0.0189 | 0.0190 | 0.99 | — | — |
| 57 | 6.0 | 0.0210 | 0.012 | 0.00110 (E_up) | 0.0136 | 0.0137 | 0.99 | — | — |
| 57 | 4.0 | C̄₂: dC̄₂/dλ = 0.326 | 0.035 | 0.00208 (E_up) | 0.0595 | 0.0595 | 1.00 | — | — |
| 57 | 4.0 | Z_bulk: 0.0265 (total) | 0.035 | ε = 0.1185 J | 0.1584 | 0.1570 | 1.01 | — | — |
| 57 | 4.0 | C_zz(edge): 0.0261 (total) | 0.035 | ε = 0.1185 J | 0.1572 | 0.1559 | 1.01 | — | — |

(Rows from pilot2, §2.3. For C̄₂ the law reads 2√(2ε·χ/S) with S = 87 pairs; for local labels 2√(2ε·χ) with the
total ε.)

- The law predicts the two-sided width to **2-6 %** at every pilot point (it slightly underestimates: the "−" side
  turns non-perturbative once the opposing field passes λ ≈ 0.05-0.07, pilot §1), and δe* to 5-10 %.
- At n = 115 (ε/Δ_in = 0.97, far outside Manchanda's ε ≤ Δ̄/2) the n = 57 susceptibility predicts D(115) to 0.1 %
  (only compared: no small-λ points at n = 115).
- Practical meaning: **two DMRG runs at a small field (or two device runs with a small staggered field) give the whole
  certification curve D(δe) of an averaged label**, and hence the device accuracy needed.

**Test 2 (toy, exact, n = 8, 10, 12; δe* by bisection of the exact two-sided width; T2 of `toy_r2.py`).**
Graphs: 6-, 8-, 10-rings with two pendants (n = 8, 10, 12; s = 1). δe* = smallest per-site window with exact width
≥ 0.06|O_GS|. Ratio δe*(n = 8)/δe*(n = 12): pure 1/n scaling gives 1.50, size independence 1.00.

| label | Jz = 1.6: δe* at n = 8 / 10 / 12 | ratio 8/12 | Jz = 2.5: ratio | Jz = 4.0: ratio | law vs exact δe* |
|---|---|---|---|---|---|
| C̄_zz (average, conjugate) | 3.21e-4 / 3.10e-4 / 3.03e-4 | 1.06 | 1.07 | 1.07 | ≤ 0.3 % |
| C̄₂ (average) | 8.19e-5 / 6.56e-5 / 5.73e-5 | 1.43 | 1.28 | 1.21 | ≤ 0.4 % |
| m_s (average) | 1.97e-4 / 1.34e-4 / 9.90e-5 | 1.99 | 1.46 | 1.29 | ≤ 1.3 % (7 % at Jz = 4) |
| Z_bulk (local) | 5.01e-5 / 3.76e-5 / 3.00e-5 | 1.67 | 1.53 | 1.50 | ≤ 1 % |
| C_zz(edge) (local) | 7.14e-5 / 5.23e-5 / 4.16e-5 | 1.72 | 1.56 | 1.51 | ≤ 0.3 % |

- Local labels follow 1/n (ratio 1.50-1.72); the conjugate average is size-independent (1.06-1.07).
- m_s and C̄₂ are not yet size-independent at n ≤ 12: their per-site susceptibility is still boundary-dominated
  (χ_s falls from 1.72 at n = 19 to 1.20 at n = 57 at Jz = 1.6). At the dataset's sizes the pilot already measured
  intensivity directly (D(115)/D(57) = 0.965; D(19) vs D(57) within 0.035 at δe = 3 × 10⁻³), so the toy is a test of
  the law, not of the n → ∞ statement for m_s.
- The law reproduces the exact δe* to ≤ 1.3 % in 14 of the 15 (label, Jz) cells (7 % for m_s at Jz = 4, where the
  "−" side is non-perturbative).

**Verdict.** A theorem with numbers, and a design rule that survives far outside the gap regime. It is the
quantitative spine of the positive half (it predicts where the map turns certified), but on its own it reads as
"Manchanda Eq. 22 in extensive form"; it should be presented as Prop. L inside candidate A, not as the headline. Cost:
0 extra (the chains exist).

## 5. Candidate 3: energy variance

**Three distinct statements, three verdicts.**

1. *Device-reported variance V_dev of the dataset state, as an extra window constraint.* It constrains the dataset
   state ψ, not the ground state (whose variance is 0 whatever V_dev is), so it can only enter a certificate of the
   truth through a fidelity bound or by excluding witnesses with larger variance. **Test (toy, exact, n = 12,
   `toy_r2.py` T3):** at the dataset's per-site errors, the extremal m_s witnesses have variance V_w/ε² = 7-12
   (Jz = 1.6), 32-46 (2.5), 164-195 (4.0); SQD-like states with the same energy (lowest eigenvector in a configuration
   subset of 6-15 % of the sector, chosen by |ψ₀|² weight or by sampling |ψ₀|²) have V/ε² = 23-25, 95-104, 397-421.
   **The witnesses have 2-3× less variance than an SQD-type state of the same energy**, so a constraint V ≤ V_dev
   excludes none of them: no narrowing.
2. *Fidelity route* (Weinstein/Temple form, E below the in-sector E₁): 1 − F ≤ V/(E₁ − E)², then
   |O_ψ − O_GS| ≤ range(O)·√(1 − F). For ±3 % on m_s it needs V ≤ 8 × 10⁻⁵, 5 × 10⁻⁴, 2.3 × 10⁻³ J² (Jz = 1.6, 2.5,
   4.0, n = 12); the SQD-like states have V = 0.40-0.44, 0.26-0.29, 0.17-0.18 J², i.e. **80-5000× too large at
   n = 12**, and V is extensive while the in-sector gap is not, so it gets worse with n (at n = 57, Jz = 1.6 the
   window is already 46 % of the in-sector gap, at n = 115 97 %).
3. *The eigenstate second-moment constraint* Tr ρ(H − E)² ≤ (E − L)², which the ground state satisfies for any lower
   bound L ≤ E₀ (a linear, convex addition to the window; no device data). Exact toy result (two-multiplier dual, n = 12):
   with L = E₀ (exact) the m_s window **collapses to the ground-state value** (2ε below the gap leaves only the ground
   state); with slack g = E₀ − L = ½ gap or 1 gap it changes **nothing** (identical to W(E) to 4 decimals); with
   g = 1 % of |E₀| (0.063 J at Jz = 1.6, below ε = 0.131 J) it halves the window ([0.414, 0.869] → [0.582, 0.788]).
   It helps exactly when E₀ is known to better than the gap minus 2ε, i.e. when the ground state could be computed
   anyway. At n = 57-115 the windows are 0.46-0.97 of the in-sector gap, so it would need g ≲ 0.1 J (≈ 0.3 % of |E₀|):
   DMRG-level knowledge, not a certificate.

**Verdict.** No positive result from variance at scale. Worth one paragraph in the paper (it pre-empts the obvious
referee question "why not also measure ⟨H²⟩?"), with the toy numbers. Cost: 0 (done). Not worth a cloud test.

## 6. Candidate 4: symmetry and other cheap side information

**Prop. S (side information about the dataset state does not certify the truth).** Any constraint set for the
ground state that is derived from data on the dataset state ψ (its labels, its variance, separately measured bond
energies, Σ(XX + YY) and ΣZZ separately) has the form W(U) ∩ 𝒢, where U is the best upper bound on E₀ implied by the
data and 𝒢 collects a-priori ground-state properties (sector, symmetry, eigen-equation). The ψ-data enter only through
U, because they are properties of ψ, not of the ground state. *Proof:* the ground state is not ψ; the only bridge from
a property of ψ to the ground state is a variational inequality (U) or a fidelity bound (§5). ∎

What this gives, item by item:
- **Σ(XX + YY) and ΣZZ separately** (= the energy at two Jz). From IBM's own labels, b = ⟨B⟩ = n_e C̄_zz/4 is known,
  so a = E_dev − Jz·b, and every dataset state gives a tangent line ℓ_i(x) = a_i + x b_i ≥ E₀(x) at **every** x. The
  envelope U(x) = min_i ℓ_i(x) can lower the window where a neighbour has a smaller error: excess over E₀(x) ≤
  ε(x_i) + κ(x − x_i)²/2 + |x − x_i|·|b_i − E₀′(x_i)|. At Jz = 1.6 the Jz = 1.8 point (ε = 0.51 J vs 0.62 J) could cut
  the window by at most ≈ 10 %, i.e. D by ≈ 5 %. Needs IBM's labels; small; not a result.
- **The sector** is essential and already used (without it the linear m_s and every ⟨Z_i⟩ is free, pilot/RESULTS §6).
- **Spin flip** maps S^z = s to −s: not a symmetry of the dataset's sector (s = 4.5, 9.5).
- **Marshall sign / stoquasticity** (the ground state is positive in the rotated basis): every diagonal-field witness
  (H − λO with O diagonal) is stoquastic too, so its ground state already has that sign structure. No narrowing for any
  Z-type label (m_s, C_zz, Z_i, Z_loop).
- **Lattice symmetry.** The ground state is in the trivial irrep (Perron-Frobenius), so the window may be restricted to
  symmetric states. Exact toy test (n = 12, reflection, T4): m_s and C̄_zz widths unchanged to 10⁻¹⁴; local Z_bulk
  narrows by ×0.77 / 0.74 / 0.72 and C_zz(edge) by ×0.68 / 0.69 / 0.70 at Jz = 1.6 / 2.5 / 4.0 (→ 1/√2 at small ε: an
  orbit average of two sites). **IBM's graphs have |Aut| = 2** (computed: heavy_hex_graph(5) and (7), one 180°
  rotation; 56/57 and 114/115 sites in orbits of size 2), so symmetry can buy at most ≈ 30 % on local labels and
  nothing at the dataset's saturated local windows.
- **Local energy terms measured separately**: properties of ψ (Prop. S); no effect on the truth beyond U.

**Verdict.** No positive result. Prop. S plus the |Aut| = 2 fact is a useful half-page "why the obvious fixes do not
work" for referees. Cost: 0 (done).

## 7. Candidate 5: the AI angle

**What is substantive.** The map of §2 is, read by an ML user, a *certified label-noise bound*: for a label O at
parameter x, both the dataset state and the ground state lie in the window, so

  |y_O(x) − O_GS(x)| ≤ w_O(E_dev(x))     (y = the dataset's label)

and for any learner f trained on those labels, its error against the inaccessible ground truth satisfies
|f − O_GS| ≤ |f − y| + w_O at every training point (and the risk version: true risk ≤ data risk + sup w_O). This is
elementary (triangle inequality; G1-1 Thm 4), but it turns the paper's object into a **safe-to-train rule**:

> a quantum-generated label O at x is safe at tolerance τ iff w_O(E_dev(x)) ≤ τ, i.e. (to ≤ 10 %, §4)
> δe_dev(x) ≤ τ²/(8 χ_O(x)) for averages, and δe_dev ≤ τ²/(8 n χ_i(x)) for local labels (until the full-range ceiling).

Applied to 2606.15983: IBM's network outputs are site- and pair-resolved (57 ⟨Z_i⟩, 151 C_zz, 4 Z_loop per point at n = 57). **None of those 212 outputs is energy-certified at ±3 % at any Jz we computed** (local widths 2.7× too wide at Jz = 4.0, 3.3× at n = 115; the law puts them near the line only at Jz = 5-6, still to be computed). Their averages are: m_s (derived from ⟨Z_i⟩) and C̄_zz (the mean of the 64 nearest-neighbour C_zz) on Jz ≳ 3.3, about 27 of the 45 training points, and C̄₂ from Jz ≈ 4. In the OOD window nothing is certified. So the honest data-centric statement is "train on the averages in the Ising region; everything else is uncertified label noise of known size", and the size is given by the map.

**What is not substantive (checked, dropped).**
- *Interval-label training* (feeding [O⁻, O⁺] to the network): where the intervals are wide (Jz ≤ 2.5), any sensible
  network is inside them, so there is nothing to learn from them; where they are narrow, they agree with the labels.
  The only shape constraint that is a theorem, C̄_zz(Jz) non-increasing (concavity of E₀), gives one-sided OOD bounds
  that are weaker than the windows themselves (C̄_zz(1.2) ≥ C̄_zz^GS(1.6) ≥ −0.878).
- *Certified OOD audit* of the network (G1-1 Thm 4): at the OOD window the certified width for m_s is 0.46 (n = 57,
  conditional floor), so IBM's "< 3 % OOD" claim cannot be transferred from new device data to the truth by any
  energy-only argument; this belongs to the negative half.

**Verdict.** Keep as the framing paragraph and the data-centric reading of the map (one theorem line, one table:
which of the 5 label families × 45 training points are safe at τ = ±3 %). Not a separate result. Cost: 0 beyond the
map itself.

## 8. Ranked recommendation, the figure, and the cost of the full paper

| rank | candidate | what goes in the paper | rigour at scale | value | extra cost for the full paper |
|---|---|---|---|---|---|
| **1** | **A: two-sided information limits + certified-label map** (with Prop. C and Prop. L inside it) | Main positive result: "the same computation certifies; here is what IBM's energy guarantees, label by label and Jz by Jz". Certified region for averages at Jz ≳ 3.3; local labels not at any computed point; the window equals the information limit | inner rigorous (given E_lo ≤ E_dev); outer DMRG-referenced; certificate also conditional on E_up ≥ E_dev | high: constructive, same scale, same machinery, falsifiable map; turns the negative half into an equality | ≈ 9-11 VM-h ≈ 6-8 EUR (below) |
| 2 | Prop. L, the device-accuracy law | the quantitative spine of rank 1 (predicts J*(O) and the 1/n failure of local labels) | theorem (exact dual form) + numbers | medium alone (Manchanda Eq. 22 in extensive form), high inside rank 1 | 0 |
| 3 | Prop. C, Hellmann-Feynman bracket | the conjugate row of the map; exact and cheap (ground states only) | DMRG-referenced | low alone: equal to the single-point limit, not few-% where it matters | included in rank 1 (the n = 115 curve: ≈ 9 job-h) |
| 4 | AI angle: safe-to-train rule, certified label noise | framing paragraph + one table | follows rank 1 | medium for the AI venue framing; elementary | 0 |
| 5 | Variance; symmetry and side information | one paragraph each, "obvious fixes that do not work" (Prop. S, |Aut| = 2, toy numbers) | exact (toy) | low (pre-empts referees) | 0 |

**The figure** (`pilot2/map_figure.png`, from `code/plot_map.py`): horizontal axis Jz ∈ [1.1, 6]; vertical axis the
two-sided information-limit width divided by 0.06·|O_GS| (log scale; below 1 = certified to ±3 %), at IBM's own
digitized errors. Rows: m_s (n = 57: 1.2, 1.6, 2.5 from the pilot at the 0.8 window; 3.0-6.0 from pilot2 at the 1.2
window; n = 115 at 4.0), C̄_zz from the ground-state curve (9 digitized Jz), C̄₂, Z_bulk, C_zz(edge) (local:
1.2, 1.6, 4.0). OOD window shaded. In the paper it should get a second panel: δe*(O, Jz) from Prop. L against IBM's
δe(Jz), whose crossing gives J*(O) and shows the 1/n drift of the local curves between n = 57 and 115.

**Extra cloud cost for the full positive half** (from pilot2's measured run times: n = 57 chain point ≈ 1.6 min,
ground state ≈ 4.5 min, C̄₂ point ≈ 2.5 min; n = 115 ≈ 3-4× that):
- n = 57: m_s at the 3 missing digitized Jz (1.8, 2.0, 2.1) ≈ 3 job-h; C̄₂ at the 9 digitized Jz ≈ 9 job-h; the 4 local
  labels at 2.5-6.0 ≈ 8 job-h: **≈ 20 job-h**;
- n = 115: references + m_s chains at 9 Jz ≈ 27 job-h; Z_bulk and C_zz(edge) at 4 Jz ≈ 10 job-h; ground-state curve
  (36 points) ≈ 9 job-h: **≈ 46 job-h**;
- total ≈ 66 job-h ≈ **9-11 VM-hours on 8 processes ≈ 5.5-6.5 EUR list (≈ 7-8 EUR with the ×1.25)**, inside STEP0's
  35-50 EUR envelope for the whole paper. No QPU. The single most valuable non-compute step is unchanged: the author
  asks the 2606.15983 authors for the exact energies (removes both reading conditions, the 0.8/1.2 margins, and the
  hidden-gap assumption above Jz = 1.6).

## 9. Pilot2 record (declaration, deviations, cloud use, final state)

- **Declaration:** `pilot2/DECLARATION.md`, SHA-256 7f0d651e0440b70b0a1ac01892eafd4b488046f3b56052545cb607c5a759867a,
  hashed 2026-10-29T20:33:04Z; nothing at n ≥ 19 and no cloud action before. Upload stamp 20261029T205557Z
  (tar 0e9d3ccf…, VM script fabd472c…; 20 files verified on the VM).
- **Deviations (dated, none changes a rule, threshold or number of the declaration):**
  1. 20:31:49Z: the first hash (714482dc…) had the writing time in local time in the header; corrected to UTC and
     re-hashed at 20:33:04Z, before any cloud action (`DECLARATION_hash_time.txt`).
  2. Before upload: `analyze2.py` used the task label n instead of the graph's n for the m_s field scale; harmless at
     n = 57/115, wrong on toy graphs; found by the toy dry run (inner > outer) and fixed. `tests/test_r2.py` grid
     coarsened (0.002 → 0.01) for speed.
  3. 21:02Z: the laptop side of the `run` call was cut by my 120 s timeout; the scheduler was already detached
     (setsid nohup) and kept running (as in the pilot's deviation 8).
  4. 22:10:57Z: concurrent tasks raised from 8 to 10 so that the n = 115 tasks started earlier (operational only).
  5. Interim read-only fetches at ≈ 22:06Z and 22:30Z; the final fetch supersedes them.
  6. Laptop only: `code/plot_map.py` written after the upload.
- **Cloud use.** cj-runner-1b (n2-highmem-8): lastStart 2026-10-29T20:54:30Z → lastStop 23:09:20Z = **2.25 VM-hours**,
  ≈ 1.33 EUR at 0.594 EUR/h list (≈ 1.67 EUR with the program's ×1.25); bucket and network < 0.05 EUR. Cap 5 VM-h
  (declared hard cap 4.5): not approached, nothing dropped. 84 tasks, 0 failed (scheduler 21:00:59Z → 23:03Z);
  13.3 job-hours on 8-10 processes. Measured per-step times: n = 57 ground state (χ 160 → 320, from Néel) 4.2-10 min
  (10 min near Jz′ = 0.6-1.0), chain point 1.5-2 min (C̄₂ 2.5-3 min), χ = 480 continuation 5-13 min; n = 115 χ 160 stage 10.6 min,
  χ 320 stage 11.2 min, S^z − 1 run 18.7 min, chain point 2.3-5.5 min.
- **Procedure followed** (the pilot's `code/vm/`, copied): `--configuration=sqd-research` only, cj-runner-1b only;
  `cj-poweroff=off` then start with max-run-duration 8 h (STOP); after boot `systemctl stop cj-runner@vm`, no
  `heavy_run.py`; work only under `/mnt/cj/sandbox/r2p2_20261029T205557Z/` (tools `/mnt/cj/sandbox/r2p2_tools/`);
  `/mnt/cj/mirror`, `prereg/runs`, the queue, the ledgers and `/mnt/cj/venv` untouched (venv used read-only).
- **Sealed ledgers** identical at boot (20:55Z) and at the end (23:07Z): CODE_FREEZE 130 ae45df9d…, DECISION_LEDGER 3
  389a3586…, RUN_LEDGER 13 dc5b8d20…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 30 ca11ff07…; runner `inactive`,
  no `heavy_run.py`.
- **Final state** (`logs_laptop/down.txt`, 23:09:55Z): `instances list` shows **cj-runner-1b TERMINATED**,
  cj-runner-1 TERMINATED; `cj-poweroff=on`; scheduling shows no max-run-duration or termination action.
  **cj-runner-2 was RUNNING** (lastStart 21:18:00Z, i.e. started during this run by someone else; it was TERMINATED in
  my listing at 20:52Z). I did not start, stop or touch it; the coordinator should check who started it.
- **Fetched** outputs: `out_20261029T205557Z/` (tar bb3e9cfb…, every file verified against OUT_SHA256SUMS.txt) and a
  copy in the bucket. MPS `.npz` files stay on the VM sandbox disk with their SHA-256 in the records.

## 10. Re-executed, only compared, not checked

**Re-executed (new computation)**
- Pilot2 on cj-runner-1b: 84 DMRG tasks (n = 57: references at Jz = 3.0, 4.0, 5.0, 6.0; 36-point ground-state curve;
  m_s chains at 3.0-6.0; C̄₂, Z_bulk, C_zz(edge) chains at 4.0; cold-start and χ = 480 checks at 4.0. n = 115 at 4.0:
  references, m_s and Z_bulk chains). Unit tests on the VM (7/7 of the pilot, 3/3 new), separate-process evaluator.
- Laptop, exact toy diagonalization (n ≤ 12): conjugate-label identity (T1), the label map and δe*(n) at n = 8-12
  (T2), variance (T3), symmetry (T4); new unit tests (3/3); a full end-to-end dry run of the pilot2 plan on toy graphs
  (84/84 tasks, gates and separate-process check pass; no number from it is used).
- Laptop analysis of the fetched pilot2 outputs (`analyze2.py`), identical to the VM's summary (chain-label widths identical to 0 and the same decision; the laptop run adds the witness pilot's states to the conjugate cross-Jz pool, which only widens the C̄_zz/C̄_xy inner sides by ≤ 0.004).

**Only compared (arithmetic on stored outputs, not recomputed)**
- The witness pilot's chains: outer bounds, linear-response χ, cross-Jz pool, 3-point Legendre bracket (§2.2, §3, §4).
- The law at n = 115, Jz = 1.6 with the n = 57 susceptibility (no small-λ points at n = 115).
- IBM's digitized ratios and gaps (PRIOR_ART_CHECK §3); IBM's Eckart bound at Jz = 4.0 from their formula.

**Not checked**
- That IBM's reported energies are exact Rayleigh quotients of in-sector states, and the figure reading itself: the
  positive certificate needs E_dev ≤ E_up (reading within ±5 % per factor, gap within 10 %), the witness statements
  need E_lo ≤ E_dev. Both disappear if the authors send their energies.
- A rigorous lower bound on any ground energy at n = 57/115: every outer side here is DMRG-referenced (χ = 320,
  χ = 480 changes ≤ 10⁻⁴ J on the curve, ≤ 5 × 10⁻¹⁰ J at the decisive λ).
- IBM's error between the digitized Jz (the map interpolates between 3.0 and 4.0 for J*), and at the OOD points.
- The C̄₂ and local labels at Jz ≠ 4.0 in pilot2 (only the pilot's 1.2 and 1.6 exist), m_s at 1.8-2.1, n = 115
  outside Jz = 1.6 and 4.0; the eigenstate second-moment constraint at scale (toy only); interval-label training of
  an actual network.
- The real Cloud bill (one-day delay).

## 11. Files

All under `J_next_paper/phase3/design/`.
- `R2_constructive_half.md` (this file).
- `toy_tests/`: `toy_r2.py` (dc8eb65e…), `toygraphs_copy.py` (copy of the pilot's patched test helper, only its path
  constant changed), `graphs/hh_d3.json` (d8d42f5f…), `toy_r2_out.json` (ec119941…), `toy_r2_log.txt`, `pilot_reanalysis.py`
  (ca94b6b1…), `pilot_reanalysis_out.json` (1fd54ecb…), `pilot_reanalysis_log.txt`.
- `pilot2/`: `DECLARATION.md` (7f0d651e…), `DECLARATION.sha256`, `DECLARATION_hash_time.txt`; `code/` (copied from the
  witness pilot, changes marked "R2": `witness.py`, `hhmodel.py` (+C2_bar), `analyze2.py`, `tests/test_r2.py`,
  `tests/dryrun_toy.py`, `vm/vm_r2p2.sh`, `vm/r2p2_vm.sh`, laptop-only `plot_map.py`); `wheels/` (the pilot's TeNPy
  1.1.0 wheel, 890b6d42…); `vm_in_20261029T205557Z/` (upload tar, EXPECTED.sha256, UPLOAD_SHA256.txt);
  `out_20261029T205557Z/` (fetched outputs, 540 files listed in OUT_SHA256SUMS.txt, 18707e53…, all verified);
  `summary2.json` (a01b69d2…, laptop analysis incl. the witness pilot's states in the conjugate pool);
  `map_figure.png` (3090ab6c…); `logs_laptop/` (instances before, boot, push, VM tests, run, separate-process check,
  VM summary, final fetch, ledgers, shutdown, VM times, the cj-runner-2 observation).
- Bucket: `gs://cj-sqd-research-0f818af9/exploratory/r2p2_20261029T205557Z/` (fetch copies).
- Nothing in `phase3/pilot_witness/` was modified (read-only use; code copied).
