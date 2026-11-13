"""break_PU.py -- referee attack on Proposition U (unpinned order). Own code; models the writer did not use:
Heisenberg ladders with unequal rung coupling, a 3-leg ladder, frustrated J1-J2 rings and chains, an easy-plane
XXZ ring, a random-bond XXZ ring with Dzyaloshinskii-Moriya terms (complex Hamiltonian: only an ANTIUNITARY F),
and a non-diagonal label (dimer order, F = translation, terms o_i that do not commute with each other).

For each model: hypotheses (<O> = <O^3> = 0, non-degenerate sector ground state), D_n by the explicit double
commutator, the trial energy identity, the explicit state psi_theta (label and energy), and the exact E*_n(c)
through the conjugate function (dual value = rigorous lower bound, explicit state = upper bound).
A violation would be:  dual lower bound on E*_n(c)  >  the bound of the proposition.
"""
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from bl_common import sector, zvals, build, swap_op, conj_cost

t00 = time.time()
rng = np.random.default_rng(7)
VIOL = []
ROWS = []


def lowest_sp(H, k=2, v0=None):
    dim = H.shape[0]
    if dim <= 400:
        w, v = np.linalg.eigh(H.toarray())
        return w[:k], v[:, 0]
    w, v = sla.eigsh(H, k=k, which="SA", tol=1e-12, v0=v0, ncv=min(dim - 1, 40), maxiter=50000)
    o = np.argsort(w)
    return w[o][:k], v[:, o[0]]


def ev(A, v):
    return float(np.real(np.vdot(v, A @ v)))


def run(name, n_terms, H, O, cs=(0.1, 0.3, 0.5, 0.7, 0.9, 1.0), xy_check=None):
    """H, O sparse Hermitian matrices in the sector; the label is O / n_terms."""
    t0 = time.time()
    n = n_terms
    w, psi = lowest_sp(H, k=3)
    E0 = w[0]
    gap = w[1] - w[0]
    if gap < 1e-7:
        print(f"{name}: sector ground state DEGENERATE (splitting {gap:.1e}) -> hypothesis fails, proposition silent")
        return
    Opsi = O @ psi
    m1 = float(np.real(np.vdot(psi, Opsi)))
    m2 = float(np.real(np.vdot(Opsi, Opsi)))
    m3 = float(np.real(np.vdot(Opsi, O @ Opsi)))
    sig = np.sqrt(m2) / n
    # D_n by the explicit double commutator [O,[H,O]]
    C = H @ O - O @ H
    DC = O @ C - C @ O
    Dn = ev(DC, psi)
    herm = abs(DC - DC.getH()).max()
    phi = Opsi / np.sqrt(m2)
    e_trial = ev(H, phi) - E0
    id_err = abs(e_trial - Dn / (2 * n * n * sig * sig))
    extra = ""
    if xy_check is not None:
        extra = f"  D_n + 16<K_xy> = {Dn + 16 * ev(xy_check, psi):.1e}"
    print(f"{name}: dim {H.shape[0]}, gap {gap:.4f}, <O>/n = {m1 / n:.1e}, <O^3>/n^3 = {m3 / n ** 3:.1e}, sigma_n = {sig:.4f}, "
          f"D_n = {Dn:.5f} (>= 0: {Dn >= -1e-10}), trial-energy identity error {id_err:.1e}, [O,[H,O]] Hermitian to {herm:.0e}{extra}")
    if abs(m1) / n > 1e-8 or abs(m3) / n ** 3 > 1e-8:
        print("    hypothesis <O> = <O^3> = 0 NOT satisfied -> no F; skipped")
        return
    cache = {"v": psi}

    def Hfun_sign(sign):
        def Hfun(mu):
            ww, v = lowest_sp(H - sign * mu * O, k=2, v0=cache["v"])
            cache["v"] = v
            return ww[0], ev(O, v) / n, ev(H, v)
        return Hfun
    for c_rel in cs:
        c = c_rel * sig
        bound = Dn / (4 * n * n * sig * sig) * (1 - np.sqrt(max(0.0, 1 - c_rel ** 2)))
        # the explicit state of the proof
        th = 0.5 * np.arcsin(min(1.0, c_rel))
        pt = np.cos(th) * psi + np.sin(th) * phi
        o_pt = ev(O, pt) / n
        e_pt = ev(H, pt) - E0
        st_err = max(abs(o_pt - c), abs(e_pt - bound))
        for sign in ((+1, -1) if c_rel in (0.5, 1.0) else (+1,)):
            cache["v"] = psi
            dual, primal, mus = conj_cost(Hfun_sign(sign), E0, n, sign * c, sign, mu_hi=0.02, iters=48)
            viol = dual > bound * (1 + 1e-9) + 1e-11
            if viol:
                VIOL.append((name, c_rel, sign, dual, bound))
            ROWS.append((name, c_rel, sign, dual, primal, bound, bound / max(dual, 1e-300), st_err))
            print(f"    c/sigma = {c_rel:4.2f} sign {sign:+d}: E* in [{dual:.9f}, {primal:.9f}]  bound {bound:.9f}  "
                  f"bound/exact {bound / max(dual, 1e-300):9.3f}  psi_theta error {st_err:.1e}  {'VIOLATION' if viol else 'ok'}")
    print(f"    [{time.time() - t0:.0f} s]")


def model(n, nup, edges, J, hopfac=None, jzfac=None, fields=None):
    """Heisenberg-type: bond e has (J_e/4)(XX + YY) * hopfac_e + (J_e/4) jzfac_e ZZ; returns states, H (csr)."""
    st = sector(n, nup)
    J = np.broadcast_to(np.asarray(J, float), (len(edges),))
    hop = 0.5 * J * (1.0 if hopfac is None else np.asarray(hopfac))
    jz = J * (1.0 if jzfac is None else np.asarray(jzfac))
    Hoff, diag = build(st, n, edges, hop=hop, jz=jz, fields=fields)
    return st, (Hoff + sp.diags(diag)).tocsr()


def stag(st, n, eta):
    return sp.diags(np.asarray(eta, float) @ zvals(st, n)).tocsr()


# --- M1, M2: open 2 x 6 Heisenberg ladders with unequal rung coupling (site (x, y) -> 2x + y)
for Jr in (2.0, 0.5):
    L = 6; n = 2 * L
    E = [(2 * x, 2 * x + 1) for x in range(L)] + [(2 * x + y, 2 * x + 2 + y) for x in range(L - 1) for y in (0, 1)]
    J = [Jr] * L + [1.0] * (2 * (L - 1))
    eta = [(-1) ** (x + y) for x in range(L) for y in (0, 1)]
    st, H = model(n, n // 2, E, J)
    run(f"Heisenberg ladder 2x6 open, J_rung = {Jr}", n, H, stag(st, n, eta))

# --- M3: 3-leg ladder 3 x 4 open (site (x, y) -> 3x + y)
Lx, Ly = 4, 3; n = Lx * Ly
E = [(3 * x + y, 3 * x + y + 1) for x in range(Lx) for y in range(Ly - 1)] + [(3 * x + y, 3 * x + 3 + y) for x in range(Lx - 1) for y in range(Ly)]
eta = [(-1) ** (x + y) for x in range(Lx) for y in range(Ly)]
st, H = model(n, n // 2, E, 1.0)
run("Heisenberg 3-leg ladder 3x4 open", n, H, stag(st, n, eta))

# --- M4, M5, M9: frustrated J1-J2 rings, N = 12 (staggered magnetization; F = spin flip)
N = 12
E1 = [(i, (i + 1) % N) for i in range(N)]
E2 = [(i, (i + 2) % N) for i in range(N)]
eta = [(-1) ** i for i in range(N)]
for J2 in (0.2, 0.4, 0.5):
    st, H = model(N, N // 2, E1 + E2, [1.0] * N + [J2] * N)
    # K_xy restricted to the bonds that join the two sublattices (J1 bonds), with their couplings
    Hxy, _ = build(st, N, E1, hop=0.5, jz=0.0)
    run(f"J1-J2 Heisenberg ring N=12, J2 = {J2}" + (" (Majumdar-Ghosh point)" if J2 == 0.5 else ""), N, H, stag(st, N, eta),
        xy_check=Hxy)

# --- M7: J1-J2 ring, DIMER order parameter O = sum_i (-1)^i P_{i,i+1}  (non-diagonal; F = translation by one site)
st, H = model(N, N // 2, E1 + E2, [1.0] * N + [0.4] * N)
Od = sum(((-1) ** i) * swap_op(st, i, (i + 1) % N) for i in range(N)).tocsr()
run("J1-J2 ring N=12, J2 = 0.4, DIMER label sum (-1)^i P_{i,i+1}", N, H, Od, cs=(0.3, 0.7, 1.0))

# --- M6: random-bond XXZ ring with DM terms (complex hopping): only an antiunitary F = (spin flip) x (complex conjugation)
st = sector(N, N // 2)
hopc = 0.5 * rng.uniform(0.7, 1.3, N) * (1 + 1j * rng.uniform(0.2, 0.6, N))
jzr = rng.uniform(1.0, 3.0, N)
Hoff, diag = build(st, N, E1, hop=hopc, jz=jzr)
Hc = (Hoff + sp.diags(diag)).tocsr()
flux = float(np.angle(np.prod(hopc)))
run(f"random-bond XXZ + DM ring N=12 (complex H, flux {flux:.3f} rad)", N, Hc, stag(st, N, eta).astype(complex), cs=(0.3, 0.7, 1.0))
# control: the unitary spin flip alone is NOT a symmetry of this H
flipidx = np.searchsorted(st, ((1 << N) - 1) ^ st)
Hflip = Hc[flipidx][:, flipidx]
print(f"    control: || X H X - H || = {abs(Hflip - Hc).max():.3f} (not a symmetry), || X conj(H) X - H || = {abs(Hflip.conj() - Hc).max():.1e} (symmetry)")

# --- M10: easy-plane XXZ ring N = 14, Jz = 0.5 (the writer used Jz >= 1)
N2 = 14
E14 = [(i, (i + 1) % N2) for i in range(N2)]
st = sector(N2, N2 // 2)
Hoff, diag = build(st, N2, E14, hop=0.5, jz=0.5)
Hxy, _ = build(st, N2, E14, hop=0.5, jz=0.0)
run("XXZ ring N=14, Jz = 0.5 (easy plane)", N2, (Hoff + sp.diags(diag)).tocsr(), stag(st, N2, [(-1) ** i for i in range(N2)]),
    cs=(0.3, 0.7, 1.0), xy_check=Hxy)

# --- M8: open J1-J2 XXZ chain N = 16 (Jz = 2 on all bonds, J2 = 0.3)
N3 = 16
Ea = [(i, i + 1) for i in range(N3 - 1)]; Eb = [(i, i + 2) for i in range(N3 - 2)]
st = sector(N3, N3 // 2)
Hoff, diag = build(st, N3, Ea + Eb, hop=[0.5] * len(Ea) + [0.15] * len(Eb), jz=[2.0] * len(Ea) + [0.6] * len(Eb))
run("open J1-J2 XXZ chain N=16 (Jz = 2, J2 = 0.3)", N3, (Hoff + sp.diags(diag)).tocsr(), stag(st, N3, [(-1) ** i for i in range(N3)]),
    cs=(0.5, 1.0))

print("\nSUMMARY")
print(f"  values of c tested: {len(ROWS)}; violations (dual lower bound on E* above the bound): {len(VIOL)}")
r1 = [r[6] for r in ROWS if r[1] == 1.0]
ra = [r[6] for r in ROWS]
print(f"  bound / exact at c = sigma_n: {min(r1):.3f} .. {max(r1):.3f};  over all c: {min(ra):.3f} .. {max(ra):.3f}")
print(f"  largest error of the explicit state psi_theta (label and energy against the formula): {max(r[7] for r in ROWS):.1e}")
print(f"  largest relative duality gap (primal - dual)/primal: {max((r[4] - r[3]) / max(r[4], 1e-300) for r in ROWS):.1e}")
for v in VIOL:
    print("  VIOLATION", v)
print(f"total time {time.time() - t00:.0f} s")
