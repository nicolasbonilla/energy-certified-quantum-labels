"""TeNPy side of the Huang-benchmark run (adapted from full_runs/map/code/hhmodel.py: same DMRG wrapper, state export and
evaluation pattern; new model).

H = sum_b J_b sigma_i . sigma_j = sum_b J_b [2 (S+_i S-_j + S-_i S+_j) + 4 Sz_i Sz_j] (Pauli units; S = sigma/2) on a
finite chain in the site order s = 5x + y, SpinHalfSite(conserve='Sz'). A label field adds -sign*lam*sum_p w_p
sigma_i . sigma_j / 3 (the field operator S*O of lattice.label_pairs).
"""
import os
import pickle
import time
import warnings
import json
import numpy as np

from tenpy.networks.site import SpinHalfSite
from tenpy.models.lattice import Chain
from tenpy.models.model import CouplingModel, MPOModel
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg
import tenpy

TENPY_VERSION = tenpy.__version__


def _add_sdot(model, coef, i, j):
    i, j = sorted((int(i), int(j)))
    if coef == 0 or i == j:
        return
    model.add_coupling_term(2.0 * coef, i, j, "Sp", "Sm")
    model.add_coupling_term(2.0 * coef, i, j, "Sm", "Sp")
    model.add_coupling_term(4.0 * coef, i, j, "Sz", "Sz")


class HeisModel(CouplingModel, MPOModel):
    def __init__(self, n, bonds, J, extra=None):
        site = SpinHalfSite(conserve="Sz")
        lat = Chain(n, site, bc="open", bc_MPS="finite")
        CouplingModel.__init__(self, lat)
        for (i, j), c in zip(bonds, J):
            _add_sdot(self, float(c), i, j)
        for (i, j), c in (extra or []):
            _add_sdot(self, float(c), i, j)
        MPOModel.__init__(self, lat, self.calc_H_MPO())


def field_terms(pairs, weights, sign, lam):
    """-sign*lam*S*O = -sign*lam*sum_p w_p C_p = sum_p (-sign*lam*w_p/3) sigma.sigma_p."""
    return [((i, j), -sign * lam * w / 3.0) for (i, j), w in zip(pairs, weights)]


def neel_labels(n, W=5):
    out = []
    for s in range(n):
        x, y = divmod(s, W)
        out.append("up" if (x + y) % 2 == 0 else "down")
    return out


def new_mps(M, labels):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*unit_cell_width.*")
        return MPS.from_product_state(M.lat.mps_sites(), labels, bc="finite")


def dmrg_opts(chi_max=None, chi_list=None, mixer=(1e-5, 2.0, 10), min_sweeps=3, max_sweeps=10, max_E_err=1e-9,
              svd_min=1e-10, max_hours=1.0, max_S_err=1e-5):
    """TeNPy 1.1.0 convergence: |Delta E| / max(E, 1) < max_E_err (absolute for E < 0) and |Delta S| < max_S_err."""
    o = {
        "trunc_params": {"chi_max": int(chi_max if chi_max else max(chi_list.values())), "svd_min": svd_min},
        "mixer": True,
        "mixer_params": {"amplitude": mixer[0], "decay": mixer[1], "disable_after": mixer[2]},
        "min_sweeps": min_sweeps, "max_sweeps": max_sweeps, "max_E_err": max_E_err, "max_hours": max_hours,
        "max_trunc_err": None, "max_S_err": max_S_err,
    }
    if chi_list:
        o["chi_list"] = {int(k): int(v) for k, v in chi_list.items()}
    return o


def run_dmrg(psi, M, opts):
    t0 = time.time()
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        eng = dmrg.TwoSiteDMRGEngine(psi, M, opts)
        E, psi = eng.run()
    ss = eng.sweep_stats
    nt = float(np.linalg.norm(psi.norm_test()))
    canon = False
    if nt > 1e-10:
        psi.canonical_form()
        canon = True
    st = dict(E_dmrg=float(E), sweeps=int(eng.sweeps), time_s=time.time() - t0,
              dE_last=float(ss["Delta_E"][-1]) if ss["Delta_E"] else None,
              max_trunc_err=float(np.max(ss["max_trunc_err"])) if ss["max_trunc_err"] else None,
              last_trunc_err=float(ss["max_trunc_err"][-1]) if ss["max_trunc_err"] else None,
              chi_max_reached=int(max(psi.chi)), norm_test_before=nt, canonicalized=canon,
              warnings=[str(w.message)[:300] for w in wl][:10])
    return psi, st


def tenpy_eval(psi, M0, pairs):
    """TeNPy-side evaluation at zero field: <psi|psi>, <H> (MPO), <C_ij> for the listed pairs, total charge."""
    E = float(np.real(M0.H_MPO.expectation_value(psi)))
    ov = complex(psi.overlap(psi))
    C = {}
    for (i, j) in pairs:
        i, j = sorted((i, j))
        zz = np.real(psi.expectation_value_term([("Sz", i), ("Sz", j)]))
        pm = np.real(psi.expectation_value_term([("Sp", i), ("Sm", j)]))
        mp = np.real(psi.expectation_value_term([("Sm", i), ("Sp", j)]))
        C["%d_%d" % (i, j)] = float((4.0 * zz + 2.0 * pm + 2.0 * mp) / 3.0)
    return dict(E=E, overlap=float(ov.real), C=C,
                total_charge_phys=[int(x) for x in np.asarray(psi.get_total_charge(only_physical_legs=True))],
                chi=[int(x) for x in psi.chi])


def export_tensors(psi):
    Ts = []
    for k in range(psi.L):
        B = psi.get_B(k, "B", copy=True)
        B.itranspose(["vL", "p", "vR"])
        Ts.append(np.asarray(B.to_ndarray()))
    Ts[0] = Ts[0] * psi.norm
    return Ts


def sz_basis(psi):
    return [float(x) for x in np.real(np.diag(psi.sites[0].Sz.to_ndarray()))]


def save_state(psi, prefix, meta, pkl=True):
    Ts = export_tensors(psi)
    meta = dict(meta)
    meta["sz_basis"] = sz_basis(psi)
    arrs = {"B%d" % k: T for k, T in enumerate(Ts)}
    tmp = prefix + ".tmp.npz"
    np.savez_compressed(tmp, meta=np.array(json.dumps(meta)), **arrs)
    os.replace(tmp, prefix + ".npz")
    if pkl:
        with open(prefix + ".pkl.tmp", "wb") as f:
            pickle.dump(psi, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(prefix + ".pkl.tmp", prefix + ".pkl")
    return Ts


def load_mps(prefix):
    with open(prefix + ".pkl", "rb") as f:
        return pickle.load(f)
