from abc import ABC, abstractmethod


class Base(ABC):
    """
    Base class for all simulation types (sim, paper, trade)
    """

    def __init__(self, args, config_file):
        super(Base, self).__init__()
        self.args = args

    @abstractmethod
    def get_next(self, interval):
        """
        Gets next data set
        :param interval:
        :return: New data in DataFrame
        """
        pass

    @abstractmethod
    def trade(self, actions, wallet):
        """
        Places given action
        :param actions:
        :return:
        """
        pass

    @abstractmethod
    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        pass
