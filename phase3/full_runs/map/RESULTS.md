# Certification map (phase 3, full run): RESULTS

**Paper-grade run, declared and hashed before any computation at n ≥ 19** (`DECLARATION.md`, SHA-256
a08178012e860ac49e8b8081ee4386e13f411d70cceaaddb631939451d2f030c, hashed 2026-10-30T02:23:12Z). Batch
20261030T022613Z on cj-runner-1b. Units: J, with H = ¼Σ_edges(XX + YY + Jz ZZ) on `heavy_hex_graph(d)`. No QPU. Every
number comes from `out_20261030T022613Z/` (fetched, every file verified against `OUT_SHA256SUMS.txt`) or from the
laptop re-executions listed in §12. Written 2026-10-30, 14:30-15:30 UTC.

## Resumen en español sencillo

1. Calculamos el mapa completo de garantías para el conjunto de datos de IBM con 57 y 115 cúbits, con las reglas selladas antes de calcular. Usamos 11,96 horas de máquina (unos 7,1 €; 8,9 € con el recargo del programa), dentro del tope de 15. La máquina quedó apagada y los registros sellados no cambiaron.
2. **Resultado positivo (veredicto declarado: MAPA POSITIVO).** El orden magnético y la correlación media entre vecinos quedan garantizados al ±3 % desde Jz ≈ 3,2 con 57 cúbits y desde Jz ≈ 3,1 con 115. Son 29-30 de los 45 puntos de entrenamiento. La garantía se mantiene aunque el error real de IBM fuera 3 veces el que leímos en sus gráficas.
3. Por debajo de Jz = 1,6 y en la zona de prueba fuera del entrenamiento no se garantiza nada, para ningún dato y en los dos tamaños. Esta conclusión se mantiene aunque el error real fuera solo el 4 % del leído.
4. Los datos de un sitio, un enlace o un anillo no quedan garantizados en ningún punto con los márgenes declarados. Con 57 cúbits rozan la línea al final del rango (Jz = 5,5-6: zona gris). Con 115 cúbits el error tolerable se reduce a la mitad (0,496 ≈ 57/115), tal como dice la regla de los datos locales.
5. La correlación a segundos vecinos queda garantizada desde Jz ≈ 4,0 (57 cúbits) y ≈ 3,8 (115).
6. La regla δe* = τ²/(8χ) acierta entre el 0 y el 5 % en 57 de 63 puntos de promedios. Falla para el orden magnético con Jz ≥ 5 (sobrestima el margen hasta 1,8 veces) porque allí aparece un salto de nivel. No cambia ninguna conclusión, porque IBM queda 10-37 veces por debajo.
7. Una segunda lectura independiente de las gráficas de IBM coincide con la primera: el error de energía sale entre 0,93 y 1,02 veces el anterior, y el mapa da lo mismo con las dos lecturas. Los estados testigo son sencillos: con dimensión de enlace 32 ya se obtiene el 97 % del efecto. Además construimos explícitamente un testigo puro.
8. Para no pasar del coste, quitamos en el orden declarado los datos locales de 115 cúbits (salvo Z_bulk en Jz = 4) y los puntos extra de J* con 115. Todas las comprobaciones pasan. Lo positivo sigue dependiendo de la lectura de las gráficas y del cálculo clásico de referencia (el mismo que usa IBM).

---

## 1. Decisions under the declared rules (DECLARATION §4)

| claim | rule | outcome | robustness (fraction of the digitized energy error, reading 1) |
|---|---|---|---|
| **C-A positive map** | m_s and C̄_zz CERTIFIED at every computed Jz ≥ 4.0 at n = 57 and 115, gates pass | **MAP-POSITIVE**: 10/10 (n = 57) and 10/10 (n = 115) rows certified; all gates pass | holds as long as IBM's true error is ≤ **3.06 ×** the digitized one (weakest row: m_s, n = 57, Jz = 4.0) |
| **C-B negative region** | every label NOT CERTIFIED at every Jz ≤ 1.6, both n | **holds** (50 rows, no exception) | holds as long as the true error is ≥ **0.036 ×** the digitized one (weakest: C̄_zz, n = 115, Jz = 1.6) |
| **C-C local labels** | no local row CERTIFIED | **holds** (65 local rows: none certified); **5 rows GRAY** at n = 57: Z_bulk and C_zz(edge) at Jz = 5.5 and 6.0, Z_boundary at 6.0 | the "not certified" local rows hold down to **0.72 ×** (weakest: Z_boundary, n = 57, Jz = 5.5) |
| **C-D δe* rule** | δe*_law/δe*^out ∈ [0.8, 1.25] at every averaged-label point with Jz ≥ 2.0 | **fails at 6 of 63 rows**: m_s at Jz = 5.0, 5.5, 6.0 (n = 57: 1.31, 1.45, 1.63; n = 115: 1.35, 1.63, 1.78); the other 57 rows are within 0.997-1.23 | — |
| **C-E intensivity** | δe*(115)/δe*(57) ∈ [0.67, 1.5] (averages), ≤ 0.75 (local), Jz ≥ 2.0 | **holds**: averages 1.00-1.17 (30 rows); Z_bulk at Jz = 4.0: **0.496** (= 57/115 to 0.1 %) | — |

**Gates** (all pass; details in §11): G1 (n = 19 vs exact diagonalization), P1 (χ = 480), P2 (χ = 320 re-runs of G),
P3 (cold starts), P4 (sector and evaluators, 2680 states), G4 (separate process, 508 headline components). G3
(record only) 66/68 within 10 %.

**Reading of C-A and C-D together.** The positive map is decided by the computed ε_τ, not by the law; the law failure
at m_s, Jz ≥ 5 is in the over-confident direction (it predicts a larger tolerable error than the computed one), but
there IBM's error is 10-37 × below the computed δe*, so no status changes. The cause is visible in the chains: the
"−" side of m_s crosses a first-order level crossing (a jump of ε from ≈ 0.3 J to 13-25 J at n = 115, Jz = 4, λ ≈ 0.22)
before the width reaches τ, so the response is not quadratic there. For C̄_zz (a Jz shift, no crossing) and C̄₂ the
law holds to ≤ 0.3 % at every Jz ≥ 2.

## 2. The map (reading 1; DMRG-referenced outer side, rigorous inner side)

Columns: O_GS = χ = 320 ground-state value; ε_dig = r₁·Δ₁ (training) or 0.012·n (OOD, conditional); w_in(E_lo) =
inner (rigorous) width at the witness-side energy; w_pure = best single stored states (no mixture); w_out(E_up) =
outer width at the certificate-side energy; w_out/τ at E_dig = the map value (below 1: certified to ±3 % at the
central reading); status (§4 rule) under reading 1 and reading 2; f_in, f_out = robustness fractions (ε_τ/ε_dig);
law/meas = δe*_law/δe*^out; ε_dig/Δ_in = window over the in-sector gap; pts = chain points (+, −). Rows dropped by the
cost rule (n = 115 local labels except Z_bulk at 4.0; n = 115 at 3.2/3.4) are absent.

@@MAPTABLES@@

**What the map says.**
- **Averages certify in the Ising part of the range, at both sizes.** m_s and C̄_zz: ratio at E_dig 0.74 (Jz = 3.6) →
  0.21-0.23 (6.0) at n = 57, 0.61-0.64 → 0.13-0.14 at n = 115. C̄₂ (second neighbours) needs larger Jz (ratio 0.98 at
  4.0 at n = 57, 0.79 at n = 115).
- **Near the transition nothing is certified**: at Jz = 1.6 the widths are 5.4-7.6 τ (averages) and 24-36 τ (local
  labels) at n = 57; at the OOD points 1.1-1.4 (conditional floor) 6.5-18 τ (averages) and up to 60 τ (local).
- **Pure-state headline (witness side).** n = 57: Jz = 1.6 m_s ∈ [0.5765, 0.8846] at E_lo, w_in = 0.3081, best stored
  pure states 0.3049; Jz = 1.2 (OOD, conditional) 0.4617 (pure 0.4393). n = 115: Jz = 1.6 0.2958 (pure 0.2607); 1.2
  0.4222 (pure 0.2946). By Toeplitz-Hausdorff every mixture value is attained by a pure state in the span of its two
  components (bond dimension ≤ χ_a + χ_b); this is constructed explicitly in §8, so w_in **is** a pure-state width.
- **Two-sided equality.** The inner and outer widths agree to ≤ 1 % at E_lo in every averaged row with Jz ≥ 1.6 at
  n = 57 (e.g. m_s, Jz = 1.6: 0.3081 vs 0.3091); the information limit is computed, not only bounded.
- **Regime.** At the certified points the window is sub-gap (ε_dig/Δ_in = 0.04 at Jz = 3.6 → 0.01 at 6.0); at Jz = 1.6
  it is 0.58 Δ_in (n = 57) and 1.22 Δ_in (n = 115); at the OOD points up to 1.94 Δ_in (n = 115; the n = 115 χ ≤ 200
  in-sector gaps at Jz ≤ 1.2 are probably over-estimated, see G3 in §11, so these ratios are lower bounds).

## 3. J* per label and size (DECLARATION §4)

@@JSTAR@@

- **m_s and C̄_zz: J* = 3.2 (n = 57) and 3.1 (n = 115) at the central reading; 3.4 and 3.3 with the declared 1.2 ×
  margin.** 29 / 30 of IBM's 45 training points are certified (27 / 28 strict); none of the OOD points. Reading 2 gives
  the same J* (28 / 30 points). The interpolation used between computed Jz was checked at n = 57: ε_τ^out at 3.3
  interpolated from 3.2 and 3.4 differs from the computed one by −0.21 % (m_s) and −0.14 % (C̄_zz), within the declared
  5 %; at n = 115 the 3.2/3.4 points were dropped (cost) and J* uses 3.0/3.3/3.6.
- The map has holes inside the certified range where IBM's own error jumps (e.g. n = 57 at Jz = 3.7, 5.4, 5.7, 5.9,
  where the digitized ratio spikes), which is why the count of certified points is below 45 − (J* − 1.6)/0.1.
- **C̄₂: J* = 4.0 (n = 57), 3.8 (n = 115).**
- **Local labels:** Z_bulk and C_zz(edge) are certified at the central reading only at the last training point
  (Jz = 6.0, ratio 0.99) and never with the declared margins (GRAY); Z_boundary and Z_loop never. See §4.

## 4. Local labels at Jz = 5-6: does any local label ever certify?

- **n = 57: no, with the declared margins.** At Jz = 6.0: Z_bulk ratio 0.991 (f_out 1.02), C_zz(edge) 0.988 (1.03),
  Z_boundary 1.051 (f_in 0.95), Z_loop 1.388 (not certified, f_in 0.52). At 5.5: Z_bulk 1.14, C_zz(edge) 1.14 (GRAY),
  Z_boundary 1.21, Z_loop 1.60. So the bulk site and edge labels reach the ±3 % line exactly at the end of the
  training range: certified only if IBM's error there is not more than 2-3 % larger than read, which the reading
  cannot guarantee (±5 % per factor).
- **n = 115: no (one computed row; the rest dropped by the cost rule).** At Jz = 4.0 Z_bulk is 3.0 τ wide (2.5 τ at
  n = 57), and its δe* is 0.496 × the n = 57 value (the 1/n law: 57/115 = 0.4957). With that ratio, the n = 57 values
  at Jz = 6.0 extrapolate to w/τ ≈ 0.99/√0.496 × (δe_IBM(115)/δe_IBM(57))^{1/2} ≈ 1.3 at n = 115 (an extrapolation by the
  law, not computed).
- In R3's language: local labels lose certifiability linearly in n at fixed per-site error (Theorem 1); the averaged
  labels do not (C-E: δe*(115)/δe*(57) = 1.00-1.17).

## 5. The δe* rule check (law δe*_law = (S/n)·τ²/(8χ), χ from the two λ₀ = 0.005 / 0.1 points)

Full table: `laptop_analysis/tables_map.md` (every computed row). Summary:

| rows | law/measured (ε_τ^out) |
|---|---|
| C̄_zz, all Jz, n = 57 and n = 115 (Jz ≥ 1.6) | 0.997-1.05 |
| C̄₂, all Jz, both n (n = 115 Jz ≥ 1.8) | 0.999-1.07 |
| m_s, n = 57, Jz ≤ 4.0 | 1.00-1.08 |
| m_s, Jz = 4.5 / 5.0 / 5.5 / 6.0 (n = 57; n = 115) | 1.15 / 1.31 / 1.45 / 1.63; 1.22 / 1.35 / 1.63 / 1.78 |
| local labels, n = 57, all Jz ≥ 1.8 | 0.98-1.02 |
| n = 115, Jz ≤ 1.4 (m_s, C̄_zz, C̄₂) | not resolved: ε_τ (≈ 0.003-0.03 J) is comparable to the χ = 160 offset of the chain states (δχ = 0.004-0.012 J); ε_τ^in and ε_τ^out differ by up to 10 × (the inner value is the conservative one used for f_in) |

- **The rule predicts δe* to ≤ 5 % at every point where the field family has no level crossing below ε_τ** (all C̄_zz,
  C̄₂ and local rows, m_s at Jz ≤ 4); it over-estimates δe* by 15-78 % for m_s at Jz ≥ 4.5, where the "−" chains
  cross to a reversed-domain state. The rule's design value τ²/(8χ) should therefore be read as an upper bound to be
  confirmed by the chain where the order is strong.
- At the dataset's own energies the law also predicts the widths: e.g. m_s at n = 57, Jz = 4.0: law 2√(2ε_up χ/S) =
  0.0348 vs computed 0.0351 (as pilot2).

## 6. Robustness to the digitized energies

- Every row carries f_in (the "not certified" conclusion holds for any true error ≥ f_in × digitized) and f_out (the
  "certified" conclusion holds for any true error ≤ f_out × digitized): table in §2.
- Claim level (§1): C-A holds up to **3.06 ×** the digitized error; C-B down to **0.036 ×**; C-C down to **0.72 ×**
  (the GRAY local rows at Jz = 5.5-6.0 are exactly the ones that are not robust in either direction: f between 0.79
  and 1.15).
- **Reading 2** (independent digitization, §7): every row status is the same under readings 1 and 2 except where the
  row is GRAY in one and NOT CERTIFIED or CERTIFIED by < 3 % in the other (see the "status r2" column); J* and the
  claims are identical.

@@DIGITIZATION@@

## 8. Explicit Toeplitz-Hausdorff pure witnesses (R1 item C6; laptop, `code/th_witness.py`)

The two m_s mixture witnesses of the headline point (n = 57, Jz = 1.6, E_lo = E₀ + 0.4990 J) were turned into single
pure states, built as the direct sum α|a⟩ + β|b⟩ of the two stored MPS (`.npz` fetched from the VM, SHA-256 verified),
with (α, β) from the 2 × 2 compression of (H, m_s) to span{a, b}, and re-evaluated with the independent evaluator:

| side | components (λ, χ) | mixture weight of a | ⟨a|b⟩ | pure state: χ | ⟨H⟩ − E_mix | m_s (pure) = m_s (mixture) | sector variance | below E_lo |
|---|---|---|---|---|---|---|---|---|
| min | m_s "−" chain, λ = 0.066484 and 0.074994 (χ = 160 each) | 0.8391 | 0.9749 | 320 | +1.4e-14 J | 0.5764973475 | 0 | yes (by 1.0e-6 J) |
| max | minimal-χ runs, λ = 0.194440 and 0.196557 (χ = 64 each) | 0.2813 | 0.99999 | 128 | −4.9e-13 J | 0.8846001192 | 0 | yes |

So the headline width at this point, 0.5765 → 0.8846 (D = 0.3081), is attained by two explicit **pure** in-sector
states with energy below the witness threshold; the larger of the two has bond dimension 320.

## 9. Minimal-bond-dimension witnesses (R1 item C5)

@@MINCHI@@

- The extremal witnesses are low-entanglement states: at Jz = 1.6 a χ = 32 MPS already gives 97 % of the pure width
  (χ = 16: 85 %, limited by its own ground-energy error of 0.069 J, 14 % of the window); at Jz = 4.0 χ = 16 gives 97 %.
  The "+" side headline witness at Jz = 1.6 (§8) is itself a χ = 64 state. These are the states a modest-χ classical
  or quantum preparation would produce: the windows are not populated only by exotic states.
- The n = 115 minimal-χ point was dropped by the cost rule (DEVIATIONS 5).

## 10. Comparison with the earlier pilots (only compared; `laptop_analysis/compare_pilots.json`)

- **Pilot2 (χ = 320 chains, same thresholds up to the reading's rounding):** every width reproduced to ≤ 1e-3, mostly
  ≤ 1e-4 (e.g. n = 57, Jz = 4.0, m_s at E_up: inner 0.03504 vs 0.03507, outer 0.03508 vs 0.03508; n = 115, Jz = 4.0
  m_s outer 0.02803 vs 0.02802; Z_bulk 0.1903 vs 0.1912). Its cold χ = 320 C̄_zz curve agrees with our Jz-shift chains
  to ≤ 0.005 in width. Ground energies at n = 57 coincide to 1e-9 J.
- **Witness pilot (E_thr = our E_lo):** m_s D(57, 1.6) = 0.3090 vs 0.3081 now; D(57, 1.2) 0.4625 vs 0.4617; D(115, 1.6)
  0.2982 vs 0.2958; local labels at 1.2/1.6 within 0.09 (the pilot's chains were denser at saturation; ours are
  denser at E_lo and ε_τ).
- J* ≈ 3.3 and "≈ 27 of 45 points" of pilot2 (from two Jz values) becomes J* = 3.2 / 3.4 (central / strict) and 29 / 27
  points at n = 57, and 3.1 / 3.3, 30 / 28 at n = 115, now resolved on IBM's 0.1 grid.

## 11. Gates, references and checks (all from `out_20261030T022613Z/out/summary_map.json`)

| gate | result | detail |
|---|---|---|
| **G1** (n = 19 vs exact diagonalization, m_s, C̄_zz, Z_bulk at Jz = 1.6, 4.0) | **pass** | outer width within 0.43 % of exact at E_lo/E_dig/E_up; inner within 0.12 % at E_lo, 0.58 % at E_dig/E_up; ε_τ (inner and outer) within 0.25 % |
| **P1** (χ 320 → 480, n = 57, Jz = 1.2, 1.6, 3.3, 4.0, 6.0) | **pass** | \|ΔE₀\| = 3.5e-6, 2.8e-7, 8.8e-11, 8.7e-12, 1.4e-13 J (limits 0.016-0.0013 J) |
| **P2** (G at χ 160 vs χ 320 at the decisive λ; n = 57, 115; Jz = 3.3, 4.0; m_s, C̄_zz; ±) | **pass** | \|ΔG\| ≤ 9.0e-5 J (n = 115, 3.3, m_s −) against limits 1.2e-3 to 3.4e-3 J; ≤ 4.9e-7 J at n = 57 |
| **P3** (cold starts, m_s ±, same points) | **pass** | F_cold − F_warm ∈ [3e-12, 4.6e-5] J, no warm start stuck |
| **P4** (2680 stored states of the sector) | **pass** | 0 out of sector, variance 0, TeNPy vs evaluator \|ΔE\| ≤ 2.6e-12 J, \|Δm_s\| ≤ 3.9e-12 |
| **G4** (separate process, TeNPy not importable; 508 headline components of m_s and C̄_zz at every Jz, both n, and Z_bulk) | **pass** | \|ΔE\| ≤ 1.8e-12 J, \|Δlabel\| = 0, \|Δnorm\|/norm ≤ 8e-15, variance 0; every mixture and pure witness below its threshold; none missing |
| G3 (record) our S^z = s − 1 gap vs IBM's | 66/68 within 10 % | within ≤ 1 % at every Jz ≥ 1.6 (both readings); n = 115, Jz = 1.1: +20.5 % and 1.2: +6.9 % (our χ ≤ 200 reference is under-converged there; OOD thresholds do not use the gap) |

References: E₀(χ 320) at n = 57 equals pilot2's at every shared Jz to ≤ 1e-9 J; δχ = |E₀(160) − E₀(320)| is
1.3e-4 J (n = 57, Jz = 1.1) → 2e-9 J (4.0) and 1.2e-2 J (n = 115, Jz = 1.1) → 4.1e-6 J (4.0) → 1.8e-7 J (6.0).

## 12. Cloud use, cost, deviations

- **cj-runner-1b:** lastStart 2026-10-30T02:24:12Z → lastStop 14:21:48Z = **11.96 VM-hours** ≈ **7.10 EUR** at
  0.594 EUR/h list (≈ 8.88 EUR with the program's ×1.25); bucket and network < 0.05 EUR. Cap 15 VM-h: respected.
  Real bill: not read (one-day delay).
- Scheduler 02:48:58Z → 14:00Z: 432 planned tasks, **74 skipped by the declared drop order** (DEVIATIONS 4-5),
  **358 finished, 0 failed, none lost** (also across the laptop's network outage, DEVIATIONS 7); ≈ 88 job-hours.
  Measured lab-task times: n = 57 6-17 min; n = 115 25-58 min (chain points at n = 115, Jz ≤ 2.5 run the full 10-sweep
  cap at χ = 160, ≈ 170 s each).
- **Procedure:** `--configuration=sqd-research` only; only cj-runner-1b; `cj-poweroff=off` → start with
  max-run-duration 13 h (STOP); runner `cj-runner@vm` stopped after boot, no `heavy_run.py`; work only under
  `/mnt/cj/sandbox/map_20261030T022613Z/` (tools in `/mnt/cj/sandbox/map_tools/`); `/mnt/cj/mirror`, `prereg/runs`, the
  queue, the ledgers and `/mnt/cj/venv` untouched (venv used read-only).
- **Sealed ledgers identical at boot (02:25Z) and end (14:19Z):** CODE_FREEZE 130 ae45df9d…, DECISION_LEDGER 3
  389a3586…, RUN_LEDGER 13 dc5b8d20…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 30 ca11ff07…; runner inactive, no
  `heavy_run.py`.
- **Final state** (`logs_laptop/down.txt`, 14:22Z): cj-runner-1b **TERMINATED**, `cj-poweroff=on`, scheduling without
  max-run-duration or termination action. cj-runner-1 TERMINATED. cj-runner-2 was RUNNING at the start (another
  agent's) and TERMINATED at the end; I never touched it.
- **Deviations** (`DEVIATIONS.md`, 8 entries): (1) SSH disconnect at the run start, no effect; (2) laptop helper
  `tables_map.py` written after the hash; (3) the 04:24Z checkpoint had no lab time yet, decision deferred to 05:52Z;
  (4) drop order applied: priorities 7, 6, 5 (n = 115 local rows at 5-6, Z_loop, C_zz(edge), Z_boundary); (5) drop
  order continued: priority 4 (n = 115 Z_bulk) **except Jz = 4.0**, the n = 115 minimal-χ point and J* points;
  (6) analysis: ε_τ beyond the computed range used as a lower bound (VM copy patched, hash-logged); (7) laptop network
  outage 12:15-13:47Z, no effect on the run; (8) `getnpz` script fix.

## 13. Re-executed, only compared, not checked

**Re-executed (new computation)**
- 358 DMRG tasks on cj-runner-1b (n = 19, 57, 115; references, 238 lab tasks with 2680 stored sector states, gates,
  minimal χ), unit tests on the VM (7/7, 3/3, 4/4) and on the laptop (4/4), the exact diagonalization gate at n = 19,
  the separate-process re-evaluation of 508 headline components.
- Laptop: the analysis from the fetched outputs (identical in content to the VM's summary), the two Toeplitz-Hausdorff
  pure witnesses (§8), both digitizations (§7), the figure.

**Only compared**
- Pilot2 and the witness pilot (§10); Supp. Fig. 9 against Fig. 2 (§7); the n = 115 local labels at Jz = 5-6 (law
  extrapolation only, §4).

**Not checked**
- That IBM's energies are exact Rayleigh quotients of in-sector states, and their E₀; IBM's error at the OOD points
  (conditional floor) and between the digitized Jz; the real cloud bill.
- A rigorous lower bound on any ground energy at n = 57/115: every outer side (hence every CERTIFIED status) is
  DMRG-referenced (χ = 160 chains with margin 2·δχ, χ = 320/480 references).
- n = 115 local labels other than Z_bulk at Jz = 4.0; n = 115 at Jz = 3.2/3.4; the n = 115 minimal-χ point (dropped).

## 14. Files (all under `J_next_paper/phase3/full_runs/map/`)

- `DECLARATION.md` (a0817801…), `DECLARATION.sha256`, `DECLARATION_hash_time.txt`, `DEVIATIONS.md`, `RESULTS.md`.
- `code/`: `witness.py` (tasks), `analyze_map.py` (analysis, gates, claims), `th_witness.py`, `plot_map2.py`,
  `tables_map.py`, `compare_pilots.py`, `project.py`, `digitize2.py`, `digitize1_pilot_copy.py`, `compare_readings.py`,
  `make_readings.py`, `readings_declared.json`, unchanged pilot2 copies, `tests/`, `vm/`.
- `digitization/`: both readings and their comparison. `vm_in_20261030T022613Z/`: upload tar and hashes.
- `out_20261030T022613Z/`: fetched outputs (`out/`, `OUT_SHA256SUMS.txt`, tar edc16ff1…); bucket copy
  `gs://cj-sqd-research-0f818af9/exploratory/map_20261030T022613Z/`.
- `npz_20261030T022613Z/`: the six `.npz` of the §8 witnesses (verified). Every other `.npz` stays on the VM disk with
  its SHA-256 in the state JSON.
- `laptop_analysis/`: `summary_map.json`, `tables_map.md`, `compare_pilots.json`.
- `th_witness/`: inputs, script and the two pure-witness results.
- `map_figure.png` (draft main-text figure; script `code/plot_map2.py`).
- `logs_laptop/`: instances before, boot, push, VM tests, run start, checkpoints (logs, projections, skip lists), g4,
  VM summary, final fetch, ledgers, shutdown, VM times.


---
Assembled by the coordinator on 2026-10-31 from RESULTS_head.md + RESULTS_body.md (the agent was cut off by a network outage after writing both parts; no content changed; section 7 is absent in the agent's numbering).
