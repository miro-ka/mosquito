from pymongo import MongoClient, ASCENDING
from exchanges.poloniex.polo import Polo
from core.bots.enums import TradeMode as tm
import configparser
import time
import argparse


client = MongoClient('localhost', 27017)
db = client.green1

DAY = 86400


def main(args):
    """
    Usage:

    # Loads and stores data mongodb for specific currency and specific days (from now)
    backfill --currency[] --days[]

    # Loads data for all currently supported currencies for specific days (from now)
    backfill --all --days[]
    """

    # Parse config and get working exchange
    config = configparser.ConfigParser()
    config.read('config.ini')
    # TODO: check which exchange we will use
    api_key = config['Poloniex']['apiKey']
    secret = config['Poloniex']['secret']
    # Mongo parameters
    db = config['MongoDB']['db']
    port = int(config['MongoDB']['port'])
    url = config['MongoDB']['url']

    # Init mongo
    # TODO: get mongo details from config
    client = MongoClient(url, port)
    db = client[db]
    ticker = db.ticker
    db.ticker.create_index([('id', ASCENDING)], unique=True)

    # Parse config and get working exchange
    config = configparser.ConfigParser()
    config.read('config.ini')
    # TODO: check which exchange we will use
    api_key = config['Poloniex']['apiKey']
    secret = config['Poloniex']['secret']
    exchange = Polo(tm.backtest, api_key=api_key, secret=secret)

    # Get list of all currencies
    if args.all:
        tickers = exchange.return_ticker()
        pairs = list(tickers.keys())
    elif args.pair is not None:
        pairs = [args.pair]

    # Get the candlestick data
    epoch_now = int(time.time())

    for pair in pairs:
        for day in reversed(range(1, args.days+1)):
            print('getting currency data: ' + pair +', days left:' + str(day))
            epoch_from = epoch_now - (DAY*day)
            epoch_to = epoch_now if day == 1 else epoch_now - (DAY * (day-1))
            candles = exchange.return_candles(pair, 300, epoch_from, epoch_to) # by default 5 minutes candles (minimum)

            for candle in candles:
                # Convert strings to number (float or int)
                for key, value in candle.items():
                    try:
                        candle[key] = int(value)
                    except ValueError:
                        candle[key] = float(value)
                # Add identifier
                candle['exchange'] = 'polo'
                candle['pair'] = pair
                id = 'polo' + '-' + pair + '-' +str(candle['date'])
                candle['id'] = id
                # Store to DB
                ticker.update_one({'id': id}, {'$set': candle}, upsert=True)

    print('import done..')


if __name__ == "__main__":
    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", help="Pair to backfill. For ex. [BTC_ETH]")
    parser.add_argument("--all", help="Backfill data for ALL currencies", action='store_true')
    parser.add_argument("--days", help="Number of days to backfill", required=True, type=int)
    args = parser.parse_args()

    main(args)