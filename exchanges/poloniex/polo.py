from poloniex import Poloniex
from types import SimpleNamespace as Namespace


class Polo:
    def __init__(self, apiKey=None, secret=None):
        self.polo = Poloniex(apiKey, secret)


    def return_ticker(self):
        '''
        Returns ticker for all currencies
        '''
        return self.polo.returnTicker()


    def return_candles(self, currencyPair, period=False, start=False, end=False):
        '''
        Returns candlestick chart data
        '''
        return self.polo.returnChartData(currencyPair, period, start, end)
