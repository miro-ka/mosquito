from pymongo import MongoClient
import configparser
from .base import Base
import time
import sys
import pandas as pd
from strategies.enums import TradeState as ts
from core.bots.enums import TradeMode
from termcolor import colored
from exchanges.exchange import Exchange


DAY = 86400


class Backtest(Base):
    """
    Main class for Backtest trading
    """
    previous_action = None
    ticker_df = None
    exchange = None
    mode = TradeMode.backtest

    def __init__(self, args, config_file):
        super(Backtest, self).__init__(args, config_file)
        self.counter = 0
        self.config = self.initialize_config(config_file)
        self.sim_start = self.config['Backtest']['from']
        self.sim_end = self.config['Backtest']['to']
        self.sim_days = int(self.config['Backtest']['days'])
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_days, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.exchange = Exchange(args, config_file, TradeMode.backtest)
        self.pairs = self.process_input_pairs(self.config['Trade']['pairs'])

    def get_pairs(self):
        return self.pairs

    def process_input_pairs(self, in_pairs):
        if in_pairs == 'all':
            print('setting_all_pairs')
            return self.exchange.get_all_pairs()
            # Get all pairs from API
        else:
            return in_pairs.replace(" ", "").split(',')

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

    def get_next(self, interval):
        """
        Returns next state of current_time + interval (in minutes)
        """
        self.ticker_df = self.exchange.get_ticker(self.current_epoch, self.pairs)
        self.current_epoch += interval*60
        return self.ticker_df

    def trade(self, actions, wallet, trades):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        for action in actions:
            (currency_symbol, asset_symbol) = tuple(action.pair.split('_'))
            currency = [item for item in wallet if item[0] == currency_symbol]
            asset = [item for item in wallet if item[0] == asset_symbol]

            if not currency or not asset:
                print('Error: provided incorrect currency pairs')
                return wallet

            ticker = self.ticker_df.loc[self.ticker_df['pair'] == action.pair]
            close_price = ticker['close'].iloc[0]

            # print('self.previous_action:', self.previous_action)

            # None
            if action.action == ts.none:
                self.previous_action = action.action
                continue
            # Buy
            elif action.action == ts.buy:
                curr_total = currency[0][1]
                if curr_total <= 0:
                    # print('want to buy, not enough assets..')
                    continue
                print(colored('buying ' + action.pair, 'green'))
                asset[0] = (asset[0][0], asset[0][1] + (currency[0][1] / close_price))
                currency[0] = (currency[0][0], 0.0)
                new_wallet = [currency[0] if currency[0][0] == e[0] else e for e in wallet]
                new_wallet = [asset[0] if asset[0][0] == e[0] else e for e in new_wallet]
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'buy']
                wallet = new_wallet
                continue
            # Sell
            elif action.action == ts.sell:
                asset_total = asset[0][1]
                if asset_total <= 0:
                    # print('want to sell, not enough assets..')
                    continue
                print(colored('selling ' + action.pair, 'red'))
                currency[0] = (currency[0][0], currency[0][1] + (asset[0][1] * close_price))
                asset[0] = (asset[0][0], 0.0)
                new_wallet = [currency[0] if currency[0][0] == e[0] else e for e in wallet]
                new_wallet = [asset[0] if asset[0][0] == e[0] else e for e in new_wallet]
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'sell']
                wallet = new_wallet
                continue
        del actions[:]
        return wallet

    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        # TODO: update wallets balance
        print('refreshing wallet')
        return wallet
