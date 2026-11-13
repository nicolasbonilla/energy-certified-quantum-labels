"""Descriptive arithmetic on stored outputs for the third reading (2026-11-04); no new computation, no decision rule.

  python -I descriptive.py <J_next_paper root> <out dir>      -> <out dir>/descriptive.json

  energy_ratio   n = 57: energy error per site of the emulated label (primary variant, results.json) against the
                 dataset's digitized one (map row at_dig.eps / n), training couplings with a map row
  label_error    n = 57: |m_s(label) - m_s(truth)| / tau of the emulated labels, and the miss of each model
                 (results.json in-distribution rows), with the number of models missing by more than tau/2 and tau
  ood_floor      both sizes: the error per site at which m_s would be certified at the test couplings
                 (eps_tau_out / n) against the assumed floor 0.012 and the digitized error at Jz = 1.6
"""
import json
import os
import sys

ROOT = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
FR = os.path.join(ROOT, "phase3", "full_runs")
TAU_REL = 0.06
FLOOR = 0.012


def rj(p):
    with open(p) as f:
        return json.load(f)


def main():
    R = rj(os.path.join(FR, "learning_ibm", "out", "results.json"))
    M = rj(os.path.join(FR, "map", "laptop_analysis", "summary_map.json"))
    MR = {(r["n"], round(r["Jz"], 1), r["label"]): r for r in M["rows"]}
    res = {}
    S = R["sizes"]["57"]
    er = {}
    for J in S["train"]:
        r = MR.get((57, J, "m_s"))
        if r is None:
            continue
        e = S["certification"][str(J)]["eps_emu"]
        er[str(J)] = dict(emu_per_site=e / 57, dig_per_site=r["eps"]["dig"] / 57, ratio=e / r["eps"]["dig"])
    res["energy_ratio_57"] = er
    le = {}
    models = [m for m in ("poly3_invJ", "mlp_pilot3", "null_nn") if "indist_emulated" in S["models"].get(m, {})]
    for row in S["models"]["poly3_invJ"]["indist_emulated"]["rows"]:
        J = row["Jz"]
        tau = TAU_REL * abs(row["m_s_truth"])
        miss = {m: next(x["miss_ms_over_tau"] for x in S["models"][m]["indist_emulated"]["rows"] if x["Jz"] == J)
                for m in models}
        le[str(J)] = dict(label_err_over_tau=abs(row["bias_ms_label"]) / tau, miss_over_tau=miss,
                          n_models_miss_gt_half_tau=sum(v > 0.5 for v in miss.values()),
                          n_models_miss_gt_tau=sum(v > 1.0 for v in miss.values()))
    res["label_error_57"] = dict(models=models, rows=le,
                                 couplings_all_models_gt_half_tau=[float(J) for J, v in le.items()
                                                                   if v["n_models_miss_gt_half_tau"] == len(models)],
                                 couplings_no_model_gt_half_tau=[float(J) for J, v in le.items()
                                                                 if v["n_models_miss_gt_half_tau"] == 0])
    fl = {}
    for n in (57, 115):
        dig16 = MR[(n, 1.6, "m_s")]["eps"]["dig"] / n
        rows = {}
        for J in (1.1, 1.2, 1.3, 1.4):
            d = MR[(n, J, "m_s")]["eps_tau_out"] / n
            rows[str(J)] = dict(de_cert_per_site=d, floor_over=FLOOR / d, dig16_over=dig16 / d)
        fl[str(n)] = dict(dig_per_site_at_1_6=dig16, rows=rows,
                          de_cert_range=[min(v["de_cert_per_site"] for v in rows.values()),
                                         max(v["de_cert_per_site"] for v in rows.values())],
                          floor_over_range=[min(v["floor_over"] for v in rows.values()),
                                            max(v["floor_over"] for v in rows.values())],
                          dig16_over_range=[min(v["dig16_over"] for v in rows.values()),
                                            max(v["dig16_over"] for v in rows.values())])
    res["ood_floor"] = fl
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "descriptive.json"), "w") as fo:
        json.dump(res, fo, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
