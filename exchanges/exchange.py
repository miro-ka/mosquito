import sys
import configparser
from .poloniex.polo import Polo
from core.bots.enums import TradeMode
from pymongo import MongoClient
import pandas as pd


class Exchange:
    """
    Main interface to all exchanges
    """

    exchange = None

    def __init__(self, args, config_file, trade_mode):
        self.exchange = self.load_exchange(config_file)
        self.trade_mode = trade_mode
        if self.trade_mode == TradeMode.backtest:
            config = configparser.ConfigParser()
            config.read(config_file)
            self.db = self.initialize_db(config)
            self.ticker = self.db.ticker

    def get_all_tickers(self):
        """
        Returns ticker for all pairs
        """
        return list(self.exchange.get_all_tickers())

    def get_symbol_ticker(self, symbol):
        """
        Returns ticker for given symbol
        """
        return self.exchange.get_symbol_ticker(symbol)

    @staticmethod
    def initialize_db(config):
        """
        DB Initialization
        """
        db = config['MongoDB']['db']
        port = int(config['MongoDB']['port'])
        url = config['MongoDB']['url']
        client = MongoClient(url, port)
        db = client[db]
        return db

    @staticmethod
    def load_exchange(config_file):
        """
        Loads exchange files
        """
        config = configparser.ConfigParser()
        config.read(config_file)
        exchange_name = config['Trade']['exchange']

        if exchange_name == 'polo':
            api_key = config['Poloniex']['apiKey']
            secret = config['Poloniex']['secret']
            return Polo(api_key=api_key, secret=secret)
        else:
            print('Trying to use not defined exchange!')
            return None

    def trade(self, actions, wallet, trade_mode):
        """
        Main class for setting up buy/sell orders
        """
        return self.exchange.trade(actions, wallet, trade_mode)

    def get_balances(self):
        """
        Returns all available account balances
        """
        return self.exchange.get_balances()

    def get_offline_ticker(self, epoch, pairs):
        """
        Returns offline data from DB
        """
        ticker = pd.DataFrame()
        for pair in pairs:
            db_doc = self.ticker.find_one({"$and": [{"date": {"$gte": epoch}},
                                          # {"pair": {"$in": pair}},
                                          {"pair": pair},
                                          {"exchange": 'polo'}]})

            if db_doc is None:
                print('not data for pair:', pair)
                continue

            dict_keys = list(db_doc.keys())
            df = pd.DataFrame([db_doc], columns=dict_keys)
            df_pair = df['pair'].str.split('_', 1, expand=True)
            df = pd.concat([df, df_pair], axis=1)
            df.rename(columns={0: 'curr_1', 1: 'curr_2'}, inplace=True)
            ticker = ticker.append(df, ignore_index=True)

        return ticker
