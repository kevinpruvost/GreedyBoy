###
### MAIN
###

import KrakenApi
from KrakenBacktestGetter import KrakenBacktestGetter
import csv, time

def getConfig():
    with open("config.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return row['apiKey'], row['apiPrivateKey'], row['githubToken'], row['repoName'], row['dataBranchName']

def main():
    apiKey, apiPrivateKey, githubToken, repoName, dataBranchName = getConfig()
    kBacktestGetter = KrakenBacktestGetter(apiKey, apiPrivateKey, githubToken, repoName, dataBranchName)
#    kApi = KrakenApi.KrakenApi(apiKey, apiPrivateKey)
    # Continue other (non WebSocket) tasks in the main thread
    while True:
        try:
            time.sleep(5)
            print("Main thread: %d" % time.time())
        except:
            kBacktestGetter.close()
            break

if __name__ == '__main__':
    main()