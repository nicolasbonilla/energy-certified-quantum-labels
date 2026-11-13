# -*- coding: utf-8 -*-
"""rd-audit: assemble real_data/RESULTS.md = head (results/RESULTS_head_rd-audit.md, with the tables of the audit filled
from checks/rd_audit_*.json, rounded outward) + the three partial result files, verbatim except for their Spanish
summaries (replaced by the consolidated one) and their heading levels. No number of a partial file is touched.
usage: python -B -I make_results_consolidated.py
"""
import glob
import hashlib
import json
import math
import os
import re
import sys

RD = 'C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work/phase3/full_runs/real_data'
A = json.load(open(RD + '/checks/rd_audit_map.json'))
P = json.load(open(RD + '/checks/rd_audit_predict_learn.json'))
I = json.load(open(RD + '/checks/rd_audit_integrity.json'))
assert not A['findings'] and not P['findings'], 'the recomputation has open disagreements'


def up(x, d):
    return math.ceil(x * 10 ** d - 1e-9) / 10 ** d


def dn(x, d):
    return math.floor(x * 10 ** d + 1e-9) / 10 ** d


def block(text, start, end, new):
    """replace from the line that starts with `start` up to (not including) the line that starts with `end`."""
    i = text.index('\n' + start) + 1
    j = text.index('\n' + end, i) + 1
    return text[:i] + new.rstrip('\n') + '\n\n' + text[j:]


head = open(RD + '/results/RESULTS_head_rd-audit.md', encoding='utf-8').read()

# file times
ref = os.path.getmtime(RD + '/DECLARATION.sha256')
allf = [f for d in ('out', 'results', 'e1') for f in glob.glob(RD + '/' + d + '/**/*', recursive=True) if os.path.isfile(f)]
old = [f for f in allf if os.path.getmtime(f) <= ref]
assert all('/out/n19/' in f.replace('\\', '/') for f in old), 'a file outside out/n19 predates the hash'
late_code = [f for d in ('code', 'tests', 'converted', 'source') for f in glob.glob(RD + '/' + d + '/**/*', recursive=True)
             if os.path.isfile(f) and os.path.getmtime(f) > ref]
assert not late_code, late_code[:3]
ft = ('- File times (when this file was assembled): of the %d files under `out/`, `results/` and `e1/`, %d are later than the\n'
      '  hash file; the other %d are the files of `out/n19/` (exact n = 19, no real datum, listed in Sec. 11 of the declaration\n'
      '  as computed before the hash). No file of `code/`, `tests/`, `converted/` or `source/` is later than the hash. Three\n'
      '  distinctive real values (two energies, one label) were searched in `tests/` and in the scratch folders of the review:\n'
      '  before the hash they occur only in the declared first look. These are file times and a text search, not an external\n'
      '  time stamp.' % (len(allf), len(allf) - len(old), len(old)))
i = head.index('\n- File times')
j = head.index('\n- `DEVIATIONS.md`', i)
head = head[:i + 1] + ft + head[j:]

# five couplings
s = 'Five couplings per size, sum_i <Z_i> - M_0 and q: '
parts = []
for n in ('57', '115'):
    dev = A['B_sector'][n]['dev']
    parts.append('n = %s: ' % n + '; '.join('%s: %.6f, %.6f' % (k, dev[k], -dev[k] / 2) for k in ('1.1', '1.6', '3.4', '4.0', '6.0')))
head = block(head, 'Five couplings per size', 'Exact interval of m_s at six', s + '. '.join(parts) + '.')

# six couplings
rows = ['| n | Jz | interval | width / tau | width / tau_rf | at M_0 alone | CERTIFIED (exact) | label, truth |', '|---|---|---|---|---|---|---|---|']
for key in ('57_3.4', '57_3.5', '57_3.6', '57_4.0', '57_5.0', '57_6.0', '115_4.0', '115_4.1', '115_4.5', '115_5.0', '115_5.5', '115_6.0'):
    r = A['C_six'][key]
    n, k = key.split('_')
    assert r['label_and_truth_inside'] and abs(r['w_tau'] - r['stored_w_tau']) < 1e-12
    rows.append('| %s | %s | [%.5f, %.5f] | %.4f | %.4f | %.4f | %s | %.6f, %.6f |'
                % (n, k, dn(r['lo'], 5), up(r['hi'], 5), up(r['w_tau'], 4), up(r['w_tau_rf'], 4), up(r['w_tau_M0'], 4),
                   'yes' if r['cert'] else 'no', r['label'], r['truth']))
head = block(head, '| n | Jz | interval |', 'The six certificates behind', '\n'.join(rows))

# not-certified rows
rows = ['| n | Jz | q | reference state | E* | pool | hull of m_s at E* | (1 - q) width | status |', '|---|---|---|---|---|---|---|---|---|']
for key in ('57_1.1', '57_3.1', '115_1.4', '115_3.0'):
    r = A['E_rows'][key]
    n, k = key.split('_')
    assert r['not_cert'] and abs(r['w_lower_tau'] - r['stored_w_lower_tau']) < 1e-9
    reev = r['kind'] == 're-evaluated'
    pool = ('%d states of %s, re-evaluated' % (r['pool'], ' and '.join(r['srcs']))) if reev else ('%d states stored at %s' % (r['pool'], k))
    rows.append('| %s | %s | %.6f | R3 of %s | %.6f | %s | [%.6f, %.6f] | %s tau | NOT CERTIFIED%s |'
                % (n, k, r['q'], r['ref'], r['Estar'], pool, r['hull'][0], r['hull'][1],
                   ('%.2f' % dn(r['w_lower_tau'], 2)) if r['w_lower_tau'] > 5 else ('%.3f' % dn(r['w_lower_tau'], 3)),
                   ' (rests on re-evaluated energies)' if reev else ''))
head = block(head, '| n | Jz | q | reference state', 'P5 ratios at five couplings', '\n'.join(rows))

# P5
ks = ('1.1', '1.5', '2.0', '2.5', '2.9')
t = []
for n in ('57', '115'):
    f = P['H'][n]['five']
    for k in ks:
        assert abs(f[k]['ratio'] - P['H'][n]['stored_five'][k]) < 2e-6
    t.append('n = %s: ' % n + ', '.join('%.4f' % f[k]['ratio'] for k in ks))
low = [k for k in ks if P['H']['115']['five'][k]['ratio'] < 0.75]
s = ('P5 ratios at five couplings (own n = 19 diagonalization), at Jz = 1.1, 1.5, 2.0, 2.5, 2.9: %s; %s (below 0.75 at %s).\n'
     'Equal to the stored ones to the digits shown. From my numbers over the 50 couplings: mean miss %.4f tau (n = 57) and %.4f tau\n'
     '(n = 115); deciding ratios outside the band: %d of %d and %d of %d; one decision: %s.'
     % (t[0], t[1], ', '.join(low), P['H']['57']['mean_miss'], P['H']['115']['mean_miss'], len(P['H']['57']['outside']),
        P['H']['57']['n_deciding'], len(P['H']['115']['outside']), P['H']['115']['n_deciding'], P['H']['P5_outcome']))
head = block(head, 'P5 ratios at five couplings', 'One split of (f3) end to end', s)

# split 0
f0 = P['J']['57_S_1_2']['split0']


def one(m):
    r = f0[m]
    assert abs(r['q'] - r['stored_q']) < 1e-12
    return '%s: q = %.9f, 2q / tau(x) = %s, miss / tau(x) = %s, truth inside at %d of %d' % (
        m, r['q'], ', '.join('%.4f' % x for x in r['widths_tau']), ', '.join('%.4f' % x for x in r['miss_tau']),
        sum(r['covered']), len(r['covered']))


s = ('One split of (f3) end to end (n = 57, S_1/2, split 0; training %s; calibration %s; queries %s). %s. %s. %s\n'
     '(control; trained on the 31 real training labels outside the calibration and query couplings). The 200 splits of every set\n'
     'equal the stored ones; q and the widths agree to 2e-12.'
     % (', '.join(f0['M1']['train']), ', '.join(f0['M1']['cal']), ', '.join(f0['M1']['query']), one('M1'), one('M2'), one('M0')))
assert f0['M0']['train'] == '31 couplings', f0['M0']['train']
head = block(head, 'One split of (f3) end to end', '**Three extra checks of the audit', s)

# check A
w = I['a_windows']
for n in ('57', '115'):
    assert w[n]['outside'] == ['1.1', '1.2', '1.3', '1.4'] and w[n]['ood'] == ['1.1', '1.2', '1.3', '1.4']
    assert w[n]['decisive_predicted'] - w[n]['decisive_implied_by_window'] == len(w[n]['decisive_not_implied'])
    assert all(x[2] == 'NOT_CERTIFIED' and x[0] < 1.5 for x in w[n]['decisive_not_implied'])
tr = {n: (dn(w[n]['ratio_train'][0], 3), up(w[n]['ratio_train'][1], 3)) for n in w}
oo = {n: (dn(min(w[n]['ratio_ood'].values()), 2), up(max(w[n]['ratio_ood'].values()), 2)) for n in w}
ndec = w['57']['decisive_predicted'] + w['115']['decisive_predicted']
s = ('- *Check A, why the map could not be contradicted.* At every stored training coupling the public energy error lies\n'
     '  inside the window that the figures-based map had assumed (%.3f-%.3f times the digitized value at n = 57, %.3f-%.3f at\n'
     '  n = 115, against a window of at least 0.8-1.2); at the four test couplings it is %.2f-%.2f times (n = 57) and\n'
     '  %.2f-%.2f times (n = 115) the floor of 0.012 per site that the map had assumed, so above its window. A window grows\n'
     '  with the energy: a row predicted CERTIFIED stays so while the energy is below the upper end of its window, and a row\n'
     '  predicted NOT CERTIFIED stays so while the energy is above the lower end. All %d decisive predicted statuses (%d at\n'
     '  training couplings, %d at test couplings) carry over for that reason alone; the 13 GRAY rows are the only ones whose\n'
     '  outcome was open.' % (tr['57'][0], tr['57'][1], tr['115'][0], tr['115'][1], oo['57'][0], oo['57'][1], oo['115'][0],
                              oo['115'][1], ndec, w['57']['decisive_implied_by_window'] + w['115']['decisive_implied_by_window'],
                              len(w['57']['decisive_not_implied']) + len(w['115']['decisive_not_implied'])))
i = head.index('\n- *Check A')
j = head.index('\n- *Check B', i)
head = head[:i + 1] + s + head[j:]
assert I['b_archive'] == dict(named=302, found=302, hash_equal=302) and not I['c_problems']
assert all(v[0] == v[1] and v[2] == 0 for v in I['c_tokens'].values())

# the three partial files
out = [head.rstrip('\n'), '']
for part, name, title in (('I', 'RESULTS_map.md', 'The map on the real energies, the accuracy factor, the filter, the gates'),
                          ('II', 'RESULTS_predict.md', 'The predictions of the emulation on the real labels'),
                          ('III', 'RESULTS_learn.md', 'The learning tests on the real labels')):
    src = open(RD + '/results/' + name, encoding='utf-8').read().split('\n')
    body = []
    skip = False
    for k, line in enumerate(src):
        if line.startswith('## Resumen'):
            skip = True
            continue
        if skip and line.startswith('## '):
            skip = False
        if skip:
            continue
        if k == 0 and line.startswith('# '):
            body.append('# Part %s. %s' % (part, title))
            body.append('')
            body.append('Verbatim from `results/%s` (SHA-256 `%s`), without its Spanish summary. Original title: "%s".'
                        % (name, hashlib.sha256(open(RD + '/results/' + name, 'rb').read()).hexdigest(), line[2:].strip()))
            continue
        m = re.match(r'^(#{2,4}) (.*)$', line)
        if m:
            line = '%s %s-%s' % (m.group(1), part, m.group(2))
        body.append(line)
    out.append('\n'.join(body).rstrip('\n'))
    out.append('')
text = '\n'.join(out) + '\n'
open(RD + '/RESULTS.md', 'w', encoding='utf-8', newline='\n').write(text)
print('written RESULTS.md: %d lines, %d bytes' % (text.count('\n'), len(text.encode('utf-8'))))

# precise values behind the numbers typed by hand in the head (to be read against it)
G = P['G']
print('q max', A['B_sector']['57']['q_max'], A['B_sector']['115']['q_max'], '| dev range', A['B_sector']['57']['min'], A['B_sector']['57']['max'],
      A['B_sector']['115']['min'], A['B_sector']['115']['max'])
print('spearman', [round(G['%s_%s' % (n, f)]['spearman'], 6) for n in ('57', '115') for f in ('sites', 'edges', 'second_neighbours', 'loops')])
print('filter', {n: (P['K'][n]['max_miss_kept'], P['K'][n]['kept'], P['K'][n]['dropped'], P['K'][n]['dropped_within_tau'],
                     P['K'][n]['n19_max_over_kept'], P['K'][n]['n19_at_test']) for n in ('57', '115')})
print('L1', {n: P['N'][n]['real']['miss_tau'] for n in ('57', '115')}, {n: P['N'][n]['dmrg']['miss_tau'] for n in ('57', '115')})
print('floor', {n: A['I'][n]['floor_over_tau_test'] for n in ('57', '115')})
for k, v in P['J'].items():
    if isinstance(v, dict):
        print('f3', k, [(m, v[m]['W_splits'], v[m]['C_pairs'], v[m]['pairs'], round(v[m]['width_min'], 5), round(v[m]['width_max'], 5),
                         round(v[m]['largest_miss'], 5)) for m in ('M1', 'M2', 'M0')], v['outcome_M1_M2'])
print('truth change over S_p', P['J']['truth_change_over_Sp_57'], P['J']['truth_change_over_Sp_115'])
print('D', {k: (v['jstar'], v['n_cert'], v['jstar_rf'], v['n_cert_rf'], round(v['w_tau_min'], 5), round(v['w_tau_max'], 5),
                round(v['widen_vs_M0_max'], 5)) for k, v in A['D'].items()})
print('F', {k: (v['headline_A'], v['headline_B'], [round(x, 2) for x in v['F_A']], [round(x, 2) for x in v['F_B']]) for k, v in A['F'].items()})
print('L local certified', A['L']['local_certified'], A['L']['counts'])
print('P5', {n: (P['H'][n]['mean_miss'], P['H'][n]['ratio_range_deciding'], P['H'][n]['n_deciding'], len(P['H'][n]['outside']),
                 P['H'][n]['median_ratio_deciding'], P['H'][n]['mean_raw']) for n in ('57', '115')})
