# real_data / checks / rd_predict_independent.py   (own code; 2026-11-12; task rd-predict; WRITTEN AFTER THE HASH)
#
# Independent recomputation of DECLARATION.md Sec. 5 (P1-P5) and of the n = 19 comparison of Sec. 6, to check the
# numbers of the sealed code (code/run_predict.py -> out/predict/predict_results.json). It shares no function with
# code/rd_common.py or code/rd_predict.py and decides nothing: the outcomes reported in results/RESULTS_predict.md are
# those of the sealed code. Differences from the sealed code, on purpose:
#   - the lattice comes from converted/lattice_maps.json (the repository's edge list and two-colouring); second
#     neighbours are derived here from the edges; loops are taken from the data files; Neel values are computed as
#     products of eta (not assumed);
#   - Spearman is scipy.stats.spearmanr; the curve is read by a hand-written interpolation in sqrt(de);
#   - the n = 19 curves are recomputed here by an exact diagonalization written from scratch (same recipe: top-D
#     truncation of the exact ground state, the same 26 levels) and compared with out/n19/n19_curves.json.
# Reads converted/ only after checking DECLARATION.sha256 and the pinned SHA-256 of each converted file.
# Plain JSON only; no pickle; nothing of the downloaded repository is imported or executed.
#
#   python -B -I rd_predict_independent.py [--no-ed]
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import bisect
import hashlib
import json
import math
import re
import sys
import time

import numpy as np
from scipy import sparse, stats
from scipy.sparse.linalg import eigsh

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)
FR = os.path.dirname(RD)
ROOT = os.path.dirname(os.path.dirname(FR))
TAU = 0.06
TEST = (1.1, 1.2, 1.3, 1.4)
OUT = {}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def jk(J):
    return "%.1f" % J


# ------------------------------------------------------------------------------------------------ gate
decl = sha(os.path.join(RD, "DECLARATION.md"))
with open(os.path.join(RD, "DECLARATION.sha256"), encoding="utf-8") as f:
    rec = re.search(r"\b[0-9a-f]{64}\b", f.read()).group(0)
if rec != decl:
    raise SystemExit("REFUSED: DECLARATION.sha256 does not match DECLARATION.md")
with open(os.path.join(RD, "DECLARATION.md"), encoding="utf-8") as f:
    dtext = f.read()
pinned = dict((m.group(2), m.group(1)) for m in re.finditer(r"^([0-9a-f]{64})  converted/(\S+)$", dtext, re.M))
for name in ("real_n57.json", "real_n115.json", "lattice_maps.json"):
    if sha(os.path.join(RD, "converted", name)) != pinned[name]:
        raise SystemExit("REFUSED: converted/%s does not have the pinned SHA-256" % name)
OUT["gate"] = dict(declaration_sha256=decl, converted_sha256_equal_to_pinned=True)
print("gate: declaration %s...; the three converted files have the pinned SHA-256" % decl[:16])

# ------------------------------------------------------------------------------------------------ inputs
LM = rj(os.path.join(RD, "converted", "lattice_maps.json"))["maps"]
SM = rj(os.path.join(FR, "map", "laptop_analysis", "summary_map.json"))
SEALED = rj(os.path.join(RD, "out", "predict", "predict_results.json"))
C19 = rj(os.path.join(RD, "out", "n19", "n19_curves.json"))
L19 = rj(os.path.join(RD, "out", "n19", "n19_labels.json"))


def lattice(n):
    m = LM[str(n)]
    edges = sorted(tuple(sorted(e)) for e in m["edges_sorted_unique"])
    adj = {i: set() for i in range(n)}
    for i, j in edges:
        adj[i].add(j); adj[j].add(i)
    es = set(edges)
    nn2 = sorted(set(tuple(sorted((a, b))) for c in range(n) for a in adj[c] for b in adj[c] if a < b) - es)
    col = m["colour_with_node0_as_1"]
    maj = 1 if sum(col) * 2 > n else 0
    eta = np.array([1.0 if c == maj else -1.0 for c in col])
    for i, j in edges:
        assert eta[i] * eta[j] == -1.0                      # proper two-colouring
    return edges, nn2, eta


def project_graph(n):
    G = rj(os.path.join(FR, "method", "code", "graphs", "hh_d%d.json" % {19: 3, 57: 5, 115: 7}[n]))
    return G


def spearman_check(x, y):
    return float(stats.spearmanr(x, y).statistic)


def interp_sqrt(curve, de):
    """Linear interpolation in sqrt(de); end values held outside the range. curve: sorted list of (de, dm)."""
    xs = [math.sqrt(max(a, 0.0)) for a, _ in curve]
    ys = [b for _, b in curve]
    x = math.sqrt(max(de, 0.0))
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    k = bisect.bisect_right(xs, x)
    return ys[k - 1] + (ys[k] - ys[k - 1]) * (x - xs[k - 1]) / (xs[k] - xs[k - 1])


# ------------------------------------------------------------------------------------------------ n = 19, from scratch
def ed19():
    G = project_graph(19)
    n = G["n"]; nd = G["n_down"]
    edges = [tuple(e) for e in G["edges"]]
    eta = np.array(G["eta"], float)
    a = np.arange(1 << n, dtype=np.int64)
    pc = np.zeros(1 << n, dtype=np.int64)
    for b in range(n):
        pc += (a >> b) & 1
    cfg = a[pc == nd]                                       # bit = 1: spin down
    dim = len(cfg)
    lut = -np.ones(1 << n, dtype=np.int64); lut[cfg] = np.arange(dim)
    Z = (1 - 2 * ((cfg[:, None] >> np.arange(n)) & 1)).astype(float)
    zz = np.zeros(dim)
    rows, cols = [], []
    for i, j in edges:
        zz += Z[:, i] * Z[:, j]
        m = (1 << i) | (1 << j)
        x = cfg & m
        sel = np.nonzero((x != 0) & (x != m))[0]
        rows.append(sel); cols.append(lut[cfg[sel] ^ m])
    rows = np.concatenate(rows); cols = np.concatenate(cols)
    assert cols.min() >= 0
    Hxy = sparse.coo_matrix((np.full(len(rows), 0.5), (rows, cols)), shape=(dim, dim)).tocsr()
    assert abs(Hxy - Hxy.T).max() == 0
    Ds = sorted(set(int(x) for x in np.round(np.logspace(0.7, np.log10(dim * .9), 26))))
    res = {}
    t0 = time.time()
    for k in range(11, 61):
        J = k / 10
        H = (Hxy + sparse.diags(J / 4 * zz)).tocsr()
        w, v = eigsh(H, k=1, which="SA", tol=1e-12, ncv=48)
        E0 = float(w[0]); psi = v[:, 0]
        resid = float(np.linalg.norm(H @ psi - E0 * psi))
        p = psi ** 2
        ms0 = float((p @ Z) @ eta / n)
        order = np.argsort(-p, kind="stable")
        cur = []
        for D in Ds:
            B = np.sort(order[:D])
            Hb = H[B][:, B]
            if D < 400:
                ww, vv = np.linalg.eigh(Hb.toarray())
            else:
                ww, vv = eigsh(Hb, k=1, which="SA", tol=1e-10)
            x = vv[:, 0]
            cur.append(((float(ww[0]) - E0) / n, float(((x ** 2) @ Z[B]) @ eta / n) - ms0))
        res[J] = dict(E0=E0, ms0=ms0, curve=sorted(cur), residual=resid, sumZ=float((p @ Z).sum()),
                      de_neel=float((-len(edges) * J / 4 - E0) / n))
    print("n = 19 from scratch: dim %d, %d levels, 50 couplings, %.0f s" % (dim, len(Ds), time.time() - t0))
    return res, Ds, len(edges), dim


# ------------------------------------------------------------------------------------------------ per size
def analyse(n, ED):
    edges, nn2, eta = lattice(n)
    G = project_graph(n)
    same_lattice = dict(edges=sorted(tuple(sorted(e)) for e in G["edges"]) == edges,
                        nn2=sorted(tuple(sorted(e)) for e in G["nn2"]) == nn2,
                        eta=bool(np.array_equal(np.array(G["eta"], float), eta)),
                        M0=float(eta.sum()))
    obj = rj(os.path.join(RD, "converted", "real_n%d.json" % n))
    lab, dm = obj["skqd_random_flip"], obj["dmrg"]
    refE = {round(r["Jz"], 1): float(r["E0"]) for r in SM["refs"].values() if r["n"] == n}
    refO = {(round(r["Jz"], 1), r["label"]): float(r["O_GS"]) for r in SM["rows"] if r["n"] == n}
    Js = [k / 10 for k in range(11, 61)]
    fam_names = ("sites", "edges", "second_neighbours", "loops")
    T = {f: {} for f in fam_names}; Dv = {f: {} for f in fam_names}; Dm = {}
    rows = []; neg = []
    gates = dict(G2_max_fraction=0.0, G2_min_fraction=9.0, G2_ok=True, G3_min=9e9, G4_max_dms_tau=0.0, G4_max_dE0=0.0,
                 G4_max_seven_tau=0.0)
    loc = G["local"]
    for J in Js:
        e, d = lab[jk(J)], dm[jk(J)]
        assert abs(e["jz"] - J) < 1e-9 and abs(d["jz"] - J) < 1e-9
        zr, zg = np.array(e["z_basis_opt"], float), np.array(d["z"], float)
        pr = {tuple(sorted(p)): float(v) for p, v in zip(e["2_nn_corr_pairs_zz_basis_opt"], e["2_nn_corr_funcs_zz_basis_opt"])}
        pg = {tuple(sorted(p)): float(v) for p, v in zip(d["2_nn_corr_pairs"], d["2_nn_corr_funcs_zz"])}
        assert len(pr) == len(e["2_nn_corr_pairs_zz_basis_opt"]) and set(pr) == set(edges) | set(nn2) == set(pg)
        lr = {frozenset(s): float(v) for s, v in zip(e["z_loop_sites"], e["z_loop"])}
        lg = {frozenset(s): float(v) for s, v in zip(d["z_loop_sites"], d["z_loop"])}
        assert set(lr) == set(lg) and all(len(s) == 12 for s in lr)
        loops = sorted(lr, key=lambda s: sorted(s))
        fam = dict(sites=(zr, zg, eta, list(range(n))),
                   edges=(np.array([pr[p] for p in edges]), np.array([pg[p] for p in edges]),
                          np.array([eta[i] * eta[j] for i, j in edges]), edges),
                   second_neighbours=(np.array([pr[p] for p in nn2]), np.array([pg[p] for p in nn2]),
                                      np.array([eta[i] * eta[j] for i, j in nn2]), nn2),
                   loops=(np.array([lr[s] for s in loops]), np.array([lg[s] for s in loops]),
                          np.array([float(np.prod([eta[i] for i in s])) for s in loops]), [sorted(s) for s in loops]))
        for f in fam_names:
            a, b, ne, items = fam[f]
            t = (a - b) / (ne - b)
            T[f][J] = t
            Dv[f][J] = float(np.mean(np.abs(a - b) / (TAU * np.abs(b))))
            for i in np.nonzero(~(t > 0))[0]:
                neg.append(dict(family=f, Jz=J, item=items[i] if f != "sites" else int(items[i]), t=float(t[i]),
                                o_real=float(a[i]), o_gs=float(b[i]), diff_over_tau_item=float((a[i] - b[i]) / (TAU * abs(b[i])))))
        # m_s, energies, truth by the rule of Sec. 0
        m_real = float(zr @ eta / n); m_auth = float(zg @ eta / n)
        E_real = float(e["final_global_energy"]); E0a = float(d["ground_state_energy"])
        E0 = refE.get(J, E0a); m_gs = refO.get((J, "m_s"), m_auth)
        Dm[J] = abs(m_real - m_gs) / (TAU * abs(m_gs))
        # gates (re-check)
        X = E_real - J / 4 * sum(pr[p] for p in edges)
        Bq = sum(0.5 * math.sqrt(max(((1 - pr[(i, j)]) / 2) ** 2 - ((zr[i] - zr[j]) / 2) ** 2, 0.0)) for i, j in edges)
        gates["G2_ok"] &= bool(-Bq <= X <= Bq)
        gates["G2_max_fraction"] = max(gates["G2_max_fraction"], -X / Bq); gates["G2_min_fraction"] = min(gates["G2_min_fraction"], -X / Bq)
        gates["G3_min"] = min(gates["G3_min"], E_real - E0a)
        if J in refE:
            gates["G4_max_dE0"] = max(gates["G4_max_dE0"], abs(refE[J] - E0a))
        if (J, "m_s") in refO:
            gates["G4_max_dms_tau"] = max(gates["G4_max_dms_tau"], abs(refO[(J, "m_s")] - m_auth) / (TAU * abs(refO[(J, "m_s")])))
        seven = dict(m_s=m_auth, Czz_bar=float(np.mean([pg[p] for p in edges])), C2_bar=float(np.mean([pg[p] for p in nn2])),
                     Z_bulk=float(zg[loc["bulk_site"]]), Z_boundary=float(zg[loc["boundary_site"]]),
                     Czz_edge=pg[tuple(sorted(loc["edge"]))], Z_loop=lg[frozenset(loc["loop"])])
        for k7, v7 in seven.items():
            if (J, k7) in refO:
                gates["G4_max_seven_tau"] = max(gates["G4_max_seven_tau"], abs(refO[(J, k7)] - v7) / (TAU * abs(refO[(J, k7)])))
        de = (E_real - E0) / n
        tau = TAU * abs(m_gs)
        row = dict(Jz=J, m_real=m_real, m_gs=m_gs, m_gs_authors=m_auth, E_real=E_real, E0=E0, E0_authors=E0a, de=de,
                   de_authors=(E_real - E0a) / n, tau=tau, Delta=m_real - m_gs, sumZ_minus_M0=float(zr.sum() - eta.sum()))
        for tag, src in (("stored", {J2: C19[str(J2)] for J2 in [J]}), ("ed", ED)):
            if src is None:
                continue
            c = src[J]
            cur = interp_sqrt([tuple(x) for x in c["curve"]], de)
            de_neel = (-20 * J / 4 - c["E0"]) / 19
            ch = (1 - c["ms0"]) * math.sqrt(max(de, 0) / de_neel)
            row.update({"curve_" + tag: cur, "ratio_" + tag: (row["Delta"] / cur) if cur != 0 else None,
                        "miss_" + tag: abs(m_real - cur - m_gs) / tau, "chord_" + tag: ch,
                        "miss_chord_" + tag: abs(m_real - ch - m_gs) / tau,
                        "n19_truth_" + tag: abs(c["ms0"] - m_gs) / tau})
        # the same with the authors' DMRG as truth everywhere (post hoc robustness; not the declared truth rule)
        c = C19[str(J)]
        taua = TAU * abs(m_auth); cura = interp_sqrt([tuple(x) for x in c["curve"]], row["de_authors"])
        row.update(ratio_authors=(m_real - m_auth) / cura, miss_authors=abs(m_real - cura - m_auth) / taua,
                   raw_authors=abs(m_real - m_auth) / taua)
        row["raw"] = abs(row["Delta"]) / tau
        row["decides"] = bool(row["raw"] >= 0.2)
        row["de_range_curve"] = [float(min(x[0] for x in c["curve"])), float(max(x[0] for x in c["curve"]))]
        rows.append(row)
    res = dict(n=n, same_lattice_as_project_graph=same_lattice, gates=gates, rows=rows, t_not_positive=neg)
    # P1-P3
    P13 = {}
    for f in fam_names:
        allt = np.concatenate([T[f][J] for J in Js])
        P13[f] = dict(n_pairs=int(len(allt)), F=float((allt > 0).mean()), holds=bool((allt > 0).mean() >= 0.95),
                      n_not_positive=int((~(allt > 0)).sum()), frac_t_le_1=float((allt <= 1).mean()),
                      t_min=float(allt.min()), t_max=float(allt.max()), t_median=float(np.median(allt)),
                      F_per_coupling={jk(J): float((T[f][J] > 0).mean()) for J in Js},
                      t_median_per_coupling={jk(J): float(np.median(T[f][J])) for J in Js})
    res["P1_P3"] = P13
    # P4
    P4 = {}
    for f in fam_names:
        rho = spearman_check(Js, [Dv[f][J] for J in Js])
        P4[f] = dict(spearman=rho, holds=bool(rho <= -0.9), D={jk(J): Dv[f][J] for J in Js},
                     n_increases=int(sum(Dv[f][Js[i + 1]] > Dv[f][Js[i]] for i in range(49))))
    rho = spearman_check(Js, [Dm[J] for J in Js])
    P4["m_s"] = dict(spearman=rho, holds=bool(rho <= -0.9), D={jk(J): Dm[J] for J in Js})
    res["P4"] = P4

    # P5
    def summ(rs, tag, ratio_key=None, miss_key=None, raw_key="raw"):
        ratio_key = ratio_key or "ratio_" + tag; miss_key = miss_key or "miss_" + tag
        dec = [r for r in rs if r[raw_key] >= 0.2]
        bad = [r["Jz"] for r in dec if r[ratio_key] is None or not (0.75 <= r[ratio_key] <= 1.3)]
        s = dict(n_couplings=len(rs), mean_miss=float(np.mean([r[miss_key] for r in rs])),
                 max_miss=float(np.max([r[miss_key] for r in rs])), mean_raw=float(np.mean([r[raw_key] for r in rs])),
                 n_deciding=len(dec), deciding=[r["Jz"] for r in dec],
                 ratio_min_deciding=float(min(r[ratio_key] for r in dec)), ratio_max_deciding=float(max(r[ratio_key] for r in dec)),
                 ratio_median_deciding=float(np.median([r[ratio_key] for r in dec])),
                 ratio_min_all=float(min(r[ratio_key] for r in rs)), ratio_max_all=float(max(r[ratio_key] for r in rs)),
                 outside=bad, mean_ok=bool(np.mean([r[miss_key] for r in rs]) <= {57: 0.2, 115: 0.6}[n]), ratios_ok=not bad)
        if ratio_key == "ratio_" + tag:
            s.update(mean_miss_chord=float(np.mean([r["miss_chord_" + tag] for r in rs])),
                     max_miss_chord=float(np.max([r["miss_chord_" + tag] for r in rs])),
                     mean_n19_truth=float(np.mean([r["n19_truth_" + tag] for r in rs])),
                     max_n19_truth=float(np.max([r["n19_truth_" + tag] for r in rs])))
        return s
    tr = [r for r in rows if r["Jz"] >= 1.6]; te = [r for r in rows if r["Jz"] in TEST]
    P5 = dict(stored_curve=dict(all=summ(rows, "stored"), training_45=summ(tr, "stored"), test=summ(te, "stored")),
              authors_truth_everywhere=dict(all=summ(rows, "stored", "ratio_authors", "miss_authors", "raw_authors"),
                                            training_45=summ(tr, "stored", "ratio_authors", "miss_authors", "raw_authors")))
    if ED is not None:
        P5["ed_curve"] = dict(all=summ(rows, "ed"), training_45=summ(tr, "ed"), test=summ(te, "ed"))
        P5["max_abs_curve_stored_minus_ed"] = float(max(abs(r["curve_stored"] - r["curve_ed"]) for r in rows))
        P5["max_abs_ratio_stored_minus_ed"] = float(max(abs(r["ratio_stored"] - r["ratio_ed"]) for r in rows))
    P5["n_de_outside_curve"] = int(sum(not (max(r["de_range_curve"][0], 0) <= r["de"] <= r["de_range_curve"][1]) for r in rows))
    res["P5"] = P5
    # Sec. 6: n = 19 against the truth, next to the label
    cmp_ = dict(rows=[dict(Jz=r["Jz"], n19_minus_truth_tau=r["n19_truth_stored"], label_miss_tau=r["raw"]) for r in rows])
    closer = [r["Jz"] for r in rows if r["n19_truth_stored"] < r["raw"]]
    cmp_.update(n19_closer_than_label_at=closer, n_n19_closer=len(closer),
                n_n19_closer_training=len([J for J in closer if J >= 1.6]),
                within_fifth_from=min(J for J in Js if all(r["n19_truth_stored"] <= 0.2 for r in rows if r["Jz"] >= J - 1e-9)),
                max_all=float(max(r["n19_truth_stored"] for r in rows)),
                max_training=float(max(r["n19_truth_stored"] for r in tr)),
                mean_all=float(np.mean([r["n19_truth_stored"] for r in rows])),
                mean_training=float(np.mean([r["n19_truth_stored"] for r in tr])))
    for name, lo in (("certificate_range_stored", {57: 3.4, 115: 4.0}[n]), ("certificate_range_with_E1", {57: 3.2, 115: 3.3}[n])):
        sel = [r for r in rows if r["Jz"] >= lo - 1e-9]
        cmp_[name] = dict(from_Jz=lo, n_couplings=len(sel), max_n19_minus_truth_tau=float(max(r["n19_truth_stored"] for r in sel)),
                          max_label_miss_tau=float(max(r["raw"] for r in sel)),
                          n19_closer_than_label=len([r for r in sel if r["n19_truth_stored"] < r["raw"]]))
    res["n19_comparison"] = cmp_
    return res


# ------------------------------------------------------------------------------------------------ comparison with sealed
def compare(n, R):
    S = SEALED["sizes"][str(n)]
    d = {}
    for f in ("sites", "edges", "second_neighbours", "loops"):
        a, b = S["P1_P3"][f], R["P1_P3"][f]
        d["P1_P3 %s F" % f] = abs(a["F"] - b["F"])
        d["P1_P3 %s F per coupling" % f] = max(abs(a["F_per_coupling"][k] - b["F_per_coupling"][k]) for k in a["F_per_coupling"])
        d["P1_P3 %s t<=1" % f] = abs(a["frac_t_le_1"] - b["frac_t_le_1"])
        d["P1_P3 %s t range" % f] = max(abs(a["t_min"] - b["t_min"]), abs(a["t_max"] - b["t_max"]))
        d["P4 %s Spearman" % f] = abs(S["P4"][f]["spearman"] - R["P4"][f]["spearman"])
        d["P4 %s D" % f] = max(abs(S["P4"][f]["D"][k] - R["P4"][f]["D"][k]) for k in S["P4"][f]["D"])
        assert a["holds"] == b["holds"] and S["P4"][f]["holds"] == R["P4"][f]["holds"] and a["n_pairs"] == b["n_pairs"]
    d["P4 m_s Spearman"] = abs(S["P4"]["m_s"]["spearman"] - R["P4"]["m_s"]["spearman"])
    for key_s, key_r in (("m_real", "m_real"), ("m_gs", "m_gs"), ("de", "de"), ("Delta", "Delta"), ("curve", "curve_stored"),
                         ("ratio", "ratio_stored"), ("raw_miss_tau", "raw"), ("miss_tau", "miss_stored"),
                         ("chord", "chord_stored"), ("miss_chord_tau", "miss_chord_stored"),
                         ("miss_n19_truth_tau", "n19_truth_stored")):
        d["P5 rows %s" % key_s] = max(abs(a[key_s] - b[key_r]) for a, b in zip(S["P5"]["rows"], R["rows"]))
    assert [a["decides_ratio"] for a in S["P5"]["rows"]] == [b["decides"] for b in R["rows"]]
    for k in ("all", "training_45"):
        a, b = S["P5"][k], R["P5"]["stored_curve"][k]
        d["P5 %s mean miss" % k] = abs(a["mean_miss_tau"] - b["mean_miss"])
        d["P5 %s mean chord" % k] = abs(a["mean_miss_chord_tau"] - b["mean_miss_chord"])
        d["P5 %s mean n19 truth" % k] = abs(a["mean_miss_n19_truth_tau"] - b["mean_n19_truth"])
        assert a["ratios_outside"] == b["outside"] and a["deciding_couplings"] == b["deciding"] and a["mean_miss_ok"] == b["mean_ok"]
    return d


def main():
    ED = None
    if "--no-ed" not in sys.argv:
        ED, Ds, ne19, dim = ed19()
        dE = max(abs(ED[J]["E0"] - C19[str(J)]["E0"]) for J in ED)
        dm = max(abs(ED[J]["ms0"] - C19[str(J)]["ms0"]) for J in ED)
        dc_e = max(abs(a[0] - b[0]) for J in ED for a, b in zip(ED[J]["curve"], C19[str(J)]["curve"]))
        dc_m = max(abs(a[1] - b[1]) for J in ED for a, b in zip(ED[J]["curve"], C19[str(J)]["curve"]))
        OUT["n19_from_scratch_vs_stored"] = dict(
            dim=dim, n_edges=ne19, levels=len(Ds), same_levels_as_stored=bool(Ds == L19["1.1"]["Ds"]),
            max_abs_dE0=dE, max_abs_dms0=dm, max_abs_curve_de=dc_e, max_abs_curve_dms=dc_m,
            max_residual=max(ED[J]["residual"] for J in ED), max_abs_sumZ_minus_3=max(abs(ED[J]["sumZ"] - 3) for J in ED),
            n_curve_points=[len(ED[J]["curve"]) for J in sorted(ED)][0],
            tolerances_of_gate_G_A2=dict(dE0=1e-8, dms=1e-6, curve=1e-5),
            within_G_A2=bool(dE <= 1e-8 and dm <= 1e-6 and max(dc_e, dc_m) <= 1e-5))
        print("n = 19 from scratch against out/n19/n19_curves.json: |dE0| <= %.1e, |dm_s| <= %.1e, curve |d de| <= %.1e, |d dm_s| <= %.1e"
              % (dE, dm, dc_e, dc_m))
    # stored n = 19 curves of the paper (bias_law/inputs) against out/n19 at the couplings they share
    B = rj(os.path.join(FR, "bias_law", "inputs", "n19_curves.json"))
    sh = sorted(set(B) & set(C19), key=float)
    OUT["n19_out_vs_bias_law_inputs"] = dict(
        shared_couplings=sh, max_abs_dE0=max(abs(B[k]["E0"] - C19[k]["E0"]) for k in sh),
        max_abs_dms0=max(abs(B[k]["ms0"] - C19[k]["ms0"]) for k in sh),
        max_abs_curve=max(abs(a[i] - b[i]) for k in sh for a, b in zip(B[k]["curve"], C19[k]["curve"]) for i in (0, 1)))
    print("out/n19 against bias_law/inputs/n19_curves.json at %d shared couplings: %s" % (len(sh), {k: v for k, v in OUT["n19_out_vs_bias_law_inputs"].items() if k != "shared_couplings"}))
    OUT["sizes"] = {}; OUT["max_abs_difference_from_sealed"] = {}
    for n in (57, 115):
        R = analyse(n, ED)
        OUT["sizes"][str(n)] = R
        d = compare(n, R)
        OUT["max_abs_difference_from_sealed"][str(n)] = d
        print("\nn = %d  lattice equal to the project graph: %s" % (n, R["same_lattice_as_project_graph"]))
        print("  gates re-checked: %s" % R["gates"])
        for f, r in R["P1_P3"].items():
            print("  P1-P3 %-18s F = %.6f (%d of %d not positive) holds %s | t<=1 %.4f | t in [%.4f, %.4f], median %.3f"
                  % (f, r["F"], r["n_not_positive"], r["n_pairs"], r["holds"], r["frac_t_le_1"], r["t_min"], r["t_max"], r["t_median"]))
        for x in R["t_not_positive"]:
            print("     t <= 0: %-18s Jz %.1f item %s t = %+.4f (real %.5f, GS %.5f, difference %.3f of the item's 6 %%)"
                  % (x["family"], x["Jz"], x["item"], x["t"], x["o_real"], x["o_gs"], x["diff_over_tau_item"]))
        for f, r in R["P4"].items():
            print("  P4    %-18s Spearman %.6f holds %s%s" % (f, r["spearman"], r["holds"],
                                                              (" | %d increases between neighbouring couplings" % r["n_increases"]) if "n_increases" in r else ""))
        for k, v in R["P5"].items():
            if isinstance(v, dict):
                for kk, s in v.items():
                    print("  P5 %-25s %-11s mean miss %.4f (ok %s) | deciding %d, ratios %.4f..%.4f (median %.4f), outside at %s | all ratios %.3f..%.3f"
                          % (k, kk, s["mean_miss"], s["mean_ok"], s["n_deciding"], s["ratio_min_deciding"], s["ratio_max_deciding"],
                             s["ratio_median_deciding"], s["outside"], s["ratio_min_all"], s["ratio_max_all"]))
            else:
                print("  P5 %s: %s" % (k, v))
        c = R["n19_comparison"]
        print("  n = 19 vs truth: closer than the label at %d of 50 couplings (%d of 45 training): %s" % (c["n_n19_closer"], c["n_n19_closer_training"], c["n19_closer_than_label_at"]))
        print("     within a fifth of tau from Jz = %.1f on; max all %.3f, training %.3f; stored certificate range: %s; with E1: %s"
              % (c["within_fifth_from"], c["max_all"], c["max_training"], c["certificate_range_stored"], c["certificate_range_with_E1"]))
        print("  largest |difference| from the sealed output: %.2e (over %d compared quantities)" % (max(d.values()), len(d)))
    OUT["P5_rule_recomputed"] = {k: ("PASS" if all(OUT["sizes"][n]["P5"][k]["all"]["mean_ok"] and OUT["sizes"][n]["P5"][k]["all"]["ratios_ok"] for n in ("57", "115")) else "FAIL")
                                 for k in OUT["sizes"]["57"]["P5"] if isinstance(OUT["sizes"]["57"]["P5"][k], dict)}
    OUT["P5_rule_sealed"] = SEALED["P5_rule"]["outcome"]
    print("\nP5 rule recomputed: %s | sealed: %s" % (OUT["P5_rule_recomputed"], OUT["P5_rule_sealed"]))
    with open(os.path.join(HERE, "rd_predict_independent.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(OUT, f, indent=1, default=float)


if __name__ == "__main__":
    main()
