# R11 fix pass (fixer FT, 2026-11-13): copy of paper/reviews/R11_2026-11-13/scratch/hostile-A/b3_rf_notcertified.py;
# only the path of the data folder was adapted. Output: ft_not_certified_without_reference_out.txt (next to this file).
# hostile-A / b3_rf_notcertified.py -- the "not certified" side without a reference value.
# A row is not certified at tolerance 0.06 |o_GS| for ANY value of o_GS if two explicit states of the window have
# labels at least 0.06 * max|O| apart; every label of the map has |O| <= 1.  Recount from the row records.
import json, collections
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")).replace("\\", "/")   # phase3/full_runs/real_data (path adapted from the reader's copy; nothing else changed)
rows = json.load(open(ROOT + "/out/map_rows.json"))["rows"]
nc = [r for r in rows if r["status"] == "NOT_CERTIFIED"]
keep = [r for r in nc if r["lower"]["w_lower"] >= 0.06]
lost = sorted((r["n"], r["label"], r["Jz"], round(r["lower"]["w_lower"], 5), round(r["lower"]["w_lower_over_tau"], 4)) for r in nc if r["lower"]["w_lower"] < 0.06)
print("not certified with the reference tolerance: %d of %d rows" % (len(nc), len(rows)))
print("of these, two explicit states at least 0.06 apart (no reference needed, |O| <= 1): %d" % len(keep))
print("rows that would become undecided (%d):" % len(lost))
for x in lost:
    print("   n=%d %-10s Jz=%.1f  distance %.5f = %.4f tau" % x)
low = [r for r in nc if r["Jz"] <= 1.5 + 1e-9]
print("rows at Jz <= 1.5: %d of %d not certified; all at least 0.06 apart: %s; smallest distance %.4f" % (
    len(low), sum(r["Jz"] <= 1.5 + 1e-9 for r in rows), all(r["lower"]["w_lower"] >= 0.06 for r in low), min(r["lower"]["w_lower"] for r in low)))
tst = [r for r in nc if r["Jz"] <= 1.4 + 1e-9]
print("rows at the test couplings 1.1-1.4: %d not certified; smallest distance %.4f = %.2f tau" % (
    len(tst), min(r["lower"]["w_lower"] for r in tst), min(r["lower"]["w_lower_over_tau"] for r in tst)))
for n in (57, 115):
    for lab in ("m_s", "Czz_bar"):
        tr = [r for r in keep if r["n"] == n and r["label"] == lab and 1.6 - 1e-9 <= r["Jz"]]
        print("   n=%d %-8s training couplings not certified without a reference: %d (with the reference: %d)" % (
            n, lab, len(tr), sum(1 for r in nc if r["n"] == n and r["label"] == lab and r["Jz"] >= 1.6 - 1e-9)))
