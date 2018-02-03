import sys
import time
import logging
from backfill.base import Base
from core.constants import SECONDS_IN_DAY
from termcolor import colored


class BackfillTicker(Base):
    """
    Back-fills ticker data
    """

    def __init__(self):
        super(BackfillTicker, self).__init__()
        self.args = self.arg_parser.parse_known_args()[0]
        self.logger = logging.getLogger(__name__)

    def run(self):
        """
        Run actual backfill job
        """
        # Get list of all currencies
        all_pairs = self.exchange.get_pairs()
        logger = logging.getLogger(__name__)
        logger.info("Back-filling total currencies:" + str(len(all_pairs)))
        time_start = time.time()
        if self.args.all:
            pairs = all_pairs
        elif self.args.pairs is not None:
            tmp_pairs = [self.args.pairs]
            pairs = []
            # Handle * suffix pairs
            for pair in tmp_pairs:
                if '*' in pair:
                    prefix = pair.replace('*', '')
                    pairs_list = [p for p in all_pairs if prefix in p]
                    pairs.extend(pairs_list)
                    # remove duplicates
                    pairs = list(set(pairs))
                else:
                    pairs.append(pair)

        # Get the candlestick data
        epoch_now = int(time.time())

        for pair in pairs:
            for day in reversed(range(1, int(self.args.days) + 1)):
                epoch_from = epoch_now - (SECONDS_IN_DAY * day)
                epoch_to = epoch_now if day == 1 else epoch_now - (SECONDS_IN_DAY * (day - 1))
                print('Getting currency data: ' + pair + ', days left: ' + str(day), end='')
                candles = self.exchange.get_candles(pair, epoch_from, epoch_to,

                                                    300)  # by default 5 minutes candles (minimum)
                print(' (got total candles: ' + str(len(candles)) + ')')
                for candle in candles:
                    if candle['date'] == 0:
                        print(colored('Found nothing for pair: ' + pair, 'yellow'))
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
