"""real_data/checks/r11/fp_device_rebuild.py  (R11 fix pass, fixer FP, 2026-11-13)
Copy of paper/reviews/R10_2026-11-12/scratch/math-rigorous-bounds/device_rq.py with its paths adapted (the work tree
is found from this file; output fp_device_rebuild_<job>_<Jz>_<var>.json next to this file). Nothing else changed.
The four cases are run and summarized by fp_device_rebuild_summary.py.

Text of the original header:
Reviewer math-rigorous-bounds (R10): the device energy "in rational arithmetic", re-derived.

usage: python -B fp_device_rebuild.py <job B|C> <Jz 4.0|6.0> <var rec|ps>

Steps
  1. raw device configurations -> unique set (own np.unique) ; counts compared with the stored record;
     the two bit-order checks recomputed from the stored check shots (job C only: they are in the same file).
  2. configuration set of the stored analysis: the authors' emu2.recover with the declared seed (needed to rebuild
     the SAME set; the set itself is arbitrary for the proof), or post-selection. Own checks: every configuration has
     exactly n_down = 24 down spins; the set is duplicate-free.
  3. Ritz vector: (a) the authors' path (emu2.SubH + emu2.ground, start vector as declared) to try to reproduce the
     stored vector bit by bit (SHA-256 of the rounded vector);  (b) own sparse matrix and own eigsh call (cross-check).
  4. OWN exact Rayleigh quotient of the rounded integer vector, two independent ways:
       (i)  vectorised: E = [ sum_x a_x (4H a)_x ] / (4 sum_x a_x^2) with Python-integer accumulation,
            neighbours found by searchsorted in the own sorted array;
       (ii) pure Python on a random sample of rows: (4H a)_x recomputed with dict lookups and big ints.
     Labels m_s and Czz_bar of the rounded vector as exact rationals.
  5. graph labellings: the certificates use the MPS relabelling; check it is an isomorphism that maps eta to eta.
Reads only; writes fp_device_rebuild_<job>_<Jz>_<var>.json next to this script.
"""
import hashlib
import json
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..")).replace(chr(92), "/")   # the work tree, found from this file (R11: path adapted)
FT = ROOT + "/phase3/full_runs/final_tests"
sys.dont_write_bytecode = True
sys.path.insert(0, FT + "/code")
import emu2  # noqa: E402  (authors' module: used only for recover / CSet / SubH / ground, to rebuild their set and vector)

job, Jzs, var = sys.argv[1], sys.argv[2], sys.argv[3]
Jz = Fraction(Jzs)
t00 = time.time()
out = dict(job=job, Jz=Jzs, var=var)

# ------------------------------------------------------------------------------------------------ graph (own parse)
G = json.load(open(FT + "/code/graphs/hh_d5.json"))
n = int(G["n"])
edges = [tuple(sorted((int(a), int(b)))) for a, b in G["edges"]]
eta = [int(x) for x in G["eta"]]
n_down = sum(1 for e in eta if e == -1)
assert n == 57 and len(edges) == 64 and n_down == 24 and all(eta[a] == -eta[b] for a, b in edges)
order = [int(x) for x in G["order"]]
inv = {v: p for p, v in enumerate(order)}
mps_edges = sorted(tuple(sorted((int(a), int(b)))) for a, b in G["mps"]["edges"])
assert sorted(order) == list(range(n))
assert sorted(tuple(sorted((inv[a], inv[b]))) for a, b in edges) == mps_edges, "MPS relabelling is not the same graph"
assert [int(x) for x in G["mps"]["eta"]] == [eta[order[p]] for p in range(n)], "MPS eta is not the relabelled eta"
assert [int(x) for x in G["mps"]["up_init"]] == [1 if eta[order[p]] == 1 else 0 for p in range(n)]
out["graph_relabelling_is_isomorphism"] = True
out["twoS_device_sector"] = n - 2 * n_down

# ----------------------------------------------------------------------------------------------- raw configurations
if job == "C":
    rawp = FT + "/jobs/C_20261108/raw_configs.npz"
    stored = json.load(open(FT + "/out_c3b_20261110T164846Z/out/c/rq_C_J%s_%s.json" % (Jzs, var)))
else:
    rawp = FT + "/inputs/qpu_B_raw_configs.npz"
    stored = json.load(open(FT + "/out_20261106T120830Z/out/c/rq_B_J%s_%s.json" % (Jzs, var)))
out["raw_sha256"] = hashlib.sha256(open(rawp, "rb").read()).hexdigest()
raw = np.load(rawp)
shots = [np.asarray(raw["J%s_k%d" % (Jzs, k)], dtype=np.uint64) for k in range(1, 11)]
allshots = np.concatenate(shots)
assert int(allshots.max()) < (1 << n)
uniq = np.unique(allshots)
pcu = np.bitwise_count(uniq).astype(np.int64)
out.update(n_shots=int(len(allshots)), n_unique=int(len(uniq)), n_unique_in_sector=int((pcu == n_down).sum()),
           stored_n_shots=stored["n_shots"], stored_n_unique=stored["n_unique"],
           stored_n_unique_in_sector=stored["n_unique_in_sector"])
assert (out["n_shots"], out["n_unique"], out["n_unique_in_sector"]) == (stored["n_shots"], stored["n_unique"], stored["n_unique_in_sector"])

# bit-order checks (job C file holds the check shots)
if "neel" in raw.files:
    chk = {}
    neel_int = sum(1 << i for i in range(n) if eta[i] == -1)
    for name in ("neel", "asym"):
        c = np.asarray(raw[name], dtype=np.uint64)
        bits = ((c[:, None] >> np.arange(n, dtype=np.uint64)[None, :]) & np.uint64(1)).astype(np.int8)
        maj = (bits.mean(axis=0) > 0.5).astype(int)
        if name == "neel":
            exp = np.array([(neel_int >> i) & 1 for i in range(n)])
        else:                         # declared asymmetric product state: these sites down (code_c3/qpu_lib.py line 49)
            asym_sites = (0, 1, 2, 3, 9, 14, 25, 30, 37, 44, 50, 56)
            exp = np.array([1 if i in asym_sites else 0 for i in range(n)])
        agree = (bits == exp[None, :]).mean(axis=0)
        chk[name] = dict(shots=int(len(c)), min_site_agreement=float(agree.min()), mean_site_agreement=float(agree.mean()),
                         worst_site=int(agree.argmin()), majority_equals_expected=bool((maj == exp).all()),
                         passes=bool(agree.min() >= 0.9 and (maj == exp).all()))
    out["bit_order_checks_recomputed"] = chk

# ----------------------------------------------------------------------------------------------- configuration set
g = emu2.load_graph(FT + "/code/graphs/hh_d5.json")
assert g["n_down"] == n_down and [tuple(sorted(e)) for e in g["edges"]] == edges
Bu, _ = emu2.unique_rows(allshots.reshape(-1, 1).astype(np.uint64))
assert (Bu[:, 0] == uniq).all()


def qseed(*parts):
    return int.from_bytes(hashlib.sha256(("qpu|" + "|".join(str(p) for p in parts)).encode()).digest()[:8], "little")


rng = np.random.default_rng(qseed("recover", 57, Jzs, "device_" + job, var))
if var == "rec":
    cs = emu2.CSet(emu2.recover(Bu, n, n_down, rng), n)
else:
    cs = emu2.CSet(Bu[pcu == n_down], n)
cfg = np.asarray(cs.B[:, 0], dtype=np.uint64).copy()
D = len(cfg)
assert bool((cfg[1:] > cfg[:-1]).all()), "set not sorted / has duplicates"
assert (np.bitwise_count(cfg) == n_down).all(), "a configuration is outside the sector"
insec_raw = uniq[pcu == n_down]
assert np.isin(insec_raw, cfg).all(), "an in-sector raw configuration is missing from the set"
out.update(D=int(D), stored_D=stored["D"], all_in_sector=True, raw_in_sector_all_kept=True)
assert D == stored["D"]

# ------------------------------------------------------------------------------------------ Ritz vector, their path
Hs = emu2.SubH(cs, g, float(Jz))
E_float, a = emu2.ground(Hs, v0=emu2.neel_start(cs, g))
s = float(2 ** 44) / float(np.max(np.abs(a)))
ai = [int(x) for x in np.rint(np.asarray(a, float) * s)]
vsha = hashlib.sha256(",".join(str(v) for v in ai).encode()).hexdigest()
out.update(E_float_theirpath=E_float, stored_E_float=stored["E_float"], vector_sha256=vsha,
           stored_vector_sha256=stored["vector_sha256"], vector_bit_identical=bool(vsha == stored["vector_sha256"]))

# ------------------------------------------------------------------------------------- own sparse matrix and solve
idx = np.arange(D, dtype=np.int64)
rows, cols = [], []
diag4 = np.zeros(D, dtype=np.int64)          # 4 * diagonal of H = Jz * sum_e ZZ_e  (integer when Jz is an integer)
assert Jz.denominator == 1
Jzi = int(Jz)
nbr = []                                     # per edge: (source indices, target indices) of flips that stay in the set
for (i, j) in edges:
    bi = (cfg >> np.uint64(i)) & np.uint64(1)
    bj = (cfg >> np.uint64(j)) & np.uint64(1)
    anti = bi != bj
    diag4 += np.where(anti, -Jzi, Jzi)
    src = idx[anti]
    flipped = cfg[anti] ^ np.uint64((1 << i) | (1 << j))
    pos = np.searchsorted(cfg, flipped)
    pos[pos >= D] = 0
    ok = cfg[pos] == flipped
    nbr.append((src[ok], pos[ok]))
    rows.append(src[ok])
    cols.append(pos[ok])
r = np.concatenate(rows)
c = np.concatenate(cols)
A = sparse.csr_matrix((np.full(len(r), 0.5), (r, c)), shape=(D, D))
assert abs(A - A.T).max() == 0
Hown = A + sparse.diags(diag4 / 4.0)
w, V = eigsh(Hown, k=1, which="SA", v0=np.asarray(a, float), tol=1e-12, ncv=40, maxiter=50000)
out.update(nnz_offdiag=int(A.nnz), E_float_own_matrix=float(w[0]),
           overlap_own_vs_theirs=float(abs(V[:, 0] @ a) / np.linalg.norm(a)),
           residual_norm_their_vector=float(np.linalg.norm(Hown @ a - E_float * a) / np.linalg.norm(a)))

# ------------------------------------------------------------------------------------------ OWN exact Rayleigh quotient
t0 = time.time()
ao = np.array(ai, dtype=object)
den = int((ao * ao).sum())
# (4 H a)_x = diag4_x a_x + 2 * sum_{x' ~ x} a_x'
Ha4 = np.array([int(d) for d in diag4], dtype=object) * ao
for (src, tgt) in nbr:
    assert len(np.unique(src)) == len(src)
    Ha4[src] = Ha4[src] + 2 * ao[tgt]
num4 = int((ao * Ha4).sum())
E_exact = Fraction(num4, 4 * den)
# labels of the rounded vector
w2 = ao * ao
stag = np.zeros(D, dtype=np.int64)
for i in range(n):
    stag += eta[i] * (1 - 2 * ((cfg >> np.uint64(i)) & np.uint64(1)).astype(np.int64))
zzsum = np.zeros(D, dtype=np.int64)
for (i, j) in edges:
    bi = ((cfg >> np.uint64(i)) & np.uint64(1)).astype(np.int64)
    bj = ((cfg >> np.uint64(j)) & np.uint64(1)).astype(np.int64)
    zzsum += 1 - 2 * (bi ^ bj)
m_s = Fraction(int((w2 * np.array([int(v) for v in stag], dtype=object)).sum()), n * den)
czz = Fraction(int((w2 * np.array([int(v) for v in zzsum], dtype=object)).sum()), len(edges) * den)
out.update(E_exact_own=str(E_exact), E_exact_own_float=float(E_exact), m_s_exact_own=str(m_s), Czz_bar_exact_own=str(czz),
           den_bits=den.bit_length(), stored_E_exact=stored["E_exact"], stored_m_s_exact=stored["m_s_exact"],
           stored_Czz_bar_exact=stored["Czz_bar_exact"],
           E_exact_equals_stored=bool(E_exact == Fraction(stored["E_exact"])),
           m_s_exact_equals_stored=bool(m_s == Fraction(stored["m_s_exact"])),
           Czz_exact_equals_stored=bool(czz == Fraction(stored["Czz_bar_exact"])),
           E_exact_own_minus_stored=float(E_exact - Fraction(stored["E_exact"])),
           m_s_own_minus_stored=float(m_s - Fraction(stored["m_s_exact"])),
           Czz_own_minus_stored=float(czz - Fraction(stored["Czz_bar_exact"])),
           E_float_minus_exact=float(Fraction(E_float) - E_exact), exact_secs=time.time() - t0)

# ---------------------------------------------------------------- pure-Python sample check of rows of (4 H a)
rs = np.random.default_rng(20261112)
sample = rs.choice(D, size=min(D, 3000), replace=False)
lut = {int(cfg[k]): k for k in range(D)}
bad = 0
for k in sample.tolist():
    x = int(cfg[k])
    assert bin(x).count("1") == n_down
    acc = 0
    dz = 0
    for (i, j) in edges:
        bi, bj = (x >> i) & 1, (x >> j) & 1
        if bi == bj:
            dz += Jzi
        else:
            dz -= Jzi
            y = x ^ (1 << i) ^ (1 << j)
            kk = lut.get(y)
            if kk is not None:
                acc += 2 * ai[kk]
    if dz * ai[k] + acc != int(Ha4[k]):
        bad += 1
out.update(sample_rows_checked=int(len(sample)), sample_rows_mismatch=int(bad))
out["secs"] = time.time() - t00
json.dump(out, open(HERE + "/fp_device_rebuild_%s_%s_%s.json" % (job, Jzs, var), "w"), indent=1)
for k, v in out.items():
    print(k, "=", v)
