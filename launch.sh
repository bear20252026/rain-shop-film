#!/bin/bash
# launch.sh sNN nworkers  -> background render workers (single-threaded each)
cd "$(dirname "$0")"
for ((w=0; w<$2; w++)); do
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nohup python3 render.py $1 $w $2 > log_$1_$w.txt 2>&1 &
done
