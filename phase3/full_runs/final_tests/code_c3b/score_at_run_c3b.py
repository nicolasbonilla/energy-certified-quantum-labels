"""C3b, read-only, seconds: the layout score S (qpu_route._choose formula) of the prepared layout, on the calibration snapshot of
preparation and on ibm_kingston's properties at the execution time. usage: python code_c3b/score_at_run_c3b.py <out.json>"""
import datetime
import json
import os
import sys

sel = json.load(open("jobs/C_20261108/prep.json"))["sel"]
snap = json.load(open("jobs/C_20261108/calibration_snapshot.json"))
g = json.load(open("code_c3/graphs/hh_d5.json"))
L = sel["layout"]
B = set(int(s) for s in sel["paths"])


def score(eps):
    S = 0.0
    for (i, j) in g["edges"]:
        if i not in B and j not in B:
            S += 3 * eps(L[i], L[j])
    for s, d in sel["paths"].items():
        for p, path in d.items():
            S += 3 * eps(path[-1], L[int(p)]) + 4 * sum(eps(path[t], path[t + 1]) for t in range(len(path) - 1))
    return S


tq = snap["twoq_error"]
S_prep = score(lambda a, b: tq["%d-%d" % tuple(sorted((a, b)))])
print("score on preparation snapshot %.4f (prep.json %.4f), snapshot last update %s" % (S_prep, sel["score_2q_per_step"], snap["last_update_date"]))
sys.path.insert(0, "code_c3")
from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: E402
b = QiskitRuntimeService().backend("ibm_kingston")
gate = sel["twoq_gate"][0]
out = dict(score_prep_snapshot=S_prep, snapshot_last_update=snap["last_update_date"], at={})
for t in ("2026-11-10T01:03:00", "2026-11-08T15:48:00"):
    pr = b.properties(datetime=datetime.datetime.fromisoformat(t).replace(tzinfo=datetime.timezone.utc))

    def eps(a, c):
        vals = []
        for q in ((a, c), (c, a)):
            try:
                vals.append(pr.gate_error(gate, list(q)))
            except Exception:
                pass
        return min(vals)
    S = score(eps)
    ro = [pr.readout_error(q) for q in L]
    out["at"][t] = dict(last_update=str(pr.last_update_date), score=S, mean_readout_homes=sum(ro) / len(ro), max_readout_homes=max(ro))
    print(t, out["at"][t])
json.dump(out, open(sys.argv[1], "w"), indent=1)
