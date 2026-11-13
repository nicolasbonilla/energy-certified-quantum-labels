# -*- coding: utf-8 -*-
"""rd-audit (R10, 2026-11-12): INDEPENDENT recomputation of the map on the public data of arXiv:2606.15983.

Own code. Imports nothing from real_data/code/ (the sealed code) and nothing from the stored map code.
Reads: converted/*.json (plain JSON), the stored certificates (*_cert.json, *_ver.json), the stored state
records (map/laptop_analysis/out/states/*.json), chains/thr/chk of the stored map, summary_map.json (references),
and, only to COMPARE, the outputs of the sealed run (out/map_rows.json, out/map_summary.json, out/learn/f2_floor.json).

Parts: B departure from the sector; C exact intervals (fractions.Fraction); D J*_exact and counts, both tolerances;
E not-certified rows from explicit states (own hull + linear program); F accuracy factors, both forms;
I floor of (f2); L like-for-like statuses at E_real against the prediction (165 rows).
usage: python -B -I rd_audit_map.py
"""
import glob
import hashlib
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

ROOT = 'C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work'
RUNS = ROOT + '/phase3/full_runs'
RD = RUNS + '/real_data'
MAP = RUNS + '/map/laptop_analysis'
OUTJ = RD + '/checks/rd_audit_map.json'
DECL = '6dfbc5681a7b4708ba790e1dd3139d8efdcccb9ced24e5ab2ce4b5a7a209ffaa'
PINS = {'real_n57.json': 'ec96cd6d49a160ba91b38a08f987d221aa01c465c470e0eb17c13f9bacedc4dd',
        'real_n115.json': '5890160c5ff0992b0859ce44fba3a74d1aff6fa6e005f8ef0d0db4f4233d0002',
        'lattice_maps.json': 'a066581a316dbcfacabe8b50f318dc323fc05eaf67c67f99209cc4282586ec81'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(RD + '/DECLARATION.md') == DECL, 'declaration hash'
for _k, _v in PINS.items():
    assert sha(RD + '/converted/' + _k) == _v, _k

GRID = [1.1, 1.2, 1.3, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0, 3.3, 3.6, 4.0, 4.5, 5.0, 5.5, 6.0]
KEYS = ['%.1f' % (k / 10) for k in range(11, 61)]
TRAIN = KEYS[5:]
TEST = KEYS[:4]
ALLOW = Fr(1, 10 ** 6)
DELTA = 1e-6
LAB7 = ['m_s', 'Czz_bar', 'C2_bar', 'Z_bulk', 'Z_boundary', 'Czz_edge', 'Z_loop']
IK = {'m_s': 'm_s', 'Czz_bar': 'Czz_bar', 'C2_bar': 'C2_bar', 'Z_bulk': 'Z_bulk', 'Z_boundary': 'Z_boundary',
      'Czz_edge': 'Czz_edge_loc', 'Z_loop': 'Z_loop'}
RES = {}
FIND = []          # disagreements with the stored outputs beyond rounding


def say(*a):
    print(*a)
    sys.stdout.flush()


# ------------------------------------------------------------------------------------------------ lattice (own)
LM = json.load(open(RD + '/converted/lattice_maps.json'))['maps']


def graph(n):
    m = LM[str(n)]
    edges = sorted(tuple(sorted(e)) for e in m['edges_sorted_unique'])
    col = m['colour_with_node0_as_1']
    maj = 1 if 2 * sum(col) > n else 0
    eta = [1 if c == maj else -1 for c in col]
    nb = {i: set() for i in range(n)}
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    nn2 = set()
    for j in range(n):
        ll = sorted(nb[j])
        for x in range(len(ll)):
            for y in range(x + 1, len(ll)):
                nn2.add((ll[x], ll[y]))
    return dict(n=n, edges=edges, eta=eta, nn2=sorted(nn2), M0=sum(eta))


G = {n: graph(n) for n in (57, 115)}
for n, d in ((57, 5), (115, 7)):
    pg = json.load(open(MAP + '/code/graphs/hh_d%d.json' % d))
    assert sorted(tuple(sorted(e)) for e in pg['edges']) == G[n]['edges'], 'edge sets differ'
    assert [int(x) for x in pg['eta']] == G[n]['eta'], 'eta differs'
    assert G[n]['M0'] == {57: 9, 115: 19}[n] and len(G[n]['nn2']) == {57: 87, 115: 185}[n]
    G[n]['sz'] = pg['sz']
say('lattice: edges', {n: len(G[n]['edges']) for n in G}, 'second neighbours', {n: len(G[n]['nn2']) for n in G},
    'M0', {n: G[n]['M0'] for n in G}, '(repository lists = project graphs, eta equal)')

# ------------------------------------------------------------------------------------------------ data and truth
D = {n: json.load(open(RD + '/converted/real_n%d.json' % n)) for n in (57, 115)}
SM = json.load(open(MAP + '/summary_map.json'))
PROW = {(r['n'], '%.1f' % r['Jz'], r['label']): r for r in SM['rows']}
PE0 = {k: v['E0'] for k, v in SM['refs'].items()}


def point(n, key):
    g = G[n]
    rf = D[n]['skqd_random_flip'][key]
    dm = D[n]['dmrg'][key]
    z = rf['z_basis_opt']
    zd = dm['z']
    pr = {tuple(sorted(p)): v for p, v in zip(rf['2_nn_corr_pairs_zz_basis_opt'], rf['2_nn_corr_funcs_zz_basis_opt'])}
    pd = {tuple(sorted(p)): v for p, v in zip(dm['2_nn_corr_pairs'], dm['2_nn_corr_funcs_zz'])}
    assert len(pr) == len(pd) == len(g['edges']) + len(g['nn2'])
    P = dict(n=n, key=key, J=float(key), E_real=rf['final_global_energy'], E0_auth=dm['ground_state_energy'],
             Mx=sum(Fr(x) for x in z), M_float=math.fsum(z),
             ms_real=math.fsum(e * x for e, x in zip(g['eta'], z)) / n,
             ms_auth=math.fsum(e * x for e, x in zip(g['eta'], zd)) / n,
             czz_real=math.fsum(pr[e] for e in g['edges']) / len(g['edges']),
             czz_auth=math.fsum(pd[e] for e in g['edges']) / len(g['edges']))
    P['E0'] = PE0.get('%d_%s' % (n, key), P['E0_auth'])
    P['E0_src'] = 'project' if '%d_%s' % (n, key) in PE0 else 'authors'
    for lab, au in (('m_s', P['ms_auth']), ('Czz_bar', P['czz_auth'])):
        r = PROW.get((n, key, lab))
        P['O_' + lab] = r['O_GS'] if r else au
        P['tau_' + lab] = 0.06 * abs(P['O_' + lab])
    P['q'] = float((g['M0'] - P['Mx']) / 2)
    P['eps'] = P['E_real'] - P['E0']
    P['de'] = P['eps'] / n
    return P


PT = {(n, k): point(n, k) for n in (57, 115) for k in KEYS}

# stored outputs of the sealed run (comparison only)
ROWS = json.load(open(RD + '/out/map_rows.json'))['rows']
SROW = {(r['n'], r['key'], r['label']): r for r in ROWS if r.get('group') == 'dataset'}
SSUM = json.load(open(RD + '/out/map_summary.json'))


def cmp(name, mine, stored, tol=1e-9, rel=False):
    """Record a disagreement beyond rounding."""
    if mine is None or stored is None:
        if mine is not stored:
            FIND.append(dict(what=name, mine=mine, stored=stored))
        return
    d = abs(mine - stored)
    if rel:
        d = d / max(abs(stored), 1e-300)
    if d > tol:
        FIND.append(dict(what=name, mine=mine, stored=stored, diff=d))
    return d


# ------------------------------------------------------------------------------------------------ B. sector
say('\n== B. departure from the sector: M_real - M_0 and q = (M_0 - M_real)/2 (own sums; exact rationals) ==')
B = {}
for n in (57, 115):
    dev = {k: float(PT[(n, k)]['Mx'] - G[n]['M0']) for k in KEYS}
    worst = 0.0
    for k in KEYS:
        s = SROW[(n, k, 'm_s')]
        worst = max(worst, abs(float(PT[(n, k)]['Mx']) - s['M_real']), abs(PT[(n, k)]['q'] - s['q']))
        if Fr(s['M_real_exact']) != PT[(n, k)]['Mx']:
            FIND.append(dict(what='M_real exact %d %s' % (n, k), mine=str(PT[(n, k)]['Mx']), stored=s['M_real_exact']))
    B[n] = dict(dev=dev, n_negative=sum(1 for v in dev.values() if v < 0), min=min(dev.values()), max=max(dev.values()),
                within_0p05=sum(1 for v in dev.values() if abs(v) <= 0.05),
                q_max=max(PT[(n, k)]['q'] for k in KEYS), q_min=min(PT[(n, k)]['q'] for k in KEYS),
                max_abs_diff_vs_stored=worst)
    say(' n=%d  negative at %d of 50; range [%.6f, %.6f]; within 0.05 at %d; q in [%.5f, %.5f]; max |mine-stored| %.1e'
        % (n, B[n]['n_negative'], B[n]['min'], B[n]['max'], B[n]['within_0p05'], B[n]['q_min'], B[n]['q_max'], worst))
    say('   five couplings (M_real - M_0 | q): ' + '; '.join('%s: %.6f | %.6f' % (k, dev[k], PT[(n, k)]['q'])
                                                              for k in ('1.1', '1.6', '3.4', '4.0', '6.0')))
RES['B_sector'] = B

# ------------------------------------------------------------------------------------------------ C. certificates
say('\n== C. exact intervals from the stored certificates (fractions.Fraction) ==')
files = []
for d in ('rigor/out_20261031T073328Z', 'rigor/out_20261031T100015Z', 'final_tests'):
    files += sorted(glob.glob(RUNS + '/' + d + '/**/*_cert.json', recursive=True))
CERT = []
seen = set()
for f in files:
    b = open(f, 'rb').read()
    h = hashlib.sha256(b).hexdigest()
    if h in seen:
        continue
    seen.add(h)
    c = json.loads(b)
    n = {'hh_d5.json': 57, 'hh_d7.json': 115}.get(c['graph'])
    t = c['task']
    if n is None or t['kind'] not in ('m_s', 'Czz_bar', 'H'):
        continue
    den = 2 ** int(c['K'])
    csum = Fr(sum(int(x) for x in c['t']), den)
    mu = Fr(int(c['mu']), den)
    assert Fr(c['E_claim']) == csum - mu * G[n]['M0'], 'E_claim identity ' + f
    v = json.load(open(f.replace('_cert.json', '_ver.json')))
    assert v['ok'] is True and v['cert_sha256'] == h and Fr(v['E_LB_exact']) == Fr(c['E_claim']), 'ver record ' + f
    CERT.append(dict(n=n, kind=t['kind'], sigma=int(t.get('sigma') or 0), lam=Fr(str(t.get('lam', 0))),
                     J=Fr(str(t['Jz'])), c=csum, mu=mu, name=os.path.basename(f)[:-10], sha=h, path=f))
say(' files %d, distinct %d, used (n = 57, 115; kinds m_s, Czz_bar, H): %d = %d + %d; every one has a verification '
    'record with ok = true, the same SHA-256 and the same exact bound'
    % (len(files), len(seen), len(CERT), sum(1 for c in CERT if c['n'] == 57), sum(1 for c in CERT if c['n'] == 115)))
RES['C_certificates'] = dict(files=len(files), distinct=len(seen), used=len(CERT),
                             used_57=sum(1 for c in CERT if c['n'] == 57), used_115=sum(1 for c in CERT if c['n'] == 115),
                             mu_range={str(n): [float(min(c['mu'] for c in CERT if c['n'] == n)),
                                                float(max(c['mu'] for c in CERT if c['n'] == n))] for n in (57, 115)})


def best(bounds, E, M, allow):
    """min over the pool of (E - c + mu M [+ |mu| allowance]) / den ; returns (value, names)."""
    out = None
    for (cc, mu, den, nm) in bounds:
        val = (E - cc + mu * M + (abs(mu) * ALLOW if allow else 0)) / den
        if out is None or val < out[0]:
            out = (val, nm)
    return out


def side(bounds, E, Mreal, M0):
    a = best(bounds, E, Mreal, True)
    b = best(bounds, E, Fr(M0), False)
    return (a[0], a[1], 'M_real', a[0], b[0]) if a[0] >= b[0] else (b[0], b[1], 'M_0', a[0], b[0])


def ms_bounds(n, J, sg):
    cs = [c for c in CERT if c['n'] == n and c['kind'] == 'm_s' and c['sigma'] == sg]
    bo = [(c['c'], c['mu'], c['lam'] * n, (c['name'],)) for c in cs if c['J'] == J]
    for a in cs:
        if a['J'] >= J:
            continue
        for b in cs:
            if b['J'] <= J:
                continue
            t = (b['J'] - J) / (b['J'] - a['J'])
            bo.append((t * a['c'] + (1 - t) * b['c'], t * a['mu'] + (1 - t) * b['mu'],
                       (t * a['lam'] + (1 - t) * b['lam']) * n, (a['name'], b['name'])))
    return bo


def czz_bounds(n, J):
    ne = len(G[n]['edges'])
    up, dn = [], []
    for c in CERT:
        if c['n'] != n or c['kind'] not in ('Czz_bar', 'H'):
            continue
        Jp = c['J'] - 4 * c['sigma'] * c['lam'] if c['kind'] == 'Czz_bar' else c['J']
        if Jp < J:
            up.append((c['c'], c['mu'], (J - Jp) * ne / 4, (c['name'],)))
        elif Jp > J:
            dn.append((c['c'], c['mu'], (Jp - J) * ne / 4, (c['name'],)))
    return up, dn


RANGE = {57: (Fr(34, 10), Fr(6)), 115: (Fr(4), Fr(6))}


def interval(n, key, label):
    P = PT[(n, key)]
    J = Fr(key)
    E = Fr(P['E_real']) + ALLOW
    if label == 'm_s':
        bp, bm = ms_bounds(n, J, +1), ms_bounds(n, J, -1)
    else:
        bp, bm = czz_bounds(n, J)
    if not bp or not bm:
        return None
    sp = side(bp, E, P['Mx'], G[n]['M0'])
    sm = side(bm, E, P['Mx'], G[n]['M0'])
    hi, lo = min(sp[0], Fr(1)), -min(sm[0], Fr(1))
    tau = Fr(P['tau_' + label])
    w = hi - lo
    inr = RANGE[n][0] <= J <= RANGE[n][1]
    tau_rf = Fr(3, 50) * min(abs(lo), abs(hi)) if lo * hi > 0 else Fr(0)
    w0 = min(sp[4], Fr(1)) + min(sm[4], Fr(1))                    # width at M = M_0 alone
    return dict(lo=lo, hi=hi, w=w, tau=tau, in_range=inr, cert=bool(inr and w <= tau), cert_rf=bool(inr and w <= tau_rf),
                w_tau=float(w / tau), w_tau_rf=float(w / tau_rf) if tau_rf else None, w_tau_M0=float(w0 / tau),
                dec=(sp[2], sm[2]), names=(sp[1], sm[1]), n_bounds=(len(bp), len(bm)))


EX = {}
n_cmp = n_eq = 0
for n in (57, 115):
    for lab in ('m_s', 'Czz_bar'):
        for k in KEYS:
            I = interval(n, k, lab)
            EX[(n, k, lab)] = I
            s = SROW[(n, k, lab)]['exact']
            if I is None:
                if s.get('exists'):
                    FIND.append(dict(what='exact interval exists in the stored output, not in mine', row=[n, k, lab]))
                continue
            if not s.get('exists'):
                FIND.append(dict(what='exact interval exists in mine, not in the stored output', row=[n, k, lab]))
                continue
            n_cmp += 1
            same = (Fr(s['lo_exact']) == I['lo'] and Fr(s['hi_exact']) == I['hi'] and bool(s['certified']) == I['cert']
                    and bool(s['certified_rf']) == I['cert_rf'])
            n_eq += same
            if not same:
                FIND.append(dict(what='exact interval differs', row=[n, k, lab], mine=[float(I['lo']), float(I['hi']), I['cert'],
                            I['cert_rf']], stored=[s['lo'], s['hi'], s['certified'], s['certified_rf']]))
say(' rows with an interval on both sides: %d compared with the stored output, %d identical as exact rationals '
    '(both ends, both flags)' % (n_cmp, n_eq))
SIX = {57: ['3.4', '3.5', '3.6', '4.0', '5.0', '6.0'], 115: ['4.0', '4.1', '4.5', '5.0', '5.5', '6.0']}
RES['C_six'] = {}
for n in (57, 115):
    say(' n=%d m_s, six couplings (lo, hi, width/tau, width/tau_rf, width/tau at M_0 alone, CERTIFIED, decisive M +/-):' % n)
    for k in SIX[n]:
        I = EX[(n, k, 'm_s')]
        P = PT[(n, k)]
        inside = I['lo'] <= Fr(P['ms_real']) <= I['hi'] and I['lo'] <= Fr(P['O_m_s']) <= I['hi']
        RES['C_six']['%d_%s' % (n, k)] = dict(lo=float(I['lo']), hi=float(I['hi']), w_tau=I['w_tau'], w_tau_rf=I['w_tau_rf'],
                                               w_tau_M0=I['w_tau_M0'], cert=I['cert'], cert_rf=I['cert_rf'], dec=I['dec'],
                                               names=[list(x) for x in I['names']], label=P['ms_real'], truth=P['O_m_s'],
                                               label_and_truth_inside=bool(inside),
                                               stored_w_tau=SROW[(n, k, 'm_s')]['exact'].get('width_over_tau'))
        say('   Jz %s: [%.7f, %.7f]  %.4f  %.4f  %.4f  %s  %s/%s  label %.6f truth %.6f inside %s'
            % (k, float(I['lo']), float(I['hi']), I['w_tau'], I['w_tau_rf'], I['w_tau_M0'], I['cert'], I['dec'][0], I['dec'][1],
               P['ms_real'], P['O_m_s'], inside))
    k = '3.9' if n == 115 else '3.3'
    say('   Jz %s (just below the certificate range): interval exists in mine: %s' % (k, EX[(n, k, 'm_s')] is not None))

# ------------------------------------------------------------------------------------------------ D. J* and counts
say('\n== D. J*_exact and counts out of the 45 training couplings, both tolerances ==')


def jstar(flags):
    """smallest training Jz from which every larger training point is certified."""
    js = None
    for k in reversed(TRAIN):
        if flags[k]:
            js = k
        else:
            break
    return js


RES['D'] = {}
for n in (57, 115):
    for lab in ('m_s', 'Czz_bar'):
        f = {k: bool(EX[(n, k, lab)] and EX[(n, k, lab)]['cert']) for k in TRAIN}
        frf = {k: bool(EX[(n, k, lab)] and EX[(n, k, lab)]['cert_rf']) for k in TRAIN}
        ws = [EX[(n, k, lab)]['w_tau'] for k in TRAIN if f[k]]
        inr = [k for k in TRAIN if EX[(n, k, lab)] and EX[(n, k, lab)]['in_range']]
        R = dict(jstar=jstar(f), n_cert=sum(f.values()), jstar_rf=jstar(frf), n_cert_rf=sum(frf.values()),
                 w_tau_min=min(ws), w_tau_max=max(ws), in_range=len(inr),
                 in_range_not_certified=[k for k in inr if not f[k]],
                 widen_vs_M0_max=max(EX[(n, k, lab)]['w_tau'] - EX[(n, k, lab)]['w_tau_M0'] for k in inr),
                 outside_range_within_tau=[k for k in TRAIN if EX[(n, k, lab)] and not EX[(n, k, lab)]['in_range']
                                           and EX[(n, k, lab)]['w'] <= EX[(n, k, lab)]['tau']])
        RES['D']['%d_%s' % (n, lab)] = R
        sj = SSUM['jstar'].get('%d_%s' % (n, lab), {})
        say(' n=%d %-7s J*_exact %s (%d of 45); reference-free %s (%d of 45); widths %.4f-%.4f tau; in range %d, not certified '
            'there %s; widening against M_0 alone at most %.4f tau; within tau outside the range at %s'
            % (n, lab, R['jstar'], R['n_cert'], R['jstar_rf'], R['n_cert_rf'], R['w_tau_min'], R['w_tau_max'], R['in_range'],
               R['in_range_not_certified'], R['widen_vs_M0_max'], R['outside_range_within_tau']))
        RES['D']['%d_%s' % (n, lab)]['stored_jstar_block'] = {kk: vv for kk, vv in sj.items() if not isinstance(vv, (list, dict))}

# ------------------------------------------------------------------------------------------------ E. explicit states
say('\n== E. not-certified side from the stored explicit states (own hull; linear program as a second method) ==')
ST = {}
for p in glob.glob(MAP + '/out/states/*.json'):
    r = json.load(open(p))
    ST[r['sid']] = r
BYNJ = {}
for r in ST.values():
    BYNJ.setdefault((r['n'], '%.1f' % r['Jz']), []).append(r)


def in_sector(r, n):
    i = r['indep']
    return bool(r.get('in_sector')) and abs(i['sum_Z'] - G[n]['M0']) < 1e-9 and i['sector_var'] < 1e-12 \
        and abs(r['sector_s'] - G[n]['sz']) < 1e-9


def bsum(r):
    return 0.25 * math.fsum(r['indep']['Czz_edges'])


def pool(n, key, label):
    """(energies at the row's coupling, labels, kind, couplings used)."""
    J = float(key)
    own = (n, key, label) in PROW
    if own:
        srcs = [key]
    else:
        lo = max(g for g in GRID if g < J)
        hi = min(g for g in GRID if g > J)
        srcs = ['%.1f' % lo, '%.1f' % hi]
    E, o = [], []
    for s in srcs:
        for r in BYNJ[(n, s)]:
            if not in_sector(r, n) or r['indep'].get(IK[label]) is None:
                continue
            E.append(r['indep']['E'] + (J - float(s)) * bsum(r))
            o.append(r['indep'][IK[label]])
    return np.array(E), np.array(o), ('stored chain' if own else 're-evaluated'), srcs


def ref_state(n, key):
    J = float(key)
    if J in GRID:
        cands = [key]
    else:
        cands = ['%.1f' % max(g for g in GRID if g < J), '%.1f' % min(g for g in GRID if g > J)]
    out = None
    for s in cands:
        r = ST['n%d_J%s_R3_sz_minus' % (n, s)]
        assert abs(r['indep']['sum_Z'] - (G[n]['M0'] - 2)) < 1e-9
        e = r['indep']['E'] + (J - float(s)) * bsum(r)
        if out is None or e < out[0]:
            out = (e, s, r)
    return out


def hull(E, o, Ecap):
    a = E <= Ecap
    if not a.any():
        return None
    hi, lo = o[a].max(), o[a].min()
    b = ~a
    if b.any():
        t = (Ecap - E[a][:, None]) / (E[b][None, :] - E[a][:, None])
        val = (1 - t) * o[a][:, None] + t * o[b][None, :]
        hi, lo = max(hi, val.max()), min(lo, val.min())
    return float(lo), float(hi)


def hull_lp(E, o, Ecap):
    from scipy.optimize import linprog
    out = []
    for sgn in (+1, -1):
        r = linprog(sgn * o, A_ub=E[None, :] - Ecap, b_ub=[0.0], A_eq=np.ones((1, len(E))), b_eq=[1.0],
                    bounds=(0, None), method='highs')
        assert r.status == 0
        out.append(sgn * r.fun)
    return out[0], out[1]


def lower(n, key, label, tau):
    P = PT[(n, key)]
    E, o, kind, srcs = pool(n, key, label)
    er, sref, r = ref_state(n, key)
    q = P['q']
    Es = (P['E_real'] - q * er) / (1 - q)
    h = hull(E, o, Es - DELTA)
    if h is None:
        return dict(exists=False)
    w = (1 - q) * (h[1] - h[0])
    orf = r['indep'][IK[label]]
    return dict(exists=True, Estar=Es, hull=h, w_lower=w, w_lower_tau=w / tau, not_cert=bool(w >= tau), q=q, kind=kind,
                srcs=srcs, ref=sref, E_ref=er, pool=len(E), min_pool_E=float(E.min()),
                witness=[(1 - q) * h[0] + q * orf, (1 - q) * h[1] + q * orf])


LOW = {}
worst = dict(Estar=0.0, hull=0.0, w=0.0)
nflag = 0
for n in (57, 115):
    for k in KEYS:
        P = PT[(n, k)]
        L = lower(n, k, 'm_s', P['tau_m_s'])
        LOW[(n, k)] = L
        s = SROW[(n, k, 'm_s')]['lower']
        worst['Estar'] = max(worst['Estar'], abs(L['Estar'] - s['Estar']))
        worst['hull'] = max(worst['hull'], abs(L['hull'][0] - s['hull'][0]), abs(L['hull'][1] - s['hull'][1]))
        worst['w'] = max(worst['w'], abs(L['w_lower_tau'] - s['w_lower_over_tau']))
        if bool(s['not_certified']) != L['not_cert'] or s['pool_size'] != L['pool']:
            nflag += 1
            FIND.append(dict(what='explicit-state row differs', row=[n, k], mine=[L['not_cert'], L['pool'], L['w_lower_tau']],
                             stored=[s['not_certified'], s['pool_size'], s['w_lower_over_tau']]))
for kk, vv in worst.items():
    if vv > 1e-9:
        FIND.append(dict(what='explicit-state side, largest difference in ' + kk, diff=vv))
say(' m_s, 100 rows: largest |mine - stored| in E* %.1e, hull ends %.1e, lower width / tau %.1e; flag or pool-size '
    'mismatches %d' % (worst['Estar'], worst['hull'], worst['w'], nflag))
RES['E_rows'] = {}
for (n, k) in ((57, '1.1'), (57, '3.1'), (115, '1.4'), (115, '3.0')):
    L = LOW[(n, k)]
    E, o, kind, srcs = pool(n, k, 'm_s')
    lp = hull_lp(E, o, L['Estar'] - DELTA)
    P = PT[(n, k)]
    RES['E_rows']['%d_%s' % (n, k)] = dict(L, lp_hull=[lp[0], lp[1]], tau=P['tau_m_s'], E_real=P['E_real'],
                                             stored_w_lower_tau=SROW[(n, k, 'm_s')]['lower']['w_lower_over_tau'],
                                             E0=P['E0'], min_pool_minus_E0=L['min_pool_E'] - P['E0'])
    say(' n=%d Jz %s: q %.6f, reference R3 of %s, E* %.6f, pool %d (%s %s), hull [%.6f, %.6f] (LP [%.6f, %.6f]), '
        '(1-q) width = %.4f tau -> NOT CERTIFIED %s (stored %.4f)'
        % (n, k, L['q'], L['ref'], L['Estar'], L['pool'], L['kind'], L['srcs'], L['hull'][0], L['hull'][1], lp[0], lp[1],
           L['w_lower_tau'], L['not_cert'], SROW[(n, k, 'm_s')]['lower']['w_lower_over_tau']))
    assert abs(lp[0] - L['hull'][0]) < 1e-8 and abs(lp[1] - L['hull'][1]) < 1e-8, (lp, L['hull'])
RES['E_summary'] = {}
for n in (57, 115):
    nc = [k for k in KEYS if LOW[(n, k)]['not_cert']]
    ex = [k for k in TRAIN if EX[(n, k, 'm_s')] and EX[(n, k, 'm_s')]['cert']]
    gray = [k for k in TRAIN if k not in nc and k not in ex]
    RES['E_summary'][n] = dict(not_certified=nc, n_not_certified_training=len([k for k in nc if k in TRAIN]), gray_training=gray,
                               reeval=[k for k in nc if LOW[(n, k)]['kind'] == 're-evaluated'])
    say(' n=%d m_s: NOT CERTIFIED (explicit states) at %s..%s (%d couplings; %d of the 45 training); GRAY at %s; rows resting on '
        're-evaluated energies: %d' % (n, nc[0], nc[-1], len(nc), len([k for k in nc if k in TRAIN]), gray,
                                       len(RES['E_summary'][n]['reeval'])))
# the witnesses lie inside the exact interval wherever both exist (consistency of the two sides)
viol = 0
for n in (57, 115):
    for k in KEYS:
        I = EX[(n, k, 'm_s')]
        if I is not None:
            wlo, whi = LOW[(n, k)]['witness']
            viol += not (float(I['lo']) <= wlo and whi <= float(I['hi']))
say(' explicit witnesses inside the exact interval of the same row (m_s rows with both): violations %d' % viol)
RES['E_witness_outside_exact'] = viol

# ------------------------------------------------------------------------------------------------ F. accuracy factor
say('\n== F. accuracy factor at the test couplings (own threshold from the in-sector pool, q = 0) ==')


def eps_tau_in(n, key, label, E0, tau):
    E, o, kind, srcs = pool(n, key, label)

    def w(e):
        h = hull(E, o, E0 + e - DELTA)
        return (h[1] - h[0]) if h else 0.0
    lo, hi = 0.0, float(E.max() - E0) + 1.0
    if w(hi) < tau:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if w(mid) >= tau:
            hi = mid
        else:
            lo = mid
    return hi


RES['F'] = {}
for n in (57, 115):
    for lab in ('m_s', 'Czz_bar'):
        fa, fb, st_in = [], [], []
        for k in TEST + ['1.5']:
            P = PT[(n, k)]
            et = eps_tau_in(n, k, lab, P['E0'], P['tau_' + lab])
            ds = et / n
            fa.append(P['de'] / ds)
            fb.append(PT[(n, '1.6')]['de'] / ds)
            r = PROW.get((n, k, lab))
            if r is not None:
                cmp('de_star_in %d %s %s (mine against the stored map)' % (n, k, lab), ds, r['de_star_in'], 1e-6, rel=True)
                st_in.append(r['de_star_in'])

        def down2(x):
            e = math.floor(math.log10(x)) - 1
            return math.floor(x / 10 ** e) * 10 ** e
        RES['F']['%d_%s' % (n, lab)] = dict(F_A=fa, F_B=fb, headline_A=down2(min(fa[:4])), headline_B=down2(min(fb[:4])),
                                             de_star_in_stored=st_in)
        say(' n=%d %-7s F_A (1.1-1.4 | 1.5) %s | %.2f   headline: more than %g;   F_B %s | %.2f   headline: more than %g'
            % (n, lab, ' '.join('%.2f' % x for x in fa[:4]), fa[4], down2(min(fa[:4])),
               ' '.join('%.2f' % x for x in fb[:4]), fb[4], down2(min(fb[:4]))))
say(' stored accuracy block (sealed run), verbatim keys: ' + json.dumps(SSUM['accuracy_factors'])[:900])
RES['F_stored'] = SSUM['accuracy_factors']

# ------------------------------------------------------------------------------------------------ I. floor of (f2)
say('\n== I. the learner-independent floor of (f2): 42nd smallest of the 45 lower widths, in units of tau(x) ==')
F2 = json.load(open(RD + '/out/learn/f2_floor.json'))['sizes']
RES['I'] = {}
for n in (57, 115):
    w = sorted((LOW[(n, k)]['w_lower'], k) for k in TRAIN)
    floor, kf = w[41]
    ft = {k: floor / (0.06 * abs(PT[(n, k)]['ms_auth'])) for k in KEYS}
    s = F2[str(n)]
    cmp('f2 floor n=%d' % n, floor, s['floor'], 1e-9)
    for k in TEST:
        cmp('f2 floor/tau n=%d %s' % (n, k), ft[k], s['floor_over_tau'][k], 1e-8)
    RES['I'][n] = dict(floor=floor, set_by=kf, four_widest=[x[1] for x in w[41:]], floor_over_tau_test=[ft[k] for k in TEST],
                       min_over_all=min(ft.values()), stored_floor=s['floor'],
                       stored_test=[s['floor_over_tau'][k] for k in TEST], holds=all(ft[k] > 1 for k in TEST))
    say(' n=%d floor %.6f (label at Jz %s; the four widest: %s); floor/tau at 1.1-1.4: %s (stored %s); smallest over the 50 '
        'couplings %.3f; holds %s'
        % (n, floor, kf, [x[1] for x in w[41:]], ' '.join('%.4f' % ft[k] for k in TEST),
           ' '.join('%.4f' % s['floor_over_tau'][k] for k in TEST), min(ft.values()), RES['I'][n]['holds']))

# ------------------------------------------------------------------------------------------------ L. like-for-like
say('\n== L. like-for-like statuses at E_real against the prediction (own outer and inner; rows of the stored map) ==')


def rj(p):
    return json.load(open(p)) if os.path.exists(p) else None


cnt = dict(confirmed=0, resolved=0, opened=0, contradicted=0, unchanged=0)
mis = 0
LIKE = {}
for (n, key, lab), r in sorted(PROW.items()):
    if n == 19:
        continue
    thr = rj(MAP + '/out/thr/thr_n%d_J%s.json' % (n, key))
    E_real = PT[(n, key)]['E_real']
    wout = 0.0
    for s, sign in (('+', 1), ('-', -1)):
        ch = rj(MAP + '/out/chains/chain_n%d_J%s_%s_%s.json' % (n, key, lab, s))
        ck = rj(MAP + '/out/chk/chk_n%d_J%s_%s_%s.json' % (n, key, lab, s))
        dG = max(2.0 * thr.get('dchi', 0.0), abs(ck['dG']) if ck else 0.0)
        wout += min(min((E_real - p['F'] + dG) / (p['lam'] * ch['S']) for p in ch['points']), 1.0)
    E, o, kind, srcs = pool(n, key, lab)
    h = hull(E, o, E_real - DELTA)
    win = (h[1] - h[0]) if h else None
    tau = r['tau']
    st = 'CERTIFIED' if wout <= tau else ('NOT_CERTIFIED' if (win is not None and win >= tau) else 'GRAY')
    pred = r['status']
    if pred == 'GRAY' and st == 'GRAY':
        rel = 'unchanged'
    elif pred == st:
        rel = 'confirmed'
    elif pred == 'GRAY':
        rel = 'resolved'
    elif st == 'GRAY':
        rel = 'opened'
    else:
        rel = 'contradicted'
    cnt[rel] += 1
    LIKE[(n, key, lab)] = (st, wout / tau, (win / tau) if win is not None else None, pred, rel)
    s = SROW[(n, key, lab)]['like']
    if s['status'].replace('_s', '') != st or abs(s['w_out_over_tau'] - wout / tau) > 1e-9:
        mis += 1
        FIND.append(dict(what='like-for-like row differs', row=[n, key, lab], mine=[st, wout / tau],
                         stored=[s['status'], s['w_out_over_tau']]))
say(' rows with data: %d; relation to the prediction: %s; rows that differ from the stored output: %d'
    % (sum(cnt.values()), cnt, mis))
loc = [(k, v) for k, v in LIKE.items() if k[2] in ('Z_bulk', 'Z_boundary', 'Czz_edge', 'Z_loop') and v[0] == 'CERTIFIED']
say(' local rows CERTIFIED_s at E_real: ' + '; '.join('n=%d Jz %s %s (w_out %.4f tau, predicted %s)' % (k[0], k[1], k[2], v[1], v[3])
                                                       for k, v in loc))
res = [(k, v) for k, v in LIKE.items() if v[4] == 'resolved']
say(' resolved rows: ' + '; '.join('%d/%s/%s->%s' % (k[0], k[1], k[2], v[0]) for k, v in res))
RES['L'] = dict(counts=cnt, mismatches=mis, local_certified=[[k[0], k[1], k[2], v[1]] for k, v in loc],
                resolved=[[k[0], k[1], k[2], v[0]] for k, v in res],
                ms=dict((('%d_%s' % (k[0], k[1])), [v[0], v[1], v[2]]) for k, v in LIKE.items() if k[2] == 'm_s'))
SP = SSUM['predicted_vs_obtained']
say(' stored counts of the sealed run: ' + json.dumps(SP['counts'])[:300] + ' confirmed_by_the_data: ' + str(SP['confirmed_by_the_data']))
RES['L']['stored_counts'] = SP['counts']

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
say('written', OUTJ)
