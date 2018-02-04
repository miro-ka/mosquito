import time
import json
import logging
import pandas as pd
import configargparse
from pymongo import ASCENDING
from backfill.base import Base
from core.constants import SECONDS_IN_DAY


class Trades(Base):
    """
    Back-fills ticker trade data
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add("--backfilltrades", help="Fetch /backfill and store trade history",  action='store_true')

    def __init__(self):
        super(Trades, self).__init__()
        self.args = self.arg_parser.parse_known_args()[0]
        self.fetch_interval = 3600*6  # 6 hour batches
        self.db_trades = self.db.trades
        self.db_trades.create_index([('id', ASCENDING)], unique=True)

    def run(self):
        """
        Run actual backfill job
        """
        # Get list of all currencies
        logger = logging.getLogger(__name__)
        pairs = self.get_backfill_pairs(self.args.all, self.args.pairs)
        logger.info("Back-filling trade orders for total currencies: " + str(len(pairs)))
        time_start = time.time()

        # Get the candlestick data
        init_date_end = int(time.time())
        init_date_start = init_date_end - (SECONDS_IN_DAY*int(self.args.days))
        fetch_interval = 3600 * 6

        for pair in pairs:
            fetch_end_date = init_date_start
            date_start = init_date_start
            while fetch_end_date < init_date_end:
                fetch_end_date = date_start + fetch_interval
                date_start_string = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date_start))
                fetch_end_string = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fetch_end_date))
                logger.debug('fetching intervals: ' + pair + ', ' + date_start_string + ' - ' + fetch_end_string)
                trades = self.exchange.get_market_history(currency_pair=pair,
                                                          start=date_start,
                                                          end=fetch_end_date)
                date_start = fetch_end_date+1
                if len(trades) == 0:
                    logger.debug('No trades for: ' + pair + str(date_start))
                    continue

                df = pd.DataFrame(trades)
                df = df.infer_objects()
                df['id'] = self.exchange_name + '-' + pair + '-' + df['globalTradeID'].astype(str)
                id_list = list(df['id'])
                # self.db_ticker.update_one({'id': unique_id}, {'$set': new_db_item}, upsert=True)
                existing_ids_df = pd.DataFrame(list(self.db_trades.find({'id': {'$in': id_list}}, {'id': 1})))
                # Check if db contains already values that we want to insert
                if not existing_ids_df.empty:
                    existing_ids = list(existing_ids_df['id'])
                    df = df[~df['id'].isin(existing_ids)]
                    # Drop existing records
                    df = df[~df['id'].isin(existing_ids)]
                    if df.empty:
                        continue
                records = json.loads(df.T.to_json()).values()
                self.db_trades.insert(records)
                # records = df.to_dict(orient='records')
                # for record in records:
                #    self.db_trades.update_one({'id': record['id']}, {'$set': record}, upsert=True)

        time_end = time.time()
        duration_in_sec = int(time_end-time_start)
        logger.info("Backfill done in (sec) " + str(duration_in_sec))
