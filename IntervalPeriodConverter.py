#!/usr/bin/env python
"""
Description
-----------
Converts the data from the ``["Date", "Price"]`` to wanted interval period prices.

Watch for :ref:`the PriceData DataFrame<PriceData>` and :ref:`the BollingerData Dataframe<BollingerData>` for more details.
"""

__author__      = "Kevin Pruvost"
__copyright__   = "Copyright 2021, GreedyBoy"
__credits__     = ["Kevin Pruvost", "Hugo Mathieu-Steinbach"]
__license__     = "Proprietary"
__version__     = "1.0.0"
__maintainer__  = "Kevin Pruvost"
__email__       = "pruvostkevin0@gmail.com"
__status__      = "Test"

from GraphViewer import GraphViewer
import Libs.pandas.core.generic as gen
import copy
import Libs.pandas as pd
from PerformanceTimer import time_function

class IntervalPeriodConverter:
    @classmethod
    def fromFilename(cls, fileName: str, interval: int = 15, movingAverageSize: int = 20):
        csvData = pd.read_csv(fileName, parse_dates=True)
        return cls(csvData, interval, movingAverageSize)

    @classmethod
    def fromDataframe(cls, data: gen.NDFrame, interval: int = 15, movingAverageSize: int = 20):
        return cls(data, interval, movingAverageSize)

    def __init__(self, data: gen.NDFrame, interval: int = 15, movingAverageSize: int = 20):
        """Constructs IntervalPeriodConverter with the given data formatted like a csv [epochTime, price].
        :param interval: Interval in minutes.
        """
        self.data = data
        self.interval = interval
        self.movingAverageSize = movingAverageSize
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
        """Appends new (epochTime, price) into the Dataframes.
        :param epochTime: timestamp of the price
        :param price: price (float)
        """
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
        self.ordered['MA'] = self.ordered['Close'].rolling(window=self.movingAverageSize).mean()
        self.ordered['Std'] = self.ordered['Close'].rolling(window=self.movingAverageSize).std()
        self.ordered['HBand'] = self.ordered['MA'] + (self.ordered['Std'] * 2)
        self.ordered['LBand'] = self.ordered['MA'] - (self.ordered['Std'] * 2)
        self.bollingerGaps['Date'] = self.ordered['Date']
        self.bollingerGaps['Value'] = round(
            (self.ordered['Close'] - self.ordered['LBand']) / (self.ordered['HBand'] - self.ordered['LBand']) * 100
        , 2)
    def convertForGraphicViews(self):
        data1, data2 = copy.deepcopy(self.ordered), copy.deepcopy(self.bollingerGaps)
        data1, data2 = data1.iloc[self.movingAverageSize:], data2.iloc[self.movingAverageSize:]
        data1["Date"], data2["Date"] = pd.to_datetime(data1["Date"], unit='s'), pd.to_datetime(data2["Date"], unit='s')
        data1, data2 = data1.set_index('Date'), data2.set_index('Date')
        return data1, data2

def main():
    intervalPeriodConverter = IntervalPeriodConverter.fromFilename("data.csv", 15, 20)
    data1, data2 = intervalPeriodConverter.convertForGraphicViews()
    print(data1, data2)
    graphicView = GraphViewer(data1, data2)
    graphicView.start()

if __name__ == '__main__':
    time_function(main)