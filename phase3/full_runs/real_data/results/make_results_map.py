# real_data / results / make_results_map.py   (own code of the task rd-map; 2026-11-12; written AFTER the hash)
#
# Reformats the outputs of the sealed map code (out/map_rows.json, map_summary.json, map_gates.json,
# map_secondary.json) into
#     out/map_real.json            one record per (size, coupling, label): 2 x 50 x 7 = 700
#     results/RESULTS_map.md       every analysis of DECLARATION.md Secs. 2, 3, 4, 6 with its rule, outcome and numbers
# It computes NO new status, interval or threshold: every number is copied from the sealed outputs (or from the two
# check files of this task, checks/spotcheck_exact_intervals.json and checks/g6_supplement.json, which are named where
# they are used). The only arithmetic done here is display arithmetic: outward rounding, ratios of two stored numbers,
# counting, and the mark "rests on a re-evaluated energy". It opens neither converted/ nor source/.
# Printed numbers are rounded OUTWARD: interval ends away from the interval, widths and misses up, margins down.
#
#   python -B -I make_results_map.py
import hashlib
import json
import math
import os
import sys
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)
OUT, CHK = os.path.join(RD, "out"), os.path.join(RD, "checks")
LABELS = ("m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop")
KEYS = ["%.1f" % (k / 10) for k in range(11, 61)]
TRAIN = [k for k in KEYS if float(k) >= 1.55]
TEST = ["1.1", "1.2", "1.3", "1.4"]
M0 = {57: 9, 115: 19}


def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def dn(x, nd=4):
    return None if x is None else math.floor(x * 10 ** nd + 1e-12) / 10 ** nd


def up(x, nd=4):
    return None if x is None else math.ceil(x * 10 ** nd - 1e-12) / 10 ** nd


def f(x, nd=4):
    return "-" if x is None else ("%." + str(nd) + "f") % x


def ranges(keys):
    out, start, prev = [], None, None
    for k in sorted(keys, key=float):
        v = round(float(k) * 10)
        if start is None:
            start = prev = v
        elif v == prev + 1:
            prev = v
        else:
            out.append((start, prev))
            start = prev = v
    if start is not None:
        out.append((start, prev))
    return ", ".join("%.1f" % (a / 10) if a == b else "%.1f-%.1f" % (a / 10, b / 10) for a, b in out) or "none"


def set_of(key):
    return "training" if key in TRAIN else ("test" if key in TEST else "apart")


SEC2 = {"CERTIFIED_EXACT": "C", "NOT_CERTIFIED": "N", "GRAY": "g", "NO_DECISION": "x", "CONFLICT": "!", "NOT_AVAILABLE": "-"}
LIKE = {"CERTIFIED_s": "C", "NOT_CERTIFIED_s": "N", "GRAY_s": "g", "NA_s": "-"}

rows = rj(os.path.join(OUT, "map_rows.json"))["rows"]
S = rj(os.path.join(OUT, "map_summary.json"))
G = rj(os.path.join(OUT, "map_gates.json"))
X = rj(os.path.join(OUT, "map_secondary.json"))
SPOT = rj(os.path.join(CHK, "spotcheck_exact_intervals.json")) if os.path.exists(os.path.join(CHK, "spotcheck_exact_intervals.json")) else None
G6S = rj(os.path.join(CHK, "g6_supplement.json")) if os.path.exists(os.path.join(CHK, "g6_supplement.json")) else None
ix = {(r["n"], r["key"], r["label"]): r for r in rows}
assert len(rows) == 700 and len(ix) == 700
DECL = S["declaration_sha256"]
assert sha(os.path.join(RD, "DECLARATION.md")) == DECL
run_log = open(os.path.join(OUT, "run_map_stdout.txt"), encoding="utf-8").read().splitlines()
T_START = [x for x in run_log if x.startswith("start ")][0][6:]
T_END = [x for x in run_log if x.startswith("end ")][0][4:]


def reeval(r):
    """True iff the explicit-state side of the row uses an energy re-evaluated at another coupling (pool or reference)."""
    lw = r.get("lower") or {}
    if (lw.get("pool") or {}).get("kind") == "re-evaluated":
        return True
    ref = lw.get("ref")
    return bool(ref and abs(ref["Jg"] - r["Jz"]) > 1e-9)


def end_info(ex, sign):
    d = ex["sides"][sign]
    b = d["cases"][d["decisive_M"]]["bound"]
    cs = b["certificates"]
    return dict(M=d["decisive_M"], how=b["how"], t=b.get("t"),
                certificates=[dict(name=c["name"], kind=c["kind"], Jz=float(Fraction(c["Jz"])), sha256=c["sha256"]) for c in cs])


def end_txt(e):
    return "%s, %s %s" % (e["M"], e["how"].replace("other_coupling", "other coupling"),
                          "+".join("%s@%.1f" % (c["kind"], c["Jz"]) for c in e["certificates"]))


# ------------------------------------------------------------------------------------------------ out/map_real.json
def real_row(r):
    lw, ex, lk = r.get("lower"), r.get("exact"), r["like"]
    marks = []
    o = dict(n=r["n"], Jz=r["Jz"], label=r["label"], set=set_of(r["key"]), E_real=r["E_real"], E0=r["E0"], E0_source=r["E0_source"],
             eps_real=r["eps_real"], de_real=r["de_real"], M_real=r.get("M_real"),
             M_real_minus_M0=None if r.get("M_real") is None else r["M_real"] - M0[r["n"]], q=r.get("q"),
             O_GS=r["O_GS"], O_source=r["O_source"], tau=r["tau"], label_real=r.get("label_real"), miss_over_tau=r.get("miss_tau"),
             status=dict(sec2=r["status"], sec2_reference_free=r["status_rf"], like_for_like=lk["status"],
                         like_for_like_interpolated=bool(lk["interpolated"]),
                         certified_exact=bool(ex and ex.get("certified")), certified_exact_reference_free=bool(ex and ex.get("certified_rf")),
                         not_certified_explicit=bool(lw and lw.get("not_certified"))),
             no_decision=r.get("no_decision", []))
    if ex and ex.get("exists"):
        o["exact"] = dict(in_declared_range=ex["in_range"], interval=[ex["lo"], ex["hi"]], interval_exact=[ex["lo_exact"], ex["hi_exact"]],
                          width=ex["width"], width_over_tau=ex["width_over_tau"], tau_rf=ex["tau_rf"],
                          width_over_tau_rf=ex["width_over_tau_rf"], certified=ex["certified"], certified_rf=ex["certified_rf"],
                          within_tau_outside_declared_range=ex["within_tau_outside_range"],
                          within_tau_rf_outside_declared_range=ex["within_tau_rf_outside_range"],
                          label_inside=ex.get("label_inside"), truth_inside=ex.get("truth_inside"), capped=ex["capped"],
                          n_bounds=ex["n_bounds"], lower_end=end_info(ex, "-"), upper_end=end_info(ex, "+"),
                          margin=dict(largest_eps_still_certified=ex.get("eps_max"), over_eps_real=ex.get("f_exact"),
                                      is_exact_root=ex.get("eps_max_is_exact_root")))
    else:
        o["exact"] = None if ex is None else dict(exists=False, in_declared_range=ex.get("in_range"), reason=ex.get("reason"))
    if lw:
        re_ = reeval(r)
        o["explicit"] = dict(not_certified=lw["not_certified"], w_in_at_Estar_over_tau=(lw["w_in"] / r["tau"]) if lw.get("w_in") is not None else None,
                             width_over_tau=lw.get("w_lower_over_tau"), witness_interval=lw.get("witness"), hull_in_sector=lw.get("hull"),
                             E_star=lw.get("Estar"), reference_state=lw.get("ref"), pool=lw.get("pool"), pool_size=lw.get("pool_size"),
                             rests_on_re_evaluated_energy=re_, reason=lw.get("reason"))
        if lw["not_certified"] and re_:
            marks.append("NOT CERTIFIED rests on a re-evaluated energy; gate G6a NOT COMPLETE (no tensors of its components on the laptop)")
    else:
        o["explicit"] = None
    o["like"] = dict(status=lk["status"], interpolated=bool(lk["interpolated"]), outer=lk.get("outer"), inner=lk.get("inner"),
                     w_out_over_tau=lk.get("w_out_over_tau"), w_in_over_tau=lk.get("w_in_over_tau"), eps_tau_in=lk.get("eps_tau_in"),
                     eps_tau_out=lk.get("eps_tau_out"), f_in=lk.get("f_in"), f_out=lk.get("f_out"),
                     note="statement about in-sector states; never a certificate of a real label")
    if lk["interpolated"] and lk["status"] != "NA_s":
        marks.append("like-for-like status from interpolated thresholds: not a bound")
    if ex and ex.get("within_tau_outside_range"):
        marks.append("exact interval within tau outside the declared range: reported, not counted")
    o["marks"] = marks
    return o


real_rows = [real_row(ix[(n, k, lab)]) for n in (57, 115) for k in KEYS for lab in LABELS]
gate_out = {}
for k, g in G.items():
    if k == "G1":
        gate_out[k] = "NOT COMPLETE (hashes equal; converter not re-run)"
    elif k == "G6a":
        gate_out[k] = "NOT COMPLETE (%d of %d components checked)" % (g["n_checked"], g["n_checked"] + g["n_missing_tensors"])
    else:
        gate_out[k] = "PASS" if g.get("pass") else "FAIL"
map_real = dict(
    schema="p5-real-data-map-real-v1", declaration_sha256=DECL, run_utc=dict(start=T_START, end=T_END),
    what="Map on the real data of arXiv:2606.15983 (DECLARATION.md Secs. 2 and 3): one record per size, coupling and label. Copied from "
         "out/map_rows.json of the sealed code by results/make_results_map.py; no number recomputed.",
    legend=dict(
        status="sec2: CERTIFIED_EXACT / NOT_CERTIFIED / GRAY in the window W(E_real, M) of Sec. 2 with tau = 0.06 |O_GS|; "
               "sec2_reference_free: the same with tau_rf = 0.06 min |O| over the interval; like_for_like: CERTIFIED_s / "
               "NOT_CERTIFIED_s / GRAY_s / NA_s under the paper's sector hypothesis (never a certificate of a real label)",
        exact="interval I = [lo, hi] of Sec. 2 (exact rationals in interval_exact), widths over both tolerances, the certificates behind "
              "each end, margin = largest eps at which the row stays CERTIFIED (exact) and its ratio to eps_real",
        explicit="width_over_tau = (1 - q) w_in(E*) / tau; NOT CERTIFIED iff >= 1; witness_interval = labels of the two explicit mixtures",
        like="outer and inner intervals of the stored map at E_real; f_in = eps_tau_in / eps_real, f_out = eps_tau_out / eps_real",
        q="q = (M_0 - M_real) / 2, the weight of the neighbouring sector needed to reach the published mean magnetization"),
    gates=gate_out, extension_E1="not available at run time (no certificate in real_data/e1/)",
    source_sha256={k: sha(os.path.join(OUT, k)) for k in ("map_rows.json", "map_summary.json", "map_gates.json", "map_secondary.json", "S_sets.json")},
    n_rows=len(real_rows), rows=real_rows)
with open(os.path.join(OUT, "map_real.json"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(map_real, indent=1, sort_keys=True, allow_nan=False) + "\n")

# ------------------------------------------------------------------------------------------------ facts used in the text
J = S["jstar"]
P = S["predicted_vs_obtained"]
F = S["filter"]
A = S["accuracy_factors"]
SETS = S["sets"]["sizes"]
nc_rows = [r for r in rows if r["status"] == "NOT_CERTIFIED"]
nc_re = [r for r in nc_rows if reeval(r)]
q_rng = {n: (min(ix[(n, k, "m_s")]["q"] for k in KEYS), max(ix[(n, k, "m_s")]["q"] for k in KEYS)) for n in (57, 115)}
dm = {n: [ix[(n, k, "m_s")]["M_real"] - M0[n] for k in KEYS] for n in (57, 115)}
ex_rows = {(n, lab): [ix[(n, k, lab)] for k in KEYS if ix[(n, k, lab)]["exact"] and ix[(n, k, lab)]["exact"].get("exists")]
           for n in (57, 115) for lab in ("m_s", "Czz_bar")}
cert = {(n, lab): [r for r in ex_rows[(n, lab)] if r["exact"]["certified"]] for (n, lab) in ex_rows}
cert_rf = {(n, lab): [r for r in ex_rows[(n, lab)] if r["exact"]["certified_rf"]] for (n, lab) in ex_rows}
assert all(len(cert[k]) == len(cert_rf[k]) for k in cert)
wr = {k: (min(r["exact"]["width_over_tau"] for r in v), max(r["exact"]["width_over_tau"] for r in v)) for k, v in cert.items()}
jx = {(n, lab): J["%d_%s" % (n, lab)] for n in (57, 115) for lab in LABELS}

L = []
w = L.append
w("# Map on the real data of arXiv:2606.15983: RESULTS (Secs. 2, 3, 4, 6 and gates G1-G7 of the declaration)")
w("")
w("Written by the task `rd-map` on 2026-11-12 from the outputs of the sealed code (`code/run_map.py`, run from %s to %s UTC, after the "
  "hash of %s). Declaration SHA-256 `%s`, checked against `DECLARATION.sha256` before anything was read. "
  "**Label of the whole analysis: DECLARED AFTER PARTIAL SIGHT. NOT BLIND.** Every block below says which of its numbers had been seen "
  "before the hash (items F1-F10 and T1-T7 of Sec. 1 of the declaration) and which are new." % (
      T_START, T_END, open(os.path.join(RD, "DECLARATION_hash_time.txt"), encoding="utf-8").read().split()[0], DECL))
w("")
w("Printed numbers are rounded outward (interval ends away from the interval, widths and misses up, margins down). The exact rationals are in "
  "`out/map_rows.json`; the same rows in compact form are in `out/map_real.json`. This file is produced by `results/make_results_map.py`, "
  "which copies and does not recompute.")
w("")
w("**Two marks that go with every result of this file.** Gate G1 is NOT COMPLETE: the three converted files have the SHA-256 pinned in the "
  "declaration and the archive has its pinned SHA-256, but the converter was not run again (it uses a restricted unpickler, and this task "
  "was told to unpickle nothing). Gate G6 (first part) is NOT COMPLETE: none of the %d witness components selected by the declared rule has "
  "its tensors on the laptop, so none was checked; %d of the %d NOT CERTIFIED rows rest on an energy re-evaluated by the linear rule and "
  "carry this mark. Extension E1 was not available when the map was run: there is no E1 column." % (
      G["G6a"]["n_missing_tensors"], len(nc_re), len(nc_rows)))
w("")
w("## Resumen en ocho líneas (español llano)")
w("")
w("1. Los datos públicos se analizaron con las reglas fijadas de antemano; la huella de la declaración se comprobó antes de abrir nada y ninguna regla se cambió después.")
w("2. Punto de partida: los estados cuyas etiquetas se publican no están en el sector que supone el artículo; la desviación es pequeña pero aparece en los 100 puntos, así que se usó la regla más débil (energía y magnetización media).")
w("3. Con esa regla y aritmética exacta, la magnetización alternada publicada queda garantizada dentro de la tolerancia en %d de 45 puntos de entrenamiento con 57 cúbits (acoplamiento %.1f a 6.0) y en %d de 45 con 115 cúbits (%.1f a 6.0); la correlación media entre vecinos, en %d y %d." % (
    len([r for r in cert[(57, "m_s")] if r["training"]]), jx[(57, "m_s")]["sec2"]["J_star_exact"],
    len([r for r in cert[(115, "m_s")] if r["training"]]), jx[(115, "m_s")]["sec2"]["J_star_exact"],
    len([r for r in cert[(57, "Czz_bar")] if r["training"]]), len([r for r in cert[(115, "Czz_bar")] if r["training"]])))
w("4. En el otro extremo, con estados explícitos se muestra que la energía y la magnetización media NO bastan para garantizar esas dos etiquetas desde 1.1 hasta 3.1 (57 cúbits) y hasta 3.0 (115), incluidos todos los puntos de prueba; las etiquetas locales no quedan garantizadas en casi ningún punto de 57 cúbits.")
w("5. Entre ambos extremos queda una franja sin decidir: 3.2 a 3.4 con 57 cúbits y 3.1 a 3.9 con 115 (magnetización alternada).")
w("6. La predicción hecha a partir de las figuras se confirma según la regla declarada: de 165 filas, %d coinciden, %d pasan de sin decidir a decididas, ninguna se contradice, y los ocho umbrales salen idénticos." % (
    P["counts"].get("confirmed", 0), P["counts"].get("resolved", 0)))
w("7. Lo que NO se puede decir: que la cifra del artículo (garantizado desde 3.2, 29 de 45) sea una propiedad de las etiquetas reales, porque descansa en la hipótesis del sector, que los datos no cumplen; ni que ninguna etiqueta local quede garantizada bajo esa hipótesis (dos lo están con 57 cúbits y acoplamiento 6.0).")
w("8. Dos comprobaciones quedaron incompletas y así se dice: no se repitió la conversión de los datos, y la comprobación de las energías recalculadas no pudo hacerse sobre los estados decisivos porque no están en este equipo.")
w("")
w("## 0. First, plainly: what the real data allow the paper to say about the dataset's own labels, and what they do not")
w("")
w("Hypothesis H behind every statement about a real label (decision 6 of the declaration): the published energy and the published site "
  "magnetizations are expectation values of one and the same state. Gate G2 supports it at all 100 points; it cannot be proved from the files.")
w("")
w("**What they allow.**")
w("")
w("1. *The published states are not in the sector.* sum_i <Z_i> is below M_0 at all 50 couplings of both sizes; q = (M_0 - M_real)/2 runs "
  "from %s to %s at n = 57 and from %s to %s at n = 115 (Sec. 1 below; seen before the hash, item T2). The paper's sector statuses are "
  "therefore not statements about these labels." % (f(dn(q_rng[57][0], 5), 5), f(up(q_rng[57][1], 4)), f(dn(q_rng[115][0], 5), 5), f(up(q_rng[115][1], 4))))
w("2. *Certified in exact arithmetic from the energy and the mean magnetization (new).* Under H, the published m_s is within tau of the "
  "sector ground-state value at every training coupling Jz = %s (n = 57: %d of 45) and Jz = %s (n = 115: %d of 45); the published "
  "Czz_bar at Jz = %s (n = 57: %d of 45) and Jz = %s (n = 115: %d of 45). The counts are the same with the reference-free "
  "tolerance. The intervals are between %s and %s tau wide (m_s, n = 57), %s and %s (m_s, n = 115), %s and %s (Czz_bar, n = 57), %s and %s "
  "(Czz_bar, n = 115). Every certified label and its truth lie inside its interval (gate G7: %d rows, no violation)." % (
      ranges([r["key"] for r in cert[(57, "m_s")]]), len(cert[(57, "m_s")]), ranges([r["key"] for r in cert[(115, "m_s")]]), len(cert[(115, "m_s")]),
      ranges([r["key"] for r in cert[(57, "Czz_bar")]]), len(cert[(57, "Czz_bar")]), ranges([r["key"] for r in cert[(115, "Czz_bar")]]), len(cert[(115, "Czz_bar")]),
      f(dn(wr[(57, "m_s")][0], 3), 3), f(up(wr[(57, "m_s")][1], 3), 3), f(dn(wr[(115, "m_s")][0], 3), 3), f(up(wr[(115, "m_s")][1], 3), 3),
      f(dn(wr[(57, "Czz_bar")][0], 3), 3), f(up(wr[(57, "Czz_bar")][1], 3), 3), f(dn(wr[(115, "Czz_bar")][0], 3), 3), f(up(wr[(115, "Czz_bar")][1], 3), 3),
      G["G7"]["n_certified_rows"]))
nc_ms = {n: [r["key"] for r in rows if r["n"] == n and r["label"] == "m_s" and r["status"] == "NOT_CERTIFIED"] for n in (57, 115)}
assert all(ix[(n_, k_, l_)]["status"] == "NOT_CERTIFIED" for n_ in (57, 115) for k_ in KEYS[:5] for l_ in LABELS)
nc_cz = {n: [r["key"] for r in rows if r["n"] == n and r["label"] == "Czz_bar" and r["status"] == "NOT_CERTIFIED"] for n in (57, 115)}
w("3. *Not certifiable from the energy and the mean magnetization, by explicit states (new for the real window).* Two explicit states with "
  "energy at most E_real and mean magnetization M_real have labels at least tau apart for m_s at Jz = %s (n = 57) and %s (n = 115), for "
  "Czz_bar at %s and %s, and for all seven labels at the four test couplings 1.1-1.4 and at 1.5, at both sizes. At n = 57 the four local "
  "labels are NOT CERTIFIED at %d, %d, %d and %d of the 45 training couplings (Z_bulk, Z_boundary, Czz_edge, Z_loop)." % (
      ranges(nc_ms[57]), ranges(nc_ms[115]), ranges(nc_cz[57]), ranges(nc_cz[115]),
      jx[(57, "Z_bulk")]["sec2"]["not_certified"], jx[(57, "Z_boundary")]["sec2"]["not_certified"],
      jx[(57, "Czz_edge")]["sec2"]["not_certified"], jx[(57, "Z_loop")]["sec2"]["not_certified"]))
w("4. *The map predicted from the figures is confirmed by the data under the declared rule* (like-for-like, sector hypothesis): %d rows "
  "confirmed, %d resolved from GRAY, 0 opened, %d contradicted, out of 165 with data; the eight stored J* are reproduced exactly (Sec. 6)." % (
      P["counts"].get("confirmed", 0), P["counts"].get("resolved", 0), len(P["contradicted"])))
w("5. *Accuracy factor at the test couplings (in-sector thresholds).* For m_s the energy per site would have to be more than %d times "
  "(n = 57) and more than %d times (n = 115) more accurate at Jz = 1.1-1.4 (form A; form B: more than %d and %d). For Czz_bar: more than "
  "%d and %d (form A), %d and %d (form B). The in-sector window is a subset of what the energy and the mean magnetization allow, so each "
  "factor is a lower bound on what the weaker hypothesis would require (Sec. 7)." % (
      A["57"]["m_s"]["headline_F_A"], A["115"]["m_s"]["headline_F_A"], A["57"]["m_s"]["headline_F_B"], A["115"]["m_s"]["headline_F_B"],
      A["57"]["Czz_bar"]["headline_F_A"], A["115"]["Czz_bar"]["headline_F_A"], A["57"]["Czz_bar"]["headline_F_B"], A["115"]["Czz_bar"]["headline_F_B"]))
fe = {k: F[k]["exact"] for k in F}
w("6. *Filter.* Keeping a training label iff its row is CERTIFIED (exact) keeps %d (n = 57) and %d (n = 115) m_s labels; every kept "
  "label is within %s tau and %s tau of the truth, and each carries the guarantee of item 2 (Sec. 8)." % (
      fe["57_m_s"]["n_kept"], fe["115_m_s"]["n_kept"], f(up(fe["57_m_s"]["miss_kept"]["max"], 3), 3), f(up(fe["115_m_s"]["miss_kept"]["max"], 3), 3)))
w("")
w("**What they do not allow.**")
w("")
r34 = ix[(57, "3.4", "m_s")]
w("1. *To print the like-for-like numbers as properties of the real labels.* \"Certified from J* = %.1f, %d of 45\" (n = 57) and \"from "
  "%.1f, %d of 45\" (n = 115) are statements about in-sector states at the real energy. For the real labels the numbers are J*_exact = "
  "%.1f (%d of 45) and %.1f (%d of 45) for m_s." % (
      jx[(57, "m_s")]["J_star_s"], jx[(57, "m_s")]["like"]["certified"], jx[(115, "m_s")]["J_star_s"], jx[(115, "m_s")]["like"]["certified"],
      jx[(57, "m_s")]["sec2"]["J_star_exact"], jx[(57, "m_s")]["sec2"]["certified_exact"],
      jx[(115, "m_s")]["sec2"]["J_star_exact"], jx[(115, "m_s")]["sec2"]["certified_exact"]))
w("2. *Any certificate of a real label other than m_s and Czz_bar.* There are no exact certificates for C2_bar or for the four local "
  "labels; in the window of Sec. 2 these rows are NOT CERTIFIED or GRAY, never CERTIFIED.")
w("3. *Any statement in the undecided band.* m_s: Jz = %s (n = 57) and %s (n = 115); Czz_bar: %s and %s. There no row is CERTIFIED (exact) under the declared rule "
  "and the explicit states do not separate by tau (for Czz_bar at n = 115, Jz = 3.6-3.9, a proved interval within tau exists but lies outside the declared range and is not counted). At n = 57, Jz = 3.4, m_s is inside the certificate range and is NOT "
  "certified: the exact interval is %s tau wide; it would be certified only if the energy error were at most %s of the published one." % (
      ranges([r["key"] for r in rows if r["n"] == 57 and r["label"] == "m_s" and r["status"] == "GRAY"]),
      ranges([r["key"] for r in rows if r["n"] == 115 and r["label"] == "m_s" and r["status"] == "GRAY"]),
      ranges([r["key"] for r in rows if r["n"] == 57 and r["label"] == "Czz_bar" and r["status"] == "GRAY"]),
      ranges([r["key"] for r in rows if r["n"] == 115 and r["label"] == "Czz_bar" and r["status"] == "GRAY"]),
      f(up(r34["exact"]["width_over_tau"], 4)), f(dn(r34["exact"]["f_exact"], 4))))
zb, ce = ix[(57, "6.0", "Z_bulk")], ix[(57, "6.0", "Czz_edge")]
w("4. *\"No local label is certified at any computed point\" as a like-for-like statement at the real energies.* Under the sector "
  "hypothesis two local rows are CERTIFIED_s at the real energy: Z_bulk and Czz_edge at n = 57, Jz = 6.0 (outer widths %s and %s tau; "
  "the energy could rise by factors %s and %s before the status changes). The stored map had both GRAY and its central reading already "
  "passed them; the relation is \"resolved\", not \"contradicted\". In the window of Sec. 2 no local label is certified." % (
      f(up(zb["like"]["w_out_over_tau"], 4)), f(up(ce["like"]["w_out_over_tau"], 4)), f(dn(zb["like"]["f_out"], 3), 3), f(dn(ce["like"]["f_out"], 3), 3)))
w("5. *That the filter selects the accurate labels.* It selects the labels that carry a guarantee. Of the %d dropped m_s labels at "
  "n = 57, %d are within tau of the truth (%d within tau/2); of the %d dropped at n = 115, %d (%d)." % (
      45 - fe["57_m_s"]["n_kept"], fe["57_m_s"]["dropped_within_tau"], fe["57_m_s"]["dropped_within_half_tau"],
      45 - fe["115_m_s"]["n_kept"], fe["115_m_s"]["dropped_within_tau"], fe["115_m_s"]["dropped_within_half_tau"]))
w("6. *Completeness of gates G1 and G6 (first part), and anything about extension E1* (see the two marks above and Sec. 10).")
w("")

# ------------------------------------------------------------------------------------------------ Sec. 1 departure
w("## 1. The departure from the sector at every coupling (finding of Sec. 2 of the declaration)")
w("")
w("Rule: none (a finding, reported in any case). **Seen before the hash (T2):** all of it. M_real = sum_i `z_basis_opt`[i]; M_0 = 9 "
  "(n = 57), 19 (n = 115); q = (M_0 - M_real)/2. M_real - M_0 is negative at %d of 50 couplings (n = 57) and %d of 50 (n = 115); "
  "|M_real - M_0| <= 0.05 at %d and %d couplings." % (
      sum(1 for x in dm[57] if x < 0), sum(1 for x in dm[115] if x < 0), sum(1 for x in dm[57] if abs(x) <= 0.05), sum(1 for x in dm[115] if abs(x) <= 0.05)))
w("")
w("| Jz | n = 57: M_real - M_0 | q | de_real | n = 115: M_real - M_0 | q | de_real |")
w("|---|---|---|---|---|---|---|")
for k in KEYS:
    a, b = ix[(57, k, "m_s")], ix[(115, k, "m_s")]
    w("| %s | %.6f | %.6f | %.6f | %.6f | %.6f | %.6f |" % (k, a["M_real"] - 9, a["q"], a["de_real"], b["M_real"] - 19, b["q"], b["de_real"]))
w("")
w("de_real = (E_real - E0)/n was seen before the hash (F2, F4). E0 is this project's reference at the 18 + 16 couplings of the stored map and "
  "the authors' DMRG value elsewhere (gate G4 compares the two where both exist).")
w("")

# ------------------------------------------------------------------------------------------------ Sec. 2 exact intervals
w("## 2. Exact intervals of m_s and Czz_bar at the real energies (certified side of Sec. 2)")
w("")
w("Rule: I = [-U_-, U_+], U_sigma = max over M in {M_real, M_0} of the smallest proved bound of the pool, at E_real + 1e-6 and with the "
  "worse of M_real +- 1e-6; CERTIFIED (exact) iff width(I) <= tau = 0.06 |O_GS| and the coupling lies in the declared range ([3.4, 6.0] at "
  "n = 57, [4.0, 6.0] at n = 115). Reference-free tolerance: tau_rf = 0.06 min |O| over I. Arithmetic: `fractions.Fraction`. "
  "**New: every number of this section** (no exact interval at a real energy had been computed before the hash). Certificates: %d files, "
  "%d distinct, %d used (n = 57: %d; n = 115: %d)." % (
      S["certificates"]["n_files"], S["certificates"]["n_distinct"], S["certificates"]["n_used"], S["certificates"]["by_size"]["57"], S["certificates"]["by_size"]["115"]))
w("")
w("| n | label | J*_exact (tau) | CERTIFIED (exact) of 45 (tau) | J*_exact (tau_rf) | of 45 (tau_rf) | certified couplings |")
w("|---|---|---|---|---|---|---|")
for n in (57, 115):
    for lab in ("m_s", "Czz_bar"):
        j = jx[(n, lab)]
        w("| %d | %s | %s | %d | %s | %d | %s |" % (n, lab, f(j["sec2"]["J_star_exact"], 1), j["sec2"]["certified_exact"],
                                                  f(j["sec2_rf"]["J_star_exact"], 1), j["sec2_rf"]["certified_exact"], ranges([r["key"] for r in cert[(n, lab)]])))
w("")
w("Outcome against what the declaration expected (Sec. 3, \"Expected and stated now\"): J*_exact does not lie below 3.4 (n = 57) or 4.0 "
  "(n = 115), as stated. At n = 115 it sits at the lower end of the certificate range for both labels. At n = 57 it is 3.5 for m_s: the row "
  "at 3.4 is not certified (width %s tau)." % f(up(r34["exact"]["width_over_tau"], 4)))
w("")


def widening(r):
    """width(I) minus the width the same pool gives at M = M_0 alone, over tau (display arithmetic on stored numbers)."""
    e = r["exact"]
    assert e["capped"] == [False, False]
    return (e["width"] - (e["sides"]["+"]["cases"]["M_0"]["u"] + e["sides"]["-"]["cases"]["M_0"]["u"])) / r["tau"]


inr = {k: [r for r in v if r["exact"]["in_range"]] for k, v in ex_rows.items()}
w("Inside the declared range, CERTIFIED (exact) at %d of %d couplings (m_s, n = 57), %d of %d (m_s, n = 115), %d of %d (Czz_bar, n = 57) and "
  "%d of %d (Czz_bar, n = 115): the distance between J*_exact and the like-for-like J*_s is set by where certificates exist, except for the "
  "one row at n = 57, Jz = 3.4." % (len(cert[(57, "m_s")]), len(inr[(57, "m_s")]), len(cert[(115, "m_s")]), len(inr[(115, "m_s")]),
                                    len(cert[(57, "Czz_bar")]), len(inr[(57, "Czz_bar")]), len(cert[(115, "Czz_bar")]), len(inr[(115, "Czz_bar")])))
w("")
w("What leaving the sector hypothesis costs on the certified side (descriptive; the declaration expected a slight widening from the term "
  "mu (M_real - M_0)): width(I) minus the width that the same certificates give at M = M_0 alone, over tau, on the rows of the declared "
  "range: at most %s (m_s, n = 57), %s (m_s, n = 115), %s (Czz_bar, n = 57), %s (Czz_bar, n = 115)." % tuple(
      f(up(max(widening(r) for r in inr[k]), 4)) for k in ((57, "m_s"), (115, "m_s"), (57, "Czz_bar"), (115, "Czz_bar"))))
w("")
_s34 = r34["exact"]["sides"]
w("The one row of the declared range that is not certified, m_s at n = 57, Jz = 3.4, in detail (descriptive, post hoc): the same "
  "certificates give %s tau at M = M_0 alone and %s tau at M = M_real alone; the declared interval, the hull over both, is %s tau wide. An "
  "in-sector state at this energy would be within tau; the published mean magnetization (q = %s) takes the row above tau. Its real label "
  "misses the truth by %s tau." % (
      f(up((_s34["+"]["cases"]["M_0"]["u"] + _s34["-"]["cases"]["M_0"]["u"]) / r34["tau"], 4)),
      f(up((_s34["+"]["cases"]["M_real"]["u"] + _s34["-"]["cases"]["M_real"]["u"]) / r34["tau"], 4)),
      f(up(r34["exact"]["width_over_tau"], 4)), f(r34["q"], 5), f(up(r34["miss_tau"], 4))))
w("")
for n in (57, 115):
    for lab in ("m_s", "Czz_bar"):
        w("**n = %d, %s.** Columns: interval I (ends rounded outward); width over tau and over tau_rf (rounded up); C = CERTIFIED (exact) "
          "with tau / with tau_rf; real label; its miss over tau (seen for m_s, F7; new for Czz_bar); truth O_GS; margin = largest energy "
          "error at which the row stays certified, over eps_real (rounded down; above 1 for a certified row); what decides each end." % (n, lab))
        w("")
        w("| Jz | eps_real | I | width/tau | width/tau_rf | C tau / tau_rf | real label | miss/tau | truth | margin | lower end | upper end |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in ex_rows[(n, lab)]:
            e = r["exact"]
            flag = "" if e["in_range"] else (" (outside the declared range; within tau, not counted)" if e["within_tau_outside_range"] else " (outside the declared range)")
            w("| %s%s | %.5f | [%s, %s] | %s | %s | %s / %s | %.6f | %s | %.6f | %s | %s | %s |" % (
                r["key"], flag, r["eps_real"], f(dn(e["lo"], 6), 6), f(up(e["hi"], 6), 6), f(up(e["width_over_tau"], 4)), f(up(e["width_over_tau_rf"], 4)),
                "C" if e["certified"] else "no", "C" if e["certified_rf"] else "no", r["label_real"], f(up(r["miss_tau"], 4)), r["O_GS"],
                f(dn(e.get("f_exact"), 4)), end_txt(end_info(e, "-")), end_txt(end_info(e, "+"))))
        w("")
out_rng = [(r["n"], r["key"], r["label"], r["exact"]["width_over_tau"]) for r in rows if r["exact"] and r["exact"].get("within_tau_outside_range")]
w("Flag \"within tau outside the declared range\" (Sec. 12 line 3: reported, never counted): %s. No interval is empty; no row is in "
  "conflict (CERTIFIED and NOT CERTIFIED at once): %s." % (
      "; ".join("n = %d, Jz = %s, %s, width %s tau" % (a, b, c, f(up(d, 4))) for a, b, c, d in out_rng) or "none",
      "none" if not S["flags"]["conflicts"] and not S["flags"]["empty_intervals"] else str(S["flags"])))
w("")

# ------------------------------------------------------------------------------------------------ Sec. 3 explicit
w("## 3. NOT CERTIFIED from explicit states (all seven labels)")
w("")
w("Rule: with q = (M_0 - M_real)/2, r the stored S^z = s - 1 state of a bracketing grid coupling (lower re-evaluated energy), E* = (E_real - "
  "q E_r)/(1 - q): NOT CERTIFIED iff (1 - q) w_in(E*) >= tau, w_in the hull width over the stored in-sector states (own chain where one is "
  "stored, otherwise the states of the two bracketing grid couplings re-evaluated by the linear rule). **New: every number of this section** "
  "(nothing at the window W(E, M) had been computed). Each cell: status of Sec. 2 (N = NOT CERTIFIED (explicit states), C = CERTIFIED (exact), "
  "g = GRAY) and (1 - q) w_in(E*)/tau rounded down; `*` = the status uses an energy re-evaluated at another coupling (pool or reference state), "
  "which gate G6 (first part) could not check on the laptop.")
w("")
for n in (57, 115):
    w("**n = %d.** NOT CERTIFIED at %s of the 350 rows (%s of the 315 training rows)." % (
        n, sum(1 for r in rows if r["n"] == n and r["status"] == "NOT_CERTIFIED"), sum(1 for r in rows if r["n"] == n and r["status"] == "NOT_CERTIFIED" and r["training"])))
    w("")
    w("| Jz | q | " + " | ".join(LABELS) + " |")
    w("|---|---|" + "---|" * len(LABELS))
    for k in KEYS:
        cells = []
        for lab in LABELS:
            r = ix[(n, k, lab)]
            v = (r["lower"] or {}).get("w_lower_over_tau")
            cells.append("%s %s%s" % (SEC2[r["status"]], "-" if v is None else "%.3f" % dn(v, 3), "*" if (r["status"] == "NOT_CERTIFIED" and reeval(r)) else ""))
        w("| %s | %.5f | %s |" % (k, ix[(n, k, "m_s")]["q"], " | ".join(cells)))
    w("")
w("| n | label | NOT CERTIFIED (explicit) of 45 | at the couplings | GRAY of 45 | CERTIFIED (exact) of 45 |")
w("|---|---|---|---|---|---|")
for n in (57, 115):
    for lab in LABELS:
        j = jx[(n, lab)]["sec2"]
        w("| %d | %s | %d | %s | %d | %d |" % (n, lab, j["not_certified"], ranges([r["key"] for r in rows if r["n"] == n and r["label"] == lab and r["status"] == "NOT_CERTIFIED"]),
                                              j["gray"], j["certified_exact"]))
w("")
w("The couplings listed include the five outside the training set (1.1-1.5). At n = 115 the stored map has no chain of Z_boundary, "
  "Czz_edge or Z_loop, and of Z_bulk only at Jz = 4.0; their pools are the states of the other labels' chains, which is why those columns "
  "turn GRAY early (and why Z_bulk and Czz_edge are NOT CERTIFIED again between 3.7 and 4.4, where the richer pool of Jz = 4.0 is in the "
  "bracket). A GRAY cell there says that the stored states do not decide, not that the label is close to certified.")
w("")

# ------------------------------------------------------------------------------------------------ Sec. 4 like-for-like
w("## 4. Like-for-like statuses under the paper's sector hypothesis, and J*_s")
w("")
w("Rule: at a coupling with a stored chain of the label, CERTIFIED_s iff w_out(E_real) <= tau, NOT CERTIFIED_s iff w_in(E_real) >= tau, "
  "GRAY_s otherwise; elsewhere the stored thresholds interpolated log-linearly in Jz (\"interpolated, not a bound\", suffix `i`). A "
  "CERTIFIED_s status is a statement about in-sector states and is never a certificate of a real label. **Seen before the hash (F6):** "
  "the m_s statuses at the couplings of the stored map, with their energy-over-threshold ratios. **New:** the other six labels, and m_s at "
  "the interpolated couplings. Each cell: status (C, N, g; `-` = not available, no chain of that label at that size) and the margin: for C, "
  "f_out = eps_tau_out/eps_real (rounded down, above 1); for N, f_in = eps_tau_in/eps_real (rounded up, below 1).")
w("")
for n in (57, 115):
    w("**n = %d.**" % n)
    w("")
    w("| Jz | eps_real | " + " | ".join(LABELS) + " |")
    w("|---|---|" + "---|" * len(LABELS))
    for k in KEYS:
        cells = []
        for lab in LABELS:
            lk = ix[(n, k, lab)]["like"]
            s = LIKE[lk["status"]]
            if s == "C":
                t = "C %s" % f(dn(lk["f_out"], 3), 3)
            elif s == "N":
                t = "N %s" % f(up(lk["f_in"], 3), 3)
            elif s == "g":
                t = "g %s/%s" % (f(dn(lk["f_out"], 3), 3), f(up(lk["f_in"], 3), 3))
            else:
                t = "-"
            cells.append(t + ("i" if (lk["interpolated"] and s != "-") else ""))
        w("| %s | %.5f | %s |" % (k, ix[(n, k, "m_s")]["eps_real"], " | ".join(cells)))
    w("")
w("| n | label | J*_s | CERTIFIED_s of 45 | NOT CERTIFIED_s | GRAY_s | not available | of which interpolated |")
w("|---|---|---|---|---|---|---|---|")
for n in (57, 115):
    for lab in LABELS:
        j = jx[(n, lab)]
        w("| %d | %s | %s | %d | %d | %d | %d | %d |" % (n, lab, f(j["J_star_s"], 1), j["like"]["certified"], j["like"]["not_certified"],
                                                       j["like"]["gray"], j["like"]["not_available"], j["like"]["interpolated"]))
w("")
w("J* is the stored definition: the smallest training Jz from which every larger training point is certified (resolution 0.1); a training "
  "coupling without a status is not a certified point.")
w("")

# ------------------------------------------------------------------------------------------------ Sec. 5 J* summary
w("## 5. J* under each rule and the counts out of 45 (table of Sec. 3 of the declaration)")
w("")
w("| n | label | J*_s | cert_s | J*_exact (tau) | cert exact (tau) | J*_exact (tau_rf) | cert exact (tau_rf) | NOT CERTIFIED (explicit) | GRAY (Sec. 2) |")
w("|---|---|---|---|---|---|---|---|---|---|")
for n in (57, 115):
    for lab in LABELS:
        j = jx[(n, lab)]
        s2, rf = j["sec2"], j["sec2_rf"]
        w("| %d | %s | %s | %d | %s | %d | %s | %d | %d | %d |" % (n, lab, f(j["J_star_s"], 1), j["like"]["certified"], f(s2.get("J_star_exact"), 1),
                                                                 s2["certified_exact"], f(rf.get("J_star_exact"), 1), rf["certified_exact"], s2["not_certified"], s2["gray"]))
w("")
w("The number \"certified from %.1f, %d of 45\" (n = 57) and \"from %.1f, %d of 45\" (n = 115) is the like-for-like number (seen, F6 and "
  "F9, at the stored couplings) and, as the declaration says, must not be printed as a property of the real labels." % (
      jx[(57, "m_s")]["J_star_s"], jx[(57, "m_s")]["like"]["certified"], jx[(115, "m_s")]["J_star_s"], jx[(115, "m_s")]["like"]["certified"]))
w("")

# ------------------------------------------------------------------------------------------------ Sec. 6 predicted vs obtained
w("## 6. Predicted from the figures versus obtained from the data (the 171 stored rows)")
w("")
w("Rule: the figures-based map is **confirmed by the data** iff no row is contradicted (CERTIFIED against NOT CERTIFIED) and, for every "
  "label and size with a stored J*, |J*_s - J*_stored| <= 0.1. The 6 rows of n = 19 have no public data; the rule is applied to the 165 "
  "rows of n = 57 and n = 115. **Seen before the hash (F6):** the m_s rows (no contradiction; n = 57: 3.2 and 3.3 resolve from GRAY to "
  "CERTIFIED_s). **New:** the rows of the other six labels.")
w("")
cnt = P["counts"]
w("**Outcome: %s.** Relations over the 165 rows: confirmed %d, resolved %d, opened %d, contradicted %d, GRAY on both sides %d (plus %d "
  "rows of n = 19 without real data)." % ("CONFIRMED BY THE DATA" if P["confirmed_by_the_data"] else "NOT CONFIRMED", cnt.get("confirmed", 0),
                                         cnt.get("resolved", 0), cnt.get("opened", 0), cnt.get("contradicted", 0), cnt.get("gray_both", 0), cnt.get("no_real_data", 0)))
w("")
w("| n | label | stored J* (central) | stored J* (strict) | certified in the stored map | J*_s at E_real | certified_s at E_real | within 0.1 |")
w("|---|---|---|---|---|---|---|---|")
for j in P["jstar"]:
    w("| %d | %s | %s | %s | %s | %s | %d | %s |" % (j["n"], j["label"], f(j["J_star_stored"], 1), f(j["J_star_stored_strict"], 1), j["n_certified_stored"],
                                                  f(j["J_star_s"], 1), jx[(j["n"], j["label"])]["like"]["certified"], "yes" if j["within_0p1"] else "NO"))
w("")
res = [t for t in P["table"] if t["relation"] == "resolved"]
w("The %d resolved rows: %s." % (len(res), "; ".join("n = %d, Jz = %.1f, %s: GRAY -> %s" % (t["n"], t["Jz"], t["label"], t["like_for_like"]) for t in res)))
w("")
cl, c2 = P["claims_like_for_like"], P["claims_sec2"]
w("**Stored claims re-evaluated on the stored rows** (map/DECLARATION.md Sec. 4), with the like-for-like statuses and with those of Sec. 2:")
w("")
w("| claim | like-for-like at E_real | with the statuses of Sec. 2 |")
w("|---|---|---|")
w("| C-A (m_s and Czz_bar certified at Jz >= 4.0, both sizes; %d rows) | %s; rows not certified: %s | %s; rows not certified: %s |" % (
    cl["C-A"]["n_rows"], cl["C-A"]["verdict"], cl["C-A"]["not_certified_rows"] or "none", c2["C-A"]["verdict"], c2["C-A"]["not_certified_rows"] or "none"))
w("| C-B (every row at Jz <= 1.6 NOT CERTIFIED; %d rows; no longer conditional on a floor) | %s; exceptions: %s | %s; exceptions: %s |" % (
    cl["C-B"]["n_rows"], "HOLDS" if cl["C-B"]["holds"] else "DOES NOT HOLD", cl["C-B"]["exceptions"] or "none",
    "HOLDS" if c2["C-B"]["holds"] else "DOES NOT HOLD", c2["C-B"]["exceptions"] or "none"))
w("| C-C (no local label certified; %d rows) | %s; certified local rows: %s | %s; certified local rows: %s; GRAY: %s |" % (
    cl["C-C"]["n_rows"], "HOLDS" if cl["C-C"]["no_local_certified"] else "DOES NOT HOLD",
    "; ".join("n = %d, Jz = %.1f, %s" % (a, b, c) for a, b, c, _ in cl["C-C"]["certified_local_rows"]) or "none",
    "HOLDS" if c2["C-C"]["no_local_certified"] else "DOES NOT HOLD",
    "; ".join("n = %d, Jz = %.1f, %s" % (a, b, c) for a, b, c, _ in c2["C-C"]["certified_local_rows"]) or "none",
    "; ".join("n = %d, Jz = %.1f, %s" % (a, b, c) for a, b, c, _ in c2["C-C"]["gray"]) or "none"))
w("")
w("C-C does not hold like-for-like: at the real energy the bulk-site and single-edge labels at n = 57, Jz = 6.0 are CERTIFIED_s (margins "
  "f_out %s and %s). In the stored map the claim held with these two rows GRAY, and its central reading already passed them (stored J* = "
  "6.0 for both, one certified point each). This is the failure of a stored claim under the real energies and is reported as such; it is "
  "not a contradicted row (GRAY became decisive), so it does not enter the rule above." % (f(dn(zb["like"]["f_out"], 3), 3), f(dn(ce["like"]["f_out"], 3), 3)))
w("")
w("| n | Jz | label | predicted (figures) | like-for-like at E_real | relation | f_out | f_in | status of Sec. 2 (tau) | (tau_rf) |")
w("|---|---|---|---|---|---|---|---|---|---|")
for t in P["table"]:
    w("| %d | %.1f | %s | %s | %s | %s | %s | %s | %s | %s |" % (t["n"], t["Jz"], t["label"], t["predicted"], t["like_for_like"] or "no real data",
                                                             t["relation"].replace("_", " "), f(dn(t["f_out"], 3), 3), f(up(t["f_in"], 3), 3),
                                                             t["sec2"] or "-", t["sec2_rf"] or "-"))
w("")

# ------------------------------------------------------------------------------------------------ Sec. 7 accuracy
w("## 7. The accuracy factor at the test couplings (Sec. 4 of the declaration)")
w("")
w("Rule: F_A = de_real(n, Jz)/de*_in(n, Jz) and F_B = de_real(n, 1.6)/de*_in(n, Jz), de*_in the stored rigorous inner threshold "
  "(explicit in-sector states) at Jz = 1.1-1.4; at 1.5 the threshold of the re-evaluated pool with q = 0. Headline: the smallest value "
  "over Jz = 1.1-1.4, rounded down to two significant digits. **Seen before the hash (F5):** every m_s value at 1.1-1.4 in both forms. "
  "**New:** Czz_bar, and the line at Jz = 1.5. de*_out is printed alongside and decides nothing (at 1.5 it is interpolated, not a bound; "
  "at n = 115, Jz = 1.1 the stored outer threshold of m_s is the floor value of the stored map).")
w("")
w("| n | label | headline form A | smallest F_A | headline form B | smallest F_B |")
w("|---|---|---|---|---|---|")
for n in ("57", "115"):
    for lab in ("m_s", "Czz_bar"):
        a = A[n][lab]
        w("| %s | %s | more than %d | %.2f | more than %d | %.2f |" % (n, lab, a["headline_F_A"], a["min_F_A"], a["headline_F_B"], a["min_F_B"]))
w("")
w("| n | label | Jz | de_real | de*_in | de*_out | F_A | F_B | source of de*_in |")
w("|---|---|---|---|---|---|---|---|---|")
for n in ("57", "115"):
    for lab in ("m_s", "Czz_bar"):
        for v in A[n][lab]["values"]:
            w("| %s | %s | %.1f%s | %.6f | %.4e | %.4e | %.2f | %.2f | %s |" % (
                n, lab, v["Jz"], "" if v["test_coupling"] else " (apart)", v["de_real"], v["de_star_in"], v["de_star_out"], v["F_A"], v["F_B"], v["source"]))
w("")
w("de_real(n, 1.6) = %.6f (n = 57) and %.6f (n = 115). Stated with the number, as declared: the in-sector window is a subset of what the "
  "energy and the mean magnetization allow, so each factor is a lower bound on what the weaker hypothesis would require." % (
      A["57"]["m_s"]["de_real_at_1p6"], A["115"]["m_s"]["de_real_at_1p6"]))
w("")

# ------------------------------------------------------------------------------------------------ Sec. 8 filter
w("## 8. The label filter on the 45 real training labels per size (Sec. 6 of the declaration)")
w("")
w("Rule (m_s primary, Czz_bar secondary): keep a label iff its row is CERTIFIED (exact). Guarantee: a kept label is within tau of the "
  "truth, given the published energy and site magnetizations (hypothesis H). The like-for-like version (stored thresholds, interpolated "
  "where there is no row; the paper's present filter) is next to it. Miss = |label - truth|/tau. **Seen before the hash:** every miss of "
  "m_s (F7) and the like-for-like counts at the stored couplings (F9: n = 57 identical to the line below; n = 115 was counted from Jz = 3.3, "
  "28 labels, and becomes 30 here because the interpolated thresholds also pass 3.1 and 3.2). **New:** the exact filter, and everything "
  "about Czz_bar.")
w("")
w("| n | label | version | kept | kept couplings | largest miss kept | mean miss kept | dropped | largest miss dropped | mean miss dropped | dropped within tau/2 | dropped within tau | dropped above tau | kept above tau/2 |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for k in ("57_m_s", "115_m_s", "57_Czz_bar", "115_Czz_bar"):
    for ver in ("exact", "exact_reference_free", "like_for_like"):
        x = F[k][ver]
        nd = x["n_training"] - x["n_kept"]
        w("| %d | %s | %s | %d | %s | %s | %s | %d | %s | %s | %d | %d | %d | %d |" % (
            x["n"], x["label"], ver.replace("_", " "), x["n_kept"], ranges(["%.1f" % v for v in x["kept"]]), f(up(x["miss_kept"]["max"], 4)),
            f(x["miss_kept"]["mean"], 4), nd, f(up(x["miss_dropped"]["max"], 4)), f(x["miss_dropped"]["mean"], 4),
            x["dropped_within_half_tau"], x["dropped_within_tau"], nd - x["dropped_within_tau"], x["kept_above_half_tau"]))
w("")
w("Cost of the exact filter, in words: at n = 57 it drops %d m_s labels, of which %d are within tau/2 and %d within tau of the truth; at "
  "n = 115 it drops %d, of which %d and %d. No kept label is above tau/2 in any version. Said in advance by the declaration: where the "
  "labels are already accurate the filter buys a guarantee, not accuracy." % (
      45 - fe["57_m_s"]["n_kept"], fe["57_m_s"]["dropped_within_half_tau"], fe["57_m_s"]["dropped_within_tau"],
      45 - fe["115_m_s"]["n_kept"], fe["115_m_s"]["dropped_within_half_tau"], fe["115_m_s"]["dropped_within_tau"]))
w("")
c57, c115 = fe["57_m_s"].get("classical_n19"), fe["115_m_s"].get("classical_n19")
if c57 and c115:
    w("**The small classical calculation next to every label (descriptive, no rule).** |m_s(exact, n = 19) - m_s^GS(n)|/tau: largest value "
      "over the kept labels %s (n = 57) and %s (n = 115); at the test couplings 1.1-1.4: %s (n = 57) and %s (n = 115). The paper's sentence "
      "(\"a range in which an exact 19-site calculation already lies within a fifth of the tolerance\") re-evaluated on the kept set: %s at "
      "n = 57, %s at n = 115. New (no real datum enters these numbers except through the kept set)." % (
          f(up(c57["max_over_kept"], 4)), f(up(c115["max_over_kept"], 4)), ", ".join(f(v, 3) for v in c57["at_test"]), ", ".join(f(v, 3) for v in c115["at_test"]),
          "true" if c57["all_kept_within_a_fifth_of_tau"] else "false", "true" if c115["all_kept_within_a_fifth_of_tau"] else "false"))
    w("")
for n in (57, 115):
    w("**n = %d, every training label** (k = kept, d = dropped; widths rounded up, misses rounded up)." % n)
    w("")
    w("| Jz | m_s miss/tau | exact | exact width/tau | like-for-like | n = 19 exact calculation, miss/tau | Czz_bar miss/tau | exact | exact width/tau | like-for-like |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    c19 = (fe["%d_m_s" % n].get("classical_n19") or {}).get("miss_tau", {})
    for k in TRAIN:
        a, b = ix[(n, k, "m_s")], ix[(n, k, "Czz_bar")]
        ea, eb = a["exact"] or {}, b["exact"] or {}
        w("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            k, f(up(a["miss_tau"], 4)), "k" if ea.get("certified") else "d", f(up(ea.get("width_over_tau"), 4)) if ea.get("exists") else "-",
            "k" if a["like"]["status"] == "CERTIFIED_s" else "d", f(up(c19.get(k), 4)), f(up(b["miss_tau"], 4)), "k" if eb.get("certified") else "d",
            f(up(eb.get("width_over_tau"), 4)) if eb.get("exists") else "-", "k" if b["like"]["status"] == "CERTIFIED_s" else "d"))
    w("")
    w("The five labels apart (m_s; none is kept by any version): %s." % "; ".join(
        "Jz = %.1f, miss %s tau" % (x["Jz"], f(up(x["miss_tau"], 3), 3)) for x in fe["%d_m_s" % n]["apart"]))
    w("")

# ------------------------------------------------------------------------------------------------ Sec. 9 sets
w("## 9. The nested sets of Sec. 7 (f3), fixed here for the learning task")
w("")
w("`out/S_sets.json`, SHA-256 `%s` (also in `out/S_sets.sha256`), written by the sealed code before any other output and before any "
  "learning number. Stored certificates only (no E1)." % S["sets"]["sha256"])
w("")
w("| n | S (interval <= tau) | S_3/4 | S_1/2 | S_p |")
w("|---|---|---|---|---|")
for n in ("57", "115"):
    s = SETS[n]
    w("| %s | %d: %s | %d: %s | %d: %s | %s (%d couplings) |" % (n, len(s["S"]), ranges(["%.1f" % v for v in s["S"]]), len(s["S_3_4"]), ranges(["%.1f" % v for v in s["S_3_4"]]),
                                                              len(s["S_1_2"]), ranges(["%.1f" % v for v in s["S_1_2"]]), s["S_p_name"].replace("_", "/").replace("S/", "S_"), len(s["S_p"])))
w("")

# ------------------------------------------------------------------------------------------------ Sec. 10 gates
w("## 10. Gates G1-G7")
w("")
w("| gate | rule | outcome | numbers |")
w("|---|---|---|---|")
w("| G1 data | converter re-run on the pinned archive reproduces `converted/SHA256SUMS.txt` | **NOT COMPLETE** | the three converted files have the "
  "SHA-256 of `converted/SHA256SUMS.txt` and of Sec. 11 of the declaration; the archive has its pinned SHA-256 (checked by this task with "
  "`sha256sum`); the converter was NOT run again: it reads the archive through a restricted unpickler and this task was told to unpickle "
  "nothing |")
for n in (57, 115):
    g2, g3, g4 = G["G2_%d" % n], G["G3_%d" % n], G["G4_%d" % n]
    rr = [x["ratio"] for x in g2["rows"]]
    w("| G2 same state, n = %d | exchange part of E_real inside [-B, B] at every coupling | **%s** | %d couplings; exchange/B between %.4f and %.4f; "
      "negative radicands: %d; failed: %s (seen, T3) |" % (n, "PASS" if g2["pass"] else "FAIL", len(rr), min(rr), max(rr),
                                                         sum(x["n_negative_radicand"] for x in g2["rows"]), g2["failed"] or "none"))
    dd = [x["E_real_minus_E0_authors"] for x in g3["rows"]]
    w("| G3 energies, n = %d | E_real >= E0(authors) at every coupling | **%s** | E_real - E0 between %.4f and %.4f; failed: %s (seen, T4) |" % (
        n, "PASS" if g3["pass"] else "FAIL", min(dd), max(dd), g3["failed"] or "none"))
    mx = max(v for v in g4["max_abs_dO_over_tau"].values() if v is not None)
    w("| G4 truth, n = %d | authors' DMRG against this project's references: at most 1e-3 tau per label, 1e-4 in E0 | **%s** | %d label rows, largest "
      "difference %.2e tau; %d energies, largest difference %.2e (seen, T5) |" % (n, "PASS" if g4["pass"] else "FAIL", g4["n_label_rows"], mx, g4["n_energy_rows"], g4["max_abs_dE0"]))
g5a, g5b = G["G5a"], G["G5b"]
w("| G5 certificates, records | every certificate used has a recorded exact verification | **%s** | %d files, %d distinct, %d used; excluded for a "
  "missing or bad record: %d |" % ("PASS" if g5a["pass"] else "FAIL", g5a["n_files"], g5a["n_distinct"], g5a["n_used"], len(g5a["excluded_for_a_missing_or_bad_record"])))
if g5b.get("skipped"):
    w("| G5 certificates, re-proof | the deciding certificates re-proved with the independent verifier | **NOT COMPLETE** | skipped |")
else:
    w("| G5 certificates, re-proof | the certificates that decide J*_exact and the boundary of the filter re-proved with `myverify.py` | **%s** | %d "
      "certificates re-proved in this run (operator identity and every cluster inequality, exact arithmetic, method `%s`); all equal the claimed "
      "bound: %s |" % ("PASS" if g5b["pass"] else "FAIL", len(g5b["rows"]), g5b["methods"], all(x["ok"] for x in g5b["rows"])))
g6a, g6b = G["G6a"], G["G6b"]
w("| G6 linear rule against tensors | decisive witness components of the NOT CERTIFIED rows within 0.3 of a J* and of ten rows drawn with the seed: "
  "agreement to 1e-8 | **NOT COMPLETE** | %d rows selected (%d near a J*, %d drawn, seed %d); %d components; checked: %d; without tensors on the "
  "laptop: %d |" % (g6a["n_rows"], len(g6a["selected"]["near_a_J_star"]), len(g6a["selected"]["drawn_with_the_seed"]), g6a["selected"]["seed"],
                    g6a["n_checked"] + g6a["n_missing_tensors"], g6a["n_checked"], g6a["n_missing_tensors"]))
w("| G6 re-evaluated energies | every re-evaluated in-sector energy at least E0(Jz) - 1e-6 | **%s** | %d rows with a re-evaluated pool; smallest "
  "(lowest pool energy - E0) = %.2e; failed: %d |" % ("PASS" if g6b["pass"] else "FAIL", g6b["n_rows"], g6b["min_over_rows"], len(g6b["failed"])))
g7 = G["G7"]
w("| G7 filter | every CERTIFIED (exact) label and its truth inside its interval | **%s** | %d certified rows (either tolerance), violations: %d; of the "
  "%d rows with an interval of any width, %d do not contain label and truth |" % ("PASS" if g7["pass"] else "FAIL", g7["n_certified_rows"], len(g7["violations"]),
                                                                              g7["n_rows_with_an_interval"], g7["n_intervals_not_containing_label_and_truth"]))
w("")
w("No gate failed, so no row is \"no decision\" (%d rows without decision). G1 and the first part of G6 are NOT COMPLETE and are not reported as "
  "passes (Sec. 12 line 14 of the declaration)." % sum(1 for r in rows if r.get("no_decision")))
w("")
if not g5b.get("skipped"):
    w("Certificates re-proved for G5: %s." % ", ".join("`%s`" % x["name"] for x in g5b["rows"]))
    w("")
if G6S:
    b = G6S["part_B"]
    a = G6S["part_A"]
    w("**Post hoc supplement to G6 (not the gate; `checks/g6_supplement.py`).** The tensors on the laptop belong to %d stored states (n = 57, "
      "Jz = 1.6). (A) Among the (row, component) pairs of all %d NOT CERTIFIED rows, %d have tensors here%s. (B) Each of the %d states evaluated from its "
      "tensors at Jz = 1.5 and 1.7 with the independent evaluator against the linear rule: %d pairs, largest difference %.1e, all within "
      "1e-8: %s. This supports the linear rule as an identity; it does not check the decisive components." % (
          len(G6S["states_with_tensors"]), a["n_rows"], a["n_checked"], "" if not a["n_checked"] else " (m_s at n = 57, Jz = %s; largest difference %.1e)" % (", ".join("%.1f" % c["Jz"] for c in a["checked"]), a["max_dE"]),
          len(G6S["states_with_tensors"]), b["n_checked"], b["max_dE"], "yes" if b["all_within_1e8"] else "NO"))
    w("")

# ------------------------------------------------------------------------------------------------ Sec. 11 secondary
w("## 11. Secondary rows (Sec. 3 of the declaration)")
w("")
w("**Window at E_first (first-stage states, in the sector by construction), m_s, like-for-like. New.**")
w("")
w("| n | de_first range | CERTIFIED_s at | NOT CERTIFIED_s at | GRAY_s at | J*_s |")
w("|---|---|---|---|---|---|")
for n in ("57", "115"):
    fs = X["first_stage"][n]
    st = {r["key"]: r["like"]["status"] for r in fs}
    js = None
    for k in reversed(TRAIN):
        if st.get(k) != "CERTIFIED_s":
            break
        js = k
    w("| %s | %.4f to %.4f | %s | %s | %s | %s |" % (n, min(r["de_first"] for r in fs), max(r["de_first"] for r in fs),
                                                    ranges([k for k in st if st[k] == "CERTIFIED_s"]), ranges([k for k in st if st[k] == "NOT_CERTIFIED_s"]),
                                                    ranges([k for k in st if st[k] == "GRAY_s"]), js or "-"))
w("")
w("**Comparison variant (`skqd_post_select`), secondary everywhere. New.**")
w("")
w("| n | what is public | gate G2 | gate G3 | label | J*_s | CERTIFIED_s | NOT CERTIFIED_s | CERTIFIED (exact) | NOT CERTIFIED (explicit) | GRAY (Sec. 2) | training couplings |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for n in ("57", "115"):
    c = X["comparison"][n]
    for lab in ("m_s", "Czz_bar", "C2_bar"):
        j = c["jstar"][lab]
        w("| %s | %s | %s | %s | %s | %s | %d | %d | %s | %s | %s | %d |" % (
            n, "energies and labels (minus Jz = %s)" % ", ".join(c["excluded"]) if c["has_labels"] else "energies only",
            "-" if c["G2"] is None else ("PASS" if c["G2"]["pass"] else "FAIL: %s" % c["G2"]["failed"]), "PASS" if c["G3"]["pass"] else "FAIL",
            lab, f(j["J_star_s"], 1), j["like"]["certified"], j["like"]["not_certified"],
            j["sec2"]["certified_exact"] if c["has_labels"] else "-", j["sec2"]["not_certified"] if c["has_labels"] else "-",
            j["sec2"]["gray"] if c["has_labels"] else "-", j["n_training"]))
w("")
w("At n = 115 the comparison variant has no J* because its largest training coupling (6.0) is one of the four excluded by gate G2 and a "
  "coupling without a status is not a certified point. Its rows are in `out/map_secondary.json`.")
w("")
w("**Extension E1.** Not available when the map was run (`real_data/e1/` held no certificate). There is no E1 column in these results. "
  "S, S_3/4, S_1/2 and S_p never use E1. Note for whoever adds the column: with certificates in `e1/` the sealed code adds a key "
  "`secondary_E1` to `S_sets.json`, whose SHA-256 would then differ; it refuses to overwrite the existing file. Run it with another "
  "`--out` folder so that the hashed `out/S_sets.json` stays as it is.")
w("")

# ------------------------------------------------------------------------------------------------ Sec. 12 spot check
w("## 12. Post hoc: independent check of the exact intervals (`checks/spotcheck_exact_intervals.py`; not declared, decides nothing)")
w("")
if SPOT:
    sm = SPOT["summary"]
    w("A separate script of this task, written from the text of the declaration, importing nothing of the sealed code (standard library, "
      "`fractions.Fraction`), rebuilt the interval of m_s and Czz_bar at all 50 couplings of both sizes from the certificate files and the "
      "converted data. Rows compared with the sealed output: %d; identical in both ends as exact rationals and in both flags: %d. "
      "Certified rows whose label or truth lies outside the interval: %d. Its counts: %s. Six rows are printed in full in "
      "`checks/spotcheck_exact_intervals_stdout.txt` (m_s at n = 57, Jz = 3.4 and 3.5; m_s at n = 115, Jz = 4.0 and 5.0; Czz_bar at n = 57, "
      "Jz = 5.0 and at n = 115, Jz = 4.0)." % (
          sm["n_compared"], sm["n_equal_to_sealed"], len(sm["G7_violations"]),
          "; ".join("n = %s %s (%s): %d of 45, J*_exact %s" % (k.split("_")[0], "m_s" if "_m_s_" in k else "Czz_bar", "tau_rf" if k.endswith("tau_rf") else "tau",
                                                              v["certified_of_45"], v["J_star_exact"]) for k, v in sorted(sm.items()) if isinstance(v, dict))))
else:
    w("Not run.")
w("")

_cons = os.path.join(CHK, "consistency_witness_inside_exact.txt")
if os.path.exists(_cons):
    _ct = [x.strip().rstrip(".") for x in open(_cons, encoding="utf-8").read().strip().splitlines()[3:6]]
    w("**Post hoc: explicit states against exact bounds (`checks/finalize_rd_map.py`; not declared, decides nothing).** The two explicit "
      "witness mixtures of a row lie in W(E_real, M_real), so their labels must lie inside the exact interval of the same row. %s; %s; %s. "
      "The two sides of Sec. 2 (stored DMRG states, exact-arithmetic certificates) do not depend on each other, so this checks both." % tuple(_ct))
    w("")

# ------------------------------------------------------------------------------------------------ Sec. 13 lists
w("## 13. Re-executed, only compared, not checked")
w("")
w("- **Re-executed by this task:** the sealed map code on `converted/` (one run, default options: hash check of G1, G2-G7, re-proof of the "
  "deciding certificates); the independent recomputation of the 200 exact rows (Sec. 12); the post hoc supplement to G6; `sha256sum` of "
  "the declaration, of every code file listed in Sec. 11 of the declaration (all equal) and of the pinned archive.")
w("- **Only compared (not recomputed here):** the stored map (chains, thresholds, states), read through its own code; the stored exact "
  "certificates other than the %d re-proved for G5 (each has its recorded verification; 196 distinct ones were re-proved by the review "
  "report `math-rigorous-bounds`); this project's references against the authors' DMRG (G4)." % (0 if g5b.get("skipped") else len(g5b["rows"])))
w("- **Not checked:** the conversion of the archive (G1 re-run); the energies of the decisive witness components from their tensors (G6, "
  "first part); that the published energy and site magnetizations belong to one state beyond the necessary condition of G2; the unit tests "
  "were not run again (gate G8 was passed and recorded by the sealing task).")
w("- **Code:** no sealed file was changed. SHA-256 of the six map code files at run time (from `out/map_summary.json`): %s." % (
    "; ".join("`%s` %s" % (k, v[:16]) for k, v in sorted(S["code_sha256"].items()))))
w("- **Files:** `out/S_sets.json`, `out/S_sets.sha256`, `out/map_rows.json`, `out/map_summary.json`, `out/map_secondary.json`, "
  "`out/map_gates.json`, `out/map_tables.md`, `out/SHA256SUMS_map.txt`, `out/g5/` (sealed code); `out/map_real.json`, "
  "`results/RESULTS_map.md` (this script); `checks/spotcheck_exact_intervals.*`, `checks/g6_supplement.*`, `checks/finalize_rd_map.py`, "
  "`checks/consistency_witness_inside_exact.txt`; `DEVIATIONS.md`; hashes in "
  "`results/SHA256SUMS_rd-map.txt`.")
w("")

with open(os.path.join(HERE, "RESULTS_map.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(L) + "\n")
print("map_real.json: %d rows, SHA-256 %s" % (len(real_rows), sha(os.path.join(OUT, "map_real.json"))))
print("RESULTS_map.md: %d lines, SHA-256 %s" % (len(L), sha(os.path.join(HERE, "RESULTS_map.md"))))
print("NOT CERTIFIED rows: %d, of which resting on a re-evaluated energy: %d" % (len(nc_rows), len(nc_re)))
