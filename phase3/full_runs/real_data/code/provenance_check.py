# real_data / provenance_check.py  (own code; 2026-11-12)
#
# Provenance of the public repository of arXiv:2606.15983 (github.com/bjader/quantum-groundstate-learning).
# The archive is UNTRUSTED: it is never extracted with extractall, nothing in it is executed or imported; members are
# read as bytes. This script
#   1. reads the archive pinned to a commit (downloaded today) and the earlier archive of `main` (first look);
#   2. checks the commit id embedded by GitHub in the pax global header of each archive;
#   3. compares the two archives member by member (path below the top folder, type, SHA-256);
#   4. checks every regular file against the git blob SHA-1 of the GitHub API tree listing of that commit;
#   5. writes MEMBERS.tsv (path, size, sha256, git blob sha1), the upstream licence text and README as text, and every
#      text file of the repository's code as flattened "*.txt" copies (to be READ, never run);
#   6. prints a summary by top-level directory.
#
# Run:  python -B -I provenance_check.py <pinned.tar.gz> <first_look.tar.gz> <tree.json> <out_source_dir>
import sys, os, io, re, json, tarfile, hashlib, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
PINNED, FIRST, TREE, OUT = sys.argv[1:5]
TEXT_EXT = (".py", ".md", ".txt", ".toml", ".cfg", ".yml", ".yaml", ".json", ".ini", ".sh", ".in", ".gitignore")


def read_archive(path):
    """Return (pax global headers, top folder, {relpath: (type, size, sha256, git_sha1, bytes or None)})."""
    out = {}
    tops = set()
    with tarfile.open(path, "r:gz") as t:
        gh = dict(t.pax_headers)
        for m in t:
            parts = m.name.split("/")
            tops.add(parts[0])
            rel = "/".join(parts[1:])
            if m.isdir():
                kind = "dir"
            elif m.isfile():
                kind = "file"
            elif m.issym() or m.islnk():
                kind = "LINK->" + m.linkname
            else:
                kind = "OTHER(%r)" % m.type
            if kind == "file":
                b = t.extractfile(m).read()
                out[rel] = (kind, len(b), hashlib.sha256(b).hexdigest(),
                            hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest(), b, m.mode)
            elif rel:
                out[rel] = (kind, 0, "", "", None, m.mode)
    assert len(tops) == 1, tops
    return gh, tops.pop(), out


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


ghA, topA, A = read_archive(PINNED)
ghB, topB, B = read_archive(FIRST)
print("pinned archive :", os.path.basename(PINNED), "| sha256", sha256_file(PINNED), "| bytes", os.path.getsize(PINNED))
print("   top folder  :", topA, "| pax global header:", ghA)
print("first-look arch:", os.path.basename(FIRST), "| sha256", sha256_file(FIRST), "| bytes", os.path.getsize(FIRST))
print("   top folder  :", topB, "| pax global header:", ghB)

# 3. member-by-member comparison
filesA = {k: v for k, v in A.items() if v[0] == "file"}
filesB = {k: v for k, v in B.items() if v[0] == "file"}
odd = [(k, v[0]) for k, v in list(A.items()) + list(B.items()) if v[0] not in ("file", "dir")]
print("\nmembers: pinned %d files / %d entries; first-look %d files / %d entries" % (len(filesA), len(A), len(filesB), len(B)))
print("non-regular members (links, devices ...):", odd if odd else "none")
onlyA = sorted(set(filesA) - set(filesB)); onlyB = sorted(set(filesB) - set(filesA))
diff = sorted(k for k in set(filesA) & set(filesB) if filesA[k][2] != filesB[k][2])
print("files only in pinned:", onlyA if onlyA else "none")
print("files only in first-look:", onlyB if onlyB else "none")
print("files with different content:", diff if diff else "none")
print("ARCHIVES IDENTICAL IN CONTENT:", (not onlyA) and (not onlyB) and (not diff))
bad_names = [k for k in A if k.startswith("/") or ".." in k.split("/") or "\\" in k or ":" in k]
print("member names that are absolute or climb out of the folder:", bad_names if bad_names else "none")

# 4. against the git tree of the API (blob sha1)
tree = json.load(open(TREE, encoding="utf-8"))
print("\nAPI tree: sha", tree.get("sha"), "| truncated:", tree.get("truncated"), "| entries", len(tree.get("tree", [])))
blobs = {e["path"]: e for e in tree["tree"] if e["type"] == "blob"}
miss_api = sorted(set(filesA) - set(blobs)); miss_tar = sorted(set(blobs) - set(filesA))
bad_sha = sorted(k for k in set(filesA) & set(blobs) if filesA[k][3] != blobs[k]["sha"])
bad_size = sorted(k for k in set(filesA) & set(blobs) if filesA[k][1] != blobs[k].get("size"))
print("files in the archive missing from the API tree:", miss_api if miss_api else "none")
print("blobs of the API tree missing from the archive:", miss_tar if miss_tar else "none")
print("git blob SHA-1 mismatches:", bad_sha if bad_sha else "none", "| size mismatches:", bad_size if bad_size else "none")
print("EVERY FILE EQUALS THE GIT BLOB OF THE COMMIT TREE:", not (miss_api or miss_tar or bad_sha or bad_size),
      "(%d files)" % len(filesA))
modes = collections.Counter(e["mode"] for e in tree["tree"])
print("git modes in the tree:", dict(modes))

# 5. durable listings and text copies
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "MEMBERS.tsv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("path\tbytes\tsha256\tgit_blob_sha1\ttar_mode\n")
    for k in sorted(filesA):
        v = filesA[k]
        f.write("%s\t%d\t%s\t%s\t%o\n" % (k, v[1], v[2], v[3], v[5]))
txt_dir = os.path.join(OUT, "code_as_text")
os.makedirs(txt_dir, exist_ok=True)
n_txt = 0
for k in sorted(filesA):
    low = k.lower()
    base = low.rsplit("/", 1)[-1]
    is_text = low.endswith(TEXT_EXT) or base in ("license", "readme", "makefile", "dockerfile")
    if low.startswith("data/") and low.endswith(".pkl"):
        continue
    if not is_text:
        continue
    safe = re.sub(r"[^A-Za-z0-9_.\-]", "_", k.replace("/", "__")) + ".txt"
    with open(os.path.join(txt_dir, safe), "wb") as f:
        f.write(filesA[k][4])
    n_txt += 1
for name in ("LICENSE", "LICENSE.txt", "LICENSE.md"):
    if name in filesA:
        with open(os.path.join(OUT, "LICENSE_upstream.txt"), "wb") as f:
            f.write(filesA[name][4])
        print("\nlicence file:", name, "| bytes", filesA[name][1], "| sha256", filesA[name][2])
        print("   first line:", filesA[name][4].decode("utf-8", "replace").strip().splitlines()[0].strip())
print("text copies written to code_as_text/:", n_txt)

# 6. summary by directory and extension
by = collections.Counter(); size = collections.Counter()
for k, v in filesA.items():
    parts = k.split("/")
    key = "/".join(parts[:3]) if parts[0] == "data" and len(parts) > 3 else ("/".join(parts[:2]) if len(parts) > 2 else (parts[0] if len(parts) > 1 else "."))
    ext = os.path.splitext(k)[1] or "(none)"
    by[(key, ext)] += 1; size[(key, ext)] += v[1]
print("\nfiles by folder and extension (count, bytes):")
for (key, ext), c in sorted(by.items()):
    print("   %-52s %-8s %4d %9d" % (key, ext, c, size[(key, ext)]))
other = sorted(k for k in filesA if not (k.startswith("data/") and k.endswith(".pkl")) and not k.lower().endswith(TEXT_EXT)
               and k.rsplit("/", 1)[-1].lower() not in ("license", "readme", "makefile", "dockerfile"))
print("\nfiles that are neither data pickles nor text (not copied as text):")
for k in other:
    print("   %s (%d bytes)" % (k, filesA[k][1]))
