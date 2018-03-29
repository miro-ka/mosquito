import configargparse
from backfill.candles import Candles
from backfill.trades import Trades


def main(args):
    if args.full:
        trades_client = Trades()
        trades_client.run()
        candles_client = Candles()
        candles_client.run()
        return

    if args.backfilltrades:
        backfill_client = Trades()
        backfill_client.run()
    else:
        backfill_client = Candles()
        backfill_client.run()


if __name__ == "__main__":
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--full',
                   help='Backfill candle and trades',
                   action='store_true')

    options = arg_parser.parse_known_args()[0]
    main(options)
