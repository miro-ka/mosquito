from abc import ABC, abstractmethod
from termcolor import colored
import configargparse
import pandas as pd


class Base(ABC):
    """
    Base class for all simulation types (sim, paper, trade)
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--price_intervals',
                   help='Price intervals saved in dataset (minutes) ',
                   default='120, 360, 720')

    feature_names = []
    scans_container = []
    min_history_ticks = 0

    def __init__(self, name, pairs):
        super(Base, self).__init__()
        self.name = name
        self.pairs = pairs
        arg_parser = configargparse.get_argument_parser()
        self.args = arg_parser.parse_known_args()[0]
        self.price_intervals = [int(x.strip()) for x in self.args.price_intervals.split(',')]
        self.Y_prefix = 'Y_'
        self.Yt_prefix = 'Yt_'
        self.Yt_column_names = self.create_yt_column_names(self.price_intervals, self.Yt_prefix)

    def get_feature_names(self):
        """
        Returns feature names
        """
        if len(self.scans_container) == 0:
            print(colored('Not enough data to get features name!', 'red'))
            return []
        df = self.scans_container[0][2]
        columns = df.columns.values.tolist()
        return columns

    @staticmethod
    @abstractmethod
    def calculate_features(df):
        """
        Method which calculates and generates features
        """

    @staticmethod
    def create_yt_column_names(intervals, prefix):
        return [prefix + str(interval) for interval in intervals]

    def scan(self,
             ticker_df=None,
             ticker_size=5):
        """
        Function that generates a blueprint from given dataset
        """
        final_scan_df = pd.DataFrame()
        if ticker_df.empty:
            return final_scan_df

        for pair_name in self.pairs:
            # Check if we have enough datasets
            pair_ticker_df = ticker_df.loc[ticker_df['pair'] == pair_name].sort_values('date')
            if len(pair_ticker_df.index) < self.min_history_ticks:
                continue

            # Create features
            features_df = self.calculate_features(pair_ticker_df.copy())
            # Initial output fields
            features_df = self.add_empty_outputs(features_df)
            self.scans_container.append((pair_name, 1, features_df))
            # Update stored scans
            final_scan = self.update(pair_name, pair_ticker_df, ticker_size)
            if final_scan:
                df_t = final_scan[2].copy()
                final_scan_df = final_scan_df.append(df_t, ignore_index=True)
        return final_scan_df

    def add_empty_outputs(self, df):
        """
        Creates interval columns with its interval as value
        """
        for interval in self.price_intervals:
            df[self.Yt_prefix+str(interval)] = None
        return df

    def update(self, pair_name, df, ticker_size):
        """
        Updates Y price intervals
        """
        # 1) get all scans for particular pair_name
        for idx, (pair, iter_counter, scan_df) in enumerate(self.scans_container[:]):
            if pair != pair_name:
                continue

            passed_interval = iter_counter * ticker_size
            scan_complete = True
            pair_df = df.loc[df['pair'] == pair]

            if pair_df.empty:
                print(colored('Got empty pair_df', 'red'))
                continue

            # Update Yt (target) intervals
            for Yt_name in self.Yt_column_names:
                interval = int(Yt_name.replace(self.Yt_prefix, ''))

                # If we have enough data and our target value is empty save it
                if passed_interval >= interval and not scan_df.iloc[-1].get(Yt_name):
                    interval_date = scan_df['date'].iloc[-1] + interval*60
                    interval_df_idx = (pair_df['date'].searchsorted(interval_date, side='right'))[0]
                    if interval_df_idx > 0:
                        interval_df_idx -= 1
                    interval_df = pair_df.iloc[interval_df_idx]
                    interval_df_date = interval_df['date']
                    if interval_df_date > interval_date:
                        print(colored("Problem while blueprint scan - invalid dates!!", 'red'))
                        exit(1)
                    close_price = interval_df['close']
                    scan_df[Yt_name] = close_price
                    # print('______________' + Yt_name + ', passed_interval: ' + str(passed_interval) + ', interval: '
                    # + str(interval))
                    # print('adding_close_value:', interval_df)
                    # print('scan_df:', scan_df)
                else:
                    column_value = scan_df.iloc[-1].get(Yt_name)
                    if not column_value:
                        scan_complete = False

            tmp_scan_list = list(self.scans_container[idx])
            tmp_scan_list[1] = iter_counter + 1
            tmp_scan_list[2] = scan_df.copy()
            self.scans_container[idx] = tuple(tmp_scan_list)

            # Check if we have all Yt data. If yes, return it
            if scan_complete:
                final_scan_df = self.scans_container[idx]
                self.scans_container.remove(final_scan_df)
                return final_scan_df
        return None
