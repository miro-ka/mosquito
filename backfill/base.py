import logging
import configargparse
from logging.config import fileConfig
from abc import ABC, abstractmethod
from pymongo import MongoClient
from exchanges.exchange import Exchange


class Base(ABC):
    """
    Base class for data back-filling
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='mosquito.ini')
    arg_parser.add('--pairs', help='Pairs to backfill. For ex. [BTC_ETH, BTC_* (to get all BTC_* prefixed pairs]')
    arg_parser.add("--all", help='Backfill data for ALL currencies', action='store_true')
    arg_parser.add("--days", help="Number of days to backfill", required=True, type=int, default=1)
    arg_parser.add('-v', '--verbosity', help='Verbosity', action='store_true')
    logging.config.fileConfig('logging.ini')

    def __init__(self):
        super(Base, self).__init__()
        args = self.arg_parser.parse_known_args()[0]
        self.exchange = Exchange()
        self.exchange_name = self.exchange.get_exchange_name()
        self.db = self.initialize_db(args)

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
        return client[db]

    def get_backfill_pairs(self, backfill_all_pairs=False, pairs_list=None):
        """
        Returns list of exchange pairs that were ordered to backfill
        """
        all_pairs = self.exchange.get_pairs()
        if backfill_all_pairs:
            return all_pairs
        elif pairs_list is not None:
            tmp_pairs = [pairs_list]
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
            return pairs

    @abstractmethod
    def run(self):
        """
        Backfill/fetch data
        """
        pass
