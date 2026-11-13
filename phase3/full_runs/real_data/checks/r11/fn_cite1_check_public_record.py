"""check_public_record.py -- cite-1 (R11, 2026-11-13). Reads ONLY the project's converted plain-JSON copies of the
public record (phase3/full_runs/real_data/converted/real_n{57,115}.json; no pickle, nothing executed) and prints the
quantities that sentences of the manuscript attribute to Ref. [jaderberg2026] (its figures) or to the public record
[jaderberg2026data]:
  A. mean unsigned relative site-magnetization error, Eq. (15) of the dataset paper's Supplement (its Supp. Fig. 11),
     at Jz = 1.1 ... 1.5, both sizes;
  B. energy error over the gap, (E - E0)/(E1 - E0), final and before the last step (its Fig. 2 and Supp. Fig. 9);
  C. energy error per site before and after the last step at Jz = 1.6, and the factor by which the step lowers it;
  D. sum of the published site magnetizations minus the sector value M0 (9 at n = 57, 19 at n = 115).
  python -B -I check_public_record.py > check_public_record_out.txt
"""
import json
import os
import statistics
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
CONV = os.path.join(ROOT, "phase3/full_runs/real_data/converted")
M0 = {57: 9, 115: 19}


def load(n):
    return json.load(open(os.path.join(CONV, "real_n%d.json" % n), encoding="utf-8"))


for n in (57, 115):
    d = load(n)
    rf, dm = d["skqd_random_flip"], d["dmrg"]
    keys = sorted(rf.keys(), key=float)
    print("=" * 96)
    print("n = %d ; couplings in skqd_random_flip: %d (%s ... %s); in dmrg: %d" % (n, len(keys), keys[0], keys[-1], len(dm)))
    print("fields of one dataset file:", sorted(k for k in rf[keys[0]].keys() if not k.startswith("_")))

    print("\nA. mean_i |Z_data - Z_dmrg| / |Z_dmrg|  (percent; in brackets the paper's literal Eq. 15 with a signed denominator)")
    for k in keys:
        if float(k) > 1.55:
            continue
        z, zr = rf[k]["z_basis_opt"], dm[k]["z"]
        assert len(z) == n and len(zr) == n
        rel = [abs(a - b) / abs(b) for a, b in zip(z, zr)]
        rel_signed = [abs(a - b) / b for a, b in zip(z, zr)]
        print("   Jz = %s : %6.2f %%   [%7.2f %%]   (std of the per-site values %5.2f)" % (
            k, 100 * statistics.fmean(rel), 100 * statistics.fmean(rel_signed), 100 * statistics.pstdev(rel)))

    print("\nB. energy error over the gap: final (final_global_energy) | before the last step (ground_state_energy)")
    for k in ("1.6", "1.8", "2.1", "2.5", "4.0"):
        e0, e1 = dm[k]["ground_state_energy"], dm[k]["e1"]
        ef, eb = rf[k]["final_global_energy"], rf[k]["ground_state_energy"]
        print("   Jz = %s : final %.4f | before %.4f | gap %.5f" % (k, (ef - e0) / (e1 - e0), (eb - e0) / (e1 - e0), e1 - e0))
    below = [k for k in keys if (rf[k]["final_global_energy"] - dm[k]["ground_state_energy"]) < (dm[k]["e1"] - dm[k]["ground_state_energy"])]
    print("   smallest Jz from which the final error stays below the gap for all larger Jz:", end=" ")
    last_bad = max([float(k) for k in keys if k not in below], default=None)
    print("last coupling with error >= gap: %s" % last_bad)
    nb = [k for k in keys if (rf[k]["ground_state_energy"] - dm[k]["ground_state_energy"]) < (dm[k]["e1"] - dm[k]["ground_state_energy"])]
    print("   couplings at which the energy BEFORE the last step is below the gap: %d of %d" % (len(nb), len(keys)))

    print("\nC. energy error per site before / after the last step, and their ratio")
    fac = []
    for k in keys:
        e0 = dm[k]["ground_state_energy"]
        de_b = (rf[k]["ground_state_energy"] - e0) / n
        de_a = (rf[k]["final_global_energy"] - e0) / n
        fac.append(de_b / de_a)
        if k in ("1.6",):
            print("   Jz = %s : before %.5f | after %.5f | factor %.3f" % (k, de_b, de_a, de_b / de_a))
    print("   factor over the %d couplings: min %.3f | median %.3f | max %.3f" % (len(fac), min(fac), statistics.median(fac), max(fac)))
    ft = [f for k, f in zip(keys, fac) if float(k) >= 1.55]
    print("   factor over the 45 training couplings only: min %.3f | median %.3f | max %.3f" % (min(ft), statistics.median(ft), max(ft)))

    print("\nD. sum of the published site magnetizations minus M0 = %d" % M0[n])
    dev = [sum(rf[k]["z_basis_opt"]) - M0[n] for k in keys]
    print("   negative at %d of %d couplings ; min %.5f ; max %.5f" % (sum(1 for v in dev if v < 0), len(dev), min(dev), max(dev)))


# ---- E, F: added after the first run (same inputs) -------------------------------------------------------------
def czz_err(rf_k, dm_k):
    a, pa = rf_k["2_nn_corr_funcs_zz_basis_opt"], rf_k["2_nn_corr_pairs_zz_basis_opt"]
    mp = {tuple(sorted(p)): v for p, v in zip(dm_k["2_nn_corr_pairs"], dm_k["2_nn_corr_funcs_zz"])}
    b = [mp[tuple(sorted(p))] for p in pa]
    return 100 * statistics.fmean(abs(x - y) / abs(y) for x, y in zip(a, b))


def loop_err(rf_k, dm_k):
    mp = {tuple(sorted(s)): v for s, v in zip(dm_k["z_loop_sites"], dm_k["z_loop"])}
    b = [mp[tuple(sorted(s))] for s in rf_k["z_loop_sites"]]
    return 100 * statistics.fmean(abs(x - y) / abs(y) for x, y in zip(rf_k["z_loop"], b))


print("=" * 96)
print("E. mean relative error of the pair correlations (first and second neighbours) and of the loops, percent")
print("   (validation of the definition: the dataset paper's text gives the medians over the phase, 1.36 % and 1.22 %")
print("    for C_zz and 1.57 % and 1.27 % for the loops, at n = 57 and 115)")
for n in (57, 115):
    d = load(n)
    rf, dm = d["skqd_random_flip"], d["dmrg"]
    train = [k for k in sorted(rf.keys(), key=float) if float(k) >= 1.55]
    cz = {k: czz_err(rf[k], dm[k]) for k in train}
    lp = {k: loop_err(rf[k], dm[k]) for k in train}
    print("   n = %3d : median over the 45 training couplings: C_zz %.2f %% | loops %.2f %%" % (
        n, statistics.median(cz.values()), statistics.median(lp.values())))
    print("             C_zz at Jz = 2.5: %.2f %% ; at Jz = 4.0: %.2f %%" % (cz["2.5"], cz["4.0"]))

print("\nF. energy error over the gap before the last step at Jz = 2.5, both variants of the record")
for n in (57, 115):
    d = load(n)
    dm = d["dmrg"]["2.5"]
    e0, e1 = dm["ground_state_energy"], dm["e1"]
    print("   n = %3d : random flip %.4f | post-selection %.4f" % (
        n, (d["skqd_random_flip"]["2.5"]["ground_state_energy"] - e0) / (e1 - e0),
        (d["skqd_post_select"]["2.5"]["ground_state_energy"] - e0) / (e1 - e0)))

# ---- G: the range quoted in main.tex:217 (added for the replacement sentence of finding cite-1-01) ----------------
print("\nG. mean unsigned relative site error at Jz = 1.1, 1.2, 1.3 (Supp. Fig. 11 of the dataset paper, left panel)")
vals = {}
for n in (57, 115):
    d = load(n)
    rf, dm = d["skqd_random_flip"], d["dmrg"]
    vals[n] = [100 * statistics.fmean(abs(a - b) / abs(b) for a, b in zip(rf[k]["z_basis_opt"], dm[k]["z"]))
               for k in ("1.1", "1.2", "1.3")]
    print("   n = %3d : %s percent" % (n, ", ".join("%.2f" % v for v in vals[n])))
lo = min(min(v) for v in vals.values())
hi = max(max(v) for v in vals.values())
import math
print("   over both sizes: min %.2f, max %.2f percent; rounded outward: %d-%d percent" % (lo, hi, math.floor(lo), math.ceil(hi)))
print("   at n = 57 alone: %.2f to %.2f percent, rounded outward %d-%d percent (the range '20-32' of main.tex:217 fits this size only)"
      % (min(vals[57]), max(vals[57]), math.floor(min(vals[57])), math.ceil(max(vals[57]))))

# ---- H: medians over all 50 couplings (the side remark of the report on the pair correlations) ---------------------
print("\nH. median over all 50 couplings of the mean relative error of the pair correlations (paper: 1.36 % and 1.22 %)")
for n in (57, 115):
    d = load(n)
    rf, dm = d["skqd_random_flip"], d["dmrg"]
    ks = sorted(rf.keys(), key=float)
    print("   n = %3d : %.2f %%" % (n, statistics.median(czz_err(rf[k], dm[k]) for k in ks)))
