import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState


class Ema(Base):
    """
    ema strategy
    """

    actions = []

    def __init__(self, args):
        super(Ema, self).__init__(args)
        self.name = 'ema'
        self.min_history_ticks = 10
        self.pair = 'USDT_NXT'

    def calculate(self, look_back, wallet):
        """
        Main strategy logic (the meat of the strategy)
        """

        (dataset_cnt, pairs_count) = self.get_dataset_count(look_back, self.group_by_field)
        print('dataset_cnt:', dataset_cnt)

        if dataset_cnt < self.min_history_ticks:
            action = TradeAction(self.pair, TradeState.none, None, 0.0, False)
            self.actions.append(action)
            return self.actions

        # print('----running strategy ema')

        df = look_back[look_back['pair'] == self.pair]
        close = df['close'].values
        # """
        # volume = df['volume'].values
        end_index = len(df.index) - 1
        ema = talib.EMA(close, timeperiod=len(close))[end_index]
        slope = talib.LINEARREG_SLOPE(close, timeperiod=len(close))[end_index]
        new_action = TradeState.none
        # new_action = TradeState.buy

        print('ema:', ema, ', slope:', slope)

        if slope >= 0:
            new_action = TradeState.buy

        if slope < 0:
            new_action = TradeState.sell

        # obv = talib.OBV(close, volume)[-1]
        # """

        df_last = df.iloc[[-1]]
        # new_action = TradeState.buy

        if new_action == TradeState.buy:
            rate = df_last.lowestAsk.convert_objects(convert_numeric=True).iloc[0]
        elif new_action == TradeState.sell:
            rate = df_last.highestBid.convert_objects(convert_numeric=True).iloc[0]

        amount = 0.1
        action = TradeAction(self.pair, new_action, amount, rate, True)
        self.actions.append(action)
        return self.actions



