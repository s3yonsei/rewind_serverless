
# REWIND: Secure, Fast, and Resource-efficient Serverless Environment

REWIND is a serverless function execution platform designed to address security and efficiency concerns.
REWIND ensures that after each function request, the container is reset to an initial state, free from any sensitive data, including a thorough restoration of the file system to prevent data leakage.
It incorporates a kernel-level memory snapshot management system, which significantly lowers memory usage and accelerates the rewind process.
Furthermore, REWIND has user-level file snapshot management schemes for container filesystem.
REWIND also optimizes runtime by reusing memory regions and leveraging the temporal locality of function executions, enhancing performance while maintaining strict data isolation between requests.
The REWIND is implemented on OpenWhisk and Linux.

## Related Paper

Please refer the paper for a comprehensive description of REWIND:

**A Secure, Fast, and Resource-Efficient Serverless Platform with Function REWIND**, Jaehyun Song, Bumsuk Kim, Minwoo Kwak, Byoungyoung Lee, Euiseong Seo, and Jinkyu Jeong, Proceedings of the 2024 USENIX Annual Technical Conference (USENIX ATC '24), Santa Clara, CA, US, July 10-12, 2024 (to appear)

**Contacts**: Please contact us if you have any questions. [Jaehyun Song](mailto:jaehyun.song@csi.skku.edu), [Jinkyu Jeong](mailto:jinkyu@yonsei.ac.kr), [Scalable Systems Software Lab](https://cslab.yonsei.ac.kr), Yonsei University, South Korea


## Contents
- [1. Getting Started](#1-getting-started)
- [2. Kernel Build](#2-kernel-build)
- [3. OpenWhisk Setup](#3-openwhisk-and-runtime-setup)
- [4. Applying REWIND](#4-applying-rewind)

## 1. Getting Started

Make your home directory the working directory.
```
$ cd ~
$ git clone --recursive https://github.com/s3yonsei/rewind_serverless.git
```

For the experiment, building the modified kernel and configuring the OpenWhisk are essential.
Once the above commands are executed, the modified kernel and OpenWhisk will be downloaded into the `rewind_serverless/rewind/kernel` and `rewind_serverless/openwhisk` directories.
Further details on kernel build and OpenWhisk setup are provided starting from [Section 2](#2-kernel-build) and [Section 3](#3-openwhisk-and-runtime-setup).

## 2. Kernel Build

Before building the kernel, ensure the following packages are installed:
```
$ sudo apt-get update
$ sudo apt-get install build-essential libncurses5 libncurses5-dev bin86 kernel-package libssl-dev bison flex libelf-dev
```

Configure the kernel:
```
$ cd rewind_serverless/rewind/kernel
$ make menuconfig
```

To prepare for building, adjust the `.config` file by setting `CONFIG_SYSTEM_TRUSTED_KEYS` and `CONFIG_SYSTEM_REVOCATION_KEYS` to empty strings (""), if they exist.
```
CONFIG_SYSTEM_TRUSTED_KEYS=""
CONFIG_SYSTEM_REVOCATION_KEYS=""
```

Build the kernel:
```
$ make -j$(nproc)
$ sudo make modules_install -j$(nproc)
$ sudo make install -j$(nproc)
```
Adjust the value of `nproc` to suit your environment.
For example, if your system has 4 CPU cores, consider setting it to `$ make -j4`.

Before restarting the system, it is necessary to configure the `GRUB_CMDLINE_LINUX` value in the GRUB configuration file.
The path of the GRUB configuration file is `/etc/default/grub`.
```
GRUB_CMDLINE_LINUX="transparent_hugepage=never intel_idle.max_cstate=1 intel_pstate=disable numa_balancing=disable"
```

Apply modified grub file:
```
$ sudo update-grub
```

Restart the system and boot into the newly built kernel. To verify the kernel version:
```
$ uname -r
```

## 3. OpenWhisk and Runtime Setup

Before setting the OpenWhisk, ensure the following packages are installed:
```
# Install JAVA, NPM, and NodeJS
$ sudo apt install openjdk-11-jre npm nodejs

# Install Docker
$ sudo apt-get install ca-certificates curl
$ sudo install -m 0755 -d /etc/apt/keyrings
$ sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
$ sudo chmod a+r /etc/apt/keyrings/docker.asc
$ echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
$ sudo apt-get update
$ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

To make use of all OpenWhisk features, the OpenWhisk command line tool called `wsk` is required.
`wsk` can be downloaded from https://s.apache.org/openwhisk-cli-download, which site provides binaries for a variety of architectures.
An example of `wsk` download for amd64 architecture is as follows:
```
$ wget https://github.com/apache/openwhisk-cli/releases/download/1.2.0/OpenWhisk_CLI-1.2.0-linux-amd64.tgz
$ tar xvf OpenWhisk_CLI-1.2.0-linux-amd64.tgz
$ sudo mv wsk /usr/bin
```

To quick start, OpenWhisk is need to set up in Standalone mode.
To configure the Standalone OpenWhisk, run commands as follows:
```
$ wsk property set --apihost 'http://localhost:3233' --auth '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
$ cd rewind_serverless/openwhisk
$ sudo su
# ./gradlew core:standalone:bootRun
```

After initiating OpenWhisk in standalone mode, setting up the OpenWhisk runtime becomes imperative.
To do so, Docker registry account, such as Docker Hub, is required.
The following assumes that `DOCKER_USER` is properly configured with an appropriate value.
```
# docker login --username $DOCKER_USER
```

To build the runtime image for REWIND:
```
$ cd rewind_serverless/runtime/mem-file
$ sudo su
# ./gradlew core:python3Action:distDocker
# sudo ./gradlew distDocker -PdockerImagePrefix=$DOCKER_USER -PdockerRegistry=docker.io
```

(Optional) To profile REWIND, an additional runtime image is necessary.
To build the runtime image for profiling REWIND:
```
$ cd rewind_serverless/runtime/profiling
$ sudo su
# sudo ./gradlew core:python3Action:distDocker
# sudo ./gradlew distDocker -PdockerImagePrefix=$DOCKER_USER -PdockerRegistry=docker.io
```

## 4. Applying REWIND

REWIND's kernel introduces three new system calls - **checkpoint**, **rewind**, and **rewindable** - to manage memroy snapshots.
At the user level, REWIND provides the Python code `file_rewinder.py` for managing file snapshots.

### Rewindable
The `rewindable` system call configures the child process of the calling process to be a REWIND process.
Within a container running on OpenWhisk, a proxy process faciliates communication with OpenWhisk, receiving user requests and forwarding them to the launcher process for execution.
This proxy process is the initial process upon container creation, with the launcher process subsequently spawned from it.
Thus, the `rewindable` system call is invoked from the proxy process.
The following example demonstrates invoking the `rewindable` system call from the file `rewind_serverless/runtime/mem-file/core/python3Action/proxy/openwhisk/initHandler.go`.

```
python_code := "import ctypes; syscall = ctypes.CDLL(None).syscall; syscall(550)"
```

In the REWIND kernel, the system call number for `rewindable` is `550`.

### Checkpoint and Rewind
The `checkpoint` system call captures a snapshot of the memory of the calling process using REWIND's schemes.
The `rewind` system call restores the memory of the calling process according to the REWIND scheme.
Handling both file snapshots and file rewinds is managed by `file_rewinder.py`.
The checkpoint and rewind operations are initiated from the launcher process.
Below is an example code snippet in the file `rewind_serverless/runtime/mem-file/core/python3Action/lib/launcher.py`.

```
...
import os
import ctypes

syscall = ctypes.CDLL(None).syscall

myname = os.popen("cat /etc/hostname").read().split('\n')[0]
CHK="checkpoint"
REW="rewind"

file_sock = socket(AF_INET, SOCK_STREAM)
file_sock.connect(('172.17.0.1', 40510))
file_sock.send(myname.encode('utf-8'))

i = 0
while True:
   if i == 1:
      file_sock.send(CHK.encode('utf-8'))
      syscall(548, 1)
   if i > 1:
      file_sock.send(REW.encode('utf-8'))
      syscall(549, 1)

   i += 1

   FUNCTION EXECUTION
```

In the REWIND kernel, the system call numbers for `checkpoint` and `rewind` are `548` and `549` each.




