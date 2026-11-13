"""theory-theorem4 (R10): the heavy-hex patch family by an explicit formula, its embedding in the infinite
heavy-hex lattice, and the classical (Peierls) part of Theorem 4 for the three tilts.  Exact rational arithmetic.

PART A  geometry
  A1 explicit definition patch(d) == rustworkx.generators.heavy_hex_graph(d) (same node numbering), d = 3..41
  A2 girth (the boundary cells are 10-cycles, the bulk cells 12-cycles)
  A3 embedding in the infinite heavy-hex lattice: bulk = induced sub-lattice, each boundary "cap" = a contracted
     F-S-F path; images are nested (patch d inside patch d+2) with the (1,1) shift
  A4 the coordinate map is 1-Lipschitz, at most 3 sites per cell  ->  |b_x(m)| <= 3 (2m+1)^2 for every d
  A5 local types are a function of (kind, parities, distances to the four sides truncated at 4); every signature
     of d >= 11 already occurs at d = 11
  A6 second-neighbour pairs: counts and the maximal number of pairs per site
PART B  classical part, units Jz = 1, B = 3/8, n_i = 1 iff site i differs from the Neel configuration
  cost_ms(D;t)  = (1/2)|dD| + 2B(a-b) + 2t|D|                 (tilt  -t sum eta_i Z_i)
  cost_zz(D;t)  = ((1-4t)/2)|dD| + 2B(a-b)                    (tilt  -t sum_edges Z_i Z_j)
  cost_2(D;t)   = (1/2)|dD| + 2B(a-b) + 2t|d2 D|              (tilt  -t sum_{second-neighbour pairs} Z_i Z_j)
  B1 the 7-value local rule g_e and the site gaps s_i (certificate), exact, d = 3..41, and on the torus / lattice type
  B2 certificates with tilt: s_i(t) >= 3/52 + 2t ; 3/52 - (42/13) t_+ ; 3/52 - 8 t_-      (exact check)
  B3 n = 19: brute force over all 2^19 sets D: exact site-wise Peierls constants, exact classical thresholds,
     and the operator identity  H_cl - E_Neel = sum_i s_i n_i + sum_e t_e + sum_p u_p  on every configuration
"""
import sys, json
from fractions import Fraction as Fr
from math import lcm
from collections import deque
import numpy as np
import rustworkx as rx
import networkx as nx

OUT = {}


def patch(d):
    """Explicit definition of the patch.  Columns i = 0..d-1, rows j.
    D(i,j), 0<=i,j<=d-1 ; F(i,j), 0<=j<=d-2, joined to D(i,j) and D(i,j+1) ;
    S(i,j), 0<=i<=d-2, 0<=j<=d-2, i+j odd, joined to F(i,j) and F(i+1,j) ;
    caps: C(i,-1) for even i<=d-2, joined to D(i,0), D(i+1,0) ; C(i,d-1) for odd i<=d-2, joined to D(i,d-1), D(i+1,d-1)."""
    assert d % 2 == 1 and d >= 3
    nd, ns, nf = d * d, (d * d - 1) // 2, d * (d - 1)
    D = lambda i, j: i * d + j
    F = lambda i, j: nd + ns + i * (d - 1) + j
    edges, kind, pos = [], {}, {}
    for i in range(d):
        for j in range(d):
            kind[D(i, j)] = "D"; pos[D(i, j)] = (i, j)
        for j in range(d - 1):
            kind[F(i, j)] = "F"; pos[F(i, j)] = (i, j)
            edges += [(D(i, j), F(i, j)), (D(i, j + 1), F(i, j))]
    s = nd
    for i in range(d - 1):
        if i % 2 == 0:
            kind[s] = "C"; pos[s] = (i, -1); edges += [(D(i, 0), s), (D(i + 1, 0), s)]; s += 1
        for j in range(d - 1):
            if (i + j) % 2 == 1:
                kind[s] = "S"; pos[s] = (i, j); edges += [(F(i, j), s), (F(i + 1, j), s)]; s += 1
        if i % 2 == 1:
            kind[s] = "C"; pos[s] = (i, d - 1); edges += [(D(i, d - 1), s), (D(i + 1, d - 1), s)]; s += 1
    assert s == nd + ns
    n = nd + ns + nf
    edges = sorted(tuple(sorted(e)) for e in edges)
    eta = [1 if kind[v] in "DS" else -1 for v in range(n)]          # majority = D and S, minority = F and caps
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    return n, edges, eta, adj, kind, pos


def lattice_key(d, kind, pos, v):
    h = (d - 1) // 2
    i, j = pos[v]
    return ("S" if kind[v] == "C" else kind[v], i - h, j - h)


def lattice_nbrs(key):
    K, I, J = key
    if K == "D":
        return [("F", I, J), ("F", I, J - 1)]
    if K == "F":
        return [("D", I, J), ("D", I, J + 1), ("S", I, J) if (I + J) % 2 else ("S", I - 1, J)]
    assert (I + J) % 2 == 1
    return [("F", I, J), ("F", I + 1, J)]


# 7-value rule (units Jz), keyed by (deg a, degrees of the other neighbours of a, deg b, degrees of the other neighbours of b),
# a = majority end, b = minority end  (print_rule_out.txt of level-theory)
G = {(2, (2,), 2, (2,)): Fr(9, 26), (2, (3,), 2, (2,)): Fr(6, 13), (2, (2,), 3, (2, 2)): Fr(3, 13),
     (2, (2,), 3, (1, 2)): Fr(3, 13), (1, (), 3, (2, 2)): Fr(1, 2), (2, (3,), 3, (2, 2)): Fr(9, 26),
     (2, (3,), 3, (1, 2)): Fr(1, 13)}
B = Fr(3, 8)
GAM = Fr(3, 52)


def edge_type(adj, a, b):
    return (len(adj[a]), tuple(sorted(len(adj[w]) for w in adj[a] if w != b)),
            len(adj[b]), tuple(sorted(len(adj[w]) for w in adj[b] if w != a)))


def flows(n, edges, eta, adj):
    g = {}
    for a, b in edges:
        if eta[a] != 1:
            a, b = b, a
        g[(a, b)] = G[edge_type(adj, a, b)]
    return g


def site_gaps(n, eta, adj, g, scale=Fr(1)):
    """s_a = 2B - scale*sum g (majority), s_b = scale*sum g - 2B (minority)"""
    s = []
    for v in range(n):
        if eta[v] == 1:
            s.append(2 * B - scale * sum((g[(v, w)] for w in adj[v]), Fr(0)))
        else:
            s.append(scale * sum((g[(w, v)] for w in adj[v]), Fr(0)) - 2 * B)
    return s


def pairs2(n, adj):
    P = set()
    for k in range(n):
        for x in adj[k]:
            for y in adj[k]:
                if x < y:
                    P.add((x, y))
    return sorted(P)


def site_type(adj, eta, v):
    return (eta[v], tuple(sorted(edge_type(adj, v, w) if eta[v] == 1 else edge_type(adj, w, v) for w in adj[v])))


def main():
    pr = print
    # ---------------- PART A
    pr("PART A  geometry")
    ok = True
    for d in range(3, 43, 2):
        n, edges, eta, adj, kind, pos = patch(d)
        g = rx.generators.heavy_hex_graph(d)
        E = sorted(tuple(sorted(e)) for e in g.edge_list())
        col = rx.graph_two_color(g); c = [int(col[i]) for i in range(n)]
        maj = 0 if c.count(0) > c.count(1) else 1
        ok &= (g.num_nodes() == n and E == edges and [1 if c[i] == maj else -1 for i in range(n)] == eta)
    pr(f"A1 explicit formula == rustworkx heavy_hex_graph(d), same numbering and same majority colouring, d = 3..41: {ok}")
    OUT["A1_formula_equals_generator_d3_41"] = ok
    for d in (3, 5, 7):
        Gs = json.load(open(f"C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work/phase3/full_runs/map/code/graphs/hh_d{d}.json"))
        n, edges, eta, adj, kind, pos = patch(d)
        same = Gs["n"] == n and [tuple(e) for e in Gs["edges"]] == edges and Gs["eta"] == eta
        pr(f"   stored graph of the paper hh_d{d}.json == formula: {same}")
        ok &= same
    A2 = {}
    for d in (3, 5, 7, 9):
        n, edges, eta, adj, kind, pos = patch(d)
        cyc = sorted(len(c) for c in nx.minimum_cycle_basis(nx.Graph(edges)))
        A2[d] = {L: cyc.count(L) for L in sorted(set(cyc))}
    pr(f"A2 lengths of a minimum cycle basis {{length: count}}: {A2}   (infinite heavy-hex lattice: all 12)")
    OUT["A2_cycle_lengths"] = {str(k): v for k, v in A2.items()}
    keysets = {}
    okA3 = True
    for d in range(3, 25, 2):
        n, edges, eta, adj, kind, pos = patch(d)
        key = [lattice_key(d, kind, pos, v) for v in range(n)]
        okA3 &= len(set(key)) == n and all((k[1] + k[2]) % 2 == 1 for k in key if k[0] == "S")
        inv = {k: v for v, k in enumerate(key)}
        Eset = set(edges)
        for v in range(n):
            if kind[v] == "C":
                # cap: lattice site S(I,J); its patch neighbours are the D sites reached through the two lattice F's, which are not in the patch
                viaF = [f for f in lattice_nbrs(key[v])]
                tgt = set()
                for f in viaF:
                    okA3 &= f not in inv
                    tgt |= {inv[x] for x in lattice_nbrs(f) if x in inv and x != key[v]}
                okA3 &= tgt == set(adj[v])
            else:
                lat = {inv[x] for x in lattice_nbrs(key[v]) if x in inv and kind[inv[x]] != "C"}
                okA3 &= lat == {w for w in adj[v] if kind[w] != "C"}
        keysets[d] = set(key)
    nested = all(keysets[d] <= keysets[d + 2] for d in range(3, 23, 2))
    pr(f"A3 embedding in the infinite lattice (bulk induced, caps = contracted F-S-F paths), d = 3..23: {okA3};  nested images: {nested}")
    OUT["A3_embedding_ok"] = bool(okA3); OUT["A3_nested"] = bool(nested)
    okA4 = True; worst = Fr(0)
    for d in range(3, 17, 2):
        n, edges, eta, adj, kind, pos = patch(d)
        okA4 &= all(max(abs(pos[a][0] - pos[b][0]), abs(pos[a][1] - pos[b][1])) <= 1 for a, b in edges)
        cells = {}
        for v in range(n):
            cells[pos[v]] = cells.get(pos[v], 0) + 1
        okA4 &= max(cells.values()) <= 3
        for x in range(n):
            dist = {x: 0}; q = deque([x])
            while q:
                u = q.popleft()
                for w in adj[u]:
                    if w not in dist:
                        dist[w] = dist[u] + 1; q.append(w)
            cnt = {}
            for v, m in dist.items():
                cnt[m] = cnt.get(m, 0) + 1
            tot = 0
            for m in range(0, max(cnt) + 1):
                tot += cnt.get(m, 0)
                okA4 &= tot <= 3 * (2 * m + 1) ** 2
                if m >= 1:
                    worst = max(worst, Fr(tot, m * m))
    pr(f"A4 coordinate map 1-Lipschitz, <= 3 sites per cell, |b_x(m)| <= 3(2m+1)^2 (d = 3..15): {okA4};  observed max |b_x(m)|/m^2 = {worst} ~ {float(worst):.3f}")
    OUT["A4_ball_growth_ok"] = bool(okA4); OUT["A4_max_ball_over_m2"] = str(worst)
    T = 4
    sig2type = {}; okA5 = True; sigs = {}; types = {}
    for d in range(3, 27, 2):
        n, edges, eta, adj, kind, pos = patch(d)
        sigs[d] = set(); types[d] = set()
        for v in range(n):
            i, j = pos[v]
            sg = (kind[v], i % 2, j % 2, min(i, T), min(d - 1 - i, T), min(j + 1, T), min(d - 1 - j, T))
            ty = site_type(adj, eta, v)
            sigs[d].add(sg); types[d].add(ty)
            if d >= 11:
                okA5 &= sig2type.setdefault(sg, ty) == ty
    okA5 &= all(sigs[d] <= sigs[11] for d in range(11, 27, 2))
    pr(f"A5 for d >= 11 the local type is a function of the signature and every signature occurs at d = 11 (d = 11..25): {okA5}")
    pr(f"   number of site types: " + ", ".join(f"d={d}: {len(types[d])}" for d in (3, 5, 7, 9, 11, 25)) +
       f";  types(d) == types(5) for d = 5..25: {all(types[d] == types[5] for d in range(5, 27, 2))};  types(3) subset of types(5)? {types[3] <= types[5]}"
       f" (|types(3) minus types(5)| = {len(types[3] - types[5])})")
    OUT["A5_types_from_signature"] = bool(okA5); OUT["A5_ntypes"] = {str(d): len(types[d]) for d in types}
    A6 = {}
    for d in (3, 5, 7, 9, 11):
        n, edges, eta, adj, kind, pos = patch(d)
        P = pairs2(n, adj)
        deg2 = [0] * n
        for x, y in P:
            deg2[x] += 1; deg2[y] += 1
        same_sub = all(eta[x] == eta[y] for x, y in P)
        A6[d] = dict(n=n, edges=len(edges), pairs2=len(P), max_pairs_per_site=max(deg2), same_sublattice=same_sub,
                     n_over_E=str(Fr(n, len(edges))), n_over_P2=str(Fr(n, len(P))))
    pr(f"A6 second-neighbour pairs: {A6}")
    OUT["A6_pairs"] = {str(k): v for k, v in A6.items()}

    # ---------------- PART B
    pr("\nPART B  classical part (units Jz = 1, B = 3/8)")
    okB1 = True; mins = {}
    tz = [Fr(1, 100), Fr(1, 60)]; t2 = [Fr(1, 200), Fr(1, 150)]
    okB2 = True; exact_min = {}
    for d in list(range(3, 23, 2)) + [25, 31, 41]:
        n, edges, eta, adj, kind, pos = patch(d)
        g = flows(n, edges, eta, adj)
        okB1 &= all(abs(x) <= Fr(1, 2) for x in g.values())
        s = site_gaps(n, eta, adj, g)
        mins[d] = min(s); okB1 &= min(s) >= GAM
        # C_zz tilt, t > 0: w_e = (1-4t)/2, g' = (1-4t) g
        for t in tz:
            sc = 1 - 4 * t
            s1 = site_gaps(n, eta, adj, g, sc)
            okB2 &= min(s1) >= GAM - Fr(42, 13) * t and all(abs(sc * x) <= sc / 2 for x in g.values())
            exact_min[("zz", str(t), d)] = min(s1)
        # C_2 tilt, t < 0: s_i - 2|t| deg2(i)
        P = pairs2(n, adj); deg2 = [0] * n
        for x, y in P:
            deg2[x] += 1; deg2[y] += 1
        for t in t2:
            s2 = [s[v] - 2 * t * deg2[v] for v in range(n)]
            okB2 &= min(s2) >= GAM - 8 * t
            exact_min[("c2", str(t), d)] = min(s2)
    pr(f"B1 rule |g_e| <= 1/2 and site gaps s_i >= 3/52 on d = 3..21, 25, 31, 41: {okB1};  min_i s_i = {sorted(set(str(v) for v in mins.values()))}")
    # torus / infinite lattice: every edge is of the bulk type
    gb = G[(2, (3,), 3, (2, 2))]
    pr(f"   bulk type (torus, infinite lattice): g = {gb}; majority s = 2B - 2g = {2*B - 2*gb}; minority s = 3g - 2B = {3*gb - 2*B}")
    pr(f"B2 tilted certificates: C_zz, t in {[str(x) for x in tz]}: min_i s_i(t) >= 3/52 - (42/13) t ; C_2, t = -{[str(x) for x in t2]}: min_i s_i(t) >= 3/52 - 8|t| : {okB2}")
    pr("   exact min_i s_i(t) at d = 5: " + ", ".join(f"{k[0]} t={k[1]}: {v} (bound {GAM - (Fr(42,13) if k[0]=='zz' else 8) * Fr(k[1])})" for k, v in exact_min.items() if k[2] == 5))
    OUT["B1_ok"] = bool(okB1); OUT["B2_ok"] = bool(okB2)

    # B3 brute force at n = 19
    n, edges, eta, adj, kind, pos = patch(3)
    P = pairs2(n, adj)
    cfg = np.arange(1 << n, dtype=np.int64)
    bits = ((cfg[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int64)          # n_i
    size = bits.sum(1)
    cut = np.zeros(1 << n, dtype=np.int64)
    for a, b in edges:
        cut += bits[:, a] ^ bits[:, b]
    cut2 = np.zeros(1 << n, dtype=np.int64)
    for a, b in P:
        cut2 += bits[:, a] ^ bits[:, b]
    amb = (bits * np.array(eta)[None, :]).sum(1)                                    # a - b
    nz = size > 0

    def min_ratio(c_cut, c_amb, c_size, c_cut2):
        """exact min over nonempty D of [c_cut*cut + c_amb*(a-b) + c_size*|D| + c_cut2*cut2] / |D|"""
        L = lcm(c_cut.denominator, c_amb.denominator, c_size.denominator, c_cut2.denominator)
        val = int(c_cut * L) * cut + int(c_amb * L) * amb + int(c_size * L) * size + int(c_cut2 * L) * cut2
        best = None
        for k in range(1, n + 1):
            m = int(val[size == k].min())
            r = Fr(m, L * k)
            best = r if best is None or r < best else best
        return best

    pr("B3 n = 19, all 2^19 sets D: exact site-wise Peierls constant  min_D cost(D)/|D|  against the certificate bound")
    rows = []
    for t in (Fr(0), Fr(1, 100), Fr(-1, 100), Fr(-1, 40)):
        ex = min_ratio(Fr(1, 2), 2 * B, 2 * t, Fr(0)); cert = GAM + 2 * t
        rows.append(("m_s", t, ex, cert)); assert ex >= cert
    for t in (Fr(1, 100), Fr(1, 60), Fr(-1, 20)):
        ex = min_ratio((1 - 4 * t) / 2, 2 * B, Fr(0), Fr(0)); cert = GAM - Fr(42, 13) * max(t, 0)
        rows.append(("C_zz", t, ex, cert)); assert ex >= cert
    for t in (Fr(1, 200), Fr(-1, 200), Fr(-1, 150)):
        ex = min_ratio(Fr(1, 2), 2 * B, Fr(0), 2 * t); cert = GAM - 8 * max(-t, 0)
        rows.append(("C_2", t, ex, cert)); assert ex >= cert
    for lab, t, ex, cert in rows:
        pr(f"   {lab:5s} t = {str(t):>6}: exact {str(ex):>9} ~ {float(ex):+.5f}   certificate bound {str(cert):>9} ~ {float(cert):+.5f}")
    OUT["B3_rows"] = [(lab, str(t), str(ex), str(cert)) for lab, t, ex, cert in rows]
    # exact classical thresholds at n = 19 (Neel unique minimiser iff all costs > 0)
    base = Fr(1, 2) * 1  # cost0 = cut/2 + 2B(a-b), in units 1/8: 4 cut + 6 (a-b)
    c0 = 4 * cut + 6 * amb                                                          # 8 * cost0  (B = 3/8)
    assert c0[nz].min() > 0
    # m_s: cost = c0/8 + 2 t |D| > 0  <=>  t > - min c0/(16|D|)
    t_ms = -min(Fr(int(c0[size == k].min()), 16 * k) for k in range(1, n + 1))
    # C_zz: cost = c0/8 - 2 t cut > 0 <=> t < min over cut>0 of c0/(16 cut)
    m = nz & (cut > 0)
    r = c0[m] / (16.0 * cut[m]); i0 = int(np.argmin(r)); t_zz = Fr(int(c0[m][i0]), 16 * int(cut[m][i0]))
    assert np.all(c0[m] * t_zz.denominator >= 16 * cut[m] * t_zz.numerator)
    # C_2: cost = c0/8 + 2 t cut2 > 0 for t < 0 <=> t > - min over cut2>0 of c0/(16 cut2)
    m2 = nz & (cut2 > 0)
    r2 = c0[m2] / (16.0 * cut2[m2]); i2 = int(np.argmin(r2)); t_c2 = -Fr(int(c0[m2][i2]), 16 * int(cut2[m2][i2]))
    assert np.all(c0[m2] * (-t_c2).denominator >= 16 * cut2[m2] * (-t_c2).numerator)
    pr(f"   exact classical windows at n = 19 (B = 3/8): m_s: t > {t_ms} ; C_zz: t < {t_zz} ; C_2: t > {t_c2}"
       f"   [certificate windows: t > -3/104 ; t < 1/56 ; t > -3/416]")
    OUT["B3_classical_windows_n19"] = dict(ms_lower=str(t_ms), zz_upper=str(t_zz), c2_lower=str(t_c2))
    # operator identity on every configuration, for one tilt of each kind (floating point, tolerance 1e-12)
    g = flows(n, edges, eta, adj); s0 = site_gaps(n, eta, adj, g)
    deg2 = [0] * n
    for x, y in P:
        deg2[x] += 1; deg2[y] += 1
    okid = True
    etaA = np.array(eta)
    for lab, t in (("m_s", Fr(-1, 100)), ("C_zz", Fr(1, 100)), ("C_zz", Fr(-1, 20)), ("C_2", Fr(1, 200)), ("C_2", Fr(-1, 200))):
        if lab == "m_s":
            w = Fr(1, 2); sc = Fr(1); s = [x + 2 * t for x in s0]; lhs = 0.5 * cut + 0.75 * amb + 2 * float(t) * size; extra = 0.0
        elif lab == "C_zz":
            w = (1 - 4 * t) / 2; sc = (1 - 4 * t) if t > 0 else Fr(1); s = site_gaps(n, eta, adj, g, sc)
            lhs = float(w) * cut + 0.75 * amb; extra = 0.0
        else:
            w = Fr(1, 2); sc = Fr(1)
            lhs = 0.5 * cut + 0.75 * amb + 2 * float(t) * cut2
            if t >= 0:
                s = list(s0); extra = 2 * float(t) * cut2                                  # u_p = 2t (n_i + n_j - 2 n_i n_j) >= 0
            else:
                s = [s0[v] + 2 * t * deg2[v] for v in range(n)]                            # -2|t|(n_i+n_j) into the site terms
                both = np.zeros(1 << n)
                for a, b in P:
                    both += bits[:, a] * bits[:, b]
                extra = 4 * float(-t) * both                                               # u_p = 4|t| n_i n_j >= 0
        rhs = (bits * np.array([float(x) for x in s])[None, :]).sum(1) + extra
        tmin = np.inf
        for (a, b), ge in g.items():
            ge = float(sc * ge)
            te = (float(w) + ge) * bits[:, a] * (1 - bits[:, b]) + (float(w) - ge) * bits[:, b] * (1 - bits[:, a])
            tmin = min(tmin, te.min()); rhs = rhs + te
        err = np.abs(lhs - rhs).max()
        okid &= err < 1e-12 and tmin >= -1e-15 and min(s) > 0
        pr(f"   identity {lab:5s} t = {str(t):>6}: max |lhs - rhs| = {err:.1e}, min t_e = {tmin:.3f}, min_i s_i = {min(s)}")
    OUT["B3_identity_ok"] = bool(okid)
    json.dump(OUT, open("geometry_peierls_out.json", "w"), indent=1)
    pr("\nall checks passed:", all(v for k, v in OUT.items() if isinstance(v, bool)))


if __name__ == "__main__":
    main()
