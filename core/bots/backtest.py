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
        self.transaction_fee = float(self.config['Trade']['transaction_fee'])
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

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        if self.ticker_df.empty:
            print('Can not trade with empty dataframe, skipping trade')
            return wallet

        for action in actions:
            # If we are forcing_sell, we will first sell all our assets
            if force_sell:
                assets = wallet.copy()
                del assets['BTC']
                for asset, value in assets.items():
                    pair = 'BTC_' + asset
                    ticker = self.ticker_df.loc[self.ticker_df['pair'] == pair]
                    if ticker.empty:
                        print('No currency data for pair: ' + pair + ', skipping')
                        continue
                    close_price = ticker['close'].iloc[0]
                    value -= (self.transaction_fee*value)/100.0
                    earned_balance = close_price * value
                    root_symbol = 'BTC'
                    currency = wallet[root_symbol]
                    # Store trade history
                    trades.loc[len(trades)] = [ticker['date'].iloc[0], pair, close_price, 'sell']
                    wallet[root_symbol] = currency + earned_balance
                    wallet[asset] = 0.0

            (currency_symbol, asset_symbol) = tuple(action.pair.split('_'))
            # Get pairs current closing price
            ticker = self.ticker_df.loc[self.ticker_df['pair'] == action.pair]
            close_price = ticker['close'].iloc[0]

            currency_balance = asset_balance = 0.0
            if currency_symbol in wallet:
                currency_balance = wallet[currency_symbol]
            if asset_symbol in wallet:
                asset_balance = wallet[asset_symbol]

            # None
            if action.action == ts.none:
                self.previous_action = action.action
                continue
            # Buy
            elif action.action == ts.buy:
                if currency_balance <= 0:
                    # print('want to buy, not enough assets..')
                    continue
                print(colored('buying ' + action.pair, 'green'))
                currency_balance -= (self.transaction_fee * currency_balance) / 100.0
                wallet[asset_symbol] = asset_balance + (currency_balance / close_price)
                wallet[currency_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'buy']
                continue
            # Sell
            elif action.action == ts.sell:
                if asset_balance <= 0:
                    # print('want to sell, not enough assets..')
                    continue
                print(colored('selling ' + action.pair, 'red'))
                asset_balance -= (self.transaction_fee * asset_balance) / 100.0
                wallet[currency_symbol] = currency_balance + (asset_balance * close_price)
                wallet[asset_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'sell']
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
