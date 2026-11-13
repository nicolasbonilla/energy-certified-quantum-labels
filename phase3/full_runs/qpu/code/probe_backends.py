"""Feasibility probe (read-only, no submission): for every real backend of the saved account, the timing
configuration (rep_delay, gate / readout durations) and whether heavy_hex_graph(5) embeds in its coupling graph,
with the best embedding under the layout rule of qpu_lib.choose_layout. Prints a short JSON summary only.
No token or account file is read or printed (QiskitRuntimeService() with the saved default account)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qpu_lib  # noqa: E402
from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: E402


def main():
    service = QiskitRuntimeService()
    out = []
    for b in service.backends(simulator=False):
        row = {"name": b.name}
        try:
            cfg = b.configuration()
            row["default_rep_delay_us"] = getattr(cfg, "default_rep_delay", None)
            row["rep_delay_range_us"] = getattr(cfg, "rep_delay_range", None)
            row["basis_gates"] = list(getattr(cfg, "basis_gates", []))
        except Exception as e:
            row["cfg_error"] = str(e)[:200]
        fq, fe = [], []
        try:
            props = b.properties()
            fq = list(props.faulty_qubits())
            fe = [tuple(gt.qubits) for gt in props.faulty_gates() if len(gt.qubits) == 2]
            row["faulty_qubits"] = fq
            row["faulty_2q_gates"] = fe
            row["last_update_date"] = str(props.last_update_date)
        except Exception as e:
            row["props_error"] = str(e)[:200]
        try:
            sel = qpu_lib.choose_layout(b.target, qpu_lib.graph57(), fq, fe)
            row["layout"] = {k: v for k, v in sel.items() if k not in ("layout", "edge_errors", "ro_errors")}
        except Exception as e:
            row["layout_error"] = f"{type(e).__name__}: {str(e)[:300]}"
        out.append(row)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
