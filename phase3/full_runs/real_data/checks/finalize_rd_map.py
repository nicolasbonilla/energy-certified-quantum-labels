# real_data / checks / finalize_rd_map.py   (own code of the task rd-map; 2026-11-12; written AFTER the hash)
#
# Closing steps of the task rd-map. It computes no result of the declaration.
#   1. Post hoc consistency check: the labels of the two explicit witness mixtures of a row lie in W(E_real, M_real), so
#      they must lie inside the exact interval I of the same row (explicit DMRG states against exact-arithmetic bounds).
#   2. Confirms that every file of code/ and tests/ listed in Sec. 11 of the declaration still has its listed SHA-256.
#   3. Appends the section of this task to DEVIATIONS.md (never overwrites; run once: a second run would append again,
#      so it refuses if the section is already there).
#   4. Writes results/SHA256SUMS_rd-map.txt.
# It opens neither converted/ nor source/.
#
#   python -B -I finalize_rd_map.py
import hashlib
import io
import json
import os
import re
import sys

sys.dont_write_bytecode = True
RD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = "## 2026-11-12, task `rd-map`"


def sha(p):
    with open(os.path.join(RD, p), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# 1. witness intervals inside the exact intervals
rows = json.load(open(os.path.join(RD, "out", "map_rows.json"), encoding="utf-8"))["rows"]
n, bad, slack = 0, [], []
for r in rows:
    ex, lw = r.get("exact"), r.get("lower")
    if ex and ex.get("exists") and lw and lw.get("witness"):
        n += 1
        a, b = lw["witness"]
        slack.append(min(a - ex["lo"], ex["hi"] - b))
        if not (ex["lo"] <= a and b <= ex["hi"]):
            bad.append((r["n"], r["key"], r["label"], ex["lo"], a, b, ex["hi"]))
txt = ("Post hoc consistency check (task rd-map, 2026-11-12). The labels of the two explicit witness mixtures of a row lie in\n"
       "W(E_real, M_real), so they must lie inside the exact interval I of the same row (two independent sides of Sec. 2 of the\n"
       "declaration: explicit DMRG states against exact-arithmetic bounds).\n"
       "rows with both an exact interval and a witness interval: %d\nviolations: %d %s\n"
       "smallest distance of a witness end to the corresponding end of I: %.6f\n" % (n, len(bad), bad, min(slack)))
with io.open(os.path.join(RD, "checks", "consistency_witness_inside_exact.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(txt)
print(txt)

# 2. sealed code unchanged
decl = io.open(os.path.join(RD, "DECLARATION.md"), encoding="utf-8").read()
man = dict((m.group(2), m.group(1)) for m in re.finditer(r"^([0-9a-f]{64})  ((?:code|tests)/\S+)$", decl, re.M))
changed = [p for p, h in sorted(man.items()) if sha(p) != h]
print("files of code/ and tests/ listed in Sec. 11: %d; changed since the hash: %s" % (len(man), changed or "none"))
assert len(man) >= 30 and not changed

# 3. DEVIATIONS.md
own = ["checks/spotcheck_exact_intervals.py", "checks/g6_supplement.py", "checks/finalize_rd_map.py", "results/make_results_map.py"]
six = ["code/map_common.py", "code/map_certs.py", "code/map_stored.py", "code/map_tables.py", "code/map_gates.py", "code/run_map.py"]
p = os.path.join(RD, "DEVIATIONS.md")
old = io.open(p, encoding="utf-8").read() if os.path.exists(p) else ""
if TAG in old:
    print("DEVIATIONS.md already holds the section of rd-map: nothing appended")
else:
    sec = []
    if not old.strip():
        sec.append("# real_data: DEVIATIONS\n\nDated notes on anything learned or done after the hash of `DECLARATION.md` (SHA-256\n`%s`, hashed 2026-11-12T19:22:32Z).\n"
                   "No rule of the declaration is changed by anything below.\n" % sha("DECLARATION.md"))
    sec.append("""
%s (the map on the real data: Secs. 2, 3, 4, 6 and gates G1-G7)

The declaration hash was checked against `DECLARATION.sha256` before anything was read. The sealed code ran once, from
2026-11-12T19:28:57Z to 19:31:01Z UTC (`out/run_map_stdout.txt`), with its default options.

1. **No sealed file was changed; no defect that needed a fix was found.** Old SHA-256 = new SHA-256 for every file of `code/` and
   `tests/` listed in Sec. 11 of the declaration (%d files, hashed again after the run). The six files of the map:
%s
2. **Gate G1 is NOT COMPLETE (no rule changed).** The gate as declared is the re-run of `code/convert_real_data.py` on the pinned
   archive. That converter passes every data file through a static inspection and then a restricted unpickler (whitelisted
   constructors only). The task `rd-map` was instructed to unpickle nothing, so `--g1-rerun` was not used. Checked instead: the
   SHA-256 of the three converted files against `converted/SHA256SUMS.txt` and Sec. 11, and of the archive against its pinned value
   (`13aa8e69...dedbb91`); all equal. To complete G1, a task that is allowed to run the converter runs
   `python -B -I code/run_map.py --g1-rerun --out <new folder>` (or the converter alone into a scratch folder) and compares the
   three hashes.
3. **Gate G6, first part, is NOT COMPLETE, with nothing checked.** The declared selection (22 NOT CERTIFIED rows within 0.3 of a J*,
   10 rows drawn with the seed 1845216616) has 150 witness components; none has its tensors on the laptop (the six tensor files are
   states of n = 57, Jz = 1.6), and Sec. 9 of the declaration excludes cloud access. The sealed summary line reads "pass on what could
   be checked; not complete"; since nothing was checked, the results report it as NOT COMPLETE only. 280 of the 439 NOT CERTIFIED rows
   use an energy re-evaluated at another coupling and carry the mark; the other 159 do not. The second part of G6 passed (472 rows,
   smallest margin above E0: 9.8e-6). Post hoc supplement, not the gate (`checks/g6_supplement.py`): the 4 (row, component) pairs with
   tensors among all NOT CERTIFIED rows (m_s, n = 57, Jz = 1.5, 1.6, 1.6, 1.7) and the six tensor states at Jz = 1.5 and 1.7 agree
   with the linear rule to 1.6e-13.
4. **Extension E1 was not available when the map ran** (`real_data/e1/` held no certificate at 19:31Z). The results have no E1
   column. Caution for the task that adds it: with certificates in `e1/` the sealed code adds the key `secondary_E1` to
   `S_sets.json`, so the SHA-256 of that file would differ from the one already fixed
   (`%s`), and the code refuses to overwrite it. Run the E1 column with
   another `--out` folder; S, S_3/4, S_1/2 and S_p do not depend on E1 by construction.
5. **Output name.** The sealed code writes the 700 rows to `out/map_rows.json`. The file asked of this task, `out/map_real.json`, is
   built from it by `results/make_results_map.py` (copy, and outward rounding for display in `results/RESULTS_map.md`; no status,
   interval or threshold is recomputed).
6. **Files added after the hash by this task** (own code; none is imported by the sealed code; none changes a rule):
%s
7. **Things noticed in the sealed code and left as they are** (they change no number of this run): (a) `map_gates.g6_linear` returns
   `pass = True` when no component could be checked (item 3); (b) `map_tables.write_s_sets` changes the content of `S_sets.json`
   when E1 certificates exist (item 4).
8. **A like-for-like count that differs from item F9 of the declaration, for a stated reason.** At n = 115 the like-for-like filter
   keeps 30 m_s labels (J*_s = 3.1), because the interpolated thresholds also pass Jz = 3.1 and 3.2; item F9 had counted 28 from
   Jz = 3.3, at the couplings of the stored map only. Both are like-for-like numbers under the sector hypothesis; neither is a
   property of the real labels.
9. **Post hoc checks added by this task (not declared; they decide nothing):** the independent recomputation of the 200 exact rows
   (`checks/spotcheck_exact_intervals.py`: 200 of 200 identical as exact rationals); the containment of every explicit witness
   interval in the exact interval of its row (`checks/consistency_witness_inside_exact.txt`: %d rows, %d violations).
""" % (TAG, len(man), "\n".join("   - `%s`  `%s` (unchanged)" % (f, sha(f)) for f in six), sha("out/S_sets.json"),
       "\n".join("   - `%s`  `%s`" % (f, sha(f)) for f in own), n, len(bad)))
    with io.open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write("".join(sec))
    print("DEVIATIONS.md: section of rd-map appended")

# 4. hashes
files = ["DECLARATION.md", "DEVIATIONS.md", "out/S_sets.json", "out/S_sets.sha256", "out/map_real.json", "out/map_rows.json",
         "out/map_summary.json", "out/map_secondary.json", "out/map_gates.json", "out/map_tables.md", "out/SHA256SUMS_map.txt",
         "out/run_map_stdout.txt", "out/run_map_stderr.txt", "results/RESULTS_map.md", "results/make_results_map.py",
         "checks/spotcheck_exact_intervals.py", "checks/spotcheck_exact_intervals.json", "checks/spotcheck_exact_intervals_stdout.txt",
         "checks/g6_supplement.py", "checks/g6_supplement.json", "checks/g6_supplement_stdout.txt",
         "checks/consistency_witness_inside_exact.txt", "checks/finalize_rd_map.py"]
files += sorted("out/g5/" + x for x in os.listdir(os.path.join(RD, "out", "g5")))
with io.open(os.path.join(RD, "results", "SHA256SUMS_rd-map.txt"), "w", encoding="utf-8", newline="\n") as f:
    for x in files:
        f.write("%s  %s\n" % (sha(x), x))
print("results/SHA256SUMS_rd-map.txt: %d files" % len(files))
for x in ("out/S_sets.json", "out/map_real.json", "results/RESULTS_map.md", "DEVIATIONS.md"):
    print(sha(x), x)
print("--- out/SHA256SUMS_map.txt (written by the sealed code), checked now:")
for line in io.open(os.path.join(RD, "out", "SHA256SUMS_map.txt"), encoding="utf-8"):
    h, name = line.split()
    print("  %s  %s  %s" % (h, name, "ok" if sha("out/" + name) == h else "DIFFERS"))
