#!/bin/bash
# laptop: explicit Toeplitz-Hausdorff pure witnesses for the two m_s mixtures at n = 57, Jz = 1.6, E_lo (exact weights
# from out_20261030T022613Z/out/g4/g4_list.json, written to th_witness/th_inputs.json)
cd "C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/Quantum_for_AI/J_next_paper/phase3/full_runs/map/"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
for w in min max; do
  args=$(python -c "import json; d=json.load(open('th_witness/th_inputs.json'))['$w']; print(d[0][0], d[0][1], d[1][0], d[1][1], d[2])")
  set -- $args
  python -I code/th_witness.py code/graphs/hh_d5.json 1.6 m_s $1 $2 $3 $4 $5 th_witness/th_n57_J1.6_m_s_$w.json > th_witness/th_${w}_stdout.txt 2>&1 &
done
wait
for w in min max; do
  python -c "import json; r=json.load(open('th_witness/th_n57_J1.6_m_s_$w.json')); print('$w', {k: r[k] for k in ('E_mix', 'O_mix', 'residual_2x2', 'chi_a', 'chi_b', 'chi_pure', 'dE_pure_mix', 'dO_pure_mix', 'below_threshold', 'overlap_ab')}, r['pure'])"
done
