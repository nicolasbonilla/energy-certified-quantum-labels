"""Compact Markdown tables for RESULTS.md, generated from <root>/out (summary.json and the task outputs). Laptop.

  python results_tables.py <root> > results_tables.md
"""
import glob
import json
import math
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fr import IBM_POST  # noqa: E402
from summarize import IBM_DZ, interp_log  # noqa: E402


def rj(p):
    with open(p) as f:
        return json.load(f)


def f(x, fmt="%.3f"):
    return "–" if x is None else fmt % x


def main(root):
    O = os.path.join(root, "out")
    S = rj(os.path.join(O, "summary.json"))
    emu = {(r["n"], round(r["Jz"], 1)): r for r in (rj(p) for p in glob.glob(os.path.join(O, "emu", "emu_n*_J*.json")))}
    gs = {(r["n"], round(r["Jz"], 1)): r for r in (rj(p) for p in glob.glob(os.path.join(O, "gsscan", "gsscan_n*_J*.json")))}
    bo = {(round(r["Jz"], 1), r["subspace"]): r for r in (rj(p) for p in glob.glob(os.path.join(O, "bo", "bo_J*.json")))}
    kry = {(r["n"], round(r["Jz"], 1)): r for r in (rj(p) for p in glob.glob(os.path.join(O, "krylov", "krylov_n*_J*.json")))}
    ref = {(r["n"], round(r["Jz"], 1)): r for r in (rj(p) for p in glob.glob(os.path.join(O, "ref", "ref_n*_J*.json")))}
    P = print
    # T1 bias tables (primary)
    for n in (57, 115):
        P("\n**Table 1%s. n = %d, primary variant (published shot budget, 1 %% flips, recovery; labels of the subspace ground state).**\n" % ("a" if n == 57 else "b", n))
        P("| Jz | D | ratio ours / IBM | m_s DMRG → label | Δm_s | ΔZ % ours / IBM | min site excess | sites over-ordered | ΔC_zz % | C_zz stronger | ΔZ_loop % |")
        P("|---|---|---|---|---|---|---|---|---|---|---|")
        for j in sorted(j for (m, j) in emu if m == n):
            v = emu[(n, j)]["var"]["primary"]; e = v["err"]
            P("| %.1f | %s | %s / %s | %.3f → %.3f | **%+.3f** | %.1f / %s | %+.3f | %d/%d | %.1f | %.0f %% | %s |" % (
                j, format(v["stats"]["D"], ","), f(v["ratio"], "%.3g"), IBM_POST[n].get(j, "–"),
                v["labels"]["m_s"] - e["dm_s"], v["labels"]["m_s"], e["dm_s"], e["dZ"], IBM_DZ[n].get(j, "–"),
                e["signed_dZ_min"], round(e["frac_sites_overordered"] * n), n, e["dCzz"], 100 * e["frac_Czz_stronger"],
                f(e["dZloop"], "%.1f")))
    # Krylov truncation
    P("\n**Krylov evolution accuracy (max truncation error per step over k = 1..10).**\n")
    rows = []
    for (n, j), r in sorted(kry.items()):
        tr = [x.get("trunc") for x in r["info"] if x.get("trunc") is not None]
        if tr:
            rows.append("n=%d Jz=%.1f: %.1e" % (n, j, max(tr)))
    P("; ".join(rows) if rows else "(pilot3 samples reused at n = 57: see pilot3)")
    # T2 mechanism
    P("\n**Table 2. Mechanism at equal Jz: Δm_s (D, energy ratio).**\n")
    P("| n, Jz | perfect GS samples, support only (projected), at D_primary | perfect GS samples + RR, at D_primary | Krylov ideal | + 1 % flips + recovery (primary) | device-like noise, post-selection | device-like noise + recovery | n = 57: noise matched to IBM raw energy |")
    P("|---|---|---|---|---|---|---|---|")
    for (n, j) in sorted(emu):
        if (n, j) not in gs:
            continue
        e = emu[(n, j)]["var"]; g = gs[(n, j)]["nested"]
        Dp = e["primary"]["stats"]["D"]
        pr, sp = interp_log([x["D"] for x in g], [x["proj"]["err"]["dm_s"] for x in g], Dp)
        rr, sr = interp_log([x["D"] for x in g], [x["err"]["dm_s"] for x in g], Dp)
        def c(name):
            if name not in e:
                return "–"
            v = e[name]
            return "%+.3f (%s, %.3g)" % (v["err"]["dm_s"], format(v["stats"]["D"], ","), v["ratio"])
        P("| %d, %.1f | %+.3f%s | %+.3f%s | %s | %s | %s | %s | %s |" % (
            n, j, pr, "" if sp == "interpolated" else " (extrap.)", rr, "" if sr == "interpolated" else " (extrap.)",
            c("ideal"), c("primary"), c("dev_ps"), c("dev_rec"), c("pre")))
    # T3 gs scans
    P("\n**Table 3. Perfect sampling of the DMRG ground state: nested subspaces (RR = Rayleigh-Ritz; proj = support only; mean = multiplicity-weighted sample mean).**\n")
    P("| n, Jz | shots N | D | captured weight W | ratio RR | Δm_s RR | Δm_s proj | Δm_s mean |")
    P("|---|---|---|---|---|---|---|---|")
    for (n, j), g in sorted(gs.items()):
        for x in g["nested"]:
            P("| %d, %.1f | %s | %s | %.4f | %.3g | %+.3f | %+.3f | %s |" % (
                n, j, format(x["N"], ","), format(x["D"], ","), x["W_captured"], x["ratio"], x["err"]["dm_s"],
                x["proj"]["err"]["dm_s"], f(x.get("sample_mean", {}).get("dm_s"), "%+.4f")))
        for x in g["topD"]:
            P("| %d, %.1f | top-D | %s | %.4f | %.3g | %+.3f | %+.3f | – |" % (
                n, j, format(x["D"], ","), x["W_captured"], x["ratio"], x["err"]["dm_s"], x["proj"]["err"]["dm_s"]))
    # T4 BO
    P("\n**Table 4. Basis optimization, n = 57 (f = fraction of E − E0 removed).**\n")
    P("| Jz, subspace | variant | stated circuit? | f | ratio before → after | θ rms | Δm_s before | Δm_s after: read off ψ′ / physical U†ψ′ | E(ψ′) under H − E0 |")
    P("|---|---|---|---|---|---|---|---|---|")
    for (j, sub), b in sorted(bo.items()):
        for name, v in b["variants"].items():
            P("| %.1f, %s | %s | %s | %.3f | %.3g → %.3g | %.1e | %+.3f | %s / %s | %s |" % (
                j, sub, name, "yes" if v["stated_circuit"] else "no", v["f_reduction"], b["ratio_pre"], v["ratio_bo"],
                v["theta_rms"], b["pre"]["err"]["dm_s"], f(v.get("unrot", {}).get("err", {}).get("dm_s"), "%+.3f"),
                f(v.get("rot", {}).get("err", {}).get("dm_s"), "%+.3f"),
                f((v["E_of_psi_unrotated_H"] - b["E0"]) if "E_of_psi_unrotated_H" in v else None, "%.3f")))
    # T5 bias at IBM energy
    P("\n**Table 5. Bias at IBM's reported energy (interpolation in log ratio along the perfect-sampler curve) and the ΔZ check.**\n")
    P("| n, Jz | IBM ratio | Δm_s at IBM ratio | band | status | ΔZ predicted there | IBM ΔZ (Supp. Fig. 11) |")
    P("|---|---|---|---|---|---|---|")
    for k, d in sorted(S["bias_at_ibm_energy"].items(), key=lambda t: (t[1]["n"], t[1]["Jz"])):
        P("| %d, %.1f | %s | %s | [%s, %s] | %s | %s | %s |" % (d["n"], d["Jz"], d["ibm_ratio"], f(d["dm_s"], "%+.3f"),
                                                       f(d["band"][0], "%+.3f"), f(d["band"][1], "%+.3f"), d["status"],
                                                       f(d["dZ_pred"], "%.1f"), d["ibm_dZ"]))
    P("\n**Table 6. ΔZ-matched reading (Δm_s = k·ΔZ_IBM; k from all emulated states at that point; every state over-orders).**\n")
    P("| n, Jz | IBM ΔZ % | k (range) | Δm_s estimate | m_s DMRG | implied ratio on the perfect-sampler curve |")
    P("|---|---|---|---|---|---|")
    for k, d in sorted(S["dZ_matched"].items(), key=lambda t: (t[1]["n"], t[1]["Jz"])):
        mGS = ref.get((d["n"], d["Jz"]), {}).get("labels", {}).get("m_s")
        P("| %d, %.1f | %s | %.5f (%.5f-%.5f) | **%+.3f** | %s | %s |" % (
            d["n"], d["Jz"], d["ibm_dZ"], d["slope"], d["slope_range"][0], d["slope_range"][1], d["dm_s"], f(mGS),
            ("%.3g (%s)" % (d["implied_ratio_gs_random"], d["implied_ratio_status"])) if d.get("implied_ratio_gs_random") else "–"))
    # T7 window
    P("\n**Table 7. Position in the energy window (f₊ = Δm_s / (m_s⁺(ε) − m_s,GS), m_s⁺ from the new '+' chains).**\n")
    P("| n, Jz | state | ε = E − E0 (J) | Δm_s | m_s⁺(ε) | f₊ |")
    P("|---|---|---|---|---|---|")
    for k, w in sorted(S["window"].items()):
        for s in w.get("states", []):
            if s["family"] in ("pipeline_floor", "pipeline_ideal", "pipeline_dev_rec") or (
                    s["family"] == "gs_random"):
                P("| %s | %s | %.3f | %+.3f | %s | %s%s |" % (k.replace("_", ", "), s["family"].replace("pipeline_floor", "primary").replace("pipeline_", ""),
                                                        s["eps"], s["dm_s"], f(s["m_plus"]), f(s["f_plus"], "%.2f"),
                                                        "" if s["status"] == "ok" else " (≤, beyond chain)"))
        if w.get("at_ibm"):
            a = w["at_ibm"]
            P("| %s | **at IBM's energy** | %.3f | %+.3f | %s | **%s** |" % (k.replace("_", ", "), a["eps_ibm"], a["dm_s"],
                                                                         f(a["m_plus"]), f(a["f_plus"], "%.2f")))
        if w.get("pilot_window") and "bias_over_D" in w["pilot_window"]:
            pw = w["pilot_window"]
            P("| %s | pilot window (%s) | %.3f | – | D = %.3f, m_s⁺ = %.3f | bias/D = %.2f, bias/(m_s⁺ − m_s,GS) = %.2f |" % (
                k.replace("_", ", "), pw["note"], pw["eps"], pw["D"], pw["plus"], pw["bias_over_D"], pw["bias_over_plus_half"]))
    # T8 learning
    for p in sorted(glob.glob(os.path.join(O, "ml", "ml_n*.json"))):
        m = rj(p)
        P("\n**Table 8 (n = %d). OOD test: relative m_s error of models trained on same-method labels (Jz ∈ %s), vs same-method labels / vs DMRG; last column: the same model trained on DMRG labels, vs DMRG.**\n" % (m["n"], m["train"]))
        P("| model | Jz = 1.1 | 1.2 | 1.3 | 1.4 |")
        P("|---|---|---|---|---|")
        for name, v in m["models"].items():
            cells = []
            for r in v["rows"]:
                cells.append("%.1f %% / %.0f %% (DMRG-trained %.1f %%)" % (r["err_vs_samemethod_pct"], r["err_vs_dmrg_pct"],
                                                                     r["err_dmrgtrained_vs_dmrg_pct"]))
            P("| %s | %s |" % (name, " | ".join(cells)))
        P("\nReadings: %s" % json.dumps(m["readings"]))
        ab = m["abstention"]
        P("\nAbstention (answer only Jz ≥ %.1f; training points by leave-one-out, IBM-like in-sample): " % m["Jstar"] +
          "; ".join("%s coverage %.0f %%, max error answered %.2f %% (mean %.2f %%), max error without abstaining %.0f %%" % (
              k, 100 * v["coverage"], v["max_err_answered"], v["mean_err_answered"], v["max_err_all"])
              for k, v in ab.items() if "coverage" in v))
        es = ab["ensemble_spread"]
        P("\nEnsemble-spread rule (τ = %.1e): abstains at %s; spread at the OOD points %s." % (
            es["tau"], [r["Jz"] for r in es["rows"] if r["abstains"]],
            ", ".join("%.1e" % r["spread"] for r in es["rows"] if r["Jz"] < 1.5)))


if __name__ == "__main__":
    main(sys.argv[1])
