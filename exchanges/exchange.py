import configargparse
from .poloniex.polo import Polo
from .bittrex.bittrexclient import BittrexClient
from pymongo import MongoClient
from core.bots.enums import TradeMode
import pandas as pd
from termcolor import colored
import time


class Exchange:
    """
    Main interface to all exchanges
    """

    exchange = None
    exchange_name = None
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--exchange', help='Exchange')
    arg_parser.add('--db_url', help='Mongo db url')
    arg_parser.add('--db_port', help='Mongo db port')
    arg_parser.add('--db', help='Mongo db')
    arg_parser.add('--pairs', help='Pairs')

    def __init__(self, trade_mode=TradeMode.backtest):
        self.args = self.arg_parser.parse_known_args()[0]
        self.exchange = self.load_exchange()
        self.trade_mode = trade_mode
        self.verbosity = self.args.verbosity
        self.db = self.initialize_db()
        self.ticker = self.db.ticker

    def get_pair_delimiter(self):
        """
        Returns exchanges pair delimiter
        """
        return self.exchange.get_pair_delimiter()

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

    def initialize_db(self):
        """
        DB Initialization
        """
        db = self.args.db
        port = int(self.args.db_port)
        url = self.args.db_url
        client = MongoClient(url, port)
        db = client[db]
        return db

    def load_exchange(self):
        """
        Loads exchange files
        """
        self.exchange_name = self.args.exchange

        if self.exchange_name == 'polo':
            return Polo()
        elif self.exchange_name == 'bittrex':
            return BittrexClient()
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

    def get_candles_df(self, currency_pair, epoch_start, epoch_end, period=300):
        """
        Returns candlestick chart data in pandas dataframe
        """
        return self.exchange.get_candles_df(currency_pair, epoch_start, epoch_end, period)

    def get_candles(self, currency_pair, epoch_start, epoch_end, period=300):
        """
        Returns candlestick chart data
        """
        return self.exchange.get_candles(currency_pair, epoch_start, epoch_end, period)

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
        # print(' Getting offline ticker for total pairs: ' + str(len(pairs)) + ', epoch:', str(epoch))
        for pair in pairs:
            db_doc = self.ticker.find_one({"$and": [{"date": {"$lte": epoch}},
                                          {"pair": pair},
                                          {"exchange": self.exchange_name}]})

            if db_doc is None:
                if self.verbosity:
                    local_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
                    print(colored('No offline data for pair: ' + pair + ', epoch: ' + str(epoch) + ' (local: '
                                  + str(local_dt) + ')', 'yellow'))
                continue

            dict_keys = list(db_doc.keys())
            df = pd.DataFrame([db_doc], columns=dict_keys)
            df_pair = df['pair'].str.split('_', 1, expand=True)
            df = pd.concat([df, df_pair], axis=1)
            df.rename(columns={0: 'curr_1', 1: 'curr_2'}, inplace=True)
            ticker = ticker.append(df, ignore_index=True)

        return ticker
