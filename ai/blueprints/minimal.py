import talib
import pandas as pd
import configargparse
import core.common as common


class Minimal:
    """
    Minimal blueprint - example of implementation blueprint logic
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--price_intervals', help='Price intervals save in dataset (minutes) ', default='5, 30, 60')
    scans_container = []

    def __init__(self, pairs):
        args = self.arg_parser.parse_known_args()[0]
        self.pairs = pairs
        self.price_intervals = [int(x.strip()) for x in args.price_intervals.split(',')]
        self.min_history_ticks = 10
        self.Y_prefix = 'Y_'
        self.Yt_prefix = 'Yt_'
        self.Yt_column_names = self.create_yt_column_names(self.price_intervals, self.Yt_prefix)

    @staticmethod
    def create_yt_column_names(intervals, prefix):
        return [prefix + str(interval) for interval in intervals]

    def scan(self, df, ticker_size):
        """
        Function that tries to generate a blueprint from given dataset
        """
        final_scan_df = pd.DataFrame()

        # Check if we have enough datasets
        (dataset_cnt, _) = common.get_dataset_count(df)
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt)
            return final_scan_df

        for pair_name in self.pairs:
            pair_df = df.loc[df['pair'] == pair_name].sort_values('date')
            if len(pair_df.index) < self.min_history_ticks:
                continue

            # Create features
            scan_df = self.calculate_features(pair_df.copy())
            # Initial output fields
            scan_df = self.add_empty_outputs(scan_df)
            self.scans_container.append((pair_name, 0, scan_df))

            # Update stored scans
            final_scan = self.update_scans(pair_df, ticker_size)
            if final_scan:
                df_t = final_scan[2]
                final_scan_df = final_scan_df.append(df_t, ignore_index=True)

        return final_scan_df

    def update_scans(self, df, ticker_size):
        """
        Updates Y price intervals
        """
        for idx, (_, iter_counter, scan_df) in enumerate(self.scans_container):
            passed_interval = iter_counter * ticker_size
            scan_complete = True

            # Update Yt intervals
            for Yt_name in self.Yt_column_names:
                interval = int(Yt_name.replace(self.Yt_prefix, ''))
                if passed_interval == interval:
                    close_price = df['close'].iloc[-1]
                    scan_df[Yt_name] = close_price
                else:
                    column_value = scan_df.iloc[-1].get(Yt_name)
                    if not column_value:
                        scan_complete = False

            tmp_scan_list = list(self.scans_container[idx])
            tmp_scan_list[1] = iter_counter + 1
            tmp_scan_list[2] = scan_df
            self.scans_container[idx] = tuple(tmp_scan_list)

            # Check if we have all Yt data. If yes, return it
            if scan_complete:
                scan_df = self.scans_container[idx]
                self.scans_container.pop(idx)
                return scan_df

        return None

    def calculate_features(self, df):
        """
        Method which calculates and generates features
        """
        close = df['close'].values
        last_row = df.tail(1).copy()

        # ************** Calc EMA10
        ema10_period = 10
        ema10 = talib.EMA(close[-ema10_period:], timeperiod=ema10_period)[-1]
        # last_row.loc[self.Y_prefix+'ema'] = ema10
        last_row[self.Y_prefix+'ema'] = ema10
        return last_row

    def add_empty_outputs(self, df):
        """
        Creates interval columns with its interval as value
        """
        for interval in self.price_intervals:
            df[self.Yt_prefix+str(interval)] = None
        return df

