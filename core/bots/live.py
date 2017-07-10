from .base import Base
from exchanges.exchange import Exchange
from core.bots.enums import TradeMode

class Live(Base):
    """
    Main class for Live Trading
    """

    def __init__(self, args, config_file):
        super(Live, self).__init__(args, config_file)
        self.counter = 0
        self.exchange = Exchange(args, config_file, TradeMode.live)

    def get_next(self, interval):
        """
        Returns next state
        """
        print('getting next ticker from Trade')

    def get_wallet_balance(self):
        """
        Returns wallet balance
        """
        return self.exchange.get_balances()

    def trade(self, actions, wallet):
        # TODO
        pass

    def get_pairs(self):
        """
        Returns the pairs the bot is working with
        """
        pass

    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        # TODO: update wallets balance
        return wallet
