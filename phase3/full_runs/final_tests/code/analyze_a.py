"""Test A analysis (DECLARATION.md section 3). Reads fetched JSON only; seconds.
usage: python analyze_a.py <fetched out dir> <inputs dir> <output json>"""
import json
import os
import sys

import numpy as np

OUT, INP, RES = sys.argv[1:4]
NE = {19: 20, 57: 64, 115: 132}
A_JZ = {57: [1.5, 1.7, 2.8, 3.2], 115: [1.5, 1.7, 2.8]}


def rj(*p):
    return json.load(open(os.path.join(*p)))


C = {J: rj(OUT, "n19", "curve_J%.1f.json" % J) for J in A_JZ[57]}


def curve19(J, de):
    c = np.array(C[J]["curve"])
    return float(np.interp(np.sqrt(max(de, 0.0)), np.sqrt(np.maximum(c[:, 0], 0.0)), c[:, 1]))


def chord(J, de):
    m0 = C[J]["ms0"]
    dn = (-NE[19] * J / 4 - C[J]["E0"]) / 19
    return float((1 - m0) * np.sqrt(max(de, 0.0) / dn))


def curve57(e57, de):
    pts = sorted((v["dE_site"], v["err"]["dm_s"]) for k, v in e57["var"].items() if k in ("ideal", "primary", "dev_rec", "dev_ps"))
    s = np.sqrt(np.r_[0, [p[0] for p in pts]])
    y = np.r_[0, [p[1] for p in pts]]
    x = np.sqrt(de)
    return float(np.interp(x, s, y)) if x <= s[-1] else float(y[-1] + (y[-1] - y[-2]) / (s[-1] - s[-2]) * (x - s[-1]))


def stat(a):
    a = np.asarray(a, float)
    return dict(mean=float(a.mean()), max=float(a.max()), n=int(a.size))


emu = {(n, J): rj(OUT, "emu", "emu_n%d_J%.1f.json" % (n, J)) for n in A_JZ for J in A_JZ[n]}
R = dict(rows=[])
for n in (57, 115):
    for J in A_JZ[n]:
        e = emu[(n, J)]
        v = e["var"]["primary"]
        m0, m, de, dm = e["ref_m_s"], v["labels"]["m_s"], v["dE_site"], v["err"]["dm_s"]
        t = 0.06 * abs(m0)
        c19 = curve19(J, de)
        row = dict(n=n, J=J, m0=m0, m=m, de=de, dm=dm, tau=t, D=v["stats"]["D"], raw=abs(dm) / t, curve19_pred=c19,
                   miss_curve19=abs(dm - c19) / t, ratio=dm / c19, chord_pred=chord(J, de),
                   miss_chord=abs(dm - chord(J, de)) / t, small_truth=abs(C[J]["ms0"] - m0) / t)
        if n == 115:
            e57 = emu[(57, J)]
            c57 = curve57(e57, de)
            m19, m57 = C[J]["ms0"], e57["ref_m_s"]
            row.update(curve57_pred=c57, miss_curve57=abs(dm - c57) / t, truth57=abs(m57 - m0) / t)
            for name, g in (("a_b_over_n", lambda x: 1 / x), ("a_b_edges_over_n", lambda x: NE[x] / x),
                            ("a_b_over_sqrt_n", lambda x: x ** -.5)):
                b = (m19 - m57) / (g(19) - g(57))
                row["miss_" + name] = abs(m57 + b * (g(115) - g(57)) - m0) / t
        R["rows"].append(row)
R["ratios_all_variants_n57"] = {}
for J in A_JZ[57]:
    e = emu[(57, J)]
    R["ratios_all_variants_n57"][str(J)] = {k: v["err"]["dm_s"] / curve19(J, v["dE_site"]) for k, v in e["var"].items()
                                            if not v.get("alias_of")}
S = {}
for n in (57, 115):
    rs = [r for r in R["rows"] if r["n"] == n]
    S[str(n)] = {k: stat([r[k] for r in rs]) for k in rs[-1] if k.startswith("miss_") or k in ("raw", "small_truth", "truth57")}
    S[str(n)]["ratio_min"] = min(r["ratio"] for r in rs)
    S[str(n)]["ratio_max"] = max(r["ratio"] for r in rs)
R["summary"] = S
m57, m115 = S["57"]["miss_curve19"]["mean"], S["115"]["miss_curve19"]["mean"]
ratios = [r["ratio"] for r in R["rows"]]
R["rule"] = dict(mean57=m57, limit57=0.2, ok57=m57 <= 0.2, mean115=m115, limit115=0.6, ok115=m115 <= 0.6, ratio_min=min(ratios),
                 ratio_max=max(ratios), ok_ratio=all(0.75 <= x <= 1.3 for x in ratios))
R["rule"]["HOLDS"] = bool(R["rule"]["ok57"] and R["rule"]["ok115"] and R["rule"]["ok_ratio"])
R["versus"] = {n: {k: S[n][k]["mean"] for k in S[n] if k.startswith("miss_")} for n in S}
# gates
st = {float(k): v for k, v in rj(INP, "stored_n19_curves.json").items()}
c16 = rj(OUT, "n19", "curve_J1.6.json")
a, b = np.array(c16["curve"]), np.array(st[1.6]["curve"])
R["gate_n19"] = dict(dE0=abs(c16["E0"] - st[1.6]["E0"]), dms0=abs(c16["ms0"] - st[1.6]["ms0"]), dcurve=float(np.abs(a - b).max()))
R["gate_n19"]["pass"] = bool(R["gate_n19"]["dE0"] <= 1e-8 and R["gate_n19"]["dms0"] <= 1e-6 and R["gate_n19"]["dcurve"] <= 1e-5)
er = rj(OUT, "emu", "emu_n57_J2.5.json")
es = rj(INP, "stored_emu_n57_J2.5.json")
R["gate_replication"] = dict(dE0=abs(er["E0"] - es["E0"]), dm_primary=abs(er["var"]["primary"]["err"]["dm_s"] - es["var"]["primary"]["err"]["dm_s"]),
                             dD=er["var"]["primary"]["stats"]["D"] - es["var"]["primary"]["stats"]["D"])
R["gate_replication"]["pass"] = bool(R["gate_replication"]["dE0"] <= 1e-3 and R["gate_replication"]["dm_primary"] <= 2e-3)
json.dump(R, open(RES, "w"), indent=1)
print(json.dumps({k: R[k] for k in ("rule", "versus", "gate_n19", "gate_replication")}, indent=1))
for r in R["rows"]:
    print("n=%3d J=%.1f de=%.5f dm=%+.4f raw %.2f curve19 %.3f ratio %.3f chord %.3f small %.2f %s" % (
        r["n"], r["J"], r["de"], r["dm"], r["raw"], r["miss_curve19"], r["ratio"], r["miss_chord"], r["small_truth"],
        " ".join("%s %.3f" % (k[5:], r[k]) for k in r if k.startswith("miss_") and k not in ("miss_curve19", "miss_chord"))))
