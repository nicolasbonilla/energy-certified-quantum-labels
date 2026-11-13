# Real data of arXiv:2606.15983: DECLARATION

**Status: reviewed and decided by the coordinator on 2026-11-12 (decisions in Sec. 10); to be hashed as soon as the
analysis code has passed gate G8 and Sec. 11 lists it.** Drafted on 2026-11-12 by the review task `real-data-setup`
(R10). **None of the analyses declared in Secs. 2-7 has been run.** The SHA-256 of this file goes into
`DECLARATION.sha256` and the UTC time into `DECLARATION_hash_time.txt` before any script of Secs. 2-7 touches
`converted/`. After the hash it does not change; anything learned later goes, dated, into `DEVIATIONS.md`. Every outcome
is reported against the rule stated here, failures included. Honest failure is an acceptable outcome; a result bent to
pass is not. The author approved adopting the public data as the basis of the paper on 2026-11-12.

**Label: DECLARED AFTER PARTIAL SIGHT. NOT BLIND.** The public files were opened on 2026-11-12 (first look by the
review agent `level-sota`, then the conversion and descriptive checks of this task). Section 1 lists exactly what was
seen. Every analysis below says which of its numbers were already seen; those parts are confirmations by a fixed
pipeline, not predictions. The certification map built from the published figures (hashed 2026-10-30, before the data
were known to be public) is the prediction; the public energies are its test.

**Run before this draft (and nothing else on the real data):** `scratch/level-sota/inspect_static.py`,
`extract_data.py`, `real_data_first_look.py` and three inline follow-ups (outputs in `scratch/level-sota/out/`);
`real_data/code/provenance_check.py`, `convert_real_data.py`, `descriptive_checks.py` (outputs in `real_data/checks/`);
one inline listing of six files of the comparison variant; one inline listing of the multiplier `mu` of the stored
exact certificates (stored numbers only).

## 0. Conventions and inputs

- **Model, graphs, labels, tolerance: unchanged from `map/DECLARATION.md` Sec. 0.** H(Jz) = (1/4) sum_edges (XX + YY +
  Jz ZZ) = A + Jz B on `heavy_hex_graph(d)`, d = 5 (n = 57), d = 7 (n = 115); eta, sector S^z = s (33 up / 24 down,
  67 / 48; M_0 := sum_i eta_i = 9, 19). Seven label families: m_s; Czz_bar (64 / 132 edges); C2_bar (87 / 185 second
  neighbours); Z_bulk (site 46 / 93); Z_boundary (site 4 / 6); Czz_edge ((11, 46) / (23, 93)); Z_loop (the 12-site
  loop through the bulk site). **tau = 0.06 |O_GS|.** "Certified" means w_O <= tau.
- **Data (plain JSON only; no script unpickles anything):** `converted/real_n57.json` (SHA-256 `ec96cd6d...acedc4dd`),
  `converted/real_n115.json` (`5890160c...233d0002`), `converted/lattice_maps.json` (`a066581a...2586ec81`); full
  hashes in `converted/SHA256SUMS.txt`. Source: `source/README.md` (commit `6b8866b6...`, Apache-2.0).
- **The dataset** is the group `skqd_random_flip` (the variant read by the repository's training scripts and by its
  Fig. 2 energy panel). The group `skqd_post_select` is a comparison variant (n = 115: energies and labels; n = 57:
  energies only) and is **secondary** everywhere. The group `dmrg` is the authors' DMRG (bond dimension 320).
- **Couplings:** Jz = k/10, k = 11..60 (50). Training: 1.6-6.0 (45; the repository's `jz_min = 1.6`). Test: 1.1-1.4
  (as in this project's earlier runs). Jz = 1.5 is in neither set and is reported on its own line.
- **Real quantities, per (n, Jz):** E_real := `final_global_energy`; M_real := sum_i `z_basis_opt`[i]; real labels from
  `z_basis_opt`, `2_nn_corr_funcs_zz_basis_opt` (matched to pairs through `2_nn_corr_pairs_zz_basis_opt`, never by
  position) and `z_loop` (matched through `z_loop_sites`), with this project's site labels (identical, Sec. 1 T1).
  E_first := `ground_state_energy` of the label file (energy before the basis optimization; no label of that state is
  public).
- **Truth:** O_GS and E0 are this project's bond-dimension-320 references where stored (`summary_map.json`: 18 + 16
  couplings), otherwise the authors' DMRG values of the public files. eps_real := E_real - E0; de_real := eps_real/n.
- **Stored objects used:** the chains, thresholds, checks and states of the map
  (`map/laptop_analysis/out/{chains,thr,chk,states}`, read through `make_limit` of
  `map/laptop_analysis/code/analyze_map.py`, imported, not changed: `outer(E)`, `inner(E)`); the exact certificates of
  `rigor/out_20261031T073328Z`, `rigor/out_20261031T100015Z` and `final_tests/` (220 files named `*_cert.json`, each
  with its verification record `*_ver.json`; 196 distinct ones were re-proved in `reports/math-rigorous-bounds.md`; the
  pipeline de-duplicates by SHA-256, uses those for n = 57 and n = 115 and prints the number used; kinds `m_s`,
  `Czz_bar` and `H`, the last being bounds on the plain Hamiltonian); `method/code/ml2.py`; `learning_ibm/code/` (as
  templates); `bias_law/code/n19b.py`.
- **What every stored state file holds** (`states/<sid>.json`): its energy at its own coupling (TeNPy and the
  independent evaluator), all seven labels, every site magnetization (`Z_graph`), every edge correlator
  (`Czz_edges`), `in_sector`, bond dimension, and the SHA-256 of its tensors. Hence, for any stored state phi and any
  coupling J, **E_phi(J) = E_phi(J_g) + (J - J_g) (1/4) sum_e <Z_i Z_j>_phi** exactly (H = A + J B), and its labels do
  not depend on J.
- **What every exact certificate holds** (`*_cert.json`): task (n, Jz, label kind, sigma, lam as a rational), cluster
  bounds `t` and the multiplier `mu` (integers over 2^K), `E_claim` = sum_k t_k - mu M_0. It proves the operator
  inequality **H(Jz) - sigma lam S O + mu M_tot >= c, with c := sum_k t_k = E_claim + mu M_0** (M_tot = sum_i Z_i).

## 1. What has already been seen (all descriptive; nothing here was a declared test)

**From the first look** (`scratch/level-sota/out/real_data_first_look_stdout.txt`, `real_data_first_look.json`,
`real_data_details_stdout.txt`, `gap_check_stdout.txt`, `final_checks_stdout.txt`; report `reports/level-sota.md`):

- F1. Names, types and shapes of every field; DMRG settings (320, 1e-6).
- F2. At all 50 couplings and both sizes (in the JSON; 19 couplings printed): E_real, E_first, `energy_vopt`, the
  post-select final energy, the authors' E0 and first excited energy, eps_real, de_real, eps_real over the gap; the
  digitized eps and ratios; **m_s of the real label and of the authors' DMRG**; the largest site error; the fraction
  of sites more ordered than DMRG.
- F3. eps_real / eps_digitized over the 45 training couplings: 0.940-1.197, median 0.994 (n = 57; 43 within 5 %, all
  within 20 %); 0.986-1.015, median 1.0005 (n = 115).
- F4. de_real at Jz = 1.1-1.5: 0.0214, 0.0198, 0.0180, 0.0154, 0.0126 (57); 0.0227, 0.0197, 0.0172, 0.0154, 0.0157 (115).
- F5. **The accuracy factor for m_s** at 1.1-1.4: same-coupling form 396.2, 268.8, 180.7, 116.5 (57) and 143.1, 124.6,
  100.6, 79.4 (115); the paper's form with the real energy at 1.6: 210.2, 154.5, 113.9, 85.7 (57) and 73.5, 73.9,
  68.4, 60.2 (115).
- F6. **Status of m_s with the real energy against the stored in-sector thresholds**, at the couplings of the stored
  map: not certified up to 3.0; certified from 3.2 (57) and from 3.3 (115); energy over threshold 1.31 (57, 3.0),
  0.955 (3.2), 0.921 (3.3), 0.765 (3.4), 0.548 (3.6); 1.20-1.18 (115, 3.0), 0.747-0.735 (3.3), 0.389 (3.6).
- F7. **Miss of the real m_s in units of tau at all 100 points**: positive at all 100; 4.95 (57, 1.1) down to 0.04
  (6.0); 4.67 (115, 1.1) down to 0.01; above tau at Jz <= 1.9 (57) and <= 1.8 (115); above tau/2 at <= 2.4 and <= 2.2.
- F8. Fraction of sites more ordered than DMRG: 1.00 at the 14 couplings printed per size, except 0.98 (115, 1.5).
- F9. Filter counts from F6 and F7: 29 of 45 training couplings at Jz >= 3.2 (57), largest miss there 0.207 tau; 16
  below, missing by 0.213-1.668 tau, 9 above tau/2, 4 above tau. 28 at Jz >= 3.3 (115), largest miss 0.152 tau; 17
  below, 0.159-1.543 tau, 7 above tau/2, 3 above tau.
- F10. Energy error per site before the optimization, after it, and for the post-select variant, at six couplings per
  size; the authors' gap against this project's gaps and the digitized gap.

**From this task** (`real_data/checks/descriptive_checks_stdout.txt`, `descriptive_checks.json`):

- T1. Lattice: the repository's edge lists equal this project's graphs as labelled sets (identity map of the sites);
  its two-colouring equals eta; its pair lists are this project's edges plus second neighbours (151 / 317), its loops
  this project's 12-site loops (4 / 12); the pair order differs between the DMRG and the label files.
- T2. **sum_i <Z_i> minus M_0 at every coupling.** Dataset, n = 57: -0.2342 (Jz 1.1) to -0.0004 (5.9), negative at all
  50, within 0.05 at 40. n = 115: -0.4352 (1.1) to -0.0027 (6.0), negative at all 50, within 0.05 at 34. Comparison
  variant, n = 115: -0.4524 to 0.0000 (exactly 0 at 5.9 and 6.0). Authors' DMRG: within 1.9e-8 (57) and 2.9e-5 (115).
- T3. Consistency identity (Sec. 8, gate G2): the exchange part E_real - (Jz/4) sum_e <ZZ>_e as a fraction of the
  largest size the published <Z_i>, <Z_j>, <Z_iZ_j> allow: 0.932-0.989 (57) and 0.952-0.997 (115) for the dataset,
  never above 1; above 1 at four couplings of the comparison variant at n = 115 (5.6: 1.059, 5.7: 1.058, 5.9: 16.7,
  6.0: 28.7). No pair distribution is negative. The edge sum of the real ZZ correlators entered this computation; it
  was not printed, stored or compared with DMRG.
- T4. `energy_vopt` equals `final_global_energy` bit for bit in all 200 label files. E_real - E0(authors): 0.0468 to
  1.2198 (57), 0.0458 to 2.6138 (115); never negative. E_first - E_real: 0.191 to 3.654 (57), 3.20 to 15.00 (115).
- T5. Authors' DMRG against this project's references at the stored couplings: at most 1.5e-4 tau (57) and 2.8e-4 tau
  (115) over the seven label types; energies within 1.9e-6 and 3.0e-5.
- T6. Comparison variant at n = 115, Jz = 5.5-6.0: ranges of |z|, of ZZ and of the loops (labels with |z| = 1 at 5.6,
  5.9, 6.0).
- T7. The multiplier mu of the stored certificates (no real datum involved): m_s on the side that opposes the order,
  -2.14 to -0.90 (57) and -1.71 to -1.00 (115); m_s on the other side, -0.04 to 0.26; Czz_bar, -1.46 to -0.46.
  Certificates exist at n = 57 for Jz = 3.4, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0 and at n = 115 for 4.0 and 6.0.

**Not seen by anyone:** any real label other than m_s compared with its reference (Czz_bar, C2_bar, single bonds,
second neighbours, loops; single sites except F2's two summary statistics); any status of a label other than m_s; any
exact-arithmetic interval at a real energy; any quantity at the mean-magnetization-aware window of Sec. 2; any ratio
of a real bias to the n = 19 curve; any learning result on real labels; any interval width at a real energy.

## 2. The window for the real states: energy and mean magnetization

**Why a new rule is needed.** The published labels are those of the state after the basis optimization,
U(theta) |psi>, with U a product over edges of CX-RY-CX blocks, i.e. of exp(-i theta_e Y_i X_j / 2)
(`qaml/skqd/basis_optimise.py` 22-34, 284-290). Y_i X_j does not commute with the total magnetization, and the
data confirm it (T2). The paper's m_s statuses assume in-sector states (`main.tex` 284, 303-310, 1008). That
assumption does not hold for these labels. The exact-arithmetic bounds need less: only the mean total magnetization
(`reports/math-rigorous-bounds.md`, verdict 1), and the public files give it.

**Window.** W(E, M) := { rho : Tr rho H <= E, Tr rho M_tot = M }. The paper's sector window is W_s(E) (states with
Pi rho Pi = rho); W_s(E) is contained in W(E, M_0).

**Certified side (theorem; labels m_s and Czz_bar).** For a certificate (sigma, lam, c, mu) at the row's coupling and
any rho in W(E, M): sigma <O> <= u_sigma(E, M) := (E - c + mu M) / (lam S).
- *Between certificate couplings (m_s).* Two certificates of the same sign at J_1 < J < J_2 combine with
  t = (J_2 - J)/(J_2 - J_1): the convex combination of the two operator inequalities is the inequality at
  (J, lam_t = t lam_1 + (1-t) lam_2) with c_t = t c_1 + (1-t) c_2 and mu_t = t mu_1 + (1-t) mu_2. Pool: every direct
  certificate at J and every pair with J_1 < J < J_2 among the stored certificate couplings of that size.
- *Czz_bar.* A certificate for the plain Hamiltonian at J' (base coupling J_b, J' = J_b - 4 sigma_b lam_b) bounds the
  label at any target J: for J' < J, Czz_bar <= 4 (E - c + mu M) / ((J - J') n_e); for J' > J,
  Czz_bar >= -4 (E - c + mu M) / ((J' - J) n_e). No combination is needed (a pair never beats its better member, the
  bound being a ratio of two affine functions of t). Pool: every stored certificate of kind `Czz_bar` or `H` of that
  size (kind `H`: J' = its coupling).
- *Interval.* U_sigma := max over M in {M_real, M_0} of [min over the pool of u_sigma(E_real, M)];
  **I := [-U_-, U_+]** (capped at the spectral range). I contains the label of the published state (M = M_real) and the
  sector ground-state value (M = M_0, energy E0 <= E_DMRG <= E_real, gate G3). **CERTIFIED (exact)** iff
  width(I) <= tau. Also reported: the reference-free version tau_rf = 0.06 min |O| over I (as Test C of
  `final_tests/DECLARATION.md`).
- Arithmetic: `fractions.Fraction` throughout; E_real, M_real and tau enter as the dyadic numbers they are; a numerical
  allowance of 1e-6 is added to E_real and M_real is taken at the worse of M_real +- 1e-6 (the authors' own validation
  tolerance, `calculate_obs_basis_opt_from_skqd.py` 127).
- Range: certificates exist at n = 57 for Jz in {3.4, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0} and at n = 115 for {4.0, 6.0}, so
  the m_s interval exists on [3.4, 6.0] and [4.0, 6.0]. Outside, no row can be CERTIFIED (exact).
- Every choice among certificates is a choice among theorems, so taking the best is legitimate and needs no
  correction for multiplicity.

**Not-certified side (explicit states; all seven labels).** Let q := (M_0 - M_real)/2 (seen: 0 < q <= 0.117 at n = 57,
<= 0.218 at n = 115). Let r be a stored S^z = s - 1 reference state (R3; M = M_0 - 2) of a grid coupling that brackets
the row's coupling, with energy E_r(J) re-evaluated at the row's coupling (Sec. 0); of the two candidates the one
with the lower E_r(J) is used. Put E* := (E_real - q E_r(J)) / (1 - q). If rho_+ and
rho_- are in-sector states with energy at most E*, then (1-q) rho_+- + q |r><r| lie in W(E_real, M_real) and their
labels differ by (1-q)(o_+ - o_-), whatever the label of r. (H, M_tot and every label operator conserve S^z, so the
superposition sqrt(1-q) |phi> + sqrt(q) |r> of a pure in-sector phi with r has the same three expectation values: pure
witnesses exist as in Lemma P of the paper.) Hence **NOT CERTIFIED (explicit states)** iff
**(1 - q) w_in(E*) >= tau**, with w_in the hull width of `hull.py` over the pool:
- at a coupling with a stored chain: all stored in-sector states of that (n, Jz), as in the map;
- at any other coupling: all stored in-sector states of the two grid couplings that bracket it, each re-evaluated at
  the row's coupling by the linear rule of Sec. 0 (every coupling of the dataset lies between two grid couplings).
If M_real > M_0 at some point, R4 (S^z = s + 1; n = 57 only) replaces R3; without such a state the row is GRAY.

**GRAY** otherwise.

**Like-for-like statuses (the paper's sector hypothesis, kept for comparison with the prediction).** At a coupling
with a stored chain: CERTIFIED_s iff w_out(E_real) <= tau; NOT CERTIFIED_s iff w_in(E_real) >= tau; GRAY_s otherwise,
with `outer` and `inner` of the stored map evaluated at E_real (no factor 0.8 or 1.2, no delta-chi: E_real is an
absolute energy; the reference term delta-G stays inside `outer`). At other couplings: eps_tau_out and eps_tau_in
interpolated log-linearly in Jz between computed grid points (the stored J* rule), flagged "interpolated, not a bound".
A CERTIFIED_s status is a statement about in-sector states and is **never** called a certificate of a real label.

## 3. (b) The map on the real energies

- **Rows:** 2 sizes x 50 couplings x 7 labels. For each: eps_real, de_real, q, the three statuses of Sec. 2 with their
  intervals and widths in units of tau, f_in = eps_tau_in/eps_real and f_out = eps_tau_out/eps_real (how far the
  energy could move before the like-for-like status changes), and for exact rows the largest eps at which the row
  would still be CERTIFIED (exact).
- **J\*** (per label and size; stored definition: the smallest training Jz from which every larger training point is
  certified; resolution 0.1): J*_s with CERTIFIED_s (interpolated thresholds where no chain is stored), and
  **J*_exact** with CERTIFIED (exact) (m_s and Czz_bar; both tolerances). Counts out of 45: certified (each rule), not
  certified, gray.
- **Table "predicted from the figures versus obtained from the data"**: the 171 rows of the stored map
  (`summary_map.json`, reading 1): predicted status | like-for-like status at E_real | relation | status of Sec. 2.
  Relation: *confirmed* (same decisive status), *resolved* (predicted GRAY, obtained decisive), *opened* (predicted
  decisive, obtained GRAY_s), *contradicted* (CERTIFIED against NOT CERTIFIED). Also: stored J* against J*_s; the
  stored claims C-A, C-B, C-C re-evaluated (C-B no longer conditional on a floor).
- **Rule.** The figures-based map is **confirmed by the data** iff no row is contradicted and, for every label and
  size with a stored J*, |J*_s - J*_stored| <= 0.1. Already seen: the m_s rows (F6): no contradiction; 57 qubits: 3.2
  and 3.3 resolve from GRAY to CERTIFIED_s. Not seen: the other six labels.
- **Expected and stated now.** J*_exact cannot lie below 3.4 (57) or 4.0 (115), where the certificates end; the term
  mu (M_real - M_0) widens the exact interval slightly (|mu| <= 2.14, |M_real - M_0| <= 0.012 at Jz >= 3.2 for
  n = 57). The number "certified from 3.2, 29 of 45" (F6, F9) is a like-for-like number and must not be printed as a
  property of the real labels.
- **Secondary rows:** the window at E_first (first-stage states are in the sector by construction: recovery and
  diagonalization in sector configurations, `qaml/skqd/skqd.py` 216-250, 284-296), like-for-like statuses of m_s
  only; the comparison variant (n = 115 with labels, minus the four couplings of gate G2; n = 57 like-for-like only).
- **Extension E1 (decided: YES; shown in a separate column):** new m_s certificates with the stored optimizer settings
  (the declared lambda grid and stage rule of `rigor/DECLARATION_v2.md`, unchanged), verified exactly, in this order of
  priority: n = 57 at Jz = 3.3 and 3.2; n = 115 at Jz = 5.0, 3.6 and 3.3. Laptop only, at most 8 hours of wall time
  in total; a coupling not finished within the cap is reported as not computed. They are theorems; they extend the
  range, they never replace the columns above, and the set S of Sec. 7 (f3) is fixed WITHOUT them (the E1-extended
  set is reported as secondary if E1 finishes).

## 4. (c) The accuracy factor at the test couplings

- de*_in(n, Jz) := stored rigorous inner threshold of the row (`de_star_in`; explicit in-sector states), Jz = 1.1-1.4;
  at 1.5 the threshold of the re-evaluated pool of Sec. 2 with q = 0. de*_out alongside.
- **Form A (same coupling):** F_A = de_real(n, Jz) / de*_in(n, Jz). **Form B (the paper's present form):**
  F_B = de_real(n, 1.6) / de*_in(n, Jz).
- Labels m_s (headline) and Czz_bar. Reported: every value at both sizes; the headline is the smallest F_A over
  Jz = 1.1-1.4 at n = 57, rounded down to two significant digits ("more than ..."), and the same for n = 115 and for F_B.
- Already seen: all m_s values (F5). Not seen: Czz_bar.
- Stated with the number: the in-sector window is a subset of what the energy and the mean magnetization allow, so
  the factor is a lower bound on what the weaker hypothesis would require.

## 5. (d) Predictions of the emulation, confronted with the real labels

For each family x (57 / 115 sites; 64 / 132 edges; 87 / 185 second neighbours; 4 / 12 loops), with Neel values eta_i,
-1, +1, +1, let **t_x := (o_x^real - o_x^GS) / (o_x^Neel - o_x^GS)** at each coupling.

- **P1-P3 (sign: every label lies on the Neel side of the truth).** F := fraction of (item, coupling) pairs with
  t_x > 0, per family and size, over the 50 couplings. **Rule: holds iff F >= 0.95** for that family and size.
  Reported: F per coupling; the fraction with t_x <= 1 ("between the ground state and the Neel state"). Seen: sites at
  14 couplings per size (F8) and the sign of m_s (F7). Not seen: edges, second neighbours, loops.
- **P4 (the error decreases with Jz).** D(n, Jz) := mean over the items of |o^real - o^GS| / (0.06 |o^GS|), per family;
  **rule: Spearman rank correlation with Jz <= -0.9** over the 50 couplings. Seen for m_s (F7). Not seen: the rest.
- **P5 (the bias-against-energy curve of Sec. V).** Recipe of the n = 19 curve unchanged (`bias_law/code/n19b.py`:
  exact ground state at n = 19 at the same Jz, top-D truncation, 26 levels, read by linear interpolation in
  sqrt(de)), computed at the 50 couplings. Delta := m_s^real - m_s^GS; ratio := Delta / curve(de_real); miss :=
  |m_s^real - curve(de_real) - m_s^GS| / tau. **Pass rule of the earlier blind test (`final_tests/DECLARATION.md`
  Sec. 3), applied to the 50 couplings of each size: mean miss <= 0.2 tau at n = 57 and <= 0.6 tau at n = 115, and
  every ratio in [0.75, 1.3] at the couplings where the raw miss is at least 0.2 tau.** Ratios elsewhere are
  reported and do not decide. Comparators as before: the chord and the truth at n = 19.
  Seen: Delta and de_real separately at all 100 points; which couplings have a raw miss above 0.2 tau. Not computed:
  any ratio or corrected miss.
  Stated now: the curve was built for the first stage (truncation in the computational basis). The real labels come
  after a rotation that lowers the energy error per site five- to tenfold. A pass extends Sec. V to the full method; a
  fail restricts Sec. V to the first stage, and the paper says so. Prior (judgment): pass 0.4.

## 6. (e) The label filter on the real labels

- **Rule (m_s primary, Czz_bar secondary): keep a label iff its row is CERTIFIED (exact) (Sec. 2).** Guarantee: a kept
  label is within tau of the truth, given the published energy and site magnetizations.
- Reported, per size, over the 45 training labels (the five others apart): number kept; largest and mean miss among
  kept and among dropped labels; dropped labels within tau/2 and within tau (the cost); kept labels above tau/2.
- Like-for-like version (stored thresholds, interpolated where there is no row; the paper's present filter) next to
  it. Seen: F9.
- **The small classical calculation, next to every label (descriptive, no rule):** |m_s(exact, n = 19) - m_s^GS(n)| in
  units of tau at all 50 couplings and both sizes (the n = 19 ground states are those of Sec. 5, P5); its largest value
  over the kept labels and its values at the test couplings. The paper's present sentence ("a range in which an exact
  19-site calculation already lies within a fifth of the tolerance") is re-evaluated on the kept set, whatever it gives.
- Said in advance: where the labels are already accurate the filter buys a guarantee, not accuracy.

## 7. (f) Learning tests on the real labels

Truth: the authors' DMRG at all 50 couplings. Scripts: new files derived from `learning_ibm/code/learn_ibm.py` and
`prop2_cubic.py`, changed only in the data loader; the stored scripts are not edited. Seeds: integer of the first
eight hex digits of the SHA-256 of the hashed declaration.

**(f1) The realistic test, as `learning_ibm/` (README and `PROP2_DESIGN.md`).** n = 57 primary, n = 115 secondary.
Training range: the 45 real training couplings; test couplings 1.1-1.4 (1.5 apart). Models: cubic in 1/Jz
(`ml2.fit_poly`, ridge 1e-8; primary), nearest-neighbour null, the pilot perceptron; the dataset paper's architecture
1 at n = 57, test range only. Standard conformal, alpha = 0.1, plain jackknife over couplings; in distribution (each
training coupling held out in turn) and out of distribution. Control on DMRG labels. Proposition 2(a) and (b) for the
cubic with each label's energy interval at (E_real, M_real): upper version = the interval I of Sec. 2 where it exists,
otherwise not available (the like-for-like `outer` is reported as indicative); lower version = (1-q) times the hull
of explicit states.
Predictions of the emulation-based test, confronted: **L1** the cubic misses the true m_s by more than tau at each of
1.1-1.4; **L2** standard intervals calibrated on the real labels cover the truth at none of the four test couplings;
**L3** the intervals of 2(b) calibrated on all 45 labels are wider than tau at every coupling (lower version). Each
holds iff true at n = 57; n = 115 reported.

**(f2) The learner-independent floor** (`reports/math-learning.md`, finding 02): for any learner and the
constant-width score, 2q >= w_(k), the k-th narrowest calibration interval, k = ceil((m+1)(1-alpha)) = 42 for m = 45.
Computed with the lower widths, reported in units of tau(x) at every query. **Holds iff the floor exceeds tau.**

**(f3) The constructive test: train and calibrate only on labels certified at their own energy.**
- S := the training couplings whose m_s row is CERTIFIED (exact) with the reference tolerance, fixed by Sec. 3 and
  written to a file with its SHA-256 before any learning number is computed. Nested sets: S_3/4 and S_1/2 (interval
  at most 3/4 and 1/2 of tau wide). S, S_3/4 and S_1/2 use the stored certificates only (not those of E1).
- 200 random splits of S (seeded): 6 training couplings, 12 calibration couplings, the rest queries (needs |S| >= 20;
  with 15 <= |S| < 20: 4, 9, rest; below 15 the test is not run and this is reported).
- Models, fitted to m_s on the training couplings: M1 line in 1/Jz; M2 1 - a/Jz^2 - b/Jz^4. Control M0: the cubic in
  1/Jz trained on every real training label outside the calibration and query couplings of the split (uncertified
  labels included).
- Scores s_j = max(|f(x_j) - lo_j|, |f(x_j) - hi_j|) over the calibration label's interval I_j; q = the
  ceil((m+1)(1-alpha))-th smallest; interval f(x) +- q. Also Proposition 2(a): W(x) = sum_j |a_j(x)| width(I_j).
- **Primary set S_p (decided before the hash, from theory and not from data):** by (f2) the interval returned by 2(b)
  is at least as wide as the widest calibration label interval, so a guarantee below tau needs calibration labels
  certified to better than tau. S_p := the most stringent of the nested sets S_1/2, S_3/4, S that has at least 15
  couplings; it is determined by Sec. 3 and written to a file with its SHA-256 before any learning number is computed.
  If S itself has fewer than 15 couplings the test is not run, and this is reported.
- **Pass rule, n = 57, set S_p, both M1 and M2: (W) in at least 90 % of the splits, 2q <= tau(x) at every query; and
  (C) the truth lies within q of the prediction in at least 90 % of all (split, query) pairs.** FAIL otherwise. The
  same for M0, for the other nested sets, and for n = 115, all secondary and all reported.
- Stated now: by (f2), 2q is at least the widest (m = 12) calibration interval, so labels certified at nearly tau make
  (W) fail even with a perfect model; the nested sets measure the margin that a guarantee below tau needs. The
  forecast from emulated labels in [4, 6] was 0.71-0.76 tau (`reports/level-experiment.md` Sec. 2.3). Prior
  (judgment): pass on S 0.4, on S_1/2 0.8.
- Limit to print with the result: between Jz = 4 and 6 the true m_s changes by 0.4 tau. The test shows that the
  intervals survive the learner and its calibration where labels are certified. It does not show that a hard function
  was learned.
- Secondary, same splits: the width-normalized score |f - y| / sigma(x), sigma(x) = log-linear interpolation in Jz of
  the calibration labels' interval widths (`reports/math-learning.md`, proposal P3).

## 8. Gates (a failure means "no decision" for what depends on it; the reason is reported)

- **G1 data:** `convert_real_data.py` re-run on the pinned archive reproduces `converted/SHA256SUMS.txt`.
- **G2 same state:** at every (n, Jz) used, the exchange part E_real - (Jz/4) sum_e <ZZ>_e lies in
  [-B, B], B = sum_e (1/2) sqrt( ((1 - <ZZ>_e)/2)^2 - ((<Z_i> - <Z_j>)/2)^2 ) (a necessary condition for the
  energy and the labels to belong to one state: on an edge, |<XX + YY>|/4 <= sqrt(p_01 p_10)). Seen: holds at the 100
  points of the dataset, where the exchange part is negative and at 0.93-0.997 of -B; fails at Jz = 5.6, 5.7, 5.9, 6.0
  of the comparison variant at n = 115, which are excluded everywhere.
- **G3 energies:** E_real >= E0(authors) at every coupling (seen: holds).
- **G4 truth:** authors' DMRG against this project's references at the stored couplings: |dO| <= 1e-3 tau for the
  seven label types, |dE0| <= 1e-4 (seen: holds).
- **G5 certificates:** every certificate used has a recorded exact verification; the certificates that decide
  J*_exact and the boundary of the filter are re-proved with the independent verifier of
  `scratch/math-rigorous-bounds/myverify.py`.
- **G6 linear re-evaluation:** for the two decisive witness components of every NOT CERTIFIED row within 0.3 of a J*
  and of ten other rows drawn with the seed, the energy at the row's coupling recomputed from the stored tensors with
  the independent evaluator agrees with the linear rule to 1e-8; every re-evaluated in-sector energy is at least
  E0(Jz) - 1e-6.
- **G7 filter:** every CERTIFIED (exact) label and its truth lie inside its interval. A violation is reported as an
  inconsistency of an input.
- **G8 code:** the analysis code is written and unit-tested on synthetic numbers and on the stored emulated labels
  before the hash, without reading `converted/`.

## 9. (g) Reported whatever the outcome

- `RESULTS.md`: an eight-line summary in plain Spanish, then English. For each analysis: the rule, the outcome against
  it (PASS, FAIL, HOLDS, DOES NOT HOLD, NO DECISION), every number, and a mark on every number already seen (Sec. 1).
- The table of Sec. 3 in full; J* under each rule; the counts; the factors of Sec. 4 in both forms; F and the rank
  correlations of Sec. 5 for every family; ratios and misses of P5 at every coupling; the filter's kept and dropped
  labels with their misses; widths, coverage and largest miss of every model and calibration of Sec. 7.
- The finding of Sec. 2 (the labels are not in the sector; sizes of the deviation) is reported in any case.
- Failures with the same prominence as passes. No rule changes after the hash; any further analysis goes into a
  section "post hoc". Lists of what was re-executed, only compared and not checked; `SHA256SUMS.txt`; `DEVIATIONS.md`.
- Laptop only: no cloud, no processor time, no new DMRG; exact diagonalization at n = 19 only (P5 and the comparison
  of Sec. 6); new certificates only for E1 (Sec. 3).

## 10. Decisions taken by the coordinator before hashing (2026-11-12)

1. **Notion of "certified" for the real labels: the window W(E, M) with M in {M_real, M_0}** (Sec. 2). The sector
   window is kept only for the like-for-like comparison with the prediction.
2. **Primary tolerance: the reference tolerance tau = 0.06 |O_GS|** (the paper's definition, comparable with the map);
   the reference-free tolerance is reported next to it for every exact row, and every count is given for both.
3. **Extension E1: yes**, as specified in Sec. 3 (laptop, capped, separate column).
4. **Primary set of (f3): S_p**, the most stringent nested set with at least 15 couplings (Sec. 7); S and the other
   nested sets are secondary and reported.
5. **P5 uses the 50 couplings of each size**, as written; the same numbers restricted to the 45 training couplings are
   reported next to them and do not decide.
6. The hypothesis behind every exact statement about a real label is stated with it: the published energy and the
   published site magnetizations are expectation values of one and the same state (supported by gate G2 and by the
   reading of the authors' code; not provable from the files).

## 11. Manifest at hash time (completed by the sealing task `rd-seal` on 2026-11-12, before the hash)

Paths are relative to `real_data/`. The first seven lines are those of the draft: the sealing task did not recompute
the first four (it opens neither `converted/` nor `source/`) and found the three code lines equal to the files on
disk. Every other line was computed by `checks/make_manifest.py` on 2026-11-12 at 19:18 UTC and is checked again by
`python -B -I checks/make_manifest.py --check`. A line `tree:<folder> [<patterns>] (<N> files)` is the SHA-256 of the
text made of one line `<SHA-256 of the file>  <path relative to the folder>` per matching file of that folder
(recursively), in bytewise order of those paths.

**Secs. 0-10 are, byte for byte, those of the reviewed draft** (SHA-256 of that draft:
`c796624c26b5ca5260adbc2ee5d8c2f3ce60b906a7cfdbbb639431cd7fa261b3`; copy in
`checks/DECLARATION_reviewed_draft_before_seal.md`). The sealing task wrote this section and Sec. 12 only.

**Gate G8 at hash time.** The sealing task ran every unit test on exactly the files listed below, on 2026-11-12 from
19:00 to 19:01 UTC, with `DECLARATION.sha256` absent (Python 3.11.4, numpy 1.26.4, scipy 1.13.1, `python -B -I`, two
threads): 33 unit tests of the map code (8 on stored objects, 25 on synthetic cases; none skipped) and 164 checks of
the prediction and learning code (20 + 70 + 54 + 20). All passed. A further cross-check of 28 points passed: the file
of nested sets written by the map code is accepted and used by every reader of the learning code (run on the
synthetic dry run of the map task). No test opened a file of `converted/`: the synthetic map tests record every file
they open, and the others ran on scratch folders while the guard of the real folder was closed. The outputs are the
`checks/G8_*` files. No code or test file was changed by the sealing task.

```
ec96cd6d49a160ba91b38a08f987d221aa01c465c470e0eb17c13f9bacedc4dd  converted/real_n57.json
5890160c5ff0992b0859ce44fba3a74d1aff6fa6e005f8ef0d0db4f4233d0002  converted/real_n115.json
a066581a316dbcfacabe8b50f318dc323fc05eaf67c67f99209cc4282586ec81  converted/lattice_maps.json
13aa8e69c9bc614c72c5a415ecd889f113eabe95eec81e221174b3f14dedbb91  source/archive/quantum-groundstate-learning-6b8866b66d62aaf3ee815cd14fa58e9bf4629d66.tar.gz
f0dcb169eee2c16161c9b542295ca4182a706cca6ec9c5c2683b6c28a0a725cd  code/convert_real_data.py
0a32fd79c98f664cfe246132d42831ff94d526b410554a5a314a601c6f48a898  code/descriptive_checks.py
ae7bae1b670b35e3488628c02be8753ef02ece89dd914503964cc5f595fbdb1a  code/provenance_check.py
# analysis code of Secs. 2-7 and gates G1-G7 (every other file of code/)
79687c7aac4d5e8950bad2fd9838562d4d24a8d98894fc14d15e04fea4d11a57  code/README.md
5415cd0c2f93e9b2dde5d70e7d4745c5b326aa56c290bf13fca7d5e82c84cd08  code/README_predict_learn.md
76fc65927e9c5e2f66e8a1e302fbd6a8c004f0fc413a434ee7c72babd4d829bd  code/SHA256SUMS.txt
ad86cbff90ac383485d353b8954ab7fb841012c4142b08ede0e812025c91e657  code/SHA256SUMS_predict_learn.txt
42c6aa8c34d220b9728d7a20a0f191b8245242416dcbaccdd686b4eaab30c6df  code/make_derived.py
3922350fea0861470d6338bfaa6fb6fe25853cac56cf8b3c83f4ffa4a19b6765  code/map_certs.py
ec8f92a77930571855c53e539fc8b75907214118c2c949664f1ba039316f639d  code/map_common.py
5f1f47a4b0b8e7193e41f936c4084c5be60fe8697d4632041fdb05005b8dc292  code/map_gates.py
e1214cf36f5a3c088b44a2d5155b33be8c3b8c1ab34aab7fba4874eec5ba0728  code/map_stored.py
a1c04230ef8b5db38610c1cd5ef2d82e082a1f4620e2049d258cf8b2461f0fe3  code/map_tables.py
76b74ee922e0ea722bf03ea0304fcdcc9cc56b5dacef37b8854ae56d4a9259e4  code/n19_curves.py
6efde0302f750d3c9e0c9a86909fd86a221b63283250f7a59665275edeeedb3e  code/rd_common.py
3512c22069365d3d2df7f2905bf4d14e2dcaf1ee518dda752db54019d6bc9704  code/rd_f23.py
9c65738a9d8f19ee0f11296e6dbc739a4a6bcada2439d6ade035d5e571ceab86  code/rd_learn_ibm.py
83e2d7fb54f54dae2de30318cff0e5658beed64e70653996eb0f30b385fc692f  code/rd_learn_parts.py
75dd603f4e9c3a337bc7337886a9deacf5ff52815f6cc715dab29b177d21b406  code/rd_predict.py
694adaf0451ed9dedf3b3562c5b3c2b608b9688a89afb7c222aa5500515eb3fe  code/rd_prop2_cubic.py
8332d1f0628911be99b80ecc4c10877a6165b7fd4dd41d83a1ba0f5d866c004f  code/run_learn.py
199e5b0a0a6c0851a7862680fe7ef040b3b5eccc62391a01917069cb9cd1866d  code/run_map.py
41c839785f83bc4017e3fb7642b46fa817230cde6a3b7c90274ab10c9159470b  code/run_predict.py
# unit tests (every *.py of tests/)
09a11f877d522c427936345f783f37962f5e5f69e07c818ffea4e7aa5cfa461c  tests/run_all.py
5792844dd99baa0d423a4e941fb4b8aff2bc0a9e0e0bffbd9f5540143cc08020  tests/run_map_tests.py
a130d77a4372d82e73e49349754a8de6dc8517076acd3ae5a4521740aefd9379  tests/synth.py
d493595b2148d0a4473cc2357ba6929e957745bfb175e7e8d004644f54e6e50e  tests/test_gate.py
2a8916159206d62327106bcd8a772ac264b3d820156a503d2f508868d53de9f1  tests/test_learn.py
15b6e977744172c7d61ab5e7a8a54427a3e2109f563c8f17ef1085731ca9419d  tests/test_map_stored.py
a23eb7e0e84875870362b50ab90e0ac8d6113bdf973fbdd838531ebe12362147  tests/test_map_synthetic.py
3b93f42d791bd8a97290b7831009f56e5baab998c30bd3611f81bca71faf7935  tests/test_port_learning.py
90586d9547944d3aed2a4fcf530a5ae322a07a6a43f15cc442e31fd7d28d592d  tests/test_predict.py
# records of gate G8 and of this manifest
598f4a6127f3dca51fd138da67d68e8044b72f2f5a0d8296cd3edef6ae7330d8  checks/G8_map_tests_pre_hash.txt
ba8e213386a7ad1853dfbc6409d63a7497649f7d862eb20bc74a0ed6fd136d84  checks/G8_predict_learn_tests_pre_hash.txt
97d5e42ab5065f261defa404e63951dedb742ec4ee7fa0d954ffee9ed01b23b0  checks/G8_sets_format_check_pre_hash.txt
69f02ff03b4f756d471e879173e8f5e2c4829636c6990e56c7a2b93866af10fc  checks/G8_map_tests_by_rd-code-map.txt
d1d9ba37f115dbd29bc808aa47c58bcdbb66c1c6a47ef28c547ac46de5a0c2f1  checks/G8_predict_learn_tests_by_rd-code-learn.txt
7adfe2bda049f538131c3cbb056a27a526ecad328b1f4ea188562733fe5b5bb8  checks/make_manifest.py
# computed before the hash, no real datum (exact n = 19)
1c8378ecfbd499e961366b4f2173c450f1d9660865300ab39341727c0c835470  out/n19/n19_curves.json
71bc6c1ac566d30d8bec80a2ff71cee4360a34dd313c5a666ae54d4c739932c3  out/n19/n19_labels.json
1be4ccc7610380a6d2a21c73c5e5fab7d5055524f6a9e4c3810d5b4335263e21  out/n19/SHA256SUMS.txt
# stored code imported unchanged and stored inputs, as they are at hash time
a08178012e860ac49e8b8081ee4386e13f411d70cceaaddb631939451d2f030c  ../map/DECLARATION.md
649ad6464d45ec74adcf899b2167aed36f7513d64d6b48998dc0fa2de77e4fb3  ../map/laptop_analysis/summary_map.json
128ea5066f739bb952e4c8e5fd3620e82e77979d28da3fd7c5f9f5231b6955b3  ../map/laptop_analysis/code/analyze_map.py
8598cdc365b58422c35fc7d5dbdc6fb68f1ea9b994c233a0fa7d7c934fcbc88a  ../map/laptop_analysis/code/hull.py
d9aec0bebeca5e25b9a681571ee56f0ae89139e617b928b5a81e0ad16b9f78b1  ../map/laptop_analysis/code/witness.py
a2993adce626856a94f90c63e80e4737ab76cc691b4e6902c7a863acefb43a54  ../map/laptop_analysis/code/indep_eval.py
cb4c697f65246c33c51fecf66a5e9ce880e2fdc405252b0a9aeee78d5e57cb74  ../map/laptop_analysis/code/readings_declared.json
d8d42f5f54e33699562ba4584ca06925074d206ee8c6baddf73b9ab8c76aace1  ../map/laptop_analysis/code/graphs/hh_d3.json
80790817cc70ed56396799df3ca7205cfe62519477fda50e6e13311b1d528712  ../map/laptop_analysis/code/graphs/hh_d5.json
b5b630097e895a46a6d4072171fec3e5552ec0ea8f6e7b41e9106c9be6e7c8d7  ../map/laptop_analysis/code/graphs/hh_d7.json
35ffcb8651cc2a80c5a17881e66b2548751d3901e21a4b8cb3bd8d67947d1d3c  ../method/code/ml2.py
d8d42f5f54e33699562ba4584ca06925074d206ee8c6baddf73b9ab8c76aace1  ../method/code/graphs/hh_d3.json
80790817cc70ed56396799df3ca7205cfe62519477fda50e6e13311b1d528712  ../method/code/graphs/hh_d5.json
b5b630097e895a46a6d4072171fec3e5552ec0ea8f6e7b41e9106c9be6e7c8d7  ../method/code/graphs/hh_d7.json
f1642735d7e1123c62dba5593831c8bf769995659e1ab04c1a65349ca6a1c549  ../learning_ibm/code/learn_ibm.py
d5c2e452c062eef70916b41129bf19697566826ca06fa4fc63e2623621cca143  ../learning_ibm/code/prop2_cubic.py
8561f97bbbf25e4b1ca5b251b359c7c7a69f9cec34d7528f71dedc01a607f450  ../bias_law/code/n19b.py
aac90b9702d123475505280181f874a484ef1a4e6e8e7f89c85247295b2d83db  ../rigor/DECLARATION_v2.md
8bf821e5af73f180fcab45e0f7c26aec94e1b78107321e7a8a031a5708e9091b  ../final_tests/DECLARATION.md
6015ebb5c41102ab9bf2c8284bf3524221e3e3393d59e156a21d4b8a8a3ee9b8  ../../../paper/reviews/R10_2026-11-12/scratch/math-rigorous-bounds/myverify.py
# stored objects read by the analysis code (tree digests; definition in checks/make_manifest.py)
32ebb502f15c007c20d755bcbb49990a986fb8a2854d1f904c74ebcb29ed79f5  tree:../map/laptop_analysis/out/states [*.json] (2762 files)
1e2a2b13171b4a8982736208cd265862df508fc9abf40ac751c5b96e6e2209eb  tree:../map/laptop_analysis/out/chains [*.json] (342 files)
1c7b93b3d58f2afd2287534849f02dedcba6cce71aa42d5e2ebbc59e441a3ec0  tree:../map/laptop_analysis/out/thr [*.json] (36 files)
4efad90b4d7bf70ba842749b28c83e7f083459fcb531462648d1617869b4c255  tree:../map/laptop_analysis/out/chk [*] (16 files)
15928f77b4f4e4cc4c477ca7b895eda56d80b3ada6703d0d73b3583200c57cc3  tree:../rigor/out_20261031T073328Z [*_cert.json,*_ver.json] (128 files)
8a00ad6f4d2cf86fc1a1472059517232932f223a6e07e3022bc4d19f95caa126  tree:../rigor/out_20261031T100015Z [*_cert.json,*_ver.json] (288 files)
169ebbd5e54351cdc12debd8d2e84027f9e356250311bd326ebff7d955acdddd  tree:../final_tests [*_cert.json,*_ver.json] (24 files)
7dd84531c6f86b1c8c3598314354767697fba8151b13e210d63abf17b96ee612  tree:../map/npz_20261030T022613Z/mps [*.npz] (6 files)
```

## 12. Clarifications before the hash

Written on 2026-11-12 by the sealing task `rd-seal`, after the analysis code had passed gate G8, before the hash and
before any analysis of Secs. 2-7 was run on the real data. The two tasks that wrote the code listed every point where
the text above admits more than one reading (`reports/rd-code-map.md`, 20 points; `reports/rd-code-learn.md`, 16
points). Each line below fixes the reading that the tested code implements. None changes a rule, a threshold or a
primary choice. A point of those two lists that is not named here needed no line: the code follows the text.

1. 2026-11-12, Sec. 0 (truth) and gate G4: "this project's references where stored" are the values held by
   `map/laptop_analysis/summary_map.json`: E0 at its 18 + 16 couplings, and O_GS wherever it has a row for that size,
   coupling and label (n = 57: the seven label types at the 16 grid couplings, m_s and Czz_bar also at 3.2 and 3.4;
   n = 115: m_s, Czz_bar and C2_bar at the 16 grid couplings, Z_bulk at Jz = 4.0). Everywhere else, and for every
   single site, pair and loop of Sec. 5, the truth is the authors' DMRG. Gate G4 compares exactly these stored
   references with the authors' DMRG. Sec. 7 uses the authors' DMRG at all couplings, as written (truth and tau(x) in
   L1-L3, (f2), (W) and (C)); membership of S, S_3/4 and S_1/2 uses the tau of Sec. 0, as fixed by Sec. 3.
2. 2026-11-12, Sec. 2 (allowances): on the certified side the allowance on M_real is applied certificate by
   certificate: every bound of the pool is evaluated at the worse of M_real - 1e-6 and M_real + 1e-6 before the
   minimum over the pool is taken, so U_sigma holds for every M within the allowance; M_0 is exact and carries none;
   E_real + 1e-6 is used with both values of M. An empty interval (upper end below lower end) is an inconsistency of
   an input: the row is not CERTIFIED (exact) and is listed. The explicit-state side has no allowance on M and keeps
   the energy margin of the stored hull (a pool state counts at energy E only if its energy is at most E - 1e-6).
3. 2026-11-12, Sec. 2 (range): "Outside, no row can be CERTIFIED (exact)" applies to both exact labels. A Czz_bar row
   outside [3.4, 6.0] (n = 57) or [4.0, 6.0] (n = 115) is never CERTIFIED (exact) and enters no J*_exact, count or
   filter, although the Czz_bar rule gives a proved interval at every target that has stored certificates with J' on
   both sides of it; such an interval is reported with its width and, if it is within tau, flagged "within tau
   outside the declared range". In the E1 column the range is the one spanned by the stored and the E1 m_s
   certificates of that size together.
4. 2026-11-12, Sec. 2 (pools): "grid couplings" are the 16 couplings of `map/DECLARATION.md` Sec. 3 (1.1, 1.2, 1.3,
   1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.3, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0); a grid coupling is bracketed by itself. "A
   coupling with a stored chain" means that a chain of the row's own label and size is stored there (a row of
   `summary_map.json`); the pool is then that of the map. Otherwise the pool is that of the bracketing grid couplings,
   re-evaluated. So the states stored at the two extra couplings 3.2 and 3.4 (n = 57) serve only the m_s and Czz_bar
   rows at those couplings, and the reference state r of every row is the R3 (or R4) state of a bracketing grid
   coupling. Where the stored map has no chain of a label at a size (n = 115: Z_boundary, Czz_edge, Z_loop; Z_bulk
   except at Jz = 4.0) the like-for-like status is "not available"; the status of Sec. 2 is still computed.
5. 2026-11-12, Sec. 3 (table and J*): of the 171 stored rows, 6 are rows of n = 19 (a gate of the stored map) and
   have no public data: they are listed as "no real data", and the rule is applied to the 165 rows of n = 57 and
   n = 115. A row that is GRAY in the prediction and GRAY_s at E_real is "unchanged" and is none of the four
   relations. "Stored J*" is J* as `map/DECLARATION.md` Sec. 4 defines it (central reading; the strict value is
   recorded next to it), under reading 1: the field `J_star_central` of `summary_map.json`. For m_s it is 3.2 (n = 57)
   and 3.1 (n = 115), where the strict values are 3.4 and 3.3; item F6 of Sec. 1 had already shown CERTIFIED_s from
   3.2 at n = 57, so this line is not blind: it is the stored definition. In every J*, a training coupling without a
   status (no chain to interpolate from, or no decision after a gate) counts as not certified. The stored claims C-A,
   C-B and C-C are re-evaluated on the stored rows twice: with the like-for-like statuses and with those of Sec. 2.
6. 2026-11-12, Sec. 2 and Sec. 10 (reference-free tolerance): it exists only where an interval I exists. It changes
   CERTIFIED (exact), J*_exact, the filter and the certified counts; NOT CERTIFIED (explicit states) always uses the
   reference tolerance.
7. 2026-11-12, Sec. 4 (Jz = 1.5): this project has no reference at 1.5, so E0 and tau are the authors' DMRG values;
   de*_in is the threshold of the re-evaluated pool (stored states of 1.4 and 1.6) with q = 0; "de*_out alongside" is
   the log-linear interpolation in Jz of the stored outer thresholds (`eps_tau_out_lb`) of 1.4 and 1.6, flagged
   "interpolated, not a bound". The headline uses Jz = 1.1-1.4 only, as written.
8. 2026-11-12, Sec. 5 (P1-P4): P1-P3 and P4 are each decided separately for every family and size (four families,
   two sizes: eight outcomes for the sign rule and eight for the rank rule); the names P1, P2, P3 are not mapped
   onto families and nothing is aggregated. An item whose t_x is undefined (Neel value equal to the ground-state
   value) counts as not positive. m_s is not one of the four families: its D and rank correlation are printed next
   to them, marked as seen (F7), and add no decision.
9. 2026-11-12, Sec. 5 (P5): P5 is one decision, as in the earlier blind test: PASS iff the mean miss is at most 0.2
   tau at n = 57 and at most 0.6 tau at n = 115 and every ratio at a deciding coupling (raw miss at least 0.2 tau)
   of either size lies in [0.75, 1.3], end values included; the parts of each size are reported. A ratio that is
   undefined (curve value 0) at a deciding coupling counts as outside. The curve is read as `n19b.py` reads it
   (linear interpolation in sqrt(de), end values held outside the range of the curve); the number of couplings read
   outside that range is reported.
10. 2026-11-12, Sec. 7 (f1): L1, L2 and L3 are decided on the cubic in 1/Jz (the primary model) and on m_s; the other
    models and the coverage of the site labels are reported. For L3, "calibrated on all 45 labels" is the calibration
    used for the test queries: its single value of 2q (lower version) is compared with tau(x) at each of the 45
    training and 4 test couplings; the held-out widths (44 labels) are reported. "Changed only in the data loader"
    includes the source of the label intervals, which the real-data branch reads from `out/S_sets.json` (the
    intervals of Sec. 2 at (E_real, M_real)); because the upper version is "not available" where no interval I
    exists, the derived script marks every such upper value as indicative, so that it can neither answer nor pin
    (two wrappers around the unchanged functions `band` and `calib`, active for the real data only). Jz = 1.5 is
    reported for the cubic only.
11. 2026-11-12, Sec. 7 (seeds): the seed governs every random choice of the new code (the splits of (f3); the ten
    rows drawn for gate G6). The neural models of (f1) keep the fixed seeds of the stored `method/code/ml2.py`
    (1000 + s and 2000 + s), which is imported unchanged.
12. 2026-11-12, Sec. 7 (f2): the rule is decided at the four test queries Jz = 1.1-1.4, whose calibration set is the
    45 training labels (m = 45, k = 42, the numbers of the rule): (f2) holds iff the floor w_(42) exceeds tau(x) at
    each of them. Reported and not deciding: the same floor in units of tau(x) at every coupling, and the held-out
    floors (m = 44, k = 41) at every training coupling. A training label without an explicit-state interval enters
    with lower width 0 (a valid lower bound) and is listed.
13. 2026-11-12, Sec. 7 (f3): the split sizes follow the size of the set that is split (S, S_3/4 or S_1/2: 20 or more
    couplings, 6 / 12 / rest; 15 to 19, 4 / 9 / rest; fewer than 15, not run). The 200 splits of a set are drawn with
    `numpy.random.default_rng([seed, n, c])`, c = 0, 1, 2 for S, S_3/4, S_1/2; each split is one permutation of the
    sorted set (first the training couplings, then the calibration couplings, the rest are queries); the same splits
    serve M1, M2, M0 and every score. M1 and M2 are fitted by ordinary least squares (M2 as 1 - m_s on 1/Jz^2 and
    1/Jz^4); M0 is the cubic in 1/Jz with ridge 1e-8, equal to `ml2.fit_poly`. tau(x) in (W) is 0.06 |m_s| of the
    authors' DMRG. The secondary width-normalized score is computed in two variants (with the calibration label
    itself, and with the worst case over its interval); neither decides.
14. 2026-11-12, Sec. 8 (outcomes of a gate): a gate, or a part of one, has three possible outcomes: PASS, FAIL, or
    NOT COMPLETE when it cannot be executed in full on the laptop under the rules in force (the reason is stated).
    Only FAIL gives "no decision". NOT COMPLETE is never reported as a pass; it names what was not checked, and it is
    printed with every result that depends on that gate. For G1 the gate as declared is the re-run of the converter
    on the pinned archive (`run_map.py --g1-rerun`); without the re-run only the hashes are compared and G1 is NOT
    COMPLETE.
15. 2026-11-12, gate G5: "the certificates that decide J*_exact and the boundary of the filter" are the certificates
    behind the exact intervals (both values of M; both members of a pair) of the two rows on either side of every
    change of the CERTIFIED (exact) status between neighbouring training couplings, for m_s and Czz_bar, both
    tolerances, and the E1 column where it exists.
16. 2026-11-12, gate G6: "the two decisive witness components" are the stored states that make up the two extremes
    of the hull (up to two states each) and, when q is not 0, the reference state r. Tensors are on the laptop for six
    stored states only (`map/npz_20261030T022613Z`, n = 57, Jz = 1.6), and Sec. 9 excludes cloud access. The first
    part of G6 is therefore evaluated on the selected components whose tensors are on the laptop; the others are
    counted and listed, and the first part is then NOT COMPLETE (line 14), whatever the number checked. The second
    part (every re-evaluated in-sector energy at least E0(Jz) - 1e-6) is evaluated for every row with a re-evaluated
    pool. Every NOT CERTIFIED status that rests on a re-evaluated energy is printed with this mark. (The linear rule
    is the identity H = A + Jz B; the unit tests of G8 confirmed it to 1e-8 on a stored state with tensors, at three
    couplings.)
17. 2026-11-12, Sec. 3 (E1): E1 certificates are read only from `real_data/e1/`, in the stored file format, each with
    its exact verification record, and pass the same checks as the stored ones. They feed only the separate E1 column
    and the secondary E1 sets.
