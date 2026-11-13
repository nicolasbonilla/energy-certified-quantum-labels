# hostile-B (R11, 2026-11-13): independent recomputation of the tests of the bias on the public labels (main.tex
# Sec. IV B and V, supplement S18) and of the numbers attributed to the dataset paper, from the converted public data
# (authors' DMRG as the reference at every coupling). Own code; imports nothing from the project.
# usage: python -B -I -X utf8 recompute_bias.py <real_data_dir>
import json, math, sys

import numpy as np

RD = sys.argv[1]


def jk(J):
    return "%.1f" % J


def rank(a):
    a = np.asarray(a, float); o = np.argsort(a, kind="mergesort"); r = np.empty(len(a)); i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[o[j + 1]] == a[o[i]]:
            j += 1
        r[o[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return r


def spearman(x, y):
    rx = rank(x); ry = rank(y); rx -= rx.mean(); ry -= ry.mean()
    return float(rx @ ry / math.sqrt((rx @ rx) * (ry @ ry)))


def main():
    C19 = json.load(open("%s/out/n19/n19_curves.json" % RD, encoding="utf-8"))
    lm = json.load(open("%s/converted/lattice_maps.json" % RD, encoding="utf-8"))["maps"]
    tot = 0; pos = 0
    for n in (57, 115):
        print("=" * 30, "n =", n)
        d = json.load(open("%s/converted/real_n%d.json" % (RD, n), encoding="utf-8"))
        col = np.array(lm[str(n)]["colour_with_node0_as_1"], float); eta = np.where(col > 0.5, 1.0, -1.0)
        edges = set(tuple(sorted(e)) for e in lm[str(n)]["edges_sorted_unique"])
        Js = [round(1.1 + 0.1 * i, 1) for i in range(50)]
        M0 = float(eta.sum())
        fam_cnt = {f: [0, 0] for f in ("sites", "edges", "second", "loops")}
        Dfam = {f: [] for f in fam_cnt}; exc = []
        de = {}; dms = {}; ms_gs = {}; defc = []; ratio_first = []; relZ = {}; eratio = {}; relC = []; relL = []
        for J in Js:
            a = d["skqd_random_flip"][jk(J)]; b = d["dmrg"][jk(J)]
            Zp = np.array(a["z_basis_opt"], float); Zg = np.array(b["z"], float)
            # sites
            t = (Zp - Zg) / (eta - Zg); tau = 0.06 * np.abs(Zg)
            fam_cnt["sites"][0] += int((t > 0).sum()); fam_cnt["sites"][1] += len(t)
            Dfam["sites"].append(float(np.mean(np.abs(Zp - Zg) / tau)))
            for i in np.where(t <= 0)[0]:
                exc.append((n, J, "site %d" % i, float(t[i]), float(abs(Zp[i] - Zg[i]) / tau[i]), float(Zp[i]), float(Zg[i])))
            relZ[J] = 100 * float(np.mean(np.abs(Zp - Zg) / np.abs(Zg)))
            # pairs
            pp = {tuple(sorted(p)): v for p, v in zip(a["2_nn_corr_pairs_zz_basis_opt"], a["2_nn_corr_funcs_zz_basis_opt"])}
            pg = {tuple(sorted(p)): v for p, v in zip(b["2_nn_corr_pairs"], b["2_nn_corr_funcs_zz"])}
            assert set(pp) == set(pg), (n, J)
            De = []; Ds = []; rel = []
            for p in pp:
                g = pg[p]; v = pp[p]; fam = "edges" if p in edges else "second"; neel = -1.0 if fam == "edges" else 1.0
                tt = (v - g) / (neel - g)
                fam_cnt[fam][0] += tt > 0; fam_cnt[fam][1] += 1
                (De if fam == "edges" else Ds).append(abs(v - g) / (0.06 * abs(g))); rel.append(abs(v - g) / abs(g))
                if tt <= 0:
                    exc.append((n, J, "%s %s" % (fam, p), float(tt), float(abs(v - g) / (0.06 * abs(g))), v, g))
            Dfam["edges"].append(float(np.mean(De))); Dfam["second"].append(float(np.mean(Ds))); relC.append(100 * float(np.mean(rel)))
            # loops
            Lp = np.array(a["z_loop"], float); Lg = np.array(b["z_loop"], float)
            assert a["z_loop_sites"] == b["z_loop_sites"]
            tl = (Lp - Lg) / (1.0 - Lg)
            fam_cnt["loops"][0] += int((tl > 0).sum()); fam_cnt["loops"][1] += len(tl)
            Dfam["loops"].append(float(np.mean(np.abs(Lp - Lg) / (0.06 * np.abs(Lg))))); relL.append(100 * float(np.mean(np.abs(Lp - Lg) / np.abs(Lg))))
            for i in np.where(tl <= 0)[0]:
                exc.append((n, J, "loop %d" % i, float(tl[i]), float(abs(Lp[i] - Lg[i]) / (0.06 * abs(Lg[i]))), float(Lp[i]), float(Lg[i])))
            # energies, m_s
            E = a["final_global_energy"]; E0 = b["ground_state_energy"]; E1 = b["e1"]; Ef = a["ground_state_energy"]
            de[J] = (E - E0) / n; ms_gs[J] = float(eta @ Zg / n); dms[J] = float(eta @ Zp / n) - ms_gs[J]
            defc.append(M0 - float(Zp.sum())); ratio_first.append((Ef - E0) / (E - E0)); eratio[J] = (E - E0) / (E1 - E0)
        for f, (p, t_) in fam_cnt.items():
            print("sign %-7s: %d of %d pairs with t>0 (F=%.6f); Spearman(D, Jz) = %.5f" % (f, p, t_, p / t_, spearman(Dfam[f], Js)))
            tot += t_; pos += p
        for e in exc:
            print("   exception: n=%d Jz=%.1f %s t=%.4f |err|/tau=%.3f pub=%.4f ref=%.4f" % e)
        print("sum of published site magnetizations below M0=%g at %d of 50 couplings; deficit %.4f to %.4f" % (
            M0, sum(x > 0 for x in defc), min(defc), max(defc)))
        print("energy error per site, first stage over final: %.2f to %.2f (median %.2f)" % (min(ratio_first), max(ratio_first), float(np.median(ratio_first))))
        print("dataset paper Eq.(15) Delta Z (%%) at Jz=1.1..1.5: %s ; at 1.6, 2.5, 4.0: %s" % (
            [round(relZ[J], 1) for J in (1.1, 1.2, 1.3, 1.4, 1.5)], [round(relZ[J], 2) for J in (1.6, 2.5, 4.0)]))
        print("dataset paper energy ratio (E-E0)/(E1-E0) at Jz=1.6, 2.5, 4.0: %s ; below 1 from Jz >= %s ; at 1.1-1.4: %s" % (
            [round(eratio[J], 4) for J in (1.6, 2.5, 4.0)], min(J for J in Js if all(eratio[K] < 1 for K in Js if K >= J)),
            [round(eratio[J], 2) for J in (1.1, 1.2, 1.3, 1.4)]))
        tr = [i for i, J in enumerate(Js) if J >= 1.6 - 1e-9]
        print("median over 1.6-6.0 of mean rel. error: Czz %.2f %% ; Zloop %.2f %% ; Z %.2f %%" % (
            float(np.median([relC[i] for i in tr])), float(np.median([relL[i] for i in tr])), float(np.median([relZ[Js[i]] for i in tr]))))
        # curve test (authors' DMRG reference at every coupling)
        rows = []
        for J in Js:
            c = C19[str(float(J))]; cv = np.array(c["curve"])
            cur = float(np.interp(math.sqrt(max(de[J], 0)), np.sqrt(np.maximum(cv[:, 0], 0)), cv[:, 1]))
            de_neel = (-20 * J / 4 - c["E0"]) / 19; ch = (1 - c["ms0"]) * math.sqrt(max(de[J], 0) / de_neel)
            tau = 0.06 * abs(ms_gs[J])
            rows.append(dict(J=J, raw=abs(dms[J]) / tau, ratio=dms[J] / cur, miss=abs(dms[J] - cur) / tau, missch=abs(dms[J] - ch) / tau,
                             n19=abs(c["ms0"] - ms_gs[J]) / tau, inrange=bool(cv[:, 0].min() <= de[J] <= cv[:, 0].max())))
        dec = [r for r in rows if r["raw"] >= 0.2]
        out = [r["J"] for r in dec if not (0.75 <= r["ratio"] <= 1.3)]
        print("curve: mean raw miss %.4f ; mean corrected %.4f ; chord %.4f ; n19 value %.4f tau" % (
            np.mean([r["raw"] for r in rows]), np.mean([r["miss"] for r in rows]), np.mean([r["missch"] for r in rows]), np.mean([r["n19"] for r in rows])))
        print("curve: %d deciding couplings (%.1f-%.1f); ratios %.4f-%.4f, median %.3f; outside band at %d: %s ; all read inside curve range: %s" % (
            len(dec), min(r["J"] for r in dec), max(r["J"] for r in dec), min(r["ratio"] for r in dec), max(r["ratio"] for r in dec),
            float(np.median([r["ratio"] for r in dec])), len(out), out, all(r["inrange"] for r in rows)))
        print("curve: ratio at Jz=1.2, 1.6, 2.5, 4.0: %s" % [round(r["ratio"], 4) for r in rows if r["J"] in (1.2, 1.6, 2.5, 4.0)])
        print("n19 value at test couplings: %s" % [round(r["n19"], 3) for r in rows[:4]])
        print("energy error per site at Jz=1.1-1.6: %s" % [round(de[J], 5) for J in (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)])
    print("TOTAL sign: %d of %d" % (pos, tot))


if __name__ == "__main__":
    main()
