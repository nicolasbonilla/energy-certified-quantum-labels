"""Learning analysis of the run (laptop; light work: small kernel models on precomputed labels).

  python learn_l.py <out_dir> <id_set> <ood_set> <result_dir> <model M1|M2> [R] [classes]
<out_dir>/inst/ holds the per-instance JSONs of task_l.py. <id_set> (the benchmark's instances) is split R times at
random into 60 training / 20 calibration / 20 test instances; <ood_set> (the declared held-out region) is a test set
for every split (training and calibration always come from <id_set>).

Label sets: exact (i); gen1, gen5 (ii, delta e = 1e-3, 5e-3); advL1, advL5, advM1, advM5 (iii, toward less / more
order). Methods: conf_l.py. Truth = exact labels. Columns = (label set, label).
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import labels_l as LB  # noqa: E402
import models_l as ML  # noqa: E402
import conf_l as CF  # noqa: E402

ALPHA = 0.10
N_TR, N_CA, N_TE = 60, 20, 20
B_ENS = 20
SEED_SPLIT = 20261103
TAUS = [0.08, 0.04]
METHODS = ["SC", "NC", "ENS", "CSC", "CNC", "CB", "BAND"]
LABELSETS = ["exact", "gen1", "gen5", "advL1", "advL5", "advM1", "advM5"]
ABST_SETS = ["gen1", "gen5", "advL1", "advL5", "advM5"]
RANKERS = ["CB", "BAND", "CNC", "CSC", "NC", "ENS", "SC", "random", "oracle"]
RULES = ["CB", "CB_mid", "BAND", "CNC", "CSC", "NC", "SC", "ENS"]
CGRID = np.arange(1, 21) / 20.0


def tables(recs, labels):
    """Flat columns c = (label set, label): Y, LO, HI (N, ncol) and truth (N, ncol)."""
    N, m = len(recs), len(labels)
    cols = [(ls, j) for ls in LABELSETS for j in range(m)]
    Y, LO, HI, TR = (np.zeros((N, len(cols))) for _ in range(4))
    for a, rec in enumerate(recs):
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
    return cols, Y, LO, HI, TR


def curves(err, score, tau, rng):
    """Risk-coverage: answer the smallest-score fraction c of the queries (random tie-break)."""
    N = len(err)
    o = np.lexsort((rng.random(N), score))
    e = err[o]
    rm, ex = [], []
    for c in CGRID:
        k = max(1, int(round(c * N)))
        rm.append(math.sqrt(float(np.mean(e[:k] ** 2))))
        ex.append(float(np.mean(np.abs(e[:k]) > tau / 2)))
    return np.array(rm), np.array(ex)


def run(out_dir, id_set, ood_set, res_dir, model="M1", R=200, classes=("avg", "nn", "diag")):
    t0 = time.time()
    recs = LB.load_all(out_dir, [id_set, ood_set])
    rD, rO = recs[id_set], recs[ood_set]
    common = set(rD[0]["labels"])
    for r in rD + rO:
        common &= set(r["labels"])
    labels = [l for l in LB.AVERAGES if l in common] + sorted(
        [l for l in common if l not in LB.AVERAGES], key=lambda s: tuple(int(x) for x in s.split("_")[1:]))
    L = rD[0]["L"]
    cls = np.array([LB.label_class(l, L) for l in labels])
    keep = np.isin(cls, list(classes))
    labels = [l for l, k in zip(labels, keep) if k]
    cls = cls[keep]
    m = len(labels)
    allrecs = rD + rO
    nD, nO = len(rD), len(rO)
    assert nD == N_TR + N_CA + N_TE, nD
    X = np.array([r["J"] for r in allrecs])
    cols, Y, LO, HI, TRUTH = tables(allrecs, labels)
    ncol = len(cols)
    col_ls = np.array([ls for ls, _ in cols])
    col_j = np.array([j for _, j in cols])
    # kernel banks: groups of columns sharing a bank
    if model == "M1":
        b, cb = ML.bank_m1(X)
        groups_k = [(b, cb, np.arange(ncol))]
    elif model == "M2":
        groups_k = []
        for j, lab in enumerate(labels):
            b, cb = ML.bank_m2(X, lab, L)
            groups_k.append((b, cb, np.where(col_j == j)[0]))
    else:
        raise ValueError(model)
    print("banks ready %.0fs" % (time.time() - t0), flush=True)
    groups = {c: np.where(cls == c)[0] for c in ("avg", "nn", "diag") if (cls == c).any()}
    groups["all"] = np.arange(m)
    acc = {meth: {k: np.zeros(ncol) for k in ("covT_id", "covO_id", "wid_id", "covT_ood", "covO_ood", "wid_ood")}
           for meth in METHODS}
    rmse = {k: np.zeros(ncol) for k in ("id", "ood")}
    band_viol = np.zeros(ncol)
    band_n = np.zeros(ncol)
    combo_names = {}
    abst = {}
    for ls in ABST_SETS:
        for g in groups:
            for dom in ("id", "ood"):
                for tau in TAUS:
                    abst["%s|%s|%s|%g" % (ls, g, dom, tau)] = dict(
                        rm={rk: np.zeros(len(CGRID)) for rk in RANKERS}, ex={rk: np.zeros(len(CGRID)) for rk in RANKERS},
                        rule={meth: np.zeros(5) for meth in RULES})      # nq, ans, exc&ans, exc_own&ans, viol
    for r_ in range(R):
        rng = np.random.default_rng(SEED_SPLIT + r_)
        perm = rng.permutation(nD)
        tr, ca, te = perm[:N_TR], perm[N_TR:N_TR + N_CA], perm[N_TR + N_CA:]
        teO = np.arange(nD, nD + nO)
        q = np.concatenate([ca, te, teO])
        rows = dict(ca=np.arange(N_CA), te=np.arange(N_CA, N_CA + N_TE), ood=np.arange(N_CA + N_TE, len(q)))
        f, flo, fhi, fex, mu, sd = (np.zeros((len(q), ncol)) for _ in range(6))
        for bank, combos, cc in groups_k:
            Ytr = Y[tr][:, cc]
            best, _ = ML.cv_select(bank, combos, tr, Ytr)
            for c, bi in zip(cc, best):
                nm = "%s_a%g" % combos[bi]
                combo_names.setdefault(int(c), {}).setdefault(nm, 0)
                combo_names[int(c)][nm] += 1
            W = ML.weights(bank, combos, tr, q, needed=set(best.tolist()))
            for bi in set(best.tolist()):
                sub = cc[best == bi]
                A = W[bi]
                f[:, sub] = A @ Y[tr][:, sub]
                flo[:, sub], fhi[:, sub] = CF.band(A, LO[tr][:, sub], HI[tr][:, sub])
                fex[:, sub] = A @ TRUTH[tr][:, sub]
            P = ML.bootstrap_preds(bank, combos, tr, q, Ytr, best, B_ENS, SEED_SPLIT * 7 + r_)
            mu[:, cc], sd[:, cc] = P.mean(0), P.std(0, ddof=1)
        nonex = col_ls != "exact"
        band_n[nonex] += len(q)
        band_viol[nonex] += np.sum((fex[:, nonex] < flo[:, nonex] - 1e-12) | (fex[:, nonex] > fhi[:, nonex] + 1e-12),
                                   axis=0)
        s = sd + 0.1 * np.median(sd[rows["ca"]], axis=0)[None, :]
        cs = rows["ca"]
        for dom, rr, tgt in (("id", rows["te"], te), ("ood", rows["ood"], teO)):
            iv = CF.intervals(f[cs], f[rr], Y[ca], LO[ca], HI[ca], s[cs], s[rr], mu[rr], sd[rr],
                              flo[cs], fhi[cs], flo[rr], fhi[rr], ALPHA)
            yt, yo = TRUTH[tgt], Y[tgt]
            for meth, (lo_, hi_) in iv.items():
                acc[meth]["covT_" + dom] += np.mean((yt >= lo_) & (yt <= hi_), axis=0)
                acc[meth]["covO_" + dom] += np.mean((yo >= lo_) & (yo <= hi_), axis=0)
                acc[meth]["wid_" + dom] += np.mean(hi_ - lo_, axis=0)
            rmse[dom] += np.sqrt(np.mean((f[rr] - yt) ** 2, axis=0))
            err_all = f[rr] - yt
            err_mid = 0.5 * (iv["CB"][0] + iv["CB"][1]) - yt
            err_own = f[rr] - yo
            dev_ex = np.abs(f[rr] - fex[rr])                 # label-induced deviation (bounded by the band width)
            widths = {meth: iv[meth][1] - iv[meth][0] for meth in iv}
            for ls in ABST_SETS:
                cl = np.where(col_ls == ls)[0]         # columns of this label set, ordered by label index
                for g, gi in groups.items():
                    cg = cl[gi]
                    e = err_all[:, cg].ravel()
                    sc = {rk: widths[rk][:, cg].ravel() for rk in ("CB", "BAND", "CNC", "CSC", "NC", "ENS", "SC")}
                    sc["random"] = np.zeros_like(e)
                    sc["oracle"] = np.abs(e)
                    for tau in TAUS:
                        key = "%s|%s|%s|%g" % (ls, g, dom, tau)
                        for rk in RANKERS:
                            rm_, ex_ = curves(e, sc[rk], tau, rng)
                            abst[key]["rm"][rk] += rm_
                            abst[key]["ex"][rk] += ex_
                        for meth in RULES:
                            wv = widths["CB" if meth == "CB_mid" else meth][:, cg].ravel()
                            ee = err_mid[:, cg].ravel() if meth == "CB_mid" else e
                            eo = err_own[:, cg].ravel()
                            ans = wv <= tau
                            viol = (ans & (dev_ex[:, cg].ravel() > wv + 1e-12)).sum() if meth == "BAND" else 0.0
                            abst[key]["rule"][meth] += np.array([len(ee), ans.sum(), (ans & (np.abs(ee) > tau / 2)).sum(),
                                                                 (ans & (np.abs(eo) > tau / 2)).sum(), viol])
        if (r_ + 1) % 20 == 0:
            print("split %d/%d  %.0fs" % (r_ + 1, R, time.time() - t0), flush=True)
    # ---- aggregate
    res = dict(meta=dict(model=model, id_set=id_set, ood_set=ood_set, R=R, n_id=nD, n_ood=nO, labels=labels,
                         classes=cls.tolist(), alpha=ALPHA, n_tr=N_TR, n_ca=N_CA, n_te=N_TE, B_ens=B_ENS,
                         seed_split=SEED_SPLIT, taus=TAUS, time_s=time.time() - t0))
    cov = {}
    for ls in LABELSETS:
        cl = np.where(col_ls == ls)[0]
        cov[ls] = {}
        for meth in METHODS:
            cov[ls][meth] = {g: {k: float(np.mean(v[cl][gi]) / R) for k, v in acc[meth].items()}
                             for g, gi in groups.items()}
            cov[ls][meth]["per_label"] = {k: (v[cl] / R).tolist() for k, v in acc[meth].items()}
    res["coverage"] = cov
    res["model_rmse"] = {ls: {g: {dom: float(np.sqrt(np.mean((rmse[dom][np.where(col_ls == ls)[0]][gi] / R) ** 2)))
                                  for dom in ("id", "ood")} for g, gi in groups.items()} for ls in LABELSETS}
    res["model_rmse_per_label"] = {ls: {dom: (rmse[dom][np.where(col_ls == ls)[0]] / R).tolist() for dom in ("id", "ood")}
                                   for ls in LABELSETS}
    res["band_check"] = {ls: dict(checks=int(band_n[col_ls == ls].sum()), violations=int(band_viol[col_ls == ls].sum()))
                         for ls in LABELSETS}
    res["combos"] = {ls: {} for ls in LABELSETS}
    for c, d in combo_names.items():
        ls, j = cols[c]
        g = cls[j]
        for nm, k in d.items():
            res["combos"][ls].setdefault(g, {}).setdefault(nm, 0)
            res["combos"][ls][g][nm] += k
    ab = {}
    for key, v in abst.items():
        rule = {}
        for meth, st in v["rule"].items():
            nq, na, ea, eo, vi = st
            rule[meth] = dict(answer_rate=na / nq, exceed_given_answer=(ea / na) if na > 0 else None,
                              joint_exceed_and_answer=ea / nq, exceed_own_given_answer=(eo / na) if na > 0 else None,
                              n_queries=nq, band_guarantee_violations=vi)
        ab[key] = dict(rm={rk: (x / R).tolist() for rk, x in v["rm"].items()},
                       ex={rk: (x / R).tolist() for rk, x in v["ex"].items()},
                       aurc={rk: float(np.mean(x / R)) for rk, x in v["rm"].items()}, rule=rule)
    res["abstention"] = ab
    res["cgrid"] = CGRID.tolist()
    os.makedirs(res_dir, exist_ok=True)
    with open(os.path.join(res_dir, "learn_%s_%s_%s.json" % (model, id_set, ood_set)), "w") as fh:
        json.dump(res, fh, indent=1)
    print("done %.0fs" % (time.time() - t0))
    return res


if __name__ == "__main__":
    a = sys.argv
    run(a[1], a[2], a[3], a[4], a[5], int(a[6]) if len(a) > 6 else 200,
        tuple(a[7].split(",")) if len(a) > 7 else ("avg", "nn", "diag"))
