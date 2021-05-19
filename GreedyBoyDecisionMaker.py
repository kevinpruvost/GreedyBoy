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

        ##
        ## TODO: Corriger buy amount par rapport au frique disponible, pareil pour sell
        ##

        self.krakenApi.AddOrder(buyOrSell, "market", amount, self.initial)
        self.__writeRowToTemp({'Date': self.lastOrder, 'Price': str(price), 'Amount': str(amount), 'Order': buyOrSell})
        self.lastOrder = {'Date': self.lastOrder, 'Price': price, 'Amount': amount, 'Order': buyOrSell}
        if self.testTime:
            if self.buyOrSellPosition == "buy":
                self.cryptoBalance += amount * (1 - 0.002)
                self.fiatBalance -= amount * price * (1 - 0.002)
            elif self.buyOrSellPosition == "sell":
                self.cryptoBalance -= amount * (1 - 0.002)
                self.fiatBalance += amount * price * (1 - 0.002)
            self.buyOrSellPosition = "buy" if self.buyOrSellPosition == "sell" else "sell"
        else:
            self.getCryptoAndFiatBalance()
        self.highest = self.lowest = 50
        print("Balance :" + str(self.cryptoBalance) + self.initial + ", " + str(self.fiatBalance) + " euros")
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

        print("Memory usage :", self.dataMachine.memoryUsage())
        self.getCryptoAndFiatBalance()
        print("Initial balance :")
        print("\t" + str(self.cryptoBalance) + " XDG")
        print("\t" + str(self.fiatBalance) + " euros")
        #print(self.dataMachine.ordered.to_csv(index=False))

    def addData(self, epoch, price):
        self.lastOrder = epoch
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
        curBolVal = self.dataMachine.currentBollingerValue()

        if not self.buyOrSellPosition: return
        if curBolVal <= 100 - self.bollingerTolerance and curBolVal >= self.bollingerTolerance: return

        if curBolVal > self.highest: self.highest = curBolVal
        elif curBolVal < self.lowest: self.lowest = curBolVal

        if self.buyOrSellPosition == "buy":
            if self.lowest < 0 and \
                    curBolVal - self.lowest >= self.bollingerTolerance:
                print(time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(self.dataMachine.bollingerGaps.iloc[-1]['Date'])))
                print("Current bollinger value :", curBolVal)
                self.AddOrder("buy", 1500)
        elif self.buyOrSellPosition == "sell":
            if self.highest > 100 and \
                    self.highest - curBolVal >= self.bollingerTolerance:
                print(time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(self.dataMachine.bollingerGaps.iloc[-1]['Date'])))
                print("Current bollinger value :", curBolVal)
                self.AddOrder("sell", 1500)

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
        self.bollingerTolerance = bollingerTolerance
        self.lastOrder = None
        self.lowest = self.highest = 50
        self.cryptoBalance = self.fiatBalance = 0
        self.buyOrSellPosition = None # "buy" / "sell"
        self.buySellLimit = 0 # 0 if no limit

        self.start()