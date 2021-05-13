###
### GreedyBoyDecisionMaker class
###

import time
import tempfile
import pandas as pd
import requests
import csv
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

    def AddOrder(self, buyOrSell: str, amount, price):
        self.krakenApi.AddOrder(buyOrSell, "market", amount, self.initial)
        self.__writeRowToTemp({'Date': str(time.time()), 'Price': str(price), 'Amount': str(amount), 'Order': buyOrSell})
        self.lastOrder = {'Date': time.time(), 'Price': price, 'Amount': amount, 'Order': buyOrSell}
        print("Added to reports : " + self.lastOrder)

    def start(self):
        self.__readLastOrders()
        self.dataMachine = GBDataMachine()

        ###################################
        # Getting data from the day before
        resp = requests.get('https://api.kraken.com/0/public/OHLC?pair=' + self.initial + 'EUR&interval=15&since=' + str(time.time() - 86400))
        if len(resp.json()["error"]) == 0: # If request actually got useful information
            results = resp.json()["result"][self.initial + "EUR"]
            for result in results:
                self.dataMachine.appendFormated(result[0], result[1], result[2], result[3], result[4])
        else:
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
        self.dataMachine.append(epoch, price)
        self.makeDecision()
        #print(self.dataMachine.iloc[:5].to_csv(index=False))

    ######################################################################
    ## Decisions Making
    def makeDecision(self):
        self.AddOrder("buy", 1500, 0.5)

    def __init__(self, apiKey, apiPrivateKey, githubToken, repoName, dataBranchName, initial, todayDataFilename,
                 ordersTempPath, ordersGithubPath, krakenToken = None):
        self.initial = initial
        self.dataPathWrite = tempfile.gettempdir() + "/data" + initial + "_old.csv"
        self.githubDataFilename = time.strftime('%d-%m-%Y', time.localtime(time.time() - 86400)) + ".csv"
        self.githubDataPath = "./price_history/" + initial + "/" + self.githubDataFilename

        self.ordersDataTempPath, self.ordersGithubPath = ordersTempPath, ordersGithubPath

        self.apiKey, self.apiPrivateKey = apiKey, apiPrivateKey
        self.branchName = dataBranchName

        self.todayDataFilename = todayDataFilename

        # Github repo
        g = Github(githubToken)
        self.greedyBoyRepo = g.get_repo(repoName)

        # Kraken API
        self.krakenApi = KrakenApi(apiKey, apiPrivateKey, krakenToken)

        # Decision making
        self.lastOrder = None
        self.lowest = self.highest = None

        self.start()