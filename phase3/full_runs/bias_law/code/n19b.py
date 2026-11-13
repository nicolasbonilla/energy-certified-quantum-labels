# Exploratory analysis, no prior declaration: baselines, reference-free energy, and learning with corrected labels.
import json, sys, itertools, glob, re, os
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
root = sys.argv[1]; cache = sys.argv[2]
G = json.load(open(root + '/phase3/full_runs/method/code/graphs/hh_d3.json'))
n = G['n']; edges = [tuple(e) for e in G['edges']]; eta = np.array(G['eta'], float); nd = G['n_down']
M = root + '/phase3/full_runs/method/out_20261030T003230Z/out'
Js57 = sorted(float(re.search(r'_J([0-9.]+)\.json', f).group(1)) for f in glob.glob(f'{M}/emu/emu_n57_J*.json'))
Js115 = sorted(float(re.search(r'_J([0-9.]+)\.json', f).group(1)) for f in glob.glob(f'{M}/emu/emu_n115_J*.json'))
if os.path.exists(cache):
    C = {float(k): v for k, v in json.load(open(cache)).items()}
else:
    cfg = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(n), nd)], dtype=np.int64); cfg.sort(); dim = len(cfg)
    bits = ((cfg[:, None] >> np.arange(n)) & 1).astype(np.int8); Zc = 1 - 2 * bits.astype(float)
    ZZ = sum(Zc[:, i] * Zc[:, j] for i, j in edges); rows, cols = [], []
    for i, j in edges:
        src = np.nonzero(bits[:, i] != bits[:, j])[0]; rows.append(src); cols.append(np.searchsorted(cfg, cfg[src] ^ ((1 << i) | (1 << j))))
    rows = np.concatenate(rows); cols = np.concatenate(cols)
    Hxy = sparse.csr_matrix((0.5 * np.ones(len(rows)), (rows, cols)), shape=(dim, dim)); C = {}
    Ds = sorted(set(int(x) for x in np.round(np.logspace(0.7, np.log10(dim * .9), 26))))
    for J in sorted(set(Js57) | set(Js115)):
        H = Hxy + sparse.diags(J / 4 * ZZ); w, v = eigsh(H, k=1, which='SA', tol=1e-10); E0 = float(w[0]); psi = v[:, 0]
        ms0 = float(((psi**2) @ Zc) @ eta / n); order = np.argsort(-psi**2); out = []
        for D in Ds:
            B = np.sort(order[:D]); Hb = H[B][:, B]
            if D < 400: ww, vv = np.linalg.eigh(Hb.toarray())
            else: ww, vv = eigsh(Hb, k=1, which='SA', tol=1e-8)
            x = vv[:, 0]; out.append(((float(ww[0]) - E0) / n, float(((x**2) @ Zc[B]) @ eta / n) - ms0))
        C[J] = dict(E0=E0, ms0=ms0, curve=sorted(out))
    json.dump({str(k): v for k, v in C.items()}, open(cache, 'w'))
def f(J, de):
    c = np.array(C[J]['curve']); return float(np.interp(np.sqrt(max(de, 0)), np.sqrt(np.maximum(c[:, 0], 0)), c[:, 1]))
def row(N, J):
    e = json.load(open(f'{M}/emu/emu_n{N}_J{J}.json')); v = e['var']['primary']
    return dict(J=J, m=v['labels']['m_s'], m0=e['ref_m_s'], de=v['dE_site'], E=v['E'], E0=e['E0'])
ne = {19: len(edges), 57: 64, 115: 132}
print('A. labels at the same coupling; miss in tau.  raw | use n=19 truth only (no quantum data) | corrected (n=19 curve) | corrected, no reference at 115 (E0 from a*n+b*edges fitted on 19, 57)')
for N, Js in ((57, Js57), (115, Js115)):
    T = []
    for J in Js:
        r = row(N, J); tau = .06 * r['m0']; mc = r['m'] - f(J, r['de']); b = C[J]['ms0']; extra = ''
        vals = [abs(r['m'] - r['m0']) / tau, abs(b - r['m0']) / tau, abs(mc - r['m0']) / tau]
        if N == 115:
            r57 = row(57, J); A = np.array([[19, ne[19]], [57, ne[57]]], float); ab = np.linalg.solve(A, [C[J]['E0'], r57['E0']])
            E0e = ab @ [115, ne[115]]; dee = (r['E'] - E0e) / 115; vals.append(abs(r['m'] - f(J, dee) - r['m0']) / tau); extra = f'  de true {r["de"]:.5f} est {dee:.5f}'
        T.append(vals); print(f'  n={N:3d} J={J:3.1f} ' + ' '.join(f'{x:6.2f}' for x in vals) + extra)
    print('   mean      ' + ' '.join(f'{x:6.2f}' for x in np.mean(T, axis=0)), '  max', ' '.join(f'{x:6.2f}' for x in np.max(T, axis=0)))
print('\nB. learning: cubic in 1/J on the training couplings (J >= 1.6), predict test J = 1.1-1.4. miss in tau.  raw labels | corrected labels | exact labels')
for N, Js in ((57, Js57), (115, Js115)):
    R = [row(N, J) for J in Js]; tr = [r for r in R if r['J'] >= 1.6]; te = [r for r in R if r['J'] < 1.5]
    X = lambda rs: np.array([[1, 1 / r['J'], 1 / r['J']**2, 1 / r['J']**3] for r in rs])
    co = {k: np.linalg.lstsq(X(tr), np.array(y), rcond=None)[0] for k, y in dict(raw=[r['m'] for r in tr], cor=[r['m'] - f(r['J'], r['de']) for r in tr], ex=[r['m0'] for r in tr]).items()}
    for r in te:
        p = {k: float(X([r])[0] @ c) for k, c in co.items()}; tau = .06 * r['m0']
        print(f"  n={N:3d} J={r['J']:3.1f}  {abs(p['raw']-r['m0'])/tau:6.2f} {abs(p['cor']-r['m0'])/tau:6.2f} {abs(p['ex']-r['m0'])/tau:6.2f}")
