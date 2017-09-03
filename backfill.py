from pymongo import MongoClient, ASCENDING
from exchanges.poloniex.polo import Polo
from exchanges.bittrex.bittrexclient import BittrexClient
import configargparse
import time


def main(args):
    """
    Usage:
    1) Loads and stores data mongodb for specific currency and specific days (from now)
       backfill --currency[] --days[]
    2) Loads data for all currently supported currencies for specific days (from now)
       backfill --all --days[]
    """
    day_constant = 86400

    # Parse config
    db = args.db
    port = int(args.db_port)
    url = args.db_url
    exchange_name = args.exchange

    # Init DB
    client = MongoClient(url, port)
    db = client[db]
    ticker = db.ticker
    db.ticker.create_index([('id', ASCENDING)], unique=True)

    # Init exchange
    if exchange_name == 'polo':
        exchange = Polo()
    elif exchange_name == 'bittrex':
        exchange = BittrexClient()
    else:
        print('Invalid exchange name in config.ini file!')
        return

    # Get list of all currencies
    all_pairs = exchange.get_pairs()
    if args.all:
        pairs = all_pairs
    elif args.pairs is not None:
        tmp_pairs = [args.pairs]
        pairs = []
        # Handle * suffix pairs
        for pair in tmp_pairs:
            if '*' in pair:
                prefix = pair.replace('*', '')
                pairs_list = [p for p in all_pairs if prefix in p]
                pairs.extend(pairs_list)
                # remove duplicates
                pairs = list(set(pairs))
            else:
                pairs.append(pair)

    # Get the candlestick data
    epoch_now = int(time.time())

    for pair in pairs:
        for day in reversed(range(1, int(args.days)+1)):
            epoch_from = epoch_now - (day_constant*day)
            epoch_to = epoch_now if day == 1 else epoch_now - (day_constant * (day-1))
            print('Getting currency data: ' + pair + ', days left: ' + str(day), end='')
            candles = exchange.get_candles(pair, epoch_from, epoch_to, 300)  # by default 5 minutes candles (minimum)
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
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='mosquito.ini')
    arg_parser.add('--pairs', help='Pairs to backfill. For ex. [BTC_ETH, BTC_* (to get all BTC_* prefixed pairs]')
    arg_parser.add("--all", help='Backfill data for ALL currencies', action='store_true')
    arg_parser.add("--days", help="Number of days to backfill", required=True, type=int, default=1)
    arg_parser.add('--exchange', help='Exchange')
    arg_parser.add('--db_url', help='Mongo db url')
    arg_parser.add('--db_port', help='Mongo db port')
    arg_parser.add('--db', help='Mongo db')
    arg_parser.add('-v', '--verbosity', help='Verbosity', action='store_true')
    options = arg_parser.parse_known_args()[0]

    main(options)
