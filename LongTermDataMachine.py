#!/usr/bin/env python
##
## LongTermDataMachine.py
##

__author__      = "Kevin Pruvost"
__copyright__   = "Copyright 2021, GreedyBoy"
__credits__     = ["Kevin Pruvost"]
__license__     = "Proprietary"
__version__     = "1.0.0"
__maintainer__  = "Kevin Pruvost"
__email__       = "pruvostkevin0@gmail.com"
__status__      = "Test"

import math

import pandas.core.generic as gen
import copy
import pandas as pd
import numpy as np

class LongTermDataMachine:
    @classmethod
    def fromFilename(cls, fileName: str, interval: int = 15, movingAverageSize: int = 30):
        """Constructor starting from a filename.

        :param fileName: Name of the file containing the data.
        :type fileName: str
        :param interval: Time gap between each price (in min).
        :type interval: int
        :param movingAverageSize: Number of data taken into account to calculate a moving average.
        :type movingAverageSize: int
        """
        csvData = pd.read_csv(fileName, parse_dates=True)
        return cls(csvData, interval, movingAverageSize)

    @classmethod
    def fromDataframe(cls, data: gen.NDFrame, interval: int = 15, movingAverageSize: int = 30):
        """Constructor starting from a filename.

        :param data: Structure containing prices and dates.
        :type data: gen.NDFrame
        :param interval: Time gap between each price (in min).
        :type interval: int
        :param movingAverageSize: Number of data taken into account to calculate a moving average.
        :type movingAverageSize: int
        """
        return cls(data, interval, movingAverageSize)

    def __init__(self, data: gen.NDFrame = None, interval: int = 1440):
        """Constructs GBDataMachine with the given data formatted like a csv [epochTime, price].

        :param data: Structure containing prices and dates.
        :type data: gen.NDFrame
        :param interval: Time gap between each price (in min) (default is 1440, 1 day).
        :type interval: int
        :param movingAverageSize: Number of data taken into account to calculate a moving average.
        :type movingAverageSize: int
        """
        self.interval = interval
        self.intervalJustClosed = False
        self.roundTemp = {
            'Date': 0,
            'Open': 0,
            'High': 0,
            'Low': 0,
            'Close': 0,
            'SMMA5': None,
            'SMMA40': None
        }
        self.newRound = copy.deepcopy(self.roundTemp)
        if data is not None:
            if 'Low' not in data:
                self.ordered = pd.DataFrame()
                self.parseToInterval(data)
            else:
                self.ordered = data
        else:
            self.ordered = pd.DataFrame()
        return

    def parseToInterval(self, data):
        for i, row in data.iterrows():
            self.__append(row['epoch'], row['price'])
        self.update()

    def _append(self, epochTime: float, price: float):
        if self.newRound['Date'] != 0 and epochTime >= self.newRound['Date'] + 60 * self.interval:
            if len(self.ordered) == 0 or self.ordered.at[len(self.ordered) - 1, 'Date'] != self.newRound['Date']:
                self.ordered = self.ordered.append(self.newRound, ignore_index=True)
                self.intervalJustClosed = True
            self.newRound = copy.deepcopy(self.roundTemp)
        self.newRound['Close'] = price
        if self.newRound['Date'] == 0:
            self.newRound['Date'] = epochTime - (epochTime % (self.interval * 60))
            self.newRound['Open'] = self.newRound['High'] = self.newRound['Low'] = price
        if self.newRound['Low'] > price:
            self.newRound['Low'] = price
        elif self.newRound['High'] < price:
            self.newRound['High'] = price

    def appendFormated(self, date: float, open: float, high: float, low: float, close: float):
        self.ordered = self.ordered.append({
            'Date': date,
            'Open': float(open),
            'High': float(high),
            'Low': float(low),
            'Close': float(close),
            'SMMA5': None,
            'SMMA40': None
        }, ignore_index=True)

    def appendFilename(self, fileName):
        csvData = pd.read_csv(fileName, parse_dates=True)
        return self.appendDataframe(csvData)

    def appendDataframe(self, dataFrame: pd.DataFrame):
        for i, row in dataFrame.iterrows():
            self._append(row['epoch'], row['price'])
        self.update()

    def appendFormatedDataframe(self, dataFrame: pd.DataFrame):
        for i, row in dataFrame.iterrows():
            self.appendFormated(row['Date'], row['Open'], row['High'], row['Low'], row['Close'])
        self.update()

    def append(self, epochTime: float, price: float, shouldPrint: bool = False):
        """Appends new (epochTime, price) into the Dataframes.

        :param epochTime: timestamp of the price
        :type epochTime: float
        :param price: price
        :type price: float
        """
        epochTime = float(epochTime)
        price = float(price)
        self._append(epochTime, price)
        self.update(shouldPrint)

    def update(self, shouldPrint: bool = False):
        """Updates the GBDataMachine and computes bollinger bands, moving averages, ..."""
        if self.newRound['Date'] != 0:
            if len(self.ordered.index) == 0 or self.ordered.at[len(self.ordered) - 1, 'Date'] != self.newRound['Date']:
                self.ordered = self.ordered.append(self.newRound, ignore_index=True)
                self.intervalJustClosed = True
            else:
                self.ordered.at[len(self.ordered) - 1, 'High'] = self.newRound['High']
                self.ordered.at[len(self.ordered) - 1, 'Low'] = self.newRound['Low']
                self.ordered.at[len(self.ordered) - 1, 'Close'] = self.newRound['Close']
                self.ordered.at[len(self.ordered) - 1, 'Open'] = self.newRound['Open']

        def sum(i, wSize):
            s = 0
            for j in range(0, wSize): s += self.ordered.iloc[i - j]['Close']
            return s

        def smma(i, wSize):
            if i == wSize:
                return np.round(sum(i, wSize) / wSize, decimals=10)
            return np.round((self.ordered.iloc[i - 1]['SMMA' + str(wSize + 1)] * wSize + self.ordered.iloc[i]['Close']) / (wSize + 1), decimals=10)

        size = len(self.ordered.index)
        if size < 5: return
        newSm = smma(size - 1, 5 - 1)
        self.ordered.loc[self.ordered.index[-1], 'SMMA5'] = newSm

        if size < 40: return
        newSm = smma(size - 1, 40 - 1)
        self.ordered.loc[self.ordered.index[-1], 'SMMA40'] = newSm
        last = self.ordered.iloc[-1]

    def convertForGraphicViews(self):
        """Convert data and format it for :ref:`GraphViewer<GraphViewer>`.

        :returns: (DataFrame containing data for Plot 1, Same for Plot 2)
        :rtype: (pandas.DataFrame, pandas.DataFrame)
        """
        data1, data2 = copy.deepcopy(self.ordered), copy.deepcopy(self.bollingerGaps)
        data1, data2 = data1.iloc[self.movingAverageSize:], data2.iloc[self.movingAverageSize:]
        data1["Date"], data2["Date"] = pd.to_datetime(data1["Date"], unit='s'), pd.to_datetime(data2["Date"], unit='s')
        data1, data2 = data1.set_index('Date'), data2.set_index('Date')
        return data1, data2

    def memoryUsage(self):
        return self.ordered.memory_usage(deep=True).sum()

    def printPrices(self):
        print(self.ordered.to_csv(index=False))

    def currentBollingerValue(self):
        return self.bollingerGaps.iloc[[-1]].iloc[0]['Value']

    def lastPrice(self):
        return self.ordered.iloc[-1]["Close"] if len(self.ordered.index) != 0 else None

    def intervalClosed(self):
        ret = self.intervalJustClosed
        self.intervalJustClosed = False
        return ret

import KrakenApi

def main():
    dataMachine = LongTermDataMachine()
    api = KrakenApi.KrakenApi("jN1hIQ7abFkjmn/ffco27/E2PC7/OfLatbX87vG5wa6vDlZP0GQTsoDa",
                    "Stha4yXDkHon3dnBBW8+nl7G+YVZvWC88OlltVKh5FhKuYJ0Z5sTgO9qe6a7bZKXfrapKMLgkNbJYuffnzvgtw==",
                    "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")
    prices = api.GetPrices("XDG", 1440, 1546214400)
    for priceBar in prices:
        dataMachine.appendFormated(priceBar[0], priceBar[1], priceBar[2], priceBar[3], priceBar[4])
    dataMachine.update()
    print(dataMachine.ordered.tail(50))

if __name__ == '__main__':
    main()