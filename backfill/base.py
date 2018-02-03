import sys
import time
import logging
from logging.config import fileConfig
from abc import ABC, abstractmethod
import configargparse
from pymongo import MongoClient, ASCENDING
from exchanges.poloniex.polo import Polo
from exchanges.bittrex.bittrexclient import BittrexClient


class Base(ABC):
    """
    Base class for data back-filling
    """

    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='mosquito.ini')
    arg_parser.add('--pairs', help='Pairs to backfill. For ex. [BTC_ETH, BTC_* (to get all BTC_* prefixed pairs]')
    arg_parser.add("--all", help='Backfill data for ALL currencies', action='store_true')
    arg_parser.add("--days", help="Number of days to backfill", required=True, type=int, default=1)
    # arg_parser.add("--backfilltrades", help="Fetch /backfill and store trade history",  action='store_true')
    arg_parser.add('--exchange', help='Exchange')
    arg_parser.add('--db_url', help='Mongo db url')
    arg_parser.add('--db_port', help='Mongo db port')
    arg_parser.add('--db', help='Mongo db')
    arg_parser.add('-v', '--verbosity', help='Verbosity', action='store_true')
    logging.config.fileConfig('logging.ini')

    def __init__(self):
        super(Base, self).__init__()
        self.logger = logging.getLogger(__name__)
        args = self.arg_parser.parse_known_args()[0]
        self.exchange_name = args.exchange
        self.exchange = self.initialize_exchange(self.exchange_name)
        self.db_ticker = self.initialize_db(args)

    def initialize_exchange(self, exchange_name):
        """
        Exchange initialize
        """
        # Init exchange
        if exchange_name == 'polo':
            exchange = Polo()
        elif exchange_name == 'bittrex':
            exchange = BittrexClient()
        else:
            logger = logging.getLogger(__name__)
            logger.error('Invalid exchange name in config.ini file!')
            raise ValueError('Invalid exchange name in .ini file!')
        return exchange

    @staticmethod
    def initialize_db(args):
        """
        DB Initializer
        """
        db = args.db
        port = int(args.db_port)
        url = args.db_url
        # Init DB
        client = MongoClient(url, port)
        db = client[db]
        db_ticker = db.ticker
        db_ticker.create_index([('id', ASCENDING)], unique=True)
        return db_ticker

    @abstractmethod
    def run(self):
        """
        Backfill/fetch data
        """
        pass
