1. Pregunta: ¿el error del método de IBM hacia "más orden magnético" sigue ahí con 115 cúbits, de dónde sale, y cuánto valdría con la energía que IBM publica? Respuesta: sigue, es mayor con 115 cúbits, y sale de quedarse con un número limitado de configuraciones, no del ruido del chip.
2. Copia del método, con el presupuesto publicado: en Jz = 1,2 el orden sale 0,26 más alto que el real con 57 cúbits y 0,30 con 115. Todos los sitios (57 de 57 y 115 de 115) y todas las correlaciones salen con más orden.
3. La regla sellada sobre 115 cúbits quedó "sin decisión": sin el último paso de mejora de IBM, nuestra copia tiene unas 5,6 veces más error de energía que los datos de IBM y no pasa el control. En Jz = 1,2 con 115 cúbits, las otras lecturas dan +0,15 (a partir del error publicado por IBM) y +0,30 (nuestra copia): ninguna baja de 0,05.
4. La causa: tomando muestras perfectas del estado verdadero, con el mismo número de configuraciones, sale el mismo error (+0,258 frente a +0,259). El ruido del chip lo aumenta (+0,32) y la "recuperación" de cadenas ni lo crea ni lo corrige. Con las mismas muestras, el simple promedio da el valor correcto: el error lo produce el paso de diagonalizar dentro de las configuraciones vistas.
5. ¿Desaparece con más configuraciones? Casi no: con 57 cúbits pasa de 0,24 a 0,22 al multiplicar por 4,3 las configuraciones; con 115, 800 mil configuraciones recogen solo el 0,2 % del estado y el error queda en 0,31.
6. El último paso de mejora de IBM, tal como está escrito, no mejora nada en ninguna de sus variantes. Dos variantes no escritas sí reproducen su ganancia de energía (80-88 % del error eliminado, frente al 85 % de IBM), y entonces el estado físico cae sobre la misma curva "error frente a energía". Leído en la energía que IBM publica, el exceso de orden es de +0,08 a +0,09 en Jz = 1,6 y de +0,02 a +0,03 en 2,5 (57 cúbits); en la zona de prueba (Jz = 1,1-1,4), de +0,10 a +0,18.
7. Esos estados están entre el 45 y el 96 % del máximo orden que su energía permite. Un modelo entrenado con esos datos acierta los datos nuevos del mismo método (<1 %) y falla un 39-42 % frente a la referencia con 57 cúbits y un 44-45 % con 115; el "vecino más cercano" también aprueba esa prueba. Una regla que se abstiene por debajo de Jz = 3,3 responde un 27-29 % de las preguntas con un error máximo del 1-2 %.
8. Coste: 7,51 horas de máquina en cj-runner-2 (unos 2,23 euros). La máquina quedó apagada y los registros sellados no cambiaron. Hablo de la familia de métodos y de las figuras de IBM; no digo que sus datos estén mal.

---

# Full method runs: label bias of the SKQD-type method class at n = 57 and n = 115 (2026-10-30)

Rules: `DECLARATION.md` (SHA-256 c1fd71e1d72085f4f46fcc7ce8938d147997242ef7114275621ce111ba079999, hashed
2026-10-30T00:20:14Z, before any computation on the target model at n ≥ 19). Deviations: `DEVIATIONS.md`. All numbers
come from `out_20261030T003230Z/` (VM outputs, 0 files failing their SHA-256) and `laptop_post/` (summary, learning
test, tables computed on the laptop from those files). Generated tables: `laptop_post/results_tables.md` and
`laptop_post/out/TABLES.md`. Every statement below is a property of the **emulated method class** under the declared
assumptions, or a reading of the dataset paper's own published figures (named as such). None is a statement that the
labels of arXiv:2606.15983 are wrong.

## 0. What was done, what it cost, what was checked

- **Cloud:** cj-runner-2 only (n2-highmem-4, lane vm2, europe-west3-b). Started 00:29:41Z, stopped 08:00:33Z:
  **7.51 VM-hours ≈ 2.23 EUR** (cap 12 VM-h). 100 tasks, **0 failed, no patch**. Final state in §9.
- **Laptop:** unit tests (17), two toy dry runs (12-site; 70-site heavy-hex fragment for the two-word code path, after
  the hash), the learning test, tables and figures.

| Status | Items |
|---|---|
| **Re-executed** | Unit tests on the VM (17/17: pilot3's 8 plus 9 new against dense algebra and exact MPS contraction); all references (25 DMRG, 8 gaps), 13 fresh Krylov runs (n = 115 at 11 Jz; n = 57 at Jz 1.2, 2.5), the calibrations, 25 emulations, 7 ground-state scans, 3 basis-optimization tasks, 5 "+" chains; summary, learning test and figures on the laptop from the fetched, hash-verified outputs |
| **Reused (hash-verified copy)** | pilot3's raw n = 57 Krylov samples at the 12 other Jz (`out/p3_import.txt`: 14 files, hashes equal to the source) |
| **Only compared** | IBM's digitized energy ratios and gaps (Fig. 2, Supp. Fig. 9; ±5 %), Supp. Fig. 11 ΔZ / ΔC_zz (±1 point), the in-sector and unique bitstring counts quoted in their Methods |
| **Not checked** | IBM's raw data and labels; their basis-optimization code (§4); Trotter circuits and device noise (replaced by exact evolution and an i.i.d. bit-flip model); basis optimization at n = 115 (64-bit code); DMRG beyond χ = 320 at n = 115 (χ = 200 → 320 changed E₀ by 6.5e-3 J at Jz = 1.1 and 4.6e-3 J at 1.2; pilot3's χ = 200 m_s at 1.1 differs by 1.5e-3 from today's χ = 320 value); the real bill |

## 1. Decisions under the declared rules

| Gate | Result |
|---|---|
| G1 unit tests on the VM | **pass** (5 files, 17 tests) |
| G2 references vs the witness pilot | **pass**: n = 57 at 1.2 / 1.6 / 2.5: |ΔE₀| ≤ 3.2e-5 J, |Δm_s| ≤ 4.5e-5; n = 115 at 1.6: |ΔE₀| = 3.2e-6 J, |Δm_s| = 2.3e-5 |
| G3(57) energy | **pass**: ratio 0.395 vs IBM 0.235 (2.5), 0.0415 vs 0.0523 (4.0) |
| G4(57) C_zz | **pass**: 5.69 % vs 3.4 % (2.5), 0.78 % vs 1.4 % (4.0) |
| **G3(115) energy** | **fail**: ratio 2.60 vs IBM 0.464 (2.5, ×5.6), 0.452 vs 0.0765 (4.0, ×5.9) |
| **G4(115) C_zz** | **fail**: 11.4 % vs 2.9 % (2.5); 4.0 recorded: 2.75 % vs ≈ 0.5 % |
| G5 sampling states | all compressed states passed (fidelity ≥ 0.9984, |Δm_s| ≤ 1e-4; χ_s = 128 at n = 57, 160 at n = 115) |
| Krylov truncation (flag > 1e-6 per step) | flagged at n = 115, Jz 4.0 / 5.0 / 6.0 (max 2.0e-6, 1.9e-6, 2.8e-6); all others ≤ 9.2e-7 |

| Decisive quantity | Value | Rule | Verdict |
|---|---|---|---|
| **D1** (plan's headline guard) | Q1 = Δm_s(n = 115, Jz = 1.2, primary) = **+0.301**; Q2 = Δm_s at IBM's energy at n = 115, Jz = 1.6 = **+0.114 (extrapolated 4.5× in r beyond the sampled range)** | KEEP needs Q1, Q2 ≥ 0.05 and G3/G4(115) | **NO DECISION** (G3(115), G4(115) fail) |
| **D2** mechanism share, n = 57, Jz = 1.2 | M = 0.258 / 0.259 = **0.997** (n = 115: 1.05, recorded) | ≥ 0.7 | **TRUNCATION-DOMINATED** |
| **D3** vanishing with D, n = 57, Jz = 1.2 | V = Δm_s(3.16×10⁶) / Δm_s(10⁶) = 0.218 / 0.239 = **0.91** | ≥ 0.6 | **PERSISTENT**, flagged "D_max short" (3.16×10⁶ < 8×10⁶: the declared 80-min sampling cap was reached) |
| **D4** basis optimization, n = 57, Jz = 2.5, dev_rec | best stated-circuit f = **0.000** (all six variants, θ_rms ≤ 1.6e-6) | REPRODUCED needs f ≥ 0.5 | **NOT REPRODUCED** (alternatives, not used for D4: f = 0.80, 0.88; IBM's own 0.85) |

**What the D1 outcome means.** The gate did its job: without the dataset's final step, the published shot budget at
n = 115 gives states 5.6-5.9× further from the ground energy than IBM's labelled states, so the n = 115 emulation does
not represent the dataset's quality and Q1 cannot be used for the plan's cut rule. The readings that do not depend on
that match all exceed the 0.05 line at n = 115 but are estimates, not a declared decision: ΔZ-matched (§5)
+0.146 (Jz 1.2), +0.105 (1.4), +0.077 (1.6); r-interpolated +0.114 at 1.6 (far extrapolation). The headline decision
at n = 115 therefore rests on the author's reading of these estimates, or on IBM's labelled data.

## 2. Bias tables (signed, published shot budget)

Primary variant = 10⁶ shots, 1 % flips, random-flip recovery, labels of the subspace ground state (p* = 0 at both n:
even the 1 % floor is above IBM's dataset energy, the declared fallback, as in pilot3). Full tables with all variants:
`laptop_post/results_tables.md`, `laptop_post/out/TABLES.md`.

| Jz | n = 57: Δm_s | ΔZ % ours / IBM | ΔC_zz % | ΔZ_loop % | n = 115: Δm_s | ΔZ % ours / IBM | ΔC_zz % | ΔZ_loop % |
|---|---|---|---|---|---|---|---|---|
| 1.1 | **+0.301** | 53.6 / 31.6 | 70.1 | 108.6 | **+0.343** | 58.5 / 29.8 | 86.0 | 129.5 |
| 1.2 | **+0.259** | 42.4 / 26.0 | 56.1 | 83.1 | **+0.301** | 47.5 / 23.0 | 70.3 | 102.3 |
| 1.3 | +0.222 | 34.0 / 21.8 | 45.5 | 65.4 | +0.264 | 39.2 / 18.5 | 58.3 | 82.7 |
| 1.4 | **+0.190** | 27.5 / 16.9 | 37.0 | 52.0 | **+0.232** | 32.8 / 14.8 | 48.9 | 68.0 |
| 1.6 | **+0.139** | 18.6 / 10.6 | 25.2 | 34.2 | **+0.181** | 23.6 / 10.0 | 35.4 | 47.9 |
| 2.0 | +0.076 | 9.2 / – | 12.7 | 16.6 | +0.114 | 13.5 / – | 20.4 | 26.7 |
| 2.5 | **+0.036** | 4.1 / 2.2 | 5.7 | 7.3 | **+0.067** | 7.5 / 2.0 | 11.4 | 14.6 |
| 3.0 | +0.018 | 1.9 / – | 2.7 | 3.4 | +0.042 | 4.5 / – | 6.8 | 8.6 |
| 4.0 | **+0.005** | 0.5 / 0.5 | 0.8 | 1.0 | **+0.017** | 1.8 / 0.4 | 2.8 | 3.4 |
| 6.0 | +0.001 | 0.1 / – | 0.2 | 0.2 | +0.004 | 0.4 / – | 0.6 | 0.7 |

- **All 147 checked states** (every variant at every (n, Jz), and every ground-state-scan subset) put more order than
  DMRG on **every** site (57/57, 115/115; the smallest per-site excess sign(Z_ref)(Z − Z_ref) of the primary states is
  +0.165 / +0.206 at Jz = 1.2); every pipeline state also makes **every** C_zz stronger and **every** 12-site loop larger.
- Energy ratios of the primary states: n = 57: 35 (1.1), 15 (1.2), 2.9 (1.6), 0.40 (2.5), 0.042 (4.0); n = 115: 98,
  45, 12, 2.6, 0.45. Grid also at 1.8, 2.2, 3.5, 5.0 (n = 57) and 5.0 (n = 115): in the tables.
- **n dependence:** at the same Jz and shot budget the n = 115 bias is larger at every Jz (×1.16 at 1.2, ×1.3 at 1.6,
  ×1.9 at 2.5, ×3.4 at 4.0).
- **Replication of pilot3** (fresh samples, new seeds) at n = 57: Jz 1.2: +0.2586 (pilot3 +0.2586; D 336,818 vs
  336,834); Jz 2.5: +0.0364 (pilot3 +0.0364).

## 3. Mechanism

**Table M1. One Jz, step by step: Δm_s (D, energy ratio).** GS = perfect samples of the DMRG ground state;
"support only" = the ground state projected on the sampled configurations (no re-weighting); RR = Rayleigh-Ritz in
the sampled subspace (what the method does); "device-like noise" = flips matched to IBM's number of distinct in-sector
bitstrings (p_dev = 0.67 at n = 57, 0.29 at n = 115; with it our unique-string counts are 978,700 and 987,800 per 10⁶
shots vs IBM's 972,759 and 999,531, and the n = 57 raw ratio at 2.5 is 1.74 vs IBM's raw 1.59).

| n, Jz | GS, support only, at D_primary | GS + RR, at D_primary | (a) Krylov, no noise | (b) + 1 % flips + recovery = primary | (c) device-like noise, post-selection | (d) device-like noise + recovery |
|---|---|---|---|---|---|---|
| 57, 1.2 | +0.175 | **+0.258** | +0.253 (216 k, 14.1) | **+0.259** (337 k, 15.2) | +0.328 (81 k, 32.4) | +0.323 (976 k, 31.3) |
| 57, 1.6 | +0.070 | +0.127 | +0.134 (254 k, 2.64) | +0.139 (375 k, 2.93) | +0.201 (82 k, 7.8) | +0.196 (976 k, 7.4) |
| 57, 2.5 | +0.009 | +0.027 | +0.033 (166 k, 0.33) | +0.036 (291 k, 0.40) | +0.079 (82 k, 1.84) | +0.077 (976 k, 1.74) |
| 115, 1.2 | +0.277 | **+0.317** | +0.297 (240 k, 43) | **+0.301** (472 k, 45) | +0.323 (82 k, 62) | +0.322 (987 k, 62) |
| 115, 1.6 | +0.146 | +0.181 | +0.178 (247 k, 11.8) | +0.181 (479 k, 12.4) | +0.201 (82 k, 19.2) | +0.201 (987 k, 18.6) |
| 115, 2.5 | +0.037 | +0.061 | +0.065 (192 k, 2.44) | +0.067 (431 k, 2.6) | +0.084 (82 k, 5.1) | +0.084 (987 k, 5.0) |

Readings.
1. **Truncation is the cause.** An ideal sampler of the exact ground state, cut to the pipeline's subspace size, gives
   the pipeline's bias (M = 0.997 at n = 57, 1.05 at n = 115). Krylov sampling itself adds nothing beyond its subspace
   size; 1 % flips add ≈ +0.005; device-like noise adds +0.02 to +0.07 (it replaces informative strings by random
   ones); random-flip recovery multiplies D by 12 but changes the bias by −0.000 to −0.005: it neither creates nor
   removes it.
2. **Two parts of the truncation error.** Keeping only the sampled support already over-orders (support only: +0.175
   of the +0.258 at n = 57, Jz = 1.2; +0.277 of +0.317 at n = 115): the missing weight sits on configurations with more
   defects. Rayleigh-Ritz then adds the rest (+0.08 / +0.04): with neighbours missing, the eigenvector moves weight
   back toward the well-connected, Néel-like configurations.
3. **The samples themselves are unbiased.** The multiplicity-weighted mean of the same perfect samples reproduces the
   DMRG m_s to |Δ| ≤ 6e-4 in every scan row. The bias is produced by discarding the counts and diagonalizing in the
   sampled set, not by the sampler.

**Table M2. How fast does it vanish with D (perfect samples, RR)?** W = captured ground-state weight Σ_{b∈B}|ψ_b|².

| n, Jz | D (shots) → Δm_s, W | … | largest D |
|---|---|---|---|
| 57, 1.2 | 86 k (10⁵) → +0.281, W 0.18 | 733 k (10⁶) → +0.244, W 0.33 | 3.16 M (5.1×10⁶) → **+0.218, W 0.45** |
| 57, 1.6 | 57 k → +0.153, W 0.50 | 398 k → +0.126, W 0.67 | 2.54 M (1.01×10⁷) → +0.099, W 0.80 |
| 57, 2.5 | 18 k → +0.049, W 0.86 | 93 k → +0.034, W 0.94 | 452 k (10⁷) → +0.024, W 0.97 |
| 57, 4.0 | 4 k → +0.011, W 0.977 | 19 k → +0.008, W 0.988 | 69 k (10⁷) → +0.004, W 0.997 |
| 115, 1.2 | 100 k → +0.322, W 0.0005 | 300 k → +0.319, W 0.0012 | 799 k (8×10⁵) → **+0.314, W 0.0020** |
| 115, 1.6 | 97 k → +0.191, W 0.037 | 288 k → +0.184, W 0.057 | 937 k (10⁶) → +0.178, W 0.083 |
| 115, 2.5 | 59 k → +0.068, W 0.48 | 455 k → +0.061, W 0.60 | 1.03 M (2.6×10⁶) → +0.055, W 0.67 |

- At n = 57, Jz = 1.2 the bias falls as ≈ D^(−0.074): a 37× larger subspace removes a fifth of it. The (wild)
  power-law extrapolation to Δm_s = 3 % of m_s needs D ~ 10²⁰: in practice it does not vanish at any reachable size.
- At n = 115, Jz = 1.2 the ground state is so spread that 8×10⁵ sampled configurations carry 0.2 % of its weight, and
  the 10⁵ most probable of them already carry all of that: the extra 7×10⁵ strings are "dust" that changes neither the
  energy nor the labels. This is why the bias grows with n at fixed budget: what controls it is the captured weight,
  and W collapses with n near the boundary.
- The most-probable-first subsets ("top-D") lie on the same curve as random subsets of equal energy (Fig.
  `fig_bias_vs_ratio.png`): the bias is not sampling noise; the best possible subspace of that size has it too.
- Capped by the declared sampling time (80 / 100 min per task), the scans reached 3.2×10⁶ (n = 57) and 8×10⁵-10⁶
  (n = 115) configurations near the boundary, not 10⁷; at Jz 1.6-4.0 (n = 57) they reached 10⁷ shots.

## 4. Basis optimization, second attempt (n = 57)

**Implemented literally from Methods / Supp. II.3-II.3.1:** H′ = UHU†, C(θ) = α†H′_Bα with the SKQD vector fixed;
U = one layer of CNOT(c→t)·RY_t(θ)·CNOT(c→t) = exp(−iθ/2 Z_cY_t) over all 64 edges in the three colour sub-layers
(the circuit read from their SVG: control dot on q0, ⊕ and RY box on q1); exact Pauli propagation (no truncation);
analytic gradient; re-diagonalization of H′_B(θ*) in the same subspace (Eq. 11); the stated optimizer (local
optimization on the 100 most probable bitstrings, global checks, ≤ 30 rounds, tolerance 1e-8, stop on a global
increase). **Unspecified, all run:** orientation (control on the minority or the majority colour), per-gate angles vs
one shared angle ("the optimal parameter θ"; 721-point scan over [−π, π] plus refinement), initialization (0 and random
scales 0.1 / 0.3 / 1.0 for the procedure; 1e-3 and 0.1 / 0.3 / 1.0 for per-gate L-BFGS). **Not specified by the paper
and not emulated:** OBP truncation settings, the number of layers actually used in the dataset, whether E′ is
evaluated exactly, whether labels are read off ψ′ or U†ψ′.

| Subspace (n = 57) | ratio before | stated circuit: best f (6 variants) | RY on control (not stated): f, ratio after | Givens, number-conserving (not stated): f, ratio after | Δm_s before → after (Givens): read off ψ′ / physical U†ψ′ |
|---|---|---|---|---|---|
| Jz 1.2, primary | 15.2 | **0.000** | 0.60 → 6.07 | 0.79 → 3.13 | +0.259 → +0.295 / **+0.133** |
| Jz 2.5, primary | 0.395 | **0.000** | 0.50 → 0.199 | 0.60 → 0.160 | +0.036 → +0.051 / **+0.022** |
| Jz 2.5, device-like noise + recovery | 1.74 | **0.000** | 0.80 → 0.352 | 0.88 → 0.208 | +0.077 → +0.091 / **+0.028** |

1. **The stated block gives no gain**, on every subspace, orientation, angle sharing and optimizer, including the
   stated procedure: θ returns to 0 (θ_rms ≤ 1.6e-6). The reason is structural: exp(−iθ/2 Z_cY_t) flips one spin, so
   inside one S^z sector C(θ) is even in θ and θ = 0 is a minimum on these subspaces (pilot3 §1.3; unchanged).
2. **Two unstated variants do reproduce IBM's gain.** With RY on the control wire, or with a number-conserving Givens
   block, the device-like subspace at Jz = 2.5 goes from ratio 1.74 to 0.35 / 0.21 (IBM's Supp. Fig. 9: 1.59 → 0.235).
   We cannot tell from the text which, if any, IBM ran; this is an item to raise with the authors, not a claim.
3. **Which labels?** If labels are those of the physical state U†ψ′, they fall on the same "bias vs energy ratio"
   curve as all other states (Jz = 2.5: +0.028 at r = 0.21 vs +0.024 on the perfect-sampler curve; +0.036 at
   r = 0.35 vs +0.034); at Jz = 1.2 the physical states (+0.133 at r = 3.1, +0.166 at 6.1) sit near the extrapolated
   curve (≈ +0.10 and +0.17). If labels are read off ψ′ directly, they are **more** over-ordered than before
   optimization (+0.09 at 2.5, +0.29 at 1.2), and ψ′ itself has an energy under H far above the reported E′
   (ε = 2.2 J vs 0.22 J at 2.5): the reported energy would not belong to the labelled state.

## 5. Bias as a function of the energy ratio, and at IBM's reported energy

Method: at each (n, Jz) with IBM's dataset ratio and a perfect-sampler scan, Δm_s at IBM's r by interpolation in log r
along the RR curve; band = r ± 5 % (digitization) and the other families where they bracket r. Check: the ΔZ the same
curve predicts there vs IBM's published ΔZ (Supp. Fig. 11). Figures: `figures/fig_bias_vs_ratio.png`.

| n, Jz | IBM ratio | **Δm_s at IBM's ratio** | status | ΔZ predicted / IBM | ΔZ-matched Δm_s (below) |
|---|---|---|---|---|---|
| 57, 1.6 | 1.348 | **+0.094** [0.092, 0.097] | slight extrapolation (lowest sampled r 1.49) | 12.5 % / 10.6 % | +0.080 |
| 57, 2.5 | 0.235 | **+0.026** [0.025, 0.027] | interpolated | 2.9 % / 2.2 % | +0.020 |
| 57, 4.0 | 0.0523 | **+0.006** [0.006, 0.006] | interpolated | 0.64 % / 0.5 % | +0.005 |
| 115, 1.6 | 2.716 | +0.114 | **extrapolated ×4.5 in r: unreliable** | 15.0 % / 10.0 % | +0.077 |
| 115, 2.5 | 0.464 | +0.019 | extrapolated ×3.9 in r | 2.2 % / 2.0 % | +0.018 |

**ΔZ-matched reading** (for the OOD points, where IBM publishes no energy). Over all emulated states at a given (n, Jz)
the ratio Δm_s / ΔZ is constant to ±0.5 % (every state over-orders every site), so IBM's unsigned ΔZ converts into a
signed Δm_s **provided the sign is coherent**, which holds for the whole method class here and which IBM's Fig. 4
colours show at Jz = 1.1, n = 115 (41 of 41 shown sites, R4 §3.2):

| Jz | 1.1 | 1.2 | 1.3 | 1.4 | 1.6 | 2.5 | 4.0 |
|---|---|---|---|---|---|---|---|
| n = 57: Δm_s from IBM's ΔZ | **+0.178** | **+0.159** | +0.142 | **+0.117** | +0.080 | +0.020 | +0.005 |
| n = 115: Δm_s from IBM's ΔZ | **+0.175** | **+0.146** | +0.125 | **+0.105** | +0.077 | +0.018 | +0.004 |

**Uncertainty.** (i) Digitization of Supp. Fig. 11 (±1 point) → ±0.006 in Δm_s at Jz ≤ 1.4. (ii) "Bias is a function
of r": at n = 57 the curve over-predicts IBM's ΔZ by 18-30 % at 1.6 / 2.5 / 4.0, so the r-interpolated values are
upper-side by that much; the two routes bracket the estimate (n = 57: +0.080 to +0.094 at 1.6, +0.020 to +0.026 at
2.5). (iii) At the OOD points the ΔZ route is the only one; the implied energies (ratio ≈ 5 at n = 57, Jz = 1.2) lie
outside our scans and are not used. (iv) These are estimates for the **method class at the dataset's published
quality**, never IBM's labels. They replace R4's "0.6 × emulation" scaling: pilot3/R4 gave +0.16-0.17 at n = 57,
Jz = 1.2 by two routes; today's value is +0.159.

## 6. Position inside the energy window

f₊ = Δm_s / (m_s⁺(ε) − m_s,GS), with m_s⁺(ε) the maximal staggered order at energy E₀ + ε from the new "+" chains
(ground states of H − λΣη_iZ_i; an inner, rigorous-given-the-states bound). f₊ = 1: the state is the most ordered state
its energy allows.

| n, Jz | method states at their own energy (ideal / primary) | at IBM's energy: r-interpolated / ΔZ-matched | pilot widths at 0.8 × IBM energy: bias / D |
|---|---|---|---|
| 57, 1.2 | 0.89 / 0.90 (GS scans 0.85-0.90) | (no IBM energy) | – |
| 57, 1.6 | 0.84 / 0.84 | **0.76 / 0.65** | 0.31 (D = 0.309) |
| 57, 2.5 | 0.66 / 0.67 | **0.60 / 0.45** | 0.28 (D = 0.095) |
| 115, 1.2 | 0.96 / 0.96 | (no IBM energy) | – |
| 115, 1.6 | 0.93 / 0.94 | 0.96 (extrapolated) / **0.65** | 0.38 / 0.26 (D = 0.298) |

- The method's states are close to the "+" witness: at their own energies they carry 66-96 % of the extra order the
  energy permits, more toward the boundary; at IBM's reported energy the estimates give 45-76 %. In units of the full
  window (from the pilot's two-sided D) that is a quarter to a third of D, all on the "+" side.
- Device-noise states and the largest scans lie beyond the chains' energy range (flagged in the tables; there f₊ is
  only an upper bound and reaches ≈ 1).

## 7. Learning consequence (minimal, with nulls and an abstaining rule)

Per-site ⟨Z_i⟩ regressors trained on the grid points in [1.6, 6.0] (n = 57: 10; n = 115: 7) on same-method (primary)
labels; m_s derived from the ⟨Z⟩ model as in the paper. Models: cubic in 1/Jz and small MLP (pilot3), "IBM-like"
architecture 1 as stated in their Supp. IV / Table 2 (one MLP per site, input (Jz, …, Jz) of length n_edges, 5 tanh
layers of 256, Adam 1e-3, 300 epochs, 3 seeds; unstated: raw inputs and targets, Glorot init, float32), and two nulls.

**n = 57, relative m_s error at Jz = 1.2 (vs same-method OOD labels / vs DMRG):** cubic 0.8 % / 41.5 %; small MLP
0.16 % / 40.6 %; IBM-like 0.73 % / 39.4 %; **nearest-neighbour null 1.15 % / 42.0 %**; constant null 4.9 % / 47.2 %.
At 1.1-1.4 every smooth model and the nearest-neighbour null stay ≤ 1.5 % against same-method labels and miss DMRG by
26-53 %. The same models trained on DMRG labels miss DMRG by 0.6 % (cubic), 7.8 % (MLP), 13 % (IBM-like) at 1.2.

**n = 115, same quantity at Jz = 1.2:** cubic 0.6 % / 44.5 %; small MLP 0.02 % / 45.4 %; IBM-like 0.24 % / 45.1 %; **nearest-neighbour null 0.24 % / 45.8 %**; constant null 1.2 % / 47.2 %. At 1.1-1.4: ≤ 1.3 % against same-method labels, 31-57 % against DMRG; trained on DMRG labels: 0.5 % (cubic), 10.1 % (MLP), 10.9 % (IBM-like) at 1.2. Full tables: `laptop_post/results_tables.md` (Table 8).

Readings (declared at Jz = 1.2): **same-method test blind** (MLP and IBM-like < 3 % vs labels, > 9 % vs DMRG) and
**test uninformative** (the nearest-neighbour null also passes it), at both n.

**Abstaining rule (answer only for Jz ≥ J* = 3.3, R2's certified boundary):** n = 57: coverage 29 % of the 14-point
grid, maximal error vs DMRG on answered queries 0.95-1.02 % (mean 0.43-0.47 %), against 49-53 % maximal error without
abstaining; n = 115: coverage 27 % of the 11-point grid, maximal error 1.8-1.9 % (mean 0.95-1.0 %), against 53-55 %. Training only on labels in the certified region and answering only there gives 0.13-0.97 % (n = 57) and 0.39-1.82 % (n = 115).
**Ensemble-spread abstention (baseline):** with τ = 3× the largest training spread, the IBM-like ensemble abstains at
1.1 and 1.2 but not at 1.3 and 1.4, at both n; its spread there (≤ 7e-4 in m_s) is ~400× smaller than the error
(0.26-0.30), so it does not signal the size of the bias.

Scope: a minimal regressor on our grid, not the paper's 45-point training set or its geometry-aware model.

## 8. Deviations and limits (details in `DEVIATIONS.md`)

- No rule, threshold or run was changed. Code changes after the hash were made before the VM run (TeNPy truncation
  check recorded instead of aborting; a named Krylov χ constant) or are post-processing only (learning-test speed-ups,
  validated against pilot3's numbers before any new learning output was read; table and figure layout).
- D3's subspace size fell short (declared cap reached); D1 has no decision (declared gates failed at n = 115).
- The learning test and the summary were run on the laptop from the fetched outputs, not on the VM.
- Two partial fetches during the run were also copied to the bucket.
- Limits: exact evolution instead of Trotter circuits; an i.i.d. flip model; DMRG references (χ ≤ 320) as truth;
  IBM's figures digitized (±5 % ratios, ±1 point errors); no basis optimization at n = 115; the D-scan at n = 115
  reaches 10⁶ configurations at most.

## 9. Cloud usage and final state

| Item | Value |
|---|---|
| Instance | **cj-runner-2 only** (n2-highmem-4, europe-west3-b, lane vm2); TERMINATED at the start (checked 23:52Z) |
| Up | cj-poweroff=off, max-run-duration 12 h, started **00:29:41Z**; bootstrap OK 00:30:07Z; `cj-runner@vm2` stopped 00:31:46Z (inactive); no `heavy_run.py` |
| Work | only under `/mnt/cj/sandbox/fr_20261030T003230Z/` and `/mnt/cj/sandbox/fr_tools/`; pilot3's sandbox read once (copy of 14 Krylov files, hashes equal); /mnt/cj/venv read-only |
| Down | stopped **08:00:33Z** → **7.51 VM-h ≈ 2.23 EUR** at 0.297 EUR/h (cap 12 VM-h); bucket < 0.01 EUR |
| Final state | cj-runner-2 **TERMINATED**, `cj-poweroff=on`, max-run-duration and termination action cleared. cj-runner-1 TERMINATED. cj-runner-1b was RUNNING at our shutdown (the certification-map agent's machine; never touched) |
| Sealed ledgers | identical at boot and at the end: CODE_FREEZE 133 a54dc944…, DECISION_LEDGER 5 402ea1a8…, RUN_LEDGER 33 8afbec65…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 58 72fbe2db…; runner inactive, no `heavy_run.py` |
| Real bill | not read (one-day delay) |

## 10. Files (under `J_next_paper/phase3/full_runs/method/`)

- `DECLARATION.md` / `.sha256` / `DECLARATION_hash_time.txt`, `CODE_SHA256_at_hash.txt`, `CODE_SHA256_final.txt`, `DEVIATIONS.md`, this file.
- `code/`: `fr.py` (tasks), `emu2.py` (115-bit configurations, exact sampler with amplitudes), `bo2.py` (basis
  optimization), `summarize.py`, `ml2.py`, `figs.py`, `results_tables.py`, `sched2.py`, copies of pilot3's `emu.py`,
  `tn.py`, `hhmodel.py`, graphs, tests (5 files), `vm/vm_fr.sh`, `vm/fr_vm.sh`.
- `vm_in_20261030T003230Z/`: upload tarball, `EXPECTED.sha256`, `UPLOAD_SHA256.txt`.
- `out_20261030T003230Z/`: VM outputs (`out/`: ref, gap, krylov, calib, emu, gsscan, bo, wplus, logs, sched, unit
  tests, versions, p3 import), `OUT_SHA256SUMS.txt`, tarball (SHA-256 d5f8144a…).
- `laptop_post/`: summary.json, TABLES.md, ml/ (learning test), results_tables.md, stdout logs; `LAPTOP_SHA256SUMS.txt`.
- `figures/`: `fig_bias_vs_Jz.png`, `fig_mechanism.png`, `fig_bias_vs_ratio.png`, `fig_learning.png` (scripts:
  `code/figs.py`).
- `logs_laptop/`: boot, push, tests, run, checkpoint, fetch, ledgers and shutdown transcripts.
- Bucket: `gs://cj-sqd-research-0f818af9/exploratory/method_20261030T003230Z/`.
