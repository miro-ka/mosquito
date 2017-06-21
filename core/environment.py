

class Environment:
    def __init__(self):
        pass

    @abstractmethod
    def get_next(self, interval):
        print('getting next from BASE')