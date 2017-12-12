import time
import numpy as np
import pandas as pd
import configargparse
from termcolor import colored
from backfill import main as backfill
from exchanges.exchange import Exchange
from utils.postman import Postman


class WalletLense:
    """
    Lense: Returns actual wallet statistics with simple daily digest (winners / losers)
    """
    arg_parser = configargparse.get_argument_parser()
    analysis_days = 1
    time_intervals_hours = [1, 3, 6, 12, 24]

    def __init__(self):
        self.args = self.arg_parser.parse_known_args()[0]
        print(colored('Starting lense on exchange: ' + self.args.exchange, 'yellow'))
        self.exchange = Exchange()
        self.postman = Postman()

    def get_stats(self):
        """
        Returns current statistics (market and wallet)
        """
        self.fetch_last_ticker(self.analysis_days)
        df_candles = self.get_ticker(self.exchange.get_pairs(), self.analysis_days)
        df_candles.to_csv('test_ticker.csv', index=False)
        # df_candles = pd.read_csv('test_ticker.csv')

        # Parse all df's to html
        html_body = ['<html><body>']
        html_body.append('<img src="https://user-images.githubusercontent.com/1301154/33856783-88f8e426-dec9-11e7-8371-ead4ef95006a.png" alt="Mosquito" width="330" height="258">')
        winners, losers = self.get_winners_losers(df_candles)
        html_body.append(self.parse_winners_losers_to_html(winners, losers))

        # wallet_stats = self.get_wallet_stats(ticker)
        print('wallet stats:')
        html_body.append('</body></html>')
        self.send_email(html_body)

    @staticmethod
    def df_to_html(df, header, bar_color='lightblue'):
        """
        Converts DataFrame to html text
        """
        df_header = '<h3>' + header + '</h1>'
        table = (df.style.set_properties(**{'font-size': '9pt', 'font-family': 'Calibri'})
                         .set_precision(3)
                         # .background_gradient(subset=['price_change'], cmap='PuBu', low=-100.0, high=100.0)
                         .set_table_styles([{'selector': '.row_heading, .blank', 'props': [('display', 'none;')]}])
                         .bar(subset=['price_change'], color=bar_color)
                         .render()
        )
        return df_header + table

    def send_email(self, body_list):
        """
        Sending email module
        """

        body = ''
        for body_item in body_list:
            body += '\n' + body_item

        self.postman.send_mail('mosquito_stats', body)

    def get_wallet_stats(self, ticker):
        """
        Returns simple wallet stats
        """
        wallet = self.exchange.get_balances()
        return wallet

    def parse_winners_losers_to_html(self, winners, losers):
        """
        Converts Winners and Losers df's to html
        """
        html = '<h2> Winners </h2>'
        grouped_winners = winners.groupby(['hour_spam'])
        for key, df in grouped_winners:
            df = df.drop(['hour_spam'], axis=1)
            # Reorder columns
            df = df[['price_change', 'pair', 'V', 'Vq']]
            html += self.df_to_html(df, str(key) + '-Hour', bar_color='lightgreen')

        html += '<hr>'

        html += '<h2> Losers </h2>'
        grouped_losers = losers.groupby(['hour_spam'])
        for key, df in grouped_losers:
            df = df.drop(['hour_spam'], axis=1)
            df = df.sort_values(['price_change'], ascending=[1])
            df['price_change'] = df['price_change'] * -1.0
            # Reorder columns
            df = df[['price_change', 'pair', 'V', 'Vq']]
            html += self.df_to_html(df, str(key) + '-Hour', bar_color='lightpink')

        return html

    def get_ticker(self, pairs, history_days):
        """
        Gets ticker for given list of pairs and given perion
        """
        print('Getting tickers.. (might take a while)')
        ticker_to = int(time.time())
        ticker_from = ticker_to - (24 * history_days * 3600)
        df_pairs_ticker = pd.DataFrame()
        for pair in pairs:
            ticker_list = self.exchange.get_candles(pair, ticker_from, ticker_to, period=1800)
            df_ticker = pd.DataFrame(ticker_list)
            df_ticker['pair'] = pair
            df_pairs_ticker = df_pairs_ticker.append(df_ticker, ignore_index=True)
        return df_pairs_ticker

    def get_winners_losers(self, df_ticker):
        """
        Get winners/losers
        """
        grouped = df_ticker.groupby(['pair'])
        df_stats = pd.DataFrame()
        for name, df_group in grouped:
            pair_stat = self.get_pair_stats(name, df_group, self.time_intervals_hours)
            df_s = pd.DataFrame(pair_stat)
            df_stats = df_stats.append(df_s, ignore_index=True)
        grouped_stats = df_stats.groupby(['hour_spam'])
        winners = pd.DataFrame()
        losers = pd.DataFrame()
        for interval, df_group in grouped_stats:
            sorted_intervals = df_group.sort_values('price_change', ascending=False)
            winners = winners.append(sorted_intervals.head(5))
            losers = losers.append(sorted_intervals.tail(5))
        return winners, losers

    def get_pair_stats(self, pair, df, hour_intervals):
        """
        Returns statistics summary
        """
        df_now = df.tail(1)
        date_end = df_now['date'].iloc[0]
        dates = df['date']
        stats = []
        for hour_interval in hour_intervals:
            next_epoch = hour_interval * 3600
            closest_date_idx = self.find_nearest(dates, date_end - next_epoch)
            closest_df = df.loc[closest_date_idx]
            df_interval = df.loc[df['date'] == closest_df.date]
            pair_stats = self.calc_pair_stats(df_now.iloc[0], df_interval.iloc[0])
            pair_stats['pair'] = pair
            pair_stats['hour_spam'] = hour_interval
            stats.append(pair_stats)
        return stats

    @staticmethod
    def calc_pair_stats(ticker_now, ticker_past):
        stats = dict()
        price_change = ((float(ticker_past.close) * 100.0) / float(ticker_now.close)) - 100.0
        volume_perc_change = ((float(ticker_past.volume) * 100.0) / float(ticker_now.volume)) - 100.0
        quote_volume_perc_change = ((float(ticker_past.quoteVolume) * 100.0) / float(ticker_now.quoteVolume)) - 100.0
        stats['price_change'] = price_change
        stats['V'] = volume_perc_change
        stats['Vq'] = quote_volume_perc_change
        return stats

    @staticmethod
    def find_nearest(array, value):
        idx = (np.abs(array - value)).argmin()
        return idx

    def fetch_last_ticker(self, prefetch_days):
        """
        Prefetch data for all pairs for given days
        """
        self.args.days = prefetch_days
        self.args.all = True
        backfill(self.args)
