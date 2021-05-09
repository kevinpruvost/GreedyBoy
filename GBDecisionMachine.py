#!/usr/bin/env python
##
## GBDecisionMachine.py
##

__author__      = "Kevin Pruvost"
__copyright__   = "Copyright 2021, GreedyBoy"
__credits__     = ["Kevin Pruvost", "Hugo Mathieu-Steinbach"]
__license__     = "Proprietary"
__version__     = "1.0.0"
__maintainer__  = "Kevin Pruvost"
__email__       = "pruvostkevin0@gmail.com"
__status__      = "Test"

import pandas.core.generic as gen
import copy
import pandas as pd

class GBDecisionMachine:
    @classmethod
    def fromFilename(cls, fileName: str):
        """Constructor starting from a filename.

        :param fileName: Name of the file containing the data.
        :type fileName: str
        :param interval: Time gap between each price (in min).
        :type interval: int
        :param movingAverageSize: Number of data taken into account to calculate a moving average.
        :type movingAverageSize: int
        """
        csvData = pd.read_csv(fileName, parse_dates=True)
        return cls(csvData)

    @classmethod
    def fromDataframe(cls, data: gen.NDFrame):
        """Constructor starting from a filename.

        :param data: Structure containing prices and dates.
        :type data: gen.NDFrame
        :param interval: Time gap between each price (in min).
        :type interval: int
        :param movingAverageSize: Number of data taken into account to calculate a moving average.
        :type movingAverageSize: int
        """
        return cls(data)

    def __init__(self, data: gen.NDFrame):
        """Constructs GBDataMachine with the given data formatted like a csv [epochTime, price].

        :param data: Structure containing prices and dates.
        :type data: gen.NDFrame
        :param interval: Time gap between each price (in min).
        :type interval: int
        :param movingAverageSize: Number of data taken into account to calculate a moving average.
        :type movingAverageSize: int
        """
        self.roundTemp = {
            'Date': 0,
            'Price': 0,
            'Amount': 0,
            'Order': '\0',
        }
        self.newRound = copy.deepcopy(self.roundTemp)
        self.bollingerGaps = pd.DataFrame()
        self.ordered = data
        return

    def __append(self, epochTime: float, price: float, amount: float, order: str):
        self.newRound['Date', 'Price', 'Amount', 'Order'] = epochTime, price, amount, order
        self.ordered.append(self.newRound, ignore_index=True)

    def append(self, epochTime: float, price: float, amount: float, order: str):
        """Appends new (epochTime, price) into the Dataframes.

        :param epochTime: timestamp of the price
        :type epochTime: float
        :param price: price
        :type price: float
        """
        self.__append(epochTime, price, amount, order)

    def convertForGraphicViews(self):
        """Convert data and format it for :ref:`GraphViewer<GraphViewer>`.

        :returns: (DataFrame containing decision data)
        :rtype: (pandas.DataFrame)
        """
        data = copy.deepcopy(self.ordered)
        print(data)
        data["Date"] = pd.to_datetime(data["Date"], unit='s')
        data = data.set_index('Date')
        return data