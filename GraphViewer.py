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

import matplotlib.pyplot as plt
import mplfinance
import matplotlib.animation as animation
import mplcursors

class GraphViewer:
    ani = None
    def __init__(self, priceDatas, bollingerDatas, animateCallback = None, fullscreen: bool = True):
        """Constructs the GraphViewer
        :param priceDatas: Dataframe containing detailed informations about prices.
        :param bollingerDatas: Dataframe containing informations about bollinger gaps.
        :param animateCallback: Callback called on the animation loop.
        :param fullscreen: De/Activates fullscreen mode for Matplotlib.
        """
        s = mplfinance.make_mpf_style(base_mpf_style='mike', rc={'font.size': 12})
        fig = mplfinance.figure(figsize=(15, 7), style=s)    # Defining figure size
        ax1 = fig.add_subplot(2, 1, 1)              # Defining plot 1
        ax2 = fig.add_subplot(2, 1, 2)              # Defining plot 2

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

            ##
            ## Drawing Price Candle Chart + Bollinger Bands
            ##
            ax1.clear()     # Clear
            mplfinance.plot(idf, ax=ax1, type='candle', style='charles')    # Drawing Candle Chart
            chart1 = bollinger_bands.plot(ax=ax1, use_index=False)          # Drawing Bollinger Bands

            ##
            ## Drawing Bollinger Gaps
            ##
            ax2.cla()           # Clear
            df.plot(ax=ax2)     # Drawing data lines
            ax2.axhline(y=100, color="red", lw=1.5, linestyle="-")    # Drawing '100' line limit
            ax2.axhline(y=0, color="green", lw=1.5, linestyle="-")    # Drawing '0' line limit

            # Defining scatter points color considering their values
            # <= 0      : Green,
            # >= 100    : Red,
            # Otherwise : Blue
            colors = ['g' if val <= 0 else 'r' if val >= 100 else '#00000033' for val in df['Value']]
            chart2 = ax2.scatter(df.index, df['Value'], color=colors)

            # Activating cursor interactions
            cursors = list()
            cursors.append(mplcursors.cursor(chart1, hover=True))
            cursors.append(mplcursors.cursor(chart2, hover=True))
            for cursor in cursors:
                @cursor.connect("add")
                def _(sel):
                    print(sel.annotation.get_text())
                    sel.annotation.set_color('black')
                    sel.annotation.get_bbox_patch().set(color="white", alpha=1)
                    sel.annotation.arrow_patch.set(arrowstyle="fancy", color="white", alpha=1)

        self.ani = animation.FuncAnimation(fig, animate, interval=1000)  # Creating Animation
        ani = self.ani

        ##
        ## Customizing Matplotlib
        ##
        figManager = plt.get_current_fig_manager()
        if fullscreen: figManager.full_screen_toggle()
        plt.subplots_adjust(left=0.04, bottom=0.067, right=0.93, top=0.955)

    def start(self):
        plt.show()