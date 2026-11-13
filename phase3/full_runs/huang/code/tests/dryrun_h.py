"""Dry run of the whole pipeline on toy strips (L = 2, n = 10, ED + DMRG; L = 3, n = 15 odd, DMRG), then g4.py and
analyze_h.py on the toy outputs. Random couplings (not from the dataset).

  python tests/dryrun_h.py <root_dir_to_create>
"""
import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, CODE)
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import witness as WT  # noqa: E402
from test_huang import write_toy_dataset  # noqa: E402


def main(root):
    os.makedirs(root)
    for (L, k, seed) in ((2, 1, 11), (3, 1, 12)):
        write_toy_dataset(root, L, k, seed)
        n = 5 * L
        rng = np.random.default_rng(seed)
        np.savetxt(os.path.join(root, "data_huang", "heisenberg_%dx5_id%d_samples.txt" % (L, k)),
                   rng.integers(0, 6, size=(200, n)), fmt="%d", delimiter="\t")
    WT.task_edref(root, 2, 1)
    for lab in ("Cnn", "Cd2", "Ccent", "Cfar", "Cstag"):
        WT.task_edlab(root, 2, 1, lab)
    WT.task_edpairs(root, 2, 1, 0)
    WT.task_ref(root, 2, 1)
    for lab in ("Cnn", "Ccent", "Cfar"):
        WT.task_lab(root, 2, 1, lab)
    WT.task_ref(root, 3, 1)
    for lab in ("Cnn", "Ccent", "Cfix"):
        WT.task_lab(root, 3, 1, lab)
    WT.task_chk(root, 3, 1, "Ccent", "+")
    WT.task_cold(root, 3, 1, "Ccent", "-")
    WT.task_lawscan(root, 3, 1, 0)
    env = dict(os.environ)
    subprocess.check_call([sys.executable, "-B", os.path.join(CODE, "g4.py"), root], env=env)
    subprocess.check_call([sys.executable, "-B", os.path.join(CODE, "analyze_h.py"), root,
                           os.path.join(root, "data_huang"), os.path.join(root, "summary")], env=env)


if __name__ == "__main__":
    main(sys.argv[1])
