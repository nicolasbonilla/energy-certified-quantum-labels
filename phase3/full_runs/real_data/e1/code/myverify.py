"""Reviewer math-rigorous-bounds (R10): independent exact re-verification of a cluster lower-bound certificate.

Own code; shares only the certificate FILE FORMAT with the authors' verifier (rigor/code/verify_exact.py is not imported).

What is proved here for one certificate, in exact integer / rational arithmetic only:
  (I)  operator identity   sum_k h_k (x) 1  =  H' + mu * sum_i Z_i      on the full 2^n space,
       by expanding every as-built cluster matrix h_k in the product operator basis B_{f,z} = X^f Z^z
       (Walsh-Hadamard transform, Python integers) and comparing the global coefficient table with a target
       table built directly from the graph and the task (not from the certificate's term list);
  (II) h_k - t_k * 1 is positive definite on every S^z block of every cluster, by
         'bareiss' : own fraction-free elimination (all leading principal minors > 0), vectorised on object arrays;
         'chol'    : verified Cholesky: a float factor L is only a witness; with L_q = round(L 2^p)/2^p the residual
                     R = (h_k - t_k - s) - L_q L_q^T is computed exactly and  h_k - t_k >= s - ||R||_inf > 0;
         'ldl'     : textbook LDL^T with fractions.Fraction (slow; used on selected blocks);
  (III) E_LB = sum_k t_k - mu * (n_up - n_down)   as an exact rational.
Then  E0_sector(H') >= E_LB  follows from (I)-(III) (see the report for the argument).

usage: python -B myverify.py <graph.json> <cert.json> <out.json> [--methods bareiss,chol] [--ldl K1,K2,...]
                                                          [--clusters a:b] [--no-identity]
"""
import hashlib
import json
import sys
import time
from fractions import Fraction
from math import lcm

import numpy as np


def popcount(x):
    return bin(x).count("1")


def as_fraction(v):
    """Exact value of a certificate / task number: strings are parsed exactly, floats are taken as the dyadic they are."""
    if isinstance(v, str):
        return Fraction(v)
    return Fraction(v)


# ------------------------------------------------------------------------------------------------ problem definition
def problem(G, task):
    """Exact definition of H' = H(Jz) - sigma*lam*S*O on the MPS-labelled graph, from the graph and the task only."""
    n = int(G["n"])
    M = G["mps"]
    edges = [tuple(sorted((int(a), int(b)))) for a, b in M["edges"]]
    assert len(set(edges)) == len(edges) and all(0 <= a < b < n for a, b in edges)
    eta = [int(x) for x in M["eta"]]
    up = [int(x) for x in M["up_init"]]
    assert len(eta) == n and len(up) == n and all(e in (1, -1) for e in eta) and all(u in (0, 1) for u in up)
    assert all((eta[i] == 1) == (up[i] == 1) for i in range(n)), "up_init is not the Neel state of eta"
    assert all(eta[a] == -eta[b] for a, b in edges), "eta is not a two-colouring"
    twoS = sum(2 * u - 1 for u in up)
    kind = task["kind"]
    Jz = as_fraction(task["Jz"])
    lam = as_fraction(task.get("lam", 0))
    sg = int(task.get("sigma", 0))
    site = [Fraction(0)] * n
    if kind == "m_s":
        site = [-sg * lam * eta[i] for i in range(n)]
        S = n
    elif kind == "Czz_bar":
        Jz = Jz - 4 * sg * lam
        S = len(edges)
    elif kind == "H":
        S = None
    else:
        raise ValueError(kind)
    return dict(n=n, edges=edges, eta=eta, twoS=twoS, kind=kind, Jz_eff=Jz, Jz_base=as_fraction(task["Jz"]), lam=lam,
                sigma=sg, site=site, S=S)


def format_terms(P):
    """Term list in the order the certificate's term_assign refers to (file format)."""
    T = []
    for (i, j) in P["edges"]:
        T.append(("xy", (i, j), Fraction(1, 4)))
        if P["Jz_eff"] != 0:
            T.append(("zz", (i, j), P["Jz_eff"] / 4))
    for i in range(P["n"]):
        if P["site"][i] != 0:
            T.append(("z", (i,), P["site"][i]))
    return T


# ---------------------------------------------------------------------------------------------- cluster operators
def build_cluster(k, P, T, C, D, den, inc):
    """Dense integer matrix D*h_k (numpy object array of Python ints). Local bit p <-> site clusters[k][p], bit 1 = up."""
    sk = C["clusters"][k]
    m = len(sk)
    dim = 1 << m
    pos = {s: p for p, s in enumerate(sk)}
    X = np.arange(dim, dtype=np.int64)
    H = np.zeros((dim, dim), dtype=object)
    H[:, :] = 0
    diag = [0] * dim

    def zsign(p):          # +1 for bit 1 (up), -1 for bit 0, as Python ints
        return [1 if (x >> p) & 1 else -1 for x in range(dim)]
    for (typ, sup, c), kk in zip(T, C["term_assign"]):
        if kk != k:
            continue
        if typ == "xy":
            p, q = pos[sup[0]], pos[sup[1]]
            v = 2 * c * D
            assert v.denominator == 1
            v = int(v)
            for x in range(dim):
                if ((x >> p) & 1) != ((x >> q) & 1):
                    H[x ^ (1 << p) ^ (1 << q), x] += v
        elif typ == "zz":
            p, q = pos[sup[0]], pos[sup[1]]
            v = c * D
            assert v.denominator == 1
            v = int(v)
            zp, zq = zsign(p), zsign(q)
            for x in range(dim):
                diag[x] += v * zp[x] * zq[x]
        elif typ == "z":
            p = pos[sup[0]]
            v = c * D
            assert v.denominator == 1
            v = int(v)
            zp = zsign(p)
            for x in range(dim):
                diag[x] += v * zp[x]
        else:
            raise ValueError(typ)
    muD = Fraction(int(C["mu"]), den) * D
    assert muD.denominator == 1
    muD = int(muD)
    for i in range(P["n"]):
        if C["site_assign"][i] == k:
            zp = zsign(pos[i])
            for x in range(dim):
                diag[x] += muD * zp[x]
    for x in range(dim):
        H[x, x] += diag[x]
    scale = D // den
    assert scale * den == D
    for (o, sgn) in inc[k]:
        kk, ll, O = C["overlaps"][o]
        q = len(O)
        op = [pos[s] for s in O]
        rest = [p for p in range(m) if p not in op]
        emb = np.zeros(1 << q, dtype=np.int64)
        for a in range(1 << q):
            x = 0
            for t, p in enumerate(op):
                if (a >> t) & 1:
                    x |= 1 << p
            emb[a] = x
        bases = np.zeros(1 << len(rest), dtype=np.int64)
        for cfg in range(1 << len(rest)):
            b = 0
            for t, p in enumerate(rest):
                if (cfg >> t) & 1:
                    b |= 1 << p
            bases[cfg] = b
        for (a, b, v) in C["Y"][o]:
            a, b, v = int(a), int(b), int(v)
            assert 0 <= a <= b < (1 << q) and popcount(a) == popcount(b), "multiplier index / S^z"
            val = sgn * v * scale
            ra, rb = bases | emb[a], bases | emb[b]
            np.add.at(H, (ra, rb), val)
            if a != b:
                np.add.at(H, (rb, ra), val)
    return H, m


def sz_blocks(H, m):
    dim = 1 << m
    pc = np.array([popcount(x) for x in range(dim)])
    nz = (H != 0)
    assert not (nz & (pc[:, None] != pc[None, :])).any(), "cluster operator does not conserve S^z"
    assert (H == H.T).all(), "cluster operator not symmetric"
    return [np.nonzero(pc == w)[0] for w in range(m + 1)]


# ------------------------------------------------------------------------------------------ exact positivity tests
def bareiss_pd(A):
    """Own fraction-free elimination on an integer symmetric matrix (object array). True iff all leading principal
    minors are > 0. Every division is checked to be exact."""
    A = A.copy()
    N = A.shape[0]
    prev = 1
    for k in range(N):
        piv = A[k, k]
        if piv <= 0:
            return False, k
        if k + 1 < N:
            num = piv * A[k + 1:, k + 1:] - np.multiply.outer(A[k + 1:, k], A[k, k + 1:])
            if prev != 1:
                quo = num // prev
                assert ((num - quo * prev) == 0).all(), "inexact division in fraction-free elimination"
                num = quo
            A[k + 1:, k + 1:] = num
        prev = piv
    return True, N


def ldl_pd(A):
    """Textbook LDL^T with Fractions; True iff every pivot d_k > 0."""
    N = A.shape[0]
    a = [[Fraction(int(A[i, j])) for j in range(N)] for i in range(N)]
    for k in range(N):
        d = a[k][k]
        if d <= 0:
            return False, k
        for i in range(k + 1, N):
            if a[i][k] != 0:
                f = a[i][k] / d
                for j in range(k + 1, i + 1):
                    a[i][j] -= f * a[j][k]
        # (only the lower triangle is used / updated)
    return True, N


def chol_pd(A, D, s_exps=(31, 33, 36, 40, 46), p=62):
    """Verified Cholesky. Returns (True, exact lower bound on lambda_min(A/D) as a Fraction) or (False, None).
    A/D - s = Lq Lq^T + R exactly, hence lambda_min(A/D) >= s - max_i sum_j |R_ij| (Gershgorin), all in integers."""
    N = A.shape[0]
    Af = A.astype(np.float64) / float(D)
    for s_exp in s_exps:
        try:
            L = np.linalg.cholesky(Af - 2.0 ** (-s_exp) * np.eye(N))
        except np.linalg.LinAlgError:
            continue
        Lint = np.zeros((N, N), dtype=object)
        Lint[:, :] = 0
        sc = float(2 ** p)
        for i in range(N):
            for j in range(i + 1):
                Lint[i, j] = int(round(float(L[i, j]) * sc))
        M = Lint.dot(Lint.T)
        R = A * (1 << (2 * p)) - D * M              # = D 2^(2p) (A/D - Lq Lq^T)
        sD = D << (2 * p - s_exp)                   # = D 2^(2p) s
        for i in range(N):
            R[i, i] -= sD
        rowsum = max(sum(abs(int(v)) for v in R[i, :]) for i in range(N))
        if sD - rowsum > 0:
            return True, Fraction(sD - rowsum, D << (2 * p))
    return False, None


# ------------------------------------------------------------------------------------------- global operator identity
def wht_rows(Tm):
    """In-place Walsh-Hadamard transform along axis 1 of an object array (dim x dim), exact integers."""
    dim = Tm.shape[1]
    h = 1
    while h < dim:
        V = Tm.reshape(Tm.shape[0], dim // (2 * h), 2, h)
        a = V[:, :, 0, :] + V[:, :, 1, :]
        b = V[:, :, 0, :] - V[:, :, 1, :]
        V[:, :, 0, :] = a
        V[:, :, 1, :] = b
        h *= 2
    return Tm


def accumulate_identity(coef, H, sk, m, Mmax):
    """Add the coefficients of (D*h_k) in the basis B_{f,z} = X^f Z^z (B|x> = (-1)^{z.x} |x^f>), scaled by 2^Mmax,
    to the global table coef[(F, Z)] (global site masks)."""
    dim = 1 << m
    X = np.arange(dim, dtype=np.int64)
    spread = [0] * dim
    for a in range(dim):
        g = 0
        for p in range(m):
            if (a >> p) & 1:
                g |= 1 << sk[p]
        spread[a] = g
    Tm = np.zeros((dim, dim), dtype=object)
    for f in range(dim):
        Tm[f, :] = H[X ^ f, X]
    wht_rows(Tm)                                    # Tm[f, z] = sum_x (-1)^{z.x} H[x^f, x] = 2^m a_{f,z}
    fz = np.nonzero(Tm != 0)
    sc = 1 << (Mmax - m)
    for f, z in zip(fz[0].tolist(), fz[1].tolist()):
        key = (spread[f], spread[z])
        coef[key] = coef.get(key, 0) + int(Tm[f, z]) * sc
    return len(fz[0])


def target_identity(P, mu, D, Mmax):
    """Coefficient table of D 2^Mmax (H' + mu sum_i Z_i) in the same basis, straight from graph and task."""
    tgt = {}
    sc = D << Mmax

    def put(F, Z, v):
        v = v * sc
        assert v.denominator == 1
        if v != 0:
            tgt[(F, Z)] = tgt.get((F, Z), 0) + int(v)
    for (i, j) in P["edges"]:
        F = (1 << i) | (1 << j)
        put(F, 0, Fraction(1, 4))                   # 1/4 (XX + YY) = 1/4 X^F (1 - Z^F)
        put(F, F, Fraction(-1, 4))
        put(0, F, P["Jz_eff"] / 4)                  # Z_i Z_j is convention independent
    for i in range(P["n"]):
        put(0, 1 << i, -(P["site"][i] + mu))        # physical Z_i (bit 1 = up) = - Z^{e_i}
    return tgt


# ------------------------------------------------------------------------------------------------------------ main
def verify(gpath, cpath, methods=("bareiss", "chol"), ldl_clusters=(), cl_range=None, identity=True, log=print):
    t0 = time.time()
    graw = open(gpath, "rb").read()
    G = json.loads(graw)
    craw = open(cpath, "rb").read()
    C = json.loads(craw)
    gsha = hashlib.sha256(graw).hexdigest()
    assert gsha == C["graph_sha256"], "graph hash differs from the certificate's"
    P = problem(G, C["task"])
    n = P["n"]
    T = format_terms(P)
    cl = [list(map(int, c)) for c in C["clusters"]]
    sets = [set(c) for c in cl]
    nc = len(cl)
    for c in cl:
        assert c == sorted(set(c)) and all(0 <= v < n for v in c)
    assert len(C["term_assign"]) == len(T) and len(C["site_assign"]) == n and len(C["t"]) == nc
    for (typ, sup, c), k in zip(T, C["term_assign"]):
        assert 0 <= k < nc and set(sup) <= sets[k]
    for i, k in enumerate(C["site_assign"]):
        assert 0 <= k < nc and i in sets[k]
    assert len(C["Y"]) == len(C["overlaps"])
    seen = set()
    inc = [[] for _ in cl]
    for o, (k, l, O) in enumerate(C["overlaps"]):
        assert 0 <= k < l < nc and list(O) == sorted(set(O)) and set(O) <= (sets[k] & sets[l]) and (k, l) not in seen
        seen.add((k, l))
        inc[k].append((o, 1))
        inc[l].append((o, -1))
    K = int(C["K"])
    den = 1 << K
    D = den
    for (typ, sup, c) in T:
        D = lcm(D, c.denominator, (2 * c).denominator)
    mu = Fraction(int(C["mu"]), den)
    tk = [Fraction(int(t), den) for t in C["t"]]
    Mmax = max(len(c) for c in cl)
    coef = {}
    rng = range(nc) if cl_range is None else range(*cl_range)
    res = dict(cert=cpath.replace("\\", "/"), cert_sha256=hashlib.sha256(craw).hexdigest(), graph_sha256=gsha, task=C["task"],
               n=n, n_clusters=nc, cluster_sizes=sorted(set(len(c) for c in cl)), n_overlaps=len(C["overlaps"]),
               n_multiplier_entries=sum(len(y) for y in C["Y"]), denominator_bits=D.bit_length() - 1,
               D_is_power_of_two=(D & (D - 1)) == 0, methods=list(methods), clusters_checked=[rng.start, rng.stop],
               n_blocks=0, max_block=0, per_cluster=[])
    all_ok = True
    for k in rng:
        tc = time.time()
        H, m = build_cluster(k, P, T, C, D, den, inc)
        blocks = sz_blocks(H, m)
        tD = tk[k] * D
        assert tD.denominator == 1
        tD = int(tD)
        rec = dict(k=k, m=m, ok={}, chol_lower_bound_min=None, float_margin=None)
        fm = None
        for meth in methods:
            rec["ok"][meth] = True
        if k in ldl_clusters:
            rec["ok"]["ldl"] = True
        cmin = None
        for I in blocks:
            A = H[np.ix_(I, I)].copy()
            for r in range(len(I)):
                A[r, r] -= tD
            res["n_blocks"] += 1
            res["max_block"] = max(res["max_block"], len(I))
            ev = np.linalg.eigvalsh(A.astype(np.float64) / float(D))[0]
            fm = ev if fm is None else min(fm, ev)
            if "bareiss" in methods:
                ok, _ = bareiss_pd(A)
                rec["ok"]["bareiss"] &= bool(ok)
            if "chol" in methods:
                ok, lb = chol_pd(A, D)
                rec["ok"]["chol"] &= bool(ok)
                if ok:
                    cmin = lb if cmin is None else min(cmin, lb)
            if k in ldl_clusters:
                ok, _ = ldl_pd(A)
                rec["ok"]["ldl"] &= bool(ok)
        rec["float_margin"] = float(fm)
        rec["chol_lower_bound_min"] = None if cmin is None else float(cmin)
        if identity:
            rec["n_basis_coeffs"] = accumulate_identity(coef, H, cl[k], m, Mmax)
        rec["secs"] = time.time() - tc
        all_ok &= all(rec["ok"].values())
        res["per_cluster"].append(rec)
        log("cluster %3d m=%d blocks %d  %s  float margin %+.3e  chol lb %s  %.1fs" % (
            k, m, len(blocks), rec["ok"], rec["float_margin"], rec["chol_lower_bound_min"], rec["secs"]))
    res["all_cluster_inequalities_proved"] = bool(all_ok)
    if identity and cl_range is None:
        coef = {kk: v for kk, v in coef.items() if v != 0}
        tgt = target_identity(P, mu, D, Mmax)
        res["identity_nonzero_coeffs"] = len(coef)
        res["identity_target_coeffs"] = len(tgt)
        res["identity_holds"] = bool(coef == tgt)
        log("operator identity sum_k h_k = H' + mu sum Z : %s (%d coefficients, target %d)" % (
            res["identity_holds"], len(coef), len(tgt)))
    E = sum(tk) - mu * P["twoS"]
    res["E_LB_exact"] = str(E)
    res["E_LB_float"] = float(E)
    res["E_claim_in_cert"] = C["E_claim"]
    res["E_matches_cert_claim"] = bool(Fraction(C["E_claim"]) == E)
    res["twoS"] = P["twoS"]
    res["mu"] = str(mu)
    res["lam"] = str(P["lam"])
    res["Jz_eff"] = str(P["Jz_eff"])
    res["S"] = P["S"]
    res["min_float_margin"] = min(r["float_margin"] for r in res["per_cluster"])
    res["time_s"] = time.time() - t0
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    gpath, cpath, opath = a[0], a[1], a[2]
    methods = ("bareiss", "chol")
    ldl = ()
    clr = None
    ident = True
    i = 3
    while i < len(a):
        if a[i] == "--methods":
            methods = tuple(x for x in a[i + 1].split(",") if x)
            i += 2
        elif a[i] == "--ldl":
            ldl = tuple(int(x) for x in a[i + 1].split(","))
            i += 2
        elif a[i] == "--clusters":
            lo, hi = a[i + 1].split(":")
            clr = (int(lo), int(hi))
            i += 2
        elif a[i] == "--no-identity":
            ident = False
            i += 1
        else:
            raise SystemExit("unknown option " + a[i])
    r = verify(gpath, cpath, methods=methods, ldl_clusters=ldl, cl_range=clr, identity=ident)
    json.dump(r, open(opath, "w"), indent=1)
    print("E_LB exact %s = %.12f ; matches cert claim: %s ; all cluster inequalities proved: %s ; identity: %s ; %d blocks, max %d ; %.1fs" % (
        r["E_LB_exact"], r["E_LB_float"], r["E_matches_cert_claim"], r["all_cluster_inequalities_proved"],
        r.get("identity_holds"), r["n_blocks"], r["max_block"], r["time_s"]))
