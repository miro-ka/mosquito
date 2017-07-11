from .base import Base
from exchanges.exchange import Exchange
from core.bots.enums import TradeMode
import pandas as pd
import time


class Paper(Base):
    """
    Main class for Paper trading
    """

    ticker_df = None

    def __init__(self, args, config_file):
        super(Paper, self).__init__(args, config_file)
        self.counter = 0
        self.ticker_df = pd.DataFrame()
        self.config = self.initialize_config(config_file)
        self.exchange = Exchange(args, config_file, TradeMode.paper)
        self.pairs = self.process_input_pairs(self.config['Trade']['pairs'])
        self.last_tick_epoch = 0

    def get_wallet_balance(self):
        """
        Returns wallet balance
        """
        return self.exchange.get_balances()

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

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        # TODO
        return wallet

    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        # TODO: update wallets balance
        return wallet
