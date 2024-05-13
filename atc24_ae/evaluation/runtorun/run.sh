LIST=("linpack" "matmul")
DOCKER="ubuntu-python-rewind"
ITER_MAX=3

if [ "$#" -lt 1 ]
then
	echo "[ERROR] Enter DOCKER_USER"
	exit 1
fi

if [ ! -d "./results" ]
then
	mkdir ./results
fi

for WORK in ${LIST[@]}
do
	# Update function
	wsk action update --memory 512 ${DOCKER}-${WORK} ../workloads/${WORK}.py --docker $1/${DOCKER}
	sleep 2

	# Cold start
	wsk action invoke ${DOCKER}-${WORK} --result --param n 1000 >> /dev/null
	sleep 2

	ITER_CNT=0
	while [ ${ITER_CNT} -lt ${ITER_MAX} ]
	do
		echo "################# Param 1000 ${WORK} ${ITER_CNT}"
		wsk action invoke ${DOCKER}-${WORK} --result --param n 1000 >> ./results/${WORK}.out
		sleep 2
		ITER_CNT=$(($ITER_CNT+1))
	done

	ITER_CNT=0
	while [ ${ITER_CNT} -lt ${ITER_MAX} ]
	do
		echo "################# Param 950 ${WORK} ${ITER_CNT}"
		wsk action invoke ${DOCKER}-${WORK} --result --param n 950 >> ./results/${WORK}.out
		sleep 2
		ITER_CNT=$(($ITER_CNT+1))
	done

	ITER_CNT=0
	while [ ${ITER_CNT} -lt ${ITER_MAX} ]
	do
		echo "################# Param 1050 ${WORK} ${ITER_CNT}"
		wsk action invoke ${DOCKER}-${WORK} --result --param n 1050 >> ./results/${WORK}.out
		sleep 2
		ITER_CNT=$(($ITER_CNT+1))
	done
done

for WORK in ${LIST[@]}
do
	cat ./results/${WORK}.out | grep runtime_start > temp_start.out
	cat ./results/${WORK}.out | grep runtime_end > temp_end.out

	for ((iter=1 ; iter < 10 ; iter++));
	do
		temp=`cat temp_start.out | sed -n ${iter}p`
		temp=`echo $temp | cut -d " " -f 2`
		start_time=`echo $temp | cut -d "," -f 1`

		temp=`cat temp_end.out | sed -n ${iter}p`
		temp=`echo $temp | cut -d " " -f 2`
		end_time=`echo $temp | cut -d "," -f 1`

		temp=`expr $end_time - $start_time`
		run_time=`echo $temp | awk '{printf "%.6f", $1 / 1000000}'`

		echo "(run-to-run #${iter} of ${WORK}) time: $run_time ms"
	done

	rm temp_start.out
	rm temp_end.out
done
