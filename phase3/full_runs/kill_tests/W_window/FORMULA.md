# Kill test W, step 0: the envelope formula (written before reading any iPEPS number)

Written 2026-11-07T15:32Z (UTC). At this time no table or figure of arXiv 2009.02313 has been opened in this session. The only iPEPS-related numbers known are those quoted in the brief (D = 7: m^2 - m0^2 ≈ 0.005; scout's envelope 0.0067-0.0084; r ≈ 0.6-0.8). The formula below was derived independently of them and is not tuned to them.

## 1. Model, units, window

- H = J Σ_<ij> S_i·S_j, spin 1/2, square lattice, nearest neighbours, J = 1, lattice spacing a = 1. Energies are per site.
- e0: ground energy per site in the thermodynamic limit. δe = e - e0 ≥ 0 (energy error per site of a state).
- Window W(δe) = all states (density matrices) of the infinite lattice with energy per site ≤ e0 + δe.
- Observable: staggered magnetization per site along z, m_s = (1/n) Σ_i ε_i S_i^z (ε_i = ±1 on the two sublattices); m0 = its value in the symmetry-broken ground state (spontaneous moment).
- Upper extent u(δe) = sup over W(δe) of m_s, minus m0. By spin-rotation symmetry the same u bounds the length |⟨S_i⟩| of the staggered moment of any translation-invariant (two-sublattice) state in the window, so the largest m^2 = |⟨S_i⟩|^2 in the window is (m0 + u)^2.
- Lower side: in two dimensions at T > 0 there is no order (Mermin-Wagner), while the thermal energy per site vanishes as T^3; also mixing or rotating domains costs zero energy per site in the infinite system. So the lower extent of m^2 is the whole range down to 0 for every δe > 0. Only the upper side carries information, and finite-D iPEPS sits on that side (it overestimates m).

## 2. The formula

Duality (paper supplement, Lemma A, extensive form): with α(h) = e0 - h m0 - e0(h) ≥ 0, where e0(h) is the ground energy per site of H - h Σ_i ε_i S_i^z,

    u(δe) = inf_{h>0} [α(h) + δe] / h.

Leading behaviour of α with Goldstone modes (O(3) nonlinear sigma model at one loop, two transverse magnons with gap^2 = c^2 m0 h / ρs):

    α(h) = A h^{3/2} + O(h^2),   A = (c / (6π)) (m0 / ρs)^{3/2}.

Source of A: C. P. Hofmann, arXiv 2008.12423, Eq. (2.7) at H = 0: z0 = -Ms Hs - (Ms Hs)^{3/2} / (6π ρs^{3/2}) - (k2 + k3) Ms^2 Hs^2 / ρs^2, with the spin-wave velocity set to 1 (footnote 1); restoring c multiplies the second term by c. Re-derived here independently: (1/2) Σ_k ω_k for two modes ω_k = sqrt(c^2 k^2 + Δ^2) has the non-analytic part -Δ^3 / (6π c^2) per unit area. The same paper, Eq. (2.29), gives Ms(Hs) = Ms [1 + m/2 + ...], m = sqrt(Ms Hs) / (2π ρs^{3/2}), i.e. dα/dh = (3/2) A h^{1/2}: consistent.

Then the "scaling lemma" of the supplement (line 192, p = 3/2) gives

    u(δe) = 3 (A/2)^{2/3} δe^{1/3} = 3 (c / (12π))^{2/3} (m0 / ρs) δe^{1/3},
    envelope for m^2:  Δm2_env(δe) = (m0 + u)^2 - m0^2 = 2 m0 u + u^2.

The optimal field is h* = (2 δe / A)^{2/3}; the extremal state is the ground state of H - h* M_s, a gapped state with magnon gap c sqrt(m0 h* / ρs).

No free parameter: everything is fixed by (c, ρs, m0) and e0 (which enters only through δe).

## 3. Constants and sources

| Constant | Value used | Source | Older value (cross-check) |
|---|---|---|---|
| e0 | -0.669441857(7) | A. W. Sandvik, arXiv 2601.20189 (abstract and Sec. III.2) | -0.669437(5), Sandvik PRB 56, 11678 (1997), cond-mat/9707123 |
| m0 | 0.307444(3) | arXiv 2601.20189, Sec. III.3 ("final result"); abstract quotes 0.307447(2) | 0.30743(1), Sandvik and Evertz PRB 82, 024407 (2010), arXiv 0807.0682; Jiang and Wiese PRB 83, 155120 (2011), arXiv 1011.6205 |
| ρs | 0.180752(6) J | arXiv 2601.20189, Sec. III.1 | 0.18081(11) J, Jiang and Wiese 1011.6205 |
| c | 1.65880(6) J a | arXiv 2601.20189, Sec. III.1 | 1.6586(3) J a, Jiang and Wiese 1011.6205 |
| χ⊥ | 0.065690(5) | arXiv 2601.20189, Sec. III.1 (= ρs / c^2; not needed by the formula, listed for completeness) | |

Values read from the arXiv abstract pages and the HTML version of 2601.20189 through a web reader on 2026-11-07, not from the PDFs; the digits should be rechecked against the published versions before any external use.

Numerically (2026 constants): A = 0.19522, u(δe) = 0.63598 δe^{1/3}, 2 m0 u = 0.39106 δe^{1/3}. With the 2010-2011 constants: 0.63570 δe^{1/3}; the difference (0.04 %) is negligible.

| δe | 1e-5 | 3e-5 | 1e-4 | 3e-4 | 1e-3 | 3e-3 |
|---|---|---|---|---|---|---|
| u | 0.0137 | 0.0198 | 0.0295 | 0.0426 | 0.0636 | 0.0917 |
| Δm2_env | 0.0086 | 0.0125 | 0.0190 | 0.0280 | 0.0432 | 0.0648 |
| h* | 0.0022 | 0.0046 | 0.0102 | 0.0211 | 0.0472 | 0.0981 |
| magnon length 1/M at h* | 16.4 | 11.4 | 7.6 | 5.3 | 3.5 | 2.5 |

## 4. Validity and error budget (stated now)

- **Leading order only.** The next term in α is analytic, (k2 + k3) m0^2 h^2 / ρs^2, with unknown low-energy constants k2, k3 (sign not known to me). Its relative effect on u grows like h*^{1/2} ∝ δe^{1/3}; at δe ≈ 1e-3 the magnon length at h* is only 3.5 lattice spacings, so the formula is less reliable for the smallest D than for the largest. I take this into account only by the 1.2 threshold of the brief, not by an extra margin.
- **Cross-check of magnitude (not the envelope).** Eliminating L between the torus finite-size laws of 2601.20189, Eq. (17), e(L) = e0 - 1.437745 c / L^3 and m^2(L) = m0^2 [1 + 0.6207465 c / (ρs L)], gives m^2 - m0^2 = 0.4030 |δe|^{1/3}, within 3 % of 2 m0 u. The torus states lie below e0 and are not in the infinite-lattice window, so this only confirms the scale; it does not replace Section 2.
- **e0.** The two QMC values differ by 4.9e-6. If an iPEPS energy lies within about 1e-5 of e0, δe is uncertain by tens of percent and r by about a third of that (r ∝ δe^{-1/3}); this is reported per D.
- **What r means.** For an iPEPS state at bond dimension D with energy e_D and moment m_D: δe_D = e_D - e0 and r_D = (m_D^2 - m0^2) / Δm2_env(δe_D). A state cannot leave the window, so the true sup is ≥ m_D: r_D > 1 beyond errors means the formula underestimates the window, i.e. it is wrong. Rule from the brief: **DEAD if r > 1.2 for any D in 3..6**.
- **Reading rule fixed now.** Use, for each D, the energy and moment the paper gives as its result for the unfrustrated model (J2 = 0) for that D; if a table exists, read the table; if both a raw and a χ-extrapolated (environment) value are given, use the extrapolated one and report the other; if only a figure exists, read it by eye, give the reading interval, and evaluate r at both ends of the interval. If the paper gives m (not m^2), square it. If it gives the moment with the convention m^2 = (3/4)... or any other normalization, convert to |⟨S_i⟩| and say so.
