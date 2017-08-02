from strategies.enums import TradeState


class TradeAction:
    """
    Trade Action class
    """

    def __init__(self, pair,
                 action=TradeState.none,
                 amount=0.0,
                 rate=0.0,
                 buy_sell_all=False):
        """
        :param buy_sell_all: if True, it will sell/buy all assets. Value parameters is ignored
        """
        self.pair = pair
        self.action = action
        self.amount = amount
        self.rate = rate
        self.buy_sell_all = buy_sell_all
        self.order_number = None

