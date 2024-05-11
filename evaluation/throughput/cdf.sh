#!/bin/bash

cat ./results/${DOCKER}_$1.txt | grep runtime_start > temp_start.out
cat ./results/${DOCKER}_$1.txt | grep runtime_end > temp_end.out

while read startline
do
	temp=`echo $startline | cut -d " " -f 2`
	starttime=`echo $temp | cut -d "," -f 1`
	echo "$starttime" >> starttimes.out
done < temp_start.out

CNT=1
while read endline
do
	temp=`echo $endline | cut -d " " -f 2`
	endtime=`echo $temp | cut -d "," -f 1`
	starttime=`cat starttimes.out | sed -n {CNT}p`

	temp=`expr $endtime - $starttime`
	run_time=`echo $temp | awk '{printf "%.6f", $1 / 1000000000}'`
	echo $run_time >> exectimes.txt
done < temp_end.out

gnuplot cdf.gnuplot

rm temp_start.out
rm temp_end.out
rm starttimes.out
rm exectimes.out
