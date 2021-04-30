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

import numpy as np
import matplotlib.pyplot as plt
import mplfinance
import matplotlib.animation as animation
import mplcursors

class GraphViewer:
    def __init__(self, priceDatas, bollingerDatas, animateCallback = None, fullscreen: bool = True):
        fig = mplfinance.figure(figsize=(15, 7))
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        idf, df = priceDatas, bollingerDatas
        bollinger_bands = idf[['HBand', 'LBand']]

        def animate(ival):
            if animateCallback: animateCallback()
            if (20 + ival) > len(df):
                print('no more data to plot')
                ani.event_source.interval *= 3
                if ani.event_source.interval > 12000:
                    exit()
                return
            # datas = df.iloc[0:(20+ival)]
            ax1.clear()
            mplfinance.plot(idf, ax=ax1, type='candle', style='charles')
            slt = bollinger_bands.plot(ax=ax1, use_index=False)
            fm = plt.get_current_fig_manager()

            # ax1.fill_between(bollinger_bands.index, bollinger_bands['HBand'], bollinger_bands['LBand'], color='grey', alpha=0.5)

            ax2.cla()

            upper = 100
            lower = 0
            supper = np.ma.masked_where(df['Value'] < upper, df['Value'])
            slower = np.ma.masked_where(df['Value'] > lower, df['Value'])
            smiddle = np.ma.masked_where((df['Value'] < lower) | (df['Value'] > upper), df['Value'])

            df.plot(ax=ax2)
            ax2.axhline(y=100, color="red", lw=1, linestyle=":")
            ax2.axhline(y=0, color="green", lw=1, linestyle=":")
            colors = ['#00a822' if val <= 0 else 'r' if val >= 100 else '#00000033' for val in df['Value']]
            slt2 = ax2.scatter(df.index, df['Value'], color=colors)
            # ax2.plot(df.index, df.index, '-r')

            mplcursors.cursor(slt, hover=True)
            mplcursors.cursor(slt2, hover=True)

        ani = animation.FuncAnimation(fig, animate, interval=1000)

        figManager = plt.get_current_fig_manager()
        if fullscreen: figManager.full_screen_toggle()

        plt.subplots_adjust(left=0.04, bottom=0.067, right=0.93, top=0.955)
        self.start()

    def start(self):
        plt.show()