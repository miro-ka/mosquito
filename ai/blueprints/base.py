from abc import ABC, abstractmethod
from termcolor import colored


class Base(ABC):
    """
    Base class for all simulation types (sim, paper, trade)
    """
    feature_names = []
    scans_container = []

    def __init__(self):
        super(Base, self).__init__()

    def get_feature_names(self):
        """
        Returns feature names
        """
        if len(self.scans_container) == 0:
            print(colored('Not enough data to get features name!', 'red'))
            return []
        df = self.scans_container[0][2]
        columns = df.columns.values.tolist()
        return columns
