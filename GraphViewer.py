#!/usr/bin/env python
## GraphViewer.py
##
## Description:
## Graphical Interface which purpose is to show in a more comfortable way,
## how different datas from GreedyBoy are going. Like the price chart, or the bot's actions.
##
## We will certainly use some candles representation, and width based bands.
##

__author__      = "Kevin Pruvost"
__copyright__   = "Copyright 2021, GreedyBoy"
__credits__     = ["Kevin Pruvost", "Hugo Matthieu-Steinbach"]
__license__     = "Proprietary"
__version__     = "1.0.0"
__maintainer__  = "Kevin Pruvost"
__email__       = "pruvostkevin0@gmail.com"
__status__      = "Test"

## csv serves as a .csv parser
import csv
import matplotlib.pyplot as plt
import mplfinance
import pandas as pd
import matplotlib.dates as mpl_dates
import matplotlib.animation as animation
import time

class DataFilter:
    """Takes prices data in input and returns the useful parts like high/end candles, ..."""

    def __init__(self):
        return

    def addData(self, time, price):
        return

class GraphViewer:
    """Contains the graphical interface in which we will see the needed representation of our data."""

    def __init__(self, data):
        """
        Constructs the GraphViewer

        :param data: Contains an 2D array, each column contains [timestamp, open, high, low, close]
        """

    def figure(self):
        return self.fig

    def show(self):
        self.fig.show()

plt.style.use('ggplot')

idf = pd.read_csv('candlestick_python_data.csv', index_col=0, parse_dates=True)
df = idf.loc['2011-07-01':'2011-12-30',:]

fig = mplfinance.figure(figsize=(11,5))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(3, 1, 3)

print(idf.rolling(window=20, min_periods=1).mean())

def animate(ival):
    if (20+ival) > len(df):
        print('no more data to plot')
        ani.event_source.interval *= 3
        if ani.event_source.interval > 12000:
            exit()
        return
    data = df.iloc[0:(20+ival)]
    ax1.clear()
    mplfinance.plot(data, ax=ax1, type='candle', style='charles')
    mplfinance.plot(data, ax=ax2, type='candle', style='charles')

ani = animation.FuncAnimation(fig, animate, interval=250)

mplfinance.show()