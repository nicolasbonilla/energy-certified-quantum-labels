"""VM, Test C3: noiseless control of the identical circuits at Jz = 6.0 (protocol of qpu/code/qpu_post.py t_control) and the same
post-processing (rec, ps). Writes <root>/out/c/control_J6.0.json.   usage: python c3_post.py <root> <shots per circuit>"""
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qpu_lib as ql  # noqa: E402
import emu2  # noqa: E402

JZ, DT = 6.0, 0.0681
root, S = sys.argv[1], int(sys.argv[2])


def seed(*parts):
    return int.from_bytes(hashlib.sha256(("qpu|" + "|".join(str(p) for p in parts)).encode()).digest()[:8], "little")


g = emu2.load_graph(os.path.join(HERE, "graphs", "hh_d5.json"))
ref = json.load(open(os.path.join(root, "inputs", "ref_n57_J6.0.json")))
T = ql.TrotterMPS(g, chi_max=256, svd_min=1e-12)
lists, info = [], []
for k in range(1, ql.K + 1):
    t0 = time.time()
    T.step(JZ, DT)
    r = emu2.sample_mps(T.export(), g["order"], 1, S, np.random.default_rng(seed("control", "6.0", k)), g["n"], batch=50000,
                        want_amp=False, merge=True)
    lists.append(emu2.expand(r["B"], r["count"]))
    info.append(dict(k=k, secs=time.time() - t0, max_chi=T.max_chi, discarded_cum=T.discarded, n_unique=int(len(r["B"]))))
    print(info[-1], flush=True)
raw = np.concatenate(lists).astype(np.uint64)
Bu, _ = emu2.unique_rows(raw)
insec = emu2.popcount(Bu) == g["n_down"]
out = dict(Jz=JZ, dt=DT, shots_per_circuit=S, info=info, discarded_total=T.discarded, flag_discarded=bool(T.discarded > 1e-6),
           E0=ref["E0"], m_s_ref=ref["labels"]["m_s"], var={})
for var, recov in (("rec", True), ("ps", False)):
    rng = np.random.default_rng(seed("recover", 57, "6.0", "control", var))
    cs = emu2.CSet(emu2.recover(Bu, g["n"], g["n_down"], rng), g["n"]) if recov else emu2.CSet(Bu[insec], g["n"])
    Hs = emu2.SubH(cs, g, JZ)
    E, a = emu2.ground(Hs, v0=emu2.neel_start(cs, g))
    lab = emu2.diag_labels(cs, a, g)
    out["var"][var] = dict(E=E, eps=E - ref["E0"], D=len(cs), m_s=lab["m_s"], dm_s=lab["m_s"] - ref["labels"]["m_s"],
                           Czz_bar=float(np.mean(lab["Czz"][:len(g["edges"])])))
    print(var, out["var"][var], flush=True)
os.makedirs(os.path.join(root, "out", "c"), exist_ok=True)
json.dump(out, open(os.path.join(root, "out", "c", "control_J6.0.json"), "w"), indent=1)
