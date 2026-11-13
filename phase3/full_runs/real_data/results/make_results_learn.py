# real_data / results / make_results_learn.py   (own code; task rd-learn; 2026-11-12; written AFTER the hash)
#
# Builds, from the outputs of the sealed code (out/learn/*, read verbatim):
#   results/RESULTS_learn.md, out/learn_real.json, results/SHA256SUMS_learn.txt,
#   out/learn/DEVIATIONS_section_rd-learn.md (text to append to DEVIATIONS.md) and the review report rd-learn.md.
# No outcome, interval, score or threshold of the declaration is recomputed here. The lines marked "post hoc" come from
# checks/rd_learn_independent.py, except the "grid-only floor", computed here from out/S_sets.json and out/map_real.json.
# Display rule: ends of ranges and bounds are rounded outward.
#
#   python -B -I results/make_results_learn.py
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)
WORK = os.path.dirname(os.path.dirname(os.path.dirname(RD)))
L = os.path.join(RD, "out", "learn")
REPORT = os.path.join(WORK, "paper", "reviews", "R10_2026-11-12", "reports", "rd-learn.md")
TEST = [1.1, 1.2, 1.3, 1.4]


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
        return f.read()


def up(x, d=3):
    return math.ceil(x * 10 ** d - 1e-9) / 10 ** d


def dn(x, d=3):
    return math.floor(x * 10 ** d + 1e-9) / 10 ** d


def fu(x, d=3):
    return ("%." + str(d) + "f") % up(x, d)


def fd(x, d=3):
    return ("%." + str(d) + "f") % dn(x, d)


def rng(a, b, d=3):
    return "%s-%s" % (fd(a, d), fu(b, d))


def es(s):
    return str(s).replace(".", ",")


def kth(vals, k):
    s = sorted(float(v) for v in vals)
    return s[-1] if k > len(s) else s[k - 1]


DECL = sha(os.path.join(RD, "DECLARATION.md"))
assert DECL == rt(os.path.join(RD, "DECLARATION.sha256")).split()[0].lower(), "declaration hash mismatch"
SETS_SHA = sha(os.path.join(RD, "out", "S_sets.json"))
assert SETS_SHA == rt(os.path.join(RD, "out", "S_sets.sha256")).split()[0].lower(), "S_sets hash mismatch"
RES = rj(os.path.join(L, "results_cheap.json")); P2 = rj(os.path.join(L, "prop2_cubic.json"))
F2 = rj(os.path.join(L, "f2_floor.json")); F3 = rj(os.path.join(L, "f3_constructive.json")); RU = rj(os.path.join(L, "f1_rules.json"))
MLP = rj(os.path.join(L, "parts", "f1_mlp_pilot3_n57_ood.json")); IC = rj(os.path.join(L, "independent_check.json"))
SETS = rj(os.path.join(RD, "out", "S_sets.json")); MAP = rj(os.path.join(RD, "out", "map_real.json"))
assert F3["sets_sha256"] == SETS_SHA and F2["sets_sha256"] == SETS_SHA and F3["declaration_sha256"] == DECL
SEED = F3["seed"]

# ---------------------------------------------------------------- manifest lines of Sec. 11, hashed again (plain files)
man_equal, man_diff, man_skipped = 0, [], 0
in_block = False
for line in rt(os.path.join(RD, "DECLARATION.md")).splitlines():
    if line.startswith("```"):
        in_block = not in_block; continue
    p = line.split("  ", 1)
    if not in_block or len(p) != 2 or len(p[0]) != 64 or p[1].startswith("tree:"):
        continue
    if p[1].startswith("source/"):
        man_skipped += 1; continue
    fp = os.path.normpath(os.path.join(RD, p[1]))
    if sha(fp) == p[0]:
        man_equal += 1
    else:
        man_diff.append(p[1])
CODE = ["code/run_learn.py", "code/rd_f23.py", "code/rd_learn_ibm.py", "code/rd_prop2_cubic.py", "code/rd_learn_parts.py", "code/rd_common.py"]
CODE_SHA = {c: sha(os.path.join(RD, c)) for c in CODE}
stdout_cheap = rt(os.path.join(L, "run_learn_cheap_stdout.txt")).splitlines()
T_CHEAP = (stdout_cheap[0].split()[1], stdout_cheap[-1].split()[1])
T_MLP = (rt(os.path.join(L, "parts", "time_mlp57_ood_start.txt")).strip(), rt(os.path.join(L, "parts", "time_mlp57_ood_end.txt")).strip())


# ---------------------------------------------------------------- numbers (all from the sealed outputs)
def blk(rows):
    if rows is None:
        return None
    return dict(n=len(rows), truth_covered=int(sum(bool(r["covM_truth"]) for r in rows)),
                label_covered=int(sum(bool(r["covM_emu"]) for r in rows)),
                site_truth=float(np.mean([r["covZ_truth"] for r in rows])), site_label=float(np.mean([r["covZ_emu"] for r in rows])),
                width_tau=[min(r["widthM_tau"] for r in rows), max(r["widthM_tau"] for r in rows)],
                site_width_tau_median=float(np.median([r["widthZ_tau_median"] for r in rows])),
                miss_tau=[min(r["miss_ms_over_tau"] for r in rows), max(r["miss_ms_over_tau"] for r in rows)],
                n_miss_above_tau=int(sum(r["miss_ms_over_tau"] > 1 for r in rows)))


SM = {}
for n in ("57", "115"):
    S = RES["sizes"][n]; s = dict(models={})
    for mk in ("poly3_invJ", "null_nn"):
        M = S["models"][mk]
        s["models"][mk] = dict(real=dict(test=blk(M["ood_emulated"]["rows"]), ind=blk(M["indist_emulated"]["rows"])),
                               control=dict(test=blk(M["ood_exact_control"]["rows"]), ind=blk(M["indist_exact_control"]["rows"])))
    if n == "57":
        s["models"]["mlp_pilot3"] = dict(real=dict(test=blk(MLP["emulated"]["rows"]), ind=None),
                                         control=dict(test=blk(MLP["exact_control"]["rows"]), ind=None))
    p = P2["sizes"][n]; ps = p["summary"]
    s["prop2"] = dict(n_queries=ps["n_queries"], n_answered_rule_c=ps["n_answered_rule_c"], not_pinned=len(ps["not_pinned_a"]), pinned=len(ps["pinned_a"]),
                      undecided=[r["Jz"] for r in p["indist"] + p["ood"] if r["band_a"] == "UNDECIDED"],
                      abstain_definite=len(ps["abstain_definite"]), abstain_default=len(ps["abstain_default"]),
                      upper_kinds={k: sum(1 for v in p["intervals"].values() if v and v["upper_kind"] == k) for k in ("exact", "like_for_like", "interpolated")},
                      upper_kinds_training={k: sum(1 for j, v in p["intervals"].items() if v and float(j) >= 1.6 and v["upper_kind"] == k) for k in ("exact", "like_for_like", "interpolated")},
                      W_lo_tau_test=ps["W_lo_tau_ood"], W_hi_tau_test_indicative=ps["W_hi_tau_ood"], W_lo_tau_ind=ps["W_lo_tau_indist"],
                      width_b_lo_tau_test=ps["width_b_lo_tau_ood"], width_b_hi_tau_test_indicative=ps["width_b_hi_tau_ood"],
                      width_b_lo_tau_ind=ps["width_b_lo_tau_indist"], truth_covered_b_lo_ind=ps["truth_covered_b_lo_indist"],
                      truth_covered_b_lo_test=ps["truth_covered_b_lo_ood"], label_in_upper=ps["sanity_label_in_outer"],
                      truth_in_upper=ps["sanity_truth_in_outer"], linearity_check=p["linearity_check_max_abs"],
                      any_query_indicative=all((r["W_indicative"] or r["q_indicative"]) for r in p["indist"] + p["ood"]))
    r = RU["sizes"][n]
    s["L1"] = r["L1"]; s["L2"] = r["L2"]; s["L3"] = dict(r["L3"]); s["apart"] = r["apart"]
    f = F2["sizes"][n]
    rows = {round(x["Jz"], 1): x for x in MAP["rows"] if x["n"] == int(n) and x["label"] == "m_s"}
    iv = {round(float(k), 1): v for k, v in SETS["sizes"][n]["intervals"].items()}
    R = [j for j in sorted(iv) if j >= 1.6]
    reev = [j for j in R if rows[j]["explicit"] and rows[j]["explicit"].get("rests_on_re_evaluated_energy")]
    wl = {j: (iv[j]["lower"]["hi"] - iv[j]["lower"]["lo"]) if iv[j]["lower"] else 0.0 for j in R}
    floor_grid = kth([0.0 if j in reev else wl[j] for j in R], f["k"])
    tauA = {round(float(k), 1): f["floor"] / v for k, v in f["floor_over_tau"].items()}       # tau(x) of the authors' DMRG
    s["f2"] = dict(m=f["m"], k=f["k"], floor=f["floor"], holds=f["holds"], holds_every=f["holds_at_every_coupling"],
                   holds_held_out=f["holds_in_distribution_held_out"], test=[f["floor_over_tau"]["%.1f" % j] for j in TEST],
                   all_min=min(f["floor_over_tau"].values()), held_out=[min(v["floor_over_tau"] for v in f["in_distribution_held_out"].values()),
                                                                         max(v["floor_over_tau"] for v in f["in_distribution_held_out"].values())],
                   missing=f["lower_width_missing_taken_as_0"], widest4=IC["sizes"][n]["f2"]["couplings_of_the_four_widest"],
                   n_training_labels_on_re_evaluated_energy=len(reev),
                   posthoc_floor_without_re_evaluated=floor_grid, posthoc_floor_without_re_evaluated_test=[floor_grid / tauA[j] for j in TEST])
    s["f3"] = dict(S_p=F3["sizes"][n]["S_p_name"], primary=F3["sizes"][n]["primary"], sets={})
    for name, x in F3["sizes"][n]["sets"].items():
        if x["status"] != "RUN":
            s["f3"]["sets"][name] = dict(status=x["status"], size=x["size"]); continue
        d = dict(status="RUN", size=x["size"], range=[x["couplings"][0], x["couplings"][-1]], n_train=x["n_train"], n_cal=x["n_cal"], n_query=x["n_query"],
                 k=x["k"], outcome_M1_M2=x["outcome_M1_M2"], outcome_M0=x["outcome_M0_control"], g7=x["gate_G7_outside_interval"], models={})
        for m in ("M1", "M2", "M0"):
            a = x["models"][m]
            d["models"][m] = {k: v for k, v in a.items() if k != "splits"}
            d["models"][m]["n_splits_W"] = int(round(a["frac_splits_W"] * a["n_splits"])); d["models"][m]["n_pairs_C"] = int(round(a["frac_pairs_C"] * a["n_pairs"]))
        s["f3"]["sets"][name] = d
    s["sets"] = {k: SETS["sizes"][n][k] for k in ("S", "S_3_4", "S_1_2", "S_p", "S_p_name")}
    s["like_for_like_block"] = dict(answered_m_s=S["abstention"]["answered_m_s"], answered_local=S["abstention"]["answered_local"],
                                    cubic=S["abstention"].get("poly3_invJ"))
    s["split_robustness"] = S["split_robustness_ood"]
    SM[n] = s

c57, c115 = SM["57"]["models"]["poly3_invJ"], SM["115"]["models"]["poly3_invJ"]
p57 = SM["57"]["f3"]["sets"][SM["57"]["f3"]["S_p"]]; p115 = SM["115"]["f3"]["sets"][SM["115"]["f3"]["S_p"]]
ic57 = IC["sizes"]["57"]["f3"]; ic115 = IC["sizes"]["115"]["f3"]
NAME = {"S": "S", "S_3_4": "S_3/4", "S_1_2": "S_1/2"}
worst = max(IC["largest_difference_from_sealed_output"].values())
FIT_S = None
try:
    import datetime
    a, b = (datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ") for x in T_MLP)
    FIT_S = (b - a).total_seconds() / 92.0
except Exception:
    pass

NOT_COMPUTED = [
    dict(what="pilot perceptron, n = 57, in distribution (45 held-out couplings, real and DMRG labels)", fits=4050,
         reason="cost: about %.0f CPU-hours at the %.1f s per fit measured in this run; outside the time allowed to this task" % (4050 * FIT_S / 3600, FIT_S),
         how="python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=H --model=mlp_pilot3 --size=57 --part=i/k (i = 0..k-1), then --assemble=k, then run_learn.py --stage=merge and --stage=rules; the test-range piece is already in out/learn/parts/"),
    dict(what="pilot perceptron, n = 115 (secondary), test range and in distribution", fits=4142,
         reason="cost: more than 22 CPU-hours", how="the same commands with --size=115 (first --part=ood)"),
    dict(what="the dataset paper's architecture 1, n = 57, test range (real and DMRG labels)", fits=92,
         reason="cost: about 13 CPU-hours (520 s per fit measured before the hash on an idle core)", how="python -B -I code/run_learn.py --hash=H --stage=f1_ibm57, then --stage=merge"),
]

# ---------------------------------------------------------------- abstract sentences (every number from SM / IC)
chg = ic57[SM["57"]["f3"]["S_p"]]["truth_change_over_tau"]
CHG = "%.2f" % chg[1]                       # a measured value (not a bound): rounded to the nearest
SENT1 = ("At 57 qubits, standard conformal intervals calibrated on the public labels contain %d of %d held-out labels but the reference (DMRG) value "
         "of the staggered magnetization at %d of the %d training couplings and at %d of the %d test couplings, where the cubic model misses it by "
         "%s to %s times the tolerance." % (c57["real"]["ind"]["label_covered"], c57["real"]["ind"]["n"], c57["real"]["ind"]["truth_covered"], c57["real"]["ind"]["n"],
                                           c57["real"]["test"]["truth_covered"], c57["real"]["test"]["n"], fd(c57["real"]["test"]["miss_tau"][0], 2), fu(c57["real"]["test"]["miss_tau"][1], 2)))
wmin = min(p57["models"][m]["width_tau_min"] for m in ("M1", "M2")); wmax = max(p57["models"][m]["width_tau_max"] for m in ("M1", "M2"))
SENT2 = ("Calibrated instead on the %d labels that the published energy and site magnetizations certify to within half the tolerance (Jz = %.1f to %.1f), "
         "intervals built from the exact energy bounds were narrower than the tolerance in %d of %d random splits (%s to %s of it) and contained the "
         "reference value in %d of %d cases, for both declared models; the true value varies by only %s of the tolerance over that range, so this shows that "
         "the guarantee survives the learner and its calibration, not that a hard function was learned." % (
             p57["size"], p57["range"][0], p57["range"][1], min(p57["models"][m]["n_splits_W"] for m in ("M1", "M2")), p57["models"]["M1"]["n_splits"],
             fd(wmin, 2), fu(wmax, 2), min(p57["models"][m]["n_pairs_C"] for m in ("M1", "M2")), p57["models"]["M1"]["n_pairs"], CHG))
SENT_ALT = ("With all 45 public training labels in the calibration set, no learner using a constant-width score can return a guaranteed interval narrower than "
            "%s times the tolerance at the test couplings (57 qubits; %s at 115)." % (fd(min(SM["57"]["f2"]["test"]), 2), fd(min(SM["115"]["f2"]["test"]), 2)))

# ---------------------------------------------------------------- RESULTS_learn.md
o = []
A = o.append
A("# Real data of arXiv:2606.15983: RESULTS of the learning tests on the real labels (declaration Sec. 7: f1, f2, f3)")
A("")
A("Task `rd-learn`, 2026-11-12. Declaration: `real_data/DECLARATION.md`, SHA-256 `%s` (checked before anything was read)." % DECL)
A("Every outcome below is the output of the sealed code `code/run_learn.py` (and its sealed helpers), run unchanged. No rule was changed.")
A("Nested sets and label intervals: `out/S_sets.json`, SHA-256 `%s` (written by the map task before any learning number; equal to `out/S_sets.sha256`)." % SETS_SHA)
A("")
A("## Resumen en español (ocho líneas)")
A("")
A("1. Se comprobó que la declaración sellada no había cambiado (su huella coincide) y que el archivo de conjuntos ya estaba escrito, con su huella, antes de calcular nada. El programa sellado se ejecutó tal cual, sin tocarlo.")
A("2. Modelo entrenado con las etiquetas reales: fuera del rango de entrenamiento falla el valor verdadero por entre %s y %s veces la tolerancia a 57 cúbits (entre %s y %s a 115), y los intervalos de confianza habituales no contienen el valor verdadero en ninguna de las cuatro constantes de prueba. Las tres predicciones L1, L2 y L3 SE CUMPLEN." % (
    es(fd(c57["real"]["test"]["miss_tau"][0], 2)), es(fu(c57["real"]["test"]["miss_tau"][1], 2)), es(fd(c115["real"]["test"]["miss_tau"][0], 2)), es(fu(c115["real"]["test"]["miss_tau"][1], 2))))
A("3. Dentro del rango de entrenamiento esos intervalos habituales contienen %d de %d etiquetas nuevas, pero el valor verdadero en %d de %d (57 cúbits) y en %d de %d (115): aciertan la etiqueta y fallan la verdad." % (
    c57["real"]["ind"]["label_covered"], c57["real"]["ind"]["n"], c57["real"]["ind"]["truth_covered"], c57["real"]["ind"]["n"], c115["real"]["ind"]["truth_covered"], c115["real"]["ind"]["n"]))
A("4. Control con etiquetas de referencia (el cálculo clásico de los autores): dentro del rango contiene la verdad en %d de %d; fuera del rango tampoco la contiene (%d de %d), aunque falla por poco (entre %s y %s de la tolerancia). Por eso L2 sola no separa «etiquetas sesgadas» de «extrapolación»; lo que las separa es el tamaño del fallo (L1)." % (
    c57["control"]["ind"]["truth_covered"], c57["control"]["ind"]["n"], c57["control"]["test"]["truth_covered"], c57["control"]["test"]["n"],
    es(fd(c57["control"]["test"]["miss_tau"][0], 2)), es(fu(c57["control"]["test"]["miss_tau"][1], 2))))
A("5. Suelo que no depende del modelo (f2): calibrando con las 45 etiquetas, ningún método puede dar un intervalo garantizado más estrecho que %s tolerancias en las constantes de prueba a 57 cúbits (%s a 115). SE CUMPLE. Con los intervalos de energía de las 45 etiquetas, el intervalo del modelo cúbico mide como mínimo entre %s y %s tolerancias, según la constante (L3)." % (
    es(fd(min(SM["57"]["f2"]["test"]), 2)), es(fd(min(SM["115"]["f2"]["test"]), 2)), es(fd(min(SM["57"]["L3"]["width_tau"].values()), 2)), es(fu(max(SM["57"]["L3"]["width_tau"].values()), 2))))
A("6. Prueba constructiva (f3), conjunto principal (las %d etiquetas certificadas a media tolerancia, Jz de %s a %s, 57 cúbits): PASA. Intervalos de entre %s y %s tolerancias en %d de %d particiones y el valor verdadero dentro en %d de %d casos, con los dos modelos declarados. A 115 cúbits (%d etiquetas, de %s a %s): PASA." % (
    p57["size"], es(p57["range"][0]), es(p57["range"][1]), es(fd(wmin, 2)), es(fu(wmax, 2)), min(p57["models"][m]["n_splits_W"] for m in ("M1", "M2")), p57["models"]["M1"]["n_splits"],
    min(p57["models"][m]["n_pairs_C"] for m in ("M1", "M2")), p57["models"]["M1"]["n_pairs"], p115["size"], es(p115["range"][0]), es(p115["range"][1])))
sS, s34 = SM["57"]["f3"]["sets"]["S"], SM["57"]["f3"]["sets"]["S_3_4"]
A("7. Con el mismo relieve: a 57 cúbits, en el conjunto completo de etiquetas certificadas (%d) y en el intermedio (%d) NO PASA, por anchura (solo %d y entre %d y %d de 200 particiones); el modelo de control, entrenado también con etiquetas sin certificar, pasa igual que los otros; y en el rango del conjunto principal el valor verdadero cambia solo %s tolerancias. La prueba muestra que la garantía sobrevive al aprendizaje, no que se haya aprendido una función difícil." % (
    sS["size"], s34["size"], max(sS["models"][m]["n_splits_W"] for m in ("M1", "M2")), min(s34["models"][m]["n_splits_W"] for m in ("M1", "M2")),
    max(s34["models"][m]["n_splits_W"] for m in ("M1", "M2")), es(CHG)))
A("8. Un segundo programa, escrito aparte, reproduce estos números (diferencia máxima %.0e). No se halló ningún defecto en el programa sellado ni se cambió regla alguna. Quedan sin calcular, por coste, la red pequeña dentro del rango y a 115 cúbits y la red grande del artículo original (de la red pequeña solo hay las cuatro constantes de prueba a 57 cúbits). Dos comprobaciones de la tarea del mapa siguen incompletas (G1 y la primera parte de G6)." % worst)
A("")
A("## Summary (English)")
A("")
A("| analysis | declared rule | outcome |")
A("|---|---|---|")
for n in ("57", "115"):
    s = SM[n]; tag = "decides" if n == "57" else "reported"
    A("| L1, n = %s (%s) | the cubic misses the true m_s by more than tau at each of 1.1-1.4 | **%s** (%s tau) |" % (
        n, tag, "HOLDS" if s["L1"]["holds"] else "DOES NOT HOLD", ", ".join("%.2f" % s["L1"]["miss_tau"]["%.1f" % j] for j in TEST)))
    A("| L2, n = %s (%s) | standard intervals calibrated on the real labels cover the truth at none of the four test couplings | **%s** (covered at %d of 4) |" % (
        n, tag, "HOLDS" if s["L2"]["holds"] else "DOES NOT HOLD", sum(s["L2"]["covered"].values())))
    A("| L3, n = %s (%s) | the 2(b) intervals calibrated on all 45 labels are wider than tau at every coupling (lower version) | **%s** (2q = %s tau over the 49 couplings) |" % (
        n, tag, "HOLDS" if s["L3"]["holds"] else "DOES NOT HOLD", rng(min(s["L3"]["width_tau"].values()), max(s["L3"]["width_tau"].values()), 2)))
for n in ("57", "115"):
    s = SM[n]["f2"]
    A("| (f2) floor, n = %s | the floor w_(%d) of the %d lower widths exceeds tau(x) at each test query | **%s** (floor = %s tau at 1.1-1.4; at least %s tau at every coupling) |" % (
        n, s["k"], s["m"], "HOLDS" if s["holds"] else "DOES NOT HOLD", " / ".join(fd(v, 2) for v in s["test"]), fd(s["all_min"], 2)))
for n in ("57", "115"):
    f3 = SM[n]["f3"]
    for name in ("S_1_2", "S_3_4", "S"):
        x = f3["sets"][name]; prim = (name == f3["S_p"])
        label = "(f3) %s n = %s, set %s%s" % ("**PRIMARY**," if (prim and n == "57") else "secondary,", n, NAME[name], " = S_p" if prim else "")
        if x["status"] != "RUN":
            A("| %s | (W) and (C) for M1 and M2 | NOT RUN: %d couplings, fewer than 15 |" % (label, x["size"])); continue
        det = "; ".join("%s: (W) %d of %d splits, (C) %d of %d pairs, 2q = %s tau, largest miss %s tau" % (
            m, x["models"][m]["n_splits_W"], x["models"][m]["n_splits"], x["models"][m]["n_pairs_C"], x["models"][m]["n_pairs"],
            rng(x["models"][m]["width_tau_min"], x["models"][m]["width_tau_max"]), fu(x["models"][m]["largest_miss_tau"])) for m in ("M1", "M2"))
        A("| %s (%d couplings, Jz %.1f-%.1f; %d train / %d calibration / %d query) | (W) 2q <= tau(x) at every query in >= 90 %% of the splits and (C) truth within q in >= 90 %% of the pairs, both M1 and M2 | **%s** (%s) |" % (
            label, x["size"], x["range"][0], x["range"][1], x["n_train"], x["n_cal"], x["n_query"], x["outcome_M1_M2"], det))
        m = x["models"]["M0"]
        A("| control M0 on the same splits | same rule | **%s** ((W) %d of %d, (C) %d of %d, 2q = %s tau, largest miss %s tau) |" % (
            x["outcome_M0"], m["n_splits_W"], m["n_splits"], m["n_pairs_C"], m["n_pairs"], rng(m["width_tau_min"], m["width_tau_max"]), fu(m["largest_miss_tau"])))
A("| (f1) models | cubic, nearest-neighbour null, pilot perceptron, architecture 1 (n = 57, test range) | cubic and null: complete at both sizes. Perceptron: test range at n = 57 only. **Not computed (cost):** perceptron in distribution and at n = 115; architecture 1 (Sec. 3.6). L1-L3 are decided on the cubic (declaration Sec. 12, line 10). |")
A("")
A("**Gate notes, printed with every result (declaration Sec. 12, line 14).** G1 is NOT COMPLETE: the converter was not re-run on the pinned archive; the converted files have the pinned SHA-256 (checked by the sealed loader at every read). "
  "The first part of G6 is NOT COMPLETE with nothing checked (no tensors on the laptop): it concerns every number of the *lower version* (the floor of f2, L3, W_lo and 2q_lo of Proposition 2), "
  "because the explicit-state interval of %d (n = 57) and %d (n = 115) of the 45 training labels rests on energies re-evaluated by the linear rule H = A + Jz B (flag `rests_on_re_evaluated_energy` of the map rows). "
  "G2, G3, G4, G5, the second part of G6 and G7 passed in the map task. The exact intervals used by (f3) rest on certificates (G5) and do not depend on G6." % (
      SM["57"]["f2"]["n_training_labels_on_re_evaluated_energy"], SM["115"]["f2"]["n_training_labels_on_re_evaluated_energy"]))
A("")
A("**Hypothesis behind every exact interval (declaration Sec. 10, item 6):** the published energy and the published site magnetizations are expectation values of one and the same state.")
A("")
A("**The limit that the declaration requires with the result of (f3):** between Jz = 4 and 6 the true m_s changes by 0.4 tau (measured here: %s tau at n = 57, %s at n = 115; over the primary set, Jz = %.1f-%.1f, %s tau). "
  "The test shows that the intervals survive the learner and its calibration where labels are certified. It does not show that a hard function was learned." % (
      rng(*IC["sizes"]["57"]["truth_change_4_to_6_over_tau"]), rng(*IC["sizes"]["115"]["truth_change_4_to_6_over_tau"]), p57["range"][0], p57["range"][1], rng(*chg)))
A("")
A("Marks on numbers: **[S]** already seen before the hash (item of declaration Sec. 1 in brackets); **[M]** fixed by the map task after the hash and before any learning number (the sets and the label intervals); "
  "**[N]** not seen and not computed before the hash. Unless marked otherwise, every learning number below is **[N]** (declaration Sec. 1: no learning result on real labels and no interval width at a real energy had been seen).")
A("")
A("## 1. What was run")
A("")
A("- `DECLARATION.sha256` equals the SHA-256 of `DECLARATION.md` (`sha256sum`, the gate of the sealed code, and this script). `python -B -I checks/make_manifest.py --check` before the runs: 69 lines of Sec. 11 equal to the files on disk, 0 different, 4 not re-hashed there. Hashed again by this script after the runs: %d plain-file lines of Sec. 11 equal, %d different%s (the archive under `source/` was not re-hashed; tree digests not recomputed here)." % (
    man_equal, len(man_diff), (" " + str(man_diff)) if man_diff else ""))
A("- `out/S_sets.json` existed with SHA-256 `%s`, equal to `out/S_sets.sha256` and to the value announced by the map task, before any learning number was computed; the sealed stages `prop2`, `f2`, `f3` refuse to run otherwise." % SETS_SHA)
A("- Command 1: `python -B -I code/run_learn.py --hash=%s --stage=cheap` (stages f1_cheap, prop2, f2, f3, rules), %s to %s UTC. Seed %d (first eight hex digits of the hash)." % (DECL, T_CHEAP[0], T_CHEAP[1], SEED))
A("- Command 2: `python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=... --model=mlp_pilot3 --size=57 --part=ood` (the perceptron, test range, real and DMRG labels; 92 fits), %s to %s UTC (%.1f s per fit on the shared laptop)." % (T_MLP[0], T_MLP[1], FIT_S))
A("- Python 3.11.4, numpy 1.26.4, scipy 1.13.1 (as at gate G8), one thread per process, laptop only.")
A("- Sealed code, hashed again after the runs and equal to Sec. 11: " + ", ".join("`%s` `%s...`" % (c, CODE_SHA[c][:12]) for c in CODE) + ".")
A("- Outputs of the sealed code (`out/learn/`): `results_cheap.json`, `prop2_cubic.json`, `f2_floor.json`, `f3_constructive.json`, `f1_rules.json`, `parts/f1_mlp_pilot3_n57_ood.json`; copied verbatim into `out/learn_real.json` with provenance, the independent check and the post hoc lines under separate keys. SHA-256 of every file: `results/SHA256SUMS_learn.txt`.")
A("- Truth in this section of the declaration: the authors' DMRG at all couplings (truth and tau(x) in L1-L3, (f2), (W), (C)); membership of S, S_3/4, S_1/2 uses the tau of Sec. 0 (Sec. 12, line 1).")
A("- No code defect was found. Nothing listed in Sec. 11 was changed. Dated notes of this task: `DEVIATIONS.md`.")
A("")
A("## 2. Inputs fixed before any learning number [M]")
A("")
A("| size | set | couplings | Jz range | exact interval width (tau) | largest miss of a real label in the set (tau) [S, F7] | true m_s changes over the set by (tau) |")
A("|---|---|---|---|---|---|---|")
for n in ("57", "115"):
    for name in ("S", "S_3_4", "S_1_2"):
        x = IC["sizes"][n]["f3"][name]
        A("| %s | %s%s | %d | %.1f-%.1f | %s | %s | %s |" % (n, NAME[name], " = **S_p**" if name == SM[n]["f3"]["S_p"] else "", x["size"], x["range"][0], x["range"][1],
                                                       rng(*x["exact_width_tau"]), fu(x["label_miss_tau_max"]), rng(*x["truth_change_over_tau"])))
A("")
A("- S: training couplings whose m_s row is CERTIFIED (exact) with the reference tolerance, stored certificates only; S_3/4 and S_1/2: exact interval at most 3/4 and 1/2 of tau wide; S_p: the most stringent nested set with at least 15 couplings (decided before the hash).")
e34 = SETS["sizes"]["57"]["intervals"]["3.4"]["exact"]
A("- n = 57, Jz = 3.4 has an exact interval %.4f tau wide and is therefore not in S (S starts at 3.5). At n = 115, S = S_3/4 (the same 21 couplings; their splits differ, being drawn with different seeds)." % e34["width_over_tau"])
A("- Exact intervals exist at %d couplings (n = 57) and %d (n = 115); explicit-state (lower) intervals at all 50 couplings of both sizes. The intervals of `out/S_sets.json` equal those of the m_s rows of `out/map_real.json` (largest difference %.1e at n = 57, %.1e at n = 115), and S equals the CERTIFIED (exact) training rows of that file (own check, Sec. 6)." % (
    IC["sizes"]["57"]["inputs"]["exact_intervals"], IC["sizes"]["115"]["inputs"]["exact_intervals"],
    IC["sizes"]["57"]["inputs"]["max_abs_diff_intervals_and_labels_vs_map_real"], IC["sizes"]["115"]["inputs"]["max_abs_diff_intervals_and_labels_vs_map_real"]))
A("")
A("## 3. (f1) The realistic test: standard conformal prediction on the real labels")
A("")
A("Standard conformal, alpha = 0.1, plain jackknife over couplings. Test range: trained and calibrated on the 45 training labels, queried at Jz = 1.1-1.4. In distribution: each training coupling held out in turn (44 labels). "
  "m_s is derived from the per-site model. \"New real labels\" are the held-out real labels (test range: the real labels at 1.1-1.4). Width = 2q / tau(x). Control: the same pipeline trained and calibrated on the authors' DMRG labels.")
A("")
A("### 3.1 Every model")
A("")
A("| size | model | labels | range | new real labels covered (m_s) | truth covered (m_s) | sites: labels / truth covered | width 2q (tau), m_s | miss of the prediction (tau), m_s | queries missed by more than tau |")
A("|---|---|---|---|---|---|---|---|---|---|")
MN = {"poly3_invJ": "cubic in 1/Jz (primary)", "null_nn": "nearest-neighbour null", "mlp_pilot3": "pilot perceptron"}
for n in ("57", "115"):
    for mk, M in SM[n]["models"].items():
        for src, sname in (("real", "real"), ("control", "DMRG (control)")):
            for rk, rname in (("test", "test 1.1-1.4"), ("ind", "in distribution")):
                b = M[src][rk]
                if b is None:
                    A("| %s | %s | %s | %s | not computed (cost) | not computed | not computed | not computed | not computed | not computed |" % (n, MN[mk], sname, rname)); continue
                A("| %s | %s | %s | %s | %s | **%d of %d** | %s | %s | %s | %d of %d |" % (
                    n, MN[mk], sname, rname, ("%d of %d" % (b["label_covered"], b["n"])) if src == "real" else "n/a", b["truth_covered"], b["n"],
                    ("%.3f / %.3f" % (b["site_label"], b["site_truth"])) if src == "real" else ("n/a / %.3f" % b["site_truth"]),
                    rng(*b["width_tau"]), rng(b["miss_tau"][0], b["miss_tau"][1], 2), b["n_miss_above_tau"], b["n"]))
A("| 57 | architecture 1 of the dataset paper | real and DMRG | test 1.1-1.4 | not computed (cost) | not computed | not computed | not computed | not computed | not computed |")
A("| 115 | pilot perceptron | real and DMRG | both | not computed (cost) | not computed | not computed | not computed | not computed | not computed |")
A("")
A("Reading, with failures and passes side by side:")
A("")
A("- **In distribution the standard intervals track the labels, not the truth.** Cubic, n = 57: %d of %d held-out real labels are covered (nominal level 0.9), the truth at %d of %d; n = 115: %d of %d labels, the truth at %d of %d. The intervals are %s tau wide (n = 57), narrower than the bias of the labels." % (
    c57["real"]["ind"]["label_covered"], c57["real"]["ind"]["n"], c57["real"]["ind"]["truth_covered"], c57["real"]["ind"]["n"],
    c115["real"]["ind"]["label_covered"], c115["real"]["ind"]["n"], c115["real"]["ind"]["truth_covered"], c115["real"]["ind"]["n"], rng(*c57["real"]["ind"]["width_tau"])))
A("- **In the test range nothing is covered.** Cubic on real labels: truth at 0 of 4 at both sizes; the real labels at 1.1-1.4 themselves at %d of 4 (n = 57) and %d of 4 (n = 115)." % (c57["real"]["test"]["label_covered"], c115["real"]["test"]["label_covered"]))
A("- **The control does not cover the truth in the test range either** (0 of 4 at both sizes): trained on DMRG labels the cubic misses the truth by %s tau (n = 57) and %s tau (n = 115) with intervals %s tau wide. "
  "L2 therefore holds for the real labels *and* would hold for exact labels: by itself it does not separate biased labels from extrapolation error. What separates them is the size of the miss: %s tau with the real labels (L1) against at most %s tau with exact labels." % (
      rng(*c57["control"]["test"]["miss_tau"], 2), rng(*c115["control"]["test"]["miss_tau"], 2), rng(*c57["control"]["test"]["width_tau"]),
      rng(*c57["real"]["test"]["miss_tau"], 2), fu(c57["control"]["test"]["miss_tau"][1], 2)))
A("- In distribution the control behaves as designed: truth covered at %d of %d (n = 57) and %d of %d (n = 115), largest miss %s tau." % (
    c57["control"]["ind"]["truth_covered"], c57["control"]["ind"]["n"], c115["control"]["ind"]["truth_covered"], c115["control"]["ind"]["n"], fu(max(c57["control"]["ind"]["miss_tau"][1], c115["control"]["ind"]["miss_tau"][1]), 4)))
nn57 = SM["57"]["models"]["null_nn"]; mlp = SM["57"]["models"]["mlp_pilot3"]
A("- Nearest-neighbour null, n = 57, in distribution: truth covered at %d of %d with intervals %s tau wide (wide enough to contain the bias at large Jz); test range: 0 of 4, miss %s tau." % (
    nn57["real"]["ind"]["truth_covered"], nn57["real"]["ind"]["n"], rng(*nn57["real"]["ind"]["width_tau"]), rng(*nn57["real"]["test"]["miss_tau"], 2)))
A("- Pilot perceptron, n = 57, test range only: truth covered at %d of 4, miss %s tau with real labels; with DMRG labels it still misses by %s tau (truth covered at %d of 4): at these couplings the perceptron extrapolates poorly whatever the labels." % (
    mlp["real"]["test"]["truth_covered"], rng(*mlp["real"]["test"]["miss_tau"], 2), rng(*mlp["control"]["test"]["miss_tau"], 2), mlp["control"]["test"]["truth_covered"]))
A("")
A("### 3.2 The cubic, coupling by coupling, with Proposition 2(a) and (b) at the real intervals")
A("")
A("Columns: miss of the real label [S, F7]; miss of the cubic's prediction; standard interval 2q; whether it contains the truth / the held-out real label; Proposition 2(a) band W = sum_j |a_j(x)| width(I_j), lower version (explicit states) and upper version; "
  "Proposition 2(b) width 2q with the interval score, lower and upper version; rule (c) and band (a) of the stored design. All in units of tau(x). Training couplings: the query's own label is held out (44 labels). "
  "**Upper version: NOT AVAILABLE at any query** (the cubic is trained and calibrated on all training labels, and those below Jz = %s (n = 57) or %s (n = 115) have no exact interval); the upper numbers printed are indicative only (like-for-like outer or interpolated width) and can neither answer nor pin." % (
      "3.4", "4.0"))
for n in ("57", "115"):
    A("")
    A("**n = %s**" % n)
    A("")
    A("| Jz | range | label miss [S] | cubic miss | standard 2q | truth / label in standard interval | W_lo (2a) | W_hi (2a, indicative) | 2q_lo (2b) | 2q_hi (2b, indicative) | upper interval of this label | rule (c) | band (a) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    M = RES["sizes"][n]["models"]["poly3_invJ"]
    std = {round(r["Jz"], 1): r for r in M["indist_emulated"]["rows"] + M["ood_emulated"]["rows"]}
    pr = {round(r["Jz"], 1): r for r in P2["sizes"][n]["indist"] + P2["sizes"][n]["ood"]}
    ivs = {round(float(k), 1): v for k, v in P2["sizes"][n]["intervals"].items()}
    for j in sorted(std):
        r, q = std[j], pr[j]
        A("| %.1f | %s | %.2f | %.2f | %.3f | %s / %s | %.2f | %.2f | %.2f | %.2f | %s | %s | %s |" % (
            j, "test" if j in TEST else "train", abs(r["bias_ms_label"]) / (0.06 * abs(r["m_s_truth"])), r["miss_ms_over_tau"], r["widthM_tau"],
            "yes" if r["covM_truth"] else "no", "yes" if r["covM_emu"] else "no", q["W_lo_tau"], q["W_hi_tau"], q["width_b_lo_tau"], q["width_b_hi_tau"],
            ivs[j]["upper_kind"].replace("_", "-"), q["rule_c"], q["band_a"]))
    ap = SM[n]["apart"]["1.5"]
    A("")
    A("Jz = 1.5 (in neither set, on its own line): cubic miss %.2f tau; standard interval contains the truth: %s; 2(b) lower width %.2f tau." % (
        ap["miss_tau"], "yes" if ap["covered_by_standard_interval"] else "no", ap["width_2b_lower_tau"]))
A("")
A("### 3.3 Proposition 2 for the cubic: summary")
A("")
for n in ("57", "115"):
    p = SM[n]["prop2"]
    A("- n = %s. 2(a), lower version: W_lo = %s tau at the test couplings and %s tau at the held-out training couplings; band (a) is NOT_PINNED at %d of %d queries, UNDECIDED at %d (Jz = %s: W_lo below tau, upper version not available), PINNED at %d. "
      "2(b), lower version: 2q_lo = %s tau at the test couplings, %s tau held out; these intervals contain the truth at %d of 4 test and %d of 45 training queries. Rule (c) answers %d of %d queries (definite abstention at %d: 2q_lo > tau). "
      "Upper kinds over the 45 training labels: exact %d, like-for-like %d, interpolated %d. Check of the stored script: every label and every truth lies in its upper interval (%s, %s); linearity check %.1e." % (
          n, rng(*p["W_lo_tau_test"], 2), rng(*p["W_lo_tau_ind"], 2), p["not_pinned"], p["n_queries"], len(p["undecided"]),
          ("%.1f-%.1f" % (min(p["undecided"]), max(p["undecided"]))) if p["undecided"] else "none", p["pinned"],
          rng(*p["width_b_lo_tau_test"], 2), rng(*p["width_b_lo_tau_ind"], 2), p["truth_covered_b_lo_test"], p["truth_covered_b_lo_ind"], p["n_answered_rule_c"], p["n_queries"], p["abstain_definite"],
          p["upper_kinds_training"]["exact"], p["upper_kinds_training"]["like_for_like"], p["upper_kinds_training"]["interpolated"], p["label_in_upper"], p["truth_in_upper"], p["linearity_check"]))
for n in ("57", "115"):
    bad = [x for x in P2["sizes"][n]["ood"] + P2["sizes"][n]["indist"] if not x["covers_truth_b_lo"]]
    A("- n = %s: queries at which the 2(b) lower-version interval does not contain the truth: %s." % (
        n, ", ".join("Jz = %.1f (miss %.2f tau against a half-width of %.2f tau)" % (x["Jz"], x["miss_over_tau"], x["width_b_lo_tau"] / 2) for x in bad) if bad else "none"))
A("- The lower version is a lower bound on the width that a valid interval of this construction must have. It is not itself a guaranteed interval, and no conformal guarantee applies outside the training range.")
A("")
A("### 3.4 Outcomes of L1, L2, L3 (each holds iff true at n = 57; n = 115 reported)")
A("")
A("| | n = 57 (decides) | n = 115 (reported) |")
A("|---|---|---|")
A("| **L1** the cubic misses the true m_s by more than tau at each of 1.1-1.4 | **%s**: %s tau | %s: %s tau |" % (
    "HOLDS" if SM["57"]["L1"]["holds"] else "DOES NOT HOLD", ", ".join("%.2f" % SM["57"]["L1"]["miss_tau"]["%.1f" % j] for j in TEST),
    "HOLDS" if SM["115"]["L1"]["holds"] else "DOES NOT HOLD", ", ".join("%.2f" % SM["115"]["L1"]["miss_tau"]["%.1f" % j] for j in TEST)))
A("| **L2** standard intervals calibrated on the real labels cover the truth at none of the four test couplings | **%s**: covered at %d of 4 (sites: %s) | %s: covered at %d of 4 (sites: %s) |" % (
    "HOLDS" if SM["57"]["L2"]["holds"] else "DOES NOT HOLD", sum(SM["57"]["L2"]["covered"].values()), ", ".join("%.3f" % SM["57"]["L2"]["site_coverage"]["%.1f" % j] for j in TEST),
    "HOLDS" if SM["115"]["L2"]["holds"] else "DOES NOT HOLD", sum(SM["115"]["L2"]["covered"].values()), ", ".join("%.3f" % SM["115"]["L2"]["site_coverage"]["%.1f" % j] for j in TEST)))
A("| **L3** 2(b) intervals calibrated on all 45 labels wider than tau at every coupling (lower version) | **%s**: one value of q_lo = %.5f; 2q_lo = %s tau over the 45 training and 4 test couplings (held out, 44 labels: %s tau) | %s: q_lo = %.5f; %s tau (held out: %s tau) |" % (
    "HOLDS" if SM["57"]["L3"]["holds"] else "DOES NOT HOLD", SM["57"]["L3"]["q_lo_all_training_labels"], rng(min(SM["57"]["L3"]["width_tau"].values()), max(SM["57"]["L3"]["width_tau"].values()), 2),
    rng(*SM["57"]["L3"]["held_out_width_tau_range"], 2), "HOLDS" if SM["115"]["L3"]["holds"] else "DOES NOT HOLD", SM["115"]["L3"]["q_lo_all_training_labels"],
    rng(min(SM["115"]["L3"]["width_tau"].values()), max(SM["115"]["L3"]["width_tau"].values()), 2), rng(*SM["115"]["L3"]["held_out_width_tau_range"], 2)))
A("")
A("L1 and L2 were predictions of the emulation-based test; the miss of the real m_s label itself at 1.1-1.4 had been seen [S, F7], the cubic's miss had not. L3 carries the mark of gate G6 (first part NOT COMPLETE).")
A("")
A("### 3.5 Blocks that the derived script inherits from the stored one")
A("")
for n in ("57", "115"):
    sr = SM[n]["split_robustness"]; lf = SM[n]["like_for_like_block"]
    A("- n = %s. Per-site split conformal over all choices of %d calibration couplings (%d choices), test range: sites covered, labels / truth: cubic %.3f / %.3f, null %.3f / %.3f. "
      "**Like-for-like block, not a property of the real labels** (the stored in-sector thresholds at E_real, at the couplings of the stored map only; seen before the hash, F6 and F9): m_s \"answered\" at Jz = %s; local labels at none; largest miss of the cubic at those couplings %s tau." % (
          n, sr["poly3_invJ"]["k_cal"], sr["poly3_invJ"]["n_splits"], sr["poly3_invJ"]["covZ_emu"], sr["poly3_invJ"]["covZ_truth"], sr["null_nn"]["covZ_emu"], sr["null_nn"]["covZ_truth"],
          ", ".join("%.1f" % j for j in lf["answered_m_s"]), fu(lf["cubic"]["max_miss_over_tau_answered"])))
A("- The block `device_illustration` of the stored script (this project's three device points against the cubic trained on the real labels) is in `out/learn/results_cheap.json`; it is not part of the declaration and is not used.")
A("")
A("### 3.6 Not computed")
A("")
for x in NOT_COMPUTED:
    A("- **%s** (%d fits). Reason: %s. To complete: %s." % (x["what"], x["fits"], x["reason"], x["how"]))
A("- None of L1-L3, (f2), (f3) uses these models. Their rows in the table of Sec. 3.1 stay empty; they are not passes.")
A("")
A("## 4. (f2) The learner-independent floor")
A("")
A("Rule: for any learner and the constant-width score, 2q >= w_(k), the k-th narrowest calibration interval, k = ceil((m+1)(1-alpha)) = 42 for m = 45; computed with the lower widths ((1 - q) x hull of explicit states); **holds iff the floor exceeds tau(x) at each of the four test queries** (Sec. 12, line 12).")
A("")
A("| size | floor w_(42) | at Jz = 1.1 / 1.2 / 1.3 / 1.4 (tau) | smallest over the 50 couplings (tau) | held out, m = 44, k = 41 (tau) | outcome |")
A("|---|---|---|---|---|---|")
for n in ("57", "115"):
    s = SM[n]["f2"]
    A("| %s | %.5f | %s | %s | %s | **%s** (every coupling: %s; held out: %s) |" % (n, s["floor"], " / ".join(fd(v, 2) for v in s["test"]), fd(s["all_min"], 2), rng(*s["held_out"], 2),
                                                                             "HOLDS" if s["holds"] else "DOES NOT HOLD", s["holds_every"], s["holds_held_out"]))
A("")
A("Floor at every query, in units of tau(x):")
A("")
A("| Jz | n = 57 | n = 115 | held out, n = 57 | held out, n = 115 |")
A("|---|---|---|---|---|")
for k in range(11, 61):
    j = "%.1f" % (k / 10)
    h57 = F2["sizes"]["57"]["in_distribution_held_out"].get(j); h115 = F2["sizes"]["115"]["in_distribution_held_out"].get(j)
    A("| %s | %s | %s | %s | %s |" % (j, fd(F2["sizes"]["57"]["floor_over_tau"][j], 2), fd(F2["sizes"]["115"]["floor_over_tau"][j], 2),
                                   fd(h57["floor_over_tau"], 2) if h57 else "-", fd(h115["floor_over_tau"], 2) if h115 else "-"))
A("")
for n in ("57", "115"):
    s = SM[n]["f2"]
    A("- n = %s: the four widest lower widths are those of the labels at Jz = %s; the floor is the fourth of them. No training label lacks an explicit-state interval (list of widths taken as 0: %s). "
      "Gate mark: %d of the 45 lower widths rest on re-evaluated energies (G6, first part, NOT COMPLETE). **Post hoc robustness (not declared):** with those widths set to 0, the floor is %.5f, that is %s tau at the four test queries: still above tau." % (
          n, ", ".join(s["widest4"]), s["missing"], s["n_training_labels_on_re_evaluated_energy"], s["posthoc_floor_without_re_evaluated"], " / ".join(fd(v, 2) for v in s["posthoc_floor_without_re_evaluated_test"])))
A("- What decides the floor: the labels at Jz = 1.6-1.9, whose windows are several tau wide. The floor says nothing about a calibration set restricted to certified labels; that is (f3).")
A("")
A("## 5. (f3) The constructive test: train and calibrate only on labels certified at their own energy")
A("")
A("200 seeded splits of the set (`numpy.random.default_rng([%d, n, c])`). M1: line in 1/Jz; M2: 1 - a/Jz^2 - b/Jz^4, both fitted to the real m_s labels of the training couplings. Control M0: the cubic in 1/Jz trained on every real training label outside the calibration and query couplings (uncertified labels included). "
  "Score s_j = max(|f(x_j) - lo_j|, |f(x_j) - hi_j|) over the exact interval of the calibration label; q = the ceil((m+1)(1-alpha))-th smallest; interval f(x) +- q. **Pass rule, n = 57, set S_p, both M1 and M2: (W) in at least 90 %% of the splits 2q <= tau(x) at every query, and (C) the truth within q of the prediction in at least 90 %% of all (split, query) pairs.**" % SEED)
A("")
A("### 5.1 Primary: n = 57, S_p = %s (%d couplings, Jz = %.1f-%.1f; %d training, %d calibration, %d query couplings per split): **%s**" % (
    NAME[SM["57"]["f3"]["S_p"]], p57["size"], p57["range"][0], p57["range"][1], p57["n_train"], p57["n_cal"], p57["n_query"], SM["57"]["f3"]["primary"]["outcome"]))
A("")
for m in ("M1", "M2"):
    a = p57["models"][m]
    A("- %s: (W) %d of %d splits (rule: at least 180): %s. (C) %d of %d pairs (rule: at least %d): %s. Width 2q = %s tau (median %.3f). Largest miss of the prediction %s tau. Smallest ratio of 2q to the widest calibration interval: %.3f (the floor of (f2) is respected in every split: %d violations)." % (
        m, a["n_splits_W"], a["n_splits"], "met" if a["W_holds"] else "NOT met", a["n_pairs_C"], a["n_pairs"], int(math.ceil(0.9 * a["n_pairs"])), "met" if a["C_holds"] else "NOT met",
        rng(a["width_tau_min"], a["width_tau_max"]), a["width_tau_median"], fu(a["largest_miss_tau"]), a["two_q_over_floor_min"], a["floor_violations"]))
a = p57["models"]["M0"]
A("- Control M0 (secondary): **%s**. (W) %d of %d, (C) %d of %d, 2q = %s tau, largest miss %s tau. **The control passes as well, with a smaller largest miss than M1 and M2:** on these data, what makes the test pass is calibrating on certified labels with the interval score; training only on certified labels brought no measurable gain." % (
    p57["outcome_M0"], a["n_splits_W"], a["n_splits"], a["n_pairs_C"], a["n_pairs"], rng(a["width_tau_min"], a["width_tau_max"]), fu(a["largest_miss_tau"])))
A("- With m = %d calibration labels, k = %d: q is the largest calibration score; the level 9/10 = 0.9 is attained exactly." % (p57["n_cal"], p57["k"]) if p57["n_cal"] == 9 else "- k = %d of m = %d calibration labels." % (p57["k"], p57["n_cal"]))
A("- The %d (split, query) pairs are drawn from %d couplings and are not independent trials; the counts are those of the declared rule." % (p57["models"]["M1"]["n_pairs"], p57["size"]))
A("- Gate G7 inside the test: labels outside their exact interval: %s; truths outside: %s." % (p57["g7"]["label"] or "none", p57["g7"]["truth"] or "none"))
A("")
A("### 5.2 Every set, model and size")
A("")
A("| size | set | couplings | train / cal / query | model | (W): splits with 2q <= tau at every query | (C): pairs with the truth inside | 2q (tau): min / median / max | largest miss (tau) | min of 2q over the widest calibration interval | outcome |")
A("|---|---|---|---|---|---|---|---|---|---|---|")
for n in ("57", "115"):
    for name in ("S", "S_3_4", "S_1_2"):
        x = SM[n]["f3"]["sets"][name]
        tagp = " (**primary**)" if (n == "57" and name == SM[n]["f3"]["S_p"]) else (" (S_p, secondary)" if name == SM[n]["f3"]["S_p"] else "")
        if x["status"] != "RUN":
            A("| %s | %s%s | %d | - | - | - | - | - | - | - | NOT RUN (fewer than 15 couplings) |" % (n, NAME[name], tagp, x["size"])); continue
        for m in ("M1", "M2", "M0"):
            a = x["models"][m]
            oc = (x["outcome_M1_M2"] if m != "M0" else x["outcome_M0"])
            A("| %s | %s%s | %d (%.1f-%.1f) | %d / %d / %d | %s | %d of %d%s | %d of %d | %s / %.3f / %s | %s | %.3f | %s%s |" % (
                n, NAME[name], tagp, x["size"], x["range"][0], x["range"][1], x["n_train"], x["n_cal"], x["n_query"], m + (" (control)" if m == "M0" else ""),
                a["n_splits_W"], a["n_splits"], "" if a["W_holds"] else " **(rule not met)**", a["n_pairs_C"], a["n_pairs"], fd(a["width_tau_min"]), a["width_tau_median"], fu(a["width_tau_max"]),
                fu(a["largest_miss_tau"]), a["two_q_over_floor_min"], "**%s**" % oc, " (M1 and M2 together)" if m != "M0" else ""))
A("")
A("- **n = 57, set S (all %d certified labels, Jz %.1f-%.1f): FAIL.** (C) is met in every pair, (W) in only %d of 200 splits: with labels certified at up to %s tau the returned interval is %s tau wide. This is the case announced in the declaration (\"labels certified at nearly tau make (W) fail even with a perfect model\"); the declared prior for a pass on S was 0.4." % (
    sS["size"], sS["range"][0], sS["range"][1], max(sS["models"][m]["n_splits_W"] for m in ("M1", "M2")), fu(ic57["S"]["exact_width_tau"][1]),
    rng(min(sS["models"][m]["width_tau_min"] for m in ("M1", "M2")), max(sS["models"][m]["width_tau_max"] for m in ("M1", "M2")))))
A("- **n = 57, set S_3/4 (%d labels): FAIL** on (W) (%d and %d of 200 splits for M1 and M2); (C) met in every pair." % (s34["size"], s34["models"]["M1"]["n_splits_W"], s34["models"]["M2"]["n_splits_W"]))
A("- **n = 57, set S_1/2 (%d labels): PASS** (declared prior 0.8)." % p57["size"])
x115 = SM["115"]["f3"]["sets"]
A("- **n = 115 (secondary): PASS on S_p = S_3/4 and on S** (the same %d couplings, Jz %.1f-%.1f, different splits); on S, M2 meets (W) in %d of 200 splits. Widths %s tau: close to the tolerance. S_1/2 has %d couplings: NOT RUN." % (
    x115["S"]["size"], x115["S"]["range"][0], x115["S"]["range"][1], x115["S"]["models"]["M2"]["n_splits_W"],
    rng(min(x115[k]["models"][m]["width_tau_min"] for k in ("S", "S_3_4") for m in ("M1", "M2")), max(x115[k]["models"][m]["width_tau_max"] for k in ("S", "S_3_4") for m in ("M1", "M2"))), x115["S_1_2"]["size"]))
A("- Forecast against outcome: the declaration quoted 0.71-0.76 tau from emulated labels in [4, 6]. Obtained on [4.0, 6.0] at n = 115: %s tau (median %.3f for M1), wider than the forecast; on [4.3, 6.0] at n = 57: %s tau (median %.3f for M1)." % (
    rng(x115["S"]["models"]["M1"]["width_tau_min"], x115["S"]["models"]["M1"]["width_tau_max"]), x115["S"]["models"]["M1"]["width_tau_median"],
    rng(p57["models"]["M1"]["width_tau_min"], p57["models"]["M1"]["width_tau_max"]), p57["models"]["M1"]["width_tau_median"]))
A("")
A("### 5.3 Proposition 2(a) on the same splits and the secondary width-normalized scores (no rule)")
A("")
A("| size | set | model | W(x) with exact intervals (tau): min-max | W(x), lower version: max (tau) | normalized score, literal: 2q sigma (tau) min-max; truth covered | normalized score, worst case over the interval: 2q sigma (tau) min-max; splits all <= tau; truth covered |")
A("|---|---|---|---|---|---|---|")
for n in ("57", "115"):
    for name in ("S", "S_3_4", "S_1_2"):
        x = SM[n]["f3"]["sets"][name]
        if x["status"] != "RUN":
            continue
        for m in ("M1", "M2", "M0"):
            a = x["models"][m]; nl, ni = a["norm_literal"], a["norm_interval"]
            A("| %s | %s | %s | %s | %s | %s; %.1f %% of pairs | %s; %.1f %% of splits; %.1f %% of pairs |" % (
                n, NAME[name], m, rng(*a["W_a_exact_tau_range"], 2) if a["W_a_exact_tau_range"] else "not available (M0 uses labels without exact interval)", fu(a["W_a_lower_tau_max"], 2),
                rng(nl["width_tau_min"], nl["width_tau_max"]), 100 * nl["frac_pairs_covered"], rng(ni["width_tau_min"], ni["width_tau_max"], 2), 100 * ni["frac_splits_all_widths_le_tau"], 100 * ni["frac_pairs_covered"]))
A("")
nl = p57["models"]["M1"]["norm_literal"]; ni = p57["models"]["M1"]["norm_interval"]
A("- The literal width-normalized score (|f - y| / sigma, which ignores the label's interval) returns narrow intervals that contain the truth in only %.1f %% of the pairs on the primary set (M1): it must not be presented as a certified interval. The worst-case variant keeps the truth inside (%.1f %%) but is below tau at every query in only %.1f %% of the splits. Neither decides anything." % (
    100 * nl["frac_pairs_covered"], 100 * ni["frac_pairs_covered"], 100 * ni["frac_splits_all_widths_le_tau"]))
A("- The band of Proposition 2(a) exceeds tau in part of the pairs (largest %s tau for M1 on the primary set): 2(a) alone would not give the guarantee that 2(b) gives here." % fu(p57["models"]["M1"]["W_a_exact_tau_range"][1], 2))
A("")
A("### 5.4 The limit, printed with the result (declaration Sec. 7)")
A("")
A("Between Jz = 4 and 6 the true m_s changes by 0.4 tau (measured: %s tau at n = 57 and %s tau at n = 115; over the primary set, Jz = %.1f-%.1f: %s tau). The test shows that the intervals survive the learner and its calibration where labels are certified. It does not show that a hard function was learned. "
  "Two facts of this run say the same: the control M0 passes, and the largest miss of the real labels of the primary set is already %s tau [S, F7]." % (
      rng(*IC["sizes"]["57"]["truth_change_4_to_6_over_tau"]), rng(*IC["sizes"]["115"]["truth_change_4_to_6_over_tau"]), p57["range"][0], p57["range"][1], rng(*chg), fu(ic57[SM["57"]["f3"]["S_p"]]["label_miss_tau_max"])))
A("")
A("## 6. Independent recomputation (own code, `checks/rd_learn_independent.py`; decides nothing)")
A("")
A("Written after the hash; imports no sealed file. It recomputes with other formulas (least squares on an augmented system instead of the normal equations; m_s fitted directly instead of site by site): the cubic and the null of (f1) at both sizes, real and control labels, test range and in distribution; q_lo and W_lo of Proposition 2; the floor of (f2); (W), (C), widths and largest miss of (f3) for every set that was run and M1, M2, M0. The splits were regenerated with the declared generator call and equal the stored ones.")
A("")
A("| quantity | largest absolute difference from the sealed output |")
A("|---|---|")
for k in sorted(IC["largest_difference_from_sealed_output"]):
    A("| %s | %.1e |" % (k, IC["largest_difference_from_sealed_output"][k]))
A("")
A("Not recomputed independently: the per-site coverages, the upper (indicative) versions of Proposition 2, the secondary normalized scores, the perceptron.")
A("")
A("## 7. Post hoc (not declared; these lines decide nothing)")
A("")
A("**7.1 The standard score on the splits of (f3).** Same splits, same models, score |f(x_j) - y_j| on the calibration labels instead of the interval score:")
A("")
A("| size | set | model | interval score (declared): (W) / (C) | standard score: splits with 2q <= tau | standard score: pairs with the truth inside | standard 2q (tau) |")
A("|---|---|---|---|---|---|---|")
for n in ("57", "115"):
    for name in ("S", "S_3_4", "S_1_2"):
        x = IC["sizes"][n]["f3"][name]
        if x["status"] != "RUN":
            continue
        for m in ("M1", "M2", "M0", "const_posthoc"):
            a = x["models"][m]; s = a["standard_score_posthoc"]
            A("| %s | %s | %s | %.1f %% / %.1f %% | %.1f %% | **%.1f %%** | %s |" % (n, NAME[name], m.replace("const_posthoc", "constant (post hoc)"), 100 * a["frac_splits_W"], 100 * a["frac_pairs_C"],
                                                                           100 * s["frac_splits_W"], 100 * s["frac_pairs_C"], rng(s["width_tau"][0], s["width_tau"][2])))
st57 = ic57[SM["57"]["f3"]["S_p"]]["models"]; st115 = ic115[SM["115"]["f3"]["S_p"]]["models"]
A("")
A("- On the primary set the standard recipe returns intervals of at most %s tau that contain the truth in %.1f %% (M1), %.1f %% (M2) and %.1f %% (M0) of the pairs; the interval score contains it in 100 %%. At n = 115 (S_p): %.1f %%, %.1f %%, %.1f %%. Even on labels certified to half the tolerance, the standard intervals follow the labels and miss the truth; the energy intervals are what restores coverage, at the price of the width." % (
    fu(max(st57[m]["standard_score_posthoc"]["width_tau"][2] for m in ("M1", "M2", "M0"))), 100 * st57["M1"]["standard_score_posthoc"]["frac_pairs_C"], 100 * st57["M2"]["standard_score_posthoc"]["frac_pairs_C"],
    100 * st57["M0"]["standard_score_posthoc"]["frac_pairs_C"], 100 * st115["M1"]["standard_score_posthoc"]["frac_pairs_C"], 100 * st115["M2"]["standard_score_posthoc"]["frac_pairs_C"], 100 * st115["M0"]["standard_score_posthoc"]["frac_pairs_C"]))
cst = st57["const_posthoc"]
A("- **7.2 A constant model** (the mean of the training labels) with the interval score on the primary set: (C) %.1f %% of pairs, (W) %.1f %% of splits (2q = %s tau, largest miss %s tau). A constant would fail the pass rule on width only, and a line in 1/Jz (M1) is enough to pass it. This quantifies the limit of Sec. 5.4." % (
    100 * cst["frac_pairs_C"], 100 * cst["frac_splits_W"], rng(cst["width_tau"][0], cst["width_tau"][2]), fu(cst["largest_miss_tau"])))
A("- **7.3 The floor without the labels that rest on re-evaluated energies:** Sec. 4.")
A("")
A("## 8. Re-executed, only compared, not checked")
A("")
A("- **Re-executed:** the sealed code (cheap stage: cubic, null, Proposition 2, floor, constructive test, rules; the perceptron's test-range piece at n = 57); the manifest check; own independent recomputation (Sec. 6); the post hoc lines.")
A("- **Only compared:** the intervals of `out/S_sets.json` with the m_s rows of `out/map_real.json` (equal); S with the CERTIFIED (exact) rows; the stored splits with the regenerated ones.")
A("- **Not checked here:** the exact certificates and the explicit states behind the intervals (map task, gates G5-G7; G6 first part NOT COMPLETE); the conversion of the public files (G1 NOT COMPLETE); the unit tests of gate G8 were not re-run; "
  "the perceptron in distribution and at n = 115 and architecture 1 were not computed (Sec. 3.6); the perceptron's test-range numbers have no independent recomputation.")
A("")
A("## 9. Two sentences for an abstract, each traceable")
A("")
A("1. %s" % SENT1)
A("   Source: `out/learn_real.json` -> `summary.57.models.poly3_invJ.real.ind` (label_covered, truth_covered), `.real.test` (truth_covered, miss_tau); sealed file `out/learn/results_cheap.json`.")
A("2. %s" % SENT2)
A("   Source: `summary.57.f3.sets.%s.models.M1|M2` (n_splits_W, n_pairs_C, width_tau_min, width_tau_max); `independent_check.sizes.57.f3.%s.truth_change_over_tau` (post hoc line); sealed file `out/learn/f3_constructive.json`." % (SM["57"]["f3"]["S_p"], SM["57"]["f3"]["S_p"]))
A("")
A("Alternative for the negative half: %s Source: `summary.57.f2.test`, `summary.115.f2.test` (sealed file `out/learn/f2_floor.json`; carries the mark of gate G6)." % SENT_ALT)
A("")
A("Limits to keep next to them: sentence 2 is a statement about %d couplings at large Jz, where the labels are already within %s tau of the truth and the control model passes too; on all %d certified labels the same test fails on width; the cases are (split, query) pairs drawn from these couplings, not independent trials; the exact intervals assume that the published energy and site magnetizations belong to one state." % (
    p57["size"], fu(ic57[SM["57"]["f3"]["S_p"]]["label_miss_tau_max"]), sS["size"]))
A("")

# ---------------------------------------------------------------- learn_real.json
out_json = dict(schema="p5-real-data-learn-v1", what="learning tests on the real labels (declaration Sec. 7: f1, f2, f3); sealed outputs verbatim under 'sealed'",
                task="rd-learn", date="2026-11-12", declaration_sha256=DECL, sets_sha256=SETS_SHA, seed=SEED,
                provenance=dict(command_1="python -B -I code/run_learn.py --hash=<H> --stage=cheap", utc_1=list(T_CHEAP),
                                command_2="python -B -I code/rd_learn_parts.py <work> out/learn --data=real --hash=<H> --model=mlp_pilot3 --size=57 --part=ood", utc_2=list(T_MLP),
                                seconds_per_perceptron_fit=FIT_S, python="3.11.4", numpy=np.__version__, threads_per_process=1,
                                sealed_code_sha256=CODE_SHA, manifest_plain_files_equal=man_equal, manifest_plain_files_different=man_diff,
                                sealed_outputs_sha256={f: sha(os.path.join(L, f)) for f in ("results_cheap.json", "prop2_cubic.json", "f2_floor.json", "f3_constructive.json", "f1_rules.json", "parts/f1_mlp_pilot3_n57_ood.json")}),
                gate_notes=dict(G1="NOT COMPLETE (converter not re-run; hashes of the converted files equal the pinned ones)",
                                G6_first_part="NOT COMPLETE, nothing checked: concerns every lower-version number (f2, L3, W_lo, 2q_lo)",
                                others="G2, G3, G4, G5, G6 second part, G7 passed in the map task", gates_of_the_map_task=MAP.get("gates")),
                outcomes=dict(L1={n: SM[n]["L1"]["holds"] for n in SM}, L2={n: SM[n]["L2"]["holds"] for n in SM}, L3={n: SM[n]["L3"]["holds"] for n in SM},
                              f2={n: SM[n]["f2"]["holds"] for n in SM}, f3_primary_n57=F3["decision"],
                              f3_all={n: {k: (v.get("outcome_M1_M2") or v["status"]) for k, v in SM[n]["f3"]["sets"].items()} for n in SM},
                              f3_M0_control={n: {k: v.get("outcome_M0") for k, v in SM[n]["f3"]["sets"].items()} for n in SM},
                              note="L1-L3 and (f3) are decided at n = 57; n = 115 is reported"),
                limit_printed_with_f3="between Jz = 4 and 6 the true m_s changes by 0.4 tau; the test shows that the intervals survive the learner and its calibration where labels are certified; it does not show that a hard function was learned",
                summary=SM, not_computed=NOT_COMPUTED, abstract_sentences=[SENT1, SENT2], abstract_sentence_alternative=SENT_ALT,
                sealed=dict(results_cheap=RES, prop2_cubic=P2, f2_floor=F2, f3_constructive=F3, f1_rules=RU, perceptron_n57_test_range=MLP),
                independent_check=IC,
                post_hoc=dict(note="not declared; decides nothing", standard_score_and_constant_model="independent_check.sizes.<n>.f3.<set>.models.<model>",
                              floor_without_re_evaluated={n: dict(floor=SM[n]["f2"]["posthoc_floor_without_re_evaluated"], over_tau_test=SM[n]["f2"]["posthoc_floor_without_re_evaluated_test"]) for n in SM}))
with open(os.path.join(RD, "out", "learn_real.json"), "w", encoding="utf-8") as f:
    json.dump(out_json, f, indent=1, default=float)
with open(os.path.join(HERE, "RESULTS_learn.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(o) + "\n")

# ---------------------------------------------------------------- hashes
own = ["checks/rd_learn_independent.py", "results/make_results_learn.py"]
files = ["out/S_sets.json", "out/learn/results_cheap.json", "out/learn/prop2_cubic.json", "out/learn/f2_floor.json", "out/learn/f3_constructive.json", "out/learn/f1_rules.json",
         "out/learn/parts/f1_mlp_pilot3_n57_ood.json", "out/learn/stdout_cheap.txt", "out/learn/prop2_cubic_stdout.txt", "out/learn/run_learn_cheap_stdout.txt",
         "out/learn/independent_check.json", "checks/rd_learn_independent_stdout.txt", "out/learn_real.json", "results/RESULTS_learn.md"] + own + CODE
with open(os.path.join(HERE, "SHA256SUMS_learn.txt"), "w", encoding="utf-8", newline="\n") as f:
    for p in files:
        f.write("%s  %s\n" % (sha(os.path.join(RD, p)), p))

# ---------------------------------------------------------------- text for DEVIATIONS.md
d = []
D = d.append
D("")
D("## 2026-11-12, task `rd-learn` (the learning tests on the real labels: Sec. 7, f1-f3)")
D("")
D("The declaration hash was checked against `DECLARATION.sha256` before anything was read; `python -B -I checks/make_manifest.py --check` gave 69 lines of Sec. 11")
D("equal to the files on disk and 0 different before the runs; `out/S_sets.json` existed with SHA-256 `%s`, equal to `out/S_sets.sha256`," % SETS_SHA)
D("before any learning number was computed.")
D("")
D("1. **No sealed file was changed; no code defect that needed a fix was found.** Hashed again after the runs and equal to Sec. 11:")
for c in CODE:
    D("   - `%s`  `%s` (unchanged)" % (c, CODE_SHA[c]))
D("   %d plain-file lines of Sec. 11 were hashed again after the runs: all equal%s." % (man_equal, "" if not man_diff else " EXCEPT %s" % man_diff))
D("2. **The sealed code was run once per stage.** `code/run_learn.py --stage=cheap` (f1_cheap, prop2, f2, f3, rules): %s to %s UTC. `code/rd_learn_parts.py" % T_CHEAP)
D("   --model=mlp_pilot3 --size=57 --part=ood` (the perceptron in the test range): %s to %s UTC (92 fits, %.1f s per fit). Seed %d." % (T_MLP[0], T_MLP[1], FIT_S, SEED))
D("3. **Three parts of (f1) were NOT COMPUTED, for cost (no rule changed; they are reported as not computed, never as passes):** the pilot perceptron in")
D("   distribution at n = 57 (4050 fits, about %.0f CPU-hours at the measured rate), the pilot perceptron at n = 115 (secondary), and the dataset paper's" % (4050 * FIT_S / 3600))
D("   architecture 1 at n = 57 (92 fits, about 13 CPU-hours). L1, L2, L3, (f2) and (f3) do not use them (Sec. 12, line 10: decided on the cubic). To complete:")
D("   `code/rd_learn_parts.py ... --part=i/k` and `--assemble=k` (the test-range piece is already in `out/learn/parts/`), `code/run_learn.py --stage=f1_ibm57`,")
D("   then `--stage=merge` and `--stage=rules`.")
D("4. **Output names.** The sealed code writes `out/learn/{results_cheap,prop2_cubic,f2_floor,f3_constructive,f1_rules}.json`. The files asked of this task,")
D("   `out/learn_real.json` and `results/RESULTS_learn.md`, are written by `results/make_results_learn.py`: the sealed outputs verbatim under the key `sealed`,")
D("   plus provenance, the independent check and the post hoc lines under separate keys; display with outward rounding; no declared outcome is recomputed.")
D("5. **Files added after the hash by this task** (own code; none is imported by the sealed code; none decides anything):")
for p in own:
    D("   - `%s`  `%s`" % (p, sha(os.path.join(RD, p)) if p != "results/make_results_learn.py" else "(its SHA-256 is in `results/SHA256SUMS_learn.txt`)"))
D("6. **Things noticed in the sealed code and left as they are** (they change no declared outcome): (a) the derived script `rd_learn_ibm.py` keeps the stored")
D("   script's blocks `certification`, `abstention` and `device_illustration`; on the real data the first two are like-for-like numbers (stored in-sector")
D("   thresholds at E_real, couplings of the stored map only) and are reported as such, never as properties of the real labels; the third is not part of the")
D("   declaration and is not used. (b) In the nearest-neighbour null, a held-out coupling has its two neighbours at the same distance up to rounding of k/10;")
D("   which one is used is decided by that rounding. No rule depends on the null. (c) In the outputs of the derived scripts the key `emulated` denotes the")
D("   real labels (as the README of the code states).")
D("7. **Gate marks carried by these results (Sec. 12, line 14).** G1 NOT COMPLETE (item 2 of the task `rd-map`). G6, first part, NOT COMPLETE with nothing checked:")
D("   it concerns every lower-version number of this task (the floor of (f2), L3, W_lo and 2q_lo of Proposition 2), because %d (n = 57) and %d (n = 115) of the 45" % (
    SM["57"]["f2"]["n_training_labels_on_re_evaluated_energy"], SM["115"]["f2"]["n_training_labels_on_re_evaluated_energy"]))
D("   training labels have an explicit-state interval that rests on re-evaluated energies. Post hoc robustness line (not the rule): with those widths set to 0")
D("   the floor is still %s tau (n = 57) and %s tau (n = 115) at the four test queries. (f3) uses the exact intervals only and does not depend on G6." % (
    " / ".join(fd(v, 2) for v in SM["57"]["f2"]["posthoc_floor_without_re_evaluated_test"]), " / ".join(fd(v, 2) for v in SM["115"]["f2"]["posthoc_floor_without_re_evaluated_test"])))
D("8. **Post hoc lines added by this task (not declared; they decide nothing; Sec. 7 of `results/RESULTS_learn.md`):** the standard score |f - y| on the splits")
D("   of (f3); a constant model on the same splits; the change of the true m_s over each nested set; the floor without the re-evaluated labels.")
D("9. **Two descriptive sentences of the declaration against the data (no rule involved).** Sec. 7 says that between Jz = 4 and 6 the true m_s changes by")
D("   0.4 tau: measured %s tau (n = 57) and %s tau (n = 115). Sec. 7 quotes a forecast of 0.71-0.76 tau for the width in [4, 6] from emulated labels:" % (
    rng(*IC["sizes"]["57"]["truth_change_4_to_6_over_tau"]), rng(*IC["sizes"]["115"]["truth_change_4_to_6_over_tau"])))
D("   obtained on [4.0, 6.0] at n = 115, %s tau (M1), wider than the forecast." % rng(x115["S"]["models"]["M1"]["width_tau_min"], x115["S"]["models"]["M1"]["width_tau_max"]))
D("10. **Time.** The suggested 45 minutes were exceeded: the perceptron piece alone took 30 minutes of wall time on the shared laptop.")
with open(os.path.join(L, "DEVIATIONS_section_rd-learn.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(d) + "\n")

# ---------------------------------------------------------------- review report
r = []
Rr = r.append
Rr("# rd-learn: the learning tests on the real labels (declaration Sec. 7: f1, f2, f3)")
Rr("")
Rr("## Answer in ten lines")
Rr("")
Rr("1. The declaration hash matches (`%s...`), the sets file existed with its hash (`%s...`) before any learning number, and the sealed code ran unchanged; no defect was found and no rule was changed." % (DECL[:16], SETS_SHA[:16]))
Rr("2. Trained on the real labels, the cubic model misses the true staggered magnetization at the four test couplings by %s tau at 57 qubits (%s at 115): L1 HOLDS." % (
    rng(*c57["real"]["test"]["miss_tau"], 2), rng(*c115["real"]["test"]["miss_tau"], 2)))
Rr("3. Standard conformal intervals calibrated on the real labels contain the truth at none of the four test couplings: L2 HOLDS. Inside the training range they contain %d of %d new labels but the truth at %d of %d (57 qubits) and %d of %d (115)." % (
    c57["real"]["ind"]["label_covered"], c57["real"]["ind"]["n"], c57["real"]["ind"]["truth_covered"], c57["real"]["ind"]["n"], c115["real"]["ind"]["truth_covered"], c115["real"]["ind"]["n"]))
Rr("4. Same prominence: the control on DMRG labels also covers the truth at 0 of 4 test couplings (it misses by %s tau with an interval %s tau wide), so L2 alone does not isolate the label bias; the size of the miss does." % (
    rng(*c57["control"]["test"]["miss_tau"], 2), rng(*c57["control"]["test"]["width_tau"])))
Rr("5. With the energy intervals of all 45 labels, the interval that Proposition 2(b) returns for the cubic is at least %s tau wide, depending on the coupling (lower version; L3 HOLDS), and no learner at all can go below %s tau at the test couplings (the floor of f2 HOLDS; %s tau at 115)." % (
    rng(min(SM["57"]["L3"]["width_tau"].values()), max(SM["57"]["L3"]["width_tau"].values()), 2), fd(min(SM["57"]["f2"]["test"]), 2), fd(min(SM["115"]["f2"]["test"]), 2)))
Rr("6. Constructive test, primary set (the %d labels certified to half the tolerance, Jz = %.1f-%.1f, 57 qubits): PASS. Intervals %s tau wide in %d of 200 splits, truth inside in %d of %d cases, for both declared models." % (
    p57["size"], p57["range"][0], p57["range"][1], rng(wmin, wmax), min(p57["models"][m]["n_splits_W"] for m in ("M1", "M2")), min(p57["models"][m]["n_pairs_C"] for m in ("M1", "M2")), p57["models"]["M1"]["n_pairs"]))
Rr("7. Same prominence: on all %d certified labels the test FAILS on width (%d of 200 splits) and on the intermediate set too (%d and %d of 200); labels certified at nearly the tolerance cannot give a guarantee below it." % (
    sS["size"], max(sS["models"][m]["n_splits_W"] for m in ("M1", "M2")), s34["models"]["M1"]["n_splits_W"], s34["models"]["M2"]["n_splits_W"]))
Rr("8. The control model, trained on uncertified labels as well, passes the primary test too, and the true value changes by only %s tau over that range: the test shows that the guarantee survives the learner, not that a hard function was learned." % CHG)
Rr("9. At 115 qubits (secondary) the test passes on the %d certified labels (Jz = %.1f-%.1f) with widths %s tau, close to the tolerance." % (
    p115["size"], p115["range"][0], p115["range"][1], rng(min(p115["models"][m]["width_tau_min"] for m in ("M1", "M2")), max(p115["models"][m]["width_tau_max"] for m in ("M1", "M2")))))
Rr("10. Not computed, for cost: the perceptron inside the training range and at 115 qubits, and the dataset paper's architecture 1 (only the perceptron's four test couplings at 57 qubits exist: miss %s tau). An independent script reproduces the other numbers to %.0e." % (
    rng(*mlp["real"]["test"]["miss_tau"], 2), worst))
Rr("")
Rr("Full results, every number and table: `real_data/results/RESULTS_learn.md`; machine-readable: `real_data/out/learn_real.json`; dated notes: `real_data/DEVIATIONS.md` (section of the task `rd-learn`).")
Rr("")
Rr("## What was re-executed, only compared, not checked")
Rr("")
Rr("- **Re-executed:** `sha256sum` of the declaration against `DECLARATION.sha256`; `checks/make_manifest.py --check` (69 equal, 0 different); `code/run_learn.py --stage=cheap` (%s to %s UTC); `code/rd_learn_parts.py --model=mlp_pilot3 --size=57 --part=ood` (%s to %s UTC); own `checks/rd_learn_independent.py`; own `results/make_results_learn.py`." % (T_CHEAP[0], T_CHEAP[1], T_MLP[0], T_MLP[1]))
Rr("- **Only compared:** the intervals and the set S of `out/S_sets.json` against the m_s rows of `out/map_real.json` (equal to %.0e); the stored splits against regenerated ones (equal)." % max(IC["sizes"][n]["inputs"]["max_abs_diff_intervals_and_labels_vs_map_real"] for n in ("57", "115")))
Rr("- **Only read:** the sealed code (`run_learn.py`, `rd_f23.py`, `rd_common.py`, `rd_learn_ibm.py`, `rd_prop2_cubic.py`, `rd_learn_parts.py`), the declaration, `DEVIATIONS.md`, the head of `RESULTS_predict.md`.")
Rr("- **Not checked:** the certificates and explicit states behind the intervals (map task); the unit tests of G8 (not re-run); the conversion (G1 NOT COMPLETE); the perceptron's numbers have no independent recomputation; background reports other than the declaration were not re-read for this task.")
Rr("- **Not computed:** " + "; ".join("%s (%s)" % (x["what"], x["reason"]) for x in NOT_COMPUTED) + ".")
Rr("")
Rr("## Outcomes against the declared rules")
Rr("")
i0 = o.index("## Summary (English)"); i1 = o.index("## 1. What was run")
r.extend(o[i0 + 2:i1])
Rr("## Findings")
Rr("")
FIND = [
    ("rd-learn-01", "note", "(f3) primary test passes",
     "On S_p = %s at n = 57 both declared models meet (W) in %d of 200 splits and (C) in %d of %d pairs; 2q = %s tau; largest miss %s tau." % (
         NAME[SM["57"]["f3"]["S_p"]], min(p57["models"][m]["n_splits_W"] for m in ("M1", "M2")), min(p57["models"][m]["n_pairs_C"] for m in ("M1", "M2")), p57["models"]["M1"]["n_pairs"], rng(wmin, wmax),
         fu(max(p57["models"][m]["largest_miss_tau"] for m in ("M1", "M2")))),
     "`out/learn/f3_constructive.json` (sizes.57.sets.%s); RESULTS_learn.md Sec. 5.1; independent recomputation equal to 1e-11." % SM["57"]["f3"]["S_p"],
     "State it with its three limits in the same sentence or the next one: half-tolerance labels only, the control passes too, the truth varies by %s tau over the range." % CHG, "high"),
    ("rd-learn-02", "major", "(f3) fails on S and on S_3/4 at n = 57",
     "On the %d labels certified within tau, (W) holds in %d of 200 splits (2q = %s tau); on S_3/4 in %d (M1) and %d (M2) of 200. (C) holds everywhere." % (
         sS["size"], max(sS["models"][m]["n_splits_W"] for m in ("M1", "M2")), rng(min(sS["models"][m]["width_tau_min"] for m in ("M1", "M2")), max(sS["models"][m]["width_tau_max"] for m in ("M1", "M2"))),
         s34["models"]["M1"]["n_splits_W"], s34["models"]["M2"]["n_splits_W"]),
     "RESULTS_learn.md Sec. 5.2.",
     "The paper must not say that training and calibrating on certified labels returns certified predictions. Say: a guarantee below tau needs labels certified to about half of tau; with labels certified at up to %s tau the returned interval reaches %s tau." % (
         fu(ic57["S"]["exact_width_tau"][1], 2), fu(max(sS["models"][m]["width_tau_max"] for m in ("M1", "M2")), 2)), "high"),
    ("rd-learn-03", "major", "the control M0 passes the primary test as well",
     "M0 (cubic trained on every training label outside the calibration and query couplings, uncertified ones included): (W) %d of 200, (C) %d of %d, largest miss %s tau, smaller than M1 and M2 (%s tau)." % (
         p57["models"]["M0"]["n_splits_W"], p57["models"]["M0"]["n_pairs_C"], p57["models"]["M0"]["n_pairs"], fu(p57["models"]["M0"]["largest_miss_tau"]), fu(max(p57["models"][m]["largest_miss_tau"] for m in ("M1", "M2")))),
     "RESULTS_learn.md Sec. 5.1 and 5.2.",
     "Attribute the result to the calibration on certified labels with the interval score, not to training on certified labels. Proposed wording: \"calibrating on labels certified at their own energy\"; report M0 next to M1 and M2.", "high"),
    ("rd-learn-04", "major", "L2 holds, but it would hold for exact labels too",
     "The DMRG-label control covers the truth at 0 of 4 test couplings at both sizes (miss %s tau, interval %s tau wide at n = 57)." % (rng(*c57["control"]["test"]["miss_tau"], 2), rng(*c57["control"]["test"]["width_tau"])),
     "RESULTS_learn.md Sec. 3.1; `out/learn/results_cheap.json` (ood_exact_control).",
     "Do not present the zero coverage in the test range as evidence of the label bias by itself. Pair it with L1 (%s tau against at most %s tau for the control) or use the in-distribution statement of finding 05, where the control covers %d of %d." % (
         rng(*c57["real"]["test"]["miss_tau"], 2), fu(c57["control"]["test"]["miss_tau"][1], 2), c57["control"]["ind"]["truth_covered"], c57["control"]["ind"]["n"]), "high"),
    ("rd-learn-05", "note", "in distribution the standard intervals cover the labels and not the truth",
     "Cubic, n = 57: %d of %d held-out labels, truth at %d of %d (intervals %s tau wide); n = 115: %d of %d and %d of %d. The control covers the truth at %d of %d." % (
         c57["real"]["ind"]["label_covered"], c57["real"]["ind"]["n"], c57["real"]["ind"]["truth_covered"], c57["real"]["ind"]["n"], rng(*c57["real"]["ind"]["width_tau"]),
         c115["real"]["ind"]["label_covered"], c115["real"]["ind"]["n"], c115["real"]["ind"]["truth_covered"], c115["real"]["ind"]["n"], c57["control"]["ind"]["truth_covered"], c57["control"]["ind"]["n"]),
     "RESULTS_learn.md Sec. 3.1 and 3.2.",
     "This is the cleanest statement about the real labels (the control separates label bias from model error). At large Jz the misses are small in absolute terms (%s tau at 6.0): say so." % ("%.2f" % [x for x in RES["sizes"]["57"]["models"]["poly3_invJ"]["indist_emulated"]["rows"] if abs(x["Jz"] - 6.0) < 1e-9][0]["miss_ms_over_tau"]), "high"),
    ("rd-learn-06", "minor", "Proposition 2, upper version, is not available at any query for the cubic",
     "The cubic is trained and calibrated on all 45 labels; %d (n = 57) and %d (n = 115) of them have no exact interval. Rule (c) answers 0 of 49 queries; band (a) is UNDECIDED at %d (n = 57) and %d (n = 115) queries." % (
         45 - SM["57"]["prop2"]["upper_kinds_training"]["exact"], 45 - SM["115"]["prop2"]["upper_kinds_training"]["exact"], len(SM["57"]["prop2"]["undecided"]), len(SM["115"]["prop2"]["undecided"])),
     "RESULTS_learn.md Sec. 3.2 and 3.3.",
     "Print the upper-version columns as indicative only, as the declaration prescribes; the positive statement about certified intervals is (f3), not Proposition 2 for the cubic on all labels.", "high"),
    ("rd-learn-07", "minor", "the floor of (f2) is set by the labels at Jz = 1.6-1.9 and carries the mark of gate G6",
     "Floor = lower width of the fourth-widest label; %d of the 45 lower widths (n = 57) rest on re-evaluated energies. Post hoc: without them the floor is still %s tau at the test queries." % (
         SM["57"]["f2"]["n_training_labels_on_re_evaluated_energy"], " / ".join(fd(v, 2) for v in SM["57"]["f2"]["posthoc_floor_without_re_evaluated_test"])),
     "RESULTS_learn.md Sec. 4.",
     "Quote the floor with the mark, or quote the robust post hoc value as a remark; say that the floor concerns a calibration set that contains the uncertified labels.", "high"),
    ("rd-learn-08", "minor", "(f1) is incomplete for the neural models",
     "Perceptron: test range at n = 57 only (truth covered at %d of 4; miss %s tau with real labels, %s tau with DMRG labels). In distribution, n = 115 and architecture 1: not computed (%.1f s per fit measured)." % (
         mlp["real"]["test"]["truth_covered"], rng(*mlp["real"]["test"]["miss_tau"], 2), rng(*mlp["control"]["test"]["miss_tau"], 2), FIT_S),
     "RESULTS_learn.md Sec. 3.1 and 3.6; `out/learn/parts/`.",
     "Either run the remaining pieces overnight with the sealed helper (commands in Sec. 3.6) or state in the paper that the realistic test on real labels was run for the cubic and the null, with the perceptron in the test range only.", "high"),
    ("rd-learn-09", "note", "post hoc: the standard score on the splits of (f3) misses the truth",
     "Same splits and models, score |f - y|: truth inside in %.1f %% (M1), %.1f %% (M2), %.1f %% (M0) of the pairs on the primary set, against 100 %% with the interval score." % (
         100 * st57["M1"]["standard_score_posthoc"]["frac_pairs_C"], 100 * st57["M2"]["standard_score_posthoc"]["frac_pairs_C"], 100 * st57["M0"]["standard_score_posthoc"]["frac_pairs_C"]),
     "RESULTS_learn.md Sec. 7.1; `checks/rd_learn_independent.py`.",
     "A useful comparison for the paper, to be labelled post hoc: it shows what the energy intervals buy even where the labels are certified.", "high"),
    ("rd-learn-10", "minor", "the literal width-normalized score does not cover the truth",
     "Secondary score |f - y| / sigma on the primary set: truth inside in %.1f %% of the pairs (M1); the worst-case variant covers %.1f %% but is below tau at every query in %.1f %% of the splits." % (
         100 * nl["frac_pairs_covered"], 100 * ni["frac_pairs_covered"], 100 * ni["frac_splits_all_widths_le_tau"]),
     "RESULTS_learn.md Sec. 5.3.",
     "Do not adopt proposal P3 of `reports/math-learning.md` in its literal form; if a normalized score is kept, use the worst-case variant and report its widths.", "high"),
    ("rd-learn-11", "note", "the declared forecast and limit against the data",
     "True m_s changes by %s tau between 4 and 6 at n = 57 (declared: 0.4). Width forecast 0.71-0.76 tau in [4, 6]: obtained %s tau on [4.0, 6.0] at n = 115." % (
         rng(*IC["sizes"]["57"]["truth_change_4_to_6_over_tau"]), rng(x115["S"]["models"]["M1"]["width_tau_min"], x115["S"]["models"]["M1"]["width_tau_max"])),
     "RESULTS_learn.md Sec. 5.2 and 5.4.", "Use the measured numbers in the paper; the forecast was optimistic at n = 115.", "high"),
    ("rd-learn-12", "note", "inherited like-for-like block",
     "The derived script still writes `certification`, `abstention` and `device_illustration`; on the real data these compare E_real with stored in-sector thresholds.",
     "RESULTS_learn.md Sec. 3.5.", "Never print them as properties of the real labels (the declaration forbids it).", "high"),
]
for fid, sev, title, claim, ev, fix, conf in FIND:
    Rr("### %s (%s): %s" % (fid, sev, title))
    Rr("")
    Rr("- What: %s" % claim)
    Rr("- Evidence: %s" % ev)
    Rr("- Proposed use or fix: %s" % fix)
    Rr("- Confidence: %s." % conf)
    Rr("")
Rr("## Two sentences for an abstract")
Rr("")
Rr("1. %s" % SENT1)
Rr("2. %s" % SENT2)
Rr("")
Rr("Traceability and the limits that must stay next to them: `real_data/results/RESULTS_learn.md` Sec. 9.")
Rr("")
Rr("## Files")
Rr("")
for p in ["out/learn_real.json", "results/RESULTS_learn.md", "results/SHA256SUMS_learn.txt", "results/make_results_learn.py", "checks/rd_learn_independent.py", "checks/rd_learn_independent_stdout.txt",
          "out/learn/ (sealed outputs, logs, parts/)", "DEVIATIONS.md (section of the task rd-learn)"]:
    Rr("- `%s/%s`" % (RD.replace("\\", "/"), p))
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(r) + "\n")

print("RESULTS_learn.md: %d lines; learn_real.json: %d bytes; report: %d lines" % (len(o), os.path.getsize(os.path.join(RD, "out", "learn_real.json")), len(r)))
print("manifest plain files equal %d, different %s" % (man_equal, man_diff))
print("SENT1:", SENT1)
print("SENT2:", SENT2)
print("ALT:", SENT_ALT)
for n in ("57", "115"):
    print(n, "f2 test", SM[n]["f2"]["test"], "posthoc grid floor", SM[n]["f2"]["posthoc_floor_without_re_evaluated_test"], "re-evaluated labels", SM[n]["f2"]["n_training_labels_on_re_evaluated_energy"])
    print(n, "prop2", {k: v for k, v in SM[n]["prop2"].items() if k not in ("undecided",)})
