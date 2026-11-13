"""Gate G4 (separate process, TeNPy not importable): re-evaluate the headline witness components of every DMRG chain
from their stored .npz with indep_eval_h only, and check energies, labels, norms, sector, and that every headline
mixture lies at or below its energy.

  python g4.py <root>        writes <root>/out/g4/g4_check.json
Headline components: the hull components of the inner extremes at E0 + n*de for de in {1e-3, 1e-2} and at the inner
eps_tau, for every DMRG chain, plus the chi 384 reference ground state of every instance.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hull  # noqa: E402
import chain as CH  # noqa: E402
import lattice as LT  # noqa: E402
import indep_eval_h as IE  # noqa: E402


def main(root):
    import importlib.util
    O = os.path.join(root, "out")
    res = dict(tenpy_importable=importlib.util.find_spec("tenpy") is not None, checked=[], missing=[], fails=[])
    cache = {}
    for f in sorted(glob.glob(os.path.join(O, "chains", "*.json"))):
        ch = json.load(open(f))
        L, k, n = ch["L"], ch["k"], ch["n"]
        I = LT.load_instance(os.path.join(root, "data_huang"), L, k)
        P, Wt, S, ob = LT.label_pairs(L, ch["label"])
        pool = CH.pool_of(ch["E0"], ch["o_GS"], ch["points"])
        Es = [ch["E0"] + n * d for d in (1e-3, 1e-2)]
        if ch.get("eps_tau_in"):
            Es.append(ch["E0"] + ch["eps_tau_in"])
        sids = {}
        for E in Es:
            for sign in (+1, -1):
                val, comps = hull.extreme(pool, E, sign)
                mixE = hull.mix_energy(comps)
                if mixE > E + 1e-9:
                    res["fails"].append(dict(chain=os.path.basename(f), E=E, mixE=mixE, why="mixture above E"))
                for (sid, w, Ea, oa) in comps:
                    if sid != "gs":
                        p = ch["points"][int(sid[1:])]
                        sids[p["sid"]] = p
        for sid, p in sids.items():
            npz = os.path.join(root, "mps", sid + ".npz")
            if not os.path.exists(npz):
                res["missing"].append(sid)
                continue
            if sid not in cache:
                Ts, meta = IE.load_npz(npz)
                cache[sid] = IE.evaluate(Ts, meta["sz_basis"], I["bonds"], I["J"], P)
            r = cache[sid]
            o = sum(w_ * r["C"]["%d_%d" % tuple(sorted(pp))] for pp, w_ in zip(P, Wt)) / S
            row = dict(sid=sid, chain=os.path.basename(f), dE=abs(r["E"] - p["E"]), dO=abs(o - p["o"]),
                       sz_var=r["sz_var"], norm=r["norm"])
            res["checked"].append(row)
            if row["dE"] > 1e-8 or row["dO"] > 1e-8 or abs(r["sz_var"]) > 1e-10:
                res["fails"].append(dict(row, why="value mismatch or out of sector"))
    for f in sorted(glob.glob(os.path.join(O, "refs", "ref_*.json"))):
        d = json.load(open(f))
        I = LT.load_instance(os.path.join(root, "data_huang"), d["L"], d["k"])
        sid = "L%dk%d_R1_chi384" % (d["L"], d["k"])
        npz = os.path.join(root, "mps", sid + ".npz")
        if not os.path.exists(npz):
            res["missing"].append(sid)
            continue
        Ts, meta = IE.load_npz(npz)
        r = IE.evaluate(Ts, meta["sz_basis"], I["bonds"], I["J"], [])
        row = dict(sid=sid, dE=abs(r["E"] - d["E0"]), dO=0.0, sz_var=r["sz_var"], norm=r["norm"])
        res["checked"].append(row)
        if row["dE"] > 1e-8 or abs(r["sz_var"]) > 1e-10:
            res["fails"].append(dict(row, why="reference mismatch"))
    res["n_checked"] = len(res["checked"])
    res["max_dE"] = max([c["dE"] for c in res["checked"]] + [0.0])
    res["max_dO"] = max([c["dO"] for c in res["checked"]] + [0.0])
    res["passed"] = (not res["fails"]) and (not res["missing"]) and not res["tenpy_importable"]
    os.makedirs(os.path.join(O, "g4"), exist_ok=True)
    with open(os.path.join(O, "g4", "g4_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: res[k] for k in ("tenpy_importable", "n_checked", "max_dE", "max_dO", "passed")}),
          "fails", len(res["fails"]), "missing", len(res["missing"]))


if __name__ == "__main__":
    main(sys.argv[1])
