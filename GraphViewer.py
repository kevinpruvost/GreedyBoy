#!/usr/bin/env python
##
## GraphViewer.py
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

from PerformanceTimer import time_function
from GraphViewerDataMachine import GraphViewerDataMachine
import ConfigManager
from GBDataMachine import GBDataMachine
from GBDecisionMachine import GBDecisionMachine

import matplotlib.pyplot as plt
import mplfinance
import matplotlib.animation as animation
import mplcursors
import pandas as pandas

currencyInitial = "XDG"
"""Contains currency code of the cryptocurrency to get the prices from."""

class GraphViewer:
    """
    :param priceData: Dataframe containing detailed informations about prices.
    :type priceData: DataFrame
    :param bollingerData: Dataframe containing informations about bollinger gaps.
    :type bollingerData: DataFrame
    :param animateCallback: Callback called on the animation loop.
    :type animateCallback: Function
    :param fullscreen: De/Activates fullscreen mode for Matplotlib.
    :type fullscreen: bool

    Draws in 2 plots, the **bollinger bands**, the **bollinger gaps** and the
    **price chart** of a given cryptocurrency.

    ``priceData`` and ``bollingerData`` must be 2 ``DataFrame`` (``pandas``) in these formats:

    .. _PriceData:

    **Price Data**

    +---------------------+----------------------------+----------------------------+------------------------------+----------------------------+-----------+------------+--------------+--------------+
    | Date (as index)     | :abbr:`Open (First price)` | :abbr:`Close (Last price)` | :abbr:`High (Highest price)` | :abbr:`Low (Lowest price)` | :ref:`MA` | :ref:`Std` | :ref:`LBand` | :ref:`HBand` |
    +=====================+============================+============================+==============================+============================+===========+============+==============+==============+
    | 2021-04-24 05:00:00 | 1917.24                    | 1920.21                    | 1932.10                      | 1899.24                    | 1901.26   | 20.547     | 1860.124     | 1948.472     |
    +---------------------+----------------------------+----------------------------+------------------------------+----------------------------+-----------+------------+--------------+--------------+
    | ...                 | ...                        | ...                        | ...                          | ...                        | ...       | ...        | ...          | ...          |
    +---------------------+----------------------------+----------------------------+------------------------------+----------------------------+-----------+------------+--------------+--------------+

    .. _BollingerData:

    **Bollinger Data**

    ===================  ========
    Date (as index)      Value
    ===================  ========
    2021-04-24 05:00:00  67.00
    ...                  ...
    ===================  ========
    """

    ani = None
    """Contains the animation callback."""

    def __init__(self, priceData: pandas.DataFrame, bollingerData: pandas.DataFrame, animateCallback = None, fullscreen: bool = True):
        self.setPricesData(priceData, bollingerData)
        self.draw = None

        s = mplfinance.make_mpf_style(base_mpf_style='mike', rc={'font.size': 12})
        fig = mplfinance.figure(figsize=(15, 7), style=s)    # Defining figure size
        ax1 = fig.add_subplot(2, 1, 1)              # Defining plot 1
        ax2 = fig.add_subplot(2, 1, 2)              # Defining plot 2

        def draw():
            ##
            ## Drawing Price Candle Chart + Bollinger Bands
            ##
            ax1.clear()  # Clear
            mplfinance.plot(self.priceData, ax=ax1, type='candle', style='charles')  # Drawing Candle Chart
            chart1 = self.bollinger_bands.plot(ax=ax1, use_index=False)  # Drawing Bollinger Bands
            #            self.reportData.plot(ax=ax1, use_index=False)

            ##
            ## Drawing Bollinger Gaps
            ##
            ax2.cla()  # Clear
            self.bollingerData.plot(ax=ax2)  # Drawing data lines
            ax2.axhline(y=100, color="red", lw=1.5, linestyle="-")  # Drawing '100' line limit
            ax2.axhline(y=0, color="green", lw=1.5, linestyle="-")  # Drawing '0' line limit

            # Defining scatter points color considering their values
            # <= 0      : Green,
            # >= 100    : Red,
            # Otherwise : Blue
            colors = ['g' if val <= 0 else 'r' if val >= 100 else '#00000033' for val in self.bollingerData['Value']]
            chart2 = ax2.scatter(self.bollingerData.index, self.bollingerData['Value'], color=colors)

            # Activating cursor interactions
            cursors = list()
            cursors.append(mplcursors.cursor(chart1, hover=True))
            cursors.append(mplcursors.cursor(chart2, hover=True))
            for cursor in cursors:
                @cursor.connect("add")
                def _(sel):
                    sel.annotation.set_color('black')
                    sel.annotation.get_bbox_patch().set(color="white", alpha=1)
                    sel.annotation.arrow_patch.set(arrowstyle="fancy", color="white", alpha=1)

        def animate(ival):
            if animateCallback: animateCallback()
            if (20 + ival) > len(self.bollingerData):
                print('no more data to plot')
                ani.event_source.interval *= 3
                if ani.event_source.interval > 12000:
                    exit()
                return
            # datas = df.iloc[0:(20+ival)]
            self.draw()

        self.draw = draw

        self.ani = animation.FuncAnimation(fig, animate, interval=10000)  # Creating Animation
        ani = self.ani

        ##
        ## Customizing Matplotlib
        ##
        figManager = plt.get_current_fig_manager()
        if fullscreen: figManager.full_screen_toggle()
        plt.subplots_adjust(left=0.04, bottom=0.067, right=0.93, top=0.955)

    def setPricesData(self, priceData: pandas.DataFrame, bollingerData: pandas.DataFrame):
        self.priceData, self.bollingerData = priceData, bollingerData
        self.bollinger_bands = self.priceData[['HBand', 'LBand']]

    def setReportData(self, reportData: pandas.DataFrame):
        self.reportData = reportData

    def start(self):
        """Starts the graph.

        .. important::

           It is a blocking function (like an app.exec() in Qt).
        """
        self.draw()
        plt.show()

def main():
    apiKey, apiPrivateKey, githubToken, repoName, dataBranchName = ConfigManager.getConfig()
    dataMachine = GraphViewerDataMachine(githubToken, repoName, dataBranchName, currencyInitial)
    priceData, reportData = dataMachine.getData()
    mergedData = pd.concat(priceData)

    dataMachine = GBDataMachine.fromDataframe(mergedData, 15, 30)
    if 'Date' in reportData: decisionMachine = GBDecisionMachine.fromDataframe(reportData)

    pricesData, bollinerData = dataMachine.convertForGraphicViews()
    if 'Date' in reportData: reportData = decisionMachine.convertForGraphicViews()

    graphicView = GraphViewer(pricesData, bollinerData)
    if 'Date' in reportData: graphicView.setReportData(reportData)
    graphicView.start()

if __name__ == '__main__':
    time_function(main)