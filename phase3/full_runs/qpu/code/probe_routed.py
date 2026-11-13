"""Feasibility of the routed proposal (read-only, NO submission): for each real backend, the routed layout under
qpu_route.choose_routed_layout with today's calibration, then local transpilation of the Jz = 1.2 Krylov circuits
(k = 1, 5, 10) and of the k = 0 check: CZ count, CZ depth, estimated circuit duration, and a QPU-time estimate per
1e6 shots. Prints JSON. No token or account file is read or printed."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qpu_lib as ql  # noqa: E402
import qpu_route as qr  # noqa: E402


def stats(isa, target):
    ops = isa.count_ops()
    d2 = isa.depth(lambda ins: ins.operation.num_qubits == 2 and ins.operation.name != "barrier")
    try:
        dur = float(isa.estimate_duration(target, unit="s"))
    except Exception as e:
        dur = "n/a: %s" % str(e)[:80]
    return dict(cz=int(ops.get("cz", 0)), cz_depth=int(d2), duration_s=dur, n_ops=int(sum(ops.values())))


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    names = sys.argv[1:]
    service = QiskitRuntimeService()
    g = ql.graph57()
    out = []
    for b in service.backends(simulator=False):
        if names and b.name not in names:
            continue
        row = dict(name=b.name)
        t0 = time.time()
        props = b.properties()
        fq = list(props.faulty_qubits())
        fe = [tuple(x.qubits) for x in props.faulty_gates() if len(x.qubits) == 2]
        row["calibration_last_update"] = str(props.last_update_date)
        try:
            sel = qr.choose_routed_layout(b.target, g, 5, fq, fe)
        except RuntimeError as e:
            row["error"] = str(e)
            out.append(row)
            continue
        row["select_secs"] = time.time() - t0
        row["sel"] = {k: v for k, v in sel.items() if k not in ("layout",)}
        row["layout"] = sel["layout"]
        Ll = qr.routed_layout_list(sel)
        circs = [qr.routed_krylov_circuit(g, 1.2, ql.DT57[1.2], k, sel) for k in (1, 5, 10)]
        isas = ql.transpile_isa(circs, b, Ll)
        row["krylov_J1.2"] = {str(k): stats(c, b.target) for k, c in zip((1, 5, 10), isas)}
        chk = ql.transpile_isa([ql.product_circuit(g, ql.neel_sites(g), "neel")], b, sel["layout"])[0]
        row["check_neel"] = stats(chk, b.target)
        rep = b.configuration().default_rep_delay
        durs = [s["duration_s"] for s in row["krylov_J1.2"].values() if isinstance(s["duration_s"], float)]
        if durs:
            # linear in k between k = 1 and 10 -> mean over k = 1..10
            d1, d10 = row["krylov_J1.2"]["1"]["duration_s"], row["krylov_J1.2"]["10"]["duration_s"]
            mean_dur = (d1 + d10) / 2.0
            row["est_qpu_s_per_1e6_shots_lower"] = 1e6 * (rep + mean_dur)
        out.append(row)
        print(json.dumps(row, default=str)[:400], file=sys.stderr, flush=True)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
