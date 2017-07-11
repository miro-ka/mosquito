from abc import ABC, abstractmethod
import configparser
import pandas as pd
from termcolor import colored
from strategies.enums import TradeState as ts


class Base(ABC):
    """
    Base class for all simulation types (sim, paper, trade)
    """
    ticker_df = pd.DataFrame()
    pairs = []
    exchange = None

    def __init__(self, args, config_file):
        super(Base, self).__init__()
        self.args = args

    def process_input_pairs(self, in_pairs):
        if in_pairs == 'all':
            print('setting_all_pairs')
            return self.exchange.get_all_tickers()
            # Get all pairs from API
        else:
            return in_pairs.replace(" ", "").split(',')

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

    @abstractmethod
    def get_wallet_balance(self):
        """
        Returns wallet balance
        """
        pass

    @abstractmethod
    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        pass

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
                    if value == 0.0:
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
                    fee = self.transaction_fee*float(value)/100.0
                    print('txn fee:', fee, ', balance before: ', value, ', after: ', value-fee)
                    value -= fee
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
                    print('want to buy, not enough money, or everything already bought..')
                    continue
                print(colored('buying ' + action.pair, 'green'))
                fee = self.transaction_fee * float(currency_balance) / 100.0
                print('txn fee:', fee, ',currency_balance: ', currency_balance, ', after: ', currency_balance-fee)
                currency_balance -= fee
                wallet[asset_symbol] = asset_balance + (currency_balance / close_price)
                wallet[currency_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'buy']
                continue
            # Sell
            elif action.action == ts.sell:
                if asset_balance <= 0:
                    print('want to buy, not enough money, or everything already sold..')
                    continue
                print(colored('selling ' + action.pair, 'red'))
                fee = self.transaction_fee * float(currency_balance) / 100.0
                print('txn fee:', fee, ',asset_balance: ', asset_balance, ', after: ', asset_balance-fee)
                asset_balance -= fee
                wallet[currency_symbol] = currency_balance + (asset_balance * close_price)
                wallet[asset_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'sell']
                continue
        del actions[:]
        return wallet
