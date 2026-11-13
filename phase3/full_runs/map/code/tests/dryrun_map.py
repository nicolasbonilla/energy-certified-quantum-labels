"""End-to-end dry run of the MAP plan on TOY graphs (n <= 12), laptop only, for pipeline testing. No number from it
is a map number. (Adapted from design/pilot2/code/tests/dryrun_toy.py.)

  python tests/dryrun_map.py <empty_tmp_root> <slots> [subset]
Copies code/ into <root>/code, replaces graphs/hh_d{3,5,7}.json by toy graphs (task labels n = 19, 57, 115 are kept;
the physics is that of the toys), runs sched.py on the full plan, then g4prep, the separate-process evaluator,
g4check and the summary.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import toygraphs as TG  # noqa: E402


def main(root, slots, subset=False):
    assert not os.path.exists(os.path.join(root, "code")), "root must be empty"
    shutil.copytree(CODE, os.path.join(root, "code"), ignore=shutil.ignore_patterns("__pycache__"))
    g = os.path.join(root, "code", "graphs")
    toys = {3: TG.ring_pendant(8), 5: TG.ring_two_pendants(10), 7: TG.ring_two_pendants(8)}
    for d, G in toys.items():
        json.dump(G, open(os.path.join(g, "hh_d%d.json" % d), "w"))
    os.makedirs(os.path.join(root, "out", "sched"), exist_ok=True)
    open(os.path.join(root, "out", "sched", "slots.txt"), "w").write(slots)
    open(os.path.join(root, "out", "sched", "prune.txt"), "w").write("1")
    py = sys.executable
    c = os.path.join(root, "code")
    subprocess.check_call([py, "-W", "ignore", os.path.join(c, "witness.py"), root, "plan",
                           os.path.join(root, "out", "plan.json")])
    if subset:                    # reduced pipeline test: keep the gate-related and a few other lab tasks
        T = json.load(open(os.path.join(root, "out", "plan.json")))["tasks"]
        def keep(a):
            return a[1] == "19" or (a[2] in ("1.2", "1.6", "3.3", "4.0") and a[3] in ("m_s", "Czz_bar")) or \
                (a[2] == "4.0" and a[3] in ("C2_bar", "Z_bulk", "Z_loop"))
        skip = [t["id"] for t in T if t["args"][0] == "lab" and not keep(t["args"])]
        with open(os.path.join(root, "out", "sched", "skip.txt"), "w") as f:
            for tid in skip:
                f.write(tid + "\n")
    subprocess.check_call([py, "-W", "ignore", os.path.join(c, "sched.py"), root, os.path.join(root, "out", "plan.json"),
                           py])
    os.makedirs(os.path.join(root, "out", "g4"), exist_ok=True)
    lst = subprocess.check_output([py, os.path.join(c, "analyze_map.py"), root, "g4prep"]).decode().split("\n")
    parts = []
    for nn, d in ((57, 5), (115, 7)):
        npz = sorted(set(os.path.join(root, l.split()[1]) for l in lst if l.strip() and l.split()[0] == str(nn)))
        if npz:
            o = os.path.join(root, "out", "g4", "part_%d.json" % nn)
            subprocess.check_call([py, os.path.join(c, "indep_eval.py"), os.path.join(g, "hh_d%d.json" % d), o] + npz,
                                  stdout=subprocess.DEVNULL)
            parts.append(o)
    subprocess.check_call([py, os.path.join(c, "analyze_map.py"), root, "g4check"] + parts)
    subprocess.check_call([py, os.path.join(c, "analyze_map.py"), root, "summary"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], len(sys.argv) > 3 and sys.argv[3] == "subset")
