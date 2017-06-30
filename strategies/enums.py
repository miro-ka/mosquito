from enum import Enum


class TradeState(Enum):
    """
    Enum class for holding all available trade states
    """
    none = 0
    buy = 1
    buying = 2
    sell = 3
    selling = 4
