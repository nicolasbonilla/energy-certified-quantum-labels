"""fn_abstract_n19_percent.py -- fixer FN (R11 fix pass, 2026-11-13). Read-only.

The abstract states that, at the couplings where the published energy certifies the order parameter (26 at n = 57,
21 at n = 115, 27 at n = 115 with the certificates added after the declaration), the exact 19-site value of m_s lies
within a stated percentage of the reference value. This script prints that percentage from the stored outputs:
  miss (units of tau) = |m_s(n = 19, exact) - O_GS| / tau,  tau = 0.06 |O_GS|  (DECLARATION.md),
so the relative miss is miss_tau * tau / |O_GS|; tau / |O_GS| is read row by row from out/map_rows.json.
Inputs: out/map_summary.json (filter.<n>_m_s.exact), e1/map_e1/map_summary.json (filter.115_m_s.exact_with_E1),
out/map_rows.json (tau, O_GS). Nothing is written except to stdout.
  python -B -I fn_abstract_n19_percent.py > fn_abstract_n19_percent_out.txt
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.abspath(os.path.join(HERE, "..", ".."))          # phase3/full_runs/real_data


def load(rel):
    with open(os.path.join(RD, rel), encoding="utf-8") as f:
        return json.load(f)


summ = load("out/map_summary.json")
summ_e1 = load("e1/map_e1/map_summary.json")
rows = load("out/map_rows.json")["rows"]
ratio = {}
for r in rows:
    if r.get("label") == "m_s":
        ratio[(r["n"], "%.1f" % r["Jz"])] = r["tau"] / abs(r["O_GS"])

cases = [("n = 57, declared certificates", 57, summ["filter"]["57_m_s"]["exact"]),
         ("n = 115, declared certificates", 115, summ["filter"]["115_m_s"]["exact"]),
         ("n = 115, with the certificates added after the declaration", 115, summ_e1["filter"]["115_m_s"]["exact_with_E1"])]
worst = 0.0
for name, n, f in cases:
    kept = sorted(f["kept"], key=float) if isinstance(f["kept"][0], str) else sorted(f["kept"])
    kept = ["%.1f" % float(k) for k in kept]
    miss = f["classical_n19"]["miss_tau"]
    rel = {k: 100.0 * miss[k] * ratio[(n, k)] for k in kept}
    kmax = max(rel, key=rel.get)
    tau_over = sorted(set(round(ratio[(n, k)], 12) for k in kept))
    print("%s: %d kept couplings (%s ... %s); tau/|O_GS| = %s" % (name, len(kept), kept[0], kept[-1], tau_over))
    print("   max miss of the exact 19-site m_s over the kept couplings: %.4f tau (max_over_kept stored: %.4f) at Jz = %s"
          % (miss[kmax], f["classical_n19"]["max_over_kept"], kmax))
    print("   = %.3f %% of the reference value" % rel[kmax])
    worst = max(worst, rel[kmax])
print("largest over the three cases: %.3f %% ; rounded up to one decimal: %.1f %%" % (worst, math.ceil(worst * 10) / 10))
