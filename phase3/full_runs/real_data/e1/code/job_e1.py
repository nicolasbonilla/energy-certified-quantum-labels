"""One E1 job = one certificate: optimize (lb_opt.py), prove exactly with the stored verifier (verify_exact.py, the
verifier of record) and with the independent exact verifier (myverify.py). Each step is a separate process, as in
rigor/code/run_v2.py (`lb_opt.py ... && verify_exact.py ...`); the three scripts are byte-identical copies.

usage: python -B job_e1.py <graph.json> <task.json> <output prefix>
files: <prefix>_cert.json            certificate (stored file format)
       <prefix>_verify_exact.json    record of the stored verifier (the stored *_ver.json format). It is NOT named
                                     *_ver.json on purpose: real_data/code/map_certs.py takes every *_cert.json that
                                     has a *_ver.json next to it as an E1 certificate, and that must happen only when
                                     collect_e1.py is run (e1/HOW_TO_COLLECT.md).
       <prefix>_myver.json           record of the independent verifier
       <prefix>_opt.log, _ver.log, _myver.log, <prefix>.done (JSON: return codes and times)
Vertex-ball jobs: stored verifier first, then the independent one (both methods). Edge-ball jobs: independent verifier
first (verified Cholesky, about a minute), then the stored verifier (tens of minutes).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main(g, tp, prefix):
    level = json.load(open(tp))["clusters"]
    py = sys.executable
    rec = dict(id=os.path.basename(prefix), level=level, started_utc=utc(), pid=os.getpid(), steps={})

    def save(name):
        tmp = prefix + name + ".tmp"
        json.dump(rec, open(tmp, "w"), indent=1)
        os.replace(tmp, prefix + name)

    def step(name, args, log, out):
        """Runs one script; its output file is written as <out>.part and renamed when the script has ended."""
        t = time.time()
        part = out + ".part"
        if os.path.exists(part):
            os.remove(part)
        with open(log, "w") as f:
            rc = subprocess.call([py, "-B"] + args + [part], cwd=HERE, stdout=f, stderr=subprocess.STDOUT)
        if os.path.exists(part):
            os.replace(part, out)
        rec["steps"][name] = dict(rc=rc, time_s=round(time.time() - t, 1), ended_utc=utc())
        save(".progress.json")
        return rc

    cert = prefix + "_cert.json"
    for stale in ("_cert.json", "_verify_exact.json", "_myver.json", ".done"):
        if os.path.exists(prefix + stale):
            os.remove(prefix + stale)
    rc = step("lb_opt", ["lb_opt.py", g, tp], prefix + "_opt.log", cert)
    if rc == 0 and os.path.exists(cert):
        stored = ("verify_exact", ["verify_exact.py", g, cert], prefix + "_ver.log", prefix + "_verify_exact.json")
        mine = ("myverify", ["myverify.py", g, cert], prefix + "_myver.log", prefix + "_myver.json")
        if level == "vball2":
            step(*stored)
            step(mine[0], mine[1], mine[2], mine[3])
        else:
            # myverify.py takes its options after the output path: pass them through a tiny wrapper call
            t = time.time()
            part = mine[3] + ".part"
            with open(mine[2], "w") as f:
                rcm = subprocess.call([py, "-B", "myverify.py", g, cert, part, "--methods", "chol"], cwd=HERE, stdout=f,
                                      stderr=subprocess.STDOUT)
            if os.path.exists(part):
                os.replace(part, mine[3])
            rec["steps"]["myverify"] = dict(rc=rcm, time_s=round(time.time() - t, 1), ended_utc=utc(), methods="chol")
            save(".progress.json")
            step(*stored)
    rec["ended_utc"] = utc()
    save(".done")
    if os.path.exists(prefix + ".progress.json"):
        os.remove(prefix + ".progress.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
