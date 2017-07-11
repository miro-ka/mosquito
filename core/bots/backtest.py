from .base import Base
import time
from core.bots.enums import TradeMode
from exchanges.exchange import Exchange


DAY = 3600


class Backtest(Base):
    """
    Main class for Backtest trading
    """
    previous_action = None
    mode = TradeMode.backtest

    def __init__(self, args, config_file):
        super(Backtest, self).__init__(args, config_file)
        self.counter = 0
        self.config = self.initialize_config(config_file)
        self.transaction_fee = float(self.config['Trade']['transaction_fee'])
        self.sim_start = self.config['Backtest']['from']
        self.sim_end = self.config['Backtest']['to']
        self.sim_hours = int(self.config['Backtest']['hours'])
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_hours, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.exchange = Exchange(args, config_file, TradeMode.backtest)
        self.pairs = self.process_input_pairs(self.config['Trade']['pairs'])

    def get_wallet_balance(self):
        """
        Returns wallet balance
        """
        pass

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

    @staticmethod
    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance. In back testing, the wallet is updated in trade
         method, so there is nothing extra needed here.
        """
        # TODO: update wallets balance
        print('refreshing wallet')
        return wallet
