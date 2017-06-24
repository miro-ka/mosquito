from .bot import Bot


class Paper(Bot):
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
