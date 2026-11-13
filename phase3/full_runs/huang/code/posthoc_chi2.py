"""POST-HOC diagnostic (DEVIATIONS 8; not a declared quantity): the rule's delta e* with chi taken from the second chain
point of each side (lambda ~ 0.3-0.5, where the label shift is ~10x the lambda_0 shift), instead of lambda_0, for the
local labels of the DMRG chains (and, for comparison, the exact n = 20 chains).
  python -I posthoc_chi2.py <root_with_out> <summary_huang.json>
chi_2 = (o_+(lam_2+) - o_-(lam_2-)) / (lam_2+ + lam_2-);  de*_law2 = S tau^2 / (8 chi_2 n)."""
import glob, json, os, sys
root, summ = sys.argv[1], json.load(open(sys.argv[2]))
rows = {(r["L"], r["k"], r["label"], r["method"]): r for r in summ["rows"] if not r.get("alias_of")}
out = []
for sub, meth in (("chains", "DMRG"), (os.path.join("ed", "chains"), "ED")):
    for f in sorted(glob.glob(os.path.join(root, "out", sub, "*.json"))):
        ch = json.load(open(f))
        if ch["label"] not in ("Ccent", "Cfar", "Cfix"):
            continue
        P = sorted([p for p in ch["points"] if p["sign"] > 0], key=lambda p: p["lam"])
        M = sorted([p for p in ch["points"] if p["sign"] < 0], key=lambda p: p["lam"])
        if len(P) < 2 or len(M) < 2:
            continue
        chi2 = (P[1]["o"] - M[1]["o"]) / (P[1]["lam"] + M[1]["lam"])
        law2 = ch["S"] * ch["tau"] ** 2 / (8 * chi2) / ch["n"]
        r = rows[(ch["L"], ch["k"], ch["label"], meth)]["tau"]
        out.append(dict(L=ch["L"], k=ch["k"], label=ch["label"], method=meth, lam2=(P[1]["lam"], M[1]["lam"]),
                        eps_lam0=(P[0]["eps"], M[0]["eps"]), chi_two=ch["chi_two"], chi_2=chi2, de_law0=r["de_law"],
                        de_law2=law2, de_in=r["de_in"], de_out=r["de_out"],
                        law2_inside_band=(r["de_out"] <= law2 <= r["de_in"]) if (r["de_in"] and r["de_out"]) else None,
                        law2_over_out=law2 / r["de_out"] if r["de_out"] else None))
for o in out:
    print("(%d,%d) %-5s %-4s lam2=(%.3f,%.3f) eps(lam0)=(%.2e,%.2e) chi_two=%.4f chi_2=%.4f de_law0=%.3e de_law2=%.3e band=[%.3e, %.3e] inside=%s law2/out=%.3f" % (
        o["L"], o["k"], o["label"], o["method"], o["lam2"][0], o["lam2"][1], o["eps_lam0"][0], o["eps_lam0"][1], o["chi_two"],
        o["chi_2"], o["de_law0"], o["de_law2"], o["de_out"], o["de_in"], o["law2_inside_band"], o["law2_over_out"]))
json.dump(out, open(os.path.join(os.path.dirname(sys.argv[2]), "posthoc_chi2.json"), "w"), indent=1)
