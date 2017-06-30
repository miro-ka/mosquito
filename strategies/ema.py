from .base import Base
from .enums import TradeState as ts
from .tradeaction import TradeAction


class Ema(Base):
    """
    ema strategy
    """

    actions = []

    def __init__(self, args):
        super(Ema, self).__init__(args)
        self.name = 'ema'

    def calculate(self, look_back):
        """
        Returns list of pairs and their corresponding actions
        """
        print('running strategy ema')
        action = TradeAction('ETH', ts.buy, None, True)
        self.actions.append(action)
        return self.actions



