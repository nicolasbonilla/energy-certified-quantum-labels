"""Label tables of the learning run (laptop; reads the per-instance JSONs written by task_l.py on the VM).

For every instance and label (the averages Cnn, Cd2, Cstag; the 31 nn-bond pairs; the 24 diagonal pairs when tier B is
present) and every declared delta e:
  * exact label (i)       : the ED ground-state value o_GS;
  * generator label (ii)  : the Rayleigh-Ritz state of the truncated-subspace emulation, at energy E_gen;
  * adversarial label (iii), direction d in {"less", "more"} (toward less / more antiferromagnetic order): the
    extreme of the explicit witness pool {ground state} U {ground states of H - s lam G} at energy E0 + n de
    (hull.extreme: pure points and two-state mixtures; by Toeplitz-Hausdorff a pure state attains every mixture value);
  * certified interval at energy E: [lo(E), hi(E)] with
        hi(E) = min over + points (E - F_lo)/(lam S),  lo(E) = - min over - points (E - F_lo)/(lam S),
    capped at the label's bounds (Lagrange duality, Lemma A; rigorous for every state with <H> <= E, F_lo = Ritz value
    minus residual). Intervals are computed at E_gen for (ii) and at E0 + n de for (iii).
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lattice as LT  # noqa: E402
import hull  # noqa: E402

DE = [1e-3, 5e-3]
AVERAGES = ["Cnn", "Cd2", "Cstag"]
ORDER_SIGN_AVG = {"Cnn": -1, "Cd2": +1, "Cstag": +1}     # direction of more AFM order


def order_sign(label):
    if label in ORDER_SIGN_AVG:
        return ORDER_SIGN_AVG[label]
    _, a, b = label.split("_")
    return LT.eta(int(a)) * LT.eta(int(b))


def label_class(label, L):
    if label in AVERAGES:
        return "avg"
    _, a, b = label.split("_")
    p = (int(a), int(b))
    if p in set(LT.bonds(L)):
        return "nn"
    if p in set(LT.diag_pairs(L)):
        return "diag"
    return "other"


def cert_interval(w, E):
    S = w["S"]
    lo_b, hi_b = w["obounds"]
    up = [(E - p["F_lo"]) / (p["lam"] * S) for p in w["points"] if p["sign"] > 0]
    dn = [(E - p["F_lo"]) / (p["lam"] * S) for p in w["points"] if p["sign"] < 0]
    hi = min([hi_b] + up)
    lo = max([lo_b] + [-x for x in dn])
    return lo, hi


def adversarial(w, E0, E, sign):
    pts = [dict(sid="gs", E=E0, o=w["o_GS"])] + [dict(sid="p%d" % i, E=p["E"], o=p["o"])
                                                  for i, p in enumerate(w["points"]) if p["sign"] == sign]
    val, comps = hull.extreme(pts, E, sign)
    return val, comps


def pair_index(n):
    return {(i, j): t for t, (i, j) in enumerate([(i, j) for i in range(n) for j in range(i + 1, n)])}


def instance_record(dA, dB=None):
    """Merge the tier-A (and optional tier-B) outputs of one instance into a label table."""
    n, L, E0 = dA["n"], dA["L"], dA["E0"]
    pidx = pair_index(n)
    ce = np.array(dA["C_exact_pairs"])
    wit = dict(dA["witness"])
    if dB is not None:
        assert abs(dB["E0"] - E0) <= 1e-9 * abs(E0), (dB["E0"], E0)
        wit.update(dB["witness"])
    gens = {round(g["de_target"], 12): g for g in dA["generator"]}
    rec = dict(set=dA["set"], k=dA["k"], n=n, L=L, J=dA["J"], E0=E0, labels={}, gen={}, gate=dA.get("gate_ed"),
               ed_residual=dA["ed_residual"], E_from_C_minus_E0=dA["E_from_C_minus_E0"])
    for de in DE:
        g = gens[round(de, 12)]
        rec["gen"][de] = {k: g[k] for k in ("D_sub", "frac_sub", "E_gen", "de_gen", "de_prev", "captured_weight",
                                             "shots_expected", "rr_residual", "E_gen_check")}
    cg = {de: np.array(gens[round(de, 12)]["C_gen_pairs"]) for de in DE}
    for lab, w in wit.items():
        if lab in AVERAGES:
            y0 = dA["exact_labels"][lab]
            yg = {de: gens[round(de, 12)]["gen_labels"][lab] for de in DE}
        else:
            _, a, b = lab.split("_")
            t = pidx[(int(a), int(b))]
            y0 = float(ce[t])
            yg = {de: float(cg[de][t]) for de in DE}
        r = dict(cls=label_class(lab, L), exact=y0, o_GS_wit=w["o_GS"], S=w["S"], obounds=w["obounds"],
                 npts=len(w["points"]), gen={}, cert_gen={}, adv={"less": {}, "more": {}}, cert_adv={})
        so = order_sign(lab)
        for de in DE:
            Eg = gens[round(de, 12)]["E_gen"]
            Et = E0 + n * de
            r["gen"][de] = yg[de]
            r["cert_gen"][de] = cert_interval(w, Eg)
            r["cert_adv"][de] = cert_interval(w, Et)
            for d, s in (("less", -so), ("more", +so)):
                v, comps = adversarial(w, E0, Et, s)
                r["adv"][d][de] = v
        rec["labels"][lab] = r
    return rec


def load_all(out_dir, sets):
    """{set: [records sorted by k]} from <out_dir>/inst/{A,B}_<set>_<k>.json."""
    res = {}
    for s in sets:
        files = sorted(glob.glob(os.path.join(out_dir, "inst", "A_%s_*.json" % s)))
        recs = []
        for f in files:
            dA = json.load(open(f))
            fb = f.replace(os.sep + "A_", os.sep + "B_").replace("/A_", "/B_")
            dB = json.load(open(fb)) if os.path.exists(fb) else None
            recs.append(instance_record(dA, dB))
        recs.sort(key=lambda r: r["k"])
        res[s] = recs
    return res


def checks(recs):
    """Deterministic validity checks of the certified intervals (any failure is a bug)."""
    out = dict(n_labels=0, exact_in_cert_gen=0, gen_in_cert_gen=0, exact_in_cert_adv=0, adv_in_cert_adv=0,
               wit_vs_ed_max=0.0, max_viol=0.0, fails=[])
    tol = 1e-9
    for rec in recs:
        for lab, r in rec["labels"].items():
            out["n_labels"] += 1
            out["wit_vs_ed_max"] = max(out["wit_vs_ed_max"], abs(r["exact"] - r["o_GS_wit"]))
            for de in DE:
                lo, hi = r["cert_gen"][de]
                lo2, hi2 = r["cert_adv"][de]
                for name, y, (a, b) in (("exact_in_cert_gen", r["exact"], (lo, hi)),
                                        ("gen_in_cert_gen", r["gen"][de], (lo, hi)),
                                        ("exact_in_cert_adv", r["exact"], (lo2, hi2)),
                                        ("adv_in_cert_adv", r["adv"]["less"][de], (lo2, hi2)),
                                        ("adv_in_cert_adv", r["adv"]["more"][de], (lo2, hi2))):
                    v = max(a - y, y - b, 0.0)
                    out["max_viol"] = max(out["max_viol"], v)
                    if v <= tol:
                        out[name] += 1
                    else:
                        out["fails"].append((rec["set"], rec["k"], lab, de, name, y, a, b))
    return out
