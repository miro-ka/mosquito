from enum import Enum


class TradeState(Enum):
    """
    Enum class for holding all available trade states
    """
    none = 0
    buy = 1
    buying = 2
    bought = 3
    sell = 4
    selling = 5
    sold = 6
