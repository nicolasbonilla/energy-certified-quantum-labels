"""Laptop analysis (DECLARATION.md §6; written after the hash, implements §6 as written). Light: reads JSON only.

  python code/analyze.py <out_dir with device_*.json / control_*.json>    -> analysis/analysis.json, analysis/TABLES.md

Map placement: device eps = E - E0 against the certification map's eps_tau (inner = rigorous, outer = DMRG-referenced)
for m_s and Czz_bar at n = 57 (map/laptop_analysis/summary_map.json): CERTIFIED if eps <= eps_tau_in, NOT CERTIFIED
if eps > eps_tau_out, GRAY otherwise. Window position: f_plus = dm_s / (m_s^+(eps) - m_s,GS), m_s^+ = upper concave
envelope of the map's m_s "+" chain with the ground state; beyond the chain's last point f_plus is an upper bound.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAP = os.path.join(ROOT, "..", "map")
MAPCH = os.path.join(MAP, "out_20261030T022613Z", "out", "chains")
IBM_RAW = {1.6: 6.89, 4.0: 0.367}            # IBM raw (pre-basis-optimization) ratios, digitized (method/code/fr.py)
IBM_INSECTOR = 81862
R_DEVREC_12 = 31.307                         # emu_n57_J1.2 dev_rec ratio (declared)


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def js(J):
    return "%.1f" % float(J)


def upper_env(points):
    """Upper concave envelope of (eps, o) points (sorted by eps); returns function eps -> (value, beyond)."""
    P = sorted(points)
    H = []
    for p in P:
        while len(H) >= 2 and (H[-1][1] - H[-2][1]) * (p[0] - H[-2][0]) <= (p[1] - H[-2][1]) * (H[-1][0] - H[-2][0]):
            H.pop()
        H.append(p)

    def f(e):
        if e >= H[-1][0]:
            return H[-1][1], True
        for a, b in zip(H[:-1], H[1:]):
            if a[0] <= e <= b[0]:
                t = (e - a[0]) / (b[0] - a[0]) if b[0] > a[0] else 0.0
                return a[1] + t * (b[1] - a[1]), False
        return H[0][1], False
    return f, H


def map_rows():
    d = rj(os.path.join(MAP, "laptop_analysis", "summary_map.json"))
    return {(r["Jz"], r["label"]): r for r in d["rows"] if r["n"] == 57}


def placement(rows, Jz, eps):
    out = {}
    for lab in ("m_s", "Czz_bar"):
        r = rows.get((Jz, lab))
        if r is None:
            out[lab] = None
            continue
        st = "CERTIFIED" if eps <= r["eps_tau_in"] else ("NOT_CERTIFIED" if eps > r["eps_tau_out"] else "GRAY")
        out[lab] = dict(eps_tau_in=r["eps_tau_in"], eps_tau_out=r["eps_tau_out"], eps_over_eps_tau=eps / r["eps_tau_out"],
                        status_at_our_energy=st, map_status_at_IBM_energy=r["status"])
    return out


def fplus(Jz, eps, dms):
    p = os.path.join(MAPCH, "chain_n57_J%s_m_s_+.json" % js(Jz))
    if not os.path.exists(p):
        return None
    c = rj(p)
    pts = [(0.0, c["o_GS"])] + [(q["eps"], q["o"]) for q in c["points"] if q.get("in_sector", True)]
    f, H = upper_env(pts)
    v, beyond = f(eps)
    return dict(m_plus=v, o_GS=c["o_GS"], f_plus=dms / (v - c["o_GS"]) if v > c["o_GS"] else None,
                beyond_chain=beyond, chain_eps_max=max(q["eps"] for q in c["points"]),
                kind="upper bound (eps beyond the chain)" if beyond else "value")


def row(v, n_shots_total):
    e = v["err"]
    st = v["stats"]
    sd = np.asarray(v["signed_dZ_site"])
    return dict(E=v["E"], eps=v["eps"], ratio=v["ratio"], dm_s=e["dm_s"], rel_m_s=e["rel_m_s"],
                frac_over=e["frac_sites_overordered"], signed_dZ_min=float(sd.min()), signed_dZ_mean=float(sd.mean()),
                dZ=e["dZ"], dCzz=e["dCzz"], dZloop=e["dZloop"], frac_Czz_stronger=e["frac_Czz_stronger"],
                n_shots=st["n_shots"], n_unique=st["n_unique"], n_unique_in_sector=st["n_unique_in_sector"], D=st["D"],
                in_sector_per_1e6=st["n_unique_in_sector"] * 1e6 / n_shots_total)


def d1(dms, over):
    if dms >= 0.10 and over >= 0.9:
        return "PRESENT"
    if abs(dms) < 0.03:
        return "NULL"
    if dms <= -0.10:
        return "REVERSED"
    return "WEAK"


def main():
    od = sys.argv[1]
    rows = map_rows()
    res = dict(points={}, checks={}, inclusion=None)
    for job in ("A", "B"):
        p = os.path.join(ROOT, "jobs", job, "checks.json")
        if os.path.exists(p):
            c = rj(p)
            res["checks"][job] = {k: ({kk: vv for kk, vv in v.items() if kk != "site_agreement"} if isinstance(v, dict)
                                      else v) for k, v in c.items()}
    for f in sorted(os.listdir(od)):
        if not (f.startswith("device_") and f.endswith(".json")):
            continue
        d = rj(os.path.join(od, f))
        Jz = round(d["Jz"], 1)
        tot = sum(d["shots_per_circuit"])
        P = dict(job=d["job"], checks_pass=d["checks_both_pass"], shots_per_circuit=d["shots_per_circuit"][0],
                 device={v: row(d["var"][v], tot) for v in ("rec", "ps")})
        cp = os.path.join(od, "control_J%s.json" % js(Jz))
        if os.path.exists(cp):
            c = rj(cp)
            P["control"] = {v: row(c["var"][v], sum([c["shots_per_circuit"]] * 10)) for v in ("rec", "ps")}
            P["control_discarded"] = c["discarded_total"]
            P["control_flag"] = c["flag_discarded"]
            P["D3_dm_s_device_minus_control"] = P["device"]["rec"]["dm_s"] - P["control"]["rec"]["dm_s"]
            P["ratio_device_over_control"] = P["device"]["rec"]["ratio"] / P["control"]["rec"]["ratio"]
        em = rj(os.path.join(ROOT, "refs", "emu_n57_J%s.json" % js(Jz)))
        P["emulation_1e6_shots"] = {k: dict(ratio=em["var"][k]["ratio"], dm_s=em["var"][k]["err"]["dm_s"])
                                    for k in ("ideal", "dev_rec") if k in em["var"]}
        P["ibm_raw_ratio"] = IBM_RAW.get(Jz)
        dv = P["device"]["rec"]
        P["D1_reading"] = d1(dv["dm_s"], dv["frac_over"]) if Jz == 1.2 else None
        P["map"] = placement(rows, Jz, dv["eps"])
        P["window"] = fplus(Jz, dv["eps"], dv["dm_s"])
        if "control" in P:
            P["window_control"] = fplus(Jz, P["control"]["rec"]["eps"], P["control"]["rec"]["dm_s"])
        res["points"][js(Jz)] = P
    p12 = res["points"].get("1.2")
    chkA = res["checks"].get("A", {}).get("both_pass", False)
    if p12:
        r = p12["device"]["rec"]["ratio"]
        cond = dict(i_checks_A_pass=bool(chkA), ii_control_computed="control" in p12,
                    iii_ratio_within_3x_of_devrec=bool(R_DEVREC_12 / 3 <= r <= R_DEVREC_12 * 3), ratio=r,
                    window=[R_DEVREC_12 / 3, R_DEVREC_12 * 3])
        cond["verdict"] = "MAIN TEXT" if all(cond[k] for k in ("i_checks_A_pass", "ii_control_computed",
                                                               "iii_ratio_within_3x_of_devrec")) else "SM ONLY"
        if not chkA:
            cond["verdict"] = "NOT USED (job A checks failed)"
        res["inclusion"] = cond
    os.makedirs(os.path.join(ROOT, "analysis"), exist_ok=True)
    with open(os.path.join(ROOT, "analysis", "analysis.json"), "w") as f:
        json.dump(res, f, indent=1)
    L = ["# Tables (generated by code/analyze.py from %s)" % od, ""]
    for job, c in res["checks"].items():
        L.append("Job %s checks: neel pass %s (min site agreement %.4f, exact-string %.3f); asym pass %s (min %.4f, exact %.3f)"
                 % (job, c["neel"]["pass_"], c["neel"]["min_site_agreement"], c["neel"]["exact_string_fraction"],
                    c["asym"]["pass_"], c["asym"]["min_site_agreement"], c["asym"]["exact_string_fraction"]))
    L += ["", "| Jz | source | shots/circ | unique | in-sector unique (per 1e6) | D | eps (J) | ratio | dm_s | sites over | signed dZ min / mean | dZ % | dCzz % | dZloop % |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for J, P in res["points"].items():
        for src in ("device", "control"):
            if src not in P:
                continue
            for v in ("rec", "ps"):
                x = P[src][v]
                L.append("| %s | %s %s | %d | %d | %d (%.0f) | %d | %.4f | %.4g | %+.4f | %.3f | %+.3f / %+.3f | %.1f | %.1f | %.1f |" % (
                    J, src, v, x["n_shots"] // 10, x["n_unique"], x["n_unique_in_sector"], x["in_sector_per_1e6"],
                    x["D"], x["eps"], x["ratio"], x["dm_s"], x["frac_over"], x["signed_dZ_min"], x["signed_dZ_mean"],
                    x["dZ"], x["dCzz"], x["dZloop"] or float("nan")))
    L.append("")
    for J, P in res["points"].items():
        L.append("Jz %s: D1 %s; D3 (device - control) %s; emulation %s; IBM raw ratio %s; map %s; window %s" % (
            J, P["D1_reading"], P.get("D3_dm_s_device_minus_control"), P["emulation_1e6_shots"], P["ibm_raw_ratio"],
            {k: (v["status_at_our_energy"], round(v["eps_over_eps_tau"], 2)) if v else None for k, v in P["map"].items()},
            P["window"]))
    L.append("")
    L.append("Inclusion: %s" % res["inclusion"])
    with open(os.path.join(ROOT, "analysis", "TABLES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
