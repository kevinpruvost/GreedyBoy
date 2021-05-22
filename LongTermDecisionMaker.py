###
### GreedyBoyDecisionMaker class
###

import time
import tempfile
import pandas as pd
import requests
import csv

from pdoc import reset

from LongTermDataMachine import LongTermDataMachine
from KrakenApi import KrakenApi
from github import Github

class LongTermDecisionMaker:
    def __writeRowToTemp(self, row):
        self.orderFile = open(self.ordersDataTempPath, "a")
        self.orderWriter = csv.DictWriter(self.orderFile, fieldnames=['Date', 'Price', 'Amount', 'Order'], lineterminator="\n")
        self.orderWriter.writerow(row)
        self.orderFile.close()

    def __readLastOrders(self):
        try:
            empty = True
            self.orders = None
            self.orderWriter = None
            githubFile = self.greedyBoyRepo.get_contents(self.ordersGithubPath, self.branchName)
            githubFileContent = githubFile.decoded_content.decode('ascii')
            empty = not csv.Sniffer().has_header(githubFileContent)
            if not empty:
                self.orderFile = open(self.ordersDataTempPath, "w")
                self.orderFile.write(githubFileContent)
                self.orderFile.close()
                self.dataMachine = LongTermDataMachine.fromFilename(self.ordersDataTempPath, interval=15)
        except:
            self.orderFile = open(self.ordersDataTempPath, "w")
            self.orderFile.write("")
            self.orderFile.close()
        self.orderFile = open(self.ordersDataTempPath, "a")
        self.orderWriter = csv.DictWriter(self.orderFile, fieldnames=['Date', 'Price', 'Amount', 'Order'], lineterminator="\n")
        if empty:
            self.orderWriter.writeheader()
        else: # Read Last Order
            orders = pd.read_csv(self.ordersDataTempPath, parse_dates=False)
            if len(orders.index) != 0:
                self.lastOrder = {
                    'Date': orders.iloc[-1]['Date'], 'Price': orders.iloc[-1]['Price'],
                    'Amount': orders.iloc[-1]['Amount'], 'Order': orders.iloc[-1]['Order']}

    def __setBuyOrSellPosition(self):
        price = self.dataMachine.lastPrice()  # Gets Last price registered
        if price:
            self.buyOrSellPosition = "buy" if self.fiatBalance > self.cryptoBalance * price else "sell"
        else:
            self.buyOrSellPosition = "buy" if self.fiatBalance >= 10 else "sell"

    def start(self):
        self.__readLastOrders()
        self.dataMachine = LongTermDataMachine()

        ###################################
        # Getting data from the day before
        if not self.testTime:
            lastTime = time.time() - 86400 * 55 - 1
            resp = self.krakenApi.GetPrices(self.initial, 1440, lastTime)
            if resp: # If request actually got useful information
                for result in resp:
                    self.dataMachine.appendFormated(result[0], result[1], result[2], result[3], result[4])

        if self.dataMachine.ordered.size == 0:
            self.dataFiles = dict()
            try:
               self.dataFiles[self.initial] = None
               githubFile = self.greedyBoyRepo.get_contents(self.githubDataPath, self.branchName)
               githubFileContent = githubFile.decoded_content.decode('ascii')
               empty = not csv.Sniffer().has_header(githubFileContent)
               if not empty:
                   self.dataFile = open(self.dataPathWrite, "w")
                   self.dataFile.write(githubFileContent)
                   self.dataFile.close()
                   self.dataMachine = LongTermDataMachine.fromFilename(self.dataPathWrite)
            except: 0

        #################################
        # Trying to add data from today
        try:
            lastDate = self.dataMachine.ordered.iloc[-1]["Date"]
            #self.dataMachine = GBDataMachine.fromFilename(self.dataPathWrite if not empty else self.todayDataFilename)
            todayData = pd.read_csv(self.todayDataFilename, parse_dates=True)
            todayData = todayData.drop(todayData[todayData.epoch < lastDate].index)
            self.dataMachine.appendDataframe(todayData)
        except: 0

        print("Memory usage :", self.dataMachine.memoryUsage())
        self.getCryptoAndFiatBalance()
        print("Initial balance :")
        print("\t" + str(self.cryptoBalance) + " XDG")
        print("\t" + str(self.fiatBalance) + " euros")
        #print(self.dataMachine.ordered.to_csv(index=False))

    def AddOrderMax(self, buyOrSell: str):
        price = self.dataMachine.ordered.iloc[-1]["Close"]  # Gets Last price registered
        amount = self.fiatBalance / price if buyOrSell == "buy" else self.cryptoBalance
        self.AddOrder(buyOrSell, amount, price)

    def AddOrder(self, buyOrSell: str, amount, price = None):
        if not price:
            price = self.dataMachine.ordered.iloc[-1]["Close"] # Gets Last price registered

        if self.buySellLimit != 0:
            maxAmount = self.buySellLimit / price # Gets max amount to buy or sell
            amount = min(amount, maxAmount)

        if buyOrSell == "buy":
            amount = min(amount, self.fiatBalance / price * 0.99975)
        elif buyOrSell == "sell":
            amount = min(amount, self.cryptoBalance * 0.99975)

        self.krakenApi.AddOrder(buyOrSell, "market", amount, self.initial)
        self.__writeRowToTemp({'Date': self.lastData, 'Price': str(price), 'Amount': str(amount), 'Order': buyOrSell})
        self.lastOrder = {'Date': self.lastData, 'Price': price, 'Amount': amount, 'Order': buyOrSell}
        if self.testTime:
            if self.buyOrSellPosition == "buy":
                self.cryptoBalance += amount * (0.9975)
                self.fiatBalance -= amount * price
            elif self.buyOrSellPosition == "sell":
                self.cryptoBalance -= amount
                self.fiatBalance += amount * price * (0.9975)
            self.__setBuyOrSellPosition()
        else:
            self.getCryptoAndFiatBalance()
        self.highest = self.lowest = 50
        print("Balance :" + str(self.cryptoBalance) + self.initial + ", " + str(self.fiatBalance) + " euros")
        print("Added to reports : " + str(self.lastOrder))

    def addFormatedData(self, epoch, open, high, low, close):
        self.lastData = epoch
        self.dataMachine.appendFormated(epoch, open, high, low, close)
        self.dataMachine.update()
        self.makeDecision()

    def addData(self, epoch, price):
        self.lastData = epoch
        self.dataMachine.append(epoch, price, False)
#        if self.dataMachine.intervalClosed():
        self.makeDecision()
        #print(self.dataMachine.iloc[:5].to_csv(index=False))

    def getCryptoAndFiatBalance(self):
        self.cryptoBalance, self.fiatBalance = self.krakenApi.GetCryptoAndFiatBalance(self.initial, "EUR")
        self.__setBuyOrSellPosition()
        return self.cryptoBalance, self.fiatBalance

    def setBuySellLimit(self, fiatValue: float):
        self.buySellLimit = fiatValue

    def setCustomBalance(self, cryptoBalance: float, fiatBalance: float):
        self.cryptoBalance, self.fiatBalance = cryptoBalance, fiatBalance
        self.__setBuyOrSellPosition()

    ######################################################################
    ## Decisions Making
    def makeDecision(self):
        ########################################################################
        ## SMMA Strategy
        def smmaStrategy():
            last = self.dataMachine.ordered.iloc[-1]
            closePrice, smma5, smma40 = last['Close'], last['SMMA5'], last['SMMA40']
            #print(time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(self.dataMachine.ordered.iloc[-1]['Date'])) +
            #      " || Close: {0:6.5f}, SMMA5: {1:6.5f}, SMMA40: {2:6.5f}".format(closePrice, smma5, smma40))
            if self.buyOrSellPosition == "buy":
                if smma5 > smma40 and smma5 / smma40 >= 1.02:
                    print(time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(self.dataMachine.ordered.iloc[-1]['Date']))
                          + " || Close: {0:6.5f}, SMMA5: {1:6.5f}, SMMA40: {2:6.5f}".format(closePrice, smma5, smma40))
                    self.AddOrderMax("buy")
            elif self.buyOrSellPosition == "sell":
                if smma5 < smma40 and smma40 / smma5 >= 1.02:
                    print(time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(self.dataMachine.ordered.iloc[-1]['Date']))
                          + " || Close: {0:6.5f}, SMMA5: {1:6.5f}, SMMA40: {2:6.5f}".format(closePrice, smma5, smma40))
                    self.AddOrderMax("sell")

        return smmaStrategy()

    def __init__(self, apiKey, apiPrivateKey, githubToken, repoName, dataBranchName, initial, todayDataFilename,
                 ordersTempPath, ordersGithubPath, krakenToken = None, bollingerTolerance: float = 20, testTime: float = None):
        self.initial = initial
        self.dataPathWrite = tempfile.gettempdir() + "/data" + initial + "_old.csv"
        self.githubDataFilename = time.strftime('%d-%m-%Y', time.localtime(time.time() - 86400)) + ".csv"
        self.githubDataPath = "./price_history/" + initial + "/" + self.githubDataFilename

        self.ordersDataTempPath, self.ordersGithubPath = ordersTempPath, ordersGithubPath

        self.apiKey, self.apiPrivateKey = apiKey, apiPrivateKey
        self.branchName = dataBranchName

        self.todayDataFilename = todayDataFilename

        # For testing purposes
        self.testTime = testTime

        # Github repo
        g = Github(githubToken)
        self.greedyBoyRepo = g.get_repo(repoName)

        # Kraken API
        self.krakenApi = KrakenApi(apiKey, apiPrivateKey, krakenToken)

        # Decision making
        self.lastOrder, self.lastData = None, None
        self.buyOrSellPosition = None  # "buy" / "sell"
        self.cryptoBalance = self.fiatBalance = 0
            ## Bollinger Strat
        self.bollingerTolerance = bollingerTolerance
        self.lowest = self.highest = 50
        self.buySellLimit = 0 # 0 if no limit
            ## Scalping Start
        self.scalping = None

        self.start()