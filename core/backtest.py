from pymongo import MongoClient, ASCENDING
import configparser
from .bot import Bot
import time
import sys
import pandas as pd


DAY = 86400


class Backtest(Bot):
    """
    Main class for Backtest trading
    """

    def __init__(self, args, config_file):
        super(Backtest, self).__init__(args, config_file)
        self.counter = 0
        self.config = self.initialize_config(config_file)
        self.db = self.initialize_db(self.config)
        self.ticker = self.db.ticker
        self.sim_start = self.config['Backtest']['from']
        self.sim_end = self.config['Backtest']['to']
        self.sim_days = int(self.config['Backtest']['days'])
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_days, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.pairs = self.config['Trade']['pairs'].replace(" ", "").split(',')
        self.exchange = self.config['Trade']['exchange']

    @staticmethod
    def get_sim_epoch_start(sim_days, sim_start):
        if sim_start:
            return sim_start
        elif sim_days:
            epoch_now = int(time.time())
            return epoch_now - (DAY*sim_days)

    @staticmethod
    def initialize_config(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    @staticmethod
    def initialize_db(config):
        db = config['MongoDB']['db']
        port = int(config['MongoDB']['port'])
        url = config['MongoDB']['url']
        client = MongoClient(url, port)
        db = client[db]
        return db

    def get_next(self, interval):
        """
        Returns next state
        """
        db_doc = self.ticker.find_one({"$and": [{"date": {"$gte": self.current_epoch}},
                                      {"pair": {"$in": self.pairs}},
                                      {"exchange": self.exchange}]})

        if db_doc is None:
            sys.exit()
        # print('getting db_data for epoch:', self.current_epoch)
        # print(db_doc['date'])
        self.current_epoch += interval*60
        dict_keys = list(db_doc.keys())
        df = pd.DataFrame([db_doc], columns=dict_keys)
        df_pair = df['pair'].str.split('_', 1, expand=True)
        df = pd.concat([df, df_pair], axis=1)
        df.rename(columns={0: 'curr_1', 1: 'curr_2'}, inplace=True)

        return df
