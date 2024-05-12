
# USENIX ATC'24 Artifacts Evaluation

## Title: A Secure, Fast, and Resource-Efficient Serverless Platform with Function REWIND

Author: Jaehyun Song, Bumsuk Kim, Minwoo Kwak, Byoungyoung Lee, Euiseong Lee, and Jinkyu Jeong

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

The evaluation can be reproduced on the hardware configurations that includes an Intel CPU.
This guide assumes a clean installation of Ubuntu 20.04 server.

## 2. Getting Started
Please refer to the following instructions: [Getting Started with REWIND](https://github.com/s3yonsei/rewind_serverless/tree/main?tab=readme-ov-file#2-getting-started)

## 3. Evaluation of REWIND

The followings are evaluations for Figure 5-10 in the paper.
We first outlines the experiments on REWIND's performance (Figure 6-10) and then describe how to profile REWIND's memory usage (Figure 5).

### Figure 6 (throughput) and 7 (CDF of function end-to-end time)
Before conducting the experiment, it is required to configure the memory size for the container pool in OpenWhisk.
This can be achieved by adjusting the `user-memory` value under the `container-pool` section within the `rewind_serverless/openwhisk/core/invoker/src/main/resources/application.conf` file.
For instance, setting `user-memory = 1024 m` would allocate 1GB of memory to OpenWhisk's container pool.
In Figure 5, the `user-memory` values were configured as follows for each experiment: 1024, 2560, 4096, and 8192.

After configuring the `user-memory` size, run next commands for throughput results.
```bash
cd rewind_serverless/atc24_ae/evaluation/throughput
./run.sh $DOCKER_USER
```
It takes approximately 2 hours for the results to come out.
To shorten the experiment time, you can decrease the `ITER_MAX` value in the `run.sh`, which is a value indicating the number of iterations.
When the experiment is finished, the throughput for each iteration is displayed in the terminal.
An example of printed output is as follows:
```bash
(Iteration 1) Throughput: 17.635092 requests/second
```

To generate the CDF graph, run next command with the number of iterations of the experiments:
```bash
./cdf.sh $ITERATION
```
This creates a file named `cdf.eps`, containing the CDF graph.

For all subsequent experiments, the `user-memory` value was fixed at 4096.

### Figure 8 (Run-to-Run execution time)

Run next commands for the run-to-run experiment results:
```bash
cd rewind_serverless/atc24_ae/evaluation/runtorun
./run.sh $DOCKER_USER
```
It takes approximately 5 minutes for the results to come out.
When the experiment is finished, the execution time for each run is displayed in the terminal.
An example of printed output is as follows:
```bash
(run-to-run #1 of linpack) time: 38.623650 ms
```

### Figure 9 (Checkpoint time) and 10 (Rewind time)

Run next commands for the checkpoint/rewind time:
```bash
cd rewind_serverless/atc24_ae/evaluation/cr
./run.sh $DOCKER_USER
```
It takes approximately 10 minutes for the results to come out.
When the experiment is finished, the checkpoint/rewind times are displayed in the terminal.
An example of printed output is as follows:
```bash
checkpoint/rewind time of matmul: 0.251824 / 1.124923 ms
```

### Figure 5 (Resident Set Size)

Run next commands for the size of the container's resident set size (RSS):
```bash
cd rewind_serverless/atc24_ae/evaluation/rss
./run.sh $DOCKER_USER
```
It takes approximately 5 minutes for the results to come out.
When the experiment is finished, the RSS of the function is displayed in the terminal.
An example of printed output is as follows:
```bash
RSS of hello: 10800 kB
```
