# R3: from one dataset to a general result (2026-10-29)

## Resumen en español sencillo (8 líneas)

1. Convertí el resultado de un solo conjunto de datos en tres reglas generales, con demostraciones completas y constantes explícitas, válidas para cualquier red de vecinos cercanos.
2. Regla 1 (datos locales: un sitio, un enlace, un anillo): la energía deja de garantizar nada en cuanto el sistema supera un tamaño N* = (costo local de energía) / (error por sitio). Desde ahí el rango posible es completo. Para IBM la cota segura es de unos 470 cúbits; en la práctica ya se nota con 57.
3. Regla 2 (promedios sobre toda la red): la duda no crece con el tamaño. Vale unas 2·√(2·χ·error por sitio), aun cuando el error total supera con mucho el salto de energía. Esto corrige al trabajo más cercano (Manchanda), que solo lo prueba con error menor que el salto.
4. Regla 3 (la más general): un dato se puede garantizar con la energía solo si moverlo cuesta una energía que crece con todo el sistema. Eso falla en datos locales, en puntos críticos y en fases ordenadas con paredes baratas. El orden de IBM sí queda anclado por su sector, y por eso sale estable.
5. Lo comprobé con cálculos exactos pequeños (hasta 12 sitios, cadenas y redes planas, imanes de Ising y XXZ): unas 300 comprobaciones, ninguna falla.
6. Datos publicados: solo hay otro conjunto de datos de chip con valores del estado fundamental usado para aprendizaje automático (Cho y Kim, 2024, IBM, 12 sitios). Es el segundo objetivo, con coste casi cero. El tercero es el conjunto público de referencia de Huang y colaboradores, por menos de 2 euros.
7. Con honestidad: la idea general («la energía controla los promedios y no los datos locales») ya se conoce. Lo nuevo es la versión precisa: las constantes, el «si y solo si», la validez muy por encima del salto, los exponentes críticos y la condición de anclaje.
8. No gasté dinero. Usé 10 consultas a arXiv, 3 búsquedas web y 3 lecturas de páginas. Algunas pruebas tardaron hasta un minuto, más de los «segundos» pedidos.

---

## 0. What was done (budget, deviations)

**Read in full:** `phase3/pilot_witness/RESULTS.md` and `TABLES.md`, `phase3/STEP0_witness_prior_art_feasibility.md`,
`phase2/G3_constructive_theorem.md` and `phase2/J2_hostile_referee.md` (§0-2 in full, the rest skimmed). I re-read the
theorem statements, the Lagrange section and the discussion of Manchanda 2610.03989v1 from the full text saved on
2026-10-29 (`scratchpad/pilot_step0/dl/2610.03989.txt`).

**Literature**
- **arXiv API:** 10 calls (2 `id_list`, 8 searches), ≥ 4.5 s apart, generic User-Agent, no `mailto`, no personal data. All
  raw XML is in `scratchpad/r3gen/dl/` (`ids1.xml`, `ids2.xml`, `s1.xml` … `s8.xml`).
- **Web searches:** 3 of 6.
- **Page fetches:** 3 (WebFetch, public pages only). nature.com was refused by a login redirect. The arXiv PDF of
  2310.19416 was read as text with `pypdf`, from a copy kept in its own folder (`dl/cho_kim/`). The arXiv HTML of 2601.03235 was summarized.

**Laptop: tiny exact diagonalization only** (n ≤ 12, BLAS single-threaded)
- Scripts are in `scratchpad/r3gen/scripts/` and outputs in `scratchpad/r3gen/out/`.
- Successful runs: t1 19 s, t2 60 s, ten t3 runs of 3-37 s each, t4 9 s, t5 4 s, t6 < 10 s. That is about 5 min in total.
- **Deviation 1.** Two aborted first attempts used about 7 min more. Multithreaded BLAS made a 256 × 256 eigensolve take
  0.8 s instead of 0.05 s. I fixed it by setting `OMP/OPENBLAS/MKL_NUM_THREADS=1`.
- **Deviation 2.** Some single scripts ran 20-60 s, which is more than "seconds".
- No cloud, no QPU, no money spent.

**Not done:** venue and must-have list (R1), positive certification and the numeric check of the δe* law (R2). The exact
form of the accuracy law appears below only as a corollary (§A.5), with no numerics of its own.

Full scratchpad path: `C:\Users\Nicolas\AppData\Local\Temp\claude\c--Users-Nicolas-Downloads-Proyecto-SQD-ML\88ff9ed4-5021-4401-9432-f2e610eba8da\scratchpad\r3gen\`.

---

## Part A: a universal theorem

### A.0 Setting and definitions

**Lattice and Hamiltonian.**
- Λ is a finite graph with n sites and maximum degree z. Each site carries C^q.
- H = Σ_{X∈𝓘} h_X, where each h_X is Hermitian, supported on X, and diam X ≤ r (finite range).
- A conserved on-site charge Q = Σ_i Q_i (for example U(1) S^z) is optional. Π is the projector on the dataset's
  sector. Π = 1 means no sector.

**Local energy constants.** For a region A ⊆ Λ:
- spread(h) := λ_max(h) − λ_min(h);
- κ_A := Σ_{X ∩ A ≠ ∅} spread(h_X) ≤ 2|A|·J_loc, with J_loc := max_i Σ_{X∋i} ‖h_X‖.
- For two-body bonds plus fields: κ_{{i}} ≤ deg(i)·s_bond + s_field.
- Examples:
  - TFIM bond −J ZZ: s = 2J. Field −hX: s = 2h.
  - XXZ bond ¼(XX + YY + Jz ZZ) with Jz ≥ 1: s = (1 + Jz)/2, which is 1.3 at Jz = 1.6.

**Window and information limit.**
- W(E) := {σ ⪰ 0, Tr σ = 1, σ = ΠσΠ, Tr Hσ ≤ E}, and E₀ := min spec(ΠHΠ).
- For an observable O: I_O(E) = [o⁻(E), o⁺(E)] := {Tr Oσ : σ ∈ W(E)}, with width w_O(E) = o⁺ − o⁻.
- Write ε = E − E₀ and δe = ε/n (the intensive error).
- o₀^± is the max/min of ⟨O⟩ over the ground-state manifold (o₀ if it is unique). The one-sided extents are
  u_±(ε) := ±(o^±(E₀+ε) − o₀^±).
- R_O is the spread of ΠOΠ on the sector (the "full range").

**Energy-only certificate.** Any interval-valued map whose soundness at E holds for every state of W(E):
- every window SDP or bootstrap at any level (2310.05844, 2604.01555, 2609.22420, 2610.06272);
- Eckart, Weinhold and Manchanda radius bounds;
- IBM's Supp. Eq. 14 used as an observable bound.

Its width is ≥ w_O(E). Certificates that add ground-state optimality constraints (2311.18707) are not covered.

**Lemma P (pure witnesses suffice).**
- The joint numerical range {(⟨ψ|H|ψ⟩, ⟨ψ|O|ψ⟩) : ψ ∈ ΠC^{q^n}, ‖ψ‖ = 1} is the numerical range of Π(H + iO)Π. By
  Toeplitz–Hausdorff it is convex, so it equals the mixed-state set.
- Hence every width below is also attained by **pure** states, and the theorems apply verbatim to pure-state
  datasets (device or algorithm outputs).

### A.1 Lemma 0 (exact duality: Cohen–Feldmann 1971; folklore; Manchanda Eq. 20 uses it numerically)

**Statement.** For ε > 0:

  o⁺(E₀+ε) = min_{λ>0} [E₀ + ε − E₀(H − λO)]/λ,

equivalently

  u₊(ε) = inf_{λ>0} (α(λ) + ε)/λ,  with α(λ) := E₀ − λo₀⁺ − E₀(H − λO) ≥ 0.

Here α is convex, with α(0) = α'(0⁺) = 0, and all ground energies are taken in the sector. Further:
- **Inverse:** α(λ) = sup_{ε≥0} (λu₊(ε) − ε).
- **Optimizer:** a ground state of H − λ*O, or a two-state mixture across a level crossing. By Lemma P a pure state also
  works.
- **E₀-free certificate form:** for any L(λ) ≤ E₀(H − λO) and every σ ∈ W(E_dev),

  Tr Oσ ≤ (E_dev − L(λ))/λ.

**Proof.**
- Weak duality: Tr(H − λO)σ ≥ E₀(H − λO).
- Strong duality and dual attainment: Slater (the ground state has energy E₀ < E₀ + ε) for this finite-dimensional
  SDP with one linear constraint.
- u₊ is concave and nondecreasing (the value function of a convex program). The pair (α, u₊) is a conjugate pair
  (the "perspective" form of Legendre duality). ∎

**Check (T1).** 6 model/label pairs (1D/2D TFIM, 1D/2D XXZ in a sector; local and averaged labels) × 2 signs × 4 ε = 48
instances. The primal witness value equals the dual at λ* to ≤ 2.8·10⁻¹⁰. No λ on a 30-point grid gives a dual value
below the primal.

### A.2 Theorem 1 (local labels: universal localization with explicit N*)

Let O be supported on A, and let B ⊇ A be finite.

**(a) No sector constraint.**
- Let R_A^+ be the reset channel ρ ↦ |φ₊⟩⟨φ₊|_A ⊗ Tr_A ρ, with φ₊ a top eigenvector of O. Let ε_A^+ := Tr H R_A^+(ψ₀) − E₀.
- Then ε_A^+ ≤ κ_A and, for every ε ≥ 0,

  u₊(ε) ≥ min(1, ε/ε_A^+)·(o_max − o₀),

  and the same holds for the lower side.
- Hence w_O(E₀ + nδe) = R_O (the **full range**) for all

  **n ≥ N*_O(δe) := κ_A/δe** (universal), or the sharper max(ε_A^+, ε_A^−)/δe.
- The same holds with any unitary U on B (C1 Thm 1(b)): u ≥ min(1, ε/ε_U)·δ_U.

**(b) Fixed charge sector (on-site symmetry).**
- Use the covariant measure-and-prepare channel on B: measure the B-charge q, then prepare φ_q := top eigenvector of
  Π_q^B O Π_q^B.
- This channel keeps the state in the sector and leaves Tr_B unchanged. Hence

  u₊(ε) ≥ min(1, ε/κ_B)·(c_B⁺ − o₀),  with c_B⁺ := Σ_q p_q λ_max(Π_q^B O Π_q^B),

  where p_q is the ground-state distribution of the B-charge.
- For O = Z_i in a U(1) sector, c_B⁺ = 1 − 2·P₀(B fully down) (likewise c_B⁻). So the extent is a constant fraction of
  the range, up to the probability that the block is fully polarized.
- For heavy-hex XXZ with B = {i, j} (j a neighbour): κ_B = (deg i + deg j − 1)(1 + Jz)/2.

**(c) E₀-free and constructive (Prop. W form).**
- If φ is any explicit sector state with Tr Hφ ≤ E_dev − κ_B, then R_B^±(φ) lie in W(E_dev).
- So every energy-only certificate at the dataset energy has width ≥ c_B⁺(φ) − c_B⁻(φ), whatever E₀ and ⟨O⟩_GS are.
- It suffices that any classical method reaches δe_cl ≤ δe_dev − κ_B/n.

**(d) Block labels.**
- Ō_B = (1/b)Σ_{i∈B} o_i reaches the full range once nδe ≥ κ_B ≤ b·κ₁. Hence every label averaged over fewer than
  **b* = nδe/κ₁** sites is completely uncertifiable.
- For k well-separated sites (no term touches two of them), the reset costs add exactly.

**Proof.**
- The channel acts on A (respectively B) only, so the reduced state on the complement is unchanged. Terms not touching
  A keep their expectation.
- For each touching term, both expectations lie in [λ_min(h_X), λ_max(h_X)], so the change is ≤ spread(h_X).
- The mixture σ_t = (1−t)ψ₀ + tR(ψ₀), with t = min(1, ε/ε_A), lies in W(E₀ + ε) and has label o₀ + t(o_max − o₀).
- (b): the covariant channel commutes with the global charge. (c): replace ψ₀ by φ and use Prop. W. ∎

**Remarks.**
- **No non-commutation hypothesis is needed.** The theorem holds for any local O with R_O > 0 on the sector, including
  terms of H and local conserved quantities such as stabilizers. The only exceptions have ΠOΠ trivial, e.g. X_i in a
  U(1) sector, where ⟨X_i⟩ = 0 identically. This is sharper than the brief's "non-conserved" hypothesis.
- **What changes above the gap, at criticality, or in symmetry-broken phases:** nothing in the statement. κ_A is a
  local constant and does not see Δ.
- **IBM dataset constants:**

  | Jz | δe | universal N* for Z_i (deg-3 site, deg-2 neighbour) |
  |---|---|---|
  | 1.6 | 0.011 | 4 × 1.3/0.011 ≈ **470** |
  | 2.5 | 0.0044 | ≈ 1,600 |

  - The actual reset costs in T2 are 0.23-0.32·κ for XXZ.
  - The pilot's field witnesses already give 49-83 % of the range at n = 57 (ε = 0.50-0.55 J). Field witnesses are the
    optimizers of Lemma 0, so they beat resets.

**Check (T2).**
- **Resets (no sector):** 14 TFIM cases (1D n = 8, 12, 10; 2D 3×4 at h = 3.5, 2.0; labels Z, X).
- **Covariant resets:** 6 cases (XXZ 1D n = 8, 12 and 2D 3×4, B = 2 sites, Sz = 0).
- In all 20 cases:
  - the reset cost was ≤ κ (cost/κ = 0.08-0.32);
  - the exact window extent was ≥ the reset shift;
  - the mixing bound held on the ε grid (slack ≥ −10⁻¹⁵).
- The 6 block resets (below) also pass: cost ≤ κ_B and the full range is reached.
- At fixed δe = 0.1, the exact Z₀ width in the TFIM h = 1.5 chain is 1.842 / 1.943 / 1.991 / 2.000 for n = 6 / 8 / 10 / 12
  (range 2).
- Block resets: the per-site cost falls from 2.03 (b = 1) to 0.67 (b = 12).

### A.3 Theorem 2 (intensive averages: exact intensive formula, two-sided √ law far above the gap)

**Setting.**
- Ō = (1/n)Σ_i o_i, with o_i supported within distance r_o of site i and ‖o_i‖ ≤ 1.
- f_n(μ) := E₀(Π(H − μnŌ)Π)/n, α_n(μ) := f_n(0) − μō₀ − f_n(μ) ≥ 0 (convex), and u_n(δe) := o⁺(E₀ + nδe) − ō₀.

**(a) Exact, intensive form of Lemma 0.**
- u_n(δe) = inf_{μ>0} (α_n(μ) + δe)/μ. Only energy densities enter.
- The extremal witnesses are the ground states of H − μ*nŌ: a **uniform conjugate field**.

**(b) Sandwich, any ε.** For μ₁ > 0, let χ_±(μ₁) := sup / inf over 0 < μ ≤ μ₁ of 2α_n(μ)/μ². Then

  min{√(2χ₋δe), χ₋μ₁/2} ≤ u_n(δe) ≤ √(2χ₊δe)  for all δe ≤ χ₊μ₁²/2.

- **Exact iff:** u_n(δe) ≤ √(2χδe) for all δe > 0 ⟺ α_n(μ) ≤ χμ²/2 for all μ > 0.

**(c) Uniformity in n, with no ε ≤ Δ condition.**
- Assume: for |μ| ≤ μ₁, H − μnŌ has a unique sector ground state with gap ≥ Δ*, and
  max_i Σ_j |⟨o_i o_j⟩_{c,μ}| ≤ C₁.
- Then **χ₊(μ₁) ≤ 2C₁/Δ***, uniformly in n.
- C₁ is finite under exponential clustering, which Hastings–Koma (math-ph/0507008) derive from a uniform gap for
  finite-range H. The sector-restricted version is SIN VERIFICAR.
- Conversely, χ_n(μ) ≥ 2v²/s₁, with v = Var(nŌ)/n and s₁ = ⟨[nŌ,[H,nŌ]]⟩/(2n) (Cauchy–Schwarz on the spectral sum,
  f-sum rule). So every average with intensive ground-state fluctuations has χ > 0.

**(d) Universal linear bound, no assumptions.** u_n(δe) ≥ (⌊nδe/κ₁⌋/n)·(o_max − ō₀) ≥ (δe/κ₁ − 1/n)(o_max − ō₀),
using k well-separated single-site resets.

**(e) When averages are certifiable (exact classification at finite n).**
- If the sector ground state is **not** an eigenvector of Ō (χ_n(0) > 0): u_n(δe) = √(2χ_n(0)δe)·(1 + O(√δe)). No energy
  certificate is better than √δe.
- If it **is** an eigenvector: u_n(δe) ≤ δe/μ_c (linear). This is Manchanda's "population term"; μ_c is the field at
  which the ground state first changes.
- Within an enforced sector, conserved charges have width 0. Without the sector they obey the √ law with the uniform
  susceptibility (the charge compressibility).
- **Hellmann–Feynman conjugates** (Ō = ∂_g H/n) are not special in principle:
  - f_n(μ) = e₀(g ± μ), so χ = |e₀''(g)| (the curvature of the physical ground-energy curve);
  - this is often small: 0.18-0.21 for X̄ vs 4.9 for Z̄ in the TFIM at h = 1.5;
  - it diverges logarithmically at a critical point;
  - they are special only in practice: the dual data (neighbouring couplings) belong to the dataset's own family (R2's
    positive half).

**Proof.**
- (a) Rescale Lemma 0 (λ = μ).
- (b), upper bound: take μ = √(2δe/χ₊) ≤ μ₁.
- (b), lower bound:
  - for μ ≤ μ₁, (α + δe)/μ ≥ χ₋μ/2 + δe/μ ≥ √(2χ₋δe);
  - for μ > μ₁, convexity and α(0) = 0 make α(μ)/μ nondecreasing, so (α + δe)/μ ≥ α(μ₁)/μ₁ ≥ χ₋μ₁/2.
- (b), the iff: "⇐" is the upper bound. "⇒": α(μ) = sup_δe(μu − δe) ≤ sup(μ√(2χδe) − δe) = χμ²/2.
- (c):
  - α'' = −f_n'' = (2/n)Σ_k |⟨k|nŌ|0⟩|²/(E_k − E₀) ≤ (2/(nΔ*))Var(nŌ) ≤ 2C₁/Δ*;
  - with α(0) = α'(0) = 0 this gives α ≤ χ₊μ²/2;
  - the lower bound follows from (Σ|c_k|²)² ≤ (Σ|c_k|²/ω_k)(Σ|c_k|²ω_k).
- (d) Theorem 1(d) applied to the sites with the largest deficits.
- (e) Analytic perturbation theory. If Ōψ₀ = ō₀ψ₀, then ψ₀ stays the ground state of H − μnŌ for μ < μ_c, so
  α ≡ 0 there and u ≤ δe/μ_c. ∎

**What changes above the gap.** Nothing in (a)-(c):
- the gap enters only through the **deformed family's** susceptibility, never through ε/Δ;
- in contrast, Manchanda's Thm 2 needs ε ≤ Δ̄_O/2;
- his Eq. 10 tends to the trivial bound ‖Ō_ex‖ as n → ∞ at fixed δe, because its population term grows like
  ε = nδe.

**Check (T3).** 10 families, about 170 (n, δe) rows. The sandwich held in every row, and the sum-rule bound in every
row (about 30). Representative rows (w = exact two-sided width):

| family | n | δe | ε/Δ | exact w | 2√(2χ₀δe) | Manchanda Thm 2 applicable? | Eq. 10 upper (radius) vs exact radius |
|---|---|---|---|---|---|---|---|
| TFIM 1D h=1.5, Z̄ | 6 → 12 | 1e-2 | 0.06-0.12 | 0.592, 0.612, 0.620, 0.623 | 0.605-0.641 | yes | — |
| same | 6 → 12 | 0.3 | 1.7 → **3.6** | 1.8965, 1.8988, 1.8994, 1.8996 (**intensive**) | — | **no** | 1.21 → 1.40 (n = 6 → 8) vs 0.948 / 0.949 |
| comb ferrimagnet (IBM-like pinning, n_B − n_A = n/3) | 6, 9, 12 | 1e-2 | 0.04-0.07 | 0.260, 0.238, 0.233 | 0.261, 0.237, 0.232 | yes | — |
| same | 12 | 0.1 | 0.71 | 0.747 | 0.735 | **no** (ε > Δ̄/2 = 1.00) | 0.651 vs 0.561 |
| same | 6, 9, 12 | 0.3 | 1.05 → 2.14 | 1.2894, 1.2933, 1.2936 (**intensive**) | — | no | 1.39 vs 1.11 (n = 12) |
| Lieb 2×2 (2D ferrimagnet, n = 12) | 12 | 1e-2 | 0.05 | 0.177 | 0.175 | yes | — |
| TFIM 1D h=1.5, X̄ (HF conjugate) | 6 → 12 | 1e-2 | ≤ 0.12 | 0.133 → 0.124 | 0.133 → 0.123 | yes | — |
| XXZ 1D Jz=1.6, periodic, Sz = 0 (**unpinned** Néel) | 6 → 12 | 1e-3 | ≤ 0.06 | 0.342 → 0.642 (grows) | χ₀ = 14.8 → 54.4 | yes | Eq. 10 = 1.59 > 1 at δe = 0.1, n = 12 (vacuous) |
| 2-leg ladder XXZ, Sz = 0 (unpinned) | 6 → 12 | 1e-3 | ≤ 0.04 | 0.327 → 0.561 (grows) | χ₀ = 13.5 → 40.7 | yes | — |

Notes on the table:
- 2D TFIM 3×4 (h = 3.5) and the 3×4 XXZ torus also satisfy the sandwich. The torus is frustrated because of its 3-cycle
  direction; it is used only as a check of the inequality.
- T6: along the field family μ ∈ [0, 0.3], the chain 2v²/s₁ ≤ χ_n(μ) ≤ 2Var/(nΔ_μ) holds for TFIM, comb and
  open-chain XXZ.

### A.4 Theorem 3 (general characterization: the cost of moving a label)

**Statement.** Define the minimal energy cost of shifting O by c within the sector:

  E*_n(c) := min{Tr Hσ − E₀ : σ ∈ sector, Tr Oσ ≥ o₀ + c}.

Then **u_n(ε) ≥ c ⟺ ε ≥ E*_n(c)**, and E*_n is the convex conjugate of α:

  E*_n(c) = sup_λ (λc − α(λ)).

So energy-only certification of O to precision c at density δe is possible for all n **iff
liminf_n E*_n(c)/n > δe**. Proof: compactness plus Lemma 0. ∎

**Classification of e*(c) := lim E*_n(c)/n.**

| label class | E*_n(c) | e*(c) | consequence |
|---|---|---|---|
| local O on A (Thm 1) | ≤ κ_A·c/(o_max − o₀) = O(1) | 0 | full range for n ≥ κ_A/δe |
| average over b = o(n) sites | ≤ bκ₁·c/(o_max − o₀) | 0 | uncertifiable for b < nδe/κ₁ |
| order parameter, **unpinned** symmetry-broken phase | ≤ tower / tunnelling splitting → 0 | 0 | lim_{δe→0⁺} u(δe) = m_spont: uncertifiable at every δe > 0 |
| order parameter, orientation fixed only by boundary or a balanced sector (**cheap interfaces**) | ≤ σ n^{(d−1)/d}·c/δ_def | 0 (as n^{−1/d}) | uncertifiable for n ≳ (σc/(δ_def δe))^d |
| average, **extensively pinned** or gapped deformed family (Thm 2(c)) | ≥ n c²/(2χ₊) | ≥ c²/(2χ₊) > 0 | √ law, intensive, valid at ε/Δ ≫ 1 |
| order parameter at a critical point (magnetic direction) | ~ n c^{1+δ} | ~ c^{1+δ} | u ∝ δe^{1/(1+δ)} |

**Scaling lemma** (checked to 10⁻¹⁵ in T4d). If α(μ) ≃ Aμ^p, then

  u(δe) = p/(p−1)·(A(p−1))^{1/p}·δe^{1−1/p}.

The cases:
- p = 2 gives the √ law.
- p = 1 + 1/δ gives the critical exponent 1/(1+δ). The certification width scales as:

  | universality | δ | width |
  |---|---|---|
  | 1D TFIM (2D Ising class) | 15 | δe^{1/16} |
  | 2D TFIM (3D Ising class) | ≈ 4.79 | δe^{≈0.17} |
  | mean field | 3 | δe^{1/4} |

- An energy-like direction with α ≃ Aμ² log(1/μ) gives u ≃ √(δe·log(1/δe)).

**Thermodynamic limit.** If f_n → f locally uniformly near 0 and ō_{0,n} → −f'(0), then u_n → u at every δe > 0. This
holds for translation-invariant or periodic finite-range H by subadditivity; heavy-hex is periodic. The pilot's
D(115)/D(57) = 0.965 is this statement in practice.

**Checks.**
- **(T4a) Unpinned symmetry-broken phase** (TFIM h = 0.5, Z̄, no parity sector): u_n(10⁻⁴) = 0.544, 0.966, 0.968, 0.968
  for n = 6-12, against m_spont = (1 − h²)^{1/8} = 0.965. At δe = 10⁻² it is 0.988 for every n.
- **(T4b) Critical HF conjugate, exact thermodynamic limit** (free fermions, X̄ of the TFIM):

  | h | (u₋)²/δe for δe = 10⁻² … 10⁻⁶ | reading |
  |---|---|---|
  | 1.5 | 0.47 → 0.367 (constant) | 2χ, χ ≈ 0.18 |
  | 1.0 | 2.39, 3.14, 3.92, 4.71, 5.49 | linear in ln(1/δe), slope 0.34 (prediction ≈ 1/π = 0.32) |

  ED at n = 12 gives 0.044 against the thermodynamic-limit 0.056 at δe = 10⁻³ (finite-size cutoff of the log).
- **(T4c) Critical order parameter** (TFIM h = 1, Z̄):
  - u_n·n^{1/8} collapses on a function of δe·n² to ≤ 1.1 % for n = 6-12;
  - the local log-slope falls from 0.26 (x = δe n² ∈ [0.3, 1]) to 0.09 (x ∈ [1, 3]), on its way to the predicted
    1/16 = 0.0625.
- **(T5) Pinning matters: u₋ at fixed total ε.**

  | system | ε | u₋ |
  |---|---|---|
  | open odd XXZ chain, Jz = 4 (orientation fixed by one extra spin; cheap domain wall) | 1.0 | 0.913 → 1.033 for n = 5 → 11 (**local-like**, grows with n) |
  | comb ferrimagnet (extensive pinning) | 1.0 | 0.800 → 0.498 for n = 6 → 12 (**regular**, falls ≈ n^{−1/2}) |

  The IBM heavy-hex sector (n_A − n_B = 9 and 19, ≈ 0.16n) is extensively pinned. This is consistent with the pilot's
  intensive D. It is **not proved** for heavy-hex.

### A.5 Corollaries

**Corollary A (exact accuracy law).**
- The largest device error at which the information limit still allows ±c is

  δe*_n(c) = E*_n(c)/n = α_n*(c)/n.

- To leading order this is c²/(2χ), which is Manchanda Eq. 22 recast per site. It is exact at all ε, impossible
  (O(1/n)) for local labels, and ∝ c^{1+δ} at criticality.
- The numerical check of this law at scale belongs to R2.

**Corollary L (learning: label-shift indistinguishability).**
- **Setting.** For a family H(x), let μ(x) be chosen so that ⟨H(x)⟩ − E₀(x) = nδe(x).
- **Construction.** The extremal witnesses ψ_μ(x) = GS of H(x) − μ(x)nŌ form the ground-state family of a local
  Hamiltonian family of the same locality (plus one on-site field).
- **Learnability.** If that family stays gapped (Thm 2(c)), the shifted label map x ↦ ⟨Ō⟩_{ψ_μ(x)} lies in the same
  class that the Huang–Kueng–Torlai–Albert–Preskill / Lewis / Wanner guarantees cover (2106.12627, 2301.13169,
  2405.18489).
- **Conclusion.** No learner, and no comparison "model vs new data of the same validation quality" (IBM's OOD test),
  can tell a dataset shifted by up to u_n(δe(x)) from the true one.
- **Physical meaning.** The worst case is not exotic: it is exactly the output of a device whose coherent bias acts as a
  small conjugate field. Examples are a Néel-seeded sampler or a miscalibrated ZZ angle.
- **Status.** The proof is by construction plus Lemma 0. It is a remark-level corollary, but it is the sentence an ML
  audience needs.

### A.6 Comparison with prior art (precise)

| work | what it proves | relation to Theorems 1-3 |
|---|---|---|
| Eckart 1930 (Phys. Rev. 36, 878) | infidelity ≤ ε/Δ, so local width ≤ 4‖O‖√(ε/Δ) | an upper bound, vacuous for ε ≥ Δ. Ours are lower bounds plus the extensive regime |
| Weinhold 1968 (J. Phys. A 1, 305) | lower bounds to expectation values from overlap information | needs overlap or variance data, not energy-only. Not comparable at extensive ε |
| Cohen–Feldmann 1971 (J. Phys. A 4, 761) | Lagrange-multiplier bounds: Lemma 0 | **Lemma 0 is theirs.** Not claimed |
| Manchanda 2610.03989, Thm 1 (Eq. 7) / Eq. 10 / Cor. 1 | upper radius ≤ population ε‖H_ex^{-½}O_exH_ex^{-½}‖ + coherence √(2εχ(ε)), capped | for Ō at fixed δe, the population term grows like nδe/Δ until it hits the trivial cap. Thm 2(b,c) replaces it by √(2χ₊δe), uniform in n |
| Manchanda Thm 2 (Eq. 15) and Cor. 2 | √(2εχ_O)·√(1 − ε/Δ̄_O) ≤ radius, valid **only for ε ≤ Δ̄_O/2**; exact ψ₀ needed | **corollary of ours at small ε** (χ_Ō = χ_site/n makes √(2εχ_Ō) = √(2δeχ_site)). Ours holds for all ε up to O(n), with field witnesses computable by DMRG |
| Manchanda Eq. 22 | ε ≲ δ*²/(2χ_O) at leading order | Corollary A gives the exact form α*(c) at any ε, plus the local and critical cases |
| Manchanda Discussion, footnote 3 | certification fails if lim ε/Δ = ∞; the "unlikely" exception is vanishing transition elements | **corrected for averages.** For Ō the transition elements scale as 1/√n generically, so the exception is the rule: the width stays √(2χδe) at ε/Δ → ∞. His conclusion holds for local labels (Thm 1) and for unpinned or cheap-defect order (Thm 3) |
| Manchanda Eqs. 17-19 (symmetry) | conserved O loses the coherence term; in-sector gap | consistent with Thm 2(e). Ours adds that without sector enforcement conserved averages obey the √ law with the compressibility |
| Wang et al. 2310.05844, 2604.01555; 2610.06272 | window SDP bounds on any observable | energy-only certificates, so bounded below by w_O at every level. With translation invariance imposed, their "local" label equals our average |
| Scheer–Chadha–Lu–Khalaf 2511.20860 | thermodynamic-limit bootstrap bounds "inevitably loose in symmetry broken phases"; cause: order-parameter defects | the same mechanism. Theorem 3's cheap-defect row is the finite-n, energy-window, explicit-N* version. Their "defect diamagnetism" fix plays the role of our extensive pinning |
| Banerjee–Guo–Chowdhury 2609.22420 | window bounds encompass the quasi-degenerate low-energy manifold | the unpinned symmetry-broken row of Thm 3 |
| 2311.18707 (Araújo et al.) | ground-state optimality conditions | the exit from Thm 1 (our witnesses are not eigenstates). Not an energy-only certificate |

**Honest verdict on novelty.**
- **Folklore or known:**
  - Lemma 0 (Cohen–Feldmann);
  - the mixing argument of Thm 1 (J2 already called it a one-liner; bootstrap and Hamiltonian-complexity folklore says
    "energy density does not constrain local observables");
  - the small-ε √(2εχ) sandwich at fixed n (Manchanda);
  - "symmetry-broken order is loose" (2511.20860, 2609.22420);
  - the analytic content of the √ law (linear response).
- **Not found anywhere in the literature searched,** and therefore the paper's precise contribution:
  1. the **uniform-in-n, non-perturbative** two-sided √(2χδe) law for averages at ε/Δ ≫ 1, with the deformed-family
     susceptibility constant (Thm 2(b,c));
  2. the **exact iff** and the exact accuracy law as a convex conjugate (Thm 2(b), Cor. A);
  3. explicit **N* = κ/δe** for local labels including **charge sectors** and block labels (Thm 1(b,d));
  4. the **cost-of-change trichotomy with the pinning condition** (Thm 3), which explains why IBM's m_s is intensive
     while local labels are free;
  5. the **critical-exponent law** δe^{1/(1+δ)} and the log law for certification widths;
  6. the learning corollary.
- **Risk.** A referee may call 1-5 "elementary convex analysis plus standard thermodynamics". The defence is that they
  are exact, uniform statements that overturn a published asymptotic conclusion (Manchanda's footnote) for the labels
  that matter, and that they are tested on every published device dataset.
- **Scoop watch.** Manchanda is closest and already has Eq. 20. The extensive regime is one paragraph away for him.

---

## Part B: generality across published quantum-generated datasets

### B.1 Inventory (2023-2026, plus three earlier precursors)

All arXiv IDs below were returned by the API today (title and date match).

| # | paper | generator / platform | model, size | labels used for ML | ML | reported quality | data public? | witness audit applies? cost |
|---|---|---|---|---|---|---|---|---|
| 1 | Jaderberg et al. **2606.15983** v1 (IBM / Oxford / Hartree) | SKQD + basis optimization (OBP), ibm_boston, 8.3 h QPU | 2D heavy-hex XXZ, n = 57 / 115, Jz 1.6-6.0 (+1.1-1.4 OOD) | Z_i, C_zz (nn + nnn), Z_loop; derived m_s | local-MLP stack (2405.18489 type) | energy ratio (E−E₀)/(E₁−E₀) in figures (δe ≈ 0.011 at Jz = 1.6); labels vs DMRG ~1-2 % | on request | **done** (pilot COMMIT, 1.2 €) |
| 2 | Cho & Kim **2310.19416** (Nat. Commun. 15, 7552, 2024) | ibm_sherbrooke 127q. Case 1: exact free-fermion ground-state circuits (Givens), mitigated by DD, twirling, **McWeeny purification**, parity check | **Case 1:** 1D random-hopping chain n = 12, x ∈ [0,2]^11, 200 points × 20,000 shots. **Case 2:** fixed-point ZXZ vs X states + symmetric random local unitaries, n = 44; surface code d = 5 (25 q) | Case 1: full correlation matrix ⟨a_i†a_j⟩. Case 2: phase class | kernel ridge regression; PCA + SVM on shadow kernel | Case 1: model RMSE 0.0168 vs ED on 10,000 test points; raw-data RMSE 0.0244. **No energy reported** | on request | **Case 1 yes**, exactly solvable at any n (below). Case 2 no (phase classes of fixed-point states, not energy-validated) |
| 3 | Candelori et al. **2601.03235** (IBM, 2026) | SKQD on ibm_fez, ≤ 50 q, Krylov dim 8, 200 shots | data Hamiltonians H(x) = B − Σ_f a^f X_f (1-, 2-local) | logits ⟨ψ₀\|O_k\|ψ₀⟩ for a synthetic classical dataset (500 points, 10 features) | linear Hamiltonian model | accuracy 50 → 91 %; **no energy errors** | no statement | conceptually yes (logits are energy-uncertified ground-state observables), but the labels are classical. Low priority |
| 4 | Lee & Park **2512.19420** (GenKSR) | SKQD samples, 20-qubit XXZ chain on IBM hardware (+ 15q 1D / 16q 2D Heisenberg simulations) | 1D XXZ n = 20 | measurement outcomes → energies | Transformer / Mamba generative model | energies vs exact | SIN VERIFICAR | yes, for which observables those energies certify. ≈ 0.2-0.5 € (n = 20 sector ED) |
| 5 | Moss et al. **2308.02647** (2023) | Rydberg snapshots, 16×16 (Ebadi et al., Nature 595, 227) → RNN pretraining → **VMC (energy-minimized)** | 2D Rydberg, 256 atoms | checkerboard order / phases of the VMC state | RNN wavefunction | VMC energy | SIN VERIFICAR | yes (energy-validated states), but **≫ 3 €** (2D long-range DMRG at 256 sites, est. 20-60 €) |
| 6 | Lange et al. **2406.00091** (Quantum 9, 1675, 2025) | experimental Rydberg dipolar-XY data (Chen et al., Nature 616, 2023) + numerical TFIM data → NQS pretraining → energy minimization | 2D, 6×6 and 10×10 | correlations, magnetization | patched transformer NQS | energy vs reference | SIN VERIFICAR | yes, but the 10×10 dipolar case ≈ 5-20 € (over budget); the 6×6 TFIM numerical part ≈ 1-2 € |
| 7 | Bennewitz et al. **2105.08086** (Nat. Mach. Intell. 4, 618, 2022), precursor | VQE outputs (numerical + experimental) → NQS → VMC | H₂, LiH, lattice Schwinger model (small) | order parameters, entanglement entropy | NQS | energy errors and fidelities | SIN VERIFICAR | yes, by ED (≈ 0 €). Exactly the "lower energy → better order parameter" claim |
| 8 | QCNN phase recognition on hardware: Herrmann et al. **2109.05909** (7q, cluster-Ising, 2021); Scarato et al. **2606.28201** (surface code ≤ 4×4 in field, 2026); Aktar et al. **2511.16851** (toric-code loop gas, VQE ground states, simulated) | hardware or VQE | ≤ 16 q | phase class | QCNN / hybrid | accuracy | — | no: nonlinear phase labels, outside Thms 1-3 |
| 9 | Miles et al. **2112.10789** (PRR 5, 013026, 2023) | 256-atom Rydberg snapshots (adiabatic) | 2D Rydberg | phase discovery (unsupervised + CCNN) | Hybrid-CCNN | none (no energy criterion) | SIN VERIFICAR | N/A (no energy validation) |
| 10 | Classical-data "stand-ins": Huang et al. **2106.12627** (Science 377, 2022) public DMRG dataset (2D random AF Heisenberg, L×5, L = 4…9, n = 20-45); ShadowGPT **2411.03285**; Wang et al. **2211.16943** | DMRG / simulated shadows | 2D Heisenberg, n = 20-45; Rydberg 13×13 (sim.) | two-point correlations, phases | kernel / generative | — | **yes** (GitHub `hsinyuan-huang/provable-ml-quantum`, also re-hosted on Hugging Face; licence SIN VERIFICAR) | yes: the paradigm's canonical benchmark. ≈ 0.5-1.5 € |
| 11 | energy-validated quantum ground-state data, not ML: Yoshioka et al. **2407.14431** (Nat. Commun. 16, 5014, KQD, 2D heavy-hex Heisenberg ≤ 56 sites); Yu et al. **2501.09702** (SKQD, Anderson impurity) | KQD / SKQD on Heron | — | energies | — | energies | SIN VERIFICAR | possible, but outside the ML scope |

**Google, Quantinuum, Pasqal.** In 10 API queries and 3 web searches I found **no** paper that trains an ML model on
device-generated ground-state observable labels from these platforms. Absence of hits is evidence about abstracts and
search engines only. QuEra/Harvard data enter only as snapshots (rows 5 and 9).

2606.15983's own introduction says earlier experiments were limited to "systems that admit exact classical solutions
and have canonical (fixed-point) states". That matches Cho–Kim (its ref. [21] is very probably 2310.19416; SIN
VERIFICAR). **So the published population of device-generated ground-state *observable* datasets used for supervised
learning is two: IBM 2606.15983 and Cho–Kim 2310.19416.** The generality of the paper must therefore rest on the theorem
plus every available dataset, not on a large dataset census.

### B.2 Ranked second and third targets

**#2 Cho & Kim 2310.19416, Case 1 (recommended second target). Cost ≈ 0 € (a laptop free-fermion computation; or
< 0.05 € in the cloud if the n ≤ 12 laptop rule is read strictly).**
- **Why:**
  - the only other published device dataset of ground-state observables used for ML;
  - a different device run, model class (1D disordered free fermions) and label type (the full correlation matrix:
    all local labels);
  - McWeeny purification makes each data point a valid Slater determinant, so its energy is an exact Rayleigh quotient
    and Prop. W applies cleanly.
- **Exactly solvable at any n:**
  - H_hop and every label O = a_i†a_j + h.c. are number-conserving quadratic operators, so E₀(H − λO) is a
    free-fermion ground energy;
  - Lemma 0 then gives the **exact information limit over all states** (not only Gaussian ones) at n = 12 and at
    n = 10²-10⁴ in seconds. This demonstrates N* = κ/δe for local labels at device-relevant sizes.
- **What we would compute:**
  1. for their family (x ∈ [0, 2]^11; open chain and filling as in their Supp. Note 3, SIN VERIFICAR), the exact widths
     of every C_ij and of averaged correlators at δe ∈ [10⁻⁴, 10⁻¹], with δe* per label;
  2. the energy error per site of each of their 200 mitigated data points (E = Σ t_ij C_ij is linear in C). This needs
     **their data (on request; the author must ask, not an agent)**. Without it, bracket δe from the reported RMSE;
  3. the same family at n = 100-1000 to show the local-label width reaching the full range at n ≈ κ/δe.
- **Caveat:** free fermions are classically easy. This target shows generality of the label map across devices and
  models, not a beyond-classical audit. Case 2 (phase classes) is out of scope.

**#3 Huang–Kueng–Torlai–Albert–Preskill benchmark (2106.12627; public DMRG dataset, 2D random AF Heisenberg L×5).
Cost ≈ 0.5-1.5 € (n2-highmem-8, ~1-2 VM-h).**
- **Why:**
  - it is the canonical dataset of the "learning from quantum data" paradigm (used by 2301.13169, 2405.18489 and the
    ML-from-device papers);
  - it is public;
  - its labels (two-point correlations of individual random-coupling instances) are exactly the spatially resolved
    labels of Thm 1.
  - The result becomes: "the paradigm's own benchmark labels cannot be certified from device energies at δe ~ 10⁻²",
    independently of IBM.
- **What we would compute:**
  1. **5 instances at L = 4** (n = 20; exact ED in the S^z = 0 sector, dim 184,756; about 6,000 Lanczos solves): local C_ij
     (nn, long-range) and the averaged correlator, exact widths at δe ∈ {10⁻³, 3·10⁻³, 10⁻²}, δe* and N*;
  2. **2 instances at L = 9** (n = 45; DMRG χ = 256, ≈ 130 runs): the same at δe = 10⁻², as witnesses, to show the trend
     with n.
- **Estimate:** ≈ 0.3 VM-h (ED) + 0.6 VM-h (DMRG) ≈ 0.6 € list price, ≈ 0.75 € with the program's × 1.25, < 1.5 € with
  contingency.

**#3' (alternative, if the author wants a third *device* dataset): GenKSR 2512.19420, IBM hardware, 20-qubit XXZ chain.
Cost ≈ 0.2-0.5 €.**
- Compute D(m_s), local Z_i widths and δe* at the energy errors they report.
- Risk: energies may exist only in figures, and data availability is unknown.
- The NQS-from-Rydberg-data papers (Lange et al. 2406.00091, Moss et al. 2308.02647) are the more interesting device
  cases, but their 2D long-range models cost ≈ 5-60 € and break the ≤ 3 € rule.

**Suggested shape of the general paper** (for R1 to weigh; not a venue analysis):
- the theorem (Thms 1-3 + Cor. A, L);
- the exact free-fermion demonstration at n up to 10³ (Cho–Kim family);
- the two device datasets (IBM 2606.15983 at 57/115 qubits; Cho–Kim);
- the canonical benchmark (Huang et al.);
- one figure with the cost-of-change trichotomy across all of them, including IBM's extensively pinned m_s vs its free
  local labels.
- Total new compute ≈ 1-2 €.

---

## C. Numerical-check index (all laptop ED, n ≤ 12; scripts in `scratchpad/r3gen/scripts`, outputs in `.../out`)

| test | script / output | what it checks | result |
|---|---|---|---|
| T1 | `t1_duality.py` / `t1_duality.txt` | Lemma 0 exactness and weak duality, 48 instances | max \|primal − dual\| 2.8e-10; no violation |
| T2 | `t2_local.py` / `t2_local.txt` | Thm 1(a,b,d): reset costs ≤ κ; exact u(ε_R) ≥ shift; mixing bound; fixed-δe growth; U(1) covariant reset; blocks | 20 + 6 block cases pass; full range at n = 12 for δe = 0.1 |
| T3 | `t3_avg.py <family>` / `t3_*.txt` (10 families) | Thm 2(a-c,e): sandwich, intensivity above the gap, sum rule, Manchanda comparison | ≈ 170 rows pass; Manchanda Thm 2 inapplicable at ε > Δ̄/2 while the exact width stays intensive |
| T4 | `t4_regimes.py` / `t4_regimes.txt` | unpinned symmetry-broken plateau; critical HF log law (exact thermodynamic limit); critical order-parameter finite-size scaling; scaling lemma | plateau 0.968 vs m_spont 0.965; slope 0.34 vs 1/π; collapse ≤ 1.1 %; lemma to 1e-15 |
| T5 | `t5_defects.py` / `t5_defects.txt` | pinning trichotomy (cheap wall vs extensive pinning); exact additivity of separated resets | as in §A.4; additivity to 1e-9 |
| T6 | `t6_chibound.py` / `t6_chibound.txt` | 2v²/s₁ ≤ χ(μ) ≤ 2Var/(nΔ_μ) along the field family | holds at all 21 points |

`edcore.py` holds the ED core: sparse spin Hamiltonians, U(1) sectors, the exact window by Brent bisection on λ plus
mixtures, and graphs (chain, rectangle, cylinder, comb, Lieb). Two pitfalls were fixed during testing:
- Lanczos warm starts trapped in a symmetry sector (now perturbed with a fixed random vector);
- saturation at a finite λ (λ is now raised until the label saturates).

## D. SIN VERIFICAR

- Hastings–Koma clustering for **sector-restricted** gaps (Thm 2(c) is stated with the clustering constant C₁ as the
  hypothesis).
- That heavy-hex at IBM's sector is "extensively pinned" in the sense of Thm 3: the pilot intensivity and the comb/Lieb
  analogues support it; it is not proved.
- The bibliographic details of Eckart, Weinhold and Cohen–Feldmann are copied from 2610.03989's reference list and not
  checked independently.
- Cho–Kim: chain boundary conditions and filling; whether 2606.15983's ref. [21] is 2310.19416.
- Data availability of 2512.19420, 2308.02647, 2406.00091, 2105.08086; the licence of the Huang et al. dataset.
- The critical exponent law is checked only through the finite-size collapse and the exact HF log case. The asymptotic
  δe^{1/16} regime is beyond n ≤ 12.

## E. Sources (web)

- [arXiv 2310.19416 PDF](https://arxiv.org/pdf/2310.19416)
- [DOAJ record, Nat. Commun. 2024](https://doaj.org/article/7b405785ddc246a596d91f4c34556e04)
- [arXiv 2606.15983 PDF](https://arxiv.org/pdf/2606.15983)
- [arXiv 2211.16943](https://arxiv.org/pdf/2211.16943)
- [Hugging Face re-host of the Huang et al. 2D Heisenberg data](https://huggingface.co/datasets/hdkqzpmta/quantum-ood-benchmark)
- [arXiv 2412.20956 HTML (cites the public dataset)](https://arxiv.org/html/2412.20956v1)
- [arXiv 2601.03235 HTML](https://arxiv.org/html/2601.03235v1)
