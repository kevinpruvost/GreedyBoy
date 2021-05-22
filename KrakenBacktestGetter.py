###
### Kraken Api class
###
import pandas
import websocket
import _thread
import csv
import time, base64, hashlib, hmac, urllib, json
import tempfile
from github import Github

currencyInitials = ["XDG", "ETH"]

class KrakenBacktestGetter:
    ##
    ## AUTHENTIFICATION
    ##

    def getToken(self):
        """Gets the token delivered from Kraken."""
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
        """Used by the _thread.start_new_thread function to run the code of ws_thread into another thread"""
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
                    test = pandas.read_csv(self.dataPaths[i], parse_dates=True)
                    print(test.info(memory_usage="deep"))
            except:
                empty = True
                self.dataFile = open(self.dataPaths[i], "w")
                self.dataFile.write("")
                self.dataFile.close()
            self.dataFiles[currencyInitials[i]] = open(self.dataPaths[i], "a")
            self.dataWriters[currencyInitials[i]] = csv.DictWriter(self.dataFiles[currencyInitials[i]], fieldnames=["epoch", "price"], lineterminator="\n")
            if empty:
                self.dataWriters[currencyInitials[i]].writeheader()

        def ws_message(ws, message):
            j = json.loads(message)
            #print(j)
            for initial in currencyInitials:
                initialEur = initial + "/EUR"
                if isinstance(j, list) and j[-1] == initialEur:
                    for info in j[1]:
                        self.dataWriters[initial].writerow({"epoch": str(info[2]), "price": str(info[0])})
                        print(initialEur + "[" + time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(float(info[2]))) + "]: " + info[0] + "€")

        def ws_open(ws):
            for initial in currencyInitials:
                ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["' + initial + '/EUR"]}')

        ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open=ws_open, on_message=ws_message)
        ws.run_forever()

    ##
    ## GITHUB PART
    ##

    def close(self):
        """Does everything needed on destruction, at the end of the execution.
        Like writing and sending backtesting data to Github.
        """
        timer = time.perf_counter()

        for i, initial in enumerate(currencyInitials):
            if not self.dataFiles[initial].closed:
                self.dataFiles[initial].close()
            self.dataFiles[initial] = open(self.dataPaths[i], "r")
            cnt = self.dataFiles[initial].read()
            self.dataFiles[initial].close()

            update = False
            try:
                dirContent = self.greedyBoyRepo.get_dir_contents("./price_history/" + initial, self.branchName)

                ## Checks if file already exists
                for file in dirContent:
                    if file.name == self.githubDataFilename:
                        update, fileSha = True, file.sha
                        break
            except: 0

            msg = self.githubDataFilename + " updated."
            if update:
                self.greedyBoyRepo.update_file(
                    path=self.githubDataPaths[i],
                    message=msg,
                    content=cnt,
                    branch=self.branchName,
                    sha=file.sha
                )
            else:
                self.greedyBoyRepo.create_file(
                    path=self.githubDataPaths[i],
                    message=msg,
                    content=cnt,
                    branch=self.branchName
                )

        print("Sending files took " + str(time.perf_counter() - timer) + " seconds.")


    ##
    ## INIT
    ##

    def __init__(self, apiKey, apiPrivateKey, githubToken, repoName, dataBranchName):
        self.dataPaths = [tempfile.gettempdir() + "/data" + initial + ".csv" for initial in currencyInitials]
        self.githubDataFilename = time.strftime('%d-%m-%Y', time.localtime(time.time())) + ".csv"
        self.githubDataPaths = ["./price_history/" + initial + "/" + self.githubDataFilename for initial in currencyInitials]

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