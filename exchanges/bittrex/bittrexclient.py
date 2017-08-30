import time
import pandas as pd
from bittrex.bittrex import Bittrex
from core.bots.enums import TradeMode
from exchanges.base import Base
from strategies.enums import TradeState
from termcolor import colored
import datetime
from datetime import timezone
from dateutil.tz import *
from dateutil.parser import *
from core.bots.enums import BuySellMode
import configargparse


class BittrexClient(Base):
    """
    Bittrex interface
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--bittrex_api_key', help='Bittrex API key')
    arg_parser.add("--bittrex_secret", help='Bittrex secret key')
    arg_parser.add("--bittrex_txn_fee", help='Bittrex txn. fee')
    open_orders = []

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(BittrexClient, self).__init__()
        api_key = args.bittrex_api_key
        secret = args.bittrex_secret
        self.transaction_fee = float(args.bittrex_txn_fee)
        self.bittrex = Bittrex(api_key, secret)
        self.pair_delimiter = '-'
        self.verbosity = args.verbosity

    def get_pairs(self):
        """
        Returns ticker pairs for all currencies
        """
        markets = self.bittrex.get_market_summaries()
        if markets is None:
            print(colored('\n! Got empty markets', 'red'))
            return None

        res = markets['result']
        pairs = []
        for market in res:
            pair = market['MarketName']
            # pair = pair.replace('-', '_')
            pairs.append(pair)
        return pairs

    def return_candles(self, currency_pair, epoch_start, epoch_end, period=300):
        """
        Returns candlestick chart data
        """
        currency_pair = currency_pair.replace('_', self.pair_delimiter)
        res = self.bittrex.get_ticks(currency_pair, 'fiveMin')
        if res is None:
            print(colored('\n! Got empty result for pair: ' + currency_pair, 'red'))
            return dict()

        tickers = res['result']
        got_min_epoch_ticker = False
        raw_tickers = []

        if tickers is None:
            print(colored('\n! Got empty tickers for pair: ' + currency_pair, 'red'))
            return dict()

        # Parse tickers
        for ticker in tickers:
            naive_dt = parse(ticker['T'])
            utc_dt = naive_dt.replace(tzinfo=tzutc())
            epoch = int(utc_dt.timestamp())

            if epoch <= epoch_start:
                got_min_epoch_ticker = True

            # Skip/remove older than wanted tickers (adding extra hours to be sure that we have the data)
            if epoch < (epoch_start - 6*3600):
                continue

            raw_ticker = dict()
            raw_ticker['high'] = ticker['H']
            raw_ticker['low'] = ticker['L']
            raw_ticker['open'] = ticker['O']
            raw_ticker['close'] = ticker['C']
            raw_ticker['volume'] = ticker['V']
            raw_ticker['quoteVolume'] = ticker['BV']
            raw_ticker['date'] = epoch
            raw_ticker['weightedAverage'] = 0.0

            raw_tickers.append(raw_ticker)
        if not got_min_epoch_ticker:
            print(colored('Not able to get all data (data not available) for pair: ' + currency_pair, 'red'))

        # Create/interpolate raw tickers to fit our interval ticker
        out_tickers = []
        for ticker_epoch in range(epoch_start, epoch_end, period):
            items = [element for element in raw_tickers if element['date'] <= ticker_epoch]
            if len(items) < 0:
                print(colored('Could not found a ticker for:' + currency_pair + ', epoch:' + str(ticker_epoch), 'red'))
                continue
            # Get the last item (should be closest to search epoch)
            item = items[-1].copy()
            item['date'] = ticker_epoch
            out_tickers.append(item)
        return out_tickers.copy()
        # return self.bittrex.returnChartData(currency_pair, period, start, end)

    def get_balances(self):
        """
        Return available account balances (function returns ONLY currencies > 0)
        """
        resp = self.bittrex.get_balances()
        balances = resp['result']
        pairs = dict()
        for item in balances:
            currency = item['Currency']
            pairs[currency] = item['Available']

        return pairs

    @staticmethod
    def get_volume_from_history(history, candle_size):
        """
        Returns volume for given candle_size
        :param history: history data
        :param candle_size: in minutes
        :return: Calculated volume for given candle_size
        """
        volume = 0.0
        epoch_now = int(time.time())
        epoch_candle_start = epoch_now - candle_size * 60
        pattern = '%Y-%m-%dT%H:%M:%S'
        for item in history:
            time_string = item['TimeStamp'].split('.', 1)[0]
            dt = datetime.datetime.strptime(time_string, pattern)
            item_epoch = dt.replace(tzinfo=timezone.utc).timestamp()
            if item_epoch >= epoch_candle_start:
                quantity = item['Quantity']
                volume += quantity
        return volume

    def get_symbol_ticker(self, symbol, candle_size=5):
        """
        Returns real-time ticker Data-Frame
        :candle_size: size in minutes to calculate the interval
        """
        market = symbol.replace('_', self.pair_delimiter)

        ticker = self.bittrex.get_ticker(market)
        history = self.bittrex.get_market_history(market, 100)['result']
        volume = self.get_volume_from_history(history, candle_size)

        df = pd.DataFrame.from_dict(ticker['result'], orient="index")
        df = df.T
        # We will use 'last' price as closing one
        df = df.rename(columns={'Last': 'close', 'Ask': 'lowestAsk', 'Bid': 'highestBid'})
        df['volume'] = volume
        df['pair'] = symbol
        df['date'] = int(datetime.datetime.utcnow().timestamp())
        return df

    def trade(self, actions, wallet, trade_mode):
        """
        Places actual buy/sell orders
        """
        if trade_mode == TradeMode.backtest:
            return Base.trade(actions, wallet, trade_mode)
        else:
            actions = self.life_trade(actions)
            return actions

    def life_trade(self, actions):
        """
        Places orders and returns order number
        """
        for action in actions:
            market = action.pair.replace('_', self.pair_delimiter)

            # Handle buy/sell mode
            wallet = self.get_balances()
            if action.buy_sell_mode == BuySellMode.all:
                action.amount = self.get_buy_sell_all_amount(wallet, action)
            elif action.buy_sell_mode == BuySellMode.fixed:
                action.amount = self.get_fixed_trade_amount(wallet, action)

            if self.verbosity:
                print('Processing live-action: ' + str(action.action) +
                      ', amount:', str(action.amount) +
                      ', pair:', market +
                      ', rate:', str(action.rate) +
                      ', buy_sell_mode:', action.buy_sell_mode)
            if action.action == TradeState.none:
                actions.remove(action)
                continue

            # If we don't have enough assets, just skip/remove the action
            if action.amount == 0.0:
                print(colored('No assets to buy/sell, ...skipping: ' + str(action.amount) + ' ' + market, 'green'))
                actions.remove(action)
                continue

            # ** Buy Action **
            if action.action == TradeState.buy:
                print(colored('setting buy order: ' + str(action.amount) + '' + market, 'green'))
                ret = self.bittrex.buy_limit(market, action.amount, action.rate)
                if not ret['success']:
                    print(colored('Error: ' + ret['message'] + '. Txn: buy-' + market, 'red'))
                    continue
                else:
                    uuid = ret['result']['uuid']
                    self.open_orders.append(uuid)
                    print(colored('Buy order placed (uuid): ' + uuid, 'green'))
                print(ret)

            # ** Sell Action **
            elif action.action == TradeState.sell:
                print(colored('setting sell order: ' + str(action.amount) + '' + market, 'yellow'))
                ret = self.bittrex.sell_limit(market, action.amount, action.rate)
                if not ret['success']:
                    print(colored('Error: ' + ret['message'] + '. Txn: sell-' + market, 'red'))
                    continue
                else:
                    uuid = ret['result']['uuid']
                    self.open_orders.append(uuid)
                    print(colored('Sell order placed (uuid): ' + uuid, 'green'))
                print(ret)
        return actions

    def cancel_order(self, order_number):
        """
        Cancels order for given order number
        """
        return self.bittrex.cancel(order_number)

    def return_open_orders(self, currency_pair=''):
        """
        Returns open orders
        """
        return self.bittrex.get_open_orders(currency_pair)
