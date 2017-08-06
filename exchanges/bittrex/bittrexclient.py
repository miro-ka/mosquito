import time
import pandas as pd
from bittrex.bittrex import Bittrex
from core.bots.enums import TradeMode
from exchanges.base import Base
from strategies.enums import TradeState
from termcolor import colored


class BittrexClient(Base):
    """
    Bittrex interface
    """

    def __init__(self, args, verbosity=2):
        super(BittrexClient, self).__init__()
        api_key = args['api_key']
        secret = args['secret']
        self.bittrex = Bittrex(api_key, secret)
        self.pair_connect_string = '-'
        # self.buy_order_type = args['buy_order_type']
        # self.sell_order_type = args['sell_order_type']
        self.verbosity = verbosity

    def get_pairs(self):
        """
        Returns ticker pairs for all currencies
        """
        markets = self.bittrex.get_market_summaries()
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
        currency_pair = currency_pair.replace('_', self.pair_connect_string)
        pattern = '%Y-%m-%dT%H:%M:%S'
        res = self.bittrex.get_ticks(currency_pair, 'fiveMin')
        tickers = res['result']
        got_min_epoch_ticker = False
        raw_tickers = []

        # Parse tickers
        for ticker in tickers:
            epoch = int(time.mktime(time.strptime(ticker['T'], pattern)))

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
            print('Not able to get all data (data not available) for pair:', currency_pair)

        # Create/interpolate raw tickers to fit our interval ticker
        out_tickers = []
        for ticker_epoch in range(epoch_start, epoch_end, period):
            items = [element for element in raw_tickers if element['date'] <= ticker_epoch]
            if len(items) < 0:
                print(colored('Could not found a ticker for:', currency_pair, ticker_epoch), 'red')
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

    def get_symbol_ticker(self, symbol):
        """
        Returns real-time ticker Data-Frame
        """
        market = symbol.replace('_', self.pair_connect_string)
        ticker = self.bittrex.get_ticker(market)

        df = pd.DataFrame.from_dict(ticker['result'], orient="index")
        df = df.T
        # We will use 'last' price as closing one
        df = df.rename(columns={'Last': 'close', 'Ask': 'ask', 'Bid': 'bid'})
        df['volume'] = None
        df['pair'] = symbol
        df['date'] = int(time.time())
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

    @staticmethod
    def get_buy_sell_all_amount(wallet, action, pair, rate):
        """
        Calculates total amount for ALL assets in wallet
        """
        if action == TradeState.none:
            return 0.0

        if rate == 0.0:
            print(colored('Got zero rate!. Can not calc. buy_sell_amount for pair: ' + pair, 'red'))
            return 0.0

        (symbol_1, symbol_2) = tuple(pair.split('_'))
        amount = 0.0
        if action == TradeState.buy and symbol_1 in wallet:
            assets = wallet.get(symbol_1)
            amount = assets / rate
        elif action == TradeState.sell and symbol_2 in wallet:
            assets = wallet.get(symbol_2)
            amount = assets
        return amount

    def life_trade(self, actions):
        """
        Places orders and returns order number
        """
        for action in actions:
            if self.verbosity > 0:
                print('Processing live-action: ' + str(action.action) +
                      ', amount:', str(action.amount) +
                      ', pair:', action.pair +
                      ', rate:', str(action.rate) +
                      ', buy_sell_all:', action.buy_sell_all)
            if action.action == TradeState.none:
                actions.remove(action)
                continue

            # Handle buy_sell_all cases
            wallet = self.get_balances()
            if action.buy_sell_all:
                action.amount = self.get_buy_sell_all_amount(wallet, action.action, action.pair, action.rate)

            # If we don't have enough assets, just skip/remove the action
            if action.amount == 0.0:
                print(colored('No assets to buy/sell, ...skipping: ' + str(action.amount) + action.pair, 'green'))
                actions.remove(action)
                continue

            # ** Buy Action **
            if action.action == TradeState.buy:
                print(colored('setting buy order: ' + str(action.amount) + '' + action.pair, 'green'))
                ret = self.bittrex.buy_limit(action.pair, action.rate, action.amount)
                if not ret['success']:
                    print(colored('Error: ' + ret['message'] + '. Txn: buy-' + action.pair, 'red'))
                    continue
                print(ret)

                # except PoloniexError as e:
                #    print(colored('Got exception: ' + str(e) + 'txn: buy-' + action.pair, 'red'))
                #    continue
                # amount_unfilled = action.order_number.get('amountUnfilled')
                # if amount_unfilled == 0.0:
                #     actions.remove(action)
                # else:
                #    action.amount = amount_unfilled
            # ** Sell Action **
            elif action.action == TradeState.sell:
                try:
                    print(colored('setting sell order: ' + str(action.amount) + '' + action.pair, 'red'))
                    action.order_number = self.bittrex.sell(action.pair, action.rate,  action.amount, self.buy_order_type)
                except PoloniexError as e:
                    print(colored('Got exception: ' + str(e) + 'txn: sell-' + action.pair, 'red'))
                    continue
                amount_unfilled = action.order_number.get('amountUnfilled')
                if amount_unfilled == 0.0:
                    actions.remove(action)
                else:
                    action.amount = amount_unfilled
        return actions







    def return_ticker(self):
        # TODO
        raise Exception('return_ticker')

        """
        Returns ticker for all currencies
        """
        return self.bittrex.returnTicker()

    def cancel_order(self, order_number):
        """
        Cancels order for given order number
        """
        # TODO
        raise Exception('cancel_order')
        return self.bittrex.cancelOrder(order_number)

    def return_open_orders(self, currency_pair='all'):
        """
        Returns your open orders
        """
        # TODO
        raise Exception('return_open_orders')
        return self.bittrex.returnOpenOrders(currency_pair)
