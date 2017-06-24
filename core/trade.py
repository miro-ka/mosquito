from .bot import Bot


class Trade(Bot):
    """
    Main class for Live Trading
    """

    def __init__(self, args):
        super(Trade, self).__init__(args)
        self.counter = 0


    def get_next(self, interval):
        """
        Returns next state
        """
        print('getting next ticker from Trade')
