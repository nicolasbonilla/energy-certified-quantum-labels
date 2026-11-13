"""Gates, decisive quantities, tables and derived curves of the full method runs (rules: ../DECLARATION.md §6-§8).

  python summarize.py <root>      -> <root>/out/summary.json, <root>/out/TABLES.md
"""
import glob
import json
import math
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fr import IBM_POST, IBM_PRE, IBM_GAP, IBM_INSECTOR, IBM_UNIQUE  # noqa: E402

# witness-pilot references (pilot_witness/RESULTS.md §1, §7, §8): E0 (chi 480 at n = 57, chi 320 at n = 115), m_s,GS
PILOT_REF = {(57, 1.2): (-27.86350709, 0.6404), (57, 1.6): (-32.53316921, 0.7703), (57, 2.5): (-44.68184805, 0.8972),
             (115, 1.6): (-66.60617474, 0.7846)}
PILOT_TOL = {57: (1e-3, 2e-3), 115: (2e-3, 3e-3)}
# IBM Supp. Fig. 11 (R4 §3.1 table, ±1 point by eye) and observable gates
IBM_DZ = {57: {1.1: 31.6, 1.2: 26.0, 1.3: 21.8, 1.4: 16.9, 1.5: 12.4, 1.6: 10.6, 2.5: 2.2, 4.0: 0.5},
          115: {1.1: 29.8, 1.2: 23.0, 1.3: 18.5, 1.4: 14.8, 1.5: 11.8, 1.6: 10.0, 2.5: 2.0, 4.0: 0.4}}
IBM_DCZZ_GATE = {57: {2.5: 3.4, 4.0: 1.4}, 115: {2.5: 2.9}}
# energy windows of m_s at the dataset's energy from the witness pilot / pilot2 (inner widths D, m_s^+, m_s^-)
WINDOW = {(57, 1.2): dict(D=0.4625, plus=0.8136, minus=0.3511, eps=0.5472, note="floor energy 0.8 x 0.012/site (IBM reports none)"),
          (57, 1.6): dict(D=0.3090, plus=0.8846, minus=0.5756, eps=0.4993, note="0.8 x IBM energy"),
          (57, 2.5): dict(D=0.0951, plus=0.9372, minus=0.8421, eps=0.1987, note="0.8 x IBM energy"),
          (115, 1.6): dict(D=0.2982, plus=0.8940, minus=0.5958, eps=1.0692, note="0.8 x IBM energy")}
STRONG, NULL = 0.05, 0.015
M_HI, M_LO = 0.7, 0.23
V_HI, V_LO = 0.6, 0.2
F_HI, F_LO = 0.5, 0.15


def rj(p):
    with open(p) as f:
        return json.load(f)


def within(a, b, fac):
    return a is not None and b is not None and a > 0 and b > 0 and abs(math.log(a / b)) <= math.log(fac)


def interp_log(xs, ys, x):
    """y at x by linear interpolation in log(x) (extrapolation from the two nearest points is flagged)."""
    pts = sorted((a, b) for a, b in zip(xs, ys) if a is not None and a > 0 and b is not None)
    if len(pts) < 2:
        return None, "insufficient"
    lx = np.log([p[0] for p in pts]); y = np.array([p[1] for p in pts]); t = math.log(x)
    if lx[0] <= t <= lx[-1]:
        return float(np.interp(t, lx, y)), "interpolated"
    i, j = (0, 1) if t < lx[0] else (len(lx) - 2, len(lx) - 1)
    if lx[j] == lx[i]:
        return float(y[i]), "extrapolated"
    return float(y[i] + (y[j] - y[i]) * (t - lx[i]) / (lx[j] - lx[i])), "extrapolated"


def plus_curve(wp, E0, mGS):
    """Upper concave envelope of (eps, m_s) over the '+' chain and the ground state (mixtures allowed)."""
    pts = [(0.0, mGS)] + sorted((p["E"] - E0, p["m_s"]) for p in wp["points"])
    hull = []
    for p in sorted(pts):
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (y2 - y1) * (p[0] - x1) <= (p[1] - y1) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(p)
    return hull


def plus_at(hull, eps):
    if eps is None or eps < 0:
        return None, "n/a"
    xs = [h[0] for h in hull]; ys = [h[1] for h in hull]
    if eps > xs[-1]:
        return ys[-1], "beyond_chain(lower bound on m_s^+)"
    return float(np.interp(eps, xs, ys)), "ok"


def main(root):
    O = os.path.join(root, "out")
    ref = {}
    for p in glob.glob(os.path.join(O, "ref", "ref_n*_J*.json")):
        r = rj(p); ref[(r["n"], round(r["Jz"], 1))] = r
    emu = {}
    for p in glob.glob(os.path.join(O, "emu", "emu_n*_J*.json")):
        r = rj(p); emu[(r["n"], round(r["Jz"], 1))] = r
    gs = {}
    for p in glob.glob(os.path.join(O, "gsscan", "gsscan_n*_J*.json")):
        r = rj(p); gs[(r["n"], round(r["Jz"], 1))] = r
    bo = {}
    for p in glob.glob(os.path.join(O, "bo", "bo_J*.json")):
        r = rj(p); bo[(round(r["Jz"], 1), r["subspace"])] = r
    wp = {}
    for p in glob.glob(os.path.join(O, "wplus", "wplus_n*_J*.json")):
        r = rj(p); wp[(r["n"], round(r["Jz"], 1))] = r
    cal = {n: rj(os.path.join(O, "calib", "calib_n%d.json" % n)) for n in (57, 115)
           if os.path.exists(os.path.join(O, "calib", "calib_n%d.json" % n))}
    S = dict(gates={}, decisions={}, calib={n: {k: v for k, v in c.items() if k != "rows"} for n, c in cal.items()})

    # ---------------------------------------------------------------- gates
    ut = []
    for f in glob.glob(os.path.join(O, "unit_tests_*_vm.txt")):
        txt = open(f, errors="replace").read()
        ut.append(dict(file=os.path.basename(f), ok=("\nOK" in txt or txt.startswith("OK"))))
    S["gates"]["G1_unit_tests_vm"] = dict(rows=ut, ok=bool(ut) and all(x["ok"] for x in ut))
    g2 = []
    for (n, j), (E, m) in PILOT_REF.items():
        if (n, j) in ref:
            dE = abs(ref[(n, j)]["E0"] - E); dm = abs(ref[(n, j)]["labels"]["m_s"] - m)
            g2.append(dict(n=n, Jz=j, dE0=dE, dm_s=dm, ok=dE <= PILOT_TOL[n][0] and dm <= PILOT_TOL[n][1]))
    S["gates"]["G2_refs"] = dict(rows=g2, ok=len(g2) == len(PILOT_REF) and all(x["ok"] for x in g2))

    def prim(n, j):
        e = emu.get((n, j))
        return e and e["var"].get("primary")
    for n in (57, 115):
        rows = []
        for j in (2.5, 4.0):
            p = prim(n, j)
            rows.append(dict(Jz=j, ratio=p and p["ratio"], ibm=IBM_POST[n][j],
                             ok=bool(p) and within(p["ratio"], IBM_POST[n][j], 2.0)))
        S["gates"]["G3_energy_n%d" % n] = dict(rows=rows, ok=all(r["ok"] for r in rows))
        rows = []
        for j, v in IBM_DCZZ_GATE[n].items():
            p = prim(n, j)
            rows.append(dict(Jz=j, dCzz=p and p["err"]["dCzz"], ibm=v, ok=bool(p) and within(p["err"]["dCzz"], v, 2.0)))
        if n == 115 and prim(115, 4.0):
            rows.append(dict(Jz=4.0, dCzz=prim(115, 4.0)["err"]["dCzz"], ibm=0.5, ok=None, note="recorded only"))
        S["gates"]["G4_Czz_n%d" % n] = dict(rows=rows, ok=all(r["ok"] for r in rows if r["ok"] is not None))
    S["gates"]["G5_sampling_state"] = {"%d_%s" % k: v["sampling_state"] for k, v in gs.items()}

    def gates_ok(n):
        G = S["gates"]
        return G["G1_unit_tests_vm"]["ok"] and G["G2_refs"]["ok"] and G["G3_energy_n%d" % n]["ok"] and \
            G["G4_Czz_n%d" % n]["ok"]

    # ---------------------------------------------------------------- families for bias vs energy ratio
    fam = {}
    for (n, j), e in emu.items():
        for name, v in e["var"].items():
            if v.get("alias_of"):
                continue
            fam.setdefault((n, j), {}).setdefault("pipeline_" + name, []).append(
                dict(ratio=v["ratio"], dm_s=v["err"]["dm_s"], dZ=v["err"]["dZ"], dCzz=v["err"]["dCzz"],
                     D=v["stats"]["D"], E=v["E"]))
        for s in e.get("kscan", []):
            fam[(n, j)].setdefault("kscan_" + s["variant"], []).append(
                dict(ratio=s["ratio"], dm_s=s["err"]["dm_s"], dZ=s["err"]["dZ"], dCzz=s["err"]["dCzz"],
                     D=s["stats"]["D"], E=s["E"], shots_per_circuit=s["shots_per_circuit"]))
    for (n, j), g in gs.items():
        F = fam.setdefault((n, j), {})
        for s in g["nested"]:
            F.setdefault("gs_random", []).append(dict(ratio=s["ratio"], dm_s=s["err"]["dm_s"], dZ=s["err"]["dZ"],
                                                      dCzz=s["err"]["dCzz"], D=s["D"], E=s["E"], N=s["N"],
                                                      W=s["W_captured"]))
            F.setdefault("gs_projected", []).append(dict(ratio=s["proj"]["ratio"], dm_s=s["proj"]["err"]["dm_s"],
                                                         dZ=s["proj"]["err"]["dZ"], D=s["D"], W=s["W_captured"]))
        for s in g["topD"]:
            F.setdefault("gs_top", []).append(dict(ratio=s["ratio"], dm_s=s["err"]["dm_s"], dZ=s["err"]["dZ"],
                                                   dCzz=s["err"]["dCzz"], D=s["D"], E=s["E"], W=s["W_captured"]))
    for (j, sub), b in bo.items():
        F = fam.setdefault((57, j), {})
        for name, v in b["variants"].items():
            if "unrot" in v:
                F.setdefault("bo_" + sub, []).append(dict(variant=name, ratio=v["ratio_bo"],
                                                          dm_s=v["unrot"]["err"]["dm_s"], dZ=v["unrot"]["err"]["dZ"],
                                                          dm_s_rot=v["rot"]["err"]["dm_s"], f=v["f_reduction"]))
    S["families"] = {"%d_%s" % k: v for k, v in fam.items()}

    # ---------------------------------------------------------------- bias at IBM's reported energy
    at_ibm = {}
    for (n, j), F in fam.items():
        r = IBM_POST[n].get(j)
        if r is None or "gs_random" not in F:
            continue
        pts = F["gs_random"]
        c, st = interp_log([p["ratio"] for p in pts], [p["dm_s"] for p in pts], r)
        lo, _ = interp_log([p["ratio"] for p in pts], [p["dm_s"] for p in pts], r * 1.05)
        hi, _ = interp_log([p["ratio"] for p in pts], [p["dm_s"] for p in pts], r * 0.95)
        dz, _ = interp_log([p["ratio"] for p in pts], [p["dZ"] for p in pts], r)
        others = {}
        for fn in ("gs_top", "kscan_ideal", "kscan_floor"):
            if fn in F and len(F[fn]) >= 2:
                v, s2 = interp_log([p["ratio"] for p in F[fn]], [p["dm_s"] for p in F[fn]], r)
                others[fn] = dict(dm_s=v, status=s2)
        vals = [c] + [o["dm_s"] for o in others.values() if o["status"] == "interpolated"]
        vals += [x for x in (lo, hi) if x is not None]
        at_ibm["%d_%s" % (n, j)] = dict(n=n, Jz=j, ibm_ratio=r, dm_s=c, status=st, dZ_pred=dz,
                                        ibm_dZ=IBM_DZ[n].get(j), other_families=others,
                                        band=[min(v for v in vals if v is not None), max(v for v in vals if v is not None)],
                                        m_s_GS=ref[(n, j)]["labels"]["m_s"] if (n, j) in ref else None)
    S["bias_at_ibm_energy"] = at_ibm

    # ---------------------------------------------------------------- dZ-matched reading (Supp. Fig. 11)
    dzm = {}
    for (n, j), F in fam.items():
        t = IBM_DZ[n].get(j)
        if t is None:
            continue
        pts = [p for fn, L in F.items() if not fn.startswith("gs_projected") and not fn.startswith("bo_") for p in L
               if p.get("dZ") is not None]
        if len(pts) < 2:
            continue
        x = np.array([p["dZ"] for p in pts]); y = np.array([p["dm_s"] for p in pts])
        k = float((x * y).sum() / (x * x).sum())
        ks = y / x
        out = dict(n=n, Jz=j, ibm_dZ=t, slope=k, slope_range=[float(ks.min()), float(ks.max())], dm_s=k * t,
                   dm_s_range=[float(ks.min() * t), float(ks.max() * t)], n_points=len(pts),
                   frac_points_over=float(np.mean(y > 0)))
        if "gs_random" in F:
            o = sorted(F["gs_random"], key=lambda p: p["dZ"])
            out["implied_ratio_gs_random"], out["implied_ratio_status"] = interp_log(
                [p["dZ"] for p in o], [math.log(p["ratio"]) for p in o], t)
            if out["implied_ratio_gs_random"] is not None:
                out["implied_ratio_gs_random"] = math.exp(out["implied_ratio_gs_random"])
        dzm["%d_%s" % (n, j)] = out
    S["dZ_matched"] = dzm

    # ---------------------------------------------------------------- window positions
    win = {}
    for (n, j), w in wp.items():
        if (n, j) not in ref:
            continue
        E0 = ref[(n, j)]["E0"]; mGS = ref[(n, j)]["labels"]["m_s"]
        hull = plus_curve(w, E0, mGS)
        rows = []
        for fn, L in fam.get((n, j), {}).items():
            for p in L:
                if p.get("E") is None:
                    continue
                eps = p["E"] - E0
                mp, st = plus_at(hull, eps)
                f = p["dm_s"] / (mp - mGS) if (mp is not None and mp > mGS) else None
                rows.append(dict(family=fn, eps=eps, dm_s=p["dm_s"], m_plus=mp, f_plus=f, status=st))
        gapv = ref and IBM_GAP[n].get(j)
        ib = at_ibm.get("%d_%s" % (n, j))
        x = None
        if ib and gapv:
            eps_ibm = ib["ibm_ratio"] * gapv
            mp, st = plus_at(hull, eps_ibm)
            x = dict(eps_ibm=eps_ibm, m_plus=mp, status=st, dm_s=ib["dm_s"],
                     f_plus=(ib["dm_s"] / (mp - mGS)) if (mp and mp > mGS and ib["dm_s"] is not None) else None)
        pw = WINDOW.get((n, j))
        if pw and ib and ib["dm_s"] is not None:
            pw = dict(pw, bias_over_D=ib["dm_s"] / pw["D"], bias_over_plus_half=ib["dm_s"] / (pw["plus"] - mGS))
        win["%d_%s" % (n, j)] = dict(hull=hull, states=rows, at_ibm=x, pilot_window=pw)
    for (n, j), pw in WINDOW.items():
        k = "%d_%s" % (n, j)
        ib = at_ibm.get(k)
        if k not in win and ib and ib["dm_s"] is not None and (n, j) in ref:
            mGS = ref[(n, j)]["labels"]["m_s"]
            win[k] = dict(pilot_window=dict(pw, bias_over_D=ib["dm_s"] / pw["D"],
                                            bias_over_plus_half=ib["dm_s"] / (pw["plus"] - mGS)))
    S["window"] = win

    # ---------------------------------------------------------------- decisions
    q1 = prim(115, 1.2)
    Q1 = q1 and q1["err"]["dm_s"]
    Q2 = at_ibm.get("115_1.6", {}).get("dm_s")
    ood115 = {j: prim(115, j)["err"]["dm_s"] for j in (1.1, 1.2, 1.3, 1.4) if prim(115, j)}
    if Q1 is None:
        d1 = "NO DECISION (missing n = 115, Jz = 1.2)"
    elif not gates_ok(115):
        d1 = "NO DECISION (gate failed)"
    elif Q1 <= -STRONG:
        d1 = "REVERSED (under-ordering)"
    elif ood115 and all(abs(v) < NULL for v in ood115.values()):
        d1 = "NULL"
    elif Q1 >= STRONG and Q2 is not None and Q2 >= STRONG:
        d1 = "KEEP (over-ordering persists at n = 115, also at the dataset's energy)"
    else:
        d1 = "SECONDARY"
    S["decisions"]["D1"] = dict(Q1_dm_s_115_1p2=Q1, Q2_dm_s_at_ibm_energy_115_1p6=Q2,
                                Q2_status=at_ibm.get("115_1.6", {}).get("status"), dm_s_ood_115=ood115,
                                gates_ok_115=gates_ok(115), rule=d1)
    # D2 mechanism share at n = 57 (and n = 115 recorded)
    for n in (57, 115):
        p = prim(n, 1.2); g = gs.get((n, 1.2))
        if p and g:
            pts = g["nested"]
            v, st = interp_log([x["D"] for x in pts], [x["err"]["dm_s"] for x in pts], p["stats"]["D"])
            M = v / p["err"]["dm_s"] if (v is not None and p["err"]["dm_s"]) else None
            rule = None
            if M is not None:
                rule = "TRUNCATION-DOMINATED" if M >= M_HI else ("PIPELINE-DOMINATED" if M <= M_LO else "MIXED")
            S["decisions"]["D2_n%d" % n] = dict(D_primary=p["stats"]["D"], dm_s_primary=p["err"]["dm_s"],
                                                dm_s_gs_at_D=v, status=st, M=M, rule=rule,
                                                decisive=(n == 57))
            # D3 vanishing with D
            v6, s6 = interp_log([x["D"] for x in pts], [x["err"]["dm_s"] for x in pts], 1e6)
            last = max(pts, key=lambda x: x["D"])
            V = last["err"]["dm_s"] / v6 if v6 else None
            rule3 = None
            if V is not None:
                rule3 = "PERSISTENT" if V >= V_HI else ("VANISHING" if V <= V_LO else "SLOW")
            # power-law fit dm_s ~ A D^-b over the nested points with D >= 1e5
            P = [(x["D"], x["err"]["dm_s"]) for x in pts if x["D"] >= 1e5 and x["err"]["dm_s"] > 0]
            fit = None
            if len(P) >= 3:
                b, a = np.polyfit(np.log([q[0] for q in P]), np.log([q[1] for q in P]), 1)
                mGS = ref[(n, 1.2)]["labels"]["m_s"]
                Dneed = math.exp((math.log(0.03 * mGS) - a) / b) if b < 0 else None
                fit = dict(exponent=float(-b), A=float(math.exp(a)), D_for_3pct_extrapolated=Dneed)
            S["decisions"]["D3_n%d" % n] = dict(dm_s_at_1e6=v6, status_1e6=s6, D_max=last["D"],
                                                dm_s_at_Dmax=last["err"]["dm_s"], V=V, rule=rule3,
                                                Dmax_ok=last["D"] >= 8e6 if n == 57 else None, powerlaw=fit,
                                                decisive=(n == 57))
    b = bo.get((2.5, "dev_rec"))
    if b:
        lit = {k: v["f_reduction"] for k, v in b["variants"].items() if v["stated_circuit"]}
        alt = {k: v["f_reduction"] for k, v in b["variants"].items() if not v["stated_circuit"]}
        fb = max(lit.values())
        rule = "REPRODUCED" if fb >= F_HI else ("NOT REPRODUCED" if fb < F_LO else "PARTIAL")
        S["decisions"]["D4"] = dict(f_best_stated=fb, f_stated=lit, f_alternatives=alt, rule=rule,
                                    ibm_f_2p5=1 - IBM_POST[57][2.5] / IBM_PRE[57][2.5])
    with open(os.path.join(O, "summary.json"), "w") as f:
        json.dump(S, f, indent=1)
    write_tables(O, S, ref, emu, gs, bo, cal, wp)
    print(json.dumps(dict(gates={k: v.get("ok") if isinstance(v, dict) else None for k, v in S["gates"].items()},
                          decisions={k: v.get("rule") for k, v in S["decisions"].items()}), indent=1))


def f4(x, fmt="%.4f"):
    return "-" if x is None else fmt % x


def write_tables(O, S, ref, emu, gs, bo, cal, wp):
    L = ["# Full method runs: tables (generated by code/summarize.py)", ""]
    L += ["## Gates", "", "```", json.dumps(S["gates"], indent=1)[:6000], "```", "",
          "## Decisions", "", "```", json.dumps(S["decisions"], indent=1), "```", ""]
    for n, c in sorted(cal.items()):
        L += ["## Calibration n = %d (Jz = 2.5; p_k = min(0.5, 0.01 + p k/10))" % n, "",
              "| p | unique | unique in sector | D | ratio |", "|---|---|---|---|---|"]
        for r in c["rows"]:
            L.append("| %.2f | %d | %d | %d | %.4f |" % (r["p"], r["n_unique"], r["n_unique_in_sector"], r["D"], r["ratio"]))
        L += ["", "p* = %.4f (%s, target ratio %.4f); p_dev = %.4f (%s, target in-sector %d); p_pre = %s" % (
            c["p_star"], c["status"], c["target_post"], c["p_dev"], c["status_dev"], c["target_insector"],
            f4(c.get("p_pre"))), ""]
    for n in (57, 115):
        rows = sorted((j, e) for (m, j), e in emu.items() if m == n)
        if not rows:
            continue
        for var in ("primary", "ideal", "floor", "dev_ps", "dev_rec", "pre"):
            sub = [(j, e["var"][var]) for j, e in rows if var in e["var"]]
            if not sub:
                continue
            L += ["## n = %d, variant %s" % (n, var), "",
                  "| Jz | D | ratio | IBM ratio | dE/site | m_s ref | m_s label | dm_s | dZ % | IBM dZ % | signed dZ (mean, min) | frac sites over | dCzz % | frac Czz stronger | dZloop % |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for j, v in sub:
                e = v["err"]
                L.append("| %.1f | %d | %s | %s | %.2e | %.4f | %.4f | %+.4f | %.2f | %s | %+.4f, %+.4f | %.2f | %.2f | %.2f | %s |" % (
                    j, v["stats"]["D"], f4(v["ratio"]), IBM_POST[n].get(j, "-"), v["dE_site"],
                    v["labels"]["m_s"] - e["dm_s"], v["labels"]["m_s"], e["dm_s"], e["dZ"],
                    {57: {1.1: 31.6, 1.2: 26.0, 1.3: 21.8, 1.4: 16.9, 1.6: 10.6}, 115: {1.1: 29.8, 1.2: 23.0, 1.3: 18.5,
                                                                                      1.4: 14.8, 1.6: 10.0}}[n].get(j, "-"),
                    e["signed_dZ_mean"], e["signed_dZ_min"], e["frac_sites_overordered"], e["dCzz"],
                    e["frac_Czz_stronger"], f4(e["dZloop"], "%.2f")))
            L.append("")
    for (n, j), g in sorted(gs.items()):
        L += ["## Ground-state sampling scan n = %d, Jz = %.1f (sampling state: %s)" % (n, j, json.dumps(g["sampling_state"])), "",
              "| subset | D | captured weight W | ratio RR | dm_s RR | dZ RR % | ratio proj | dm_s proj | dm_s sample mean | overlap RR-proj |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for s in g["nested"] + g["topD"]:
            L.append("| %s | %d | %.4f | %.4f | %+.4f | %.2f | %s | %+.4f | %s | %.4f |" % (
                s["tag"], s["D"], s["W_captured"], s["ratio"], s["err"]["dm_s"], s["err"]["dZ"],
                f4(s["proj"]["ratio"]), s["proj"]["err"]["dm_s"],
                f4(s.get("sample_mean", {}).get("dm_s"), "%+.4f"), s["overlap_RR_proj"]))
        L.append("")
    for (n, j), e in sorted(emu.items()):
        if e.get("kscan"):
            L += ["## Krylov shot scan n = %d, Jz = %.1f" % (n, j), "", "| variant | shots/circuit | D | ratio | dm_s |",
                  "|---|---|---|---|---|"]
            for s in e["kscan"]:
                L.append("| %s | %d | %d | %.4f | %+.4f |" % (s["variant"], s["shots_per_circuit"], s["stats"]["D"],
                                                            s["ratio"], s["err"]["dm_s"]))
            L.append("")
    for (j, sub), b in sorted(bo.items()):
        L += ["## Basis optimization, n = 57, Jz = %.1f, subspace %s (D = %d, ratio before %.4f)" % (j, sub, b["D"], b["ratio_pre"]), "",
              "| variant | stated circuit | strings | params | C(0) | C(opt) | E' | ratio after | f | theta rms | dm_s unrot | dm_s rot | E of psi' under H |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, v in b["variants"].items():
            L.append("| %s | %s | %d | %d | %.6f | %.6f | %.6f | %.4f | %.4f | %.2e | %s | %s | %s |" % (
                name, v["stated_circuit"], v["n_strings"], v["n_params"], v["C_at_0"], v["C_opt"], v["E_bo"],
                v["ratio_bo"], v["f_reduction"], v["theta_rms"],
                f4(v.get("unrot", {}).get("err", {}).get("dm_s"), "%+.4f"),
                f4(v.get("rot", {}).get("err", {}).get("dm_s"), "%+.4f"), f4(v.get("E_of_psi_unrotated_H"), "%.6f")))
        L.append("")
    L += ["## Bias at IBM's reported energy (gs_random interpolation in log ratio)", "", "```",
          json.dumps(S["bias_at_ibm_energy"], indent=1), "```", "", "## dZ-matched reading", "", "```",
          json.dumps(S["dZ_matched"], indent=1), "```", "", "## Window positions", "", "```",
          json.dumps({k: dict(at_ibm=v.get("at_ibm"), pilot_window=v.get("pilot_window"),
                              states=[s for s in v.get("states", []) if s["family"].startswith("pipeline")])
                      for k, v in S["window"].items()}, indent=1), "```", ""]
    with open(os.path.join(O, "TABLES.md"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
