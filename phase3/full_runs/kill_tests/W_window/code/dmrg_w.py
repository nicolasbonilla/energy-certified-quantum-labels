"""Method (a): two-site DMRG (TeNPy 1.1.0) on the 4x6 torus at fixed bond dimension chi, from the Neel product state
(DECLARATION.md sec. 5a). Each final MPS is contracted to the full S^z = 0 vector and evaluated exactly with wlib.Ops.

  python dmrg_w.py <SB> <J2> <chi1,chi2,...> <tag>     -> out/methods/dmrg_<J2>_<tag>.json
Gate per state: |E_DMRG - E_exact(vector)| / n <= 1e-9 and 1 - norm^2 <= 1e-9 (else the state is flagged).
"""
import os
import sys
import time
import warnings

import numpy as np

import wlib

warnings.filterwarnings("ignore")


def build_model(J2):
    from tenpy.models.model import CouplingMPOModel
    from tenpy.networks.site import SpinHalfSite

    class J1J2Torus(CouplingMPOModel):
        def init_sites(self, p):
            return SpinHalfSite(conserve="Sz")

        def init_terms(self, p):
            J2v = p.get("J2", 0.0)
            for u1, u2, dx in self.lat.pairs["nearest_neighbors"]:
                self.add_coupling(1.0, u1, "Sz", u2, "Sz", dx)
                self.add_coupling(0.5, u1, "Sp", u2, "Sm", dx, plus_hc=True)
            if J2v != 0.0:
                for u1, u2, dx in self.lat.pairs["next_nearest_neighbors"]:
                    self.add_coupling(J2v, u1, "Sz", u2, "Sz", dx)
                    self.add_coupling(0.5 * J2v, u1, "Sp", u2, "Sm", dx, plus_hc=True)

    return J1J2Torus({"lattice": "Square", "Lx": 6, "Ly": 4, "bc_x": "periodic", "bc_y": "periodic",
                      "bc_MPS": "finite", "J2": float(J2)})


def mps_sites(M):
    """lattice site index (x*4 + y) of every MPS position"""
    out = []
    for p in range(M.lat.N_sites):
        x, y, u = M.lat.mps2lat_idx(p)
        out.append(int(x) * 4 + int(y))
    return out


def mps_to_vector(psi, site_of, basis, up_idx):
    L = psi.L
    T = np.ones((1, 1))
    for p in range(L):
        B = psi.get_B(p, form="B").transpose(["vL", "p", "vR"]).to_ndarray()
        T = np.tensordot(T, B, axes=([1], [0]))          # (2^p, 2, chiR)
        T = T.reshape(-1, B.shape[2])
    full = T.reshape(-1)
    idx = np.zeros(basis.size, dtype=np.int64)
    for p in range(L):
        up = (basis >> site_of[p]) & 1
        phys = np.where(up == 1, up_idx, 1 - up_idx)
        idx = idx * 2 + phys
    return full[idx]


def main(SB, J2, chis, tag):
    from tenpy.algorithms import dmrg
    from tenpy.networks.mps import MPS
    J2 = float(J2)
    od = os.path.join(SB, "out", "methods"); os.makedirs(od, exist_ok=True)
    out = os.path.join(od, "dmrg_%g_%s.json" % (J2, tag))
    lat = wlib.Lattice(6, 4)
    ops = wlib.Ops(lat, J2)
    M = build_model(J2)
    site_of = mps_sites(M)
    site = M.lat.mps_sites()[0]
    up_idx = site.state_labels["up"]
    labels = ["up" if lat.eps[site_of[p]] == 1 else "down" for p in range(M.lat.N_sites)]
    rows = []
    for chi in [int(c) for c in chis.split(",")]:
        t0 = time.time()
        psi = MPS.from_product_state(M.lat.mps_sites(), labels, bc="finite")
        params = {"mixer": True, "mixer_params": {"amplitude": 1e-5, "decay": 1.2, "disable_after": 15},
                  "max_E_err": 1e-11, "max_S_err": 1e-7, "min_sweeps": 6, "max_sweeps": 40, "max_trunc_err": 1.0,
                  "trunc_params": {"chi_max": chi, "svd_min": 1e-14}}
        eng = dmrg.TwoSiteDMRGEngine(psi, M, params)
        E, psi = eng.run()
        sec_dmrg = time.time() - t0
        v = mps_to_vector(psi, site_of, ops.basis, up_idx)
        ev = ops.evaluate(v)
        stats = eng.sweep_stats
        # E returned by the engine is that of the last two-site update before truncation; the gate compares the
        # MPO expectation value of the final (truncated) MPS with the exact evaluation of its full vector
        E_mpo = float(np.real(M.H_MPO.expectation_value(psi)))
        row = {"method": "MPS", "J2": J2, "label": "chi%d" % chi, "chi": chi, "E_dmrg": float(E), "E_mpo": E_mpo,
               "e_dmrg": float(E) / lat.n, "dE_check": E_mpo / lat.n - ev["e"], "norm2_sector": ev["norm2"],
               "max_chi_reached": int(max(psi.chi)), "sweeps": int(len(stats["E"])) if "E" in stats else None,
               "trunc_err": float(np.max(stats["max_trunc_err"][-1])) if "max_trunc_err" in stats else None,
               "sec": sec_dmrg, "sec_total": time.time() - t0, **ev}
        row["gate_ok"] = bool(abs(row["dE_check"]) <= 1e-9 and abs(1 - ev["norm2"]) <= 1e-9)
        rows.append(row)
        print(wlib.now(), "J2=%g chi=%d E/n=%.12f exact=%.12f diff=%.1e norm2=%.12f ms=%.8f dim=%.8f %.0fs" % (
            J2, chi, E / lat.n, ev["e"], row["dE_check"], ev["norm2"], ev["ms"], ev["dim"], row["sec_total"]),
            flush=True)
        wlib.dump(out, {"J2": J2, "rows": rows, "done": False})
    wlib.dump(out, {"J2": J2, "rows": rows, "done": True, "time": wlib.now()})


if __name__ == "__main__":
    main(*sys.argv[1:])
