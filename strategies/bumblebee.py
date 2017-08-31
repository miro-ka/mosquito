import talib
import configargparse
from .base import Base
import core.common as common
from .enums import TradeState
from core.bots.enums import BuySellMode
from core.tradeaction import TradeAction


class Bumblebee(Base):
    """
    Bumblebee strategy
    About: Combination of OBV and EMA indicators
    """
    arg_parser = configargparse.get_argument_parser()

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Bumblebee, self).__init__()
        self.name = 'bumblebee'
        self.min_history_ticks = 20  # 300 minute interval
        self.pair = self.parse_pairs(args.pairs)[0]
        self.buy_sell_mode = BuySellMode.all

    def calculate(self, look_back, wallet):
        """
        Main strategy logic (the meat of the strategy)
        """
        (dataset_cnt, _) = common.get_dataset_count(look_back, self.group_by_field)

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt)
            return self.actions

        self.actions.clear()
        # Calculate indicators

        df = look_back.tail(self.min_history_ticks)
        close = df['close'].values
        volume = df['volume'].values
        new_action = TradeState.none
        close_price = self.get_price(TradeState.none, look_back, self.pair)

        # ************** OBV (On Balance Volume)
        obv = talib.OBV(close, volume)[-1]
        print('obv:', obv)
        if obv >= 100.0:
            new_action = TradeState.buy
        elif obv < 100.0:
            new_action = TradeState.sell

        # ************** Calc EMA
        ema_period = 6
        ema = talib.EMA(close[-ema_period:], timeperiod=ema_period)[-1]
        if close_price <= ema:
            new_action = TradeState.sell

        if new_action == TradeState.none:
            return self.actions

        trade_price = self.get_price(new_action, df.tail(), self.pair)

        action = TradeAction(self.pair,
                             new_action,
                             amount=None,
                             rate=trade_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)
        return self.actions



