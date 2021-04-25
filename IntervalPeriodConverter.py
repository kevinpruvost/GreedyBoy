#!/usr/bin/env python
## IntervalPeriodConverter.py
##
## Description:
## Converts the data from the ["Date", "Price"] to wanted interval period prices.
## The purpose is to make it easier and more practical to use.
##

__author__      = "Kevin Pruvost"
__copyright__   = "Copyright 2021, GreedyBoy"
__credits__     = ["Kevin Pruvost", "Hugo Matthieu-Steinbach"]
__license__     = "Proprietary"
__version__     = "1.0.0"
__maintainer__  = "Kevin Pruvost"
__email__       = "pruvostkevin0@gmail.com"
__status__      = "Test"

import pandas as pd

class IntervalPeriodConverter:
    def __init__(self, data, interval="15"):
        """Constructs IntervalPeriodConverter with the given data.
        :param interval: Interval in minutes.
        """
        self.data = data.rolling(interval + 'T')
        return

    def append(self, to_append):
        return

data = pd.read_csv("data.csv")
data = IntervalPeriodConverter(data)