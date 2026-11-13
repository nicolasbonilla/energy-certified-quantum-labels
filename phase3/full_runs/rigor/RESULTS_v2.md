# Rigor test, stage v2 (declared λ grid): RESULTS

**Declared and hashed before any v2 computation** (`DECLARATION_v2.md`, SHA-256
aac90b9702d123475505280181f874a484ef1a4e6e8e7f89c85247295b2d83db, hashed 2026-10-31T09:37:31Z; VM started 09:58:31Z).
Run 20261031T100015Z on cj-runner-1b. Every number below comes from `out_20261031T100015Z/out/` (fetched, 897 files,
all verified against `OUT_SHA256SUMS.txt`) and from the v1 certificates in `out_20261031T073328Z/out/`, through the
declared `code/analyze_v2.py` (`outputs/results_v2.json`).

## Resumen en español sencillo

1. Repetimos la prueba con una regla fijada antes de calcular: en cada fila probamos todos los valores del campo guardados en el mapa, más tres valores algo menores, y nos quedamos con la mejor garantía. Las 135 garantías nuevas se comprobaron con aritmética exacta en un programa separado, y todas pasaron.
2. **57 cúbits, Jz = 4 y 6 (la confirmación pedida): ACEPTADO.** Las cuatro filas (orden magnético y correlación entre vecinos) quedan garantizadas sin depender del cálculo clásico de referencia. Usan como mucho el 13 % del margen disponible.
3. **57 cúbits, resto de valores de Jz (3,4 a 5,5): 9 de 10 filas garantizadas.** Solo falla el orden magnético en Jz = 3,4, donde el cálculo de referencia ya tenía un margen de apenas el 4 %. Por esa fila, la regla sellada da RECHAZO a este bloque (relación 3,05, justo por encima del límite de 3).
4. **115 cúbits, Jz = 4 y 6: ACEPTADO.** Las cuatro filas quedan garantizadas. El método escala bien: cada cálculo tarda unos 6 minutos, 1,4 veces lo que tarda con 57 cúbits.
5. En total quedan garantizadas de forma totalmente rigurosa 17 de las 18 filas probadas. Siguen dependiendo, como todo el mapa, de la lectura de las gráficas de IBM y de que sus estados tengan el número correcto de espines hacia arriba.
6. Prueba con 19 cúbits: las 24 garantías quedan por debajo del valor exacto, como debe ser (la mayor diferencia es 0,03).
7. Coste: 2,75 horas de máquina, unos 1,63 € (2,04 € con el recargo); sumando la primera prueba, 4,56 horas y unos 2,7 €. Esperé mi turno para usar la máquina y lo devolví al acabar. La máquina quedó apagada, con la señal de apagado puesta y sin límite de tiempo, y los registros sellados no cambiaron.
8. Para el artículo, el texto propuesto está en el §6: dice qué filas son ahora totalmente rigurosas y cuál no.

---

## 1. What was declared (summary of `DECLARATION_v2.md`)

- **Grid per (n, Jz, label, sign):** every λ point of the map's stored chain plus λ_dec·0.85^k (k = 1, 2, 3; dyadic 2⁻²⁰),
  λ_dec = the chain point decisive for the DMRG-referenced bound at E_up. Provable pruning of points that cannot lead to a
  certified width.
- **Stage A (vball2)** by exact branch-and-bound per side (each side's bound within 0.01 τ of the best over its grid);
  verified v1 certificates at grid points included. **Stage B (eball2)** at the best point of each side of rows above
  0.85 τ (caps 8/8/4). **Gate:** 24 n = 19 jobs at the S1 refinement points with exact diagonalization.
- **Decision:** w_cert = Σ_sides min over verified certificates of (E_up − E_LB)/(λS); ρ = (w_cert − w_F)/(τ − w_F) with
  w_F the DMRG-referenced width on the same grid; per scope ACCEPT if ρ_max ≤ 1, REJECT if ρ_max ≥ 3, GRAY otherwise
  (S1 includes v1's ρ_H = 0.025, 0.002 for H(4.0), H(6.0)).

## 2. Results per row (rigorous interval at E_up; reading 1)

| scope | n | Jz | row | rigorous interval | w_cert/τ | DMRG w/τ | ρ | status | winning "+" point (λ, kind, level, slack) | winning "−" point |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 57 | 4.0 | m_s | [0.93594, 0.97394] | 0.661 | 0.610 | **0.130** | CERTIFIED | 0.31488 chain vball2, 0.0012 J | 0.15165 chain eball2, 0.0196 J |
| S1 | 57 | 4.0 | C̄_zz | [−0.97092, −0.93360] | 0.652 | 0.625 | **0.071** | CERTIFIED | 0.16784 chain vball2, 0.0148 J | 0.26005 chain vball2, 0.0024 J |
| S1 | 57 | 6.0 | m_s | [0.97347, 0.98758] | 0.240 | 0.232 | **0.011** | CERTIFIED | 0.40649 chain vball2, 0.0015 J | 0.26183 chain eball2, 0.0062 J |
| S1 | 57 | 6.0 | C̄_zz | [−0.98598, −0.97124] | 0.251 | 0.247 | **0.005** | CERTIFIED | 0.23214 chain vball2, 0.0024 J | 0.33002 chain vball2, 0.0010 J |
| S2 | 57 | 3.4 | m_s | [0.90479, 0.96624] | 1.086 | 0.958 | **3.052** | not certified | 0.30516 chain eball2, 0.0016 J | 0.12592 chain eball2, 0.0391 J |
| S2 | 57 | 3.4 | C̄_zz | [−0.96245, −0.90646] | 0.994 | 0.953 | **0.883** | CERTIFIED | 0.16634 chain eball2, 0.0231 J | 0.25414 chain eball2, 0.0030 J |
| S2 | 57 | 3.6 | m_s | [0.91720, 0.96898] | 0.909 | 0.809 | **0.525** | CERTIFIED | 0.30471 chain eball2, 0.0014 J | 0.12376 ref ×0.85² eball2, 0.0266 J |
| S2 | 57 | 3.6 | C̄_zz | [−0.96545, −0.91755] | 0.845 | 0.814 | **0.167** | CERTIFIED | 0.16110 chain eball2, 0.0164 J | 0.25307 chain eball2, 0.0026 J |
| S2 | 57 | 4.5 | m_s | [0.95009, 0.97864] | 0.492 | 0.446 | **0.082** | CERTIFIED | 0.32733 chain vball2, 0.0009 J | 0.16630 chain vball2, 0.0210 J |
| S2 | 57 | 4.5 | C̄_zz | [−0.97609, −0.94836] | 0.480 | 0.465 | **0.027** | CERTIFIED | 0.17555 chain vball2, 0.0083 J | 0.26887 chain vball2, 0.0017 J |
| S2 | 57 | 5.0 | m_s | [0.96141, 0.98187] | 0.350 | 0.325 | **0.037** | CERTIFIED | 0.32336 chain vball2, 0.0007 J | 0.18192 chain vball2, 0.0132 J |
| S2 | 57 | 5.0 | C̄_zz | [−0.97969, −0.95923] | 0.351 | 0.343 | **0.013** | CERTIFIED | 0.18905 chain vball2, 0.0051 J | 0.26480 chain vball2, 0.0014 J |
| S2 | 57 | 5.5 | m_s | [0.96832, 0.98503] | 0.285 | 0.267 | **0.024** | CERTIFIED | 0.35581 chain vball2, 0.0017 J | 0.20203 chain vball2, 0.0096 J |
| S2 | 57 | 5.5 | C̄_zz | [−0.98318, −0.96622] | 0.290 | 0.283 | **0.009** | CERTIFIED | 0.20687 chain vball2, 0.0034 J | 0.29008 chain vball2, 0.0021 J |
| S3 | 115 | 4.0 | m_s | [0.94198, 0.97364] | 0.549 | 0.486 | **0.123** | CERTIFIED | 0.27277 chain vball2, 0.0029 J | 0.14497 chain vball2, 0.0527 J |
| S3 | 115 | 4.0 | C̄_zz | [−0.97001, −0.93895] | 0.541 | 0.516 | **0.052** | CERTIFIED | 0.15416 chain vball2, 0.0255 J | 0.21562 chain vball2, 0.0054 J |
| S3 | 115 | 6.0 | m_s | [0.97754, 0.98657] | 0.153 | 0.144 | **0.011** | CERTIFIED | 0.26344 chain vball2, 0.0036 J | 0.20129 chain vball2, 0.0096 J |
| S3 | 115 | 6.0 | C̄_zz | [−0.98454, −0.97494] | 0.163 | 0.159 | **0.005** | CERTIFIED | 0.16279 chain vball2, 0.0039 J | 0.20551 chain vball2, 0.0022 J |

Slack = DMRG reference (chain F, or for refinement points the variational F_up) minus the verified E_LB; it is ≥ the true
slack. The "−" m_s winners sit at λ = 0.12-0.26, below the reversed-domain crossings that defeated v1. Every side's
branch-and-bound ran to completion (no deadline stop).

## 3. Verdicts (declared rule)

| scope | rows | certified | ρ_max | **verdict** |
|---|---|---|---|---|
| S1: n = 57, Jz = 4.0, 6.0 (with v1's H items) | 4 | 4 | 0.130 | **ACCEPT** |
| S2: n = 57, Jz = 3.4, 3.6, 4.5, 5.0, 5.5 | 10 | 9 | 3.052 (m_s, Jz = 3.4) | **REJECT** |
| S3: n = 115, Jz = 4.0, 6.0 | 4 | 4 | 0.123 | **ACCEPT** |

- S2 is decided by one row: m_s at Jz = 3.4, whose DMRG-referenced width is already 0.958 τ, so its margin is 4 % of τ.
  The certified width is 1.086 τ, an excess of 3.05 × that margin. The C̄_zz row at 3.4 is certified at 0.994 τ, which is
  within the 0.02 τ branch-and-bound tolerance of τ. The certificate is still valid, but its margin is thin.
- **Gate (n = 19):** all 24 v2 bounds ≤ the exact sector E₀. True slack 0.0002-0.029 J; the largest values are at the
  m_s "−" refinement points of Jz = 4.0 (0.029, 0.016, 0.010 J at λ = 0.159, 0.135, 0.115).

## 4. n = 115: does it scale, and what does it cost

- vball2 at n = 115: 113 clusters (n = 57: 55), 867 overlaps, ≈ 2.3·10⁴ multiplier entries. Each job took 6.3 min median
  (10.5 max) at 8 parallel jobs, against 4.5 min at n = 57: 1.4 × the time for 2 × the sites. The exact verification is
  per cluster, so it scales linearly.
- The slacks did not grow with n: 0.002-0.025 J away from crossings, 0.053 J on the m_s "−" side at Jz = 4.0. All four
  rows were certified at stage A, with no eball2 job needed (an n = 115 eball2 job would take ≈ 75 min).
- Cost of S3: 20 jobs, ≈ 2.1 core-hours. Because a side runs one job at a time, the last n = 115 side (m_s "−" at
  Jz = 4.0, 9 points) added a sequential tail of ≈ 35 min at low load.

## 5. Cost, VM state, lock

- cj-runner-1b: lastStart 2026-10-31T09:58:31Z → lastStop 12:43:35Z = **2.75 VM-hours ≈ 1.63 EUR** at 0.594 EUR/h list
  (≈ 2.04 EUR with ×1.25). Cap 5 VM-h: respected. v1 + v2: 4.56 VM-h ≈ 2.71 EUR (≈ 3.39 EUR with ×1.25). Real bill: not
  read.
- 135 jobs: 83 n = 57 vball2 (4.5 min median), 8 n = 57 eball2 (54 min), 20 n = 115 vball2, 24 n = 19 gate jobs. All 135
  certificates were verified exactly, with 0 failures.
- **Lock:** the lock was held by another agent ("qpu", from 09:27:54Z). I waited with background polling and created
  mine at 09:56:58Z after its release. The VM was TERMINATED when I started. I deleted my lock at 12:44:08Z, after `down`
  showed TERMINATED.
- Procedure: as v1 (`logs_laptop_v2/`). Runner stopped after boot, no `heavy_run.py`. Work only under
  `/mnt/cj/sandbox/rigor_20261031T100015Z/` and `rigor_tools/`; the v1 sandbox was only read. Sealed ledgers identical at
  boot (09:59Z) and end (12:42Z): CODE_FREEZE 130 ae45df9d…, DECISION_LEDGER 3 389a3586…, RUN_LEDGER 13 dc5b8d20…,
  RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 30 ca11ff07….
- **Final state** (`logs_laptop_v2/down.txt`, 12:44Z): cj-runner-1b **TERMINATED**, `cj-poweroff=on`, scheduling
  without max-run-duration. cj-runner-1 TERMINATED. cj-runner-2 TERMINATED at the end; I never touched it.
- Deviations: `DEVIATIONS_v2.md` (3 entries: scheduling order, the stage-B cap used in S2, the wait for the lock).

## 6. For the paper (updates §6 of `RESULTS.md`)

Proposed text:

> "The certificate side of the positive map can be made fully rigorous. For every λ, ⟨O⟩ ≤ (E_thr − E_LB(H − λO))/λ
> with E_LB an exact lower bound on the sector ground energy. We obtain E_LB from a local-consistency (cluster-marginal)
> relaxation in dual form. Its multipliers are rounded to rationals, and every cluster inequality is checked by exact
> integer elimination in a separate program. With a λ grid fixed in advance (the stored chain points plus a fixed
> geometric refinement), 13 of the 14 certified rows at n = 57 (m_s and C̄_zz at Jz = 3.4-6.0) and all four rows tested
> at n = 115 (Jz = 4, 6) are certified with no classical reference on their certificate side. The rigorous widths exceed
> the DMRG-referenced ones by 0.004-0.10 τ on the certified rows. The exception is m_s at Jz = 3.4 (rigorous width 1.09 τ), where the
> DMRG-referenced width is already 0.96 τ. The bounds are tight to ≤ 0.05 % of |E| away from level crossings and lose
> ≈ 2 % next to the reversed-domain crossing of the "−" m_s chains. A fixed grid avoids that point. These statements
> remain conditional on the digitized energies and on IBM's states being in-sector, as for the whole map."

Notes for the author:
- The rigorous statement holds at the **computed** Jz values. J* and the count of certified training points (29 / 45)
  rely on interpolating ε_τ between computed Jz, which is not part of the certificate.
- With the declared rules, the S2 verdict is REJECT because of one row. The sentence above reports this; it does not
  hide it.
- The H bounds of v1 (E₀ within 0.0045 J at Jz = 4 and 0.0011 J at 6) remain valid and can be quoted.

## 7. Re-executed, only compared, not checked

**Re-executed:**
- 135 new certificates, each optimized and verified exactly in a separate process on the VM.
- 24 exact diagonalizations at n = 19.
- VM toy tests (9 cases plus the tamper test).
- On the laptop: the grid and plan (`make_plan_v2.py`), a mock run of the scheduler (no physics), and the analysis.

**Only compared:** the map's DMRG chain energies F and the stored chain states' (E, o), used for the grid, the pruning
bound and the reported slacks only. The 20 v1 certificates at grid points were reused, not recomputed.

**Not checked:**
- C̄₂ and the local labels.
- n = 115 at Jz other than 4.0 and 6.0.
- The interpolated training points between computed Jz.
- A laptop re-verification of the n = 57 and n = 115 certificates (too heavy for the laptop rule).
- That IBM's energies are in-sector Rayleigh quotients.
- The literature.
- The real bill.

## 8. Files (under `J_next_paper/phase3/full_runs/rigor/`)

- `DECLARATION_v2.md` (aac90b97…), `DECLARATION_v2.sha256`, `DECLARATION_v2_hash_time.txt`, `DEVIATIONS_v2.md`,
  `RESULTS_v2.md`.
- New code: `code/make_plan_v2.py`, `code/run_v2.py`, `code/analyze_v2.py`; `code/vm/vm_rigor.sh` (lock, `push2`) and
  `code/vm/rigor_vm.sh` (`runv2`). Bound and verifier code unchanged from v1.
- `outputs/grid_v2.json`, `outputs/plan_v2_A.json`, `outputs/results_v2.json`, `outputs/analyze_v2_stdout.txt`,
  `outputs/SHA256SUMS_v2.txt`.
- `out_20261031T100015Z/` (tar d28fab87…, `OUT_SHA256SUMS.txt` a061adcd…, `out/jobs/`, `out/state_v2.json`,
  `out/run_log.txt`); `vm_in_20261031T100015Z/`; `logs_laptop_v2/`. Bucket copy:
  `gs://cj-sqd-research-0f818af9/exploratory/rigor_20261031T100015Z/`.
