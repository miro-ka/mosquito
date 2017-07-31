from .base import Base
from core.bots.enums import TradeMode
import time


class Live(Base):
    """
    Main class for Live Trading
    """

    mode = TradeMode.live

    def __init__(self, args, config_file):
        super(Live, self).__init__(args, config_file, TradeMode.live)
        self.counter = 0
        # open_orders = self.exchange.return_open_orders()
        # print(open_orders)

    def get_next(self, interval):
        """
        Returns next state
        Interval: Interval in minutes
        """
        epoch_now = int(time.time())
        if self.last_tick_epoch > 0:
            next_ticker_time = (self.last_tick_epoch + interval * 60)
            delay_second = epoch_now - next_ticker_time
            if delay_second < 0:
                print('going to sleep for: ', abs(delay_second), ' seconds.')
                time.sleep(abs(delay_second))

        if not self.ticker_df.empty:
            self.ticker_df.drop(self.ticker_df.index, inplace=True)

        epoch_now = int(time.time())
        for pair in self.pairs:
            df = self.exchange.get_symbol_ticker(pair)
            if self.ticker_df.empty:
                self.ticker_df = df.copy()
            else:
                self.ticker_df = self.ticker_df.append(df, ignore_index=True)

        self.last_tick_epoch = epoch_now
        return self.ticker_df

    def get_balance(self):
        """
        Returns wallet balance
        """
        return self.exchange.get_balances()

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        # TODO: we need to deal with trades-buffer (trades)
        return self.exchange.trade(actions, wallet, TradeMode.live)
