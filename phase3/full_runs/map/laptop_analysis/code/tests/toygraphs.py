"""Toy graphs (n <= 12) in the same JSON schema as code/graphs/hh_d*.json, for unit tests only."""
import json
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, CODE)
from collections import deque  # noqa: E402


# The four helpers below are verbatim copies of code/gen_graphs.py (which imports rustworkx, absent on the VM).
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
    for cut in range(1, n):
        prof.append(sum(1 for (a, b) in edges if min(pos[a], pos[b]) < cut <= max(pos[a], pos[b])))
    return prof


def cycles_of_length(adj, L):
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
    nodes = set(nodes); start = min(nodes); cyc = [start]; prev = None; cur = start
    while True:
        nxt = sorted(v for v in adj[cur] if v in nodes and v != prev)
        nxt = [v for v in nxt if v not in cyc] or [start]
        v = nxt[0]
        if v == start:
            break
        cyc.append(v); prev, cur = cur, v
    return cyc


def from_edges(n, edges, loop_len=None, root=None, order=None):
    edges = sorted(tuple(sorted(e)) for e in edges)
    adj = {i: set() for i in range(n)}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    # two-colouring by BFS
    col = [-1] * n; col[0] = 0; q = [0]
    while q:
        u = q.pop(0)
        for v in adj[u]:
            if col[v] < 0:
                col[v] = 1 - col[u]; q.append(v)
            assert col[v] != col[u]
    c0 = col.count(0); maj = 0 if c0 > n - c0 else 1
    assert c0 != n - c0, "toy graphs need unequal sublattices"
    eta = [1 if col[i] == maj else -1 for i in range(n)]
    # distances
    INF = 10 ** 9
    dist = np.full((n, n), INF, dtype=int)
    for s in range(n):
        dist[s, s] = 0; q = [s]
        while q:
            u = q.pop(0)
            for v in adj[u]:
                if dist[s, v] == INF:
                    dist[s, v] = dist[s, u] + 1; q.append(v)
    nn2 = sorted((i, j) for i in range(n) for j in range(i + 1, n) if dist[i, j] == 2)
    if order is None:
        order = bfs_order(adj, 0 if root is None else root)
    pos = {v: k for k, v in enumerate(order)}
    deg = [len(adj[i]) for i in range(n)]
    ecc = dist.max(axis=1)
    deg3 = [i for i in range(n) if deg[i] == 3] or [i for i in range(n) if deg[i] == max(deg)]
    bulk = min(deg3, key=lambda i: (ecc[i], i))
    deg1 = [i for i in range(n) if deg[i] == 1] or [i for i in range(n) if deg[i] == min(deg)]
    boundary = min(deg1)
    nb = min(adj[bulk])
    loop = None
    if loop_len:
        cyc = [c for c in cycles_of_length(adj, loop_len) if bulk in c] or cycles_of_length(adj, loop_len)
        loop = cycle_in_order(adj, cyc[0])
    n_up = sum(1 for e in eta if e == 1)
    return dict(n=n, d=None, edges=[list(e) for e in edges], nn2=[list(p) for p in nn2], colour=col, eta=eta,
                n_up=n_up, n_down=n - n_up, sz=(2 * n_up - n) / 2, degrees=deg, order=order,
                max_crossing=max(crossings(order, edges)),
                mps=dict(edges=[sorted([pos[a], pos[b]]) for a, b in edges],
                         nn2=[sorted([pos[a], pos[b]]) for a, b in nn2],
                         eta=[eta[order[k]] for k in range(n)],
                         up_init=[1 if eta[order[k]] == 1 else 0 for k in range(n)]),
                local=dict(bulk_site=bulk, boundary_site=boundary, edge=sorted([bulk, nb]), loop=loop))


def ring_pendant(L=10):
    edges = [(i, (i + 1) % L) for i in range(L)] + [(0, L)]
    return from_edges(L + 1, edges, loop_len=L)


def ring_two_pendants(L=10):
    """L-ring with pendants on ring sites 0 and 2 (same colour): sublattices differ by 2, s = 1."""
    edges = [(i, (i + 1) % L) for i in range(L)] + [(0, L), (2, L + 1)]
    return from_edges(L + 2, edges, loop_len=L)


def hh3_prefix(m=12):
    G = json.load(open(os.path.join(CODE, "graphs", "hh_d3.json")))
    keep = G["order"][:m]
    idx = {v: k for k, v in enumerate(keep)}
    edges = [(idx[a], idx[b]) for a, b in G["edges"] if a in idx and b in idx]
    return from_edges(m, edges, loop_len=None)
