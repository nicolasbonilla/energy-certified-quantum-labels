"""theory-theorem4 (R10): exact diagonalization at n = 19, all 20 S^z sectors, for the two pair-label tilts.
H(lam) = (1/4) sum_edges (XX + YY + Jz ZZ) - lam * sum_p Z_i Z_j ,  p over edges (C_zz) or second-neighbour pairs (C_2).
H - B M has the same eigenvectors.  Checks of the bridging steps of Theorem 4 at B = 3 Jz / 8:
 (i) the ground state of H(lam) - B M is non-degenerate and lies in the Neel sector, (ii) sector gap >= global gap,
 and the pair clustering sums  C_pair = max_p sum_p' |<Z_p Z_p'> - <Z_p><Z_p'>|  in that state.
Adapted from scratch/level-theory/ed19.py (same sector construction); graph from the explicit formula."""
import itertools, json, time
import numpy as np, scipy.sparse as sp
from scipy.sparse.linalg import eigsh
from geometry_peierls import patch, pairs2
n, edges, eta, adj, kind, pos = patch(3); eta = np.array(eta); P2 = pairs2(n, adj); KN = int((eta == 1).sum())
def sector(k):
    st = np.array(sorted(sum(1 << i for i in c) for c in itertools.combinations(range(n), k)), dtype=np.int64)
    bits = ((st[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8); Z = 2 * bits - 1
    rows, cols = [], []
    for a, b in edges:
        m = bits[:, a] != bits[:, b]; fl = st[m] ^ ((1 << a) | (1 << b))
        rows.append(np.nonzero(m)[0]); cols.append(np.searchsorted(st, fl))
    r = np.concatenate(rows); c = np.concatenate(cols)
    K = sp.csr_matrix((np.full(len(r), 0.5), (r, c)), shape=(len(st), len(st)))
    ze = np.stack([Z[:, a] * Z[:, b] for a, b in edges], 1).astype(float)
    z2 = np.stack([Z[:, a] * Z[:, b] for a, b in P2], 1).astype(float)
    return dict(K=K, ze=ze, z2=z2, dim=len(st))
def low2(S, diag, vec=False):
    if S["dim"] <= 400:
        w, v = np.linalg.eigh(S["K"].toarray() + np.diag(diag)); w = list(w[:2]) + [np.inf] * (2 - min(2, len(w)))
        return (w[0], w[1], v[:, 0]) if vec else (w[0], w[1])
    w, v = eigsh(S["K"] + sp.diags(diag), k=3, which="SA", ncv=40, tol=1e-10); o = np.argsort(w)
    return (w[o[0]], w[o[1]], v[:, o[0]]) if vec else (w[o[0]], w[o[1]])
t0 = time.time(); SEC = {k: sector(k) for k in range(n + 1)}; out = []
print(f"n={n} edges={len(edges)} second-neighbour pairs={len(P2)} Neel sector k={KN} (dim {SEC[KN]['dim']})")
for Jz in (2.5, 6.0, 10.0):
    for lab in ("C_zz", "C_2"):
        for t in (0.0, 0.01, -0.01):
            if lab == "C_2" and t == 0.0: continue
            lam = t * Jz; E = {}
            for k in range(n + 1):
                S = SEC[k]; diag = (Jz / 4) * S["ze"].sum(1) - lam * (S["ze"].sum(1) if lab == "C_zz" else S["z2"].sum(1))
                if k == KN:
                    e0, e1, v = low2(S, diag, True); E[k] = (e0, e1); p = v ** 2
                    cp = {}
                    for nm, Zp in (("edges", S["ze"]), ("pairs2", S["z2"])):
                        mean = p @ Zp; cov = (Zp * p[:, None]).T @ Zp - np.outer(mean, mean); cp[nm] = float(np.abs(cov).sum(1).max())
                else:
                    E[k] = low2(S, diag)
            e0 = E[KN][0]; sgap = E[KN][1] - e0; B = 0.375 * Jz
            ggap = min([sgap] + [E[k][0] - e0 - 2 * B * (k - KN) for k in range(n + 1) if k != KN])
            hi = min((E[k][0] - e0) / (2 * (k - KN)) for k in range(KN + 1, n + 1)); lo = max((e0 - E[k][0]) / (2 * (KN - k)) for k in range(0, KN))
            rec = dict(Jz=Jz, label=lab, t=t, sector_gap=sgap, global_gap_B38=ggap, in_neel_sector=bool(ggap > 0), B_lo=lo / Jz, B_hi=hi / Jz,
                       C_pair_edges=cp["edges"], C_pair_pairs2=cp["pairs2"]); out.append(rec)
            print(f"Jz={Jz:5.1f} {lab:4s} lam/Jz={t:+.2f} | sector gap {sgap:7.4f} | window of B/Jz ({lo/Jz:+.4f}, {hi/Jz:+.4f}) | global gap at B=3Jz/8: {ggap:+7.4f}"
                  f" = {ggap/Jz:+.4f} Jz | (i) g.s. in Neel sector: {ggap > 0} | (ii) sector gap >= global gap: {sgap >= ggap - 1e-12} |"
                  f" C_pair edges {cp['edges']:.4f}, pairs2 {cp['pairs2']:.4f}", flush=True)
json.dump(out, open("ed19_pairs_out.json", "w"), indent=1); print(f"total {time.time()-t0:.1f}s")
