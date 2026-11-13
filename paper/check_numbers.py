"""check_numbers.py -- every number printed in main.tex against the source named in its `% src:` comment.

  python -I check_numbers.py [main.tex]      (writes check_numbers_output.txt next to this file)

For every line of the document body that prints a number, the trailing comment must name its source:
    % src: <item> [; <item> ...]
Item forms (paths relative to J_next_paper/, the parent of paper/):
    map:<path>        phase3/full_runs/map/laptop_analysis/summary_map.json
                      row(n,Jz,label).a.b  selects a row of "rows"; a trailing "/tau" divides by that row's tau
    meth:<path>       phase3/full_runs/method/laptop_post/out/summary.json
    rig:<path>        phase3/full_runs/rigor/outputs/results_v2.json  (rigorous certificates, declared grid)
    rig1:<path>       phase3/full_runs/rigor/outputs/results.json     (first rigorous test)
    qpu:<path>        phase3/full_runs/qpu/analysis/analysis.json     (our device data)
    hu:<path>         phase3/full_runs/huang/laptop_analysis/summary_huang.json (second benchmark)
                      list selectors: rows[Jz=1.2] or rows[n=57,Jz=3.4,label=m_s] (numbers to 1e-9, strings exact)
    emu(n,Jz):<path>  .../laptop_post/out/emu/emu_n<n>_J<Jz>.json
    ref(n,Jz):<path>  .../laptop_post/out/ref/ref_n<n>_J<Jz>.json
    ml(n):<path>      .../laptop_post/out/ml/ml_n<n>.json ; list selector rows[Jz=1.2]
    file:<relpath>    the printed string must occur in that file (weak check)
    def:<relpath>     a convention fixed in that file; checked like file:
    r3:<file>         paper/data/r3gen/out/<file>; checked like file:
    lm1 lm2 lver lib lwh lp2 ldsc blw fta ftb ftc ftx ftp:<path>   see P below
    fts:<path>        final_tests/analysis/post_checks_s.json (post hoc, not declared; R5 S1, S13)
    tsc:<path>        map/laptop_analysis/tau_scan.json (post hoc tolerance scan; R5 S6)
    wan:<path>        kill_tests/W_window/out_20261107T190617Z/out/analysis.json (test W, step 1)
    ws0:<path>        kill_tests/W_window/step0_recheck.json (test W, step 0, constants re-read on the arXiv API)
    ws2:<path>        kill_tests/W_window/s2_summary.json (test W, post-hoc <S^2> ranges per method; R6 S11)
    derived: ...      arithmetic on cited values: reported, not checked
    fig: ...          a reading of a published figure of the dataset paper: reported, not checkable here
A comment starting with "% (" marks a line whose digits are structural (no source needed); it is reported.

Verdicts per printed number:
    PATH     equals a value at the cited JSON path, to the printed precision (also x100 for percentages)
    STRING   occurs verbatim (or in an equivalent spelling) in a cited file
    CONTEXT  a model constant (n = 19, 57, 115; 45 training points) or a Jz grid value on a line about Jz
    UNCHECKED  the line cites only derived:/fig: sources, or is marked structural
    MISSING  no cited source contains it, or the line has no `% src:` comment
The script exits 0; it is a report, not a gate.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
P = {"map": "phase3/full_runs/map/laptop_analysis/summary_map.json",
     "meth": "phase3/full_runs/method/laptop_post/out/summary.json",
     # integration pass (2026-10-31): rigorous bounds (v2 grid run, v1 first test), device data, second benchmark
     "rig": "phase3/full_runs/rigor/outputs/results_v2.json",
     "rig1": "phase3/full_runs/rigor/outputs/results.json",
     "qpu": "phase3/full_runs/qpu/analysis/analysis.json",
     "hu": "phase3/full_runs/huang/laptop_analysis/summary_huang.json",
     # Track-1 integration (2026-11-04): the learning run
     "lm1": "phase3/full_runs/learning/analysis/learn_M1_D_O.json",
     "lm2": "phase3/full_runs/learning/analysis/learn_M2_D_O.json",
     "lver": "phase3/full_runs/learning/analysis/verdicts.json",
     # final-fix pass (2026-11-04): the realistic learning test on the heavy-hex model, and the benchmark widths
     "lib": "phase3/full_runs/learning_ibm/out/results.json",
     "lwh": "phase3/full_runs/learning_ibm/out/widths_huang.json",
     # third reading (2026-11-04): Proposition 2(a)/(b) for the cubic model, and descriptive ratios
     "lp2": "phase3/full_runs/learning_ibm/out/prop2_cubic.json",
     "ldsc": "phase3/full_runs/learning_ibm/out/descriptive.json",
     # Quantum reframing (2026-11-06): exploratory bias analysis
     "blw": "phase3/full_runs/bias_law/out/results.json",
     # declared tests (2026-11-06)
     "fta": "phase3/full_runs/final_tests/analysis/test_a.json",
     "ftb": "phase3/full_runs/final_tests/analysis/test_b.json",
     "ftc": "phase3/full_runs/final_tests/analysis/test_c.json",
     "ftx": "phase3/full_runs/final_tests/analysis/test_c_extra.json",
     "ftp": "phase3/full_runs/final_tests/analysis/post_checks.json",
     # declared test C3 (2026-11-10): exact analysis of the ibm_kingston job of 2026-11-10 (analyze_c.py, unchanged)
     "ft3": "phase3/full_runs/final_tests/analysis/c3b_20261110/test_c3b.json",
     # R5 should-fix pass and test W (2026-11-08); post-hoc reads of stored outputs, labelled as such in the text
     "fts": "phase3/full_runs/final_tests/analysis/post_checks_s.json",
     "tsc": "phase3/full_runs/map/laptop_analysis/tau_scan.json",
     "wan": "phase3/full_runs/kill_tests/W_window/out_20261107T190617Z/out/analysis.json",
     "ws0": "phase3/full_runs/kill_tests/W_window/step0_recheck.json",
     # R6 pass (2026-11-08): post-hoc read of test W (<S^2> of the stored states), written by W_window/code/post/s2_summary.py
     "ws2": "phase3/full_runs/kill_tests/W_window/s2_summary.json",
     # real-data pass (2026-11-12): the public data of the dataset paper (repository at a pinned commit, converted to
     # JSON) and the analyses declared in phase3/full_runs/real_data/DECLARATION.md
     "rd57": "phase3/full_runs/real_data/converted/real_n57.json",
     "rd115": "phase3/full_runs/real_data/converted/real_n115.json",
     "rdm": "phase3/full_runs/real_data/out/map_real.json",          # the map on the public energies (rows, gates)
     "rdw": "phase3/full_runs/real_data/out/map_rows.json",
     "rdq": "phase3/full_runs/real_data/out/map_summary.json",
     "rdx": "phase3/full_runs/real_data/out/map_secondary.json",
     "rdg": "phase3/full_runs/real_data/out/map_gates.json",
     "rds": "phase3/full_runs/real_data/out/S_sets.json",            # sets of certified labels used by the learning tests
     "rdp": "phase3/full_runs/real_data/out/predict_real.json",      # sign, trend and curve of the bias on the public labels
     "rdl": "phase3/full_runs/real_data/out/learn_real.json",        # learning tests on the public labels
     "rdc": "phase3/full_runs/real_data/out/learn/results_cheap.json",
     "rdf1": "phase3/full_runs/real_data/out/learn/f1_rules.json",
     "rdf2": "phase3/full_runs/real_data/out/learn/f2_floor.json",
     "rdf3": "phase3/full_runs/real_data/out/learn/f3_constructive.json",
     "rdp2": "phase3/full_runs/real_data/out/learn/prop2_cubic.json",
     "rdd": "phase3/full_runs/real_data/checks/descriptive_checks.json",
     "rdam": "phase3/full_runs/real_data/checks/rd_audit_map.json",   # independent recomputation (audit)
     "rdap": "phase3/full_runs/real_data/checks/rd_audit_predict_learn.json",
     "rdai": "phase3/full_runs/real_data/checks/rd_audit_integrity.json",
     # extension E1 of the declaration (certificates computed after it, separate column; collected 2026-11-12)
     "rdew": "phase3/full_runs/real_data/e1/map_e1/map_rows.json",     # fields exact_e1, status_e1, status_e1_rf
     "rdeq": "phase3/full_runs/real_data/e1/map_e1/map_summary.json",  # jstar.<n>_<label>.sec2_e1, filter...exact_with_E1
     "rdes": "phase3/full_runs/real_data/e1/map_e1/S_sets.json",       # sizes.<n>.secondary_E1
     "rdec": "phase3/full_runs/real_data/e1/certs/E1_CERTS.json",
     # secondary run of the constructive test on the E1-extended sets (writer L, 2026-11-12)
     "rdel": "phase3/full_runs/real_data/e1/learn_e1/summary_e1.json",
     # energy error of the emulated first stage over the published one (coordinator, 2026-11-13; descriptive)
     "rdee": "phase3/full_runs/real_data/checks/emulation_vs_published_energy.json",
     # (f1) of the declaration, the neural pieces completed after the audit (coordinator, 2026-11-13; sealed scripts unchanged)
     "rdn57": "phase3/full_runs/real_data/f1_neural/out/results_mlp_pilot3_n57.json",
     "rdn115": "phase3/full_runs/real_data/f1_neural/out/results_mlp_pilot3_n115.json"}
EMU = "phase3/full_runs/method/laptop_post/out/emu/emu_n%d_J%.1f.json"
REF = "phase3/full_runs/method/laptop_post/out/ref/ref_n%d_J%.1f.json"
ML = "phase3/full_runs/method/laptop_post/out/ml/ml_n%d.json"
R3 = "paper/data/r3gen/out/"
CONTEXT_INTS = {19, 57, 115, 45}
GRID = {round(1.0 + 0.1 * k, 1) for k in range(1, 51)}
_cache = {}


def load_json(rel):
    if rel not in _cache:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            _cache[rel] = json.load(f)
    return _cache[rel]


def load_text(rel):
    key = "TXT:" + rel
    if key not in _cache:
        txt = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        try:                                  # undo a double encoding (UTF-8 read as cp1252) if present
            fixed = txt.encode("cp1252").decode("utf-8")
            if fixed != txt:
                txt = txt + "\n" + fixed
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        _cache[key] = txt
    return _cache[key]


def leaves(x):
    """all numbers inside x (lists/dicts recursively); a list also contributes its length."""
    out = []
    if isinstance(x, bool) or x is None:
        return out
    if isinstance(x, (int, float)):
        return [float(x)]
    if isinstance(x, str):
        try:
            return [float(x)]
        except ValueError:
            return []
    if isinstance(x, dict):
        for v in x.values():
            out += leaves(v)
    if isinstance(x, list):
        out.append(float(len(x)))
        for v in x:
            out += leaves(v)
    return out


def walk(obj, path):
    """resolve a dotted path with selectors: key, rows[Jz=1.2], row(n,Jz,label) (map only)."""
    tau = None
    m = re.match(r"row\((\d+),([0-9.]+),([A-Za-z_]+)\)\.?(.*)", path)
    if m:
        n, J, lab = int(m.group(1)), float(m.group(2)), m.group(3)
        rows = [r for r in obj["rows"] if r["n"] == n and abs(r["Jz"] - J) < 1e-9 and r["label"] == lab]
        if not rows:
            raise KeyError("no map row %s" % path)
        obj, path, tau = rows[0], m.group(4), rows[0]["tau"]
    div = False
    if path.endswith("/tau"):
        path, div = path[:-4], True
    rest = path
    while rest:
        rest = rest.lstrip(".")
        if not rest:
            break
        sel = re.match(r"(\w+)\[([^\]]+)\]", rest)
        if sel:
            conds = [c.split("=", 1) for c in sel.group(2).split(",")]

            def ok(r):
                for k, v in conds:
                    k, v = k.strip(), v.strip()
                    if k not in r:
                        return False
                    try:
                        if abs(float(r[k]) - float(v)) > 1e-9:
                            return False
                    except (TypeError, ValueError):
                        if str(r[k]) != v:
                            return False
                return True
            hits = [r for r in obj[sel.group(1)] if ok(r)]
            if not hits:
                raise KeyError("no element %s" % sel.group(0))
            obj = hits[0]
            rest = rest[sel.end():]
            continue
        if isinstance(obj, dict):
            # longest key of this dict that is a prefix of the remaining path (keys may contain dots, e.g. 57_1.6_m_s)
            cand = [k for k in obj if rest == k or rest.startswith(k + ".")]
            if not cand:
                raise KeyError(rest.split(".")[0])
            k = max(cand, key=len)
            obj, rest = obj[k], rest[len(k):]
        elif isinstance(obj, list):
            m2 = re.match(r"(\d+)", rest)
            obj, rest = obj[int(m2.group(1))], rest[m2.end():]
        else:
            raise KeyError(rest)
    vals = leaves(obj)
    if div and tau:
        vals = [v / tau for v in vals]
    return vals


def resolve(item):
    """-> (kind, values or text)"""
    item = item.strip()
    if not item.startswith(("derived", "fig")):
        item = re.sub(r"\s+\([^()]*\)\s*$", "", item)        # drop a trailing human note "(0.2586)"
    m = re.match(r"(%s):(.+)$" % "|".join(sorted((re.escape(k) for k in P), key=len, reverse=True)), item)   # every alias of P (2026-11-12)
    if m:
        return "path", walk(load_json(P[m.group(1)]), m.group(2).strip())
    m = re.match(r"(emu|ref)\((\d+),([0-9.]+)\):(.+)$", item)
    if m:
        rel = (EMU if m.group(1) == "emu" else REF) % (int(m.group(2)), float(m.group(3)))
        return "path", walk(load_json(rel), m.group(4).strip())
    m = re.match(r"ml\((\d+)\):(.+)$", item)
    if m:
        return "path", walk(load_json(ML % int(m.group(1))), m.group(2).strip())
    m = re.match(r"(file|def):\s*(\S+)", item)
    if m:
        return "string", load_text(m.group(2))
    m = re.match(r"r3:\s*(\S+)", item)
    if m:
        return "string", load_text(R3 + m.group(1))
    if item.startswith("derived"):
        return "derived", None
    if item.startswith("fig"):
        return "fig", None
    if item.startswith("...") or item == "":
        return "none", None
    return "unknown", None


def split_comment(line):
    i = 0
    while True:
        j = line.find("%", i)
        if j < 0:
            return line, ""
        if j > 0 and line[j - 1] == "\\":
            i = j + 1
            continue
        return line[:j], line[j:]


def strip_tex(code):
    s = code
    s = re.sub(r"\\(cite|ref|eqref|label|input|includegraphics|begin|end|url|homepage|email|graphicspath|bibliography|"
               r"todo|texttt|newcommand|renewcommand|theoremstyle|newtheorem|documentclass|usepackage|hypersetup)"
               r"\*?(\[[^\]]*\])?\{[^{}]*\}", " ", s)
    s = re.sub(r"(Supp\.\\?\s*)?(Figs?|Secs?|Tables?|Eqs?|Thm|Cor)\.?~?\s*S?\d+", " ", s)
    s = re.sub(r"Sec\.~S\d+|Secs?\.~", " ", s)
    s = re.sub(r"Columns? \d+(--\d+)?|[Rr]eading \d", " ", s)
    s = re.sub(r"U\(1\)", " ", s)
    s = re.sub(r"\\Ctwo|\\Czz|\\des|\\de\b", " X ", s)
    return s


def tokens(code):
    """numeric tokens printed by a line: (string, value, decimals)."""
    s = strip_tex(code)
    s = re.sub(r"([0-9.]+)\s*\\times\s*10\^\{?(-?\d+)\}?", lambda m: " %se%s " % (m.group(1), m.group(2)), s)
    s = re.sub(r"(?<![0-9.])10\^\{?(-?\d+)\}?", lambda m: " 1e%s " % m.group(1), s)
    out = []
    parts = re.split(r"(\$[^$]*\$)", s)
    for part in parts:
        math = part.startswith("$") and part.endswith("$") and len(part) > 1
        p = part
        if math:
            p = re.sub(r"_\{[^{}]*\}|_\\?[A-Za-z0-9]", " ", p)
            p = re.sub(r"\^\{[^{}]*\}|\^[0-9a-zA-Z]", " ", p)
        for m in re.finditer(r"(?<![A-Za-z\\])[-+]?\d+(?:\.\d+)?(?:e-?\d+)?", p):
            t = m.group(0)
            body = t.lstrip("+-")
            if "e" in body:
                mant = body.split("e")[0]
                dec = len(mant.split(".")[1]) if "." in mant else 0
                val = float(body)
                prec = 0.5 * 10 ** (-dec) * 10 ** int(body.split("e")[1])
            else:
                dec = len(body.split(".")[1]) if "." in body else 0
                val = float(body)
                prec = 0.5 * 10 ** (-dec)
            if math and "." not in body and "e" not in body and val < 10:
                only = re.fullmatch(r"\$\s*[-+]?\d+\s*(\\%|\\,\\tau)?\s*\$", part.strip())
                if not only:
                    continue                    # a formula constant inside mathematics
            out.append((t, val, prec))
    return out


def match_path(val, prec, values):
    for v in values:
        for s in (1, 100, 0.01):
            if abs(val - abs(v) * s) <= prec * 1.0001 + 1e-15:
                return True
    return False


def spellings(t, val):
    b = t.lstrip("+-")
    out = {b}
    if "e" in b:
        mant, ex = b.split("e")
        out |= {"%se%s" % (mant, ex), "%se-0%s" % (mant, ex.lstrip("-")) if ex.startswith("-") else b,
                "%s×10%s" % (mant, ex)}
        sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
        out.add("%s×10%s" % (mant, ex.translate(sup)))
        out.add("%s × 10%s" % (mant, ex.translate(sup)))
        if mant == "1":
            out.add("10%s" % ex.translate(sup))
    if b.endswith(".0"):
        out.add(b[:-2])
    if "." in b and b.startswith("0."):
        out.add(b[1:])
    if val >= 1000 and "." not in b:
        out.add("{:,}".format(int(val)))
    return out


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "main.tex")
    lines = open(src, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().startswith(r"\begin{document}"))
    except StopIteration:
        start = 0
    rep, counts = [], {"PATH": 0, "STRING": 0, "CONTEXT": 0, "UNCHECKED": 0, "MISSING": 0}
    missing_lines, unknown_items = [], []
    for ln in range(start, len(lines)):
        code, com = split_comment(lines[ln])
        if not code.strip():
            continue
        toks = tokens(code)
        if not toks:
            continue
        srcs = []
        structural = com.strip().startswith("% (")
        m = re.search(r"%\s*(src|fig):(.*)$", com)
        if m:
            body = m.group(2) if m.group(1) == "src" else "fig:" + m.group(2)
            srcs, depth, cur = [], 0, ""
            for ch in body:                           # split on ';' outside parentheses
                depth += (ch == "(") - (ch == ")")
                if ch == ";" and depth == 0:
                    srcs.append(cur)
                    cur = ""
                else:
                    cur += ch
            srcs.append(cur)
        resolved = []
        for it in srcs:
            try:
                k, v = resolve(it)
            except Exception as e:                      # a broken path is a finding, not a crash
                k, v = "broken", str(e)
            if k in ("unknown", "broken"):
                unknown_items.append((ln + 1, it.strip(), v if k == "broken" else "unknown form"))
            resolved.append((k, v))
        lineverd = []
        jz_line = ("J_z" in code) or ("\\Jz" in code) or ("J^*" in code)
        for t, val, prec in toks:
            verdict = None
            for k, v in resolved:
                if k == "path" and v and match_path(val, prec, v):
                    verdict = "PATH"
                    break
            if not verdict:
                for k, v in resolved:
                    if k == "string" and any(sp in v for sp in spellings(t, val)):
                        verdict = "STRING"
                        break
            if not verdict:
                if (val in CONTEXT_INTS and "." not in t) or (jz_line and round(val, 1) in GRID and abs(val - round(val, 1)) < 1e-9):
                    verdict = "CONTEXT"
            if not verdict:
                if structural or any(k in ("derived", "fig") for k, _ in resolved):
                    verdict = "UNCHECKED"
                else:
                    verdict = "MISSING"
            counts[verdict] += 1
            lineverd.append("%s=%s" % (t, verdict))
        bad = [x for x in lineverd if x.endswith("MISSING")]
        if bad:
            missing_lines.append((ln + 1, " ".join(bad), code.strip()[:110], "no src" if not srcs and not structural else ""))
        rep.append("L%-4d %s" % (ln + 1, "  ".join(lineverd)))
    out = []
    total = sum(counts.values())
    out.append("check_numbers.py on %s" % os.path.relpath(src, ROOT))
    out.append("printed numbers found: %d" % total)
    for k in ("PATH", "STRING", "CONTEXT", "UNCHECKED", "MISSING"):
        out.append("  %-9s %4d" % (k, counts[k]))
    out.append("")
    out.append("== MISSING (no cited source contains the number, or no src comment) ==")
    for ln, b, c, why in missing_lines:
        out.append("L%-4d %s   %s  | %s" % (ln, why, b, c))
    out.append("")
    out.append("== source items that could not be resolved ==")
    for ln, it, why in unknown_items:
        out.append("L%-4d %s  -> %s" % (ln, it[:90], str(why)[:80]))
    out.append("")
    out.append("== per line ==")
    out += rep
    txt = "\n".join(out)
    with open(os.path.join(HERE, "check_numbers_output.txt"), "w", encoding="utf-8") as fo:
        fo.write(txt + "\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out[:12 + len(missing_lines) + len(unknown_items) + 4]))


if __name__ == "__main__":
    main()
