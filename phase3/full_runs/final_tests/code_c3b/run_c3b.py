"""C3b (2026-11-08, ADDENDUM_C3b.md): runs the SEALED code_c3/submit_c3.py functions unchanged, with two settings fixed by the
author's decision of 2026-11-08:
  (1) job directory jobs/C_20261108/ (jobs/C/, prepared for ibm_fez on 2026-11-06, stays untouched);
  (2) backend: ibm_kingston only, i.e. the first branch of the sealed backend rule (operational and the sealed layout rule
      qpu_route.choose_routed_layout succeeds), plus the stop-only condition score <= 0.95 expected two-qubit errors per step.
      If either fails: STOP. No fall-back to any other backend (the author approved only ibm_kingston).
Everything else (circuits, shots, layout rule, transpilation, ISA checks, equivalence, sampler options, max_execution_time,
balance check, poll, fetch, bit-order checks) is the sealed function itself.
usage (from final_tests/, with C:/tmp/qgss4env):  python code_c3b/run_c3b.py account|prepare|submit|poll|fetch"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEALED = {  # ADDENDUM_C3.md, "Code at this hash"
    "code_c3/c3_post.py": "3b62b60c48613f1da8e1da3d15d116cffefc10e1a3437418ed29d8730fed1315",
    "code_c3/qpu_lib.py": "b5d9483fac22887c75ed73d546fe4a2cadaeb7c10146342aed42635ba2c970be",
    "code_c3/qpu_route.py": "7ff6fd17a0cba8c3452b4a4d37ecbc0d1483044ca1d3ccb82aab2c4c2d85e18b",
    "code_c3/submit_c3.py": "4e4a642c2988ac0bd619453d9495689a6bf15b739d68b35f4dcf888c53c92ef2",
    "code_c3/tests/test_bitorder.py": "0ffacd2ed6cbf0c979a835c6939a4734711589625edc4d091cf8542ca847db96",
    "code_c3/tests/toygraphs.py": "2ca90a6ec4349d027adbde10699ba6f8b1d7fbba559bd95a41be4dec762af0e0",
    "code_c3/method_copy/emu.py": "a0f0ac663742f306c0daaca4fe80f8859bc1b547189015b41893355ca0c98fae",
    "code_c3/method_copy/emu2.py": "79e295a61025d686b30ecec69b7dbf53f9fae5be75e706884b453865893ad586",
    "code_c3/method_copy/hhmodel.py": "1eb7b6cead37b1e06e95592f8cf7a08b252f188c4ac9e0730a977ee92db4921a",
    "code_c3/method_copy/tn.py": "edd848d7ffd2952ec332cd0cd5bd149c8bf0cd00840329979c0eece957a39d9a",
}
LIMIT = 0.95          # stop-only: validity limit of the gate's noise model (DEVIATIONS item 3), stricter than the seal
JOBDIR = os.path.join(ROOT, "jobs", "C_20261108")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


for rel, h in SEALED.items():
    if sha(os.path.join(ROOT, rel)) != h:
        raise SystemExit("STOP: %s differs from the sealed hash" % rel)
sys.path.insert(0, os.path.join(ROOT, "code_c3"))
import submit_c3 as sc  # noqa: E402

sc.D = JOBDIR


def kingston_only(svc):
    """The first branch of the sealed choose_backend (same calls), without the fall-back; plus the stop-only score limit."""
    g = sc.ql.graph57()
    b = svc.backend(sc.PRIMARY)
    st = b.status()
    if not st.operational:
        raise SystemExit("STOP: ibm_kingston not operational")
    props = b.properties()
    fq = list(props.faulty_qubits())
    fe = [tuple(x.qubits) for x in props.faulty_gates() if len(x.qubits) == 2]
    try:
        sel = sc.qr.choose_routed_layout(b.target, g, 5, fq, fe)
    except RuntimeError as e:
        raise SystemExit("STOP: sealed layout rule fails on ibm_kingston: %s" % e)
    if sel["score_2q_per_step"] > LIMIT:
        raise SystemExit("STOP: ibm_kingston score %.4f > %.2f (validity limit of the gate's noise model)" % (sel["score_2q_per_step"], LIMIT))
    return b, sel, dict(faulty_qubits=fq, faulty_2q=fe, pending_jobs=st.pending_jobs, tried=[],
                        c3b="ibm_kingston only (author 2026-11-08); stop-only score limit %.2f" % LIMIT)


sc.choose_backend = kingston_only


def addendum_ok():
    p = os.path.join(ROOT, "ADDENDUM_C3b.sha256")
    if not os.path.exists(p):
        return False
    want = open(p, encoding="utf-8").read().split()[0]
    return sha(os.path.join(ROOT, "ADDENDUM_C3b.md")) == want


def submit_guarded():
    if not addendum_ok():
        raise SystemExit("STOP: ADDENDUM_C3b.md missing, unhashed or changed")
    prep = sc.rjson(os.path.join(JOBDIR, "prep.json"))
    if prep["backend"] != sc.PRIMARY:
        raise SystemExit("STOP: prepared backend is %s, not ibm_kingston" % prep["backend"])
    if prep["sel"]["score_2q_per_step"] > LIMIT:
        raise SystemExit("STOP: prepared score %.4f > %.2f" % (prep["sel"]["score_2q_per_step"], LIMIT))
    sc.submit()


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "account":
        a = sc.account(sc.service())
        print({k: a[k] for k in ("time", "consumed_s", "limit_s", "remaining_s", "free_ok", "period", "limit_reached")})
    elif m == "prepare":
        if not addendum_ok():
            raise SystemExit("STOP: ADDENDUM_C3b.md missing, unhashed or changed")
        sc.prepare()
    elif m == "submit":
        submit_guarded()
    elif m == "poll":
        sys.exit(sc.poll())
    elif m == "fetch":
        sc.fetch()
    else:
        raise SystemExit("mode?")
