#!/bin/bash
# queue.sh : renders scenes listed in queue.txt in order (3 workers each), then finish.sh. Waits for new entries; stops when file STOP exists.
cd "$(dirname "$0")"
while pgrep -f "python3 render[.]py s01" >/dev/null; do sleep 30; done
while [ ! -f STOP ]; do
  N=""
  for n in $(cat queue.txt); do [ -f out/$n.mp4 ] || { N=$n; break; }; done
  if [ -z "$N" ]; then sleep 120; continue; fi
  echo "$(date +%T) start $N" >> queue_log.txt
  for w in 0 1 2 3; do python3 render.py $N $w 4 > log_${N}_$w.txt 2>&1 & done
  wait
  ./finish.sh $N > log_finish_$N.txt 2>&1 || { echo "$(date +%T) FINISH FAILED $N" >> queue_log.txt; touch out/$N.failed; sleep 60; }
  echo "$(date +%T) done $N" >> queue_log.txt
  [ -f out/$N.failed ] && break
done
