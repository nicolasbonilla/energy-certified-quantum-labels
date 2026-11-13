"""Diagnostic of the failed G1 tolerance (DEVIATIONS.md item 1). n = 19 only, no target model.
Is the 4e-5 difference a bug of the disordered code, or the time-step error of the evolution used by the method run?
Compares max_i |<Z_i>_MPS - <Z_i>_exact| for: (a) the unchanged tn.krylov_states at J_e = 1; (b) ft.dis_krylov_states at J_e = 1;
(c) ft.dis_krylov_states at disordered J_e; each with nsub = 2 (the declared value), 4 and 8. A second-order method must fall
about 4x per doubling of nsub; a wrong coupling would not fall at all."""
import os
import sys

import numpy as np
from scipy.sparse.linalg import expm_multiply

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import emu2  # noqa: E402
import ft  # noqa: E402
import ftlib as fl  # noqa: E402
import tn  # noqa: E402

g = emu2.load_graph(os.path.join(fl.HERE, "graphs", "hh_d3.json"))
G = fl.graph_json(3)
pos = {v: k for k, v in enumerate(g["order"])}
dt, Jz, Kst = 0.057, 2.5, 10


def exact_Z(J):
    inst = fl.make_instance(G, range(19), J, "t")
    sec = fl.sector(19, inst["n_down"])
    H = fl.build_H(sec, inst["edges"], inst["J"], Jz)
    v = np.zeros(sec.dim, complex)
    v[int(np.searchsorted(sec.cfg, sum(1 << i for i in range(19) if inst["eta"][i] == -1)))] = 1
    out = []
    for _ in range(Kst):
        v = expm_multiply((-1j * dt) * H, v)
        out.append((np.abs(v) ** 2) @ sec.Zc)
    return out


def err(gen, Zx):
    e = []
    for (k, psi, inf), z in zip(gen, Zx):
        Zm = np.real(np.asarray(psi.expectation_value("Sigmaz")))
        e.append(float(np.abs(np.array([Zm[pos[i]] for i in range(19)]) - z).max()))
    return e


one = np.ones(20)
dis = np.random.default_rng(9).uniform(.5, 1.5, 20)
Zu, Zd = exact_Z(one), exact_Z(dis)
for nsub in (2, 4, 8):
    a = err(tn.krylov_states(g, Jz, dt, Kst, chi_max=128, nsub=nsub), Zu)
    b = err(ft.dis_krylov_states(g, Jz, one, dt, Kst, chi_max=128, nsub=nsub), Zu)
    c = err(ft.dis_krylov_states(g, Jz, dis, dt, Kst, chi_max=128, nsub=nsub), Zd)
    print("nsub %d  unchanged tn, J=1: max %.3e | new code, J=1: max %.3e | new code, disordered: max %.3e (at k=4 %.3e)" % (
        nsub, max(a), max(b), max(c), c[3]), flush=True)
