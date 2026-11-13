1. Pedido: medir nosotros mismos, en un procesador cuántico gratuito de IBM, el modelo de 57 cúbits del artículo. Resultado: **no se envió nada al procesador**; paré antes, en el paso de "¿es posible?".
2. Motivo: el grafo del artículo (`heavy_hex_graph(5)`) tiene cuatro ciclos cerrados de 10 sitios, y en los chips de IBM el ciclo más corto tiene 12. Por eso el grafo no cabe "de forma nativa" en los chips de red hexagonal del plan gratuito (fez, kingston y marrakesh). La condición obligatoria del encargo no se puede cumplir en ellos.
3. La única salida es mover, en cada paso, el estado de 4 sitios del borde a través de cúbits libres. En kingston, con la calibración de hoy, el circuito más largo tendría 2240 puertas de dos cúbits en vez de 1920, y profundidad 141 en vez de 91 (las cifras de una colocación nativa del mismo circuito). Es un cambio de diseño; el coordinador lo aprobó (opción a).
4. Tiempo de procesador: la cuenta es del plan gratuito, con 600 segundos libres (0 usados en los últimos 28 días). El plan cabe dentro de 480 s (con el 20 % de margen): Jz = 1,2 con el millón de disparos de IBM (unos 260-300 s), más las dos comprobaciones de orden de bits, y Jz = 1,6 y 4,0 con unos 25 mil disparos por circuito.
5. Ya preparado y probado en el portátil: el código, la regla para elegir los cúbits y las comprobaciones de orden de bits. Las 7 pruebas pasan en el simulador local, y un borrador de declaración queda sin sellar.
6. El fundador debe elegir: (a) aceptar el camino con puertas extra, con el mismo modelo y comparable con nuestra copia del método; (b) usar otro grafo de 57 cúbits que sí cabe, pero entonces se pierde la comparación con IBM y con nuestros cálculos; (c) esperar a tener un chip de red cuadrada, que sí lo admitiría (hoy no está en el plan gratuito).
7. Sobre cómo colocó IBM sus circuitos no afirmamos nada: no lo sabemos.
8. Coste: 0 minutos de procesador (quedan 10), 0 horas de máquina en la nube, 0 €. No toqué ninguna máquina: las dos estaban ocupadas por otros trabajos, y su estado final no cambió por mi parte.

---

# Feasibility record of 2026-10-31 (superseded by the coordinator's decision for option (a); see RESULTS.md)

**Status: STOPPED before the declaration and before any QPU submission.** A binding requirement of the brief — "a
heavy-hex backend that can embed heavy_hex_graph(5) natively" — is impossible on every IBM heavy-hex device, by a
girth argument (§1). Nothing was submitted to IBM (no job ids exist), no VM was started, no cloud resource was
touched. Everything needed to run the routed alternative is prepared and unit-tested (§5); The unhashed draft was replaced by `DECLARATION.md`.

| Status | Items |
|---|---|
| **Re-executed (today, laptop)** | read-only account check (plan, usage window); read-only backend probes (configuration, calibration, coupling maps of ibm_fez / ibm_kingston / ibm_marrakesh); girth and VF2 embedding checks; routed-layout search and local transpilation with today's calibrations; 7 bit-order / equivalence unit tests on the local Aer simulator; a 2-step timing run of the noiseless MPS control at n = 57 |
| **Only compared** | the method run's emulation outputs, DMRG references and gaps (`method/out_20261030T003230Z/out/`, read, not recomputed); IBM's published numbers (Methods of 2606.15983: 10⁵ shots per circuit, ≈ 5 min per job, 1920 CZ and CZ depth 91 at n = 57, 81,862 in-sector strings per 10⁶ shots; digitized raw ratios from method/code/fr.py) |
| **Not checked** | any device behaviour (no job); the runtime's own usage estimate (it needs a submission); any live device other than fez / kingston / marrakesh; how 2606.15983 embedded its graph (no claim made) |

## 1. The blocker: heavy_hex_graph(5) is not a subgraph of any IBM heavy-hex coupling graph

- **Girth.** `rustworkx.generators.heavy_hex_graph(d)` has girth **10** for d = 3, 5, 7: exactly one 10-cycle per
  *boundary syndrome node* (a syndrome node whose two neighbours are both data nodes). d = 5: four 10-cycles, through
  nodes 25, 30, 31, 36 (e.g. 0-37-1-38-26-42-6-41-5-25-0). d = 7 (n = 115): six, through 49, 56, 57, 64, 65, 72.
  The heavy-hex coupling graphs offered to this instance have girth **12**: ibm_fez, ibm_kingston, ibm_marrakesh
  (live targets, §1 next bullet), and also the library snapshots FakeFez, FakeKingston, FakeMarrakesh, FakeAachen,
  FakePittsburgh, FakeTorino and ten 127-qubit snapshots (`logs_laptop/girth_check.txt`). A subgraph cannot have a
  shorter cycle than its host, so **no native embedding exists on these heavy-hex devices**.
  *Correction (2026-10-31, coordinator):* an earlier version of this note also named ibm_boston. That statement was
  checked only against the library snapshot `FakeBoston` of qiskit-ibm-runtime 0.48.0 (156 qubits, Heron r3,
  calibration dated 2026-04-17, girth 12), not against the live device, and is withdrawn. We make no claim about the
  device or the embedding used by 2606.15983.
- **Confirmed on today's devices:** VF2 subgraph search finds **0 embeddings** on ibm_fez, ibm_kingston and
  ibm_marrakesh (`logs_laptop/probe_backends_1.json`). The graph JSON used everywhere (`graphs/hh_d5.json`, the same
  file as method/ and map/) is asserted equal to rustworkx's graph at every import.
- A square-lattice device (FakeNighthawk, 120 q) does host heavy_hex_graph(5) natively
  (`logs_laptop/square_lattice_check.txt`), but no such backend is offered to this Open-plan instance.

**Scope.** We make no claim about how 2606.15983 embedded its circuits or which device topology it used.

## 2. Account, plan and minutes (read-only)

- `QiskitRuntimeService()` with the saved default account works (channel ibm_quantum_platform). The token and the
  account file were never read or printed. The instance is "open-instance", **plan "open", pricing "free"**.
- Usage window (rolling 28 days, read at 08:12Z): 2026-10-03T08:12:59Z → 2026-10-31T08:12:59Z, **consumed 0 s,
  limit 600 s, remaining 600 s**. Re-read at the end (08:46Z, `logs_laptop/account_check_2.json`): consumed 0 s,
  remaining 600 s. Unchanged by this run.
- Backends offered: ibm_fez, ibm_kingston, ibm_marrakesh (Heron r2, 156 qubits, basis cz/rz/sx/x, default rep_delay
  250 µs, range 0-2 ms), all operational at 08:12Z.

## 3. The routed alternative (option a), measured with today's calibrations (no submission)

The 53-node core (graph minus 25, 30, 31, 36) embeds natively, in 96 ways on each device. Each boundary node gets a
free home, and its non-adjacent edge(s) are applied after moving the site's state into free |0⟩ qubits
(move = CX·CX, exact when the target is |0⟩) and back (`code/qpu_route.py`). The logical circuit is unchanged; the
routed circuit equals it exactly at d = 3 (test T5). Layout rule: minimise the expected two-qubit error per Trotter
step (`logs_laptop/probe_routed_2.json`, `diag_core_1.json`):

| backend (calibration time) | rule result | expected 2q errors per step | moves per step | k = 10: CZ / CZ depth / duration | k = 1: CZ / depth |
|---|---|---|---|---|---|
| ibm_kingston (08:30 CET) | found, thresholds relaxed ×2 | **0.790** | 16 | **2240 / 141 / 17.6 µs** | 224 / 15 |
| ibm_fez (09:09 CET) | found, relaxed ×4 | 1.119 | 16 | 2240 / 143 / 15.6 µs | 224 / 17 |
| ibm_marrakesh (09:21 CET) | none, even ×4 | — | — | — | — |

Against a native embedding of the same Trotter circuit (3 CZ × 64 edges × 10 steps = 1920, depth 9 × 10 + 1 = 91), the
routed circuits have +16.7 % two-qubit gates and +55 % depth: more noise than a native circuit would have.

## 4. Feasibility of the plan within the free minutes (estimate; no measured job)

- QPU time per shot ≈ rep_delay + circuit duration: lower bound **261 s per 10⁶ shots** (kingston, mean over
  k = 1..10). IBM measured ≈ 300 s per 10⁶ shots for the same circuit family with DD and twirling (≈ 5 min per job).
- Cap 480 s (80 % of 600 s). Job A (decisive): two bit-order checks (10⁴ shots each) + Jz = 1.2 at 10 × 10⁵ shots ≈
  265-306 s. Job B: the checks again + Jz = 1.6 and 4.0 with S_B from job A's measured usage, ≈ 2.5 × 10⁴ shots per
  circuit. **Jz = 1.2 plus the checks fit with IBM's full shot budget**, so the minutes are not the obstacle.
- Decisive threshold vs prediction (method run, published budget, only compared). Δm_s at Jz = 1.2 is +0.253 for
  noiseless exact-evolution Krylov and +0.323 for device-like noise matched to IBM's in-sector count (ratio 31.3). A
  "present" line at +0.10 sits 2.5-3.2× below these, within the ~3× rule. At 1.6 the predictions are +0.134 and
  +0.196 (ratio 7.44 vs IBM raw 6.89); at 4.0, +0.004 and +0.023 (ratio 0.40 vs IBM raw 0.367).
- Noiseless MPS control of the identical circuits (`qpu_lib.TrotterMPS`): laptop timing 2.2 s for step 1 (χ 125)
  and 198 s for step 2 (χ 256), discarded weight ≤ 2.3e-20 (`logs_laptop/mps_control_timing.txt`). Estimated cost
  with post-processing: **≈ 2-3 VM-hours (≈ 0.6-0.9 EUR on cj-runner-2)**, within the 6 VM-h cap.
- VMs today: `huang/RESULTS.md` and `rigor/RESULTS.md` do not exist, so cj-runner-2 and cj-runner-1b are in use by
  other agents and are not available under the rule. Not touched; gcloud was not called.

## 5. What is ready (unit-tested, not sealed)

- `code/qpu_lib.py`: conventions C1-C7 in the header (site = virtual qubit = clbit; |1⟩ = down; Qiskit
  little-endian = emu2's configuration convention; layout list; decode from BitArray), circuits (checks and Krylov),
  native layout rule, ISA checks, decoder, device-check verdict, noiseless Trotter MPS control.
  `code/qpu_route.py`: routed layout rule, routed circuits, routed ISA checks.
- `code/tests/test_bitorder.py`: **7/7 pass** on the local Aer simulator (`logs_laptop/test_bitorder_run2.txt`;
  run 1 had a test-harness error in the Aer seed option, fixed before run 2). The tests cover: the asymmetric check
  state against all graph automorphisms and against i → 56 − i; product states (asymmetric, Néel, single sites
  including routed boundary homes) through transpilation, routed layout, Aer and the decoder, where the reversed
  reading fails as it should; the routed ISA checks and the verdict logic; MPS vs dense; routed vs logical circuit,
  exactly at d = 3; the full chain on an entangled state (ISA circuit on the fake device → Aer MPS → decoder → ⟨Z_i⟩
  within 5σ of the exact values); and the method's sampler on the control MPS.
- `code/method_copy/` (emu.py, emu2.py, hhmodel.py, tn.py) and `code/graphs/` are byte-identical copies of method/
  (SHA-256 equal). `DECLARATION_DRAFT.md` holds the decisive quantities, the inclusion rule, the shot formula, the
  480-s cap and the VM rule for option (a).

## 6. Decision needed from the author

(a) Accept the routed embedding of the same model (+17 % CZ, +55 % depth). The device data then remain comparable
with our emulation, DMRG references and map; the text names the routing. Then: seal the declaration, re-run the
tests, submit job A, then job B, post-process on a free VM. (b) A device-native 57-qubit heavy-hex patch: a
different model, which needs new references and emulation, and is not comparable with IBM's dataset. (c) Wait.
Nothing is lost by waiting: the 600 s window is untouched.

## 7. Usage and final state

| Item | Value |
|---|---|
| QPU | 0 s used; 600 s remaining in the rolling window (Open plan, free); no job submitted, no job id |
| VM | 0 VM-hours; no instance started or stopped; gcloud not called |
| Cost | 0 EUR |
| VM final state | unchanged by this run: cj-runner-2 and cj-runner-1b in use by the huang / rigor agents (their RESULTS.md absent) |

## 8. Files (under `phase3/full_runs/qpu/`; SHA-256 in `SHA256SUMS.txt`)

`RESULTS.md`, `DECLARATION_DRAFT.md` (unhashed draft); `code/` (qpu_lib.py, qpu_route.py, ibm_account_check.py,
probe_backends.py, probe_routed.py, diag_core.py, tests/test_bitorder.py, tests/toygraphs.py, method_copy/,
graphs/); `logs_laptop/` (account_check_1/2.json, probe_backends_1.json, probe_routed_1/2.json, diag_core_1.json,
girth_check.txt, square_lattice_check.txt, test_bitorder_run1/2.txt, mps_control_timing.txt).
