"""Laptop, seconds, before the hash: copies the stored inputs of the final tests into final_tests/inputs/ (no physics).
usage: python make_inputs.py <phase3/full_runs>"""
import glob
import json
import os
import shutil
import sys
from fractions import Fraction

R = sys.argv[1]
F = os.path.join(R, "final_tests", "inputs")
os.makedirs(F, exist_ok=True)
M = os.path.join(R, "method", "out_20261030T003230Z", "out")
for n in (57, 115):
    shutil.copy(os.path.join(M, "calib", "calib_n%d.json" % n), F)
for j in ("4.0", "6.0"):
    shutil.copy(os.path.join(M, "ref", "ref_n57_J%s.json" % j), F)
shutil.copy(os.path.join(M, "ref", "ref_n57_J2.5.json"), os.path.join(F, "stored_ref_n57_J2.5.json"))
shutil.copy(os.path.join(M, "emu", "emu_n57_J2.5.json"), os.path.join(F, "stored_emu_n57_J2.5.json"))
shutil.copy(os.path.join(R, "bias_law", "inputs", "n19_curves.json"), os.path.join(F, "stored_n19_curves.json"))
shutil.copy(os.path.join(R, "qpu", "jobs", "B", "raw_configs.npz"), os.path.join(F, "qpu_B_raw_configs.npz"))
fb = json.load(open(os.path.join(R, "qpu", "jobs", "B", "fetch.json")))
json.dump({k: {a: v[a] for a in ("shots", "unique", "unique_in_sector", "shots_in_sector")} for k, v in fb["pubs"].items()},
          open(os.path.join(F, "qpu_B_pubs.json"), "w"), indent=1)
shutil.copy(os.path.join(R, "qpu", "out_20261031T093107Z", "out", "device_B_J4.0.json"), os.path.join(F, "stored_device_B_J4.0.json"))
certs = []
for d in ("rigor/out_20261031T073328Z/out/jobs", "rigor/out_20261031T100015Z/out/jobs"):
    for vf in sorted(glob.glob(os.path.join(R, d, "*_ver.json"))):
        jid = os.path.basename(vf)[:-9]
        tf = vf.replace("_ver.json", "_task.json")
        if "n57_" not in jid or not os.path.exists(tf):
            continue
        t = json.load(open(tf))
        v = json.load(open(vf))
        if Fraction(str(t["Jz"])) not in (4, 6) or t["kind"] == "H" or not v.get("ok"):
            continue
        certs.append(dict(kind=t["kind"], Jz=str(t["Jz"]), sigma=int(t["sigma"]), lam=str(t["lam"]), level=t["clusters"],
                          E_LB_exact=v["E_LB_exact"], src=d.split("/")[1] + "/" + jid, cert_sha256=v["cert_sha256"]))
json.dump(certs, open(os.path.join(F, "certs_n57_stored.json"), "w"), indent=0)
print(len(certs), "stored certificates at n = 57, Jz = 4, 6")
