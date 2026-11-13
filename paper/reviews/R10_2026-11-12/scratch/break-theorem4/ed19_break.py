# break-theorem4 / ed19_break.py
# Sparse exact diagonalization of the d=3 patch (n=19), all 20 magnetization sectors, written independently.
# For Jz in {6,12,24,48}, field B = 3Jz/8 and two tilts per label (opposing side, inside the windows of the proof):
#   - global ground state of H - lambda*S*O - B*M: which sector?  gap to the rest of the spectrum
#   - gap inside the Neel sector
#   - comparison with the classical gap (exact enumeration of the 2^19 configurations, same script)
# Output: ed19_break_out.txt / .json next to this file.
import os, sys, time, json, itertools
os.environ.setdefault("OMP_NUM_THREADS", "2"); os.environ.setdefault("MKL_NUM_THREADS", "2"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = open(os.path.join(HERE, "ed19_break_out.txt"), "w")
def pr(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); OUT.write(s + "\n"); OUT.flush()

def patch(d):
    sites = [('D', i, j) for i in range(d) for j in range(d)]
    sites += [('F', i, j) for i in range(d) for j in range(d - 1)]
    sites += [('S', i, j) for i in range(d - 1) for j in range(d - 1) if (i + j) % 2 == 1]
    sites += [('C', i) for i in range(d - 1)]
    ix = {s: k for k, s in enumerate(sites)}
    E = []
    for i in range(d):
        for j in range(d - 1):
            E.append((ix[('D', i, j)], ix[('F', i, j)])); E.append((ix[('D', i, j + 1)], ix[('F', i, j)]))
    for i in range(d - 1):
        for j in range(d - 1):
            if (i + j) % 2 == 1:
                E.append((ix[('S', i, j)], ix[('F', i, j)])); E.append((ix[('S', i, j)], ix[('F', i + 1, j)]))
    for i in range(d - 1):
        jj = 0 if i % 2 == 0 else d - 1
        E.append((ix[('D', i, jj)], ix[('C', i)])); E.append((ix[('D', i + 1, jj)], ix[('C', i)]))
    eta = [1 if s[0] in 'DS' else -1 for s in sites]
    return sites, E, eta

t00 = time.time()
sites, E, eta = patch(3); n = len(sites)
adj = [[] for _ in range(n)]
for a, b in E: adj[a].append(b); adj[b].append(a)
P2 = sorted({tuple(sorted(p)) for k in range(n) for p in itertools.combinations(adj[k], 2)})
dim = 2 ** n
conf = np.arange(dim, dtype=np.int64)
bits = [((conf >> i) & 1).astype(np.int8) for i in range(n)]        # 1 = spin up, Z = +1
Z = [2 * b - 1 for b in bits]
pop = np.zeros(dim, dtype=np.int16)
for b in bits: pop += b
zz = np.zeros(dim, dtype=np.int32)
for a, b in E: zz += Z[a].astype(np.int32) * Z[b]
Mz = (2 * pop - n).astype(np.int32)
SO = {'ms': np.zeros(dim, dtype=np.int32), 'czz': zz, 'c2': np.zeros(dim, dtype=np.int32)}
for i in range(n): SO['ms'] += eta[i] * Z[i].astype(np.int32)
for i, j in P2: SO['c2'] += Z[i].astype(np.int32) * Z[j]
Ssize = {'ms': n, 'czz': len(E), 'c2': len(P2)}
neel = sum(1 << i for i in range(n) if eta[i] == 1)
kN = int(pop[neel])
pr(f"n={n} |E|={len(E)} |P2|={len(P2)}  Neel sector: {kN} up spins, M={int(Mz[neel])}, dimension {int((pop == kN).sum())}")

# sector bases and the exchange part K = (1/4) sum (XX+YY): matrix element 1/2 between configurations that differ by one exchange
idx = [np.nonzero(pop == k)[0] for k in range(n + 1)]
look = np.zeros(dim, dtype=np.int32)
for k in range(n + 1): look[idx[k]] = np.arange(len(idx[k]), dtype=np.int32)
Kk = []
for k in range(n + 1):
    s = idx[k]; rows = []; cols = []
    for a, b in E:
        m = bits[a][s] != bits[b][s]
        src = s[m]; dst = src ^ ((1 << a) | (1 << b))
        rows.append(look[src]); cols.append(look[dst])
    rows = np.concatenate(rows); cols = np.concatenate(cols)
    Kk.append(sp.csr_matrix((np.full(len(rows), 0.5), (rows, cols)), shape=(len(s), len(s))))
pr(f"built the 20 sector matrices in {time.time()-t00:.1f}s; largest sector {max(len(s) for s in idx)}")
rng = np.random.default_rng(7)

def lowest(k, diag, nev):
    d = diag[idx[k]]; m = len(d)
    if m <= 1500:
        w, v = np.linalg.eigh(Kk[k].toarray() + np.diag(d))
        return w[:nev], v[:, :nev]
    H = Kk[k] + sp.diags(d)
    v0 = rng.standard_normal(m) * 0.02; v0[np.argmin(d)] += 1.0
    w, v = sla.eigsh(H, k=nev, which='SA', tol=1e-11, v0=v0, ncv=max(24, 2 * nev + 8), maxiter=20000)
    o = np.argsort(w)
    return w[o], v[:, o]

def run(Jz, label, t, want_corr=False):
    lam = t * Jz; B = 0.375 * Jz
    diag = 0.25 * Jz * zz - (lam * SO[label] if t != 0 else 0.0)
    # classical data (units Jz): W = zz/4 - (3/8) M - t*S*O
    W = 0.25 * zz - 0.375 * Mz - (t * SO[label] if t != 0 else 0.0)
    o = np.argpartition(W, 2)[:3]; o = o[np.argsort(W[o])]
    cl_gs_is_neel = bool(o[0] == neel); cl_gap = float(W[o[1]] - W[o[0]])
    Wn = W[idx[kN]]; on = np.sort(np.partition(Wn, 1)[:2]); cl_sec_gap = float(on[1] - on[0])
    lev = []          # (shifted energy, sector, index in sector)
    e_sec = {}
    vecN = None
    for k in range(n + 1):
        nev = 2 if (k == kN and len(idx[k]) > 1) else 1
        w, v = lowest(k, diag, nev)
        e_sec[k] = w
        if k == kN: vecN = v[:, 0]
        for j, x in enumerate(w): lev.append((x - B * (2 * k - n), k, j))
    lev.sort()
    gs = lev[0]; gap = lev[1][0] - lev[0][0]
    sec_gap = e_sec[kN][1] - e_sec[kN][0]
    # degeneracy guard: the first excited level found is either the 2nd level of the Neel sector or the lowest of another sector
    res = dict(Jz=Jz, label=label, t=t, gs_sector_up=int(gs[1]), gs_in_neel=bool(gs[1] == kN), global_gap=float(gap),
               global_gap_over_Jz=float(gap / Jz), cl_gap=cl_gap, cl_gs_is_neel=cl_gs_is_neel, first_excited_sector_up=int(lev[1][1]),
               sector_gap=float(sec_gap), sector_gap_over_Jz=float(sec_gap / Jz), cl_sector_gap=cl_sec_gap)
    if want_corr:
        p = vecN ** 2; s = idx[kN]
        zexp = np.array([np.dot(p, Z[i][s]) for i in range(n)])
        C = np.array([[np.dot(p, Z[i][s].astype(np.float64) * Z[j][s]) for j in range(n)] for i in range(n)]) - np.outer(zexp, zexp)
        res['max_i_sum_j_abs_conn_ZZ_incl_diag'] = float(np.abs(C).sum(axis=1).max())
        res['max_i_sum_j_abs_conn_ZZ_excl_diag'] = float((np.abs(C).sum(axis=1) - np.abs(np.diag(C))).max())
        res['var_n_ms_over_n'] = float(np.array(eta) @ C @ np.array(eta) / n)
    return res

settings = [('ms', 0.0), ('ms', -1 / 100), ('ms', -1 / 40), ('czz', 1 / 100), ('czz', 1 / 60), ('c2', -1 / 200), ('c2', -1 / 150)]
extra = [('ms', -0.035), ('ms', -0.045), ('czz', 0.07), ('c2', -0.035)]      # outside the windows of the proof (first one inside the exact n=19 window)
ALL = []
pr("\nJz   label  t=lambda/Jz | global g.s. sector (#up) in Neel? | global gap  gap/Jz  classical gap  gap-Jz*cl | 1st excited in sector | sector gap  /Jz  classical")
for Jz in (6.0, 12.0, 24.0, 48.0):
    for label, t in settings + (extra if Jz in (12.0, 48.0) else []):
        t1 = time.time()
        r = run(Jz, label, t, want_corr=(t == 0.0))
        ALL.append(r)
        pr(f"{Jz:4.0f} {label:4s} {t:+.5f} | {r['gs_sector_up']:2d} {str(r['gs_in_neel']):5s} (classical g.s. Neel: {r['cl_gs_is_neel']}) | "
           f"{r['global_gap']:9.5f} {r['global_gap_over_Jz']:.5f} {r['cl_gap']:.5f} {r['global_gap']-Jz*r['cl_gap']:+.4f} | {r['first_excited_sector_up']:2d} | "
           f"{r['sector_gap']:9.5f} {r['sector_gap_over_Jz']:.5f} {r['cl_sector_gap']:.5f}   [{time.time()-t1:.0f}s]")
        if t == 0.0:
            pr(f"      Neel-sector ground state at Jz={Jz:.0f}, lambda=0: max_i sum_j |<Z_i;Z_j>| = {r['max_i_sum_j_abs_conn_ZZ_incl_diag']:.4f} (j=i included), "
               f"{r['max_i_sum_j_abs_conn_ZZ_excl_diag']:.4f} (j!=i); Var(n m_s)/n = {r['var_n_ms_over_n']:.4f}")
json.dump(ALL, open(os.path.join(HERE, "ed19_break_out.json"), "w"), indent=1)
pr(f"\ntotal {time.time()-t00:.0f}s")
