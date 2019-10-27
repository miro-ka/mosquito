import configargparse
import pandas as pd
from strategies.base import Base
import core.common as common
from ai.blueprints.luckyantelope import Luckyantelope as Model
from strategies.ai.scikitbase import ScikitBase
from core.bots.enums import BuySellMode
from strategies.enums import TradeState
from core.tradeaction import TradeAction


class Luckyantelope(Base, ScikitBase):
    """
    Luckyantelope strategy
    About: Strategy using trained model from Luckyantelope blueprint factory
    """
    arg_parser = configargparse.get_argument_parser()
    trade_history = pd.DataFrame(columns=['close', 'predicted'])

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Luckyantelope, self).__init__()
        self.name = 'luckyantelope'
        self.min_history_ticks = 21
        self.pair = self.parse_pairs(args.pairs)[0]
        self.buy_sell_mode = BuySellMode.fixed

    def calculate(self, look_back, wallet):
        """
        Main strategy logic (the meat of the strategy)
        """
        (dataset_cnt, _) = common.get_dataset_count(look_back, self.group_by_field)

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt, ',..waiting for more data..')
            return self.actions

        self.actions.clear()

        df = look_back.tail(self.min_history_ticks)
        df_blueprint = Model.calculate_features(df)

        # Remove not-used columns
        df_blueprint = df_blueprint[self.feature_names]

        # Re-ordering column names
        column_names = self.feature_names
        x = df_blueprint[column_names]
        price_now = x.close.iloc[0]
        price_predicted = self.predict(x)

        if price_predicted is None:
            return self.actions
        else:
            price_predicted = price_predicted[0]

        if price_predicted > 0.08 or price_predicted < 0.05:
            return self.actions

        price_change = ((price_predicted * 100) / price_now) - 100

        if price_change > 10:
            return self.actions

        self.trade_history = self.trade_history.append({'close': price_now,
                                                        'predicted': price_predicted}, ignore_index=True)
        self.trade_history.to_csv('out/luckyantelope_out.csv', index=False)

        print('price_change:' + str(price_change) + ', close_price: ' + str(x.close.iloc[0]) + ', predicted: ' + str(price_predicted))

        new_action = TradeState.buy if price_predicted > price_now else TradeState.sell
        trade_price = self.get_price(new_action, df.tail(), self.pair)

        action = TradeAction(self.pair,
                             new_action,
                             amount=None,
                             rate=trade_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)
        return self.actions



