from .base import Base
import time
from strategies.enums import TradeState as ts
from core.bots.enums import TradeMode
from termcolor import colored
from exchanges.exchange import Exchange


DAY = 3600


class Backtest(Base):
    """
    Main class for Backtest trading
    """
    previous_action = None
    ticker_df = None
    exchange = None
    mode = TradeMode.backtest

    def __init__(self, args, config_file):
        super(Backtest, self).__init__(args, config_file)
        self.counter = 0
        self.config = self.initialize_config(config_file)
        self.transaction_fee = float(self.config['Trade']['transaction_fee'])
        self.sim_start = self.config['Backtest']['from']
        self.sim_end = self.config['Backtest']['to']
        self.sim_hours = int(self.config['Backtest']['hours'])
        self.sim_epoch_start = self.get_sim_epoch_start(self.sim_hours, self.sim_start)
        self.current_epoch = self.sim_epoch_start
        self.exchange = Exchange(args, config_file, TradeMode.backtest)
        self.pairs = self.process_input_pairs(self.config['Trade']['pairs'])

    def get_pairs(self):
        return self.pairs

    def process_input_pairs(self, in_pairs):
        if in_pairs == 'all':
            print('setting_all_pairs')
            return self.exchange.get_all_tickers()
            # Get all pairs from API
        else:
            return in_pairs.replace(" ", "").split(',')

    def get_wallet_balance(self):
        """
        Returns wallet balance
        """
        pass

    @staticmethod
    def get_sim_epoch_start(sim_hours, sim_start):
        if sim_start:
            return sim_start
        elif sim_hours:
            epoch_now = int(time.time())
            return epoch_now - (DAY*sim_hours)

    def get_next(self, interval):
        """
        Returns next state of current_time + interval (in minutes)
        """
        self.ticker_df = self.exchange.get_offline_ticker(self.current_epoch, self.pairs)
        self.current_epoch += interval*60
        return self.ticker_df

    def trade(self, actions, wallet, trades, force_sell=True):
        """
        Simulate currency buy/sell (places fictive buy/sell orders)
        """
        if self.ticker_df.empty:
            print('Can not trade with empty dataframe, skipping trade')
            return wallet

        for action in actions:
            # If we are forcing_sell, we will first sell all our assets
            if force_sell:
                assets = wallet.copy()
                del assets['BTC']
                for asset, value in assets.items():
                    if value == 0.0:
                        continue
                    pair = 'BTC_' + asset
                    # If we have the same pair that we want to buy, lets not sell it
                    if pair == action.pair:
                        continue
                    ticker = self.ticker_df.loc[self.ticker_df['pair'] == pair]
                    if ticker.empty:
                        print('No currency data for pair: ' + pair + ', skipping')
                        continue
                    close_price = ticker['close'].iloc[0]
                    fee = self.transaction_fee*float(value)/100.0
                    print('txn fee:', fee, ', balance before: ', value, ', after: ', value-fee)
                    value -= fee
                    earned_balance = close_price * value
                    root_symbol = 'BTC'
                    currency = wallet[root_symbol]
                    # Store trade history
                    trades.loc[len(trades)] = [ticker['date'].iloc[0], pair, close_price, 'sell']
                    wallet[root_symbol] = currency + earned_balance
                    wallet[asset] = 0.0

            (currency_symbol, asset_symbol) = tuple(action.pair.split('_'))
            # Get pairs current closing price
            ticker = self.ticker_df.loc[self.ticker_df['pair'] == action.pair]
            close_price = ticker['close'].iloc[0]

            currency_balance = asset_balance = 0.0
            if currency_symbol in wallet:
                currency_balance = wallet[currency_symbol]
            if asset_symbol in wallet:
                asset_balance = wallet[asset_symbol]

            # None
            if action.action == ts.none:
                self.previous_action = action.action
                continue
            # Buy
            elif action.action == ts.buy:
                if currency_balance <= 0:
                    print('want to buy, not enough money, or everything already bought..')
                    continue
                print(colored('buying ' + action.pair, 'green'))
                fee = self.transaction_fee * float(currency_balance) / 100.0
                print('txn fee:', fee, ',currency_balance: ', currency_balance, ', after: ', currency_balance-fee)
                currency_balance -= fee
                wallet[asset_symbol] = asset_balance + (currency_balance / close_price)
                wallet[currency_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'buy']
                continue
            # Sell
            elif action.action == ts.sell:
                if asset_balance <= 0:
                    print('want to buy, not enough money, or everything already sold..')
                    continue
                print(colored('selling ' + action.pair, 'red'))
                fee = self.transaction_fee * float(currency_balance) / 100.0
                print('txn fee:', fee, ',asset_balance: ', asset_balance, ', after: ', asset_balance-fee)
                asset_balance -= fee
                wallet[currency_symbol] = currency_balance + (asset_balance * close_price)
                wallet[asset_symbol] = 0.0
                # Append trade
                trades.loc[len(trades)] = [ticker['date'].iloc[0], action.pair, close_price, 'sell']
                continue
        del actions[:]
        return wallet

    @staticmethod
    def refresh_wallet(self, wallet):
        """
        Returns new updated wallet balance. In back testing, the wallet is updated in trade
         method, so there is nothing extra needed here.
        """
        # TODO: update wallets balance
        print('refreshing wallet')
        return wallet
