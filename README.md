
# USENIX ATC'24 Artifacts Evaluation

## Title: A Secure, Fast, and Resource-Efficient Serverless Platform with Function REWIND
Contact: Jaehyun Song (jaehyun.song@csi.skku.edu)

This repository reproduces the evaluation presented in the paper published at USENIX ATC '24.

## Contents
- [1. Configurations](#1-configurations)
- [2. Getting Started](#2-getting-started)
- [3. Kernel Build](#3-kernel-build)
- [4. OpenWhisk Setup](#4-openwhisk-setup)

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
git clone https://github.com/s3yonsei/rewind_atc24_ae.git
```

Obtain the required code from GitHub by execution the following commands.
```bash
cd rewind_atc24_ae
git clone https://github.com/s3yonsei/rewind_serverless.git
git clone -b 1.0.0 https://github.com/apache/openwhisk.git
```

For the experiment, building the modified kernel and configuring the OpenWhisk are essential. Once the above commands are executed, the modified kernel and OpenWhisk will be downloaded into the `rewind_serverless/kernel` and `openwhisk` directories. Further details on kernel build and OpenWhisk setup are provided starting from [Section 3](#3-kernel-build) and [Section 4](#4-openwhisk-setup).

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

## 4. OpenWhisk Setup

In the artifact evaluation, OpenWhisk is set up in standalone mode.
```bash
cd ~/rewind_atc_24_ae/openwhisk
./gradlwe core:standalone:bootRun
```

## 5. Evaluation of REWIND

The following are evaluations for Fig 5-10 in the paper.

### Figure 5
TBD

### Figure 6
TBD

### Figure 7
TBD

### Figure 8

### Figure 9 and 10
TBD
