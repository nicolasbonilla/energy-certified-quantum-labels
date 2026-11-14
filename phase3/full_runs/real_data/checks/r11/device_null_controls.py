"""device_null_controls.py -- what did the processor contribute to the interval of the device label?

    python -B device_null_controls.py C     (the job at Jz = 6.0 of 2026-11-10)
    python -B device_null_controls.py B     (the job at Jz = 4.0 of 2026-10-31)

Inputs that contain no dynamics are pushed through the SAME pipeline as the stored device shots (recovery of the
sector, Rayleigh-Ritz in the span of the configurations, the stored exact lower bounds; here in floating point):
  N1  "noise only": the Neel string with independent bit flips, one probability per circuit chosen so that the
      fraction of in-sector strings equals the device's for that circuit; no Hamiltonian enters.
  N2  "site-shuffled": the device shots of a circuit with every site's column permuted independently over the
      shots: the single-site marginals of the device, no correlation between sites.
  and two sets written down with no sampling: the Neel string with its 64 single bond flips, and all
  configurations within two exchange moves of the Neel string.
Post hoc: computed on 2026-11-12, after the device result was known, by the study
paper/reviews/R10_2026-11-12/scratch/level-experiment/eb_null.py; this file is that script with paths relative to
the package, a portable count of set bits, and a summary block that rounds every range OUTWARD to two decimals.
Needs NumPy 2 (like phase3/full_runs/final_tests/code/emu2.py). About two minutes per job on two threads.
Reads only; writes device_null_controls_Jz<Jz>.json next to this script; the printed text is the stored output.
"""
import json
import math
import os
import sys
import time
from math import comb

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import device_null_lib as L  # noqa: E402

sys.path.insert(0, L.FT + "/code")
import emu2  # noqa: E402

job = sys.argv[1]
Jz = {"C": 6.0, "B": 4.0}[job]
Jzs = "%.1f" % Jz
raw = np.load(L.FT + ("/jobs/C_20261108/raw_configs.npz" if job == "C" else "/inputs/qpu_B_raw_configs.npz"))
shots = {k: np.asarray(raw["J%s_k%d" % (Jzs, k)], dtype=np.uint64) for k in range(1, 11)}
FULL = len(shots[1])
g = emu2.load_graph(L.FT + "/code/graphs/hh_d5.json")
n, n_down = g["n"], g["n_down"]
G = L.rj(L.FT + "/code/graphs/hh_d5.json")
eta = np.array([int(x) for x in G["eta"]])
edges = [tuple(e) for e in G["edges"]]
E0 = L.E0_map(Jz)
certs = [c for c in L.load_certs() if abs(c["Jz"] - Jz) < 1e-9]
NEEL = np.uint64(sum(1 << i for i in range(n) if eta[i] == -1))
BITS = np.arange(n, dtype=np.uint64)


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


def pack(M):
    return (M.astype(np.uint64) << BITS[None, :]).sum(axis=1).astype(np.uint64)


def unpack(x):
    return ((x[:, None] >> BITS[None, :]) & np.uint64(1)).astype(bool)


def in_sector_fraction(x):
    return float((unpack(np.asarray(x, dtype=np.uint64)).sum(axis=1) == n_down).mean())


def solve(allshots, rseed):
    Bu, _ = emu2.unique_rows(allshots.reshape(-1, 1).astype(np.uint64))
    cs = emu2.CSet(emu2.recover(Bu, n, n_down, np.random.default_rng(rseed)), n)
    cfg = np.asarray(cs.B[:, 0], dtype=np.uint64)
    E, a = emu2.ground(emu2.SubH(cs, g, float(Jz)), v0=emu2.neel_start(cs, g))
    iv = L.cert_interval(E, certs, "m_s", Jz)
    return dict(D=int(len(cfg)), eps=float(E - E0), w_over_tau=iv["w_over_tau"], in_sector=in_sector_fraction(allshots))


def down(x):
    return math.floor(x * 100.0 + 1e-9) / 100.0


def up(x):
    return math.ceil(x * 100.0 - 1e-9) / 100.0


out = dict(job=job, Jz=Jz, rows=[])
pk = {}
for k in range(1, 11):
    f = in_sector_fraction(shots[k])
    pk[k] = dict(in_sector=f, p_iid=inv(f))
out["pk"] = pk
print("device_null_controls.py, job %s, Jz = %s, n = %d; %d shots per circuit, 10 circuits" % (job, Jzs, n, FULL))
print("per circuit: in-sector fraction of the device, matched independent flip probability")
for k in pk:
    print("  k=%2d  in-sector %.4f  p %.4f" % (k, pk[k]["in_sector"], pk[k]["p_iid"]), flush=True)
for (name, ks) in (("k=1", [1]), ("k<=3", [1, 2, 3]), ("k<=10", list(range(1, 11)))):
    for seed in (1, 2):
        t0 = time.time()
        rs = np.random.default_rng(100 * seed + len(ks))
        dev = np.concatenate([shots[k] for k in ks])
        n1 = np.concatenate([pack(unpack(np.full(FULL, NEEL)) ^ (rs.random((FULL, n)) < pk[k]["p_iid"])) for k in ks])
        n2 = []
        for k in ks:
            M = unpack(shots[k])
            n2.append(pack(np.stack([M[rs.permutation(FULL), i] for i in range(n)], axis=1)))
        n2 = np.concatenate(n2)
        r = dict(circuits=name, seed=seed, shots=int(len(dev)), device=solve(dev, 5000 + seed),
                 noise_only=solve(n1, 6000 + seed), site_shuffled=solve(n2, 7000 + seed))
        out["rows"].append(r)
        print("%-6s seed %d shots %7d | device eps %.4f w/tau %.4f D %d | N1 noise-only eps %.4f w/tau %.4f D %d | "
              "N2 site-shuffled eps %.4f w/tau %.4f D %d  (%.0f s)" % (
                  name, seed, r["shots"], r["device"]["eps"], r["device"]["w_over_tau"], r["device"]["D"],
                  r["noise_only"]["eps"], r["noise_only"]["w_over_tau"], r["noise_only"]["D"],
                  r["site_shuffled"]["eps"], r["site_shuffled"]["w_over_tau"], r["site_shuffled"]["D"], time.time() - t0), flush=True)
# sets written down with no sampling at all
one = [NEEL] + [NEEL ^ np.uint64((1 << i) | (1 << j)) for (i, j) in edges]
two = set(int(x) for x in one)
for a_ in one[1:]:
    for (i, j) in edges:
        bi, bj = (int(a_) >> i) & 1, (int(a_) >> j) & 1
        if bi != bj:
            two.add(int(a_) ^ (1 << i) ^ (1 << j))
fixed = {}
for key, nm, lst in (("one", "Neel string and its %d single bond flips" % len(edges), one),
                     ("two", "all configurations within two exchange moves of the Neel string", sorted(two))):
    cs = emu2.CSet(np.array(lst, dtype=np.uint64).reshape(-1, 1), n)
    E, a = emu2.ground(emu2.SubH(cs, g, float(Jz)), v0=emu2.neel_start(cs, g))
    iv = L.cert_interval(E, certs, "m_s", Jz)
    fixed[key] = dict(name=nm, D=len(cs), eps=float(E - E0), w_over_tau=iv["w_over_tau"])
    print("%s: D = %d, eps = %.4f, m_s interval %.4f tau" % (nm, len(cs), E - E0, iv["w_over_tau"]))
out["fixed_sets"] = fixed

full = [r for r in out["rows"] if r["circuits"] == "k<=10"]
dv = [r["device"]["w_over_tau"] for r in full]
n1v = [r["noise_only"]["w_over_tau"] for r in full]
n2v = [r["site_shuffled"]["w_over_tau"] for r in full]
gain = [min(n1v) - max(dv), max(n1v) - min(dv)]
summary = dict(device=[down(min(dv)), up(max(dv))], noise_only=[down(min(n1v)), up(max(n1v))],
               site_shuffled=[down(min(n2v)), up(max(n2v))], one=up(fixed["one"]["w_over_tau"]),
               two=up(fixed["two"]["w_over_tau"]), gain=[down(gain[0]), up(gain[1])],
               D_device=[min(r["device"]["D"] for r in full), max(r["device"]["D"] for r in full)])


def device_range(name):
    v = [r["device"]["w_over_tau"] for r in out["rows"] if r["circuits"] == name]
    return [down(min(v)), up(max(v))]


# added 2026-11-14 (second pass): how much the later circuits add, and the in-sector fraction of the device shots
summary["device_first_circuit"] = device_range("k=1")
summary["device_first_three"] = device_range("k<=3")
summary["in_sector_first_tenth"] = [round(pk[1]["in_sector"], 2), round(pk[10]["in_sector"], 2)]
out["summary_rounded_outward"] = summary
print("")
print("SUMMARY (Jz = %s, all ten circuits, two recovery seeds; widths of the m_s interval in units of tau, every range" % Jzs)
print("rounded outward to two decimals; floating-point evaluation of the formula of the proved interval):")
print("  device shots: %.2f to %.2f tau (%d to %d configurations)" % (summary["device"][0], summary["device"][1], summary["D_device"][0], summary["D_device"][1]))
print("  noise-only strings (N1): %.2f to %.2f tau" % tuple(summary["noise_only"]))
print("  site-shuffled device shots (N2): %.2f to %.2f tau" % tuple(summary["site_shuffled"]))
print("  %s (%d configurations): %.2f tau" % (fixed["one"]["name"], fixed["one"]["D"], summary["one"]))
print("  %s (%d configurations): %.2f tau" % (fixed["two"]["name"], fixed["two"]["D"], summary["two"]))
print("  noise-only minus device: %.2f to %.2f tau" % tuple(summary["gain"]))
print("  device shots, first circuit only: %.2f to %.2f tau" % tuple(summary["device_first_circuit"]))
print("  device shots, first three circuits: %.2f to %.2f tau" % tuple(summary["device_first_three"]))
print("  in-sector fraction of the device shots: %.2f on the first circuit, %.2f on the tenth (rounded to two decimals)"
      % tuple(summary["in_sector_first_tenth"]))
json.dump(out, open(HERE + "/device_null_controls_Jz%s.json" % Jzs, "w"), indent=1)
