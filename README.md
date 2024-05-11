
# REWIND: Secure, Fast, and Resource-efficient Serverless Environment

REWIND is an innovative and efficient serverless function execution platform designed to address security and efficiency concerns.
REWIND ensures that after each function request, the container is reset to an initial state, free from any sensitive data, including a thorough restoration of the file system to prevent data leakage.
It incorporates a kernel-level memory snapshot management system, which significantly lowers memory usage and accelerates the rewind process.
Furthermore, REWIND has user-level file snapshot management system for container filesystem.
REWIND also optimizes runtime by reusing memory regions and leveraging the temporal locality of function executions, enhancing performance while maintaining strict data isolation between requests.
The REWIND is implemented on OpenWhisk and Linux.

## Related Paper

Please refer the paper for a comprehensive description of REWIND:

**A Secure, Fast, and Resource-Efficient Serverless Platform with Function REWIND**

Author: Jaehyun Song, Bumsuk Kim, Minwoo Kwak, Byoungyoung Lee, Euiseong Seo, and Jinkyu Jeong

Conference: 2024 USENIX Annual Technical Conference (USENIX ATC'24)

Contact: Jaehyun Song (jaehyun.song@csi.skku.edu)

## Contents
- [1. Getting Started](#1-getting-started)
- [2. Kernel Build](#2-kernel-build)
- [3. OpenWhisk Setup](#3-openwhisk-and-runtime-setup)
- [4. Secure Container with REWIND](#4-secure-container-with-rewind)

## 1. Getting Started

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
Further details on kernel build and OpenWhisk setup are provided starting from [Section 2](#2-kernel-build) and [Section 3](#3-openwhisk-and-runtime-setup).

## 2. Kernel Build

Before building the kernel, ensure the following packages are installed:
```bash
sudo apt-get update
sudo apt-get install build-essential libncurses5 libncurses5-dev bin86 kernel-package libssl-dev bison flex libelf-dev
```

Configure the kernel:
```bash
cd rewind_serverless/rewind/kernel
make olddefconfig
```

To prepare for building, adjust the `.config` file by setting `CONFIG_SYSTEM_TRUSTED_KEYS` and `CONFIG_SYSTEM_REVOCATION_KEYS` to empty strings ("").
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

## 3. OpenWhisk and Runtime Setup

To evaluate artifact, OpenWhisk is need to set up in standalone mode.
```bash
cd rewind_serverless/openwhisk
./gradlew core:standalone:bootRun
```

After initiating OpenWhisk in standalone mode, setting up the OpenWhisk runtime becomes imperative.
To do so, Docker registry account, such as Docker Hub, is required.
The following assumes that `DOCKER_USER` is properly configured with an appropriate value.
```bash
docker login --username $DOCKER_USER
```

To build the runtime image for REWIND, execute the following commands.
```bash
cd rewind_serverless/runtime/mem-file
./gradlew core:python3Action:distDocker
./gradlew distDocker -PdockerImagePrefix=$DOCKER_USER -PdockerRegistry=docker.io
```

To profile REWIND (e.g., container's RSS), an additional runtime image is necessary.
To build the runtime image for profiling REWIND, execute the following commands.
```bash
cd rewind_serverless/runtime/profiling
./gradlew core:python3Action:distDocker
./gradlew distDocker -PdockerImagePrefix=$DOCKER_USER -PdockerRegistry=docker.io
```

## 4. Secure Container with REWIND

To manage memory snapshot, REWIND's kernel has three new system calls: **checkpoint**, **rewind**, and **rewindable**.
`checkpoint` take a REWIND's snapshot of the memory of the calling process.
`rewind` restore the memory of the calling process with the REWIND scheme.
`rewindable` sets the child process of the calling process to be a REWIND process.
To manage file snapshot at user-level, REWIND provides Python code.

### rewindable system call
TBD

### checkpoint
TBD

### rewind
TBD

