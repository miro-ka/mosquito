import talib

from core.tradeaction import TradeAction
from .base import Base
from .enums import TradeState
from lib.indicators.macd import macd
from lib.indicators.ropc import ropc
import math
import numpy
from core.bots.enums import BuySellMode


class Mosquito(Base):
    """
    !!! ONLY IN DEVELOPMENT AND TESTED ONLY IN BACK-TEST !!!
    About: Multi-currency strategy focusing on buying most profitable strategy
    """

    def __init__(self, args, verbosity=2, pair_delimiter='_'):
        super(Mosquito, self).__init__(args, verbosity, pair_delimiter)
        self.name = 'mosquito'
        self.min_history_ticks = 26
        self.previous_obv = {}
        self.obv_interval = 3
        self.previous_macds = {}
        self.prev_pair_adx = {}
        self.buy_sell_mode = BuySellMode.fixed
        self.active_pairs = []

    def calculate(self, look_back, wallet):
        """
        Main Strategy function, which takes recent history data and returns recommended list of actions
        """

        (dataset_cnt, pairs_count) = self.get_dataset_count(look_back, self.group_by_field)



        close_pair_price = self.get_price(TradeState.buy, look_back, 'BTC_ETH')
        action = TradeAction('BTC_ETH',
                             TradeState.buy,
                             amount=None,
                             rate=close_pair_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)
        return self.actions


        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt)
            return self.actions

        self.actions.clear()
        look_back = look_back.tail(pairs_count * self.min_history_ticks)
        pairs_names = look_back.pair.unique()

        self.sync_active_pairs(wallet.current_balance)

        positive_pairs = []
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

            # *** Add conditions ***
            # MACD - Skip pairs that has down-trending indicator
            if self.verbosity > 5:
                print('macd_value:', macd_value)
                print('signal_line:', signal_line)
            if math.isnan(macd_value) or 0 > macd_value < signal_line:
                # print('Got negative macd, skipping pair: ' + pair)
                continue

            # ************** Calc EMA
            sma_interval_short = 5
            sma_interval_long = 15
            sma_short = talib.SMA(close[-sma_interval_short:], timeperiod=sma_interval_short)[-1]
            sma_long = talib.SMA(close[-sma_interval_long:], timeperiod=sma_interval_long)[-1]
            if sma_short <= sma_long:  # If we are below death cross, skip pair
                continue

            # ************** ROPC
            ropc_interval = 5
            ropc_res = ropc(close[-ropc_interval:], timeperiod=ropc_interval)
            if ropc_res < 1.0:
                continue

            positive_pairs.append((pair, sma_short))

        # Handle all the pairs that have not been selected (are not up-trending)
        positive_pair_names = [(i[0]).split(self.pair_delimiter, 1)[-1] for i in positive_pairs]
        pair_prefix = pairs_names[0].split(self.pair_delimiter, 1)[0]
        for wallet_item in wallet.current_balance:
            if wallet_item == pair_prefix:
                continue
            if wallet_item not in positive_pair_names:
                pair_name = pair_prefix + self.pair_delimiter + wallet_item
                close_pair_price = self.get_price(TradeState.sell, look_back, pair_name)
                action = TradeAction(pair_name,
                                     TradeState.sell,
                                     amount=None,
                                     rate=close_pair_price,
                                     buy_sell_mode=self.buy_sell_mode)
                self.actions.append(action)
                if pair_name in self.active_pairs:
                    self.active_pairs.remove(pair_name)

        # Handle positive pairs
        # Sort indicators
        sorted_positives = sorted(positive_pairs, key=lambda x: x[1], reverse=True)
        print('sorted_indicators:', len(sorted_positives), 'items:', sorted_positives)
        for (positive_pair, _) in sorted_positives:
            # Check if we have already bought the currency. If yes, just skip it
            if positive_pair in self.active_pairs:
                continue

            # If pair is not bought yet, buy it
            close_pair_price = self.get_price(TradeState.buy, look_back, positive_pair)
            action = TradeAction(positive_pair,
                                 TradeState.buy,
                                 amount=None,
                                 rate=close_pair_price,
                                 buy_sell_mode=self.buy_sell_mode)
            self.active_pairs.append(positive_pair)
            self.actions.append(action)

        return self.actions

    def sync_active_pairs(self, wallet):
        """
        Synchronizes active_pairs container with current_balance
        """
        for active_pair in list(self.active_pairs):
            if active_pair not in wallet:
                self.active_pairs.remove(active_pair)
