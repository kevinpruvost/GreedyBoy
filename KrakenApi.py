#!/usr/bin/env python
"""
Description
-----------

Makes every interactions between GreedyBoy and the Kraken API.
"""

import Libs.websocket as websocket
import Libs.urllib.request as req
import _thread
import tempfile
import time, base64, hashlib, hmac, json
from github import Github

currencyInitial = "XDG"
"""Contains currency code of the cryptocurrency to interact with."""

class KrakenApi:
    """Interacts with Kraken API.
    """

    def getToken(self):
        """Gets the token from Kraken.

        Check for :ref:`configuration <configuration>` to see how it works.
        """
        api_nonce = bytes(str(int(time.time() * 1000)), "utf-8")
        api_request = req.Request("https://api.kraken.com/0/private/GetWebSocketsToken",
                                             b"nonce=%s" % api_nonce)
        api_request.add_header("API-Key", self.apiKey)
        api_request.add_header("API-Sign", base64.b64encode(hmac.new(
            base64.b64decode(self.apiPrivateKey),
            b"/0/private/GetWebSocketsToken" + hashlib.sha256(api_nonce + b"nonce=%s" % api_nonce).digest(),
            hashlib.sha512).digest()))

        res = json.loads(req.urlopen(api_request).read())
        try:
            return res['result']['token']
        except:
            print("Didn't get that token.")
            return self.getToken()

    ##
    ## REQUESTS
    ##

    def __ws_thread(*args):
        def ws_message(ws, message):
            j = json.loads(message)
            if "event" not in j or j["event"] != "heartbeat":
                if isinstance(j, list) and j[-1] == "XDG/EUR":
                    for info in j[1]:
                        print("XDG/EUR [" + time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(float(info[2]))) + "]: " + info[0] + " euros.")
                else:
                    print("OUTPUT : %s" % message)

        def ws_open(ws):
            ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["XDG/EUR"]}')
        ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open=ws_open, on_message=ws_message)
        ws.run_forever()

    def __init__(self, apiKey, apiPrivateKey, githubToken, repoName, dataBranchName):
        """
        :param apiKey: Kraken API key
        :type apiKey: str
        :param apiPrivateKey: Kraken private API key
        :type apiPrivateKey: str
        :param githubToken: Github token
        :type githubToken: str
        :param repoName: Github repo name
        :type repoName: str
        :param dataBranchName: Github branch name
        :type dataBranchName: str
        """
        self.dataPaths = tempfile.gettempdir() + "/data" + currencyInitial + ".csv"
        self.githubDataFilename = time.strftime('%d-%m-%Y', time.localtime(time.time())) + ".csv"
        self.githubDataPaths = "./price_history/" + currencyInitial + "/" + self.githubDataFilename
        self.apiKey, self.apiPrivateKey = apiKey, apiPrivateKey
        self.githubToken, self.branchName = githubToken, dataBranchName

        # Kraken Token
        token = self.getToken()
        print(token)

        # Github repo
        g = Github(githubToken)
        self.greedyBoyRepo = g.get_repo(repoName)

        # Start a new thread for the WebSocket interface
        _thread.start_new_thread(self.__ws_thread, ())