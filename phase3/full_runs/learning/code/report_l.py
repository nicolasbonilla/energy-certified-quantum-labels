"""Gates, label statistics, tables and the declared verdicts of the learning run (laptop).

  python report_l.py <out_dir> <analysis_dir> [<id_set> <ood_set>]   (defaults D O; toys: T3 U3)
Reads <out_dir>/inst/*.json (VM outputs) and <analysis_dir>/learn_M{1,2}_D_O.json (learn_l.py); writes
<analysis_dir>/gates.json, label_stats.json, verdicts.json and TABLES.md.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import labels_l as LB  # noqa: E402

DE = LB.DE


def gates(out_dir, recs):
    g = dict(ED={}, GEN={}, WIT={})
    for s, rr in recs.items():
        res = [max(r["ed_residual"]) for r in rr]
        ident = [abs(r["E_from_C_minus_E0"]) for r in rr]
        row = dict(n=len(rr), max_residual=max(res), max_identity=max(ident),
                   pass_residual=sum(x <= 1e-8 for x in res), pass_identity=sum(x <= 1e-8 for x in ident))
        if rr[0].get("gate"):
            dE = [r["E0"] - r["gate"]["E_file_x2"] for r in rr]
            rel = [abs(r["E0"] / r["gate"]["E_file_x2"] - 1) for r in rr]
            dC = [r["gate"]["max_dC_vs_XX"] for r in rr]
            dC3 = [r["gate"]["max_dC_vs_mean3"] for r in rr]
            xz = [r["gate"]["file_max_XX_minus_ZZ"] for r in rr]
            row.update(max_E0_minus_2Efile=max(dE), min_E0_minus_2Efile=min(dE), max_rel_E=max(rel),
                       max_dC_vs_XX=max(dC), median_dC_vs_XX=float(np.median(dC)), max_dC_vs_mean3=max(dC3),
                       file_max_XX_minus_ZZ=max(xz),
                       pass_variational=sum(r["E0"] <= r["gate"]["E_file_x2"] + 1e-9 * abs(r["E0"]) for r in rr),
                       pass_relE=sum(x <= 1e-5 for x in rel), pass_dC=sum(x <= 1e-4 for x in dC))
            fails = [r["k"] for r in rr if not (max(r["ed_residual"]) <= 1e-8 and abs(r["E_from_C_minus_E0"]) <= 1e-8
                                                 and r["E0"] <= r["gate"]["E_file_x2"] + 1e-9 * abs(r["E0"])
                                                 and abs(r["E0"] / r["gate"]["E_file_x2"] - 1) <= 1e-5
                                                 and r["gate"]["max_dC_vs_XX"] <= 1e-4)]
        else:
            fails = [r["k"] for r in rr if not (max(r["ed_residual"]) <= 1e-8 and abs(r["E_from_C_minus_E0"]) <= 1e-8)]
        row["failing_instances"] = fails
        g["ED"][s] = row
        gr = {}
        for de in DE:
            ratio = [r["gen"][de]["de_gen"] / de for r in rr]
            chk = [abs(r["gen"][de]["E_gen_check"] - r["gen"][de]["E_gen"]) for r in rr]
            rres = [r["gen"][de]["rr_residual"] for r in rr]
            fails = [r["k"] for r, a, b, c in zip(rr, ratio, chk, rres) if not (0.9 <= a <= 1.0 + 1e-12 and b <= 1e-8
                                                                             and c <= 1e-6)]
            gr[str(de)] = dict(min_ratio=min(ratio), max_ratio=max(ratio), max_Echeck=max(chk), max_rr_residual=max(rres),
                               failing_instances=fails,
                               frac_sub=[min(r["gen"][de]["frac_sub"] for r in rr), float(np.median([r["gen"][de]["frac_sub"] for r in rr])),
                                         max(r["gen"][de]["frac_sub"] for r in rr)],
                               D_sub=[min(r["gen"][de]["D_sub"] for r in rr), int(np.median([r["gen"][de]["D_sub"] for r in rr])),
                                      max(r["gen"][de]["D_sub"] for r in rr)],
                               captured_weight=[min(r["gen"][de]["captured_weight"] for r in rr),
                                                float(np.median([r["gen"][de]["captured_weight"] for r in rr])),
                                                max(r["gen"][de]["captured_weight"] for r in rr)],
                               shots=[min(r["gen"][de]["shots_expected"] for r in rr),
                                      float(np.median([r["gen"][de]["shots_expected"] for r in rr])),
                                      max(r["gen"][de]["shots_expected"] for r in rr)])
        g["GEN"][s] = gr
        c = LB.checks(rr)
        c["fails"] = c["fails"][:20]
        c["n_points"] = int(sum(v["npts"] for r in rr for v in r["labels"].values()))
        g["WIT"][s] = c
    return g


def label_stats(recs):
    out = {}
    for s, rr in recs.items():
        out[s] = {}
        for de in DE:
            for cl in ("avg", "nn", "diag"):
                b, hw, hwa, aL, aM, ys = [], [], [], [], [], []
                for r in rr:
                    for lab, v in r["labels"].items():
                        if v["cls"] != cl:
                            continue
                        so = LB.order_sign(lab)
                        b.append(so * (v["gen"][de] - v["exact"]))
                        lo, hi = v["cert_gen"][de]
                        hw.append((hi - lo) / 2)
                        lo2, hi2 = v["cert_adv"][de]
                        hwa.append((hi2 - lo2) / 2)
                        aL.append(so * (v["adv"]["less"][de] - v["exact"]))
                        aM.append(so * (v["adv"]["more"][de] - v["exact"]))
                if not b:
                    continue
                b, hw, hwa, aL, aM = map(np.array, (b, hw, hwa, aL, aM))
                out[s]["%s|%g" % (cl, de)] = dict(
                    n=len(b), gen_bias_toward_order_mean=float(b.mean()), gen_bias_sd=float(b.std()),
                    gen_frac_less_order=float((b < 0).mean()), gen_abs_bias_mean=float(np.abs(b).mean()),
                    cert_halfwidth_gen_mean=float(hw.mean()), cert_halfwidth_gen_median=float(np.median(hw)),
                    cert_halfwidth_adv_mean=float(hwa.mean()), gen_abs_bias_over_halfwidth_mean=float(np.mean(np.abs(b) / hw)),
                    advL_shift_mean=float(aL.mean()), advM_shift_mean=float(aM.mean()),
                    frac_certified_tau008=float(np.mean(2 * hw <= 0.08)), frac_certified_tau004=float(np.mean(2 * hw <= 0.04)))
    return out


def fmt(x, d=3):
    return "—" if x is None else ("%.*f" % (d, x))


def verdict(c, strong, null):
    return "STRONG" if c < strong else ("NULL" if c >= null else "INTERMEDIATE")


def main(out_dir, an, sid="D", sood="O"):
    recs = LB.load_all(out_dir, [sid, sood])
    G = gates(out_dir, recs)
    S = label_stats(recs)
    json.dump(G, open(os.path.join(an, "gates.json"), "w"), indent=1)
    json.dump(S, open(os.path.join(an, "label_stats.json"), "w"), indent=1)
    R = {}
    for M in ("M1", "M2"):
        p = os.path.join(an, "learn_%s_%s_%s.json" % (M, sid, sood))
        if os.path.exists(p):
            R[M] = json.load(open(p))
    V = {}
    T = []
    if "M1" in R:
        c = R["M1"]["coverage"]
        V["D1"] = dict(value=c["gen5"]["SC"]["nn"]["covT_id"], verdict=verdict(c["gen5"]["SC"]["nn"]["covT_id"], .70, .85))
        V["D2"] = dict(value=c["gen5"]["SC"]["avg"]["covT_id"], verdict=verdict(c["gen5"]["SC"]["avg"]["covT_id"], .70, .85))
        V["D3"] = dict(value=c["advL5"]["SC"]["nn"]["covT_id"], verdict=verdict(c["advL5"]["SC"]["nn"]["covT_id"], .70, .85))
        rho = {cl: c["gen5"]["CSC"][cl]["wid_id"] / c["gen5"]["SC"][cl]["wid_id"] for cl in ("avg", "nn")}
        V["D5"] = {cl: dict(value=v, verdict="EXPENSIVE" if v >= 4.5 else ("CHEAP" if v <= 1.5 else "MODERATE"))
                   for cl, v in rho.items()}
        ab = R["M1"]["abstention"]
        a_avg = ab["gen5|avg|id|0.08"]["rule"]["BAND"]["answer_rate"]
        a_nn = ab["gen5|nn|id|0.08"]["rule"]["BAND"]["answer_rate"]
        V["D6"] = dict(a_avg=a_avg, a_nn=a_nn, verdict="CONFIRMED" if (a_avg >= 0.9 and a_nn <= 0.1) else
                       ("REFUTED" if (a_avg <= 0.5 or a_nn >= 0.5) else "PARTIAL"))
        key = "advL5|all|id|0.08"
        # pooled avg + nn: the 'all' group contains diag too when tier B is present; D7 is declared on avg + nn
        rule = ab[key]["rule"]["NC"]
        V["D7_note"] = "computed from the avg and nn groups pooled (query-weighted)"
        na = nq = ne = 0.0
        for g in ("avg", "nn"):
            st = ab["advL5|%s|id|0.08" % g]["rule"]["NC"]
            nq += st["n_queries"]
            na += st["answer_rate"] * st["n_queries"]
            ne += st["joint_exceed_and_answer"] * st["n_queries"]
        ar = na / nq
        e = ne / na if na > 0 else None
        V["D7"] = dict(answer_rate=ar, e_NC=e, verdict="NO DECISION (NC answers < 1 %)" if ar < 0.01 else
                       ("UNSAFE" if e >= 0.30 else ("SAFE" if e <= 0.10 else "INTERMEDIATE")))
    if "M2" in R:
        c = R["M2"]["coverage"]
        V["D3prime_M2"] = dict(value=c["advL5"]["SC"]["nn"]["covT_id"],
                               verdict=verdict(c["advL5"]["SC"]["nn"]["covT_id"], .70, .85))
    # D4
    det = all(len(G["WIT"][s]["fails"]) == 0 for s in G["WIT"])
    bands = all(R[M]["band_check"][ls]["violations"] == 0 for M in R for ls in R[M]["band_check"])
    bandrule = all(v["rule"]["BAND"]["band_guarantee_violations"] == 0 for M in R for v in R[M]["abstention"].values())
    stat = []
    for M in R:
        for ls in ("gen1", "gen5", "advL1", "advL5", "advM1", "advM5"):
            for meth in ("CSC", "CB"):
                for cl in ("avg", "nn", "diag"):
                    if cl in R[M]["coverage"][ls][meth]:
                        stat.append((M, ls, meth, cl, R[M]["coverage"][ls][meth][cl]["covT_id"]))
    worst = min(stat, key=lambda t: t[4]) if stat else None
    V["D4"] = dict(deterministic=det, band_checks=bands, band_rule=bandrule, worst_certified_coverage=worst,
                   verdict="PASS" if (det and bands and bandrule and worst and worst[4] >= 0.88) else "FAIL")
    json.dump(V, open(os.path.join(an, "verdicts.json"), "w"), indent=1)
    # ---- tables
    T.append("# Learning run: tables (generated by code/report_l.py)\n")
    T.append("## Gates\n")
    for s in (sid, sood):
        e = G["ED"][s]
        T.append("- ED %s: %d instances; max residual %.1e; max |sum 3JC - E0| %.1e; failing %s" % (
            s, e["n"], e["max_residual"], e["max_identity"], e["failing_instances"]))
        if "max_dC_vs_XX" in e:
            T.append("  - vs dataset: E0 - 2E_file in [%.2e, %.2e]; max rel %.2e; max |C - XX_file| %.2e (median %.2e); "
                     "max |C - (XX+YY+ZZ)/3| %.2e; the file's own max |XX - ZZ| %.2e" % (
                         e["min_E0_minus_2Efile"], e["max_E0_minus_2Efile"], e["max_rel_E"], e["max_dC_vs_XX"],
                         e["median_dC_vs_XX"], e["max_dC_vs_mean3"], e["file_max_XX_minus_ZZ"]))
        for de in DE:
            gg = G["GEN"][s][str(de)]
            T.append("- GEN %s de=%g: de_gen/de in [%.4f, %.4f]; failing %s; D (min/median/max) %s of the sector; frac %s; "
                     "captured weight %s; shots %s" % (s, de, gg["min_ratio"], gg["max_ratio"], gg["failing_instances"],
                                                       gg["D_sub"], ["%.3f" % x for x in gg["frac_sub"]],
                                                       ["%.4f" % x for x in gg["captured_weight"]],
                                                       ["%.2g" % x for x in gg["shots"]]))
        w = G["WIT"][s]
        T.append("- certified intervals %s: %d labels x 2 de; exact in cert(gen) %d, gen in cert(gen) %d, exact in "
                 "cert(adv) %d, adv in cert(adv) %d; failures %d; max violation %.1e; witness points %d" % (
                     s, w["n_labels"], w["exact_in_cert_gen"], w["gen_in_cert_gen"], w["exact_in_cert_adv"],
                     w["adv_in_cert_adv"], len(w["fails"]), w["max_viol"], w["n_points"]))
    T.append("\n## Generator label bias vs the certified half-width (signed toward more order; mean over labels and instances)\n")
    T.append("| set | class | de | n | gen bias | frac less order | mean abs bias | cert half-width (gen) | abs bias / half-width | advL shift | advM shift | frac certified tau=0.08 |")
    T.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in (sid, sood):
        for k, v in S[s].items():
            cl, de = k.split("|")
            T.append("| %s | %s | %s | %d | %+.4f | %.2f | %.4f | %.4f | %.2f | %+.4f | %+.4f | %.2f |" % (
                s, cl, de, v["n"], v["gen_bias_toward_order_mean"], v["gen_frac_less_order"], v["gen_abs_bias_mean"],
                v["cert_halfwidth_gen_mean"], v["gen_abs_bias_over_halfwidth_mean"], v["advL_shift_mean"],
                v["advM_shift_mean"], v["frac_certified_tau008"]))
    for M, r in R.items():
        c = r["coverage"]
        T.append("\n## %s: coverage of the TRUE labels (nominal 0.90), own-label coverage, mean width\n" % M)
        T.append("Model RMSE vs truth (ID / OOD): " + "; ".join(
            "%s %s %.4f / %.4f" % (ls, g, r["model_rmse"][ls][g]["id"], r["model_rmse"][ls][g]["ood"])
            for ls in ("exact", "gen5", "advL5") for g in ("avg", "nn", "diag") if g in r["model_rmse"][ls]))
        T.append("")
        T.append("| label set | class | " + " | ".join("%s truth ID / own ID / width ID / truth OOD" % m for m in
                                                     ("SC", "NC", "ENS", "CSC", "CNC", "CB", "BAND")) + " |")
        T.append("|---|---|" + "---|" * 7)
        for ls in ("exact", "gen1", "gen5", "advL1", "advL5", "advM1", "advM5"):
            for g in ("avg", "nn", "diag"):
                if g not in c[ls]["SC"]:
                    continue
                T.append("| %s | %s | " % (ls, g) + " | ".join(
                    "%.3f / %.3f / %.3f / %.3f" % (c[ls][m][g]["covT_id"], c[ls][m][g]["covO_id"], c[ls][m][g]["wid_id"],
                                                   c[ls][m][g]["covT_ood"]) for m in
                    ("SC", "NC", "ENS", "CSC", "CNC", "CB", "BAND")) + " |")
        T.append("\n### %s: width cost\n" % M)
        T.append("| label set | class | width SC | width CSC | CSC/SC | width CB | CB/SC | width SC(exact labels) | CSC/SC(exact) | BAND width |")
        T.append("|---|---|---|---|---|---|---|---|---|---|")
        for ls in ("gen1", "gen5", "advL1", "advL5"):
            for g in ("avg", "nn", "diag"):
                if g not in c[ls]["SC"]:
                    continue
                wsc, wcsc, wcb = c[ls]["SC"][g]["wid_id"], c[ls]["CSC"][g]["wid_id"], c[ls]["CB"][g]["wid_id"]
                wex = c["exact"]["SC"][g]["wid_id"]
                T.append("| %s | %s | %.4f | %.4f | %.2f | %.4f | %.2f | %.4f | %.2f | %.4f |" % (
                    ls, g, wsc, wcsc, wcsc / wsc, wcb, wcb / wsc, wex, wcsc / wex, c[ls]["BAND"][g]["wid_id"]))
        T.append("\n### %s: abstention rules at tau (answer rate / truth exceedance P(|err| > tau/2) given answered / own-label exceedance)\n" % M)
        T.append("| key | " + " | ".join(("CB_mid", "BAND", "CSC", "CNC", "NC", "SC", "ENS")) + " |")
        T.append("|---|" + "---|" * 7)
        for key, v in r["abstention"].items():
            T.append("| %s | " % key + " | ".join("%.3f / %s / %s" % (v["rule"][m]["answer_rate"], fmt(v["rule"][m]["exceed_given_answer"]),
                                                                    fmt(v["rule"][m]["exceed_own_given_answer"]))
                                                  for m in ("CB_mid", "BAND", "CSC", "CNC", "NC", "SC", "ENS")) + " |")
        T.append("\n### %s: AURC (mean selective RMSE vs truth over coverage 0.05..1)\n" % M)
        rk = ["oracle", "CB", "BAND", "CSC", "CNC", "NC", "ENS", "SC", "random"]
        T.append("| key | " + " | ".join(rk) + " |")
        T.append("|---|" + "---|" * len(rk))
        for key, v in r["abstention"].items():
            if key.endswith("|0.08"):
                T.append("| %s | " % key + " | ".join("%.4f" % v["aurc"][x] for x in rk) + " |")
    T.append("\n## Verdicts\n")
    T.append("```\n" + json.dumps(V, indent=1) + "\n```")
    open(os.path.join(an, "TABLES.md"), "w", encoding="utf-8").write("\n".join(T) + "\n")
    print(json.dumps(V, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
