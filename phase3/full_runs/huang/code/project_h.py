"""Checkpoint projection (DECLARATION section 5): remaining job-hours and VM-hours from the scheduler log.

  python project_h.py <plan.json> <sched_log.txt> <vm_hours_so_far> [<slots>=4] [<efficiency>=0.65] [skip ids...]
Task time per kind = mean of finished tasks of that kind (kinds: edpairs, edlab, edref, ref<n>, lab<n>, chk, cold,
lawscan), else the declared placeholder; running tasks count half. VM-h remaining = job-h / (slots * efficiency).
"""
import json
import sys

PLACEHOLDER = dict(edref=60, edlab=150, edpairs=420, ref20=600, ref30=1500, ref45=3000, lab20=300, lab30=600,
                   lab45=1200, chk=900, cold=600, lawscan=1200)


def kind_of(t):
    a = t["args"]
    if a[0] in ("ref", "lab"):
        return "%s%d" % (a[0], 5 * int(a[1]))
    return a[0]


def main(plan, log, vmh, slots=4, eff=0.65, *skip):
    tasks = {t["id"]: t for t in json.load(open(plan))["tasks"]}
    start, end = {}, {}
    for line in open(log):
        p = line.split()
        if len(p) >= 3 and p[1] == "start":
            start[p[2]] = p[0]
        if len(p) >= 4 and p[1] == "end":
            end[p[2]] = float(p[4].rstrip("s")) if len(p) > 4 else None
    times = {}
    for tid, dt in end.items():
        if tid in tasks and dt:
            times.setdefault(kind_of(tasks[tid]), []).append(dt)
    mean = {k: sum(v) / len(v) for k, v in times.items()}
    rem = 0.0
    by = {}
    for tid, t in tasks.items():
        if tid in end or tid in skip:
            continue
        k = kind_of(t)
        dt = mean.get(k, PLACEHOLDER.get(k, 900))
        w = 0.5 if tid in start else 1.0
        rem += w * dt
        by[t["prio"]] = by.get(t["prio"], 0.0) + w * dt
    vm_rem = rem / 3600.0 / (int(slots) * float(eff))
    print("measured mean task times (s):", {k: round(v) for k, v in mean.items()})
    print("remaining job-hours %.2f by prio %s" % (rem / 3600, {p: round(v / 3600, 2) for p, v in sorted(by.items())}))
    print("projected total VM-h = %.2f (so far %.2f + remaining %.2f)" % (float(vmh) + vm_rem, float(vmh), vm_rem))


if __name__ == "__main__":
    main(*sys.argv[1:])
