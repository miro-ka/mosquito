import re
import talib
from .base import Base
import core.common as common
from .enums import TradeState
from core.bots.enums import BuySellMode
from core.tradeaction import TradeAction


class Mosquito(Base):
    """
    About: Multi-currency strategy focusing on buying most profitable strategy
    """
    pair_delimiter = None

    def __init__(self):
        super(Mosquito, self).__init__()
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
        if not self.pair_delimiter:
            self.pair_delimiter = self.get_delimiter(look_back)

        (dataset_cnt, pairs_count) = common.get_dataset_count(look_back, self.group_by_field)

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt)
            return self.actions

        self.actions.clear()
        look_back = look_back.tail(pairs_count * self.min_history_ticks)
        pairs_names = look_back.pair.unique()
        self.sync_active_pairs(wallet.current_balance)

        positive_pairs = []
        got_all_buffers = True
        for pair in pairs_names:
            df = look_back.loc[look_back['pair'] == pair].sort_values('date')
            # Check if the dataset has required buffer size
            df_size = len(df.index)
            if df_size < self.min_history_ticks:
                continue

            close = df['close'].values
            # volume = df['volume'].values
            close_price = self.get_price(TradeState.none, look_back, pair)

            # ************** Calc EMA20
            ema20_period = 20
            ema20 = talib.EMA(close[-ema20_period:], timeperiod=ema20_period)[-1]
            if close_price <= ema20:
                continue

            # ************** Calc RSI
            rsi = talib.RSI(close[-15:], timeperiod=14)[-1]
            if rsi > 20:
                continue

            # ************** Calc EMA
            ema_interval_short = 6
            ema_interval_long = 25
            ema_short = talib.EMA(close[-ema_interval_short:], timeperiod=ema_interval_short)[-1]
            ema_long = talib.EMA(close[-ema_interval_long:], timeperiod=ema_interval_long)[-1]
            if ema_short <= ema_long:  # If we are below death cross, skip pair
                continue

            positive_pairs.append((pair, 0.0))

        # If we didn't get all buffers just return empty actions
        if not got_all_buffers:
            return self.actions

        # Handle all the pairs that have not been selected (are not up-trending)

        positive_pair_names = [re.split('[-_]', i[0])[-1] for i in positive_pairs]
        pair_prefix = re.split('[-_]', pairs_names[0])[0]
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

        # Take only first 3 pairs
        # if len(sorted_positives) > 3:
        #    sorted_positives = sorted_positives[:3]

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
