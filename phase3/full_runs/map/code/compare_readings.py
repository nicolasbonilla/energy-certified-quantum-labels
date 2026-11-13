"""Combine and compare the two readings of IBM 2606.15983's energy figures (laptop, numbers only).

  python -I compare_readings.py <reading1_fig2_raw.txt> <reading1_fig4_raw.txt> <reading2_raw.json> <out.json>
Reading 1 = the pilot's method (pilot/PRIOR_ART_CHECK.md §3, script copied as digitize1_pilot_copy.py, same
calibration), re-run at every Jz = k/10. Reading 2 = digitize2.py (independent calibration and marker location).
Output: per (quantity, n, Jz) both readings, their ratio, and summary statistics; Supp. Fig. 9 (same data as Fig. 2
left, 'rand. flip (basis opt.)') is compared with Fig. 2 as a figure-to-figure check; points where Supp. Fig. 9's
reading differs by more than a factor 2 are reported as confusions with another series of the same colour.
"""
import ast
import json
import sys
import numpy as np


def parse_r1(path):
    out = {}
    for line in open(path):
        name, rest = line.split(" ", 1)
        out.setdefault(name, []).append(dict(ast.literal_eval(rest.strip())))
    return out


def stats(pairs):
    q = np.array([b / a - 1.0 for a, b in pairs])
    return dict(n=len(q), median_rel=float(np.median(q)), mean_abs_rel=float(np.mean(np.abs(q))),
                max_abs_rel=float(np.max(np.abs(q))) if len(q) else None,
                n_within_5pct=int(np.sum(np.abs(q) <= 0.05)), n_within_10pct=int(np.sum(np.abs(q) <= 0.10)))


def main(r1f2, r1f4, r2p, outp):
    A = parse_r1(r1f2)                    # 'purple' (n = 115) and 'green' (n = 57) dicts Jz -> value
    B = parse_r1(r1f4)
    R2 = json.load(open(r2p))
    r1 = {("ratio", 115): A["purple"][0], ("ratio", 57): A["green"][0],
          ("gap", 115): B["purple"][0], ("gap", 57): B["green"][0]}
    key2 = {("ratio", 57): ("fig2_left", "ratio_n57"), ("ratio", 115): ("fig2_left", "ratio_n115"),
            ("gap", 115): ("fig4_left", "gap_n115"), ("gap", 57): ("fig4_left", "gap_n57")}
    table = {}
    summ = {}
    for (q, n), d1 in r1.items():
        f, s = key2[(q, n)]
        pts2 = R2[f][s]["points"]
        pairs = []
        for J, v1 in sorted(d1.items()):
            v2 = pts2.get("%.1f" % J, {}).get("value")
            table["%s_n%d_%.1f" % (q, n, J)] = dict(r1=v1, r2=v2, rel=(v2 / v1 - 1.0) if (v1 and v2) else None)
            if v1 and v2:
                pairs.append((v1, v2))
        summ["%s_n%d" % (q, n)] = stats(pairs)
    # Supp. Fig. 9 against Fig. 2 (reading 2 both), same data
    supp = {}
    for n in (57, 115):
        f2 = R2["fig2_left"]["ratio_n%d" % n]["points"]
        s9 = R2["supp_fig9"]["ratio_n%d" % n]["points"]
        pairs, conf = [], []
        for J in f2:
            a, b = f2[J].get("value"), s9.get(J, {}).get("value")
            if a and b:
                if b / a > 2 or b / a < 0.5:
                    conf.append(J)
                else:
                    pairs.append((a, b))
        supp["n%d" % n] = dict(stats=stats(pairs), confusions=conf,
                               unreadable=[J for J in f2 if not s9.get(J, {}).get("value")])
    # energy error per site, both readings, training points
    de = {}
    for n in (57, 115):
        for J in [round(1.6 + 0.1 * k, 1) for k in range(45)]:
            r_1 = r1[("ratio", n)].get(J)
            g_1 = r1[("gap", 115)].get(J) if (n == 115 or J > 1.65) else r1[("gap", 57)].get(J)
            p2r = R2["fig2_left"]["ratio_n%d" % n]["points"].get("%.1f" % J, {}).get("value")
            g2s = "gap_n115" if (n == 115 or J > 1.65) else "gap_n57"
            p2g = R2["fig4_left"][g2s]["points"].get("%.1f" % J, {}).get("value")
            de["%d_%.1f" % (n, J)] = dict(r1=r_1, gap1=g_1, eps1=(r_1 * g_1) if (r_1 and g_1) else None,
                                          r2=p2r, gap2=p2g, eps2=(p2r * p2g) if (p2r and p2g) else None)
            e = de["%d_%.1f" % (n, J)]
            e["eps2_over_eps1"] = (e["eps2"] / e["eps1"]) if (e["eps1"] and e["eps2"]) else None
    out = dict(points=table, summary=summ, supp_vs_fig2=supp, eps=de,
               calib2={k: R2[k]["calib"] for k in R2})
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps(dict(summary=summ, supp={k: dict(v["stats"], confusions=v["confusions"],
                                                       unreadable=v["unreadable"]) for k, v in supp.items()}),
                     indent=1))
    q = [v["eps2_over_eps1"] for v in de.values() if v["eps2_over_eps1"]]
    print("eps2/eps1: n=%d median %.4f min %.4f max %.4f" % (len(q), np.median(q), min(q), max(q)))


if __name__ == "__main__":
    main(*sys.argv[1:])
