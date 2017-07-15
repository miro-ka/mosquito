from .base import Base
from .enums import TradeState as ts
from .tradeaction import TradeAction
import talib


class Ema(Base):
    """
    ema strategy
    """

    actions = []

    def __init__(self, args):
        super(Ema, self).__init__(args)
        self.name = 'ema'
        self.min_history_ticks = 5
        self.pair = 'BTC_ETH'

    def calculate(self, look_back, wallet):
        """
        Main strategy logic (the meat of the strategy)
        """

        (dataset_cnt, pairs_count) = self.get_dataset_count(look_back, self.group_by_field)
        print('dataset_cnt:', dataset_cnt)

        if dataset_cnt < self.min_history_ticks:
            action = TradeAction('BTC_ETH', ts.none, None, False)
            self.actions.append(action)
            return self.actions

        # print('----running strategy ema')

        df = look_back[look_back['pair'] == self.pair]
        close = df['close'].values
        # volume = df['volume'].values
        end_index = len(df.index) - 1
        ema = talib.EMA(close, timeperiod=len(close))[end_index]
        slope = talib.LINEARREG_SLOPE(close, timeperiod=len(close))[end_index]
        new_action = ts.none
        # new_action = ts.buy

        print('ema:', ema, ', slope:', slope)

        if slope >= 0:
            new_action = ts.buy

        if slope < 0:
            new_action = ts.sell

        # obv = talib.OBV(close, volume)[-1]

        action = TradeAction(self.pair, new_action, None, True)
        self.actions.append(action)
        return self.actions



