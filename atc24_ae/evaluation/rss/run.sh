N=3
LIST=("hello" "pkg4" "float" "linpack" "matmul" "pyaes" "chameleon" "imgproc" "vidproc" "train" "lr")
DOCKER="ubuntu-python-rewind-rss"

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
		wsk action invoke ${DOCKER}-${WORK} --result >> /dev/null
		sleep 2
	done
done

for WORK in ${LIST[@]}
do
	DOCKER_NAME=$(printf "%s%s" "_ubuntupythonrewindrss" "${WORK}")
	DOCKER_ID=$(docker ps | grep $DOCKER_NAME | awk '{print $1}')
	echo "docker name: $DOCKER_NAME"
	echo "docker ID: $DOCKER_ID"
	
	docker cp ${DOCKER_ID}:/tmp/proxy.out ./results/proxy${WORK}.txt
	docker cp ${DOCKER_ID}:/tmp/launcher.out ./results/launcher${WORK}.txt

	temp=`tail -n 1 ./results/launcher${WORK}.txt`
	launcher=`echo $temp | cut -d " " -f 2`

	temp=`tail -n 1 ./results/proxy${WORK}.txt`
	proxy=`echo $temp | cut -d " " -f 2`

	total_rss=`expr $launcher + $proxy`
	echo "RSS of ${WORK}: $total_rss kB"
done


