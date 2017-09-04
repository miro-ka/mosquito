from .base import Base
from core.bots.enums import TradeMode
import time


class Live(Base):
    """
    Main class for Live Trading
    """
    mode = TradeMode.live

    def __init__(self):
        super(Live, self).__init__(self.mode)
        self.counter = 0
        # open_orders = self.exchange.return_open_orders()
        # print(open_orders)

    def get_next(self, interval_in_min):
        """
        Returns next state
        Interval: Interval in minutes
        """
        interval_in_sec = interval_in_min*60
        epoch_now = int(time.time())
        if self.last_tick_epoch > 0:
            next_ticker_time = (self.last_tick_epoch + interval_in_sec)
            delay_second = epoch_now - next_ticker_time
            if delay_second < 0:
                print('Going to sleep for: ', abs(delay_second), ' seconds.')
                time.sleep(abs(delay_second))

        if not self.ticker_df.empty:
            self.ticker_df.drop(self.ticker_df.index, inplace=True)

        print('Fetching data for ' + str(len(self.pairs)) + ' ticker/tickers.', end='', flush=True)

        epoch_now = int(time.time())
        epoch_start = epoch_now - interval_in_sec*5  # just to be sure get extra 5 datasets
        epoch_end = epoch_now
        for pair in self.pairs:
            new_df = self.exchange.get_candles_df(pair, epoch_start, epoch_end, interval_in_sec)
            # df = self.exchange.get_symbol_ticker(pair, interval_in_min)
            if self.ticker_df.empty:
                self.ticker_df = new_df.copy()
            else:
                self.ticker_df = self.ticker_df.append(new_df, ignore_index=True)
            print('.', end='', flush=True)

        print('..done')
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
