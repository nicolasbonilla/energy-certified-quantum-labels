# Proposition 2(a)/(b) for the cubic model on the heavy-hex labels -- design note

Written 2026-11-04, before the script `code/prop2_cubic.py` exists and before any of its numbers is computed.
SHA-256 of this file: `PROP2_DESIGN.sha256`, time of hashing: `PROP2_DESIGN_hash_time.txt` (also in `README.md`).
Laptop only; stored outputs only (no DMRG, no diagonalization, no emulation, no device).

## Why

The abstention rule run by `code/learn_ibm.py` is a filter on labels: it answers at a coupling only if the map
certifies the generated label there at that label's own energy. That needs a generated label and its energy at the
query. Proposition 2 of the paper is a statement about the learner: (a) the band W(x) by which a learner linear in
its labels can move when every training label is replaced by any value in its energy interval, and (b) conformal
intervals whose calibration scores take the worst value over each calibration label's energy interval; rule (c)
answers only where such an interval is at most tau wide. Neither (a) nor (b) was computed in the realistic test. This
note fixes how they are computed for the cubic model, which is linear in its labels, and what counts as an answer.

## Inputs (read-only)

- `../method/out_20261030T003230Z/out/emu/emu_n{57,115}_J*.json` (variant `primary`: labels and energy) and
  `.../ref/ref_n*_J*.json` (DMRG truth), loaded exactly as in `code/learn_ibm.py`.
- The certification map's stored chains, thresholds, checks and states, `../map/laptop_analysis/out/{chains,thr,chk,
  states}`, through `make_limit` of `../map/laptop_analysis/code/analyze_map.py` (imported, not changed): `outer(E)`
  (DMRG-referenced interval containing every sector state with energy at most E) and `inner_fast(E)` (hull of the
  stored explicit sector states with energy at most E; a sub-interval of the window).
- `../map/laptop_analysis/summary_map.json` (eps_tau_out per row, for the interpolated label filter).
- `../method/code/ml2.py` (`fit_poly`, `ms`), imported, not changed.

## Definitions

- Model: `ml2.fit_poly` (cubic in 1/Jz, ridge 1e-8), trained per site on the emulated labels; m_s = sum_i eta_i Z_i/n
  of the per-site predictions. Its prediction of m_s at x is sum_j a_j(x) m_s,j with a(x) = v(x)^T (X^T X + 1e-8 I)^-1
  X^T, v(x) = (1/x^3, 1/x^2, 1/x, 1), the same for every site.
- Energy interval of a training label j (m_s): the map's window at the label's own energy E_j = E0_map + eps_emu,j,
  with eps_emu,j = E_primary,j - E0_emu,j as in `learn_ibm.py`. Upper version (valid, DMRG-referenced): `outer(E_j)`,
  width w_out,j. Lower version: `inner_fast(E_j)`, width w_in,j (any interval that contains the window is at least this
  wide). Sanity check recorded: the label and the truth lie in `outer(E_j)`.
- Couplings without a map row (n = 57: Jz = 2.2, 3.5): no interval is computable. Lower versions use width 0 and the
  label itself; upper versions are NOT available and are reported only as an indicative number, with the width at the
  label's energy interpolated log-linearly in Jz between the neighbouring computed rows (2.0 and 2.5; 3.0 and 4.0).
- (a) W(x) = sum_j |a_j(x)| w_j, in units of tau(x) = 0.06 |m_s^truth(x)|. W_lo with w_in (0 at missing rows), W_hi
  with w_out (interpolated widths at missing rows; flagged indicative when any is used).
- (b) Certified scores in the same leave-one-coupling-out calibration as the standard intervals of `learn_ibm.py`
  (model trained on all calibration couplings, residuals of the model trained without each one; the plain jackknife,
  no finite-sample guarantee): s_j = max over y in I_j of |f_-j(x_j) - y|. s_lo,j = max(|f_-j - y_j|, |f_-j - lo_in,j|,
  |f_-j - hi_in,j|); s_hi,j = max(|f_-j - lo_out,j|, |f_-j - hi_out,j|), or |f_-j - y_j| + interpolated width at a
  missing row (indicative). q = the ceil((1-alpha)(N+1))-th smallest score, alpha = 0.1, or the largest if that
  exceeds N (as in `learn_ibm.py`). Interval f(x) +- q; width 2q/tau(x). Coverage of the truth recorded.
- Tests, as in `learn_ibm.py`: in distribution, hold out t in the training range R, train and calibrate on R \ {t},
  evaluate at t (repeat over t); out of distribution, train and calibrate on R, evaluate at Jz = 1.1-1.4. Also
  reported: W(x) of the cubic trained on all of R at each training coupling (in sample).
- Sizes: n = 57 (primary) and n = 115 (secondary; emulation outside its energy calibration; m_s level 7/8).

## What counts as an answer (rule (c) of Proposition 2, m_s only)

- (b): ANSWER at x iff 2 q_hi(x) <= tau(x) with no interpolated width used; ABSTAIN if 2 q_lo(x) > tau(x);
  otherwise abstain by default (upper version not computable) and say so.
- (a) (a statement about the trained model, not about the truth): the prediction is pinned to within tau by the
  energies iff W_hi(x) <= tau(x) (no interpolated width); NOT pinned if W_lo(x) > tau(x).
- Outcome reported whichever way it goes, at every coupling of both ranges. If (b) answers nowhere, the paper must
  say that the learner-side rule answers 0 of 14 couplings and that "3 of 14" is the label filter.

## Also computed (bookkeeping for the label filter, no new rule)

- The label filter with the map threshold eps_tau_out interpolated log-linearly in Jz at the two couplings without a
  map row (2.2 and 3.5 at n = 57), as the paper does for J*: certified iff eps_emu <= interpolated eps_tau_out.

## Not done (declared)

- Jackknife+ (kept the plain jackknife so that (b) is comparable with the standard intervals already reported).
- Other models: (a) needs linearity in the labels; (b) for the neural models is not declared here.
- Site labels (their energy intervals are >= 35 tau wide out of range already).
- A cubic trained on the certified labels only (three couplings for four coefficients).
