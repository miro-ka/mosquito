import configargparse
import pandas as pd
import pandas_ta as ta
from .base import Base
import core.common as common
from .enums import TradeState
from core.bots.enums import BuySellMode
from core.tradeaction import TradeAction
from lib.indicators.stoploss import StopLoss


class Ema(Base):
    """
    Ema strategy
    About: Buy when close_price > ema20, sell when close_price < ema20 and below death_cross
    """
    arg_parser = configargparse.get_argument_parser()

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Ema, self).__init__()
        self.name = 'ema'
        self.min_history_ticks = 30
        self.pair = self.parse_pairs(args.pairs)[0]
        self.buy_sell_mode = BuySellMode.all
        self.stop_loss = StopLoss(int(args.ticker_size))

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
        new_action = TradeState.none

        # Calculate indicators
        df = look_back.tail(self.min_history_ticks)
        close = df['close']

        # ************** Calc EMA
        ema5 = ta.ema(close, length=5).values[-1]
        ema10 = ta.ema(close, length=10).values[-1]
        ema20 = ta.ema(close, length=20).values[-1]

        close_price = self.get_price(TradeState.none, df.tail(), self.pair)

        print('close_price:', close_price, 'ema:', ema20)
        if close_price < ema10 or close_price < ema20:
            new_action = TradeState.sell
        elif close_price > ema5 and close_price > ema10:
            new_action = TradeState.buy

        trade_price = self.get_price(new_action, df.tail(), self.pair)

        # Get stop-loss
        if new_action == TradeState.buy and self.stop_loss.calculate(close.values):
            print('stop-loss detected,..selling')
            new_action = TradeState.sell

        action = TradeAction(self.pair,
                             new_action,
                             amount=None,
                             rate=trade_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)
        return self.actions



