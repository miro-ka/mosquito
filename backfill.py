from pymongo import MongoClient, ASCENDING
from exchanges.poloniex.polo import Polo
from exchanges.bittrex.bittrexclient import BittrexClient
import configparser
import time
import argparse


def main(args):
    """
    Usage:
    1) Loads and stores data mongodb for specific currency and specific days (from now)
       backfill --currency[] --days[]
    2) Loads data for all currently supported currencies for specific days (from now)
       backfill --all --days[]
    """

    client = MongoClient('localhost', 27017)
    db = client.mosquito
    day_constant = 86400

    # Parse config
    config = configparser.ConfigParser()
    config.read('config.ini')
    db = config['MongoDB']['db']
    port = int(config['MongoDB']['port'])
    url = config['MongoDB']['url']
    exchange_name = config['Trade']['exchange']

    # Init DB
    client = MongoClient(url, port)
    db = client[db]
    ticker = db.ticker
    db.ticker.create_index([('id', ASCENDING)], unique=True)

    # Init exchange
    if exchange_name == 'polo':
        exchange = Polo(config['Poloniex'])
    elif exchange_name == 'bittrex':
        exchange = BittrexClient(config['Bittrex'])
    else:
        print('Invalid exchange name in config.ini file!')
        return

    # Get list of all currencies
    if args.all:
        pairs = exchange.get_pairs()
    elif args.pair is not None:
        pairs = [args.pair]

    # Get the candlestick data
    epoch_now = int(time.time())

    for pair in pairs:
        for day in reversed(range(1, args.days+1)):
            epoch_from = epoch_now - (day_constant*day)
            epoch_to = epoch_now if day == 1 else epoch_now - (day_constant * (day-1))
            print('Getting currency data: ' + pair + ', days left: ' + str(day), end='')
            candles = exchange.return_candles(pair, epoch_from, epoch_to, 300)  # by default 5 minutes candles (minimum)
            print(' (got total candles: ' + str(len(candles)) + ')')
            for candle in candles:
                # Convert strings to number (float or int)
                for key, value in candle.items():
                    is_already_number = isinstance(value, (int, float, complex))
                    if not is_already_number:
                        try:
                            candle[key] = int(value)
                        except ValueError:
                            candle[key] = float(value)
                new_db_item = candle.copy()
                # Add identifier
                new_db_item['exchange'] = exchange_name
                new_db_item['pair'] = pair
                unique_id = exchange_name + '-' + pair + '-' + str(candle['date'])
                new_db_item['id'] = unique_id
                # Store to DB
                ticker.update_one({'id': unique_id}, {'$set': new_db_item}, upsert=True)

    # print('Backfill data import done..')


if __name__ == "__main__":
    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", help="Pair to backfill. For ex. [BTC_ETH]")
    parser.add_argument("--all", help="Backfill data for ALL currencies", action='store_true')
    parser.add_argument("--days", help="Number of days to backfill", required=True, type=int)
    in_args = parser.parse_args()

    main(in_args)
