#!/bin/bash
# Laptop, run from J_next_paper/phase3/full_runs/huang/ after `vm_h.sh fetch <stamp>`: analysis, tables, figure and
# SHA-256 sums of the laptop outputs. Python runs with -I -B (the data folder is read as data only).
#   bash code/post_laptop.sh <stamp>
set -euo pipefail
[ "$(basename "$(pwd)")" = huang ] || { echo "STOP: run from full_runs/huang/"; exit 9; }
STAMP=${1:?stamp}
O=out_$STAMP
mkdir -p laptop_analysis
python -I -B code/analyze_h.py "$O" data_huang laptop_analysis | tee laptop_analysis/analyze_stdout.txt
python -B code/plot_h.py laptop_analysis/summary_huang.json huang_figure.png
sha256sum laptop_analysis/* huang_figure.png | sed 's/ \*/  /' > laptop_analysis/LAPTOP_SHA256.txt
cat laptop_analysis/LAPTOP_SHA256.txt
