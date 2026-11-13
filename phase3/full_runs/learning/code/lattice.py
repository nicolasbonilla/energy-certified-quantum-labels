"""Geometry, couplings and labels of the Huang-Kueng-Torlai-Albert-Preskill 2D random Heisenberg benchmark
(arXiv:2106.12627; data: github.com/hsinyuan-huang/provable-ml-quantum, folder heisenberg_data/).

Conventions (verified before the declaration hash, see DECLARATION.md section 0):
  * lattice L x 5 (L = "length" in the file name heisenberg_{L}x5_id{k}_*.txt), open boundaries;
  * site index s = 5 x + y (x = 0..L-1 along the length, y = 0..4 across), the order of ITensors' square_lattice(L, 5);
  * bond k of the couplings file is the k-th bond of square_lattice(L, 5; yperiodic = false): for s = 0..n-1, first the
    bond (s, s + 5) if x < L - 1, then (s, s + 1) if y < 4;
  * H = sum_b J_b (X_i X_j + Y_i Y_j + Z_i Z_j) (the paper's text, Fig. 3a); the repository's *_E.txt files store
    <H>/2 (checked: sum_b J_b (XX + YY + ZZ)_b from the stored correlation matrices equals 2 E_file);
  * labels: C_ij = (X_i X_j + Y_i Y_j + Z_i Z_j)/3 (the paper's two-point correlator; *_XX.txt holds it for the
    ground state, which is SU(2) symmetric so that XX = YY = ZZ).
This module only parses numbers from the data files (never executes anything from them).
"""
import json
import os

W = 5                                   # width of every lattice in the dataset


def site(x, y):
    return W * x + y


def coords(s):
    return divmod(s, W)


def bonds(L):
    B = []
    for s in range(L * W):
        x, y = divmod(s, W)
        if x < L - 1:
            B.append((s, s + W))
        if y < W - 1:
            B.append((s, s + 1))
    return B


def diag_pairs(L):
    """Second-neighbour (diagonal) pairs (x, y)-(x + 1, y +- 1), i < j."""
    P = []
    for x in range(L - 1):
        for y in range(W):
            for dy in (-1, 1):
                if 0 <= y + dy < W:
                    a, b = site(x, y), site(x + 1, y + dy)
                    P.append((min(a, b), max(a, b)))
    return sorted(P)


def eta(s):
    x, y = divmod(s, W)
    return 1 if (x + y) % 2 == 0 else -1


def featured(L):
    """Featured local labels: the central horizontal bond of the middle row (Ccent), the end-to-end pair of that row
    (Cfar), and the fixed bond (1, 2)-(2, 2) (Cfix; = Ccent at L = 4). Instances with the same dataset index k share
    their first couplings (the k = 1 lists of L = 4, 6, 9 are prefixes of one another; bond 13 = (7, 12) and its
    neighbourhood up to column 2 coincide), so Cfix is the same physical bond with the same local couplings at every
    size of the k = 1 family."""
    xc = (L - 1) // 2
    cent = (site(xc, 2), site(xc + 1, 2))
    far = (site(0, 2), site(L - 1, 2))
    fix = (site(1, 2), site(2, 2)) if L >= 3 else cent     # toys (L < 3): Cfix := Ccent
    return {"Ccent": cent, "Cfar": far, "Cfix": fix}


def read_floats(path):
    vals = []
    with open(path, "r") as f:
        for line in f:
            for tok in line.replace("\t", " ").split():
                vals.append(float(tok))
    return vals


def read_matrix(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            t = line.replace("\t", " ").split()
            if t:
                rows.append([float(v) for v in t])
    return rows


def load_instance(data_dir, L, k):
    p = lambda kind: os.path.join(data_dir, "heisenberg_%dx5_id%d_%s.txt" % (L, k, kind))
    J = read_floats(p("couplings"))
    B = bonds(L)
    assert len(J) == len(B), (len(J), len(B))
    assert all(0.0 <= j <= 2.0 for j in J)
    return dict(L=L, k=k, n=L * W, J=J, bonds=B, E_file=read_floats(p("E"))[0], SvN_file=read_floats(p("SvN"))[0],
                XX=read_matrix(p("XX")), YY=read_matrix(p("YY")), ZZ=read_matrix(p("ZZ")))


def label_pairs(L, label):
    """(pairs, weights, S, (o_min, o_max)) of a label O = (1/S) sum_p w_p C_p. The field operator is S O."""
    n = L * W
    if label == "Cnn":
        P = bonds(L)
        return P, [1.0] * len(P), float(len(P)), (-1.0, 1.0 / 3.0)
    if label == "Cd2":
        P = diag_pairs(L)
        return P, [1.0] * len(P), float(len(P)), (-1.0, 1.0 / 3.0)
    if label == "Cstag":
        P = [(i, j) for i in range(n) for j in range(i + 1, n)]
        return P, [float(eta(i) * eta(j)) for (i, j) in P], float(len(P)), (-1.0, 1.0)
    if label in ("Ccent", "Cfar", "Cfix"):
        p = tuple(sorted(featured(L)[label]))
        return [p], [1.0], 1.0, (-1.0, 1.0 / 3.0)
    if label.startswith("P_"):
        _, a, b = label.split("_")
        a, b = sorted((int(a), int(b)))
        return [(a, b)], [1.0], 1.0, (-1.0, 1.0 / 3.0)
    raise ValueError(label)


def pair_label(i, j):
    i, j = sorted((int(i), int(j)))
    return "P_%d_%d" % (i, j)


def all_pair_labels(L):
    n = L * W
    return [pair_label(i, j) for i in range(n) for j in range(i + 1, n)]


def nn_pair_labels(L):
    return [pair_label(i, j) for (i, j) in bonds(L)]


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)
