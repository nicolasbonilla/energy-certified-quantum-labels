# rd-audit: which certificates decide J*_exact (m_s; both values of M; both members of a pair), and were they re-proved?
import json, sys, hashlib, glob, os
from fractions import Fraction as Fr
sys.argv = [sys.argv[0]]
import importlib.util
ROOT = 'C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work'
RUNS = ROOT + '/phase3/full_runs'; RD = RUNS + '/real_data'
A = json.load(open(RD + '/checks/rd_audit_map.json'))
V = json.load(open(ROOT + '/paper/reviews/R10_2026-11-12/scratch/math-rigorous-bounds/verify_all.json'))
recs = V if isinstance(V, list) else V.get('certs', V.get('results', list(V.values())))
print('verify_all.json: type', type(V).__name__, 'entries', len(recs))
r0 = recs[0] if isinstance(recs, list) else None
print('keys of one record:', list(r0.keys())[:25] if isinstance(r0, dict) else str(r0)[:200])
names = set()
for row in ('57_3.4', '57_3.5', '115_4.0'):
    for side in A['C_six'][row]['names']:
        names.update(side)
print('deciding certificates (decisive M):', sorted(names))
files = {}
for d in ('rigor/out_20261031T073328Z', 'rigor/out_20261031T100015Z', 'final_tests'):
    for f in glob.glob(RUNS + '/' + d + '/**/*_cert.json', recursive=True):
        files.setdefault(os.path.basename(f)[:-10], f)
out = []
for nm in sorted(names):
    f = files[nm]; h = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    hit = [r for r in recs if isinstance(r, dict) and (r.get('cert_sha256') == h or r.get('sha256') == h or h in json.dumps(r)[:2000])]
    c = json.load(open(f))
    out.append(dict(name=nm, path=f, sha256=h, graph=c['graph'], reproved_by_math_rigorous_bounds=len(hit) > 0,
                    ok=[(r.get('ok'), r.get('all_proved'), r.get('identity_ok')) for r in hit][:1]))
    print(nm, h[:12], c['graph'], 'in the 196 re-proved:', len(hit) > 0, out[-1]['ok'])
json.dump(out, open(RD + '/checks/rd_audit_g5_list.json', 'w'), indent=1)
