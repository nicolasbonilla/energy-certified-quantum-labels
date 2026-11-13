# R11 fix pass (fixer FT, 2026-11-13): copy of paper/reviews/R11_2026-11-13/scratch/hostile-A/c1_theory.py;
# only the path of the data folder was adapted. Run here with the argument CD (the 12-site comb with the window of
# energy and mean magnetization, and the sectors of the 19-site patch): output ft_mean_window_comb_and_n19_out.txt.
# hostile-A / c1_theory.py -- own numerical tests of the new statements (Sec. II window of energy and mean magnetization,
# contour bound, local rule of Sec. S16, Lemma on single sites, Proposition on unpinned order, Theorem 4 remarks at n = 19).
# Own code throughout; exact diagonalization up to 19 sites.  usage: python -B -I c1_theory.py [parts]
import itertools, json, math, sys, time
from fractions import Fraction as Fr
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
from scipy.optimize import minimize_scalar, linprog

PARTS = sys.argv[1] if len(sys.argv) > 1 else "ABCDEFG"
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")).replace("\\", "/")   # phase3/full_runs (path adapted from the reader's copy; nothing else changed)
T0 = time.time()


# ------------------------------------------------------------------ graphs
def heavy_hex(d):
    """Patch of odd distance d from the definition printed in Supplemental Secs. S1 / S16."""
    idx = {}
    def node(*k):
        return idx.setdefault(k, len(idx))
    for c in range(d):
        for k in range(d):
            node("D", c, k)
    edges = []
    for c in range(d):
        for r in range(d - 1):
            f = node("F", c, r); edges += [(f, node("D", c, r)), (f, node("D", c, r + 1))]
    for i in range(d - 1):
        for r in range(d - 1):
            if (i + r) % 2 == 1:
                s = node("S", i, r); edges += [(s, node("F", i, r)), (s, node("F", i + 1, r))]
    for i in range(d - 1):
        t = node("T", i)
        if i % 2 == 0:
            edges += [(t, node("D", i, 0)), (t, node("D", i + 1, 0))]
        else:
            edges += [(t, node("D", i, d - 1)), (t, node("D", i + 1, d - 1))]
    n = len(idx)
    eta = np.zeros(n, int)
    for k, v in idx.items():
        eta[v] = 1 if k[0] in ("D", "S") else -1
    edges = [tuple(sorted(e)) for e in edges]
    return n, edges, eta, idx


def comb(nb):
    edges = [(i, i + 1) for i in range(nb - 1)]
    n = nb
    for i in range(1, nb, 2):
        edges.append((i, n)); n += 1
    eta = np.zeros(n, int)
    for i in range(nb):
        eta[i] = 1 if i % 2 == 0 else -1
    for (a, b) in edges[nb - 1:]:
        eta[b] = -eta[a]
    if eta.sum() < 0:
        eta = -eta
    return n, edges, eta


# ------------------------------------------------------------------ exact diagonalization in S^z sectors
def sector_states(n, nup):
    st = np.fromiter((sum(1 << i for i in c) for c in itertools.combinations(range(n), nup)), dtype=np.int64)
    st.sort()
    return st


def zvals(st, n):
    return 2.0 * ((st[:, None] >> np.arange(n)[None, :]) & 1) - 1.0      # Z = +1 for a set bit (up)


def xxz_sector(n, edges, Jz, st, Z=None):
    """H = 1/4 sum (XX + YY + Jz ZZ) on the given basis states (fixed number of up spins)."""
    Z = zvals(st, n) if Z is None else Z
    diag = np.zeros(len(st))
    rows, cols = [], []
    for (i, j) in edges:
        diag += 0.25 * Jz * Z[:, i] * Z[:, j]
        sel = np.nonzero(Z[:, i] != Z[:, j])[0]
        tgt = st[sel] ^ (1 << i) ^ (1 << j)
        rows.append(np.searchsorted(st, tgt)); cols.append(sel)
    if rows:
        r = np.concatenate(rows); c = np.concatenate(cols)
        off = sp.csr_matrix((np.full(len(r), 0.5), (r, c)), shape=(len(st), len(st)))
    else:
        off = sp.csr_matrix((len(st), len(st)))
    return off, diag


def lowest(off, diag, k=1, dense_below=1500):
    m = len(diag)
    if m <= dense_below:
        w, v = np.linalg.eigh(off.toarray() + np.diag(diag))
        return w[:k], v[:, :k]
    rng = np.random.default_rng(7)
    w, v = eigsh(off + sp.diags(diag), k=k, which="SA", v0=rng.standard_normal(m), tol=1e-11, maxiter=20000)
    o = np.argsort(w)
    return w[o], v[:, o]


import scipy.linalg as sla


def low1(off, diag):
    """lowest eigenvalue of off + diag(diag); off may be dense or sparse."""
    m = len(diag)
    if m <= 600:
        A = (off.toarray() if sp.issparse(off) else off) + np.diag(diag)
        return sla.eigh(A, eigvals_only=True, subset_by_index=[0, 0])[0] if m > 1 else A[0, 0]
    return lowest(off if sp.issparse(off) else sp.csr_matrix(off), diag, k=1)[0][0]


def argmin_log(f, lo=-8.0, hi=5.0, npts=14):
    """minimum of f(log lambda) on [lo, hi]: coarse grid, then bounded refinement around the best point."""
    xs = np.linspace(lo, hi, npts); fs = [f(x) for x in xs]
    k = int(np.argmin(fs)); a = xs[max(k - 1, 0)]; b = xs[min(k + 1, npts - 1)]
    r = minimize_scalar(f, bounds=(a, b), method="bounded", options=dict(xatol=1e-9, maxiter=60))
    return min(r.fun, fs[k])


if "A" in PARTS:
    print("== A. geometry of the patches (own construction) ==")
    for d in (3, 5, 7, 9, 11, 13):
        n, edges, eta, idx = heavy_hex(d)
        deg = np.zeros(n, int)
        nb = [[] for _ in range(n)]
        for a, b in edges:
            deg[a] += 1; deg[b] += 1; nb[a].append(b); nb[b].append(a)
        assert len(set(edges)) == len(edges) and all(eta[a] * eta[b] == -1 for a, b in edges)
        maj = np.nonzero(eta == 1)[0]; mino = np.nonzero(eta == -1)[0]
        S1 = (sorted(deg[maj]).count(1) == 2 and set(deg[maj]) <= {1, 2} and set(deg[mino]) <= {2, 3}
              and int((deg[mino] == 2).sum()) == 2 * (d - 1))
        S2 = all(any(deg[a] == 2 and deg[[x for x in nb[a] if x != b][0]] == 3 for a in nb[b]) for b in mino)
        P2 = set()
        for k in range(n):
            for x, y in itertools.combinations(nb[k], 2):
                P2.add((min(x, y), max(x, y)))
        per_site = np.zeros(n, int)
        for x, y in P2:
            per_site[x] += 1; per_site[y] += 1
        ok_counts = (n == (5 * d * d - 2 * d - 1) // 2 and len(edges) == 3 * d * d - 2 * d - 1 and len(maj) == (3 * d * d - 2 * d + 1) // 2
                     and len(mino) == d * d - 1 and len(P2) == (9 * d * d - 10 * d - 1) // 2)
        # local rule of Table (S16), field 3/8: g on every edge from the degrees, then the site gaps
        g = {}
        bad = 0
        for (u, v) in edges:
            a, b = (u, v) if eta[u] == 1 else (v, u)
            oa = [deg[x] for x in nb[a] if x != b]
            ob = sorted(deg[x] for x in nb[b] if x != a)
            if deg[a] == 1 and deg[b] == 3:
                val = Fr(1, 2)
            elif deg[a] == 2 and oa == [2] and deg[b] == 2:
                val = Fr(9, 26)
            elif deg[a] == 2 and oa == [3] and deg[b] == 2:
                val = Fr(6, 13)
            elif deg[a] == 2 and oa == [2] and deg[b] == 3 and ob in ([2, 2], [1, 2]):
                val = Fr(3, 13)
            elif deg[a] == 2 and oa == [3] and deg[b] == 3 and ob == [2, 2]:
                val = Fr(9, 26)
            elif deg[a] == 2 and oa == [3] and deg[b] == 3 and ob == [1, 2]:
                val = Fr(1, 13)
            else:
                bad += 1; val = Fr(0)
            g[(a, b)] = val
        s = []
        for i in range(n):
            tot = sum(g[(i, b)] if eta[i] == 1 else g[(b, i)] for b in nb[i])
            s.append(Fr(3, 4) - tot if eta[i] == 1 else tot - Fr(3, 4))
        print("d=%2d n=%3d edges=%3d |P2|=%3d counts ok=%s (S1)=%s (S2)=%s max pairs/site=%d | rule: edges outside the 7 types=%d, max|g|=%s, min site gap=%s, set of gaps=%s" % (
            d, n, len(edges), len(P2), ok_counts, S1, S2, per_site.max(), bad, max(g.values()), min(s), sorted(set(s))))
        if d in (3, 5, 7):
            G = json.load(open(ROOT + "/rigor/code/graphs/hh_d%d.json" % d))
            import networkx as nx
            A = nx.Graph(); A.add_edges_from(edges); Bg = nx.Graph(); Bg.add_edges_from([tuple(e) for e in G["edges"]])
            print("      isomorphic to the stored graph hh_d%d.json: %s ; stored n_up/n_down = %s/%s" % (d, nx.is_isomorphic(A, Bg), G["n_up"], G["n_down"]))

if "B" in PARTS:
    print("\n== B. contour bound at n = 19, all 2^19 - 1 sets (units of Jz) ==")
    n, edges, eta, idx = heavy_hex(3)
    X = np.arange(1, 2 ** n, dtype=np.int64)
    bnd = np.zeros(len(X), int)
    for (i, j) in edges:
        bnd += ((X >> i) ^ (X >> j)) & 1
    a = np.zeros(len(X), int); b = np.zeros(len(X), int)
    for i in range(n):
        if eta[i] == 1:
            a += (X >> i) & 1
        else:
            b += (X >> i) & 1
    size = a + b
    for B in (Fr(1, 8), Fr(1, 4), Fr(7, 20), Fr(3, 8), Fr(13, 32), Fr(7, 16), Fr(1, 2), Fr(0)):
        cost = 0.5 * bnd + 2 * float(B) * (a - b)
        ratio = cost / size
        k = int(np.argmin(ratio))
        gam = min(2 * B / 13, (1 - 2 * B) / 3)
        print("B=%-6s exact min cost/|D| = %.6f (|D|=%d, boundary %d)  bound gamma(B) = %.6f  violated: %s" % (
            B, ratio[k], size[k], bnd[k], float(gam), bool(ratio[k] < float(gam) - 1e-12)))
    bal = a == b
    r = 0.5 * bnd[bal] / size[bal]
    k = int(np.argmin(r))
    print("sector (a = b): %d sets, min (1/2)|dD|/|D| = %.6f = 3/28? %s (|D|=%d, boundary %d) -> classical crossing at mu = -%.6f Jz" % (
        int(bal.sum()), r[k], abs(r[k] - 3 / 28) < 1e-12, size[bal][k], bnd[bal][k], r[k] / 2))
    # tilted classical parts of Sec. S16 (field 3/8): exact windows in which Neel is the unique minimizer
    P2 = set(); nbr = [[] for _ in range(n)]
    for u, v in edges:
        nbr[u].append(v); nbr[v].append(u)
    for k in range(n):
        for x, y in itertools.combinations(nbr[k], 2):
            P2.add((min(x, y), max(x, y)))
    pairflip = np.zeros(len(X), int)          # number of P2 pairs with exactly one end in D (Z_iZ_j changes sign)
    for (i, j) in P2:
        pairflip += ((X >> i) ^ (X >> j)) & 1
    base = 0.5 * bnd + 0.75 * (a - b)         # cost at B = 3/8, no tilt
    # m_s tilt: + 2 t |D| ; C_zz tilt: -t ZZ on edges -> -2 t * boundary ; C_2 tilt: -t Z_iZ_j on P2 (Neel value +1) -> +2 t * pairflip
    tm = np.max(-base / (2 * size)); tc = np.min(base[bnd > 0] / (2 * bnd[bnd > 0])); t2 = np.max(-base[pairflip > 0] / (2 * pairflip[pairflip > 0]))
    print("Neel unique minimizer of W_O(t) at n=19 iff: m_s t > %.6f (-1/24 = %.6f) ; C_zz t < %.6f (1/16) ; C_2 t > %.6f (-1/32 = %.6f)" % (
        tm, -1 / 24, tc, t2, -1 / 32))
    for (name, extra, ts, gam) in (("m_s", 2.0 * size, (-0.02, -0.028, 0.05), lambda t: 3 / 52 + 2 * t),
                                   ("C_zz", -2.0 * bnd, (0.01, 0.017, -0.05), lambda t: 3 / 52 - 42 / 13 * max(t, 0)),
                                   ("C_2", 2.0 * pairflip, (-0.005, -0.007, 0.05), lambda t: 3 / 52 - 8 * max(-t, 0))):
        for t in ts:
            m = np.min((base + t * extra) / size)
            print("   %-5s t=%+.4f: min cost/|D| = %.6f  gamma_O(t) = %.6f  violated: %s" % (name, t, m, gam(t), bool(m < gam(t) - 1e-12)))

if "C" in PARTS:
    print("\n== C. window of energy and mean magnetization on the 12-site comb (Sec. II) ==")
    n, edges, eta = comb(8)
    M0 = int(eta.sum()); nup0 = (n + M0) // 2
    print("comb: n=%d, M_0=%d, edges=%d" % (n, M0, len(edges)))
    for Jz in (1.6, 4.0):
        sect = {}
        for nup in range(n + 1):
            st = sector_states(n, nup); Z = zvals(st, n)
            off, diag = xxz_sector(n, edges, Jz, st, Z)
            sect[2 * nup - n] = (off, diag, Z @ eta, np.mean([Z[:, i] * Z[:, j] for i, j in edges], axis=0))
        e0 = {M: low1(h, dg) for M, (h, dg, _, _) in sect.items()}
        E0 = e0[M0]
        Bp = min((e0[M] - E0) / (M - M0) for M in e0 if M > M0)
        Bm = max((E0 - e0[M]) / (M0 - M) for M in e0 if M < M0)
        print("Jz=%.1f: E0(sector)=%.6f, E0(-M_0 sector)-E0=%.2e, B_-=%.6f, B_+=%.6f" % (Jz, E0, e0[-M0] - E0, Bm, Bp))
        for de in (1e-3, 1e-2):
            E = E0 + n * de

            mode_now = [None]

            def sector_e0(lam, sgn, which):
                out = {}
                for M, (h, dg, O1, O2) in sect.items():
                    O = O1 if which == "ms" else O2 * len(edges)
                    if mode_now[0] == "sector" and M != M0:
                        continue
                    out[M] = low1(h, dg - sgn * lam * O)
                return out

            def end(which, sgn, mode, M=None):
                S = n if which == "ms" else len(edges)

                def f(loglam):
                    lam = math.exp(loglam)
                    e = sector_e0(lam, sgn, which)
                    if mode == "sector":
                        low = e[M0]
                    elif mode == "none":
                        low = min(e.values())
                    else:        # lower convex envelope of (M', e(M')) at M
                        low = min(e[M1] + (e[M2] - e[M1]) * (M - M1) / (M2 - M1) if M2 > M1 else e[M1]
                                  for M1 in e for M2 in e if M1 <= M <= M2 and (M2 > M1 or M1 == M))
                    return (E - low) / (lam * S)
                mode_now[0] = mode
                return sgn * argmin_log(f)
            for which in (("ms", "czz") if de == 1e-3 else ("ms",)):
                res = []
                for (mode, M) in (("sector", None), ("mean", M0), ("mean", M0 - 0.2), ("none", None)):
                    res.append("[%+.4f, %+.4f]" % (end(which, -1, mode, M), end(which, +1, mode, M)))
                print("   de=%.0e %-3s  sector %s | mean M_0 %s | mean M_0-0.2 %s | no constraint %s" % (de, which, *res))
            # greatest weight of the reversed sector compatible with energy and mean (linear programme over sector weights)
            Ms = sorted(e0)
            for M in (M0, M0 - 0.2):
                c = np.zeros(len(Ms)); c[Ms.index(-M0)] = -1
                r = linprog(c, A_ub=[[e0[m] for m in Ms]], b_ub=[E], A_eq=[[1] * len(Ms), Ms], b_eq=[1, M], bounds=(0, 1))
                bound = (M0 - M) / (2 * M0) + de / (2 * (M0 / n) * Bp)
                print("   de=%.0e mean=%.1f: greatest weight of the reversed sector = %.6f ; bound q/M_0 + de/(2 m_0 B_+) = %.6f ; ok %s" % (
                    de, M, -r.fun, bound, -r.fun <= bound + 1e-9))

if "D" in PARTS:
    print("\n== D. n = 19 patch: sectors, the field 3/8 Jz, tilts (Theorem 4 remarks) ==   t=%.0fs" % (time.time() - T0))
    n, edges, eta, idx = heavy_hex(3)
    M0 = int(eta.sum()); nupN = (n + M0) // 2
    bases = {}
    for nup in range(n + 1):
        st = sector_states(n, nup); bases[nup] = (st, zvals(st, n))
    def sector_levels(Jz, mu_ms=0.0, k=1, only=None):
        out = {}
        for nup, (st, Z) in bases.items():
            if only is not None and nup not in only:
                continue
            off, diag = xxz_sector(n, edges, Jz, st, Z)
            diag = diag - mu_ms * (Z @ eta)
            kk = min(k, len(st))
            w, v = lowest(off, diag, k=kk)
            out[2 * nup - n] = w
        return out
    for (Jz, t) in ((1.6, 0.0), (4.0, 0.0), (4.0, -1 / 40), (4.5, -1 / 40), (1.6, -1 / 40), (6.0, 0.0)):
        lv = sector_levels(Jz, mu_ms=t * Jz)
        e = {M: w[0] for M, w in lv.items()}
        E0 = e[M0]
        Bp = min((e[M] - E0) / (M - M0) for M in e if M > M0)
        Bm = max((E0 - e[M]) / (M0 - M) for M in e if M < M0)
        B = 0.375 * Jz
        dc = min(e[M] - E0 - B * (M - M0) for M in e if M != M0)
        gap = sector_levels(Jz, mu_ms=t * Jz, k=2, only=[nupN])[M0]
        print("Jz=%.1f tilt t=%+.4f: interval of fields (B_-, B_+) = (%.4f, %.4f) Jz ; charge gap at B=3/8 Jz: %+.4f ; sector gap %.4f  -> full-space ground state in the Neel sector: %s" % (
            Jz, t, Bm / Jz, Bp / Jz, dc, gap[1] - gap[0], dc > 0))
    # correlation sum at Jz = 6
    st, Z = bases[nupN]
    off, diag = xxz_sector(n, edges, 6.0, st, Z)
    w, v = lowest(off, diag, k=1)
    p = v[:, 0] ** 2
    zm = p @ Z
    C = (Z * p[:, None]).T @ Z - np.outer(zm, zm)
    print("Jz=6.0: max_i sum_j |<Z_i;Z_j>| = %.4f ; m_s = %.5f" % (np.abs(C).sum(axis=1).max(), float(zm @ eta) / n))

if "E" in PARTS:
    print("\n== E. exact m_s at n = 19 against the reference at n = 57 and 115 (authors' DMRG, public file) ==   t=%.0fs" % (time.time() - T0))
    n, edges, eta, idx = heavy_hex(3)
    M0 = int(eta.sum()); nupN = (n + M0) // 2
    st = sector_states(n, nupN); Z = zvals(st, n)
    ms19 = {}
    keys = ["%.1f" % (1.1 + 0.1 * k) for k in range(50)]
    for k in keys:
        off, diag = xxz_sector(n, edges, float(k), st, Z)
        w, v = lowest(off, diag, k=1)
        ms19[k] = float((v[:, 0] ** 2) @ (Z @ eta)) / n
    for N, cert_from in ((57, 3.5), (115, 4.0)):
        D = json.load(open(ROOT + "/real_data/converted/real_n%d.json" % N))
        Lm = json.load(open(ROOT + "/real_data/converted/lattice_maps.json"))["maps"][str(N)]
        col = Lm["colour_with_node0_as_1"]; vals = sorted(set(col)); maj = max(vals, key=col.count)
        e = np.array([1 if c == maj else -1 for c in col])
        dist = {}
        for k in keys:
            ref = float(np.dot(e, D["dmrg"][k]["z"])) / N
            dist[k] = abs(ms19[k] - ref) / (0.06 * abs(ref))
        kept = [k for k in keys if float(k) >= cert_from - 1e-9]
        print("n=%d: |m_s(19) - reference| / tau: max over the %d certified couplings = %.4f ; at the test couplings %s ; at Jz=1.6: %.3f ; mean over 50 = %.3f" % (
            N, len(kept), max(dist[k] for k in kept), ["%.3f" % dist[k] for k in ("1.1", "1.2", "1.3", "1.4")], dist["1.6"], np.mean(list(dist.values()))))

if "F" in PARTS:
    print("\n== F. Lemma on single sites in a sector: exact window width against the bound ==   t=%.0fs" % (time.time() - T0))
    worst = 1e9; ntest = 0
    systems = [("chain10", 10, [(i, i + 1) for i in range(9)]), ("comb12",) + comb(8)[:2], ("ring10", 10, [(i, (i + 1) % 10) for i in range(10)])]
    for (name, n, edges) in systems:
        for Jz in (1.6, 4.0):
            spread = max(1.0, (1 + Jz) / 2)                 # lambda_max - lambda_min of a bond term 1/4(XX+YY+Jz ZZ)
            degs = np.zeros(n, int)
            for a, b in edges:
                degs[a] += 1; degs[b] += 1
            kappa1 = degs.max() * spread
            for nup in ((2, 3, n // 2, n - 3) if n <= 10 else (2, 3, 8, 9)):
                st = sector_states(n, nup); Z = zvals(st, n)
                off, diag = xxz_sector(n, edges, Jz, st, Z)
                H = off.toarray() + np.diag(diag)
                w, v = np.linalg.eigh(H)
                if w[1] - w[0] < 1e-8:
                    continue                                   # the lemma assumes a unique sector ground state
                m = (2 * nup - n) / n
                for site in (0, n // 2, n - 1):
                    oGS = float((v[:, 0] ** 2) @ Z[:, site])
                    for eps in (0.05, 1.0):
                        E = w[0] + eps
                        def endp(sgn):
                            f = lambda ll: (E - low1(H, -sgn * math.exp(ll) * Z[:, site])) / math.exp(ll)
                            return argmin_log(f, -7.0, 6.0, 12)
                        width = endp(+1) + endp(-1)
                        bound = n / (n - 1) * (1 - m * oGS) * min(1, eps / (2 * kappa1))
                        ntest += 1; worst = min(worst, width / bound)
    print("tests: %d ; smallest exact width / bound = %.3f (must be >= 1)" % (ntest, worst))

if "G" in PARTS:
    print("\n== G. Proposition on unpinned order: ring, S^z = 0 ==   t=%.0fs" % (time.time() - T0))
    for n in (8, 12):
        edges = [(i, (i + 1) % n) for i in range(n)]
        eta = np.array([1 if i % 2 == 0 else -1 for i in range(n)])
        st = sector_states(n, n // 2); Z = zvals(st, n)
        O = Z @ eta
        for Jz in (1.0, 2.5):
            off, diag = xxz_sector(n, edges, Jz, st, Z)
            H = off.toarray() + np.diag(diag)
            w, v = np.linalg.eigh(H); psi = v[:, 0]
            sig2 = float(psi @ (O ** 2 * psi)) / n ** 2
            Kxy = float(psi @ (off @ psi))
            Dn = -16 * Kxy
            phi = O * psi; phi /= np.linalg.norm(phi)
            lhs = float(phi @ (H @ phi)) - w[0]
            print("n=%d Jz=%.1f: <O>=%.1e sigma_n=%.4f D_n=%.4f ; <phi|H-E0|phi>=%.6f vs D_n/(2 n^2 sigma^2)=%.6f" % (
                n, Jz, float(psi @ (O * psi)), math.sqrt(sig2), Dn, lhs, Dn / (2 * n ** 2 * sig2)))
            for frac in (0.25, 0.5, 0.75, 1.0):
                c = frac * math.sqrt(sig2)
                # exact E*_n(c) = sup_mu [E0(H - mu O) - E0 + mu n c]
                g = lambda lm: -(low1(H, -math.exp(lm) * O) - w[0] + math.exp(lm) * n * c)
                Estar = -argmin_log(g, -14.0, 3.0, 18)
                bnd = Dn / (4 * n ** 2 * sig2) * (1 - math.sqrt(max(0.0, 1 - frac ** 2)))
                print("    c/sigma=%.2f: exact E*=%.6f  bound=%.6f  ok=%s" % (frac, Estar, bnd, Estar <= bnd + 1e-9))
print("\ndone in %.0f s" % (time.time() - T0))
