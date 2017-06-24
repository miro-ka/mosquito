import configparser
import sys
from termcolor import colored
from .simulation import Simulation
from .paper import Paper
from .trade import Trade
from .wallet import Wallet
from importlib import import_module



class Engine:
    """
    Main class for Simulation Engine (main class where all is happening
    """

    def __init__(self, args, config_file):
        self.buffer_size = None
        self.interval = None
        self.pairs = None
        self.parse_config(config_file)
        # Arguments should override config.ini file, so lets initialize
        # them only after config file parsing
        self.args = args
        self.config = config_file
        strategy_class = self.load_strategy(args.strategy)
        self.strategy = strategy_class(args)
        self.look_back_data = []
        self.wallet = Wallet(config_file)
        self.bot = None
        self.data = None
        if args.sim:
            self.bot = Simulation(args, config_file)
        elif args.trade:
            self.bot = Trade(args, config_file)
        elif args.paper:
            self.bot = Paper(args, config_file)


    @staticmethod
    def load_strategy(strategy_name):
        module = import_module("strategies." + strategy_name)
        strategy = getattr(module, strategy_name.capitalize())
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
        if self.bot is None:
            print(colored('The bot type is NOT specified. You need to choose one action (--sim, --paper, --trade)', 'red'))
            sys.exit()

        print('starting simulation')

        #TODO: initialize wallet

        #TODO run loop

        try:
            while True:
                # TODO self.wallet = wallet.update_balance()

                self.data = self.bot.get_next(self.interval)

                # TODO simulation/paper/trade - get next sample(sample_size)
                action = self.strategy.calulate(self.interval)
                # TODO Update wallet
                # TODO report
        except KeyboardInterrupt:
            print('shutting down and writing final statistics!')


