from abc import ABC, abstractmethod



class Base(ABC):
    """
    Base class for all strategies
    """

    def __init__(self, args):
        super(Base, self).__init__()
        self.args = args


    @abstractmethod
    def calulate(self, interval):
        pass
