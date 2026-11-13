"""Data for the 3-D figures (certification landscape, lattice portrait): read from the deposited outputs only.

Nothing is recomputed physically: the window edges are the inner hull of the stored sector states (the rule of
phase3/full_runs/map/laptop_analysis/code/analyze_map.py + hull.py, re-implemented here and checked against
summary_map.json at the three stored window energies of every m_s row), and per-site values are read from the stored
states and emulation outputs.

Sources (read-only):
  phase3/full_runs/map/laptop_analysis/out/states/*.json   stored states: energy (tenpy.E), m_s and per-site <Z_i>
                                                           (indep.m_s, indep.Z_graph), sector checks
  phase3/full_runs/map/laptop_analysis/out/thr/*.json      E0 and window energies per (n, Jz)
  phase3/full_runs/map/laptop_analysis/summary_map.json    rows (tau, o_GS, eps, eps_tau_out, status, witness comps)
  phase3/full_runs/map/laptop_analysis/code/graphs/        heavy-hex graphs (edges, colouring); identical copies are
                                                           in phase3/pilot_witness/code/graphs/
  phase3/full_runs/method/laptop_post/out/                 emu/, ref/ (emulated and reference labels), summary.json
"""
import glob
import json
import os

import numpy as np

import common as C

OUT = os.path.join(C.MAP, "laptop_analysis", "out")
GRAPHS = os.path.join(C.MAP, "laptop_analysis", "code", "graphs")
GRAPHS_PILOT = os.path.join(C.ROOT, "phase3", "pilot_witness", "code", "graphs")
D_OF_N = {57: 5, 115: 7}
DELTA = 1e-6                                   # analyze_map.DELTA (energy margin of the inner hull)

_STATES = None


def graph(n):
    g = C.rj(os.path.join(GRAPHS, "hh_d%d.json" % D_OF_N[n]))
    gp = C.rj(os.path.join(GRAPHS_PILOT, "hh_d%d.json" % D_OF_N[n]))
    assert g["edges"] == gp["edges"] and g["eta"] == gp["eta"], "graph copies differ"
    return g


def states():
    global _STATES
    if _STATES is None:
        _STATES = {}
        for p in glob.glob(os.path.join(OUT, "states", "*.json")):
            r = C.rj(p)
            _STATES[r["sid"]] = r
    return _STATES


def thr(n, J):
    return C.rj(os.path.join(OUT, "thr", "thr_n%d_J%.1f.json" % (n, J)))


def pool(n, J):
    """stored in-sector states of (n, Jz), as in analyze_map.Data.pool: arrays (E, m_s)"""
    sz = graph(n)["sz"]
    E, o = [], []
    for r in states().values():
        if r["n"] != n or abs(r["Jz"] - J) > 1e-9 or not r.get("in_sector"):
            continue
        if abs(r["sector_s"] - sz) > 1e-9 or r["indep"]["sector_var"] >= 1e-12:
            continue
        E.append(r["tenpy"]["E"])
        o.append(r["indep"]["m_s"])
    return np.array(E), np.array(o)


def inner(E, o, Eq):
    """inner window [o-, o+] at energies Eq: pure states below E and two-state mixtures straddling E
    (analyze_map.make_limit.inner_fast, vectorised over Eq)."""
    lo, hi = np.full(len(Eq), np.nan), np.full(len(Eq), np.nan)
    for k, e in enumerate(np.asarray(Eq) - DELTA):
        a = E <= e
        if not a.any():
            continue
        h, l_ = o[a].max(), o[a].min()
        b = ~a
        if b.any():
            ea, eb = E[a][:, None], E[b][None, :]
            t = (e - ea) / (eb - ea)
            val = (1 - t) * o[a][:, None] + t * o[b][None, :]
            h, l_ = max(h, val.max()), min(l_, val.min())
        lo[k], hi[k] = l_, h
    return lo, hi


def rows(n, label="m_s"):
    S = C.map_summary()
    return sorted((r for r in S["rows"] if r["n"] == n and r["label"] == label), key=lambda r: r["Jz"])


def check_inner(n):
    """max |difference| between this inner hull and summary_map.json at E_lo, E_dig, E_up of every m_s row"""
    worst = 0.0
    for r in rows(n):
        E, o = pool(n, r["Jz"])
        E0 = thr(n, r["Jz"])["E0"]
        for key, ek in (("at_lo", "lo"), ("at_dig", "dig"), ("at_up", "up")):
            lo, hi = inner(E, o, [E0 + r["eps"][ek]])
            worst = max(worst, abs(lo[0] - r[key]["inner"][0]), abs(hi[0] - r[key]["inner"][1]))
    return worst


def landscape(n, Js, de):
    """upper/lower edges of the m_s window relative to the ground-state value on the grid Js x de (error per site),
    and the validity mask (de at most the largest stored energy of that Jz)"""
    up = np.full((len(Js), len(de)), np.nan)
    lo = np.full((len(Js), len(de)), np.nan)
    ok = np.zeros((len(Js), len(de)), bool)
    for i, J in enumerate(Js):
        E, o = pool(n, J)
        t = thr(n, J)
        E0, oG = t["E0"], t["m_s_GS"]
        l_, h = inner(E, o, E0 + n * de)
        up[i], lo[i] = h - oG, l_ - oG
        ok[i] = n * de <= (E.max() - E0)
    return up, lo, ok


def emu_states(n, var="primary"):
    """emulated method-class states at their own energy: (Jz, error per site, m_s - m_s_ref)"""
    out = []
    for (nn, J), r in sorted(C.meth_emu().items()):
        if nn == n:
            v = r["var"][var]
            out.append((J, v["dE_site"], v["err"]["dm_s"]))
    return out


def dz_matched(n):
    """bias estimate at the dataset's energy from its published unsigned Delta Z (summary.json dZ_matched)"""
    M = C.meth_summary()["dZ_matched"]
    return sorted((v["Jz"], v["dm_s"]) for v in M.values() if v["n"] == n)


def at_reported_energy(n):
    """bias read at the dataset's reported energy ratio (summary.json bias_at_ibm_energy)"""
    M = C.meth_summary()["bias_at_ibm_energy"]
    return sorted((v["Jz"], v["dm_s"], v["status"]) for v in M.values() if v["n"] == n)


# ----------------------------------------------------------------------------------------------- lattice geometry
def layout(n):
    """planar coordinates of the heavy-hex graph rustworkx.generators.heavy_hex_graph(d) (the dataset's graphs):
    d x d data qubits on rows (indices 0..d^2-1), flag qubits between neighbours of a row (next d(d-1) indices after
    the syndrome qubits), syndrome qubits between rows placed at the mean of their neighbours.  Every edge then has
    unit length (checked), i.e. this is the usual heavy-hex drawing of the coupling map, not a force layout."""
    g = graph(n)
    d = g["d"]
    nd, ns = d * d, (d - 1) * (d + 1) // 2
    pos = np.full((n, 2), np.nan)
    for i in range(nd):
        r, c = divmod(i, d)
        pos[i] = (2 * c, -2 * r)
    for k in range(d * (d - 1)):
        r, c = divmod(k, d - 1)
        pos[nd + ns + k] = (2 * c + 1, -2 * r)
    nb = {i: [] for i in range(n)}
    for a, b in g["edges"]:
        nb[a].append(b)
        nb[b].append(a)
    for i in range(nd, nd + ns):
        pos[i] = pos[nb[i]].mean(axis=0)
    L = np.array([np.linalg.norm(pos[a] - pos[b]) for a, b in g["edges"]])
    assert np.allclose(L, 1.0), ("heavy-hex layout: edge lengths", L.min(), L.max())
    return pos, np.array(g["edges"])


# ----------------------------------------------------------------------------------------------- per-site values
def site_overorder(n, J, var="primary"):
    """eta_i (<Z_i>_emu - <Z_i>_ref): signed per-site excess of order of the emulated method class (graph order)"""
    e = C.meth_emu()[(n, J)]
    ref = C.meth_ref()[(n, J)]
    eta = np.array(graph(n)["eta"], float)
    return eta * (np.array(e["var"][var]["labels"]["Z"]) - np.array(ref["labels"]["Z"]))


def site_freedom(n, J, at="at_lo"):
    """eta_i (<Z_i>(phi+) - <Z_i>(phi-)) for the two m_s witnesses of the window at E_lo (stored mixtures of stored
    states, weights from summary_map.json rows[*].at_lo.comps); also returns the m_s of both and the width."""
    r = [x for x in rows(n) if abs(x["Jz"] - J) < 1e-9][0]
    S = states()
    eta = np.array(graph(n)["eta"], float)
    Z, ms = [], []
    for comps in r[at]["comps"]:                    # [lower side, upper side]
        z = sum(w * np.array(S[sid]["indep"]["Z_graph"]) for sid, w, _, _ in comps)
        Z.append(z)
        ms.append(sum(w * S[sid]["indep"]["m_s"] for sid, w, _, _ in comps))
    d = eta * (Z[1] - Z[0])
    assert abs(d.mean() - (ms[1] - ms[0])) < 1e-9, "per-site freedom does not average to the m_s width"
    return d, ms, r[at]["inner"]


if __name__ == "__main__":
    for n in (57, 115):
        print("n=%d: inner hull vs summary_map.json, max |diff| = %.2e" % (n, check_inner(n)))
    d, ms, inn = site_freedom(57, 1.2)
    print("n=57 Jz=1.2 witnesses m_s", ms, "summary inner", inn, "mean freedom", d.mean(), "min", d.min())
    a = site_overorder(57, 1.2)
    print("n=57 Jz=1.2 over-ordering: mean %.4f min %.4f max %.4f" % (a.mean(), a.min(), a.max()))
