"""Independent evaluator of MPS states for the Huang-benchmark run (numpy only; never imports TeNPy).

Input: raw dense tensors B_k with legs (vL, p, vR) (norm folded into B_0) and the physical S^z basis. Output: norm,
<C_ij> = <sigma_i . sigma_j>/3 for the requested pairs, the energy sum_b J_b * 3 <C_b>, and the first two moments of
the total S^z (sector variance). No canonical form is assumed: left and right environments are computed explicitly.

  python indep_eval_h.py <spec.json> <out.json> <npz> [<npz> ...]
spec.json: {"n": n, "bonds": [[i, j], ...], "J": [...], "pairs": [[i, j], ...]} (pairs evaluated in addition to the bonds)
"""
import json
import sys
import numpy as np


def ops(szb):
    szb = [float(x) for x in szb]
    u = int(np.argmax(szb)); d = int(np.argmin(szb))
    Sz = np.diag(szb)
    Sp = np.zeros((2, 2)); Sp[u, d] = 1.0
    Sm = Sp.T.copy()
    return dict(Sz=Sz, Sp=Sp, Sm=Sm, Id=np.eye(2), Sz2=Sz @ Sz)


def tl(L, A, O=None):
    """Left transfer: L'[b, b'] = sum conj(A[a, s, b]) L[a, a'] O[s, t] A[a', t, b']."""
    X = np.tensordot(L, A, axes=(1, 0))                    # (a, t, b')
    if O is not None:
        X = np.tensordot(O, X, axes=(1, 1)).transpose(1, 0, 2)   # (a, s, b')
    return np.tensordot(A.conj(), X, axes=([0, 1], [0, 1]))      # (b, b')


def tr_(R, A):
    """Right transfer (identity): R'[a, a'] = sum conj(A[a, s, b]) A[a', s, b'] R[b, b']."""
    X = np.tensordot(A, R, axes=(2, 1))                    # (a', s, b)
    return np.tensordot(A.conj(), X, axes=([1, 2], [1, 2]))      # (a, a')


def evaluate(Ts, szb, bonds, J, pairs=()):
    n = len(Ts)
    P = ops(szb)
    Ls = [np.ones((1, 1))]
    for k in range(n):
        Ls.append(tl(Ls[-1], Ts[k]))
    Rs = [None] * (n + 1)
    Rs[n] = np.ones((1, 1))
    for k in range(n - 1, -1, -1):
        Rs[k] = tr_(Rs[k + 1], Ts[k])
    norm = float(np.real(Ls[n][0, 0]))
    need = {}
    for (i, j) in list(bonds) + list(pairs):
        i, j = sorted((int(i), int(j)))
        need.setdefault(i, set()).add(j)
    C = {}
    for i, js in need.items():
        jmax = max(js)
        for oi, oj, c in (("Sz", "Sz", 4.0), ("Sp", "Sm", 2.0), ("Sm", "Sp", 2.0)):
            X = tl(Ls[i], Ts[i], P[oi])
            for j in range(i + 1, jmax + 1):
                if j in js:
                    Y = tl(X, Ts[j], P[oj])
                    v = float(np.real(np.sum(Y * Rs[j + 1])))
                    key = "%d_%d" % (i, j)
                    C[key] = C.get(key, 0.0) + c * v / norm / 3.0
                if j < jmax:
                    X = tl(X, Ts[j])
    E = 0.0
    for (i, j), c in zip(bonds, J):
        i, j = sorted((int(i), int(j)))
        E += 3.0 * float(c) * C["%d_%d" % (i, j)]
    L0, L1, L2 = np.ones((1, 1)), np.zeros((1, 1)), np.zeros((1, 1))
    for k in range(n):
        A = Ts[k]
        nL0 = tl(L0, A)
        nL1 = tl(L1, A) + tl(L0, A, P["Sz"])
        nL2 = tl(L2, A) + 2.0 * tl(L1, A, P["Sz"]) + tl(L0, A, P["Sz2"])
        L0, L1, L2 = nL0, nL1, nL2
    m1 = float(np.real(L1[0, 0])) / norm
    m2 = float(np.real(L2[0, 0])) / norm
    return dict(norm=norm, E=E, C=C, sz_mean=m1, sz_var=m2 - m1 * m1)


def load_npz(path):
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    n = len([k for k in z.files if k.startswith("B")])
    Ts = [np.asarray(z["B%d" % k]) for k in range(n)]
    return Ts, meta


def main(argv):
    spec = json.load(open(argv[0]))
    out = {}
    for p in argv[2:]:
        Ts, meta = load_npz(p)
        r = evaluate(Ts, meta["sz_basis"], spec["bonds"], spec["J"], spec.get("pairs", []))
        r["sid"] = meta.get("sid")
        out[p] = r
        print("%s E=%.12f norm=%.12f szvar=%.2e" % (meta.get("sid"), r["E"], r["norm"], r["sz_var"]), flush=True)
    with open(argv[1] + ".tmp", "w") as f:
        json.dump(out, f, indent=1)
    import os
    os.replace(argv[1] + ".tmp", argv[1])


if __name__ == "__main__":
    main(sys.argv[1:])
