from termcolor import colored
from datetime import datetime


class Report:
    """
    Main reporting class (overall score and plots)
    """

    initial_close = []
    initial_balance = 0.0

    def __init__(self, initial_wallet, pairs):
        self.initial_wallet = initial_wallet
        self.pairs = pairs

    def calc_stats(self, ticker_data, wallet):
        """
        Creates ticker report
        """
        if len(self.initial_close) != len(self.pairs):
            self.initialize_start_price(ticker_data)
        date_time = datetime.fromtimestamp(ticker_data['date']).strftime('%c') + ','
        current_close = 'close:' + format(ticker_data.iloc[0]['close'], '2f') + ','
        # Wallet
        wallet_text = self.get_wallet_text(wallet)
        # Balance
        balance = self.calc_balance(ticker_data, wallet)
        balance_text = self.get_color_text('$: ', balance) + ','
        # Buy & Hold
        bh = self.calc_buy_and_hold(ticker_data)
        bh_text = self.get_color_text('b&h: ', bh)
        print(date_time,
              current_close,
              wallet_text,
              balance_text,
              bh_text)

        return 0

    @staticmethod
    def get_wallet_text(wallet, currencies=None):
        """
        Returns wallet balance in string. By default it returns balance of the entire wallet.
        You can specify currencies which you would like to receive update
        """
        # TODO return only wallet of given currencies
        wallet_string = ''
        for item in wallet.current_balance:
            wallet_string += ' | ' + str(item[1]) + item[0]
        wallet_string += ' |'
        return wallet_string

    @staticmethod
    def get_color_text(text, value):
        """
        Returns colored text
        """
        v = round(value, 2) + 0.0
        output_text = text + str(round(v, 2)) + '%'
        color = 'green' if round(v, 2) >= 0 else 'red'
        return colored(output_text, color)

    def calc_balance(self, ticker_data, wallet):
        """
        Calculates current balance (profit/loss)
        """
        current_balance = 0
        for pair in self.pairs:
            if pair == ticker_data.iloc[0]['pair']:
                current_closing = ticker_data.iloc[0]['close']
                # TODO Here we assume that our base is BITCOIN. This might need to be changed
                pair_1_item = [item for item in wallet.current_balance if item[0] == ticker_data.iloc[0]['curr_1']]
                pair_1_balance = float(pair_1_item[0][1])
                pair_2_item = [item for item in wallet.current_balance if item[0] == ticker_data.iloc[0]['curr_2']]
                pair_2_balance = float(pair_2_item[0][1])
                current_balance += pair_1_balance + pair_2_balance*current_closing

        # print('current_balance:', current_balance)
        print('initial_close:', self.initial_close)
        price_diff = current_balance - self.initial_balance
        perc_change = ((price_diff*100.0)/self.initial_balance)
        return perc_change

    def initialize_start_price(self, ticker_data):
        """
        Save initial Closing price
        """
        # print('-------------------saving init price')
        ticker_pair = ticker_data.iloc[0]['pair']
        closing = ticker_data.iloc[0]['close']
        # Check if item is in our pairs, that we are trading
        if ticker_pair in self.pairs:
            # Check if we have already saved the closing price
            balance_item = [item for item in self.initial_close if ticker_pair in item[0]]
            if not balance_item:
                self.initial_close.append((ticker_pair, closing))
                # Recalculate initial_balance
                pair1_currency = ticker_data.iloc[0]['curr_1']
                pair2_currency = ticker_data.iloc[0]['curr_2']
                currency1_wallet = float([item for item in self.initial_wallet if pair1_currency in item[0]][0][1])
                currency2_wallet = float([item for item in self.initial_wallet if pair2_currency in item[0]][0][1])
                self.initial_balance += closing * currency2_wallet + currency1_wallet

    def calc_buy_and_hold(self, ticker_data):
        """
        Calculate Buy & Hold price
        """
        pair = ticker_data.iloc[0]['pair']
        current_closing = ticker_data.iloc[0]['close']
        init_closing = [item for item in self.initial_close if pair in item][0][1]
        return ((current_closing - init_closing)*100.0)/init_closing
