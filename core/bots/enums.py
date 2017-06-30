from enum import Enum


class TradeMode(Enum):
    """
    Enum class for holding all available trade modes
    """
    backtest = 0
    paper = 1
    live = 2
