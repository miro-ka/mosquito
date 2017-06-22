from core.simulation import Simulation
from core.paper import Paper
from core.trade import Trade
import configparser
import argparse



'''
Main class for Simulation Engine (main class where all is happening
'''


class Engine:
    def __init__(self, args, config_file):
        self.parseConfig(config_file)
        # Arguments should override config.ini file, so lets initialize
        # them only after config file parsing
        self.args = args
        self.config = config_file
        self.strategy = args.strategy
        self.look_back_data = []
        if args.sim:
            self.bot = Simulation(args)
        elif args.Trade:
            self.bot = Trade(args)
        elif args.paper:
            self.bot = Paper(args)



    def parseConfig(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.buffer_size = config['Trade']['buffer_size']
        self.interval = config['Trade']['interval']
        self.pairs = config['Trade']['pairs'].split(',')
        self.strategy = config['Trade']['strategy']



    def run(self):
        print('starting simulation')

        #TODO: initialize wallet

        #TODO load simulation. trade or paper

        #TODO load strategies

        #TODO run loop
        #while self.sim.finished():
        #    self.sim.get_next(2)

            #TODO simulation/paper/trade - get next sample(sample_size)
            #action = strategy.run
            #TODO Update wallet
            #TODO report