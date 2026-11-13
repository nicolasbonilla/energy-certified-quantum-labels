"""E1 watchdog: an independent process that stops everything of E1 once the cap is over (real_data/DECLARATION.md
Sec. 3: at most 8 hours of wall time in total). The scheduler stops its jobs itself at the cap; this is the backstop.

usage: python -B watchdog_e1.py [cap_hours = 8]     wait until first start + cap + 2 minutes, then stop everything
       python -B watchdog_e1.py --now               stop everything of E1 at once (also creates out/KILL)
       python -B watchdog_e1.py --list              only list the E1 processes that are alive
It ends by itself, without stopping anything, as soon as out/RUN_EXIT exists and no E1 process is left.
"Everything of E1" = the scheduler and the jobs recorded in out/pids.json (with their child processes) and every
python process whose command line contains the folder real_data\\e1\\code (found through PowerShell).
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SB = os.path.dirname(HERE)
OUTD = os.path.join(SB, "out")
MARK = os.path.join(os.path.basename(os.path.dirname(SB)), os.path.basename(SB), "code")   # real_data\e1\code


def utc(t=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def log(s):
    with open(os.path.join(OUTD, "watchdog_log.txt"), "a") as f:
        f.write("%s %s\n" % (utc(), s))


def e1_processes():
    """[(pid, command line)] of the python processes of E1, this process excluded."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
          "ForEach-Object { '{0}|{1}' -f $_.ProcessId, $_.CommandLine }")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True,
                             text=True, timeout=120).stdout
    except Exception as ex:
        log("process listing failed: %r" % ex)
        return []
    res = []
    for line in out.splitlines():
        pid, _, cl = line.partition("|")
        norm = cl.replace("/", "\\").lower()
        if pid.strip().isdigit() and MARK.lower() in norm and int(pid) != os.getpid() and "watchdog_e1.py" not in norm:
            res.append((int(pid), cl.strip()))
    return res


def kill_tree(pid):
    try:
        r = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True, timeout=60)
        return r.returncode
    except Exception as ex:
        return repr(ex)


def stop_all(reason):
    open(os.path.join(OUTD, "KILL"), "w").write("%s %s\n" % (utc(), reason))
    time.sleep(20)                                    # the scheduler stops its own jobs and writes the status file
    pids = {}
    try:
        d = json.load(open(os.path.join(OUTD, "pids.json")))
        pids.update({"job " + k: v for k, v in d.get("jobs", {}).items()})
        pids["scheduler"] = d.get("scheduler")
    except Exception:
        pass
    alive = dict(e1_processes())
    for name, pid in pids.items():
        if pid in alive:
            log("stopping %s pid %s: %s" % (name, pid, kill_tree(pid)))
    for pid, cl in e1_processes():
        log("stopping pid %d (%s): %s" % (pid, cl[-120:], kill_tree(pid)))
    left = e1_processes()
    log("stopped (%s); E1 processes left: %d" % (reason, len(left)))
    open(os.path.join(OUTD, "WATCHDOG_FIRED"), "w").write("%s %s; processes left: %d\n" % (utc(), reason, len(left)))


def main():
    a = sys.argv[1:]
    if a and a[0] == "--list":
        for pid, cl in e1_processes():
            print(pid, cl)
        return 0
    if a and a[0] == "--now":
        stop_all("stopped by hand (watchdog_e1.py --now)")
        return 0
    cap_h = float(a[0]) if a else 8.0
    t0p = os.path.join(OUTD, "T0.txt")
    for _ in range(120):                              # the scheduler writes T0.txt when it starts
        if os.path.exists(t0p):
            break
        time.sleep(5)
    else:
        log("no T0.txt after 10 minutes: nothing to watch")
        return 1
    T0 = float(open(t0p).read().split()[0])
    end = T0 + cap_h * 3600 + 120
    log("watching: first start %s, cap %g h, everything is stopped at %s (pid %d)" % (utc(T0), cap_h, utc(end), os.getpid()))
    while time.time() < end:
        time.sleep(30)
        if os.path.exists(os.path.join(OUTD, "RUN_EXIT")) and not e1_processes():
            log("scheduler has ended and no E1 process is left: nothing to stop")
            return 0
    stop_all("cap of %g h reached" % cap_h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
