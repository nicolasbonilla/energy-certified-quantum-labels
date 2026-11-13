# real_data / f1_neural / run_f1_neural.py   (coordinator, 2026-11-12, after the hashed declaration)
#
# Completes the three pieces of (f1) that the task rd-learn did not compute for cost (RESULTS_learn.md Sec. 3.6):
#   A  pilot perceptron, n = 57, in distribution (45 held-out couplings, real and DMRG labels)
#   B  pilot perceptron, n = 115 (secondary), test range and in distribution
#   C  the dataset paper's architecture 1, n = 57, test range
# It only STARTS the sealed scripts of real_data/code/ (unchanged) with the commands that RESULTS_learn.md gives, and
# writes into real_data/f1_neural/out/ (a new folder): real_data/out/ is not written. No rule, no new number of its own.
#   python -B -I run_f1_neural.py            (run detached; progress in STATUS.json and out/driver_log.txt)
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(RD, "..", "..", ".."))
CODE = os.path.join(RD, "code")
OUT = os.path.join(HERE, "out")
PARTS = os.path.join(OUT, "parts")
H = open(os.path.join(RD, "DECLARATION.sha256")).read().split()[0]
K = 8
ENV = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", PYTHONIOENCODING="utf-8")
LOW = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
T0 = time.time()
STATE = dict(started_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), declaration_sha256=H, k=K, steps=[])


def log(msg):
    line = "%s  %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    with open(os.path.join(OUT, "driver_log.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    STATE["steps"].append(line)
    STATE["elapsed_hours"] = round((time.time() - T0) / 3600, 3)
    with open(os.path.join(HERE, "STATUS.json"), "w", encoding="utf-8") as f:
        json.dump(STATE, f, indent=1)


def start(script, args, logname):
    f = open(os.path.join(OUT, logname), "w")
    cmd = [sys.executable, "-B", "-I", os.path.join(CODE, script), ROOT, OUT, "--data=real", "--hash=" + H] + args
    return subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=ENV, cwd=HERE, creationflags=LOW), f


def wait(procs, what):
    codes = []
    for p, f in procs:
        codes.append(p.wait())
        f.close()
    log("%s: exit codes %s" % (what, codes))
    return all(c == 0 for c in codes)


def perceptron(n, need_ood):
    tag = "mlp%d" % n
    if need_ood:
        if not wait([start("rd_learn_parts.py", ["--model=mlp_pilot3", "--size=%d" % n, "--part=ood"],
                           "stdout_%s_ood.txt" % tag)], "%s test range" % tag):
            return False
    procs = [start("rd_learn_parts.py", ["--model=mlp_pilot3", "--size=%d" % n, "--part=%d/%d" % (i, K)],
                   "stdout_%s_part%dof%d.txt" % (tag, i, K)) for i in range(K)]
    log("%s in distribution: %d processes started" % (tag, K))
    if not wait(procs, "%s in distribution" % tag):
        return False
    return wait([start("rd_learn_parts.py", ["--model=mlp_pilot3", "--size=%d" % n, "--assemble=%d" % K],
                       "stdout_%s_assemble.txt" % tag)], "%s assemble" % tag)


def main():
    os.makedirs(PARTS, exist_ok=True)
    log("driver started; declaration %s; out %s" % (H, OUT))
    src = os.path.join(RD, "out", "learn", "parts", "f1_mlp_pilot3_n57_ood.json")       # computed by rd-learn (kept)
    dst = os.path.join(PARTS, "f1_mlp_pilot3_n57_ood.json")
    if not os.path.isfile(dst):
        shutil.copyfile(src, dst)
        log("copied the stored test-range piece of the perceptron at n = 57")
    arch = start("rd_learn_ibm.py", ["--models=ibm_arch1", "--sizes=57", "--tag=ibm57"], "stdout_ibm57.txt")   # piece C
    log("architecture 1, n = 57, test range: started (one process, many hours)")
    okA = perceptron(57, need_ood=False)                                                 # piece A
    okB = perceptron(115, need_ood=True)                                                 # piece B
    okC = wait([arch], "architecture 1, n = 57")
    STATE["finished"] = True
    STATE["ok"] = dict(A_mlp57=okA, B_mlp115=okB, C_ibm57=okC)
    log("driver finished: %s" % STATE["ok"])


if __name__ == "__main__":
    main()
