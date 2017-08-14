import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState
from lib.indicators.macd import macd
from lib.indicators.ropc import ropc
import math
import numpy


class Mosquito(Base):
    """
    !!! ONLY IN DEVELOPMENT AND TESTED ONLY IN BACK-TEST !!!
    About: Multi-currency strategy focusing on buying most profitable strategy
    """

    def __init__(self, args, verbosity=2):
        super(Mosquito, self).__init__(args, verbosity)
        self.name = 'mosquito'
        self.min_history_ticks = 26
        self.previous_obv = {}
        self.obv_interval = 3
        self.previous_macds = {}
        self.active_pair = None
        self.prev_pair_adx = {}

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

        indicators = []
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            # Check if the dataset has required buffer size
            df_size = len(df.index)
            if df_size < self.min_history_ticks:
                continue

            close = df['close'].values
            volume = df['volume'].values

            # ************** Calc OBV
            obv_now = talib.OBV(close[-self.obv_interval:], volume[-self.obv_interval:])[-1]

            buffer_ready = True
            if pair not in self.previous_obv:
                # print('missing previous_obvs, skipping pair: ' + pair)
                self.previous_obv[pair] = obv_now
                buffer_ready = False

            self.previous_obv[pair] = obv_now
            if self.previous_obv[pair] > obv_now > 0:
                print('OBV is down-trending, skipping pair: ' + pair)

            # ************** Get ADX
            high = df['high'].values
            low = df['low'].values
            adx = talib.ADX(high, low, close, timeperiod=3)
            adx = adx[-1]
            if pair not in self.prev_pair_adx:
                self.prev_pair_adx[pair] = adx
                buffer_ready = False

            # ************** Get MACD
            prev_pair_macds = [] if pair not in self.previous_macds else self.previous_macds[pair]
            macd_value, signal_line = macd(close, numpy.asarray(prev_pair_macds))
            prev_pair_macds.append(macd_value)
            prev_pair_macds = prev_pair_macds[-9:]
            self.previous_macds[pair] = prev_pair_macds
            if signal_line is None:
                buffer_ready = False

            # If we don't have all data in our buffer, just skip the pair
            if not buffer_ready:
                continue

            # Add conditions
            # ADX
            if adx < self.prev_pair_adx[pair]:
                self.prev_pair_adx[pair] = adx
                continue
            self.prev_pair_adx[pair] = adx

            # MACD - Skip pairs that has down-trending indicator
            if self.verbosity > 5:
                print('macd_value:', macd_value)
                print('signal_line:', signal_line)
            if math.isnan(macd_value) or 0 > macd_value < signal_line:
                # print('Got negative macd, skipping pair: ' + pair)
                continue

            # ************** Calc EMA
            ema_interval1 = 25
            # ema_interval2 = 9
            ema1 = talib.EMA(close[-ema_interval1:], timeperiod=ema_interval1)[-1]
            # ema2 = talib.EMA(close[-ema_interval2:], timeperiod=ema_interval2)[-1]
            # print('ema1:', ema1, 'ema2:', ema2)
            if ema1 < 0.0:  # or ema2 < 0.0:
                continue

            # ************** ROPC
            ropc_interval = 5
            ropc_res = ropc(close[-ropc_interval:], timeperiod=ropc_interval)
            if ropc_res < 0.0:
                continue

            indicators.append((pair, ropc_res))

        # Handle case when no indicators have up-trend
        if len(indicators) <= 0:
            if self.active_pair is None:
                return self.actions
            # If no pair has up-trend sell the active_pair
            close_pair_price = look_back.loc[look_back['pair'] == self.active_pair].sort_values('date').close.iloc[0]
            action = TradeAction(self.active_pair,
                                 TradeState.sell,
                                 amount=None,
                                 rate=close_pair_price,
                                 buy_sell_all=True)
            # TODO: here we have to be sure that the action was successful
            self.active_pair = None
            self.actions.append(action)
            return self.actions

        # If active_pair is still up-trending keep it
        if self.active_pair is not None:
            contains_active_pair = [item for item in indicators if item[0] == self.active_pair]
            if len(contains_active_pair) > 0:
                return self.actions

        # Handle new up-trending pairs
        sorted_indicators = sorted(indicators, key=lambda x: x[1], reverse=True)
        winner = sorted_indicators[0]
        winner_pair = winner[0]
        self.active_pair = winner_pair
        close_pair_price = look_back.loc[look_back['pair'] == winner_pair].sort_values('date').close.iloc[0]
        action = TradeAction(winner_pair,
                             TradeState.buy,
                             amount=None,
                             rate=close_pair_price,
                             buy_sell_all=True)
        self.actions.append(action)
        print('sorted_indicators:', len(sorted_indicators), 'items:', sorted_indicators)
        return self.actions



