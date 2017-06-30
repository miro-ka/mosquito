from abc import ABC, abstractmethod
from .enums import TradeState as ts


class Base(ABC):
    """
    Base class for all strategies
    """

    action_request = ts.none

    def __init__(self, args):
        super(Base, self).__init__()
        self.args = args

    @abstractmethod
    def calculate(self, interval):
        pass

