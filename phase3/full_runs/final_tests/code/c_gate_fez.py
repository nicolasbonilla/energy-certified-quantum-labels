"""DEVIATIONS.md item 3. The gate of C2 used noise calibrated on ibm_kingston (job B); today's backend rule gives ibm_fez with a worse layout.
Repeats the gate simulation with p_k scaled by the ratio of expected two-qubit errors per Trotter step (and by a higher factor, for margin).
This can only stop the job: it adds a check, it does not relax one.   usage: python c_gate_fez.py <root> <ratio>"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emu2  # noqa: E402
import fr  # noqa: E402
import ft  # noqa: E402
import ftlib as fl  # noqa: E402

root, ratio = sys.argv[1], float(sys.argv[2])
g = fr.graph(57)
sim = json.load(open(os.path.join(root, "out", "c", "sim.json")))
E0 = sim["E0"]["6.0"]
sh6, _, _ = fr.krylov_shots(root, 57, 6.0)
out = dict(ratio=ratio, rows=[])
for name, f in [("scaled", ratio), ("scaled_x1.25", 1.25 * ratio)] + [("f%.2f" % x, x) for x in (1.0, 1.1, 1.2, 1.3, 1.4)]:
    pk = [min(0.5, p * f) for p in sim["p_k"]]
    for r in range(ft.C_SEEDS):
        x = ft.emu_pk(sh6, g, pk, ft.C_SHOTS, 6.0, fl.rng_of("C", "fez", name, r))
        x.update(tag=name, factor=f, seed_index=r, eps=x["E"] - E0, p_k=pk)
        out["rows"].append(x)
        print(name, f, x["eps"], x["D"], x["n_unique_in_sector"], flush=True)
        json.dump(out, open(os.path.join(root, "out", "c", "sim_fez.json"), "w"), indent=1)
