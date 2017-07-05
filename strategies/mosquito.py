from .base import Base
from .enums import TradeState as ts
from .tradeaction import TradeAction
import talib


class Mosquito(Base):
    """
    Strategy with focus to monitor entire exchange and buy & keep only the most profitable currencies
    """

    actions = []

    def __init__(self, args):
        super(Mosquito, self).__init__(args)
        self.name = 'ema'
        self.buffer_size = 3

    def calculate(self, look_back, wallet):
        """
        Main Strategy function, which takes recent history data and returns recommended list of actions
        """
        pairs_group = look_back.groupby(['pair'])
        pairs_count = len(pairs_group.groups.keys())
        dataset_cnt = pairs_group.size().iloc[0]
        print('dataset_cnt:', dataset_cnt)
        # Wait until we have enough data
        if dataset_cnt < self.buffer_size:
            return self.actions
        elif dataset_cnt > self.buffer_size:
            look_back = look_back.tail(pairs_count * self.buffer_size)

        pairs_names = look_back.pair.unique()
        indicators = []
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            close = df['close'].values
            # volume = df['volume']
            end_index = len(df.index)-1
            ema = talib.EMA(close, timeperiod=len(close))[end_index]
            slope = talib.LINEARREG_SLOPE(close, timeperiod=len(close))[end_index]
            indicators.append((pair, ema, slope))

        # Get currency with the highest EMA
        ema_sorted = sorted(indicators, key=lambda x: x[1], reverse=True)
        slope_sorted = sorted(indicators, key=lambda x: x[2], reverse=True)

        (winner_pair, ema, slope) = ema_sorted[0]

        # TODO Calculated success probability



        # print('pairs_names:', pairs_names)
        # obv = talib.OBV(close, volume)[-1]
        # TODO: sell all
        action = TradeAction(winner_pair, ts.buy, None, True)
        self.actions.append(action)
        return self.actions



