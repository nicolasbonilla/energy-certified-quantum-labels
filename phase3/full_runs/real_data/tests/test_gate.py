# real_data / tests / test_gate.py  (own code; 2026-11-12; task rd-code-learn)
# The gate: no script of Secs. 5-7 reads converted/ unless DECLARATION.sha256 exists and matches. No real datum is
# read by this test (the entry points are called with a hash that cannot be the declaration's and must stop before
# opening anything).     python -B -I test_gate.py
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # python -I does not add the script folder
import synth  # noqa: E402
from synth import rdc  # noqa: E402

C = synth.Checks("test_gate")
tmp = tempfile.mkdtemp(prefix="rd_gate_")
with open(os.path.join(tmp, "DECLARATION.md"), "w", newline="\n") as f:
    f.write("declaration under test\n")
sha = rdc.sha256_file(os.path.join(tmp, "DECLARATION.md"))
C.raises(rdc.Refused, lambda: rdc.require_declaration_hash(tmp), "no DECLARATION.sha256: refused")
with open(os.path.join(tmp, "DECLARATION.sha256"), "w") as f:
    f.write("%s *DECLARATION.md\n" % ("0" * 64))
C.raises(rdc.Refused, lambda: rdc.require_declaration_hash(tmp), "a recorded hash that is not the file's: refused")
with open(os.path.join(tmp, "DECLARATION.sha256"), "w") as f:
    f.write("%s *DECLARATION.md\n" % sha)
g = rdc.require_declaration_hash(tmp)
C.ok(isinstance(g, rdc.Gate) and g.sha == sha and rdc.require_declaration_hash(tmp, sha.upper()).sha == sha, "matching hash: the gate opens (argument compared without regard to case)")
C.raises(rdc.Refused, lambda: rdc.require_declaration_hash(tmp, "1" * 64), "a hash argument that is not the declaration's: refused")
with open(os.path.join(tmp, "DECLARATION.md"), "a") as f:
    f.write("edited after the hash\n")
C.raises(rdc.Refused, lambda: rdc.require_declaration_hash(tmp), "a declaration edited after the hash: refused")
C.raises(rdc.Refused, lambda: rdc.read_converted(57, None), "the reader of converted/ needs a gate object")
C.raises(rdc.Refused, lambda: rdc.read_converted(57, sha), "a bare hash string is not a gate object")
try:
    rdc.require_declaration_hash(tmp)
except rdc.Refused as ex:
    C.ok(ex.code == 3, "a refusal ends the process with exit code 3")

# the entry points and the derived scripts, as processes, with a hash that cannot match
fake = "0" * 64
before = {d: os.path.exists(os.path.join(rdc.RD, "out", d)) for d in ("predict", "learn")}
jobs = [("run_predict.py", ["--hash=" + fake]), ("run_predict.py", []), ("run_learn.py", ["--hash=" + fake, "--stage=cheap"]),
        ("run_learn.py", ["--stage=f3"]), ("rd_learn_ibm.py", [synth.ROOT, tmp, "--hash=" + fake, "--models=poly3_invJ"]),
        ("rd_learn_ibm.py", [synth.ROOT, tmp, "--models=poly3_invJ"]), ("rd_prop2_cubic.py", [synth.ROOT, tmp, "--hash=" + fake]),
        ("rd_prop2_cubic.py", [synth.ROOT, tmp])]
for script, args in jobs:
    r = subprocess.run([sys.executable, "-B", "-I", os.path.join(synth.CODE, script)] + args, capture_output=True, text=True)
    C.ok(r.returncode == 3 and "REFUSED" in r.stderr, "%s %s -> exit %d, %s" % (script, " ".join(a for a in args if a.startswith("--")), r.returncode, r.stderr.strip()[:90]))
C.ok(before == {d: os.path.exists(os.path.join(rdc.RD, "out", d)) for d in ("predict", "learn")} and not [f for f in os.listdir(tmp) if f.endswith(".json")],
     "the refused runs wrote nothing")

# static: only rd_common names the converted data files; nothing imports pickle; no downloaded code is imported
mine = ["rd_common.py", "rd_predict.py", "run_predict.py", "rd_f23.py", "run_learn.py", "rd_learn_ibm.py", "rd_prop2_cubic.py", "n19_curves.py", "make_derived.py"]
src = {m: open(os.path.join(synth.CODE, m), encoding="utf-8").read() for m in mine}
code_only = {m: " ".join(l for l in src[m].splitlines() if not l.lstrip().startswith("#")) for m in mine}
C.ok([m for m in mine if "real_n" in code_only[m]] == ["rd_common.py"], "only rd_common.py names the converted data files in its code")
C.ok(not [m for m in mine if re.search(r"^\s*(import|from)\s+(pickle|dill|qaml)", src[m], re.M)], "no script imports pickle, dill or the downloaded package")
C.ok(src["rd_common.py"].count("def read_converted") == 1 and "isinstance(gate, Gate)" in src["rd_common.py"]
     and src["rd_common.py"].count("open(p, \"rb\")") == 1, "the converted files are opened in one place, behind the gate")
C.done()
