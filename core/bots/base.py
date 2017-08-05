from abc import ABC, abstractmethod
import configparser
import pandas as pd
from termcolor import colored
from strategies.enums import TradeState as ts
import time
from backfill import main as backfill
from argparse import Namespace
import math
from exchanges.exchange import Exchange


class Base(ABC):
    """
    Base class for all simulation types (sim, paper, trade)
    """
    ticker_df = pd.DataFrame()
    pairs = []
    exchange = None
    balance = None

    def __init__(self, args, config_file, trade_mode):
        super(Base, self).__init__()
        self.args = args
        self.config = self.initialize_config(config_file)
        self.exchange = Exchange(args, config_file, trade_mode)
        self.transaction_fee = float(self.config['Trade']['transaction_fee'])
        self.ticker_df = pd.DataFrame()
        self.pairs = self.process_input_pairs(self.config['Trade']['pairs'])
        self.last_tick_epoch = 0
        self.transaction_fee = float(self.config['Trade']['transaction_fee'])

    def process_input_pairs(self, in_pairs):
        all_pairs = self.exchange.get_pairs()
        if in_pairs == 'all':
            print('setting_all_pairs')
            return all_pairs
        else:
            pairs = []
            parsed_pairs = in_pairs.replace(" ", "").split(',')
            for in_pair in parsed_pairs:
                if '*' in in_pair:
                    prefix = in_pair.replace('*', '')
                    pairs_list = [p for p in all_pairs if prefix in p]
                    pairs.extend(pairs_list)
                    # remove duplicates
                    pairs = list(set(pairs))
                else:
                    pairs.append(in_pair)
            return pairs

    def prefetch(self, min_ticker_size, ticker_interval):
        """
        Method pre-fetches data to ticker buffer
        """
        prefetch_epoch_size = ticker_interval * min_ticker_size * 60
        prefetch_days = math.ceil(prefetch_epoch_size / 86400)
        # Prefetch/Backfill data
        for pair in self.pairs:
            args = Namespace(pair=pair, days=prefetch_days, all=False)
            backfill(args)
        # Load data to our ticker buffer
        prefetch_epoch_size = ticker_interval * min_ticker_size * 60
        epoch_now = int(time.time())
        prefetch_epoch = epoch_now - prefetch_epoch_size
        print('Going to prefetch data of size (minutes): ', ticker_interval * min_ticker_size)
        df = pd.DataFrame()
        while prefetch_epoch < epoch_now:
            data = self.exchange.get_offline_ticker(prefetch_epoch, self.pairs)
            df = df.append(data, ignore_index=True)
            prefetch_epoch += (ticker_interval * 60)
        print('Fetching done..')
        return df

    @staticmethod
    def initialize_config(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    def get_pairs(self):
        """
        Returns the pairs the bot is working with
        """
        return self.pairs

    @abstractmethod
    def get_next(self, interval):
        """
        Gets next data set
        :param interval:
        :return: New data in DataFrame
        """
        pass

    def get_balance(self):
        """
        Returns current balance
        """
        return self.balance

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        force_sell: Sells ALL assets before buying new one
        Simulate currency buy/sell (places fictive buy/sell orders).
        Returns remaining / not - processed actions
        """
        self.balance = wallet
        if self.ticker_df.empty:
            print('Can not trade with empty dataframe, skipping trade')
            return actions

        for action in actions:
            # None
            if action.action == ts.none:
                actions.remove(action)
                continue
            # If we are forcing_sell, we will first sell all our assets
            if force_sell:
                assets = wallet.copy()
                del assets['BTC']
                for asset, amount in assets.items():
                    if amount == 0.0:
                        continue
                    pair = 'BTC_' + asset
                    # If we have the same pair that we want to buy, lets not sell it
                    if pair == action.pair:
                        continue
                    ticker = self.ticker_df.loc[self.ticker_df['pair'] == pair]
                    if ticker.empty:
                        print('No currency data for pair: ' + pair + ', skipping')
                        continue
                    close_price = ticker['close'].iloc[0]
                    fee = self.transaction_fee*float(amount)/100.0
                    print('txn fee:', fee, ', balance before: ', amount, ', after: ', amount-fee)
                    amount -= fee
                    earned_balance = close_price * amount
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

            # Buy
            if action.action == ts.buy:
                if currency_balance <= 0:
                    print('Want to buy ' + action.pair + ', not enough money, or everything already bought..')
                    actions.remove(action)
                    continue
                print(colored('Buying ' + action.pair, 'green'))
                fee = self.transaction_fee * float(currency_balance) / 100.0
                # print('txn fee:', fee, ',currency_balance: ', currency_balance, ', after: ', currency_balance-fee)
                currency_balance -= fee
                wallet[asset_symbol] = asset_balance + (currency_balance / close_price)
                wallet[currency_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'buy']
                actions.remove(action)
                continue
            # Sell
            elif action.action == ts.sell:
                if asset_balance <= 0:
                    print('Want to sell ' + action.pair + ', not enough assets, or everything already sold..')
                    actions.remove(action)
                    continue
                print(colored('Selling ' + action.pair, 'yellow'))
                fee = self.transaction_fee * float(currency_balance) / 100.0
                # print('txn fee:', fee, ',asset_balance: ', asset_balance, ', after: ', asset_balance-fee)
                asset_balance -= fee
                wallet[currency_symbol] = currency_balance + (asset_balance * close_price)
                wallet[asset_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'sell']
                actions.remove(action)
                continue
        self.balance = wallet
        return actions
