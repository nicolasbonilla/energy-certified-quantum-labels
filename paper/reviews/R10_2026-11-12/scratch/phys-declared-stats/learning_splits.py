"""R10 reviewer phys-declared-stats: spread of the benchmark coverage numbers (main.tex 918-932) over the 200 splits and
over the 100 instances.  The stored analysis keeps only values pooled over splits; this driver re-runs the split loop
for the standard (SC) and energy-calibrated (CSC) split-conformal intervals and keeps per-split and per-instance counts.

It imports the run's own label loader and kernel learners read-only (labels_l.py, models_l.py: deterministic, no random
numbers in the fits) and uses the declared split seeds; the conformal step is written here independently.  The pooled
means are compared with the stored learn_<model>_D_O.json as a check of the re-execution.
usage: python -B learning_splits.py M1|M2
"""
import json
import math
import os
import sys
import time

import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
LR = ROOT + "/phase3/full_runs/learning"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, LR + "/code")
import labels_l as LB  # noqa: E402
import models_l as ML  # noqa: E402

MODEL = sys.argv[1]
R = 200
ALPHA = 0.10
N_TR, N_CA, N_TE = 60, 20, 20
SEED_SPLIT = 20261103
LABELSETS = ["exact", "gen1", "gen5", "advL1", "advL5", "advM1", "advM5"]
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    lines.append(s)


def qhat(scores):
    m = scores.shape[0]
    k = int(math.ceil((m + 1) * (1.0 - ALPHA) - 1e-12))
    assert k <= m
    return np.sort(scores, axis=0)[k - 1]


t0 = time.time()
recs = LB.load_all(LR + "/out_20261031T152732Z/out", ["D", "O"])
rD = recs["D"]
common = set(rD[0]["labels"])
for r in rD + recs["O"]:
    common &= set(r["labels"])
labels = [l for l in LB.AVERAGES if l in common] + sorted([l for l in common if l not in LB.AVERAGES],
                                                          key=lambda s: tuple(int(x) for x in s.split("_")[1:]))
L = rD[0]["L"]
cls = np.array([LB.label_class(l, L) for l in labels])
keep = np.isin(cls, ["avg", "nn", "diag"])
labels = [l for l, k in zip(labels, keep) if k]
cls = cls[keep]
m = len(labels)
nD = len(rD)
assert nD == 100 and m == 58, (nD, m)
X = np.array([r["J"] for r in rD])
cols = [(ls, j) for ls in LABELSETS for j in range(m)]
ncol = len(cols)
Y, LO, HI, TR = (np.zeros((nD, ncol)) for _ in range(4))
for a, rec in enumerate(rD):
    for c, (ls, j) in enumerate(cols):
        r = rec["labels"][labels[j]]
        TR[a, c] = r["exact"]
        if ls == "exact":
            Y[a, c] = LO[a, c] = HI[a, c] = r["exact"]
            continue
        de = 1e-3 if ls.endswith("1") else 5e-3
        if ls.startswith("gen"):
            Y[a, c] = r["gen"][de]
            LO[a, c], HI[a, c] = r["cert_gen"][de]
        else:
            Y[a, c] = r["adv"]["less" if ls.startswith("advL") else "more"][de]
            LO[a, c], HI[a, c] = r["cert_adv"][de]
col_ls = np.array([ls for ls, _ in cols])
col_j = np.array([j for _, j in cols])
P("containment of every label and true value in its interval: label %s, truth %s" % (
    bool(((Y >= LO - 1e-12) & (Y <= HI + 1e-12)).all()), bool(((TR >= LO - 1e-12) & (TR <= HI + 1e-12)).all())))
if MODEL == "M1":
    b, cb = ML.bank_m1(X)
    groups_k = [(b, cb, np.arange(ncol))]
else:
    groups_k = []
    for j, lab in enumerate(labels):
        b, cb = ML.bank_m2(X, lab, L)
        groups_k.append((b, cb, np.where(col_j == j)[0]))
P("banks ready %.0fs" % (time.time() - t0))
METH = ("SC", "CSC")
covT = {k: np.zeros((R, ncol)) for k in METH}       # per split, per column: fraction of the 20 test instances covered
covO = {k: np.zeros((R, ncol)) for k in METH}
wid = {k: np.zeros((R, ncol)) for k in METH}
hitT = {k: np.zeros((nD, ncol)) for k in METH}      # per instance: times covered when in the test set
cnt = np.zeros(nD)
for r_ in range(R):
    rng = np.random.default_rng(SEED_SPLIT + r_)
    perm = rng.permutation(nD)
    tr, ca, te = perm[:N_TR], perm[N_TR:N_TR + N_CA], perm[N_TR + N_CA:]
    q = np.concatenate([ca, te])
    f = np.zeros((len(q), ncol))
    for bank, combos, cc in groups_k:
        Ytr = Y[tr][:, cc]
        best, _ = ML.cv_select(bank, combos, tr, Ytr)
        W = ML.weights(bank, combos, tr, q, needed=set(best.tolist()))
        for bi in set(best.tolist()):
            sub = cc[best == bi]
            f[:, sub] = W[bi] @ Y[tr][:, sub]
    fca, fte = f[:N_CA], f[N_CA:]
    sc = {"SC": np.abs(Y[ca] - fca), "CSC": np.maximum(np.abs(fca - LO[ca]), np.abs(fca - HI[ca]))}
    for k in METH:
        qq = qhat(sc[k])
        okT = np.abs(TR[te] - fte) <= qq[None, :]
        okO = np.abs(Y[te] - fte) <= qq[None, :]
        covT[k][r_] = okT.mean(0)
        covO[k][r_] = okO.mean(0)
        wid[k][r_] = 2 * qq
        hitT[k][te] += okT
    cnt[te] += 1
    if (r_ + 1) % 50 == 0:
        P("split %d/%d %.0fs" % (r_ + 1, R, time.time() - t0))

stored = json.load(open(LR + "/analysis/learn_%s_D_O.json" % MODEL))
rngb = np.random.default_rng(12345)
out = {}
P("")
P("model %s: truth coverage in distribution, nominal 0.90 (expected value of exact split conformal 19/21 = 0.9048)" % MODEL)
P("%-6s %-4s %-4s | pooled (stored)  | sd over 200 splits | 2.5-97.5 %% of splits | splits below 0.90 | bootstrap over the 100 instances, 95 %%" % ("set", "meth", "cls"))
for ls in LABELSETS:
    cl = np.where(col_ls == ls)[0]
    for k in METH:
        for g in ("avg", "nn", "diag"):
            cg = cl[cls == g]
            per_split = covT[k][:, cg].mean(1)
            pooled = float(per_split.mean())
            st = stored["coverage"][ls][k][g]["covT_id"]
            # instance bootstrap: coverage = sum_i hits_i / sum_i (count_i * n_labels)
            h = hitT[k][:, cg].sum(1)
            n_ = cnt * len(cg)
            ix = rngb.integers(0, nD, (4000, nD))
            bs = h[ix].sum(1) / n_[ix].sum(1)
            lo_, hi_ = np.percentile(bs, [2.5, 97.5])
            out["%s|%s|%s" % (ls, k, g)] = dict(pooled=pooled, stored=st, sd_splits=float(per_split.std(ddof=1)),
                                               p025=float(np.percentile(per_split, 2.5)), p975=float(np.percentile(per_split, 97.5)),
                                               frac_below_090=float((per_split < 0.90).mean()), boot_inst=[float(lo_), float(hi_)],
                                               width_mean=float(wid[k][:, cg].mean()), own=float(covO[k][:, cg].mean()))
            P("%-6s %-4s %-4s | %.4f (%.4f) | %.4f | [%.3f, %.3f] | %.2f | [%.3f, %.3f]%s" % (
                ls, k, g, pooled, st, per_split.std(ddof=1), np.percentile(per_split, 2.5), np.percentile(per_split, 97.5),
                (per_split < 0.90).mean(), lo_, hi_, "" if abs(pooled - st) < 1e-9 else "   <-- differs from stored by %.2e" % (pooled - st)))
mx = max(abs(v["pooled"] - v["stored"]) for v in out.values())
P("largest |pooled - stored| over all cells: %.2e" % mx)
P("every instance was a test instance between %d and %d times (mean %.1f)" % (cnt.min(), cnt.max(), cnt.mean()))
json.dump(out, open(os.path.join(HERE, "learning_splits_%s_out.json" % MODEL), "w"), indent=1)
open(os.path.join(HERE, "learning_splits_%s_out.txt" % MODEL), "w", encoding="utf8").write("\n".join(lines) + "\n")
P("done %.0fs" % (time.time() - t0))
