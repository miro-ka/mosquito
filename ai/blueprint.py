import click
from exchanges.exchange import Exchange


@click.command()
@click.option('--exchange', default='polo', help='Exchange (Default Poloniex)')
@click.option('--pairs', default='BTC_*', help='Included pairs: * for all or prefix_* for prefix group (default BTC_*)')
@click.option('--days', default=30, required=False, help='Number of history days, the dataset should be generated')
@click.option('--ticker', default=5, required=False, help='Ticker size in minutes')
@click.option('--features', help='Path to input features list file')
class Blueprint:
    """
    Main module for generating and handling datasets for AI
    """

    exchange = None

    def __init__(self, exchange, pairs, days, ticker, features):
        self.exchange = Exchange(None, 'config.ini')
        v = self.exchange.get_pairs()
        pass

    def run(self):
        """
        Calculates and stores dataset
        """
        print('calculate')