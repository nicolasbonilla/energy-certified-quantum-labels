"""C3b, seconds on the laptop, read-only: effective i.i.d. flip probability per circuit from the in-sector shot fraction.
For any in-sector configuration (33 up, 24 down) i.i.d. flips with probability p keep the sector with probability
P(p) = sum_j C(24,j) C(33,j) p^(2j) (1-p)^(57-2j), independent of the state; ft.calibrate_pk inverts the same function by
Monte Carlo. Compares today's p_k (Jz = 6, ibm_kingston) with the gate's p_k (job B, Jz = 4) -> noise factor f per circuit.
usage: python code_c3b/noise_c3b.py <out.json>   (exploratory; no rule uses it)"""
import json
import sys
from math import comb


def P(p, nu=33, nd=24):
    return sum(comb(nd, j) * comb(nu, j) * p ** (2 * j) * (1 - p) ** (nu + nd - 2 * j) for j in range(nd + 1))


def inv(f):
    a, b = 0.0, 0.5
    for _ in range(80):
        c = 0.5 * (a + b)
        if P(c) > f:
            a = c
        else:
            b = c
    return 0.5 * (a + b)


fe = json.load(open("jobs/C_20261108/fetch.json"))["pubs"]
pb = json.load(open("inputs/qpu_B_pubs.json"))
sim = json.load(open("out_20261106T120830Z/out/c/sim.json"))
R = dict(rows=[])
for k in range(1, 11):
    fc = fe["J6.0_k%d" % k]["shots_in_sector"] / fe["J6.0_k%d" % k]["shots"]
    fb = pb["J4.0_k%d" % k]["shots_in_sector"] / pb["J4.0_k%d" % k]["shots"]
    pc, pbk = inv(fc), inv(fb)
    R["rows"].append(dict(k=k, in_sector_C=fc, in_sector_B=fb, p_C=pc, p_B_exact_inverse=pbk, p_B_gate=sim["p_k"][k - 1], f=pc / sim["p_k"][k - 1]))
    print("k=%2d in-sector C %.4f B %.4f  p_C %.4f p_B %.4f (gate %.4f)  f %.3f" % (k, fc, fb, pc, pbk, sim["p_k"][k - 1], pc / sim["p_k"][k - 1]))
for t in ("neel",):
    fc = fe[t]["shots_in_sector"] / fe[t]["shots"]
    R[t] = dict(in_sector_C=fc, p_C=inv(fc))
    fbn = pb[t]["shots_in_sector"] / pb[t]["shots"] if t in pb else None
    R[t]["in_sector_B"] = fbn
    R[t]["p_B"] = inv(fbn) if fbn else None
    print(t, R[t])
fs = [r["f"] for r in R["rows"]]
R["f_mean"] = sum(fs) / len(fs)
R["f_shot_weighted_over_k"] = sum(r["p_C"] for r in R["rows"]) / sum(r["p_B_gate"] for r in R["rows"])
print("f mean %.3f  f (sum p_C / sum p_gate) %.3f  min %.3f max %.3f" % (R["f_mean"], R["f_shot_weighted_over_k"], min(fs), max(fs)))
json.dump(R, open(sys.argv[1], "w"), indent=1)
