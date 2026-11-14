"""R10 reviewer math-map-logic: OWN re-implementation of the certification-map analysis.

Reads only the lowest-level stored records of the map run (read in place, never written):
  out/states/*.json   one record per stored MPS (both evaluators, sector weights, DMRG stats)
  out/chains/*.json   only for the LIST of chain points (sid, lam, sign); E, o, F are re-derived from the state records
  out/thr/*.json      only to cross-check; thresholds are re-derived from the states and the declared readings
  code/readings_declared.json, digitization/reading1_*_raw.txt
Nothing is imported from the project's analysis code (analyze_map.py, hull.py, witness.py are NOT used).
"""
import glob
import json
import math
import os
import re

MAP = "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work/phase3/full_runs/map"
OUT = MAP + "/out_20261030T022613Z/out"
TAU_FRAC = 0.06
DELTA = 1e-6          # the project's safety offset below the threshold (kept, so that numbers are comparable)
IKEY = {"m_s": "m_s", "Czz_bar": "Czz_bar", "C2_bar": "C2_bar", "Z_bulk": "Z_bulk", "Z_boundary": "Z_boundary",
        "Czz_edge": "Czz_edge_loc", "Z_loop": "Z_loop"}
SCALE = {57: {"m_s": 57.0, "Czz_bar": 64.0, "C2_bar": 87.0}, 115: {"m_s": 115.0, "Czz_bar": 132.0, "C2_bar": 185.0},
         19: {"m_s": 19.0, "Czz_bar": None, "C2_bar": None}}
SZ = {19: 1.5, 57: 4.5, 115: 9.5}
NUP = {19: 11, 57: 33, 115: 67}


def rj(p):
    with open(p) as f:
        return json.load(f)


_STATES = None


def states():
    """All state records, slimmed to what the analysis needs."""
    global _STATES
    if _STATES is None:
        S = {}
        for p in glob.glob(OUT + "/states/*.json"):
            r = rj(p)
            ind, ten = r["indep"], r["tenpy"]
            S[r["sid"]] = dict(sid=r["sid"], n=r["n"], Jz=r["Jz"], kind=r["kind"], sector_s=r["sector_s"],
                               E_t=ten["E"], E_i=ind.get("E"), ov=ten["overlap"], norm_i=ind["norm"],
                               o={k: ind.get(v) for k, v in IKEY.items()}, m_s_t=ten["m_s"],
                               sector_var=ind.get("sector_var"), weights=ind.get("sector_weights"),
                               charge=ten["total_charge_phys"], in_sector_flag=r.get("in_sector"),
                               chi=r.get("chi"), label=r.get("label"), sign=r.get("sign"), lam=r.get("lam"),
                               dmrg=r.get("dmrg"), agree=r.get("agree"))
        _STATES = S
    return _STATES


def my_in_sector(r):
    """Own sector test: all the weight on the declared number of up spins (from the charge-resolved weights of the
    independent evaluator) and the TeNPy charge equal to 2s."""
    n = r["n"]
    w = r["weights"] or {}
    tot = sum(w.values())
    good = w.get(str(NUP[n]), 0.0)
    return abs(r["sector_s"] - SZ[n]) < 1e-9 and r["charge"] == [int(round(2 * SZ[n]))] and abs(good - tot) < 1e-12 \
        and abs(tot - 1) < 1e-9


def pool(n, J, label, energy="indep"):
    """All stored states of (n, Jz) in the declared sector: list of (E, o, sid). energy: 'indep' or 'tenpy'."""
    pts = []
    for r in states().values():
        if r["n"] != n or abs(r["Jz"] - J) > 1e-9:
            continue
        if not my_in_sector(r):
            continue
        o = r["o"].get(label)
        if o is None:
            continue
        E = r["E_i"] if energy == "indep" else r["E_t"]
        pts.append((E, o, r["sid"]))
    return pts


# ---------------------------------------------------------------------------------------------- own hull
def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


class Hull:
    """Upper and lower envelopes of {(sum p_i E_i, sum p_i o_i)} for probability vectors p, evaluated as
    o_plus(E) = max{ sum p_i o_i : sum p_i E_i <= E } and o_minus(E) likewise with min (monotone chain + running
    extreme). Independent of the project's pair enumeration."""
    def __init__(self, pts):
        P = sorted(set((e, o) for e, o, _ in pts))
        self.P = P
        up = []
        for p in P:
            while len(up) >= 2 and _cross(up[-2], up[-1], p) >= 0:
                up.pop()
            up.append(p)
        lo = []
        for p in P:
            while len(lo) >= 2 and _cross(lo[-2], lo[-1], p) <= 0:
                lo.pop()
            lo.append(p)
        # keep only the part up to the global extreme (afterwards the constraint "<= E" makes it flat)
        kmax = max(range(len(up)), key=lambda k: up[k][1])
        kmin = min(range(len(lo)), key=lambda k: lo[k][1])
        self.up = up[:kmax + 1]
        self.lo = lo[:kmin + 1]
        self.Emin = P[0][0]

    @staticmethod
    def _eval(chain, E):
        if E < chain[0][0]:
            return None
        if E >= chain[-1][0]:
            return chain[-1][1]
        for a, b in zip(chain[:-1], chain[1:]):
            if a[0] <= E <= b[0]:
                t = (E - a[0]) / (b[0] - a[0])
                return (1 - t) * a[1] + t * b[1]
        return chain[-1][1]

    def plus(self, E):
        # points with the same minimal energy: the first vertex of 'up' is the max-o point at Emin or left of it
        return self._eval(self.up, E)

    def minus(self, E):
        return self._eval(self.lo, E)

    def width(self, E):
        a, b = self.plus(E), self.minus(E)
        return None if a is None else a - b


def hull_lp(pts, E):
    """Independent check of Hull by linear programming (scipy HiGHS)."""
    import numpy as np
    from scipy.optimize import linprog
    Es = np.array([p[0] for p in pts]); os_ = np.array([p[1] for p in pts])
    e0 = Es.min()
    res = []
    for sgn in (+1, -1):
        r = linprog(-sgn * os_, A_ub=[Es - e0], b_ub=[E - e0], A_eq=[np.ones(len(pts))], b_eq=[1.0],
                    bounds=(0, None), method="highs")
        res.append(sgn * (-r.fun) if r.status == 0 else None)
    return res[1], res[0]          # (minus, plus)


# ---------------------------------------------------------------------------------------------- thresholds
_RD = None


def readings():
    global _RD
    if _RD is None:
        _RD = rj(MAP + "/code/readings_declared.json")
    return _RD


def st(n, J, tag):
    return states().get("n%d_J%.1f_%s" % (n, J, tag))


def thresholds(n, J):
    """Re-derived from the reference states and the declared readings (DECLARATION Sec. 2)."""
    S = states()
    gs = st(n, J, "R1_chi320")
    if gs is None:
        return None
    E0 = gs["E_t"]
    g160 = st(n, J, "R1_chi160")
    dchi = abs(g160["E_t"] - E0)
    gaps = {}
    for tag, key in (("R2_E1", "in_sector"), ("R3_sz_minus", "sz_minus"), ("R4_sz_plus", "sz_plus")):
        r = st(n, J, tag)
        if r is not None:
            gaps[key] = r["E_t"] - E0
    ours = min(gaps.values())
    RD = readings()
    key = "%d_%.1f" % (n, J)
    out = dict(n=n, Jz=J, E0=E0, E0_indep=gs["E_i"], dchi=dchi, gaps=gaps, gap_ours=ours, gap1=RD["gap1"].get(key),
               gap2=RD["gap2"].get(key))
    if J >= 1.55:
        r1, g1 = RD["r1"][key], RD["gap1"][key]
        out.update(ood=False, r1=r1, eps_dig=r1 * g1, eps_lo=0.8 * r1 * min(ours, g1),
                   eps_up=1.2 * r1 * max(ours, g1) + dchi)
        r2, g2 = RD["r2"].get(key), RD["gap2"].get(key)
        if r2 and g2:
            out.update(r2=r2, eps_dig2=r2 * g2, eps_lo2=0.8 * r2 * min(ours, g2), eps_up2=1.2 * r2 * max(ours, g2) + dchi)
    else:
        ed = 0.012 * n
        out.update(ood=True, r1=None, eps_dig=ed, eps_lo=0.8 * ed, eps_up=1.2 * ed + dchi)
    return out


# ---------------------------------------------------------------------------------------------- chains and outer
def chain_points(n, J, label, sg):
    """Chain points re-derived from the state records: (lam, E, o, G=E - sigma lam S o, sid). The chain file is used
    only for the list of sids."""
    p = OUT + "/chains/chain_n%d_J%.1f_%s_%s.json" % (n, J, label, sg)
    if not os.path.exists(p):
        return None
    ch = rj(p)
    S = states()
    sgn = 1 if sg == "+" else -1
    scale = ch["S"]
    out = []
    for q in ch["points"]:
        r = S[q["sid"]]
        E, o = r["E_t"], r["o"][label]
        assert abs(r["lam"] - q["lam"]) < 1e-12 and r["label"] == label and r["sign"] == sg
        G = E - sgn * q["lam"] * scale * o
        out.append(dict(lam=q["lam"], E=E, o=o, G=G, sid=q["sid"], G_file=q["F"], G_dmrg=q.get("F_dmrg"),
                        in_sector=my_in_sector(r), sweeps=q.get("sweeps")))
    return dict(S=scale, pts=out)


def delta_G(n, J, label, sg, dchi):
    """dG = max(2 dchi, |G160 - G320| where the chi = 320 check exists), re-derived from the chk320 state."""
    r = st(n, J, "chk320_%s_%s" % (label, "p" if sg == "+" else "m"))
    meas = None
    if r is not None:
        ch = chain_points(n, J, label, sg)
        sgn = 1 if sg == "+" else -1
        G320 = r["E_t"] - sgn * r["lam"] * ch["S"] * r["o"][label]
        q = min(ch["pts"], key=lambda q: abs(q["lam"] - r["lam"]))
        assert abs(q["lam"] - r["lam"]) < 1e-12
        meas = q["G"] - G320
    return max(2 * dchi, abs(meas) if meas is not None else 0.0), meas


def outer_bounds(chains, dG, E):
    """(lower, upper) outer bounds of <O> at energy threshold E from weak duality, capped at +-1."""
    res = {}
    for sg, sgn in (("+", 1), ("-", -1)):
        b = min((E - q["G"] + dG[sg]) / (q["lam"] * chains[sg]["S"]) for q in chains[sg]["pts"])
        res[sg] = sgn * min(b, 1.0)
    return res["-"], res["+"]


def decisive(chains, dG, E, sg):
    return min(chains[sg]["pts"], key=lambda q: (E - q["G"] + dG[sg]) / (q["lam"] * chains[sg]["S"]))


def bisect_smallest(f, target, lo, hi, it=200):
    """Smallest x in [lo, hi] with f(x) >= target for nondecreasing f (geometric bisection)."""
    if f(hi) < target:
        return None
    if f(lo) >= target:
        return lo
    for _ in range(it):
        m = math.sqrt(lo * hi)
        if f(m) >= target:
            hi = m
        else:
            lo = m
        if hi / lo - 1 < 1e-13:
            break
    return hi


class Row:
    def __init__(self, n, J, label, energy="tenpy", tau_frac=TAU_FRAC, o_gs_scale=1.0, dE0=0.0, extra_dG=0.0,
                 pool_filter=None):
        """dE0: hypothetical amount by which the true E0 lies BELOW the chi = 320 value (>= 0).
        o_gs_scale: hypothetical factor on |o_GS| in tau. extra_dG: added to the declared dG (outer side)."""
        self.n, self.J, self.label = n, J, label
        self.thr = thresholds(n, J)
        self.E0 = self.thr["E0"] - dE0
        gs = st(n, J, "R1_chi320")
        self.oGS = gs["o"][label]
        self.tau = tau_frac * abs(self.oGS) * o_gs_scale
        pts = pool(n, J, label, energy)
        if pool_filter:
            pts = [p for p in pts if pool_filter(states()[p[2]])]
        self.pts = pts
        self.hull = Hull(pts)
        self.ch = {sg: chain_points(n, J, label, sg) for sg in "+-"}
        self.ok = all(self.ch[sg] for sg in "+-")
        if self.ok:
            self.dG, self.dGmeas = {}, {}
            for sg in "+-":
                d, meas = delta_G(n, J, label, sg, self.thr["dchi"])
                self.dG[sg], self.dGmeas[sg] = d + extra_dG, meas
            self.S = self.ch["+"]["S"]
            self.emax = max([q["E"] - self.thr["E0"] for sg in "+-" for q in self.ch[sg]["pts"]] + [self.thr["eps_up"]])

    # eps is measured from self.E0 (the possibly shifted ground energy)
    def w_in(self, eps):
        w = self.hull.width(self.E0 + eps - DELTA)
        return 0.0 if w is None else w

    def inner(self, eps):
        E = self.E0 + eps - DELTA
        return self.hull.minus(E), self.hull.plus(E)

    def w_out(self, eps):
        lo, up = outer_bounds(self.ch, self.dG, self.E0 + eps)
        return up - lo

    def outer(self, eps):
        return outer_bounds(self.ch, self.dG, self.E0 + eps)

    def pure(self, eps):
        E = self.E0 + eps - DELTA
        c = [p for p in self.pts if p[0] <= E]
        if not c:
            return None, None, None, None
        a = max(c, key=lambda p: p[1]); b = min(c, key=lambda p: p[1])
        return b[1], a[1], b[2], a[2]

    def eps_tau_in(self):
        return bisect_smallest(self.w_in, self.tau, 1e-7, self.emax + (self.thr["E0"] - self.E0))

    def eps_tau_out(self):
        return bisect_smallest(self.w_out, self.tau, 1e-7, self.emax + (self.thr["E0"] - self.E0))

    def chi_lin(self):
        p = min(self.ch["+"]["pts"], key=lambda q: q["lam"]); m = min(self.ch["-"]["pts"], key=lambda q: q["lam"])
        if abs(p["lam"] - m["lam"]) > 1e-12:
            return None
        return (p["o"] - m["o"]) / (2 * p["lam"])


def lab_list():
    out = []
    for p in sorted(glob.glob(OUT + "/labs/lab_n*_J*_*.json")):
        m = re.match(r"lab_n(\d+)_J([0-9.]+)_(.+)\.json", os.path.basename(p))
        out.append((int(m.group(1)), float(m.group(2)), m.group(3)))
    return out
