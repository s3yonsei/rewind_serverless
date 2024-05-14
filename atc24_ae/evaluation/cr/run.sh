N=20
LIST=("hello" "pkg4" "float" "linpack" "matmul" "pyaes" "chameleon" "imgproc" "vidpro" "train" "lr")
DOCKER="ubuntu-python-rewind-profile"

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
	wsk action update --memory 256 ${DOCKER}-${WORK} workloads/${WORK}.py --docker $1/${DOCKER}
	sleep 2

	# Cold start	
	wsk action invoke ${DOCKER}-${WORK} --result >> /dev/null
	sleep 2
done

for i in $(seq 1 $N)
do
	for WORK in ${LIST[@]}
	do
		wsk action invoke ${DOCKER}-${WORK} --result >> ./results/${WORK}.out
		sleep 2
	done
done

for WORK in ${LIST[@]}
do
	dmesg | grep REWIND > ./results/${WORK}.out

	cat ./results/${WORK}.out | grep checkpoint > temp_check.out
	cat ./results/${WORK}.out | grep rewind > temp_rewind.out

	CHECK=`cat temp_check.out | cut -d " " -f 4`

	REWIND=0
	for ((iter=1; iter <= 20; iter++));
	do
		temp=`cat temp_rewind.out | sed -n ${iter}p`
		temp=`echo $temp | cut -d " " -f 4`

		REWIND=`expr $CHECK + $temp`
	done

	CHECK=`echo $CHECK | awk '{printf "%.6f", $1 / 1000000}'`
	REWIND=`echo $REWIND | awk '{printf "%.6f", $1 / 20000000}'`

	echo "checkpoint/rewind time of ${WORK}: $CHECK / $REWIND ms"

	rm temp_check.out
	rm temp_rewind.out
done
