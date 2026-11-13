"""C3b (2026-11-08), read-only look: plan balance, ibm_kingston status and calibration, the sealed layout rule
qpu_route.choose_routed_layout (ladder x1, x2, x4) on its current calibration; diagnostic x8 and x20 only if the sealed
ladder fails (as on 2026-11-06, logs_laptop/diag_kingston.txt). Submits nothing. Never reads or prints credentials.
usage (from final_tests/):  C:/tmp/qgss4env/Scripts/python.exe code_c3b/diag_c3b.py <out.json>"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code_c3"))
import submit_c3 as sc  # noqa: E402  (sealed; imported, not changed)

ql, qr = sc.ql, sc.qr
OUTP = sys.argv[1]
svc = sc.service()
R = dict(time=sc.now(), account=sc.account(svc))
a = R["account"]
print("account", {k: a[k] for k in ("consumed_s", "limit_s", "remaining_s", "free_ok", "period", "limit_reached")}, flush=True)
b = svc.backend(sc.PRIMARY)
st = b.status()
R["status"] = dict(operational=bool(st.operational), pending_jobs=int(st.pending_jobs), status_msg=str(getattr(st, "status_msg", "")))
print("status", R["status"], flush=True)
props = b.properties()
t = b.target
fq = list(props.faulty_qubits())
fe = [tuple(x.qubits) for x in props.faulty_gates() if len(x.qubits) == 2]
Gd, twoq = ql.device_graph(t)
ro = {q: ql._err(t, "measure", (q,)) for q in range(t.num_qubits)}
rov = np.array([v for v in ro.values() if v is not None])
pairs = sorted(tuple(sorted(e)) for e in Gd.edge_list())
pe = {p: ql.edge_error(t, twoq, *p) for p in pairs}
pev = np.array([v for v in pe.values() if v is not None])
R["calibration"] = dict(last_update_date=str(props.last_update_date), num_qubits=t.num_qubits, twoq_gate=twoq, faulty_qubits=fq,
                        faulty_2q=[list(x) for x in fe],
                        readout=dict(median=float(np.median(rov)), n_gt_005=int(np.sum(rov > 0.05)), n_gt_01=int(np.sum(rov > 0.1)),
                                     n_gt_02=int(np.sum(rov > 0.2)),
                                     worst=sorted(((q, v) for q, v in ro.items() if v is not None), key=lambda x: -x[1])[:8]),
                        pairs=dict(n=len(pairs), median=float(np.median(pev)), n_gt_005=int(np.sum(pev > 0.05)), n_gt_01=int(np.sum(pev > 0.1)),
                                   n_gt_02=int(np.sum(pev > 0.2)),
                                   worst=sorted(((v, list(p)) for p, v in pe.items() if v is not None), key=lambda x: -x[0])[:10]))
c = R["calibration"]
print("last update", c["last_update_date"], "faulty q", fq, "faulty 2q", fe, flush=True)
print("readout median %.4f, >0.05: %d, >0.1: %d, >0.2: %d worst %s" % (c["readout"]["median"], c["readout"]["n_gt_005"], c["readout"]["n_gt_01"],
                                                                       c["readout"]["n_gt_02"], c["readout"]["worst"]), flush=True)
print("pairs %d median %.4f >0.05: %d, >0.1: %d, >0.2: %d worst %s" % (c["pairs"]["n"], c["pairs"]["median"], c["pairs"]["n_gt_005"],
                                                                      c["pairs"]["n_gt_01"], c["pairs"]["n_gt_02"], c["pairs"]["worst"][:7]), flush=True)
g = ql.graph57()
try:
    sel = qr.choose_routed_layout(t, g, 5, fq, fe)
    R["sealed_rule"] = dict(ok=True, relax=sel["relax"], score_2q_per_step=sel["score_2q_per_step"], moves_per_step=sel["moves_per_step"],
                            mean_readout_error=sel["mean_readout_error"], n_core_mappings=sel["n_core_mappings"], sel=sel)
    print("sealed rule OK: relax %s score %.4f moves/step %d mean readout %.4f (%d core mappings)" % (
        sel["relax"], sel["score_2q_per_step"], sel["moves_per_step"], sel["mean_readout_error"], sel["n_core_mappings"]), flush=True)
except RuntimeError as e:
    R["sealed_rule"] = dict(ok=False, reason=str(e))
    print("sealed rule (x1, x2, x4) fails:", e, flush=True)
    R["diagnostic_relax"] = {}
    for rl in (8, 20):
        try:
            s2 = qr._choose(t, g, 5, fq, fe, 20000, 3, ql.READOUT_MAX * rl, ql.CZ_MAX * rl)
            R["diagnostic_relax"][str(rl)] = dict(score_2q_per_step=s2["score_2q_per_step"], mean_readout_error=s2["mean_readout_error"],
                                                  moves_per_step=s2["moves_per_step"])
            print("diagnostic relax %d score %.4f readout %.4f moves %d" % (rl, s2["score_2q_per_step"], s2["mean_readout_error"],
                                                                         s2["moves_per_step"]), flush=True)
        except RuntimeError as e2:
            R["diagnostic_relax"][str(rl)] = dict(reason=str(e2))
            print("diagnostic relax %d fails: %s" % (rl, e2), flush=True)
LIMIT = 0.95
R["conditions"] = dict(a_sealed_rule_gives_kingston=bool(R["status"]["operational"] and R["sealed_rule"]["ok"]),
                       b_score_le_095=bool(R["sealed_rule"]["ok"] and R["sealed_rule"]["score_2q_per_step"] <= LIMIT),
                       c_remaining_ge_150=bool(a["remaining_s"] is not None and a["remaining_s"] >= sc.CAP and a["free_ok"]))
print("conditions", R["conditions"], flush=True)
sc.wjson(OUTP, R)
print("wrote", OUTP, ql.sha256_file(OUTP))
