"""E1 plan: the declared lambda grid of rigor/DECLARATION_v2.md Sec. 2 for the five m_s rows of extension E1
(real_data/DECLARATION.md Sec. 3): n = 57 at Jz = 3.3, 3.2; n = 115 at Jz = 5.0, 3.6, 3.3 (this order of priority).

Derived from rigor/code/make_plan_v2.py (SHA-256 8f76ff92...). The body of `build_row` is the loop body of that
script, statement by statement; only the inputs differ:
  - rows: the five E1 rows (m_s only) instead of the scopes S1-S3;
  - tau: the stored tau of the row (summary_map.json, = 0.06 |O_GS| with this project's reference), as in v2 (there
    read through requirement.json, which holds only the rows the map certified and so lacks n = 57 at 3.2 and 3.3);
  - the row's upper energy E_up: the PUBLIC energy of the row plus the allowance of real_data/DECLARATION.md Sec. 2,
    E_up := E_real + 1e-6, E_real = `final_global_energy` of group `skqd_random_flip` (converted/real_n<n>.json).
    Reason (fixed in e1/E1_SPEC.md before any E1 bound was computed): the E1 certificates serve the rows of the
    real-data map, whose energy is E_real; with the digitized upper reading of the stored map the pruning rule of
    v2 leaves nothing to compute at n = 57, Jz = 3.2 and 3.3 (printed below for the record).
E_up enters only the choice of points (lambda_dec, pruning, order, stopping, stage B). It never enters a certificate:
every certificate is a statement about the operator H(Jz) - sigma lam S O + mu M_tot and holds for any energy.

Self-check (always run first): the same `build_row`, fed with the stored v2 inputs (rigor/outputs/requirement.json),
must reproduce rigor/outputs/grid_v2.json and the stage-A entries of plan_v2_A.json exactly. Otherwise nothing is written.

usage: python -B -I make_plan_e1.py            (standard library only; reads converted/ only after the hash check)
writes e1/plan_e1.json, e1/grid_e1.json, e1/plan_e1_stdout.txt is the redirected output
"""
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
E1 = os.path.dirname(HERE)
RD = os.path.dirname(E1)
FULL = os.path.dirname(RD)
CH = os.path.join(FULL, "map", "laptop_analysis", "out", "chains")
SUMMARY = os.path.join(FULL, "map", "laptop_analysis", "summary_map.json")
V2_REQ = os.path.join(FULL, "rigor", "outputs", "requirement.json")
V2_GRID = os.path.join(FULL, "rigor", "outputs", "grid_v2.json")
V2_PLAN = os.path.join(FULL, "rigor", "outputs", "plan_v2_A.json")

GRAPH = {19: "hh_d3.json", 57: "hh_d5.json", 115: "hh_d7.json"}
NE = {19: 20, 57: 64, 115: 132}
REF = (0.85, 0.85 ** 2, 0.85 ** 3)
OPT_V = dict(K=32, maxiter=600, betas=[30, 300, 3000, 30000, 100000], use_mu=True, clusters="vball2")
# (cap group of stage B, priority, n, Jz): the order of real_data/DECLARATION.md Sec. 3
E1_ROWS = [("E57", 0, 57, 3.3), ("E57", 1, 57, 3.2), ("E115", 2, 115, 5.0), ("E115", 3, 115, 3.6), ("E115", 4, 115, 3.3)]
ALLOW = 1e-6


def dyadic(x, bits=20):
    return Fraction(round(x * 2 ** bits), 2 ** bits)


def build_row(scope, n, Jz, lab, Eup, tau, s_req, prefix):
    """Loop body of make_plan_v2.py: returns (grid row, plan entries of stage A)."""
    S = float(n if lab == "m_s" else NE[n])
    sides = {}
    for s, sg in (("+", 1), ("-", -1)):
        ch = json.load(open(os.path.join(CH, "chain_n%d_J%.1f_%s_%s.json" % (n, Jz, lab, s))))
        st = [(p["E"], p["o"]) for p in ch["points"]]

        def Fup(lam):
            return min(E - sg * lam * S * o for (E, o) in st)
        pts = []
        for p in ch["points"]:
            lam = Fraction(p["lam"])
            pts.append(dict(lam=str(lam), lam_f=p["lam"], kind="chain", F=p["F"], F_up=min(p["F"], Fup(p["lam"])),
                            eps=p["eps"]))
        dec = min(pts, key=lambda q: (Eup - q["F"]) / (q["lam_f"] * S))
        for f in REF:
            lam = dyadic(dec["lam_f"] * f)
            pts.append(dict(lam=str(lam), lam_f=float(lam), kind="ref%.4f" % f, F=None, F_up=Fup(float(lam)),
                            eps=None))
        for q in pts:
            q["u_lb"] = (Eup - q["F_up"]) / (q["lam_f"] * S)
        sides[s] = dict(sigma=sg, pts=pts, lam_dec=dec["lam_f"])
    for s, o in (("+", "-"), ("-", "+")):
        best_other = min(q["u_lb"] for q in sides[o]["pts"])
        for q in sides[s]["pts"]:
            q["pruned"] = q["u_lb"] + best_other > tau
    w_F = sum(min((Eup - q["F"]) / (q["lam_f"] * S) for q in sides[s]["pts"] if q["F"] is not None)
              for s in "+-")
    row = dict(scope=scope, n=n, Jz=Jz, label=lab, S=S, E_up=Eup, tau=tau, s_req=s_req, w_F=w_F,
               sides=sides)
    plan = []
    for s in "+-":
        for q in sorted(sides[s]["pts"], key=lambda q: q["u_lb"]):
            if q["pruned"]:
                continue
            task = dict(OPT_V, kind=lab, Jz=repr(Jz), sigma=sides[s]["sigma"], lam=q["lam"])
            plan.append(dict(id="%s_n%d_vball2_%s_%s%.1f_l%.6f" % (prefix, n, lab, "p" if s == "+" else "m", Jz, q["lam_f"]),
                             graph=GRAPH[n], task=task, ed=False, n=n, scope=scope, row="%d_%.1f_%s" % (n, Jz, lab),
                             side=s, lam_f=q["lam_f"], F=q["F"], F_up=q["F_up"], u_lb=q["u_lb"], kind=q["kind"]))
    return row, plan


def self_check():
    """The copied rule reproduces the stored v2 grid and stage-A plan from the stored v2 inputs."""
    req = json.load(open(V2_REQ))
    grid0 = json.load(open(V2_GRID))
    plan0 = [p for p in json.load(open(V2_PLAN)) if p["scope"] != "G19"]
    grid, plan = [], []
    for scope, n, Jzs in [("S1", 57, [4.0, 6.0]), ("S2", 57, [3.4, 3.6, 4.5, 5.0, 5.5]), ("S3", 115, [4.0, 6.0])]:
        for Jz in Jzs:
            for lab in ("m_s", "Czz_bar"):
                r = next(x for x in req if x["n"] == n and x["Jz"] == Jz and x["label"] == lab)
                row, pl = build_row(scope, n, Jz, lab, r["E_up"], r["tau"], r["s_req"], "v2")
                grid.append(row)
                plan += pl
    order = {"S1": 0, "S2": 2, "S3": 3}
    plan.sort(key=lambda p: order[p["scope"]])
    g_ok = json.loads(json.dumps(grid)) == grid0
    p_ok = json.loads(json.dumps(plan)) == plan0
    return g_ok, p_ok, len(grid0), len(plan0)


def main():
    decl = hashlib.sha256(open(os.path.join(RD, "DECLARATION.md"), "rb").read()).hexdigest()
    rec = open(os.path.join(RD, "DECLARATION.sha256")).read().split()[0]
    if decl != rec:
        raise SystemExit("REFUSED: DECLARATION.md does not match DECLARATION.sha256")
    print("declaration SHA-256 %s matches" % decl)
    g_ok, p_ok, ng, npl = self_check()
    print("self-check against the stored v2 grid (%d rows) and stage-A plan (%d jobs): grid %s, plan %s" % (ng, npl, g_ok, p_ok))
    if not (g_ok and p_ok):
        raise SystemExit("REFUSED: the copied rule does not reproduce the stored v2 grid; nothing written")
    S = json.load(open(SUMMARY))
    real = {n: json.load(open(os.path.join(RD, "converted", "real_n%d.json" % n))) for n in (57, 115)}
    grid, plan = [], []
    for scope, prio, n, Jz in E1_ROWS:
        r = next(x for x in S["rows"] if x["n"] == n and abs(x["Jz"] - Jz) < 1e-9 and x["label"] == "m_s")
        ref = S["refs"]["%d_%.1f" % (n, Jz)]
        e = real[n]["skqd_random_flip"]["%.1f" % Jz]
        assert abs(float(e["jz"]) - Jz) < 1e-9
        E_real = float(e["final_global_energy"])
        Eup = E_real + ALLOW
        tau = r["tau"]
        row, pl = build_row(scope, n, Jz, "m_s", Eup, tau, None, "e1")
        row.update(prio=prio, E_real=E_real, E0_ref=ref["E0"], eps_real=E_real - ref["E0"], E_up_digitized=ref["E_up"],
                   O_GS=r["O_GS"], stored_map_status=r["status"])
        for p in pl:
            p["prio"] = prio
        # for the record only: what the same rule gives with the digitized upper reading of the stored map
        row_d, pl_d = build_row(scope, n, Jz, "m_s", ref["E_up"], tau, None, "e1")
        row["with_digitized_E_up"] = dict(E_up=ref["E_up"], w_F_over_tau=row_d["w_F"] / tau, n_jobs_kept=len(pl_d),
                                          lam_dec={s: row_d["sides"][s]["lam_dec"] for s in "+-"})
        grid.append(row)
        plan += pl
        ns = {s: (len(row["sides"][s]["pts"]), sum(not q["pruned"] for q in row["sides"][s]["pts"])) for s in "+-"}
        print("prio %d %s n=%d Jz=%.1f m_s  E_real %.6f eps_real %.5f (digitized eps_up %.5f) tau %.5f  w_F/tau %.3f  "
              "grid(+) %d kept %d  grid(-) %d kept %d  lam_dec %.4f / %.4f | with the digitized E_up: w_F/tau %.3f, jobs kept %d" % (
                  prio, scope, n, Jz, E_real, E_real - ref["E0"], ref["eps_up"], tau, row["w_F"] / tau, ns["+"][0], ns["+"][1],
                  ns["-"][0], ns["-"][1], row["sides"]["+"]["lam_dec"], row["sides"]["-"]["lam_dec"],
                  row_d["w_F"] / tau, len(pl_d)))
        for s in "+-":
            print("      side %s: " % s + "  ".join("%.5f%s%s(u_lb/tau %.3f)" % (q["lam_f"], "c" if q["kind"] == "chain" else "r",
                                                                              "X" if q["pruned"] else "", q["u_lb"] / tau)
                                                    for q in sorted(row["sides"][s]["pts"], key=lambda q: q["u_lb"])))
    plan.sort(key=lambda p: p["prio"])
    json.dump(plan, open(os.path.join(E1, "plan_e1.json"), "w"), indent=1)
    json.dump(grid, open(os.path.join(E1, "grid_e1.json"), "w"), indent=1)
    from collections import Counter
    print("stage-A jobs at most:", dict(Counter("%d_%.1f" % (p["n"], p["task"] and float(p["task"]["Jz"])) for p in plan)), "total", len(plan))
    print("legend: c = chain point, r = refinement point, X = pruned (not computed)")


if __name__ == "__main__":
    main()
