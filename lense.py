import configargparse
from utils.walletlense import WalletLense

"""
Lense: Returns actual wallet statistics with simple daily digest (winners / losers)
"""


def main():
    lense = WalletLense()
    lense.get_stats()


if __name__ == "__main__":
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='mosquito.ini')
    arg_parser.add('-v', '--verbosity', help='Verbosity', action='store_true')
    args = arg_parser.parse_known_args()[0]

    main()

