#!/bin/bash
# join all scenes into one film, then cut into <=25 MB .ts pieces + JOIN bat
set -e
cd "$(dirname "$0")"; SC=$PWD/scenes; OUT=$PWD/final; mkdir -p $OUT/parts
cd $SC; rm -f $OUT/list.txt
for n in 01 02 03 04 05 06 07 08 09 10 11 12 13; do echo "file '$SC/s$n.mp4'" >> $OUT/list.txt; done
ffmpeg -y -v error -f concat -safe 0 -i $OUT/list.txt -c copy -movflags +faststart $OUT/The_Rain_Shop.mp4
ffmpeg -y -v error -i $OUT/The_Rain_Shop.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts $OUT/full.ts
rm -f $OUT/parts/*; split -b 24M -d -a 2 $OUT/full.ts $OUT/parts/RainShop.part; rm $OUT/full.ts
cd $OUT/parts; for f in RainShop.part*; do mv $f $f.ts; done
files=$(ls RainShop.part*.ts | tr '\n' '+' | sed 's/+$//')
printf '@echo off\r\ncd /d "%%~dp0"\r\ncopy /b %s The_Rain_Shop.ts\r\necho Done. Open The_Rain_Shop.ts\r\npause\r\n' "$files" > JOIN_The_Rain_Shop.bat
ls -la $OUT/parts | tail -4; ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT/The_Rain_Shop.mp4
