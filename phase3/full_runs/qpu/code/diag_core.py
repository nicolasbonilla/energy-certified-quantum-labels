"""Diagnostic (read-only, no submission): for every real backend, every native embedding of the core
(heavy_hex_graph(5) minus its 4 boundary nodes): worst readout error and worst CZ error on the core, number of
broken couplers (error >= 0.5) touching it, and the free-path distance between the two partners of every boundary
node. Prints a compact summary."""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import rustworkx as rx  # noqa: E402
import qpu_lib as ql  # noqa: E402
import qpu_route as qr  # noqa: E402
from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: E402


def main():
    service = QiskitRuntimeService()
    g = ql.graph57()
    B = qr.boundary_nodes(g, 5)
    core = [v for v in range(57) if v not in B]
    idx = {v: k for k, v in enumerate(core)}
    P = rx.PyGraph()
    P.add_nodes_from(core)
    for (i, j) in g["edges"]:
        if i in idx and j in idx:
            P.add_edge(idx[i], idx[j], None)
    res = {}
    for b in service.backends(simulator=False):
        t = b.target
        Gd, twoq = ql.device_graph(t)
        ro = [ql._err(t, "measure", (q,)) for q in range(t.num_qubits)]
        cz_all = [ql.edge_error(t, twoq, a, c) for a, c in Gd.edge_list()]
        rows = []
        for m in rx.vf2_mapping(Gd, P, subgraph=True, induced=False, id_order=False):
            L = [None] * 57
            for ph, k in m.items():
                L[core[k]] = int(ph)
            e_core = [ql.edge_error(t, twoq, L[i], L[j]) for (i, j) in g["edges"] if i in idx and j in idx]
            used = set(x for x in L if x is not None)
            dists = []
            for s in B:
                ps = [j if i == s else i for (i, j) in g["edges"] if s in (i, j)]
                free = set(range(t.num_qubits)) - used
                dist = {L[ps[0]]: 0}
                q = [L[ps[0]]]
                for u in q:
                    for v in Gd.neighbors(u):
                        if v not in dist and (v in free or v == L[ps[1]]):
                            dist[v] = dist[u] + 1
                            q.append(v)
                dists.append(dist.get(L[ps[1]]))
            rows.append(dict(worst_ro=max(ro[L[v]] for v in core), worst_cz=max(e_core),
                             mean_cz=float(np.mean(e_core)), n_broken=int(sum(e >= 0.5 for e in e_core)),
                             dists=dists, img=sorted(used)))
        rows.sort(key=lambda r: (r["n_broken"], r["worst_cz"]))
        c = collections.Counter((r["n_broken"] > 0, r["worst_ro"] <= 0.05, r["worst_cz"] <= 0.05,
                                 all(d == 4 for d in r["dists"])) for r in rows)
        res[b.name] = dict(n_core_embeddings=len(rows),
                           device_ro_median=float(np.median(ro)), device_ro_gt_0p05=int(sum(r > 0.05 for r in ro)),
                           device_cz_median=float(np.median(cz_all)), device_cz_broken=int(sum(e >= 0.5 for e in cz_all)),
                           classes=[[list(k), v] for k, v in c.most_common()],
                           best5=[{k: v for k, v in r.items() if k != "img"} for r in rows[:5]])
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
