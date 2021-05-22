#!/usr/bin/env python
##
## KrakenApi.py
##
import pandas as pd
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

def get_kraken_token(apiKey, apiPrivateKey):
    """Gets the token from Kraken.

    Check for :ref:`configuration <configuration>` to see how it works.
    """
    api_nonce = bytes(str(int(time.time() * 1000)), "utf-8")
    api_request = req.Request("https://api.kraken.com/0/private/GetWebSocketsToken",
                                             b"nonce=%s" % api_nonce)
    api_request.add_header("API-Key", apiKey)
    api_request.add_header("API-Sign", base64.b64encode(hmac.new(
        base64.b64decode(apiPrivateKey),
        b"/0/private/GetWebSocketsToken" + hashlib.sha256(api_nonce + b"nonce=%s" % api_nonce).digest(),
        hashlib.sha512).digest()))

    res = json.loads(req.urlopen(api_request).read())
    try:
        return res['result']['token']
    except:
        print("Didn't get that token.")
        return get_kraken_token(apiKey, apiPrivateKey)

class KrakenApi:
    """Interacts with Kraken API.
    """

    def kraken_post_request(self, uri_path, data):
        headers = {}
        headers['API-Key'] = self.apiKey
        # get_kraken_signature() as defined in the 'Authentication' section
        headers['API-Sign'] = get_kraken_signature(uri_path, data, self.apiPrivateKey)
        req = requests.post((self.apiUrl + uri_path), headers=headers, data=data)
        return req

    def kraken_get_request(self, uri_path):
        headers = {}
        headers['API-Key'] = self.apiKey
        # get_kraken_signature() as defined in the 'Authentication' section
        req = requests.get((self.apiUrl + uri_path), headers=headers)
        return req

    def getToken(self):
        """Gets the token from Kraken.

        Check for :ref:`configuration <configuration>` to see how it works.
        """
        return get_kraken_token(self.apiKey, self.apiPrivateKey)

    def GetPricesFullname(self, cryptoFiat: str, interval: int, since: int):
        """GetPrices but with cryptoFiat parameter instead of crypto & fiat separated

        :param cryptoFiat: name of the pair
        :type cryptoFiat: str
        :param interval: interval (in min)
        :type interval: int
        :param since: epoch time in seconds
        :type since: int
        """
        fiat = "USD" if "USD" in cryptoFiat else "EUR"
        return self.GetPrices(cryptoFiat.replace(fiat, ''), interval, since, fiat)

    def GetPrices(self, crypto: str, interval: int, since: int, fiat: str = "EUR"):
        """Returns an array containing every price info, formatted like this :
        [time, open, high, low, close, vwap, volume, count]

        :param crypto: name of the crypto (XDG for instance)
        :type crypto: str
        :param fiat: name of the fiat exchange currency (EUR for instance)
        :type fiat: str
        :param interval: interval (in min)
        :type interval: int
        :param since: epoch time in seconds
        :type since: int
        """
        resp = self.kraken_get_request('/0/public/OHLC?pair={0}&interval={1}&since={2}'.format(crypto + fiat, interval, since - 1))
        respJson = resp.json()
        if len(respJson['error']) != 0: return None
        return respJson['result'][crypto + fiat]

    def CancelOrders(self):
        """Just cancels every orders"""
        resp = self.kraken_post_request('/0/private/CancelAll', {
            "nonce": str(int(1000 * time.time()))
        })
        return resp.json()

    def AddOrder(self, buyOrSell, orderType, amount, cryptocurrency = "XDG", currency = "EUR", test = True, price = 1):
        """
        :param buyOrSell: "buy" or "sell"
        :type buyOrSell: str
        :param orderType: can be one of these : "market", "limit", "stop-loss", "take-profit", "stop-loss-limit", "take-profit-limit", "settle-position"
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

        resp = self.kraken_post_request('/0/private/AddOrder', buildRequest)
        respJson = resp.json()
        return None if len(respJson['error']) != 0 else respJson

    def CheckAccount(self):
        """Checks the account balances"""
        resp = self.kraken_post_request('/0/private/Balance', {
            "nonce": str(int(1000 * time.time() + 5000))
        })
        respJson = resp.json()
        return respJson['result'] if len(respJson['error']) == 0 else None

    def GetCryptoAndFiatBalance(self, currencyInitial: str, fiatInitial: str = "EUR"):
        """Gets a specific currency & fiat balance

        :param currencyInitial: initials of the cryptocurrency
        :type currencyInitial: str
        :param fiatInitial: initials of the fiat currency
        :type fiatInitial:str
        """
        resp = self.CheckAccount()
        return float(resp["X" + currencyInitial]), float(resp["Z" + fiatInitial]) if resp else None

    def GetLastTrades(self):
        """Gets the last trades made on your account"""
        resp = self.kraken_post_request('/0/private/TradesHistory', {
            "nonce": str(int(1000 * time.time() + 5000))
        })
        respJson = resp.json()
        return respJson['result']['trades'] if len(respJson['error']) == 0 else None

    def GetPairs(self, finishesWith: str = None):
        """Gets a list containing every exchange pairs (XDGEUR or XBTUSD for instance)

        :param finishesWith: to specify if you only want EUR exchange pairs for instance (so you need to put "EUR")
        :type finishesWith: str
        """
        resp = self.kraken_post_request('/0/public/AssetPairs', {
            "nonce": str(int(1000 * time.time() + 5000))
        })
        respJson = resp.json()
        result = respJson['result'] if len(respJson['error']) == 0 else None
        if finishesWith is not None and result is not None:
            lst = []
            for name in result:
                if name.endswith(finishesWith): lst += [name]
            return lst
        return result

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
        #print(self.token)

if __name__ == '__main__':
    api = KrakenApi("jN1hIQ7abFkjmn/ffco27/E2PC7/OfLatbX87vG5wa6vDlZP0GQTsoDa",
                    "Stha4yXDkHon3dnBBW8+nl7G+YVZvWC88OlltVKh5FhKuYJ0Z5sTgO9qe6a7bZKXfrapKMLgkNbJYuffnzvgtw==",
                    "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")
    #print(api.GetPrices('XDG', 1, time.time() - 180))
    #print(api.CheckAccount())
    pairs = api.GetPairs("EUR")
    print(pairs)