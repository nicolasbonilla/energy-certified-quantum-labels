"""Second attempt at the basis-optimization step of arXiv:2606.15983 (Methods "Basis optimization"; Supp. II.3,
II.3.1), n <= 64 (uint64 configurations; pilot3's emu.py is reused for the subspace algebra).

Stated in the paper (implemented literally):
  H'(theta) = U H U^dag, C(theta) = <psi~|H'|psi~> with the SKQD vector fixed (Eqs. 7-10); U = one layer of
  CNOT(c->t) . RY_t(theta) . CNOT(c->t) blocks (= exp(-i theta/2 Z_c Y_t)) tiled over the heavy-hex edges in the
  optimal 3-colouring; gradient dC/dtheta_i analytic; local optimization on the 100 most probable bitstrings with
  global checks, tolerance 1e-8, <= 30 rounds, stop if the global cost increases; then re-diagonalization of
  H'_B(theta*) in the same subspace (Eq. 11).
Unspecified (choices declared): orientation of each block (control on the minority or the majority colour);
  per-gate vs one shared angle ("the optimal parameter theta" vs dC/dtheta_i): both run; initialization (0 and three
  random scales); exact (untruncated) Pauli propagation; whether labels are read off psi' or U^dag psi': both kept.
Alternatives (NOT the stated circuit; reported as such): RY on the control wire (generator Y_c X_t) and a
  number-conserving Givens block exp(-i phi/4 (X_c Y_t - Y_c X_t)).
"""
import json
import numpy as np
from scipy.optimize import minimize, minimize_scalar

import emu


def graph64(G):
    return emu.load_graph(G)


# gate = (xg, zg, cg, param, scale): rotation exp(-i (scale * phi[param]) / 2 * P), P = cg X^xg Z^zg (Z first)
def gates_for(g, kind, orientation="minority_control", shared=False):
    base = emu.bo_gates(g, orientation)
    gates = []
    for p, (c, t, sl) in enumerate(base):
        q = 0 if shared else p
        if kind == "ZY":       # stated circuit: CNOT RY_t CNOT = exp(-i th/2 Z_c Y_t);  Z_c Y_t = i X_t Z_c Z_t
            gates.append((1 << t, (1 << c) | (1 << t), 1j, q, 1.0))
        elif kind == "YX":     # RY on the control wire: exp(-i th/2 Y_c X_t);  Y_c X_t = i X_c X_t Z_c
            gates.append(((1 << c) | (1 << t), 1 << c, 1j, q, 1.0))
        elif kind == "GV":     # Givens: exp(-i phi/4 X_c Y_t) exp(+i phi/4 Y_c X_t)
            gates.append(((1 << c) | (1 << t), 1 << t, 1j, q, 0.5))
            gates.append(((1 << c) | (1 << t), 1 << c, 1j, q, -0.5))
        else:
            raise ValueError(kind)
    npar = 1 if shared else len(base)
    return gates, npar


def propagate(terms, gates):
    """U O U^dag for U = prod_g exp(-i th_g/2 P_g) (gate 0 acts first). Returns dict (x, z) -> monomials
    (real coefficient, cosmask, sinmask) over gate indices."""
    cur = {}
    for (c, x, z) in terms:
        cur.setdefault((x, z), []).append((complex(c), 0, 0))
    for gi, (xg, zg, cg, _, _) in enumerate(gates):
        bit = 1 << gi
        new = {}
        for (x, z), monos in cur.items():
            if emu.anticommute(x, z, xg, zg):
                new.setdefault((x, z), []).extend((m[0], m[1] | bit, m[2]) for m in monos)
                c2, x2, z2 = emu.mult(1.0, x, z, cg, xg, zg)
                fac = 1j * c2
                new.setdefault((x2, z2), []).extend((m[0] * fac, m[1], m[2] | bit) for m in monos)
            else:
                new.setdefault((x, z), []).extend(monos)
        cur = new
    out = {}
    for k, monos in cur.items():
        acc = {}
        for (c, cm, sm) in monos:
            assert abs(c.imag) < 1e-12, c
            acc[(cm, sm)] = acc.get((cm, sm), 0.0) + c.real
        out[k] = [(v, cm, sm) for (cm, sm), v in acc.items() if abs(v) > 1e-15]
    return {k: v for k, v in out.items() if v}


class Param:
    """Gate angles theta = A phi (sparse map)."""

    def __init__(self, gates, npar):
        self.ng = len(gates); self.npar = npar
        self.pi = np.array([q for (_, _, _, q, _) in gates]); self.sc = np.array([s for (*_, s) in gates])

    def theta(self, phi):
        return self.sc * np.asarray(phi)[self.pi]

    def grad(self, gth):
        return np.bincount(self.pi, weights=self.sc * gth, minlength=self.npar)


class Problem:
    def __init__(self, C, alpha, g, Jz, kind, orientation, shared):
        self.gates, self.npar = gates_for(g, kind, orientation, shared)
        self.P = Param(self.gates, self.npar)
        strings = emu.sector_relevant(propagate(emu.H_terms(g, Jz), self.gates))
        self.op = emu.GroupedOp(strings, len(self.gates))
        self.C, self.alpha = C, alpha
        self.e = self.op.string_expectations(C, alpha)
        self.n_strings = self.op.n_strings

    def f(self, phi, e=None):
        v, gth = self.op.value_and_grad(self.P.theta(phi), self.e if e is None else e)
        return v, self.P.grad(gth)


def lbfgs(fun, x0, maxiter=500):
    r = minimize(fun, x0, jac=True, method="L-BFGS-B", options=dict(maxiter=maxiter, gtol=1e-10, ftol=1e-14))
    return r.x, float(r.fun), int(r.nit)


def opt_pergate(pb, rng, scales=(1e-3, 0.1, 0.3, 1.0)):
    best = None; runs = []
    for s in scales:
        x0 = np.full(pb.npar, s) if s == 1e-3 else rng.normal(0, s, pb.npar)
        x, fv, it = lbfgs(pb.f, x0)
        runs.append(dict(init_scale=s, C=fv, nit=it, phi_rms=float(np.sqrt(np.mean(x ** 2)))))
        if best is None or fv < best[1]:
            best = (x, fv)
    return best[0], best[1], runs


def opt_shared(pb):
    span = 2 * np.pi if max(abs(pb.P.sc)) < 1 else np.pi
    grid = np.linspace(-span, span, 721)
    vals = np.array([pb.f(np.array([t]))[0] for t in grid])
    i = int(np.argmin(vals))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    r = minimize_scalar(lambda t: pb.f(np.array([t]))[0], bounds=(lo, hi), method="bounded",
                        options=dict(xatol=1e-10))
    x = np.array([r.x]) if r.fun <= vals[i] else np.array([grid[i]])
    return x, float(min(r.fun, vals[i])), dict(grid_min=float(vals.min()), grid_at=float(grid[i]),
                                               C_at_0=float(pb.f(np.zeros(1))[0]))


def opt_procedure(pb, rng, ntop=100, scales=(0.0, 0.1, 0.3, 1.0)):
    """Supp. II.3.1 as written: local optimization on the ntop most probable bitstrings, global cost checks, then
    full optimization from the local parameters; <= 30 rounds; stop on increase or when the decrease < 1e-8."""
    top = np.argsort(-np.abs(pb.alpha))[:ntop]
    Cs = pb.C[top]
    o = np.argsort(Cs)
    Cs = Cs[o]; aS = pb.alpha[top][o]; aS = aS / np.linalg.norm(aS)
    eS = pb.op.string_expectations(Cs, aS)
    best = None; runs = []
    for s in scales:
        phi = np.zeros(pb.npar) if s == 0 else rng.normal(0, s, pb.npar)
        Cg = pb.f(phi)[0]
        log = [dict(round=0, C_global=Cg)]
        for it in range(1, 31):
            loc, _, _ = lbfgs(lambda x: pb.f(x, eS), phi, maxiter=200)
            Cl = pb.f(loc)[0]
            if Cl > Cg:
                log.append(dict(round=it, C_global_after_local=Cl, stop="global cost increased"))
                break
            full, Cf, _ = lbfgs(pb.f, loc, maxiter=200)
            dec = Cg - Cf
            phi, Cg = full, Cf
            log.append(dict(round=it, C_global_after_local=Cl, C_global=Cf, decrease=dec))
            if dec < 1e-8:
                log[-1]["stop"] = "tolerance"
                break
        runs.append(dict(init_scale=s, C=Cg, rounds=len(log) - 1, log=log[-3:],
                         phi_rms=float(np.sqrt(np.mean(phi ** 2)))))
        if best is None or Cg < best[1]:
            best = (phi.copy(), Cg)
    return best[0], best[1], runs


def rotated_labels(C, psi, g, gates, theta):
    n = g["n"]
    Z = []
    for i in range(n):
        op = emu.GroupedOp(emu.sector_relevant(propagate([(1.0, 0, 1 << i)], gates)), len(gates))
        Z.append(op.expectation(C, psi, theta))
    Czz = []
    for (i, j) in g["pairs"]:
        op = emu.GroupedOp(emu.sector_relevant(propagate([(1.0, 0, (1 << i) | (1 << j))], gates)), len(gates))
        Czz.append(op.expectation(C, psi, theta))
    Z = np.array(Z)
    return dict(Z=Z.tolist(), Czz=Czz, Zloop=[], m_s=float(g["eta"] @ Z / n))


VARIANTS = [  # (name, kind, orientation, mode, stated circuit?)
    ("ZY_pergate_minority", "ZY", "minority_control", "pergate", True),
    ("ZY_pergate_majority", "ZY", "majority_control", "pergate", True),
    ("ZY_shared_minority", "ZY", "minority_control", "shared", True),
    ("ZY_shared_majority", "ZY", "majority_control", "shared", True),
    ("ZY_procedure_minority", "ZY", "minority_control", "procedure", True),
    ("ZY_procedure_majority", "ZY", "majority_control", "procedure", True),
    ("YX_pergate_minority", "YX", "minority_control", "pergate", False),
    ("YX_pergate_majority", "YX", "majority_control", "pergate", False),
    ("GV_pergate", "GV", "minority_control", "pergate", False),
]


def run_all(C, alpha, E_pre, g, Jz, ref, gap, rng, toy=False):
    import time
    H = emu.build_H(C, g, Jz)
    E_check = float(alpha @ (H @ alpha))
    out = dict(D=int(len(C)), E_pre=E_pre, E_pre_check=E_check, ratio_pre=(E_pre - ref["E0"]) / gap, variants={})
    lab_pre = emu.diag_labels(C, alpha, g)
    out["pre"] = dict(labels=lab_pre, err=emu.label_errors(lab_pre, ref["labels"]))
    for (name, kind, orient, mode, stated) in VARIANTS:
        t0 = time.time()
        pb = Problem(C, alpha, g, Jz, kind, orient, mode == "shared")
        C0 = pb.f(np.zeros(pb.npar))[0]
        if mode == "pergate":
            phi, Copt, runs = opt_pergate(pb, rng)
        elif mode == "shared":
            phi, Copt, runs = opt_shared(pb)
        else:
            phi, Copt, runs = opt_procedure(pb, rng)
        th = pb.P.theta(phi)
        Hp = pb.op.matrix(C, th)
        asym = float(abs(Hp - Hp.T).max()) if Hp.nnz else 0.0
        Ebo, psi = emu.ground(Hp, v0=alpha)
        if alpha @ psi < 0:
            psi = -psi
        res = dict(kind=kind, orientation=orient, mode=mode, stated_circuit=stated, n_strings=pb.n_strings,
                   n_params=pb.npar, C_at_0=C0, C_opt=Copt, E_bo=Ebo, ratio_bo=(Ebo - ref["E0"]) / gap,
                   f_reduction=1.0 - (Ebo - ref["E0"]) / (E_pre - ref["E0"]), theta_rms=float(np.sqrt(np.mean(th ** 2))),
                   theta_max=float(np.max(np.abs(th))), asym=asym, runs=runs)
        if Ebo < E_pre - 1e-9:
            lab_u = emu.diag_labels(C, psi, g)
            res["E_of_psi_unrotated_H"] = float(psi @ (H @ psi))
            res["unrot"] = dict(labels=lab_u, err=emu.label_errors(lab_u, ref["labels"]))
            lab_r = rotated_labels(C, psi, g, pb.gates, th)
            res["rot"] = dict(labels=lab_r, err=emu.label_errors(lab_r, ref["labels"]))
        res["secs"] = time.time() - t0
        out["variants"][name] = res
        print("bo", Jz, name, "C0 %.6f Copt %.6f Ebo %.6f f %.4f th_rms %.2e %.0fs" % (
            C0, Copt, Ebo, res["f_reduction"], res["theta_rms"], res["secs"]), flush=True)
    return out
