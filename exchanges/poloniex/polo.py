from poloniex import Poloniex
from .base import Base


class Polo(Base):
    """
    Poloniex interface
    """

    def __init__(self, trade_mode, api_key=None, secret=None):
        super(Polo, self).__init__()
        self.polo = Poloniex(api_key, secret)
        self.trade_mode = trade_mode

    def return_ticker(self):
        """
        Returns ticker for all currencies
        """
        return self.polo.returnTicker()

    def return_candles(self, currency_pair, period=False, start=False, end=False):
        """
        Returns candlestick chart data
        """
        return self.polo.returnChartData(currency_pair, period, start, end)

    def trade(self, actions, wallet):
        if self.trade_mode == 'backtest':
            return Base.trade(actions, wallet)
        else:
            # TODO: implement life trading
            print('TODO:')
