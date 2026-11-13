"""Learners (laptop). Both are kernel ridge regressions, hence linear in the training labels: f(x) = sum_i a_i(x) y_i.

M1 = the benchmark's model class, arXiv:2106.12627 (official notebook github.com/hsinyuan-huang/provable-ml-quantum,
     Code.ipynb, cells 3-4; read as text, never run). Faithful numpy reimplementation of its KernelRidge branch:
  * Dirichlet features: for every coupling x_k and k1 = -2..2 the feature cos(pi k1 x_k) (5 per coupling, in that
    order), each instance's feature vector normalized to unit length; linear kernel;
  * Gaussian kernel: the coupling vector normalized to unit length (the notebook normalizes Xfull in place), sklearn's
    rbf kernel with gamma = 1 / n_features;
  * KernelRidge(alpha = 1 / (2 C)), C in {0.0125, 0.025, 0.05, 0.125, 0.25, 0.5, 1, 2}; no intercept;
  * model selection by 5-fold cross-validation (contiguous folds, no shuffle, as sklearn's cross_val_score) on the
    mean fold RMSE of the training labels; first minimum kept (the notebook's strict '>'); here over both kernels
    together (Dirichlet first). Omitted: the SVR branch (not linear in the labels) and the neural tangent kernels.
M2 = a geometrically local learner of the type of Lewis et al. (Nat. Commun. 15, 895 (2024)): the label is modelled
     as a sum of functions of the couplings near each of its terms. Kernel limit of their random Fourier features
     (Gaussian kernel on the raw local couplings) with ridge instead of their l1 penalty (to stay linear in the
     labels): K_l(x, x') = (1/|T_l|) sum_{p in T_l} exp(-gamma_p |x_N(p) - x'_N(p)|^2), T_l = the pairs of label l
     (one pair for a pair label; all nn bonds for Cnn; all diagonal pairs for Cd2; all pairs for Cstag), N(p) = the
     bonds with an endpoint within lattice (Manhattan) distance delta of a site of p, gamma_p = c / |N(p)|.
     Grid: delta in {0, 1}, c in {0.25, 1, 4}, alpha in {1e-3, 1e-2, 1e-1, 1}; the same 5-fold selection.
"""
import numpy as np

import lattice as LT

C_GRID = [0.0125, 0.025, 0.05, 0.125, 0.25, 0.5, 1.0, 2.0]
ALPHAS_M1 = [1.0 / (2.0 * c) for c in C_GRID]
M2_DELTA = [0, 1]
M2_C = [0.25, 1.0, 4.0]
ALPHAS_M2 = [1e-3, 1e-2, 1e-1, 1.0]


def dirichlet_features(X):
    X = np.asarray(X, float)
    cols = []
    for k in range(X.shape[1]):
        for k1 in range(-2, 3):
            cols.append(np.cos(np.pi * k1 * X[:, k]))
    F = np.stack(cols, axis=1)
    return F / np.linalg.norm(F, axis=1, keepdims=True)


def _rbf(Z, gamma):
    sq = (Z * Z).sum(1)
    D2 = np.maximum(sq[:, None] + sq[None, :] - 2.0 * Z @ Z.T, 0.0)
    return np.exp(-gamma * D2)


def bank_m1(X):
    """M1 kernel bank {name: Gram matrix} and its combos [(name, alpha)] in selection order."""
    F = dirichlet_features(X)
    Xn = np.asarray(X, float)
    Xn = Xn / np.linalg.norm(Xn, axis=1, keepdims=True)
    bank = {"dir": F @ F.T, "rbf": _rbf(Xn, 1.0 / Xn.shape[1])}
    combos = [(kk, a) for kk in ("dir", "rbf") for a in ALPHAS_M1]
    return bank, combos


def label_terms(label, L):
    n = L * LT.W
    if label == "Cnn":
        return LT.bonds(L)
    if label == "Cd2":
        return LT.diag_pairs(L)
    if label == "Cstag":
        return [(i, j) for i in range(n) for j in range(i + 1, n)]
    _, a, b = label.split("_")
    return [(int(a), int(b))]


def neighbourhood(p, delta, L):
    def d(a, b):
        ax, ay = divmod(a, LT.W)
        bx, by = divmod(b, LT.W)
        return abs(ax - bx) + abs(ay - by)
    return [t for t, (u, v) in enumerate(LT.bonds(L)) if min(d(w, s) for s in p for w in (u, v)) <= delta]


def bank_m2(X, label, L):
    X = np.asarray(X, float)
    T = label_terms(label, L)
    bank = {}
    for delta in M2_DELTA:
        nb = [neighbourhood(p, delta, L) for p in T]
        for c in M2_C:
            K = np.zeros((len(X), len(X)))
            for idx in nb:
                K += _rbf(X[:, idx], c / len(idx))
            bank["d%d_c%g" % (delta, c)] = K / len(T)
    combos = [(kk, a) for kk in bank for a in ALPHAS_M2]
    return bank, combos


def kfold(nn, k=5):
    """sklearn KFold(n_splits=k, shuffle=False) index sets."""
    sizes = np.full(k, nn // k, dtype=int)
    sizes[: nn % k] += 1
    out, start = [], 0
    for s in sizes:
        va = np.arange(start, start + s)
        tr = np.concatenate([np.arange(0, start), np.arange(start + s, nn)])
        out.append((tr, va))
        start += s
    return out


def _names(combos):
    seen = []
    for kk, _ in combos:
        if kk not in seen:
            seen.append(kk)
    return seen


def cv_select(bank, combos, tr, Y):
    """Y: (len(tr), m). Returns (best combo index per column, cv scores (n_combos, m))."""
    m = Y.shape[1]
    scores = np.zeros((len(combos), m))
    for a, b in kfold(len(tr)):
        ta, va = tr[a], tr[b]
        for kk in _names(combos):
            lam, U = np.linalg.eigh(bank[kk][np.ix_(ta, ta)])
            Kva = bank[kk][np.ix_(va, ta)] @ U
            UY = U.T @ Y[a]
            for ci, (k2, al) in enumerate(combos):
                if k2 != kk:
                    continue
                P = Kva @ (UY / (lam + al)[:, None])
                scores[ci] += np.sqrt(np.mean((P - Y[b]) ** 2, axis=0))
    scores /= 5.0
    best = np.zeros(m, dtype=int)
    for j in range(m):                      # first minimum (strict improvement), in combos order
        bj, bs = 0, scores[0, j]
        for c in range(1, len(combos)):
            if bs > scores[c, j]:
                bj, bs = c, scores[c, j]
        best[j] = bj
    return best, scores


def weights(bank, combos, tr, q, needed=None):
    """{combo index: A (len(q), len(tr))} with f(q) = A @ y_tr (only the combos in `needed`, default all)."""
    needed = set(range(len(combos))) if needed is None else set(needed)
    out = {}
    for kk in _names(combos):
        cis = [ci for ci, (k2, _) in enumerate(combos) if k2 == kk and ci in needed]
        if not cis:
            continue
        lam, U = np.linalg.eigh(bank[kk][np.ix_(tr, tr)])
        KqU = bank[kk][np.ix_(q, tr)] @ U
        for ci in cis:
            out[ci] = (KqU / (lam + combos[ci][1])[None, :]) @ U.T
    return out


def bootstrap_preds(bank, combos, tr, q, Y, best, B, seed):
    """Bootstrap ensemble (resample the training instances) with each column's selected combo: (B, len(q), m)."""
    rng = np.random.default_rng(seed)
    m = Y.shape[1]
    P = np.zeros((B, len(q), m))
    for b in range(B):
        sel = rng.integers(0, len(tr), size=len(tr))
        idx = tr[sel]
        Yb = Y[sel]
        for kk in _names(combos):
            cols = [j for j in range(m) if combos[best[j]][0] == kk]
            if not cols:
                continue
            lam, U = np.linalg.eigh(bank[kk][np.ix_(idx, idx)])
            KqU = bank[kk][np.ix_(q, idx)] @ U
            for ci in sorted(set(best[cols].tolist())):
                cj = [j for j in cols if best[j] == ci]
                P[b][:, cj] = KqU @ ((U.T @ Yb[:, cj]) / (lam + combos[ci][1])[:, None])
    return P
