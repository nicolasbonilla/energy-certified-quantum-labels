"""Pool hull of the witness pilot (DECLARATION.md SHA-256 529e8dcd..., §3). numpy only.

A pool is a list of points {sid, E, o}. o+(E) = max over pure points with E_a <= E and over two-point mixtures with
energy (1-t)E_a + tE_b = E (straddling pairs; non-straddling mixtures are dominated). o-(E) likewise with min.
"""
import math


def extreme(pts, E, sign=+1):
    """Return (value, components) of sign*max(sign*o) at energy <= E; components = [(sid, weight, E_a, o_a)]."""
    best = None
    for a in pts:
        if a["E"] <= E:
            v = sign * a["o"]
            if best is None or v > best[0]:
                best = (v, [(a["sid"], 1.0, a["E"], a["o"])])
    for a in pts:
        if a["E"] > E:
            continue
        for b in pts:
            if b["E"] <= E:
                continue
            t = (E - a["E"]) / (b["E"] - a["E"])
            val = (1 - t) * a["o"] + t * b["o"]
            v = sign * val
            if best is None or v > best[0] + 1e-15:
                best = (v, [(a["sid"], 1 - t, a["E"], a["o"]), (b["sid"], t, b["E"], b["o"])])
    if best is None:
        return None, []
    return sign * best[0], best[1]


def pure_extreme(pts, E, sign=+1):
    c = [a for a in pts if a["E"] <= E]
    if not c:
        return None, None
    a = max(c, key=lambda a: sign * a["o"])
    return a["o"], a["sid"]


def width(pts, E):
    up, cu = extreme(pts, E, +1)
    lo, cl = extreme(pts, E, -1)
    if up is None:
        return None, None, None, cu, cl
    return up - lo, up, lo, cu, cl


def mix_energy(comps):
    return sum(w * Ea for (_, w, Ea, _) in comps)


def curve(pts, E0, eps_list):
    out = []
    for e in eps_list:
        D, up, lo, _, _ = width(pts, E0 + e)
        out.append((e, D, up, lo))
    return out


def eps_star(pts, E0, target):
    """Smallest eps >= 0 with D(E0 + eps) >= target. D is piecewise linear between the union of the pool energies."""
    bps = sorted(set([0.0] + [a["E"] - E0 for a in pts if a["E"] - E0 > 0]))
    prev = None
    for e in bps:
        D = width(pts, E0 + e)[0]
        if D is None:
            prev = (e, None)
            continue
        if D >= target:
            if prev is None or prev[1] is None:
                return e, D
            e0, D0 = prev
            # D is linear on [e0, e]; solve D0 + (D - D0)(x - e0)/(e - e0) = target (bisection for safety)
            lo, hi = e0, e
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if width(pts, E0 + mid)[0] >= target:
                    hi = mid
                else:
                    lo = mid
            return hi, width(pts, E0 + hi)[0]
        prev = (e, D)
    return None, None


def log_grid(lo, hi, k):
    return [lo * (hi / lo) ** (i / (k - 1)) for i in range(k)]


def next_lambda(evals, E0, Ethr, delta, eps_used, lam0, lam_max, tol, N_max):
    """Declared lambda search (§5.2). evals: list of (lam, E) for lam > 0 already evaluated in this chain.
    Returns the next lambda, or None (finished). Also returns a status string."""
    if not evals:
        return lam0, "start"
    thr = Ethr - delta
    below = [p for p in evals if p[1] <= thr]
    lam_lo = max([p[0] for p in below], default=0.0)
    E_lo = E0 if lam_lo == 0.0 else min(p[1] for p in evals if p[0] == lam_lo)
    above = [p for p in evals if p[1] > thr and p[0] > lam_lo]
    if not above:
        lam_last = max(p[0] for p in evals)
        if lam_last >= lam_max - 1e-15:
            return None, "saturated"
        if len(evals) >= N_max:
            return None, "N_max"
        return min(2 * lam_last, lam_max), "double"
    if len(evals) >= N_max:
        return None, "N_max"
    lam_hi = min(p[0] for p in above)
    E_hi = min(p[1] for p in evals if p[0] == lam_hi)
    if E_hi - E_lo <= tol * eps_used:
        return None, "bracketed"
    lam = math.sqrt(lam_lo * lam_hi) if lam_lo > 0 else lam_hi / 2
    if any(abs(lam - p[0]) <= 1e-12 * max(1.0, lam) for p in evals):
        return None, "repeat"
    return lam, "bisect"


def bracket(evals, Ethr, delta):
    thr = Ethr - delta
    below = [p for p in evals if p[1] <= thr]
    lam_lo = max([p[0] for p in below], default=0.0)
    above = [p for p in evals if p[1] > thr and p[0] > lam_lo]
    lam_hi = min([p[0] for p in above], default=None)
    return lam_lo, lam_hi


def monotone_flags(evals_sorted_by_lam, sign_o):
    """evals: list of (lam, E, o). Returns (E monotone nondecreasing, sign*o monotone nondecreasing)."""
    e = [p[1] for p in evals_sorted_by_lam]
    o = [sign_o * p[2] for p in evals_sorted_by_lam]
    tolE = 1e-7
    return (all(e[i + 1] >= e[i] - tolE for i in range(len(e) - 1)),
            all(o[i + 1] >= o[i] - 1e-7 for i in range(len(o) - 1)))
