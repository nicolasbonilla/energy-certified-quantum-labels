"""Convention check of the Huang et al. data files (arithmetic on stored numbers only; no diagonalization, no DMRG).

  python -I check_data.py <data_dir> [<all_data_dir>]
For every instance found: number of couplings = number of bonds of square_lattice(L, 5) with open boundaries; all
couplings in [0, 2]; the stored energy equals sum_b J_b (XX + YY + ZZ)_b / 2 with the ITensors bond order (and the
residual for three alternative orders); XX = YY = ZZ (SU(2)); XX symmetric with unit diagonal.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lattice as LT  # noqa: E402


def alt_orders(L):
    W = LT.W
    hv = [(s, s + W) for s in range(L * W) if divmod(s, W)[0] < L - 1] + \
         [(s, s + 1) for s in range(L * W) if divmod(s, W)[1] < W - 1]
    nh = (L - 1) * W
    vh = hv[nh:] + hv[:nh]
    return dict(itensor=LT.bonds(L), h_then_v=hv, v_then_h=vh)


def check_dir(d, label):
    files = sorted(glob.glob(os.path.join(d, "heisenberg_*x5_id*_couplings.txt")))
    rows = []
    for f in files:
        m = re.search(r"heisenberg_(\d+)x5_id(\d+)_couplings", f)
        L, k = int(m.group(1)), int(m.group(2))
        try:
            I = LT.load_instance(d, L, k)
        except (OSError, AssertionError) as e:
            rows.append((L, k, "ERROR %s" % e))
            continue
        n = I["n"]
        XX, YY, ZZ = I["XX"], I["YY"], I["ZZ"]
        res = {}
        for name, B in alt_orders(L).items():
            Ec = sum(c * (XX[i][j] + YY[i][j] + ZZ[i][j]) for (i, j), c in zip(B, I["J"])) / 2.0
            res[name] = Ec - I["E_file"]
        dxy = max(abs(XX[i][j] - YY[i][j]) for i in range(n) for j in range(n))
        dxz = max(abs(XX[i][j] - ZZ[i][j]) for i in range(n) for j in range(n))
        sym = max(abs(XX[i][j] - XX[j][i]) for i in range(n) for j in range(n))
        dia = max(abs(XX[i][i] - 1) for i in range(n))
        rows.append((L, k, n, len(I["J"]), min(I["J"]), max(I["J"]), I["E_file"], res, dxy, dxz, sym, dia))
    print("== %s: %d instances" % (label, len(rows)))
    worst = dict(itensor=0.0, dxz=0.0)
    for r in rows:
        if isinstance(r[2], str):
            print(r)
            continue
        L, k, n, nJ, jmin, jmax, E, res, dxy, dxz, sym, dia = r
        worst["itensor"] = max(worst["itensor"], abs(res["itensor"]) / abs(E))
        worst["dxz"] = max(worst["dxz"], dxz)
        if label == "chosen":
            print("L=%d k=%d n=%d nJ=%d J in [%.4f, %.4f] E_file=%.10f  sum J(XX+YY+ZZ)/2 - E_file: itensor %.2e, "
                  "h_then_v %.2e, v_then_h %.2e | max|XX-YY| %.1e max|XX-ZZ| %.1e sym %.1e |diag-1| %.1e" % (
                      L, k, n, nJ, jmin, jmax, E, res["itensor"], res["h_then_v"], res["v_then_h"], dxy, dxz, sym, dia))
    by = {}
    for r in rows:
        if not isinstance(r[2], str):
            by.setdefault(r[0], []).append(r)
    for L, rs in sorted(by.items()):
        print("L=%d: %d instances, max rel |E_itensor - E_file| = %.2e, max |XX-ZZ| = %.2e, J range [%.4f, %.4f]" % (
            L, len(rs), max(abs(r[7]["itensor"]) / abs(r[6]) for r in rs), max(r[9] for r in rs),
            min(r[4] for r in rs), max(r[5] for r in rs)))
    print("worst over all: rel dE (itensor order) %.2e, max |XX-ZZ| %.2e" % (worst["itensor"], worst["dxz"]))


if __name__ == "__main__":
    check_dir(sys.argv[1], "chosen")
    if len(sys.argv) > 2:
        check_dir(sys.argv[2], "all instances in the repository")
