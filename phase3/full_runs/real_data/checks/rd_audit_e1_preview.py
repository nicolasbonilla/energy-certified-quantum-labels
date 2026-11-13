# -*- coding: utf-8 -*-
"""rd-audit: the E1 column recomputed with the audit's OWN interval code and compared with the declared E1 column
(e1/map_e1/map_rows.json, built by e1/collect_e1.py with the sealed map code after E1 finished).

Reads e1/certs/*_cert.json (stored file format). A certificate is used only if its two verification records exist and
agree with it (stored verifier: *_ver.json; independent verifier: *_myver.json). Range of the E1 column (declaration
Sec. 12, line 3): the one spanned by the stored and the E1 m_s certificates of that size together.
usage: python -B -I rd_audit_e1_preview.py
"""
import contextlib
import glob
import hashlib
import io
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
with contextlib.redirect_stdout(io.StringIO()):
    import rd_audit_map as A          # the audit's own module (re-runs its checks; nothing sealed is imported)

E1 = A.RD + '/e1/certs'
status = json.load(open(A.RD + '/e1/STATUS.json'))
print('E1 status: finished %s (%s), updated %s, jobs %s' % (status['finished'], status.get('stop_reason'), status['updated_utc'],
                                                           status['job_counts']))
stored_iv = {(n, k, lab): A.interval(n, k, lab) for n in (57, 115) for k in A.KEYS for lab in ('m_s', 'Czz_bar')}

new, skipped = [], []
for f in sorted(glob.glob(E1 + '/*_cert.json')):
    b = open(f, 'rb').read()
    h = hashlib.sha256(b).hexdigest()
    c = json.loads(b)
    n = {'hh_d5.json': 57, 'hh_d7.json': 115}.get(c['graph'])
    t = c['task']
    den = 2 ** int(c['K'])
    csum = Fr(sum(int(x) for x in c['t']), den)
    mu = Fr(int(c['mu']), den)
    okc = Fr(c['E_claim']) == csum - mu * A.G[n]['M0']
    try:
        e = json.load(open(f.replace('_cert.json', '_ver.json')))
        m = json.load(open(f.replace('_cert.json', '_myver.json')))
        rec = dict(stored_ok=e.get('ok') is True, stored_sha=e.get('cert_sha256') == h,
                   stored_bound=Fr(str(e.get('E_LB_exact'))) == Fr(c['E_claim']),
                   indep_proved=m.get('all_cluster_inequalities_proved') is True, indep_identity=m.get('identity_holds') is True,
                   indep_claim=m.get('E_matches_cert_claim') is True, indep_sha=m.get('cert_sha256') == h)
    except Exception as ex:
        rec = dict(error=repr(ex)[:100])
    if not (okc and all(v is True for v in rec.values())):
        skipped.append((os.path.basename(f), okc, rec))
        continue
    assert t['kind'] == 'm_s'
    new.append(dict(n=n, kind='m_s', sigma=int(t['sigma']), lam=Fr(str(t['lam'])), J=Fr(str(t['Jz'])), c=csum, mu=mu,
                    name=os.path.basename(f)[:-10], sha=h, path=f))
print('E1 certificate files %d; used %d (claim identity, stored verifier record and independent verifier record all agree); '
      'skipped %d' % (len(new) + len(skipped), len(new), len(skipped)))
for s in skipped[:5]:
    print('   skipped', s)
by = {}
for c in new:
    by[(c['n'], '%.1f' % float(c['J']), c['sigma'])] = by.get((c['n'], '%.1f' % float(c['J']), c['sigma']), 0) + 1
print('   by (n, Jz, sign):', {('%d/%s/%+d' % k): v for k, v in sorted(by.items())})

A.CERT.extend(new)
for n in (57, 115):
    js = [c['J'] for c in A.CERT if c['n'] == n and c['kind'] == 'm_s']
    A.RANGE[n] = (min(js), max(js))
RES = dict(status=dict(finished=status['finished'], updated_utc=status['updated_utc'], job_counts=status['job_counts']),
           used=len(new), skipped=[s[0] for s in skipped], range={str(n): [str(A.RANGE[n][0]), str(A.RANGE[n][1])] for n in (57, 115)})

# the declared E1 column (sealed code, run by the E1 task)
SE = {}
p = A.RD + '/e1/map_e1/map_rows.json'
if os.path.exists(p):
    SE = {(r['n'], r['key'], r['label']): r for r in json.load(open(p))['rows'] if r.get('group') == 'dataset'}
print('declared E1 column present:', bool(SE))


def jstar(flags):
    js = None
    for k in reversed(A.TRAIN):
        if flags[k]:
            js = k
        else:
            break
    return js


FIND = []
for n in (57, 115):
    for lab in ('m_s', 'Czz_bar'):
        iv = {k: A.interval(n, k, lab) for k in A.KEYS}
        ncmp = neq = 0
        for k in A.KEYS:
            s = (SE.get((n, k, lab)) or {}).get('exact_e1')
            if not SE:
                break
            mine_exists = iv[k] is not None
            st_exists = bool(s and s.get('exists'))
            if mine_exists != st_exists:
                FIND.append(dict(what='E1 interval exists on one side only', row=[n, k, lab], mine=mine_exists, stored=st_exists))
                continue
            if not mine_exists:
                continue
            ncmp += 1
            same = (Fr(s['lo_exact']) == iv[k]['lo'] and Fr(s['hi_exact']) == iv[k]['hi'] and bool(s['certified']) == iv[k]['cert']
                    and bool(s['certified_rf']) == iv[k]['cert_rf'])
            neq += same
            if not same:
                FIND.append(dict(what='E1 interval differs', row=[n, k, lab], mine=[float(iv[k]['lo']), float(iv[k]['hi']), iv[k]['cert'],
                                 iv[k]['cert_rf'], iv[k]['in_range']], stored=[s['lo'], s['hi'], s['certified'], s['certified_rf'], s.get('in_range')]))
        f = {k: bool(iv[k] and iv[k]['cert']) for k in A.TRAIN}
        frf = {k: bool(iv[k] and iv[k]['cert_rf']) for k in A.TRAIN}
        f0 = {k: bool(stored_iv[(n, k, lab)] and stored_iv[(n, k, lab)]['cert']) for k in A.TRAIN}
        newrows = [k for k in A.TRAIN if iv[k] and iv[k]['in_range'] and not (stored_iv[(n, k, lab)] and stored_iv[(n, k, lab)]['in_range'])]
        changed = [k for k in A.TRAIN if stored_iv[(n, k, lab)] and stored_iv[(n, k, lab)]['in_range'] and iv[k]
                   and abs(iv[k]['w_tau'] - stored_iv[(n, k, lab)]['w_tau']) > 1e-12]
        inr = [k for k in A.TRAIN if iv[k] and iv[k]['in_range']]
        inside = all(iv[k]['lo'] <= Fr(A.PT[(n, k)]['ms_real' if lab == 'm_s' else 'czz_real']) <= iv[k]['hi']
                     and iv[k]['lo'] <= Fr(A.PT[(n, k)]['O_' + lab]) <= iv[k]['hi'] for k in inr)
        R = dict(jstar=jstar(f), n_cert=sum(f.values()), jstar_rf=jstar(frf), n_cert_rf=sum(frf.values()),
                 jstar_stored_only=jstar(f0), n_cert_stored_only=sum(f0.values()), rows_compared=ncmp, rows_identical=neq,
                 new_rows={k: dict(w_tau=iv[k]['w_tau'], w_tau_rf=iv[k]['w_tau_rf'], w_tau_M0=iv[k]['w_tau_M0'], cert=iv[k]['cert'],
                                   cert_rf=iv[k]['cert_rf'], lo=float(iv[k]['lo']), hi=float(iv[k]['hi'])) for k in newrows},
                 improved_rows={k: [stored_iv[(n, k, lab)]['w_tau'], iv[k]['w_tau']] for k in changed},
                 w_tau_range_certified=[min(iv[k]['w_tau'] for k in A.TRAIN if f[k]), max(iv[k]['w_tau'] for k in A.TRAIN if f[k])],
                 label_and_truth_inside_all=bool(inside))
        if lab == 'm_s':
            R['sets'] = dict(S=[k for k in A.TRAIN if f[k]],
                             S_3_4=[k for k in A.TRAIN if f[k] and iv[k]['w'] <= Fr(3, 4) * iv[k]['tau']],
                             S_1_2=[k for k in A.TRAIN if f[k] and iv[k]['w'] <= Fr(1, 2) * iv[k]['tau']])
        RES['%d_%s' % (n, lab)] = R
        print(' n=%d %-7s with E1: J*_exact %s (%d of 45; reference-free %s, %d); stored certificates only: %s (%d); against the '
              'declared E1 column: %d rows compared, %d identical as exact rationals; label and truth inside every interval: %s'
              % (n, lab, R['jstar'], R['n_cert'], R['jstar_rf'], R['n_cert_rf'], R['jstar_stored_only'], R['n_cert_stored_only'],
                 ncmp, neq, inside))
        print('     new rows of the extended range (width / tau; CERTIFIED): '
              + '; '.join('%s: %.4f %s' % (k, v['w_tau'], 'yes' if v['cert'] else 'no') for k, v in R['new_rows'].items()))
        if changed:
            print('     %d rows of the old range become narrower; largest gain at %s: %.4f -> %.4f tau'
                  % (len(changed), max(changed, key=lambda k: R['improved_rows'][k][0] - R['improved_rows'][k][1]),
                     *R['improved_rows'][max(changed, key=lambda k: R['improved_rows'][k][0] - R['improved_rows'][k][1])]))
        if lab == 'm_s':
            print('     sets with E1: |S| = %d (%s-%s), |S_3/4| = %d, |S_1/2| = %d'
                  % (len(R['sets']['S']), R['sets']['S'][0], R['sets']['S'][-1], len(R['sets']['S_3_4']), len(R['sets']['S_1_2'])))
RES['findings'] = FIND
print('disagreements with the declared E1 column beyond rounding: %d' % len(FIND))
for x in FIND[:10]:
    print('   ', json.dumps(x)[:300])
json.dump(RES, open(HERE + '/rd_audit_e1_preview.json', 'w'), indent=1)
print('written', HERE + '/rd_audit_e1_preview.json')
