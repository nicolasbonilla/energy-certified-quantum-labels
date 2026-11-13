"""Post-hoc checks asked for by the fifth reading (paper/reviews/R5_fresh.md). NOT part of the declaration. Reads stored JSON only; seconds.
usage: python -I post_checks.py <phase3/full_runs dir>   writes final_tests/analysis/post_checks.json"""
import json
import os
import sys

R = sys.argv[1]


def rj(*p):
    return json.load(open(os.path.join(R, *p), encoding='utf8'))


b = rj('final_tests', 'analysis', 'test_b.json')
a = rj('final_tests', 'analysis', 'test_a.json')['rows']
e = rj('bias_law', 'out', 'results.json')['n19_curve']
s = rj('map', 'laptop_analysis', 'summary_map.json')
L = rj('learning_ibm', 'out', 'results.json')['sizes']['57']['models']['poly3_invJ']
out = {}

# labels against the regression on the same local couplings
for J in ('1.6', '2.5'):
    m = b['Jz'][J]['mean']
    out['gain_over_reg_' + J] = {q: 100 * (1 - m[q] / m['reg']) for q in ('q_top', 'q_kry')}
    out['ratio_to_best_' + J] = {q: m[q] / m['emb19'] for q in ('q_top', 'q_kry')}

# how far the blind test could have surprised
tot = {'57': [], '115': []}
for r in a:
    rows = sorted(e[str(r['n'])]['rows'], key=lambda x: x['J'])
    lo = max((x for x in rows if x['J'] < r['J']), key=lambda x: x['J'])
    hi = min((x for x in rows if x['J'] > r['J']), key=lambda x: x['J'])
    w = (r['J'] - lo['J']) / (hi['J'] - lo['J'])
    tot[str(r['n'])].append(((1 - w) * abs(lo['corrected']) + w * abs(hi['corrected']), r['miss_curve19']))
out['interp_mean'] = {n: sum(x[0] for x in v) / len(v) for n, v in tot.items()}
out['interp_maxdiff'] = {n: max(abs(x[0] - x[1]) for x in v) for n, v in tot.items()}

# truth at n = 19 inside the certified range
out['n19_truth_certified_range'] = {str(x['J']): x['small_truth'] for x in e['57']['rows'] if x['J'] >= 3.5}

# margins of the map
row0 = s['rows'][0]
keyJ = 'Jz' if 'Jz' in row0 else ('J' if 'J' in row0 else None)
keyL = 'label' if 'label' in row0 else ('obs' if 'obs' in row0 else None)
keyS = 'status' if 'status' in row0 else None
print('row keys', list(row0.keys())[:16])
if keyJ and keyL and keyS:
    c = [r for r in s['rows'] if r[keyS] == 'CERTIFIED' and r[keyL] in ('m_s', 'Czz_bar') and r.get('f_out') is not None and r['n'] in (57, 115)]
    out['f_out_min_certified'] = min(r['f_out'] for r in c)
    out['f_out_min_J4'] = min(r['f_out'] for r in c if r[keyJ] >= 4.0)

# learning: training and test ranges of the cubic model
for k in ('indist_emulated', 'ood_emulated'):
    q = L[k]['summary']
    out['learn_' + k] = {x: q[x] for x in q if x in ('covZ_emu', 'covM_emu', 'miss_ms_over_tau_range', 'covZ_truth')}
p = os.path.join(R, 'final_tests', 'analysis', 'post_checks.json')
json.dump(out, open(p, 'w', encoding='utf8'), indent=1)
print(json.dumps(out)[:1500])
