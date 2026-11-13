1. Paso 0: la fórmula de la ventana (crece como δe elevado a 1/3) aguanta los datos publicados de iPEPS: los estados usan entre el 52 % y el 57 % de la ventana en todos los tamaños; el límite para matarla era 120 %.
2. Paso 1, en una red de 4x6 con solución exacta: la idea era que las redes neuronales tipo transformador (ViT) usan mucho menos de la ventana que los MPS. Sale al revés.
3. Con J2 = 0, en los cinco puntos de energía declarados, la ViT usa entre el 16 % y el 33 % de la ventana y el MPS entre el 0,5 % y el 6 %: la ViT gasta de 5 a 35 veces más. La regla mataba si pasaba de 0,5 veces en 3 de 5 puntos; pasa en los 5.
4. **Veredicto: MUERTA.** No es un caso dudoso: el resultado secundario (medianas) da lo mismo, de 7 a 19 veces.
5. Con J2 = 0,5 (sin veredicto) la ViT solo llegó a dos de los cinco puntos: gasta 1,3 y 1,8 veces lo del MPS en el orden antiferromagnético, y 1,0 y 0,4 veces en el orden de dímeros.
6. En 24 sitios la ventana crece como δe elevado a 1/2, no a 1/3, como se esperaba en un sistema tan pequeño: este cálculo no puede confirmar ni negar la ley de 1/3.
7. Problemas: pausas de casi una hora entre pasos al principio (1,9 horas de máquina parada), dos fallos de mis controles de DMRG corregidos antes de usar datos, y las ViT cortadas por tiempo (entre 200 y 620 pasos de los 2000 previstos).
8. Coste: 4,67 horas de máquina, unos 2,77 € de 5 € permitidos. Las tres máquinas están apagadas, sin dirección externa y sin candado.

---

# Kill test W: results (2026-11-07)

Rules: `DECLARATION.md` (SHA-256 1ed2ba12…, hashed 2026-11-07T18:13:55Z, before the VM started; code manifest `DECLARATION_manifest.sha256`). Deviations: `DEVIATIONS.md` (8 items, none changes a rule; item 6 changes the reference of a DMRG gate, item 7 the scheduling of declared DMRG runs). Run stamp 20261107T190617Z on cj-runner-1b. All numbers below come from `out_20261107T190617Z/out/analysis.json` (computed on the VM by `code/analyze_w.py`) or from the method JSON files next to it; the laptop only read them. Fetched archive: 0 files failing their SHA-256.

## 1. Verdict

| Item | Rule | Outcome | Verdict |
|---|---|---|---|
| Step 0 (`STEP0.md`) | DEAD if r > 1.2 for any D = 3..6 (iPEPS, arXiv 2009.02313) | r = 0.558, 0.556, 0.533, 0.522 (D = 3..6); 0.566 at D = 7 | survives |
| Step 1, primary | J2 = 0, O_ms: DEAD if r_ViT / r_MPS > 0.5 at ≥ 3 of 5 points | 5 of 5 evaluable, all above 0.5 (5.4 to 35) | **DEAD** |
| Secondary statistic (median ±0.2 decades) | report | 5 of 5 above 0.5 (7.1 to 19.1) | same |
| **Overall** | | | **DEAD** |

## 2. Exact reference (4x6 torus, S^z = 0 sector, 2 704 156 states)

| | e0(24) | O_ms(GS) | O_dim(GS) | ⟨S²⟩ | sector |
|---|---|---|---|---|---|
| J2 = 0 | -0.689688074749 | 0.2333251797 | 0.0411559086 | 1e-29 | Tx = Ty = +1, flip +1 |
| J2 = 0.5 | -0.522524935367 | 0.1063662194 | 0.0669363356 | 4e-29 | Tx = Ty = +1, flip +1 |

Envelope chains: 6 chains × 42 points (λ = 1e-3 .. 100). Weak duality worst violation ≤ 1.4e-11 (tolerance 1e-9); random-restart ground energies at λ = 0.1, 1, 10 agree to ≤ 2e-15 per site; residuals ≤ 1.6e-10; w_out/w_in at the test points within 0.1-2.6 %. Largest r_outer over all states: 0.60 (J2 = 0, ms), 0.89 (0.5, ms), 0.57 (0.5, dim), so no state leaves the window.

Window widths at the five points, J2 = 0, O_ms (inner hull):

| δe | 1.0e-3 | 1.78e-3 | 3.16e-3 | 5.62e-3 | 1.0e-2 |
|---|---|---|---|---|---|
| w+ (more order) | 0.01109 | 0.01446 | 0.01878 | 0.02423 | 0.03069 |
| w- (less order) | 0.01243 | 0.01692 | 0.02325 | 0.03210 | 0.04423 |

**Exponent (report, no rule).** Least-squares slope of ln w+ against ln δe on the hull points, J2 = 0, O_ms: 0.498 (δe 1e-6..1e-5), 0.495 (1e-5..1e-4), 0.483 (1e-4..1e-3), 0.439 (1e-3..1e-2), 0.252 (1e-2..1e-1). Lower side: 0.50, 0.51, 0.52, 0.55, 0.60. At 24 sites the window is quadratic (exponent 1/2) wherever the finite-size gap dominates; the slope falls through 1/3 only above δe ≈ 1e-2, where O_ms approaches its largest eigenvalue (0.29167; the chain ends at 0.29165), i.e. by saturation of a bounded operator, not by Goldstone physics. This test therefore says nothing for or against the δe^(1/3) law of `FORMULA.md`.

## 3. r per method, J2 = 0, O_ms (the rule)

Interpolated r (piecewise linear in log10 δe) and the ratio:

| δe | r_ViT | r_MPS | r_ViT / r_MPS | Krylov |
|---|---|---|---|---|
| 1.0e-3 | 0.163 | 0.0100 | 16.3 | not reached |
| 1.78e-3 | 0.158 | 0.0226 | 7.0 | not reached |
| 3.16e-3 | 0.186 | 0.0053 | 35.2 | not reached |
| 5.62e-3 | 0.235 | 0.0091 | 25.8 | not reached |
| 1.0e-2 | 0.331 | 0.0616 | 5.4 | not reached |

Checked by hand on the laptop at δe = 1e-3 from the per-state table (bracketing points ViT M step 200 / M step 100, MPS χ = 160 / 128): 0.1632 and 0.0100, equal to the VM's values.

Per-state values (δe, error in O_ms, r):
- **ViT** (20 checkpoints, 3 sizes): every ViT state overestimates O_ms (err > 0, upper side). r falls with δe: 0.57-0.61 at δe 2-5e-2 (step 10), 0.29-0.34 at 6e-3..1.2e-2, 0.12-0.21 at 2e-3..5.3e-3, 0.05-0.16 at 3.6e-4..9.3e-4. Best states: L step 281 (δe 3.60e-4, err +3.6e-4, r 0.053), M step 618 (3.63e-4, +5.5e-4, 0.081). ⟨S²⟩ 0.009-2.7 (the ViT is not a singlet).
- **MPS** (26 χ, 2..256, all pass the gate with |Δe| ≤ 7e-15): errors of both signs and tiny: |err| ≤ 3.3e-4 for χ ≥ 80 (δe ≤ 3.5e-3), 1.4e-3..4.1e-3 for χ = 6..48. r = 0.0002-0.064 for every χ ≥ 4; r = 0.19-0.20 only at χ = 2, 3 (δe 0.08-0.12). δe reaches 2.3e-4 at χ = 256.
- **Krylov (no verdict)**: the idealised generator never gets below δe = 1.04e-2 (top-K 1e6), so it covers none of the five points. r = 0.003-0.44; it overestimates order for small subspaces (K ≤ 3e4: r 0.003-0.44) and underestimates it for large ones (K ≥ 1e5: r 0.04-0.25).

Reading: on this lattice the MPS reaches a given energy error while keeping the staggered order almost exact (it errs mainly in short-range correlations), whereas the ViT errs on O_ms by a sizeable, systematic fraction of the window, always towards more order. The candidate's hypothesis (ViT uses much less of the window than tensor networks) is contradicted by a factor 5 to 35, not marginally.

## 4. J2 = 0.5, reported without verdict

ViT reached only δe ≥ 5.45e-3 (wall cap; L 203 steps, M 549 steps), so only the last two points are evaluable.

| δe | O_ms: r_ViT, r_MPS, ratio | O_dim: r_ViT, r_MPS, ratio | Krylov r (ms, dim) |
|---|---|---|---|
| 1.0e-3 | —, 0.168, — | —, 0.229, — | — |
| 1.78e-3 | —, 0.243, — | —, 0.241, — | — |
| 3.16e-3 | —, 0.244, — | —, 0.280, — | — |
| 5.62e-3 | 0.235, 0.186, **1.26** | 0.271, 0.281, **0.97** | 0.079, 0.014 |
| 1.0e-2 | 0.507, 0.279, **1.82** | 0.206, 0.494, **0.42** | 0.054, 0.013 |

Signs: ViT overestimates O_ms and underestimates O_dim; MPS underestimates both. At J2 = 0.5 the MPS uses a large share of the window (O_ms: r 0.08-0.27 for χ ≥ 10, down to δe = 1.0e-4 at χ = 256, and 0.35-0.41 for χ = 4-8; O_dim: r 0.13-0.31 for χ ≥ 12), unlike at J2 = 0.

## 5. What a hostile referee would say

1. "Twenty-four sites is not the Goldstone regime." Correct: the window here is quadratic (exponent ≈ 0.5) up to δe ≈ 1e-2; the δe^(1/3) claim is a thermodynamic-limit statement that this test cannot reach. Only the measured fraction per method on this lattice survives as a fact.
2. "When both methods err on the same side, r_ViT / r_MPS at equal δe is just the ratio of observable errors; the envelope adds a normalisation, not information." Largely true here (MPS errs on both sides; w-/w+ ≤ 1.45 at the test points, far smaller than the observed ratios).
3. "Your ViT is small and under-trained." True: 534 to 13 138 parameters, one seed per size, 1024 samples, cut by the 80-minute wall cap at 203-618 of the 2000 declared steps because the CPU was shared. A production transformer could behave differently; this test says nothing about it. But the ViT r falls only slowly as δe falls (0.33 at 1e-2, 0.05-0.08 at 3.6e-4), while MPS r is ≤ 0.06 everywhere, so longer training of these models would not obviously close a factor 5-35.
4. "DMRG from a Néel start on a torus at fixed χ is one particular MPS path." True; other orderings, cylinders or warm starts give other states at the same δe.
5. "One observable, one model, one lattice." The rule used O_ms at J2 = 0 only; at J2 = 0.5 the picture is mixed (ratio 0.4-1.8 at two points).
6. Eckart/Weinhold: first-order observable error from second-order energy error is textbook; nobody decides a phase by energy alone. Nothing new is claimed.

## 6. Re-executed, only compared, not checked

| Status | Items |
|---|---|
| **Re-executed (this test, on the VM)** | exact ground states and 6 envelope chains; 26 + 26 DMRG states; 5 ViT runs (33 checkpoints evaluated on full vectors); Krylov generator (12 subspaces per J2); analysis; gates G1 (4x4 energy -11.2284832084, diff 3e-11), G2 (Néel closed forms), G3 (ladder vs pair sum, 4e-16), G4 (dimer product 45/256 and 24/256), G5 (DMRG χ = 16, both J2), G6 (NetKet full-sum energy vs wlib, ≤ 4e-16; S^z = 0 samples; 30 VMC steps lower the energy), G7 (propagator vs expm_multiply, 3e-16) |
| **Checked on the laptop** | interpolated r at δe = 1e-3 for ViT and MPS from the per-state table; chain checks and widths read from `analysis.json`; step 0 arithmetic (`STEP0.md`) |
| **Only compared** | published 4x4 energy; published iPEPS numbers (step 0, from the vector figures and Table II of 2009.02313); QMC constants (Sandvik 2601.20189, Jiang-Wiese 1011.6205), Hofmann 2008.12423 Eq. (2.7) |
| **Not checked** | prior-art papers 2606.31021, 2602.02665 and the V-score paper 2302.04919 (not opened in this test); 1803.08445 and 1803.08566 only through 2009.02313; the NLO constants k2 + k3 of the envelope; other ViT seeds, larger ViTs, the declared 2000 steps; other MPS geometries; sizes other than 4x6; MPS states below δe = 1e-4 at J2 = 0 (χ = 256 gives 2.3e-4; the brief's 1e-4 was not reached at J2 = 0) |

## 7. Cost and final state

| Item | Value |
|---|---|
| VM (gcloud timestamps) | cj-runner-1b only. Start 2026-11-07T18:15:47.4Z, stop 22:55:50.4Z: **4.67 VM-h ≈ 2.77 EUR** at 0.594 EUR/h list (≈ 3.47 EUR with ×1.25). Budget 5 EUR; 8 VM-h stop rule not reached |
| Idle time | about 1.9 VM-h before computing started (gaps between laptop steps, DEVIATIONS 1) |
| Temporary address | `w-temp-pip` attached 20:06:25Z, deleted 20:08:36Z; absent at every later check and at 22:56:14Z |
| Final state | cj-runner-1, cj-runner-1b, cj-runner-2 **TERMINATED**; cj-poweroff = on; max-run-duration cleared; no external address; lock released 22:56:24Z. Nothing deleted in the cloud; no new resource; no IBM; `paper/` not edited; no git operation |
| Left on the VM disk | the sandbox `/mnt/cj/sandbox/W_20261107T190617Z/` with its venv (1.0 GB), two ground-state vectors (43 MB) and the pip wheel; /mnt/cj free space 2.3 GB (3.3 GB before). The `clean` step was not run because the VM was stopped by the watchdog; deleting them needs a restart |

Files (`phase3/full_runs/kill_tests/W_window/`, SHA-256 in `SHA256SUMS.txt`): `FORMULA.md` (+ `.sha256`), `STEP0.md`, `step0_inputs/`, `DECLARATION.md` (+ `.sha256`, `_manifest.sha256`), `DEVIATIONS.md`, this file, `code/` (wlib, ed_env, dmrg_w, vit_w, krylov_w, gates_w, analyze_w, sched_W, plan.json, VM and watchdog scripts, step-0 extraction scripts), `vm_in_20261107T190617Z/`, `patches_20261107T190617Z/`, `out_20261107T190617Z/` (JSON, logs, `analysis.json`), `logs_laptop/`.
