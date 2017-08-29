import configargparse


class Wallet:
    """
    Class holding current status of wallet (assets and currencies)
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--wallet_currency', help='Wallet currency (separated by comma)')
    arg_parser.add("--wallet_amount", help='Wallet amount (separated by comma)')

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        currency = args.wallet_currency.replace(" ", "").split(',')
        amount = args.wallet_amount.replace(" ", "").split(',')
        amount = [float(i) for i in amount]
        self.initial_balance = dict(zip(currency, amount))
        self.current_balance = self.initial_balance.copy()
