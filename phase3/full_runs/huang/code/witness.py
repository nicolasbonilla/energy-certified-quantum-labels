"""Tasks of the Huang-benchmark certification run (phase3/full_runs/huang/DECLARATION.md). Run on the VM by sched.py
(a verbatim copy of full_runs/map/code/sched.py, which starts code/witness.py).

  python witness.py <root> edref   <L> <k>                 exact GS (sector ED), all C_ij, gate G2 (n = 20)
  python witness.py <root> edlab   <L> <k> <label>         exact witness ladder of one featured label (n = 20)
  python witness.py <root> edpairs <L> <k> <batch>         exact short ladders of a batch of pair labels (n = 20)
  python witness.py <root> ref     <L> <k>                 DMRG ground states chi_c = 256 -> 384 (E0 := chi 384)
  python witness.py <root> lab     <L> <k> <label>         DMRG witness ladder (chain bond dimension chi_c)
  python witness.py <root> chk     <L> <k> <label> <+|->   gate P2: chi = 384 re-run of G at the decisive lambda
  python witness.py <root> cold    <L> <k> <label> <+|->   gate P3: cold start at the decisive lambda
  python witness.py <root> lawscan <L> <k> <batch>         lambda_0 points (both signs) of a batch of nn-bond labels
  python witness.py <root> plan    <plan.json>
<root> holds code/, data_huang/, out/ and mps/. Every output JSON is written atomically.
Energies in the paper's units H = sum_b J_b sigma_i . sigma_j; labels C_ij = sigma_i . sigma_j / 3.
"""
import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lattice as LT  # noqa: E402
import chain as CH  # noqa: E402

INSTANCES = [(4, 1), (4, 2), (4, 3), (6, 1), (9, 1), (9, 2)]       # (L, dataset index k); n = 5L
ED_L = 4
DE_GRID = [1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3, 1e-2]               # intensive energy error (paper units)
DE_AIM_SHORT = [1e-3, 3e-3, 1e-2]                                   # aimed grid points of the ED pair ladders
DE_AIM_DMRG = [1e-3, 1e-2]                                          # aimed grid points of the DMRG ladders
TAU = 0.08                                                          # 0.06 x (4/3): half-width 3 % of the C range
EPS_CAP_FACTOR = 20.0                                               # never aim beyond 20 x n x 1e-2
FEATURED = ["Cnn", "Cd2", "Ccent", "Cfar"]                          # ED featured labels (n = 20)
FEATURED_DMRG = FEATURED + ["Cfix"]                                 # DMRG featured labels (Cfix = Ccent at L = 4)
ED_EXTRA = ["Cstag"]                                                # record-only average (n = 20)
AVERAGES = ["Cnn", "Cd2", "Cstag"]
N_MAX_ED_FEAT, N_MAX_ED_PAIR, N_MAX_DMRG = 16, 9, 8
CHI_C = {20: 256, 30: 256, 45: 256}                                 # chain bond dimension (toys: 64)


def chic_of(n):
    return CHI_C.get(int(n), 64)

CHI_REF = (384,)                                                    # reference ground state (E0 := chi 384)
CHI_CHK = 384                                                       # gate P2 bond dimension
PAIR_BATCH = 16
G1_INSTANCE = (4, 1)
G1_LABELS = ["Cnn", "Ccent", "Cfar"]
GATE_INSTANCE = (9, 1)
GATE_LABELS = ["Cnn", "Ccent"]
LAWSCAN_INSTANCE = (9, 1)
LAWSCAN_BATCH = 19


def jdump(path, obj):
    LT.write_json(path, obj)


def jload(path):
    with open(path) as f:
        return json.load(f)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lam_params(label):
    if label in AVERAGES:
        return 0.005, 6.4
    return 0.1, 25.6


def inst(root, L, k):
    return LT.load_instance(os.path.join(root, "data_huang"), int(L), int(k))


def pair_batches(L):
    """Deterministic batches of pair labels: nn bonds first (ITensor order), then the other pairs (i < j)."""
    nn = LT.nn_pair_labels(L)
    rest = [p for p in LT.all_pair_labels(L) if p not in set(nn)]
    allp = nn + rest
    return [allp[i:i + PAIR_BATCH] for i in range(0, len(allp), PAIR_BATCH)], len(nn)


def nn_batches(L):
    nn = LT.nn_pair_labels(L)
    return [nn[i:i + LAWSCAN_BATCH] for i in range(0, len(nn), LAWSCAN_BATCH)]


def targets_for(n, kind):
    grid = DE_GRID if kind == "ed_feat" else (DE_AIM_DMRG if kind == "dmrg" else DE_AIM_SHORT)
    return [(n * d, False) for d in grid]


# ----------------------------------------------------------------------------------------------- exact (n = 20)
_SEC = {}


def ed_setup(root, L, k):
    import ed_h
    I = inst(root, L, k)
    n = I["n"]
    if n not in _SEC:
        _SEC[n] = ed_h.Sector(n)
    sec = _SEC[n]
    Hm = sec.hamiltonian(I["bonds"], I["J"])
    return I, sec, Hm


def task_edref(root, L, k):
    import numpy as np
    L, k = int(L), int(k)
    t0 = time.time()
    I, sec, Hm = ed_setup(root, L, k)
    w, v, res = sec.lowest(Hm, 1e-13, k=2)
    psi = v[:, 0] / np.linalg.norm(v[:, 0])
    C = sec.all_corr(psi)
    n = I["n"]
    Cf = np.array(I["XX"])
    Cf3 = (np.array(I["XX"]) + np.array(I["YY"]) + np.array(I["ZZ"])) / 3.0
    off = ~np.eye(n, dtype=bool)
    E_from_C = sum(3.0 * c * C[i, j] for (i, j), c in zip(I["bonds"], I["J"]))
    szm, szv = sec.sz_moments(psi)
    labels = {}
    for lab in FEATURED + ED_EXTRA:
        P, Wt, S, ob = LT.label_pairs(L, lab)
        labels[lab] = float(sum(w_ * C[i, j] for (i, j), w_ in zip(P, Wt)) / S)
    out = dict(L=L, k=k, n=n, dim=sec.D, nup=sec.nup, E0=float(w[0]), E1_sector=float(w[1]), residual=res,
               E_from_C=float(E_from_C), E_file=I["E_file"], E_file_x2=2.0 * I["E_file"],
               dE_vs_file=float(w[0] - 2.0 * I["E_file"]),
               max_dC_vs_XX=float(np.abs(C - Cf)[off].max()), max_dC_vs_mean3=float(np.abs(C - Cf3)[off].max()),
               rms_dC_vs_XX=float(np.sqrt(np.mean((C - Cf)[off] ** 2))), sz_mean=szm, sz_var=szv,
               labels=labels, C=C.tolist(), time_s=time.time() - t0)
    jdump(os.path.join(root, "out", "ed", "ref_L%d_k%d.json" % (L, k)), out)
    print("edref L=%d k=%d E0=%.12f E1=%.6f 2E_file=%.10f max|dC|=%.2e t=%.0fs" % (
        L, k, w[0], w[1], 2 * I["E_file"], out["max_dC_vs_XX"], out["time_s"]), flush=True)


def ed_ladder(root, L, k, label, I, sec, Hm, kind):
    import ed_h
    ref = jload(os.path.join(root, "out", "ed", "ref_L%d_k%d.json" % (L, k)))
    E0 = ref["E0"]
    n = I["n"]
    P, Wt, S, ob = LT.label_pairs(L, label)
    import numpy as np
    C = np.array(ref["C"])
    o0 = float(sum(w_ * C[i, j] for (i, j), w_ in zip(P, Wt)) / S)
    G = sec.sdots(P, [w_ / 3.0 for w_ in Wt])
    solver = ed_h.LabelSolver(sec, Hm, G, S)
    lam0, lam_max = lam_params(label)
    t0 = time.time()

    def solve(sign, lam, why):
        r = solver.solve(sign, lam)
        r.pop("psi")
        r["F_lo"] = r["F"] - r["residual"]
        return r
    nmax = N_MAX_ED_FEAT if kind == "ed_feat" else N_MAX_ED_PAIR
    lad = CH.Ladder(solve, E0, o0, S, ob, TAU, lam0, lam_max, nmax)
    summ = lad.run(targets_for(n, kind), EPS_CAP_FACTOR * n * 1e-2)
    out = dict(L=L, k=k, n=n, label=label, kind=kind, method="ED", S=S, obounds=ob, E0=E0, o_GS=o0, tau=TAU,
               lam0=lam0, lam_max=lam_max, points=sorted(lad.points(), key=lambda p: (p["sign"], p["lam"])),
               log=lad.log, time_s=time.time() - t0, **summ)
    jdump(os.path.join(root, "out", "ed", "chains", "L%d_k%d_%s.json" % (L, k, label)), out)
    print("edlab L=%d k=%d %s o0=%.6f chi=%.5g eps_tau in/out=%s/%s law=%s pts=%s t=%.0fs" % (
        L, k, label, o0, summ["chi_two"], summ["eps_tau_in"], summ["eps_tau_out"], summ["eps_tau_law"],
        summ["n_points"], out["time_s"]), flush=True)


def task_edlab(root, L, k, label):
    L, k = int(L), int(k)
    I, sec, Hm = ed_setup(root, L, k)
    ed_ladder(root, L, k, label, I, sec, Hm, "ed_feat")


def task_edpairs(root, L, k, b):
    L, k, b = int(L), int(k), int(b)
    I, sec, Hm = ed_setup(root, L, k)
    batches, _ = pair_batches(L)
    for label in batches[b]:
        if os.path.exists(os.path.join(root, "out", "ed", "chains", "L%d_k%d_%s.json" % (L, k, label))):
            continue
        ed_ladder(root, L, k, label, I, sec, Hm, "ed_pair")


# ----------------------------------------------------------------------------------------------- DMRG (n = 30, 45; G1)
def sid_of(L, k, tag):
    return "L%dk%d_%s" % (L, k, tag)


def record_state(root, I, psi, tag, kind, M0, pairs_extra, extra=None, pkl=False, indep_pairs=None):
    """TeNPy-side evaluation (MPO energy, C on the label pairs) and the independent numpy evaluation (energy from the
    bond correlators, C on pairs_extra or on indep_pairs, norm, S^z moments) of one explicit state; npz kept."""
    import hmodel as HM
    import indep_eval_h as IE
    L, k, n = I["L"], I["k"], I["n"]
    sid = sid_of(L, k, tag)
    t0 = time.time()
    tev = HM.tenpy_eval(psi, M0, pairs_extra)
    meta = dict(n=n, L=L, k=k, sid=sid, kind=kind, tenpy=HM.TENPY_VERSION)
    if extra:
        meta.update({kk: v for kk, v in extra.items() if kk in ("label", "sign", "lam", "chi")})
    os.makedirs(os.path.join(root, "mps"), exist_ok=True)
    prefix = os.path.join(root, "mps", sid)
    Ts = HM.save_state(psi, prefix, meta, pkl=pkl)
    iev = IE.evaluate(Ts, HM.sz_basis(psi), I["bonds"], I["J"], indep_pairs if indep_pairs else pairs_extra)
    s2 = (n % 2)                                             # 2 S^z of the sector (0 or 1)
    rec = dict(sid=sid, L=L, k=k, n=n, kind=kind, tenpy=tev, indep=iev, npz=os.path.relpath(prefix + ".npz", root),
               npz_sha256=sha256(prefix + ".npz"), eval_time_s=time.time() - t0)
    if extra:
        rec.update(extra)
    rec["in_sector"] = bool(tev["total_charge_phys"] == [s2] and abs(iev["sz_var"]) < 1e-10
                            and abs(iev["sz_mean"] - 0.5 * s2) < 1e-10)
    rec["E"] = tev["E"]
    rec["agree"] = dict(dE=abs(tev["E"] - iev["E"]), dnorm_rel=abs(iev["norm"] / tev["overlap"] - 1.0),
                        dC=max([abs(tev["C"][kk] - iev["C"][kk]) for kk in tev["C"]] + [0.0]))
    jdump(os.path.join(root, "out", "states", sid + ".json"), rec)
    return rec


def label_value(rec, L, label, which="indep"):
    P, Wt, S, ob = LT.label_pairs(L, label)
    C = rec[which]["C"]
    return float(sum(w_ * C["%d_%d" % (i, j)] for (i, j), w_ in zip(P, Wt)) / S)


def eval_pairs(L, labels):
    ps = set()
    for lab in labels:
        P, _, _, _ = LT.label_pairs(L, lab)
        ps.update(tuple(sorted(p)) for p in P)
    return sorted(ps)


def task_ref(root, L, k):
    import hmodel as HM
    L, k = int(L), int(k)
    I = inst(root, L, k)
    n = I["n"]
    M = HM.HeisModel(n, I["bonds"], I["J"])
    pairs = eval_pairs(L, FEATURED_DMRG)
    psi = HM.new_mps(M, HM.neel_labels(n))
    res = dict(L=L, k=k, n=n, stages=[])
    svd_min = 1e-12
    chic = chic_of(n)
    steps = [c for c in (32, 64, 128) if c < chic] + [chic]
    grow = {2 * i: c for i, c in enumerate(steps)}
    stages = [("chi%d" % chic, HM.dmrg_opts(chi_list=grow, mixer=(1e-5, 2.0, 10), min_sweeps=12, max_sweeps=24,
                                            max_E_err=1e-9, max_S_err=1e-4, svd_min=svd_min, max_hours=2.0))]
    for chi in CHI_REF:                                      # staged growth from the previous state
        if chi > chic:
            stages.append(("chi%d" % chi, HM.dmrg_opts(chi_max=chi, mixer=(1e-6, 2.0, 2), min_sweeps=4,
                                                       max_sweeps=10, max_E_err=1e-9, max_S_err=1e-4,
                                                       svd_min=svd_min, max_hours=3.0)))
    allp = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for tag, opts in stages:
        psi, st = HM.run_dmrg(psi, M, opts)
        chi = int(tag[3:])
        last = tag == "chi%d" % CHI_REF[-1]
        rec = record_state(root, I, psi, "R1_" + tag, "gs", M, pairs, extra=dict(dmrg=st, chi=chi),
                           pkl=(chi == chic), indep_pairs=allp if last else None)
        res["stages"].append(dict(tag=tag, chi=chi, E=rec["E"], E_indep=rec["indep"]["E"], dmrg=st, sid=rec["sid"],
                                  in_sector=rec["in_sector"]))
        print("R1 %s L=%d k=%d E=%.12f sweeps=%d t=%.0fs" % (tag, L, k, rec["E"], st["sweeps"], st["time_s"]),
              flush=True)
    import numpy as np
    Cd = rec["indep"]["C"]
    dif = [abs(Cd["%d_%d" % (i, j)] - I["XX"][i][j]) for i in range(n) for j in range(i + 1, n)]
    res.update(E0=rec["E"], E_chic=[s["E"] for s in res["stages"] if s["chi"] == chic][0], chi_c=chic,
               E_file_x2=2.0 * I["E_file"], dE_vs_file=rec["E"] - 2.0 * I["E_file"], max_dC_vs_XX=float(max(dif)),
               rms_dC_vs_XX=float(np.sqrt(np.mean(np.square(dif)))),
               labels={lab: label_value(rec, L, lab) for lab in FEATURED_DMRG})
    res["dchi"] = abs(res["E_chic"] - res["E0"])
    jdump(os.path.join(root, "out", "refs", "ref_L%d_k%d.json" % (L, k)), res)


def chain_opts(n):
    import hmodel as HM
    return HM.dmrg_opts(chi_max=chic_of(n), mixer=(1e-6, 2.0, 2), min_sweeps=3, max_sweeps=8, max_E_err=1e-7,
                        max_S_err=1e-3, svd_min=1e-12, max_hours=2.0)


def model_for(I, label, sign, lam):
    import hmodel as HM
    P, Wt, S, ob = LT.label_pairs(I["L"], label)
    extra = HM.field_terms(P, Wt, sign, lam) if lam > 0 else None
    return HM.HeisModel(I["n"], I["bonds"], I["J"], extra)


def task_lab(root, L, k, label):
    import hmodel as HM
    L, k = int(L), int(k)
    I = inst(root, L, k)
    n = I["n"]
    ref = jload(os.path.join(root, "out", "refs", "ref_L%d_k%d.json" % (L, k)))
    E0 = ref["E0"]
    gs = jload(os.path.join(root, "out", "states", sid_of(L, k, "R1_chi%d" % CHI_REF[-1]) + ".json"))
    o0 = label_value(gs, L, label)
    P, Wt, S, ob = LT.label_pairs(L, label)
    M0 = HM.HeisModel(n, I["bonds"], I["J"])
    psi_start = HM.load_mps(os.path.join(root, "mps", sid_of(L, k, "R1_chi%d" % chic_of(n))))
    opts = chain_opts(n)
    pairs = eval_pairs(L, [label])
    lam0, lam_max = lam_params(label)
    psis = {+1: {}, -1: {}}
    t0 = time.time()

    def solve(sign, lam, why):
        if psis[sign]:
            near = min(psis[sign], key=lambda l: abs(math.log(l) - math.log(lam)))
            psi = psis[sign][near].copy()
        else:
            psi = psi_start.copy()
        M = model_for(I, label, sign, lam)
        psi, st = HM.run_dmrg(psi, M, opts)
        tag = "%s_%s_l%.6f" % (label, "p" if sign > 0 else "m", lam)
        rec = record_state(root, I, psi, tag, "witness", M0, pairs,
                           extra=dict(label=label, sign=sign, lam=lam, dmrg=st, step=why, chi=chic_of(n)))
        o = label_value(rec, L, label)
        F = rec["E"] - sign * lam * S * o
        psis[sign][lam] = psi
        if len(psis[sign]) > 4:
            far = max(psis[sign], key=lambda l: abs(math.log(l) - math.log(lam)))
            psis[sign].pop(far)
        print("lab L=%d k=%d %s%s lam=%.6f eps=%.6g o=%.6f sweeps=%d t=%.0fs [%s]" % (
            L, k, label, "+" if sign > 0 else "-", lam, rec["E"] - E0, o, st["sweeps"], st["time_s"], why), flush=True)
        return dict(lam=lam, E=rec["E"], o=o, F=F, F_dmrg=st["E_dmrg"], F_lo=F, sid=rec["sid"], sweeps=st["sweeps"],
                    time_s=st["time_s"], in_sector=rec["in_sector"], o_tenpy=label_value(rec, L, label, "tenpy"))
    lad = CH.Ladder(solve, E0, o0, S, ob, TAU, lam0, lam_max, N_MAX_DMRG)
    summ = lad.run(targets_for(n, "dmrg"), EPS_CAP_FACTOR * n * 1e-2)
    out = dict(L=L, k=k, n=n, label=label, kind="dmrg", method="DMRG", chi_c=chic_of(n), S=S, obounds=ob, E0=E0,
               o_GS=o0, tau=TAU, lam0=lam0, lam_max=lam_max, dchi=ref["dchi"],
               points=sorted(lad.points(), key=lambda p: (p["sign"], p["lam"])), log=lad.log,
               time_s=time.time() - t0, **summ)
    jdump(os.path.join(root, "out", "chains", "L%d_k%d_%s.json" % (L, k, label)), out)
    print(json.dumps({kk: out[kk] for kk in ("label", "chi_two", "eps_tau_in", "eps_tau_out", "eps_tau_law",
                                             "n_points", "time_s")}), flush=True)


def decisive_point(root, L, k, label, sg):
    ch = jload(os.path.join(root, "out", "chains", "L%d_k%d_%s.json" % (L, k, label)))
    sign = +1 if sg == "+" else -1
    e = ch["eps_tau_out"] or ch["eps_hi"]
    E = ch["E0"] + e
    pts = [p for p in ch["points"] if p["sign"] == sign]
    best = min(pts, key=lambda p: (E - p["F_lo"]) / (p["lam"] * ch["S"]))
    return ch, best, e


def task_chk(root, L, k, label, sg):
    import hmodel as HM
    L, k = int(L), int(k)
    sign = +1 if sg == "+" else -1
    I = inst(root, L, k)
    ch, pt, e = decisive_point(root, L, k, label, sg)
    lam = pt["lam"]
    M = model_for(I, label, sign, lam)
    M0 = HM.HeisModel(I["n"], I["bonds"], I["J"])
    psi = HM.load_mps(os.path.join(root, "mps", sid_of(L, k, "R1_chi%d" % chic_of(I["n"]))))
    opts = HM.dmrg_opts(chi_list={0: chic_of(I["n"]), 2: CHI_CHK}, mixer=(1e-6, 2.0, 2), min_sweeps=4,
                        max_sweeps=10, max_E_err=1e-9, max_S_err=1e-4, svd_min=1e-12, max_hours=3.0)
    psi, st = HM.run_dmrg(psi, M, opts)
    rec = record_state(root, I, psi, "chk%d_%s_%s" % (CHI_CHK, label, "p" if sign > 0 else "m"), "chk", M0,
                       eval_pairs(L, [label]), extra=dict(label=label, sign=sign, lam=lam, dmrg=st, chi=CHI_CHK))
    o = label_value(rec, L, label)
    Gchk = rec["E"] - sign * lam * ch["S"] * o
    out = dict(L=L, k=k, label=label, sign=sg, lam=lam, eps_decisive=e, chi_chk=CHI_CHK, G_c=pt["F"], G_chk=Gchk,
               dG=pt["F"] - Gchk, o_c=pt["o"], o_chk=o, sid=rec["sid"], dmrg=st)
    jdump(os.path.join(root, "out", "chk", "chk_L%d_k%d_%s_%s.json" % (L, k, label, sg)), out)
    print("chk L=%d k=%d %s%s lam=%.6f dG=%.3e" % (L, k, label, sg, lam, out["dG"]), flush=True)


def task_cold(root, L, k, label, sg):
    import hmodel as HM
    L, k = int(L), int(k)
    sign = +1 if sg == "+" else -1
    I = inst(root, L, k)
    n = I["n"]
    ch, pt, e = decisive_point(root, L, k, label, sg)
    lam = pt["lam"]
    M = model_for(I, label, sign, lam)
    M0 = HM.HeisModel(n, I["bonds"], I["J"])
    psi = HM.new_mps(M, HM.neel_labels(n))
    opts = HM.dmrg_opts(chi_list={0: 32, 2: 64, 4: 128, 6: chic_of(n)}, mixer=(1e-5, 2.0, 10), min_sweeps=12,
                        max_sweeps=24, max_E_err=1e-9, max_S_err=1e-4, svd_min=1e-12, max_hours=3.0)
    psi, st = HM.run_dmrg(psi, M, opts)
    rec = record_state(root, I, psi, "cold_%s_%s" % (label, "p" if sign > 0 else "m"), "cold", M0,
                       eval_pairs(L, [label]), extra=dict(label=label, sign=sign, lam=lam, dmrg=st, chi=chic_of(n)))
    o = label_value(rec, L, label)
    Fc = rec["E"] - sign * lam * ch["S"] * o
    out = dict(L=L, k=k, label=label, sign=sg, lam=lam, F_warm=pt["F"], F_cold=Fc, dF=Fc - pt["F"], o_warm=pt["o"],
               o_cold=o, flag_warm_stuck=bool(Fc < pt["F"] - 1e-5 * abs(pt["F"])), sid=rec["sid"], dmrg=st)
    jdump(os.path.join(root, "out", "cold", "cold_L%d_k%d_%s_%s.json" % (L, k, label, sg)), out)
    print("cold L=%d k=%d %s%s lam=%.6f dF=%.3e" % (L, k, label, sg, lam, out["dF"]), flush=True)


def task_lawscan(root, L, k, b):
    """lambda_0 = 0.1 points on both signs for a batch of nn-bond labels: chi_two and the law's delta e* only."""
    import hmodel as HM
    L, k, b = int(L), int(k), int(b)
    I = inst(root, L, k)
    n = I["n"]
    ref = jload(os.path.join(root, "out", "refs", "ref_L%d_k%d.json" % (L, k)))
    M0 = HM.HeisModel(n, I["bonds"], I["J"])
    psi_start = HM.load_mps(os.path.join(root, "mps", sid_of(L, k, "R1_chi%d" % chic_of(n))))
    opts = chain_opts(n)
    gs = jload(os.path.join(root, "out", "states", sid_of(L, k, "R1_chi%d" % CHI_REF[-1]) + ".json"))
    rows = []
    for label in nn_batches(L)[b]:
        P, Wt, S, ob = LT.label_pairs(L, label)
        lam0, _ = lam_params(label)
        o = {}
        for sign in (+1, -1):
            psi = psi_start.copy()
            psi, st = HM.run_dmrg(psi, model_for(I, label, sign, lam0), opts)
            rec = record_state(root, I, psi, "scan_%s_%s" % (label, "p" if sign > 0 else "m"), "scan", M0,
                               eval_pairs(L, [label]), extra=dict(label=label, sign=sign, lam=lam0, dmrg=st,
                                                                  chi=chic_of(n)))
            o[sign] = dict(o=label_value(rec, L, label), eps=rec["E"] - ref["E0"], sweeps=st["sweeps"])
        chi = (o[+1]["o"] - o[-1]["o"]) / (2 * lam0)
        rows.append(dict(label=label, o_GS=label_value(gs, L, label), lam0=lam0, chi_two=chi, plus=o[+1],
                         minus=o[-1], eps_tau_law=S * TAU ** 2 / (8 * chi) if chi > 0 else None))
        print("scan L=%d k=%d %s chi=%.5g" % (L, k, label, chi), flush=True)
    jdump(os.path.join(root, "out", "lawscan", "scan_L%d_k%d_b%d.json" % (L, k, b)), dict(rows=rows))


# ----------------------------------------------------------------------------------------------- plan
def make_plan(path):
    """Priorities (a higher number is dropped first; DECLARATION section 5):
    1: ED references; ED featured labels (Cnn, Cd2, Ccent, Cfar) of the three n = 20 instances; DMRG references and
       the Cnn and Ccent rows of n = 30 and n = 45; gate G1 (DMRG Cnn, Ccent, Cfar at n = 20, instance (4, 1)).
    2: DMRG Cfar and Cfix rows (n = 30, 45), Cd2 rows of (6, 1) and (9, 1); ED pair labels on the nn bonds (three
       n = 20 instances); gates P2, P3.
    3: ED Cstag (three n = 20 instances); ED all other pair labels of instance (4, 1); DMRG Cd2 of (9, 2).
    4: ED all other pair labels of instances (4, 2) and (4, 3).
    (The law-only scan task exists but is not planned.)"""
    T = []
    ids = set()

    def add(tid, args, deps, prio):
        assert tid not in ids, tid
        ids.add(tid)
        T.append(dict(id=tid, args=args, deps=deps, prio=prio))
    ed_inst = [(L, k) for (L, k) in INSTANCES if L == ED_L]
    dm_inst = [(L, k) for (L, k) in INSTANCES if L != ED_L]
    for (L, k) in dm_inst:                                   # longest first
        add("ref_L%d_k%d" % (L, k), ["ref", str(L), str(k)], [], 1)
    for (L, k) in ed_inst:
        add("edref_L%d_k%d" % (L, k), ["edref", str(L), str(k)], [], 1)
    L, k = G1_INSTANCE
    add("ref_L%d_k%d" % (L, k), ["ref", str(L), str(k)], [], 1)
    for (L, k) in dm_inst:
        for lab in ("Cnn", "Ccent"):
            add("lab_L%d_k%d_%s" % (L, k, lab), ["lab", str(L), str(k), lab], ["ref_L%d_k%d" % (L, k)], 1)
    for (L, k) in ed_inst:
        for lab in FEATURED:
            add("edlab_L%d_k%d_%s" % (L, k, lab), ["edlab", str(L), str(k), lab], ["edref_L%d_k%d" % (L, k)], 1)
    L, k = G1_INSTANCE
    for lab in G1_LABELS:
        add("lab_L%d_k%d_%s" % (L, k, lab), ["lab", str(L), str(k), lab], ["ref_L%d_k%d" % (L, k)], 1)
    for (L, k) in dm_inst:
        for lab in ("Cfar", "Cfix", "Cd2"):
            prio = 3 if (lab == "Cd2" and (L, k) == (9, 2)) else 2
            add("lab_L%d_k%d_%s" % (L, k, lab), ["lab", str(L), str(k), lab], ["ref_L%d_k%d" % (L, k)], prio)
    for (L, k) in ed_inst:
        batches, nnn = pair_batches(L)
        nb_nn = (nnn + PAIR_BATCH - 1) // PAIR_BATCH
        for b in range(len(batches)):
            prio = 2 if b < nb_nn else (3 if (L, k) == G1_INSTANCE else 4)
            add("edpairs_L%d_k%d_b%d" % (L, k, b), ["edpairs", str(L), str(k), str(b)], ["edref_L%d_k%d" % (L, k)],
                prio)
    L, k = GATE_INSTANCE
    for lab in GATE_LABELS:
        for s in "+-":
            dep = ["lab_L%d_k%d_%s" % (L, k, lab)]
            add("chk_L%d_k%d_%s_%s" % (L, k, lab, s), ["chk", str(L), str(k), lab, s], dep, 2)
            add("cold_L%d_k%d_%s_%s" % (L, k, lab, s), ["cold", str(L), str(k), lab, s], dep, 2)
    for (L, k) in ed_inst:
        add("edlab_L%d_k%d_Cstag" % (L, k), ["edlab", str(L), str(k), "Cstag"], ["edref_L%d_k%d" % (L, k)], 3)
    jdump(path, dict(tasks=T))
    print(len(T), "tasks")


def main(argv):
    root, task = argv[0], argv[1]
    a = argv[2:]
    f = dict(edref=task_edref, edlab=task_edlab, edpairs=task_edpairs, ref=task_ref, lab=task_lab, chk=task_chk,
             cold=task_cold, lawscan=task_lawscan)
    if task == "plan":
        make_plan(a[0])
    elif task in f:
        f[task](root, *a)
    else:
        raise SystemExit("unknown task " + task)


if __name__ == "__main__":
    main(sys.argv[1:])
