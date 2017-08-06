import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState
from lib.indicators.macd import macd
from lib.indicators.percentchange import percent_change
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
        self.previous_obvs1 = {}
        self.previous_obvs2 = {}
        self.interval1 = 6
        self.interval2 = 12
        self.previous_macds = {}

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
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            close = df['close'].values

            # ************** Calc OBV
            """
            volume = df['volume'].values
            obv1_now = talib.OBV(close[-self.interval1:], volume[-self.interval1:])[-1]
            obv2_now = talib.OBV(close[-self.interval2:], volume[-self.interval2:])[-1]

            if pair not in self.previous_obvs1 or pair not in self.previous_obvs2:
                # print('missing previous_obvs, skipping pair: ' + pair)
                self.previous_obvs1[pair] = obv1_now
                self.previous_obvs2[pair] = obv2_now
                continue

            obv1_prev = self.previous_obvs1[pair]
            obv2_prev = self.previous_obvs2[pair]

            obv1_perc_change = ((obv1_now - obv1_prev) * 100) / obv1_prev
            obv2_perc_change = ((obv2_now - obv2_prev) * 100) / obv2_prev

            if self.verbosity > 0:
                print('obv:')
                print('\tobv1_now:', obv1_now)
                print('\tobv2_now:', obv2_now)
                print('\tobv1_now:', obv1_prev)
                print('\tobv2_now:', obv2_prev)
                print('\tobv1_perc_change:', obv1_perc_change)
                print('\tobv2_perc_change:', obv2_perc_change)

            self.previous_obvs1[pair] = obv1_now
            self.previous_obvs2[pair] = obv2_now

            if obv1_perc_change <= 0 or obv2_perc_change <= 0:
                print('Got negative obv, skipping pair: ' + pair)
                continue

            obv_perc_change = obv1_perc_change - (obv2_perc_change/2.0)
            """

            # ************** Get MACD
            prev_pair_macds = [] if pair not in self.previous_macds else self.previous_macds[pair]
            macd_value, signal_line = macd(close, numpy.asarray(prev_pair_macds))
            prev_pair_macds.append(macd_value)
            prev_pair_macds = prev_pair_macds[-9:]
            self.previous_macds[pair] = prev_pair_macds
            if signal_line is None:
                continue

            if self.verbosity > 0:
                print('macd_value:', macd_value)
                print('signal_line:', signal_line)

            # Skip pairs that has down-trending indicator
            if math.isnan(macd_value) or macd_value < signal_line:
                print('Got negative macd, skipping pair: ' + pair)
                continue

            # ************** Calc RSI
            rsi = talib.RSI(close[-15:], timeperiod=14)[-1]
            print('rsi:', rsi)
            if rsi > 70:
                print('RSI indicating to overbought, skipping pair: ' + pair)
                continue

            # ************** Calc SMA
            sma_interva1 = 6
            sma_interva2 = 18
            sma1 = talib.SMA(close[-sma_interva1:], timeperiod=sma_interva1)[-1]
            sma2 = talib.SMA(close[-sma_interva2:], timeperiod=sma_interva2)[-1]
            print('sma1:', sma1, 'sma2:', sma2)
            if sma1 < 0.0 or sma2 < 0.0:
                continue

            # ************** Calc EMA
            ema1 = talib.EMA(close[-self.interval1:], timeperiod=self.interval1)[-1]
            ema2 = talib.EMA(close[-self.interval2:], timeperiod=self.interval2)[-1]
            print('ema1:', ema1, 'ema2:', ema2)
            if ema1 < 0.0 or ema2 < 0.0:
                continue
            # ema_perc_change = ((ema1 - ema2) * 100) / ema2

            # ************** Calc Perc Change
            perc_change1 = percent_change(df, n_size=self.interval1)
            perc_change2 = percent_change(df, n_size=self.interval2)
            if perc_change1 <= 0.0 or perc_change2 <= 0.0:
                continue
            perc_change_sum = perc_change1 + perc_change2/2.0

            indicators.append((pair, perc_change_sum))

        # Sort
        sorted_indicators = sorted(indicators, key=lambda x: x[1], reverse=True)

        if len(sorted_indicators) <= 0:
            return self.actions

        print('sorted_indicators:', sorted_indicators)
        middle_one = (len(sorted_indicators)-1) / 2
        winner = sorted_indicators[0]
        winner_pair = winner[0]
        close_pair_price = look_back.loc[look_back['pair'] == winner_pair].sort_values('date').close.iloc[0]
        action = TradeAction(winner_pair,
                             TradeState.buy,
                             amount=(round((0.01 / close_pair_price), 8)),
                             rate=close_pair_price,
                             buy_sell_all=False)
        self.actions.append(action)
        return self.actions



