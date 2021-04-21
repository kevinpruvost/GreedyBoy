###
### MAIN
###

import KrakenApi, KrakenBacktestGetter
import time

def main():
    kBacktestGetter = KrakenBacktestGetter.KrakenBacktestGetter()
#    kApi = KrakenApi.KrakenApi()
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