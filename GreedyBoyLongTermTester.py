###
### GreedyBoyDecisionTester class
###

from LongTermDecisionMaker import LongTermDecisionMaker
from ConfigManager import getConfig
from KrakenApi import get_kraken_token
from KrakenApi import KrakenApi
import tempfile, time, csv, os
from github import Github
import pandas as pd

# Testing with Dogecoin
currencyInitial = "XDG"

def getCryptoList(krakenApi) -> [str]:
    return krakenApi.GetPairs("EUR")

def main():
    apiKey, apiPrivateKey, githubToken, repoName, dataBranchName = getConfig()
    ordersDataPath = tempfile.gettempdir() + "/reports" + currencyInitial + ".csv"
    githubOrdersPath = "./reports/" + currencyInitial + "-reports.csv"
    krakenToken = get_kraken_token(apiKey, apiPrivateKey)
    krakenApi = KrakenApi(apiKey, apiPrivateKey, krakenToken)

    # Github repo
    g = Github(githubToken)
    repoName = repoName
    greedyBoyRepo = g.get_repo(repoName)

    # Loop
    pairs = getCryptoList(krakenApi)
    #pairs = ["XDGEUR"] # Only test XDG

    # Log test
    testLog = open(tempfile.gettempdir() + "/testResults.csv", "w")
    testLogWriter = csv.DictWriter(
        testLog,
        fieldnames=['Pair', 'Crypto', 'Fiat', 'OpeningPrice', 'ClosePrice', 'OpeningValue', 'CloseValue', 'OverallBenefit', 'BotBenefit', 'NoBotOverallBenefit'],
        lineterminator="\n"
    )
    testLogWriter.writeheader()

    # Test Configurations
    fixFiatBalance = 300
    cryptoBalance, fiatBalance = 0, 0 # 300 euros

    # Loading test files
    testDatas = dict()
    for i, pair in enumerate(pairs):
        print("Loading", pair, "...")

        dataPath = tempfile.gettempdir() + "/testData-" + str(pair) + ".csv"

        if os.path.exists(dataPath):
            try:
                testDatas[pair] = pd.read_csv(dataPath, parse_dates=False)
                continue
            except: 0

        try:
            prices = krakenApi.GetPricesFullname(pair, 1440, 1483142400) # since 2017 every 1 day
            frame = pd.DataFrame()
            for priceTab in prices:
                frame = frame.append({
                    'Date': priceTab[0],
                    'Open': priceTab[1],
                    'High': priceTab[2],
                    'Low': priceTab[3],
                    'Close': priceTab[4]
                }, ignore_index=True)
            dataFile = open(dataPath, "w")
            dataFile.write(frame.to_csv(index=False))
            dataFile.close()
            testDatas[pair] = frame
        except: 0

    print("Beginning tests...")
    for i, pair in enumerate(pairs):
        if not pair in testDatas: continue

        print("Test " + pairs[i] + ": ")
        dataPath = tempfile.gettempdir() + "/data" + pairs[i] + ".csv"
        githubDataFilename = pairs[i] + ".csv"
        githubDataPath = "./price_history/" + currencyInitial + "/" + githubDataFilename
        ordersDataPath = tempfile.gettempdir() + "/reports_test-" + pairs[i] + ".csv"

        # Test decision maker
        gbDM = LongTermDecisionMaker(
            apiKey, apiPrivateKey, githubToken, repoName,   # Api Key, Api Private Key, Github repo
            dataBranchName, currencyInitial, "dataPath",      # Branch name, trading initial, temp path of today's data
            ordersDataPath, githubOrdersPath, krakenToken,  # temp path containing orders, kraken token
            testTime=1                               # Test Time
        )
        # To get for comparisons
        row = testDatas[pair].iloc[0]
        gbDM.addFormatedData(row['Date'], row['Open'], row['High'], row['Low'], row['Close'])
        beginningPrice = gbDM.dataMachine.lastPrice()

        ## Defining balance
        cryptoBalance = fixFiatBalance / beginningPrice
        #fiatBalance = fixFiatBalance

        gbDM.setCustomBalance(cryptoBalance, fiatBalance)
        for x in range(1, len(testDatas[pair].index)):
            row = testDatas[pair].iloc[x]
            gbDM.addFormatedData(row['Date'], row['Open'], row['High'], row['Low'], row['Close'])

        # Log
        startingMoney = fiatBalance + cryptoBalance * beginningPrice

        # Benefits computed in percentage
        overallBenefit = (gbDM.fiatBalance + gbDM.cryptoBalance * gbDM.dataMachine.lastPrice()) / startingMoney
        botBenefit = (gbDM.fiatBalance + gbDM.cryptoBalance * gbDM.dataMachine.lastPrice()) / \
                     (fiatBalance + cryptoBalance * gbDM.dataMachine.lastPrice())

        overallBenefit = (overallBenefit - 1) * 100
        botBenefit = (botBenefit - 1) * 100

        row = {
            'Pair': pairs[i],
            'Crypto': gbDM.cryptoBalance,
            'Fiat': gbDM.fiatBalance,
            'OpeningPrice': beginningPrice,
            'ClosePrice': gbDM.dataMachine.lastPrice(),
            'OpeningValue': beginningPrice * cryptoBalance + fiatBalance,
            'CloseValue': gbDM.dataMachine.lastPrice() * gbDM.cryptoBalance + gbDM.fiatBalance,
            'OverallBenefit': overallBenefit,
            'BotBenefit': botBenefit,
            'NoBotOverallBenefit': ((fiatBalance + cryptoBalance * gbDM.dataMachine.lastPrice() / startingMoney) - 1) * 100
        }
        testLogWriter.writerow(row)
        print("Results of '" + pairs[i] + "': " + str(row))

    # Close log
    testLog.close()

if __name__ == '__main__':
    main()