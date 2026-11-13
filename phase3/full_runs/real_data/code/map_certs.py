# real_data / map_certs.py  (own code; 2026-11-12; task rd-code-map)
#
# DECLARATION.md Sec. 2, certified side. Standard library only; every statement in fractions.Fraction.
#
#   load_certificates()  the stored exact certificates (files *_cert.json of the two rigor runs and of final_tests/),
#                        de-duplicated by SHA-256, each accepted only with its recorded exact verification (*_ver.json:
#                        ok, same file hash, same task, same exact bound) and with  sum_k t_k - mu M_0 == E_claim.
#                        Kinds m_s, Czz_bar, H. A certificate proves the operator inequality
#                              H(J) - sigma lam S O + mu M_tot >= c,        c = sum_k t_k = E_claim + mu M_0.
#   pool_ms / pool_czz   the pool of Sec. 2 for one row: direct certificates and pairs combined by concavity (m_s);
#                        every certificate of kind Czz_bar or H read as a bound on the plain Hamiltonian at J'
#                        (Czz_bar). Every member is one proved inequality  sigma <O> <= (E - c + mu M) / lamS.
#   exact_interval       I = [-U_-, U_+],  U_sigma = max over M in {M_real, M_0} of [min over the pool of u_sigma],
#                        with the allowance 1e-6 added to E_real and, for M = M_real, the worse of M_real +- 1e-6 taken
#                        bound by bound (so the result holds for every M within the allowance), capped at [-1, 1].
#   judge                width against tau = 0.06 |O_GS| (a dyadic number) and against tau_rf = (6/100) min |O| over I.
#   largest_E            the largest energy at which the row would still be CERTIFIED (exact), solved exactly.
import json
import os
from fractions import Fraction

import map_common as C

CERT_ROOTS = (os.path.join(C.RIGOR, "out_20261031T073328Z"), os.path.join(C.RIGOR, "out_20261031T100015Z"), C.FT)
E1_ROOT = os.path.join(C.RD, "e1")                     # extension E1 (Sec. 3): separate column, never in S
GRAPH_N = {"hh_d3.json": 19, "hh_d5.json": 57, "hh_d7.json": 115}
M0_OF_N = {19: 3, 57: 9, 115: 19}
# Sec. 2, "Range": couplings of the stored m_s certificates; outside, no row can be CERTIFIED (exact)
DECLARED_RANGE = {57: (Fraction(34, 10), Fraction(6)), 115: (Fraction(4), Fraction(6))}
CAP = (Fraction(-1), Fraction(1))                      # spectral range of m_s and of Czz_bar


class Cert:
    __slots__ = ("sha", "paths", "name", "n", "kind", "sigma", "lam", "J", "Jp", "c", "mu", "E_claim", "level")

    def ident(self):
        return dict(name=self.name, sha256=self.sha, kind=self.kind, Jz=C.fstr(self.J), sigma=self.sigma,
                    lam=C.fstr(self.lam), level=self.level, path=self.paths[0])


def find_cert_files(roots=CERT_ROOTS):
    out = []
    for root in roots:
        for dp, _, fn in os.walk(root):
            for f in fn:
                if f.endswith("_cert.json"):
                    out.append(os.path.join(dp, f).replace("\\", "/"))
    return sorted(out)


def read_cert(path):
    """(Cert, None) or (None, reason). Nothing is trusted that is not checked here in exact arithmetic."""
    with open(path, "rb") as f:
        raw = f.read()
    sha = C.sha256_bytes(raw)
    d = json.loads(raw)
    n = GRAPH_N.get(d.get("graph"))
    if n is None:
        return None, "graph %s is not one of the heavy-hex graphs" % d.get("graph")
    task, spec = d["task"], d["spec"]
    kind = task["kind"]
    if kind not in ("m_s", "Czz_bar", "H"):
        return None, "kind %s" % kind
    K = d["K"]
    if not isinstance(K, int) or not isinstance(d["mu"], int) or not all(isinstance(x, int) for x in d["t"]):
        return None, "mu, t or K is not an integer"
    den = 2 ** K
    mu = Fraction(d["mu"], den)
    c = sum(Fraction(x, den) for x in d["t"])
    E_claim = Fraction(d["E_claim"])
    J = Fraction(str(task["Jz"]))
    sigma = int(task.get("sigma", 0))
    lam = Fraction(str(task.get("lam", "0")))
    Jp = Fraction(spec["Jz"])
    if Fraction(spec["Jz_base"]) != J or int(spec.get("sigma", 0)) != sigma or Fraction(spec.get("lam", "0")) != lam:
        return None, "task and spec disagree"
    if kind == "H":
        if sigma != 0 or lam != 0 or Jp != J:
            return None, "kind H with a field"
    else:
        if sigma not in (1, -1) or lam <= 0:
            return None, "no sign or no positive field"
        if Jp != (J - 4 * sigma * lam if kind == "Czz_bar" else J):
            return None, "effective coupling of the spec is not the declared one"
    if c - mu * M0_OF_N[n] != E_claim:
        return None, "sum_k t_k - mu M_0 differs from E_claim"
    vp = path[:-len("_cert.json")] + "_ver.json"
    if not os.path.exists(vp):
        return None, "no verification record"
    v = C.rj(vp)
    if v.get("ok") is not True:
        return None, "verification record not ok"
    if v.get("cert_sha256") != sha:
        return None, "verification record is for another file"
    if v.get("task") != task or Fraction(v["E_LB_exact"]) != E_claim or int(v.get("twoS", -1)) != M0_OF_N[n]:
        return None, "verification record disagrees with the certificate"
    x = Cert()
    x.sha, x.paths, x.name, x.n, x.kind, x.sigma, x.lam = sha, [path], os.path.basename(path)[:-len("_cert.json")], n, kind, sigma, lam
    x.J, x.Jp, x.c, x.mu, x.E_claim, x.level = J, Jp, c, mu, E_claim, task.get("clusters")
    return x, None


def load_certificates(sizes=C.SIZES, roots=CERT_ROOTS):
    """dict(certs=[Cert], n_files, n_distinct, n_used, by_size, excluded=[(path, reason)]). De-duplicated by SHA-256."""
    files = find_cert_files(roots)
    by_sha, excluded, distinct = {}, [], set()
    for p in files:
        with open(p, "rb") as f:
            distinct.add(C.sha256_bytes(f.read()))
        x, why = read_cert(p)
        if x is None:
            excluded.append((p, why))
        elif x.sha in by_sha:
            by_sha[x.sha].paths.append(p)
        else:
            by_sha[x.sha] = x
    certs = sorted((x for x in by_sha.values() if x.n in sizes), key=lambda x: (x.n, x.kind, x.J, x.sigma, x.lam, x.sha))
    other = [x for x in by_sha.values() if x.n not in sizes]
    return dict(certs=certs, n_files=len(files), n_distinct=len(distinct), n_used=len(certs),
                n_verified_other_sizes=len(other), by_size={n: sum(1 for x in certs if x.n == n) for n in sizes},
                by_kind={"%d_%s" % (n, k): sum(1 for x in certs if x.n == n and x.kind == k) for n in sizes
                         for k in ("m_s", "Czz_bar", "H")}, excluded=excluded)


def ms_couplings(certs, n):
    return sorted(set(x.J for x in certs if x.n == n and x.kind == "m_s"))


def in_range(certs, n, J):
    """Sec. 2 'Range': J inside [smallest, largest] coupling of the m_s certificates of that size in this set."""
    js = ms_couplings(certs, n)
    return bool(js) and js[0] <= J <= js[-1]


# ------------------------------------------------------------------------------------------------ bounds and pools
class Bound:
    """One proved inequality for a row:  sigma <O> <= (E - c + mu M) / lamS  for every rho in W(E, M)."""
    __slots__ = ("sigma", "lamS", "c", "mu", "how", "members", "t")

    def __init__(self, sigma, lamS, c, mu, how, members, t=None):
        assert lamS > 0
        self.sigma, self.lamS, self.c, self.mu, self.how, self.members, self.t = sigma, lamS, c, mu, how, members, t

    def u(self, E, M, dM=0):
        """Value of the bound; dM > 0 takes the worse of M - dM and M + dM (the bound is affine in M)."""
        return (E - self.c + self.mu * M + abs(self.mu) * dM) / self.lamS

    def line(self, M, dM=0):
        """(a, b) with u(E) = a + b E."""
        return (-self.c + self.mu * M + abs(self.mu) * dM) / self.lamS, 1 / self.lamS

    def ident(self):
        return dict(how=self.how, t=C.fstr(self.t) if self.t is not None else None,
                    certificates=[m.ident() for m in self.members])


def combine(a, b, J, S):
    """Sec. 2: two certificates of the same sign at J_1 < J < J_2, t = (J_2 - J)/(J_2 - J_1). The convex combination of
    the two operator inequalities is the inequality at (J, t lam_1 + (1-t) lam_2) (H(J) is affine in J)."""
    assert a.sigma == b.sigma and a.J < J < b.J
    t = (b.J - J) / (b.J - a.J)
    assert t * a.J + (1 - t) * b.J == J
    return Bound(a.sigma, (t * a.lam + (1 - t) * b.lam) * S, t * a.c + (1 - t) * b.c, t * a.mu + (1 - t) * b.mu, "pair", (a, b), t)


def pool_ms(certs, n, J, pairs=True):
    """Sec. 2 pool for m_s: every direct certificate at J and every pair with J_1 < J < J_2 (same sign, that size)."""
    cs = [x for x in certs if x.n == n and x.kind == "m_s"]
    out = {1: [], -1: []}
    for x in cs:
        if x.J == J:
            out[x.sigma].append(Bound(x.sigma, x.lam * n, x.c, x.mu, "direct", (x,)))
    if pairs:
        for s in (1, -1):
            lo = [x for x in cs if x.sigma == s and x.J < J]
            hi = [x for x in cs if x.sigma == s and x.J > J]
            for a in lo:
                for b in hi:
                    out[s].append(combine(a, b, J, n))
    return out


def pool_czz(certs, n, J, n_e):
    """Sec. 2 pool for Czz_bar: every certificate of kind Czz_bar or H of that size, read as  H(J') + mu M >= c.
    J' < J gives Czz_bar <= 4 (E - c + mu M)/((J - J') n_e); J' > J gives Czz_bar >= -4 (E - c + mu M)/((J' - J) n_e)."""
    out = {1: [], -1: []}
    for x in certs:
        if x.n != n or x.kind not in ("Czz_bar", "H") or x.Jp == J:
            continue
        s = 1 if x.Jp < J else -1
        how = "direct" if (x.kind == "Czz_bar" and x.J == J) else "other_coupling"
        out[s].append(Bound(s, abs(J - x.Jp) * n_e / 4, x.c, x.mu, how, (x,)))
    return out


def make_pool(certs, n, label, J, n_e=None, pairs=True):
    if label == "m_s":
        return pool_ms(certs, n, J, pairs)
    if label == "Czz_bar":
        return pool_czz(certs, n, J, n_e)
    raise ValueError("no exact certificates for label %s" % label)


# ------------------------------------------------------------------------------------------------ the interval
def _cases(M_real, M0, allow):
    cs = []
    if M_real is not None:
        cs.append(("M_real", Fraction(M_real), allow))
    if M0 is not None:
        cs.append(("M_0", Fraction(M0), 0))
    return cs


def exact_interval(pool, E_real, M_real, M0, allow=C.ALLOW, cap=CAP):
    """Sec. 2. E_real, M_real: exact rationals (the dyadic numbers of the file). M_real = None evaluates the sector
    value M_0 only (unit tests against the stored rows). Returns None when one side has no certificate."""
    if not pool[1] or not pool[-1]:
        return None
    E = Fraction(E_real) + allow
    U, sides = {}, {}
    for s in (1, -1):
        cases = {}
        for tag, M, dM in _cases(M_real, M0, allow):
            best = None
            for b in pool[s]:
                v = b.u(E, M, dM)
                if best is None or v < best[0]:
                    best = (v, b)
            cases[tag] = best
        dec = max(cases, key=lambda k: cases[k][0])
        U[s] = cases[dec][0]
        sides[s] = dict(U=U[s], decisive_M=dec, cases=cases)
    lo_raw, hi_raw = -U[-1], U[1]
    lo, hi = max(lo_raw, cap[0]), min(hi_raw, cap[1])
    return dict(lo=lo, hi=hi, lo_raw=lo_raw, hi_raw=hi_raw, width=hi - lo, empty=bool(hi < lo), sides=sides,
                E_used=E, n_bounds={1: len(pool[1]), -1: len(pool[-1])})


def tau_reference_free(lo, hi):
    """As Test C of final_tests/DECLARATION.md: 0.06 times the smallest |O| on the interval."""
    return C.TAU_RF * (Fraction(0) if lo <= 0 <= hi else min(abs(lo), abs(hi)))


def judge(iv, tau):
    """tau: exact rational of the float 0.06 |O_GS|. Width against both tolerances (exact comparisons)."""
    tau = Fraction(tau)
    trf = tau_reference_free(iv["lo"], iv["hi"]) if not iv["empty"] else Fraction(0)
    return dict(tau=tau, tau_rf=trf, within_tau=bool(not iv["empty"] and iv["width"] <= tau),
                within_tau_rf=bool(not iv["empty"] and iv["width"] <= trf),
                width_over_tau=float(iv["width"] / tau) if tau > 0 else None,
                width_over_tau_rf=float(iv["width"] / trf) if trf > 0 else None)


def winners(iv):
    """The certificates behind the interval: for each side and each M, the members of the best bound."""
    out = {}
    for s, d in iv["sides"].items():
        for tag, (v, b) in d["cases"].items():
            for m in b.members:
                out[m.sha] = m
    return list(out.values())


def describe_sides(iv):
    return {("+" if s == 1 else "-"): dict(U=C.fstr(d["U"]), U_float=float(d["U"]), decisive_M=d["decisive_M"],
                                           cases={tag: dict(u=float(v), bound=b.ident()) for tag, (v, b) in d["cases"].items()})
            for s, d in iv["sides"].items()}


# ------------------------------------------------------------------------------------------------ largest energy
def _lines(pool, M_real, M0, allow):
    out = {}
    for s in (1, -1):
        out[s] = []
        for tag, M, dM in _cases(M_real, M0, allow):
            ls = [b.line(M, dM) for b in pool[s]]
            out[s].append((ls, [(float(a), float(b)) for a, b in ls]))
    return out


def _width_exact(L, E, cap):
    ends = []
    for s in (1, -1):
        best = None
        for ls, _ in L[s]:
            v = min((a + b * E, b) for a, b in ls)
            if best is None or v > best:
                best = v
        ends.append(best)
    (up, sp), (um, sm) = ends
    hi, lo = min(up, cap[1]), max(-um, cap[0])
    return hi - lo, (sp if up < cap[1] else 0) + (sm if -um > cap[0] else 0)


def _width_float(L, E, cap):
    w = 0.0
    for s, c in ((1, float(cap[1])), (-1, -float(cap[0]))):
        w += min(max(min(a + b * E for a, b in fl) for _, fl in L[s]), c)
    return w


def largest_E(pool, M_real, M0, tau, E_start, allow=C.ALLOW, cap=CAP):
    """The largest energy argument E (allowance already included) with width(I(E)) <= tau. The width is continuous,
    nondecreasing and piecewise affine in E: a float bisection locates the root, the active affine piece is then
    solved in exact arithmetic and the result is verified exactly (exact=True iff width(E) == tau as rationals;
    otherwise the returned E is an exact inner value with width(E) <= tau). None if no bracket is found."""
    if not pool[1] or not pool[-1]:
        return None
    tau = Fraction(tau)
    L = _lines(pool, M_real, M0, allow)
    tf = float(tau)
    lo = hi = float(E_start)
    step = 1.0 / 64
    if _width_float(L, lo, cap) <= tf:
        for _ in range(60):
            hi = lo + step
            if _width_float(L, hi, cap) > tf:
                break
            lo, step = hi, 2 * step
        else:
            return None
    else:
        for _ in range(60):
            lo = hi - step
            if _width_float(L, lo, cap) <= tf:
                break
            hi, step = lo, 2 * step
        else:
            return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if _width_float(L, mid, cap) <= tf:
            lo = mid
        else:
            hi = mid
    x = Fraction(lo)
    inner = None
    for _ in range(40):
        w, s = _width_exact(L, x, cap)
        if w == tau:
            return dict(E=x, exact=True)
        if w < tau and (inner is None or x > inner):
            inner = x
        if s <= 0:
            break
        x = x + (tau - w) / s
    if inner is None:                                  # walk down in exact arithmetic until the width is within tau
        x = Fraction(lo)
        for k in range(60):
            x = x - Fraction(1, 10 ** 12) * 2 ** k
            if _width_exact(L, x, cap)[0] <= tau:
                inner = x
                break
    return dict(E=inner, exact=False) if inner is not None else None
