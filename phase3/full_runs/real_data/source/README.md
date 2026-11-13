# real_data/source: the public repository of arXiv:2606.15983, pinned

Written 2026-11-12 by the review task `real-data-setup` (R10). This folder holds **untrusted downloads**. Nothing in it
is executed or imported by this project, and no script may call `pickle.load` on its files. Later analyses read only
`../converted/*.json`.

## What this is

| | |
|---|---|
| Repository | `github.com/bjader/quantum-groundstate-learning` ("Code to reproduce 'Learning ground state observables from quantum computing experiments'", arXiv:2606.15983) |
| Branch, commit | `main`, `6b8866b66d62aaf3ee815cd14fa58e9bf4629d66` (merge of pull request 2; author and committer date 2026-07-22T09:38:59Z; signature reported "verified" by the GitHub API) |
| Git tree | `a6cefd388e2fcc949ccf49bdbaf7e51ef94711fa`; parents `ec75617251e1...` and `b3a73667ad35...` |
| Data commits | `8d852a38` 2026-07-17 "added reduced datasets"; `2a976857` and `76eca8c2` 2026-07-21 "added the data", "data added"; `ec756172` 2026-07-21 "added dmrg data" (commit list fetched by the first look: `paper/reviews/R10_2026-11-12/scratch/level-sota/out/gh/commits.json`) |
| Repository dates | created 2026-05-05T14:07:37Z; `pushed_at` 2026-08-28T09:58:16Z. Today the only branch is `main` at the commit above and there is no tag, so the later push left no trace in `main`. |
| Licence | Apache-2.0 (`LICENSE_upstream.txt`, 11 357 bytes, SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`) |
| Archive | `archive/quantum-groundstate-learning-6b8866b66d62aaf3ee815cd14fa58e9bf4629d66.tar.gz`, 778 170 bytes, SHA-256 `13aa8e69c9bc614c72c5a415ecd889f113eabe95eec81e221174b3f14dedbb91` |
| Download | 2026-11-12T17:08:58Z, `curl` with a generic User-Agent, from `https://codeload.github.com/bjader/quantum-groundstate-learning/tar.gz/<commit>`; no personal detail in any request |

## Checks made on the archive (script `../code/provenance_check.py`, output `../checks/provenance_check_stdout.txt`)

1. The commit id written by GitHub into the pax header of the archive is the commit above.
2. The archive fetched by the first look (`paper/reviews/R10_2026-11-12/scratch/level-sota/dl_untrusted/tar/repo_main.tar.gz`,
   778 499 bytes, SHA-256 `9ff134ece3c804f36ed134118dbcfa00d2029b8d3f950997d3d2d959674dca52`, top folder `...-main`)
   carries the same commit id. The two archives differ as byte streams (the top folder name differs) and are
   **identical in content**: 378 regular files in each, none missing on either side, none with different bytes.
3. Every one of the 378 files has the git blob SHA-1 and the size that the GitHub API lists for the tree of that commit
   (`github_api/tree_<commit>.json`, not truncated). No link, device or other non-regular member; no absolute path and
   no path that leaves the folder.
4. Contents: 302 data files (`data/spins_{57,115}/{skqd/recovery_random_flip, skqd/recovery_post_select,
   dmrg/chi_max_320_trunc_1e-06_reduced}/XXZ_2d_jz_*.pkl`), two edge lists (`cmaps/`), 69 Python files, the licence,
   the README, a `.gitignore`, `requirements.txt`, `environment.yml`. Sizes by folder are in the output file.

## Files here

- `archive/`: the pinned archive, as downloaded. Never extracted to disk as a tree.
- `github_api/`: public metadata fetched from `api.github.com` at the same time (commit, tree, branches, tags,
  repository record; `fetch_time_utc.txt`).
- `LICENSE_upstream.txt`: the licence text, copied from the archive member `LICENSE`.
- `MEMBERS.tsv`: path, size, SHA-256, git blob SHA-1 and tar mode of each of the 378 files.
- `code_as_text/`: the 76 text files of the repository (code, README, edge lists, requirements), each saved under a
  flattened name with `.txt` appended, so that they can be **read** with line numbers and cannot be imported or run.
  The line numbers quoted in `paper/reviews/R10_2026-11-12/reports/real-data-setup.md` refer to these copies, which are
  byte-identical to the archive members.
- `SHA256SUMS.txt`: SHA-256 of every file of this folder except itself.

## When these data were first opened by this project

- **2026-11-12**, by the review agent `level-sota` of the R10 review, with
  `paper/reviews/R10_2026-11-12/scratch/level-sota/inspect_static.py` (opcodes only), `extract_data.py` (member bytes,
  flattened names) and `real_data_first_look.py` (restricted unpickler, whitelist of five numpy constructors). File
  times in that scratch folder: repository metadata 17:30, archive 17:32, first outputs 17:34-17:48 (local time,
  UTC+1). Its outputs are `scratch/level-sota/out/real_data_first_look_stdout.txt`, `real_data_first_look.json`,
  `real_data_details_stdout.txt`, `gap_check_stdout.txt`, `final_checks_stdout.txt`; its report is
  `reports/level-sota.md`.
- The same day, later, this task read the files again through `../code/convert_real_data.py` and ran
  `../code/descriptive_checks.py` (outputs in `../checks/`). What was seen is listed exactly in
  `../DECLARATION_DRAFT.md`, part (a).
- **Every earlier analysis of the paper used only the published figures and text of arXiv:2606.15983**: the
  certification map (`../map/`, declared 2026-10-30, energies digitized from the figures, `map/digitization/`), the
  exact-arithmetic bounds (`../rigor/`, 2026-10-31), the emulation (`../method/`), the device runs (`../qpu/`,
  `../final_tests/`), the learning tests (`../learning_ibm/`, `../learning/`, `../huang/`) and the bias study
  (`../bias_law/`). The manuscript of that date says so (`paper/main.tex` 1173-1174: "we did not request them and read
  only its published figures"), and the arXiv record does not link to the repository. This is a statement of the
  project's records; this task found nothing that contradicts it and has no means to prove a negative.

## How to use

Do not open the `.pkl` members. Use `../converted/real_n57.json`, `../converted/real_n115.json` and
`../converted/lattice_maps.json` (plain JSON; every field of every data file; SHA-256 of each input member inside).
To re-create them: `python -B -I ../code/convert_real_data.py archive/<archive> ../converted` (static opcode
inspection, then a restricted unpickler; the three outputs are deterministic and must reproduce
`../converted/SHA256SUMS.txt`).

When citing: Ref. arXiv:2606.15983, its authors' repository at the commit above, Apache-2.0.
