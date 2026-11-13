# break-theorem4 / ed19_threshold.py  (set-up copied verbatim from ed19_break.py)
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
OUT = open(os.path.join(HERE, "ed19_threshold_out.txt"), "w")
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


# ---- where does part (a) (global ground state in the Neel sector at B = 3Jz/8, with a gap) start to hold at n = 19?
def probe(Jz, label, t):
    lam = t * Jz; B = 0.375 * Jz
    diag = 0.25 * Jz * zz - (lam * SO[label] if t != 0 else 0.0)
    G = {}
    for k in range(n + 1):
        w, _ = lowest(k, diag, 1)
        G[k] = w[0] - B * (2 * k - n)
    kbest = min(G, key=G.get)
    others = min(v for k, v in G.items() if k != kN)
    return kbest, others - G[kN]          # second number > 0  <=>  the Neel sector holds the global ground state

settings = [('ms', 0.0), ('ms', -1 / 100), ('ms', -1 / 40), ('czz', 1 / 100), ('czz', 1 / 60), ('c2', -1 / 200), ('c2', -1 / 150)]
grid = [1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
pr("\nlowest level of the other sectors minus lowest level of the Neel sector, for H - lambda*S*O - (3Jz/8) M, n = 19")
pr("(positive: the global ground state is in the Neel sector; negative: part (a) of Theorem 4 fails at this Jz and n = 19)")
pr("label  t        | " + " ".join(f"Jz={J:<5}" for J in grid) + " | first grid value from which it holds up to 5.5")
RES = {}
for label, t in settings:
    row = []; 
    for J in grid:
        kb, dlt = probe(J, label, t); row.append((J, kb, dlt))
    ok_from = None
    for J, kb, dlt in reversed(row):
        if dlt > 1e-8: ok_from = J
        else: break
    RES[f"{label} {t:+.5f}"] = [(J, int(kb), float(dlt)) for J, kb, dlt in row]
    pr(f"{label:4s} {t:+.5f} | " + " ".join(f"{dlt:+8.4f}" for J, kb, dlt in row) + f" | {ok_from}")
json.dump(RES, open(os.path.join(HERE, "ed19_threshold_out.json"), "w"), indent=1)
pr(f"\ntotal {time.time()-t00:.0f}s")
