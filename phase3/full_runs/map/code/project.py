"""Cost projection at the checkpoint (DECLARATION §5). Laptop; reads the plan and the scheduler log fetched from the VM.

  python -I project.py <plan.json> <sched_log.txt> <elapsed_vm_hours> [<slots>=8] [<skip.txt>]
Category of a task = (kind, n, label class). Mean duration of the finished tasks of each category; categories with no
finished task borrow the n = 57 mean x 2.4 (n = 115) or the overall lab mean. Running tasks count half. The projection
is elapsed + remaining job-hours / slots (the tail is ignored, so it is optimistic by about one long task).
"""
import json
import re
import sys
from collections import defaultdict


def cat(t):
    a = t["args"]
    k = a[0]
    n = a[1] if len(a) > 1 else "-"
    lab = a[3] if (k == "lab" and len(a) > 3) else (a[3] if k == "ref" else "")
    if k == "lab":
        lab = "avg" if lab in ("m_s", "Czz_bar") else ("c2" if lab == "C2_bar" else "loc")
    return (k, n, lab)


def main(plan, logp, elapsed, slots=8, skipp=None):
    T = json.load(open(plan))["tasks"]
    skip = set(open(skipp).read().split()) if skipp else set()
    start, end = {}, {}
    for line in open(logp):
        m = re.match(r"(\S+) (start|end) (\S+)", line)
        if not m:
            continue
        if m.group(2) == "start":
            start[m.group(3)] = m.group(1)
        else:
            d = re.search(r" (\d+)s$", line.strip())
            end[m.group(3)] = float(d.group(1)) if d else None
    dur = defaultdict(list)
    for t in T:
        if t["id"] in end and end[t["id"]]:
            dur[cat(t)].append(end[t["id"]])
    mean = {c: sum(v) / len(v) for c, v in dur.items()}
    labs = [v for c, vs in dur.items() if c[0] == "lab" for v in vs]
    lab_mean = sum(labs) / len(labs) if labs else 900.0
    rem = 0.0
    by = defaultdict(float)
    for t in T:
        if t["id"] in end or t["id"] in skip:
            continue
        c = cat(t)
        if c in mean:
            m = mean[c]
        elif c[1] == "115" and (c[0], "57", c[2]) in mean:
            m = 2.4 * mean[(c[0], "57", c[2])]
        else:
            m = lab_mean * (2.4 if c[1] == "115" else 1.0)
        w = 0.5 if t["id"] in start else 1.0
        rem += w * m
        by[t["prio"]] += w * m / 3600
    proj = float(elapsed) + rem / 3600 / int(slots)
    print(json.dumps(dict(mean_s={"%s/%s/%s" % c: round(v) for c, v in sorted(mean.items())},
                          remaining_job_h=round(rem / 3600, 2), remaining_by_prio={k: round(v, 2) for k, v in
                                                                                  sorted(by.items())},
                          projected_vm_h=round(proj, 2)), indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
