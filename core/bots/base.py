import re
import math
import time
import pandas as pd
import configargparse
import core.common as common
from termcolor import colored
from abc import ABC, abstractmethod
from backfill import main as backfill
from exchanges.exchange import Exchange
from strategies.enums import TradeState
from core.bots.enums import BuySellMode


class Base(ABC):
    """
    Base class for all simulation types (sim, paper, trade)
    """
    ticker_df = pd.DataFrame()
    pairs = []
    exchange = None
    balance = None
    arg_parser = configargparse.get_argument_parser()

    def __init__(self, trade_mode):
        super(Base, self).__init__()
        self.args = self.arg_parser.parse_known_args()[0]
        self.exchange = Exchange(trade_mode)
        self.transaction_fee = self.exchange.get_transaction_fee()
        self.ticker_df = pd.DataFrame()
        self.verbosity = self.args.verbosity
        self.pairs = common.parse_pairs(self.exchange, self.args.pairs)
        self.fixed_trade_amount = float(self.args.fixed_trade_amount)
        self.pair_delimiter = self.exchange.get_pair_delimiter()
        self.last_tick_epoch = 0

    def get_pair_delimiter(self):
        """
        Returns exchanges pair delimiter
        """
        return self.pair_delimiter

    def prefetch(self, min_ticker_size, ticker_interval):
        """
        Method pre-fetches data to ticker buffer
        """
        prefetch_epoch_size = ticker_interval * min_ticker_size * 60
        prefetch_days = math.ceil(prefetch_epoch_size / 86400)
        # Prefetch/Backfill data
        self.args.days = prefetch_days
        orig_pair = self.args.pairs
        for pair in self.pairs:
            self.args.pairs = pair
            backfill(self.args)
        self.args.pairs = orig_pair
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
        # Remove all items with zero amount
        self.balance = {k: v for k, v in self.balance.items() if v != 0}
        return self.balance

    def sell_all_assets(self, trades, wallet, pair_to_hold):
        """
        Sells all available assets in wallet
        """
        assets = wallet.copy()
        del assets['BTC']
        for asset, amount in assets.items():
            if amount == 0.0:
                continue
            pair = 'BTC' + self.pair_delimiter + asset
            # If we have the same pair that we want to buy, lets not sell it
            if pair == pair_to_hold:
                continue
            ticker = self.ticker_df.loc[self.ticker_df['pair'] == pair]
            if ticker.empty:
                print('No currency data for pair: ' + pair + ', skipping')
                continue
            close_price = ticker['close'].iloc[0]
            fee = self.transaction_fee * float(amount) / 100.0
            print('txn fee:', fee, ', balance before: ', amount, ', after: ', amount - fee)
            print(colored('Sold: ' + str(amount) + ', pair: ' + pair + ', price: ' + str(close_price), 'yellow'))
            amount -= fee
            earned_balance = close_price * amount
            root_symbol = 'BTC'
            currency = wallet[root_symbol]
            # Store trade history
            trades.loc[len(trades)] = [ticker['date'].iloc[0], pair, close_price, 'sell']
            wallet[root_symbol] = currency + earned_balance
            wallet[asset] = 0.0

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
            # If action is None, just skip it
            if action.action == TradeState.none:
                actions.remove(action)
                continue

            # If we are forcing_sell, we will first sell all our assets
            if force_sell:
                self.sell_all_assets(trades, wallet, action.pair)

            # Get pairs current closing price
            (currency_symbol, asset_symbol) = tuple(re.split('[-_]', action.pair))
            ticker = self.ticker_df.loc[self.ticker_df['pair'] == action.pair]

            if len(ticker.index) == 0:
                print('Could not find pairs ticker, skipping trade')
                continue

            close_price = action.rate

            currency_balance = asset_balance = 0.0
            if currency_symbol in wallet:
                currency_balance = wallet[currency_symbol]
            if asset_symbol in wallet:
                asset_balance = wallet[asset_symbol]

            if action.buy_sell_mode == BuySellMode.all:
                action.amount = self.get_buy_sell_all_amount(wallet, action)
            elif action.buy_sell_mode == BuySellMode.fixed:
                action.amount = self.get_fixed_trade_amount(wallet, action)

            fee = self.transaction_fee * float(action.amount) / 100.0
            # *** Buy ***
            if action.action == TradeState.buy:
                if currency_balance <= 0:
                    print('Want to buy ' + action.pair + ', not enough money, or everything already bought..')
                    actions.remove(action)
                    continue
                print(colored('Bought: ' + str(action.amount) + ', pair: ' + action.pair + ', price: ' + str(close_price), 'green'))
                wallet[asset_symbol] = asset_balance + action.amount - fee
                wallet[currency_symbol] = currency_balance - (action.amount*action.rate)
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'buy']
                actions.remove(action)
                continue

            # *** Sell ***
            elif action.action == TradeState.sell:
                if asset_balance <= 0:
                    print('Want to sell ' + action.pair + ', not enough assets, or everything already sold..')
                    actions.remove(action)
                    continue
                print(colored('Sold: ' + str(action.amount) + '' + action.pair + ', price: ' + str(close_price), 'yellow'))
                wallet[currency_symbol] = currency_balance + ((action.amount-fee)*action.rate)
                wallet[asset_symbol] = asset_balance - action.amount
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'sell']
                actions.remove(action)
                continue
        self.balance = wallet
        return actions

    def get_buy_sell_all_amount(self, wallet, action):
        """
        Calculates total amount for ALL assets in wallet
        """
        if action.action == TradeState.none:
            return 0.0

        if action.rate == 0.0:
            print(colored('Got zero rate!. Can not calc. buy_sell_amount for pair: ' + action.pair, 'red'))
            return 0.0

        (symbol_1, symbol_2) = tuple(action.pair.split(self.pair_delimiter))
        amount = 0.0
        if action.action == TradeState.buy and symbol_1 in wallet:
            assets = wallet.get(symbol_1)
            amount = assets / action.rate
        elif action.action == TradeState.sell and symbol_2 in wallet:
            assets = wallet.get(symbol_2)
            amount = assets

        if amount <= 0.0:
            return 0.0
        return amount

    def get_fixed_trade_amount(self, wallet, action):
        """
        Calculates fixed trade amount given action
        """
        if action.action == TradeState.none:
            return 0.0

        if action.rate == 0.0:
            print(colored('Got zero rate!. Can not calc. buy_sell_amount for pair: ' + action.pair, 'red'))
            return 0.0

        (symbol_1, symbol_2) = tuple(action.pair.split(self.pair_delimiter))
        amount = 0.0
        if action.action == TradeState.buy and symbol_1 in wallet:
            assets = self.fixed_trade_amount
            amount = assets / action.rate
        elif action.action == TradeState.sell and symbol_2 in wallet:
            assets = wallet.get(symbol_2)
            amount = assets

        if amount <= 0.0:
            return 0.0
        return amount
