# real_data / n19_curves.py  (own code; 2026-11-12; task rd-code-learn)
#
# The n = 19 bias-against-energy curve of Sec. V at the 50 couplings of the dataset (DECLARATION.md Sec. 5, P5, and the
# "small classical calculation" of Sec. 6). NO REAL DATUM IS READ: the script reads one graph file of this project
# (method/code/graphs/hh_d3.json) and nothing else.
#
# Recipe: bias_law/code/n19b.py lines 15-31, UNCHANGED (same basis, same Hamiltonian, same eigensolver calls and
# tolerances, same 26 logarithmic truncation levels, same sorted (de, dm_s) list). What differs from n19b.py:
#   - the couplings are Jz = k/10 (k = 11..60) instead of the couplings of the stored emulation;
#   - one JSON per coupling (so a run can be split over processes and resumed), merged afterwards into
#     n19_curves.json, which has the SAME format as bias_law/inputs/n19_curves.json;
#   - the exact n = 19 labels of the ground state are stored as well (n19_labels.json): every <Z_i>, every edge and
#     second-neighbour <Z_i Z_j>, m_s, Czz_bar, C2_bar, the local labels of hh_d3.json, the Neel energy error per site.
#
#   python -B -I n19_curves.py <ROOT = work/> <out_dir> run <k_first> <k_last> <k_step>     (couplings k/10)
#   python -B -I n19_curves.py <ROOT = work/> <out_dir> merge
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import hashlib
import itertools
import json
import sys
import time

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh

K_ALL = list(range(11, 61))          # Jz = k/10


def build(root):
    """Lines 7-8 and 15-22 of n19b.py (same statements; variables kept)."""
    G = json.load(open(root + '/phase3/full_runs/method/code/graphs/hh_d3.json'))
    n = G['n']; edges = [tuple(e) for e in G['edges']]; eta = np.array(G['eta'], float); nd = G['n_down']
    cfg = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(n), nd)], dtype=np.int64); cfg.sort(); dim = len(cfg)
    bits = ((cfg[:, None] >> np.arange(n)) & 1).astype(np.int8); Zc = 1 - 2 * bits.astype(float)
    ZZ = sum(Zc[:, i] * Zc[:, j] for i, j in edges); rows, cols = [], []
    for i, j in edges:
        src = np.nonzero(bits[:, i] != bits[:, j])[0]; rows.append(src); cols.append(np.searchsorted(cfg, cfg[src] ^ ((1 << i) | (1 << j))))
    rows = np.concatenate(rows); cols = np.concatenate(cols)
    Hxy = sparse.csr_matrix((0.5 * np.ones(len(rows)), (rows, cols)), shape=(dim, dim))
    Ds = sorted(set(int(x) for x in np.round(np.logspace(0.7, np.log10(dim * .9), 26))))
    return G, n, edges, eta, dim, Zc, ZZ, Hxy, Ds


def one(J, G, n, edges, eta, dim, Zc, ZZ, Hxy, Ds):
    """Lines 24-31 of n19b.py for one coupling (same statements), plus the exact labels of the ground state."""
    H = Hxy + sparse.diags(J / 4 * ZZ); w, v = eigsh(H, k=1, which='SA', tol=1e-10); E0 = float(w[0]); psi = v[:, 0]
    ms0 = float(((psi**2) @ Zc) @ eta / n); order = np.argsort(-psi**2); out = []
    for D in Ds:
        B = np.sort(order[:D]); Hb = H[B][:, B]
        if D < 400: ww, vv = np.linalg.eigh(Hb.toarray())
        else: ww, vv = eigsh(Hb, k=1, which='SA', tol=1e-8)
        x = vv[:, 0]; out.append(((float(ww[0]) - E0) / n, float(((x**2) @ Zc[B]) @ eta / n) - ms0))
    rec = dict(E0=E0, ms0=ms0, curve=sorted(out))
    # ---- additions (not part of the recipe): exact labels of the n = 19 ground state, and checks
    p = psi ** 2
    Z = p @ Zc
    nn2 = [tuple(e) for e in G['nn2']]
    loc = G['local']
    czz = [float(p @ (Zc[:, i] * Zc[:, j])) for i, j in edges]
    c2 = [float(p @ (Zc[:, i] * Zc[:, j])) for i, j in nn2]
    res = float(np.linalg.norm(H @ psi - E0 * psi))
    lab = dict(Jz=J, n=n, dim=dim, E0=E0, m_s=ms0, Z=[float(x) for x in Z], Czz_edges=czz, Czz_nn2=c2,
               Czz_bar=float(np.mean(czz)), C2_bar=float(np.mean(c2)), Z_bulk=float(Z[loc['bulk_site']]),
               Z_boundary=float(Z[loc['boundary_site']]),
               Czz_edge=float(p @ (Zc[:, loc['edge'][0]] * Zc[:, loc['edge'][1]])),
               sum_Z=float(Z.sum()), M0=float(eta.sum()),
               E_neel=float(-len(edges) * J / 4), de_neel=float((-len(edges) * J / 4 - E0) / n),
               residual_norm=res, norm=float(p.sum()), Ds=Ds, n_levels=len(Ds),
               de_curve_min=float(min(o[0] for o in out)), de_curve_max=float(max(o[0] for o in out)))
    return rec, lab


def main():
    root, out_dir, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    parts = os.path.join(out_dir, "parts")
    os.makedirs(parts, exist_ok=True)
    if mode == "run":
        k0, k1, ks = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        t0 = time.time()
        built = build(root)
        print("built: dim %d, %d levels, %.1f s" % (built[4], len(built[8]), time.time() - t0), flush=True)
        for k in range(k0, k1 + 1, ks):
            assert k in K_ALL, k
            J = k / 10
            path = os.path.join(parts, "n19_J%.1f.json" % J)
            if os.path.exists(path):
                print("exists", path, flush=True)
                continue
            t1 = time.time()
            rec, lab = one(J, *built)
            with open(path + ".tmp", "w") as f:
                json.dump(dict(Jz=J, curve_record=rec, labels=lab, secs=time.time() - t1), f)
            os.replace(path + ".tmp", path)
            print("J=%.1f E0=%.10f m_s=%.8f residual %.1e  %.1f s" % (J, rec["E0"], rec["ms0"], lab["residual_norm"], time.time() - t1), flush=True)
        print("done %.0f s" % (time.time() - t0))
    elif mode == "merge":
        C, L, missing = {}, {}, []
        for k in K_ALL:
            J = k / 10
            path = os.path.join(parts, "n19_J%.1f.json" % J)
            if not os.path.exists(path):
                missing.append(J)
                continue
            r = json.load(open(path))
            C[str(J)] = r["curve_record"]; L[str(J)] = r["labels"]
        if missing:
            raise SystemExit("missing couplings: %s" % missing)
        sums = {}
        for name, obj in (("n19_curves.json", C), ("n19_labels.json", L)):
            s = json.dumps(obj, indent=None if name == "n19_curves.json" else 1)
            with open(os.path.join(out_dir, name), "w", newline="\n") as f:
                f.write(s)
            sums[name] = hashlib.sha256(s.encode()).hexdigest()
        with open(os.path.join(out_dir, "SHA256SUMS.txt"), "w", newline="\n") as f:
            for name in sorted(sums):
                f.write("%s  %s\n" % (sums[name], name))
        print("merged %d couplings" % len(C), sums)
    else:
        raise SystemExit("mode must be run or merge")


if __name__ == "__main__":
    main()
