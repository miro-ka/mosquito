import datetime
import pandas as pd
from poloniex import Poloniex, PoloniexError
from core.bots.enums import TradeMode
from exchanges.base import Base
from strategies.enums import TradeState
from termcolor import colored
from json import JSONDecodeError
import time
from core.bots.enums import BuySellMode
import configargparse


class Polo(Base):
    """
    Poloniex interface
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--polo_api_key', help='Poloniex API key')
    arg_parser.add("--polo_secret", help='Poloniex secret key')
    arg_parser.add("--polo_txn_fee", help='Poloniex txn. fee')
    arg_parser.add("--polo_buy_order", help='Poloniex buy order type')
    arg_parser.add("--polo_sell_order", help='Poloniex sell order type')

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Polo, self).__init__()
        api_key = args.polo_api_key
        secret = args.polo_secret
        self.transaction_fee = float(args.polo_txn_fee)
        self.polo = Poloniex(api_key, secret)
        self.buy_order_type = args.polo_buy_order
        self.sell_order_type = args.polo_sell_order
        self.verbosity = args.verbosity
        self.pair_delimiter = '_'
        self.tickers_cache_refresh_interval = 50  # If the ticker request is within the interval, get data from cache
        self.last_tickers_fetch_epoch = 0  #
        self.last_tickers_cache = None  # Cache for storing immediate tickers

    def get_balances(self):
        """
        Return available account balances (function returns ONLY currencies > 0)
        """
        try:
            balances = self.polo.returnBalances()
            only_non_zeros = {k: float(v) for k, v in balances.items() if float(v) > 0.0}
        except PoloniexError as e:
            print(colored('!!! Got exception (polo.get_balances): ' + str(e), 'red'))
            only_non_zeros = dict()

        return only_non_zeros

    def get_symbol_ticker(self, symbol, candle_size=5):
        """
        Returns real-time ticker Data-Frame for given symbol/pair
        Info: Currently Poloniex returns tickers for ALL pairs. To speed the queries and avoid
              unnecessary API calls, this method implements temporary cache
        """
        epoch_now = int(time.time())
        if epoch_now < (self.last_tickers_fetch_epoch + self.tickers_cache_refresh_interval):
            # If the ticker request is within cache_fetch_interval, try to get data from cache
            pair_ticker = self.last_tickers_cache[symbol].copy()
        else:
            # If cache is too old fetch data from Poloniex API
            try:
                ticker = self.polo.returnTicker()
                pair_ticker = ticker[symbol]
                self.last_tickers_fetch_epoch = int(time.time())
                self.last_tickers_cache = ticker.copy()
            except (PoloniexError | JSONDecodeError) as e:
                print(colored('!!! Got exception in get_symbol_ticker. Details: ' + str(e), 'red'))
                pair_ticker = self.last_tickers_cache[symbol].copy()
                pair_ticker = dict.fromkeys(pair_ticker, None)

        df = pd.DataFrame.from_dict(pair_ticker, orient="index")
        df = df.T
        # We will use 'last' price as closing one
        df = df.rename(columns={'last': 'close', 'baseVolume': 'volume'})
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['pair'] = symbol
        df['date'] = int(datetime.datetime.utcnow().timestamp())
        return df

    def return_ticker(self):
        """
        Returns ticker for all currencies
        """
        return self.polo.returnTicker()

    def cancel_order(self, order_number):
        """
        Cancels order for given order number
        """
        return self.polo.cancelOrder(order_number)

    def return_open_orders(self, currency_pair='all'):
        """
        Returns your open orders
        """
        return self.polo.returnOpenOrders(currency_pair)

    def get_pairs(self):
        """
        Returns ticker pairs for all currencies
        """
        ticker = self.polo.returnTicker()
        return list(ticker)

    def get_candles_df(self, currency_pair, epoch_start, epoch_end, period=False):
        """
        Returns candlestick chart data in pandas dataframe
        """
        try:
            data = self.polo.returnChartData(currency_pair, period, epoch_start, epoch_end)
            df = pd.DataFrame(data)
            df = df.tail(1)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            df['pair'] = currency_pair
            return df
        except (PoloniexError, JSONDecodeError) as e:
            print()
            print(colored('!!! Got exception while retrieving polo data:' + str(e) + ', pair: ' + currency_pair, 'red'))
        return pd.DataFrame()

    def get_candles(self, currency_pair, epoch_start, epoch_end, period=False):
        """
        Returns candlestick chart data
        """
        data = []
        try:
            data = self.polo.returnChartData(currency_pair, period, epoch_start, epoch_end)
        except (PoloniexError, JSONDecodeError) as e:
            print()
            print(colored('!!! Got exception while retrieving polo data:' + str(e) + ', pair: ' + currency_pair, 'red'))
        return data

    def trade(self, actions, wallet, trade_mode):
        if trade_mode == TradeMode.backtest:
            return Base.trade(actions, wallet, trade_mode)
        else:
            actions = self.life_trade(actions)
            return actions

    def life_trade(self, actions):
        """
        Places orders and returns order number
        !!! For now we are NOT handling postOnly type of orders !!!
        """
        for action in actions:

            if action.action == TradeState.none:
                actions.remove(action)
                continue

            # Handle buy_sell mode
            wallet = self.get_balances()
            if action.buy_sell_mode == BuySellMode.all:
                action.amount = self.get_buy_sell_all_amount(wallet, action)
            elif action.buy_sell_mode == BuySellMode.fixed:
                action.amount = self.get_fixed_trade_amount(wallet, action)

            if self.verbosity:
                print('Processing live-action: ' + str(action.action) +
                      ', amount:', str(action.amount) +
                      ', pair:', action.pair +
                      ', rate:', str(action.rate) +
                      ', buy_sell_mode:', action.buy_sell_mode)

            # If we don't have enough assets, just skip/remove the action
            if action.amount == 0.0:
                print(colored('No assets to buy/sell, ...skipping: ' + str(action.amount) + ' ' + action.pair, 'green'))
                actions.remove(action)
                continue

            # ** Buy Action **
            if action.action == TradeState.buy:
                try:
                    print(colored('Setting buy order: ' + str(action.amount) + '' + action.pair, 'green'))
                    action.order_number = self.polo.buy(action.pair, action.rate, action.amount, self.buy_order_type)
                except PoloniexError as e:
                    print(colored('Got exception: ' + str(e) + ' Txn: buy-' + action.pair, 'red'))
                    continue
                amount_unfilled = action.order_number.get('amountUnfilled')
                if float(amount_unfilled) == 0.0:
                    actions.remove(action)
                    print(colored('Bought: ' + str(action.amount) + '' + action.pair, 'green'))
                else:
                    action.amount = amount_unfilled
                    print(colored('Not filled 100% buy txn. Unfilled amount: ' + str(amount_unfilled) + '' + action.pair, 'red'))

            # ** Sell Action **
            elif action.action == TradeState.sell:
                try:
                    print(colored('Setting sell order: ' + str(action.amount) + '' + action.pair, 'yellow'))
                    action.order_number = self.polo.sell(action.pair, action.rate,  action.amount, self.buy_order_type)
                except PoloniexError as e:
                    print(colored('Got exception: ' + str(e) + ' Txn: sell-' + action.pair, 'red'))
                    continue
                amount_unfilled = action.order_number.get('amountUnfilled')
                if float(amount_unfilled) == 0.0:
                    actions.remove(action)
                    print(colored('Sold: ' + str(action.amount) + '' + action.pair, 'yellow'))
                else:
                    action.amount = amount_unfilled
                    print(colored('Not filled 100% sell txn. Unfilled amount: ' + str(amount_unfilled) + '' + action.pair, 'red'))
        return actions

