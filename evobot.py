import time
import argparse
import configparser
from time import sleep
from exchanges.poloniex.polo import Polo



timeout = 60

def main(args):
    print('testing')
    '''
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


        # Get ticker data
        for ticker, values in tickers.items():
            print(ticker)
            print(values)
            print(values['last'])

        # Get candlestick data
        epoch_time = int(time.time())
        data = exchange.returnChartData('BTC_ETH', 300, 1, epoch_time)
        print(data)

        sleep(timeout)
        '''




if __name__ == "__main__":

    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--sim", action='store_true')
    parser.add_argument("--paper", help="Simulate your strategy on real ticker", action='store_true')
    parser.add_argument("--trade", help="REAL trading mode", action='store_true')
    parser.add_argument("--strategy", help="Name of strategy to be run (if not set default one will be used")

    args = parser.parse_args()

    main(args)

