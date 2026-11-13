# R11 fix pass (fixer FT, 2026-11-13). Prints, from the stored verification records of the two rigorous runs
# (rigor/out_20261031T073328Z = v1, rigor/out_20261031T100015Z = v2), the number of S^z blocks proved per
# certificate and the size of the largest block, per size and cluster set. It replaces, as the source of the
# numbers printed in Supplemental Sec. S4 (406, 568, 126 x 126, 854 blocks), an internal review report.
# Reads only *_ver.json files; writes nothing. Output: ft_rigor_block_counts_out.txt (stdout).
# usage: python -B -I ft_rigor_block_counts.py > ft_rigor_block_counts_out.txt
import glob, json, os
from collections import defaultdict

RIG = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rigor"))
RUNS = {"v1": "out_20261031T073328Z", "v2": "out_20261031T100015Z"}

shape = defaultdict(set)      # (n, clusters) -> {(n_blocks, max_block)}
count = defaultdict(int)
for tag, folder in RUNS.items():
    for f in sorted(glob.glob(os.path.join(RIG, folder, "out", "jobs", "*_ver.json"))):
        v = json.load(open(f))
        if not v.get("ok"):
            continue
        base = os.path.basename(f)
        n = None
        for tok in base.split("_"):
            if tok.startswith("n") and tok[1:].isdigit():
                n = int(tok[1:]); break
        cl = v.get("task", {}).get("clusters") or ("eball2" if "eball2" in base else "vball2" if "vball2" in base else "?")
        if n is None or "n_blocks" not in v:
            continue
        shape[(n, cl)].add((v["n_blocks"], v.get("max_block")))
        count[(n, cl)] += 1

print("verified certificates of the two rigorous runs: S^z blocks per certificate and largest block, per size and cluster set")
for k in sorted(shape):
    print("  n=%3d %-7s certificates %3d   (blocks per certificate, largest block) = %s" % (k[0], k[1], count[k], sorted(shape[k])))
