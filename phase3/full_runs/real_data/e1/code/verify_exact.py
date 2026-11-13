"""Separate exact verifier of a cluster lower-bound certificate (pure Python integers / Fractions; no numpy, no
import of the optimizer code).  Re-derives the Hamiltonian from the graph JSON and the task, re-builds every
cluster operator h_k from the certificate's multipliers with its own code, and proves h_k - t_k*1 >= 0 EXACTLY
(fraction-free Bareiss elimination on the integer matrix D*(h_k - t_k) of every Sz block: all leading principal
minors > 0).  Then E0(sector) >= sum_k t_k - mu*twoS exactly, because
    sum_k h_k = H + mu*sum_i Z_i   (each multiplier Y_O enters +Y in cluster k and -Y in cluster l; every term once)
and sum_i Z_i = twoS = n_up - n_down on the sector.

usage: python verify_exact.py <graph.json> <cert.json> <out.json>
"""
import hashlib
import json
import sys
import time
from fractions import Fraction
from math import lcm


def popc(x):
    return bin(x).count("1")


def hamiltonian(G, task):
    n = G["n"]
    edges = [tuple(sorted(int(v) for v in e)) for e in G["mps"]["edges"]]
    eta = [int(v) for v in G["mps"]["eta"]]
    Jz, lam, sg = Fraction(task["Jz"]), Fraction(task.get("lam", 0)), int(task.get("sigma", 0))
    site = [Fraction(0)] * n
    if task["kind"] == "m_s":
        site = [-sg * lam * eta[i] for i in range(n)]
    elif task["kind"] == "Czz_bar":
        Jz = Jz - 4 * sg * lam
    elif task["kind"] != "H":
        raise ValueError(task["kind"])
    T = []
    for (i, j) in edges:                     # 1/4 (XX+YY) + Jz/4 ZZ
        T.append(("xy", (i, j), Fraction(1, 4)))
        if Jz != 0:
            T.append(("zz", (i, j), Jz / 4))
    for i in range(n):
        if site[i] != 0:
            T.append(("z", (i,), site[i]))
    up = [int(v) for v in G["mps"]["up_init"]]
    return T, 2 * sum(up) - n, Jz, site


def bareiss_pd(A):
    """True iff the symmetric integer matrix A (list of lists, modified in place) is positive definite."""
    n = len(A)
    prev = 1
    for k in range(n):
        piv = A[k][k]
        if piv <= 0:
            return False, k
        rk = A[k]
        for i in range(k + 1, n):
            ri = A[i]
            aik = ri[k]
            for j in range(k + 1, i + 1):
                v = (piv * ri[j] - aik * rk[j]) // prev
                ri[j] = v
                A[j][i] = v
        prev = piv
    return True, n


def main(gpath, cpath, opath):
    t0 = time.time()
    graw = open(gpath, "rb").read()
    G = json.loads(graw)
    C = json.load(open(cpath))
    assert hashlib.sha256(graw).hexdigest() == C["graph_sha256"], "graph hash differs"
    T, twoS, Jz_eff, site = hamiltonian(G, C["task"])
    n = G["n"]
    cl = [list(c) for c in C["clusters"]]
    sets = [set(c) for c in cl]
    for c in cl:
        assert c == sorted(set(c)) and all(0 <= v < n for v in c)
    # the certificate's spec must match the re-derived Hamiltonian (for the record; we use OUR derivation)
    assert Fraction(C["spec"]["Jz"]) == Jz_eff and [Fraction(s) for s in C["spec"]["site"]] == site
    # assignments
    assert len(C["term_assign"]) == len(T) and len(C["site_assign"]) == n
    for (typ, sup, c), k in zip(T, C["term_assign"]):
        assert set(sup) <= sets[k], "term outside its cluster"
    for i, k in enumerate(C["site_assign"]):
        assert i in sets[k]
    ovs = C["overlaps"]
    for (k, l, O) in ovs:
        assert k < l and sorted(O) == O and set(O) <= sets[k] & sets[l]
    K = int(C["K"])
    den = 2 ** K
    D = den
    for (typ, sup, c) in T:
        D = lcm(D, (2 * c).denominator, c.denominator)
    mu = Fraction(int(C["mu"]), den)
    tks = [Fraction(int(t), den) for t in C["t"]]
    # per-cluster incident overlaps
    inc = [[] for _ in cl]
    for o, (k, l, O) in enumerate(ovs):
        inc[k].append((o, 1))
        inc[l].append((o, -1))
    nblocks, maxblock = 0, 0
    for k, sk in enumerate(cl):
        m = len(sk)
        pos = {s: p for p, s in enumerate(sk)}
        # sparse integer operator: dict (x, y) -> int, value = D*h_k
        H = {}

        def add(x, y, v):
            if v:
                H[(x, y)] = H.get((x, y), 0) + v
        for (typ, sup, c), kk in zip(T, C["term_assign"]):
            if kk != k:
                continue
            ps = [pos[s] for s in sup]
            for x in range(2 ** m):
                if typ == "xy":
                    p, q = ps
                    if ((x >> p) & 1) != ((x >> q) & 1):
                        add(x ^ (1 << p) ^ (1 << q), x, int(2 * c * D))
                elif typ == "zz":
                    p, q = ps
                    zz = (1 if ((x >> p) & 1) == ((x >> q) & 1) else -1)
                    add(x, x, int(c * D) * zz)
                else:
                    add(x, x, int(c * D) * (1 if (x >> ps[0]) & 1 else -1))
        mysites = [pos[i] for i in range(n) if C["site_assign"][i] == k]
        if mu:
            for x in range(2 ** m):
                zsum = sum(1 if (x >> p) & 1 else -1 for p in mysites)
                add(x, x, int(mu * D) * zsum)
        for (o, sgn) in inc[k]:
            O = ovs[o][2]
            op = [pos[s] for s in O]
            rest = [p for p in range(m) if p not in op]
            q = len(O)

            def emb(a, base):
                x = base
                for t2, p in enumerate(op):
                    if (a >> t2) & 1:
                        x |= 1 << p
                return x
            bases = []
            for cfg in range(2 ** len(rest)):
                b = 0
                for t2, p in enumerate(rest):
                    if (cfg >> t2) & 1:
                        b |= 1 << p
                bases.append(b)
            for (a, b, v) in C["Y"][o]:
                assert 0 <= a <= b < 2 ** q and popc(a) == popc(b), "multiplier breaks Sz or index range"
                iv = sgn * int(v) * (D // den)
                for base in bases:
                    xa, xb = emb(a, base), emb(b, base)
                    add(xa, xb, iv)
                    if a != b:
                        add(xb, xa, iv)
        tD = tks[k] * D
        assert tD.denominator == 1
        tD = int(tD)
        # Sz blocks; check that no entry couples different popcounts, then exact PD of D*(h_k - t_k)
        for (x, y), v in H.items():
            assert popc(x) == popc(y) or v == 0, "operator does not conserve Sz"
            assert H.get((y, x), 0) == v, "operator not symmetric"
        for w in range(m + 1):
            I = [x for x in range(2 ** m) if popc(x) == w]
            ix = {x: r for r, x in enumerate(I)}
            A = [[0] * len(I) for _ in I]
            for (x, y), v in H.items():
                if popc(x) == w:
                    A[ix[x]][ix[y]] += v
            for r in range(len(I)):
                A[r][r] -= tD
            ok, where = bareiss_pd(A)
            nblocks += 1
            maxblock = max(maxblock, len(I))
            if not ok:
                res = dict(ok=False, cluster=k, block_popcount=w, failed_at_minor=where, time_s=time.time() - t0)
                json.dump(res, open(opath, "w"), indent=1)
                print("FAILED", res)
                return 1
    E = sum(tks) - mu * twoS
    assert str(E) == C["E_claim"] or Fraction(C["E_claim"]) == E, "claimed bound differs from re-derived one"
    res = dict(ok=True, E_LB_exact=str(E), E_LB_float_floor=float(E) - 1e-12 * max(1.0, abs(float(E))),
               n_clusters=len(cl), n_blocks=nblocks, max_block=maxblock, denominator_bits=D.bit_length() - 1,
               twoS=twoS, task=C["task"], cert_sha256=hashlib.sha256(open(cpath, "rb").read()).hexdigest(),
               time_s=time.time() - t0)
    json.dump(res, open(opath, "w"), indent=1)
    print("VERIFIED E0(sector) >= %.9f  (%d clusters, %d blocks, max block %d, %.1fs)" % (
        res["E_LB_float_floor"], len(cl), nblocks, maxblock, res["time_s"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
