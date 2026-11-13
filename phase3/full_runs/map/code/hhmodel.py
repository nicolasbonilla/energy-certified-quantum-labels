"""TeNPy side of R2 pilot2 (copied from phase3/pilot_witness/code/hhmodel.py 1eb7b6ce...; one addition: label C2_bar).

H = 1/4 sum_edges (XX + YY + Jz ZZ) = sum_edges [1/2 (S+S- + S-S+) + Jz Sz Sz] on a finite chain in the MPS order of
the graph JSON, SpinHalfSite(conserve='Sz'). Optional fields: list of (coef, [mps sites]) meaning coef * prod Z.
"""
import json
import os
import pickle
import time
import warnings
import numpy as np

from tenpy.networks.site import SpinHalfSite
from tenpy.models.lattice import Chain
from tenpy.models.model import CouplingModel, MPOModel
from tenpy.networks.mps import MPS
from tenpy.algorithms import dmrg
import tenpy

TENPY_VERSION = tenpy.__version__


class HHModel(CouplingModel, MPOModel):
    def __init__(self, G, Jz, field=None):
        n = G["n"]
        site = SpinHalfSite(conserve="Sz")
        lat = Chain(n, site, bc="open", bc_MPS="finite")
        CouplingModel.__init__(self, lat)
        for (i, j) in G["mps"]["edges"]:
            self.add_coupling_term(0.5, i, j, "Sp", "Sm")
            self.add_coupling_term(0.5, i, j, "Sm", "Sp")
            self.add_coupling_term(float(Jz), i, j, "Sz", "Sz")
        for coef, sites in (field or []):
            sites = sorted(int(x) for x in sites)
            if coef == 0:
                continue
            if len(sites) == 1:
                self.add_onsite_term(float(coef), sites[0], "Sigmaz")
            elif len(sites) == 2:
                self.add_coupling_term(float(coef), sites[0], sites[1], "Sigmaz", "Sigmaz")
            else:
                self.add_multi_coupling_term(float(coef), sites, ["Sigmaz"] * len(sites), ["Id"] * (len(sites) - 1))
        MPOModel.__init__(self, lat, self.calc_H_MPO())


def label_terms(G, label):
    """Operator O of a label as a list of (coef, [mps sites]) with O = sum coef * prod Z."""
    pos = {v: k for k, v in enumerate(G["order"])}
    loc = G["local"]
    if label == "m_s":
        return [(float(G["mps"]["eta"][k]), [k]) for k in range(G["n"])]
    if label == "Z_bulk":
        return [(1.0, [pos[loc["bulk_site"]]])]
    if label == "Z_boundary":
        return [(1.0, [pos[loc["boundary_site"]]])]
    if label == "Czz_edge":
        a, b = loc["edge"]
        return [(1.0, sorted([pos[a], pos[b]]))]
    if label == "Z_loop":
        return [(1.0, sorted(pos[v] for v in loc["loop"]))]
    if label == "C2_bar":
        # field operator = sum over second-neighbour pairs of Z_i Z_j (the label is this sum / n_nn2)
        return [(1.0, sorted(int(x) for x in p)) for p in G["mps"]["nn2"]]
    raise ValueError(label)


def field_for(G, label, sign, lam):
    """Field terms of H - sign*lam*O."""
    return [(-sign * lam * c, s) for c, s in label_terms(G, label)]


def product_state(G, kind="neel"):
    """Labels per MPS site. kind: 'neel' | 'swap_edge' (declared edge swapped) | 'sz_minus' | 'sz_plus'."""
    n = G["n"]
    up = list(G["mps"]["up_init"])
    pos = {v: k for k, v in enumerate(G["order"])}
    mid = (n - 1) / 2.0
    if kind == "swap_edge":
        a, b = G["local"]["edge"]
        ka, kb = pos[a], pos[b]
        assert up[ka] != up[kb]
        up[ka], up[kb] = up[kb], up[ka]
    elif kind == "sz_minus":
        k = min((k for k in range(n) if up[k] == 1), key=lambda k: (abs(k - mid), k))
        up[k] = 0
    elif kind == "sz_plus":
        k = min((k for k in range(n) if up[k] == 0), key=lambda k: (abs(k - mid), k))
        up[k] = 1
    elif kind != "neel":
        raise ValueError(kind)
    return ["up" if u else "down" for u in up]


def new_mps(M, labels):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*unit_cell_width.*")
        return MPS.from_product_state(M.lat.mps_sites(), labels, bc="finite")


def dmrg_opts(chi_max=None, chi_list=None, mixer=(1e-5, 2.0, 10), min_sweeps=3, max_sweeps=10, max_E_err=1e-9,
              svd_min=1e-10, max_hours=1.0):
    o = {
        "trunc_params": {"chi_max": int(chi_max if chi_max else max(chi_list.values())), "svd_min": svd_min},
        "mixer": True,
        "mixer_params": {"amplitude": mixer[0], "decay": mixer[1], "disable_after": mixer[2]},
        "min_sweeps": min_sweeps, "max_sweeps": max_sweeps, "max_E_err": max_E_err, "max_hours": max_hours,
    }
    if chi_list:
        o["chi_list"] = {int(k): int(v) for k, v in chi_list.items()}
    return o


def run_dmrg(psi, M, opts, ortho=None):
    t0 = time.time()
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        eng = dmrg.TwoSiteDMRGEngine(psi, M, opts, orthogonal_to=ortho if ortho else None)
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


def tenpy_eval(psi, G, Jz, M0=None):
    """TeNPy-side exact evaluation at lambda = 0: <psi|psi>, <H> (MPO contraction), <Z_i>, m_s, local labels, charge."""
    if M0 is None:
        M0 = HHModel(G, Jz)
    n = G["n"]
    E = float(np.real(M0.H_MPO.expectation_value(psi)))
    ov = complex(psi.overlap(psi))
    Zm = np.real(np.asarray(psi.expectation_value("Sigmaz")))
    eta = np.array(G["mps"]["eta"], dtype=float)
    pos = {v: k for k, v in enumerate(G["order"])}
    loc = G["local"]
    out = dict(E=E, overlap=float(ov.real), overlap_imag=float(ov.imag), m_s=float(eta @ Zm / n),
               Z_mps=[float(x) for x in Zm], total_charge=[int(x) for x in np.asarray(psi.get_total_charge())],
               total_charge_phys=[int(x) for x in np.asarray(psi.get_total_charge(only_physical_legs=True))],
               chi=[int(x) for x in psi.chi], norm_attr=float(psi.norm))
    out["Z_bulk"] = float(Zm[pos[loc["bulk_site"]]])
    out["Z_boundary"] = float(Zm[pos[loc["boundary_site"]]])
    a, b = sorted([pos[x] for x in loc["edge"]])
    out["Czz_edge_loc"] = float(np.real(psi.expectation_value_term([("Sigmaz", a), ("Sigmaz", b)])))
    if loc.get("loop"):
        sl = sorted(pos[v] for v in loc["loop"])
        out["Z_loop"] = float(np.real(psi.expectation_value_term([("Sigmaz", k) for k in sl])))
    return out


def export_tensors(psi):
    """Raw dense tensors (vL, p, vR), norm folded into the first one."""
    Ts = []
    for k in range(psi.L):
        B = psi.get_B(k, "B", copy=True)
        B.itranspose(["vL", "p", "vR"])
        Ts.append(np.asarray(B.to_ndarray()))
    Ts[0] = Ts[0] * psi.norm
    return Ts


def site_basis_meta(psi):
    site = psi.sites[0]
    return dict(sz_basis=[float(x) for x in np.real(np.diag(site.Sz.to_ndarray()))],
                state_labels={str(k): int(v) for k, v in site.state_labels.items()})


def save_pkl(psi, path):
    with open(path + ".tmp", "wb") as f:
        pickle.dump(psi, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(path + ".tmp", path)


def save_state(psi, path_prefix, meta, pkl=True):
    """Write <prefix>.npz (raw dense tensors + meta JSON) and, if pkl, <prefix>.pkl (TeNPy MPS, for warm starts)."""
    Ts = export_tensors(psi)
    meta = dict(meta)
    meta.update(site_basis_meta(psi))
    arrs = {"B%d" % k: T for k, T in enumerate(Ts)}
    tmp = path_prefix + ".tmp.npz"
    np.savez_compressed(tmp, meta=np.array(json.dumps(meta)), **arrs)
    os.replace(tmp, path_prefix + ".npz")
    if pkl:
        save_pkl(psi, path_prefix + ".pkl")
    return Ts


def load_mps(path_prefix):
    with open(path_prefix + ".pkl", "rb") as f:
        return pickle.load(f)
