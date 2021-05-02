#!/usr/bin/env python
"""
## PerformanceTimer.py
## Description:
## Measures the time the input function has to take to execute completely.
##
"""

__author__      = "Kevin Pruvost"
__copyright__   = "Copyright 2021, GreedyBoy"
__credits__     = ["Kevin Pruvost", "Hugo Matthieu-Steinbach"]
__license__     = "Proprietary"
__version__     = "1.0.0"
__maintainer__  = "Kevin Pruvost"
__email__       = "pruvostkevin0@gmail.com"
__status__      = "Test"

import time

def time_function(func, *args, **kwargs):
    begin = time.perf_counter()
    func(*args, **kwargs)
    print(func.__name__ + " took " + str(time.perf_counter() - begin) + "seconds to execute.")