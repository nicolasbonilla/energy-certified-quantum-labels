"""v_item1b_support.py -- verifier V, item 1 (sharp part): where exactly the gap enters the proof of
Nachtergaele-Sims Theorem 2, tested on the WHOLE Hilbert space (no sector information used in the spectral sums).

For a sector ground state psi (energy E_q, sector gap D_s), A at one site, B' = A' - <A'>:
   I(alpha)   = sum_k conj(<k|B'* psi>) <k|A psi> (1/2) erfc(e_k / (2 sqrt(alpha)))        (their Eqs. (36)-(39), b = 0)
   III(alpha) = sum_k conj(<k|A* psi>) <k|B' psi> (1/2) erfc(e_k / (2 sqrt(alpha)))        (their Eqs. (42)-(46), b = 0)
with e_k = E_k - E_q over ALL eigenvectors k of K_0 = H - mu O on the full 2^n space.  The proof bounds
   |I| <= (1/2)|A psi||B'* psi| exp(-gamma^2/(4 alpha)),  |III| <= (1/2)|A* psi||B' psi| exp(-gamma^2/(4 alpha))
and needs:  every k with <k|B' psi> != 0 or <k|B'* psi> != 0 has e_k >= gamma.
Claim (d): with gamma = D_s this holds whenever A' commutes with the charge, whatever the other sectors do.
Tested here: (1) lowest e_k that carries weight of B' psi, for charge-conserving A' (Z_j, Z_j Z_k, S+_j S-_k + h.c.)
and, as a control, for A' = X_j (does not commute with the charge); (2) the two bounds with gamma = D_s on a grid
of alpha; (3) the control violates them when another sector lies below E_q + D_s.
Models (n = 10): the referee's pinned wall; my dimer chain (other sectors 1.49 BELOW the sector ground state);
a 10-site piece of the heavy-hex patch at Jz = 1.6 with an opposing tilt.
Output: v_item1b_out.txt
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v_common import patch, adjacency, full_xxz
import numpy as np
from scipy.special import erfc

t00 = time.time()
lines = []
fails = 0


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def run(name, n, E, hop, jz, fields, nup, site_x, tests):
    global fails
    H, z = full_xxz(n, E, hop, jz, fields)
    dim = 1 << n
    st = np.arange(dim)
    pop = np.array([bin(s).count("1") for s in st])
    idx = np.nonzero(pop == nup)[0]
    ws, vs = np.linalg.eigh(H[np.ix_(idx, idx)])
    psi = np.zeros(dim)
    psi[idx] = vs[:, 0]
    Eq, Ds = ws[0], ws[1] - ws[0]
    w, V = np.linalg.eigh(H)                       # whole space, no symmetry used
    e = w - Eq
    below = int((e < -1e-9).sum())
    say(f"{name}: n = {n}, sector M = {2*nup-n}: E_q = {Eq:.6f}, sector gap D_s = {Ds:.5f}; levels of the whole space below E_q: "
        f"{below}; lowest level of the whole space at e = {e.min():+.4f}; levels of other sectors inside (0, D_s): "
        f"{int(((e > 1e-9) & (e < Ds - 1e-9)).sum())}")

    def Zop(j):
        return np.diag(z[:, j])

    def Xop(j):
        m = np.zeros((dim, dim))
        m[st ^ (1 << j), st] = 1.0
        return m

    def hopop(j, k):
        m = np.zeros((dim, dim))
        dif = (((st >> j) ^ (st >> k)) & 1) == 1
        m[st[dif] ^ ((1 << j) | (1 << k)), st[dif]] = 1.0
        return m
    A = Zop(site_x)
    Apsi = A @ psi
    alphas = np.exp(np.linspace(np.log(0.02), np.log(200.0), 60))
    say("   A'                      commutes with M   lowest e_k with weight of B'psi   weight below D_s   "
        "max_alpha |I|/bound   max_alpha |III|/bound   |<A;A'>|   max_alpha(|I| or |III| minus its bound)")
    for label, kind, args in tests:
        if kind == "Z":
            Ap = Zop(*args)
        elif kind == "ZZ":
            Ap = Zop(args[0]) @ Zop(args[1])
        elif kind == "hop":
            Ap = hopop(*args)
        elif kind == "X":
            Ap = Xop(*args)
            A = Xop(site_x)
            Apsi = A @ psi
        conserving = kind != "X"
        mean = psi @ (Ap @ psi)
        Bp = Ap - mean * np.eye(dim)
        b1 = V.T @ (Bp @ psi)                      # <k|B' psi>
        b2 = V.T @ (Bp.T @ psi)                    # <k|B'* psi>
        a1 = V.T @ Apsi                            # <k|A psi>
        a2 = V.T @ (A.T @ psi)                     # <k|A* psi>
        wt = b1 ** 2 + b2 ** 2
        carr = e[wt > 1e-22]
        emin = carr.min() if len(carr) else np.inf
        wbelow = float(wt[e < Ds - 1e-8].sum())
        nb = np.linalg.norm(Bp @ psi)
        nbs = np.linalg.norm(Bp.T @ psi)
        rI, rIII, exc = 0.0, 0.0, -1.0
        for al in alphas:
            g = 0.5 * erfc(e / (2 * np.sqrt(al)))
            I = float((b2 * a1) @ g)
            III = float((a2 * b1) @ g)
            bI = 0.5 * np.linalg.norm(Apsi) * nbs * np.exp(-Ds ** 2 / (4 * al))
            bIII = 0.5 * np.linalg.norm(A.T @ psi) * nb * np.exp(-Ds ** 2 / (4 * al))
            # ratios only where the bound is above the rounding noise of the spectral sums (1e-10); below it the
            # comparison is |I| - bound <= 1e-12 (the weights that vanish by symmetry are ~1e-16 in double precision)
            if bI > 1e-10:
                rI = max(rI, abs(I) / bI)
            if bIII > 1e-10:
                rIII = max(rIII, abs(III) / bIII)
            exc = max(exc, abs(I) - bI, abs(III) - bIII)
        corr = abs(float(psi @ (A @ (Bp @ psi))))
        okS = emin >= Ds - 1e-7
        okB = exc <= 1e-12
        if conserving and not (okS and okB):
            fails += 1
        say(f"   {label:22s}  {str(conserving):5s}             {emin:+10.5f} ({'>= D_s' if okS else '<  D_s'})          "
            f"{wbelow:9.2e}          {rI:9.3e}             {rIII:9.3e}         {corr:.3e}   max excess {exc:+.1e}"
            f"{'' if conserving else '   <- control (A = X at the first site)'}")
        if kind == "X":
            A = Zop(site_x)
            Apsi = A @ psi
    say(f"   [{time.time()-t00:.0f} s]")


# 1. pinned wall, n = 10
n = 10
E = [(i, i + 1) for i in range(n - 1)]
f = np.zeros(n)
f[0], f[-1] = -1.0, 1.0
run("1. pinned wall (referee's example)", n, E, 0.5, -4.0, f, 5, 4,
    [("Z_5", "Z", (5,)), ("Z_7", "Z", (7,)), ("Z_6 Z_7", "ZZ", (6, 7)), ("S+_6 S-_7 + h.c.", "hop", (6, 7)), ("X_6", "X", (6,))])

# 2. dimers, n = 10
L = 5
n = 2 * L
E, hop, jz = [], [], []
for k in range(L):
    E.append((2 * k, 2 * k + 1)); hop.append(0.5); jz.append(-4.0)
    if k < L - 1:
        E.append((2 * k + 1, 2 * k + 2)); hop.append(0.2); jz.append(0.0)
f = np.zeros(n)
mid = (L - 1) // 2
for k in range(L):
    if k < mid:
        f[2 * k] = f[2 * k + 1] = -1.0
    elif k > mid:
        f[2 * k] = f[2 * k + 1] = +1.0
run("2. ferromagnetic dimers with a step field (mine)", n, E, hop, jz, f, 5, 4,
    [("Z_5", "Z", (5,)), ("Z_7", "Z", (7,)), ("Z_6 Z_7", "ZZ", (6, 7)), ("S+_6 S-_7 + h.c.", "hop", (6, 7)), ("X_6", "X", (6,))])

# 3. a 10-site connected piece of the heavy-hex patch (ball around a degree-3 minority site), Jz = 1.6, opposing tilt
n19, E19, names, eta19 = patch(3)
adj = adjacency(n19, E19)
root = [i for i in range(n19) if eta19[i] < 0 and len(adj[i]) == 3][0]
order, seen = [root], {root}
q = [root]
while q and len(order) < 10:
    u = q.pop(0)
    for v in adj[u]:
        if v not in seen and len(order) < 10:
            seen.add(v)
            order.append(v)
            q.append(v)
pos = {v: k for k, v in enumerate(order)}
E10 = [(pos[a], pos[b]) for a, b in E19 if a in pos and b in pos]
eta10 = np.array([eta19[v] for v in order])
nup10 = int((eta10 > 0).sum())
say(f"   (piece: sites {order} of the 19-site patch, {len(E10)} bonds, {nup10} majority / {10-nup10} minority sites)")
for mu in (0.0, -0.15):
    x_site = pos[root]
    far = [k for k in range(10) if k != x_site][-3:]
    run(f"3. heavy-hex piece, Jz = 1.6, tilt mu = {mu:+.2f} Jz (field -mu eta_i Z_i)", 10, E10, 0.5, 1.6, -(mu * 1.6) * eta10, nup10,
        x_site, [(f"Z_{far[0]}", "Z", (far[0],)), (f"Z_{far[2]}", "Z", (far[2],)),
                 (f"Z_{far[1]} Z_{far[2]}", "ZZ", (far[1], far[2])), (f"X_{far[2]}", "X", (far[2],))])

say(f"\nfailures for charge-conserving A' (spectral support below D_s, or a violated bound on I, III): {fails}   [{time.time()-t00:.0f} s]")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v_item1b_out.txt"), "w") as fo:
    fo.write("\n".join(lines) + "\n")
