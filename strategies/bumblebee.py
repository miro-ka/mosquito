import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState
import pandas as pd
from lib.indicators.ropc import ropc
from core.bots.enums import BuySellMode


class Bumblebee(Base):
    """
    Bumblebee strategy
    About: Strategy dealing with ONLY 1 pair
    """
    def __init__(self, args, verbosity=2, pair_delimiter='_'):
        super(Bumblebee, self).__init__(args, verbosity, pair_delimiter)
        self.name = 'ema'
        self.min_history_ticks = 60  # 300 minute interval
        self.pair = 'BTC_DGB'

    def calculate(self, look_back, wallet):
        """
        Main strategy logic (the meat of the strategy)
        """

        (dataset_cnt, pairs_count) = self.get_dataset_count(look_back, self.group_by_field)
        print('dataset_cnt:', dataset_cnt)

        # !!!Debug!!!
        """
        if dataset_cnt < 0:
            return self.actions

        df = look_back.tail(self.min_history_ticks)
        df = df[df['pair'] == self.pair]
        df_last = df.iloc[[-1]]
        new_action = TradeState.sell
        rate = pd.to_numeric(df_last['close'], downcast='float').iloc[0]
        action = TradeAction(self.pair, new_action, rate=rate, buy_sell_mode=BuySellMode.all)
        self.actions.append(action)
        return self.actions
        # !!!Debug-end!!!
        """

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            # action = TradeAction(self.pair, TradeState.none, None, 0.0, False)
            # self.actions.append(action)
            return self.actions

        self.actions.clear()
        # Calculate indicators
        df = look_back.tail(self.min_history_ticks)
        df = df[df['pair'] == self.pair]
        close = df['close'].values
        volume = df['volume'].values

        # ** Ema **
        # end_index = len(df.index) - 1
        # ema = talib.EMA(close, timeperiod=len(close))[end_index]
        # print('ema:', ema)

        # ** Slope **
        # end_index = len(df.index) - 1
        # slope = talib.LINEARREG_SLOPE(close, timeperiod=len(close))[end_index]
        # print('slope:', slope)

        # ** OBV (On Balance Volume)
        obv = talib.OBV(close, volume)
        obv = obv[-1]
        print('obv:', obv)

        # Create new buy/sell order
        new_action = TradeState.none

        # Calculate perc. change for 'hand-brake
        perc_change = ropc(close, 2)
        print('perc_change:', perc_change)

        if obv >= 20:
            new_action = TradeState.buy
        elif obv < -5:  # or perc_change <= -1.0:
            new_action = TradeState.sell

        df_last = df.iloc[[-1]]

        if new_action == TradeState.none:
            return self.actions
        elif new_action == TradeState.buy:
            if 'lowestAsk' in df_last:
                rate = pd.to_numeric(df_last['lowestAsk'], downcast='float').iloc[0]
            else:
                rate = pd.to_numeric(df_last['close'], downcast='float').iloc[0]
        elif new_action == TradeState.sell:
            if 'highestBid' in df_last:
                rate = pd.to_numeric(df_last['highestBid'], downcast='float').iloc[0]
            else:
                rate = pd.to_numeric(df_last['close'], downcast='float')

        action = TradeAction(self.pair, new_action, rate=rate, buy_sell_mode=BuySellMode.all)
        self.actions.append(action)
        return self.actions



