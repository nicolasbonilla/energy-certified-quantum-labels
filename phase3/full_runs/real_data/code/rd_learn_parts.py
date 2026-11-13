# real_data / rd_learn_parts.py  (own code; 2026-11-12; task rd-code-learn)
#
# OPERATIONAL helper, no rule and no new number: runs the realistic test (f1) of ONE model and ONE size in pieces, so
# that the costly models (the pilot perceptron: about 4100 fits per size with 45 training couplings) can be spread over
# several processes. It calls the functions of rd_learn_ibm.py UNCHANGED (load, fitters, evaluate, summarize) with the
# same arguments as its main(); every fit is deterministic, so the assembled file holds exactly the numbers a single
# run of rd_learn_ibm.py --models=<model> --sizes=<n> would give (checked on the stored emulated labels by
# tests/test_port_learning.py).
#
#   python -B -I rd_learn_parts.py <ROOT> <out> --data=real --hash=<H> --model=mlp_pilot3 --size=57 --part=ood
#   python -B -I rd_learn_parts.py <ROOT> <out> --data=real --hash=<H> --model=mlp_pilot3 --size=57 --part=<i>/<k>   (i = 0..k-1)
#   python -B -I rd_learn_parts.py <ROOT> <out> --data=real --hash=<H> --model=mlp_pilot3 --size=57 --assemble=<k>
#        -> <out>/results_<model>_n<size>.json, in the format of results_<tag>.json (then: run_learn.py --stage=merge)
# The gate is that of rd_learn_ibm.py (it refuses to read the real data without the hashed declaration).
import json
import os
import runpy
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = {a.split("=")[0][2:]: a.split("=", 1)[1] for a in sys.argv[3:] if "=" in a}
MODEL, N = ARGS["model"], int(ARGS["size"])
NS = runpy.run_path(os.path.join(HERE, "rd_learn_ibm.py"), run_name="rd_learn_ibm")     # module level only: gate, loader
OUT = NS["OUT"]
PARTS = os.path.join(OUT, "parts")
SOURCES = ("emulated", "exact_control")          # names of the stored script: labels of the data source, DMRG labels


def setup():
    eta, n_in, D = NS["load"](N)
    Js = sorted(D)
    R = [j for j in Js if j >= NS["TRAIN_MIN"]]
    od = [j for j in Js if j in NS["OOD"]]
    Y = dict(emulated={j: D[j]["Z_lab"] for j in Js}, exact_control={j: D[j]["Z_ref"] for j in Js})
    return eta, D, Js, R, od, NS["fitters"](n_in)[MODEL], Y


def pname(tag):
    return os.path.join(PARTS, "f1_%s_n%d_%s.json" % (MODEL, N, tag))


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w") as f:
        json.dump(obj, f, indent=1, default=float)
    os.replace(path + ".tmp", path)


def main():
    eta, D, Js, R, od, fit, Y = setup()
    if "part" in ARGS and ARGS["part"] == "ood":
        res = {}
        for src in SOURCES:                                      # as main(): evaluate(fit, R, Y, od, D, eta, src)
            ev, _ = NS["evaluate"](fit, R, Y[src], od, D, eta, src)
            res[src] = dict(summary=NS["summarize"](ev["rows"]), levelZ=ev["levelZ"], levelM=ev["levelM"], rows=ev["rows"])
        dump(pname("ood"), res)
    elif "part" in ARGS:
        i, k = (int(x) for x in ARGS["part"].split("/"))
        res = {src: {} for src in SOURCES}
        for t in R[i::k]:
            for src in SOURCES:                                  # as main(): evaluate(fit, [j for j in R if j != t], Y, [t], ...)
                ev2, _ = NS["evaluate"](fit, [j for j in R if j != t], Y[src], [t], D, eta, src)
                res[src]["%.1f" % t] = [dict(r, levelZ=ev2["levelZ"], levelM=ev2["levelM"]) for r in ev2["rows"]]
            dump(pname("part%dof%d" % (i, k)), res)              # rewritten after every held-out coupling
            print("held out %.1f done" % t, flush=True)
    elif "assemble" in ARGS:
        k = int(ARGS["assemble"])
        ood = json.load(open(pname("ood")))
        held = {src: {} for src in SOURCES}
        for i in range(k):
            p = json.load(open(pname("part%dof%d" % (i, k))))
            for src in SOURCES:
                held[src].update(p[src])
        M = {}
        for src in SOURCES:
            missing = [t for t in R if "%.1f" % t not in held[src]]
            if missing:
                raise SystemExit("held-out couplings missing for %s: %s" % (src, missing))
            rows = [r for t in R for r in held[src]["%.1f" % t]]
            M["ood_" + src] = ood[src]
            M["indist_" + src] = dict(summary=NS["summarize"](rows), rows=rows)
        M["secs"] = None
        res = dict(alpha=NS["ALPHA"], ood=NS["OOD"], train_min=NS["TRAIN_MIN"], tau_rel=NS["TAU_REL"], assembled_from_parts=k,
                   sizes={str(N): dict(couplings=Js, train=R, ood=od, n_couplings=len(Js), models={MODEL: M})})
        dump(os.path.join(OUT, "results_%s_n%d.json" % (MODEL, N)), res)
        o = M["ood_emulated"]["summary"]; s = M["indist_emulated"]["summary"]
        print("assembled n=%d %s: test range covM truth %.2f, miss %.2f-%.2f tau | in distribution covM truth %.2f" % (
            N, MODEL, o["covM_truth"], *o["miss_ms_over_tau_range"], s["covM_truth"]))
    else:
        raise SystemExit("give --part=ood, --part=i/k or --assemble=k")


if __name__ == "__main__":
    main()
