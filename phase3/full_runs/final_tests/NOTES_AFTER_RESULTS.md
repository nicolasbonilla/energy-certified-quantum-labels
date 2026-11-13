# Notes after RESULTS.md (2026-11-06)

RESULTS.md, DECLARATION.md and DEVIATIONS.md are left as hashed. These notes correct or extend them.

- RESULTS.md says "9 and 20" in two places. The ratio at Jz = 2.5 is 21.06 (0.2073 / 0.0098); -2006 % is a change, not a ratio. The paper says 9 and 21.
- The coordinator recomputed Tests A and B from the raw files with separate code; C1, C2 and the noise scan were only read.
- `code/post_checks.py` -> `analysis/post_checks.json`: post-hoc numbers asked for by paper/reviews/R5_fresh.md, not declared: gains over the regression on the
  same local couplings; linear interpolation of the exploratory misses (limited power of the blind test); truth at n = 19 in the certified range; margins of the map.
- The decision not to submit C3 (deviation 3) was taken by the agent; see the author decision below.

## Author decision, 2026-11-06
Asked whether to confirm not submitting on ibm_fez and to retry only if ibm_kingston is repaired, the author answered "SI AUTORIZO TODO". Read as ratifying deviation 3, as recommended; the author can correct this reading.

## Correction, 2026-11-08 (R6 reading, paper/reviews/R6_fresh.md Sec. 11, R5 S13)
RESULTS.md is hashed (SHA256SUMS.txt, entry `./RESULTS.md`, sha256 3a70e993...f591, unchanged today), so the correction is recorded here and RESULTS.md is not edited.
- RESULTS.md line 3 ("de 9 a 20 veces peor") and line 95 ("by a factor of 9 and 20") should read **9 and 21**. From `analysis/test_b.json`, mean miss of the
  primary corrected label over the mean miss of the 19-site embedded cluster: Jz = 1.6, 0.74203 / 0.081906 = 9.06; Jz = 2.5, 0.20726 / 0.009843 = **21.06**
  (recomputed on the laptop on 2026-11-08 from the stored means; same values as `analysis/post_checks.json` ratio_to_best_*.q_top).
- RESULTS.md line 97 ("20 times worse at Jz = 2.5") is about the secondary family and is right: 0.19583 / 0.009843 = 19.90 (5.29 at Jz = 1.6).
