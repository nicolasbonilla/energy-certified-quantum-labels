"""VM side (DECLARATION.md §5): post-processing of the device data and the noiseless control of the identical
circuits. Pure numpy / scipy (no qiskit, no rustworkx). Root layout: <root>/code (this folder), <root>/jobs/<A|B>/
(raw_configs.npz, prep.json, checks.json), <root>/refs/ (method run ref / gap / emu JSONs), <root>/out/.

  python qpu_post.py <root> selftest                 TrotterMPS vs dense and the sampler on the d = 3 graph
  python qpu_post.py <root> device  <job> <Jz>       device shots k = 1..10 -> rec / ps subspaces -> labels
  python qpu_post.py <root> control <Jz> <shots>     TrotterMPS (chi <= 256) -> emu2.sample_mps -> same post-processing
  python qpu_post.py <root> summary

Configurations: uint64, bit i = 1 <=> site i down (qpu_lib C3 = emu2's convention), one word (n = 57).
Post-processing = method/code/fr.py subspace(p < 0, recovery) -> rr -> evaluate, with byte-identical emu2.
"""
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qpu_lib as ql  # noqa: E402
import emu2  # noqa: E402  (method_copy, put on sys.path by qpu_lib)

CHI = 256
SVD_MIN = 1e-12
FLAG_DISCARDED = 1e-6
SAMPLE_BATCH = 50_000


def seed(*parts):
    return int.from_bytes(hashlib.sha256(("qpu|" + "|".join(str(p) for p in parts)).encode()).digest()[:8], "little")


def js(Jz):
    return "%.1f" % float(Jz)


def wjson(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w") as f:
        json.dump(obj, f, indent=1, default=float)
    os.replace(p + ".tmp", p)


def rjson(p):
    with open(p) as f:
        return json.load(f)


def g57():
    return emu2.load_graph(os.path.join(HERE, "graphs", "hh_d5.json"))


def refs(root, Jz):
    r = rjson(os.path.join(root, "refs", "ref_n57_J%s.json" % js(Jz)))
    gp = rjson(os.path.join(root, "refs", "gap_n57_J%s.json" % js(Jz)))
    return r, gp["E_sm1"] - r["E0"]


def subspace(shots, g, recovery, rng):
    """fr.py subspace() with p < 0 (no added noise): unique, then recovery or post-selection."""
    raw = np.concatenate([s.reshape(-1, 1) if s.ndim == 1 else s for s in shots]).astype(np.uint64)
    Bu, _ = emu2.unique_rows(raw)
    insec = emu2.popcount(Bu) == g["n_down"]
    stats = dict(n_shots=int(len(raw)), n_unique=int(len(Bu)), n_unique_in_sector=int(insec.sum()))
    if recovery:
        cs = emu2.CSet(emu2.recover(Bu, g["n"], g["n_down"], rng), g["n"])
    else:
        cs = emu2.CSet(Bu[insec], g["n"])
    stats["D"] = len(cs)
    return cs, stats


def rr_eval(cs, g, Jz, ref, gap):
    t0 = time.time()
    Hs = emu2.SubH(cs, g, Jz)
    E, a = emu2.ground(Hs, v0=emu2.neel_start(cs, g))
    lab = emu2.diag_labels(cs, a, g)
    err = emu2.label_errors(lab, ref["labels"])
    Z = np.asarray(lab["Z"])
    Zr = np.asarray(ref["labels"]["Z"])
    return dict(E=E, eps=E - ref["E0"], ratio=(E - ref["E0"]) / gap, dE_site=(E - ref["E0"]) / g["n"], labels=lab,
                err=err, signed_dZ_site=(np.sign(Zr) * (Z - Zr)).tolist(), nnz=Hs.nnz, rr_secs=time.time() - t0)


def process(shot_lists, g, Jz, ref, gap, tagname):
    out = {}
    for var, recov in (("rec", True), ("ps", False)):
        rng = np.random.default_rng(seed("recover", 57, js(Jz), tagname, var))
        cs, st = subspace(shot_lists, g, recov, rng)
        res = rr_eval(cs, g, Jz, ref, gap)
        res["stats"] = st
        out[var] = res
        print(tagname, Jz, var, st, "ratio %.4g" % res["ratio"], "dm_s %+.4f" % res["err"]["dm_s"],
              "over %.3f" % res["err"]["frac_sites_overordered"], flush=True)
    return out


def t_device(root, job, Jz):
    g = g57()
    Jz = float(Jz)
    d = os.path.join(root, "jobs", job)
    chk = rjson(os.path.join(d, "checks.json"))
    raw = np.load(os.path.join(d, "raw_configs.npz"))
    shots = [raw["J%s_k%d" % (js(Jz), k)] for k in range(1, ql.K + 1)]
    ref, gap = refs(root, Jz)
    res = process(shots, g, Jz, ref, gap, "device_" + job)
    wjson(os.path.join(root, "out", "device_%s_J%s.json" % (job, js(Jz))),
          dict(job=job, Jz=Jz, checks_both_pass=chk["both_pass"], shots_per_circuit=[int(len(s)) for s in shots],
               E0=ref["E0"], gap=gap, m_s_ref=ref["labels"]["m_s"], var=res))


def t_control(root, Jz, shots):
    g = g57()
    Jz = float(Jz)
    shots = int(shots)
    dt = ql.DT57[round(Jz, 1)]
    T = ql.TrotterMPS(g, chi_max=CHI, svd_min=SVD_MIN)
    lists, info, store = [], [], {}
    for k in range(1, ql.K + 1):
        t0 = time.time()
        T.step(Jz, dt)
        t1 = time.time()
        Ts = T.export()
        rng = np.random.default_rng(seed("control", js(Jz), k))
        r = emu2.sample_mps(Ts, g["order"], 1, shots, rng, g["n"], batch=SAMPLE_BATCH, want_amp=False, merge=True)
        lists.append(emu2.expand(r["B"], r["count"]))
        store["B%d" % k] = r["B"][:, 0]
        store["c%d" % k] = r["count"]
        info.append(dict(k=k, step_secs=t1 - t0, sample_secs=time.time() - t1, max_chi=T.max_chi,
                         discarded_cum=T.discarded, n_unique=int(len(r["B"]))))
        print("control", Jz, info[-1], flush=True)
    os.makedirs(os.path.join(root, "out"), exist_ok=True)
    np.savez_compressed(os.path.join(root, "out", "control_samples_J%s.npz" % js(Jz)), **store)
    ref, gap = refs(root, Jz)
    res = process(lists, g, Jz, ref, gap, "control")
    wjson(os.path.join(root, "out", "control_J%s.json" % js(Jz)),
          dict(Jz=Jz, dt=dt, shots_per_circuit=shots, chi_max=CHI, svd_min=SVD_MIN, info=info,
               discarded_total=T.discarded, flag_discarded=bool(T.discarded > FLAG_DISCARDED), E0=ref["E0"], gap=gap,
               m_s_ref=ref["labels"]["m_s"], var=res))


def t_selftest(root):
    g = emu2.load_graph(os.path.join(HERE, "graphs", "hh_d3.json"))
    T = ql.TrotterMPS(g, chi_max=64)
    for _ in range(3):
        T.step(1.2, 0.0569)
    v = ql.dense_trotter(g, 1.2, 0.0569, 3)
    pr = np.abs(v) ** 2
    idx = np.arange(len(v))
    Zd = np.array([float(pr @ (1 - 2 * ((idx >> i) & 1))) for i in range(g["n"])])
    dz = float(np.max(np.abs(T.z_expect() - Zd)))
    N = 40000
    r = emu2.sample_mps(T.export(), g["order"], 1, N, np.random.default_rng(3), g["n"], batch=20000, want_amp=False)
    B = r["B"][:, 0]
    Zs = np.array([1 - 2 * float(np.sum(r["count"] * ((B >> np.uint64(i)) & np.uint64(1))) / N) for i in range(g["n"])])
    zs = float(np.max(np.abs(Zs - Zd) / np.sqrt(np.maximum(1 - Zd ** 2, 1e-4) / N)))
    ok = dz < 1e-9 and zs < 5.0
    wjson(os.path.join(root, "out", "selftest.json"), dict(max_dZ_mps_dense=dz, max_sampler_sigma=zs, ok=ok))
    print("SELFTEST", "OK" if ok else "FAILED", dz, zs)
    if not ok:
        sys.exit(1)


def t_summary(root):
    o = os.path.join(root, "out")
    S = dict(device={}, control={})
    for f in sorted(os.listdir(o)):
        if f.startswith("device_") and f.endswith(".json"):
            d = rjson(os.path.join(o, f))
            S["device"][js(d["Jz"])] = dict(job=d["job"], checks=d["checks_both_pass"],
                                            **{v: dict(ratio=d["var"][v]["ratio"], eps=d["var"][v]["eps"],
                                                       dm_s=d["var"][v]["err"]["dm_s"],
                                                       over=d["var"][v]["err"]["frac_sites_overordered"],
                                                       dZ=d["var"][v]["err"]["dZ"], dCzz=d["var"][v]["err"]["dCzz"],
                                                       stats=d["var"][v]["stats"]) for v in ("rec", "ps")})
        if f.startswith("control_J") and f.endswith(".json"):
            d = rjson(os.path.join(o, f))
            S["control"][js(d["Jz"])] = dict(discarded=d["discarded_total"], flag=d["flag_discarded"],
                                             **{v: dict(ratio=d["var"][v]["ratio"], eps=d["var"][v]["eps"],
                                                        dm_s=d["var"][v]["err"]["dm_s"],
                                                        over=d["var"][v]["err"]["frac_sites_overordered"],
                                                        stats=d["var"][v]["stats"]) for v in ("rec", "ps")})
    wjson(os.path.join(o, "summary.json"), S)
    print(json.dumps(S, indent=1, default=float)[:6000])


if __name__ == "__main__":
    root, mode = sys.argv[1], sys.argv[2]
    if mode == "selftest":
        t_selftest(root)
    elif mode == "device":
        t_device(root, sys.argv[3], sys.argv[4])
    elif mode == "control":
        t_control(root, sys.argv[3], sys.argv[4])
    elif mode == "summary":
        t_summary(root)
    else:
        raise SystemExit("mode?")
