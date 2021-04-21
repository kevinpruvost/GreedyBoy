###
### Kraken Api class
###

import websocket
import _thread
import csv
import time, base64, hashlib, hmac, urllib.request, json

def getApiKeys():
        with open("config.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                return row['apiKey'], row['apiPrivateKey']

class KrakenApi:
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

    def ws_thread(*args):
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

    def __init__(self):
        self.apiKey, self.apiPrivateKey = getApiKeys()
        token = self.getToken()
        print(token)
        # Start a new thread for the WebSocket interface
        _thread.start_new_thread(self.ws_thread, ())