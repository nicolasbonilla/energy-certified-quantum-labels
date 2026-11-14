"""device_null_lib.py -- helpers of device_null_controls.py. Reads only; floating point (estimates, not proofs).

Copy of the helper of the study of 2026-11-12 (paper/reviews/R10_2026-11-12/scratch/level-experiment/lx_lib.py) with
the paths made relative to this file, so that it runs inside the replication package.

- load_certs(): every verified exact-arithmetic certificate at n = 57 (rigor runs v1 and v2; the six of the final
  tests), as floats.
- cert_interval(): the interval of a label at energy E from a list of certificates (the formula of the device
  analysis, in floats), with the reference-free tolerance 0.06 * min|O|.
"""
import glob
import json
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..")).replace(os.sep, "/")
FR = ROOT + "/phase3/full_runs"
FT = FR + "/final_tests"
RIG = FR + "/rigor"
MAPO = FR + "/map/laptop_analysis/out"
SS = {"m_s": 57.0, "Czz_bar": 64.0}


def rj(p):
    with open(p) as f:
        return json.load(f)


def _fr(v):
    return float(Fraction(v)) if isinstance(v, str) else float(v)


def load_certs(n=57):
    out = []
    for d, tag in ((RIG + "/out_20261031T073328Z/out/jobs", "v1"), (RIG + "/out_20261031T100015Z/out/jobs", "v2"),
                   (FT + "/out_20261106T120830Z/out/c/certs", "ft")):
        for vf in sorted(glob.glob(d + "/*_ver.json")):
            jid = os.path.basename(vf)[:-9]
            if ("n%d_" % n) not in jid:
                continue
            v = rj(vf)
            if not v.get("ok"):
                continue
            t = v["task"]
            if t.get("kind") not in SS or "lam" not in t or "sigma" not in t:
                continue
            lam = _fr(t["lam"])
            if lam <= 0:
                continue
            out.append(dict(kind=t["kind"], Jz=round(_fr(t["Jz"]), 6), sigma=int(t["sigma"]), lam=lam,
                            E_LB=float(Fraction(v["E_LB_exact"])), level=t["clusters"], src=tag + ":" + jid))
    return out


def side(E, certs, kind, Jz, sigma):
    best = None
    for c in certs:
        if c["kind"] != kind or abs(c["Jz"] - Jz) > 1e-9 or c["sigma"] != sigma:
            continue
        u = (E - c["E_LB"]) / (c["lam"] * SS[kind])
        if best is None or u < best[0]:
            best = (u, c)
    return best


def cert_interval(E, certs, kind, Jz):
    """(lo, hi, tau, w/tau, ...); tau = 0.06 * min(|lo|, |hi|) (reference-free); None if a side has no certificate."""
    up, dn = side(E, certs, kind, Jz, +1), side(E, certs, kind, Jz, -1)
    if up is None or dn is None:
        return None
    hi = min(up[0], 1.0)
    lo = max(-dn[0], -1.0)
    m = 0.0 if lo <= 0.0 <= hi else min(abs(lo), abs(hi))
    tau = 0.06 * m
    w = hi - lo
    return dict(lo=lo, hi=hi, tau=tau, w_over_tau=(w / tau if tau > 0 else float("inf")), up=up[1]["src"],
                up_lam=up[1]["lam"], dn=dn[1]["src"], dn_lam=dn[1]["lam"])


def E0_map(Jz, n=57):
    return float(rj(MAPO + "/thr/thr_n%d_J%.1f.json" % (n, Jz))["E0"])
