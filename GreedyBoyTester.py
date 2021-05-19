###
### GreedyBoyDecisionTester class
###
import datetime

from GreedyBoyDecisionMaker import GreedyBoyDecisionMaker
from ConfigManager import getConfig
from KrakenApi import get_kraken_token
import tempfile, time, csv, os
from github import Github
import pandas as pd

# Testing with Dogecoin
currencyInitial = "XDG"

def getTestTimeList(greedyBoyRepo, branchName) -> [float]:
    githubDataPath = "./price_history/" + currencyInitial + "/"

    tab = []
    try:
        dirContent = greedyBoyRepo.get_contents(os.path.dirname(githubDataPath), branchName)

        ## Checks if file already exists
        for file in dirContent:
            fileDate = os.path.splitext(os.path.basename(file.name))[0]
            fileDateTime = datetime.datetime.strptime(fileDate, "%d-%m-%Y")
            tab += [(fileDateTime - datetime.datetime(1970, 1, 1)).total_seconds()]
    except:
        0

    return tab

def main():
    apiKey, apiPrivateKey, githubToken, repoName, dataBranchName = getConfig()
    ordersDataPath = tempfile.gettempdir() + "/reports" + currencyInitial + ".csv"
    githubOrdersPath = "./reports/" + currencyInitial + "-reports.csv"
    krakenToken = get_kraken_token(apiKey, apiPrivateKey)

    # Github repo
    g = Github(githubToken)
    repoName = repoName
    greedyBoyRepo = g.get_repo(repoName)

    # Loop
    testTimes = getTestTimeList(greedyBoyRepo, dataBranchName)
    testTimes.sort()

    # Loading test files
    testDatas = []
    for i, testTime in enumerate(testTimes):
        if i + 1 == len(testTimes): continue

        print("Loading", time.strftime('%d/%m/%Y', time.gmtime(testTime)), "...")

        dataPath = tempfile.gettempdir() + "/data" + currencyInitial + str(testTime) + ".csv"
        githubDataFilename = time.strftime('%d-%m-%Y', time.gmtime(testTime)) + ".csv"
        githubDataPath = "./price_history/" + currencyInitial + "/" + githubDataFilename

        try:
            githubFile = greedyBoyRepo.get_contents(githubDataPath, dataBranchName)
            githubFileContent = githubFile.decoded_content.decode('ascii')
            empty = not csv.Sniffer().has_header(githubFileContent)
            if not empty:
                dataFile = open(dataPath, "w")
                dataFile.write(githubFileContent)
                dataFile.close()
                testDatas += [pd.read_csv(dataPath, parse_dates=False)]
        except: 0


    print("Beginning tests...")
    for i, testTime in enumerate(testTimes):
        if i == 0 or i + 1 == len(testTimes): continue
        if testTimes[i - 1] != testTime - 86400: continue
        print("Test " + time.strftime('%d/%m/%Y', time.gmtime(testTime)) + ": ")
        dataPath = tempfile.gettempdir() + "/data" + currencyInitial + str(testTime) + ".csv"
        githubDataFilename = time.strftime('%d-%m-%Y', time.gmtime(testTime)) + ".csv"
        githubDataPath = "./price_history/" + currencyInitial + "/" + githubDataFilename
        ordersDataPath = tempfile.gettempdir() + "/reports" + currencyInitial + time.strftime('%d-%m-%Y', time.gmtime(testTime)) + ".csv"

        # Test decision maker
        gbDM = GreedyBoyDecisionMaker(
            apiKey, apiPrivateKey, githubToken, repoName,   # Api Key, Api Private Key, Github repo
            dataBranchName, currencyInitial, "dataPath",      # Branch name, trading initial, temp path of today's data
            ordersDataPath, githubOrdersPath, krakenToken,  # temp path containing orders, kraken token
            testTime=testTime                               # Test Time
        )
        gbDM.dataMachine.appendDataframe(testDatas[i - 1])
        for i, row in testDatas[i].iterrows():
            gbDM.addData(row['epoch'], row['price'])

if __name__ == '__main__':
    main()