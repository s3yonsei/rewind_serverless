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
from __future__ import print_function
from sys import stdin
from sys import stdout
from sys import stderr
from os import fdopen
import sys, os, json, traceback, warnings
import ctypes
import time
from socket import *

syscall = ctypes.CDLL(None).syscall

myname = os.popen("cat /etc/hostname").read().split('\n')[0]
CHK="checkpoint"
REW="rewind"

try:
  # if the directory 'virtualenv' is extracted out of a zip file
  path_to_virtualenv = os.path.abspath('./virtualenv')
  if os.path.isdir(path_to_virtualenv):
    # activate the virtualenv using activate_this.py contained in the virtualenv
    activate_this_file = path_to_virtualenv + '/bin/activate_this.py'
    if not os.path.exists(activate_this_file): # try windows path
      activate_this_file = path_to_virtualenv + '/Scripts/activate_this.py'
    if os.path.exists(activate_this_file):
      with open(activate_this_file) as f:
        code = compile(f.read(), activate_this_file, 'exec')
        exec(code, dict(__file__=activate_this_file))
    else:
      sys.stderr.write("Invalid virtualenv. Zip file does not include 'activate_this.py'.\n")
      sys.exit(1)
except Exception:
  traceback.print_exc(file=sys.stderr, limit=0)
  sys.exit(1)

# now import the action as process input/output
from main__ import main as main

out = fdopen(3, "wb")
if os.getenv("__OW_WAIT_FOR_ACK", "") != "":
    out.write(json.dumps({"ok": True}, ensure_ascii=False).encode('utf-8'))
    out.write(b'\n')
    out.flush()

file_sock = socket(AF_INET, SOCK_STREAM)
file_sock.connect(('172.17.0.1', 40510))
file_sock.send(myname.encode('utf-8'))

#################### RSS Profiling ####################
proxy_path = "/proc/1/status"
launcher_path = "/proc/" + str(os.getpid()) + "/status"
#######################################################

env = os.environ
i = 0
while True:
  checktime = 0
  if i == 1:
    check_start = time.time()
    file_sock.send(CHK.encode('utf-8'))
    syscall(548, 1)
    checktime = time.time() - check_start
  if i > 1:
    rewind_log = open("/tmp/rewind.out", 'a')
    rewind_log.write(time.time())
    rewind_log.close()
    file_sock.send(REW.encode('utf-8'))
    syscall(549, 2)

  timestamp = time.time()
  i +=1
  line = stdin.readline()
  if not line: break
  args = json.loads(line)
  payload = {}
  for key in args:
    if key == "value":
      payload = args["value"]
    else:
      env["__OW_%s" % key.upper()]= args[key]
  res = {}
  try:
    start = time.time()
    res = main(payload)
    TrueTime = time.time() - start
    res["TrueTime"] = TrueTime
    res["CheckpointTime"] = checktime
    res["Timestamp"] = timestamp
  except Exception as ex:
    print(traceback.format_exc(), file=stderr)
    res = {"error": str(ex)}
  out.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
  out.write(b'\n')
  stdout.flush()
  stderr.flush()
  out.flush()

  ################### RSS Profiling ####################
  proxy_file = open(proxy_path, 'r')
  proxy_log = open("/tmp/proxy.out", 'a')
  while True:
    proxy_line = proxy_file.readline()
    if not proxy_line: break
    proxy_log.write(proxy_line)
  proxy_file.close()
  proxy_log.close()

  launcher_file = open(launcher_path, 'r')
  launcher_log = open("/tmp/launcher.out", 'a')
  while True:
    launcher_line = launcher_file.readline()
    if not launcher_line: break
    launcher_log.write(launcher_line)
  launcher_file.close()
  launcher_log.close()
######################################################
