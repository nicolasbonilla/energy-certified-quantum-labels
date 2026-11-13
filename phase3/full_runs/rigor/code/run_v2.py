"""v2 VM scheduler: branch-and-bound over the declared lambda grid (DECLARATION_v2.md sections 2-3).

Per side (row, sign): grid points in increasing u_lb (a provable lower bound on the rigorous u of the point). A side
launches its next point only while u_lb(next) < (best rigorous u of that side so far) - TOL*tau, one job per side at a
time, so the side's final best is within TOL*tau of the best over the whole grid (the row width within 2*TOL*tau).
Initial best values come from verified v1 certificates at grid points (read-only, v1 sandbox).
Stage B: when both sides of a row are done and the row's certified width w_cert > 0.85 tau, eball2 is run at the best
vball2 point of each side (caps: S1 8, S2 8, S3 4 jobs; S3 only if elapsed < 2.5 h).
n = 19 gate jobs (with exact diagonalization) are run as plain jobs.
usage: python run_v2.py <sandbox> <plan_v2_A.json> <grid_v2.json> <v1_jobs_dir> <n_parallel> <deadline_epoch_s> [mock]
(mock: scheduler test only; jobs write a fake verification E_LB = F_up - 0.01 instead of computing)
"""
import glob
import json
import os
import subprocess
import sys
import time
from fractions import Fraction

SB, PLAN, GRID, V1, NP, DEADLINE = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), float(sys.argv[6])
MOCK = len(sys.argv) > 7 and sys.argv[7] == "mock"
CODE = os.path.join(SB, "code")
OUT = os.path.join(SB, "out", "jobs")
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(SB, "out", "run_log.txt"), "a")
T0 = time.time()
OPT_E = dict(K=32, maxiter=600, betas=[30, 300, 3000, 30000, 100000], use_mu=True, clusters="eball2")
CAPB = {"S1": 8, "S2": 8, "S3": 4}
RANK = {"S1": 0, "G19": 2, "S2": 3, "S3": 5}
TOL = 0.01


def log(s):
    LOG.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), s))
    LOG.flush()


def key(n, kind, Jz, sigma, lam):
    return (int(n), kind, Fraction(str(Jz)), int(sigma), Fraction(str(lam)))


def read_ver(path):
    try:
        v = json.load(open(path))
        return v["E_LB_float_floor"] if v.get("ok") else None
    except Exception:
        return None


known = {}
for vf in glob.glob(os.path.join(V1, "*_ver.json")):
    jid = os.path.basename(vf)[:-9]
    tf = os.path.join(V1, jid + "_task.json")
    E = read_ver(vf)
    if E is None or not os.path.exists(tf):
        continue
    t = json.load(open(tf))
    n = 57 if "n57_" in jid else (19 if "n19_" in jid else None)
    if n is None:
        continue
    known.setdefault(key(n, t["kind"], t["Jz"], t["sigma"], t["lam"]), []).append((E, t["clusters"], "v1:" + jid))

plan = json.load(open(PLAN))
grid = json.load(open(GRID))
rows = {"%d_%.1f_%s" % (g["n"], g["Jz"], g["label"]): g for g in grid}
sides = {}
for p in plan:
    if p["scope"] == "G19":
        continue
    sides.setdefault((p["row"], p["side"]), []).append(p)
for k in sides:
    sides[k].sort(key=lambda p: p["u_lb"])
state = {k: dict(i=0, best=None, best_pt=None, running=False, done=False) for k in sides}
gate = [p for p in plan if p["scope"] == "G19"]
stageB_used = {"S1": 0, "S2": 0, "S3": 0}
stageB_done_rows = set()
pending_B = []
running = {}


def u_of(row, p, E):
    return (row["E_up"] - E) / (p["lam_f"] * row["S"])


def known_at(p):
    t = p["task"]
    return known.get(key(p["n"], t["kind"], t["Jz"], t["sigma"], t["lam"]), [])


for k in sides:
    row = rows[k[0]]
    for p in sides[k]:
        for (E, lev, src) in known_at(p):
            u = u_of(row, p, E)
            if state[k]["best"] is None or u < state[k]["best"]:
                state[k]["best"], state[k]["best_pt"] = u, dict(p, E_LB=E, level=lev, src=src)


def cmd(job, jid):
    g = os.path.join(CODE, "graphs", job["graph"])
    tp = os.path.join(OUT, jid + "_task.json")
    json.dump(job["task"], open(tp, "w"), indent=1)
    py = sys.executable
    if MOCK:
        E = (job.get("F_up") if job.get("F_up") is not None else -10.0) - 0.01
        return "%s -c \"import json; json.dump(dict(ok=True, E_LB_float_floor=%r, E_LB_exact='0'), open(r'%s','w'))\"" % (
            py, E, os.path.join(OUT, jid + "_ver.json"))
    c = "%s -B lb_opt.py %s %s %s > %s 2>&1 && %s -B verify_exact.py %s %s %s > %s 2>&1" % (
        py, g, tp, os.path.join(OUT, jid + "_cert.json"), os.path.join(OUT, jid + "_opt.log"),
        py, g, os.path.join(OUT, jid + "_cert.json"), os.path.join(OUT, jid + "_ver.json"), os.path.join(OUT, jid + "_ver.log"))
    if job.get("ed"):
        c += " ; %s -B ed_sector.py %s %s %s > %s 2>&1" % (py, g, tp, os.path.join(OUT, jid + "_ed.json"),
                                                         os.path.join(OUT, jid + "_ed.log"))
    return c


def next_point(k):
    st = state[k]
    while st["i"] < len(sides[k]):
        p = sides[k][st["i"]]
        if st["best"] is not None and p["u_lb"] >= st["best"] - TOL * rows[k[0]]["tau"]:
            st["done"] = True
            return None
        if any(lev == "vball2" for (E, lev, src) in known_at(p)):
            st["i"] += 1
            continue
        return p
    st["done"] = True
    return None


def candidates():
    c = []
    for k, st in state.items():
        if st["running"] or st["done"]:
            continue
        p = next_point(k)
        if p is not None:
            c.append((RANK[p["scope"]], p["u_lb"], ("A", k, p)))
    for p in gate:
        if not p.get("_launched"):
            c.append((RANK["G19"], 0.0, ("G", None, p)))
    for j in pending_B:
        if not j.get("_launched"):
            c.append((RANK[j["scope"]] + 1, 0.0, ("B", None, j)))
    c.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in c]


def check_stageB():
    for rk, row in rows.items():
        if rk in stageB_done_rows:
            continue
        kp, km = (rk, "+"), (rk, "-")
        if kp not in state or km not in state:
            continue
        if not (state[kp]["done"] and state[km]["done"]) or state[kp]["running"] or state[km]["running"]:
            continue
        stageB_done_rows.add(rk)
        if state[kp]["best"] is None or state[km]["best"] is None:
            log("row %s stage A done without bounds" % rk)
            continue
        w = state[kp]["best"] + state[km]["best"]
        sc = row["scope"]
        log("row %s stage A done: w_cert/tau = %.4f" % (rk, w / row["tau"]))
        if w <= 0.85 * row["tau"]:
            continue
        if sc == "S3" and time.time() - T0 > 2.5 * 3600:
            log("stage B skipped for %s (elapsed > 2.5 h)" % rk)
            continue
        for k in (kp, km):
            bp = state[k]["best_pt"]
            if any(lev == "eball2" for (E, lev, src) in known_at(bp)):
                continue
            if stageB_used[sc] >= CAPB[sc]:
                log("stage B cap reached for %s" % sc)
                continue
            stageB_used[sc] += 1
            t = bp["task"]
            task = dict(OPT_E, kind=t["kind"], Jz=t["Jz"], sigma=t["sigma"], lam=t["lam"])
            j = dict(bp, task=task, id=bp["id"].replace("vball2", "eball2"), stageB_side=list(k))
            pending_B.append(j)
            log("stage B queued %s" % j["id"])


def dump_state():
    json.dump(dict(time=time.time(), stageB_used=stageB_used,
                   sides={"%s|%s" % k: dict(best=v["best"], done=v["done"], i=v["i"], n_grid=len(sides[k]),
                                            best_pt=(v["best_pt"]["id"] if v["best_pt"] else None),
                                            best_src=(v["best_pt"]["src"] if v["best_pt"] else None))
                          for k, v in state.items()}),
              open(os.path.join(SB, "out", "state_v2.json"), "w"), indent=1)


log("v2 start: %d sides, %d gate jobs, %d parallel; sides with a v1 bound: %d" % (
    len(sides), len(gate), NP, sum(1 for s in state.values() if s["best"] is not None)))
while True:
    for jid, (proc, t0, kind, k, p) in list(running.items()):
        if proc.poll() is None:
            continue
        E = read_ver(os.path.join(OUT, jid + "_ver.json"))
        open(os.path.join(OUT, jid + ".done"), "w").write("rc=%d time_s=%.1f E_LB=%s\n" % (proc.returncode, time.time() - t0, E))
        log("done %s rc=%d %.1fs E_LB=%s" % (jid, proc.returncode, time.time() - t0, E))
        del running[jid]
        if kind in ("A", "B") and E is not None:
            t = p["task"]
            known.setdefault(key(p["n"], t["kind"], t["Jz"], t["sigma"], t["lam"]), []).append((E, t["clusters"], "v2:" + jid))
            kk = k if kind == "A" else tuple(p["stageB_side"])
            u = u_of(rows[kk[0]], p, E)
            if state[kk]["best"] is None or u < state[kk]["best"]:
                state[kk]["best"], state[kk]["best_pt"] = u, dict(p, E_LB=E, level=t["clusters"], src="v2:" + jid)
        if kind == "A":
            state[k]["running"] = False
            state[k]["i"] += 1
    check_stageB()
    stop = os.path.exists(os.path.join(SB, "out", "STOP")) or time.time() > DEADLINE
    if not stop:
        for item in candidates():
            if len(running) >= NP:
                break
            kind, k, p = item
            jid = p["id"]
            proc = subprocess.Popen(cmd(p, jid), shell=True, cwd=CODE)
            running[jid] = (proc, time.time(), kind, k, p)
            if kind == "A":
                state[k]["running"] = True
            else:
                p["_launched"] = True
            log("launch %s %s" % (kind, jid))
    dump_state()
    if not running and (stop or not candidates()):
        break
    time.sleep(0.5 if MOCK else 3)
check_stageB()
dump_state()
log("v2 exit (stop=%s)" % (os.path.exists(os.path.join(SB, "out", "STOP")) or time.time() > DEADLINE))
open(os.path.join(SB, "out", "RUN_EXIT"), "w").write("exit %s\n" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
