from .base import Base
import time
import pandas as pd
from core.bots.enums import TradeMode
import configargparse


DAY = 3600


class Backtest(Base):
    """
    Main class for Backtest trading
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--backtest_from', help='Backtest epoch start datetime')
    arg_parser.add("--backtest_to", help='Backtest epoch end datetime')
    arg_parser.add("--backtest_hours", help='Number of history days the simulation should start from')

    mode = TradeMode.backtest
    sim_start = None
    sim_end = None
    sim_hours = None

    def __init__(self, wallet):
        args = self.arg_parser.parse_known_args()[0]
        super(Backtest, self).__init__(self.mode)
        self.counter = 0
        if args.backtest_from:
            self.sim_start = int(args.backtest_from)
        if args.backtest_to:
            self.sim_end = int(args.backtest_to)
        if args.backtest_hours:
            self.sim_hours = int(args.backtest_hours)
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_hours, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.balance = wallet

    @staticmethod
    def get_sim_epoch_start(sim_hours, sim_start):
        if sim_start:
            return sim_start
        elif sim_hours:
            epoch_now = int(time.time())
            return epoch_now - (DAY*sim_hours)

    def get_next(self, interval):
        """
        Returns next state of current_time + interval (in minutes)
        """
        if self.sim_end and self.current_epoch > self.sim_end:
            return pd.DataFrame()
        self.ticker_df = self.exchange.get_offline_ticker(self.current_epoch, self.pairs)
        self.current_epoch += interval*60
        return self.ticker_df

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        return super(Backtest, self).trade(actions, wallet, trades, force_sell=False)

