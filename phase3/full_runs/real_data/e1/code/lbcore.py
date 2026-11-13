"""Shared model definitions for the rigor test (cluster / local-consistency lower bounds), numeric side.

Model (identical conventions to map/code/hhmodel.py, MPS site labels of the graph JSON):
    H = sum_edges [ 1/4 (X_i X_j + Y_i Y_j) + (Jz/4) Z_i Z_j ] + sum_i c_i Z_i       (Pauli matrices)
    'H'       : c = 0
    'm_s'     : H(Jz) - sigma*lam*sum_i eta_i Z_i       (S*m_s = sum_i eta_i Z_i)
    'Czz_bar' : H(Jz - 4*sigma*lam)                       (S*Czz_bar = sum_e Z_i Z_j)
Sector: Sz = (n_up - n_down)/2, i.e. sum_i Z_i = twoS = n_up - n_down.
Basis bit 1 = up = Z eigenvalue +1. All coefficients are kept as exact Fractions (dyadic when built from floats).
"""
import json
from fractions import Fraction


def load_graph(path):
    G = json.load(open(path))
    n = G["n"]
    edges = [tuple(sorted(map(int, e))) for e in G["mps"]["edges"]]
    eta = [int(x) for x in G["mps"]["eta"]]
    up = [int(x) for x in G["mps"]["up_init"]]
    n_up = sum(up)
    return dict(n=n, edges=edges, eta=eta, n_up=n_up, n_down=n - n_up, twoS=2 * n_up - n, raw=G)


def frac(x):
    """Exact Fraction of a float / int / 'p/q' string (floats are converted exactly: dyadic)."""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, str):
        return Fraction(x)
    return Fraction(x)


def ham_spec(g, kind, Jz, sigma=0, lam=0):
    """Exact coefficients: dict(Jz=Fraction, site=[Fraction]*n). lam may be a float (taken exactly)."""
    Jz, lam = frac(Jz), frac(lam)
    n = g["n"]
    if kind == "H":
        return dict(kind=kind, Jz=Jz, site=[Fraction(0)] * n, sigma=0, lam=Fraction(0), Jz_base=Jz)
    if kind == "m_s":
        return dict(kind=kind, Jz=Jz, site=[-sigma * lam * g["eta"][i] for i in range(n)], sigma=sigma, lam=lam,
                    Jz_base=Jz)
    if kind == "Czz_bar":
        return dict(kind=kind, Jz=Jz - 4 * sigma * lam, site=[Fraction(0)] * n, sigma=sigma, lam=lam, Jz_base=Jz)
    raise ValueError(kind)


def spec_to_json(sp):
    return dict(kind=sp["kind"], Jz=str(sp["Jz"]), Jz_base=str(sp["Jz_base"]), sigma=sp["sigma"], lam=str(sp["lam"]),
                site=[str(c) for c in sp["site"]])


def spec_from_json(d):
    return dict(kind=d["kind"], Jz=Fraction(d["Jz"]), Jz_base=Fraction(d["Jz_base"]), sigma=int(d["sigma"]),
                lam=Fraction(d["lam"]), site=[Fraction(c) for c in d["site"]])


def terms(g, sp):
    """List of terms: ('xy', (i,j), 1/4), ('zz', (i,j), Jz/4), ('z', (i,), c_i) (zero coefficients dropped)."""
    T = []
    for (i, j) in g["edges"]:
        T.append(("xy", (i, j), Fraction(1, 4)))
        if sp["Jz"] != 0:
            T.append(("zz", (i, j), sp["Jz"] / 4))
    for i, c in enumerate(sp["site"]):
        if c != 0:
            T.append(("z", (i,), c))
    return T
