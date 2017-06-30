from .base import Base


class Paper(Base):
    """
    Main class for Paper trading
    """

    def __init__(self, args):
        super(Paper, self).__init__(args)
        self.counter = 0

    def get_next(self, interval):
        """
        Returns next state
        """
        print('getting next ticker from Paper')

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

