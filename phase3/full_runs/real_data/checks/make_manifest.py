# real_data / checks / make_manifest.py   (own code; 2026-11-12; sealing task rd-seal)
#
# The manifest of DECLARATION.md Sec. 11: SHA-256 of every code and test file of the analysis, of the records of gate
# G8, of what was computed before the hash without any real datum, and of the stored code and stored objects that the
# analysis code reads (as they are at hash time).
#
#   python -B -I make_manifest.py            prints the lines for Sec. 11 and writes checks/manifest_at_hash_time.txt
#   python -B -I make_manifest.py --check    recomputes every line of Sec. 11 of ../DECLARATION.md and compares
#
# Paths are relative to real_data/ (stored runs therefore begin with ../). A line
#     <hash>  tree:<folder> [<pattern>,...] (<N> files)
# gives, for the files of that folder (recursively) whose name matches one of the patterns, the SHA-256 of the text
# made of one line "<SHA-256 of the file>  <path relative to the folder, forward slashes>\n" per file, in bytewise
# order of those paths.
#
# This script never opens a file of converted/ or of source/: the lines of Sec. 11 for those files were written by the
# set-up task and are checked by the guard of the analysis code at every read. Standard library only.
import fnmatch
import hashlib
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)                                    # .../phase3/full_runs/real_data
NEVER = ("converted/", "source/")

CODE_DRAFT = ("code/convert_real_data.py", "code/descriptive_checks.py", "code/provenance_check.py")   # already in the draft
G8_RECORDS = ("checks/G8_map_tests_pre_hash.txt", "checks/G8_predict_learn_tests_pre_hash.txt",
              "checks/G8_sets_format_check_pre_hash.txt", "checks/G8_map_tests_by_rd-code-map.txt",
              "checks/G8_predict_learn_tests_by_rd-code-learn.txt", "checks/make_manifest.py")
BEFORE_HASH = ("out/n19/n19_curves.json", "out/n19/n19_labels.json", "out/n19/SHA256SUMS.txt")
REVIEW = "../../../paper/reviews/R10_2026-11-12"
STORED_FILES = (
    "../map/DECLARATION.md", "../map/laptop_analysis/summary_map.json",
    "../map/laptop_analysis/code/analyze_map.py", "../map/laptop_analysis/code/hull.py",
    "../map/laptop_analysis/code/witness.py", "../map/laptop_analysis/code/indep_eval.py",
    "../map/laptop_analysis/code/readings_declared.json",
    "../map/laptop_analysis/code/graphs/hh_d3.json", "../map/laptop_analysis/code/graphs/hh_d5.json",
    "../map/laptop_analysis/code/graphs/hh_d7.json",
    "../method/code/ml2.py", "../method/code/graphs/hh_d3.json", "../method/code/graphs/hh_d5.json",
    "../method/code/graphs/hh_d7.json",
    "../learning_ibm/code/learn_ibm.py", "../learning_ibm/code/prop2_cubic.py", "../bias_law/code/n19b.py",
    "../rigor/DECLARATION_v2.md", "../final_tests/DECLARATION.md",
    REVIEW + "/scratch/math-rigorous-bounds/myverify.py",
)
TREES = (
    ("../map/laptop_analysis/out/states", ("*.json",)),
    ("../map/laptop_analysis/out/chains", ("*.json",)),
    ("../map/laptop_analysis/out/thr", ("*.json",)),
    ("../map/laptop_analysis/out/chk", ("*",)),
    ("../rigor/out_20261031T073328Z", ("*_cert.json", "*_ver.json")),
    ("../rigor/out_20261031T100015Z", ("*_cert.json", "*_ver.json")),
    ("../final_tests", ("*_cert.json", "*_ver.json")),
    ("../map/npz_20261030T022613Z/mps", ("*.npz",)),
)


def full(rel):
    if rel.startswith(NEVER):
        raise SystemExit("this script does not open %s" % rel)
    return os.path.normpath(os.path.join(RD, *rel.split("/")))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tree(rel, patterns):
    root = full(rel)
    if not os.path.isdir(root):
        raise SystemExit("no such folder: %s" % root)
    names = []
    for dp, _, fn in os.walk(root):
        for f in fn:
            if any(fnmatch.fnmatchcase(f, p) for p in patterns):
                names.append(os.path.relpath(os.path.join(dp, f), root).replace("\\", "/"))
    names.sort(key=lambda s: s.encode("utf-8"))
    text = "".join("%s  %s\n" % (sha256_file(os.path.join(root, *n.split("/"))), n) for n in names)
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), len(names)


def tree_line(rel, patterns):
    h, k = tree(rel, patterns)
    return "%s  tree:%s [%s] (%d files)" % (h, rel, ",".join(patterns), k)


def listing(folder, keep):
    return sorted("%s/%s" % (folder, f) for f in os.listdir(full(folder)) if os.path.isfile(os.path.join(full(folder), f)) and keep(f))


def build():
    code = [p for p in listing("code", lambda f: True) if p not in CODE_DRAFT]
    tests = listing("tests", lambda f: f.endswith(".py"))
    groups = [("analysis code of Secs. 2-7 and gates G1-G7 (every other file of code/)", code),
              ("unit tests (every *.py of tests/)", tests),
              ("records of gate G8 and of this manifest", list(G8_RECORDS)),
              ("computed before the hash, no real datum (exact n = 19)", list(BEFORE_HASH)),
              ("stored code imported unchanged and stored inputs, as they are at hash time", list(STORED_FILES))]
    lines = []
    for title, paths in groups:
        lines.append("# " + title)
        for p in paths:
            lines.append("%s  %s" % (sha256_file(full(p)), p))
    lines.append("# stored objects read by the analysis code (tree digests; definition in checks/make_manifest.py)")
    for rel, pats in TREES:
        lines.append(tree_line(rel, pats))
    return lines, len(code), len(tests)


def check():
    with open(os.path.join(RD, "DECLARATION.md"), encoding="utf-8") as f:
        text = f.read()
    a = text.index("\n## 11.")
    b = text.find("\n## 12.", a)
    sec = text[a:b if b > 0 else len(text)]
    n_ok = n_bad = n_skip = 0
    for line in sec.splitlines():
        m = re.match(r"^([0-9a-f]{64})  (.+)$", line)
        if not m:
            continue
        h, what = m.group(1), m.group(2)
        if what.startswith(NEVER):
            n_skip += 1
            print("  not re-hashed here   %s" % what)
            continue
        t = re.match(r"^tree:(\S+) \[([^\]]+)\] \((\d+) files\)$", what)
        if t:
            got, k = tree(t.group(1), tuple(t.group(2).split(",")))
            good = (got == h and k == int(t.group(3)))
        else:
            good = os.path.isfile(full(what)) and sha256_file(full(what)) == h
        n_ok += good
        n_bad += not good
        if not good:
            print("  MISMATCH             %s" % what)
    print("Sec. 11: %d lines equal to the files on disk, %d different, %d not re-hashed here (converted/, source/)" % (n_ok, n_bad, n_skip))
    return 1 if n_bad else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    L, nc, nt = build()
    out = "\n".join(L) + "\n"
    with open(os.path.join(HERE, "manifest_at_hash_time.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    sys.stdout.write(out)
    sys.stderr.write("%d code files (besides the three of the draft), %d test files\n" % (nc, nt))
