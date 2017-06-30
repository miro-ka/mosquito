from .base import Base


class Live(Base):
    """
    Main class for Live Trading
    """

    def __init__(self, args):
        super(Live, self).__init__(args)
        self.counter = 0

    def get_next(self, interval):
        """
        Returns next state
        """
        print('getting next ticker from Trade')

    def trade(self, actions, wallet):
        # TODO
        pass

    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        # TODO: update wallets balance
        return wallet
