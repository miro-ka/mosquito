import time
import logging
import pymongo
import pandas as pd
import configargparse
from termcolor import colored
from .poloniex.polo import Polo
from .bittrex.bittrexclient import BittrexClient
from core.bots.enums import TradeMode


class Exchange:
    """
    Main interface to all exchanges
    """

    exchange = None
    exchange_name = None
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--exchange', help='Exchange')
    arg_parser.add('--db_url', help='Mongo db url')
    arg_parser.add('--db_port', help='Mongo db port')
    arg_parser.add('--db', help='Mongo db')
    arg_parser.add('--pairs', help='Pairs')
    logger = logging.getLogger(__name__)

    def __init__(self, trade_mode=TradeMode.backtest, ticker_size=5):
        self.args = self.arg_parser.parse_known_args()[0]
        self.exchange = self.load_exchange()
        self.trade_mode = trade_mode
        self.db = self.initialize_db()
        self.ticker_client = self.db.ticker
        self.trades_client = self.db.trades
        self.ticker_size = ticker_size

    def get_pair_delimiter(self):
        """
        Returns exchanges pair delimiter
        """
        return self.exchange.get_pair_delimiter()

    def get_transaction_fee(self):
        """
        Returns exchanges transaction fee
        """
        return self.exchange.get_transaction_fee()

    def get_pairs(self):
        """
        Returns ticker for all pairs
        """
        return self.exchange.get_pairs()

    def get_symbol_ticker(self, symbol, candle_size=5):
        """
        Returns ticker for given symbol
        """
        return self.exchange.get_symbol_ticker(symbol, candle_size)

    def initialize_db(self):
        """
        DB Initialization
        """
        db = self.args.db
        port = int(self.args.db_port)
        url = self.args.db_url
        client = pymongo.MongoClient(url, port)
        db = client[db]
        return db

    def get_exchange_name(self):
        """
        Returns name of the exchange
        """
        return self.exchange_name

    def load_exchange(self):
        """
        Loads exchange files
        """
        self.exchange_name = self.args.exchange

        if self.exchange_name == 'polo':
            return Polo()
        elif self.exchange_name == 'bittrex':
            return BittrexClient()
        else:
            print('Trying to use not defined exchange!')
            return None

    def trade(self, actions, wallet, trade_mode):
        """
        Main class for setting up buy/sell orders
        """
        return self.exchange.trade(actions, wallet, trade_mode)

    def cancel_order(self, order_number):
        """
        Cancels order for given order number
        """
        return self.exchange.cancel_order(order_number)

    def get_balances(self):
        """
        Returns all available account balances
        """
        return self.exchange.get_balances()

    def get_candles_df(self, currency_pair, epoch_start, epoch_end, period=300):
        """
        Returns candlestick chart data in pandas dataframe
        """
        return self.exchange.get_candles_df(currency_pair, epoch_start, epoch_end, period)

    def get_candles(self, currency_pair, epoch_start, epoch_end, period=300):
        """
        Returns candlestick chart data
        """
        return self.exchange.get_candles(currency_pair, epoch_start, epoch_end, period)

    def get_open_orders(self, currency_pair='all'):
        """
        Returns your open orders
        """
        return self.exchange.get_open_orders(currency_pair)

    def get_market_history(self, start, end, currency_pair='all'):
        """
        Returns trade history
        """
        return self.exchange.get_market_history(start=int(start),
                                                end=int(end),
                                                currency_pair=currency_pair)

    # Do not use!!!: It turns out that group method is very consuming (takes approx 3x then get_offline_ticker)
    def get_offline_tickers(self, epoch, pairs):
        """
        Returns offline data from DB
        """
        pipeline = [
            {"$match": {"date": {"$lte": epoch}, "pair": {"$in": pairs}}},
            {"$group": {"_id": "$pair",
                        "pair": {"$last": "$pair"},
                        "high": {"$last": "$high"},
                        "low": {"$last": "$low"},
                        "open": {"$last": "$open"},
                        "close": {"$last": "$close"},
                        "volume": {"$last": "$volume"},
                        "quoteVolume": {"$last": "$quoteVolume"},
                        "weightedAverage": {"$last": "$weightedAverage"},
                        "date": {"$last": "$date"}
                        }
             }
        ]

        db_list = list(self.ticker_client.aggregate(pipeline, allowDiskUse=True))
        ticker_df = pd.DataFrame(db_list)
        df_pair = ticker_df['pair'].str.split('_', 1, expand=True)
        ticker_df = pd.concat([ticker_df, df_pair], axis=1)
        ticker_df = ticker_df.drop(['_id'], axis=1)
        return ticker_df

    def get_offline_ticker(self, epoch, pairs):
        """
        Returns offline ticker data from DB
        """
        ticker = pd.DataFrame()
        # print(' Getting offline ticker for total pairs: ' + str(len(pairs)) + ', epoch:', str(epoch))
        for pair in pairs:
            db_doc = self.ticker_client.find_one({"$and": [{"date": {"$lte": epoch}},
                                                           {"pair": pair},
                                                           {"exchange": self.exchange_name}]},
                                                 sort=[("date", pymongo.DESCENDING)])

            if db_doc is None:
                local_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
                print(colored('No offline data for pair: ' + pair + ', epoch: ' + str(epoch) + ' (local: '
                              + str(local_dt) + ')', 'yellow'))
                continue

            dict_keys = list(db_doc.keys())
            df = pd.DataFrame([db_doc], columns=dict_keys)
            df_pair = df['pair'].str.split('_', 1, expand=True)
            df = pd.concat([df, df_pair], axis=1)
            df.rename(columns={0: 'curr_1', 1: 'curr_2'}, inplace=True)
            ticker = ticker.append(df, ignore_index=True)
        return ticker

    def get_offline_trades(self, epoch, pairs):
        """
        Returns offline trades data from DB
        """
        trades = pd.DataFrame()
        date_start = epoch - self.ticker_size*60
        for pair in pairs:
            timer_start = time.time()
            db_doc = self.trades_client.find({"$and": [{"date": {"$gte": date_start, "$lte": epoch}},
                                                       {"pair": pair},
                                                       {"exchange": self.exchange_name}]})
            timer_duration = int(time.time() - timer_start)
            self.logger.info('data fetched from DB in sec:' + str(timer_duration))

            if db_doc.count() == 0:
                local_dt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))
                print(colored('No offline data for pair: ' + pair + ', epoch: ' + str(epoch) + ' (local: '
                              + str(local_dt) + ')', 'yellow'))

                # Add empty/zeroes dataframe
                single_trades_df = self.summarize_trades(pd.DataFrame(), pair)
                trades = trades.append(single_trades_df, ignore_index=True)
                continue

            timer_start = time.time()
            dict_keys = list(db_doc[0].keys())
            pair_trades_tmp = pd.DataFrame(list(db_doc), columns=dict_keys)
            timer_duration = int(time.time() - timer_start)
            self.logger.info('mongo doc parsed in sec:' + str(timer_duration))

            timer_start = time.time()
            single_trades_df = self.summarize_trades(pair_trades_tmp, pair)
            timer_duration = int(time.time() - timer_start)
            self.logger.info('trades data summarized in sec:' + str(timer_duration))
            trades = trades.append(single_trades_df, ignore_index=True)
        return trades

    def summarize_trades(self, df, pair):
        """
        Summarizes trades
        """
        trades_dict = {'pair': pair,
                       'exchange': self.exchange_name,
                       'buys_count': 0,
                       'buys_min': 0.0,
                       'buys_max': 0.0,
                       'buys_mean': 0,
                       'buys_volume': 0.0,
                       'buys_rate_mean': 0.0,
                       'buys_rate_spam': 0.0,
                       'sells_count': 0,
                       'sells_min': 0.0,
                       'sells_max': 0.0,
                       'sells_mean': 0,
                       'sells_volume': 0.0,
                       'sells_rate_mean': 0.0,
                       'sells_rate_spam': 0.0,
                       }

        if not df.empty:
            # Buy trades
            buys_df = df[df['type'] == 'buy']
            trades_dict['pair'] = df.pair.iloc[0]
            trades_dict['exchange'] = df.exchange.iloc[0]
            trades_dict['buys_count'] = int(buys_df.shape[0])
            trades_dict['buys_min'] = buys_df.amount.min()
            trades_dict['buys_max'] = buys_df.amount.max()
            trades_dict['buys_mean'] = buys_df.amount.mean()
            trades_dict['buys_volume'] = buys_df.amount.sum()
            trades_dict['buys_rate_mean'] = buys_df.rate.mean()
            trades_dict['buys_rate_spam'] = buys_df.rate.max() - buys_df.rate.min()
            # Sell trades
            sells_df = df[df['type'] == 'sell']
            trades_dict['sells_count'] = int(sells_df.shape[0])
            trades_dict['sells_min'] = sells_df.amount.min()
            trades_dict['sells_max'] = sells_df.amount.max()
            trades_dict['sells_mean'] = sells_df.amount.mean()
            trades_dict['sells_volume'] = sells_df.amount.sum()
            trades_dict['sells_rate_mean'] = sells_df.rate.mean()
            trades_dict['sells_rate_spam'] = sells_df.rate.max() - sells_df.rate.min()

        ticker_df = pd.DataFrame.from_dict(trades_dict, orient="index").transpose()
        return ticker_df
