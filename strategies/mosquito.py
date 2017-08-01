import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState as ts


class Mosquito(Base):
    """
    Strategy with focus to monitor multiple currencies and buy & keep only the most profitable currencies
    """

    def __init__(self, args):
        super(Mosquito, self).__init__(args)
        self.name = 'mosquito'
        self.min_history_ticks = 6  # 30 minutes of data

    def calculate(self, look_back, wallet):
        """
        Main Strategy function, which takes recent history data and returns recommended list of actions
        """
        actions = []

        (dataset_cnt, pairs_count) = self.get_dataset_count(look_back, self.group_by_field)
        print('dataset_cnt:', dataset_cnt)

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            return actions

        look_back = look_back.tail(pairs_count * self.min_history_ticks)

        pairs_names = look_back.pair.unique()
        indicators = []
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            close = df['close'].values
            # volume = df['volume']
            end_index = len(df.index)-1
            # if we have only 1 item, skip pair (not enough data)
            if len(df.index) <= 1:
                print("Can't run ta-lib with only one element. Pair: ", pair)
                continue
            ema = talib.EMA(close, timeperiod=len(close))[end_index]
            slope = talib.LINEARREG_SLOPE(close, timeperiod=len(close))[end_index]
            indicators.append((pair, ema, slope, close))

        # Get currency with the highest EMA
        # ema_sorted = sorted(indicators, key=lambda x: x[1], reverse=True)
        slope_sorted = sorted(indicators, key=lambda x: x[2], reverse=True)

        (winner_pair, ema, slope, close) = slope_sorted[0]
        # print('mosquito: slopes: ', slope_sorted)
        # TODO Calculated success probability
        # obv = talib.OBV(close, volume)[-1]
        action = TradeAction(winner_pair, ts.buy, None, close, True)
        actions.append(action)
        return actions



