from poloniex import Poloniex
from .base import Base
from core.bots.enums import TradeMode


class Polo(Base):
    """
    Poloniex interface
    """

    def __init__(self, api_key=None, secret=None, offline_mode=True):
        super(Polo, self).__init__()
        self.polo = Poloniex(api_key, secret)
        self.offline_mode = offline_mode

    def return_ticker(self):
        """
        Returns ticker for all currencies
        """
        return self.polo.returnTicker()

    def return_ticker_pairs(self):
        """
        Returns ticker pairs for all currencies
        """
        ticker = self.polo.returnTicker()
        only_btc_key = [k for k in list(ticker) if 'BTC_' in k]
        l = [(key, ticker.get(key)) for key in only_btc_key]
        only_btc_dict = dict(l)
        return only_btc_dict

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
            print('TODO:')
