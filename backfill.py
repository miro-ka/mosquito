from pymongo import MongoClient, ASCENDING
from exchanges.poloniex.polo import Polo
import configparser
import time
import argparse



'''
Usage:
 
# Loads and stores data mongodb for specific currency and specific days (from now) 
backfill --currency[] --days[]

# Loads data for all currently supported currencies for specific days (from now)
backfill --all --days[]
'''


client = MongoClient('localhost', 27017)
db = client.evobot1

DAY = 86400



def main(args):
    # Parse config and get working exchange
    config = configparser.ConfigParser()
    config.read('config.ini')
    # TODO: check which exchange we will use
    apiKey = config['Poloniex']['apiKey']
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
    apiKey = config['Poloniex']['apiKey']
    secret = config['Poloniex']['secret']
    exchange = Polo(apiKey=apiKey, secret=secret)

    # Get list of all currencies
    if args.all:
        tickers = exchange.returnTicker()
        pairs = list(tickers.keys())
    elif args.pair is not None:
        pairs = [args.pair]

    # Get the candlestick data
    epochNow = int(time.time())

    for pair in pairs:
        for day in reversed(range(1, args.days+1)):
            print('getting data for currency: ' + pair +', days left:' + str(day))
            epochFrom = epochNow - (DAY*day)
            epochTo = epochNow if day == 1 else epochNow - (DAY * (day-1))
            candles = exchange.returnChartData(pair, 300, epochFrom, epochTo) # by default 5 minutes candles (minimum)
            for candle in candles:
                candle['exchange'] = 'polo'
                candle['pair'] = pair
                id = 'polo' + '-' + pair + '-' +str(candle['date'])
                candle['id'] = id
                ##ticker.insertOne(candle)
                ticker.update_one({'id': id}, {'$set':candle}, upsert=True)


if __name__ == "__main__":
    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", help="Pair to backfill. For ex. [BTC_ETH]")
    parser.add_argument("--all", help="Backfill data for ALL currencies", action='store_true')
    parser.add_argument("--days", help="Number of days to backfill", required=True, type=int)
    args = parser.parse_args()

    main(args)