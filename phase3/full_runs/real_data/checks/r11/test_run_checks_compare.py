r"""test_compare.py -- tests of the comparison of run_checks.py on copies of real stored outputs.
  python -B -I test_compare.py <path of run_checks.py> <path of the package>
Each case builds a changed copy of a stored output in a temporary folder and calls compare(); the expected verdict is
stated next to the case. Nothing of the package is written.
"""
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

RC, PKG = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("rc", RC)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

RD = os.path.join(PKG, "phase3", "full_runs", "real_data")
CASES = []
FAILS = []


def walk(x, f_float=None, state=None):
    if isinstance(x, bool) or x is None:
        return x
    if isinstance(x, float):
        return f_float(x, state) if f_float else x
    if isinstance(x, list):
        return [walk(v, f_float, state) for v in x]
    if isinstance(x, dict):
        return {k: walk(v, f_float, state) for k, v in x.items()}
    return x


def first_path(x, want, path=()):
    """path of the first entry of the wanted type (deep), or None"""
    if isinstance(x, want) and not isinstance(x, bool):
        return path
    if isinstance(x, dict):
        for k, v in x.items():
            p = first_path(v, want, path + (k,))
            if p is not None:
                return p
    if isinstance(x, list):
        for i, v in enumerate(x):
            p = first_path(v, want, path + (i,))
            if p is not None:
                return p
    return None


def set_path(x, path, f):
    cur = x
    for k in path[:-1]:
        cur = cur[k]
    cur[path[-1]] = f(cur[path[-1]])


def run_case(label, stored_dir, name, make, expect_pass, expect_words, loose=()):
    tmp = tempfile.mkdtemp(prefix="cmp_")
    try:
        src = os.path.join(stored_dir, name)
        raw = open(src, "rb").read()
        new = make(raw)
        open(os.path.join(tmp, name), "wb").write(new)
        rc.RESULTS.clear()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ok = rc.compare("test", tmp, stored_dir, [name], loose=loose)
        line = buf.getvalue().strip()
        good = (ok == expect_pass) and all(w in line for w in expect_words)
        CASES.append((label, good))
        if not good:
            FAILS.append((label, line))
        print("%s  %-58s -> %s" % ("ok " if good else "BAD", label, line[:150]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def json_edit(f):
    def make(raw):
        crlf = b"\r\n" in raw
        d = json.loads(raw.decode("utf-8"))
        d = f(d)
        s = json.dumps(d, indent=1)
        return s.replace("\n", "\r\n").encode("utf-8") if crlf else s.encode("utf-8")
    return make


def scale_floats(eps):
    return lambda d: walk(d, lambda v, st: v * (1.0 + eps) if v == v and abs(v) < 1e300 else v)


def one_float(eps):
    def f(d):
        p = first_path(d, float)
        set_path(d, p, lambda v: v * (1.0 + eps) if v != 0 else eps)
        return d
    return f


def one_int(d):
    p = first_path(d, int)
    set_path(d, p, lambda v: v + 1)
    return d


def one_str(d):
    p = first_path(d, str)
    set_path(d, p, lambda v: v + "x")
    return d


def drop_key(d):
    k = sorted(d.keys())[-1]
    del d[k]
    return d


def flip_hash(d):
    """change one hexadecimal digit inside the first checksum-like string"""
    done = [False]

    def g(x):
        if isinstance(x, str) and re.fullmatch(r"[0-9a-f]{64}", x) and not done[0]:
            done[0] = True
            c = "0" if x[10] != "0" else "1"
            return x[:10] + c + x[11:]
        if isinstance(x, list):
            return [g(v) for v in x]
        if isinstance(x, dict):
            return {k: g(v) for k, v in x.items()}
        return x
    out = g(d)
    if not done[0]:
        raise KeyError("no checksum string")
    return out


FILES = [
    (os.path.join(RD, "out", "predict"), "predict_results.json", ()),
    (os.path.join(RD, "out", "learn"), "f2_floor.json", ()),
    (os.path.join(RD, "out", "learn"), "f1_rules.json", ()),
    (os.path.join(RD, "out", "learn"), "results_cheap.json", ("results_cheap.json",)),
    (os.path.join(RD, "e1", "map_e1"), "map_summary.json", ()),
    (os.path.join(RD, "e1", "map_e1"), "map_gates.json", ("map_gates.json",)),
    (os.path.join(RD, "e1", "map_e1"), "S_sets.json", ()),
]
for d, n, loose in FILES:
    run_case("%s: identical copy" % n, d, n, lambda raw: raw, True, ["SHA-256 equal"], loose)
    run_case("%s: other line endings" % n, d, n,
             lambda raw: raw.replace(b"\r\n", b"\n") if b"\r\n" in raw else raw.replace(b"\n", b"\r\n"),
             True, ["apart from line endings"], loose)
    run_case("%s: same entries, other spacing" % n, d, n,
             lambda raw: json.dumps(json.loads(raw.decode("utf-8")), indent=3).encode("utf-8"),
             True, ["apart from recorded run times"] if loose else ["differ only in how the same"], loose)
    has_float = first_path(json.loads(open(os.path.join(d, n), "rb").read().decode("utf-8")), float) is not None
    if has_float:
        run_case("%s: every decimal number times (1 + 3e-13)" % n, d, n, json_edit(scale_floats(3e-13)), True,
                 ["NOT byte for byte", "entry by entry"], loose)
        run_case("%s: one decimal number off by 1e-6" % n, d, n, json_edit(one_float(1e-6)), False, ["DIFFERS"], loose)
    parsed = json.loads(open(os.path.join(d, n), "rb").read().decode("utf-8"))
    if first_path(parsed, int) is not None:
        run_case("%s: one integer plus one" % n, d, n, json_edit(one_int), False, ["DIFFERS"], loose)
    if first_path(parsed, str) is not None:
        run_case("%s: one word changed" % n, d, n, json_edit(one_str), False, ["DIFFERS"], loose)
    run_case("%s: one key removed" % n, d, n, json_edit(drop_key), False, ["DIFFERS"], loose)
    try:
        flip_hash(json.loads(open(os.path.join(d, n), "rb").read().decode("utf-8")))
        run_case("%s: one digit of a checksum changed" % n, d, n, json_edit(flip_hash), False, ["DIFFERS"], loose)
    except KeyError:
        pass

# the text table of the map
d, n = os.path.join(RD, "e1", "map_e1"), "map_tables.md"
txt = open(os.path.join(d, n), "rb").read().decode("utf-8")
floats = list(rc.FLOAT_RX.finditer(txt))
print("map_tables.md: %d decimal numbers found by the pattern" % len(floats))
m = floats[len(floats) // 2]


def md_last_digit(raw):
    t = raw.decode("utf-8")
    s = m.group(0)
    v = float(s)
    new = repr(v * (1 + 2e-12)) if "e" not in s.lower() else s
    return (t[:m.start()] + new + t[m.end():]).encode("utf-8")


def md_big(raw):
    t = raw.decode("utf-8")
    v = float(m.group(0))
    return (t[:m.start()] + repr(v * 1.001 if v else 0.001) + t[m.end():]).encode("utf-8")


def md_int(raw):
    t = raw.decode("utf-8")
    k = re.search(r"(?<![\w.])\d+(?![\w.])", t)
    return (t[:k.start()] + str(int(k.group(0)) + 1) + t[k.end():]).encode("utf-8")


def md_word(raw):
    t = raw.decode("utf-8")
    k = re.search(r"[A-Za-z]{5,}", t)
    return (t[:k.start()] + k.group(0)[::-1] + "q" + t[k.end():]).encode("utf-8")


run_case("map_tables.md: identical copy", d, n, lambda raw: raw, True, ["SHA-256 equal"])
run_case("map_tables.md: other line endings", d, n, lambda raw: raw.replace(b"\n", b"\r\n"), True, ["apart from line endings"])
run_case("map_tables.md: one decimal number, last digits", d, n, md_last_digit, True, ["NOT byte for byte"])
run_case("map_tables.md: one decimal number off by 1e-3", d, n, md_big, False, ["DIFFERS"])
run_case("map_tables.md: one integer plus one", d, n, md_int, False, ["DIFFERS"])
run_case("map_tables.md: one word changed", d, n, md_word, False, ["DIFFERS"])

# the pattern must not read parts of names, checksums or identifiers as decimal numbers
for s, want in (("n57_J1.6_m_s_m_l0.066484", 0), ("13aa8e69c9bc614c72c5", 0), ("v1.2.3", 0), ("x = 0.25, y = -1.5e-3", 2),
                ("file_2.5.json", 0), ("(3.14)", 1), ("1e5", 1), ("abc1e5", 0), ("12", 0), ("0.5-0.7", 1), ("[0.5, 0.7]", 2)):
    got = len(rc.FLOAT_RX.findall(s))
    good = got == want
    CASES.append(("pattern on %r" % s, good))
    if not good:
        FAILS.append(("pattern on %r" % s, "found %d, wanted %d: %s" % (got, want, rc.FLOAT_RX.findall(s))))
    print("%s  pattern on %-28r -> %d decimal numbers %s" % ("ok " if good else "BAD", s, got, rc.FLOAT_RX.findall(s)))

print("\n%d cases, %d as expected, %d not" % (len(CASES), sum(1 for _, g in CASES if g), len(FAILS)))
for label, line in FAILS:
    print("NOT AS EXPECTED:", label, "|", line[:300])
sys.exit(1 if FAILS else 0)
