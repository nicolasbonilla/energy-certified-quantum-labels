"""VM job runner: for each job of plan.json run (separate processes) lb_opt.py -> verify_exact.py [-> ed_sector.py].
usage: python run_all.py <sandbox> <plan.json> <n_parallel>     (writes <sandbox>/out/jobs/, <sandbox>/out/run_log.txt)
A file <sandbox>/out/STOP stops launching new jobs."""
import json
import os
import subprocess
import sys
import time

SB, PLAN, NP = sys.argv[1], sys.argv[2], int(sys.argv[3])
CODE = os.path.join(SB, "code")
OUT = os.path.join(SB, "out", "jobs")
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(SB, "out", "run_log.txt"), "a")


def log(s):
    LOG.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), s))
    LOG.flush()


def script(job):
    j = job["id"]
    g = os.path.join(CODE, "graphs", job["graph"])
    tp = os.path.join(OUT, j + "_task.json")
    json.dump(job["task"], open(tp, "w"), indent=1)
    py = sys.executable
    cmd = "%s -B lb_opt.py %s %s %s > %s 2>&1 && %s -B verify_exact.py %s %s %s > %s 2>&1" % (
        py, g, tp, os.path.join(OUT, j + "_cert.json"), os.path.join(OUT, j + "_opt.log"),
        py, g, os.path.join(OUT, j + "_cert.json"), os.path.join(OUT, j + "_ver.json"), os.path.join(OUT, j + "_ver.log"))
    if job.get("ed"):
        cmd += " ; %s -B ed_sector.py %s %s %s > %s 2>&1" % (py, g, tp, os.path.join(OUT, j + "_ed.json"),
                                                          os.path.join(OUT, j + "_ed.log"))
    return cmd


plan = json.load(open(PLAN))
queue = [j for j in plan if not os.path.exists(os.path.join(OUT, j["id"] + ".done"))]
running = {}
log("start %d jobs, %d parallel" % (len(queue), NP))
while queue or running:
    for jid, (p, t0) in list(running.items()):
        if p.poll() is not None:
            open(os.path.join(OUT, jid + ".done"), "w").write("rc=%d time_s=%.1f\n" % (p.returncode, time.time() - t0))
            log("done %s rc=%d %.1fs" % (jid, p.returncode, time.time() - t0))
            del running[jid]
    while queue and len(running) < NP and not os.path.exists(os.path.join(SB, "out", "STOP")):
        job = queue.pop(0)
        p = subprocess.Popen(script(job), shell=True, cwd=CODE)
        running[job["id"]] = (p, time.time())
        log("launch %s" % job["id"])
    if os.path.exists(os.path.join(SB, "out", "STOP")) and not running:
        break
    time.sleep(2)
log("exit (queue left %d)" % len(queue))
open(os.path.join(SB, "out", "RUN_EXIT"), "w").write("exit %s\n" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
