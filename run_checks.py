"""run_checks.py -- re-run, on a laptop, the checks of this package that need no cloud machine.

    python run_checks.py                      all steps below, in this order
    python run_checks.py numbers              the guardian paper/check_numbers.py on both documents (expected: 0 MISSING)
    python run_checks.py certificates         exact verification of a sample of 5 certificates
                                              (--sample N, --all, --verifier independent|stored)
    python run_checks.py map                  the declared map code on the public data, into a temporary folder, compared
                                              with the stored outputs by SHA-256 (--no-reprove skips the exact re-proofs)
    python run_checks.py bias                 the declared tests of the bias on the public labels, compared
    python run_checks.py learning             the cheap stage of the learning tests (cubic model, floor, 200 splits), compared
    python run_checks.py pdf                  pdflatex + bibtex of main.tex, supplement.tex and tables.tex (--in-place)

Options: --tmp DIR (work folder; default: a new folder in the system temporary folder, removed at the end unless --keep),
         --keep, --threads N (default 2), --python EXE (default: the interpreter that runs this file).

How a re-computed output is compared with the stored one: byte for byte (SHA-256). If the bytes differ, entry by
entry: integers, words and structure must be identical and decimal numbers must agree to a relative 1e-9. Such a
file is reported as passed WITH that note and counted on its own line of the summary: another processor or
numerical library changes the last digits of a floating-point result. On the machine where the package was built
every output is reproduced byte for byte.

Works on Windows, Linux and macOS: only Python is needed for the first five steps (numpy for `certificates`, `map`,
`bias` and `learning`; see requirements.txt), and pdflatex + bibtex for `pdf`. Nothing is downloaded, nothing of the
dataset's repository is executed, no pickle is opened. Apart from paper/check_numbers_output.txt (rewritten with the
same content by the guardian) the steps write only into the temporary folder, unless --in-place is given.
Exit code 0 if every step that ran passed.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(ROOT, "paper")
RUNS = os.path.join(ROOT, "phase3", "full_runs")
RD = os.path.join(RUNS, "real_data")
MYVERIFY = os.path.join(PAPER, "reviews", "R10_2026-11-12", "scratch", "math-rigorous-bounds", "myverify.py")
VERIFY_STORED = os.path.join(RUNS, "rigor", "code", "verify_exact.py")
GRAPH_DIRS = [os.path.join(RUNS, "map", "laptop_analysis", "code", "graphs"), os.path.join(RUNS, "rigor", "code", "graphs")]
STEPS = ["numbers", "certificates", "map", "bias", "learning", "pdf"]
RESULTS = []


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def report(step, ok, detail):
    RESULTS.append((step, ok, detail))
    print("[%s] %-12s %s" % ("PASS" if ok else "FAIL", step, detail), flush=True)


def run(cmd, cwd, env, timeout=7200):
    t = time.time()
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return p, time.time() - t


def read_sums(path):
    out = {}
    for line in read(path).splitlines():
        m = re.match(r"([0-9a-f]{64})\s+\*?(.+)$", line.strip())
        if m:
            out[m.group(2).strip()] = m.group(1)
    return out


def declaration_hash():
    return read(os.path.join(RD, "DECLARATION.sha256")).split()[0]


# -------------------------------------------------------------------------------------------------------- numbers
def step_numbers(a, env, tmp):
    exp = {}
    p = os.path.join(ROOT, "docs", "EXPECTED.json")
    if os.path.isfile(p):
        exp = json.load(open(p, encoding="utf-8")).get("guardian", {})
    for doc in ("supplement.tex", "main.tex"):               # main last: check_numbers_output.txt is the main report
        r, dt = run([a.python, "-B", "-I", "check_numbers.py", doc], PAPER, env)
        rep = os.path.join(PAPER, "check_numbers_output.txt")
        if r.returncode != 0 or not os.path.isfile(rep):
            report("numbers", False, "%s: the guardian stopped (exit %d): %s" % (doc, r.returncode, (r.stderr or "")[-300:]))
            continue
        text = read(rep)
        c = {"total": int(re.search(r"printed numbers found:\s*(\d+)", text).group(1))}
        for k in ("PATH", "STRING", "CONTEXT", "UNCHECKED", "MISSING"):
            c[k] = int(re.search(r"^\s+%s\s+(\d+)\s*$" % k, text, re.M).group(1))
        stored = os.path.join(PAPER, "check_numbers_output_%s.txt" % doc[:-4])
        same = os.path.isfile(stored) and read(stored).replace("\\", "/") == text.replace("\\", "/")
        e = exp.get(doc)
        ok = c["MISSING"] == 0 and (e is None or all(c[k] == e[k] for k in c))
        report("numbers", ok, "%s: %d numbers, PATH %d, STRING %d, CONTEXT %d, UNCHECKED %d, MISSING %d%s%s (%.0f s)" % (
            doc, c["total"], c["PATH"], c["STRING"], c["CONTEXT"], c["UNCHECKED"], c["MISSING"],
            "" if e is None else ("; counts as recorded when the package was built" if all(c[k] == e[k] for k in c) else "; COUNTS DIFFER from docs/EXPECTED.json %s" % e),
            "; report identical to the stored one" if same else "; report differs from the stored one", dt))


# --------------------------------------------------------------------------------------------------- certificates
def all_certificates():
    p = os.path.join(ROOT, "docs", "CERTIFICATES.tsv")
    if os.path.isfile(p):
        return [l.strip() for l in read(p).splitlines()[1:] if l.strip()]
    out = []
    for dp, dn, fn in os.walk(os.path.join(ROOT, "phase3")):
        dn.sort()
        for f in sorted(fn):
            if f.endswith("_cert.json"):
                out.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))
    return sorted(out)


def step_certificates(a, env, tmp):
    certs = all_certificates()
    if not certs:
        report("certificates", False, "no certificate file found")
        return
    if a.all:
        chosen = certs
    else:                                                     # the same sample on every machine: evenly spaced in the sorted list
        k = max(1, min(a.sample, len(certs)))
        chosen = sorted(set(certs[round(i * (len(certs) - 1) / max(1, k - 1))] for i in range(k)))
    out_dir = os.path.join(tmp, "certificates")
    os.makedirs(out_dir, exist_ok=True)
    print("certificates: %d of %d, verifier: %s" % (len(chosen), len(certs),
          "independent (operator identity + every block, exact arithmetic)" if a.verifier == "independent" else "stored (verify_exact.py; about 10 minutes or more each)"), flush=True)
    for rel in chosen:
        path = os.path.join(ROOT, *rel.split("/"))
        d = json.load(open(path, encoding="utf-8"))
        cands = [os.path.join(g, d["graph"]) for g in [os.path.dirname(path)] + GRAPH_DIRS]      # next to the certificate first
        gpath = next((g for g in cands if os.path.isfile(g) and sha256_file(g) == d.get("graph_sha256")), None)
        name = os.path.basename(rel)[:-len("_cert.json")]
        if gpath is None:
            report("certificates", False, "%s: graph file missing or different from the one the certificate names" % name)
            continue
        out = os.path.join(out_dir, name + "_check.json")
        if os.path.exists(out):
            os.remove(out)
        if a.verifier == "independent":
            cmd = [a.python, "-B", "-I", MYVERIFY, gpath, path, out, "--methods", "chol"]
        else:
            cmd = [a.python, "-B", "-I", VERIFY_STORED, gpath, path, out]
        r, dt = run(cmd, ROOT, env, timeout=6 * 3600)
        if r.returncode != 0 or not os.path.isfile(out):
            report("certificates", False, "%s: the verifier stopped (exit %d): %s" % (name, r.returncode, (r.stderr or "")[-300:]))
            continue
        v = json.load(open(out, encoding="utf-8"))
        claim = d.get("E_claim")
        if a.verifier == "independent":
            ok = (v.get("identity_holds") is True and v.get("all_cluster_inequalities_proved") is True
                  and v.get("E_matches_cert_claim") is True and v.get("cert_sha256") == sha256_file(path))
        else:
            ok = v.get("ok") is True and v.get("E_LB_exact") == claim and v.get("cert_sha256") == sha256_file(path)
        stored = next((path[:-len("_cert.json")] + suf for suf in ("_ver.json", "_verify_exact.json")
                       if os.path.isfile(path[:-len("_cert.json")] + suf)), None)
        note = ""
        if stored:
            s = json.load(open(stored, encoding="utf-8"))
            agree = s.get("ok") is True and s.get("E_LB_exact") == v.get("E_LB_exact")
            ok = ok and agree
            note = "; equals the stored verification record" if agree else "; DIFFERS from the stored verification record"
        report("certificates", ok, "%s: bound %s proved in exact arithmetic%s (%.0f s)" % (name, v.get("E_LB_exact"), note, dt)
               if ok else "%s: NOT confirmed%s (%.0f s)" % (name, note, dt))


# ------------------------------------------------------------------------------------------- map, bias, learning
ANCHOR = r"(?:phase3[\\/]+full_runs|paper[\\/]+reviews)"
# an absolute path up to the folder that holds phase3/ and paper/: a drive letter, or a slash right after a quote or a blank
ROOT_RX = re.compile(r"(?:[A-Za-z]:|(?<=[\"'\s=(]))(?:[\\/]+[^\\/\"'\s:*?<>|]+)+?(?=[\\/]+" + ANCHOR + r"[\\/])")
TAIL_RX = re.compile(r"<ROOT>((?:[\\/]+[\w.+\-]+)+)")


def canon(text):
    """the same text with the folder that holds phase3/ and paper/ written as <ROOT> and the path separators after it
    written as '/': stored outputs record the full path of the files they used."""
    text = ROOT_RX.sub("<ROOT>", text)
    return TAIL_RX.sub(lambda m: "<ROOT>" + re.sub(r"[\\/]+", "/", m.group(1)), text)


def drop_times(x):
    if isinstance(x, dict):
        return {k: drop_times(v) for k, v in x.items() if k not in ("time_s", "seconds", "elapsed_s", "secs")}
    if isinstance(x, list):
        return [drop_times(v) for v in x]
    return x


REL_TOL, ABS_TOL = 1e-9, 1e-12
# a decimal number standing on its own: not part of a word, a file name, a checksum or an identifier
FLOAT_RX = re.compile(r"(?<![\w.+\-])[-+]?(?:\d+\.\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?|\d+[eE][-+]?\d+)(?![\w.])")
TOLERANT = []          # (step, file) of the outputs that passed entry by entry and not byte for byte


class Tolerant:
    """entry-by-entry comparison of two outputs: everything identical except decimal numbers, which may differ by a
    relative REL_TOL (or by ABS_TOL when both are that small)."""

    def __init__(self):
        self.n = self.diff = 0
        self.worst = 0.0

    def num(self, x, y):
        self.n += 1
        if x == y or (x != x and y != y):
            return True
        d, scale = abs(x - y), max(abs(x), abs(y))
        if d <= max(ABS_TOL, REL_TOL * scale):
            self.diff += 1
            self.worst = max(self.worst, d / scale if scale > 0 else 0.0)
            return True
        return False

    def text(self, s, t):
        if s == t:
            return True
        if FLOAT_RX.split(s) != FLOAT_RX.split(t):          # the text between the decimal numbers must be identical
            return False
        return all(self.num(float(u), float(v)) for u, v in zip(FLOAT_RX.findall(s), FLOAT_RX.findall(t)))

    def value(self, x, y):
        if x is None or y is None or isinstance(x, bool) or isinstance(y, bool):
            return x is y
        if isinstance(x, float) or isinstance(y, float):
            return isinstance(x, (int, float)) and isinstance(y, (int, float)) and self.num(float(x), float(y))
        if isinstance(x, int):
            return isinstance(y, int) and x == y
        if isinstance(x, str):
            return isinstance(y, str) and self.text(x, y)
        if isinstance(x, list):
            return isinstance(y, list) and len(x) == len(y) and all(self.value(u, v) for u, v in zip(x, y))
        if isinstance(x, dict):
            return isinstance(y, dict) and set(x) == set(y) and all(self.value(x[k], y[k]) for k in x)
        return False


def equal_within_tolerance(t_new, t_old, without_times):
    """-> (equal?, Tolerant) for two outputs already written with <ROOT>; JSON entry by entry, any other text by its
    decimal numbers."""
    tol = Tolerant()
    try:
        j_new, j_old = json.loads(t_new), json.loads(t_old)
    except ValueError:
        return tol.text(t_new, t_old), tol
    if without_times:
        j_new, j_old = drop_times(j_new), drop_times(j_old)
    return tol.value(j_new, j_old), tol


def compare(step, new_dir, stored_dir, names, sums=None, loose=()):
    """byte comparison by SHA-256; if the bytes differ, in this order: apart from line endings; with the folder of the
    package written as a placeholder (files that record where they were made); for files in `loose`, without the
    recorded run times; last, entry by entry with decimal numbers to a relative REL_TOL. Each case is reported in words."""
    all_ok = True
    for name in names:
        new, old = os.path.join(new_dir, name), os.path.join(stored_dir, name)
        if not os.path.isfile(new) or not os.path.isfile(old):
            report(step, False, "%s: %s" % (name, "not produced" if not os.path.isfile(new) else "no stored file to compare with"))
            all_ok = False
            continue
        h_new, h_old = sha256_file(new), sha256_file(old)
        listed = (sums or {}).get(name)
        if listed and listed != h_old:
            report(step, False, "%s: the stored file does not have the SHA-256 of its checksum list" % name)
            all_ok = False
            continue
        if h_new == h_old:
            report(step, True, "%s: SHA-256 equal to the stored output (%s)" % (name, h_new[:16]))
            continue
        r_new, r_old = read(new), read(old)                 # read() gives the text with every line ending written as "\n"
        if r_new == r_old:
            report(step, True, "%s: equal to the stored output apart from line endings (the stored file was written on "
                               "Windows, this one on a system with other line endings)" % name)
            continue
        t_new, t_old = canon(r_new), canon(r_old)
        if t_new == t_old:
            report(step, True, "%s: equal to the stored output once the folder of the package is written as <ROOT> "
                               "(the file records the paths of the certificates it used)" % name)
            continue
        if name in loose:
            try:
                j_new, j_old = drop_times(json.loads(t_new)), drop_times(json.loads(t_old))
            except ValueError:
                j_new, j_old = 0, 1
            if j_new == j_old:
                report(step, True, "%s: equal to the stored output apart from recorded run times and the folder of the package" % name)
                continue
        same, tol = equal_within_tolerance(t_new, t_old, name in loose)
        if same and not tol.diff:                           # the same entries written differently (spacing, order of keys)
            report(step, True, "%s: equal to the stored output entry by entry; the two files differ only in how the same "
                               "entries are written" % name)
            continue
        if same:
            TOLERANT.append((step, name))
            report(step, True, "%s: equal to the stored output entry by entry, NOT byte for byte: %d of its %d decimal numbers "
                               "differ in the last digits (largest relative difference %.1e, tolerance %.0e), everything else is "
                               "identical; expected on another processor or numerical library"
                   % (name, tol.diff, tol.n, tol.worst, REL_TOL))
            continue
        report(step, False, "%s: DIFFERS from the stored output (new %s, stored %s)" % (name, h_new[:16], h_old[:16]))
        all_ok = False
    return all_ok


def step_map(a, env, tmp):
    out = os.path.join(tmp, "map")
    os.makedirs(out, exist_ok=True)
    e1 = os.path.join(RD, "e1", "certs")
    with_e1 = os.path.isdir(e1) and any(f.endswith("_cert.json") for f in os.listdir(e1))
    stored = os.path.join(RD, "e1", "map_e1") if with_e1 else os.path.join(RD, "out")
    cmd = [a.python, "-B", "-I", os.path.join(RD, "code", "run_map.py"), "--out", out] + (["--no-g5-reprove"] if a.no_reprove else [])
    print("map: running the declared code (%s); stored outputs to compare with: %s" % (
        "about 3 to 6 minutes" if not a.no_reprove else "under a minute", os.path.relpath(stored, ROOT).replace(os.sep, "/")), flush=True)
    r, dt = run(cmd, ROOT, env)
    with open(os.path.join(out, "run_map_stdout.txt"), "w", encoding="utf-8") as f:
        f.write(r.stdout + "\n--- stderr ---\n" + r.stderr)
    if r.returncode != 0:
        report("map", False, "run_map.py stopped (exit %d) after %.0f s: %s" % (r.returncode, dt, (r.stderr or r.stdout)[-400:]))
        return
    g = re.search(r"gates: (\{.*\})", r.stdout)
    report("map", True, "run_map.py finished in %.0f s; %s" % (dt, g.group(1) if g else "no gate line found"))
    sums = read_sums(os.path.join(stored, "SHA256SUMS_map.txt"))
    names = ["S_sets.json", "map_rows.json", "map_summary.json", "map_secondary.json", "map_tables.md", "map_gates.json"]
    if a.no_reprove:
        print("map: --no-reprove was given: map_gates.json and map_summary.json then record the re-proofs as skipped and are expected to differ", flush=True)
    compare("map", out, stored, names, sums=sums, loose=("map_gates.json",))


def step_bias(a, env, tmp):
    out = os.path.join(tmp, "predict")
    os.makedirs(out, exist_ok=True)
    r, dt = run([a.python, "-B", "-I", os.path.join(RD, "code", "run_predict.py"), "--hash=" + declaration_hash(), "--out=" + out], ROOT, env)
    if r.returncode != 0:
        report("bias", False, "run_predict.py stopped (exit %d): %s" % (r.returncode, (r.stderr or r.stdout)[-400:]))
        return
    report("bias", True, "run_predict.py finished in %.0f s" % dt)
    compare("bias", out, os.path.join(RD, "out", "predict"), ["predict_results.json"])


def step_learning(a, env, tmp):
    out = os.path.join(tmp, "learn")
    os.makedirs(out, exist_ok=True)
    r, dt = run([a.python, "-B", "-I", os.path.join(RD, "code", "run_learn.py"), "--hash=" + declaration_hash(),
                 "--stage=cheap", "--out=" + out], ROOT, env)
    if r.returncode != 0:
        report("learning", False, "run_learn.py --stage=cheap stopped (exit %d): %s" % (r.returncode, (r.stderr or r.stdout)[-400:]))
        return
    report("learning", True, "run_learn.py --stage=cheap finished in %.0f s" % dt)
    sums = {k.replace("out/learn/", ""): v for k, v in read_sums(os.path.join(RD, "results", "SHA256SUMS_learn.txt")).items()
            if k.startswith("out/learn/")}
    compare("learning", out, os.path.join(RD, "out", "learn"),
            ["results_cheap.json", "prop2_cubic.json", "f2_floor.json", "f3_constructive.json", "f1_rules.json"], sums=sums,
            loose=("results_cheap.json",))                 # this file records how long each model took


# ---------------------------------------------------------------------------------------------------------- pdf
def step_pdf(a, env, tmp):
    if not shutil.which("pdflatex") or not shutil.which("bibtex"):
        report("pdf", False, "pdflatex or bibtex not found on this machine")
        return
    build = PAPER if a.in_place else os.path.join(tmp, "pdf")
    os.makedirs(build, exist_ok=True)
    env2 = dict(env)
    env2["BIBINPUTS"] = PAPER + os.pathsep + env.get("BIBINPUTS", "")
    for doc in ("main", "supplement", "tables"):
        if not os.path.isfile(os.path.join(PAPER, doc + ".tex")):
            continue
        latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error"] + ([] if a.in_place else ["-output-directory=" + build]) + [doc + ".tex"]
        t0 = time.time()
        seq = [("pdflatex", latex, PAPER), ("bibtex", ["bibtex", doc], build), ("pdflatex", latex, PAPER), ("pdflatex", latex, PAPER)]
        failed = None
        for label, cmd, cwd in seq:
            r, _ = run(cmd, cwd, env2, timeout=1800)
            if r.returncode != 0:
                failed = "%s stopped (exit %d): %s" % (label, r.returncode, (r.stdout or "")[-300:].replace("\n", " "))
                break
        log = read(os.path.join(build, doc + ".log")) if os.path.isfile(os.path.join(build, doc + ".log")) else ""
        if not failed and re.search(r"Rerun to get|Label\(s\) may have changed", log):
            run(latex, PAPER, env2, timeout=1800)
            log = read(os.path.join(build, doc + ".log"))
        pdf = os.path.join(build, doc + ".pdf")
        if failed or not os.path.isfile(pdf):
            report("pdf", False, "%s.tex: %s" % (doc, failed or "no PDF written"))
            continue
        pages = re.search(r"Output written on .*?\((\d+) pages?", log.replace("\n", ""))
        bad = re.findall(r"^! .*$|Citation .* undefined|Reference .* undefined", log, re.M)
        ok = not bad
        report("pdf", ok, "%s.pdf: %s pages, %d LaTeX errors or undefined citations/references%s (%.0f s) -> %s" % (
            doc, pages.group(1) if pages else "?", len(bad), "" if ok else " (first: %s)" % bad[0][:80], time.time() - t0, pdf))


# ---------------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("steps", nargs="*", help="any of: %s (default: all)" % " ".join(STEPS))
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true", help="certificates: verify every certificate (about twenty minutes on a laptop)")
    ap.add_argument("--verifier", choices=["independent", "stored"], default="independent")
    ap.add_argument("--no-reprove", action="store_true", help="map: skip the exact re-proof of the deciding certificates")
    ap.add_argument("--in-place", action="store_true", help="pdf: compile inside paper/ (overwrites paper/*.pdf)")
    ap.add_argument("--tmp", default=None)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    steps = a.steps or STEPS
    unknown = [s for s in steps if s not in STEPS]
    if unknown:
        ap.error("unknown step(s): %s" % " ".join(unknown))
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[k] = str(a.threads)
    own_tmp = a.tmp is None
    tmp = tempfile.mkdtemp(prefix="p5_checks_") if own_tmp else os.path.abspath(a.tmp)
    os.makedirs(tmp, exist_ok=True)
    print("package: %s\nwork folder: %s\npython: %s" % (ROOT, tmp, a.python), flush=True)
    funcs = dict(numbers=step_numbers, certificates=step_certificates, map=step_map, bias=step_bias, learning=step_learning, pdf=step_pdf)
    try:
        for s in STEPS:
            if s in steps:
                try:
                    funcs[s](a, env, tmp)
                except subprocess.TimeoutExpired as e:
                    report(s, False, "stopped after the time limit: %s" % e)
                except Exception as e:                       # a broken step is a result, not a crash of the others
                    report(s, False, "%s: %s" % (type(e).__name__, e))
        with open(os.path.join(tmp, "run_checks_report.json"), "w", encoding="utf-8") as f:
            json.dump([dict(step=s, passed=ok, detail=d) for s, ok, d in RESULTS], f, indent=1)
    finally:
        n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
        print("\nsummary: %d lines, %d PASS, %d FAIL" % (len(RESULTS), len(RESULTS) - n_fail, n_fail))
        for s in STEPS:
            rows = [ok for st, ok, _ in RESULTS if st == s]
            if rows:
                print("  %-12s %s (%d of %d)" % (s, "PASS" if all(rows) else "FAIL", sum(rows), len(rows)))
        if TOLERANT:
            print("  not byte for byte, equal entry by entry to a relative %.0e: %s"
                  % (REL_TOL, ", ".join("%s/%s" % t for t in TOLERANT)))
        if own_tmp and not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)           # only the folder this run created itself
        else:
            print("work folder kept: %s" % tmp)
    return 1 if any(not ok for _, ok, _ in RESULTS) else 0


if __name__ == "__main__":
    sys.exit(main())
