# real_data / tests / run_all.py  (own code; 2026-11-12; task rd-code-learn)
# Runs the unit tests of the prediction and learning code (gate G8 of DECLARATION.md) and stores their output.
# No real datum is read.     python -B -I run_all.py        -> tests/out/predict_learn_tests.txt, exit code 0 iff all pass
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = ["test_gate.py", "test_predict.py", "test_learn.py", "test_port_learning.py"]
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
env = dict(os.environ)
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    env.setdefault(v, "2")
lines, bad = [], 0
for t in TESTS:
    t0 = time.time()
    r = subprocess.run([sys.executable, "-B", "-I", os.path.join(HERE, t)], capture_output=True, text=True, env=env)
    bad += r.returncode != 0
    lines.append("##### %s  exit %d  %.0f s\n%s\n%s" % (t, r.returncode, time.time() - t0, r.stdout, ("--- stderr ---\n" + r.stderr) if r.stderr.strip() else ""))
    print("%-24s exit %d  %.0f s  %s" % (t, r.returncode, time.time() - t0, r.stdout.strip().split("\n")[-1]))
with open(os.path.join(HERE, "out", "predict_learn_tests.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print("ALL PASSED" if not bad else "%d TEST FILE(S) FAILED" % bad)
sys.exit(1 if bad else 0)
