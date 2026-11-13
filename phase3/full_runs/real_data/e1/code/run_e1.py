"""E1 scheduler (laptop): branch-and-bound over the declared lambda grid and the stage rule of
rigor/DECLARATION_v2.md Secs. 2-3, for the five m_s rows of extension E1 (real_data/DECLARATION.md Sec. 3).

Derived from rigor/code/run_v2.py (SHA-256 d511e631...). UNCHANGED from it: the order of the points of a side
(increasing u_lb), one job per side at a time, the stopping rule u_lb(next) >= best - 0.01 tau, "only verified bounds
count", stage B (edge balls at the best vertex-ball point of each side when both sides are done and the row is wider
than 0.85 tau), the optimizer settings (plan_e1.json; OPT_E below), the caps of stage B (n = 57: 8 jobs, as S2;
n = 115: 4 jobs and only if less than 2.5 h have passed since the first start, as S3), stage B of a row before stage A
of the rows that follow it in priority.
CHANGED (plumbing only): rows are ranked in the order of priority of E1 (n = 57: 3.3, 3.2; n = 115: 5.0, 3.6, 3.3);
no earlier certificates exist at these couplings; jobs are started without a shell through job_e1.py (Windows), two
threads each; every certificate is proved by the stored verifier AND by the independent one; a status file; a hard
stop at the cap (jobs still running are stopped and counted as not computed); a restart resumes from the files on disk.

usage: python -B run_e1.py [n_parallel = 6] [cap_hours = 8]
stop:  create out/STOP (no new job; running jobs finish) or out/KILL (running jobs are stopped at once)
"""
import glob
import json
import os
import subprocess
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
SB = os.path.dirname(HERE)
CODE = HERE
OUTD = os.path.join(SB, "out")
OUT = os.path.join(OUTD, "jobs")
PLAN = os.path.join(SB, "plan_e1.json")
GRID = os.path.join(SB, "grid_e1.json")
STATUS = os.path.join(SB, "STATUS.json")
NP = int(sys.argv[1]) if len(sys.argv) > 1 else 6
CAP_H = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUTD, "run_log.txt"), "a")
OPT_E = dict(K=32, maxiter=600, betas=[30, 300, 3000, 30000, 100000], use_mu=True, clusters="eball2")
CAPB = {"E57": 8, "E115": 4}
LATE_B = {"E115": 2.5 * 3600}
TOL = 0.01
ENV = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", NUMEXPR_NUM_THREADS="2",
           PYTHONDONTWRITEBYTECODE="1")


def utc(t=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def log(s):
    LOG.write("%s %s\n" % (utc(), s))
    LOG.flush()


t0p = os.path.join(OUTD, "T0.txt")
if os.path.exists(t0p):
    T0 = float(open(t0p).read().split()[0])
    RESUMED = True
else:
    T0 = time.time()
    open(t0p, "w").write("%r %s first start of the E1 scheduler; the cap of %g h counts from here\n" % (T0, utc(T0), CAP_H))
    RESUMED = False
DEADLINE = T0 + CAP_H * 3600


def key(n, kind, Jz, sigma, lam):
    return (int(n), kind, Fraction(str(Jz)), int(sigma), Fraction(str(lam)))


def rj(path):
    try:
        return json.load(open(path))
    except Exception:
        return None


def verdicts(jid):
    """(E_LB or None, dict for the status file). A bound counts only with an ok record of the stored verifier; a
    record of the independent verifier that does not confirm it makes the certificate DISPUTED (it does not count)."""
    v = rj(os.path.join(OUT, jid + "_verify_exact.json"))
    m = rj(os.path.join(OUT, jid + "_myver.json"))
    d = dict(stored_verifier=None if v is None else bool(v.get("ok")), independent_verifier=None)
    if m is not None:
        okm = bool(m.get("all_cluster_inequalities_proved")) and m.get("identity_holds") is True and bool(m.get("E_matches_cert_claim"))
        if v is not None and v.get("ok"):
            okm = okm and Fraction(m["E_LB_exact"]) == Fraction(v["E_LB_exact"]) and m.get("cert_sha256") == v.get("cert_sha256")
        d["independent_verifier"] = okm
        d["independent_methods"] = m.get("methods")
    if v is None or not v.get("ok"):
        return None, d
    d["E_LB_exact"] = v["E_LB_exact"]
    if d["independent_verifier"] is False:
        d["DISPUTED"] = True
        return None, d
    return v["E_LB_float_floor"], d


plan = json.load(open(PLAN))
grid = json.load(open(GRID))
rows = {"%d_%.1f_%s" % (g["n"], g["Jz"], g["label"]): g for g in grid}
PRIO = {rk: g["prio"] for rk, g in rows.items()}
sides = {}
for p in plan:
    sides.setdefault((p["row"], p["side"]), []).append(p)
for k in sides:
    sides[k].sort(key=lambda p: p["u_lb"])
state = {k: dict(i=0, best=None, best_pt=None, running=False, done=False) for k in sides}
stageB_used = {"E57": 0, "E115": 0}
stageB_done_rows = set()
stageB_skipped = {}
pending_B = []
running = {}
jobs = {}            # jid -> record for the status file
known = {}
stop_reason = None


def u_of(row, p, E):
    return (row["E_up"] - E) / (p["lam_f"] * row["S"])


def known_at(p):
    t = p["task"]
    return known.get(key(p["n"], t["kind"], t["Jz"], t["sigma"], t["lam"]), [])


def job_record(jid, p, kind, **kw):
    t = p["task"]
    r = jobs.setdefault(jid, dict(id=jid, stage=kind, level=t["clusters"], n=p["n"], Jz=t["Jz"], sigma=t["sigma"],
                                  lam=t["lam"], lam_f=p["lam_f"], row=p["row"], side=p["side"], point=p["kind"]))
    r.update(kw)
    return r


def absorb(jid, p, kind, k):
    """Reads the files of a finished job; a verified bound enters `known` and the best of its side."""
    E, d = verdicts(jid)
    done = rj(os.path.join(OUT, jid + ".done")) or {}
    r = job_record(jid, p, kind, **d)
    r["steps"] = done.get("steps")
    if E is None:
        r["state"] = "DISPUTED" if d.get("DISPUTED") else "failed (no ok record of the stored verifier)"
        return None
    t = p["task"]
    known.setdefault(key(p["n"], t["kind"], t["Jz"], t["sigma"], t["lam"]), []).append((E, t["clusters"], "e1:" + jid))
    row = rows[p["row"]]
    u = u_of(row, p, E)
    r.update(state="verified", E_LB=E, u=u, u_over_tau=u / row["tau"],
             slack=(p["F"] if p.get("F") is not None else p["F_up"]) - E if (p.get("F") is not None or p.get("F_up") is not None) else None)
    if state[k]["best"] is None or u < state[k]["best"]:
        state[k]["best"], state[k]["best_pt"] = u, dict(p, E_LB=E, level=t["clusters"], src="e1:" + jid)
    return E


# resume: every finished job on disk (vertex balls of the plan; edge balls recognised by their id)
if RESUMED:
    for k in sides:
        for p in sides[k]:
            if os.path.exists(os.path.join(OUT, p["id"] + ".done")):
                absorb(p["id"], p, "A", k)
            jb = p["id"].replace("vball2", "eball2")
            if os.path.exists(os.path.join(OUT, jb + ".done")):
                t = p["task"]
                pb = dict(p, task=dict(OPT_E, kind=t["kind"], Jz=t["Jz"], sigma=t["sigma"], lam=t["lam"]), id=jb, stageB_side=list(k))
                absorb(jb, pb, "B", k)
                stageB_used[rows[p["row"]]["scope"]] += 1


def launch(job, jid):
    g = os.path.join(CODE, "graphs", job["graph"])
    tp = os.path.join(OUT, jid + "_task.json")
    json.dump(job["task"], open(tp, "w"), indent=1)
    err = open(os.path.join(OUT, jid + "_job.log"), "w")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return subprocess.Popen([sys.executable, "-B", os.path.join(CODE, "job_e1.py"), g, tp, os.path.join(OUT, jid)],
                            cwd=CODE, env=ENV, stdin=subprocess.DEVNULL, stdout=err, stderr=subprocess.STDOUT,
                            creationflags=flags)


def kill_tree(pid):
    try:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=60)
    except Exception as ex:
        log("taskkill %s: %r" % (pid, ex))


def next_point(k):
    st = state[k]
    while st["i"] < len(sides[k]):
        p = sides[k][st["i"]]
        if st["best"] is not None and p["u_lb"] >= st["best"] - TOL * rows[k[0]]["tau"]:
            st["done"] = True
            return None
        if any(lev == "vball2" for (E, lev, src) in known_at(p)) or p["id"] in jobs:
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
            c.append((2 * PRIO[k[0]], p["u_lb"], ("A", k, p)))
    for j in pending_B:
        if not j.get("_launched"):
            c.append((2 * PRIO[j["row"]] + 1, 0.0, ("B", None, j)))
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
        log("row %s stage A done: w_cert/tau = %.4f (at E_real + 1e-6, in-sector form)" % (rk, w / row["tau"]))
        if w <= 0.85 * row["tau"]:
            stageB_skipped[rk] = "not needed (row at most 0.85 tau after stage A)"
            continue
        if sc in LATE_B and time.time() - T0 > LATE_B[sc]:
            stageB_skipped[rk] = "skipped by the declared rule: more than 2.5 h since the start (%.2f h)" % ((time.time() - T0) / 3600)
            log("stage B skipped for %s (elapsed > 2.5 h)" % rk)
            continue
        for k in (kp, km):
            bp = state[k]["best_pt"]
            if any(lev == "eball2" for (E, lev, src) in known_at(bp)):
                continue
            if stageB_used[sc] >= CAPB[sc]:
                log("stage B cap reached for %s" % sc)
                stageB_skipped[rk] = "cap of stage B reached"
                continue
            stageB_used[sc] += 1
            t = bp["task"]
            task = dict(OPT_E, kind=t["kind"], Jz=t["Jz"], sigma=t["sigma"], lam=t["lam"])
            j = dict(bp, task=task, id=bp["id"].replace("vball2", "eball2"), stageB_side=list(k))
            for extra in ("E_LB", "level", "src"):
                j.pop(extra, None)
            pending_B.append(j)
            log("stage B queued %s" % j["id"])


def dump_status(finished=False):
    now = time.time()
    R = {}
    for rk, row in sorted(rows.items(), key=lambda x: x[1]["prio"]):
        sd = {}
        for s in "+-":
            st = state[(rk, s)]
            bp = st["best_pt"]
            sd[s] = dict(best_u=st["best"], best_u_over_tau=None if st["best"] is None else st["best"] / row["tau"],
                         best_job=None if bp is None else bp["src"][3:], best_level=None if bp is None else bp["level"],
                         best_lam=None if bp is None else bp["lam_f"], stage_A_done=st["done"] and not st["running"],
                         points_done=st["i"], points_kept_in_grid=len(sides[(rk, s)]),
                         n_verified=sum(1 for j in jobs.values() if j["row"] == rk and j["side"] == s and j.get("state") == "verified"))
        both = sd["+"]["best_u"] is not None and sd["-"]["best_u"] is not None
        w = (sd["+"]["best_u"] + sd["-"]["best_u"]) if both else None
        R[rk] = dict(priority=row["prio"], n=row["n"], Jz=row["Jz"], label="m_s", tau=row["tau"], E_up_used=row["E_up"],
                     w_F_over_tau=row["w_F"] / row["tau"], sides=sd,
                     interval_in_sector_form=None if not both else [-sd["-"]["best_u"], sd["+"]["best_u"]],
                     w_cert_over_tau=None if w is None else w / row["tau"],
                     within_tau_in_sector_form=None if w is None else bool(w <= row["tau"]),
                     has_certificates_both_sides=both,
                     stage_A_done=sd["+"]["stage_A_done"] and sd["-"]["stage_A_done"],
                     stage_B=stageB_skipped.get(rk, [j["id"] for j in pending_B if j["row"] == rk] or
                                                ("pending" if rk not in stageB_done_rows else "none queued")))
    cnt = {}
    for j in jobs.values():
        cnt[j.get("state", "?")] = cnt.get(j.get("state", "?"), 0) + 1
    st = dict(schema="p5-e1-status-v1", what="Extension E1 of real_data/DECLARATION.md Sec. 3: new exact m_s certificates. "
              "The widths here are in the in-sector form at E_real + 1e-6 (they steer the search); the E1 column of the "
              "map (energy and mean magnetization, Sec. 2) is computed by collect_e1.py.",
              updated_utc=utc(now), first_start_utc=utc(T0), cap_hours=CAP_H, hard_stop_utc=utc(DEADLINE),
              elapsed_hours=round((now - T0) / 3600, 3), finished=finished, stop_reason=stop_reason,
              scheduler_pid=os.getpid(), n_parallel=NP, threads_per_process=2,
              running=[dict(id=jid, pid=v[0].pid, stage=v[2], minutes=round((now - v[1]) / 60, 1)) for jid, v in running.items()],
              job_counts=cnt, stage_B_jobs_used=stageB_used, rows=R,
              jobs=sorted(jobs.values(), key=lambda j: (PRIO[j["row"]], j["side"], j["level"], j["lam_f"])))
    tmp = STATUS + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATUS)
    json.dump(dict(scheduler=os.getpid(), jobs={jid: v[0].pid for jid, v in running.items()}, updated_utc=utc(now)),
              open(os.path.join(OUTD, "pids.json.tmp"), "w"))
    os.replace(os.path.join(OUTD, "pids.json.tmp"), os.path.join(OUTD, "pids.json"))


if RESUMED:
    # jobs left over from a previous start (a scheduler that died) are stopped before anything is started again
    import watchdog_e1 as W
    for pid, cl in W.e1_processes():
        if pid != os.getpid() and "run_e1.py" not in cl:
            kill_tree(pid)
            log("resume: stopped a process left over from the previous start: pid %d" % pid)
    time.sleep(2)

log("E1 start%s: %d sides, %d kept grid points, %d parallel, cap %g h, hard stop %s; verified on disk: %d" % (
    " (RESUMED)" if RESUMED else "", len(sides), len(plan), NP, CAP_H, utc(DEADLINE),
    sum(1 for j in jobs.values() if j.get("state") == "verified")))
while True:
    for jid, (proc, t0, kind, k, p) in list(running.items()):
        if proc.poll() is None:
            continue
        kk = k if kind == "A" else tuple(p["stageB_side"])
        E = absorb(jid, p, kind, kk)
        jobs[jid]["wall_s"] = round(time.time() - t0, 1)
        log("done %s rc=%s %.1fs E_LB=%s" % (jid, proc.returncode, time.time() - t0, E))
        del running[jid]
        if kind == "A":
            state[k]["running"] = False
            state[k]["i"] += 1
    check_stageB()
    now = time.time()
    kill = os.path.exists(os.path.join(OUTD, "KILL")) or now > DEADLINE
    stop = kill or os.path.exists(os.path.join(OUTD, "STOP")) or now > DEADLINE - min(600.0, 360 * CAP_H)
    if kill:
        stop_reason = "cap of %g h reached" % CAP_H if now > DEADLINE else "file out/KILL"
        for jid, (proc, t0, kind, k, p) in list(running.items()):
            kill_tree(proc.pid)
            job_record(jid, p, kind, state="stopped: not finished (%s)" % stop_reason, wall_s=round(now - t0, 1))
            log("stopped %s (%s)" % (jid, stop_reason))
            del running[jid]
            if kind == "A":
                state[k]["running"] = False
    if not stop:
        for item in candidates():
            if len(running) >= NP:
                break
            kind, k, p = item
            jid = p["id"]
            proc = launch(p, jid)
            running[jid] = (proc, time.time(), kind, k, p)
            job_record(jid, p, kind, state="running", started_utc=utc())
            if kind == "A":
                state[k]["running"] = True
            else:
                p["_launched"] = True
            log("launch %s %s pid %d" % (kind, jid, proc.pid))
    elif stop_reason is None and not kill:
        stop_reason = "file out/STOP" if os.path.exists(os.path.join(OUTD, "STOP")) else "less than 10 minutes to the cap: no new job"
    dump_status()
    if not running and (stop or not candidates()):
        break
    time.sleep(5)
check_stageB()
if stop_reason is None:
    stop_reason = "all tasks finished"
dump_status(finished=True)
log("E1 exit (%s)" % stop_reason)
open(os.path.join(OUTD, "RUN_EXIT"), "w").write("exit %s %s\n" % (utc(), stop_reason))
