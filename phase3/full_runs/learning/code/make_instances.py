"""Draw the declared instance sets (laptop, before the declaration hash; numbers only, no physics).

  python make_instances.py <code_dir>
  * instances_ood.json  : the out-of-distribution set O: 40 instances of the 4 x 5 lattice with every coupling
                          J_b ~ U[1, 2] i.i.d. (the held-out region [1, 2]^31 of coupling space; the benchmark draws
                          J_b ~ U[0, 2], so none of its instances lies in this region), seed 20261102.
  * instances_T3.json / instances_U3.json : toy sets on the 3 x 5 lattice (n = 15) for the laptop dry run only
                          (100 instances with U[0, 2], 40 with U[1, 2]; seeds 777, 778). Never used for any result.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lattice as LT  # noqa: E402


def draw(L, N, lo, hi, seed):
    rng = np.random.default_rng(seed)
    nb = len(LT.bonds(L))
    return [[float(x) for x in rng.uniform(lo, hi, size=nb)] for _ in range(N)]


def main(d):
    sets = {
        "instances_ood.json": dict(L=4, N=40, lo=1.0, hi=2.0, seed=20261102,
                                   note="OOD set O: J_b ~ U[1,2] iid on the 4x5 lattice (held-out region [1,2]^31)"),
        "instances_T3.json": dict(L=3, N=100, lo=0.0, hi=2.0, seed=777, note="toy ID set (dry run only)"),
        "instances_U3.json": dict(L=3, N=40, lo=1.0, hi=2.0, seed=778, note="toy OOD set (dry run only)"),
    }
    for fn, s in sets.items():
        J = draw(s["L"], s["N"], s["lo"], s["hi"], s["seed"])
        obj = dict(s, J=J, generator="numpy.random.default_rng(seed).uniform(lo, hi, size=n_bonds) per instance, "
                                      "instances drawn in order k = 1..N", numpy=np.__version__)
        with open(os.path.join(d, fn), "w") as f:
            json.dump(obj, f, indent=0)
        print(fn, s["N"], "instances, L =", s["L"], "bonds =", len(J[0]), "J range", min(map(min, J)), max(map(max, J)))


if __name__ == "__main__":
    main(sys.argv[1])
