# real_data / run_learn.py  (own code; 2026-11-12; task rd-code-learn)   ENTRY POINT, DECLARATION.md Sec. 7
#
#   python -B -I run_learn.py --hash=<SHA-256 of DECLARATION.md> --stage=<stage> [--root=<work/>] [--out=<dir>]
#                             [--sets=<S_sets.json>] [--converted=<dir>]
#
# REFUSES to read converted/ unless real_data/DECLARATION.sha256 exists, equals the SHA-256 of DECLARATION.md and
# equals --hash (exit code 3, nothing read). The seed of every random choice is the integer of the first eight hex
# digits of --hash. Stages (default out = real_data/out/learn):
#   f1_cheap   rd_learn_ibm.py: cubic in 1/Jz and nearest-neighbour null, both sizes            (about a minute)
#   f1_mlp57   rd_learn_ibm.py: the pilot perceptron, n = 57, test range and in distribution    (hours: see README)
#   f1_mlp115  the same at n = 115 (secondary)                                                  (hours)
#   f1_ibm57   rd_learn_ibm.py: the dataset paper's architecture 1, n = 57, test range only     (many hours)
#   merge      rd_learn_ibm.py --merge: results_<tag>.json -> results.json
#   prop2      rd_prop2_cubic.py: Proposition 2(a), (b) for the cubic (needs out/S_sets.json and its .sha256)
#   f2         the learner-independent floor (needs the sets file)
#   f3         the constructive test: 200 seeded splits, M1, M2, control M0, both scores, pass rule (needs the sets file)
#   rules      L1, L2, L3 from the stored outputs of f1_cheap (or merge) and prop2; the coupling 1.5 on its own line
#   cheap      f1_cheap, prop2, f2, f3, rules in this order
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import rd_common as rdc  # noqa: E402
import rd_f23 as f23  # noqa: E402

F1_JOBS = dict(f1_cheap=["--models=poly3_invJ,null_nn", "--tag=cheap"],
               f1_mlp57=["--models=mlp_pilot3", "--sizes=57", "--tag=mlp57"],
               f1_mlp115=["--models=mlp_pilot3", "--sizes=115", "--tag=mlp115"],
               f1_ibm57=["--models=ibm_arch1", "--sizes=57", "--tag=ibm57"])


def sub(script, args, log):
    cmd = [sys.executable, "-B", "-I", os.path.join(HERE, script)] + args
    with open(log, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    print("  %s %s -> exit %d (log %s)" % (script, " ".join(a for a in args if not a.startswith("--hash")), r.returncode, log))
    if r.returncode != 0:
        raise SystemExit("stage failed: see %s" % log)


def ms_data(n, gate, root, converted, sets):
    """m_s labels, truth (the authors' DMRG, Sec. 7), tau(x), and the intervals of the sets file, for one size."""
    rd = rdc.load_real(n, gate, root, converted)
    Js = rd.labelled()
    y = {J: rd.lab[J]["labels"]["m_s"] for J in Js}
    ystar = {J: rd.truth_authors[J]["labels"]["m_s"] for J in Js}
    tau = {J: rdc.TAU_REL * abs(ystar[J]) for J in Js}
    iv = sets["intervals"]
    exact = {J: (iv[J]["exact"]["lo"], iv[J]["exact"]["hi"]) for J in iv if iv[J]["exact"] is not None}
    lower_w = {J: (iv[J]["lower"]["width"] if (J in iv and iv[J]["lower"] is not None) else 0.0) for J in Js}   # no witness: width 0
    return dict(y=y, ystar=ystar, tau=tau, exact=exact, lower_w=lower_w, train_all=[J for J in Js if J >= rdc.TRAIN_MIN],
                lower_missing=[J for J in Js if J not in iv or iv[J]["lower"] is None])


def main(argv):
    arg = {a.split("=")[0][2:]: a.split("=", 1)[1] for a in argv if a.startswith("--") and "=" in a}
    if "hash" not in arg or "stage" not in arg:
        raise rdc.Refused("--hash=<SHA-256 of the hashed declaration> and --stage=<stage> are required.")
    gate = rdc.require_declaration_hash(rdc.RD, arg["hash"])          # nothing of converted/ is opened before this line
    seed0 = rdc.seed_from_hash(gate.sha)
    root = os.path.abspath(arg.get("root", rdc.ROOT_DEFAULT))
    out = os.path.abspath(arg.get("out", os.path.join(rdc.RD, "out", "learn")))
    sets_path = os.path.abspath(arg.get("sets", os.path.join(rdc.RD, "out", "S_sets.json")))
    os.makedirs(out, exist_ok=True)
    common = ["--data=real", "--hash=" + gate.sha] + (["--converted=" + arg["converted"]] if "converted" in arg else [])
    stages = ["f1_cheap", "prop2", "f2", "f3", "rules"] if arg["stage"] == "cheap" else [arg["stage"]]
    print("declaration %s | seed %d | stages %s" % (gate.sha, seed0, stages))
    for stage in stages:
        if stage in F1_JOBS:
            sub("rd_learn_ibm.py", [root, out] + common + F1_JOBS[stage], os.path.join(out, "stdout_%s.txt" % stage[3:]))
        elif stage == "merge":
            sub("rd_learn_ibm.py", [root, out, "--merge"], os.path.join(out, "stdout_merge.txt"))
        elif stage == "prop2":
            sub("rd_prop2_cubic.py", [root, out] + common + ["--sets=" + sets_path], os.path.join(out, "prop2_cubic_stdout.txt"))
        elif stage in ("f2", "f3"):
            res = dict(declaration_sha256=gate.sha, seed=seed0, sets_sha256=rdc.sha256_file(sets_path), sizes={})
            for n in (57, 115):
                sets = rdc.load_sets(sets_path, n, gate)
                d = ms_data(n, gate, root, arg.get("converted"), sets)
                if stage == "f2":
                    r = f23.floor_f2({J: d["lower_w"][J] for J in d["train_all"]}, d["tau"], d["train_all"])
                    r["lower_width_missing_taken_as_0"] = d["lower_missing"]
                    print("  f2 n = %d: floor w_(%d) of %d = %.5f = %.2f-%.2f tau at the test queries -> %s (readings agree: %s)" % (
                        n, r["k"], r["m"], r["floor"], min(r["floor_over_tau"][rdc.jkey(J)] for J in rdc.TEST),
                        max(r["floor_over_tau"][rdc.jkey(J)] for J in rdc.TEST), "HOLDS" if r["holds"] else "DOES NOT HOLD",
                        r["readings_agree"]))
                else:
                    r = f23.run_f3(n, sets, d, seed0)
                    r["sets_warnings"] = sets["warnings"]
                    print("  f3 n = %d: |S| = %d, |S_3/4| = %d, |S_1/2| = %d, primary %s -> %s" % (
                        n, len(sets["S"]), len(sets["S_3_4"]), len(sets["S_1_2"]), sets["S_p_name"], r["primary"]["outcome"]))
                    for name, s in r["sets"].items():
                        if s["status"] != "RUN":
                            print("     %-6s %s" % (name, s["status"])); continue
                        for m in f23.MODELS:
                            a = s["models"][m]
                            print("     %-6s %s: (W) %.3f of splits, (C) %.3f of pairs, 2q/tau %.3f-%.3f, largest miss %.3f tau" % (
                                name, m, a["frac_splits_W"], a["frac_pairs_C"], a["width_tau_min"], a["width_tau_max"], a["largest_miss_tau"]))
                res["sizes"][str(n)] = r
            if stage == "f3":
                res["decision"] = dict(res["sizes"]["57"]["primary"], note="n = 57, set S_p, both M1 and M2; everything else is secondary")
            with open(os.path.join(out, "f2_floor.json" if stage == "f2" else "f3_constructive.json"), "w") as f:
                json.dump(res, f, indent=1, default=float)
        elif stage == "rules":
            rp = os.path.join(out, "results.json")
            results = rdc.rj(rp if os.path.exists(rp) else os.path.join(out, "results_cheap.json"))
            prop2 = rdc.rj(os.path.join(out, "prop2_cubic.json"))
            res = dict(declaration_sha256=gate.sha, note="each of L1-L3 holds iff true at n = 57; n = 115 is reported", sizes={})
            for n in (57, 115):
                r = f23.f1_rules(results, prop2, n)
                rd = rdc.load_real(n, gate, root, arg.get("converted"))          # the coupling 1.5, on its own line
                R = [J for J in rd.labelled() if J >= rdc.TRAIN_MIN]
                y = np.array([rd.lab[J]["labels"]["m_s"] for J in R])
                apart = {}
                for J in rdc.APART:
                    if J in rd.lab and rd.lab[J]["has_labels"]:
                        a, c = f23.coef("M0", R, J)
                        t = rd.truth_authors[J]["labels"]["m_s"]; tau = rdc.TAU_REL * abs(t); p = c + float(a @ y)
                        qM = results["sizes"][str(n)]["models"]["poly3_invJ"]["ood_emulated"]["rows"][0]["qM"]
                        apart[rdc.jkey(J)] = dict(pred=p, truth=t, miss_tau=abs(p - t) / tau, standard_q=qM,
                                                  covered_by_standard_interval=bool(abs(p - t) <= qM),
                                                  width_2b_lower_tau=2 * r["L3"]["q_lo_all_training_labels"] / tau)
                r["apart"] = apart
                res["sizes"][str(n)] = r
                print("  n = %d: L1 %s %s | L2 %s | L3 %s (2q_lo = %.2f-%.2f tau)" % (
                    n, "HOLDS" if r["L1"]["holds"] else "DOES NOT HOLD", {k: round(v, 2) for k, v in r["L1"]["miss_tau"].items()},
                    "HOLDS" if r["L2"]["holds"] else "DOES NOT HOLD", "HOLDS" if r["L3"]["holds"] else "DOES NOT HOLD",
                    min(r["L3"]["width_tau"].values()), max(r["L3"]["width_tau"].values())))
            with open(os.path.join(out, "f1_rules.json"), "w") as f:
                json.dump(res, f, indent=1, default=float)
        else:
            raise SystemExit("unknown stage %s" % stage)


if __name__ == "__main__":
    main(sys.argv[1:])
