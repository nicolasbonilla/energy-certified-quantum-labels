"""real_data/checks/r11/fp_counts.py  (R11 fix pass, fixer FP, 2026-11-13; descriptive, reads stored outputs only)

Two counts that the manuscript printed with an internal review report as their only source (finding release-01):

 (a) the 147 checked states of the emulation: pipeline states plus subsets of perfect samples, and how many of them
     have a site, a nearest-neighbour correlation or a 12-site loop that is NOT more ordered than the reference
     (same logic as the last block of paper/reviews/R10_2026-11-12/scratch/num-guardians/verify_findings.py);
     source: phase3/full_runs/method/laptop_post/out/{emu,gsscan,ref}/*.json
 (b) the length selected by cross-validation in the eight quantum-side fits of the declared test on disordered
     lattices (two couplings, site and bond labels, primary and secondary family), against the declared grid;
     source: phase3/full_runs/final_tests/out_20261106T120830Z/out/b/model_J<Jz>_<type>.json (fits.<name>.best, .cv)

  python -B -I fp_counts.py        (writes fp_counts_out.txt next to this file)
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # phase3/full_runs
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


# ------------------------------------------------------------------------------------------------ (a) the 147 states
base = os.path.join(RUNS, "method", "laptop_post", "out")


def ref(n, J):
    return json.load(open(os.path.join(base, "ref", "ref_n%d_J%.1f.json" % (n, J)), encoding="utf-8"))["labels"]


def all_over(labels, rl):
    res = {}
    for key in ("Z", "Czz", "Zloop"):
        ex = [(1 if y > 0 else -1) * (x - y) for x, y in zip(labels[key], rl[key])]
        res[key] = all(e > 0 for e in ex)
    return res


n_pipe = n_gs = bad = 0
per = {}
for f in sorted(glob.glob(os.path.join(base, "emu", "emu_n*_J*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    rl = ref(d["n"], d["Jz"])
    for name, v in d["var"].items():
        if name == "primary":
            continue                       # alias of another variant
        n_pipe += 1
        per[d["n"]] = per.get(d["n"], 0) + 1
        bad += (not all(all_over(v["labels"], rl).values()))
for f in sorted(glob.glob(os.path.join(base, "gsscan", "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    rl = ref(d["n"], d["Jz"])
    for kind in ("nested", "topD"):
        for r in d.get(kind) or []:
            n_gs += 1
            per[d["n"]] = per.get(d["n"], 0) + 1
            bad += (not all(all_over(r["labels"], rl).values()))
P("(a) checked states of the emulation: pipeline states %d + subsets of perfect samples %d = %d (103 + 44 = 147 expected)" % (
    n_pipe, n_gs, n_pipe + n_gs))
P("    by size: %s ; states with a site, a nearest-neighbour correlation or a loop NOT more ordered than the reference: %d" % (
    {k: per[k] for k in sorted(per)}, bad))
assert (n_pipe, n_gs, bad) == (103, 44, 0), (n_pipe, n_gs, bad)

# ------------------------------------------------------------------- (b) lengths selected in the quantum-side fits
P("")
bdir = os.path.join(RUNS, "final_tests", "out_20261106T120830Z", "out", "b")
n_fits = n_top = 0
grid_all = set()
for J in ("1.6", "2.5"):
    for typ in ("site", "bond"):
        d = json.load(open(os.path.join(bdir, "model_J%s_%s.json" % (J, typ)), encoding="utf-8"))
        for name in ("q_top", "q_kry"):
            fit = d["fits"][name]
            grid = sorted(set(c["ell"] for c in fit["cv"] if c.get("ell") is not None))
            grid_all |= set(grid)
            best = fit["best"]
            n_fits += 1
            n_top += (best["kind"] == "rff" and best["ell"] == max(grid))
            P("(b) Jz %s %-4s %-5s selected: kind %s, length %g, penalty %g ; lengths of the grid %s" % (
                J, typ, name, best["kind"], best["ell"], best["alpha"], [("%g" % g) for g in grid]))
P("(b) quantum-side fits: %d ; fits that selected the greatest length of the declared grid {%s}: %d of %d" % (
    n_fits, ", ".join("%g" % g for g in sorted(grid_all)), n_top, n_fits))

open(os.path.join(HERE, "fp_counts_out.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
