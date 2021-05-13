#!/usr/bin/env python
##
## KrakenApi.py
##

import websocket as websocket
import urllib.request as req
import urllib
import requests
import _thread
import tempfile
import time, base64, hashlib, hmac, json


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

class KrakenApi:
    """Interacts with Kraken API.
    """

    def kraken_request(self, uri_path, data):
        headers = {}
        headers['API-Key'] = self.apiKey
        # get_kraken_signature() as defined in the 'Authentication' section
        headers['API-Sign'] = get_kraken_signature(uri_path, data, self.apiPrivateKey)
        req = requests.post((self.apiUrl + uri_path), headers=headers, data=data)
        return req

    def __increaseNonce(self):
        self.nonce += 1

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

    def CancelOrders(self):
        resp = self.kraken_request('/0/private/CancelAll', {
            "nonce": str(int(1000 * time.time()))
        })
        return resp.json()

    def AddOrder(self, buyOrSell, orderType, amount, cryptocurrency = "XDG", currency = "EUR", test = True, price = 1):
        """
        :param buyOrSell: "buy" or "sell"
        :type buyOrSell: str
        :param orderType: can be one of these :
        "market": Sells as soon as possible at the first available offers
        "limit": Sells at a fixed price
        "stop-loss":
        "take-profit":
        "stop-loss-limit":
        "take-profit-limit":
        "settle-position":
        :type orderType: str
        """
        buildRequest = {
            "nonce": str(int(1000*time.time())),
            "ordertype": orderType,
            "type": buyOrSell,
            "volume": amount,
            "pair": cryptocurrency + currency,
            "validate": True # test # TO UNCOMMENT LATER
        }
        # If order is "market", then we can't send a price
        if orderType != "market": buildRequest['price'] = price

        resp = self.kraken_request('/0/private/AddOrder', buildRequest)
        return resp.json()

    def CheckAccount(self):
        resp = self.kraken_request('/0/private/Balance', {
            "nonce": str(int(1000 * time.time() + 5000))
        })
        return resp.json()

    def GetCryptoAndFiatBalance(self, currencyInitial, fiatInitial = "EUR"):
        resp = self.CheckAccount()
        try:
            return resp['result']["X" + currencyInitial], resp['result']["Z" + fiatInitial]
        except: return None

    def __init__(self, apiKey, apiPrivateKey, token = None):
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
        self.apiUrl = "https://api.kraken.com"
        self.apiKey, self.apiPrivateKey = apiKey, apiPrivateKey
        self.nonce = 0

        # Kraken Token
        self.token = token if token else self.getToken()
        print(self.token)

if __name__ == '__main__':
    api = KrakenApi("jN1hIQ7abFkjmn/ffco27/E2PC7/OfLatbX87vG5wa6vDlZP0GQTsoDa",
                    "Stha4yXDkHon3dnBBW8+nl7G+YVZvWC88OlltVKh5FhKuYJ0Z5sTgO9qe6a7bZKXfrapKMLgkNbJYuffnzvgtw==",
                    "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")
    print(api.AddOrder("sell", "market", 100, test=True))
    print(api.CancelOrders())
    print(api.GetCryptoAndFiatBalance("XDG"))