"""SKQD-type device run on an IBM heavy-hex processor: circuits, layout rule, bit-order conventions, decoding.

Model: H = 1/4 sum_edges (X X + Y Y + Jz Z Z) on rustworkx.generators.heavy_hex_graph(5) (n = 57, 64 edges),
sector 33 up / 24 down (Neel of the two-colouring). Same graph JSON as full_runs/method (graphs/hh_d5.json).

=====================================================================================================================
BIT-ORDER AND LAYOUT CONVENTIONS (DECLARATION.md section 2). Checked by tests/test_bitorder.py (local simulator) and
by the two device checks inside every job (k = 0 Neel circuit and an asymmetric product state).
 C1  Site i = node i of heavy_hex_graph(5) = virtual qubit i of every logical circuit = classical bit i of the
     57-bit register "c". (graph JSON edges are verified equal to rustworkx's at import: graph57()).
 C2  |0> = spin up (Z = +1), |1> = spin down (Z = -1). A measured 1 on clbit i means site i is DOWN.
 C3  Qiskit is little-endian: in a counts string the RIGHT-most character is clbit 0, and the integer value of a shot
     has bit i = clbit i. A configuration is that integer (uint64): bit i = 1 <=> site i down. This is exactly the
     convention of method/code/emu.py and emu2.py ("bit i = 1 <=> node i DOWN"), so device configurations enter the
     method's post-processing without any re-ordering.
 C4  Neel = minority colour (eta = -1, 24 sites) DOWN = X on those 24 virtual qubits; sector = popcount 24.
 C5  Layout: L[i] = physical qubit that carries virtual qubit i (passed as initial_layout, a list indexed by virtual
     qubit). After transpilation check_isa() requires: initial_index_layout == L; final_index_layout == L (no
     routing permutation, no SWAP); every two-qubit gate acts on (L[i], L[j]) with (i, j) a graph edge; every
     measurement writes physical qubit L[c] into clbit c.
 C6  Decoding (decode_bitarray): SamplerV2 BitArray.array has shape (shots, nbytes) uint8 in BIG-endian byte order
     (the LAST byte holds clbits 0..7, least significant bit = clbit 0). config = sum_b a[:, b] << 8*(nbytes-1-b).
     Cross-checked against BitArray.get_int_counts() and get_counts() in the unit test.
 C7  MPS control (noiseless): the same logical gate list (trotter_gates) applied to an MPS in the MPS order of the
     graph JSON (mps site k = node order[k]); sampled with method_copy/emu2.sample_mps, which writes node order[k]
     into bit order[k] with bit 1 = down (same as C3).
=====================================================================================================================

Trotter circuit (declared): one first-order Trotter step of size dt per Krylov step; in every step the three edge
colour classes of method_copy/emu.edge_colouring act in the order 0, 1, 2; every edge gate is
U_e = exp(-i dt/4 (XX + YY + Jz ZZ)) = RXX(dt/2) RYY(dt/2) RZZ(Jz dt/2) (the three factors commute).
Krylov circuit k (k = 1..10) = Neel preparation + k Trotter steps + measurement of all 57 qubits.
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "method_copy"))
import emu   # noqa: E402  (edge_colouring; identical copy of method/code/emu.py)
import emu2  # noqa: E402  (post-processing and sampler; identical copy of method/code/emu2.py)

K = 10
DT57 = {1.2: 0.0569, 1.6: 0.0622, 4.0: 0.0602}           # 2606.15983 Supp. Table 1 (as method/code/fr.py DT[57])
# Asymmetric product state of the bit-order check (declared): X on these sites (12 of 57, both colours).
ASYM_SITES = (0, 1, 2, 3, 9, 14, 25, 30, 37, 44, 50, 56)
READOUT_MAX = 0.05     # layout rule: every embedded qubit with readout error <= this (relaxed in steps if impossible)
CZ_MAX = 0.05          # layout rule: every embedded edge with CZ error <= this


# ----------------------------------------------------------------------------------------------------------- graph
def graph_path(d=5):
    return os.path.join(HERE, "graphs", "hh_d%d.json" % d)


def graph(d=5):
    """emu2 graph dict, after verifying the JSON edges equal rustworkx.heavy_hex_graph(d)."""
    import rustworkx as rx
    with open(graph_path(d), encoding="utf-8") as f:
        G = json.load(f)
    hh = rx.generators.heavy_hex_graph(d)
    e_rx = sorted(tuple(sorted(e)) for e in hh.edge_list())
    e_js = sorted(tuple(sorted(e)) for e in G["edges"])
    assert hh.num_nodes() == G["n"] and e_rx == e_js, "graph JSON differs from rustworkx heavy_hex_graph(%d)" % d
    g = emu2.load_graph(G)
    return g


def graph57():
    return graph(5)


def colouring(g):
    col = emu.edge_colouring(dict(n=g["n"], edges=g["edges"]))
    for v in range(g["n"]):
        cs = [c for e, c in col.items() if v in e]
        assert len(cs) == len(set(cs))
    return col


def trotter_gates(g, Jz, dt):
    """One Trotter step as an ordered list of (i, j) edges (colour 0, then 1, then 2; sorted inside a colour)."""
    col = colouring(g)
    es = sorted(col.items(), key=lambda kv: (kv[1], kv[0]))
    return [(int(e[0]), int(e[1])) for e, c in es]


def edge_unitary(Jz, dt):
    """exp(-i dt/4 (XX + YY + Jz ZZ)) as a 4x4 matrix in the basis |b_i b_j> with index 2*b_i + b_j (b = 1: down).
    In the {up, down} = {|0>, |1>} basis: |00>,|11>: exp(-i Jz dt/4); the |01>,|10> block:
    exp(+i Jz dt/4) [[cos(dt/2), -i sin(dt/2)], [-i sin(dt/2), cos(dt/2)]]."""
    a = np.exp(-1j * Jz * dt / 4)
    b = np.exp(1j * Jz * dt / 4)
    c, s = np.cos(dt / 2), np.sin(dt / 2)
    U = np.zeros((4, 4), complex)
    U[0, 0] = a
    U[3, 3] = a
    U[1, 1] = b * c
    U[2, 2] = b * c
    U[1, 2] = -1j * b * s
    U[2, 1] = -1j * b * s
    return U


def neel_sites(g):
    return [i for i in range(g["n"]) if g["eta"][i] == -1]


def config_int(sites):
    v = 0
    for i in sites:
        v |= 1 << int(i)
    return v


# --------------------------------------------------------------------------------------------------------- circuits
def product_circuit(g, sites, name):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(g["n"], "q")
    c = ClassicalRegister(g["n"], "c")
    qc = QuantumCircuit(q, c, name=name)
    for i in sorted(sites):
        qc.x(q[i])
    qc.barrier()
    for i in range(g["n"]):
        qc.measure(q[i], c[i])
    return qc


def krylov_circuit(g, Jz, dt, k, measure=True):
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    q = QuantumRegister(g["n"], "q")
    c = ClassicalRegister(g["n"], "c")
    qc = QuantumCircuit(q, c, name="krylov_J%.1f_k%d" % (Jz, k))
    for i in neel_sites(g):
        qc.x(q[i])
    step = trotter_gates(g, Jz, dt)
    for _ in range(k):
        for (i, j) in step:
            qc.rxx(dt / 2, q[i], q[j])
            qc.ryy(dt / 2, q[i], q[j])
            qc.rzz(Jz * dt / 2, q[i], q[j])
    if measure:
        qc.barrier()
        for i in range(g["n"]):
            qc.measure(q[i], c[i])
    return qc


def job_circuits(g, Jz_list, k_max=K, checks=True):
    """Ordered list of (tag, logical circuit). Checks first: 'neel' (k = 0) and 'asym'; then Krylov k = 1..k_max per Jz."""
    out = []
    if checks:
        out.append(("neel", product_circuit(g, neel_sites(g), "check_neel_k0")))
        out.append(("asym", product_circuit(g, ASYM_SITES, "check_asym")))
    for Jz in Jz_list:
        for k in range(1, k_max + 1):
            out.append(("J%.1f_k%d" % (Jz, k), krylov_circuit(g, Jz, DT57[round(Jz, 1)], k)))
    return out


# ----------------------------------------------------------------------------------------------------------- layout
def device_graph(target):
    import rustworkx as rx
    nq = target.num_qubits
    G = rx.PyGraph()
    G.add_nodes_from(list(range(nq)))
    seen = set()
    twoq = [nm for nm in target.operation_names if target.operation_from_name(nm).num_qubits == 2
            and nm in ("cz", "ecr", "cx")]
    for nm in twoq:
        for qargs in target[nm]:
            if qargs is None or len(qargs) != 2:
                continue
            e = tuple(sorted(qargs))
            if e not in seen:
                seen.add(e)
                G.add_edge(e[0], e[1], e)
    return G, twoq


def _err(target, name, qargs):
    try:
        p = target[name][qargs]
    except KeyError:
        return None
    return None if p is None else p.error


def edge_error(target, twoq, a, b):
    vals = []
    for nm in twoq:
        for qa in ((a, b), (b, a)):
            e = _err(target, nm, qa)
            if e is not None:
                vals.append(e)
    return min(vals) if vals else None


def choose_layout(target, g, faulty_qubits=(), faulty_edges=(), max_embeddings=200000):
    """Declared layout rule (DECLARATION.md 3.2): among all embeddings of the graph as a (not necessarily induced)
    subgraph of the device coupling graph, keep those with no faulty qubit / edge, every embedded qubit with readout
    error <= READOUT_MAX and every embedded edge with two-qubit error <= CZ_MAX (if none: READOUT_MAX and CZ_MAX are
    doubled, then quadrupled, and the relaxation is recorded); choose the lowest MEAN two-qubit error over the 64
    embedded edges; ties by lower mean readout error, then lexicographically smallest layout. Returns L (list,
    virtual -> physical) and the statistics."""
    import rustworkx as rx
    Gd, twoq = device_graph(target)
    P = rx.PyGraph()
    P.add_nodes_from(list(range(g["n"])))
    for (i, j) in g["edges"]:
        P.add_edge(i, j, (i, j))
    faulty_q = set(int(x) for x in faulty_qubits)
    faulty_e = set(tuple(sorted(e)) for e in faulty_edges)
    cand = []
    n_emb = 0
    for m in rx.vf2_mapping(Gd, P, subgraph=True, induced=False, id_order=False):
        n_emb += 1
        if n_emb > max_embeddings:
            break
        L = [None] * g["n"]
        for phys, virt in m.items():
            L[virt] = int(phys)
        if any(x is None for x in L):
            continue
        ee = [edge_error(target, twoq, L[i], L[j]) for (i, j) in g["edges"]]
        ro = [_err(target, "measure", (L[i],)) for i in range(g["n"])]
        if any(x is None for x in ee) or any(x is None for x in ro):
            continue
        if faulty_q & set(L) or any(tuple(sorted((L[i], L[j]))) in faulty_e for (i, j) in g["edges"]):
            continue
        cand.append((float(np.mean(ee)), float(np.mean(ro)), tuple(L), max(ee), max(ro), ee, ro))
    if not cand:
        raise RuntimeError("no embedding of heavy_hex_graph(5) found (%d mappings tried)" % n_emb)
    for relax in (1, 2, 4):
        ok = [c for c in cand if c[3] <= CZ_MAX * relax and c[4] <= READOUT_MAX * relax]
        if ok:
            break
    ok.sort(key=lambda c: (c[0], c[1], c[2]))
    best = ok[0]
    return dict(layout=list(best[2]), mean_2q_error=best[0], mean_readout_error=best[1], max_2q_error=best[3],
                max_readout_error=best[4], edge_errors=best[5], ro_errors=best[6], n_mappings=n_emb,
                n_candidates=len(cand), n_ok=len(ok), relax=relax, twoq_gate=twoq,
                runner_up_mean_2q=[c[0] for c in ok[1:4]])


# ---------------------------------------------------------------------------------------------------- transpilation
def transpile_isa(circs, backend_or_target, L, seed=20261031, optimization_level=3):
    from qiskit.transpiler import generate_preset_pass_manager
    kw = dict(optimization_level=optimization_level, initial_layout=list(L), seed_transpiler=seed)
    if hasattr(backend_or_target, "target"):
        pm = generate_preset_pass_manager(backend=backend_or_target, **kw)
    else:
        pm = generate_preset_pass_manager(target=backend_or_target, **kw)
    return pm.run(circs)


def check_isa(isa, g, L, logical=None):
    """Convention C5 on one transpiled circuit. Returns a dict of statistics; raises AssertionError on any failure."""
    lay = isa.layout
    assert lay is not None, "no layout attached"
    init = lay.initial_index_layout(filter_ancillas=True)
    fin = lay.final_index_layout(filter_ancillas=True)
    assert list(init) == list(L), "initial layout differs from L"
    assert list(fin) == list(L), "final layout differs from L (routing permutation)"
    phys2virt = {p: v for v, p in enumerate(L)}
    edges = set(tuple(sorted(e)) for e in g["edges"])
    n2q = 0
    n_meas = 0
    ops = {}
    meas_map = {}
    for inst in isa.data:
        nm = inst.operation.name
        ops[nm] = ops.get(nm, 0) + 1
        qs = [isa.find_bit(q).index for q in inst.qubits]
        if nm == "swap":
            raise AssertionError("SWAP in ISA circuit")
        if len(qs) == 2 and nm not in ("barrier",):
            a, b = qs
            assert a in phys2virt and b in phys2virt, "2q gate on an unmapped qubit"
            assert tuple(sorted((phys2virt[a], phys2virt[b]))) in edges, "2q gate on a non-edge"
            n2q += 1
        if nm == "measure":
            cb = isa.find_bit(inst.clbits[0]).index
            meas_map[cb] = qs[0]
            n_meas += 1
    if n_meas:
        assert n_meas == g["n"], "measurements: %d" % n_meas
        for c in range(g["n"]):
            assert meas_map[c] == L[c], "clbit %d reads physical %d, expected %d" % (c, meas_map[c], L[c])
    depth2q = isa.depth(lambda ins: ins.operation.num_qubits == 2 and ins.operation.name != "barrier")
    return dict(n2q=n2q, depth2q=int(depth2q), ops=ops, n_meas=n_meas)


# --------------------------------------------------------------------------------------------------------- decoding
def decode_bitarray(ba):
    """Convention C6: BitArray -> uint64 configurations, one per shot, in shot order."""
    a = np.asarray(ba.array)
    assert a.ndim == 2, a.shape
    nb = a.shape[1]
    assert ba.num_bits <= 64
    out = np.zeros(a.shape[0], dtype=np.uint64)
    for b in range(nb):
        out |= a[:, b].astype(np.uint64) << np.uint64(8 * (nb - 1 - b))
    return out


def site_agreement(configs, expected, n):
    """Per-site fraction of shots whose bit equals the expected bit; majority-vote pattern."""
    configs = np.asarray(configs, dtype=np.uint64)
    f = np.zeros(n)
    maj = 0
    for i in range(n):
        bi = ((configs >> np.uint64(i)) & np.uint64(1)).astype(np.int8)
        e = (expected >> i) & 1
        f[i] = float(np.mean(bi == e))
        if np.mean(bi) > 0.5:
            maj |= 1 << i
    return f, maj


def check_verdict(configs, expected, n, thr=0.9):
    f, maj = site_agreement(configs, expected, n)
    return dict(pass_=bool(f.min() >= thr and maj == expected), min_site_agreement=float(f.min()),
                mean_site_agreement=float(f.mean()), worst_site=int(np.argmin(f)), majority_equals_expected=bool(
                    maj == expected), exact_string_fraction=float(np.mean(np.asarray(configs) == np.uint64(expected))),
                site_agreement=[float(x) for x in f])


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


# ----------------------------------------------------------------------------------------- noiseless MPS control
class TrotterMPS:
    """Pure-numpy MPS (tensors (vL, p, vR), p index 0 = up = |0>, 1 = down = |1>) in the MPS order of the graph JSON.
    Applies the logical gate list of trotter_gates exactly, long-range gates by adjacent swaps (moved back after
    every gate), SVD truncation chi_max / svd_min with the discarded weight accumulated. Convention C7."""

    def __init__(self, g, chi_max=256, svd_min=1e-12):
        self.g = g
        self.order = list(g["order"])
        self.pos = {v: k for k, v in enumerate(self.order)}
        self.n = g["n"]
        self.chi_max = chi_max
        self.svd_min = svd_min
        self.discarded = 0.0
        self.max_chi = 1
        down = set(neel_sites(g))
        self.T = []
        for k in range(self.n):
            t = np.zeros((1, 2, 1), complex)
            t[0, 1 if self.order[k] in down else 0, 0] = 1.0
            self.T.append(t)
        self.center = 0            # orthogonality centre (mixed canonical form)

    def _move_center(self, k):
        while self.center < k:
            c = self.center
            A = self.T[c]
            vL, p, vR = A.shape
            Q, R = np.linalg.qr(A.reshape(vL * p, vR))
            self.T[c] = Q.reshape(vL, p, Q.shape[1])
            self.T[c + 1] = np.tensordot(R, self.T[c + 1], axes=(1, 0))
            self.center += 1
        while self.center > k:
            c = self.center
            A = self.T[c]
            vL, p, vR = A.shape
            Q, R = np.linalg.qr(A.reshape(vL, p * vR).T)
            self.T[c] = Q.T.reshape(Q.shape[1], p, vR)
            self.T[c - 1] = np.tensordot(self.T[c - 1], R.T, axes=(2, 0))
            self.center -= 1

    def _apply2(self, k, U):
        """Apply a 4x4 U on adjacent MPS sites (k, k+1); U index = 2*p_k + p_{k+1}."""
        self._move_center(k)
        A, B = self.T[k], self.T[k + 1]
        vL = A.shape[0]
        vR = B.shape[2]
        th = np.tensordot(A, B, axes=(2, 0))                       # vL, p, q, vR
        th = np.tensordot(U.reshape(2, 2, 2, 2), th, axes=([2, 3], [1, 2]))   # p', q', vL, vR
        th = th.transpose(2, 0, 1, 3).reshape(vL * 2, 2 * vR)
        u, s, vh = np.linalg.svd(th, full_matrices=False)
        nrm2 = float(np.sum(s ** 2))
        keep = int(min(self.chi_max, np.sum(s > self.svd_min * s[0])))
        keep = max(keep, 1)
        self.discarded += float(np.sum(s[keep:] ** 2)) / nrm2
        s = s[:keep] / np.sqrt(np.sum(s[:keep] ** 2) / nrm2) / np.sqrt(nrm2)
        self.T[k] = u[:, :keep].reshape(vL, 2, keep)
        self.T[k + 1] = (s[:, None] * vh[:keep]).reshape(keep, 2, vR)
        self.center = k + 1
        self.max_chi = max(self.max_chi, keep)

    SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], complex)

    def gate(self, i, j, U):
        """U on graph nodes (i, j), U index 2*b_i + b_j."""
        a, b = self.pos[i], self.pos[j]
        if a > b:
            a, b = b, a
            P = self.SWAP
            U = P @ U @ P
        # move site b down to a + 1 by swaps, apply, move back
        for k in range(b - 1, a, -1):
            self._apply2(k, self.SWAP)
        self._apply2(a, U)
        for k in range(a + 1, b):
            self._apply2(k, self.SWAP)

    def step(self, Jz, dt):
        U = edge_unitary(Jz, dt)
        for (i, j) in trotter_gates(self.g, Jz, dt):
            self.gate(i, j, U)

    def export(self):
        """Right-canonical dense tensors (vL, p, vR) for emu2.sample_mps (norm folded into the first tensor)."""
        self._move_center(0)
        return [t.copy() for t in self.T]

    def z_expect(self):
        """<Z_i> in graph-node indexing (Z = +1 up)."""
        out = np.zeros(self.n)
        for k in range(self.n):
            self._move_center(k)
            A = self.T[k]
            pr = np.sum(np.abs(A) ** 2, axis=(0, 2))
            out[self.order[k]] = (pr[0] - pr[1]) / pr.sum()
        return out


def dense_trotter(g, Jz, dt, k):
    """Toy sizes only: exact state vector after Neel + k Trotter steps, index sum_i b_i 2^i (b = 1 down)."""
    n = g["n"]
    v = np.zeros(1 << n, complex)
    v[config_int(neel_sites(g))] = 1.0
    U = edge_unitary(Jz, dt)
    gl = trotter_gates(g, Jz, dt)
    idx = np.arange(1 << n)
    for _ in range(k):
        for (i, j) in gl:
            bi = (idx >> i) & 1
            bj = (idx >> j) & 1
            sub = 2 * bi + bj
            new = np.zeros_like(v)
            for s_out in range(4):
                for s_in in range(4):
                    if U[s_out, s_in] == 0:
                        continue
                    sel = sub == s_in
                    tgt = idx[sel] ^ ((((s_in >> 1) ^ (s_out >> 1)) & 1) << i) ^ (((s_in ^ s_out) & 1) << j)
                    np.add.at(new, tgt, U[s_out, s_in] * v[sel])
            v = new
    return v
