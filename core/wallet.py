import configparser



class Wallet:
    """
    Class holding current status of wallet (assets and currencies)
    """

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        currency = config['Wallet']['currency'].split(',')
        value = config['Wallet']['value'].split(',')
        self.initial = list(zip(currency, value))
