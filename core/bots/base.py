from abc import ABC, abstractmethod
import configparser


class Base(ABC):
    """
    Base class for all simulation types (sim, paper, trade)
    """

    def __init__(self, args, config_file):
        super(Base, self).__init__()
        self.args = args

    @staticmethod
    def initialize_config(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    @abstractmethod
    def get_next(self, interval):
        """
        Gets next data set
        :param interval:
        :return: New data in DataFrame
        """
        pass

    @abstractmethod
    def get_pairs(self):
        """
        Returns the pairs the bot is working with
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
    def get_wallet_balance(self):
        """
        Returns wallet balance
        """
        pass

    @abstractmethod
    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance
        :return:
        """
        pass
