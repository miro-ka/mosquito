from strategies.enums import TradeState
from core.bots.enums import BuySellMode


class TradeAction:
    """
    Trade Action class
    """

    def __init__(self, pair,
                 action=TradeState.none,
                 amount=0.0,
                 rate=0.0,
                 buy_sell_mode=BuySellMode.all):
        """
        Definition of Trace Action
        """

        self.pair = pair
        self.action = action
        self.amount = amount
        self.rate = rate
        self.buy_sell_mode = buy_sell_mode
        self.order_number = None

