###
### GreedyBoyDecisionMaker class
###

import time
import tempfile
import pandas as pd
import requests
import csv

from pdoc import reset

from GBDataMachine import GBDataMachine
from KrakenApi import KrakenApi
from github import Github

class GreedyBoyDecisionMaker:
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
                self.dataMachine = GBDataMachine.fromFilename(self.ordersDataTempPath)
        except: 0
        self.orderFile = open(self.ordersDataTempPath, "a")
        self.orderWriter = csv.DictWriter(self.orderFile, fieldnames=['Date', 'Price', 'Amount', 'Order'], lineterminator="\n")
        if empty:
            self.orderWriter.writeheader()

    def AddOrder(self, buyOrSell: str, amount, price = None):
        if not price:
            price = self.dataMachine.ordered.iloc[-1]["Close"] # Gets Last price registered

        if self.buySellLimit != 0:
            maxAmount = self.buySellLimit / price # Gets max amount to buy or sell
            amount = min(amount, maxAmount)

        self.krakenApi.AddOrder(buyOrSell, "market", amount, self.initial)
        self.__writeRowToTemp({'Date': str(time.time()), 'Price': str(price), 'Amount': str(amount), 'Order': buyOrSell})
        self.lastOrder = {'Date': time.time(), 'Price': price, 'Amount': amount, 'Order': buyOrSell}
        print("Added to reports : " + str(self.lastOrder))

    def start(self):
        self.__readLastOrders()
        self.dataMachine = GBDataMachine()

        ###################################
        # Getting data from the day before
        if not self.testTime:
            lastTime = time.time() - 86401
            resp = self.krakenApi.GetPrices(self.initial, 15, lastTime)
            if resp: # If request actually got useful information
                for result in resp:
                    self.dataMachine.appendFormated(result[0], result[1], result[2], result[3], result[4])
                lastTime = resp[-1][0] - 1
            resp = self.krakenApi.GetPrices(self.initial, 1, lastTime)
            if resp:
                for result in resp:
                    self.dataMachine.append(result[0], result[1])
                    self.dataMachine.append(result[0], result[2])
                    self.dataMachine.append(result[0], result[3])
                    self.dataMachine.append(result[0], result[4])
                    self.dataMachine.append(result[0], result[5])

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
                   self.dataMachine = GBDataMachine.fromFilename(self.dataPathWrite)
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

        print(self.dataMachine.memoryUsage())
        #print(self.dataMachine.ordered.to_csv(index=False))

    def addData(self, epoch, price):
        self.dataMachine.append(epoch, price, False)
        self.makeDecision()
        #print(self.dataMachine.iloc[:5].to_csv(index=False))

    def getCryptoAndFiatBalance(self):
        self.cryptoBalance, self.fiatBalance = self.krakenApi.GetCryptoAndFiatBalance(self.initial, "EUR")
        self.buyOrSellPosition = "buy" if self.fiatBalance >= 1 else "sell"
        return self.cryptoBalance, self.fiatBalance

    def setBuySellLimit(self, fiatValue: float):
        self.buySellLimit = fiatValue

    ######################################################################
    ## Decisions Making
    def makeDecision(self):
        self.AddOrder("buy", 1500, 0.5)

    def __init__(self, apiKey, apiPrivateKey, githubToken, repoName, dataBranchName, initial, todayDataFilename,
                 ordersTempPath, ordersGithubPath, krakenToken = None, testTime: float = None):
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
        self.lastOrder = None
        self.lowest = self.highest = None
        self.cryptoBalance = self.fiatBalance = 0
        self.buyOrSellPosition = None # "buy" / "sell"
        self.buySellLimit = 0 # 0 if no limit

        self.start()