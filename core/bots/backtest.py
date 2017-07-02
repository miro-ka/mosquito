from pymongo import MongoClient
import configparser
from .base import Base
import time
import sys
import pandas as pd
from strategies.enums import TradeState as ts
from termcolor import colored

DAY = 86400


class Backtest(Base):
    """
    Main class for Backtest trading
    """
    current_action = None
    ticker_df = None

    def __init__(self, args, config_file):
        super(Backtest, self).__init__(args, config_file)
        self.counter = 0
        self.config = self.initialize_config(config_file)
        self.db = self.initialize_db(self.config)
        self.ticker = self.db.ticker
        self.sim_start = self.config['Backtest']['from']
        self.sim_end = self.config['Backtest']['to']
        self.sim_days = int(self.config['Backtest']['days'])
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_days, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.pairs = self.config['Trade']['pairs'].replace(" ", "").split(',')
        self.exchange = self.config['Trade']['exchange']

    @staticmethod
    def get_sim_epoch_start(sim_days, sim_start):
        if sim_start:
            return sim_start
        elif sim_days:
            epoch_now = int(time.time())
            return epoch_now - (DAY*sim_days)

    @staticmethod
    def initialize_config(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

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

    def get_next(self, interval):
        """
        Returns next state
        """
        db_doc = self.ticker.find_one({"$and": [{"date": {"$gte": self.current_epoch}},
                                      {"pair": {"$in": self.pairs}},
                                      {"exchange": self.exchange}]})

        if db_doc is None:
            sys.exit()
        # print('getting db_data for epoch:', self.current_epoch)
        # print(db_doc['date'])
        self.current_epoch += interval*60
        dict_keys = list(db_doc.keys())
        df = pd.DataFrame([db_doc], columns=dict_keys)
        df_pair = df['pair'].str.split('_', 1, expand=True)
        df = pd.concat([df, df_pair], axis=1)
        df.rename(columns={0: 'curr_1', 1: 'curr_2'}, inplace=True)
        self.ticker_df = df
        return df

    def trade(self, actions, wallet, trades):
        """
        Simulate currency buy/sell
        :param actions:
        :return: updated wallet
        """
        for action in actions:
            (currency_symbol, asset_symbol) = tuple(action.pair.split('_'))
            currency = [item for item in wallet if item[0] == currency_symbol]
            asset = [item for item in wallet if item[0] == asset_symbol]

            if not currency or not asset:
                print('Error: provided incorrect currency pairs')
                return wallet

            ticker = self.ticker_df.loc[self.ticker_df['pair'] == action.pair]
            close_price = ticker['close'][0]

            # Buy
            # For now we are accepting only 1 AND ONLY 1 active order
            if action.action == ts.buy:
                if self.current_action in [ts.buy, ts.buying, ts.sold, ts.none, None]:
                    print(colored('buying ' + action.pair, 'red'))
                    asset[0] = (asset[0][0], asset[0][1] + (currency[0][1] / close_price))
                    currency[0] = (currency[0][0], 0.0)
                    # TODO: add buy_sell_all functionality
                    self.current_action = ts.bought
                    new_wallet = [currency[0] if currency[0][0] == e[0] else e for e in wallet]
                    new_wallet = [asset[0] if asset[0][0] == e[0] else e for e in new_wallet]
                    # Append trade
                    trades.loc[len(trades)] = [ticker['date'][0], action.pair, close_price, 'buy']
                    return new_wallet
                elif self.current_action in [ts.sell, ts.selling]:
                    print('cancelling sell order..')
                    self.current_action = ts.none
                    return wallet

            # Sell
            # For now we are accepting only 1 AND ONLY 1 active order
            if action.action == ts.sell:
                if self.current_action in [ts.sell, ts.selling, ts.bought, ts.none, None]:
                    print(colored('selling ' + action.pair, 'red'))
                    currency[0] = (currency[0][0], currency[0][1] + (asset[0][1] * close_price))
                    asset[0] = (asset[0][0], 0.0)
                    # TODO: add buy_sell_all functionality
                    self.current_action = ts.bought
                    new_wallet = [currency[0] if currency[0][0] == e[0] else e for e in wallet]
                    new_wallet = [asset[0] if asset[0][0] == e[0] else e for e in new_wallet]
                    # Append trade
                    trades.loc[len(trades)] = [ticker['date'][0], action.pair, close_price, 'sell']
                    return new_wallet
                elif self.current_action in [ts.buy, ts.buying]:
                    print('cancelling buy order..')
                    self.current_action = ts.none
                    return wallet
        # TODO add trade to list of trades
        return wallet

    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        # TODO: update wallets balance
        print('refreshing wallet')
        return wallet
