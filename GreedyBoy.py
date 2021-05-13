###
### Kraken Api class
###
import os.path

import websocket
import _thread
import csv
import time, base64, hashlib, hmac, urllib, json
import tempfile
from github import Github
from GreedyBoyDecisionMaker import GreedyBoyDecisionMaker

currencyInitials = ["XDG", "ETH"]

class GreedyBoy:
    ##
    ## AUTHENTIFICATION
    ##

    def getToken(self):
        api_nonce = bytes(str(int(time.time() * 1000)), "utf-8")
        api_request = urllib.request.Request("https://api.kraken.com/0/private/GetWebSocketsToken",
                                             b"nonce=%s" % api_nonce)
        api_request.add_header("API-Key", self.apiKey)
        api_request.add_header("API-Sign", base64.b64encode(hmac.new(
            base64.b64decode(self.apiPrivateKey),
            b"/0/private/GetWebSocketsToken" + hashlib.sha256(api_nonce + b"nonce=%s" % api_nonce).digest(),
            hashlib.sha512).digest()))

        res = json.loads(urllib.request.urlopen(api_request).read())
        try:
            return res['result']['token']
        except:
            print("Didn't get that token.")
            return self.getToken()

    ##
    ## REQUESTS
    ##

    def ws_thread(self, *args):
        for arg in args:
            self.limitTime = arg if arg else self.limitTime
        # Kraken Token
        self.token = self.getToken()
        print(self.token)

        self.dataFiles = dict()
        self.dataWriters = dict()
        for i in range(len(currencyInitials)):
            try:
                self.dataFiles[currencyInitials[i]] = None
                self.dataWriters[currencyInitials[i]] = None
                githubFile = self.greedyBoyRepo.get_contents(self.githubDataPaths[i], self.branchName)
                githubFileContent = githubFile.decoded_content.decode('ascii')
                empty = not csv.Sniffer().has_header(githubFileContent)
                if not empty:
                    self.dataFile = open(self.dataPaths[i], "w")
                    self.dataFile.write(githubFileContent)
                    self.dataFile.close()
            except:
                empty = True
                self.dataFile = open(self.dataPaths[i], "w")
                self.dataFile.write("")
                self.dataFile.close()
            self.dataFiles[currencyInitials[i]] = open(self.dataPaths[i], "a")
            self.dataWriters[currencyInitials[i]] = csv.DictWriter(self.dataFiles[currencyInitials[i]], fieldnames=["epoch", "price"], lineterminator="\n")
            if empty:
                self.dataWriters[currencyInitials[i]].writeheader()
        # Decision Maker
        self.decisionMaker = GreedyBoyDecisionMaker(
            self.apiKey, self.apiPrivateKey, self.githubToken, self.repoName,     # Api Key, Api Private Key, Github repo
            self.branchName, currencyInitials[0], self.dataPaths[0],              # Branch name, trading initial, temp path of today's data
            self.ordersDataPath, self.githubOrdersPath, self.token                # temp path containing orders, kraken token
        )


        def ws_message(ws, message):
            if self.limitTime - time.perf_counter() <= 0: self.ws.close()
            j = json.loads(message)
            for initial in currencyInitials:
                initialEur = initial + "/EUR"
                if isinstance(j, list) and j[-1] == initialEur:
                    for info in j[1]:
                        print(initialEur + "[" + time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(float(info[2]))) + "]: " + info[0] + "€")
                        if initial == self.decisionMaker.initial:
                            self.decisionMaker.addData(float(info[2]), float(info[0]))
                        self.dataWriters[initial].writerow({"epoch": str(info[2]), "price": str(info[0])})

        def ws_open(ws):
            for initial in currencyInitials:
                ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["' + initial + '/EUR"]}')
            ws.send('{"event":"subscribe", "subscription":{"name":"ownTrades", "token": "' + base64.b64decode(self.apiPrivateKey) +'"}}')

        def ws_close(ws):
            print("Stopping !!!")

        self.ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open=ws_open, on_message=ws_message, on_close=ws_close)
        self.decisionMaker.krakenApi.AddOrder("buy", "market", 100)
        self.ws.run_forever()

    ##
    ## GITHUB PART
    ##

    def close(self):
        timer = time.perf_counter()

        def sendToGithub(dataFile, dataPath, githubPath: str):
            if not dataFile.closed:
                dataFile.close()
            dataFile = open(dataPath, "r")
            cnt = dataFile.read()
            dataFile.close()

            if len(cnt) == 0: return

            update = False
            try:
                dirContent = self.greedyBoyRepo.get_contents(os.path.dirname(githubPath), self.branchName)

                ## Checks if file already exists
                fName = os.path.basename(githubPath)
                for file in dirContent:
                    if file.name == fName:
                        update, fileSha = True, file.sha
                        break
            except:
                0

            print("Writing to " + githubPath)
            msg = githubPath + " updated."
            if update:
                self.greedyBoyRepo.update_file(
                    path=githubPath,
                    message=msg,
                    content=cnt,
                    branch=self.branchName,
                    sha=fileSha
                )
            else:
                self.greedyBoyRepo.create_file(
                    path=githubPath,
                    message=msg,
                    content=cnt,
                    branch=self.branchName
                )

        for i, initial in enumerate(currencyInitials):
            sendToGithub(self.dataFiles[initial], self.dataPaths[i], self.githubDataPaths[i])
        try:
            sendToGithub(self.dataFiles[currencyInitials[0]], self.ordersDataPath, self.githubOrdersPath)
        except: 0

        print("Sending files took " + str(time.perf_counter() - timer) + " seconds.")


    ##
    ## INIT
    ##

    def __init__(self, apiKey, apiPrivateKey, githubToken, repoName, dataBranchName, limitTime):
        self.dataPaths = [tempfile.gettempdir() + "/data" + initial + ".csv" for initial in currencyInitials]
        self.githubDataFilename = time.strftime('%d-%m-%Y', time.localtime(time.time())) + ".csv"
        self.githubDataPaths = ["./price_history/" + initial + "/" + self.githubDataFilename for initial in currencyInitials]

        self.apiKey, self.apiPrivateKey = apiKey, apiPrivateKey
        self.githubToken, self.branchName = githubToken, dataBranchName

        # For orders history
        self.ordersDataPath = tempfile.gettempdir() + "/reports" + currencyInitials[0] + ".csv"
        self.githubOrdersPath = "./reports/" + currencyInitials[0] + "-reports.csv"

        # Github repo
        g = Github(githubToken)
        self.repoName = repoName
        self.greedyBoyRepo = g.get_repo(repoName)

        # Start a new thread for the WebSocket interface
        thr = _thread.start_new_thread(self.ws_thread, (limitTime,))


import datetime
import ConfigManager

def main(event, context):
    timer = time.perf_counter() + 2 * 15 - 15
    apiKey, apiPrivateKey, githubToken, repoName, dataBranchName = ConfigManager.getConfig()
    greedyBoy = GreedyBoy(apiKey, apiPrivateKey, githubToken, repoName, dataBranchName, timer)

    today = datetime.datetime.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrowLimit = datetime.datetime.fromtimestamp(
        today.timestamp() + 86400 - 15
    )

    while True:
        try:
            print(time.strftime('Now: %H:%M:%S, ', time.localtime(time.time()))
                  + time.strftime('Limit : %d/%m/%Y %H:%M:%S, Time remaining: ', time.localtime(tomorrowLimit.timestamp()))
                  + str(timer - time.perf_counter()))
            if time.time() > tomorrowLimit.timestamp():
                print("Day finished !")
                break
            time.sleep(3)
            if time.perf_counter() > timer:
                break
        except:
            break
    greedyBoy.close()
    return {
        'statusCode': 200,
        'body': json.dumps("Hello coomers !")
    }

if __name__ == '__main__':
    main(1, 2)