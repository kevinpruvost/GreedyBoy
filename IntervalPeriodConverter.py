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
import pandas.core.generic as gen
from numba import jit
import copy

class IntervalPeriodConverter:
    def __init__(self, data: gen.NDFrame, interval: int = 15):
        """Constructs IntervalPeriodConverter with the given data.
        :param interval: Interval in minutes.
        """
        self.data = data
        self.interval = interval
        self.roundTemp = {
            'Date': 0,
            'Open': 0,
            'High': 0,
            'Low': 0,
            'Close': 0
        }
        self.newRound = copy.deepcopy(self.roundTemp)
        if 'Low' not in data:
            self.ordered = pd.DataFrame()
            self.parseToInterval()
        else:
            self.ordered = data
        return

    def parseToInterval(self):
        for i, row in self.data.iterrows():
            self.__append(row['epoch'], row['price'])
        self.update()
#        self.ordered["Date"] = pd.to_datetime(self.ordered["Date"], unit='s')
#        self.ordered = self.ordered.set_index('Date')
        self.data = pd.DataFrame()

    def __append(self, epochTime, price):
        if self.newRound['Date'] != 0 and epochTime >= self.newRound['Date'] + 60 * self.interval:
            if len(self.ordered) == 0 or self.ordered.at[len(self.ordered) - 1, 'Date'] != self.newRound['Date']:
                self.ordered = self.ordered.append(self.newRound, ignore_index=True)
            self.newRound = copy.deepcopy(self.roundTemp)
        self.newRound['Close'] = price
        if self.newRound['Date'] == 0:
            self.newRound['Date'] = epochTime - (epochTime % (self.interval * 60))
            self.newRound['Open'] = self.newRound['High'] = self.newRound['Low'] = price
        if self.newRound['Low'] > price:
            self.newRound['Low'] = price
        elif self.newRound['High'] < price:
            self.newRound['High'] = price

    def append(self, epochTime, price):
        self.__append(epochTime, price)
        self.update()

    def update(self):
        if self.ordered.at[len(self.ordered) - 1, 'Date'] != self.newRound['Date']:
            self.ordered = self.ordered.append(self.newRound, ignore_index=True)
        else:
            self.ordered.at[len(self.ordered) - 1, 'High'] = self.newRound['High']
            self.ordered.at[len(self.ordered) - 1, 'Low'] = self.newRound['Low']
            self.ordered.at[len(self.ordered) - 1, 'Close'] = self.newRound['Close']
            self.ordered.at[len(self.ordered) - 1, 'Open'] = self.newRound['Open']

data = pd.read_csv("data.csv", parse_dates=True)
#data["epoch"] = pd.to_datetime(data["epoch"], unit='s')
data = IntervalPeriodConverter(data, 15)
data.append(data.ordered.at[len(data.ordered) - 1, 'Date'] + 15 * 60, 2100)
data.ordered["Date"] = pd.to_datetime(data.ordered["Date"], unit='s')
data.ordered = data.ordered.set_index('Date')
print(data.ordered)
