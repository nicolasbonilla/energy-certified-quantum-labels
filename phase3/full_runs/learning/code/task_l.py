"""VM tasks of the learning run (full_runs/learning/DECLARATION.md). Started by sched.py (copy of the Huang run's).

  python task_l.py <root> A <set> <k>     tier A of one instance: ED ground state, generator labels at both delta e,
                                          witness points of the averages and of the 31 nn-bond labels
  python task_l.py <root> B <set> <k>     tier B of one instance: ED ground state again, witness points of the 24
                                          diagonal-pair labels
  python task_l.py <root> plan <plan.json>
<set> = D (the benchmark's own n = 20 instances, files in <root>/data_huang20/) or O (the declared out-of-distribution
instances, couplings in code/instances_ood.json). Toys: any other set name <s> (couplings in code/instances_<s>.json).

Units: the benchmark paper's H = sum_b J_b sigma_i . sigma_j; labels C_ij = sigma_i . sigma_j / 3; label fields use the
field operator G = S O = sum_p w_p C_p (lattice.label_pairs). Every output JSON is written atomically. numpy/scipy only.
"""
import json
import math
import os
import sys
import time

import numpy as np
import scipy.sparse.linalg as sla

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lattice as LT  # noqa: E402
import ed_h  # noqa: E402

DE_TARGETS = [1e-3, 5e-3]            # declared intensive energy errors (paper units)
AVERAGES = ["Cnn", "Cd2", "Cstag"]
CHI_GUESS = {"Cnn": 1.0, "Cd2": 1.15, "Cstag": 120.0, "pair": 0.06}   # first-step guesses only (secant corrects)
ED_TOL = 1e-12                       # ground state of H
WIT_TOL = 1e-10                      # ground states of H - sign*lam*G (residual returned, F_lo = F - residual)
SECANT_REL = 0.25                    # stop when |E(lam) - E0 - eps| <= 0.25 eps
SECANT_MAX = 3                       # at most 3 evaluations per (sign, target)
SEED_GEN = 20261101                  # generator shot streams: SEED_GEN + 100000*set_code + k
SET_CODE = {"D": 0, "O": 1}


def jdump(path, obj):
    LT.write_json(path, obj)


def load_couplings(root, sset, k):
    """(L, J list, dataset file dict or None)."""
    if sset == "D":
        I = LT.load_instance(os.path.join(root, "data_huang20"), 4, int(k))
        return 4, I["J"], I
    if sset == "O":
        d = json.load(open(os.path.join(root, "code", "instances_ood.json")))
    else:                               # toys: code/instances_<set>.json
        d = json.load(open(os.path.join(root, "code", "instances_%s.json" % sset)))
    J = d["J"][int(k) - 1]
    assert len(J) == len(LT.bonds(d["L"]))
    return d["L"], J, None


def set_code(sset):
    return SET_CODE.get(sset, 7)


def label_list(L, tier):
    if tier == "A":
        return AVERAGES + LT.nn_pair_labels(L)
    if tier == "B":
        return [LT.pair_label(i, j) for (i, j) in LT.diag_pairs(L)]
    raise ValueError(tier)


def chi_guess(label):
    return CHI_GUESS.get(label, CHI_GUESS["pair"])


# --------------------------------------------------------------------------------------------- generator (ii)
def gen_order(psi0, seed):
    """Order of first appearance of the configurations in an i.i.d. shot stream from |psi0|^2 (Poissonized: the
    first arrival of configuration b in a rate-p_b Poisson process is E_b / p_b with E_b ~ Exp(1); sorting these
    times gives exactly the order of first appearance; the k-th time is the expected number of shots needed)."""
    p = psi0 * psi0
    p = p / p.sum()
    rng = np.random.default_rng(seed)
    e = rng.exponential(size=len(p))
    with np.errstate(divide="ignore"):
        T = np.where(p > 0, e / np.where(p > 0, p, 1.0), np.inf)
    order = np.argsort(T, kind="stable")
    return order, T[order], p


def rr_ground(H, idx, v0seed=12345):
    """Rayleigh-Ritz ground state of H in span{|b> : b in idx} (sorted index array). Returns (E, vec on idx, res)."""
    Hs = H[idx][:, idx]
    m = len(idx)
    if m <= 1200:
        w, v = np.linalg.eigh(Hs.toarray())
        x = v[:, 0]
        E = float(w[0])
    else:
        rng = np.random.default_rng(v0seed)
        w, v = sla.eigsh(Hs, k=1, which="SA", tol=1e-10, v0=rng.standard_normal(m))
        x = v[:, 0]
        E = float(w[0])
    x = x / np.linalg.norm(x)
    res = float(np.linalg.norm(Hs @ x - E * x))
    return E, x, res


def generator(sec, H, E0, psi0, n, de, order, T, p):
    """Smallest prefix of the shot stream's configurations whose Rayleigh-Ritz energy error per site is <= de
    (nested subspaces: the RR energy is non-increasing in the prefix length; bisection on the prefix length)."""
    D = len(order)
    cache = {}

    def err(kk):
        if kk not in cache:
            idx = np.sort(order[:kk])
            E, x, res = rr_ground(H, idx)
            cache[kk] = (E, idx, x, res)
        return (cache[kk][0] - E0) / n

    lo, hi = 1, D                      # invariant: err(hi) <= de; err(lo-1) > de (lo = 1: nothing known)
    k = 1
    while k < D and err(k) > de:       # geometric search for an upper end
        lo = k + 1
        k = min(D, 2 * k)
    hi = k
    while lo < hi:
        mid = (lo + hi) // 2
        if err(mid) <= de:
            hi = mid
        else:
            lo = mid + 1
    kk = hi
    err(kk)
    E, idx, x, res = cache[kk]
    psi = np.zeros(D)
    psi[idx] = x
    prev = (cache[kk - 1][0] - E0) / n if (kk - 1) in cache else None
    return dict(de_target=de, D_sub=int(kk), frac_sub=kk / D, E_gen=E, de_gen=(E - E0) / n,
                de_prev=prev, rr_residual=res, captured_weight=float(p[idx].sum()),
                shots_expected=float(T[kk - 1]), n_rr_solves=len(cache)), psi


# --------------------------------------------------------------------------------------------- witnesses (iii, certified)
def witness_points(sec, H, E0, o0, G, S, sign, eps_list, chi0, tol=WIT_TOL):
    """Ground states of H - sign*lam*G at lambdas aimed (secant in log-log) so that the witness energy <H> equals
    E0 + eps for each eps of eps_list. Every evaluated point is returned; any point gives the rigorous bound
    sign*<O> <= (E - F_lo)/(lam S) for every state with <H> <= E (Lagrange duality, Lemma A)."""
    pts = []

    def ev(lam, why):
        A = (H - (sign * lam) * G).tocsr()
        w, v, res = sec.lowest(A, tol)
        psi = v[:, 0] / np.linalg.norm(v[:, 0])
        E = float(psi @ (H @ psi))
        g = float(psi @ (G @ psi))
        pt = dict(sign=sign, lam=float(lam), F=float(w[0]), residual=float(res[0]), F_lo=float(w[0] - res[0]),
                  E=E, o=g / S, why=why)
        pts.append(pt)
        return pt

    lam = math.sqrt(2.0 * eps_list[0] / chi0)
    for ti, eps in enumerate(eps_list):
        if ti > 0:   # start from the closest evaluated point
            best = min(pts, key=lambda q: abs(math.log(max(q["E"] - E0, 1e-300) / eps)))
            de_ = best["E"] - E0
            lam = best["lam"] * math.sqrt(eps / de_) if de_ > 0 else 2.0 * best["lam"]
        for it in range(SECANT_MAX):
            near = [q for q in pts if abs(q["E"] - E0 - eps) <= SECANT_REL * eps]
            if near:
                break
            if any(abs(math.log(lam / q["lam"])) < 1e-3 for q in pts):
                break
            pt = ev(lam, "t%d_i%d" % (ti, it))
            de_ = pt["E"] - E0
            if de_ <= 0:
                lam = 2.0 * lam
            else:
                lam = lam * math.sqrt(eps / de_)
    return pts


# --------------------------------------------------------------------------------------------- tasks
_SEC = {}


def sector(n):
    if n not in _SEC:
        _SEC[n] = ed_h.Sector(n)
    return _SEC[n]


def label_value(C, L, label):
    P, Wt, S, ob = LT.label_pairs(L, label)
    return float(sum(w_ * C[i, j] for (i, j), w_ in zip(P, Wt)) / S)


def pairs_vector(C, n):
    return [float(C[i, j]) for i in range(n) for j in range(i + 1, n)]


def task(root, tier, sset, k):
    k = int(k)
    t0 = time.time()
    L, J, Ifile = load_couplings(root, sset, k)
    n = L * LT.W
    B = LT.bonds(L)
    sec = sector(n)
    H = sec.hamiltonian(B, J)
    w, v, res = sec.lowest(H, ED_TOL, k=2)
    psi0 = v[:, 0] / np.linalg.norm(v[:, 0])
    E0 = float(w[0])
    C0 = sec.all_corr(psi0)
    t_ed = time.time() - t0
    out = dict(tier=tier, set=sset, k=k, L=L, n=n, dim=sec.D, nup=sec.nup, J=list(map(float, J)), E0=E0,
               E1_sector=float(w[1]), ed_residual=[float(r) for r in res], t_ed=t_ed,
               C_exact_pairs=pairs_vector(C0, n),
               exact_labels={lab: label_value(C0, L, lab) for lab in AVERAGES})
    if Ifile is not None:
        Cf = np.array(Ifile["XX"])
        off = ~np.eye(n, dtype=bool)
        Cm3 = (np.array(Ifile["XX"]) + np.array(Ifile["YY"]) + np.array(Ifile["ZZ"])) / 3.0
        out["gate_ed"] = dict(E_file_x2=2.0 * Ifile["E_file"], dE_vs_file=E0 - 2.0 * Ifile["E_file"],
                              max_dC_vs_XX=float(np.abs(C0 - Cf)[off].max()),
                              max_dC_vs_mean3=float(np.abs(C0 - Cm3)[off].max()),
                              file_max_XX_minus_ZZ=float(np.abs(np.array(Ifile["XX"]) - np.array(Ifile["ZZ"])).max()))
    E_from_C = sum(3.0 * c * C0[i, j] for (i, j), c in zip(B, J))
    out["E_from_C_minus_E0"] = float(E_from_C - E0)
    print("ED %s%d E0=%.10f E1=%.6f res=%.1e t=%.0fs" % (sset, k, E0, w[1], res[0], t_ed), flush=True)
    if tier == "A":
        order, T, p = gen_order(psi0, SEED_GEN + 100000 * set_code(sset) + k)
        gens = []
        for de in DE_TARGETS:
            tg = time.time()
            g, psig = generator(sec, H, E0, psi0, n, de, order, T, p)
            Cg = sec.all_corr(psig)
            g["C_gen_pairs"] = pairs_vector(Cg, n)
            g["gen_labels"] = {lab: label_value(Cg, L, lab) for lab in AVERAGES}
            g["E_gen_check"] = float(psig @ (H @ psig))
            g["t"] = time.time() - tg
            gens.append(g)
            print("GEN %s%d de=%.0e D=%d (%.3f) de_gen=%.4e W=%.4f shots~%.3g t=%.0fs" % (
                sset, k, de, g["D_sub"], g["frac_sub"], g["de_gen"], g["captured_weight"], g["shots_expected"],
                g["t"]), flush=True)
        out["generator"] = gens
    eps_list = [n * de for de in DE_TARGETS]
    wits = {}
    for lab in label_list(L, tier):
        tl = time.time()
        P, Wt, S, ob = LT.label_pairs(L, lab)
        G = sec.sdots(P, [w_ / 3.0 for w_ in Wt])
        o0 = label_value(C0, L, lab)
        pts = []
        for sign in (+1, -1):
            pts += witness_points(sec, H, E0, o0, G, S, sign, eps_list, chi_guess(lab))
        wits[lab] = dict(S=S, obounds=list(ob), o_GS=o0, points=pts, t=time.time() - tl)
        print("WIT %s%d %s o0=%.5f npts=%d t=%.0fs" % (sset, k, lab, o0, len(pts), time.time() - tl), flush=True)
    out["witness"] = wits
    out["time_s"] = time.time() - t0
    jdump(os.path.join(root, "out", "inst", "%s_%s_%03d.json" % (tier, sset, k)), out)
    print("DONE %s %s%d t=%.0fs" % (tier, sset, k, out["time_s"]), flush=True)


def plan(root, path, sets=(("D", 100), ("O", 40)), tiers=("A", "B")):
    tasks = []
    for tier in tiers:
        for sset, N in sets:
            for k in range(1, N + 1):
                tasks.append(dict(id="%s_%s_%03d" % (tier, sset, k), args=[tier, sset, str(k)],
                                  prio=1 if tier == "A" else 2, deps=[]))
    LT.write_json(path, dict(tasks=tasks))
    print("plan: %d tasks" % len(tasks))


if __name__ == "__main__":
    root, mode = sys.argv[1], sys.argv[2]
    if mode in ("A", "B"):
        task(root, mode, sys.argv[3], sys.argv[4])
    elif mode == "plan":
        plan(root, sys.argv[3])
    elif mode == "plantoy":
        plan(root, sys.argv[3], sets=((sys.argv[4], int(sys.argv[5])),), tiers=tuple(sys.argv[6].split(",")))
    else:
        raise SystemExit("usage")
