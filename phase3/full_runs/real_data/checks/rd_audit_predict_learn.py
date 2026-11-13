# -*- coding: utf-8 -*-
"""rd-audit (R10, 2026-11-12): INDEPENDENT recomputation of the predictions and of the learning tests on the public data.

Own code. Imports nothing from real_data/code/ (the sealed code), nothing from the stored project code.
Parts: G sign rule P1-P3 (four families) and rank rule P4; H the n = 19 curve from an own exact diagonalization and the
P5 ratios and decision; K filter numbers and the n = 19 comparison; M like-for-like J*_s with interpolated thresholds;
J (f3) every split end to end from own exact intervals (split 0 printed); N L1 and L2 for the cubic.
usage: python -B -I rd_audit_predict_learn.py
"""
import glob
import hashlib
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh

T00 = time.time()
ROOT = 'C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work'
RUNS = ROOT + '/phase3/full_runs'
RD = RUNS + '/real_data'
MAP = RUNS + '/map/laptop_analysis'
OUTJ = RD + '/checks/rd_audit_predict_learn.json'
DECL = '6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa'
PINS = {'real_n57.json': 'ec96cd6d49a160ba91b38a08f987d221aa01c465c470e0eb17c13f9bacedc4dd',
        'real_n115.json': '5890160c5ff0992b0859ce44fba3a74d1aff6fa6e005f8ef0d0db4f4233d0002',
        'lattice_maps.json': 'a066581a316dbcfacabe8b50f318dc323fc05eaf67c67f99209cc4282586ec81'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(RD + '/DECLARATION.md') == DECL
for _k, _v in PINS.items():
    assert sha(RD + '/converted/' + _k) == _v
SEED = int(DECL[:8], 16)
KEYS = ['%.1f' % (k / 10) for k in range(11, 61)]
TRAIN = KEYS[5:]
TEST = KEYS[:4]
ALLOW = Fr(1, 10 ** 6)
RES = {}
FIND = []


def say(*a):
    print(*a)
    sys.stdout.flush()


def cmp(name, mine, stored, tol):
    d = abs(mine - stored)
    if d > tol:
        FIND.append(dict(what=name, mine=mine, stored=stored, diff=d))
    return d


LM = json.load(open(RD + '/converted/lattice_maps.json'))['maps']
G = {}
for n in (57, 115):
    m = LM[str(n)]
    edges = sorted(tuple(sorted(e)) for e in m['edges_sorted_unique'])
    col = m['colour_with_node0_as_1']
    maj = 1 if 2 * sum(col) > n else 0
    eta = [1 if c == maj else -1 for c in col]
    nb = {i: set() for i in range(n)}
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    nn2 = sorted({(x, y) for j in range(n) for x in nb[j] for y in nb[j] if x < y})
    G[n] = dict(edges=edges, eta=eta, nn2=nn2, M0=sum(eta))
D = {n: json.load(open(RD + '/converted/real_n%d.json' % n)) for n in (57, 115)}
SM = json.load(open(MAP + '/summary_map.json'))
PROW = {(r['n'], '%.1f' % r['Jz'], r['label']): r for r in SM['rows']}
PE0 = {k: v['E0'] for k, v in SM['refs'].items()}
SPRED = json.load(open(RD + '/out/predict/predict_results.json'))
SF3 = json.load(open(RD + '/out/learn/f3_constructive.json'))
SSETS = json.load(open(RD + '/out/S_sets.json'))
assert sha(RD + '/out/S_sets.json') == open(RD + '/out/S_sets.sha256').read().split()[0]


def items(n, key):
    """real and reference (authors' DMRG) values of every item of the four families, matched by sites, never by position."""
    g = G[n]
    rf = D[n]['skqd_random_flip'][key]
    dm = D[n]['dmrg'][key]
    pr = {tuple(sorted(p)): v for p, v in zip(rf['2_nn_corr_pairs_zz_basis_opt'], rf['2_nn_corr_funcs_zz_basis_opt'])}
    pd = {tuple(sorted(p)): v for p, v in zip(dm['2_nn_corr_pairs'], dm['2_nn_corr_funcs_zz'])}
    lr = {tuple(s): v for s, v in zip(rf['z_loop_sites'], rf['z_loop'])}
    ld = {tuple(s): v for s, v in zip(dm['z_loop_sites'], dm['z_loop'])}
    assert set(lr) == set(ld) and len(lr) == {57: 4, 115: 12}[n]
    out = {}
    out['sites'] = (np.array(rf['z_basis_opt']), np.array(dm['z']), np.array(g['eta'], float))
    out['edges'] = (np.array([pr[e] for e in g['edges']]), np.array([pd[e] for e in g['edges']]), -np.ones(len(g['edges'])))
    out['second_neighbours'] = (np.array([pr[e] for e in g['nn2']]), np.array([pd[e] for e in g['nn2']]), np.ones(len(g['nn2'])))
    ks = sorted(lr)
    out['loops'] = (np.array([lr[k] for k in ks]), np.array([ld[k] for k in ks]), np.ones(len(ks)))
    return out


def base(n, key):
    g = G[n]
    rf = D[n]['skqd_random_flip'][key]
    dm = D[n]['dmrg'][key]
    P = dict(E_real=rf['final_global_energy'], Mx=sum(Fr(x) for x in rf['z_basis_opt']),
             ms_real=math.fsum(e * x for e, x in zip(g['eta'], rf['z_basis_opt'])) / n,
             ms_auth=math.fsum(e * x for e, x in zip(g['eta'], dm['z'])) / n)
    P['E0'] = PE0.get('%d_%s' % (n, key), dm['ground_state_energy'])
    r = PROW.get((n, key, 'm_s'))
    P['ms_gs'] = r['O_GS'] if r else P['ms_auth']
    P['tau'] = 0.06 * abs(P['ms_gs'])
    P['de'] = (P['E_real'] - P['E0']) / n
    return P


PT = {(n, k): base(n, k) for n in (57, 115) for k in KEYS}


def spearman(x, y):
    def rank(v):
        v = np.asarray(v)
        o = np.argsort(v, kind='stable')
        r = np.empty(len(v))
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
                j += 1
            r[o[i:j + 1]] = 0.5 * (i + j) + 1
            i = j + 1
        return r
    a, b = rank(x), rank(y)
    a -= a.mean()
    b -= b.mean()
    return float((a @ b) / math.sqrt((a @ a) * (b @ b)))


# ------------------------------------------------------------------------------------------------ G. P1-P3, P4
say('== G. sign rule P1-P3 (F = fraction of (item, coupling) pairs with t > 0) and rank rule P4, own code ==')
RES['G'] = {}
tot = [0, 0]
for n in (57, 115):
    for fam in ('sites', 'edges', 'second_neighbours', 'loops'):
        pos = cnt = le1 = 0
        Dv = []
        exc = []
        for k in KEYS:
            real, gs, neel = items(n, k)[fam]
            t = (real - gs) / (neel - gs)
            pos += int((t > 0).sum())
            le1 += int((t <= 1).sum())
            cnt += len(t)
            if (t <= 0).any():
                exc.append((k, int((t <= 0).sum())))
            Dv.append(float(np.mean(np.abs(real - gs) / (0.06 * np.abs(gs)))))
        F = pos / cnt
        rho = spearman([float(k) for k in KEYS], Dv)
        s1 = SPRED['sizes'][str(n)]['P1_P3'][fam]
        s4 = SPRED['sizes'][str(n)]['P4'][fam]
        cmp('P1 F %d %s' % (n, fam), F, s1['F'], 1e-12)
        cmp('P4 spearman %d %s' % (n, fam), rho, s4['spearman'], 1e-9)
        tot[0] += pos
        tot[1] += cnt
        RES['G']['%d_%s' % (n, fam)] = dict(F=F, pairs=cnt, positive=pos, exceptions=exc, frac_t_le_1=le1 / cnt, spearman=rho,
                                            holds_sign=F >= 0.95, holds_rank=rho <= -0.9, stored_F=s1['F'],
                                            stored_spearman=s4['spearman'])
        say(' n=%d %-17s F = %d/%d = %.6f (stored %.6f) HOLDS %s; exceptions at %s; t<=1: %.4f; Spearman(D, Jz) = %.6f '
            '(stored %.6f) HOLDS %s' % (n, fam, pos, cnt, F, s1['F'], F >= 0.95, exc, le1 / cnt, rho, s4['spearman'], rho <= -0.9))
say(' all families and sizes: %d of %d pairs on the Neel side' % (tot[0], tot[1]))
RES['G']['total'] = tot

# ------------------------------------------------------------------------------------------------ H. P5
say('\n== H. n = 19 curve from an own exact diagonalization (recipe of bias_law/code/n19b.py re-implemented) and P5 ==')
g19 = json.load(open(RUNS + '/method/code/graphs/hh_d3.json'))
n19 = g19['n']
e19 = [tuple(e) for e in g19['edges']]
eta19 = np.array(g19['eta'], float)
cfg = np.array(sorted(sum(1 << i for i in c) for c in itertools.combinations(range(n19), g19['n_down'])), dtype=np.int64)
dim = len(cfg)
bits = ((cfg[:, None] >> np.arange(n19)) & 1).astype(np.int8)
Zc = 1.0 - 2.0 * bits
zz = np.zeros(dim)
rows, cols = [], []
for i, j in e19:
    zz += Zc[:, i] * Zc[:, j]
    src = np.nonzero(bits[:, i] != bits[:, j])[0]
    dst = np.searchsorted(cfg, cfg[src] ^ ((1 << i) | (1 << j)))
    assert (cfg[dst] == (cfg[src] ^ ((1 << i) | (1 << j)))).all()
    rows.append(src)
    cols.append(dst)
Hxy = sparse.csr_matrix((0.5 * np.ones(sum(len(r) for r in rows)), (np.concatenate(rows), np.concatenate(cols))), shape=(dim, dim))
assert abs(Hxy - Hxy.T).max() == 0
Ds = sorted(set(int(x) for x in np.round(np.logspace(0.7, np.log10(dim * .9), 26))))
say(' n = 19: %d sites, %d edges, sector dimension %d, %d truncation levels (D = %d .. %d)' % (n19, len(e19), dim, len(Ds), Ds[0], Ds[-1]))
S19 = json.load(open(RD + '/out/n19/n19_curves.json'))
C19 = {}
order_first = ['1.1', '1.5', '2.0', '2.5', '2.9']
todo = order_first + [k for k in KEYS if k not in order_first]
worst19 = dict(E0=0.0, ms0=0.0, curve=0.0)
for k in todo:
    if time.time() - T00 > 420 and k not in order_first:
        break
    J = float(k)
    H = (Hxy + sparse.diags(J / 4 * zz)).tocsr()
    w, v = eigsh(H, k=1, which='SA', tol=1e-10)
    psi = v[:, 0]
    E0 = float(w[0])
    ms0 = float(((psi ** 2) @ Zc) @ eta19 / n19)
    order = np.argsort(-psi ** 2, kind='stable')
    pts = []
    for Dn in Ds:
        Bs = np.sort(order[:Dn])
        Hb = H[Bs][:, Bs]
        if Dn < 400:
            ww, vv = np.linalg.eigh(Hb.toarray())
        else:
            ww, vv = eigsh(Hb, k=1, which='SA', tol=1e-8)
        x = vv[:, 0]
        pts.append(((float(ww[0]) - E0) / n19, float(((x ** 2) @ Zc[Bs]) @ eta19 / n19) - ms0))
    pts = sorted(pts)
    C19[k] = dict(E0=E0, ms0=ms0, curve=pts)
    s = S19[k]
    worst19['E0'] = max(worst19['E0'], abs(E0 - s['E0']))
    worst19['ms0'] = max(worst19['ms0'], abs(ms0 - s['ms0']))
    worst19['curve'] = max(worst19['curve'], float(np.abs(np.array(pts) - np.array(s['curve'])).max()))
say(' couplings diagonalized: %d of 50 (%.0f s); against the curve file fixed before the hash: |dE0| <= %.1e, |dm_s| <= %.1e, '
    'curve points <= %.1e' % (len(C19), time.time() - T00, worst19['E0'], worst19['ms0'], worst19['curve']))
for kk, vv in worst19.items():
    if vv > 1e-6:
        FIND.append(dict(what='n19 ' + kk + ' against out/n19/n19_curves.json', diff=vv))


def curve(k, de):
    c = np.array(C19[k]['curve'])
    return float(np.interp(math.sqrt(max(de, 0.0)), np.sqrt(np.maximum(c[:, 0], 0)), c[:, 1]))


RES['H'] = dict(n19_done=len(C19), n19_worst=worst19)
for n in (57, 115):
    rowsP = {}
    srow = {('%.1f' % r['Jz']): r for r in SPRED['sizes'][str(n)]['P5']['rows']}
    for k in KEYS:
        if k not in C19:
            continue
        P = PT[(n, k)]
        Delta = P['ms_real'] - P['ms_gs']
        cv = curve(k, P['de'])
        rowsP[k] = dict(Delta=Delta, de=P['de'], curve=cv, ratio=Delta / cv, raw=abs(Delta) / P['tau'],
                        miss=abs(P['ms_real'] - cv - P['ms_gs']) / P['tau'])
        cmp('P5 ratio %d %s' % (n, k), rowsP[k]['ratio'], srow[k]['ratio'], 2e-6)
        cmp('P5 miss %d %s' % (n, k), rowsP[k]['miss'], srow[k]['miss_tau'], 2e-6)
    dec = [k for k in rowsP if rowsP[k]['raw'] >= 0.2]
    outside = [k for k in dec if not (0.75 <= rowsP[k]['ratio'] <= 1.3)]
    full = len(rowsP) == 50
    mean = float(np.mean([r['miss'] for r in rowsP.values()]))
    dec45 = [k for k in dec if k in TRAIN]
    R = dict(five={k: rowsP[k] for k in order_first}, stored_five={k: srow[k]['ratio'] for k in order_first},
             n_rows=len(rowsP), mean_miss=mean if full else None, n_deciding=len(dec), outside=outside,
             ratio_range_deciding=[min(rowsP[k]['ratio'] for k in dec), max(rowsP[k]['ratio'] for k in dec)],
             median_ratio_deciding=float(np.median([rowsP[k]['ratio'] for k in dec])),
             mean_raw=float(np.mean([r['raw'] for r in rowsP.values()])),
             mean_miss_45=float(np.mean([rowsP[k]['miss'] for k in TRAIN if k in rowsP])),
             outside_45=[k for k in dec45 if k in outside], n_deciding_45=len(dec45))
    RES['H'][n] = R
    say(' n=%d five couplings, ratio = Delta / curve(de_real) (mine | stored): ' % n
        + '; '.join('%s: %.4f | %.4f' % (k, rowsP[k]['ratio'], srow[k]['ratio']) for k in order_first))
    say('   %d couplings: mean miss after correction %.4f tau (raw %.4f; limit %s); deciding couplings %d, ratios %.4f-%.4f, '
        'median %.3f, outside [0.75, 1.3]: %d %s' % (len(rowsP), mean, R['mean_raw'], {57: 0.2, 115: 0.6}[n], len(dec),
                                                   R['ratio_range_deciding'][0], R['ratio_range_deciding'][1],
                                                   R['median_ratio_deciding'], len(outside), outside))
    say('   45 training couplings only (reported, not deciding): mean miss %.4f tau; deciding %d, outside %d'
        % (R['mean_miss_45'], len(dec45), len(R['outside_45'])))
if all(RES['H'][n]['n_rows'] == 50 for n in (57, 115)):
    ok = (RES['H'][57]['mean_miss'] <= 0.2 and RES['H'][115]['mean_miss'] <= 0.6 and not RES['H'][57]['outside']
          and not RES['H'][115]['outside'])
    RES['H']['P5_outcome'] = 'PASS' if ok else 'FAIL'
    say(' P5, one decision by the declared rule, from my numbers: %s (stored: %s)' % (RES['H']['P5_outcome'], SPRED['P5_rule']['outcome']))

# ------------------------------------------------------------------------------------------------ exact m_s intervals (own)
files = []
for d in ('rigor/out_20261031T073328Z', 'rigor/out_20261031T100015Z', 'final_tests'):
    files += sorted(glob.glob(RUNS + '/' + d + '/**/*_cert.json', recursive=True))
CERT, seen = [], set()
for f in files:
    b = open(f, 'rb').read()
    h = hashlib.sha256(b).hexdigest()
    if h in seen:
        continue
    seen.add(h)
    c = json.loads(b)
    n = {'hh_d5.json': 57, 'hh_d7.json': 115}.get(c['graph'])
    if n is None or c['task']['kind'] != 'm_s':
        continue
    den = 2 ** int(c['K'])
    CERT.append(dict(n=n, sigma=int(c['task']['sigma']), lam=Fr(str(c['task']['lam'])), J=Fr(str(c['task']['Jz'])),
                     c=Fr(sum(int(x) for x in c['t']), den), mu=Fr(int(c['mu']), den)))


def ms_interval(n, key):
    P = PT[(n, key)]
    J = Fr(key)
    E = Fr(P['E_real']) + ALLOW
    ends = []
    for sg in (+1, -1):
        cs = [c for c in CERT if c['n'] == n and c['sigma'] == sg]
        bo = [(c['c'], c['mu'], c['lam'] * n) for c in cs if c['J'] == J]
        for a in cs:
            for b in cs:
                if a['J'] < J < b['J']:
                    t = (b['J'] - J) / (b['J'] - a['J'])
                    bo.append((t * a['c'] + (1 - t) * b['c'], t * a['mu'] + (1 - t) * b['mu'], (t * a['lam'] + (1 - t) * b['lam']) * n))
        if not bo:
            return None
        uR = min((E - cc + mu * P['Mx'] + abs(mu) * ALLOW) / dn for cc, mu, dn in bo)
        u0 = min((E - cc + mu * G[n]['M0']) / dn for cc, mu, dn in bo)
        ends.append(min(max(uR, u0), Fr(1)))
    return -ends[1], ends[0]


IV = {(n, k): ms_interval(n, k) for n in (57, 115) for k in TRAIN}
SETS = {}
for n in (57, 115):
    wt = {k: float((IV[(n, k)][1] - IV[(n, k)][0]) / Fr(PT[(n, k)]['tau'])) for k in TRAIN if IV[(n, k)]}
    S = [k for k in TRAIN if k in wt and (IV[(n, k)][1] - IV[(n, k)][0]) <= Fr(PT[(n, k)]['tau'])]
    S34 = [k for k in S if (IV[(n, k)][1] - IV[(n, k)][0]) <= Fr(3, 4) * Fr(PT[(n, k)]['tau'])]
    S12 = [k for k in S if (IV[(n, k)][1] - IV[(n, k)][0]) <= Fr(1, 2) * Fr(PT[(n, k)]['tau'])]
    SETS[n] = dict(S=S, S_3_4=S34, S_1_2=S12)
    st = SSETS['sizes'][str(n)]
    for nm in ('S', 'S_3_4', 'S_1_2'):
        if ['%.1f' % x for x in st[nm]] != SETS[n][nm]:
            FIND.append(dict(what='set %s n=%d differs' % (nm, n), mine=SETS[n][nm], stored=st[nm]))
    cands = [nm for nm in ('S_1_2', 'S_3_4', 'S') if len(SETS[n][nm]) >= 15]
    SETS[n]['S_p'] = cands[0] if cands else None
    if SETS[n]['S_p'] != st['S_p_name']:
        FIND.append(dict(what='S_p n=%d' % n, mine=SETS[n]['S_p'], stored=st['S_p_name']))
    for k in S:
        cmp('interval lo %d %s vs S_sets' % (n, k), float(IV[(n, k)][0]), st['intervals'][k]['exact']['lo'], 1e-12)
        cmp('interval hi %d %s vs S_sets' % (n, k), float(IV[(n, k)][1]), st['intervals'][k]['exact']['hi'], 1e-12)
say('\n== sets of (f3) from my own exact intervals ==')
for n in (57, 115):
    say(' n=%d |S| = %d (%s-%s), |S_3/4| = %d (%s-%s), |S_1/2| = %d (%s-%s), S_p = %s  (equal to out/S_sets.json: %s)'
        % (n, len(SETS[n]['S']), SETS[n]['S'][0], SETS[n]['S'][-1], len(SETS[n]['S_3_4']), SETS[n]['S_3_4'][0], SETS[n]['S_3_4'][-1],
           len(SETS[n]['S_1_2']), SETS[n]['S_1_2'][0], SETS[n]['S_1_2'][-1], SETS[n]['S_p'],
           not any('set ' in f['what'] or 'S_p' in f['what'] for f in FIND)))
RES['sets'] = SETS

# ------------------------------------------------------------------------------------------------ K. filter, n = 19
say('\n== K. the filter on the 45 training labels (keep iff CERTIFIED (exact)) and the n = 19 comparison ==')
RES['K'] = {}
SMAP = json.load(open(RD + '/out/map_summary.json'))
for n in (57, 115):
    miss = {k: abs(PT[(n, k)]['ms_real'] - PT[(n, k)]['ms_gs']) / PT[(n, k)]['tau'] for k in TRAIN}
    kept = SETS[n]['S']
    drop = [k for k in TRAIN if k not in kept]
    R = dict(kept=len(kept), max_miss_kept=max(miss[k] for k in kept), mean_miss_kept=float(np.mean([miss[k] for k in kept])),
             dropped=len(drop), dropped_within_half=sum(1 for k in drop if miss[k] <= 0.5),
             dropped_within_tau=sum(1 for k in drop if miss[k] <= 1.0), dropped_above_tau=sum(1 for k in drop if miss[k] > 1.0),
             kept_above_half=sum(1 for k in kept if miss[k] > 0.5), max_miss_dropped=max(miss[k] for k in drop))
    if len(C19) == 50:
        d19 = {k: abs(C19[k]['ms0'] - PT[(n, k)]['ms_gs']) / PT[(n, k)]['tau'] for k in KEYS}
        R['n19_max_over_kept'] = max(d19[k] for k in kept)
        R['n19_at_test'] = [d19[k] for k in TEST]
        R['n19_closer_than_label_kept'] = sum(1 for k in kept if d19[k] < miss[k])
        R['n19_closer_than_label_all50'] = sum(1 for k in KEYS if d19[k] < abs(PT[(n, k)]['ms_real'] - PT[(n, k)]['ms_gs']) / PT[(n, k)]['tau'])
        sc = SPRED['sizes'][str(n)]['n19_comparison']
        cmp('n19 max over kept %d' % n, R['n19_max_over_kept'], sc['max_over_kept'], 1e-6)
    RES['K'][n] = R
    say(' n=%d kept %d, largest miss kept %.4f tau (mean %.4f); dropped %d: within tau/2 %d, within tau %d, above tau %d (largest '
        '%.3f tau); kept above tau/2: %d' % (n, R['kept'], R['max_miss_kept'], R['mean_miss_kept'], R['dropped'],
                                           R['dropped_within_half'], R['dropped_within_tau'], R['dropped_above_tau'],
                                           R['max_miss_dropped'], R['kept_above_half']))
    if 'n19_max_over_kept' in R:
        say('   exact n = 19 against the truth: at most %.4f tau on the kept labels; %s tau at 1.1-1.4; closer to the truth than the '
            'label at %d of the %d kept and at %d of 50' % (R['n19_max_over_kept'], ' '.join('%.3f' % x for x in R['n19_at_test']),
                                                           R['n19_closer_than_label_kept'], R['kept'], R['n19_closer_than_label_all50']))
say(' stored filter block (sealed run), m_s: ' + json.dumps({k: {kk: vv for kk, vv in v.items() if not isinstance(vv, (list, dict))}
                                                              for k, v in SMAP['filter'].items() if k.endswith('m_s')})[:1200])

# ------------------------------------------------------------------------------------------------ M. like-for-like J*_s
say('\n== M. like-for-like J*_s for m_s (sector hypothesis; interpolated thresholds where no chain is stored) ==')
AM = json.load(open(RD + '/checks/rd_audit_map.json'))
RES['M'] = {}
for n in (57, 115):
    comp = sorted(float(k[1]) for k in PROW if k[0] == n and k[2] == 'm_s')
    st = {}
    for k in TRAIN:
        J = float(k)
        if (n, k, 'm_s') in PROW:
            st[k] = AM['L']['ms']['%d_%s' % (n, k)][0] == 'CERTIFIED'
        else:
            a = max(x for x in comp if x < J)
            b = min(x for x in comp if x > J)
            ea = PROW[(n, '%.1f' % a, 'm_s')]['eps_tau_out_lb']
            eb = PROW[(n, '%.1f' % b, 'm_s')]['eps_tau_out_lb']
            et = math.exp(math.log(ea) + (J - a) / (b - a) * (math.log(eb) - math.log(ea)))
            st[k] = (PT[(n, k)]['E_real'] - PT[(n, k)]['E0']) <= et
    js = None
    for k in reversed(TRAIN):
        if st[k]:
            js = k
        else:
            break
    RES['M'][n] = dict(jstar_s=js, n_cert_s=sum(st.values()), stored_jstar=SM['jstar']['%d_m_s_r1' % n].get('J_star_central'))
    say(' n=%d J*_s = %s, CERTIFIED_s at %d of 45 (stored figures-based J* = %s). A like-for-like number about in-sector states.'
        % (n, js, sum(st.values()), RES['M'][n]['stored_jstar']))

# ------------------------------------------------------------------------------------------------ J. (f3)
say('\n== J. (f3) the constructive test, every split end to end from my own exact intervals ==')


def fit(model, Jt, yt):
    Jt = np.asarray(Jt, float)
    yt = np.asarray(yt, float)
    if model == 'M1':
        A = np.column_stack([np.ones(len(Jt)), 1 / Jt])
        w = np.linalg.lstsq(A, yt, rcond=None)[0]
        return lambda x: w[0] + w[1] / np.asarray(x, float)
    if model == 'M2':
        A = np.column_stack([1 / Jt ** 2, 1 / Jt ** 4])
        w = np.linalg.lstsq(A, 1 - yt, rcond=None)[0]
        return lambda x: 1 - w[0] / np.asarray(x, float) ** 2 - w[1] / np.asarray(x, float) ** 4
    X = np.vander(1 / Jt, 4)
    w = np.linalg.solve(X.T @ X + 1e-8 * np.eye(4), X.T @ yt)
    return lambda x: np.vander(1 / np.atleast_1d(np.asarray(x, float)), 4) @ w


RES['J'] = {}
for n, nm, c in ((57, 'S', 0), (57, 'S_3_4', 1), (57, 'S_1_2', 2), (115, 'S', 0), (115, 'S_3_4', 1)):
    S = SETS[n][nm]
    L = len(S)
    ntr, nca = (6, 12) if L >= 20 else (4, 9)
    k = math.ceil((nca + 1) * 0.9)
    rng = np.random.default_rng([SEED, n, c])
    sst = SF3['sizes'][str(n)]['sets'][nm]
    agg = {m: dict(W=0, C=0, pairs=0, wmin=9.0, wmax=0.0, miss=0.0) for m in ('M1', 'M2', 'M0')}
    split_ok = 0
    dq = 0.0
    first = None
    for isp in range(200):
        perm = rng.permutation(L)
        tr = sorted(S[i] for i in perm[:ntr])
        ca = sorted(S[i] for i in perm[ntr:ntr + nca])
        qu = sorted(S[i] for i in perm[ntr + nca:])
        ss = sst['splits'][isp]
        split_ok += (['%.1f' % x for x in ss['train']] == tr and ['%.1f' % x for x in ss['cal']] == ca
                     and ['%.1f' % x for x in ss['query']] == qu)
        for m in ('M1', 'M2', 'M0'):
            if m == 'M0':
                tk = [x for x in TRAIN if x not in ca and x not in qu]
            else:
                tk = tr
            f = fit(m, [float(x) for x in tk], [PT[(n, x)]['ms_real'] for x in tk])
            sc = sorted(max(abs(float(f(float(x))) - float(IV[(n, x)][0])), abs(float(f(float(x))) - float(IV[(n, x)][1]))) for x in ca)
            q = sc[k - 1]
            wt = [2 * q / (0.06 * abs(PT[(n, x)]['ms_auth'])) for x in qu]
            ms = [abs(PT[(n, x)]['ms_auth'] - float(f(float(x)))) for x in qu]
            cov = [mm <= q for mm in ms]
            a = agg[m]
            a['W'] += all(w <= 1 for w in wt)
            a['C'] += sum(cov)
            a['pairs'] += len(qu)
            a['wmin'] = min(a['wmin'], min(wt))
            a['wmax'] = max(a['wmax'], max(wt))
            a['miss'] = max(a['miss'], max(mm / (0.06 * abs(PT[(n, x)]['ms_auth'])) for mm, x in zip(ms, qu)))
            sm = sst['models'][m]['splits'][isp]
            dq = max(dq, abs(q - sm['q']), max(abs(u - v) for u, v in zip(wt, sm['widths_tau'])))
            if cov != sm['covered']:
                FIND.append(dict(what='f3 coverage flags differ', where=[n, nm, m, isp]))
            if isp == 0 and m in ('M1', 'M2', 'M0'):
                first = first or {}
                first[m] = dict(train=tk if m != 'M0' else '%d couplings' % len(tk), cal=ca, query=qu, q=q, widths_tau=wt,
                                miss_tau=[mm / (0.06 * abs(PT[(n, x)]['ms_auth'])) for mm, x in zip(ms, qu)], covered=cov,
                                stored_q=sm['q'], stored_widths_tau=sm['widths_tau'])
    if split_ok != 200:
        FIND.append(dict(what='f3 splits differ from the stored ones', where=[n, nm], equal=split_ok))
    if dq > 1e-9:
        FIND.append(dict(what='f3 q or widths differ', where=[n, nm], diff=dq))
    out = {}
    for m in ('M1', 'M2', 'M0'):
        a = agg[m]
        out[m] = dict(W_splits=a['W'], C_pairs=a['C'], pairs=a['pairs'], width_min=a['wmin'], width_max=a['wmax'], largest_miss=a['miss'],
                      W_holds=a['W'] >= 180, C_holds=a['C'] >= 0.9 * a['pairs'])
        so = sst['models'][m]
        cmp('f3 frac W %d %s %s' % (n, nm, m), a['W'] / 200, so['frac_splits_W'], 1e-12)
        cmp('f3 frac C %d %s %s' % (n, nm, m), a['C'] / a['pairs'], so['frac_pairs_C'], 1e-12)
    out['outcome_M1_M2'] = 'PASS' if all(out[m]['W_holds'] and out[m]['C_holds'] for m in ('M1', 'M2')) else 'FAIL'
    out['sizes'] = [L, ntr, nca, L - ntr - nca, k]
    out['splits_equal_to_stored'] = split_ok
    out['max_abs_diff_q_widths'] = dq
    out['split0'] = first
    RES['J']['%d_%s' % (n, nm)] = out
    say(' n=%d %-5s (%d couplings: %d train / %d calibration / %d query, k = %d): splits equal to the stored ones %d of 200; '
        'max |mine - stored| in q and widths %.1e' % (n, nm, L, ntr, nca, L - ntr - nca, k, split_ok, dq))
    for m in ('M1', 'M2', 'M0'):
        o = out[m]
        say('    %s: (W) %d of 200 splits, (C) %d of %d pairs, 2q = %.4f-%.4f tau, largest miss %.4f tau'
            % (m, o['W_splits'], o['C_pairs'], o['pairs'], o['width_min'], o['width_max'], o['largest_miss']))
    say('    outcome for M1 and M2 by the declared rule: %s' % out['outcome_M1_M2'])
f0 = RES['J']['57_S_1_2']['split0']
say(' split 0 of the primary set (n = 57, S_1/2), end to end:')
say('   train %s | calibration %s | query %s' % (f0['M1']['train'], f0['M1']['cal'], f0['M1']['query']))
for m in ('M1', 'M2', 'M0'):
    say('   %s: q = %.9f (stored %.9f); 2q/tau(x) = %s; miss/tau = %s; covered %s'
        % (m, f0[m]['q'], f0[m]['stored_q'], ' '.join('%.4f' % x for x in f0[m]['widths_tau']),
           ' '.join('%.4f' % x for x in f0[m]['miss_tau']), f0[m]['covered']))
dts = {n: (max(PT[(n, k)]['ms_auth'] for k in SETS[n][SETS[n]['S_p']]) - min(PT[(n, k)]['ms_auth'] for k in SETS[n][SETS[n]['S_p']]))
       for n in (57, 115)}
for n in (57, 115):
    Sp = SETS[n][SETS[n]['S_p']]
    t = [dts[n] / (0.06 * abs(PT[(n, k)]['ms_auth'])) for k in (Sp[0], Sp[-1])]
    say(' n=%d: change of the true m_s over S_p (%s-%s): %.3f-%.3f tau' % (n, Sp[0], Sp[-1], min(t), max(t)))
    RES['J']['truth_change_over_Sp_%d' % n] = [min(t), max(t)]

# ------------------------------------------------------------------------------------------------ N. L1, L2
say('\n== N. L1 and L2 for the cubic in 1/Jz trained on the 45 real labels (own code; jackknife over couplings) ==')
RES['N'] = {}
for n in (57, 115):
    Jt = [float(k) for k in TRAIN]
    out = {}
    for src in ('real', 'dmrg'):
        yt = [PT[(n, k)]['ms_real' if src == 'real' else 'ms_auth'] for k in TRAIN]
        f = fit('M0', Jt, yt)
        res = []
        for i in range(45):
            fi = fit('M0', Jt[:i] + Jt[i + 1:], yt[:i] + yt[i + 1:])
            res.append(abs(yt[i] - float(fi(Jt[i]))))
        q = sorted(res)[math.ceil(46 * 0.9) - 1]
        miss = [abs(float(f(float(k))) - PT[(n, k)]['ms_auth']) / (0.06 * abs(PT[(n, k)]['ms_auth'])) for k in TEST]
        cov = [abs(float(f(float(k))) - PT[(n, k)]['ms_auth']) <= q for k in TEST]
        wid = [2 * q / (0.06 * abs(PT[(n, k)]['ms_auth'])) for k in TEST]
        out[src] = dict(miss_tau=miss, covered=cov, width_tau=wid)
    RES['N'][n] = out
    say(' n=%d real labels: miss at 1.1-1.4 = %s tau (L1 holds: %s); standard interval %.3f-%.3f tau wide, truth covered at %d of 4 '
        '(L2 holds: %s)' % (n, ' '.join('%.3f' % x for x in out['real']['miss_tau']), all(x > 1 for x in out['real']['miss_tau']),
                           min(out['real']['width_tau']), max(out['real']['width_tau']), sum(out['real']['covered']),
                           sum(out['real']['covered']) == 0))
    say('        control on DMRG labels: miss %s tau; interval %.4f-%.4f tau wide; truth covered at %d of 4'
        % (' '.join('%.3f' % x for x in out['dmrg']['miss_tau']), min(out['dmrg']['width_tau']), max(out['dmrg']['width_tau']),
           sum(out['dmrg']['covered'])))

RES['findings'] = FIND
say('\n== disagreements with the stored outputs beyond rounding: %d ==' % len(FIND))
for f in FIND[:40]:
    say('  ', json.dumps(f)[:400])


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(x) for x in o]
    if isinstance(o, Fr):
        return str(o)
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


json.dump(clean(RES), open(OUTJ, 'w'), indent=1)
say('written', OUTJ, '(%.0f s)' % (time.time() - T00))
