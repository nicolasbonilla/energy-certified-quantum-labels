"""Tasks of the certification MAP (phase3/full_runs/map/DECLARATION.md). Built on design/pilot2/code/witness.py (R2,
7f0d651e...) and phase3/pilot_witness/code/witness.py; every change is marked "MAP". Run on the VM by sched.py (which
starts code/witness.py; the file name is kept so that sched.py stays a verbatim copy).

  python witness.py <root> ref    <n> <Jz> <R1a|R1b|R2|R3|R4>
  python witness.py <root> thr    <n> <Jz>
  python witness.py <root> lab    <n> <Jz> <label>          both signs, law-guided multi-target ladder (MAP)
  python witness.py <root> cold   <n> <Jz> <label> <+|->     cold-start check at the decisive lambda (gate P3)
  python witness.py <root> chk    <n> <Jz> <label> <+|->     chi = 320 check of G at the decisive lambda (gate P2)
  python witness.py <root> minchi <n> <Jz> <label>           minimal-chi witnesses (chi 16, 32, 64; R1 item C5)
  python witness.py <root> g1     <Jz>                       n = 19 exact-diagonalization gate (G1)
  python witness.py <root> plan   <plan.json>
<root> holds code/ (with graphs/ and readings_declared.json), out/ and mps/. Every output JSON is written atomically.
Labels: m_s, Czz_bar (edge average of ZZ; field = shift of Jz), C2_bar (second-neighbour average), Z_bulk,
Z_boundary, Czz_edge (one edge), Z_loop (12-site Z string). Field: H - sign*lam*S*O with S = n, n_e, n_nn2 or 1.
"""
import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hull  # noqa: E402

D_OF_N = {19: 3, 57: 5, 115: 7}
DELTA = 1e-6
CHAIN_CHI = 160                                  # MAP: bond dimension of every witness-chain state
GRID = [1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.3, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0]
JSTAR_EXTRA = [3.2, 3.4]                         # MAP: extra points for J* (m_s and Czz_bar only)
LABELS = ["m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop"]
AVERAGES = ["m_s", "Czz_bar", "C2_bar"]
LOCALS = ["Z_bulk", "Z_boundary", "Czz_edge", "Z_loop"]
M_LO, M_UP = 0.8, 1.2                            # witness side / certificate side margins (pilot2)
DE_FLOOR = 0.012                                 # OOD (Jz < 1.6): declared conditional per-site floor (pilot)
TAU_FRAC = 0.06                                  # tau = 0.06 |O_GS| (interval of half-width 3 %)
A_COVER = 0.10                                   # a target energy is covered by a point within +-10 % of its eps
N_MAX_SIDE = 9                                   # evaluations per sign (lambda_0 included)
EPS_CAP_FACTOR = 20.0                            # never aim beyond 20 * eps_up
GATE_POINTS = [(57, 3.3), (57, 4.0), (115, 3.3), (115, 4.0)]     # P2 / P3 (decisive region of J*)
MINCHI_POINTS = [(57, 1.6), (57, 4.0), (115, 1.6)]
MINCHI_CHIS = [16, 32, 64]
G1_POINTS = [1.6, 4.0]
G1_LABELS = ["m_s", "Czz_bar", "Z_bulk"]


def jstr(Jz):
    return "%.1f" % float(Jz)


def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def rjson(path):
    with open(path) as f:
        return json.load(f)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class Ctx:
    def __init__(self, root, n):
        self.root = root
        self.n = n
        self.G = rjson(os.path.join(root, "code", "graphs", "hh_d%d.json" % D_OF_N[n]))
        self.out = os.path.join(root, "out")
        self.mps = os.path.join(root, "mps")
        os.makedirs(self.mps, exist_ok=True)

    def p(self, *a):
        return os.path.join(self.out, *a)


def dopts(**kw):
    """MAP: hhmodel.dmrg_opts plus max_trunc_err = None. TeNPy 1.1.0 otherwise raises when the last sweep's truncation
    error exceeds 1e-4, which happens at chi <= 160 near Jz = 1 (found in the toy dry run at chi = 16); the error is
    downgraded to a warning and the truncation errors are recorded with every state (dmrg.max_trunc_err,
    last_trunc_err). Exact evaluation makes witnesses insensitive to it; the outer side carries the margin dG."""
    import hhmodel as HM
    o = HM.dmrg_opts(**kw)
    o["max_trunc_err"] = None
    return o


def sid_of(n, Jz, tag):
    return "n%d_J%s_%s" % (n, jstr(Jz), tag)


# ----------------------------------------------------------------------------------------------- labels (MAP)
def field_scale(G, label):
    if label == "m_s":
        return float(G["n"])
    if label == "C2_bar":
        return float(len(G["mps"]["nn2"]))
    if label == "Czz_bar":
        return float(len(G["mps"]["edges"]))
    return 1.0


def model_for(G, Jz, label, sign, lam):
    """MAP: model of H - sign*lam*S*O. For Czz_bar, H - sign*lam*sum_e Z_iZ_j = H(Jz - 4*sign*lam) exactly."""
    import hhmodel as HM
    if lam == 0:
        return HM.HHModel(G, Jz)
    if label == "Czz_bar":
        return HM.HHModel(G, float(Jz) - 4.0 * sign * lam)
    return HM.HHModel(G, Jz, HM.field_for(G, label, sign, lam))


IKEY = {"m_s": "m_s", "Czz_bar": "Czz_bar", "C2_bar": "C2_bar", "Z_bulk": "Z_bulk", "Z_boundary": "Z_boundary",
        "Czz_edge": "Czz_edge_loc", "Z_loop": "Z_loop"}


def label_value(rec, label):
    """MAP: every label from the independent (numpy) evaluator; TeNPy agreement is recorded per state."""
    return rec["indep"][IKEY[label]]


def lam_params(G, Jz, label, sign):
    if label in AVERAGES:
        lam0 = 0.005
        if label == "Czz_bar":
            lam_max = (float(Jz) - 0.2) / 4.0 if sign > 0 else 2.0     # Jz' = Jz - 4 sign lam stays >= 0.2
        else:
            lam_max = 1.28
    else:
        lam0, lam_max = 0.1, 6.4
    return lam0, lam_max


# ----------------------------------------------------------------------------------------------- state recording
def record_state(C, psi, Jz, tag, kind, M0, extra=None, sector_s=None, pkl=True):
    import hhmodel as HM
    import indep_eval as IE
    G = C.G
    sid = sid_of(C.n, Jz, tag)
    s = G["sz"] if sector_s is None else sector_s
    t0 = time.time()
    tev = HM.tenpy_eval(psi, G, Jz, M0)
    meta = dict(n=G["n"], order=G["order"], Jz=float(Jz), sid=sid, kind=kind, tenpy=HM.TENPY_VERSION)
    if extra:
        meta.update({k: v for k, v in extra.items() if k in ("label", "sign", "lam", "chi")})
    prefix = os.path.join(C.mps, sid)
    Ts = HM.save_state(psi, prefix, meta, pkl=pkl)
    sz_basis = HM.site_basis_meta(psi)["sz_basis"]
    iev = IE.evaluate(Ts, G, float(Jz), sz_basis, s=s, full=True)
    rec = dict(sid=sid, n=C.n, Jz=float(Jz), kind=kind, sector_s=s, tenpy=tev, indep=iev,
               npz=os.path.relpath(prefix + ".npz", C.root), npz_sha256=sha256(prefix + ".npz"),
               eval_time_s=time.time() - t0)
    if extra:
        rec.update(extra)
    rec["in_sector"] = bool(tev["total_charge_phys"] == [int(round(2 * G["sz"]))] and iev["sector_var"] < 1e-12)
    rec["E"] = tev["E"]
    rec["agree"] = dict(dE=abs(tev["E"] - iev["E"]), dm=abs(tev["m_s"] - iev["m_s"]),
                        dnorm_rel=abs(iev["norm"] / tev["overlap"] - 1.0))
    wjson(C.p("states", sid + ".json"), rec)
    return rec


# ----------------------------------------------------------------------------------------------- references
def task_ref(root, n, Jz, kind):
    import hhmodel as HM
    n = int(n); Jz = float(Jz)
    C = Ctx(root, n)
    G = C.G
    M = HM.HHModel(G, Jz)
    res = dict(n=n, Jz=Jz, kind=kind, stages=[])
    big = n >= 57
    mh = 3.0 if n == 57 else (5.0 if n == 115 else 1.0)
    svd_min = 1e-10 if big else 1e-14
    if kind == "R1a":
        psi = HM.new_mps(M, HM.product_state(G, "neel"))
        if big:
            stages = [("chi160", dopts(chi_list={0: 32, 2: 64, 4: 128, 6: 160}, mixer=(1e-5, 2.0, 10),
                                               min_sweeps=12, max_sweeps=30, max_E_err=1e-10, svd_min=svd_min,
                                               max_hours=mh)),
                      ("chi320", dopts(chi_max=320, mixer=(1e-6, 2.0, 4), min_sweeps=6, max_sweeps=20,
                                               max_E_err=1e-10, svd_min=svd_min, max_hours=mh))]
        else:
            stages = [("chi512", dopts(chi_list={0: 32, 2: 64, 4: 128, 6: 256, 8: 512}, mixer=(1e-5, 2.0, 10),
                                               min_sweeps=12, max_sweeps=40, max_E_err=1e-13, svd_min=svd_min,
                                               max_hours=mh))]
        for tag, opts in stages:
            psi, st = HM.run_dmrg(psi, M, opts)
            rec = record_state(C, psi, Jz, "R1_" + tag, "gs", M, extra=dict(dmrg=st, chi=int(tag[3:])))
            res["stages"].append(dict(tag=tag, E=rec["E"], m_s=rec["tenpy"]["m_s"], dmrg=st, sid=rec["sid"]))
            print("R1 %s n=%d Jz=%s E=%.10f m_s=%.6f sweeps=%d t=%.0fs" % (tag, n, Jz, rec["E"], rec["tenpy"]["m_s"],
                                                                         st["sweeps"], st["time_s"]), flush=True)
    elif kind == "R1b":
        psi = HM.load_mps(os.path.join(C.mps, sid_of(n, Jz, "R1_chi320")))
        opts = dopts(chi_max=480, mixer=(1e-6, 2.0, 4), min_sweeps=6, max_sweeps=20, max_E_err=1e-10,
                            svd_min=svd_min, max_hours=mh)
        psi, st = HM.run_dmrg(psi, M, opts)
        rec = record_state(C, psi, Jz, "R1_chi480", "gs", M, extra=dict(dmrg=st, chi=480), pkl=False)
        res["stages"].append(dict(tag="chi480", E=rec["E"], m_s=rec["tenpy"]["m_s"], dmrg=st, sid=rec["sid"]))
        print("R1b n=%d Jz=%s E=%.10f t=%.0fs" % (n, Jz, rec["E"], st["time_s"]), flush=True)
    elif kind in ("R2", "R3", "R4"):
        # MAP: excited-state / other-sector references at chi <= 200 (both n); an under-converged (too high) energy
        # can only enlarge Delta_ours, i.e. E_up (conservative for certificates); E_lo uses min(Delta_ours, Delta_IBM)
        cold = dopts(chi_list={0: 32, 2: 64, 4: 128, 6: 200}, mixer=(1e-5, 2.0, 10), min_sweeps=14,
                            max_sweeps=24, max_E_err=1e-10, svd_min=svd_min, max_hours=mh)
        if n == 19:
            cold = dopts(chi_list={0: 32, 2: 64, 4: 128, 6: 256, 8: 512}, mixer=(1e-5, 2.0, 10), min_sweeps=14,
                                max_sweeps=30, max_E_err=1e-12, svd_min=svd_min, max_hours=mh)
        gs_tag = "R1_chi512" if n == 19 else "R1_chi320"
        if kind == "R2":
            gs = HM.load_mps(os.path.join(C.mps, sid_of(n, Jz, gs_tag)))
            psi = HM.new_mps(M, HM.product_state(G, "swap_edge"))
            psi, st = HM.run_dmrg(psi, M, cold, ortho=[gs])
            ov = abs(complex(gs.overlap(psi)))
            rec = record_state(C, psi, Jz, "R2_E1", "e1", M, extra=dict(dmrg=st, chi=200, overlap_with_gs=ov),
                               pkl=False)
        else:
            pk = "sz_minus" if kind == "R3" else "sz_plus"
            ds = -1 if kind == "R3" else +1
            psi = HM.new_mps(M, HM.product_state(G, pk))
            psi, st = HM.run_dmrg(psi, M, cold)
            rec = record_state(C, psi, Jz, kind + "_" + pk, "sz" + ("-" if ds < 0 else "+"), M,
                               extra=dict(dmrg=st, chi=200), sector_s=G["sz"] + ds, pkl=False)
        res["stages"].append(dict(tag=kind, E=rec["E"], dmrg=st, sid=rec["sid"]))
        print("%s n=%d Jz=%s E=%.10f t=%.0fs" % (kind, n, Jz, rec["E"], st["time_s"]), flush=True)
    else:
        raise ValueError(kind)
    wjson(C.p("refs", "ref_n%d_J%s_%s.json" % (n, jstr(Jz), kind)), res)


def state(C, Jz, tag):
    return rjson(C.p("states", sid_of(C.n, Jz, tag) + ".json"))


def readings(root):
    return rjson(os.path.join(root, "code", "readings_declared.json"))


def task_thr(root, n, Jz):
    """MAP thresholds (DECLARATION §2). Training points (Jz >= 1.6): eps_dig = r1 * gap1 (reading 1 of IBM's Fig. 2
    left / Fig. 4 left); E_lo = E0 + 0.8 r1 min(D_ours, gap1); E_up = E0 + 1.2 r1 max(D_ours, gap1) + dchi.
    OOD (Jz < 1.6, conditional floor): eps_dig = 0.012 n; E_lo = E0 + 0.8 * 0.012 n; E_up = E0 + 1.2 * 0.012 n + dchi.
    n = 19 (gate G1 only): the per-site window of n = 57 at the same Jz. D_ours = min of the computed in-sector E1 (R2)
    and S^z = s -+ 1 (R3, R4) gaps; dchi = |E0(chi 160) - E0(chi 320)| (n = 57, 115)."""
    n = int(n); Jz = float(Jz)
    C = Ctx(root, n)
    RD = readings(root)
    if n == 19:
        gs = state(C, Jz, "R1_chi512")
        E0 = gs["E"]
        e57 = RD["eps1"]["57_%s" % jstr(Jz)]
        ed = e57 * 19.0 / 57.0
        out = dict(n=n, Jz=Jz, E0=E0, eps_dig=ed, eps_lo=M_LO * ed, eps_up=M_UP * ed, dchi=0.0, gaps={},
                   rule="n = 19 gate: per-site window of n = 57", ood=False)
    else:
        gs = state(C, Jz, "R1_chi320")
        E0 = gs["E"]
        gaps = {}
        for tag, key in (("R2_E1", "in_sector"), ("R3_sz_minus", "sz_minus"), ("R4_sz_plus", "sz_plus")):
            p = C.p("states", sid_of(n, Jz, tag) + ".json")
            if os.path.exists(p):
                gaps[key] = rjson(p)["E"] - E0
        ours = min(gaps.values())
        dchi = abs(state(C, Jz, "R1_chi160")["E"] - E0)
        key = "%d_%s" % (n, jstr(Jz))
        if Jz >= 1.55:
            r1, g1 = RD["r1"][key], RD["gap1"][key]
            ed = r1 * g1
            eps_lo = M_LO * r1 * min(ours, g1)
            eps_up = M_UP * r1 * max(ours, g1) + dchi
            ood = False
            rule = "E_up = E0 + 1.2 r1 max(gaps) + dchi; E_lo = E0 + 0.8 r1 min(gaps); reading 1"
        else:
            r1, g1 = None, RD["gap1"].get(key)
            ed = DE_FLOOR * C.G["n"]
            eps_lo = M_LO * ed
            eps_up = M_UP * ed + dchi
            ood = True
            rule = "OOD conditional floor 0.012 per site, x0.8 / x1.2 (+dchi)"
        out = dict(n=n, Jz=Jz, E0=E0, gaps=gaps, gap_ours=ours, gap_ibm1=g1, r1=r1, dchi=dchi, eps_dig=ed,
                   eps_lo=eps_lo, eps_up=eps_up, ood=ood, rule=rule)
    out.update(E_lo=E0 + out["eps_lo"], E_up=E0 + out["eps_up"], E_dig=E0 + out["eps_dig"], gs_sid=gs["sid"],
               m_s_GS=gs["tenpy"]["m_s"])
    wjson(C.p("thr", "thr_n%d_J%s.json" % (n, jstr(Jz))), out)
    print(json.dumps(out))


# ----------------------------------------------------------------------------------------------- lab task (MAP)
def chain_opts(n):
    import hhmodel as HM
    return dopts(chi_max=CHAIN_CHI, mixer=(1e-6, 2.0, 2), min_sweeps=3, max_sweeps=10, max_E_err=1e-9,
                        svd_min=1e-10 if n > 19 else 1e-14, max_hours=1.5 if n <= 57 else 3.0)


def predict_lam(pts, E0, eps_t, chi_two, S, lam0, lam_max):
    """MAP: lambda expected to give <H> - E0 = eps_t on one side. pts: [(lam, E)] of that side. Log-log interpolation
    between the bracketing points; below the lowest point eps ~ lam^2; above the highest, the local log-log slope
    (clipped to [1, 4]; slope 2 from a single point) with at most a factor 100 step; with no usable point, the law
    eps = S*chi*lam^2/2."""
    good = sorted((l, E - E0) for l, E in pts if E - E0 > 1e-12)
    if not good:
        if chi_two and chi_two > 0:
            return min(lam_max, math.sqrt(2.0 * eps_t / (S * chi_two)))
        return min(lam_max, 2.0 * lam0)
    below = [p for p in good if p[1] <= eps_t]
    above = [p for p in good if p[1] > eps_t]
    if below and above:
        lo = max(below, key=lambda p: p[0])
        hi_c = [p for p in above if p[0] > lo[0]]
        if hi_c:
            hi = min(hi_c, key=lambda p: p[0])
            x0, x1 = math.log(lo[0]), math.log(hi[0])
            y0, y1 = math.log(lo[1]), math.log(hi[1])
            if y1 > y0:
                x = x0 + (math.log(eps_t) - y0) * (x1 - x0) / (y1 - y0)
                return min(lam_max, math.exp(x))
            return min(lam_max, math.sqrt(lo[0] * hi[0]))
    if not below:                                         # target under every point: eps ~ lam^2 from the lowest
        l1, e1 = min(good, key=lambda p: p[0])
        return min(lam_max, l1 * math.sqrt(eps_t / e1))
    top = sorted(good)[-2:]
    if len(top) == 2 and top[1][1] > top[0][1] and top[1][0] > top[0][0]:
        slope = (math.log(top[1][1]) - math.log(top[0][1])) / (math.log(top[1][0]) - math.log(top[0][0]))
        slope = max(1.0, min(4.0, slope))
    else:
        slope = 2.0
    l1, e1 = top[-1]
    lam = l1 * (eps_t / e1) ** (1.0 / slope)
    return min(lam_max, lam, 100.0 * l1)


def eps_tau_from(points_p, points_m, E0, o0, S, tau, eps_hi):
    """MAP (in-task, for the refinement only): eps where the two-sided width reaches tau, from the inner hull of the
    task's own points (GS + both chains) and from the Lagrange-dual outer bound of the chains. Returns (in, out)."""
    pool = [dict(sid="gs", E=E0, o=o0)] + [dict(sid="p%d" % k, E=p["E"], o=p["o"]) for k, p in enumerate(points_p)] + \
           [dict(sid="m%d" % k, E=p["E"], o=p["o"]) for k, p in enumerate(points_m)]

    def w_in(e):
        W = hull.width(pool, E0 + e)[0]
        return W if W is not None else 0.0

    def w_out(e):
        ub = [(E0 + e - p["F"]) / (p["lam"] * S) for p in points_p]
        lb = [(E0 + e - p["F"]) / (p["lam"] * S) for p in points_m]
        if not ub or not lb:
            return None
        return min(1.0, min(ub)) + min(1.0, min(lb))

    def solve(f, lo, hi):
        if f(hi) is None or f(hi) < tau:
            return None
        for _ in range(60):
            mid = math.sqrt(lo * hi)
            if f(mid) >= tau:
                hi = mid
            else:
                lo = mid
        return hi
    lo = 1e-9
    return solve(w_in, lo, eps_hi), solve(w_out, lo, eps_hi)


def task_lab(root, n, Jz, label):
    """MAP: one (n, Jz, label), both signs. Points: lambda_0 on both sides (small-field susceptibility chi); then per
    side the target energies eps_lo, eps_up and the law's first guess eps_tau_law = S tau^2/(8 chi) (capped at
    20 eps_up) are aimed at by log-log interpolation until each has a point within +-10 % (at most 2 tries; eps_lo is
    straddled: a point in [0.9, 1] and one in (1, 1.1] of it, at most 3 tries); then the eps_tau measured from the
    points (inner and outer) is straddled in the same way on each side, in up to two rounds (stop when inner and
    outer agree to 2 %). At most 9 evaluations per side."""
    import hhmodel as HM
    n = int(n); Jz = float(Jz)
    C = Ctx(root, n)
    G = C.G
    thr = rjson(C.p("thr", "thr_n%d_J%s.json" % (n, jstr(Jz))))
    E0 = thr["E0"]
    gs = state(C, Jz, "R1_chi512" if n == 19 else "R1_chi320")
    o0 = label_value(gs, label)
    tau = TAU_FRAC * abs(o0)
    S = field_scale(G, label)
    M0 = HM.HHModel(G, Jz)
    psi_gs = HM.load_mps(os.path.join(C.mps, gs["sid"]))
    opts = chain_opts(n)
    sides = {}
    for sg, sign in (("+", 1), ("-", -1)):
        lam0, lam_max = lam_params(G, Jz, label, sign)
        sides[sg] = dict(sign=sign, lam0=lam0, lam_max=lam_max, pts=[], psis={}, saturated=False,
                         cpath=C.p("chains", "chain_n%d_J%s_%s_%s.json" % (n, jstr(Jz), label, sg)))
    log = []
    t_task = time.time()

    def evaluate(sg, lam, why):
        sd = sides[sg]
        sign = sd["sign"]
        if any(abs(lam - p["lam"]) <= 1e-9 * max(1.0, lam) for p in sd["pts"]):
            return None
        if sd["psis"]:
            near = min(sd["psis"], key=lambda l: abs(math.log(l) - math.log(lam)))
            psi = sd["psis"][near].copy()
        else:
            psi = psi_gs.copy()
        M = model_for(G, Jz, label, sign, lam)
        psi, st = HM.run_dmrg(psi, M, opts)
        tag = "%s_%s_l%.6f" % (label, "p" if sign > 0 else "m", lam)
        rec = record_state(C, psi, Jz, tag, "witness", M0,
                           extra=dict(label=label, sign=sg, lam=lam, dmrg=st, step=why, chi=CHAIN_CHI), pkl=False)
        o = label_value(rec, label)
        F = rec["E"] - sign * lam * S * o
        pt = dict(lam=lam, E=rec["E"], eps=rec["E"] - E0, o=o, F=F, F_dmrg=st["E_dmrg"], sid=rec["sid"], step=why,
                  sweeps=st["sweeps"], time_s=st["time_s"], in_sector=rec["in_sector"])
        sd["pts"].append(pt)
        sd["psis"][lam] = psi
        if len(sd["psis"]) > 6:                          # keep memory bounded: drop the most distant warm start
            far = max(sd["psis"], key=lambda l: abs(math.log(l) - math.log(lam)))
            sd["psis"].pop(far)
        if lam >= sd["lam_max"] * (1 - 1e-12) and abs(o) > 0.995:
            sd["saturated"] = True
        print("lab n=%d Jz=%s %s%s lam=%.6f eps=%.6g o=%.6f sweeps=%d t=%.0fs [%s]" % (
            n, Jz, label, sg, lam, rec["E"] - E0, o, st["sweeps"], st["time_s"], why), flush=True)
        save_chain(sg)
        return pt

    def save_chain(sg):
        sd = sides[sg]
        wjson(sd["cpath"], dict(n=n, Jz=Jz, label=label, sign=sg, S=S, E0=E0, o_GS=o0, tau=tau, gs_sid=gs["sid"],
                                lam0=sd["lam0"], lam_max=sd["lam_max"], chain_chi=CHAIN_CHI,
                                eps_lo=thr["eps_lo"], eps_dig=thr["eps_dig"], eps_up=thr["eps_up"],
                                points=sorted(sd["pts"], key=lambda p: p["lam"]), saturated=sd["saturated"],
                                log=log))

    def cover(sg, eps_t):
        pts = sides[sg]["pts"]
        below = any(eps_t * (1 - A_COVER) <= p["eps"] <= eps_t for p in pts)
        above = any(eps_t < p["eps"] <= eps_t * (1 + A_COVER) for p in pts)
        return below, above

    def aim(sg, eps_t, why, chi_two, straddle=False, bias=1.0):
        """Aim at eps_t until a point lies within +-10 % (straddle: one point in [0.9, 1] eps_t AND one in (1, 1.1]
        eps_t, so that the inner mixture at eps_t is tight); at most 2 tries (3 when straddling)."""
        sd = sides[sg]
        for _ in range(3 if straddle else 2):
            below, above = cover(sg, eps_t)
            if (below and above) or (not straddle and (below or above)) or len(sd["pts"]) >= N_MAX_SIDE:
                return
            if sd["saturated"]:
                return
            goal = eps_t * bias
            if straddle and below:
                goal = eps_t * (1 + 0.5 * A_COVER)
            elif straddle and above:
                goal = eps_t * (1 - 0.5 * A_COVER)
            lam = predict_lam([(p["lam"], p["E"]) for p in sd["pts"]], E0, goal, chi_two, S, sd["lam0"], sd["lam_max"])
            pt = evaluate(sg, lam, why)
            if pt is None:
                return
            if lam >= sd["lam_max"] * (1 - 1e-12) and pt["eps"] < eps_t:
                log.append(dict(side=sg, note="lam_max reached below target", eps_t=eps_t))
                return

    # 1. lambda_0 on both sides; two-sided susceptibility
    for sg in ("+", "-"):
        evaluate(sg, sides[sg]["lam0"], "lam0")
    pp, pm = sides["+"]["pts"][0], sides["-"]["pts"][0]
    chi_two = (pp["o"] - pm["o"]) / (2.0 * sides["+"]["lam0"]) if sides["+"]["lam0"] == sides["-"]["lam0"] else None
    eps_tau_law = (S * tau ** 2 / (8.0 * chi_two)) if (chi_two and chi_two > 0) else None
    cap = EPS_CAP_FACTOR * thr["eps_up"]
    targets = [(thr["eps_lo"], True, 1.0), (thr["eps_up"], False, 1.03)]   # eps_up aimed 3 % above (inner mixture)
    if eps_tau_law:
        targets.append((min(cap, eps_tau_law), False, 1.0))  # first guess of eps_tau (often far from eps_lo)
    targets = sorted(targets)
    # 2. declared targets, ascending, per side (straddled at eps_lo: the witness-side headline)
    for sg in ("+", "-"):
        for e, strad, bias in targets:
            aim(sg, e, "target", chi_two, strad, bias)
    # 3. measured eps_tau, straddled on each side; two rounds (the first estimate can be coarse)
    eps_hi = max([p["eps"] for s in sides.values() for p in s["pts"]] + [cap])
    e_in, e_out = eps_tau_from(sides["+"]["pts"], sides["-"]["pts"], E0, o0, S, tau, eps_hi)
    for _ in range(2):
        e_mid = math.sqrt(e_in * e_out) if (e_in and e_out) else (e_in or e_out)
        if not e_mid:
            break
        for sg in ("+", "-"):
            aim(sg, e_mid, "tau", chi_two, True)
        e_in, e_out = eps_tau_from(sides["+"]["pts"], sides["-"]["pts"], E0, o0, S, tau, eps_hi)
        if e_in and e_out and e_in / e_out < 1.02:
            break
    summ = dict(n=n, Jz=Jz, label=label, S=S, E0=E0, o_GS=o0, tau=tau, chi_two=chi_two, eps_tau_law=eps_tau_law,
                eps_tau_in_task=e_in, eps_tau_out_task=e_out, targets=[t[0] for t in targets],
                n_points={sg: len(sides[sg]["pts"]) for sg in sides},
                saturated={sg: sides[sg]["saturated"] for sg in sides}, time_s=time.time() - t_task)
    for sg in ("+", "-"):
        save_chain(sg)
    prune(C, n, Jz, label, sides, thr, [e_in, e_out])
    wjson(C.p("labs", "lab_n%d_J%s_%s.json" % (n, jstr(Jz), label)), summ)
    print(json.dumps(summ), flush=True)


def prune(C, n, Jz, label, sides, thr, extra_eps):
    """MAP (DECLARATION §5, disk): only if out/sched/prune.txt contains '1'. Keeps the npz of the lambda_0 points and of
    the two points of each side nearest (in eps) to each of eps_lo, eps_dig, eps_up and the measured eps_tau; removes
    the other npz (their JSON keeps the values of both evaluators and the SHA-256 of the removed file)."""
    try:
        flag = open(os.path.join(C.out, "sched", "prune.txt")).read().strip() == "1"
    except OSError:
        flag = False
    if not flag:
        return
    keep = set()
    marks = [thr["eps_lo"], thr["eps_dig"], thr["eps_up"]] + [e for e in extra_eps if e]
    for sd in sides.values():
        pts = sd["pts"]
        if not pts:
            continue
        keep.add(pts[0]["sid"])
        for e in marks:
            for p in sorted(pts, key=lambda p: abs(p["eps"] - e))[:2]:
                keep.add(p["sid"])
        for p in pts:
            if p["sid"] in keep:
                continue
            sp = C.p("states", p["sid"] + ".json")
            rec = rjson(sp)
            npz = os.path.join(C.root, rec["npz"])
            if os.path.exists(npz):
                os.remove(npz)
                rec["npz_pruned"] = True
                wjson(sp, rec)


# ----------------------------------------------------------------------------------------------- gates P2 / P3 (MAP)
def decisive_point(C, n, Jz, label, sg):
    """The chain point whose dual line gives the outer bound at E_up (argmin over the side's points)."""
    thr = rjson(C.p("thr", "thr_n%d_J%s.json" % (n, jstr(Jz))))
    ch = rjson(C.p("chains", "chain_n%d_J%s_%s_%s.json" % (n, jstr(Jz), label, sg)))
    S = ch["S"]
    best = min(ch["points"], key=lambda p: (thr["E_up"] - p["F"]) / (p["lam"] * S))
    return thr, ch, best


def task_cold(root, n, Jz, label, sg):
    import hhmodel as HM
    n = int(n); Jz = float(Jz)
    sign = +1 if sg == "+" else -1
    C = Ctx(root, n)
    G = C.G
    thr, ch, pt = decisive_point(C, n, Jz, label, sg)
    lam = pt["lam"]
    M = model_for(G, Jz, label, sign, lam)
    M0 = HM.HHModel(G, Jz)
    psi = HM.new_mps(M, HM.product_state(G, "neel"))
    opts = dopts(chi_list={0: 32, 2: 64, 4: 128, 6: CHAIN_CHI}, mixer=(1e-5, 2.0, 10), min_sweeps=14,
                        max_sweeps=30, max_E_err=1e-10, svd_min=1e-10, max_hours=3.0)
    psi, st = HM.run_dmrg(psi, M, opts)
    rec = record_state(C, psi, Jz, "cold_%s_%s" % (label, "p" if sign > 0 else "m"), "cold", M0,
                       extra=dict(label=label, sign=sg, lam=lam, dmrg=st, chi=CHAIN_CHI), pkl=False)
    o = label_value(rec, label)
    Fc = rec["E"] - sign * lam * ch["S"] * o
    out = dict(n=n, Jz=Jz, label=label, sign=sg, lam=lam, F_warm=pt["F"], F_cold=Fc, dF=Fc - pt["F"],
               o_warm=pt["o"], o_cold=o, flag_warm_stuck=bool(Fc < pt["F"] - 1e-5 * abs(pt["F"])), sid=rec["sid"],
               dmrg=st)
    print("cold n=%d Jz=%s %s%s lam=%.6f F_warm=%.10f F_cold=%.10f dF=%.3e" % (n, Jz, label, sg, lam, pt["F"], Fc,
                                                                             Fc - pt["F"]), flush=True)
    wjson(C.p("cold", "cold_n%d_J%s_%s_%s.json" % (n, jstr(Jz), label, sg)), out)


def task_chk(root, n, Jz, label, sg):
    """MAP gate P2: chi = 320 ground state of H - sign lam S O at the decisive lambda, warm-started from the chi = 320
    ground state of H; dG = G(chi 160) - G(chi 320)."""
    import hhmodel as HM
    n = int(n); Jz = float(Jz)
    sign = +1 if sg == "+" else -1
    C = Ctx(root, n)
    G = C.G
    thr, ch, pt = decisive_point(C, n, Jz, label, sg)
    lam = pt["lam"]
    M = model_for(G, Jz, label, sign, lam)
    M0 = HM.HHModel(G, Jz)
    psi = HM.load_mps(os.path.join(C.mps, sid_of(n, Jz, "R1_chi320")))
    opts = dopts(chi_max=320, mixer=(1e-6, 2.0, 2), min_sweeps=4, max_sweeps=12, max_E_err=1e-10,
                        svd_min=1e-10, max_hours=3.0)
    psi, st = HM.run_dmrg(psi, M, opts)
    rec = record_state(C, psi, Jz, "chk320_%s_%s" % (label, "p" if sign > 0 else "m"), "chk320", M0,
                       extra=dict(label=label, sign=sg, lam=lam, dmrg=st, chi=320), pkl=False)
    o = label_value(rec, label)
    G320 = rec["E"] - sign * lam * ch["S"] * o
    out = dict(n=n, Jz=Jz, label=label, sign=sg, lam=lam, G160=pt["F"], G320=G320, dG=pt["F"] - G320, o160=pt["o"],
               o320=o, sid=rec["sid"], dmrg=st, eps_up=thr["eps_up"])
    print("chk n=%d Jz=%s %s%s lam=%.6f G160=%.10f G320=%.10f dG=%.3e" % (n, Jz, label, sg, lam, pt["F"], G320,
                                                                        pt["F"] - G320), flush=True)
    wjson(C.p("chk", "chk_n%d_J%s_%s_%s.json" % (n, jstr(Jz), label, sg)), out)


# ----------------------------------------------------------------------------------------------- minimal chi (MAP)
def task_minchi(root, n, Jz, label):
    """MAP (R1 item C5): for chi in 16, 32, 64 and both signs, ground states of H - sign lam S O at bond dimension chi,
    cold from the Neel state, with lambda bisected (log scale) so that the best state stays below E_lo (witness side);
    lambda = 0 included (the chi-limited ground state). At most 10 evaluations per (chi, sign)."""
    import hhmodel as HM
    n = int(n); Jz = float(Jz)
    C = Ctx(root, n)
    G = C.G
    thr = rjson(C.p("thr", "thr_n%d_J%s.json" % (n, jstr(Jz))))
    E0, Et = thr["E0"], thr["E_lo"]
    S = field_scale(G, label)
    M0 = HM.HHModel(G, Jz)
    res = dict(n=n, Jz=Jz, label=label, E0=E0, E_lo=Et, runs=[])
    for chi in MINCHI_CHIS:
        def run(sign, lam):
            M = model_for(G, Jz, label, sign, lam)
            psi = HM.new_mps(M, HM.product_state(G, "neel"))
            opts = dopts(chi_list={0: min(8, chi), 2: chi}, mixer=(1e-5, 2.0, 6), min_sweeps=8, max_sweeps=24,
                                max_E_err=1e-10, svd_min=1e-12, max_hours=1.0)
            psi, st = HM.run_dmrg(psi, M, opts)
            tag = "minchi%d_%s_%s_l%.6f" % (chi, label, "p" if sign > 0 else ("m" if sign < 0 else "0"), lam)
            rec = record_state(C, psi, Jz, tag, "minchi", M0,
                               extra=dict(label=label, sign="+" if sign > 0 else ("-" if sign < 0 else "0"), lam=lam,
                                          dmrg=st, chi=chi), pkl=False)
            return dict(lam=lam, E=rec["E"], eps=rec["E"] - E0, o=label_value(rec, label), sid=rec["sid"],
                        in_sector=rec["in_sector"], chi_reached=max(rec["tenpy"]["chi"]))
        gs = run(0, 0.0)
        res["runs"].append(dict(chi=chi, sign="0", points=[gs]))
        for sg, sign in (("+", 1), ("-", -1)):
            pts = []
            if gs["E"] <= Et:
                lam_lo, lam_hi = 0.0, None
                lam = lam_params(G, Jz, label, sign)[0] * 8
                for _ in range(10):
                    p = run(sign, lam)
                    pts.append(p)
                    if p["E"] <= Et:
                        lam_lo = lam
                    else:
                        lam_hi = lam
                    if lam_hi is None:
                        lam = min(lam * 2, lam_params(G, Jz, label, sign)[1])
                        if lam_lo >= lam_params(G, Jz, label, sign)[1]:
                            break
                    else:
                        if lam_lo > 0 and lam_hi / lam_lo < 1.02:
                            break
                        lam = math.sqrt(lam_lo * lam_hi) if lam_lo > 0 else lam_hi / 2
            res["runs"].append(dict(chi=chi, sign=sg, points=pts))
            print("minchi n=%d Jz=%s chi=%d %s: %d points" % (n, Jz, chi, sg, len(pts)), flush=True)
    wjson(C.p("minchi", "minchi_n%d_J%s_%s.json" % (n, jstr(Jz), label)), res)


# ----------------------------------------------------------------------------------------------- gate G1 (MAP)
def ed_diag(sec, G, label):
    import numpy as np
    if label == "m_s":
        return sec.M / G["n"], float(G["n"])
    if label == "Czz_bar":
        return sec.zz / len(G["edges"]), float(len(G["edges"]))
    if label == "Z_bulk":
        return sec.z[:, G["local"]["bulk_site"]].astype(float), 1.0
    raise ValueError(label)


class EDCurve:
    """Exact (sector ED) extremes of <O> at <H> <= E for one diagonal label and sign: ground states of
    H - sign*lam*S*O on a log grid of lam (cached), then bisection in lam inside the bracketing grid interval; the
    value at E is the mixture of the final bracket (exact energy E)."""
    def __init__(self, sec, H, diag, S, sign):
        import numpy as np
        self.sec, self.H, self.diag, self.S, self.sign = sec, H, diag, S, sign
        self.grid = [self.pt(l) for l in [0.0] + list(np.geomspace(1e-4, 64.0, 110))]

    def pt(self, lam):
        import numpy as np
        import scipy.sparse as sp
        A = (self.H - sp.diags(self.sign * lam * self.S * self.diag)).tocsr() if lam > 0 else self.H
        w, v, r = self.sec.lowest(A, 1, 1e-12)
        psi = v[:, 0]
        return (lam, float(psi @ (self.H @ psi)), float(np.dot(psi * psi, self.diag)))

    def extreme(self, E, refine=True):
        g = self.grid
        if E >= g[-1][1]:
            return g[-1][2]
        k = max(i for i in range(len(g)) if g[i][1] <= E)
        lo, hi = g[k], g[k + 1]
        if refine:
            for _ in range(30):
                if hi[1] - lo[1] < 1e-11:
                    break
                m = self.pt(0.5 * (lo[0] + hi[0]))
                if m[1] <= E:
                    lo = m
                else:
                    hi = m
        t = (E - lo[1]) / (hi[1] - lo[1]) if hi[1] > lo[1] else 0.0
        return (1 - t) * lo[2] + t * hi[2]


def task_g1(root, Jz):
    """MAP gate G1: n = 19, exact sector diagonalization of the information limit of m_s, Czz_bar and Z_bulk at
    E_lo, E_dig, E_up and at the exact eps_tau; compared with the lab tasks by analyze_map.py."""
    import ed
    import numpy as np
    Jz = float(Jz)
    C = Ctx(root, 19)
    G = C.G
    thr = rjson(C.p("thr", "thr_n19_J%s.json" % jstr(Jz)))
    sec = ed.Sector(G, G["n_up"])
    H = sec.H(Jz)
    w, v, r = sec.lowest(H, 1, 1e-13)
    E0 = float(w[0])
    out = dict(Jz=Jz, E0_ed=E0, E0_dmrg=thr["E0"], dim=sec.D, labels={})
    for label in G1_LABELS:
        diag, S = ed_diag(sec, G, label)
        o0 = float(np.dot(v[:, 0] ** 2, diag))
        tau = TAU_FRAC * abs(o0)
        cp, cm = EDCurve(sec, H, diag, S, +1), EDCurve(sec, H, diag, S, -1)
        rows = {}
        for key in ("eps_lo", "eps_dig", "eps_up"):
            E = E0 + thr[key]
            up, lo = cp.extreme(E), cm.extreme(E)
            rows[key] = dict(eps=thr[key], hi=up, lo=lo, w=up - lo)

        def wgrid(e):
            return cp.extreme(E0 + e, False) - cm.extreme(E0 + e, False)

        def wex(e):
            return cp.extreme(E0 + e) - cm.extreme(E0 + e)
        a, b = 1e-8, max(20 * thr["eps_up"], 1.0)
        et = None
        if wgrid(b) >= tau:
            for _ in range(60):
                m = math.sqrt(a * b)
                if wgrid(m) >= tau:
                    b = m
                else:
                    a = m
            xs = [b * f for f in (0.88, 0.94, 1.0, 1.04)]
            ws = [wex(x) for x in xs]
            for (x0, w0), (x1, w1) in zip(zip(xs, ws), zip(xs[1:], ws[1:])):
                if w0 <= tau <= w1 and w1 > w0:
                    et = x0 + (tau - w0) * (x1 - x0) / (w1 - w0)
            if et is None:
                et = b
        out["labels"][label] = dict(o_GS=o0, tau=tau, rows=rows, eps_tau=et)
        print("g1 Jz=%s %s o0=%.6f w_lo=%.6f w_up=%.6f eps_tau=%s" % (Jz, label, o0, rows["eps_lo"]["w"],
                                                                     rows["eps_up"]["w"], et), flush=True)
    wjson(C.p("g1", "g1_J%s.json" % jstr(Jz)), out)


# ----------------------------------------------------------------------------------------------- plan (MAP)
def make_plan(path):
    """Priorities (DECLARATION §3/§5; a higher number is dropped first): 1 references + m_s and Czz_bar rows (both n),
    G1; 2 C2_bar rows, R1b, gates P2/P3; 3 local rows n = 57, J* extra points, minimal chi; 4 n = 115 Z_bulk rows
    (Jz <= 4.5); 5 n = 115 Czz_edge and Z_boundary rows (Jz <= 4.5); 6 n = 115 Z_loop rows (Jz <= 4.5);
    7 n = 115 local rows at Jz = 5.0-6.0."""
    T = []
    ids = set()

    def add(tid, args, deps, prio):
        assert tid not in ids, tid
        ids.add(tid)
        T.append(dict(id=tid, args=args, deps=deps, prio=prio))

    def refs(n, J, prio, full=True):
        j = jstr(J)
        add("ref%d_R1a_%s" % (n, j), ["ref", str(n), j, "R1a"], [], prio)
        add("ref%d_R3_%s" % (n, j), ["ref", str(n), j, "R3"], [], prio)
        deps = ["ref%d_R1a_%s" % (n, j), "ref%d_R3_%s" % (n, j)]
        if full:
            add("ref%d_R2_%s" % (n, j), ["ref", str(n), j, "R2"], ["ref%d_R1a_%s" % (n, j)], prio)
            deps.append("ref%d_R2_%s" % (n, j))
            if n == 57:
                add("ref57_R4_%s" % j, ["ref", "57", j, "R4"], [], prio)
                deps.append("ref57_R4_%s" % j)
        add("thr%d_%s" % (n, j), ["thr", str(n), j], deps, prio)

    def lab(n, J, label, prio):
        j = jstr(J)
        add("lab%d_%s_%s" % (n, label, j), ["lab", str(n), j, label], ["thr%d_%s" % (n, j)], prio)

    # priority 1: references and the m_s / Czz_bar rows, n = 115 first (longest), then n = 57; gate G1
    for n in (115, 57):
        for J in GRID:
            refs(n, J, 1)
    for n in (115, 57):
        for J in GRID:
            for label in ("m_s", "Czz_bar"):
                lab(n, J, label, 1)
    for J in G1_POINTS:
        j = jstr(J)
        add("ref19_R1a_%s" % j, ["ref", "19", j, "R1a"], [], 1)
        add("thr19_%s" % j, ["thr", "19", j], ["ref19_R1a_%s" % j], 1)
        for label in G1_LABELS:
            lab(19, J, label, 1)
        add("g1_%s" % j, ["g1", j], ["thr19_%s" % j], 1)
    # priority 2: C2_bar rows (both n); R1b (n = 57) at five points; gates P2 / P3 at the J* region
    for n in (115, 57):
        for J in GRID:
            lab(n, J, "C2_bar", 2)
    for J in (1.2, 1.6, 3.3, 4.0, 6.0):
        add("ref57_R1b_%s" % jstr(J), ["ref", "57", jstr(J), "R1b"], ["ref57_R1a_%s" % jstr(J)], 2)
    for (n, J) in GATE_POINTS:
        for label in ("m_s", "Czz_bar"):
            for s in "+-":
                dep = ["lab%d_%s_%s" % (n, label, jstr(J))]
                add("chk%d_%s_%s_%s" % (n, label, s, jstr(J)), ["chk", str(n), jstr(J), label, s], dep, 2)
                if label == "m_s":
                    add("cold%d_%s_%s_%s" % (n, label, s, jstr(J)), ["cold", str(n), jstr(J), label, s], dep, 2)
    # priority 3: local rows at n = 57; J* extra points (m_s, Czz_bar, both n); minimal chi
    for J in GRID:
        for label in LOCALS:
            lab(57, J, label, 3)
    for n in (57, 115):
        for J in JSTAR_EXTRA:
            refs(n, J, 3, full=False)
            for label in ("m_s", "Czz_bar"):
                lab(n, J, label, 3)
    for (n, J) in MINCHI_POINTS:
        add("minchi%d_%s" % (n, jstr(J)), ["minchi", str(n), jstr(J), "m_s"], ["thr%d_%s" % (n, jstr(J))], 3)
    # priorities 4-7: n = 115 local rows
    for J in GRID:
        if J <= 4.5:
            lab(115, J, "Z_bulk", 4)
            lab(115, J, "Czz_edge", 5)
            lab(115, J, "Z_boundary", 5)
            lab(115, J, "Z_loop", 6)
        else:
            for label in LOCALS:
                lab(115, J, label, 7)
    wjson(path, dict(tasks=T))
    print(len(T), "tasks")


def main(argv):
    root, task = argv[0], argv[1]
    a = argv[2:]
    if task == "ref":
        task_ref(root, *a)
    elif task == "thr":
        task_thr(root, *a)
    elif task == "lab":
        task_lab(root, *a)
    elif task == "cold":
        task_cold(root, *a)
    elif task == "chk":
        task_chk(root, *a)
    elif task == "minchi":
        task_minchi(root, *a)
    elif task == "g1":
        task_g1(root, *a)
    elif task == "plan":
        make_plan(a[0])
    else:
        raise SystemExit("unknown task " + task)


if __name__ == "__main__":
    main(sys.argv[1:])
