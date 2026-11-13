"""Exploratory bias-versus-energy analysis (2026-11-06). NOT a blind test: found after the data were known.
Reads stored outputs only (method, qpu, the n = 19 curves from n19b.py, the small-model outputs); no physics is recomputed.
Writes out/results.json and the PGFPlots data under paper/figures/data_biaslaw/.
Miss = |value - truth| / tau, tau = 0.06 |m_s(GS)| at the target size.
"""
import glob
import json
import os
import re
import sys

import numpy as np

ROOT = sys.argv[1]
D = ROOT + '/phase3/full_runs/bias_law'
M = ROOT + '/phase3/full_runs/method/out_20261030T003230Z/out'
C = {float(k): v for k, v in json.load(open(D + '/inputs/n19_curves.json')).items()}
Q = json.load(open(ROOT + '/phase3/full_runs/qpu/analysis/analysis.json'))
NE = {19: 20, 57: 64, 115: 132}
OUT = ROOT + '/paper/figures/data_biaslaw'
os.makedirs(OUT, exist_ok=True)


def grid(n):
    return sorted(float(re.search(r'_J([0-9.]+)\.json', f).group(1)) for f in glob.glob(f'{M}/emu/emu_n{n}_J*.json'))


def emu(n, J):
    return json.load(open(f'{M}/emu/emu_n{n}_J{J}.json'))


def family(n, J):
    """All stored states at (n, J): pipeline variants, shot scan, perfect-sample subsets."""
    e = emu(n, J)
    P = [('pipe_' + k, v['dE_site'], v['err']['dm_s'], v['err']['dZ']) for k, v in e['var'].items() if not v.get('alias_of')]
    P += [('kscan', (s['E'] - e['E0']) / n, s['err']['dm_s'], s['err']['dZ']) for s in e.get('kscan', [])]
    f = f'{M}/gsscan/gsscan_n{n}_J{J}.json'
    if os.path.exists(f):
        g = json.load(open(f))
        P += [('gs_random', s['dE_site'], s['err']['dm_s'], s['err']['dZ']) for s in g['nested']]
        P += [('gs_top', s['dE_site'], s['err']['dm_s'], s['err']['dZ']) for s in g['topD']]
    return e, P


def curve19(J, de):
    c = np.array(C[J]['curve'])
    return float(np.interp(np.sqrt(max(de, 0.0)), np.sqrt(np.maximum(c[:, 0], 0.0)), c[:, 1]))


def fit(P, col=2):
    s = np.sqrt([p[1] for p in P])
    y = np.array([p[col] for p in P])
    A = np.c_[s, s**2, s**3]
    c = np.linalg.lstsq(A, y, rcond=None)[0]
    return lambda de: float(np.array([de**.5, de, de**1.5]) @ c)


def stat(a):
    a = np.asarray(a, float)
    return dict(mean=float(a.mean()), max=float(a.max()), n=int(a.size))


R = {'note': 'exploratory, not blind; miss in units of tau = 0.06 |m_s(GS)|'}

# A. curve from exact n = 19 applied to the primary labels
R['n19_curve'] = {}
for n in (57, 115):
    rows = []
    for J in grid(n):
        e = emu(n, J)
        v = e['var']['primary']
        t = .06 * e['ref_m_s']
        d = v['err']['dm_s']
        rows.append(dict(J=J, de=v['dE_site'], raw=abs(d) / t, small_truth=abs(C[J]['ms0'] - e['ref_m_s']) / t,
                         corrected=abs(d - curve19(J, v['dE_site'])) / t))
    R['n19_curve'][str(n)] = dict(rows=rows, raw=stat([r['raw'] for r in rows]), small_truth=stat([r['small_truth'] for r in rows]),
                                  corrected=stat([r['corrected'] for r in rows]))

# B. device readings
dev = {'n19': [], 'emu57': [], 'raw': [], 'rows': []}
for J in ('1.2', '1.6', '4.0'):
    e, P = family(57, float(J))
    f = fit(P)
    t = .06 * e['ref_m_s']
    for m in ('rec', 'ps'):
        v = Q['points'][J]['device'][m]
        de = v['eps'] / 57
        d = v['dm_s']
        dev['raw'].append(abs(d) / t)
        dev['n19'].append(abs(d - curve19(float(J), de)) / t)
        dev['emu57'].append(abs(d - f(de)) / t)
        dev['rows'].append(dict(J=float(J), reading=m, de=de, dm=d))
R['device'] = dict(raw=stat(dev['raw']), n19=stat(dev['n19']), emu57=stat(dev['emu57']), rows=dev['rows'])

# C. all n = 57 families -> all n = 115 families
A = []
names = set()
for J in (1.2, 1.6, 2.5):
    e57, P57 = family(57, J)
    f = fit(P57)
    e, P = family(115, J)
    t = .06 * e['ref_m_s']
    for name, de, dm, _ in P:
        A.append((abs(dm) / t, abs(dm - f(de)) / t))
        names.add(name)
A = np.array(A)
R['families_57_to_115'] = dict(raw=stat(A[:, 0]), corrected=stat(A[:, 1]), n_families=len(names))

# D. classical extrapolation against the correction with the n = 57 curve, n = 115
rows = []
for J in grid(115):
    e57 = emu(57, J)
    e = emu(115, J)
    m19, m57, m115 = C[J]['ms0'], e57['ref_m_s'], e['ref_m_s']
    t = .06 * m115
    b = (m19 - m57) / (1 / 19 - 1 / 57)
    ex = m57 - b / 57 + b / 115
    pts = sorted((v['dE_site'], v['err']['dm_s']) for k, v in e57['var'].items() if k in ('ideal', 'primary', 'dev_rec', 'dev_ps'))
    s = np.sqrt(np.r_[0, [p[0] for p in pts]])
    y = np.r_[0, [p[1] for p in pts]]
    v = e['var']['primary']
    x = np.sqrt(v['dE_site'])
    d = float(np.interp(x, s, y)) if x <= s[-1] else float(y[-1] + (y[-1] - y[-2]) / (s[-1] - s[-2]) * (x - s[-1]))
    rows.append(dict(J=J, raw=abs(v['err']['dm_s']) / t, extrap=abs(ex - m115) / t, corr57=abs(v['err']['dm_s'] - d) / t))
R['classical_tie_115'] = dict(rows=rows, raw=stat([r['raw'] for r in rows]), extrap=stat([r['extrap'] for r in rows]),
                              corr57=stat([r['corr57'] for r in rows]))

# E. energy reference without a calculation at n = 115: E0 = a n + b |edges| fitted on n = 19, 57
rows = []
for J in grid(115):
    e57 = emu(57, J)
    e = emu(115, J)
    v = e['var']['primary']
    t = .06 * e['ref_m_s']
    ab = np.linalg.solve(np.array([[19, NE[19]], [57, NE[57]]], float), [C[J]['E0'], e57['E0']])
    de = (v['E'] - ab @ [115, NE[115]]) / 115
    rows.append(abs(v['err']['dm_s'] - curve19(J, de)) / t)
R['no_reference_115'] = stat(rows)

# F. learner: cubic in 1/J on the training couplings, test J = 1.1-1.4
R['learner'] = {}
for n in (57, 115):
    rs = []
    for J in grid(n):
        e = emu(n, J)
        v = e['var']['primary']
        rs.append(dict(J=J, m=v['labels']['m_s'], m0=e['ref_m_s'], de=v['dE_site']))
    tr = [r for r in rs if r['J'] >= 1.6]
    te = [r for r in rs if r['J'] < 1.5]

    def X(q):
        return np.array([[1, 1 / r['J'], 1 / r['J']**2, 1 / r['J']**3] for r in q])

    targets = dict(raw=[r['m'] for r in tr], corrected=[r['m'] - curve19(r['J'], r['de']) for r in tr], exact=[r['m0'] for r in tr])
    res = {}
    for k, y in targets.items():
        c = np.linalg.lstsq(X(tr), np.array(y), rcond=None)[0]
        miss = [abs(float(X([r])[0] @ c) - r['m0']) / (.06 * r['m0']) for r in te]
        res[k] = dict(min=min(miss), max=max(miss))
    R['learner'][str(n)] = res

# G. published site error against the curve of dZ at the dataset's energy (ratio and dZ as in method/RESULTS.md)
pub = {(57, 1.6): (1.348, 10.6), (57, 2.5): (.235, 2.2), (57, 4.0): (.0523, .5), (115, 1.6): (2.716, 10.0), (115, 2.5): (.464, 2.0)}
rows = []
for (n, J), (r, z) in pub.items():
    e = emu(n, J)
    _, P = family(57, J)
    de = r * e['gap'] / n
    p = fit(P, col=3)(de)
    rows.append(dict(n=n, J=J, de=de, dZ_pred=p, dZ_pub=z, over_pct=100 * (p / z - 1)))
R['published'] = dict(rows=rows, over_min=min(r['over_pct'] for r in rows), over_max=max(r['over_pct'] for r in rows))

# H. other models: parse the small-model output
tag = None
rows = []
for L in open(D + '/inputs/generality.txt', encoding='utf8').read().splitlines():
    h = re.match(r'(.+?): sizes', L)
    if h:
        tag = h.group(1)
    m = re.search(r'from\s+(\d+) to (\d+): rows\s+(\d+)\s+raw mean\s+([\d.]+).*corrected mean\s+([\d.]+).*baseline\s+([\d.]+)', L)
    if m:
        rows.append(dict(model=tag, src=int(m.group(1)), raw=float(m.group(4)), corrected=float(m.group(5)), small_truth=float(m.group(6))))
strong = [r for r in rows if 'square XXZ' in r['model'] and ('Jz=2.0' in r['model'] or 'Jz=4.0' in r['model'])]
hard = [r for r in rows if r not in strong]
R['other_models'] = dict(rows=rows, n_strong=len(strong), wins_strong=sum(r['corrected'] < r['small_truth'] for r in strong),
                         n_hard=len(hard), wins_hard=sum(r['corrected'] < r['small_truth'] for r in hard),
                         raw_over_corrected_min=min(r['raw'] / r['corrected'] for r in rows),
                         raw_over_corrected_max=max(r['raw'] / r['corrected'] for r in rows))
t = open(D + '/inputs/instance_test.txt', encoding='utf8').read()
m = re.search(r'raw ([\d.]+) corrected ([\d.]+) classical ([\d.]+) corrected\+local ([\d.]+)', t)
R['instance_test'] = dict(raw=float(m.group(1)), corrected=float(m.group(2)), classical=float(m.group(3)), both=float(m.group(4)))

# I. internal checks on a biased family: every sample is a variational state at every other coupling (H = A + J B)
ic = {}
for n in (57, 115):
    Js = grid(n)
    E, b, b0, e0 = [], [], [], []
    for J in Js:
        e = emu(n, J)
        ref = json.load(open(f'{M}/ref/ref_n{n}_J{J}.json'))
        v = e['var']['primary']
        E.append(v['E'])
        b.append(sum(v['labels']['Czz'][:NE[n]]) / 4)
        b0.append(sum(ref['labels']['Czz'][:NE[n]]) / 4)
        e0.append(ref['E0'])
    J = np.array(Js)
    E, b, b0, e0 = map(np.array, (E, b, b0, e0))
    a = E - J * b
    frac = [(E[i] - (a + x * b).min()) / (E[i] - e0[i]) for i, x in enumerate(Js)]
    slope = np.gradient(E, J)
    sel = J <= 2.5
    ic[str(n)] = dict(hull_fraction_max=float(max(frac)),
                      slope_error_over_label_error_min=float((np.abs(slope - b0) / np.abs(b - b0))[sel].min()),
                      slope_error_over_label_error_max=float((np.abs(slope - b0) / np.abs(b - b0))[sel].max()))
R['internal_checks'] = ic
print('internal_checks', ic)

# J. nulls and limits added after the fourth reading (paper/reviews/R4_fresh.md)
# parameter-free chord from the n = 19 ground state: (1 - m0) sqrt(de / de_Neel), de_Neel = (E_Neel - E0)/19, E_Neel = -20 J/4
def chord(J, de):
    m0 = C[J]['ms0']
    dn = (-NE[19] * J / 4 - C[J]['E0']) / 19
    return (1 - m0) * np.sqrt(max(de, 0.0) / dn)


nulls = {}
for n in (57, 115):
    a = [abs(emu(n, J)['var']['primary']['err']['dm_s'] - chord(J, emu(n, J)['var']['primary']['dE_site'])) / (.06 * emu(n, J)['ref_m_s']) for J in grid(n)]
    nulls[f'chord_{n}'] = stat(a)
a = []
for r in R['device']['rows']:
    t = .06 * emu(57, r['J'])['ref_m_s']
    a.append(abs(r['dm'] - chord(r['J'], r['de'])) / t)
nulls['chord_device'] = stat(a)
# classical two-point forms for the truth at n = 115 from n = 19, 57
forms = {'a_b_over_n': lambda n: 1 / n, 'a_b_over_sqrt_n': lambda n: n**-.5, 'a_b_edges_over_n': lambda n: NE[n] / n}
for name, g in forms.items():
    a = []
    for J in grid(115):
        m19, m57, m115 = C[J]['ms0'], emu(57, J)['ref_m_s'], emu(115, J)['ref_m_s']
        b = (m19 - m57) / (g(19) - g(57))
        a.append(abs(m57 + b * (g(115) - g(57)) - m115) / (.06 * m115))
    nulls[name] = stat(a)
nulls['truth57_alone'] = stat([abs(emu(57, J)['ref_m_s'] - emu(115, J)['ref_m_s']) / (.06 * emu(115, J)['ref_m_s']) for J in grid(115)])
# spread of all stored states around the n = 19 curve, plotted couplings, and how close the labels are to the ceiling 1 - m0
rat = []
for J in (1.2, 1.6, 2.5, 4.0):
    for n in (57, 115):
        _, P = family(n, J)
        rat += [dm / curve19(J, de) for _, de, dm, _ in P if curve19(J, de) > 0]
nulls['ratio_to_curve_min'] = float(min(rat))
nulls['ratio_to_curve_max'] = float(max(rat))
ceil = [emu(115, J)['var']['primary']['err']['dm_s'] / (1 - emu(115, J)['ref_m_s']) for J in grid(115) if J <= 1.6]
nulls['ceiling_fraction_115_min'] = float(min(ceil))
nulls['ceiling_fraction_115_max'] = float(max(ceil))
# test couplings at n = 115 with the n = 19 curve
te = [r for r in R['n19_curve']['115']['rows'] if r['J'] < 1.5]
nulls['n19_curve_115_test_min'] = float(min(r['corrected'] for r in te))
nulls['n19_curve_115_test_max'] = float(max(r['corrected'] for r in te))
# local log-log slope of the n = 19 curves
sl = {}
for J in (1.2, 2.5, 4.0):
    c = np.array([p for p in C[J]['curve'] if p[0] > 1e-5 and p[1] > 0])
    x, y = np.log(c[:, 0]), np.log(c[:, 1])
    for lo, hi, key in ((1e-4, 1e-3, 'low'), (1e-2, 1e-1, 'high')):
        m_ = (c[:, 0] >= lo) & (c[:, 0] <= hi)
        if m_.sum() >= 3:
            sl[f'{J}_{key}'] = float(np.polyfit(x[m_], y[m_], 1)[0])
nulls['log_slope'] = sl
nulls['spread_pct_low'] = 100 * (1 - nulls['ratio_to_curve_min'])
nulls['spread_pct_high'] = 100 * (nulls['ratio_to_curve_max'] - 1)
nulls['ceiling_pct_min'] = 100 * nulls['ceiling_fraction_115_min']
nulls['ceiling_pct_max'] = 100 * nulls['ceiling_fraction_115_max']
# E0(57) scaled from n = 19 alone, then the reading at n = 57
for key, ratio in (('e0_57_per_bond', NE[57] / NE[19]), ('e0_57_per_site', 57 / 19)):
    a = []
    for J in grid(57):
        e = emu(57, J)
        v = e['var']['primary']
        de = (v['E'] - C[J]['E0'] * ratio) / 57
        a.append(abs(v['err']['dm_s'] - curve19(J, de)) / (.06 * e['ref_m_s']))
    nulls[key] = stat(a)
# truth at n = 19 used as the answer at the test couplings
for n in ('57', '115'):
    te = [r['small_truth'] for r in R['n19_curve'][n]['rows'] if r['J'] < 1.5]
    nulls[f'small_truth_test_{n}_min'] = float(min(te))
    nulls[f'small_truth_test_{n}_max'] = float(max(te))
# instance test, row counts
rows_i = [L.split() for L in open(D + '/inputs/instance_test.txt', encoding='utf8') if re.match(r'\s+\d\s+\d\.\d{4}', L)]
R['instance_test']['rows'] = len(rows_i)
R['instance_test']['corrected_beats_classical'] = sum(float(r[3]) < float(r[4]) for r in rows_i)
R['instance_test']['both_beats_classical'] = sum(float(r[5]) < float(r[4]) for r in rows_i)
R['nulls'] = nulls
print('nulls', json.dumps({k: v for k, v in nulls.items() if k.startswith(('e0_', 'small_', 'spread', 'ceiling_pct'))})[:900], R['instance_test'])

json.dump(R, open(D + '/out/results.json', 'w'), indent=1)

# PGFPlots data
for J in (1.2, 1.6, 2.5, 4.0):
    with open(f'{OUT}/curve19_J{J}.dat', 'w') as f:
        f.write('de dm\n')
        for de, dm in C[J]['curve']:
            if de > 1e-5:
                f.write(f'{de:.6e} {dm:.6e}\n')
    for n in (57, 115):
        _, P = family(n, J)
        with open(f'{OUT}/states_n{n}_J{J}.dat', 'w') as f:
            f.write('de dm\n')
            for _, de, dm, _ in sorted(P, key=lambda p: p[1]):
                if de > 1e-5:
                    f.write(f'{de:.6e} {dm:.6e}\n')
with open(f'{OUT}/device.dat', 'w') as f:
    f.write('de dm\n')
    for r in dev['rows']:
        if r['reading'] == 'rec':
            f.write(f"{r['de']:.6e} {r['dm']:.6e}\n")
with open(f'{OUT}/tie115.dat', 'w') as f:
    f.write('J raw extrap sqrtn corr\n')
    for r in R['classical_tie_115']['rows']:
        J = r['J']
        m19, m57, m115 = C[J]['ms0'], emu(57, J)['ref_m_s'], emu(115, J)['ref_m_s']
        b = (m19 - m57) / (19**-.5 - 57**-.5)
        sq = abs(m57 + b * (115**-.5 - 57**-.5) - m115) / (.06 * m115)
        f.write(f"{J} {r['raw']:.5f} {r['extrap']:.5f} {max(sq, 1e-4):.5f} {max(r['corr57'], 1e-3):.5f}\n")
for J in (1.2, 1.6, 2.5, 4.0):
    with open(f'{OUT}/chord_J{J}.dat', 'w') as f:
        f.write('de dm\n')
        dn = (-NE[19] * J / 4 - C[J]['E0']) / 19
        for de in np.logspace(np.log10(4e-4), np.log10(dn), 30):
            f.write(f'{de:.6e} {chord(J, de):.6e}\n')


def brief(x):
    return {a: b for a, b in x.items() if a != 'rows'}


print('n19', {n: brief(x) for n, x in R['n19_curve'].items()})
for k in ('device', 'families_57_to_115', 'classical_tie_115', 'published', 'other_models'):
    print(k, brief(R[k]))
print('no_reference_115', R['no_reference_115'])
print('learner', R['learner'])
print('instance_test', R['instance_test'])
for r in R['published']['rows']:
    print(r)
