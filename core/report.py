from termcolor import colored
from datetime import  datetime


class Report:
    """
    Main reporting class (overall score and plots)
    """

    init_close = []

    def __init__(self, balance):
        self.init_balance = balance

    def calc_stats(self, ticker_data):
        """
        Creates ticker report
        """
        if len(self.init_close) == 0:
            self.initialize_start_price(ticker_data)
        date_time = datetime.fromtimestamp(ticker_data['date']).strftime('%c') + ':\t '
        current_close = 'close:' + format(ticker_data.iloc[0]['close'], '2f') + ', '
        # Buy & Hold
        buy_and_hold = self.calc_buy_and_hold(ticker_data)
        if buy_and_hold < 0:
            buy_and_hold = colored('b&h: ' + format(buy_and_hold, '.2f') + '%', 'red')
        else:
            buy_and_hold = colored('buy_hold: ' + format(buy_and_hold, '.2f') + '%', 'green')

        print(date_time + current_close + buy_and_hold)
        return 0

    def initialize_start_price(self, ticker_data):
        currency = ticker_data.iloc[0]['curr_1']
        closing = ticker_data.iloc[0]['close']
        balance_item = [item for item in self.init_balance if currency in item]
        if balance_item[0][0] == currency:
            self.init_close.append((currency, closing))

    def calc_buy_and_hold(self, ticker_data):
        currency = ticker_data.iloc[0]['curr_1']
        current_closing = ticker_data.iloc[0]['close']
        init_closing = [item for item in self.init_close if currency in item][0][1]
        return ((current_closing - init_closing)*100.0)/init_closing
