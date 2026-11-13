"""R10 reviewer phys-declared-stats: own exact-fraction evaluation of the device intervals of the third declared test
(main.tex 750-758; supplement Table 'ft_c') from the stored exact Rayleigh quotients and the stored/verified lower
bounds.  Checks arithmetic and reporting only: the certificates themselves (E_LB_exact) are taken as stored.
Also reads the gate numbers of the simulation (seed spread).  Reads only."""
import glob
import json
import os
from fractions import Fraction as Fr

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
FT = ROOT + "/phase3/full_runs/final_tests"
HERE = os.path.dirname(os.path.abspath(__file__))
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def rj(p):
    with open(p) as f:
        return json.load(f)


certs = [dict(kind=c["kind"], Jz=c["Jz"], sigma=int(c["sigma"]), lam=c["lam"], E_LB=c["E_LB_exact"], src="stored") for c in rj(FT + "/inputs/certs_n57_stored.json")]
new = 0
for f in sorted(glob.glob(FT + "/out_20261106T120830Z/out/c/certs/*_ver.json")):
    v = rj(f)
    assert v["ok"] is True
    t = v["task"]
    certs.append(dict(kind=t["kind"], Jz=t["Jz"], sigma=int(t["sigma"]), lam=t["lam"], E_LB=v["E_LB_exact"], src="new"))
    new += 1
P("certificates: %d stored + %d new verified; at Jz=6.0: %d (m_s %d, Czz_bar %d); at Jz=4.0: %d" % (
    len(certs) - new, new, sum(Fr(c["Jz"]) == 6 for c in certs), sum(Fr(c["Jz"]) == 6 and c["kind"] == "m_s" for c in certs),
    sum(Fr(c["Jz"]) == 6 and c["kind"] == "Czz_bar" for c in certs), sum(Fr(c["Jz"]) == 4 for c in certs)))
SS = {"m_s": 57, "Czz_bar": 64}


def interval(E, kind, Jz):
    best = {}
    for sg in (+1, -1):
        cand = [((E - Fr(c["E_LB"])) / (Fr(c["lam"]) * SS[kind]), c) for c in certs if c["kind"] == kind and Fr(c["Jz"]) == Fr(Jz) and c["sigma"] == sg]
        best[sg] = min(cand, key=lambda x: x[0])
    hi = min(best[+1][0], Fr(1))
    lo = max(-best[-1][0], Fr(-1))
    return lo, hi, best


def tol(lo, hi):
    m = Fr(0) if lo <= 0 <= hi else min(abs(lo), abs(hi))
    return Fr(6, 100) * m


for tag, path, Jz in (("device Jz=6.0 rec (decides)", FT + "/out_c3b_20261110T164846Z/out/c/rq_C_J6.0_rec.json", "6.0"),
                      ("device Jz=6.0 ps", FT + "/out_c3b_20261110T164846Z/out/c/rq_C_J6.0_ps.json", "6.0"),
                      ("device Jz=4.0 rec", FT + "/out_20261106T120830Z/out/c/rq_B_J4.0_rec.json", "4.0"),
                      ("device Jz=4.0 ps", FT + "/out_20261106T120830Z/out/c/rq_B_J4.0_ps.json", "4.0")):
    r = rj(path)
    E = Fr(r["E_exact"])
    P("%s: D=%d, E_exact=%.9f, |E_float-E_exact|=%.1e" % (tag, r["D"], float(E), abs(r["E_float"] - float(E))))
    for kind, labk in (("m_s", "m_s_exact"), ("Czz_bar", "Czz_bar_exact")):
        lo, hi, best = interval(E, kind, Jz)
        t = tol(lo, hi)
        lab = Fr(r[labk])
        P("   %-8s label %.6f  interval [%.6f, %.6f]  width %.6f  tau %.6f  width/tau %.4f  below tau: %s  label inside: %s  (upper cert %s lam=%s; lower cert %s lam=%s)" % (
            kind, float(lab), float(lo), float(hi), float(hi - lo), float(t), float((hi - lo) / t), (hi - lo) <= t, lo <= lab <= hi,
            best[+1][1]["src"], best[+1][1]["lam"], best[-1][1]["src"], best[-1][1]["lam"]))
        if kind == "m_s" and Jz == "6.0" and "rec" in tag:
            # how much energy margin is left: largest E with width <= tau (bisection in exact fractions)
            a, b = E, E + Fr(2)
            for _ in range(80):
                c = (a + b) / 2
                l2, h2, _ = interval(c, kind, Jz)
                if (h2 - l2) <= tol(l2, h2):
                    a = c
                else:
                    b = c
            P("   energy margin to the threshold: E_thr - E = %.4f J (%.5f per site); device energy error against stored DMRG E0 is a planning number only" % (float(a - E), float(a - E) / 57))

sim = rj(FT + "/out_20261106T120830Z/out/c/sim.json")
E0 = sim["E0"]
P("")
P("gate simulation (3 seeds each):")
for tag in ("J4.0_S23000", "J6.0_S40000", "J6.0_S23000"):
    v = [x["eps"] for x in sim["rows"] if x["tag"] == tag]
    P("  %s eps: %s mean %.4f min %.4f max %.4f" % (tag, [round(x, 4) for x in v], sum(v) / len(v), min(v), max(v)))
st = rj(FT + "/inputs/stored_device_B_J4.0.json")
P("  stored device job at Jz=4.0: keys", list(st.keys())[:12])
fez = rj(FT + "/out_20261106T120830Z/out/c/sim_fez.json")
P("  noise scan file keys:", list(fez.keys()))
for k, v in fez.items():
    if isinstance(v, list) and v and isinstance(v[0], dict):
        by = {}
        for x in v:
            by.setdefault(round(x.get("f", x.get("factor", -1)), 4), []).append(x.get("eps"))
        for f_, e_ in sorted(by.items()):
            P("    f=%s eps %s mean %.4f" % (f_, [round(y, 4) for y in e_], sum(e_) / len(e_)))
open(os.path.join(HERE, "recompute_c3_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
