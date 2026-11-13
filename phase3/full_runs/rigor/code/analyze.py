"""Laptop analysis of the fetched rigor run (declared before the hash).
usage: python analyze.py <out_dir/out> <plan.json> <requirement.json> <results.json>

Per job: E_LB (exact, from *_ver.json, only if ok), F_ref (DMRG reference = upper bound on the true ground energy),
slack s = F_ref - E_LB (>= true slack), ED E0 (n = 19), true slack E0 - E_LB.
Per row (n, Jz, label) with decisive points sigma = +/-:
    rho_row = [sum_sigma s_sigma/(lam_sigma S)] / [tau - sum_sigma (E_up - F_sigma)/(lam_sigma S)]
    w_rig   = sum_sigma (E_up - E_LB_sigma)/(lam_sigma S)       (rigorous outer width at E_up; CERTIFIED iff <= tau)
Per H(Jz): rho_H = s_H / s_req,H, s_req,H = min over the two rows at that Jz of s_req.
Verdict (n = 57; best verified bound per item over the declared levels): rho_max = max(rho_rows, rho_H);
ACCEPT if rho_max <= 1, REJECT if rho_max >= 3, GRAY otherwise.  Gate: at n = 19 every verified E_LB <= ED E0 + 1e-9,
else NO DECISION.
"""
import json
import os
import sys
from fractions import Fraction

OUT, PLAN, REQ, RES = sys.argv[1:5]
plan = json.load(open(PLAN))
req = json.load(open(REQ))
J = os.path.join(OUT, "jobs")


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


ed_by_spec = {}
jobs = {}
for p in plan:
    jid = p["id"]
    ver = load(os.path.join(J, jid + "_ver.json"))
    cert = load(os.path.join(J, jid + "_cert.json"))
    ed = load(os.path.join(J, jid + "_ed.json"))
    level = p["task"]["clusters"]
    spec = jid.split("_" + level + "_", 1)[1]
    if ed:
        ed_by_spec[(p["n"], spec)] = ed["E0"]
    jobs[jid] = dict(id=jid, n=p["n"], level=level, spec=spec, task=p["task"], F_ref=p["F_ref"], row=p["row"],
                     verified=bool(ver and ver.get("ok")), E_LB=(ver["E_LB_float_floor"] if ver and ver.get("ok")
                                                                 else None),
                     E_LB_exact=(ver["E_LB_exact"] if ver and ver.get("ok") else None),
                     anderson=(cert["anderson"] if cert else None), float_bound=(cert["bound_float"] if cert else None),
                     opt_time_s=(cert["time_s"] if cert else None), ver_time_s=(ver["time_s"] if ver else None),
                     n_clusters=(cert["info"]["n_clusters"] if cert else None),
                     n_params=(cert["info"]["n_params"] if cert else None))
for j in jobs.values():
    j["E0_ED"] = ed_by_spec.get((j["n"], j["spec"]))
    j["slack_ref"] = (j["F_ref"] - j["E_LB"]) if (j["E_LB"] is not None and j["F_ref"] is not None) else None
    j["slack_true"] = (j["E0_ED"] - j["E_LB"]) if (j["E_LB"] is not None and j["E0_ED"] is not None) else None
    ref = j["F_ref"] if j["F_ref"] is not None else j["E0_ED"]
    j["slack_rel_pct"] = (100 * (ref - j["E_LB"]) / abs(ref)) if (j["E_LB"] is not None and ref) else None

gate = all(j["slack_true"] >= -1e-9 for j in jobs.values() if j["slack_true"] is not None)
gate_n = sum(1 for j in jobs.values() if j["slack_true"] is not None)


def best(n, spec):
    c = [j for j in jobs.values() if j["n"] == n and j["spec"] == spec and j["E_LB"] is not None]
    return max(c, key=lambda j: j["E_LB"]) if c else None


rows = []
for r in req:
    if (r["n"], r["Jz"]) not in ((57, 4.0), (57, 6.0), (19, 4.0)) or r["label"] not in ("m_s", "Czz_bar"):
        continue
    n, Jz, lab = r["n"], r["Jz"], r["label"]
    S = (n if lab == "m_s" else {57: 64, 19: 20}[n])
    pre = "G1_" if n == 19 else ""
    out = dict(n=n, Jz=Jz, label=lab, tau=r["tau"], E_up=r["E_up"], s_req=r["s_req"], levels={})
    for level in ("eball2", "vball2", "best"):
        num, den0, w, ok = 0.0, 0.0, 0.0, True
        sides = {}
        for s, sg in (("+", "p"), ("-", "m")):
            d = r["decisive"][s]
            spec = "%s%s_%s%.1f" % (pre, lab, sg, Jz)
            jj = best(n, spec) if level == "best" else jobs.get("n%d_%s_%s" % (n, level, spec))
            if not jj or jj["E_LB"] is None:
                ok = False
                break
            lS = d["lam"] * S
            sl = d["F"] - jj["E_LB"]
            num += sl / lS
            den0 += (r["E_up"] - d["F"]) / lS
            w += (r["E_up"] - jj["E_LB"]) / lS
            sides[s] = dict(job=jj["id"], E_LB=jj["E_LB"], F=d["F"], slack=sl, lam=d["lam"],
                            slack_rel_pct=100 * sl / abs(d["F"]), E0_ED=jj["E0_ED"])
        if ok:
            out["levels"][level] = dict(sides=sides, rho=num / (r["tau"] - den0), w_rig=w, w_over_tau=w / r["tau"],
                                        certified_rigorously=(w <= r["tau"]))
    rows.append(out)

Hs = []
for Jz in (4.0, 6.0):
    sreq = min(r["s_req"] for r in req if r["n"] == 57 and r["Jz"] == Jz and r["label"] in ("m_s", "Czz_bar"))
    o = dict(Jz=Jz, s_req=sreq, levels={})
    for level in ("eball2", "vball2", "best"):
        spec = "H_%.1f" % Jz
        jj = best(57, spec) if level == "best" else jobs.get("n57_%s_%s" % (level, spec))
        if jj and jj["E_LB"] is not None:
            o["levels"][level] = dict(job=jj["id"], E_LB=jj["E_LB"], E0_ref=jj["F_ref"], slack=jj["slack_ref"],
                                      slack_rel_pct=jj["slack_rel_pct"], rho=jj["slack_ref"] / sreq)
    Hs.append(o)

verdicts = {}
for level in ("eball2", "vball2", "best"):
    rh = [r["levels"][level]["rho"] for r in rows if r["n"] == 57 and level in r["levels"]]
    rH = [h["levels"][level]["rho"] for h in Hs if level in h["levels"]]
    complete = len(rh) == 4 and len(rH) == 2
    rmax = max(rh + rH) if (rh or rH) else None
    v = None
    if not gate:
        v = "NO DECISION (n = 19 gate failed)"
    elif not complete:
        v = "INCOMPLETE"
    else:
        v = "ACCEPT" if rmax <= 1 else ("REJECT" if rmax >= 3 else "GRAY")
    verdicts[level] = dict(rho_max=rmax, complete=complete, verdict=v,
                           rho_rows={("%s_%.1f" % (r["label"], r["Jz"])): r["levels"][level]["rho"]
                                     for r in rows if r["n"] == 57 and level in r["levels"]},
                           rho_H={("H_%.1f" % h["Jz"]): h["levels"][level]["rho"] for h in Hs if level in h["levels"]})

res = dict(gate_n19=dict(passed=gate, n_compared=gate_n), verdicts=verdicts, rows=rows, H=Hs,
           jobs=sorted(jobs.values(), key=lambda j: j["id"]))
json.dump(res, open(RES, "w"), indent=1)
print("gate n=19 (E_LB <= ED E0 for %d jobs):" % gate_n, gate)
for j in sorted(jobs.values(), key=lambda j: (j["n"], j["spec"], j["level"])):
    print("%-34s %-7s E_LB %14s  ref %12s  ED %12s  slack_ref %9s  slack_true %9s  rel %7s%%  Anderson %s" % (
        j["spec"], j["level"], "%.6f" % j["E_LB"] if j["E_LB"] is not None else "-",
        "%.6f" % j["F_ref"] if j["F_ref"] is not None else "-", "%.6f" % j["E0_ED"] if j["E0_ED"] is not None else "-",
        "%.5f" % j["slack_ref"] if j["slack_ref"] is not None else "-",
        "%.5f" % j["slack_true"] if j["slack_true"] is not None else "-",
        "%.4f" % j["slack_rel_pct"] if j["slack_rel_pct"] is not None else "-",
        "%.4f" % j["anderson"] if j["anderson"] is not None else "-"))
for r in rows:
    for level, L in r["levels"].items():
        print("row n=%d Jz=%.1f %-8s %-6s rho %.3f  w_rig/tau %.3f  rigorously certified: %s" % (
            r["n"], r["Jz"], r["label"], level, L["rho"], L["w_over_tau"], L["certified_rigorously"]))
for h in Hs:
    for level, L in h["levels"].items():
        print("H Jz=%.1f %-6s slack %.4f (%.3f%%) s_req %.4f rho %.3f" % (h["Jz"], level, L["slack"],
                                                                     L["slack_rel_pct"], h["s_req"], L["rho"]))
for level, v in verdicts.items():
    print("VERDICT %-6s rho_max %s -> %s" % (level, "%.3f" % v["rho_max"] if v["rho_max"] is not None else "-",
                                               v["verdict"]))
