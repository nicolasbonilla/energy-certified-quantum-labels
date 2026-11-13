"""Exact ground state and exact envelope chain of one (J2, observable, side) on the 4x6 torus (DECLARATION.md sec. 4).

  python ed_env.py <SB> gs  <J2>                    -> out/ed/gs_J2.json and work/gs_J2.npy
  python ed_env.py <SB> env <J2> <obs> <side>       -> out/ed/env_J2_obs_side.json   (obs: ms|dim, side: +1|-1)

Chain: ground states of H - side*lam*n*O for lam = 10^(k/8), k = -24..16, warm-started (previous vector plus 1e-3 of a
seeded random vector), stopped early once (e - e0) > 1.0 or O has changed by < 1e-7 over three consecutive points.
Random-restart check at lam = 0.1, 1, 10. Every record keeps the eigenvalue (dual), the primal pair (e, O) and
diagnostics.
"""
import os
import sys
import time

import numpy as np

import wlib


def main(SB, mode, J2, obs=None, side=None):
    J2 = float(J2)
    od = os.path.join(SB, "out", "ed"); wd = os.path.join(SB, "work")
    os.makedirs(od, exist_ok=True); os.makedirs(wd, exist_ok=True)
    lat = wlib.Lattice(6, 4)
    lat.check_bonds()
    ops = wlib.Ops(lat, J2)
    n, dim = ops.n, ops.dim
    rng = np.random.default_rng(wlib.seed_of("ed", mode, J2, obs, side))
    t0 = time.time()
    g0, v0, nmv, res = wlib.ground(lambda x: ops.H @ x, dim, rng.standard_normal(dim), tol=1e-14, ncv=40)
    ev0 = ops.evaluate(v0)
    rec0 = {"lam": 0.0, "g": g0 / n, "nmv": nmv, "res": res, "sec": time.time() - t0, **ev0}
    print(wlib.now(), "GS J2=%g E0=%.12f e0=%.12f ms=%.10f dim=%.10f S2=%.2e res=%.1e nmv=%d" % (
        J2, g0, g0 / n, ev0["ms"], ev0["dim"], ev0["S2"], res, nmv), flush=True)
    if mode == "gs":
        np.save(os.path.join(wd, "gs_%g.npy" % J2), v0)
        wlib.dump(os.path.join(od, "gs_%g.json" % J2), {"J2": J2, "n": n, "dim": dim, "E0": g0, "e0": g0 / n,
                                                       "gs": rec0, "build_seconds": ops.build_seconds,
                                                       "time": wlib.now()})
        return
    side = int(side)
    assert obs in ("ms", "dim") and side in (1, -1)
    e0 = g0 / n
    o0 = ev0[obs]
    recs = [rec0]
    v = v0.copy()
    stable = 0
    lams = [10.0 ** (k / 8.0) for k in range(-24, 17)]
    for lam in lams:
        def mv(x, lam=lam):
            return ops.H @ x - side * lam * n * ops.O(obs, x)
        start = v + 1e-3 * np.linalg.norm(v) * rng.standard_normal(dim) / np.sqrt(dim)
        t1 = time.time()
        g, v, nmv, res = wlib.ground(mv, dim, start, tol=1e-12, ncv=24)
        ev = ops.evaluate(v)
        rec = {"lam": lam, "g": g / n, "nmv": nmv, "res": res, "sec": time.time() - t1, **ev}
        if abs(lam - 0.1) < 1e-9 or abs(lam - 1.0) < 1e-9 or abs(lam - 10.0) < 1e-9:
            gr, vr, nmr, rr = wlib.ground(mv, dim, rng.standard_normal(dim), tol=1e-12, ncv=24)
            rec["restart"] = {"g": gr / n, "dg": (gr - g) / n, "nmv": nmr, "res": rr}
        recs.append(rec)
        print(wlib.now(), "lam=%.4g g=%.12f de=%.4e %s=%.10f dO=%+.3e S2=%.2e res=%.1e nmv=%d %.0fs" % (
            lam, g / n, ev["e"] - e0, obs, ev[obs], ev[obs] - o0, ev["S2"], res, nmv, rec["sec"]), flush=True)
        wlib.dump(os.path.join(od, "env_%g_%s_%+d.json" % (J2, obs, side)),
                  {"J2": J2, "obs": obs, "side": side, "n": n, "e0": e0, "o0": o0, "records": recs, "done": False})
        stable = stable + 1 if abs(ev[obs] - recs[-2][obs]) < 1e-7 else 0
        if ev["e"] - e0 > 1.0 or stable >= 3:
            break
    wlib.dump(os.path.join(od, "env_%g_%s_%+d.json" % (J2, obs, side)),
              {"J2": J2, "obs": obs, "side": side, "n": n, "e0": e0, "o0": o0, "records": recs, "done": True,
               "build_seconds": ops.build_seconds, "time": wlib.now()})


if __name__ == "__main__":
    main(*sys.argv[1:])
