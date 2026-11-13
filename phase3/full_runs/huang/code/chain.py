"""Witness chains and the two-sided information limit for one label (shared by the exact-diagonalization and the DMRG
tasks of phase3/full_runs/huang; DECLARATION.md section 1). Built on full_runs/map/code/witness.py (predict_lam,
eps_tau_from, the aim/straddle ladder); generalized to labels with spectral bounds [o_min, o_max] and field scale S.

A chain point is a dict with at least: lam, sign (+1/-1), E (exact energy of an explicit state), o (its label value),
F_lo (a lower bound used for the dual line: E0(H - sign lam S O) >= F_lo).
  inner width  w_in(E):  hull of the explicit states (pure points and two-state mixtures, hull.py), rigorous;
  outer width  w_out(E): Lagrange-dual lines sign*o <= (E - F_lo)/(lam S), capped at the spectral bounds.
"""
import math
import hull


def w_in(pool, E):
    W = hull.width(pool, E)[0]
    return W if W is not None else 0.0


def ub_out(points, E, S, obounds):
    up = obounds[1]
    lo = obounds[0]
    for p in points:
        if p["lam"] <= 0:
            continue
        b = (E - p["F_lo"]) / (p["lam"] * S)
        if p["sign"] > 0:
            up = min(up, b)
        else:
            lo = max(lo, -b)
    return lo, up


def w_out(points, E, S, obounds):
    lo, up = ub_out(points, E, S, obounds)
    return up - lo


def pool_of(E0, o0, points):
    return [dict(sid="gs", E=E0, o=o0)] + [dict(sid="p%d" % k, E=p["E"], o=p["o"]) for k, p in enumerate(points)]


def eps_tau(E0, o0, points, S, obounds, tau, eps_hi):
    """(eps_tau_in, eps_tau_out): smallest eps with w_in(E0 + eps) >= tau, resp. w_out >= tau, on [1e-9, eps_hi]
    (None if not reached by eps_hi). Both widths are nondecreasing in eps."""
    pool = pool_of(E0, o0, points)
    have_both = any(p["sign"] > 0 and p["lam"] > 0 for p in points) and any(p["sign"] < 0 and p["lam"] > 0
                                                                            for p in points)

    def solve(f):
        lo, hi = 1e-9, eps_hi
        if f(hi) < tau:
            return None
        for _ in range(70):
            mid = math.sqrt(lo * hi)
            if f(mid) >= tau:
                hi = mid
            else:
                lo = mid
        return hi
    ein = solve(lambda e: w_in(pool, E0 + e))
    eout = solve(lambda e: w_out(points, E0 + e, S, obounds)) if have_both else None
    return ein, eout


def predict_lam(pts, eps_t, chi_two, S, lam0, lam_max):
    """lambda expected to give eps = eps_t on one side; pts = [(lam, eps)] of that side (map/witness.py)."""
    good = sorted((l, e) for l, e in pts if e > 1e-13 and l > 0)
    if not good:
        if chi_two and chi_two > 0:
            return min(lam_max, math.sqrt(2.0 * eps_t / (S * chi_two)))
        return min(lam_max, 2.0 * lam0)
    below = [p for p in good if p[1] <= eps_t]
    above = [p for p in good if p[1] > eps_t]
    if below and above:
        lo = max(below, key=lambda p: p[0])
        hi_c = [p for p in above if p[0] > lo[0]]
        if hi_c:
            hi = min(hi_c, key=lambda p: p[0])
            x0, x1 = math.log(lo[0]), math.log(hi[0])
            y0, y1 = math.log(lo[1]), math.log(hi[1])
            if y1 > y0:
                x = x0 + (math.log(eps_t) - y0) * (x1 - x0) / (y1 - y0)
                return min(lam_max, math.exp(x))
            return min(lam_max, math.sqrt(lo[0] * hi[0]))
    if not below:
        l1, e1 = min(good, key=lambda p: p[0])
        return min(lam_max, l1 * math.sqrt(eps_t / e1))
    top = sorted(good)[-2:]
    if len(top) == 2 and top[1][1] > top[0][1] and top[1][0] > top[0][0]:
        slope = (math.log(top[1][1]) - math.log(top[0][1])) / (math.log(top[1][0]) - math.log(top[0][0]))
        slope = max(1.0, min(4.0, slope))
    else:
        slope = 2.0
    l1, e1 = top[-1]
    lam = l1 * (eps_t / e1) ** (1.0 / slope)
    return min(lam_max, lam, 100.0 * l1)


class Ladder:
    """The declared point ladder of one label (both signs). solve(sign, lam, why) -> point dict (or None)."""

    def __init__(self, solve, E0, o0, S, obounds, tau, lam0, lam_max, n_max_side, a_cover=0.10, log=None):
        self.solve, self.E0, self.o0, self.S, self.ob = solve, E0, o0, S, obounds
        self.tau, self.lam0, self.lam_max, self.n_max = tau, lam0, lam_max, n_max_side
        self.a = a_cover
        self.pts = {+1: [], -1: []}
        self.sat = {+1: False, -1: False}
        self.log = log if log is not None else []
        self.chi_two = None

    def points(self):
        return self.pts[+1] + self.pts[-1]

    def evaluate(self, sign, lam, why):
        if any(abs(lam - p["lam"]) <= 1e-9 * max(1.0, lam) for p in self.pts[sign]):
            return None
        if len(self.pts[sign]) >= self.n_max:
            return None
        p = self.solve(sign, lam, why)
        if p is None:
            return None
        p["sign"] = sign
        p["eps"] = p["E"] - self.E0
        p["step"] = why
        self.pts[sign].append(p)
        bound = self.ob[1] if sign > 0 else self.ob[0]
        if lam >= self.lam_max * (1 - 1e-12) and abs(p["o"] - bound) <= 0.005 * (self.ob[1] - self.ob[0]):
            self.sat[sign] = True
        return p

    def cover(self, sign, e):
        below = any(e * (1 - self.a) <= p["eps"] <= e for p in self.pts[sign])
        above = any(e < p["eps"] <= e * (1 + self.a) for p in self.pts[sign])
        return below, above

    def aim(self, sign, e, why, straddle=False, bias=1.0):
        for _ in range(3 if straddle else 2):
            below, above = self.cover(sign, e)
            if (below and above) or (not straddle and (below or above)):
                return
            if self.sat[sign] or len(self.pts[sign]) >= self.n_max:
                return
            goal = e * bias
            if straddle and below:
                goal = e * (1 + 0.5 * self.a)
            elif straddle and above:
                goal = e * (1 - 0.5 * self.a)
            lam = predict_lam([(p["lam"], p["eps"]) for p in self.pts[sign]], goal, self.chi_two, self.S,
                              self.lam0, self.lam_max)
            p = self.evaluate(sign, lam, why)
            if p is None:
                return
            if lam >= self.lam_max * (1 - 1e-12) and p["eps"] < e:
                self.log.append(dict(side=sign, note="lam_max reached below target", eps_t=e))
                return

    def run(self, targets, eps_cap, tau_rounds=2):
        """targets: list of (eps, straddle) aimed at in ascending order on both sides, after lambda_0; then the
        measured eps_tau (inner/outer geometric mean) straddled on each side, up to tau_rounds rounds."""
        for sign in (+1, -1):
            self.evaluate(sign, self.lam0, "lam0")
        pp, pm = self.pts[+1][0], self.pts[-1][0]
        self.chi_two = (pp["o"] - pm["o"]) / (2.0 * self.lam0)
        law = self.S * self.tau ** 2 / (8.0 * self.chi_two) if self.chi_two > 0 else None
        T = list(targets)
        if law:
            T.append((min(eps_cap, law), False))
        T = sorted(T)
        for sign in (+1, -1):
            for e, strad in T:
                self.aim(sign, e, "target", strad)
        eps_hi = max([p["eps"] for p in self.points()] + [eps_cap])
        ein, eout = eps_tau(self.E0, self.o0, self.points(), self.S, self.ob, self.tau, eps_hi)
        for _ in range(tau_rounds):
            em = math.sqrt(ein * eout) if (ein and eout) else (ein or eout)
            if not em:
                break
            for sign in (+1, -1):
                self.aim(sign, em, "tau", True)
            eps_hi = max([p["eps"] for p in self.points()] + [eps_cap])
            ein, eout = eps_tau(self.E0, self.o0, self.points(), self.S, self.ob, self.tau, eps_hi)
            if ein and eout and ein / eout < 1.02:
                break
        return dict(chi_two=self.chi_two, eps_tau_law=law, eps_tau_in=ein, eps_tau_out=eout, eps_hi=eps_hi,
                    saturated={"+": self.sat[+1], "-": self.sat[-1]},
                    n_points={"+": len(self.pts[+1]), "-": len(self.pts[-1])})
