
# USENIX ATC'24 Artifacts Evaluation

## Title: A Secure, Fast, and Resource-Efficient Serverless Platform with Function REWIND
Contact: Jaehyun Song (jaehyun.song@csi.skku.edu)

This repository reproduces the evaluation presented in the paper published at USENIX ATC '24.

## Contents
- [1. Configurations](#1-configurations)
- [2. Getting Started](#2-getting-started)
- [3. Kernel Build](#3-kernel-build)
- [4. OpenWhisk Setup](#4-openwhisk-and-runtime-setup)
- [5. Evaluation of REWIND](#5-evaluation-of-rewind)

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

We presume that the user's home directory serves as the working directory.
```bash
cd ~
git clone https://github.com/s3yonsei/rewind_serverless.git
```

Obtain the OpenWhisk source code from GitHub by execution the following commands.
```bash
cd rewind_serverless
git clone -b 1.0.0 https://github.com/apache/openwhisk.git
```

For the experiment, building the modified kernel and configuring the OpenWhisk are essential.
Once the above commands are executed, the modified kernel and OpenWhisk will be downloaded into the `rewind_serverless/kernel` and `openwhisk` directories.
Further details on kernel build and OpenWhisk setup are provided starting from [Section 3](#3-kernel-build) and [Section 4](#4-openwhisk-and-runtime-setup).

## 3. Kernel Build

Before building the kernel, ensure the following packages are installed:
```bash
sudo apt-get update
sudo apt-get install build-essential libncurses5 libncurses5-dev bin86 kernel-package libssl-dev bison flex libelf-dev
```

Configure the kernel:
```bash
cd rewind_serverless/kernel
make olddefconfig
```

To prepare for building, adjust the `.config` file by setting `CONFIG_SYSTEM_TRUSTED_KETS` and `CONFIG_SYSTEM_REVOCATION_KEYS` to empty strings ("").
```bash
CONFIG_SYSTEM_TRUSTED_KEYS=""
CONFIG_SYSTEM_REVOCATION_KEYS=""
```

Build the kernel:
```bash
make -j$(nproc)
sudo make modules_install
sudo make install
```

Restart the system and boot into the newly built kernel. To verify the kernel version:
```bash
uname -r
```

## 4. OpenWhisk and Runtime Setup

To evaluate artifact, OpenWhisk is need to set up in standalone mode.
```bash
cd rewind_serverless/openwhisk
./gradlwe core:standalone:bootRun
```

After initiating OpenWhisk in standalone mode, setting up the OpenWhisk runtime becomes imperative.
To do so, Docker registry account, such as Docker Hub, is required.
The following assumes that `DOCKER_USER` is properly configured with an appropriate value.
```bash
docker login --username $DOCKER_USER
```

To build the runtime image for REWIND, execute the following commands.
```bash
cd rewind_serverless/mem-file
./gradlew core:python3Action:distDocker
./gradlew distDocker -PdockerImagePrefix=$DOCKER_USER -PdockerRegistry=docker.io
```

To profile REWIND (e.g., container's RSS), an additional runtime image is necessary.
To build the runtime image for profiling REWIND, execute the following commands.
```bash
cd rewind_serverless/profiling
./gradlew core:python3Action:distDocker
./gradlew distDocker -PdockerImagePrefix=$DOCKER_USER -PdockerRegistry=docker.io
```

## 5. Evaluation of REWIND

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

In all subsequent experiments, the `user-memory` value is configured to 4096.

### Figure 8 (Run-to-Run execution time)
```bash
cd rewind_serverless/evaluation/runtorun
./run.sh $DOCKER_USER
```

### Figure 9 (Checkpoint time) and 10 (Rewind time)
```bash
cd rewind_serverless/evaluation/cr
./run.sh $DOCKER_USER
```

### Figure 5 (RSS)
```bash
cd rewind_serverless/evaluation/rss
./run.sh $DOCKER_USER
```
