import configargparse
from backfill.candles import Candles
from backfill.trades import Trades


def main(args):
    if args.backfilltrades:
        backfill_client = Trades()
        backfill_client.run()
    else:
        backfill_client = Candles()
        backfill_client.run()


if __name__ == "__main__":
    arg_parser = configargparse.get_argument_parser()
    options = arg_parser.parse_known_args()[0]
    main(options)
