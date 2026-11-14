"""combine_b.py -- a model that combines the generated label with embedded clusters (disordered lattices, test B).

    python -B combine_b.py <Jz> <site|bond> <top|kry>      Jz = 1.6 or 2.5; top = primary estimate, kry = secondary

POST HOC, not part of the declared test: computed on 2026-11-12, after the outcome of the declared test was known, by
the study paper/reviews/R10_2026-11-12/scratch/phys-declared-stats/combine_b.py; this file is that script with the
paths made relative to the package (nothing else changed). The stored training rows allow one such combination at no
new physics cost: the declared classical "stack" (regression of truth - emb13 on local couplings and the 13-site
clusters) with the generated label and its energy error added as inputs. Same regressor (ftml.Model, declared grid
and cross-validation), same 600 training instances at n = 19, no n = 57 truth in training. Compared per test instance
with the stored "stack" and with the best classical estimate (19-site embedded cluster). A 19-site cluster cannot
enter the training (the training systems have 19 sites).
Reads only; writes combine_b_J<Jz>_<type>_<family>_out.txt and .json next to this script. One to five minutes per case.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..")).replace(os.sep, "/")
FT = ROOT + "/phase3/full_runs/final_tests"
OUT = FT + "/out_20261106T120830Z/out"
sys.dont_write_bytecode = True
sys.path.insert(0, FT + "/code")
import ftlib as fl  # noqa: E402
import ftml  # noqa: E402

Jz = float(sys.argv[1])
typ = sys.argv[2]
fam = sys.argv[3]
js = fl.js
B_NTRAIN, B_CHUNK, B_NTEST = 600, 25, 6
t0 = time.time()
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    lines.append(s)


def rj(p):
    with open(p) as f:
        return json.load(f)


feats = fl.site_features if typ == "site" else fl.bond_features
key = "Z" if typ == "site" else "C"
pk = "Z_" if typ == "site" else "C_"


def qcols(lab, de):
    d = np.full(len(lab), float(de))
    s = np.sqrt(np.maximum(d, 0.0))
    return np.column_stack([lab, s, d, lab * s, lab * d])


Xs, ys, gs = [], [], []
for c in range(B_NTRAIN // B_CHUNK):
    for r in rj(OUT + "/b/train_J%s_c%03d.json" % (js(Jz), c))["rows"]:
        inst = fl.train_instance(Jz, r["idx"])
        F = feats(inst)
        s = inst["eta"].astype(float) if typ == "site" else np.ones(len(inst["edges"]))
        y = s * np.array(r[key])
        o13 = s * np.array(r["patch13"][pk + "open"])
        e13 = s * np.array(r["patch13"][pk + "emb"])
        lev = r[fam]
        if len(lev) > 8:
            lev = [lev[int(q)] for q in np.round(np.linspace(0, len(lev) - 1, 8))]
        for v in lev:
            lab = s * np.array(v[key])
            Xs.append(np.column_stack([F, o13, e13, qcols(lab, v["de"])]))
            ys.append(y - e13)
            gs.append(np.full(len(y), r["idx"]))
X, y, g = np.vstack(Xs), np.concatenate(ys), np.concatenate(gs)
P("combination model, family %s: %d training rows, %d columns, %.0fs" % (fam, len(y), X.shape[1], time.time() - t0))
mdl = ftml.Model(fl.seed("R10", "combine", js(Jz), typ, fam)).fit(X, y, g)
P("selected %s  %.0fs" % ({k: mdl.best[k] for k in ("kind", "ell", "alpha", "cv_mae", "train_mae")}, time.time() - t0))
STO = rj(OUT + "/b/model_J%s_%s.json" % (js(Jz), typ))
P("stored stack model for comparison: %s" % {k: STO["fits"]["stack"]["best"][k] for k in ("kind", "ell", "alpha", "cv_mae")})
res = dict(Jz=Jz, typ=typ, fam=fam, best=mdl.best, rows=[])
for i in range(B_NTEST):
    inst = fl.test_instance(Jz, i)
    ref = rj(OUT + "/b/ref_J%s_%d.json" % (js(Jz), i))
    emu = rj(OUT + "/b/emu_J%s_%d.json" % (js(Jz), i))
    pat = rj(OUT + "/b/patch_J%s_%d.json" % (js(Jz), i))
    F = feats(inst)
    ne = len(inst["edges"])
    s = inst["eta"].astype(float) if typ == "site" else np.ones(ne)
    kk = "Czz" if key == "C" else "Z"
    truth = s * np.array(ref["labels320"][kk][:ne] if key == "C" else ref["labels320"][kk])
    gen = s * np.array(emu["labels"][kk][:ne] if key == "C" else emu["labels"][kk])
    o13, e13 = s * np.array(pat["p13"][pk + "open"]), s * np.array(pat["p13"][pk + "emb"])
    e19 = s * np.array(pat["p19"][pk + "emb"])
    de = (emu["E"] - ref["E320"]) / inst["n"]
    tau = 0.06 * np.abs(truth).mean()
    comb = e13 + mdl.predict(np.column_stack([F, o13, e13, qcols(gen, de)]))
    m = lambda a: float(np.mean(np.abs(np.asarray(a) - truth) / tau))
    row = dict(i=i, combined=m(comb), stack=m(STO["test"][i]["stack"]), emb13=m(e13), emb19=m(e19), q=m(STO["test"][i]["q_" + fam]),
               label=m(gen), pred=comb.tolist())
    res["rows"].append(row)
    P("instance %d: label+13-site clusters %.4f | stored stack (no label) %.4f | emb13 %.4f | emb19 (best classical) %.4f | q_%s %.4f" % (
        i, row["combined"], row["stack"], row["emb13"], row["emb19"], fam, row["q"]))
a = np.array([r["combined"] for r in res["rows"]])
b = np.array([r["stack"] for r in res["rows"]])
e = np.array([r["emb19"] for r in res["rows"]])
P("mean miss (this type): combined %.4f, stack %.4f (change %+.1f %%; combined better in %d of 6), emb19 %.4f (combined better in %d of 6)" % (
    a.mean(), b.mean(), 100 * (a.mean() / b.mean() - 1), int((a < b).sum()), e.mean(), int((a < e).sum())))
tag = "combine_b_J%s_%s_%s" % (js(Jz), typ, fam)
json.dump(res, open(os.path.join(HERE, tag + "_out.json"), "w"))
open(os.path.join(HERE, tag + "_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
P("done %.0fs" % (time.time() - t0))
