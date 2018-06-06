import configargparse
from strategies.base import Base
import core.common as common
from ai.blueprints.junior import Junior as Model
from strategies.ai.scikitbase import ScikitBase
from core.bots.enums import BuySellMode
from strategies.enums import TradeState
from core.tradeaction import TradeAction


class Junior(Base, ScikitBase):
    """
    Junior strategy
    About: Strategy using trained model from Junior blueprint factory
    """
    arg_parser = configargparse.get_argument_parser()

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Junior, self).__init__()
        self.name = 'junior'
        self.min_history_ticks = 35
        self.pair = self.parse_pairs(args.pairs)[0]
        self.buy_sell_mode = BuySellMode.all
        self.feature_names = ['open', 'quoteVolume', 'close', 'low', 'high', 'volume', 'weightedAverage', 'ema2', 'ema4', 'ema8', 'ema12', 'ema16', 'ema20', 'rsi5', 'rsi_above_505', 'cci5', 'macd_above_signal34', 'macd_above_zero34', 'obv2', 'obv4', 'obv8', 'obv12', 'obv16', 'obv20']

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
        df_blueprint = Model.calculate_features(df)

        # Remove not-used columns
        df_blueprint = df_blueprint.drop(['pair', 'date', 'id', '_id', 'exchange', 'curr_1', 'curr_2'], axis=1)

        # Re-ordering column names
        column_names = self.feature_names
        x = df_blueprint[column_names]
        predicted = self.predict(x)[0]

        new_action = TradeState.sell if predicted == 1 else TradeState.buy
        trade_price = self.get_price(new_action, df.tail(), self.pair)

        action = TradeAction(self.pair,
                             new_action,
                             amount=None,
                             rate=trade_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)
        return self.actions



