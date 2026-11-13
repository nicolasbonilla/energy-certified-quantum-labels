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

## 11. Manifest at hash time (to be completed by the coordinator)

```
ec96cd6d49a160ba91b38a08f987d221aa01c465c470e0eb17c13f9bacedc4dd  converted/real_n57.json
5890160c5ff0992b0859ce44fba3a74d1aff6fa6e005f8ef0d0db4f4233d0002  converted/real_n115.json
a066581a316dbcfacabe8b50f318dc323fc05eaf67c67f99209cc4282586ec81  converted/lattice_maps.json
13aa8e69c9bc614c72c5a415ecd889f113eabe95eec81e221174b3f14dedbb91  source/archive/quantum-groundstate-learning-6b8866b66d62aaf3ee815cd14fa58e9bf4629d66.tar.gz
f0dcb169eee2c16161c9b542295ca4182a706cca6ec9c5c2683b6c28a0a725cd  code/convert_real_data.py
0a32fd79c98f664cfe246132d42831ff94d526b410554a5a314a601c6f48a898  code/descriptive_checks.py
ae7bae1b670b35e3488628c02be8753ef02ece89dd914503964cc5f595fbdb1a  code/provenance_check.py
(analysis code of Secs. 3-7: to be written, tested under G8 and listed here)
```
