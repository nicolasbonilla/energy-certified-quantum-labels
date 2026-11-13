"""Figure of the device run (laptop): (left) signed per-site excess sign(Z_ref)(Z - Z_ref) at Jz = 1.2 for the device
data and the noiseless control of the identical circuits, sites ordered by the reference |Z_ref|; (right) dm_s vs Jz
for device, control, and the method emulation at 1e6 shots (ideal, dev_rec). Reads out_<stamp>/out JSON only."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    od = sys.argv[1]
    dev = rj(os.path.join(od, "device_A_J1.2.json"))
    ctl = rj(os.path.join(od, "control_J1.2.json"))
    ref = rj(os.path.join(ROOT, "refs", "ref_n57_J1.2.json"))
    zr = np.abs(np.array(ref["labels"]["Z"]))
    o = np.argsort(zr)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].plot(np.arange(57), np.array(dev["var"]["rec"]["signed_dZ_site"])[o], "o", ms=4, color="#c0392b",
               label="device (ibm_kingston), recovery")
    ax[0].plot(np.arange(57), np.array(ctl["var"]["rec"]["signed_dZ_site"])[o], "s", ms=3.5, mfc="none",
               color="#2c3e50", label="noiseless control, same circuits")
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].set_xlabel("site (ordered by DMRG |<Z_i>|)")
    ax[0].set_ylabel("sign(Z_ref) (Z_i - Z_ref)")
    ax[0].set_title("Jz = 1.2, n = 57: every site over-ordered")
    ax[0].legend(fontsize=8, loc="lower right")
    J = [1.2, 1.6, 4.0]
    files = {1.2: "device_A_J1.2.json", 1.6: "device_B_J1.6.json", 4.0: "device_B_J4.0.json"}
    d = [rj(os.path.join(od, files[j]))["var"]["rec"]["err"]["dm_s"] for j in J]
    c = [rj(os.path.join(od, "control_J%.1f.json" % j))["var"]["rec"]["err"]["dm_s"] for j in J]
    em = [rj(os.path.join(ROOT, "refs", "emu_n57_J%.1f.json" % j))["var"] for j in J]
    ax[1].plot(J, d, "o-", color="#c0392b", label="device (1e6 shots at 1.2; 2.3e5 at 1.6, 4.0)")
    ax[1].plot(J, c, "s--", mfc="none", color="#2c3e50", label="noiseless control, same circuits and shots")
    ax[1].plot(J, [e["dev_rec"]["err"]["dm_s"] for e in em], "^:", color="#7f8c8d", label="emulation, device-like noise (1e6)")
    ax[1].plot(J, [e["ideal"]["err"]["dm_s"] for e in em], "v:", color="#95a5a6", label="emulation, no noise (1e6)")
    ax[1].axhline(0, color="k", lw=0.6)
    ax[1].set_xlabel("Jz")
    ax[1].set_ylabel("m_s(labels) - m_s(DMRG)")
    ax[1].set_title("signed bias of the raw SKQD stage")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    os.makedirs(os.path.join(ROOT, "analysis"), exist_ok=True)
    fig.savefig(os.path.join(ROOT, "analysis", "fig_qpu.png"), dpi=160)
    print("saved analysis/fig_qpu.png")


if __name__ == "__main__":
    main()
