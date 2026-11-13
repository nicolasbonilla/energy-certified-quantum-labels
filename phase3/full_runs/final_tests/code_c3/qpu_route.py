"""ROUTED EMBEDDING (a proposal for the author's decision; nothing here has been run on a device).

heavy_hex_graph(d) has girth 10: one 10-cycle per boundary syndrome node (a syndrome node whose two neighbours are
both data nodes; d = 5: nodes 25, 30, 31, 36). Every IBM heavy-hex coupling graph has girth 12 (checked: fez,
kingston, marrakesh today; FakeBoston, FakeTorino, FakeSherbrooke, ...), so heavy_hex_graph(5) has NO native embedding.

Proposal: embed the core (graph minus the boundary nodes) natively; give every boundary node s a free physical
"home" and route its non-adjacent edge(s) by moving the state of s through free physical qubits that are in |0>
(move(a -> b) = CX(a, b) CX(b, a), exact when b is |0>), applying the same edge gate there and moving it back.
Conventions C1-C6 of qpu_lib are unchanged (site i = virtual qubit i = clbit i, measured at its home L[i]);
ancilla virtual qubits n, n+1, ... carry no site and are not measured.
"""
import numpy as np

import qpu_lib as ql


def boundary_nodes(g, d):
    nd = d * d
    ns = (nd - 1) // 2
    nb = {v: set() for v in range(g["n"])}
    for (i, j) in g["edges"]:
        nb[i].add(j)
        nb[j].add(i)
    return [v for v in range(nd, nd + ns) if all(u < nd for u in nb[v])]


def _bfs_paths(Gd, src, allowed):
    """Shortest paths from src through allowed nodes. Returns dict node -> path (list, src first)."""
    par = {src: None}
    q = [src]
    for u in q:
        for v in Gd.neighbors(u):
            if v not in par and v in allowed:
                par[v] = u
                q.append(v)
    out = {}
    for v in par:
        p = [v]
        while par[p[-1]] is not None:
            p.append(par[p[-1]])
        out[v] = p[::-1]
    return out


def choose_routed_layout(target, g, d=5, faulty_qubits=(), faulty_edges=(), max_embeddings=20000, max_moves=3):
    """Applies _choose with the thresholds READOUT_MAX / CZ_MAX, relaxed x2 then x4 if nothing qualifies."""
    last = None
    for relax in (1, 2, 4):
        try:
            sel = _choose(target, g, d, faulty_qubits, faulty_edges, max_embeddings, max_moves,
                          ql.READOUT_MAX * relax, ql.CZ_MAX * relax)
            sel['relax'] = relax
            return sel
        except RuntimeError as e:
            last = e
    raise last


def _choose(target, g, d, faulty_qubits, faulty_edges, max_embeddings, max_moves, ro_max, cz_max):
    """Routed layout rule: minimise the expected two-qubit error per Trotter step,
    S = sum_native 3 eps(edge) + sum_routed [3 eps(last pair) + 2 * 2 * sum eps(move pairs)] (moves out and back);
    ties by fewer moves, then mean readout error of the 57 homes. Greedy per boundary node (sorted), disjoint homes and
    paths between different boundary nodes."""
    import rustworkx as rx
    Gd, twoq = ql.device_graph(target)
    B = boundary_nodes(g, d)
    core = [v for v in range(g["n"]) if v not in B]
    idx = {v: k for k, v in enumerate(core)}
    P = rx.PyGraph()
    P.add_nodes_from(core)
    for (i, j) in g["edges"]:
        if i in idx and j in idx:
            P.add_edge(idx[i], idx[j], (i, j))
    faulty_q = set(int(x) for x in faulty_qubits)
    faulty_e = set(tuple(sorted(e)) for e in faulty_edges)

    def eps(a, b):
        if tuple(sorted((a, b))) in faulty_e:
            return None
        return ql.edge_error(target, twoq, a, b)

    def ro(q):
        return ql._err(target, "measure", (q,))
    nbr = {s: [j if i == s else i for (i, j) in g["edges"] if s in (i, j)] for s in B}
    best = None
    n_emb = 0
    for m in rx.vf2_mapping(Gd, P, subgraph=True, induced=False, id_order=False):
        n_emb += 1
        if n_emb > max_embeddings:
            break
        L = [None] * g["n"]
        for phys, k in m.items():
            L[core[k]] = int(phys)
        if faulty_q & set(x for x in L if x is not None):
            continue
        if any((ro(L[v]) or 1.0) > ro_max for v in core):
            continue
        S = 0.0
        bad = False
        for (i, j) in g["edges"]:
            if i in idx and j in idx:
                e = eps(L[i], L[j])
                if e is None or e > cz_max:
                    bad = True
                    break
                S += 3 * e
        if bad:
            continue
        used = set(x for x in L if x is not None)
        paths = {}
        moves_total = 0
        for s in B:
            free = set(range(target.num_qubits)) - used - faulty_q
            opt = None
            for h in free:
                r = ro(h)
                if r is None or r > ro_max:
                    continue
                cost, mv, pth = 0.0, 0, {}
                ok = True
                reach = _bfs_paths(Gd, h, free - {h})
                for p in nbr[s]:
                    tgt = L[p]
                    cands = []
                    for y, path in reach.items():
                        if len(path) - 1 > max_moves or tgt not in set(Gd.neighbors(y)):
                            continue
                        e_last = eps(y, tgt)
                        e_mv = [eps(path[t], path[t + 1]) for t in range(len(path) - 1)]
                        if e_last is None or any(x is None for x in e_mv) or max([e_last] + e_mv) > cz_max:
                            continue
                        cands.append((3 * e_last + 4 * sum(e_mv), len(path) - 1, path))
                    if not cands:
                        ok = False
                        break
                    cands.sort(key=lambda t: (t[0], t[1]))
                    c_, k_, path_ = cands[0]
                    cost += c_
                    mv += 2 * k_
                    pth[p] = path_
                if not ok:
                    continue
                key = (cost, mv, r)
                if opt is None or key < opt[0]:
                    opt = (key, h, pth)
            if opt is None:
                bad = True
                break
            (cost, mv, r), h, pth = opt
            L[s] = h
            paths[s] = pth
            used |= {h}
            for pp in pth.values():
                used |= set(pp)
            S += cost
            moves_total += mv
        if bad:
            continue
        mro = float(np.mean([ro(q) for q in L]))
        key = (S, moves_total, mro, tuple(L))
        if best is None or key < best[0]:
            best = (key, list(L), paths)
    if best is None:
        raise RuntimeError("no routed embedding found (%d core mappings tried)" % n_emb)
    (S, moves_total, mro, _), L, paths = best
    anc = []
    for s in sorted(paths):
        for p in sorted(paths[s]):
            for q in paths[s][p][1:]:
                if q not in anc:
                    anc.append(q)
    native = [(i, j) for (i, j) in g["edges"] if Gd.has_edge(L[i], L[j])]
    routed = [(i, j) for (i, j) in g["edges"] if not Gd.has_edge(L[i], L[j])]
    return dict(layout=L, paths={int(s): {int(p): [int(x) for x in v] for p, v in d_.items()}
                                 for s, d_ in paths.items()},
                ancillas=[int(x) for x in anc], boundary=B, score_2q_per_step=S, moves_per_step=moves_total,
                mean_readout_error=mro, n_core_mappings=n_emb, n_native_edges=len(native), routed_edges=routed,
                twoq_gate=twoq)


def routed_krylov_circuit(g, Jz, dt, k, sel, measure=True):
    """Logical circuit on n + n_anc qubits (virtual i < n = site i at its home; virtual n + a = ancilla
    sel['ancillas'][a]); same edge order and edge gate as qpu_lib.krylov_circuit; routed edges by moves into |0>."""
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    n = g["n"]
    anc = sel["ancillas"]
    q = QuantumRegister(n + len(anc), "q")
    c = ClassicalRegister(n, "c")
    qc = QuantumCircuit(q, c, name="krylov_J%.1f_k%d" % (Jz, k))
    L = sel["layout"]
    virt = {L[i]: i for i in range(n)}
    for a, phys in enumerate(anc):
        virt[phys] = n + a
    for i in ql.neel_sites(g):
        qc.x(q[i])
    step = ql.trotter_gates(g, Jz, dt)
    paths = sel["paths"]

    def U(a, b):
        qc.rxx(dt / 2, q[a], q[b])
        qc.ryy(dt / 2, q[a], q[b])
        qc.rzz(Jz * dt / 2, q[a], q[b])

    def move(a, b):          # state of a -> b (b in |0>)
        qc.cx(q[a], q[b])
        qc.cx(q[b], q[a])
    for _ in range(k):
        for (i, j) in step:
            s, p = (i, j) if i in paths else (j, i) if j in paths else (None, None)
            if s is None or len(paths[s][p]) == 1:
                U(i, j)
                continue
            vp = [virt[x] for x in paths[s][p]]
            for t in range(len(vp) - 1):
                move(vp[t], vp[t + 1])
            U(vp[-1], p)
            for t in range(len(vp) - 1, 0, -1):
                move(vp[t], vp[t - 1])
    if measure:
        qc.barrier()
        for i in range(n):
            qc.measure(q[i], c[i])
    return qc


def routed_layout_list(sel):
    return list(sel["layout"]) + list(sel["ancillas"])


def allowed_pairs(g, sel):
    """Physical pairs on which a two-qubit gate is allowed: images of native edges and the routing pairs."""
    L = sel["layout"]
    ok = set()
    for s, d_ in sel["paths"].items():
        for p, path in d_.items():
            for t in range(len(path) - 1):
                ok.add(tuple(sorted((path[t], path[t + 1]))))
            ok.add(tuple(sorted((path[-1], L[int(p)]))))
    B = set(int(s) for s in sel["paths"])
    for (i, j) in g["edges"]:
        if i not in B and j not in B:
            ok.add(tuple(sorted((L[i], L[j]))))
    return ok


def check_isa_routed(isa, g, sel):
    """Convention C5 for the routed layout: initial and final layout = routed_layout_list(sel); 2q gates only on
    allowed_pairs; clbit c <- physical home L[c]; no SWAP."""
    Ll = routed_layout_list(sel)
    L = sel["layout"]
    lay = isa.layout
    init = list(lay.initial_index_layout(filter_ancillas=True))
    fin = list(lay.final_index_layout(filter_ancillas=True))
    assert init == Ll, "initial layout differs"
    assert fin == Ll, "final layout differs (routing permutation)"
    ok = allowed_pairs(g, sel)
    n2q = 0
    meas = {}
    for inst in isa.data:
        nm = inst.operation.name
        qs = [isa.find_bit(q).index for q in inst.qubits]
        assert nm != "swap", "SWAP in ISA circuit"
        if len(qs) == 2 and nm != "barrier":
            assert tuple(sorted(qs)) in ok, "2q gate on a pair outside the declared set: %s" % (qs,)
            n2q += 1
        if nm == "measure":
            meas[isa.find_bit(inst.clbits[0]).index] = qs[0]
    if meas:
        assert sorted(meas) == list(range(g["n"])), "not every clbit measured once"
        for c in range(g["n"]):
            assert meas[c] == L[c], "clbit %d reads physical %d, expected home %d" % (c, meas[c], L[c])
    return dict(n2q=n2q, n_meas=len(meas))
