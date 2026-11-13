"""Laptop only: generate the heavy-hex graphs of the witness pilot and write them as JSON.

Graph: rustworkx.generators.heavy_hex_graph(d) (rustworkx 0.14.2), d = 3, 5, 7 (n = 19, 57, 115).
Written once, before the DECLARATION is hashed; the JSON files are inputs of every later step.

Contents of graphs/hh_d<d>.json:
  n, d, edges (graph labels, i < j), colour (two-colouring), eta (+1 on the majority colour), n_up/n_down of the
  Neel sector, s = Sz_tot, second-neighbour pairs (graph distance 2), degrees, the BFS order used as MPS order
  (order[k] = graph node at MPS site k), the MPS-index versions of edges / pairs / eta, the cut-crossing profile,
  12-cycles (heavy-hex cells), and the deterministic choice of local-label operators.
"""
import json, sys, itertools, hashlib
from collections import deque
import numpy as np
import rustworkx as rx


def bfs_order(adj, root):
    seen = {root}; order = [root]; q = deque([root])
    while q:
        u = q.popleft()
        for v in sorted(adj[u]):
            if v not in seen:
                seen.add(v); order.append(v); q.append(v)
    return order


def crossings(order, edges):
    pos = {v: k for k, v in enumerate(order)}
    n = len(order)
    prof = []
    for cut in range(1, n):          # cut between MPS sites cut-1 and cut
        prof.append(sum(1 for (a, b) in edges if min(pos[a], pos[b]) < cut <= max(pos[a], pos[b])))
    return prof


def cycles_of_length(adj, L):
    """All simple cycles of length L, as sorted node tuples (brute-force DFS, fine for n <= 115, L = 12)."""
    n = len(adj); found = set()
    for s in range(n):
        stack = [(s, [s])]
        while stack:
            u, path = stack.pop()
            if len(path) == L:
                if s in adj[u]:
                    found.add(tuple(sorted(path)))
                continue
            for v in adj[u]:
                if v > s and v not in path:
                    stack.append((v, path + [v]))
    return sorted(found)


def cycle_in_order(adj, nodes):
    """Return the cycle nodes in cyclic order (starting from the smallest)."""
    nodes = set(nodes); start = min(nodes); cyc = [start]; prev = None; cur = start
    while True:
        nxt = sorted(v for v in adj[cur] if v in nodes and v != prev)
        nxt = [v for v in nxt if v not in cyc] or [start]
        v = nxt[0]
        if v == start:
            break
        cyc.append(v); prev, cur = cur, v
    return cyc


def build(d):
    g = rx.generators.heavy_hex_graph(d)
    n = g.num_nodes()
    edges = sorted(tuple(sorted(e)) for e in g.edge_list())
    adj = {i: set() for i in range(n)}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    col = rx.graph_two_color(g)
    assert col is not None, "not bipartite"
    colour = [int(col[i]) for i in range(n)]
    for a, b in edges:
        assert colour[a] != colour[b]
    c0 = colour.count(0); c1 = n - c0
    maj = 0 if c0 > c1 else 1
    eta = [1 if colour[i] == maj else -1 for i in range(n)]
    n_up = max(c0, c1); n_down = min(c0, c1)
    dist = np.array(rx.distance_matrix(g), dtype=int)
    nn2 = sorted((i, j) for i in range(n) for j in range(i + 1, n) if dist[i, j] == 2)
    deg = [len(adj[i]) for i in range(n)]
    # BFS order: root minimising (max crossing, sum of crossings), ties -> smallest root
    best = None
    for r in range(n):
        o = bfs_order(adj, r); prof = crossings(o, edges)
        key = (max(prof), sum(prof), r)
        if best is None or key < best[0]:
            best = (key, o, prof)
    (mx, sm, root), order, prof = best
    prof0 = crossings(list(range(n)), edges)
    mx_root0 = max(crossings(bfs_order(adj, 0), edges))   # STEP0's ordering (BFS from node 0)
    pos = {v: k for k, v in enumerate(order)}
    # local-label choices (deterministic)
    ecc = dist.max(axis=1)
    deg3 = [i for i in range(n) if deg[i] == 3]
    bulk = min(deg3, key=lambda i: (ecc[i], i))
    deg1 = [i for i in range(n) if deg[i] == 1]
    boundary = min(deg1)
    edge_loc = (bulk, min(adj[bulk])) if bulk < min(adj[bulk]) else (min(adj[bulk]), bulk)
    loops = cycles_of_length(adj, 12)
    loops_bulk = [c for c in loops if bulk in c]
    loop_loc = cycle_in_order(adj, loops_bulk[0]) if loops_bulk else None
    out = dict(
        generator=f"rustworkx.generators.heavy_hex_graph({d})", rustworkx=rx.__version__,
        d=d, n=n, n_edges=len(edges), n_nn2=len(nn2), n_czz_outputs=len(edges) + len(nn2),
        edges=[list(e) for e in edges], nn2=[list(p) for p in nn2], colour=colour, majority_colour=maj,
        eta=eta, n_up=n_up, n_down=n_down, sz=(n_up - n_down) / 2,
        degrees=deg, degree_counts={str(k): deg.count(k) for k in sorted(set(deg))},
        bfs_root=root, order=order, max_crossing=mx, crossing_profile=prof, max_crossing_index_order=max(prof0),
        max_crossing_bfs_root0=mx_root0,
        mps=dict(
            edges=[sorted([pos[a], pos[b]]) for a, b in edges],
            nn2=[sorted([pos[a], pos[b]]) for a, b in nn2],
            eta=[eta[order[k]] for k in range(n)],
            up_init=[1 if eta[order[k]] == 1 else 0 for k in range(n)],
        ),
        n_loops12=len(loops), loops12=[list(c) for c in loops],
        local=dict(bulk_site=bulk, bulk_ecc=int(ecc[bulk]), boundary_site=boundary, edge=list(edge_loc),
                   loop=loop_loc),
    )
    return out


if __name__ == "__main__":
    outdir = sys.argv[1]
    for d in (3, 5, 7):
        G = build(d)
        p = f"{outdir}/hh_d{d}.json"
        with open(p, "w") as f:
            json.dump(G, f, indent=1)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        print(f"d={d} n={G['n']} up/down={G['n_up']}/{G['n_down']} s={G['sz']} edges={G['n_edges']} nn2={G['n_nn2']} "
              f"sum={G['n_czz_outputs']} deg={G['degree_counts']} root={G['bfs_root']} maxcross={G['max_crossing']} "
              f"(BFS root 0: {G['max_crossing_bfs_root0']}; index order {G['max_crossing_index_order']}) loops12={G['n_loops12']} local={G['local']} sha256={h}")
