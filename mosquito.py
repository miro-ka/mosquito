import argparse

from core.engine import Engine


def main(args):

    engine = Engine(args, 'config.ini')
    engine.run()


def has_mandatory_fields(args):
    """
    Checks if command arguments contain all mandatory arguments
    """
    if not args.backtest and not args.live and not args.paper:
        return False
    return True

if __name__ == "__main__":
    # Parse input
    parser = argparse.ArgumentParser()
    parser.add_argument("--backtest", help="Simulate your strategy on history ticker data", action='store_true')
    parser.add_argument("--paper", help="Simulate your strategy on real ticker", action='store_true')
    parser.add_argument("--live", help="REAL trading mode", action='store_true')
    parser.add_argument("--strategy", help="Name of strategy to be run (if not set, the default one will be used")
    parser.add_argument("--plot", help="Generate a candle stick plot at simulation end", action='store_true')

    args = parser.parse_args()

    if not has_mandatory_fields(args):
        print("Missing trade mode argument (backtest, paper or live). See --help for more details.")
        exit(0)

    main(args)

