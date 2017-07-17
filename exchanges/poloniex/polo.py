from poloniex import Poloniex
from .base import Base
from core.bots.enums import TradeMode
import pandas as pd
import time


class Polo(Base):
    """
    Poloniex interface
    """

    def __init__(self, polo_args):
        super(Polo, self).__init__()
        api_key = polo_args['api_key']
        secret = polo_args['secret']
        self.polo = Poloniex(api_key, secret)
        self.buy_order_type = polo_args['buy_order_type']
        self.sell_order_type = polo_args['sell_order_type']

    def get_balances(self):
        """
        Return available account balances (function returns ONLY currencies > 0)
        """
        balances = self.polo.returnBalances()
        only_non_zeros = {k: float(v) for k, v in balances.items() if float(v) > 0.0}
        return only_non_zeros

    def get_symbol_ticker(self, symbol):
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
        df['date'] = int(time.time())
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

    def return_open_orders(self, currency_pair = 'all'):
        """
        Returns your open orders
        """
        return self.polo.returnOpenOrders(currency_pair)

    def get_all_tickers(self):
        """
        Returns ticker pairs for all currencies
        """
        ticker = self.polo.returnTicker()
        return ticker

    def return_candles(self, currency_pair, period=False, start=False, end=False):
        """
        Returns candlestick chart data
        """
        return self.polo.returnChartData(currency_pair, period, start, end)

    def trade(self, actions, wallet, trade_mode):
        if trade_mode == TradeMode.backtest:
            return Base.trade(actions, wallet)
        else:
            # TODO: implement life trading
            print('TODO: live trading')
