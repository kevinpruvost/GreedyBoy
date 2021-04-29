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

import numpy as np
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
            'Close': 0,
            'MA': 0,
            'Std': 0,
            'LBand': 0,
            'HBand': 0
        }
        self.bGapRoundTemp = {
            'Date': 0,
            'Value': 0
        }
        self.newRound = copy.deepcopy(self.roundTemp)
        self.newGapRound = copy.deepcopy(self.bGapRoundTemp)
        self.bollingerGaps = pd.DataFrame()
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
        self.ordered['MA'] = self.ordered['Close'].rolling(window=20).mean()
        self.ordered['Std'] = self.ordered['Close'].rolling(window=20).std()
        self.ordered['HBand'] = self.ordered['MA'] + (self.ordered['Std'] * 2)
        self.ordered['LBand'] = self.ordered['MA'] - (self.ordered['Std'] * 2)
        self.bollingerGaps['Date'] = self.ordered['Date']
        self.bollingerGaps['Value'] = (self.ordered['Close'] - self.ordered['LBand']) / (self.ordered['HBand'] - self.ordered['LBand']) * 100

data = pd.read_csv("data.csv", parse_dates=True)
#data["epoch"] = pd.to_datetime(data["epoch"], unit='s')

##
## TODO: We must copy another DataFrame in order to give the program the capacity of Realtime price view.
##
data = IntervalPeriodConverter(data, 15)
time_function(pd.to_datetime, data.ordered["Date"], unit='s')
time_function(pd.to_datetime, data.bollingerGaps["Date"], unit='s')
oof = copy.deepcopy(data.ordered)
oof["Date"] = pd.to_datetime(oof["Date"], unit='s')
oof = oof.set_index('Date')

import csv
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import mplfinance
import pandas as pd
import matplotlib.dates as mpl_dates
import matplotlib.animation as animation
import time
import mplcursors
from matplotlib.colors import ListedColormap, BoundaryNorm

plt.style.use('dark_background')

idf = oof
idf = idf.iloc[20:]
df = copy.deepcopy(data.bollingerGaps)
df['Date'] = pd.to_datetime(df['Date'], unit='s')
df = df.set_index('Date')
df = df.iloc[20:]

fig = mplfinance.figure(figsize=(15,7))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(3, 1, 3)
print(idf)
print(df)



bollinger_bands = idf[['HBand', 'LBand']]

def animate(ival):
    if (20+ival) > len(df):
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return
    #datas = df.iloc[0:(20+ival)]
    ax1.clear()
    mplfinance.plot(idf, ax=ax1, type='candle', style='charles')
    slt = bollinger_bands.plot(ax=ax1, use_index=False)
    fm = plt.get_current_fig_manager()

    #ax1.fill_between(bollinger_bands.index, bollinger_bands['HBand'], bollinger_bands['LBand'], color='grey', alpha=0.5)

    ax2.cla()

    upper = 100
    lower = 0
    supper = np.ma.masked_where(df['Value'] < upper, df['Value'])
    slower = np.ma.masked_where(df['Value'] > lower, df['Value'])
    smiddle = np.ma.masked_where((df['Value'] < lower) | (df['Value'] > upper), df['Value'])

    slt2 = df.plot(ax=ax2)
    ax2.axhline(y=100, color="red", lw=1, linestyle=":")
    ax2.axhline(y=0, color="green", lw=1, linestyle=":")
    #ax2.plot(df.index, df.index, '-r')

    mplcursors.cursor(slt, hover=True)
    mplcursors.cursor(slt2, hover=True)

ani = animation.FuncAnimation(fig, animate, interval=1000)

plt.show()
