# real_data / run_map.py  (own code; 2026-11-12; task rd-code-map)
#
# ENTRY POINT of the map on the real energies: DECLARATION.md Secs. 2, 3, 4, 6, the sets of Sec. 7 and gates G1-G7.
#
#   python -B -I run_map.py [--out DIR] [--g1-rerun] [--no-g5-reprove] [--no-g6-tensors]
#
# It REFUSES to read converted/ unless DECLARATION.sha256 exists and equals the SHA-256 of DECLARATION.md (exit code 3;
# the check is the first statement of main() and is repeated inside the loader). Nothing is unpickled; no code of the
# downloaded repository is imported or executed. --g1-rerun runs this project's own converter again in a separate
# process (gate G1 as declared); without it G1 checks the hashes only and is reported as incomplete.
#
# Outputs (deterministic JSON, sorted keys, no time stamps), in --out (default real_data/out):
#   S_sets.json, S_sets.sha256   the nested sets S, S_3/4, S_1/2, S_p of Sec. 7 (written first)
#   map_rows.json                2 sizes x 50 couplings x 7 labels, every number of every row
#   map_summary.json             J* under each rule, counts, the table "predicted versus obtained" with its relations,
#                                claims, accuracy factors (forms A and B), filter tables, certificate counts
#   map_secondary.json           window at E_first (m_s, like-for-like) and the comparison variant
#   map_gates.json               G1-G7
#   map_tables.md                the main tables as text
#   SHA256SUMS_map.txt           SHA-256 of the files above
# run() takes already parsed data and is what the unit tests call on synthetic objects.
import argparse
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import map_common as C      # noqa: E402
import map_certs as MC      # noqa: E402
import map_gates as MG      # noqa: E402
import map_stored as MS     # noqa: E402
import map_tables as T      # noqa: E402

CODE_FILES = ("map_common.py", "map_certs.py", "map_stored.py", "map_tables.py", "map_gates.py", "run_map.py")
RULES = dict(
    grid="the 16 grid couplings of map/DECLARATION.md Sec. 3 (witness.GRID); a grid coupling is bracketed by itself",
    stored_chain="a chain of the row's own label and size is stored at the row's coupling (a row of summary_map.json)",
    truth="E0: this project's reference at the 18 + 16 couplings of summary_map.json; O_GS: this project's reference "
          "where summary_map.json has a row for that label, size and coupling; otherwise the authors' DMRG",
    M_allowance="the worse of M_real +- 1e-6 is taken certificate by certificate (holds for every M in between)",
    range="CERTIFIED (exact) is assigned only inside [3.4, 6.0] (n = 57) and [4.0, 6.0] (n = 115), for both labels; a "
          "Czz_bar interval outside is reported and flagged",
    jstar_stored="stored J* = J_star_central of reading 1",
)


def _fmt(x, nd=4):
    return "-" if x is None else (("%." + str(nd) + "f") % x if isinstance(x, float) else str(x))


def tables_md(summary):
    L = ["# Map on the real energies: main tables (written by run_map.py)", "",
         "Declaration SHA-256: `%s`" % summary["declaration_sha256"], "",
         "## J* and counts out of 45 (per label and size)", "",
         "| n | label | J*_s | cert_s | notcert_s | gray_s | J*_exact | cert exact | J*_exact (ref-free) | cert exact (ref-free) | not certified (explicit) | gray |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, j in summary["jstar"].items():
        s2, rf = j.get("sec2", {}), j.get("sec2_rf", {})
        L.append("| %d | %s | %s | %d | %d | %d | %s | %s | %s | %s | %s | %s |" % (
            j["n"], j["label"], _fmt(j["J_star_s"], 1), j["like"]["certified"], j["like"]["not_certified"], j["like"]["gray"],
            _fmt(s2.get("J_star_exact"), 1), _fmt(s2.get("certified_exact")), _fmt(rf.get("J_star_exact"), 1),
            _fmt(rf.get("certified_exact")), _fmt(s2.get("not_certified")), _fmt(s2.get("gray"))))
    p = summary["predicted_vs_obtained"]
    L += ["", "## Predicted from the figures versus obtained from the data", "",
          "Relations over the stored rows: %s. Contradicted rows: %d. Confirmed by the data (rule of Sec. 3): **%s**." % (
              ", ".join("%s %d" % kv for kv in sorted(p["counts"].items())), len(p["contradicted"]), p["confirmed_by_the_data"]), "",
          "| n | label | stored J* | J*_s | within 0.1 |", "|---|---|---|---|---|"]
    for j in p["jstar"]:
        L.append("| %d | %s | %s | %s | %s |" % (j["n"], j["label"], _fmt(j["J_star_stored"], 1), _fmt(j["J_star_s"], 1), j["within_0p1"]))
    L += ["", "| n | Jz | label | predicted | like-for-like at E_real | relation | status of Sec. 2 |", "|---|---|---|---|---|---|---|"]
    for t in p["table"]:
        L.append("| %d | %.1f | %s | %s | %s | %s | %s |" % (t["n"], t["Jz"], t["label"], t["predicted"], t["like_for_like"],
                                                              t["relation"], t["sec2"]))
    L += ["", "## Accuracy factors at the test couplings (Sec. 4)", "",
          "| n | label | Jz | de_real | de*_in | de*_out | F_A | F_B |", "|---|---|---|---|---|---|---|---|"]
    for n, d in summary["accuracy_factors"].items():
        for lab, f in d.items():
            for v in f["values"]:
                L.append("| %s | %s | %.1f | %s | %s | %s | %s | %s |" % (n, lab, v["Jz"], _fmt(v["de_real"], 6), _fmt(v["de_star_in"], 8),
                                                                      _fmt(v["de_star_out"], 8), _fmt(v["F_A"], 2), _fmt(v["F_B"], 2)))
            L.append("| %s | %s | headline | | | | more than %s | more than %s |" % (n, lab, _fmt(f["headline_F_A"], 0), _fmt(f["headline_F_B"], 0)))
    L += ["", "## Filter (Sec. 6), over the 45 training labels", "",
          "| n | label | rule | kept | largest miss kept | mean miss kept | largest miss dropped | dropped within tau/2 | dropped within tau | kept above tau/2 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, d in summary["filter"].items():
        for rule, f in d.items():
            L.append("| %d | %s | %s | %d | %s | %s | %s | %d | %d | %d |" % (
                f["n"], f["label"], rule, f["n_kept"], _fmt(f["miss_kept"]["max"]), _fmt(f["miss_kept"]["mean"]),
                _fmt(f["miss_dropped"]["max"]), f["dropped_within_half_tau"], f["dropped_within_tau"], f["kept_above_half_tau"]))
    L += ["", "## Nested sets (Sec. 7), m_s, stored certificates only", ""]
    for n, s in summary["sets"]["sizes"].items():
        L.append("- n = %s: |S| = %d, |S_3/4| = %d, |S_1/2| = %d, S_p = %s (%d couplings)" % (
            n, len(s["S"]), len(s["S_3_4"]), len(s["S_1_2"]), s["S_p_name"], len(s["S_p"])))
    L += ["", "S_sets.json SHA-256: `%s`" % summary["sets"]["sha256"], "", "## Gates", ""]
    for k, g in summary["gates"].items():
        L.append("- %s: %s" % (k, g))
    return "\n".join(L) + "\n"


def run(real, stored, loaded, decl_sha, out_dir, sizes=C.SIZES, couplings=C.ALL_J, certs_e1=None, n19=None,
        g1=None, g5_reprove=False, g6_tensors=True, log=print, replace_sets=False):
    """real: {n: parsed real data}. Writes the outputs into out_dir and returns the summary."""
    certs = loaded["certs"]
    os.makedirs(out_dir, exist_ok=True)
    gates, rows = {}, []
    if g1 is not None:
        gates["G1"] = g1
    for n in sizes:
        g2, g3, g4 = MG.g2_same_state(real[n]), MG.g3_energies(real[n]), MG.g4_truth(stored, real[n])
        gates.update({"G2_%d" % n: g2, "G3_%d" % n: g3, "G4_%d" % n: g4})
        log("n = %d: G2 %s, G3 %s, G4 %s; building rows" % (n, g2["pass"], g3["pass"], g4["pass"]))
        rn = T.build_rows(stored, certs, real[n], n, couplings=couplings, certs_e1=certs_e1)
        nb = MG.apply_no_decision(rn, g2, g3, g4)
        log("n = %d: %d rows, %d without decision" % (n, len(rn), nb))
        rows += rn
    ix = T.index(rows)
    # the nested sets are fixed and hashed first (Sec. 7: before any learning number is computed)
    sets, sets_sha = T.write_s_sets({n: {k: r for k, r in ix.items() if k[0] == n} for n in sizes}, decl_sha, out_dir,
                                    with_e1=bool(certs_e1), replace=replace_sets)
    log("S_sets.json written, SHA-256 %s" % sets_sha)
    jst = {"%d_%s" % (n, lab): T.jstar_table(ix, n, lab) for n in sizes for lab in C.LABELS}
    pvo = T.predicted_vs_obtained(stored, ix)
    fac = {str(n): T.accuracy_factors(stored, real[n], ix, n) for n in sizes if (n, "1.6", "m_s") in ix}
    keeps = dict(exact=lambda r: bool(r["exact"] and r["exact"].get("certified")),
                 exact_reference_free=lambda r: bool(r["exact"] and r["exact"].get("certified_rf")),
                 like_for_like=lambda r: r["like"]["status"] == "CERTIFIED_s")
    if certs_e1:
        keeps["exact_with_E1"] = lambda r: bool(r["exact_e1"] and r["exact_e1"].get("certified"))
    filt = {"%d_%s" % (n, lab): {rule: T.filter_table(ix, n, lab, keep=k, n19=n19) for rule, k in keeps.items()}
            for n in sizes for lab in C.EXACT_LABELS}
    # secondary rows
    sec = dict(first_stage={str(n): T.first_stage_rows(stored, real[n], n) for n in sizes}, comparison={})
    for n in sizes:
        if not real[n]["comparison"]:
            continue
        lab_any = any(r["has_labels"] for r in real[n]["comparison"].values())
        g2c = MG.g2_same_state(real[n], "comparison") if lab_any else None
        g3c = MG.g3_energies(real[n], "comparison")
        rc = T.build_rows(stored, certs, real[n], n, group="comparison", couplings=couplings)
        MG.apply_no_decision(rc, g2c, g3c, gates["G4_%d" % n])
        ixc = T.index(rc)
        sec["comparison"][str(n)] = dict(rows=rc, G2=g2c, G3=g3c, has_labels=lab_any, excluded=list(C.G2_EXCLUDED.get((n, C.COMPARISON), ())),
                                         jstar={lab: T.jstar_table(ixc, n, lab) for lab in C.LABELS})
    # gates that need the rows
    dec = MG.deciding_certificates(ix)
    gates["G5a"] = MG.g5_records(loaded, dec)
    names = sorted(c["name"] for c in dec.values())
    if g5_reprove:
        log("G5: re-proving %d deciding certificates with the independent verifier" % len(dec))
        gates["G5b"] = MG.g5_reprove(sorted(dec.values(), key=lambda c: c["name"]), os.path.join(out_dir, "g5"))
    else:
        gates["G5b"] = {"gate": "G5b", "skipped": True, "deciding": names, "pass": None}
    jstars = {}
    for n in sizes:
        for lab in C.LABELS:
            j = jst["%d_%s" % (n, lab)]
            jstars[(n, lab)] = [j["J_star_s"]] + [j[t]["J_star_exact"] for t in ("sec2", "sec2_rf", "sec2_e1", "sec2_e1_rf")
                                                  if t in j and "J_star_exact" in j[t]]
    near, other = MG.g6_select(rows, jstars, C.seed_from_hash(decl_sha))
    if g6_tensors:
        gates["G6a"] = MG.g6_linear(stored, near + other)
    else:
        gates["G6a"] = {"gate": "G6a", "skipped": True, "pass": None}
    gates["G6a"]["selected"] = dict(near_a_J_star=[(r["n"], r["Jz"], r["label"]) for r in near],
                                    drawn_with_the_seed=[(r["n"], r["Jz"], r["label"]) for r in other],
                                    seed=C.seed_from_hash(decl_sha))
    gates["G6b"] = MG.g6_energies(rows)
    gates["G7"] = MG.g7_filter(rows)
    gate_summary = {k: (g.get("pass") if not g.get("skipped") else "skipped") for k, g in gates.items()}
    for k in ("G1", "G6a"):
        if k in gates and gates[k].get("pass") and gates[k].get("complete") is False:
            gate_summary[k] = "pass on what could be checked; not complete"
    flags = dict(
        conflicts=[(r["n"], r["Jz"], r["label"]) for r in rows if "CONFLICT" in (r["status"], r["status_rf"])],
        czz_within_tau_outside_range=[(r["n"], r["Jz"]) for r in rows if r["exact"] and r["exact"].get("within_tau_outside_range")],
        empty_intervals=[(r["n"], r["Jz"], r["label"]) for r in rows if r["exact"] and r["exact"].get("empty")],
        orientation_not_plus=[(n, k) for n in sizes for k, d in real[n]["dataset"].items() if d.get("orientation") != 1] +
                             [(n, "dmrg " + k) for n in sizes for k, d in real[n]["dmrg"].items() if d.get("orientation") != 1 and C.jfr(k) in C.ALL_J])
    summary = dict(schema="p5-real-data-map-v1", declaration_sha256=decl_sha, rules=RULES, sizes=list(sizes),
                   certificates={k: v for k, v in loaded.items() if k not in ("certs", "excluded")},
                   certificates_E1=0 if not certs_e1 else len(certs_e1), n_rows=len(rows), jstar=jst,
                   predicted_vs_obtained=pvo, accuracy_factors=fac, filter=filt,
                   sets=dict(sha256=sets_sha, sizes={n: {k: v for k, v in s.items() if k != "intervals"} for n, s in sets["sizes"].items()}),
                   gates=gate_summary, flags=flags,
                   code_sha256={f: C.sha256_file(os.path.join(HERE, f)) for f in CODE_FILES})
    summary["certificates"]["by_size"] = {str(k): v for k, v in loaded["by_size"].items()}
    sums = {"S_sets.json": sets_sha}
    sums["map_rows.json"] = C.dump_json(os.path.join(out_dir, "map_rows.json"), dict(schema="p5-real-data-map-rows-v1", declaration_sha256=decl_sha, rows=rows))
    sums["map_summary.json"] = C.dump_json(os.path.join(out_dir, "map_summary.json"), summary)
    sums["map_secondary.json"] = C.dump_json(os.path.join(out_dir, "map_secondary.json"), sec)
    sums["map_gates.json"] = C.dump_json(os.path.join(out_dir, "map_gates.json"), gates)
    md = tables_md(summary)
    with open(os.path.join(out_dir, "map_tables.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    sums["map_tables.md"] = C.sha256_bytes(md.encode("utf-8"))
    with open(os.path.join(out_dir, "SHA256SUMS_map.txt"), "w", encoding="utf-8", newline="\n") as f:
        for k in sorted(sums):
            f.write("%s  %s\n" % (sums[k], k))
    return summary


def load_e1(certs):
    """Certificates of extension E1 (real_data/e1/, if any), accepted under the same checks; those already stored
    are dropped. They only feed the separate E1 column."""
    if not os.path.isdir(MC.E1_ROOT):
        return None
    have = set(x.sha for x in certs)
    e1 = [x for x in MC.load_certificates(roots=(MC.E1_ROOT,))["certs"] if x.sha not in have]
    return e1 or None


def load_n19():
    p = os.path.join(C.OUT, "n19", "n19_labels.json")
    if not os.path.exists(p):
        return None
    d = C.rj(p)
    return {k: float(v["m_s"]) for k, v in d.items() if isinstance(v, dict) and "m_s" in v}


def main(argv=None):
    decl_sha = C.declaration_guard()                 # FIRST: refuse before anything of converted/ is touched
    ap = argparse.ArgumentParser(description="Map on the real energies (DECLARATION.md Secs. 2, 3, 4, 6; gates G1-G7)")
    ap.add_argument("--out", default=C.OUT)
    ap.add_argument("--g1-rerun", action="store_true", help="re-run the project's converter on the pinned archive (gate G1 in full)")
    ap.add_argument("--no-g5-reprove", action="store_true", help="do not re-prove the deciding certificates (G5 reported as skipped)")
    ap.add_argument("--no-g6-tensors", action="store_true", help="do not evaluate stored tensors (G6a reported as skipped)")
    ap.add_argument("--replace-sets", action="store_true", help="overwrite an existing S_sets.json that has another content")
    a = ap.parse_args(argv)
    print("declaration SHA-256 %s: hash file present and matching" % decl_sha, flush=True)
    g1 = MG.g1_data(rerun=a.g1_rerun, scratch=os.path.join(a.out, "g1_rerun") if a.g1_rerun else None)
    print("G1:", {k: v for k, v in g1.items() if k != "files"}, flush=True)
    if not g1["pass"]:
        os.makedirs(a.out, exist_ok=True)
        C.dump_json(os.path.join(a.out, "map_gates.json"), {"G1": g1})
        raise SystemExit("G1 failed: no decision on anything. Nothing else was computed.")
    real = {n: C.load_real(n) for n in C.SIZES}
    stored = MS.Stored()
    loaded = MC.load_certificates()
    print("certificates: %d files, %d distinct by SHA-256, %d used (n = 57: %d, n = 115: %d)" % (
        loaded["n_files"], loaded["n_distinct"], loaded["n_used"], loaded["by_size"][57], loaded["by_size"][115]), flush=True)
    summary = run(real, stored, loaded, decl_sha, a.out, certs_e1=load_e1(loaded["certs"]), n19=load_n19(), g1=g1,
                  g5_reprove=not a.no_g5_reprove, g6_tensors=not a.no_g6_tensors, log=lambda s: print(s, flush=True),
                  replace_sets=a.replace_sets)
    print("gates:", summary["gates"])
    print("written to", a.out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.Refused as ex:                          # say why on stderr; exit code 3
        print("REFUSED: " + ex.msg, file=sys.stderr)
        sys.exit(3)
