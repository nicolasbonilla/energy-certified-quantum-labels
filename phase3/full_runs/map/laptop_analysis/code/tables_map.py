"""Markdown tables of the certification map from summary_map.json (laptop; arithmetic only).

  python -I tables_map.py <summary_map.json> <out.md>
"""
import json
import sys

LN = {"m_s": "m_s", "Czz_bar": "C̄_zz", "C2_bar": "C̄₂", "Z_bulk": "Z_bulk", "Z_boundary": "Z_boundary",
      "Czz_edge": "C_zz(edge)", "Z_loop": "Z_loop"}
ORDER = ["m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop"]


def f(x, d=4):
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    if abs(x) >= 1000 or (abs(x) < 1e-3 and x != 0):
        return "%.2e" % x
    return ("%." + str(d) + "f") % x


def main(sp, outp):
    S = json.load(open(sp))
    L = []
    rows = [r for r in S["rows"] if r["n"] in (57, 115)]
    for n in (57, 115):
        L.append("\n### n = %d\n" % n)
        L.append("| label | Jz | O_GS | ε_dig (J) | w_in(E_lo) | w_pure(E_lo) | w_out(E_up) | w_out/τ at E_dig | status | "
                 "status r2 | f_in | f_out | law/meas | ε_dig/Δ_in | pts |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for lab in ORDER:
            for r in sorted((r for r in rows if r["n"] == n and r["label"] == lab), key=lambda r: r["Jz"]):
                st = {"CERTIFIED": "**CERT**", "NOT_CERTIFIED": "not", "GRAY": "gray"}[r["status"]]
                st2 = {"CERTIFIED": "CERT", "NOT_CERTIFIED": "not", "GRAY": "gray"}.get(r.get("status_r2"), "—")
                L.append("| %s | %.1f%s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %d+%d |" % (
                    LN[lab], r["Jz"], " (OOD)" if r.get("ood") else "", f(r["O_GS"]), f(r["eps"]["dig"]),
                    f(r["at_lo"]["w_in"]), f(r["at_lo"]["w_pure"]), f(r["at_up"]["w_out"]),
                    f(r["at_dig"]["ratio_out"], 3), st, st2, f(r.get("f_in"), 3), (f(r.get("f_out"), 3) if r.get("f_out") is not None else
                                                          ("> " + f(r.get("f_out_lb"), 1) if r.get("f_out_lb") else "�")),
                    f(r.get("law_ratio_out"), 3), f(r.get("eps_over_gap_in"), 3),
                    r["n_points"]["+"], r["n_points"]["-"]))
    L.append("\n### J* (IBM training grid 1.6-6.0, step 0.1)\n")
    L.append("| n | label | J* central (r1) | J* strict (r1) | certified points central / strict (r1, of 45) | "
             "J* central (r2) | certified central (r2) |")
    L.append("|---|---|---|---|---|---|---|")
    for n in (57, 115):
        for lab in ORDER:
            a, b = S["jstar"].get("%d_%s_r1" % (n, lab)), S["jstar"].get("%d_%s_r2" % (n, lab))
            if not a:
                continue
            L.append("| %d | %s | %s | %s | %d / %d | %s | %s |" % (
                n, LN[lab], a["J_star_central"] or "none", a["J_star_strict"] or "none", a["n_certified_central"],
                a["n_certified_strict"], (b or {}).get("J_star_central") or "none",
                (b or {}).get("n_certified_central", "—")))
    L.append("\n### δe* rule (law δe*_law = (S/n)τ²/(8χ) vs measured δe* = ε_τ^out/n)\n")
    L.append("| n | Jz | label | χ | δe*_law | δe*_in | δe*_out | law/out | ε_dig/Δ_in |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (r["n"], ORDER.index(r["label"]), r["Jz"])):
        if r.get("de_star_law"):
            L.append("| %d | %.1f | %s | %s | %s | %s | %s | %s | %s |" % (
                r["n"], r["Jz"], LN[r["label"]], f(r["chi"]), f(r["de_star_law"]), f(r.get("de_star_in")),
                f(r.get("de_star_out")), f(r.get("law_ratio_out"), 3), f(r.get("eps_over_gap_in"), 3)))
    L.append("\n### Gates\n")
    for k, v in S["gates"].items():
        if isinstance(v, dict):
            L.append("- %s: pass = %s; %s" % (k, v.get("pass_"), json.dumps(
                {kk: vv for kk, vv in v.items() if kk not in ("rows", "mixtures", "pass_")}, default=str)[:600]))
    L.append("\n### Claims\n")
    for k, v in S.get("claims", {}).items():
        L.append("- %s: %s" % (k, json.dumps({kk: vv for kk, vv in v.items() if kk != "rows"}, default=str)[:900]))
    L.append("\n### Minimal-χ witnesses (best pure states below E_lo)\n")
    L.append("| point | χ | E₀(χ) − E₀ (J) | D_pure(χ) | fraction of full D_pure |")
    L.append("|---|---|---|---|---|")
    for k, m in S.get("minchi", {}).items():
        for chi, d in sorted(m["chis"].items(), key=lambda x: int(x[0])):
            L.append("| %s | %s | %s | %s | %s |" % (k, chi, f(d["gs_eps"]), f(d["D_pure"]), f(d["frac_of_full"], 3)))
    L.append("\n### J* interpolation check (3.3 from 3.2 and 3.4)\n")
    for k, v in S.get("jstar_interp_check", {}).items():
        L.append("- %s: interpolated %s, computed %s, rel %s, ok %s" % (k, f(v["interp"]), f(v["computed"]),
                                                                       f(v["rel"], 4), v["ok"]))
    open(outp, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", outp, len(L), "lines")


if __name__ == "__main__":
    main(*sys.argv[1:])
