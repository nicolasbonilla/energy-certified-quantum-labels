"""Analysis of the Huang-benchmark certification run (DECLARATION.md sections 1, 4). numpy only, no TeNPy.

  python analyze_h.py <root> <data_dir> <out_dir>
<root> holds out/ (fetched from the VM). Writes <out_dir>/summary_huang.json and <out_dir>/tables_huang.md.

Per chain (one label of one instance):
  * ED (n = 20): inner = hull of exact eigenvectors, outer = dual lines with F_lo = Ritz value - residual.
  * DMRG: inner = hull of explicit MPS states evaluated at E0 + eps - 2 dchi_ref (E0 := chi 384 energy, dchi_ref =
    |E0(256) - E0(384)|); outer = dual lines with F_lo = F - dG, dG = max(2 dchi_c, max |G(chi_c) - G(256)| measured by
    gate P2 at that instance), dchi_c = |E0(chi_c) - E0(384)|.
  * status at delta e: CERTIFIED if w_out(n de) <= tau, NOT CERTIFIED if w_in(n de) >= tau, GRAY otherwise.
  * eps_tau (in, out), delta e* = eps_tau / n, the law delta e*_law = S tau^2 / (8 chi_two n), law / computed.
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import chain as CH  # noqa: E402
import lattice as LT  # noqa: E402

DE_GRID = [1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3, 1e-2]
TAU = 0.08
TAU2 = 0.04
LAW_BAND = (0.8, 1.25)
FEATURED = ["Cnn", "Cd2", "Ccent", "Cfar", "Cfix"]
LOCALS = ["Ccent", "Cfar", "Cfix"]
AVERAGES = ["Cnn", "Cd2", "Cstag"]


def jl(p):
    with open(p) as f:
        return json.load(f)


def eps_tau_shift(E0, o0, pts_in, pts_out, S, ob, tau, eps_hi, shift_in):
    pool = CH.pool_of(E0, o0, pts_in)

    def solve(f):
        lo, hi = 1e-9, eps_hi
        if f(hi) < tau:
            return None
        for _ in range(70):
            mid = math.sqrt(lo * hi)
            if f(mid) >= tau:
                hi = mid
            else:
                lo = mid
        return hi
    ein = solve(lambda e: CH.w_in(pool, E0 + e - shift_in))
    eout = solve(lambda e: CH.w_out(pts_out, E0 + e, S, ob))
    return ein, eout


def classify_pair(L, label):
    _, a, b = label.split("_")
    a, b = int(a), int(b)
    xa, ya = LT.coords(a)
    xb, yb = LT.coords(b)
    dx, dy = abs(xa - xb), abs(ya - yb)
    if dx + dy == 1:
        return "nn"
    if dx == 1 and dy == 1:
        return "diag"
    r = math.hypot(dx, dy)
    return "r<=3" if r <= 3.0 else "r>3"


def analyse_chain(ch, dG=0.0, shift_in=0.0, tau_paper=None):
    n, S, ob, E0, o0 = ch["n"], ch["S"], tuple(ch["obounds"]), ch["E0"], ch["o_GS"]
    pts = ch["points"]
    pts_out = [dict(p, F_lo=p["F_lo"] - dG) for p in pts]
    pool = CH.pool_of(E0, o0, pts)
    eps_hi = ch["eps_hi"]
    row = dict(L=ch["L"], k=ch["k"], n=n, label=ch["label"], method=ch["method"], S=S, o_GS=o0, dG=dG,
               shift_in=shift_in, n_points=ch["n_points"], saturated=ch["saturated"], eps_hi=eps_hi)
    chi = ch["chi_two"]
    row["chi_two"] = chi
    row["chi_site"] = chi * n / S if chi else None
    taus = {"tau": TAU, "tau2": TAU2}
    if tau_paper:
        taus["tau_paper"] = tau_paper
    row["taus"] = taus
    for key, tau in taus.items():
        ein, eout = eps_tau_shift(E0, o0, pts, pts_out, S, ob, tau, eps_hi, shift_in)
        law = S * tau ** 2 / (8.0 * chi) if chi and chi > 0 else None
        wtop = CH.w_out(pts_out, E0 + eps_hi, S, ob)
        r = dict(eps_tau_in=ein, eps_tau_out=eout, de_in=ein / n if ein else None, de_out=eout / n if eout else None,
                 eps_law=law, de_law=law / n if law else None,
                 out_lower_bound=(eout is None and wtop < tau), eps_out_lb=eps_hi if (eout is None and wtop < tau)
                 else None)
        r["law_over_out"] = (law / eout) if (law and eout) else None
        r["law_over_in"] = (law / ein) if (law and ein) else None
        st = []
        ws = []
        for de in DE_GRID:
            e = n * de
            wi = CH.w_in(pool, E0 + e - shift_in)
            wo = CH.w_out(pts_out, E0 + e, S, ob)
            s = "C" if wo <= tau else ("N" if wi >= tau else "G")
            st.append(s)
            ws.append(dict(de=de, w_in=wi, w_out=wo))
        r["status"] = st
        r["widths"] = ws
        row[key] = r
    return row


def tau_paper_of(data_dir, L, k, nlines=None):
    """2 x RMSE (over pairs i < j) of the notebook's shadow estimator of C_ij (all snapshots of *_samples.txt, or
    the first nlines) against *_XX.txt: the noise of the benchmark's own training labels."""
    I = LT.load_instance(data_dir, L, k)
    n = I["n"]
    S = np.loadtxt(os.path.join(data_dir, "heisenberg_%dx5_id%d_samples.txt" % (L, k)), dtype=int)
    if nlines:
        S = S[:nlines]
    basis, out = S // 2, S % 2
    sq = []
    for i in range(n):
        for j in range(i + 1, n):
            same = basis[:, i] == basis[:, j]
            val = np.where(same, np.where(out[:, i] == out[:, j], 3.0, -3.0), 0.0)
            sq.append((val.mean() - I["XX"][i][j]) ** 2)
    rmse = float(np.sqrt(np.mean(sq)))
    return dict(rmse=rmse, tau_paper=2 * rmse, T=int(len(S)))


def main(root, data_dir, outdir):
    O = os.path.join(root, "out")
    summ = dict(rows=[], pairs={}, gates={}, refs={}, claims={})
    # ---------------------------------------------------------------- tolerance of the benchmark itself (record)
    tp = {}
    for f in sorted(glob.glob(os.path.join(O, "ed", "ref_*.json")) + glob.glob(os.path.join(O, "refs", "ref_*.json"))):
        d = jl(f)
        key = (d["L"], d["k"])
        if key not in tp:
            tp[key] = tau_paper_of(data_dir, *key)
            tp[key]["T500"] = tau_paper_of(data_dir, key[0], key[1], 500)
    summ["tau_paper"] = {"%d_%d" % k: v for k, v in tp.items()}
    tpap = float(np.mean([v["tau_paper"] for v in tp.values()])) if tp else None
    summ["tau_paper_mean"] = tpap
    # ---------------------------------------------------------------- ED references and chains
    edref = {}
    for f in sorted(glob.glob(os.path.join(O, "ed", "ref_*.json"))):
        d = jl(f)
        edref[(d["L"], d["k"])] = d
        summ["refs"]["ED_%d_%d" % (d["L"], d["k"])] = {kk: d[kk] for kk in (
            "n", "dim", "E0", "E1_sector", "residual", "E_from_C", "E_file_x2", "dE_vs_file", "max_dC_vs_XX",
            "max_dC_vs_mean3", "rms_dC_vs_XX", "sz_mean", "sz_var", "labels", "time_s")}
        summ["refs"]["ED_%d_%d" % (d["L"], d["k"])]["gap"] = d["E1_sector"] - d["E0"]
    for f in sorted(glob.glob(os.path.join(O, "ed", "chains", "*.json"))):
        ch = jl(f)
        row = analyse_chain(ch, 0.0, 0.0, tpap)
        gap = edref[(ch["L"], ch["k"])]["E1_sector"] - edref[(ch["L"], ch["k"])]["E0"]
        row["gap"] = gap
        row["max_residual"] = max(p["residual"] for p in ch["points"])
        if ch["label"].startswith("P_"):
            row["cls"] = classify_pair(ch["L"], ch["label"])
            summ["pairs"].setdefault("%d_%d" % (ch["L"], ch["k"]), []).append(row)
        else:
            summ["rows"].append(row)
            if ch["label"] == "Ccent" and ch["L"] == 4:          # Cfix = Ccent at L = 4 (same bond 7-12)
                summ["rows"].append(dict(row, label="Cfix", alias_of="Ccent"))
    # ---------------------------------------------------------------- DMRG references, gates P2/P3, chains
    dref = {}
    for f in sorted(glob.glob(os.path.join(O, "refs", "ref_*.json"))):
        d = jl(f)
        st = {s["chi"]: s["E"] for s in d["stages"]}
        d["dchi_ref"] = abs(st[256] - st[384]) if (256 in st and 384 in st) else None
        d["dchi_c"] = abs(d["E_chic"] - d["E0"])
        dref[(d["L"], d["k"])] = d
        summ["refs"]["DMRG_%d_%d" % (d["L"], d["k"])] = dict(
            n=d["n"], E_by_chi=st, E0=d["E0"], chi_c=d["chi_c"], dchi_c=d["dchi_c"], dchi_ref=d["dchi_ref"],
            E_file_x2=d["E_file_x2"], dE_vs_file=d["dE_vs_file"], max_dC_vs_XX=d["max_dC_vs_XX"],
            rms_dC_vs_XX=d["rms_dC_vs_XX"], labels=d["labels"],
            in_sector=[s["in_sector"] for s in d["stages"]], times=[s["dmrg"]["time_s"] for s in d["stages"]])
    chk = {}
    for f in sorted(glob.glob(os.path.join(O, "chk", "*.json"))):
        d = jl(f)
        chk.setdefault((d["L"], d["k"]), []).append(d)
    cold = [jl(f) for f in sorted(glob.glob(os.path.join(O, "cold", "*.json")))]
    for f in sorted(glob.glob(os.path.join(O, "chains", "*.json"))):
        ch = jl(f)
        R = dref[(ch["L"], ch["k"])]
        dG = max([2.0 * R["dchi_c"]] + [abs(c["dG"]) for c in chk.get((ch["L"], ch["k"]), [])])
        shift = 2.0 * (R["dchi_ref"] or 0.0)
        row = analyse_chain(ch, dG, shift, tpap)
        row["dchi_c"], row["dchi_ref"] = R["dchi_c"], R["dchi_ref"]
        row["max_dO_tenpy"] = max(abs(p["o"] - p["o_tenpy"]) for p in ch["points"])
        row["all_in_sector"] = all(p["in_sector"] for p in ch["points"])
        # POST-HOC sensitivity (DEVIATIONS 4; not a declared quantity): the same chain referenced to the chi_c = 256
        # ground state (same truncation as the chain states, so the chain offset cancels to leading order)
        sp_ = os.path.join(O, "states", "L%dk%d_R1_chi%d.json" % (ch["L"], ch["k"], R["chi_c"]))
        if os.path.exists(sp_):
            g = jl(sp_)
            P, Wt, S_, ob_ = LT.label_pairs(ch["L"], ch["label"])
            o0c = sum(w_ * g["indep"]["C"]["%d_%d" % tuple(sorted(pp))] for pp, w_ in zip(P, Wt)) / S_
            chc = dict(ch, E0=R["E_chic"], o_GS=o0c)
            rc = analyse_chain(chc, dG, 0.0, None)
            row["same_chi_ref"] = dict(E0=R["E_chic"], o_GS=o0c, eps_tau_in=rc["tau"]["eps_tau_in"],
                                       eps_tau_out=rc["tau"]["eps_tau_out"], de_out=rc["tau"]["de_out"],
                                       law_over_out=rc["tau"]["law_over_out"], status=rc["tau"]["status"])
        summ["rows"].append(row)
    # ---------------------------------------------------------------- gates
    G = summ["gates"]
    # G2: dataset agreement (convention gate)
    g2 = []
    for key, d in edref.items():
        g2.append(dict(src="ED", L=key[0], k=key[1], max_dC=d["max_dC_vs_XX"], rel_dE=abs(d["E0"] / d["E_file_x2"] - 1)))
    for key, d in dref.items():
        g2.append(dict(src="DMRG", L=key[0], k=key[1], max_dC=d["max_dC_vs_XX"],
                       rel_dE=abs(d["E0"] / d["E_file_x2"] - 1)))
    G["G2"] = dict(rows=g2, passed=all(r["max_dC"] <= 0.01 and r["rel_dE"] <= 1e-3 for r in g2))
    # G1: DMRG pipeline at n = 20 (instance 4, 1; chi_c = 128) vs ED
    g1 = []
    byk = {(r["L"], r["k"], r["label"], r["method"]): r for r in summ["rows"]}
    for lab in ("Cnn", "Ccent", "Cfar"):
        a, b = byk.get((4, 1, lab, "ED")), byk.get((4, 1, lab, "DMRG"))
        if not (a and b):
            continue
        ra, rb = a["tau"], b["tau"]
        ex = None
        for key in ("eps_tau_in", "eps_tau_out"):
            if ra["eps_tau_out"] and rb[key]:
                d = abs(rb[key] / (0.5 * (ra["eps_tau_in"] + ra["eps_tau_out"])) - 1)
                ex = max(ex or 0, d)
        dw = max(abs(wb["w_out"] - 0.5 * (wa["w_in"] + wa["w_out"])) / (0.5 * (wa["w_in"] + wa["w_out"]))
                 for wa, wb in zip(ra["widths"], rb["widths"]) if wb["de"] in (1e-3, 1e-2))
        g1.append(dict(label=lab, max_rel_d_eps_tau=ex, max_rel_d_wout_aimed=dw, ed_gap_rel=max(
            (wa["w_out"] - wa["w_in"]) / wa["w_out"] for wa in ra["widths"])))
    R41 = dref.get((4, 1))
    e_true = edref.get((4, 1), {}).get("E0")
    G["G1"] = dict(rows=g1, passed=bool(g1) and all((r["max_rel_d_eps_tau"] or 0) <= 0.05 and
                                                    r["max_rel_d_wout_aimed"] <= 0.01 for r in g1),
                   E0_errors=({str(c): E - e_true for c, E in summ["refs"]["DMRG_4_1"]["E_by_chi"].items()}
                              if (R41 and e_true is not None) else None))
    # P1: reference convergence relative to the smallest featured local eps_tau of the instance
    p1 = []
    for key, d in dref.items():
        rows = [r for r in summ["rows"] if (r["L"], r["k"]) == key and r["method"] == "DMRG"]
        loc = [r["tau"]["eps_tau_out"] for r in rows if r["label"] in LOCALS and r["tau"]["eps_tau_out"]]
        m = min(loc) if loc else None
        p1.append(dict(L=key[0], k=key[1], dchi_c=d["dchi_c"], dchi_ref=d["dchi_ref"], min_local_eps_tau=m,
                       ratio_c=(d["dchi_c"] / m) if m else None, ratio_ref=(d["dchi_ref"] / m) if m else None))
    G["P1"] = dict(rows=p1, passed=all((r["ratio_ref"] or 0) <= 0.02 for r in p1),
                   note="dchi_ref <= 0.02 min local eps_tau (reference); dchi_c enters the outer margin")
    p2 = []
    for key, L_ in chk.items():
        for c in L_:
            r = byk.get((c["L"], c["k"], c["label"], "DMRG"))
            e = r["tau"]["eps_tau_out"] if r else None
            p2.append(dict(L=c["L"], k=c["k"], label=c["label"], sign=c["sign"], lam=c["lam"], dG=c["dG"],
                           eps_tau_out=e, ratio=abs(c["dG"]) / e if e else None))
    G["P2"] = dict(rows=p2, passed=all((r["ratio"] or 0) <= 0.01 for r in p2))
    G["P3"] = dict(rows=[dict(L=c["L"], k=c["k"], label=c["label"], sign=c["sign"], dF=c["dF"],
                              stuck=c["flag_warm_stuck"]) for c in cold],
                   passed=all(not c["flag_warm_stuck"] for c in cold))
    # P4: every stored DMRG state in sector, TeNPy vs independent evaluator
    p4 = dict(n=0, out_of_sector=0, max_dE=0.0, max_dC=0.0, max_dnorm=0.0)
    for f in glob.glob(os.path.join(O, "states", "*.json")):
        s = jl(f)
        p4["n"] += 1
        p4["out_of_sector"] += 0 if s["in_sector"] else 1
        p4["max_dE"] = max(p4["max_dE"], s["agree"]["dE"])
        p4["max_dC"] = max(p4["max_dC"], s["agree"]["dC"])
        p4["max_dnorm"] = max(p4["max_dnorm"], s["agree"]["dnorm_rel"])
    p4["passed"] = p4["out_of_sector"] == 0 and p4["max_dE"] < 1e-8 and p4["max_dC"] < 1e-8 and p4["max_dnorm"] < 1e-8
    G["P4"] = p4
    gf = os.path.join(O, "g4", "g4_check.json")
    G["G4"] = jl(gf) if os.path.exists(gf) else None
    # ---------------------------------------------------------------- law scan (record)
    scans = []
    for f in sorted(glob.glob(os.path.join(O, "lawscan", "*.json"))):
        scans += jl(f)["rows"]
    summ["lawscan"] = dict(rows=scans, n=len(scans))
    # ---------------------------------------------------------------- pair-label aggregates (n = 20)
    agg = {}
    for key, rows in summ["pairs"].items():
        a = dict(n_labels=len(rows), counts={}, de_star={}, law={})
        for tk in ("tau", "tau2", "tau_paper"):
            if tk not in rows[0]:
                continue
            a["counts"][tk] = [dict(de=de, C=sum(r[tk]["status"][i] == "C" for r in rows),
                                    N=sum(r[tk]["status"][i] == "N" for r in rows),
                                    G=sum(r[tk]["status"][i] == "G" for r in rows)) for i, de in enumerate(DE_GRID)]
        for cls in ("all", "nn", "diag", "r<=3", "r>3"):
            sel = [r for r in rows if cls == "all" or r["cls"] == cls]
            v = [r["tau"]["de_out"] for r in sel if r["tau"]["de_out"]]
            lr = [r["tau"]["law_over_out"] for r in sel if r["tau"]["law_over_out"]]
            if v:
                a["de_star"][cls] = dict(n=len(sel), min=min(v), p10=float(np.percentile(v, 10)),
                                         median=float(np.median(v)), p90=float(np.percentile(v, 90)), max=max(v))
            if lr:
                a["law"][cls] = dict(n=len(lr), min=min(lr), median=float(np.median(lr)), max=max(lr),
                                     frac_in_band=float(np.mean([LAW_BAND[0] <= x <= LAW_BAND[1] for x in lr])))
        agg[key] = a
    summ["pair_aggregates"] = agg
    # ---------------------------------------------------------------- claims (DECLARATION section 4)
    C = summ["claims"]
    allpairs = [r for rows in summ["pairs"].values() for r in rows]
    n_c_1e3 = sum(r["tau"]["status"][0] == "C" for r in allpairs)
    n_c_1e2 = sum(r["tau"]["status"][-1] == "C" for r in allpairs)
    C["C-H1"] = dict(rule="no n = 20 pair correlator CERTIFIED at delta e = 1e-3 (all computed pairs, 3 instances)",
                     n_pairs=len(allpairs), certified_at_1e3=n_c_1e3, certified_at_1e2=n_c_1e2,
                     holds=(n_c_1e3 == 0) if allpairs else None)
    loc = [r for r in summ["rows"] if r["label"] in LOCALS and r["n"] > 20]
    C["C-H2"] = dict(rule="Ccent, Cfar and Cfix NOT CERTIFIED (rigorous inner side) at delta e = 1e-3 at every n = 30, 45 "
                          "instance", rows=[(r["L"], r["k"], r["label"], r["tau"]["status"][0]) for r in loc],
                     holds=all(r["tau"]["status"][0] == "N" for r in loc) if loc else None)
    av = [r for r in summ["rows"] if r["label"] == "Cnn" and not (r["method"] == "DMRG" and r["n"] == 20)]
    C["C-H3"] = dict(rule="Cnn CERTIFIED at delta e = 1e-3 at all six instances (record: at 1e-2)",
                     rows=[(r["L"], r["k"], r["tau"]["status"][0], r["tau"]["status"][-1]) for r in av],
                     holds=all(r["tau"]["status"][0] == "C" for r in av) if av else None,
                     certified_at_1e2_all=all(r["tau"]["status"][-1] == "C" for r in av) if av else None)
    law_av = [r for r in summ["rows"] if r["label"] in ("Cnn", "Cd2") and not (r["method"] == "DMRG" and r["n"] == 20)]
    law_loc = [r for r in summ["rows"] if r["label"] in LOCALS and not (r["method"] == "DMRG" and r["n"] == 20)]

    def inband(r):
        x = r["tau"]["law_over_out"]
        return x is not None and LAW_BAND[0] <= x <= LAW_BAND[1]
    fr = [r["tau"]["law_over_out"] for r in allpairs if r["tau"]["law_over_out"]]
    C["C-H4"] = dict(rule="law / computed in [0.8, 1.25] for every Cnn and Cd2 row (averages) and for every Ccent, "
                          "Cfar, Cfix row (local); pair labels: fraction in band >= 0.9",
                     averages=[(r["L"], r["k"], r["label"], r["tau"]["law_over_out"]) for r in law_av],
                     local=[(r["L"], r["k"], r["label"], r["tau"]["law_over_out"]) for r in law_loc],
                     averages_hold=all(inband(r) for r in law_av) if law_av else None,
                     local_hold=all(inband(r) for r in law_loc) if law_loc else None,
                     pairs_frac_in_band=float(np.mean([LAW_BAND[0] <= x <= LAW_BAND[1] for x in fr])) if fr else None,
                     pairs_hold=(float(np.mean([LAW_BAND[0] <= x <= LAW_BAND[1] for x in fr])) >= 0.9) if fr else None)
    sp = {}
    for lab in FEATURED + ["Cstag"]:
        for nn_ in (20, 30, 45):
            rs = [r for r in summ["rows"] if r["label"] == lab and r["n"] == nn_ and
                  not (r["method"] == "DMRG" and nn_ == 20)]
            v = [r["tau"]["de_out"] if r["tau"]["de_out"] else r["tau"]["eps_out_lb"] / r["n"] if
                 r["tau"]["eps_out_lb"] else None for r in rs]
            v = [x for x in v if x]
            if v:
                sp["%s_%d" % (lab, nn_)] = dict(n_inst=len(v), min=min(v), max=max(v), mean=float(np.mean(v)),
                                                 values=v)
    summ["spread"] = sp
    # C-H5: size dependence. (a) Cfix in the k = 1 family (same bond, same local couplings at n = 20, 30, 45): eps_tau
    # (extensive cost) O(1), i.e. eps_tau(n) / eps_tau(20) in [0.67, 1.5] and de* ~ 1/n; (b) Cnn intensive:
    # de*(n) / mean de*(20) in [0.67, 1.5] at n = 30, 45.
    def eout(L, k, lab):
        r = byk.get((L, k, lab, "ED" if L == 4 else "DMRG"))
        if lab == "Cfix" and L == 4:
            r = byk.get((4, k, "Ccent", "ED"))
        return (r["tau"]["eps_tau_out"] or r["tau"]["eps_out_lb"]) if r else None
    fx = {"%d_%d" % (L, k): eout(L, k, "Cfix") for (L, k) in ((4, 1), (6, 1), (9, 1), (4, 2), (9, 2))}
    ra = {}
    for (L, k) in ((6, 1), (9, 1), (9, 2)):
        a_, b_ = fx["%d_%d" % (L, k)], fx["4_%d" % k]
        ra["%d_%d" % (L, k)] = (a_ / b_) if (a_ and b_) else None
    m20 = sp.get("Cnn_20", {}).get("mean")
    rb = {}
    for nn_ in (30, 45):
        d = sp.get("Cnn_%d" % nn_)
        if d and m20:
            rb[nn_] = [v / m20 for v in d["values"]]
    C["C-H5"] = dict(rule="(a) Cfix, k = 1 and k = 2 families: eps_tau(n)/eps_tau(20, same k) in [0.67, 1.5] at "
                          "n = 30, 45; (b) Cnn: "
                          "de*(n)/mean de*(20) in [0.67, 1.5] at every n = 30, 45 instance",
                     cfix_eps_tau=fx, cfix_ratio=ra, cnn_ratio=rb,
                     holds_a=all(x is not None and 0.67 <= x <= 1.5 for x in ra.values()) if ra else None,
                     holds_b=all(0.67 <= x <= 1.5 for v in rb.values() for x in v) if rb else None,
                     spread=sp)
    C["C-H5"]["holds"] = (C["C-H5"]["holds_a"], C["C-H5"]["holds_b"])
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "summary_huang.json"), "w") as f:
        json.dump(summ, f, indent=1)
    write_tables(summ, os.path.join(outdir, "tables_huang.md"))
    print(json.dumps(dict(claims={k: v.get("holds") for k, v in C.items()},
                          gates={k: (v.get("passed") if isinstance(v, dict) else v) for k, v in G.items()}), indent=1))


def f3(x, d=3):
    if x is None:
        return "-"
    if isinstance(x, float) and (abs(x) < 1e-3 or abs(x) >= 1e4) and x != 0:
        return ("%." + str(d - 1) + "e") % x
    return ("%." + str(d) + "g") % x


def write_tables(s, path):
    L = []
    L.append("# Huang benchmark: tables (generated by analyze_h.py)\n")
    L.append("delta e grid: " + ", ".join("%g" % d for d in DE_GRID) + "; tau = %.2f (primary), %.2f (tau2), "
             "tau_paper = %s (record)\n" % (TAU, TAU2, f3(s.get("tau_paper_mean"))))
    L.append("## Featured labels\n")
    L.append("| inst (L,k) | n | method | label | O_GS | chi_site (avg) / chi_i (local) | de*_law | de*_in | de*_out | "
             "law/out | status tau (de grid) | status tau2 | w_out/tau at 1e-3, 1e-2 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(s["rows"], key=lambda r: (r["label"], r["n"], r["k"], r["method"])):
        t = r["tau"]
        chi = r["chi_site"] if r["label"] in AVERAGES else r["chi_two"]
        deo = f3(t["de_out"]) if t["de_out"] else ("> %s" % f3(t["eps_out_lb"] / r["n"]) if t["eps_out_lb"] else "-")
        L.append("| (%d,%d) | %d | %s | %s | %.5f | %s | %s | %s | %s | %s | %s | %s | %.2f, %.2f |" % (
            r["L"], r["k"], r["n"], r["method"], r["label"], r["o_GS"], f3(chi), f3(t["de_law"]), f3(t["de_in"]), deo,
            f3(t["law_over_out"]), "".join(t["status"]), "".join(r["tau2"]["status"]),
            t["widths"][0]["w_out"] / TAU, t["widths"][-1]["w_out"] / TAU))
    L.append("\n## Pair labels at n = 20 (ED): counts per delta e (C / N / G) at tau\n")
    for key, a in sorted(s["pair_aggregates"].items()):
        L.append("**instance %s** (%d labels)\n" % (key, a["n_labels"]))
        for tk, rows in a["counts"].items():
            L.append("- %s: " % tk + "; ".join("%g: %d/%d/%d" % (c["de"], c["C"], c["N"], c["G"]) for c in rows))
        L.append("")
        L.append("| class | n | de* min | p10 | median | p90 | max | law/out median | frac law in band |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for cls, d in a["de_star"].items():
            lw = a["law"].get(cls, {})
            L.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s |" % (
                cls, d["n"], f3(d["min"]), f3(d["p10"]), f3(d["median"]), f3(d["p90"]), f3(d["max"]),
                f3(lw.get("median")), f3(lw.get("frac_in_band"))))
        L.append("")
    L.append("## Gates\n")
    for k, v in s["gates"].items():
        L.append("- **%s**: %s" % (k, json.dumps(v)[:1500]))
    L.append("\n## Claims\n")
    for k, v in s["claims"].items():
        L.append("- **%s**: %s" % (k, json.dumps(v)[:1500]))
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
