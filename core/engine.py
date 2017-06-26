import configparser
import sys
from termcolor import colored
from .simulation import Simulation
from .paper import Paper
from .trade import Trade
from .wallet import Wallet
from .report import Report
from importlib import import_module
import pandas as pd


class Engine:
    """
    Main class for Simulation Engine (main class where all is happening
    """
    buffer_size = None
    interval = None
    pairs = None
    bot = None
    ticker = None
    look_back = None
    report = None

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
        if args.sim:
            self.bot = Simulation(args, config_file)
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
        self.pairs = config['Trade']['pairs'].split(',')
        self.strategy = config['Trade']['strategy']

    def run(self):
        """
        This is the main simulation loop
        """
        if self.bot is None:
            print(colored('The bot type is NOT specified. You need to choose one action (--sim, --paper, --trade)', 'red'))
            sys.exit()

        print('starting simulation')

        # Initialization
        self.report = Report(self.wallet.initial_balance)
        # TODO: initialize wallet

        # TODO run loop

        try:
            while True:
                # 1) Get next ticker set
                self.ticker = self.bot.get_next(self.interval)

                self.look_back = self.look_back.append(self.ticker, ignore_index=True)
                #print(self.look_back)

                if len(self.look_back.index) > self.buffer_size:
                    self.look_back = self.look_back.drop(self.look_back.index[0])
                self.look_back.append(self.ticker)
                # 2) simulation/paper/trade - get next action(sample_size)
                action = self.strategy.calculate(self.look_back)

                # 3) trade(action)
                # TODO self.wallet = wallet.update_balance()

                # 4) trade.update_wallet

                # 5) write/draw report
                self.report.calc_stats(self.ticker)

        except KeyboardInterrupt:
            print('shutting down and writing final statistics!')

        except SystemExit:
            print('simulation done')



