import configparser
from .poloniex.polo import Polo
from .bittrex.bittrexclient import BittrexClient
from pymongo import MongoClient
import pandas as pd
from termcolor import colored


class Exchange:
    """
    Main interface to all exchanges
    """

    exchange = None
    exchange_name = None

    def __init__(self, args, config_file, trade_mode):
        self.exchange = self.load_exchange(config_file)
        self.args = args
        self.trade_mode = trade_mode
        # if self.trade_mode == TradeMode.backtest:
        config = configparser.ConfigParser()
        config.read(config_file)
        self.db = self.initialize_db(config)
        self.ticker = self.db.ticker

    def get_transaction_fee(self):
        """
        Returns exchanges transaction fee
        """
        return self.exchange.get_transaction_fee()

    def get_pairs(self):
        """
        Returns ticker for all pairs
        """
        return self.exchange.get_pairs()

    def get_symbol_ticker(self, symbol, candle_size=5):
        """
        Returns ticker for given symbol
        """
        return self.exchange.get_symbol_ticker(symbol, candle_size)

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

    def load_exchange(self, config_file):
        """
        Loads exchange files
        """
        config = configparser.ConfigParser()
        config.read(config_file)
        verbosity = int(config['General']['verbosity'])
        self.exchange_name = config['Trade']['exchange']

        if self.exchange_name == 'polo':
            return Polo(config['Poloniex'], verbosity)
        elif self.exchange_name == 'bittrex':
            return BittrexClient(config['Bittrex'], verbosity)
        else:
            print('Trying to use not defined exchange!')
            return None

    def trade(self, actions, wallet, trade_mode):
        """
        Main class for setting up buy/sell orders
        """
        return self.exchange.trade(actions, wallet, trade_mode)

    def cancel_order(self, order_number):
        """
        Cancels order for given order number
        """
        return self.exchange.cancel_order(order_number)

    def get_balances(self):
        """
        Returns all available account balances
        """
        return self.exchange.get_balances()

    def return_open_orders(self, currency_pair='all'):
        """
        Returns your open orders
        """
        return self.exchange.return_open_orders(currency_pair)

    def get_offline_ticker(self, epoch, pairs):
        """
        Returns offline data from DB
        """
        ticker = pd.DataFrame()
        # print('getting offline ticker for total pairs: ' + str(len(pairs)) + ', epoch:', str(epoch))
        for pair in pairs:
            db_doc = self.ticker.find_one({"$and": [{"date": {"$gte": epoch}},
                                          {"pair": pair},
                                          {"exchange": self.exchange_name}]})

            if db_doc is None:
                print(colored('No offline data for pair: ' + pair + ', epoch:' + str(epoch), 'red'))
                continue

            dict_keys = list(db_doc.keys())
            df = pd.DataFrame([db_doc], columns=dict_keys)
            df_pair = df['pair'].str.split('_', 1, expand=True)
            df = pd.concat([df, df_pair], axis=1)
            df.rename(columns={0: 'curr_1', 1: 'curr_2'}, inplace=True)
            ticker = ticker.append(df, ignore_index=True)

        return ticker
