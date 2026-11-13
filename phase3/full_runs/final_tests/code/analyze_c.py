"""Test C analysis (DECLARATION.md section 5). Reads fetched JSON only; exact arithmetic; seconds.
usage: python analyze_c.py <fetched out dir> <inputs dir> <output json> [job C]"""
import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, INP, RES = sys.argv[1:4]
JOBC = len(sys.argv) > 4
SRC = open(os.path.join(HERE, "ftlib.py"), encoding="utf8").read()
# only the interval functions of ftlib (no numpy / emu2 import needed for them)
exec(SRC[SRC.index("def side_bound"):])


def rj(*p):
    return json.load(open(os.path.join(*p)))


certs = rj(INP, "certs_n57_stored.json")
new = []
for vf in sorted(glob.glob(os.path.join(OUT, "c", "certs", "*_ver.json"))):
    v = rj(vf)
    if v.get("ok"):
        t = v["task"]
        new.append(dict(kind=t["kind"], Jz=str(t["Jz"]), sigma=int(t["sigma"]), lam=str(t["lam"]), level=t["clusters"],
                        E_LB_exact=v["E_LB_exact"], src="final_tests/" + os.path.basename(vf)[:-9], cert_sha256=v["cert_sha256"]))
S = {"m_s": 57, "Czz_bar": 64}


def row(E, cs, Jz, kind, truth=None):
    lo, hi, cu, cd = interval(E, cs, kind, Jz, S[kind])
    tau = tol_of(lo, hi)
    return dict(kind=kind, lo=float(lo), hi=float(hi), lo_exact=str(lo), hi_exact=str(hi), width=float(hi - lo), tau=float(tau),
                w_over_tau=float((hi - lo) / tau) if tau else None, below_tau=bool(hi - lo <= tau),
                up_cert=dict(lam=cu["lam"], level=cu["level"], src=cu["src"]), down_cert=dict(lam=cd["lam"], level=cd["level"], src=cd["src"]))


R = dict(n_stored=len(certs), n_new_verified=len(new), C1={}, C2={})
for var in ("rec", "ps"):
    q = rj(OUT, "c", "rq_B_J4.0_%s.json" % var)
    E = Fraction(q["E_exact"])
    R["C1"][var] = dict(E_exact_float=float(E), E_float=q["E_float"], D=q["D"], m_s_label=float(Fraction(q["m_s_exact"])),
                        Czz_bar_label=float(Fraction(q["Czz_bar_exact"])), m_s=row(E, certs, "4.0", "m_s"),
                        Czz_bar=row(E, certs, "4.0", "Czz_bar"))
    lab = R["C1"][var]
    lab["m_s"]["label_inside"] = bool(lab["m_s"]["lo"] <= lab["m_s_label"] <= lab["m_s"]["hi"])
    lab["Czz_bar"]["label_inside"] = bool(lab["Czz_bar"]["lo"] <= lab["Czz_bar_label"] <= lab["Czz_bar"]["hi"])
sd = rj(INP, "stored_device_B_J4.0.json")
R["C1"]["check_E_vs_stored"] = abs(R["C1"]["rec"]["E_exact_float"] - sd["var"]["rec"]["E"])
sim = rj(OUT, "c", "sim.json")
E0 = {4.0: sim["E0"]["4.0"], 6.0: sim["E0"]["6.0"]}
allc = certs + new
thr = {}
for tag, cs in (("stored_only", certs), ("stored_plus_new", allc)):
    a = threshold(cs, "m_s", "6.0", 57, Fraction(E0[6.0]) + Fraction(1, 100), Fraction(E0[6.0]) + 3)
    thr[tag] = None if a is None else float(a) - E0[6.0]
R["C2"]["eps_threshold_m_s"] = thr
R["C2"]["E_threshold_exact"] = str(threshold(allc, "m_s", "6.0", 57, Fraction(E0[6.0]) + Fraction(1, 100), Fraction(E0[6.0]) + 3))
tags = {}
for r in sim["rows"]:
    tags.setdefault(r["tag"], []).append(r["eps"])
R["C2"]["eps_sim"] = {k: dict(mean=sum(v) / len(v), values=v) for k, v in tags.items()}
R["C2"]["p_k"] = sim["p_k"]
R["C2"]["validation_eps_J4"] = dict(sim=R["C2"]["eps_sim"]["J4.0_S23000"]["mean"], device=sd["var"]["rec"]["E"] - sd["E0"])
R["C2"]["validation_eps_J4"]["ratio_device_over_sim"] = R["C2"]["validation_eps_J4"]["device"] / R["C2"]["validation_eps_J4"]["sim"]
e6 = R["C2"]["eps_sim"]["J6.0_S40000"]["mean"]
t = thr["stored_plus_new"]
R["C2"]["gate"] = dict(eps_sim=e6, eps_threshold=t, limit=0.8 * t, ratio=e6 / t, PASS=bool(e6 <= 0.8 * t),
                       eps_sim_rescaled=e6 * max(1.0, R["C2"]["validation_eps_J4"]["ratio_device_over_sim"]))
if JOBC:
    R["C3"] = {}
    for var in ("rec", "ps"):
        q = rj(OUT, "c", "rq_C_J6.0_%s.json" % var)
        E = Fraction(q["E_exact"])
        x = dict(E_exact=q["E_exact"], E_float=float(E), eps=float(E) - E0[6.0], D=q["D"], m_s_label=float(Fraction(q["m_s_exact"])),
                 Czz_bar_label=float(Fraction(q["Czz_bar_exact"])), m_s=row(E, allc, "6.0", "m_s"), Czz_bar=row(E, allc, "6.0", "Czz_bar"))
        x["m_s"]["label_inside"] = bool(x["m_s"]["lo"] <= x["m_s_label"] <= x["m_s"]["hi"])
        x["Czz_bar"]["label_inside"] = bool(x["Czz_bar"]["lo"] <= x["Czz_bar_label"] <= x["Czz_bar"]["hi"])
        R["C3"][var] = x
json.dump(R, open(RES, "w"), indent=1)
print(json.dumps(R, indent=1)[:6000])
