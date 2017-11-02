import talib
import pandas as pd
import configargparse
from termcolor import colored


class Junior:
    """
    Mid-size blueprint - EMA, RCI, CCI, OBV
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--price_intervals', help='Price intervals saved in dataset (minutes) ', default='5, 30, 60')
    scans_container = []

    def __init__(self, pairs):
        args = self.arg_parser.parse_known_args()[0]
        self.name = 'junior'
        self.pairs = pairs
        self.price_intervals = [int(x.strip()) for x in args.price_intervals.split(',')]
        self.min_history_ticks = 35
        self.Y_prefix = 'Y_'
        self.Yt_prefix = 'Yt_'
        self.Yt_column_names = self.create_yt_column_names(self.price_intervals, self.Yt_prefix)

    @staticmethod
    def create_yt_column_names(intervals, prefix):
        return [prefix + str(interval) for interval in intervals]

    def scan(self, df, ticker_size):
        """
        Function that generates a blueprint from given dataset
        """
        final_scan_df = pd.DataFrame()
        if df.empty:
            return final_scan_df

        for pair_name in self.pairs:
            # Check if we have enough datasets
            pair_df = df.loc[df['pair'] == pair_name].sort_values('date')
            if len(pair_df.index) < self.min_history_ticks:
                continue

            # Create features
            scan_df = self.calculate_features(pair_df.copy())
            # Initial output fields
            scan_df = self.add_empty_outputs(scan_df)
            self.scans_container.append((pair_name, 1, scan_df))

            # Update stored scans
            final_scan = self.update_scans(pair_name, pair_df, ticker_size)
            if final_scan:
                df_t = final_scan[2]
                final_scan_df = final_scan_df.append(df_t, ignore_index=True)
        return final_scan_df

    def update_scans(self, pair_name, df, ticker_size):
        """
        Updates Y price intervals
        """
        for idx, (pair, iter_counter, scan_df) in enumerate(self.scans_container[:]):
            if pair != pair_name:
                continue

            passed_interval = iter_counter * ticker_size
            scan_complete = True

            pair_df = df.loc[df['pair'] == pair]

            if pair_df.empty:
                print(colored('Got empty pair_df', 'red'))
                continue

            # Update Yt intervals
            for Yt_name in self.Yt_column_names:
                interval = int(Yt_name.replace(self.Yt_prefix, ''))
                if passed_interval == interval:
                    close_price = pair_df['close'].iloc[-1]
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
                self.scans_container.remove(scan_df)
                return scan_df
        return None

    @staticmethod
    def calculate_features(df):
        """
        Method which calculates and generates features
        """
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        last_row = df.tail(1).copy()

        # ************** Calc EMAs
        ema_periods = [3, 6, 12, 18]
        for ema_period in ema_periods:
            ema = talib.EMA(close[-ema_period:], timeperiod=ema_period)[-1]
            last_row['ema' + str(ema_period)] = ema

        # ************** Calc RSIs
        rsi_periods = [15]
        for rsi_period in rsi_periods:
            rsi = talib.RSI(close[-rsi_period:], timeperiod=rsi_period-1)[-1]
            last_row['rsi' + str(rsi_period)] = rsi
            last_row['rsi_above_50' + str(rsi_period)] = int(rsi > 50.0)

        # ************** Calc CCIs
        cci_periods = [14]
        for cci_period in cci_periods:
            cci = talib.CCI(high[-cci_period:],
                            low[-cci_period:],
                            close[-cci_period:],
                            timeperiod=cci_period)[-1]
            last_row['cci' + str(cci_period)] = cci

        # ************** Calc MACD
        macd_periods = [34]
        for macd_period in macd_periods:
            macd, macd_signal, _ = talib.MACD(close[-macd_period:],
                                              fastperiod=12,
                                              slowperiod=26,
                                              signalperiod=9)
            macd = macd[-1]
            signal_line = macd_signal[-1]
            last_row['macd_above_signal'] = int(macd > signal_line)
            last_row['macd_above_zero'] = int(macd > 0.0)

        # ************** Calc OBVs
        obv_periods = [6, 12, 18]
        for obv_period in obv_periods:
            obv = talib.OBV(close[-obv_period:], volume[-obv_period:])[-1]
            last_row['obv' + str(obv_period)] = obv

        return last_row

    def add_empty_outputs(self, df):
        """
        Creates interval columns with its interval as value
        """
        for interval in self.price_intervals:
            df[self.Yt_prefix+str(interval)] = None
        return df

