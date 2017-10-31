import configargparse
from strategies.base import Base
import core.common as common
from ai.blueprints.junior6h import Junior6h
from strategies.ai.scikitbase import ScikitBase
from core.bots.enums import BuySellMode
from strategies.enums import TradeState
from core.tradeaction import TradeAction


class Junior6h1(Base, ScikitBase):
    """
    Junior6h1 strategy
    About: Strategy using trained model from blueprint factory
    """
    arg_parser = configargparse.get_argument_parser()

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Junior6h1, self).__init__()
        self.name = 'junior6h1'
        self.min_history_ticks = 35
        self.pair = self.parse_pairs(args.pairs)[0]
        self.buy_sell_mode = BuySellMode.fixed

    def calculate(self, look_back, wallet):
        """
        Main strategy logic (the meat of the strategy)
        """
        (dataset_cnt, _) = common.get_dataset_count(look_back, self.group_by_field)

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt)
            return self.actions

        self.actions.clear()

        df = look_back.tail(self.min_history_ticks)
        df_blueprint = Junior6h.calculate_features(df)

        # Remove not-used columns
        df_blueprint = df_blueprint.drop(['pair', 'date', 'id', '_id', 'exchange', 'curr_1', 'curr_2'], axis=1)

        # Re-ordering column names
        column_names = Junior6h.get_column_names()
        Y = df_blueprint[column_names]
        predicted = self.predict(Y)[0]

        new_action = TradeState.sell if predicted == 0 else TradeState.buy
        trade_price = self.get_price(new_action, df.tail(), self.pair)

        action = TradeAction(self.pair,
                             new_action,
                             amount=None,
                             rate=trade_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)
        return self.actions



