"""Laptop toy tests (n <= 12, seconds): lower bound <= exact sector E0, exact verifier accepts the certificate and
rejects a tampered one.  usage: python tests/test_toy.py <workdir>"""
import json
import os
import subprocess
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, CODE)
from ed_sector import sector_ground  # noqa: E402


def colour(n, edges):
    adj = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j)
        adj[j].append(i)
    col = [-1] * n
    col[0] = 0
    q = deque([0])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if col[w] < 0:
                col[w] = 1 - col[u]
                q.append(w)
    assert all(col[i] != col[j] for i, j in edges)
    maj = 0 if col.count(0) >= col.count(1) else 1
    return [1 if c == maj else -1 for c in col], [1 if c == maj else 0 for c in col]


def toy_graph(name, n, edges):
    eta, up = colour(n, edges)
    return dict(n=n, name=name, mps=dict(edges=[list(e) for e in edges], eta=eta, up_init=up))


def hh_piece(m=12):
    G = json.load(open(os.path.join(CODE, "graphs", "hh_d3.json")))
    E = [tuple(e) for e in G["mps"]["edges"]]
    n = G["n"]
    adj = [[] for _ in range(n)]
    for i, j in E:
        adj[i].append(j)
        adj[j].append(i)
    root = next(v for v in range(n) if len(adj[v]) == 3)
    seen, q = [root], deque([root])
    while q and len(seen) < m:
        u = q.popleft()
        for w in adj[u]:
            if w not in seen and len(seen) < m:
                seen.append(w)
                q.append(w)
    lab = {v: k for k, v in enumerate(seen)}
    edges = sorted(tuple(sorted((lab[i], lab[j]))) for i, j in E if i in lab and j in lab)
    return toy_graph("hh_d3_piece12", m, edges)


def main(work):
    os.makedirs(work, exist_ok=True)
    graphs = [hh_piece(12), toy_graph("ring12", 12, [(i, (i + 1) % 12) for i in range(12)]),
              toy_graph("tree10", 10, [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (5, 6), (4, 7), (7, 8), (8, 9)])]
    tasks = [dict(kind="H", Jz="4"), dict(kind="m_s", Jz="4", sigma=-1, lam="0.22"),
             dict(kind="Czz_bar", Jz="4", sigma=1, lam="0.25")]
    modes = sys.argv[2].split(",") if len(sys.argv) > 2 else ["vball2"]
    ok = True
    rows = []
    for G in graphs:
        gp = os.path.join(work, G["name"] + ".json")
        json.dump(G, open(gp, "w"))
        for cm in modes:
            for t in tasks:
                task = dict(t, clusters=cm, K=32, maxiter=200, betas=[10, 100, 1000])
                tag = "%s_%s_%s_%s_%s" % (G["name"], cm, t["kind"], t["Jz"], t.get("lam", 0))
                tp, cp, vp = (os.path.join(work, tag + s) for s in ("_task.json", "_cert.json", "_ver.json"))
                json.dump(task, open(tp, "w"))
                E0 = sector_ground(G, task)[0][0]
                r = subprocess.run([sys.executable, "-I", os.path.join(CODE, "lb_opt.py"), gp, tp, cp],
                                   capture_output=True, text=True, cwd=CODE)
                if r.returncode:
                    print(r.stdout, r.stderr)
                    return 1
                v = subprocess.run([sys.executable, "-I", os.path.join(CODE, "verify_exact.py"), gp, cp, vp],
                                   capture_output=True, text=True)
                V = json.load(open(vp))
                C = json.load(open(cp))
                good = V.get("ok") and V["E_LB_float_floor"] <= E0 + 1e-12
                ok &= bool(good)
                rows.append((tag, E0, C["anderson"], V.get("E_LB_float_floor"), good))
                print("%-48s E0 %11.6f  Anderson %11.6f  certified %11.6f  slack %.2e (%.3f%%) %s" % (
                    tag, E0, C["anderson"], V.get("E_LB_float_floor") or float("nan"),
                    E0 - (V.get("E_LB_float_floor") or 0), 100 * (E0 - (V.get("E_LB_float_floor") or 0)) / abs(E0),
                    "OK" if good else "FAIL"), flush=True)
    # tamper test: lower the cluster bound claim of one cluster -> still valid; raise one t above lambda_min -> reject
    C = json.load(open(cp))
    C["t"][0] += 2 ** 26          # +2^-6 J above the true lambda_min of cluster 0 (margin was 1e-9)
    C["E_claim"] = str(__import__("fractions").Fraction(C["E_claim"]) + __import__("fractions").Fraction(2 ** 26, 2 ** 32))
    json.dump(C, open(cp + ".tampered", "w"))
    v = subprocess.run([sys.executable, "-I", os.path.join(CODE, "verify_exact.py"), gp, cp + ".tampered",
                        vp + ".tampered"], capture_output=True, text=True)
    rej = json.load(open(vp + ".tampered")).get("ok") is False
    print("tampered certificate rejected:", rej)
    ok &= rej
    print("ALL OK" if ok else "SOME FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
