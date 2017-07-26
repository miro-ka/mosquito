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

    def __init__(self, args, config_file):
        # Arguments should override config.ini file, so lets initialize
        # them only after config file parsing
        self.parse_config(config_file)
        self.args = args
        self.config = config_file
        strategy_class = self.load_strategy(args.strategy, self.config_strategy_name)
        self.strategy = strategy_class(args)
        self.wallet = Wallet(config_file)
        self.history = pd.DataFrame()
        trade_columns = ['date', 'pair', 'close_price', 'action']
        self.trades = pd.DataFrame(columns=trade_columns, index=None)
        if args.backtest:
            self.bot = Backtest(args, config_file)
            self.trade_mode = TradeMode.backtest
        elif args.paper:
            self.bot = Paper(args, config_file)
            self.trade_mode = TradeMode.paper
            self.wallet.initial_balance = self.bot.get_balance()
            self.wallet.current_balance = self.bot.get_balance()
        elif args.live:
            self.bot = Live(args, config_file)
            self.trade_mode = TradeMode.live
            self.wallet.initial_balance = self.bot.get_balance()
            self.wallet.current_balance = self.bot.get_balance()
        self.pairs = self.bot.get_pairs()
        self.look_back = pd.DataFrame()
        self.max_lookback_size = int(self.buffer_size*(60/self.interval)*len(self.pairs))

    @staticmethod
    def load_strategy(arg_strategy, config_strategy):
        """
        Loads strategy module based on given name.
        """
        if arg_strategy is None and config_strategy == '':
            print(colored('Not provided strategy,. please add it as an argument or in config file', 'red'))
            sys.exit()
        if arg_strategy is not None:
            strategy_name = arg_strategy
        else:
            strategy_name = config_strategy
        mod = import_module("strategies." + strategy_name)
        strategy_class = getattr(mod, strategy_name.capitalize())
        return strategy_class

    def parse_config(self, config_file):
        """
        Parsing of config.ini file
        """
        config = configparser.ConfigParser()
        config.read(config_file)
        self.root_report_currency = config['Trade']['root_report_currency']
        self.buffer_size = config['Trade']['buffer_size']
        self.prefetch = config.getboolean('Trade', 'prefetch')
        if self.buffer_size != '':
            self.buffer_size = int(self.buffer_size)
        self.interval = config['Trade']['interval']
        if self.interval != '':
            self.interval = int(self.interval)
        self.config_strategy_name = config['Trade']['strategy']
        self.plot_pair = config['Report']['plot_pair']
        self.verbosity = int(config['General']['verbosity'])

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

        print('Starting simulation..')
        # Initialization
        self.report = Report(self.wallet.initial_balance,
                             self.pairs,
                             self.root_report_currency)
        self.report.set_verbosity(self.verbosity)
        self.plot = Plot()

        # Prefetch Buffer Data (if
        if self.prefetch:
            self.history = self.bot.prefetch(self.strategy.get_min_history_ticks(), self.interval)
            self.look_back = self.history.copy()

        try:
            while True:
                # Get next ticker set and save it to our container
                self.ticker = self.bot.get_next(self.interval)
                if self.ticker.empty:
                    print("No more data,..simulation done,. quitting")
                    exit(0)

                # Save ticker to buffer
                self.history = self.history.append(self.ticker, ignore_index=True)
                self.look_back = self.look_back.append(self.ticker, ignore_index=True)
                buffer_size = len(self.look_back.index)
                if buffer_size > self.max_lookback_size:
                    print('max memory exceeded, cleaning/cutting buffer')
                    rows_to_delete = buffer_size - self.max_lookback_size
                    self.look_back = self.look_back.ix[rows_to_delete:]
                    self.look_back = self.look_back.reset_index(drop=True)

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






