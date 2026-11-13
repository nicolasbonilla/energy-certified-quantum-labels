# real_data / tests / test_port_learning.py  (own code; 2026-11-12; task rd-code-learn)
# PORT CHECK of the derived learning files on the stored EMULATED labels (no real datum):
#   1. rd_learn_ibm.py and rd_prop2_cubic.py contain every line of the stored scripts in order, except the "def" lines
#      of the renamed loaders; every stored function has the same syntax tree in the derived file;
#   2. run with --data=emulated they reproduce the stored outputs of learning_ibm/out/ number by number, among them
#      the miss of 3.05 tau, the width of 16.55 tau and zero answers of 14;
#   3. the statements L1-L3 of the declaration, read by rd_f23.f1_rules, hold on the emulated labels (they are the
#      predictions of the emulation-based test).
#     python -B -I test_port_learning.py
import ast
import difflib
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # python -I does not add the script folder
import synth  # noqa: E402
from synth import rdc  # noqa: E402
import rd_f23 as f23  # noqa: E402

C = synth.Checks("test_port_learning")
STORED = os.path.join(rdc.FR, "learning_ibm")
RENAMED = {"learn_ibm.py": {"load": "load_emulated"}, "prop2_cubic.py": {"load": "load_emulated", "intervals": "intervals_emulated"}}


def text(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def functions(src):
    return {n.name: ast.dump(ast.Module(body=n.body, type_ignores=[])) for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}


def constants(src):
    out = {}
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id.isupper():
            try:
                out[n.targets[0].id] = ast.literal_eval(n.value)
            except ValueError:
                pass
    return out


for name, ren in RENAMED.items():
    a, b = text(os.path.join(STORED, "code", name)), text(os.path.join(synth.CODE, "rd_" + name))
    removed = [l[2:] for l in difflib.ndiff(a.split("\n"), b.split("\n")) if l.startswith("- ")]
    C.ok(sorted(removed) == sorted("def %s(%s):" % (k, "n" if k == "load" else "n, D, Dmap, MR") for k in ren),
         "%s: every stored line is in the derived file, in order, except the def lines of the renamed loaders %s" % (name, removed))
    fa, fb = functions(a), functions(b)
    same = [k for k in fa if fa[k] == fb.get(ren.get(k, k))]
    C.ok(len(same) == len(fa), "%s: all %d stored functions have the same syntax tree in the derived file (loaders under their new names)" % (name, len(fa)))
    ca, cb = constants(a), constants(b)
    C.ok(all(cb.get(k) == v for k, v in ca.items()) and ca.get("ALPHA") == 0.1 and ca.get("TAU_REL") == 0.06, "%s: constants unchanged %s" % (name, ca))
    added = [l[2:] for l in difflib.ndiff(a.split("\n"), b.split("\n")) if l.startswith("+ ")]
    code_added = [l for l in added if l.strip() and not l.lstrip().startswith("#") and "# RD" not in l and '"""' not in l and "RD:" not in l
                  and not l.startswith("    upper version") and not l.startswith("    lower version") and not l.startswith("    with E0")]
    C.ok(not code_added, "%s: every added code line carries the mark '# RD' %s" % (name, code_added[:3]))


def same(x, y, path=""):
    """Deep comparison of two JSON trees; timings are ignored. Returns the list of differing paths."""
    if isinstance(x, dict) and isinstance(y, dict):
        d = [path + "/" + k for k in set(x) ^ set(y)]
        for k in set(x) & set(y):
            if k != "secs":
                d += same(x[k], y[k], path + "/" + k)
        return d
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return [path + " (length)"]
        return [p for i, (u, v) in enumerate(zip(x, y)) for p in same(u, v, "%s[%d]" % (path, i))]
    if isinstance(x, float) or isinstance(y, float):
        ok = (x is not None and y is not None and not isinstance(x, (str, bool)) and abs(x - y) <= 1e-12 * max(1.0, abs(x), abs(y)))
        return [] if ok else [path]
    return [] if x == y else [path]


tmp = tempfile.mkdtemp(prefix="rd_port_")
env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
r1 = subprocess.run([sys.executable, "-B", "-I", os.path.join(synth.CODE, "rd_learn_ibm.py"), synth.ROOT, tmp, "--data=emulated",
                     "--models=poly3_invJ,null_nn", "--tag=cheap"], capture_output=True, text=True, env=env)
r2 = subprocess.run([sys.executable, "-B", "-I", os.path.join(synth.CODE, "rd_prop2_cubic.py"), synth.ROOT, tmp, "--data=emulated"],
                    capture_output=True, text=True, env=env)
C.ok(r1.returncode == 0 and r2.returncode == 0, "the derived scripts run on the stored emulated labels (--data=emulated needs no declaration hash)")
new_res, old_res = rdc.rj(os.path.join(tmp, "results_cheap.json")), rdc.rj(os.path.join(STORED, "out", "results_cheap.json"))
new_p2, old_p2 = rdc.rj(os.path.join(tmp, "prop2_cubic.json")), rdc.rj(os.path.join(STORED, "out", "prop2_cubic.json"))
d1, d2 = same(new_res, old_res), same(new_p2, old_p2)
C.ok(not d1, "results_cheap.json: every number equals the stored one (timings apart) %s" % d1[:3])
C.ok(not d2, "prop2_cubic.json: every number equals the stored one %s" % d2[:3])
C.ok(r2.stdout.replace("\r\n", "\n") == text(os.path.join(STORED, "out", "prop2_cubic_stdout.txt")), "prop2_cubic stdout is identical to the stored one")
miss = max(r["miss_ms_over_tau"] for r in new_res["sizes"]["57"]["models"]["poly3_invJ"]["indist_emulated"]["rows"])
wid = min(r["width_b_lo_tau"] for r in new_p2["sizes"]["57"]["indist"])
S = new_p2["sizes"]["57"]["summary"]
C.ok("%.2f" % miss == "3.05", "the miss of the cubic in the training range, up to %.4f tau (stored text: 3.05)" % miss)
C.ok("%.2f" % wid == "16.55", "the narrowest energy-calibrated interval, %.4f tau (stored text: 16.55)" % wid)
C.ok(S["n_answered_rule_c"] == 0 and S["n_queries"] == 14, "rule (c) answers %d of %d couplings (stored text: 0 of 14)" % (S["n_answered_rule_c"], S["n_queries"]))
merged = rdc.rj(os.path.join(STORED, "out", "results.json"))
for n in (57, 115):
    L = f23.f1_rules(merged, old_p2, n)
    C.ok(L["L1"]["holds"] and L["L2"]["holds"] and L["L3"]["holds"] and L["L3"]["one_value"],
         "n = %d, emulated labels: L1 (miss %.2f-%.2f tau), L2 (no test coupling covered), L3 (2q >= %.2f tau at %d couplings) hold" % (
             n, min(L["L1"]["miss_tau"].values()), max(L["L1"]["miss_tau"].values()), min(L["L3"]["width_tau"].values()), L["L3"]["n_couplings"]))

# the run in pieces (rd_learn_parts.py) gives the numbers of the single run: checked on the emulated labels, both cheap models
tmp2 = tempfile.mkdtemp(prefix="rd_parts_")
for model in ("poly3_invJ", "null_nn"):
    codes = []
    for a in ("--part=ood", "--part=0/3", "--part=1/3", "--part=2/3", "--assemble=3"):
        codes.append(subprocess.run([sys.executable, "-B", "-I", os.path.join(synth.CODE, "rd_learn_parts.py"), synth.ROOT, tmp2, "--data=emulated",
                                     "--model=" + model, "--size=57", a], capture_output=True, text=True, env=env).returncode)
    got = rdc.rj(os.path.join(tmp2, "results_%s_n57.json" % model))["sizes"]["57"]
    ref = old_res["sizes"]["57"]
    d3 = same(got["models"][model], ref["models"][model]) + same([got["train"], got["ood"], got["couplings"]], [ref["train"], ref["ood"], ref["couplings"]])
    C.ok(codes == [0] * 5 and not d3, "%s in three pieces plus the test range, assembled: every number equals the stored single run %s" % (model, d3[:3]))
r = subprocess.run([sys.executable, "-B", "-I", os.path.join(synth.CODE, "rd_learn_parts.py"), synth.ROOT, tmp2, "--model=poly3_invJ", "--size=57", "--part=ood"],
                   capture_output=True, text=True, env=env)
C.ok(r.returncode == 3 and "REFUSED" in r.stderr, "rd_learn_parts.py on the real data without a hash is refused (exit %d)" % r.returncode)
C.done()
