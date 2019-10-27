import talib
import configargparse
from .base import Base
import core.common as common
from .enums import TradeState
from core.bots.enums import BuySellMode
from core.tradeaction import TradeAction
from lib.indicators.stoploss import StopLoss


class Macd(Base):
    """
    Ema strategy
    About: Buy when close_price > ema20, sell when close_price < ema20 and below death_cross
    """
    arg_parser = configargparse.get_argument_parser()

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Macd, self).__init__()
        self.name = 'macd'
        self.min_history_ticks = 51
        self.pair = self.parse_pairs(args.pairs)[0]
        self.buy_sell_mode = BuySellMode.all
        self.stop_loss = StopLoss(int(args.ticker_size))
        self.buy_triggers = 0

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
        close = df['close'].values

        last_row = df.tail(1).copy()

        # ************** Calc SMA-50
        sma = df['close'].rolling(window=50).mean().values[-1]
        print('sma-50:', sma)

        # ************** Calc EMA-30
        ema_period = 30
        ema = df['close'].ewm(span=ema_period, adjust=False).mean().values[-1]
        print('ema-30:', ema)

        ema_above_sma = ema > sma
        print('ema_above_sma: ', ema_above_sma)

        if ema_above_sma:
            # self.buy_triggers += 1
            # if self.buy_triggers >= 5:
            new_action = TradeState.buy
        else:
            new_action = TradeState.sell
            self.buy_triggers = 0

        trade_price = self.get_price(new_action, df.tail(), self.pair)

        """
        # Get stop-loss
        if new_action == TradeState.buy and self.stop_loss.calculate(close):
            print('stop-loss detected,..selling')
            new_action = TradeState.sell
        """

        action = TradeAction(self.pair,
                             new_action,
                             amount=None,
                             rate=trade_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)

        return self.actions



