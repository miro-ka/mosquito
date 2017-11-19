import numpy as np
import configargparse


class StopLoss:
    """
    StopLoss class with normal and trailing stop-loss functionality
    :param: interval: Interval in minutes for checking price difference
    :param stop_loss_limit: Percentage value for stop-loss (how much should the price drop to send stop-loss signal
    :param trailing: If True stop_loss Trailing stop-loss will be applied. If False first price will be used
    for a static stop-loss limit
    :param ticker_size: Ticker size
    """

    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--stoploss_interval', help='Stop-loss interval in minutes')
    base_price = None

    def __init__(self, ticker_size, interval=30, stop_loss_limit=-0.1, trailing=True, ):
        self.trailing = trailing
        self.checkpoint = int(interval/ticker_size)
        self.stop_loss_limit = stop_loss_limit

    def calculate(self, price):
        """

        :param price: numpy array of price values
        :return: Returns True if Stop-Loss met conditions
        """

        # Check if array has data
        if len(price) < self.checkpoint:
            print('StopLoss: not enough data.')
            return False

        if not self.base_price:
            self.base_price = price[-1]
            print('StopLoss: setting base-price to:', self.base_price)
            return False

        last_price = price[-1]
        checkpoint_price = price[-self.checkpoint]
        percentage_change = last_price*100/checkpoint_price - 100.0
        if percentage_change <= self.stop_loss_limit:
            return True

        # Handle trailing
        if self.trailing:
            if last_price > self.base_price:
                self.base_price = last_price

