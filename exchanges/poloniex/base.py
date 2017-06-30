from abc import ABC


class Base(ABC):
    """
    Base class for all exchanges
    """

    def __init__(self):
        super(Base, self).__init__()
        pass

    @staticmethod
    def trade(actions, wallet):
        """
        Apply given actions and returns updated wallet - Base class only simulates buy/sell.
        For exchange the buy/sel logic should be implemented here
        """

        for action in actions:
            print('applying action:', action.action, ', for pair: ', action.pair)
            # TODO: check if we already don't have the same action in process

            # In simulation we are just buying straight currency
        return wallet
