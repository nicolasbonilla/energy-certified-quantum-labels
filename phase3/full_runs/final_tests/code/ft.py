"""Tasks of the final tests (DECLARATION.md). One task per process, run by sched_ft.py.

Test A (uniform model, method/code/fr.py unchanged, new couplings in its time-step table):
  ref <n> <Jz> | krylov <n> <Jz> | emu <n> <Jz>   fr.t_ref, fr.t_krylov, fr.t_emu
  n19 <Jz>                                         exact n = 19 truncated curve (bias_law/code/n19b.py procedure)
Test B (disordered couplings):
  btrain <Jz> <chunk> | bref <Jz> <i> | bkry <Jz> <i> | bpatch <Jz> <i> | bmodel <Jz> <site|bond>
Test C:
  crq <job> <Jz> <var>   device subspace vector, Rayleigh quotient and labels in exact arithmetic
  csim                   device-calibrated emulation at Jz = 4.0 (validation) and 6.0 (gate)
  cert <id>              new exact lower bound (rigor/lb_opt.py, rigor/verify_exact.py)
plan <plan.json>
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import warnings
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emu2  # noqa: E402
import fr  # noqa: E402
import ftlib as fl  # noqa: E402

# ----------------------------------------------------------------------------------------------------- declarations
A_JZ = {57: [1.5, 1.7, 2.8, 3.2], 115: [1.5, 1.7, 2.8]}
# time steps at couplings absent from the published table: linear interpolation between the neighbouring entries
DT_EXTRA = {57: {1.7: 0.06075, 2.8: 0.05856, 3.2: 0.05892}, 115: {1.7: 0.035275, 2.8: 0.03346}}
for _n, _d in DT_EXTRA.items():
    fr.DT[_n].update(_d)
B_JZ = [1.6, 2.5]
B_NTEST = 6
B_NTRAIN = 600
B_CHUNK = 25
B_DT = {1.6: 0.0622, 2.5: 0.0570}                 # fr.DT[57], published table
B_NOM = {1.6: 0.0248, 2.5: 0.0073}                # energy error per site of the uniform model (stored emulation)
B_WIN = {j: (B_NOM[j] / 5.0, B_NOM[j] * 5.0) for j in B_JZ}
C_SHOTS = 40000                                   # shots per circuit of the planned device job
C_SEEDS = 3
OPT = dict(K=32, maxiter=600, betas=[30, 300, 3000, 30000, 100000], use_mu=True)
CERTS = [("m_s", "6.0", -1, "297/1024", "eball2"), ("m_s", "6.0", -1, "317/1024", "eball2"),
         ("m_s", "6.0", -1, "338/1024", "eball2"), ("m_s", "6.0", 1, "614/1024", "vball2"),
         ("m_s", "6.0", 1, "819/1024", "vball2"), ("m_s", "6.0", 1, "1", "vball2")]


def O(root, *p):
    return os.path.join(root, "out", *p)


def IN(root, *p):
    return os.path.join(root, "inputs", *p)


def Dd(root, *p):
    return os.path.join(root, "data", *p)


wjson = fr.wjson
rjson = fr.rjson
js = fl.js


# ------------------------------------------------------------------------------------------------------------ Test A
def t_ref(root, n, Jz):
    fr.t_ref(root, n, Jz)


def t_krylov(root, n, Jz):
    fr.t_krylov(root, n, Jz)


def t_emu(root, n, Jz):
    fr.t_emu(root, n, Jz)


def t_n19(root, J):
    """bias_law/code/n19b.py, lines 15-31, for one coupling."""
    from scipy import sparse
    from scipy.sparse.linalg import eigsh
    import itertools
    J = float(J)
    G = fl.graph_json(3)
    n = G["n"]
    edges = [tuple(e) for e in G["edges"]]
    eta = np.array(G["eta"], float)
    nd = G["n_down"]
    cfg = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(n), nd)], dtype=np.int64)
    cfg.sort()
    dim = len(cfg)
    bits = ((cfg[:, None] >> np.arange(n)) & 1).astype(np.int8)
    Zc = 1 - 2 * bits.astype(float)
    ZZ = sum(Zc[:, i] * Zc[:, j] for i, j in edges)
    rows, cols = [], []
    for i, j in edges:
        src = np.nonzero(bits[:, i] != bits[:, j])[0]
        rows.append(src)
        cols.append(np.searchsorted(cfg, cfg[src] ^ ((1 << i) | (1 << j))))
    rows = np.concatenate(rows)
    cols = np.concatenate(cols)
    Hxy = sparse.csr_matrix((0.5 * np.ones(len(rows)), (rows, cols)), shape=(dim, dim))
    Ds = sorted(set(int(x) for x in np.round(np.logspace(0.7, np.log10(dim * .9), 26))))
    H = Hxy + sparse.diags(J / 4 * ZZ)
    w, v = eigsh(H, k=1, which='SA', tol=1e-10)
    E0 = float(w[0])
    psi = v[:, 0]
    ms0 = float(((psi ** 2) @ Zc) @ eta / n)
    order = np.argsort(-psi ** 2)
    out = []
    for D in Ds:
        B = np.sort(order[:D])
        Hb = H[B][:, B]
        if D < 400:
            ww, vv = np.linalg.eigh(Hb.toarray())
        else:
            ww, vv = eigsh(Hb, k=1, which='SA', tol=1e-8)
        x = vv[:, 0]
        out.append(((float(ww[0]) - E0) / n, float(((x ** 2) @ Zc[B]) @ eta / n) - ms0))
    wjson(O(root, "n19", "curve_J%s.json" % js(J)), dict(J=J, E0=E0, ms0=ms0, curve=sorted(out)))
    print("n19", J, E0, ms0)


# ------------------------------------------------------------------------------------------------------------ Test B
def DisModel(G, Jz, J):
    """hhmodel.HHModel with a coupling J_e per edge of G['edges']."""
    from tenpy.networks.site import SpinHalfSite
    from tenpy.models.lattice import Chain
    from tenpy.models.model import CouplingModel, MPOModel

    class _M(CouplingModel, MPOModel):
        def __init__(self):
            n = G["n"]
            site = SpinHalfSite(conserve="Sz")
            lat = Chain(n, site, bc="open", bc_MPS="finite")
            CouplingModel.__init__(self, lat)
            pos = {v: k for k, v in enumerate(G["order"])}
            for (a, b), x in zip(G["edges"], J):
                i, j = sorted((pos[int(a)], pos[int(b)]))
                self.add_coupling_term(0.5 * float(x), i, j, "Sp", "Sm")
                self.add_coupling_term(0.5 * float(x), i, j, "Sm", "Sp")
                self.add_coupling_term(float(Jz) * float(x), i, j, "Sz", "Sz")
            MPOModel.__init__(self, lat, self.calc_H_MPO())
    return _M()


def dmrg_d(g, Jz, J, chi_list, min_sweeps, max_sweeps, psi0=None, max_hours=1.5):
    """fr.dmrg with disordered couplings (same options)."""
    import hhmodel
    from tenpy.algorithms import dmrg as tdmrg
    G = g["G"]
    M = DisModel(G, Jz, J)
    psi = psi0 if psi0 is not None else hhmodel.new_mps(M, hhmodel.product_state(G, "neel"))
    opts = hhmodel.dmrg_opts(chi_list=chi_list, min_sweeps=min_sweeps, max_sweeps=max_sweeps, max_E_err=1e-9,
                             max_hours=max_hours)
    opts["max_trunc_err"] = 1e-2
    t0 = time.time()
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        eng = tdmrg.TwoSiteDMRGEngine(psi, M, opts)
        E, psi = eng.run()
    ss = eng.sweep_stats
    nt = float(np.linalg.norm(psi.norm_test()))
    if nt > 1e-10:
        psi.canonical_form()
    E0 = float(np.real(M.H_MPO.expectation_value(psi)))
    st = dict(E_dmrg=float(E), E_H=E0, sweeps=int(eng.sweeps), time_s=time.time() - t0,
              E_sweeps=[float(x) for x in ss["E"]], chi_sweeps=[int(x) for x in ss["max_chi"]],
              dE_last=float(ss["Delta_E"][-1]) if ss["Delta_E"] else None,
              max_trunc_err=float(np.max(ss["max_trunc_err"])) if ss["max_trunc_err"] else None,
              last_trunc_err=float(ss["max_trunc_err"][-1]) if ss["max_trunc_err"] else None,
              chi_max_reached=int(max(psi.chi)), norm_test_before=nt, warnings=[str(w.message)[:200] for w in wl][:5])
    return psi, E0, st


def dis_krylov_states(g, Jz, J, dt, K, chi_max=128, nsub=2, svd_min=1e-12):
    """tn.krylov_states with disordered couplings (same options)."""
    import hhmodel
    from tenpy.algorithms.mpo_evolution import ExpMPOEvolution
    G = g["G"]
    M = DisModel(G, Jz, J)
    psi = hhmodel.new_mps(M, hhmodel.product_state(G, "neel"))
    for k in range(len(psi._B)):
        psi._B[k] = psi._B[k].astype(np.complex128)
    opts = {"dt": dt / nsub, "N_steps": nsub, "order": 2, "approximation": "II", "compression_method": "SVD",
            "trunc_params": {"chi_max": chi_max, "svd_min": svd_min}}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        eng = ExpMPOEvolution(psi, M, opts)
        for k in range(1, K + 1):
            t0 = time.time()
            eng.run()
            yield k, psi, dict(t=float(eng.evolved_time), chi=int(max(psi.chi)), secs=time.time() - t0,
                               trunc=float(eng.trunc_err.eps))


def t_btrain(root, Jz, chunk):
    Jz = float(Jz)
    chunk = int(chunk)
    win = B_WIN[Jz]
    rows = []
    t0 = time.time()
    for idx in range(chunk * B_CHUNK, (chunk + 1) * B_CHUNK):
        inst = fl.train_instance(Jz, idx)
        ex = fl.solve_exact(inst, Jz)
        top = fl.topD_levels(ex, inst, win)
        kry = fl.krylov_levels(ex, inst, Jz, B_DT[Jz], win, fl.rng_of("B", "krylov19", js(Jz), idx))
        pe = fl.patch_estimates(inst, Jz, 13)
        rows.append(dict(idx=idx, n=inst["n"], E0=ex["E0"], Z=ex["Z"].tolist(), C=ex["C"].tolist(), e=ex["e"].tolist(),
                         top=top, kry=kry, patch13=pe))
        print("btrain", Jz, idx, "E0 %.5f top %d kry %d %.1fs" % (ex["E0"], len(top), len(kry), time.time() - t0), flush=True)
    wjson(O(root, "b", "train_J%s_c%03d.json" % (js(Jz), chunk)), dict(Jz=Jz, chunk=chunk, rows=rows, secs=time.time() - t0))


def t_bref(root, Jz, i):
    import tn
    Jz = float(Jz)
    i = int(i)
    g = fr.graph(57)
    inst = fl.test_instance(Jz, i)
    assert [tuple(int(v) for v in e) for e in g["G"]["edges"]] == inst["edges"]
    J = inst["J"]
    t0 = time.time()
    res = dict(Jz=Jz, i=i, J=J.tolist(), low={})
    psi, E200, st = dmrg_d(g, Jz, J, fr.CHI_REF[57], *fr.SWEEPS[57])
    res.update(E200=E200, dmrg200=st, labels200=tn.mps_labels(psi, g))
    wjson(O(root, "b", "ref_J%s_%d.json" % (js(Jz), i)), res)
    psi, E320, st = dmrg_d(g, Jz, J, {0: 320}, 4, 8, psi0=psi)
    res.update(E320=E320, dmrg320=st, labels320=tn.mps_labels(psi, g))
    wjson(O(root, "b", "ref_J%s_%d.json" % (js(Jz), i)), res)
    for chi, cl in ((32, {0: 32}), (64, {0: 32, 2: 64})):
        p, E, st = dmrg_d(g, Jz, J, cl, *fr.SWEEPS[57])
        res["low"][str(chi)] = dict(E=E, labels=tn.mps_labels(p, g), time_s=st["time_s"], sweeps=st["sweeps"])
    res["secs"] = time.time() - t0
    wjson(O(root, "b", "ref_J%s_%d.json" % (js(Jz), i)), res)
    print("bref", Jz, i, E200, E320, "%.0fs" % res["secs"])


def t_bkry(root, Jz, i):
    import tn
    Jz = float(Jz)
    i = int(i)
    g = fr.graph(57)
    inst = fl.test_instance(Jz, i)
    J = inst["J"]
    rng = fl.rng_of("B", "shots", js(Jz), i)
    shots, info = [], []
    t0 = time.time()
    for k, psi, inf in dis_krylov_states(g, Jz, J, B_DT[Jz], fr.K, chi_max=fr.KCHI):
        Ts = tn.export(psi)
        r = emu2.sample_mps(Ts, g["order"], tn.down_index(psi), fr.STD_SHOTS, rng, g["n"], batch=fr.KBATCH, want_amp=False,
                            merge=False)
        shots.append(emu2.expand(r["B"], r["count"]))
        info.append(inf)
        print("bkry", Jz, i, k, inf, flush=True)
    r2 = fl.rng_of("B", "floor", js(Jz), i)
    cs, stats = fr.subspace(shots, g, 0.0, True, r2)
    Hs = fl.SubHd(cs, g, Jz, J)
    E, a = emu2.ground(Hs, v0=emu2.neel_start(cs, g))
    lab = emu2.diag_labels(cs, a, g)
    wjson(O(root, "b", "emu_J%s_%d.json" % (js(Jz), i)),
          dict(Jz=Jz, i=i, E=E, labels=lab, stats=stats, info=info, nnz=Hs.nnz, secs=time.time() - t0))
    print("bkry", Jz, i, "E", E, stats, "%.0fs" % (time.time() - t0))


def t_bpatch(root, Jz, i):
    Jz = float(Jz)
    i = int(i)
    inst = fl.test_instance(Jz, i)
    t0 = time.time()
    p13 = fl.patch_estimates(inst, Jz, 13)
    p19 = fl.patch_estimates(inst, Jz, 19)
    wjson(O(root, "b", "patch_J%s_%d.json" % (js(Jz), i)), dict(Jz=Jz, i=i, p13=p13, p19=p19, secs=time.time() - t0))
    print("bpatch", Jz, i, "%.0fs" % (time.time() - t0))


def b_rows(root, Jz, typ):
    """Training tables of Test B. Returns dict of arrays; y in staggered form for sites (eta_i Z_i), plain for bonds."""
    feats = fl.site_features if typ == "site" else fl.bond_features
    L = dict(X=[], y=[], g=[], em=[], p13o=[], p13e=[], top=[], kry=[], Etr=[], Jv=[])
    for c in range(B_NTRAIN // B_CHUNK):
        for r in rjson(O(root, "b", "train_J%s_c%03d.json" % (js(Jz), c)))["rows"]:
            inst = fl.train_instance(Jz, r["idx"])
            F = feats(inst)
            s = inst["eta"].astype(float) if typ == "site" else np.ones(len(inst["edges"]))
            key = "Z" if typ == "site" else "C"
            y = s * np.array(r[key])
            L["X"].append(F)
            L["y"].append(y)
            L["g"].append(np.full(len(y), r["idx"]))
            pk = "Z_" if typ == "site" else "C_"
            L["p13o"].append(s * np.array(r["patch13"][pk + "open"]))
            L["p13e"].append(s * np.array(r["patch13"][pk + "emb"]))
            for fam in ("top", "kry"):
                lev = r[fam]
                if len(lev) > 8:                      # at most 8 levels per instance, evenly in the list (log of energy)
                    lev = [lev[int(q)] for q in np.round(np.linspace(0, len(lev) - 1, 8))]
                for v in lev:
                    L[fam].append((F, y, s * np.array(v[key]), v["de"], r["idx"]))
            if typ == "bond":
                L["em"].append(np.array(r["e"]))
                L["Jv"].append(inst["J"])
    out = dict(X=np.vstack(L["X"]), y=np.concatenate(L["y"]), g=np.concatenate(L["g"]), p13o=np.concatenate(L["p13o"]),
               p13e=np.concatenate(L["p13e"]))
    if typ == "bond":
        out["em"] = np.concatenate(L["em"])
    for fam in ("top", "kry"):
        out[fam] = L[fam]
    return out


def qmat(F, lab, de):
    """Inputs of the quantum-side model: local features, generated label, energy error per site (de: a number)."""
    d = np.full(len(lab), float(de))
    s = np.sqrt(np.maximum(d, 0.0))
    return np.column_stack([F, lab, s, d, lab * s, lab * d])


def t_bmodel(root, Jz, typ):
    import ftml
    Jz = float(Jz)
    t0 = time.time()
    T = b_rows(root, Jz, typ)
    res = dict(Jz=Jz, typ=typ, fits={}, test=[])
    mdl = {}

    def fit(name, X, y, g):
        mdl[name] = ftml.Model(fl.seed("B", "model", js(Jz), typ, name)).fit(X, y, g)
        res["fits"][name] = dict(best=mdl[name].best, cv=mdl[name].cv)
        print(name, mdl[name].best, "%.0fs" % (time.time() - t0), flush=True)
        wjson(O(root, "b", "model_J%s_%s.json" % (js(Jz), typ)), res)
    fit("reg", T["X"], T["y"], T["g"])
    fit("stack", np.c_[T["X"], T["p13o"], T["p13e"]], T["y"] - T["p13e"], T["g"])
    if typ == "bond":
        fit("bond_energy", T["X"], T["em"], T["g"])
    for fam in ("top", "kry"):
        rows = T[fam]
        Xq = np.vstack([qmat(F, lab, de) for F, y, lab, de, gi in rows])
        yq = np.concatenate([y - lab for F, y, lab, de, gi in rows])
        gq = np.concatenate([np.full(len(y), gi) for F, y, lab, de, gi in rows])
        fit("q_" + fam, Xq, yq, gq)
        del Xq, yq, gq
    feats = fl.site_features if typ == "site" else fl.bond_features
    key = "Z" if typ == "site" else "C"
    for i in range(B_NTEST):
        inst = fl.test_instance(Jz, i)
        ref = rjson(O(root, "b", "ref_J%s_%d.json" % (js(Jz), i)))
        emu = rjson(O(root, "b", "emu_J%s_%d.json" % (js(Jz), i)))
        pat = rjson(O(root, "b", "patch_J%s_%d.json" % (js(Jz), i)))
        F = feats(inst)
        ne = len(inst["edges"])
        s = inst["eta"].astype(float) if typ == "site" else np.ones(ne)

        def lab(L):
            return s * np.array(L[key][:ne] if key == "C" else L[key])
        truth = lab({key: ref["labels320"]["Czz" if key == "C" else "Z"]})
        t200 = lab({key: ref["labels200"]["Czz" if key == "C" else "Z"]})
        gen = lab({key: emu["labels"]["Czz" if key == "C" else "Z"]})
        low = {c: lab({key: v["labels"]["Czz" if key == "C" else "Z"]}).tolist() for c, v in ref["low"].items()}
        pk = "Z_" if typ == "site" else "C_"
        o13, e13 = s * np.array(pat["p13"][pk + "open"]), s * np.array(pat["p13"][pk + "emb"])
        o19, e19 = s * np.array(pat["p19"][pk + "open"]), s * np.array(pat["p19"][pk + "emb"])
        E0 = ref["E320"]
        E0_patch = float(np.sum(pat["p19"]["e_emb"]))
        de = (emu["E"] - E0) / inst["n"]
        de_nr = max((emu["E"] - E0_patch) / inst["n"], 1e-6)
        row = dict(i=i, E0=E0, E_label=emu["E"], E0_patch=E0_patch, de=de, de_noref=de_nr, truth=truth.tolist(),
                   truth200=t200.tolist(), label=gen.tolist(), open13=o13.tolist(), emb13=e13.tolist(), open19=o19.tolist(),
                   emb19=e19.tolist(), reg=mdl["reg"].predict(F).tolist(), low=low,
                   stack=(e13 + mdl["stack"].predict(np.c_[F, o13, e13])).tolist())
        for fam in ("top", "kry"):
            row["q_" + fam] = (gen + mdl["q_" + fam].predict(qmat(F, gen, de))).tolist()
            row["q_%s_noref" % fam] = (gen + mdl["q_" + fam].predict(qmat(F, gen, de_nr))).tolist()
        if typ == "bond":
            row["E0_reg"] = float(np.sum(mdl["bond_energy"].predict(F)))
        res["test"].append(row)
    res["secs"] = time.time() - t0
    wjson(O(root, "b", "model_J%s_%s.json" % (js(Jz), typ)), res)
    print("bmodel done", Jz, typ, "%.0fs" % res["secs"])


# ------------------------------------------------------------------------------------------------------------ Test C
def qseed(*parts):
    return int.from_bytes(hashlib.sha256(("qpu|" + "|".join(str(p) for p in parts)).encode()).digest()[:8], "little")


def t_crq(root, job, Jz, var):
    Jz = float(Jz)
    g = fr.graph(57)
    raw = np.load(IN(root, "qpu_%s_raw_configs.npz" % job))
    shots = [raw["J%s_k%d" % (js(Jz), k)] for k in range(1, fr.K + 1)]
    all_ = np.concatenate([s.reshape(-1, 1) for s in shots]).astype(np.uint64)
    Bu, _ = emu2.unique_rows(all_)
    insec = emu2.popcount(Bu) == g["n_down"]
    rng = np.random.default_rng(qseed("recover", 57, js(Jz), "device_" + job, var))
    if var == "rec":
        cs = emu2.CSet(emu2.recover(Bu, g["n"], g["n_down"], rng), g["n"])
    else:
        cs = emu2.CSet(Bu[insec], g["n"])
    Hs = emu2.SubH(cs, g, Jz)
    E, a = emu2.ground(Hs, v0=emu2.neel_start(cs, g))
    ai = fl.round_vector(a)
    t0 = time.time()
    x = fl.exact_rq(cs, g, Fraction(js(Jz)), ai)
    lab = emu2.diag_labels(cs, a, g)
    out = dict(job=job, Jz=Jz, var=var, D=len(cs), n_unique=int(len(Bu)), n_unique_in_sector=int(insec.sum()),
               n_shots=int(len(all_)), E_float=E, E_exact=str(x["E"]), E_exact_float=float(x["E"]), m_s_exact=str(x["m_s"]),
               m_s_float=float(x["m_s"]), Czz_bar_exact=str(x["Czz_bar"]), Czz_bar_float=float(x["Czz_bar"]),
               den_bits=x["den_bits"], m_s_label=lab["m_s"], Czz_bar_label=float(np.mean(lab["Czz"][:len(g["edges"])])),
               Z=lab["Z"], secs=time.time() - t0,
               vector_sha256=hashlib.sha256(",".join(str(v) for v in ai).encode()).hexdigest())
    wjson(O(root, "c", "rq_%s_J%s_%s.json" % (job, js(Jz), var)), out)
    print("crq", job, Jz, var, E, float(x["E"]), float(x["m_s"]), float(x["Czz_bar"]), "%.0fs" % out["secs"])


def in_fraction(s, n, nd, p, rng):
    return float(np.mean(emu2.popcount(emu2.add_noise(s, n, p, rng)) == nd))


def calibrate_pk(shots, g, target):
    """Per circuit: the i.i.d. flip probability that reproduces the device's fraction of in-sector shots."""
    pk = []
    for k, (s, f) in enumerate(zip(shots, target), start=1):
        a, b = 0.0, 0.5
        for it in range(16):
            c = 0.5 * (a + b)
            v = in_fraction(s, g["n"], g["n_down"], c, fl.rng_of("C", "cal", k, it))
            if v > f:
                a = c
            else:
                b = c
        pk.append(0.5 * (a + b))
    return pk


def emu_pk(shots, g, pk, S, Jz, rng):
    parts = []
    for s, p in zip(shots, pk):
        idx = rng.permutation(len(s))[:S]
        parts.append(emu2.add_noise(s[idx], g["n"], p, rng))
    raw = np.concatenate(parts)
    Bu, _ = emu2.unique_rows(raw)
    insec = int((emu2.popcount(Bu) == g["n_down"]).sum())
    cs = emu2.CSet(emu2.recover(Bu, g["n"], g["n_down"], rng), g["n"])
    Hs = emu2.SubH(cs, g, Jz)
    E, a = emu2.ground(Hs, v0=emu2.neel_start(cs, g))
    lab = emu2.diag_labels(cs, a, g)
    return dict(E=E, D=len(cs), n_unique=int(len(Bu)), n_unique_in_sector=insec, m_s=lab["m_s"])


def t_csim(root):
    g = fr.graph(57)
    pubs = rjson(IN(root, "qpu_B_pubs.json"))
    ref = {j: rjson(IN(root, "ref_n57_J%s.json" % j)) for j in ("4.0", "6.0")}
    sh4, _, _ = fr.krylov_shots(root, 57, 4.0)
    sh6, _, _ = fr.krylov_shots(root, 57, 6.0)
    target = [pubs["J4.0_k%d" % k]["shots_in_sector"] / pubs["J4.0_k%d" % k]["shots"] for k in range(1, fr.K + 1)]
    pk = calibrate_pk(sh4, g, target)
    print("p_k", pk, flush=True)
    out = dict(target_in_sector=target, p_k=pk, rows=[], E0={j: ref[j]["E0"] for j in ref})
    wjson(O(root, "c", "sim.json"), out)
    for tag, sh, Jz, S in (("J4.0_S23000", sh4, 4.0, 23000), ("J6.0_S40000", sh6, 6.0, C_SHOTS), ("J6.0_S23000", sh6, 6.0, 23000)):
        for r in range(C_SEEDS):
            x = emu_pk(sh, g, pk, S, Jz, fl.rng_of("C", "sim", tag, r))
            x.update(tag=tag, Jz=Jz, S=S, seed_index=r, eps=x["E"] - ref[js(Jz)]["E0"])
            out["rows"].append(x)
            print(x, flush=True)
            wjson(O(root, "c", "sim.json"), out)


def t_cert(root, i):
    i = int(i)
    kind, Jz, sg, lam, lev = CERTS[i]
    d = O(root, "c", "certs")
    os.makedirs(d, exist_ok=True)
    jid = "ft_n57_%s_%s_s%+d_%s_%s" % (lev, kind, sg, Jz, lam.replace("/", "o"))
    task = dict(OPT, clusters=lev, kind=kind, Jz=Jz, sigma=sg, lam=lam)
    tp = os.path.join(d, jid + "_task.json")
    json.dump(task, open(tp, "w"), indent=1)
    gp = os.path.join(HERE, "graphs", "hh_d5.json")
    cp = os.path.join(d, jid + "_cert.json")
    subprocess.check_call([sys.executable, "-B", os.path.join(HERE, "rigor", "lb_opt.py"), gp, tp, cp])
    subprocess.check_call([sys.executable, "-B", os.path.join(HERE, "rigor", "verify_exact.py"), gp, cp, os.path.join(d, jid + "_ver.json")])


# -------------------------------------------------------------------------------------------------------------- plan
def t_plan(root, path):
    T = []

    def add(tid, args, deps, prio, mem):
        T.append(dict(id=tid, args=args, deps=deps, prio=prio, mem=mem))
    for j in ("4.0", "6.0"):
        add("krylov_57_" + j, ["krylov", "57", j], [], 1, 2)
    add("crq_B_rec", ["crq", "B", "4.0", "rec"], [], 1, 3)
    add("crq_B_ps", ["crq", "B", "4.0", "ps"], [], 1, 2)
    add("csim", ["csim"], ["krylov_57_4.0", "krylov_57_6.0"], 1, 6)
    for i, c in enumerate(CERTS):
        add("cert_%d" % i, ["cert", str(i)], [], 1, 3)
    for j in sorted(set(A_JZ[57]) | {1.6}):
        add("n19_%s" % js(j), ["n19", js(j)], [], 2, 2)
    for n in (115, 57):
        for j in A_JZ[n]:
            add("ref_%d_%s" % (n, js(j)), ["ref", str(n), js(j)], [], 2, 5 if n == 115 else 2)
            add("krylov_%d_%s" % (n, js(j)), ["krylov", str(n), js(j)], [], 2, 3 if n == 115 else 2)
            add("emu_%d_%s" % (n, js(j)), ["emu", str(n), js(j)], ["ref_%d_%s" % (n, js(j)), "krylov_%d_%s" % (n, js(j))], 2,
                7 if n == 115 else 4)
    add("ref_57_2.5", ["ref", "57", "2.5"], [], 2, 2)            # replication gate of the pipeline
    add("krylov_57_2.5", ["krylov", "57", "2.5"], [], 2, 2)
    add("emu_57_2.5", ["emu", "57", "2.5"], ["ref_57_2.5", "krylov_57_2.5"], 2, 4)
    for Jz in B_JZ:
        for i in range(B_NTEST):
            add("bref_%s_%d" % (js(Jz), i), ["bref", js(Jz), str(i)], [], 3, 4)
            add("bkry_%s_%d" % (js(Jz), i), ["bkry", js(Jz), str(i)], [], 3, 3)
            add("bpatch_%s_%d" % (js(Jz), i), ["bpatch", js(Jz), str(i)], [], 3, 2)
        for c in range(B_NTRAIN // B_CHUNK):
            add("btrain_%s_%03d" % (js(Jz), c), ["btrain", js(Jz), str(c)], [], 3, 2)
        deps = ["bref_%s_%d" % (js(Jz), i) for i in range(B_NTEST)] + ["bkry_%s_%d" % (js(Jz), i) for i in range(B_NTEST)] + \
               ["bpatch_%s_%d" % (js(Jz), i) for i in range(B_NTEST)] + \
               ["btrain_%s_%03d" % (js(Jz), c) for c in range(B_NTRAIN // B_CHUNK)]
        for typ in ("site", "bond"):
            add("bmodel_%s_%s" % (js(Jz), typ), ["bmodel", js(Jz), typ], deps, 4, 8)
    wjson(path, dict(tasks=T))
    print(len(T), "tasks")


if __name__ == "__main__":
    root, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    dict(ref=t_ref, krylov=t_krylov, emu=t_emu, n19=t_n19, btrain=t_btrain, bref=t_bref, bkry=t_bkry, bpatch=t_bpatch,
         bmodel=t_bmodel, crq=t_crq, csim=t_csim, cert=t_cert, plan=t_plan)[cmd](root, *args)
