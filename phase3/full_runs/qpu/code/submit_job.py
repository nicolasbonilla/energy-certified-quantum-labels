"""Device jobs of DECLARATION.md §3-§5: preparation, submission, polling, fetch. Run from full_runs/qpu/.

  python code/submit_job.py prepare A|B     account check, backend, layout rule on the current calibration
                                            (snapshot saved), circuits, ISA checks, pre-submission equivalence
                                            (Aer MPS of the k = 1 ISA circuit vs TrotterMPS), QPY + SHA-256
  python code/submit_job.py submit  A|B     re-reads the account IMMEDIATELY before submitting (plan open / free,
                                            remaining >= max_execution_time + 120 s), submits, writes the job id
  python code/submit_job.py poll    A|B     status (exit 0 when final, 3 otherwise)
  python code/submit_job.py fetch   A|B     result -> decoded configurations (npz), device checks, usage

Bit order: conventions C1-C7 of qpu_lib.py (site i = virtual qubit i = clbit i; measured 1 = down; little-endian
integer = emu2 configuration). Never reads or prints the token or the account file; QiskitRuntimeService() only.
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
JOBS = os.path.join(ROOT, "jobs")
PRIMARY, FALLBACK = "ibm_kingston", "ibm_fez"
CAP_TOTAL = 480
MARGIN = 120
CHECK_SHOTS = 10_000
SHOTS_A = 100_000
CAP_A = 380


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
                twoq_error={"%d-%d" % p: ql.edge_error(t, twoq, *p) for p in pairs},
                properties=props.to_dict())


def equivalence(isa_k1, sel, Jz, dt):
    """Aer MPS <Z> at the 57 homes of the k = 1 ISA circuit vs TrotterMPS k = 1 (DECLARATION §4)."""
    from qiskit.quantum_info import SparsePauliOp
    from qiskit_aer import AerSimulator
    g = ql.graph57()
    qc = isa_k1.remove_final_measurements(inplace=False)
    L = sel["layout"]
    N = qc.num_qubits
    for i in range(g["n"]):     # full-width operator (the subset-qubit form returned wrong values in Aer MPS here)
        op = SparsePauliOp.from_sparse_list([("Z", [L[i]], 1.0)], num_qubits=N)
        qc.save_expectation_value(op, list(range(N)), label="z%d" % i)
    sim = AerSimulator(method="matrix_product_state")
    data = sim.run(qc, shots=1).result().data()
    z_isa = np.array([float(np.real(data["z%d" % i])) for i in range(g["n"])])
    T = ql.TrotterMPS(g, chi_max=256)
    T.step(Jz, dt)
    z_mps = T.z_expect()
    return dict(max_abs_diff=float(np.max(np.abs(z_isa - z_mps))), z_isa=z_isa.tolist(), z_mps=z_mps.tolist(),
                ok=bool(np.max(np.abs(z_isa - z_mps)) <= 1e-6))


def choose_backend(svc, job):
    names = [PRIMARY, FALLBACK] if job == "A" else [rjson(os.path.join(JOBS, "A", "prep.json"))["backend"]]
    log = []
    g = ql.graph57()
    for nm in names:
        b = svc.backend(nm)
        st = b.status()
        if not st.operational:
            log.append(dict(backend=nm, reason="not operational"))
            continue
        props = b.properties()
        fq = list(props.faulty_qubits())
        fe = [tuple(x.qubits) for x in props.faulty_gates() if len(x.qubits) == 2]
        try:
            sel = qr.choose_routed_layout(b.target, g, 5, fq, fe)
        except RuntimeError as e:
            log.append(dict(backend=nm, reason=str(e)))
            continue
        return b, sel, dict(faulty_qubits=fq, faulty_2q=fe, pending_jobs=st.pending_jobs, tried=log)
    raise SystemExit("STOP: no backend qualifies: %s" % log)


def prepare(job):
    from qiskit import qpy
    d = os.path.join(JOBS, job)
    if os.path.exists(os.path.join(d, "job_id.txt")):
        raise SystemExit("STOP: job %s already submitted" % job)
    os.makedirs(d, exist_ok=True)
    svc = service()
    acc = account(svc)
    if not acc["free_ok"]:
        raise SystemExit("STOP: instance is not the free Open plan: %s" % acc["instances"])
    g = ql.graph57()
    if job == "A":
        Jzs, shots_k, cap = [1.2], SHOTS_A, CAP_A
        sb_info = None
    else:
        ua = rjson(os.path.join(JOBS, "A", "usage.json"))["quantum_seconds"]
        u = ua / (2 * CHECK_SHOTS + 10 * SHOTS_A)
        Jzs = [1.6, 4.0]
        S = 1000 * int((CAP_TOTAL - ua - 10 - 2 * CHECK_SHOTS * u) / (20 * u) / 1000)
        if S < 10_000:
            Jzs = [1.6]
            S = 1000 * int((CAP_TOTAL - ua - 10 - 2 * CHECK_SHOTS * u) / (10 * u) / 1000)
        if S < 10_000:
            wjson(os.path.join(d, "prep.json"), dict(job=job, time=now(), decision="not submitted", U_A=ua, u=u, S_B=S))
            raise SystemExit("job B not submitted: S_B = %d < 1e4 (U_A = %.1f s)" % (S, ua))
        shots_k, cap = S, int(np.floor(CAP_TOTAL - ua - 10))
        sb_info = dict(U_A=ua, u=u, S_B_declared_formula=S, Jz=Jzs)
        # DEVIATIONS.md item 2: the declared per-shot formula ignores the per-randomization overhead (job B has 20
        # Krylov pubs, job A had 10). Fit T = shots * r0 + n_rand * o on job A's Krylov execution span (r0 = rep_delay
        # + mean ISA duration), then choose S so that the expected usage is <= 0.9 * cap (same cap).
        import re
        fa = rjson(os.path.join(JOBS, "A", "fetch.json"))
        pa = rjson(os.path.join(JOBS, "A", "prep.json"))
        spans = re.findall(r"start='([^']+)', stop='([^']+)', size=(\d+)", str(fa["result_metadata"]))
        tt = [((datetime.datetime.fromisoformat(b_) - datetime.datetime.fromisoformat(a_)).total_seconds(), int(n_))
              for a_, b_, n_ in spans]
        t_chk = [t for t, n_ in tt if n_ < 100000][0]
        t_kry = [t for t, n_ in tt if n_ >= 100000][0]
        repd = 0.00025
        r0a = repd + float(np.mean(pa["durations_s"][2:]))
        o_rand = (t_kry - 10 * SHOTS_A * r0a) / (10 * 32)
        sb_info.update(span_checks_s=t_chk, span_krylov_s=t_kry, r0_A=r0a, overhead_per_randomization_s=o_rand)
        sb_info["_pending_fit"] = True
    b, sel, binfo = choose_backend(svc, job)
    snap = snapshot(b, sel)
    wjson(os.path.join(d, "calibration_snapshot.json"), snap)
    tags, circs, shots = [], [], []
    for t_, s_ in (("neel", ql.neel_sites(g)), ("asym", ql.ASYM_SITES)):
        tags.append(t_)
        circs.append(ql.product_circuit(g, s_, "check_" + t_))
        shots.append(CHECK_SHOTS)
    chk_isa = ql.transpile_isa(circs, b, sel["layout"])
    kr_tags, kr_circs = [], []
    for Jz in Jzs:
        for k in range(1, ql.K + 1):
            kr_tags.append("J%.1f_k%d" % (Jz, k))
            kr_circs.append(qr.routed_krylov_circuit(g, Jz, ql.DT57[Jz], k, sel))
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
    shots += [shots_k] * len(kr_tags)
    rep = b.configuration().default_rep_delay
    durs = [float(c.estimate_duration(b.target, unit="s")) for c in isas]
    if sb_info and sb_info.pop("_pending_fit", False):
        nk = len(Jzs) * ql.K
        r0b = rep + float(np.mean(durs[2:]))
        S_fit = 1000 * int((0.9 * cap - sb_info["span_checks_s"] - nk * 32 * sb_info["overhead_per_randomization_s"])
                           / (nk * r0b) / 1000)
        sb_info.update(r0_B=r0b, S_B_used=min(S_fit, sb_info["S_B_declared_formula"]),
                       expected_usage_s=sb_info["span_checks_s"] + nk * 32 * sb_info["overhead_per_randomization_s"]
                       + nk * min(S_fit, sb_info["S_B_declared_formula"]) * r0b)
        if sb_info["S_B_used"] < 10_000:
            raise SystemExit("job B not submitted: fitted S_B < 1e4 (%s)" % sb_info)
        shots = shots[:2] + [sb_info["S_B_used"]] * nk
    est = float(sum(s * (rep + du) for s, du in zip(shots, durs)))
    eq = equivalence(kr_isa[0], sel, Jzs[0], ql.DT57[Jzs[0]])
    qp = os.path.join(d, "isa.qpy")
    with open(qp, "wb") as f:
        qpy.dump(isas, f)
    with open(qp, "rb") as f:
        back = qpy.load(f)
    for t_, c in zip(tags, back):
        if t_ in ("neel", "asym"):
            ql.check_isa(c, g, sel["layout"])
        else:
            qr.check_isa_routed(c, g, sel)
    prep = dict(job=job, time=now(), account=acc, backend=b.name, backend_info=binfo, sel=sel, Jz=Jzs, tags=tags,
                shots=shots, max_execution_time=cap, est_qpu_lower_s=est, durations_s=durs, isa_stats=stats,
                equivalence={k: v for k, v in eq.items() if k in ("max_abs_diff", "ok")}, qpy_sha256=ql.sha256_file(qp),
                qpy_reload_checked=True, sb=sb_info, calibration_last_update=snap["last_update_date"],
                calibration_snapshot_sha256=ql.sha256_file(os.path.join(d, "calibration_snapshot.json")))
    wjson(os.path.join(d, "equivalence.json"), eq)
    wjson(os.path.join(d, "prep.json"), prep)
    print(json.dumps({k: prep[k] for k in ("job", "backend", "Jz", "max_execution_time", "est_qpu_lower_s",
                                            "equivalence", "qpy_sha256", "calibration_last_update")}, default=str))
    print("layout score/step %.4f relax %s moves/step %d; k=10 cz %s depth %s" % (
        sel["score_2q_per_step"], sel.get("relax"), sel["moves_per_step"], stats[kr_tags[-1]]["cz"],
        stats[kr_tags[-1]]["cz_depth"]))
    if not eq["ok"]:
        raise SystemExit("STOP: pre-submission equivalence failed (max |dZ| = %.3e)" % eq["max_abs_diff"])
    if est > cap:
        raise SystemExit("STOP: lower-bound estimate %.1f s exceeds the job cap %d s" % (est, cap))


def submit(job):
    from qiskit import qpy
    from qiskit_ibm_runtime import SamplerV2
    d = os.path.join(JOBS, job)
    prep = rjson(os.path.join(d, "prep.json"))
    if os.path.exists(os.path.join(d, "job_id.txt")):
        raise SystemExit("STOP: already submitted")
    if not prep["equivalence"]["ok"]:
        raise SystemExit("STOP: equivalence not ok")
    qp = os.path.join(d, "isa.qpy")
    if ql.sha256_file(qp) != prep["qpy_sha256"]:
        raise SystemExit("STOP: QPY hash differs")
    with open(qp, "rb") as f:
        isas = qpy.load(f)
    svc = service()
    acc = account(svc)
    cap = int(prep["max_execution_time"])
    if not acc["free_ok"]:
        raise SystemExit("STOP: not the free Open plan")
    if acc["remaining_s"] is None or acc["remaining_s"] < cap + MARGIN:
        raise SystemExit("STOP: remaining %s s < cap %d + margin %d" % (acc["remaining_s"], cap, MARGIN))
    b = svc.backend(prep["backend"])
    if not b.status().operational:
        raise SystemExit("STOP: backend not operational")
    sampler = SamplerV2(mode=b)
    sampler.options.dynamical_decoupling.enable = True
    sampler.options.twirling.enable_gates = True
    sampler.options.twirling.enable_measure = False
    sampler.options.twirling.num_randomizations = "auto"
    sampler.options.twirling.shots_per_randomization = "auto"
    sampler.options.max_execution_time = cap
    pubs = [(c, None, int(s)) for c, s in zip(isas, prep["shots"])]
    job_ = sampler.run(pubs)
    jid = job_.job_id()
    with open(os.path.join(d, "job_id.txt"), "w") as f:
        f.write(jid + "\n")
    rec = dict(job=job, job_id=jid, submitted=now(), backend=b.name, account_before=acc, max_execution_time=cap,
               options=dict(dd=True, twirling_gates=True, twirling_measure=False, randomizations="auto",
                            shots_per_randomization="auto"), n_pubs=len(pubs), total_shots=int(sum(prep["shots"])))
    try:
        rec["usage_estimation"] = job_.usage_estimation
    except Exception as e:
        rec["usage_estimation_error"] = str(e)[:200]
    wjson(os.path.join(d, "submit.json"), rec)
    print("submitted", jid, rec.get("usage_estimation"))
    est = (rec.get("usage_estimation") or {}).get("quantum_seconds")
    if est is not None and est > cap:
        job_.cancel()
        rec["cancelled"] = "usage estimate %.1f s > cap %d s" % (est, cap)
        wjson(os.path.join(d, "submit.json"), rec)
        print("CANCELLED:", rec["cancelled"])


def poll(job):
    d = os.path.join(JOBS, job)
    jid = open(os.path.join(d, "job_id.txt")).read().strip()
    svc = service()
    j = svc.job(jid)
    st = j.status()
    st = st if isinstance(st, str) else getattr(st, "name", str(st))
    row = dict(time=now(), job_id=jid, status=st)
    try:
        row["usage_estimation"] = j.usage_estimation
    except Exception:
        pass
    wjson(os.path.join(d, "status.json"), row)
    print(json.dumps(row, default=str))
    sub = rjson(os.path.join(d, "submit.json"))
    est = (row.get("usage_estimation") or {}).get("quantum_seconds")
    if st in ("QUEUED", "INITIALIZING") and est is not None and est > sub["max_execution_time"] \
            and "cancelled" not in sub:
        j.cancel()
        sub["cancelled"] = "usage estimate %.1f s > cap %d s (at poll)" % (est, sub["max_execution_time"])
        wjson(os.path.join(d, "submit.json"), sub)
        print("CANCELLED:", sub["cancelled"])
    return 0 if st in ("DONE", "ERROR", "CANCELLED") else 3


def fetch(job):
    d = os.path.join(JOBS, job)
    prep = rjson(os.path.join(d, "prep.json"))
    jid = open(os.path.join(d, "job_id.txt")).read().strip()
    svc = service()
    j = svc.job(jid)
    st = j.status()
    st = st if isinstance(st, str) else getattr(st, "name", str(st))
    if st != "DONE":
        raise SystemExit("job status %s" % st)
    res = j.result()
    g = ql.graph57()
    raw = {}
    out = dict(job=job, job_id=jid, fetched=now(), status=st, pubs={})
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
        out["pubs"][t_] = dict(shots=int(len(conf)), unique=int(len(u)),
                               unique_in_sector=int(np.sum(pc == g["n_down"])),
                               shots_in_sector=int(np.sum(c[pc == g["n_down"]])), metadata=r.metadata)
    np.savez_compressed(os.path.join(d, "raw_configs.npz"), **raw)
    checks = {}
    for t_, s_ in (("neel", ql.neel_sites(g)), ("asym", ql.ASYM_SITES)):
        checks[t_] = ql.check_verdict(raw[t_], ql.config_int(s_), g["n"])
    checks["both_pass"] = bool(checks["neel"]["pass_"] and checks["asym"]["pass_"])
    wjson(os.path.join(d, "checks.json"), checks)
    usage = dict(time=now())
    try:
        usage["quantum_seconds"] = float(j.usage())
    except Exception as e:
        usage["usage_error"] = str(e)[:200]
    try:
        usage["metrics"] = j.metrics()
        q = usage["metrics"].get("usage", {}).get("quantum_seconds")
        if "quantum_seconds" not in usage and q is not None:
            usage["quantum_seconds"] = float(q)
    except Exception as e:
        usage["metrics_error"] = str(e)[:200]
    usage["account_after"] = account(svc)
    wjson(os.path.join(d, "usage.json"), usage)
    out["result_metadata"] = res.metadata
    wjson(os.path.join(d, "fetch.json"), out)
    with open(os.path.join(d, "raw_configs.sha256"), "w") as f:
        f.write(ql.sha256_file(os.path.join(d, "raw_configs.npz")) + "  raw_configs.npz\n")
    print("checks: neel pass %s (min %.4f), asym pass %s (min %.4f); usage %s s" % (
        checks["neel"]["pass_"], checks["neel"]["min_site_agreement"], checks["asym"]["pass_"],
        checks["asym"]["min_site_agreement"], usage.get("quantum_seconds")))
    for t_ in prep["tags"]:
        p = out["pubs"][t_]
        print(t_, p["shots"], p["unique"], p["unique_in_sector"], p["shots_in_sector"])


if __name__ == "__main__":
    mode, job = sys.argv[1], sys.argv[2]
    assert job in ("A", "B")
    if mode == "prepare":
        prepare(job)
    elif mode == "submit":
        submit(job)
    elif mode == "poll":
        sys.exit(poll(job))
    elif mode == "fetch":
        fetch(job)
    else:
        raise SystemExit("mode?")
