"""Referee R2: is the 'shifted inside the window' label set (advL/advM) realizable as ONE dataset?

On the Huang benchmark H = sum_b J_b (XX+YY+ZZ)_b = 3 sum_b J_b C_b, so the 31 nn-bond labels of an instance fix the
energy of whatever state produced them. A single state at energy E0 + n*de must satisfy 3 sum_b J_b C_b = E0 + n*de.
The deposit's shifted labels take each bond from its OWN witness state (DECLARATION.md Sec. 3 (iii)). We compute the
energy those 31 labels imply and compare it with the energy they are reported at. Read-only; uses the deposit's
label loader. Usage: python spot... <J_next_paper root>"""
import sys, os, glob, json
import numpy as np
root = sys.argv[1] if len(sys.argv) > 1 else '.'
code = os.path.join(root, 'phase3/full_runs/learning/code')
sys.path.insert(0, code)
import labels_l as LL, lattice as LT  # deposit code, read-only

out = os.path.join(root, 'phase3/full_runs/learning/out_20261031T152732Z/out')
recs = LL.load_all(out, ['D'])['D']
L = recs[0]['L']; B = LT.bonds(L)
res = {de: dict(gen=[], less=[], more=[], exact=[]) for de in LL.DE}
for r in recs:
    J = np.array(r['J']); E0 = r['E0']; n = r['n']
    for de in LL.DE:
        eps = n * de
        for kind in ('exact', 'gen', 'less', 'more'):
            C = []
            for (a, b) in B:
                lab = 'P_%d_%d' % (a, b)
                x = r['labels'][lab]
                C.append(x['exact'] if kind == 'exact' else x['gen'][de] if kind == 'gen' else x['adv'][kind][de])
            Eimp = 3.0 * float(np.dot(J, C))
            # excess energy implied by the labels, in units of the reported excess eps
            res[de][kind].append((Eimp - E0) / eps)
for de in LL.DE:
    print(f"de = {de:g}  (reported excess eps = n*de = {20*de:g})")
    for kind in ('exact', 'gen', 'less', 'more'):
        v = np.array(res[de][kind])
        print(f"  {kind:5s}: implied (E - E0)/eps  min {v.min():9.3f}  median {np.median(v):9.3f}  max {v.max():9.3f}")
# the Cnn average label: how much does the per-label adversary move it relative to the generator?
