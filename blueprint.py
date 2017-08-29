import argparse
import configparser
from ai.blueprint import Blueprint


def run(cfg):
    """
     Start blueprint
    """
    blueprint = Blueprint(cfg)
    blueprint.run()


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    config_parser = argparse.ArgumentParser()

    defaults = dict()
    args, remaining_argv = config_parser.parse_known_args()
    config = configparser.ConfigParser()
    config.read('mosquito.ini')
    for item in config.items():
        i = config.items(item[0])
        defaults[item[0]] = dict(config.items(item[0]))

    args = args_parser.parse_args(remaining_argv)
    #parser.set_defaults(**defaults)
    args_parser.add_argument("--exchange", help="Exchange (Default Poloniex)", default='polo')
    args_parser.add_argument("--pairs", help="* for all or prefix_* for prefix group (default BTC_*)", default='BTC_*')
    args_parser.add_argument("--days", help="Number of history days, the dataset should be generated", default=30)
    args_parser.add_argument("--interval", help="Ticker size in minutes", default=5)
    args_parser.add_argument("--features", help="Path to input features file", action='store_true')

    config_parser.set_defaults(**defaults)
    config_vars = config_parser.parse_args()
    # args = parser.parse_args(remaining_argv)
    print(args)
    print('*******---default********************')
    print(args.DEFAULT)
    run(args)
