"""Check 5 -- independent re-verification of deposited lower-bound certificates (Sec. S4 of the supplement).

Own implementation (numpy, float64), sharing only the certificate FILE FORMAT with the authors' verifier:
  * rebuild H' = 1/4 sum (XX+YY) + Jz/4 sum ZZ - sigma*lam*S*O from the graph file and the task;
  * check that every term of H' is assigned to exactly one cluster that contains it, and that each overlap
    multiplier enters +Y in one cluster and -Y in the other (so sum_k h_k = H' + mu sum_i Z_i exactly);
  * build every cluster operator h_k densely with our own bit embedding and check lambda_min(h_k) >= t_k
    (reporting the smallest margin);
  * recompute E_LB = sum_k t_k - mu * (n_up - n_down) and the certified one-sided bound
    u = (E_up - E_LB)/(lam S), with E_up taken from results_v2.json, and the resulting interval and width.
Also exercises the authors' exact integer routine bareiss_pd against numpy on random matrices.
Reads deposit files only. About half a minute.
"""
import importlib.util
import json
import os
import sys
from fractions import Fraction

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
RIG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "phase3", "full_runs", "rigor"))
JOBDIRS = [os.path.join(RIG, "out_20261031T100015Z", "out", "jobs"), os.path.join(RIG, "out_20261031T073328Z", "out", "jobs")]
RES = json.load(open(os.path.join(RIG, "outputs", "results_v2.json")))


def find(jid):
    for d in JOBDIRS:
        p = os.path.join(d, jid + "_cert.json")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(jid)


def verify(cert_path):
    C = json.load(open(cert_path))
    G = json.load(open(os.path.join(RIG, "code", "graphs", C["graph"])))
    n = G["n"]
    edges = [tuple(sorted(int(v) for v in e)) for e in G["mps"]["edges"]]
    eta = [int(v) for v in G["mps"]["eta"]]
    up = [int(v) for v in G["mps"]["up_init"]]
    task = C["task"]
    Jz, lam, sg = float(Fraction(task["Jz"])), float(Fraction(task["lam"])), int(task["sigma"])
    if task["kind"] == "m_s":
        site = [-sg * lam * eta[i] for i in range(n)]
        S = n
    else:                                 # Czz_bar: field lam * sum ZZ  ==  Jz -> Jz - 4 sigma lam
        Jz = Jz - 4 * sg * lam
        site = [0.0] * n
        S = len(edges)
    terms = []
    for (i, j) in edges:
        terms.append(("xy", (i, j), 0.25))
        terms.append(("zz", (i, j), Jz / 4))
    for i in range(n):
        if site[i] != 0:
            terms.append(("z", (i,), site[i]))
    cl = [list(c) for c in C["clusters"]]
    assert len(C["term_assign"]) == len(terms), "term count differs"
    for (typ, sup, c), k in zip(terms, C["term_assign"]):
        assert set(sup) <= set(cl[k]), "term outside its cluster"
    for i, k in enumerate(C["site_assign"]):
        assert i in cl[k]
    den = 2.0 ** int(C["K"])
    mu = int(C["mu"]) / den
    t = np.array([int(x) for x in C["t"]], dtype=float) / den
    inc = [[] for _ in cl]
    for o, (k, l, O) in enumerate(C["overlaps"]):
        assert set(O) <= set(cl[k]) & set(cl[l])
        inc[k].append((o, +1.0))
        inc[l].append((o, -1.0))
    margins = []
    for k, sk in enumerate(cl):
        m = len(sk)
        pos = {s: p for p, s in enumerate(sk)}
        dim = 2 ** m
        X = np.arange(dim)
        bit = lambda p: (X >> p) & 1
        h = np.zeros((dim, dim))
        for (typ, sup, c), kk in zip(terms, C["term_assign"]):
            if kk != k:
                continue
            if typ == "xy":
                p, q = pos[sup[0]], pos[sup[1]]
                anti = bit(p) != bit(q)
                h[X[anti] ^ (1 << p) ^ (1 << q), X[anti]] += 2 * c
            elif typ == "zz":
                p, q = pos[sup[0]], pos[sup[1]]
                h[X, X] += c * np.where(bit(p) == bit(q), 1.0, -1.0)
            else:
                p = pos[sup[0]]
                h[X, X] += c * np.where(bit(p) == 1, 1.0, -1.0)
        for i in [i for i in range(n) if C["site_assign"][i] == k]:
            h[X, X] += mu * np.where(bit(pos[i]) == 1, 1.0, -1.0)
        for (o, sgn) in inc[k]:
            O = C["overlaps"][o][2]
            op = [pos[s] for s in O]
            rest = [p for p in range(m) if p not in op]
            bases = []
            for cfg in range(2 ** len(rest)):
                b = 0
                for t2, p in enumerate(rest):
                    if (cfg >> t2) & 1:
                        b |= 1 << p
                bases.append(b)
            bases = np.array(bases)

            def emb(a):
                x = np.zeros_like(bases) + bases
                for t2, p in enumerate(op):
                    if (a >> t2) & 1:
                        x = x | (1 << p)
                return x
            for (a, b, v) in C["Y"][o]:
                assert bin(a).count("1") == bin(b).count("1")
                val = sgn * int(v) / den
                xa, xb = emb(a), emb(b)
                h[xa, xb] += val
                if a != b:
                    h[xb, xa] += val
        assert np.allclose(h, h.T)
        pc = np.array([bin(int(x)).count("1") for x in X])
        assert np.all(np.abs(h[pc[:, None] != pc[None, :]]) < 1e-15), "cluster operator does not conserve S^z"
        lmin = min(np.linalg.eigvalsh(h[np.ix_(pc == w, pc == w)])[0] for w in range(m + 1))
        margins.append(lmin - t[k])
    twoS = 2 * sum(up) - n
    E_LB = t.sum() - mu * twoS
    return dict(n=n, kind=task["kind"], Jz=float(Fraction(task["Jz"])), sigma=sg, lam=lam, S=S, E_LB=E_LB,
                E_claim=float(Fraction(C["E_claim"])), min_margin=min(margins), n_clusters=len(cl),
                max_cluster=max(len(c) for c in cl))


rows = {(57, 4.0, "m_s"), (57, 3.4, "Czz_bar"), (115, 6.0, "m_s"), (57, 6.0, "Czz_bar")}
allok = True
for r in RES["rows"]:
    key = (r["n"], r["Jz"], r["label"])
    if key not in rows:
        continue
    us = {}
    for s in "+-":
        b = r["sides"][s]["best"]
        jid = b["src"].split(":", 1)[1]
        v = verify(find(jid))
        u = (r["E_up"] - v["E_LB"]) / (v["lam"] * v["S"])
        us[s] = u
        ok = v["min_margin"] >= -1e-9 and abs(v["E_LB"] - v["E_claim"]) < 1e-9 and abs(u - b["u"]) < 1e-8
        allok &= ok
        print("%s n=%3d Jz=%.1f %-8s side %s: %d clusters (<= %d sites)  min[lambda_min(h_k) - t_k] = %+.2e  "
              "E_LB = %.6f (claimed %.6f)  u = %+.6f (deposit %+.6f)  %s" % (
                  jid[:2], key[0], key[1], key[2], s, v["n_clusters"], v["max_cluster"], v["min_margin"], v["E_LB"],
                  v["E_claim"], u, b["u"], "OK" if ok else "PROBLEM"))
    w = us["+"] + us["-"]
    print("      -> certified interval [%.5f, %.5f], width %.5f = %.4f tau (deposit %.4f tau)   [E_up = %.6f, a DMRG-anchored number]" % (
        -us["-"], us["+"], w, w / r["tau"], r["w_over_tau"], r["E_up"]))
print("all re-verified certificates consistent:", allok)

# the authors' integer PD routine against numpy on random symmetric integer matrices
sys.dont_write_bytecode = True          # do not leave a __pycache__ file inside the deposit
spec = importlib.util.spec_from_file_location("verify_exact_copy", os.path.join(RIG, "code", "verify_exact.py"))
ve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ve)
rng = np.random.default_rng(3)
bad = tested = 0
for trial in range(3000):
    m = int(rng.integers(1, 13))
    A = rng.integers(-6, 7, size=(m, m))
    A = A + A.T
    shift = int(rng.integers(-8, 25))
    A = A + shift * np.eye(m, dtype=int)
    ev = np.linalg.eigvalsh(A.astype(float))
    if abs(ev[0]) < 1e-6:
        continue
    tested += 1
    ok, _ = ve.bareiss_pd([list(map(int, row)) for row in A])
    bad += ok != (ev[0] > 0)
print("bareiss_pd vs numpy on %d random symmetric integer matrices: %d disagreements" % (tested, bad))
