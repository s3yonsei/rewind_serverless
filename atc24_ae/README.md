
# USENIX ATC'24 Artifacts Evaluation

## Title: A Secure, Fast, and Resource-Efficient Serverless Platform with Function REWIND
Contact: Jaehyun Song (jaehyun.song@csi.skku.edu)

This repository reproduces the evaluation presented in the paper published at USENIX ATC '24.

## Contents
- [1. Configurations](#1-configurations)
- [2. Getting Started](#2-getting-started)
- [3. Evaluation of REWIND](#3-evaluation-of-rewind)

## 1. Configurations

The experimental environment was performed on the following hardware configurations:

| **Component**       | **Specification**
|---------------------|--------------------------------------------|
| Processor           | Two Intel Xeon Gold 5118 2.3 GHz, 24 cores |
| Memory              | DDR4 2666 MHz, 192 GB (16GB x 12)          |
| OS                  | Ubuntu 20.04 Server (kernel v5.4.0)        |
| Serverless Platform | OpenWhisk 1.0.0                            |

The evaluation can be reproducible on other hardware configurations, provided they have an Intel CPUs.
This guide is assumes a clean installation of Ubuntu 20.04 server.

## 2. Getting Started
Please follow the instructions in [Getting Started with REWIND](https://github.com/s3yonsei/rewind_serverless/tree/main?tab=readme-ov-file#2-getting-started)

## 3. Evaluation of REWIND

The following are evaluations for Figure 5-10 in the paper.
First, the experiment concerning REWIND's performance (Figure 6-10) is outlined, followed by a description of profiling REWIND's memory usage (Figure 5).

### Figure 6 (throughput) and 7 (CDF of function end-to-end time)
Prior to conducting the experiment, it's essential to configure the memory size for the container pool in OpenWhisk.
This can be achieved by adjusting the `user-memory` value under the `container-pool` section within the `rewind_serverless/openwhisk/core/invoker/src/main/resources/application.conf` file.
For instance, setting `user-memory = 1024 m` would allocate 1GB of memory to OpenWhisk's container pool.
In Figure 5, the `user-memory` values were configured as follows for each experiment: 1024, 2560, 4096, and 8192.

After configuring the `user-memory` size, executing the following commands makes the throughput results.
```bash
cd rewind_serverless/evaluation/throughput
./run.sh $DOCKER_USER
```
Obtaining the throughput results may take nearly 2 hour or more to complete.
To shorten the experiment time, decrease the value of `ITER_MAX` in the `run.sh`, which represents the number of iterations.
At the finish of the experiment, the throughput for each iteration is displayed in the terminal.
For example, `(Iteration 1) Throughput: 17.635092 requests/second`.

To generate the CDF graph, execute the following command with the number of iterations of the experiments.
```bash
./cdf.sh $ITERATION
```
After executing the command, a file named `cdf.eps` will be generated containing the CDF graph.

In all subsequent experiments, the `user-memory` value is configured to 4096.

### Figure 8 (Run-to-Run execution time)

To aqcuire the run-to-run experiment results, execute the following commands.
```bash
cd rewind_serverless/evaluation/runtorun
./run.sh $DOCKER_USER
```
This process may take nearly 5 minutes or more to complete.
At the finish of the experiment, the execution time of the function for each run is displayed in the terminal.
For example, `(run-to-run #1 of linpack) time: 38.623650 ms`.

### Figure 9 (Checkpoint time) and 10 (Rewind time)

For obtaining the checkpoint/rewind time, execute the following commands.
```bash
cd rewind_serverless/evaluation/cr
./run.sh $DOCKER_USER
```
This process may take nearly 10 minutes or more to complete.
At the finish of the experiment, the checkpoint/rewind time of the function is displayed in the terminal.
For example, `checkpoint/rewind time of matmul: 0.251824 / 1.124923 ms`.

### Figure 5 (RSS)

To obtain the size of the container's RSS, execute the following commands.
```bash
cd rewind_serverless/evaluation/rss
./run.sh $DOCKER_USER
```
This step may take nearly 5 minutes or more to complete.
At the finish of the experiment, the RSS of the function is displayed in the terminal.
For example, `RSS of hello: 10800 kB`.
