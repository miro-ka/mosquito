import os
import time
import pandas as pd
import configargparse
import core.common as common
from exchanges.exchange import Exchange
from termcolor import colored


class Blueprint:
    """
    Main module for generating and handling datasets for AI. Application will generate datasets including
    future target/output parameters.
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--days', help='Days to start blueprint from', default=30)
    arg_parser.add('-f', '--features', help='Blueprints module name to be used to generated features', required=True)
    arg_parser.add('--ticker_size', help='Size of the candle ticker (minutes)', default=5)
    arg_parser.add('--pairs', help='Pairs to blueprint')
    arg_parser.add('-v', '--verbosity', help='Verbosity', action='store_true')
    arg_parser.add("--buffer_size", help="Maximum Buffer size (days)", default=30)
    arg_parser.add("--output_dir", help="Output directory")

    features_list = None
    exchange = None
    blueprint = None
    out_dir = 'out/blueprints/'

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        self.blueprint_days = args.days
        self.ticker_size = int(args.ticker_size)
        self.blueprint_end_time = int(time.time())
        self.start_time = self.blueprint_end_time - int(self.blueprint_days)*86400
        self.ticker_epoch = self.start_time
        self.exchange = Exchange(None)
        self.pairs = common.parse_pairs(self.exchange, args.pairs)
        blueprints_module = common.load_module('ai.blueprints.', args.features)
        self.blueprint = blueprints_module(self.pairs)
        self.max_buffer_size = int(int(args.buffer_size) * (1440 / self.ticker_size) * len(self.pairs))
        self.df_buffer = pd.DataFrame()
        self.df_blueprint = pd.DataFrame()
        self.output_dir = args.output_dir
        self.export_file_name = self.get_output_file_path(self.output_dir, self.blueprint.name)
        self.export_file_initialized = False

        # Crete output dir
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

    @staticmethod
    def get_output_file_path(dir_path, blueprint_name):
        filename = 'blueprint_' + blueprint_name + '_' + str(int(time.time())) + '.csv'
        if dir_path:
            if not dir_path.endswith(os.path.sep):
                dir_path += os.path.sep
            filename = dir_path + filename
        return filename

    def print_progress_dot(self, counter):
        """
        Prints progress
        """
        if counter % 100 == 0:
            print('.', end='', flush=True)
        if counter > 101:
            counter = 0
            self.write_to_file()
        return counter+1

    def write_to_file(self):
        """
        Writes df to file
        """
        if self.df_blueprint.empty:
            print('Blueprint is empty, nothing to write to file.')
            return

        export_df = self.df_blueprint.copy()
        dropping_columns = ['_id', 'id', 'curr_1', 'curr_2', 'exchange']
        df_columns = self.blueprint.get_feature_names()
        df_columns = [x for x in df_columns if x not in dropping_columns]
        export_df = export_df.drop(dropping_columns, axis=1)
        export_df = export_df[df_columns]
        dt = export_df.tail(1).date.iloc[0]
        dt_string = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(dt))
        print('saving,..(last df date: ' + dt_string + ')')
        if not self.export_file_initialized:
            export_df.to_csv(self.out_dir + self.export_file_name, index=False, columns=df_columns)
            self.export_file_initialized = True
        else:
            export_df.to_csv(self.out_dir + self.export_file_name,
                             mode='a',
                             header=False,
                             index=False,
                             columns=df_columns)

        self.df_blueprint = self.df_blueprint[0:0]

    def run(self):
        """
        Calculates and stores dataset
        """
        info_text = 'Starting generating data for Blueprint ' + self.blueprint.name + ' :back-days ' + \
                    self.blueprint_days + ' (This might take several hours/days,.so please stay back and relax)'
        print(colored(info_text, 'yellow'))
        dot_counter = 0
        while True:
            # Get new dataset
            df = self.exchange.get_offline_ticker(self.ticker_epoch, self.pairs)

            # Check if the simulation is finished
            if self.ticker_epoch >= self.blueprint_end_time:
                self.write_to_file()
                return

            # Store df to buffer
            if not self.df_buffer.empty:
                df = df[list(self.df_buffer)]
                self.df_buffer = self.df_buffer.append(df, ignore_index=True)
            else:
                self.df_buffer = self.df_buffer.append(df, ignore_index=True)
            self.df_buffer = common.handle_buffer_limits(self.df_buffer, self.max_buffer_size)

            scan_df = self.blueprint.scan(self.df_buffer, self.ticker_size)
            if not scan_df.empty:
                dot_counter = self.print_progress_dot(dot_counter)
                self.df_blueprint = self.df_blueprint.append(scan_df, ignore_index=True)

            self.ticker_epoch += self.ticker_size*60

