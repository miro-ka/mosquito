import configparser
import sys
from termcolor import colored
from .backtest import Backtest
from .paper import Paper
from .trade import Trade
from .wallet import Wallet
from .report import Report
from .plot import Plot
from importlib import import_module
import pandas as pd


class Engine:
    """
    Main class for Simulation Engine (main class where all is happening
    """
    buffer_size = interval = pairs = None
    ticker = look_back = history = None
    bot = report = plot = None

    def __init__(self, args, config_file):
        self.parse_config(config_file)
        # Arguments should override config.ini file, so lets initialize
        # them only after config file parsing
        self.args = args
        self.config = config_file
        strategy_class = self.load_strategy(args.strategy)
        self.strategy = strategy_class(args)
        self.wallet = Wallet(config_file)
        self.look_back = pd.DataFrame()
        self.history = pd.DataFrame()
        if args.backtest:
            self.bot = Backtest(args, config_file)
        elif args.trade:
            self.bot = Trade(args, config_file)
        elif args.paper:
            self.bot = Paper(args, config_file)

    @staticmethod
    def load_strategy(strategy_name):
        mod = import_module("strategies." + strategy_name)
        strategy = getattr(mod, strategy_name.capitalize())
        return strategy

    def parse_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.buffer_size = config['Trade']['buffer_size']
        if self.buffer_size != '':
            self.buffer_size = int(self.buffer_size)
        self.interval = config['Trade']['interval']
        if self.interval != '':
            self.interval = int(self.interval)
        self.pairs = config['Trade']['pairs'].replace(" ", "").split(',')
        self.strategy = config['Trade']['strategy']

    def on_simulation_done(self):
        """
        Last function called when the simulation is finished
        """
        print('shutting down and writing final statistics!')
        self.plot.draw(self.history)

    def run(self):
        """
        This is the main simulation loop
        """
        if self.bot is None:
            print(colored('The bot type is NOT specified. You need to choose one action (--sim, --paper, --trade)', 'red'))
            sys.exit()

        print('starting simulation')

        # Initialization
        self.report = Report(self.wallet.initial_balance, self.pairs)
        self.plot = Plot()

        try:
            while True:
                # 1) Get next ticker set
                self.ticker = self.bot.get_next(self.interval)
                self.history = self.history.append(self.ticker, ignore_index=True)
                self.look_back = self.look_back.append(self.ticker, ignore_index=True)
                #print('--ticker--', self.ticker)
                if len(self.look_back.index) > self.buffer_size:
                    self.look_back = self.look_back.drop(self.look_back.index[0])
                self.look_back.append(self.ticker)

                # 2) simulation/paper/trade - get next action(sample_size)
                action = self.strategy.calculate(self.look_back)

                # 3) trade(action)
                # TODO self.wallet = wallet.update_balance()

                # 4) trade.update_wallet

                # 5) write report
                self.report.calc_stats(self.ticker, self.wallet)

        except KeyboardInterrupt:
            self.on_simulation_done()

        except SystemExit:
            self.on_simulation_done()






