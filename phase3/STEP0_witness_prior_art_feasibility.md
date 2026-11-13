# STEP 0 of the witness paper: prior art, rigor of the witnesses, feasibility (2026-10-29)

Working title: "States with the energy of a 115-qubit quantum-learning dataset can carry a different order
parameter". No cloud compute was used. Everything below is reading, arithmetic and one tiny laptop estimate (§3.4).

## Resumen en español sencillo (8 líneas)

1. Busqué a fondo trabajos anteriores. Nadie ha construido todavía, al tamaño del experimento de IBM (57 y 115 cúbits), estados concretos con la misma energía que sus datos y un orden magnético distinto. La idea es nueva en esa forma, pero sus piezas ya se conocen.
2. El trabajo más cercano (Manchanda, 2 de octubre) demuestra la regla de la raíz cuadrada en los dos sentidos. Pero solo vale cuando el error de energía es menor que el salto de energía del sistema, y lo prueba en sistemas pequeños (12 sitios, 20 orbitales, una molécula). Los datos de IBM cerca del borde de fase quedan fuera de ese caso.
3. El artículo de IBM sigue en su primera versión, del 14 de junio. Sus energías solo aparecen en gráficas, y los datos se dan «a petición». El riesgo de que se nos adelanten es medio: Manchanda tiene financiación de IBM en el Reino Unido y ya recomienda mirar más allá de la energía.
4. Encontré una forma rigurosa que no necesita conocer la energía exacta del estado fundamental. Basta con dos estados concretos con una energía menor que la que da el propio conjunto de datos. Si su orden magnético difiere en una cantidad D, ningún método que use solo esa energía puede garantizar el dato con un margen menor que D.
5. Solo falta un dato: la energía exacta de cada punto de IBM. Si dejamos un margen del 20 % por la lectura de las gráficas, la separación baja solo un 11 %. El fundador debería pedir esas energías a los autores; no puede hacerlo un agente.
6. Hice una cuenta de 13 segundos en el portátil con la red pequeña de la misma familia (19 sitios). La separación del orden magnético sale 0,41 en Jz = 1,6 y 0,13 en Jz = 2,5. Si se mantiene con 57 sitios, la prueba previa pasaría con holgura.
7. La geometría de IBM se reproduce exactamente. Recomiendo usar el mismo programa de cálculo que usó IBM, en la máquina de 64 GB. La prueba previa cuesta unos 4-6 euros y un día. El artículo completo, unos 35-50 euros.
8. Regla propuesta: seguir si la separación es de 0,15 o más en Jz = 1,6 y en Jz = 1,2 con 57 sitios; abandonar si baja de 0,05 en Jz = 1,6. El riesgo principal no es el cálculo, sino que los árbitros lo vean como ideas conocidas aplicadas a un caso. Para la revista Quantum es razonable; para Physical Review Letters es difícil.

---

## 0. What was done (budget used)

**Read in full**
- `pilot/RESULTS.md`, `pilot/PRIOR_ART_CHECK.md`, `phase2/J1_editor.md`, `phase2/J2_hostile_referee.md` §0-2 (F1 block),
  and `phase2/G3_constructive_theorem.md` §2 (C1, Theorem 1).
- **Full text** of Manchanda 2610.03989v1: main text and Appendices A-D.
- **Full text and supplement** of 2606.15983v1: main text, Methods, Supplementary I-V.
- 2310.05844v5 (Wang et al.): Sections III-IV in full; the rest skimmed.
- 2511.20860 and 2609.22420: abstract, discussion or end matter, and system sizes, from yesterday's saved full text.

**arXiv API** (`export.arxiv.org`, ≥ 4 s between calls, generic User-Agent, no `mailto`, no personal data)
- 3 `id_list` calls (18 IDs).
- 10 topical searches.
- 1 HTML fetch (2310.05844v5).

**Web searches:** 4 of 4.

**Laptop**
- About 2 s of graph checks.
- One tiny exact-diagonalization estimate: a first attempt was killed at its 90 s timeout and gave no output; the
  reduced run took 13.3 s. That is about 105 s in total, which is over the "seconds" allowance. Declared here; no
  number in this file is a pilot number.

**Raw files (scratchpad, untrusted downloads kept apart from scripts)**
- `C:\Users\Nicolas\AppData\Local\Temp\claude\c--Users-Nicolas-Downloads-Proyecto-SQD-ML\88ff9ed4-5021-4401-9432-f2e610eba8da\scratchpad\step0_witness\dl\`
- `C:\Users\Nicolas\AppData\Local\Temp\claude\c--Users-Nicolas-Downloads-Proyecto-SQD-ML\88ff9ed4-5021-4401-9432-f2e610eba8da\scratchpad\step0_witness\scripts\`

---

## 1. Prior art, deep

### 1.1 Manchanda, arXiv:2610.03989v1 (single author, Oxford Chemistry, 2026-10-02; still v1 today)

**Setting.**
- Non-degenerate ground state, gap Δ.
- Indistinguishability set M_ε = {ρ : E₀ ≤ Tr Hρ ≤ E₀ + ε}.
- "Certification radius" δ_O(M_ε) = sup_{M_ε} |Tr Oρ − O₀₀| (Eq. 3). This is the one-sided version of our width.

**What is proved.**
- **Thm 1 (upper bound), Eq. 7:**
  δ_O ≤ ε‖H_ex^{-1/2} O_ex H_ex^{-1/2}‖ (the "population" term) + 2√(ε A_O(ε)), with A_O(ε) = Σ_{n>0} |O_{0n}|²/(E_n − E₀ + ε)
  (the "coherence" term). Eq. 10 is the capped form, ≤ ‖O_ex‖ + σ_O, finite at every ε but vacuous once ε ≫ Δ.
- **Cor. 1:** δ_O ≲ population + √(2εχ_O), where χ_O = 2A_O is the static susceptibility.
- **Thm 2 (lower bound), Eq. 15:** for ε ≤ Δ̄_O/2, δ_O ≥ √(2εχ_O)·√(1 − ε/Δ̄_O), where Δ̄_O is an O-weighted mean gap
  with Δ ≤ Δ̄_O ≤ Δ_O.
  - The proof (App. B) uses **explicit witness states** ψ± = √(1−p)ψ₀ ± √p·u, with u ∝ H_ex⁻¹Π_ex Oψ₀ (the
    first-order response direction) and p = ε/Δ̄_O.
  - So the √(2εχ) law is **two-sided at leading order** (Cor. 2, a sandwich), not only an upper estimate.
  - But the witnesses are built from the **exact** ground state and spectrum, so they are not computable or certifiable
    at scale. The theorem is perturbative: ε ≤ Δ̄_O/2.
- **Symmetry (Eqs. 17-19):** conserved O loses the coherence term; sector-adapted states see the in-sector gap; there is
  a leakage bound and a selection rule.
- **Discussion:** accuracy target ε ≲ δ*²/(2χ_O) (Eq. 22); asymptotic failure when ε_eff/Δ diverges with L (critical
  gaps L^{−z}). The recommendations are to benchmark beyond energy, use symmetry-adapted ansätze, and track ε/Δ.

**What is shown numerically** (the exact region is computed with the Lagrange form, Eq. 20, from ground energies of
H ∓ λO, credited to Cohen-Feldmann 1971):

| Study | System and size | Observable | Method | Witness of failure |
|---|---|---|---|---|
| VQE | open TFIM chain, L = 12 (ED reference) | magnetization M | hardware-efficient vs parity-preserving ansatz | broken-symmetry optimizer outputs |
| DMRG | two H₅ chains, 20 orbitals | ⟨S²⟩ (conserved, so the region comes from sector energies) | block2 | SZ-DMRG outputs |
| KQD | LiF, 400-dimensional active space | dipole μ | simulated noisy Krylov | Krylov outputs |

**What is not there.**
- No lattice beyond 1D; no system beyond about 20 orbitals or 12 spins.
- No extensive-window regime (ε = nδe ≫ Δ), and no averaged-vs-local split of labels. The asymptotic remark is
  qualitative and in a footnote.
- No explicit witnesses at scale, and no E₀-free (dataset-energy-relative) formulation.
- No learning dataset, no device data (KQD is simulated), no order parameter of a 2D magnet, no uniform-in-parameter
  statement.

**Two facts that matter for us.**
- Its acknowledgements state support from "EPSRC and IBM Research Europe through an Industrial Doctoral Landscape
  Award". It cites 2310.05844 and 2607.04845.
- Its footnote 2 says "the error need not reach the radius". Our title wording "can carry" must keep that distinction.

### 1.2 Jaderberg, Shah, Jeon, Sahin, Zoufal, Sharma, arXiv:2606.15983 (IBM, Oxford, Hartree Centre)

- **Versions.** The API lists **v1 only** (published and updated 2026-06-14): 20 pages, 14 figures, no journal
  reference. The LaTeX date inside the HTML ("August 24, 2026") is a rendering artefact; there is no v2.
- **Model and graphs.**
  - H = ¼Σ(XX + YY + Jz ZZ) on heavy-hex graphs of distance 5 and 7 (n = 57, 115).
  - The SKQD initial state is the Néel state of the two-colouring: 33↑/24↓ and 67↑/48↓. Bitstrings outside that net
    spin are bit-flip-recovered (Supp. II.2), so the dataset states live in that sector.
  - I verified today that `rustworkx.generators.heavy_hex_graph(d)` reproduces exactly:
    - n = 57, bipartition 33/24, 64 edges + 87 second-neighbour pairs = **151** (= their C_zz output dimension);
    - n = 115, bipartition 67/48, 132 + 185 = **317** (= theirs).
- **Labels trained.**
  - ⟨Z_i⟩: 57 / 115 outputs.
  - C_zz = ⟨Z_iZ_j⟩ on first- and second-neighbour pairs: 151 / 317 outputs.
  - Z_loop (12-site Z products): 4 / 12 outputs.
  - The OOD order parameter m_s = (1/N)Σ η_i⟨Z_i⟩ "is not explicitly learned but is derived from the model trained to
    predict ⟨Z⟩".
- **Data split.**
  - Training range 1.6 ≤ Jz ≤ 6.0 in steps of 0.1 (45 points), stratified [1.6, 2.0] / [2.1, 4.0] / [4.1, 6.0], with
    20 % held out.
  - OOD test: 1.1 ≤ Jz ≤ 1.4 from new experiments.
  - Jz = 1.5 was also generated (50 jobs per size; Supp. Fig. 11) but is in neither claim.
- **Claims.**
  - Data vs DMRG: median C_zz errors 1.36 % / 1.22 %, Z_loop 1.57 % / 1.27 % (n = 57 / 115); Z errors are in Supp.
    Fig. 11.
  - ML vs data, in distribution: ≤ 2 % (n = 57), < 1 % (n = 115).
  - **OOD, ML vs new quantum data (not vs truth):** m_s < 3 %; C_zz and loops < 4 %; spatial boundary/bulk structure
    reproduced at Jz = 1.1 (qubits 20 vs 25).
  - The selling line: a "path toward regimes where quantum processors could provide training data beyond the reach of
    classical approximation methods".
- **Energy errors.** They are given **only in figures**, as (E − E₀)/(E₁ − E₀) against TeNPy DMRG at χ = 320 (Fig. 2
  left; Supp. Fig. 9 with and without basis optimization). The gap is in Fig. 4 left.
  - Text: below the gap for Jz ≥ 1.8 (n = 57) and Jz ≥ 2.1 (n = 115).
  - **No energy is reported for the OOD points 1.1-1.4.**
  - Energy is the dataset's acceptance criterion: one job (n = 115, Jz = 3.1) "was resubmitted due to erroneously high
    energy".
  - Digitized values (PRIOR_ART_CHECK §3, ±5 % per factor), with ε = ratio × gap:

    | Jz | n = 57: ratio, gap, ε (J), δe | n = 115: ratio, gap, ε (J), δe |
    |---|---|---|
    | 1.6 | 1.348, 0.463, **0.624**, 0.0110 | 2.716, 0.493, **1.339**, 0.0116 |
    | 2.5 | 0.235, (1.061)†, **0.249**, 0.0044 | 0.464, 1.061, **0.492**, 0.0043 |
    | 4.0 | 0.0523, (1.883)†, **0.0985**, 0.0017 | 0.0765, 1.883, **0.144**, 0.0013 |
    | 1.2 (OOD) | not reported; gap 0.162; floor δe 0.012 → ε = 0.684 (4.2 gaps) | not reported; gap 0.190; floor → 1.38 (7.3 gaps) |

    † The n = 57 gap markers above Jz = 1.6 are hidden under the n = 115 markers; equal gaps are assumed.
  - Relative to |E₀| (about 0.52 J per bond at Jz = 1.6, from the n = 19 estimate in §3.4), ε is about 2 % of |E₀| at
    Jz = 1.6 and about 0.15 % at Jz = 4.
- **Eckart section (Supp. III.1).**
  - From Lemma 1 of the SKQD paper: ‖ψ − φ₀‖² < 2(1 − √(1 − (E−E₀)/(E₁−E₀))) (Eq. 14, Fig. 10), saturated at 1 above
    the gap.
  - They state that "when the energy lies below the gap we can make guarantees as to the closeness of the state" and,
    honestly, that "this bound does not directly control local observables".
  - Worked example, n = 115, Jz = 2.5 (r = 0.464): ‖ψ − φ₀‖ < 0.73 and trace distance ≤ √r = 0.68. That allows label
    errors up to 1.36‖O‖, so their own guarantee is nearly vacuous for labels, even below the gap.
- **Availability.**
  - Data: "available from the corresponding author upon request". Code: "upon reasonable request".
  - The E_dev values must be requested by the author himself, not by an agent.
- **SIN VERIFICAR:**
  - whether the reported E is an exact Rayleigh quotient (it is, if the single-layer OBP conjugation is untruncated;
    probably yes);
  - whether E₁ is the in-sector first excited state or the lowest state in Sz ± 1;
  - whether observables were computed with the rotated operators UOU†.

### 1.3 Wang, Surace, Frérot, Legat, Renou, Magron, Acín, arXiv:2310.05844v5 (PRX 14, 031006)

- **Method (§III, Eq. 6).** An NPA moment SDP with two added constraints: E_A − H ⪰ 0 in expectation (variational
  upper bound) and H − E_R ⪰ 0 (relaxation lower bound). It bounds any observable: "correlation functions of
  arbitrary order, structure factors, or order parameters".
- **Systems.** Translation-invariant, periodic, isotropic Heisenberg models:
  - chain N ≤ 100;
  - J1-J2 chain N = 40 (and N = 100 for energies);
  - square lattice L ≤ 10;
  - J1-J2 square lattice.
- **Observables bounded.** C₁, C₂, C(r); long-range C(L/2, L/2) is certified positive for L ≤ 8, and the bounds
  "become increasingly looser" with L.
- **The window** is the tiny DMRG/QMC-to-SDP energy gap, not a device error.
- **Absent:** no witnesses, no device energies, no learning, no single-instance or non-translation-invariant labels.
- **Follow-up 2604.01555v2** (SciPost Phys. 21, 074): structured relaxations up to a 16 × 16 square lattice.
- **Related:** 2512.17713 (Naceur, Wang, Magron, Acín) turns inexact SDP output into rigorous bounds. Relevant only if
  we ever need a certified E₀ lower bound.

### 1.4 Bootstrap line

- **2511.20860v1** (Scheer, Chadha, Lu, Khalaf, 2025-11-25).
  - Abstract: bounds "inevitably become loose in symmetry broken phases". Discussion: deep in the SSB phase "any value
    of ⟨Z₀⟩ in the interval [−1, 1] is actually allowed". The cause is order-parameter defects (domain walls).
  - The fix is a defect model with ancillas. Demonstrated on infinite 1D/2D TFIM.
- **2609.22420v1** (Banerjee, Guo, Chowdhury, 2026-09-18).
  - String bootstrap; the window uses DMRG χ_max = 300 upper bounds. Sizes: TFIM N = 30, cluster-Ising N = 20,
    spin-1 Heisenberg N = 10.
  - End matter: perturbative-positivity (optimality) bounds are "considerably looser than variational ones", and
    "when low-lying states are quasi-degenerate … the bounds necessarily encompass this entire low-energy manifold".
- **2610.06272v1** (Vallée, Kelman, Mildenberger, Tura, Emonts, 2026-10-05): window-SDP two-sided bounds for lattice
  gauge theories (129 sites in 1D, 97 sites in 2D). No witnesses.

All three are certifier-side (outer bounds). None constructs inner witnesses at scale or touches learning data.

### 1.5 Search for "explicit low-energy states with wrong observables at scale, for a learning or benchmark dataset"

**arXiv API, 10 searches.**
- energy ∧ observable ∧ certif* ∧ variational ∧ "ground state": 4 hits (2310.05844, 2610.03989, 2610.06272,
  2609.22420), all covered above.
- "energy window" ∧ observable*: 0.
- "quantum data" ∧ "ground state" ∧ learning ∧ (certif* ∨ verif* ∨ labels): 2, both irrelevant (QCNN interpretability;
  toric-code quantum-data learning, 2511.16851).
- "heavy-hex" ∧ XXZ: 1, irrelevant (central charge, 2408.06342).
- ti: energy ∧ "not enough": 16 hits. Two are on-topic but small and unrelated to witnesses:
  - 2607.04845v2 (Niu et al., HamQASBench, molecules ≤ 14 qubits; "equal-energy outputs on a degenerate instance occupy
    distinct spin components");
  - 2609.13521v1 (Chen, VQE particle-number leakage).
- SQD/SKQD ∧ observables ∧ accuracy/certification: 2 hits, irrelevant.
- "energy error" ∧ observable ∧ susceptibility/amplification/certif*: 0.
- learning ∧ "ground state" ∧ out-of-distribution ∧ observables: 2606.15983 itself, plus one DFT paper.
- variational ∧ order parameter ∧ low-energy ∧ misleading/wrong/spurious: 0.
- "close in energy" ∧ observables: 0.

**Web searches, 4.**
- No follow-up, comment, data release or certified-label analysis of 2606.15983 was found. The hits were scirate,
  chatpaper and alphaxiv mirrors, plus related learning-from-quantum-data experiments: 2310.19416 (Cho, Kim, Nat.
  Commun. 15, 7552) and 2601.03235 (IBM SKQD-based learning).
- No paper constructs energy-window witnesses at 50-100+ qubits.
- Generic lore resurfaced: energy converges quadratically and hides wavefunction errors; certifying that an MPS ground
  state has been found is hard (Schuch et al., 0802.3351).

**Classical ancestors to cite (not re-verified today; all cited inside 2610.03989):**
- Eckart 1930;
- Weinhold 1968 (lower bounds to expectation values);
- **Cohen-Feldmann 1971 (Lagrange-multiplier bounds: exactly our λ-scan of H − λO);**
- Blau-Rau-Spruch 1973;
- Lucha-Schöberl 2000;
- Mora-Waintal 2007 (variational overlap);
- Zheng et al. 2017 (near-degenerate competing stripe orders in the Hubbard model: the folk version of our claim);
- V-score benchmarks, 2302.04919 (Science 386, 296), an energy-based benchmark culture.

Absence of hits is evidence about abstracts and search engines only.

### 1.6 Verdict

**Is the witness-at-scale result new?** **Yes in form, no in mechanism.**
- No paper found builds explicit states, at the size of a published quantum-learning experiment (57/115 qubits, 2D
  heavy-hex), that:
  - are in the experiment's own symmetry sector;
  - lie below the experiment's own energy;
  - and carry a different order parameter or different local labels.
- The mechanism is known:
  - Weinhold, Cohen-Feldmann, Eckart;
  - Manchanda's √(2εχ) sandwich and witness states ψ±;
  - the bootstrap papers' "the window encompasses the whole low-energy manifold";
  - Hubbard competing-order lore.

**What we would add beyond Manchanda (each item must be in the abstract or it does not count):**
1. **Regime.**
   - At the dataset's own errors, ε exceeds the gap: ε/Δ = 1.35 (n = 57) and 2.7 (n = 115) at Jz = 1.6, and 4-7 at
     the OOD point with the floor error.
   - Thm 2 needs ε ≤ Δ̄_O/2 and the exact spectrum. Thm 1/Eq. 10 is vacuous there.
   - Our witnesses are non-perturbative and computable: MPS ground states of H ∓ λO, and their mixtures.
2. **Rigor without E₀** (§2). The window is defined by the dataset's own energy E_dev, using two-sided witnesses. No
   lower bound on E₀ and no knowledge of ⟨O⟩_GS is needed. Manchanda's ψ± need the exact ψ₀.
3. **Scale and object.** A real 2D learning dataset, with its sector, its five label families, its training/OOD split
   and its energy-based quality criterion. A label-by-label map: which labels the dataset's energy can and cannot
   certify.
4. **Extensive-window scaling,** which Manchanda does not state:
   - averaged labels have an intensive witness width, D ≈ 2√(2δe·χ_site) at small δe, saturating non-perturbatively;
   - local labels (Z_i, single-edge C_zz, Z_loop) reach the full range beyond N* = ε_U/δe (C1 Thm 1(b), our
     constructive one-liner);
   - the Hellmann-Feynman-conjugate edge average stays narrow.
5. **A device-accuracy requirement per label** at scale: δe*(O) = energy density needed to certify O to the reported
   few-% level. It is intensive for averages and impossible (it shrinks as 1/N) for local labels. This is
   Manchanda's Eq. 22 recast for extensive windows and evaluated on the dataset.
6. **The positive half:**
   - the certifiable set (edge-averaged ZZ, second-neighbour average);
   - the corrected uniform-in-Jz bracket, attacked and tight to 2 %. It is only DMRG-referenced at scale; see §3.6.

**Scoop risk.**
- **IBM v2:** none so far (API, 2026-10-29). v1 is 4.5 months old, so a journal revision could appear at any time.
  - The text already concedes that Eckart "does not directly control local observables". A referee-driven revision
    would more likely add a caveat than witnesses.
  - Risk that IBM itself publishes witnesses: low (≈ 5-10 % in 6 months, my judgment).
- **IBM-adjacent analysis:** Manchanda is IBM-Research-Europe-funded at Oxford. 2606.15983 has IBM Research Europe and
  Oxford authors. He holds the exact tool and ends with "benchmark beyond the energy". Risk that he or IBM posts a
  certification-radius analysis of this dataset: **medium (≈ 15-25 % in 6 months, my judgment).**
- **Bootstrap groups:** they work on the certifier side and are unlikely to build witnesses for a learning dataset
  (≈ 5 %).
- **Mitigation:** the pilot takes one day; move to a posted preprint within 4-6 weeks if it commits.

**Honest positioning risk (the strongest referee objection).**
- "IBM never claimed that energy certifies labels; they benchmarked labels against DMRG. Witnesses are ground states of
  H − λO (1971), and DMRG on 115 sites is routine."
- The answer must be the beyond-classical argument. In the regime IBM motivates, no DMRG check exists. Energy (with
  E₀ and E₁ unknown) is then the only quality signal, and we quantify per label what it can and cannot guarantee at
  their errors.
- Never write that their labels are wrong. Witnesses show possibility, not actuality.

---

## 2. Rigor: when a DMRG witness is a rigorous lower bound on the certification width

### 2.1 Definitions

- **H:** H(Jz) on the heavy-hex graph.
- **Π:** projector on the dataset's sector, Sz = (n_A − n_B)/2 (33/24 or 67/48 up/down).
- **O:** a label (m_s, Z_i, Z_iZ_j, Z_loop, C̄_zz, …).
- **Window:** W(E) = {σ ⪰ 0, Tr σ = 1, ΠσΠ = σ, Tr Hσ ≤ E}.
- **Information limit:** I_O(E) = [min_{W(E)} Tr Oσ, max_{W(E)} Tr Oσ], with width w_O(E).
- **Energy-only certificate at threshold E:** any interval J whose soundness rests only on membership in W(E), i.e.
  J ⊇ {Tr Oσ : σ ∈ W(E)}. This covers:
  - every window moment-SDP or bootstrap at any level (Wang et al.; 2609.22420; 2610.06272);
  - Eckart, Weinhold and Manchanda radius bounds;
  - IBM's Eq. 14 used as an observable bound.

  It does **not** cover relaxations that add ground-state optimality constraints (⟨[H,G]⟩ = 0, ⟨G†[H,G]⟩ ≥ 0),
  because the witnesses are not eigenstates. The 1D pilot found those constraints inactive at level 2 (B = B0, 13/13
  cells); that is a relaxation fact, not a theorem.

### 2.2 Proposition W (rigorous, E₀-free)

**Statement.** Let φ₊, φ₋ be explicit normalized states (MPS, or density matrices such as mixtures of two MPS) with
Πφ± = φ± and ⟨H⟩_{φ±} ≤ E. Let D = ⟨O⟩_{φ₊} − ⟨O⟩_{φ₋}. Then:
- **(a)** w_O(E) ≥ D, so every energy-only certificate at threshold E has width ≥ D;
- **(b)** for every real o, in particular the unknown o = ⟨O⟩_GS, max± |⟨O⟩_{φ±} − o| ≥ D/2. The energy E is
  compatible with a state whose label is off by at least D/2;
- **(c)** for E' ≥ E, (a)-(b) hold at E'.

**Proof.** φ± ∈ W(E) ⊆ W(E'). An interval containing both values has width ≥ D. The triangle inequality gives (b). ∎

**Corollary (dataset).** With E = E_thr ≤ E_dev(n, Jz), the energy reported for the dataset state:
- the dataset's energy cannot certify its O-label to better than D;
- it is compatible with a label error ≥ D/2 relative to the ground-state value, **whatever E₀ and ⟨O⟩_GS are**.

This needs only that E_dev upper-bounds E₀, which is automatic if E_dev is a Rayleigh quotient of a sector state.

### 2.3 What makes the numbers rigorous

1. **Exact evaluation.** ⟨φ|φ⟩, ⟨φ|H|φ⟩ and ⟨φ|O|φ⟩ come from exact MPS-MPO contraction of the stored MPS, not the
   DMRG-reported energy, in double precision.
   - The rounding error is below about 1e-10 J at these sizes (‖H‖₁ ≈ 10² J).
   - Require ⟨H⟩ ≤ E_thr − 1e-6 J.
   - Re-evaluate the stored witnesses in a second library (ITensor) and require agreement to 1e-8.
2. **Sector exactness.** U(1) block-sparse tensors carry exact charges. Check ⟨(S^z_tot − s)²⟩ < 1e-12.
3. **Convergence is not needed for rigor.** An unconverged MPS is still an explicit state. DMRG convergence affects
   only tightness, i.e. how close D comes to the true w_O. Only the reference energies used to build E_thr (§2.4) need
   care.
4. **Mixtures.** For a target E_thr between two λ runs, the mixture σ = (1−t)φ_a + tφ_b has affine energy and label.
   It is a valid window element, so a coarse λ grid still gives rigorous witnesses.

### 2.4 The threshold E_thr (the only non-computational input)

E_dev = E₀^IBM + r·Δ^IBM. Here r is read from Fig. 2 / Supp. Fig. 9 (±5 %), and E₀^IBM, Δ^IBM are their TeNPy χ = 320
values, which are not published. Until the authors send E_dev, use:

> **E_thr = E₀^ours(χ = 320) + (1 − m)·r_read·Δ_min^ours, with m = 0.2.**

- Δ_min^ours is the smaller of the in-sector E₁ (orthogonalized DMRG) and the lowest Sz ± 1 energy, because IBM's
  definition of E₁ is unverified.
- **Per-n errors, not the pinned maximum over n.** At n = 57 the pinned 0.012 overstates ε by 9 %.

**Validity condition.** E_thr ≤ E_dev holds if E₀^ours − E₀^IBM ≤ [1 − 0.8 × 1.05 × 1.10]·ε = 0.076·ε, given:
- |r_read/r − 1| ≤ 0.05;
- our gap within 10 % of theirs.

Since E₀^IBM ≥ E₀^true, it suffices that E₀^ours − E₀^true ≤ 0.076·ε. **Gate:** |E₀(χ = 320) − E₀(χ = 480)| ≤ 0.02·ε
in the pilot, a 4× safety factor. The residual non-rigor is this extrapolation and the pixel reading. Both disappear
if the authors provide E_dev; then E_thr = E_dev.

**Cost of the margin.** D grows like √ε, so a 20 % energy margin costs √0.8 ≈ 0.89, about −11 % of D.

### 2.5 The E₀-relative version and why it is not the theorem

W'(ε) = W(E₀ + ε). Rigorous membership needs ⟨H⟩ ≤ E₀^low + ε, with a certified lower bound E₀^low.
- At 2D n = 57/115, relaxation slacks of order 1 % of |E₀| (about 0.33 J at n = 57 and 0.7 J at n = 115 for Jz = 1.6)
  eat 50 % of the window at Jz = 1.6 and all of it at Jz ≥ 2.5.
- So the ε-relative statement is used **only under a stated DMRG assumption**: E₀^true ≥ E₀^DMRG − δ_extrap, with
  δ_extrap from the χ-extrapolation as in IBM Supp. Fig. 5.
- This inherits exactly IBM's own assumption: their δe is DMRG-referenced too.
- The OOD points (no reported E) are **conditional**: "if the device error at Jz ≤ 1.4 is at least the Jz = 1.6
  value". Report D(δe) and δe*(O) there as well.

### 2.6 Arithmetic margin vs the pinned δe

| (n, Jz) | ε (J) | margin 0.2ε (J) | rounding | DMRG E₀ reproduction (expected) | pixel reading |
|---|---|---|---|---|---|
| 57, 1.6 | 0.624 | 0.125 | ~1e-10 | ≲ 1e-3 | ±7 % of ε |
| 57, 2.5 | 0.249 | 0.050 | ~1e-10 | ≲ 1e-4 | ±7 % |
| 57, 4.0 | 0.0985 | 0.020 | ~1e-10 | ≲ 1e-5 | ±7 % |
| 115, 1.6 | 1.339 | 0.268 | ~1e-10 | ≲ 5e-3 (SIN VERIFICAR) | ±7 % |
| 115, 2.5 | 0.492 | 0.098 | ~1e-10 | ≲ 1e-3 | ±7 % |
| 115, 4.0 | 0.144 | 0.029 | ~1e-10 | ≲ 1e-4 | ±7 % |

- The binding uncertainty is the figure reading, not numerics. The 20 % margin covers it 3× in quadrature.
- Even the smallest window (n = 57, Jz = 4: 0.020 J) leaves a ≥ 20× margin over the expected DMRG mismatch and ~10⁸×
  over rounding.

---

## 3. Feasibility (no runs)

### 3.1 Geometry and MPO size (checked today)

- `heavy_hex_graph(5)` and `heavy_hex_graph(7)` reproduce IBM's node counts, bipartitions and C_zz output dimensions
  (§1.2). Degrees: 2 / 39 / 16 sites of degree 1 / 2 / 3 (n = 57) and 2 / 77 / 36 (n = 115). Mean degree is 2.25-2.3:
  strong quantum fluctuations.
- With a breadth-first ordering, the maximal number of edges crossing an MPS cut is **7 (n = 57) and 11 (n = 115)**.
  The index ordering gives 58 / 122 and must not be used.
- MPO bond dimension ≈ 2 + 3 × crossing ≈ **23 and 35**. A spectral (Fiedler) ordering may shave 1-2 crossings.
- Witness fields (staggered or local Z) are on-site and do not change the MPO. Z_loop is one 12-site string term, +1
  bond across its span.

### 3.2 Library choice

| Option | For | Against | Use |
|---|---|---|---|
| **TeNPy** (Python) | IBM's own reference: same library and χ = 320, so "our E₀ and gap reproduce theirs" is a clean check. `SpinHalfSite(conserve='Sz')`; arbitrary long-range couplings via `add_coupling_term(i, j)` on a chain in BFS order; on-site and multi-site terms; `orthogonal_to` for E₁; exact `MPO.expectation_value` | Python overhead, slower than ITensor (my estimate 2-3×) | **Primary** |
| **ITensorMPS.jl** (Julia) | QN block-sparse, OpSum compresses long-range MPOs, multithreaded blocks, fast | New stack (Julia install about 10 min plus precompile); not IBM's tool | **Independent re-evaluation** of stored witnesses and of 2-3 E₀ values |
| block2 | Fastest CPU DMRG (Manchanda used it) | Spin-lattice setup on arbitrary graphs is less standard | Not needed |
| quimb | Easy | Dense by default: no native U(1) sector, so a penalty would be needed and the sector exactness of §2.3 is lost | **Not recommended** |

### 3.3 Cost per run on n2-highmem-8 (8 vCPU = 4 physical cores, 64 GB, no GPU, 0.594 EUR/h list)

**Flop estimate at χ = 320, d = 2, MPO bond dimension D_W.**
- Per two-site matvec: ≈ 2χ³d²D_W + χ²d⁴D_W² ≈ 1.1e10 flops (n = 115, D_W = 35).
- About 6 Lanczos steps per bond and 2n bond updates per sweep give ≈ 1.5e13 flops dense, ≈ 2-4e12 with U(1) blocks.
- At ≈ 40 GFLOP/s effective (4 threads), that is **≈ 1-2 min per sweep (n = 115)** and ≈ 15-30 s (n = 57).

**Per run (×3 uncertainty either way):**

| Run type | n = 57 | n = 115 |
|---|---|---|
| Cold ground state (χ ramp 40 → 320, about 12 sweeps) | ≈ 4 min | ≈ 15 min |
| E₁ (orthogonalized) | ≈ 6 min | ≈ 22 min |
| Warm-started witness at one λ (4-6 sweeps) | ≈ 2.5 min | ≈ 8-10 min |

- Witness states with pinning fields are less entangled and usually cheaper.
- Near Jz = 1.1-1.2 the bond dimension saturates and runs cost more.
- **Memory:** environments ≈ n·χ²·D_W·8 B ≈ 3 GB (n = 115). Run 2 jobs × 4 threads concurrently; 64 GB is ample.

**Runs needed for the full paper.**
- Points: 2 sizes × 11 Jz (1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 4.0, 6.0).
- Per point:
  - 3 reference runs (E₀, E₁, χ-check);
  - ≈ 14 m_s witness runs (2 signs × about 7 λ with bisection);
  - ≈ 30 local-label witness runs (Z_i at 3 sites, one edge C_zz, one Z_loop; 2 signs × 3 λ);
  - ≈ 6 runs for the C̄_zz / C̄₂ information limit (E₀ on a Jz' grid).
- That is ≈ 1,170 runs: about 24 job-hours (n = 57) plus 97 (n = 115), ≈ 121 job-hours. Two concurrent jobs give
  ≈ 60-85 VM-hours.
- **Cost ≈ 35-50 EUR** (range 15-150 EUR at ×3). This is affordable but larger than the pilot; n = 115 local-label
  scans can be thinned without loss, since Thm 1(b) guarantees them.

### 3.4 Laptop prior (13 s, n = 19 heavy-hex d = 3; not a pilot number)

**Setup.**
- Exact sector diagonalization: 11↑/8↓, dimension 75,582.
- Witnesses are ground states of H ∓ λM_s on a 9-value λ grid, with mixture interpolation at ε = δe·19. These are
  inner bounds, so D below is a lower bound on the n = 19 information-limit width.
- Script: `...\scratchpad\step0_witness\scripts\hh19_prior_small.py`.

| Jz | δe | ε (J) | ε/gap* | m_s (GS) | witness window for m_s | D(m_s) | Δ(m_s²) |
|---|---|---|---|---|---|---|---|
| 1.6 | 0.012 | 0.228 | 0.23 | 0.733 | [0.470, 0.884] | **0.414** | 0.56 |
| 2.5 | 0.0044 | 0.084 | 0.05 | 0.882 | [0.807, 0.932] | **0.125** | 0.22 |

\* The gap comes from a symmetric Lanczos start, so it is the lowest in-sector state of the lattice-symmetric irrep and
may overstate the true gap. D does not use it.

**Readings.**
- The implied effective staggered susceptibility is χ_site ≈ 1.8 (Jz = 1.6) and ≈ 0.44 (Jz = 2.5), from D/2 ≈
  √(2δe·χ_site). The window is asymmetric: m_s saturates toward 1.
- **Device-accuracy requirement (prior).** Certifying m_s from energy to the few-% level the dataset reports (δ* ≈
  0.03·m_s) needs δe* ≈ δ*²/(2χ_site):
  - ≈ 1.3e-4 at Jz = 1.6, **about 90× below** the dataset's 0.012;
  - ≈ 8e-4 at Jz = 2.5, ≈ 6× below its 0.0044.
- **Caveat.** n = 19 is boundary-dominated, and its windows lie below the gap. At n = 57/115 the windows are above the
  gap (extensive regime), where the intensive estimate D ≈ 2√(2δe·χ_site) should hold if χ_site has converged. That is
  exactly what the pilot tests.

### 3.5 Pilot (1-2 days, ≤ 10 EUR), declared before any run

**Decisive quantity.**
- Q(Jz) = D(m_s), the two-sided witness separation of the **linear** staggered magnetization (IBM's label), for n = 57.
- Threshold: E_thr = E₀ + 0.8·r_read·Δ_min (§2.4) at Jz = 1.6 (ε ≈ 0.62 J) and 2.5 (ε ≈ 0.25 J).
- At the OOD point Jz = 1.2: E₀ + 0.8 × 0.012 × 57 = E₀ + 0.55 J (conditional floor).
- Equivalent in the coordinator's units: Δ(m_s²) ≈ 2m_s·D ≈ 1.5·D at m_s ≈ 0.75.

**Rules (thresholds 3× apart).**
- **COMMIT** if Q(1.6) ≥ 0.15 **and** Q(1.2) ≥ 0.15 (≈ Δm_s² ≥ 0.2), and all gates below pass.
- **KILL** the order-parameter headline if Q(1.6) < 0.05 (≈ Δm_s² < 0.08).
  - Then the dataset's energy pins m_s to ±0.025 (≈ 3 %), consistent with IBM's claims.
  - What survives is a short Quantum note on local labels and the label map.
- **GRAY** otherwise: Quantum paper with local-label witnesses plus the label map; no PRL.
- **Recorded, not decisive:**
  - Q(2.5) (prior ≈ 0.12);
  - local-label witnesses Z_bulk, Z_boundary, Z_loop at Jz = 1.2 and 1.6 (expected ≥ 0.4 by Thm 1(b) at n = 57);
  - n = 115 intensivity D(115)/D(57) at Jz = 1.6 (expected 0.7-1.5; otherwise flag).
- **Prior from §3.4:** Q(1.6) ≈ 0.3-0.4. P(COMMIT) ≈ 0.7, P(KILL) ≈ 0.05 (my judgment). The real risk is novelty, not
  the number.

**Gates (fail means no decision).**
- (G1) The n = 19 TeNPy unit test reproduces the ED values to 1e-6: E₀ = −10.3643 (Jz = 1.6), −14.1015 (2.5); m_s =
  0.733 / 0.882. Its witness D must be ≥ 0.40 / ≥ 0.12.
- (G2) |E₀(χ = 320) − E₀(χ = 480)| ≤ 0.02·ε at Jz = 1.2 and 1.6.
- (G3) Our gap within 10 % of IBM's Fig. 4 at Jz = 1.2 and 1.6 (0.162, 0.463 for n = 57). If not, E₁'s definition is
  unresolved and E_thr uses Δ_min.
- (G4) Every witness passes §2.3 (exact energy, sector, ITensor re-evaluation of the 6 decisive witnesses).

**Run list and cost.**

| Stage | Runs | Est. job-min | VM-h (2 concurrent) |
|---|---|---|---|
| Install (TeNPy pinned, rustworkx) and the n = 19 unit test | — | 30 | 0.5 |
| n = 57 references: E₀ at χ 160/320/480 × Jz {1.2, 1.6, 2.5}; E₁ in-sector and Sz − 1 × 3 | 15 | ≈ 80 | 0.7 |
| n = 57 m_s witnesses: 3 Jz × 2 signs × about 7 λ (bisection) | 42 | ≈ 105 | 0.9 |
| n = 57 local witnesses: 3 labels × 2 signs × 4 λ × Jz {1.2, 1.6} | 48 | ≈ 100 | 0.8 |
| n = 115, Jz = 1.6: E₀ (χ 160/320), E₁, m_s witnesses 2 × 6 | 15 | ≈ 170 | 1.4 |
| ITensor install and re-evaluation (6 witnesses + 2 E₀) | 8 | ≈ 40 | 0.5 |
| **Total** | ≈ 130 | ≈ 9 job-h | **≈ 5 VM-h ≈ 3 EUR**; ×1.5 contingency and the program's ×1.25 → ≈ 6 EUR |

- **Hard cap:** stop at 15 VM-h (8.9 EUR). If runs are 3× slower than estimated, cut the n = 115 stage first; it is
  not decisive.
- Wall time: about 1 day including setup; about 2 days at the hard cap.

### 3.6 What is rigorous and what is DMRG-referenced at scale

- **Rigorous (Prop. W):** every witness lower bound on widths and errors, given E_thr ≤ E_dev.
- **DMRG-exact but not rigorous:** the outer side of the information limit, i.e. its upper end. Its dual needs lower
  bounds on ground energies of μH − O, so DMRG supplies only the inner side.
- **Also DMRG-referenced at scale:**
  - the certifiable set (C̄_zz, C̄₂), whose width bound uses E₀(Jz') at neighbouring Jz';
  - the corrected uniform-in-Jz bracket, whose slack g would need a relaxation at n = 57/115.

  State both as "DMRG-referenced". Rigorous versions exist only at n ≤ 27 (ED/SDP), or with a 2604.01555-type
  structured relaxation at n = 57 (SIN VERIFICAR whether it is usable on heavy-hex).
- The witness half (the headline) does not depend on any of this.

---

## 4. Venue and recommendation

- **Physical Review Letters (subscription route).** The hook would be the general statement: energy validation of
  quantum-generated training data does not scale for spatially resolved labels, and certifies order parameters only if
  δe ≲ δ*²/(2χ_site), shown with explicit 115-qubit witnesses on a real dataset.
  - Weaknesses: the theory pieces are elementary (Thm 1(b), Cohen-Feldmann, Manchanda), and the target is an
    unpublished v1 preprint whose authors already concede the point qualitatively. Editors may read it as a Comment.
  - My odds: P(referees) ≈ 0.15-0.25, P(accept) ≈ 0.03-0.06.
- **Quantum.** A natural fit for "what quantum-generated labels can be certified": witnesses, label map, certifiable
  set, uniform bracket.
  - If the pilot commits: P(referees) ≈ 0.4, P(accept) ≈ 0.15-0.2. This is consistent with J1's F-A numbers, a little
    higher because the witness half is constructive and rigorous.
- **Title.** Keep "can carry" (possibility, not actuality). Per J1, the abstract's first sentence should state the
  constructive result (explicit witnesses plus the per-label accuracy requirement), not "only averages".
- **Author's own steps** (not for an agent):
  - request the E_dev values, and ideally the m_s / Z_i data at Jz = 1.1-1.6, from the 2606.15983 corresponding
    author;
  - decide PRL vs Quantum after the pilot.
- **Next action.** Run the pilot of §3.5 as declared (≤ 10 EUR). Write nothing before COMMIT.

---

## Annex A. Identifiers verified today (arXiv API, title match)

| ID | Version / date | Title (short) | Note |
|---|---|---|---|
| 2606.15983 | v1 only, 2026-06-14 | Learning ground state observables from quantum computing experiments | 20 pp, 14 figs |
| 2610.03989 | v1, 2026-10-02 | Certification failure in variational-principle observables | 10 pp |
| 2310.05844 | v5, 2024-07-18 | Certifying ground-state properties of quantum many-body systems | PRX 14, 031006 |
| 2604.01555 | v2, 2026-08-12 | Scalable ground-state certification … structured NC polynomial optimization | SciPost Phys. 21, 074 |
| 2511.20860 | v1, 2025-11-25 | Defect bootstrap | |
| 2609.22420 | v1, 2026-09-18 | Bootstrap certification of string order | |
| 2610.06272 | v1, 2026-10-05 | Two-sided bounds … lattice gauge theories | |
| 2311.18707 | v5, 2026-02-21 | First-order optimality conditions for NC optimization | Found. Comput. Math. 2026 |
| 2607.04845 | v2, 2026-09-11 | Energy accuracy is not enough (HamQASBench) | |
| 2609.13521 | v1, 2026-09-11 | Energy is not enough: leakage-aware ansatz criterion | |
| 2511.16851 | v1, 2025-11-20 | Quantum data learning … toric code loop gas | |
| 2512.17713 | v2 | Certified bounds on optimization problems in quantum theory | |
| 2603.17856 | v1, 2026-03-18 | Toward bootstrapping tensor-network contractions | |
| 2302.04919 | v2 | Variational benchmarks for quantum many-body problems | Science 386, 296 |
| 2310.19416 | v1 | Machine learning on quantum experimental data … | Nat. Commun. 15, 7552 |
| 2512.19420 | v1 | Generative Krylov subspace representations | |
| 2601.03235 | v1 | Shallow-circuit supervised learning on a quantum processor | |
| 2610.23138 | v1 | Sample-based quantum linear solver … | irrelevant |

Not re-verified today (classical references, as cited inside 2610.03989): Eckart 1930, Weinhold 1968, Cohen-Feldmann
1971, Blau-Rau-Spruch 1973, Lucha-Schöberl 2000, Mora-Waintal 2007, Zheng et al. 2017. Also 0802.3351, which surfaced
in a web search and was not checked by the API.

## Annex B. Web sources (4 searches)

- [arXiv 2606.15983 PDF](https://arxiv.org/pdf/2606.15983)
- [chatpaper listing of 2606.15983](https://chatpaper.com/chatpaper/paper/299576)
- [alphaxiv 2606.15983v1](https://alphaxiv.org/audio/2606.15983v1)
- [scirate listing](https://scirate.com/abhinav-deshpande/scites?page=2)
- [arXiv 2310.19416](https://arxiv.org/pdf/2310.19416)
- [arXiv 2601.03235](https://arxiv.org/html/2601.03235v1)
- [arXiv 2512.19420](https://arxiv.org/pdf/2512.19420)
- [arXiv 2310.05844](https://arxiv.org/pdf/2310.05844)
- [arXiv 2512.17713](https://arxiv.org/pdf/2512.17713)
- [arXiv 2603.17856 (alphaxiv)](https://www.alphaxiv.org/abs/2603.17856)
- [MPS approximations of low-variance states (Quantum 2024)](https://quantum-journal.org/papers/q-2024-07-10-1401/)
- [Schuch QIP 2009 talk](https://qipconference.org/2009/talks/28-Schuch-QIP-2009.pdf)

## Annex C. SIN VERIFICAR (open items)

- Whether IBM's E is an exact Rayleigh quotient (untruncated OBP), and whether their E₁ is in-sector or Sz ± 1.
- IBM's DMRG convergence |E(320) − E(∞)| near Jz = 1.1-1.6 at n = 115 (Supp. Fig. 5, not digitized).
- Whether χ_site at n = 57/115 matches the n = 19 prior (that is what the pilot measures).
- The run times in §3.3 (estimates, ×3).
- Whether the 2604.01555 code runs on heavy-hex at n = 57.
- Whether IBM's m_s data lie on the over-ordered side (σ₊ direction), as a Néel-seeded sampling bias would suggest.
  This hypothesis needs their data.
