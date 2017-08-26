from enum import Enum


class TradeMode(Enum):
    """
    Enum class for holding all available trade modes
    """
    backtest = 0
    paper = 1
    live = 2


class BuySellMode(Enum):
    """
    Enum class holding buy/sell mode the bot should use
    """
    all = 0          # Only 1 currency will be used for trading
    fixed = 1        # Currencies will be bought only for given amount
    user_defined = 2  # Buy/sell amount is specified by the user
