"""Explicit Toeplitz-Hausdorff pure witness from two stored MPS (R1 item C6). Laptop; numpy only (no TeNPy).

Given two in-sector MPS a, b (raw npz of the run) and the mixture rho = (1-t)|a><a| + t|b><b| of the inner hull, the
joint numerical range of (H, O) compressed to span{a, b} is a filled ellipse (Toeplitz-Hausdorff) containing the
points of a and b, hence the segment between them, hence the mixture point. We find a unit vector
v = cos(th) e1 + exp(i ph) sin(th) e2 (e1, e2 an orthonormal basis of the span) with <v|H|v> = <H>_rho and
<v|O|v> = <O>_rho, build the pure MPS alpha*a + beta*b (direct sum, bond dimension chi_a + chi_b) and evaluate it
with the independent evaluator: energy, label, sector variance.

  python -I th_witness.py <graph.json> <Jz> <label> <npz_a> <t_a> <npz_b> <t_b> <E_thr> <out.json>
(t_a + t_b = 1 are the mixture weights). The 2x2 matrices of H and O in {a, b} come from evaluations of the direct
sums a + b and a + i b with the same evaluator (unnormalised expectation = value * norm).
"""
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indep_eval as IE  # noqa: E402

KEY = {"m_s": "m_s", "Czz_bar": "Czz_bar", "C2_bar": "C2_bar", "Z_bulk": "Z_bulk", "Z_boundary": "Z_boundary",
       "Czz_edge": "Czz_edge_loc", "Z_loop": "Z_loop"}


def direct_sum(A, B, ca, cb):
    """MPS of ca*A + cb*B (open boundary, same physical basis)."""
    n = len(A)
    out = []
    for k in range(n):
        a, b = A[k], B[k]
        dt = np.result_type(a, b, complex(ca), complex(cb))
        if k == 0:
            T = np.concatenate([ca * a, cb * b], axis=2).astype(dt)
        elif k == n - 1:
            T = np.concatenate([a, b], axis=0).astype(dt)
        else:
            T = np.zeros((a.shape[0] + b.shape[0], 2, a.shape[2] + b.shape[2]), dtype=dt)
            T[:a.shape[0], :, :a.shape[2]] = a
            T[a.shape[0]:, :, a.shape[2]:] = b
        out.append(T)
    return out


def ev(Ts, G, Jz, sz_basis, label):
    r = IE.evaluate(Ts, G, Jz, sz_basis, s=G["sz"], full=True)
    nrm = r["norm"]
    return dict(N=nrm, H=r["E"] * nrm, O=r[KEY[label]] * nrm, var=r["sector_var"], full=r)


def main(gpath, Jz, label, pa, ta, pb, tb, Ethr, outp):
    Jz, ta, tb, Ethr = float(Jz), float(ta), float(tb), float(Ethr)
    G = json.load(open(gpath))
    A, ma = IE.load_npz(pa)
    B, mb = IE.load_npz(pb)
    assert ma["sz_basis"] == mb["sz_basis"] and ma["order"] == G["order"]
    sz = ma["sz_basis"]
    Ea, Eb = ev(A, G, Jz, sz, label), ev(B, G, Jz, sz, label)
    S1 = ev(direct_sum(A, B, 1.0, 1.0), G, Jz, sz, label)
    Si = ev(direct_sum(A, B, 1.0, 1j), G, Jz, sz, label)
    M = {}
    for X in ("N", "H", "O"):
        re = 0.5 * (S1[X] - Ea[X] - Eb[X])          # Re <a|X|b>
        im = 0.5 * (Si[X] - Ea[X] - Eb[X])          # <a+ib|X|a+ib> = Xaa + Xbb + 2 Re(i Xab) = ... - 2 Im Xab
        xab = re - 1j * im
        M[X] = np.array([[Ea[X], xab], [np.conj(xab), Eb[X]]], dtype=complex)
    # orthonormal basis of the span: columns of C express e1, e2 in terms of (a, b)
    Nm = M["N"]
    w, U = np.linalg.eigh(Nm)
    C = U @ np.diag(1 / np.sqrt(w)) @ U.conj().T            # Loewdin: C^dag N C = 1
    Ht = C.conj().T @ M["H"] @ C
    Ot = C.conj().T @ M["O"] @ C
    Emix = ta * Ea["H"] / Ea["N"] + tb * Eb["H"] / Eb["N"]
    Omix = ta * Ea["O"] / Ea["N"] + tb * Eb["O"] / Eb["N"]

    def f(x):
        th, ph = x
        v = np.array([np.cos(th), np.exp(1j * ph) * np.sin(th)])
        return np.array([np.real(v.conj() @ Ht @ v) - Emix, np.real(v.conj() @ Ot @ v) - Omix])
    from scipy.optimize import least_squares
    best = None
    for th0 in np.linspace(0.05, np.pi / 2 - 0.05, 7):
        for ph0 in np.linspace(0, 2 * np.pi, 9)[:-1]:
            r = least_squares(f, [th0, ph0], xtol=1e-15, ftol=1e-15, gtol=1e-15)
            if best is None or np.max(np.abs(r.fun)) < np.max(np.abs(best.fun)):
                best = r
    th, ph = best.x
    v = np.array([np.cos(th), np.exp(1j * ph) * np.sin(th)])
    coef = C @ v                                             # coefficients on (a, b)
    P = direct_sum(A, B, coef[0], coef[1])
    r = IE.evaluate(P, G, Jz, sz, s=G["sz"], full=True)
    out = dict(graph=gpath, Jz=Jz, label=label, npz_a=pa, npz_b=pb, t_a=ta, t_b=tb, E_thr=Ethr,
               E_a=Ea["H"] / Ea["N"], E_b=Eb["H"] / Eb["N"], O_a=Ea["O"] / Ea["N"], O_b=Eb["O"] / Eb["N"],
               overlap_ab=complex(M["N"][0, 1] / np.sqrt(Ea["N"] * Eb["N"])).__repr__(),
               H_ab=complex(M["H"][0, 1]).__repr__(), O_ab=complex(M["O"][0, 1]).__repr__(),
               E_mix=Emix, O_mix=Omix, residual_2x2=float(np.max(np.abs(best.fun))),
               coef_a=repr(complex(coef[0])), coef_b=repr(complex(coef[1])),
               chi_a=int(max(T.shape[2] for T in A)), chi_b=int(max(T.shape[2] for T in B)),
               chi_pure=int(max(T.shape[2] for T in P)),
               pure=dict(E=r["E"], O=r[KEY[label]], norm=r["norm"], sector_var=r["sector_var"], m_s=r["m_s"]),
               dE_pure_mix=r["E"] - Emix, dO_pure_mix=r[KEY[label]] - Omix, below_threshold=bool(r["E"] <= Ethr))
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("graph",)}, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:])
