#!/bin/bash
# finish.sh sNN : sound + join chunks + final encode -> out/sNN.mp4, copy to project files
set -e
cd "$(dirname "$0")"
N=$1
D=out/$N
python3 $N.py sound $D/sound.wav > /dev/null
ls $D/c????.mp4 | sort | sed "s/^/file '/; s/$/'/; s#file 'out/$N/#file '#" > $D/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i $D/list.txt -i $D/sound.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 21 -tune animation -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart out/$N.mp4
mkdir -p scenes
cp out/$N.mp4 scenes/$N.mp4
ls -la out/$N.mp4
