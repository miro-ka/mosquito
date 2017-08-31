import sys
import configargparse
import core.common as common
import pandas as pd
from core.bots.paper import Paper
from termcolor import colored
from core.bots.backtest import Backtest
from core.bots.enums import TradeMode
from core.bots.live import Live
from core.plot import Plot
from core.report import Report
from core.wallet import Wallet


class Engine:
    """
    Main class for Simulation Engine (main class where all is happening
    """

    arg_parser = configargparse.get_argument_parser()
    arg_parser.add("--strategy", help="Name of strategy to be run (if not set, the default one will be used")
    arg_parser.add("--plot", help="Generate a candle stick plot at simulation end", action='store_true')
    arg_parser.add("--interval", help="Simulation interval", default=5)
    arg_parser.add("--root_report_currency", help="Root currency used in final plot")
    arg_parser.add("--buffer_size", help="Buffer size", default=24)
    arg_parser.add("--prefetch", help="Prefetch data from history DB",  action='store_true')
    arg_parser.add("--plot_pair", help="Plot pair")
    arg_parser.add("--all", help="Include all currencies/tickers")
    arg_parser.add("--days", help="Days to pre-fill")

    buffer_size = None
    interval = None
    pairs = None
    verbosity = None
    ticker = None
    look_back = None
    history = None
    bot = None
    report = None
    plot = None
    plot_pair = None
    trade_mode = None
    root_report_currency = None
    config_strategy_name = None
    actions = None
    prefetch = None
    first_ticker = None
    last_valid_ticker = None

    def __init__(self):
        self.args = self.arg_parser.parse_known_args()[0]
        self.parse_config()
        strategy_class = common.load_module('strategies.', self.args.strategy)
        self.wallet = Wallet()
        self.history = pd.DataFrame()
        trade_columns = ['date', 'pair', 'close_price', 'action']
        self.trades = pd.DataFrame(columns=trade_columns, index=None)
        if self.args.backtest:
            self.bot = Backtest(self.wallet.initial_balance.copy())
            self.trade_mode = TradeMode.backtest
        elif self.args.paper:
            self.bot = Paper(self.wallet.initial_balance.copy())
            self.trade_mode = TradeMode.paper
            self.wallet.initial_balance = self.bot.get_balance()
            self.wallet.current_balance = self.bot.get_balance()
        elif self.args.live:
            self.bot = Live()
            self.trade_mode = TradeMode.live
            self.wallet.initial_balance = self.bot.get_balance()
            self.wallet.current_balance = self.bot.get_balance()
        self.strategy = strategy_class()
        self.pairs = self.bot.get_pairs()
        self.look_back = pd.DataFrame()
        self.max_lookback_size = int(self.buffer_size*(60/self.interval)*len(self.pairs))
        self.initialize()

    def initialize(self):
        # Initialization
        self.report = Report(self.wallet.initial_balance,
                             self.pairs,
                             self.root_report_currency,
                             self.bot.get_pair_delimiter())
        self.report.set_verbosity(self.verbosity)
        self.plot = Plot()

    def parse_config(self):
        """
        Parsing of config.ini file
        """
        self.root_report_currency = self.args.root_report_currency
        self.buffer_size = self.args.buffer_size
        self.prefetch = self.args.prefetch
        if self.buffer_size != '':
            self.buffer_size = int(self.buffer_size)
        self.interval = self.args.interval
        if self.interval != '':
            self.interval = int(self.interval)
        self.config_strategy_name = self.args.strategy
        self.plot_pair = self.args.plot_pair
        self.verbosity = self.args.verbosity

    def on_simulation_done(self):
        """
        Last function called when the simulation is finished
        """
        print('shutting down and writing final statistics!')
        strategy_info = self.report.write_final_stats(self.first_ticker,
                                                      self.last_valid_ticker,
                                                      self.wallet, self.trades)
        if self.args.plot:
            plot_title = ['Simulation: ' + str(self.trade_mode) + ' Strategy: ' + self.config_strategy_name + ', Pair: '
                          + str(self.pairs)]
            strategy_info = plot_title + strategy_info
            self.plot.draw(self.history,
                           self.trades,
                           self.plot_pair,
                           strategy_info)

    @staticmethod
    def validate_ticker(df):
        """
        Validates if the given dataframe contains mandatory fields
        """
        columns_to_check = ['close', 'volume']
        df_column_names = list(df)
        if not set(columns_to_check).issubset(df_column_names):
            return False
        nan_columns = df.columns[df.isnull().any()].tolist()
        nans = [i for i in nan_columns if i in columns_to_check]
        if len(nans) > 0:
            return False
        return True

    def run(self):
        """
        This is the main simulation loop
        """
        if self.bot is None:
            print(colored('The bots type is NOT specified. You need to choose one action (--sim, --paper, --trade)', 'red'))
            sys.exit()

        print(colored('Starting simulation: ' + str(self.trade_mode) + ', Strategy: ' + self.config_strategy_name, 'yellow'))

        # Prefetch Buffer Data (if enabled in config)
        if self.prefetch:
            self.history = self.bot.prefetch(self.strategy.get_min_history_ticks(), self.interval)
            self.look_back = self.history.copy()

        try:
            while True:
                # Get next ticker
                self.ticker = self.bot.get_next(self.interval)
                if self.ticker.empty:
                    print("No more data,..simulation done,. quitting")
                    exit(0)

                # Check if ticker is valid
                if not self.validate_ticker(self.ticker):
                    print(colored('Received invalid ticker, will have to skip it! Details:\n' + str(self.ticker), 'red'))
                    continue

                # Save ticker to buffer
                self.history = self.history.append(self.ticker, ignore_index=True)
                self.look_back = self.look_back.append(self.ticker, ignore_index=True)

                # Check if buffer is not overflown
                self.look_back = common.handle_buffer_limits(self.look_back, self.max_lookback_size)

                if self.first_ticker is None:
                    self.first_ticker = self.ticker
                self.last_valid_ticker = self.ticker

                # Get next actions
                self.actions = self.strategy.calculate(self.look_back, self.wallet)

                # Set trade
                self.actions = self.bot.trade(self.actions,
                                              self.wallet.current_balance,
                                              self.trades)

                # Get wallet balance
                self.wallet.current_balance = self.bot.get_balance()

                # Write report
                self.report.calc_stats(self.ticker, self.wallet)

        except KeyboardInterrupt:
            self.on_simulation_done()

        except SystemExit:
            self.on_simulation_done()






