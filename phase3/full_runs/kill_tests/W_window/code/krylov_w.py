"""Method (c), reported without verdict: the project's generator emulated exactly (DECLARATION.md sec. 5c).
Krylov states psi_k = exp(-i H k dt)|Neel>, k = 1..10, dt = pi / (E_max - E_0), exact propagation in the S^z = 0
sector; configuration subspaces (i) the K most probable configurations of p(x) = (1/10) sum_k |<x|psi_k>|^2 (ties by
basis order), (ii) the union of exact multinomial samples with `shots` per circuit; Rayleigh-Ritz in the span; the
lowest Ritz vector is evaluated exactly.

  python krylov_w.py <SB> <J2>       -> out/methods/krylov_<J2>.json  (needs out/ed/gs_<J2>.json)
"""
import json
import math
import os
import sys
import time

import numpy as np
import scipy.sparse as sp

import wlib

KS = [100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000]
SHOTS = [1000, 10000, 100000]
NK = 10


def propagate(H, v, t, hnorm):
    m = max(1, int(math.ceil(abs(t) * hnorm / 0.5)))
    tau = t / m
    nmv = 0
    for _ in range(m):
        term = v.copy(); acc = v.copy()
        for j in range(1, 40):
            term = (-1j * tau / j) * wlib.mul(H, term); nmv += 1
            acc += term
            if np.linalg.norm(term) < 1e-16:
                break
        v = acc
    return v, nmv


def subspace_ground(H, S):
    S = np.sort(np.asarray(S, dtype=np.int64))
    K = S.size
    pos = -np.ones(H.shape[0], dtype=np.int64); pos[S] = np.arange(K)
    R = H[S]
    R = R.tocoo()
    keep = pos[R.col] >= 0
    Hs = sp.csr_matrix((R.data[keep], (R.row[keep], pos[R.col[keep]])), shape=(K, K))
    if K <= 3000:
        w, U = np.linalg.eigh(Hs.toarray())
        g, x = float(w[0]), U[:, 0]
    else:
        g, x, _, _ = wlib.ground(lambda y: Hs @ y, K, np.ones(K) / np.sqrt(K), tol=1e-12, ncv=30)
    return S, g, x


def main(SB, J2):
    J2 = float(J2)
    od = os.path.join(SB, "out", "methods"); os.makedirs(od, exist_ok=True)
    out = os.path.join(od, "krylov_%g.json" % J2)
    gs = json.load(open(os.path.join(SB, "out", "ed", "gs_%g.json" % J2)))
    lat = wlib.Lattice(6, 4)
    ops = wlib.Ops(lat, J2)
    n = lat.n
    E0 = gs["E0"]
    Emax = (2 * n + J2 * 2 * n) / 4.0
    dt = math.pi / (Emax - E0)
    hnorm = max(abs(E0), Emax)
    i0 = int(np.searchsorted(ops.basis, lat.neel_int()))
    assert ops.basis[i0] == lat.neel_int()
    v = np.zeros(ops.dim, dtype=np.complex128); v[i0] = 1.0
    p = np.zeros(ops.dim)
    kryl = []
    t0 = time.time()
    states = []
    for k in range(1, NK + 1):
        v, nmv = propagate(ops.H, v, dt, hnorm)
        a2 = np.abs(v) ** 2
        p += a2 / NK
        states.append(a2)
        ek = float(np.vdot(v, wlib.mul(ops.H, v)).real) / n
        kryl.append({"k": k, "norm": float(np.linalg.norm(v)), "e": ek, "nmv": nmv})
        print(wlib.now(), "k=%d norm-1=%.1e e=%.12f nmv=%d" % (k, kryl[-1]["norm"] - 1, ek, nmv), flush=True)
    order = np.argsort(-p, kind="stable")
    rows = []
    rng = np.random.default_rng(wlib.seed_of("krylov-shots", J2))
    variants = [("topK", K, None) for K in KS] + [("shots", None, s) for s in SHOTS]
    for kind, K, shots in variants:
        t1 = time.time()
        if kind == "topK":
            S = order[:K]
        else:
            sel = set()
            for a2 in states:
                c = rng.multinomial(shots, a2 / a2.sum())
                sel.update(np.nonzero(c)[0].tolist())
            S = np.array(sorted(sel), dtype=np.int64)
        S, g, x = subspace_ground(ops.H, S)
        vec = np.zeros(ops.dim); vec[S] = x
        ev = ops.evaluate(vec)
        row = {"method": "Krylov", "J2": J2, "label": "%s_%s" % (kind, K if K else shots), "kind": kind,
               "K": int(S.size), "shots_per_circuit": shots, "g_ritz": g / n, "dE_check": g / n - ev["e"],
               "p_captured": float(p[S].sum()), "sec": time.time() - t1, **ev}
        rows.append(row)
        print(wlib.now(), "%s K=%d e=%.10f ms=%.8f dim=%.8f %.0fs" % (row["label"], S.size, ev["e"], ev["ms"],
                                                                     ev["dim"], row["sec"]), flush=True)
        wlib.dump(out, {"J2": J2, "dt": dt, "E0": E0, "Emax": Emax, "krylov": kryl, "rows": rows, "done": False})
    wlib.dump(out, {"J2": J2, "dt": dt, "E0": E0, "Emax": Emax, "krylov": kryl, "rows": rows, "done": True,
                    "seconds": time.time() - t0, "time": wlib.now()})


if __name__ == "__main__":
    main(*sys.argv[1:])
