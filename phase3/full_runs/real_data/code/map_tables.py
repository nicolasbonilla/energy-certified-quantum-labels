# real_data / map_tables.py  (own code; 2026-11-12; task rd-code-map)
#
# DECLARATION.md Secs. 3, 4, 6 and the sets of Sec. 7, built on map_certs.py (exact side) and map_stored.py (explicit
# states, like-for-like):
#   build_row / build_rows     one row per (size, coupling, label): eps_real, de_real, q, the three statuses of Sec. 2
#                              with their intervals and widths in units of tau, f_in, f_out, the largest eps at which an
#                              exact row would still be CERTIFIED (exact), both tolerances;
#   jstar, counts              J* under each rule (stored definition) and the counts out of 45;
#   predicted_vs_obtained      the table of the 171 stored rows with its four relations, stored J* against J*_s, the
#                              rule "confirmed by the data", and the stored claims C-A, C-B, C-C re-evaluated;
#   accuracy_factors           forms A and B at the test couplings (and 1.5 apart), headline rounded down;
#   filter_table               the filter of Sec. 6 (exact, reference-free, like-for-like);
#   s_sets / write_s_sets      S, S_3/4, S_1/2 and the primary set S_p, written with a SHA-256 (out/S_sets.json in the
#                              format read by rd_common.parse_sets, out/S_sets.sha256).
# Every exact statement is a comparison of fractions.Fraction; floats are printed copies.
import os
from fractions import Fraction

import map_common as C
import map_certs as MC
import map_stored as MS

SETS_SCHEMA = "p5-real-data-S-sets-v1"
DECISIVE = ("CERTIFIED", "NOT_CERTIFIED")


# ------------------------------------------------------------------------------------------------ one row
def exact_side(certs, n, label, J, E_real, M_real, tau, E0, G, eps=None):
    """Sec. 2 certified side of one row (labels m_s and Czz_bar). E_real, tau, E0: floats, taken as the dyadic numbers
    they are; M_real: exact rational. JSON-ready dict."""
    J = C.jfr(J)
    rng = MC.in_range(certs, n, J)
    pool = MC.make_pool(certs, n, label, J, n_e=len(G["edges"]))
    iv = MC.exact_interval(pool, Fraction(E_real), M_real, G["M0"])
    if iv is None:
        return dict(exists=False, in_range=rng, certified=False, certified_rf=False,
                    reason="no certificate on at least one side")
    jd = MC.judge(iv, Fraction(tau))
    out = dict(exists=True, in_range=rng, empty=iv["empty"], lo=float(iv["lo"]), hi=float(iv["hi"]),
               lo_exact=C.fstr(iv["lo"]), hi_exact=C.fstr(iv["hi"]), width=float(iv["width"]),
               width_exact=C.fstr(iv["width"]), tau=float(jd["tau"]), tau_rf=float(jd["tau_rf"]),
               tau_rf_exact=C.fstr(jd["tau_rf"]), width_over_tau=jd["width_over_tau"],
               width_over_tau_rf=jd["width_over_tau_rf"],
               certified=bool(jd["within_tau"] and rng), certified_rf=bool(jd["within_tau_rf"] and rng),
               within_tau_outside_range=bool(jd["within_tau"] and not rng),
               within_tau_rf_outside_range=bool(jd["within_tau_rf"] and not rng),
               capped=[bool(iv["lo"] != iv["lo_raw"]), bool(iv["hi"] != iv["hi_raw"])],
               n_bounds={"+": iv["n_bounds"][1], "-": iv["n_bounds"][-1]}, sides=MC.describe_sides(iv),
               certificates=[m.ident() for m in MC.winners(iv)])
    if rng and not iv["empty"]:
        le = MC.largest_E(pool, M_real, G["M0"], Fraction(tau), iv["E_used"])
        if le is not None:
            em = le["E"] - C.ALLOW - Fraction(E0)
            out.update(eps_max=float(em), eps_max_exact=C.fstr(em), eps_max_is_exact_root=le["exact"],
                       f_exact=(float(em) / eps) if (eps is not None and eps > 0) else None)
    return out


def sec2_status(exact, lower, which="certified"):
    cert = bool(exact and exact.get(which))
    nc = bool(lower and lower.get("not_certified"))
    if cert and nc:
        return "CONFLICT"
    return "CERTIFIED_EXACT" if cert else ("NOT_CERTIFIED" if nc else "GRAY")


def _clean_lower(lw):
    if lw is None:
        return None
    out = {k: v for k, v in lw.items() if k not in ("comps_min", "comps_max")}
    out["components"] = dict(min=[list(c) for c in lw.get("comps_min", [])], max=[list(c) for c in lw.get("comps_max", [])])
    return out


def build_row(stored, certs, real, n, J, label, group="dataset", certs_e1=None):
    """One row of the map on the real energies (Sec. 3). real: output of map_common.parse_real / load_real."""
    J = C.jfr(J)
    key, G = C.jkey(J), real["G"]
    rec = real[group][key]
    tr = MS.truth(stored, real, n, J, label)
    E, E0, tau = rec["E_real"], tr["E0"], tr["tau"]
    eps = E - E0
    row = dict(n=n, Jz=float(J), key=key, label=label, group=group, training=bool(J in C.TRAIN_J), E_real=E, E0=E0,
               E0_source=tr["E0_source"], eps_real=eps, de_real=eps / n, O_GS=tr["O_GS"], O_source=tr["O_source"],
               tau=tau, has_chain=stored.has_chain(n, J, label), has_labels=rec["has_labels"])
    like = stored.like_for_like(n, J, label, E, E0, tau)
    like.pop("comps_min", None), like.pop("comps_max", None)
    for k in ("w_out", "w_in"):
        like[k + "_over_tau"] = (like[k] / tau) if like.get(k) is not None else None
    row["like"] = like
    lower = exact = exact_e1 = None
    if rec["has_labels"]:
        lab = rec["labels"][label]
        row.update(M_real=rec["M_float"], M_real_exact=C.fstr(rec["M"]), q=(G["M0"] - rec["M_float"]) / 2.0,
                   label_real=lab, miss_tau=abs(lab - tr["O_GS"]) / tau if tau > 0 else None)
        lower = stored.not_certified(n, J, label, E, rec["M_float"], tau)
        lower["w_lower_over_tau"] = (lower["w_lower"] / tau) if lower.get("w_lower") is not None else None
        if label in C.EXACT_LABELS:
            exact = exact_side(certs, n, label, J, E, rec["M"], tau, E0, G, eps)
            if exact.get("exists"):
                le = rec["labels_exact"][label]
                lo, hi = Fraction(exact["lo_exact"]), Fraction(exact["hi_exact"])
                exact.update(label_inside=bool(lo <= le <= hi), truth_inside=bool(lo <= Fraction(tr["O_GS"]) <= hi))
            if certs_e1:
                exact_e1 = exact_side(list(certs) + list(certs_e1), n, label, J, E, rec["M"], tau, E0, G, eps)
    row.update(lower=_clean_lower(lower), exact=exact, exact_e1=exact_e1,
               status=sec2_status(exact, lower), status_rf=sec2_status(exact, lower, "certified_rf"))
    if not rec["has_labels"]:                      # no published magnetization: only the like-for-like status exists
        row["status"] = row["status_rf"] = "NOT_AVAILABLE"
    if exact_e1 is not None:
        row.update(status_e1=sec2_status(exact_e1, lower), status_e1_rf=sec2_status(exact_e1, lower, "certified_rf"))
    return row


def build_rows(stored, certs, real, n, group="dataset", labels=C.LABELS, couplings=C.ALL_J, certs_e1=None, log=None):
    rows = []
    for J in couplings:
        if C.jkey(J) not in real[group]:
            continue
        for label in labels:
            rows.append(build_row(stored, certs, real, n, J, label, group, certs_e1))
        if log:
            log("   n = %d  Jz = %s  done" % (n, C.jkey(J)))
    return rows


def index(rows):
    return {(r["n"], r["key"], r["label"]): r for r in rows}


def first_stage_rows(stored, real, n):
    """Sec. 3, secondary: the window at E_first (first-stage states are in the sector by construction); like-for-like
    statuses of m_s only."""
    out = []
    for J in C.ALL_J:
        key = C.jkey(J)
        rec = real["dataset"].get(key)
        if rec is None:
            continue
        tr = MS.truth(stored, real, n, J, "m_s")
        like = stored.like_for_like(n, J, "m_s", rec["E_first"], tr["E0"], tr["tau"])
        like.pop("comps_min", None), like.pop("comps_max", None)
        out.append(dict(n=n, Jz=float(J), key=key, label="m_s", E_first=rec["E_first"], eps_first=rec["E_first"] - tr["E0"],
                        de_first=(rec["E_first"] - tr["E0"]) / n, tau=tr["tau"], like=like))
    return out


# ------------------------------------------------------------------------------------------------ J* and counts
def jstar(flags):
    """Stored definition: the smallest training Jz from which every larger training point is certified; resolution
    0.1. flags: {coupling key: True / False / None}. A point without a status (None: no chain to interpolate from, or
    'no decision' after a gate) is not a certified point, so J* cannot extend below it. (The stored code skipped
    such entries; the stored map has none, so both readings give the stored J*.) None when the largest training
    coupling is not certified."""
    js = None
    for J in reversed(C.TRAIN_J):
        if not flags.get(C.jkey(J)):
            break
        js = float(J)
    return js


def _train(ix, n, label):
    return [ix[(n, C.jkey(J), label)] for J in C.TRAIN_J if (n, C.jkey(J), label) in ix]


def jstar_table(ix, n, label):
    """J* under each rule and the counts out of 45 for one label and size."""
    tr = _train(ix, n, label)
    like = {r["key"]: (None if r["like"]["status"] == "NA_s" else r["like"]["status"] == "CERTIFIED_s") for r in tr}
    out = dict(n=n, label=label, n_training=len(tr), J_star_s=jstar(like),
               no_decision=sum(1 for r in tr if r.get("no_decision")),
               like=dict(certified=sum(1 for r in tr if r["like"]["status"] == "CERTIFIED_s"),
                         not_certified=sum(1 for r in tr if r["like"]["status"] == "NOT_CERTIFIED_s"),
                         gray=sum(1 for r in tr if r["like"]["status"] == "GRAY_s"),
                         not_available=sum(1 for r in tr if r["like"]["status"] == "NA_s"),
                         interpolated=sum(1 for r in tr if r["like"]["interpolated"])))
    for tag, sk, ek in (("sec2", "status", "certified"), ("sec2_rf", "status_rf", "certified_rf"),
                        ("sec2_e1", "status_e1", "certified"), ("sec2_e1_rf", "status_e1_rf", "certified_rf")):
        if not tr or sk not in tr[0]:
            continue
        src = "exact_e1" if "e1" in tag else "exact"
        d = dict(certified_exact=sum(1 for r in tr if r[sk] == "CERTIFIED_EXACT"),
                 not_certified=sum(1 for r in tr if r[sk] == "NOT_CERTIFIED"), gray=sum(1 for r in tr if r[sk] == "GRAY"),
                 conflict=sum(1 for r in tr if r[sk] == "CONFLICT"))
        if label in C.EXACT_LABELS:
            d["J_star_exact"] = jstar({r["key"]: bool(r[src] and r[src].get(ek)) for r in tr})
        out[tag] = d
    return out


# ------------------------------------------------------------------------------------------------ predicted vs obtained
def relation(predicted, obtained):
    """Sec. 3: confirmed (same decisive status), resolved (predicted GRAY, obtained decisive), opened (predicted
    decisive, obtained GRAY_s), contradicted (CERTIFIED against NOT CERTIFIED). A row GRAY on both sides is none of
    the four and is listed as 'gray_both'."""
    g = obtained[:-2] if obtained.endswith("_s") else obtained
    if g == "NA":
        return "not_available"
    if predicted in DECISIVE:
        return "confirmed" if g == predicted else ("opened" if g == "GRAY" else "contradicted")
    return "resolved" if g in DECISIVE else "gray_both"


def predicted_vs_obtained(stored, ix):
    """The 171 stored rows (reading 1): predicted | like-for-like at E_real | relation | status of Sec. 2; stored J*
    against J*_s; the rule; the stored claims C-A, C-B, C-C re-evaluated."""
    table, cnt = [], {}
    for (n, key, label), r in sorted(stored.rows.items(), key=lambda kv: (kv[0][0], C.LABELS.index(kv[0][2]), float(kv[0][1]))):
        row = ix.get((n, key, label))
        if row is None:
            rel, like, s2, s2rf = "no_real_data", None, None, None
        else:
            like, s2, s2rf = row["like"]["status"], row["status"], row["status_rf"]
            rel = relation(r["status"], like)
        cnt[rel] = cnt.get(rel, 0) + 1
        table.append(dict(n=n, Jz=r["Jz"], label=label, predicted=r["status"], like_for_like=like, relation=rel,
                          sec2=s2, sec2_rf=s2rf, f_in=None if row is None else row["like"]["f_in"],
                          f_out=None if row is None else row["like"]["f_out"]))
    jrows, j_ok = [], True
    for n in C.SIZES:
        for label in C.LABELS:
            js = stored.SM["jstar"].get("%d_%s_r1" % (n, label))
            if js is None or js.get("J_star_central") is None:
                continue
            got = jstar_table(ix, n, label)["J_star_s"]
            ok = got is not None and abs(got - js["J_star_central"]) <= 0.1 + 1e-9
            j_ok = j_ok and ok
            jrows.append(dict(n=n, label=label, J_star_stored=js["J_star_central"], J_star_stored_strict=js.get("J_star_strict"),
                              n_certified_stored=js.get("n_certified_central"), J_star_s=got, within_0p1=bool(ok)))
    contradicted = [t for t in table if t["relation"] == "contradicted"]
    return dict(table=table, counts=cnt, contradicted=contradicted, jstar=jrows,
                confirmed_by_the_data=bool(not contradicted and j_ok),
                claims_like_for_like=claims(stored, ix, lambda r: r["like"]["status"].replace("_s", "")),
                claims_sec2=claims(stored, ix, lambda r: {"CERTIFIED_EXACT": "CERTIFIED"}.get(r["status"], r["status"])))


def claims(stored, ix, status_of):
    """C-A, C-B, C-C of map/DECLARATION.md Sec. 4 on the stored rows, with the statuses obtained from the data
    (C-B is no longer conditional on a floor: the energies at Jz = 1.1-1.4 are now real)."""
    rows = [(k, r, ix[k]) for k, r in stored.rows.items() if k in ix]
    st = lambda x: status_of(x[2])
    hi = {n: [x for x in rows if x[0][0] == n and x[0][2] in ("m_s", "Czz_bar") and x[1]["Jz"] >= 3.95] for n in C.SIZES}
    allc = {n: bool(hi[n]) and all(st(x) == "CERTIFIED" for x in hi[n]) for n in hi}
    anyc = {n: any(st(x) == "CERTIFIED" for x in hi[n]) for n in hi}
    gates_ok = bool(stored.SM["claims"]["C-A"]["gates_ok"])
    if allc[57] and allc[115] and gates_ok:
        v = "MAP-POSITIVE"
    elif not anyc[115]:
        v = "MAP-ABSENT"
    else:
        v = "MAP-PARTIAL"
    low = [x for x in rows if x[1]["Jz"] <= 1.65]
    loc = [x for x in rows if x[0][2] in C.LOCALS]
    name = lambda x: [x[0][0], x[1]["Jz"], x[0][2], st(x)]
    return {"C-A": dict(verdict=v, stored_gates_ok=gates_ok, all_certified={str(n): allc[n] for n in allc},
                        not_certified_rows=[name(x) for n in hi for x in hi[n] if st(x) != "CERTIFIED"], n_rows=sum(len(hi[n]) for n in hi)),
            "C-B": dict(holds=bool(low) and all(st(x) == "NOT_CERTIFIED" for x in low), n_rows=len(low),
                        exceptions=[name(x) for x in low if st(x) != "NOT_CERTIFIED"]),
            "C-C": dict(no_local_certified=not any(st(x) == "CERTIFIED" for x in loc), n_rows=len(loc),
                        certified_local_rows=[name(x) for x in loc if st(x) == "CERTIFIED"],
                        gray=[name(x) for x in loc if st(x) == "GRAY"])}


# ------------------------------------------------------------------------------------------------ Sec. 4
def accuracy_factors(stored, real, ix, n):
    """Forms A and B for m_s (headline) and Czz_bar at Jz = 1.1-1.4 (stored de_star_in) and at 1.5 (threshold of the
    re-evaluated pool with q = 0), de*_out alongside."""
    out = {}
    de16 = ix[(n, "1.6", "m_s")]["de_real"]
    for label in ("m_s", "Czz_bar"):
        vals = []
        for J in C.TEST_J + C.APART_J:
            key = C.jkey(J)
            de = ix[(n, key, label)]["de_real"]
            if J in C.TEST_J:
                r = stored.rows[(n, key, label)]
                de_in, de_out, src, flag = r["de_star_in"], r["de_star_out"], "stored row (de_star_in)", None
            else:
                tr = MS.truth(stored, real, n, J, label)
                et, info = stored.eps_tau_in_pool(n, J, label, tr["E0"], tr["tau"])
                de_in = (et / n) if et else None
                eo = stored.interp(n, label, J, "eps_tau_out_lb")
                de_out = (eo / n) if eo else None
                src, flag = "re-evaluated pool of Sec. 2 with q = 0 (%s)" % info["couplings"], "de*_out interpolated, not a bound"
            vals.append(dict(Jz=float(J), de_real=de, de_star_in=de_in, de_star_out=de_out, source=src, flag=flag,
                             F_A=(de / de_in) if de_in else None, F_B=(de16 / de_in) if de_in else None,
                             test_coupling=bool(J in C.TEST_J)))
        fa = [v["F_A"] for v in vals if v["test_coupling"] and v["F_A"] is not None]
        fb = [v["F_B"] for v in vals if v["test_coupling"] and v["F_B"] is not None]
        out[label] = dict(values=vals, de_real_at_1p6=de16, min_F_A=min(fa) if fa else None, min_F_B=min(fb) if fb else None,
                          headline_F_A=C.round_down_2sig(min(fa)) if fa else None,
                          headline_F_B=C.round_down_2sig(min(fb)) if fb else None)
    return out


# ------------------------------------------------------------------------------------------------ Sec. 6
def filter_table(ix, n, label="m_s", keep=lambda r: bool(r["exact"] and r["exact"].get("certified")), n19=None):
    """Sec. 6 for one size and label over the 45 training labels (the five others apart). keep: the rule.
    n19: optional {coupling key: m_s of the exact 19-site ground state} for the small classical calculation."""
    tr = _train(ix, n, label)
    kept, dropped = [r for r in tr if keep(r)], [r for r in tr if not keep(r)]
    ms = lambda rs: [r["miss_tau"] for r in rs]
    stat = lambda v: dict(n=len(v), max=max(v) if v else None, mean=(sum(v) / len(v)) if v else None)
    out = dict(n=n, label=label, n_training=len(tr), n_kept=len(kept), kept=[r["Jz"] for r in kept],
               dropped=[r["Jz"] for r in dropped], miss_kept=stat(ms(kept)), miss_dropped=stat(ms(dropped)),
               dropped_within_half_tau=sum(1 for r in dropped if r["miss_tau"] <= 0.5),
               dropped_within_tau=sum(1 for r in dropped if r["miss_tau"] <= 1.0),
               kept_above_half_tau=sum(1 for r in kept if r["miss_tau"] > 0.5),
               kept_above_tau=sum(1 for r in kept if r["miss_tau"] > 1.0),
               per_label=[dict(Jz=r["Jz"], kept=bool(keep(r)), miss_tau=r["miss_tau"]) for r in tr],
               apart=[dict(Jz=float(J), kept_by_rule=bool(keep(ix[(n, C.jkey(J), label)])), miss_tau=ix[(n, C.jkey(J), label)]["miss_tau"])
                      for J in C.TEST_J + C.APART_J if (n, C.jkey(J), label) in ix])
    if n19 is not None and label == "m_s":
        cl = {}
        for J in C.ALL_J:
            r = ix.get((n, C.jkey(J), "m_s"))
            if r is not None and C.jkey(J) in n19:
                cl[C.jkey(J)] = abs(n19[C.jkey(J)] - r["O_GS"]) / r["tau"]
        kk = [cl[C.jkey(C.jfr(j))] for j in out["kept"] if C.jkey(C.jfr(j)) in cl]
        out["classical_n19"] = dict(miss_tau=cl, max_over_kept=max(kk) if kk else None,
                                    at_test=[cl.get(C.jkey(J)) for J in C.TEST_J],
                                    all_kept_within_a_fifth_of_tau=bool(kk and max(kk) <= 0.2))
    return out


# ------------------------------------------------------------------------------------------------ Sec. 7 sets
def choose_S_p(S, S34, S12, nmin=15):
    for name, s in (("S_1_2", S12), ("S_3_4", S34), ("S", S)):
        if len(s) >= nmin:
            return name, list(s)
    return None, []


def s_sets(ix, n, source="exact"):
    """S: training couplings whose m_s row is CERTIFIED (exact) with the reference tolerance; S_3/4, S_1/2: interval at
    most 3/4 and 1/2 of tau wide (exact comparisons); S_p: the most stringent with at least 15 couplings.
    source='exact' uses the stored certificates only (the declared sets); 'exact_e1' gives the secondary E1 sets."""
    S, S34, S12 = [], [], []
    for r in _train(ix, n, "m_s"):
        ex = r.get(source)
        if not (ex and ex.get("certified")):
            continue
        w, tau = Fraction(ex["width_exact"]), Fraction(r["tau"])
        S.append(r["Jz"])
        if 4 * w <= 3 * tau:
            S34.append(r["Jz"])
        if 2 * w <= tau:
            S12.append(r["Jz"])
    name, sp = choose_S_p(S, S34, S12)
    return dict(S=S, S_3_4=S34, S_1_2=S12, S_p=sp, S_p_name=name)


def sets_object(ix_by_n, decl_sha, with_e1=False):
    obj = dict(schema=SETS_SCHEMA, declaration_sha256=decl_sha, label="m_s",
               note="S, S_3_4, S_1_2, S_p of DECLARATION.md Sec. 7 (f3), from the stored certificates only; intervals "
                    "of m_s at (E_real, M_real): exact = interval I of Sec. 2, lower = labels of the two explicit "
                    "witness mixtures, outer_like = like-for-like outer of the stored map (indicative).", sizes={})
    for n, ix in sorted(ix_by_n.items()):
        s = s_sets(ix, n)
        iv = {}
        for J in C.ALL_J:
            r = ix.get((n, C.jkey(J), "m_s"))
            if r is None:
                continue
            ex, lw, lk = r.get("exact"), r.get("lower"), r["like"]
            iv[C.jkey(J)] = dict(
                tau=r["tau"], q=r.get("q"), training=r["training"],
                exact=None if not (ex and ex.get("exists")) else dict(lo=ex["lo"], hi=ex["hi"], lo_exact=ex["lo_exact"],
                                                                      hi_exact=ex["hi_exact"], width_over_tau=ex["width_over_tau"],
                                                                      certified=ex["certified"], certified_rf=ex["certified_rf"]),
                lower=None if not (lw and lw.get("witness")) else dict(lo=lw["witness"][0], hi=lw["witness"][1],
                                                                        not_certified=lw["not_certified"]),
                outer_like=None if not lk.get("outer") else dict(lo=lk["outer"][0], hi=lk["outer"][1]))
        s["intervals"] = iv
        if with_e1:
            s["secondary_E1"] = s_sets(ix, n, "exact_e1")
        obj["sizes"][str(n)] = s
    return obj


def write_s_sets(ix_by_n, decl_sha, out_dir=None, with_e1=False, replace=False):
    """Writes <out>/S_sets.json and <out>/S_sets.sha256; returns (object, sha256). The sets are fixed before any
    learning number is computed (Sec. 7): an existing S_sets.json with ANOTHER content is not overwritten unless
    replace=True (the same content is written again without complaint: the file is deterministic)."""
    import json
    out_dir = out_dir or C.OUT
    obj = sets_object(ix_by_n, decl_sha, with_e1)
    p = os.path.join(out_dir, "S_sets.json")
    new = C.sha256_bytes((json.dumps(obj, indent=1, sort_keys=True, allow_nan=False, ensure_ascii=True) + "\n").encode("utf-8"))
    if os.path.exists(p) and not replace and C.sha256_file(p) != new:
        raise RuntimeError("%s exists with another content (SHA-256 %s, new %s): the nested sets were already fixed. "
                           "Nothing was overwritten." % (p, C.sha256_file(p), new))
    sha = C.dump_json(p, obj)
    assert sha == new
    with open(os.path.join(out_dir, "S_sets.sha256"), "w", encoding="utf-8", newline="\n") as f:
        f.write("%s  S_sets.json\n" % sha)
    assert C.sha256_file(p) == sha
    return obj, sha
