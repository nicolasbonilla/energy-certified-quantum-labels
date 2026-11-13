"""R10 reviewer phys-declared-stats: gather the re-fit outputs (retrain_b_*_out.json, combine_b_*_out.json) into the
tables of the report.  Site and bond means are combined with weights 57 and 64 (121 labels per instance)."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
lines = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def rj(name):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else None


def comb(site, bond):
    return (57 * np.array(site) + 64 * np.array(bond)) / 121.0


P("=== (a) replication of the stored predictions ===")
for J in ("1.6", "2.5"):
    for T in ("site", "bond"):
        r = rj("retrain_b_J%s_%s_base_reg_out.json" % (J, T))
        if r:
            P("Jz %s %-4s reg   declared cross-validation re-run: same selection %s ; max |prediction - stored| %.1e" % (J, T, r["reg"]["same_selection"], r["reg"]["maxdiff"]))
        for N in ("q_top", "q_kry"):
            d = rj("retrain_b_J%s_%s_direct_%s_out.json" % (J, T, N))
            if d:
                P("Jz %s %-4s %-5s fit at the stored hyperparameters, declared seed: max |prediction - stored| %.1e" % (J, T, N, d["direct_reproduces_stored_maxdiff"]))
P("")
P("=== (b) seed spread and lengths beyond the declared grid (all 121 labels, mean over six instances) ===")
for J in ("1.6", "2.5"):
    for N in ("q_top", "q_kry"):
        s = rj("retrain_b_J%s_site_direct_%s_out.json" % (J, N))
        b = rj("retrain_b_J%s_bond_direct_%s_out.json" % (J, N))
        if not (s and b):
            P("Jz %s %s: not finished (site %s, bond %s)" % (J, N, bool(s), bool(b)))
            for nm, x in (("site", s), ("bond", b)):
                if x:
                    sd = [float(np.mean(v["per_instance"])) for v in x["seeds"]]
                    g = min(x["grid"], key=lambda v: np.mean(v["per_instance"]))
                    P("    %s only: stored %.4f ; five seeds %.4f-%.4f ; best beyond the grid %.4f (length %g, penalty %g) ; emb19 %.4f" % (
                        nm, np.mean(x["stored_per_instance"]), min(sd), max(sd), np.mean(g["per_instance"]), g["ell"], g["alpha"], np.mean(x["emb19_per_instance"])))
            continue
        sto = comb(s["stored_per_instance"], b["stored_per_instance"])
        e19 = comb(s["emb19_per_instance"], b["emb19_per_instance"])
        seeds = [comb(vs["per_instance"], vb["per_instance"]) for vs, vb in zip(s["seeds"], b["seeds"])]
        sm = [float(x.mean()) for x in seeds]
        # oracle: best (length, penalty) per label type, chosen on the test instances
        gs = min(s["grid"], key=lambda v: np.mean(v["per_instance"]))
        gb = min(b["grid"], key=lambda v: np.mean(v["per_instance"]))
        orc = comb(gs["per_instance"], gb["per_instance"])
        P("Jz %s %-5s stored %.4f ; five other seeds %.4f-%.4f (mean %.4f) ; oracle beyond the grid %.4f (%+.1f %%; sites length %g penalty %g, bonds length %g penalty %g)" % (
            J, N, sto.mean(), min(sm), max(sm), np.mean(sm), orc.mean(), 100 * (orc.mean() / sto.mean() - 1), gs["ell"], gs["alpha"], gb["ell"], gb["alpha"]))
        P("          ratio to the 19-site embedded cluster: stored %.2f ; seeds %.2f-%.2f ; oracle %.2f ; oracle better than emb19 in %d of 6 instances" % (
            sto.mean() / e19.mean(), min(sm) / e19.mean(), max(sm) / e19.mean(), orc.mean() / e19.mean(), int((orc < e19).sum())))
P("")
P("=== (c) exploratory combination: label + 13-site clusters against the stored stack (no label) ===")
for fam in ("top", "kry"):
    for J in ("1.6", "2.5"):
        s = rj("combine_b_J%s_site_%s_out.json" % (J, fam))
        b = rj("combine_b_J%s_bond_%s_out.json" % (J, fam))
        for nm, x in (("site", s), ("bond", b)):
            if x:
                a = np.array([r["combined"] for r in x["rows"]])
                st = np.array([r["stack"] for r in x["rows"]])
                P("Jz %s family %s %-4s: combined %.4f, stack %.4f (%+.1f %%), combined better in %d/6 ; cv_mae combined %.5f" % (
                    J, fam, nm, a.mean(), st.mean(), 100 * (a.mean() / st.mean() - 1), int((a < st).sum()), x["best"]["cv_mae"]))
        if s and b:
            a = comb([r["combined"] for r in s["rows"]], [r["combined"] for r in b["rows"]])
            st = comb([r["stack"] for r in s["rows"]], [r["stack"] for r in b["rows"]])
            e19 = comb([r["emb19"] for r in s["rows"]], [r["emb19"] for r in b["rows"]])
            e13 = comb([r["emb13"] for r in s["rows"]], [r["emb13"] for r in b["rows"]])
            P("   Jz %s family %s, all 121 labels: label + 13-site clusters %.4f [%.3f, %.3f] ; stack %.4f ; change %+.1f %% ; better in %d of 6 instances ; emb13 %.4f ; emb19 %.4f (combined better in %d of 6)" % (
                J, fam, a.mean(), a.min(), a.max(), st.mean(), 100 * (a.mean() / st.mean() - 1), int((a < st).sum()), e13.mean(), e19.mean(), int((a < e19).sum())))
open(os.path.join(HERE, "summarize_refits_out.txt"), "w", encoding="utf8").write("\n".join(lines) + "\n")
