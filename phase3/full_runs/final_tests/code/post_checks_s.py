"""Post-hoc checks for the should-fix items of the fifth reading (paper/reviews/R5_fresh.md S1, S13). NOT part of the
declaration. Reads stored JSON only; seconds.
usage: python -I post_checks_s.py <phase3/full_runs dir>   writes final_tests/analysis/post_checks_s.json"""
import json
import os
import sys

R = sys.argv[1]
B = os.path.join(R, 'final_tests', 'out_20261106T120830Z', 'out', 'b')


def rj(*p):
    return json.load(open(os.path.join(*p), encoding='utf8'))


b = rj(R, 'final_tests', 'analysis', 'test_b.json')
dsc = rj(R, 'learning_ibm', 'out', 'descriptive.json')['energy_ratio_57']
out = {}
# S13: the headline counts of test B
out['test_b_instances_total'] = sum(b['Jz'][J]['q_top']['n'] for J in ('1.6', '2.5'))
out['test_b_wins_total'] = sum(b['Jz'][J]['q_top']['wins'] for J in ('1.6', '2.5'))
# S1: energy error per site of the generated labels against the dataset's digitized one on the uniform model
for J in ('1.6', '2.5'):
    de = [m['de'] for m in b['Jz'][J]['meta']]
    dig = dsc[J]['dig_per_site']
    out['label_de_' + J] = dict(min=min(de), max=max(de), dataset_digitized_uniform=dig,
                                ratio_min=min(de) / dig, ratio_max=max(de) / dig)
# S1: single-core wall-clock seconds per test instance, as recorded by the tasks
cost = {k: [] for k in ('clusters', 'emulation', 'dmrg32', 'dmrg64', 'dmrg200', 'dmrg320')}
for J in ('1.6', '2.5'):
    for i in range(6):
        cost['clusters'].append(rj(B, 'patch_J%s_%d.json' % (J, i))['secs'])
        cost['emulation'].append(rj(B, 'emu_J%s_%d.json' % (J, i))['secs'])
        f = rj(B, 'ref_J%s_%d.json' % (J, i))
        cost['dmrg32'].append(f['low']['32']['time_s'])
        cost['dmrg64'].append(f['low']['64']['time_s'])
        cost['dmrg200'].append(f['dmrg200']['time_s'])
        cost['dmrg320'].append(f['dmrg320']['time_s'])
out['seconds_per_instance'] = {k: dict(min=min(v), max=max(v), n=len(v)) for k, v in cost.items()}
out['minutes_per_instance'] = {k: dict(min=min(v) / 60, max=max(v) / 60) for k, v in cost.items()}
p = os.path.join(R, 'final_tests', 'analysis', 'post_checks_s.json')
json.dump(out, open(p, 'w', encoding='utf8'), indent=1)
print(json.dumps(out, indent=1))
