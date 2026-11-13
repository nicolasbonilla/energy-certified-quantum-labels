# break-theorem4 / ed19_sectorgap.py  (set-up copied verbatim from ed19_break.py)
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
OUT = open(os.path.join(HERE, "ed19_sectorgap_out.txt"), "w")
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


# ---- gap INSIDE the Neel sector (statement (b) of Theorem 4 does not involve the field) on the grid of ed19_threshold.py
settings = [('ms', 0.0), ('ms', -1 / 100), ('ms', -1 / 40), ('czz', 1 / 100), ('czz', 1 / 60), ('c2', -1 / 200), ('c2', -1 / 150)]
grid = [1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
pr("\ngap of H - lambda*S*O inside the Neel sector (11 up spins), n = 19")
pr("label  t        | " + " ".join(f"Jz={J:<5}" for J in grid))
RES = {}
for label, t in settings:
    row = []
    for J in grid:
        diag = 0.25 * J * zz - (t * J * SO[label] if t != 0 else 0.0)
        w, _ = lowest(kN, diag, 2)
        row.append(float(w[1] - w[0]))
    RES[f"{label} {t:+.5f}"] = row
    pr(f"{label:4s} {t:+.5f} | " + " ".join(f"{g:8.4f}" for g in row))
pr(f"smallest sector gap on the grid: {min(min(r) for r in RES.values()):.4f}")
json.dump(dict(grid=grid, gaps=RES), open(os.path.join(HERE, "ed19_sectorgap_out.json"), "w"), indent=1)
pr(f"\ntotal {time.time()-t00:.0f}s")
