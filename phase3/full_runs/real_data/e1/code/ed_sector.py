"""Exact sector ground energy (sparse Lanczos) of the same Hamiltonians, for toys (n <= 12, laptop) and the n = 19
calibration (VM).  Independent of lb_opt.py.  usage: python ed_sector.py <graph.json> <task.json> <out.json>"""
import json
import sys
import time
from itertools import combinations

import numpy as np
import scipy.sparse as sps
from scipy.sparse.linalg import eigsh


def sector_ground(G, task, k=1):
    n = G["n"]
    edges = [tuple(sorted(int(v) for v in e)) for e in G["mps"]["edges"]]
    eta = np.array(G["mps"]["eta"], dtype=float)
    nup = int(sum(G["mps"]["up_init"]))
    Jz, lam, sg = float(eval_frac(task["Jz"])), float(eval_frac(task.get("lam", 0))), int(task.get("sigma", 0))
    hz = np.zeros(n)
    if task["kind"] == "m_s":
        hz = -sg * lam * eta
    elif task["kind"] == "Czz_bar":
        Jz = Jz - 4 * sg * lam
    states = np.array([sum(1 << i for i in c) for c in combinations(range(n), nup)], dtype=np.int64)
    states.sort()
    index = {int(s): r for r, s in enumerate(states)}
    bits = ((states[:, None] >> np.arange(n)[None, :]) & 1)
    z = 2 * bits - 1
    diag = z @ hz
    rows, cols, vals = [], [], []
    for (i, j) in edges:
        diag = diag + 0.25 * Jz * z[:, i] * z[:, j]
        anti = np.where(bits[:, i] != bits[:, j])[0]
        flipped = states[anti] ^ (1 << i) ^ (1 << j)
        rows.extend(int(index[int(f)]) for f in flipped)
        cols.extend(anti.tolist())
        vals.extend([0.5] * len(anti))
    dim = len(states)
    H = sps.csr_matrix((vals, (rows, cols)), shape=(dim, dim)) + sps.diags(diag)
    if dim <= 400:
        w = np.linalg.eigvalsh(H.toarray())[:k]
    else:
        w = np.sort(eigsh(H, k=k, which="SA", tol=1e-12, maxiter=100000)[0])
    return [float(x) for x in w], dim


def eval_frac(s):
    from fractions import Fraction
    return Fraction(s) if isinstance(s, str) else Fraction(s)


if __name__ == "__main__":
    t0 = time.time()
    G = json.load(open(sys.argv[1]))
    task = json.load(open(sys.argv[2]))
    w, dim = sector_ground(G, task)
    out = dict(task=task, E0=w[0], dim=dim, time_s=time.time() - t0)
    json.dump(out, open(sys.argv[3], "w"), indent=1)
    print("ED sector dim %d E0 = %.12f (%.1fs)" % (dim, w[0], time.time() - t0))
