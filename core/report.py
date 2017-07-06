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
        self.initial_close = dict((pair, None) for pair in self.pairs)

    def calc_stats(self, ticker_data, wallet):
        """
        Creates ticker report
        """
        none_init_balances = {k: v for k, v in self.initial_close.items() if v is None}
        # Store initial closing price and initial overall wallet balance
        if len(none_init_balances) > 0:
            self.initialize_start_price(ticker_data, none_init_balances)
            self.initial_balance = self.initialize_start_balance(self.initial_wallet,
                                                                 self.initial_close)
        # print('ticker_data....', ticker_data)
        date_time = datetime.fromtimestamp(ticker_data['date'][0]).strftime('%c') + ','
        current_close = 'close:' + format(ticker_data.iloc[0]['close'], '2f') + ','
        # Wallet
        wallet_text = self.get_wallet_text(wallet)
        # Balance
        balance = self.calc_balance(ticker_data, wallet.current_balance)
        balance_text = self.get_color_text('$: ', balance) + ','
        # Buy & Hold
        bh = self.calc_buy_and_hold(ticker_data, wallet.initial_balance)
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
        for symbol, balance in wallet.current_balance.items():
            if balance > 0:
                wallet_string += ' | ' + str(balance) + symbol
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

    def calc_balance(self, ticker_data, wallet_balance):
        """
        Calculates current balance (profit/loss)
        """
        current_balance = 0
        for currency, value in wallet_balance.items():
            if currency == 'BTC':
                current_balance += value
                continue

            pair = 'BTC_' + currency
            ticker = ticker_data.loc[ticker_data['pair'] == pair]
            if ticker.empty:
                print('DataFrame of following pair is empty:', pair)
                continue
            current_closing = ticker.iloc[0]['close']
            currency_symbol = ticker.iloc[0]['curr_2']
            pair_2_balance = 0.0
            if currency_symbol in wallet_balance:
                pair_2_balance = float(wallet_balance[currency_symbol])
            current_balance += pair_2_balance * current_closing

        price_diff = current_balance - self.initial_balance
        perc_change = ((price_diff*100.0)/self.initial_balance)
        return perc_change

    def initialize_start_price(self, ticker_data, none_init_balances):
        """
        Save initial Closing price
        """
        # Get only currencies that have not been initialized yet
        for pair in none_init_balances:
            ticker = ticker_data.loc[ticker_data['pair'] == pair]
            if ticker.empty:
                print("Couldn't find ticker for pair:", pair)
                continue
            closing = ticker.iloc[0]['close']
            self.initial_close[pair] = closing

    @staticmethod
    def initialize_start_balance(wallet, close_prices):
        """
        Calculate overall wallet balance in bitcoins
        """
        balance = 0.0
        for currency, value in wallet.items():
            if currency == 'BTC':
                balance += value
                continue
            pair = 'BTC_' + currency
            init_value = close_prices.get(pair)
            if init_value is None:
                init_value = 0.0
            curr_value = value * init_value
            balance += curr_value
        return balance

    def calc_buy_and_hold(self, ticker_data, initial_balance):
        """
        Calculate Buy & Hold price
        """
        return self.calc_balance(ticker_data, initial_balance)
