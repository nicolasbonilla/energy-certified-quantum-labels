"""attack_L1.py -- numerical attack of Lemma L1 (field lemma).

Claim attacked: H conserves M = sum_i Z_i; O = sum_i eta_i Z_i commutes with M. If the ground state psi of
H_mu = H - mu O in the sector M = M0 is unique with sector gap D_s, and for some real B
        E0(M') - E0(M0) - B (M' - M0) >= D_c > 0   for every other sector M',
then psi is the unique ground state of H_mu - B M on the whole space, with gap exactly min(D_s, D_c(B)), where
D_c(B) is the minimum of the left-hand side over M' != M0.  The set of admissible B is the interval (B-, B+),
        B- = max_{M' < M0} [E0(M0) - E0(M')]/(M0 - M'),   B+ = min_{M' > M0} [E0(M') - E0(M0)]/(M' - M0).
Part 1 (n = 10, a decorated chain with 7 majority and 3 minority sites): the sector data against a diagonalization
        of the full 2^10-dimensional matrix H_mu - B M built without any sector decomposition, for B inside and
        outside the window; also the clustering constant C_1 of the sector ground state.
Part 2 (n = 19, the heavy-hex patch d = 3): lowest level of all 20 sectors, window of B and best global gap, for
        comparison with the table of reports/level-theory.md (independent code).
Run:  python -B attack_L1.py > attack_L1_out.txt
"""
import time
import numpy as np
import rustworkx as rx
from ed_small import basis, zvals, build, lowest

t0 = time.time()


def sector_levels(n, E, eta, Jz, mu, k_in=2, M0_nup=None):
    """two lowest levels (where the dimension allows) of every S^z sector of H - mu O"""
    lev = {}
    vec = {}
    for nup in range(n + 1):
        st = basis(n, nup)
        if len(st) == 1:
            z = zvals(st, n)[:, 0]
            e = 0.25 * Jz * sum(z[a] * z[b] for a, b in E) - mu * float(np.dot(eta, z))
            lev[2 * nup - n] = [e]
            continue
        K, diag = build(st, n, E, Jz, -mu * np.asarray(eta, float))
        kk = 2 if (len(st) <= 2500 or nup == M0_nup) else 1
        w, v = lowest(K, diag, kk)
        lev[2 * nup - n] = list(w[:kk])
        if nup == M0_nup:
            vec = dict(st=st, psi=v)
    return lev, vec


def window(lev, M0):
    e0 = lev[M0][0]
    Bm = max([(e0 - lev[M][0]) / (M0 - M) for M in lev if M < M0], default=-np.inf)
    Bp = min([(lev[M][0] - e0) / (M - M0) for M in lev if M > M0], default=np.inf)
    return Bm, Bp


def charge_gap(lev, M0, B):
    return min(lev[M][0] - lev[M0][0] - B * (M - M0) for M in lev if M != M0)


def best_gap(lev, M0):
    Bm, Bp = window(lev, M0)
    Ds = lev[M0][1] - lev[M0][0]
    if not Bm < Bp:
        return None, None, Ds
    Bs = np.linspace(Bm, Bp, 4001)
    g = np.array([min(Ds, charge_gap(lev, M0, B)) for B in Bs])
    i = int(np.argmax(g))
    return Bs[i], g[i], Ds


# ---------------------------------------------------------------------------------------------------------------
print("=" * 108)
print("Part 1: decorated chain, n = 10 (minority b1..b3 = sites 0..2; majority a0..a3 = 3..6 and teeth t1..t3 = 7..9)")
n = 10
E = []
for j in range(3):
    E += [(j, 3 + j), (j, 4 + j), (j, 7 + j)]
eta = [-1, -1, -1] + [1] * 7
M0 = 4                                  # Neel sector: 7 up, 3 down
allst = np.arange(1 << n, dtype=np.int64)
zall = zvals(allst, n)
Mall = zall.sum(axis=0)
nfail = 0
ntest = 0
for Jz in (1.6, 4.0):
    for mu_rel in (0.0, -0.04, 0.04, -0.2):
        mu = mu_rel * Jz
        lev, vec = sector_levels(n, E, eta, Jz, mu, M0_nup=7)
        Bm, Bp = window(lev, M0)
        Bs, gbest, Ds = best_gap(lev, M0)
        st, psi = vec["st"], vec["psi"]
        z = zvals(st, n); p = psi * psi
        zz = (z * p) @ z.T
        zi = z @ p
        C1 = float(np.max(np.sum(np.abs(zz - np.outer(zi, zi)), axis=1)))
        print(f"\nJz={Jz} mu={mu_rel:+.2f} Jz: sector gap D_s={Ds:.6f}; window of B: ({Bm:+.6f}, {Bp:+.6f})"
              + (f"; best global gap {gbest:.6f} at B={Bs:+.6f}" if Bs is not None else "; EMPTY window")
              + f"; m_s={float(np.dot(eta, zi))/n:+.4f}; C_1={C1:.4f}")
        tests = []
        if Bm < Bp:
            tests += [Bm + f * (Bp - Bm) for f in (0.02, 0.25, 0.5, 0.75, 0.98)]
        tests += [Bm - 0.05, Bp + 0.05, 0.0]
        for B in tests:
            Kf, df = build(allst, n, E, Jz, -mu * np.asarray(eta, float) - B)
            w, V = np.linalg.eigh(Kf.toarray() + np.diag(df))
            g_full = w[1] - w[0]
            Mgs = float((V[:, 0] ** 2) @ Mall)
            inside = Bm < B < Bp
            Dc = charge_gap(lev, M0, B)
            pred = min(Ds, Dc)
            if inside:
                ok = abs(Mgs - M0) < 1e-8 and abs(g_full - pred) < 1e-8 and abs(w[0] - (lev[M0][0] - B * M0)) < 1e-8
            else:
                # outside the window the sector ground state is not the unique global ground state
                ok = (abs(Mgs - M0) > 1e-6) or g_full < 1e-8
            ntest += 1; nfail += (not ok)
            print(f"    B={B:+.6f} {'inside ' if inside else 'outside'}: full-space ground state has M={Mgs:+.4f}, "
                  f"gap={g_full:.6f}; lemma: min(D_s, D_c)={pred:+.6f}  {'ok' if ok else 'FAIL'}")
print(f"\nPart 1: {ntest} comparisons with the full-space diagonalization, failures: {nfail}")

# ---------------------------------------------------------------------------------------------------------------
print("=" * 108)
print("Part 2: heavy-hex patch d = 3 (n = 19, Neel sector 11 up / 8 down, M0 = 3), all 20 sectors")
g = rx.generators.heavy_hex_graph(3)
n = g.num_nodes()
E = sorted({(min(a, b), max(a, b)) for a, b in g.edge_list()})
col = rx.graph_two_color(g)
c0 = sum(1 for i in range(n) if col[i] == 0)
majc = 0 if c0 > n - c0 else 1
eta = [1 if col[i] == majc else -1 for i in range(n)]
assert sum(1 for e in eta if e == 1) == 11
M0 = 3
for (Jz, mu_rel) in ((1.6, 0.0), (4.0, 0.0), (4.0, -0.04), (4.0, -0.08)):
    t1 = time.time()
    lev, vec = sector_levels(n, E, eta, Jz, mu_rel * Jz, M0_nup=11)
    Bm, Bp = window(lev, M0)
    Bs, gbest, Ds = best_gap(lev, M0)
    st, psi = vec["st"], vec["psi"]
    z = zvals(st, n); p = psi * psi
    zi = z @ p
    zz = (z * p) @ z.T
    C1 = float(np.max(np.sum(np.abs(zz - np.outer(zi, zi)), axis=1)))
    line = f"  Jz={Jz} mu={mu_rel:+.2f} Jz: D_s={Ds:.5f}; window of B/Jz: ({Bm/Jz:+.6f}, {Bp/Jz:+.6f})"
    if Bs is not None:
        B38 = 0.375 * Jz
        g38 = min(Ds, charge_gap(lev, M0, B38)) if Bm < B38 < Bp else float("nan")
        line += f"; best global gap {gbest:.5f} at B={Bs/Jz:.4f} Jz; gap at B=3Jz/8: {g38:.5f}"
    else:
        line += "; EMPTY window (no B makes the sector ground state the global one)"
    line += f"; m_s={float(np.dot(eta, zi))/n:+.4f}; C_1={C1:.4f}   ({time.time()-t1:.0f} s)"
    print(line)
print("  reports/level-theory.md, same quantities: Jz=1.6: D_s 0.962, window (0, 0.365), best 0.772 at 0.123, C_1 1.49;")
print("     Jz=4: D_s 3.061, window (0, 0.425), best 2.551 at 0.106, gap at 3Jz/8 0.401, C_1 0.26;")
print("     Jz=4, mu=-0.04Jz: window (0.241, 0.333), best 0.552; Jz=4, mu=-0.08Jz: none")
print("total %.1f s" % (time.time() - t0))
