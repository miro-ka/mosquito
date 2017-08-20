from abc import ABC, abstractmethod
from .enums import TradeState as ts
import pandas as pd
from strategies.enums import TradeState


class Base(ABC):
    """
    Base class for all strategies
    """

    action_request = ts.none
    actions = []

    def __init__(self, args, verbosity=2, pair_delimiter='_'):
        super(Base, self).__init__()
        self.pair_delimiter = pair_delimiter
        self.verbosity = verbosity
        self.args = args
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
        pair_df = df.loc[df['pair'] == pair].sort_values('date').iloc[-1]

        if trade_action == TradeState.buy:
            if 'lowestAsk' in pair_df:
                return pair_df.get('lowestAsk')
            else:
                return pair_df.get('close')
        elif trade_action == TradeState.sell:
            if 'highestBid' in pair_df:
                return pair_df.get('highestBid')
            else:
                return pair_df.get('close')
