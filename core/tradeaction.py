
class TradeAction:
    """
    Trade Action class
    """

    def __init__(self, pair, action, amount, rate, buy_sell_all=False):
        """
        :param pair:
        :param action:
        :param amount:
        :param rate:
        :param buy_sell_all: if True, it will sell/buy all assets. Value parameters is ignored
        """
        self.pair = pair
        self.action = action
        self.amount = amount
        self.rate = rate
        self.buy_sell_all = buy_sell_all

