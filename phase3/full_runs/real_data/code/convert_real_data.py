# real_data / convert_real_data.py  (own code; 2026-11-12)
#
# Turns the public data files of arXiv:2606.15983 (github.com/bjader/quantum-groundstate-learning, pinned commit) into
# plain JSON, so that no later script of this project ever unpickles anything.
#
# Safety. The archive and its .pkl files are UNTRUSTED. Nothing of the repository is imported or executed, and
# pickle.load / pickle.loads are never called on its files. Each data file goes through two barriers:
#   (1) STATIC inspection (pickletools.genops: opcodes are decoded, nothing is built). The file is refused unless every
#       opcode is in SAFE_OPS and every global it names (GLOBAL, or STACK_GLOBAL with its two string arguments resolved
#       statically) is in the whitelist ALLOWED.
#   (2) a RESTRICTED unpickler whose find_class returns only the whitelisted constructors (exact module and name; five
#       numpy constructors and a local re-implementation of dill's array helper) and raises on anything else. This is
#       the barrier that counts; (1) is a pre-check that refuses a file before it reaches (2).
# After loading, every value is checked to be a plain container, a number, a string, or a numeric numpy array.
#
# Output (deterministic: no time stamp inside the data files, so their SHA-256 can be reproduced):
#   <out>/real_n57.json, <out>/real_n115.json : every field of every data file, by group and coupling, with the SHA-256
#                                               of each input member;
#   <out>/lattice_maps.json                   : the two edge lists (cmaps/), parsed as the repository's reader does;
#   <out>/SHA256SUMS.txt                      : SHA-256 of the three outputs;  <out>/conversion_log.json : per-file record.
#
# Run:  python -B -I convert_real_data.py <pinned.tar.gz> <out_dir>
import sys, os, io, re, json, tarfile, hashlib, pickle, pickletools, collections, math
import numpy as np
import numpy._core.multiarray as nm

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
TAR, OUT = sys.argv[1], sys.argv[2]
COMMIT = "6b8866b66d62aaf3ee815cd14fa58e9bf4629d66"
REPO = "github.com/bjader/quantum-groundstate-learning"

# ---------------------------------------------------------------------------------------------- whitelist


def _create_array(f, args, state, npdict=None):
    """Local re-implementation of dill._dill._create_array (dill itself is not imported)."""
    if f is not nm._reconstruct or npdict is not None:
        raise pickle.UnpicklingError("unexpected use of the dill array helper")
    a = f(*args)
    a.__setstate__(state)
    return a


ALLOWED = {
    ("numpy._core.multiarray", "scalar"): nm.scalar,
    ("numpy.core.multiarray", "scalar"): nm.scalar,
    ("numpy._core.multiarray", "_reconstruct"): nm._reconstruct,
    ("numpy.core.multiarray", "_reconstruct"): nm._reconstruct,
    ("numpy", "dtype"): np.dtype,
    ("numpy", "ndarray"): np.ndarray,
    ("dill._dill", "_create_array"): _create_array,
}
SAFE_OPS = {
    "PROTO", "FRAME", "STOP", "MARK", "MEMOIZE", "BINPUT", "LONG_BINPUT", "BINGET", "LONG_BINGET",
    "EMPTY_DICT", "EMPTY_LIST", "EMPTY_TUPLE", "TUPLE", "TUPLE1", "TUPLE2", "TUPLE3",
    "APPEND", "APPENDS", "SETITEM", "SETITEMS",
    "SHORT_BINUNICODE", "BINUNICODE", "BINUNICODE8", "SHORT_BINBYTES", "BINBYTES", "BINBYTES8",
    "SHORT_BINSTRING", "BINSTRING",
    "BINFLOAT", "BININT", "BININT1", "BININT2", "LONG1", "NONE", "NEWTRUE", "NEWFALSE",
    "GLOBAL", "STACK_GLOBAL", "REDUCE", "BUILD",
}
STR_OPS = {"SHORT_BINUNICODE", "BINUNICODE", "BINUNICODE8", "SHORT_BINSTRING", "BINSTRING", "UNICODE", "STRING"}


def static_inspect(b):
    """Decode the opcodes without building anything. Returns (ok, record)."""
    ops = collections.Counter()
    globs = []
    unresolved = 0
    memo = {}
    last_two = [None, None]          # values of the last two "push" events that were strings (else None)
    proto = None
    try:
        for op, arg, pos in pickletools.genops(b):
            name = op.name
            ops[name] += 1
            if name == "PROTO":
                proto = arg
            if name in STR_OPS:
                last_two = [last_two[1], arg]
            elif name == "MEMOIZE":
                memo[len(memo)] = last_two[1]
            elif name in ("BINPUT", "LONG_BINPUT", "PUT"):
                memo[arg] = last_two[1]
            elif name in ("BINGET", "LONG_BINGET", "GET"):
                last_two = [last_two[1], memo.get(arg)]
            elif name == "GLOBAL":
                mod, _, nam = arg.partition(" ")
                globs.append((mod, nam))
                last_two = [None, None]
            elif name == "STACK_GLOBAL":
                mod, nam = last_two
                if isinstance(mod, str) and isinstance(nam, str):
                    globs.append((mod, nam))
                else:
                    unresolved += 1
                last_two = [None, None]
            elif name == "FRAME" or name == "PROTO":
                pass
            else:
                last_two = [last_two[1], None]
    except Exception as ex:                                   # malformed stream: refuse
        return False, {"error": "genops: %r" % (ex,)}
    bad_ops = sorted(set(ops) - SAFE_OPS)
    bad_globs = sorted(set(g for g in globs if g not in ALLOWED))
    ok = (not bad_ops) and (not bad_globs) and unresolved == 0 and ops.get("STOP", 0) == 1
    return ok, {"protocol": proto, "opcodes": dict(sorted(ops.items())), "globals": sorted(set("%s.%s" % g for g in globs)),
                "bad_opcodes": bad_ops, "bad_globals": ["%s.%s" % g for g in bad_globs], "unresolved_stack_globals": unresolved}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in ALLOWED:
            return ALLOWED[(module, name)]
        raise pickle.UnpicklingError("blocked global %s.%s" % (module, name))

    def persistent_load(self, pid):
        raise pickle.UnpicklingError("persistent ids are not allowed")


# ---------------------------------------------------------------------------------------------- to plain JSON
NOTES = collections.Counter()


def describe(v):
    if isinstance(v, np.ndarray):
        return "ndarray %s shape %s" % (v.dtype.str, tuple(int(s) for s in v.shape))
    if isinstance(v, np.generic):
        return "numpy.%s" % type(v).__name__
    if isinstance(v, (list, tuple)):
        inner = sorted(set(describe(x) for x in v)) if len(v) else []
        return "%s len %d of [%s]" % (type(v).__name__, len(v), "; ".join(inner[:3]) + (" ..." if len(inner) > 3 else ""))
    if isinstance(v, dict):
        return "dict keys %s" % sorted(str(k) for k in v)
    return type(v).__name__


def fnum(x):
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        NOTES["nan_or_inf_written_as_null"] += 1
        return None
    return x


def plain(v):
    if v is None or isinstance(v, (bool, str)):
        return v
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return fnum(v)
    if isinstance(v, (complex, np.complexfloating)):
        NOTES["complex_values"] += 1
        return {"re": fnum(v.real), "im": fnum(v.imag)}
    if isinstance(v, np.ndarray):
        if v.dtype.kind in "fiub":
            return plain(v.tolist())
        if v.dtype.kind == "c":
            NOTES["complex_arrays"] += 1
            return {"re": plain(v.real.tolist()), "im": plain(v.imag.tolist())}
        raise TypeError("array of dtype %s is not allowed" % v.dtype)
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            if not isinstance(k, str):
                NOTES["non_string_keys"] += 1
            out[str(k)] = plain(x)
        return out
    raise TypeError("value of type %s is not allowed" % type(v))


def sha256(b):
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------------------------- read the archive
members = {}
with tarfile.open(TAR, "r:gz") as t:
    pax = dict(t.pax_headers)
    for m in t:
        if not m.isfile():
            continue
        rel = "/".join(m.name.split("/")[1:])
        if (rel.startswith("data/") and rel.endswith(".pkl")) or (rel.startswith("cmaps/") and rel.endswith(".txt")):
            members[rel] = t.extractfile(m).read()
assert pax.get("comment") == COMMIT, pax
tar_sha = hashlib.sha256(open(TAR, "rb").read()).hexdigest()
print("archive sha256", tar_sha, "| commit in pax header", pax.get("comment"))
print("data members:", sum(1 for k in members if k.endswith(".pkl")), "| cmaps:", sum(1 for k in members if k.startswith("cmaps/")))

PAT = re.compile(r"^data/spins_(\d+)/(skqd|dmrg)/([^/]+)/XXZ_2d_jz_(\d+\.\d)\.pkl$")
GROUP = {("skqd", "recovery_random_flip"): "skqd_random_flip", ("skqd", "recovery_post_select"): "skqd_post_select"}
data = {57: collections.defaultdict(dict), 115: collections.defaultdict(dict)}
inputs = {57: {}, 115: {}}
log = {"archive_sha256": tar_sha, "commit": COMMIT, "files": {}, "refused": [], "unmatched_members": []}
all_ops = collections.Counter(); all_globs = collections.Counter(); protos = collections.Counter()
for rel in sorted(members):
    if not rel.endswith(".pkl"):
        continue
    mm = PAT.match(rel)
    if not mm:
        log["unmatched_members"].append(rel)
        continue
    n, kind, sub, jz = int(mm.group(1)), mm.group(2), mm.group(3), mm.group(4)
    group = GROUP.get((kind, sub), "dmrg" if kind == "dmrg" else "%s__%s" % (kind, sub))
    b = members[rel]
    ok, rec = static_inspect(b)
    rec.update(sha256=sha256(b), bytes=len(b), group=group, jz=jz, n=n, dmrg_folder=sub if kind == "dmrg" else None)
    log["files"][rel] = rec
    if not ok:
        log["refused"].append(rel)
        print("REFUSED by the static inspection:", rel, rec)
        continue
    all_ops.update(rec["opcodes"]); all_globs.update(rec["globals"]); protos[rec["protocol"]] += 1
    obj = RestrictedUnpickler(io.BytesIO(b)).load()
    if not isinstance(obj, dict):
        raise SystemExit("unexpected top-level type in %s: %s" % (rel, type(obj)))
    rec["fields"] = {str(k): describe(v) for k, v in obj.items()}
    entry = plain(obj)
    entry["_source_member"] = rel
    entry["_source_sha256"] = rec["sha256"]
    if "jz" in obj and abs(float(obj["jz"]) - float(jz)) > 1e-9:
        NOTES["jz_field_differs_from_file_name"] += 1
        rec["jz_field"] = float(obj["jz"])
    if jz in data[n][group]:
        raise SystemExit("two files for the same (n, group, coupling): %s" % rel)
    data[n][group][jz] = entry
    inputs[n][rel] = {"sha256": rec["sha256"], "bytes": rec["bytes"]}

print("pickle protocols:", dict(protos))
print("opcodes over all files:", dict(sorted(all_ops.items())))
print("globals over all files:", dict(sorted(all_globs.items())))
print("refused files:", len(log["refused"]), "| members not matching the name pattern:", log["unmatched_members"])

# ---------------------------------------------------------------------------------------------- lattice maps


def read_edges_txt_bytes(b):
    """Same rule as the repository's qaml/graph/graph_utils.py:read_edges_txt (read as text, re-implemented)."""
    es = set(); n = 0; raw = []
    for line in b.decode("utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        i, j = int(parts[0]), int(parts[1])
        raw.append([i, j])
        if i == j:
            continue
        a, c = (i, j) if i < j else (j, i)
        n = max(n, a, c); es.add((a, c))
    return raw, sorted(es), n + 1


def two_colouring(n, edges):
    adj = collections.defaultdict(list)
    for a, c in edges:
        adj[a].append(c); adj[c].append(a)
    col = {0: 1}; st = [0]                      # node 0 gets colour 1 (as networkx.bipartite.color does for its first node)
    while st:
        u = st.pop()
        for v in adj[u]:
            if v not in col:
                col[v] = 1 - col[u]; st.append(v)
            elif col[v] == col[u]:
                raise SystemExit("edge list is not bipartite")
    assert len(col) == n, "edge list is not connected"
    return [col[i] for i in range(n)]


maps = {"schema": "p5-real-data-lattice-v1", "source": {"repository": REPO, "commit": COMMIT, "archive_sha256": tar_sha}, "maps": {}}
for rel, n_expect in (("cmaps/heavy_hex_edges_d_5.txt", 57), ("cmaps/heavy_hex_edges_d_7.txt", 115)):
    raw, edges, n = read_edges_txt_bytes(members[rel])
    assert n == n_expect, (rel, n)
    col = two_colouring(n, edges)
    deg = [0] * n
    for a, c in edges:
        deg[a] += 1; deg[c] += 1
    maps["maps"][str(n)] = {
        "member": rel, "sha256": sha256(members[rel]), "bytes": len(members[rel]), "n": n,
        "n_lines_with_an_edge": len(raw), "n_unique_edges": len(edges), "edges_file_order": raw, "edges_sorted_unique": edges,
        "colour_with_node0_as_1": col, "class_sizes": {"colour_1_contains_node_0": sum(col), "colour_0": n - sum(col)},
        "degrees": deg,
    }
    print("lattice map %s: n = %d, %d unique edges, colour classes %d (with node 0) / %d" % (rel, n, len(edges), sum(col), n - sum(col)))

# ---------------------------------------------------------------------------------------------- write


def dump(path, obj):
    s = json.dumps(obj, indent=1, sort_keys=True, allow_nan=False, ensure_ascii=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s + "\n")
    return sha256((s + "\n").encode("utf-8"))


os.makedirs(OUT, exist_ok=True)
sums = {}
for n in (57, 115):
    groups = {g: dict(sorted(d.items(), key=lambda kv: float(kv[0]))) for g, d in data[n].items()}
    fields = {}
    for g, d in groups.items():
        pres = collections.defaultdict(list); types = collections.defaultdict(set)
        for jz, e in d.items():
            rec = log["files"][e["_source_member"]]
            for k, desc in rec["fields"].items():
                pres[k].append(jz); types[k].add(desc)
        fields[g] = {k: {"n_couplings": len(v), "couplings": "all %d" % len(d) if len(v) == len(d) else v,
                         "types": sorted(types[k])} for k, v in sorted(pres.items())}
    out = {
        "schema": "p5-real-data-v1",
        "what": "Every field of every public data file of arXiv:2606.15983 for this size, converted to plain JSON "
                "(floats are exact float64 round trips; NaN or infinity would be null). Keys of each group are couplings Jz.",
        "source": {"repository": REPO, "commit": COMMIT, "licence": "Apache-2.0", "archive_sha256": tar_sha,
                   "converter": "real_data/code/convert_real_data.py"},
        "n": n,
        "groups": {g: {"n_couplings": len(d), "couplings": list(d)} for g, d in groups.items()},
        "fields": fields,
        "inputs_sha256": inputs[n],
    }
    out.update(groups)
    name = "real_n%d.json" % n
    sums[name] = dump(os.path.join(OUT, name), out)
    print("\nn = %d:" % n)
    for g, d in groups.items():
        print("  group %-18s couplings %d (%s .. %s)" % (g, len(d), list(d)[0], list(d)[-1]))
        for k, v in fields[g].items():
            print("     %-34s present at %-8s %s" % (k, v["couplings"] if isinstance(v["couplings"], str) else "%d of %d" % (v["n_couplings"], len(d)), "; ".join(v["types"])))
sums["lattice_maps.json"] = dump(os.path.join(OUT, "lattice_maps.json"), maps)
log["notes"] = dict(NOTES)
log["outputs_sha256"] = sums
log["whitelist"] = sorted("%s.%s" % k for k in ALLOWED)
log["python"] = sys.version.split()[0]; log["numpy"] = np.__version__
with open(os.path.join(OUT, "conversion_log.json"), "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(log, indent=1, sort_keys=True) + "\n")
with open(os.path.join(OUT, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
    for k in sorted(sums):
        f.write("%s  %s\n" % (sums[k], k))
print("\nnotes:", dict(NOTES))
print("outputs:", sums)
