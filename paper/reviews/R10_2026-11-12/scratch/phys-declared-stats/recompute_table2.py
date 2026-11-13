"""R10 reviewer phys-declared-stats: independent recomputation of Table II (main.tex 766-787) and of the ratios quoted in
Sec. V, from the per-instance outputs of final_tests (read in place, nothing written outside this folder).

Path 1 (raw): labels from b/emu_*.json, truth from b/ref_*.json (labels320), clusters from b/patch_*.json, DMRG chi=32
              from b/ref_*.json['low'].  No file written by the run's own analysis is used.
Path 2 (model files): per-label predictions of the learned models (reg, stack, q_top, q_kry, ...) from b/model_*.json;
              these cannot be rebuilt without re-training, so their per-label arrays are taken as stored.
The two paths are compared wherever both exist.
"""
import json
import os

import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
OUT = ROOT + "/phase3/full_runs/final_tests/out_20261106T120830Z/out"
HERE = os.path.dirname(os.path.abspath(__file__))
JZ = ("1.6", "2.5")
NI = 6
NE = 64


def rj(*p):
    with open(os.path.join(*p)) as f:
        return json.load(f)


res = {}
for J in JZ:
    S = rj(OUT, "b", "model_J%s_site.json" % J)
    B = rj(OUT, "b", "model_J%s_bond.json" % J)
    per = {}       # estimator -> list over instances of mean miss over 121 labels
    per_site = {}
    per_bond = {}
    per_raw = {}
    meta = []
    maxdiff = {}
    for i in range(NI):
        ref = rj(OUT, "b", "ref_J%s_%d.json" % (J, i))
        emu = rj(OUT, "b", "emu_J%s_%d.json" % (J, i))
        pat = rj(OUT, "b", "patch_J%s_%d.json" % (J, i))
        tZ = np.array(ref["labels320"]["Z"])
        tC = np.array(ref["labels320"]["Czz"][:NE])
        assert len(tZ) == 57 and len(tC) == 64
        tauZ = 0.06 * np.abs(tZ).mean()
        tauC = 0.06 * np.abs(tC).mean()

        def miss(z, c):
            return float(np.r_[np.abs(np.array(z) - tZ) / tauZ, np.abs(np.array(c) - tC) / tauC].mean())
        raw = dict(label=miss(emu["labels"]["Z"], emu["labels"]["Czz"][:NE]),
                   open19=miss(pat["p19"]["Z_open"], pat["p19"]["C_open"]),
                   emb19=miss(pat["p19"]["Z_emb"], pat["p19"]["C_emb"]),
                   open13=miss(pat["p13"]["Z_open"], pat["p13"]["C_open"]),
                   emb13=miss(pat["p13"]["Z_emb"], pat["p13"]["C_emb"]),
                   dmrg32=miss(ref["low"]["32"]["labels"]["Z"], ref["low"]["32"]["labels"]["Czz"][:NE]),
                   dmrg64=miss(ref["low"]["64"]["labels"]["Z"], ref["low"]["64"]["labels"]["Czz"][:NE]),
                   truth200=miss(ref["labels200"]["Z"], ref["labels200"]["Czz"][:NE]))
        for k, v in raw.items():
            per_raw.setdefault(k, []).append(v)
        # path 2: model files (site labels stored as eta*Z; |difference| and mean|truth| do not depend on eta)
        s, b = S["test"][i], B["test"][i]
        assert s["i"] == i and b["i"] == i
        ts, tb = np.array(s["truth"]), np.array(b["truth"])
        maxdiff.setdefault("truth_site_abs", []).append(float(np.abs(np.abs(ts) - np.abs(tZ)).max()))
        maxdiff.setdefault("truth_bond", []).append(float(np.abs(tb - tC).max()))
        tZ2, tC2 = 0.06 * np.abs(ts).mean(), 0.06 * np.abs(tb).mean()
        for k in ("label", "reg", "open13", "emb13", "open19", "emb19", "stack", "q_top", "q_top_noref", "q_kry",
                  "q_kry_noref"):
            ms_ = np.abs(np.array(s[k]) - ts) / tZ2
            mb_ = np.abs(np.array(b[k]) - tb) / tC2
            per.setdefault(k, []).append(float(np.r_[ms_, mb_].mean()))
            per_site.setdefault(k, []).append(float(ms_.mean()))
            per_bond.setdefault(k, []).append(float(mb_.mean()))
        m32 = float(np.r_[np.abs(np.array(s["low"]["32"]) - ts) / tZ2, np.abs(np.array(b["low"]["32"]) - tb) / tC2].mean())
        per.setdefault("dmrg32", []).append(m32)
        meta.append(dict(i=i, de=(emu["E"] - ref["E320"]) / 57, E_label=emu["E"], E320=ref["E320"], E200=ref["E200"],
                         secs_emu=emu["secs"], secs_patch=pat["secs"], secs_ref=ref["secs"],
                         t32=ref["low"]["32"]["time_s"], t64=ref["low"]["64"]["time_s"], D=emu["stats"]["D"],
                         min_abs_truth_site=float(np.abs(tZ).min()), min_abs_truth_bond=float(np.abs(tC).min()),
                         n_sites_wrong_sign=int((np.sign(ts) < 0).sum())))
    res[J] = dict(per=per, per_site=per_site, per_bond=per_bond, per_raw=per_raw, meta=meta,
                  maxdiff={k: max(v) for k, v in maxdiff.items()})

TABLE = [("Label as generated", "label"), ("Label with correction (primary)", "q_top"),
         ("Same, trained on first stage at n=19", "q_kry"), ("Regression on local couplings", "reg"),
         ("Open cluster, 19 sites", "open19"), ("Embedded cluster, 13 sites", "emb13"),
         ("Embedded cluster, 19 sites (best)", "emb19"), ("DMRG on target, chi=32", "dmrg32")]
PRINTED = {"label": ("3.30", "0.87"), "q_top": ("0.74", "0.21"), "q_kry": ("0.43", "0.20"), "reg": ("0.92", "0.24"),
           "open19": ("0.92", "0.16"), "emb13": ("0.16", "0.025"), "emb19": ("0.082", "0.010"),
           "dmrg32": ("0.051", "0.004")}

lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


P("== Table II recomputed (mean over six instances of the mean miss over 121 labels; units 0.06*mean|truth| per type) ==")
ok_all = True
for name, k in TABLE:
    row = []
    for jj, J in enumerate(JZ):
        a = np.array(res[J]["per"][k])
        m = a.mean()
        pr = PRINTED[k][jj]
        nd = len(pr.split(".")[1])
        ok = (("%." + str(nd) + "f") % m) == pr
        ok_all &= ok
        row.append((m, pr, a.min(), a.max(), a.std(ddof=1), ok))
    P("%-38s | Jz=1.6 %9.5f printed %6s [%7.4f, %7.4f] sd %.4f %s | Jz=2.5 %9.5f printed %6s [%7.4f, %7.4f] sd %.4f %s" % (
        name, row[0][0], row[0][1], row[0][2], row[0][3], row[0][4], "OK" if row[0][5] else "MISMATCH",
        row[1][0], row[1][1], row[1][2], row[1][3], row[1][4], "OK" if row[1][5] else "MISMATCH"))
P("all 16 printed numbers reproduce at printed precision:", ok_all)

P("")
P("== path 1 (raw emu/ref/patch files) against path 2 (model files), max |difference of per-instance mean miss| ==")
for J in JZ:
    for k in ("label", "open19", "emb19", "open13", "emb13", "dmrg32"):
        d = np.abs(np.array(res[J]["per_raw"][k]) - np.array(res[J]["per"][k])).max()
        P("Jz", J, k, "%.3e" % d)
    P("Jz", J, "truth stored in model files vs labels320 of ref files:", res[J]["maxdiff"])
    P("Jz", J, "gate G-B1: max over instances of mean |chi200 - chi320|/tau =", "%.3e" % max(res[J]["per_raw"]["truth200"]),
      "(limit 0.1)")
    P("Jz", J, "dmrg64 mean miss %.5f" % np.mean(res[J]["per_raw"]["dmrg64"]))

P("")
P("== best classical (declared: smallest mean miss among reg, open13, emb13, open19, emb19, stack) ==")
for J in JZ:
    means = {k: float(np.mean(res[J]["per"][k])) for k in ("reg", "open13", "emb13", "open19", "emb19", "stack")}
    best = min(means, key=means.get)
    P("Jz", J, {k: round(v, 4) for k, v in means.items()}, "best:", best)

P("")
P("== ratios quoted in the text ==")
rng = np.random.default_rng(20261112)
NB = 20000


def boot_ratio(a, b):
    a, b = np.array(a), np.array(b)
    ix = rng.integers(0, len(a), (NB, len(a)))
    r = a[ix].mean(1) / b[ix].mean(1)
    return np.percentile(r, [2.5, 97.5])


for J in JZ:
    p = res[J]["per"]
    e19 = np.array(p["emb19"])
    for q in ("q_top", "q_kry", "q_top_noref", "q_kry_noref"):
        a = np.array(p[q])
        r = a.mean() / e19.mean()
        lo, hi = boot_ratio(a, e19)
        pi = a / e19
        P("Jz %s  %-12s / emb19: ratio of means %.3f  (declared 'improvement' 1-ratio = %.4f)  per-instance ratios %s  min %.2f max %.2f  bootstrap95 over instances [%.2f, %.2f]  wins %d/6" % (
            J, q, r, 1 - r, np.round(pi, 2).tolist(), pi.min(), pi.max(), lo, hi, int((a < e19).sum())))
    a, l = np.array(p["q_top"]), np.array(p["label"])
    P("Jz %s  label / q_top: ratio of means %.3f  per-instance %s" % (J, l.mean() / a.mean(), np.round(l / a, 2).tolist()))
    a2 = np.array(p["q_kry"])
    P("Jz %s  label / q_kry: ratio of means %.3f  per-instance %s" % (J, l.mean() / a2.mean(), np.round(l / a2, 2).tolist()))
    d32 = np.array(p["dmrg32"])
    P("Jz %s  dmrg32 vs emb19: means %.4f vs %.4f; dmrg32 better in %d/6 instances; per-instance dmrg32 %s emb19 %s" % (
        J, d32.mean(), e19.mean(), int((d32 < e19).sum()), np.round(d32, 4).tolist(), np.round(e19, 4).tolist()))
    for k in ("q_top", "emb19", "reg", "label"):
        P("Jz %s  %-6s sites %.4f bonds %.4f" % (J, k, np.mean(res[J]["per_site"][k]), np.mean(res[J]["per_bond"][k])))

P("")
P("== gain over the regression on the same local couplings (post hoc; text: 19 %, 14 %; 53 %, 19 %) ==")


def boot_gain(a, b):
    a, b = np.array(a), np.array(b)
    ix = rng.integers(0, len(a), (NB, len(a)))
    g = 100 * (1 - a[ix].mean(1) / b[ix].mean(1))
    return np.percentile(g, [2.5, 97.5]), float((g <= 0).mean())


for J in JZ:
    p = res[J]["per"]
    reg = np.array(p["reg"])
    for q in ("q_top", "q_kry", "q_top_noref", "q_kry_noref"):
        a = np.array(p[q])
        g = 100 * (1 - a.mean() / reg.mean())
        (lo, hi), pneg = boot_gain(a, reg)
        gi = 100 * (1 - a / reg)
        P("Jz %s  %-12s vs reg: gain %.2f %%  per-instance gains %s  (min %.1f, max %.1f)  wins %d/6  bootstrap95 [%.1f, %.1f]  P(boot gain<=0)=%.4f" % (
            J, q, g, np.round(gi, 1).tolist(), gi.min(), gi.max(), int((a < reg).sum()), lo, hi, pneg))
    for c in ("open19", "open13", "stack", "emb13"):
        a, b = np.array(p["q_top"]), np.array(p[c])
        P("Jz %s  q_top vs %-7s: means %.4f vs %.4f  q_top wins %d/6" % (J, c, a.mean(), b.mean(), int((a < b).sum())))
        a = np.array(p["q_kry"])
        P("Jz %s  q_kry vs %-7s: means %.4f vs %.4f  q_kry wins %d/6" % (J, c, a.mean(), b.mean(), int((a < b).sum())))

P("")
P("== energy error per site of the generated labels, and recorded times ==")
for J in JZ:
    m = res[J]["meta"]
    de = [x["de"] for x in m]
    P("Jz", J, "de min %.5f max %.5f" % (min(de), max(de)), "| emulation s %.1f-%.1f (min %.2f-%.2f)" % (
        min(x["secs_emu"] for x in m), max(x["secs_emu"] for x in m), min(x["secs_emu"] for x in m) / 60,
        max(x["secs_emu"] for x in m) / 60),
      "| clusters s %.1f-%.1f" % (min(x["secs_patch"] for x in m), max(x["secs_patch"] for x in m)),
      "| dmrg32 s %.2f-%.2f | dmrg64 s %.2f-%.2f" % (min(x["t32"] for x in m), max(x["t32"] for x in m),
                                                     min(x["t64"] for x in m), max(x["t64"] for x in m)),
      "| min |truth| site %.3f bond %.3f" % (min(x["min_abs_truth_site"] for x in m), min(x["min_abs_truth_bond"] for x in m)))

json.dump(res, open(os.path.join(HERE, "recompute_table2_out.json"), "w"), indent=1)
open(os.path.join(HERE, "recompute_table2_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
