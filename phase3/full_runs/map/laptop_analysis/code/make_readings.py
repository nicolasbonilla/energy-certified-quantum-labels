"""Build code/readings_declared.json from the two readings (laptop; fixed before DECLARATION.md is hashed).
  python -I make_readings.py <digitization/readings.json> <out.json>
r1, gap1 = reading 1 (pilot method re-run at every Jz = k/10; primary, used for every threshold); r2, gap2 = reading 2
(digitize2.py; used only in the analysis: map under reading 2, agreement, robustness). Gap: the n = 57 marker where
visible (Jz <= 1.6; reading 2 cannot read it at 1.5, not a grid point), otherwise the n = 115 marker (the hidden-marker convention of
the pilots); eps = r * gap (energy error, J)."""
import json
import sys


def main(src, outp):
    d = json.load(open(src))
    P = d["points"]
    out = dict(r1={}, gap1={}, eps1={}, r2={}, gap2={}, eps2={}, note=__doc__)
    for n in (57, 115):
        for k in range(50):
            J = round(1.1 + 0.1 * k, 1)
            key = "%d_%.1f" % (n, J)
            g57 = P.get("gap_n57_%.1f" % J, {})
            g115 = P.get("gap_n115_%.1f" % J, {})
            if n == 57 and J <= 1.65 and g57.get("r1"):
                out["gap1"][key] = g57["r1"]
                out["gap2"][key] = g57["r2"] if (g57.get("r2") and abs(J - 1.5) > 0.01) else g115.get("r2")
            else:
                out["gap1"][key] = g115["r1"]
                out["gap2"][key] = g115["r2"]
            if J >= 1.55:
                r = P["ratio_n%d_%.1f" % (n, J)]
                out["r1"][key] = r["r1"]
                out["r2"][key] = r["r2"]
                out["eps1"][key] = r["r1"] * out["gap1"][key]
                out["eps2"][key] = (r["r2"] * out["gap2"][key]) if (r["r2"] and out["gap2"][key]) else None
    json.dump(out, open(outp, "w"), indent=1, sort_keys=True)
    for key in ("57_1.6", "57_3.3", "57_4.0", "115_1.6", "115_4.0", "57_1.2"):
        print(key, {k: out[k].get(key) for k in ("r1", "gap1", "eps1", "r2", "gap2", "eps2")})


if __name__ == "__main__":
    main(*sys.argv[1:])
