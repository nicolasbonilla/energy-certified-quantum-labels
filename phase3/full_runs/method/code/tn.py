"""TeNPy side of the R4 pilot: DMRG references, exact-evolution Krylov states (two-site TDVP), MPS export."""
import time
import warnings
import numpy as np

import hhmodel
from hhmodel import HHModel, product_state, new_mps, dmrg_opts, run_dmrg


def down_index(psi):
    sz = np.real(np.diag(psi.sites[0].Sz.to_ndarray()))
    return int(np.argmin(sz))


def export(psi):
    Ts = hhmodel.export_tensors(psi)
    return [np.asarray(T, dtype=complex) for T in Ts]


def mps_labels(psi, g):
    """Exact MPS labels in graph-node indexing: Z_i, C_zz on g['pairs'], loops, m_s."""
    G = g["G"]
    order = g["order"]
    pos = {v: k for k, v in enumerate(order)}
    Zm = np.real(np.asarray(psi.expectation_value("Sigmaz")))
    Z = np.zeros(g["n"])
    for k, v in enumerate(order):
        Z[v] = Zm[k]
    Czz = []
    for (i, j) in g["pairs"]:
        a, b = sorted([pos[i], pos[j]])
        Czz.append(float(np.real(psi.expectation_value_term([("Sigmaz", a), ("Sigmaz", b)]))))
    loops = []
    for lp in g["loops"]:
        sl = sorted(pos[v] for v in lp)
        loops.append(float(np.real(psi.expectation_value_term([("Sigmaz", k) for k in sl]))))
    return dict(Z=Z.tolist(), Czz=Czz, Zloop=loops, m_s=float(g["eta"] @ Z / g["n"]))


def dmrg_ground(g, Jz, chi_list, max_sweeps=14, kind="neel", min_sweeps=4, max_E_err=1e-9):
    G = g["G"]
    M = HHModel(G, Jz)
    psi = new_mps(M, product_state(G, kind))
    opts = dmrg_opts(chi_list=chi_list, min_sweeps=min_sweeps, max_sweeps=max_sweeps, max_E_err=max_E_err,
                     max_hours=3.0)
    psi, st = run_dmrg(psi, M, opts)
    E = float(np.real(M.H_MPO.expectation_value(psi)))
    return psi, E, st


def krylov_states(g, Jz, dt, K, chi_max=128, nsub=2, svd_min=1e-12):
    """Yield (k, psi_k, info) for |psi_k> = exp(-i H k dt)|Neel>, k = 1..K. Exact (non-Trotter) evolution by the
    TeNPy W^II MPO method, order 2, nsub sub-steps per dt (toy check: infidelity <= 3e-7 at k = 10, nsub = 2)."""
    from tenpy.algorithms.mpo_evolution import ExpMPOEvolution
    G = g["G"]
    M = HHModel(G, Jz)
    psi = new_mps(M, product_state(G, "neel"))
    for k in range(len(psi._B)):
        psi._B[k] = psi._B[k].astype(np.complex128)
    opts = {"dt": dt / nsub, "N_steps": nsub, "order": 2, "approximation": "II", "compression_method": "SVD",
            "trunc_params": {"chi_max": chi_max, "svd_min": svd_min}}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        eng = ExpMPOEvolution(psi, M, opts)
        for k in range(1, K + 1):
            t0 = time.time()
            eng.run()
            yield k, psi, dict(t=float(eng.evolved_time), chi=int(max(psi.chi)), secs=time.time() - t0,
                               trunc=float(eng.trunc_err.eps))


def dense_vector(psi, g):
    """Toy only: MPS -> vector in the emu basis (index sum_i bit_i 2^i, bit 1 = down)."""
    n = g["n"]
    th = psi.get_theta(0, n).to_ndarray().reshape([2] * n)
    di = down_index(psi)
    v = np.zeros(1 << n, dtype=complex)
    for idx in np.ndindex(*([2] * n)):
        b = 0
        for k, p in enumerate(idx):
            if p == di:
                b |= 1 << g["order"][k]
        v[b] = th[idx]
    return v * psi.norm
