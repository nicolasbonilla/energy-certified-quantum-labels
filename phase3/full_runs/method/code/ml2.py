"""Learning test of the full method runs (DECLARATION §5): per-site <Z_i> regressors trained on Jz in [1.6, 6.0] on
(L) the emulated `primary` labels ("same-method") and (T) DMRG labels; OOD test at Jz = 1.1-1.4; two null models; an
abstaining rule at J* = 3.3; an ensemble-spread abstention baseline.

  python ml2.py <root> [n ...]      -> <root>/out/ml/ml_n<n>.json and stdout summary
"""
import glob
import json
import os
import sys
import numpy as np

TRAIN_MIN = 1.6
OOD = [1.1, 1.2, 1.3, 1.4]
JSTAR = 3.3
HERE = os.path.dirname(os.path.abspath(__file__))


def rj(p):
    with open(p) as f:
        return json.load(f)


def load(root, n):
    ref, lab = {}, {}
    for p in glob.glob(os.path.join(root, "out", "ref", "ref_n%d_J*.json" % n)):
        r = rj(p); ref[round(r["Jz"], 1)] = np.array(r["labels"]["Z"])
    for p in glob.glob(os.path.join(root, "out", "emu", "emu_n%d_J*.json" % n)):
        r = rj(p); lab[round(r["Jz"], 1)] = np.array(r["var"]["primary"]["labels"]["Z"])
    return ref, lab


# ------------------------------------------------------------------------------------------------- models
def fit_poly(J, Y, deg=3, ridge=1e-8):
    u = 1.0 / np.asarray(J)
    X = np.vander(u, deg + 1)
    W = np.linalg.solve(X.T @ X + ridge * np.eye(deg + 1), X.T @ Y)
    return lambda Jq: np.vander(1.0 / np.atleast_1d(Jq), deg + 1) @ W


def fit_mlp(J, Y, seeds=5, hidden=32, epochs=6000, lr=3e-3):
    """pilot3's small tanh MLP (1 -> h -> h -> n_out), full-batch Adam on standardized data, seed ensemble."""
    J = np.asarray(J, float)[:, None]
    mu, sd = J.mean(), J.std()
    x = (J - mu) / sd
    ym, ys = Y.mean(axis=0), Y.std(axis=0) + 1e-9
    y = (Y - ym) / ys
    models = []
    for s in range(seeds):
        rng = np.random.default_rng(1000 + s)
        P = [rng.normal(0, 1.0, (1, hidden)), np.zeros(hidden), rng.normal(0, 1 / np.sqrt(hidden), (hidden, hidden)),
             np.zeros(hidden), rng.normal(0, 1 / np.sqrt(hidden), (hidden, Y.shape[1])), np.zeros(Y.shape[1])]
        m = [np.zeros_like(p) for p in P]; v = [np.zeros_like(p) for p in P]
        for t in range(1, epochs + 1):
            h1 = np.tanh(x @ P[0] + P[1]); h2 = np.tanh(h1 @ P[2] + P[3]); out = h2 @ P[4] + P[5]
            d = 2 * (out - y) / y.size
            g5 = d.sum(0); g4 = h2.T @ d
            d2 = (d @ P[4].T) * (1 - h2 ** 2)
            g3 = d2.sum(0); g2 = h1.T @ d2
            d1 = (d2 @ P[2].T) * (1 - h1 ** 2)
            g1 = d1.sum(0); g0 = x.T @ d1
            G = [g0, g1, g2, g3, g4, g5]
            for i in range(6):
                m[i] = 0.9 * m[i] + 0.1 * G[i]; v[i] = 0.999 * v[i] + 0.001 * G[i] ** 2
                P[i] -= lr * (m[i] / (1 - 0.9 ** t)) / (np.sqrt(v[i] / (1 - 0.999 ** t)) + 1e-8)
        models.append([p.copy() for p in P])

    def pred(Jq):
        xq = (np.atleast_1d(np.asarray(Jq, float))[:, None] - mu) / sd
        outs = []
        for P in models:
            h1 = np.tanh(xq @ P[0] + P[1]); h2 = np.tanh(h1 @ P[2] + P[3]); outs.append(h2 @ P[4] + P[5])
        return np.mean(outs, axis=0) * ys + ym
    return pred


def _bmm(A, B, ta=False, tb=False):
    """Per-site 2D matmuls (numpy's stacked matmul is ~20x slower here). A, B stacked over the first axis."""
    S = A.shape[0]
    out = None
    for k in range(S):
        a = A[k].T if ta else A[k]
        b = B[k].T if tb else B[k]
        r = a @ b
        if out is None:
            out = np.empty((S,) + r.shape, dtype=r.dtype)
        out[k] = r
    return out


def fit_ibm(J, Y, n_in, seeds=3, width=256, depth=5, lr=1e-3, epochs=300, batch=32):
    """'IBM-like' architecture 1 (2606.15983 Supp. IV.1.1, Table 2): one MLP per observable, input (Jz, ..., Jz) of
    length n_in, `depth` hidden tanh layers of `width`, linear output, MSE, Adam(lr), `epochs` epochs, batch `batch`.
    Unstated, chosen here: raw inputs and targets, Glorot-normal weights, zero biases, float32 arithmetic. All S per-site
    networks are trained together as a stack (disjoint parameters, per-parameter Adam: identical to separate training)."""
    J = np.asarray(J, float); N, S = Y.shape
    X = np.repeat(J[:, None], n_in, axis=1).astype(np.float32)
    Y = np.asarray(Y, np.float32)
    ens = []
    for s in range(seeds):
        rng = np.random.default_rng(2000 + s)
        dims = [n_in] + [width] * depth + [1]
        W = [rng.normal(0, np.sqrt(2.0 / (dims[i] + dims[i + 1])), (S, dims[i], dims[i + 1])).astype(np.float32)
             for i in range(len(dims) - 1)]
        b = [np.zeros((S, 1, dims[i + 1]), np.float32) for i in range(len(dims) - 1)]
        P = W + b
        m = [np.zeros_like(p) for p in P]; v = [np.zeros_like(p) for p in P]
        t = 0
        for ep in range(epochs):
            order = rng.permutation(N)
            for st in range(0, N, batch):
                idx = order[st:st + batch]
                x0 = np.ascontiguousarray(np.broadcast_to(X[idx][None], (S, len(idx), n_in)))
                h = [x0]
                for i in range(depth):
                    h.append(np.tanh(_bmm(h[-1], W[i]) + b[i]))
                out = (_bmm(h[-1], W[depth]) + b[depth])[:, :, 0]          # (S, B)
                d = 2 * (out - Y[idx].T) / len(idx)                         # per-site MSE gradient
                gW = [None] * (depth + 1); gb = [None] * (depth + 1)
                delta = d[:, :, None]
                for i in range(depth, -1, -1):
                    gW[i] = _bmm(h[i], delta, ta=True)
                    gb[i] = delta.sum(axis=1, keepdims=True)
                    if i > 0:
                        delta = _bmm(delta, W[i], tb=True) * (1 - h[i] ** 2)
                G = gW + gb
                t += 1
                c1 = lr / (1 - 0.9 ** t); c2 = 1.0 / np.sqrt(1 - 0.999 ** t)
                for k in range(len(P)):          # Adam, in place (same arithmetic as the textbook form)
                    m[k] *= 0.9; m[k] += 0.1 * G[k]
                    v[k] *= 0.999; np.multiply(G[k], G[k], out=G[k]); G[k] *= 0.001; v[k] += G[k]
                    np.sqrt(v[k], out=G[k]); G[k] *= c2; G[k] += 1e-8
                    np.divide(m[k], G[k], out=G[k]); G[k] *= c1; P[k] -= G[k]
        ens.append(([p.copy() for p in P[:depth + 1]], [p.copy() for p in P[depth + 1:]]))

    def pred(Jq, members=False):
        Jq = np.atleast_1d(np.asarray(Jq, float))
        Xq = np.repeat(Jq[:, None], n_in, axis=1).astype(np.float32)
        outs = []
        for Wm, bm in ens:
            h = np.ascontiguousarray(np.broadcast_to(Xq[None], (S, len(Jq), n_in)))
            for i in range(depth):
                h = np.tanh(_bmm(h, Wm[i]) + bm[i])
            outs.append((_bmm(h, Wm[depth]) + bm[depth])[:, :, 0].T)
        outs = np.array(outs, dtype=float)
        return outs if members else outs.mean(axis=0)
    return pred


def fit_const(J, Y):
    mu = Y.mean(axis=0)
    return lambda Jq: np.repeat(mu[None], len(np.atleast_1d(Jq)), axis=0)


def fit_nn(J, Y):
    J = np.asarray(J, float)
    return lambda Jq: np.array([Y[int(np.argmin(np.abs(J - q)))] for q in np.atleast_1d(Jq)])


def ms(Z, eta):
    return Z @ eta / len(eta)


def main(root, ns=None):
    out_all = {}
    for n in (ns or [57, 115]):
        n = int(n)
        G = json.load(open(os.path.join(HERE, "graphs", "hh_d%d.json" % {57: 5, 115: 7}[n])))
        eta = np.array(G["eta"], float); n_in = len(G["edges"])
        ref, lab = load(root, n)
        common = sorted(set(ref) & set(lab))
        tr = [j for j in common if j >= TRAIN_MIN]
        od = [j for j in common if j in OOD]
        if len(tr) < 4 or not od:
            continue
        res = dict(n=n, train=tr, ood=od, Jstar=JSTAR, models={})
        fits = dict(poly3_invJ=fit_poly, mlp_pilot3=fit_mlp, ibm_arch1=lambda J, Y: fit_ibm(J, Y, n_in),
                    null_const=fit_const, null_nn=fit_nn)
        preds = {}
        for mname, fit in fits.items():
            fL = fit(tr, np.array([lab[j] for j in tr]))
            fT = fit(tr, np.array([ref[j] for j in tr]))
            preds[mname] = (fL, fT)
            rows = []
            for j in od:
                pL, pT = fL(j)[0], fT(j)[0]
                mt, ml = ms(ref[j], eta), ms(lab[j], eta)
                mpL, mpT = ms(pL, eta), ms(pT, eta)
                rows.append(dict(Jz=j, m_s_truth=mt, m_s_labels=ml, m_s_pred_labels=mpL, m_s_pred_dmrg=mpT,
                                 err_vs_samemethod_pct=abs(mpL - ml) / ml * 100,
                                 err_vs_dmrg_pct=abs(mpL - mt) / mt * 100,
                                 err_dmrgtrained_vs_dmrg_pct=abs(mpT - mt) / mt * 100,
                                 dZ_vs_samemethod_pct=float(np.mean(np.abs(pL - lab[j]) / np.abs(lab[j])) * 100),
                                 dZ_vs_dmrg_pct=float(np.mean(np.abs(pL - ref[j]) / np.abs(ref[j])) * 100)))
            fitq = float(np.max([abs(ms(fL(j)[0], eta) - ms(lab[j], eta)) for j in tr]))
            res["models"][mname] = dict(rows=rows, max_train_fit_err_m_s=fitq)
            r12 = [r for r in rows if abs(r["Jz"] - 1.2) < 1e-9]
            if r12:
                print("n=%d %-12s Jz=1.2: vs same-method %.2f%%  vs DMRG %.2f%%" % (
                    n, mname, r12[0]["err_vs_samemethod_pct"], r12[0]["err_vs_dmrg_pct"]), flush=True)
        # declared readings at Jz = 1.2
        def row12(m):
            r = [x for x in res["models"][m]["rows"] if abs(x["Jz"] - 1.2) < 1e-9]
            return r[0] if r else None
        blind = [m for m in ("mlp_pilot3", "ibm_arch1") if row12(m) and row12(m)["err_vs_samemethod_pct"] < 3
                 and row12(m)["err_vs_dmrg_pct"] > 9]
        nn12 = row12("null_nn")
        res["readings"] = dict(same_method_test_blind=bool(blind), blind_models=blind,
                               test_uninformative=bool(nn12 and nn12["err_vs_samemethod_pct"] < 3))
        # abstention: union grid, leave-one-out for training points
        grid = sorted(set(tr) | set(od))
        ab = {}
        for mname in ("poly3_invJ", "mlp_pilot3", "ibm_arch1"):
            fit = fits[mname]
            rows = []
            for q in grid:
                insample = False
                if q not in tr:                       # OOD query: the model trained on all training points
                    f = preds[mname][0]
                elif mname == "ibm_arch1":            # cost: in-sample (flagged) for the IBM-like model
                    f = preds[mname][0]; insample = True
                else:                                 # training point: leave-one-out
                    trq = [j for j in tr if abs(j - q) > 1e-9]
                    f = fit(trq, np.array([lab[j] for j in trq]))
                mp = ms(f(q)[0], eta); mt = ms(ref[q], eta)
                rows.append(dict(Jz=q, err_vs_dmrg_pct=abs(mp - mt) / mt * 100, answered=q >= JSTAR,
                                 in_sample=insample))
            ans = [r for r in rows if r["answered"]]
            ab[mname] = dict(rows=rows, coverage=len(ans) / len(rows),
                             max_err_answered=max((r["err_vs_dmrg_pct"] for r in ans), default=None),
                             mean_err_answered=float(np.mean([r["err_vs_dmrg_pct"] for r in ans])) if ans else None,
                             max_err_all=max(r["err_vs_dmrg_pct"] for r in rows),
                             mean_err_all=float(np.mean([r["err_vs_dmrg_pct"] for r in rows])))
        cert = [j for j in tr if j >= JSTAR]
        if len(cert) >= 3:
            f = fit_poly(cert, np.array([lab[j] for j in cert]), deg=min(3, len(cert) - 1))
            ab["certified_only_poly"] = dict(train=cert, rows=[dict(Jz=q, err_vs_dmrg_pct=abs(ms(f(q)[0], eta) - ms(ref[q], eta)) /
                                                                   ms(ref[q], eta) * 100, answered=q >= JSTAR) for q in grid])
        # spread-based abstention (IBM-like ensemble)
        fL = preds["ibm_arch1"][0]                 # the label-trained IBM-like ensemble of the main test
        mem = fL(grid, members=True)                       # (seeds, len(grid), S)
        spread = np.array([np.std([ms(mem[s, i], eta) for s in range(mem.shape[0])]) for i in range(len(grid))])
        tau = 3 * max(spread[i] for i, q in enumerate(grid) if q in tr)
        ab["ensemble_spread"] = dict(tau=float(tau), rows=[dict(Jz=q, spread=float(spread[i]), abstains=bool(spread[i] > tau))
                                                          for i, q in enumerate(grid)])
        res["abstention"] = ab
        out_all[n] = res
        os.makedirs(os.path.join(root, "out", "ml"), exist_ok=True)
        with open(os.path.join(root, "out", "ml", "ml_n%d.json" % n), "w") as f:
            json.dump(res, f, indent=1)
        print("n=%d readings %s; abstention J*: %s; spread abstains at OOD: %s" % (
            n, res["readings"], {k: (v.get("coverage"), v.get("max_err_answered")) for k, v in ab.items() if "coverage" in v},
            [r["Jz"] for r in ab["ensemble_spread"]["rows"] if r["abstains"]]), flush=True)
    return out_all


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or None)
