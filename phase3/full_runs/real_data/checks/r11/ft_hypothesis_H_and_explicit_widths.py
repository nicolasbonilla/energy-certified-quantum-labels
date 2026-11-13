# R11 fix pass (fixer FT, 2026-11-13): copy of paper/reviews/R11_2026-11-13/scratch/hostile-A/b2_extra.py;
# only the path of the data folder was adapted. Output: ft_hypothesis_H_and_explicit_widths_out.txt (next to this file).
# hostile-A / b2_extra.py -- (1) explicit-state width against exact width near the lowest certified coupling;
# (2) further necessary conditions of hypothesis H from the public files: positivity of every published two-site
#     distribution (edges and second neighbours); (3) the published label inside every exact interval (own recount).
import json, math
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")).replace("\\", "/")   # phase3/full_runs/real_data (path adapted from the reader's copy; nothing else changed)
rows = json.load(open(ROOT + "/e1/map_e1/map_rows.json"))["rows"]
print("(1) m_s: explicit-state width (lower) against exact width, in tau")
for n, js in ((57, (3.1, 3.2, 3.3, 3.4, 3.5, 3.6)), (115, (3.0, 3.1, 3.3, 3.4, 3.6, 3.9, 4.0))):
    for J in js:
        r = [x for x in rows if x["n"] == n and x["label"] == "m_s" and abs(x["Jz"] - J) < 1e-9][0]
        lw = (r.get("lower") or {}).get("w_lower_over_tau")
        ex = r["exact"]; e1 = r.get("exact_e1") or {}
        wex = (ex["hi"] - ex["lo"]) / r["tau"] if ex.get("exists") else None
        we1 = (e1["hi"] - e1["lo"]) / r["tau"] if e1.get("exists") else None
        print("   n=%d Jz=%.1f status=%-15s status_e1=%-15s explicit %.4f | exact primary %s | exact with E1 %s | sector-like outer %.4f inner %.4f" % (
            n, J, r["status"], r.get("status_e1"), lw if lw is not None else float("nan"),
            "%.4f" % wex if wex else "-", "%.4f" % we1 if we1 else "-",
            r["like"]["w_out_over_tau"] if r["like"].get("w_out_over_tau") is not None else float("nan"),
            r["like"]["w_in_over_tau"] if r["like"].get("w_in_over_tau") is not None else float("nan")))
print("\n(2) two-site distributions of the published labels")
for n in (57, 115):
    D = json.load(open(ROOT + "/converted/real_n%d.json" % n))["skqd_random_flip"]
    worst = (1.0, None); npairs = 0
    for k in sorted(D, key=float):
        z = D[k]["z_basis_opt"]
        for (i, j), v in zip(D[k]["2_nn_corr_pairs_zz_basis_opt"], D[k]["2_nn_corr_funcs_zz_basis_opt"]):
            ps = [(1 + a * z[i] + b * z[j] + a * b * v) / 4 for a in (1, -1) for b in (1, -1)]
            npairs += 1
            if min(ps) < worst[0]:
                worst = (min(ps), (k, i, j))
        assert all(abs(x) <= 1 for x in z) and all(abs(x) <= 1 for x in D[k]["z_loop"])
    print("   n=%d: %d published pairs (edges and second neighbours, 50 couplings): smallest two-site probability %.3e at %s" % (n, npairs, worst[0], worst[1]))
print("\n(3) published label inside the exact interval, reference inside")
for tag in ("exact", "exact_e1"):
    c = [0, 0, 0]
    for r in rows:
        e = r.get(tag) or {}
        if r["label"] in ("m_s", "Czz_bar") and e.get("exists"):
            c[0] += 1; c[1] += e["lo"] <= r["label_real"] <= e["hi"]; c[2] += e["lo"] <= r["O_GS"] <= e["hi"]
    print("   %-9s rows with an interval %d ; label inside %d ; reference inside %d" % (tag, *c))
