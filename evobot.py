import configparser
from exchanges.poloniex.polo import Polo
from time import sleep
import time



timeout = 60

def main():
    # Parse config and get working exchange
    config = configparser.ConfigParser()
    config.read('config.ini')
    # TODO: check which exchange we will use
    api_key = config['Poloniex']['apiKey']
    secret = config['Poloniex']['secret']

    exchange = Polo(apiKey=api_key, secret=secret)

    # TODO 1) config: define ticker interval
    # TODO 2) store ticker to mongodb
    # TODO 3) add engine
    # TODO 4) add strategy
    # TODO 5) add backfill
    # TODO 6) add --paper, --trade, --sim

    # Loop
    while True:
        #tickers = exchange.returnTicker()

        '''
        # Get ticker data
        for ticker, values in tickers.items():
            print(ticker)
            print(values)
            print(values['last'])
        '''

        # Get candlestick data
        epoch_time = int(time.time())
        data = exchange.returnChartData('BTC_ETH', 300, 1, epoch_time)
        print(data)

        sleep(timeout)




if __name__ == "__main__":
    main()

