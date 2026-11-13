#!/bin/bash
# Laptop post-processing of the learning run (written after the declaration hash; implements only declared steps).
# Run from J_next_paper/phase3/full_runs/learning/:  bash code/post_laptop.sh <out_stamp_dir>
set -euo pipefail
O=${1:?out_<stamp> directory}
A=analysis
mkdir -p "$A"
python -I -B code/learn_l.py "$O/out" D O "$A" M1 200 | tee "$A/learn_M1_stdout.txt"
python -I -B code/learn_l.py "$O/out" D O "$A" M2 200 | tee "$A/learn_M2_stdout.txt"
python -I -B code/report_l.py "$O/out" "$A" D O | tee "$A/report_stdout.txt"
python -B code/plot_learn.py "$A" D O
(cd "$A" && sha256sum *.json *.md *.png *.txt > ANALYSIS_SHA256.txt)
