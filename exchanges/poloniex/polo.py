import datetime
import pandas as pd
from poloniex import Poloniex, PoloniexError
from core.bots.enums import TradeMode
from exchanges.base import Base
from strategies.enums import TradeState
from termcolor import colored
from json import JSONDecodeError


class Polo(Base):
    """
    Poloniex interface
    """

    def __init__(self, polo_args, verbosity=2):
        super(Polo, self).__init__()
        api_key = polo_args['api_key']
        secret = polo_args['secret']
        self.polo = Poloniex(api_key, secret)
        self.buy_order_type = polo_args['buy_order_type']
        self.sell_order_type = polo_args['sell_order_type']
        self.verbosity = verbosity

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
        Returns real-time ticker Data-Frame
        """
        ticker = self.polo.returnTicker()[symbol]
        df = pd.DataFrame.from_dict(ticker, orient="index")
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

    def return_candles(self, currency_pair, epoch_start, epoch_end, period=False):
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

            # Handle buy_sell_all cases
            wallet = self.get_balances()
            if action.buy_sell_all:
                action.amount = self.get_buy_sell_all_amount(wallet, action.action, action.pair, action.rate)

            if self.verbosity > 0:
                print('Processing live-action: ' + str(action.action) +
                      ', amount:', str(action.amount) +
                      ', pair:', action.pair +
                      ', rate:', str(action.rate) +
                      ', buy_sell_all:', action.buy_sell_all)

            # If we don't have enough assets, just skip/remove the action
            if action.amount == 0.0:
                print(colored('No assets to buy/sell, ...skipping: ' + str(action.amount) + action.pair, 'green'))
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
            amount = assets/rate
        elif action == TradeState.sell and symbol_2 in wallet:
            assets = wallet.get(symbol_2)
            amount = assets

        return amount
