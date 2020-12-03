#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import sys
import time
import datetime

sys.setrecursionlimit(10 ** 9)

@functools.lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n -1) + fib(n - 2)

start_time = time.time()
print(fib(10000))
print('cost: ', time.time() - start_time)

