# real_data / tests / synth.py  (own code; 2026-11-12; task rd-code-learn)
#
# SYNTHETIC data in the schema of the converted files ("p5-real-data-v1"), with known answers. No real datum: the
# only project files read are the graph files and the n = 19 curves (exact diagonalization, no datum).
# Used by the tests; never by an analysis.
import hashlib
import json
import os
import shutil
import sys

import numpy as np

TESTS = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.join(os.path.dirname(TESTS), "code")
sys.dont_write_bytecode = True
sys.path.insert(0, CODE)
import rd_common as rdc  # noqa: E402
import rd_predict as rp  # noqa: E402

ROOT = rdc.ROOT_DEFAULT
REAL_RD = rdc.RD
N_NEG = {"edges": {57: 200, 115: 300}, "second_neighbours": {57: 217, 115: 100}}     # pairs with t = -0.1


def truth_fields(G, J):
    n = G["n"]; i = np.arange(n)
    c = 0.6 + 0.4 * ((i * 7) % 11) / 10.0
    Z = G["eta"] * (1 - c / (J ** 2 + 1.0))
    edges = np.array([-(1 - (0.8 + 0.2 * (k % 5) / 4) / (J ** 2 + 1.0)) for k in range(len(G["edges"]))])
    nn2 = np.array([+(1 - (1.2 + 0.3 * (k % 3) / 2) / (J ** 2 + 1.0)) for k in range(len(G["nn2"]))])
    loops = np.array([1 - (2.5 + 0.1 * k) / (J ** 2 + 2.5) for k in range(len(G["loops"]))])
    return Z, edges, nn2, loops


def de_of(J):
    return 0.02 / J


def ratio_of(J, n, ratio_dev=None):
    return (ratio_dev or {}).get((n, round(J, 1)), 1.0)


def build(n, C19, ratio_dev=None, seed=0):
    """(obj, expected): a synthetic converted object for size n and the answers it must give."""
    G = rdc.graph(n, ROOT)
    rng = np.random.default_rng(seed + n)
    Js = [k / 10 for k in range(11, 61)]
    obj = {"schema": "p5-real-data-v1", "n": n, "skqd_random_flip": {}, "skqd_post_select": {}, "dmrg": {}}
    neg = {fam: N_NEG[fam][n] for fam in N_NEG}
    count = {fam: 0 for fam in N_NEG}
    exp = dict(delta={}, m_gs={}, m_real={}, de={}, loops_t={}, D_sites={})
    for J in [1.0] + Js:
        Z, edges, nn2, loops = truth_fields(G, J)
        E0 = -0.4 * n * J
        pe = list(G["edges"]) + list(G["nn2"]); pv = list(edges) + list(nn2)
        perm = rng.permutation(len(pe))
        obj["dmrg"]["%.1f" % J] = {
            "jz": J, "ground_state_energy": E0, "e1": E0 + 0.5, "dmrg_params": {"chi_max": 320, "trunc_cut": 1e-6},
            "z": [float(x) for x in Z], "2_nn_corr_pairs": [[int(pe[i][1]), int(pe[i][0])] for i in perm],
            "2_nn_corr_funcs_zz": [float(pv[i]) for i in perm], "z_loop": [float(x) for x in loops],
            "z_loop_sites": [[int(s) for s in l] for l in G["loops"]], "_heavy_hex_ordered": True}
        if J == 1.0:
            continue
        m_gs = float(Z @ G["eta"] / n)
        de = de_of(J)
        delta = ratio_of(J, n, ratio_dev) * rp.curve_value(C19, J, de)
        Zr = Z + G["eta"] * delta
        t_e = np.full(len(edges), 0.2); t_2 = np.full(len(nn2), 0.3)
        for fam, t in (("edges", t_e), ("second_neighbours", t_2)):
            for k in range(len(t)):
                if count[fam] < neg[fam]:
                    t[k] = -0.1; count[fam] += 1
        t_l = 1.5 if J < 2.0 else 0.5
        er = edges + t_e * (-1 - edges); n2r = nn2 + t_2 * (1 - nn2); lr = loops + t_l * (1 - loops)
        pvr = list(er) + list(n2r)
        perm2 = rng.permutation(len(pe)); lperm = rng.permutation(len(G["loops"]))
        E = E0 + n * de
        obj["skqd_random_flip"]["%.1f" % J] = {
            "jz": J, "ground_state_energy": E + 1.0, "final_global_energy": E, "energy_vopt": E,
            "z_basis_opt": [float(x) for x in Zr],
            "2_nn_corr_pairs_zz_basis_opt": [[int(pe[i][0]), int(pe[i][1])] for i in perm2],
            "2_nn_corr_funcs_zz_basis_opt": [float(pvr[i]) for i in perm2],
            "z_loop": [float(lr[i]) for i in lperm],
            "z_loop_sites": [[int(s) for s in rng.permutation(list(G["loops"][i]))] for i in lperm]}
        ps = {"jz": J, "ground_state_energy": E + 1.0, "final_global_energy": E + 0.1, "energy_vopt": E + 0.1}
        if n == 115:                                       # as in the public files: the variant has labels at n = 115 only
            ps.update({k: v for k, v in obj["skqd_random_flip"]["%.1f" % J].items() if k not in ps})
        obj["skqd_post_select"]["%.1f" % J] = ps
        exp["delta"][J] = delta; exp["m_gs"][J] = m_gs; exp["m_real"][J] = m_gs + delta; exp["de"][J] = de
        exp["loops_t"][J] = t_l
        exp["D_sites"][J] = float(np.mean(abs(delta) / (0.06 * np.abs(Z))))
    exp["F"] = dict(sites=1.0, loops=1.0,
                    edges=1 - neg["edges"] / (50 * len(G["edges"])),
                    second_neighbours=1 - neg["second_neighbours"] / (50 * len(G["nn2"])))
    exp["loops_frac_t_le_1"] = 41 / 50
    return obj, exp, G


def sets_object(n, y, ystar, sha, width_frac=None, lower_frac=None, outer_like_at=()):
    """A synthetic sets file for one size: exact intervals centred on the truth at Jz >= 3.4 with widths
    width_frac(J) * tau; lower intervals everywhere; like-for-like outers at the couplings given."""
    width_frac = width_frac or (lambda J: 0.9 if J < 4.0 else (0.6 if J < 5.0 else 0.4))
    lower_frac = lower_frac or (lambda J: 3.0 if J < 3.0 else 0.3)
    iv = {}
    S, S34, S12 = [], [], []
    for J in sorted(y):
        tau = 0.06 * abs(ystar[J]); r = {"Jz": J, "tau": tau, "q": 0.01}
        wl = lower_frac(J) * tau
        r["lower"] = {"lo": ystar[J] - wl / 2, "hi": ystar[J] + wl / 2}
        if J >= 3.4:
            w = width_frac(J) * tau
            r["exact"] = {"lo": ystar[J] - w / 2, "hi": ystar[J] + w / 2, "certified": True}
            S.append(J)
            if width_frac(J) <= 0.75: S34.append(J)
            if width_frac(J) <= 0.5: S12.append(J)
        else:
            r["exact"] = None
        r["outer_like"] = {"lo": ystar[J] - 2 * tau, "hi": ystar[J] + 2 * tau} if J in outer_like_at else None
        iv["%.1f" % J] = r
    name, sp = rdc.choose_S_p(S, S34, S12)
    return {"S": S, "S_3_4": S34, "S_1_2": S12, "S_p": sp or [], "S_p_name": name, "intervals": iv}


def make_rd(tmp, C19_path, ratio_dev=None, hashed=True):
    """A synthetic real_data folder: DECLARATION.md (+ .sha256), converted/, out/n19, out/S_sets.json (+ .sha256).
    Returns (sha, expected answers per size). The caller patches rdc.RD and rdc.PINNED."""
    os.makedirs(os.path.join(tmp, "converted")); os.makedirs(os.path.join(tmp, "out", "n19"))
    with open(os.path.join(tmp, "DECLARATION.md"), "w", newline="\n") as f:
        f.write("# synthetic declaration for the unit tests\n")
    sha = rdc.sha256_file(os.path.join(tmp, "DECLARATION.md"))
    if hashed:
        with open(os.path.join(tmp, "DECLARATION.sha256"), "w") as f:
            f.write("%s *DECLARATION.md\n" % sha)
    shutil.copy(C19_path, os.path.join(tmp, "out", "n19", "n19_curves.json"))
    C19 = rdc.rj(C19_path)
    pinned, exp, sizes = {}, {}, {}
    for n in (57, 115):
        obj, e, G = build(n, C19, ratio_dev)
        s = json.dumps(obj)
        with open(os.path.join(tmp, "converted", "real_n%d.json" % n), "w", newline="\n") as f:
            f.write(s)
        pinned["real_n%d.json" % n] = hashlib.sha256(s.encode()).hexdigest()
        exp[n] = e
        sizes[str(n)] = sets_object(n, e["m_real"], e["m_gs"], sha, outer_like_at=(1.1, 1.6, 2.0, 3.0))
    sets = {"schema": rdc.SETS_SCHEMA, "declaration_sha256": sha, "label": "m_s", "sizes": sizes}
    sp = os.path.join(tmp, "out", "S_sets.json")
    with open(sp, "w", newline="\n") as f:
        f.write(json.dumps(sets, indent=1))
    with open(os.path.join(tmp, "out", "S_sets.sha256"), "w") as f:
        f.write("%s *S_sets.json\n" % rdc.sha256_file(sp))
    return sha, exp, pinned


class Checks:
    """A minimal test runner: named checks, a count, a non-zero exit code on any failure."""

    def __init__(self, title):
        self.title, self.n, self.bad = title, 0, []
        print("== " + title)

    def ok(self, cond, name):
        self.n += 1
        if not cond:
            self.bad.append(name)
        print("  [%s] %s" % ("ok" if cond else "FAIL", name))

    def close(self, a, b, name, tol=1e-12):
        self.ok(abs(a - b) <= tol * max(1.0, abs(a), abs(b)), "%s (%.12g against %.12g)" % (name, a, b))

    def raises(self, exc, fn, name):
        try:
            fn()
        except exc:
            self.ok(True, name); return
        except BaseException as ex:                      # noqa: BLE001
            self.ok(False, name + " (raised %r instead)" % (ex,)); return
        self.ok(False, name + " (nothing raised)")

    def done(self):
        print("%s: %d checks, %d failed%s" % (self.title, self.n, len(self.bad), (": " + "; ".join(self.bad)) if self.bad else ""))
        if self.bad:
            raise SystemExit(1)
