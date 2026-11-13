"""Supplemental tables added in the integration pass (2026-10-31): rigorous lower bounds, our device data, the
second benchmark, and a one-page view of the map.

  python make_sm_new.py     -> sm_tables/{map_glance,rig_v2,rig_v1,qpu,huang_featured,huang_pairs}.tex

No number is typed by hand: every value is read from the deposited outputs below (read-only) and only rounded and
laid out here, with the helpers and layout rules of make_sm_tables.py.

Sources (paths relative to J_next_paper/):
  phase3/full_runs/map/laptop_analysis/summary_map.json      map statuses per (n, Jz, label)
  phase3/full_runs/rigor/outputs/results_v2.json             rigorous certificates, declared lambda grid (v2)
  phase3/full_runs/rigor/outputs/results.json                first rigorous test (v1, declared fields)
  phase3/full_runs/qpu/analysis/analysis.json                our device data, noiseless control, emulation
  phase3/full_runs/huang/laptop_analysis/summary_huang.json  benchmark of arXiv:2106.12627
"""
import json
import os

import common as C
import make_sm_tables as M
from make_sm_tables import sig, hd, sci_small, grp


def write(name, src, *a, **k):
    """make_sm_tables.write, with the generated-by line naming this script"""
    M.write(name, src, *a, **k)
    p = os.path.join(M.OUT, name + ".tex")
    first, rest = open(p, encoding="utf-8").read().split("\n", 1)
    open(p, "w", encoding="utf-8").write(first.replace("make_sm_tables.py", "make_sm_new.py") + "\n" + rest)


def m(x):
    """number in math mode (true minus sign)"""
    return "$%s$" % x

R = os.path.join(C.ROOT, "phase3", "full_runs")
F_RIG2 = os.path.join(R, "rigor", "outputs", "results_v2.json")
F_RIG1 = os.path.join(R, "rigor", "outputs", "results.json")
F_QPU = os.path.join(R, "qpu", "analysis", "analysis.json")
F_HU = os.path.join(R, "huang", "laptop_analysis", "summary_huang.json")
LABTEX = {k: t for k, t, *_ in C.LAB}
LABTEX["Czz_bar"] = r"$\bar C_{zz}$"


def rel(p):
    return os.path.relpath(p, C.ROOT).replace(os.sep, "/")


# ------------------------------------------------------------------------------------------------ map at a glance
def t_map_glance():
    S = C.map_summary()
    rig = C.rj(F_RIG2)
    proved = {(r["n"], round(r["Jz"], 1), r["label"]): r["certified"] for r in rig["rows"]}
    Js = sorted({round(r["Jz"], 1) for r in S["rows"] if r["n"] in (57, 115)})
    ood = {round(r["Jz"], 1) for r in S["rows"] if r.get("ood")}
    sym = {"CERTIFIED": "C", "NOT_CERTIFIED": "N", "GRAY": "G"}
    groups = []
    counts = {"R": 0, "C": 0, "C*": 0}
    for n, labs in ((57, ["m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop"]),
                    (115, ["m_s", "Czz_bar", "C2_bar", "Z_bulk"])):
        rows = []
        for lab in labs:
            cells = [LABTEX[lab]]
            for J in Js:
                rr = [r for r in S["rows"] if r["n"] == n and r["label"] == lab and abs(r["Jz"] - J) < 1e-9]
                if not rr:
                    cells.append(r"$\cdot$")
                    continue
                s = sym[rr[0]["status"]]
                key = (n, J, lab)
                if s == "C" and key in proved:
                    s = r"\textbf{R}" if proved[key] else r"C$^{*}$"
                    counts["R" if proved[key] else "C*"] += 1
                elif s == "C":
                    counts["C"] += 1
                cells.append(s)
            rows.append(cells)
        groups.append(("$n=%d$" % n, rows))
    head = ["Label & " + " & ".join(("%.1f" % J) + (r"$^{\dagger}$" if J in ood else "") for J in Js)]
    colspec = "@{}l" + "c" * len(Js) + "@{}"
    write("map_glance", "%s (status), %s (rigorous rows)" % (rel(C.F_MAP_SUMMARY), rel(F_RIG2)), colspec,
          head, groups)
    print("   glance counts:", counts)
    return counts


# ------------------------------------------------------------------------------------------------ rigorous bounds
def t_rig_v2():
    d = C.rj(F_RIG2)
    groups = []
    for n in (57, 115):
        rows = []
        for r in sorted((x for x in d["rows"] if x["n"] == n), key=lambda x: (x["Jz"], x["label"] != "m_s")):
            lo, hi = r["interval"]
            sp, sm = r["sides"]["+"]["best"], r["sides"]["-"]["best"]
            cells = ["%.1f" % r["Jz"], LABTEX[r["label"]], r"$[%s,\,%s]$" % (sig(lo, 5), sig(hi, 5)),
                     sig(r["w_over_tau"], 3), sig(r["w_F"] / r["tau"], 3),
                     "%s / %s" % (sig(sp["slack"], 2), sig(sm["slack"], 2)),
                     r"certified \ding{51}" if r["certified"] else r"not certified \ding{55}"]
            rows.append((cells, "cert") if r["certified"] else cells)
        groups.append(("$n=%d$" % n, rows))
    head = [r"$J_z$ & Label & rigorous interval at $E_{\rm up}$ & $w_{\rm rig}/\tau$ & $w_{\rm DMRG}/\tau$ & "
            r"slack $+$ / $-$ & status"]
    write("rig_v2", rel(F_RIG2) + " (rows)", "@{}llcccc l@{}".replace(" ", ""), head, groups)
    v = d["verdicts"]
    return {k: (v[k]["n_certified"], v[k]["n_rows"], v[k]["rho_max"], v[k]["verdict"]) for k in v}


def t_rig_v1():
    d = C.rj(F_RIG1)
    rho = d["verdicts"]["best"]["rho_rows"] if "rho_rows" in d["verdicts"]["best"] else d["verdicts"]["eball2"]["rho_rows"]
    rows = []
    for h in d["H"]:
        b = h["levels"]["best"]
        rows.append(["%.1f" % h["Jz"], r"$E_0$", m(sig(b["E0_ref"], 8)), m(sig(b["E_LB"], 8)),
                     r"%s (%s\,\%%)" % (sig(b["slack"], 2), sig(b["slack_rel_pct"], 2)), sig(b["rho"], 2), "---"])
    out = []
    for r in sorted((x for x in d["rows"] if x["n"] == 57), key=lambda x: (x["label"] != "m_s", x["Jz"])):
        key = "%s_%.1f" % (r["label"], r["Jz"])
        b = r["levels"]["best"]
        sl = "%s / %s" % (sig(b["sides"]["+"]["slack"], 2), sig(b["sides"]["-"]["slack"], 2))
        out.append(["%.1f" % r["Jz"], LABTEX[r["label"]], "---", "---", sl, sig(rho[key], 3),
                    sig(b["w_over_tau"], 3) + (r" \ding{51}" if b["certified_rigorously"] else r" \ding{55}")])
    head = [r"$J_z$ & item & DMRG value & certified bound & slack $+$ / $-$ & $\rho$ & $w_{\rm rig}/\tau$"]
    write("rig_v1", rel(F_RIG1) + " (H, rows[*].levels.best, verdicts.best)", "@{}llccccc@{}", head,
          [(r"ground energy, $n=57$", rows), (r"labels at the declared fields, $n=57$", out)])
    return d["verdicts"]["best"]


# ------------------------------------------------------------------------------------------------ device data
def t_qpu():
    d = C.rj(F_QPU)
    groups = []
    for J in ("1.2", "1.6", "4.0"):
        p = d["points"][J]
        rows = []
        srcs = [("device, recovery", p["device"]["rec"]), ("device, post-selection", p["device"]["ps"]),
                ("noiseless control", p["control"]["rec"])]
        if J != "1.2":
            srcs = [srcs[0], srcs[2]]
        for name, x in srcs:
            rows.append([name, grp(p["shots_per_circuit"]), grp(x["D"]), sig(x["ratio"], 3), m("%+.3f" % x["dm_s"]),
                         m("%+.3f" % x["signed_dZ_min"]), sig(x["dZ"], 3), sig(x["dCzz"], 3)])
        e = p["emulation_1e6_shots"]
        rows.append([r"emulation, device-like noise ($10^6$ shots)", "---", "---", sig(e["dev_rec"]["ratio"], 3),
                     m("%+.3f" % e["dev_rec"]["dm_s"]), "---", "---", "---"])
        rows.append([r"emulation, noiseless ($10^6$ shots)", "---", "---", sig(e["ideal"]["ratio"], 3),
                     m("%+.3f" % e["ideal"]["dm_s"]), "---", "---", "---"])
        groups.append((r"$J_z=%s$" % J, rows))
    head = [r"source & shots/circuit & $D$ & $r$ & $\Delta m_s$ & " + hd("smallest", "site excess") +
            r" & $\Delta Z$ (\%) & $\Delta C_{zz}$ (\%)"]
    write("qpu", rel(F_QPU) + " (points.*.device/control/emulation_1e6_shots)", "@{}lccccccc@{}", head, groups)
    return d


# ------------------------------------------------------------------------------------------------ second benchmark
HU_LAB = [("Cnn", r"$\bar C_{\rm nn}$ (average)"), ("Cd2", r"$\bar C_{\rm diag}$ (average)"),
          ("Cstag", r"$\bar C_{\rm stag}$ (average)"), ("Ccent", r"$C_{\rm cent}$ (central bond)"),
          ("Cfix", r"$C_{(7,12)}$ (same bond, growing lattice)"), ("Cfar", r"$C_{\rm far}$ (end to end)")]


def t_huang():
    d = C.rj(F_HU)
    groups = []
    for lab, name in HU_LAB:
        rows = []
        rr = [r for r in d["rows"] if r["label"] == lab and not (r["method"] == "DMRG" and r["n"] == 20)
              and not r.get("alias_of")]
        if lab == "Cfix":
            rr = [r for r in rr if r["n"] > 20]       # at n = 20 the bond (7,12) is the central bond (same rows)
        for r in sorted(rr, key=lambda x: (x["n"], x["k"])):
            t = r["tau"]
            st = " ".join(t["status"])
            rows.append(["$(%d,%d)$" % (r["L"], r["k"]), "%d" % r["n"], "exact" if r["method"] == "ED" else "DMRG",
                         sci_small(t["de_in"], 2, 1e-2), sci_small(t["de_out"], 2, 1e-2),
                         sci_small(t["de_law"], 2, 1e-2), sig(t["law_over_out"], 3), r"\texttt{%s}" % st])
        groups.append((name, rows))
    head = [r"instance & $n$ & method & $\delta e^*_{\rm in}$ & $\delta e^*_{\rm out}$ & $\delta e^*_{\rm law}$ & "
            r"law/out & status at $\delta e=10^{-3}\dots10^{-2}$"]
    write("huang_featured", rel(F_HU) + " (rows[*].tau)", "@{}lclccccl@{}", head, groups)
    # all pair correlators at n = 20
    grid = [w["de"] for w in d["pairs"]["4_1"][0]["tau"]["widths"]]
    rows, tot = [], [0] * len(grid)
    for inst in ("4_1", "4_2", "4_3"):
        prs = d["pairs"][inst]
        cnt = [sum(1 for p in prs if p["tau"]["status"][i] == "C") for i in range(len(grid))]
        tot = [a + b for a, b in zip(tot, cnt)]
        rows.append(["$(%s)$" % inst.replace("_", ",")] + ["%d" % c for c in cnt])
    rows.append([r"all (%d pairs)" % sum(len(d["pairs"][i]) for i in d["pairs"])] + ["%d" % c for c in tot])
    head = [r"instance & " + " & ".join(r"$%s\times10^{%d}$" % ((sig(g * 1e2, 2), -2) if g >= 1e-2 else
                                                                (sig(g * 1e3, 2), -3)) for g in grid)]
    write("huang_pairs", rel(F_HU) + " (pairs[*][*].tau.status)", "@{}l" + "c" * len(grid) + "@{}", head,
          [(None, rows)])
    return tot


def main():
    c = t_map_glance()
    v2 = t_rig_v2()
    v1 = t_rig_v1()
    t_qpu()
    tot = t_huang()
    print("rigor v2 verdicts:", v2)
    print("rigor v1 verdict (best level):", v1["verdict"], round(v1["rho_max"], 3))
    print("benchmark pairs certified per delta e (n = 20, 570 pairs):", tot)
    assert c["R"] == 17 and c["C*"] == 1, c
    assert tot[0] == 206 and tot[-1] == 3, tot


if __name__ == "__main__":
    main()
