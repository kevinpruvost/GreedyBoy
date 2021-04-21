###
### Kraken Api class
###

import websocket
import _thread
import csv
import time, base64, hashlib, hmac, urllib.request, json
import tempfile
from github import Github

DATA_FILENAME = "data.csv"

class KrakenBacktestGetter:
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
        ##
        ## TODO: Make it retrieve data from Github, not temp
        ##
        try:
            self.dataFile = open(self.dataPath, "r")
            empty = not csv.Sniffer().has_header(self.dataFile.read(1024))
            self.dataFile.close()
        except:
            empty = True
        self.dataFile = open(self.dataPath, "a")
        self.dataWriter = csv.DictWriter(self.dataFile, fieldnames=["epoch", "price"], lineterminator="\n")
        if empty:
            self.dataWriter.writeheader()

        def ws_message(ws, message):
            j = json.loads(message)
            if isinstance(j, list) and j[-1] == "XDG/EUR":
                for info in j[1]:
                    self.dataWriter.writerow({"epoch": str(info[2]), "price": str(info[0])})
                    print("XDG/EUR [" + time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(float(info[2]))) + "]: " + info[0] + " euros.")

        def ws_open(ws):
            ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["XDG/EUR"]}')

        ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open=ws_open, on_message=ws_message)
        ws.run_forever()

    ##
    ## GITHUB PART
    ##

    def close(self):
        if not self.dataFile.closed:
            self.dataFile.close()
        self.dataFile = open(self.dataPath, "r")
        cnt = self.dataFile.read()

        fileName = time.strftime('%d-%m-%Y', time.localtime(time.time())) + ".csv"
        update = False
        try:
            dirContent = self.greedyBoyRepo.get_dir_contents("./price_history", self.branchName)

            ## Checks if file already exists
            for file in dirContent:
                if file.name == fileName:
                    update, fileSha = True, file.sha
                    break
        except: 0

        if update:
            self.greedyBoyRepo.update_file(
                path="./price_history/" + fileName,
                message="",
                content=cnt,
                branch=self.branchName,
                sha=file.sha
            )
        else:
            self.greedyBoyRepo.create_file(
                path="./price_history/" + fileName,
                message="",
                content=cnt,
                branch=self.branchName
            )

    ##
    ## INIT
    ##

    def __init__(self, apiKey, apiPrivateKey, githubToken, repoName, dataBranchName):
        self.dataPath = tempfile.gettempdir() + "\\" + DATA_FILENAME

        self.apiKey, self.apiPrivateKey = apiKey, apiPrivateKey
        self.githubToken, self.branchName = githubToken, dataBranchName

        # Kraken Token
        token = self.getToken()
        print(token)

        # Github repo
        g = Github(githubToken)
        self.greedyBoyRepo = g.get_repo(repoName)

        # Start a new thread for the WebSocket interface
        _thread.start_new_thread(self.ws_thread, ())