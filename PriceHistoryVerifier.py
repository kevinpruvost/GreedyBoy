import pandas as pd
import time, base64, hashlib, hmac, urllib, json
import tempfile, os, csv, datetime

def verifyValidity(fileName, todayLimit, tomorrowLimit):
    dataFile = open(fileName, "r")
    cnt = dataFile.read()
    dataFile.close()
    empty = not csv.Sniffer().has_header(cnt)
    if empty: return False

    tab = pd.read_csv(fileName)
    if len(tab['epoch']) <= 100: return False
    midnight = tab['epoch'][0] - tab['epoch'][0] % 86400
    tomorrow = midnight + 86399
    if tab['epoch'][0] - midnight >= 600: return False
    if tomorrow - tab['epoch'].iloc[-1] >= 600: return False

    return True

def main():
    path = './price_history'

    today = datetime.datetime.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    todayLimit = datetime.datetime.fromtimestamp(today.timestamp())
    tomorrowLimit = today.replace(hour=23, minute=59, second=59)

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:
                filePath = r + "/" + file
                if not verifyValidity(filePath, todayLimit, tomorrowLimit):
                    print("Removing " + filePath)
                    os.remove(filePath)

if __name__ == '__main__':
    main()