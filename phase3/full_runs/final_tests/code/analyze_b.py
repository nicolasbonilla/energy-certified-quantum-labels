"""Test B analysis (DECLARATION.md section 4). Reads fetched JSON only; seconds.
usage: python analyze_b.py <fetched out dir> <output json>"""
import json
import os
import sys

import numpy as np

OUT, RES = sys.argv[1:3]
JZ = (1.6, 2.5)
CLASSICAL = ("reg", "open13", "emb13", "open19", "emb19", "stack")
QUANTUM = ("q_top", "q_top_noref", "q_kry", "q_kry_noref")
ALL = CLASSICAL + QUANTUM + ("label", "truth200")


def rj(*p):
    return json.load(open(os.path.join(*p)))


R = dict(Jz={})
for Jz in JZ:
    S = rj(OUT, "b", "model_J%.1f_site.json" % Jz)
    B = rj(OUT, "b", "model_J%.1f_bond.json" % Jz)
    per = {k: [] for k in ALL}
    per_site = {k: [] for k in ALL}
    per_bond = {k: [] for k in ALL}
    per_rel = {k: [] for k in ALL}
    low = {"32": [], "64": []}
    meta = []
    for s, b in zip(S["test"], B["test"]):
        ts, tb = np.array(s["truth"]), np.array(b["truth"])
        tauZ, tauC = 0.06 * np.abs(ts).mean(), 0.06 * np.abs(tb).mean()
        for k in ALL:
            ms = np.abs(np.array(s[k]) - ts) / tauZ
            mb = np.abs(np.array(b[k]) - tb) / tauC
            per[k].append(float(np.r_[ms, mb].mean()))
            per_site[k].append(float(ms.mean()))
            per_bond[k].append(float(mb.mean()))
            per_rel[k].append(float(np.r_[np.abs(np.array(s[k]) - ts) / (0.06 * np.abs(ts)),
                                          np.abs(np.array(b[k]) - tb) / (0.06 * np.abs(tb))].mean()))
        for c in low:
            low[c].append(float(np.r_[np.abs(np.array(s["low"][c]) - ts) / tauZ, np.abs(np.array(b["low"][c]) - tb) / tauC].mean()))
        meta.append(dict(i=s["i"], de=s["de"], de_noref=s["de_noref"], E0=s["E0"], E0_patch=s["E0_patch"], E0_reg=b.get("E0_reg"),
                         tauZ=tauZ, tauC=tauC, min_abs_truth=float(min(np.abs(ts).min(), np.abs(tb).min()))))
    mean = {k: float(np.mean(v)) for k, v in per.items()}
    best = min(CLASSICAL, key=lambda k: mean[k])
    row = dict(per_instance=per, per_instance_site=per_site, per_instance_bond=per_bond, mean=mean, best_classical=best, meta=meta,
               mean_per_label_tol={k: float(np.mean(v)) for k, v in per_rel.items()},
               best_classical_per_label_tol=min(CLASSICAL, key=lambda k: float(np.mean(per_rel[k]))),
               low_chi=low, low_chi_mean={c: float(np.mean(v)) for c, v in low.items()},
               gate_truth=dict(max_mean_change=max(per["truth200"]), limit=0.1, passed=bool(max(per["truth200"]) <= 0.1)))
    rng = np.random.default_rng(1)
    for q in QUANTUM:
        d = np.array(per[best]) - np.array(per[q])
        imp = 1.0 - mean[q] / mean[best]
        wins = int((d > 0).sum())
        boots = []
        for _ in range(4000):
            ix = rng.integers(0, len(d), len(d))
            boots.append(1.0 - np.mean(np.array(per[q])[ix]) / np.mean(np.array(per[best])[ix]))
        row[q] = dict(improvement=imp, wins=wins, n=len(d), passes=bool(imp >= 0.25 and wins >= 5),
                      boot_low=float(np.percentile(boots, 2.5)), boot_high=float(np.percentile(boots, 97.5)))
    R["Jz"][str(Jz)] = row
R["verdict"] = {str(j): R["Jz"][str(j)]["q_top"]["passes"] for j in JZ}
R["verdict"]["general"] = all(R["verdict"][str(j)] for j in JZ)
R["verdict"]["secondary_q_kry"] = {str(j): R["Jz"][str(j)]["q_kry"]["passes"] for j in JZ}
R["verdict"]["noref_q_top"] = {str(j): R["Jz"][str(j)]["q_top_noref"]["passes"] for j in JZ}
json.dump(R, open(RES, "w"), indent=1)
for j in JZ:
    r = R["Jz"][str(j)]
    print("Jz", j, "best classical", r["best_classical"], {k: round(v, 3) for k, v in r["mean"].items()}, "low chi", r["low_chi_mean"])
    print("  per instance best classical", [round(x, 3) for x in r["per_instance"][r["best_classical"]]])
    print("  per instance q_top         ", [round(x, 3) for x in r["per_instance"]["q_top"]])
    for q in QUANTUM:
        print("  ", q, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in r[q].items()})
    print("  gate", r["gate_truth"], "de", [round(m["de"], 5) for m in r["meta"]])
print(json.dumps(R["verdict"]))
