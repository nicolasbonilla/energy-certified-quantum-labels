# Rigor test (optional upgrade): certified lower bounds on heavy-hex XXZ ground energies — RESULTS

**Declared and hashed before any computation at n ≥ 19** (`DECLARATION.md`, SHA-256
fddd75427408d8f9be5b62220706897db5e4250ae4e6354256e9602a81fa2210, hashed 2026-10-31T07:28:44Z; VM started 07:31:56Z).
Run 20261031T073328Z on cj-runner-1b. Units: J; H = ¼Σ_edges(XX + YY + Jz ZZ) on `heavy_hex_graph(d)`, sector 33↑/24↓
(n = 57) and 11↑/8↓ (n = 19). Every number below comes from `out_20261031T073328Z/out/` (fetched; 409 files, all
verified against `OUT_SHA256SUMS.txt`) through `code/analyze.py` (declared) or `code/analyze_explore.py` (post hoc).

## Resumen en español sencillo

1. Probamos si se puede garantizar con matemática exacta (comprobada número a número, sin redondeos) la energía mínima de la red de IBM con 57 cúbits, para que el lado «sí se puede garantizar» del mapa deje de depender del cálculo clásico de referencia.
2. Lo que hacía falta, calculado con los números del mapa: un margen de error de como mucho 0,18 en Jz = 4 (0,27 % de la energía; la estimación del plan, 0,3 %, era buena) y de 0,66-0,94 en Jz = 6 (0,7-1 %).
3. **Veredicto con la regla sellada: RECHAZO.** Lo decide un solo punto: el orden magnético en Jz = 4, en el lado donde el campo empuja contra el orden. Allí nuestra garantía queda 0,88 por debajo del valor de referencia, 3,5 veces el margen permitido.
4. La correlación media entre vecinos sí queda garantizada de forma totalmente rigurosa en Jz = 4 y en Jz = 6, usando solo el 6 % y menos del 1 % del margen permitido. La energía mínima queda fijada con un error garantizado de 0,005 (Jz = 4) y 0,001 (Jz = 6), es decir del 0,007 % y el 0,001 %.
5. El fallo del orden magnético tiene una causa clara: el punto elegido de antemano está justo antes de un cambio brusco de estado (aparece un dominio invertido). Allí el método pierde precisión. Lo comprobamos con el cálculo exacto en 19 cúbits: cerca de ese cambio el método se equivoca entre un 0,5 % y un 1,9 %; lejos de él, menos del 0,05 %.
6. Con un campo algo menor, elegido después de ver los datos (y anotado como desviación), el orden magnético también queda garantizado de forma rigurosa: el intervalo garantizado mide el 69 % del permitido en Jz = 4 y el 28 % en Jz = 6. Las garantías son exactas, pero esa elección se hizo a posteriori.
7. Las 55 garantías se comprobaron con aritmética exacta en un programa separado. En 19 cúbits, las 32 quedan por debajo del valor exacto, como debe ser. No probamos 115 cúbits ni los demás valores de Jz.
8. Coste: 1,81 horas de máquina, unos 1,08 € (1,35 € con el recargo), dentro del tope de 5 horas. La máquina quedó apagada y sin límite de tiempo, con la señal de apagado puesta, y los registros sellados no cambiaron. Para el artículo, según la regla queda una frase; ahora puede ser una frase fuerte (véase §6).

---

## 1. Slack requirement per row (derived from the map; `outputs/requirement.json`)

Rigorous outer side: replace the DMRG energy F of the tilted Hamiltonian by a certified lower bound G_LB = F − s and
drop δG. With equal slack on both sides the largest admissible s is s_req (bisection on the map's chain points); the
decisive chain points are those minimising each side at E_up + s_req.

| row (n = 57) | ε_up | ε_τ^out | **s_req** | s_req/\|E₀\| | decisive λ (+ / −) | F (+ / −) |
|---|---|---|---|---|---|---|
| m_s, Jz = 4.0 | 0.1185 | 0.3017 | **0.1832 J** | 0.273 % | 0.5850 / 0.2196 | −99.410 / −55.131 |
| C̄_zz, Jz = 4.0 | 0.1185 | 0.3036 | **0.1851 J** | 0.276 % | 0.2500 (Jz' = 3.000) / 0.5025 (6.010) | −51.950 / −98.169 |
| m_s, Jz = 6.0 | 0.0625 | 0.7203 | **0.6577 J** | 0.671 % | 1.2800 / 0.3448 | −170.174 / −78.819 |
| C̄_zz, Jz = 6.0 | 0.0625 | 1.0018 | **0.9392 J** | 0.958 % | 0.6460 (Jz' = 3.416) / 2.0000 (14.0) | −58.147 / −224.868 |

The plan's guess (≤ 0.3 % of |E₀|) is right at Jz = 4.0 and conservative at 6.0. Not decisive here: the rows at
Jz = 3.4 and 3.6 need 0.015-0.017 J (0.03 %) and 0.074 J (0.12 %); 4.5-5.5 need 0.32-0.73 J. H(Jz) itself is not used
by the certificate side (E_up is built from the DMRG E₀, an upper bound); its declared requirement is the smaller row
value at that Jz (0.1832 J at 4.0, 0.6577 J at 6.0).

## 2. Method (as declared)

Local-consistency (cluster-marginal) relaxation in dual form = Anderson cluster bound with fully optimized splitting:
E₀(sector) ≥ Σ_k λ_min(h_k) − μ(n_up − n_down), with S^z-preserving overlap multipliers Y_O (±Y_O in the two clusters
of each overlap) and a mean-magnetization multiplier μ. Clusters: **eball2** (all sites within distance 2 of an edge;
≤ 9 sites; n = 57: 62 clusters, 719 overlaps, 131 148 multiplier entries) and **vball2** (radius-2 vertex balls,
≤ 7 sites). Numerics: soft-min L-BFGS-B with β = 30 → 10⁵. Certificate: multipliers rounded to 2⁻³²; every cluster
bound t_k proved by **exact integer Bareiss elimination** of D·(h_k − t_k) on every S^z block (568 blocks per n = 57
certificate, largest 126 × 126, common denominator 2³²-2⁵⁵) in a separate process (`code/verify_exact.py`, pure Python
integers, no import of the optimizer). Toy tests (n ≤ 12) passed on the laptop and on the VM, including the rejection
of a tampered certificate.

## 3. Calibration at n = 19 (exact diagonalization in the sector)

Gate: all 28 declared verified bounds ≤ the exact sector E₀ (**pass**; the 4 exploratory n = 19 bounds too). True slack E₀ − E_LB (best level):

| item (n = 19) | E₀ (ED) | E_LB (verified) | true slack | % of \|E₀\| |
|---|---|---|---|---|
| H(4.0) | −21.025613 | −21.026899 | 0.0013 | 0.006 % |
| H(6.0) | −30.689675 | −30.689965 | 0.0003 | 0.001 % |
| C̄_zz spec Jz' = 3.000 / 6.010 | −16.351631 / −30.737878 | −16.356267 / −30.738310 | 0.0046 / 0.0004 | 0.028 % / 0.001 % |
| C̄_zz spec Jz' = 3.416 / 14.0 | −18.274753 / −70.297243 | −18.277349 / −70.297302 | 0.0026 / 0.0001 | 0.014 % / 0.0001 % |
| m_s "+" (Jz 4.0, λ 0.585 / Jz 6.0, λ 1.28) | −31.800758 / −54.720225 | −31.804946 / −54.721945 | 0.0042 / 0.0017 | 0.013 % / 0.003 % |
| **m_s "−" (Jz 4.0, λ 0.2196)** | −17.357384 | −17.663389 | **0.306** | **1.76 %** |
| **m_s "−" (Jz 6.0, λ 0.3448)** | −25.071635 | −25.554681 | **0.483** | **1.93 %** |
| n = 19 map rows (gate G1, Jz = 4.0): C̄_zz + / −, m_s + / − | | | 0.0042 / 0.0004, 0.0002 / **0.088** | |

So the relaxation is tight to ≤ 0.05 % everywhere except on the m_s "−" side near the reversed-domain crossing, and
this is a property of the relaxation (measured against exact values), not of the DMRG reference. Post hoc (same n = 19
chains, smaller field; `x_` jobs): λ = 0.15165 → 0.0092, 0.18747 → 0.0391 (Jz = 4.0); 0.21829 → 0.0013, 0.26183 →
0.0026 (Jz = 6.0): the loss grows sharply only as λ approaches the crossing.

## 4. n = 57: certified bounds, slacks and the declared decision

Slack s = F_ref − E_LB with F_ref the map's DMRG value (an upper bound on the true energy, so s ≥ the true slack).
Best verified bound per item (level in brackets):

| item (n = 57) | F_ref (DMRG) | E_LB (exact, verified) | slack s | % of \|F\| |
|---|---|---|---|---|
| H(4.0) | −66.995812 | −67.000353 [e] | **0.0045** | 0.007 % |
| H(6.0) | −98.014127 | −98.015250 [e] | **0.0011** | 0.001 % |
| C̄_zz 4.0 "+" (H at Jz' = 3.000) | −51.949722 | −51.965111 [e] | 0.0154 | 0.030 % |
| C̄_zz 4.0 "−" (Jz' = 6.010) | −98.168689 | −98.169810 [e] | 0.0011 | 0.001 % |
| C̄_zz 6.0 "+" (Jz' = 3.416) | −58.146645 | −58.155353 [e] | 0.0087 | 0.015 % |
| C̄_zz 6.0 "−" (Jz' = 14.0) | −224.867970 | −224.868209 [e] | 0.0002 | 0.0001 % |
| m_s 4.0 "+" (λ 0.585) | −99.410110 | −99.410762 [v] | 0.0007 | 0.001 % |
| **m_s 4.0 "−" (λ 0.2196)** | −55.131251 | −56.015318 [e] | **0.884** | 1.60 % |
| m_s 6.0 "+" (λ 1.28) | −170.174387 | −170.180776 [v] | 0.0064 | 0.004 % |
| **m_s 6.0 "−" (λ 0.3448)** | −78.818969 | −80.270294 [e] | **1.451** | 1.84 % |

([e] eball2, [v] vball2; the vball2 bound is better on the two m_s "+" items (and on four n = 19 items) only because
the eball2 optimizer did not converge fully, DEVIATIONS 4.) Exact values (fractions) are in `out/jobs/*_ver.json`; each n = 57 verification took 6-20 min.

**Declared decision (`code/analyze.py`, `outputs/results.json`):**

| row / item | ρ (slack / requirement) | rigorous outer width at E_up, w_rig/τ | rigorous interval at E_up |
|---|---|---|---|
| C̄_zz, Jz = 4.0 | **0.058** | 0.715 → CERTIFIED | [−0.97309, −0.93214] |
| C̄_zz, Jz = 6.0 | **0.007** | 0.492 → CERTIFIED | [−0.99154, −0.96262] |
| m_s, Jz = 4.0 | **3.51** | 1.878 → not certified | [0.86769, 0.97571] |
| m_s, Jz = 6.0 | **1.74** | 1.534 → not certified | [0.89965, 0.98998] |
| H(4.0) / H(6.0) | 0.025 / 0.002 | — | — |

**ρ_max = 3.51 ≥ 3 → REJECT** (eball2 alone: 3.54; vball2 alone: 4.25). n = 19 gate passed, every item present.

## 5. Post hoc (DEVIATIONS 1; not part of the verdict)

Same "−" chains of the map, smaller field, eball2, exactly verified:

| Jz | λ ("−") | F (DMRG) | E_LB (verified) | slack | with the "+" bound above: rigorous m_s interval at E_up | w/τ |
|---|---|---|---|---|---|---|
| 4.0 | 0.15165 | −58.767523 | −58.787162 | 0.0196 | **[0.9359, 0.9757]** | **0.691 → certified** |
| 4.0 | 0.18747 | −56.845572 | −56.890302 | 0.0447 | [0.9346, 0.9757] | 0.714 |
| 6.0 | 0.26183 | −83.417060 | −83.423215 | 0.0062 | **[0.9735, 0.9900]** | **0.281 → certified** |

(The map's DMRG-referenced outer widths at E_up are 0.0351 and 0.0136; the rigorous ones are 0.0398 and 0.0165.) The
inequalities are exact whatever λ is; what is post hoc is only the choice of λ, made after the declared point failed.

## 6. Reading

- **Reachable, with one identified obstacle.** Certified lower bounds with exact verification exist on IBM's
  heavy-hex at n = 57 with slack 0.0002-0.02 J (≤ 0.035 % of |E|) for H and for every tilted Hamiltonian that is not
  next to a level crossing. That is ≥ 10 × below what the certified rows need. The C̄_zz rows at Jz = 4.0 and 6.0
  (n = 57) are therefore certified with no DMRG reference on their outer side (still conditional on the readings and
  on IBM's energies being in-sector Rayleigh quotients, as in the map).
- **Why the declared test fails.** The declared decisive point for m_s "−" sits just below the first-order crossing
  of the "−" chain to a reversed-domain in-sector state (the chain jumps at λ = 0.2666 for Jz = 4.0 and 0.3713 for 6.0).
  There the relaxation, which imposes the sector only through its mean magnetization and through local consistency,
  loses 1.6-1.9 % (measured exactly at n = 19: 1.8-1.9 %). Moving the "−" field away from the crossing restores
  0.007-0.03 % slack (0.08 % at λ = 0.187) and certifies both m_s rows (post hoc).
- **For the paper (declared consequence: one sentence).** A sentence that the numbers support: "Exact-arithmetic
  lower-bound certificates (local-consistency relaxation, dual rounded to rationals) bound the n = 57 heavy-hex ground
  energies to within 0.007 % (Jz = 4) and 0.001 % (Jz = 6) and make the C̄_zz rows of the positive map fully rigorous;
  for m_s the pre-declared test failed at a field next to a level crossing, where the relaxation loses ≈ 2 %; a smaller
  field, chosen afterwards, certifies those rows too." If the author wants the m_s rows as a declared result, a
  confirmatory run with a pre-stated rule for λ (e.g. the largest chain λ below 0.8 × the crossing) would take ≈ 1 VM-h.
- By-product (not declared): the H slacks (0.0045 J at 4.0, 0.0011 J at 6.0) are also below 0.2·ε_dig (0.020 J and
  0.010 J), the margin the witness side would need if IBM's reference energy were the exact E₀.

## 7. Cost and VM state

- cj-runner-1b: lastStart 2026-10-31T07:31:55Z → lastStop 09:20:42Z = **1.81 VM-hours ≈ 1.08 EUR** at 0.594 EUR/h list
  (≈ 1.35 EUR with the ×1.25); bucket copy 85 MB (< 0.01 EUR). Cap 5 VM-h: respected. Real bill: not read.
- Procedure (`logs_laptop/`): `--configuration=sqd-research` only; cj-runner-1b TERMINATED before start; `cj-poweroff=off`,
  max-run-duration 5 h (STOP); runner `cj-runner@vm` stopped after boot, no `heavy_run.py`; work only under
  `/mnt/cj/sandbox/rigor_20261031T073328Z/` and `/mnt/cj/sandbox/rigor_tools/`; `/mnt/cj/mirror`, `prereg/runs`, the
  queue, the ledgers and `/mnt/cj/venv` untouched (venv read-only).
- Sealed ledgers identical at boot (07:33Z) and end (09:19Z): CODE_FREEZE 130 ae45df9d…, DECISION_LEDGER 3 389a3586…,
  RUN_LEDGER 13 dc5b8d20…, RUN_LEDGER_vm 246 aa68f773…, RUN_LEDGER_vm2 30 ca11ff07…; runner inactive, no `heavy_run.py`.
- **Final state** (`logs_laptop/down.txt`, 09:21Z): cj-runner-1b **TERMINATED**, `cj-poweroff=on`, scheduling without
  max-run-duration or termination action. cj-runner-1 TERMINATED. cj-runner-2 was TERMINATED at my start and RUNNING at
  my end (another agent's); I never touched it.
- Outputs also at `gs://cj-sqd-research-0f818af9/exploratory/rigor_20261031T073328Z/`.

## 8. Re-executed, only compared, not checked

**Re-executed (new computation):** 55 certificates (48 declared + 7 exploratory) optimized and each verified exactly
in a separate process on the VM; 18 exact sector diagonalizations at n = 19; VM toy tests (9 cases + tamper test);
laptop toy tests; the requirement derivation from the map's stored chains; both analyses on the fetched outputs.
**Only compared:** the DMRG references F and E₀ of the map (read from its outputs, not recomputed).
**Not checked:** n = 115; the other certified rows (Jz = 3.4, 3.6, 4.5-5.5); whether the map's DMRG F at the m_s "−"
decisive points is the true ground energy (our bound cannot tell; at n = 19 the gap there is the relaxation's); a
second, laptop re-verification of the n = 57 certificates (too heavy for the laptop rule); the literature (no search
was done here; the brief's references were not read); the author's earlier certification code (the same principle —
dual certificate plus exact rational check — was re-implemented, not reused); the real bill.

## 9. Files (under `J_next_paper/phase3/full_runs/rigor/`)

- `DECLARATION.md` (fddd7542…), `DECLARATION.sha256`, `DECLARATION_hash_time.txt`, `DEVIATIONS.md` (4 entries),
  `RESULTS.md`.
- `code/`: `requirement.py`, `lbcore.py`, `lb_opt.py`, `verify_exact.py`, `ed_sector.py`, `make_plan.py`, `run_all.py`,
  `analyze.py`, `analyze_explore.py` (post hoc), `tests/test_toy.py`, `vm/vm_rigor.sh`, `vm/rigor_vm.sh`,
  `graphs/hh_d{3,5,7}.json` (identical to the map's).
- `outputs/`: `requirement.json`, `plan.json`, `plan_explore.json`, `results.json`, `results_posthoc.json`, stdout files,
  `SHA256SUMS.txt`.
- `out_20261031T073328Z/`: fetched archive (tar f2b90e4e…), `OUT_SHA256SUMS.txt` (409 files), `out/jobs/` (task,
  certificate, verification, ED and log of every job). `vm_in_20261031T073328Z/`: upload tar and hashes.
- `logs_laptop/`: instances before, boot, push, VM tests, run start, fetch, ledgers at the end, shutdown.
