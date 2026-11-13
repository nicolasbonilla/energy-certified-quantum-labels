"""Test C3 device job (DECLARATION.md section 5, ADDENDUM_C3.md). From qpu/code/submit_job.py, one job, Jz = 6.0. Run from final_tests/.

  python code_c3/submit_c3.py account     balance and plan, read-only
  python code_c3/submit_c3.py prepare     backend rule, layout on the current calibration, circuits, ISA checks, equivalence
  python code_c3/submit_c3.py submit      re-reads the account immediately before submitting; writes the job id
  python code_c3/submit_c3.py poll        status (exit 0 when final, 3 otherwise)
  python code_c3/submit_c3.py fetch       result -> configurations (npz), device checks, usage

Never reads or prints the token or the account file; QiskitRuntimeService() only.
"""
import datetime
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qpu_lib as ql  # noqa: E402
import qpu_route as qr  # noqa: E402

ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "jobs", "C")
PRIMARY = "ibm_kingston"
CAP = 150                # max_execution_time and total limit of this run, seconds
CHECK_SHOTS = 10_000
SHOTS = 40_000
JZ = 6.0
DT = 0.0681              # published table, method/code/fr.py DT[57][6.0]
ql.DT57[JZ] = DT


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def wjson(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=str)
    os.replace(p + ".tmp", p)


def rjson(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def tag(s):
    return hashlib.sha256(str(s).encode()).hexdigest()[:10] if s else None


def service():
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService()


def account(svc):
    insts = svc.instances()
    u = svc.usage()
    row = dict(time=now(), instances=[dict(name=i.get("name"), plan=i.get("plan"), pricing_type=i.get("pricing_type"),
                                           crn_tag=tag(i.get("crn"))) for i in insts],
               consumed_s=u.get("usage_consumed_seconds"), limit_s=u.get("usage_limit_seconds"),
               remaining_s=u.get("usage_remaining_seconds"), period=u.get("usage_period"),
               limit_reached=u.get("usage_limit_reached"))
    row["free_ok"] = bool(len(insts) == 1 and insts[0].get("plan") == "open" and insts[0].get("pricing_type") == "free")
    return row


def snapshot(b, sel):
    props = b.properties()
    t = b.target
    cfg = b.configuration()
    _, twoq = ql.device_graph(t)
    used = sorted(set(qr.routed_layout_list(sel)))
    pairs = sorted(qr.allowed_pairs(ql.graph57(), sel))
    return dict(backend=b.name, time=now(), last_update_date=str(props.last_update_date),
                default_rep_delay_s=cfg.default_rep_delay, processor_type=getattr(b, "processor_type", None),
                readout_error={q: ql._err(t, "measure", (q,)) for q in used},
                twoq_error={"%d-%d" % p: ql.edge_error(t, twoq, *p) for p in pairs}, properties=props.to_dict())


def equivalence(isa_k1, sel):
    from qiskit.quantum_info import SparsePauliOp
    from qiskit_aer import AerSimulator
    g = ql.graph57()
    qc = isa_k1.remove_final_measurements(inplace=False)
    L = sel["layout"]
    N = qc.num_qubits
    for i in range(g["n"]):
        op = SparsePauliOp.from_sparse_list([("Z", [L[i]], 1.0)], num_qubits=N)
        qc.save_expectation_value(op, list(range(N)), label="z%d" % i)
    sim = AerSimulator(method="matrix_product_state")
    data = sim.run(qc, shots=1).result().data()
    z_isa = np.array([float(np.real(data["z%d" % i])) for i in range(g["n"])])
    T = ql.TrotterMPS(g, chi_max=256)
    T.step(JZ, DT)
    z_mps = T.z_expect()
    return dict(max_abs_diff=float(np.max(np.abs(z_isa - z_mps))), ok=bool(np.max(np.abs(z_isa - z_mps)) <= 1e-6))


def choose_backend(svc):
    """ibm_kingston if operational and the layout rule succeeds; else the free backend with the fewest pending jobs where it does."""
    g = ql.graph57()
    log = []

    def attempt(nm):
        b = svc.backend(nm)
        st = b.status()
        if not st.operational:
            log.append(dict(backend=nm, reason="not operational"))
            return None
        props = b.properties()
        fq = list(props.faulty_qubits())
        fe = [tuple(x.qubits) for x in props.faulty_gates() if len(x.qubits) == 2]
        try:
            sel = qr.choose_routed_layout(b.target, g, 5, fq, fe)
        except RuntimeError as e:
            log.append(dict(backend=nm, reason=str(e)))
            return None
        return b, sel, dict(faulty_qubits=fq, faulty_2q=fe, pending_jobs=st.pending_jobs, tried=log)
    r = attempt(PRIMARY)
    if r:
        return r
    others = sorted((x for x in svc.backends(simulator=False, operational=True) if x.name != PRIMARY),
                    key=lambda x: x.status().pending_jobs)
    for b in others:
        r = attempt(b.name)
        if r:
            return r
    raise SystemExit("STOP: no backend qualifies: %s" % log)


def prepare():
    from qiskit import qpy
    if os.path.exists(os.path.join(D, "job_id.txt")):
        raise SystemExit("STOP: job already submitted")
    os.makedirs(D, exist_ok=True)
    svc = service()
    acc = account(svc)
    print({k: acc[k] for k in ("consumed_s", "limit_s", "remaining_s", "free_ok")}, flush=True)
    if not acc["free_ok"]:
        raise SystemExit("STOP: instance is not the free Open plan")
    if acc["remaining_s"] is None or acc["remaining_s"] < CAP:
        raise SystemExit("STOP: remaining %s s < %d s" % (acc["remaining_s"], CAP))
    g = ql.graph57()
    b, sel, binfo = choose_backend(svc)
    print("backend", b.name, "pending", binfo["pending_jobs"], "relax", sel.get("relax"), "score", sel["score_2q_per_step"], flush=True)
    snap = snapshot(b, sel)
    wjson(os.path.join(D, "calibration_snapshot.json"), snap)
    tags, circs, shots = [], [], []
    for t_, s_ in (("neel", ql.neel_sites(g)), ("asym", ql.ASYM_SITES)):
        tags.append(t_)
        circs.append(ql.product_circuit(g, s_, "check_" + t_))
        shots.append(CHECK_SHOTS)
    chk_isa = ql.transpile_isa(circs, b, sel["layout"])
    kr_tags = ["J%.1f_k%d" % (JZ, k) for k in range(1, ql.K + 1)]
    kr_circs = [qr.routed_krylov_circuit(g, JZ, DT, k, sel) for k in range(1, ql.K + 1)]
    kr_isa = ql.transpile_isa(kr_circs, b, qr.routed_layout_list(sel))
    stats = {}
    for t_, c in zip(tags, chk_isa):
        stats[t_] = ql.check_isa(c, g, sel["layout"])
    for t_, c in zip(kr_tags, kr_isa):
        stats[t_] = qr.check_isa_routed(c, g, sel)
        stats[t_].update(cz=int(c.count_ops().get("cz", 0)),
                         cz_depth=int(c.depth(lambda i: i.operation.num_qubits == 2 and i.operation.name != "barrier")))
    isas = list(chk_isa) + list(kr_isa)
    tags += kr_tags
    shots += [SHOTS] * len(kr_tags)
    rep = b.configuration().default_rep_delay
    durs = [float(c.estimate_duration(b.target, unit="s")) for c in isas]
    est = float(sum(s * (rep + du) for s, du in zip(shots, durs)))
    eq = equivalence(kr_isa[0], sel)
    qp = os.path.join(D, "isa.qpy")
    with open(qp, "wb") as f:
        qpy.dump(isas, f)
    prep = dict(job="C", time=now(), account=acc, backend=b.name, backend_info=binfo, sel=sel, Jz=[JZ], dt=DT, tags=tags, shots=shots,
                max_execution_time=CAP, est_qpu_lower_s=est, durations_s=durs, isa_stats=stats, equivalence=eq,
                qpy_sha256=ql.sha256_file(qp), calibration_last_update=snap["last_update_date"],
                calibration_snapshot_sha256=ql.sha256_file(os.path.join(D, "calibration_snapshot.json")))
    wjson(os.path.join(D, "prep.json"), prep)
    print(json.dumps({k: prep[k] for k in ("backend", "max_execution_time", "est_qpu_lower_s", "equivalence", "qpy_sha256",
                                            "calibration_last_update")}, default=str))
    print("layout score/step %.4f relax %s moves/step %d; k=10 cz %s depth %s" % (
        sel["score_2q_per_step"], sel.get("relax"), sel["moves_per_step"], stats[kr_tags[-1]]["cz"], stats[kr_tags[-1]]["cz_depth"]))
    if not eq["ok"]:
        raise SystemExit("STOP: pre-submission equivalence failed (max |dZ| = %.3e)" % eq["max_abs_diff"])
    if est > CAP:
        raise SystemExit("STOP: lower-bound estimate %.1f s exceeds the cap %d s" % (est, CAP))


def submit():
    from qiskit import qpy
    from qiskit_ibm_runtime import SamplerV2
    prep = rjson(os.path.join(D, "prep.json"))
    if os.path.exists(os.path.join(D, "job_id.txt")):
        raise SystemExit("STOP: already submitted")
    if not prep["equivalence"]["ok"]:
        raise SystemExit("STOP: equivalence not ok")
    qp = os.path.join(D, "isa.qpy")
    if ql.sha256_file(qp) != prep["qpy_sha256"]:
        raise SystemExit("STOP: QPY hash differs")
    with open(qp, "rb") as f:
        isas = qpy.load(f)
    svc = service()
    acc = account(svc)
    if not acc["free_ok"]:
        raise SystemExit("STOP: not the free Open plan")
    if acc["remaining_s"] is None or acc["remaining_s"] < CAP:
        raise SystemExit("STOP: remaining %s s < %d s" % (acc["remaining_s"], CAP))
    b = svc.backend(prep["backend"])
    if not b.status().operational:
        raise SystemExit("STOP: backend not operational")
    sampler = SamplerV2(mode=b)
    sampler.options.dynamical_decoupling.enable = True
    sampler.options.twirling.enable_gates = True
    sampler.options.twirling.enable_measure = False
    sampler.options.twirling.num_randomizations = "auto"
    sampler.options.twirling.shots_per_randomization = "auto"
    sampler.options.max_execution_time = CAP
    job_ = sampler.run([(c, None, int(s)) for c, s in zip(isas, prep["shots"])])
    jid = job_.job_id()
    with open(os.path.join(D, "job_id.txt"), "w") as f:
        f.write(jid + "\n")
    rec = dict(job="C", job_id=jid, submitted=now(), backend=b.name, account_before=acc, max_execution_time=CAP,
               total_shots=int(sum(prep["shots"])), n_pubs=len(isas))
    try:
        rec["usage_estimation"] = job_.usage_estimation
    except Exception as e:
        rec["usage_estimation_error"] = str(e)[:200]
    wjson(os.path.join(D, "submit.json"), rec)
    print("submitted", jid, rec.get("usage_estimation"))


def poll():
    jid = open(os.path.join(D, "job_id.txt")).read().strip()
    j = service().job(jid)
    st = j.status()
    st = st if isinstance(st, str) else getattr(st, "name", str(st))
    wjson(os.path.join(D, "status.json"), dict(time=now(), job_id=jid, status=st))
    print(now(), jid, st)
    return 0 if st in ("DONE", "ERROR", "CANCELLED") else 3


def fetch():
    prep = rjson(os.path.join(D, "prep.json"))
    jid = open(os.path.join(D, "job_id.txt")).read().strip()
    svc = service()
    j = svc.job(jid)
    st = j.status()
    st = st if isinstance(st, str) else getattr(st, "name", str(st))
    if st != "DONE":
        raise SystemExit("job status %s" % st)
    res = j.result()
    g = ql.graph57()
    raw = {}
    out = dict(job="C", job_id=jid, fetched=now(), status=st, pubs={})
    for t_, s_, r in zip(prep["tags"], prep["shots"], res):
        ba = r.data.c
        conf = ql.decode_bitarray(ba)
        assert len(conf) == s_, (t_, len(conf), s_)
        ic = ba.get_int_counts()
        u, c = np.unique(conf, return_counts=True)
        assert len(ic) == len(u) and all(ic[int(a)] == int(b_) for a, b_ in zip(u[:50], c[:50]))
        raw[t_] = conf
        raw[t_ + "_unique"] = u
        raw[t_ + "_count"] = c
        pc = np.bitwise_count(u).astype(int)
        out["pubs"][t_] = dict(shots=int(len(conf)), unique=int(len(u)), unique_in_sector=int(np.sum(pc == g["n_down"])),
                               shots_in_sector=int(np.sum(c[pc == g["n_down"]])), metadata=r.metadata)
    np.savez_compressed(os.path.join(D, "raw_configs.npz"), **raw)
    checks = {}
    for t_, s_ in (("neel", ql.neel_sites(g)), ("asym", ql.ASYM_SITES)):
        checks[t_] = ql.check_verdict(raw[t_], ql.config_int(s_), g["n"])
    checks["both_pass"] = bool(checks["neel"]["pass_"] and checks["asym"]["pass_"])
    wjson(os.path.join(D, "checks.json"), checks)
    usage = dict(time=now())
    try:
        usage["quantum_seconds"] = float(j.usage())
    except Exception as e:
        usage["usage_error"] = str(e)[:200]
    usage["account_after"] = account(svc)
    wjson(os.path.join(D, "usage.json"), usage)
    out["result_metadata"] = res.metadata
    wjson(os.path.join(D, "fetch.json"), out)
    print("checks: neel pass %s (min %.4f), asym pass %s (min %.4f); usage %s s; remaining %s" % (
        checks["neel"]["pass_"], checks["neel"]["min_site_agreement"], checks["asym"]["pass_"],
        checks["asym"]["min_site_agreement"], usage.get("quantum_seconds"), usage["account_after"]["remaining_s"]))


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "account":
        a = account(service())
        print({k: a[k] for k in ("consumed_s", "limit_s", "remaining_s", "free_ok", "period")})
    elif m == "prepare":
        prepare()
    elif m == "submit":
        submit()
    elif m == "poll":
        sys.exit(poll())
    elif m == "fetch":
        fetch()
    else:
        raise SystemExit("mode?")
