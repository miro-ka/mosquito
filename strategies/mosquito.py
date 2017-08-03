import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState
from sklearn.preprocessing import scale


class Mosquito(Base):
    """
    About: Multi-currency strategy focusing on buying most profitable strategy
    """

    def __init__(self, args, verbosity=2):
        super(Mosquito, self).__init__(args, verbosity)
        self.name = 'mosquito'
        self.data_intervals = [26]
        self.min_history_ticks = self.data_intervals[-1]
        self.use_obv = False
        self.use_ema = True
        self.use_slope = False

    def calculate(self, look_back, wallet):
        """
        Main Strategy function, which takes recent history data and returns recommended list of actions
        """

        (dataset_cnt, pairs_count) = self.get_dataset_count(look_back, self.group_by_field)

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt)
            return self.actions

        self.actions.clear()
        look_back = look_back.tail(pairs_count * self.min_history_ticks)
        pairs_names = look_back.pair.unique()

        indicators = []  # tuple(pair, interval, slope, ema, obv)
        idx_slope = 2
        idx_ema = 3
        idx_obv = 4
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            # Scale data
            df_close = scale(df['close'].values)
            df_volume = scale(df['volume'].values)

            macd, macdsignal, macdhist = talib.MACD(df_close)

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
        slope_sorted = sorted(indicators, key=lambda x: x[idx_slope], reverse=True)
        ema_sorted = sorted(indicators, key=lambda x: x[idx_ema], reverse=True)
        obv_sorted = sorted(indicators, key=lambda x: x[idx_obv], reverse=True)

        # Get first winner/sorted pair for every interval
        slope_winners = []
        ema_winners = []
        obv_winners = []
        for idx, interval in enumerate(self.data_intervals):
            slope_winners.append(slope_sorted[idx][0])
            ema_winners.append(ema_sorted[idx][0])
            obv_winners.append(obv_sorted[idx][0])

        # If all intervals have the same winner let's buy
        has_unique_slope_winner = all(x == slope_winners[0] for x in slope_winners)
        has_unique_ema_winner = all(x == ema_winners[0] for x in ema_winners)
        has_unique_obv_winner = all(x == obv_winners[0] for x in obv_winners)

        if self.verbosity > 0:
            print('slope_winners:', slope_winners)
            print('ema_winners:', ema_winners)
            print('obv_winners:', obv_winners)

        winner_pair = None
        winner_value = None
        if self.use_obv and has_unique_obv_winner:
            print('!!! Has_unique_obv_winner!')
            winner_value = obv_sorted[0][idx_obv]
            winner_pair = obv_winners[0]

        if self.use_slope and has_unique_slope_winner:
            print('!!! Has_unique_slope_winner!')
            winner_value = slope_sorted[0][idx_slope]
            winner_pair = slope_winners[0]

        if self.use_ema and has_unique_ema_winner:
            print('!!! Has_unique_ema_winner!')
            winner_value = ema_sorted[0][idx_ema]
            winner_pair = ema_winners[0]

        # ** State check and Create action **

        # If we didn't find anything just return empty actions
        if winner_pair is None:
            self.actions.clear()
            return self.actions

        # If the value is negative, do nothing (return empty actions)
        if winner_value <= 0:
            self.actions.clear()
            return self.actions

        close_pair_price = look_back.loc[look_back['pair'] == winner_pair].sort_values('date').close.iloc[0]
        action = TradeAction(winner_pair,
                             TradeState.buy,
                             amount=None,
                             rate=close_pair_price,
                             buy_sell_all=True)
        self.actions.append(action)
        return self.actions



