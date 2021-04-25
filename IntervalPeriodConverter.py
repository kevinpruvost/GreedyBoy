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
from PerformanceTimer import time_function

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

##
## TODO: We must copy another DataFrame in order to give the program the capacity of Realtime price view.
##
data = IntervalPeriodConverter(data, 15)
time_function(pd.to_datetime, data.ordered["Date"], unit='s')
oof = copy.deepcopy(data.ordered)
oof["Date"] = pd.to_datetime(oof["Date"], unit='s')
oof = oof.set_index('Date')
print(data.ordered)
print(oof)

import csv
import matplotlib.pyplot as plt
import mplfinance
import pandas as pd
import matplotlib.dates as mpl_dates
import matplotlib.animation as animation
import time

idf = data.ordered
df = idf.loc['2021-04-24 00:00:00':'2021-04-24 12:00:00',:]

fig = mplfinance.figure(figsize=(11,5))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(3, 1, 3)

def animate(ival):
    if (20+ival) > len(df):
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return
    datas = df.iloc[0:(20+ival)]
    ax1.clear()
    mplfinance.plot(idf, ax=ax1, type='candle', style='charles')
    mplfinance.plot(datas, ax=ax2, type='candle', style='charles')

ani = animation.FuncAnimation(fig, animate, interval=250)

mplfinance.show()
