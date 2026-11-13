# Rigor test: deviations from DECLARATION.md (SHA-256 fddd7542…)

1. **2026-10-31T08:09Z — exploratory jobs added (post hoc; they do not change the declared verdict).** At β = 3000 the
   declared m_s "−" bounds at n = 57 were ≈ 0.9 J (Jz = 4.0, λ = 0.2196) and ≈ 1.5 J (6.0, λ = 0.3448) below the DMRG
   reference, while every other item was within 0.02 J. Both declared "−" points sit just below the level crossing to a
   reversed-domain in-sector state seen in the map's chains (at n = 57 the chain jumps at λ = 0.2666 for Jz = 4.0 and
   0.3713 for 6.0). To learn whether this is a property of the relaxation near the crossing or of the method, four extra
   n = 57 jobs at smaller field on the same "−" chains (Jz = 4.0: λ = 0.15165, 0.18747; Jz = 6.0: λ = 0.26183, 0.21829;
   exact chain λ, same eball2 settings) and their n = 19 analogues with exact diagonalization were started in the same
   sandbox with a second runner (`outputs/plan_explore.json`, SHA-256 c1f5de9b…, uploaded and logged in
   `out/patches.txt`; job ids prefixed `x_`). Any rigorous statement made from them is labelled post hoc (the bound is
   an exact inequality whatever λ is chosen, but the choice of λ was made after seeing results).
2. **2026-10-31T09:09Z — one exploratory job stopped (cost).** The n = 57 job at Jz = 6.0, λ = 0.21829 (`x_n57_…_l0.21829`)
   was stopped after 8 min because the λ = 0.26183 job of the same chain had already answered the question (its slack
   was 0.006 J against a budget of 0.64 J), and it would have extended the VM time by ≈ 40 min. Its n = 19 analogue ran to
   completion. Only the process I had started was stopped (logged in `out/patches.txt`).
3. **Laptop, after the run — post-hoc analysis script.** `code/analyze_explore.py` (SHA-256 702bb5b2…) was written after
   the hash to evaluate the exploratory points of item 1 (rigorous m_s widths using every verified bound per side). The
   declared `code/analyze.py` was run unchanged and alone decides the verdict.
4. **Optimizer not fully converged (record).** On six items (n = 57: m_s "+" at Jz = 4.0 and 6.0, where L-BFGS-B
   stopped with 0 iterations at the larger β; n = 19: C̄_zz specs Jz' = 6.010 and 14.0, m_s "+" at 4.0 and 6.0) the
   eball2 bound came out weaker than the vball2 one although the eball2 relaxation contains the vball2 one. As declared, the best verified bound per item is used; every bound is
   valid regardless.
