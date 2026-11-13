# real_data / rd_learn_ibm.py  (DERIVED FILE, written by make_derived.py; 2026-11-12; task rd-code-learn)
#
# Derived from learning_ibm/code/learn_ibm.py (SHA-256 f1642735d7e1123c62dba5593831c8bf769995659e1ab04c1a65349ca6a1c549), changed ONLY in the data loader:
#   --data=real      (default) the public labels of arXiv:2606.15983, through rd_common (needs the hashed
#                    declaration: --hash=<SHA-256 of DECLARATION.md>; refuses otherwise)
#   --data=emulated  the stored emulated labels, with the ORIGINAL loader kept verbatim (port check)
# Every line marked "# RD" is new; everything else is a verbatim copy of the stored script, whose docstring
# follows unchanged (where it says "emulated", read "the labels of the chosen data source").
"""Realistic learning test on the 57/115-qubit heavy-hex XXZ model (final-fix pass, 2026-11-04).

Light post-processing of stored outputs only: no DMRG, no diagonalization, no new emulation.

Inputs (read-only)
  method/out_20261030T003230Z/out/emu/emu_n<n>_J*.json   emulated first-stage states of the dataset's method
                                                         (labels Z_i, m_s, energy E); 'primary' = the declared label
                                                         variant, 'ideal' = a second emulated state at the same Jz
  method/out_20261030T003230Z/out/ref/ref_n<n>_J*.json   DMRG reference (the truth)
  map/laptop_analysis/summary_map.json                    certification map (eps_tau_out, windows, tau, status)
  qpu/analysis/analysis.json                              our device points (illustration only)
  method/code/ml2.py, method/code/graphs/hh_d*.json        the regressors of the method test (imported, not changed)

Design (fixed before any output of this script was read; the earlier ml2.py numbers were known)
  couplings      all stored couplings with both an emulated state and a DMRG reference; training range
                 R = {Jz >= 1.6}; out-of-distribution (OOD) range {1.1, 1.2, 1.3, 1.4}
  labels         per-site <Z_i> (local; the dataset paper learns one model per site) and m_s = sum_i eta_i Z_i / n
                 (average, derived from the per-site model as in ml2.py and in the dataset paper)
  models         cubic in 1/Jz (linear in its labels), the small MLP of the pilot, the 'IBM-like' architecture 1
                 (OOD test only, for cost), nearest-neighbour null
  calibration    standard conformal, alpha = 0.1, on held-out emulated labels: each training coupling is held out in
                 turn (leave-one-coupling-out, the jackknife form of split conformal); interval = prediction of the
                 model trained on all training couplings +- q, q = the ceil((1-alpha)(N+1))-th smallest held-out
                 residual (N = number of held-out residuals; pooled over sites for <Z_i>). With N couplings the
                 attainable level for m_s is N/(N+1) when that is below 0.9 (n = 115), reported as 'level'.
  tests          OOD: train/calibrate on R, test at 1.1-1.4. In distribution: hold out one test coupling t in R,
                 train/calibrate on R \\ {t}, repeat over t.
                 Coverage of (i) new emulated labels (the held-out 'primary' labels; and the 'ideal' state) and
                 (ii) the DMRG truth. Widths in units of tau = 0.06 |o_GS| (per site for <Z_i>, as in the map).
  control        the same models and calibration trained on DMRG labels (exact-label control: model error only)
  robustness     per-site split conformal with 3 (n = 57) / 2 (n = 115) held-out calibration couplings, all choices
                 (cubic and nearest-neighbour only)
  certified      the map's window at the emulated label's own energy eps_emu: certified (width <= tau) iff
                 eps_emu <= eps_tau_out of that label and coupling; width bounds from the stored windows (window
                 width is non-decreasing in eps): >= w_in at the largest stored eps <= eps_emu, <= w_out at the
                 smallest stored eps >= eps_emu. Local labels use the map's representative rows Z_bulk, Z_boundary
                 (both must certify). Couplings without a map row: abstain.
  abstention     physics-derived: answer a query only where the map certifies that label at the label's energy.

  python -I learn_ibm.py <J_next_paper root> <out dir> [--fast] [--models=a,b] [--sizes=57,115] [--tag=x] [--no-indist=m1,m2]
  python -I learn_ibm.py <J_next_paper root> <out dir> --merge      (merges results_<tag>.json into results.json)
  Run single-threaded (OMP_NUM_THREADS=1); the jobs of the final-fix pass are listed in ../README.md.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")   # tiny matrices: one BLAS thread is much faster
import glob
import itertools
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
FAST = "--fast" in sys.argv
ARG = {a.split("=")[0][2:]: a.split("=", 1)[1] for a in sys.argv[3:] if "=" in a}
MODELS = ARG["models"].split(",") if "models" in ARG else None
SIZES = [int(s) for s in ARG["sizes"].split(",")] if "sizes" in ARG else [57, 115]
NO_INDIST = ARG.get("no-indist", "ibm_arch1").split(",")
TAG = ARG.get("tag")
METHOD = os.path.join(ROOT, "phase3", "full_runs", "method")
EMU = os.path.join(METHOD, "out_20261030T003230Z", "out")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(METHOD, "code"))
import ml2  # noqa: E402  (read-only import; no bytecode written)

# RD ---- data source (begin)
DATA = ARG.get("data", "real")  # RD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # RD
import rd_common as rdc  # noqa: E402  # RD
GATE = None  # RD
if DATA == "real" and "--merge" not in sys.argv:  # RD
    if "hash" not in ARG:  # RD
        raise rdc.Refused("--hash=<SHA-256 of the hashed declaration> is required to read the real data.")  # RD
    GATE = rdc.require_declaration_hash(rdc.RD, ARG["hash"])  # RD: refuses unless DECLARATION.sha256 matches
elif DATA not in ("real", "emulated"):  # RD
    raise SystemExit("--data must be real or emulated")  # RD
# RD ---- data source (end)

ALPHA = 0.1
OOD = [1.1, 1.2, 1.3, 1.4]
TRAIN_MIN = 1.6
TAU_REL = 0.06


def rj(p):
    with open(p) as f:
        return json.load(f)


def load_emulated(n):  # RD: the stored loader, renamed; body verbatim
    G = rj(os.path.join(METHOD, "code", "graphs", "hh_d%d.json" % {57: 5, 115: 7}[n]))
    eta = np.array(G["eta"], float)
    D = {}
    for p in glob.glob(os.path.join(EMU, "emu", "emu_n%d_J*.json" % n)):
        e = rj(p); J = round(e["Jz"], 1)
        r = rj(os.path.join(EMU, "ref", "ref_n%d_J%s.json" % (n, ("%g" % J if J != int(J) else "%.1f" % J))))
        v = e["var"]
        D[J] = dict(E0=e["E0"], Z_lab=np.array(v["primary"]["labels"]["Z"]), eps=v["primary"]["E"] - e["E0"],
                    Z_ideal=np.array(v["ideal"]["labels"]["Z"]) if "ideal" in v else None,
                    eps_ideal=(v["ideal"]["E"] - e["E0"]) if "ideal" in v else None,
                    Z_ref=np.array(r["labels"]["Z"]))
    return eta, len(G["edges"]), D


def load_real(n):  # RD
    """RD: the public labels. Z_lab = z_basis_opt; Z_ref = the authors' DMRG (declaration Sec. 7); eps = E_real - E0
    with E0 of declaration Sec. 0; no second state (Z_ideal = None)."""
    return rdc.learning_dict(rdc.load_real(n, GATE, ROOT, ARG.get("converted")))  # RD


def load(n):  # RD
    return load_emulated(n) if DATA == "emulated" else load_real(n)  # RD


def qconf(scores, alpha=ALPHA):
    s = np.sort(np.ravel(scores)); N = len(s)
    k = int(np.ceil((1 - alpha) * (N + 1)))
    if k > N:                      # level not attainable: use the max, report the level N/(N+1)
        return float(s[-1]), N / (N + 1)
    return float(s[k - 1]), 1 - alpha


def fitters(n_in):
    return dict(poly3_invJ=ml2.fit_poly, mlp_pilot3=ml2.fit_mlp,
                ibm_arch1=lambda J, Y: ml2.fit_ibm(J, Y, n_in), null_nn=ml2.fit_nn)


def loo_calib(fit, Js, Y, eta):
    """Leave-one-coupling-out residuals on the couplings Js (labels Y[J]). Returns pooled per-site residuals and m_s
    residuals."""
    rZ, rM = [], []
    for k in Js:
        tr = [j for j in Js if j != k]
        f = fit(tr, np.array([Y[j] for j in tr]))
        p = f(k)[0]
        rZ.append(np.abs(p - Y[k])); rM.append(abs(ml2.ms(p, eta) - ml2.ms(Y[k], eta)))
    return np.concatenate(rZ), np.array(rM)


def evaluate(fit, Js_train, Ylab, tests, D, eta, label_key):
    """Train on Js_train with labels Ylab, calibrate by LOO, evaluate at the test couplings."""
    f = fit(Js_train, np.array([Ylab[j] for j in Js_train]))
    rZ, rM = loo_calib(fit, Js_train, Ylab, eta)
    qZ, lvZ = qconf(rZ); qM, lvM = qconf(rM)
    rows = []
    for t in tests:
        p = f(t)[0]; d = D[t]
        Zt, Zl = d["Z_ref"], d["Z_lab"]
        tauZ = TAU_REL * np.abs(Zt)
        mp, mt, ml = ml2.ms(p, eta), ml2.ms(Zt, eta), ml2.ms(Zl, eta)
        tauM = TAU_REL * abs(mt)
        row = dict(Jz=t, qZ=qZ, qM=qM,
                   covZ_truth=float(np.mean(np.abs(p - Zt) <= qZ)),
                   covZ_emu=float(np.mean(np.abs(p - Zl) <= qZ)),
                   widthZ_tau_median=float(np.median(2 * qZ / tauZ)),
                   covM_truth=bool(abs(mp - mt) <= qM), covM_emu=bool(abs(mp - ml) <= qM),
                   widthM_tau=float(2 * qM / tauM),
                   m_s_pred=mp, m_s_truth=mt, m_s_emu=ml,
                   err_ms_vs_truth_pct=abs(mp - mt) / mt * 100, err_ms_vs_emu_pct=abs(mp - ml) / ml * 100,
                   bias_ms_label=ml - mt, miss_ms_over_tau=abs(mp - mt) / tauM)
        if d["Z_ideal"] is not None:
            mi = ml2.ms(d["Z_ideal"], eta)
            row.update(covZ_ideal=float(np.mean(np.abs(p - d["Z_ideal"]) <= qZ)), covM_ideal=bool(abs(mp - mi) <= qM))
        rows.append(row)
    return dict(levelZ=lvZ, levelM=lvM, qZ=qZ, qM=qM, rows=rows), f


def summarize(rows):
    k = lambda key: [r[key] for r in rows if key in r]
    out = dict(n_cases=len(rows),
               covZ_truth=float(np.mean(k("covZ_truth"))), covZ_emu=float(np.mean(k("covZ_emu"))),
               covM_truth=float(np.mean(k("covM_truth"))), covM_emu=float(np.mean(k("covM_emu"))),
               widthZ_tau_median=float(np.median(k("widthZ_tau_median"))),
               widthM_tau_median=float(np.median(k("widthM_tau"))),
               widthM_tau_range=[float(min(k("widthM_tau"))), float(max(k("widthM_tau")))],
               err_ms_vs_truth_pct_range=[float(min(k("err_ms_vs_truth_pct"))), float(max(k("err_ms_vs_truth_pct")))],
               err_ms_vs_emu_pct_max=float(max(k("err_ms_vs_emu_pct"))),
               miss_ms_over_tau_range=[float(min(k("miss_ms_over_tau"))), float(max(k("miss_ms_over_tau")))])
    if k("covZ_ideal"):
        out.update(covZ_ideal=float(np.mean(k("covZ_ideal"))), covM_ideal=float(np.mean(k("covM_ideal"))))
    return out


def map_rows():
    M = rj(os.path.join(ROOT, "phase3", "full_runs", "map", "laptop_analysis", "summary_map.json"))
    return {(r["n"], round(r["Jz"], 1), r["label"]): r for r in M["rows"]}


def cert_at(row, eps):
    """Certified status and width bounds (units of tau) of the map's window at energy excess eps."""
    if row is None:
        return dict(row=False, certified=False)
    et = row.get("eps_tau_out")
    emax = row.get("eps_max_computed")
    if et is None:                  # never reached tau within the computed range
        cert = emax is not None and eps <= emax
    else:
        cert = eps <= et
    st = sorted([(row[a]["eps"], row[a]["w_in"], row[a]["w_out"]) for a in ("at_lo", "at_dig", "at_up")
                 if row.get(a) and row[a].get("w_in") is not None])
    lo = [w_in for e, w_in, _ in st if e <= eps]
    hi = [w_out for e, _, w_out in st if e >= eps]
    tau = row["tau"]
    return dict(row=True, certified=bool(cert), eps_tau_out=et, status_map=row["status"],
                width_tau_ge=(lo[-1] / tau) if lo else None, width_tau_le=(hi[0] / tau) if hi else None)


def main():
    t0 = time.time()
    MR = map_rows()
    res = dict(alpha=ALPHA, ood=OOD, train_min=TRAIN_MIN, tau_rel=TAU_REL, sizes={})
    qpu = rj(os.path.join(ROOT, "phase3", "full_runs", "qpu", "analysis", "analysis.json"))
    for n in SIZES:
        eta, n_in, D = load(n)
        Js = sorted(D)
        R = [j for j in Js if j >= TRAIN_MIN]
        od = [j for j in Js if j in OOD]
        F = fitters(n_in)
        S = dict(couplings=Js, train=R, ood=od, n_couplings=len(Js), models={})
        Ylab = {j: D[j]["Z_lab"] for j in Js}
        Yref = {j: D[j]["Z_ref"] for j in Js}
        for mname, fit in F.items():
            if FAST and mname in ("mlp_pilot3", "ibm_arch1"):
                continue
            if MODELS is not None and mname not in MODELS:
                continue
            ts = time.time()
            M = {}
            for src, Y in (("emulated", Ylab), ("exact_control", Yref)):
                ev, _ = evaluate(fit, R, Y, od, D, eta, src)
                M["ood_" + src] = dict(summary=summarize(ev["rows"]), levelZ=ev["levelZ"], levelM=ev["levelM"],
                                       rows=ev["rows"])
                if mname not in NO_INDIST:   # in-distribution test (cost: N(N-1) fits per source)
                    rows = []
                    for t in R:
                        ev2, _ = evaluate(fit, [j for j in R if j != t], Y, [t], D, eta, src)
                        rows += [dict(r, levelZ=ev2["levelZ"], levelM=ev2["levelM"]) for r in ev2["rows"]]
                    M["indist_" + src] = dict(summary=summarize(rows), rows=rows)
            M["secs"] = time.time() - ts
            S["models"][mname] = M
            o = M["ood_emulated"]["summary"]; c = M["ood_exact_control"]["summary"]
            print("n=%d %-11s OOD: covZ truth %.3f emu %.3f | covM truth %.2f emu %.2f | wM/tau %.2f | err vs truth "
                  "%.1f-%.1f%% (control %.1f-%.1f%%) | %.0fs" % (
                      n, mname, o["covZ_truth"], o["covZ_emu"], o["covM_truth"], o["covM_emu"], o["widthM_tau_median"],
                      *o["err_ms_vs_truth_pct_range"], *c["err_ms_vs_truth_pct_range"], M["secs"]), flush=True)
            if "indist_emulated" in M:
                o = M["indist_emulated"]["summary"]
                print("        in-dist: covZ truth %.3f emu %.3f | covM truth %.2f emu %.2f | wM/tau %.2f" % (
                    o["covZ_truth"], o["covZ_emu"], o["covM_truth"], o["covM_emu"], o["widthM_tau_median"]), flush=True)
        if MODELS is not None and "poly3_invJ" not in MODELS:
            res["sizes"][str(n)] = S
            continue
        # robustness: per-site split conformal, all choices of the calibration couplings (cheap models only)
        kc = 3 if n == 57 else 2
        rob = {}
        for mname in ("poly3_invJ", "null_nn"):
            cov_t, cov_e, wz = [], [], []
            for C in itertools.combinations(R, kc):
                T = [j for j in R if j not in C]
                f = F[mname](T, np.array([Ylab[j] for j in T]))
                q, _ = qconf(np.concatenate([np.abs(f(c)[0] - Ylab[c]) for c in C]))
                for t in od:
                    p = f(t)[0]
                    cov_t.append(np.mean(np.abs(p - D[t]["Z_ref"]) <= q)); cov_e.append(np.mean(np.abs(p - D[t]["Z_lab"]) <= q))
                    wz.append(np.median(2 * q / (TAU_REL * np.abs(D[t]["Z_ref"]))))
            rob[mname] = dict(n_splits=len(list(itertools.combinations(R, kc))), k_cal=kc,
                              covZ_truth=float(np.mean(cov_t)), covZ_emu=float(np.mean(cov_e)),
                              widthZ_tau_median=float(np.median(wz)))
        S["split_robustness_ood"] = rob
        # certification at the labels' own energies; physics-derived abstention
        cert = {}
        for J in Js:
            e = D[J]["eps"]
            cm = cert_at(MR.get((n, J, "m_s")), e)
            cb = cert_at(MR.get((n, J, "Z_bulk")), e); cbd = cert_at(MR.get((n, J, "Z_boundary")), e)
            cert[str(J)] = dict(eps_emu=e, eps_emu_per_site=e / n, m_s=cm, Z_bulk=cb, Z_boundary=cbd,
                                answer_m_s=cm["certified"], answer_local=bool(cb["certified"] and cbd["certified"]))
        S["certification"] = cert
        ans_m = [float(J) for J in Js if cert[str(J)]["answer_m_s"]]
        ans_z = [float(J) for J in Js if cert[str(J)]["answer_local"]]
        ab = dict(answered_m_s=ans_m, answered_local=ans_z, frac_m_s=len(ans_m) / len(Js), frac_local=len(ans_z) / len(Js),
                  frac_m_s_ood=sum(1 for j in ans_m if j in OOD) / len(od))
        for mname in ("poly3_invJ", "mlp_pilot3"):
            if mname not in S["models"]:
                continue
            rows = S["models"][mname]["indist_emulated"]["rows"] + S["models"][mname]["ood_emulated"]["rows"]
            errs = [r["err_ms_vs_truth_pct"] for r in rows if r["Jz"] in ans_m]
            ab[mname] = dict(max_err_answered_pct=max(errs) if errs else None,
                             max_err_all_pct=max(r["err_ms_vs_truth_pct"] for r in rows),
                             max_miss_over_tau_answered=max([r["miss_ms_over_tau"] for r in rows if r["Jz"] in ans_m],
                                                            default=None))
        ws = [cert[str(J)]["m_s"]["width_tau_ge"] for J in od if cert[str(J)]["m_s"].get("width_tau_ge")]
        ab["m_s_certified_width_tau_ge_ood"] = [min(ws), max(ws)] if ws else None
        wl = [cert[str(J)]["Z_bulk"]["width_tau_ge"] for J in od if cert[str(J)]["Z_bulk"].get("width_tau_ge")]
        ab["Z_bulk_certified_width_tau_ge_ood"] = [min(wl), max(wl)] if wl else None
        S["abstention"] = ab
        print("n=%d abstention: answers m_s at %s (%d/%d), local at %s; certified m_s width at OOD >= %s tau" % (
            n, ans_m, len(ans_m), len(Js), ans_z, ab["m_s_certified_width_tau_ge_ood"]), flush=True)
        # device points (illustration; n = 57 only)
        if n == 57 and "poly3_invJ" in S["models"]:
            dev = {}
            f = F["poly3_invJ"](R, np.array([Ylab[j] for j in R]))
            qM = S["models"]["poly3_invJ"]["ood_emulated"]["summary"]
            _, rM = loo_calib(F["poly3_invJ"], R, Ylab, eta); qMv, _ = qconf(rM)
            for Jk, p in qpu["points"].items():
                J = round(float(Jk), 1)
                mt = ml2.ms(D[J]["Z_ref"], eta); md = mt + p["device"]["rec"]["dm_s"]
                mp = ml2.ms(f(J)[0], eta)
                dev[Jk] = dict(m_s_truth=mt, m_s_device=md, dm_s_device=p["device"]["rec"]["dm_s"],
                               eps_device=p["device"]["rec"]["eps"], m_s_pred_emu_trained=mp, qM=qMv,
                               device_in_interval=bool(abs(md - mp) <= qMv), truth_in_interval=bool(abs(mt - mp) <= qMv),
                               certified_at_device_energy=cert_at(MR.get((57, J, "m_s")), p["device"]["rec"]["eps"])["certified"])
            S["device_illustration"] = dev
            print("n=57 device:", {k: (round(v["m_s_device"], 4), v["device_in_interval"], v["certified_at_device_energy"])
                                   for k, v in dev.items()}, flush=True)
        res["sizes"][str(n)] = S
    res["secs"] = time.time() - t0
    os.makedirs(OUT, exist_ok=True)
    name = "results_fast.json" if FAST else ("results_%s.json" % TAG if TAG else "results.json")
    with open(os.path.join(OUT, name), "w") as fo:
        json.dump(res, fo, indent=1, default=float)
    print("done %.0f s" % res["secs"])


def merge():
    """Merge the partial job files results_<tag>.json into results.json (models dicts united per size)."""
    parts = sorted(glob.glob(os.path.join(OUT, "results_*.json")))
    parts = [p for p in parts if not p.endswith("results_fast.json")]
    res = None
    for p in parts:
        r = rj(p)
        if res is None:
            res = dict(r, sizes={}, merged_from=[])
        res["merged_from"].append(os.path.basename(p))
        for n, S in r["sizes"].items():
            if n not in res["sizes"]:
                res["sizes"][n] = dict(S, models={})
            for k, v in S.items():
                if k != "models" and k not in res["sizes"][n]:
                    res["sizes"][n][k] = v
            res["sizes"][n]["models"].update(S["models"])
    with open(os.path.join(OUT, "results.json"), "w") as fo:
        json.dump(res, fo, indent=1, default=float)
    print("merged", res["merged_from"])


if __name__ == "__main__":
    merge() if "--merge" in sys.argv else main()
