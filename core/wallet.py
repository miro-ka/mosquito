import configparser


class Wallet:
    """
    Class holding current status of wallet (assets and currencies)
    """

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        currency = config['Wallet']['currency'].replace(" ", "").split(',')
        value = config['Wallet']['value'].replace(" ", "").split(',')
        self.initial_balance = list(zip(currency, value))
        self.current_balance = self.initial_balance
