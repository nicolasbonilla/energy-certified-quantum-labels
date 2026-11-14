"""R10 math-map-logic, script 07: the other numbers of Sec. IV A / S12 from the own recomputation (01_rows.json):
accuracy law (C-D), intensivity (C-E), eps/Delta_in at certified rows, inner-outer agreement at E_lo, the map values
of Table S (w/tau), the inner-vs-outer threshold along the dataset line (direction of Fig. 2(a)).
Run: python -B 07_other_claims.py > 07_other_claims_out.txt"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mapcore as M

rows = json.load(open(os.path.join(HERE, "01_rows.json")))
R = {(d["n"], d["Jz"], d["label"]): d for d in rows.values()}
AV = ("m_s", "Czz_bar", "C2_bar")

print("== C-D accuracy law: de*_law / de*_out at the averaged rows with Jz >= 2.0")
vals = []
for k, d in sorted(R.items()):
    if k[2] in AV and k[1] >= 1.95 and d["de_star_law"] and d["de_star_out"]:
        vals.append((d["de_star_law"] / d["de_star_out"], k))
inside = [v for v in vals if 0.8 <= v[0] <= 1.25]
outside = [v for v in vals if not 0.8 <= v[0] <= 1.25]
print("rows %d ; inside [0.8, 1.25]: %d, range %.4f - %.4f ; outside: %d" % (len(vals), len(inside), min(inside)[0], max(inside)[0], len(outside)))
for v in sorted(outside):
    d = R[v[1]]
    print("   outside: %s ratio %.4f ; f_out = %.3f" % (v[1], v[0], d["f_out"]))
print("   rows with no law ratio (no eps_tau_out or no chi):", [(k) for k, d in sorted(R.items()) if k[2] in AV and k[1] >= 1.95 and not (d["de_star_law"] and d["de_star_out"])])
print("   min f_out among the outside rows: %.3f" % min(R[v[1]]["f_out"] for v in outside))
print("   law ratio with the INNER threshold at the same rows (de*_law/de*_in): range %.4f - %.4f" % (
    min(d["de_star_law"] / d["de_star_in"] for k, d in R.items() if k[2] in AV and k[1] >= 1.95 and d["de_star_law"] and d["de_star_in"]),
    max(d["de_star_law"] / d["de_star_in"] for k, d in R.items() if k[2] in AV and k[1] >= 1.95 and d["de_star_law"] and d["de_star_in"])))

print("\n== C-E intensivity: de*_out(115)/de*_out(57), Jz >= 2.0")
rat = []
for k, d in sorted(R.items()):
    if k[0] == 57 and k[1] >= 1.95 and (115, k[1], k[2]) in R:
        b = R[(115, k[1], k[2])]
        if d["de_star_out"] and b["de_star_out"]:
            rat.append((b["de_star_out"] / d["de_star_out"], k[1], k[2]))
av = [r for r in rat if r[2] in AV]
print("averages: %d rows, range %.4f - %.4f (min at %s, max at %s)" % (len(av), min(av)[0], max(av)[0], min(av)[1:], max(av)[1:]))
print("local:", [r for r in rat if r[2] not in AV], " 57/115 = %.5f" % (57 / 115))
print("the same below Jz = 2.0 (not part of the declared claim):", [("%.1f" % k[1], k[2], round(R[(115, k[1], k[2])]["de_star_out"] / d["de_star_out"], 3))
      for k, d in sorted(R.items()) if k[0] == 57 and k[1] < 1.95 and (115, k[1], k[2]) in R and d["de_star_out"] and R[(115, k[1], k[2])]["de_star_out"]])
inn = [R[(115, k[1], k[2])]["de_star_in"] / d["de_star_in"] for k, d in R.items() if k[0] == 57 and k[1] >= 1.95 and k[2] in AV
       and (115, k[1], k[2]) in R and d["de_star_in"] and R[(115, k[1], k[2])]["de_star_in"]]
print("with the inner thresholds, Jz >= 2.0 averages: %d rows, range %.4f - %.4f" % (len(inn), min(inn), max(inn)))

print("\n== eps_dig / Delta_in at the certified rows (in-sector gap from the R2 reference where it exists)")
mx = []
for k, d in sorted(R.items()):
    if d["status"] == "CERTIFIED":
        t = M.thresholds(k[0], k[1])
        g = t["gaps"].get("in_sector")
        if g:
            mx.append((t["eps_dig"] / g, k))
        else:
            mx.append((None, k))
have = [m for m in mx if m[0] is not None]
print("certified rows: %d ; with a recorded in-sector gap: %d ; max eps_dig/Delta_in = %.4f at %s ; max at n = 57: %.4f at %s" % (
    len(mx), len(have), max(have)[0], max(have)[1], max(m for m in have if m[1][0] == 57)[0], max(m for m in have if m[1][0] == 57)[1]))
print("   certified rows without an in-sector gap reference:", [m[1] for m in mx if m[0] is None])
for k in ((57, 1.6, "m_s"), (115, 1.6, "m_s")):
    t = M.thresholds(k[0], k[1])
    print("   eps_dig/Delta_in at %s: %.4f" % (k, t["eps_dig"] / t["gaps"]["in_sector"]))

print("\n== inner vs outer width at E_lo, averaged rows with Jz >= 1.6, n = 57")
dif = [(d["at_lo"]["w_out"] / d["at_lo"]["w_in"] - 1, k) for k, d in R.items() if k[0] == 57 and k[2] in AV and k[1] >= 1.55]
print("max (w_out - w_in)/w_in at E_lo: %.4f at %s ; n = 115: %.4f at %s" % (max(dif)[0], max(dif)[1],
      max((d["at_lo"]["w_out"] / d["at_lo"]["w_in"] - 1, k) for k, d in R.items() if k[0] == 115 and k[2] in AV and k[1] >= 1.55)[0],
      max((d["at_lo"]["w_out"] / d["at_lo"]["w_in"] - 1, k) for k, d in R.items() if k[0] == 115 and k[2] in AV and k[1] >= 1.55)[1]))

print("\n== direction of main Fig. 2(a): the colour and the teal contour are the INNER width. Inner vs outer thresholds (m_s, n = 57)")
for J in (1.1, 1.4, 1.6, 2.0, 3.0, 3.2, 3.4, 4.0, 4.5, 5.0, 5.5, 6.0):
    d = R[(57, J, "m_s")]
    print("   Jz=%.1f de*_in=%.4e de*_out=%.4e in/out = %.4f ; at the dataset's energy: w_in/tau = %.4f, w_out/tau = %.4f" % (
        J, d["de_star_in"], d["de_star_out"], d["de_star_in"] / d["de_star_out"],
        (d["at_dig"]["inner"][1] - d["at_dig"]["inner"][0]) / d["tau"], d["at_dig"]["w_out"] / d["tau"]))

print("\n== Table S (safe-to-train summary), own values")
for n in (57, 115):
    for lab in ("m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop"):
        a, b = R.get((n, 1.2, lab)), R.get((n, 1.6, lab))
        last = R.get((n, 6.0, lab)) or R.get((n, 4.0, lab))
        if not last:
            continue
        print("   n=%3d %-10s w_in(lo)/tau at 1.2: %s ; at 1.6: %s ; w_out(E_dig)/tau at the last point (Jz=%.1f): %.3f" % (
            n, lab, ("%.2f" % (a["at_lo"]["w_in"] / a["tau"])) if a else "--", ("%.2f" % (b["at_lo"]["w_in"] / b["tau"])) if b else "--",
            last["Jz"], last["at_dig"]["w_out"] / last["tau"]))
d = R[(57, 1.2, "m_s")]
print("   m_s width at the OOD point 1.2 (n=57): w_in(E_lo) = %.4f ; window at E_dig (inner) = %.4f" % (d["at_lo"]["w_in"], d["at_dig"]["inner"][1] - d["at_dig"]["inner"][0]))
d = R[(57, 1.6, "m_s")]
print("   m_s at 1.6 (n=57): inner window at E_lo [%.4f, %.4f] ; at E_dig [%.4f, %.4f] (w = %.4f = %.2f tau) ; outer at E_up [%.4f, %.4f] (%.2f tau)" % (
    d["at_lo"]["inner"][0], d["at_lo"]["inner"][1], d["at_dig"]["inner"][0], d["at_dig"]["inner"][1],
    d["at_dig"]["inner"][1] - d["at_dig"]["inner"][0], (d["at_dig"]["inner"][1] - d["at_dig"]["inner"][0]) / d["tau"],
    d["at_up"]["outer"][0], d["at_up"]["outer"][1], d["at_up"]["w_out"] / d["tau"]))
# local reach quoted in S12: field witnesses reach 50-62 % of the range at n = 57, Jz = 1.6
print("   local labels at (57, 1.6): w_in(E_lo)/2 =", {lab: round(R[(57, 1.6, lab)]["at_lo"]["w_in"] / 2, 4) for lab in ("Z_bulk", "Z_boundary", "Czz_edge", "Z_loop")})
