"""Kill test W: gates (DECLARATION.md sec. 8). Runs on the VM, writes out/gates/<name>.json.

  python gates_w.py <SB> ed       G1-G4: exact code on 4x4 and 4x6 against closed forms and the literature
  python gates_w.py <SB> netket   G6: NetKet energy of a random ViT equals wlib's exact evaluation (4x4); sampler
                                  stays in S^z = 0; 30 VMC steps run
  python gates_w.py <SB> krylov   G7: Taylor propagator against scipy expm_multiply (4x4)
"""
import json
import math
import os
import sys
import time

import numpy as np

import wlib


def out(SB, name, d):
    od = os.path.join(SB, "out", "gates"); os.makedirs(od, exist_ok=True)
    d["time"] = wlib.now()
    wlib.dump(os.path.join(od, name + ".json"), d)
    print(json.dumps(d, indent=1, default=float), flush=True)


def gate_ed(SB):
    res = {}
    # G1: 4x4 Heisenberg ground energy against the literature value E0 = -11.2284832084 (e0 = -0.70178020)
    lat = wlib.Lattice(4, 4); lat.check_bonds()
    ops = wlib.Ops(lat, 0.0)
    g, v, nmv, rs = wlib.ground(lambda x: ops.H @ x, ops.dim, np.ones(ops.dim) + 0.01 * np.arange(ops.dim) / ops.dim,
                                tol=1e-14, ncv=40)
    ev = ops.evaluate(v)
    res["G1_4x4_E0"] = {"E0": g, "lit": -11.2284832084, "diff": g + 11.2284832084, "ms": ev["ms"], "S2": ev["S2"],
                        "ok": abs(g + 11.2284832084) < 1e-6}
    # G3: m_s^2 by ladder operators against the direct pair sum (1/n^2) sum_ij eps_i eps_j <S_i.S_j>
    n = lat.n
    direct = 0.75 * n
    for i in range(n):
        for j in range(i + 1, n):
            Bij = wlib.bond_operator(ops.basis, [(i, j, 1.0)])
            direct += 2 * lat.eps[i] * lat.eps[j] * float(v @ (Bij @ v))
    direct /= n ** 2
    res["G3_ms_pairsum"] = {"ladder": ev["ms"], "direct": direct, "diff": ev["ms"] - direct,
                            "ok": abs(ev["ms"] - direct) < 1e-12}
    # G4: columnar singlet product on 4x4 (ground state of the even x-bonds only): dim = 45/256, ms = 24/256
    bw = [(i, j, 1.0) for (i, j, d) in lat.j1() if d == "x" and lat.xy[i][0] % 2 == 0]
    Hd = wlib.bond_operator(ops.basis, bw)
    gd, vd, _, _ = wlib.ground(lambda x: Hd @ x, ops.dim, np.ones(ops.dim) + 0.01 * np.arange(ops.dim) / ops.dim,
                               tol=1e-14, ncv=40)
    evd = ops.evaluate(vd)
    res["G4_dimer_product"] = {"E": gd, "E_expected": -0.75 * 8, "dim": evd["dim"], "dim_expected": 45 / 256,
                               "ms": evd["ms"], "ms_expected": 24 / 256,
                               "ok": abs(gd + 6) < 1e-10 and abs(evd["dim"] - 45 / 256) < 1e-10 and abs(evd["ms"] - 24 / 256) < 1e-10}
    # G2: Neel product state on 4x6 (both J2): e = -0.5 - J2*0.5... closed forms
    for J2 in (0.0, 0.5):
        lat6 = wlib.Lattice(6, 4); lat6.check_bonds()
        o6 = wlib.Ops(lat6, J2)
        v6 = np.zeros(o6.dim); v6[np.searchsorted(o6.basis, lat6.neel_int())] = 1.0
        e6 = o6.evaluate(v6)
        n6 = lat6.n
        exp_e = (-0.25 * 2 * n6 + J2 * 0.25 * 2 * n6) / n6
        res["G2_neel_4x6_J2=%g" % J2] = {"e": e6["e"], "e_expected": exp_e, "ms": e6["ms"],
                                         "ms_expected": 0.25 + 1 / (2 * n6), "dim": e6["dim"],
                                         "dim_expected": 1 / (2 * n6), "S2": e6["S2"], "S2_expected": n6 / 2,
                                         "dim_sector": o6.dim, "build_seconds": o6.build_seconds,
                                         "ok": abs(e6["e"] - exp_e) < 1e-12 and abs(e6["ms"] - 0.25 - 1 / (2 * n6)) < 1e-12
                                         and abs(e6["dim"] - 1 / (2 * n6)) < 1e-12 and abs(e6["S2"] - n6 / 2) < 1e-10}
        del o6
    res["all_ok"] = all(v_["ok"] for v_ in res.values() if isinstance(v_, dict))
    out(SB, "ed", res)


def gate_netket(SB):
    import jax
    import vit_w
    res = {}
    lat = wlib.Lattice(4, 4)
    for J2 in (0.0, 0.5):
        model = vit_w.make_model(lat, "M")
        nk, hi, Hop, vs = vit_w.netket_objects(lat, J2, model, ("gate", J2), n_samples=256)
        fs = nk.vqs.FullSumState(hi, model, variables=vs.variables)
        e_nk = float(np.real(fs.expect(Hop).mean)) / lat.n
        ops = wlib.Ops(lat, J2)
        v = vit_w.exact_vector(model, vs.variables, ops.basis, lat.n)
        ev = ops.evaluate(v)
        smp = np.asarray(vs.sample()).reshape(-1, lat.n)
        res["G6_J2=%g" % J2] = {"e_netket_fullsum": e_nk, "e_wlib": ev["e"], "diff": e_nk - ev["e"],
                                "sample_sz_max_abs": float(np.abs(smp.sum(axis=1)).max()),
                                "sample_values": sorted(set(np.unique(smp).tolist())),
                                "ok": abs(e_nk - ev["e"]) < 1e-10 and float(np.abs(smp.sum(axis=1)).max()) == 0.0}
    # 30 VMC steps, J2 = 0, 4x4 (smoke)
    model = vit_w.make_model(lat, "M")
    nk, hi, Hop, vs = vit_w.netket_objects(lat, 0.0, model, ("gate-vmc",), n_samples=512)
    log = []
    gs, kind = vit_w.make_driver(nk, Hop, vs)
    res["driver"] = kind
    t0 = time.time()
    gs.run(n_iter=30, callback=lambda s, ld, d: log.append(float(np.real(ld["Energy"].mean)) / lat.n) or True,
           show_progress=False)
    res["G6_vmc_smoke"] = {"first": log[0], "last": log[-1], "exact_4x4": -0.70178020, "seconds": time.time() - t0,
                           "ok": log[-1] < log[0]}
    res["versions"] = {"jax": jax.__version__, "netket": nk.__version__}
    res["all_ok"] = all(v_["ok"] for k, v_ in res.items() if k.startswith("G"))
    out(SB, "netket", res)


def gate_krylov(SB):
    import scipy.sparse.linalg as sla
    import krylov_w
    lat = wlib.Lattice(4, 4)
    ops = wlib.Ops(lat, 0.5)
    v = np.zeros(ops.dim, dtype=np.complex128); v[np.searchsorted(ops.basis, lat.neel_int())] = 1.0
    dt = 0.3
    a, nmv = krylov_w.propagate(ops.H, v, dt, 12.0)
    b = sla.expm_multiply(-1j * dt * ops.H.astype(np.complex128), v)
    d = {"G7_propagator": {"max_abs_diff": float(np.abs(a - b).max()), "norm_a": float(np.linalg.norm(a)), "nmv": nmv,
                           "ok": float(np.abs(a - b).max()) < 1e-10}}
    d["all_ok"] = d["G7_propagator"]["ok"]
    out(SB, "krylov", d)


if __name__ == "__main__":
    SB, which = sys.argv[1], sys.argv[2]
    {"ed": gate_ed, "netket": gate_netket, "krylov": gate_krylov}[which](SB)
