#!/usr/bin/env python
"""
Description
-----------
The `GraphViewer` is a GUI which has the ability is to display in a simple way,
different data from GreedyBoy.

These informations will be displayed:

- Plot 1

    * Price over time (candlesticks)

    * Bot's actions (points)

    * Bollinger bands (lines)

- Plot 2

    * Bollinger bands width (lines and points)

    * Volatility (lines)

Video Demonstration
-------------------
.. raw:: html

    <div style="text-align: center; margin-bottom: 2em;">
    <iframe width="100%" height="500" src="https://www.youtube-nocookie.com/embed/GlOQnsVOa2o?rel=0" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
    </div>
"""

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
    """Draws in 2 plots, the bollinger bands, the bollinger gaps and the price chart of a given cryptocurrency.

    The data must be given in DataFrames (pandas) in this format:

    **Price Data**

    ===================  =======  =======  =======  =======  =========  ==========  ============  ============
    Date (as index)      Open     Close    High     Low      :ref:`MA`  :ref:`Std`  :ref:`LBand`  :ref:`LBand`
    ===================  =======  =======  =======  =======  =========  ==========  ============  ============
    2021-04-24 05:00:00  1917.24  1920.21  1932.10  1899.24  1901.26    20.547      1860.124      1948.472
    ...                  ...      ...      ...      ...      ...        ...         ...           ...
    ===================  =======  =======  =======  =======  =========  ==========  ============  ============

    **Bollinger Data**

    ===================  ========
    Date (as index)      Value
    ===================  ========
    2021-04-24 05:00:00  67.00
    ...                  ...
    ===================  ========
    """

    ani = None
    """"""

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