"""Independent MPS evaluator of the witness pilot (DECLARATION.md SHA-256 529e8dcd...). numpy + json ONLY (no TeNPy).

Reads raw dense MPS tensors (legs vL, p, vR; the physical basis order is taken from the exported metadata 'sz_basis',
e.g. [-0.5, 0.5] for TeNPy 1.1.0 = (down, up)) and the graph JSON, and computes from
left/right environments built directly from the raw tensors (no canonical form, no normalisation assumed):
  <psi|psi>, every <Z_i>, for every edge <S+_i S-_j>, <S-_i S+_j>, <Z_i Z_j>  ->  <H> = sum_e [1/2 (+- + -+) + Jz/4 ZZ],
  every second-neighbour <Z_i Z_j>, Z-strings (Z_loop), and the sector check <(Sz_tot - s)^2> = sum_q (q - s)^2 p_q
  from charge-resolved weights (environments indexed by the number of up spins).
All values are normalised by <psi|psi>; site indices in the output are GRAPH labels unless stated.

CLI (separate-process re-evaluation, gate G4):
  python indep_eval.py <graph.json> <out.json> <npz> [<npz> ...]
"""
import json
import sys
import time
import numpy as np


class Basis:
    """Single-site operators in the exported physical basis order (sz_basis = Sz eigenvalue of each index)."""
    def __init__(self, sz_basis):
        sz = [float(x) for x in sz_basis]
        assert sorted(sz) == [-0.5, 0.5], "spin-1/2 basis expected"
        u, d = sz.index(0.5), sz.index(-0.5)
        self.Z = np.diag([2.0 * x for x in sz])
        self.SP = np.zeros((2, 2)); self.SP[u, d] = 1.0      # S+ = |up><down|
        self.SM = self.SP.T.copy()                           # S- = |down><up|
        self.PUP = np.zeros((2, 2)); self.PUP[u, u] = 1.0
        self.PDN = np.zeros((2, 2)); self.PDN[d, d] = 1.0


def load_npz(path):
    z = np.load(path, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    n = int(meta["n"])
    Ts = [np.asarray(z["B%d" % k]) for k in range(n)]
    return Ts, meta


def tL(L, A, op=None):
    """Left transfer: new[b', b] = sum conj(A[a', s', b']) op[s', s] L[a', a] A[a, s, b]  (bra index first)."""
    X = np.tensordot(L, A, axes=(1, 0))                  # (a', s, b)
    if op is not None:
        X = np.tensordot(op, X, axes=(1, 1)).transpose(1, 0, 2)   # (a', s', b)
    return np.tensordot(A.conj(), X, axes=([0, 1], [0, 1]))       # (b', b)


def tR(R, A, op=None):
    """Right transfer: new[a', a] = sum conj(A[a', s', b']) op[s', s] A[a, s, b] R[b', b]."""
    X = np.tensordot(A, R, axes=(2, 1))                  # (a, s, b')
    if op is not None:
        X = np.tensordot(op, X, axes=(1, 1)).transpose(1, 0, 2)   # (a, s', b')
    return np.tensordot(X, A.conj(), axes=([1, 2], [1, 2])).T     # (a', a)


def close(X, R):
    return np.sum(X * R)


class Evaluator:
    def __init__(self, Ts, basis):
        self.b = basis
        self.Ts = Ts
        self.n = len(Ts)
        assert Ts[0].shape[0] == 1 and Ts[-1].shape[2] == 1, "open boundary MPS expected"
        self.L = [np.ones((1, 1), dtype=Ts[0].dtype)]
        for A in Ts:
            self.L.append(tL(self.L[-1], A))
        self.R = [None] * (self.n + 1)
        self.R[self.n] = np.ones((1, 1), dtype=Ts[0].dtype)
        for k in range(self.n - 1, -1, -1):
            self.R[k] = tR(self.R[k + 1], Ts[k])
        self.norm = self.L[self.n][0, 0]
        self.norm_R = self.R[0][0, 0]

    def one(self, k, op):
        return close(tL(self.L[k], self.Ts[k], op), self.R[k + 1]) / self.norm

    def string(self, sites, ops):
        """<prod_k ops[k] at sites[k]> for sorted distinct MPS sites."""
        o = dict(zip(sites, ops))
        i0, i1 = min(sites), max(sites)
        X = self.L[i0]
        for k in range(i0, i1 + 1):
            X = tL(X, self.Ts[k], o.get(k))
        return close(X, self.R[i1 + 1]) / self.norm

    def pairs(self, plist, opi_opj):
        """Two-point values for a list of MPS pairs (i < j) and a list of (op_i, op_j); propagates once per (i, op_i)."""
        by_i = {}
        for (i, j) in plist:
            by_i.setdefault(i, []).append(j)
        out = {}
        for i, js in by_i.items():
            jmax = max(js); jset = set(js)
            for t, (oi, oj) in enumerate(opi_opj):
                X = tL(self.L[i], self.Ts[i], oi)
                for k in range(i + 1, jmax + 1):
                    if k in jset:
                        out[(i, k, t)] = close(tL(X, self.Ts[k], oj), self.R[k + 1]) / self.norm
                    if k < jmax:
                        X = tL(X, self.Ts[k])
        return out

    def sector_weights(self):
        """p_u = weight of the component with u up spins (u = 0..n), from raw tensors; exact zeros stay zero."""
        envs = {0: self.L[0]}
        for A in self.Ts:
            new = {}
            for u, E in envs.items():
                if not np.any(E):
                    continue
                for du, P in ((1, self.b.PUP), (0, self.b.PDN)):
                    X = tL(E, A, P)
                    if np.any(X):
                        new[u + du] = new.get(u + du, 0) + X
            envs = new
        return {u: float(np.real(E[0, 0] / self.norm)) for u, E in envs.items()}


def evaluate(Ts, G, Jz, sz_basis, s=None, full=True):
    """Full independent evaluation. G: graph JSON dict (needs n, order, mps edges/nn2/eta). Returns a dict."""
    t0 = time.time()
    n = G["n"]
    order = G["order"]
    b = Basis(sz_basis)
    Zop, SP, SM = b.Z, b.SP, b.SM
    ev = Evaluator(Ts, b)
    res = {"norm": float(np.real(ev.norm)), "norm_R": float(np.real(ev.norm_R))}
    Zm = np.array([np.real(ev.one(k, Zop)) for k in range(n)])
    res["Z_graph"] = [0.0] * n
    for k in range(n):
        res["Z_graph"][order[k]] = float(Zm[k])
    eta = np.array(G["mps"]["eta"], dtype=float)
    res["m_s"] = float(np.dot(eta, Zm) / n)
    res["sum_Z"] = float(np.sum(Zm))
    edges = [tuple(e) for e in G["mps"]["edges"]]
    nn2 = [tuple(e) for e in G["mps"]["nn2"]]
    if full:
        vals = ev.pairs(edges, [(SP, SM), (SM, SP), (Zop, Zop)])
        E = 0.0; imag = 0.0
        zz_e = []
        for (i, j) in edges:
            pm, mp, zz = vals[(i, j, 0)], vals[(i, j, 1)], vals[(i, j, 2)]
            term = 0.5 * (pm + mp) + 0.25 * Jz * zz
            E += np.real(term); imag = max(imag, abs(np.imag(term)))
            zz_e.append(float(np.real(zz)))
        res["E"] = float(E)
        res["E_max_imag"] = float(imag)
    else:
        vals = ev.pairs(edges, [(Zop, Zop)])
        zz_e = [float(np.real(vals[(i, j, 0)])) for (i, j) in edges]
    v2 = ev.pairs(nn2, [(Zop, Zop)])
    zz_2 = [float(np.real(v2[(i, j, 0)])) for (i, j) in nn2]
    res["Czz_edges"] = zz_e          # in the order of G['mps']['edges'] == G['edges']
    res["Czz_nn2"] = zz_2            # in the order of G['mps']['nn2'] == G['nn2']
    res["Czz_bar"] = float(np.mean(zz_e))
    res["C2_bar"] = float(np.mean(zz_2))
    loc = G["local"]
    pos = {v: k for k, v in enumerate(order)}
    res["Z_bulk"] = res["Z_graph"][loc["bulk_site"]]
    res["Z_boundary"] = res["Z_graph"][loc["boundary_site"]]
    a, b = loc["edge"]
    res["Czz_edge_loc"] = float(np.real(ev.string(sorted([pos[a], pos[b]]), [Zop, Zop])))
    if loc.get("loop"):
        sl = sorted(pos[v] for v in loc["loop"])
        res["Z_loop"] = float(np.real(ev.string(sl, [Zop] * len(sl))))
    w = ev.sector_weights()
    res["sector_weights"] = {str(u): p for u, p in sorted(w.items())}
    if s is not None:
        res["sector_var"] = float(sum(((u - n / 2.0) - s) ** 2 * p for u, p in w.items()))
    res["time_s"] = time.time() - t0
    return res


def main(argv):
    gpath, outp = argv[0], argv[1]
    G = json.load(open(gpath))
    out = []
    for p in argv[2:]:
        Ts, meta = load_npz(p)
        assert meta["n"] == G["n"] and meta["order"] == G["order"], "graph/order mismatch"
        r = evaluate(Ts, G, float(meta["Jz"]), meta["sz_basis"], s=G["sz"], full=True)
        r["npz"] = p
        r["meta"] = meta
        out.append(r)
        print(p, "E=%.12f m_s=%.12f norm=%.14f var=%.3e t=%.1fs" % (r["E"], r["m_s"], r["norm"], r["sector_var"],
                                                                    r["time_s"]), flush=True)
    with open(outp, "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
