import math
import time

def float_operations(n):
    start = time.time()
    for i in range(0, n):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    latency = time.time() - start
    return latency


def main(args):
    result = {}
    startTime = time.time()
    num = int(args.get('n', '100000'))
    latency = float_operations(num)
    endTime = time.time()
    result['startTime'] = startTime
    result['latency'] = latency
    result['functionTime'] = endTime - startTime
    return result
