"""T2: Theorem 1 (local labels).  Reset witnesses: explicit states in the window with the extreme label.
Checks: (i) reset energy cost eps_R <= kappa_A (universal spread bound);
(ii) exact window u(eps_R) >= label shift of the reset state (the reset state is in W(E0+eps_R));
(iii) interpolation bound u(eps) >= min(1, eps/eps_R) * shift on an eps grid;
(iv) fixed-density growth of the local width with n; N* = eps_R/de (sharp) and kappa_A/de (universal).
(v) U(1)-covariant reset on B={0,1} for XXZ in a fixed Sz sector; block averages."""
import os, time, numpy as np
from edcore import *

t0 = time.time()


def full_from(b, v):
    return b.embed(v) if not b.full else v.astype(complex)


def reset_vectors(psi, n, B, target_of):
    """Covariant measure-and-prepare on region B (list of sites).
    target_of(s_bits) -> local config t (tuple of bits) to prepare given the measured config s.
    Returns list of full-space vectors v_s (unnormalized), rho' = sum_s |v_s><v_s|."""
    idx = np.arange(2 ** n)
    loc = np.stack([(idx >> i) & 1 for i in B], axis=1)  # (2^n, |B|)
    out = []
    for s in set(map(tuple, loc)):
        m = np.all(loc == np.array(s), axis=1)
        t = target_of(s)
        tgt = idx[m].copy()
        for k, i in enumerate(B):
            tgt = (tgt & ~(1 << i)) | (t[k] << i)
        v = np.zeros(2 ** n, dtype=complex)
        v[tgt] = psi[m]
        out.append(v)
    return out


def mix_exp(M, vs):
    return float(sum(np.real(np.vdot(v, M @ v)) for v in vs))


def spread(hmat):
    w = np.linalg.eigvalsh(hmat)
    return w[-1] - w[0]


X = np.array([[0, 1], [1, 0]]); Y = np.array([[0, -1j], [1j, 0]]); Z = np.diag([-1.0, 1.0])
I2 = np.eye(2)
s_tfim_bond = lambda J: spread(-J * np.kron(Z, Z))
s_tfim_field = lambda h: spread(-h * X)
s_xxz_bond = lambda Jz: spread(0.25 * (np.kron(X, X) + np.kron(Y, Y) + Jz * np.kron(Z, Z)).real)

rows = []
print("== (i)-(iii) single-site resets, no symmetry constraint (TFIM) ==")
for (name, n, edges, h) in [('TFIM1D h=1.5', 8, chain_edges(8), 1.5), ('TFIM1D h=1.5', 12, chain_edges(12), 1.5),
                            ('TFIM1D h=0.5', 10, chain_edges(10), 0.5),
                            ('TFIM2D 3x4 h=3.5', 12, rect_edges(3, 4, True), 3.5),
                            ('TFIM2D 3x4 h=2.0', 12, rect_edges(3, 4, True), 2.0)]:
    b, H = tfim(n, edges, 1.0, h)
    i0 = 5 if '2D' in name else 0
    deg = sum(1 for e in edges if i0 in e)
    kappa = deg * s_tfim_bond(1.0) + s_tfim_field(h)
    labs = [('Z', diag_op(b, [(1.0, (i0,))]), (1,), (0,))] + ([('X', x_op(b, [(i0, 1.0)]), None, None)] if (name == 'TFIM1D h=1.5') else [])
    for lab, O, up, dn in labs:
        for sgn in (+1, -1):
            W = Window(H, O, sgn)
            psi = full_from(b, W.psi0)
            if lab == 'Z':
                t = (1,) if sgn > 0 else (0,)
                vs = reset_vectors(psi, n, [i0], lambda s, t=t: t)
            else:  # reset to X = +-1 eigenstate |+> or |->: superpose the two target configs
                c = 1 / np.sqrt(2)
                v_up = reset_vectors(psi, n, [i0], lambda s: (1,))
                v_dn = reset_vectors(psi, n, [i0], lambda s: (0,))
                # v_s(|+>) = c (|1>|a_s> + sgn |0>|a_s>)
                vs = [c * (a + sgn * bb) for a, bb in zip(v_up, v_dn)]
            Hf = H if b.full else None
            eR = mix_exp(H, vs) - W.E0
            oR = mix_exp(W.O, vs) - W.o0   # shift in the signed frame
            uR, _, _ = W.u(max(eR, 1e-9))
            # interpolation check
            worst = 1.0
            for eps in (0.25 * eR, eR):
                ue, _, _ = W.u(eps)
                worst = min(worst, ue - min(1, eps / eR) * oR)
            rows.append((name, n, f"{lab}_{i0}", sgn, eR, kappa, oR, uR, worst))
            print(f"{name:18s} n={n:2d} O={lab}_{i0} sgn={sgn:+d}: reset cost eps_R={eR:.4f} <= kappa_A={kappa:.3f} [{eR <= kappa + 1e-12}]; "
                  f"reset shift={oR:.4f}; exact u(eps_R)={uR:.4f} >= shift [{uR >= oR - 1e-9}]; min over grid of u-interp = {worst:+.2e} [>= 0: {worst >= -1e-9}]")

print("\n== (iv) local width at fixed energy density grows with n (TFIM1D h=1.5, O=Z_0, range 2) ==")
for de in (0.05, 0.1, 0.2):
    line = []
    for n in (6, 8, 10, 12):
        b, H = tfim(n, chain_edges(n), 1.0, 1.5)
        O = diag_op(b, [(1.0, (0,))])
        w = sum(Window(H, O, s).u(n * de)[0] for s in (+1, -1))
        line.append(f"n={n}: w={w:.3f}")
    print(f"de={de}: " + "; ".join(line))

print("\n== (v) U(1) sector: covariant reset on B={0,1} (XXZ Jz=1.6, Sz=0) and 2D ==")
for (name, n, edges, Jz, B) in [('XXZ1D', 8, chain_edges(8), 1.6, [0, 1]), ('XXZ1D', 12, chain_edges(12), 1.6, [0, 1]),
                                ('XXZ2D 3x4', 12, rect_edges(3, 4, True), 1.6, [5, 6])]:
    b, H = xxz(n, edges, Jz, n // 2)
    bf = Basis(n)
    Hf = sp.csr_matrix(flipflop_op(bf, edges, 0.5) + diag_op(bf, [(Jz / 4.0, e) for e in edges]))
    i0 = B[0]
    O = diag_op(b, [(1.0, (i0,))]); Of = diag_op(bf, [(1.0, (i0,))])
    nb = sum(1 for e in edges if (e[0] in B or e[1] in B))
    kappa = nb * s_xxz_bond(Jz)
    for sgn in (+1, -1):
        W = Window(H, O, sgn)
        psi = b.embed(W.psi0)
        # measured local charge q = number of ups on B; prepare the config with Z_{i0} = sgn whenever possible
        def tgt(s, sgn=sgn):
            q = sum(s)
            if q == 1:
                return (1, 0) if sgn > 0 else (0, 1)
            return s
        vs = reset_vectors(psi, n, B, tgt)
        eR = mix_exp(Hf, vs) - W.E0
        oR = sgn * mix_exp(Of, vs) - W.o0
        p_block = sum(np.linalg.norm(v) ** 2 for v in vs if True)
        uR, _, _ = W.u(eR)
        print(f"{name:10s} n={n:2d} B={B} sgn={sgn:+d}: eps_R={eR:.4f} <= kappa_B={kappa:.3f} [{eR <= kappa}]; shift={oR:.4f} "
              f"(= 1 - o0 - 2P(blocked) ; o0={W.o0:+.4f}); exact u(eps_R)={uR:.4f} [>= shift: {uR >= oR - 1e-9}]; norm={p_block:.12f}")

print("\n== block averages (TFIM1D h=1.5 n=12): reset all b sites of a block to up ==")
n = 12
b, H = tfim(n, chain_edges(n), 1.0, 1.5)
for bsz in (1, 2, 3, 4, 6, 12):
    B = list(range(bsz))
    O = diag_op(b, [(1.0 / bsz, (i,)) for i in B])
    W = Window(H, O, +1)
    vs = reset_vectors(W.psi0.astype(complex), n, B, lambda s, bsz=bsz: tuple([1] * bsz))
    eR = mix_exp(H, vs) - W.E0
    uR, _, fl = W.u(eR)
    kap = sum(1 for e in chain_edges(n) if e[0] in B or e[1] in B) * 2.0 + bsz * 3.0
    print(f"b={bsz:2d}: eps_R={eR:.3f} (per site {eR / bsz:.3f}); kappa_B={kap:.1f}; u(eps_R)={uR:.4f} vs full 1-o0={1 - W.o0:.4f}; "
          f"so full range once n*de >= {eR:.2f}, i.e. b* = n de/{eR / bsz:.2f}")
print(f"time {time.time() - t0:.1f} s")
