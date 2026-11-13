# real_data / tests / run_map_tests.py  (own code; 2026-11-12; task rd-code-map)
#
# Runs the unit tests of the map code (gate G8) and keeps their output:
#   python -B -I run_map_tests.py [--slow]        -> tests/out/map_tests.txt ; exit code 0 iff every test passed
# --slow also re-proves one stored certificate with the independent verifier (gate G5, about ten seconds).
# No test opens a file of converted/ (test_map_synthetic.py records every open() and fails otherwise).
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2")
if "--slow" in sys.argv:
    env["RD_MAP_SLOW"] = "1"
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
ok, text = True, []
for name in ("test_map_stored.py", "test_map_synthetic.py"):
    t0 = time.time()
    p = subprocess.run([sys.executable, "-B", "-I", os.path.join(HERE, name)], capture_output=True, text=True, env=env)
    ok = ok and p.returncode == 0
    text.append("===== %s  (exit code %d, %.1f s) =====\n%s\n%s" % (name, p.returncode, time.time() - t0, p.stdout, p.stderr))
out = "\n".join(text) + "\nALL MAP TESTS PASSED\n" if ok else "\n".join(text) + "\nSOME MAP TESTS FAILED\n"
with open(os.path.join(HERE, "out", "map_tests.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
print(out)
sys.exit(0 if ok else 1)
