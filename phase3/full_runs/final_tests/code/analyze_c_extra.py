"""Test C, after the decision not to submit (DEVIATIONS.md item 3): intervals at Jz = 6 for the states that exist, for the statement that a classical
method is at least as good, and the noise scan. Planning numbers, not proofs: these energies are floats of stored or simulated states, not exact quotients.
usage: python analyze_c_extra.py <fetched out dir> <inputs dir> <output json>"""
import glob
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
OUT, INP, RES = sys.argv[1:4]
SRC = open(os.path.join(HERE, "ftlib.py"), encoding="utf8").read()
exec(SRC[SRC.index("def side_bound"):])


def rj(*p):
    return json.load(open(os.path.join(*p)))


certs = rj(INP, "certs_n57_stored.json")
for vf in sorted(glob.glob(os.path.join(OUT, "c", "certs", "*_ver.json"))):
    v = rj(vf)
    t = v["task"]
    certs.append(dict(kind=t["kind"], Jz=str(t["Jz"]), sigma=int(t["sigma"]), lam=str(t["lam"]), level=t["clusters"], E_LB_exact=v["E_LB_exact"],
                      src=os.path.basename(vf), cert_sha256=v["cert_sha256"]))
E0 = rj(OUT, "c", "sim.json")["E0"]["6.0"]
ctl = rj(OUT, "c", "control_J6.0.json")
fez = rj(OUT, "c", "sim_fez.json")
scan = {}
for r in fez["rows"]:
    scan.setdefault(round(r["factor"], 4), []).append(r["eps"])
scan = {str(k): dict(mean=sum(v) / len(v), values=v) for k, v in sorted(scan.items())}


def at(eps):
    o = {}
    for kind, S in (("m_s", 57), ("Czz_bar", 64)):
        lo, hi, _, _ = interval(Fraction(E0) + Fraction(eps), certs, kind, "6.0", S)
        t = tol_of(lo, hi)
        o[kind] = dict(lo=float(lo), hi=float(hi), width=float(hi - lo), tau=float(t), w_over_tau=float((hi - lo) / t))
    return o


R = dict(E0=E0, n_certs_J6=sum(1 for c in certs if Fraction(c["Jz"]) == 6), noise_scan_eps=scan, gate_limit=0.47824779600806555, eps_threshold=0.5978097450100819,
         control=dict(eps=ctl["var"]["rec"]["eps"], dm_s=ctl["var"]["rec"]["dm_s"], D=ctl["var"]["rec"]["D"], discarded=ctl["discarded_total"]),
         intervals=dict(dmrg_E0=at(0.0), noiseless_control=at(ctl["var"]["rec"]["eps"]), simulated_kingston_noise=at(0.2892371857278799),
                        simulated_fez_scaled=at(scan[str(round(fez["ratio"], 4))]["mean"])))
json.dump(R, open(RES, "w"), indent=1)
print(json.dumps(R, indent=1))
