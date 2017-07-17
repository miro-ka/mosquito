import configparser


class Wallet:
    """
    Class holding current status of wallet (assets and currencies)
    """

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        currency = config['Wallet']['currency'].replace(" ", "").split(',')
        amount = config['Wallet']['amount'].replace(" ", "").split(',')
        amount = [float(i) for i in amount]
        self.initial_balance = dict(zip(currency, amount))
        self.current_balance = self.initial_balance.copy()
