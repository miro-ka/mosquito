from exchanges.exchange import Exchange
import time
import configargparse


class Blueprint:
    """
    Main module for generating and handling datasets for AI
    """

    exchange = None
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--days', help='Days to start blueprint from', default=30)
    arg_parser.add('--features', help='Path to input features file', action='store_true')
    arg_parser.add('--ticker_size', help='Size of the candle ticker', default=5)
    arg_parser.add('-v', '--verbosity', help='Verbosity', action='store_true')

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        self.ticker_size = int(args.ticker_size)
        self.features = self.load_features(args.features)
        self.start_time = int(time.time()) - int(args.days)*86400
        self.exchange = Exchange(None)
        p = self.exchange.get_pairs()
        print(p)

    @staticmethod
    def load_features(features_path):
        """
        Loads features list file and returns its content
        """
        # TODO load features list
        print('loading features')
        return []

    def run(self):
        """
        Calculates and stores dataset
        """
        print('calculate')
