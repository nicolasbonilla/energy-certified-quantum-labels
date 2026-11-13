# real_data / checks / rd_predict_make_results.py   (own code; 2026-11-12; task rd-predict; WRITTEN AFTER THE HASH)
#
# Writes results/RESULTS_predict.md and out/predict_real.json from
#   out/predict/predict_results.json      the output of the SEALED code (code/run_predict.py), copied verbatim;
#   checks/rd_predict_independent.json    the independent recomputation (checks/rd_predict_independent.py);
#   converted/real_n{57,115}.json         only for one post hoc line (energy before the basis optimization).
# It computes no declared quantity: every outcome and every declared number is read from the sealed output. The few
# derived numbers (counts, ranges, the post hoc lines) are computed from the rows of the sealed output and are marked.
#
#   python -B -I rd_predict_make_results.py
import hashlib
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)
FAMS = ("sites", "edges", "second_neighbours", "loops")
FAM_TXT = dict(sites="sites", edges="edges", second_neighbours="second neighbours", loops="loops")
N_ITEMS = {57: dict(sites=57, edges=64, second_neighbours=87, loops=4), 115: dict(sites=115, edges=132, second_neighbours=185, loops=12)}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def rt(p):
    with open(p, encoding="utf-8") as f:
        return f.read().strip()


def lo(x, d=3):
    return math.floor(x * 10 ** d) / 10 ** d


def hi(x, d=3):
    return math.ceil(x * 10 ** d) / 10 ** d


def es(x, d=3):
    return ("%.*f" % (d, x)).replace(".", ",")


def runs(js):
    """Couplings as text, consecutive ones (step 0.1) joined: 2.6-5.3, 5.5."""
    js = sorted(js); out = []; i = 0
    while i < len(js):
        j = i
        while j + 1 < len(js) and round(js[j + 1] - js[j], 1) == 0.1:
            j += 1
        out.append("%.1f" % js[i] if i == j else "%.1f-%.1f" % (js[i], js[j]))
        i = j + 1
    return ", ".join(out) if out else "none"


def med(v):
    v = sorted(v); k = len(v)
    return v[k // 2] if k % 2 else 0.5 * (v[k // 2 - 1] + v[k // 2])


decl_sha = sha(os.path.join(RD, "DECLARATION.md"))
rec = re.search(r"\b[0-9a-f]{64}\b", rt(os.path.join(RD, "DECLARATION.sha256"))).group(0)
assert rec == decl_sha, "declaration hash mismatch"
dtext = open(os.path.join(RD, "DECLARATION.md"), encoding="utf-8").read()
manifest = dict((m.group(2), m.group(1)) for m in re.finditer(r"^([0-9a-f]{64})  (\S+)$", dtext, re.M))
CODE = ("code/run_predict.py", "code/rd_predict.py", "code/rd_common.py", "code/n19_curves.py", "out/n19/n19_curves.json",
        "out/n19/n19_labels.json")
code_ok = {c: (sha(os.path.join(RD, *c.split("/"))) == manifest[c]) for c in CODE}
assert all(code_ok.values()), code_ok
for name in ("real_n57.json", "real_n115.json"):
    assert sha(os.path.join(RD, "converted", name)) == manifest["converted/" + name]

SEALED_PATH = os.path.join(RD, "out", "predict", "predict_results.json")
R = rj(SEALED_PATH)
I = rj(os.path.join(HERE, "rd_predict_independent.json"))
assert R["declaration_sha256"] == decl_sha
FIRST = os.path.join(RD, "out", "predict", "first_run_before_S_sets", "predict_results.json")
t_run = dict(first_started=rt(os.path.join(os.path.dirname(FIRST), "run_predict_started_utc.txt")),
             first_finished=rt(os.path.join(os.path.dirname(FIRST), "run_predict_finished_utc.txt")),
             second_started=rt(os.path.join(RD, "out", "predict", "run_predict_started_utc.txt")),
             second_finished=rt(os.path.join(RD, "out", "predict", "run_predict_finished_utc.txt")))
sets_sha = sha(os.path.join(RD, "out", "S_sets.json"))
assert sets_sha == re.search(r"\b[0-9a-f]{64}\b", rt(os.path.join(RD, "out", "S_sets.sha256"))).group(0)

# ------------------------------------------------------------------------------------------------ derived (from sealed rows)
post = {}
E_first = {}
for n in (57, 115):
    obj = rj(os.path.join(RD, "converted", "real_n%d.json" % n))
    E_first[n] = {round(float(k), 1): float(v["ground_state_energy"]) for k, v in obj["skqd_random_flip"].items()}
D = {}
for n in (57, 115):
    S = R["sizes"][str(n)]
    rows = S["P5"]["rows"]
    dec = [r for r in rows if r["decides_ratio"]]
    d = dict(
        n_ratio_outside_all_50=[r["Jz"] for r in rows if not (0.75 <= r["ratio"] <= 1.3)],
        ratio_all=[min(r["ratio"] for r in rows), max(r["ratio"] for r in rows)],
        ratio_median_deciding=sorted(r["ratio"] for r in dec)[len(dec) // 2] if len(dec) % 2 else
        0.5 * (sorted(r["ratio"] for r in dec)[len(dec) // 2 - 1] + sorted(r["ratio"] for r in dec)[len(dec) // 2]),
        chord_ratio_deciding=[min(r["Delta"] / r["chord"] for r in dec), max(r["Delta"] / r["chord"] for r in dec)],
        chord_ratio_outside_deciding=[r["Jz"] for r in dec if not (0.75 <= r["Delta"] / r["chord"] <= 1.3)],
        curve_better_than_chord_at=[r["Jz"] for r in rows if r["miss_tau"] < r["miss_chord_tau"]],
        corrected_worse_than_raw_at=[r["Jz"] for r in rows if r["miss_tau"] > r["raw_miss_tau"]])
    D[n] = d
# post hoc: energy error per site before the basis optimization over the one after it. E_first and E_real are read
# from the converted files (plain JSON); E0 is the one behind the sealed rows (E_real - de * n).
for n in (57, 115):
    obj = rj(os.path.join(RD, "converted", "real_n%d.json" % n))
    rows = R["sizes"][str(n)]["P5"]["rows"]
    fac = {}
    for r in rows:
        E_real = float(obj["skqd_random_flip"]["%.1f" % r["Jz"]]["final_global_energy"])
        E0 = E_real - r["de"] * n
        fac[r["Jz"]] = (E_first[n][r["Jz"]] - E0) / (E_real - E0)
    D[n]["de_first_over_de_real"] = dict(min=min(fac.values()), max=max(fac.values()),
                                         median=med(fac.values()), at_deciding=[min(fac[r["Jz"]] for r in rows if r["decides_ratio"]),
                                                                                      max(fac[r["Jz"]] for r in rows if r["decides_ratio"])],
                                         per_coupling={"%.1f" % k: v for k, v in fac.items()})
    c = R["sizes"][str(n)]["n19_comparison"]
    kept = set(c["kept"])
    kr = [x for x in c["rows"] if x["Jz"] in kept]
    D[n]["kept"] = dict(n=len(kr), first=min(kept), last=max(kept), max_n19=max(x["n19_minus_truth_tau"] for x in kr),
                        mean_n19=sum(x["n19_minus_truth_tau"] for x in kr) / len(kr),
                        max_label=max(x["label_miss_tau"] for x in kr), mean_label=sum(x["label_miss_tau"] for x in kr) / len(kr),
                        n19_closer=[x["Jz"] for x in kr if x["n19_minus_truth_tau"] < x["label_miss_tau"]])
    D[n]["n19_closer_all"] = [x["Jz"] for x in c["rows"] if x["n19_minus_truth_tau"] < x["label_miss_tau"]]
    D[n]["n19_within_fifth_from"] = min(x["Jz"] for x in c["rows"] if all(y["n19_minus_truth_tau"] <= 0.2 for y in c["rows"] if y["Jz"] >= x["Jz"]))
    assert D[n]["n19_closer_all"] == I["sizes"][str(n)]["n19_comparison"]["n19_closer_than_label_at"]

s57, s115 = R["sizes"]["57"], R["sizes"]["115"]
a57, a115 = s57["P5"]["all"], s115["P5"]["all"]
t57, t115 = s57["P5"]["training_45"], s115["P5"]["training_45"]
e57, e115 = s57["P5"]["test_1p1_1p4"], s115["P5"]["test_1p1_1p4"]
maxdiff = max(max(v.values()) for v in I["max_abs_difference_from_sealed"].values())
ndiff = sum(len(v) for v in I["max_abs_difference_from_sealed"].values())
F_all = [R["sizes"][str(n)]["P1_P3"][f]["F"] for n in (57, 115) for f in FAMS]
rho_all = [R["sizes"][str(n)]["P4"][f]["spearman"] for n in (57, 115) for f in FAMS]
le1_all = [v for n in (57, 115) for f in FAMS for v in R["sizes"][str(n)]["P1_P3"][f]["frac_t_le_1_per_coupling"].values()]
assert all(R["sizes"][str(n)]["P1_P3"][f]["holds"] for n in (57, 115) for f in FAMS)
assert all(R["sizes"][str(n)]["P4"][f]["holds"] for n in (57, 115) for f in FAMS)
assert R["P5_rule"]["outcome"] == "FAIL" and a57["mean_miss_ok"] and a115["mean_miss_ok"] and a57["ratios_ok"] and not a115["ratios_ok"]
assert min(le1_all) == 1.0

# ------------------------------------------------------------------------------------------------ text
L = []
w = L.append
w("# Real data of arXiv:2606.15983: RESULTS of the predictions (declaration Sec. 5) and of the n = 19 comparison (Sec. 6)")
w("")
w("Task `rd-predict`, 2026-11-12. Declaration: `real_data/DECLARATION.md`, SHA-256 `%s` (checked before anything was read)." % decl_sha)
w("Every outcome below is the output of the sealed code `code/run_predict.py`, run unchanged. No rule was changed.")
w("")
w("## Resumen en español (ocho líneas)")
w("")
w("1. Se comprobó que la declaración sellada no había cambiado (su huella coincide) y se ejecutó el programa sellado, tal cual, sobre los datos públicos.")
w("2. Predicción de signo (P1-P3): SE CUMPLE en los ocho casos (cuatro familias de etiquetas, dos tamaños). Entre el %s %% y el 100 %% de las etiquetas reales quedan desplazadas hacia el estado de Néel respecto del valor verdadero; la regla pedía el 95 %%."
  % es(100 * lo(min(F_all), 4), 2))
w("3. Predicción de que el error baja al crecer Jz (P4): SE CUMPLE en los ocho casos. La correlación de rangos va de %s a %s; la regla pedía -0,9 o menos."
  % (es(lo(min(rho_all))), es(hi(max(rho_all)))))
w("4. Predicción de la curva de sesgo contra energía (P5): NO PASA. El error medio tras corregir sí cumple (%s tau con límite 0,2 a 57 cúbits; %s tau con límite 0,6 a 115) y los cocientes a 57 cúbits también (de %s a %s); pero a 115 cúbits %d de los %d cocientes que deciden quedan por debajo de 0,75 (van de %s a %s)."
  % (es(a57["mean_miss_tau"]), es(a115["mean_miss_tau"]), es(lo(a57["ratio_range_deciding"][0])), es(hi(a57["ratio_range_deciding"][1])),
     len(a115["ratios_outside"]), a115["n_deciding"], es(lo(a115["ratio_range_deciding"][0])), es(hi(a115["ratio_range_deciding"][1]))))
w("5. Consecuencia fijada de antemano en la declaración: la Sec. V del artículo queda limitada a la primera etapa del método, y el artículo tiene que decirlo.")
w("6. La fórmula sencilla sin parámetros (la «cuerda») corrige mejor que la curva sobre las 50 constantes: %s tau frente a %s tau a 57 cúbits y %s tau frente a %s tau a 115."
  % (es(a57["mean_miss_chord_tau"]), es(a57["mean_miss_tau"]), es(a115["mean_miss_chord_tau"]), es(a115["mean_miss_tau"])))
w("7. El cálculo exacto pequeño (19 sitios) queda a %s-%s tau (57) y %s-%s tau (115) de la verdad en las cuatro constantes de prueba y, como mucho, a %s tau y %s tau en las etiquetas que el filtro conserva; a 57 cúbits está más cerca de la verdad que la etiqueta real en %d de las 50 constantes (a 115, en %d)."
  % (es(min(s57["n19_comparison"]["at_test"].values()), 2), es(max(s57["n19_comparison"]["at_test"].values()), 2),
     es(min(s115["n19_comparison"]["at_test"].values()), 2), es(max(s115["n19_comparison"]["at_test"].values()), 2),
     es(hi(D[57]["kept"]["max_n19"])), es(hi(D[115]["kept"]["max_n19"])), len(D[57]["n19_closer_all"]), len(D[115]["n19_closer_all"])))
w("8. Un segundo programa, escrito aparte, reproduce todos los números (diferencia máxima %.0e). No se halló ningún defecto en el programa sellado y no se cambió ninguna regla. Una comprobación queda incompleta (G1: no se repitió la conversión de los datos; sus huellas sí coinciden)."
  % maxdiff)
w("")
w("## Summary (English)")
w("")
w("| analysis | declared rule | outcome |")
w("|---|---|---|")
for n in (57, 115):
    for f in FAMS:
        r = R["sizes"][str(n)]["P1_P3"][f]
        w("| P1-P3 sign, %s, n = %d | F >= 0.95 over the 50 couplings | **HOLDS** (F = %.6f; %d of %d pairs not positive) |"
          % (FAM_TXT[f], n, r["F"], r["n_pairs"] - round(r["F"] * r["n_pairs"]), r["n_pairs"]))
for n in (57, 115):
    for f in FAMS:
        r = R["sizes"][str(n)]["P4"][f]
        w("| P4 error decreases with Jz, %s, n = %d | Spearman(D, Jz) <= -0.9 over the 50 couplings | **HOLDS** (%.6f) |" % (FAM_TXT[f], n, r["spearman"]))
w("| P5 bias-against-energy curve (one decision) | mean miss <= 0.2 tau (n = 57) and <= 0.6 tau (n = 115), and every ratio in [0.75, 1.3] where the raw miss is at least 0.2 tau; 50 couplings of each size | **FAIL** |")
w("| P5, part n = 57 | | mean miss %.3f tau: met. Ratios at the %d deciding couplings %.3f-%.3f: all inside. |"
  % (a57["mean_miss_tau"], a57["n_deciding"], lo(a57["ratio_range_deciding"][0]), hi(a57["ratio_range_deciding"][1])))
w("| P5, part n = 115 | | mean miss %.3f tau: met. Ratios at the %d deciding couplings %.3f-%.3f: **%d outside, all below 0.75** (Jz = %s). |"
  % (a115["mean_miss_tau"], a115["n_deciding"], lo(a115["ratio_range_deciding"][0]), hi(a115["ratio_range_deciding"][1]),
     len(a115["ratios_outside"]), ", ".join("%.1f" % j for j in a115["ratios_outside"])))
w("| P5 on the 45 training couplings (reported, does not decide) | same rule | FAIL (n = 115: %d of %d deciding ratios outside) |" % (len(t115["ratios_outside"]), t115["n_deciding"]))
w("| n = 19 comparison of Sec. 6 | descriptive, no rule | see Sec. 5 below |")
w("")
w("**Gate note, printed with every result (declaration Sec. 12, line 14).** G1 is NOT COMPLETE: the converter was not re-run on the pinned archive; the three converted files have the pinned SHA-256 (checked by the sealed loader at every read, by the map task and by this task). G2, G3 and G4 pass for the dataset at both sizes (map task; re-checked here with own code, Sec. 7). G8 was passed before the hash.")
w("")
w("**What P5 means for Sec. V of the paper, as the declaration states it (Sec. 5, P5):** \"the curve was built for the first stage (truncation in the computational basis). The real labels come after a rotation that lowers the energy error per site five- to tenfold. A pass extends Sec. V to the full method; a fail restricts Sec. V to the first stage, and the paper says so.\" The outcome is FAIL. **Sec. V is therefore restricted to the first stage, and the paper has to say so.** The declared prior for a pass was 0.4.")
w("")
w("Marks on numbers: **[S]** already seen before the hash (item of declaration Sec. 1 in brackets); **[N]** not seen and not computed before the hash; **[0]** involves no real datum (exact n = 19 and the truth, both in hand before the hash).")
w("")
# ---------------------------------------------------------------- 1
w("## 1. What was run")
w("")
w("- `DECLARATION.sha256` equals the SHA-256 of `DECLARATION.md` (`sha256sum`; the gate of the sealed code; the independent script). `python -B -I checks/make_manifest.py --check`: 69 lines of Sec. 11 equal to the files on disk, 0 different, 4 not re-hashed there (`converted/`, `source/`). The four code and two n = 19 files used here were hashed again by this script and equal Sec. 11: %s."
  % ", ".join("`%s`" % c for c in CODE))
w("- Command: `python -B -I code/run_predict.py --hash=%s` (Python 3.11.4, numpy 1.26.4, scipy 1.13.1, two threads, laptop; about 3 s)." % decl_sha)
w("- Run 1: %s to %s UTC, before `out/S_sets.json` existed (kept set of the filter not available). Run 2: %s to %s UTC, after the map task had written `out/S_sets.json` (SHA-256 `%s`, equal to `out/S_sets.sha256`). The two outputs are identical except for the kept-set part of the n = 19 comparison (compared key by key). Run 1 is kept in `out/predict/first_run_before_S_sets/`."
  % (t_run["first_started"], t_run["first_finished"], t_run["second_started"], t_run["second_finished"], sets_sha))
w("- Output of the sealed code: `out/predict/predict_results.json` (SHA-256 `%s`), copied verbatim into `out/predict_real.json` together with provenance, the independent check and the post hoc lines." % sha(SEALED_PATH))
w("- Truth (declaration Sec. 0 and Sec. 12, line 1): this project's bond-dimension-320 references for E0 and m_s at %d (n = 57) and %d (n = 115) couplings, the authors' DMRG elsewhere and for every single site, pair and loop. Orientation +1 at every coupling for labels and truth: %s (57), %s (115)."
  % (len(s57["truth_sources"]["E0_project"]), len(s115["truth_sources"]["E0_project"]), s57["orientation_all_plus"], s115["orientation_all_plus"]))
w("- No code defect was found. Nothing listed in Sec. 11 was changed. See `DEVIATIONS.md` for the dated notes of this task.")
w("")
# ---------------------------------------------------------------- 2
w("## 2. P1-P3: every label lies on the Neel side of the truth")
w("")
w("Rule: t_x = (o_real - o_GS) / (o_Neel - o_GS); F = fraction of (item, coupling) pairs with t_x > 0 over the 50 couplings; **holds iff F >= 0.95**, decided separately for each family and size (eight outcomes). Neel values eta_i, -1, +1, +1.")
w("")
w("| n | family | items | pairs | pairs with t <= 0 | F | outcome | fraction with t <= 1 | smallest t | largest t | seen before? |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
for n in (57, 115):
    for f in FAMS:
        r = R["sizes"][str(n)]["P1_P3"][f]
        seen = "[S] at 14 couplings (F8: Jz = 1.1-2.0, 3.0, 4.0, 5.0, 6.0), [N] at the other 36" if f == "sites" else "[N]"
        w("| %d | %s | %d | %d | %d | %.6f | **HOLDS** | %.4f | %.4f | %.4f | %s |"
          % (n, FAM_TXT[f], r["n_items"], r["n_pairs"], r["n_pairs"] - round(r["F"] * r["n_pairs"]), r["F"], r["frac_t_le_1"], r["t_min"], r["t_max"], seen))
w("")
w("- Undefined t_x (Neel value equal to the truth): none. The fraction with t_x <= 1 (\"between the ground state and the Neel state\" when t_x > 0) is 1.0000 at every coupling, for every family and size: no label lies beyond the Neel value.")
w("- Sites: the first-look file also holds a number of this kind for all 50 couplings (F2), printed for 14 (F8: 1.00 everywhere except 0.98 at n = 115, Jz = 1.5). The present values agree with F8: F = %.4f at (115, 1.5), 1.0000 at the other 13 printed couplings of each size."
  % R["sizes"]["115"]["P1_P3"]["sites"]["F_per_coupling"]["1.5"])
neg57 = I["sizes"]["57"]["t_not_positive"]; neg115 = I["sizes"]["115"]["t_not_positive"]
w("- **The pairs that are not on the Neel side** (list from the independent recomputation; the counts are those of the sealed output):")
w("  - n = 57: %d pairs, both edges at Jz = 1.9: %s. Both differences are below 0.05 of the item's own 6 %% tolerance."
  % (len(neg57), "; ".join("edge (%d, %d), t = %+.4f (label %.5f, truth %.5f)" % (x["item"][0], x["item"][1], x["t"], x["o_real"], x["o_gs"]) for x in neg57)))
w("  - n = 115: %d pairs, **all at Jz = 1.5** and all around sites 19 and 89 (2 sites, 3 edges, 7 second-neighbour pairs, 1 loop). There the published label is *less* ordered than the truth by %.1f to %.1f times the item's own 6 %% tolerance: site 19 has <Z> = %.3f against %.3f. This is a local feature of that one published state, at a coupling that is in neither the training nor the test set."
  % (len(neg115), lo(min(abs(x["diff_over_tau_item"]) for x in neg115), 1), hi(max(abs(x["diff_over_tau_item"]) for x in neg115), 1),
     [x for x in neg115 if x["family"] == "sites" and x["item"] == 19][0]["o_real"], [x for x in neg115 if x["family"] == "sites" and x["item"] == 19][0]["o_gs"]))
w("")
w("F per coupling (fraction of the items of the family with t_x > 0). Sites: [S] at Jz = 1.1-2.0, 3.0, 4.0, 5.0, 6.0; everything else [N].")
w("")
w("| Jz | sites 57 | edges 57 | 2nd nb. 57 | loops 57 | sites 115 | edges 115 | 2nd nb. 115 | loops 115 |")
w("|---|---|---|---|---|---|---|---|---|")
for k in range(11, 61):
    key = "%.1f" % (k / 10)
    w("| %s | %s |" % (key, " | ".join("%.4f" % R["sizes"][str(n)]["P1_P3"][f]["F_per_coupling"][key] for n in (57, 115) for f in FAMS)))
w("")
# ---------------------------------------------------------------- 3
w("## 3. P4: the error decreases with Jz")
w("")
w("Rule: D(n, Jz) = mean over the items of |o_real - o_GS| / (0.06 |o_GS|); **holds iff the Spearman rank correlation of D with Jz is <= -0.9** over the 50 couplings, decided separately for each family and size (eight outcomes). m_s is not one of the four families; it is printed next to them and adds no decision.")
w("")
w("| n | family | Spearman(D, Jz) | outcome | largest D (Jz = 1.1) | smallest D | seen before? |")
w("|---|---|---|---|---|---|---|")
for n in (57, 115):
    for f in FAMS + ("m_s",):
        r = R["sizes"][str(n)]["P4"][f]
        w("| %d | %s | %.6f | %s | %.3f | %.3f | %s |" % (n, FAM_TXT.get(f, "m_s (no decision)"), r["spearman"], "**HOLDS**" if f != "m_s" else "(<= -0.9)",
                                                    r["D_max"], r["D_min"], "[N]" if f != "m_s" else "[S] (F7)"))
w("")
w("D is not monotonic. Couplings at which D is larger than at the coupling 0.1 below (from the D values of the sealed output; the rule is a rank correlation and tolerates them):")
w("")
w("| n | family | number of increases | at Jz = |")
w("|---|---|---|---|")
P4_INC = {}
for n in (57, 115):
    for f in FAMS + ("m_s",):
        Dd = R["sizes"][str(n)]["P4"][f]["D"]
        inc = [k / 10 for k in range(12, 61) if Dd["%.1f" % (k / 10)] > Dd["%.1f" % ((k - 1) / 10)]]
        P4_INC["%d %s" % (n, f)] = inc
        if f != "m_s":
            assert len(inc) == I["sizes"][str(n)]["P4"][f]["n_increases"]
        w("| %d | %s | %d | %s |" % (n, FAM_TXT.get(f, "m_s"), len(inc), runs(inc)))
w("")
same_order = {}
for n in (57, 115):
    Ds_, Dm_ = R["sizes"][str(n)]["P4"]["sites"]["D"], R["sizes"][str(n)]["P4"]["m_s"]["D"]
    ks = ["%.1f" % (k / 10) for k in range(11, 61)]
    same_order[n] = sorted(ks, key=lambda k: Ds_[k]) == sorted(ks, key=lambda k: Dm_[k])
w("How blind each line is: m_s was seen (F7). For the sites, the 50 couplings are ordered by D exactly as by the m_s miss at n = 57 (%s) and at n = 115 (%s), so the rank correlation of the sites repeats a number that was seen: it is a confirmation by a fixed pipeline, not a prediction. Edges, second neighbours and loops had not been compared with their references before the hash."
  % ("same order" if same_order[57] else "not the same order", "same order" if same_order[115] else "not the same order"))
w("")
w("D per coupling, in units of the item's 6 % tolerance (m_s columns [S], F7; the others [N]).")
w("")
w("| Jz | sites 57 | edges 57 | 2nd nb. 57 | loops 57 | m_s 57 [S] | sites 115 | edges 115 | 2nd nb. 115 | loops 115 | m_s 115 [S] |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
for k in range(11, 61):
    key = "%.1f" % (k / 10)
    w("| %s | %s |" % (key, " | ".join("%.3f" % R["sizes"][str(n)]["P4"][f]["D"][key] for n in (57, 115) for f in FAMS + ("m_s",))))
w("")
# ---------------------------------------------------------------- 4
w("## 4. P5: the bias-against-energy curve of Sec. V")
w("")
w("Recipe of the n = 19 curve unchanged (`bias_law/code/n19b.py`: exact ground state at n = 19 at the same Jz, top-D truncation, 26 levels, read by linear interpolation in sqrt(de), end values held), computed before the hash at the 50 couplings (`out/n19/n19_curves.json`, no real datum). Delta = m_s(real) - m_s(GS); ratio = Delta / curve(de_real); corrected miss = |m_s(real) - curve(de_real) - m_s(GS)| / tau.")
w("")
w("**Rule (one decision): PASS iff the mean corrected miss is at most 0.2 tau at n = 57 and at most 0.6 tau at n = 115, and every ratio lies in [0.75, 1.3] at the couplings where the raw miss is at least 0.2 tau, over the 50 couplings of each size.**")
w("")
w("**Outcome: FAIL.**")
w("")
w("| part | n = 57 | n = 115 |")
w("|---|---|---|")
w("| mean corrected miss over the 50 couplings [N] | %.4f tau (limit 0.2): met | %.4f tau (limit 0.6): met |" % (a57["mean_miss_tau"], a115["mean_miss_tau"]))
w("| deciding couplings (raw miss >= 0.2 tau) [S] | %d: Jz = %s | %d: Jz = %s |"
  % (a57["n_deciding"], "1.1-3.1 and 3.3" if a57["deciding_couplings"] == [k / 10 for k in range(11, 32)] + [3.3] else str(a57["deciding_couplings"]),
     a115["n_deciding"], "1.1-2.9" if a115["deciding_couplings"] == [k / 10 for k in range(11, 30)] else str(a115["deciding_couplings"])))
w("| ratios at the deciding couplings [N] | %.4f to %.4f (median %.3f): **all inside [0.75, 1.3]** | %.4f to %.4f (median %.3f): **%d of %d outside, all below 0.75**: Jz = %s |"
  % (a57["ratio_range_deciding"][0], a57["ratio_range_deciding"][1], D[57]["ratio_median_deciding"], a115["ratio_range_deciding"][0],
     a115["ratio_range_deciding"][1], D[115]["ratio_median_deciding"], len(a115["ratios_outside"]), a115["n_deciding"],
     ", ".join("%.1f" % j for j in a115["ratios_outside"])))
w("| couplings read outside the range of the curve | %d | %d |" % (a57["n_de_outside_curve"], a115["n_de_outside_curve"]))
w("| the part of this size | both conditions met | mean miss met, ratio condition **not met** |")
w("")
w("In words: at n = 115 the published labels are biased towards the Neel state by %.0f to %.0f %% of what the first-stage curve gives at their own energy error (median %.0f %%) wherever the bias matters (raw miss at least 0.2 tau). The curve over-corrects them. At n = 57 the same ratio is %.0f to %.0f %% (median %.0f %%), inside the declared band."
  % (100 * lo(a115["ratio_range_deciding"][0], 2), 100 * hi(a115["ratio_range_deciding"][1], 2), 100 * D[115]["ratio_median_deciding"],
     100 * lo(a57["ratio_range_deciding"][0], 2), 100 * hi(a57["ratio_range_deciding"][1], 2), 100 * D[57]["ratio_median_deciding"]))
w("")
w("### 4.1 Mean and largest misses, with the comparators (units of tau)")
w("")
w("| set of couplings | n | label as published (raw) [S] | corrected with the curve [N] | corrected with the chord [N] | truth at n = 19 instead of the label [0] | curve beats chord? |")
w("|---|---|---|---|---|---|---|")
for name, k in (("all 50 (decides)", "all"), ("45 training, Jz >= 1.6 (reported)", "training_45"), ("4 test, Jz = 1.1-1.4 (reported)", "test_1p1_1p4")):
    for n in (57, 115):
        s = R["sizes"][str(n)]["P5"][k]
        w("| %s | %d | mean %.3f, max %.3f | mean %.3f, max %.3f | mean %.3f, max %.3f | mean %.3f, max %.3f | %s |"
          % (name, n, s["mean_raw_miss_tau"], s["max_raw_miss_tau"], s["mean_miss_tau"], s["max_miss_tau"], s["mean_miss_chord_tau"],
             s["max_miss_chord_tau"], s["mean_miss_n19_truth_tau"], s["max_miss_n19_truth_tau"], "yes" if s["curve_beats_chord"] else "**no**"))
w("")
w("- The correction with the curve lowers the mean miss at both sizes (%.3f to %.3f tau at n = 57, %.3f to %.3f tau at n = 115, 50 couplings). This is what the mean-miss part of the rule measures, and it is met."
  % (a57["mean_raw_miss_tau"], a57["mean_miss_tau"], a115["mean_raw_miss_tau"], a115["mean_miss_tau"]))
w("- **The parameter-free chord does better than the curve** over the 50 couplings at both sizes (%.3f against %.3f tau at n = 57; %.3f against %.3f tau at n = 115) and over the 45 training couplings at n = 57 (%.3f against %.3f); over the 45 training couplings at n = 115 the two are level (%.3f chord, %.3f curve)."
  % (a57["mean_miss_chord_tau"], a57["mean_miss_tau"], a115["mean_miss_chord_tau"], a115["mean_miss_tau"], t57["mean_miss_chord_tau"],
     t57["mean_miss_tau"], t115["mean_miss_chord_tau"], t115["mean_miss_tau"]))
w("- At the four test couplings the curve leaves %.2f-%.2f tau (n = 57) and %.2f-%.2f tau (n = 115); the chord leaves %.2f-%.2f and %.2f-%.2f tau."
  % (lo(min(r["miss_tau"] for r in s57["P5"]["rows"][:4]), 2), hi(max(r["miss_tau"] for r in s57["P5"]["rows"][:4]), 2),
     lo(min(r["miss_tau"] for r in s115["P5"]["rows"][:4]), 2), hi(max(r["miss_tau"] for r in s115["P5"]["rows"][:4]), 2),
     lo(min(r["miss_chord_tau"] for r in s57["P5"]["rows"][:4]), 2), hi(max(r["miss_chord_tau"] for r in s57["P5"]["rows"][:4]), 2),
     lo(min(r["miss_chord_tau"] for r in s115["P5"]["rows"][:4]), 2), hi(max(r["miss_chord_tau"] for r in s115["P5"]["rows"][:4]), 2)))
w("- The same rule on the 45 training couplings (reported, does not decide): FAIL; mean misses %.4f (n = 57) and %.4f tau (n = 115), both within the limits; ratios at the deciding couplings %.4f-%.4f (n = 57, %d couplings, none outside) and %.4f-%.4f (n = 115, %d couplings, %d outside: Jz = %s)."
  % (t57["mean_miss_tau"], t115["mean_miss_tau"], t57["ratio_range_deciding"][0], t57["ratio_range_deciding"][1], t57["n_deciding"],
     t115["ratio_range_deciding"][0], t115["ratio_range_deciding"][1], t115["n_deciding"], len(t115["ratios_outside"]),
     ", ".join("%.1f" % j for j in t115["ratios_outside"])))
w("")
for n in (57, 115):
    S = R["sizes"][str(n)]
    w("### 4.%d Every coupling, n = %d" % ({57: 2, 115: 3}[n], n))
    w("")
    w("de = (E_real - E0)/n. Columns marked [S] were seen before the hash (de: F2, F4; Delta: m_s of the label and of the truth, F2; raw miss: F7; which couplings decide). Ratio, corrected miss and chord miss are [N]. \"D\" marks a deciding coupling; **OUT** a deciding ratio outside [0.75, 1.3]; (out) a ratio outside the band at a coupling that does not decide.")
    w("")
    w("| Jz | set | de [S] | Delta [S] | curve(de) | ratio [N] | decides [S] | raw miss/tau [S] | corrected miss/tau [N] | chord miss/tau [N] | n = 19 truth miss/tau [0] |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in S["P5"]["rows"]:
        J = r["Jz"]
        st = "test" if J < 1.45 else ("apart" if J < 1.55 else "train")
        inside = 0.75 <= r["ratio"] <= 1.3
        rtxt = ("%.4f" % r["ratio"]) if inside else (("**%.4f OUT**" % r["ratio"]) if r["decides_ratio"] else ("%.4f (out)" % r["ratio"]))
        w("| %.1f | %s | %.6f | %.6f | %.6f | %s | %s | %.3f | %.3f | %.3f | %.3f |"
          % (J, st, r["de"], r["Delta"], r["curve"], rtxt, "D" if r["decides_ratio"] else "-", r["raw_miss_tau"], r["miss_tau"], r["miss_chord_tau"], r["miss_n19_truth_tau"]))
    w("")
w("Ratios at couplings that do not decide (reported): at n = 57 the ratio rises with Jz and is above 1.3 at %d couplings (Jz = %s), where the raw miss is at most %.3f tau; over all 50 couplings it runs from %.3f to %.3f. At n = 115 it is below 0.75 at %d further couplings that do not decide (Jz = %s); over all 50 it runs from %.3f to %.3f."
  % (len([j for j in D[57]["n_ratio_outside_all_50"] if j not in a57["ratios_outside"]]),
     ", ".join("%.1f" % j for j in D[57]["n_ratio_outside_all_50"] if j not in a57["ratios_outside"]),
     hi(max(r["raw_miss_tau"] for r in s57["P5"]["rows"] if r["Jz"] in D[57]["n_ratio_outside_all_50"]), 3),
     lo(D[57]["ratio_all"][0]), hi(D[57]["ratio_all"][1]),
     len([j for j in D[115]["n_ratio_outside_all_50"] if j not in a115["ratios_outside"]]),
     ", ".join("%.1f" % j for j in D[115]["n_ratio_outside_all_50"] if j not in a115["ratios_outside"]),
     lo(D[115]["ratio_all"][0]), hi(D[115]["ratio_all"][1])))
w("")
# ---------------------------------------------------------------- 5
w("## 5. The small classical calculation next to every label (Sec. 6; descriptive, no rule)")
w("")
w("|m_s(exact, n = 19) - m_s^GS(n)| in units of tau = 0.06 |m_s^GS(n)|, at all 50 couplings and both sizes [0], next to the miss of the published label [S] (F7). \"kept\" = the training coupling is in the set S fixed by the map task (m_s row CERTIFIED (exact), reference tolerance, stored certificates; `out/S_sets.json`).")
w("")
w("| Jz | n = 57: n = 19 exact [0] | n = 57: published label [S] | n = 57 kept | n = 115: n = 19 exact [0] | n = 115: published label [S] | n = 115 kept |")
w("|---|---|---|---|---|---|---|")
c57, c115 = s57["n19_comparison"], s115["n19_comparison"]
for x, y in zip(c57["rows"], c115["rows"]):
    w("| %.1f | %.3f | %.3f | %s | %.3f | %.3f | %s |" % (x["Jz"], x["n19_minus_truth_tau"], x["label_miss_tau"], "kept" if x["Jz"] in c57["kept"] else "",
                                                     y["n19_minus_truth_tau"], y["label_miss_tau"], "kept" if y["Jz"] in c115["kept"] else ""))
w("")
w("- **Test couplings (Jz = 1.1, 1.2, 1.3, 1.4):** %s tau (n = 57) and %s tau (n = 115). These are the values already printed in the paper (1.05-1.47 and 1.43-2.07 tau)."
  % (", ".join("%.3f" % c57["at_test"][k] for k in ("1.1", "1.2", "1.3", "1.4")), ", ".join("%.3f" % c115["at_test"][k] for k in ("1.1", "1.2", "1.3", "1.4"))))
w("- **Largest value over all 50 couplings:** %.3f tau (n = 57) and %.3f tau (n = 115), both at Jz = 1.1. The exact n = 19 value is within a fifth of tau of the truth from Jz = %.1f on (n = 57) and from Jz = %.1f on (n = 115)."
  % (c57["max_all"], c115["max_all"], D[57]["n19_within_fifth_from"], D[115]["n19_within_fifth_from"]))
w("- **Largest value over the kept labels:** %.4f tau at n = 57 (%d labels, Jz = %.1f-%.1f) and %.4f tau at n = 115 (%d labels, Jz = %.1f-%.1f). **The paper's sentence (\"a range in which an exact 19-site calculation already lies within a fifth of the tolerance\") is true on the kept set at both sizes** (sealed output: %s, %s)."
  % (c57["max_over_kept"], c57["n_kept"], D[57]["kept"]["first"], D[57]["kept"]["last"], c115["max_over_kept"], c115["n_kept"],
     D[115]["kept"]["first"], D[115]["kept"]["last"], c57["sentence_within_a_fifth_on_kept"], c115["sentence_within_a_fifth_on_kept"]))
w("- **Against the label itself.** At n = 57 the exact n = 19 value is closer to the truth than the published label at %d of the 50 couplings (%d of the 45 training couplings), including %d of the %d kept labels (Jz = %s); over the kept labels the mean distances are %.3f tau (n = 19) and %.3f tau (label). At n = 115 it is closer at %d of 50 (Jz = %.1f-%.1f only) and at none of the %d kept labels (mean %.3f against %.3f tau)."
  % (len(D[57]["n19_closer_all"]), len([j for j in D[57]["n19_closer_all"] if j >= 1.6]), len(D[57]["kept"]["n19_closer"]), D[57]["kept"]["n"],
     ", ".join("%.1f" % j for j in D[57]["kept"]["n19_closer"]), D[57]["kept"]["mean_n19"], D[57]["kept"]["mean_label"],
     len(D[115]["n19_closer_all"]), min(D[115]["n19_closer_all"]), max(D[115]["n19_closer_all"]), D[115]["kept"]["n"],
     D[115]["kept"]["mean_n19"], D[115]["kept"]["mean_label"]))
w("- Said in advance in the declaration (Sec. 6): where the labels are already accurate the filter buys a guarantee, not accuracy.")
w("- If extension E1 adds certificates below the stored range (reported by its own task): the n = 19 distance is %.3f tau at Jz = 3.4 and %.3f tau at 3.3 for n = 115 (above a fifth), and at most %.3f tau for n = 57 down to Jz = 3.2."
  % ([y for y in c115["rows"] if abs(y["Jz"] - 3.4) < 1e-9][0]["n19_minus_truth_tau"], [y for y in c115["rows"] if abs(y["Jz"] - 3.3) < 1e-9][0]["n19_minus_truth_tau"],
     max(x["n19_minus_truth_tau"] for x in c57["rows"] if x["Jz"] >= 3.2 - 1e-9)))
w("")
# ---------------------------------------------------------------- 6
V = R["variant_post_select"]["115"]
va = V["P5"]["all"]
w("## 6. Secondary: the comparison variant (`skqd_post_select`, n = 115, %d couplings; Jz = 5.6, 5.7, 5.9, 6.0 excluded by gate G2)" % V["n_couplings"])
w("")
w("Same code, same rules, no decision attached (secondary everywhere). All [N].")
w("")
w("- Sign: F = %s (sites, edges, second neighbours, loops), all pairs positive; fraction with t <= 1: 1.0000." % ", ".join("%.4f" % V["P1_P3"][f]["F"] for f in FAMS))
w("- Rank correlation of D with Jz: %s." % ", ".join("%.4f" % V["P4"][f]["spearman"] for f in FAMS))
w("- Curve: mean corrected miss %.3f tau (raw %.3f, chord %.3f, truth at n = 19 %.3f); ratios at the %d deciding couplings %.3f-%.3f, **outside [0.75, 1.3] at %d of them** (Jz = %s). The variant shows the same shortfall as the dataset at n = 115."
  % (va["mean_miss_tau"], va["mean_raw_miss_tau"], va["mean_miss_chord_tau"], va["mean_miss_n19_truth_tau"], va["n_deciding"],
     lo(va["ratio_range_deciding"][0]), hi(va["ratio_range_deciding"][1]), len(va["ratios_outside"]), runs(va["ratios_outside"])))
w("")
# ---------------------------------------------------------------- 7
g57, g115 = I["sizes"]["57"]["gates"], I["sizes"]["115"]["gates"]
nn = I["n19_from_scratch_vs_stored"]; nb = I["n19_out_vs_bias_law_inputs"]
w("## 7. Gates and checks behind these numbers")
w("")
w("- **G1 (data): NOT COMPLETE.** Hashes of `converted/real_n57.json`, `real_n115.json`, `lattice_maps.json` equal the pinned ones; the declared re-run of the converter on the pinned archive was not done (not by this task; the map task records `rerun: null`).")
w("- **G2 (same state), re-checked here with own code:** the exchange part of the energy lies inside the bound at all 100 points: %.3f-%.3f of the bound (n = 57) and %.3f-%.3f (n = 115) [S] (T3)."
  % (g57["G2_min_fraction"], g57["G2_max_fraction"], g115["G2_min_fraction"], g115["G2_max_fraction"]))
w("- **G3 (energies):** E_real - E0(authors) >= %.4f (n = 57) and %.4f (n = 115) [S] (T4). **G4 (truth):** authors' DMRG against this project's references at the stored couplings: m_s within %.1e tau and %.1e tau, the seven label types within %.1e and %.1e tau (limit 1e-3), E0 within %.1e and %.1e (limit 1e-4) [S] (T5)."
  % (g57["G3_min"], g115["G3_min"], g57["G4_max_dms_tau"], g115["G4_max_dms_tau"], g57["G4_max_seven_tau"], g115["G4_max_seven_tau"], g57["G4_max_dE0"], g115["G4_max_dE0"]))
w("- **Independent recomputation** (`checks/rd_predict_independent.py`, written after the hash, no function shared with the sealed code; lattice from the repository's edge list, second neighbours derived, Neel values computed as products of eta, `scipy.stats.spearmanr`, own interpolation): the largest absolute difference from the sealed output over %d compared quantities (F, F per coupling, t range, D, rank correlations, every column of the P5 rows, the means) is **%.1e**; the same couplings decide, the same ratios are outside, the same outcomes."
  % (ndiff, maxdiff))
w("- **n = 19 from scratch** (own exact diagonalization, sector dimension %d, the same %d levels): against `out/n19/n19_curves.json` at the 50 couplings |dE0| <= %.0e, |dm_s| <= %.0e, curve points within %.0e (energy) and %.0e (bias); residual of the ground state at most %.0e. Reading the curve from this recomputation changes no ratio by more than %.0e."
  % (nn["dim"], nn["levels"], nn["max_abs_dE0"], nn["max_abs_dms0"], nn["max_abs_curve_de"], nn["max_abs_curve_dms"], nn["max_residual"],
     max(I["sizes"][s]["P5"]["max_abs_ratio_stored_minus_ed"] for s in ("57", "115"))))
w("- **Same recipe as the paper's curves:** `out/n19/n19_curves.json` against `bias_law/inputs/n19_curves.json` at the %d couplings they share: |dE0| <= %.0e, |dm_s| <= %.0e, curve within %.0e (the tolerances of the earlier gate were 1e-8, 1e-6, 1e-5)."
  % (len(nb["shared_couplings"]), nb["max_abs_dE0"], nb["max_abs_dms0"], nb["max_abs_curve"]))
w("")
# ---------------------------------------------------------------- 8
w("## 8. Post hoc (not declared; no rule; nothing here changes an outcome)")
w("")
w("- **The outcome of P5 does not depend on the choice of truth or on the curve file.** With the authors' DMRG as truth at every coupling (instead of this project's references where stored): FAIL, the same %d couplings outside at n = 115, ratios %.4f-%.4f; n = 57 ratios %.4f-%.4f. With the curve recomputed from scratch: FAIL, identical."
  % (len(I["sizes"]["115"]["P5"]["authors_truth_everywhere"]["all"]["outside"]), I["sizes"]["115"]["P5"]["authors_truth_everywhere"]["all"]["ratio_min_deciding"],
     I["sizes"]["115"]["P5"]["authors_truth_everywhere"]["all"]["ratio_max_deciding"], I["sizes"]["57"]["P5"]["authors_truth_everywhere"]["all"]["ratio_min_deciding"],
     I["sizes"]["57"]["P5"]["authors_truth_everywhere"]["all"]["ratio_max_deciding"]))
w("- **Not a borderline failure.** Three of the twelve outside ratios at n = 115 are within 0.01 of the band (Jz = 1.6: %.4f; 1.7: %.4f; 1.9: %.4f); the other nine are %.3f or lower, down to %.4f at Jz = 1.5."
  % tuple([[r["ratio"] for r in s115["P5"]["rows"] if abs(r["Jz"] - j) < 1e-9][0] for j in (1.6, 1.7, 1.9)]
          + [hi(max(r["ratio"] for r in s115["P5"]["rows"] if r["decides_ratio"] and r["ratio"] < 0.74)), a115["ratio_range_deciding"][0]]))
w("- **The point n = 115, Jz = 1.5** has the lowest ratio, a larger energy error per site than its neighbour at 1.4 (%.4f against %.4f) and all %d pairs of Sec. 2 that are not on the Neel side: the published state has a local region (around sites 19 and 89) that is less ordered than the ground state. Without this coupling the ratio condition still fails at n = 115 (%d other couplings outside)."
  % ([r["de"] for r in s115["P5"]["rows"] if abs(r["Jz"] - 1.5) < 1e-9][0], [r["de"] for r in s115["P5"]["rows"] if abs(r["Jz"] - 1.4) < 1e-9][0],
     len(neg115), len(a115["ratios_outside"]) - 1))
w("- **Ratio of the bias to the chord** (the rule does not apply to the chord): at the deciding couplings %.3f-%.3f at n = 57 (%d outside [0.75, 1.3]) and %.3f-%.3f at n = 115 (%d outside: Jz = %s). The chord has smaller mean misses than the curve, but it would not meet the ratio condition at n = 115 either."
  % (lo(D[57]["chord_ratio_deciding"][0]), hi(D[57]["chord_ratio_deciding"][1]), len(D[57]["chord_ratio_outside_deciding"]),
     lo(D[115]["chord_ratio_deciding"][0]), hi(D[115]["chord_ratio_deciding"][1]), len(D[115]["chord_ratio_outside_deciding"]),
     ", ".join("%.1f" % j for j in D[115]["chord_ratio_outside_deciding"])))
w("- **Coupling by coupling,** the curve leaves a smaller miss than the chord at %d of 50 couplings at n = 57 (Jz = %s) and at %d of 50 at n = 115 (Jz = %s); the chord leaves the smaller miss at the other %d and %d (Jz = %s; Jz = %s). The chord wins in the mean because it is the better of the two at small Jz, where the misses are large. The correction with the curve makes no label worse than it was (couplings with corrected miss above raw miss: %d at n = 57, %d at n = 115)."
  % (len(D[57]["curve_better_than_chord_at"]), runs(D[57]["curve_better_than_chord_at"]), len(D[115]["curve_better_than_chord_at"]), runs(D[115]["curve_better_than_chord_at"]),
     50 - len(D[57]["curve_better_than_chord_at"]), 50 - len(D[115]["curve_better_than_chord_at"]),
     runs([r["Jz"] for r in s57["P5"]["rows"] if r["Jz"] not in D[57]["curve_better_than_chord_at"]]),
     runs([r["Jz"] for r in s115["P5"]["rows"] if r["Jz"] not in D[115]["curve_better_than_chord_at"]]),
     len(D[57]["corrected_worse_than_raw_at"]), len(D[115]["corrected_worse_than_raw_at"])))
w("- **How much the basis optimization lowers the energy error** (E_first against E_real, both in the public files; [S] in part: F10, T4): the error per site before the optimization is %.1f to %.1f times the final one at n = 57 (median %.1f) and %.1f to %.1f times at n = 115 (median %.1f); at the deciding couplings %.1f-%.1f and %.1f-%.1f. The declaration's phrase \"five- to tenfold\" describes n = 57; at n = 115 the factor is above ten at %d of the 50 couplings. The final optimization does far more of the work at n = 115, which is where the first-stage curve fails. This is an observation; no test of it was declared or made."
  % (D[57]["de_first_over_de_real"]["min"], D[57]["de_first_over_de_real"]["max"], D[57]["de_first_over_de_real"]["median"],
     D[115]["de_first_over_de_real"]["min"], D[115]["de_first_over_de_real"]["max"], D[115]["de_first_over_de_real"]["median"],
     D[57]["de_first_over_de_real"]["at_deciding"][0], D[57]["de_first_over_de_real"]["at_deciding"][1],
     D[115]["de_first_over_de_real"]["at_deciding"][0], D[115]["de_first_over_de_real"]["at_deciding"][1],
     sum(v > 10 for v in D[115]["de_first_over_de_real"]["per_coupling"].values())))
w("")
# ---------------------------------------------------------------- 9
w("## 9. Re-executed, only compared, not checked")
w("")
w("**Re-executed by this task:** the hash check of the declaration; `checks/make_manifest.py --check`; the sealed `code/run_predict.py` (twice); an independent recomputation of P1-P5 and of the n = 19 comparison from the plain JSON; the exact diagonalization at n = 19 at the 50 couplings, from scratch; gates G2, G3, G4 for the dataset.")
w("")
w("**Only read or compared:** the kept sets of `out/S_sets.json` (fixed by the map task; read through the sealed loader, which checks the file against `out/S_sets.sha256` and the declaration hash; not re-derived here); the gate records of the map task (`out/map_gates.json`, `out/run_map_stdout.txt`); the numbers of declaration Sec. 1 (F4, F7, F8, T3-T5) against the present output, which agree at every value compared (de at Jz = 1.1-1.5; raw misses 4.95 and 4.67 tau at Jz = 1.1; above tau up to Jz = 1.9 and 1.8, above tau/2 up to 2.4 and 2.2; site fraction 0.98 at (115, 1.5)).")
w("")
w("**Not checked:** gate G1 in full (no re-run of the converter); the unit tests of G8 were not re-run (their records are `checks/G8_*`; the tested files are byte-identical to those run, by the manifest); that the published energy and the published labels belong to one and the same state (declaration Sec. 10, point 6: supported by G2 and by the reading of the authors' code, not provable from the files); the authors' DMRG itself, which is the truth for every single site, pair and loop (no new DMRG was run).")
w("")
w("## 10. Files")
w("")
w("| file | what |")
w("|---|---|")
w("| `out/predict/predict_results.json` | output of the sealed code, run 2 (with the kept set) |")
w("| `out/predict/run_predict_stdout.txt` | its printed summary |")
w("| `out/predict/first_run_before_S_sets/` | run 1 (before the kept set existed) |")
w("| `out/predict_real.json` | sealed output verbatim + provenance + independent check + post hoc lines |")
w("| `checks/rd_predict_independent.py`, `.json`, `_stdout.txt` | independent recomputation (written after the hash; decides nothing) |")
w("| `checks/rd_predict_make_results.py` | writes this file and `out/predict_real.json` from the two JSON files above |")
w("| `results/SHA256SUMS_predict.txt` | SHA-256 of the files of this task |")
w("| `DEVIATIONS.md` | dated notes of this task (no code defect; two runs; file names) |")
w("")

os.makedirs(os.path.join(RD, "results"), exist_ok=True)
res_path = os.path.join(RD, "results", "RESULTS_predict.md")
with open(res_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")

# ------------------------------------------------------------------------------------------------ out/predict_real.json
outcomes = []
for n in (57, 115):
    for f in FAMS:
        r = R["sizes"][str(n)]["P1_P3"][f]
        outcomes.append(dict(id="P1-P3 %s n=%d" % (f, n), rule="F >= 0.95", value=r["F"], outcome="HOLDS" if r["holds"] else "DOES NOT HOLD"))
for n in (57, 115):
    for f in FAMS:
        r = R["sizes"][str(n)]["P4"][f]
        outcomes.append(dict(id="P4 %s n=%d" % (f, n), rule="Spearman(D, Jz) <= -0.9", value=r["spearman"], outcome="HOLDS" if r["holds"] else "DOES NOT HOLD"))
outcomes.append(dict(id="P5", rule=R["P5_rule"]["rule"], outcome=R["P5_rule"]["outcome"],
                     parts={"57": dict(mean_miss_tau=a57["mean_miss_tau"], mean_miss_ok=a57["mean_miss_ok"], ratios_ok=a57["ratios_ok"],
                                       ratio_range_deciding=a57["ratio_range_deciding"], ratios_outside=a57["ratios_outside"]),
                            "115": dict(mean_miss_tau=a115["mean_miss_tau"], mean_miss_ok=a115["mean_miss_ok"], ratios_ok=a115["ratios_ok"],
                                        ratio_range_deciding=a115["ratio_range_deciding"], ratios_outside=a115["ratios_outside"])},
                     meaning_for_Sec_V="FAIL: by the declaration (Sec. 5, P5), a fail restricts Sec. V to the first stage, and the paper says so."))
out = dict(R)
out["provenance"] = dict(
    task="rd-predict", date="2026-11-12", note="The keys declaration_sha256, n19_curves_sha256, seen, sizes, variant_post_select, P5_rule and "
    "P5_rule_training_45_reported_only are the output of the sealed code (out/predict/predict_results.json), verbatim. "
    "Everything under provenance, outcomes, gates, independent_recomputation and post_hoc was added after the hash by "
    "checks/rd_predict_make_results.py and decides nothing.",
    command="python -B -I code/run_predict.py --hash=" + decl_sha, runs_utc=t_run,
    sealed_output_sha256=sha(SEALED_PATH), first_run_output_sha256=sha(FIRST), S_sets_sha256=sets_sha,
    code_and_inputs_equal_to_manifest=code_ok, manifest_check="69 lines equal, 0 different, 4 not re-hashed (converted/, source/)",
    environment="Python 3.11.4, numpy 1.26.4, scipy 1.13.1, two threads, laptop")
out["outcomes"] = outcomes
out["gates"] = dict(G1="NOT COMPLETE: converter not re-run on the pinned archive; hashes of the converted files equal the pinned ones",
                    G2_G3_G4_rechecked_here={"57": g57, "115": g115}, G8="passed before the hash (checks/G8_*)")
out["independent_recomputation"] = dict(script="checks/rd_predict_independent.py", max_abs_difference_from_sealed=maxdiff,
                                        n_quantities_compared=ndiff, per_size=I["max_abs_difference_from_sealed"],
                                        n19_from_scratch_vs_stored=nn, n19_out_vs_bias_law_inputs=nb,
                                        P5_rule_recomputed=I["P5_rule_recomputed"],
                                        t_not_positive={s: I["sizes"][s]["t_not_positive"] for s in ("57", "115")})
out["post_hoc"] = dict(note="not declared; no rule; changes no outcome", per_size={str(n): D[n] for n in (57, 115)},
                       P4_increases_between_neighbours=P4_INC,
                       P5_authors_truth_everywhere={s: I["sizes"][s]["P5"]["authors_truth_everywhere"] for s in ("57", "115")})
real_path = os.path.join(RD, "out", "predict_real.json")
with open(real_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, indent=1, default=float)
# the sealed part must have survived verbatim
back = rj(real_path)
assert all(back[k] == R[k] for k in R), "sealed part altered"

files = ["out/predict/predict_results.json", "out/predict/run_predict_stdout.txt", "out/predict/first_run_before_S_sets/predict_results.json",
         "out/predict/first_run_before_S_sets/run_predict_stdout.txt", "out/predict_real.json", "checks/rd_predict_independent.py",
         "checks/rd_predict_independent.json", "checks/rd_predict_independent_stdout.txt", "checks/rd_predict_make_results.py",
         "results/RESULTS_predict.md"]
with open(os.path.join(RD, "results", "SHA256SUMS_predict.txt"), "w", encoding="utf-8", newline="\n") as f:
    for p in files:
        f.write("%s  %s\n" % (sha(os.path.join(RD, *p.split("/"))), p))
print("written:", res_path, real_path, "(%d lines)" % len(L))
