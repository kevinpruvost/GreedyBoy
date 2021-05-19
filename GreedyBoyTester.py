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
    print("Beginning tests...")
    for i, testTime in enumerate(testTimes):
        if i == 0: continue
        if testTimes[i - 1] != testTime - 86400: continue
        print("Test " + time.strftime('%d/%m/%Y', time.gmtime(testTime)))
        continue
        start_date = testTime - 86400
        end_date = testTime
        mask = (overallData['epoch'] >= start_date) & (overallData['epoch'] <= end_date)
        dataToUse = overallData.loc[mask]
        print(overallData)
        return
        dataPath = tempfile.gettempdir() + "/data" + currencyInitial + ".csv"
        githubDataFilename = time.strftime('%d-%m-%Y', time.gmtime(testTime)) + ".csv"
        githubDataPath = "./price_history/" + currencyInitial + "/" + githubDataFilename

        try:
            dataWriter = None
            githubFile = greedyBoyRepo.get_contents(githubDataPath, dataBranchName)
            githubFileContent = githubFile.decoded_content.decode('ascii')
            empty = not csv.Sniffer().has_header(githubFileContent)
            if not empty:
                dataFile = open(dataPath, "w")
                dataFile.write(githubFileContent)
                dataFile.close()
        except:
            empty = True
            dataFile = open(dataPath, "w")
            dataFile.write("")
            dataFile.close()

        # Test decision maker
        gbDM = GreedyBoyDecisionMaker(
            apiKey, apiPrivateKey, githubToken, repoName,   # Api Key, Api Private Key, Github repo
            dataBranchName, currencyInitial, dataPath,      # Branch name, trading initial, temp path of today's data
            ordersDataPath, githubOrdersPath, krakenToken,  # temp path containing orders, kraken token
            testTime                                        # Test Time
        )

if __name__ == '__main__':
    main()