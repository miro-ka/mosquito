import configargparse
from core.engine import Engine


def main():
    engine = Engine()
    engine.run()


def has_mandatory_fields(args):
    """
    Checks if command arguments contain all mandatory arguments
    """
    if not args.backtest and not args.live and not args.paper:
        return False
    return True

if __name__ == "__main__":
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('-c', '--config', is_config_file=True, help='config file path', default='mosquito.ini')
    arg_parser.add('-v', '--verbosity', help='Verbosity', action='store_true')
    arg_parser.add('--strategy', help='Strategy')
    arg_parser.add('--fixed_trade_amount', help='Fixed trade amount')
    args = arg_parser.parse_known_args()

    main()

