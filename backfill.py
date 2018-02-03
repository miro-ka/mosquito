import configargparse
from backfill.backfillticker import BackfillTicker


def main(args):
    if 'backfilltrades' in args:
        # TODO
        print('wohoho')
    else:
        backfill_client = BackfillTicker()
        backfill_client.run()


if __name__ == "__main__":
    arg_parser = configargparse.get_argument_parser()
    options = arg_parser.parse_known_args()[0]
    main(options)
