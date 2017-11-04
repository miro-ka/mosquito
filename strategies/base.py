import configargparse
from termcolor import colored
from abc import ABC, abstractmethod
from .enums import TradeState as ts
from strategies.enums import TradeState


class Base(ABC):
    """
    Base class for all strategies
    """
    arg_parser = configargparse.get_argument_parser()
    action_request = ts.none
    actions = []

    def __init__(self):
        super(Base, self).__init__()
        args = self.arg_parser.parse_known_args()[0]
        self.verbosity = args.verbosity
        self.min_history_ticks = 5
        self.group_by_field = 'pair'

    def get_min_history_ticks(self):
        """
        Returns min_history_ticks
        """
        return self.min_history_ticks

    @staticmethod
    def get_delimiter(df):
        if df.empty:
            print('Error: get_delimiter! Got empty df!')
        pair = df.iloc[-1].pair
        return '_' if '_' in pair else '-'

    @staticmethod
    def parse_pairs(pairs):
        return [x.strip() for x in pairs.split(',')]

    @abstractmethod
    def calculate(self, look_back, wallet):
        """
        Main Strategy function, which takes recent history data and returns recommended list of actions
        """
        None

    @staticmethod
    def get_price(trade_action, df, pair):
        """
        Returns price based on on the given action and dataset.
        """

        if df.empty:
            print(colored('get_price: got empty dataframe (pair): ' + pair + ', skipping!', 'red'))
            return 0.0

        pair_df = df.loc[df['pair'] == pair].sort_values('date')
        if pair_df.empty:
            print(colored('get_price: got empty dataframe for pair: ' + pair + ', skipping!', 'red'))
            return 0.0

        pair_df = pair_df.iloc[-1]
        close_price = float(pair_df.get('close'))
        price = None

        if trade_action == TradeState.buy:
            if 'lowestAsk' in pair_df:
                price = float(pair_df.get('lowestAsk'))
        elif trade_action == TradeState.sell:
            if 'highestBid' in pair_df:
                price = float(pair_df.get('highestBid'))

        # Check if we don't have nan
        if not price or price != price:
            if close_price != close_price:
                print(colored('got Nan price for pair: ' + pair + '. Dataframe: ' + str(pair_df), 'red'))
                return 0.0
            else:
                return close_price

        return price
