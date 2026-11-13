# real_data / rd_common.py  (own code; 2026-11-12; task rd-code-learn)
#
# Shared by the prediction and learning code of DECLARATION.md Secs. 5-7:
#   - the GATE: nothing here opens converted/ unless DECLARATION.sha256 exists and equals the SHA-256 of DECLARATION.md;
#   - the loader of the converted public data (plain JSON; schema "p5-real-data-v1" of convert_real_data.py), with
#     pairs matched by their site pair and loops by their site set, never by position;
#   - the truth rule of Sec. 0 (this project's references where stored, otherwise the authors' DMRG);
#   - the file of nested sets and label intervals written by the map code (out/S_sets.json, format in
#     README_predict_learn.md), with its consistency checks.
# No pickle anywhere. No code of the downloaded repository is imported or executed.
import hashlib
import json
import math
import os
import re
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RD = os.path.dirname(HERE)                                   # .../phase3/full_runs/real_data
FR = os.path.dirname(RD)                                     # .../phase3/full_runs
ROOT_DEFAULT = os.path.dirname(os.path.dirname(FR))          # .../work

TAU_REL = 0.06
ALPHA = 0.1
TRAIN_MIN = 1.6
TEST = [1.1, 1.2, 1.3, 1.4]
APART = [1.5]
ALL_J = [k / 10 for k in range(11, 61)]                      # the 50 couplings of the dataset
TRAIN_J = [j for j in ALL_J if j >= TRAIN_MIN]               # 45
G2_EXCLUDED_POST_SELECT_115 = [5.6, 5.7, 5.9, 6.0]           # gate G2 of the declaration (comparison variant only)
SEVEN = ("m_s", "Czz_bar", "C2_bar", "Z_bulk", "Z_boundary", "Czz_edge", "Z_loop")
FAMILIES = ("sites", "edges", "second_neighbours", "loops")
# SHA-256 of the converted files, as pinned in DECLARATION.md Sec. 11
PINNED = {
    "real_n57.json": "ec96cd6d49a160ba91b38a08f987d221aa01c465c470e0eb17c13f9bacedc4dd",
    "real_n115.json": "5890160c5ff0992b0859ce44fba3a74d1aff6fa6e005f8ef0d0db4f4233d0002",
    "lattice_maps.json": "a066581a316dbcfacabe8b50f318dc323fc05eaf67c67f99209cc4282586ec81",
}
SETS_SCHEMA = "p5-real-data-S-sets-v1"
HEX64 = re.compile(r"\b[0-9a-fA-F]{64}\b")


# ------------------------------------------------------------------------------------------------ gate and seeds
class Refused(SystemExit):
    """Raised when a script would read converted/ without a hashed, matching declaration (exit code 3)."""

    def __init__(self, msg):
        print("REFUSED: " + msg, file=sys.stderr)
        super().__init__(3)
        self.msg = msg


class Gate:
    """Proof that the declaration hash was checked. The loaders of the real data accept nothing else."""

    def __init__(self, sha):
        self.sha = sha


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def require_declaration_hash(rd=None, hash_arg=None):
    """Returns a Gate iff <rd>/DECLARATION.sha256 exists, its 64-hex token equals the SHA-256 of <rd>/DECLARATION.md,
    and (when given) the hash passed as an argument equals both. Otherwise raises Refused: nothing is read."""
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
    if hash_arg is not None and str(hash_arg).lower() != actual:
        raise Refused("the hash passed as an argument (%s...) is not the hash of the declaration (%s...)."
                      % (str(hash_arg)[:12], actual[:12]))
    return Gate(actual)


def seed_from_hash(h):
    """Sec. 7: 'integer of the first eight hex digits of the SHA-256 of the hashed declaration'."""
    h = str(h).strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", h):
        raise ValueError("the hash must be 64 hexadecimal digits")
    return int(h[:8], 16)


# ------------------------------------------------------------------------------------------------ graphs, families
def rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def st(x):
    return tuple(sorted(int(i) for i in x))


def graph(n, root=None):
    """This project's graph file (identical to the repository's lattice as labelled sets: declaration Sec. 1, T1)."""
    root = root or ROOT_DEFAULT
    G = rj(os.path.join(root, "phase3", "full_runs", "method", "code", "graphs", "hh_d%d.json" % {19: 3, 57: 5, 115: 7}[n]))
    eta = np.array(G["eta"], float)
    out = dict(n=G["n"], eta=eta, M0=float(eta.sum()), edges=[st(e) for e in G["edges"]], nn2=[st(e) for e in G["nn2"]],
               loops=[st(l) for l in G["loops12"]], local=G["local"])
    assert out["n"] == n and len(set(out["edges"])) == len(out["edges"]) and len(set(out["nn2"])) == len(out["nn2"])
    return out


def neel_values(G):
    """Neel values of Sec. 5: eta_i (sites), -1 (edges), +1 (second neighbours), +1 (loops)."""
    return dict(sites=G["eta"].copy(), edges=-np.ones(len(G["edges"])), second_neighbours=np.ones(len(G["nn2"])),
                loops=np.ones(len(G["loops"])))


def family_arrays(rec, G):
    """Values of one state (a parsed record) on the four families, in the item order of this project's graph file."""
    try:
        return dict(sites=np.array(rec["Z"], float), edges=np.array([rec["pairs"][e] for e in G["edges"]], float),
                    second_neighbours=np.array([rec["pairs"][e] for e in G["nn2"]], float),
                    loops=np.array([rec["loops"][l] for l in G["loops"]], float))
    except KeyError as ex:
        raise ValueError("a pair or loop of this project's graph is missing in the data file: %s" % (ex,))


def seven_labels(rec, G):
    """The seven label types of map/DECLARATION.md Sec. 0 for one parsed record."""
    f = family_arrays(rec, G); loc = G["local"]; n = G["n"]
    out = dict(m_s=float(f["sites"] @ G["eta"] / n), Czz_bar=float(f["edges"].mean()),
               C2_bar=float(f["second_neighbours"].mean()), Z_bulk=float(f["sites"][loc["bulk_site"]]),
               Z_boundary=float(f["sites"][loc["boundary_site"]]), Czz_edge=float(rec["pairs"][st(loc["edge"])]))
    out["Z_loop"] = float(rec["loops"][st(loc["loop"])]) if loc.get("loop") else None
    return out


# ------------------------------------------------------------------------------------------------ converted data
def jkey(j):
    return "%.1f" % float(j)


def _finite(a):
    a = np.asarray(a, float)
    if not np.all(np.isfinite(a)):
        raise ValueError("non-finite value in the data")
    return a


def _pairs(plist, vals, what):
    keys = [st(p) for p in plist]
    if len(keys) != len(vals) or len(set(keys)) != len(keys):
        raise ValueError("%s: pair list and values do not match one to one" % what)
    return dict(zip(keys, [float(v) for v in _finite(vals)]))


def parse_label_group(obj, group, n):
    """{Jz: record} for a label group of a converted file (schema p5-real-data-v1). Records of files without labels
    (skqd_post_select at n = 57) hold the energies only (has_labels False)."""
    out = {}
    for key, e in obj[group].items():
        J = round(float(key), 1)
        if "jz" in e and abs(float(e["jz"]) - J) > 1e-9:
            raise ValueError("%s %s: the jz field differs from the coupling of the file name" % (group, key))
        r = dict(Jz=J, E_real=float(e["final_global_energy"]), E_first=float(e["ground_state_energy"]),
                 has_labels="z_basis_opt" in e)
        if r["has_labels"]:
            Z = _finite(e["z_basis_opt"])
            if Z.shape != (n,):
                raise ValueError("%s %s: z_basis_opt has shape %s" % (group, key, Z.shape))
            r.update(Z=Z, M_real=float(Z.sum()),
                     pairs=_pairs(e["2_nn_corr_pairs_zz_basis_opt"], e["2_nn_corr_funcs_zz_basis_opt"], "%s %s" % (group, key)),
                     loops=_pairs(e["z_loop_sites"], e["z_loop"], "%s %s loops" % (group, key)))
        out[J] = r
    return out


def parse_dmrg(obj, n):
    """{Jz: record} of the authors' DMRG (group 'dmrg')."""
    out = {}
    for key, e in obj["dmrg"].items():
        J = round(float(key), 1)
        if "jz" in e and abs(float(e["jz"]) - J) > 1e-9:
            raise ValueError("dmrg %s: the jz field differs from the coupling of the file name" % key)
        Z = _finite(e["z"])
        if Z.shape != (n,):
            raise ValueError("dmrg %s: z has shape %s" % (key, Z.shape))
        out[J] = dict(Jz=J, E0=float(e["ground_state_energy"]), e1=float(e["e1"]), Z=Z, M=float(Z.sum()),
                      pairs=_pairs(e["2_nn_corr_pairs"], e["2_nn_corr_funcs_zz"], "dmrg %s" % key),
                      loops=_pairs(e["z_loop_sites"], e["z_loop"], "dmrg %s loops" % key))
    return out


def read_converted(n, gate, converted_dir=None):
    """The parsed JSON of converted/real_n<n>.json. Needs a Gate; checks the pinned SHA-256 of the file."""
    if not isinstance(gate, Gate):
        raise Refused("read_converted was called without a checked declaration hash.")
    name = "real_n%d.json" % n
    p = os.path.join(converted_dir or os.path.join(RD, "converted"), name)
    with open(p, "rb") as f:
        b = f.read()
    if hashlib.sha256(b).hexdigest() != PINNED[name]:
        raise Refused("%s does not have the SHA-256 pinned in the declaration." % p)
    obj = json.loads(b.decode("utf-8"))
    if obj.get("schema") != "p5-real-data-v1" or obj.get("n") != n:
        raise ValueError("unexpected schema in %s" % p)
    return obj


def project_refs(n, root=None):
    """This project's bond-dimension-320 references of the stored map: {Jz: E0} and {(Jz, label): O_GS}."""
    SM = rj(os.path.join(root or ROOT_DEFAULT, "phase3", "full_runs", "map", "laptop_analysis", "summary_map.json"))
    E0 = {round(r["Jz"], 1): float(r["E0"]) for r in SM["refs"].values() if r["n"] == n}
    O = {(round(r["Jz"], 1), r["label"]): float(r["O_GS"]) for r in SM["rows"] if r["n"] == n}
    return E0, O


def truth_table(dm, G, refs=None):
    """Sec. 0: 'O_GS and E0 are this project's references where stored, otherwise the authors' DMRG values'. Items of
    the four families are stored only in the authors' files, so they always come from there.
    dm: parse_dmrg output. refs: project_refs output or None (authors' values everywhere, as Sec. 7 prescribes)."""
    E0p, Op = refs if refs is not None else ({}, {})
    out = {}
    for J, r in dm.items():
        sv = seven_labels(r, G)
        lab, src = {}, {}
        for k in SEVEN:
            if (J, k) in Op:
                lab[k], src[k] = Op[(J, k)], "project"
            else:
                lab[k], src[k] = sv[k], "authors"
        out[J] = dict(Jz=J, E0=E0p.get(J, r["E0"]), E0_source="project" if J in E0p else "authors", E0_authors=r["E0"],
                      labels=lab, label_source=src, labels_authors=sv, families=family_arrays(r, G), Z=r["Z"],
                      orientation=float(np.sign(r["Z"] @ G["eta"])))
    return out


class RealData:
    """Everything the analyses of Secs. 5-7 need for one size: labels, energies, truth."""

    def __init__(self, n, lab, dm, G, refs, group):
        self.n, self.G, self.group = n, G, group
        self.lab = {J: r for J, r in lab.items()}
        self.truth = truth_table(dm, G, refs)                      # Sec. 0 rule
        self.truth_authors = truth_table(dm, G, None)              # Sec. 7: the authors' DMRG at all couplings
        self.Js = sorted(J for J in self.lab if J in self.truth)
        for J in self.Js:
            r, t = self.lab[J], self.truth[J]
            r["eps"] = r["E_real"] - t["E0"]; r["de"] = r["eps"] / n
            if r["has_labels"]:
                r["labels"] = seven_labels(r, G); r["families"] = family_arrays(r, G)
                r["q"] = (G["M0"] - r["M_real"]) / 2
                r["orientation"] = float(np.sign(r["Z"] @ G["eta"]))

    def labelled(self):
        return [J for J in self.Js if self.lab[J]["has_labels"]]


def from_objects(n, obj, G, refs, group="skqd_random_flip", exclude=()):
    lab = {J: r for J, r in parse_label_group(obj, group, n).items() if J not in set(exclude)}
    return RealData(n, lab, parse_dmrg(obj, n), G, refs, group)


def load_real(n, gate, root=None, converted_dir=None, group="skqd_random_flip"):
    """The dataset (group skqd_random_flip) or the comparison variant (skqd_post_select; at n = 115 without the four
    couplings excluded by gate G2). Needs a Gate."""
    obj = read_converted(n, gate, converted_dir)
    excl = G2_EXCLUDED_POST_SELECT_115 if (group == "skqd_post_select" and n == 115) else ()
    return from_objects(n, obj, graph(n, root), project_refs(n, root), group, excl)


def learning_dict(rd):
    """The dictionary D of learning_ibm/code/learn_ibm.py:load for the real labels.
    Z_lab = published site labels; Z_ref = the authors' DMRG (Sec. 7); eps = E_real - E0 with E0 of Sec. 0."""
    D = {}
    for J in rd.labelled():
        r = rd.lab[J]
        D[J] = dict(E0=rd.truth[J]["E0"], Z_lab=np.array(r["Z"], float), eps=r["eps"], Z_ideal=None, eps_ideal=None,
                    Z_ref=np.array(rd.truth_authors[J]["Z"], float))
    return rd.G["eta"], len(rd.G["edges"]), D


# ------------------------------------------------------------------------------------------------ conformal index
def k_index(m, alpha=ALPHA):
    """ceil((m + 1)(1 - alpha)), in exact rational arithmetic (alpha read as a decimal)."""
    return int(math.ceil(Fraction(m + 1) * (1 - Fraction(str(alpha)))))


# ------------------------------------------------------------------------------------------------ nested sets file
def choose_S_p(S, S34, S12, nmin=15):
    """Sec. 7 (f3): the most stringent of S_1/2, S_3/4, S that has at least nmin couplings; (None, None) if none."""
    for name, s in (("S_1_2", S12), ("S_3_4", S34), ("S", S)):
        if len(s) >= nmin:
            return name, list(s)
    return None, None


def split_sizes(m):
    """Sec. 7 (f3): |T| >= 20 -> 6 training, 12 calibration; 15 <= |T| < 20 -> 4, 9; below 15 the test is not run."""
    if m >= 20:
        return 6, 12
    if m >= 15:
        return 4, 9
    return None


def _iv(d):
    if d is None:
        return None
    lo, hi = float(d["lo"]), float(d["hi"])
    if not (math.isfinite(lo) and math.isfinite(hi) and lo <= hi):
        raise ValueError("an interval of the sets file is not ordered: %r" % (d,))
    return dict(d, lo=lo, hi=hi, width=hi - lo)


def parse_sets(obj, n, declaration_sha=None):
    """One size of the sets file (format: README_predict_learn.md). Returns dict(S, S_3_4, S_1_2, S_p, S_p_name,
    intervals={Jz: dict(tau, q, exact, lower, outer_like)}, warnings=[...]). Raises ValueError on an inconsistency
    that would change a decision."""
    if obj.get("schema") != SETS_SCHEMA:
        raise ValueError("sets file: schema is not %s" % SETS_SCHEMA)
    if declaration_sha is not None and str(obj.get("declaration_sha256", "")).lower() != declaration_sha:
        raise ValueError("sets file: it was not written under the hashed declaration")
    s = obj["sizes"][str(n)]
    grid = set(TRAIN_J)
    sets = {}
    for k in ("S", "S_3_4", "S_1_2", "S_p"):
        v = sorted(round(float(x), 1) for x in s[k])
        if len(set(v)) != len(v) or not set(v) <= grid:
            raise ValueError("sets file: %s is not a set of training couplings" % k)
        sets[k] = v
    if not (set(sets["S_1_2"]) <= set(sets["S_3_4"]) <= set(sets["S"])):
        raise ValueError("sets file: the sets are not nested")
    name, sp = choose_S_p(sets["S"], sets["S_3_4"], sets["S_1_2"])
    if (sp or []) != sets["S_p"]:
        raise ValueError("sets file: S_p is not the most stringent nested set with at least 15 couplings")
    iv, warn = {}, []
    for key, r in s["intervals"].items():
        J = round(float(key), 1)
        iv[J] = dict(Jz=J, tau=float(r["tau"]) if r.get("tau") is not None else None,
                     q=float(r["q"]) if r.get("q") is not None else None,
                     exact=_iv(r.get("exact")), lower=_iv(r.get("lower")), outer_like=_iv(r.get("outer_like")))
    frac = {"S": 1.0, "S_3_4": 0.75, "S_1_2": 0.5}
    for k, c in frac.items():
        for J in sets[k]:
            e = iv.get(J, {}).get("exact")
            if e is None:
                raise ValueError("sets file: Jz = %.1f is in %s but has no exact interval" % (J, k))
            t = iv[J]["tau"]
            if t is not None and e["width"] > c * t * (1 + 1e-9):
                raise ValueError("sets file: Jz = %.1f is in %s but its interval is %.4f tau wide" % (J, k, e["width"] / t))
        for J in sorted(grid - set(sets[k])):                    # completeness (float level: a warning only)
            e = iv.get(J, {}).get("exact"); t = iv.get(J, {}).get("tau")
            if e is not None and t is not None and e["width"] <= c * t * (1 - 1e-9):
                warn.append("Jz = %.1f has an exact interval %.4f tau wide but is not in %s" % (J, e["width"] / t, k))
    return dict(sets, S_p_name=name, intervals=iv, warnings=warn)


def load_sets(path=None, n=None, gate=None, require_sha=True):
    """Reads out/S_sets.json. With require_sha, out/S_sets.sha256 must exist and match (Sec. 7: 'written to a file with
    its SHA-256 before any learning number is computed')."""
    path = path or os.path.join(RD, "out", "S_sets.json")
    if require_sha:
        hp = os.path.splitext(path)[0] + ".sha256"
        if not os.path.exists(hp):
            raise Refused("%s does not exist: the nested sets are not fixed yet." % hp)
        with open(hp, encoding="utf-8") as f:
            m = HEX64.search(f.read())
        if not m or m.group(0).lower() != sha256_file(path):
            raise Refused("%s does not match %s." % (hp, path))
    obj = rj(path)
    return parse_sets(obj, n, gate.sha if gate is not None else None)


def prop2_intervals(Js, y, ystar, sets):
    """Label intervals for Proposition 2 of the cubic (Sec. 7, f1), in the structure of prop2_cubic.intervals:
    upper version ('outer') = the exact interval I of Sec. 2 where it exists; otherwise NOT AVAILABLE, and an
    indicative one is used and flagged: the like-for-like outer of the sets file where given, else a width
    interpolated log-linearly in Jz between the neighbouring couplings that have one (as prop2_cubic.interp_width),
    placed as [y - w, y + w] so that the stored score formula |f - y| + w is reproduced.
    lower version ('inner') = the interval of the explicit witness mixtures ((1 - q) x hull); None -> width 0."""
    iv = sets["intervals"]
    I = {}
    for J in Js:
        r = iv.get(J)
        if r is None:
            raise ValueError("sets file: no interval record at Jz = %.1f" % J)
        d = dict(upper_kind=None, indicative=False)
        if r["exact"] is not None:
            d.update(outer=[r["exact"]["lo"], r["exact"]["hi"]], upper_kind="exact")
        elif r["outer_like"] is not None:
            d.update(outer=[r["outer_like"]["lo"], r["outer_like"]["hi"]], upper_kind="like_for_like", indicative=True)
        if r["lower"] is not None:
            d.update(inner=[r["lower"]["lo"], r["lower"]["hi"]], w_in=r["lower"]["width"])
        else:
            d.update(inner=None, w_in=0.0)
        I[J] = d
    have = sorted(J for J in Js if I[J]["upper_kind"] is not None)
    for J in Js:
        d = I[J]
        if d["upper_kind"] is None:
            lo = [j for j in have if j < J]; hi = [j for j in have if j > J]
            if not lo or not hi:
                raise ValueError("no upper interval of any kind on both sides of Jz = %.1f" % J)
            a, b = lo[-1], hi[0]
            wa, wb = I[a]["outer"][1] - I[a]["outer"][0], I[b]["outer"][1] - I[b]["outer"][0]
            t = (J - a) / (b - a)
            w = math.exp((1 - t) * math.log(wa) + t * math.log(wb))
            d.update(outer=[y[J] - w, y[J] + w], w_out=w, upper_kind="interpolated", indicative=True, neighbours=[a, b])
        else:
            d["w_out"] = d["outer"][1] - d["outer"][0]
        olo, ohi = d["outer"]
        d.update(label_in_outer=bool(olo - 1e-12 <= y[J] <= ohi + 1e-12),
                 truth_in_outer=bool(olo - 1e-12 <= ystar[J] <= ohi + 1e-12))
    return I
