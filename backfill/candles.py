import time
import logging
from pymongo import ASCENDING
from backfill.base import Base
from core.constants import SECONDS_IN_DAY


class Candles(Base):
    """
    Back-fills ticker candle data
    """

    def __init__(self):
        super(Candles, self).__init__()
        self.args = self.arg_parser.parse_known_args()[0]
        self.db_ticker = self.db.ticker
        self.db_ticker.create_index([('id', ASCENDING)], unique=True)

    def run(self):
        """
        Run actual backfill job
        """
        # Get list of all currencies
        logger = logging.getLogger(__name__)
        time_start = time.time()
        pairs = self.get_backfill_pairs(self.args.all, self.args.pairs)
        logger.info("Back-filling candles for total currencies:" + str(len(pairs)))

        # Get the candlestick data
        epoch_now = int(time.time())

        for pair in pairs:
            for day in reversed(range(1, int(self.args.days) + 1)):
                epoch_from = epoch_now - (SECONDS_IN_DAY * day)
                epoch_to = epoch_now if day == 1 else epoch_now - (SECONDS_IN_DAY * (day - 1))
                logger.info('Getting currency data: ' + pair + ', days left: ' + str(day))
                candles = self.exchange.get_candles(pair,
                                                    epoch_from,
                                                    epoch_to,
                                                    300)  # by default 5 minutes candles (minimum)
                logger.info(' (got total candles: ' + str(len(candles)) + ')')
                for candle in candles:
                    if candle['date'] == 0:
                        logger.warning('Found nothing for pair: ' + pair)
                        continue
                    # Convert strings to number (float or int)
                    for key, value in candle.items():
                        if key == 'date':
                            candle[key] = int(value)
                        else:
                            candle[key] = float(value)
                    new_db_item = candle.copy()
                    # Add identifier
                    new_db_item['exchange'] = self.exchange_name
                    new_db_item['pair'] = pair
                    unique_id = self.exchange_name + '-' + pair + '-' + str(candle['date'])
                    new_db_item['id'] = unique_id
                    # Store to DB
                    self.db_ticker.update_one({'id': unique_id}, {'$set': new_db_item}, upsert=True)

        time_end = time.time()
        duration_in_sec = int(time_end-time_start)
        logger.info("Backfill done in (sec) " + str(duration_in_sec))
