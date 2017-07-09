import sys
import configparser
from importlib import import_module
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
    buffer_size = interval = pairs = None
    ticker = look_back = history = None
    bot = report = plot = plot_pair = None
    trade_mode = root_report_currency = None

    def __init__(self, args, config_file):
        # Arguments should override config.ini file, so lets initialize
        # them only after config file parsing
        self.parse_config(config_file)
        self.args = args
        self.config = config_file
        strategy_class = self.load_strategy(args.strategy)
        self.strategy = strategy_class(args)
        self.wallet = Wallet(config_file)
        self.history = pd.DataFrame()
        trade_columns = ['date', 'pair', 'close_price', 'action']
        self.trades = pd.DataFrame(columns=trade_columns, index=None)
        if args.backtest:
            self.bot = Backtest(args, config_file)
            self.trade_mode = TradeMode.backtest
        elif args.trade:
            self.bot = Live(args, config_file)
            self.trade_mode = TradeMode.live
        elif args.paper:
            self.bot = Paper(args, config_file)
            self.trade_mode = TradeMode.paper
        self.pairs = self.bot.get_pairs()
        self.look_back = pd.DataFrame()
        self.max_lookback_size = self.buffer_size*(60/self.interval)*len(self.pairs)

    @staticmethod
    def load_strategy(strategy_name):
        mod = import_module("strategies." + strategy_name)
        strategy = getattr(mod, strategy_name.capitalize())
        return strategy

    def parse_config(self, config_file):
        """
        Parsing of config.ini file
        """
        config = configparser.ConfigParser()
        config.read(config_file)
        self.root_report_currency = config['Trade']['root_report_currency']
        self.buffer_size = config['Trade']['buffer_size']
        if self.buffer_size != '':
            self.buffer_size = int(self.buffer_size)
        self.interval = config['Trade']['interval']
        if self.interval != '':
            self.interval = int(self.interval)
        self.strategy = config['Trade']['strategy']
        self.plot_pair = config['Report']['plot_pair']

    def on_simulation_done(self):
        """
        Last function called when the simulation is finished
        """
        print('shutting down and writing final statistics!')
        # TODO: this should be done next! (miro)
        if self.args.plot:
            self.plot.draw(self.history,
                           self.trades,
                           self.plot_pair)

    def run(self):
        """
        This is the main simulation loop
        """
        if self.bot is None:
            print(colored('The bots type is NOT specified. You need to choose one action (--sim, --paper, --trade)', 'red'))
            sys.exit()

        print('starting simulation')

        # Initialization
        self.report = Report(self.wallet.initial_balance,
                             self.pairs,
                             self.root_report_currency)
        self.plot = Plot()

        try:
            while True:
                # Get next ticker set and save it to our container
                self.ticker = self.bot.get_next(self.interval)
                if self.ticker.empty:
                    print("No more data,..simulation done,. quitting")
                    exit(0)

                self.history = self.history.append(self.ticker, ignore_index=True)
                self.look_back = self.look_back.append(self.ticker, ignore_index=True)
                # print('--ticker--', self.ticker)
                buffer_size = len(self.look_back.index)
                print('buffer_size: ', buffer_size)
                if buffer_size > self.max_lookback_size:
                    print('max memory exceeded, cleaning buffer')
                    self.look_back = self.look_back.drop(self.look_back.index[[0, buffer_size - self.max_lookback_size]])

                # Get next actions
                actions = self.strategy.calculate(self.look_back, self.wallet)

                # Set trade
                self.wallet.current_balance = self.bot.trade(actions,
                                                             self.wallet.current_balance,
                                                             self.trades)

                # Write report
                self.report.calc_stats(self.ticker, self.wallet)

        except KeyboardInterrupt:
            self.on_simulation_done()

        except SystemExit:
            self.on_simulation_done()






