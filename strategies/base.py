from abc import ABC, abstractmethod
from .enums import TradeState as ts
from strategies.enums import TradeState
from termcolor import colored


class Base(ABC):
    """
    Base class for all strategies
    """

    action_request = ts.none
    actions = []

    def __init__(self, verbosity=2, pair_delimiter='_'):
        super(Base, self).__init__()
        self.pair_delimiter = pair_delimiter
        self.verbosity = verbosity
        self.min_history_ticks = 5
        self.group_by_field = 'pair'

    def get_min_history_ticks(self):
        """
        Returns min_history_ticks
        """
        return self.min_history_ticks

    @staticmethod
    def get_dataset_count(df, group_by_field):
        """
        Returns count of dataset and pairs_count (group by provided string)
        """
        pairs_group = df.groupby([group_by_field])
        # cnt = pairs_group.count()
        pairs_count = len(pairs_group.groups.keys())
        dataset_cnt = pairs_group.size().iloc[0]
        return dataset_cnt, pairs_count

    @abstractmethod
    def calculate(self, data, wallet):
        pass

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
