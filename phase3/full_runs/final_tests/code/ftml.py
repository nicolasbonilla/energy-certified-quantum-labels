"""Final tests, Test B: regressors (numpy only). Same machinery for every learned model, classical or quantum side.

Candidates: ridge on all quadratic monomials of the standardized inputs ('poly2'), and ridge on linear terms plus M = 1500
random Fourier features of Gaussian kernels of length ell ('rff'; equivalent to kernel ridge regression at this size).
Model and penalty are chosen by 4-fold cross-validation over training INSTANCES (mean absolute error), on at most 240
instances; the final fit uses all training rows. Test instances are never seen here.
"""
import numpy as np

ALPHAS = [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
ELLS = [2.0, 4.0, 8.0]
M_RFF = 1500
CHUNK = 20000
CV_GROUPS = 240


class Std:
    def __init__(self, X):
        self.mu = X.mean(0)
        sd = X.std(0)
        sd[sd < 1e-12] = 1.0
        self.sd = sd

    def __call__(self, X):
        return (X - self.mu) / self.sd


def design(Xs, spec):
    N, d = Xs.shape
    if spec[0] == "poly2":
        iu, ju = np.triu_indices(d)
        return np.hstack([np.ones((N, 1)), Xs, Xs[:, iu] * Xs[:, ju]])
    _, ell, W, b = spec
    return np.hstack([np.ones((N, 1)), Xs, np.sqrt(2.0 / W.shape[1]) * np.cos(Xs @ W / ell + b)])


def gram(Xs, y, spec):
    A = None
    for s in range(0, len(Xs), CHUNK):
        P = design(Xs[s:s + CHUNK], spec)
        if A is None:
            A = np.zeros((P.shape[1], P.shape[1]))
            c = np.zeros(P.shape[1])
        A += P.T @ P
        c += P.T @ y[s:s + CHUNK]
    return A, c


def solve(A, c, alpha):
    p = A.shape[0]
    s = alpha * np.trace(A) / p
    return np.linalg.solve(A + s * np.eye(p), c)


def predict(Xs, spec, w):
    out = np.empty(len(Xs))
    for s in range(0, len(Xs), CHUNK):
        out[s:s + CHUNK] = design(Xs[s:s + CHUNK], spec) @ w
    return out


class Model:
    """fit(X, y, groups): y is predicted as offset-free regression on X. Stores the cross-validation record."""

    def __init__(self, seed):
        self.seed = seed

    def fit(self, X, y, groups):
        rng = np.random.default_rng(self.seed)
        self.st = Std(X)
        Xs = self.st(X)
        self.ybar = float(y.mean())
        yc = y - self.ybar
        d = Xs.shape[1]
        specs = [("poly2",)]
        W = rng.standard_normal((d, M_RFF))
        b = rng.uniform(0, 2 * np.pi, M_RFF)
        for ell in ELLS:
            specs.append(("rff", ell, W, b))
        ug = rng.permutation(np.unique(groups))
        sel = ug[:CV_GROUPS]
        fold_of = {gg: i % 4 for i, gg in enumerate(sel)}
        mask = np.isin(groups, sel)
        fo = np.array([fold_of[gg] for gg in groups[mask]])
        Xc, yv = Xs[mask], yc[mask]
        rec = []
        best = None
        for spec in specs:
            parts = [gram(Xc[fo == f], yv[fo == f], spec) for f in range(4)]
            A = sum(p[0] for p in parts)
            c = sum(p[1] for p in parts)
            for a in ALPHAS:
                err = 0.0
                for f in range(4):
                    w = solve(A - parts[f][0], c - parts[f][1], a)
                    err += float(np.abs(predict(Xc[fo == f], spec, w) - yv[fo == f]).sum())
                err /= len(yv)
                rec.append(dict(kind=spec[0], ell=(spec[1] if spec[0] == "rff" else None), alpha=a, cv_mae=err))
                if best is None or err < best[0]:
                    best = (err, spec, a)
        self.cv = rec
        self.best = dict(cv_mae=best[0], kind=best[1][0], ell=(best[1][1] if best[1][0] == "rff" else None), alpha=best[2],
                         n_rows=int(len(y)), n_groups=int(len(ug)), n_cv_groups=int(len(sel)))
        self.spec = best[1]
        A, c = gram(Xs, yc, self.spec)
        self.w = solve(A, c, best[2])
        self.best["train_mae"] = float(np.abs(predict(Xs, self.spec, self.w) - yc).mean())
        return self

    def predict(self, X):
        return predict(self.st(X), self.spec, self.w) + self.ybar
