import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState
from sklearn.preprocessing import scale


class Mosquito(Base):
    """
    About: Multi-currency strategy focusing on buying most profitable strategy
    """

    def __init__(self, args):
        super(Mosquito, self).__init__(args)
        self.name = 'mosquito'
        self.data_intervals = [3, 6, 9]
        self.min_history_ticks = self.data_intervals[-1]

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

        indicators = []  # tuple(pair, interval, slope, ema, obv)
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            # Scale data
            df_close = scale(df['close'].values)
            df_volume = scale(df['volume'].values)

            # For every pair get slope of every interval
            for interval in self.data_intervals:
                # Calculate slope/angle
                slope = talib.LINEARREG_ANGLE(df_close[-interval:], timeperiod=interval)[-1]
                # Calculate ema
                ema = talib.EMA(df_close[-interval:], timeperiod=interval)[-1]
                # Calculate obv
                obv = talib.OBV(df_close[-interval:], df_volume[-interval:])[-1]
                # Store data
                indicators.append((pair, interval, slope, ema, obv))

        # Sort indicators
        slope_sorted = sorted(indicators, key=lambda x: x[2], reverse=True)
        ema_sorted = sorted(indicators, key=lambda x: x[3], reverse=True)
        obv_sorted = sorted(indicators, key=lambda x: x[4], reverse=True)

        # Get first winner/sorted pair for every interval
        slope_winners = []
        ema_winners = []
        obv_winners = []
        for idx, interval in enumerate(self.data_intervals):
            slope_winners.append(slope_sorted[idx][0])
            ema_winners.append(ema_sorted[idx][0])
            obv_winners.append(obv_sorted[idx][0])

        # If all intervals have the same winner let's buy
        # has_unique_slope_winner = all(x == slope_winners[0] for x in slope_winners)
        # has_unique_ema_winner = all(x == ema_winners[0] for x in ema_winners)
        has_unique_obv_winner = all(x == obv_winners[0] for x in obv_winners)

        if has_unique_obv_winner:
            # Check if the winner is positive
            winner_value = obv_sorted[0][4]
            if winner_value <= 0:
                return actions
            winner_pair = ema_winners[0]
            close_pair_price = look_back.loc[look_back['pair'] == winner_pair].sort_values('date').close.iloc[0]
            action = TradeAction(winner_pair,
                                 TradeState.buy,
                                 amount=None,
                                 rate=close_pair_price,
                                 buy_sell_all=True)
            actions.append(action)
        return actions



