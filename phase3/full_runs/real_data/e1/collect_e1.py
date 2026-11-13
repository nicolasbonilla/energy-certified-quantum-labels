"""collect_e1.py: merges the finished, exactly verified E1 certificates into the separate E1 column of the map.
The rule of real_data/DECLARATION.md Sec. 2 is not re-implemented here: the column is computed by the declared map
code (real_data/code/run_map.py, unchanged), which reads E1 certificates from real_data/e1/ (clarification 17).

Steps
 1. real_data/DECLARATION.md must match DECLARATION.sha256 (else: refuse).
 2. Every certificate of e1/out/jobs/ is accepted only if ALL of this holds (exact arithmetic, standard library):
      - it is an E1 task: label m_s, one of the five (n, Jz) of E1, a field of the declared grid (grid_e1.json),
        vertex or edge balls of radius 2, the stored optimizer settings, the stored graph file;
      - sum_k t_k - mu M_0 equals its claimed bound;
      - the record of the stored verifier (verify_exact.py, <id>_verify_exact.json) is ok, is for this very file
        (SHA-256), for this task, and gives the same exact bound;
      - the record of the independent exact verifier (myverify.py, <id>_myver.json) proves every cluster
        inequality and the operator identity, for this very file, with the same exact bound. If that record is
        missing it is produced now (about 20 s for vertex balls, about 1 min for edge balls).
    A certificate that fails any check is listed with the reason and is not collected.
 3. Accepted certificates are copied to e1/certs/ as <id>_cert.json + <id>_ver.json (the stored names and format;
    the second file is the record of the stored verifier, byte for byte) + <id>_myver.json; a manifest
    e1/certs/E1_CERTS.json and SHA256SUMS.txt are written. Files of an earlier collection that are no longer
    accepted are removed from e1/certs/.
 4. The declared map code is run with a SEPARATE output folder: python -B -I real_data/code/run_map.py --out
    e1/map_e1. Its E1 column (fields exact_e1, status_e1, status_e1_rf of map_rows.json; sec2_e1 of the J* table;
    secondary_E1 of S_sets.json) is printed. real_data/out/ is not touched.

usage: python -B -I collect_e1.py [--partial] [--no-map] [--dry]
   --partial  collect although STATUS.json does not say "finished" (every collected certificate is a theorem
              anyway; the column is then not the final one)
   --no-map   stop after step 3
   --dry      steps 1-2 only: list what would be collected, write nothing
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from fractions import Fraction

E1 = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(E1)
CODE = os.path.join(E1, "code")
JOBS = os.path.join(E1, "out", "jobs")
CERTS = os.path.join(E1, "certs")
MAPOUT = os.path.join(E1, "map_e1")
M0 = {57: 9, 115: 19}
GRAPH_N = {"hh_d5.json": 57, "hh_d7.json": 115}
E1_COUPLINGS = {(57, Fraction(33, 10)), (57, Fraction(32, 10)), (115, Fraction(5)), (115, Fraction(36, 10)), (115, Fraction(33, 10))}
SETTINGS = dict(K=32, maxiter=600, betas=[30, 300, 3000, 30000, 100000], use_mu=True)
SUFFIXES = ("_cert.json", "_ver.json", "_myver.json")


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rj(p):
    try:
        return json.load(open(p))
    except Exception:
        return None


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def allowed_fields():
    """(n, Jz, sigma) -> fields of the declared grid that the plan keeps (not pruned)."""
    out = {}
    for g in json.load(open(os.path.join(E1, "grid_e1.json"))):
        for s in "+-":
            sd = g["sides"][s]
            out[(g["n"], Fraction(repr(g["Jz"])), sd["sigma"])] = set(Fraction(q["lam"]) for q in sd["pts"] if not q["pruned"])
    return out


def run_myverify(jid, level):
    g = os.path.join(CODE, "graphs", json.load(open(os.path.join(JOBS, jid + "_cert.json")))["graph"])
    out = os.path.join(JOBS, jid + "_myver.json")
    cmd = [sys.executable, "-B", "myverify.py", g, os.path.join(JOBS, jid + "_cert.json"), out + ".part"]
    if level != "vball2":
        cmd += ["--methods", "chol"]
    with open(os.path.join(JOBS, jid + "_myver.log"), "w") as f:
        subprocess.call(cmd, cwd=CODE, stdout=f, stderr=subprocess.STDOUT)
    if os.path.exists(out + ".part"):
        os.replace(out + ".part", out)


def check(jid, allowed, dry):
    """dict of the accepted certificate; raises AssertionError with the reason otherwise."""
    cf = os.path.join(JOBS, jid + "_cert.json")
    raw = open(cf, "rb").read()
    csha = hashlib.sha256(raw).hexdigest()
    d = json.loads(raw)
    n = GRAPH_N.get(d.get("graph"))
    assert n is not None, "graph %r is not hh_d5 or hh_d7" % d.get("graph")
    assert d["graph_sha256"] == sha_file(os.path.join(CODE, "graphs", d["graph"])), "graph hash differs"
    task = d["task"]
    assert task["kind"] == "m_s", "label is not m_s"
    J, sigma, lam = Fraction(str(task["Jz"])), int(task["sigma"]), Fraction(str(task["lam"]))
    assert (n, J) in E1_COUPLINGS, "not one of the five E1 rows"
    assert sigma in (1, -1) and lam in allowed.get((n, J, sigma), ()), "field is not a kept point of the declared grid"
    level = task["clusters"]
    assert level in ("vball2", "eball2"), "cluster family %r" % level
    for k, v in SETTINGS.items():
        assert task.get(k) == v, "optimizer setting %s differs from the stored one" % k
    assert isinstance(d["K"], int) and isinstance(d["mu"], int) and all(isinstance(t, int) for t in d["t"]), "non-integer data"
    den = 2 ** d["K"]
    c, mu, E = sum(Fraction(t, den) for t in d["t"]), Fraction(d["mu"], den), Fraction(d["E_claim"])
    assert c - mu * M0[n] == E, "sum_k t_k - mu M_0 differs from the claimed bound"
    v = rj(os.path.join(JOBS, jid + "_verify_exact.json"))
    assert v is not None, "no record of the stored verifier"
    assert v.get("ok") is True, "stored verifier: not ok"
    assert v.get("cert_sha256") == csha, "record of the stored verifier is for another file"
    assert v.get("task") == task and Fraction(v["E_LB_exact"]) == E and int(v.get("twoS", -1)) == M0[n], \
        "record of the stored verifier disagrees with the certificate"
    if rj(os.path.join(JOBS, jid + "_myver.json")) is None and not dry:
        run_myverify(jid, level)
    m = rj(os.path.join(JOBS, jid + "_myver.json"))
    assert m is not None, "no record of the independent verifier" + (" (not produced in a dry run)" if dry else "")
    assert m.get("all_cluster_inequalities_proved") is True, "independent verifier: a cluster inequality is not proved"
    assert m.get("identity_holds") is True, "independent verifier: operator identity not shown"
    assert m.get("E_matches_cert_claim") is True and Fraction(m["E_LB_exact"]) == E, "independent verifier: other bound"
    assert m.get("cert_sha256") == csha, "record of the independent verifier is for another file"
    return dict(id=jid, n=n, Jz=str(J), sigma=sigma, lam=str(lam), lam_float=float(lam), level=level, cert_sha256=csha,
                E_LB_exact=str(E), E_LB_float=float(E), mu_exact=str(mu), mu_float=float(mu), c_exact=str(c),
                verified_by=["verify_exact.py (stored verifier, exact integers)",
                             "myverify.py (independent, exact; methods %s)" % ",".join(m.get("methods", []))],
                verify_exact_sha256=sha_file(os.path.join(JOBS, jid + "_verify_exact.json")),
                myver_sha256=sha_file(os.path.join(JOBS, jid + "_myver.json")))


def steering_table(acc):
    """Per row: best bound per side in the in-sector form at E_real + 1e-6 (what steered the search; exact rationals
    of the dyadic inputs). The declared E1 column (energy and mean magnetization) comes from run_map.py."""
    L = []
    for g in sorted(json.load(open(os.path.join(E1, "grid_e1.json"))), key=lambda g: g["prio"]):
        n, J, S, E, tau = g["n"], Fraction(repr(g["Jz"])), g["n"], Fraction(g["E_up"]), Fraction(g["tau"])
        best = {}
        for a in acc:
            if a["n"] == n and Fraction(a["Jz"]) == J:
                u = (E - Fraction(a["E_LB_exact"])) / (Fraction(a["lam"]) * S)
                if a["sigma"] not in best or u < best[a["sigma"]][0]:
                    best[a["sigma"]] = (u, a)
        cnt = sum(1 for a in acc if a["n"] == n and Fraction(a["Jz"]) == J)
        if 1 in best and -1 in best:
            w = best[1][0] + best[-1][0]
            L.append("  n = %3d  Jz = %.1f: %2d certificates; in-sector interval at E_real + 1e-6: [%.5f, %.5f], width %.4f tau "
                     "(%s tau); best '+' %s (%s), best '-' %s (%s)" % (
                         n, float(J), cnt, float(-best[-1][0]), float(best[1][0]), float(w / tau),
                         "within" if w <= tau else "WIDER than", best[1][1]["id"], best[1][1]["level"], best[-1][1]["id"],
                         best[-1][1]["level"]))
        else:
            L.append("  n = %3d  Jz = %.1f: %2d certificates; sides with a certificate: %s -> no interval yet" % (
                n, float(J), cnt, ", ".join("+" if s == 1 else "-" for s in sorted(best, reverse=True)) or "none"))
    return L


def main():
    ap = argparse.ArgumentParser(description="Collect the verified E1 certificates and compute the E1 column of the map")
    ap.add_argument("--partial", action="store_true")
    ap.add_argument("--no-map", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    decl = sha_file(os.path.join(RD, "DECLARATION.md"))
    if decl != open(os.path.join(RD, "DECLARATION.sha256")).read().split()[0]:
        raise SystemExit("REFUSED: DECLARATION.md does not match DECLARATION.sha256")
    st = rj(os.path.join(E1, "STATUS.json")) or {}
    print("STATUS.json: finished = %s, stop reason = %s, updated %s, elapsed %s h" % (
        st.get("finished"), st.get("stop_reason"), st.get("updated_utc"), st.get("elapsed_hours")))
    if not st.get("finished") and not (a.partial or a.dry):
        raise SystemExit("E1 has not finished. Wait, or pass --partial (the column is then not the final one).")
    allowed = allowed_fields()
    acc, rej = [], []
    for cf in sorted(glob.glob(os.path.join(JOBS, "*_cert.json"))):
        jid = os.path.basename(cf)[:-len("_cert.json")]
        try:
            acc.append(check(jid, allowed, a.dry))
        except AssertionError as ex:
            rej.append(dict(id=jid, reason=str(ex)))
        except Exception as ex:                       # unreadable or half-written file
            rej.append(dict(id=jid, reason="unreadable: %r" % ex))
    print("certificates in out/jobs: %d; accepted (stored verifier AND independent verifier): %d; not accepted: %d" % (
        len(acc) + len(rej), len(acc), len(rej)))
    for r in rej:
        print("  NOT ACCEPTED %s: %s" % (r["id"], r["reason"]))
    table = steering_table(acc)
    print("Search summary (in-sector form; NOT the declared E1 column):")
    print("\n".join(table))
    couplings = sorted(set((x["n"], x["Jz"]) for x in acc))
    print("couplings with at least one accepted certificate:", ", ".join("n=%d Jz=%.1f" % (n, float(Fraction(J))) for n, J in couplings) or "none")
    if a.dry:
        print("dry run: nothing written")
        return 0
    os.makedirs(CERTS, exist_ok=True)
    keep = set()
    for x in acc:
        for src, dst in (("_cert.json", "_cert.json"), ("_verify_exact.json", "_ver.json"), ("_myver.json", "_myver.json")):
            shutil.copyfile(os.path.join(JOBS, x["id"] + src), os.path.join(CERTS, x["id"] + dst))
            keep.add(x["id"] + dst)
        assert sha_file(os.path.join(CERTS, x["id"] + "_cert.json")) == x["cert_sha256"]
    for f in os.listdir(CERTS):                        # plain files of an earlier collection that are no longer accepted
        if f.endswith(SUFFIXES) and f not in keep:
            os.remove(os.path.join(CERTS, f))
    man = dict(schema="p5-e1-certs-v1", collected_utc=utc(), declaration_sha256=decl, e1_spec_sha256=sha_file(os.path.join(E1, "E1_SPEC.md")),
               status_finished=bool(st.get("finished")), status_stop_reason=st.get("stop_reason"), n_accepted=len(acc),
               couplings=["n=%d Jz=%.1f" % (n, float(Fraction(J))) for n, J in couplings], accepted=acc, not_accepted=rej,
               search_summary_in_sector_form=table)
    json.dump(man, open(os.path.join(CERTS, "E1_CERTS.json"), "w"), indent=1)
    with open(os.path.join(CERTS, "SHA256SUMS.txt"), "w", newline="\n") as f:
        for name in sorted(keep) + ["E1_CERTS.json"]:
            f.write("%s  %s\n" % (sha_file(os.path.join(CERTS, name)), name))
    print("copied %d certificates to %s (manifest E1_CERTS.json, SHA256SUMS.txt)" % (len(acc), CERTS))
    if a.no_map or not acc:
        print("map not run (%s)" % ("--no-map" if a.no_map else "no accepted certificate"))
        return 0
    os.makedirs(MAPOUT, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2")
    print("running the declared map code with the E1 column: run_map.py --out %s (a few minutes) ..." % MAPOUT, flush=True)
    r = subprocess.run([sys.executable, "-B", "-I", os.path.join(RD, "code", "run_map.py"), "--out", MAPOUT, "--replace-sets"],
                       cwd=os.path.join(RD, "code"), env=env, capture_output=True, text=True)
    open(os.path.join(MAPOUT, "run_map_stdout.txt"), "w").write("start of collection %s\n%s\nexit code %d\n" % (man["collected_utc"], r.stdout, r.returncode))
    open(os.path.join(MAPOUT, "run_map_stderr.txt"), "w").write(r.stderr)
    print(r.stdout[-3000:])
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit("run_map.py ended with code %d: no E1 column. See %s" % (r.returncode, MAPOUT))
    try:
        rows = json.load(open(os.path.join(MAPOUT, "map_rows.json")))["rows"]
        summ = json.load(open(os.path.join(MAPOUT, "map_summary.json")))
        print("E1 certificates used by the map code: %s" % summ.get("certificates_E1"))
        print("E1 column, m_s, dataset rows where it differs from the column of the stored certificates:")
        for x in rows:
            if x.get("label") != "m_s" or x.get("group") != "dataset":
                continue
            e0, e1 = x.get("exact") or {}, x.get("exact_e1") or {}
            if not e1.get("exists") or (e0.get("exists") and e0.get("width_exact") == e1.get("width_exact")):
                continue
            print("  n = %3d  Jz = %s%s: stored: %s | with E1: [%.5f, %.5f], width %.4f tau (reference-free %.4f), status %s / %s" % (
                x["n"], x["key"], "" if x.get("training") else " (not a training coupling)",
                ("width %.4f tau, %s" % (e0["width_over_tau"], x.get("status"))) if e0.get("exists") else "no interval",
                e1["lo"], e1["hi"], e1["width_over_tau"], e1.get("width_over_tau_rf") or float("nan"), x.get("status_e1"), x.get("status_e1_rf")))
        for n in (57, 115):
            j = summ["jstar"]["%d_m_s" % n]
            print("  J*_exact, n = %d: stored certificates %s (reference-free %s); with E1 %s (reference-free %s)" % (
                n, j["sec2"].get("J_star_exact"), j["sec2_rf"].get("J_star_exact"),
                (j.get("sec2_e1") or {}).get("J_star_exact"), (j.get("sec2_e1_rf") or {}).get("J_star_exact")))
        print("gates:", summ.get("gates"))
    except Exception as ex:
        print("the map ran; the short table could not be printed (%r). Read %s/map_rows.json and map_summary.json." % (ex, MAPOUT))
    print("E1 column written to %s (real_data/out/ was not touched)" % MAPOUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
