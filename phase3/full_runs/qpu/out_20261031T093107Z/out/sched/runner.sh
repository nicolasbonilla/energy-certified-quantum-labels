#!/bin/bash
SB=$1; VPY=$2
cd "$SB/code"
one() { nm=$(echo "$*" | tr ' ' '_'); echo "$(date -u +%FT%TZ) start $nm" >> "$SB/out/sched/sched_log.txt"
  if "$VPY" -B -P qpu_post.py "$SB" $* > "$SB/out/logs/$nm.log" 2>&1; then touch "$SB/out/sched/$nm.ok"; else touch "$SB/out/sched/$nm.fail"; fi
  echo "$(date -u +%FT%TZ) end $nm" >> "$SB/out/sched/sched_log.txt"; }
export -f one; export SB VPY
xargs -P 4 -I{} bash -c 'one {}' < "$SB/out/sched/tasks.txt"
"$VPY" -B -P qpu_post.py "$SB" summary > "$SB/out/logs/summary.log" 2>&1
date -u +%FT%TZ > "$SB/out/sched/SCHED_EXIT"
