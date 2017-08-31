

class Minimal:
    """
    Minimal blueprint - example of implementation blueprint logic
    """

    def __init__(self):
        print('minimal init')

    @staticmethod
    def scan(df):
        """
        Function that tries to generate a blueprint from given dataset
        """
        print('scanning for features,..from total rows:' + str(len(df.index)))
        return None

