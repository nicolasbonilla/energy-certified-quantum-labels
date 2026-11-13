"""Reviewer math-learning (R10): OWN implementation of the heavy-hex learning numbers.

Reads only raw stored JSON (emulated labels, DMRG references, map thresholds, chains, checks, states).
Imports NOTHING from the project's code (no ml2.py, no analyze_map.py, no hull.py).
"""
import glob
import json
import math
import os

import numpy as np

ROOT = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work"
FR = ROOT + "/phase3/full_runs"
EMU = FR + "/method/out_20261030T003230Z/out"
MAP = FR + "/map/laptop_analysis"
ALPHA = 0.1
TAU_REL = 0.06
OOD = [1.1, 1.2, 1.3, 1.4]
TRAIN_MIN = 1.6
DELTA = 1e-6          # the map's energy margin for explicit states (analyze_map.DELTA)


def rj(p):
    with open(p) as f:
        return json.load(f)


def jname(J):
    return "%.1f" % float(J)


# ----------------------------------------------------------------------------------------------------- data
def load_labels(n):
    """Emulated primary labels, the second ('ideal') state, energies, DMRG truth. Keys: Jz rounded to 0.1."""
    d = {57: 5, 115: 7}[n]
    G = rj(FR + "/method/code/graphs/hh_d%d.json" % d)
    eta = np.array(G["eta"], float)
    D = {}
    for p in sorted(glob.glob(EMU + "/emu/emu_n%d_J*.json" % n)):
        e = rj(p)
        J = round(e["Jz"], 1)
        r = rj(EMU + "/ref/ref_n%d_J%s.json" % (n, jname(J)))
        v = e["var"]
        D[J] = dict(
            Zl=np.array(v["primary"]["labels"]["Z"], float),
            Zi=np.array(v["ideal"]["labels"]["Z"], float) if "ideal" in v else None,
            Zr=np.array(r["labels"]["Z"], float),
            E_lab=float(v["primary"]["E"]), E0_emu=float(e["E0"]), E0_ref=float(r["E0"]),
            primary_alias=e.get("primary_alias"))
        D[J]["eps"] = D[J]["E_lab"] - D[J]["E0_emu"]
    return eta, D


def ms(Z, eta):
    return float(np.dot(Z, eta) / len(eta))


# ----------------------------------------------------------------------------------------------------- cubic
def design(J, deg=3):
    u = 1.0 / np.asarray(J, float)
    return np.stack([u ** k for k in range(deg, -1, -1)], axis=1)      # columns u^3, u^2, u, 1


def coef_vec(Jtr, Jq, deg=3, ridge=1e-8):
    """a(Jq): prediction = a @ labels.  Own route: augmented least squares solved by QR (lstsq), not the normal
    equations.  ridge = 0 gives the plain least-squares cubic."""
    X = design(Jtr, deg)
    v = design([Jq], deg)[0]
    if ridge > 0:
        A = np.vstack([X, math.sqrt(ridge) * np.eye(deg + 1)])
        # W = argmin |A W - [Y; 0]|^2  ->  W = pinv(A)[:, :N] Y
        P = np.linalg.pinv(A)[:, :len(Jtr)]
    else:
        P = np.linalg.pinv(X)
    return v @ P


def predict(Jtr, Y, Jq, deg=3, ridge=1e-8):
    """Y: (N, sites) array or (N,) vector of labels at Jtr."""
    return coef_vec(Jtr, Jq, deg, ridge) @ np.asarray(Y)


def conf_q(scores, alpha=ALPHA):
    """Split-conformal quantile: the ceil((1-alpha)(N+1))-th smallest score; the largest if that index exceeds N
    (then the attainable level is N/(N+1))."""
    s = np.sort(np.ravel(np.asarray(scores, float)))
    N = len(s)
    k = int(math.ceil((1 - alpha) * (N + 1) - 1e-12))
    if k > N:
        return float(s[-1]), N / (N + 1.0), N, N
    return float(s[k - 1]), k / (N + 1.0), k, N


# ----------------------------------------------------------------------------------------------------- windows
class Windows:
    """Energy window of m_s at (n, Jz) from the stored map files: outer (chain bound) and inner (explicit states)."""

    def __init__(self, n):
        self.n = n
        d = {19: 3, 57: 5, 115: 7}[n]
        self.sz = rj(MAP + "/code/graphs/hh_d%d.json" % d)["sz"]
        self.states = {}
        for p in glob.glob(MAP + "/out/states/n%d_J*.json" % n):
            r = rj(p)
            if r["n"] != n:
                continue
            self.states.setdefault(round(r["Jz"], 1), []).append(r)

    def has_row(self, J):
        return os.path.exists(MAP + "/out/thr/thr_n%d_J%s.json" % (self.n, jname(J))) and \
            os.path.exists(MAP + "/out/chains/chain_n%d_J%s_m_s_+.json" % (self.n, jname(J)))

    def thr(self, J):
        return rj(MAP + "/out/thr/thr_n%d_J%s.json" % (self.n, jname(J)))

    def pool(self, J):
        pts = []
        for r in self.states.get(round(J, 1), []):
            if not r.get("in_sector"):
                continue
            if abs(r["sector_s"] - self.sz) > 1e-9:
                continue
            if r["indep"]["sector_var"] >= 1e-12:
                continue
            o = r["indep"].get("m_s")
            if o is None:
                continue
            pts.append((float(r["tenpy"]["E"]), float(o)))
        return np.array(pts)

    def inner(self, J, E):
        """Hull of the stored in-sector states with energy <= E - DELTA and of two-state mixtures of energy exactly
        E - DELTA (one state below, one above).  Returns (lo, hi) or (None, None)."""
        P = self.pool(J)
        e = E - DELTA
        below = P[P[:, 0] <= e]
        above = P[P[:, 0] > e]
        if len(below) == 0:
            return None, None
        hi, lo = below[:, 1].max(), below[:, 1].min()
        for (Ea, oa) in below:
            for (Eb, ob) in above:
                t = (e - Ea) / (Eb - Ea)
                val = (1 - t) * oa + t * ob
                hi, lo = max(hi, val), min(lo, val)
        return float(lo), float(hi)

    def outer(self, J, E):
        """Chain bound: sigma <O> <= min over chain points of (E - F + dG)/(lam S), capped at 1."""
        th = self.thr(J)
        res = {}
        for s, sign in (("+", 1.0), ("-", -1.0)):
            ch = rj(MAP + "/out/chains/chain_n%d_J%s_m_s_%s.json" % (self.n, jname(J), s))
            S = ch["S"]
            pc = MAP + "/out/chk/chk_n%d_J%s_m_s_%s.json" % (self.n, jname(J), s)
            dG = 2.0 * th.get("dchi", 0.0)
            if os.path.exists(pc):
                dG = max(dG, abs(rj(pc)["dG"]))
            best = min((E - p["F"] + dG) / (p["lam"] * S) for p in ch["points"])
            res[s] = sign * min(best, 1.0)
        return res["-"], res["+"]

    def chain_range(self, J):
        out = {}
        for s in "+-":
            ch = rj(MAP + "/out/chains/chain_n%d_J%s_m_s_%s.json" % (self.n, jname(J), s))
            out[s] = (min(p["eps"] for p in ch["points"]), max(p["eps"] for p in ch["points"]),
                      max(p["lam"] for p in ch["points"]), ch.get("saturated"), ch.get("lam_max"))
        return out
