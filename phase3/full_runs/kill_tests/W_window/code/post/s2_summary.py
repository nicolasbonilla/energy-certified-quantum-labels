"""s2_summary.py -- post-hoc read of test W (not declared; asked by paper/reviews/R6_fresh.md, item S11).

Reads out_20261107T190617Z/out/analysis.json (J2 = 0, O_ms table, field S2 = <S^2> of each stored state, computed on the
VM by analyze_w.py) and writes ../../s2_summary.json with, per method, the range of <S^2> over all states and over the
states that bracket the five declared test points (from the last state below the smallest target to the first state
above the largest target, in energy error per site). Nothing is recomputed from wave functions; no rule is touched.

    python -I s2_summary.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(W, "out_20261107T190617Z", "out", "analysis.json")
OUT = os.path.join(W, "s2_summary.json")

d = json.load(open(SRC, encoding="utf-8"))
blk = d["J2=0"]
targets = d["targets"]
lo, hi = min(targets), max(targets)
res = {"source": "out_20261107T190617Z/out/analysis.json", "J2": 0, "label": "ms (<M_s.M_s>/n^2)",
       "gs_S2": blk["gs"]["S2"], "targets_de": targets, "methods": {}}
for meth in ("MPS", "ViT", "Krylov"):
    rows = sorted([r for r in blk["obs"]["ms"]["table"] if r["method"] == meth], key=lambda r: r["de"])
    below = [r for r in rows if r["de"] < lo]
    above = [r for r in rows if r["de"] > hi]
    de_min = below[-1]["de"] if below else rows[0]["de"]
    de_max = above[0]["de"] if above else rows[-1]["de"]
    br = [r for r in rows if de_min <= r["de"] <= de_max]
    res["methods"][meth] = {
        "n_states": len(rows),
        "S2_all": [min(r["S2"] for r in rows), max(r["S2"] for r in rows)],
        "bracket_de": [de_min, de_max],
        "n_bracket": len(br),
        "S2_bracket": [min(r["S2"] for r in br), max(r["S2"] for r in br)] if br else None,
        "all_err_positive": all(r["err"] > 0 for r in rows),
    }
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
print(json.dumps(res, indent=1))
