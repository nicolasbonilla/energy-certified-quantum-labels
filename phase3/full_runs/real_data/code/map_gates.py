# real_data / map_gates.py  (own code; 2026-11-12; task rd-code-map)
#
# The gates G1-G7 of DECLARATION.md Sec. 8 as functions. Each returns a JSON-ready dict with 'gate', 'pass' and the
# numbers behind it. A failure means "no decision" for what depends on it (apply_no_decision marks the rows).
#   G1 data            hashes of converted/ against converted/SHA256SUMS.txt and the declaration; with rerun=True the
#                      project's own converter is run again on the pinned archive (a separate process, scratch output).
#   G2 same state      exchange part E - (Jz/4) sum_e <ZZ>_e inside [-B, B].
#   G3 energies        E_real >= E0(authors).
#   G4 truth           authors' DMRG against this project's references at the stored couplings.
#   G5 certificates    every certificate used has a recorded exact verification (enforced by the loader); the deciding
#                      certificates are re-proved with the independent verifier of the review (separate process).
#   G6 re-evaluation   linear rule against the stored tensors with the independent evaluator, where tensors are stored;
#                      every re-evaluated in-sector energy at least E0(Jz) - 1e-6.
#   G7 filter          every CERTIFIED (exact) label and its truth inside its interval.
import math
import os
import random
import subprocess
import sys

import map_common as C


# ------------------------------------------------------------------------------------------------ G1
def _read_sums(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2 and C.HEX64.fullmatch(p[0]):
                out[p[-1].lstrip("*")] = p[0].lower()
    return out


def g1_data(rd=None, rerun=False, scratch=None, python=None, pinned=None, archive=None):
    """rerun=False checks the hashes only ('complete' is then False: the gate as declared needs the re-run)."""
    rd = rd or C.RD
    pinned = C.PINNED if pinned is None else pinned
    C.declaration_guard(rd)
    sums = _read_sums(os.path.join(rd, "converted", "SHA256SUMS.txt"))
    rows = []
    for name, pin in sorted(pinned.items()):
        h = C.sha256_file(os.path.join(rd, "converted", name))
        rows.append(dict(file=name, sha256=h, equals_sums=bool(sums.get(name) == h), equals_declaration=bool(h == pin)))
    ok = all(r["equals_sums"] and r["equals_declaration"] for r in rows) and set(sums) == set(pinned)
    res = dict(gate="G1", files=rows, hashes_ok=bool(ok), rerun=None, complete=False)
    if rerun:
        rel, tar_sha = archive or C.PINNED_ARCHIVE
        tar = os.path.join(rd, *rel.split("/"))
        if scratch is None or (os.path.exists(scratch) and os.listdir(scratch)):
            raise ValueError("G1 re-run needs a new, empty scratch folder")
        if C.sha256_file(tar) != tar_sha:
            res["rerun"] = dict(ok=False, reason="the archive does not have the pinned SHA-256")
        else:
            os.makedirs(scratch, exist_ok=True)
            p = subprocess.run([python or sys.executable, "-B", "-I", os.path.join(rd, "code", "convert_real_data.py"), tar, scratch],
                               capture_output=True, text=True, timeout=1800)
            new = _read_sums(os.path.join(scratch, "SHA256SUMS.txt")) if p.returncode == 0 else {}
            res["rerun"] = dict(ok=bool(p.returncode == 0 and new == sums), returncode=p.returncode, sums=new,
                                stderr_tail=p.stderr[-500:])
        res["complete"] = True
    res["pass"] = bool(ok and (res["rerun"]["ok"] if rerun else True))
    return res


# ------------------------------------------------------------------------------------------------ G2, G3
def g2_point(rec, G, energy="E_real"):
    """Necessary condition for the energy and the labels to belong to one state: on an edge
    |<XX + YY>|/4 <= sqrt(p_01 p_10) = (1/2) sqrt(((1 - <ZZ>)/2)^2 - ((<Z_i> - <Z_j>)/2)^2)."""
    ce, z = rec["families"]["edges"], rec["z"]
    exch = rec[energy] - float(rec["Jz"]) / 4.0 * math.fsum(ce)
    B, nneg = 0.0, 0
    for (i, j), c in zip(G["edges"], ce):
        rad = ((1.0 - c) / 2.0) ** 2 - ((z[i] - z[j]) / 2.0) ** 2
        if rad < 0:
            nneg, rad = nneg + 1, 0.0
        B += 0.5 * math.sqrt(rad)
    return dict(exchange=exch, B=B, ratio=(exch / B) if B > 0 else None, ok=bool(-B <= exch <= B),
                n_negative_radicand=nneg)


def g2_same_state(real, group="dataset", energy="E_real"):
    rows = []
    for key, rec in sorted(real[group].items(), key=lambda kv: float(kv[0])):
        if rec["has_labels"]:
            rows.append(dict(n=real["n"], Jz=float(rec["Jz"]), key=key, **g2_point(rec, real["G"], energy)))
    return dict(gate="G2", n=real["n"], group=group, energy=energy, rows=rows, failed=[r["key"] for r in rows if not r["ok"]],
                **{"pass": bool(rows) and all(r["ok"] for r in rows)})


def g3_energies(real, group="dataset"):
    rows = []
    for key, rec in sorted(real[group].items(), key=lambda kv: float(kv[0])):
        d = real["dmrg"].get(key)
        if d is not None:
            rows.append(dict(n=real["n"], Jz=float(rec["Jz"]), key=key, E_real_minus_E0_authors=rec["E_real"] - d["E0"],
                             ok=bool(rec["E_real"] >= d["E0"])))
    return dict(gate="G3", n=real["n"], group=group, rows=rows, failed=[r["key"] for r in rows if not r["ok"]],
                **{"pass": bool(rows) and all(r["ok"] for r in rows)})


# ------------------------------------------------------------------------------------------------ G4
def g4_truth(stored, real, tol_O=1e-3, tol_E=1e-4):
    """|dO| <= 1e-3 tau for the seven label types and |dE0| <= 1e-4 at the couplings of this project's references."""
    n, rows, erows = real["n"], [], []
    for (nn, key), t in sorted(stored.refs.items(), key=lambda kv: (kv[0][0], float(kv[0][1]))):
        if nn != n or key not in real["dmrg"]:
            continue
        d, J = real["dmrg"][key], C.jfr(key)
        dE = d["E0"] - float(t["E0"])
        erows.append(dict(Jz=float(J), dE0=dE, ok=bool(abs(dE) <= tol_E)))
        for label in C.LABELS:
            o = stored.O_GS(n, J, label)
            if o is None:
                continue
            tau = C.TAU_FRAC * abs(o)
            dO = d["labels"][label] - o
            rows.append(dict(Jz=float(J), label=label, dO=dO, dO_over_tau=(dO / tau) if tau > 0 else None,
                             ok=bool(abs(dO) <= tol_O * tau)))
    worst = {lab: max((abs(r["dO_over_tau"]) for r in rows if r["label"] == lab and r["dO_over_tau"] is not None), default=None)
             for lab in C.LABELS}
    ok = bool(rows) and all(r["ok"] for r in rows) and all(r["ok"] for r in erows)
    return dict(gate="G4", n=n, n_label_rows=len(rows), n_energy_rows=len(erows), max_abs_dO_over_tau=worst,
                max_abs_dE0=max((abs(r["dE0"]) for r in erows), default=None),
                failed=[r for r in rows if not r["ok"]] + [r for r in erows if not r["ok"]], **{"pass": ok})


# ------------------------------------------------------------------------------------------------ G5
def g5_records(loaded, used_idents=None):
    """Every certificate the pipeline can use went through map_certs.read_cert: verification record present, ok,
    same file hash, same task, same exact bound. Heavy-hex certificates that fail this are excluded and listed."""
    bad = [(p, why) for p, why in loaded["excluded"] if "not one of the heavy-hex graphs" not in why]
    return dict(gate="G5a", n_files=loaded["n_files"], n_distinct=loaded["n_distinct"], n_used=loaded["n_used"],
                by_size={str(k): v for k, v in loaded["by_size"].items()}, excluded_for_a_missing_or_bad_record=bad,
                n_deciding=None if used_idents is None else len(used_idents), **{"pass": True})


def deciding_rows(ix, n, label, which="certified", source="exact"):
    """Rows whose certificates decide J*_exact and the boundary of the filter: both rows of every pair of neighbouring
    training couplings whose CERTIFIED (exact) flags differ."""
    tr = [ix[(n, C.jkey(J), label)] for J in C.TRAIN_J if (n, C.jkey(J), label) in ix]
    flag = lambda r: bool(r.get(source) and r[source].get(which))
    out = []
    for a, b in zip(tr[:-1], tr[1:]):
        if flag(a) != flag(b):
            out += [a, b]
    return out


def deciding_certificates(ix):
    """{sha256: ident} of the certificates behind the intervals of the deciding rows (both labels, both tolerances;
    the stored certificates and, where the separate E1 column exists, that column too)."""
    out = {}
    for n in C.SIZES:
        for label in C.EXACT_LABELS:
            for which in ("certified", "certified_rf"):
                for source in ("exact", "exact_e1"):
                    for r in deciding_rows(ix, n, label, which, source):
                        if r.get(source) and r[source].get("exists"):
                            for c in r[source]["certificates"]:
                                out[c["sha256"]] = c
    return out


def g5_reprove(idents, out_dir, methods="chol", python=None, timeout=7200):
    """Re-proves certificates with the independent verifier scratch/math-rigorous-bounds/myverify.py (operator
    identity and positivity of every block in exact arithmetic), one separate process each."""
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for c in idents:
        path = c["path"]
        d = C.rj(path)
        gpath = os.path.join(C.MAP_CODE, "graphs", d["graph"])
        out = os.path.join(out_dir, c["name"] + "_myver.json")
        r = dict(name=c["name"], sha256=c["sha256"], ok=False)
        if C.sha256_file(gpath) != d["graph_sha256"]:
            r["reason"] = "graph file differs from the certificate's"
        else:
            p = subprocess.run([python or sys.executable, "-B", C.MYVERIFY, gpath, path, out, "--methods", methods],
                               capture_output=True, text=True, timeout=timeout)
            if p.returncode != 0 or not os.path.exists(out):
                r["reason"] = "verifier failed: " + p.stderr[-300:]
            else:
                v = C.rj(out)
                r.update(identity_holds=v.get("identity_holds"), all_cluster_inequalities_proved=v.get("all_cluster_inequalities_proved"),
                         E_matches_cert_claim=v.get("E_matches_cert_claim"), E_LB_exact=v.get("E_LB_exact"), time_s=v.get("time_s"))
                r["ok"] = bool(v.get("identity_holds") is True and v.get("all_cluster_inequalities_proved") is True
                               and v.get("E_matches_cert_claim") is True and v.get("cert_sha256") == c["sha256"])
        rows.append(r)
    return dict(gate="G5b", verifier=C.MYVERIFY, verifier_sha256=C.sha256_file(C.MYVERIFY), methods=methods, rows=rows,
                **{"pass": all(r["ok"] for r in rows)})


# ------------------------------------------------------------------------------------------------ G6
def g6_select(rows, jstars, seed, n_other=10):
    """Rows of gate G6: every NOT CERTIFIED row within 0.3 of a J* of its label and size (jstars: {(n, label): [J*,
    ...]}, every rule), and n_other further NOT CERTIFIED rows drawn with the seed."""
    nc = sorted((r for r in rows if r["status"] == "NOT_CERTIFIED"), key=lambda r: (r["n"], r["Jz"], C.LABELS.index(r["label"])))
    near = [r for r in nc if any(js is not None and abs(r["Jz"] - js) <= 0.3 + 1e-9 for js in jstars.get((r["n"], r["label"]), []))]
    ids = set(id(r) for r in near)
    rest = [r for r in nc if id(r) not in ids]
    other = random.Random(seed).sample(rest, min(n_other, len(rest)))
    return near, other


def g6_components(row):
    """Stored states behind the witnesses of a NOT CERTIFIED row: the components of the two hull extremes (up to two
    each) and the reference state of the neighbouring sector when q is not zero."""
    lw = row.get("lower") or {}
    sids = [c[0] for side in ("min", "max") for c in (lw.get("components") or {}).get(side, [])]
    if lw.get("ref"):
        sids.append(lw["ref"]["sid"])
    return sorted(set(sids))


def g6_linear(stored, rows, npz_root=None, tol=1e-8, evaluator=None):
    """For every component: energy at the row's coupling from the stored tensors with the independent evaluator
    (map/laptop_analysis/code/indep_eval.py) against the linear rule. Components whose tensors are not stored on this
    machine cannot be checked and are counted; 'complete' is True only if none is missing."""
    npz_root = npz_root or os.path.join(C.MAPRUN, "npz_20261030T022613Z")
    checked, missing, cache = [], [], {}
    for row in rows:
        n, J = row["n"], row["Jz"]
        for sid in g6_components(row):
            stt = stored.D.states[sid]
            E_lin = stt["tenpy"]["E"] + (J - stt["Jz"]) * stored.slope(sid)
            path = os.path.join(npz_root, *stt["npz"].split("/"))
            if not os.path.exists(path):
                missing.append(dict(n=n, Jz=J, label=row["label"], sid=sid))
                continue
            if (sid, J) not in cache:
                if evaluator is None:
                    if C.MAP_CODE not in sys.path:
                        sys.path.append(C.MAP_CODE)
                    import indep_eval as IE          # stored code (numpy + json only), imported, not changed
                    Ts, meta = IE.load_npz(path)
                    G = C.graph(n)["raw"]
                    assert meta["n"] == G["n"] and meta["order"] == G["order"]
                    cache[(sid, J)] = IE.evaluate(Ts, G, float(J), meta["sz_basis"], s=None, full=True)["E"]
                else:
                    cache[(sid, J)] = evaluator(path, n, float(J))
            dE = abs(cache[(sid, J)] - E_lin)
            checked.append(dict(n=n, Jz=J, label=row["label"], sid=sid, Jg=stt["Jz"], E_tensors=cache[(sid, J)], E_linear=E_lin,
                                dE=dE, ok=bool(dE <= tol)))
    return dict(gate="G6a", n_rows=len(rows), n_checked=len(checked), n_missing_tensors=len(missing), checked=checked,
                missing=missing, max_dE=max((c["dE"] for c in checked), default=None),
                complete=bool(not missing), **{"pass": all(c["ok"] for c in checked)})


def g6_energies(rows, tol=1e-6):
    """Every re-evaluated in-sector energy is at least E0(Jz) - 1e-6 (smallest pool energy of each row)."""
    out = []
    for r in rows:
        lw = r.get("lower") or {}
        if lw.get("min_pool_E") is not None and (lw.get("pool") or {}).get("kind") == "re-evaluated":
            d = lw["min_pool_E"] - r["E0"]
            out.append(dict(n=r["n"], Jz=r["Jz"], label=r["label"], min_minus_E0=d, ok=bool(d >= -tol)))
    return dict(gate="G6b", n_rows=len(out), min_over_rows=min((x["min_minus_E0"] for x in out), default=None),
                failed=[x for x in out if not x["ok"]], **{"pass": all(x["ok"] for x in out)})


# ------------------------------------------------------------------------------------------------ G7
def g7_filter(rows):
    """Every CERTIFIED (exact) label (either tolerance) and its truth lie inside its interval. A violation is an
    inconsistency of an input. Also counted, for information: rows with an interval of any width."""
    viol, n_cert, n_iv, n_iv_out = [], 0, 0, 0
    for r in rows:
        ex = r.get("exact")
        if not (ex and ex.get("exists")):
            continue
        n_iv += 1
        inside = bool(ex.get("label_inside") and ex.get("truth_inside") and not ex.get("empty"))
        n_iv_out += not inside
        if ex.get("certified") or ex.get("certified_rf"):
            n_cert += 1
            if not inside:
                viol.append(dict(n=r["n"], Jz=r["Jz"], label=r["label"], label_inside=ex.get("label_inside"),
                                 truth_inside=ex.get("truth_inside"), empty=ex.get("empty")))
    return dict(gate="G7", n_certified_rows=n_cert, violations=viol, n_rows_with_an_interval=n_iv,
                n_intervals_not_containing_label_and_truth=n_iv_out, **{"pass": not viol})


# ------------------------------------------------------------------------------------------------ consequences
def apply_no_decision(rows, g2=None, g3=None, g4=None):
    """Sec. 8: 'a failure means no decision for what depends on it'. Rows at a coupling where G2 or G3 fails, and every
    row of a size where G4 fails, get no_decision = [reasons] and the status NO_DECISION (statuses kept as *_raw)."""
    bad = {}
    for g, tag in ((g2, "G2"), (g3, "G3")):
        if g is not None:
            for key in g["failed"]:
                bad.setdefault((g["n"], key), []).append(tag)
    n_bad = 0
    for r in rows:
        why = list(bad.get((r["n"], r["key"]), []))
        if g4 is not None and g4["n"] == r["n"] and not g4["pass"]:
            why.append("G4")
        r["no_decision"] = why
        if why:
            n_bad += 1
            for k in ("status", "status_rf", "status_e1", "status_e1_rf"):
                if k in r:
                    r[k + "_raw"], r[k] = r[k], "NO_DECISION"
            r["like"]["status_raw"], r["like"]["status"] = r["like"]["status"], "NA_s"
            for k in ("exact", "exact_e1"):
                if r.get(k):
                    r[k]["certified_raw"], r[k]["certified_rf_raw"] = r[k].get("certified"), r[k].get("certified_rf")
                    r[k]["certified"] = r[k]["certified_rf"] = False
    return n_bad
