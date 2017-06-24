from pymongo import MongoClient, ASCENDING
import configparser
from .bot import Bot
import time


DAY = 86400



class Simulation(Bot):
    """
    Main class for Simulation trading
    """

    def __init__(self, args, config_file):
        super(Simulation, self).__init__(args, config_file)
        self.counter = 0
        self.config = self.initialize_config(config_file)
        self.db = self.initialize_db(self.config)
        self.ticker = self.db.ticker
        self.sim_start = self.config['Simulation']['from']
        self.sim_end = self.config['Simulation']['to']
        self.sim_days = int(self.config['Simulation']['days'])
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_days, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.pairs = self.config['Trade']['pairs'].split(',')
        self.exchange = self.config['Trade']['exchange']



    def get_sim_epoch_start(self, sim_days, sim_start):
        if sim_start:
            return sim_start
        elif sim_days:
            epoch_now = int(time.time())
            return epoch_now - (DAY*sim_days)



    def initialize_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config



    def initialize_db(self, config):
        db = config['MongoDB']['db']
        port = int(config['MongoDB']['port'])
        url = config['MongoDB']['url']
        client = MongoClient(url, port)
        db = client[db]
        return db


    def get_next(self, interval):
        '''
        Returns next state
        '''
        db_doc = self.ticker.find_one({"$and": [{"date": {"$gte": self.current_epoch}},
                                      {"pair": {"$in": self.pairs}},
                                      {"exchange": self.exchange}]})

#
        print('getting db_data for epoch:', self.current_epoch)
        print(db_doc['date'])
        print(db_doc)
        self.current_epoch += interval*60

        print('getting next ticker from Sim')
        return db_doc
