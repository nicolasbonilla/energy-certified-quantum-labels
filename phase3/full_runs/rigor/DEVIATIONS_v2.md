# Rigor test v2: deviations from DECLARATION_v2.md (SHA-256 aac90b97…)

1. **Scheduling order (no effect on results).** `run_v2.py` orders launchable sides by (priority, u_lb). Within a scope this
   mixes "+" and "−" sides, whose u_lb have opposite signs, so the "−" m_s sides and the "+" C̄_zz sides were served first.
   The branch-and-bound per side and its stopping rule are unaffected; only the order (and the late start of S3) changed.
2. **Stage-B cap reached in S2 (record).** The S2 cap of 8 eball2 jobs was used by the 3.4 rows, the 3.6 C̄_zz row and the
   3.6 m_s row (each above 0.85 τ after stage A). No other S2 row needed stage B. S1 and S3 rows were all ≤ 0.85 τ after
   stage A, so no stage-B job ran there (no n = 115 eball2 job).
3. **Waiting for the VM lock.** The lock was held by another agent ("qpu", 09:27:54Z); my start waited (background polling)
   until it was released at 09:56Z, created my lock at 09:56:58Z and started the VM at 09:58:31Z. No other change.
