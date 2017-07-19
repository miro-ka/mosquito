from .base import Base
import time
from core.bots.enums import TradeMode
from exchanges.exchange import Exchange


DAY = 3600


class Backtest(Base):
    """
    Main class for Backtest trading
    """
    mode = TradeMode.backtest

    def __init__(self, args, config_file):
        super(Backtest, self).__init__(args, config_file)
        self.counter = 0
        self.sim_start = self.config['Backtest']['from']
        self.sim_end = self.config['Backtest']['to']
        self.sim_hours = int(self.config['Backtest']['hours'])
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_hours, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.exchange = Exchange(args, config_file, TradeMode.backtest)

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
        self.ticker_df = self.exchange.get_offline_ticker(self.current_epoch, self.pairs)
        self.current_epoch += interval*60
        return self.ticker_df

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        return super(Backtest, self).trade(actions, wallet, trades)

