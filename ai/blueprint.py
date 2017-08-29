from exchanges.exchange import Exchange
import time


class Blueprint:
    """
    Main module for generating and handling datasets for AI
    """

    exchange = None

    def __init__(self, cfg):
        """
        self.ticker_size = cfg.ticker_size
        self.features = cfg.load_features(features)
        self.start_time = int(time.time()) - days*86400
        self.exchange = Exchange(None, 'config.ini')
        """
        pass

    @staticmethod
    def load_features(features_path):
        """
        Loads features list file and returns its content
        """
        # TODO load features list
        return []

    def run(self):
        """
        Calculates and stores dataset
        """
        print('calculate')
