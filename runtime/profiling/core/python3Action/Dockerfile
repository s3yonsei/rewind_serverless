#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get install -y build-essential linux-headers-generic libglib2.0-dev

# build go proxy from source
#FROM golang:1.18 AS builder_source
#ARG GO_PROXY_GITHUB_USER=apache
#ARG GO_PROXY_GITHUB_BRANCH=master
#RUN git clone --branch ${GO_PROXY_GITHUB_BRANCH} \
#   https://github.com/${GO_PROXY_GITHUB_USER}/openwhisk-runtime-go /src ;\
#   cd /src ; env GO111MODULE=on CGO_ENABLED=0 go build main/proxy.go && \
#   mv proxy /bin/proxy

# or build it from a release
#FROM golang:1.18 AS builder_release
#ARG GO_PROXY_RELEASE_VERSION=1.18@1.20.0
#RUN curl -sL \
#  https://github.com/apache/openwhisk-runtime-go/archive/{$GO_PROXY_RELEASE_VERSION}.tar.gz\
#  | tar xzf -\
#  && cd openwhisk-runtime-go-*/main\
#  && GO111MODULE=on CGO_ENABLED=0 go build -o /bin/proxy

FROM golang:1.15 AS builder_source
RUN mkdir -p /src
COPY proxy /src
RUN cd /src ; env GO111MODULE=on CGO_ENABLED=0 go build main/proxy.go && \
    mv proxy /bin/proxy

FROM python:3.8.2-buster

# select the builder to use
#ARG GO_PROXY_BUILD_FROM=release
ARG GO_PROXY_BUILD_FROM=source

# Install common modules for python
COPY requirements_common.txt requirements_common.txt
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip six wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gevent==21.12.0 flask==2.2.2 && \
    pip install --no-cache-dir mypy==0.982 django==4.1.2 numpy==1.23.3 pyaes==1.6.1 && \
    pip install --no-cache-dir sphinx==5.2.3 chameleon==3.10.1 igraph==0.10.1 && \
    pip install --no-cache-dir boto3==1.24.89 pillow==9.2.0 && \
    pip install --no-cache-dir opencv-python-headless==4.9.0.80 && \
    pip install --no-cache-dir scikit-learn==1.3.2 pandas==2.0.3 torch==2.1.2 tensorflow==2.13.1 keras_applications==1.0.8

RUN mkdir -p /action
WORKDIR /

COPY --from=builder_source /bin/proxy /bin/proxy_source
#COPY --from=builder_release /bin/proxy /bin/proxy_release
RUN mv /bin/proxy_${GO_PROXY_BUILD_FROM} /bin/proxy

ADD bin/compile /bin/compile
ADD lib/launcher.py /lib/launcher.py

# log initialization errors
# ENV OW_LOG_INIT_ERROR=1
# the launcher must wait for an ack
ENV OW_WAIT_FOR_ACK=1
# execution environment
ENV OW_EXECUTION_ENV=openwhisk/ubuntu-python-rewind-rss
# compiler script
ENV OW_COMPILER=/bin/compile

ENTRYPOINT ["/bin/proxy"]
