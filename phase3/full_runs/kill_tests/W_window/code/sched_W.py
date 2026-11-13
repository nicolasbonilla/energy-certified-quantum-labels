"""Task runner for kill test W (sched_T.py of test T with a per-task script, thread count and environment).
Resumable; one OS process per task.

  python sched_W.py <root> <plan.json> <python>
Control files in <root>/out/sched/: slots.txt (concurrent tasks, default 8), mem.txt (GB budget, default 56; each task
declares 'mem' GB), skip.txt (task ids to drop, one per line), STOP (finish running tasks, start nothing new).
State: <id>.ok / <id>.fail markers, out/logs/<id>.log, sched_log.txt (start/end times, exit codes).
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


def main(root, plan, py):
    S = os.path.join(root, "out", "sched")
    L = os.path.join(root, "out", "logs")
    os.makedirs(S, exist_ok=True); os.makedirs(L, exist_ok=True)
    tasks = json.load(open(plan))["tasks"]
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
        memb = float(rd(os.path.join(S, "mem.txt"), "56"))
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
                if t["id"] in blocked or t["id"] in done:
                    continue
                if t["id"] in skip or t["id"] in failed or any(d in failed or d in skip or d in blocked for d in t["deps"]):
                    blocked.add(t["id"]); changed = True
        ready = [t for t in byid.values() if t["id"] not in done and t["id"] not in running and t["id"] not in blocked
                 and all(d in done for d in t["deps"])]
        ready.sort(key=lambda t: (t["prio"], tasks.index(t)))
        if not stop:
            used = sum(byid[t].get("mem", 1) for t in running)
            while ready and len(running) < slots:
                fit = [t for t in ready if used + t.get("mem", 1) <= memb]
                if not fit:
                    break
                t = fit[0]
                ready.remove(t)
                used += t.get("mem", 1)
                env = dict(os.environ)
                thr = str(t.get("threads", 1))
                for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
                    env[k] = thr
                env.update(t.get("env", {}))
                lf = open(os.path.join(L, t["id"] + ".log"), "a")
                p = subprocess.Popen([py, "-B", os.path.join(root, "code", t["script"]), root] + t["args"],
                                     stdout=lf, stderr=subprocess.STDOUT, env=env, cwd=os.path.join(root, "code"))
                running[t["id"]] = (p, time.time())
                note("start %s threads=%s mem=%s pid=%d" % (t["id"], thr, t.get("mem", 1), p.pid))
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
