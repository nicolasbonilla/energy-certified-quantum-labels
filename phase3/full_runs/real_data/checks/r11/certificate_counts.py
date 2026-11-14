"""certificate_counts.py -- how many certificate files the one-command check verifies, and how many are distinct.

    python -B -I certificate_counts.py [root of the package]

Reads the stored record of the run of 2026-11-13 (package_checks_certificates_all_2026-11-13.txt, next to this
script): it has one PASS line per certificate file. A certificate is named after the bound it proves, so two files
with the same name prove the same bound. If docs/CERTIFICATES.tsv and docs/MANIFEST.tsv are found under the root
(they exist in the built package), the files that share a name are also compared by their SHA-256.
Prints counts only; verifies no certificate (run_checks.py does that).
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = os.path.join(HERE, "package_checks_certificates_all_2026-11-13.txt")


def find_root():
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])
    d = HERE
    for _ in range(8):
        if os.path.isfile(os.path.join(d, "docs", "CERTIFICATES.tsv")):
            return d
        d = os.path.dirname(d)
    return None


def main():
    rec = open(RECORD, encoding="utf-8").read()
    names = re.findall(r"^\[PASS\] certificates (\S+):", rec, flags=re.M)
    fails = len(re.findall(r"^\[FAIL\] certificates ", rec, flags=re.M))
    count = collections.Counter(names)
    twice = sorted(n for n, v in count.items() if v == 2)
    more = sorted(n for n, v in count.items() if v > 2)
    print("record: package_checks_certificates_all_2026-11-13.txt")
    print("certificate files verified (PASS lines): %d ; FAIL lines: %d" % (len(names), fails))
    print("distinct certificates (distinct names, one per bound): %d distinct" % len(count))
    print("certificates stored as two files: %d ; as more than two: %d" % (len(twice), len(more)))
    print("check: %d distinct + %d second files = %d files" % (len(count), len(twice), len(count) + len(twice)))
    root = find_root()
    cert_tsv = os.path.join(root, "docs", "CERTIFICATES.tsv") if root else None
    man_tsv = os.path.join(root, "docs", "MANIFEST.tsv") if root else None
    if not (root and os.path.isfile(cert_tsv) and os.path.isfile(man_tsv)):
        print("docs/CERTIFICATES.tsv and docs/MANIFEST.tsv not found: the files are not compared by checksum here")
        return 0
    sha = {}
    for line in open(man_tsv, encoding="utf-8").read().split("\n")[1:]:
        if line:
            p, _, h = line.split("\t")
            sha[p] = h
    files = [l.strip() for l in open(cert_tsv, encoding="utf-8").read().split("\n")[1:] if l.strip()]
    by = collections.defaultdict(list)
    for f in files:
        by[os.path.basename(f)[:-len("_cert.json")]].append(f)
    print("package list docs/CERTIFICATES.tsv: %d files, %d distinct names, %d distinct SHA-256"
          % (len(files), len(by), len(set(sha[f] for f in files))))
    same = diff = 0
    pairs = collections.Counter()
    for n, lst in sorted(by.items()):
        if len(lst) > 1:
            if len(set(sha[f] for f in lst)) == 1:
                same += 1
                kind = "identical copies"
            else:
                diff += 1
                kind = "the same bound from two runs (different files)"
            pairs[(" + ".join(sorted(os.path.dirname(f) for f in lst)), kind)] += 1
    print("of the certificates stored as two files: %d are identical copies (same SHA-256), %d are the same bound"
          " computed in two runs (different files)" % (same, diff))
    for (folders, kind), v in sorted(pairs.items(), key=lambda kv: -kv[1]):
        print("  %3d  %s: %s" % (v, kind, folders))
    return 0


if __name__ == "__main__":
    sys.exit(main())
