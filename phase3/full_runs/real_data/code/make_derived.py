# real_data / make_derived.py  (own code; 2026-11-12; task rd-code-learn)
#
# Writes rd_learn_ibm.py and rd_prop2_cubic.py FROM the stored scripts learning_ibm/code/learn_ibm.py and
# prop2_cubic.py by exact text operations, so that everything outside the data loader is a verbatim copy. The stored
# scripts are read, never written. Each anchor must occur exactly once, otherwise the script stops.
# tests/test_port_learning.py re-checks the result (function by function, on the syntax trees) and re-runs the stored
# emulated numbers through the derived files.
#
#   python -B -I make_derived.py <ROOT = work/>        (rewrites the two derived files next to this script)
import hashlib
import os
import sys

ROOT = os.path.abspath(sys.argv[1])
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "phase3", "full_runs", "learning_ibm", "code")


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def once(text, old, new):
    if text.count(old) != 1:
        raise SystemExit("anchor not found exactly once: %r (%d times)" % (old[:60], text.count(old)))
    return text.replace(old, new)


def header(name, src_sha):
    return ('# real_data / %s  (DERIVED FILE, written by make_derived.py; 2026-11-12; task rd-code-learn)\n'
            '#\n'
            '# Derived from learning_ibm/code/%s (SHA-256 %s), changed ONLY in the data loader:\n'
            '#   --data=real      (default) the public labels of arXiv:2606.15983, through rd_common (needs the hashed\n'
            '#                    declaration: --hash=<SHA-256 of DECLARATION.md>; refuses otherwise)\n'
            '#   --data=emulated  the stored emulated labels, with the ORIGINAL loader kept verbatim (port check)\n'
            '# Every line marked "# RD" is new; everything else is a verbatim copy of the stored script, whose docstring\n'
            '# follows unchanged (where it says "emulated", read "the labels of the chosen data source").\n'
            % (name, name[3:], src_sha))


# ------------------------------------------------------------------------------------------------ learn_ibm.py
src = read(os.path.join(SRC, "learn_ibm.py"))
sha = hashlib.sha256(open(os.path.join(SRC, "learn_ibm.py"), "rb").read()).hexdigest()
t = src
t = once(t, 'import ml2  # noqa: E402  (read-only import; no bytecode written)\n',
         'import ml2  # noqa: E402  (read-only import; no bytecode written)\n'
         '\n'
         '# RD ---- data source (begin)\n'
         'DATA = ARG.get("data", "real")  # RD\n'
         'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # RD\n'
         'import rd_common as rdc  # noqa: E402  # RD\n'
         'GATE = None  # RD\n'
         'if DATA == "real" and "--merge" not in sys.argv:  # RD\n'
         '    if "hash" not in ARG:  # RD\n'
         '        raise rdc.Refused("--hash=<SHA-256 of the hashed declaration> is required to read the real data.")  # RD\n'
         '    GATE = rdc.require_declaration_hash(rdc.RD, ARG["hash"])  # RD: refuses unless DECLARATION.sha256 matches\n'
         'elif DATA not in ("real", "emulated"):  # RD\n'
         '    raise SystemExit("--data must be real or emulated")  # RD\n'
         '# RD ---- data source (end)\n')
t = once(t, 'def load(n):\n    G = rj(os.path.join(METHOD, "code", "graphs", "hh_d%d.json" % {57: 5, 115: 7}[n]))',
         'def load_emulated(n):  # RD: the stored loader, renamed; body verbatim\n'
         '    G = rj(os.path.join(METHOD, "code", "graphs", "hh_d%d.json" % {57: 5, 115: 7}[n]))')
t = once(t, '\n\ndef qconf(scores, alpha=ALPHA):',
         '\n\ndef load_real(n):  # RD\n'
         '    """RD: the public labels. Z_lab = z_basis_opt; Z_ref = the authors\' DMRG (declaration Sec. 7); eps = E_real - E0\n'
         '    with E0 of declaration Sec. 0; no second state (Z_ideal = None)."""\n'
         '    return rdc.learning_dict(rdc.load_real(n, GATE, ROOT, ARG.get("converted")))  # RD\n'
         '\n\n'
         'def load(n):  # RD\n'
         '    return load_emulated(n) if DATA == "emulated" else load_real(n)  # RD\n'
         '\n\ndef qconf(scores, alpha=ALPHA):')
with open(os.path.join(HERE, "rd_learn_ibm.py"), "w", encoding="utf-8", newline="\n") as f:
    f.write(header("rd_learn_ibm.py", sha) + t)

# ------------------------------------------------------------------------------------------------ prop2_cubic.py
src = read(os.path.join(SRC, "prop2_cubic.py"))
sha = hashlib.sha256(open(os.path.join(SRC, "prop2_cubic.py"), "rb").read()).hexdigest()
t = src
t = once(t, 'import analyze_map as AM  # noqa: E402\n',
         'import analyze_map as AM  # noqa: E402\n'
         '\n'
         '# RD ---- data source (begin)\n'
         'ARG = {a.split("=")[0][2:]: a.split("=", 1)[1] for a in sys.argv[3:] if "=" in a}  # RD\n'
         'DATA = ARG.get("data", "real")  # RD\n'
         'sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # RD\n'
         'import rd_common as rdc  # noqa: E402  # RD\n'
         'GATE = None  # RD\n'
         'if DATA == "real":  # RD\n'
         '    if "hash" not in ARG:  # RD\n'
         '        raise rdc.Refused("--hash=<SHA-256 of the hashed declaration> is required to read the real data.")  # RD\n'
         '    GATE = rdc.require_declaration_hash(rdc.RD, ARG["hash"])  # RD: refuses unless DECLARATION.sha256 matches\n'
         'elif DATA != "emulated":  # RD\n'
         '    raise SystemExit("--data must be real or emulated")  # RD\n'
         '# RD ---- data source (end)\n')
t = once(t, 'def load(n):\n    """As learn_ibm.load', 'def load_emulated(n):  # RD: the stored loader, renamed; body verbatim\n    """As learn_ibm.load')
t = once(t, '\n\ndef coef(Jtr, Jq, deg=3):',
         '\n\ndef load_real(n):  # RD\n'
         '    """RD: the public labels (y), the authors\' DMRG (ystar, declaration Sec. 7), eps = E_real - E0 (Sec. 0)."""\n'
         '    rd = rdc.load_real(n, GATE, ROOT, ARG.get("converted"))  # RD\n'
         '    eta = rd.G["eta"]; D = {}  # RD\n'
         '    for J in rd.labelled():  # RD\n'
         '        r = rd.lab[J]; Zl, Zr = np.array(r["Z"], float), np.array(rd.truth_authors[J]["Z"], float)  # RD\n'
         '        D[J] = dict(eps=r["eps"], E0_emu=rd.truth[J]["E0"], y=ml2.ms(Zl, eta), ystar=ml2.ms(Zr, eta), Zl=Zl)  # RD\n'
         '    return eta, D  # RD\n'
         '\n\n'
         'def load(n):  # RD\n'
         '    return load_emulated(n) if DATA == "emulated" else load_real(n)  # RD\n'
         '\n\ndef coef(Jtr, Jq, deg=3):')
t = once(t, 'def intervals(n, D, Dmap, MR):\n', 'def intervals_emulated(n, D, Dmap, MR):  # RD: the stored function, renamed; body verbatim\n')
t = once(t, '\n\ndef interp_width(J, I, D):',
         '\n\ndef intervals_real(n, D, Dmap, MR):  # RD\n'
         '    """RD: the label intervals at (E_real, M_real) written by the map code (out/S_sets.json; declaration Sec. 7, f1):\n'
         '    upper version = the exact interval I of Sec. 2 where it exists, otherwise an indicative one (flagged);\n'
         '    lower version = the interval of the explicit witness mixtures, (1 - q) x hull."""\n'
         '    sets = rdc.load_sets(ARG.get("sets"), n, GATE)  # RD\n'
         '    return rdc.prop2_intervals(sorted(D), {J: D[J]["y"] for J in D}, {J: D[J]["ystar"] for J in D}, sets)  # RD\n'
         '\n\n'
         'def intervals(n, D, Dmap, MR):  # RD\n'
         '    return intervals_emulated(n, D, Dmap, MR) if DATA == "emulated" else intervals_real(n, D, Dmap, MR)  # RD\n'
         '\n\ndef interp_width(J, I, D):')
t = once(t, '\n\ndef main():',
         '\n\n# RD ---- flags for upper intervals that are not exact intervals of Sec. 2 (real data only; begin)\n'
         'if DATA == "real":  # RD\n'
         '    _band_stored, _calib_stored = band, calib  # RD: the stored functions, called unchanged\n'
         '\n'
         '    def band(Jtr, Jq, I, D):  # RD\n'
         '        b = _band_stored(Jtr, Jq, I, D)  # RD\n'
         '        b["indicative"] = bool(b["indicative"] or any(I[j].get("indicative", False) for j in Jtr))  # RD\n'
         '        return b  # RD\n'
         '\n'
         '    def calib(Jcal, I, D):  # RD\n'
         '        qlo, qhi, lev, ind, rows = _calib_stored(Jcal, I, D)  # RD\n'
         '        return qlo, qhi, lev, bool(ind or any(I[j].get("indicative", False) for j in Jcal)), rows  # RD\n'
         '# RD ---- flags (end)\n'
         '\n\ndef main():')
with open(os.path.join(HERE, "rd_prop2_cubic.py"), "w", encoding="utf-8", newline="\n") as f:
    f.write(header("rd_prop2_cubic.py", sha) + t)
print("written rd_learn_ibm.py, rd_prop2_cubic.py")
