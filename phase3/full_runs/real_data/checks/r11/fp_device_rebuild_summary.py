"""real_data/checks/r11/fp_device_rebuild_summary.py  (R11 fix pass, fixer FP, 2026-11-13; descriptive)

Runs fp_device_rebuild.py (next to this file) for the four cases of the device labels with proved intervals (job B at
Jz = 4.0 and job C at Jz = 6.0, each with recovery and with post-selection) and prints, from the four JSON files it
writes, what the Supplement states about that rebuild: the subspace is reproduced, the rounded vector is or is not
reproduced bit for bit, and the exact energy of the rebuilt vector minus the stored exact energy.

  python -B -I fp_device_rebuild_summary.py [--no-run]     (writes fp_device_rebuild_out.txt next to this file)
With --no-run the four JSON files are read as they are. Each run takes 10 to 40 s on a laptop (2 threads).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = [("C", "6.0", "rec"), ("C", "6.0", "ps"), ("B", "4.0", "rec"), ("B", "4.0", "ps")]
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


if "--no-run" not in sys.argv:
    env = dict(os.environ, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", MKL_NUM_THREADS="2")
    for job, J, var in CASES:
        r = subprocess.run([sys.executable, "-B", "-I", os.path.join(HERE, "fp_device_rebuild.py"), job, J, var],
                           capture_output=True, text=True, errors="replace", env=env)
        if r.returncode != 0:
            raise SystemExit("fp_device_rebuild.py %s %s %s failed:\n%s" % (job, J, var, r.stderr[-2000:]))

P("job  Jz   reading  D (rebuilt = stored)   vector bit-identical   exact E rebuilt minus stored   m_s, Czz rebuilt minus stored")
worst = 0.0
for job, J, var in CASES:
    d = json.load(open(os.path.join(HERE, "fp_device_rebuild_%s_%s_%s.json" % (job, J, var)), encoding="utf-8"))
    assert d["D"] == d["stored_D"] and d["all_in_sector"] and d["sample_rows_mismatch"] == 0
    worst = max(worst, abs(d["E_exact_own_minus_stored"]))
    P("%-4s %-4s %-8s %-22s %-22s %-29s %s" % (
        job, J, "recovery" if var == "rec" else "post-sel", "%d = %d" % (d["D"], d["stored_D"]),
        "yes" if d["vector_bit_identical"] else "no", "%.1e" % d["E_exact_own_minus_stored"],
        "%.1e, %.1e" % (d["m_s_own_minus_stored"], d["Czz_own_minus_stored"])))
P("")
P("greatest |exact E rebuilt minus stored| over the four cases: %.1e (below 1e-25: %s)" % (worst, worst < 1e-25))
P("all four subspaces reproduced exactly (same dimension, every configuration in the sector): True")
open(os.path.join(HERE, "fp_device_rebuild_out.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
