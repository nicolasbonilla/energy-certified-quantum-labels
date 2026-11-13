"""Tasks of the full method runs (../DECLARATION.md). One task per process, run by sched2.py.

  python fr.py <root> ref     <n> <Jz>          DMRG ground state (labels; pickle kept for gsscan Jz)
  python fr.py <root> gap     <n> <Jz>          DMRG lowest state of S^z - 1
  python fr.py <root> krylov  <n> <Jz>          exact-evolution Krylov states from Neel, k = 1..10, fresh samples
  python fr.py <root> kreuse  <Jz>              n = 57: pilot3 Krylov samples converted (copied at setup, hashed)
  python fr.py <root> calib   <n>               noise levels p*, p_dev (and p_pre at n = 57) at Jz = 2.5
  python fr.py <root> emu     <n> <Jz>          all emulation variants (+ Krylov shot scan at KSCAN Jz)
  python fr.py <root> gsscan  <n> <Jz>          perfect sampling of the DMRG ground state, nested subspace scan
  python fr.py <root> bo      <Jz> <subspace>   n = 57: second basis-optimization attempt (bo2.py)
  python fr.py <root> wplus   <n> <Jz>          "+" witness chain: ground states of H - lam sum_i eta_i Z_i
  python fr.py <root> plan    <plan.json>
"""
import json
import os
import pickle
import sys
import time
import warnings
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emu2  # noqa: E402

TOY = os.environ.get("FR_TOY", "")      # "" | "12" | "70": laptop pipeline dry runs only (toy graphs)
K = 10
P_RO = 0.01
P_GRID = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
CALIB_JZ = 2.5
KBATCH = 50000                     # Krylov sampling batch (shots per circuit per batch)
STD_SHOTS = 100000                 # shots per Krylov circuit in the published pipeline
GBATCH = 100000                    # ground-state sampling batch
KCHI = 128                         # Krylov MPS bond dimension
DT = {57: {1.1: 0.0591, 1.2: 0.0569, 1.3: 0.0548, 1.4: 0.0582, 1.5: 0.0579, 1.6: 0.0622, 1.8: 0.0593, 2.0: 0.0551,
           2.2: 0.0537, 2.5: 0.0570, 3.0: 0.0596, 3.5: 0.0579, 4.0: 0.0602, 5.0: 0.0578, 6.0: 0.0681},
      115: {1.1: 0.0352, 1.2: 0.0354, 1.3: 0.0337, 1.4: 0.0334, 1.5: 0.0335, 1.6: 0.0361, 2.0: 0.0328, 2.5: 0.0334,
            3.0: 0.0335, 4.0: 0.0351, 5.0: 0.0344, 6.0: 0.0358}}
# digitized IBM values (R4 / pilot PRIOR_ART_CHECK §3; ±5 % on log axes): dataset (post-BO) ratio, raw ratio, gap
IBM_POST = {57: {1.6: 1.348, 1.8: 0.822, 2.0: 0.574, 2.1: 0.521, 2.5: 0.235, 3.0: 0.121, 4.0: 0.0523, 5.0: 0.024,
                 6.0: 0.0179},
            115: {1.6: 2.716, 1.8: 1.772, 2.0: 1.111, 2.1: 0.992, 2.5: 0.464, 3.0: 0.253, 4.0: 0.0765, 5.0: 0.0407,
                  6.0: 0.0157}}
IBM_PRE = {57: {1.6: 6.89, 2.0: 3.39, 2.5: 1.586, 3.0: 0.902, 4.0: 0.367, 5.0: 0.200, 6.0: 0.097}, 115: {}}
IBM_GAP = {57: {1.1: 0.080, 1.2: 0.162, 1.6: 0.463, 1.8: 0.624, 2.0: 0.757, 2.5: 1.061, 3.0: 1.336, 4.0: 1.883,
                5.0: 2.395, 6.0: 2.905},
           115: {1.1: 0.102, 1.2: 0.190, 1.6: 0.493, 1.8: 0.624, 2.0: 0.757, 2.5: 1.061, 3.0: 1.336, 4.0: 1.883,
                 5.0: 2.395, 6.0: 2.905}}
IBM_INSECTOR = {57: 81862, 115: 81974}       # unique in-sector bitstrings per 1e6 shots (Methods)
IBM_UNIQUE = {57: 972759, 115: 999531}

if TOY:
    JZ = {57: [1.2, 1.6, 2.5, 4.0], 115: [1.2, 1.6, 2.5, 4.0]}
else:
    JZ = {57: [1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0],
          115: [1.1, 1.2, 1.3, 1.4, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]}
GAP_JZ = {57: [1.2, 1.6, 2.5, 4.0], 115: [1.2, 1.6, 2.5, 4.0]}
KFRESH57 = [1.2, 2.5]                                   # n = 57 Jz with fresh Krylov runs (3e5 shots per circuit)
KEXTRA = {57: {1.2: 300000, 2.5: 300000}, 115: {1.2: 300000, 2.5: 300000}}
KSCAN = {57: [1.2, 2.5], 115: [1.2, 2.5]}
PRE_JZ = [1.2, 2.5, 4.0]
GS_JZ = {57: [1.2, 1.6, 2.5, 4.0], 115: [1.2, 1.6, 2.5]}
GS_NMAX = {57: {1.2: 20_000_000, 1.6: 20_000_000, 2.5: 10_000_000, 4.0: 10_000_000},
           115: {1.2: 5_000_000, 1.6: 3_000_000, 2.5: 3_000_000}}
GS_TCAP = {57: 80 * 60, 115: 100 * 60}                 # sampling wall-time cap per task (s), declared
GS_LADDER = [100_000, 300_000, 1_000_000, 3_000_000, 10_000_000, 20_000_000]
TOPD = [100_000, 300_000, 1_000_000, 3_000_000]
CHIS = {57: [128, 200], 115: [160, 240]}               # sampling-state bond dimensions tried in order (gate G5)
BO_SUBS = [(1.2, "primary"), (2.5, "primary"), (2.5, "dev_rec")]
W_JZ = {57: [1.2, 1.6, 2.5], 115: [1.2, 1.6]}
W_LAMS = [1.3, 0.8, 0.5, 0.32, 0.22, 0.15, 0.1, 0.05, 0.02]
CHI_REF = {57: {0: 32, 2: 64, 4: 128, 6: 200}, 115: {0: 32, 2: 64, 4: 128, 6: 200, 8: 320}}
CHI_GAP = {57: {0: 32, 2: 64, 4: 128, 6: 200}, 115: {0: 32, 2: 64, 4: 128, 6: 200}}
SWEEPS = {57: (4, 14), 115: (10, 16)}
P3_DATA = "/mnt/cj/sandbox/r4_20261029T211913Z/data"     # read-only source of pilot3 Krylov samples (setup copy)

if TOY:
    GS_NMAX = {57: {j: 60000 for j in JZ[57]}, 115: {j: 60000 for j in JZ[115]}}
    GS_LADDER = [10000, 30000, 60000]
    TOPD = [2000, 5000]
    GBATCH = 10000
    KBATCH = 2000
    KCHI = 24
    STD_SHOTS = 4000
    KEXTRA = {57: {1.2: 8000}, 115: {1.2: 8000}}
    KSCAN = {57: [1.2], 115: [1.2]}
    KFRESH57 = list(JZ[57])
    GS_JZ = {57: [1.2, 2.5], 115: [1.2]}
    CHIS = {57: [16, 32], 115: [16, 32]}
    CHI_REF = {57: {0: 16, 2: 32}, 115: {0: 16, 2: 32}}
    CHI_GAP = CHI_REF
    SWEEPS = {57: (4, 8), 115: (4, 8)}
    W_JZ = {57: [1.2], 115: [1.2]}
    W_LAMS = [0.8, 0.3, 0.1]
    BO_SUBS = [(1.2, "primary"), (2.5, "dev_rec")]
    P_GRID = [0.0, 0.1, 0.3, 0.6, 1.0]


def js(Jz):
    return "%.1f" % float(Jz)


def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(path + ".tmp", path)


def rjson(path):
    with open(path) as f:
        return json.load(f)


def graph(n):
    n = int(n)
    if TOY:
        sys.path.insert(0, os.path.join(HERE, "tests"))
        import toygraphs
        if TOY == "70" and n == 115:
            G = toygraphs.hh7_prefix(70)
        else:
            G = toygraphs.hh3_prefix(12)
        G.setdefault("loops12", [G["local"]["loop"]] if G["local"].get("loop") else [])
        return emu2.load_graph(G)
    return emu2.load_graph(os.path.join(HERE, "graphs", "hh_d%d.json" % {57: 5, 115: 7}[n]))


def seed(*parts):
    import hashlib
    return int.from_bytes(hashlib.sha256(("fr|" + "|".join(str(p) for p in parts)).encode()).digest()[:8], "little")


def O(root, *p):
    return os.path.join(root, "out", *p)


def Dd(root, *p):
    return os.path.join(root, "data", *p)


# ----------------------------------------------------------------------------------------------------------- DMRG
def dmrg(g, Jz, chi_list, min_sweeps, max_sweeps, kind="neel", field=None, psi0=None, max_hours=1.5):
    """Two-site DMRG (settings of the pilots) returning per-sweep energies and bond dimensions."""
    import hhmodel
    from tenpy.algorithms import dmrg as tdmrg
    G = g["G"]
    M = hhmodel.HHModel(G, Jz, field=field)
    psi = psi0 if psi0 is not None else hhmodel.new_mps(M, hhmodel.product_state(G, kind))
    opts = hhmodel.dmrg_opts(chi_list=chi_list, min_sweeps=min_sweeps, max_sweeps=max_sweeps, max_E_err=1e-9,
                             max_hours=max_hours)
    opts["max_trunc_err"] = 1e-2        # TeNPy's consistency check would abort the task; the error is recorded instead
    t0 = time.time()
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        eng = tdmrg.TwoSiteDMRGEngine(psi, M, opts)
        E, psi = eng.run()
    ss = eng.sweep_stats
    nt = float(np.linalg.norm(psi.norm_test()))
    if nt > 1e-10:
        psi.canonical_form()
    M0 = M if field is None else hhmodel.HHModel(G, Jz)
    E0 = float(np.real(M0.H_MPO.expectation_value(psi)))
    st = dict(E_dmrg=float(E), E_H=E0, sweeps=int(eng.sweeps), time_s=time.time() - t0,
              E_sweeps=[float(x) for x in ss["E"]], chi_sweeps=[int(x) for x in ss["max_chi"]],
              dE_last=float(ss["Delta_E"][-1]) if ss["Delta_E"] else None,
              max_trunc_err=float(np.max(ss["max_trunc_err"])) if ss["max_trunc_err"] else None,
              last_trunc_err=float(ss["max_trunc_err"][-1]) if ss["max_trunc_err"] else None,
              chi_max_reached=int(max(psi.chi)), norm_test_before=nt,
              warnings=[str(w.message)[:200] for w in wl][:5])
    return psi, E0, st


def t_ref(root, n, Jz):
    import tn
    import hhmodel
    n = int(n); Jz = float(Jz)
    g = graph(n)
    t0 = time.time()
    psi, E, st = dmrg(g, Jz, CHI_REF[n], *SWEEPS[n])
    lab = tn.mps_labels(psi, g)
    wjson(O(root, "ref", "ref_n%d_J%s.json" % (n, js(Jz))),
          dict(n=n, Jz=Jz, E0=E, dmrg=st, labels=lab, secs=time.time() - t0, chi=CHI_REF[n]))
    if Jz in GS_JZ[n]:
        os.makedirs(Dd(root), exist_ok=True)
        hhmodel.save_pkl(psi, Dd(root, "gs_n%d_J%s.pkl" % (n, js(Jz))))
    print("ref", n, Jz, E, lab["m_s"], "%.0fs" % (time.time() - t0))


def t_gap(root, n, Jz):
    n = int(n); Jz = float(Jz)
    g = graph(n)
    t0 = time.time()
    psi, E, st = dmrg(g, Jz, CHI_GAP[n], *SWEEPS[n], kind="sz_minus")
    wjson(O(root, "gap", "gap_n%d_J%s.json" % (n, js(Jz))), dict(n=n, Jz=Jz, E_sm1=E, dmrg=st,
                                                                  secs=time.time() - t0))
    print("gap", n, Jz, E)


def gap_of(root, n, Jz):
    p = O(root, "gap", "gap_n%d_J%s.json" % (n, js(Jz)))
    r = O(root, "ref", "ref_n%d_J%s.json" % (n, js(Jz)))
    if os.path.exists(p) and os.path.exists(r):
        return rjson(p)["E_sm1"] - rjson(r)["E0"], "ours_Sz-1"
    return IBM_GAP[n].get(round(Jz, 1)), "IBM_digitized"


# --------------------------------------------------------------------------------------------------------- Krylov
def t_krylov(root, n, Jz):
    import tn
    n = int(n); Jz = float(Jz)
    g = graph(n)
    per_k = KEXTRA[n].get(Jz, STD_SHOTS)
    rng = np.random.default_rng(seed("krylov", n, js(Jz)))
    S = dict(batch=np.array(KBATCH), std_batches=np.array(STD_SHOTS // KBATCH), per_k=np.array(per_k))
    info = []
    t0 = time.time()
    for k, psi, inf in tn.krylov_states(g, Jz, DT[n][round(Jz, 1)] if not TOY else 0.06, K, chi_max=KCHI):
        t1 = time.time()
        Ts = tn.export(psi)
        r = emu2.sample_mps(Ts, g["order"], tn.down_index(psi), per_k, rng, g["n"], batch=KBATCH, want_amp=False,
                            merge=False)
        S["B%d" % k] = r["B"]; S["c%d" % k] = r["count"]; S["b%d" % k] = r["batch"]
        std = r["batch"] < STD_SHOTS // KBATCH
        inf["n_unique_std"] = int(len(emu2.unique_rows(r["B"][std])[1]))
        nb = emu2.CSet(g["neel"][None, :], g["n"])
        inf["p_neel_std"] = float(r["count"][std][nb.contains(r["B"][std])].sum() / STD_SHOTS)
        inf["sample_secs"] = time.time() - t1
        info.append(inf)
        print("krylov", n, Jz, k, inf, flush=True)
    os.makedirs(Dd(root), exist_ok=True)
    np.savez(Dd(root, "krylov_n%d_J%s.npz" % (n, js(Jz))), **S)
    wjson(O(root, "krylov", "krylov_n%d_J%s.json" % (n, js(Jz))),
          dict(n=n, Jz=Jz, dt=DT[n].get(round(Jz, 1)), per_k=per_k, info=info, secs=time.time() - t0, fresh=True))


def t_kreuse(root, Jz):
    """n = 57: pilot3 raw Krylov samples (1e5 per circuit, uint64) -> this run's format (one batch per circuit)."""
    Jz = float(Jz)
    src = Dd(root, "p3", "krylov_J%s.npz" % js(Jz))
    d = np.load(src)
    S = dict(batch=np.array(100000), std_batches=np.array(1), per_k=np.array(100000))
    info = []
    for k in range(1, K + 1):
        raw = d["k%d" % k]
        u, c = np.unique(raw, return_counts=True)
        S["B%d" % k] = u.reshape(-1, 1); S["c%d" % k] = c.astype(np.int64); S["b%d" % k] = np.zeros(len(u), np.int32)
        info.append(dict(k=k, n_unique_std=int(len(u))))
    np.savez(Dd(root, "krylov_n57_J%s.npz" % js(Jz)), **S)
    wjson(O(root, "krylov", "krylov_n57_J%s.json" % js(Jz)),
          dict(n=57, Jz=Jz, dt=DT[57].get(round(Jz, 1)), per_k=100000, info=info, fresh=False,
               source="pilot3 r4_20261029T211913Z data/krylov_J%s.npz (sha256 in out/p3_import.txt)" % js(Jz)))
    print("kreuse", Jz, [x["n_unique_std"] for x in info])


def krylov_shots(root, n, Jz, nb=None):
    """Per-circuit shot arrays (one row per shot) from the first nb batches (default: the published 1e5)."""
    d = np.load(Dd(root, "krylov_n%d_J%s.npz" % (n, js(Jz))))
    nb = int(d["std_batches"]) if nb is None else nb
    out = []
    for k in range(1, K + 1):
        sel = d["b%d" % k] < nb
        out.append(emu2.expand(d["B%d" % k][sel], d["c%d" % k][sel]))
    return out, int(d["batch"]), int(d["per_k"]) // int(d["batch"])


def subspace(shots, g, p, recovery, rng):
    """Noise (p_k = min(0.5, P_RO + p k / K); p < 0: no noise at all), unique, recovery or post-selection."""
    n = g["n"]
    parts = []
    for k, s in enumerate(shots, start=1):
        pk = 0.0 if p < 0 else min(0.5, P_RO + p * k / K)
        parts.append(emu2.add_noise(s, n, pk, rng))
    raw = np.concatenate(parts)
    Bu, _ = emu2.unique_rows(raw)
    insec = emu2.popcount(Bu) == g["n_down"]
    stats = dict(n_shots=int(len(raw)), n_unique=int(len(Bu)), n_unique_in_sector=int(insec.sum()))
    if recovery:
        cs = emu2.CSet(emu2.recover(Bu, n, g["n_down"], rng), n)
    else:
        cs = emu2.CSet(Bu[insec], n)
    stats["D"] = len(cs)
    return cs, stats


def rr(cs, g, Jz, v0=None):
    t0 = time.time()
    Hs = emu2.SubH(cs, g, Jz)
    E, a = emu2.ground(Hs, v0=emu2.neel_start(cs, g) if v0 is None else v0)
    return E, a, dict(nnz=Hs.nnz, rr_secs=time.time() - t0)


def evaluate(cs, a, E, g, ref, gap):
    lab = emu2.diag_labels(cs, a, g)
    return dict(E=E, ratio=(E - ref["E0"]) / gap if gap else None, dE_site=(E - ref["E0"]) / g["n"],
                labels=lab, err=emu2.label_errors(lab, ref["labels"]))


# ---------------------------------------------------------------------------------------------------- calibration
def t_calib(root, n):
    n = int(n)
    g = graph(n)
    ref = rjson(O(root, "ref", "ref_n%d_J%s.json" % (n, js(CALIB_JZ))))
    gap, gsrc = gap_of(root, n, CALIB_JZ)
    shots, _, _ = krylov_shots(root, n, CALIB_JZ)
    rows = []
    for p in P_GRID:
        rng = np.random.default_rng(seed("calib", n, p))
        t0 = time.time()
        cs, stats = subspace(shots, g, p, True, rng)
        E, a, info = rr(cs, g, CALIB_JZ)
        row = dict(p=p, E=E, ratio=(E - ref["E0"]) / gap, secs=time.time() - t0, **stats, **info)
        rows.append(row)
        print("calib", n, row, flush=True)
    ps = np.array(P_GRID)

    def match(vals, target, log=True):
        v = np.array(vals, float)
        for i in range(len(ps) - 1):
            if (v[i] - target) * (v[i + 1] - target) <= 0:
                if log and v[i] > 0 and v[i + 1] > 0:
                    f = (np.log(target) - np.log(v[i])) / (np.log(v[i + 1]) - np.log(v[i]))
                else:
                    f = (target - v[i]) / (v[i + 1] - v[i]) if v[i + 1] != v[i] else 0.0
                return float(ps[i] + f * (ps[i + 1] - ps[i])), "matched"
        st = "below_range" if (v[0] > target) == (not log or True) else "above_range"
        return float(ps[int(np.argmin(np.abs(v - target)))]), "no_crossing_" + st
    r = [x["ratio"] for x in rows]
    p_star, st_star = match(r, IBM_POST[n][CALIB_JZ])
    if st_star != "matched" and r[0] > IBM_POST[n][CALIB_JZ]:
        p_star, st_star = 0.0, "ideal_worse_than_target"      # declared fallback (as pilot3)
    p_dev, st_dev = match([x["n_unique_in_sector"] for x in rows], IBM_INSECTOR[n], log=False)
    out = dict(n=n, Jz=CALIB_JZ, gap=gap, gap_source=gsrc, rows=rows, target_post=IBM_POST[n][CALIB_JZ],
               p_star=p_star, status=st_star, target_insector=IBM_INSECTOR[n], p_dev=p_dev, status_dev=st_dev)
    if IBM_PRE[n].get(CALIB_JZ):
        out["p_pre"], out["status_pre"] = match(r, IBM_PRE[n][CALIB_JZ])
        out["target_pre"] = IBM_PRE[n][CALIB_JZ]
    wjson(O(root, "calib", "calib_n%d.json" % n), out)
    print("calib", n, "p*", p_star, st_star, "p_dev", p_dev, st_dev, "p_pre", out.get("p_pre"))


# ------------------------------------------------------------------------------------------------------ emulation
def t_emu(root, n, Jz):
    n = int(n); Jz = float(Jz)
    g = graph(n)
    ref = rjson(O(root, "ref", "ref_n%d_J%s.json" % (n, js(Jz))))
    cal = rjson(O(root, "calib", "calib_n%d.json" % n))
    gap, gsrc = gap_of(root, n, Jz)
    shots, batch, nbmax = krylov_shots(root, n, Jz)
    variants = [("ideal", -1.0, True), ("floor", 0.0, True)]
    if cal["p_star"] > 0:
        variants.append(("primary", cal["p_star"], True))
    variants += [("dev_ps", cal["p_dev"], False), ("dev_rec", cal["p_dev"], True)]
    if n == 57 and "p_pre" in cal and (Jz in PRE_JZ or TOY):
        variants.append(("pre", cal["p_pre"], True))
    out = dict(n=n, Jz=Jz, E0=ref["E0"], gap=gap, gap_source=gsrc, ref_m_s=ref["labels"]["m_s"],
               p_star=cal["p_star"], p_dev=cal["p_dev"], p_pre=cal.get("p_pre"), primary_alias=None, var={})
    t00 = time.time()
    for name, p, recov in variants:
        rng = np.random.default_rng(seed("emu", n, js(Jz), name))
        t0 = time.time()
        cs, stats = subspace(shots, g, p, recov, rng)
        E, a, info = rr(cs, g, Jz)
        res = evaluate(cs, a, E, g, ref, gap)
        res.update(p=p, recovery=recov, stats=stats, rr=info, secs=time.time() - t0)
        out["var"][name] = res
        if n == 57 and not TOY or (TOY and n == 57):
            for (jb, sub) in BO_SUBS:
                if abs(jb - Jz) < 1e-9 and (sub == name or (sub == "primary" and name == "floor"
                                                           and cal["p_star"] == 0)):
                    np.savez(Dd(root, "sub_n57_J%s_%s.npz" % (js(Jz), sub)), C=cs.B[:, 0], alpha=a, E=E)
        print("emu", n, Jz, name, stats, "ratio", res["ratio"], "dm_s %+.4f" % res["err"]["dm_s"],
              "%.0fs" % res["secs"], flush=True)
    if cal["p_star"] == 0:
        out["primary_alias"] = "floor"
        out["var"]["primary"] = dict(out["var"]["floor"], alias_of="floor")
    # Krylov shot scan (ideal and floor), nested batches of KBATCH shots per circuit
    if Jz in KSCAN[n] and nbmax > 1:
        allshots, _, nbm = krylov_shots(root, n, Jz, nb=10 ** 9)
        d = np.load(Dd(root, "krylov_n%d_J%s.npz" % (n, js(Jz))))
        scan = []
        for nb in range(1, nbm + 1):
            sh = []
            for k in range(1, K + 1):
                sel = d["b%d" % k] < nb
                sh.append(emu2.expand(d["B%d" % k][sel], d["c%d" % k][sel]))
            for name, p in (("ideal", -1.0), ("floor", 0.0)):
                rng = np.random.default_rng(seed("kscan", n, js(Jz), name, nb))
                cs, stats = subspace(sh, g, p, True, rng)
                E, a, info = rr(cs, g, Jz)
                res = evaluate(cs, a, E, g, ref, gap)
                res.update(variant=name, shots_per_circuit=nb * batch, stats=stats, rr=info)
                del res["labels"]["Czz"]
                scan.append(res)
                print("kscan", n, Jz, name, nb * batch, stats["D"], res["ratio"], "%+.4f" % res["err"]["dm_s"],
                      flush=True)
        out["kscan"] = scan
    out["secs"] = time.time() - t00
    wjson(O(root, "emu", "emu_n%d_J%s.json" % (n, js(Jz))), out)


# --------------------------------------------------------------------------------------------- ground-state scans
def sampling_state(root, n, Jz, g, ref):
    """Compressed copy of the DMRG reference for sampling (gate G5: fidelity >= 0.995, |dm_s| <= 2e-3)."""
    import tn
    import hhmodel
    psi = hhmodel.load_mps(Dd(root, "gs_n%d_J%s" % (n, js(Jz))))
    tried = []
    for chi_s in CHIS[n]:
        if chi_s >= max(psi.chi):
            tried.append(dict(chi_s=chi_s, used_reference=True))
            return psi, tried
        c = psi.copy()
        err = c.compress_svd({"chi_max": chi_s, "svd_min": 1e-14})
        c.norm = 1.0
        ov = complex(psi.overlap(c))
        F = abs(ov) ** 2
        lab = tn.mps_labels(c, g)
        dm = lab["m_s"] - ref["labels"]["m_s"]
        row = dict(chi_s=chi_s, fidelity=F, dm_s=dm, trunc_eps=float(err.eps), ok=bool(F >= 0.995 and abs(dm) <= 2e-3))
        tried.append(row)
        if row["ok"]:
            return c, tried
    tried.append(dict(chi_s=int(max(psi.chi)), used_reference=True))
    return psi, tried


def t_gsscan(root, n, Jz):
    import tn
    n = int(n); Jz = float(Jz)
    g = graph(n)
    ref = rjson(O(root, "ref", "ref_n%d_J%s.json" % (n, js(Jz))))
    gap, gsrc = gap_of(root, n, Jz)
    t0 = time.time()
    psi, tried = sampling_state(root, n, Jz, g, ref)
    Ts = tn.export(psi)
    Ts = [T.real if np.abs(T.imag).max() < 1e-14 else T for T in Ts]
    rng = np.random.default_rng(seed("gsscan", n, js(Jz)))
    Nmax = GS_NMAX[n][Jz]
    rows = []
    nb = 0
    ts = time.time()
    while nb * GBATCH < Nmax:
        r = emu2.sample_mps(Ts, g["order"], tn.down_index(psi), GBATCH, rng, g["n"], batch=GBATCH, merge=False)
        r["batch"][:] = nb
        rows.append(r)
        nb += 1
        el = time.time() - ts
        if el / nb * (nb + 1) > GS_TCAP[n] and nb * GBATCH < Nmax:
            print("gsscan time cap reached after %d batches" % nb, flush=True)
            break
    t_sample = time.time() - ts
    B = np.concatenate([r["B"] for r in rows]); cnt = np.concatenate([r["count"] for r in rows])
    bat = np.concatenate([r["batch"] for r in rows]); lp = np.concatenate([r["logp"] for r in rows])
    sg = np.concatenate([r["sign"] for r in rows]).real
    del rows
    N_done = nb * GBATCH
    ladder = [x for x in GS_LADDER if x <= N_done]
    if N_done not in ladder:
        ladder.append(N_done)
    out = dict(n=n, Jz=Jz, E0=ref["E0"], gap=gap, gap_source=gsrc, ref_m_s=ref["labels"]["m_s"],
               sampling_state=tried, N_done=N_done, N_max=Nmax, t_sample=t_sample, nested=[], topD=[])

    def one(cs, w_proj, counts, tag):
        t1 = time.time()
        Hs = emu2.SubH(cs, g, Jz)
        amp = np.exp(0.5 * w_proj[0]) * w_proj[1]
        Wcap = float(np.exp(w_proj[0]).sum())
        E_proj = Hs.energy(amp)
        E, a = emu2.ground(Hs, v0=amp / np.linalg.norm(amp))
        res = evaluate(cs, a, E, g, ref, gap)
        lab_p = emu2.diag_labels(cs, np.exp(w_proj[0]), g, weights=True)
        res.update(tag=tag, D=len(cs), W_captured=Wcap, nnz=Hs.nnz, secs=time.time() - t1,
                   proj=dict(E=E_proj, ratio=(E_proj - ref["E0"]) / gap if gap else None,
                             m_s=lab_p["m_s"], err=emu2.label_errors(lab_p, ref["labels"])))
        if counts is not None:
            lab_s = emu2.diag_labels(cs, counts.astype(float), g, weights=True)
            res["sample_mean"] = dict(m_s=lab_s["m_s"], dm_s=lab_s["m_s"] - ref["labels"]["m_s"])
        res["overlap_RR_proj"] = float(abs(a @ amp) / np.linalg.norm(amp))
        print("gsscan", n, Jz, tag, len(cs), "W %.4f" % Wcap, "ratio %.4f" % res["ratio"],
              "dm_s RR %+.4f proj %+.4f" % (res["err"]["dm_s"], res["proj"]["err"]["dm_s"]), "%.0fs" % res["secs"],
              flush=True)
        return res
    full = None
    for N in ladder:
        sel = bat < N // GBATCH
        Bu, _, c, lpu, sgu = emu2.unique_rows(B[sel], cnt[sel], lp[sel], sg[sel], reduce=["sum", "first", "first"])
        cs = emu2.CSet(Bu, g["n"], presorted=True)
        res = one(cs, (lpu, sgu), c, "N=%d" % N)
        res["N"] = N
        out["nested"].append(res)
        if N == ladder[-1]:
            full = (Bu, lpu, sgu)
        wjson(O(root, "gsscan", "gsscan_n%d_J%s.json" % (n, js(Jz))), out)
    Bu, lpu, sgu = full
    order = np.argsort(-lpu, kind="stable")
    for Dt in TOPD:
        if Dt > len(Bu) // 2:
            continue
        idx = order[:Dt]
        B2, _, l2, s2 = emu2.unique_rows(Bu[idx], lpu[idx], sgu[idx])
        cs = emu2.CSet(B2, g["n"], presorted=True)
        res = one(cs, (l2, s2), None, "top%d" % Dt)
        res["p_threshold"] = float(np.exp(lpu[order[Dt - 1]]))
        res["expected_hits_at_threshold"] = float(np.exp(lpu[order[Dt - 1]]) * N_done)
        out["topD"].append(res)
        wjson(O(root, "gsscan", "gsscan_n%d_J%s.json" % (n, js(Jz))), out)
    out["secs"] = time.time() - t0
    wjson(O(root, "gsscan", "gsscan_n%d_J%s.json" % (n, js(Jz))), out)


# ------------------------------------------------------------------------------------------- basis optimization
def t_bo(root, Jz, sub):
    import bo2
    Jz = float(Jz)
    g64 = bo2.graph64(graph(57)["G"])
    ref = rjson(O(root, "ref", "ref_n57_J%s.json" % js(Jz)))
    gap, gsrc = gap_of(root, 57, Jz)
    d = np.load(Dd(root, "sub_n57_J%s_%s.npz" % (js(Jz), sub)))
    rng = np.random.default_rng(seed("bo", js(Jz), sub))
    res = bo2.run_all(d["C"], d["alpha"], float(d["E"]), g64, Jz, ref, gap, rng, toy=bool(TOY))
    res.update(Jz=Jz, subspace=sub, gap=gap, gap_source=gsrc, E0=ref["E0"])
    wjson(O(root, "bo", "bo_J%s_%s.json" % (js(Jz), sub)), res)


# ------------------------------------------------------------------------------------------------ "+" witnesses
def t_wplus(root, n, Jz):
    import tn
    n = int(n); Jz = float(Jz)
    g = graph(n)
    G = g["G"]
    eta_mps = G["mps"]["eta"]
    chi = 128 if n == 57 else 160
    if TOY:
        chi = 32
    psi = None
    pts = []
    t0 = time.time()
    for lam in W_LAMS:
        field = [(-lam * eta_mps[k], [k]) for k in range(g["n"])]
        chi_list = {0: 32, 2: 64, 4: chi} if psi is None else {0: chi}
        psi, E, st = dmrg(g, Jz, chi_list, 3 if psi is not None else 6, 10, field=field, psi0=psi, max_hours=0.5)
        lab = tn.mps_labels(psi, g)
        Cbar = float(np.mean(lab["Czz"][:len(g["edges"])]))
        pts.append(dict(lam=lam, E=E, m_s=lab["m_s"], Czz_bar=Cbar, Z=lab["Z"], dmrg=st))
        print("wplus", n, Jz, lam, E, lab["m_s"], "%.0fs" % st["time_s"], flush=True)
        wjson(O(root, "wplus", "wplus_n%d_J%s.json" % (n, js(Jz))), dict(n=n, Jz=Jz, chi=chi, points=pts,
                                                                         secs=time.time() - t0))


# ------------------------------------------------------------------------------------------------------------ plan
def t_plan(root, path):
    T = []

    def add(tid, args, deps, prio, mem):
        T.append(dict(id=tid, args=args, deps=deps, prio=prio, mem=mem))
    big = 1 if TOY else 0
    m115 = 1 if TOY else 5
    first = [1.2, 2.5, 4.0]
    # references and gaps
    for n in (57, 115):
        for j in JZ[n]:
            pr = 1 if j in first else (3 if n == 115 else 2)
            if n == 115 and j in (1.3, 5.0):
                pr = 7
            add("ref_%d_%s" % (n, js(j)), ["ref", str(n), js(j)], [], pr, 2 if n == 57 else m115)
        for j in GAP_JZ[n]:
            add("gap_%d_%s" % (n, js(j)), ["gap", str(n), js(j)], [], 1 if j == CALIB_JZ else 4,
                2 if n == 57 else 4)
    # Krylov
    p3 = os.path.isdir(Dd(root, "p3"))
    for j in JZ[57]:
        if j in KFRESH57 or not p3 or not os.path.exists(Dd(root, "p3", "krylov_J%s.npz" % js(j))):
            add("krylov_57_%s" % js(j), ["krylov", "57", js(j)], [], 1 if j in first else 4, 2)
        else:
            add("krylov_57_%s" % js(j), ["kreuse", js(j)], [], 1, 1)
    for j in JZ[115]:
        pr = 1 if j in first else (3 if j in (1.1, 1.4, 1.6) else 4)
        if j in (1.3, 5.0):
            pr = 7
        add("krylov_115_%s" % js(j), ["krylov", "115", js(j)], [], pr, 3)
    for n in (57, 115):
        add("calib_%d" % n, ["calib", str(n)],
            ["ref_%d_%s" % (n, js(CALIB_JZ)), "krylov_%d_%s" % (n, js(CALIB_JZ)), "gap_%d_%s" % (n, js(CALIB_JZ))],
            2, 3 if n == 57 else 6)
        for j in JZ[n]:
            deps = ["ref_%d_%s" % (n, js(j)), "krylov_%d_%s" % (n, js(j)), "calib_%d" % n]
            if j in GAP_JZ[n]:
                deps.append("gap_%d_%s" % (n, js(j)))
            pr = 2 if j in first else (5 if n == 115 else 4)
            if n == 115 and j in (1.3, 5.0):
                pr = 7
            add("emu_%d_%s" % (n, js(j)), ["emu", str(n), js(j)], deps, pr, 4 if n == 57 else 7)
        for j in GS_JZ[n]:
            deps = ["ref_%d_%s" % (n, js(j))] + (["gap_%d_%s" % (n, js(j))] if j in GAP_JZ[n] else [])
            pr = 3 if j == 1.2 else (4 if j == 1.6 else 6)
            add("gsscan_%d_%s" % (n, js(j)), ["gsscan", str(n), js(j)], deps, pr, (6 if n == 57 else 8) - big * 5)
        for j in W_JZ[n]:
            add("wplus_%d_%s" % (n, js(j)), ["wplus", str(n), js(j)], [], 6 if n == 57 else (6 if j == 1.2 else 8),
                2 if n == 57 else 4)
    for (j, sub) in BO_SUBS:
        add("bo_%s_%s" % (js(j), sub), ["bo", js(j), sub], ["emu_57_%s" % js(j)], 6, 6)
    wjson(path, dict(tasks=T))
    print(len(T), "tasks; pilot3 Krylov data present:", p3)


if __name__ == "__main__":
    root, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    dict(ref=t_ref, gap=t_gap, krylov=t_krylov, kreuse=t_kreuse, calib=t_calib, emu=t_emu, gsscan=t_gsscan, bo=t_bo,
         wplus=t_wplus, plan=t_plan)[cmd](root, *args)
