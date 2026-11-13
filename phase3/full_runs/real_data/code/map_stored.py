# real_data / map_stored.py  (own code; 2026-11-12; task rd-code-map)
#
# The stored objects of the certification map, read through the stored code (imported, never changed):
#   map/laptop_analysis/code/analyze_map.py : Data, make_limit (outer(E), inner(E)), eps_tau;   hull.py : width.
# On top of them, DECLARATION.md Sec. 2:
#   - the linear re-evaluation of a stored state's energy at another coupling (Sec. 0):
#         E_phi(J) = E_phi(J_g) + (J - J_g) (1/4) sum_e <Z_i Z_j>_phi ;
#   - the pool of in-sector states of a row: the states of that (n, Jz) where a chain of the row's label is stored
#     ("as in the map"), otherwise the states of the two grid couplings that bracket it, re-evaluated;
#   - the reference state of the neighbouring sector (R3: S^z = s - 1; R4: S^z = s + 1, n = 57 only);
#   - the NOT CERTIFIED side: q = (M_0 - M_real)/2, E* = (E_real - q E_r(J))/(1 - q), (1 - q) w_in(E*) >= tau;
#   - the like-for-like statuses (sector hypothesis): outer and inner of the stored map at E_real where a chain is
#     stored, log-linearly interpolated thresholds elsewhere ("interpolated, not a bound").
# Floating point, as in the stored map (the exact side is map_certs.py). numpy only inside the stored code and in the
# fast hull used by the threshold bisection (checked against hull.py).
import math
import os
import sys

import map_common as C

if C.MAP_CODE not in sys.path:
    sys.path.append(C.MAP_CODE)
import analyze_map as AM          # noqa: E402  (stored code; it puts its own folder first in sys.path)
import hull                       # noqa: E402  (stored code)
import witness as W               # noqa: E402  (stored code: constants only)

# keep the stored code importable but LAST in the search path (it holds files named like standard modules)
_norm = lambda p: os.path.normcase(os.path.abspath(p))
sys.path[:] = [p for p in sys.path if _norm(p) != _norm(C.MAP_CODE)] + [C.MAP_CODE]

DELTA = AM.DELTA                   # 1e-6: a pool state counts at energy E only if its energy is <= E - DELTA
REF_TAG = {"R3": ("R3_sz_minus", -2), "R4": ("R4_sz_plus", +2)}


def hull_width_fast(Ea, oa, e):
    """Same value as hull.width(pts, e)[0] (pure points and straddling two-point mixtures), vectorised."""
    import numpy as np
    a = Ea <= e
    if not a.any():
        return None
    b = ~a
    hi, lo = oa[a].max(), oa[a].min()
    if b.any():
        ea, eb = Ea[a][:, None], Ea[b][None, :]
        t = (e - ea) / (eb - ea)
        val = (1 - t) * oa[a][:, None] + t * oa[b][None, :]
        hi, lo = max(hi, val.max()), min(lo, val.min())
    return float(hi - lo)


class Stored:
    def __init__(self, mapdir=None):
        self.mapdir = mapdir or C.MAPDIR
        self.D = AM.Data(self.mapdir)
        self.SM = C.rj(os.path.join(self.mapdir, "summary_map.json"))
        self.rows = {(r["n"], C.jkey(r["Jz"]), r["label"]): r for r in self.SM["rows"]}
        self.refs = {(t["n"], C.jkey(t["Jz"])): t for t in self.SM["refs"].values()}
        self.GRID = tuple(C.jfr(x) for x in W.GRID)        # the 16 grid couplings of map/DECLARATION.md Sec. 3
        self._lim, self._slope, self._pool = {}, {}, {}

    # ---------------------------------------------------------------------------------------- truth (Sec. 0)
    def E0(self, n, J):
        t = self.refs.get((n, C.jkey(J)))
        return None if t is None else float(t["E0"])

    def O_GS(self, n, J, label):
        """This project's bond-dimension-320 reference of a label where summary_map.json stores it: the rows of the
        stored map (the same reading as rd_common.project_refs of the learning code). None elsewhere."""
        r = self.rows.get((n, C.jkey(J), label))
        return None if r is None else float(r["O_GS"])

    def O_GS_record(self, n, J, label):
        """The same quantity from the stored ground-state record (all seven labels at the 18 + 16 couplings); equal to
        O_GS wherever a row exists. Not used for the truth; kept for checks."""
        gs = self.D.st(n, float(J), "R1_chi320") if (n, C.jkey(J)) in self.refs else None
        return None if gs is None else gs["indep"].get(AM.KEY[label])

    # ---------------------------------------------------------------------------------------- stored chains
    def has_chain(self, n, J, label):
        return (n, C.jkey(J), label) in self.rows

    def limit(self, n, J, label):
        k = (n, C.jkey(J), label)
        if k not in self._lim:
            self._lim[k] = AM.make_limit(self.D, n, float(J), label, self.D.thr(n, float(J)))
        return self._lim[k]

    def chain_couplings(self, n, label):
        return sorted(C.jfr(k) for (nn, k, lab) in self.rows if nn == n and lab == label)

    # ---------------------------------------------------------------------------------------- pools
    def slope(self, sid):
        """dE/dJz of a stored state: (1/4) sum over the edges of its stored <Z_i Z_j> (Sec. 0)."""
        if sid not in self._slope:
            self._slope[sid] = 0.25 * math.fsum(self.D.states[sid]["indep"]["Czz_edges"])
        return self._slope[sid]

    def bracket(self, J):
        """The two grid couplings that bracket J (both equal J when J is a grid coupling)."""
        J = C.jfr(J)
        return max(g for g in self.GRID if g <= J), min(g for g in self.GRID if g >= J)

    def own_pool(self, n, Jg, label):
        k = (n, C.jkey(Jg), label)
        if k not in self._pool:
            self._pool[k] = self.D.pool(n, float(Jg), label)
        return self._pool[k]

    def reeval(self, n, Jg, label, J):
        """The stored in-sector states of (n, Jg), with their energies re-evaluated at J by the linear rule."""
        out = []
        for p in self.own_pool(n, Jg, label):
            sl = self.slope(p["sid"])
            out.append(dict(sid=p["sid"], E=p["E"] + (float(J) - float(Jg)) * sl, o=p["o"], E_own=p["E"],
                            Jg=float(Jg), slope=sl))
        return out

    def pool(self, n, J, label):
        """Sec. 2: (points, description). Points are dicts {sid, E, o} as hull.py wants them."""
        J = C.jfr(J)
        if self.has_chain(n, J, label):
            return self.limit(n, J, label)["pts"], dict(kind="stored chain", couplings=[float(J)])
        a, b = self.bracket(J)
        pts = self.reeval(n, a, label, J) + (self.reeval(n, b, label, J) if b != a else [])
        return pts, dict(kind="re-evaluated" if a != b else "stored states, no chain of this label",
                         couplings=sorted({float(a), float(b)}))

    def ref_state(self, n, J, which):
        """R3 or R4 of a grid coupling that brackets J, energy re-evaluated at J; of the two the lower one."""
        tag, dM = REF_TAG[which]
        M0 = C.graph(n)["M0"]
        cands = []
        for g in sorted(set(self.bracket(J))):
            r = self.D.st(n, float(g), tag)
            if r is None:
                continue
            if abs(r["indep"]["sum_Z"] - (M0 + dM)) > 1e-8 or r["indep"].get("sector_var", 1.0) >= 1e-12:
                continue
            sl = self.slope(r["sid"])
            cands.append(dict(sid=r["sid"], which=which, Jg=float(g), E_own=r["tenpy"]["E"], slope=sl,
                              E=r["tenpy"]["E"] + (float(J) - float(g)) * sl,
                              labels={lab: r["indep"].get(AM.KEY[lab]) for lab in C.LABELS}))
        return min(cands, key=lambda c: c["E"]) if cands else None

    # ---------------------------------------------------------------------------------------- NOT CERTIFIED side
    def not_certified(self, n, J, label, E_real, M_real, tau):
        """Sec. 2, explicit states. Returns a dict; 'not_certified' is True iff (1 - q) w_in(E*) >= tau."""
        M0 = C.graph(n)["M0"]
        q = (M0 - float(M_real)) / 2.0
        res = dict(q=q, not_certified=False, reason=None, weight=abs(q), ref=None)
        r = None
        if q != 0.0:
            r = self.ref_state(n, J, "R3" if q > 0 else "R4")
            if r is None:
                res["reason"] = "no stored %s state (GRAY by rule)" % ("R3" if q > 0 else "R4")
                return res
        w = abs(q)
        if not w < 1.0:
            res["reason"] = "|q| >= 1"
            return res
        Estar = (E_real - w * r["E"]) / (1.0 - w) if r is not None else E_real
        pts, info = self.pool(n, J, label)
        res.update(ref=None if r is None else dict(sid=r["sid"], which=r["which"], Jg=r["Jg"], E_at_J=r["E"]),
                   Estar=Estar, pool=info, pool_size=len(pts), min_pool_E=min(p["E"] for p in pts) if pts else None)
        Wd, up, lo, cu, cl = hull.width(pts, Estar - DELTA)
        if Wd is None:
            res["reason"] = "no pool state at or below E* - 1e-6"
            return res
        o_r = r["labels"][label] if r is not None else 0.0
        res.update(w_in=Wd, w_lower=(1.0 - w) * Wd, hull=[lo, up], comps_min=cl, comps_max=cu,
                   witness=[(1.0 - w) * lo + w * o_r, (1.0 - w) * up + w * o_r],
                   not_certified=bool((1.0 - w) * Wd >= tau))
        return res

    def eps_tau_in_pool(self, n, J, label, E0, tau):
        """Smallest eps with w_in(E0 + eps) >= tau over the Sec. 2 pool with q = 0 (Sec. 4, Jz = 1.5); the stored
        bisection AM.eps_tau on a fast hull, then checked against hull.py at the result."""
        import numpy as np
        pts, info = self.pool(n, J, label)
        if not pts:
            return None, info
        Ea, oa = np.array([p["E"] for p in pts]), np.array([p["o"] for p in pts])

        def w(e):
            v = hull_width_fast(Ea, oa, E0 + e - DELTA)
            return v if v is not None else 0.0
        emax = float(Ea.max()) - E0 + 2 * DELTA
        et = AM.eps_tau(w, tau, 1e-7, emax) if emax > 1e-7 else None
        if et is not None:
            ref = hull.width(pts, E0 + et - DELTA)[0]
            assert ref is not None and abs(ref - w(et)) <= 1e-10, "fast hull differs from hull.py"
        return et, info

    # ---------------------------------------------------------------------------------------- like-for-like
    def interp(self, n, label, J, key):
        """The stored J* rule: log-linear in Jz between computed grid points of that label and size."""
        pts = sorted(((r["Jz"], k) for k, r in self.rows.items() if k[0] == n and k[2] == label))
        Jf = float(J)
        for (J0, k0), (J1, k1) in zip(pts[:-1], pts[1:]):
            if J0 - 1e-9 <= Jf <= J1 + 1e-9:
                a, b = self.rows[k0].get(key), self.rows[k1].get(key)
                if not a or not b:
                    return None
                t = (Jf - J0) / (J1 - J0)
                return math.exp((1 - t) * math.log(a) + t * math.log(b))
        return None

    def like_for_like(self, n, J, label, E, E0, tau, E_inner=None):
        """Statuses under the paper's sector hypothesis. E: energy for the outer side (and for the inner side unless
        E_inner is given; the unit test against the stored map passes E_up and E_lo)."""
        Ei = E if E_inner is None else E_inner
        eps, eps_i = E - E0, Ei - E0
        if self.has_chain(n, J, label):
            L, row = self.limit(n, J, label), self.rows[(n, C.jkey(J), label)]
            olo, oup = L["outer"](E)
            lo, up, cl, cu = L["inner"](Ei)
            w_out, w_in = oup - olo, ((up - lo) if up is not None else None)
            status = "CERTIFIED_s" if w_out <= tau else ("NOT_CERTIFIED_s" if (w_in is not None and w_in >= tau) else "GRAY_s")
            et_in, et_out = row.get("eps_tau_in"), row.get("eps_tau_out_lb")
            return dict(status=status, interpolated=False, outer=[olo, oup], inner=[lo, up], w_out=w_out, w_in=w_in,
                        eps_tau_in=et_in, eps_tau_out=et_out, eps_tau_out_is_lower_bound=row.get("eps_tau_out") is None,
                        f_in=(et_in / eps_i) if (et_in and eps_i > 0) else None,
                        f_out=(et_out / eps) if (et_out and eps > 0) else None, comps_min=cl, comps_max=cu)
        et_out, et_in = self.interp(n, label, J, "eps_tau_out_lb"), self.interp(n, label, J, "eps_tau_in")
        if et_out is None and et_in is None:
            status = "NA_s"
        elif et_out is not None and eps <= et_out:
            status = "CERTIFIED_s"
        elif et_in is not None and eps_i >= et_in:
            status = "NOT_CERTIFIED_s"
        else:
            status = "GRAY_s"
        return dict(status=status, interpolated=True, note="interpolated, not a bound", outer=None, inner=None,
                    w_out=None, w_in=None, eps_tau_in=et_in, eps_tau_out=et_out, eps_tau_out_is_lower_bound=False,
                    f_in=(et_in / eps_i) if (et_in and eps_i > 0) else None,
                    f_out=(et_out / eps) if (et_out and eps > 0) else None)


def truth(stored, real, n, J, label):
    """Sec. 0: O_GS and E0 are this project's bond-dimension-320 references where stored (summary_map.json: E0 at
    18 + 16 couplings, O_GS in the rows of the stored map), otherwise the authors' DMRG values of the public files.
    tau = 0.06 |O_GS| (float product, as in the stored map)."""
    key = C.jkey(J)
    d = real["dmrg"].get(key) if real is not None else None
    E0p = stored.E0(n, J)
    Op = stored.O_GS(n, J, label)
    E0 = E0p if E0p is not None else d["E0"]
    O = Op if Op is not None else d["labels"][label]
    return dict(E0=E0, E0_source="project" if E0p is not None else "authors", O_GS=O,
                O_source="project" if Op is not None else "authors", tau=C.TAU_FRAC * abs(O),
                E0_authors=None if d is None else d["E0"], O_authors=None if d is None else d["labels"][label])
