
# USENIX ATC'24 Artifacts Evaluation

**A Secure, Fast, and Resource-Efficient Serverless Platform with Function REWIND**, Jaehyun Song, Bumsuk Kim, Minwoo Kwak, Byoungyoung Lee, Euiseong Seo, and Jinkyu Jeong, Proceedings of the 2024 USENIX Annual Technical Conference (USENIX ATC '24), Santa Clara, CA, US, July 10-12, 2024 (to appear)

This repository reproduces the evaluation presented in the paper published at USENIX ATC '24.
Please contact us if you have any questions.
[Jaehyun Song](mailto:jaehyun.song@csi.skku.edu), [Jinkyu Jeong](mailto:jinkyu@yonsei.ac.kr), [Scalable Systems Software Lab](https://cslab.yonsei.ac.kr), Yonsei University, South Korea

## Contents
- [1. Configurations](#1-configurations)
- [2. Getting Started](#2-getting-started)
- [3. Evaluation of REWIND](#3-evaluation-of-rewind)

## 1. Configurations

The experimental environment was set up on the following hardware configurations:

| **Component**       | **Specification**
|---------------------|--------------------------------------------|
| Processor           | Two Intel Xeon Gold 5118 2.3 GHz, 24 cores |
| Memory              | DDR4 2666 MHz, 192 GB (16GB x 12)          |
| OS                  | Ubuntu 20.04 Server (kernel v5.4.0)        |
| Serverless Platform | OpenWhisk 1.0.0                            |

The evaluation can be reproduced on the hardware configurations that includes an Intel CPU.
This guide assumes a clean installation of Ubuntu 20.04 server.

## 2. Getting Started
Please refer to the instructions at the following link:
[Getting Started with REWIND](https://github.com/s3yonsei/rewind_serverless/tree/main?tab=readme-ov-file#2-getting-started)

Running REWIND will require three terminals, the first one running the OpenWhisk, and the second one running the file rewind Python code, and the final one for sending function request to the OpenWhisk.
To verify that the configuration of the REWIND has been successfully completed, run next commands in the first terminal:
```
$ cd rewind_serverless/openwhisk
$ sudo ./gradlew core:standalone:bootRun
```

Second terminal (do not close the 1st one):
```
$ cd rewind_serverless/rewind
$ sudo python3 file_rewinder.py
```

Third terminal (do not close the 1st/2nd ones):
```
$ cd rewind_serverless/atc24_ae/evaluation
$ sudo wsk action update --memory 128 helloworld ./workloads/hello.py --docker $(DOCKER_USER)/ubuntu-python-rewind
$ sudo wsk action invoke helloworld --result
```

If the REWIND configuration is successful, the following result should be displayed in the third terminal.
```
{
    "TrueTime": 0.0000045299530029296875,
    "greeting": "Hello stranger!",
    "runtime_end": 1715565302350653411,
    "runtime_start": 1715565302350417521,
    "startTime": 1715565302.3505592
}
```

## 3. Evaluation of REWIND

The following section reproduces evaluations for Figure 5-10 in the paper.
We first outline the experiments on REWIND's performance (Figure 6-8) and then describe how to profile REWIND (Figure 5, 9, 10).

Before getting start, OpenWhisk configuration is necessary if your system has multiple NUMA nodes.
To check NUMA nodes, run next commands:
```
$ lscpu | grep "NUMA node(s)"
```
If the printed result is larger than 1, configuring OpenWhisk is required to launch Docker containers on single NUMA node for removing NUMA effects.

The following example is configuring OpenWhisk to launch Docker containers fixed to NUMA node 0.
To check the core numbers in NUMA node 0, run the next command:
```
$ lscpu | grep "NUMA node0"
```

An example of printed output is as follows:
```
NUMA node0 CPU(s): 0,2,4,6,8,10,12,14,16,18,20,22
```

Code for launching Docker container in OpenWhisk is implemented in the file `rewind_serverless/openwhisk/core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool/docker/DockerContainer.scala`.
Insert following code snippet starting from line 43:
```
object cpus {
    var useCPU: Int = 0
    def getCPU(): Int = {
        useCPU = (useCPU + 2) % 24
        if (useCPU == 0)
                useCPU = 2
        useCPU
    }
}
```
The value `24` in the code snippet means the number of total CPU cores in example system.
Modifying the following code is also required:
```
val args = Seq(
  "--cpu-shares",
  cpuShares.toString,
  "--memory",
  s"${memory.toMB}m",
  "--memory-swap",
  s"${memory.toMB}m",
  "--network",
  network) ++
  environmentArgs ++
  dnsServers.flatMap(d => Seq("--dns", d)) ++
  dnsSearch.flatMap(d => Seq("--dns-search", d)) ++
  dnsOptions.flatMap(d => Seq(dnsOptString, d)) ++
  name.map(n => Seq("--name", n)).getOrElse(Seq.empty) ++
  params
```
Change the above code as follows:
```
val useCPU = cpus.getCPU()
val cpuset = Seq("--cpuset-cpus", useCPU,toString)
val args = Seq(
  "--cpu-shares",
  cpuShares.toString,
  "--memory",
  s"${memory.toMB}m",
  "--memory-swap",
  s"${memory.toMB}m",
  "--network",
  network) ++
  cpuset ++
  environmentArgs ++
  dnsServers.flatMap(d => Seq("--dns", d)) ++
  dnsSearch.flatMap(d => Seq("--dns-search", d)) ++
  dnsOptions.flatMap(d => Seq(dnsOptString, d)) ++
  name.map(n => Seq("--name", n)).getOrElse(Seq.empty) ++
  params
```

This section requires gnuplot.
Install the gnuplot package:
```
sudo apt-get install gnuplot
```

### Figure 6 (throughput) and 7 (CDF of function end-to-end time)
Before conducting the experiment, it is required to configure the memory size for the container pool in OpenWhisk.
This can be achieved by adjusting the `user-memory` value under the `container-pool` section within the `rewind_serverless/openwhisk/core/invoker/src/main/resources/application.conf` file.
For instance, setting `user-memory = 1024 m` would allocate 1GB of memory to OpenWhisk's container pool.
In Figure 5, the `user-memory` values were configured as follows for each experiment: 1024, 2560, 4096, and 8192.

After configuring the `user-memory` size, run next commands for throughput results:
```
$ cd rewind_serverless/atc24_ae/evaluation/throughput
$ sudo ./run.sh $(DOCKER_USER)
```
It takes approximately 2 hours for the results to come out.
To shorten the experiment time, you can decrease the `ITER_MAX` value in the `run.sh`, which is a value indicating the number of iterations.
When the experiment is finished, the throughput for each iteration is displayed in the terminal.
An example of printed output is as follows:
```
(Iteration 1) Throughput: 17.635092 requests/second
```

To generate the CDF graph, run next command with the number of iterations of the experiments:
```
$ ./cdf.sh $ITERATION
```
This creates a file named `cdf.eps`, containing the CDF graph.

For all subsequent experiments, the `user-memory` value was fixed at 8192.

### Figure 8 (Run-to-Run execution time)

Run next commands for the run-to-run experiment results:
```
$ cd rewind_serverless/atc24_ae/evaluation/runtorun
$ sudo ./run.sh $(DOCKER_USER)
```
It takes approximately 5 minutes for the results to come out.
When the experiment is finished, the execution time for each run is displayed in the terminal.
An example of printed output is as follows:
```
(run-to-run #1 of linpack) time: 38.623650 ms
```


### Figure 5 (Resident Set Size)

Run next commands for the size of the container's resident set size (RSS):
```
$ cd rewind_serverless/atc24_ae/evaluation/rss
$ sudo ./run.sh $(DOCKER_USER)
```
It takes approximately 5 minutes for the results to come out.
When the experiment is finished, the RSS of the function is displayed in the terminal.
An example of printed output is as follows:
```
RSS of hello: 10800 kB
```

### Figure 9 (Checkpoint time) and 10 (Rewind time)

Run next commands for the checkpoint/rewind time:
```
$ cd rewind_serverless/atc24_ae/evaluation/cr
$ sudo ./run.sh $(DOCKER_USER)
```
It takes approximately 10 minutes for the results to come out.
When the experiment is finished, the checkpoint/rewind times are displayed in the terminal.
An example of printed output is as follows:
```
checkpoint/rewind time of matmul: 0.251824 / 1.124923 ms
```

