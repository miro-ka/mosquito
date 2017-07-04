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
        self.min_buffer_data_size = 10

    def calculate(self, look_back):
        """
        Main Strategy function, which takes recent history data and returns recommended list of actions
        """

        dataset_cnt = look_back.groupby(['pair']).size().iloc[0]
        print('dataset_cnt:', dataset_cnt)
        # Wait until we have enough data
        if dataset_cnt < self.min_buffer_data_size:
            return self.actions

        pairs_names = look_back.pair.unique()
        ema_values = []
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            close = df['close'].values
            # volume = df['volume']
            ema = talib.EMA(close, timeperiod=len(close))[len(close)-1]
            # slope = talib.LINEARREG_SLOPE(close, timeperiod=len(close))
            ema_values.append((pair, ema))

        # Get currency with the highest EMA
        ema_sorted = sorted(ema_values, key=lambda x: x[1], reverse=True)
        (winner_pair, ema) = ema_sorted[0]

        print('pairs_names:', pairs_names)
        # obv = talib.OBV(close, volume)[-1]
        # TODO: sell all
        action = TradeAction(winner_pair, ts.buy, None, True)
        self.actions.append(action)
        return self.actions



