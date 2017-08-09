from abc import ABC, abstractmethod


class Base(ABC):
    """
    Base class for all exchanges
    """

    transaction_fee = 0.0

    def __init__(self):
        super(Base, self).__init__()
        self.pair_connect_string = '_'

    @abstractmethod
    def return_open_orders(self, currency_pair='all'):
        """
        Returns your open orders
        """
        pass

    def get_transaction_fee(self):
        """
        Returns exchanges transaction fee
        """
        return self.transaction_fee

    @abstractmethod
    def cancel_order(self, order_number):
        """
        Cancels order for given order number
        """
        pass

    @classmethod
    def trade(cls, actions, wallet, trade_mode):
        """
        Apply given actions and returns updated wallet - Base class only simulates buy/sell.
        For exchange the buy/sel logic should be implemented here
        """

        for action in actions:
            print('applying action:', action.action, ', for pair: ', action.pair)
            # TODO: check if we already don't have the same action in process

            # In simulation we are just buying straight currency
        return wallet
