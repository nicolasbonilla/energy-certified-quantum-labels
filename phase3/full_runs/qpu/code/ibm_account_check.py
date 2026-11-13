"""Read-only check of the author's saved IBM Quantum account (no submission).

Prints ONLY: channel, plan / pricing type and instance display name, the usage
window (consumed / limit / remaining seconds, period), and the list of real
backends with qubit count, processor family and queue length.

Never prints, logs or stores the token, the account file or the instance CRN
(the CRN is reduced to a short SHA-256 tag so that two runs can be compared).
Uses QiskitRuntimeService() with the saved default account; never save_account.
"""
import hashlib
import json
import sys

from qiskit_ibm_runtime import QiskitRuntimeService, __version__ as rt_version


def tag(s):
    return hashlib.sha256(str(s).encode()).hexdigest()[:10] if s else None


def main():
    out = {"qiskit_ibm_runtime": rt_version}
    try:
        service = QiskitRuntimeService()
    except Exception as e:  # account missing / invalid
        out["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        print(json.dumps(out, indent=1))
        sys.exit(2)
    out["channel"] = getattr(service, "channel", None)
    try:
        insts = service.instances()
        rows = []
        for it in insts:
            if isinstance(it, dict):
                rows.append({"name": it.get("name"), "plan": it.get("plan"),
                             "pricing_type": it.get("pricing_type"),
                             "crn_tag": tag(it.get("crn"))})
            else:
                rows.append({"crn_tag": tag(it)})
        out["instances"] = rows
    except Exception as e:
        out["instances_error"] = f"{type(e).__name__}: {str(e)[:300]}"
    try:
        u = service.usage()
        keep = {}
        for k, v in (u or {}).items():
            if "instance" in k.lower() or "crn" in k.lower() or "id" == k.lower()[-2:]:
                keep[k] = tag(v)
            else:
                keep[k] = v
        out["usage"] = keep
    except Exception as e:
        out["usage_error"] = f"{type(e).__name__}: {str(e)[:300]}"
    try:
        bl = []
        for b in service.backends(simulator=False):
            try:
                st = b.status()
                op, pend = st.operational, st.pending_jobs
            except Exception:
                op, pend = None, None
            bl.append({"name": b.name, "num_qubits": b.num_qubits,
                       "processor_type": getattr(b, "processor_type", None),
                       "operational": op, "pending_jobs": pend})
        out["backends"] = bl
    except Exception as e:
        out["backends_error"] = f"{type(e).__name__}: {str(e)[:300]}"
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
