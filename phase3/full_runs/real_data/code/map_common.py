# real_data / map_common.py  (own code; 2026-11-12; task rd-code-map)
#
# Shared by the MAP code of DECLARATION.md Secs. 2, 3, 4, 6 and the gates of Sec. 8:
#   - paths and the constants of Sec. 0 (sizes, couplings, labels, tolerance, numerical allowance);
#   - the GUARD: nothing here reads converted/ unless DECLARATION.sha256 exists and equals the SHA-256 of
#     DECLARATION.md (read_converted calls the guard itself; there is no argument that switches it off);
#   - the loader of the converted public data BY SCHEMA ("p5-real-data-v1" of convert_real_data.py): pairs are matched
#     by their site pair and loops by their site set, never by position; every exact quantity is a fractions.Fraction
#     of the dyadic numbers stored in the file (M_real, m_s, Czz_bar, the edge sum of ZZ).
# parse_real() takes an already parsed object and touches no file: the unit tests feed it synthetic objects.
# No pickle anywhere. No code of the downloaded repository is imported or executed. Standard library only.
import sys

sys.dont_write_bytecode = True          # never write __pycache__ into the stored run folders this code imports from

import hashlib
import json
import math
import os
import re
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)                                   # .../phase3/full_runs/real_data
FULL = os.path.dirname(RD)                                   # .../phase3/full_runs
ROOT = os.path.dirname(os.path.dirname(FULL))                # .../work
MAPRUN = os.path.join(FULL, "map")
MAPDIR = os.path.join(MAPRUN, "laptop_analysis")
MAP_CODE = os.path.join(MAPDIR, "code")
RIGOR = os.path.join(FULL, "rigor")
FT = os.path.join(FULL, "final_tests")
OUT = os.path.join(RD, "out")
REVIEW = os.path.join(ROOT, "paper", "reviews", "R10_2026-11-12")
MYVERIFY = os.path.join(REVIEW, "scratch", "math-rigorous-bounds", "myverify.py")

SCHEMA = "p5-real-data-v1"
SIZES = (57, 115)
D_OF_N = {19: 3, 57: 5, 115: 7}
LABELS = ("m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop")
EXACT_LABELS = ("m_s", "Czz_bar")                            # labels with exact certificates (Sec. 2)
LOCALS = ("Z_bulk", "Z_boundary", "Czz_edge", "Z_loop")
TAU_FRAC = 0.06                                              # tau = 0.06 |O_GS| (float product, as in the stored map)
TAU_RF = Fraction(6, 100)                                    # reference-free: tau_rf = (6/100) min |O| over I
ALLOW = Fraction(1, 10 ** 6)                                 # numerical allowance of Sec. 2 on E_real and on M_real
DATASET, COMPARISON, DMRG = "skqd_random_flip", "skqd_post_select", "dmrg"
G2_EXCLUDED = {(115, COMPARISON): ("5.6", "5.7", "5.9", "6.0")}   # Sec. 8, G2: excluded everywhere
ALL_J = tuple(Fraction(k, 10) for k in range(11, 61))        # the 50 couplings of the dataset
TRAIN_J = tuple(J for J in ALL_J if J >= Fraction(16, 10))   # 45
TEST_J = tuple(Fraction(k, 10) for k in (11, 12, 13, 14))
APART_J = (Fraction(15, 10),)
# SHA-256 of the converted files and of the pinned archive, as listed in DECLARATION.md Sec. 11
PINNED = {
    "real_n57.json": "ec96cd6d49a160ba91b38a08f987d221aa01c465c470e0eb17c13f9bacedc4dd",
    "real_n115.json": "5890160c5ff0992b0859ce44fba3a74d1aff6fa6e005f8ef0d0db4f4233d0002",
    "lattice_maps.json": "a066581a316dbcfacabe8b50f318dc323fc05eaf67c67f99209cc4282586ec81",
}
PINNED_ARCHIVE = ("source/archive/quantum-groundstate-learning-6b8866b66d62aaf3ee815cd14fa58e9bf4629d66.tar.gz",
                  "13aa8e69c9bc614c72c5a415ecd889f113eabe95eec81e221174b3f14dedbb91")
HEX64 = re.compile(r"\b[0-9a-fA-F]{64}\b")
JKEY = re.compile(r"^\d+\.\d$")


# ------------------------------------------------------------------------------------------------ small helpers
def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jfr(x):
    """A coupling as an exact rational (every coupling of this project is a multiple of 1/10)."""
    if isinstance(x, Fraction):
        return x
    return Fraction("%.1f" % float(x))


def jkey(J):
    return "%.1f" % float(J)


def st(x):
    return tuple(sorted(int(i) for i in x))


def fstr(x):
    """Exact rational as 'p/q' (JSON output)."""
    return None if x is None else "%d/%d" % (x.numerator, x.denominator)


def dump_json(path, obj):
    """Deterministic JSON (sorted keys, no time stamp); returns the SHA-256 of the bytes written."""
    s = json.dumps(obj, indent=1, sort_keys=True, allow_nan=False, ensure_ascii=True) + "\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    return sha256_bytes(s.encode("utf-8"))


# ------------------------------------------------------------------------------------------------ the guard
class Refused(SystemExit):
    """Raised when converted/ would be read without a hashed, matching declaration (exit code 3)."""

    def __init__(self, msg):
        super().__init__("REFUSED: " + msg)
        self.code = 3
        self.msg = msg


def declaration_guard(rd=None):
    """Returns the SHA-256 of <rd>/DECLARATION.md iff <rd>/DECLARATION.sha256 exists and holds exactly that hash.
    Otherwise raises Refused. Every function of this code that opens a file of converted/ calls it first."""
    rd = rd or RD
    dpath, hpath = os.path.join(rd, "DECLARATION.md"), os.path.join(rd, "DECLARATION.sha256")
    if not os.path.exists(hpath):
        raise Refused("%s does not exist: the declaration is not hashed, so converted/ is not read." % hpath)
    if not os.path.exists(dpath):
        raise Refused("%s does not exist." % dpath)
    with open(hpath, encoding="utf-8") as f:
        m = HEX64.search(f.read())
    if not m:
        raise Refused("%s holds no SHA-256." % hpath)
    recorded, actual = m.group(0).lower(), sha256_file(dpath)
    if recorded != actual:
        raise Refused("DECLARATION.sha256 (%s...) does not match DECLARATION.md (%s...)." % (recorded[:12], actual[:12]))
    return actual


def seed_from_hash(h):
    """Sec. 7: 'integer of the first eight hex digits of the SHA-256 of the hashed declaration' (used by gate G6)."""
    h = str(h).strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", h):
        raise ValueError("the hash must be 64 hexadecimal digits")
    return int(h[:8], 16)


# ------------------------------------------------------------------------------------------------ graphs
_GRAPHS = {}


def graph(n):
    """This project's graph file (the one the stored map and the certificates use; identical to the repository's
    lattice as labelled sets, declaration Sec. 1, T1)."""
    if n not in _GRAPHS:
        G = rj(os.path.join(MAP_CODE, "graphs", "hh_d%d.json" % D_OF_N[n]))
        eta = [int(x) for x in G["eta"]]
        g = dict(n=int(G["n"]), eta=eta, M0=sum(eta), edges=[st(e) for e in G["edges"]], nn2=[st(e) for e in G["nn2"]],
                 loops=[st(l) for l in G["loops12"]], local=G["local"], raw=G)
        assert g["n"] == n and len(set(g["edges"])) == len(g["edges"]) and len(set(g["nn2"])) == len(g["nn2"])
        assert not (set(g["edges"]) & set(g["nn2"])) and all(abs(e) == 1 for e in eta)
        _GRAPHS[n] = g
    return _GRAPHS[n]


def synthetic_graph(n, edges, nn2, eta, loops, local):
    """A graph record in the same form, for the unit tests."""
    return dict(n=n, eta=list(eta), M0=sum(eta), edges=[st(e) for e in edges], nn2=[st(e) for e in nn2],
                loops=[st(l) for l in loops], local=local, raw=None)


# ------------------------------------------------------------------------------------------------ schema loader
def _floats(v, what, length=None):
    if not isinstance(v, list) or (length is not None and len(v) != length):
        raise ValueError("%s: expected a list%s" % (what, "" if length is None else " of length %d" % length))
    out = []
    for x in v:
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(float(x)):
            raise ValueError("%s: non-numeric or non-finite value" % what)
        out.append(float(x))
    return out


def _match(plist, vals, what):
    """{sorted site tuple: value}; one to one, never by position."""
    if not isinstance(plist, list):
        raise ValueError("%s: no site list" % what)
    keys = [st(p) for p in plist]
    vals = _floats(vals, what, len(keys))
    if len(set(keys)) != len(keys):
        raise ValueError("%s: a site set appears twice" % what)
    return dict(zip(keys, vals))


def observables(z, pairs, loops, G):
    """The real quantities of Sec. 0 for one state given by its site magnetizations, pair correlators and loops.
    Exact (Fraction of the stored dyadic numbers): M = sum_i z_i, m_s, Czz_bar and the edge sum of ZZ."""
    n, eta, loc = G["n"], G["eta"], G["local"]
    zf = [Fraction(x) for x in z]
    M = sum(zf)
    ms = sum(e * x for e, x in zip(eta, zf)) / n
    try:
        ce = [pairs[e] for e in G["edges"]]
        c2 = [pairs[e] for e in G["nn2"]]
        lab_edge = pairs[st(loc["edge"])]
        lab_loop = loops[st(loc["loop"])]
        loop_vals = [loops[l] for l in G["loops"]]
    except KeyError as ex:
        raise ValueError("a pair or loop of this project's graph is missing in the data: %s" % (ex,))
    sum_zz = sum(Fraction(c) for c in ce)
    czz = sum_zz / len(ce)
    labels = dict(m_s=float(ms), Czz_bar=float(czz), C2_bar=math.fsum(c2) / len(c2), Z_bulk=z[loc["bulk_site"]],
                  Z_boundary=z[loc["boundary_site"]], Czz_edge=lab_edge, Z_loop=lab_loop)
    return dict(M=M, M_float=float(M), labels=labels, labels_exact=dict(m_s=ms, Czz_bar=czz), sum_zz_edges=sum_zz,
                orientation=(1 if ms > 0 else (-1 if ms < 0 else 0)),
                families=dict(sites=list(z), edges=ce, second_neighbours=c2, loops=loop_vals))


def _coupling(key, e, what):
    if not JKEY.match(str(key)):
        raise ValueError("%s: '%s' is not a coupling key" % (what, key))
    J = Fraction(str(key))
    if "jz" in e and abs(float(e["jz"]) - float(J)) > 1e-9:
        raise ValueError("%s %s: the jz field differs from the coupling key" % (what, key))
    return J


def _energy(e, k, what):
    v = e.get(k)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
        raise ValueError("%s: field %s is missing or not a finite number" % (what, k))
    return float(v)


def parse_label_entry(key, e, G, group):
    """One label file. E_real := final_global_energy; E_first := ground_state_energy (energy before the basis
    optimization); labels from z_basis_opt, 2_nn_corr_funcs_zz_basis_opt (through 2_nn_corr_pairs_zz_basis_opt)
    and z_loop (through z_loop_sites). Files without labels (comparison variant at n = 57) keep the energies."""
    what = "%s %s" % (group, key)
    J = _coupling(key, e, what)
    r = dict(Jz=J, key=jkey(J), group=group, E_real=_energy(e, "final_global_energy", what),
             E_first=_energy(e, "ground_state_energy", what), has_labels="z_basis_opt" in e,
             source_sha256=e.get("_source_sha256"))
    r["energy_vopt"] = float(e["energy_vopt"]) if "energy_vopt" in e else None
    if r["has_labels"]:
        z = _floats(e["z_basis_opt"], what + " z_basis_opt", G["n"])
        pairs = _match(e["2_nn_corr_pairs_zz_basis_opt"], e["2_nn_corr_funcs_zz_basis_opt"], what + " pairs")
        loops = _match(e["z_loop_sites"], e["z_loop"], what + " loops")
        r.update(z=z, pairs=pairs, loops=loops)
        r.update(observables(z, pairs, loops, G))
    return r


def parse_dmrg_entry(key, e, G):
    """One file of the authors' DMRG (bond dimension 320): E0, e1 and the same observables."""
    what = "dmrg %s" % key
    J = _coupling(key, e, what)
    z = _floats(e["z"], what + " z", G["n"])
    pairs = _match(e["2_nn_corr_pairs"], e["2_nn_corr_funcs_zz"], what + " pairs")
    loops = _match(e["z_loop_sites"], e["z_loop"], what + " loops")
    r = dict(Jz=J, key=jkey(J), group=DMRG, E0=_energy(e, "ground_state_energy", what), e1=_energy(e, "e1", what),
             z=z, pairs=pairs, loops=loops, source_sha256=e.get("_source_sha256"))
    r.update(observables(z, pairs, loops, G))
    return r


def parse_real(obj, n, G=None):
    """Parsed content of converted/real_n<n>.json -> dict(n, G, dataset, comparison, dmrg), each {coupling key: record}.
    Touches no file. Raises ValueError on anything that does not fit the schema."""
    if not isinstance(obj, dict) or obj.get("schema") != SCHEMA or int(obj.get("n", -1)) != n:
        raise ValueError("not a '%s' object for n = %d" % (SCHEMA, n))
    G = G or graph(n)
    out = dict(n=n, G=G, dataset={}, comparison={}, dmrg={})
    for group, dst in ((DATASET, "dataset"), (COMPARISON, "comparison")):
        excl = G2_EXCLUDED.get((n, group), ())
        for key, e in obj.get(group, {}).items():
            if key in excl:
                continue
            out[dst][key] = parse_label_entry(key, e, G, group)
    for key, e in obj.get(DMRG, {}).items():
        out["dmrg"][key] = parse_dmrg_entry(key, e, G)
    return out


def check_complete(real, couplings=ALL_J):
    """The dataset must hold labels and the authors' DMRG a truth at every one of the 50 couplings."""
    miss = [jkey(J) for J in couplings if jkey(J) not in real["dataset"] or not real["dataset"][jkey(J)]["has_labels"]]
    miss_d = [jkey(J) for J in couplings if jkey(J) not in real["dmrg"]]
    if miss or miss_d:
        raise ValueError("n = %d: couplings without labels %s, without the authors' DMRG %s" % (real["n"], miss, miss_d))
    return True


def read_converted(n, rd=None):
    """(parsed JSON of converted/real_n<n>.json, SHA-256 of the hashed declaration). The guard runs first; then the
    bytes are checked against the hash pinned in the declaration (Sec. 11), which must itself list that hash."""
    rd = rd or RD
    decl_sha = declaration_guard(rd)
    name = "real_n%d.json" % n
    with open(os.path.join(rd, "DECLARATION.md"), encoding="utf-8") as f:
        if PINNED[name] not in f.read():
            raise Refused("the hashed declaration does not list the pinned SHA-256 of %s." % name)
    p = os.path.join(rd, "converted", name)
    with open(p, "rb") as f:
        b = f.read()
    if sha256_bytes(b) != PINNED[name]:
        raise Refused("%s does not have the SHA-256 pinned in the declaration." % p)
    return json.loads(b.decode("utf-8")), decl_sha


def load_real(n, rd=None):
    """The real data of one size, parsed and checked for completeness. Needs the hashed declaration."""
    obj, decl_sha = read_converted(n, rd)
    real = parse_real(obj, n)
    check_complete(real)
    real["declaration_sha256"] = decl_sha
    return real


def round_down_2sig(x):
    """Sec. 4: 'rounded down to two significant digits' (exact decimal arithmetic on the shortest repr)."""
    from decimal import Decimal, ROUND_FLOOR
    if x is None or not x > 0:
        return None
    d = Decimal(repr(float(x)))
    q = Decimal(1).scaleb(d.adjusted() - 1)
    return float((d / q).to_integral_value(rounding=ROUND_FLOOR) * q)
