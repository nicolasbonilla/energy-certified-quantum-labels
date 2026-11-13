"""Task runner (copy of full_runs/huang/code/sched.py; only the task script name changed to task_l.py). Resumable; one OS process per task.

  python sched.py <root> <plan.json> <python> [<only-prio-max>]
Control files in <root>/out/sched/: slots.txt (concurrent tasks, default 8), threads.txt (BLAS threads per task,
default 1), skip.txt (task ids to drop, one per line), STOP (finish running tasks, start nothing new).
State: <id>.ok / <id>.fail markers, logs/<id>.log, sched_log.txt (start/end times, exit codes).
"""
import json
import os
import subprocess
import sys
import time


def rd(path, default):
    try:
        with open(path) as f:
            return f.read().strip() or default
    except OSError:
        return default


def main(root, plan, py, prio_max=None):
    S = os.path.join(root, "out", "sched")
    L = os.path.join(root, "out", "logs")
    os.makedirs(S, exist_ok=True); os.makedirs(L, exist_ok=True)
    tasks = json.load(open(plan))["tasks"]
    if prio_max is not None:
        tasks = [t for t in tasks if t["prio"] <= int(prio_max)]
    byid = {t["id"]: t for t in tasks}
    running = {}
    log = open(os.path.join(S, "sched_log.txt"), "a")

    def note(msg):
        log.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)); log.flush()
    note("scheduler start pid=%d tasks=%d" % (os.getpid(), len(tasks)))
    while True:
        skip = set(rd(os.path.join(S, "skip.txt"), "").split())
        stop = os.path.exists(os.path.join(S, "STOP"))
        slots = int(rd(os.path.join(S, "slots.txt"), "8"))
        thr = rd(os.path.join(S, "threads.txt"), "1")
        # reap
        for tid, (p, t0) in list(running.items()):
            rc = p.poll()
            if rc is not None:
                open(os.path.join(S, tid + (".ok" if rc == 0 else ".fail")), "w").write("%d %.0f\n" % (rc, time.time() - t0))
                note("end %s rc=%d %.0fs" % (tid, rc, time.time() - t0))
                del running[tid]
        done = {t for t in byid if os.path.exists(os.path.join(S, t + ".ok"))}
        failed = {t for t in byid if os.path.exists(os.path.join(S, t + ".fail"))}
        blocked = set()
        changed = True
        while changed:
            changed = False
            for t in byid.values():
                if t["id"] in blocked:
                    continue
                if t["id"] in skip or t["id"] in failed or any(d in failed or d in skip or d in blocked for d in t["deps"]):
                    if t["id"] not in done:
                        blocked.add(t["id"]); changed = True
        ready = [t for t in byid.values() if t["id"] not in done and t["id"] not in running and t["id"] not in blocked
                 and all(d in done for d in t["deps"])]
        ready.sort(key=lambda t: (t["prio"], tasks.index(t)))
        if not stop:
            while ready and len(running) < slots:
                t = ready.pop(0)
                env = dict(os.environ)
                for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
                    env[k] = thr
                lf = open(os.path.join(L, t["id"] + ".log"), "a")
                p = subprocess.Popen([py, "-B", os.path.join(root, "code", "task_l.py"), root] + t["args"],
                                     stdout=lf, stderr=subprocess.STDOUT, env=env, cwd=os.path.join(root, "code"))
                running[t["id"]] = (p, time.time())
                note("start %s threads=%s pid=%d" % (t["id"], thr, p.pid))
        pending = [t for t in byid if t not in done and t not in blocked]
        if not running and (stop or not [t for t in pending if all(d in done for d in byid[t]["deps"])]):
            note("scheduler exit: done=%d failed=%d blocked=%d pending=%d" % (len(done), len(failed), len(blocked),
                                                                             len(pending)))
            open(os.path.join(S, "SCHED_EXIT"), "w").write("%d %d %d %d\n" % (len(done), len(failed), len(blocked),
                                                                             len(pending)))
            break
        time.sleep(10)


if __name__ == "__main__":
    main(*sys.argv[1:])
