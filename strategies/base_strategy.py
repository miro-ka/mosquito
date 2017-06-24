from abc import ABC, abstractmethod


'''
Base class for all strategies
'''


class Base_Strategy(ABC):
    def __init__(self, args):
        super(Base_Strategy, self).__init__()
        self.args = args


    @abstractmethod
    def calulate(self, interval):
        pass
