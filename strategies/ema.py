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

        """
        Returns list of pairs and their corresponding actions
        """
        # print('----running strategy ema')

        df = look_back[look_back['pair'] == 'USDT_BTC']
        close = df['close'].values
        # volume = df['volume'].values
        end_index = len(df.index) - 1
        ema = talib.EMA(close, timeperiod=len(close))[end_index]
        slope = talib.LINEARREG_SLOPE(close, timeperiod=len(close))[end_index]

        print('ema:', ema, ', slope:', slope)

        """
        obv = talib.OBV(close, volume)[-1]
        print('obv:', obv)
        new_action = ts.none
        if obv >= 300:
            new_action = ts.buy

        if obv < 300:
            new_action = ts.sell
        """

        # action = TradeAction('BTC_ETH', new_action, None, True)
        # self.actions.append(action)
        return self.actions



