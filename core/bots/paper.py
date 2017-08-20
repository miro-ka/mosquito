from .base import Base
from core.bots.enums import TradeMode
import time
import configparser


class Paper(Base):
    """
    Main class for Paper trading
    """

    mode = TradeMode.paper
    ticker_df = None

    def __init__(self, args, config_file, wallet):
        super(Paper, self).__init__(args, config_file, self.mode)
        config = configparser.ConfigParser()
        config.read(config_file)
        self.use_real_wallet = config.getboolean('Paper', 'use_real_wallet')
        if not self.use_real_wallet:
            self.balance = wallet.copy()

    def get_next(self, interval):
        """
        Returns next state
        Interval: Interval in minutes
        """
        epoch_now = int(time.time())
        if self.last_tick_epoch > 0:
            next_ticker_time = (self.last_tick_epoch + interval*60)
            delay_second = epoch_now - next_ticker_time
            if delay_second < 0:
                print('Going to sleep for: ', abs(delay_second), ' seconds.')
                time.sleep(abs(delay_second))

        if not self.ticker_df.empty:
            self.ticker_df.drop(self.ticker_df.index, inplace=True)

        epoch_now = int(time.time())
        for pair in self.pairs:
            df = self.exchange.get_symbol_ticker(pair, interval)
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
        if self.use_real_wallet:
            return self.exchange.get_balances()
        else:
            return self.balance.copy()

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        return super(Paper, self).trade(actions, wallet, trades, force_sell=True)
