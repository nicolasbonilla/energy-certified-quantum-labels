"""v_item4_ed19.py -- verifier V, item 4: the n = 19 numbers of theorem4_v2.tex, with my own exact diagonalization.

H(Jz, label, t) = K + (Jz/4) sum_E ZZ - lambda * S*O - (3 Jz/8) M ,  lambda = t * Jz,
S*O = sum_i eta_i Z_i (m_s), sum_E Z_i Z_j (C_zz), sum_{P2} Z_i Z_j (C_2).
All 20 sectors. Output: v_item4_ed19_out.txt / .json
  A. where statement (a) holds: min over the other sectors of the lowest level, minus the lowest level of the
     Neel sector (M = 3); grid Jz = 1.6 ... 5.5, seven tilt settings (table of break-theorem4, Sec. 8)
  B. the gap inside the Neel sector on the same grid
  C. Jz = 6, 12, 24, 48: gap over the whole space in units of Jz against the classical gap
  D. tilts outside the windows at Jz = 12, 48
  E. correlation sum max_i sum_j |<Z_i;Z_j>| at Jz = 6, no tilt
"""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v_common import patch, pairs_dist2, sector_states, zmat, hop_matrix, lowest
import numpy as np

t00 = time.time()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item4_ed19_out")
lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


n, E, names, eta = patch(3)
P2 = pairs_dist2(n, E)
assert n == 19 and len(E) == 20 and len(P2) == 25
NUP_NEEL = int((eta > 0).sum())            # 11
assert 2 * NUP_NEEL - n == 3
secs = {}
for nup in range(n + 1):
    st = sector_states(n, nup)
    z = zmat(st, n)
    secs[nup] = dict(K=hop_matrix(st, E, 0.5), zz=sum(z[:, i] * z[:, j] for i, j in E), stag=z @ eta,
                     p2=sum(z[:, i] * z[:, j] for i, j in P2), M=2 * nup - n, z=z if nup == NUP_NEEL else None)
say(f"n = {n}, |E| = {len(E)}, |P2| = {len(P2)}; Neel sector nup = {NUP_NEEL} (M = 3), dim {len(secs[NUP_NEEL]['zz'])}; "
    f"built in {time.time()-t00:.0f} s")
# Neel configuration is in the sector and has zz = -20
neel_bits = sum(1 << i for i in range(n) if eta[i] > 0)


def solve(Jz, label, t, field=0.375, want_vec=False):
    lam = t * Jz
    e0 = {}
    extra = {}
    for nup, S in secs.items():
        diag = 0.25 * Jz * S["zz"] - field * Jz * S["M"]
        if label == "ms":
            diag = diag - lam * S["stag"]
        elif label == "czz":
            diag = diag - lam * S["zz"]
        elif label == "c2":
            diag = diag - lam * S["p2"]
        elif label != "none":
            raise ValueError
        k = 2 if nup == NUP_NEEL else 1
        w, v = lowest(S["K"], diag, k=k)
        e0[nup] = float(w[0])
        if nup == NUP_NEEL:
            extra["sector_gap"] = float(w[1] - w[0])
            if want_vec:
                extra["vec"] = v[:, 0]
    eN = e0[NUP_NEEL]
    other = min(e for q, e in e0.items() if q != NUP_NEEL)
    arg = min((e, q) for q, e in e0.items() if q != NUP_NEEL)[1]
    extra.update(dc=other - eN, arg_other_M=2 * arg - n, e_neel=eN)
    return extra


TILTS = [("none", "no tilt", 0.0), ("ms", "m_s, -1/100", -1 / 100), ("ms", "m_s, -1/40", -1 / 40),
         ("czz", "C_zz, +1/100", 1 / 100), ("czz", "C_zz, +1/60", 1 / 60),
         ("c2", "C_2, -1/200", -1 / 200), ("c2", "C_2, -1/150", -1 / 150)]
JZ_A = [1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
res = dict(A={}, B={}, C={}, D={}, E={})

say("\nA. lowest level of the other sectors minus lowest level of the Neel sector, field 3Jz/8 (absolute units)")
say("   " + f"{'label, t':16s}" + "".join(f"{jz:>9.1f}" for jz in JZ_A))
secgap_min = (9e9, None)
for lab, nm, t in TILTS:
    row, rowg = [], []
    for jz in JZ_A:
        r = solve(jz, lab, t)
        row.append(r["dc"])
        rowg.append(r["sector_gap"])
        if r["sector_gap"] < secgap_min[0]:
            secgap_min = (r["sector_gap"], (nm, jz))
    res["A"][nm] = row
    res["B"][nm] = rowg
    say("   " + f"{nm:16s}" + "".join(f"{x:>+9.4f}" for x in row) + f"   [{time.time()-t00:.0f} s]")
say("\nB. gap inside the Neel sector on the same grid (absolute units)")
say("   " + f"{'label, t':16s}" + "".join(f"{jz:>9.1f}" for jz in JZ_A))
for lab, nm, t in TILTS:
    say("   " + f"{nm:16s}" + "".join(f"{x:>9.4f}" for x in res["B"][nm]))
say(f"   smallest sector gap on the grid: {secgap_min[0]:.4f} at {secgap_min[1]}")

say("\nC. gap of H - lambda S O - (3Jz/8) M over the whole space, units of Jz; classical gaps of break-theorem4 Sec. 8")
CL = {"no tilt": "1/4", "m_s, -1/100": "19/100", "m_s, -1/40": "1/10", "C_zz, +1/100": "21/100",
      "C_zz, +1/60": "11/60", "C_2, -1/200": "21/100", "C_2, -1/150": "59/300"}
JZ_C = [6.0, 12.0, 24.0, 48.0]
say("   " + f"{'label, t':16s}" + "".join(f"{jz:>9.0f}" for jz in JZ_C) + "   classical   GS in Neel sector   sector gap/Jz")
for lab, nm, t in TILTS:
    row, inn, sg = [], [], []
    for jz in JZ_C:
        r = solve(jz, lab, t)
        g = min(r["dc"], r["sector_gap"]) if r["dc"] > 0 else r["dc"]
        row.append(g / jz)
        inn.append(r["dc"] > 0)
        sg.append(r["sector_gap"] / jz)
    res["C"][nm] = dict(gap_over_Jz=row, in_neel=inn, sector_gap_over_Jz=sg)
    say("   " + f"{nm:16s}" + "".join(f"{x:>9.4f}" for x in row) + f"   {CL[nm]:>9s}   {str(all(inn)):>5s}"
        + "               " + " ".join(f"{x:.3f}" for x in sg) + f"   [{time.time()-t00:.0f} s]")

say("\nD. tilts outside the windows of the proof, Jz = 12 and 48: is the ground state in the Neel sector?")
for lab, nm, t in [("ms", "m_s, -0.035", -0.035), ("ms", "m_s, -0.045", -0.045), ("czz", "C_zz, +0.07", 0.07),
                   ("c2", "C_2, -0.035", -0.035)]:
    out = []
    for jz in (12.0, 48.0):
        r = solve(jz, lab, t)
        out.append((jz, r["dc"] > 0, r["dc"] / jz, r["arg_other_M"]))
    res["D"][nm] = out
    say("   " + f"{nm:14s}" + "; ".join(f"Jz = {jz:.0f}: in Neel sector {ok}, (other - Neel)/Jz = {d:+.4f} (M' = {m})"
                                        for jz, ok, d, m in out))

say("\nE. Jz = 6, no tilt: connected correlations in the Neel-sector ground state")
r = solve(6.0, "none", 0.0, want_vec=True)
v = r["vec"]
z = secs[NUP_NEEL]["z"]
p = v * v
mz = z.T @ p
corr = (z * p[:, None]).T @ z - np.outer(mz, mz)
rowsum = np.abs(corr).sum(axis=1)
i = int(np.argmax(rowsum))
res["E"] = dict(sector_gap=r["sector_gap"], global_gap=min(r["dc"], r["sector_gap"]), C1_incl=float(rowsum.max()),
                C1_excl=float((rowsum - np.abs(np.diag(corr))).max()), ms=float(mz @ eta / n))
say(f"   sector gap {r['sector_gap']:.4f}, other-sector gap {r['dc']:.4f}; m_s = {mz @ eta / n:.4f}; "
    f"max_i sum_j |<Z_i;Z_j>| = {rowsum.max():.4f} (j = i included; site {i}), "
    f"{(rowsum - np.abs(np.diag(corr))).max():.4f} without it")
r2 = solve(6.0, "czz", 0.01)
say(f"   Jz = 6, C_zz at +0.01: sector gap {r2['sector_gap']:.4f}, other-sector gap {r2['dc']:.4f}")
res["E"]["czz_p01"] = dict(sector_gap=r2["sector_gap"], dc=r2["dc"])

say(f"\ntotal time {time.time()-t00:.0f} s")
with open(OUT + ".txt", "w") as f:
    f.write("\n".join(lines) + "\n")
with open(OUT + ".json", "w") as f:
    json.dump(res, f, indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
